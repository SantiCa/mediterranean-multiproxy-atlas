# CUR-READING-13: diez entidades Reading v3

- Estado: validado para integración en main; publicación reservada al rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, 20a43bb. Registro a303340; commit funcional 7646775; cierre posterior en git log.
- Archivos: build_forest_pollen_v13.py, pollen_v13_sources.json, test_forest_pollen_v13.py, atlas-v13.json, quantitative_v13_release.json; estado y relevo.
- Resultado: CUETOAV, N-SAL, LANZBOG, CUAII, PRD4, PATATERO, SERTAL, TORNOS01, ESTACAS y N-PEQ. 328 muestras, 60 series y 1.968 valores nuevos. Total 223/1.774/960.682, 1.000 grupos; v13-c0f960a7901.
- Decisiones: reutiliza originales por hash, parser v9 y ensamblador v10 sin cambios. Mantiene seis parámetros, suma de 205 taxones, CC BY 4.0, ceros, BP negativos e incertidumbres sin reinterpretación. PATATERO conserva la corrección del techo de v3. N-PEQ cita el dataset PANGAEA.738850: related_paper_dois vacío, fuente y cronología incorporadas siguen siendo Reading v3.
- Evidencia: 101 pruebas Python, 15 Node; snapshot/check-snapshot compara 960.682 valores, 1.002 archivos, máximo 2,3 MiB. Sin cuarentenas ni solapamientos numéricos parciales detectados. Comprobación exacta de todos los vectores nuevos, también los menores de diez muestras, sin coincidencias completas con el padre ni entre ellos. Sin consultas remotas; originales locales verificados.
- Límites: SERTAL y ESTACAS tienen nueve muestras, sin interpolación ni resolución uniforme inferida. Proximidad archivada como cribado; no certifica independencia física exhaustiva. Bloqueos anteriores conservados. Sin compilación ni publicación de Sites.
- Siguiente: rol 04 publica main con atlas-v13.json tras regenerar/verificar snapshot y compilar. Otro lote excluirá las 69 entidades de los contratos v9–v13.
