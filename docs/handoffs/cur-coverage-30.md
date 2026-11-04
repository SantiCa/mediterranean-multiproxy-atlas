# CUR-COVERAGE-30 — cerrado y publicado

Codex, 30-10-2026. Base relevo 0a82a6a; petición: completar ratios inorgánicos,
corrientes, oxigenación y vegetación continental. No se repitió el lote V29.

v6-c8ff5c5a738:138 registros/1.311 series/903.690 valores. Incremento real sobre
v5:10/225/38.097. PANGAEA 213 series y NOAA 12. Detalle científico y reproducción
en docs/curation/priority_v6.md; contratos/importadores priority_v6 y noaa_priority_v6.

Se verificaron todas las celdas nuevas y la inmutabilidad de v5. 71 pruebas Python y 27 pruebas Node
locales correctas. Cinco series retenidas por porcentajes fuera de rango o unidad
ambigua;29 fuentes PANGAEA retenidas, y NOAA 10418 sin edades por muestra. NOAA 43639
añade el registro ligur a 432 m: aguas intermedias, no oxígeno abisal inferido.

UI: búsqueda por alias Fe/Al/Ti/Ca, filtro ≥2 por defecto, notas por serie y contextos
que separan fracciones, sumas de polen y matrices. Los recuentos no se convierten
en porcentaje ni tipos de bosque. La tabla completa de originales/exclusiones y
la inclusión manual de cuarentenas permanecen pendientes.

CI de curación recompone v6 tras cambiar v5; snapshot.mjs rechaza padres obsoletos.
No usar un atlas-v6 viejo para ocultar una nueva versión v5.

Publicado en Site privado; fuente 525ef3fc345122ebcbb55570b69035b9c5608308,
despliegue appgdep_6ae470954d0c8191a2574ae50de66207 succeeded. 964 archivos estáticos remotos
idénticos al snapshot contrastado celda a celda. tsc/build y QA local correctos;
QA visual remota requiere iniciar sesión ChatGPT. Recibos priority_v6_sites_*.json.
Siguiente:
ampliar forestales relativos con denominadores documentados (NOAA/Neotoma), buscar
modelos publicados para 10418 y ampliar Ti/Ca/Fe/Al/sortable silt a más ubicaciones.
