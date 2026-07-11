"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { Book, PublishingAccount } from "@/lib/types";

const PLATFORM_LABELS: Record<string, string> = {
  kdp: "Amazon KDP",
  apple_books: "Apple Books",
  google_play_books: "Google Play Books",
  kobo: "Kobo",
};

export function PreparePublicationForm({
  book,
  accounts,
}: {
  book: Book;
  accounts: PublishingAccount[];
}) {
  const router = useRouter();
  const [accountId, setAccountId] = useState(accounts[0]?.id ?? "");
  const [title, setTitle] = useState(book.title ?? "");
  const [subtitle, setSubtitle] = useState(book.subtitle ?? "");
  const [description, setDescription] = useState(book.sales_blurb ?? "");
  const [keywords, setKeywords] = useState(book.seo_keywords.join(", "));
  const [categories, setCategories] = useState(book.categories.join(", "));
  const [price, setPrice] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (!accountId) {
      setError("Conecta primero una cuenta de publicación");
      return;
    }

    setIsSubmitting(true);
    const response = await fetch(`/api/books/${book.id}/publications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        publishing_account_id: accountId,
        metadata: { title, subtitle, description, keywords, categories, price },
      }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo preparar la publicación");
      return;
    }

    router.refresh();
  }

  if (accounts.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Todavía no tienes ninguna cuenta de publicación conectada. Conéctala primero en{" "}
        <a href="/dashboard/publishing" className="underline">
          Publicación
        </a>
        .
      </p>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <label htmlFor="account" className="text-sm font-medium text-slate-700">
          Cuenta de publicación
        </label>
        <select
          id="account"
          value={accountId}
          onChange={(e) => setAccountId(e.target.value)}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
        >
          {accounts.map((account) => (
            <option key={account.id} value={account.id}>
              {PLATFORM_LABELS[account.platform] ?? account.platform} — {account.display_name}
            </option>
          ))}
        </select>
      </div>
      <Input id="pub_title" label="Título" value={title} onChange={(e) => setTitle(e.target.value)} />
      <Input
        id="pub_subtitle"
        label="Subtítulo"
        value={subtitle}
        onChange={(e) => setSubtitle(e.target.value)}
      />
      <div className="flex flex-col gap-1">
        <label htmlFor="pub_description" className="text-sm font-medium text-slate-700">
          Descripción comercial
        </label>
        <textarea
          id="pub_description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={4}
          className="rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-slate-500 focus:ring-1 focus:ring-slate-500"
        />
      </div>
      <Input
        id="pub_keywords"
        label="Palabras clave (separadas por comas)"
        value={keywords}
        onChange={(e) => setKeywords(e.target.value)}
      />
      <Input
        id="pub_categories"
        label="Categorías (separadas por comas)"
        value={categories}
        onChange={(e) => setCategories(e.target.value)}
      />
      <Input
        id="pub_price"
        label="Precio de venta"
        placeholder="Ej. 4.99"
        value={price}
        onChange={(e) => setPrice(e.target.value)}
      />
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Preparando..." : "Preparar publicación"}
      </Button>
    </form>
  );
}
