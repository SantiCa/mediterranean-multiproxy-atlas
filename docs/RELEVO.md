# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 04-11-2026
- Tarea actual: CUR-FOUR-COVERAGE en curso. Ampliar Ti/Ca, Fe/Al, sortable silt y polen forestal en nuevas ubicaciones. Lote anterior cerrado y fusionado en f9a9d0f.
- Lote anterior: CUR-COVERAGE-30 cerrado: lote PANGAEA+NOAA incorporado y publicado. Siguiente propuesta: ampliar cobertura comparable continental y ratios/corrientes por ubicación.
- Estado: Site ChatGPT privado sirve v6-c8ff5c5a738 (138 registros,1.311 series,903.690 valores). Lote propio sobre V29:+10/+225/+38.097. Snapshot público estático; Mis datos desactivado sin OWNER_PASSWORD.
- Hecho: contratos nativos por columna/evento, DOI/año/licencia, duplicados y unidades revisados; cada celda nueva contrastada, v5 inmutable. 71 pruebas Python/27 pruebas Node locales, tsc/build y snapshot completos correctos.964 archivos estáticos remotos idénticos. Handoff docs/handoffs/cur-coverage-30.md; balance reports/priority_v6_coverage.json.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

0. CUR-FOUR-COVERAGE: cotejar sitios/columnas ya incluidos en v6, verificar nuevos candidatos nativos y publicar la ampliación reproducible con trazabilidad.

1. CUR-COVERAGE-30 terminado y publicado en Sites. No repetir este lote ni sus82 fuentes: leer docs/handoffs/cur-coverage-30.md y docs/curation/priority_v6.md. Release v6-c8ff5c5a738:138 registros/1.311 series/903.690 valores. Incremento propio sobre V29:10 registros/225 series/38.097 valores. Datos v5 preservados íntegramente.
2. Siguiente lote propuesto: ampliar porcentajes forestales con denominadores publicados (NOAA/Neotoma); completar Ti/Ca/Fe/Al/sortable silt a más ubicaciones y buscar modelos de edad explícitos para los11 cores de NOAA 10418. Integrar los alias conservadores en el ranking general: el antiguo informe PANGAEA con cero ratios NO demuestra ausencia de razones elementales. No reutilizar automáticamente casos 401/ND/radiocarbono ni convertir cuentas en porcentajes.
3. Al cambiar v5, ejecutar el tramo priority-v6 del flujo de curación antes de publicar: prepare/curate PANGAEA, curate NOAA, build_v6, coverage. La semilla y el snapshot bloquean padres obsoletos. La caja actual sigue [-10,28,42,48]; U1385 (-10,126°) permanece fuera, sin cambio silencioso de región.
4. Tabla completa de originales/usados y exclusiones por usuario sigue pendiente; actualmente se muestran notas por serie y cuarentenas en informes. No afirmar que esa interfaz exista. Cinco series v6 conservadas en cuarentena;29 fuentes PANGAEA retenidas y NOAA 10418 sin edades por muestra.
5. Sites: mismo proyecto privado y checkout ../sites/medatlas-v28. Publicación525ef3fc; despliegue succeeded appgdep_6ae470954d0c8191a2574ae50de66207. Recibos reports/priority_v6_sites_*.json.964 archivos remotos iguales al snapshot comprobado.71 pruebas Python/27 pruebas Node,tsc/build y QA local correctos; navegador de producción pide sesión ChatGPT (no se elude). Mis datos sigue sin OWNER_PASSWORD. No pedir IDs al usuario para retomar.

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

Sites v6 verificado: https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (privado del propietario). El checkout nuevo conserva intacto ../sites/medatlas-v1 y sus borradores. Las credenciales efímeras no se guardan en Git ni informes. El despliegue Sites continúa siendo exclusivo de Codex.

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sirve ahora la instantánea estática v6 verificada; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.
