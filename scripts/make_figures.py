"""Standalone SVG evidence figures with editable text, plus PNGs for visual QA."""
from pathlib import Path
import json
import platform
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figures"
OUT.mkdir(exist_ok=True)
plt.rcParams.update({"svg.fonttype": "none", "font.family": "DejaVu Sans", "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
rows = json.loads((ROOT / "data/processed/observations.json").read_text(encoding="utf-8"))
panels = [
    (438816, "alkenone_SST", "A · MD95-2043 · SST de alquenonas", "SST anual (°C)"),
    (901666, "MgCa_SST", "B · HER-GC-ALB2 · SST de Mg/Ca", "SST corregida (°C)"),
    (759535, "UP10_noncarbonate", "C · MD99-2343 · Fracción no carbonatada", "UP10 (%)"),
    (921230, "G_muellerae_relative_abundance", "D · ODP 161-977A · MIS 11", "G. muellerae (%)"),
]
fig, axes = plt.subplots(2, 2, figsize=(13, 8.5), layout="constrained")
for ax, (dataset, proxy, title, ylabel) in zip(axes.flat, panels):
    subset = [r for r in rows if r["dataset_id"] == dataset and r["proxy"] == proxy]
    x = [r["age_ka_bp"] for r in subset]
    y = [r["value"] for r in subset]
    if proxy == "MgCa_SST":
        ax.errorbar(x, y, yerr=[r["value_uncertainty"] for r in subset], fmt="none",
                    ecolor="#b8c6ce", elinewidth=0.5, alpha=0.7)
    ax.scatter(x, y, s=8, color="#23566e", edgecolor="none", zorder=3)
    ax.set_title(f"{title}\nn={len(subset)} · PANGAEA.{dataset}", loc="left", fontsize=11)
    ax.set_xlabel("Edad archivada (ka BP; referencia 1950)")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.15)
fig.suptitle("Semilla verificable: escalas independientes, sin interpolación", x=0.01, ha="left", fontsize=15)
fig.supxlabel("B: barras = error estándar de SST archivado; no representan incertidumbre de edad.\nCronologías originales sin armonizar. Estos paneles no prueban sincronía ni gradientes espaciales.", fontsize=10)
fig.savefig(OUT / "seed_timeseries.svg")
fig.savefig(OUT / "seed_timeseries.png", dpi=140)
plt.close(fig)

subset = [r for r in rows if r["dataset_id"] == 898587 and r["proxy"] == "BHT_isomer_per_TOC"]
fig, ax = plt.subplots(figsize=(7, 6), layout="constrained")
ax.scatter([r["value"] for r in subset], [float(r["depth_source_value"]) for r in subset], color="#23566e", s=28)
ax.invert_yaxis()
ax.set_xlabel("BHT isomer / TOC (µg/g TOC)")
ax.set_ylabel("Profundidad publicada (mbsf)")
ax.set_title("LC21: vista en profundidad, sin edades asignadas\n19 muestras · PANGAEA.898587", loc="left")
ax.grid(axis="y", alpha=0.15)
fig.supxlabel("Sin columna de edad en esta tabla; sin conversión de sapropeles a ka BP.", fontsize=9)
fig.savefig(OUT / "lc21_depth_only.svg")
fig.savefig(OUT / "lc21_depth_only.png", dpi=140)
plt.close(fig)
(ROOT / "reports/environment.json").write_text(json.dumps({"python": platform.python_version(), "matplotlib": matplotlib.__version__}, indent=2), encoding="utf-8")
print("Created 2 editable SVG figures and 2 PNG previews")
