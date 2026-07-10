# Go-to-market: fase de validación con clientes reales

**Fecha de entrada en esta fase**: 2026-07-10.

El MVP "Empleado Documental" (Fase 2, ver [ROADMAP.md](../../ROADMAP.md)) está
terminado. A partir de aquí **dejamos de construir funcionalidades nuevas**.
El objetivo único de esta fase es conseguir el primer cliente de pago y
validar con gestorías reales si esto resuelve un problema por el que
pagarían.

## El reto de los próximos 30 días

No es escribir más código. Es conseguir:

- **20 conversaciones** con gestorías reales.
- **5 demos** de 10 minutos.
- **1-3 pilotos** reales en marcha.
- **El primer cliente dispuesto a pagar.**

El progreso se controla en `seguimiento-crm.md`, no de memoria.

## La regla

> **No se cambia el producto por la opinión de una sola gestoría.**
> Solo se modifica el roadmap cuando:
> - 3 gestorías distintas tienen el mismo problema, o
> - existe una razón clara de bloqueo para vender (ej. nadie firma sin
>   multi-usuario, y lo dicen 3 de 3 pilotos).

Esto no es una sugerencia, es un bloqueo. Antes de escribir una sola línea
de código de producto, comprueba
[`roadmap-validado.md`](roadmap-validado.md): si la idea no cumple una de
las dos condiciones de arriba, no se construye — se anota como candidata
y se sigue vendiendo el producto tal como está.

## Índice de documentos

| Documento | Para qué sirve |
|---|---|
| [`lista-prospectos.md`](lista-prospectos.md) | Dónde encontrar gestorías españolas, criterios para las primeras 50, perfil ideal de piloto y cómo priorizarlas. |
| [`mensajes-contacto.md`](mensajes-contacto.md) | Mensajes de WhatsApp, email, LinkedIn y guion de llamada — todos con un único objetivo: conseguir una demo de 10 minutos. |
| [`seguimiento-crm.md`](seguimiento-crm.md) | Sistema simple (una hoja de cálculo) para controlar contacto, respuesta, reunión, demo, piloto y rechazo (con motivo) de cada prospecto. |
| [`puntos-debiles-y-objeciones.md`](puntos-debiles-y-objeciones.md) | Autocrítica del producto desde el punto de vista de un gerente de gestoría, y las 20 objeciones más probables con su respuesta. |
| [`demo-10-min.md`](demo-10-min.md) | Guion minuto a minuto de una demo de producto de 10 minutos, sin hablar de tecnología. |
| [`guion-venta.md`](guion-venta.md) | Guion completo de la reunión comercial: apertura, descubrimiento, demo, objeciones, cierre. |
| [`onboarding.md`](onboarding.md) | Checklist para dejar a una gestoría operativa (primera campaña enviada) en menos de 15 minutos. |
| [`piloto.md`](piloto.md) | Diseño del primer piloto: duración, configuración, qué medir, qué preguntar y qué resultado decide si funciona. |
| [`proceso-feedback.md`](proceso-feedback.md) | Cómo se recoge el feedback de cada reunión y cómo se convierte en tareas priorizadas. |
| [`roadmap-validado.md`](roadmap-validado.md) | El backlog real: solo entra lo que ha pedido gente de verdad. Empieza casi vacío a propósito. |
| [`feedback/`](feedback/) | Una nota por reunión/llamada con una gestoría real (plantilla en `proceso-feedback.md`). |

## Qué NO hacer en esta fase

- No añadir integraciones, canales (WhatsApp), personalización de marca,
  importación masiva, ni ninguna otra cosa que "parezca obviamente
  necesaria" sin que un cliente real la haya pedido. La lista de
  candidatas ya identificadas está en `roadmap-validado.md` — ahí se
  quedan hasta que tengan 3 votos reales.
- No optimizar el producto para una gestoría hipotética. Cada mejora debe
  poder señalar a una conversación real y citarla.
- No perder tiempo puliendo detalles visuales que ninguna gestoría ha
  mencionado como problema.
