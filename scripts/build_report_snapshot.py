"""Package reviewed evidence for the local feasibility report viewer."""
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / "data/processed/catalog.json").read_text(encoding="utf-8"))
rows = json.loads((ROOT / "data/processed/observations.json").read_text(encoding="utf-8"))
prior_art = [
    dict(name="PaleoMED20", year=2025, url="https://www.nature.com/articles/s41597-025-05451-5", scope="Inventario mediterráneo de metadatos; no auditado el fichero Figshare"),
    dict(name="WDB-Paleo", year=2017, url="https://www.pi.ingv.it/252362-2/", scope="Modelo relacional y datos cuantitativos publicados; servicio actual no probado"),
    dict(name="World Paleoceanographic Atlas", year=None, url="https://paleodataview.marum.de/", scope="Datos por profundidad y edad; detalles de incertidumbre documentados para 2024"),
    dict(name="NOAA WDS Paleo", year=None, url="https://www.ncei.noaa.gov/access/paleo-search/api", scope="Documentación de búsqueda y acceso; sin importación numérica"),
    dict(name="PANGAEA", year=2023, url="https://doi.org/10.1038/s41597-023-02269-x", scope="Repositorio original de los cinco conjuntos descargados"),
    dict(name="LiPD", year=2016, url="https://cp.copernicus.org/articles/12/1093/2016/", scope="Marco de intercambio; no implementado"),
]
snapshot = dict(surface="report", title="Mediterranean Multiproxy Atlas · informe de viabilidad", generatedAt=datetime.now(timezone.utc).isoformat(),
                status="reviewed-evidence-with-limitations", buildStatus="creating", filters=[],
                scientificReportMarkdown=(ROOT / "reports/informe_viabilidad.md").read_text(encoding="utf-8"),
                architectureMarkdown=(ROOT / "docs/arquitectura_datos.md").read_text(encoding="utf-8"),
                report=dict(asOf="2026-10-28", audience="Investigación paleoceanográfica"), queries={
                    "seed_catalog": dict(rows=catalog, source=dict(label="Cinco conjuntos PANGAEA descargados y verificados", provider="PANGAEA", files=[f"data/raw/pangaea/{r['dataset_id']}.tsv" for r in catalog], links=[dict(label=r["core"], url=f"https://doi.pangaea.de/{r['dataset_doi']}") for r in catalog], transformations=["T001: extracción explícita sin armonización de edades ni imputación"], caveats=["Selección intencional, sin representatividad mediterránea", "Edad archivada, no modelo de edad auditado", "Tesis revisada; suplementos y datos fuente pendientes de auditoría"], metricDefinitions=[dict(label="Filas originales", definition="Filas de muestra por tabla TSV; no número de valores ni réplicas independientes", componentIds=["catalog-evidence"]) ])),
                    "prior_art": dict(rows=prior_art, source=dict(label="Fuentes editoriales e institucionales consultadas", links=[dict(label=r["name"],url=r["url"]) for r in prior_art], caveats=["Revisión dirigida; no revisión sistemática exhaustiva", "Cuartiles no verificados"])),
                    "sst_example": dict(rows=[dict(age_ka_bp=r["age_ka_bp"], value=r["value"], source_row=r["source_row"], core=r["core"], dataset_doi=r["dataset_doi"], unit=r["unit"]) for r in rows if r["dataset_id"]==438816], source=dict(label="Cacho et al. (1999), MD95-2043, PANGAEA.438816", files=["data/raw/pangaea/438816.tsv"], links=[dict(label="PANGAEA.438816",url="https://doi.pangaea.de/10.1594/PANGAEA.438816")], filters=["Todas las 97 filas originales, SST anual de alquenonas"], caveats=["Cronología archivada sin armonizar", "SST es reconstrucción publicada; incertidumbre no informada en esta tabla"], metricDefinitions=[dict(label="SST anual", definition="Valor publicado de SST anual de alquenonas, grados Celsius; sin recálculo local", componentIds=["sst-evidence"])]))
                })
(ROOT / "reports/reviewed_snapshot.json").write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
print("Saved reviewed report snapshot")
