"""Load versioned atlas releases into Cloudflare D1 from outside the Worker.

The v5 seed (3.4 MB gzip) exceeds the Workers Free script limit, so the Worker
only bundles a small manifest and the deploy workflow writes D1 through
`wrangler d1 execute --file`. Contract kept from the former /api/bootstrap:
identical row encoding, append-only observations (id = series_id:source_row,
ON CONFLICT DO NOTHING) and a release row only after every series of that
release has its full observation count.

Subcommands
  manifest  --seed v3 --seed v4 --seed v5 --out app/atlas-web/data/release.json
  plan      --seed ... --counts counts.json --out-dir DIR [--max-obs N]
            writes 0001.sql... for series still incomplete, oldest release first
  finalize  --seed ... --counts counts.json --releases releases.json --out FILE
            refreshes metadata and registers every newly complete release
`counts.json`/`releases.json` are `wrangler d1 execute --json` outputs.
Free plan: 100 000 rows written/day (index entries count), so a large release
takes several daily runs; partial loads stay invisible (see lib/release.mjs).
"""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

OBS_COLUMNS = "id,series_id,age_ka_bp,value,source_row,source_line,original_age,original_value,age_uncertainty_ka,value_uncertainty,depth_original"


def load_seeds(paths):
    """Seeds oldest first; each must declare its parent as the previous one."""
    seeds = [json.loads(Path(p).read_text(encoding="utf8")) for p in paths]
    for parent, child in zip(seeds, seeds[1:]):
        if child.get("parent_version") != parent["version"]:
            raise ValueError(child["version"] + " does not descend from " + parent["version"])
    return seeds


def sql(v):
    """SQLite literal. Strings are quoted, never interpolated raw."""
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, (int, float)):
        if v != v or v in (float("inf"), float("-inf")):
            raise ValueError("Non-finite number in seed")
        return repr(v)
    return "'" + str(v).replace("'", "''") + "'"


def compact(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def record_row(r):
    return [r["id"], r["name"], r["realm"], r["latitude"], r["longitude"], compact(r)]


def series_row(s):
    meta = {k: v for k, v in s.items() if k != "rows"}
    return [s["id"], s["record_id"], s["proxy"], s["label"], s["unit"], compact(meta)]


def insert(table, columns, rows, conflict, width=50, max_bytes=90_000):
    """Multi-row INSERTs below D1's 100 KB statement limit (series metadata ~3-20 KB)."""
    out, group, size = [], [], 0
    head = "INSERT INTO " + table + "(" + columns + ") VALUES "

    def emit():
        if group:
            out.append(head + ",".join(group) + " " + conflict + ";")

    for row in rows:
        value = "(" + ",".join(sql(v) for v in row) + ")"
        if len(value.encode()) + len(head) > max_bytes:
            raise ValueError("Row too large for one D1 statement")
        if group and (len(group) >= width or size + len(value.encode()) > max_bytes - len(head)):
            emit()
            group, size = [], 0
        group.append(value)
        size += len(value.encode()) + 1
    emit()
    return out


def wrangler_rows(path):
    data = json.loads(Path(path).read_text(encoding="utf8"))
    if isinstance(data, list):
        data = data[0]
    return data.get("results", [])


def counts_of(path):
    return {r["series_id"]: int(r["n"]) for r in wrangler_rows(path)}


def ordered_series(seeds):
    """Every series of the newest release, in the release where it first appears."""
    latest = {s["id"]: s for s in seeds[-1]["series"]}
    seen, out = set(), []
    for seed in seeds:
        for s in seed["series"]:
            if s["id"] in latest and s["id"] not in seen:
                seen.add(s["id"])
                out.append(latest[s["id"]])
    return out


def cmd_manifest(a):
    """Manifest of the release chain. Releases already listed in the existing manifest
    but no longer among the seeds are kept (before the newest), so the Worker can keep
    serving a loaded older release while a newer one is still being written to D1."""
    seeds = load_seeds(a.seed)
    new = [{
        "version": s["version"],
        "parent_version": s.get("parent_version"),
        "observation_count": sum(len(x["rows"]) for x in s["series"]),
        "records": sorted(r["id"] for r in s["records"]),
        "series": sorted(x["id"] for x in s["series"]),
    } for s in seeds]
    names = {r["version"] for r in new}
    old = []
    out = Path(a.out)
    for extra in ([out] if out.exists() else []) + [Path(x) for x in (a.keep or [])]:
        for r in json.loads(extra.read_text(encoding="utf8"))["releases"]:
            if r["version"] not in names and r.get("parent_version") in names:
                old.append(r)
                names.add(r["version"])
    manifest = {"releases": new[:-1] + old + new[-1:]}
    out.write_text(compact(manifest) + "\n", encoding="utf8")
    print(a.out, [r["version"] for r in manifest["releases"]])


def cmd_plan(a):
    seeds = load_seeds(a.seed)
    counts = counts_of(a.counts) if a.counts else {}
    records = {r["id"]: r for seed in seeds for r in seed["records"]}
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pending = [s for s in ordered_series(seeds) if counts.get(s["id"], 0) < len(s["rows"])]
    files, chunk, size = 0, [], 0

    def flush():
        nonlocal files, chunk, size
        if chunk:
            files += 1
            (out / ("%04d.sql" % files)).write_text("\n".join(chunk) + "\n", encoding="utf8")
        chunk, size = [], 0

    for s in pending:
        # Parents first (foreign key). Existing metadata is left untouched here so the
        # served release does not change until finalize.
        chunk += insert("atlas_records", "id,name,realm,latitude,longitude,metadata_json",
                        [record_row(records[s["record_id"]])], "ON CONFLICT(id) DO NOTHING")
        chunk += insert("atlas_series", "id,record_id,proxy,label,unit,metadata_json",
                        [series_row(s)], "ON CONFLICT(id) DO NOTHING")
        rows = [[s["id"] + ":" + str(r[2]), s["id"], *r] for r in s["rows"]]
        for i in range(0, len(rows), a.max_obs):
            part = rows[i:i + a.max_obs]
            if size and size + len(part) > a.max_obs:
                flush()
            chunk += insert("atlas_observations", OBS_COLUMNS, part, "ON CONFLICT(id) DO NOTHING")
            size += len(part)
    flush()
    total = sum(len(s["rows"]) - counts.get(s["id"], 0) for s in pending)
    print("pending_series=%d pending_values<=%d files=%d" % (len(pending), total, files))


def cmd_finalize(a):
    seeds = load_seeds(a.seed)
    counts = counts_of(a.counts)
    present = {r["id"] for r in wrangler_rows(a.releases)}
    stmts, done = [], []
    for seed in seeds:
        if seed["version"] in present:
            continue
        if any(counts.get(s["id"], 0) != len(s["rows"]) for s in seed["series"]):
            break  # releases complete in order; newer ones wait for this one
        stmts += insert("atlas_records", "id,name,realm,latitude,longitude,metadata_json",
                        [record_row(r) for r in seed["records"]],
                        "ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json")
        stmts += insert("atlas_series", "id,record_id,proxy,label,unit,metadata_json",
                        [series_row(s) for s in seed["series"]],
                        "ON CONFLICT(id) DO UPDATE SET metadata_json=excluded.metadata_json")
        n = sum(len(s["rows"]) for s in seed["series"])
        stmts.append("INSERT OR IGNORE INTO atlas_releases VALUES(" + ",".join(
            sql(v) for v in (seed["version"], n, datetime.now(timezone.utc).isoformat())) + ");")
        done.append(seed["version"])
    Path(a.out).write_text("\n".join(stmts) + "\n" if stmts else "", encoding="utf8")
    print("complete_now=" + (",".join(done) or "none"))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest"); m.add_argument("--seed", action="append", required=True); m.add_argument("--out", required=True); m.add_argument("--keep", action="append", help="older manifest whose releases stay servable")
    q = sub.add_parser("plan"); q.add_argument("--seed", action="append", required=True); q.add_argument("--counts"); q.add_argument("--out-dir", required=True); q.add_argument("--max-obs", type=int, default=5000)
    f = sub.add_parser("finalize"); f.add_argument("--seed", action="append", required=True); f.add_argument("--counts", required=True); f.add_argument("--releases", required=True); f.add_argument("--out", required=True)
    a = p.parse_args()
    {"manifest": cmd_manifest, "plan": cmd_plan, "finalize": cmd_finalize}[a.cmd](a)


if __name__ == "__main__":
    main()
