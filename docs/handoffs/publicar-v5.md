# Handoff — PUBLICAR-V5 (Claude, 29-10-2026, V18)

- `claude/curado` fusionada en `relevo` (atlas v4 y v5 + scripts/CI de curado).
- v5 (3,4 MB gzip) no cabe en el Worker Free: semilla fuera del bundle; manifiesto `data/release.json`; `lib/release.mjs` elige la última release completa; `/api/bootstrap` responde 503 (la carga la hace el flujo).
- `scripts/d1_release.py` (manifest/plan/finalize) mantiene la codificación y el contrato append-only del antiguo bootstrap. Simulado en SQLite: carga parcial invisible; v3 → v4 → v5 completas (212.880).
- Flujo: paso «Load releases into D1», cron diario, validador con varias semillas (valida la release servida y avisa si la nueva sigue en carga).
- Pruebas: 19 Node, Python OK (15 omitidas), build + dry-run 972 KB gzip.
- Sites (Codex): sin semilla en bundle seguirá sirviendo la release que ya tenga cargada; para cargar v5 allí haría falta este cargador contra su D1.
