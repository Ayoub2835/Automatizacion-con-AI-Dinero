# Sistema de seguimiento automático

"Automático" aquí significa que **la hoja de cálculo te dice cada día a
quién le toca escribir y qué mensaje mandar** — no que el envío se haga
solo. No hay ninguna herramienta de automatización de envíos en este
sistema (y así se queda, ver `mensajes-personalizados.md` sobre por qué
no conviene automatizar WhatsApp/LinkedIn). Lo automático es el
cálculo de cuándo toca, no el envío en sí.

## La cadencia (4 toques desde el primer contacto)

| Toque | Cuándo | Canal | Tono |
|---|---|---|---|
| 1 — Primer contacto | Día 0 | El mejor disponible: WhatsApp > email > LinkedIn > llamada (ver `lista-prospectos.md` y `mensajes-personalizados.md`) | Directo, pide los 10 minutos |
| 2 — Seguimiento 1 | Día 3-4 | Mismo canal que el toque 1 | Recordatorio breve, una línea |
| 3 — Seguimiento 2 | Día 7-8 | **Canal distinto** al toque 1 (si empezaste por WhatsApp, prueba email o llamada) | Igual de breve, cambia el canal porque el primero puede no haberse visto |
| 4 — Seguimiento 3 (último) | Día 12-14 | El que quede | Cierra la puerta con educación, deja la opción abierta a que te contacten ellos más adelante |
| — Cierre | Día 15 | — | Se marca `estado=sin_respuesta` en el CRM y se detiene el contacto activo — no se borra la fila |

Los textos exactos de cada toque están en `mensajes-contacto.md`
(sección de seguimiento de cada canal) y `mensajes-personalizados.md`
(versión con campos de fusión).

## Cómo lo calcula la hoja de cálculo

En `crm/prospectos-crm.xlsx`, pestaña **CRM**, las dos últimas columnas
hacen el cálculo por ti:

- **`dias_desde_contacto`**: días transcurridos desde `fecha_contacto`
  (fórmula `=TODAY()-fecha_contacto`). Vacío si todavía no se ha
  contactado.
- **`accion_sugerida_hoy`**: te dice literalmente qué tocaría hacer hoy
  con esa fila, cruzando `dias_desde_contacto` con `num_toques` y con
  `estado`/`respuesta`:
  - Si no hay `fecha_contacto` → *"Contactar (día 0)"*.
  - Si ya respondió, está rechazada, es cliente de pago, o ya se cerró
    como sin respuesta → vacío (fuera de la cadencia, no hace falta
    tocarla).
  - Si lleva 1 toque y ≥3 días → *"Seguimiento 1 (mismo canal)"*.
  - Si lleva 2 toques y ≥7 días → *"Seguimiento 2 (canal distinto)"*.
  - Si lleva 3 toques y ≥12 días → *"Seguimiento 3 (último...)"*.
  - Si lleva 4+ toques o ≥15 días sin respuesta → *"Cerrar: marcar
    sin-respuesta"*.
  - Si no toca nada todavía (está esperando su turno) → vacío.

## Cómo se usa, en la práctica

Cada día del `plan-30-dias.md`, antes de contactar prospectos nuevos:

1. Abre la pestaña CRM y filtra u ordena por la columna
   `accion_sugerida_hoy` (Datos → Filtro, o simplemente ordena
   alfabéticamente esa columna para agrupar las filas con texto arriba
   o abajo).
2. Todas las filas con algo escrito ahí son las que tocan hoy —
   ejecútalas primero, antes que los contactos nuevos del día.
3. Después de cada toque, actualiza a mano en esa fila: `num_toques`
   +1, y si cambiaste de canal, `canal_contacto`. La fórmula recalcula
   sola la próxima vez que abras la hoja.
4. Cuando llegue una respuesta, actualiza `respuesta=sí` y
   `fecha_respuesta` — la fila sale automáticamente de la cadencia (la
   fórmula deja de sugerir nada).

## Qué hacer con las respuestas que no son un "sí" claro

La cadencia de 4 toques es solo para el silencio. Si responden con un
"ahora no, contactadme en dos meses" o similar, **no entra en esta
cadencia** — se anota en `notas` la fecha que han pedido, se pone
`estado=en_seguimiento`, y se agenda un recontacto manual para esa
fecha (fuera del sistema de toques, es una cita concreta que ellos han
pedido, no una insistencia tuya).

## Por qué 3 seguimientos y no más

Más de 3 seguimientos sin respuesta deja de ser seguimiento comercial y
empieza a sonar a acoso — con este perfil de cliente (gerentes con poco
tiempo, career de por medio), insistir más allá del toque 3 daña más la
marca de lo que puede aportar una respuesta tardía. El "cierre" de la
tabla existe justamente para reconocer eso y pasar a otro prospecto sin
mala conciencia ni desgaste.
