import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BackendError, backendFetch } from "@/lib/backend-client";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import type { Campaign } from "@/lib/types";

export async function POST(request: Request): Promise<NextResponse> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json({ detail: "No autenticado" }, { status: 401 });
  }

  const payload = await request.json();

  try {
    const campaign = await backendFetch<Campaign>("/campaigns", {
      method: "POST",
      body: JSON.stringify(payload),
      token,
    });
    return NextResponse.json(campaign, { status: 201 });
  } catch (error) {
    if (error instanceof BackendError) {
      return NextResponse.json({ detail: error.detail }, { status: error.status });
    }
    return NextResponse.json({ detail: "Error inesperado" }, { status: 502 });
  }
}
