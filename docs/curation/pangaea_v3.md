# Curación PANGAEA — primer lote cuantitativo v3

Consulta y descarga: 28-10-2026. Script `scripts/importers/curate_pangaea_v3.py`; ejecución offline por defecto, `--download` para recuperar los recursos explícitos. TSV y XML nativos en `data/interim/quantitative_v3/pangaea/`, ignorado; hashes SHA-256 revisados y fijados en el script. Un cambio remoto requiere revisar un nuevo snapshot, nunca sobrescribir silenciosamente el original. Los DOI de artículos se contrastan con respuestas Crossref preservadas. No se ha realizado una auditoría independiente completa de modelos de edad ni calibraciones originales.

| Dataset PANGAEA | Evento | Variables incorporadas | Cronología usada |
|---|---|---|---|
| [438384](https://doi.pangaea.de/10.1594/PANGAEA.438384) | GeoB5901-2 | SST, Prahl et al. 1988 | AGE ka BP publicada |
| [438795](https://doi.pangaea.de/10.1594/PANGAEA.438795) | M40/4_SL78 | SST, Müller et al. 1998 | AGE ka BP publicada |
| [438799](https://doi.pangaea.de/10.1594/PANGAEA.438799) | M39/1_08-3 | SST, Müller et al. 1998 | AGE ka BP publicada |
| [789685](https://doi.pangaea.de/10.1594/PANGAEA.789685) | GT91-1 | UK′37 y SST publicadas | a AD/CE → (1950−CE)/1000 |
| [789686](https://doi.pangaea.de/10.1594/PANGAEA.789686) | GT89-3 | UK′37 y SST publicadas | a AD/CE → (1950−CE)/1000 |
| [789690](https://doi.pangaea.de/10.1594/PANGAEA.789690) | GT90-3 | UK′37 y SST publicadas | a AD/CE → (1950−CE)/1000 |
| [836213](https://doi.pangaea.de/10.1594/PANGAEA.836213) | 161-975 compuesto | δ13C/δ18O, G. bulloides/G. ruber | AGE ka BP publicada |
| [871130](https://doi.pangaea.de/10.1594/PANGAEA.871130) | HER_MC_MR03_1a | SST Mg/Ca | AGE ka BP publicada |
| [818921](https://doi.pangaea.de/10.1594/PANGAEA.818921) | Mo05, lago Mondsee | Ti XRF cps | Varve age a BP /1000 |

Resultado: **9 registros de dataset/evento, 15 series, 37.782 valores finitos**, incluidos 36.459 valores Ti de Mondsee. Todos los valores incorporados tienen edad en las columnas elegidas. Los huecos nativos no se rellenan; las filas se identifican por posición nativa, línea, columna y hash. La cifra no demuestra nueve ubicaciones independientes: GT89-3 y GT90-3 tienen coordenadas idénticas, y las correlaciones entre archivos deben mantenerse explícitas.

## Decisiones científicas

- La SST Prahl1988 se separa de Müller1998. Las dos nuevas Müller1998 comparten grupo de compatibilidad con las SST v1 del mismo método, sin eliminar diferencias ecológicas ni de resolución.
- Versteegh2007 etiqueta UK′37 como calculado según Conte2006, mientras que la columna SST no explicita su calibración en la metadata nativa. Se mantiene un grupo conservador propio para su SST, sin atribuirle automáticamente Conte2006. Los tres cores comparten una cuadrícula temporal con numerosas celdas vacías; se conservan únicamente valores presentes. El dataset compuesto789691 se excluye para no añadir el agregado como réplica independiente.
- Las cuatro series isotópicas de ODP975 permanecen separadas por especie e isótopo. El encabezado abrevia PDB pero cada comentario de parámetro explicita VPDB: se estandariza la etiqueta, con números sin transformación y unidad original conservada. El registro es un compuesto de sitio, no un único testigo individual.
- Cisneros2016: la metadata PANGAEA denomina anual a la SST Mg/Ca, pero el [artículo primario](https://cp.copernicus.org/articles/12/849/2016/) identifica una señal primaveral de G. bulloides. Se conservan ambas informaciones, grupo independiente y límites mínimo/máximo por fila. No se inventa una incertidumbre simétrica ni nivel de confianza.
- Mondsee: se usa exclusivamente la columna explícita de edad varvada BP. Su columna AD/CE contiene magnitudes sin signo para edades anteriores a CE y no se convierte automáticamente. Se preserva el valor −0,053 ka BP del techo. Ti cps representa respuesta instrumental, no concentración; el grupo queda restringido al dataset/instrumento y no se combina con cps de otros laboratorios.
- Las edades BP publicadas se conservan tal cual; no se afirma que su calendario haya sido verificado de manera independiente. No se interpolan modelos de edad ni se recalibran edades 14C. La conversión CE/BP cambia únicamente la referencia y la escala de una cronología calendárica explícita.
- PANGAEA438795 conserva la relación declarada con un editorial contextual de 2003 en `related_reference_*`. `publication_year` y `paper_doi` permanecen nulos porque no se verifica un artículo original de las mediciones; el año2003 del dataset/editorial no participa como año de artículo en filtros. El propio dataset es citable. PANGAEA438795 y438799 advierten ser subconjuntos de las versiones publicadas: no se declara haber importado los originales completos.
- PANGAEA854682 (PRGL1) se descargó pero **no se ingiere**: la relación nativa cita un trabajo submitted sin DOI final verificado. No se asigna el año del dataset como año de artículo.

## Calidad y duplicados

Se rechazan datasets con DOI ya existente en la semilla y series con firma exacta de pares edad/valor ya cargados; no se fusionan eventos por semejanza. No hay repeticiones exactas de edad+valor+profundidad en las series seleccionadas. GeoB5901-2 tiene35 edades repetidas y Mondsee15: corresponden a filas con profundidades distintas y se conservan, sin equiparar igual edad a duplicación demostrada.

La comparación de DOI nativo enlaza cada registro con su entrada DataCite del inventario. El informe por serie distingue valores ausentes, censurados/no numéricos, edades desconocidas, ceros, edades negativas y repeticiones. La igualdad exacta no basta para descartar solapamientos parciales: la integración con NOAA debe revisar especialmente las reconstrucciones de Golfo de Taranto y sus republicaciones. Ni proximidad geográfica ni nombres parecidos demuestran equivalencia.

`tests/test_pangaea_v3.py` compara cada uno de los37.782 valores y sus localizadores con las tablas nativas, valida las referencias de edad, las unidades, el aislamiento XRF y los42 límites asimétricos. Las pruebas de originales se omiten explícitamente cuando la caché ignorada no está disponible; las pruebas de conversión/censura no requieren red.
