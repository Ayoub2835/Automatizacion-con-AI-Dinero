"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";

export function BookForm() {
  const router = useRouter();
  const [topic, setTopic] = useState("");
  const [niche, setNiche] = useState("");
  const [targetAudience, setTargetAudience] = useState("");
  const [language, setLanguage] = useState("español");
  const [style, setStyle] = useState("");
  const [targetPages, setTargetPages] = useState(60);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    const response = await fetch("/api/books", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic,
        niche,
        target_audience: targetAudience,
        language,
        style,
        target_pages: targetPages,
      }),
    });
    setIsSubmitting(false);

    if (!response.ok) {
      const body = await response.json().catch(() => ({ detail: "Error inesperado" }));
      setError(body.detail ?? "No se pudo crear el libro");
      return;
    }

    const book = await response.json();
    router.push(`/dashboard/books/${book.id}`);
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <Input
        id="topic"
        label="Tema del libro"
        type="text"
        required
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Ej. Finanzas personales para freelancers"
      />
      <Input
        id="niche"
        label="Nicho"
        type="text"
        required
        value={niche}
        onChange={(e) => setNiche(e.target.value)}
        placeholder="Ej. Desarrollo personal / negocios"
      />
      <Input
        id="target_audience"
        label="Público objetivo"
        type="text"
        required
        value={targetAudience}
        onChange={(e) => setTargetAudience(e.target.value)}
        placeholder="Ej. Autónomos que empiezan"
      />
      <Input
        id="language"
        label="Idioma"
        type="text"
        required
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      />
      <Input
        id="style"
        label="Estilo"
        type="text"
        required
        value={style}
        onChange={(e) => setStyle(e.target.value)}
        placeholder="Ej. cercano y práctico, con ejemplos"
      />
      <Input
        id="target_pages"
        label="Páginas aproximadas"
        type="number"
        min={10}
        max={1000}
        required
        value={targetPages}
        onChange={(e) => setTargetPages(Number(e.target.value))}
      />
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? "Creando..." : "Crear libro y empezar a generar"}
      </Button>
    </form>
  );
}
