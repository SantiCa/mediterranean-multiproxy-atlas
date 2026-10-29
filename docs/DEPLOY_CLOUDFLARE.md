# Despliegue propio en Cloudflare

Alojamiento independiente de ChatGPT Sites. La web (`app/atlas-web`) ya es un Cloudflare Worker con D1; aquí se despliega en la cuenta Cloudflare de Santiago mediante `.github/workflows/deploy-cloudflare.yml`.

## Cómo funciona

- Cada fusión en `main` que toque `app/atlas-web/` despliega sola. También se puede lanzar a mano: pestaña **Actions → Deploy web to Cloudflare → Run workflow**. Ningún agente despliega a mano.
- El flujo crea (la primera vez) o reutiliza la base D1 `medatlas`, aplica las migraciones versionadas `app/atlas-web/drizzle/*.sql`, compila con `CF_WORKER_NAME`/`CF_D1_DATABASE_*` (sin ellas el build es idéntico al de Sites) y despliega el Worker `med` en **https://med.proxyatlas.workers.dev** (subdominio de cuenta `proxyatlas`, registrado o renombrado por el flujo).
- Después carga semilla e inventario mediante los endpoints idempotentes `/api/bootstrap` y `/api/inventory`. Repetir la ejecución reanuda sin reescribir.
- Sin los secretos, el flujo termina con un aviso y no falla.

## Configuración inicial (Santiago, una sola vez)

1. Crear cuenta gratuita en <https://dash.cloudflare.com/sign-up> y verificar el email.
2. Abrir **Workers & Pages** una vez y aceptar el subdominio `*.workers.dev` que propone.
3. Copiar el **Account ID** (columna derecha de la página de inicio de la cuenta o de Workers & Pages).
4. **My Profile → API Tokens → Create Token**, plantilla **Edit Cloudflare Workers**. Añadir el permiso **Account · D1 · Edit**. Account Resources: tu cuenta. Crear y copiar el token (solo se muestra una vez).
5. En GitHub, repositorio → **Settings → Secrets and variables → Actions → New repository secret**:
   - `CLOUDFLARE_API_TOKEN` = token del paso 4
   - `CLOUDFLARE_ACCOUNT_ID` = ID del paso 3
6. **Actions → Deploy web to Cloudflare → Run workflow** (rama `main`). La URL aparece en el resumen de la ejecución.

## Límites y decisiones abiertas

- Visibilidad: la URL `workers.dev` es **pública** por defecto (Sites era privado). Datos PANGAEA CC-BY y NOAA WDS; aun así, decidir antes de difundir. Para restringirla a un email: Cloudflare Zero Trust → Access → aplicación sobre esa URL.
- Plan gratuito: las consultas D1 fallan al superar el límite diario de filas escritas o leídas hasta medianoche UTC (desde 01-09-2026). La primera carga escribe ~81.500 observaciones y ~20.100 filas de inventario, más índices: puede necesitar dos ejecuciones en días distintos.
- Tamaño del Worker: 2,26 MB comprimido (límite gratuito 3 MB). Semilla e inventario van dentro del bundle; si crecen, moverlos a R2 o a assets estáticos.
- ChatGPT Sites sigue activo hasta comprobar la nueva URL con `python scripts/validate_quantitative_api.py --url <URL>`.

## Verificación local realizada (29-10-2026)

Build con variables propias, `wrangler deploy --dry-run` correcto, migraciones 0000–0003 sobre D1 local, carga completa con el mismo script del flujo y `validate_quantitative_api.py`: 29 registros, 89 series, 81.339 valores comparados celda a celda, 62 grupos. Despliegue remoto no verificado aún (faltan secretos).

## Carga de releases (V18, 29-10-2026)

La semilla ya no va en el Worker (v5 supera los 3 MB gzip del plan Free). El Worker solo empaqueta `app/atlas-web/data/release.json` (manifiesto: versiones, IDs de series y registros) y sirve la **última release completa** en D1. El flujo escribe D1 con `scripts/d1_release.py` (`plan` → lotes SQL de 5.000 valores, `finalize` → metadatos y fila de release solo con recuentos completos). Si se alcanza el límite diario (100.000 filas escritas), avisa y se reanuda con la ejecución diaria (cron 00:17 UTC). Nueva release: añadir su `--seed` en el flujo y regenerar el manifiesto con `python scripts/d1_release.py manifest --seed … --out app/atlas-web/data/release.json`.

## Datos públicos estáticos (V28, 29-10-2026)

Sustituye la «Carga de releases» anterior. Los datos públicos ya no están en D1: en cada despliegue `app/atlas-web/scripts/snapshot.mjs` genera `public/snapshot/` desde la semilla más reciente (`catalog.json`, `obs/<grupo>.json`, `inventory.json`), `scripts/check-snapshot.mjs` lo compara celda a celda con la semilla y se sirve como archivos estáticos (sin lecturas ni escrituras de base de datos, sin límites diarios). El navegador filtra igual que la antigua API (`seriesMatches`; inventario en `lib/inventory-local.mjs`). D1 queda solo para «Mis datos» (sesiones y datos privados) y la cola de DOI («Añadir fuente»). Rutas `/api/catalog`, `/api/observations`, `/api/bootstrap`, `/api/inventory` y `scripts/d1_release.py` eliminadas. Una nueva versión curada aparece en cuanto se fusiona en `main`. Límites de assets (plan Free): ≤ 25 MiB por archivo y ≤ 20 000 archivos; hoy 2,8 MB de catálogo y 608 archivos. Al superar ~3.000 series: dividir el catálogo (índice ligero) y pasar a archivos por serie.
