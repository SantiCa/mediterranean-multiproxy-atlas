# CUR-READING-15: diez entidades Reading v3

- Estado: validado para integración en main; Sites pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, 2b88a58. Registro 28d193a; versión corregida a535bfb; cierre posterior en git log.
- Archivos: build_forest_pollen_v15.py, pollen_v15_sources.json, test_forest_pollen_v15.py, atlas-v15.json, quantitative_v15_release.json; guardia cronológica en ensamblador v10; estado/relevo.
- Resultado: PANERA, LACRUZ, BREZOSA, ELPERRO, VINUELAS, VILLUERCAS, MITJANA, ELPAYO, Ojos del Tremendal core 1 y SALOIO. 386 muestras, 60 series, 2.316 valores nuevos. Total 243/1.894/965.152, 1.000 grupos; v15-c43715a903d.
- Decisiones: originales por hash; seis variables, suma de 205 taxones, CC BY 4.0, BP negativos, ceros e incertidumbre original conservados. VILLUERCAS usa mediana IntCal20, sin mezclar IPE.
- Auditoría: CANALEJA retenida: [PANGAEA.835786](https://doi.pangaea.de/10.1594/PANGAEA.835786) repite coordenadas Reading (40,9; −2,45) pero cita Romangordo; artículo inaccesible por Anubis, posición corregida sin verificar. CUCU tiene medianas hasta 130 ka; [IntCal20](https://doi.org/10.1017/RDC.2020.41) cubre 0–55 ka. Se retiene entero para contrato específico; guardia impide nuevas admisiones fuera de dominio. No se recortan edades.
- Evidencia: 114 pruebas Python, 15 Node; snapshot/check-snapshot coteja 965.152 valores, 1.002 archivos, máximo 2,3 MiB. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados; vectores completos auditados. No publicar v15-c238c8dd19b, provisional sustituida.
- Límites: independencia física no certificada exhaustivamente; bloqueos anteriores conservados. 89/122 entidades incorporadas, 33 pendientes. Sin compilación ni publicación.
- Siguiente: rol 04 publica main con atlas-v15.json tras regenerar/verificar snapshot y compilar; producción sigue en v13.
