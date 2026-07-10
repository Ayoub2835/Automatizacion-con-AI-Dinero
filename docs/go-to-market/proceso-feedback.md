# Proceso de feedback: de la conversación a la tarea priorizada

Objetivo: que ninguna conversación con una gestoría real se pierda, y
que ninguna decisión de producto se tome sin poder señalar a conversaciones
concretas que la respaldan.

## Paso 1 — Una ficha por conversación

Después de **cada** reunión, demo, llamada de onboarding o seguimiento —
sin excepción, incluso si "no ha pasado nada relevante" — crea un
archivo en `docs/go-to-market/feedback/AAAA-MM-DD-nombre-gestoria.md`
con esta plantilla:

```markdown
# [Nombre gestoría] — [fecha]

**Tipo de contacto**: primera reunión / demo / onboarding / seguimiento
**Quién**: nombre y rol de la persona (gerente, socio, administrativo...)
**Tamaño**: nº de clientes aprox. de la gestoría
**Software que usan hoy**: A3 / Sage / Holded / Excel / ninguno centralizado

## Dolor confirmado
(La respuesta literal, o resumida fielmente, a "¿cuánto tiempo os cuesta
hoy reclamar documentación?". Si no se pudo confirmar el dolor, dilo.)

## Objeciones que salieron
(Lista. Marca cuáles ya estaban en `puntos-debiles-y-objeciones.md` y
cuáles son nuevas.)

## Peticiones explícitas de funcionalidad
(Solo lo que pidieron ellos, con sus palabras. No añadas aquí lo que tú
crees que necesitarían.)

## Resultado
Piloto aceptado / rechazado / pendiente de decidir.
Próximo paso y fecha concreta (o "sin próximo paso" si se cerró la
puerta).

## Nota libre
(Cualquier cosa que no encaje arriba pero te parezca importante
recordar.)
```

No hace falta software de gestión de feedback: un archivo Markdown por
conversación, en el propio repositorio, es suficiente en esta fase y
queda versionado junto con el resto del proyecto.

## Paso 2 — De la ficha a la señal

Cada "petición explícita de funcionalidad" de cada ficha se convierte en
una línea en la tabla de candidatas de `roadmap-validado.md`, con estos
campos:

| Campo | Qué significa |
|---|---|
| **Petición** | Descripción corta, en el lenguaje del cliente, no en jerga técnica. |
| **Gestorías que la han pedido** | Lista de nombres (o iniciales si hace falta anonimizar) — no un número, la lista en sí, para poder verificarla. |
| **Fecha de la 1ª mención** | Para detectar si es una moda pasajera o algo sostenido en el tiempo. |
| **Bloqueante o "estaría bien"** | ¿Dijeron literalmente que sin esto no lo usarían, o que "estaría bien tenerlo"? Son prioridades muy distintas. |

Si la misma petición aparece en dos fichas de la **misma** gestoría (por
ejemplo, la mencionan en la demo y otra vez en el seguimiento), cuenta
como **una sola gestoría**, no dos. Lo que valida una petición es la
diversidad de quién la pide, no la repetición.

## Paso 3 — La regla de las 3 gestorías

Una petición solo pasa de "candidata" a "roadmap comprometido" cuando:

1. La han pedido **3 gestorías distintas**, de forma independiente (no
   porque tú se lo sugeriste a la segunda o tercera después de que la
   primera la mencionara — eso contamina la señal).
2. Al menos una de esas tres la ha calificado como **bloqueante**, no
   solo "estaría bien".

Cuando una petición cumple esto, se mueve de la tabla de candidatas a la
sección de "próximo en construir" de `roadmap-validado.md`, con un
enlace a las 3 fichas de feedback que la justifican.

## Paso 4 — Revisión periódica

Cada vez que se cierre una nueva ficha de feedback (no en un ciclo fijo
de calendario — que sea después de cada conversación real), revisa si
alguna candidata ha cruzado el umbral de 3 gestorías. Si es así,
actualízalo en `roadmap-validado.md` inmediatamente, no lo dejes
acumulado.

## Qué NO hacer

- No promediar ni puntuar con fórmulas complejas (RICE, ICE, etc.) en
  esta fase — con 3-10 conversaciones totales, la aritmética no aporta
  nada que el propio criterio no vea a simple vista. Reintroducir un
  marco de puntuación tiene sentido cuando haya volumen (decenas de
  fichas), no antes.
- No mezclar "lo que yo como fundador creo que necesitan" con "lo que
  han dicho". Si quieres proponer una hipótesis propia, anótala aparte,
  fuera de la tabla de candidatas, y no la cuentes como una gestoría.
