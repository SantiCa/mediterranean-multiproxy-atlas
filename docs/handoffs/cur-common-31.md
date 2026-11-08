# CUR-COMMON-31

08-11-2026. v31-c3f90e6626c incorpora siete series y 486 observaciones en tres testigos existentes. Conserva campos, unidades y filas de nueve celdas.

- MVSEIS08_TG-2 aporta cuatro asociaciones climáticas planctónicas de la fracción >150 µm, en %. Se mantienen los grupos publicados y se omiten los dos taxones ya incorporados. [PANGAEA.966840](https://doi.pangaea.de/10.1594/PANGAEA.966840)
- GeoB9064-1 aporta temperatura del fondo en °C reconstruida con Mg/Ca bentónico, con el error publicado por fila. Mn/Ca y acumulación ya estaban en el atlas. [PANGAEA.932720](https://doi.pangaea.de/10.1594/PANGAEA.932720)
- MD99-2339 aporta SST de verano en °C y producción exportada en g/m²/a por SIMMAX28. [PANGAEA.857153](https://doi.pangaea.de/10.1594/PANGAEA.857153)

GeoB3004-1 queda fuera del ámbito piloto. Las series de Cibicidoides de 465030 quedan pendientes de cotejar con las tablas isotópicas existentes.

Pasaron 146 pruebas Python, 46 Node, TypeScript, compilación y cotejo íntegro del snapshot de 1.038.072 observaciones. Auditorías con cero errores. Las 22 vistas comprobadas carecen de conjuntos agregados idénticos. La temperatura de fondo queda fuera de SST.

Reproducir con `python scripts/build_common_v31.py --fetch`. Integración y publicación para rol 04.
