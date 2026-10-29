# Respaldo estático si D1 no responde (V27)

- Agente: Claude · 29-10-2026
- Problema: al agotarse el límite diario de D1 (Free), `/api/catalog` da 5xx y la web se queda en «Conectando con el catálogo…».
- Solución: `app/atlas-web/scripts/snapshot.mjs` genera en el build (`deploy-cloudflare.yml`, paso Build) `public/snapshot/` desde la semilla más reciente (`data/processed/atlas-v*.json`, orden -V): `catalog.json` (mismo formato que la API, con `snapshot.groups`) y `obs/<sha1(grupo)[:16]>.json` por grupo de compatibilidad (filas en el orden de la API). Se sirve como assets (no cuenta en el tamaño del Worker; v5: 2,7 MB + 606 archivos, máx. 2,3 MB).
- Cliente (`app/page.tsx`): si `/api/catalog` falla, carga la instantánea; las observaciones se leen del archivo del grupo y se filtran con `seriesMatches` (mismos filtros que la API). Aviso amarillo arriba con la versión. «Mis datos» no funciona sin D1.
- Pruebas: tests Node (14/14), `tsc` sin errores en page.tsx, build vinext OK; Worker local con D1 vacío: `/api/catalog` 500, `/snapshot/catalog.json` 200.
- Nota: la instantánea es la semilla más nueva; puede ser más reciente que la release que sirve D1 (la que aún se carga). Los valores son los de la semilla versionada.
