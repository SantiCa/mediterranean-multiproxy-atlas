# Handoff — atlas v1 online

Base: main 1936aee; rama codex/atlas-v1-online. Objetivo: primera web interactiva con datos reales y base persistente.

Fuente web app/atlas-web, SQL migrations/, importers scripts/importers/, canonical data/processed/atlas-v1.json. Release r2: 13 registros, 22 series, 14.751 valores, 40 sin edad. Detalles y comandos en docs/WEB_V1.md. DOI se verifica bibliográficamente y entra pendiente; valores requieren curación.

Decisiones: D1/SQLite, Sites privado, fuentes PANGAEA/NOAA numéricas; Neotoma/DataCite recuperación/metadatos. z dentro de la misma variable respecto a referencia fija; IDW opcional limitado y sin incertidumbre espacial. No reconstrucción validada. Anomalías NOAA y profundidad ODP 977 preservadas/documentadas.

Verificación: 26 tests Python, 6 Node, TypeScript/build, igualdad de los 9 campos de 14.751 filas D1 locales/seed, CSV/SVG y móvil. Consultar informe de despliegue para commit/URL efectivos. Próximo: revisión independiente cronológica y de fuentes, un registro lacustre y validación espacial. No reabrir toda la tesis ni leer los JSON masivos para tareas de interfaz.
