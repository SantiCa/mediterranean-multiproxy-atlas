# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: Claude
- Fecha: 30-10-2026
- Tarea actual: CURADO en claude/curado (Claude retoma 30-10 01:52). V29 publicado en Cloudflare: v5-c501be5f380 (128 registros, 1.086 series, 865.593 valores) y arreglo de superficie con sitios coincidentes. El Site de ChatGPT sigue en V28 (actualizarlo lo hace Codex). SITES-V28 cerrada por Codex.
- Estado: Site ChatGPT privado actualizado desde main dfdb419 (V28.1), con datos públicos estáticos. Release v5-c25cc8a2394: 102 registros, 815 series, 606 grupos y 241.826 valores. Ya no depende de completar cargas públicas D1. Mis datos desactivado: falta OWNER_PASSWORD; migración 0004 incluida en el paquete y despliegue gestionado por Sites.
- Hecho: snapshot.mjs + check-snapshot.mjs antes de compilar; 24 Node, tsc y build correctos. 608 archivos remotos idénticos por SHA256 al snapshot comprobado celda a celda; las cuatro API retiradas devuelven404. QA visual de inventario, mapa, serie temporal y Mis datos en producción. Handoff docs/handoffs/sites-v28.md; recibos reports/sites_v28_*.json. Fuente Sites743a94ba4509999d409ce07a07519fe90e9abebe; despliegue succeeded appgdep_6ae3c6fb23d08191a63ccb7ba6658dd6.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

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
