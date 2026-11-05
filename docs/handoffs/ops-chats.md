# OPS-CHATS

05-11-2026 · Codex · cierre de organización de chats

Se actualizó docs/CHAT_PROMPTS.md con cuatro roles, modelos, esfuerzos, límites de lote, prompts de activación y reglas de relevo secuencial. Los ocho prompts antiguos contenían primeros entregables ya completados y referencias al trabajo paralelo. La guía nueva enlaza el estado científico actual.

Se crearon cuatro chats locales en el proyecto Volviendo a publicare, con la ruta del repositorio real explícita en sus prompts. El primer mensaje solo pide esperar activación. El modelo heredado gpt-5.5 falló por incompatibilidad con la cuenta. Santiago confirmó explícitamente Sol para curación/auditoría y Terra para programa/publicación. Se aplicaron los modelos y esfuerzos a los mismos chats mediante send_message_to_thread. Los cuatro finalizaron correctamente con «Preparado. Esperando activación.», sin herramientas ni cambios del repositorio.

- Atlas 01 · Curación de datos. gpt-6.1-sol, esfuerzo medium. Chat 01a1aab3-0c68-71d0-b506-f1c40bc763ec.
- Atlas 02 · Auditoría científica. gpt-6.1-sol, esfuerzo high. Chat 01a1aab3-0e87-7f43-86d9-bb4a0a7542e4.
- Atlas 03 · Programa y pruebas. gpt-6.1-terra, esfuerzo medium. Chat 01a1aab3-1105-7201-9ce2-ed034cef2ea3.
- Atlas 04 · Publicación. gpt-6.1-terra, esfuerzo low. Chat 01a1aab3-1361-7c21-83fe-8eb9772b0376.

Host de los cuatro chats local. Velocidad Standard recomendada, sin cambios de configuración global de cuenta. Los prompts por sí solos no seleccionan modelos en chats futuros.

Verificación de esta tarea documental, git diff --check y confirmación del turno completado/estado idle de cada chat. Los criterios científicos y el protocolo de commits, push y cierre siguen en AGENTS.md.

Siguiente acción propuesta, activar Atlas 01 con «Sigue desde relevo» para un lote de hasta diez entidades de Reading v3. Activar un solo chat cada vez. Tras cerrar un lote validado, activar Atlas 04 con una orden de publicar. Claude puede retomar el mismo relevo conforme al protocolo existente.
