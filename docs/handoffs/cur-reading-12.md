# CUR-READING-12: diez entidades interiores Reading v3

- Estado: validado para integración en main; Sites pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, 0592029. Registro 5feab74; commit funcional b52b7ee; cierre posterior en git log.
- Archivos: build_forest_pollen_v10.py admite notas del contrato; build_forest_pollen_v12.py, pollen_v12_sources.json, test_forest_pollen_v12.py, atlas-v12.json, quantitative_v12_release.json; estado y relevo.
- Resultado: ADAJA, ALSA, NAVALACA, VALDECON, CARCAVAS, ATXURI01, QUINTA02, AREO, LAMEIRAS y TIEMBLO. 462 muestras, 60 series y 2.772 valores nuevos. Total 213/1.714/958.714, 1.000 grupos; v12-cbfb32f9dfc.
- Decisiones: originales y parser fijados por hash. Se mantienen seis parámetros, suma de 205 taxones, CC BY 4.0, BP negativos, ceros e incertidumbre original sin reinterpretación. QUINTA02 conserva la corrección de fechas de v3 frente a v2, documentada en el readme, con nota única por registro/serie.
- Evidencia: 95 pruebas Python, 15 Node; snapshot/check-snapshot compara 958.714 valores, 1.002 archivos, máximo 2,3 MiB. Reconstrucción v11 idéntica en contenido. Sin cuarentenas ni solapamientos numéricos parciales detectados.
- Identidad: QUINTA02 y LASPARDI distan 0,01663 grados; Reading declara sitios distintos, elevaciones 1.470/1.850 m y referencias diferentes. Proximidad archivada, sin fusionar ni afirmar independencia exhaustiva. Consulta bibliográfica adicional consistente; DOI primarios inaccesibles mediante web, decisión sustentada en la compilación local verificada.
- Límites: porcentajes derivados, no cubierta forestal. Pedrido, ELX, costa, Villarquemado y Monticchio siguen pendientes. Sin compilación ni publicación de Sites.
- Siguiente: rol 04 publica main con atlas-v12.json tras regenerar/verificar snapshot y compilar. Otro lote excluirá las 59 entidades de los contratos v9–v12.
