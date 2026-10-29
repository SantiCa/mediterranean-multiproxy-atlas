/** Newest release of the bundled manifest that D1 marks complete. The loader
 * (scripts/d1_release.py) writes the release row only after every series has its
 * full observation count, so partial loads never become visible. */
export function pickRelease(manifest, presentIds) {
  const present = new Set(presentIds);
  for (let i = manifest.releases.length - 1; i >= 0; i--) {
    const r = manifest.releases[i];
    if (present.has(r.version))
      return { ...r, seriesIds: new Set(r.series), recordIds: new Set(r.records) };
  }
  return null;
}
