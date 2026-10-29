# Colección cuantitativa y explorador de proxies — v3

Integración: 29-10-2026. Descargas del lote: 28-10-2026. Región piloto: Mediterráneo y áreas adyacentes. Release `atlas-quantitative-2026-10-29-v3-r1`.

## Qué se incorpora

29 registros, 89 series y 81.339 valores finitos: **16 registros, 67 series y 66.588 valores nuevos**. PANGAEA añade nueve registros/15 series/37.782 valores; NOAA añade siete/52/28.806. El piloto v1 (13/22/14.751) se conserva, con sus observaciones exactamente iguales. No es una cosecha de todas las series del inventario.

Las ocho familias son temperatura, geoquímica elemental, sedimentología, biomarcadores, micropaleontología, isótopos estables, palinología y paleoincendios. Hay 62 grupos definidos por variable, compatibilidad de método y unidad, no 62 variables ambientales independientes.

- [Curación PANGAEA](curation/pangaea_v3.md): SST por calibración, UK′37, isótopos por especie, Mg/Ca y Ti de Mondsee.
- [Curación NOAA](curation/noaa_v3.md): cuatro cores marinos de Jalali2018; Ohrid con biomarcadores, polen, diatomeas y geoquímica; dos cores de Bourget.
- Rango numérico −0,0574 a 1.365 ka BP. La cobertura de metadatos hasta 121.000 ka continúa separada de las muestras.
- 101 valores sin edad se conservan en almacenamiento y se excluyen del eje temporal y del mapa por edad. No se convierten ausencias en cero.
- 1.371 valores %terr de LDB04-I quedan en cuarentena: 18 exceden 100 %. No se recortan ni se incluyen en `series`.
- Los errores nativos `#DIV/0!` de Ohrid se cuentan y excluyen. Edades repetidas no se eliminan sin evidencia: pueden corresponder a distintas muestras y no son réplicas temporales independientes.

## Selección y filtros

El explorador admite búsqueda por etiqueta, alias, sondeo, especie, calibración y unidad, tolerando mayúsculas/acentos y δ18O/d18O. Facetas encadenadas familia → variable → método/calibración → unidad, paginación de 18 grupos, favoritos en el navegador y opción de cobertura solapada con la ventana de edad. Buscar no cambia la selección activa hasta pulsar «Usar este grupo».

Cada tarjeta muestra número de registros, series, valores y rango de edad. Los filtros globales de fuente, archivo marino/continental, base cronológica y años mínimo/máximo del artículo se aplican conjuntamente al catálogo de opciones y a los datos. Un año desconocido se excluye si se fija un límite. Los años de datasets/editoriales no se presentan como año de un artículo original no resuelto.

La selección activa es un grupo de **proxy + compatibilidad + unidad**. Compartir unidad no demuestra que dos calibraciones o especies sean equivalentes. Müller1998, Prahl1988, Conte2006, SST Versteegh2007 archivada y reconstrucciones Mg/Ca permanecen separados. También permanecen separados denominadores de polen, las calibraciones MAAT, señales estacionales y XRF cps de instrumentos distintos. La normalización z no elimina estas restricciones.

«Ver cobertura» ajusta la ventana al intervalo publicado del grupo y cambia explícitamente a unidades originales. El desplazamiento temporal mantiene la referencia z fija. Las cronologías publicadas BP, varvadas, CE convertidas, 14C calibrado y ajuste orbital se describen por separado; no se recalibran ni se prueban sincronías independientes. Ohrid tiene ajuste orbital: no usar su alineación orbital como validación independiente.

## Datos y escalabilidad

`GET /api/catalog` devuelve metadatos con recuentos y límites temporales, **sin las filas numéricas**. `GET /api/observations?group=...` carga únicamente las series completas del grupo y filtros de registros. No recorta por edad: la referencia z puede situarse fuera de la ventana objetivo. Hay límites explícitos de 150.000 valores y 40 series por petición; un exceso produce error y pide reducir selección, sin truncamiento silencioso. Las consultas usan el índice serie/edad y un máximo de seis consultas simultáneas.

La importación añade la release en etapas de registros, series y observaciones; lotes de 240 filas, ocho por sentencia, como máximo 30 sentencias por lote y menos de 100 parámetros por sentencia. La tabla de releases se marca solo tras contrastar recuentos de todas las series. No hay DDL en peticiones ni borrado de datos/candidatos. El ensamblador rechaza cambios de las observaciones v1. La sincronización general con correcciones/retiradas y cronologías alternativas sigue pendiente.

La nube densa muestra hasta unos 10.000 puntos por selección mediante extremos de bloques consecutivos de muestras, con aviso visible. Es una reducción exclusivamente visual: resúmenes, dominios, CSV y SVG usan los datos completos seleccionados. Se comprobó Mondsee: 10.000 círculos en pantalla, **36.459 en SVG y CSV**, con cada edad/valor/hash contrastado contra la semilla.

La independencia espacial se comprueba además del número de registros: coordenadas exactamente coincidentes suspenden el IDW y mantienen los puntos. Las coincidencias y DOI compartidos son enlaces de revisión, no fusiones automáticas. Las duplicaciones parciales y la dependencia entre modelos requieren revisión científica posterior.

## Trazabilidad y derechos

Observaciones compactas: edad ka BP, valor, fila, línea física, edad/valor originales, incertidumbre de edad/valor y profundidad original. Cada serie conserva tabla/columna/URL/hash, unidad nativa, transformación, método y restricciones. En registros con varias tablas, exportaciones usan el hash/URL de **la serie**. Los límites asimétricos de Cisneros se conservan y exportan por separado, sin inventar un error simétrico.

PANGAEA mantiene CC-BY según cada dataset; NOAA conserva ausencia de licencia CC específica y base de disponibilidad/reutilización WDS, sin atribuir CC0. Los originales se guardan en área local ignorada. Los manifiestos y scripts versionados fijan hashes; archivos nuevos o modificados por proveedores requieren revisión.

## Reproducción y evidencia

```powershell
python scripts/importers/curate_pangaea_v3.py --download
python scripts/importers/curate_noaa_v3.py --fetch
python scripts/build_quantitative_v3.py --site-dir app/atlas-web
python -m unittest discover -s tests -v
node --test app/atlas-web/tests/science.test.mjs app/atlas-web/tests/timeline.test.mjs app/atlas-web/tests/proxies.test.mjs
```

Los curadores son offline por defecto; las opciones de descarga solo recuperan recursos ausentes de sus contratos y verifican hashes. `data/processed/atlas-v1.json` es la línea base inmutable; `atlas-v3.json` es la release nueva. No regenerar la web actual con `build_atlas_v1.py`.

Comprobación explícita del API local: `python scripts/validate_quantitative_api.py --url http://127.0.0.1:5173`. Inicializa solo una base local y compara **las 81.339 filas** devueltas por los 62 grupos contra la semilla. Informe `reports/quantitative_v3_api_check.json`. Otros informes: `quantitative_v3_release.json`, `quantitative_v3_exports.json` y `noaa_v3_audit.json`.

La implementación y las comprobaciones de extracción no equivalen a una reconstrucción mediterránea validada. Siguen pendientes revisión independiente de cronologías/calibraciones, incertidumbre propagada y validación espacial.

## Publicación verificada

El despliegue privado y el API de producción se verificaron el 29-10-2026 mediante acceso de servicio oficial de Sites: las 81.339 observaciones de 62 grupos coinciden con la semilla; filtros combinados y enlace de inventario correctos. Recibos en reports/quantitative_v3_deployment.json y quantitative_v3_production_check.json. Las pruebas visuales se realizaron localmente; el navegador integrado necesita inicio de sesión del visitante. La comprobación de servicio no añade identidad de visitante ni modifica la audiencia. La opción --site-service-access del comprobador exige el dominio exacto y recibe la credencial efímera por entrada oculta, sin guardarla.
