# ADR-0016 — Los permisos pasan al nivel B: modo auto, con el bypass bloqueado

| Campo | Valor |
|---|---|
| Fecha | 2026-10-26 |
| Estado | ACEPTADA — decisión del Director («vamos con el B»). **Aplicada en el repo; sin verificar en la PC** |
| Fase | Operación |

## Decisión

En `.claude/settings.json` se fija `defaultMode: "auto"` y `disableBypassPermissionsMode: "disable"`, con reglas `ask` para lo delicado (empujar a `main`, forzar, `reset --hard`, `rm -r` y `rm -f`) y `deny` para leer los `.env`. Reemplaza al riesgo aceptado del 2026-09-14 (`bypassPermissions`) cuando se verifique en la PC.

## Contexto

Hechos verificados contra la documentación oficial de Claude Code, leída el 2026-10-26:

- Los modos son `default`, `acceptEdits`, `plan`, `auto`, `dontAsk` y `bypassPermissions`.
- **La documentación recomienda `bypassPermissions` «solo en entornos aislados, como contenedores o VMs».** Esta PC no usa aislamiento: la virtualización está habilitada desde el 2026-09-15, pero WSL2 está diferido y no se usan contenedores (ADR-0009, `AGENTS.md` §7). *Corrección del 2026-10-26: la primera versión de este ADR decía, por error, que la virtualización estaba apagada.*
- El modo `auto` revisa con un clasificador los comandos y pedidos de red antes de ejecutarlos. Está disponible en **todos los planes**, con Sonnet 4.6 o superior, Opus 4.6 o superior, Haiku 5.5 y Fable. **Haiku 4.5 no está soportado**. Anthropic puede apagarlo del lado del servidor.
- Las reglas las aplica Claude Code, no el modelo; una regla `deny` o `ask` rige aunque un hook devuelva otra cosa, así que el guardia de `~/.claude` sigue sumando.
- `permissions.disableBypassPermissionsMode: "disable"` funciona desde cualquier archivo de configuración.

**No verificado:** el comportamiento en la PC del Director y su versión de Claude Code; si las reglas `ask` piden confirmación dentro del modo `auto`; qué configuración gana entre la del usuario y la del proyecto para `defaultMode`; las reglas para comandos de PowerShell; y si los subagentes con Haiku 4.5 se ven afectados.

## Opciones consideradas

1. **A — seguir con `bypassPermissions`** — descartada: contradice la recomendación oficial en una máquina sin aislamiento.
2. **C — pedir permiso casi siempre** — descartada por fricción: el Director no lee código y aprobaría sin leer.
3. **B — modo `auto` con reglas** — la elegida.

## Enfoque elegido

B, con el clasificador para lo rutinario y reglas explícitas para lo que el contrato reserva al Director (`AGENTS.md` §10).

## Por qué

Mantiene el trabajo fluido y devuelve un punto de control antes de lo irreversible. Es lo que la guía recomienda (`docs/research/guia-claude-code-2026-10.md` §9).

## Trade-offs

- **Se gana:** un control antes de borrar, forzar o publicar.
- **Se pierde:** algunas confirmaciones y la fluidez total.
- **Se acepta:** que el clasificador es un modelo, no un muro: puede equivocarse. Sigue valiendo la separación de roles como control principal (§7).

## Consecuencias

- **Pendiente:** verificar en la PC (que arranque en modo `auto`, que pida confirmación al intentar `rm -r` sobre una carpeta de prueba y que el bypass esté bloqueado) y recién entonces dar por reemplazado el riesgo aceptado.
- **Señal de reconsideración:** tras una semana de uso, contar confirmaciones por sesión, bloqueos injustificados y cualquier incidente. Si el modo `auto` no está disponible o bloquea trabajo legítimo, bajar a `acceptEdits` con una lista de comandos seguros.
