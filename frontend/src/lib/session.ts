import { cookies } from "next/headers";

import { backendFetch } from "@/lib/backend-client";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import type { User } from "@/lib/types";

/** Lee el usuario autenticado en un Server Component. Null si no hay sesión válida. */
export async function getCurrentUser(): Promise<User | null> {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value;
  if (!token) {
    return null;
  }

  try {
    return await backendFetch<User>("/auth/me", { token });
  } catch {
    return null;
  }
}
