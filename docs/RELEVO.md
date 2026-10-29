# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: PUBLICAR-V5 + CURADO — (1) publicar en la web la versión curada actual (atlas-v5, rama `claude/curado`, fusionada aquí); (2) seguir el curado en `claude/curado`, empezando por asignar edad a datasets PANGAEA cuya edad está en otro dataset del mismo evento.
- Estado: web sirve v5 validada celda a celda (V20: API dentro del límite de CPU Free). V22: lote con modelos de edad del mismo evento (+91 series interpolated_from_age_model) fusionado; release v5-c58d9be4128 se carga en D1 (puede tardar un día). Antes: PUBLICAR-V5 hecho (V18); el despliegue carga v4+v5 en D1 en varios días (límite Free). atlas-v5 (95 registros/709 series/212.880 valores) no cabe en el Worker Free (semilla 3,4 MB gzip > 3 MB): la semilla sale del bundle y la carga en D1 la hace el flujo de despliegue por SQL, por lotes, reanudable a diario (límite 100.000 filas escritas/día). La web sirve la última release completa (v3 hasta terminar la carga).
- Hecho: V19 trocea metadatos <90 KB por sentencia (D1 rechazó el registro de release en V18; observaciones v4+v5 ya cargadas). Validador fusionado; semilla fuera del Worker; `scripts/d1_release.py`; cron diario; handoff docs/handoffs/publicar-v5.md.
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Comprobar en Actions que v5-c58d9be4128 termina de cargar y valida (si avisa «Carga D1 parcial», se completa sola con el cron diario).
2. Seguir curado en `claude/curado`: más lotes `[v5 propose=40 agemodels]`; ampliar candidatos a modelo (hermanos sin `Depth sed` = 105 descartes: revisar si usan otra columna de profundidad equivalente, sin mezclar marcos); NOAA WDS y Neotoma con el mismo patrón; litología categórica.
3. Pendiente decisión de Santiago: «añadir registros» que proponga PANGAEA DOI al contrato de curado; cuenta privada con datos propios (ver respuesta 29-10 en el chat).

## Solicitudes del usuario registradas, pendientes de implementar

- 29-10 (19:02) EN CURSO (Claude): (1) subir datos propios en cuenta privada con identificación, coherentes con la base; (2) búsqueda de proxies ordenable por nº de registros y nº de datos; (3) opción de agrupar en el mapa proxies que miden lo mismo (p. ej. SST); (4) seguir curando priorizando proxies con muchos registros (mapas espaciales), evitando proliferación de proxies distintos.

- 29-10 (18:06): publicar la versión actual; seguir curado en `claude/curado`; interpolar edades con el modelo de edad de otro archivo cuando sea posible. Preguntas: ¿«añadir registros» con un enlace lo cura? ¿coste de cuenta propia con datos privados coherentes con la base?
- Priorizar completar los proxies existentes, especialmente temperatura, foraminíferos, oxigenación, detrítico y corrientes; no afirmar exhaustividad de toda la literatura sin cobertura verificable.
- Inconsistencias visibles en la aplicación; que el usuario pueda decidir sobre uso/exclusión conservando advertencias y originales.
- Tabla al elegir proxy/mapa con todos los valores del archivo original y cuáles se usan; excluir muestras individuales o todo un sondeo, con trazabilidad.
- La resolución ODP977A debe aparecer en esa futura interfaz QC; no como conversión de profundidad.

## Hosting y preservación

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sigue activo; su despliegue es exclusivo de Codex (con la semilla fuera del bundle, Sites seguirá sirviendo su última release cargada). Un solo agente a la vez en `relevo`.
