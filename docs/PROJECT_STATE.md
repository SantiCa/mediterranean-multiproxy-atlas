# Estado breve del proyecto

Actualizado: 28-10-2026. Repositorio privado `SantiCa/mediterranean-multiproxy-atlas`. Usar git log para el commit efectivo.

## Ejecutable v2

- URL: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (privado del propietario).
- Inventario enlazado: 15.572 entradas de fuente, con 5.846 de sondeos/sitios/unidades y 9.726 referencias a datasets PANGAEA. 289 etiquetas de campaña. No equivalen a ubicaciones físicas independientes ya depuradas.
- Fuentes: PaleoMED20 (1.524), NOAA IMLGS (2.723), Neotoma (1.153 unidades), NOAA WDS (355 sitios), PANGAEA XML (10 eventos) y WPA 2025.0 (81 entradas de la consulta); PANGAEA/DataCite 9.726 DOI separados de identidades de core. Consultas/versiones/límites en docs/DISCOVERY_V2.md.
- Mapa/lista, búsquedas y filtros por campaña/fuente/archivo/tipo, agrupación por campaña y exportación CSV. Lista paginada en D1 y puntos compactos con agrupación de navegación.
- Colección cuantitativa conserva 13 registros, 22 series y 14.751 valores. No se atribuyen miles de series numéricas al inventario de metadatos.
- Ventanas temporales de ancho fijo, desplazamiento/recorrido y rango global, con separación de cobertura publicada frente a edades numéricas. Nube de varios/todos los sondeos compatibles, figura ampliada, zoom de intervalo, original/z, opacidad y CSV/SVG trazables.
- Primera prospección de artículos/suplementos documentada en docs/curation/article_scout_2026-10-28.md; convertidos BioC y versión de autor GP03PC en área local. Candidatos pendientes de revisión, sin números inventados.

## Archivos y verificación

Fuente web app/atlas-web; semillas data/processed/atlas-v1.json e inventory-v2.json; migraciones 0000–0003. 30 pruebas Python locales, 9 Node, TypeScript; informes en reports/atlas_v1_release.json y reports/inventory_v2_release.json. El informe v2 se actualiza con el despliegue/verificación efectivos. No inferir CI remota de comprobaciones locales.

## Pendientes científicos / tecnológicos

- Revisar identidad entre fuentes y correspondencias de campaña; corregir solo con evidencia/versiones. Resolver profundidad ODP 977 y datos GP03.
- Importar una primera serie desde suplemento de artículo con doble curación, derechos y cronología comprobados.
- Cronologías alternativas, taxonomías/denominadores, incertidumbre de edad y validación espacial del IDW.
- Sincronización general con retiradas/correcciones/historial; consultas por viewport antes de escalar más allá del límite explícito de puntos.
- Cosecha independiente SISAL/SeaDataNet/ISMAR y servicio WDB-Paleo verificable; evaluación editorial frente a antecedentes, licencia de código pendiente.

No cargar tesis/JSON completos para interfaz rutinaria. Usar AGENTS.md, docs/DISCOVERY_V2.md y el handoff pertinente. No se presenta una nueva reconstrucción paleoambiental validada.
