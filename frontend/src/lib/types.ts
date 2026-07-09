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
