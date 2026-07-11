export interface User {
  id: string;
  organization_id: string;
  email: string;
  role: "admin" | "member";
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Client {
  id: string;
  organization_id: string;
  name: string;
  email: string;
  phone: string | null;
  created_at: string;
}

export interface CampaignDocumentType {
  id: string;
  name: string;
}

export interface Campaign {
  id: string;
  organization_id: string;
  name: string;
  created_at: string;
  document_types: CampaignDocumentType[];
}

export interface PublicDocumentTypeStatus {
  name: string;
  satisfied: boolean;
}

export interface PublicDocument {
  id: string;
  original_filename: string;
  document_type_name: string | null;
  status: "classified" | "unclassified";
  uploaded_at: string;
}

export interface PublicCampaignStatus {
  campaign_name: string;
  client_status: "pending" | "complete";
  document_types: PublicDocumentTypeStatus[];
  documents: PublicDocument[];
}

export interface CampaignStatusDocumentType {
  name: string;
  satisfied: boolean;
}

export interface CampaignStatusDocument {
  id: string;
  original_filename: string;
  document_type_name: string | null;
  status: "classified" | "unclassified";
  uploaded_at: string;
}

export interface CampaignClientStatus {
  campaign_client_id: string;
  client_id: string;
  client_name: string;
  client_email: string;
  status: "pending" | "complete";
  document_types: CampaignStatusDocumentType[];
  documents: CampaignStatusDocument[];
}

export interface CampaignStatusResponse {
  campaign_id: string;
  campaign_name: string;
  clients: CampaignClientStatus[];
}

export interface CampaignClientInvite {
  id: string;
  campaign_id: string;
  client_id: string;
  client_name: string;
  client_email: string;
  status: "pending" | "complete";
  upload_url: string;
  created_at: string;
  last_reminder_sent_at: string | null;
}

// ---- BookAgent AI ----

export type BookStatus = "draft" | "generating" | "ready" | "exported" | "failed";

export type GenerationStage =
  | "research"
  | "title"
  | "outline"
  | "chapters"
  | "editing"
  | "sales_copy"
  | "cover_brief"
  | "export"
  | "done";

export interface MarketResearch {
  summary: string;
  trending_angles: string[];
  competitor_titles: string[];
  recommended_keywords: string[];
}

export interface Book {
  id: string;
  organization_id: string;
  topic: string;
  niche: string;
  target_audience: string;
  language: string;
  style: string;
  target_pages: number;
  status: BookStatus;
  generation_stage: GenerationStage | null;
  error_message: string | null;
  title: string | null;
  subtitle: string | null;
  market_research: MarketResearch | null;
  sales_blurb: string | null;
  seo_keywords: string[];
  categories: string[];
  cover_brief: string | null;
  has_epub: boolean;
  has_pdf: boolean;
  created_at: string;
  updated_at: string;
}

export type ChapterStatus = "pending" | "drafted" | "edited";

export interface Chapter {
  id: string;
  book_id: string;
  order: number;
  title: string;
  summary: string;
  content: string | null;
  word_count: number;
  status: ChapterStatus;
  created_at: string;
  updated_at: string;
}

export type PublishingPlatform = "kdp" | "apple_books" | "google_play_books" | "kobo";

export interface PublishingAccount {
  id: string;
  organization_id: string;
  platform: PublishingPlatform;
  display_name: string;
  connection_status: "manual" | "connected" | "needs_reauth";
  notes: string | null;
  created_at: string;
}

export type PublicationStatus =
  | "draft"
  | "metadata_ready"
  | "pending_review"
  | "approved"
  | "submitted"
  | "live"
  | "rejected"
  | "failed";

export interface Publication {
  id: string;
  organization_id: string;
  book_id: string;
  publishing_account_id: string;
  platform: PublishingPlatform;
  status: PublicationStatus;
  metadata: Record<string, string>;
  missing_metadata_fields: string[];
  instructions: string | null;
  review_notes: string | null;
  external_book_id: string | null;
  submitted_at: string | null;
  published_at: string | null;
  last_synced_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface SalesRecord {
  id: string;
  organization_id: string;
  publication_id: string;
  period_start: string;
  period_end: string;
  units_sold: number;
  revenue_amount: number;
  currency: string;
  source: string;
  recorded_at: string;
}

export interface DashboardSummary {
  total_books: number;
  books_by_status: Record<string, number>;
  total_publications: number;
  publications_by_status: Record<string, number>;
  total_units_sold: number;
  revenue_by_currency: Record<string, number>;
}
