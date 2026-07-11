import { backendFetch } from "@/lib/backend-client";
import type { Book, Chapter } from "@/lib/types";

/** Lista los libros de la organización autenticada. Server-side only (BFF). */
export async function getBooks(token: string): Promise<Book[]> {
  return backendFetch<Book[]>("/books", { token });
}

/** Obtiene un libro por id. Server-side only (BFF). */
export async function getBook(token: string, bookId: string): Promise<Book> {
  return backendFetch<Book>(`/books/${bookId}`, { token });
}

/** Capítulos de un libro, en orden. Server-side only (BFF). */
export async function getBookChapters(token: string, bookId: string): Promise<Chapter[]> {
  return backendFetch<Chapter[]>(`/books/${bookId}/chapters`, { token });
}
