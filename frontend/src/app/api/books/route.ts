import type { NextResponse } from "next/server";

import { proxyToBackend } from "@/lib/api-route";
import type { Book } from "@/lib/types";

export async function POST(request: Request): Promise<NextResponse> {
  const payload = await request.json();
  return proxyToBackend<Book>("/books", { body: payload, successStatus: 201 });
}
