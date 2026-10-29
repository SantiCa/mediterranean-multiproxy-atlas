# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: PUBLICAR-V5 + CURADO — (1) publicar en la web la versión curada actual (atlas-v5, rama `claude/curado`, fusionada aquí); (2) seguir el curado en `claude/curado`, empezando por asignar edad a datasets PANGAEA cuya edad está en otro dataset del mismo evento.
- Estado: fusión `claude/curado` → `relevo` en curso. atlas-v5 (95 registros/709 series/212.880 valores) no cabe en el Worker Free (semilla 3,4 MB gzip > 3 MB): la semilla sale del bundle y la carga en D1 la hace el flujo de despliegue por SQL, por lotes, reanudable a diario (límite 100.000 filas escritas/día). La web sirve la última release completa (v3 hasta terminar la carga).
- Hecho: validador fusionado (User-Agent + varias semillas, admite carga parcial).
- Cola científica: temperatura → foraminíferos → oxigenación/MO/bioturbación → detrítico → corrientes; geoquímica inorgánica (razones XRF, EF vs PAAS) prioritaria; litología categórica y mapas por edad pendientes. Detalle en docs/handoffs/claude-curado.md.

## Siguiente acción

1. Implementar carga de releases en D1 fuera del Worker: `data/release.json` (manifiesto pequeño: versiones, series y registros), catálogo/observaciones sirven la última release completa; script Python que genera SQL por lotes; paso del flujo y cron diario. Pruebas, fusionar a main (despliega solo).
2. Volver a `claude/curado`: modelos de edad en otro dataset del mismo evento PANGAEA → asignar edad por interpolación lineal en profundidad dentro del rango del modelo (sin extrapolar), marcando la edad como interpolada y citando el dataset del modelo. Autorizado por Santiago (29-10-2026).

## Solicitudes del usuario registradas, pendientes de implementar

- 29-10 (18:06): publicar la versión actual; seguir curado en `claude/curado`; interpolar edades con el modelo de edad de otro archivo cuando sea posible. Preguntas: ¿«añadir registros» con un enlace lo cura? ¿coste de cuenta propia con datos privados coherentes con la base?
- Priorizar completar los proxies existentes, especialmente temperatura, foraminíferos, oxigenación, detrítico y corrientes; no afirmar exhaustividad de toda la literatura sin cobertura verificable.
- Inconsistencias visibles en la aplicación; que el usuario pueda decidir sobre uso/exclusión conservando advertencias y originales.
- Tabla al elegir proxy/mapa con todos los valores del archivo original y cuáles se usan; excluir muestras individuales o todo un sondeo, con trazabilidad.
- La resolución ODP977A debe aparecer en esa futura interfaz QC; no como conversión de profundidad.

## Hosting y preservación

HOST-CF validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`. Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las escrituras fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas`, decidir visibilidad. Sites sigue activo; su despliegue es exclusivo de Codex (con la semilla fuera del bundle, Sites seguirá sirviendo su última release cargada). Un solo agente a la vez en `relevo`.
