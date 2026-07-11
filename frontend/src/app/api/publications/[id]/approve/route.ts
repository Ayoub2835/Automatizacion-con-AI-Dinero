import type { NextResponse } from "next/server";

import { proxyToBackend } from "@/lib/api-route";
import type { Publication } from "@/lib/types";

export async function POST(
  _request: Request,
  { params }: { params: Promise<{ id: string }> },
): Promise<NextResponse> {
  const { id } = await params;
  return proxyToBackend<Publication>(`/publications/${id}/approve`);
}
