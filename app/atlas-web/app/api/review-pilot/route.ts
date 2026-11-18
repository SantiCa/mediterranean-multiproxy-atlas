import { env } from "cloudflare:workers";
import { and, desc, eq, ne } from "drizzle-orm";
import { reviewProposals } from "../../../db/schema";
import { getDb } from "../../../db";
import { getChatGPTUser } from "../../chatgpt-auth";
import {
  findReviewSample,
  LOCAL_REVIEW_EDITOR,
  LOCAL_REVIEW_REVIEWER,
  type ReviewProposal,
  type ReviewRole,
  type ReviewSnapshot,
  type ReviewState,
} from "../../../lib/review-pilot.mjs";

declare const __REVIEW_SNAPSHOT__: ReviewSnapshot | null;
declare const __REVIEW_LOCAL_AUTH__: boolean;

export const dynamic = "force-dynamic";

function response(body: ReviewState | { error: string }, status = 200) {
  return Response.json(body, { status, headers: { "Cache-Control": "private, no-store" } });
}

async function reviewAccount() {
  if (!__REVIEW_SNAPSHOT__ || !env.DB) return null;
  const editorEmail = __REVIEW_LOCAL_AUTH__
    ? LOCAL_REVIEW_EDITOR : env.ATLAS_REVIEW_EDITOR_EMAIL?.trim().toLowerCase();
  const reviewerEmail = __REVIEW_LOCAL_AUTH__
    ? LOCAL_REVIEW_REVIEWER : env.ATLAS_REVIEW_REVIEWER_EMAIL?.trim().toLowerCase();
  if (!editorEmail || !reviewerEmail || editorEmail === reviewerEmail) return null;
  const user = await getChatGPTUser();
  const email = user?.email.toLowerCase();
  const role: ReviewRole | null = email === editorEmail ? "editor" : email === reviewerEmail ? "reviewer" : null;
  return user && role ? { id: user.userId, role } : null;
}

async function reviewState(release: string, role: ReviewRole): Promise<ReviewState> {
  const proposals = await getDb().select().from(reviewProposals)
    .where(eq(reviewProposals.releaseId, release))
    .orderBy(desc(reviewProposals.createdAt));
  return {
    role,
    localDemo: __REVIEW_LOCAL_AUTH__,
    proposals: proposals.map((entry): ReviewProposal => ({
      id: entry.id,
      sampleKey: entry.sampleKey,
      evidence: JSON.parse(entry.evidence),
      reason: entry.reason,
      status: entry.status,
      createdAt: entry.createdAt,
      decidedAt: entry.decidedAt,
      reviewNote: entry.reviewNote,
    })),
  };
}

export async function GET(request: Request) {
  const account = await reviewAccount();
  if (!account || !__REVIEW_SNAPSHOT__) {
    return response({ role: null, localDemo: __REVIEW_LOCAL_AUTH__, proposals: [] });
  }
  const release = new URL(request.url).searchParams.get("release");
  if (release !== __REVIEW_SNAPSHOT__.version)
    return response({ error: "Actualiza la página para revisar la versión activa del catálogo." }, 409);
  return response(await reviewState(release, account.role));
}

export async function POST(request: Request) {
  if (request.headers.get("origin") !== new URL(request.url).origin)
    return response({ error: "Origen no permitido." }, 403);
  const account = await reviewAccount();
  const snapshot = __REVIEW_SNAPSHOT__;
  if (!account || !snapshot) return response({ error: "Cuenta sin acceso al piloto." }, 403);

  let payload: Record<string, unknown>;
  try {
    const body = await request.text();
    if (body.length > 4096) return response({ error: "Solicitud demasiado larga." }, 413);
    const parsed: unknown = JSON.parse(body);
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) throw new Error();
    payload = parsed as Record<string, unknown>;
  } catch {
    return response({ error: "Solicitud inválida." }, 400);
  }
  if (payload.release !== snapshot.version)
    return response({ error: "Actualiza la página para revisar la versión activa del catálogo." }, 409);

  const db = getDb();
  const now = new Date().toISOString();
  if (payload.action === "propose" && account.role === "editor") {
    const { sampleKey, reason } = payload;
    if (typeof sampleKey !== "string" || typeof reason !== "string" || !reason.trim() || reason.length > 500)
      return response({ error: "Elige una muestra e indica un motivo de hasta 500 caracteres." }, 400);
    const evidence = findReviewSample(snapshot, sampleKey);
    if (!evidence) return response({ error: "La muestra no se puede identificar en este proxy y versión." }, 422);
    const inserted = await db.insert(reviewProposals).values({
      id: crypto.randomUUID(),
      releaseId: snapshot.version,
      sampleKey,
      evidence: JSON.stringify(evidence),
      reason: reason.trim(),
      createdBy: account.id,
      createdAt: now,
    }).onConflictDoNothing().returning({ id: reviewProposals.id });
    if (!inserted.length) return response({ error: "Ya existe una exclusión pendiente o aprobada." }, 409);
  } else if (payload.action === "decide" && account.role === "reviewer") {
    const { proposalId, decision, note } = payload;
    if (typeof proposalId !== "string" || (decision !== "approved" && decision !== "rejected") ||
      typeof note !== "string" || !note.trim() || note.length > 500)
      return response({ error: "Indica una decisión y un comentario de hasta 500 caracteres." }, 400);
    const updated = await db.update(reviewProposals).set({
      status: decision,
      decidedBy: account.id,
      decidedAt: now,
      reviewNote: note.trim(),
    }).where(and(
      eq(reviewProposals.id, proposalId),
      eq(reviewProposals.releaseId, snapshot.version),
      eq(reviewProposals.status, "pending"),
      ne(reviewProposals.createdBy, account.id),
    )).returning({ id: reviewProposals.id });
    if (!updated.length) return response({ error: "Solo puedes resolver una propuesta pendiente de otra cuenta." }, 409);
  } else {
    return response({ error: "Tu cuenta no puede realizar esta acción." }, 403);
  }
  return response(await reviewState(snapshot.version, account.role));
}
