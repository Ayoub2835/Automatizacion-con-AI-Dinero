# 0007 — El navegador nunca llama al backend directamente (patrón BFF)

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Al implementar el panel (Fase 4), la alternativa "por defecto" era que el
navegador llamase directamente a la API de FastAPI usando una variable
`NEXT_PUBLIC_API_URL` (como se apuntaba de forma implícita en el ADR 0003),
guardando el JWT en `localStorage` o una cookie no-httpOnly gestionada por
JavaScript del cliente.

Ese enfoque tiene dos problemas para una base pensada para durar años:

1. Un JWT accesible desde JavaScript (localStorage, cookie no-httpOnly) es
   robable vía XSS. Con `httpOnly`, un XSS no puede exfiltrar el token.
2. Requiere configurar CORS en el backend para el dominio del frontend y
   expone la URL del backend al público.

## Decisión

El navegador solo habla con **Route Handlers de Next.js** (`src/app/api/`).
Estos, ejecutándose en el servidor, llaman al backend usando una variable
`API_URL` **sin** prefijo `NEXT_PUBLIC_` (por tanto invisible al navegador)
y gestionan la sesión con una cookie `httpOnly`, `sameSite=lax` y `secure`
en producción.

Esto es el patrón "Backend for Frontend" (BFF): Next.js actúa como
intermediario entre el navegador y la API real.

## Consecuencias

- Ya no hace falta configurar CORS entre frontend y backend (las llamadas
  servidor-a-servidor no están sujetas a CORS); `backend_cors_origins` en
  `core/config.py` queda como salvaguarda para llamadas directas futuras
  (ej. una app móvil), no como mecanismo principal.
- El middleware de Next.js (`src/middleware.ts`) solo puede comprobar que
  la cookie existe, no validar el JWT en sí — la validación real ocurre en
  el backend en cada request. Esto es suficiente para decidir a qué página
  redirigir, no sustituye la autorización real.
- Si en el futuro se necesita que un cliente externo (móvil, integración
  de terceros) llame al backend directamente, esa es una decisión nueva
  que requiere su propio ADR (autenticación por API key, OAuth, etc.).
