# CLAUDE.md

El contrato de obra canónico vive en `AGENTS.md`. Se importa entero:

@AGENTS.md

Lo siguiente es específico de Claude Code y no forma parte del contrato portable.

## Configuración de esta obra

- **Modelo de sesión:** Sonnet 5. Subir a Opus 5 solo para arquitectura, trade-offs o depuración difícil.
- **Subagentes:** Haiku 4.5 salvo justificación escrita. Es donde se multiplica el gasto.
- **Bloqueado por el plan** (requieren usage credits, deshabilitados): Fable 5/5.1, contexto 1M en Opus, fast mode.
- **Shell:** hay Git Bash y PowerShell 5.1 al mismo tiempo. Git Bash para POSIX, PowerShell para lo nativo de Windows. Cada uno con su sintaxis; no mezclar.

## Antes de empezar cualquier tramo

1. Leer `PROGRESS.md`.
2. Si hay `memory/HANDOFF.md`, leerlo y borrarlo al retomar.
3. Si el pedido ya está resuelto en `artifacts/`, leer el artefacto en vez de rehacer el trabajo.

## Al cerrar un tramo

1. Escribir `memory/HANDOFF.md`: estado, decisiones tomadas, próximo paso.
2. Actualizar `PROGRESS.md` si cambió el estado de la fase.
3. Commitear.
4. `/clear` antes del tramo siguiente — no dejar que dispare el auto-compact.

## Recordatorio de costos

Todo fan-out de subagentes declara su costo estimado antes de ejecutarse. Fan-out solo para investigación de lectura con ramas independientes; nunca para trabajo con estado compartido.
