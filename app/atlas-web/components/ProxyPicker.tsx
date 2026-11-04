"use client";
import { useState, useEffect, useMemo, useRef } from "react";
import { createPortal } from "react-dom";
import { Search, X, Star, SlidersHorizontal } from "lucide-react";
import { proxyCatalog as proxyGroups, filterGroups, sortGroups } from "../lib/proxies.mjs";
const number = (n: number) =>
  n.toLocaleString("es-ES", { maximumFractionDigits: 3 });
export default function ProxyPicker({
  catalog,
  selectedKey,
  onSelect,
  f,
  setF,
}: any) {
  const [open, setOpen] = useState(false),
    [q, setQ] = useState({
      search: "",
      family: "all",
      variable: "all",
      method: "all",
      unit: "all",
      overlap: false,
      favoritesOnly: false,
      sort: "records",
      aggregates: true,
      minRecords: 2,
    }),
    [favorites, setFavorites] = useState<string[]>([]),
    [page, setPage] = useState(0);
  const dialog = useRef<HTMLDivElement>(null);
  useEffect(() => {
    try {
      setFavorites(
        JSON.parse(localStorage.getItem("medatlas-proxy-favorites-v1") || "[]"),
      );
    } catch {}
  }, []);
  const groups = useMemo(
    () => proxyGroups(catalog, f),
    [catalog, f.provider, f.realm, f.yearMin, f.yearMax, f.chronology],
  );
  const all = useMemo(() => proxyGroups(catalog), [catalog]);
  const selected = all.find((g: any) => g.key === selectedKey);
  const scoped = groups.find((g: any) => g.key === selectedKey);
  const matches = sortGroups(
    filterGroups(groups, {
      ...q,
      favorites,
      min: f.min,
      max: f.max,
    }),
    q.sort,
  );
  const familyOptions = [...new Set(groups.map((g: any) => g.family))].sort();
  const variableOptions = [
    ...new Set(
      groups
        .filter((g: any) => q.family === "all" || g.family === q.family)
        .map((g: any) => g.variable),
    ),
  ].sort();
  const methodOptions = [
    ...new Set(
      groups
        .filter(
          (g: any) =>
            (q.family === "all" || g.family === q.family) &&
            (q.variable === "all" || g.variable === q.variable),
        )
        .map((g: any) => g.method),
    ),
  ].sort();
  const unitOptions = [
    ...new Set(
      groups
        .filter(
          (g: any) =>
            (q.family === "all" || g.family === q.family) &&
            (q.variable === "all" || g.variable === q.variable) &&
            (q.method === "all" || g.method === q.method),
        )
        .map((g: any) => g.unit),
    ),
  ].sort();
  useEffect(() => {
    setPage(0);
  }, [q, f.provider, f.realm, f.yearMin, f.yearMax, f.chronology]);
  useEffect(() => {
    if (!open) return;
    const old = document.activeElement as HTMLElement,
      controls = () =>
        Array.from(
          dialog.current?.querySelectorAll("button,input,select,a[href]") || [],
        ) as HTMLElement[];
    controls()[0]?.focus();
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
      if (e.key === "Tab") {
        const c = controls(),
          a = c[0],
          b = c.at(-1);
        if (e.shiftKey && document.activeElement === a) {
          e.preventDefault();
          b?.focus();
        } else if (!e.shiftKey && document.activeElement === b) {
          e.preventDefault();
          a?.focus();
        }
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      old?.focus();
    };
  }, [open]);
  function favorite(key: string) {
    const next = favorites.includes(key)
      ? favorites.filter((x) => x !== key)
      : [...favorites, key];
    setFavorites(next);
    try {
      localStorage.setItem("medatlas-proxy-favorites-v1", JSON.stringify(next));
    } catch {}
  }
  const choose = (g: any) => {
    onSelect(g);
    setOpen(false);
  };
  const reset = () =>
    setQ({
      search: "",
      family: "all",
      variable: "all",
      method: "all",
      unit: "all",
      overlap: false,
      favoritesOnly: false,
      sort: "records",
      aggregates: true,
      minRecords: 2,
    });
  return (
    <section className="proxy-picker">
      <span className="overline">01 / EXPLORADOR DE PROXIES</span>
      <button className="proxy-open" onClick={() => setOpen(true)}>
        <Search size={16} /> Buscar y seleccionar proxy
      </button>
      {selected && (
        <div className="proxy-selected">
          <small>{selected.family}</small>
          <b>{selected.label}</b>
          <span>
            {selected.unit} · {scoped?.records || 0} registros ·{" "}
            {number(scoped?.count || 0)} valores con los filtros activos
          </span>
          <details open={!!selected.aggregate}>
            <summary>Método y compatibilidad</summary>
            <p>{selected.method}</p>
            {selected.aggregate ? (
              <p className="aggregate-note">
                Agrupación de {selected.members.length} grupos que miden la
                misma variable en {selected.unit}. Métodos, calibraciones y
                estaciones son distintos y no se armonizan: cada punto conserva
                el suyo. Para comparar anomalías usa «z por sondeo».
              </p>
            ) : (
              <p>
                Solo se combinan series de este grupo. Compartir unidad no
                demuestra equivalencia.
              </p>
            )}
          </details>
          {Number.isFinite(selected.min) && (
            <button
              className="proxy-coverage"
              onClick={() =>
                setF((p: any) => ({
                  ...p,
                  min: selected.min,
                  max: selected.max,
                  mode: "raw",
                }))
              }
            >
              Ver cobertura: {number(selected.min)}–{number(selected.max)} ka
            </button>
          )}
        </div>
      )}
      <p className="field-note">
        Familia → variable → método → unidad. Ordena por nº de sondeos o de datos y agrupa métodos que miden lo mismo (p. ej. SST) para mapas más completos. Busca también por sondeo, especie,
        calibración o δ18O / d18O. Los favoritos se guardan en este navegador.
      </p>
      {open &&
        createPortal(
          <div
            className="modal-backdrop proxy-backdrop"
            onClick={() => setOpen(false)}
          >
            <div
              ref={dialog}
              role="dialog"
              aria-modal="true"
              aria-label="Explorador de proxies"
              className="proxy-dialog"
              onClick={(e) => e.stopPropagation()}
            >
              <header>
                <div>
                  <span className="overline">COLECCIÓN CUANTITATIVA</span>
                  <h2>Encontrar un proxy</h2>
                  <p>
                    Selecciona una variable y un grupo comparable para el mapa y
                    las series.
                  </p>
                </div>
                <button
                  className="icon"
                  aria-label="Cerrar explorador de proxies"
                  onClick={() => setOpen(false)}
                >
                  <X />
                </button>
              </header>
              <div className="proxy-search">
                <Search size={18} />
                <input
                  autoFocus
                  aria-label="Buscar proxies"
                  placeholder="Temperatura, Ti, d18O, Müller, Mondsee…"
                  value={q.search}
                  onChange={(e) => setQ({ ...q, search: e.target.value })}
                />
              </div>
              <div className="proxy-facets">
                <label>
                  Familia
                  <select
                    aria-label="Familia del proxy"
                    value={q.family}
                    onChange={(e) =>
                      setQ({
                        ...q,
                        family: e.target.value,
                        variable: "all",
                        method: "all",
                        unit: "all",
                      })
                    }
                  >
                    <option value="all">Todas las familias</option>
                    {familyOptions.map((v: any) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Variable
                  <select
                    aria-label="Variable del proxy"
                    value={q.variable}
                    onChange={(e) =>
                      setQ({
                        ...q,
                        variable: e.target.value,
                        method: "all",
                        unit: "all",
                      })
                    }
                  >
                    <option value="all">Todas las variables</option>
                    {variableOptions.map((v: any) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Método / calibración
                  <select
                    aria-label="Método del proxy"
                    value={q.method}
                    onChange={(e) =>
                      setQ({ ...q, method: e.target.value, unit: "all" })
                    }
                  >
                    <option value="all">Todos los métodos</option>
                    {methodOptions.map((v: any) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
                <label>
                  Unidad
                  <select
                    aria-label="Unidad del proxy"
                    value={q.unit}
                    onChange={(e) => setQ({ ...q, unit: e.target.value })}
                  >
                    <option value="all">Todas las unidades</option>
                    {unitOptions.map((v: any) => (
                      <option key={v}>{v}</option>
                    ))}
                  </select>
                </label>
              </div>
              <div className="proxy-options">
                <label>
                  Ordenar por{" "}
                  <select
                    aria-label="Ordenar proxies"
                    value={q.sort}
                    onChange={(e) => setQ({ ...q, sort: e.target.value })}
                  >
                    <option value="records">Nº de registros (sondeos)</option>
                    <option value="values">Nº de datos</option>
                    <option value="name">Nombre</option>
                  </select>
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={q.aggregates}
                    onChange={(e) =>
                      setQ({ ...q, aggregates: e.target.checked })
                    }
                  />{" "}
                  Agrupar proxies que miden lo mismo
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={q.minRecords > 1}
                    onChange={(e) =>
                      setQ({ ...q, minRecords: e.target.checked ? 2 : 0 })
                    }
                  />{" "}
                  Solo con ≥2 registros (mapas)
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={q.favoritesOnly}
                    onChange={(e) =>
                      setQ({ ...q, favoritesOnly: e.target.checked })
                    }
                  />{" "}
                  Solo favoritos
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={q.overlap}
                    onChange={(e) => setQ({ ...q, overlap: e.target.checked })}
                  />{" "}
                  Cobertura solapada con {number(f.min)}–{number(f.max)} ka
                </label>
                <button onClick={reset}>Limpiar búsqueda</button>
              </div>
              <p className="proxy-results">
                {matches.length} grupos compatibles disponibles · {all.length}{" "}
                en la colección. Se aplican los filtros de fuente, archivo,
                cronología y año del panel. El solapamiento de cobertura no
                garantiza muestras dentro de la ventana.
              </p>
              <div className="proxy-cards">
                {matches.slice(page * 18, page * 18 + 18).map((g: any) => (
                  <article
                    key={g.key}
                    className={
                      (g.key === selectedKey ? "selected " : "") +
                      (g.aggregate ? "aggregate" : "")
                    }
                  >
                    <div className="proxy-card-top">
                      <small>
                        {g.aggregate ? "AGRUPADO · " : ""}
                        {g.family}
                      </small>
                      <button
                        className="icon"
                        aria-label={
                          favorites.includes(g.key)
                            ? "Quitar favorito " + g.label
                            : "Guardar favorito " + g.label
                        }
                        aria-pressed={favorites.includes(g.key)}
                        onClick={() => favorite(g.key)}
                      >
                        <Star
                          size={16}
                          fill={
                            favorites.includes(g.key) ? "currentColor" : "none"
                          }
                        />
                      </button>
                    </div>
                    <h3>{g.label}</h3>
                    <b>{g.unit}</b>
                    <p className="proxy-method">{g.method}</p>
                    <div className="proxy-metrics">
                      {g.records} registros · {g.series.length} series ·{" "}
                      {number(g.count)} valores
                    </div>
                    <p>
                      {Number.isFinite(g.min)
                        ? number(g.min) + "–" + number(g.max) + " ka BP"
                        : "Edad no disponible"}
                    </p>
                    <button className="proxy-select" onClick={() => choose(g)}>
                      {g.key === selectedKey
                        ? "Seleccionado"
                        : "Usar este grupo"}
                    </button>
                  </article>
                ))}
              </div>
              {!matches.length && (
                <div className="empty">
                  No hay grupos con estos filtros. Amplía la búsqueda o cambia
                  los filtros del panel.
                </div>
              )}
              <footer>
                <button disabled={!page} onClick={() => setPage((p) => p - 1)}>
                  Anterior
                </button>
                <span>
                  Página {page + 1} /{" "}
                  {Math.max(1, Math.ceil(matches.length / 18))}
                </span>
                <button
                  disabled={(page + 1) * 18 >= matches.length}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Siguiente
                </button>
              </footer>
            </div>
          </div>,
          document.body,
        )}
    </section>
  );
}
