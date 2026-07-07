import { NextResponse } from "next/server";

import { BackendError, backendFetch } from "@/lib/backend-client";
import type { User } from "@/lib/types";

export async function POST(request: Request): Promise<NextResponse> {
  const payload = await request.json();

  try {
    const user = await backendFetch<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    if (error instanceof BackendError) {
      return NextResponse.json({ detail: error.detail }, { status: error.status });
    }
    return NextResponse.json({ detail: "Error inesperado" }, { status: 502 });
  }
}
