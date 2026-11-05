# CUR-READING-16: ocho entidades Reading v3 de diez revisadas

- Estado: validado para integración en main; Sites pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026.
- Rama/base: relevo, a64d1f5. Registro 50c7365; commit funcional cd48d71; cierre posterior en git log.
- Archivos: build_forest_pollen_v16.py, pollen_v16_sources.json, test_forest_pollen_v16.py, atlas-v16.json, quantitative_v16_release.json; prueba común v10 parametrizada por tamaño de contrato; estado/relevo.
- Resultado: PLAESTANY, Manaderos core, PozoN_2015 core, Laguna de Rio Seco core 1, LdlM 10-02, LdlMo composite, PENANEGR y LAGOA_CO. 473 muestras, 48 series y 2.838 valores nuevos. Total 251/1.942/967.990, 1.000 grupos; v16-cc875bfb999.
- Decisiones: parser v9, ensamblador v10 y originales por hash reutilizados sin cambios. Mantiene seis variables, suma de 205 taxones, CC BY 4.0, ceros, edades BP negativas e incertidumbres originales sin reinterpretación. Polen PozoN_2015 conserva 41 filas: no hereda exclusiones del archivo de carbón.
- Auditoría: Armena tiene once sumas nulas entre 53 muestras; Estanya Catena dos entre 92. Entidades completas retenidas con filas originales explícitas. Cierre con ocho admitidas de diez candidatas, sin reemplazar faltantes ni interpolar.
- Evidencia: 120 pruebas Python, 15 Node; snapshot/check-snapshot coteja 967.990 valores, 1.002 archivos, máximo 2,3 MiB. Sin cuarentenas de admisión ni solapamientos numéricos parciales detectados. Vectores completos auditados; padre íntegro. Sin consultas remotas; originales verificados localmente.
- Límites: proximidad archivada como cribado; no certifica independencia física exhaustiva. Bloqueos previos conservados. 97/122 entidades incorporadas, 25 restantes pendientes de revisión dirigida. Sin compilación ni publicación.
- Siguiente: rol 04 publica main con atlas-v16.json tras regenerar/verificar snapshot y compilar. Próximo lote, CANDIEIR e identidades/costa según RELEVO; producción sigue en v13.
