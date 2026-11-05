# AUD-PROXY-USO: datos, agrupaciones y proxies calculados

Auditoría del 05-11-2026 sobre v17-c6564e1246e. Evidencia reproducible en `reports/proxy_use_audit.json` y `scripts/audit_proxy_use.mjs`. Se comprobó además v18-c6df0c5c06b, provisional y en pausa del rol 01: `reports/proxy_use_v18_provisional_audit.json`. El examen estructural de v18 no sustituye su cierre de curación.

## Resultado y alcance

- v17: 256 registros, 1.972 series, 971.380 valores; 1.000 grupos base y 143 agrupaciones de consulta tras las correcciones.
- Todas las celdas numéricas: sin valores no finitos, porcentajes fuera de 0–100, identificadores duplicados, series huérfanas, discrepancias de recuento/extensión ni localizadores repetidos por serie.
- 6.615 valores sin edad permanecen conservados y fuera de mapas por edad. Se conservan 7.035 edades BP negativas y 70.962 ceros observados.
- Sin candidatos de vector completo idéntico de al menos diez muestras para el mismo proxy/unidad. Siete grupos de coordenadas coincidentes requieren revisión de identidad; no se fusionan. No se certifica ausencia de duplicación parcial ni independencia de cronologías.
- v18 provisional: 258 registros, 1.984 series y 971.680 valores; sin errores en los mismos controles. Conserva su estado provisional y sus bloqueos de cronología.

La auditoría recorre la colección procesada completa y la lógica de consulta. No reextrae todos los originales ni revalida cada edad o interpretación ambiental. El inventario de 5.846 entradas de sondeos/sitios/unidades y 9.726 referencias a datasets tiene otro grano: descubrir una fuente no garantiza observaciones cuantitativas revisadas.

## Correcciones de uso

1. Se muestran por defecto los grupos de un solo registro: 873 grupos estaban ocultos por el mínimo de dos, pese a servir para localizar sondeos y asociaciones publicadas. El filtro de dos registros sigue disponible.
2. Familias de presentación coherentes: Palinología → Polen y Biomarcadores → Materia orgánica y biomarcadores. Se conserva `series.family` nativo; la función `proxyFamily` aplica el vocabulario de consulta.
3. Dos índices OI de Rock-Eval de ODP 160-967A y 161-976C estaban etiquetados como Foraminíferos. Se presentan como materia orgánica y se corrige la regla de descubrimiento para futuras ingestiones. La ficha primaria [PANGAEA.259364](https://doi.pangaea.de/10.1594/PANGAEA.259364) define CO2/TOC en mg/g y método Rock-Eval; no es un BFOI.
4. Nueve series SST sin estación explícita dejan de clasificarse automáticamente como anuales. Hay agrupación de estación no declarada; los grupos anual/verano/invierno exigen etiqueta explícita.
5. Los porcentajes polínicos sin contexto de denominador no generan agrupaciones automáticas por nombre de parámetro. Permanecen consultables en sus grupos base. La normalización z no demuestra equivalencia de calibración, especie o estación.
6. Atajos de consulta para censos de foraminíferos, AP/NAP, mesófilos, microhábitats bentónicos, Ti/Ca y sortable silt. «Agrupación» significa selección de series; la suma de especies requiere una fórmula aparte.

## Proxies de uso real y cobertura

La colección contiene asociaciones publicadas: polen AP/NAP con/sin Pinus, mesófilos, montanos, relictos y woody taxa; microhábitats bentónicos epifauna/infauna/infauna profunda; censos específicos planctónicos/bentónicos. Se distinguen de SST reconstruida, isótopos, geoquímica, índices orgánicos y sedimentología. Los recuentos por uso están en `report.coverage`: son ayudas de búsqueda, con categorías solapadas, y no una validación ambiental.

El cribado no detecta series numéricas de bioturbación/icnofábrica. Nanofósiles/diatomeas tienen cobertura escasa. Reading incorpora seis taxones seleccionados por entidad: no se debe presentar su suma como bosque total, AP o asociación mediterránea completa.

Fuentes primarias consultadas el 05-11-2026:

- [ForCenS-LGM, Jonkers et al. 2024](https://www.nature.com/articles/s41597-024-03166-7): censos por muestra y taxonomía armonizada son requisitos de comparación de ensamblajes. No se ha importado este dataset durante la auditoría.
- [Hes et al. 2022](https://cp.copernicus.org/articles/18/1429/2022/): las sumas polínicas y la asociación forestal dependen de exclusiones explícitas; Pinus no comparte necesariamente denominador con otros taxones.
- PANGAEA.259364, citada arriba, respalda la corrección de OI. La lectura completa de MDPI 9/5/551 encontró HTTP 429; no se usa como evidencia de un nuevo preset ecológico.

## Crear proxies

En «Proxies y series» → «Crear proxy de especies»: elegir sondeo y tabla, nombre, términos A/B y operación. Permite suma A, relación A/B y proporción 100 × A/(A+B). Opcionalmente aplica la misma receta a otras tablas con todos los taxones, método, unidad, fracción, denominador y cronología compatibles. Taxones ambiguos o ausentes excluyen la tabla, nunca se imputan a cero.

El motor exige identidad de sondeo/tabla/hash y localizadores nativos de fila/línea para cada cálculo. Comprueba concordancia de edad, profundidad e incertidumbre cronológica; no une por edad ni interpola. Rechaza denominador cero, porcentajes imposibles, localizadores ambiguos y sumas porcentuales >100. El usuario declara ausencia de solapamiento taxonómico; no se deduce automáticamente que un grupo AP excluya un taxón seleccionado. Los porcentajes sin contexto verificable requieren curación previa; no se ofrecen como entradas.

Resultados identificados como transformación de usuario, con unidad y fórmula. Los originales de entrada, hashes, columnas y exclusiones se exportan en JSON y los puntos CSV llevan fórmula y entradas por muestra. El resultado no se presenta como un valor originalmente publicado. La incertidumbre del valor no se propaga; no se asigna calibración ambiental.

Recetas locales, hasta 20, exportables/importables como JSON; al restaurarlas se calculan contra la colección disponible comprobando hashes de referencia. «Todos compatibles» puede incorporar nuevas tablas en una colección posterior: guardar también la auditoría del resultado para fijar el conjunto exacto usado. Ninguna receta modifica la semilla ni se publica en el servidor.

## Verificación

133 pruebas Python y 34 Node correctas, TypeScript y build correctos. Snapshot v17: 971.380 filas cotejadas celda a celda. QA de escritorio: buscar mesófilos devuelve las dos asociaciones de Ohrid con/sin Pinus aun siendo de un registro; filtro ≥2 desmarcado. Suma real Abies + Alnus: 102 tablas, 7.110 valores; mapa 6–8 ka con 59/102 sitios y 961 valores. Captura local ignorada: `outputs/proxy-use-qa.png`. No se certifica QA móvil ni publicación remota.

## Siguiente paso

Rol 01 retoma CUR-READING-18 y completa su cierre. La integración conjunta en main queda pendiente para no incorporar por accidente el commit provisional 7891aa1. Después, rol 04 publica el código con la última colección validada. Producción continúa v13. Mantener los bloqueos de MD99-2337, reservorios/identidad y la futura tabla QC de originales/exclusiones.
