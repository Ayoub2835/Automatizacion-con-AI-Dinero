import { cookies } from "next/headers";

import { GenerateBookButton } from "@/components/GenerateBookButton";
import { PreparePublicationForm } from "@/components/PreparePublicationForm";
import { PublicationActions } from "@/components/PublicationActions";
import { SalesRecordForm } from "@/components/SalesRecordForm";
import { Card } from "@/components/ui/Card";
import { getBook, getBookChapters } from "@/lib/books";
import { SESSION_COOKIE_NAME } from "@/lib/config";
import { getPublicationsForBook, getPublishingAccounts } from "@/lib/publishing";

const STATUS_LABELS: Record<string, string> = {
  draft: "Borrador",
  generating: "Generando...",
  ready: "Listo",
  exported: "Exportado",
  failed: "Error",
};

const PLATFORM_LABELS: Record<string, string> = {
  kdp: "Amazon KDP",
  apple_books: "Apple Books",
  google_play_books: "Google Play Books",
  kobo: "Kobo",
};

const PUBLICATION_STATUS_LABELS: Record<string, string> = {
  draft: "Borrador",
  metadata_ready: "Metadatos listos",
  pending_review: "En revisión",
  approved: "Aprobada",
  submitted: "Enviada",
  live: "Publicada",
  rejected: "Rechazada",
  failed: "Error",
};

export default async function BookDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";

  const [book, chapters, accounts, publications] = await Promise.all([
    getBook(token, id),
    getBookChapters(token, id),
    getPublishingAccounts(token),
    getPublicationsForBook(token, id),
  ]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-lg font-semibold">{book.title ?? book.topic}</h1>
          {book.subtitle && <p className="text-sm text-slate-600">{book.subtitle}</p>}
          <p className="mt-1 text-xs text-slate-500">
            {book.niche} · {book.target_audience} · {book.language} · ~{book.target_pages} páginas
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
            {STATUS_LABELS[book.status] ?? book.status}
            {book.generation_stage ? ` · ${book.generation_stage}` : ""}
          </span>
          {(book.status === "draft" || book.status === "failed") && (
            <GenerateBookButton bookId={book.id} />
          )}
        </div>
      </div>

      {book.error_message && (
        <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">{book.error_message}</p>
      )}

      {(book.has_epub || book.has_pdf) && (
        <div className="flex gap-3">
          {book.has_epub && (
            <a
              href={`/api/books/${book.id}/export/epub`}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Descargar EPUB
            </a>
          )}
          {book.has_pdf && (
            <a
              href={`/api/books/${book.id}/export/pdf`}
              className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Descargar PDF
            </a>
          )}
        </div>
      )}

      {book.market_research && (
        <Card className="w-full max-w-3xl">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Investigación de mercado</h2>
          <p className="text-sm text-slate-600">{book.market_research.summary}</p>
          <dl className="mt-3 grid grid-cols-1 gap-3 text-xs text-slate-600 sm:grid-cols-3">
            <div>
              <dt className="font-medium text-slate-700">Ángulos con demanda</dt>
              <dd>{book.market_research.trending_angles.join(", ")}</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-700">Competidores</dt>
              <dd>{book.market_research.competitor_titles.join(", ")}</dd>
            </div>
            <div>
              <dt className="font-medium text-slate-700">Palabras clave</dt>
              <dd>{book.market_research.recommended_keywords.join(", ")}</dd>
            </div>
          </dl>
        </Card>
      )}

      {book.sales_blurb && (
        <Card className="w-full max-w-3xl">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Material de venta</h2>
          <p className="text-sm text-slate-600">{book.sales_blurb}</p>
          <p className="mt-2 text-xs text-slate-500">
            SEO: {book.seo_keywords.join(", ")} · Categorías: {book.categories.join(", ")}
          </p>
        </Card>
      )}

      {book.cover_brief && (
        <Card className="w-full max-w-3xl">
          <h2 className="mb-2 text-sm font-semibold text-slate-700">Idea de portada</h2>
          <p className="text-sm text-slate-600">{book.cover_brief}</p>
        </Card>
      )}

      {chapters.length > 0 && (
        <div>
          <h2 className="mb-2 text-sm font-semibold text-slate-700">
            Capítulos ({chapters.length})
          </h2>
          <div className="flex flex-col gap-2">
            {chapters.map((chapter) => (
              <details
                key={chapter.id}
                className="rounded-lg border border-slate-200 bg-white p-4"
              >
                <summary className="cursor-pointer text-sm font-medium text-slate-800">
                  {chapter.order}. {chapter.title}{" "}
                  <span className="text-xs font-normal text-slate-400">
                    ({chapter.status}, {chapter.word_count} palabras)
                  </span>
                </summary>
                <p className="mt-2 whitespace-pre-line text-sm text-slate-600">
                  {chapter.content ?? chapter.summary}
                </p>
              </details>
            ))}
          </div>
        </div>
      )}

      <div>
        <h2 className="mb-2 text-sm font-semibold text-slate-700">Publicación</h2>
        <div className="flex flex-col gap-4">
          {publications.map((publication) => (
            <Card key={publication.id} className="w-full max-w-3xl">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-sm font-medium text-slate-800">
                  {PLATFORM_LABELS[publication.platform] ?? publication.platform}
                </span>
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                  {PUBLICATION_STATUS_LABELS[publication.status] ?? publication.status}
                </span>
              </div>
              {publication.missing_metadata_fields.length > 0 && (
                <p className="mb-2 text-xs text-amber-700">
                  Faltan metadatos: {publication.missing_metadata_fields.join(", ")}
                </p>
              )}
              <PublicationActions publication={publication} />
              {publication.status === "live" && (
                <div className="mt-4 border-t border-slate-100 pt-4">
                  <h3 className="mb-2 text-xs font-semibold text-slate-700">Registrar venta</h3>
                  <SalesRecordForm publicationId={publication.id} />
                </div>
              )}
            </Card>
          ))}

          {(book.status === "ready" || book.status === "exported") && (
            <Card className="w-full max-w-3xl">
              <h3 className="mb-3 text-sm font-semibold text-slate-700">
                Preparar nueva publicación
              </h3>
              <PreparePublicationForm book={book} accounts={accounts} />
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
