# NOAA v4 — handoff

Base atlas-v3.json inmutable. Archivos propios: curate_noaa_v4.py, noaa_v4_sources.json, tests/test_noaa_v4.py, reports/noaa_v4_audit.json, docs/curation/noaa_v4.md. Fragmento ignorado quantitative_v4/noaa_curated.json.

6 nuevos registros /22 series/17.924 valores, 6 estudios continentales: Kaite33716,Trio11817,Ifoulki23970,Redon22582,Silvaplana13017,Monticchio5463. Solo integrar records/series; quarantined_series contiene7series/3.007valores. No se recortaron concentraciones negativas ni se derivaron edades.

Kaite tiene coordenadas TXT/JSON discordantes: gobierna coordenada primaria Cruz2021 43°2′N3°39′W, decimal43.0333333333/−3.65; ambas originales conservadas. Ifoulki/Redon fijan cp1252 pese a declaraciónUTF8. Silvaplana es índiceXRD normalizado (negativosválidos). Monticchio incorpora corrección de Si publicada, con74ceros (73 provenientes de estimacionesnegativas); origen derivado explícito.

Nuevos chronology_status con label humano ya suministrado: published_uranium_thorium,published_calendar_as_archived,published_lamination_BP. No reemplazar labels por códigos. Fuente/hash a nivelserie; records multitabla no fingen hashúnico.

5 pruebas correctas: todoslos valores/edades/errores/localizadores contra originales, cuarentenas, baseline duplicados, unidades/representaciones. Sin commit/push/deploy ni cambios compartidos. Siguiente: revisión independiente de cronologías, negativos analíticos y convenciones de Monticchio.
