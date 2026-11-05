# Estado breve del proyecto

Actualizado: 05-11-2026. Repositorio privado `SantiCa/mediterranean-multiproxy-atlas`. Consultar git log para el commit efectivo.

## Colección v12 validada, pendiente de publicar (05-11-2026)

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
