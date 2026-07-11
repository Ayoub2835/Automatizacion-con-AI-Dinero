import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BackendError, backendFetch } from "@/lib/backend-client";
import { SESSION_COOKIE_NAME } from "@/lib/config";

/**
 * Reenvía una acción al backend desde un Route Handler (patrón BFF, ver ADR
 * 0007): lee el token de la cookie httpOnly, llama al backend y traduce el
 * resultado (o el error) a una respuesta JSON. Pensado para los múltiples
 * endpoints de acción de BookAgent AI (aprobar, rechazar, enviar...), donde
 * escribir el mismo try/catch en cada fichero de ruta no aporta nada.
 */
export async function proxyToBackend<T>(
  path: string,
  options: { method?: string; body?: unknown; successStatus?: number } = {},
): Promise<NextResponse> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json({ detail: "No autenticado" }, { status: 401 });
  }

  try {
    const data = await backendFetch<T>(path, {
      method: options.method ?? "POST",
      body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
      token,
    });
    return NextResponse.json(data, { status: options.successStatus ?? 200 });
  } catch (error) {
    if (error instanceof BackendError) {
      return NextResponse.json({ detail: error.detail }, { status: error.status });
    }
    return NextResponse.json({ detail: "Error inesperado" }, { status: 502 });
  }
}
