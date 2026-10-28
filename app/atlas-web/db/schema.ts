import { sqliteTable, text, real, integer, index } from 'drizzle-orm/sqlite-core';

export const records = sqliteTable('atlas_records', {
  id: text('id').primaryKey(), name: text('name').notNull(), realm: text('realm').notNull(),
  latitude: real('latitude').notNull(), longitude: real('longitude').notNull(), metadata: text('metadata_json').notNull(),
});
export const series = sqliteTable('atlas_series', {
  id: text('id').primaryKey(), recordId: text('record_id').notNull().references(()=>records.id),
  proxy: text('proxy').notNull(), label: text('label').notNull(), unit: text('unit').notNull(), metadata: text('metadata_json').notNull(),
});
export const observations = sqliteTable('atlas_observations', {
  id: text('id').primaryKey(), seriesId: text('series_id').notNull().references(()=>series.id),
  age: real('age_ka_bp'), value: real('value').notNull(), sourceRow: integer('source_row').notNull(),
  sourceLine: integer('source_line'), originalAge: text('original_age'), originalValue: text('original_value'),
  ageUncertainty: real('age_uncertainty_ka'), valueUncertainty: real('value_uncertainty'), depthOriginal: text('depth_original'),
}, table=>[index('atlas_series_age_idx').on(table.seriesId,table.age)]);
export const releases = sqliteTable('atlas_releases', {
  id: text('id').primaryKey(), count: integer('observation_count').notNull(), importedAt: text('imported_at').notNull(),
});
export const candidates = sqliteTable('atlas_candidates', {
  id: text('id').primaryKey(), doi: text('doi').notNull().unique(), title: text('title').notNull(),
  state: text('state').notNull().default('pending_review'), metadata: text('metadata_json').notNull(), createdAt: text('created_at').notNull(),
});
