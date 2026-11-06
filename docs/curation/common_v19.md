# CUR-COMMON-19: proxies comunes y compuestos publicados

06-11-2026. Padre atlas-v18.json, inmutable. Contrato scripts/importers/common_v19_sources.json; extracción scripts/build_common_v19.py. Esta tanda sigue la nueva prioridad de densidad espacial, reconstrucciones publicadas e interpretación explícita. No se afirma cobertura mundial exhaustiva.

## Resultado y formato

38 series y 5.182 valores nuevos en ocho entidades de seis datasets PANGAEA. Dos testigos nuevos de Marmara comparten coordenadas: una ubicación, sin tratarlos como dos vecinos independientes. Se enriquecen seis registros existentes mediante identidad de evento PANGAEA y posición compatible, sin modificar metadatos ni observaciones del padre.

La release v19-c4262530e6b contiene 260 registros, 2.016 series y 974.983 valores. Se mantiene exactamente la estructura anterior: campos existentes de registros/series y nueve celdas por observación. Nombre en proxy/label/comparison_parameter_name; unidades en unit/original_unit; variable ambiental y restricciones en qc_notes. No se añaden columnas ni campos a la base.

| Proxy publicado | Variable interpretada o reconstruida | Unidad preservada |
| --- | --- | --- |
| δ18O de G. bulloides, C. pachyderma y C. lobatulus | Señal hidrográfica: temperatura y composición isotópica del agua/volumen de hielo; no temperatura o salinidad aisladas | ‰ PDB |
| δ13C de las mismas especies | Ciclo del carbono y masas de agua; no reconstrucción directa de oxígeno | ‰ PDB |
| UK′37, TEX86 y LDI | Índices moleculares relacionados con temperatura; la conversión cuantitativa requiere calibración específica | Adimensional, archivo «sin unidad» |
| BIT | Aporte relativo de GDGT ramificados/terrestres y control de interpretación de TEX86; no precipitación cuantitativa | Adimensional |
| SST por UK′37, TEX86, LDI o MAT/SIMMAX28 | Temperatura publicada, anual o estacional según parámetro y método | °C |
| Producción exportada por MAT/SIMMAX28 | Paleoproductividad marina reconstruida, anual/primavera/verano según serie | g m⁻² año⁻¹, archivo g/m**2/a |

## Contratos científicos

- [Marmara, PANGAEA.853815](https://doi.pangaea.de/10.1594/PANGAEA.853815): UK′37/TEX86/LDI y SST publicadas. Calibraciones de Prahl–Wakeham, Kim y Rampen separadas. Desviaciones estándar adyacentes conservadas en la celda de incertidumbre del valor, sin inventar error de calibración. Edades estimadas de la fuente; no son cronologías recalibradas aquí.
- [Mar Negro, PANGAEA.854722](https://doi.pangaea.de/10.1594/PANGAEA.854722): BIT, TEX86 y temperatura rotulada SST para 0–200 m. Contexto separado de superficie estricta; no se incorpora la reconstrucción lacustre LST. Se preserva el contexto Saalian–Eemian y la limitación de aportes terrestres.
- [MedSeA-S3-c1, PANGAEA.939417](https://doi.pangaea.de/10.1594/PANGAEA.939417): UK′37 y SST archivadas. CE y BP concuerdan numéricamente con referencia 1950. Calibración específica no declarada en la columna: SST aislada por dataset, sin atribuir una fórmula no verificada.
- [MD99-2339, PANGAEA.733103](https://doi.pangaea.de/10.1594/PANGAEA.733103) y [MD95-2040, PANGAEA.743087](https://doi.pangaea.de/10.1594/PANGAEA.743087): temperaturas y producción exportada por análogos de foraminíferos. Se seleccionan los estimadores ponderados por distancia; no se suman alternativas no ponderadas como nuevas observaciones independientes. Las desviaciones sin atribución inequívoca al estimador permanecen en el original, sin asignación inventada.
- [GC-01A-PC/TC, PANGAEA.966665](https://doi.pangaea.de/10.1594/PANGAEA.966665): especies y corrección «corr» explícitas. La alternativa δ18O «corr+0.64» no se añade como réplica. Se conserva ‰ PDB, sin cambio implícito a VPDB. Dos series de C. lobatulus del TC tienen solo dos valores: se preservan, sin interpolación ni apoyo espacial inferido.
- PANGAEA.939418 queda retenido: dos eventos en metadatos sin columna Event. No se atribuye la tabla a c1/c3 a partir del título o de coordenadas coincidentes.

Los índices de biomarcadores y las funciones de transferencia de esta tanda cumplen la prioridad de compuestos publicados. No se calcula CIA a partir de cuentas XRF ni se transforma U/Th de datación en proxy redox. CIA, paleoredox y razones XRF de otras fuentes requieren contratos propios de materiales, concentraciones/óxidos y normalización.

## Cobertura y validación

En la categoría nativa Temperatura, las ubicaciones fechadas distintas pasan de 26 a 30; Isótopos estables, de 34 a 35. Son recuentos de familias nativas con coordenadas a cuatro decimales, no cobertura SST exclusiva, equivalencia entre métodos ni validación de una interpolación. Comparaciones por proxy/método/unidad y restricciones de contexto se conservan.

Fuentes TSV/XML y metadatos de artículos fijados por hash; se reutilizan los dos originales de MedSeA disponibles. Licencias CC BY 3.0/4.0 por recurso; año del dataset y del artículo no se confunden. Cuando la relación bibliográfica es ambigua, año/DOI de artículo siguen desconocidos, con referencia nativa conservada.

142 pruebas Python aisladas por archivo, sin omisiones; 36 Node, tsc/build y snapshot íntegro: 974.983 valores, 1.017 grupos y 1.019 archivos. Auditorías sin errores estructurales. Pruebas de celdas/edades/incertidumbre/eventos, esquema intacto y duplicación por vector completo del mismo registro/unidad, incluso entre IDs de proxy distintos. Avisos conocidos del padre conservados; nuevo par espacial coincidente de Marmara explícito. Evidencia en reports/common_v19_validation.json y reports/quantitative_v19_release.json.

Publicación reservada al rol 04. No se despliega el Site en este cierre.
