# CUR-POLLEN-MONTICCHIO

05-11-2026 · Codex · rama relevo

## Entregable

Lote reproducible v9. Añade 29 entidades continentales de nuevas ubicaciones ibéricas y ocho series al registro NOAA de Monticchio ya existente. En total, 182 series y 19.898 valores nuevos. El catálogo resultante contiene 183 registros, 1.534 series y 944.650 valores. Padre v8 preservado por el ensamblador, con auditoría de vectores completos y solapamientos parciales.

`python scripts/build_forest_pollen_v9.py --fetch` restaura los originales ausentes, comprueba SHA-256 y reconstruye la semilla. Contrato en `scripts/importers/pollen_v9_sources.json`. Informe en `reports/quantitative_v9_release.json`. Los archivos originales descargados quedan en `data/interim/pollen_v9`, fuera de Git.

## Monticchio

Se incorporan 496 muestras de `pollen.txt` del estudio NOAA 5463. Variables originales en porcentaje de woody taxa, Pinus, Juniperus type, Betula, Quercus, Alnus, Abies y Fagus. Se preservan ceros, tokens originales, fila y línea. Se comprueba el cierre woody + herbaceous = 100 con tolerancia de redondeo de 0,011 puntos porcentuales. Las edades son lamination years BP divididas entre 1.000. La escala publicada conserva su identidad, sin recalibrar.

La tabla identifica D (1990) + J (1994), un subconjunto del compuesto B-D-J-L ya incorporado como `noaa-5463-8909`. Enlace declarado al estudio existente, sin añadir un punto espacial. La posición NOAA tiene menos precisión que la posición de la ficha PANGAEA del lago. Se conserva la posición del padre con advertencia sobre su alcance. La licencia se mantiene como base de reutilización NOAA WDS, sin asignar una licencia Creative Commons al artículo.

Se descargó también Neotoma 47525, DOI 10.21233/KVNC-0856, con 924 muestras entre 59 y 132.809 años calendario BP, cronología 33110 basada en varvas y tasas de acumulación. Su compuesto P90/B/D/E/MF/J/K/L/M/O incluye material compartido con las versiones NOAA y ACER. Su localización es un polígono con GPS nulo. Se retiene para una futura auditoría de sustitución/versionado. Añadirlo como otro sondeo independiente duplicaría material.

Fuentes principales

- [NOAA 5463](https://www.ncei.noaa.gov/access/paleo-search/study/5463)
- [Archivo de polen original](https://www.ncei.noaa.gov/pub/data/paleo/paleolimnology/europe/italy/pollen.txt)
- [Readme original](https://www.ncei.noaa.gov/pub/data/paleo/paleolimnology/europe/italy/readme_allen1999.txt)
- [Allen et al. 1999](https://doi.org/10.1038/23432)
- [Neotoma 47525](https://data.neotomadb.org/47525)

## Iberia

Fuente versionada de Harrison, Shen y Sweeney (2022), DOI 10.17864/1947.000369, CC BY 4.0. Es una compilación que conserva referencias originales por entidad, con revisión de edades IntCal20/Bacon. La versión 3 corrige problemas presentes en versiones anteriores. Este lote selecciona 29 entidades con identidad, posición, profundidades únicas y cronología mediana monotónica verificadas. No incorpora las entidades con solapamiento espacial/correspondencia de archivo pendiente, ni ELX, con 23 filas de suma nula.

Se amplían seis parámetros de polen existentes, Abies, Alnus, Betula, Fagus, Pinus y Quercus deciduo. Para Pinus se suman las columnas Pinus, diploxylon y haploxylon, conservando sus nombres en la procedencia. Para cada parámetro se calcula 100 × abundancia / suma de las 205 columnas retenidas por los compiladores. La documentación advierte que unas entidades contienen recuentos y otras porcentajes, sin un identificador por entidad. La fórmula tiene la misma interpretación relativa cuando los valores de una muestra comparten escala. `original_unit` refleja esa limitación y nunca declara recuentos para todas las entidades.

El denominador conserva todos los taxones armonizados, incluidas las esporas retenidas. Se almacena por muestra en `record.pollen_sample_audit`, junto con fila física, profundidad y campos cronológicos originales. Este porcentaje se compara entre estas entidades con un contexto propio. No se interpreta como cubierta de bosque ni se equipara a otras sumas de polen terrestre. La taxonomía armonizada puede diferir de la del artículo original. Se conservan referencias de los autores y fuentes de EPD/PANGAEA/provisión directa.

Las edades usan INTCAL2020_median / 1.000. Se mantienen las edades negativas BP. Los cuatro campos de incertidumbre originales permanecen en la auditoría por muestra. El readme los llama límites pero algunas medianas quedan fuera de los campos 5/95. Por ello se conserva la incertidumbre sin convertirla en bandas numéricas absolutas. La fecha de publicación de la compilación es 2022. Se deja el año del artículo por serie nulo cuando no hay una única atribución verificada, manteniendo la referencia original íntegra y sus DOI expresos.

[Datos y documentación de Reading v3](https://researchdata.reading.ac.uk/369/)

## MD99-2337

Permanece en espera. La búsqueda adicional no verificó una tabla numérica de edad y profundidad del propio sondeo. Se revisaron las referencias a Ducassou et al. (2018), DOI 10.1016/j.margeo.2017.09.014, y su enlace oficial Elsevier a texto completo. El endpoint oficial respondió HTTP 429. La ficha de ScienceDirect no permitió acceder al texto completo. PANGAEA.971575, .971574 y .256528 siguen siendo tablas por profundidad. Las franjas estratigráficas de las tesis ya revisadas no proporcionan controles numéricos suficientes para asignar edades. No se trasladan cronologías de MD99-2339 ni se convierten las franjas en puntos inventados.

Siguiente acción concreta, localizar una versión pública del texto/suplemento o una tabla de controles del mismo marco de profundidad. Mientras se resuelve, ampliar los seis parámetros ibéricos con otras entidades, revisando primero las entidades de costa con fechas marinas y los enlaces con registros existentes. Para Neotoma Monticchio hace falta identificar las muestras compartidas y escoger una versión activa de cada observación.

## Verificación y publicación

81 pruebas Python y 28 Node superadas durante el cierre del lote. Pruebas específicas de porcentajes, muestras vacías, ceros, edades negativas, cronología de laminación y conservación de incertidumbres ambiguas. La publicación y el recibo de producción se completan al cerrar el despliegue en esta misma tarea.
