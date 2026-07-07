# 0003 — Frontend en Next.js + TypeScript

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Necesitamos un panel web básico ahora, con capacidad de crecer hacia un
producto completo sin reescritura, una vez validado el mercado.

## Decisión

Frontend en **Next.js (App Router) + TypeScript**.

Razones:

- Es el framework de React más usado en paneles/SaaS profesionales en
  2025-2026, lo que facilita incorporar talento sin curva de aprendizaje
  extra.
- SSR/SSG disponibles de fábrica si en el futuro hace falta SEO (ej.
  páginas de marketing) sin cambiar de stack.
- Convenciones claras de estructura (`app/`, layouts, server components)
  reducen decisiones arbitrarias en una fase donde el equipo es pequeño.

Se descartó una SPA con React + Vite por ser más simple para un panel
puramente básico, pero requeriría más decisiones manuales (routing,
data fetching, SSR) según el producto creciera — preferimos pagar ese
coste de convención ahora que reescribir más adelante.

## Consecuencias

- El panel actual es intencionalmente mínimo (login + shell de dashboard),
  pero la estructura de carpetas ya sigue convenciones de Next.js
  preparadas para crecer.
- Cualquier futura landing/marketing site puede vivir en el mismo proyecto
  Next.js aprovechando SSG, si se decide más adelante.
