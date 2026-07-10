# Puntos débiles del producto y 20 objeciones de venta

Escrito poniéndose en el lugar del gerente de una gestoría española media
(3-15 empleados, gestiona IRPF/Sociedades/laboral de 200-2000 clientes,
usa A3 o Sage, no tiene perfil técnico interno).

## 1. Autocrítica honesta del producto

Puntos débiles reales, verificados contra el código actual (no
supuestos):

- **El email no dice de qué gestoría viene.** `build_document_request_email`
  no incluye el nombre de la gestoría en ningún sitio, ni asunto ni
  cuerpo, y el remitente (`SMTP_FROM_EMAIL`) es una única dirección
  global para toda la plataforma, no una por gestoría. Un cliente que
  recibe "Documentación solicitada: Campaña Renta 2026" desde una
  dirección genérica tiene motivos legítimos para desconfiar y no abrir
  el enlace. **Este es probablemente el mayor riesgo de adopción real**,
  por encima de cualquier objeción de precio.
- **Sin importación masiva de clientes.** Alta uno a uno por formulario.
  Una gestoría con 300 clientes no va a teclearlos a mano.
- **Un único usuario por gestoría.** `/auth/register` crea una
  organización y un usuario a la vez; no hay forma de invitar a un
  compañero de la oficina a la misma cuenta. En una gestoría con varios
  gestores esto es un bloqueante, no un detalle.
- **Sin duplicar campañas.** Cada campaña de renta/trimestre hay que
  crearla de cero, tecleando otra vez los mismos tipos de documento.
- **Solo email.** Gran parte de la cartera de clientes de una gestoría
  media (especialmente autónomos y clientes de más edad) mira más el
  WhatsApp que el correo.
- **El enlace de subida no caduca ni se puede revocar** (decisión
  explícita del MVP, ver ADR 0008). Aceptable en un piloto con pocos
  clientes de confianza; no lo es a escala.
- **Sin exportación de datos.** Si la gestoría quiere sacar la lista de
  clientes o el estado de una campaña a Excel para su propio archivo, no
  puede.
- **Sin panel agregado entre campañas.** Hay que entrar campaña por
  campaña; no hay una vista "todo lo que tengo pendiente ahora mismo en
  toda la gestoría".
- **Clasificación de Claude puede fallar o no estar activa** (sin
  `ANTHROPIC_API_KEY` todo queda "sin clasificar"). Degrada con
  elegancia — no rompe el flujo — pero si el gestor esperaba
  automatización total y ve todo "sin clasificar", la primera impresión
  es mala.
- **Sin rastro de auditoría ni documento de cumplimiento (RGPD)** que
  poder enseñar a un cliente que pregunte dónde se guardan sus DNIs.
- **Sin plan de precios definido.** No hay nada que responder hoy si
  preguntan "¿cuánto cuesta esto?" más allá de "estamos en fase piloto".

## 2. Las 20 objeciones más probables

Cada una con la respuesta a dar **hoy, sin escribir código**, y — cuando
aplica — la nota de que es candidata a roadmap condicionada a 3
gestorías (ver `roadmap-validado.md`).

**1. "Ya uso A3/Sage/Holded para esto."**
No competimos con tu ERP: resolvemos lo que pasa *antes* de que el
documento entre ahí — reclamarlo y clasificarlo. Hoy no hay integración
directa; se sube el archivo ya clasificado desde el ERP como siempre.
Integración → candidata a roadmap si 3 gestorías la piden (ver ADR 0008,
Fase 3 explícitamente pospuesta).

**2. "Mis clientes no miran el email, todo se lo gestiono por WhatsApp."**
Es la objeción más seria y la más frecuente que esperamos. Hoy: el
enlace seguro se puede copiar y reenviar a mano por WhatsApp (el enlace
no depende del email para funcionar, solo el *aviso* es por email). Si
esto sale en 3+ conversaciones, WhatsApp automático sube de prioridad
inmediatamente.

**3. "¿Cómo sé que ese correo lo hemos mandado nosotros y no es spam/phishing?"**
Objeción legítima y bien fundada — ver autocrítica arriba. Respuesta
honesta en el piloto: "tienes razón, hoy el remitente es genérico;
para tu piloto lo configuramos con el nombre de tu gestoría en el
'De:' (posible hoy sin cambiar código, es una variable de configuración
por despliegue) y avisamos a tus primeros clientes por otro canal de que
va a llegar ese correo." No prometer whitelabel completo todavía.

**4. "¿Es seguro subir el DNI de un cliente a esto?"**
Explicar lo que hay: enlace con token único no adivinable, sin
indexar, sin necesidad de cuenta del cliente. Ser honesto sobre lo que
falta: no hay todavía documento de política de privacidad ni cifrado en
reposo verificado formalmente. No firmar un cliente que gestione datos
especialmente sensibles a gran escala hasta tener eso resuelto.

**5. "¿Cuánto cuesta?"**
"Estamos en fase de validación: los primeros 3-5 despachos lo prueban
gratis a cambio de una reunión de feedback cada 2 semanas. El precio se
define con vosotros, no antes." (Ver `guion-venta.md`, cierre.)

**6. "No tengo tiempo para aprender otra herramienta."**
Ese es literalmente el objetivo del onboarding de 15 minutos (ver
`onboarding.md`): sin formación, sin manual, primera campaña enviada en
la misma llamada.

**7. "Aunque envíe recordatorios automáticos, al final tengo que llamarles igual."**
Cierto y hay que decirlo así de claro: reduce el trabajo, no lo elimina.
El valor está en no tener que acordarte tú de a quién le falta qué — el
panel te lo dice, tú decides si llamas.

**8. "Ya tengo un Excel y un grupo de WhatsApp para esto, funciona."**
No se discute que "funciona" — se cuantifica en la demo cuánto tiempo
cuesta hoy hacerlo así (ver `demo-10-min.md`, minuto 9): perseguir a 40
clientes cada trimestre, ver quién falta, y no tener trazabilidad de qué
se pidió y cuándo.

**9. "No voy a dar de alta a mis 300 clientes uno a uno."**
Cierto hoy — no hay importación masiva. Oferta concreta en el piloto:
"mándame tu Excel de clientes y te los doy de alta yo mismo para
empezar." Importación CSV self-service → candidata a roadmap si 3
gestorías lo piden.

**10. "¿Y si falla internet el día que el cliente tiene que subir el documento?"**
El enlace es asíncrono: el cliente lo abre cuando puede, no depende de
que tú estés conectado en ese momento.

**11. "¿Qué pasa si cerráis la empresa? Mis datos se quedan atrapados."**
Objeción legítima de un proveedor pequeño. Compromiso honesto: "hoy no
hay un botón de exportar todo, pero te lo puedo sacar yo a mano en
cualquier momento que lo pidas, sin coste." Exportación self-service →
candidata a roadmap.

**12. "Ya tengo empleados que hacen esto, no voy a pagar por algo que ya hago con personal."**
No sustituye personal — libera las horas que ese personal dedica a
tareas repetitivas (perseguir documentos) para dedicarlas a
asesoramiento, que es lo que factura mejor.

**13. "¿Pueden usarlo varios de mi oficina, no solo yo?"**
Hoy no — un usuario por cuenta. Decirlo claro y no prometer lo
contrario. Multi-usuario → candidata firme a roadmap (es de las que más
frecuencia esperamos, probablemente llega a 3 votos rápido).

**14. "¿Puedo probarlo con dos clientes antes de meter a todos?"**
Sí, sin ningún problema — de hecho es justo cómo está pensado el piloto:
una campaña pequeña primero.

**15. "No quiero que un robot decida qué documento es qué sin que yo lo revise."**
No decide nada de forma irreversible: si Claude no está seguro, lo deja
"sin clasificar" y lo ves tú. El gestor mantiene el criterio profesional
en todo momento.

**16. "¿Sirve solo para la Renta o también para IRPF trimestral, Sociedades, laboral...?"**
Sirve para cualquier campaña: los tipos de documento son texto libre,
tú decides qué pides en cada una.

**17. "No quiero otra suscripción SaaS más en la lista de gastos."**
No hay suscripción todavía — estamos en fase piloto gratuita. Cuando
haya precio, se plantea contra el ahorro de horas facturables, no como
gasto fijo.

**18. "¿Qué pasa si el cliente sube el documento equivocado?"**
Puede subir varios documentos al mismo enlace; tú los ves todos en el
panel y decides. No bloquea ni impide seguir subiendo el correcto
después.

**19. "Mis clientes son mayores y no van a saber usar un enlace web."**
Es un formulario de una sola pantalla: ver el nombre de la campaña, ver
qué falta, un botón para subir un archivo. Se enseña en la demo (ver
`demo-10-min.md`, minuto 4) precisamente para que se pueda juzgar in
situ si el propio interlocutor lo ve viable para su cartera de clientes.

**20. "¿Por qué debería confiar en una startup nueva con esto en vez de seguir como hasta ahora?"**
No pedimos confianza a ciegas: pedimos un piloto con 2-3 clientes reales
elegidos por ellos, gratis, con reunión de seguimiento a los 15 días
para decidir juntos si continúa. El riesgo de probar es prácticamente
cero.
