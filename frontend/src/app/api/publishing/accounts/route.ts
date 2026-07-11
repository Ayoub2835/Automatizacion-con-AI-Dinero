import type { NextResponse } from "next/server";

import { proxyToBackend } from "@/lib/api-route";
import type { PublishingAccount } from "@/lib/types";

export async function POST(request: Request): Promise<NextResponse> {
  const payload = await request.json();
  return proxyToBackend<PublishingAccount>("/publishing/accounts", {
    body: payload,
    successStatus: 201,
  });
}
