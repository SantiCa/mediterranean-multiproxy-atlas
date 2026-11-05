# Auditoría científica v17 y QC al publicar (V30)

- Agente: Claude · 05-11-2026 · semilla atlas-v17-c6564e1246e (256 registros, 1.972 series, 971.380 valores).
- Herramienta: `scripts/audit_science.py <semilla> [--json]` (solo lectura). Falla solo por errores de integridad (recuentos, no finitos, huérfanas, ids o unidades por grupo); el resto son avisos. Se ejecuta en el despliegue antes del snapshot.
- Resultado: 0 errores de integridad. Avisos:
  1. **Corregido (QC)**: Mondsee MO-05, PANGAEA.929110 (19 series): «Age [ka BP]» está en ka CE (título 1500 BCE–500 CE; columna «Age [a AD/CE]»). Se publicaba en -1,5…0,5 ka BP. Ahora ka BP = 1,95 − ka CE (1,45–3,45 ka BP); `age_original` intacta.
  2. **Retenidas (QC)**: 6 series pangaea6 idénticas a otras del mismo sondeo (MD99-2343 ×3, MD95-2043 Quercus ×2, HER_GC_UB06 ×1).
  3. Pendiente de revisar (rol datos): edades ligeramente futuras de techo de testigo en NDT-6-2016 (-0,14 ka) y MD95-2040 (-0,0895 ka), tal como están archivadas; 40 series con inversiones de edad en orden de fuente (p. ej. PANGAEA.253132 color, 68/2683); 7 pares de registros con mismas coordenadas (U1389B/C, GC-01A PC/TC…); 56 series de polen Reading todo-cero (taxón ausente, válido).
- Mecanismo: `config/qc_corrections.json` + `app/atlas-web/lib/qc-corrections.mjs`, aplicado por `snapshot.mjs` y `check-snapshot.mjs` sobre una copia de la semilla (no la modifica). Idempotente; falla si una retención apunta a una serie inexistente. La web lo muestra en «Fuentes».
- Para el rol de datos: incorporar 1 y 2 en la próxima release (v18) y vaciar las entradas correspondientes de `config/qc_corrections.json`.
- Pruebas: 30 Node (incluye tests/qc-corrections.test.mjs), tsc sin errores, check-snapshot celda a celda (969.501 valores), build vinext OK. Python: fallo previo `test_forest_pollen_v15` por falta de iberia.csv local (requiere --fetch), ajeno a este cambio.
