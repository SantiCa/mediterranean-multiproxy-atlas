# CUR-COMMON-26

07-11-2026. Base fff9c43 e implementación bd4cbef. v26-cc3b334b8f6 añade dos testigos del Nilo, 13 series y 1.704 observaciones. Conserva el esquema y las nueve celdas por observación.

| Fuente | Variables y unidades | Observaciones |
|---|---|---:|
| [161-977A](https://doi.pangaea.de/10.1594/PANGAEA.819805) | TEX86 y BIT adimensionales. Temperatura TEX86H Kim 2010 en °C | 597 |
| [161-975B](https://doi.pangaea.de/10.1594/PANGAEA.693919) | Ti/Al y K/Al adimensionales, calcita XRD en %, Ba en exceso en mg/kg y δ¹⁸O y δ¹³C de G. bulloides en ‰ PDB | 362 |
| [MS21PC](https://doi.pangaea.de/10.1594/PANGAEA.875737) | Ti/Al adimensional, TOC en % y δ¹³C del TOC en ‰ PDB | 514 |
| [PS009PC](https://doi.pangaea.de/10.1594/PANGAEA.875736) | δ¹³C del TOC en ‰ PDB | 231 |

La calibración TEX86H conserva contexto propio. El artículo discute un posible sesgo estival pese al rótulo anual de la tabla. Zr/Al y Ba/Al de 975B quedan pendientes por discrepancia de escala. El bario en exceso se incorpora como concentración publicada.

Se unifican los nombres de δ¹³C del TOC en una agrupación de cuatro series. Calcita XRD conserva su grupo. Las 22 vistas comprobadas tienen conjuntos de series agregadas distintos.

Reproducir con `python scripts/build_common_v26.py --fetch`. Pasaron 146 Python, 44 Node, TypeScript y compilación. Auditorías con cero errores. Cotejadas 1.704 observaciones nuevas y 1.026.061 del snapshot en 1.074 archivos.

Integración y publicación para rol 04. Main activa Cloudflare.
