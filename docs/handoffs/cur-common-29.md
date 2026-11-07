# CUR-COMMON-29

07-11-2026. Base a160ff2. v29-c45997d0668 incorpora tres ubicaciones nuevas del Adriático, 70 series y 3.938 observaciones. Conserva el esquema y las nueve celdas por observación.

| Sondeo | Muestras | Series | Observaciones |
|---|---:|---:|---:|
| [AMC99-1](https://doi.pangaea.de/10.1594/PANGAEA.875744) | 42 | 20 | 840 |
| [SA03-1](https://doi.pangaea.de/10.1594/PANGAEA.875783) | 57 | 25 | 1.425 |
| [ST04-1](https://doi.pangaea.de/10.1594/PANGAEA.875784) | 67 | 25 | 1.673 |

Recuentos taxonómicos publicados de la fracción >106 µm en # y concentraciones totales publicadas en #/g. Se conservan edades calibradas de OxCal, 2.110 ceros y nombres taxonómicos. Dos celdas vacías quedaron fuera. Los totales de recuento y masas secas permanecen en los originales. Las tablas bentónicas requieren revisión de taxones y totales.

Las concentraciones comparten un grupo base. Los recuentos por muestra conservan su contexto por tabla. Las 22 vistas comprobadas presentan conjuntos agregados distintos.

Reproducir con `python scripts/build_common_v29.py --fetch`. Pasaron 146 pruebas Python, 46 Node, TypeScript y compilación en checkout aislado. Auditorías con cero errores. Cotejados los originales y el snapshot de 1.032.367 valores en 1.158 archivos.

Integración y publicación para rol 04. Usar el QC del relevo y regenerar el snapshot en el checkout de publicación.
