# Frontend

Panel web en **Next.js (App Router) + TypeScript + Tailwind CSS**.
Intencionalmente mínimo: login, registro y un shell de dashboard vacío. Ver
[`/ARCHITECTURE.md`](../ARCHITECTURE.md) para la visión general.

## Patrón: Backend for Frontend (BFF)

El navegador **nunca** llama directamente a la API de FastAPI. Todas las
llamadas pasan por Route Handlers de Next.js (`src/app/api/`), que:

1. Reciben la petición del navegador.
2. Llaman al backend usando `API_URL` (variable solo de servidor, sin
   prefijo `NEXT_PUBLIC_`).
3. Gestionan la sesión con una cookie `httpOnly` — el JWT nunca es
   accesible desde JavaScript del cliente.

Ver [ADR 0007](../docs/decisions/0007-frontend-backend-for-frontend.md)
para el razonamiento completo.

## Estructura

```
src/
├── app/
│   ├── api/auth/          # Route Handlers: proxy al backend + cookie de sesión
│   ├── login/, register/  # Páginas públicas
│   └── dashboard/         # Páginas protegidas (requieren sesión)
├── components/
│   ├── ui/                # Primitivas visuales (Button, Input, Card)
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── LogoutButton.tsx
├── lib/
│   ├── config.ts           # Variables de entorno de servidor
│   ├── backend-client.ts   # Wrapper fetch para llamar al backend
│   ├── session.ts          # Lectura del usuario autenticado (Server Components)
│   └── types.ts
├── middleware.ts            # Redirección según exista/no exista cookie de sesión
└── test/                    # Setup y tests de Vitest + Testing Library
```

## Desarrollo local

Desde la raíz del repo: `./scripts/dev-up.sh` (recomendado, usa Docker).

O directamente con Node:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

## Comandos

| Comando | Qué hace |
|---|---|
| `npm run dev` | Servidor de desarrollo con hot-reload |
| `npm run build` | Build de producción |
| `npm run lint` | ESLint |
| `npm run type-check` | `tsc --noEmit` |
| `npm run test` | Tests con Vitest + Testing Library |

## Añadir una página nueva

1. Si requiere sesión, colócala bajo `app/dashboard/` (o actualiza
   `middleware.ts` si necesita otra convención de ruta protegida).
2. Si llama al backend, añade un Route Handler en `app/api/` que use
   `backendFetch` — no llames a `API_URL` desde un Client Component.
3. Componentes de UI reutilizables van en `components/ui/`; los
   específicos de una página, junto a ella o en `components/`.
