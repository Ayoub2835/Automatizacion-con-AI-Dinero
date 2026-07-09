# 0009 — Envío de email por SMTP genérico, no un proveedor concreto

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

El MVP necesita enviar por email la solicitud de documentación con el
enlace seguro de subida (ver ADR 0008). Existían dos caminos: integrar el
SDK de un proveedor transaccional concreto (SendGrid, Postmark, Resend...)
o hablar SMTP directamente.

## Decisión

Se implementa un puerto `EmailSender` (`app/domain/ports/email_sender.py`)
con una única implementación `SmtpEmailSender` que usa `smtplib` (estándar
de Python) contra cualquier servidor SMTP configurado por variables de
entorno (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`,
`SMTP_USE_TLS`, `SMTP_FROM_EMAIL`).

En desarrollo, `docker-compose.yml` levanta **Mailpit** (`axllent/mailpit`)
como servidor SMTP local: intercepta los emails salientes y los muestra en
una UI web (`http://localhost:8025`), sin necesitar credenciales reales
para probar el flujo completo. Esto es infraestructura de desarrollo, no
una integración de producto — análogo a levantar Postgres en Docker.

Para una demo con una gestoría real, basta con cambiar las variables
`SMTP_*` a un proveedor real (Gmail, SendGrid vía SMTP, Amazon SES, el
SMTP del propio dominio de la gestoría...); no requiere cambiar código.

`smtplib` es síncrono/bloqueante; `SmtpEmailSender` lo ejecuta en un hilo
(`asyncio.to_thread`) para no bloquear el event loop de FastAPI.

## Consecuencias

- Cero acoplamiento a un proveedor de email concreto — coherente con "no
  añadir integraciones" (ver ADR 0008): SMTP es un protocolo, no un
  vendor.
- **No se maneja fallo parcial de envío**: si al enviar la campaña a N
  clientes falla el envío a uno, la petición completa falla y no se
  persiste ninguna asociación de esa tanda (transacción de base de datos
  + email en la misma unidad de trabajo). Aceptable para el volumen de un
  MVP; revisar si el volumen de clientes por campaña crece.
- Sin colas ni reintentos: el email se envía síncronamente dentro de la
  petición HTTP. Si el SMTP configurado es lento, el endpoint
  `POST /campaigns/{id}/send` tarda proporcionalmente. Aceptable para
  campañas de decenas de clientes; una campaña de miles necesitaría un
  worker en background, que no se construye sin esa necesidad real.
