# ADR-0004 — AGENTS.md canónico con CLAUDE.md como puntero

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

Las instrucciones permanentes viven en un **`AGENTS.md` canónico**. `CLAUDE.md` queda como archivo corto que lo importa y agrega solo lo específico de Claude Code.

## Contexto

- `AGENTS.md` es un formato abierto con adopción real y masiva: más de 60.000 repositorios, soportado por Codex, Gemini CLI, Cursor, Copilot, Zed y Warp, entre otros.
- **Anthropic no figura en la lista oficial de agentes que soportan `AGENTS.md`.** El "estándar universal" tiene justo el agujero que importa: la herramienta principal del Director.
- En Windows **no se puede** usar `ln -s AGENTS.md CLAUDE.md`: los symlinks exigen privilegios de administrador o Modo Desarrollador. La documentación oficial recomienda el import `@AGENTS.md`.
- Los `CLAUDE.md` se concatenan por jerarquía y los imports se expanden al arrancar, recursando hasta 4 saltos.

## Opciones consideradas

1. **Solo `CLAUDE.md`** — simple, pero acopla todo el contrato a un proveedor.
2. **Duplicar el contenido en ambos archivos** — dos fuentes de verdad que divergen en la primera edición.
3. **Symlink** — imposible sin admin en Windows.
4. **`AGENTS.md` canónico + `CLAUDE.md` puntero por import.**

## Enfoque elegido

Opción 4.

## Por qué

Una sola fuente de verdad, portabilidad real y costo cero. Cumple el principio de interoperabilidad del mandato (§35) sin acoplar el núcleo a Anthropic.

## Trade-offs

- **Se gana:** si mañana el Director usa otro agente, el contexto del repositorio viaja con él.
- **Se pierde:** un nivel de indirección. Hay que recordar editar `AGENTS.md`, no `CLAUDE.md`.
- **Se acepta:** las reglas condicionales de `.claude/rules/` con `paths:` son específicas de Claude Code y no son portables. Es un precio razonable por la economía de contexto que dan.

## Consecuencias

- `AGENTS.md` es el documento extenso; `CLAUDE.md` tiene pocas líneas.
- Las skills se escriben en formato `SKILL.md` estándar dentro de `.claude/skills/`, porque **Claude Code no escanea `.agents/skills/`**. Se proyecta una copia a `.agents/skills/` solo cuando exista un segundo cliente que la use.
- Cuidado en Windows: rutas con barra normal, finales de línea LF, y **sin BOM** — PowerShell 5.1 escribe BOM por defecto y eso rompe el parseo del frontmatter YAML.
