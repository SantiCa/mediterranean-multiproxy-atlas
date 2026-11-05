# CUR-READING-11: segundo lote de diez entidades Reading v3

- Estado: validado para integración en main; publicación reservada al rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, 3311929. Registro 130af23; commit funcional 8d94c65; cierre posterior en git log.
- Archivos: ensamblador build_forest_pollen_v10.py parametrizado; build_forest_pollen_v11.py, pollen_v11_sources.json, test_forest_pollen_v11.py, atlas-v11.json, quantitative_v11_release.json; estado y relevo.
- Resultado: LAGNEGRA, AYOO, LAGOAJO, LASPARDI, SALDROPO, TUB, PALANQUES, PERAFITA, BELATE01 y CULAZON. 747 muestras, 60 series, 4.482 valores nuevos. Total 203 registros / 1.654 series / 955.942 valores, 1.000 grupos; v11-c58348d32e0.
- Decisiones: reutiliza originales por hash, parser v9 y ensamblador v10. Conserva seis variables, suma de 205 taxones, CC BY 4.0, ceros y edades negativas, incertidumbres originales sin reinterpretación. IDs reading9 mantienen identidad de fuente. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados; distancias archivadas solo como cribado.
- Evidencia: `python scripts/build_forest_pollen_v11.py`; 90 pruebas Python, 15 Node. Snapshot/check-snapshot: 955.942 valores cotejados celda a celda, 1.002 archivos, máximo 2,3 MiB. Reconstrucción de v10 idéntica en contenido. Sin consultas remotas: originales locales verificados por hash.
- Límites: PEDRIDO, 63/71 sumas nulas, retenido entero con filas trazadas. Sumas pequeñas (LAGOAJO mínimo 16) conservadas; no inferir precisión de conteos con unidades mixtas. Costa, ELX, Villarquemado y Monticchio siguen pendientes. No se ha compilado ni publicado el Site.
- Siguiente: rol 04 publica main usando atlas-v11.json tras regenerar/verificar snapshot y compilar; referencia ignorada outputs/reading-v11-snapshot. Otro lote excluirá las 49 entidades de los contratos v9/v10/v11.
