# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 04-11-2026
- Tarea actual: CUR-FOUR-COVERAGE cerrado. v7 publicada en el Site privado. Lote anterior fusionado en f9a9d0f.
- Lote anterior: CUR-COVERAGE-30 cerrado: lote PANGAEA+NOAA incorporado y publicado. Siguiente propuesta: ampliar cobertura comparable continental y ratios/corrientes por ubicación.
- Estado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site sirve v7-cb1b445291e con 151 registros, 1.349 series y 924.446 valores. El dominio anterior redirige al actual. Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: 13 registros, 38 series y 20.756 valores nuevos. Ti/Ca 8→14 ubicaciones, Fe/Al 3→6, sortable silt 3→4 por medida y polen forestal 2→5. 74 pruebas Python, 27 Node, tsc, compilación, cotejo local y QA del mapa. Handoff docs/handoffs/cur-four-coverage.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Leer docs/handoffs/cur-four-coverage.md y scripts/importers/four_v7_sources.json. Priorizar sortable silt en CADKS24, MD99-2337, U1386 y U1390. Exigir una cronología publicada en el mismo marco de profundidad; U1386 tiene candidato PANGAEA.870577 pendiente de verificar el splice. No repetir candidatos ya resueltos.
2. Revisar polen de Monticchio en Neotoma y otras ubicaciones continentales. Verificar denominador y cronología antes de derivar porcentajes. Revisar BL12-10 para Ti/Ca. Mantener MP37PC en espera hasta confirmar el rótulo Fe/A.
3. Al actualizar v6, revisar de nuevo los solapamientos y actualizar el hash padre del contrato v7 antes de recompilar. El snapshot rechaza una versión con un padre obsoleto. Reproducir desde los contratos fijados y no sustituir originales silenciosamente.
4. La tabla completa de originales, usados y exclusiones por usuario sigue pendiente. Revisar también el contador del mapa: actualmente cuenta filas resumidas por serie bajo el rótulo «sitios». El informe de cobertura deduplica por ubicación.
5. Site privado del mismo proyecto. Despliegue appgdep_6aeb7107ffdc819198245c48b3cca0f8 y fuente e87a5359. Los 987 archivos de producción coinciden byte a byte con el snapshot validado. Recibos reports/four_v7_sites_*.json. URL anterior redirige. Handoff visual en navegador requiere sesión ChatGPT.

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

Sites v7 publicado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site (privado del propietario). El checkout nuevo conserva intacto ../sites/medatlas-v1 y sus borradores. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática v7; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
