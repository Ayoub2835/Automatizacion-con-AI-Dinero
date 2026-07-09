import { backendFetch } from "@/lib/backend-client";
import type { Client } from "@/lib/types";

/** Lista los clientes de la gestoría autenticada. Server-side only (BFF). */
export async function getClients(token: string): Promise<Client[]> {
  return backendFetch<Client[]>("/clients", { token });
}
