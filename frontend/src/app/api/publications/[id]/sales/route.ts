import type { NextResponse } from "next/server";

import { proxyToBackend } from "@/lib/api-route";
import type { SalesRecord } from "@/lib/types";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  const payload = await request.json();
  return proxyToBackend<SalesRecord>(`/publications/${id}/sales`, {
    body: payload,
    successStatus: 201,
  });
}
