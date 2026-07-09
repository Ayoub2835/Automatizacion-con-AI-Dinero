import { NextResponse } from "next/server";

import { API_URL } from "@/lib/config";

/**
 * Reenvía la subida multipart al backend tal cual (no se puede usar
 * backendFetch: siempre serializa a JSON). Sin token de sesión: el propio
 * `token` del enlace seguro es la autorización, ver ADR 0008.
 */
export async function POST(
  request: Request,
  { params }: { params: Promise<{ token: string }> },
): Promise<NextResponse> {
  const { token } = await params;
  const formData = await request.formData();

  const response = await fetch(`${API_URL}/public/campaigns/${token}/documents`, {
    method: "POST",
    body: formData,
    cache: "no-store",
  });

  const body = await response.json().catch(() => ({ detail: response.statusText }));
  return NextResponse.json(body, { status: response.status });
}
