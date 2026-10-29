# Handoff — ampliación cuantitativa y selección de proxies v3

Base main 523a1f1; rama codex/quantitative-proxy-browser. Release atlas-quantitative-2026-10-29-v3-r1. Fuente Sites ../sites/medatlas-v1, copia app/atlas-web, mismo project_id privado. Ver docs/QUANTITATIVE_V3.md y reports/quantitative_v3_*.json.

29 registros/89 series/81.339 valores, 62 grupos y ocho familias; 16 registros/66.588 valores nuevos. PANGAEA9datasets y NOAA3estudios. Originales locales ignorados; curadores con contratos/hashes; baseline atlas-v1.json intacta y actual atlas-v3.json. 101 valores sin edad conservados. %terr LDB04-I en cuarentena; Cadagno intervalar y PRGL1 sin publicación resuelta no ingeridos.

Selector con búsqueda/facetas/favoritos, filtros conjuntos y grupo variable/método/unidad. Calendarios/especies/calibraciones/denominadores separados. Metadata sin observaciones, consulta lazy completa por grupo (máx150k/40series). Bootstrap por etapas idempotentes; no DDL ni borrado. Densidad visual reducida con aviso, cálculos/CSV/SVG completos. IDW suspendido con coordenadas coincidentes.

Verificación: 41 pruebas Python, 14 Node, TypeScript/build. API local compara las81.339 filas de62grupos. CSV820SSTConte y36.459Ti Mondsee contrastados; SVG36.459círculos aunque vista10k. QA desktop/móvil/favoritos. Producción se comprueba con acceso de servicio oficial Sites, secreto solo por entrada oculta; no exigir sesión de navegador ni relajar audiencia. Guardar recepción de despliegue en informe.

Próximo: lotes explícitos adicionales, resolver solapamientos parciales/modelos de edad y cuarentenas; formalizar actualización con retiradas/correcciones y revisión independiente. No repetir toda la cosecha para editar interfaz.
