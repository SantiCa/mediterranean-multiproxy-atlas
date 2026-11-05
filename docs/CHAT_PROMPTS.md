# Chats del atlas y prompts breves

Actualizado el 05-11-2026. Los cuatro chats comparten este repositorio y trabajan por relevo, uno activo cada vez. La rama y la siguiente acción están en docs/RELEVO.md.

## Elección del chat

| Chat | Modelo recomendado | Esfuerzo | Entregable por activación |
| --- | --- | --- | --- |
| Atlas 01 · Curación de datos | GPT-6.1 Sol | Medio | Hasta 10 entidades de una fuente y un grupo de proxies existente |
| Atlas 02 · Auditoría científica | GPT-6.1 Sol | Alto | Una duda concreta de edad, unidad, denominador, taxonomía o duplicación |
| Atlas 03 · Programa y pruebas | GPT-6.1 Terra | Medio | Una mejora funcional o un fallo reproducible |
| Atlas 04 · Publicación | GPT-6.1 Terra | Bajo | Una publicación de main ya validado en el Site existente |

Usar velocidad Standard. Santiago confirmó esta asignación y se aplicó a los cuatro chats mediante sus ajustes de modelo y esfuerzo. El texto de un prompt por sí solo no cambia el selector. En futuros chats nuevos, revisar el modelo heredado. La velocidad Standard se recomienda para el selector, sin modificar la configuración global de la cuenta.

Para código rutinario ya descrito por un contrato, se puede probar Luna con esfuerzo medio. Mantener Sol para decisiones científicas. Revisar el resultado con los mismos criterios de aceptación. Escalar solo cuando quede una duda concreta que el modelo elegido no resuelva.

Guía contrastada con [OpenAI Docs sobre selección de modelos](https://developers.openai.com/api/docs/guides/model-selection) y [consumo](https://learn.chatgpt.com/docs/pricing), consultadas el 05-11-2026. El ahorro debe comprobarse con el consumo real de la cuenta.

## Forma de trabajar común

- Abrir un solo chat para ejecutar cada paso. El siguiente retoma desde Git y RELEVO. Los chats preparados esperan una orden de activación.
- El repositorio está en la subcarpeta mediterranean-multiproxy-atlas del proyecto Volviendo a publicare. Comprobar la ruta antes de cualquier comando Git.
- Al activarse, seguir AGENTS.md, hacer fetch y retomar relevo. Leer PROJECT_STATE y el handoff pertinente, consultando primero sus apartados actuales.
- Mantener los criterios científicos de AGENTS.md. Una duda sin resolver queda marcada y trazable. Conservar originales, licencias, unidades, cronologías y denominadores.
- Reutilizar importadores y descargas por hash. Obtener conteos y anomalías con scripts. Mostrar solo las filas necesarias para decidir.
- Repetir una búsqueda bloqueada cuando haya una pista o acceso nuevo. Consultar primero las fuentes y fallos ya documentados. En auditorías bibliográficas, empezar por hasta cinco fuentes primarias pertinentes.
- Ejecutar las comprobaciones exigidas por AGENTS y las pertinentes al cambio. Repetirlas cuando cambien sus entradas o aparezca un fallo. La revisión del mismo lote se conserva en el handoff.
- Actualizar RELEVO y hacer commit/push tras cada paso que funcione. Al cerrar, handoff, pruebas y merge según AGENTS. Conservar este relevo también al alternar con Claude.
- Las activaciones de datos, ciencia y programa preparan el cierre en Git. La publicación de ChatGPT Sites se activa en el chat 04. Una orden expresa del usuario de publicar en otro chat también autoriza esa publicación.
- Cerrar cada respuesta en unas 150 palabras con resultado, comprobación, límite y siguiente acción. Un hallazgo que requiera más explicación puede superar ese tamaño.
- Renovar el chat al terminar un lote si acumula mucho historial. Pegar solo el prompt del rol. El nuevo chat retoma el estado del repositorio.

## 01 · Curación de datos

Modelo recomendado GPT-6.1 Sol, esfuerzo medio.

Mensaje de activación reutilizable

~~~text
Sigue desde relevo. Aplica el rol 01 de docs/CHAT_PROMPTS.md. Completa hasta diez entidades de una misma fuente para proxies existentes, priorizando ubicaciones nuevas. Reutiliza contratos e importadores, revisa unidades, edades, denominadores y duplicados, y marca las inconsistencias. Cierra el lote con pruebas, handoff y Git según AGENTS. Deja la publicación de ChatGPT Sites para el rol 04.
~~~

El primer lote propuesto continúa Reading v3 con los seis parámetros de polen ya incorporados. Ver docs/handoffs/cur-pollen-monticchio.md y scripts/importers/pollen_v9_sources.json. La lista de entidades admitidas se obtiene del contrato y del catálogo mediante scripts.

## 02 · Auditoría científica

Modelo recomendado GPT-6.1 Sol, esfuerzo alto.

Mensaje de activación reutilizable

~~~text
Sigue desde relevo. Aplica el rol 02 de docs/CHAT_PROMPTS.md y resuelve una sola inconsistencia científica documentada. Revisa lo ya buscado antes de consultar fuentes nuevas. Contrasta el marco de profundidad, las edades y las observaciones con fuentes primarias. Entrega una decisión reproducible o un bloqueo preciso. Documenta cualquier corrección y ejecuta las pruebas pertinentes. Cierra según AGENTS.
~~~

Primer caso propuesto MD99-2337. Falta verificar una tabla numérica de edad y profundidad del propio sondeo. Revisar el handoff de Monticchio y el contrato ss_v8. Una nueva búsqueda necesita una pista adicional respecto de las ya registradas. Para un manuscrito, activar expresamente una sección concreta en este rol y contrastar sus afirmaciones con el código y los informes.

## 03 · Programa y pruebas

Modelo recomendado GPT-6.1 Terra, esfuerzo medio.

Mensaje de activación reutilizable

~~~text
Sigue desde relevo. Aplica el rol 03 de docs/CHAT_PROMPTS.md. Implementa una sola mejora pendiente y verificable de la interfaz. Reproduce el comportamiento actual, modifica lo necesario y comprueba el recorrido normal del usuario. Reutiliza los contratos científicos existentes. Ejecuta pruebas pertinentes y QA visual cuando cambie la interacción. Cierra con handoff y Git según AGENTS. Deja ChatGPT Sites para el rol 04.
~~~

Primera mejora propuesta, tabla de valores originales y usados con exclusión de muestras y registros. Antes de implementarla, delimitar un paso funcional que conserve trazabilidad y advierta qué columnas originales están disponibles para cada fuente.

## 04 · Publicación

Modelo recomendado GPT-6.1 Terra, esfuerzo bajo. ChatGPT/Codex gestiona Sites.

Mensaje de activación reutilizable

~~~text
Publica main validado en el ChatGPT Site existente. Aplica el rol 04 de docs/CHAT_PROMPTS.md y la skill Sites. Comprueba RELEVO y el último recibo para identificar cambios. Usa la semilla más reciente, genera snapshot.mjs y ejecuta check-snapshot.mjs antes de compilar. Conserva el acceso actual. Publica una sola versión, comprueba el resultado y guarda recibo sin secretos. Cierra según AGENTS. Si main ya está publicado sin cambios pertinentes, informa y termina.
~~~

Las cuatro API públicas se retiraron en V28. Los datos cuantitativos se sirven desde el snapshot estático. El proyecto Sites, el checkout y los límites de Mis datos constan en RELEVO. Usar las instrucciones y herramientas vigentes de Sites.

## Cuándo cambiar de rol

Datos pasa a ciencia si una inconsistencia impide la admisión. Ciencia deja una decisión o un bloqueo en el relevo. Programa interviene cuando hace falta una funcionalidad. Publicación se activa tras un cierre validado o una orden expresa del usuario. Al cambiar de chat, terminar o detener el trabajo anterior y conservar el estado en Git.
