# CUR-READING-14: diez entidades Reading v3

- Estado: validado para integración en main; publicación reservada al rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, 1ebb4e5. Registro 9e44d68; commit funcional ed1070b; cierre posterior en git log.
- Archivos: build_forest_pollen_v14.py, pollen_v14_sources.json, test_forest_pollen_v14.py, atlas-v14.json, quantitative_v14_release.json; estado y relevo.
- Resultado: LABRADILLOS, BOTIJA, LANCHAS, BOSSIER, AGUASFRIAS, BERMU, REDONDO, VALDEYER, XL y LECHE. 359 muestras, 60 series y 2.154 valores nuevos. Total 233/1.834/962.836, 1.000 grupos; v14-c21d91a390a.
- Decisiones: originales por hash, parser v9 y ensamblador v10 reutilizados sin cambios. Conserva seis parámetros, suma de 205 taxones, CC BY 4.0, ceros, edades BP negativas e incertidumbres originales sin reinterpretación. XL mantiene la corrección del tratamiento de fechas postmodernas del techo documentada en el readme v3, con nota única por registro y serie. No se inventan DOI ausentes en BOTIJA/BERMU; referencia íntegra preservada.
- Evidencia: 107 pruebas Python, 15 Node; snapshot/check-snapshot compara 962.836 valores, 1.002 archivos, máximo 2,3 MiB. Sin cuarentenas ni solapamientos numéricos parciales detectados. Vectores completos cotejados contra padre y entre nuevos. Sin consultas remotas; originales locales verificados.
- Límites: proximidad archivada como cribado, sin certificar independencia física exhaustiva. Unidades originales mixtas y bloqueos anteriores conservados. 79/122 entidades Reading incorporadas; 43 restantes no equivalen a 43 admisibles. Sin compilación ni publicación de Sites.
- Siguiente: rol 04 publica main con atlas-v14.json tras regenerar/verificar snapshot y compilar. Producción continúa en v13. Candidatas para otro lote en RELEVO; excluir las 79 entidades de contratos v9–v14.
