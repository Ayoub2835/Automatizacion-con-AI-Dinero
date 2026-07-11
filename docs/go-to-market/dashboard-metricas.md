# Dashboard de métricas

El dashboard vive en `crm/prospectos-crm.xlsx`, pestaña **Dashboard** —
son fórmulas en vivo sobre la pestaña **CRM**, no hay que tocar nada en
esta pestaña nunca; se actualiza sola al rellenar el CRM. Este
documento explica qué mide cada fila y cómo interpretarla.

## Métricas principales

| Métrica | Qué cuenta | Fórmula (sobre la pestaña CRM) |
|---|---|---|
| Total prospectos en el CRM | Filas con nombre de gestoría | `COUNTA` de la columna `nombre_gestoria` |
| Contactos realizados | Filas con `fecha_contacto` rellena | `COUNTA` de `fecha_contacto` |
| Respuestas recibidas | Filas con `respuesta = sí` | `COUNTIF` de `respuesta` |
| Reuniones / demos agendadas | Filas con `reunion_agendada = sí` | `COUNTIF` de `reunion_agendada` |
| Demos realizadas | Filas con `demo_realizada = sí` | `COUNTIF` de `demo_realizada` |
| Pilotos iniciados | Filas con `piloto_aceptado = sí` | `COUNTIF` de `piloto_aceptado` |
| Clientes de pago | Filas con `cliente_pago = sí` | `COUNTIF` de `cliente_pago` |
| **MRR (€/mes)** | Suma de `mrr_eur` de las filas con `cliente_pago = sí` | `SUMIF` |
| Rechazos | Filas con `rechazo = sí` | `COUNTIF` de `rechazo` |

`mrr_eur` se rellena a mano en el momento en que una gestoría empieza a
pagar (número, en euros/mes, sin símbolo). Si el primer acuerdo es a
precio reducido o de prueba, ese es el número que va aquí — el MRR real
al que te comprometes, no una lista de precios teórica.

## Tasas de conversión entre etapas

Además de los totales, el dashboard calcula cuatro tasas — la señal más
útil para saber **dónde** se pierde gente en el embudo, no solo cuántos
hay en cada etapa:

- **Contacto → respuesta**: si es baja, el problema está en los
  mensajes (`mensajes-personalizados.md`) o en la calidez/encaje de a
  quién se contacta (`lista-prospectos.md`), no en el producto.
- **Respuesta → demo**: si es baja, revisa cómo se está cerrando la cita
  en la propia conversación (`guion-venta.md`, sección de
  descubrimiento) — puede que se esté "vendiendo" antes de tiempo en vez
  de simplemente pedir los 10 minutos.
- **Demo → piloto**: si es baja, el problema está en la demo en sí
  (`demo-10-min.md`) o en el cierre (`playbook-cierre-pilotos.md`), no
  en la prospección.
- **Piloto → cliente de pago**: la métrica más importante de todas — si
  esta es baja con varios pilotos completados, es la señal más fuerte
  de que algo del producto o del precio no encaja (revisar
  `piloto.md`, preguntas de cierre, y `roadmap-validado.md`).

## El reto de 30 días, con progreso en vivo

La última tabla del dashboard compara los 4 objetivos del mes
(conversaciones, demos, pilotos, cliente de pago) contra el número
actual del CRM y calcula el % cumplido de cada uno. Revísala en los
puntos marcados en `plan-30-dias.md` (días 6-7, 14, 21, 29-30) — no
hace falta ningún cálculo manual, solo abrir la pestaña.

## Qué NO mide este dashboard (a propósito)

- No mide tiempo ahorrado a los clientes ni ninguna métrica de producto
  — eso se recoge cualitativamente en `piloto.md` (preguntas de cierre)
  y en las fichas de `feedback/`, no aquí. Este dashboard es
  puramente del embudo comercial.
- No proyecta MRR futuro ni hace forecasting. Con 1-3 pilotos reales,
  cualquier proyección sería ruido — cuando haya más de 5-10 clientes de
  pago tiene sentido añadir esa vista, no antes.
