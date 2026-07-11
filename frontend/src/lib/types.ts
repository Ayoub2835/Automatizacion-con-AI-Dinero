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
