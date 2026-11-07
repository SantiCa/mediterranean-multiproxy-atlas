# CUR-COMMON-24

07-11-2026. Base 5ee5e82 e implementación 9697739. v24-c17c40ccf3b añade siete series y 14.322 observaciones a PRGL1-4 y MD99-2348, ambos existentes. Conserva los campos y las nueve celdas por observación.

| Variable | Unidad | Observaciones |
|---|---|---:|
| Calcio XRF de PRGL1-4 | cts | 8.202 |
| Arena fina 125–250 µm de la fracción total | % | 2.382 |
| Razón limo/arcilla de la fracción descarbonatada | Adimensional | 1.959 |
| δ¹⁸O de Globigerina bulloides | ‰ PDB | 1.779 |

Las siete tablas usan las edades calendáricas archivadas. La cronología publicada comparte el marco estratigráfico de ambos archivos. El δ¹⁸O participa en la sincronización. Dos tablas de geoquímica orgánica permanecen retenidas por la identificación cruzada de PRGL_1-4 y por tratamientos alternativos en una de ellas. [Colección original de Frigola](https://doi.pangaea.de/10.1594/PANGAEA.911440)

Se compararon los conjuntos de IDs de serie en el catálogo completo y en 21 vistas filtradas por ámbito, proveedor o cronología. Los 144 agregados del catálogo completo tienen miembros distintos. Se comprobó la separación entre Ca XRF y CaCO₃ y entre las fracciones granulométricas.

Reproducir con `python scripts/build_common_v24.py --fetch`. Pasaron 146 pruebas Python, 42 Node, TypeScript y compilación. Auditorías con cero errores. Cotejados los 14.322 valores nuevos con sus originales y el snapshot completo de 1.002.900 observaciones y 1.053 archivos.

Integración y publicación para rol 04. Main activa Cloudflare.
