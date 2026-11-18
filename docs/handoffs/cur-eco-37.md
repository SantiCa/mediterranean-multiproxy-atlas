# CUR-ECO-37

18-11-2026. `atlas-quantitative-2026-11-18-v37-ca98c1d0c15` añade seis eventos, 24 series y 2.292 observaciones a v36, cuyo contenido se conserva. Los nuevos eventos son Bonnecombe (BCOMBE1), Brameloup (BRAMELOU), lago Ledro (LL081), lago Martignano (MARTIGAN), Urio Quattrocchi (QUATTROC) y lago Segrino (SEGRINO). El tipo general se mantiene como sedimento porque hay tanto turberas como lagos.

La [tabla PANGAEA.989934](https://doi.pangaea.de/10.1594/PANGAEA.989934), relacionada con [d'Oliveira et al. (2025)](https://doi.org/10.5194/cp-21-2331-2025), contiene reconstrucciones estacionales basadas en polen. Se incluyen las medias publicadas de MAT y BRT para temperatura del aire (°C) y precipitación (mm por estación), diferenciando verano e invierno. No son mediciones directas; las estimaciones y sus componentes utilizan muestras comunes. No se calculan nuevos valores ni incertidumbres.

Se contrastaron nombres y proximidad frente a v36, pero la distancia no demuestra independencia de muestras entre bases: quedan pendientes la identidad cruzada y la revisión de los modelos cronológicos. Las fuentes previas por evento están identificadas en el TSV original, incluidas las publicaciones de Ledro y los DOI Neotoma de las demás secuencias. Los caracteres de reemplazo presentes en algunos metadatos del TSV del proveedor se conservan; las unidades de las columnas seleccionadas coinciden con el XML nativo.

Se cotejaron los 2.292 valores nuevos con sus edades, profundidades y localizadores originales. Auditoría científica sin errores estructurales, auditoría de uso sin vectores duplicados y alias controlados revisados; persisten avisos históricos. Pasaron los archivos de pruebas Python, 46 pruebas Node, TypeScript y compilación. La instantánea final se verificó celda a celda: 1.078.640 valores en 1.248 archivos. Reproducir con `python scripts/build_common_v37.py --fetch`.

Integración y publicación reservadas al rol 04; preservar el QC heredado de v36.
