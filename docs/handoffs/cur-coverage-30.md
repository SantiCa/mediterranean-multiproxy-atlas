# CUR-COVERAGE-30 — lote implementado, publicación pendiente

Codex,30-10-2026. Base relevo0a82a6a; petición: completar ratios inorgánicos,
corrientes, oxigenación y vegetación continental. No se repitió el lote V29.

v6-c8ff5c5a738:138 registros/1.311 series/903.690 valores. Incremento real sobre
v5:10/225/38.097. PANGAEA213 series y NOAA12. Detalle científico y reproducción
en docs/curation/priority_v6.md; contratos/importadores priority_v6 y noaa_priority_v6.

Se verificaron todas las celdas nuevas y la inmutabilidad de v5. 71Python y27Node
locales correctas. Cinco series retenidas por porcentajes fuera de rango o unidad
ambigua;29 fuentes PANGAEA retenidas, y NOAA10418 sin edades por muestra. Noaá43639
añade el registro ligur a432m: aguas intermedias, no oxígeno abisal inferido.

UI: búsqueda por alias Fe/Al/Ti/Ca, filtro≥2por defecto, notas por serie y contextos
que separan fracciones, sumas de polen y matrices. Los recuentos no se convierten
en porcentaje ni tipos de bosque. La tabla completa de originales/exclusiones y
la inclusión manual de cuarentenas permanecen pendientes.

CI de curación recompone v6 tras cambiar v5; snapshot.mjs rechaza padres obsoletos.
No usar un atlas-v6 viejo para ocultar una nueva versiónv5.

Siguiente: compilar y verificar snapshot de v6; desplegar Site privado conservando
identidad y audiencia; registrar recibos, QA y merge --no-ff a main. Después:
ampliar forestales relativos con denominadores documentados (NOAA/Neotoma), buscar
modelos publicados para10418 y ampliar Ti/Ca/Fe/Al/sortable silt a más ubicaciones.
