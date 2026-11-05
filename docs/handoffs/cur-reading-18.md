# CUR-READING-18: cierre tras auditoría del rol 02

- Estado: validado para integración conjunta; publicación pendiente del rol 04.
- Agente/rol: Codex / Atlas 01, 05-11-2026. Base 82917f1; pausa 7891aa1; auditoría final ab45c83; reanudación 7496c2d; paso funcional ed8366f; cierre en git log.
- Archivos: importadores v9/v10/v18, contrato pollen_v18_sources.json, pruebas v18, atlas-v18.json, informes quantitative/scientific/proxy_use_v18 y reading_v18_validation.json, QC de publicación, estado/relevo.
- Resultado: v18-cd0f8159f62; 258 registros/1.978 series/969.801 valores, 994 grupos. Armena/PEDRIDO añaden 12 series/300 valores de 50 muestras; 124 muestras originales y 57 controles auditados, 74 sumas nulas excluidas explícitamente. ELX/Estanya siguen retenidas por reservorio/agua dura.
- Conclusiones: 1.807 edades de 19 series Mondsee corregidas a BP; seis duplicados (1.879 valores) fuera de series activas, con objetos originales completos en curation_excluded_series. Tabla original fijada por hash. Ambos encabezados de edad son ambiguos: la segunda columna coincide numéricamente con años BP pese al rótulo AD/CE. Tokens intactos; transformación coherente con el intervalo publicado, sin recalibración.
- Padre: 25 excepciones declaradas en informe; restantes series y todos los registros intactos. V17 reproducida sin cambios de contenido. QC de publicación vacío porque se integra científicamente en v18; semillas antiguas requieren QC histórico.
- Evidencia: 136 Python aisladas por archivo, cero omisiones; 36 Node, tsc/build y snapshot íntegro (969.801 valores, 996 archivos). Auditorías sin errores estructurales; avisos conocidos conservados. Recibo reading_v18_validation.json.
- Siguiente: integrar según AGENTS; rol 04 publica main/atlas-v18.json tras regenerar/verificar snapshot y compilar. No publicar v18 provisional. Creador del rol 02 y escala del rol 03 conservados; sin despliegue en este cierre, producción v13.
