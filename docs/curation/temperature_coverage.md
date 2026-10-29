# Cobertura de temperatura: cola verificable

29-10-2026. Prioridad: completar temperatura existente antes de ampliar familias.
`reports/temperature_coverage.json` es una **cola de fuentes**, no una colección de
observaciones ni un recuento de sondeos independientes.

La consulta explícita DataCite/PANGAEA recuperó 6.659 DOI en siete páginas de
1.000, con total estable y sin DOI repetidos. Se comprueba que un mismo punto
esté dentro de [-10,28,42,48]; los dos filtros geográficos indexados por separado
no bastan. La consulta ya no exige las palabras sediment/core, para incluir
archivos continentales. Se unen los candidatos del inventario anterior y las
fuentes cuantitativas revisadas que la búsqueda no encuentra.

Sobre la semilla v3, PANGAEA tiene 14 DOI con alguna serie de temperatura admitida,
1.878 candidatos pendientes de revisar tabla nativa, 71 ambiguos y 98 resultados
fuera del objetivo (p.ej. temperatura de pirólisis o durante la perforación).
Los 1.878 son coincidencias de metadatos, **no** 1.878 reconstrucciones confirmadas.

NOAA se revisa desde sus JSON completos por sitio/tabla/archivo: la lista resumida
de proxies del inventario pierde detalles. Hay cinco entradas con temperatura
admitida y 57 pendientes. No se suman estas entradas a los DOI PANGAEA como si
fueran sondeos; pueden ser versiones, réplicas, tablas de calibración u observaciones
modernas. Se contrasta el orden de coordenadas NOAA con sus cuatro límites.

Cada entrada guarda identificador, localizador, hash, estado, parámetros/métodos
nativos y series admitidas. Los campos no resueltos siguen nulos. La admisión de
una serie no significa haber extraído todas las columnas. Los archivos de un
borrador no se consideran revisados ni publicados. La cobertura de literatura con
metadatos ausentes o solo bounding boxes sigue abierta.

Reglas: SST, agua profunda, aire y superficie del terreno se separan. δ18O o
Mg/Ca no se convierten en temperatura sin reconstrucción/calibración publicada.
La estación, calibración, especie y dependencia cronológica deben revisarse antes
de agrupar. Compartir °C o aplicar z-score no demuestra equivalencia.

```powershell
python scripts/temperature_coverage.py --fetch  # primera descarga acotada
python scripts/temperature_coverage.py          # reproduce con caché inmutable
python -m unittest discover -s tests -p test_temperature_coverage.py -v
```

Los originales permanecen ignorados; URLs, fechas y hashes están en el informe.
El resultado puede repetirse exactamente con esas respuestas, pero no se presenta
como una cosecha completa de toda la bibliografía ni cambia la web desplegada.
