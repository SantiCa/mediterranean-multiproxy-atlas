# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: PUBLICAR-V5 + CURADO — (1) publicar en la web la versión curada actual (atlas-v5, rama `claude/curado`, fusionada aquí); (2) seguir el curado en `claude/curado`, empezando por asignar edad a datasets PANGAEA cuya edad está en otro dataset del mismo evento.
- Estado: web sirve v5 validada celda a celda (V20: API dentro del límite de CPU Free). V22: lote con modelos de edad del mismo evento (+91 series interpolated_from_age_model) fusionado; release v5-c58d9be4128 se carga en D1 (puede tardar un día). Antes: PUBLICAR-V5 hecho (V18); el despliegue carga v4+v5 en D1 en varios días (límite Free). atlas-v5 (95 registros/709 series/212.880 valores) no cabe en el Worker Free (semilla 3,4 MB gzip > 3 MB): la semilla sale del bundle y la carga en D1 la hace el flujo de despliegue por SQL, por lotes, reanudable a diario (límite 100.000 filas escritas/día). La web sirve la última release completa (v3 hasta terminar la carga).
- Hecho: V27 respaldo estático (`public/snapshot/`, generado en el build) cuando D1 no responde. V26 reduce lecturas D1 (recuentos solo de series pendientes por índice; validación completa solo al completar una release). V19 trocea metadatos <90 KB por sentencia (D1 rechazó el registro de release en V18; observaciones v4+v5 ya cargadas). Validador fusionado; semilla fuera del Worker; `scripts/d1_release.py`; cron diario; handoff docs/handoffs/publicar-v5.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Límite diario D1 agotado el 29-10 (19:30): la ejecución nocturna (00:17 UTC) aplica la migración 0004 (Mis datos), despliega y continúa la carga de la v5 nueva (ids de serie con hash de contenido → recarga ~240.000 valores v5, 2–5 días). Mientras tanto la web sirve v5-c58d9be4128 (conservada en el manifiesto). Comprobar en Actions.
2. Santiago: crear secreto GitHub `ATLAS_OWNER_PASSWORD` (≥12 caracteres) y relanzar «Deploy web to Cloudflare» para activar «Mis datos».
3. Seguir curado en `claude/curado` con `[v5 propose=60 agemodels prune]`: el orden ya prioriza parámetros con más sondeos fechados; columnas con < 3 sondeos se difieren (reversible) salvo las de agrupaciones (SST, δ18O/δ13C, TOC, CaCO3). Pendiente: NOAA WDS y Neotoma con el mismo patrón; 105 hermanos sin `Depth sed`.

## Solicitudes del usuario registradas, pendientes de implementar

- 29-10 (22:02) HECHO (V27, docs/handoffs/respaldo-estatico.md): la web cae cuando se agota el límite diario de D1 (API 5xx, «Conectando con el catálogo…»). Respaldo: instantánea estática de la última semilla (catálogo + observaciones por grupo) en `public/snapshot/`, generada en el build; el cliente la usa si la API falla, con aviso.

- 29-10 (19:02) (1)–(3) HECHOS en V23; (4) V24: curado por cobertura (docs/handoffs/claude-curado.md). Petición: (1) subir datos propios en cuenta privada con identificación, coherentes con la base; (2) búsqueda de proxies ordenable por nº de registros y nº de datos; (3) opción de agrupar en el mapa proxies que miden lo mismo (p. ej. SST); (4) seguir curando priorizando proxies con muchos registros (mapas espaciales), evitando proliferación de proxies distintos.

- 29-10 (18:06): publicar la versión actual; seguir curado en `claude/curado`; interpolar edades con el modelo de edad de otro archivo cuando sea posible. Preguntas: ¿«añadir registros» con un enlace lo cura? ¿coste de cuenta propia con datos privados coherentes con la base?
- Priorizar completar los proxies existentes, especialmente temperatura, foraminíferos, oxigenación, detrítico y corrientes; no afirmar exhaustividad de toda la literatura sin cobertura verificable.
- Inconsistencias visibles en la aplicación; que el usuario pueda decidir sobre uso/exclusión conservando advertencias y originales.
- Tabla al elegir proxy/mapa con todos los valores del archivo original y cuáles se usan; excluir muestras individuales o todo un sondeo, con trazabilidad.
- La resolución ODP977A debe aparecer en esa futura interfaz QC; no como conversión de profundidad.

## Hosting y preservación

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sigue activo; su despliegue es exclusivo de Codex (con la semilla fuera del bundle, Sites seguirá sirviendo su última release cargada). Un solo agente a la vez en `relevo`.
