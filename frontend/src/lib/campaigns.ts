import { backendFetch } from "@/lib/backend-client";
import type { Campaign } from "@/lib/types";

/** Lista las campañas de la gestoría autenticada. Server-side only (BFF). */
export async function getCampaigns(token: string): Promise<Campaign[]> {
  return backendFetch<Campaign[]>("/campaigns", { token });
}

/** Obtiene una campaña por id. Server-side only (BFF). */
export async function getCampaign(token: string, campaignId: string): Promise<Campaign> {
  return backendFetch<Campaign>(`/campaigns/${campaignId}`, { token });
}
