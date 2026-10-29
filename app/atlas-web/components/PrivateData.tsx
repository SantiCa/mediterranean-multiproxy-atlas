"use client";
import { useEffect, useMemo, useState } from "react";
import { Lock, LogOut, Trash2, Upload, RefreshCw } from "lucide-react";
import { proxyGroups, sortGroups } from "../lib/proxies.mjs";
import { parseTable, num, AGE_UNITS, REALMS, buildPrivate } from "../lib/private-data.mjs";
const REALM_LABEL: any = {
  marine: "Marino",
  lake: "Lago",
  continental: "Continental",
  speleothem: "Espeleotema",
  other: "Otro",
};
/** Owner-only upload of own datasets. Values join existing comparison groups
 * (inheriting proxy, method and unit) or a clearly private new proxy. */
export default function PrivateData({ catalog, datasets, onDatasets }: any) {
  const [session, setSession] = useState<any>(null),
    [password, setPassword] = useState(""),
    [msg, setMsg] = useState(""),
    [busy, setBusy] = useState(false),
    [file, setFile] = useState<any>(null),
    [table, setTable] = useState<any>(null),
    [rec, setRec] = useState<any>({ name: "", latitude: "", longitude: "", realm: "marine", water_depth_m: "", reference: "", notes: "" }),
    [depthCol, setDepthCol] = useState(-1),
    [ageCol, setAgeCol] = useState(-1),
    [ageUnit, setAgeUnit] = useState("ka BP"),
    [model, setModel] = useState<any>(null),
    [modelUnit, setModelUnit] = useState("ka BP"),
    [targets, setTargets] = useState<any>({});
  const groups = useMemo(
    () => sortGroups(proxyGroups({ ...catalog, series: catalog.series.filter((s: any) => !s.private) }), "records"),
    [catalog],
  );
  async function refresh() {
    const s: any = await (await fetch("/api/private/session")).json();
    setSession(s);
    if (s.owner) {
      const d: any = await (await fetch("/api/private/data")).json();
      onDatasets(d.datasets || []);
    }
  }
  useEffect(() => {
    refresh().catch(() => setSession({ configured: false, owner: false }));
  }, []);
  async function login(e: any) {
    e.preventDefault();
    setBusy(true);
    setMsg("");
    try {
      const r = await fetch("/api/private/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      const d: any = await r.json();
      if (!r.ok) throw new Error(d.error);
      setPassword("");
      await refresh();
    } catch (e: any) {
      setMsg(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function logout() {
    await fetch("/api/private/session", { method: "DELETE" });
    onDatasets([]);
    setSession({ ...session, owner: false });
  }
  async function readFile(f: File, as: "table" | "model") {
    try {
      const t = parseTable(await f.text());
      if (as === "model") {
        // Two columns: depth, age (same depth frame as the data file).
        setModel({ name: f.name, pairs: t.rows.map((r: any) => [num(r.cells[0], t.decimalComma), num(r.cells[1], t.decimalComma)]), header: t.header });
        return;
      }
      setFile(f.name);
      setTable(t);
      const find = (re: RegExp) => t.header.findIndex((h: string) => re.test(h));
      setDepthCol(find(/depth|profund/i));
      setAgeCol(find(/^age|edad/i));
      setTargets({});
      setMsg("");
    } catch (e: any) {
      setMsg(e.message);
    }
  }
  const input = () => ({
    id: "preview",
    filename: file,
    record: rec,
    table,
    depthColumn: depthCol,
    ageColumn: model ? -1 : ageCol,
    ageUnit,
    ageModel: model ? { pairs: model.pairs, unit: modelUnit, source: model.name } : null,
    groupMeta: Object.fromEntries(
      Object.values(targets)
        .filter((t: any) => t?.type === "group" && t.key)
        .map((t: any) => {
          const g: any = groups.find((x: any) => x.key === t.key);
          const { rows, ...m } = g?.series[0] || {};
          return [t.key, m];
        }),
    ),
    columns: Object.entries(targets)
      .filter(([, t]: any) => t && t.type && (t.type === "new" || t.key))
      .map(([i, t]: any) => ({ index: Number(i), target: t })),
  });
  const preview: any = useMemo((): any => {
    if (!table) return null;
    try {
      const map = new Map(groups.map((g: any) => [g.key, g.series[0]]));
      return buildPrivate(input(), map);
    } catch (e: any) {
      return { error: e.message };
    }
  }, [table, rec, depthCol, ageCol, ageUnit, model, modelUnit, targets, groups]);
  async function upload() {
    setBusy(true);
    setMsg("Validando y guardando…");
    try {
      const r = await fetch("/api/private/data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input()),
      });
      const d: any = await r.json();
      if (!r.ok) throw new Error(d.error);
      setMsg(`Guardado: ${d.series} series, ${d.values} valores.` + (d.warnings.length ? " Avisos: " + d.warnings.join(" · ") : ""));
      setTable(null);
      setModel(null);
      await refresh();
    } catch (e: any) {
      setMsg(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function remove(id: string) {
    await fetch("/api/private/data?id=" + encodeURIComponent(id), { method: "DELETE" });
    await refresh();
  }
  if (!session) return <p>Comprobando sesión…</p>;
  if (!session.owner)
    return (
      <>
        <span className="overline">ÁREA PRIVADA</span>
        <h2>Mis datos</h2>
        <p>
          Sube tus propios sondeos. Solo tú los ves, tras identificarte; se
          integran en los mismos grupos (variable, método y unidad) que la base
          pública.
        </p>
        {session.configured ? (
          <form onSubmit={login}>
            <label htmlFor="owner-pass">Contraseña</label>
            <input id="owner-pass" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={12} />
            <button className="export-data" disabled={busy} type="submit">
              <Lock size={16} /> Entrar
            </button>
          </form>
        ) : (
          <p className="add-message">
            Cuenta sin configurar: crea en GitHub (Settings → Secrets → Actions)
            el secreto <code>ATLAS_OWNER_PASSWORD</code> (mínimo 12 caracteres)
            y vuelve a desplegar.
          </p>
        )}
        {msg && <div className="add-message" role="status">{msg}</div>}
      </>
    );
  const cols = table?.header || [];
  return (
    <>
      <span className="overline">ÁREA PRIVADA</span>
      <h2>
        Mis datos{" "}
        <button className="link-button" onClick={logout}>
          <LogOut size={14} /> Salir
        </button>
      </h2>
      <h3>Mis conjuntos <span>{datasets.length}</span></h3>
      {datasets.length ? (
        datasets.map((d: any) => (
          <div className="candidate" key={d.id}>
            <div>
              <b>{d.name}</b>
              <small>
                {d.series.length} series · {d.series.reduce((n: number, s: any) => n + s.observation_count, 0)} valores · {d.filename} · {d.created_at.slice(0, 10)}
              </small>
              <small>{d.series.map((s: any) => s.variable_label + " (" + s.unit + ")").join(" · ")}</small>
            </div>
            <button className="icon" aria-label={"Borrar " + d.name} onClick={() => remove(d.id)}>
              <Trash2 size={16} />
            </button>
          </div>
        ))
      ) : (
        <p className="field-note">Aún no has subido datos.</p>
      )}
      <h3>Subir un sondeo</h3>
      <p className="field-note">
        CSV o TSV (de Excel: «Guardar como CSV»), una fila por muestra. También
        sirve un archivo de PANGAEA (.tab). Decimales con punto o coma.
      </p>
      <label className="file-input">
        <Upload size={16} /> Archivo de datos
        <input type="file" accept=".csv,.tsv,.txt,.tab" onChange={(e) => e.target.files?.[0] && readFile(e.target.files[0], "table")} />
      </label>
      {table && (
        <div className="private-form">
          <p className="field-note">{file}: {table.rows.length} filas, {cols.length} columnas.</p>
          <fieldset>
            <legend>Sondeo</legend>
            <label>Nombre<input value={rec.name} onChange={(e) => setRec({ ...rec, name: e.target.value })} /></label>
            <label>Latitud (°N)<input inputMode="decimal" value={rec.latitude} onChange={(e) => setRec({ ...rec, latitude: e.target.value })} /></label>
            <label>Longitud (°E, oeste negativo)<input inputMode="decimal" value={rec.longitude} onChange={(e) => setRec({ ...rec, longitude: e.target.value })} /></label>
            <label>Archivo
              <select value={rec.realm} onChange={(e) => setRec({ ...rec, realm: e.target.value })}>
                {REALMS.map((r: string) => <option key={r} value={r}>{REALM_LABEL[r]}</option>)}
              </select>
            </label>
            <label>Profundidad de agua (m, opcional)<input inputMode="decimal" value={rec.water_depth_m} onChange={(e) => setRec({ ...rec, water_depth_m: e.target.value })} /></label>
            <label>Referencia / DOI (opcional)<input value={rec.reference} onChange={(e) => setRec({ ...rec, reference: e.target.value })} /></label>
          </fieldset>
          <fieldset>
            <legend>Edad</legend>
            <label>Columna de profundidad
              <select value={depthCol} onChange={(e) => setDepthCol(Number(e.target.value))}>
                <option value={-1}>— ninguna —</option>
                {cols.map((h: string, i: number) => <option key={i} value={i}>{h}</option>)}
              </select>
            </label>
            {!model && (
              <>
                <label>Columna de edad
                  <select value={ageCol} onChange={(e) => setAgeCol(Number(e.target.value))}>
                    <option value={-1}>— ninguna —</option>
                    {cols.map((h: string, i: number) => <option key={i} value={i}>{h}</option>)}
                  </select>
                </label>
                <label>Unidad de edad
                  <select value={ageUnit} onChange={(e) => setAgeUnit(e.target.value)}>
                    {Object.keys(AGE_UNITS).map((u) => <option key={u}>{u}</option>)}
                  </select>
                </label>
              </>
            )}
            <label className="file-input">
              <Upload size={14} /> {model ? "Modelo: " + model.name : "…o modelo de edad aparte (profundidad, edad)"}
              <input type="file" accept=".csv,.tsv,.txt,.tab" onChange={(e) => e.target.files?.[0] && readFile(e.target.files[0], "model")} />
            </label>
            {model && (
              <>
                <label>Unidad de edad del modelo
                  <select value={modelUnit} onChange={(e) => setModelUnit(e.target.value)}>
                    {Object.keys(AGE_UNITS).map((u) => <option key={u}>{u}</option>)}
                  </select>
                </label>
                <button className="link-button" onClick={() => setModel(null)}>Quitar modelo</button>
                <p className="field-note">Interpolación lineal en profundidad, sin extrapolar fuera del modelo.</p>
              </>
            )}
          </fieldset>
          <fieldset>
            <legend>Columnas de valores</legend>
            <p className="field-note">
              Elige un grupo existente para que tus datos salgan en los mismos
              mapas (heredan proxy, método y unidad; la unidad debe coincidir),
              o crea un proxy privado.
            </p>
            {cols.map((h: string, i: number) =>
              i === depthCol || i === ageCol ? null : (
                <div key={i} className="private-col">
                  <b>{h}</b>
                  <select
                    value={targets[i]?.type === "group" ? targets[i].key : targets[i]?.type || ""}
                    onChange={(e) => {
                      const v = e.target.value;
                      setTargets({ ...targets, [i]: v === "" ? null : v === "new" ? { type: "new", label: h, unit: (h.match(/\[([^\]]+)\]/) || [])[1] || "", method: "" } : { type: "group", key: v } });
                    }}
                  >
                    <option value="">No importar</option>
                    <option value="new">Proxy privado nuevo…</option>
                    {groups.map((g: any) => (
                      <option key={g.key} value={g.key}>
                        {g.label} · {g.unit} · {g.records} reg.
                      </option>
                    ))}
                  </select>
                  {targets[i]?.type === "new" && (
                    <span className="private-new">
                      <input aria-label="Nombre del proxy" value={targets[i].label} onChange={(e) => setTargets({ ...targets, [i]: { ...targets[i], label: e.target.value } })} />
                      <input aria-label="Unidad" placeholder="unidad" value={targets[i].unit} onChange={(e) => setTargets({ ...targets, [i]: { ...targets[i], unit: e.target.value } })} />
                      <input aria-label="Método" placeholder="método / calibración" value={targets[i].method} onChange={(e) => setTargets({ ...targets, [i]: { ...targets[i], method: e.target.value } })} />
                    </span>
                  )}
                </div>
              ),
            )}
          </fieldset>
          {preview && (
            <div className="add-message" role="status">
              {preview.error
                ? "Falta o no es válido: " + preview.error
                : `Listo: ${preview.series.length} series, ${preview.values} valores.` + (preview.warnings.length ? " Avisos: " + preview.warnings.join(" · ") : "")}
            </div>
          )}
          <button className="export-data" disabled={busy || !preview || !!preview.error} onClick={upload}>
            {busy ? <RefreshCw className="spin" size={16} /> : <Upload size={16} />} Guardar en mi cuenta
          </button>
        </div>
      )}
      {msg && <div className="add-message" role="status">{msg}</div>}
    </>
  );
}
