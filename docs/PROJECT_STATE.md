# Estado breve del proyecto

Actualizado: 28-10-2026. GitHub `SantiCa/mediterranean-multiproxy-atlas`, privado. Usar `git log -1` para el commit efectivo.

## Ejecutable

- Web v1 en https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site (privado): mapa de proxies, capas base, selección por edad/publicación/archivo, z o valores originales, IDW optativo, series y exportaciones CSV/SVG.
- Base propia D1/SQLite: 13 registros, 22 series, 14.751 valores. 10 registros PANGAEA y 3 espeleotemas NOAA. 40 valores sin edad preservados; no se ubican en ventanas cronológicas. Semilla `data/processed/atlas-v1.json`, release `atlas-v1-2026-10-28-r2`.
- Fuente web en `app/atlas-web/`; migraciones en `migrations/`; construcción SQLite/semilla `scripts/build_atlas_v1.py`. Detalles y reproducción: `docs/WEB_V1.md`.
- Clientes Python PANGAEA, NOAA, Neotoma, DataCite; lector LiPD. Los últimos cuatro checks HTTP recuperan datos/metadatos; solo PANGAEA y NOAA aportan valores al atlas.
- Cola DOI persistente: verifica identidad bibliográfica y deja la fuente pendiente de curación; no inventa extracción automática de artículos.
- AGENTS.md/CLAUDE.md, prompts en docs/CHAT_PROMPTS.md, tesis revisada y borrador de publicación disponibles.

## Verificación

26 pruebas Python locales, 6 Node, TypeScript y build. Fidelidad de las 14.751 filas D1 locales contra semilla con 9 campos. Exportaciones reales CSV/SVG y móvil probados. Los conteos no prueban representatividad ni independencia de muestras. CI remota se consulta por ejecución; no inferir su éxito a partir de pruebas locales.

## Backlog

| ID | Entregable |
|---|---|
| CUR-02 | Doble revisión por artículo: tablas, métodos, cronología, licencia, duplicados; resolver profundidad ODP 977 y disponibilidad GP03 |
| CON-02 | Un registro lacustre/polínico Neotoma real, con taxonomía y cronología preservadas |
| DB-02 | Versionar cronologías/regiones/transformaciones en tablas; contrato compatible con v1 y migración reversible |
| MAP-02 | Validación espacial/temporal, propagación de incertidumbre, resolución apropiada y criterios de exclusión |
| API-02 | Paginación/consultas por viewport y agregación servidor; pruebas de escala antes de ampliar miles de registros |
| PUB-02 | Comparación cuantitativa versionada con antecedentes y evaluación independiente; elegir licencia de código |

## Límites

z compara anomalías de la misma variable, no convierte proxies distintos en una reconstrucción común. IDW es exploratorio. Sin cronologías armonizadas ni incertidumbre espacial. El modelo relacional operativo es menor que la arquitectura científica propuesta. Continental actual = espeleotemas, no todos los archivos. Basemaps externos pueden cambiar. El visor `report-app/` es auxiliar, distinto de la web del atlas. No cargar la tesis completa para desarrollo rutinario: usar `docs/revision_tesis.md`.
