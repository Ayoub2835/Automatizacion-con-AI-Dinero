"use client";

import { useRouter } from "next/navigation";
import { useRef, useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";

export function UploadDocumentForm({ token }: { token: string }) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setError("Selecciona un fichero");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setIsSubmitting(true);
    const response = await fetch(`/api/public/campaigns/${token}/documents`, {
      method: "POST",
      body: formData,
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo subir el documento");
      return;
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="document_file" className="text-sm font-medium text-slate-700">
          Documento (PDF, JPG o PNG, máx. 15 MB)
        </label>
        <input
          id="document_file"
          ref={fileInputRef}
          type="file"
          accept="application/pdf,image/jpeg,image/png"
          className="rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
      </div>
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Subiendo..." : "Subir documento"}
      </Button>
    </form>
  );
}
