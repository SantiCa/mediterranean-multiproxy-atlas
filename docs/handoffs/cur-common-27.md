# CUR-COMMON-27

07-11-2026. Base d191dfb. v27-cdeefdc51f6 incorpora dos sondeos, nueve series y 1.233 observaciones. Conserva el esquema y las nueve celdas por observación.

| Fuente | Variables y unidades | Observaciones |
|---|---|---:|
| [M40/4_SL87](https://doi.pangaea.de/10.1594/PANGAEA.69826) | δ¹⁸O de G. ruber blanco en ‰ PDB | 233 |
| [160-969E](https://doi.pangaea.de/10.1594/PANGAEA.79182) | δ¹⁸O de G. ruber blanco en ‰ PDB | 96 |
| [GT90-3](https://doi.pangaea.de/10.1594/PANGAEA.857573) | δ¹⁸O de G. ruber en ‰ PDB | 560 |
| [MD99-2339](https://doi.pangaea.de/10.1594/PANGAEA.465031) | δ¹⁸O y δ¹³C de Uvigerina en ‰ PDB | 188 |
| [POPEI_VC2B](https://doi.pangaea.de/10.1594/PANGAEA.882266) | UK′37 adimensional y SST en °C | 156 |

969E y 969D representan el mismo sitio de perforación. Se mantienen los taxones originales y el contexto propio de SST de POPEI_VC2B. Se retuvo 930775 por discrepancia de identificación y 884646 por enlace sitio-sondeo y columnas promediadas pendientes.

Reproducir con `python scripts/build_common_v27.py --fetch`. Pasaron 146 pruebas Python, 44 Node, TypeScript y compilación. Las auditorías dieron cero errores. Cotejadas las observaciones nuevas con los originales y el snapshot completo de 1.027.294 valores en 1.081 archivos. Las 22 vistas verificadas presentan conjuntos de series agregadas distintos.

Integración y publicación para rol 04.
