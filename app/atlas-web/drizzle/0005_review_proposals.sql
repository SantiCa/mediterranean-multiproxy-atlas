CREATE TABLE `atlas_review_proposals` (
	`id` text PRIMARY KEY NOT NULL,
	`release_id` text NOT NULL,
	`sample_key` text NOT NULL,
	`evidence_json` text NOT NULL,
	`reason` text NOT NULL,
	`status` text DEFAULT 'pending' NOT NULL,
	`created_by` text NOT NULL,
	`created_at` text NOT NULL,
	`decided_by` text,
	`decided_at` text,
	`review_note` text
);
--> statement-breakpoint
CREATE INDEX `atlas_review_release_created_idx` ON `atlas_review_proposals` (`release_id`,`created_at`);--> statement-breakpoint
CREATE UNIQUE INDEX `atlas_review_active_sample_idx` ON `atlas_review_proposals` (`release_id`,`sample_key`) WHERE "atlas_review_proposals"."status" <> 'rejected';
