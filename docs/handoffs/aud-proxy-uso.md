# AUD-PROXY-USO: auditoría y creador de proxies

- Estado: funcional, comprobado y guardado en relevo; integración/publicación pendientes.
- Agente/rol: Codex, Atlas 02; ampliación expresamente solicitada por Santiago. Cierre solicitado con «termina».
- Base: eb85664; registro c90043b; primer paso f4a4820. El commit ajeno 7891aa1 guarda CUR-READING-18 provisional en pausa; se conserva.
- Archivos: `scripts/audit_proxy_use.mjs`, informes `reports/proxy_use*_audit.json`, `docs/curation/proxy_use_audit.md`, `lib/proxies.mjs`, nuevo motor/componentes/pruebas de derivados, selector, página, CSV y vocabulario de descubrimiento.
- Resultado: auditoría completa de celdas v17 y adicional v18 provisional sin errores estructurales; 6.615 valores sin edad, siete grupos de coordenadas coincidentes. No equivale a validación integral de cronologías ni duplicados parciales.
- Correcciones: registros únicos visibles; familias coherentes; OI Rock-Eval fuera de Foraminíferos; nueve SST sin estación separadas de anual; porcentajes polínicos sin contexto no se agrupan por nombre. Asociaciones publicadas accesibles.
- Creador local: sumas, A/B, 100×A/(A+B), opción multisondeo compatible; identidad de tabla/muestra, denominadores, hashes, originales/exclusiones, recetas JSON y CSV trazables. Sin interpolación ni incertidumbre propagada; taxones disjuntos confirmados por usuario.
- Evidencia 05-11-2026: 133 Python, 34 Node, tsc/build y snapshot v17 correctos; QA escritorio Abies+Alnus: 102 tablas/7.110 valores, 59 sitios/961 valores en 6–8 ka. Captura ignorada en outputs. Sin QA móvil ni despliegue.
- Siguiente: rol 01 finaliza CUR-READING-18; después merge `relevo`→`main` y publicación por rol 04. No fusionar ahora el lote provisional. Documentación científica y límites en el informe de curación.
