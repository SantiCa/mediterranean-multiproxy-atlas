# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 05-11-2026
- Tarea en curso: AUD-PROXY-USO finalizada a petición de Santiago («termina»). Handoff docs/handoffs/aud-proxy-uso.md e informe docs/curation/proxy_use_audit.md. Siguiente trabajo propuesto: retomar CUR-READING-18 en rol 01 tras activación; conserva sus bloqueos y estado provisional. Publicación reservada al rol 04; producción v13.
- AUD-PROXY-USO: informes reproducibles de v17 (971.380 valores) y v18 provisional (971.680), sin errores estructurales; 6.615 valores sin edad y siete grupos de coordenadas coincidentes. Corregidos descubrimiento, familias, OI Rock-Eval, estación SST y agrupación polínica sin denominador. Creador de sumas/cocientes/proporciones integrado con multisondeo compatible, recetas locales, originales y exclusiones JSON/CSV. 133 Python, 34 Node, tsc/build, snapshot v17 y QA escritorio correctos. No fusionado a main para conservar fuera de main el lote provisional 7891aa1; integrar conjuntamente tras su cierre. Sin despliegue remoto.
- Estado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site publicado con v13-c0f960a7901: 223 registros, 1.774 series y 960.682 valores. Acceso privado conservado. Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: 182 series y 19.898 valores nuevos con fuentes fijadas por hash, sumas de polen explícitas y originales conservados. 81 pruebas Python, 28 Node, tsc, snapshot, build y QA local. Los 1.002 archivos de producción coinciden. Handoff docs/handoffs/cur-pollen-monticchio.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Rol 01, tras activación: retomar docs/handoffs/cur-reading-18.md y las recomendaciones de docs/handoffs/aud-proxy-uso.md. Terminar la validación de v18 y fusionar relevo en main según AGENTS; la interfaz de auditoría está validada con v17. Después, rol 04 publica main y la última semilla validada regenerando/comprobando snapshot y build, con acceso privado. Producción sigue en v13. No publicar v18 provisional ni v15-c238c8dd19b sustituida.
2. Próximo lote dirigido: contratos pollen_v9_sources.json a pollen_v17_sources.json incorporan 102/122 entidades Reading; las 20 restantes requieren resolver un bloqueo antes de admitir. BANYOLES_1/Banyoles SB2 y NAVA1/NAVARRE3: identidad con padres existentes y muestras compartidas. GALDANA/ESGRAU/HINOJOS/Castello Lagoon y Vilamora P01-5: calibración marina/reservorio. ROQUETAS/ALCUDIA/Abi 05/07: origen del material fechado. LLIGAT: además signo de longitud y posición. Armena/Estanya/Pedrido/ELX: sumas nulas. Villarquemado: contrato IPE; CANALEJA: identidad/coordenadas; CUCU: cronología. Reutilizar iberia-dates.csv (SHA a9bde3e7c9e063ea05e2fcb639596f5a2ecca961ca5c8221a8d7f851ae1986a6), readme v3 y contrato v17. No equiparar age_used vacío con aceptación explícita; conservar exclusiones y correlaciones entre testigos. No repetir búsquedas bloqueadas sin pista nueva.
3. MD99-2337 sigue en espera. Falta una tabla numérica de edad y profundidad del propio sondeo. Consultar el handoff actual y el contrato ss_v8 antes de repetir búsquedas ya documentadas. No usar MD99-2339 como sustituto. Revisar una versión pública de Ducassou 2018 o sus suplementos si aparece acceso nuevo.
4. Monticchio Neotoma 47525 requiere auditoría de versiones y muestras compartidas con NOAA/ACER antes de ampliar su intervalo. Para Reading revisar las entidades de costa con edades marinas y los solapamientos con archivos existentes. ELX tiene 23 filas de suma nula y permanece en espera.
5. Al cambiar un padre, actualizar y reconstruir sus hijos tras revisar duplicados. Para publicar, generar y comprobar el snapshot de atlas-v17.json antes de compilar. El Site usa datos estáticos. El ensamblador Reading rechaza nuevas edades mayores de 55 ka bajo el contrato IntCal20; requieren revisión y contrato cronológico específico, sin recortar ni reemplazar edades.
6. La tabla completa de originales, usados y exclusiones por usuario sigue pendiente. También BL12-10 Ti/Ca y la identificación Fe/A de MP37PC.
7. Organización de chats implementada el 05-11. Datos y auditoría usan GPT-6.1 Sol, esfuerzos medio/alto. Programa y publicación usan GPT-6.1 Terra, esfuerzos medio/bajo. El modelo heredado incompatible quedó corregido en los cuatro chats y se verificó su respuesta de espera. La velocidad Standard es recomendación para el selector. Sin cambios globales de cuenta. Prompts y modo de trabajo en docs/CHAT_PROMPTS.md.
8. Despliegue final appgdep_6aec3335807c81919b6f59ae2ad612a9, fuente 788bc5f. Recibos reports/pollen_v9_sites_*.json. El navegador requiere inicio de sesión ChatGPT.

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

Sites v13 publicado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site (privado del propietario). Checkout ../sites/medatlas-v28. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática v9; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
