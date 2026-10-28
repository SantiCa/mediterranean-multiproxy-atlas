# Revisión técnica — 28-10-2026

Alcance: repositorio local inicialmente en `3aa7f9b`, clientes HTTP, dataclasses,
scripts de entrega/visor, pruebas, documentación y coordinación de agentes.
Esta revisión no demuestra ausencia de todos los defectos ni certifica las inferencias científicas.

## Fallos corregidos

1. **Entrega incluía material ignorado por Git.** Recorrer el directorio incluía tesis e imágenes y podía incluir entornos locales. El empaquetador ahora exporta solo archivos seguidos por Git a `medatlas-source.zip`, con manifiesto/hash. No sobrescribe el antiguo ZIP privado de viabilidad; ese archivo previo sigue siendo una entrega local con material de tesis.
2. **Visor podía seguir mostrando datos antiguos.** La sincronización cambiaba el JSON/manifest de `dist` aunque el HTML incrustaba otra ruta. Ahora actualiza solo `src/data.json`, conserva identidad e informa que hace falta recompilar. No se distribuye una supuesta compilación actualizada.
3. **Entrada ambigua a endpoints.** DOI de PANGAEA se valida y normaliza; parámetros especiales de DOI DataCite se codifican; número de página debe ser positivo.
4. **Preview NOAA permitía desactivar preview.** Se fuerza `preview=true`. Booleanos se codifican en minúsculas. Esquemas de paginación inesperados y continuaciones fuera del proveedor fallan explícitamente.
5. **Respuesta no necesariamente era dato.** JSON escalar y HTML en lugar de tabla PANGAEA se rechazan. Lecturas HTTP tienen tamaño máximo configurable y timeout.
6. **Procedencia y concurrencia.** Se verifica el hash contra los bytes, se restringen nombres de fuente/extensión y se bloquea escritura concurrente de manifiestos para evitar perder entradas.
7. **Año desconocido rompía filtros.** El año nulo se conserva y se excluye de consultas por año, sin usar cero.
8. **LiPD ambiguo se aceptaba silenciosamente.** Se requiere una única metadata.jsonld de tipo objeto y se contextualizan errores de archivo. La función sigue siendo inspección, no validación completa del estándar.
9. **Clon sin originales fallaba sin explicación en tests de semilla.** Ahora omite esa clase con instrucción de descarga; los tests offline del código funcionan sin originales. La integridad de la semilla se sigue ejecutando cuando están presentes.

## Evidencia y pendientes

Instalación editable correcta y 22 pruebas locales pasan. Los originales locales
siguen coincidiendo con los hashes y las celdas seleccionadas de la semilla.
Un clon limpio independiente pasa 14 pruebas offline; omite explícitamente la clase
de integridad de semilla hasta recuperar los originales.
Las regresiones de entrega prueban que documentos locales ignorados y archivos sin
seguimiento no entran en el ZIP. La regresión de visor verifica identidad y ausencia
de modificaciones falsas de `dist`.

Se incorporó una comprobación explícita de servicios en `scripts/check_live_sources.py`.
El informe fechado `live_source_check.json` muestra respuestas JSON de NOAA, Neotoma
y DataCite y HTTP 400 de PANGAEA. Un segundo intento PANGAEA con un Accept MIME único
también devolvió 400; no se atribuye la causa al proveedor o al cliente sin diagnóstico.
No se inventó una conexión correcta ni se recurrió a un endpoint interno.

Pendientes: resolver esa descarga PANGAEA; validación de paginación y respuestas
completas de proveedores; reintentos/rate limits; validación LiPD real; migraciones;
revisión independiente de cronología/unidades/taxonomía/licencias y licencia del código.
CI añadida: consultar Actions tras la subida para ver resultados de otras plataformas.
La ejecución [40722350578](https://github.com/SantiCa/mediterranean-multiproxy-atlas/actions/runs/40722350578)
del commit `50cc278` pasó en las cuatro combinaciones Windows/Linux y Python 3.10/3.14.

## Organización para agentes

Reglas comunes en `AGENTS.md`, entrada de Claude en `CLAUDE.md`, estado breve en
`PROJECT_STATE.md`, siete prompts con archivos/dueños/dependencias y plantilla de
handoff en `docs/`. Los comentarios añadidos explican supuestos científicos y motivos
de comportamiento; no se comenta mecánicamente cada instrucción.
