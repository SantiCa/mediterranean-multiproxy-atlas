"use client";
import { useState, useEffect, useRef, useMemo } from "react";
import { inventoryFetch } from "../lib/inventory-local.mjs";
import {
  Search,
  Layers,
  Download,
  MapPin,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  SlidersHorizontal,
  X,
  Database,
} from "lucide-react";
const bases: any = {
  ocean: [
    "Batimetría",
    "https://services.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
    "Esri, GEBCO, NOAA, National Geographic, Garmin",
    10,
  ],
  topo: [
    "Topografía",
    "https://tile.opentopomap.org/{z}/{x}/{y}.png",
    "© OpenStreetMap contributors, SRTM | © OpenTopoMap (CC-BY-SA)",
    17,
  ],
  imagery: [
    "Imagen en color",
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "Esri, Maxar, Earthstar Geographics, GIS User Community",
    17,
  ],
  political: [
    "Político",
    "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
    19,
  ],
};
const palette = [
  "#2b7a84",
  "#bd6639",
  "#7a6a9f",
  "#819243",
  "#4879ae",
  "#a95675",
];
const colour = (s: string) =>
  palette[
    Array.from(s || "").reduce((n, c) => n + c.charCodeAt(0) * 31, 0) %
      palette.length
  ];
const fmt = (n: any) =>
  typeof n === "number"
    ? n.toLocaleString("es-ES", { maximumFractionDigits: 4 })
    : "—";
const safe = (url: any) =>
  typeof url === "string" && /^https?:\/\//i.test(url) ? url : undefined;
export default function DiscoveryExplorer({ onOpenSeries, onSummary }: any) {
  const [summary, setSummary] = useState<any>(null),
    [progress, setProgress] = useState("Preparando el catálogo enlazado…"),
    [error, setError] = useState(""),
    [filters, setFilters] = useState({
      provider: "all",
      realm: "all",
      campaign: "all",
      kind: "sites",
      q: "",
    }),
    [query, setQuery] = useState("");
  const [points, setPoints] = useState<any[]>([]),
    [rows, setRows] = useState<any[]>([]),
    [groups, setGroups] = useState<any[]>([]),
    [total, setTotal] = useState(0),
    [offset, setOffset] = useState(0),
    [view, setView] = useState("map"),
    [grouped, setGrouped] = useState(false),
    [loading, setLoading] = useState(false),
    [truncated, setTruncated] = useState(false);
  const [selected, setSelected] = useState(""),
    [detail, setDetail] = useState<any>(null),
    [base, setBase] = useState("ocean"),
    [mapReady, setMapReady] = useState(false),
    [drawer, setDrawer] = useState(false),
    [tileError, setTileError] = useState(false);
  const [preparedCsv, setPreparedCsv] = useState<{
    url: string;
    params: string;
  } | null>(null);
  const [preparingCsv, setPreparingCsv] = useState(false);
  useEffect(
    () => () => {
      if (preparedCsv) URL.revokeObjectURL(preparedCsv.url);
    },
    [preparedCsv],
  );
  const el = useRef<HTMLDivElement>(null),
    map = useRef<any>(null),
    layer = useRef<any>(null),
    tiles = useRef<any>(null);
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        let r = await inventoryFetch("/api/inventory");
        let d: any = await r.json();
        if (!r.ok) throw new Error(d.error);
        if (d.needsBootstrap) {
          let n = 0;
          for (let i = 0; i < 1000; i++) {
            if (!active) return;
            setProgress(`Indexando metadatos · ${fmt(n)} filas preparadas`);
            r = await inventoryFetch("/api/inventory", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ offset: n }),
            });
            const p: any = await r.json();
            if (!r.ok) throw new Error(p.error);
            if (p.ready) break;
            n = p.next;
            if (i === 999) throw new Error("Importación incompleta");
          }
          r = await inventoryFetch("/api/inventory");
          d = await r.json();
        }
        if (!active) return;
        if (!r.ok || !d.counts)
          throw new Error("No se pudo leer el inventario");
        setSummary(d);
        onSummary?.(d);
        setProgress("");
      } catch (e: any) {
        if (active) setError(e.message);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, []);
  useEffect(() => {
    const timer = setTimeout(
      () => setFilters((f) => ({ ...f, q: query })),
      250,
    );
    return () => clearTimeout(timer);
  }, [query]);
  const params = useMemo(
    () => new URLSearchParams(filters).toString(),
    [filters],
  );
  const change = (k: string, v: string) => {
    setFilters((f) => ({ ...f, [k]: v }));
    setOffset(0);
  };
  useEffect(() => {
    if (!summary) return;
    const controller = new AbortController();
    setLoading(true);
    Promise.all(
      ["map", "list", "groups"].map(async (v) => {
        const r = await inventoryFetch(
          `/api/inventory?${params}&view=${v}&offset=${offset}`,
          { signal: controller.signal },
        );
        const d: any = await r.json();
        if (!r.ok) throw new Error(d.error);
        return d;
      }),
    )
      .then(([m, l, g]) => {
        setPoints(m.points);
        setTruncated(m.truncated);
        setRows(l.records);
        setTotal(l.total);
        setGroups(g.groups);
        setLoading(false);
      })
      .catch((e) => {
        if (e.name !== "AbortError") {
          setError(e.message);
          setLoading(false);
        }
      });
    return () => controller.abort();
  }, [summary, params, offset]);
  useEffect(() => {
    if (!selected) return;
    setDetail(null);
    const controller = new AbortController();
    inventoryFetch("/api/inventory?view=detail&id=" + encodeURIComponent(selected), {
      signal: controller.signal,
    })
      .then((r) => r.json())
      .then(setDetail)
      .catch((e) => {
        if (e.name !== "AbortError") setError(e.message);
      });
    return () => controller.abort();
  }, [selected]);
  useEffect(() => {
    if (!summary || !el.current || map.current) return;
    let alive = true;
    async function init() {
      try {
        if (!(window as any).L)
          await new Promise<void>((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "/vendor/leaflet/leaflet.js";
            script.onload = () => resolve();
            script.onerror = () =>
              reject(new Error("No se pudo cargar Leaflet"));
            document.head.appendChild(script);
          });
        if (!alive || !el.current) return;
        const L = (window as any).L;
        map.current = L.map(el.current, {
          zoomControl: false,
          preferCanvas: true,
          minZoom: 2,
          maxZoom: 17,
        }).setView([38, 15], 4);
        L.control.zoom({ position: "bottomright" }).addTo(map.current);
        L.control.scale({ imperial: false }).addTo(map.current);
        layer.current = L.layerGroup().addTo(map.current);
        setMapReady(true);
      } catch (e: any) {
        setError(e.message);
      }
    }
    init();
    return () => {
      alive = false;
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, [summary]);
  useEffect(() => {
    if (!mapReady || !map.current) return;
    const L = (window as any).L,
      b = bases[base];
    if (tiles.current) map.current.removeLayer(tiles.current);
    setTileError(false);
    let failures = 0;
    tiles.current = L.tileLayer(b[1], {
      attribution: b[2],
      maxNativeZoom: b[3],
      maxZoom: 17,
    })
      .on("tileerror", () => {
        if (++failures > 5) setTileError(true);
      })
      .addTo(map.current);
  }, [mapReady, base]);
  useEffect(() => {
    if (!mapReady || !map.current || !layer.current) return;
    const L = (window as any).L;
    function draw() {
      layer.current.clearLayers();
      const buckets = new Map<string, any[]>();
      const z = map.current.getZoom();
      for (const p of points) {
        const xy = map.current.project([p.latitude, p.longitude], z);
        const k =
          z >= 9 ? p.id : `${Math.floor(xy.x / 36)}:${Math.floor(xy.y / 36)}`;
        const list = buckets.get(k) || [];
        list.push(p);
        buckets.set(k, list);
      }
      for (const bucket of buckets.values()) {
        const first = bucket[0],
          n = bucket.length,
          lat = bucket.reduce((a, p) => a + p.latitude, 0) / n,
          lon = bucket.reduce((a, p) => a + p.longitude, 0) / n;
        const dot = L.circleMarker([lat, lon], {
          radius: n === 1 ? 5 : Math.min(18, 7 + Math.log2(n) * 1.7),
          fillColor:
            n === 1
              ? colour(
                  grouped ? first.campaign_id || "unknown" : first.provider,
                )
              : "#2b7780",
          fillOpacity: 0.78,
          weight: n === 1 ? 1 : 2,
          color: "#fff",
        });
        const label = document.createElement("span");
        label.textContent =
          n === 1
            ? `${first.name} · ${first.provider}`
            : `${n} entradas de fuentes · amplía para separarlas`;
        if (n > 1)
          dot.bindTooltip(String(n), {
            permanent: true,
            direction: "center",
            className: "cluster-label",
          });
        else dot.bindTooltip(label);
        dot.on("click", () => {
          if (n === 1) setSelected(first.id);
          else
            map.current.fitBounds(
              L.latLngBounds(bucket.map((p) => [p.latitude, p.longitude])),
              { padding: [40, 40], maxZoom: z + 3 },
            );
        });
        dot.addTo(layer.current);
      }
    }
    draw();
    map.current.on("zoomend", draw);
    return () => map.current?.off("zoomend", draw);
  }, [points, mapReady, grouped]);
  useEffect(() => {
    if (view === "map" && map.current)
      setTimeout(() => map.current?.invalidateSize(), 50);
  }, [view]);
  useEffect(() => {
    if (detail && window.innerWidth <= 700)
      document
        .getElementById("discovery-detail")
        ?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [detail]);
  async function exportInventory() {
    setPreparingCsv(true);
    try {
      const response = await inventoryFetch("/api/inventory?" + params + "&view=export");
      if (!response.ok) {
        const err: any = await response.json();
        throw new Error(err.error || "No se pudo exportar");
      }
      const blob = await response.blob();
      const objectUrl = URL.createObjectURL(blob);
      // Keep a real download link: asynchronous preparation can lose browser
      // user activation. Associate it with the exact filters to avoid stale CSVs.
      setPreparedCsv({ url: objectUrl, params });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setPreparingCsv(false);
    }
  }
  const fit = () => {
    if (points.length && map.current)
      map.current.fitBounds(
        (window as any).L.latLngBounds(
          points.map((p) => [p.latitude, p.longitude]),
        ),
        { padding: [35, 35], maxZoom: 8 },
      );
  };
  const select = (r: any) => {
    setSelected(r.id);
    if (r.latitude != null && map.current)
      map.current.setView([r.latitude, r.longitude], 7);
  };
  if (progress || (!summary && !error))
    return (
      <div className="discovery-loading">
        <div className="spinner" />
        <h2>Ampliando la mirada</h2>
        <p>{progress}</p>
      </div>
    );
  if (!summary)
    return (
      <div className="empty" role="alert">
        {error}
        <button onClick={() => location.reload()}>Reintentar</button>
      </div>
    );
  return (
    <div className="discovery-shell">
      <div className="discovery-mobile">
        <button onClick={() => setDrawer(!drawer)}>
          <SlidersHorizontal size={16} /> Filtros de sondeos
        </button>
        <span>{fmt(total)} entradas</span>
      </div>
      <aside className={"discovery-filters " + (drawer ? "open" : "")}>
        <div className="sidebar-title">
          <Database size={17} />
          <b>Descubrir registros</b>
          <button
            className="icon"
            aria-label="Cerrar filtros de sondeos"
            onClick={() => setDrawer(false)}
          >
            <X size={15} />
          </button>
        </div>
        <section>
          <label className="overline" htmlFor="core-search">
            BUSCAR SONDEO O IDENTIFICADOR
          </label>
          <div className="discovery-search">
            <Search size={15} />
            <input
              id="core-search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="MD95, ODP, lago…"
            />
          </div>
        </section>
        <section>
          <label className="overline" htmlFor="inventory-kind">
            TIPO DE ENTRADA
          </label>
          <select
            id="inventory-kind"
            value={filters.kind}
            onChange={(e) => change("kind", e.target.value)}
          >
            <option value="sites">
              Sondeos, sitios y unidades de colección
            </option>
            <option value="datasets">Referencias a datasets PANGAEA</option>
            <option value="all">Todas las entradas</option>
          </select>
          <p className="field-note">
            Un dataset puede incluir varios sondeos. Una ubicación de dataset no
            demuestra la identidad de un testigo.
          </p>
        </section>
        <section>
          <label className="overline" htmlFor="inventory-provider">
            REPOSITORIO / INVENTARIO
          </label>
          <select
            id="inventory-provider"
            value={filters.provider}
            onChange={(e) => change("provider", e.target.value)}
          >
            <option value="all">Todas las fuentes</option>
            {summary.providers.map((p: any) => (
              <option key={p.provider} value={p.provider}>
                {p.provider} · {fmt(p.count)}
              </option>
            ))}
          </select>
          <label
            className="overline discovery-spaced"
            htmlFor="inventory-realm"
          >
            ARCHIVO
          </label>
          <select
            id="inventory-realm"
            value={filters.realm}
            onChange={(e) => change("realm", e.target.value)}
          >
            <option value="all">Todos los archivos</option>
            {[
              "marine",
              "lake",
              "speleothem",
              "terrestrial",
              "continental",
              "unknown",
            ].map((v) => (
              <option key={v} value={v}>
                {
                  (
                    {
                      marine: "Marino",
                      lake: "Lacustre",
                      speleothem: "Espeleotema",
                      terrestrial: "Terrestre",
                      continental: "Continental",
                      unknown: "No clasificado",
                    } as any
                  )[v]
                }
              </option>
            ))}
          </select>
        </section>
        <section>
          <label className="overline" htmlFor="inventory-campaign">
            CAMPAÑA / CRUCERO
          </label>
          <select
            id="inventory-campaign"
            value={filters.campaign}
            onChange={(e) => change("campaign", e.target.value)}
          >
            <option value="all">Todas las campañas</option>
            <option value="unknown">Sin campaña declarada</option>
            {summary.campaigns.map((c: any) => (
              <option key={c.id} value={c.id}>
                {c.name} · {c.provider}
                {c.expedition_year ? " · " + c.expedition_year : ""} ({c.count})
              </option>
            ))}
          </select>
          <label className="group-option">
            <input
              type="checkbox"
              checked={grouped}
              onChange={(e) => setGrouped(e.target.checked)}
            />{" "}
            Agrupar por campaña
          </label>
          <p className="field-note">
            {summary.counts.campaigns} etiquetas de campaña con procedencia. Los
            estudios bibliográficos no se convierten en campañas; no se unifican
            nombres de expediciones por semejanza.
          </p>
        </section>
        <section>
          <details>
            <summary>Cobertura de la búsqueda</summary>
            <p className="field-note">
              Mediterráneo y zonas adyacentes. Rectángulo 10° O–42° E, 28–48° N.
              Incluye márgenes atlánticos y mares adyacentes.
            </p>
            {summary.coverage.map((c: any) => (
              <div className="coverage-source" key={c.provider}>
                <b>{c.provider}</b>
                <p>
                  {c.reported_core_rows
                    ? `${c.mapped_entries}/${c.reported_core_rows} filas publicadas`
                    : c.retrieved_unique_datasets
                      ? `${c.retrieved_unique_datasets} DOI · ${c.pages_retrieved} páginas`
                      : c.queried_rows
                        ? `${c.mapped_entries} testigos/perforaciones de ${c.queried_rows} muestreos`
                        : `NOAA: ${c.noaa_retrieved_studies} estudios; Neotoma: ${c.neotoma_sites} sitios`}
                </p>
                {c.limitations?.map((s: string) => (
                  <p key={s}>{s}</p>
                ))}
              </div>
            ))}
          </details>
          <p className="field-note">
            Los recuentos son entradas de fuentes, no sondeos físicos
            independientes. Posibles duplicados entre repositorios se conservan
            hasta verificar identidad.
          </p>
        </section>
        {preparedCsv?.params === params ? (
          <a
            className="catalogue-export"
            href={preparedCsv.url}
            download="medatlas-catalogue.csv"
          >
            <Download size={15} /> Descargar metadatos CSV
          </a>
        ) : (
          <button
            className="catalogue-export"
            onClick={exportInventory}
            disabled={preparingCsv}
          >
            <Download size={15} />{" "}
            {preparingCsv ? "Preparando CSV…" : "Preparar metadatos CSV"}
          </button>
        )}
      </aside>
      <main className="discovery-main">
        <div className="discovery-heading">
          <div>
            <div className="eyebrow">
              INVENTARIO ENLAZADO / MEDITERRÁNEO Y ÁREAS ADYACENTES
            </div>
            <h1>Sondeos y campañas</h1>
            <p>
              {fmt(total)} entradas encontradas · {fmt(points.length)}{" "}
              ubicaciones de fuente{loading ? " · Actualizando…" : ""}
            </p>
          </div>
          <div className="segmented">
            <button
              className={view === "map" ? "on" : ""}
              onClick={() => setView("map")}
            >
              Mapa
            </button>
            <button
              className={view === "list" ? "on" : ""}
              onClick={() => setView("list")}
            >
              Lista
            </button>
          </div>
        </div>
        {error && (
          <p role="alert" className="warning">
            {error}
          </p>
        )}
        {truncated && (
          <p role="alert">
            Mapa limitado a 20.000 entradas: reduce los filtros. La lista sigue
            paginada.
          </p>
        )}
        <div
          className="discovery-map-frame"
          style={view === "map" ? {} : { display: "none" }}
        >
          <div
            ref={el}
            className="discovery-map"
            aria-label="Mapa del inventario de sondeos"
          />
          <select
            className="discovery-basemap"
            aria-label="Capa base del inventario"
            value={base}
            onChange={(e) => setBase(e.target.value)}
          >
            {Object.entries(bases).map(([id, b]: any) => (
              <option key={id} value={id}>
                {b[0]}
              </option>
            ))}
          </select>
          <button className="discovery-fit" onClick={fit}>
            Ajustar sondeos
          </button>
          <div className="discovery-map-note">
            Agrupaciones de puntos para navegar; no son valores de proxy. Amplía
            o pulsa una agrupación.
            {tileError &&
              " El proveedor de la capa base no responde; prueba otra capa."}
          </div>
        </div>
        <div className="discovery-results">
          {grouped ? (
            <>
              <h3>Grupos de campaña · {groups.length}</h3>
              <div className="campaign-grid">
                {groups.map((g) => (
                  <button
                    key={g.id}
                    onClick={() => {
                      change("campaign", g.id);
                      setGrouped(false);
                    }}
                  >
                    <span>{g.name}</span>
                    <b>{fmt(g.count)}</b>
                    <small>{g.provider || "Sin atribución"}</small>
                  </button>
                ))}
              </div>
            </>
          ) : (
            <>
              <div className="inventory-list-title">
                <h3>
                  {view === "map"
                    ? "Entradas de la selección"
                    : "Resultados del inventario"}
                </h3>
                <span>
                  {fmt(offset + 1)}–{fmt(Math.min(offset + 60, total))} /{" "}
                  {fmt(total)}
                </span>
              </div>
              <div className="inventory-list">
                {rows.map((r) => (
                  <button
                    key={r.id}
                    className={selected === r.id ? "selected" : ""}
                    onClick={() => select(r)}
                  >
                    <MapPin size={15} />
                    <div>
                      <b>{r.name}</b>
                      <small>
                        {r.provider} ·{" "}
                        {r.campaigns?.map((c: any) => c.name).join(" / ") ||
                          "Sin campaña declarada"}
                      </small>
                    </div>
                    <span>
                      {r.record_type === "dataset" ? "Dataset" : "Metadatos"}
                    </span>
                  </button>
                ))}
              </div>
              <div className="inventory-pages">
                <button
                  disabled={offset === 0}
                  onClick={() => setOffset((n) => Math.max(0, n - 60))}
                >
                  <ChevronLeft size={16} /> Anterior
                </button>
                <button
                  disabled={offset + 60 >= total}
                  onClick={() => setOffset((n) => n + 60)}
                >
                  Siguiente <ChevronRight size={16} />
                </button>
              </div>
            </>
          )}
        </div>
      </main>
      <aside className="inspector discovery-detail" id="discovery-detail">
        <span className="overline">PROCEDENCIA DEL REGISTRO</span>
        {detail ? (
          <>
            <h2>{detail.name}</h2>
            <div className="record-tags">
              <span>{detail.provider}</span>
              <span>{detail.record_type}</span>
            </div>
            <p className="discovery-coordinates">
              {fmt(detail.latitude)}° N · {fmt(detail.longitude)}° E
            </p>
            <div className="metadata-state">
              Metadatos enlazados. La disponibilidad de una serie cuantitativa
              se revisa por separado.
            </div>
            <dl className="metadata">
              <div>
                <dt>ID de fuente</dt>
                <dd>{detail.source_id}</dd>
              </div>
              <div>
                <dt>Archivo / método</dt>
                <dd>{detail.archive_type}</dd>
              </div>
              {detail.water_depth_m != null && (
                <div>
                  <dt>Profundidad de agua</dt>
                  <dd>{detail.water_depth_m} m</dd>
                </div>
              )}
              {detail.publication_year && (
                <div>
                  <dt>Año de artículo archivado</dt>
                  <dd>{detail.publication_year}</dd>
                </div>
              )}
              {detail.dataset_publication_year && (
                <div>
                  <dt>Año de dataset</dt>
                  <dd>{detail.dataset_publication_year}</dd>
                </div>
              )}
            </dl>
            <h3>Campaña</h3>
            {detail.campaigns?.length ? (
              detail.campaigns.map((c: any) => (
                <div className="campaign-detail" key={c.id}>
                  <b>{c.name}</b>
                  <p>
                    {c.platform || c.basis || ""} {c.expedition_year || ""}
                  </p>
                  <small>{c.id}</small>
                  {safe(c.url) && (
                    <a href={c.url} target="_blank" rel="noreferrer">
                      Ficha de campaña ↗
                    </a>
                  )}
                </div>
              ))
            ) : (
              <p className="field-note">
                La fuente no declara campaña. No se infiere a partir del nombre.
              </p>
            )}
            <a
              className="source-main-link"
              href={safe(detail.source_url)}
              target="_blank"
              rel="noreferrer"
            >
              Abrir registro original <ExternalLink size={15} />
            </a>
            {safe(detail.repository_url) && (
              <a
                className="source-main-link"
                href={detail.repository_url}
                target="_blank"
                rel="noreferrer"
              >
                Repositorio de muestras ↗
              </a>
            )}
            {detail.curated_record_id && (
              <button
                className="export-data"
                onClick={() => onOpenSeries(detail.curated_record_id)}
              >
                Ver serie cuantitativa revisada
              </button>
            )}
            <h3>Proxies declarados</h3>
            <p className="field-note">
              {detail.proxies?.join(" · ") ||
                "No especificados en este inventario."}
            </p>
            <h3>Coordenadas</h3>
            <p className="field-note">{detail.coordinate_basis}</p>
            {detail.age_max_ka_bp != null && (
              <>
                <h3>Cobertura temporal declarada</h3>
                <p>
                  {fmt(detail.age_min_ka_bp)}–{fmt(detail.age_max_ka_bp)} ka BP
                </p>
                <p className="field-note">
                  {detail.age_basis}. No son edades de muestras descargadas.
                </p>
              </>
            )}
            <details className="quality">
              <summary>Localizador, licencia y control</summary>
              <p>{detail.metadata_status}</p>
              <p>{JSON.stringify(detail.source_locators)}</p>
              <p>SHA-256: {detail.raw_sha256}</p>
              <p>
                Licencia / términos:{" "}
                {typeof detail.license === "string"
                  ? detail.license
                  : JSON.stringify(detail.license) ||
                    "No declarados; revisar la fuente antes de redistribuir valores."}
              </p>
            </details>
          </>
        ) : (
          <>
            <h2>Cada punto tiene una fuente</h2>
            <p className="field-note">
              Pulsa un punto o una fila para consultar identificadores, enlaces
              originales y campaña. Los círculos agrupados reúnen ubicaciones
              para facilitar la navegación.
            </p>
            <div className="discovery-totals">
              <strong>{fmt(summary.counts.core_site_entries)}</strong>
              <span>entradas de sondeos / sitios</span>
              <strong>{fmt(summary.counts.dataset_references)}</strong>
              <span>referencias a datasets PANGAEA</span>
              <strong>{fmt(summary.counts.campaigns)}</strong>
              <span>etiquetas de campaña</span>
            </div>
            <p className="field-note">
              La colección cuantitativa contiene{" "}
              {fmt(summary.quantitative?.records || 0)} registros y{" "}
              {fmt(summary.quantitative?.observations || 0)} valores. Puedes
              abrirla en «Proxies y series».
            </p>
          </>
        )}
      </aside>
    </div>
  );
}
