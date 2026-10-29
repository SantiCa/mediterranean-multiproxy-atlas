CREATE TABLE `atlas_private_datasets` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`filename` text,
	`created_at` text NOT NULL,
	`record_json` text NOT NULL,
	`series_json` text NOT NULL,
	`warnings_json` text
);
--> statement-breakpoint
CREATE TABLE `atlas_private_sessions` (
	`token_hash` text PRIMARY KEY NOT NULL,
	`created_at` text NOT NULL,
	`expires_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `atlas_private_failures` (
	`id` integer PRIMARY KEY NOT NULL,
	`at` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_private_failures_at_idx` ON `atlas_private_failures` (`at`);
