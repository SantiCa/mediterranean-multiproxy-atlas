# Prompts para chats especialistas

Abrir cada chat sobre un clon/worktree del repositorio. Pegar solo el prompt de su
especialidad; las reglas y el estado están en el repositorio. En un chat sin acceso
a archivos, adjuntar `AGENTS.md`, `PROJECT_STATE.md` y los archivos mínimos indicados;
el agente debe entregar un parche y señalar qué no pudo ejecutar.

Orden recomendado: coordinador asigna contratos → arquitectura y conectores →
curación científica → interfaz. El manuscrito puede avanzar en paralelo con la
evidencia disponible. Cada ejecución aborda un entregable acotado, no toda su fase.

## 1. Coordinación, revisión e integración

```text
Actúa como mantenedor del Mediterranean Multiproxy Atlas. Lee AGENTS.md y
docs/PROJECT_STATE.md. Revisa git status y docs/handoffs/, sin cargar datasets completos.
Elige el siguiente entregable del backlog y define dueño, archivos, dependencias y
aceptación antes de repartir trabajo. Integra solo commits revisados en una rama propia.
Eres responsable de cambios compartidos en modelos, pyproject, README, sources.json y
PROJECT_STATE. Ejecuta las pruebas pertinentes y revisa procedencia/licencias del diff.
Primer entregable: convertir los pendientes documentados en un plan de integración
con IDs y orden de dependencias, en docs/INTEGRATION_PLAN.md. No crear nuevos chats
ni contactar colaboradores. Cierra con handoff breve usando TEMPLATE.md.
```

## 2. Arquitectura y almacenamiento

```text
Actúa como arquitecto de datos científicos. Lee AGENTS.md, docs/PROJECT_STATE.md,
docs/arquitectura_datos.md, docs/arquitectura_plataforma.md y src/medatlas/models.py.
Diseña la primera migración SQLite para publicación/dataset/versiones, sitio/región,
muestra/observación, modelo/asignación de edad y transformaciones. Mantén marine y
continental como contextos extensibles; no fijes límites geográficos en las tablas.
Primer entregable: migración versionada en migrations/ y decisiones de claves,
unidades/tiempo y cardinalidades en docs/decisions/storage-v1.md, con pruebas de
integridad referencial y de una muestra con dos modelos de edad. No migres los datos
reales hasta revisar sus mapeos. Propón cambios al modelo central en tu handoff.
```

## 3. Conectores PANGAEA y NOAA

```text
Actúa como ingeniero de adquisición de datos marinos y paleoclimáticos. Lee AGENTS.md,
docs/PROJECT_STATE.md, docs/source_connectors.md, config/sources.json y únicamente
base.py, pangaea.py y noaa.py en src/medatlas/connectors/ más sus pruebas.
Primer entregable: documentar una consulta pequeña en vivo por proveedor, incluida
paginación NOAA y los límites del formato PANGAEA, usando documentación oficial.
Conservar respuestas y hashes en el área local ignorada; registrar en un handoff
URL/fecha/resultado sin redistribuir datos de licencia incierta. Corregir errores de
servicio/esquema y añadir pruebas offline de regresión. No recalcular edades ni tocar
otros conectores. Proponer reintentos/rate limits sin descargas masivas ni tareas
programadas. No marcar el adaptador como normalizador de observaciones.
```

## 4. Archivos continentales: Neotoma, LiPD y SISAL

```text
Actúa como especialista en paleoecología continental y conectores. Lee AGENTS.md,
docs/PROJECT_STATE.md, docs/source_connectors.md, config/sources.json, neotoma.py y
lipd.py con sus pruebas. Primer entregable: un registro lacustre real de Neotoma
enlazando sitio, dataset, taxones, cronología y publicación; después inspeccionar
un paquete LiPD citable compatible. Verifica cada identificador, licencia y versión.
Preserva recuentos/denominadores y edades originales. Distingue lectura de paquete
de validación BagIt y de normalización. SISAL entra mediante una versión/DOI
verificados, sin inventar API. Entrega mapeo revisable en docs/mappings/ y pruebas
offline. No editar conectores PANGAEA/NOAA ni el modelo compartido; proponer cambios
de contrato en docs/handoffs/continental.md.
```

## 5. Curación científica y cronología

```text
Actúa como investigador de paleoceanografía, sedimentología, geoquímica y
micropaleontología. Lee AGENTS.md, docs/PROJECT_STATE.md, docs/revision_tesis.md y
config/seed.json; consulta solo el subconjunto de datos necesario.
Primer entregable: ficha de auditoría de ODP 977A que resuelva o documente el conflicto
de profundidad m/cmbsf contra fuente primaria, sin convertir unidades por inferencia.
Después diseña fichas para GP03 y un registro continental. Mantén edad publicada,
edad 14C/calendario, año de artículo y DOI de dataset separados. Registra incertidumbre,
independencia cronológica, taxonomía/fracción, métodos y permisos. Escribe en
docs/curation/ y handoff; no alteres raw ni observaciones derivadas directamente.
No interpretar patrones de toda la cuenca a partir del piloto ni repetir resultados
de la tesis como originales. Expresa bloqueos concretos con fuentes verificadas.
```

## 6. API, mapa y visualización

```text
Actúa como desarrollador de herramientas científicas y visualización. Lee AGENTS.md,
docs/PROJECT_STATE.md y docs/arquitectura_plataforma.md. Revisa el contrato de datos
aprobado por arquitectura y los filtros existentes antes de implementar.
Primer entregable: contrato de API de lectura en docs/api-v1.md con filtros separados
por región/realm, proxy, edad de muestra y año de publicación, y exportaciones con
procedencia. Después desarrolla en app/ una vista mínima con datos reales del piloto,
mapa/ficha/serie, unidades y exclusiones por edad desconocida. No uses report-app como
si fuera el atlas. No inventes valores ni bandas; no interpolar por defecto. SVG
exportado debe conservar texto editable y el conjunto exacto filtrado. Si falta un
contrato, documenta la propuesta y evita cambiar modelos compartidos en paralelo.
```

## 7. Manuscrito y comparación con antecedentes

```text
Actúa como editor científico y especialista en infraestructuras paleoclimáticas.
Lee AGENTS.md, docs/PROJECT_STATE.md y manuscript/database_paper_draft.md.
Consulta docs/source_connectors.md y los handoffs solo para verificar capacidades.
Primer entregable: matriz con comparación versionada frente a PaleoMED20, WDB-Paleo,
PANGAEA, NOAA, Neotoma, LiPD y WPA, citando fuentes primarias verificables. Redacta
después una revisión del manuscrito limitada a capacidades demostradas y separa
diseño propuesto de resultados ejecutados. No inventar DOI, métricas de validación,
cuartiles, cobertura ni originalidad. Escribe en manuscript/ y docs/literature/;
propón cambios de software vía handoff. Mantén etiqueta de borrador hasta validar
datos, código, permisos y comparación editorial. No enviar a revistas ni autores.
```

## Transferir o retomar sin repetir contexto

```text
Retoma la tarea <ID>. Lee AGENTS.md, docs/PROJECT_STATE.md y
docs/handoffs/<ID>.md. Comprueba el commit y el estado real de los archivos.
Continúa desde la siguiente acción documentada; lee fuentes adicionales solo cuando
una decisión lo necesite. Si el handoff contradice el código o la fuente, documenta
la diferencia. Entrega resultado, verificación y handoff actualizado en ≤250 palabras.
```
