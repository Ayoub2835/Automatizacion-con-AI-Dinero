import { backendFetch } from "@/lib/backend-client";
import type { DashboardSummary, Publication, PublishingAccount, SalesRecord } from "@/lib/types";

/** Cuentas de plataformas de venta conectadas. Server-side only (BFF). */
export async function getPublishingAccounts(token: string): Promise<PublishingAccount[]> {
  return backendFetch<PublishingAccount[]>("/publishing/accounts", { token });
}

/** Publicaciones (intentos de venta) de un libro, una por plataforma preparada. */
export async function getPublicationsForBook(
  token: string,
  bookId: string,
): Promise<Publication[]> {
  return backendFetch<Publication[]>(`/books/${bookId}/publications`, { token });
}

/** Ventas registradas de una publicación (manuales en este MVP). */
export async function getSalesForPublication(
  token: string,
  publicationId: string,
): Promise<SalesRecord[]> {
  return backendFetch<SalesRecord[]>(`/publications/${publicationId}/sales`, { token });
}

/** Agregados para el panel: libros/publicaciones por estado, ventas e ingresos. */
export async function getDashboardSummary(token: string): Promise<DashboardSummary> {
  return backendFetch<DashboardSummary>("/publishing/dashboard", { token });
}
