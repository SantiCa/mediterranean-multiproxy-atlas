# A provenance-first, region-extensible database and visual atlas for georeferenced paleoclimate records

**Manuscript status: working draft for discussion; not submitted or publication-ready.**

## Abstract

Paleoclimate records are distributed across repositories that represent different archives, sampling conventions, chronologies and rights of reuse. Existing catalogues and synthesis products provide important discovery and visualization services, but records may remain difficult to compare across repositories and environmental settings, and a plotted curve can obscure the distinction between original measurements, published reconstructions and environmental interpretations. We describe the design of a provenance-first, region-extensible data platform intended to connect published paleoclimate records through source-specific adapters while retaining their native metadata and values. The initial case study is the Mediterranean, using a small PANGAEA seed and the thesis-linked ODP 976/977 and GP03 research context; the architecture includes marine, lacustrine, terrestrial, fluvial, speleothem and ice archives. Read-only connectors target PANGAEA, NOAA/NCEI WDS for Paleoclimatology, the Neotoma Paleoecology Database, DataCite and local LiPD packages. A canonical model separates publication year from sample age, source observations from derived values, age models from age assignments, and site location from region membership. Every retrieved payload is associated with its source URI, retrieval time and checksum; license capture and review remain resource-specific curation steps. The current prototype demonstrates source-specific retrieval interfaces and a 13-record marine/continental web pilot (22 series; 14,751 values), but it does not yet provide complete basin coverage, harmonized chronologies or an environmental reconstruction. The principal contribution proposed for evaluation is an auditable workflow and interoperable data model that can scale across regions without flattening archive-specific semantics. Evaluation must establish metadata coverage, extraction fidelity, provenance completeness, licensing and performance before claims of a production atlas or new paleoenvironmental result are warranted.

**Keywords:** paleoclimate data; data provenance; marine sediment cores; lake sediments; geospatial database; interoperability; open science; Mediterranean

## 1. Introduction

Sediment, ice, tree-ring, coral and speleothem archives record environmental change on different timescales and with distinct analytical and chronological methods. Large repositories and synthesis products make these records discoverable, but a research workflow that combines sources must still reconcile site identity, variable definitions, time scales, units, sample support, chronology, publication metadata and redistribution rights. A value presented on an age axis may be an observation with an archived age, a reconstruction from a transfer function, or a result recalculated by a later synthesis. These products are scientifically different and should not be represented by a single undifferentiated proxy field.

The Mediterranean provides a focused first region because its western and eastern basins contain contrasting marine archives, including organic-rich layers and sapropels, and because the initiating thesis applies sedimentological, geochemical, micropaleontological and ichnological evidence. The first five-record PANGAEA evidence seed is intentionally a software/curation pilot, not a representative regional compilation. It includes an ODP 977A dataset that overlaps the thesis's published methodological work. A later multiproxy Alboran publication identifies GP03PC as an additional candidate record. These prior results are source material to document and compare, not novel claims of this database project.

Our objective is to define and implement a reusable data architecture and a minimum set of connectors, while leaving the geographic domain open. We ask: (i) what source-neutral entities are required to retain provenance across archive types; (ii) which public services support reproducible discovery and data retrieval; and (iii) how can the Mediterranean pilot be expanded to continental archives without changing its central data model?

## 2. Related infrastructure

PaleoMED20 inventories Mediterranean marine sediment-core metadata for the last 20 ka and flags proxy availability; its deposited files require independent audit before quantitative reuse. WDB-Paleo provides an earlier relational Mediterranean database. PANGAEA publishes citable environmental datasets and exposes OAI-PMH metadata harvesting and DOI-based data/metadata retrieval. NOAA/NCEI WDS Paleo provides JSON study search with pagination, file previews and source-dependent download restrictions. Neotoma provides REST access to continental paleoecological sites, datasets, chronologies and downloads. LiPD is a package format for structured proxy data and metadata, not itself a repository. The World Paleoceanographic Atlas provides a global marine comparison for data and visualization. The platform is designed to link these systems without duplicating their authority or conflating a catalogue entry with a numerical series.

## 3. Requirements and design

### 3.1 Data model

The relational model distinguishes: source and source version; dataset and publication; site and core; original site aliases; region and versioned region geometry; depth frame and sample; proxy definition and original variable label; measurement method; observation; age model and assignment; transformation and its inputs; interpretation and supporting observations; license and redistribution status. A dataset may relate to several publications and a site may belong to several regions. Marine water depth and terrestrial elevation are separate quantities. Realm and archive type describe the sample context, rather than defining region-specific tables.

Every observation preserves the value and unit as received, the source row/file/column, sample support, age-scale label, chronology link, retrieval checksum and a status. Harmonized values are separate child records with a transformation identifier, code version, parameters, uncertainty handling and input links. Publication year, dataset registration/publication date, data access date and sample age occupy separate fields. Missing, censored, non-numeric and uncalibrated values retain explicit semantics.

### 3.2 Acquisition and connector interfaces

Connectors are read-only and return source-native payloads with requested and resolved URIs, access timestamp, media type and SHA-256. PANGAEA access uses DOI content negotiation and its documented OAI-PMH endpoint; its undocumented internal search endpoint is deliberately excluded. NOAA requests preserve the returned next-page link and the file-preview status. Neotoma uses documented v2 endpoints and preserves dataset, taxonomic and chronology identifiers. DataCite supports cross-repository DOI discovery only. LiPD import inspects the local BagIt-style `.lpd` package and keeps source files unchanged. A source registry states whether each adapter supports discovery, metadata, file retrieval, parsing or harmonization.

### 3.3 Geographic extensibility

The Mediterranean is configured as an initial analysis area. In the proposed full architecture, region geometries are versioned and stored separately from site records; a site can map to multiple analytical areas. Marine, lacustrine, fluvial, terrestrial, speleothem and ice archives share site/sample/provenance contracts while retaining archive-specific fields and taxonomies. New regions are added through geographic metadata and search configuration, not by modifying measurement tables.

### 3.4 Reproducible visual outputs

The implemented v1 interface filters sites and observations by realm, proxy, sample-age interval and publication year; a region selector remains planned. Charts should distinguish point measurements from continuous scans, show original units and available uncertainties, and expose whether an age model is source-published or recalculated. SVG figures are produced from a documented query and remain editable; CSV exports include citation and transformation manifests.

## 4. Prototype and initial case study

The feasibility seed comprises five PANGAEA datasets, five records, eleven selected series, and 2,684 selected values (2,646 with archived ages and 38 represented only by depth). The selection includes sedimentological, geochemical and micropaleontological examples and has explicit edge cases: negative BP ages, missing age columns, section-boundary geometry, and a depth-unit ambiguity in an ODP 977 dataset. Existing scripts retain source files, hashes and source-row locators; selected data are not treated as statistically independent replicates. The thesis review places the 977A seed in context with three published thesis articles and a subsequent GP03 multiproxy article. It also identifies overlap that must be removed before evaluating coverage or independence.

This pilot demonstrates ingestion and provenance patterns only. Five records cannot establish database completeness, Mediterranean representativeness, robust basin-scale synchronicity or an environmental mean. Values from thesis figures have not been digitized into the seed. The GP03 dataset remains a priority for the next ingestion step after source-data availability and license are confirmed.

### 4.1 Implemented web v1 (28 October 2026)

The initial five-record seed has been extended with five PANGAEA annual alkenone SST records and three NOAA WDS speleothem records (Soreq, Peqiin and Sofular). The operational D1/SQLite projection contains 13 records, 22 series and 14,751 finite values; 40 lack sample ages. The application provides record/proxy/age/publication filters, point maps, original-unit time series, fixed-reference within-series z scores, bounded optional inverse-distance fields, DOI review candidates, and CSV/editable SVG exports. All nine compact observation fields were compared between local D1 and the seed. This is extraction and software evidence, not an independent chronology audit or a validated reconstruction. The full proposed model of versioned regions, age ensembles and transformations exceeds this operational schema. See docs/WEB_V1.md and docs/curation/ for exact mappings and limits.

## 5. Evaluation plan

Before a data-descriptor submission, we will evaluate each connector against a versioned sample of source IDs and quantify: DOI/record resolution; field completeness; exact byte/hash reproducibility; native-table extraction fidelity; preservation of age model and taxonomic provenance; license capture; duplicate detection across repositories; pagination; and behavior under rate limits/service errors. A second curator will independently verify source-to-canonical mappings and selected observations. Coverage will be measured as metadata presence and quantitative series availability separately, stratified by realm, archive type, region, sample age, publication year and proxy family. Comparison to PaleoMED20 and the World Paleoceanographic Atlas will use named versions and a documented record linkage table.

For an original paleoenvironmental paper, a separate protocol will define an event hypothesis before comparison, identify chronologies independent of the target proxy, propagate age ensembles and distinguish observation, reconstruction and interpretation. A cross-basin comparison must treat western Mediterranean ORLs and eastern Mediterranean sapropels in their different depositional contexts. This database manuscript will not claim a new reconstruction unless the source records and uncertainty support that analysis.

## 6. Discussion

A global catalogue and an environmental synthesis are separate products. The database contribution is potentially publishable if source coverage, extraction fidelity, licensing, maintenance and interoperability are demonstrated beyond existing discovery systems. The science contribution requires an independent question and evidence beyond previously published thesis and follow-up results. The architecture avoids an early fixed regional schema; three curated speleothem records demonstrate a second archive type, but lake/taxonomic data and other-region scalability remain unbenchmarked. PANGAEA, NOAA and Neotoma also have different data models and reuse conditions; a single common interface should not be mistaken for semantic equivalence.

## 7. Limitations and status

This is a living design draft, not a completed database descriptor. Bounded retrieval checks returned JSON from NOAA, Neotoma and DataCite, while a PANGAEA table request initially returned HTTP 400; omitting Accept on explicit textfile retrieval resolved it, and all four latest bounded checks succeeded (see reports/live_source_check.json). Offline regression tests cover request construction, response handling and provenance, but complete schema validation and second-curator review remain pending. The initial seed is small and purpose-selected. The raw thesis archive and full-page images are excluded from the proposed public repository; source article/data permissions must be resolved separately. Q1/Q2 quartiles have not been asserted. No pooled series, recalibrated chronology, causal attribution or new regional reconstruction is reported.

## 8. Code and data availability (planned statement)

Source code, configuration, documentation and the initial open-data seed will be archived in a versioned public repository after connector checks, license review and maintainer approval. Raw third-party data will be retrieved by DOI or official API where permitted rather than copied wholesale. Each release will include a software version, data manifest and citation. A citable DOI, license for project code, API attribution, and long-term maintainer are to be selected before release.

## References (selected, to be normalized to target journal style)

- Alberico, I. et al. (2017). WDB-Paleo: a relational database for the Mediterranean paleoclimatic data. DOI: [10.1515/geo-2017-0019](https://doi.org/10.1515/geo-2017-0019).
- Casanova-Arenillas, S. et al. (2020). Applied ichnology in sedimentary geology: Python scripts as a method to automatise ichnofabric analysis in marine core images. DOI: [10.1016/j.cageo.2020.104407](https://doi.org/10.1016/j.cageo.2020.104407).
- Casanova-Arenillas, S. et al. (2021). Ichnological analysis as a tool for assessing deep-sea circulation in the westernmost Mediterranean over the last Glacial Cycle. DOI: [10.1016/j.palaeo.2020.110082](https://doi.org/10.1016/j.palaeo.2020.110082).
- Casanova-Arenillas, S. et al. (2022). Ichnological evidence for bottom water oxygenation during organic rich layer deposition in the westernmost Mediterranean over the Last Glacial Cycle. DOI: [10.1016/j.margeo.2021.106673](https://doi.org/10.1016/j.margeo.2021.106673).
- Casanova-Arenillas, S. et al. (2024). Reconstructing deep-sea oxygenation in the Western Alboran Sea Basin during Late Pleistocene-Holocene (last 37 kyrs): Insights from a multiproxy approach. DOI: [10.1016/j.palaeo.2024.112427](https://doi.org/10.1016/j.palaeo.2024.112427).
- Felden, J. et al. (2023). PANGAEA – Data Publisher for Earth & Environmental Science. DOI: [10.1038/s41597-023-02269-x](https://doi.org/10.1038/s41597-023-02269-x).
- McKay, N.P. & Emile-Geay, J. (2016). The Linked Paleo Data framework. DOI: [10.5194/cp-12-1093-2016](https://doi.org/10.5194/cp-12-1093-2016).
- Viganò, A. & Agnini, C. (2025). Mediterranean marine sediment cores database: unlocking paleoclimatic signals for the last 20,000 years. DOI: [10.1038/s41597-025-05451-5](https://doi.org/10.1038/s41597-025-05451-5).
