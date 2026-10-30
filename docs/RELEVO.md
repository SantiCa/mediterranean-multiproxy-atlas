# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 30-10-2026
- Tarea actual: CUR-COVERAGE-30 — relevo Codex, ampliar en un lote amplio la cobertura de proxies existentes: ratios de elementos inorgánicos, corrientes, oxigenación profunda y vegetación/bosque continental. Base V29 v5-c501be5f380 (128 registros, 1.086 series, 865.593 valores); no repetir lotes de Claude. El Site ChatGPT sigue V28 hasta nuevo despliegue Codex.
- Estado: Site ChatGPT privado actualizado desde main dfdb419 (V28.1), con datos públicos estáticos. Release v5-c25cc8a2394: 102 registros, 815 series, 606 grupos y 241.826 valores. Ya no depende de completar cargas públicas D1. Mis datos desactivado: falta OWNER_PASSWORD; migración 0004 incluida en el paquete y despliegue gestionado por Sites.
- Hecho: snapshot.mjs + check-snapshot.mjs antes de compilar; 24 Node, tsc y build correctos. 608 archivos remotos idénticos por SHA256 al snapshot comprobado celda a celda; las cuatro API retiradas devuelven404. QA visual de inventario, mapa, serie temporal y Mis datos en producción. Handoff docs/handoffs/sites-v28.md; recibos reports/sites_v28_*.json. Fuente Sites743a94ba4509999d409ce07a07519fe90e9abebe; despliegue succeeded appgdep_6ae3c6fb23d08191a63ccb7ba6658dd6.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

0. Petición registrada 30-10: priorizar nº de registros por proxy usado, no proliferar grupos de un sondeo. Revisar alias de ratios (el informe antiguo declara cero), parámetros y denominadores de polen, profundidad/hábitat de indicadores redox/corrientes, unidades y cronologías. Completar candidatos verificables de PANGAEA/NOAA/Neotoma en un lote; conservar incertidumbres/duplicados/inconsistencias y no inventar clases forestales o velocidades de corriente. Trabajar secuencialmente en relevo, con checkpoints y push; al terminar pruebas, handoff y merge --no-ff, actualizar Sites con snapshot verificado. Si se necesita otro chat, el contexto mínimo quedará en el handoff y este puntero.

   Checkpoint Codex: 82 datasets intentados;76 TSV/XML descargados en data/interim/priority_v6/pangaea,6 HTTP401 sin bypass. Metadatos/hashes/IDs versionados en reports/priority_v6_candidates.json. Alias de elementos largos y clasificación conservadora en scripts/discovery/priority_vocabulary.py (3pruebas): no confundir diatomea alpinus con Pinus, Rock-Eval con oxigenación, U-Th con redox o eDNA con polen. Ensamblador v5 admite padre/fragmento/prefijo explícitos para crear v6 sin alterar v5. Próximo: contrato e importador del lote, excluir metadatos ND de nueva redistribución sin revisión, eventos fuera de caja (U1385 a-10,126°) y separar GC-01A-PC/TC por columna Event; seleccionar columnas aún ausentes de los datasets ya curados.

   Lote PANGAEA ya funciona: curate_priority_v6.py + contrato priority_v6_sources.json + build_quantitative_v6.py; v6-c12503ee3d2 =137registros/1.299series/902.530valores; +9/+213/+36.937 sobre v5. 5series en cuarentena,29fuentes retenidas (acceso/licencia/edad/ámbito). Cada celda/evento nuevo contrastado; v5 inmutable. Pruebas70Python locales y26Node correctas (ver skips explícitos por originales previos). UI busca Fe/Al/Ti/Ca por alias, muestra notas de la serie incluso si el registro padre es antiguo, separa fracciones/denominadores y prioriza≥2registros. Aún no desplegado. Siguiente: ampliar NOAA con estudios10418 (Black Sea geochemistry) y43639 (Ligurian Sea geochemistry + sortable silt), encontrados en metadatos ya enlazados; revisar tablas/cronología/sitios antes de incorporar. No repetir los82PANGAEA.

   Lote conjunto terminado: v6-c8ff5c5a738,138registros/1.311series/903.690valores; +10/+225/+38.097. NOAA43639 añade12series/1.160valores;10418 retenido sin edad por muestra (11cores). DOI/año2026 comprobados en Crossref, U/Mn con1σ nativo.71Python/27Node correctas. Documentación docs/curation/priority_v6.md y handoff docs/handoffs/cur-coverage-30.md; balance reports/priority_v6_coverage.json. CI recompone v6 tras cambios de v5 y snapshot bloquea padres obsoletos. Próximo inmediato: snapshot/build/QA/despliegue privado Sites desde ../sites/medatlas-v28; comprobar todos los estáticos, registrar publicación y cerrar con merge --no-ff. No hay necesidad de pedir IDs al usuario.

   Preflight Sites correcto: snapshot v6 comprobado celda a celda (903.690valores/962grupos/964archivos; mayor estático inventario16,6MiB). Fuente159archivos exportada desde803fd45. Recibo reports/priority_v6_sites_preflight.json. Helper oficial abierto sobre743a94b en ../sites/medatlas-v28. Ahora tsc/build/empaquetado y QA antes de publicar.

1. Seguir curado en `claude/curado` con `[v5 propose=60 agemodels prune]`; al fusionar en main se publica en Cloudflare. Pendiente: NOAA WDS y Neotoma con el mismo patrón; 105 hermanos sin `Depth sed`. Consultar su handoff y log antes de repetir fuentes; el checkpoint antiguo de temperatura no está integrado.
2. (30-10 01:11 UTC: migración 0004 aplicada en Cloudflare con el despliegue V29; solo falta el secreto.) Si Santiago decide activar Mis datos: GitHub usa ATLAS_OWNER_PASSWORD y el Worker recibe OWNER_PASSWORD; el Site ChatGPT necesita su propio secreto OWNER_PASSWORD. No copiar ni inventar contraseñas. La ausencia del secreto no impide usar datos públicos.
3. Futuros despliegues Sites: usar ../sites/medatlas-v28, conservar identidad/audiencia y generar/comprobar snapshot desde la semilla más reciente antes del build. scripts/validate_static_site.py verifica los archivos publicados; ya no usar validate_quantitative_api.py contra las API eliminadas. No repetir el despliegue V28 ya confirmado.

## Solicitudes del usuario registradas, pendientes de implementar

- 30-10 (01:54) HECHO V29.1: en SST agrupada, «registros con coordenadas coincidentes» suspendía la superficie; ahora cuentan como un nodo (mediana) y se avisa.

- 29-10 (22:47) HECHO V28: datos públicos desde archivos estáticos; D1 solo para Mis datos y DOI.

- 29-10 (22:02) HECHO (V27, docs/handoffs/respaldo-estatico.md): la web cae cuando se agota el límite diario de D1 (API 5xx, «Conectando con el catálogo…»). Respaldo: instantánea estática de la última semilla (catálogo + observaciones por grupo) en `public/snapshot/`, generada en el build; el cliente la usa si la API falla, con aviso.

- 29-10 (19:02) (1)–(3) HECHOS en V23; (4) V24: curado por cobertura (docs/handoffs/claude-curado.md). Petición: (1) subir datos propios en cuenta privada con identificación, coherentes con la base; (2) búsqueda de proxies ordenable por nº de registros y nº de datos; (3) opción de agrupar en el mapa proxies que miden lo mismo (p. ej. SST); (4) seguir curando priorizando proxies con muchos registros (mapas espaciales), evitando proliferación de proxies distintos.

- 29-10 (18:06): publicar la versión actual; seguir curado en `claude/curado`; interpolar edades con el modelo de edad de otro archivo cuando sea posible. Preguntas: ¿«añadir registros» con un enlace lo cura? ¿coste de cuenta propia con datos privados coherentes con la base?
- Priorizar completar los proxies existentes, especialmente temperatura, foraminíferos, oxigenación, detrítico y corrientes; no afirmar exhaustividad de toda la literatura sin cobertura verificable.
- Inconsistencias visibles en la aplicación; que el usuario pueda decidir sobre uso/exclusión conservando advertencias y originales.
- Tabla al elegir proxy/mapa con todos los valores del archivo original y cuáles se usan; excluir muestras individuales o todo un sondeo, con trazabilidad.
- La resolución ODP977A debe aparecer en esa futura interfaz QC; no como conversión de profundidad.

## Hosting y preservación

Sites V28 verificado: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (privado del propietario). El checkout nuevo conserva intacto ../sites/medatlas-v1 y sus borradores. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática V28 verificada; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
