import Link from "next/link";
import { cookies } from "next/headers";

import { BookForm } from "@/components/BookForm";
import { Card } from "@/components/ui/Card";
import { getBooks } from "@/lib/books";
import { SESSION_COOKIE_NAME } from "@/lib/config";

const STATUS_LABELS: Record<string, string> = {
  draft: "Borrador",
  generating: "Generando...",
  ready: "Listo",
  exported: "Exportado",
  failed: "Error",
};

export default async function BooksPage() {
  const token = (await cookies()).get(SESSION_COOKIE_NAME)?.value ?? "";
  const books = await getBooks(token);

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-lg font-semibold">Libros</h1>
        <p className="text-sm text-slate-600">
          BookAgent AI investiga el mercado, escribe el manuscrito y prepara los ficheros de
          publicación de forma autónoma a partir de un brief.
        </p>
      </div>

      <Card className="w-full max-w-md">
        <h2 className="mb-4 text-sm font-semibold text-slate-700">Nuevo libro</h2>
        <BookForm />
      </Card>

      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-slate-600">
            <tr>
              <th className="px-4 py-2 font-medium">Título</th>
              <th className="px-4 py-2 font-medium">Nicho</th>
              <th className="px-4 py-2 font-medium">Estado</th>
              <th className="px-4 py-2 font-medium"></th>
            </tr>
          </thead>
          <tbody>
            {books.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-500">
                  Todavía no has creado ningún libro.
                </td>
              </tr>
            ) : (
              books.map((book) => (
                <tr key={book.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-2">{book.title ?? book.topic}</td>
                  <td className="px-4 py-2">{book.niche}</td>
                  <td className="px-4 py-2">
                    {STATUS_LABELS[book.status] ?? book.status}
                    {book.status === "generating" && book.generation_stage && (
                      <span className="text-slate-400"> ({book.generation_stage})</span>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <Link
                      href={`/dashboard/books/${book.id}`}
                      className="font-medium text-slate-900 underline"
                    >
                      Ver
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
