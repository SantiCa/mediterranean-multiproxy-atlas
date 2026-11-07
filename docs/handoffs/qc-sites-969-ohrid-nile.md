# QC espacial y cronológico: 969, Ohrid y Nilo

- Estado: implementado en relevo, sin despliegue. Atlas 02, 07-11-2026. Base científica v28-c5fa6332d0f; revisión previa 5728a14.
- **969D/E:** comparten la identidad espacial documentada del [sitio ODP 969](https://www-odp.tamu.edu/publications/160_IR/VOLUME/CHAPTERS/ir160_10.pdf). Cobertura e IDW usan una única clave de sitio. Ambos sondeos conservan coordenadas, registros, series y selección individuales.
- **Ohrid:** la serie PANGAEA.908113 avisa de la inversión de 4,8 años entre líneas TSV 1004 y 1005. El aviso aparece en la ficha de la serie y solo esas filas llevan `sample_qc` en los CSV. No se corrige ni excluye ninguna muestra. [Original](https://doi.org/10.1594/PANGAEA.908113).
- **Nilo:** los modelos publicados de MS21PC y PS009PC aparecen en «Procedencia y límites» y en los CSV: controles AMS ¹⁴C, calibración marina, corrección local de reservorio, ajuste por tramos y dependencia del techo PS009PC respecto de PS008BC. [Hennekam et al., §2, tabla 1 y fig. 2](https://doi.org/10.1016/j.quascirev.2015.05.031). Sin recalibrar.
- Evidencia: 46 Node, TypeScript y compilación correctos. Snapshots v27 y v28 cotejados (1.027.294 y 1.028.429 valores). Verificados en v28 dos registros/una clave espacial, dos filas marcadas y cuatro series con modelos documentados. Ninguna fila cambió en la aplicación del QC.
- Siguiente: el rol 04 debe regenerar la instantánea desde la semilla y `config/qc_corrections.json` antes de publicar; no reutilizar un snapshot sin estas anotaciones.
