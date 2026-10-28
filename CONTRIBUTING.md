# Contributing

This project is scientific infrastructure. Changes to data semantics need a short written rationale and evidence from the source documentation.

## Adding or changing a connector

1. Identify the provider's official, documented API or citable data-release format. Record the exact documentation URL and access date in `docs/source_connectors.md`.
2. Keep the adapter read-only. Fetch one or more explicitly identified records; do not crawl an undocumented search endpoint or upload data to a source.
3. Keep source-native IDs, names, units, fields, age-model labels, publication links and license statements. Unknown fields remain in the original payload.
4. Preserve the exact response bytes, SHA-256, request/final URL, media type, and retrieval time. A changed source payload creates a new version; it does not overwrite the earlier release.
5. Respect pagination, rate limits, timeouts, and per-record data restrictions. Treat third-party download links as external sources with their own license.
6. Demonstrate a connector on a small, cited source record. Review the resulting normalized data against the raw response and record missingness, mapping decisions and known limitations.
7. Add the source to `config/sources.json` and state which capabilities are implemented: discovery, metadata, file retrieval, parsing or harmonization.

## Scientific review

- Keep observation, reconstruction, transformation and interpretation distinguishable.
- Do not conflate sample ages (for example ka BP) with article publication years or repository deposit dates.
- Do not infer absence from a missing field or zero from a blank cell.
- Preserve original and harmonized values side by side; document equations, input IDs, code version and uncertainty treatment.
- Keep one source file per DOI/data version, and maintain article-to-dataset and site-alias evidence.
- Do not add thesis page images or publisher figures to the public project without rights review.

## Data and licenses

Metadata visibility does not grant permission to redistribute numerical tables, images, maps or supplements. Every imported object needs its own rights determination. The code license and data licenses are separate choices. The project has no code license selected yet.
