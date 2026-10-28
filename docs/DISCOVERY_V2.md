# Catálogo enlazado, campañas y comparación temporal — v2

Corte: 28-10-2026. Ámbito confirmado por el usuario: Mediterráneo y zonas adyacentes, rectángulo [-10,28,42,48] (O,S,E,N). No se afirma inventariar todos los sondeos existentes ni todos los repositorios del mundo. Esta caja incluye Alpes, márgenes atlánticos, Mar Negro y borde del Mar Rojo; una futura geometría de cuencas permitirá afinarla sin modificar entidades.

## Resultados por fuente

| Fuente | Entradas incorporadas | Grano / límites |
|---|---:|---|
| PaleoMED20 v1 | 1.524 | Todas las filas de Core database del XLSX publicado; CC-BY-4.0; crucero, plataforma y año nativos |
| NOAA IMLGS / ERDDAP | 2.723 | Testigos/perforaciones de 3.578 muestreos; se excluyen dragas, grabs y dispositivos desconocidos |
| Neotoma | 1.153 | Unidades de colección identificadas: 1.186 sitios en dos páginas; 1.983 representaciones se consolidan solo por ID exacto de unidad/sitio |
| NOAA WDS | 355 | Sitios puntuales de 298 estudios de archivos seleccionados; no se convierten polígonos globales en ubicaciones inventadas |
| PANGAEA, XML nativo | 10 | Eventos de los datasets cuantitativos actuales; 6 declaran campaña explícita |
| WPA 2025.0 | 81 | Tabla pública Raw Data de la consulta guardada; no se afirma cubrir todas las vistas/variables WPA |
| PANGAEA vía DataCite | 9.726 | Referencias a datasets, separadas de identidades de sondeo; 10 páginas completas de la consulta declarada; 3.329 puntos dentro de la caja |

Total: 15.572 entradas de fuente; 5.846 de sondeos/sitios/unidades y 9.726 de datasets. 9.175 tienen una coordenada utilizable al incluir datasets. Los recuentos no representan sondeos físicos independientes: las correspondencias entre fuentes permanecen sin fusionar hasta verificar identidad. Una coincidencia de coordenadas o nombre parecido no basta. Las variables/taxones originales de unidades Neotoma repetidas se conservan como uniones de IDs y etiquetas, no como nuevas observaciones.

PANGAEA/DataCite: consulta reproducible en `scripts/discovery/pangaea_inventory.py`. Los campos indexados de latitud y longitud pueden corresponder a distintas ubicaciones de un mismo registro; se revisa la coordenada exacta antes de dibujar. Las referencias sin un único punto admitido siguen enlazadas en la lista, sin fabricar un sondeo o un centroide. El año de publicación del dataset permanece separado del año del artículo.

IMLGS: el visor histórico fue retirado, pero la respuesta ERDDAP oficial consultada sigue accesible; su metadata declara una instantánea creada el 11-11-2024 y muestreos hasta 2023. Es un inventario de muestras físicas, no una garantía de disponibilidad actual. El DOI de facility es del repositorio, no del testigo. No se recalcula una edad de muestra desde la fecha de expedición.

SeaDataNet/ISMAR forman parte de las fuentes documentales del inventario PaleoMED20, pero aquí no se ha implementado su cosecha independiente. SISAL y WDB-Paleo permanecen pendientes de importación/servicio verificable. La cobertura se describe por fuente, consulta y versión; «conectado» no significa «completo» ni «datos cuantitativos revisados».

## Campañas y navegación

289 etiquetas de campaña declaradas, con IDs en el espacio de cada fuente y localizador de procedencia. Se conservan plataforma, fechas/año y alias disponibles. La vista agrupada incluye una categoría adicional «sin campaña declarada»; no se trata como una campaña. Un estudio bibliográfico no se convierte en crucero y no se deduce una campaña desde el prefijo de un testigo.

Las diferencias entre LEG161 (PaleoMED20), Leg161 (PANGAEA) y 161 (IMLGS) se mantienen visibles. Los años archivados también se conservan; no se corrigen por conocimiento informal. Una tabla de correspondencias revisada será un entregable independiente. Los círculos agrupados en mapa son agrupaciones para navegación, no promedios de proxies ni evidencia de independencia espacial.

## Implementación y escalabilidad

`atlas_inventory`, `atlas_campaigns`, `atlas_inventory_campaigns`, `atlas_inventory_releases` se añaden mediante migraciones 0002/0003; no se ejecuta DDL en peticiones. La colección cuantitativa conserva sus tablas y sus 14.751 valores. El catálogo completo versionado está en `data/processed/inventory-v2.json`; `data/inventory.json` es su copia web generada.

API `/api/inventory`: resumen/cobertura, detalle por ID, lista paginada (60), grupos de campaña y mapa con campos compactos. Búsqueda textual y filtros fuente/archivo/tipo/campaña usan parámetros SQL. El mapa tiene un límite explícito de 20.000 entradas por consulta; informa truncado si se supera y permite reducir selección. El CSV de metadatos respeta los mismos filtros, limita exportaciones excesivas explícitamente y conserva fuente/estado/DOI/años/campañas. Las ubicaciones y las referencias a datasets se distinguen de las series revisadas.

La exportación del catálogo se prepara desde la página y después ofrece «Descargar metadatos CSV». El enlace conserva los filtros usados y se invalida al cambiarlos; evita depender de una navegación directa al endpoint de descarga o de un clic programático tras una petición asíncrona.

La inicialización usa lotes idempotentes de 240 filas, ≤90 parámetros por sentencia y menos de 50 sentencias por petición; codifica únicamente el lote actual para limitar CPU/memoria. La primera carga importa la versión; después consulta D1. Esta v2 es una incorporación de instantánea, no un motor general de sincronización con retiradas, correcciones e historial relacional. Antes de programar actualizaciones, añadir revisión de diff, estado activo/retirado, versionado de relaciones y migración de correcciones. No hay tareas periódicas configuradas.

## Ventanas móviles y series

El usuario puede fijar el ancho en ka, desplazar inicio manteniendo ancho, avanzar/retroceder por una ventana, recorrer automáticamente, pausar y ampliar la escala cerca de la posición. Se conserva el intervalo libre. Los límites proceden de todo el catálogo y no del proxy/año actualmente filtrados; se preservan las edades BP negativas. La referencia z no se recalcula al mover la ventana.

Valores numéricos actuales: −0,056 a 429,69 ka. Cobertura máxima declarada en metadata: 121.000 ka (121 Ma), DSDP 545 del margen atlántico, estudio NOAA 14568 sobre el Cretácico. No se han cargado sus muestras. El selector «Extensión temporal» permite usar toda la cobertura publicada o solo el rango de los valores cargados; el aviso distingue ambos. El mapa queda vacío/gris sin datos suficientes: la extensión del deslizador no produce observaciones.

La comparación temporal permite un sondeo, varios elegidos o todos los compatibles con la variable/método/unidad seleccionados. Nube de puntos por sondeo con colores distintos, sin líneas que crucen hiatos; escala original o z con referencia fija, zoom al intervalo seleccionado, opacidad, figura ampliada y exportación CSV/SVG con DOI, hashes, localizadores y parámetros. No combina diferentes proxies en una unidad ambiental ficticia. Los valores sin edad permanecen en la base y no se dibujan en un eje de edad.

## Reproducción

```powershell
python scripts/discovery/fetch_aux_inventory.py
python scripts/discovery/pangaea_inventory.py
python scripts/discovery/continental_inventory.py
python scripts/discovery/build_inventory.py --site-dir app/atlas-web
python -m unittest discover -s tests -v
node --test app/atlas-web/tests/science.test.mjs app/atlas-web/tests/timeline.test.mjs
```

Los originales van en `data/interim/`, ignorado. La caché existente no se sobrescribe; los hashes de los originales usados quedan en el catálogo/informe. La reproducción desde proveedores vivos puede encontrar versiones nuevas; se requiere revisar un nuevo snapshot en vez de prometer identidad de bytes a futuro. No ejecutar todos los recolectores para tareas rutinarias de interfaz: la semilla versionada permite ejecutar offline.

Validación local: 30 pruebas Python, 9 Node, TypeScript, endpoints con filtros/paginación/grupos, campaña LEG161→6 entradas, nube SST→294 puntos/6 sondeos y comparación de cada edad/valor exportados contra semilla. SVG de nube: 294 círculos, 6 colores distintos. La v1 cuantitativa sigue siendo una muestra intencional, no una reconstrucción validada. Evidencia de despliegue y verificación real en `reports/inventory_v2_release.json`.
