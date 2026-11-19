# CUR-ECO-38

19-11-2026. `atlas-quantitative-2026-11-19-v38-c87e896832c` incorpora seis eventos, 24 series y 2.660 observaciones a v37, conservando su contenido. Son Vallon de Provence (CBB75), Correo (CORREO), Embouchac (EMBOU), Lago del Greppo (GREPPO), Lago Padule (PADULE) y Tourves (TOURVES).

La [tabla PANGAEA.989934](https://doi.pangaea.de/10.1594/PANGAEA.989934), relacionada con [d'Oliveira et al. (2025)](https://doi.org/10.5194/cp-21-2331-2025), aporta la media publicada de MAT y BRT para temperatura del aire (°C) y precipitación (mm por estación), separadas por verano e invierno. Son reconstrucciones climáticas basadas en polen y no observaciones directas; los componentes y la media comparten muestras. Sin cálculos ni incertidumbres añadidas.

Los nombres y la proximidad se cotejaron frente a v37. La distancia no demuestra independencia de muestras entre archivos y los modelos de edad requieren revisión. Los DOI Neotoma correspondientes a los seis eventos se conservan en la tabla original. Los caracteres de reemplazo presentes en parte de los metadatos TSV del proveedor se conservan; las unidades de las columnas seleccionadas se cotejaron con XML.

Las 2.660 observaciones nuevas coinciden con sus edades, profundidades y localizadores originales. La auditoría científica no detectó errores estructurales, pero señala 48 temperaturas invernales de CBB75 inferiores a −3 °C (mínimo −14,11 °C) y una de GREPPO (−3,15 °C). El umbral genérico de °C también se aplica a series marinas y no establece por sí solo un error en reconstrucciones de aire invernal; conservar los valores originales y revisar científicamente las reconstrucciones. Persisten avisos históricos. Auditoría de uso sin vectores duplicados y alias controlados revisados.

Pasaron los archivos de pruebas Python, 49 pruebas Node, TypeScript y compilación. La instantánea final se cotejó celda a celda: 1.081.300 valores en 1.248 archivos. Reproducir con `python scripts/build_common_v38.py --fetch`. Integración y publicación para rol 04, conservando el QC heredado.
