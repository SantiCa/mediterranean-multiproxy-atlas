# CUR-COMMON-21

07-11-2026. Base b2bfff2. Implementación 1fce67f. v21-c80c881825a incorpora siete series y 5.610 observaciones de cinco tablas en tres ubicaciones. Hazar y SW104-ND11 son registros nuevos. Volvi ya existía.

| Fuente | Variable y unidad archivada | Valores |
|---|---|---:|
| [Volvi](https://doi.pangaea.de/10.1594/PANGAEA.982341) | Susceptibilidad magnética MS2E, 10⁻⁶ SI | 3.783 |
| [Hazar](https://doi.pangaea.de/10.1594/PANGAEA.881321) | Susceptibilidad magnética GEOTEK, 10⁻⁶ SI | 339 |
| [Hazar](https://doi.pangaea.de/10.1594/PANGAEA.881322) | δ¹³C y δ¹⁸O de ostrácodos, ‰ PDB con referencia VPDB declarada | 162 |
| [Hazar](https://doi.pangaea.de/10.1594/PANGAEA.881323) | Intensidades de Fe y Ti por micro-XRF, cps | 1.266 |
| [Sicilia](https://doi.pangaea.de/10.1594/PANGAEA.920704) | SST por Mg/Ca de G. ruber blanco, °C, con error estándar absoluto | 60 |

Edades archivadas, contexto por método y metadatos ambientales en campos existentes. AD91-17 y KC-13 ya estaban representados. Componentes ICA pendientes de verificar la atribución individual en el artículo primario. Se conservan los grupos base y los valores de origen. UK′37 reúne 11 series con rótulos equivalentes de unidad adimensional. TIC conserva su identidad frente a CaCO₃ y log-Br/Ti frente al cociente directo.

Reproducir con `python scripts/build_common_v21.py --fetch`. 146 pruebas Python, 41 Node, TypeScript y compilación correctos. Cotejadas las 5.610 celdas nuevas con sus tablas y las 980.691 observaciones del snapshot con la semilla. Auditorías con cero errores. Informes en reports.

Rol 04 recibe v21 en relevo para integrar y publicar. Main activa Cloudflare.
