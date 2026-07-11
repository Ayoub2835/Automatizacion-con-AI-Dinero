import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { API_URL, SESSION_COOKIE_NAME } from "@/lib/config";

/**
 * Descarga del EPUB/PDF: a diferencia del resto de rutas, la respuesta del
 * backend no es JSON sino el fichero en sí, así que se reenvía el body y
 * las cabeceras relevantes tal cual en vez de usar `proxyToBackend`.
 */
export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string; format: string }> },
): Promise<NextResponse> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json({ detail: "No autenticado" }, { status: 401 });
  }

  const { id, format } = await params;
  const response = await fetch(`${API_URL}/books/${id}/export/${format}`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
    return NextResponse.json(body, { status: response.status });
  }

  const buffer = await response.arrayBuffer();
  return new NextResponse(buffer, {
    status: 200,
    headers: {
      "Content-Type": response.headers.get("content-type") ?? "application/octet-stream",
      "Content-Disposition": response.headers.get("content-disposition") ?? "attachment",
    },
  });
}
