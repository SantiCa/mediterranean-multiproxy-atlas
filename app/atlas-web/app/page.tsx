"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Globe2,
  Layers,
  SlidersHorizontal,
  ArrowUpRight,
  MapPin,
  Download,
  ChevronDown,
  X,
  Plus,
  BookOpen,
  Info,
  Check,
  RefreshCw,
  Search,
  Compass,
  Database,
  ExternalLink,
  Lock,
} from "lucide-react";
import {
  summarize,
  fieldGrid,
  mapSiteCounts,
  landMask,
  color,
  colorDomain,
  finite,
} from "../lib/science.mjs";

import DiscoveryExplorer from "../components/DiscoveryExplorer";
import TimeWindow from "../components/TimeWindow";
import SeriesComparison from "../components/SeriesComparison";
import { timeExtent } from "../lib/timeline.mjs";
import ProxyPicker from "../components/ProxyPicker";
import DerivedProxyBuilder from "../components/DerivedProxyBuilder";
import { derivationRow } from "../lib/derived-proxies.mjs";
import { groupKey, proxyCatalog as proxyGroups, isAggregateKey, inGroup, seriesMatches } from "../lib/proxies.mjs";
import PrivateData from "../components/PrivateData";
import { seriesSource, rowUncertainty } from "../lib/provenance.mjs";
import { scientificNumber } from "../lib/format.mjs";

const fmt = (x: any, n?: number) =>
  typeof x === "number" && Number.isFinite(x)
    ? n === undefined
      ? scientificNumber(x)
      : x.toLocaleString("es-ES", { maximumFractionDigits: n })
    : "—";
const doiUrl = (doi: string) => (doi ? "https://doi.org/" + doi : undefined);
const BASES: any = {
  ocean: {
    label: "Batimetría",
    url: "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
    credit: "Esri, GEBCO, NOAA, National Geographic, Garmin",
    max: 10,
  },
  topo: {
    label: "Topografía",
    url: "https://tile.opentopomap.org/{z}/{x}/{y}.png",
    credit: "© OpenStreetMap contributors, SRTM | © OpenTopoMap (CC-BY-SA)",
    max: 17,
  },
  imagery: {
    label: "Imagen en color",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    credit: "Esri, Maxar, Earthstar Geographics, GIS User Community",
    max: 17,
  },
  political: {
    label: "Político",
    url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    credit:
      '© <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap contributors</a>',
    max: 19,
  },
};
function download(name: string, content: string, type = "text/plain") {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([content], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function xml(s: any) {
  return String(s ?? "").replace(
    /[<>&"']/g,
    (c) =>
      ({
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
      })[c] || c,
  );
}

export default function Atlas() {
  const [data, setData] = useState<any>(null),
    [loading, setLoading] = useState("Conectando con el catálogo…"),
    [error, setError] = useState("");
  const [tab, setTab] = useState("inventory"),
    [modal, setModal] = useState(""),
    [selected, setSelected] = useState("pangaea-438816"),
    [filtersOpen, setFiltersOpen] = useState(false);
  const [inventoryInfo, setInventoryInfo] = useState<any>(null);
  const [catalog, setCatalog] = useState<any>(null),
    [seriesLoading, setSeriesLoading] = useState(false),
    [seriesError, setSeriesError] = useState("");
  const [f, setF] = useState<any>({
    proxy: "alkenone_SST",
    min: 6,
    max: 8,
    refMin: 0,
    refMax: 10,
    minN: 1,
    mode: "z",
    stat: "median",
    realm: "all",
    yearMin: 0,
    yearMax: 0,
    provider: "all",
    chronology: "all",
    group: "",
  });
  const [base, setBase] = useState("ocean"),
    [surface, setSurface] = useState(false),
    [radius, setRadius] = useState(600),
    [tileError, setTileError] = useState(false);
  const [mask, setMask] = useState<any>(null),
    [coast, setCoast] = useState<any>(null),
    [mapReady, setMapReady] = useState(false),
    [mapError, setMapError] = useState("");
  const [privateSets, setPrivateSets] = useState<any[]>([]);
  const [derivedSets, setDerivedSets] = useState<any[]>([]);
  const viewCatalog = useMemo(() => catalog ? { ...catalog, series: [...catalog.series,
    ...derivedSets.flatMap((entry: any) => entry.series.map(({ rows, ...series }: any) => ({ ...series, rows: [] })))] } : null,
    [catalog, derivedSets]);
  // Owner datasets are merged client-side only; public endpoints never include them.
  useEffect(() => {
    setCatalog((c: any) => {
      if (!c) return c;
      const recs = c.records.filter((r: any) => !r.private),
        ser = c.series.filter((s: any) => !s.private);
      return {
        ...c,
        records: [...recs, ...privateSets.map((d: any) => d.record)],
        series: [...ser, ...privateSets.flatMap((d: any) => d.series.map((s: any) => ({ ...s, rows: [] })))],
      };
    });
  }, [privateSets]);
  useEffect(() => {
    fetch("/api/private/session")
      .then((r) => r.json())
      .then(async (s: any) => {
        if (s.owner) setPrivateSets(((await (await fetch("/api/private/data")).json()) as any).datasets || []);
      })
      .catch(() => {});
  }, []);
  const [candidates, setCandidates] = useState<any[]>([]),
    [newDoi, setNewDoi] = useState(""),
    [adding, setAdding] = useState(false),
    [addMessage, setAddMessage] = useState("");
  const mapEl = useRef<HTMLDivElement>(null),
    mapRef = useRef<any>(null),
    leaflet = useRef<any>(null),
    tileRef = useRef<any>(null),
    marks = useRef<any>(null),
    field = useRef<any>(null),
    chartRef = useRef<SVGSVGElement>(null);
  useEffect(() => {
    if (!modal) return;
    const previous = document.activeElement as HTMLElement;
    const panel = document.querySelector("[role=dialog]");
    const controls = () =>
      Array.from(
        panel?.querySelectorAll(
          "button:not([disabled]),a[href],input,select",
        ) || [],
      ) as HTMLElement[];
    controls()[0]?.focus();
    const handle = (e: KeyboardEvent) => {
      if (e.key === "Escape") setModal("");
      if (e.key === "Tab") {
        const c = controls(),
          first = c[0],
          last = c.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", handle);
    return () => {
      document.removeEventListener("keydown", handle);
      previous?.focus();
    };
  }, [modal]);
  async function load() {
    setError("");
    // Public data are static files built from the versioned seed at deploy time
    // (no database reads, no daily limits). D1 only holds private data and the DOI queue.
    try {
      const r = await fetch("/snapshot/catalog.json");
      if (!r.ok) throw new Error("No se pudo leer el catálogo");
      const d: any = await r.json();
      setCatalog(d);
      setData({ ...d, series: [] });
    } catch (e: any) {
      setError(e.message || "Error de conexión");
    }
    setLoading("");
  }
  useEffect(() => {
    load();
    fetch("/geo/land.geojson")
      .then((r) => r.json())
      .then((g) => {
        setMask(() => landMask(g));
        setCoast(g);
      })
      .catch(() =>
        setMapError("Máscara de costa no disponible; superficie desactivada."),
      );
  }, []);
  useEffect(() => {
    if (!data || tab !== "map" || mapRef.current || !mapEl.current) return;
    let cancelled = false;
    async function init() {
      try {
        if (!(window as any).L) {
          await new Promise<void>((resolve, reject) => {
            const s = document.createElement("script");
            s.src = "/vendor/leaflet/leaflet.js";
            s.onload = () => resolve();
            s.onerror = () => reject(new Error("No se pudo cargar el mapa"));
            document.head.appendChild(s);
          });
        }
        if (cancelled || !mapEl.current) return;
        const L = (window as any).L;
        leaflet.current = L;
        const map = L.map(mapEl.current, {
          zoomControl: false,
          minZoom: 2,
          maxZoom: 17,
          worldCopyJump: true,
        }).setView([36.8, 15], 4);
        L.control.zoom({ position: "bottomright" }).addTo(map);
        L.control.scale({ position: "bottomleft", imperial: false }).addTo(map);
        mapRef.current = map;
        marks.current = L.layerGroup().addTo(map);
        setMapReady(true);
      } catch (e: any) {
        setMapError(e.message);
      }
    }
    init();
    return () => {
      cancelled = true;
    };
  }, [data, tab]);
  useEffect(() => {
    if (!mapReady || !leaflet.current) return;
    const L = leaflet.current,
      map = mapRef.current;
    if (tileRef.current) map.removeLayer(tileRef.current);
    setTileError(false);
    const b = BASES[base];
    let failures = 0;
    const tile = L.tileLayer(b.url, {
      attribution: b.credit,
      maxNativeZoom: b.max,
      maxZoom: 17,
      crossOrigin: false,
    });
    tile.on("tileerror", () => {
      if (++failures > 5) setTileError(true);
    });
    tile.addTo(map);
    tileRef.current = tile;
  }, [base, mapReady]);
  useEffect(() => {
    if (mapRef.current && tab === "map")
      setTimeout(() => mapRef.current?.invalidateSize(), 100);
  }, [tab, filtersOpen]);
  const proxies = useMemo(
    () => (viewCatalog ? proxyGroups(viewCatalog) : []),
    [viewCatalog],
  );
  const proxy =
    proxies.find((p: any) => p.key === f.group) ||
    proxies.find((p: any) => p.id === f.proxy);
  useEffect(() => {
    if (catalog && !f.group) {
      const first = proxies.find((p: any) => p.id === f.proxy) || proxies[0];
      if (first)
        setF((p: any) => ({ ...p, proxy: first.id, group: first.key }));
    }
  }, [catalog, f.group, proxies]);
  useEffect(() => {
    if (!catalog || !f.group) return;
    const controller = new AbortController();
    setSeriesLoading(true);
    setSeriesError("");
    setData({ ...catalog, series: [] });
    const base = {
      provider: f.provider,
      realm: f.realm,
      yearMin: String(f.yearMin),
      yearMax: String(f.yearMax),
      chronology: f.chronology,
    };
    // An aggregation is fetched as its member comparison groups (each validated).
    const keys = isAggregateKey(f.group)
      ? proxies.find((p: any) => p.key === f.group)?.members || []
      : [f.group];
    const records = new Map((catalog.records || []).map((r: any) => [r.id, r]));
    const fs = { ...base, yearMin: Number(base.yearMin) || 0, yearMax: Number(base.yearMax) || 0 };
    const fromSnapshot = (group: string) => {
      const file = catalog.snapshot.groups[group];
      if (!file) return Promise.resolve([]);
      return fetch("/snapshot/obs/" + file, { signal: controller.signal }).then(async (response) => {
        if (!response.ok) throw new Error("No se pudieron cargar las series");
        const result: any = await response.json();
        return result.series.filter(
          (s: any) => records.has(s.record_id) && seriesMatches(s, records.get(s.record_id), fs),
        );
      });
    };
    const one = fromSnapshot;
    (async () => {
      const out: any[] = [];
      for (let i = 0; i < keys.length; i += 6)
        out.push(...(await Promise.all(keys.slice(i, i + 6).filter((k: string) => !k.includes('"private_')).map(one))).flat());
      const mine = [...privateSets, ...derivedSets].flatMap((d: any) => d.series).filter((s: any) => inGroup(s, f.group));
      return [...out, ...mine];
    })()
      .then((series) => {
        if (!controller.signal.aborted) setData({ ...catalog, series });
      })
      .catch((e) => {
        if (e.name !== "AbortError") setSeriesError(e.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setSeriesLoading(false);
      });
    return () => controller.abort();
  }, [
    catalog,
    f.group,
    f.provider,
    f.realm,
    f.yearMin,
    f.yearMax,
    f.chronology,
    privateSets,
    derivedSets,
  ]);
  const summary = useMemo(() => {
    if (!data) return { items: [], error: "" };
    try {
      return { items: summarize(data, f), error: "" };
    } catch (e: any) {
      return { items: [], error: e.message };
    }
  }, [data, f]);
  const items: any[] = summary.items,
    valid = items.filter((s) => finite(s.value)),
    active = items.find((s) => s.record.id === selected) || items[0];
  const mapSites = useMemo(() => mapSiteCounts(items), [items]);
  useEffect(() => {
    if (items.length && !items.some((s) => s.record.id === selected))
      setSelected(items[0].record.id);
  }, [items, selected]);
  const domain = colorDomain(items, f.mode === "z");
  const grid = useMemo(
    () =>
      surface && mask
        ? fieldGrid(items, radius, mask)
        : { cells: [], reason: null },
    [items, surface, radius, mask],
  );
  const totalValues =
      catalog?.series.reduce(
        (n: number, s: any) => n + (s.observation_count || 0),
        0,
      ) || 0,
    nFiltered = valid.reduce((n, s) => n + s.n, 0);
  const domainTime = useMemo(
    () => timeExtent(catalog, inventoryInfo?.time_extent?.metadata_max),
    [catalog, inventoryInfo],
  );
  function change(k: string, v: any) {
    setF((p: any) => ({ ...p, [k]: v }));
  }
  useEffect(() => {
    if (!mapReady) return;
    const L = leaflet.current;
    marks.current.clearLayers();
    for (const item of items) {
      const r = item.record,
        val = finite(item.value);
      const dot = L.circleMarker([r.latitude, r.longitude], {
        radius: r.id === selected ? 10 : 7,
        fillColor: color(item.value, domain[0], domain[1], f.mode === "z"),
        color: r.id === selected ? "#173848" : "#fff",
        weight: r.id === selected ? 3 : 2,
        fillOpacity: val ? 0.96 : 0.5,
      });
      const tooltip = document.createElement("span");
      tooltip.textContent = `${r.name} · ${val ? fmt(item.value) + " " + (f.mode === "z" ? "z" : proxy?.unit) : item.reason}`;
      dot.bindTooltip(tooltip, { direction: "top" });
      dot.on("click", () => setSelected(r.id));
      dot.addTo(marks.current);
    }
  }, [mapReady, items, selected, domain[0], domain[1]]);
  useEffect(() => {
    if (!mapReady) return;
    const L = leaflet.current,
      map = mapRef.current;
    if (field.current) {
      map.removeLayer(field.current);
      field.current = null;
    }
    if (!surface || !grid.cells.length) return;
    const layer = L.layerGroup();
    for (const c of grid.cells)
      L.rectangle(
        [
          [c.lat - c.dy / 2, c.lon - c.dx / 2],
          [c.lat + c.dy / 2, c.lon + c.dx / 2],
        ],
        {
          stroke: false,
          fillColor: color(c.value, domain[0], domain[1], f.mode === "z"),
          fillOpacity: 0.58,
          interactive: false,
        },
      ).addTo(layer);
    layer.addTo(map);
    field.current = layer;
    marks.current.eachLayer((m: any) => m.bringToFront());
  }, [mapReady, surface, grid, domain[0], domain[1]]);
  function fit() {
    if (mapRef.current && items.length) {
      const L = leaflet.current;
      mapRef.current.fitBounds(
        L.latLngBounds(
          items.map((s) => [s.record.latitude, s.record.longitude]),
        ),
        { padding: [50, 50], maxZoom: 6 },
      );
    }
  }
  function exportCSV() {
    const header = [
      "record",
      "series",
      "age_ka_bp",
      "age_original",
      "value_original",
      "value_numeric",
      "unit",
      "sample_z",
      "map_value",
      "exclusion_reason",
      "selection_min_ka",
      "selection_max_ka",
      "statistic",
      "normalization",
      "compatibility_group",
      "reference_min",
      "reference_max",
      "reference_n",
      "reference_mean",
      "reference_sd",
      "source_row",
      "source_line",
      "age_uncertainty_ka",
      "value_uncertainty",
      "depth_original",
      "dataset_doi",
      "paper_doi",
      "publication_year",
      "license",
      "sha256",
      "source_url",
      "age_scale",
      "uncertainty_lower",
      "uncertainty_upper",
      "license_url",
      "citation",
      "value_uncertainty_type",
      "age_probability_levels",
      "age_probability_bounds",
      "derivation_formula",
      "derivation_inputs_json",
      "evidence_type",
    ];
    const rows = items.flatMap((i) =>
      i.target.map((r: any) => [
        i.record.name,
        i.series.proxy,
        r[0],
        r[4],
        i.series.derivation ? null : r[5] ?? r[1],
        r[1],
        i.series.unit,
        f.mode === "z" && i.reference.n >= 5 && i.reference.sd > 0
          ? (r[1] - i.reference.mean) / i.reference.sd
          : null,
        i.value,
        i.reason,
        f.min,
        f.max,
        f.stat,
        f.mode,
        i.series.compatibility_group,
        f.refMin,
        f.refMax,
        i.reference.n,
        i.reference.mean,
        i.reference.sd,
        r[2],
        r[3],
        r[6],
        r[7],
        r[8],
        seriesSource(i.series, i.record).dataset_doi,
        seriesSource(i.series, i.record).paper_doi,
        seriesSource(i.series, i.record).publication_year,
        seriesSource(i.series, i.record).license,
        i.series.raw_sha256 || i.record.raw_sha256,
        i.series.source_url || i.record.source_url,
        i.series.age_scale ||
          i.record.time_scale ||
          i.series.age_transformation,
        i.series.uncertainty_bounds?.find((b: any) => b[0] === r[2])?.[1],
        i.series.uncertainty_bounds?.find((b: any) => b[0] === r[2])?.[2],
        seriesSource(i.series, i.record).license_url,
        seriesSource(i.series, i.record).citation,
        rowUncertainty(i.series, r).value_uncertainty_type,
        JSON.stringify(rowUncertainty(i.series, r).age_probability_levels),
        JSON.stringify(rowUncertainty(i.series, r).age_probability_bounds),
        i.series.derivation?.formula,
        JSON.stringify(derivationRow(i.series, r)),
        i.series.evidence_type,
      ]),
    );
    download(
      "medatlas-selection.csv",
      [header, ...rows]
        .map((r) =>
          r
            .map((v: any) => '"' + String(v ?? "").replaceAll('"', '""') + '"')
            .join(","),
        )
        .join("\n"),
      "text/csv;charset=utf-8",
    );
  }
  function exportMap() {
    const b = mapRef.current?.getBounds();
    if (!b) return;
    const west = b.getWest(),
      east = b.getEast(),
      south = b.getSouth(),
      north = b.getNorth(),
      W = 1200,
      H = 720;
    const project = (p: any) => [
      ((p[0] - west) / (east - west)) * W,
      H - ((p[1] - south) / (north - south)) * H,
    ];
    const shapes =
      coast?.features
        .flatMap((g: any) =>
          (g.geometry.type === "Polygon"
            ? [g.geometry.coordinates]
            : g.geometry.coordinates
          ).map(
            (poly: any) =>
              '<path d="' +
              poly
                .map(
                  (ring: any) =>
                    ring
                      .map((p: any, j: number) => {
                        const [x, y] = project(p);
                        return (
                          (j ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1)
                        );
                      })
                      .join(" ") + "Z",
                )
                .join(" ") +
              '" fill="#e7e7d9" fill-rule="evenodd" stroke="#9caeac" stroke-width=".6"/>',
          ),
        )
        .join("") || "";
    const cells = grid.cells
      .map((c: any) => {
        const p = project([c.lon - c.dx / 2, c.lat + c.dy / 2]);
        return `<rect x="${p[0]}" y="${p[1]}" width="${(c.dx / (east - west)) * W}" height="${(c.dy / (north - south)) * H}" fill="${color(c.value, ...domain, f.mode === "z")}" opacity=".65"/>`;
      })
      .join("");
    const dots = valid
      .map((i) => {
        const p = project([i.record.longitude, i.record.latitude]);
        return `<circle cx="${p[0]}" cy="${p[1]}" r="8" fill="${color(i.value, ...domain, f.mode === "z")}" stroke="white" stroke-width="2"/><text x="${p[0] + 12}" y="${p[1] - 8}" font-size="12">${xml(i.record.name)} ${xml(fmt(i.value))}</text>`;
      })
      .join("");
    const cites = valid
      .map((i) => seriesSource(i.series, i.record).dataset_doi)
      .filter(Boolean)
      .join("; ");
    download(
      "medatlas-map.svg",
      `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="840" viewBox="0 0 1200 840"><metadata>${xml(JSON.stringify({ filters: f, radius, surface, domain, projection: "equirectangular", bounds: { west, east, south, north }, version: data.release.id, sources: valid.map((i) => seriesSource(i.series, i.record)), dois: cites }))}</metadata><defs><linearGradient id="scale"><stop stop-color="${color(domain[0], ...domain, f.mode === "z")}"/><stop offset="50%" stop-color="${color((domain[0] + domain[1]) / 2, ...domain, f.mode === "z")}"/><stop offset="100%" stop-color="${color(domain[1], ...domain, f.mode === "z")}"/></linearGradient><clipPath id="map"><rect width="1200" height="720"/></clipPath></defs><rect width="1200" height="840" fill="#f7faf9"/><g clip-path="url(#map)" font-family="Arial">${shapes}${cells}${dots}</g><g font-family="Arial" fill="#183944"><rect x="950" y="740" width="220" height="8" fill="url(#scale)"/><text x="950" y="765" font-size="11">${fmt(domain[0])}</text><text x="1170" y="765" text-anchor="end" font-size="11">${fmt(domain[1])}</text><text x="24" y="750" font-size="20">${xml(proxy?.label)} · ${f.min}–${f.max} ka BP · ${f.mode === "z" ? "z por sondeo" : "valores originales"}</text><text x="24" y="775" font-size="12">${xml(f.mode === "z" ? `Referencia ${f.refMin}–${f.refMax} ka BP; media y σ por serie; mínimo 5 valores` : "Mediana/media por sitio, sin conversión entre métodos")}</text><text x="24" y="795" font-size="10">${xml(cites)}</text><text x="24" y="815" font-size="10">Proyección equirectangular; costa Natural Earth (dominio público). ${surface ? "IDW exploratorio, no reconstrucción validada." : "Puntos observados agregados."} Edades archivadas; BP antes de 1950.</text></g></svg>`,
      "image/svg+xml",
    );
  }
  async function openSources() {
    setModal("source");
    setAddMessage("");
    const r = await fetch("/api/candidates");
    const d: any = await r.json();
    setCandidates(d.candidates || []);
  }
  async function addDOI(e: any) {
    e.preventDefault();
    setAdding(true);
    setAddMessage("Verificando DOI…");
    try {
      const r = await fetch("/api/candidates", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doi: newDoi }),
      });
      const d: any = await r.json();
      if (!r.ok) throw new Error(d.error);
      setAddMessage(
        "Fuente verificada y añadida a la cola de revisión. Sus valores se incorporarán tras curación.",
      );
      setNewDoi("");
      const q = await fetch("/api/candidates");
      setCandidates(((await q.json()) as any).candidates || []);
    } catch (e: any) {
      setAddMessage(e.message);
    } finally {
      setAdding(false);
    }
  }
  if (!data)
    return (
      <main className="loading">
        <Globe2 size={42} />
        <h1>Mediterranean Multiproxy Atlas</h1>
        <p>{loading || error}</p>
        {error ? (
          <button onClick={load}>Reintentar conexión</button>
        ) : (
          <div className="spinner" />
        )}
      </main>
    );
  return (
    <div className="atlas-app">
      <header className="topbar">
        <a className="brand" href="/" aria-label="Inicio del atlas">
          <span className="brand-mark">
            <Globe2 size={27} />
          </span>
          <span>
            <b>MEDITERRANEAN</b>
            <small>MULTIPROXY ATLAS</small>
          </span>
        </a>
        <nav aria-label="Vistas">
          <button
            className={tab === "inventory" ? "active" : ""}
            onClick={() => setTab("inventory")}
          >
            Sondeos
          </button>
          <button
            className={tab === "map" ? "active" : ""}
            onClick={() => setTab("map")}
          >
            Proxies y series
          </button>
          <button
            className={tab === "catalog" ? "active" : ""}
            onClick={() => setTab("catalog")}
          >
            Datos curados <span>{data.records.length}</span>
          </button>
          <button onClick={() => setModal("methods")}>
            Métodos <ArrowUpRight size={13} />
          </button>
        </nav>
        <div className="header-end">
          <span className="pilot">
            <i /> ATLAS · datos v
            {data.release.id.match(/-v([0-9]+)-/)?.[1] || "3"}
          </span>
          <button className="add-source" onClick={() => setModal("private")}>
            <Lock size={15} /> Mis datos
          </button>
          <button className="add-source" onClick={openSources}>
            <Plus size={15} /> Añadir fuente
          </button>
        </div>
      </header>
      {tab === "inventory" && (
        <DiscoveryExplorer
          onSummary={setInventoryInfo}
          onOpenSeries={(id: string) => {
            const item = catalog.series.find((s: any) => s.record_id === id);
            if (item) {
              setSelected(id);
              setF((p: any) => ({
                ...p,
                proxy: item.proxy,
                group: groupKey(item),
                provider: "all",
                chronology: "all",
                yearMax: 0,
                realm: "all",
                yearMin: 0,
              }));
              setTab("map");
            }
          }}
        />
      )}
      <div
        className="mobile-toolbar"
        style={tab === "inventory" ? { display: "none" } : {}}
      >
        <button onClick={() => setFiltersOpen(!filtersOpen)}>
          <SlidersHorizontal size={16} /> Filtros
        </button>
        <span>{valid.length} registros con datos</span>
      </div>
      <div
        className="workspace"
        style={tab === "inventory" ? { display: "none" } : {}}
      >
        <aside className={"filters " + (filtersOpen ? "mobile-open" : "")}>
          <div className="sidebar-title">
            <SlidersHorizontal size={16} />
            <b>Configura tu mapa</b>
            <button
              className="icon mobile-close"
              onClick={() => setFiltersOpen(false)}
              aria-label="Cerrar filtros"
            >
              <X size={16} />
            </button>
          </div>
          <ProxyPicker
            catalog={viewCatalog}
            selectedKey={f.group}
            f={f}
            setF={setF}
            onSelect={(g: any) => {
              setF((p: any) => ({ ...p, proxy: g.id, group: g.key }));
              setFiltersOpen(false);
            }}
          />
          <DerivedProxyBuilder catalog={catalog} privateSets={privateSets} onChange={setDerivedSets}
            onSelect={(series: any) => setF((previous: any) => ({ ...previous, proxy: series.proxy, group: groupKey(series), mode: "raw" }))} />
          <section>
            <label className="overline" htmlFor="realm">
              02 / ARCHIVO
            </label>
            <div className="segmented">
              <button
                className={f.realm === "all" ? "on" : ""}
                onClick={() => change("realm", "all")}
              >
                Todos
              </button>
              <button
                className={f.realm === "marine" ? "on" : ""}
                onClick={() => change("realm", "marine")}
              >
                Marino
              </button>
              <button
                className={f.realm === "continental" ? "on" : ""}
                onClick={() => change("realm", "continental")}
              >
                Continental
              </button>
            </div>
          </section>
          <TimeWindow
            f={f}
            setF={setF}
            domain={domainTime}
            metadataRecord={inventoryInfo?.time_extent?.metadata_max_record}
          />
          <section>
            <label className="overline" htmlFor="normalization">
              04 / VALORES Y NORMALIZACIÓN
            </label>
            <select
              id="normalization"
              value={f.mode}
              onChange={(e) => change("mode", e.target.value)}
            >
              <option value="z">Anomalía normalizada · z por sondeo</option>
              <option value="raw">{proxy?.series[0]?.derivation ? "Valores calculados" : "Valores originales"} · {proxy?.unit}</option>
            </select>
            {f.mode === "z" && (
              <>
                <div className="reference">
                  <span>Referencia (ka BP)</span>
                  <input
                    aria-label="Referencia desde"
                    type="number"
                    value={f.refMin}
                    onChange={(e) => change("refMin", Number(e.target.value))}
                  />
                  <span>–</span>
                  <input
                    aria-label="Referencia hasta"
                    type="number"
                    value={f.refMax}
                    onChange={(e) => change("refMax", Number(e.target.value))}
                  />
                </div>
                <p className="field-note">
                  z = (valor − media) / σ de cada serie. Referencia fija, ≥5
                  valores; describe anomalías relativas y elimina el gradiente
                  medio entre sitios.
                </p>
              </>
            )}
            <div className="paired">
              <label>
                Resumen
                <select
                  aria-label="Estadístico"
                  value={f.stat}
                  onChange={(e) => change("stat", e.target.value)}
                >
                  <option value="median">Mediana</option>
                  <option value="mean">Media</option>
                </select>
              </label>
              <label>
                Mín. muestras
                <select
                  aria-label="Mínimo de muestras"
                  value={f.minN}
                  onChange={(e) => change("minN", Number(e.target.value))}
                >
                  <option>1</option>
                  <option>3</option>
                  <option>5</option>
                  <option>10</option>
                </select>
              </label>
            </div>
          </section>
          <section className="surface-option">
            <label className="toggle">
              <span>
                <Layers size={16} />
                <b>Superficie de color</b>
              </span>
              <input
                type="checkbox"
                checked={surface}
                onChange={(e) => setSurface(e.target.checked)}
              />
            </label>
            <p className="field-note">
              IDW exploratorio: sin extrapolación fuera de la envolvente de
              sitios. ≥3 vecinos por celda y máscara de costa.
            </p>
            {surface && (
              <label className="radius">
                Radio máximo <strong>{radius} km</strong>
                <input
                  aria-label="Radio IDW km"
                  type="range"
                  min="200"
                  max="1600"
                  step="100"
                  value={radius}
                  onChange={(e) => setRadius(Number(e.target.value))}
                />
              </label>
            )}
          </section>
          <section>
            <label className="overline" htmlFor="provider">
              05 / FUENTE Y CRONOLOGÍA
            </label>
            <select
              id="provider"
              aria-label="Fuente cuantitativa"
              value={f.provider}
              onChange={(e) => change("provider", e.target.value)}
            >
              <option value="all">Todas las fuentes</option>
              {[...new Set([...catalog.records, ...catalog.series].map((r: any) => r.provider).filter(Boolean))]
                .sort()
                .map((v: any) => (
                  <option key={v}>{v}</option>
                ))}
            </select>
            <label className="field-note" htmlFor="chronology">
              Base de edad publicada
            </label>
            <select
              id="chronology"
              aria-label="Base de edad publicada"
              value={f.chronology}
              onChange={(e) => change("chronology", e.target.value)}
            >
              <option value="all">Todas las cronologías admitidas</option>
              {[...new Set(catalog.series.map((s: any) => s.chronology_status))]
                .filter(Boolean)
                .sort()
                .map((v: any) => (
                  <option key={v} value={v}>
                    {catalog.series.find((s: any) => s.chronology_status === v)
                      ?.chronology_label ||
                      (v === "published_calendar_multi_method"
                        ? "Calendario publicado · controles mixtos"
                        : v === "published_calendar"
                          ? "Calendario publicado"
                          : v === "published_CE"
                            ? "Años CE → BP"
                            : v === "published_varve_BP"
                              ? "Edad varvada BP"
                              : v === "published_BP"
                                ? "Edad BP archivada"
                                : v === "legacy_archived"
                                  ? "Piloto · edad archivada"
                                  : v)}
                  </option>
                ))}
            </select>
            <p className="field-note">
              La base de edad está revisada en la tabla; no se han recalibrado
              ni validado independientemente los modelos.
            </p>
          </section>
          <section>
            <label className="overline">06 / AÑO DEL ARTÍCULO</label>
            <div className="publication-range">
              <label>
                Desde
                <input
                  aria-label="Artículo desde el año"
                  type="number"
                  min="1800"
                  max="2100"
                  placeholder="Cualquiera"
                  value={f.yearMin || ""}
                  onChange={(e) => change("yearMin", Number(e.target.value))}
                />
              </label>
              <label>
                Hasta
                <input
                  aria-label="Artículo hasta el año"
                  type="number"
                  min="1800"
                  max="2100"
                  placeholder="Cualquiera"
                  value={f.yearMax || ""}
                  onChange={(e) => change("yearMax", Number(e.target.value))}
                />
              </label>
            </div>
            <p className="field-note">
              Años de publicación, separados de las edades de las muestras. Si
              no hay año conocido, se excluye al fijar un límite.
            </p>
            <button
              className="proxy-coverage"
              onClick={() =>
                setF((p: any) => ({
                  ...p,
                  provider: "all",
                  realm: "all",
                  chronology: "all",
                  yearMin: 0,
                  yearMax: 0,
                }))
              }
            >
              Restablecer filtros de registros
            </button>
          </section>
          <div className="sidebar-footer">
            <Database size={16} />
            <span>
              <b>{fmt(totalValues, 0)} valores trazables</b>
              <small>Fuentes publicadas · {catalog.records.length} registros</small>
            </span>
          </div>
        </aside>
        {(seriesLoading || seriesError) && (
          <div
            className="series-status"
            role={seriesError ? "alert" : "status"}
          >
            {seriesError || "Cargando series seleccionadas…"}
          </div>
        )}
        <main
          className="main-area"
          style={tab === "map" ? {} : { display: "none" }}
        >
          <div className="map-heading">
            <div>
              <div className="eyebrow">
                EXPLORAR / MEDITERRÁNEO Y ÁREAS ADYACENTES
              </div>
              <h1>{proxy?.label}</h1>
              <p>
                {fmt(f.min)}–{fmt(f.max)} ka BP <span>·</span>{" "}
                {f.stat === "median" ? "Mediana" : "Media"} por sitio{" "}
                <span>·</span>{" "}
                {f.mode === "z"
                  ? "Anomalía respecto a referencia"
                  : proxy?.unit}
              </p>
            </div>
            <button className="fit-button" onClick={fit}>
              <Compass size={16} /> Ajustar vista
            </button>
          </div>
          <div className="map-frame">
            <div
              ref={mapEl}
              className="map-canvas"
              aria-label="Mapa interactivo de registros paleoambientales"
            />
            <div className="map-stats">
              <div>
                <strong>
                  {mapSites.withData}
                  <small>/{mapSites.total}</small>
                </strong>
                <span title="Ubicaciones únicas por coordenadas a cuatro decimales">SITIOS CON DATOS</span>
              </div>
              <i />
              <div>
                <strong>{fmt(nFiltered, 0)}</strong>
                <span>VALORES EN VENTANA</span>
              </div>
            </div>
            <div className="base-control">
              <Layers size={15} />
              <select
                aria-label="Capa del mapa"
                value={base}
                onChange={(e) => setBase(e.target.value)}
              >
                {Object.entries(BASES).map(([k, v]: any) => (
                  <option key={k} value={k}>
                    {v.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="legend">
              <div className="legend-title">
                <b>
                  {f.mode === "z" ? "Anomalía por sondeo (z)" : proxy?.unit}
                </b>
                <span>{surface ? "Puntos + IDW" : "Puntos observados"}</span>
              </div>
              <div
                className="colorbar"
                style={{
                  background: `linear-gradient(90deg,${color(domain[0], ...domain, f.mode === "z")},${color((domain[0] + domain[1]) / 2, ...domain, f.mode === "z")},${color(domain[1], ...domain, f.mode === "z")})`,
                }}
              />
              <div className="legend-ticks">
                <span>{fmt(domain[0])}</span>
                <span>{fmt((domain[0] + domain[1]) / 2)}</span>
                <span>{fmt(domain[1])}</span>
              </div>
              <small>
                <i className="missing-dot" /> Gris: sin valor comparable en esta
                selección
              </small>
            </div>
            <div className="map-export">
              <button onClick={exportMap}>
                <Download size={14} /> SVG mapa
              </button>
            </div>
            {(summary.error ||
              mapError ||
              tileError ||
              (surface && grid.reason)) && (
              <div className="map-notice">
                <Info size={15} />
                <span>
                  {summary.error ||
                    mapError ||
                    (tileError
                      ? "La capa base está respondiendo con errores. Cambia de capa; los datos siguen disponibles."
                      : grid.reason)}
                </span>
              </div>
            )}
          </div>
          <div className="map-foot">
            <span>
              <i />{" "}
              {surface
                ? `IDW exploratorio · ${grid.cells.length} celdas con soporte`
                : "Mapa de muestras agregadas · sin interpolación"}
            </span>
            <button onClick={() => setModal("methods")}>
              Cómo se calcula <ArrowUpRight size={13} />
            </button>
          </div>
          <div className="record-strip">
            {items.map((i) => (
              <button
                key={i.record.id}
                className={selected === i.record.id ? "chosen" : ""}
                onClick={() => setSelected(i.record.id)}
              >
                <span
                  className="strip-dot"
                  style={{
                    background: color(i.value, ...domain, f.mode === "z"),
                  }}
                />
                <div>
                  <b>{i.record.name}</b>
                  <small>
                    {finite(i.value)
                      ? fmt(i.value) +
                        " " +
                        (f.mode === "z" ? "z" : proxy?.unit)
                      : "Sin datos en ventana"}
                  </small>
                </div>
                <span className="strip-n">n {i.n}</span>
              </button>
            ))}
          </div>
        </main>
        {tab === "map" && (
          <aside className="inspector">
            {active ? (
              <>
                <div className="inspector-top">
                  <span className="overline">REGISTRO SELECCIONADO</span>
                  <MapPin size={18} />
                </div>
                <h2>{active.record.name}</h2>
                <p className="site-coords">
                  {fmt(Math.abs(active.record.latitude), 4)}°{" "}
                  {active.record.latitude < 0 ? "S" : "N"} ·{" "}
                  {fmt(Math.abs(active.record.longitude), 4)}°{" "}
                  {active.record.longitude < 0 ? "W" : "E"}
                </p>
                <div className="record-tags">
                  <span>
                    {active.record.realm === "marine"
                      ? "Sedimento marino"
                      : /speleothem/i.test(active.record.archive_type || "")
                        ? "Espeleotema"
                        : "Archivo continental"}
                  </span>
                  <span>
                    {active.series.provider || active.record.provider}
                  </span>
                </div>
                <div className="result-card">
                  <small>
                    {f.stat === "median" ? "MEDIANA" : "MEDIA"} · {f.min}–
                    {f.max} ka BP
                  </small>
                  <div>
                    {finite(active.value) ? fmt(active.value) : "—"}{" "}
                    <span>{f.mode === "z" ? "z" : proxy?.unit}</span>
                  </div>
                  <p>
                    {active.n} muestras · {active.nUnique} edades distintas
                  </p>
                  {active.reason && <p className="warning">{active.reason}</p>}
                </div>
                <SeriesComparison
                  items={items}
                  active={active}
                  f={f}
                  release={data.release.id}
                />
                {f.mode === "z" && (
                  <div className="reference-details">
                    <b>Referencia utilizada</b>
                    <span>
                      {fmt(active.reference.min)}–{fmt(active.reference.max)} ka
                      BP · n {active.reference.n}
                    </span>
                    <span>
                      Media {fmt(active.reference.mean)} · σ{" "}
                      {fmt(active.reference.sd)} {proxy?.unit}
                    </span>
                  </div>
                )}
                <dl className="metadata">
                  <div>
                    <dt>
                      {active.record.realm === "marine"
                        ? "Profundidad de agua"
                        : "Elevación"}
                    </dt>
                    <dd>
                      {fmt(
                        active.record.water_depth_m ??
                          active.record.elevation_m,
                        0,
                      )}{" "}
                      m
                    </dd>
                  </div>
                  <div>
                    <dt>Artículo</dt>
                    <dd>
                      {seriesSource(active.series, active.record)
                        .publication_year ?? "No resuelto"}
                    </dd>
                  </div>
                  <div>
                    <dt>Tipo de evidencia</dt>
                    <dd>
                      {active.series.derivation ? "Transformación de usuario"
                        : active.series.evidence_type ===
                      "published_reconstruction"
                        ? "Reconstrucción publicada"
                        : active.series.evidence_type === "derived_relative_abundance"
                          ? "Abundancia relativa calculada"
                        : "Valor publicado"}
                    </dd>
                  </div>
                </dl>
                <div className="source-links">
                  <a
                    href={
                      active.series.source_url ||
                      active.record.source_url ||
                      doiUrl(active.record.dataset_doi)
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    <Database size={15} /> Dataset original{" "}
                    <ExternalLink size={12} />
                  </a>
                  <a
                    href={doiUrl(
                      seriesSource(active.series, active.record).paper_doi,
                    )}
                    target="_blank"
                    rel="noreferrer"
                  >
                    <BookOpen size={15} />{" "}
                    {seriesSource(active.series, active.record).paper_doi
                      ? "Artículo científico"
                      : "Artículo original no resuelto"}{" "}
                    <ExternalLink size={12} />
                  </a>
                </div>
                <details className="quality">
                  <summary>
                    Procedencia y límites <ChevronDown size={13} />
                  </summary>
                  <p>{active.series.method}</p>
                  <p>
                    {active.series.age_scale ||
                      active.series.age_transformation ||
                      active.record.age_scale_status ||
                      active.record.time_scale ||
                      "Cronología archivada; sin armonización local"}
                  </p>
                  {[...new Set([...(active.record.qc_notes || []), ...(active.series.qc_notes || [])])].map(
                    (n: string, i: number) => (
                      <p key={i}>{n}</p>
                    ),
                  )}
                  <p>
                    Licencia:{" "}
                    {seriesSource(active.series, active.record).license}
                  </p>
                  <p className="hash">
                    SHA-256:{" "}
                    {active.series.raw_sha256 || active.record.raw_sha256}
                  </p>
                </details>
                <button className="export-data" onClick={exportCSV}>
                  <Download size={16} /> Exportar selección CSV
                </button>
              </>
            ) : (
              <div className="empty">
                <Info /> Sin registros para esta combinación de filtros.
              </div>
            )}
          </aside>
        )}
        {tab === "catalog" && (
          <main className="catalog">
            <div className="eyebrow">BASE DE DATOS / COLECCIÓN CURADA</div>
            <h1>Registros con historia y procedencia</h1>
            <p>
              {catalog.records.length} registros con valores. Las relaciones con
              artículos y repositorios están verificadas; la cronología y la
              interpretación tienen límites específicos por fuente.
            </p>
            <div className="catalog-summary">
              <span>
                <b>{data.records.length}</b> registros
              </span>
              <span>
                <b>{catalog.series.length}</b> series
              </span>
              <span>
                <b>{fmt(totalValues, 0)}</b> valores
              </span>
            </div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Registro</th>
                    <th>Archivo</th>
                    <th>Series</th>
                    <th>Fuente / artículo</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  {data.records.map((r: any) => {
                    const ss = catalog.series.filter(
                      (s: any) => s.record_id === r.id,
                    );
                    return (
                      <tr key={r.id}>
                        <td>
                          <b>{r.name}</b>
                          <small>
                            {fmt(r.latitude, 3)}, {fmt(r.longitude, 3)}
                          </small>
                        </td>
                        <td>
                          {r.realm === "marine" ? "Marino" : "Continental"}
                        </td>
                        <td>
                          {ss.length}
                          <small>
                            {fmt(
                              ss.reduce(
                                (n: number, s: any) =>
                                  n + (s.observation_count || 0),
                                0,
                              ),
                              0,
                            )}{" "}
                            valores
                          </small>
                        </td>
                        <td>
                          <a
                            href={r.source_url || doiUrl(r.dataset_doi)}
                            target="_blank"
                            rel="noreferrer"
                          >
                            {r.provider === "PANGAEA" ? "PANGAEA" : "NOAA"}{" "}
                            <ExternalLink size={11} />
                          </a>
                          <small>
                            <a
                              href={doiUrl(r.paper_doi)}
                              target="_blank"
                              rel="noreferrer"
                            >
                              {r.paper_doi
                                ? "Artículo " + r.publication_year
                                : "Artículo original no resuelto"}
                            </a>
                          </small>
                        </td>
                        <td>
                          <button
                            onClick={() => {
                              setSelected(r.id);
                              setF({
                                ...f,
                                proxy: ss[0].proxy,
                                group: groupKey(ss[0]),
                                realm: "all",
                                provider: "all",
                                chronology: "all",
                                yearMin: 0,
                                yearMax: 0,
                              });
                              setTab("map");
                            }}
                          >
                            Ver serie <ArrowUpRight size={13} />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </main>
        )}
      </div>
      {modal && (
        <div className="modal-backdrop" onClick={() => setModal("")}>
          <section
            className={"modal " + (modal === "methods" ? "wide" : "")}
            role="dialog"
            aria-modal="true"
            aria-label={
              modal === "methods" ? "Métodos del atlas" : "Añadir fuente"
            }
            onClick={(e) => e.stopPropagation()}
          >
            <button
              className="close-modal icon"
              onClick={() => setModal("")}
              aria-label="Cerrar"
            >
              <X size={20} />
            </button>
            {modal === "private" ? (
              <PrivateData
                catalog={catalog}
                datasets={privateSets}
                onDatasets={setPrivateSets}
              />
            ) : modal === "methods" ? (
              <>
                <span className="overline">TRANSPARENCIA CIENTÍFICA</span>
                <h2>Del dato al mapa</h2>
                <div className="method-grid">
                  <article>
                    <b>01 · Seleccionar</b>
                    <p>
                      Una variable, unidad y método compatibles. Las
                      calibraciones de SST se mantienen en grupos separados;
                      Mg/Ca también conserva método y especie. δ¹⁸O y δ¹³C son
                      variables distintas, sin conversión a precipitación.
                    </p>
                  </article>
                  <article>
                    <b>02 · Resumir</b>
                    <p>
                      La mediana o media usa las muestras dentro de la ventana
                      inclusiva. Cada muestra pesa igual; no es una media
                      ponderada por tiempo. No se imputan datos ni se interpola
                      entre edades.
                    </p>
                  </article>
                  <article>
                    <b>03 · Normalizar</b>
                    <p>
                      z = (valor − μ) / σ. μ y σ poblacional se calculan por
                      serie en una referencia fija, con ≥5 valores y σ mayor que
                      cero. El mapa z representa anomalías relativas, elimina el
                      gradiente medio y no convierte diferentes proxies en una
                      magnitud ambiental común.
                    </p>
                  </article>
                  <article>
                    <b>04 · Representar</b>
                    <p>
                      Los círculos son agregados observados por sitio. La
                      superficie opcional usa IDW de potencia 2, solo dentro de
                      la envolvente convexa, con ≥3 vecinos en el radio y
                      máscara Natural Earth. No incluye incertidumbre espacial y
                      no es una reconstrucción validada.
                    </p>
                  </article>
                </div>
                <div className="method-warning">
                  <Info size={18} />
                  <p>
                    Las edades son las archivadas por cada fuente, sin recálculo
                    ni ensambles armonizados. La resolución, el muestreo
                    irregular, los hiatos y los efectos de archivo limitan
                    cualquier comparación de fase o causalidad. El registro
                    Soreq conserva una discrepancia de coordenadas, documentada
                    en su ficha.
                  </p>
                </div>
                <h3>Fuentes y base cartográfica</h3>
                <p className="method-links">
                  <a href="https://www.pangaea.de/" target="_blank">
                    PANGAEA
                  </a>{" "}
                  ·{" "}
                  <a
                    href="https://www.ncei.noaa.gov/products/paleoclimatology"
                    target="_blank"
                  >
                    NOAA WDS
                  </a>{" "}
                  ·{" "}
                  <a
                    href="https://www.naturalearthdata.com/about/terms-of-use/"
                    target="_blank"
                  >
                    Natural Earth, dominio público
                  </a>{" "}
                  · Leaflet 1.9.4, BSD-2-Clause. Las capas base mantienen la
                  atribución del proveedor en el mapa. Su color representa
                  relieve/imagen; la capa de proxy es independiente.
                </p>
                <p>
                  Versión {data.release.id} · {fmt(totalValues, 0)} valores
                  preservados. Los CSV incluyen localizadores, DOI, licencia,
                  hash y parámetros de cálculo; el SVG incorpora la selección y
                  las fuentes.
                </p>
              </>
            ) : (
              <>
                <span className="overline">CRECER CON LA LITERATURA</span>
                <h2>Una nueva fuente para el atlas</h2>
                <p>
                  Guarda un DOI de artículo o dataset. Su identidad
                  bibliográfica se verifica; los valores entran al catálogo
                  después de contrastar tablas, metodología, cronología y
                  licencia.
                </p>
                <form onSubmit={addDOI}>
                  <label htmlFor="doi-input">DOI de artículo o dataset</label>
                  <input
                    id="doi-input"
                    value={newDoi}
                    onChange={(e) => setNewDoi(e.target.value)}
                    placeholder="10.1594/PANGAEA.…"
                    required
                  />
                  <button
                    disabled={adding}
                    className="export-data"
                    type="submit"
                  >
                    {adding ? (
                      <RefreshCw className="spin" size={16} />
                    ) : (
                      <Plus size={16} />
                    )}{" "}
                    {adding ? "Verificando…" : "Verificar y añadir a revisión"}
                  </button>
                </form>
                {addMessage && (
                  <div className="add-message" role="status">
                    {addMessage}
                  </div>
                )}
                <h3>
                  Cola de curación <span>{candidates.length}</span>
                </h3>
                {candidates.length ? (
                  candidates.map((c) => (
                    <div className="candidate" key={c.id}>
                      <BookOpen size={16} />
                      <div>
                        <a
                          target="_blank"
                          href={doiUrl(c.doi)}
                          rel="noreferrer"
                        >
                          {c.title}
                        </a>
                        <small>{c.doi} · Pendiente de curación</small>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="field-note">
                    La cola está vacía. Cada fuente incorporada conservará su
                    DOI, versión y evidencia de revisión.
                  </p>
                )}
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
}
