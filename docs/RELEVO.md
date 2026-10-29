# Relevo — puntero vivo

Copia válida: rama `relevo`. Actualizar con commit + push tras cada paso (ver «Relevo» en AGENTS.md).

- Último agente: Claude
- Fecha: 29-10-2026
- Tarea actual: CUR-ODP977A — ficha de auditoría del conflicto de profundidad m/cmbsf de ODP 977A (prompt 5 de `docs/CHAT_PROMPTS.md`); después GP03 con el mismo formato.
- Estado: aceptada por Santiago, sin empezar.
- Hecho: —
- Pendiente: todo.
- Pruebas: 33 Python (6 omitidas sin originales) y 14 Node correctas en clon limpio, base 32e1752.

## Siguiente acción

1. Localizar en `config/seed.json`, `docs/revision_tesis.md`, `docs/curation/v1_marine.md` y `scripts/prepare_seed.py` dónde aparece la profundidad de ODP 977A y en qué unidad se declara.
2. Contrastar contra la fuente primaria (dataset PANGAEA y su metadato de columna; ODP Proceedings Leg 161) sin convertir unidades por inferencia.
3. Escribir `docs/curation/odp977a_depth_audit.md` (resolución o conflicto documentado con citas) y handoff `docs/handoffs/cur-odp977a.md`.
