# Diseño del primer piloto

## Duración

**2-4 semanas, haciéndolo coincidir con un ciclo real de campaña** de la
propia gestoría (una liquidación trimestral, un lote de Renta, un
cierre de Sociedades) en vez de un plazo de calendario arbitrario. El
ahorro de tiempo solo es medible y creíble si se mide contra un ciclo de
trabajo real, no contra dos semanas sueltas sin campaña de por medio.

Dos hitos fijos dentro de ese periodo:

- **Check-in a mitad de piloto** (aprox. día 10-15): llamada corta de
  10 minutos para detectar bloqueos pronto, no esperar al final para
  descubrir que dejaron de usarlo la primera semana.
- **Cierre del piloto** (al terminar el ciclo de campaña): la reunión de
  resultado, ver sección de preguntas más abajo. Se agenda ya en la
  propia reunión de onboarding (ver `guion-venta.md`, cierre), nunca "ya
  quedamos".

## Qué configuraremos

Sigue `onboarding.md` para la mecánica exacta. En el contexto del
piloto, en concreto:

- **Fase 1 (días 1-3): prueba interna con 2-3 clientes.** El propio
  gestor y su equipo suben un documento de prueba para comprobar que
  todo el flujo funciona sin sorpresas antes de exponerlo a clientes de
  verdad en volumen.
- **Fase 2 (resto del piloto): una campaña real completa**, con una
  muestra representativa de clientes de esa campaña — no los 2-3 de
  prueba, sino un grupo lo bastante grande (orden de 15-30 clientes,
  según el tamaño de la gestoría) para que el ahorro de tiempo sea
  perceptible y no anecdótico. Es la propia gestoría quien decide qué
  clientes entran; sugiere empezar por los más colaboradores para
  reducir fricción en esta primera prueba.
- Remitente del email configurado con el nombre real de la gestoría
  (posible hoy sin tocar código, ver `onboarding.md`).
- Tipos de documento reales de esa campaña, no ejemplos genéricos.

## Qué mediremos

| Métrica | Cómo se obtiene |
|---|---|
| Tiempo dedicado a reclamar documentación, antes vs. durante | La cifra "antes" ya se capturó en el descubrimiento (`guion-venta.md`); la de "durante" se pregunta directamente al gestor en el check-in y el cierre — no hay forma de instrumentarlo automáticamente en este MVP, se pregunta. |
| % de clientes que completan sin llamada de seguimiento manual | Comparar el panel de estado (completos/pendientes al cierre) con cuántos de esos completos necesitaron, aun así, una llamada o WhatsApp manual aparte del recordatorio automático (se pregunta, no se mide en el producto). |
| Nº de recordatorios automáticos usados | Directamente del panel (botón de reenvío usado, ver T8/T12). |
| Tiempo medio hasta completar cada cliente | Se puede leer de las fechas de creación de la campaña y de subida de los documentos en el panel de estado. |
| Incidencias técnicas | Cualquier fallo, email no entregado, confusión de un cliente al subir — anotado en el check-in y el cierre, con detalle. |
| Disposición a pagar | Pregunta directa en el cierre (ver más abajo). |

No se necesita ninguna instrumentación nueva para esto — todo sale de
preguntar directamente y de mirar el panel ya construido.

## Qué preguntas haremos

**En el check-in intermedio:**

1. ¿Lo habéis usado de verdad, o ha quedado aparcado esta primera
   semana?
2. ¿Ha habido algún bloqueo o algo que no ha funcionado como
   esperabais?
3. ¿Ha salido alguna objeción o duda nueva que no habíamos hablado
   antes?

**En el cierre del piloto (todas, sin saltarse ninguna, en este orden):**

1. "¿Cuánto tiempo dirías que os ha ahorrado esta campaña frente a cómo
   lo hacíais antes?" — pide una cifra, aunque sea aproximada.
2. "¿Ha habido algún momento en el que preferisteis volver al método
   antiguo (Excel, WhatsApp, llamada)? ¿Por qué?"
3. "¿Qué te ha faltado para que esto sustituya del todo el proceso
   manual?"
4. "¿Tus clientes han tenido problemas para usar el enlace de subida?"
5. "Si tuvieras que pagar por esto hoy, ¿lo harías? ¿Qué te parecería
   un precio razonable al mes?" — no sugieras tú una cifra antes de que
   respondan; escucha primero su número.
6. "¿Se lo recomendarías a otra gestoría? ¿Por qué sí o por qué no?"
7. "Si solo pudieras pedir una cosa nueva, ¿cuál sería?" — esta
   respuesta va directa a `roadmap-validado.md` como candidata, con el
   nombre de esta gestoría.

Sobre la pregunta 5: es razonable tener en la cabeza un ancla de partida
para reaccionar con naturalidad si preguntan "¿y vosotros qué
pensabais cobrar?" — algo en el rango de **40-150€/mes** según el
tamaño de la cartera, mencionado como hipótesis a validar, no como
precio cerrado. Lo que importa de verdad no es acertar la cifra, sino
si dicen que sí pagarían algo y qué orden de magnitud manejan ellos.

Rellena la ficha de `feedback/` con las respuestas literales
inmediatamente después de esta reunión, igual que con cualquier otra
conversación (ver `proceso-feedback.md`).

## Qué resultado necesitamos para saber si funciona

- **Éxito → seguir y proponer pasar a cliente de pago.** El gestor
  confirma un ahorro de tiempo real y cuantificable, responde que sí
  pagaría por esto, y la mayoría de los clientes de la muestra
  completaron el proceso sin fricción grave.
- **Éxito parcial → seguir, sin tocar el producto todavía.** Hay ahorro
  percibido pero con alguna objeción puntual (no compartida por otras
  gestorías) — se anota como candidata en `roadmap-validado.md` con
  esta gestoría como primer voto, y se sigue el piloto o se convierte
  en cliente igualmente si el gestor está dispuesto.
- **Fracaso → aprender y pasar al siguiente prospecto, sin forzar.** El
  gestor no percibe ahorro de tiempo, dice explícitamente que no
  pagaría, o el equipo dejó de usarlo a mitad de piloto sin una razón
  externa clara (no por vacaciones, no por no tener campaña activa esas
  semanas). Se documenta el motivo con el mismo detalle que un rechazo
  (ver `seguimiento-crm.md`) y no se insiste en salvar ese piloto a base
  de cambios de producto para un solo cliente.

## La regla que manda por encima de todo esto

> No se cambia el producto por la opinión de una sola gestoría. Solo se
> modifica el roadmap cuando 3 gestorías distintas tienen el mismo
> problema, o cuando existe una razón de bloqueo clara para vender (por
> ejemplo: nadie firma sin multi-usuario, y lo dicen 3 de 3 pilotos).

Cualquier petición o queja que salga de un piloto va a
`roadmap-validado.md` como candidata con un voto, nunca como una tarea
de desarrollo inmediata — el proceso completo está en
`proceso-feedback.md`.
