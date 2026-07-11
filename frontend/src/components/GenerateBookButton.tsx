"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

export function GenerateBookButton({ bookId }: { bookId: string }) {
  const router = useRouter();
  const [message, setMessage] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleClick() {
    setMessage(null);
    setIsSubmitting(true);

    const response = await fetch(`/api/books/${bookId}/generate`, { method: "POST" });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setMessage(body.detail ?? "No se pudo lanzar la generación");
      return;
    }

    router.refresh();
  }

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        type="button"
        onClick={handleClick}
        disabled={isSubmitting}
        className="rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {isSubmitting ? "Lanzando..." : "Generar / reintentar"}
      </button>
      {message && <p className="text-sm text-red-600">{message}</p>}
    </div>
  );
}
