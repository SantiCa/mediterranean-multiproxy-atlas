# Lote de cobertura prioritaria — 30-10-2026

Padre inmutable: v5-c501be5f380, 128 registros / 1.086 series / 865.593 valores.
Resultado v6-c8ff5c5a738: **138 / 1.311 / 903.690**; diez registros, 225 series
y 38.097 valores nuevos. Un registro no implica un vecino espacial independiente.

Se intentaron 82 datasets PANGAEA: 76 TSV/XML recuperados y seis HTTP401, sin
eludir restricciones. Se seleccionaron columnas ausentes de datasets ya curados
y fuentes nuevas; no se volvió a contar una tabla por cambiar de repositorio.
PANGAEA aporta 213 series/36.937 valores admitidos; NOAA aporta12/1.160.
El ensamblador rechaza vectores numéricos completos duplicados, conserva enlaces
de solapamiento parcial y contrasta que todo v5 permanezca exactamente igual.

## Cobertura

Recuento por variable y unidad, antes → después. La comparación visual conserva
fracciones, denominadores, métodos y contextos: esta tabla no afirma equivalencia.

| Indicador | Registros | Ubicaciones distintas después |
|---|---:|---:|
| Ti/Ca |7 → 8|8|
| Fe/Al |2 → 4|3|
| Mn/Al |0 → 2|2|
| Zr/Al |0 → 3|2|
| D50 (fracciones separadas en la aplicación) |1 → 4|4|
| Sortable silt porcentual (contextos separados) |0 → 4|3|
| Polen arbóreo porcentual (sumas separadas) |1 → 3|3|

Los taxones forestales conservan nombre/tipo nativo y unidad: por ejemplo Fagus
en recuentos aparece en dos registros y en porcentaje en uno. No se convierten
recuentos en cobertura forestal ni se inventan clases de bosque. El fichero
reports/priority_v6_coverage.json contiene el balance completo, incluyendo series
únicas preservadas pero ocultas por defecto por el filtro ≥2 registros.

## Fuentes y controles específicos

- PANGAEA966842/966843: razones XRF de MVSEIS08_TG-2 y GC-01A-PC/TC; se conservan
  [Zr/Al y ln(Zr/Al)](https://doi.org/10.1594/PANGAEA.966843) como variables distintas.
  PC y TC se separan usando la columna Event, con localizadores de fila originales;
  sus coordenadas coincidentes no se cuentan como vecinos independientes del IDW.
- [PANGAEA944306](https://doi.org/10.1594/PANGAEA.944306): K/Al, Ti/Al y Ba/Ti
  de NDT-6-2016. Las cuentas/razones XRF no se convierten en concentraciones.
- [PANGAEA961603](https://doi.org/10.1594/PANGAEA.961603): polen de Prespa,
  porcentajes AP con y sin Pinus, árboles templados y Quercus caducifolio. Las
  sumas con exclusiones conservan un contexto de comparación propio.
- [NOAA43639](https://www.ncei.noaa.gov/access/paleo-search/study/43639),
  [Selvaggi et al.2026](https://doi.org/10.1016/j.quascirev.2026.109800): Mn/Al,
  Zr/Rb, Ti/Ca, SS%, tamaño medio de sortable silt, microhábitats bentónicos,
  índice de oxígeno, U/Mn y dos taxones ya presentes en v5. Cinco tablas, un solo
  registro NDT_22_2016. Es agua **intermedia,432m**, no una reconstrucción abisal.
  El índice Oxy_Index no se equipara a una fórmula BFOI no confirmada. U/Mn_std
  es1σ nativo; no se inventa incertidumbre de las edades.
- La traducción NOAA Epifauna/Infauna/Deep_infauna a los rótulos de comparación
  epifaunal/infaunal/deep infaunal se declara en el contrato; no se atribuye a NOAA
  un parámetro PANGAEA original. Se conserva PaST y su columna mediante el JSON
  nativo fijado por hash. Ti/Ca no declara unidad en su cabecera: original_unit
  es nulo y la etiqueta adimensional no implica calibración a masa.

## Pendientes y cuarentenas

29 fuentes PANGAEA retenidas:18 por licencia que requiere revisión antes de nueva
redistribución,6 por HTTP401,3 por cronología radiocarbono no armonizada,1 fuera
de la caja configurada y1 sin edad propia admitida. No se eliminan esos metadatos.

Cinco series completas preservadas en el fragmento de cuarentena: dos fracciones
63–31µm con porcentajes fuera de[0,100], y tres «mean, carb-free» que el proveedor
etiqueta en%. No se recortan ni se reinterpretan comoµm. El SS_mean de NOAA está
expresamente en micrómetros y sí puede incorporarse con esa unidad.

NOAA10418, [Dean y Arthur2010](https://doi.org/10.3133/ofr20101323): once sondeos
del mar Negro con geoquímica y profundidad, pero sin edad por muestra en la tabla.
La narración estratigráfica no se convierte en un modelo numérico inventado.
Este lote no demuestra cobertura completa de PANGAEA, NOAA, Neotoma o literatura.

La interfaz muestra las notas por serie incluso si su sondeo procede del padre;
la inclusión manual de cuarentenas y la tabla completa de originales/exclusiones
siguen pendientes de su tarea específica. No se presentan como implementadas.

## Reproducir

```powershell
python scripts/importers/curate_priority_v6.py --prepare --fetch
python scripts/importers/curate_priority_v6.py --fetch
python scripts/importers/curate_noaa_priority_v6.py --fetch
python scripts/build_quantitative_v6.py
python scripts/summarize_priority_coverage.py
python -m unittest discover -s tests -v
node --test app/atlas-web/tests/*.test.mjs
```

Sin --fetch, los curadores requieren originales locales con hashes coincidentes.
El contrato NOAA ya fija sus columnas/unidades y no debe regenerarse para aceptar
cambios de proveedor sin revisión. Los originales se guardan ignorados; contratos,
informes y scripts sí están versionados. La comprobación de cada celda nueva usa
fila, línea física, columna, valor y edad originales; el cambio NOAA es únicamente
años calendario BP/1000. Las pruebas no certifican reconstrucciones independientes.

El flujo de curación actualiza v6 tras cambiar v5. El snapshot y el ensamblador
rechazan un padre obsoleto antes de sustituir el snapshot comprobado; así un v6
antiguo no oculta incorporaciones posteriores a v5. Para futuras regiones la caja
se configura por lote; no se identifica ni fusiona un core por proximidad.
