# Handoff — DATOS-ESTÁTICOS (Claude, 29-10-2026, V28)

- Petición de Santiago (22:47): servir lo público sin base de datos para no agotar los límites diarios de D1.
- Hecho: el cliente lee `/snapshot/catalog.json`, `/snapshot/obs/*.json` y `/snapshot/inventory.json` (pestaña Sondeos, consultas en `lib/inventory-local.mjs` con la semántica del SQL anterior). Worker 17 MB → 1,1 MB. Despliegue: instantánea + comprobación celda a celda + comprobación de la URL pública; sin cron ni cargas D1.
- «Mis datos»: la subida envía los metadatos del grupo desde el catálogo estático; el servidor exige coherencia con la clave del grupo (proxy, grupo, unidad) y prohíbe grupos `private_`.
- Pruebas: 24 Node (incl. inventario local), tsc, build, e2e local (wrangler dev + Playwright): catálogo, agrupación SST, Mis datos, Sondeos (5.846 entradas, mapa y lista).
- Pendiente: las tablas públicas antiguas de D1 (atlas_records/series/observations/inventory) pueden borrarse para liberar espacio; no es urgente.
