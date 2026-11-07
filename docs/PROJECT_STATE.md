# Estado breve del proyecto

Actualizado el 07-11-2026. Repositorio privado `SantiCa/mediterranean-multiproxy-atlas`. Consultar git log para el commit efectivo.

## Colección v26 validada en relevo (07-11-2026)

- v26-cc3b334b8f6 reúne **269 registros, 2.098 series, 1.026.061 observaciones y 1.072 grupos base**. Añade 13 series y 1.704 observaciones de cuatro tablas, con dos testigos nuevos del Nilo. Fuentes y decisiones en docs/handoffs/cur-common-26.md.
- δ¹³C del TOC reúne cuatro series bajo un nombre de consulta. Se comprobaron 22 vistas. Pasaron 146 Python, 44 Node, TypeScript, compilación y snapshot íntegro. Auditorías con cero errores. Integración y publicación para rol 04.

## Colección v25 validada (07-11-2026)

- v25-c4c7fe7c54e reúne **267 registros, 2.085 series, 1.024.357 observaciones y 1.062 grupos base**. Añade 11 series y 21.457 observaciones de Prespa, Ohrid y Baleares. Fuentes y límites en docs/handoffs/cur-common-25.md.
- Alias Ca/Al y criterio de admisión CaCO₃ revisados. Catálogo completo y 21 vistas filtradas sin conjuntos de series agregadas idénticos. Pasaron 146 Python, 43 Node, TypeScript, compilación y snapshot completo. Auditorías con cero errores. Integración y publicación para rol 04.

## Colección v24 validada en relevo (07-11-2026)

- v24-c17c40ccf3b reúne **267 registros, 2.074 series, 1.002.900 observaciones y 1.051 grupos base**. Siete series y 14.322 observaciones de calcio XRF, granulometría y δ¹⁸O planctónico en dos testigos existentes del golfo de León. Fuentes y límites en docs/handoffs/cur-common-24.md.
- Catálogo completo y 21 vistas filtradas sin membresías agregadas idénticas. Verificadas las unidades XRF y las fracciones granulométricas. Pasaron 146 pruebas Python, 42 Node, TypeScript, compilación y snapshot completo. Auditorías con cero errores. Integración y publicación para rol 04.

## Colección v23 validada en relevo (07-11-2026)

- v23-c339e7f2aa6 reúne **267 registros, 2.067 series, 988.578 observaciones y 1.047 grupos base**. Añade 34 series y 3.461 observaciones de GDGT, SST, UK′37 e isótopos por especie. Cuatro eventos nuevos, con los sondeos de U1387 pertenecientes al mismo sitio. Fuentes y límites en docs/handoffs/cur-common-23.md.
- Cotejadas las membresías de los 144 agregados. Rótulos estivales diferenciados según el alcance de la selección. Pasaron 146 pruebas Python, 42 Node, TypeScript, compilación y snapshot íntegro. Auditorías con cero errores. Integración y publicación para rol 04.

## Colección v22 validada en relevo (07-11-2026)

- v22-cf1f6241933 reúne **263 registros, 2.033 series, 985.117 valores y 1.034 grupos base**. Añade siete series y 4.426 observaciones de susceptibilidad volumétrica, SST y biomarcadores. Lungo y 161-977A enlazados a eventos existentes. Identidad cruzada de D13902 pendiente. Fuentes y límites en docs/handoffs/cur-common-22.md.
- Tarjeta anual SST consolidada con 22 series de 16 registros. La reconstrucción de 0–200 m conserva su grupo específico.
- 146 pruebas Python, 42 Node, TypeScript, compilación y snapshot completo verificados. Auditorías con cero errores. Integración y publicación para rol 04.

## Colección v21 validada en relevo (07-11-2026)

- v21-c80c881825a reúne **262 registros, 2.026 series, 980.691 valores y 1.027 grupos base**. Siete series y 5.610 valores de susceptibilidad magnética, isótopos de ostrácodos, micro-XRF y SST publicada. Dos registros nuevos. Tabla de fuentes y límites en docs/handoffs/cur-common-21.md.
- UK′37 reúne 11 series y 1.108 valores bajo un nombre y unidad de consulta comunes. TIC reúne 10 series y 685 valores. Se normaliza la escritura de Br/Ti y Sr en cocientes sin alterar logaritmos, métodos ni unidades archivadas.
- 146 pruebas Python, 41 Node, TypeScript, compilación y snapshot de 1.029 archivos correctos. La admisión cotejó el esquema y cada observación nueva con su origen. Auditorías con cero errores. Rol 04 tiene la integración y publicación.

## Colección v20 publicada en Sites (07-11-2026)

- v20-cf635885fac: **260 registros / 2.019 series / 975.081 valores / 1.020 grupos base**. Tres series/98 valores de carbono orgánico, N y P lábil en BEN14-P4 existente; sin nuevas ubicaciones independientes. Padre v19, esquema y cuarentenas anteriores intactos.
- Alias TOC/total organic carbon/C org/sed y razones elementales (Ti/Ca, etc.) unificados para consulta. Un agregado TOC % completo: 24 registros/31 series. CaCO3 normalizado; grupos base, unidades, fracciones, métodos, logaritmos y bases de cocientes incompatibles conservados por separado. Detalle docs/curation/groups_v20.md.
- 146 Python sin omisiones, 39 Node, tsc/build y snapshot íntegro (975.081 valores/1.022 archivos). Auditorías sin errores, avisos heredados sin cambios; 38 contextos de alias comprobados. Reproducción v19 idéntica. Recibo common_v20_validation.json y handoff cur-groups-20.md.
- PANGAEA.667403 en cuarentena por TOC negativo; 993109 retenida por unidades de edad contradictorias. Sin correcciones implícitas. Auditoría rol 02 intacta. Se deja en relevo: push a main activaría publicación automática de Cloudflare; integración y publicación siguen reservadas al rol 04.

## Colección v19 validada, sustituida por v20 en relevo (06-11-2026)

- v19-c4262530e6b: **260 registros / 2.016 series / 974.983 valores / 1.017 grupos**. Añade 38 series/5.182 valores de seis datasets PANGAEA en ocho entidades. Dos nuevos testigos de Marmara comparten una ubicación; seis registros existentes enriquecidos. Padre v18 y cuarentenas intactos.
- Nueva prioridad: proxies comunes e índices consolidados. Esta tanda incorpora δ18O/δ13C por especie, UK′37/TEX86/LDI/BIT, SST moleculares y MAT/SIMMAX28, producción exportada por transferencia. Nombre, unidad e interpretación ambiental explícitos en campos existentes; estructura y nueve celdas por observación sin cambios. Detalle y unidades en docs/curation/common_v19.md.
- Reproducción: `python scripts/build_common_v19.py --fetch`; contrato common_v19_sources.json y originales/TSV/XML por hash. Calibraciones, estaciones, especies y correcciones separadas; incertidumbres nativas inequívocas conservadas. TEX86 Mar Negro 0–200 m y SST sin calibración específica declarada tienen contextos propios. PANGAEA.939418 retenido por dos eventos sin columna Event. No se inventan CIA ni paleoredox desde razones radiométricas/cuentas.
- Cobertura de la categoría nativa Temperatura: 26→30 ubicaciones fechadas; Isótopos estables: 34→35. No es un inventario mundial, cobertura SST exclusiva ni garantía de calidad de interpolación; los métodos conservan sus grupos de comparación.
- 142 Python sin omisiones, 36 Node, tsc/build y snapshot íntegro (974.983 valores/1.019 archivos). Auditorías sin errores estructurales; avisos del padre y nuevo par coincidente explícitos. Recibo common_v19_validation.json; handoff cur-common-19.md. Publicación reservada al rol 04; última referencia de producción registrada v13.

## Colección v18 validada, sustituida por v19 (05-11-2026)

- v18-cd0f8159f62: **258 registros / 1.978 series / 969.801 valores / 994 grupos**. Armena/PEDRIDO añaden 12 series/300 valores de 50 muestras. Las 124 muestras originales y 57 controles siguen auditados; 74 sumas nulas excluidas explícitamente, sin imputación.
- Incorpora las conclusiones Atlas 02 y QC V30: corrige 1.807 edades de 19 series Mondsee por cambio de referencia, sin recalibración, y retiene seis duplicados (1.879 valores). Objetos originales completos en seed.curation_excluded_series y en v17. Las 25 excepciones están declaradas; resto del padre y todos sus registros intactos.
- Reproducción: `python scripts/build_forest_pollen_v18.py --fetch`; contrato pollen_v18_sources.json. Mondsee conserva ambos encabezados ambiguos: la segunda columna coincide numéricamente con años BP pese a su rótulo AD/CE. El intervalo publicado 1500 BCE–500 CE respalda la transformación; no se interpreta el segundo encabezado como control independiente.
- 136 Python aisladas por archivo, sin omisiones; 36 Node, tsc/build y snapshot de 969.801 valores cotejados: 994 grupos/996 archivos. Auditorías científica/de uso sin errores estructurales; avisos conocidos preservados. Recibo reports/reading_v18_validation.json. V17 reproducida sin cambios de contenido; no se certifica validación científica exhaustiva.
- QC incorporado científicamente: config/qc_corrections.json vacío; semillas antiguas necesitan su configuración histórica. Informes provisionales conservados como evidencia histórica, no como recuentos vigentes. Creador de proxies y escala configurable conservados. 104/122 entidades Reading incorporadas, dos parcialmente; ELX/Estanya mantienen bloqueos. Producción v13; publicación reservada al rol 04.

## Auditoría de uso y creador de proxies (05-11-2026, validada junto con v18)

Auditoría reproducible de todas las celdas v17, más cribado adicional de v18 provisional; informes `reports/proxy_use_audit.json` y `reports/proxy_use_v18_provisional_audit.json`. Selector incluye registros únicos, familias de consulta coherentes, OI Rock-Eval corregido, SST sin estación separada de anual y contexto de sumas polínicas conservado. Creador de sumas/relaciones/proporciones de abundancias con muestras nativas, opción multisondeo compatible, recetas locales y exportación de originales/fórmulas/exclusiones. 133 Python, 34 Node, tsc/build, snapshot v17 y QA escritorio correctos. Integración en main pendiente del cierre de CUR-READING-18 provisional; producción v13. Límites en docs/curation/proxy_use_audit.md y handoff docs/handoffs/aud-proxy-uso.md.

## Colección v17 validada, pendiente de publicar (05-11-2026)

- Release v17-c6564e1246e: **256 registros / 1.972 series / 971.380 valores / 1.000 grupos base**. Cinco entidades Reading v3 admitidas de diez revisadas: CANDIEIR, CreixellT, TRAVESS1, VdL PB2 y ADP 01/06. 565 muestras, 30 series y 3.390 valores nuevos; padre v16 íntegro.
- Reproducción: `python scripts/build_forest_pollen_v17.py`; contrato pollen_v17_sources.json e informe quantitative_v17_release.json. Añade la tabla oficial Iberia_data_dates_v3.csv fijada por hash y 64 controles con celdas, filas, materiales y notas originales en record.reading_dates_audit. Age_used vacío significa no especificado, no aceptación explícita. No se recalibran edades.
- Candieira se distingue de PEX19-01 (lago Peixao) con la ficha primaria PANGAEA.954457. Archivos costeros/estuarinos etiquetados; el grupo continental operativo de polen no demuestra deposición exclusivamente terrestre. VdL conserva la dependencia publicada respecto del testigo paralelo VDL 02/08, sin interpolación local.
- 126 pruebas Python, 15 Node y snapshot con 971.380 valores cotejados celda a celda. v16 reproducida sin cambios de contenido; sin cuarentena de admisión ni solapamientos numéricos parciales detectados. Handoff docs/handoffs/cur-reading-17.md. No se certifica independencia física exhaustiva ni ausencia de reservorio en sedimento total.
- ROQUETAS, ALCUDIA, Vilamora P01-5, Abi 05/07 y LLIGAT retenidas con sus filas de fechas por materiales/reservorio/posición. Contratos v9–v17: 102/122 entidades incorporadas; 20 restantes con bloqueos específicos. Producción sigue en v13; publicación de v17 reservada al rol 04.

## Colección v16 validada, sustituida por v17 (05-11-2026)

- Release v16-cc875bfb999: **251 registros / 1.942 series / 967.990 valores / 1.000 grupos base**. Ocho ubicaciones Reading v3 nuevas, 473 muestras, 48 series y 2.838 valores. Padre v15 íntegro; seis parámetros y denominadores conservados.
- Reproducción: `python scripts/build_forest_pollen_v16.py`; contrato pollen_v16_sources.json e informe quantitative_v16_release.json. Originales por hash e importadores existentes reutilizados sin cambios. Las exclusiones de carbón de PozoN_2015 no se trasladan automáticamente al polen: se conservan sus 41 muestras publicadas y se documenta la diferencia.
- 120 pruebas Python, 15 Node y snapshot con 967.990 valores cotejados celda a celda. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados; vectores completos auditados. Handoff docs/handoffs/cur-reading-16.md. La proximidad se registra como cribado, sin certificar independencia física exhaustiva.
- Armena retenida por 11/53 muestras de suma nula; Estanya Catena por 2/92. Filas explícitas en contrato e informe; no se convierten en porcentajes cero ni se imputan. Lote acotado a diez candidatas: ocho admitidas, dos retenidas.
- Producción sigue en v13; publicación de v16 reservada al rol 04. Contratos v9–v16: 97/122 entidades Reading incorporadas; 25 restantes incluyen bloqueos, cronologías marinas e identidades pendientes.

## Colección v15 validada, sustituida por v16 (05-11-2026)

- Release v15-c43715a903d: **243 registros / 1.894 series / 965.152 valores / 1.000 grupos base**. Diez ubicaciones Reading v3 nuevas, 386 muestras, 60 series y 2.316 valores. Padre v14 íntegro; seis parámetros y suma armonizada de 205 taxones conservados.
- Reproducción: `python scripts/build_forest_pollen_v15.py`; contrato pollen_v15_sources.json e informe quantitative_v15_release.json. Originales fijados por hash e importadores reutilizados. VILLUERCAS usa exclusivamente INTCAL2020_median, preservando IPE en auditoría.
- 114 pruebas Python, 15 Node y snapshot con 965.152 valores cotejados celda a celda. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados; vectores completos auditados. Handoff docs/handoffs/cur-reading-15.md. No se certifica independencia física exhaustiva.
- CANALEJA retenida por posible incoherencia entre coordenadas y referencia. CUCU retenida por valores INTCAL2020_median hasta 130 ka: requieren contrato cronológico específico, fuera del dominio 0–55 ka de IntCal20 (Reimer et al. 2020, DOI 10.1017/RDC.2020.41). El ensamblador rechaza nuevas edades >55 ka bajo este contrato. Ojos del Tremendal y Saloio completan el lote; la versión provisional de v15 se sustituye.
- Producción sigue en v13; publicación de v15 reservada al rol 04. Contratos v9–v15: 89/122 entidades incorporadas; 33 restantes incluyen bloqueos y solapamientos pendientes.

## Colección v14 validada, sustituida por v15 (05-11-2026)

- Release v14-c21d91a390a: **233 registros / 1.834 series / 962.836 valores / 1.000 grupos base**. Diez ubicaciones Reading v3 nuevas, 359 muestras, 60 series y 2.154 valores. Padre v13 íntegro; seis parámetros y suma armonizada de 205 taxones conservados.
- Reproducción: `python scripts/build_forest_pollen_v14.py`; contrato pollen_v14_sources.json e informe quantitative_v14_release.json. Originales fijados por hash e importadores existentes reutilizados sin cambios. XL conserva el tratamiento corregido de fechas postmodernas del techo publicado en v3.
- 107 pruebas Python, 15 Node y snapshot con 962.836 valores cotejados celda a celda. Sin cuarentenas ni solapamientos numéricos parciales detectados; auditoría exacta adicional de todos los vectores nuevos. Handoff docs/handoffs/cur-reading-14.md. No se certifica independencia física exhaustiva.
- Producción permanece en v13, según recibo reports/reading_v13_sites_deployment.json. Publicación de v14 reservada al rol 04. Los contratos v9–v14 incorporan 79/122 entidades Reading; las 43 restantes incluyen bloqueos anteriores y casos de identidad/cronología pendientes.

## Colección v13 publicada (05-11-2026)

- Release v13-c0f960a7901: **223 registros / 1.774 series / 960.682 valores / 1.000 grupos base**. Diez ubicaciones Reading v3 nuevas, 328 muestras, 60 series y 1.968 valores. Padre v12 íntegro; seis parámetros y denominadores conservados.
- Reproducción: `python scripts/build_forest_pollen_v13.py`. Contrato pollen_v13_sources.json e informe quantitative_v13_release.json. Originales por hash y ensamblador existentes reutilizados. PATATERO conserva la corrección del techo publicada en v3. N-PEQ mantiene PANGAEA.738850 como referencia de dataset, sin atribuirlo como DOI de artículo ni cambiar la cronología Reading.
- 101 pruebas Python, 15 Node y snapshot completo cotejado celda a celda. Sin cuarentenas ni solapamientos numéricos parciales detectados. Auditoría exacta adicional incluye vectores de menos de diez muestras: SERTAL y ESTACAS conservan sus nueve muestras cada uno, con advertencia. Handoff docs/handoffs/cur-reading-13.md.
- Publicación v13 registrada en reports/reading_v13_sites_deployment.json; acceso privado conservado. Continúan los bloqueos anteriores; no se certifica independencia física exhaustiva ni resolución uniforme.

## Colección v12 validada, sustituida por v13 (05-11-2026)

- Release v12-cbfb32f9dfc: **213 registros / 1.714 series / 958.714 valores / 1.000 grupos base**. Diez ubicaciones Reading v3 nuevas, 462 muestras, 60 series y 2.772 valores. Padre v11 íntegro; seis parámetros polínicos y denominadores conservados.
- Reproducción: `python scripts/build_forest_pollen_v12.py`; contrato pollen_v12_sources.json e informe quantitative_v12_release.json. Reutiliza originales por hash y ensamblador parametrizado; notas científicas específicas del contrato llegan al registro y a sus series. QUINTA02 usa la cronología corregida de v3, documentada en el readme original.
- 95 pruebas Python, 15 Node y snapshot completo cotejado celda a celda. Reproducción de v11 idéntica en contenido. Sin cuarentenas ni solapamientos numéricos parciales detectados en este lote; no se certifica independencia física exhaustiva. Handoff docs/handoffs/cur-reading-12.md.
- Sites sigue en v9; publicación de v12 reservada al rol 04. Se mantienen los bloqueos de Pedrido, ELX, Villarquemado, entidades costeras y Monticchio.

## Colección v11 validada, sustituida por v12 (05-11-2026)

- Release v11-c58348d32e0: **203 registros / 1.654 series / 955.942 valores / 1.000 grupos base**. Diez ubicaciones Reading v3 nuevas, 60 series y 4.482 valores; padre v10 íntegro. Abies, Alnus, Betula, Fagus, Pinus y Quercus deciduo conservan su contexto de comparación y denominadores.
- Reproducción: `python scripts/build_forest_pollen_v11.py`; originales y parser v9 fijados por hash, ensamblador v10 parametrizado. La reproducción de v10 conserva la semilla y el informe sin cambios de contenido. Contrato pollen_v11_sources.json e informe quantitative_v11_release.json.
- 90 pruebas Python, 15 Node y snapshot con 955.942 valores cotejados celda a celda. Sin cuarentena de admisión ni solapamientos numéricos parciales detectados. Handoff docs/handoffs/cur-reading-11.md. No se afirma independencia física exhaustiva.
- PEDRIDO permanece en espera: 63/71 muestras con suma retenida nula, filas explícitas en contrato. Sumas pequeñas (mínimo 16 en LAGOAJO) se conservan, sin asignar precisión de conteos a unidades originales ambiguas. Sites sigue en v9; publicación de v11 reservada al rol 04.

## Colección v10 validada, sustituida por v11 (05-11-2026)

- Release v10-cf8f572c33a: **193 registros / 1.594 series / 951.460 valores / 1.000 grupos base**. Añade diez ubicaciones interiores Reading v3, 60 series y 6.810 valores para los seis parámetros polínicos existentes. Conserva íntegro el padre v9.
- Contrato scripts/importers/pollen_v10_sources.json; reproducción offline con `python scripts/build_forest_pollen_v10.py`. Reutiliza el parser, las 205 columnas y los originales v3 fijados por hash del lote anterior. Porcentajes derivados y denominadores por muestra explícitos; MAI/MOLINAES conservan la corrección cronológica de v3.
- 85 pruebas Python, 15 Node y snapshot con los 951.460 valores cotejados celda a celda. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados en este lote; no equivale a una auditoría exhaustiva de independencia física. Handoff docs/handoffs/cur-reading-10.md.
- Sites permanece en v9; publicación reservada al rol 04. Villarquemado requiere contrato propio para las edades IPE (361 medianas IntCal20 ausentes). Los bloqueos marinos, ELX y Monticchio permanecen.

## Ejecutable v9 (publicado, 05-11-2026)

- Site privado actualizado en https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site.
- Release v9-c55489c6f83 contiene **183 registros / 1.534 series / 944.650 valores / 1.000 grupos base**. Añade 29 ubicaciones ibéricas para seis parámetros forestales y amplía Monticchio NOAA con ocho series. Son 182 series y 19.898 valores nuevos.
- Reading usa porcentajes del conjunto armonizado de 205 taxones, con contexto de comparación explícito y denominador por muestra. Incertidumbres cronológicas ambiguas conservadas como originales. Monticchio mantiene los porcentajes publicados y edades de laminación.
- MD99-2337 continúa sin controles numéricos verificados. Neotoma Monticchio 47525 en espera por material compartido con NOAA/ACER. Límites y reproducción en docs/handoffs/cur-pollen-monticchio.md.
- 81 pruebas Python, 28 Node, tsc, snapshot y build correctos. Producción comprobada en 1.002 archivos. QA local confirma Pinus 24/29 sitios con 507 valores en 6–8 ka BP y nube de 2.655 puntos. Rótulo de evidencia calculada corregido.
- Recibos reports/pollen_v9_sites_*.json. Fuente Sites 788bc5f. Navegador de producción requiere inicio de sesión ChatGPT. Mis datos sigue desactivado por falta de OWNER_PASSWORD.

## Referencia histórica v8 (05-11-2026)

- Site privado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site.
- Release v8-c131d231e50: **154 registros / 1.352 series / 924.752 valores / 986 grupos base**. Añade 306 mediciones de tamaño medio de sortable silt en U1386, U1390 y CADKS24. 248 quedan fechadas por interpolación entre controles publicados.
- Contador del mapa por coordenadas a cuatro decimales. Los valores fuera de controles se conservan por profundidad y se excluyen de las ventanas de edad.
- Verificación y límites en docs/handoffs/cur-ss-ages.md y reports/quantitative_v8_release.json.

## Referencia histórica v7 (04-11-2026)

- Site privado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site. La dirección anterior redirige aquí.
- Release v7-cb1b445291e: **151 registros / 1.349 series / 924.446 valores / 985 grupos base**. Añade 13 registros, 38 series y 20.756 valores de PANGAEA y Zenodo sobre v6.
- Ti/Ca, Fe/Al, sortable silt y polen forestal. Los grupos conservan escalas, unidades, métodos, fracciones y sumas de polen. El filtro de fuente sigue el repositorio de la serie aunque se vincule a un sondeo existente.
- Reproducción, cobertura y límites en docs/handoffs/cur-four-coverage.md y reports/quantitative_v7_release.json. Pruebas Python/Node, snapshot, tsc, build y verificación local del selector correctos. Los 987 archivos remotos coinciden con el snapshot validado.

## Referencia histórica v6 (30-10-2026)

- Site privado: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site.
- Release v6-c8ff5c5a738: **138 registros/1.311 series/903.690 valores/962 grupos base**. Incremento sobre V29:10 registros/225 series/38.097 valores, de PANGAEA y NOAA.
- Prioridad: razones inorgánicas, indicadores de corrientes/bentónicos y vegetación continental. Datos anteriores íntegros; fuentes, unidades, denominadores y matrices conservados. No se afirma cobertura exhaustiva ni equivalencia de métodos por compartir unidades.
- Selección: alias Fe/Al/Ti/Ca, ≥2 registros por defecto y separación de contextos. Notas por serie visibles también al colgar de un registro padre. Cuarentenas e inclusión/exclusión manual: consultar límites en docs/curation/priority_v6.md.
- 71 pruebas Python/27 pruebas Node locales, tsc/build y snapshot correctos; 964 archivos estáticos remotos iguales. Navegador de producción requiere sesión; QA visual local realizada. Recibos reports/priority_v6_sites_*.json; handoff docs/handoffs/cur-coverage-30.md.
- El flujo recompone v6 tras cambios en v5; el snapshot rechaza padres obsoletos. Revisar RELEVO antes de ampliar. Los apartados siguientes son históricos.

## Referencia histórica V28.1

- Site ChatGPT privado actualizado desde main dfdb419: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site.
- Datos públicos desde /snapshot/catalog.json, /snapshot/obs/*.json e /snapshot/inventory.json; las cuatro API públicas anteriores se han retirado. D1 se conserva para el área privada y la cola DOI.
- Release v5-c25cc8a2394 (atlas-v5.json): **102 registros / 815 series / 241.826 valores / 606 grupos**. Son recuentos de la colección, no sondeos físicos independientes ni cobertura completa de literatura.
- snapshot.mjs y check-snapshot.mjs correctos antes del build. Producción: 608 archivos idénticos a la instantánea comprobada celda a celda; 24 Node, tsc, build y QA visual correctos. Recibos reports/sites_v28_*.json; handoff docs/handoffs/sites-v28.md.
- Mis datos desactivado en Sites porque falta OWNER_PASSWORD. Migración0004 incluida en el despliegue; Sites gestiona las migraciones. Las credenciales GitHub/Cloudflare no se transfieren automáticamente al Site.
- Para continuar ciencia consultar docs/RELEVO.md y docs/handoffs/claude-curado.md. Para despliegues estáticos consultar docs/handoffs/datos-estaticos.md. Los apartados siguientes conservan la referencia histórica v3 y sus límites.

## Referencia histórica v3

- URL: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (privado del propietario).
- Colección cuantitativa: **29 registros / 89 series / 81.339 valores / 62 grupos de comparación**, ocho familias. Lote nuevo PANGAEA y NOAA de 16 registros/66.588 valores. Datos marinos, lacustres y espeleotemas.
- Edades numéricas −0,0574 a 1.365 ka BP; cobertura de metadatos hasta 121.000 ka separada. 101 valores sin edad conservados.
- Selector buscable por familia/variable/método/unidad, favoritos, cobertura; filtros conjuntos de fuente, archivo, base cronológica y años de artículo. Las calibraciones, especies y denominadores se separan.
- Carga de metadatos sin observaciones; API lazy por grupo completo, límite explícito 150.000 valores/40 series. Ventana móvil, varios/todos compatibles, CSV/SVG completos. Nubes densas aligeradas solo en pantalla con aviso.
- Inventario enlazado v2 conservado: 15.572 entradas de fuente, 5.846 de sondeos/sitios/unidades, 9.726 referencias PANGAEA, 289 etiquetas de campaña. No representan ubicaciones físicas independientes depuradas.
- Cuarentena LDB04-I %terr (18 valores >100); ajustes orbitales, edades repetidas y licencias documentados. No se inventan datos ni modelos de edad.
- Prospección de artículos sigue separada de la ingestión numérica revisada.

## Archivos mínimos

Leer **docs/QUANTITATIVE_V3.md** para web/ingestión actuales; docs/DISCOVERY_V2.md para inventario; docs/WEB_V1.md conserva el contrato histórico. Fuente web app/atlas-web; semilla actual data/processed/atlas-v3.json y su copia web data/seed.json. atlas-v1.json permanece como línea base. Migraciones 0000–0003 vigentes.

Curadores scripts/importers/curate_pangaea_v3.py y curate_noaa_v3.py; ensamblador scripts/build_quantitative_v3.py. Informes reports/quantitative_v3_*.json. Originales ignorados. El API local compara las 81.339 observaciones contra la release; las pruebas de originales se omiten explícitamente sin caché. No afirmar CI remota a partir de pruebas locales.

## Siguientes entregables

- Ampliar lotes con contratos de columnas/cronología/licencia y cola revisable; no cosecha ciega.
- Resolver identidades y duplicación parcial entre datasets/cores; variantes de campañas, ODP977 y GP03.
- Modelos de edad alternativos, incertidumbre, taxonomías y denominadores revisados. Conservar dependencia orbital y correlación entre archivos.
- Importación de suplementos con doble curación; cuarentena Bourget y edades intervalares Cadagno pendientes.
- Agregación por sitio y validación espacial de IDW; no contar cores coincidentes como vecinos independientes.
- Motor de actualización con correcciones/retiradas/versiones y consultas por viewport; pasar a otro almacenamiento solo con necesidad demostrada.
- SISAL/SeaDataNet/ISMAR independientes y WDB-Paleo verificable pendientes. Licencia de código por elegir.

No cargar tesis ni JSON completos para tareas de interfaz. No se presenta una nueva reconstrucción paleoambiental validada.
