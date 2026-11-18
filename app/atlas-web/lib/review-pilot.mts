export const REVIEW_GROUP = '["alkenone_SST","sst_alkenone_mueller1998_annual","°C"]';
export const LOCAL_REVIEW_EDITOR = "seedy@sites.test";
export const LOCAL_REVIEW_REVIEWER = "reviewer@sites.test";

export type ReviewRole = "editor" | "reviewer";
export type ReviewStatus = "pending" | "approved" | "rejected";
export type ObservationRow = [number | null, number, number, ...unknown[]];
export type ReviewSeries = {
  id: string;
  record_id: string;
  unit: string;
  raw_sha256?: string;
  source_url?: string;
  rows: ObservationRow[];
};
export type ReviewSnapshot = {
  version: string;
  group: string;
  series: ReviewSeries[];
};
export type SampleEvidence = {
  seriesId: string;
  recordId: string;
  unit: string;
  sourceHash: string | null;
  sourceUrl: string | null;
  row: ObservationRow;
};
export type ReviewProposal = {
  id: string;
  sampleKey: string;
  evidence: SampleEvidence;
  reason: string;
  status: ReviewStatus;
  createdAt: string;
  decidedAt: string | null;
  reviewNote: string | null;
};
export type ReviewView =
  | { mode: "original" | "approved" }
  | { mode: "preview"; proposalId: string };

export type ReviewState = {
  role: ReviewRole | null;
  localDemo: boolean;
  proposals: ReviewProposal[];
};

export function reviewSampleKey(series: ReviewSeries, row: ObservationRow) {
  return JSON.stringify([series.id, series.raw_sha256 ?? null, row]);
}

export function findReviewSample(snapshot: ReviewSnapshot, key: string): SampleEvidence | null {
  let match: SampleEvidence | null = null;
  for (const series of snapshot.series) {
    for (const row of series.rows) {
      if (reviewSampleKey(series, row) !== key || !Number.isFinite(row[0]) || !Number.isFinite(row[1]))
        continue;
      if (match) return null;
      match = {
        seriesId: series.id,
        recordId: series.record_id,
        unit: series.unit,
        sourceHash: series.raw_sha256 ?? null,
        sourceUrl: series.source_url ?? null,
        row,
      };
    }
  }
  return match;
}

export function appliedReviewExclusions(proposals: ReviewProposal[], view: ReviewView) {
  if (view.mode === "original") return new Map<string, ReviewProposal>();
  return new Map(proposals
    .filter((proposal) => proposal.status === "approved" ||
      (view.mode === "preview" && proposal.id === view.proposalId && proposal.status === "pending"))
    .map((proposal) => [proposal.sampleKey, proposal]));
}

export function applyReviewExclusions<Series extends ReviewSeries>(
  series: Series[],
  exclusions: ReadonlyMap<string, ReviewProposal>,
): Series[] {
  if (!exclusions.size) return series;
  const affected = new Set([...exclusions.values()].map((proposal) => proposal.evidence.seriesId));
  return series.map((entry) => affected.has(entry.id)
    ? { ...entry, rows: entry.rows.filter((row) => !exclusions.has(reviewSampleKey(entry, row))) }
    : entry);
}

export function reviewExportSamples(
  series: ReviewSeries,
  target: ObservationRow[],
  exclusions: ReadonlyMap<string, ReviewProposal>,
  ageWindow: { min: number; max: number; refMin: number; refMax: number; mode: string },
) {
  const included = target.map((row) => ({ row, exclusion: null as ReviewProposal | null, inWindow: true }));
  const excluded = [...exclusions.values()].flatMap((proposal) => {
    if (proposal.evidence.seriesId !== series.id) return [];
    const row = proposal.evidence.row;
    const age = row[0];
    if (age === null) return [];
    const inWindow = age >= ageWindow.min && age <= ageWindow.max;
    const inReference = ageWindow.mode === "z" && age >= ageWindow.refMin && age <= ageWindow.refMax;
    return inWindow || inReference ? [{ row, exclusion: proposal, inWindow }] : [];
  });
  return [...included, ...excluded];
}
