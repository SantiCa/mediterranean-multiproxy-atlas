import { useCallback, useEffect, useRef, useState } from "react";
import type { ReviewState, ReviewView } from "../lib/review-pilot.mjs";

const endpoint = "/api/review-pilot";
type ReviewAction =
  | { action: "propose"; sampleKey: string; reason: string }
  | { action: "decide"; proposalId: string; decision: "approved" | "rejected"; note: string };

async function readState(response: Response): Promise<ReviewState> {
  if (response.ok) return response.json();
  const detail = await response.json().catch(() => null) as { error?: string } | null;
  throw new Error(detail?.error ?? "No se pudieron cargar o guardar las revisiones.");
}

export function useReviewPilot(release: string | null) {
  const [loaded, setLoaded] = useState<{ release: string; state: ReviewState } | null>(null);
  const [selection, setSelection] = useState<{ release: string | null; view: ReviewView } | null>(null);
  const [failure, setFailure] = useState<{ release: string; message: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const requestSequence = useRef(0);

  const refresh = useCallback(async (signal?: AbortSignal) => {
    if (!release) return;
    const sequence = ++requestSequence.current;
    try {
      const response = await fetch(`${endpoint}?release=${encodeURIComponent(release)}`, { signal });
      const state = await readState(response);
      if (!signal?.aborted && sequence === requestSequence.current) {
        setLoaded({ release, state });
        setFailure(null);
      }
    } catch (error) {
      if (!signal?.aborted && sequence === requestSequence.current)
        setFailure({ release, message: (error as Error).message });
    }
  }, [release]);

  useEffect(() => {
    const controller = new AbortController();
    void refresh(controller.signal);
    return () => controller.abort();
  }, [refresh]);

  async function submit(action: ReviewAction) {
    if (!release || busy) return false;
    const sequence = ++requestSequence.current;
    setBusy(true);
    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ release, ...action }),
      });
      const state = await readState(response);
      if (sequence === requestSequence.current) {
        setLoaded({ release, state });
        setFailure(null);
      }
      return true;
    } catch (error) {
      if (sequence === requestSequence.current)
        setFailure({ release, message: (error as Error).message });
      return false;
    } finally {
      setBusy(false);
    }
  }

  const state = loaded?.release === release ? loaded?.state ?? null : null;
  const requested = selection?.release === release ? selection?.view : undefined;
  const view: ReviewView = requested && (requested.mode !== "preview" ||
    state?.proposals.some((proposal) => proposal.id === requested.proposalId && proposal.status === "pending"))
    ? requested
    : { mode: "approved" };
  return {
    state,
    view,
    setView: (view: ReviewView) => setSelection({ release, view }),
    error: failure?.release === release ? failure?.message ?? "" : "",
    refresh: () => refresh(),
    submit,
    busy,
  };
}
