# Roadmap

Este roadmap distingue explícitamente entre **construir base técnica** (lo
que hacemos ahora) y **construir producto** (lo que depende de validar el
problema con gestorías reales). Mezclar ambas cosas demasiado pronto es el
riesgo principal que este documento intenta evitar.

## Fase 0 — Fundación técnica ✅ (este repositorio)

- [x] Estructura de proyecto, documentación de arquitectura y decisiones.
- [x] Backend con arquitectura limpia (FastAPI), sin lógica de negocio.
- [x] Modelo de datos multi-tenant mínimo (Organization + User).
- [x] Panel web básico (Next.js): login + shell de dashboard vacío.
- [x] Docker Compose, CI/CD, logging, manejo de errores, tests base.

**Criterio de salida de esta fase**: cualquier desarrollador nuevo puede
clonar el repo, levantar el entorno con un comando, y entender en menos de
30 minutos dónde añadir código sin tener que preguntar.

## Fase 1 — Validación del problema (no es una fase de código)

Antes de construir cualquier funcionalidad de negocio:

- Entrevistas con gestorías reales para confirmar qué tarea manual duele
  más y con qué frecuencia.
- Definir el ICP (perfil de cliente ideal): tamaño de gestoría, software
  que usan hoy, presupuesto.
- Validar si el dolor es de **tiempo** (tareas repetitivas), de
  **cumplimiento** (errores/plazos), o de **conocimiento** (dudas
  normativas) — la respuesta determina qué construimos en Fase 2.

Esta fase la impulsa negocio/producto, no ingeniería. El código de este
repo no debería cambiar sustancialmente durante esta fase, más allá de
arreglos.

## Fase 2 — MVP de producto (pendiente de definir tras validación)

Deliberadamente sin definir todavía. Candidatos a evaluar según lo que
diga la Fase 1 (ninguno decidido):

- Asistente de IA para responder dudas normativas con fuentes verificables.
- Extracción/estructuración de datos de documentos (facturas, nóminas).
- Panel de cumplimiento de plazos (alertas de vencimientos).

Cuando se decida, este documento se actualiza con las funcionalidades
concretas y un ADR justifica la elección.

## Fase 3 — Integraciones (pospuesta explícitamente)

No se empieza sin que un cliente de pago la pida:

- Integración con software de gestorías (A3, Sage, u otros según lo que
  use el ICP real).
- Integración con la Agencia Tributaria / Seguridad Social si aplica.

## Fase 4 — Automatización avanzada y agentes de IA (pospuesta explícitamente)

Solo después de que Fase 2 esté validada con clientes de pago recurrente:

- Flujos de automatización multi-paso.
- Agentes de IA con capacidad de acción (no solo consulta).

## Principio guía

> Si una funcionalidad no tiene un cliente real esperándola, no se
> construye — se documenta como punto de extensión.

Cada vez que se sienta la tentación de "adelantar trabajo" para una fase
futura, la pregunta a hacerse es: *¿esto lo estamos construyendo porque un
cliente lo pidió, o porque parece buena idea?* Solo lo primero justifica
escribir el código ahora.
