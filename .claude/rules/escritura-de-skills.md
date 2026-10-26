---
description: Convenciones para escribir y admitir skills en Bruno AI OS
paths:
  - "skills/**"
  - ".claude/skills/**"
---

# Escribir una skill

**Antes de crear una skill, verificar que no exista ya.** Hay 7 plugins instalados con cero usos y 3 skills propias del Director (`plan-before-build`, `mentor-literario`, `gemini-image-json-prompt`). Usar lo que ya está es más barato que crear.

**Cada skill nueva es un impuesto fijo sobre cada sesión:** las descripciones de todas las skills están siempre en contexto. Pocas y buenas.

## Formato

- `SKILL.md` con frontmatter YAML. Obligatorios: `name`, `description`.
- `name`: 1–64 caracteres, minúsculas, dígitos y guiones. Sin guiones consecutivos. **Debe coincidir exactamente con el nombre de la carpeta** (incluso en NTFS, que no distingue mayúsculas).
- Cuerpo bajo **500 líneas** y bajo **5.000 tokens**.
- Carga progresiva en tres niveles: metadata siempre cargada → cuerpo al activarse → `references/` bajo demanda.
- Subcarpetas canónicas: `references/` (documentación que se lee cuando hace falta), `assets/` (plantillas, datos), `scripts/` (ejecutable).
- **Referencias de un solo nivel.** Anidarlas degrada la lectura.

## Descripción — de acá depende que dispare

El triggering se basa **únicamente** en el campo `description`. Escribirla en tercera persona, diciendo **qué hace + cuándo usarla**, enfocada en la intención del usuario.

Advertencia oficial poco conocida: **los agentes solo consultan skills para tareas que exceden lo que pueden hacer solos.** Una descripción perfecta no dispara en un pedido trivial de un paso.

## Medir, no suponer

Una skill entra solo si mejora un baseline medido. Herramienta: `claude plugin eval` — corre un brazo con la skill y un brazo baseline sin ella, y reporta la diferencia. Casos de prueba negativos útiles: los *near-miss* que comparten palabras clave pero necesitan otra cosa.

## Admisión de skills de terceros

Solo de (a) repos oficiales de Anthropic, (b) organizaciones con reputación verificable y código leído, (c) propias. **Nada de marketplaces agregadores.**

Antes de instalar, revisar con `rg`: comandos de contexto dinámico que invoquen `curl`, `wget`, `nc` o `bash`; `allowed-tools` demasiado amplios; URLs externas; hooks de `session-start`. **Los comandos dinámicos de un `SKILL.md` se ejecutan antes de que el modelo vea nada**: no alcanza con que "el modelo lo note".

## Windows

Rutas con barra normal. Archivos **sin BOM** y con finales de línea **LF** — un BOM antes del `---` inicial rompe el parseo del frontmatter.
