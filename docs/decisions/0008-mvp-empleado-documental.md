# 0008 — MVP "Empleado Documental": alcance y modelo de datos

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

Con la base técnica terminada (Fase 0), entramos en fase de MVP para
conseguir el primer cliente de pago. Se elige una única hipótesis a
validar: automatizar la reclamación y clasificación de documentación
anual de los clientes de una gestoría ("Empleado Documental").

## Decisión

Se construye únicamente el flujo: crear clientes → crear campaña (con
tipos de documento requeridos) → enviar por email con enlace seguro →
el cliente sube documentos sin login → Claude los clasifica → el gestor
ve estado (completo/pendiente, documentos recibidos/faltantes) → puede
reenviar recordatorios.

### Modelo de datos (extiende el esquema de la Fase 0, ver ADR 0004/0005)

Todas las tablas nuevas llevan la cadena de pertenencia a
`organization_id` (directa o vía `campaign_id`/`client_id`), según la
regla de multi-tenancy ya establecida.

- `clients`: un cliente de la gestoría (`organization_id`, `name`,
  `email`, `phone`, `metadata` JSONB).
- `campaigns`: una campaña de solicitud (`organization_id`, `name`,
  `metadata` JSONB).
- `campaign_document_types`: los tipos de documento que pide una campaña
  (ej. "DNI", "Recibo de autónomos"). Texto libre, no un catálogo fijo —
  cada gestoría pide lo que necesita.
- `campaign_clients`: la instancia de "esta campaña enviada a este
  cliente". Lleva el `upload_token` único que es el enlace seguro, y el
  `status` (pending/complete).
- `documents`: un fichero subido por un cliente para una
  `campaign_client`, con su `campaign_document_type_id` asignado (o nulo
  si Claude no pudo clasificarlo con confianza suficiente).

### Explícitamente fuera de alcance (no construir sin que lo pida un cliente de pago)

- **WhatsApp**: solo email en este MVP.
- **Expiración/revocación de enlaces seguros**: el token no caduca.
  Aceptable para una prueba con clientes reales de confianza; revisar
  antes de un uso más amplio.
- **Reclasificación manual de documentos**: si Claude no clasifica un
  documento con confianza suficiente, se marca "sin clasificar" y lo ve
  el gestor — no hay UI para que el gestor lo reasigne a mano todavía.
- **Múltiples campañas activas simultáneas por cliente con tipos que se
  solapan**: no se resuelve ese conflicto; cada campaña es independiente.
- **Facturación, permisos granulares, notificaciones avanzadas,
  dashboards con métricas/gráficas**: fuera de alcance por instrucción
  explícita — el objetivo es el MVP más pequeño demostrable en una
  semana, no una plataforma completa.

Cada una de estas decisiones pospuestas debe revisarse cuando el primer
cliente de pago la convierta en un bloqueo real, no antes.

## Consecuencias

- El esquema es deliberadamente simple (texto libre para tipos de
  documento, sin catálogo normativo) — prioriza poder enseñar el flujo a
  una gestoría real esta semana sobre modelar el dominio "correctamente".
- Los puertos nuevos (envío de email, clasificación de documentos,
  almacenamiento de ficheros) siguen el mismo patrón hexagonal ya
  establecido (`domain/repositories` como interfaces, implementación en
  `infrastructure`), documentados en sus propios ADRs cuando se
  implementen (0009, 0010, 0011).
