import { cookies } from "next/headers";
import { NextResponse } from "next/server";

import { BackendError, backendFetch } from "@/lib/backend-client";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import type { CampaignClientInvite } from "@/lib/types";

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return NextResponse.json({ detail: "No autenticado" }, { status: 401 });
  }

  const { id } = await params;

  try {
    const reminders = await backendFetch<CampaignClientInvite[]>(`/campaigns/${id}/remind`, {
      method: "POST",
      token,
    });
    return NextResponse.json(reminders, { status: 200 });
  } catch (error) {
    if (error instanceof BackendError) {
      return NextResponse.json({ detail: error.detail }, { status: error.status });
    }
    return NextResponse.json({ detail: "Error inesperado" }, { status: 502 });
  }
}
