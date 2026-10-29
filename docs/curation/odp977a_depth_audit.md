# CUR-ODP977A — auditoría del marco de profundidad

Fecha: 29-10-2026. Dataset [PANGAEA.921230](https://doi.pangaea.de/10.1594/PANGAEA.921230), ODP Hole161-977A. **Resultado científico: unidad m resuelta por definición explícita del artículo, sin conversión numérica.** El marco es profundidad corregida, no profundidad de agua ni mbsf de perforación intercambiables automáticamente.

## Evidencia primaria localizada

| Fuente | Declaración relevante | Alcance |
|---|---|---|
| PANGAEA921230, parámetro3 | `Depth corr [m]`, método Depth correlation/correction, comentario `[cmbsf]` | La unidad declarada es m; el acrónimo aislado motivó la advertencia histórica |
| [González-Lanchas et al., 2020](https://doi.org/10.1016/j.quascirev.2020.106520), apartado3.1 y tabla1; [versión aceptada institucional](https://ricerca.uniba.it/retrieve/28f431ac-919a-4bd9-ab13-86998b1abe1e/Gonza%CC%81lez-Lanchas%20et%20al.%2C%202020_QSR_preprint.pdf) | La tabla define «Cmbsf: corrected meters below seafloor»; el apartado3.1 sitúa el intervalo entre58,64 y67,49 metros corregidos | Resuelve el significado en ESTE estudio; no es una definición universal del acrónimo |
| [ODP Leg161, Site977, informe preliminar](https://www-odp.tamu.edu/publications/prelim/161_Prelim/OP977.HTML); [Initial Reports, capítulo7](https://www-odp.tamu.edu/publications/161_IR/VOLUME/CHAPTERS/ir161_07.pdf) | Distingue mbsf, mbsl y mbrf; profundidad de agua1984m y recuperación mayor del100% en el tramo APC | Confirma que agua, perforación y recuperación son magnitudes/marcos diferentes; no suministra por sí solo la transformación posterior de los autores |

El artículo explica que se ajustó la recuperación de10,01m del core8 y10,03m del core7 a9,5m. Se conserva esa explicación, pero NO se deducen automáticamente desplazamientos de secciones ni una función de conversión a la profundidad ODP: exigiría la tabla de correspondencias y la convención exacta de límites.

## Comprobación del archivo conservado

TSV original: `data/raw/pangaea/921230.tsv`, SHA-256 `b8739412ed7d26be05ca0d9d4c9bab807dab4bf2c8edb33d755071037c3d2dd5`. Hay181filas de muestra, profundidades58,64–67,49 en la columna declarada m y edades375,97–429,69ka BP. Fila1: muestra161-977A-7H-6,4-6, profundidad58,64. No se ha alterado ningún valor, edad, incertidumbre ni fila original.

## Decisión y límites

- Interpretación admitida: metros corregidos bajo el fondo, conforme al artículo y la cabecera. **No dividir ni multiplicar por100.**
- La bandera histórica `depth_header_m_vs_metadata_comment_cmbsf_conflict` registraba una sospecha, no prueba de centímetros. Esta ficha resuelve la unidad; sigue siendo necesario conservar el comentario nativo y la trazabilidad.
- Prohibida la unión automática a mbsf/mcd de otras tablas por igualdad de número, etiqueta de core o semejanza de profundidad. No confundir con1984m de columna de agua.
- Las edades publicadas permanecen disponibles para exploración por edad. El apartado3.2 describe correlación de SST con U1313; esa dependencia impide usar después su sincronía como prueba independiente.
- Las semillas históricas versionadas no se reescriben. La resolución deberá aparecer como anotación de curación en la siguiente release/interfaz, conservando el aviso original como historial; no se ha cambiado todavía la aplicación.

## Cierre y reproducción

La definición se verifica en el apartado3.1 del editor y en la tabla1 indexada del manuscrito aceptado. La descarga directa del manuscrito institucional respondió HTTP403; no se eludió el bloqueo ni se afirma haber leído ese PDF localmente. El informe ODP completo y el preliminar sí quedaron archivados por hash. El contexto de profundidad de agua aparece en las páginasPDF1,2,5,10,14 y32 del capítulo. La limitación de acceso al manuscrito no convierte en ambigua la definición explícita del editor.

El TSV actual descargado el29-10-2026 es idéntico byte a byte al conservado. Hashes, URLs, fechas y localizadores: data/provenance/odp977a_audit_retrievals.json y reports/odp977a_depth_audit.json. Originales en data/raw/odp977a_audit/, ignorado. La resolución versionada está en config/curation_assertions.json; es una anotación, no una reescritura de semilla ni una nueva escala.

Reproducción: python scripts/audit_odp977a_depth.py, offline con caché; añadir --fetch para recuperar los recursos explícitos ausentes. La extracciónPDF usa pypdf (observado6.21.4), dependencia opcional de investigación. Las pruebas comprueban que no se requiere conversión y que las181profundidades de ambas series v3 siguen exactamente iguales a las celdas nativas.

**CUR-ODP977A cerrada:** unidad resuelta; transformación del marco corregido a mbsf no implementada ni inferida; aplicación sin cambio numérico. La anotación deberá incorporarse a la próxima interfaz de control de calidad.
