# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 05-11-2026
- Tarea cerrada: CUR-READING-18 tras incorporar conclusiones Atlas 02. v18-cd0f8159f62: 258 registros / 1.978 series / 969.801 valores / 994 grupos. Añade 12 series/300 valores Reading; corrige 1.807 edades de 19 series Mondsee y retiene seis duplicados (1.879 valores), con originales completos en curation_excluded_series. QC incorporado al contrato científico y retirado del parche de publicación. 136 Python aisladas por archivo (cero omisiones), 36 Node, tsc/build y snapshot completo correctos. Auditorías sin errores estructurales. Recibo reports/reading_v18_validation.json; handoff docs/handoffs/cur-reading-18.md. Publicación reservada al rol 04; producción v13.
- AUD-PROXY-USO: informes históricos de v17 (971.380 valores) y v18 provisional (971.680), sin errores estructurales; 6.615 valores sin edad y siete grupos de coordenadas coincidentes. Corregidos descubrimiento, familias, OI Rock-Eval, estación SST y agrupación polínica sin denominador. Creador de sumas/cocientes/proporciones con multisondeo compatible, recetas locales, originales y exclusiones JSON/CSV. Su cierre previo pasó 133 Python, 34 Node, tsc/build, snapshot v17 y QA escritorio. Integración conjunta al cierre científico de v18, cuyo recibo sustituye los recuentos provisionales. Sin despliegue remoto.
- Al cerrar se integró origin/relevo 98467e3 (Claude V30/V31): QC Mondsee y seis duplicados, más CI. El bruto de los informes se conserva; `usage_after_qc` distingue lo servido tras QC: v17 1.966 series / 969.501 valores. Tras merge: 36 Node, tsc/build y snapshot QC completo correctos. Mantener estas correcciones en la siguiente publicación e incorporarlas al cierre científico de v18. Nuestro cribado por mismo proxy no certificaba identidad entre importadores con IDs distintos.
- Estado: https://mediterranean-multiproxy-atlas.santic1290.chatgpt.site publicado con v13-c0f960a7901: 223 registros, 1.774 series y 960.682 valores. Acceso privado conservado. Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: 182 series y 19.898 valores nuevos con fuentes fijadas por hash, sumas de polen explícitas y originales conservados. 81 pruebas Python, 28 Node, tsc, snapshot, build y QA local. Los 1.002 archivos de producción coinciden. Handoff docs/handoffs/cur-pollen-monticchio.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Rol 04: publicar main con atlas-v18.json, v18-cd0f8159f62. Regenerar/comprobar snapshot antes de compilar, con acceso privado. config/qc_corrections.json está vacío porque v18 integra el QC; no restaurar ni aplicar el parche antiguo sobre v18. V17 requiere su QC histórico. No publicar v18-c6df0c5c06b provisional. Recibo reports/reading_v18_validation.json. Integración conjunta incluye el creador del rol 02 y la escala configurable del rol 03. Esta activación no publica; producción v13.
2. Próximo lote dirigido: contratos v9–v18 incorporan 104/122 entidades Reading; Armena/PEDRIDO parcialmente (42/8 muestras válidas, 74 sumas nulas preservadas y excluidas). Quedan 18 bloqueadas. Banyoles/Navarres requieren identidad y muestras compartidas; costa requiere reservorio/materiales/posición; Estanya agua dura 820+/-100 y sumas nulas; ELX conchas y sumas nulas; Villarquemado contrato IPE; CANALEJA identidad; CUCU cronología. Reutilizar tabla de fechas por hash; no inferir aceptación de age_used vacío ni repetir búsquedas bloqueadas sin pista nueva.
3. MD99-2337 sigue en espera. Falta una tabla numérica de edad y profundidad del propio sondeo. Consultar el handoff actual y el contrato ss_v8 antes de repetir búsquedas ya documentadas. No usar MD99-2339 como sustituto. Revisar una versión pública de Ducassou 2018 o sus suplementos si aparece acceso nuevo.
4. Monticchio Neotoma 47525 requiere auditoría de versiones y muestras compartidas con NOAA/ACER antes de ampliar su intervalo. Para Reading revisar las entidades de costa con edades marinas y los solapamientos con archivos existentes. ELX tiene 23 filas de suma nula y permanece en espera.
5. Al cambiar un padre, actualizar y reconstruir sus hijos tras revisar duplicados. Publicar solo el snapshot comprobado de atlas-v18.json. El ensamblador Reading rechaza nuevas edades >55 ka bajo IntCal20; requieren contrato específico. V18 declara 19 series corregidas y seis retenidas como excepciones a la inmutabilidad del padre; las demás series y todos los registros permanecen íntegros.
6. La tabla completa de originales, usados y exclusiones por usuario sigue pendiente. También BL12-10 Ti/Ca y la identificación Fe/A de MP37PC.
7. Organización de chats implementada el 05-11. Datos y auditoría usan GPT-6.1 Sol, esfuerzos medio/alto. Programa y publicación usan GPT-6.1 Terra, esfuerzos medio/bajo. El modelo heredado incompatible quedó corregido en los cuatro chats y se verificó su respuesta de espera. La velocidad Standard es recomendación para el selector. Sin cambios globales de cuenta. Prompts y modo de trabajo en docs/CHAT_PROMPTS.md.
8. Despliegue final appgdep_6aec3335807c81919b6f59ae2ad612a9, fuente 788bc5f. Recibos reports/pollen_v9_sites_*.json. El navegador requiere inicio de sesión ChatGPT.

## Solicitudes del usuario registradas, pendientes de implementar

- 05-11 HECHO: escala de color fija entre edades con límites editables; se reinicia al cambiar proxy, modo o referencia. Handoff docs/handoffs/escala-mapa.md. Pendiente integrar en main después de cerrar v18 provisional y publicar mediante rol 04.

- 05-11 (16:37) HECHO V31 (Claude): fallaban los «Python checks» en cada push. Causas: (1) `test_forest_pollen_v15` no se omitía sin el original ignorado iberia.csv; (2) la suite en un proceso agotaba memoria (semillas de ~70 MB retenidas por clase) y los trabajos se cancelaban. Arreglo: skip como en v16+, y checks.yml ejecuta un archivo de prueba por proceso. Nuevas pruebas que carguen semillas: liberar en tearDownClass o mantener el patrón.

- 05-11 (16:08) HECHO V30 (Claude, rama claude/qc-v30 fusionada en main y aquí; docs/handoffs/auditoria-v17.md): repasar cambios, auditar datos, mejorar y subir. `scripts/audit_science.py` en el despliegue Cloudflare; QC al publicar (`config/qc_corrections.json`): edades Mondsee PANGAEA.929110 corregidas (columna «Age [ka BP]» en ka CE → ka BP = 1,95 − ka CE), 6 series duplicadas pangaea6 retenidas. Rol datos: incorporarlos en v18 y vaciar esas entradas. AUD-PROXY-USO y la v18 provisional de esta rama NO se han publicado.

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
