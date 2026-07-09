"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import type { CampaignClientInvite, Client } from "@/lib/types";

export function SendCampaignForm({
  campaignId,
  clients,
}: {
  campaignId: string;
  clients: Client[];
}) {
  const router = useRouter();
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sentInvites, setSentInvites] = useState<CampaignClientInvite[] | null>(null);

  function toggle(clientId: string) {
    setSelectedIds((current) =>
      current.includes(clientId)
        ? current.filter((id) => id !== clientId)
        : [...current, clientId],
    );
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (selectedIds.length === 0) {
      setError("Selecciona al menos un cliente");
      return;
    }

    setIsSubmitting(true);
    const response = await fetch(`/api/campaigns/${campaignId}/send`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ client_ids: selectedIds }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo enviar la campaña");
      return;
    }

    const invites: CampaignClientInvite[] = await response.json();
    setSentInvites(invites);
    setSelectedIds([]);
    router.refresh();
  }

  if (clients.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Todavía no tienes clientes. Añádelos primero en la página de Clientes.
      </p>
    );
  }

  return (
    <div className="flex flex-col gap-4">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <ul className="flex flex-col gap-2">
          {clients.map((client) => (
            <li key={client.id} className="flex items-center gap-2">
              <input
                type="checkbox"
                id={`client-${client.id}`}
                checked={selectedIds.includes(client.id)}
                onChange={() => toggle(client.id)}
                className="h-4 w-4 rounded border-slate-300"
              />
              <label htmlFor={`client-${client.id}`} className="text-sm text-slate-700">
                {client.name} ({client.email})
              </label>
            </li>
          ))}
        </ul>
        {error && (
          <p role="alert" className="text-sm text-red-600">
            {error}
          </p>
        )}
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Enviando..." : "Enviar campaña a los seleccionados"}
        </Button>
      </form>

      {sentInvites !== null && (
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4 text-sm">
          {sentInvites.length === 0 ? (
            <p>Los clientes seleccionados ya tenían esta campaña enviada.</p>
          ) : (
            <>
              <p className="mb-2 font-medium">Enviado a {sentInvites.length} cliente(s):</p>
              <ul className="flex flex-col gap-1">
                {sentInvites.map((invite) => (
                  <li key={invite.id}>
                    {invite.client_name} —{" "}
                    <a href={invite.upload_url} className="underline" target="_blank">
                      {invite.upload_url}
                    </a>
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>
      )}
    </div>
  );
}
