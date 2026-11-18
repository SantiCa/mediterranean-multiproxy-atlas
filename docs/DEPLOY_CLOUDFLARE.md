# Visor público de Cloudflare

El Worker `med` conserva la URL **https://med.proxyatlas.workers.dev**. La configuración `app/atlas-web/wrangler.public.json` publica solo HTML, JavaScript de navegador, estilos, mapas base locales y la instantánea del catálogo. Las teselas de terceros se solicitan desde el navegador. Los mapas, series y exportaciones se calculan en el cliente.

El paquete público carece de código de servidor, rutas de API y conexiones a bases de datos. Mis datos, Añadir fuente y el piloto están reservados al Site privado. La ruta de DOI en Sites exige identidad autenticada y comprueba el origen de las escrituras. El despliegue público no aplica migraciones ni transfiere registros o sesiones; la base histórica `medatlas` se conserva. Si hubiera datos en esa base que deban trasladarse a Sites, inventariarlos con el propietario antes de cualquier importación.

## Construir y comprobar

Desde `app/atlas-web`, con las dependencias instaladas:

```powershell
node scripts/build-public-viewer.mjs ../../data/processed/atlas-v37.json
npx --no-install wrangler deploy --dry-run --config wrangler.public.json
npx --no-install wrangler dev --local --config wrangler.public.json
```

El empaquetado coteja las celdas con la semilla curada, comprueba el inventario de archivos permitido y aplica los límites de activos de Workers Free. En la previsualización, comprobar que abren Sondeos, Proxies y series y Datos curados, que funcionan las exportaciones y que las rutas privadas devuelven 404.

## Publicar

`.github/workflows/deploy-cloudflare.yml` ejecuta las pruebas, genera el paquete con la última semilla seguida en `main` y publica en el Worker existente. Solo el paso de publicación recibe los secretos de Cloudflare. Puede lanzarse manualmente desde `main`. Tras publicar coteja el catálogo servido con el local y comprueba que la API DOI anterior ya no responde.

- Conservar la cuenta Cloudflare existente y el subdominio `proxyatlas`. El workflow ya no crea ni renombra subdominios.
- El token necesita permiso para desplegar el Worker. Ya no requiere permiso de edición de D1. Revocar cualquier token expuesto y provisionar el reemplazo desde los paneles, sin copiarlo a archivos, chats ni logs.
- Mantener Workers Free. La publicación no cambia la suscripción. Los archivos servidos directamente se rigen por la [facturación de activos estáticos de Cloudflare](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/).
- Verificar el Site privado por separado. Su integración, permisos y piloto quedan a cargo del rol 04.
