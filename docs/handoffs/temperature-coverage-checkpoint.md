# PROXY-COVERAGE-TEMP — checkpoint, no cierre

29-10-2026, Codex. Base53fa4a3; inventario35b7aac. Rama de conservación
`codex/temperature-coverage-checkpoint`, subida al remoto. **Puntero vivo:
origin/relevo/docs/RELEVO.md**, no este borrador. No fusionar ni desplegar sin
reconciliar el turno de trabajo: origin/relevo recibió1e9668c,77eee66,a51bb3c
durante la sesión (Cloudflare). Push de35b7aac rechazado; ningún force-push.
Se preguntó al usuario si Claude había terminado. No sobrescribir su workflow.

Entregable: script/cola/informe y cuatro pruebas de cobertura, documentados en
docs/curation/temperature_coverage.md. 47Python y14Node locales correctas.
Sin cambios de valores, semilla ni web; online sigue v3.

Originales ignorados en data/interim/temperature_batch1, con recibos por recurso:

-921234:172 filas SST,375,97–429,69ka; mismo evento161-977A existente. Reutilizar
su record_id; no añadir segundo sondeo. Artículo2020, dataset2024. Profundidad
cmbsf en metros corregidos, sin factor100; cronología ajustada mediante SST.
-939417/939418:33/42filas MedSeA;955015:47filas. Las edades CE/BP coinciden
exactamente en todas las parejas presentes. Conte2006 explícito en955015 XML,
y sección3.3 del artículo primario103549 para los otros dos. Padre955024 aún
enlaza publicación «in review NN»: no atribuir automáticamente el artículo2021
como fuente original de los datos2023.
-866949:32filas,9,467–15,893ka. Dos columnas con etiqueta idéntica, conjuntos
de entrenamiento Norteamérica/Suecia distintos. Leer por índice ordinal; no
DictReader. Metadato advierte cronología2008 mejorada en2011/2012; conservar aviso.
-925876:161filas de temperatura mensual, SIN edad. Mantener pendiente de enlace
documentado al modelo; no inventar ni trasladar edades por profundidad sin revisión.
-NOAA21992:216filas (Gol-Ho1B19,KSGC-31197), Conte2006, CE. Archivo latin1.
Sin coincidencias exactas edad/valor con las cuatro SSTNOAA32914 actuales.
Localización NOAA conjunta de dos cores: no inventar dos coordenadas independientes.
-NOAA22582:56filas. pla2004-pyrenee y versión PAGES2k tienen los mismos cinco
campos en todas las filas: registrar duplicación, no sumar muestras. Archivo
principal: BOM UTF8 seguido de texto latin1; conservar bytes y documentar decoder.
Anomalía invierno/primavera, no SST ni temperatura absoluta. Año de artículo por
resolver antes de admitir. Informe local adicional en ../outputs/temperature_batch1_source_review.json.

Siguiente: confirmado el relevo, integrar commit de cobertura sin tocar workflow,
documentar hallazgos en contratos versionados y extraer primer lote. No afirmar
temperatura completa: miles de coincidencias son metadatos, no series confirmadas.
