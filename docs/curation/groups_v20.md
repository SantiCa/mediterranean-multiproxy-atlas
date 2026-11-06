# Proxies comunes y alias de consulta — v20

06-11-2026. Padre v19-c4262530e6b íntegro; resultado v20-cf635885fac.
260 registros, 2.019 series, 975.081 valores y 1.020 grupos base.
Se añaden tres series y 98 valores a BEN14-P4, ya existente; no aumenta el número de ubicaciones independientes. Se conservan exactamente los campos y las nueve celdas por observación.

## Admisión científica

| Fuente y columna | Nombre / interpretación | Unidad nativa | Valores |
|---|---|---|---:|
| [PANGAEA.896609](https://doi.org/10.1594/PANGAEA.896609), C org/sed | Carbono orgánico por masa de sedimento; aporte, producción y preservación | mg/g | 33 |
| Misma fuente, N/sed | Nitrógeno por masa de sedimento; aporte y preservación de nutrientes | mg/g | 33 |
| Misma fuente, P/sed | Fósforo **lábil**, extracción Olsen con bicarbonato; nutrientes/eutrofización | µg/g | 32 |

Datos CHN para C/N, fracción Olsen para P, edades archivadas en ka BP. Una celda P ausente sigue ausente; no se convierte en cero. P lábil conserva contexto explícito para no agruparlo con P total. Concentraciones aisladas no se convierten en tasas de productividad ni en C/N. La fuente CC-BY-4.0 es suplemento de [Perrette et al., 2019](https://doi.org/10.1016/j.ancene.2018.11.005). Las interpretaciones y unidades se incorporan en campos existentes, incluidos qc_notes y comparison_parameter_name.

[PANGAEA.667403](https://doi.org/10.1594/PANGAEA.667403): el original contiene TOC −1,710 % a 12,7679 ka BP y 1,010 m. La regla preexistente retiene la serie completa de 135 valores por porcentaje fuera de rango; no se recorta ni corrige el original.

[PANGAEA.993109](https://doi.org/10.1594/PANGAEA.993109): retenida. Columnas calendáricas rotuladas ka BP contienen medianas 11167–17706, incompatibles con el intervalo 11–17 ka del resumen primario. No se aplica silenciosamente un factor 1000 ni calibración radiocarbónica. Contrato y auditoría preservan la discrepancia.

## Revisión de agrupaciones

- TOC, total organic carbon, Carbon, organic, total y C org/sed comparten nombre de consulta «Carbono orgánico total (TOC)». Un único agregado de TOC en % reúne 24 registros, 31 series y 3.073 valores, sin el subconjunto duplicado por nombre nativo. mg/g permanece separado de %.
- Ti/Ca y Titanium/Calcium ratio, además de otros cocientes elementales reconocidos (Fe/Ca, Ti/Al, Si/Ti, etc.), usan símbolos comunes. CaCO3 y Calcium carbonate también comparten nombre.
- Las facetas de variable y la búsqueda reconocen esos alias. Los grupos base, IDs, unidades, métodos, fuentes y observaciones no se reescriben. Las tarjetas de método siguen siendo opciones válidas distintas de los agregados.
- Cociente directo, ln, log y log10 siguen separados, así como base molar, másica, escáner e instrumentación, matriz y contextos explícitos. «Base de la razón no declarada» se etiqueta como tal; el nombre común no demuestra comparabilidad científica. TIC no equivale a CaCO3; isótopos, flujos, TOC/TN y fracciones distintas tampoco equivalen a TOC.

## Reproducción y comprobaciones

`python scripts/build_common_v20.py --fetch` restaura los originales fijados por hash y reconstruye la semilla; requiere el padre v19 seguido por Git. `node scripts/audit_group_aliases.mjs` comprueba los alias sobre el catálogo real y produce reports/group_aliases_v20.json (38 combinaciones de nombre/unidad/contexto). El constructor v19 sigue reproduciendo idénticos bytes del padre.

146 pruebas Python en procesos por archivo, sin omisiones; 39 Node; TypeScript y compilación correctos. Auditorías científica y de uso: cero errores; avisos heredados sin cambios. Snapshot: 975.081 valores comparados celda a celda, 1.020 grupos/1.022 archivos. No se certifica auditoría científica exhaustiva, equivalencia entre métodos ni calidad de interpolación. Sin QA visual adicional; los cambios de catálogo se verifican con pruebas y auditoría real de membresías.

Publicación e integración en main reservadas al rol 04: el workflow deploy-cloudflare.yml publica automáticamente al recibir estos cambios en main. No se activa ese flujo desde este lote.
