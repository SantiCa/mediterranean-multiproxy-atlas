# Source connectors and current access conditions

This is an implementation inventory, not a claim that each provider is fully ingested. Connector status is also recorded in `config/sources.json`; update both records when behavior changes.

## Implemented read paths

| Provider | Documented access | What this repository can request | What remains provider-native |
|---|---|---|---|
| PANGAEA | DOI/content negotiation for data and metadata; OAI-PMH for bulk/incremental metadata | Dataset table by DOI; DataCite metadata XML; OAI single record and list records | Search facets and full metadata schema; data semantics, original units, attached publication, and individual terms |
| NOAA/NCEI WDS Paleo | Public GET JSON study and parameter search; page links; data-file preview | Search one study page, parameter catalogue, and file preview | Study/file decoding, download restrictions, third-party records, original terms and chronology semantics |
| Neotoma | Public REST v2 JSON site/dataset/chronology/download endpoints | Site search, dataset search, site datasets, dataset metadata/chronologies/download | Neotoma sample/taxon/chronology conventions and any site contributors' reuse terms |
| DataCite | Public REST API | DOI search and DOI metadata | Underlying measurements, licenses as rights instruments, and repository-specific data formats |
| LiPD | `.lpd` BagIt-style file with JSON-LD metadata and CSV values | Local package inventory and package checksum | Controlled-vocabulary/ontology mapping and external source identity |

### PANGAEA

PANGAEA's documented path is DOI-based retrieval and OAI-PMH; the platform does not expose a separately documented general-purpose data API. Bulk metadata harvesting may use OAI-PMH `ListRecords`, but the index must preserve set, metadata prefix, date window/resumption token, deletion behavior, raw payload and OAI identifier. DOI table download does not imply permission to reuse every associated image. The PANGAEA schema changed in August 2026; adapters should archive and version schema examples and tolerate unknown fields. See [PANGAEA Data Access and Reuse](https://wiki.pangaea.de/wiki/Data_Access_and_Reuse), [OAI-PMH](https://wiki.pangaea.de/wiki/OAI-PMH) and the [schema-transition notes](https://wiki.pangaea.de/wiki/Event-Campaign-Merge).

### NOAA/NCEI

`study/search.json` returns JSON with `study` entries and pagination; a full-study request is limited to ten studies per page. Search metadata and preview potential file downloads before transfer; the API identifies cases with third-party distribution constraints. This makes NOAA valuable for both marine and continental records, but an API search result is not equivalent to an openly redistributable data table. Follow the [official API guide](https://www.ncei.noaa.gov/access/paleo-search/api) and [WDS Paleo search page](https://www.ncei.noaa.gov/access/paleo-search/).

### Neotoma

Neotoma's v2 API exposes linked site, dataset, chronology, taxonomic and data-download records. Preserve Neotoma IDs, contributor roles, taxonomy, chronology metadata and the source publication. A canonical site coordinate cannot be treated as a coordinate for every sample or collection. Refer to the [OpenAPI documentation](https://api.neotomadb.org/api-docs/), [data-access page](https://www.neotomadb.org/index.php/data) and [raw-data manual](https://open.neotomadb.org/manual/working-with-the-raw-data.html).

### LiPD and related collections

LiPD is a versioned exchange package, not one globally authoritative repository. Preserve package checksum, schema/ontology version and original table files before interpretation. Use the [LiPD format specification](https://lipd.net/format) and the published framework description by [McKay & Emile-Geay (2016)](https://cp.copernicus.org/articles/12/1093/2016/). SISAL should enter through a named release/DOI and retain site, speleothem, age-model and isotope-table relationships.

## Integration order

1. Establish PANGAEA DOI and OAI metadata retrieval on the existing Mediterranean seed.
2. Add one NOAA study from each broad realm (marine and continental) and follow real API pagination and data-preview restrictions.
3. Add Neotoma site → dataset → chronology → download example from a lake/terrestrial record.
4. Import one LiPD package and one SISAL release, preserving raw payloads.
5. Link NOAA/PANGAEA/DataCite/Neotoma duplicates by DOI or confirmed identifiers; never treat similar titles or nearby coordinates as proof of identity.
6. Build coverage views only after validating the measurement grain and age assignments by provider.

