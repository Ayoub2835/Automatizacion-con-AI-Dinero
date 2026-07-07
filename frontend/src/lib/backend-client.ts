import { API_URL } from "@/lib/config";

export class BackendError extends Error {
  constructor(
    public status: number,
    public detail: string,
  ) {
    super(detail);
  }
}

/**
 * Wrapper mínimo para llamar al backend desde el servidor (Route Handlers /
 * Server Components). No es un SDK completo a propósito — cuando haya más
 * de un par de endpoints, considerar generar un cliente tipado a partir del
 * OpenAPI schema que expone FastAPI en /docs.
 */
export async function backendFetch<T>(
  path: string,
  init?: RequestInit & { token?: string },
): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  if (init?.token) {
    headers.set("Authorization", `Bearer ${init.token}`);
  }

  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: response.statusText }));
    throw new BackendError(response.status, body.detail ?? "Error desconocido del backend");
  }

  return response.json() as Promise<T>;
}
