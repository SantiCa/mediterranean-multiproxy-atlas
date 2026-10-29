# Handoff — lote NOAA cuantitativo v3

Base coordinador: main 523a1f1; sin commit ni publicación por este agente. Archivos propios: scripts/importers/curate_noaa_v3.py, noaa_v3_sources.json; tests/test_noaa_v3.py; reports/noaa_v3_audit.json; docs/curation/noaa_v3.md.

Fragmento ignorado preparado en data/interim/quantitative_v3/noaa_curated.json: 7 registros de sitio, 52 series, 28.806 celdas finitas. Estudios NOAA 32914 (4 cores marinos), 28070 (1 core Ohrid/6 tablas), 13666 (2 cores Bourget). inventory_ids son enlaces exactos estudio/sitio, no inferencias por proximidad. Originales y metadata en data/interim/quantitative_v3/noaa; hashes exigidos por contrato. Reproducir offline con el script; --fetch solo recupera ausentes con hashes exactos.

Integrar solamente records/series, NO quarantined_series. Allí se conserva %terr LDB04-I: 18 valores>100, máximo124,2; 1.371 filas pendientes, sin recorte. Cadagno con edades intervalares queda excluido. Ohrid: 61 valores válidos sin edad; 12 #DIV/0! excluidos; edad orbitalmente ajustada, máximo1.365ka. NOAA2019 vsartículo2020 preservados; filtro2020. SSTConte2006 separada deMüller1998, MAATcalibraciones ydenominadorespolínicos separados.

Cada serie tiene hash/URL/tabla/definiciones/filas. RegistroOhrid raw_sha256=null porque6archivos; exportar hash/URL de la serie. Repeticionesedad/valor se cuentan,no borran (OhridXRF1132pares adicionales); no asumir independencia estadística. LicenciaCCno declarada, políticaWDSdocumentada.

Cinco pruebas pasan, incluida comparación de todas las celdas contra originales. Falta revisión cruzada PANGAEA y ensamblado/deploy del coordinador. Conservar atlas-v1.json como baseline para detección de DOI/hash repetidos y reproducción.
