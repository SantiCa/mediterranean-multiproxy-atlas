# SITES-V28 — cerrado

Codex, 29-10-2026. Solicitud: publicar main V28 en el Site ChatGPT existente.
Base científica/web: main `dfdb4191452d305b9ec8209175321f6b52de3c04` (V28.1).
Los 158 archivos de la fuente Sites coinciden byte a byte con los blobs de main;
no se integró el antiguo checkpoint de temperatura.

Checkout: `../sites/medatlas-v28`. Se preservó medatlas-v1. Exportación selectiva
de archivos seguidos; eliminadas las cuatro rutas públicas y data/seed.json
obsoletos. Identidad, audiencia privada y binding DB conservados.

Antes del build: snapshot.mjs con atlas-v5.json (última versión numérica) e
inventory.json, seguido de check-snapshot.mjs. Release v5-c25cc8a2394:
102 registros / 815 series / 606 grupos / 241.826 valores; 608 archivos estáticos.
24 pruebas Node, tsc --noEmit y build correctos. Migración 0004 incluida;
Sites gestiona las migraciones del despliegue. No se consultó el esquema D1
de producción de forma independiente.

Fuente Sites `743a94ba4509999d409ce07a07519fe90e9abebe`.
Despliegue `appgdep_6ae3c6fb23d08191a63ccb7ba6658dd6`, succeeded.
URL: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site

Verificación remota: 608 archivos idénticos por SHA256 a la instantánea comprobada
celda a celda. /api/catalog, observations, bootstrap e inventory devuelven404.
QA visual: inventario5846 entradas, mapa, serie temporal y Mis datos.
OWNER_PASSWORD ausente; /api/private/session configured=false. No se creó secreto.

Recibos: reports/sites_v28_preflight.json, sites_v28_deployment.json y
sites_v28_production_check.json. Validador reutilizable: scripts/validate_static_site.py;
credencial oficial por stdin oculto solo al origen exacto, nunca persistida.
Siguiente propuesta: continuar curado desde su handoff; regenerar snapshot para
cada futura publicación Sites.
