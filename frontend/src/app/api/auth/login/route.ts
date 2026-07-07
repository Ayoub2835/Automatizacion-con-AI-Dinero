import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BackendError, backendFetch } from "@/lib/backend-client";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import type { TokenResponse } from "@/lib/types";

export async function POST(request: Request): Promise<NextResponse> {
  const payload = await request.json();

  try {
    const tokens = await backendFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(payload),
    });

    (await cookies()).set(SESSION_COOKIE_NAME, tokens.access_token, {
      httpOnly: true,
      sameSite: "lax",
      secure: process.env.NODE_ENV === "production",
      path: "/",
      // Debe coincidir con ACCESS_TOKEN_EXPIRE_MINUTES del backend.
      maxAge: 30 * 60,
    });

    return NextResponse.json({ ok: true });
  } catch (error) {
    if (error instanceof BackendError) {
      return NextResponse.json({ detail: error.detail }, { status: error.status });
    }
    return NextResponse.json({ detail: "Error inesperado" }, { status: 502 });
  }
}
