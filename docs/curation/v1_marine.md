# V1: ampliación marina SST con datos reales

Revisión/acceso: 28-10-2026. Entregable de investigación en `data/interim/v1_marine/`:
`marine_sst.json` contiene **cinco nuevos sondeos y 197 valores cuantitativos**;
`raw/*.tsv` conserva bytes originales; `fetch_and_curate.py` reproduce la adquisición;
`audit_staging.py` comprueba cada valor/edad/localizador y los hashes.
Estos staging files están ignorados por Git: el integrador debe publicar una
selección curada/licenciada y su código de importación, sin forzar todo interim.

## Registros adquiridos

| Sondeo | DOI del dataset | Coordenadas (N/E) | Profundidad agua | N | Rango archivado ka BP | Año artículo / dataset |
|---|---|---|---:|---:|---|---|
| BS79-33 | [10.1594/PANGAEA.438371](https://doi.pangaea.de/10.1594/PANGAEA.438371) | 38.262 / 14.030 | 1282 m | 18 | 0.86–11.00 | 2001 / 2001 |
| BS79-38 | [10.1594/PANGAEA.438379](https://doi.pangaea.de/10.1594/PANGAEA.438379) | 38.412 / 13.577 | 1489 m | 36 | 0.87–11.34 | 2001 / 2001 |
| ODP 160-967D | [10.1594/PANGAEA.433068](https://doi.pangaea.de/10.1594/PANGAEA.433068) | 34.0708 / 32.7256 | 2552 m | 48 | 0.20–11.14 | 2000 / 2000 |
| M25/4-KL11 | [10.1594/PANGAEA.438794](https://doi.pangaea.de/10.1594/PANGAEA.438794) | 36.745833 / 17.7175 | 3376 m | 44 | 0.15–11.16 | 2000 / 2000 |
| AD91-17 | [10.1594/PANGAEA.438366](https://doi.pangaea.de/10.1594/PANGAEA.438366) | 40.870 / 18.636 | 844 m | 51 | 1.99–11.37 | 2001 / 2006 |

Con MD95-2043 de la semilla anterior (97 valores), hay **seis localizaciones y 294
valores de SST de alquenonas comparables en cuanto a unidad/calibración declaradas**.
HER-GC-ALB2 Mg/Ca-SST se mantiene en otro grupo de compatibilidad y no se mezcla
automáticamente con estas reconstrucciones de alquenonas.

## Evidencia y artículos

Los cinco TSV declaran °C, `SST (1-12)` (media anual) y calibración de UK'37 según
Müller et al. (1998), DOI [10.1016/S0016-7037(98)00097-0](https://doi.org/10.1016/S0016-7037(98)00097-0).
Se verificaron columnas/cabeceras, licencia CC-BY-3.0 y vínculo nativo al artículo:

- BS79-33/38: Cacho et al. (2001), *Variability of the Western Mediterranean sea surface temperatures during the last 25 000 years and its connection with the northern hemisphere climatic changes*, DOI [10.1029/2000PA000502](https://doi.org/10.1029/2000PA000502). [Serie depositada y abstract](https://doi.pangaea.de/10.1594/PANGAEA.735765). El resumen contrasta reconstrucciones de alquenonas de un transecto W-E e incluye el Tirreno; el PDF institucional de Ifremer fue localizado pero su lectura completa devolvió 403.
- 160-967D/KL11: Emeis et al. (2000), *Temperature and salinity variations of Mediterranean Sea surface water over the last 16,000 years from records of planktonic stable oxygen isotopes and alkenone unsaturation ratios*, DOI [10.1016/S0031-0182(00)00053-5](https://doi.org/10.1016/S0031-0182(00)00053-5). [Serie depositada con resumen y datasets](https://doi.pangaea.de/10.1594/PANGAEA.735959).
- AD91-17: Giunta, Emeis y Negri (2001), *Sea-surface temperature reconstruction of the last 16,000 years in the Eastern Mediterranean Sea*, DOI [10.13130/2039-4942/5447](https://doi.org/10.13130/2039-4942/5447). El dataset es de 2006 y declara relación `Related to`, no suplemento original de 2001. [Registro primario](https://doi.pangaea.de/10.1594/PANGAEA.438366).

**Alcance de contraste:** se revisaron registros primarios, resúmenes y las relaciones
artículo-dataset. No se afirma una auditoría completa de todos los protocolos de
laboratorio, la cronología, los suplementos de artículos o sus figuras. La
calibración se atribuye a los metadatos archivados de PANGAEA; una versión depositada
puede no reproducir todas las versiones/calibraciones de una publicación histórica.

ODP160-967D y KL11 advierten expresamente que el depósito muestra **solo un subconjunto
de la versión publicada**. No asignarles los 16 ka del título/resumen del artículo:
las edades descargadas terminan cerca de 11.1 ka. El campo `source_comment` y la
lista de `limitations` conservan esa advertencia.

## Tiempo, comparación y normalización

La columna nativa es `Age [ka BP]`; se retiene numéricamente, sin recalibración ni
conversión de 14C a calendario. Las cronologías y sus incertidumbres no han sido
auditadas de forma independiente. No atribuir bandas de edad inexistentes.

Grupo explícito: `sst_alkenone_mueller1998_annual`. Todos los registros nuevos
preservan `calibration`, `calibration_doi`, `calibration_source`, `seasonality`,
`compatibility_group`, fuente/DOI, fila/línea/columna y SHA-256. La unidad nativa
compatible permite un mapa de SST física en °C, pero no elimina diferencias
ecológicas, estacionales ni de preservación entre testigos.

Si la aplicación ofrece z-score por sondeo sobre referencia 0–20 ka:

1. Usar solo datos reales dentro de referencia, exigir al menos cinco puntos y SD>0.
2. Guardar/mostrar N, media, SD, rango efectivo cubierto y convención de SD (poblacional o muestral); no usar estadísticos del intervalo móvil como referencia que cambie sin aviso.
3. Mostrar que z es **anomalía relativa de cada sondeo**: elimina su media y amplitud de referencia, así que ya no representa el gradiente espacial físico de temperatura.
4. Aquí la referencia 0–20 ka se calcula solo sobre cobertura disponible, distinta entre testigos (aprox. 0.15/1.99–11.37 ka). Ofrecer un periodo común 2–10 ka en futuras comparaciones y análisis de sensibilidad.
5. No transformar a cero los sitios sin muestras en el intervalo seleccionado ni rellenar usando la edad más próxima sin política explícita.

Una agregación por intervalo debe indicar N y amplitud de edades realmente
muestreadas. La media aritmética de muestras representa el muestreo disponible;
con resolución irregular no equivale a una media temporal integrada. Evitar
representar superficies continuas por toda la cuenca con seis sitios dispersos;
los puntos coloreados tienen soporte local, cualquier interpolación requiere
etiqueta exploratoria y límites de distancia/soporte y tierra/océano.

## Diagnóstico HTTP 400 PANGAEA

`header_diagnosis.json` documenta cuatro lecturas acotadas del mismo URL público
`https://doi.pangaea.de/10.1594/PANGAEA.438816?format=textfile`:

| Perfil | Resultado |
|---|---|
| User-Agent simple, sin Accept | 200; 3543 bytes |
| User-Agent legacy, sin Accept | 200; 3543 bytes |
| User-Agent simple, Accept `text/tab-separated-values` | 400 |
| User-Agent simple, Accept múltiple TSV/text | 400 |

Ambas respuestas 200 coinciden con el hash histórico de la semilla
`73edaf96101ea2f9ec14f61503b4cc406f09c05cc383adc276dbca33304e6531`.
Recomendación al integrador: permitir `accept=None` en el cliente HTTP y omitir
ese header para PANGAEA `?format=textfile`. No es necesario inventar un endpoint.
No se atribuye la causa del 400 al servidor o a un proxy sin evidencia adicional.
