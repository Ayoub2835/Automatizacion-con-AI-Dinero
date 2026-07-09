# 0013 — Política de reenvío de recordatorios

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

El punto 9 del MVP (ADR 0008) requiere poder reenviar automáticamente el
recordatorio de solicitud de documentación. Había que decidir el alcance
mínimo: ¿a quién se reenvía, con qué límite de frecuencia, y qué cambia
en el envío (token, contenido)?

## Decisión

`POST /api/v1/campaigns/{id}/remind` (autenticado, mismo dueño de la
campaña) reenvía el email a **todos los `campaign_clients` en estado
`pending`** de esa campaña, reutilizando `build_document_request_email`
y el mismo `upload_token` ya generado en el envío original (T3) — no se
genera uno nuevo. Se actualiza `campaign_clients.last_reminder_sent_at`
a la hora del reenvío.

Explícitamente fuera de esta tarea:

- **Sin límite de frecuencia**: se puede llamar tantas veces como quiera
  el gestor; no hay cooldown ni aviso de "ya se envió hace poco". Es una
  acción manual con un clic (ver T12), no un cron automático.
- **Sin selección de destinatarios**: reenvía a todos los pendientes de
  la campaña, no a un subconjunto. Si la gestoría solo quiere avisar a
  uno, ese caso de uso no está cubierto en el MVP.
- **Clientes ya `complete` nunca reciben recordatorio** (se filtran en
  `CampaignDeliveryService.send_reminders`), consistente con ADR 0012.

## Consecuencias

- Reutiliza toda la infraestructura de T3/T4 (mismo `EmailSender`, mismo
  cuerpo de email, mismo token) — no hay código nuevo de envío, solo de
  selección de destinatarios pendientes y de registro de la fecha.
- Si en el futuro se necesita limitar la frecuencia de recordatorios
  (para no saturar al cliente), `last_reminder_sent_at` ya está
  persistido y es la columna a partir de la cual calcular ese límite.
