# Medición de disparo de las skills

| Campo | Valor |
|---|---|
| Propósito | Responder si las tres skills creadas se activan cuando corresponde |
| Fecha | 2026-09-15 |
| Versión | 1.0 |
| Clasificación | INTERNO |
| Fuentes | 5 sesiones headless reales con `claude -p`, inspeccionando el flujo de eventos |
| Estado | **VERIFIED** |
| Relaciones | `artifacts/auditoria-de-skills.md` · `.claude/rules/escritura-de-skills.md` |

---

## Resultado

**5 de 5 casos correctos.** Las tres skills disparan en pedidos que les corresponden y se quedan calladas en pedidos que no.

| # | Caso | Esperado | Resultado |
|---|---|---|---|
| 1 | "Terminé el trabajo de la fase. Cerrala como corresponde." | dispara | ✅ `checkpoint-de-fase` |
| 2 | "Qué alternativas hay para versionar archivos grandes, comparadas, documentado." | dispara | ✅ `investigacion-con-artefacto` |
| 3 | "No entiendo por qué se usa separación de roles en vez de permisos." | dispara | ✅ `explicar-concepto` |
| 4 | "¿Cuántos archivos .md hay en docs?" | **no** dispara | ✅ solo usó `Bash` |
| 5 | "Corregí el error de tipeo 'recuros' en el README." | **no** dispara | ✅ solo usó `Grep` y `Glob` |

Costo de la medición: **USD 0,6625** en 5 sesiones.

## El hallazgo que cambió el diseño de la prueba

El primer intento usó el pedido *"explicame en una sola frase qué es una API"*. **No disparó ninguna skill.** No era un defecto de la descripción: es comportamiento documentado por Anthropic —

> los agentes solo consultan skills para tareas que **exceden lo que pueden hacer solos**.

Un pedido trivial de un paso no dispara nada, por perfecta que sea la descripción. Por eso los casos positivos de esta medición son pedidos no triviales, que es como el Director realmente le habla al sistema.

**Consecuencia práctica:** no tiene sentido escribir una skill para algo que el agente ya resuelve en un turno. Sería peso muerto: cuesta contexto en cada sesión y no se activa nunca.

## Por qué no se usó el harness oficial

`claude plugin eval` existe, está documentado y sería la herramienta correcta —brazo con-skill contra brazo baseline, tres corridas por caso, graders—. Pero responde:

```
`plugin eval` is currently in early access
```

No está disponible en esta cuenta. No es un problema de instalación ni de login: el CLI está instalado y autenticado, y se verificó que responde.

Esta medición es una versión mínima del mismo experimento. **Responde menos**: confirma que la skill se activa, pero no mide si el resultado con skill es mejor que sin ella. Esa pregunta queda abierta hasta que el harness oficial esté disponible.

## Cómo repetirla

```
python tests/medir-disparo.py
python tests/medir-disparo.py --caso 3
```

Conviene volver a correrla cada vez que se agregue una skill o se cambie una descripción.
