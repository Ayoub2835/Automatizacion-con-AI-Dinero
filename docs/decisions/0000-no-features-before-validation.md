# 0000 — No construir funcionalidades sin validar con clientes reales

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Estamos construyendo un SaaS de IA para gestorías españolas, pero todavía
no hemos validado con clientes reales cuál es el problema exacto que más
duele. Existe la tentación natural de empezar a construir integraciones
(A3, Sage), automatizaciones o agentes de IA porque "seguro que hacen
falta".

## Decisión

No se construye ninguna funcionalidad de negocio, integración,
automatización o agente de IA hasta que:

1. Se haya hablado con clientes reales (gestorías) y confirmado el
   problema.
2. Exista una hipótesis concreta y priorizada sobre qué construir.

Lo que sí se construye ahora es la **base técnica**: arquitectura,
estructura de proyecto, backend limpio, modelo de datos flexible, panel
básico, CI/CD. Es decir, todo lo que es necesario sin importar qué
funcionalidad de negocio termine ganando.

## Consecuencias

- Positivas: evitamos construir y luego tirar código especulativo; el
  equipo de ingeniería no bloquea al de producto/validación, y viceversa.
- Negativas: el repositorio "no hace nada" desde el punto de vista de
  negocio durante un tiempo — esto es intencional, no un olvido.
- Cada vez que se proponga una funcionalidad nueva, debe poder señalarse
  qué conversación con qué cliente la motivó, o quedar documentada como
  punto de extensión pendiente en `ARCHITECTURE.md` / `ROADMAP.md`.
