# 0011 — Clasificación automática de documentos con Claude

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

Cuando un cliente sube un documento (ADR 0008), hay que averiguar
automáticamente a cuál de los tipos que pide la campaña corresponde (por
ejemplo, distinguir un DNI de un recibo de autónomos), para poder detectar
qué falta (T7) sin que el gestor tenga que abrir cada fichero.

## Decisión

Puerto `DocumentClassifier` (`app/domain/ports/document_classifier.py`) con
una implementación `ClaudeDocumentClassifier` que llama a la API de Claude
(`claude-opus-4-8`) con el documento (PDF o imagen, en base64) y le pide
clasificarlo mediante **structured outputs** (`output_config.format` con un
JSON Schema): un campo `document_type` restringido por `enum` a los
nombres de tipo que pide *esa* campaña más `"unknown"`, y una `confidence`
entre 0 y 1.

Un documento se marca `classified` solo si `confidence >= 0.6`
(`_CLASSIFICATION_CONFIDENCE_THRESHOLD` en `public_campaign_service.py`);
si no, queda `unclassified` para que lo vea el gestor. No hay
reclasificación manual en este MVP (ver ADR 0008).

**Fallo de clasificación no bloquea la subida**: si la llamada a Claude
falla (sin `ANTHROPIC_API_KEY` configurada, error de red, límite de tasa),
el documento se guarda igualmente con estado `unclassified` — el cliente
nunca ve un error de subida por un problema de clasificación. Esto se
implementa capturando la excepción en `PublicCampaignService._classify`.

## Consecuencias

- Cero coste de clasificación hasta que se configura `ANTHROPIC_API_KEY`
  (variable sin valor por defecto) — el flujo de subida funciona igual,
  simplemente sin clasificar, lo cual es aceptable para probar el resto
  del producto sin esa dependencia.
- Los tipos de documento son texto libre por campaña (ADR 0008), así que
  el `enum` del schema se construye dinámicamente en cada llamada — no hay
  un catálogo fijo de tipos que mantener.
- Solo se admiten PDF/JPG/PNG (ver `_ALLOWED_CONTENT_TYPES` en
  `api/v1/routers/public.py`) porque son los formatos que Claude clasifica
  con fiabilidad para este caso de uso.
- El umbral de confianza (0.6) es una elección inicial sin datos reales
  todavía — ajustar cuando haya campañas reales con las que medir falsos
  positivos/negativos.
