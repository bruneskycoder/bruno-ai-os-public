# ADR-0006 — Diseñar asumiendo cero aislamiento: separación de roles

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

El control de seguridad principal de Bruno AI OS es la **separación de roles entre agentes** —lector sin credenciales, ejecutor sin contenido externo— y no las reglas de permisos, que se tratan como fricción y registro de auditoría.

## Contexto

Medido en la máquina, no supuesto:

- **Virtualización deshabilitada en el firmware** (`HypervisorPresent: False`, `VirtualizationFirmwareEnabled: False`). Sin WSL2, sin Windows Sandbox, sin Docker. Habilitarla exige entrar al BIOS.
- **El sandbox de Bash de Claude Code no existe en Windows nativo** (documentación oficial: solo macOS, Linux y WSL2).
- **Las reglas de permisos matchean el comando tal como está escrito**: no matchean el mismo programa invocado por ruta absoluta ni dentro de `sh -c`.
- `bypassPermissions` está opt-in a nivel de cuenta.
- La "trifecta letal" ya está completa: conectores (datos privados) + web, email e issues (contenido no confiable) + `gh`, `curl` y conectores (canal de salida).
- La única mitigación que la evidencia 2025-2026 sostiene como efectiva es **determinística**, no evaluada por modelos.

## Opciones consideradas

1. **Confiar en las reglas de permisos** — la documentación misma las declara evadibles.
2. **Exigir habilitar virtualización antes de empezar** — bloquea la obra por una decisión de firmware del Director.
3. **Diseñar asumiendo cero aislamiento, separando roles**, y dejar el endurecimiento estructural como decisión posterior.

## Enfoque elegido

Opción 3.

## Por qué

Es el único control que no depende de que un modelo o un matcher de texto acierte. Rompe la trifecta por diseño: el agente que navega no tiene con qué exfiltrar, y el agente que puede actuar no consume contenido no confiable.

## Trade-offs

- **Se gana:** reducción real del daño posible, sin depender del entorno.
- **Se pierde:** flexibilidad. Un solo agente que hace todo sería más cómodo y más barato.
- **Se acepta honestamente:** esto **no impide** una prompt injection exitosa. Reduce el daño; no elimina el vector.

## Consecuencias

- Los subagentes de Fase 6 se diseñan con esta separación desde el principio, no como agregado posterior.
- Controles mínimos adelantados a Fase 1: `gitleaks` en pre-commit, `.gitignore` estricto, `git bundle` fuera del alcance del agente, y clasificación de datos.
- Los checkpoints entre fases dejan de ser burocracia y pasan a ser el control humano del sistema.
- Tres decisiones quedan explícitamente en manos del Director (`THREAT_MODEL.md` §7): `bypassPermissions`, virtualización en BIOS, y alcance del token de GitHub.
