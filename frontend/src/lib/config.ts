/**
 * URL del backend, solo accesible desde el servidor (Route Handlers,
 * Server Components). El navegador nunca llama directamente al backend:
 * todo pasa por las rutas /api/* de Next.js (patrón backend-for-frontend).
 * Ver frontend/README.md.
 */
export const API_URL = process.env.API_URL ?? "http://localhost:8000/api/v1";

export const SESSION_COOKIE_NAME = "session_token";
