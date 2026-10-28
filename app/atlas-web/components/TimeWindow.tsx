"use client";
import { useState, useEffect } from "react";
import { ChevronLeft, ChevronRight, Play, Pause } from "lucide-react";
import { moveWindow } from "../lib/timeline.mjs";
export default function TimeWindow({
  f,
  setF,
  domain: globalDomain,
  metadataRecord,
}: any) {
  const [fixed, setFixed] = useState(false),
    [width, setWidth] = useState(Math.max(0.1, f.max - f.min)),
    [playing, setPlaying] = useState(false),
    [zoom, setZoom] = useState(false);
  const [extent, setExtent] = useState("published");
  const domain =
    extent === "numeric"
      ? { ...globalDomain, max: globalDomain.numericMax }
      : globalDomain;
  const span = domain.max - domain.min;
  const setStart = (start: number, w = width) => {
    const next = moveWindow(start, w, domain);
    setWidth(next.width);
    setF((p: any) => ({ ...p, min: next.min, max: next.max }));
  };
  useEffect(() => {
    if (!playing) return;
    const timer = setInterval(
      () =>
        setF((p: any) => {
          if (p.max >= domain.max - 1e-7) {
            setPlaying(false);
            return p;
          }
          const n = moveWindow(p.min + width, width, domain);
          return { ...p, min: n.min, max: n.max };
        }),
      1000,
    );
    return () => clearInterval(timer);
  }, [playing, width, domain.min, domain.max, setF]);
  useEffect(() => {
    if (!fixed || Math.abs(f.max - f.min - width) < 1e-7) return;
    setPlaying(false);
    setWidth(Math.max(0.001, f.max - f.min));
  }, [f.min, f.max]);
  const sliderMin = zoom ? Math.max(domain.min, f.min - width * 5) : domain.min;
  const sliderMax = zoom
    ? Math.min(domain.max - width, f.min + width * 5)
    : domain.max - width;
  return (
    <section className="time-window">
      <div className="section-label">
        <label className="overline">03 / EDAD DE MUESTRA</label>
        <span className="unit-tag">ka BP</span>
      </div>
      <label className="field-note" htmlFor="timeline-extent">
        Extensión temporal
      </label>
      <select
        id="timeline-extent"
        value={extent}
        onChange={(e) => {
          const v = e.target.value;
          setPlaying(false);
          setExtent(v);
          const d =
            v === "numeric"
              ? { ...globalDomain, max: globalDomain.numericMax }
              : globalDomain;
          const n = moveWindow(f.min, Math.max(0.001, f.max - f.min), d);
          setWidth(n.width);
          setF((p: any) => ({ ...p, min: n.min, max: n.max }));
        }}
      >
        <option value="published">
          Todo el catálogo · hasta {globalDomain.max.toLocaleString("es-ES")} ka
        </option>
        <option value="numeric">
          Valores cargados · hasta{" "}
          {globalDomain.numericMax?.toLocaleString("es-ES")} ka
        </option>
      </select>
      <div className="segmented">
        <button
          className={!fixed ? "on" : ""}
          onClick={() => {
            setFixed(false);
            setPlaying(false);
          }}
        >
          Intervalo libre
        </button>
        <button
          className={fixed ? "on" : ""}
          onClick={() => {
            setFixed(true);
            setStart(f.min, Math.max(0.001, f.max - f.min));
          }}
        >
          Ventana móvil
        </button>
      </div>
      <div className="age-values">
        <label>
          Desde
          <input
            aria-label="Edad desde ka BP"
            type="number"
            step="0.1"
            value={f.min}
            onChange={(e) => {
              setPlaying(false);
              fixed
                ? setStart(Number(e.target.value))
                : setF((p: any) => ({ ...p, min: Number(e.target.value) }));
            }}
          />
        </label>
        <span>—</span>
        <label>
          Hasta
          <input
            aria-label="Edad hasta ka BP"
            type="number"
            step="0.1"
            value={f.max}
            onChange={(e) => {
              setPlaying(false);
              fixed
                ? setStart(Number(e.target.value) - width)
                : setF((p: any) => ({ ...p, max: Number(e.target.value) }));
            }}
          />
        </label>
      </div>
      {fixed ? (
        <>
          <label className="window-width">
            Ancho de ventana (ka)
            <input
              aria-label="Ancho de ventana ka"
              type="number"
              min="0.001"
              max={span}
              step="0.1"
              value={width}
              onChange={(e) => {
                const n = Number(e.target.value);
                setPlaying(false);
                if (n > 0) setStart(f.min, n);
              }}
            />
          </label>
          <input
            aria-label="Mover ventana temporal"
            type="range"
            min={sliderMin}
            max={Math.max(sliderMin, sliderMax)}
            step="0.001"
            value={f.min}
            onChange={(e) => {
              setPlaying(false);
              setStart(Number(e.target.value));
            }}
          />
          <div className="window-controls">
            <button
              aria-label="Mover ventana hacia edades más recientes"
              onClick={() => {
                setPlaying(false);
                setStart(f.min - width);
              }}
            >
              <ChevronLeft size={16} />
            </button>
            <button
              onClick={() => setPlaying(!playing)}
              aria-label={
                playing
                  ? "Pausar recorrido temporal"
                  : "Reproducir recorrido temporal"
              }
            >
              {playing ? <Pause size={14} /> : <Play size={14} />}{" "}
              {playing ? "Pausa" : "Recorrer"}
            </button>
            <button
              aria-label="Mover ventana hacia edades más antiguas"
              onClick={() => {
                setPlaying(false);
                setStart(f.min + width);
              }}
            >
              <ChevronRight size={16} />
            </button>
          </div>
          <label className="window-zoom">
            <input
              type="checkbox"
              checked={zoom}
              onChange={(e) => setZoom(e.target.checked)}
            />{" "}
            Ampliar escala alrededor de la ventana
          </label>
        </>
      ) : (
        <div className="ranges">
          <input
            aria-label="Ajustar edad mínima"
            type="range"
            min={domain.min}
            max={domain.max}
            step="0.001"
            value={f.min}
            onChange={(e) =>
              setF((p: any) => ({
                ...p,
                min: Math.min(Number(e.target.value), p.max),
              }))
            }
          />
          <input
            aria-label="Ajustar edad máxima"
            type="range"
            min={domain.min}
            max={domain.max}
            step="0.001"
            value={f.max}
            onChange={(e) =>
              setF((p: any) => ({
                ...p,
                max: Math.max(Number(e.target.value), p.min),
              }))
            }
          />
        </div>
      )}
      <div className="range-caption">
        <span>
          {(fixed && zoom ? sliderMin : domain.min).toLocaleString("es-ES")} ka
        </span>
        <span>
          {(fixed && zoom ? sliderMax + width : domain.max).toLocaleString(
            "es-ES",
          )}{" "}
          ka
        </span>
      </div>
      <div className="presets">
        <button
          onClick={() => {
            setPlaying(false);
            setWidth(10);
            setF((p: any) => ({ ...p, min: 0, max: 10 }));
          }}
        >
          Holoceno 0–10
        </button>
        <button
          onClick={() => {
            setPlaying(false);
            setWidth(2);
            setF((p: any) => ({ ...p, min: 6, max: 8 }));
          }}
        >
          6–8 ka
        </button>
      </div>
      <p className="field-note">
        Escala global, independiente del proxy. Valores numéricos hasta{" "}
        {domain.numericMax?.toLocaleString("es-ES")} ka.
        {domain.max > domain.numericMax && (
          <>
            {" "}
            Extremo ampliado por cobertura publicada: {metadataRecord}; no
            implica valores cargados.
          </>
        )}{" "}
        BP antes de 1950. Sin datos no se rellena el mapa. La referencia z
        permanece fija durante el recorrido.
      </p>
    </section>
  );
}
