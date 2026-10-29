# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit + push tras cada paso (ver «Relevo» en AGENTS.md).

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: HOST-CF — alojar la web en una cuenta Cloudflare propia (Workers + D1, R2 más adelante) con despliegue por GitHub Actions al fusionar en `main`, sin depender de ChatGPT Sites. Sites sigue activo hasta verificar la nueva web (81.339 valores idénticos).
- Cola: CUR-ODP977A (auditoría profundidad ODP 977A) → GP03.
- Estado: en curso (Claude).
- Hecho: decisión de Santiago (29-10, 15:07).
- Pendiente: config de build independiente de `.openai/hosting.json`; workflow de despliegue; guía para que Santiago cree cuenta/API token/secrets; carga inicial D1 y verificación.
- Pruebas: 33 Python (6 omitidas sin originales) y 14 Node correctas, base 32e1752.

## Siguiente acción

1. `npm ci` y `vinext build` en `app/atlas-web` fuera del perfil managed-linux; medir tamaño del Worker (límite plan Free ~3 MB comprimido) porque `data/seed.json` e `inventory.json` se importan en el bundle.
2. Hacer que `vite.config.ts` lea `CF_D1_DATABASE_ID`/`CF_WORKER_NAME` del entorno (manteniendo compatibilidad con Sites).
3. `.github/workflows/deploy-cloudflare.yml`: build, `wrangler d1 migrations apply --remote`, `wrangler deploy`, bucle POST `/api/bootstrap` hasta `ready`.
