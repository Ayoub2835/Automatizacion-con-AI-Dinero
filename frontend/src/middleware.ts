import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

import { SESSION_COOKIE_NAME } from "@/lib/config";

const PUBLIC_PATHS = ["/login", "/register"];

/**
 * Comprueba solo que exista la cookie de sesión (no valida el JWT en sí:
 * eso es responsabilidad del backend en cada request). Es suficiente para
 * decidir a qué página redirigir; no sustituye la autorización real.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE_NAME);
  // /upload/{token}: enlace seguro sin login (ver ADR 0008), el propio
  // token es la autorización — no requiere cookie de sesión.
  const isPublicUploadLink = pathname.startsWith("/upload/");

  if (!hasSession && !PUBLIC_PATHS.includes(pathname) && !isPublicUploadLink) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  if (hasSession && PUBLIC_PATHS.includes(pathname)) {
    return NextResponse.redirect(new URL("/dashboard", request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
};
