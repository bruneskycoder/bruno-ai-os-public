# ADR-0014 — La condición de terminación verificable entra al contrato y se suma una skill de implementación

| Campo | Valor |
|---|---|
| Fecha | 2026-10-26 |
| Estado | ACEPTADA — decisión del Director («sí del 1 al 3») |
| Fase | Operación |

## Decisión

1. Se agrega al contrato (`AGENTS.md` §3) la regla de que toda tarea de construcción declara **cómo se demuestra que terminó** antes de empezar, reporta lo que no pudo comprobar y lleva tope de iteraciones y de consumo.
2. Se suma **una** skill, `implementar-con-evidencia`, que operacionaliza esa regla como ciclo con topes y reporte final.
3. Se agrega a `arrancar-proyecto` el **contrato de entrega para imágenes** de otras IAs.

## Contexto

La guía «Cómo trabajar mejor con Claude Code» (`docs/research/guia-claude-code-2026-10.md`, fuente secundaria sin reverificar) recomienda un ciclo verificable y contratos de entrega. El cruce contra el repo (`artifacts/guia-claude-code-vs-bruno-ai-os.md`) encontró que casi todos los mecanismos ya existían y que faltaban tres cosas. Hechos:

- Ningún archivo del repo mencionaba «criterio de aceptación», «condición de terminación» ni «criterios de parada».
- **Solapamiento detectado al implementar:** la skill del Director `plan-before-build` ya exige verificación por paso y criterio de éxito cuando se planifica. La brecha real es el ciclo de ejecución, sus topes y el reporte final.
- Una skill nueva es un impuesto fijo sobre cada sesión (`.claude/rules/escritura-de-skills.md`), y la regla de la casa pide que entre solo si mejora un baseline medido. Esa medición no se puede hacer hoy: `claude plugin eval` sigue en acceso anticipado (B12). **Esta decisión no está medida.**

## Opciones consideradas

1. **No hacer nada, porque `plan-before-build` cubre la planificación** — descartada: no cubre los topes ni el reporte, y las tareas chicas no pasan por un plan.
2. **Solo la regla, sin skill** — descartada: una regla sin procedimiento se olvida; la skill carga solo cuando se construye.
3. **Las tres skills que sugiere la guía** (implementar, auditar, validar) — descartada: triplica el impuesto fijo por un beneficio no medido.
4. **Regla + una skill + contrato de imágenes** — la elegida.

## Enfoque elegido

La regla vive en el contrato (unas 120 palabras, siempre cargada). La skill ocupa 54 líneas, con la descripción siempre en contexto y el cuerpo solo al activarse, y se declara complementaria de `plan-before-build`. El contrato de imágenes son pocas líneas dentro de `arrancar-proyecto`.

## Por qué

Coincide con «nunca afirmar sin evidencia» (`AGENTS.md` §3) y cierra un caso real: en el tramo de portfolio una afirmación de «reproducible» resultó cierta en 12 de 13 páginas al medirla. Con la regla, la condición se declara antes y esa diferencia aparece en el reporte, no después.

## Trade-offs

- **Se gana:** un criterio explícito de «terminado», topes que evitan ciclos largos y un reporte que separa lo comprobado de lo supuesto.
- **Se pierde:** unas 120 palabras fijas en el contrato, una descripción más en el contexto de toda sesión y algo de fricción en tareas chicas.
- **Se acepta:** que la skill entre sin medición contra un baseline, por decisión del Director.

## Consecuencias

- `tests/validar-componentes.py` valida la skill nueva (formato y separación de roles): pasa con 5 skills y 3 subagentes.
- Los proyectos ya creados con `nuevo-proyecto.py` **no heredan** la regla: su `AGENTS.md` es una copia anterior. Propagarla es una decisión aparte.
- **Señal de reconsideración:** si en tres usos reales la skill no cambia el resultado frente a trabajar sin ella (medido con `plugin eval` cuando exista, o comparando a mano el reporte final), se elimina. Si `plan-before-build` absorbe el ciclo, se fusionan.
