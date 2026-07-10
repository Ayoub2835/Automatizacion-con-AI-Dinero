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

## Fase 2 — MVP: "Empleado Documental" 🚧 (en curso)

Hipótesis elegida para validar con el primer cliente de pago: la gestoría
pierde tiempo reclamando y organizando la documentación anual de sus
clientes (DNI, recibos, justificantes...). El MVP automatiza solo ese
flujo, de punta a punta, sin nada más:

1. Registrar clientes de la gestoría.
2. Crear una campaña con los tipos de documento requeridos.
3. Enviarla por email con un enlace seguro (sin login) por cliente.
4. El cliente sube sus documentos desde ese enlace.
5. Claude clasifica automáticamente cada documento entre los tipos
   requeridos.
6. El gestor ve, por campaña, qué clientes están completos, cuáles
   pendientes y qué documento falta a cada uno.
7. El gestor puede reenviar el recordatorio con un clic.

Explícitamente fuera de esta fase (ver [ADR 0008](docs/decisions/0008-mvp-empleado-documental.md)):
WhatsApp (solo email por ahora), facturación, permisos granulares,
notificaciones avanzadas, dashboards sofisticados, reclasificación manual
de documentos, expiración de enlaces. Se documentan como puntos de
extensión, no se construyen sin que un cliente de pago los pida.

Criterio de salida de esta fase: una gestoría real usa el flujo completo
con sus propios clientes durante al menos una campaña real.

## Fase 2.5 — Validación comercial 🚧 (en curso)

El MVP está terminado. **Se deja de escribir código de producto.** El
único objetivo ahora es conseguir el primer cliente de pago y validar
con gestorías reales si esto resuelve un problema por el que pagarían.
Todo el proceso — objeciones, guion de venta, onboarding, recogida de
feedback y el backlog que decide qué de las Fases 3/4 de abajo (si algo)
se acaba construyendo — vive en
[`docs/go-to-market/`](docs/go-to-market/README.md).

Regla explícita de esta fase:

> No se desarrolla ninguna funcionalidad nueva que no haya sido
> solicitada o validada por al menos 3 gestorías distintas. Ver
> [`docs/go-to-market/roadmap-validado.md`](docs/go-to-market/roadmap-validado.md).

Criterio de salida de esta fase: al menos una gestoría paga por el
producto de forma recurrente.

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
