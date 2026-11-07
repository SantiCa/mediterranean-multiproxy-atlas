# CUR-COMMON-28

07-11-2026. Base de datos v27-cdeefdc51f6. Implementación d764eb8. v28-c5fa6332d0f añade dos ubicaciones nuevas, 10 series y 1.135 observaciones. Conserva el esquema y las nueve celdas por observación.

| Fuente | Variables y unidades | Observaciones |
|---|---|---:|
| [161-974C, Tirreno](https://doi.pangaea.de/10.1594/PANGAEA.726198) | CaCO₃ y TOC en %, acumulación de TOC en g/cm²/ka, δ¹³C en ‰ PDB, δ¹⁵N en ‰ aire y C/N atómico | 712 |
| [4WS00-4P, lago de Lucerna](https://doi.pangaea.de/10.1594/PANGAEA.881553) | TEX86 y BIT adimensionales en contexto lacustre | 389 |
| [M72/5_640-1, mar Negro](https://doi.pangaea.de/10.1594/PANGAEA.854726) | UK′37 adimensional y SST de principios de verano en °C | 34 |

En 161-974C, una columna rotulada como acumulación de TOC coincide con sedimentación por densidad seca en 122 filas. Se admite únicamente la columna explícita coherente con la fracción de TOC. El cálculo se empleó para identificar la columna y los valores incorporados proceden del original.

Las 22 vistas revisadas tienen conjuntos de series agregadas distintos. TEX86 y BIT lacustres conservan su contexto y la SST del mar Negro figura en la selección estival.

Reproducir con `python scripts/build_common_v28.py --fetch`. Pasaron 146 pruebas Python, 44 Node, TypeScript y compilación. Auditorías con cero errores. Cotejados los originales y el snapshot completo de 1.028.429 valores en 1.090 archivos. Integración y publicación para rol 04.
