# Escala fija del mapa

- Objetivo: comparar edades con una escala de color elegida y constante.
- Base: ab45c83, solicitud registrada en 47722f3; rama relevo.
- Archivos: app/atlas-web/app/page.tsx y app/atlas-web/app/globals.css.
- La escala inicial toma el rango de la primera ventana con datos y permanece fija al cambiar edades. El usuario puede introducir mínimo y máximo; los valores fuera de rango usan el color extremo. Se reinicia al cambiar grupo, modo o referencia z. El SVG utiliza el mismo dominio y lo conserva en metadatos.
- Comprobación: 15 pruebas Node científicas/timeline/proxies y TypeScript sin errores. QA local de escritorio: límites −3 y 3, cambio de 6–8 a 4–6 ka y leyenda constante. No se comprobó móvil.
- Siguiente: cerrar CUR-READING-18 antes de integrar relevo en main; rol 04 publica el resultado. No se publicó ni se integró el lote provisional.
