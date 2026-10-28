# Handoff — catálogo, campañas y series v2

Base main 83dec8e; rama codex/catalogue-campaigns. Fuente operativa Sites en ../sites/medatlas-v1; copia pública de código en app/atlas-web. Reutilizar project_id, nunca crear otro Site.

15.572 entradas de fuente (5.846 cores/sitios/unidades; 9.726 DOI de datasets); 289 etiquetas de campaña. No equivalen a sondeos independientes. Fuentes/mapeos/reproducción: docs/DISCOVERY_V2.md. Scripts en scripts/discovery; originales ignorados; semillas versionadas. Migraciones nuevas 0002/0003; colección numérica intacta: 13 registros/14.751 valores.

Ventana móvil de ancho fijo, escala global observada/publicada; comparación de uno/varios/todos compatibles con original/z, zoom, opacidad, ampliación y CSV/SVG. 30 pruebas Python, 9 Node, TypeScript; exportación de nube 294 valores/6 sondeos contrastada. Publicación privada efectiva y comprobaciones en reports/inventory_v2_release.json. El CSV del catálogo usa preparación asíncrona y enlace explícito asociado a los filtros.

Prospección inicial de 5 artículos con fuentes primarias/Crossref y API BioC; suplementos convertidos y preprint GP03 en staging, no ingestión numérica. Próximo: licencia/esquema/celdas originales de Bourget o cloro, doble curación e identidad entre repositorios. La sincronización general con retiradas/correcciones aún no está implementada; no programar importaciones masivas sin protocolo.
