# Plan de ejecución de 30 días

Objetivo del plan (no del código): **20 conversaciones, 5 demos, 1-3
pilotos, 1 cliente dispuesto a pagar.** Se controla en
`crm/prospectos-crm.xlsx` (pestaña Dashboard), no de memoria. Cero
funcionalidad nueva de producto en estos 30 días (ver la regla en
`README.md`).

Convención: "contactar" significa usar `mensajes-personalizados.md`
(email/WhatsApp/LinkedIn) o el guion de `mensajes-contacto.md`
(llamada); "seguimiento N" significa el toque N de
`seguimiento-automatico.md`; "demo" sigue `demo-10-min.md` dentro de
`guion-venta.md`; "piloto" sigue `piloto.md`; cerrar sigue
`playbook-cierre-pilotos.md`.

## Día 1 — Completar el CRM y arrancar por el círculo cercano

- Ejecutar el sprint de investigación para ampliar `crm/prospectos-crm.xlsx`
  de 55 a 200 filas (ver receta al final de este documento). Resérvale
  la mañana; es la única tarea de "investigación pura" de todo el plan.
- Por la tarde: escribir a **todo tu círculo cercano** (contactos
  `calidez=caliente`) pidiendo su propia gestoría o una recomendación —
  es la fuente con más tasa de respuesta, se usa el primer día, no se
  guarda para más adelante.
- Marca cada envío en el CRM (`estado=contactado`, `fecha_contacto`,
  `canal_contacto`).

## Días 2-5 — Primera oleada de contacto (tier A/B, caliente y tibio)

- Cada día: contactar 8-12 gestorías nuevas, priorizando en este orden:
  caliente+alto → caliente+medio → tibio+alto (ver `lista-prospectos.md`,
  sección 4).
- Cada día: revisar el CRM y aplicar `seguimiento-automatico.md` a
  cualquier contacto que ya tenga 3-4 días sin respuesta.
- En cuanto alguien responda que sí, **agenda la demo esa misma
  conversación**, no lo dejes para "ya te escribo" — cita concreta,
  igual que indica `guion-venta.md`.

## Días 6-7 — Primer corte de revisión

- Contar en el Dashboard: contactos, respuestas, demos agendadas.
- Si la tasa de contacto→respuesta va por debajo de 1 de cada 5, revisar
  los mensajes (`mensajes-personalizados.md`) y la calidez/encaje de a
  quién se está escribiendo — no esperes a la semana 2 para ajustar.
- Seguir contactando tier A/B restantes y hacer los seguimientos que
  toquen según el calendario.

## Días 8-14 (semana 2) — Demos y segunda oleada

- Cada día con huecos libres: 1-3 demos agendadas de la semana 1 (usar
  `demo-10-min.md` dentro de `guion-venta.md`).
- Cada día: seguir contactando prospectos nuevos (tier A/B tibio/frío,
  y tier C si hace falta volumen) hasta agotar bloques de 10.
- Aplicar seguimiento 2 y 3 (`seguimiento-automatico.md`) a los
  contactos de la semana 1 que sigan sin respuesta.
- En cada demo que termine bien, usa el cierre de `guion-venta.md` para
  proponer el piloto — no dejes ninguna demo sin una pregunta de cierre
  explícita.
- Rellena una ficha en `../feedback/` después de cada demo, sin
  excepción, aunque no lleve a nada.

## Días 15-21 (semana 3) — Arrancan los primeros pilotos

- Onboarding (`onboarding.md`) de cada piloto aceptado, en los 2-3 días
  siguientes a que digan que sí — no lo dejes enfriar.
- Seguir con demos pendientes de la semana 2 y últimos contactos nuevos
  si todavía falta volumen para las 20 conversaciones.
- Check-in intermedio (`piloto.md`) de cualquier piloto que ya lleve
  más de 7-10 días activo.
- Cierre del ciclo de seguimiento (toque 3 → "sin respuesta") para todo
  contacto de la semana 1 que siga en silencio; libera esas filas del
  foco activo, pero no las borres del CRM.

## Días 22-28 (semana 4) — Cierre de pilotos y últimas demos

- Reuniones de cierre de piloto (`piloto.md`, preguntas de cierre) para
  cualquier piloto que llegue al final de su ciclo de campaña.
- Aplicar `playbook-cierre-pilotos.md` en cada cierre: la conversación
  de cierre es la más importante de todo el plan, no se improvisa.
- Si algún piloto dice que sí paga: cerrar el acuerdo (aunque sea
  informal al principio — un email de confirmación con precio y fecha
  de primer cobro basta) y registrar `cliente_pago=sí` y `mrr_eur` en el
  CRM inmediatamente.
- Seguir agendando y haciendo demos si el número de 5 aún no está
  cubierto — no se detiene la prospección por tener pilotos activos.

## Días 29-30 — Revisión completa del mes

- Abrir la pestaña Dashboard y comparar contra la meta: 20
  conversaciones, 5 demos, 1-3 pilotos, 1 cliente de pago.
- Repasar `../feedback/` completo: ¿hay alguna petición que ya haya
  cruzado el umbral de `roadmap-validado.md` (3 gestorías, o un bloqueo
  de venta claro y repetido)? Si es así, es el único caso en que se
  reabre la conversación de construir algo — y solo entonces.
- Repasar los rechazos por `motivo_rechazo` (ver `seguimiento-crm.md`,
  sección 3): si un motivo se repite mucho, es la señal más valiosa del
  mes, más que cualquier piloto individual.
- Decidir el plan de los siguientes 30 días en función de estos
  números reales, no de la sensación general del mes.

---

## Receta para ampliar el CRM de 55 a 200 (Día 1, y cuando haga falta más volumen)

Mismo método que se usó para las 55 primeras (`crm/README.md`): buscar
`"gestoría asesoría autónomos pymes [ciudad] dirección teléfono"` (o
variantes) y registrar solo negocios con nombre propio verificable,
nunca inventados. Ciudades objetivo para las 145 filas restantes, a
~5-6 gestorías por ciudad:

Gijón, Vitoria-Gasteiz, Córdoba, Elche, Oviedo, L'Hospitalet (ampliar),
Badalona, Cartagena, Terrassa, Jerez de la Frontera, Sabadell,
Móstoles, Alcalá de Henares, Pamplona, Fuenlabrada, Almería, Leganés,
Getafe, Castellón de la Plana, San Sebastián, Burgos, Santander,
Albacete, Alcorcón, Logroño, Badajoz, Salamanca, Huelva, Marbella,
Lleida, Tarragona, Cádiz, Torrejón de Ardoz, Girona, Toledo, y una
segunda vuelta con más profundidad en Madrid/Barcelona/Valencia (son las
tres provincias con más densidad de gestorías, dan para más de 6 cada
una).

Al añadir cada gestoría nueva al CRM, rellena como mínimo `nombre`,
`ciudad`, `web` o `telefono`, `tier`/`calidez`/`encaje` — el resto
(`fuente`, `notas`, `proxima_accion`) igual que en las 55 ya cargadas.
