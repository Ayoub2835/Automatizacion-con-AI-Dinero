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
