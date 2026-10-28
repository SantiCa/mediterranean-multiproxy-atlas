# Web v1: implementación, reproducción y límites

Fecha de corte: 28-10-2026. Release de datos `atlas-v1-2026-10-28-r2`.
URL: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (acceso privado del propietario).

## Qué está implementado

13 registros, 22 series, 14.751 valores finitos. PANGAEA: 10 registros, 16 series, 2.881 valores. NOAA WDS: Soreq, Peqiin y Sofular, 6 series, 11.870 valores. Hay 40 valores sin edad (38 LC21 y 2 Peqiin), conservados en almacenamiento y excluidos del mapa por edad. Los registros continentales actuales son espeleotemas; aún no hay series lacustres o polínicas normalizadas. No se afirma cobertura de toda la cuenca.

El mapa permite elegir variable, ámbito, edad de muestra, año del artículo, resumen media/mediana, mínimo de muestras y referencia de normalización. Círculos observados, superficie IDW opcional, serie temporal de valores originales y catálogo trazable. Capas batimetría Esri Ocean, topografía OpenTopoMap, imagen Esri y político OpenStreetMap. Se conserva atribución; son servicios remotos, sin garantía local de disponibilidad ni descarga masiva. No suministran al atlas valores numéricos de batimetría. OpenStreetMap se usa según https://operations.osmfoundation.org/policies/tiles/; el navegador conserva su caché y Referer normales. No se exportan ni se almacenan sus teselas.

CSV incluye selección, valores numéricos y celdas originales, localizadores, incertidumbre disponible, profundidad nativa, DOI, año, licencia y hash. El SVG del mapa contiene costa y datos vectoriales en proyección equirectangular (distinta de Web Mercator en pantalla), leyenda y metadatos de selección. No copia teselas. La serie SVG conserva puntos y texto editables en Illustrator.

## Almacenamiento y arquitectura

- `app/atlas-web/`: copia versionada del código web desplegado, React/TypeScript sobre Vinext/Worker. El checkout operativo de Sites se conserva separado para no introducir repositorios Git anidados.
- `db/schema.ts`, `drizzle/`: esquema Drizzle y migraciones D1. Las copias SQL en `migrations/` permiten SQLite local desde Python.
- Cinco tablas: registros, series, observaciones, releases y candidatos. Metadatos nativos/ampliados se conservan en JSON junto a claves/variables/coordenadas indexables; las observaciones tienen índice por serie/edad.
- `data/processed/atlas-v1.json`: semilla canónica reproducible; `data/seed.json` es su copia para despliegue. No editar sus valores directamente.
- `GET /api/catalog`: catálogo desde D1. `POST /api/bootstrap`: importación idempotente de la semilla versionada, lotes acotados; no ejecuta DDL. Los cambios de esquema son migraciones.
- `GET/POST /api/candidates`: cola persistente. Un DOI se contrasta contra Crossref o DataCite; esto verifica identidad bibliográfica, no extrae ni valida automáticamente valores. Los datos numéricos se incorporan tras curación por script/release.
- No hay claves privadas en el cliente. D1 se vincula al Worker; el control de acceso de Sites mantiene privado el piloto. SQLite local facilita migrar a PostgreSQL/Supabase si el volumen o la concurrencia lo requieren.

El modelo operativo v1 es una proyección pequeña del modelo científico completo propuesto. No implementa todavía regiones versionadas, cronologías alternativas relacionales, taxonomías ni permisos multiusuario. Las coordenadas no se restringen a la cuenca. Nuevas regiones no requieren tablas regionales, aunque el panel y sus límites iniciales son mediterráneos. El catálogo completo se carga en cliente para esta semilla; antes de crecer hay que añadir consultas paginadas/por viewport, agregación en servidor, presupuesto de consultas, importación administrativa y una caché de resultados. IDW con cruce del antimeridiano no está soportado.

## Contrato científico de los mapas

Se selecciona una misma variable y grupo de compatibilidad; no se promedian SST, δ18O y abundancias. Las seis series SST de alquenonas comparten la calibración Müller et al. (1998); Mg/Ca y otras calibraciones permanecen separados. La unidad común no basta para probar equivalencia ambiental.

Por serie: z = (x − μ_ref) / σ_ref poblacional, calculado en una referencia fija elegida por el usuario (por defecto 0–10 ka BP), con al menos 5 valores y σ > 0. La referencia no cambia al desplazar la ventana objetivo. Se muestran su cobertura efectiva, n, media y desviación. El resumen de la ventana es media o mediana con igual peso por muestra, sin ponderación temporal. z expresa anomalías relativas respecto a cada sitio y elimina el gradiente espacial medio; para estudiar temperaturas absolutas se usa la capa original en °C. No existe una conversión automática de distintos proxies a un clima común.

IDW potencia 2: malla 56×32 sobre la extensión de los sitios seleccionados, solo dentro de la envolvente convexa de sitios distintos no colineales, mínimo 3 vecinos dentro del radio elegido, máscara de tierra/mar Natural Earth 1:110m. El enmascaramiento usa el centro de celda y es aproximado en costas/islas. Una geometría sin soporte deja huecos. No se extrapola fuera de la envolvente; la malla cambia al cambiar la selección de sitios, no al hacer zoom, y el SVG exporta sus parámetros y límites de vista. El IDW no tiene incertidumbre espacial estimada ni validación cruzada: es exploración, no reconstrucción publicable.

Edades archivadas, sin recalibración 14C, interpolación de edad, ensambles ni sincronización. Se preservan BP negativos, ceros y ausencias. Incertidumbres existentes se guardan con su tipo nativo; no se inventan ni se propagan aún al campo espacial. Resolución, duplicación de edades, hiatos y sesgos de muestreo impiden interpretar un mapa atractivo como evidencia automática de sincronía o causalidad.

## Reproducir

Python >=3.10, biblioteca estándar para la base:

```powershell
python -m pip install -e .
python scripts/build_atlas_v1.py --from-seed --sqlite data/processed/atlas-v1-local.sqlite
python -m unittest discover -s tests -v
node --test app/atlas-web/tests/science.test.mjs
```

El script rechaza sobrescribir una SQLite existente. Para reconstruir desde tablas originales:

```powershell
python scripts/fetch_seed.py
python scripts/prepare_seed.py
python scripts/importers/fetch_marine_v1.py
python scripts/importers/audit_marine_v1.py
python scripts/importers/fetch_continental_v1.py
python scripts/importers/curate_continental_v1.py
python scripts/build_atlas_v1.py --site-dir app/atlas-web
```

Los originales van en carpetas ignoradas; un cambio de bytes existentes detiene la adquisición y requiere una nueva versión revisada. La igualdad exacta de bytes remotos futuros no se garantiza. Cambios de fecha de acceso en metadatos generan una nueva huella del derivado. `docs/curation/` documenta mapeos y discrepancias. La semilla versionada permite ejecutar la aplicación sin depender de la disponibilidad del proveedor.

Web (Node >=22.13, npm): desde `app/atlas-web`, `npm ci`, `npm run build`; aplicar ambos `drizzle/*.sql` a D1 local con Wrangler según `STARTER.md`, después `npm run dev`. Primer acceso importa la semilla; no hay esquema creado silenciosamente durante peticiones. El despliegue Sites aplica las migraciones al D1 gestionado. Para publicar se reutiliza `.openai/hosting.json` y el workflow oficial de Sites; credenciales efímeras solo por stdin, nunca en Git. `scripts/sync_atlas_site.py <checkout-sites>` copia exclusivamente fuente hacia este repositorio.

## Evidencia y pendientes

26 pruebas Python locales; 6 pruebas Node científicas; TypeScript y build web. Comparación de las 14.751 filas D1 locales contra los 9 campos de la semilla, incluyendo celdas e incertidumbres. Exportación probada: δ18O continental 6–8 ka, 543 filas CSV y SVG válido. DOI PaleoMED20 verificado y guardado en cola local. Prueba móvil 390×844 y capas de mapa. Estas comprobaciones técnicas y de extracción no sustituyen una revisión independiente de cada cronología/calibración ni validación paleoclimática.

PANGAEA HTTP 400 se resolvió omitiendo Accept para `?format=textfile`; los bytes recuperados coinciden con el original. Comprobación remota acotada de los 4 proveedores correcta. Neotoma y DataCite están conectados para recuperación/metadatos; no se presenta ninguna serie Neotoma como ingerida. LiPD sigue limitado al lector y fixture.

Prioridades: protocolo de curación de artículos y doble revisión; taxonomía y cronologías/duplicados; un archivo lacustre de Neotoma; validación de superficies y propagación de edad/medición; pruebas de escala; persistencia/versionado de consultas; revisión de licencias antes de difusión pública. El código del proyecto sigue sin licencia elegida. NOAA conserva licencia de registro no declarada y base de reutilización WDS documentada, sin inventar CC0. Véase `docs/curation/v1_continental.md`.


### Comprobación autenticada online

El 28-10-2026 se verificó el despliegue con sesión del propietario: catálogo 13/22/14.751, selección SST 6–8 ka con 64 valores y 300 celdas IDW a 600 km; selección δ18O continental con 543 valores y 2 de 3 sitios, sin superficie por falta de soporte. Ambas exportaciones CSV coinciden para cada fila en edad/valor numéricos y sus celdas originales con la semilla. SVG mapa y serie válidos. Se probaron las cuatro capas base, navegación catálogo/mapa y exclusión por año de artículo. PaleoMED20 se verificó por DOI y permanece pendiente de curación tras recarga; no se añadieron sus valores. No se capturaron errores/avisos de consola durante estas pruebas. Véase `reports/atlas_v1_release.json`; esta verificación funcional no es validación paleoclimática.
