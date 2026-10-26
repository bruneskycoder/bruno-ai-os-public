# ADR-0011 — La autonomía que falta no es de permisos: es de iniciativa

| Campo | Valor |
|---|---|
| Fecha | 2026-09-16 |
| Estado | ACEPTADA |
| Fase | 11 — Autonomía |
| Relaciones | ADR-0002 (presupuesto) · ADR-0006 (separación de roles) · ADR-0009 (aislamiento diferido) |

## Decisión

Se amplía la autonomía del agente en **cuatro categorías de iniciativa con historial medido**, se deja **una sola tarea desatendida** —la que ya corre— y se fija un **límite duro sin excepciones**. La ampliación no toca permisos: define qué hace el agente **sin que se lo pidan**.

## Contexto — la premisa de esta fase caducó antes de que la fase llegara

El `ROADMAP.md` escribió la Fase 11 el 2026-09-14 como *"subir el techo, con evidencia"*: ampliar lo que el sistema hace sin preguntar. Esa formulación asume que **las confirmaciones de permisos son el freno**.

En esta máquina no lo son, y no lo fueron en ningún momento de la obra: `bypassPermissions` está activo a nivel de cuenta desde antes de la Fase 0. El agente ya no pregunta nada. **El techo ya está arriba y no hay hacia dónde subirlo.**

Lo que sí quedó sin escribir es lo otro: qué hace el agente **sin que el Director lo pida**, y qué corre **cuando nadie está mirando**. Hasta hoy eso dependía del criterio de cada sesión — exactamente el tipo de cosa que este repositorio existe para no dejar librada al criterio de cada sesión.

## Qué habilita hablar de autonomía acá

Tres controles construidos antes, los tres con evidencia:

| Control | Qué aporta | Evidencia |
|---|---|---|
| Git + libro de obra | Todo lo que el agente hace queda registrado y se deshace en un comando | 16 commits · `logs/libro-de-obra.md` |
| Guardia de comandos | Lo irreversible se bloquea por código de salida, no por confirmación | 25/25 casos · bloqueó comandos reales en vivo |
| `gitleaks` fail-closed | Un secreto no entra al repositorio aunque el agente se equivoque | Bloqueó un commit propio con un token de forma real |

**Sin esos tres, esta decisión no se podría tomar.** La autonomía no se justifica por confianza en el agente: se justifica porque todo lo que haga por iniciativa propia queda escrito y revertirlo es barato.

## 1. Iniciativa — qué hace sin que se lo pidan

| Categoría | ¿Sin preguntar? | Historial que lo respalda |
|---|---|---|
| Actualizar `PROGRESS.md`, `HANDOFF.md` y documentación al cerrar un tramo | **Sí** | 9 fases documentadas sin incidentes ni retrabajo |
| Commitear trabajo terminado y verificado | **Sí** | `gitleaks` fail-closed + historial reversible |
| Correr las pruebas del repositorio antes de declarar algo `VERIFIED` | **Sí** | El contrato ya lo exige; automatizarlo saca un paso manual olvidable |
| Corregir una inconsistencia entre documentos maestros, declarándola en el reporte | **Sí** | Este mismo tramo: cuatro maestros desactualizados aparecieron sin ir a buscarlos |
| Instalar, comprar, publicar, rotar credenciales | **No** | Dos claves filtradas durante la obra, una por error del propio agente |
| Fan-out de subagentes sin tope declarado | **No** | 11 de 15 agentes muertos por límite en 11 minutos |
| Empujar a `main` o a cualquier rama ajena al tramo | **No** | Es la rama de la que depende el espejo y el respaldo |

## 2. Desatendida — qué corre sin nadie mirando

Solo el **respaldo semanal** (tarea del Programador de Windows, domingos 20:00), ya probado punta a punta: se borraron todos los respaldos y la tarea regeneró un bundle válido.

**No se agrega ninguna tarea desatendida más.** La restricción del threat model pasa de nota a regla: *ninguna tarea desatendida procesa contenido externo*. Un agente que lee la web sin testigo y además puede escribir es la trifecta letal, con horario.

## 3. El límite duro

No se mueve, no tiene excepción por conveniencia y no depende de que el guardia lo atrape: **credenciales, compras, BIOS, borrados fuera del repositorio, publicar hacia afuera y todo lo irreversible son del Director.**

## Criterio de admisión y de revocación

Una categoría entra a *sin preguntar* cuando cumple las tres:

1. **Historial medido** — registro de ejecuciones correctas en el libro de obra, no la impresión de que salió bien.
2. **Reversible en un comando** — git, o una tarea que se deshace sola.
3. **No toca contenido externo no confiable ni credenciales.**

Y sale por una sola: **si el Director tuvo que deshacer algo que el agente hizo por iniciativa propia, esa categoría vuelve a preguntar**, y el motivo se escribe en `memory/` como aprendizaje. La revocación no es castigo: es el único mecanismo que impide que la autonomía crezca por inercia.

## Opciones consideradas

| # | Opción | Veredicto |
|---|---|---|
| 1 | Dejar la fase como estaba escrita: subir el techo de permisos | **Descartada.** No hay techo que subir: ya está en bypass |
| 2 | Bajar `bypassPermissions` y reconstruir la autonomía con permisos granulares | **Reservada.** Más limpia en el papel, pero las reglas de permisos matchean texto y son evadibles: daría fricción sin seguridad. Se reconsidera si aparece aislamiento real (ADR-0009) |
| 3 | Escribir qué hace el agente por iniciativa, con criterio de admisión y de revocación | **Elegida** |
| 4 | Ampliar el parque de tareas desatendidas | **Descartada.** Cada tarea desatendida es superficie de ataque sin testigo |
| 5 | No escribir nada y seguir con el criterio de cada sesión | **Rechazada.** Es el estado actual, y es el que hace que dos sesiones se comporten distinto |

## Enfoque elegido

**Opción 3**, con la 2 reservada detrás del disparador de ADR-0009.

## Por qué

Porque el riesgo real de este sistema nunca fue que el agente hiciera de más sin permiso: fue que **cada sesión decidiera distinto**. Una regla escrita sobre iniciativa cuesta unas quince líneas de contexto por sesión y elimina esa varianza. Es la misma lógica que ya gobierna el ruteo de modelos: una tabla, no un programa.

Y porque ampliar autonomía sin ampliar observabilidad sería justo el movimiento que este proyecto viene rechazando desde la Fase 0. Acá la observabilidad se construyó primero, en la Fase 2, adelantada a propósito.

## Trade-offs

- **Se gana:** comportamiento igual entre sesiones; menos ida y vuelta por trivialidades; el cierre de tramo deja de depender de que alguien se acuerde.
- **Se pierde:** el Director se entera **después**, no antes, de cambios que antes habría visto pasar. El reporte de tramo queda como único punto de control de esas categorías.
- **Se acepta a sabiendas:** una corrección por iniciativa propia puede estar mal. Deshacerla cuesta un `git revert`; no tener la regla escrita cuesta que cada sesión improvise.

## Consecuencias

1. `AGENTS.md` gana una sección **§10** con la tabla mínima. Es el único lugar donde tiene que estar, porque es lo que se lee siempre.
2. Toda acción por iniciativa propia **se declara en el reporte del tramo**. El silencio no es autonomía: es pérdida de trazabilidad.
3. La revocación se registra en `memory/` como aprendizaje, con fecha y motivo.
4. **No requiere nada de la máquina del Director.** Esta fase no instala ni configura: es contrato. Entra en vigor en la próxima sesión que lea `AGENTS.md`.

> Consecuencia no obvia: esta es la primera fase que se completó **entera** sin tocar la máquina donde vive el proyecto. El contrato resultó ser la capa más portable del sistema — que es, exactamente, lo que ADR-0001 predijo cuando decidió que esto fuera un repositorio y no un programa.
