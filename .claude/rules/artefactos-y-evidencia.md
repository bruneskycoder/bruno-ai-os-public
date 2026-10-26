---
description: Encabezado obligatorio de artefactos y estados de evidencia
paths:
  - "artifacts/**"
  - "docs/**"
  - "memory/**"
---

# Artefactos y evidencia

## Encabezado obligatorio

Todo artefacto o documento relevante abre con una tabla:

| Campo | Contenido |
|---|---|
| Propósito | Para qué existe, en una línea |
| Fecha | `YYYY-MM-DD` |
| Versión | Entero o `mayor.menor` |
| Clasificación | `PERSONAL` · `INTERNO` · `PÚBLICO` — **sin declarar se asume PERSONAL** |
| Fuentes | URLs o rutas. Los datos verificados llevan fuente o no son verificados |
| Estado | `VERIFIED` · `PARTIALLY VERIFIED` · `ASSUMED` · `BLOCKED` |
| Relaciones | Artefactos o ADRs vinculados |

## Estados de evidencia — no negociables

Prohibido escribir "implementado", "funcionando", "integrado", "seguro" u "optimizado" sin evidencia.

En investigación, separar además: `VERIFIED` (documentación o repositorio oficial recuperado, con URL) · `COMMUNITY EVIDENCE` (foros, issues, blogs) · `INFERENCE` (razonamiento propio) · `RECOMMENDATION` (juicio de diseño).

**Un "no pude verificar" honesto vale más que un dato plausible falso.** Lo que no se pudo verificar se declara como pregunta abierta, no se disfraza de hecho.

## Decisiones

Toda decisión importante se registra como ADR en `docs/decisions/`, con: Decisión · Contexto · Opciones consideradas · Enfoque elegido · Por qué · Trade-offs · Consecuencias · Fecha.

## Memoria — qué sí y qué no

Persistir: decisiones, hechos, configuraciones, conceptos, estado, artefactos, aprendizajes.
No persistir: conversaciones completas, duplicados, información obsoleta, contexto temporal.

Enlazar archivos relacionados con `[[nombre]]`.
