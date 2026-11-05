# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 05-11-2026
- Tarea en curso: CUR-READING-11 (Atlas 01). v11-c58348d32e0 construida: diez ubicaciones, 60 series y 4.482 valores nuevos; total 203 registros / 1.654 series / 955.942 valores. Cinco pruebas específicas pasan y v10 se reproduce sin cambios con el ensamblador reutilizable. PEDRIDO en espera: 63/71 sumas nulas trazadas en contrato. Pendientes pruebas generales, snapshot, handoff e integración. Publicación reservada al rol 04.
- Estado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site sirve v9-c55489c6f83. 183 registros, 1.534 series y 944.650 valores. 29 ubicaciones nuevas, ocho series de Monticchio. Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: 182 series y 19.898 valores nuevos con fuentes fijadas por hash, sumas de polen explícitas y originales conservados. 81 pruebas Python, 28 Node, tsc, snapshot, build y QA local. Los 1.002 archivos de producción coinciden. Handoff docs/handoffs/cur-pollen-monticchio.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Completar CUR-READING-11: revisar hasta diez entidades interiores ausentes de los contratos v9/v10, construir hijo v11, comprobar valores/cronología/duplicados, pruebas y snapshot, handoff y merge según AGENTS. Después rol 04 publicará la última semilla validada. Producción sigue en v9.
2. Próximo lote de datos: continuar seis parámetros Reading v3 con hasta diez entidades interiores nuevas. Consultar ambos contratos pollen_v9_sources.json y pollen_v10_sources.json (39 entidades ya incorporadas). Candidatas por revisar: LAGNEGRA, AYOO, LAGOAJO, LASPARDI, PEDRIDO, SALDROPO. Villarquemado carece de medianas IntCal20 en sus 361 filas: requiere contrato independiente para IPE, sin fallback implícito. Reutilizar originales por hash.
2. MD99-2337 sigue en espera. Falta una tabla numérica de edad y profundidad del propio sondeo. Consultar el handoff actual y el contrato ss_v8 antes de repetir búsquedas ya documentadas. No usar MD99-2339 como sustituto. Revisar una versión pública de Ducassou 2018 o sus suplementos si aparece acceso nuevo.
3. Monticchio Neotoma 47525 requiere auditoría de versiones y muestras compartidas con NOAA/ACER antes de ampliar su intervalo. Para Reading revisar las entidades de costa con edades marinas y los solapamientos con archivos existentes. ELX tiene 23 filas de suma nula y permanece en espera.
4. Al cambiar un padre, actualizar y reconstruir sus hijos tras revisar duplicados. Para publicar, generar y comprobar el snapshot de atlas-v9.json antes de compilar. El Site usa datos estáticos.
5. La tabla completa de originales, usados y exclusiones por usuario sigue pendiente. También BL12-10 Ti/Ca y la identificación Fe/A de MP37PC.
6. Organización de chats implementada el 05-11. Datos y auditoría usan GPT-6.1 Sol, esfuerzos medio/alto. Programa y publicación usan GPT-6.1 Terra, esfuerzos medio/bajo. El modelo heredado incompatible quedó corregido en los cuatro chats y se verificó su respuesta de espera. La velocidad Standard es recomendación para el selector. Sin cambios globales de cuenta. Prompts y modo de trabajo en docs/CHAT_PROMPTS.md.
7. Despliegue final appgdep_6aec3335807c81919b6f59ae2ad612a9, fuente 788bc5f. Recibos reports/pollen_v9_sites_*.json. El navegador requiere inicio de sesión ChatGPT.

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

Sites v9 publicado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site (privado del propietario). Checkout ../sites/medatlas-v28. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática v9; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
