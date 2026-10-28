# REV-01: repositorio, revisión y trabajo entre agentes

- Estado: integrado; el resultado de CI se consulta en GitHub Actions.
- Agente/rol: Codex, integración/revisión.
- Rama y commit base: `codex/review-agent-workflows`, base `3aa7f9b`.
- Commit entregado: `50cc278` y seguimiento de documentación/contratos; consultar `git log`.
- Archivos: conectores HTTP/procedencia, scripts de entrega/visor, filtros, tests, AGENTS/CLAUDE, prompts, estado y revisión técnica.
- Resultado: creado remoto privado `SantiCa/mediterranean-multiproxy-atlas`, conectado a `origin` y subido `main`. Tesis, originales crudos y visor auxiliar quedan fuera de Git.
- Decisiones: exportar archivos seguidos por Git; no simular compilación del visor; errores de fuente explícitos; manifiestos con bloqueo por fuente; roles con worktrees/archivos propios.
- Evidencia: instalación editable y 22 tests correctos en Windows/Python 3.14; clon limpio con 14 tests offline y clase de semilla omitida explícitamente. Remoto y commit local comparados por Git. Consultas limitadas de 28-10-2026 documentadas en `reports/live_source_check.json`.
- Limitaciones: PANGAEA HTTP 400 pendiente de diagnóstico; respuestas NOAA/Neotoma/DataCite recuperadas sin normalización completa. Falta revisión científica independiente, esquema relacional y licencia del código.
- Dependencias: usar contratos de DB-01 antes de API-01; separar archivos de conectores marinos y continentales entre chats.
- Siguiente acción: SRC-01, resolver descarga PANGAEA con fuente oficial y verificar paginación NOAA; ver prompt 3 en `docs/CHAT_PROMPTS.md`.
