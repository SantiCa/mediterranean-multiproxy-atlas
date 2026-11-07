"use client";
import { useMemo, useState, useRef, useEffect } from "react";
import { Download, Expand, X } from "lucide-react";
import { displayRows, extent } from "../lib/plot.mjs";
import { seriesSource, rowUncertainty, rowQcNote } from "../lib/provenance.mjs";
import { derivationRow } from "../lib/derived-proxies.mjs";
import { scientificNumber } from "../lib/format.mjs";
const COLORS = [
  "#267783",
  "#c75e36",
  "#9474ad",
  "#aa891f",
  "#277b54",
  "#3265ac",
  "#a64d76",
  "#65743d",
];
const num = scientificNumber;
const hash = (s: string) =>
  Array.from(s).reduce((a, c) => (a * 31 + c.charCodeAt(0)) >>> 0, 0);
function save(name: string, content: string, type: string) {
  const u = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = u;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(u), 1000);
}
export default function SeriesComparison({ items, active, f, release }: any) {
  const [mode, setMode] = useState("active"),
    [chosen, setChosen] = useState<string[]>([]),
    [zoom, setZoom] = useState(false),
    [values, setValues] = useState("raw"),
    [opacity, setOpacity] = useState(0.6),
    [expanded, setExpanded] = useState(false),
    [error, setError] = useState(""),
    [siteSearch, setSiteSearch] = useState("");
  const svg = useRef<SVGSVGElement>(null);
  const available = items.filter(
    (i: any) =>
      i.series.unit === active.series.unit &&
      i.series.compatibility_group === active.series.compatibility_group,
  );
  const colorFor = (id: string) => {
    const ids = available.map((i: any) => i.record.id).sort();
    const k = ids.indexOf(id);
    return k < COLORS.length
      ? COLORS[Math.max(0, k)]
      : `hsl(${(k * 137.508) % 360} 55% 43%)`;
  };
  useEffect(() => {
    if (!expanded) return;
    const old = document.activeElement as HTMLElement;
    const panel = document.querySelector(".comparison-modal");
    const controls = Array.from(
      panel?.querySelectorAll("button,select,input") || [],
    ) as HTMLElement[];
    controls[0]?.focus();
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setExpanded(false);
      if (e.key === "Tab") {
        const first = controls[0],
          last = controls.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      old?.focus();
    };
  }, [expanded]);
  const selected = available.filter(
    (i: any) =>
      mode === "all" ||
      (mode === "active"
        ? i.record.id === active.record.id
        : chosen.includes(i.record.id)),
  );
  const series = useMemo(
    () =>
      selected.map((i: any) => ({
        ...i,
        plotRows: i.rows
          .filter((r: any) => !zoom || (r[0] >= f.min && r[0] <= f.max))
          .filter(
            () =>
              values === "raw" || (i.reference.n >= 5 && i.reference.sd > 0),
          )
          .map((r: any) => ({
            source: r,
            age: r[0],
            value:
              values === "raw"
                ? r[1]
                : (r[1] - i.reference.mean) / i.reference.sd,
          })),
      })),
    [
      items,
      active.record.id,
      mode,
      chosen.join("|"),
      zoom,
      values,
      f.min,
      f.max,
      f.refMin,
      f.refMax,
    ],
  );
  const points = series.flatMap((i: any) => i.plotRows),
    unit = values === "raw" ? active.series.unit : "z";
  const ageExtent = extent(points.map((p: any) => p.age)),
    valueExtent = extent(points.map((p: any) => p.value));
  let xmin = zoom ? f.min : ageExtent[0],
    xmax = zoom ? f.max : ageExtent[1],
    ymin = valueExtent[0],
    ymax = valueExtent[1];
  const shownSeries = series.map((i: any) => ({
    ...i,
    shown: displayRows(
      i.plotRows,
      Math.max(
        4,
        Math.floor((10000 * i.plotRows.length) / Math.max(1, points.length)),
      ),
    ),
  }));
  const shownCount = shownSeries.reduce(
    (n: number, i: any) => n + i.shown.length,
    0,
  );
  const pad = (ymax - ymin || 1) * 0.08;
  ymin -= pad;
  ymax += pad;
  const W = 800,
    H = 380,
    l = 67,
    r = 24,
    t = 28,
    b = 52;
  const x = (v: number) => l + ((v - xmin) / (xmax - xmin || 1)) * (W - l - r),
    y = (v: number) => t + ((ymax - v) / (ymax - ymin || 1)) * (H - t - b);
  const exportSvg = () => {
    if (!svg.current) return;
    const copy = svg.current.cloneNode(true) as SVGSVGElement,
      ns = "http://www.w3.org/2000/svg";
    // Rebuild the point groups from full data, not the visual-only subset.
    for (const i of series) {
      const group = Array.from(
        copy.querySelectorAll<SVGGElement>("[data-series-id]"),
      ).find((g) => g.getAttribute("data-series-id") === i.series.id);
      if (!group) continue;
      group.replaceChildren();
      const nodes = document.createDocumentFragment();
      for (const p of i.plotRows) {
        const c = document.createElementNS(ns, "circle");
        c.setAttribute("cx", String(x(p.age)));
        c.setAttribute("cy", String(y(p.value)));
        c.setAttribute("r", points.length > 2000 ? "1.6" : "2.7");
        c.setAttribute("opacity", String(opacity));
        nodes.append(c);
      }
      group.appendChild(nodes);
    }
    copy.setAttribute("data-export-points", String(points.length));
    save(
      "medatlas-series-comparison.svg",
      new XMLSerializer().serializeToString(copy),
      "image/svg+xml",
    );
  };
  function exportCsv() {
    const headers = [
      "record",
      "series",
      "age_ka_bp",
      "age_original",
      "value_original",
      "value_numeric",
      "plotted_value",
      "plotted_unit",
      "source_row",
      "source_line",
      "age_uncertainty_ka",
      "value_uncertainty",
      "source_unit",
      "reference_min_ka",
      "reference_max_ka",
      "reference_n",
      "reference_mean",
      "reference_sd",
      "dataset_doi",
      "paper_doi",
      "sha256",
      "source_url",
      "compatibility_group",
      "age_scale",
      "uncertainty_lower",
      "uncertainty_upper",
      "license",
      "license_url",
      "citation",
      "publication_year",
      "value_uncertainty_type",
      "age_probability_levels",
      "age_probability_bounds",
      "derivation_formula",
      "derivation_inputs_json",
      "evidence_type",
      "age_model",
      "age_model_source_url",
      "sample_qc",
    ];
    const rows = series.flatMap((i: any) =>
      i.plotRows.map((p: any) => {
        const row = p.source,
          origin = seriesSource(i.series, i.record);
        return [
          i.record.name,
          i.series.proxy,
          p.age,
          row[4],
          row[5],
          row[1],
          p.value,
          unit,
          row[2],
          row[3],
          row[6],
          row[7],
          i.series.unit,
          f.refMin,
          f.refMax,
          i.reference.n,
          i.reference.mean,
          i.reference.sd,
          origin.dataset_doi,
          origin.paper_doi,
          i.series.raw_sha256 || i.record.raw_sha256,
          i.series.source_url || i.record.source_url,
          i.series.compatibility_group,
          i.series.age_scale ||
            i.record.time_scale ||
            i.series.age_transformation,
          i.series.uncertainty_bounds?.find((b: any) => b[0] === row[2])?.[1],
          i.series.uncertainty_bounds?.find((b: any) => b[0] === row[2])?.[2],
          origin.license,
          origin.license_url,
          origin.citation,
          origin.publication_year,
          rowUncertainty(i.series, row).value_uncertainty_type,
          JSON.stringify(rowUncertainty(i.series, row).age_probability_levels),
          JSON.stringify(rowUncertainty(i.series, row).age_probability_bounds),
          i.series.derivation?.formula,
          JSON.stringify(derivationRow(i.series, row)),
          i.series.evidence_type,
          origin.age_model,
          i.series.age_model_source_url,
          rowQcNote(i.series, row),
        ];
      }),
    );
    save(
      "medatlas-series-comparison.csv",
      [headers, ...rows]
        .map((row) =>
          row
            .map((v: any) => '"' + String(v ?? "").replaceAll('"', '""') + '"')
            .join(","),
        )
        .join("\n"),
      "text/csv;charset=utf-8",
    );
  }
  const controls = (
    <>
      <div className="chart-heading">
        <b>Comparar series temporales</b>
        <div>
          <button
            aria-label="Ampliar comparación de series"
            className="icon"
            onClick={() => setExpanded(true)}
          >
            <Expand size={16} />
          </button>
          <button
            aria-label="Descargar comparación SVG"
            className="icon"
            onClick={exportSvg}
          >
            <Download size={16} />
          </button>
        </div>
      </div>
      <label
        className="field-note"
        htmlFor={expanded ? "compare-expanded" : "compare-mode"}
      >
        Sondeos del mismo proxy
      </label>
      <select
        id={expanded ? "compare-expanded" : "compare-mode"}
        aria-label="Sondeos en la serie temporal"
        value={mode}
        onChange={(e) => {
          setMode(e.target.value);
          if (!chosen.length) setChosen([active.record.id]);
        }}
      >
        <option value="active">Solo el seleccionado</option>
        <option value="custom">Elegir varios sondeos</option>
        <option value="all">
          Todos como nube de puntos ({available.length})
        </option>
      </select>
      {mode === "custom" && (
        <div>
          <input
            aria-label="Buscar sondeo en la comparación"
            placeholder="Buscar sondeo…"
            value={siteSearch}
            onChange={(e) => setSiteSearch(e.target.value)}
          />
          <div className="compare-checkboxes">
            {available
              .filter((i: any) =>
                i.record.name.toLowerCase().includes(siteSearch.toLowerCase()),
              )
              .map((i: any) => (
                <label key={i.record.id}>
                  <input
                    type="checkbox"
                    checked={chosen.includes(i.record.id)}
                    onChange={(e) =>
                      setChosen((c) =>
                        e.target.checked
                          ? [...c, i.record.id]
                          : c.filter((x) => x !== i.record.id),
                      )
                    }
                  />
                  {i.record.name}
                </label>
              ))}
          </div>
        </div>
      )}
      <div className="compare-controls">
        <select
          aria-label="Escala de valores en la serie"
          value={values}
          onChange={(e) => setValues(e.target.value)}
        >
          <option value="raw">Unidades originales</option>
          <option value="z">z con referencia fija del mapa</option>
        </select>
        <label>
          <input
            type="checkbox"
            checked={zoom}
            onChange={(e) => setZoom(e.target.checked)}
          />{" "}
          Solo ventana elegida
        </label>
        <label>
          Opacidad{" "}
          <input
            aria-label="Opacidad de los puntos"
            type="range"
            min="0.1"
            max="1"
            step="0.05"
            value={opacity}
            onChange={(e) => setOpacity(Number(e.target.value))}
          />
        </label>
      </div>
    </>
  );
  const chart = points.length ? (
    <svg
      ref={svg}
      className="comparison-svg"
      xmlns="http://www.w3.org/2000/svg"
      viewBox={`0 0 ${W} ${H}`}
      role="img"
      aria-label={`Comparación de ${selected.length} sondeos, ${points.length} valores`}
    >
      <title>
        {active.series.label} · {points.length} valores de {selected.length}{" "}
        sondeos
      </title>
      <metadata>
        {JSON.stringify({
          release,
          proxy: active.series.proxy,
          unit,
          window: [f.min, f.max],
          zoom,
          normalization: values,
          reference: [f.refMin, f.refMax],
          population_sd: true,
          records: selected.map((i: any) => ({
            id: i.record.id,
            dataset: seriesSource(i.series, i.record).dataset_doi,
            paper: seriesSource(i.series, i.record).paper_doi,
            ...seriesSource(i.series, i.record),
            sha256: i.series.raw_sha256 || i.record.raw_sha256,
            reference: i.reference,
          })),
          missing_ages: "excluded",
          interpolation: "none",
        })}
      </metadata>
      <rect width={W} height={H} fill="white" />
      <defs>
        <clipPath id="series-clip">
          <rect x={l} y={t} width={W - l - r} height={H - t - b} />
        </clipPath>
      </defs>
      <g clipPath="url(#series-clip)">
        {f.max > f.min && (
          <rect
            x={x(f.min)}
            y={t}
            width={Math.max(0, x(f.max) - x(f.min))}
            height={H - t - b}
            fill="#e8d7ac"
            opacity=".4"
          />
        )}
        {shownSeries.map((i: any) => (
          <g
            data-series-id={i.series.id}
            key={i.series.id}
            fill={colorFor(i.record.id)}
          >
            {i.shown.map((p: any, j: number) => (
              <circle
                key={j}
                cx={x(p.age)}
                cy={y(p.value)}
                r={points.length > 2000 ? 1.6 : 2.7}
                opacity={opacity}
              >
                <title>
                  {i.record.name} · {num(p.age)} ka BP · {num(p.value)} {unit}
                </title>
              </circle>
            ))}
          </g>
        ))}
      </g>
      {[0, 0.25, 0.5, 0.75, 1].map((q) => (
        <g key={q} fontFamily="Arial" fill="#56717a" fontSize="12">
          <line
            x1={l}
            x2={W - r}
            y1={y(ymin + q * (ymax - ymin))}
            y2={y(ymin + q * (ymax - ymin))}
            stroke="#dfe8e7"
          />
          <text x={l - 7} y={y(ymin + q * (ymax - ymin)) + 4} textAnchor="end">
            {num(ymin + q * (ymax - ymin))}
          </text>
          <text
            x={x(xmin + q * (xmax - xmin))}
            y={H - b + 23}
            textAnchor="middle"
          >
            {num(xmin + q * (xmax - xmin))}
          </text>
        </g>
      ))}
      <text
        x={W / 2}
        y={H - 7}
        textAnchor="middle"
        fontFamily="Arial"
        fontSize="14"
        fill="#56717a"
      >
        Edad archivada (ka BP · antes de 1950)
      </text>
      <text x="9" y="17" fontFamily="Arial" fontSize="13" fill="#56717a">
        {unit}
      </text>
    </svg>
  ) : (
    <p className="empty">
      No hay puntos para esta selección. En z se requieren ≥5 valores de
      referencia y σ mayor que cero.
    </p>
  );
  const legend = (
    <>
      <div className="compare-legend">
        {series.map((i: any) => (
          <div key={i.record.id}>
            <i style={{ background: colorFor(i.record.id) }} />
            {i.record.name} <span>{i.plotRows.length} puntos</span>
          </div>
        ))}
      </div>
      {shownCount < points.length && (
        <p className="chart-note">
          Vista aligerada: {shownCount.toLocaleString("es-ES")} de{" "}
          {points.length.toLocaleString("es-ES")} puntos, conservando extremos
          por bloques. Los cálculos y las exportaciones CSV/SVG conservan todos
          los puntos seleccionados.
        </p>
      )}
      <p className="chart-note">
        {points.length.toLocaleString("es-ES")} puntos; {selected.length}{" "}
        sondeos. Sin líneas entre muestras ni relleno de hiatos. Edades
        desconocidas excluidas. La misma variable y método no garantizan
        equivalencia ambiental.
      </p>
      <button className="compare-csv" onClick={exportCsv}>
        Descargar puntos CSV
      </button>
    </>
  );
  return (
    <div className="series-comparison">
      {!expanded && (
        <>
          {controls}
          {chart}
          {legend}
        </>
      )}
      {expanded && (
        <div className="modal-backdrop">
          <section
            className="modal comparison-modal"
            role="dialog"
            aria-modal="true"
            aria-label="Comparación ampliada de series"
          >
            <button
              className="close-modal icon"
              aria-label="Cerrar comparación ampliada"
              onClick={() => setExpanded(false)}
            >
              <X size={20} />
            </button>
            {controls}
            {chart}
            {legend}
          </section>
        </div>
      )}
    </div>
  );
}
