declare namespace Cloudflare {
  interface Env {
    DB?: D1Database;
    BUCKET?: R2Bucket;
    ATLAS_REVIEW_EDITOR_EMAIL?: string;
    ATLAS_REVIEW_REVIEWER_EMAIL?: string;
  }
}
