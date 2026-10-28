CREATE TABLE `atlas_campaigns` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`provider` text NOT NULL,
	`metadata_json` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `atlas_inventory` (
	`id` text PRIMARY KEY NOT NULL,
	`provider` text NOT NULL,
	`source_id` text NOT NULL,
	`name` text NOT NULL,
	`realm` text NOT NULL,
	`record_type` text NOT NULL,
	`latitude` real,
	`longitude` real,
	`metadata_json` text NOT NULL
);
--> statement-breakpoint
CREATE INDEX `atlas_inventory_provider_idx` ON `atlas_inventory` (`provider`);--> statement-breakpoint
CREATE INDEX `atlas_inventory_kind_idx` ON `atlas_inventory` (`record_type`);--> statement-breakpoint
CREATE TABLE `atlas_inventory_campaigns` (
	`id` text PRIMARY KEY NOT NULL,
	`record_id` text NOT NULL,
	`campaign_id` text NOT NULL,
	FOREIGN KEY (`record_id`) REFERENCES `atlas_inventory`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`campaign_id`) REFERENCES `atlas_campaigns`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `atlas_inventory_campaign_idx` ON `atlas_inventory_campaigns` (`campaign_id`,`record_id`);--> statement-breakpoint
CREATE TABLE `atlas_inventory_releases` (
	`id` text PRIMARY KEY NOT NULL,
	`entry_count` integer NOT NULL,
	`imported_at` text NOT NULL
);
