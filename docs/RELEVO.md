# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 05-11-2026
- Tarea actual: CUR-POLLEN-MONTICCHIO. Verificar Monticchio y ampliar polen forestal continental. En paralelo, buscar controles numéricos del propio MD99-2337. Publicar las series verificadas.
- Estado: v9-c55489c6f83 verificado localmente, pendiente de publicar. 29 nuevas ubicaciones continentales, Monticchio ampliado, 182 series y 19.898 valores nuevos. 81 pruebas Python y 28 Node pasan. Handoff docs/handoffs/cur-pollen-monticchio.md.
- Producción anterior: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site sirve v8-c131d231e50 con 154 registros, 1.352 series y 924.752 valores. Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: tres series de sortable silt, 306 valores originales, 248 edades interpoladas y 58 sin edad. Contador de ubicaciones a cuatro decimales, consistente con la superficie. 76 pruebas Python, 28 Node, tsc, compilación, snapshot y QA local. Detalles en docs/handoffs/cur-ss-ages.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

0. Lote v9 implementado y probado. Publicar en Sites desde la copia sites/medatlas-v28, generando snapshot de atlas-v9.json y comprobándolo antes de compilar. El contrato y el generador están en Git. Lote investigado inicialmente. Se descargaron Neotoma 47525 (Monticchio, 924 muestras), NOAA 5463 pollen.txt (496 muestras) y Reading Iberia v3 DOI 10.17864/1947.000369. Monticchio tiene solapamiento entre repositorios. Reading contiene unidades mixtas y campos de incertidumbre que requieren revisar su significado antes de convertirlos. Originales locales en data/interim/pollen_v9, aún sin admisión. MD99-2337 sigue sin controles numéricos verificados. Terminar el lote y publicarlo. Petición del 05-11 añadida antes de implementarla: explicar y proponer cómo reducir el consumo de créditos en siguientes sesiones.

1. Continuar la curación con los mismos criterios de procedencia y compatibilidad. Para MD99-2337 buscar puntos numéricos del propio sondeo, en la escala original. Se consultaron PANGAEA.971575/.971574/.256528, Ducassou et al. (2018) y las tesis de Moal-Darrigade y Hassan. Consultar el contrato v8 antes de repetir búsquedas.
2. Continuar con polen de Monticchio en Neotoma y otras ubicaciones continentales. Verificar denominador y cronología antes de derivar porcentajes. Revisar BL12-10 para Ti/Ca. Mantener MP37PC en espera hasta confirmar el rótulo Fe/A.
3. Al cambiar v7, revisar solapamientos y actualizar el hash padre del contrato v8 antes de recompilar. El snapshot bloquea releases con padre obsoleto.
4. La tabla completa de originales, usados y exclusiones por usuario sigue pendiente. El contador del mapa ya cuenta ubicaciones únicas. En Ti/Ca, 11 de 14 sitios con datos en 6–8 ka BP frente a 13 de 16 series en v7.
5. Site privado del mismo proyecto. Despliegue appgdep_6aebc09358a481919ea6def7e182fece y fuente 44c2420. Recibos reports/ss_v8_sites_*.json. El navegador requiere sesión ChatGPT.

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

Sites v8 publicado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site (privado del propietario). El checkout nuevo conserva intacto ../sites/medatlas-v1 y sus borradores. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática v8; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
