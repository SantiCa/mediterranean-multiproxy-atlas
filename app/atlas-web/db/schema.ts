import {
  sqliteTable,
  text,
  real,
  integer,
  index,
} from "drizzle-orm/sqlite-core";

export const records = sqliteTable("atlas_records", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  realm: text("realm").notNull(),
  latitude: real("latitude").notNull(),
  longitude: real("longitude").notNull(),
  metadata: text("metadata_json").notNull(),
});
export const series = sqliteTable("atlas_series", {
  id: text("id").primaryKey(),
  recordId: text("record_id")
    .notNull()
    .references(() => records.id),
  proxy: text("proxy").notNull(),
  label: text("label").notNull(),
  unit: text("unit").notNull(),
  metadata: text("metadata_json").notNull(),
});
export const observations = sqliteTable(
  "atlas_observations",
  {
    id: text("id").primaryKey(),
    seriesId: text("series_id")
      .notNull()
      .references(() => series.id),
    age: real("age_ka_bp"),
    value: real("value").notNull(),
    sourceRow: integer("source_row").notNull(),
    sourceLine: integer("source_line"),
    originalAge: text("original_age"),
    originalValue: text("original_value"),
    ageUncertainty: real("age_uncertainty_ka"),
    valueUncertainty: real("value_uncertainty"),
    depthOriginal: text("depth_original"),
  },
  (table) => [index("atlas_series_age_idx").on(table.seriesId, table.age)],
);
export const releases = sqliteTable("atlas_releases", {
  id: text("id").primaryKey(),
  count: integer("observation_count").notNull(),
  importedAt: text("imported_at").notNull(),
});
export const candidates = sqliteTable("atlas_candidates", {
  id: text("id").primaryKey(),
  doi: text("doi").notNull().unique(),
  title: text("title").notNull(),
  state: text("state").notNull().default("pending_review"),
  metadata: text("metadata_json").notNull(),
  createdAt: text("created_at").notNull(),
});

// Source-linked metadata inventory. Counts are entries, not independent physical cores.
export const inventory = sqliteTable(
  "atlas_inventory",
  {
    id: text("id").primaryKey(),
    provider: text("provider").notNull(),
    sourceId: text("source_id").notNull(),
    name: text("name").notNull(),
    realm: text("realm").notNull(),
    kind: text("record_type").notNull(),
    latitude: real("latitude"),
    longitude: real("longitude"),
    metadata: text("metadata_json").notNull(),
  },
  (t) => [
    index("atlas_inventory_provider_idx").on(t.provider),
    index("atlas_inventory_kind_idx").on(t.kind),
  ],
);
export const campaigns = sqliteTable("atlas_campaigns", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  provider: text("provider").notNull(),
  metadata: text("metadata_json").notNull(),
});
export const inventoryCampaigns = sqliteTable(
  "atlas_inventory_campaigns",
  {
    id: text("id").primaryKey(),
    recordId: text("record_id")
      .notNull()
      .references(() => inventory.id),
    campaignId: text("campaign_id")
      .notNull()
      .references(() => campaigns.id),
  },
  (t) => [
    index("atlas_inventory_campaign_idx").on(t.campaignId, t.recordId),
    index("atlas_inventory_record_campaign_idx").on(t.recordId, t.campaignId),
  ],
);
export const inventoryReleases = sqliteTable("atlas_inventory_releases", {
  id: text("id").primaryKey(),
  count: integer("entry_count").notNull(),
  importedAt: text("imported_at").notNull(),
});
// Owner-only private uploads (lib/private-data.mjs); never served by public endpoints.
export const privateDatasets = sqliteTable("atlas_private_datasets", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  filename: text("filename"),
  createdAt: text("created_at").notNull(),
  record: text("record_json").notNull(),
  series: text("series_json").notNull(),
  warnings: text("warnings_json"),
});
export const privateSessions = sqliteTable("atlas_private_sessions", {
  tokenHash: text("token_hash").primaryKey(),
  createdAt: text("created_at").notNull(),
  expiresAt: text("expires_at").notNull(),
});
export const privateFailures = sqliteTable(
  "atlas_private_failures",
  {
    id: integer("id").primaryKey(),
    at: text("at").notNull(),
  },
  (t) => [index("atlas_private_failures_at_idx").on(t.at)],
);
