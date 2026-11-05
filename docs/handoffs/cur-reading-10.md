# CUR-READING-10: diez entidades Reading v3

- Estado: validado para integración en main; Sites pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama y base: relevo, b75888f. Commit funcional: 613a551; cierre documental posterior consultable en git log.
- Archivos: scripts/build_forest_pollen_v10.py, scripts/importers/pollen_v10_sources.json, tests/test_forest_pollen_v10.py, data/processed/atlas-v10.json, reports/quantitative_v10_release.json, PROJECT_STATE y RELEVO.
- Resultado: CERRATO, MOLINAES, LAGMESAG, VERDEOSPESOA, MAI, SANABRIA, PINOBLANCO, BOSCESTA, ARBARRAIN y CADELA. Diez ubicaciones, 60 series, 6.810 valores nuevos. Total 193/1.594/951.460, 1.000 grupos; v10-cf8f572c33a.
- Decisiones: parser v9 reutilizado; IDs reading9 conservan su identidad de fuente. Ambos contratos y padre fijados por hash. Originales ignorados reutilizados sin descargas. Se mantienen las seis variables, suma de 205 taxones, CC BY 4.0, ceros, BP negativos e incertidumbre original sin reinterpretarla. MAI/MOLINAES usan las correcciones documentadas de v3.
- Evidencia: `python scripts/build_forest_pollen_v10.py`; 85 pruebas Python y 15 Node requeridas correctas. Snapshot/check-snapshot sobre atlas-v10.json: 951.460 valores comparados celda a celda, 1.002 archivos, máximo 2,3 MiB. Sin cuarentena ni solapamientos numéricos parciales detectados; padre íntegro. Instantánea local outputs/reading-v10-snapshot ignorada.
- Límites: porcentajes derivados, no cubierta forestal. Unidades originales mixtas documentadas. Proximidad registrada como cribado, sin inferir identidad. Villarquemado tiene 361 medianas IntCal20 ausentes; requiere contrato IPE separado. Costa, ELX y Monticchio siguen pendientes. La consulta web Reading falló; documentación original local verificada por hash.
- Siguiente: rol 04 publica main con v10 tras regenerar/verificar snapshot y compilar. Después ampliar Reading excluyendo las 39 entidades de ambos contratos.
