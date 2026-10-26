# Pruebas de aceptación — ¿esto sirve?

| Campo | Valor |
|---|---|
| Propósito | Someter el sistema construido a las pruebas del mandato §34, con evidencia |
| Fecha | 2026-09-15 |
| Versión | 1.0 |
| Clasificación | INTERNO |
| Fuentes | El propio repositorio, sus bancos de prueba y el historial de esta obra |
| Estado | **VERIFIED** — todas las afirmaciones se apoyan en evidencia ejecutada |
| Relaciones | `ROADMAP.md` · `PROGRESS.md` · `COST_MODEL.md` |

---

## Regla de esta evaluación

Una prueba **no se aprueba porque el componente exista**. Se aprueba si hay evidencia de que **funcionó**. Donde la evidencia es parcial, el veredicto es parcial — aunque la fase esté "terminada".

## Resultado

| Prueba | Veredicto |
|---|---|
| **A — Investigación** | ✅ `VERIFIED` |
| **B — Software** | ✅ `VERIFIED` |
| **C — Conocimiento** | ✅ `VERIFIED` (medido) |
| **D — Multi-modelo** | ⚠️ `PARTIALLY VERIFIED` |
| **E — Economía de tokens** | ✅ `VERIFIED` (medido) |
| **F — Recuperación ante fallo** | ✅ `VERIFIED` |
| **G — Seguridad** | ⚠️ `PARTIALLY VERIFIED` |
| **H — Zero-code** | ✅ `VERIFIED`, con fricción medible |

**6 aprobadas, 2 parciales, 0 falladas.**

---

## A · Investigación ✅

> *"Investigá X" → clasifica → investiga → verifica → artefacto → memoria.*

No se simuló: **se ejecutó durante la Fase 0**. 10 dominios, **178 hallazgos** clasificados en `VERIFIED` / `COMMUNITY EVIDENCE` / `INFERENCE` / `RECOMMENDATION`. Verificación adversarial de los 10 claims que gobernaban decisiones: **7 confirmados, 3 corregidos, 0 refutados de raíz** — y las tres correcciones se incorporaron.

Artefactos: `docs/research/FINDINGS.md` más 10 JSON crudos. Memoria: 6 archivos persistentes.

**Lo que lo hace pasar de verdad:** las preguntas abiertas se declararon como tales (`Q1`…`Q8`) en vez de rellenarse con suposiciones plausibles.

## B · Software ✅

> *"Construí X" → spec → arquitectura → implementación → tests → depuración → docs.*

El ciclo completo, recorrido sobre el guardia de comandos:

| Etapa | Evidencia |
|---|---|
| Spec | Vector V5 y decisión D-SEC-1 del threat model |
| Arquitectura | ADR-0006: separación de roles; hook `PreToolUse` con código 2 |
| Implementación | `config/hooks/guardia.py` |
| Tests | `probar-guardia.py`, 25 casos **incluida prueba negativa** |
| Depuración | Falso positivo real encontrado en uso (`--output-format`) y corregido |
| Docs | ADR + regla del repositorio + libro de obra |

Se repitió en el respaldo, el lector de consumo y el medidor de skills. **13 herramientas propias**, todas con su banco de prueba.

## C · Conocimiento ✅ *(medido)*

> *Reutiliza información previa sin reconstruir todo el contexto.*

**46 veces más barato.** Reconstruir el contexto leyendo la documentación: ~33.000 tokens. Leer el handoff: ~730. Medido con `config/costo-de-retomar.py`, no estimado a ojo.

Y se probó en condiciones reales: la memoria automática quedó huérfana al mudar el repositorio, se detectó, se migró con verificación byte a byte, y la lección quedó persistida para que no vuelva a pasar en ningún proyecto.

## D · Multi-modelo ⚠️

> *Puede delegar entre modelos sin copy/paste manual cuando aporte valor.*

**Lo que funciona:** el segundo cerebro responde de punta a punta con `gemini-3.6-flash`, sin gastar un token del plan de Claude, y con la regla de clasificación de datos activa.

**Por qué no es un aprobado:**

1. **No hay ventaja demostrada.** El mandato pide delegar *cuando aporte valor*. No se midió ninguna tarea donde Gemini rindiera mejor o más barato que hacerla con Claude. Sin ese número, la integración no está justificada — solo está disponible.
2. **No es delegación real.** `llm` es una llamada de texto, no un agente: no lee archivos ni ejecuta nada. La orquestación sigue corriendo por Claude, así que el ahorro real es cercano a cero.
3. **El alcance es angosto por diseño.** Los términos del tier gratuito prohíben datos personales, y este repositorio es un mapa detallado de la máquina del Director. Queda restringido a trabajo público.

**Veredicto honesto:** la capacidad existe, el valor no está probado. Es exactamente lo que ADR-0008 anticipó: *si no muestra ventaja medible, no se integra*. Sigue en evaluación, no adoptado.

## E · Economía de tokens ✅ *(medido)*

> *Demostrar reducción de trabajo redundante.*

| Evidencia | Número |
|---|---|
| Línea base del plan | Semanal ≈ 8M tokens; ventana de 5 h ≈ 1,1–1,4M |
| Fases 1 a 8 de construcción | **0 tokens de subagente** |
| Fan-out sin tope vs. con tope | 14 % del semanal vs. 9 %, mismo trabajo |
| Auditoría de capacidad instalada | **−1.339 tokens** fijos por sesión, −17 servidores MCP |
| Handoff vs. reconstruir | **46×** más barato |

**La prueba más fuerte no es un número: es que el instrumento frenó a su propio constructor.** El 2026-09-15, con el semanal en 55 % en el día 2 de 7, el tablero disparó la alarma y se suspendió el trabajo caro. Un sistema que mide pero no actúa sobre lo medido no sirve de nada.

## F · Recuperación ante fallo ✅

> *Provocar un fallo controlado y recuperar.*

Se **borraron todos los respaldos** a propósito. La tarea programada de Windows corrió sola y regeneró un bundle válido de 253 KB. Por separado, se clonó desde un bundle y se recuperaron los **29 archivos con el historial intacto**.

No fue una verificación de que el archivo existiera: fue destruir y recuperar.

## G · Seguridad ⚠️

> *Una herramienta comprometida no obtiene acceso ilimitado.*

**Lo que sí está probado:**

| Control | Evidencia |
|---|---|
| Separación de roles | Impuesta por configuración de herramientas, con **prueba negativa**: se inyectó un agente que la viola y el test lo rechazó |
| Guardia de comandos | 25/25 casos. **Bloqueó tres comandos reales míos** en uso, no solo en pruebas |
| Detección de secretos | Fail-closed. **Bloqueó un commit propio** que llevaba un token con forma real |
| Respaldo fuera de alcance | El bundle vive donde ningún agente trabaja |
| Token de GitHub | Reducido a *fine-grained*, solo los repos necesarios |

**Por qué no es un aprobado:**

1. **No hay aislamiento.** Sin sandbox, una herramienta comprometida corre con los permisos completos del usuario. La virtualización recién se habilitó (2026-09-15); adoptarla exige decisión y trabajo (`B13`).
2. **Los controles son por texto y evadibles.** El guardia protege contra **accidentes**, no contra un atacante decidido. Está escrito así en su propio código.
3. **`bypassPermissions` sigue activo** por decisión registrada del Director. No hay confirmación intermedia que frene nada.
4. **Dos claves filtradas durante la obra**, una por el Director y otra **por un error propio** en un script de diagnóstico. Ambas rotadas, ambas con su corrección documentada — pero ocurrieron.

**Veredicto honesto:** el daño posible está acotado y hay evidencia de que los controles actúan. Pero "acceso ilimitado" solo se descarta de verdad con aislamiento, y todavía no lo hay.

## H · Zero-code ✅ *(con fricción)*

> *El Director puede operar el sistema mediante lenguaje natural.*

En toda la obra, el Director **no escribió una línea de código, ni un script, ni una configuración**. Dirigió en lenguaje natural, decidió en los checkpoints y autorizó lo irreversible.

**La fricción, medida con honestidad:** tuvo que ejecutar comandos a mano tres veces — el login del CLI, el token de GitHub y la clave de Gemini. Las tres son autenticación o credenciales, que el contrato reserva explícitamente para él. Pero **son comandos igual**, y en dos de esos tres hubo un problema (`Ctrl+V` guardando basura invisible, y la clave pegada en el chat).

**Mejora identificada:** los pasos con credenciales necesitan más andamiaje — terminal abierta lista, advertencia de pegado, validación inmediata. Parte ya se aplicó.

---

## Qué falta para el "DONE" del mandato §42

| Requisito | Estado |
|---|---|
| Existe repositorio | ✅ 13 commits, 70 archivos, espejo privado |
| Arquitectura documentada | ✅ Con 8 ADRs |
| Skills funcionan | ✅ **5/5** de disparo medido |
| Memoria funciona | ✅ Migrada, verificada, medida |
| Artefactos funcionan | ✅ 3 artefactos, convención y plantillas |
| MCP necesario funciona | ✅ Decisión fundada de **no agregar ninguno** (ADR-0007) |
| Model routing funciona | ✅ Tabla operativa + subagentes con modelo asignado |
| Workflow multi-modelo | ⚠️ Disponible, valor sin demostrar |
| Git y recuperación | ✅ Destruido y recuperado |
| Logging funciona | ✅ Libro de obra + consumo + registro del guardia |
| Benchmarks pasan | ✅ 4 bancos, 100 % |
| Controles de seguridad probados | ⚠️ Probados; falta aislamiento |
| El Director opera en lenguaje natural | ✅ Con fricción en credenciales |
| Ningún componente crítico depende de una conversación | ✅ Todo en archivos versionados |

**11 de 14 completos, 3 parciales, ninguno fallado.**

> El mandato pide **FUNCIONAL + MEDIBLE + REVERSIBLE + SEGURO + EVOLUTIVO**, no perfección.
> Funcional: sí. Medible: sí, y es su punto más fuerte. Reversible: sí, probado destruyendo. Evolutivo: sí, con señales de reconsideración escritas.
> **Seguro: parcialmente** — y es lo único que separa a este sistema de su definición de terminado.

## Lo que sigue, en orden de valor

1. ~~**`B13` — decidir sobre WSL2.**~~ **Resuelto en ADR-0009: se difiere.** El análisis dio vuelta la premisa de esta lista — el sandbox de Bash protege la shell, y **la trifecta letal de este sistema no pasa por la shell**, pasa por los conectores. WSL2 no la toca. Queda un disparador escrito: se instala cuando haya que ejecutar código ajeno.
2. **`B12` — comparar calidad con y sin skill.** Bloqueado por acceso anticipado del harness oficial.
3. **`D` — probar Gemini en una tarea pública real** y medir si aporta. Si no aporta, **darlo de baja** es el resultado correcto.
