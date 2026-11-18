"use client";
import { useState } from "react";
import type { useReviewPilot } from "../hooks/use-review-pilot";
import { reviewSampleKey, type ObservationRow, type ReviewSeries } from "../lib/review-pilot.mjs";
import { scientificNumber } from "../lib/format.mjs";

type Summary = { value: number | null; n: number };
type OriginalSummary = Summary & { series: ReviewSeries; target: ObservationRow[] };
const statusLabels = { pending: "Pendiente", approved: "Aprobada", rejected: "Rechazada" };
const displayValue = (value: number | null) => value === null ? "Sin valor" : scientificNumber(value);

export default function ReviewPilotPanel({
  review, original, current, recordName, unit, focusRecord,
}: {
  review: ReturnType<typeof useReviewPilot>;
  original?: OriginalSummary;
  current: Summary;
  recordName: string;
  unit: string;
  focusRecord: (id: string) => void;
}) {
  const [sampleKey, setSampleKey] = useState("");
  const [reason, setReason] = useState("");
  const [decisionNote, setDecisionNote] = useState("");
  const { state, view, setView, refresh, submit, busy, error } = review;
  if (!state?.role && !state?.localDemo && !error) return null;

  const selectedProposal = view.mode === "preview"
    ? state?.proposals.find((proposal) => proposal.id === view.proposalId)
    : undefined;
  const options = original?.target.map((row) => ({
    key: reviewSampleKey(original.series, row),
    label: `${row[0]} ka BP · ${row[1]} ${original.series.unit} · fila ${row[2]}`,
  })) ?? [];
  const availableSamples = options.filter((option) =>
    !state?.proposals.some((proposal) => proposal.sampleKey === option.key && proposal.status !== "rejected"));
  const selectedSample = availableSamples.find((option) => option.key === sampleKey)?.key ?? "";

  return (
    <section className="review-panel" aria-label="Revisión de muestras">
      <h3>Revisión de muestras</h3>
      {state?.localDemo && (
        <div className="review-actions">
          <a href="/signin-with-chatgpt?return_to=%2F%3Fpilot%3D1" target="_top">Cuenta de edición local</a>
          <a href="/signin-with-chatgpt?return_to=%2F%3Fpilot%3D1&local_account=reviewer" target="_top">Cuenta de revisión local</a>
        </div>
      )}
      {error && <p role="alert">{error}</p>}
      {(state?.role || error) && (
        <button type="button" onClick={() => void refresh()} disabled={busy}>Actualizar revisiones</button>
      )}
      {state?.role && (
        <>
          <p>{state.role === "editor" ? "Cuenta de edición" : "Cuenta de revisión"}</p>
          <label>
            Vista del mapa y la exportación
            <select
              value={view.mode === "preview" ? view.proposalId : view.mode}
              onChange={(event) => {
                const selectedView = event.target.value;
                setDecisionNote("");
                setView(selectedView === "original" || selectedView === "approved"
                  ? { mode: selectedView }
                  : { mode: "preview", proposalId: selectedView });
                const proposal = state.proposals.find((entry) => entry.id === selectedView);
                if (proposal) focusRecord(proposal.evidence.recordId);
              }}
            >
              <option value="original">Originales</option>
              <option value="approved">Con exclusiones aprobadas</option>
              {state.proposals.filter((proposal) => proposal.status === "pending").map((proposal) => (
                <option key={proposal.id} value={proposal.id}>
                  Previsualizar · {proposal.evidence.recordId} · fila {proposal.evidence.row[2]}
                </option>
              ))}
            </select>
          </label>
          {original && (
            <p aria-live="polite">
              {recordName}: {displayValue(original.value)} {unit} (n = {original.n}) →{" "}
              {displayValue(current.value)} {unit} (n = {current.n})
            </p>
          )}
          {state.role === "editor" && availableSamples.length > 0 && (
            <form onSubmit={async (event) => {
              event.preventDefault();
              if (await submit({ action: "propose", sampleKey: selectedSample, reason })) {
                setReason("");
                setSampleKey("");
              }
            }}>
              <label>
                Muestra de {recordName}
                <select required value={selectedSample} onChange={(event) => setSampleKey(event.target.value)}>
                  <option value="">Selecciona una muestra de la ventana</option>
                  {availableSamples.map((option) => <option key={option.key} value={option.key}>{option.label}</option>)}
                </select>
              </label>
              <label>Motivo de exclusión<textarea required maxLength={500} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
              <button disabled={busy || !selectedSample || !reason.trim()}>Proponer exclusión</button>
            </form>
          )}
          {state.role === "reviewer" && selectedProposal && (
            <div>
              <label>Comentario de revisión<textarea maxLength={500} value={decisionNote} onChange={(event) => setDecisionNote(event.target.value)} /></label>
              <div className="review-actions">
                {(["approved", "rejected"] as const).map((decision) => (
                  <button key={decision} type="button" disabled={busy || !decisionNote.trim()} onClick={async () => {
                    if (await submit({ action: "decide", proposalId: selectedProposal.id, decision, note: decisionNote })) {
                      setDecisionNote("");
                      setView({ mode: "approved" });
                    }
                  }}>
                    {decision === "approved" ? "Aprobar exclusión" : "Rechazar exclusión"}
                  </button>
                ))}
              </div>
            </div>
          )}
          {state.proposals.length > 0 && (
            <details open={Boolean(selectedProposal)}>
              <summary>Historial · {state.proposals.length}</summary>
              <ul>
                {state.proposals.map((proposal) => (
                  <li key={proposal.id}>
                    <b>{statusLabels[proposal.status]}</b> · {proposal.evidence.recordId} · fila {proposal.evidence.row[2]}
                    <div>Original: {String(proposal.evidence.row[5] ?? proposal.evidence.row[1])} {proposal.evidence.unit}</div>
                    <div>{proposal.evidence.row[0]} ka BP</div>
                    <div>{proposal.reason}</div>
                    {proposal.reviewNote && <div>Revisión: {proposal.reviewNote}</div>}
                  </li>
                ))}
              </ul>
            </details>
          )}
        </>
      )}
    </section>
  );
}
