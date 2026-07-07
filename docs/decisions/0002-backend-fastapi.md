# 0002 — Backend en Python + FastAPI

**Estado**: Aceptado
**Fecha**: 2026-07-07

## Contexto

Necesitamos elegir el lenguaje y framework del backend de un SaaS de IA.
El producto probablemente involucrará, en fases futuras, integración con
modelos de lenguaje, procesamiento de documentos y pipelines de datos.
Las alternativas consideradas fueron Python + FastAPI, Node.js + NestJS y
Python + Django.

## Decisión

Backend en **Python 3.12+ con FastAPI**.

Razones:

- El ecosistema de IA/ML/LLM (SDKs de Anthropic/OpenAI, librerías de
  procesamiento de documentos, `pandas`, etc.) es más maduro en Python que
  en Node.js, y este producto integrará LLMs de forma central.
- FastAPI soporta async nativo, generación automática de OpenAPI/Swagger,
  y validación de datos vía Pydantic — buen ajuste con arquitectura limpia
  y con la necesidad de contratos de API claros mientras iteramos rápido.
- Es más ligero y menos "opinionado" que Django, lo cual encaja mejor con
  una arquitectura hexagonal explícita en vez de la estructura MVC de
  Django.

## Consecuencias

- El equipo necesita (o necesitará contratar) experiencia en Python
  moderno con tipado (type hints, Pydantic).
- El frontend y el backend no comparten lenguaje; se mitiga con contratos
  de API tipados (OpenAPI) y generación de tipos TypeScript a partir del
  esquema cuando el frontend lo necesite.
