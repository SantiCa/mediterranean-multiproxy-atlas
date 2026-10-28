"""Independent source-line/hash/column checks for the small marine SST staging set."""
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data/interim/v1_marine"
bundle = json.loads((ROOT / "marine_sst.json").read_text(encoding="utf-8"))
records = {record["record_id"]: record for record in bundle["records"]}
sources = {}
for key, record in records.items():
    raw = (ROOT / record["source_raw"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record["raw_sha256"]
    text = raw.decode("utf-8-sig")
    rows = list(csv.DictReader(io.StringIO(text.split("*/", 1)[1].strip()), delimiter="\t"))
    assert len(rows) == record["sample_count"]
    sources[key] = (text.splitlines(), rows)
for observation in bundle["observations"]:
    lines, rows = sources[observation["record_id"]]
    native = rows[observation["source_row"] - 1]
    assert native[observation["source_column"]] == observation["source_value"]
    assert float(native[observation["source_column"]]) == observation["value"]
    assert float(native["Age [ka BP]"]) == observation["age_ka_bp"]
    assert observation["source_value"] in lines[observation["source_line"] - 1].split("\t")
    assert math.isfinite(observation["value"]) and math.isfinite(observation["age_ka_bp"])
    assert observation["raw_sha256"] == records[observation["record_id"]]["raw_sha256"]
assert len(bundle["observations"]) == sum(record["sample_count"] for record in records.values())
summary = dict(source_records=len(records), observations=len(bundle["observations"]),
               observations_0_20_ka=sum(0 <= item["age_ka_bp"] <= 20 for item in bundle["observations"]),
               checks="sha256, source row/line/column, value/age equality, finite values, dataset counts",
               status="passed", scientific_limit="No age recalibration, publication-completeness or lab-method validation")
(ROOT / "audit.json").write_text(json.dumps(summary, indent=2)+"\n", encoding="utf-8")
print(json.dumps(summary))
