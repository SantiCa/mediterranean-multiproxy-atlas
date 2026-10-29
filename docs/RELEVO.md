# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit+push tras cada paso; ver AGENTS.md.

- Último agente: ChatGPT/Codex
- Fecha: 29-10-2026
- Tarea actual: PROXY-COVERAGE-TEMP — completar cobertura cuantitativa de temperatura del Mediterráneo y áreas adyacentes, por fuentes/consultas/versiones verificadas.
- Estado: CUR-ODP977A cerrada y fusionada en main (53fa4a3). Primer paso de cobertura de temperatura terminado: cola reproducible de fuentes, sin cambios todavía en observaciones/web.
- Hecho: auditoría en docs/curation/odp977a_depth_audit.md; cmbsf significa metros corregidos bajo el fondo en el artículo primario. No convertir por100. Anotación en config/curation_assertions.json, recibos y script audit_odp977a_depth.py, handoff docs/handoffs/cur-odp977a.md. Raw/semillas/valores sin cambios.
- Pruebas: 43 Python locales (originales disponibles),14Node correctas. No equivale a CI remota. La descarga del manuscrito aceptado da403; la definición se verifica en el texto publicado del editor. ODP y TSV sí archivados porhash.
- Cola: temperatura → foraminíferos → oxigenación geoquímica y otros indicadores → aporte detrítico → corrientes. GP03 permanece pendiente.
- Cobertura: scripts/temperature_coverage.py y reports/temperature_coverage.json. Nueva consulta DataCite sin sesgo sediment/core:6.659 DOI/7páginas; postfiltro de puntos y unión con inventario/seed. PANGAEA:14 DOI admitidos con temperatura,1.878 pendientes,71 ambiguos,98 fuera de objetivo. NOAA:5 entradas sitio/tabla/archivo admitidas y57 pendientes; no sumar como sondeos. Pruebas específicas4 correctas; documentación docs/curation/temperature_coverage.md.

## Siguiente acción

1. Continuar desde la cola de temperatura ya generada. Revisar primer lote nativo descargado en data/interim/temperature_batch1: PANGAEA921234,939417,939418,955015,866949,925876 y NOAA21992/22582. Cada recurso tiene recibo/hash. No están incorporados.925876 no contiene edad; no inventarla ni unir por profundidad sin modelo explícito.866949 tiene DOS columnas idénticamente nombradas: leer por ordinal, no DictReader que perdería una calibración. NOAA21992 es latin1 aunque no lo declare bien; preservar bytes.22582 tiene versiones relacionadas y posibles discrepancias de año: revisar antes de admitir.
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

HOST-CF V2 deClaude (f0cffe1, merge main92637a4) está listo y espera cuenta/token/secretos del usuario. No repetirlo ni retirar Sites. Si Santiago confirma secretos, comprobar Actions, URL remota y visibilidad; mientras tanto avanzar ciencia. El despliegue Sites sigue siendo exclusivo deCodex.

El borradorv4 previo está preservado en la rama remota indicada, no integrado ni desplegado:17registros/63series/22.195valores nuevos; revisión local completa de103.534observaciones. Los cambios no subidos de esa sesión ya están conservados allí. No confundir borrador con el estado activo.
