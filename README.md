# Mediterranean Multiproxy Atlas

**Global in architecture; Mediterranean first in the research workflow.** A research software project to discover, document, connect and visualize georeferenced paleoclimate records while preserving source metadata, age models, transformations, licensing and uncertainty.

The model is designed for marine and continental archives. The proposed relational architecture uses versioned geography independently of records; region storage and migrations remain to be implemented. The first interactive web pilot is implemented with a D1/SQLite database; Mediterranean synthesis and full scientific validation remain future work.

## Interactive v1

[Open the atlas](https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site) (owner-private). Marine and continental records, proxy/age filters, original or normalized values, optional exploratory color fields, time series, CSV and editable SVG. [Implementation, reproduction and scientific limits](docs/WEB_V1.md). Web source: `app/atlas-web/`; reproducible SQLite: `python scripts/build_atlas_v1.py --from-seed --sqlite data/processed/atlas-v1-local.sqlite`.

## Project documents

- Agent instructions: [`AGENTS.md`](AGENTS.md); Claude entry: [`CLAUDE.md`](CLAUDE.md)
- Short current state and backlog: [`docs/PROJECT_STATE.md`](docs/PROJECT_STATE.md)
- Specialist chat prompts: [`docs/CHAT_PROMPTS.md`](docs/CHAT_PROMPTS.md)
- Technical review and remaining issues: [`reports/revision_codigo_2026-10-28.md`](reports/revision_codigo_2026-10-28.md)

- Feasibility report: [`reports/informe_viabilidad.md`](reports/informe_viabilidad.md)
- Thesis and publication review: [`docs/revision_tesis.md`](docs/revision_tesis.md)
- Source-neutral data model: [`docs/arquitectura_datos.md`](docs/arquitectura_datos.md)
- Scalable platform design: [`docs/arquitectura_plataforma.md`](docs/arquitectura_plataforma.md)
- Provider access and integration plan: [`docs/source_connectors.md`](docs/source_connectors.md)
- Source inventory and integration status: [`config/sources.json`](config/sources.json)
- Draft publication on the database design: [`manuscript/database_paper_draft.md`](manuscript/database_paper_draft.md)
- Existing five-dataset PANGAEA evidence seed: `data/processed` and `data/provenance`
- Editable evidence figures: `figures/*.svg`

The source thesis and full-page thesis images are retained in the local workspace, excluded from Git by default, and are not required to install or run the code. The report viewer is separate from the atlas application and excluded from the Git project.

## Connected sources

Live retrieval status is recorded in [`reports/live_source_check.json`](reports/live_source_check.json).
The latest bounded checks retrieved responses from PANGAEA, NOAA, Neotoma and DataCite. The PANGAEA HTTP 400 was resolved by omitting Accept on explicit textfile requests. These checks do not certify full ingestion or scientific validity.

The Python package provides read-only interfaces for PANGAEA DOI/OAI-PMH retrieval, NOAA/NCEI WDS Paleo JSON search, Neotoma v2 site/dataset/chronology/data endpoints, DataCite DOI discovery and local LiPD `.lpd` packages. Exact API capability and limitations are listed per provider in `config/sources.json`. PaleoMED20, the World Paleoceanographic Atlas, WDB-Paleo and SISAL are registered for source-specific evaluation; this repository does not claim live connectors for those sources yet.

Connector methods return source-native payloads. They do not silently harmonize ages, units, taxa or environmental interpretations. Raw bytes can be recorded by SHA-256 with request/final URLs, retrieval time and content type. Respect the license on each record; a metadata endpoint does not grant reuse rights for the associated values, figures or images.

## Install the local package

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

The connector clients use the Python standard library and do not require API keys for documented public reads. Optional plotting dependencies and their recorded versions are in `requirements-figures.txt`.

Example usage:

```python
from medatlas.connectors import NeotomaConnector, NOAAWDSConnector, PANGAEAConnector

pangaea = PANGAEAConnector()
table_response = pangaea.dataset_table("10.1594/PANGAEA.921230")

noaa = NOAAWDSConnector()
studies, response = noaa.search_studies(dataPublisher="NOAA", headersOnly="true", limit=10)

neotoma = NeotomaConnector()
sites, response = neotoma.search_sites(sitename="Marion Lake")
```

The examples query sources directly and do not stage the returned payloads in the repository. Use the content-addressed preservation helper only after recording the source's reuse terms.

## Reproducir la semilla

Python con biblioteca estándar para descargar, extraer y verificar. Matplotlib para figuras; las versiones usadas se registran en `reports/environment.json`. Si el entorno ya tiene Matplotlib, no hace falta instalar nada.

`requirements-figures.txt` fija las versiones observadas de Matplotlib y sus dependencias en el entorno usado. Es una especificación de reproducción, no una instalación que se haya realizado en un entorno limpio.

```powershell
python scripts/fetch_seed.py
python scripts/prepare_seed.py
python -m unittest discover -s tests -v
python scripts/make_figures.py
```

The data seed can be reproduced from the official PANGAEA DOI endpoints. No age conversion, recalibration, smoothing or interpolation is applied. The long table retains original cell values, locators and hashes. `config/seed.json` declares selected columns. The scripts fail on source format/content changes they cannot handle explicitly.

## Research publication

`manuscript/database_paper_draft.md` is an explicitly labeled manuscript draft about the database design and publication path. It separates software/curation contributions from potential new paleoenvironmental results and makes no claim that the proposed atlas is already complete.

## Verification and source delivery

```powershell
python -m unittest discover -s tests -v
python scripts/check_live_sources.py
python scripts/package_delivery.py
```

The unit suite is offline. Seed-integrity checks require downloaded originals and
are explicitly skipped otherwise. The live-provider command is separate, makes one
bounded request per service and records failures as well as successful retrievals.
GitHub Actions runs offline checks on Windows/Linux with Python 3.10/3.14.
The delivery command exports tracked files only to `../outputs/medatlas-source.zip`;
review `git ls-files` first. Old local thesis-containing archives are private working
artifacts and are not source releases.

## Licenses and citation

The PANGAEA seed datasets retain their CC-BY-3.0 or CC-BY-4.0 licenses. NOAA record-specific licenses are not declared; the documented WDS unrestricted-access reuse basis and required citation are retained, without assigning CC0. Cite the dataset DOI and associated paper. The project does not modify third-party licenses or grant rights over publisher images. A project code license remains to be selected before public release.

## Scientific scope and limits

The original seed contains five records selected to exercise data heterogeneity, not for representativeness. The web v1 expands to 13 records, 22 series and 14,751 values from PANGAEA/NOAA; it remains purpose-selected. LC21 has depth but no sample-age column in the downloaded table. ODP 977 includes an MIS 11 interval. Age models have not been audited. A depth-unit conflict in ODP 977 is preserved and that field must not be used in depth–age joins until resolved.

The counts of 1,026 rows and 2,684 values apply only to this selected seed, not all data available for those sites. Values are not statistically independent samples. These counts do not validate paleoenvironmental interpretations.

## Feasibility-report viewer

`report-app` is a viewer for the feasibility report, not the atlas application. It is a separate historical local artifact; use the online atlas above for the current application.

The local report viewer is outside this software project; the scientific Python package and source connectors do not depend on its runtime.
