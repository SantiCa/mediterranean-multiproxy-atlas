# CUR-FOUR-COVERAGE

Codex, 4 de noviembre de 2026. Base `f9a9d0f`, cierre del lote anterior. v7 incorpora 13 registros, 38 series y 20.756 valores. Total 151 registros, 1.349 series y 924.446 valores. v6 se conserva íntegra.

| Proxy | Ubicaciones antes → después | Series nuevas |
| --- | --- | ---: |
| Ti/Ca sin logaritmo | 8 → 14 | 7 |
| Fe/Al, todas las etiquetas de unidad | 3 → 6 | 3 |
| Sortable silt, media en µm | 3 → 4 | 1 |
| Sortable silt, fracción en % | 3 → 4 | 1 |
| Polen forestal continental, porcentajes seleccionados | 2 → 5 | 26 |

Ti/Ca de PANGAEA.941818 y Fe/Al de PANGAEA.693917, .896929 y .896930. Las dos series del Adriático con etiqueta nativa `%` se mantienen en grupo propio. MP37PC queda pendiente por `Fe/A`. U1389A añade dos series Zenodo 8163513. McCave (2023), §3.1, resuelve la etiqueta `mm` como µm sin alterar números. Edades ajustadas orbitalmente con participación del mismo proxy. Ohrid DEEP, Tenaghi Philippon y Füramoos amplían el polen. Se conservan sumas y taxones publicados, y se cuenta una sola ubicación para Ohrid DEEP.

Reproducir con `python -m pip install openpyxl==3.1.5`, `python scripts/importers/curate_four_v7.py --fetch` y `python scripts/build_quantitative_v7.py`. Contratos en `scripts/importers/four_v7_sources.json`. La compilación rechaza un padre v6 distinto. Pasaron 74 pruebas Python y 27 Node, incluidos cotejo celda a celda y agrupación espacial a cuatro decimales.

Pendiente inmediato: validar el snapshot, compilar y publicar. Después, verificar cronologías en la misma escala de profundidad para CADKS24, MD99-2337, U1386 y U1390. Revisar denominadores de Neotoma antes de calcular porcentajes.
