# 0001 — Usar Architecture Decision Records (ADRs)

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

El proyecto va a evolucionar mucho durante la fase de validación de
mercado. Sin un registro explícito, se pierde el "por qué" de cada
decisión técnica y se acaba re-discutiendo lo mismo o revirtiendo
decisiones por desconocimiento del contexto original.

## Decisión

Cada decisión técnica con impacto relevante (elección de framework,
modelo de datos, estrategia de despliegue, etc.) se documenta como un ADR
en `docs/decisions/`, con el formato:

```
# NNNN — Título corto en imperativo
**Estado**: Propuesto | Aceptado | Reemplazado por NNNN | Rechazado
**Fecha**: YYYY-MM-DD

## Contexto
## Decisión
## Consecuencias
```

Los ADRs son inmutables una vez aceptados: si una decisión cambia, se crea
un ADR nuevo que referencia y reemplaza al anterior, en vez de editarlo.

## Consecuencias

- Cualquier persona que se incorpore al proyecto puede entender por qué el
  sistema es como es, sin depender de memoria oral del equipo.
- Añade un pequeño coste de disciplina (escribir el ADR) a cambio de
  trazabilidad a largo plazo.
