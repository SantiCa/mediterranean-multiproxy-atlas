export const dynamic = "force-dynamic";
/** Releases are no longer bundled (v5 exceeds the Workers Free script size).
 * D1 is loaded by the deploy workflow (scripts/d1_release.py), never by visitors. */
export async function POST() {
  return Response.json(
    {
      error:
        "La base científica se está cargando desde el flujo de despliegue. Vuelve a intentarlo más tarde.",
    },
    { status: 503 },
  );
}
