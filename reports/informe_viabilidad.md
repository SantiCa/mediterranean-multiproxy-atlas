# Mediterranean Multiproxy Atlas — informe de viabilidad

**Fecha de corte: 28 de octubre de 2026. Versión 0.2, revisión con tesis.**

## Dictamen

El atlas es técnicamente viable como catálogo geográfico con series cuantitativas trazables. Su publicabilidad exige una contribución demostrable de curación, interoperabilidad o metodología: el mapa y los filtros, por sí solos, tienen antecedentes directos. Una reconstrucción paleoambiental original del Mediterráneo es una segunda investigación, condicionada a la disponibilidad, independencia y comparabilidad de los registros. Esta evaluación no demuestra todavía que existan los datos suficientes para ella.

Se ha preparado una semilla de evidencia, código Python y especificaciones; **no se ha construido el atlas completo**. La semilla incluye cinco conjuntos de PANGAEA, cinco testigos, 1.026 filas de muestras en las tablas originales y 11 series seleccionadas, equivalentes a 2.684 valores. De estos valores, 2.646 tienen edad archivada y 38 solo profundidad. Los recuentos proceden de los archivos descargados, no del número de “data points” que muestra el repositorio. Una fila de muestra puede contener varias variables; estos valores no son réplicas independientes.

**Alcance de la revisión:** la tesis fue examinada en su versión Markdown con imágenes. Se identificaron los tres artículos publicados que reproduce y la continuidad de un capítulo sometido en 2023 con un artículo publicado en 2024. El archivo conserva figuras como imágenes y algunos detalles de tablas no se pueden auditar solo desde el texto extraído; por tanto, no se han transcrito curvas ni afirmado disponibilidad/licencia de los datos que no se verificaron.

## 1. Estado de las seis tareas solicitadas

| Tarea | Resultado y límite |
|---|---|
| Examinar tesis y tres artículos | Completada a nivel de estructura, texto de los capítulos/artículos, abstracts, métodos y resultados principales; ver fichas en `docs/revision_tesis.md`. Pendiente auditoría completa de suplementos, figuras y datos |
| Investigar antecedentes | Revisión dirigida de publicaciones y páginas oficiales; no es una revisión sistemática exhaustiva |
| Arquitectura y carpetas | Diseño propuesto en este informe y en `docs/arquitectura_datos.md` |
| Desafíos científicos y técnicos | Evaluados; cuatro alertas concretas detectadas en la semilla |
| Diseñar MVP con registros reales | Especificado con cinco fuentes descargadas y verificadas; sin aplicación cartográfica |
| Informe de viabilidad y originalidad | Entregado como evaluación provisional, con decisiones condicionadas |

### Resultado de la revisión de tesis

El ZIP recibido contiene la tesis de Santiago Casanova-Arenillas (2023), UGR, *Análisis integrado del impacto de la variabilidad ambiental en las condiciones del fondo marino en el Mediterráneo durante el Último Ciclo Glacial* ([handle 10481/88714](https://hdl.handle.net/10481/88714)). Los capítulos V–VII reproducen tres artículos publicados (2020, 2021 y 2022); el capítulo VIII consta como manuscrito enviado en 2023 y el IX como trabajo en curso. El capítulo VIII tiene continuidad en un artículo de 2024 sobre el testigo GP03, DOI [10.1016/j.palaeo.2024.112427](https://doi.org/10.1016/j.palaeo.2024.112427), con registro institucional UGR [10481/109754](https://hdl.handle.net/10481/109754). El detalle está en [`docs/revision_tesis.md`](../docs/revision_tesis.md).

Esta lectura identifica temas y testigos, pero no reemplaza la comparación de suplementos, conjuntos de datos y versiones editoriales. Las figuras del Markdown conservan gráficos como imágenes; sus curvas no se han digitalizado.

#### Consecuencia científica inmediata

La tesis hace de la icnología y la oxigenación del fondo marino un foco claro, con ODP Sites 976/977 y ORLs en el Alborán occidental; incluye además un capítulo multiproxy vinculado a GP03 y trabajo del Mediterráneo oriental. El piloto actual con ODP 977A ya se conecta con el artículo metodológico y no debe contarse como una nueva réplica independiente. El siguiente registro para ampliar el prototipo debería ser GP03, si se localizan series reutilizables y licencia verificable. Las publicaciones 2020–2022 cubren en buena medida las interpretaciones ya planteadas por la tesis: un artículo original debe aportar datos o análisis adicionales y responder una pregunta no resuelta, no volver a empaquetar sus curvas.

La tesis ya interpreta que ORLs y sapropeles suelen ser asincrónicos, que sus controles dominantes difieren entre Este y Oeste y que las ORLs varían internamente, con reoxigenaciones breves en ORL1. El proyecto no puede reclamar esas observaciones como novedades. La posibilidad original que queda abierta es someter la asincronía y la heterogeneidad espacial a una comparación cuantitativa con edades/proxies independientes, incertidumbre temporal propagada y cobertura adicional de sitios; la factibilidad dependerá de esa auditoría. La tesis atribuye estas conclusiones a sus registros y métodos, no se presentan aquí como consenso general.

## 2. Antecedentes y espacio de contribución

### PaleoMED20

Viganò y Agnini (2025) reúnen metadatos de 1.524 testigos mediterráneos para los últimos 20.000 años. El artículo distingue 465 testigos con información paleoclimática y realiza una comprobación sobre 36. Es un antecedente directo para localización, disponibilidad de proxies y cobertura, no evidencia de que cada entrada contenga series numéricas listas para combinar. [Artículo, DOI 10.1038/s41597-025-05451-5](https://www.nature.com/articles/s41597-025-05451-5).

**Consecuencia de diseño:** usarlo como índice de descubrimiento y comparación de cobertura. Para cada serie se debe llegar al depósito o suplemento original. El archivo de Figshare no se descargó ni auditó en esta fase; su licencia específica y estructura efectiva quedan pendientes. La licencia del artículo no debe trasladarse a sus datos ni a figuras de terceros. El candidato de novedad sería una capa cuantitativa auditable y ampliable, con prueba explícita de qué añade a este inventario.

### WDB-Paleo

Alberico et al. (2017) describen un modelo de 20 entidades que combina metadatos, presencia de proxies en unas 200 publicaciones y datos cuantitativos de unos 14 testigos. El trabajo presenta aplicaciones al Younger Dryas. Esto impide sostener que una base mediterránea relacional y multiproxy sea, por sí sola, una innovación. [Artículo y resumen institucional, DOI 10.1515/geo-2017-0019](https://www.pi.ingv.it/252362-2/).

**Consecuencia:** aprender de sus entidades y de la distinción entre existencia y cuantificación. Se verificó el trabajo publicado; no se verificó un servicio de consulta activo ni su código actual. No se propone depender de una instancia cuyo mantenimiento no se ha comprobado.

### PANGAEA

Es la fuente numérica de esta semilla: proporciona DOI de conjunto, eventos, parámetros, métodos y licencias individualizadas en los registros inspeccionados. El trabajo que describe el repositorio ofrece el contexto institucional y técnico. [Felden et al., 2023, DOI 10.1038/s41597-023-02269-x](https://doi.org/10.1038/s41597-023-02269-x).

**Consecuencia:** conservar los ficheros originales, citar conjunto y artículo, registrar la fecha de acceso y comprobar relaciones padre/hijo y versiones. Un DOI de colección no equivale a una tabla: la colección ODP 977 contiene conjuntos hijos, y el año del hijo descargado difiere del artículo.

### NOAA / WDS for Paleoclimatology

El servicio oficial permite descubrir estudios por localización, investigador y parámetros; ofrece API de metadatos y enlaces a datos. La API documenta paginación y diferencias entre contenido propio y terceros. [Paleoceanography, NCEI](https://www.ncei.noaa.gov/products/paleoclimatology/paleoceanography), [documentación API](https://www.ncei.noaa.gov/access/paleo-search/api).

**Consecuencia:** incorporar un adaptador separado y respetar la paginación. No asumir que una entrada de PANGAEA encontrada mediante NOAA es otro registro independiente, ni que la API redistribuya todos los datos externos. En esta fase se revisó documentación; no se incorporaron ni verificaron tablas numéricas de NOAA.

### World Paleoceanographic Atlas / PaleoDataView

La interfaz de MARUM ofrece datos por profundidad y series por edad, incluidas series equidistantes. Su descripción de la versión 2024 especifica paso de 0,5 kyr y rangos de incertidumbre a partir de 1.000 realizaciones. La página también muestra una versión 2025; no se auditó su contenido ni se atribuyen automáticamente a ella los métodos de 2024. [Interfaz y descripción](https://paleodataview.marum.de/).

La compilación isotópica publicada por Mulitza et al. (2022) es otro antecedente esencial. [DOI 10.5194/essd-14-2553-2022](https://essd.copernicus.org/articles/14/2553/2022/).

**Consecuencia:** una interfaz con series e incertidumbre tampoco es nueva por sí misma. El atlas mediterráneo deberá diferenciar los valores archivados de reconstrucciones armonizadas y demostrar el beneficio de integrar familias adicionales, especialmente sedimentología, micropaleontología e icnología.

### Interoperabilidad

LiPD proporciona un marco publicado para empaquetar datos paleoclimáticos y metadatos estructurados. Se propone como formato de intercambio cuando la correspondencia de campos se haya probado; no como sustituto automático del modelo relacional. [McKay y Emile-Geay, 2016, DOI 10.5194/cp-12-1093-2016](https://cp.copernicus.org/articles/12/1093/2016/).

### Selección bibliográfica

La primera prioridad será la publicación revisada por pares y el acceso al conjunto original, al método y a la cronología. Se registrarán `quartile_system`, `quartile_year`, `subject_category`, `quartile_value` y evidencia de consulta; hasta entonces el cuartil será desconocido. **No se han verificado clasificaciones JCR/SJR y no se asigna aquí Q1/Q2 a ninguna revista.** La prioridad solicitada no debe excluir trabajos fundacionales o conjuntos técnicamente esenciales por su antigüedad, ni sustituir la evaluación de cada registro.

## 3. Semilla real y verificable

La selección es intencional para probar heterogeneidad, no una muestra representativa del Mediterráneo. Predomina el sector occidental; LC21 aporta un caso oriental sin cronología tabulada. No permite inferir patrones de toda la cuenca.

| Testigo y DOI del conjunto | Variables seleccionadas | Filas | Edades archivadas, ka BP | Año artículo / cita del conjunto |
|---|---|---:|---|---|
| MD95-2043 — [438816](https://doi.pangaea.de/10.1594/PANGAEA.438816) | SST anual de alquenonas | 97 | 1,01–11,50 | 1999 / 1999 |
| HER-GC-ALB2 — [901666](https://doi.pangaea.de/10.1594/PANGAEA.901666) | Mg/Ca, Mg/Ca corregido, SST corregida | 292 | −0,0124–15,0388 | 2019 / 2019 |
| MD99-2343 — [759535](https://doi.pangaea.de/10.1594/PANGAEA.759535) | D50, limo/arcilla, UP10; fracción no carbonatada | 437 | 0,062–52,480 | 2008 / 2008 |
| MD81-LC21 — [898587](https://doi.pangaea.de/10.1594/PANGAEA.898587) | BHT/TOC, ladderanos/OC | 19 | Sin columna de edad; profundidad 1,50–9,70 mbsf | 2019 / 2019 |
| ODP 161-977A — [921230](https://doi.pangaea.de/10.1594/PANGAEA.921230) | Abundancia relativa de G. muellerae y abundancia absoluta de cocolitos | 181 | 375,97–429,69 | 2020 / 2024 |

Las coordenadas, profundidad de agua, autores, métodos, licencias y huellas se conservan en `data/processed/catalog.csv` y en las cabeceras de `data/raw/pangaea/*.tsv`. Los ficheros de 438816 y 759535 indican CC-BY-3.0; los otros tres, CC-BY-4.0. Se mantiene la atribución en las exportaciones.

El artículo de Català et al. identifica la comparación multiproxy como un problema ya estudiado en Alborán; una nueva aplicación deberá ir más allá de reproducirla. [DOI 10.5194/cp-15-927-2019](https://cp.copernicus.org/articles/15/927/2019/). El registro de nanofósiles corresponde al artículo de González-Lanchas et al. de 2020, no a un supuesto artículo de 2024. [DOI 10.1016/j.quascirev.2020.106520](https://doi.org/10.1016/j.quascirev.2020.106520).

### Hallazgos de integridad

- **Edad negativa:** HER-GC-ALB2 contiene −0,0124 ka BP. Se conserva; una edad posterior a 1950 no debe transformarse automáticamente en cero. Su interpretación cronológica exacta requiere revisar el modelo.
- **Cronología ausente:** LC21 conserva edades nulas. “S1”, “S3” o “S5” son etiquetas estratigráficas, no edades individuales de muestra. Los filtros cronológicos lo excluyen y deben informar de esta exclusión; la consulta por profundidad sigue disponible.
- **Geometría de sección:** algunos límites inferiores de sección de LC21 aparecen como cero. Se preservan y se señala que no permiten calcular espesores sin revisión.
- **Unidad de profundidad conflictiva:** en ODP 977, la cabecera dice `Depth corr [m]` y el comentario menciona `[cmbsf]`. No se aplica una conversión de factor 100. Este campo queda inhabilitado para unión profundidad–edad hasta resolver la discrepancia con el trabajo original. La vista por edad usa la columna de edad ya publicada.

Las edades se muestran como **“edad archivada (ka BP)”**. No se certifican aquí como una cronología calendarizada armonizada. Se conserva el error estándar de SST que incluye HER-GC-ALB2; no se usa como error de edad ni se inventan intervalos para las otras series.

### Figuras de evidencia

`figures/seed_timeseries.svg` muestra cuatro series en paneles de escalas independientes; los puntos no se interpolan. Las barras de HER-GC-ALB2 representan exclusivamente el error estándar de SST archivado. El panel MIS 11 tiene un dominio distinto: no es una comparación sincrónica con el Holoceno. `figures/lc21_depth_only.svg` muestra BHT/TOC contra profundidad.

Ambos SVG conservan texto editable (`svg.fonttype=none`), unidades y marcas vectoriales. Se acompañan de PNG para inspección. La edición en Adobe Illustrator debe preservar ejes, valores, atribución y archivo maestro; no se ha probado la apertura en Illustrator.

## 4. Arquitectura científica y de datos

### Separación de productos

1. **Archivo original:** bytes de la fuente, metadatos, licencia, acceso y hash. “Archivado” no significa necesariamente medición instrumental sin tratamiento.
2. **Metadatos normalizados:** ubicación, testigo, publicación, muestras, profundidad, método, taxón, unidad y cobertura.
3. **Observaciones:** medidas, recuentos, porcentajes o cocientes con su soporte de muestra y estado de control.
4. **Reconstrucciones y transformaciones:** SST, flujos, cocientes recalculados o edades modelizadas; cada resultado enlaza entradas, ecuación, parámetros, código y versión.
5. **Interpretaciones:** inferencias ambientales atribuidas al autor, evidencia de apoyo/contradicción y alcance. “Ventilación reducida” no se almacena como si fuera una concentración medida de oxígeno.

El diseño detallado de entidades, campos y relaciones está en `docs/arquitectura_datos.md`. La unidad fundamental será **una observación de una variable sobre una muestra o intervalo, bajo un método y una versión de procesamiento**. Una edad es una asignación de un modelo a una profundidad, no una propiedad fija e irreversible de la observación.

### Decisión tecnológica

Para el MVP: Python, ficheros originales inmutables, tablas normalizadas CSV/Parquet y SQLite para el catálogo. La extracción experimental entregada usa CSV/JSON y biblioteca estándar; no se ha desplegado SQLite ni Parquet. Una aplicación local pequeña podría usar Streamlit, con selección cartográfica y gráficos interactivos, después de validar el contrato científico.

Para colaboración y publicación sostenida: PostgreSQL/PostGIS, almacenamiento versionado de ficheros, API de lectura y una interfaz web con mapa y gráficos. Esta es una opción de evolución, no un requisito inicial. Evitar una migración temprana reduce mantenimiento mientras cambien taxonomía y esquema. Los formatos de exportación deben ser independientes de la interfaz.

LiPD/GeoJSON serían salidas de intercambio; CSV/Parquet conservan los datos tabulares, y SVG las figuras. Una licencia de software futura —por ejemplo una licencia permisiva elegida por el titular— no cambia las licencias de los conjuntos incorporados.

## 5. Desafíos científicos

| Riesgo | Efecto | Tratamiento propuesto |
|---|---|---|
| Modelos de edad distintos y reservorio marino variable | Sincronías y desfases aparentes | Conservar modelo publicado y crear escenarios separados; registrar curvas, ΔR y dependencias |
| Edad ajustada al proxy que se quiere comparar | Circularidad en correlación o fase | Grafo de dependencias y análisis restringido a cronologías independientes |
| Bioturbación, condensación, hiatus y retrabajamiento | Resolución efectiva inferior al muestreo | Registrar soporte, mezcla y discontinuidades; no interpolar a través de hiatus |
| Proxies sensibles a varios procesos | Atribución ambiental no unívoca | Formular mecanismos alternativos y buscar convergencia entre familias independientes |
| TOC y redox afectados por diagénesis y dilución | Confusión entre producción, preservación y aporte | Metadatos sedimentarios y geoquímicos conjuntos; no convertir un proxy en O₂ sin calibración |
| XRF counts frente a concentraciones | Mezcla de escalas y efectos de matriz | Conservar instrumento, normalización y calibración; no fusionar counts/cps/ppm |
| Fracciones granulométricas y pretratamientos diferentes | Cocientes incomparables | Registrar límites de clases, fracción y eliminación de carbonato/OM |
| Taxonomía, fracción de tamiz y denominador | Sesgo de porcentajes micropaleontológicos | Nombre original y aceptado, protocolo y recuento total; tratar composición explícitamente |
| Escalas icnológicas y preservación | Índices ordinales tratados como medidas continuas | Registrar escala, observador, tamaño del área, imágenes y acuerdo entre observadores |
| Desigual cobertura geográfica y batimétrica | Generalización excesiva | Mostrar cobertura de cada análisis; ponderación/sensibilidad por región y testigo |
| Series reutilizadas en varios artículos/repositorios | Pseudorreplicación | Relaciones de identidad, versión y derivación; unidad independiente = testigo/archivo, no DOI |

Una revisión de la cronología marina debe partir del material fechado y la definición de la corrección de reservorio. Marine20 es una referencia metodológica para muestras marinas; no debe aplicarse directamente una curva atmosférica a un fechado marino sin un procedimiento explícito de reservorio. **En esta fase no se ha recalibrado ninguna fecha.** [Heaton et al., 2020, DOI 10.1017/RDC.2020.68](https://doi.org/10.1017/RDC.2020.68).

La icnología puede aportar restricciones sobre colonización bentónica, mezcla y oxigenación, pero la presencia de una traza no equivale automáticamente a una concentración de oxígeno ni a ausencia de anoxia en toda la columna de agua. La propuesta deberá distinguir ausencia observada, ausencia de observación y falta de preservación. Un estudio multiproxy de ODP 977 declara imágenes y datos icnológicos disponibles bajo solicitud; esta barrera debe resolverse antes de incorporarlos como datos abiertos. [Marine Geology, 2022, artículo 106774, depósito institucional](https://gredos.usal.es/bitstream/handle/10366/159437/DGL_Mediterranean.pdf?sequence=1). No se ha solicitado material a autores ni se han redistribuido imágenes.

## 6. Desafíos tecnológicos y de mantenimiento

- Los conectores deberán soportar cambios de esquema, colecciones y versiones sin alterar registros ya publicados. Una descarga que cambia se conserva como nueva versión pendiente de curación.
- Los filtros espaciales deben usar coordenadas verificadas, CRS explícito y convenciones de longitud; una caja envolvente mediterránea también incluye tierra y áreas ajenas. Para una selección regional robusta se necesita un polígono marino documentado.
- El rendimiento se resolverá primero mediante consultas e índices y, después, mediante agregaciones para visualización. Una línea simplificada en pantalla nunca sustituirá los datos completos de descarga.
- Cada valor tendrá una ruta hasta fuente, fila/columna, muestra y transformación. La interfaz mostrará las limitaciones al lado de la variable, incluidas edades y licencias desconocidas.
- Se necesitan pruebas de contrato para los adaptadores, comprobaciones de unidades y relaciones y un registro de cambios. No se utilizará OCR o extracción automática de tablas sin revisión humana.
- El mantenimiento requiere responsable científico, responsable técnico, revisión de incorporaciones y un mecanismo de correcciones. El atlas no debe prometer actualizaciones continuas sin recursos para curarlas.

## 7. MVP propuesto

### Alcance y secuencia

**MVP-A, demostración de integridad:** los cinco conjuntos actuales; vista de cada serie en su soporte original, mapa de sitios y búsqueda por proxy/año. La semilla ya valida el tratamiento de edades negativas, cronología ausente, versiones y unidades problemáticas. El registro MIS 11 demuestra flexibilidad temporal; no amplía por sí solo el alcance científico del piloto holoceno.

**MVP-B, piloto científico:** comenzar con Alborán occidental, 0–37 ka, enlazando GP03 (multiproxy, continuación publicada en 2024), ODP 976/977 (icnología/ORLs) y registros de comparación solo cuando compartan ventana, marco cronológico y variable interpretable. En una segunda etapa, contrastar cobertura con PaleoMED20 y añadir testigos orientales. La presencia de múltiples proxies en un sitio no garantiza independencia: medir y declarar relaciones de derivación y calibración.

### Recorrido funcional

1. Mapa con un marcador por testigo; ficha con alias, coordenadas, profundidad de agua y fuentes.
2. Filtros separados: **edad de muestra, ka BP**; **año del artículo, año CE**; proxy, región y tipo de evidencia. El año de depósito será un filtro distinto, opcional.
3. La edad filtra valores reales; para descubrir registros también puede consultarse el solapamiento de coberturas. No basta con que un testigo tenga alguna edad dentro de un intervalo si sus valores seleccionados están fuera.
4. Mostrar recuento de muestras/valores seleccionados, excluidos por edad ausente y excluidos por calidad; indicar si la búsqueda usa cronología archivada o armonizada.
5. Gráficos con ejes numéricos, puntos originales, unidades, errores disponibles y opción edad/profundidad cuando sea válida. Mantener escalas independientes para variables distintas. No unir series con un eje común si el método o soporte lo hace engañoso.
6. Descargar selección, metadatos, DOI, licencias y manifiesto; generar SVG mediante el mismo conjunto seleccionado en Python. La figura debe incluir configuración de filtros y estado cronológico.

### Exclusiones del MVP

No habrá reconstrucción espacial continua, índice ambiental global, cronología recalculada masivamente, conversión automática a oxígeno, interpolación por defecto ni “curva mediterránea media”. Tampoco se interpretará el número de publicaciones como densidad temporal de datos.

### Criterios de aceptación

| Prueba | Resultado requerido |
|---|---|
| Trazabilidad | Cada valor exportado resuelve archivo original, hash, fila y columna; artículo y conjunto citados |
| Filtrado | Proxy, edad y año funcionan conjuntamente; ODP 977 figura por artículo 2020 aunque el conjunto se cite como 2024 |
| Ausencia | LC21 no aparece en una selección numérica de edades; sí en catálogo y vista en profundidad |
| Unidades | La profundidad conflictiva de ODP 977 no entra en una unión ni se convierte sin revisión |
| Incertidumbre | Ninguna banda inventada; distinguir error analítico/calibración de error cronológico |
| Exportación | CSV coincide con los valores de la vista; SVG conserva texto y unidades |
| Curación científica | Un segundo revisor verifica un subconjunto de extracciones y todas las conversiones no triviales |
| Publicación | Cada recurso redistribuido tiene atribución y licencia/permiso documentado |

El código entregado cubre extracción, trazabilidad, filtros y figuras estáticas. En esta versión la tesis y los tres artículos reproducidos están identificados; la auditoría de suplementos/datos, la revisión por segundo investigador, la interfaz cartográfica y la apertura real de SVG en Illustrator permanecen pendientes.

## 8. Qué sería contribución científica original

| Producto | Funcionalidad técnica | Aportación que habría que demostrar |
|---|---|---|
| Atlas | Mapa, filtros, descarga y gráficos | Por sí solos no prueban originalidad |
| Compilación curada | Importar, normalizar y enlazar fuentes | Cobertura cuantitativa nueva, esquema reproducible, resolución documentada de inconsistencias y comparación con antecedentes |
| Método | Implementar cronologías, controles o calibraciones | Validación independiente, mejora demostrada y límites frente a métodos existentes |
| Reconstrucción | Analizar series y generar figuras | Hipótesis nueva, evidencia independiente, incertidumbre propagada y conclusión que exceda las publicaciones fuente |

### Preguntas candidatas, todavía no resultados

**Acoplamiento superficie–fondo:** ¿los cambios en productividad, aporte terrígeno y colonización bentónica son compatibles con cambios de ventilación en un intervalo definido? Exige registros co-localizados o correlacionados con justificación, no proxies dispersos llamados todos “oxigenación”. Evaluar modelos alternativos de preservación y dilución. La dirección de una asociación no demostrará causalidad.

**Magnitud de la asincronía entre Este y Oeste:** ¿se mantiene al comparar observaciones compatibles bajo modelos cronológicos independientes y ensambles de edad? La tesis ya propone asincronía general y controles distintos; la contribución nueva tendría que cuantificar el desfase y su incertidumbre con más sitios, y evaluar sensibilidad a la selección de proxies. ORLs y sapropeles se mantienen como procesos/contextos distintos, no como capas equivalentes. [Rogerson et al., 2008, DOI 10.1029/2007GC001936](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2007GC001936).

**Valor añadido de la icnología:** ¿reduce ambigüedad o cambia una inferencia obtenida con geoquímica/microfósiles? Requiere evaluar interpretaciones con y sin datos icnológicos y comprobar reproducibilidad de la clasificación. La mera incorporación de imágenes no basta.

Para analizar desfases se usarían realizaciones de edad, resolución efectiva y dependencia entre registros; un desfase inferior a la incertidumbre combinada no se interpretaría como secuencia de procesos. No se alinearán primero los proxies al evento para después “descubrir” su sincronía. Si las dataciones o ensambles no están disponibles, el alcance se reducirá a comparación exploratoria en profundidad o edad archivada.

### Puertas de decisión editorial

1. **Auditoría de datos de tesis y seguimiento:** identificar qué series de ODP 976/977 y GP03 están disponibles y bajo qué términos; separar la publicación de tesis, el artículo GP03 de 2024 y datos originales/suplementos.
2. **Auditoría de cobertura:** construir una matriz región × profundidad × proxy × tiempo con disponibilidad numérica, calidad cronológica e independencia. Un recuento de metadatos no la sustituye.
3. **Originalidad:** comparación explícita de contenido y métodos con PaleoMED20, WDB-Paleo y WPA; describir solapamientos sin llamarlos datos nuevos.
4. **Ruta de datos/herramienta:** viable si hay curación reutilizable, documentación, licencia, validación y una versión archivada. No exige vender el atlas como reconstrucción nueva.
5. **Ruta de artículo paleoambiental:** avanzar solo si la hipótesis tiene cobertura y cronología suficiente y sobrevive a pruebas de sensibilidad por testigo, subcuenca, método y modelo de edad. No hay una cifra universal de testigos que garantice potencia; debe evaluarse tras definir el efecto y la resolución.

## 9. Plan de trabajo y recursos

Las duraciones siguientes son estimaciones de planificación para una persona investigadora con apoyo técnico puntual, no costes medidos ni compromisos de entrega. Dependen del formato/acceso a suplementos y datos.

| Fase | Entregable y decisión | Orden de esfuerzo estimado |
|---|---|---|
| A. Tesis y originales | Fichas preliminares completadas; auditoría de datos, versiones y permisos por cerrar | 3–5 jornadas adicionales con suplementos y conjuntos accesibles |
| B. Curación piloto | Diccionario, controles, licencias y cronologías revisadas | 1–3 semanas; más si hay solicitudes a autores |
| C. MVP local | Mapa, filtros, series y exportación coherentes | 1–2 semanas tras estabilizar el esquema |
| D. Validación científica | Segunda revisión, casos de uso y comparación con antecedentes | 1–2 semanas según cobertura |
| E. Evaluación de reconstrucción | Análisis de potencia/resolución y diseño de hipótesis | Decisión posterior a B–D; sin duración comprometida |

Se recomienda empezar con la auditoría A y curación B, priorizando GP03 y los enlaces de ODP 976/977. La restricción ahora es la localización y permiso de los datos fuente y sus cronologías; el mayor riesgo es científico y de curación, no cartográfico. Una versión pública debe contar con repositorio versionado, entorno reproducible, archivo con DOI y responsable de mantenimiento.

## 10. Reproducibilidad, verificaciones y pendientes

Ejecutar desde la raíz del proyecto:

```powershell
python scripts/fetch_seed.py
python scripts/prepare_seed.py
python -m unittest discover -s tests -v
python scripts/make_figures.py
```

La primera instrucción descarga solo los archivos ausentes y verifica los existentes. `--refresh` compara y rechaza cambios de bytes; no sobrescribe un original distinto. La extracción selecciona columnas declaradas en `config/seed.json`, conserva texto original y transforma únicamente la representación numérica de las celdas. Se registra como `T001_extract_selected_columns_v1`.

**No ejecutado:** recalibración radiocarbónica, armonización taxonómica, recálculo de SST, interpolación, suavizado, imputación, modelos jerárquicos o reconstrucciones regionales. No se han evaluado los protocolos completos de laboratorio de todos los artículos fuente. Las figuras demuestran lectura de datos, no validación de sus interpretaciones originales.

Los resultados exactos están en `reports/seed_audit.json`; el entorno de figuras, en `reports/environment.json`; las descargas, en `data/provenance/downloads.json`. La revisión de tesis está resumida en `docs/revision_tesis.md`; el ZIP recibido y sus imágenes se conservan en `thesis_source/`. La viabilidad técnica del atlas queda respaldada por una semilla reproducible; el camino de contribución más sólido es curación cuantitativa auditable e integración explícita de icnología con otros proxies. La opción de artículo original sigue abierta, pero no demostrada: primero se requiere inventariar los datos de GP03 y los testigos ODP, luego definir una pregunta que exceda los artículos publicados y someterla a pruebas de resolución, independencia cronológica y sensibilidad.
