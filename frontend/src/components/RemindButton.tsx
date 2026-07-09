"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function RemindButton({ campaignId }: { campaignId: string }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleClick() {
    setMessage(null);
    setIsSubmitting(true);

    const response = await fetch(`/api/campaigns/${campaignId}/remind`, { method: "POST" });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setMessage(body.detail ?? "No se pudieron reenviar los recordatorios");
      return;
    }

    const reminders = await response.json();
    setMessage(
      reminders.length === 0
        ? "No hay clientes pendientes a los que recordar."
        : `Recordatorio reenviado a ${reminders.length} cliente(s).`,
    );
    router.refresh();
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        type="button"
        onClick={handleClick}
        disabled={isSubmitting}
        className="rounded-md bg-slate-700 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? "Enviando..." : "Reenviar recordatorio a pendientes"}
      </button>
      {message && <p className="text-sm text-slate-600">{message}</p>}
    </div>
  );
}
