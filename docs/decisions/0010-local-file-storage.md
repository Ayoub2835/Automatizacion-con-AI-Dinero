# 0010 — Almacenamiento de documentos en disco local (no S3 todavía)

**Estado**: Aceptado
**Fecha**: 2026-07-09

## Contexto

Los clientes suben documentos (DNI, recibos...) a través del enlace
seguro (ver ADR 0008). Hay que guardar esos ficheros en algún sitio.

## Decisión

Puerto `FileStorage` (`app/domain/ports/file_storage.py`) con una única
implementación `LocalFileStorage` que guarda los ficheros en el sistema
de ficheros local, bajo `UPLOADS_DIR` (`/app/uploads` dentro del
contenedor, en un volumen Docker persistente `uploads_data`).

Cada fichero se guarda como
`<UPLOADS_DIR>/<campaign_client_id>/<uuid>_<nombre-saneado>`: el UUID
evita colisiones de nombre y el saneado del nombre original evita path
traversal a partir de un nombre de fichero que controla el cliente que
sube el documento (no de confianza).

No se sirven los ficheros directamente por una URL pública: se leen solo
a través del backend (para clasificación en T6; no hay endpoint de
descarga en este MVP, ver "Explícitamente fuera de alcance" abajo).

## Explícitamente fuera de alcance

- **Almacenamiento en la nube (S3/GCS/Azure Blob)**: el puerto
  `FileStorage` ya aísla esta decisión — cambiar de disco local a S3 es
  añadir una implementación nueva sin tocar el resto del sistema. No se
  hace ahora porque el volumen de un MVP no lo necesita y añade una
  dependencia/coste operativo (bucket, credenciales, IAM) sin beneficio
  todavía.
- **Endpoint de descarga del fichero original para el gestor**: el
  requisito pedido es "ver documentos recibidos", que se resuelve con
  metadatos (nombre, tipo clasificado, fecha) en el panel (T7). Descargar
  el fichero en sí es una extensión natural si un cliente de pago lo pide.
- **Antivirus/escaneo de malware en los ficheros subidos**: aceptable para
  una prueba con una gestoría de confianza; revisar antes de abrir el
  producto a desconocidos sin invitación.

## Consecuencias

- Un contenedor de backend sin el volumen `uploads_data` montado pierde
  los ficheros al recrearse — el volumen es obligatorio en
  `docker-compose.yml`, documentado ahí.
- Migrar a almacenamiento en la nube en el futuro no requiere cambiar
  `domain` ni `application`, solo añadir un adaptador nuevo en
  `infrastructure/external/` y cambiar qué implementación inyecta
  `app/api/v1/routers/public.py`.
