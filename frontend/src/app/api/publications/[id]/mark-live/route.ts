import type { NextResponse } from "next/server";

import { proxyToBackend } from "@/lib/api-route";
import type { Publication } from "@/lib/types";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  const payload = await request.json();
  return proxyToBackend<Publication>(`/publications/${id}/mark-live`, { body: payload });
}
