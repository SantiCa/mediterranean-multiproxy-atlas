# V1: registros continentales NOAA WDS

Consulta y extracción: 28-10-2026. Dueño de esta tarea: investigación de fuentes continentales. La entrega está en `data/interim/v1_continental/` (área local ignorada); la extracción se ha integrado en la release atlas-v1-2026-10-28-r2.

## Entrega

`continental_seed.json` contiene `records`, `observations`, `transformations`, `manifest` y `limitations`. Cada observación conserva el valor numérico y su celda textual, edad original, unidad de edad, fila de tabla, línea de archivo, columna y SHA-256. El script versionado `scripts/importers/curate_continental_v1.py` reproduce la selección desde los tres archivos NOAA descargados. No contiene series fabricadas ni curvas digitalizadas.

| Registro | Archivo | Muestras originales | δ18O | δ13C | Edad calendario, ka BP |
|---|---|---:|---:|---:|---:|
| Soreq Cave composite | `soreq_2003-noaa.txt` | 1404 | 1390 | 1389 | 0–184 |
| Peqiin Cave composite | `peqiin_2003-noaa.txt` | 586 | 568 | 571 | 14–248.2 |
| Sofular Cave, So-1 | `sofular2009-noaa.txt` | 3976 | 3976 | 3976 | −0.056–50.2745 |

Total: 5966 filas originales y 11870 observaciones finitas seleccionadas. Dos observaciones de Peqiin conservan edad nula (línea 516 del archivo). Las celdas de proxy vacías o `na` no se convierten a cero. Las edades negativas de Sofular se conservan. Varias variables por muestra no son réplicas independientes.

## Fuentes y vínculo a artículos

### Soreq y Peqiin

[NOAA Study 5423](https://www.ncei.noaa.gov/access/paleo-search/study/5423), DOI de dataset [10.25921/8a4v-ac50](https://doi.org/10.25921/8a4v-ac50). El API enlaza dos sitios y dos tablas: Peqiin, site 6549/table 7157, y Soreq, site 6550/table 7158.

Artículo principal vinculado por el archivo y metadata NOAA: Bar-Matthews, M., Ayalon, A., Gilmour, M., Matthews, A. & Hawkesworth, C.J. (2003), *Sea–land oxygen isotopic relationships from planktonic foraminifera and speleothems in the Eastern Mediterranean region and their implication for paleorainfall during interglacial intervals*, Geochimica et Cosmochimica Acta 67(17), 3181–3199, DOI [10.1016/S0016-7037(02)01031-1](https://doi.org/10.1016/S0016-7037(02)01031-1). El dataset también cita artículos de Soreq de 1997 y 1999, retenidos en `related_publications`; el año de catálogo/depósito no se usa como edad ni convierte datos reutilizados en resultados nuevos.

Descargas oficiales:

- [Soreq](https://www.ncei.noaa.gov/pub/data/paleo/speleothem/israel/soreq_2003-noaa.txt)
- [Peqiin](https://www.ncei.noaa.gov/pub/data/paleo/speleothem/israel/peqiin_2003-noaa.txt)
- [Metadata JSON de estudio](https://www.ncei.noaa.gov/access/paleo-search/study/search.json?NOAAStudyId=5423)

Las unidades de los valores seleccionados son `per mil VPDB` en carbonato cálcico y el método declarado es espectrometría de masas de razones isotópicas. Las tablas son compuestos de varios espeleotemas; la pertenencia de cada muestra a una pieza y las incertidumbres de su edad no se reconstruyen en esta primera extracción.

**Conflicto de ubicación Soreq:** el bloque Site_Information y el bbox del API declaran 31.8 N, 35.0 E; el párrafo Description_Notes declara 31.45 N, 35.03 E. La extracción conserva 31.8/35.0 como coordenada cartográfica declarada en Site_Information, con `qc_notes` visible. No se hizo una corrección geográfica silenciosa. Peqiin tiene 32.58 N/35.19 E, 650 m de elevación, concordantes en metadata/archivo. Soreq declara 400 m de elevación.

**Conflicto textual de unidad de edad:** Data_Collection indica `cal yr BP`, mientras el nombre y definición de la columna numérica son `age_calkaBP` y `calendar kiloyear before present`. Los números (p. ej. 0–184) y la cobertura del estudio son coherentes con ka BP; se retienen sin multiplicar ni dividir, usando la definición específica de variable. El conflicto queda documentado, no borrado.

### Sofular So-1

[NOAA Study 8637](https://www.ncei.noaa.gov/access/paleo-search/study/8637), dataset DOI [10.25921/3hwz-z793](https://doi.org/10.25921/3hwz-z793). Site 22943, table 12506, ubicación 41.416 N/31.934 E, elevación 700 m.

Artículo: Fleitmann et al. (2009), *Timing and climatic impact of Greenland interstadials recorded in stalagmites from northern Turkey*, Geophysical Research Letters 36, L19707, DOI [10.1029/2009GL040050](https://doi.org/10.1029/2009GL040050). Se verificó la ficha editorial y el PDF institucional de la Universidad de Berna: [texto de autor](https://climatehomes.unibe.ch/~raible/fleitmann_grl_2009.pdf). La cronología de So-1 se basa en interpolación lineal entre dataciones U-Th; el artículo declara una interrupción entre 21.2 y 24.8 ka BP. Se añade ese intervalo a `hiatus_intervals_ka`: no dibujar una línea/interpolación continua sobre ese hiato.

Descargas oficiales:

- [Tabla Sofular](https://www.ncei.noaa.gov/pub/data/paleo/speleothem/asia/turkey/sofular2009-noaa.txt)
- [Metadata JSON de estudio](https://www.ncei.noaa.gov/access/paleo-search/study/search.json?NOAAStudyId=8637)

La tabla usa `age_calBP` (años calendario antes de 1950), `depth_mm`, δ13C y δ18O VPDB. La única conversión temporal es `age_ka_bp = age_calBP / 1000`. No se recalibran edades. El archivo declara precisiones analíticas de 0.06‰ para δ13C y 0.07‰ para δ18O (1σ); se registran como precisión del método, no como incertidumbre de edad. La versión NOAA de febrero de 2024 agregó profundidades provenientes de SISAL; esto no cambia el año del artículo 2009.

## Acceso, licencia y atribución

En los dos estudios consultados los campos `dataLicenseDescription` y `dataLicenseUrl` son nulos. Por ello no se atribuye CC0 o CC BY al registro por suposición. Los archivos solicitan citar artículo, dataset DOI, landing page y fecha de acceso. El programa [NOAA WDS contributing data](https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data) describe estas contribuciones como datos libre y permanentemente disponibles sin restricciones; el [plan de gestión del área paleoclimática](https://www.ncei.noaa.gov/pub/data/paleo/data_management/ncei-paleoclimatology-data-management-plan.pdf), sección 7.1, declara sus productos públicamente disponibles sin restricciones.

La extracción etiqueta esa base de acceso como política NOAA WDS con atribución científica, conservando nulos los campos de licencia específica. No traslada permisos a las figuras editoriales ni redistribuye el PDF del artículo. Si la política del producto exige una licencia SPDX explícita, estos tres registros deben mostrarse como metadata/preview hasta completar revisión de derechos, en lugar de inventar la licencia.

## Comparabilidad y mapas

δ18O de calcita de espeleotema y δ13C de calcita se mantienen como dos proxies distintos, separados de isótopos marinos o de agua y de SST. Compartir VPDB no convierte los valores entre archivos en una temperatura, precipitación u oxigenación común. Sus niveles medios pueden depender de localidad, elevación, fuente de humedad, estación, vegetación y procesos de cueva.

Un mapa inicial defendible colorea los sitios según el estadístico de observaciones dentro del intervalo, informa n/rango/edad mínima/máxima real y muestra la advertencia de Soreq. Una normalización por serie debe usar una referencia explícita y marcar su cobertura; Peqiin no puede normalizarse respecto a 0–10 ka porque no contiene ese tramo. No se calcularon aquí z-scores, superficies interpoladas ni índices que mezclen δ18O, δ13C y SST.

## Verificación y transferencia

El script comprueba IDs de sitio/tabla, cabecera, número de columnas y finitud de valores; conserva cada celda de origen y los SHA-256. Los números seleccionados proceden de tablas NOAA vinculadas a los artículos; no se ha realizado una validación científica independiente de todos los valores o de sus modelos de edad. `continental_seed.json` tiene seis series, tres registros y 11870 observaciones; la entrega no modifica los modelos centrales ni la app. Pendiente: revisión independiente de coordenadas Soreq y de unidad textual del bloque Collection frente a la definición de variable, además de política final de reutilización del atlas.
