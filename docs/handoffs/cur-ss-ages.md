# CUR-SS-AGES

Codex, 5 de noviembre de 2026. Base `0a9bdad`. Release v8-c131d231e50 con 154 registros, 1.352 series y 924.752 valores. v7 se conserva íntegra.

| Registro | Valores originales | Con edad interpolada | Base cronológica |
| --- | ---: | ---: | --- |
| U1386 | 33 | 30 | Moal-Darrigade (2022), tesis, tabla 3-5, mcd |
| U1390 | 187 | 186 | van Dijk et al. (2018), PANGAEA.884620, mcd |
| CADKS24 | 86 | 32 | Hassan (2014), cap. III, tabla 2, profundidad en sedimento |

El atlas interpola linealmente y conserva 58 valores fuera de los controles con edad nula. Para CADKS24 se usa el punto medio de los intervalos datados de 214–215, 375–378 y 525–527 cm. No se recalibran las edades ni se propaga incertidumbre. Para U1386 se usa el modelo AMS/LR04 de las muestras y no el modelo alternativo de Br de PANGAEA.870577. Para U1390 se usa el compuesto A/B/C. Las edades publicadas de PANGAEA se conservan con su precisión de archivo. MD99-2337 queda pendiente: tesis y artículo describen bioeventos, pero no se verificó una tabla numérica edad–profundidad.

Contratos, DOI, localizadores y hashes en `scripts/importers/ss_v8_sources.json`. Reproducir con `python -m pip install openpyxl==3.1.5` y `python scripts/build_sortable_silt_v8.py --fetch`. Los valores y localizadores se contrastaron celda a celda. 76 pruebas Python y 28 Node correctas. El contador y la superficie comparten una ubicación por par de coordenadas a cuatro decimales. La suma de muestras conserva todas las series.

Pendiente inmediato: validar snapshot y publicar.
