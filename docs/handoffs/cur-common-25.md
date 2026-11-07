# CUR-COMMON-25

07-11-2026. Base 78bd747 e implementación 3f0f6df. v25-c4c7fe7c54e añade 11 series y 21.457 observaciones a tres eventos existentes, con el mismo esquema y las nueve celdas originales por observación.

| Archivo | Variables y unidades | Observaciones |
|---|---|---:|
| [Prespa, Co1215](https://doi.pangaea.de/10.1594/PANGAEA.804611) | Susceptibilidad volumétrica GEOTEK, 10⁻⁶ SI | 17.363 |
| [Ohrid, ICDP5045-1](https://doi.pangaea.de/10.1594/PANGAEA.908113) | Susceptibilidad en muestras discretas, 10⁻⁶ SI | 1.352 |
| [Baleares, MD99-2343](https://doi.pangaea.de/10.1594/PANGAEA.759537) | δ¹⁸O y δ¹³C por especie en ‰ PDB, cocientes Si/Al, Ti/Al, Ca/Al y K/Al adimensionales y dos abundancias relativas en % | 2.742 |

Se conservan edades y profundidades publicadas. Los 394 huecos de susceptibilidad de Prespa permanecen en el original. Los cocientes de Baleares conservan contexto propio por base analítica sin declarar en la tabla. Mg/Ca de Alborán queda pendiente de revisar calibración y hábitat por especie.

Ca/Al y Calcium/Aluminium ratio comparten nombre de consulta. CaCO₃ exige la magnitud canónica y un contexto compatible, con sus 20 series elegibles. Se cotejaron membresías agregadas en 22 vistas, incluido el catálogo completo, sin conjuntos idénticos.

Reproducir con `python scripts/build_common_v25.py --fetch`. Pasaron 146 pruebas Python, 43 Node, TypeScript y compilación. Auditorías con cero errores. Cotejados los 21.457 valores nuevos con sus originales y el snapshot completo de 1.024.357 observaciones y 1.064 archivos.

Integración y publicación para rol 04. Main activa Cloudflare.
