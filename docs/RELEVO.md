# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit + push tras cada paso (ver «Relevo» en AGENTS.md).

- Último agente: ChatGPT/Codex
- Fecha: 29-10-2026
- Tarea actual: CUR-ODP977A — auditar el conflicto de profundidad m/cmbsf de ODP 977A. Santiago autoriza continuar el 29-10-2026. HOST-CF queda pendiente de sus credenciales; no rehacer el código de Claude.
- Cola priorizada por Santiago: CUR-ODP977A → completar cobertura de temperatura → foraminíferos → oxigenación geoquímica y otros indicadores → aporte detrítico → corrientes. GP03 y la tabla de revisión/exclusiones permanecen pendientes; no se eliminan.
- Estado: CUR-ODP977A, unidad resuelta por fuente primaria: cmbsf=corrected meters below seafloor en el artículo de 2020; no hay conversión por100. Ficha preliminar guardada; pendiente archivar PDF/páginas y cierre con pruebas. HOST-CF V2 sigue esperando cuenta/secretos.
- Hecho: `vite.config.ts` acepta `CF_WORKER_NAME`/`CF_D1_DATABASE_NAME`/`CF_D1_DATABASE_ID` (sin ellas, build igual a Sites); `.github/workflows/deploy-cloudflare.yml` (crea/reutiliza D1, migra, compila, despliega, carga semilla+inventario; se salta sin secretos); guía `docs/DEPLOY_CLOUDFLARE.md`. Verificado en local: dry-run 2,26 MB gzip, migraciones 0000–0003, carga completa y `validate_quantitative_api.py` 81.339/81.339 valores.
- Pendiente: (a) Santiago: cuenta, token, secretos, «Run workflow»; (b) validar URL remota con `scripts/validate_quantitative_api.py --url <URL>`; (c) decidir visibilidad (pública por defecto, o Cloudflare Access); (d) actualizar README/PROJECT_STATE con la nueva URL y retirar dependencia de Sites cuando Santiago lo confirme.
- Pruebas: 14 Node correctas; Python sin cambios (33, 6 omitidas).

## Siguiente acción

1. Completar el archivo de evidencia primaria de CUR-ODP977A (PDF aceptado Bari, informe ODP Leg161 y PANGAEA); guardar hashes/localizadores. La cabecera m y el artículo coinciden; no corregir las profundidades numéricas. Ver docs/curation/odp977a_depth_audit.md.
2. Guardar la evidencia y la resolución o incertidumbre en docs/curation/odp977a_depth_audit.md y docs/handoffs/cur-odp977a.md. Tras cada paso válido, actualizar este archivo y hacer commit+push a relevo.
3. Al cerrar con pruebas, merge --no-ff a main. Continuar con un inventario reproducible de cobertura de temperatura, priorizando completar grupos existentes en vez de añadir familias nuevas.

## Solicitudes registradas de Santiago (29-10-2026)

- Completar los registros disponibles de cada proxy del Mediterráneo y áreas adyacentes: primero temperatura, luego foraminíferos, oxigenación, aporte detrítico y corrientes. Medir cobertura por fuentes/consultas/versiones explícitas; no afirmar exhaustividad de toda la literatura sin evidencia.
- Temperatura: separar métodos/calibraciones, estación y variable ambiental; permitir agrupación solo con equivalencia científica justificada. No tratar igual unidad como igual señal.
- Inconsistencias: señalarlas en la aplicación y permitir decisión del usuario sobre uso/exclusión, conservando originales y advertencias.
- Tabla tras seleccionar proxy/mapa: mostrar archivo original y valores usados; permitir excluir una muestra o todo el sondeo, con trazabilidad de la selección. No implementada todavía.
- Existe un borrador local v4 de la sesión anterior: 17 registros nuevos, 63 series/22.195 valores; revisión local y scripts todavía sin integrar/publicar. Mantenerlo separado de la auditoría y preservar sus archivos antes de cualquier limpieza. No presentarlo como estado online ni rehacerlo sin comprobar su disponibilidad.

## HOST-CF pendiente, sin repetir lo hecho

Claude dejó workflow y configuración V2 en f0cffe1, fusionados a main en 92637a4. Esperar cuenta/token/secretos de Santiago; después comprobar Actions/URL remota y visibilidad. Sites sigue privado y activo. Las nuevas prioridades científicas pueden avanzar mientras tanto; no cambiar audiencia ni retirar Sites sin la decisión correspondiente.
