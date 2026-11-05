# CUR-READING-17: cinco entidades de diez revisadas

- Estado: validado para integración; Sites pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Base: a745ebb; registro bebd825; commit funcional 5d6785c; cierre posterior en git log.
- Archivos: build_forest_pollen_v17.py, pollen_v17_sources.json, test_forest_pollen_v17.py, atlas-v17.json, quantitative_v17_release.json; ensamblador/pruebas comunes v10 y estado/relevo.
- Resultado: CANDIEIR, CreixellT, TRAVESS1, VdL PB2 y ADP 01/06. 565 muestras, 30 series y 3.390 valores nuevos. Total 256/1.972/971.380, 1.000 grupos; v17-c6564e1246e.
- Fuentes: [fechas Reading v3](https://researchdata.reading.ac.uk/369/23/Iberia_data_dates_v3.csv), 76.390 bytes, SHA a9bde3e7c9e063ea05e2fcb639596f5a2ecca961ca5c8221a8d7f851ae1986a6; [PEX19-01](https://doi.pangaea.de/10.1594/PANGAEA.954457) identifica Peixao, distinto de Candieira. Consulta 05-11-2026; CC BY 4.0 Reading.
- Decisiones: se conservan 64 controles originales, cinco exclusiones de Candieira, techo asumido, exclusión ADP y notas de correlación VdL/VDL 02/08. Age_used vacío permanece no especificado. Archivos costeros/estuarinos explícitos, sin inferir deposición exclusivamente terrestre. Seis proxies y denominadores previos conservados; sin recalibración ni interpolación local.
- Retenidas: ROQUETAS/ALCUDIA/Abi 05/07 por materiales ambiguos; Vilamora por conchas sin tratamiento de reservorio verificado; LLIGAT por reservorio y posible signo de longitud incorrecto. Filas de fechas en contrato.
- Evidencia: 126 pruebas Python, 15 Node y snapshot de 971.380 valores cotejados; 1.002 archivos, máximo 2,3 MiB. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados. Reproducción v16 idéntica en contenido.
- Límites/siguiente: 102/122 entidades incorporadas; 20 requieren auditoría dirigida según RELEVO. Independencia física/reservorios no certificados exhaustivamente. Rol 04 publicará atlas-v17.json tras regenerar/verificar snapshot y compilar; producción sigue en v13.
