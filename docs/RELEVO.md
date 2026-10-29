# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 29-10-2026
- Tarea actual: PROXY-COVERAGE-TEMP — completar cobertura cuantitativa de temperatura del Mediterráneo y áreas adyacentes, por fuentes/consultas/versiones verificadas.
- Estado: CUR-ODP977A cerrada y preparada para merge --no-ff a main con pruebas correctas; cobertura de temperatura aún sin empezar.
- Hecho: auditoría en docs/curation/odp977a_depth_audit.md; cmbsf significa metros corregidos bajo el fondo en el artículo primario. No convertir por100. Anotación en config/curation_assertions.json, recibos y script audit_odp977a_depth.py, handoff docs/handoffs/cur-odp977a.md. Raw/semillas/valores sin cambios.
- Pruebas: 43 Python locales (originales disponibles),14Node correctas. No equivale a CI remota. La descarga del manuscrito aceptado da403; la definición se verifica en el texto publicado del editor. ODP y TSV sí archivados porhash.
- Cola: temperatura → foraminíferos → oxigenación geoquímica y otros indicadores → aporte detrítico → corrientes. GP03 permanece pendiente.

## Siguiente acción

1. Construir un inventario reproducible de cobertura de temperatura usando las fuentes ya enlazadas: PANGAEA/DataCite y NOAA, caja [-10,28,42,48], sin edades ni proxies inventados. Contar candidatos, descargados, aptos, duplicados, ambiguos y pendientes.
2. Separar target (SST/aire/agua subsuperficial), estación, método/calibración, unidad y cronología. Buscar primero registros ausentes de grupos existentes; permitir agrupación solo con equivalencia documentada. Misma unidad no basta.
3. Revisar el bundle PANGAEA921235 de ODP977A: ya hay cocolitos, faltan sus SST/isótopos; no crear un segundo sondeo para otro dataset del mismo core. Conservar dependencia del modelo de edadSST.
4. Antes de incorporar datos, revisar el borrador v4 guardado en origin/codex/draft-quantitative-v4 (8239b28), docs/handoffs/quantitative-v4-draft.md; reutilizar lo verificado. No fusionar ciegamente su seed ni sobreescribir vite.config.ts deClaude. El estado online sigue siendo v3:29registros/81.339valores.
5. Tras cada paso válido, actualizar este archivo y commit+push a relevo. Al cerrar tarea, pruebas, handoff y merge --no-ff a main.

## Solicitudes del usuario registradas, pendientes de implementar

- Priorizar completar los proxies existentes, especialmente temperatura, foraminíferos, oxigenación, detrítico y corrientes; no afirmar exhaustividad de toda la literatura sin cobertura verificable.
- Inconsistencias visibles en la aplicación; que el usuario pueda decidir sobre uso/exclusión conservando advertencias y originales.
- Tabla al elegir proxy/mapa con todos los valores del archivo original y cuáles se usan; excluir muestras individuales o todo un sondeo, con trazabilidad.
- La resoluciónODP977A debe aparecer en esa futura interfazQC; no como conversión de profundidad.

## Hosting y preservación

HOST-CF cerrado y validado (Claude, 29-10, V17): **https://med.proxyatlas.workers.dev** (Worker `med`, subdominio de cuenta `proxyatlas`, D1 `medatlas`). Despliegue automático al fusionar en `main` cambios de `app/atlas-web/`; el flujo carga y valida celda a celda (última: 81.339/81.339, 62 grupos). Plan Workers Free sin método de pago: no hay cobro posible; al superar límites diarios D1 las consultas fallan hasta 00:00 UTC. Pendiente de Santiago: Roll del token (se expuso en chat), borrar el Worker sobrante `medatlas` en el panel, decidir visibilidad (pública). Sites sigue activo; su despliegue es exclusivo de Codex. Un solo agente a la vez en `relevo`.

El borradorv4 previo está preservado en la rama remota indicada, no integrado ni desplegado:17registros/63series/22.195valores nuevos; revisión local completa de103.534observaciones. Los cambios no subidos de esa sesión ya están conservados allí. No confundir borrador con el estado activo.
