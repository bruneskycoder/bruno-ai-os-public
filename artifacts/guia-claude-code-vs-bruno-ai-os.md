# Guía de Claude Code contra Bruno AI OS

| Campo | Valor |
|---|---|
| Propósito | Decidir qué de la guía vale implementar en Bruno AI OS y qué no, antes de tocar nada |
| Fecha | 2026-10-26 |
| Versión | 1 |
| Clasificación | INTERNO |
| Fuentes | `docs/research/guia-claude-code-2026-10.md`; inventario del repo en la rama `claude/quirky-dirac-a0na89` (comandos de abajo); `AGENTS.md`, `HANDOFF.md`, ADR-0006, 0007, 0012 y 0013 |
| Estado | **PARTIALLY VERIFIED** — el inventario es verificable; lo que dice la guía sobre comandos y modelos no se contrastó con la documentación oficial. **Cambios 1 a 3 implementados el 2026-10-26 (ADR-0014)**; el 4 y `free-claude-code` siguen abiertos |
| Relaciones | `memory/HANDOFF.md` · `AGENTS.md` §3, §4, §6, §7 · `MODEL_ROUTING.md` |

## Conclusión

Bruno AI OS ya tiene la mayoría de los **mecanismos** que la guía recomienda. Lo que no tiene es chico: una regla de «condición de terminación verificable» y un procedimiento para implementar con evidencia. Y hay una propuesta de la guía que **choca con el contrato** y no debería entrar.

## Lo que ya está (hechos, con evidencia)

| La guía recomienda | En el repo | Evidencia |
|---|---|---|
| `CLAUDE.md` breve, detalle aparte | Sí | `CLAUDE.md` 31 líneas; contrato en `AGENTS.md` (159) |
| Skills para tareas repetibles | 4 | `.claude/skills/`: `arrancar-proyecto`, `checkpoint-de-fase`, `explicar-concepto`, `investigacion-con-artefacto` |
| Subagentes con permisos acotados y revisor | 3 | `.claude/agents/`: `critico` (solo lectura), `investigador` (web, sin escritura), `ejecutor` (escritura, sin web) |
| Separar quien lee contenido externo de quien escribe | Sí, con test | `tests/validar-componentes.py` rompe si un agente tiene escritura y web a la vez (ADR-0006) |
| Secretos fuera del repo | Sí | gitleaks en `pre-commit`, *fail-closed* |
| Contenido externo es dato, no orden | Sí | `AGENTS.md` §7 |
| Estado entre sesiones: PLAN/PROGRESS/DECISIONS | Sí | `PROGRESS.md`, `ROADMAP.md`, 13 ADR, `memory/HANDOFF.md` |
| `/clear` + resumen en vez de compactar | Sí | `AGENTS.md` §4.3 |
| Modelo según dificultad y costo | Sí | `MODEL_ROUTING.md`, escalera en `AGENTS.md` §5 |
| Informes de investigación trazables | Sí | `docs/research/` y la skill `investigacion-con-artefacto` (clasifica por nivel de evidencia) |
| No afirmar sin comprobar | Sí | `AGENTS.md` §3: estados `VERIFIED`/`PARTIALLY VERIFIED`/`ASSUMED`/`BLOCKED` |

## Lo que falta (0 coincidencias en el repo)

| Falta | Qué pide la guía | Hallazgo |
|---|---|---|
| **Condición de terminación verificable** | Definir antes de actuar cómo se demuestra que terminó (§5, §12) | 0 archivos mencionan «criterio de aceptación», «condición de terminación» o «criterios de parada» |
| **Procedimiento de implementación con evidencia** | Bucle leer → planificar → actuar → comprobar → corregir, con límite de iteraciones y de consumo (§12) | Las 4 skills de este repo investigan, explican, arrancan o cierran fases. **Corrección (2026-10-26):** la skill del Director `plan-before-build` sí exige verificación por paso y criterio de éxito al planificar; la brecha real era el ciclo de ejecución con topes y el reporte final |
| **Verificación del resultado real** | Tres niveles: calidad, comportamiento, resultado (§5) | `tests/` valida formato y roles de componentes; no hay un chequeo genérico de entregables |
| **Especificaciones por funcionalidad** | `specs/feature-N.md` | Carpeta inexistente |
| **Contrato de entrega para imágenes de otras IAs** | Dimensiones, formato, transparencia, nombres (§4) | 0 coincidencias; el contrato de **investigación** sí está cubierto |
| **Paralelo con worktrees** | §6 | 0 menciones; ADR-0012 solo regula el fan-out de investigación |

## Lo que choca con el contrato o con decisiones vigentes

| Propuesta de la guía | Conflicto | Recomendación |
|---|---|---|
| **`free-claude-code`**: proxy que enruta Claude Code a otros proveedores (§10) | `AGENTS.md` §6: lo `PERSONAL` va **solo a Claude**. Un proxy manda código y prompts a terceros; sus términos permiten usar prompts para mejorar productos en los tiers gratuitos. Además es AGPL-3.0 y su instalación descarga scripts remotos. Nunca se evaluó (0 menciones en el repo) | **No implementar.** Si interesa para trabajo `PÚBLICO`, abrir un ADR experimental aparte |
| **Permisos mínimos, no aprobar sin leer** (§9) | El repo corre con `bypassPermissions` por decisión del Director (riesgo aceptado, 2026-09-14) y el guardia es evadible por diseño | No se cambia sola. Es una **decisión del Director** con costo de fricción; ver abajo |
| **`/init`** para generar `CLAUDE.md` (§14) | Ya existe y está curado | No correrlo: lo pisaría |
| **MCP, plugins, hooks de formato** (§8) | ADR-0007 (no agregar MCP); el Director no programa, así que un formateador no aplica | No implementar |
| **`/loop`, `/schedule`** (§6) | ADR-0013: el relevo automático corrió un mes sin ejecutarse nunca | Solo con condición de parada y prueba de que corrió |

## Hooks: aclaración

`.claude/settings.json` del repo no tiene hooks ni permisos (solo `statusLine` y `env`). El guardia vive en `~/.claude/guardia.py` de la **PC** (lo copia `config/hooks/instalar.py`). Es **inferencia**: una sesión en la nube no lo tiene instalado, igual que no pasa por gitleaks (ya anotado en el handoff).

## Qué implementar, en orden de costo y valor

Criterio que domina: el costo fijo de contexto (`AGENTS.md` §4.6, cada skill es un impuesto en toda sesión) y la regla «prohibido el overengineering».

| # | Cambio | Costo | Por qué ahora |
|---|---|---|---|
| 1 | Regla de 3 o 4 líneas en `AGENTS.md` §3: toda tarea de construcción declara su **condición de terminación verificable** antes de empezar y reporta qué quedó sin comprobar | Texto, ~100 tokens permanentes | Cierra la brecha más grande. Caso real: en el tramo de portfolio una afirmación de «reproducible» resultó cierta en 12 de 13 páginas al medirla |
| 2 | **Una** skill, `implementar-con-evidencia`, que junta los dos prompts de la guía (§5 y §12) con tope de iteraciones y de consumo | ~60 líneas + una descripción siempre cargada | Reemplaza prompts pegados a mano. Se valida con `tests/validar-componentes.py` |
| 3 | Agregar a `arrancar-proyecto` el contrato de entrega para imágenes de otras IAs | Pocas líneas | Hoy solo está el de investigación |
| 4 | Decidir sobre `bypassPermissions` | Decisión, no código | Es la mayor distancia entre la guía y el repo |

Fuera de alcance por ahora: worktrees, MCP, hooks de formato, `free-claude-code`, `/loop`.

## Dónde y con qué modelo

| Cambio | Dónde | Modelo |
|---|---|---|
| 1, 2, 3 (solo texto y una skill) | Nube o PC; `tests/validar-componentes.py` corre en ambas | Sonnet |
| 4 (permisos, guardia, `settings.json`) | **PC**: el guardia y la telemetría viven ahí y no se pueden probar desde la nube | Opus para decidir y registrar el ADR; Sonnet para ejecutarlo |

## Decisiones del Director

1. ¿Se implementan los cambios 1 a 3 tal como están?
2. ¿Se abre la discusión de `bypassPermissions` (4) o se deja como está?
3. ¿`free-claude-code` queda descartado para trabajo `PERSONAL` y `INTERNO`?

## Cómo se verificó este inventario

```
ls .claude/skills .claude/agents config/hooks docs/decisions tests docs/research
python3 -c "import json; print(json.load(open('.claude/settings.json')).keys())"
grep -r -l -i -E "criterio de aceptaci|condici[oó]n de terminaci|criterios de parada" --include='*.md' .   # 0
grep -r -l -i "free-claude-code" .                                                                          # 0
```

## Estado de las decisiones (2026-10-26)

| # | Decisión | Estado |
|---|---|---|
| 1 | Implementar los cambios 1 a 3 | **Sí.** Hecho: regla en `AGENTS.md` §3, skill `implementar-con-evidencia` y contrato de imágenes en `arrancar-proyecto`. Registrado en ADR-0014 |
| 2 | `bypassPermissions` | **Decidido: nivel B** (modo `auto`, bypass bloqueado). ADR-0016. Aplicado en `.claude/settings.json`, **sin verificar en la PC** |
| 3 | `free-claude-code` | **Descartado por ahora** (decisión del Director, 2026-10-26). Lo valioso que queda: RTK y Headroom, a medir y auditar aparte. Detalle: El Director quiere **probarlo** con trabajo `PÚBLICO`. Auditoría y protocolo de prueba en `artifacts/auditoria-free-claude-code.md`: no instalar como viene (escucha en `0.0.0.0` sin autenticación por defecto); probar solo con condiciones estrictas |

## El cambio 4 explicado sin tecnicismos

`bypassPermissions` es como darle al capataz una autorización firmada para toda la obra: **nunca pide permiso**, ni para demoler. Se trabaja sin interrupciones, que es lo cómodo, pero si algo sale mal (un error del agente o una instrucción maliciosa escondida en una página web) **no hay ningún punto de control** que lo frene. Lo que lo compensa hoy: un script guardia que bloquea ciertos comandos (se puede esquivar), subagentes que leen la web pero no escriben, el escaneo de secretos antes de cada commit y el respaldo semanal.

Hay tres niveles posibles: **A)** como está; **B)** término medio, donde lo seguro (leer, buscar) pasa solo y lo delicado (borrar, publicar, instalar, gastar) pide permiso; **C)** pedir permiso casi siempre. La guía recomienda B. Se prueba en la PC y se decide después de usarlo unos días, no antes.
