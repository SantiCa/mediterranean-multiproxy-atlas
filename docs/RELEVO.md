# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit + push tras cada paso (ver «Relevo» en AGENTS.md).

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: HOST-CF — alojar la web en una cuenta Cloudflare propia (Workers + D1, R2 más adelante) con despliegue por GitHub Actions al fusionar en `main`, sin depender de ChatGPT Sites. Sites sigue activo hasta verificar la nueva web (81.339 valores idénticos).
- Cola: CUR-ODP977A (auditoría profundidad ODP 977A) → GP03.
- Estado: código listo y fusionado en `main` (V2); bloqueado hasta que Santiago cree la cuenta Cloudflare y los secretos (pasos en `docs/DEPLOY_CLOUDFLARE.md`).
- Hecho: `vite.config.ts` acepta `CF_WORKER_NAME`/`CF_D1_DATABASE_NAME`/`CF_D1_DATABASE_ID` (sin ellas, build igual a Sites); `.github/workflows/deploy-cloudflare.yml` (crea/reutiliza D1, migra, compila, despliega, carga semilla+inventario; se salta sin secretos); guía `docs/DEPLOY_CLOUDFLARE.md`. Verificado en local: dry-run 2,26 MB gzip, migraciones 0000–0003, carga completa y `validate_quantitative_api.py` 81.339/81.339 valores.
- Pendiente: (a) Santiago: cuenta, token, secretos, «Run workflow»; (b) validar URL remota con `scripts/validate_quantitative_api.py --url <URL>`; (c) decidir visibilidad (pública por defecto, o Cloudflare Access); (d) actualizar README/PROJECT_STATE con la nueva URL y retirar dependencia de Sites cuando Santiago lo confirme.
- Pruebas: 14 Node correctas; Python sin cambios (33, 6 omitidas).

## Siguiente acción

Si Santiago dice que ya creó los secretos: lanzar o revisar la ejecución de «Deploy web to Cloudflare» en Actions (rama `main`), leer su URL del resumen y ejecutar la validación remota. Si falla la carga por límite diario de D1, relanzar al día siguiente (reanuda). Si aún no los ha creado, guiarle con `docs/DEPLOY_CLOUDFLARE.md` o avanzar con CUR-ODP977A mientras tanto.
