# Sistema de mensajes personalizados (email, WhatsApp, LinkedIn)

Este documento no repite las plantillas base — esas están en
[`mensajes-contacto.md`](mensajes-contacto.md) y siguen siendo la
fuente de los textos. Lo que añade este documento es **cómo generar una
versión personalizada por cada una de las gestorías del CRM sin
escribir 200 mensajes a mano uno por uno**, y sin escribir código para
hacerlo.

## Los campos de fusión

Las plantillas de `mensajes-contacto.md` se reescriben con estos campos
entre `{{...}}`, que se rellenan directamente desde las columnas del
CRM (`crm/prospectos-crm.xlsx`):

| Campo | Columna del CRM | Ejemplo |
|---|---|---|
| `{{nombre_gestoria}}` | `nombre_gestoria` | Asesoría Aldaba |
| `{{ciudad}}` | `ciudad` | Málaga |
| `{{nota}}` | `notas` (resumida a una frase corta, a mano) | "especializada en autónomos" |

No hay campo de fusión para el nombre de la persona de contacto porque
el CRM no lo tiene todavía para la mayoría de filas (los directorios
públicos dan el nombre de la empresa, no del gerente) — cuando lo
consigas (llamando y preguntando, o por LinkedIn), añádelo a una columna
nueva `contacto_nombre` en el CRM y úsalo en el saludo en vez de
"Hola equipo de...".

## Plantillas con campos de fusión

**Email — asunto:**
> 10 minutos sobre cómo pedís documentación a vuestros clientes

**Email — cuerpo:**
> Hola, equipo de {{nombre_gestoria}},
>
> Estoy hablando con gestorías de {{ciudad}} sobre un problema muy
> concreto: el tiempo que se dedica cada campaña (Renta, trimestral...)
> a reclamar documentación a los clientes y comprobar quién falta.
>
> Antes de contarte nada, me gustaría entender cómo lo gestionáis hoy
> vosotros — ¿tendríais 10 minutos esta semana para una llamada corta?
> Dime qué día os viene mejor y lo cuadramos.
>
> Gracias,
> [Tu nombre]
> [Teléfono]

**WhatsApp:**
> Hola, os escribo de parte de {{nombre_gestoria}} — soy [Tu nombre].
> Estoy hablando con gestorías de {{ciudad}} sobre cómo gestionáis hoy
> la petición de documentación a vuestros clientes cada campaña (DNI,
> recibos...). ¿Tendríais 10 minutos esta semana para contarme cómo lo
> hacéis? No es una venta, solo quiero entender el problema de primera
> mano.

**LinkedIn — nota de conexión (usar con el nombre de la persona si se
conoce, si no, dirigirse a la gestoría):**
> Hola, estoy hablando con gerentes de gestorías como {{nombre_gestoria}}
> sobre cómo organizan la petición de documentación a clientes cada
> campaña. Me gustaría conectar para, si te interesa, comentarlo 10
> minutos.

## Cómo generar las 200 versiones sin escribir código

**Para email — mail merge con Google Sheets + Gmail:**

1. Sube `crm/prospectos-crm.xlsx` a Google Sheets (Archivo → Importar).
2. Instala un complemento de mail merge gratuito para Gmail (por
   ejemplo, "Yet Another Mail Merge" o "Mailmeteor" — buscar en Google
   Workspace Marketplace, ambos tienen plan gratuito suficiente para
   este volumen).
3. Escribe la plantilla de email de este documento como un borrador en
   Gmail, sustituyendo `{{nombre_gestoria}}` y `{{ciudad}}` por los
   marcadores que use el complemento (normalmente `{{nombre_gestoria}}`
   funciona igual, leen directamente los nombres de columna de la hoja).
4. Conecta el complemento a la hoja de Sheets, mapea las columnas
   `email`, `nombre_gestoria`, `ciudad`, y lanza el envío — solo a las
   filas que ya tengan `email` relleno.
5. El complemento registra automáticamente si se abrió el email; para
   la respuesta en sí, sigues comprobando el correo a mano y
   actualizando el CRM.

**Para WhatsApp: NO automatizar el envío masivo.** A diferencia del
email, mandar WhatsApp en bloque con herramientas de terceros incumple
las condiciones de uso de WhatsApp Business y arriesga el número a un
bloqueo — y además le quita al canal justo lo que lo hace funcionar
(mensaje corto, con nombre de pila, que suena a persona real, no a
campaña). Genera el texto personalizado copiando la plantilla y
sustituyendo `{{nombre_gestoria}}`/`{{ciudad}}` a mano — con la
plantilla ya escrita, son 20-30 segundos por envío, perfectamente
asumible al ritmo de 8-12 contactos/día que marca `plan-30-dias.md`.

**Para LinkedIn: tampoco automatizar.** Las herramientas de
automatización de LinkedIn (envío masivo de invitaciones/mensajes)
violan sus condiciones de uso y pueden llevar a un bloqueo de la
cuenta. Se manda uno a uno, igual que WhatsApp — el volumen de LinkedIn
en este plan es menor que el de email/WhatsApp precisamente por esto.

## Ejemplos ya personalizados (de las 55 gestorías reales del CRM)

Para comprobar que el sistema funciona, aquí están 5 ya rellenados,
listos para enviar tal cual (verifica antes el email/teléfono exacto en
la propia web de cada una, como indica `crm/README.md`):

---

**Sevitia (Sevilla)** — email a `info@sevitia.com`:
> Hola, equipo de Sevitia,
>
> Estoy hablando con gestorías de Sevilla sobre un problema muy
> concreto: el tiempo que se dedica cada campaña (Renta, trimestral...)
> a reclamar documentación a los clientes y comprobar quién falta.
>
> Antes de contarte nada, me gustaría entender cómo lo gestionáis hoy
> vosotros — ¿tendríais 10 minutos esta semana para una llamada corta?
> Dime qué día os viene mejor y lo cuadramos.
>
> Gracias,
> [Tu nombre] · [Teléfono]

---

**Gestoría Aguilera (Bilbao)** — WhatsApp al 688 72 97 38:
> Hola, os escribo de parte de Gestoría Aguilera — soy [Tu nombre].
> Estoy hablando con gestorías de Bilbao sobre cómo gestionáis hoy la
> petición de documentación a vuestros clientes cada campaña (DNI,
> recibos...). ¿Tendríais 10 minutos esta semana para contarme cómo lo
> hacéis? No es una venta, solo quiero entender el problema de primera
> mano.

---

**Asesoría Aldaba (Málaga)** — email a `info@asesoriaaldaba.com`:
> Hola, equipo de Asesoría Aldaba,
>
> Estoy hablando con gestorías de Málaga sobre un problema muy
> concreto: el tiempo que se dedica cada campaña (Renta, trimestral...)
> a reclamar documentación a los clientes y comprobar quién falta.
>
> Antes de contarte nada, me gustaría entender cómo lo gestionáis hoy
> vosotros — ¿tendríais 10 minutos esta semana para una llamada corta?
> Dime qué día os viene mejor y lo cuadramos.
>
> Gracias,
> [Tu nombre] · [Teléfono]

---

**Gestión de Autónomos (Madrid)** — WhatsApp/llamada al 913 83 96 52:
> Hola, os escribo de parte de Gestión de Autónomos — soy [Tu nombre].
> Estoy hablando con gestorías de Madrid sobre cómo gestionáis hoy la
> petición de documentación a vuestros clientes cada campaña (DNI,
> recibos...). ¿Tendríais 10 minutos esta semana para contarme cómo lo
> hacéis? No es una venta, solo quiero entender el problema de primera
> mano.

---

**Centro de Gestión (Zaragoza)** — email a `info@centrodegestion.com`:
> Hola, equipo de Centro de Gestión,
>
> Estoy hablando con gestorías de Zaragoza sobre un problema muy
> concreto: el tiempo que se dedica cada campaña (Renta, trimestral...)
> a reclamar documentación a los clientes y comprobar quién falta.
>
> Antes de contarte nada, me gustaría entender cómo lo gestionáis hoy
> vosotros — ¿tendríais 10 minutos esta semana para una llamada corta?
> Dime qué día os viene mejor y lo cuadramos.
>
> Gracias,
> [Tu nombre] · [Teléfono]

---

Repite este mismo patrón para el resto del CRM a medida que avanza
`plan-30-dias.md` — con las plantillas y el mail merge de arriba, no
hace falta redactar cada una desde cero.
