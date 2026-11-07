# CUR-COMMON-23

07-11-2026. Base bb27970 e implementación 95415a0. v23-c339e7f2aa6 añade 34 series y 3.461 observaciones con el esquema y las nueve celdas de v22.

| Fuente | Variables y unidades | Series | Observaciones |
|---|---|---:|---:|
| [Golfo de León](https://doi.pangaea.de/10.1594/PANGAEA.900448) | RI-OH, TEX86 y BIT adimensionales. SST RI-OH y mediana TEX86H BAYSPAR en °C | 10 | 2.125 |
| [U1387 biomarcadores](https://doi.pangaea.de/10.1594/PANGAEA.986649) | UK′37 adimensional y SST Müller 1998 en °C | 6 | 226 |
| [U1387 isótopos](https://doi.pangaea.de/10.1594/PANGAEA.986643) | δ¹⁸O y δ¹³C por especie, ‰ PDB con referencia VPDB declarada | 18 | 1.110 |

Cuatro eventos nuevos y un enlace a U1387C existente. Los sondeos de U1387 pertenecen a un sitio de perforación. Edades LR04 nativas para los isótopos. Probstack, δ¹³C bentónico compuesto y percentiles laterales de BAYSPAR permanecen en las tablas originales. El contrato documenta seis candidatos retenidos, incluido PRGL1_Site pendiente de cotejar con PRGL1-4.

Las 144 agrupaciones tienen membresías distintas. Se aclara la diferencia entre verano declarado (5 series) y verano con meses estivales (9). Se conservan las claves de selección.

Reproducir con `python scripts/build_common_v23.py --fetch`. Pasaron 146 Python, 42 Node, TypeScript y compilación. Auditorías con cero errores. Cotejadas las 3.461 observaciones nuevas con sus originales y las 988.578 del snapshot con la semilla (1.049 archivos).

Integración y publicación para rol 04. Main activa Cloudflare.
