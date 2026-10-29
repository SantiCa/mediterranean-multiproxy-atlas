# Handoff — CUR-PRIORIDAD (Claude, rama claude/curado)

29-10-2026. Rama propia desde codex/draft-quantitative-v4 (8239b28) porque otra sesión de Claude trabaja en `relevo` (URL/Cloudflare). No tocar `relevo` desde esta rama hasta fusionar.

Petición de Santiago (29-10): seguir la curación de ChatGPT añadiendo sondeos; priorizar proxies con más sondeos (mapas), y especialmente foraminíferos, oxigenación/materia orgánica y todo lo que tenga bioturbación.

- El entorno de Claude no llega a PANGAEA/DataCite/NOAA/Crossref (proxy 403). Se usa `.github/workflows/curation.yml` en runners de GitHub.
- `scripts/discovery/proxy_coverage.py`: cola de priorización por familia (eventos distintos, con columna AGE, no curados). Informe en `reports/proxy_coverage_pangaea.json` y `docs/curation/proxy_coverage_pangaea.md`.
- Job `reproduce-v4`: descarga originales del borrador v4, recompila atlas-v4 y pasa pruebas (revisión del trabajo de ChatGPT).
- Siguiente: con el informe, elegir lotes v5 (foraminíferos → TOC/redox → bioturbación) con contrato de columnas/edad/licencia, igual que v4.
