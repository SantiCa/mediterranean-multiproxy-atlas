# Estado breve del proyecto

Actualizado: 28-10-2026. Repositorio: `SantiCa/mediterranean-multiproxy-atlas`, privado.
Usar `git log -1` para el commit efectivo; este archivo no sustituye el estado Git.

## Disponible

- Piloto PANGAEA: 5 conjuntos, 11 series, 2.684 valores seleccionados (2.646 con edad archivada, 38 solo profundidad). Datos numéricos en `data/processed/`; originales locales en `data/raw/`, recuperables por script.
- Paquete Python `medatlas` instalable. Clientes de lectura PANGAEA, NOAA, Neotoma, DataCite y lector local LiPD. Mantienen respuestas nativas; no implementan una normalización completa.
- Arquitectura relacional/global propuesta, dataclasses iniciales, scripts de semilla, filtros y figuras SVG. No hay todavía base relacional, API del atlas ni mapa interactivo del atlas implementados.
- Borrador de artículo en `manuscript/`, revisión de tesis y antecedentes en `docs/`, informe de viabilidad en `reports/`.
- Guía común `AGENTS.md`, entrada `CLAUDE.md`, roles/prompts en `docs/CHAT_PROMPTS.md`, handoffs cortos en `docs/handoffs/`.

## Verificación realizada

- Instalación editable correcta en Windows/Python 3.14; 22 pruebas locales pasan, incluidas 8 de integridad contra originales de la semilla.
- Suite offline sobre conectores, conservación/hash/bloqueo, paquete de entrega y sincronización de visor. CI configurada para Windows/Linux y Python 3.10/3.14; consultar Actions para su resultado efectivo.
- Consulta acotada por proveedor en `reports/live_source_check.json`: NOAA, Neotoma y DataCite devolvieron JSON; PANGAEA devolvió HTTP 400. Eso mide recuperación, no fidelidad científica ni normalización de todo el esquema.
- LiPD comprobado con fixture controlado; falta paquete científico real/versionado. No se ha validado BagIt ni migrado cronologías.

## Siguientes entregables

| ID | Dueño sugerido | Entregable / dependencia |
|---|---|---|
| SRC-01 | PANGAEA/NOAA | Diagnosticar HTTP 400 en PANGAEA con documentación/servicio oficial; verificar paginación y archivo NOAA sin descargas amplias |
| DB-01 | Arquitectura | Primera migración SQLite con claves y marcos de tiempo/profundidad versionados |
| CON-01 | Continental | Registro Neotoma lacustre + paquete LiPD real; mapeo de taxones, muestras, cronologías y permisos |
| SCI-01 | Curación | Resolver profundidad ODP 977 m/cmbsf y auditar disponibilidad/licencia GP03 |
| API-01 | API/visualización | Contrato de consulta/exportación tras DB-01 y mapeos revisados |
| PUB-01 | Manuscrito | Matriz de antecedentes/versiones y contribuciones demostradas; sin reclamar reconstrucción nueva |

## Límites y decisiones pendientes

El código aún no tiene licencia de distribución seleccionada. Las licencias de cada dataset son independientes. Los clientes no tienen aún un sistema general de reintentos/backoff ni un validador completo de esquemas de proveedor. `preserve_raw` falla explícitamente si otro proceso escribe el manifiesto. La semilla es intencional y no representa toda la cuenca. La arquitectura de regiones y las extensiones de taxonomía/cronología están diseñadas, todavía no implementadas en almacenamiento. El visor local `report-app/` es auxiliar, ignorado y requiere recompilación propia.

No cargar la tesis completa para desarrollo rutinario. Consultar `docs/revision_tesis.md`; acudir a capítulos/páginas concretos cuando una pregunta científica lo requiera.
