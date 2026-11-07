# CUR-COMMON-22

07-11-2026. Base 561c329 e implementación 684785b. v22-cf1f6241933 incorpora siete series y 4.426 observaciones. Conserva los campos, las nueve celdas por observación y los registros y series de v21.

| Fuente | Variables y unidades | Observaciones |
|---|---|---:|
| [Lago Lungo](https://doi.pangaea.de/10.1594/PANGAEA.885937) | Susceptibilidad magnética volumétrica, 10⁻⁶ SI | 2.809 |
| [D13902, plataforma del Tajo](https://doi.pangaea.de/10.1594/PANGAEA.762035) | UK′37 adimensional, SST en °C, n-alcoholes en µg/g y alquenonas C37:2+C37:3 en ng/g | 308 |
| [161-977A, Alborán](https://doi.pangaea.de/10.1594/PANGAEA.787811) | SST de alquenonas en °C y C37:4 en % | 1.309 |

Lungo y 161-977A enlazados a eventos existentes. D13902 entra con los identificadores y coordenadas de D249. Su posible equivalencia con POS287_26_D13902 sigue abierta. Prevalecen edades ka BP publicadas. En D13902 difieren hasta cinco años de las edades CE donde coexisten. Cuatro candidatos retenidos con razones en el contrato.

La tarjeta anual de SST conserva 22 series de 16 registros y sustituye en el catálogo al subconjunto genérico redundante. La serie del mar Negro de 0–200 m conserva su grupo específico. Las selecciones estivales de distinta resolución se mantienen.

Reproducir con `python scripts/build_common_v22.py --fetch`. Pasaron 146 pruebas Python, 42 Node, TypeScript y compilación. Auditorías con cero errores. Cotejados los 4.426 valores nuevos con sus tablas y el snapshot completo con 985.117 observaciones y 1.036 archivos.

El rol 04 recibe la integración y publicación. Main activa Cloudflare.
