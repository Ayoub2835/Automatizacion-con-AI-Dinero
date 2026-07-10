# Seguimiento del pipeline (CRM simple)

No hace falta ninguna herramienta de CRM para esto — con 50 prospectos,
una sola hoja de cálculo (Google Sheets o Excel) es más rápida de usar
en el día a día que cualquier software, porque necesitas poder ordenar,
filtrar y ver el embudo entero de un vistazo mientras haces llamadas.
Este documento define la estructura, no la herramienta.

## 1. Una fila por gestoría, estas columnas

Copia esta cabecera directamente a una hoja de cálculo:

```
Nombre gestoría | Contacto (persona) | Teléfono | Email | LinkedIn | Ciudad | Tamaño aprox. | Calidez (caliente/tibio/frío) | Encaje (alto/medio/bajo) | Canal 1er contacto | Fecha 1er contacto | Nº de toques | Respuesta (sí/no/pendiente) | Fecha respuesta | Reunión agendada (sí/no + fecha) | Demo realizada (sí/no + fecha) | Piloto aceptado (sí/no/pendiente) | Rechazo (sí/no) | Motivo de rechazo | Ficha de feedback (enlace) | Próxima acción | Fecha próxima acción
```

Notas sobre columnas concretas:

- **Calidez / Encaje**: se rellenan al añadir la fila, según los
  criterios de `lista-prospectos.md` (sección 4). Sirven para ordenar
  la hoja y decidir a quién contactar primero.
- **Nº de toques**: cuenta cuántos mensajes/llamadas se han hecho sin
  respuesta (máximo 3, ver `mensajes-contacto.md`). Al llegar a 3 sin
  respuesta, `Respuesta` pasa a "no" definitivo y se detiene el
  contacto — no se sigue insistiendo.
- **Ficha de feedback**: en cuanto haya una reunión o demo real, se crea
  la ficha correspondiente en `feedback/` (plantilla en
  `proceso-feedback.md`) y aquí se enlaza el nombre de archivo. La hoja
  de cálculo es el estado (dónde está cada prospecto ahora); las fichas
  de `feedback/` son el detalle cualitativo de cada conversación.
- **Motivo de rechazo**: usa siempre una de estas categorías estándar
  (para poder contarlas después, ver sección 3), añadiendo detalle libre
  si hace falta:
  - `ya-resuelto` — usan otra cosa y están contentos.
  - `no-es-el-momento` — reconocen el problema pero no es prioridad ahora.
  - `precio` — preguntaron precio y no siguieron (aunque no haya precio
    fijo, la reticencia a "otra suscripción" cuenta aquí).
  - `confianza` — dudas de seguridad/RGPD o de fiarse de una startup
    pequeña.
  - `sin-dolor-real` — al preguntar, no dedican tiempo relevante a esto.
  - `bloqueante-funcional` — falta algo concreto sin lo que no lo usarían
    (anota cuál — va directo a `roadmap-validado.md` como candidata).
  - `sin-respuesta` — nunca contestó tras 3 toques.
  - `otro` — con el detalle en texto libre.

## 2. El embudo (las etapas, en orden)

```
Prospecto añadido
   → Contacto enviado
      → Respuesta recibida
         → Reunión agendada
            → Demo realizada
               → Piloto aceptado
                  → Piloto completado
                     → Cliente de pago
```

En cualquier etapa puede pasar a **Rechazo** con su motivo. Un rechazo no
es un fallo del proceso — es información. El objetivo de los 30 días
(ver el reto abajo) cuenta conversaciones y demos conseguidas, no solo
los "síes".

## 3. Revisión del embudo (hazlo cada pocos días, no esperes al final)

Con la hoja de cálculo, un resumen de una tabla dinámica o unas fórmulas
simples de conteo por columna te da esto en segundos:

| Métrica | Fórmula (conteo de filas donde...) |
|---|---|
| Contactados | `Fecha 1er contacto` no vacío |
| Con respuesta | `Respuesta` = sí |
| Reuniones agendadas | `Reunión agendada` = sí |
| Demos realizadas | `Demo realizada` = sí |
| Pilotos aceptados | `Piloto aceptado` = sí |
| Rechazos por motivo | Agrupar por `Motivo de rechazo` |

Revisa esto **cada vez que completes un bloque de contactos** (por
ejemplo, cada 10 prospectos trabajados), no en un ciclo de calendario
fijo. Si la conversión de "contacto enviado" a "respuesta" es muy baja
(por debajo de 1 de cada 5), el problema está en los mensajes de
`mensajes-contacto.md` o en la calidez/encaje de la lista, no en el
producto — no lo confundas con una señal sobre el producto en sí.

## 4. Contra el reto de 30 días

Compara el conteo de la sección 3 contra el objetivo:

| Objetivo (30 días) | Columna que lo mide |
|---|---|
| 20 conversaciones | `Respuesta` = sí (una conversación real, no solo un mensaje leído) |
| 5 demos | `Demo realizada` = sí |
| 1-3 pilotos | `Piloto aceptado` = sí |
| 1 cliente de pago | fuera del alcance de esta hoja por ahora — se añade una etapa más cuando se llegue ahí |

Si a mitad del periodo (día 15) el ritmo no da para llegar a 20
conversaciones, la palanca a mover es el volumen de contactos y la
calidez de la lista (`lista-prospectos.md`), no cambiar el producto ni
el mensaje de venta a mitad de camino sin haber probado antes con
volumen suficiente.

## 5. Qué NO hacer con esta hoja

- No la conviertas en una base de datos compleja con más de estas
  columnas mientras el volumen sea de decenas de filas, no de cientos.
- No borres las filas de rechazo — son las que más enseñan. Un rechazo
  archivado es tan útil como un piloto aceptado para saber si el
  producto encaja.
- No mezcles aquí las notas largas de cada conversación — esas van en
  `feedback/`, enlazadas desde la columna correspondiente. Esta hoja es
  el estado, no el detalle.
