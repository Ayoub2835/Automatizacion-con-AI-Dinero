# CRM de prospectos

- **`prospectos-crm.csv`** — fuente de verdad, versionada en el repositorio (texto, se puede diferenciar con git).
- **`prospectos-crm.xlsx`** — la misma información en Excel/Google Sheets, con dos pestañas:
  - **CRM**: los mismos datos que el CSV, con listas desplegables en las
    columnas de estado (`tier`, `calidez`, `encaje`, `estado`,
    `canal_contacto`, `respuesta`, `reunion_agendada`, `demo_realizada`,
    `piloto_aceptado`, `rechazo`, `cliente_pago`, `motivo_rechazo`) para
    que rellenarlo a mano sea rápido y sin errores de escritura.
  - **Dashboard**: fórmulas en vivo sobre la pestaña CRM — contactos,
    respuestas, demos, pilotos, clientes de pago, MRR, tasas de
    conversión entre cada etapa, y el progreso contra el reto de 30 días.
    Se actualiza solo al rellenar la pestaña CRM, no hace falta tocar
    nada en Dashboard.

**Trabaja siempre sobre el `.xlsx`** (ábrelo en Excel o súbelo a Google
Sheets) — es el que se actualiza y el que hay que rellenar día a día.
El `.csv` es la versión de referencia que queda en el repositorio; si
quieres que el `.csv` refleje cambios hechos en el `.xlsx`, expórtalo de
nuevo a CSV desde Excel/Sheets sobrescribiendo este archivo.

## Sobre las 55 filas de este CRM (y por qué no son 200)

Las 55 gestorías de este CRM son **reales**, encontradas por búsqueda web
el 2026-07-11, con nombre, ciudad y — cuando estaba disponible
públicamente — web, teléfono, email y dirección, citando la fuente.
Cubren 14 ciudades españolas grandes y medianas (Madrid, Barcelona,
Valencia, Sevilla, Zaragoza, Málaga, Bilbao, Alicante, Palma, Murcia,
Valladolid, A Coruña, Vigo).

**No se han inventado las 145 filas restantes hasta 200.** Rellenar un
CRM con nombres de empresas ficticios o con datos de contacto no
verificados sería peor que no tener el CRM — se perdería tiempo
contactando direcciones erróneas y, si alguna coincidiera por azar con
una empresa real, se le atribuiría información incorrecta. En su lugar,
`../plan-30-dias.md` incluye la receta exacta (misma técnica que se ha
usado para estas 55) para llegar a 200 en los primeros días del plan:
qué buscar, en qué ciudades, y cuántas por ciudad — es trabajo de una
tarde, no de una semana, y es mejor que lo ejecutes tú (o alguien de
confianza) con acceso a búsqueda en tiempo real y criterio para
descartar resultados que no encajen.

## Antes de escribir a cualquiera de estas 55

Varias filas tienen teléfono/web pero no email, o viceversa — el campo
`proxima_accion` de cada fila ya dice qué verificar primero. Visita la
web de cada gestoría para confirmar el dato de contacto exacto antes
del primer mensaje; los datos aquí son los que aparecían en fuentes
públicas en la fecha de búsqueda y pueden haber cambiado.
