import { redirect } from "next/navigation";
import type { ReactNode } from "react";

import { LogoutButton } from "@/components/LogoutButton";
import { getCurrentUser } from "@/lib/session";

export default async function DashboardLayout({ children }: { children: ReactNode }) {
  const user = await getCurrentUser();

  // El middleware ya redirige por ausencia de cookie; esto cubre el caso de
  // un token presente pero inválido/expirado (el backend lo rechaza en /me).
  if (!user) {
    redirect("/login");
  }

  return (
    <div className="min-h-screen">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4">
        <span className="font-semibold">GestorIA</span>
        <div className="flex items-center gap-4 text-sm text-slate-600">
          <span>{user.email}</span>
          <LogoutButton />
        </div>
      </header>
      <main className="p-6">{children}</main>
    </div>
  );
}
