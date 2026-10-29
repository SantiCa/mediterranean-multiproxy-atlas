/** Display precision adapts to small isotope ratios/fluxes. This never changes
 * stored values, statistical calculations or full-precision numeric exports. */
export function scientificNumber(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "—";
  const a = Math.abs(value);
  if (a > 0 && (a < 1e-4 || a >= 1e7))
    return value.toExponential(6).replace(".", ",").replace("e-", "e−");
  return value.toLocaleString("es-ES", { maximumSignificantDigits: 8 });
}
