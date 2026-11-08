# CUR-COMMON-32

08-11-2026. v32-c9a4ef57496 añade dos ubicaciones, nueve series y 30.323 observaciones con el esquema original.

- Fucino F1/F3 aporta 9.914 valores de TN, TIC, TOC, TOC/TN atómico y señales XRF de Ca, Ti y Zr normalizadas por dispersión coherente. F1 y F3 forman un solo archivo compuesto. Se mantienen la profundidad compuesta de Mannella 2019 y la edad puntual Bacon. Los límites asimétricos quedan en el original. [PANGAEA.906204](https://doi.pangaea.de/10.1594/PANGAEA.906204)
- Anterne ANT07 aporta 20.409 valores de frecuencia de crecidas y sedimentación continua. La ventana móvil de 101 años produce valores solapados. [PANGAEA.958979](https://doi.pangaea.de/10.1594/PANGAEA.958979)

Quedan pendientes Dojran por condiciones de reutilización y Zoñar por cotejar la identidad de su evento con el registro existente.

Se cotejaron todas las observaciones nuevas y el snapshot completo de 1.068.395 valores. Pasaron 146 Python, 46 Node, TypeScript y compilación. Las auditorías dieron cero errores. Se revisaron 22 vistas sin conjuntos agregados idénticos. Las señales XRF normalizadas conservan su contexto.

Reproducir con `python scripts/build_common_v32.py --fetch`. Integración y publicación para rol 04.
