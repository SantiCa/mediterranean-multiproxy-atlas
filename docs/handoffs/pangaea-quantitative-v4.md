# Handoff — PANGAEA cuantitativo v4

Base atlas-v3 (29/89/81.339), sin tocar baseline/app/archivos compartidos. Script curate_pangaea_v4.py y contrato pangaea_v4_sources.json; originales ignorados en quantitative_v4/pangaea. Fragmento pangaea_curated.json: **11 eventos, 41 series, 4.271 valores activos**, 15 datasets activos de17 revisados. 4series/531valores en cuarentena, NO incorporar.

Cuarentena:995820 Peixão (edades fraccionales ka pasan a1003..11150 aunque fuenteholocena~11100años), tresseries396valores intactos. No inferir división1000.667403TOC−1,71%, serie135intacta. Fuente primariaPeixão954457TOC válido; GeoB7608primaria667328δ18OCandona. IDs nuevos pangaea-954457 y pangaea-667328.

Seis pruebas pasan, contraste de las4.802 celdas revisadas. Cada serie tiene DOI/paper/year/licencia/hash/cita propios. BichlerCCBYSA4 requierepreservarcondiciones, no licenciauniforme. CuatroWeldeabG.ruberwhitePDB/MAT251comparten grupo; PDBnoVPDBinferido. VSMOWsolo dondecommentnativoloexplicita.

Incertidumbre: SE/SD/2σNd preservados, Baconbounds solo940127, εPeixaoparámetrosinvertidos sinnormalizar. CP10BCelementosdespuésdesegundacolumnaprofundidaden espera,944660Sr/Ndconedadpropia sí. Nadaedad-depth. Rangoactivo−.069..193.07ka, noampliaglobal1365.

Docs/curation/pangaea_v4.md y reports/pangaea_v4_audit.json. No commit/push/deploy. Root integra fragmento SOLO series activas y revisa metadata/grupos/exportes.

