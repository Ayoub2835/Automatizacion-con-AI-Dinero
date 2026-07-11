"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { PublishingPlatform } from "@/lib/types";

const PLATFORMS: { value: PublishingPlatform; label: string }[] = [
  { value: "kdp", label: "Amazon Kindle Direct Publishing (KDP)" },
  { value: "apple_books", label: "Apple Books" },
  { value: "google_play_books", label: "Google Play Books" },
  { value: "kobo", label: "Kobo" },
];

export function ConnectAccountForm() {
  const router = useRouter();
  const [platform, setPlatform] = useState<PublishingPlatform>("kdp");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const response = await fetch("/api/publishing/accounts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ platform, display_name: displayName }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo conectar la cuenta");
      return;
    }

    setDisplayName("");
    router.refresh();
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="platform" className="text-sm font-medium text-slate-700">
          Plataforma
        </label>
        <select
          id="platform"
          value={platform}
          onChange={(e) => setPlatform(e.target.value as PublishingPlatform)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
        >
          {PLATFORMS.map((p) => (
            <option key={p.value} value={p.value}>
              {p.label}
            </option>
          ))}
        </select>
      </div>
      <Input
        id="display_name"
        label="Nombre de la cuenta"
        type="text"
        required
        value={displayName}
        onChange={(e) => setDisplayName(e.target.value)}
        placeholder="Ej. Mi cuenta de autor"
      />
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Conectando..." : "Conectar cuenta"}
      </Button>
    </form>
  );
}
