"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import type { Publication } from "@/lib/types";

async function postAction(path: string, body?: unknown): Promise<{ detail?: string } | null> {
  const response = await fetch(path, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!response.ok) {
    return response.json().catch(() => ({ detail: "Error inesperado" }));
  }
  return null;
}

export function PublicationActions({ publication }: { publication: Publication }) {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [externalId, setExternalId] = useState("");

  async function run(action: () => Promise<{ detail?: string } | null>) {
    setError(null);
    setIsSubmitting(true);
    const failure = await action();
    setIsSubmitting(false);
    if (failure) {
      setError(failure.detail ?? "No se pudo completar la acción");
      return;
    }
    router.refresh();
  }

  const buttonClass =
    "rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50";

  return (
    <div className="flex flex-col gap-3">
      {publication.status === "metadata_ready" && (
        <button
          type="button"
          disabled={isSubmitting}
          className={buttonClass}
          onClick={() => run(() => postAction(`/api/publications/${publication.id}/request-review`))}
        >
          Enviar a revisión
        </button>
      )}

      {publication.status === "pending_review" && (
        <div className="flex flex-col gap-2">
          <button
            type="button"
            disabled={isSubmitting}
            className={buttonClass}
            onClick={() => run(() => postAction(`/api/publications/${publication.id}/approve`))}
          >
            Aprobar
          </button>
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Motivo del rechazo"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm outline-none focus:border-slate-500"
            />
            <button
              type="button"
              disabled={isSubmitting || !rejectReason}
              className="rounded-md border border-red-300 px-3 py-1.5 text-sm font-medium text-red-700 transition hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
              onClick={() =>
                run(() =>
                  postAction(`/api/publications/${publication.id}/reject`, {
                    reason: rejectReason,
                  }),
                )
              }
            >
              Rechazar
            </button>
          </div>
        </div>
      )}

      {publication.status === "approved" && (
        <button
          type="button"
          disabled={isSubmitting}
          className={buttonClass}
          onClick={() => run(() => postAction(`/api/publications/${publication.id}/submit`))}
        >
          Enviar a la plataforma
        </button>
      )}

      {publication.status === "submitted" && (
        <div className="flex flex-col gap-2">
          {publication.instructions && (
            <p className="whitespace-pre-line rounded-md bg-slate-50 p-3 text-xs text-slate-600">
              {publication.instructions}
            </p>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              placeholder="Identificador asignado por la plataforma (opcional)"
              value={externalId}
              onChange={(e) => setExternalId(e.target.value)}
              className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm outline-none focus:border-slate-500"
            />
            <button
              type="button"
              disabled={isSubmitting}
              className={buttonClass}
              onClick={() =>
                run(() =>
                  postAction(`/api/publications/${publication.id}/mark-live`, {
                    external_book_id: externalId || null,
                  }),
                )
              }
            >
              Marcar como publicado
            </button>
          </div>
        </div>
      )}

      {publication.status === "rejected" && publication.review_notes && (
        <p className="text-sm text-red-600">Rechazada: {publication.review_notes}</p>
      )}

      {publication.status === "live" && (
        <p className="text-sm text-green-700">
          Publicado{publication.external_book_id && ` (ID: ${publication.external_book_id})`}
        </p>
      )}

      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  );
}
