"""Scientific audit of a versioned atlas seed. Read-only: reports, never edits values.

Usage: python scripts/audit_science.py data/processed/atlas-vN.json [--json out.json]
Exit code 1 only for hard integrity errors (counts, non-finite numbers, orphan series,
duplicate ids). Plausibility findings are warnings for curator review.
"""
import argparse
import collections
import hashlib
import json
import math
import sys

# Physical/plausible bounds per unit (inclusive). Outside -> warning, not error.
BOUNDS = {
    "%": (0, 100), "% en masa": (0, 100),
    "°C": (-3, 40),
    "‰ PDB": (-20, 10), "‰ VPDB": (-20, 10), "‰ VSMOW": (-30, 45),
}
POST_BOMB_KA = -0.08   # 2030 CE in ka BP
MAX_AGE_KA = 5000      # beyond Pliocene: likely unit error
BOX = (-20, 50, 25, 50)  # lon_min, lon_max, lat_min, lat_max (Mediterranean + Iberian/N. African margins)


def finite(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def audit(seed):
    err, warn = [], collections.defaultdict(list)
    recs = {r["id"]: r for r in seed["records"]}
    if len(recs) != len(seed["records"]):
        err.append("ids de registro duplicados")
    ids = [s["id"] for s in seed["series"]]
    if len(set(ids)) != len(ids):
        err.append("ids de serie duplicados: " + ", ".join(k for k, n in collections.Counter(ids).items() if n > 1))

    coords = collections.defaultdict(list)
    for r in seed["records"]:
        lo, la = r.get("longitude"), r.get("latitude")
        if not (finite(lo) and finite(la)):
            warn["sin_coordenadas"].append(r["id"])
            continue
        if not (BOX[0] <= lo <= BOX[1] and BOX[2] <= la <= BOX[3]):
            warn["fuera_de_area"].append(f"{r['id']} ({la},{lo})")
        coords[(round(lo, 4), round(la, 4))].append(r["id"])
        if not (r.get("dataset_doi") or r.get("paper_doi") or r.get("source_url")):
            warn["registro_sin_doi_ni_url"].append(r["id"])
    for k, v in coords.items():
        if len(v) > 1:
            warn["registros_mismas_coordenadas"].append(f"{k}: {', '.join(sorted(v))}")

    units_by_group = collections.defaultdict(set)
    fingerprints = collections.defaultdict(list)
    for s in seed["series"]:
        sid, rows = s["id"], s["rows"]
        if s["record_id"] not in recs:
            err.append(f"{sid}: registro inexistente {s['record_id']}")
        if s.get("observation_count") != len(rows):
            err.append(f"{sid}: observation_count {s.get('observation_count')} != {len(rows)} filas")
        if not (s.get("license") or s.get("license_url")) and not (recs.get(s["record_id"], {}).get("license")):
            warn["serie_sin_licencia"].append(sid)
        units_by_group[(s["proxy"], s.get("compatibility_group") or sid)].add(s["unit"])
        ages = [r[0] for r in rows if r[0] is not None]
        vals = [r[1] for r in rows]
        bad = [v for v in vals + ages if v is not None and not finite(v)]
        if bad:
            err.append(f"{sid}: {len(bad)} números no finitos")
        if ages:
            lo, hi = min(ages), max(ages)
            if s.get("age_min_ka_bp") is not None and abs(lo - s["age_min_ka_bp"]) > 1e-9:
                err.append(f"{sid}: age_min declarado {s['age_min_ka_bp']} != {lo}")
            if s.get("age_max_ka_bp") is not None and abs(hi - s["age_max_ka_bp"]) > 1e-9:
                err.append(f"{sid}: age_max declarado {s['age_max_ka_bp']} != {hi}")
            if lo < POST_BOMB_KA:
                warn["edad_futura"].append(f"{sid} min {lo} ka")
            if hi > MAX_AGE_KA:
                warn["edad_extrema"].append(f"{sid} max {hi} ka")
        b = BOUNDS.get(s["unit"])
        # Per-mil bounds are for carbonate/water δ18O only (lipid δD/δ13C are legitimately lower).
        if s["unit"].startswith("‰") and "18o" not in (s["proxy"] + s.get("label", "") + str(s.get("source_column", ""))).lower():
            b = None
        if b:
            out = [v for v in vals if finite(v) and not (b[0] <= v <= b[1])]
            if out:
                warn["valor_fuera_de_rango"].append(f"{sid} [{s['unit']}] {len(out)} valores, p.ej. {out[0]}")
        # Age reversals in source order (depth order) beyond 1 % of rows: possible age-model issue.
        by_src = sorted((r for r in rows if r[0] is not None and r[2] is not None), key=lambda r: r[2])
        inv = sum(1 for a, c in zip(by_src, by_src[1:]) if c[0] < a[0])
        if len(by_src) > 10 and inv > max(1, 0.01 * len(by_src)) and inv < len(by_src) - 1:
            warn["inversiones_de_edad_en_orden_fuente"].append(f"{sid}: {inv}/{len(by_src)}")
        if len(rows) >= 5:
            h = hashlib.sha1(json.dumps([[r[0], r[1]] for r in rows]).encode()).hexdigest()
            fingerprints[h].append(sid)
    for (p, g), u in units_by_group.items():
        if len(u) > 1:
            err.append(f"grupo {p}/{g} con unidades distintas: {sorted(u)}")
    for h, v in fingerprints.items():
        recs_v = {x.split(":")[0] for x in v}
        if len(v) > 1 and len(recs_v) > 1:
            warn["series_identicas_en_registros_distintos"].append(", ".join(sorted(v)))
    return err, warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed")
    ap.add_argument("--json")
    a = ap.parse_args()
    seed = json.load(open(a.seed, encoding="utf8"))
    err, warn = audit(seed)
    print(f"{seed['version']}: {len(seed['records'])} registros, {len(seed['series'])} series, "
          f"{sum(len(s['rows']) for s in seed['series'])} valores")
    print(f"ERRORES: {len(err)}")
    for e in err[:50]:
        print("  -", e)
    for k, v in sorted(warn.items()):
        print(f"AVISO {k}: {len(v)}")
        for x in v[:8]:
            print("    ·", x)
    if a.json:
        json.dump({"version": seed["version"], "errors": err, "warnings": warn}, open(a.json, "w"),
                  ensure_ascii=False, indent=1)
    sys.exit(1 if err else 0)


if __name__ == "__main__":
    main()
