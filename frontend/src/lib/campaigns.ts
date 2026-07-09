import { backendFetch } from "@/lib/backend-client";
import type { Campaign, CampaignStatusResponse } from "@/lib/types";

/** Lista las campañas de la gestoría autenticada. Server-side only (BFF). */
export async function getCampaigns(token: string): Promise<Campaign[]> {
  return backendFetch<Campaign[]>("/campaigns", { token });
}

/** Obtiene una campaña por id. Server-side only (BFF). */
export async function getCampaign(token: string, campaignId: string): Promise<Campaign> {
  return backendFetch<Campaign>(`/campaigns/${campaignId}`, { token });
}

/** Panel del gestor: clientes completos/pendientes, documentos recibidos y faltantes. */
export async function getCampaignStatus(
  token: string,
  campaignId: string,
): Promise<CampaignStatusResponse> {
  return backendFetch<CampaignStatusResponse>(`/campaigns/${campaignId}/status`, { token });
}
