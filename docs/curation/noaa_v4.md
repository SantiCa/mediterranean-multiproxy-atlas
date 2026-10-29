# NOAA v4 — nuevos archivos continentales y proxies

Descarga de tablas y contraste bibliográfico: 29-10-2026; metadata de descubrimiento NOAA preservada de 28-10-2026. Lote explícito, no cosecha exhaustiva. Contrato: `scripts/importers/noaa_v4_sources.json`; curador offline: `python scripts/importers/curate_noaa_v4.py`. `--fetch` recupera recursos ausentes y exige SHA-256; un cambio del proveedor requiere revisar nueva versión. Originales ignorados en `data/interim/quantitative_v4/noaa/`.

## Incorporación propuesta

| Estudio NOAA | Registro de archivo | Series | Valores | Proxies |
|---|---|---:|---:|---|
| [33716](https://www.ncei.noaa.gov/access/paleo-search/study/33716) | Kaite, Buda-100 | 2 | 148 | 87Sr/86Sr y flujo de polvo reconstruido |
| [11817](https://www.ncei.noaa.gov/access/paleo-search/study/11817) | Trio, TRIO1 | 11 | 3.578 | Óxidos/trazas, δD de inclusiones y δ13C/δ18O |
| [23970](https://www.ncei.noaa.gov/access/paleo-search/study/23970) | Ifoulki, IFK1 | 4 | 12.298 | Mg/Sr en ppm e isótopos |
| [22582](https://www.ncei.noaa.gov/access/paleo-search/study/22582) | Lago Redon, Pla2004 | 1 | 56 | Anomalía térmica invierno/primavera, quistes |
| [13017](https://www.ncei.noaa.gov/access/paleo-search/study/13017) | Lago Silvaplana, Trachsel2008b | 2 | 721 | Índices XRD normalizados |
| [5463](https://www.ncei.noaa.gov/access/paleo-search/study/5463) | Monticchio, compuesto B/D/J/L | 2 | 1.123 | Si biogénica normativa corregida y LOI |

Total **6 registros, 22 series, 17.924 celdas cuantitativas**. No se demuestra que seis registros bibliográficos equivalgan a seis sondeos físicos independientes. Identidades enlazadas por estudio/sitio exactos al inventario; sin fusiones por proximidad ni prefijos.

## Decisiones científicas

- **Kaite:** [Cruz2021](https://doi.org/10.1126/sciadv.abe6102) distingue Sr medido mediante TIMS de polvo reconstruido por balance de masas. El artículo, recuperado mediante BioC oficial PMC11559594, explicita 43°2′N/3°39′W. La conversión decimal primaria gobierna la posición; se conservan los puntos discordantes de JSON NOAA (43.04/−3.6597) y cabecera (43.33/−3.66). No se toma el error inicial de 230Th como incertidumbre de todas las muestras.
- **Trio:** [Siklósy2009](https://doi.org/10.1002/rcm.3943). NOAA añadió en marzo2025 edades según el modelo lineal publicado. Se utiliza la columna suministrada; no se calcula una edad desde profundidad. La tabla isotópica de menor resolución queda pendiente para evitar solapamiento; δ18O en VSMOW no se cuenta de nuevo tras seleccionar VPDB. δD de agua de inclusiones permanece separado del carbonato.
- **Ifoulki:** [Ait Brahim2017](https://doi.org/10.1016/j.epsl.2017.07.045). Mg y Sr son concentraciones en ppm, no razones Mg/Ca y Sr/Ca. Las edades CE se convierten por (1950−CE)/1000. El alias age_AD/age_CE de la tabla isotópica se declara. Las incertidumbres de los controles U-Th no se propagan ficticiamente.
- **Redon:** [Pla2004](https://doi.org/10.1007/s00382-004-0482-1). Se conserva una anomalía de temperatura, no temperatura absoluta, y el error publicado sin atribuirle 1σ u otro nivel. Las columnas calendarioBP y CE se contrastan algebraicamente. PAGES2k/LiPD son republicaciones, no nuevos datos.
- **Silvaplana:** [Trachsel2008](https://doi.org/10.1029/2008GL034121). Los índices minerales están normalizados en la fuente; sus signos negativos son válidos. No se convierten localmente en precipitación ni temperatura ni se interpretan como razones minerales negativas.
- **Monticchio:** [Allen1999](https://doi.org/10.1038/23432). Se usa la edad publicada de laminaciónBP/1000, con dependencia de tasas de sedimentación/tefras explícita. El compuesto de cuatro cores es un solo registro. Si normativa corregida contiene74 ceros, incluidos73 asociados a estimaciones nativas negativas de la columna sin corregir: se conserva la corrección publicada, sin recalcularla. No son 74 ausencias de sílice demostradas.

## Cuarentenas, unidades y trazabilidad

**7 series completas / 3.007 valores en cuarentena:** Ce, Pr, Nd y Th, La/Ce de TRIO1 por concentraciones/razones negativas; La/Th por denominador Th pendiente; y Si normativa sin corregir por73 valores negativos. No se recortan muestras ni se corrigen signos. Densidad seca y susceptibilidad de Monticchio quedan pendientes por convención de unidades no resuelta.

Ifoulki y Redon declaran UTF8, pero contienen bytes heredados Windows1252: el contrato fija la decodificación, conserva bytes/hashes y celdas numéricas ASCII. Se preservan fila, línea física, columna, edad/valor originales, unidad nativa, URL y hash de cada serie. Las ausencias/censuras se cuentan y no se imputan.

No hay coincidencias de vectores completos ni solapamientos amplios de pares edad/valor con la línea base v3. Se conserva más de una representación como cuarentena/referencia cuando puede duplicar la misma medida. Esto no certifica ausencia universal de solapamiento parcial.

Los campos CC específicos NOAA están vacíos; se mantiene esa ausencia y la [política de disponibilidad WDS](https://www.ncei.noaa.gov/products/paleoclimatology/contributing-data), sin asignar CC0 ni trasladar la licencia del artículo al dataset.

`reports/noaa_v4_audit.json` resume cada serie y cuarentena. `tests/test_noaa_v4.py` contrasta todas las celdas del lote y de sus cuarentenas con originales, referencia temporal, signos, unidades, errores y localizadores. Cinco pruebas locales correctas; no equivalen a una auditoría independiente de modelos de edad.
