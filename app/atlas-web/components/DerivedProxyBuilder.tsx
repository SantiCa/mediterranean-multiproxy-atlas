"use client";
import { useEffect, useMemo, useRef, useState } from "react";
import { abundanceTable, computeDerivedProxy, DERIVED_VERSION, isAbundance, planDerivedProxy } from "../lib/derived-proxies.mjs";
import { groupKey } from "../lib/proxies.mjs";

const STORAGE = "medatlas-derived-proxy-recipes-v1";
function saveJSON(name: string, value: any) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(new Blob([JSON.stringify(value, null, 2)], { type: "application/json" }));
  link.download = name;
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

export default function DerivedProxyBuilder({ catalog, privateSets, onChange, onSelect }: any) {
  const [recipes, setRecipes] = useState<any[]>([]), [sets, setSets] = useState<any[]>([]);
  const [record, setRecord] = useState(""), [table, setTable] = useState("");
  const [label, setLabel] = useState(""), [operation, setOperation] = useState("sum");
  const [numerator, setNumerator] = useState<string[]>([]), [denominator, setDenominator] = useState<string[]>([]);
  const [allCompatible, setAllCompatible] = useState(true), [confirmed, setConfirmed] = useState(false);
  const [busy, setBusy] = useState(false), [message, setMessage] = useState("");
  const dialog = useRef<HTMLDialogElement>(null), generation = useRef(0);
  const eligible = useMemo(() => catalog.series.filter(isAbundance), [catalog]);
  const records = catalog.records.filter((item: any) => eligible.some((series: any) => series.record_id === item.id));
  const currentRecord = record || records[0]?.id || "";
  const tables = [...new Map(eligible.filter((series: any) => series.record_id === currentRecord).map((series: any) => [abundanceTable(series), series])).entries()] as [string, any][];
  const currentTable = tables.some(([key]) => key === table) ? table : tables[0]?.[0];
  const terms = eligible.filter((series: any) => abundanceTable(series) === currentTable);

  async function rebuild(next: any[], selectId?: string) {
    const run = ++generation.current;
    setBusy(true);
    setMessage("");
    const results: any[] = [], problems: string[] = [], cache = new Map();
    for (const recipe of next) {
      try {
        const plans = planDerivedProxy(catalog, recipe);
        const inputs = [...new Map(plans.flatMap((plan: any) => [...plan.numerator, ...plan.denominator]).map((term: any) => [term.id, term])).values()] as any[];
        const keys = [...new Set(inputs.filter((term) => !term.private).map(groupKey))];
        for (let offset = 0; offset < keys.length; offset += 6) {
          await Promise.all(keys.slice(offset, offset + 6).map(async (key) => {
            if (cache.has(key)) return;
            const file = catalog.snapshot?.groups[key];
            if (!file) throw new Error("Falta un archivo de observaciones de la receta.");
            const response = await fetch("/snapshot/obs/" + file);
            if (!response.ok) throw new Error("No se pudieron cargar las observaciones.");
            const body: any = await response.json();
            if (body.version !== catalog.release.id || body.group !== key) throw new Error("El snapshot no coincide con la colección actual.");
            cache.set(key, body.series);
          }));
        }
        if (generation.current !== run) return;
        const loaded = [...keys.flatMap((key) => cache.get(key) || []), ...privateSets.flatMap((entry: any) => entry.series)];
        const byId = new Map(loaded.map((term: any) => [term.id, term]));
        results.push(computeDerivedProxy({ ...catalog, series: inputs.map((term) => {
          if (!byId.has(term.id)) throw new Error("No se ha encontrado una serie de entrada.");
          return byId.get(term.id);
        }) }, recipe));
      } catch (error: any) {
        problems.push(`${recipe.label || "Receta"}: ${error.message}`);
      }
    }
    if (generation.current !== run) return;
    setSets(results);
    onChange(results);
    setMessage(problems.join(" · "));
    setBusy(false);
    const selected = results.find((entry) => entry.recipe.id === selectId);
    if (selected) { onSelect(selected.series[0]); dialog.current?.close(); }
  }
  useEffect(() => {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE) || "[]");
      if (!Array.isArray(saved) || saved.length > 20) throw new Error("Recetas guardadas no válidas.");
      setRecipes(saved);
      void rebuild(saved);
    } catch (error: any) { setMessage(error.message); }
    return () => { generation.current++; };
  }, [catalog, privateSets]);

  function persist(next: any[], selectId?: string) {
    if (next.length > 20) { setMessage("Máximo 20 recetas por navegador."); return; }
    setRecipes(next);
    try { localStorage.setItem(STORAGE, JSON.stringify(next)); }
    catch { setMessage("No se pudieron guardar las recetas en este navegador."); }
    void rebuild(next, selectId);
  }
  function create(event: any) {
    event.preventDefault();
    const ids = [...new Set([...numerator, ...(operation === "sum" ? [] : denominator)])];
    const recipe = { id: crypto.randomUUID(), version: DERIVED_VERSION, label, operation, numerator,
      denominator: operation === "sum" ? [] : denominator, allCompatible, disjointConfirmed: confirmed,
      source_release: catalog.release.id, input_hashes: Object.fromEntries(ids.map((id) => [id, catalog.series.find((term: any) => term.id === id)?.raw_sha256])) };
    try { planDerivedProxy(catalog, recipe); persist([...recipes, recipe], recipe.id); }
    catch (error: any) { setMessage(error.message); }
  }
  const toggle = (ids: string[], id: string) => ids.includes(id) ? ids.filter((value) => value !== id) : [...ids, id];
  function resetTerms() { setNumerator([]); setDenominator([]); setConfirmed(false); }

  return <section className="derived-section">
    <button className="proxy-open" onClick={() => dialog.current?.showModal()}>Crear proxy de especies</button>
    <p className="field-note">Sumas, A/B o 100 × A/(A+B). Recetas locales; cálculo por muestra, sin interpolar.</p>
    {busy && <p role="status">Calculando muestras y conservando originales…</p>}
    {message && <p role="alert" className="derived-error">{message}</p>}
    {recipes.map((recipe) => {
      const result = sets.find((entry) => entry.recipe.id === recipe.id);
      return <div className="derived-saved" key={recipe.id}>
        <b>{recipe.label}</b>
        {result && <>
          <p>{result.series.length} tablas · {result.series.reduce((count: number, term: any) => count + term.rows.length, 0)} valores calculados</p>
          <button onClick={() => onSelect(result.series[0])}>Usar en mapa y series</button>
          <details><summary>Fórmula, originales y exclusiones</summary>
            <p>{result.series[0].derivation.formula}</p>
            <p>{result.series.reduce((count: number, term: any) => count + term.derivation.exclusions.length, 0)} muestras excluidas. Incertidumbre del valor sin propagar.</p>
            <button onClick={() => saveJSON("medatlas-derived-audit.json", { release: catalog.release.id, ...result })}>Descargar auditoría y originales JSON</button>
          </details>
        </>}
        <button disabled={busy} onClick={() => persist(recipes.filter((entry) => entry.id !== recipe.id))}>Eliminar receta</button>
      </div>;
    })}
    {!!recipes.length && <button onClick={() => saveJSON("medatlas-proxy-recipes.json", recipes)}>Exportar recetas JSON</button>}
    <label className="derived-import">Importar recetas JSON<input type="file" accept="application/json,.json" disabled={busy} onChange={async (event) => {
      const file = event.target.files?.[0];
      if (!file) return;
      try {
        if (file.size > 100000) throw new Error("Archivo de recetas demasiado grande.");
        const imported = JSON.parse(await file.text());
        if (!Array.isArray(imported) || imported.some((entry) => !entry.input_hashes)) throw new Error("Se requiere una lista de recetas con hashes originales.");
        imported.forEach((entry) => planDerivedProxy(catalog, entry));
        persist([...new Map([...recipes, ...imported].map((entry) => [entry.id, entry])).values()]);
      } catch (error: any) { setMessage(error.message); }
      event.target.value = "";
    }} /></label>
    <dialog ref={dialog} className="derived-dialog" aria-labelledby="derived-title">
      <header><h2 id="derived-title">Crear un proxy de abundancias</h2><button type="button" onClick={() => dialog.current?.close()} aria-label="Cerrar creador">Cerrar</button></header>
      <p>Una asociación expresa la fórmula que definas; su interpretación ambiental requiere justificación. Porcentajes con sumas distintas y taxones de tablas diferentes permanecen separados.</p>
      <form onSubmit={create}>
        <label>Nombre del proxy<input required maxLength={160} value={label} onChange={(event) => setLabel(event.target.value)} placeholder="Ej.: suma de Abies y Fagus" /></label>
        <label>Sondeo de referencia<select aria-label="Sondeo de referencia" value={currentRecord} onChange={(event) => { setRecord(event.target.value); setTable(""); resetTerms(); }}>
          {records.map((item: any) => <option key={item.id} value={item.id}>{item.name} · {item.provider}</option>)}
        </select></label>
        <label>Tabla, método, unidad y contexto<select aria-label="Tabla, método, unidad y contexto" value={currentTable || ""} onChange={(event) => { setTable(event.target.value); resetTerms(); }}>
          {tables.map(([key, term]) => <option key={key} value={key}>{term.method} · {term.unit} · {term.comparison_context_key || "conteos nativos"} · {term.raw_sha256?.slice(0, 8)}</option>)}
        </select></label>
        {!terms.length && <p>No hay abundancias con contexto verificable. Los porcentajes sin denominador documentado requieren curación previa.</p>}
        <label>Operación<select aria-label="Operación" value={operation} onChange={(event) => { setOperation(event.target.value); setDenominator([]); setConfirmed(false); }}>
          <option value="sum">Suma A (unidad original)</option><option value="ratio">Relación A/B (adimensional)</option><option value="share">Proporción 100 × A/(A+B) (%)</option>
        </select></label>
        <div className="derived-terms">{["A", ...(operation === "sum" ? [] : ["B"])].map((side) => <fieldset key={side}>
          <legend>Suma {side}</legend><div>{terms.map((term: any) => <label key={term.id}>
            <input type="checkbox" checked={(side === "A" ? numerator : denominator).includes(term.id)} onChange={() => {
              if (side === "A") setNumerator(toggle(numerator, term.id)); else setDenominator(toggle(denominator, term.id));
              setConfirmed(false);
            }} />{term.taxon || term.parameter_name_pangaea || term.label} [{term.unit}]
          </label>)}</div>
        </fieldset>)}</div>
        <label className="derived-check"><input type="checkbox" checked={allCompatible} onChange={(event) => setAllCompatible(event.target.checked)} />Aplicar también a tablas de otros sondeos con todos los mismos taxones, método, unidad y contexto.</label>
        <label className="derived-check"><input type="checkbox" required checked={confirmed} onChange={(event) => setConfirmed(event.target.checked)} />He revisado que los taxones/grupos de cada suma no se solapan (p. ej., AP ya puede incluir Pinus).</label>
        <p>Solo muestras completas y localizadores coincidentes; denominador cero excluido. No se transforma un censo en porcentaje del total sin declarar ese total. Recetas guardadas en este navegador y exportables.</p>
        {message && <p role="alert" className="derived-error">{message}</p>}
        <button type="submit" className="proxy-select" disabled={busy || !terms.length}>Calcular y usar proxy</button>
      </form>
    </dialog>
  </section>;
}
