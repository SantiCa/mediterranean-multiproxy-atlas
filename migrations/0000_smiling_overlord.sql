CREATE TABLE `atlas_candidates` (
	`id` text PRIMARY KEY NOT NULL,
	`doi` text NOT NULL,
	`title` text NOT NULL,
	`state` text DEFAULT 'pending_review' NOT NULL,
	`metadata_json` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE UNIQUE INDEX `atlas_candidates_doi_unique` ON `atlas_candidates` (`doi`);--> statement-breakpoint
CREATE TABLE `atlas_observations` (
	`id` text PRIMARY KEY NOT NULL,
	`series_id` text NOT NULL,
	`age_ka_bp` real,
	`value` real NOT NULL,
	`source_row` integer NOT NULL,
	`source_line` integer,
	`original_age` text,
	`original_value` text,
	FOREIGN KEY (`series_id`) REFERENCES `atlas_series`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `atlas_series_age_idx` ON `atlas_observations` (`series_id`,`age_ka_bp`);--> statement-breakpoint
CREATE TABLE `atlas_records` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`realm` text NOT NULL,
	`latitude` real NOT NULL,
	`longitude` real NOT NULL,
	`metadata_json` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `atlas_releases` (
	`id` text PRIMARY KEY NOT NULL,
	`observation_count` integer NOT NULL,
	`imported_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `atlas_series` (
	`id` text PRIMARY KEY NOT NULL,
	`record_id` text NOT NULL,
	`proxy` text NOT NULL,
	`label` text NOT NULL,
	`unit` text NOT NULL,
	`metadata_json` text NOT NULL,
	FOREIGN KEY (`record_id`) REFERENCES `atlas_records`(`id`) ON UPDATE no action ON DELETE no action
);
