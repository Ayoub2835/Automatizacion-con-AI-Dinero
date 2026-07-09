"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function CampaignForm() {
  const router = useRouter();
  const [name, setName] = useState("");
  const [documentTypes, setDocumentTypes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    const types = documentTypes
      .split(",")
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    if (types.length === 0) {
      setError("Indica al menos un tipo de documento");
      return;
    }

    setIsSubmitting(true);
    const response = await fetch("/api/campaigns", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, document_types: types }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo crear la campaña");
      return;
    }

    const campaign = await response.json();
    router.push(`/dashboard/campaigns/${campaign.id}`);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        id="campaign_name"
        label="Nombre de la campaña"
        type="text"
        required
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <Input
        id="document_types"
        label="Documentos a solicitar (separados por comas)"
        type="text"
        placeholder="DNI, Recibo de autónomos"
        required
        value={documentTypes}
        onChange={(e) => setDocumentTypes(e.target.value)}
      />
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creando..." : "Crear campaña"}
      </Button>
    </form>
  );
}
