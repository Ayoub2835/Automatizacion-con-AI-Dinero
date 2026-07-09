# 0012 — Cuándo se marca "completo" un cliente de una campaña

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

`campaign_clients.status` (ADR 0005/0008) es `pending` o `complete`. Había
que decidir dónde y cuándo se recalcula: ¿en cada lectura (GET de estado),
derivado en el momento, o persistido y sincronizado en el momento en que
cambia la razón de fondo (se sube/clasifica un documento)?

## Decisión

Se persiste y se sincroniza **en el momento en que llega un documento
nuevo**: `PublicCampaignService.upload_document` (T5/T6), tras clasificar
el documento, recalcula si todos los tipos requeridos de la campaña ya
tienen un documento `classified` (usando
`compute_document_type_statuses`/`is_complete` de
`application/services/document_status.py`) y, si es así, marca la
`campaign_client` como `complete` vía
`CampaignClientRepository.update_status`.

El endpoint de estado del gestor (`GET /campaigns/{id}/status`, T7) por
tanto solo **lee** `campaign_client.status` — no recalcula nada en el GET,
que se mantiene sin efectos secundarios.

## Consecuencias

- La transición es monótona en este MVP: no hay forma de "des-completar"
  un cliente (no se puede borrar un documento ya clasificado), así que no
  hace falta manejar el caso contrario.
- Si en el futuro se permite borrar o reclasificar documentos, hay que
  revisar este punto — quizás recalculando en cada lectura en vez de
  persistir, para evitar estados desincronizados.
- `document_types`/`documents` en la respuesta del panel del gestor sí se
  calculan en cada lectura (no se persisten) porque son baratos de derivar
  y cambian con cada documento nuevo — solo el resumen `status` se
  persiste, por ser el único campo que otras partes del sistema (el envío
  de recordatorios en T8) necesitan consultar sin recorrer documentos.
