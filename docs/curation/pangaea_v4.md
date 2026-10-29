# PANGAEA — ampliación cuantitativa v4

Corte de descarga y revisión: 29-10-2026. Scripts y contratos: `scripts/importers/curate_pangaea_v4.py`, `pangaea_v4_sources.json`. Originales TSV/XML y Crossref en `data/interim/quantitative_v4/pangaea/`, ignorado; fragmento en `data/interim/quantitative_v4/pangaea_curated.json`. La ejecución es offline por defecto. `--download` recupera recursos explícitos ausentes con tamaño/tiempo acotados y exige hashes TSV/XML revisados antes de guardarlos. Cambios remotos requieren un nuevo snapshot, no sobrescritura silenciosa.

**Resultado activo: 11 eventos nuevos, 15 datasets que aportan datos, 41 series y 4.271 valores.** Se revisaron 17 tablas del contrato; cuatro series/531 valores quedan en cuarentena. No se equiparan tablas con cores independientes: Bichlersee, Verney, CP10BC, GeoB7608 y Peixão reúnen varias tablas bajo un evento. El rango numérico activo del lote es **−0,069 a 193,07 ka BP**. Ningún valor activo carece de edad en este lote. La ampliación no implica una auditoría independiente de todos los modelos cronológicos.

| Evento | Dataset(s) activos | Variables / revisión |
|---|---|---|
| M40/4_KL51, M44/3_KL83, M40/4_SL67, M40/4_SL71 | [69822](https://doi.pangaea.de/10.1594/PANGAEA.69822), [69823](https://doi.pangaea.de/10.1594/PANGAEA.69823), [69824](https://doi.pangaea.de/10.1594/PANGAEA.69824), [69825](https://doi.pangaea.de/10.1594/PANGAEA.69825) | G. ruber blanco δ18O, Finnigan MAT251, ‰ PDB; grupo común por especie/método/estudio |
| GeoB7608-1, Mar Negro | [667328](https://doi.pangaea.de/10.1594/PANGAEA.667328) | Candona spp. δ18O; versión de edad revisada; TOC de 667403 en cuarentena |
| CP10BC, Jónico | [944656](https://doi.pangaea.de/10.1594/PANGAEA.944656), [944660](https://doi.pangaea.de/10.1594/PANGAEA.944660) | TOC, Sr detrítico, 87Sr/86Sr, 143Nd/144Nd y εNd(0); dos bloques con edades propias |
| GeoB7702-3, margen de Israel | [961488](https://doi.pangaea.de/10.1594/PANGAEA.961488) | n-C31 δD corregido por hielo y por vegetación+hielo; aporte C4 publicado, grupos separados |
| DSDDP_5017-1-A, Mar Muerto | [940127](https://doi.pangaea.de/10.1594/PANGAEA.940127) | C30 ácido graso δD y δ13C; edad posterior mediana Bacon y límites probabilísticos nativos |
| Bichlersee_BS_14, Alpes | [962012](https://doi.pangaea.de/10.1594/PANGAEA.962012), [962033](https://doi.pangaea.de/10.1594/PANGAEA.962033), [962034](https://doi.pangaea.de/10.1594/PANGAEA.962034) | TOC/CaCO3, n-C27/29/31 δD y fucosa δ18O; edad mediana publicada |
| Verney_Mastercore, Alpes | [878051](https://doi.pangaea.de/10.1594/PANGAEA.878051), [878053](https://doi.pangaea.de/10.1594/PANGAEA.878053) | LOI a 550°C/4h, 950°C/2h y residuo; óxidos/elementos XRF en % nativo con SD |
| PEX19-01, lago Peixão | [954457](https://doi.pangaea.de/10.1594/PANGAEA.954457) | TOC en cronología publicada válida; isótopos de 995820 en cuarentena |

## Cronología, unidades e incertidumbre

- Cada serie conserva su propio DOI de dataset, artículo y año, fuente/columna, hash, cita, licencia y URL. Los campos bibliográficos del core corresponden a su fuente primaria activa; no se hereda el año2026 de un dataset en cuarentena a TOC2023. Los DOI/años se verifican contra Crossref y enlaces nativos. Los artículos de2026 se publicaron antes del corte; la identidad bibliográfica no valida las mediciones.
- Las edades publicadas puntuales en ka BP se copian sin interpolar profundidad/edad, recalibrar 14C ni convertir por conjetura. Los cuatro registros Weldeab y el modelo revisado Bahr permanecen clasificados BP archivado, sin afirmar una escala calendárica armonizada ni independencia de correlaciones estratigráficas.
- Las etiquetas PDB de Weldeab y Candona se conservan **‰ PDB**. No se asume VPDB. Para Bichlersee n-alcanos/fucosa los comentarios nativos explicitan V-SMOW; para Meyer explicitan VSMOW; para Mar Muerto explicitan VSMOW y VPDB según isótopo. Solo esas referencias explícitas justifican la etiqueta estándar; los números y el encabezado original se conservan.
- Los SD, SE y la incertidumbre εNd etiquetada como **2 sigma** se conservan con su tipo nativo; no se divide por dos ni se asignan incertidumbres genéricas del método a cada muestra.
- Mar Muerto conserva los cuatro límites de edad por fila, niveles0,025/0,16/0,84/0,975, asociados solo a sus series C30. No se convierten en un error simétrico ni se trasladan a otras series.
- Las correcciones publicadas de hielo/vegetación de Meyer son transformaciones o reconstrucciones, no mediciones brutas nuevas. Tampoco LOI a950°C se mezcla con CaCO3 de otro método por compartir porcentaje. Los XRF de Verney son fracciones nativas, no cps ni concentraciones recalculadas.

## Cuarentenas y exclusiones

1. **PANGAEA995820, Peixão: tres series/396 valores completos.** La columna se etiqueta `Age [ka BP]`, pero las primeras28 edades van de−0,069 a0,970 y la siguiente salta a1003, terminando en11150. La descripción y el [artículo de2026](https://doi.org/10.1029/2026PA005517) corresponden a un registro holoceno de unos11100 años; los órdenes de magnitud son incompatibles. No se divide una parte por1000 ni se publica11,15Ma como antigüedad real. Los originales y números del fragmento en cuarentena permanecen intactos hasta una aclaración verificable. Las columnas denominadas min/max de la reconstrucción también están numéricamente invertidas porque representan sensibilidades ε−12/ε+12; se conservan con sus nombres de parámetro y no como límites estandarizados.
2. **PANGAEA667403, TOC GeoB7608: una serie/135 valores completos.** Incluye una celda nativa−1,71%; no es una fracción física de carbono interpretable sin aclaración analítica. Se preserva íntegramente, sin borrar la celda ni recortarla a cero. El core sí aporta el δ18O de Candona del dataset667328.
3. **CP10BC944656:** solo se admite el primer bloque profundidad/edad/TOC. Hay una segunda columna también llamada profundidad sedimentaria, con valores incompatibles con la primera. Los elementos y razones posteriores no reciben edades por compartir fila. La tabla944660 sí presenta sus propias edades puntuales y aporta Sr/Nd.
4. SL114BC944662 y Verney878052 (granulometría), entre otras tablas exploradas, carecen de edades puntuales. No se interpolan ni se unen a tablas cronológicas por semejanza de profundidad.

## Duplicados y derechos

No se repiten DOI o eventos exactos de la línea base v3. Se comprueban firmas completas de edad/valor/unidad; no se fusionan cores por proximidad. Una edad repetida no prueba una observación duplicada: dos repeticiones de Bichlersee se conservan en sus filas originales. El número de celdas no es n efectivo. El Mar Negro cambió de condiciones lacustres a marinas; la categoría espacial del archivo no impone un ambiente marino a todas sus edades.

Cada tabla conserva su licencia nativa: CC-BY3.0/4.0 según fuente; **Bichlersee CC-BY-SA4.0**. No se declara una licencia uniforme para toda la colección ni se transfiere la licencia del artículo a los datos. La atribución y las condiciones ShareAlike deben conservarse en reutilizaciones aplicables.

## Verificación y reproducción

```powershell
python scripts/importers/curate_pangaea_v4.py --download
python -m unittest discover -s tests -p test_pangaea_v4.py -v
```

Seis pruebas pasan: contrato de valores ausentes/censurados, todas las celdas/edades/errores y localizadores de las4.802 observaciones revisadas (4.271 activas+531 en cuarentena), agrupación por evento, referencias isotópicas, licencias/años propios, tipos de incertidumbre, parámetros nativos y regresión de la cronología mixta. Las pruebas que requieren los originales ignorados se omiten explícitamente sin caché. El informe por serie, rangos y motivos se conserva en `reports/pangaea_v4_audit.json`.

