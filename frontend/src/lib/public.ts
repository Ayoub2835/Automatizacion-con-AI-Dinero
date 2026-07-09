import { backendFetch } from "@/lib/backend-client";
import type { PublicCampaignStatus } from "@/lib/types";

/** Estado de la campaña para el enlace seguro `token` (sin autenticación). */
export async function getPublicCampaignStatus(token: string): Promise<PublicCampaignStatus> {
  return backendFetch<PublicCampaignStatus>(`/public/campaigns/${token}`);
}
