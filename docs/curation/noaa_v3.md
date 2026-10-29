# Lote cuantitativo NOAA v3

Consulta y descarga: 28-10-2026. Primera ampliación acotada, no una cosecha universal. Contrato de fuentes: `scripts/importers/noaa_v3_sources.json`; extracción reproducible offline: `python scripts/importers/curate_noaa_v3.py`. `--fetch` recupera exclusivamente archivos ausentes y exige el hash esperado; una modificación del proveedor requiere revisión de nueva versión. Originales ignorados en `data/interim/quantitative_v3/noaa/`; fragmento de integración en `data/interim/quantitative_v3/noaa_curated.json`. No editar sus valores a mano.

## Contenido listo para integrar

| NOAA estudio | Registros de sitio | Series | Observaciones | Intervalo numérico ka BP |
|---|---:|---:|---:|---|
| 32914, Jalali et al. 2018 | 4 | 16 | 3.306 | −0,0574 a 2,6363 |
| 28070, Panagiotopoulos et al. 2020 | 1 | 34 | 22.374 | 1.163,23 a 1.365,00 |
| 13666, Arnaud et al. 2012 | 2 | 2 | 3.126 | −0,047 a 11,104 |
| Total | 7 | 52 | 28.806 | — |

Los identificadores `inventory_ids` corresponden exactamente a estudio/sitio NOAA del inventario enlazado. Un sitio con varias tablas conserva un único registro. Los recuentos son celdas finitas, no necesariamente muestras independientes ni edades distintas.

### Mediterráneo/Adriático

[NOAA 32914](https://www.ncei.noaa.gov/access/paleo-search/study/32914) enlaza CSS00-07, INV12-15, KESC9-14 y SW104-ND-14 con [Jalali et al., 2018](https://doi.org/10.1029/2017PA003298). Variables: Uᵏ′₃₇, SST publicada, n-alcanos terrestres y ACL. El artículo, secciones 3.1/3.2, documenta modelos con ²¹⁰Pb, ¹⁴C calibrado y tefras según sondeo, y calibración SST Conte et al. (2006). Se mantienen separadas de las SST Müller et al. (1998) de la colección previa. Unidades nativas de las edades: años calendario BP; única transformación temporal, división entre mil. No se transfieren incertidumbres de puntos de control a muestras ni se recalcula la SST.

### Lago Ohrid

[NOAA 28070](https://www.ncei.noaa.gov/access/paleo-search/study/28070), DEEP ICDP5045-1: geoquímica, carbonatos isotópicos, biomarcadores, grupos de diatomeas, grupos de polen, arena y XRF. [Artículo, sección 3.2](https://nora.nerc.ac.uk/id/eprint/526047/1/Lake_Ohrid.pdf#page=4): en este intervalo la cronología depende de ajuste orbital de proxies sensibles al clima; no demuestra sincronía orbital independiente. La columna `age_ka` declara kiloyears calendario BP y se conserva sin conversión, aunque el resumen de colección NOAA indica años. Crossref y el volumen final datan el artículo en 2020, mientras NOAA conserva 2019; se guardan ambos y el filtro usa 2020.

Las tres temperaturas MAAT (Peterse, Russell, de Jonge) quedan en grupos distintos. Los porcentajes polínicos con y sin Pinus conservan denominadores y grupos diferentes. La relación XRF se preserva como `Ti/Ti+K`, con una nota porque el texto del artículo también utiliza Ti/K; no se transforma la razón por inferencia. Una tabla concentra 18.693 valores XRF, de los cuales 61 carecen de edad válida: se conservan con edad nula. Se excluyen 12 errores de cálculo `#DIV/0!`, sin convertirlos a cero. Repeticiones de edad/valor se auditan y permanecen asociadas a sus filas nativas; requieren revisión antes de interpretar n como tamaño efectivo.

### Lago Bourget

[NOAA 13666](https://www.ncei.noaa.gov/access/paleo-search/study/13666), LDB01-I y LDB04-I, [Arnaud et al., 2012](https://doi.org/10.1016/j.quascirev.2012.07.025). El archivo documenta un modelo CLAM con cronología radiocarbónica; las edades publicadas son calendario BP. Se incorpora %terr de LDB01-I y K/Ti de LDB04-I. Las coordenadas redondeadas comunes y la cronología correlacionada no convierten dos cores en réplicas espaciales independientes.

**Cuarentena:** %terr de LDB04-I contiene 18 valores mayores de 100, máximo 124,2. Se preservan sus 1.371 celdas en `quarantined_series` y los bytes originales; la serie completa queda fuera de `series`, sin recorte ni imputación. Cadagno 12909 fue descargado pero queda pendiente porque sus edades son intervalos top/bottom; no se inventa un punto medio. Tampoco se incorporan predicciones categóricas de bioma como números.

## Derechos, trazabilidad y comprobaciones

Los campos de licencia específicos de estos registros NOAA están vacíos. Se conserva esa ausencia y la [política WDS de disponibilidad y uso](https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data), con cita solicitada. No se asigna CC0 ni se transfiere la licencia del artículo al dataset.

Cada serie conserva URL/tabla/columna, hash SHA-256, celdas originales, fila y línea física, unidad/definición nativa y transformación. Ohrid tiene seis archivos: su registro no finge un único hash; usar el hash/URL de cada serie en exportaciones. `reports/noaa_v3_audit.json` resume fuentes, cobertura y cuarentenas. `tests/test_noaa_v3.py` compara todas las edades/valores contra las celdas originales y comprueba BP negativos, ausencias, calibraciones, denominadores y cuarentena. No se presenta como una revisión independiente de todos los modelos de edad.
