# PROGRESS.md — Bruno AI OS

| Campo | Valor |
|---|---|
| Última actualización | 2026-10-17 |
| Fase actual | **11 — Autonomía · cerrada (ADR-0011)** |
| Siguiente | **Trabajo real del Director.** La obra de infraestructura está terminada |
| Resultado de aceptación | **6 aprobadas · 2 parciales · 0 falladas** — `artifacts/pruebas-de-aceptacion.md` |
| Modo de trabajo | **Continuo** — el Director levantó la parada entre fases el 2026-09-15. Se sigue frenando solo ante lo irreversible, credenciales y lo que solo puede hacer él |
| Repositorio | `<carpeta-del-proyecto>` · espejo privado en `bruneskycoder/bruno-ai-os` |

---

## DONE

### Fase 0 — Replanteo `VERIFIED`

- Auditoría read-only completa del entorno. Nada se modificó.
- Investigación verificada de 9 dominios: **178 hallazgos clasificados**.
- **Verificación adversarial** de los 10 claims que gobiernan decisiones: 7 confirmados, 3 corregidos, 0 refutados de raíz.
- Auditoría de 30 repositorios de GitHub con veredicto ADOPTAR / MIRAR IDEAS / DESCARTAR.
- Arquitectura, threat model, plan de fases, 6 ADRs.

### Fase 1 — Cimientos `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| Repositorio en carpeta definitiva | `VERIFIED` | 33 archivos versionados. **Cierra R7** |
| Todo lo de Fase 0 mudado del workspace efímero | `VERIFIED` | Commit `10243c1` |
| `AGENTS.md` canónico + `CLAUDE.md` puntero | `VERIFIED` | ADR-0004 implementado |
| Estructura de directorios | `VERIFIED` | 20 carpetas según `ARCHITECTURE.md` §8 |
| 3 reglas condicionales en `.claude/rules/` | `VERIFIED` | Con `paths:` — cargan solo al tocar esos archivos |
| `.gitignore` estricto | `VERIFIED` | Secretos, backups, ruido de sistema |
| Detección de secretos en pre-commit | `VERIFIED` | gitleaks 8.30.1, **fail-closed**. Bloqueó un token con forma real (exit 1, sin commit) — incluido un intento propio |
| Respaldo fuera del alcance del agente | `VERIFIED` | Bundle de 174 KB en `~/Backups/bruno-ai-os`, **restauración probada**: 29 archivos, historial intacto |
| Espejo privado en GitHub | `VERIFIED` | `bruneskycoder/bruno-ai-os`, visibilidad `PRIVATE` |
| Política de clasificación de datos | `VERIFIED` | Operativa en `AGENTS.md` §6 |
| Pregunta abierta Q8 | `CERRADA` | Ver `docs/research/FINDINGS.md` |

**Decisiones del Director registradas:**
- Plan de fases aprobado **con las dos desviaciones** (medición adelantada a F2, seguridad mínima adelantada a F1).
- Repositorio en `<carpeta-del-proyecto>`.
- `bypassPermissions` se mantiene activo — **riesgo aceptado**, asentado en `THREAT_MODEL.md` §7 D-SEC-1.

Los 6 ADRs pasan de **PROPUESTA** a **ACEPTADA**.

### Fase 2 — Tablero `VERIFIED` (con una salvedad)

| Entregable | Estado | Evidencia |
|---|---|---|
| Status line con medidores de consumo | `PARTIALLY VERIFIED` | Script probado contra 5 casos (normal, crítico, sin datos, JSON corrupto, stdin vacío). **Falta que el Director confirme que se ve en pantalla** |
| Lector de consumo real | `VERIFIED` | `config/consumo.py` lee la telemetría, detecta resets y registra marcas |
| Libro de obra | `VERIFIED` | `logs/libro-de-obra.md` + `logs/consumo.csv` |
| **Línea base numérica** | `PARTIALLY VERIFIED` | `COST_MODEL.md` — una sola observación limpia, limitaciones declaradas |
| Protocolo de sesión operativo | `VERIFIED` | En `AGENTS.md` §4 con los números reales; `memory/HANDOFF.md` en uso |
| Presupuesto por fase en el contrato | `VERIFIED` | Topes y señal de alarma en `AGENTS.md` §4 |

**El número que faltaba:** la ventana semanal vale **≈ 8 millones de tokens**; la de 5 horas, **≈ 1,1–1,4 millones**. Un fan-out sin tope de 15 agentes cuesta **14 % de la semana** — entran siete. Una fase de construcción determinista cuesta **0 %**.

### Fase 3 — Archivo de obra `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| **Memoria automática migrada** | `VERIFIED` | 6 archivos movidos al proyecto nuevo, verificados byte a byte con `cmp`, huérfanos eliminados |
| Tabla de decisión: qué va dónde | `VERIFIED` | `memory/README.md` con diagrama y los cuatro almacenes |
| Plantillas de artefacto, handoff y ADR | `VERIFIED` | `memory/plantillas/` y `docs/decisions/plantilla-ADR.md` |
| **Medición handoff vs reconstruir** | `VERIFIED` | `config/costo-de-retomar.py` → **46x**. Artefacto en `artifacts/costo-de-retomar.md` |
| Lección nueva persistida en memoria | `VERIFIED` | `memoria-automatica-se-ata-a-la-ruta.md` |

**Hallazgo de la fase — pérdida silenciosa de memoria.** La memoria automática se indexa **por ruta de proyecto**. Al mudar el repositorio en Fase 1, los seis archivos de memoria quedaron huérfanos bajo el slug de la carpeta efímera y el proyecto nuevo arrancó con memoria vacía. **Nada falló y no hubo ningún aviso**: el agente simplemente habría dejado de saber quién es el Director. Migrado y documentado.

**Medición de la fase:** reconstruir el contexto leyendo la documentación cuesta ~33.000 tokens; leer el handoff, ~730. **46 veces menos.** Por retomada el ahorro es ~0,4 % del semanal; cada 50 retomadas, ~20 % de una semana entera.

### Fase 4 — Oficios (skills) `PARTIALLY VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| **Auditoría de la capacidad instalada** | `VERIFIED` | `artifacts/auditoria-de-skills.md` con números de la herramienta oficial |
| Herramienta de auditoría reutilizable | `VERIFIED` | `config/auditar-skills.py`; contrastada contra la oficial, 13 % alta |
| 3 skills creadas | `VERIFIED` (formato) | Validadas contra la spec: nombre, carpeta, longitud, sin BOM, LF |
| Ambigüedad de estructura resuelta | `VERIFIED` | Eliminadas `skills/` y `agents/` de la raíz: las skills viven en `.claude/skills/` |
| **Medición de disparo** | **`VERIFIED` (2026-09-15)** | **5/5 casos correctos** con `tests/medir-disparo.py`. Las 3 skills disparan cuando deben y callan cuando no. El harness oficial `claude plugin eval` está en **acceso anticipado** y no está disponible en esta cuenta |

**Lo que se encontró.** 56 skills disponibles en cada sesión, **≈5.280 tokens fijos de contexto**. Dos plugins —`bio-research` (genómica, Nextflow) y `finance` (SOX, asientos contables)— aportan **1.339 tokens y 17 servidores MCP declarados** para capacidades sin ninguna relación con la vida del Director, con **0 usos** desde que se instalaron.

**Lo que se creó:** 3 skills por **378 tokens**, todas con reutilización ya demostrada en este mismo proyecto. Se descartaron deliberadamente las demás del catálogo del mandato §12 por falta de evidencia de reutilización.

> Se puede sacar **3,5 veces más contexto del que se agrega.** Desinstalar los dos plugins es decisión del Director: es su cuenta y es reversible.

### Fase 5 — Herramientas `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| Mapa real de integraciones | `VERIFIED` | `docs/MCP_ARCHITECTURE.md` — medido en la sesión |
| Decisión sobre MCP nuevos | `VERIFIED` | ADR-0007: **no se agrega ninguno** |
| Checklist de admisión | `VERIFIED` | `docs/security/ADMISION-DE-COMPONENTES.md`, 4 puertas |

**La fase se planeó mal y la medición lo mostró.** Iba a "reemplazar los conectores rotos". La realidad: **141 herramientas ya funcionan** en 8 conectores, y los **22 servidores MCP que traen los plugins no funciona ninguno** — 10 sin autenticar, 6 sin URL, 4 con el error de registro dinámico, 2 con endpoint muerto.

Y lo decisivo: **los rotos duplican lo que ya anda.** El plugin de Notion pide autenticación mientras el conector de Notion da 43 herramientas; los de Gmail y Calendar no tienen URL mientras los conectores funcionan.

> No falta nada por conectar. Lo que está roto es redundante.

### Fase 6 — Cuadrillas `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| 3 subagentes con separación de roles | `VERIFIED` | `.claude/agents/` — la separación está **impuesta por configuración**, no por instrucción |
| Tabla de ruteo operativa | `VERIFIED` | `MODEL_ROUTING.md` con modelos, effort, agentes y clasificación de datos |
| **Prueba de la separación de roles** | `VERIFIED` | `tests/validar-componentes.py`, con **prueba negativa**: se le inyectó un agente que viola la regla y lo detectó |

**El control de seguridad dejó de ser una intención.** `investigador` lee el mundo exterior y **no tiene herramientas de escritura, shell ni credenciales**. `ejecutor` cambia el repositorio y **no navega ni lee correo**. `critico` solo lee. El que puede ser atacado no tiene con qué hacer daño; el que puede hacer daño no consume contenido no confiable.

### Fase 7 — Multi-modelo `VERIFIED` (decisión de no instalar)

| Entregable | Estado | Evidencia |
|---|---|---|
| Decisión documentada | `VERIFIED` | ADR-0008: **preparado, no instalado** |
| Viabilidad técnica comprobada | `VERIFIED` | `llm 0.35` + `llm-gemini 0.34`: 34 paquetes, **todos wheels, cero a compilar**. Verificado sin instalar nada |
| Procedimiento listo en un comando | `VERIFIED` | `config/segundo-cerebro.py`, probado en sus rutas de error |
| Regla de datos activa | `VERIFIED` | `AGENTS.md` §6 y `MODEL_ROUTING.md` |
| **Instalado y funcionando** | **`VERIFIED` (2026-09-15)** | El Director generó la clave. Responde de punta a punta con `gemini-3.6-flash`, **sin gastar un token del plan de Claude** |
| **Ventaja medible frente a solo-Claude** | **`BLOCKED`** | Falta la prueba que decide su permanencia: una tarea real donde aporte más que hacerla solo con Claude |

Instalar 34 dependencias que no se pueden ejercitar habría violado la Puerta 0 del propio checklist de admisión. Cuando se active, la clave va al **Credential Manager**, nunca a un archivo.

### Fase 8 — Automatización `PARTIALLY VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| **Respaldo semanal automático** | `VERIFIED` | Tarea de Windows, domingos 20:00. **Probado de punta a punta**: se borraron todos los respaldos y la tarea regeneró un bundle válido de 253 KB |
| Guardia de comandos irreversibles | `VERIFIED` (lógica) | `config/hooks/guardia.py` + `probar-guardia.py`: **11 bloqueos y 10 pasadas, 21/21 correctos** |
| **Guardia activo en sesión** | **`VERIFIED` (2026-09-15)** | **Funcionando.** Bloqueó dos comandos reales en vivo durante su propia instalación |

**Por qué el guardia importa acá.** Con `bypassPermissions` activo por decisión del Director, no hay ninguna confirmación que frene nada. Un hook `PreToolUse` que devuelve código 2 **sí bloquea**, independientemente del modo de permisos: es el único portón programático que queda.

**Honestidad sobre su alcance:** protege contra **accidentes** —un push forzado, un borrado recursivo, un token impreso en claro—, que es el riesgo realista. **No** protege contra un atacante decidido: como todo control por texto, se evade con variables, codificación o rutas absolutas.

**El respaldo no gasta tokens.** Es una tarea del Programador de Windows, no un agente. Usar un modelo para copiar un archivo sería pagar por algo gratis.

**Cierre del 2026-09-15 — el guardia funciona, y el diagnóstico estaba mal.** No fallaba por falta de reinicio: fallaba porque estaba en el `settings.json` **del proyecto**. Movido a la configuración **de usuario**, funcionó al instante. Bloqueó dos comandos míos en vivo durante su propia instalación — comandos legítimos que contenían el texto de un patrón bloqueado. No los reescribí para esquivarlo: es la regla que el propio guardia impone.

Se instala en `~/.claude/guardia.py`, **fuera del repositorio**. Si el hook global apuntara a una ruta del repositorio y esa carpeta se moviera, Python fallaría con código 2 — el mismo código que significa *bloquear* — y ningún comando Bash volvería a ejecutarse en ninguna sesión. Era un modo de falla catastrófico introducido al hacerlo global, detectado antes de dejarlo así.

**Efecto medido de sacar los dos plugins (B9, hecho por el Director):** **56 → 42 skills**, de 5.620 a **4.114 tokens** fijos por sesión, y 17 servidores MCP menos de superficie de ataque.

---

## IN PROGRESS

Nada. La fase está cerrada y commiteada.

---

## BLOCKED

| # | Bloqueo | Quién lo destraba |
|---|---|---|
| B7 | **Confirmar que la status line se ve** en la barra de estado | Director: mirar la barra inferior en este repositorio |
| **R1** | 🔴 **Presupuesto: 55 % del semanal el 2026-09-15 (día 2 de 7)** — sin medición posterior | Ver "Alarma de presupuesto" abajo |
| B11 | **Rotar la clave de Gemini otra vez** | **Error mío:** un script de diagnóstico propio la imprimió en un mensaje de excepción. Ya está corregido, pero la clave quedó quemada |
| B13 | ~~Decidir sobre WSL2~~ | **RESUELTO** — ADR-0009: se difiere con disparadores escritos |
| B14 | Verificar si el **sandbox de VM de la app** está disponible en este plan | Tarea barata y acotada. Si está, vuelve innecesaria la discusión de WSL2 |
| B12 | Comparar calidad **con** y **sin** skill | Bloqueado: `claude plugin eval` está en acceso anticipado |

### 🔴 Alarma de presupuesto — 2026-09-15

El ciclo semanal reseteó el **2026-09-14 13:22**. Hoy, **día 2 de 7**, está en **55 %**.

La regla propia (`AGENTS.md` §4) dice: *si el semanal pasa del 60 % antes del cuarto día, parar y revisar en vez de seguir construyendo*. Estamos a 5 puntos del umbral, con cinco días por delante.

A este ritmo (~41 puntos por día) el plan se agota alrededor del día 3, y el Director se queda **sin Claude por cuatro días**.

**Decisión:** se suspende el trabajo caro. Lo que sigue es documentación determinista, que cuesta 0 %. Esta alarma la disparó el tablero construido en la Fase 2 — es la primera vez que el sistema frena a su propio constructor.

**Al 2026-09-16 no hay medición nueva `BLOCKED`.** La telemetría vive en `plan-usage-history.json`, en la máquina del Director, y solo se actualiza con la app abierta. La computadora está apagada: el 55 % es el último dato real, no el dato de hoy. Primer comando al volver: `python config/consumo.py`.
| B5 | **Q1** — ¿Cowork consume del mismo pool de límites que Claude Code y el chat? | Director: abrir Cowork, usarlo un rato y mirar `/usage` |
| B6 | **Q6** — ¿Los conectores rotos funcionan en claude.ai aunque fallen acá? | Director: abrir claude.ai y probar el conector de GitHub |
| B4 | ~~D-SEC-2 (virtualización en BIOS) y D-SEC-3 (alcance del token de GitHub)~~ | **RESUELTOS** — virtualización habilitada el 2026-09-15; token *fine-grained* en uso |

---

### Fase 9 — Evaluación `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| Pruebas de aceptación §34 (A–H) | `VERIFIED` | **6 aprobadas, 2 parciales, 0 falladas** — `artifacts/pruebas-de-aceptacion.md` |
| Medición de disparo de skills | `VERIFIED` | 5/5 |
| Bancos de prueba del repositorio | `VERIFIED` | 4 bancos, **100 %**: componentes, guardia (25), secretos, respaldo |
| Contraste contra el "DONE" del mandato §42 | `VERIFIED` | **11 de 14 completos**, 3 parciales |

**Las dos parciales, dichas sin adorno:**

- **D — Multi-modelo.** Gemini responde, pero **no hay ventaja demostrada**. `llm` no es un agente: la orquestación sigue corriendo por Claude, así que el ahorro real es cercano a cero. Es lo que ADR-0008 anticipó: *si no muestra ventaja medible, no se integra*. Disponible, no adoptado.
- **G — Seguridad.** Los controles actúan y hay evidencia: el guardia bloqueó tres comandos reales, el detector de secretos bloqueó un commit propio, la separación de roles pasó su prueba negativa. Pero **sin aislamiento no se puede descartar el acceso ilimitado**, y durante la obra se filtraron dos claves — una por el Director y **una por un error propio**.

> El mandato pide **FUNCIONAL + MEDIBLE + REVERSIBLE + SEGURO + EVOLUTIVO**. Los cuatro primeros están. **Seguro está a medias, y es lo único que separa al sistema de su definición de terminado.**

---

### Fase 10 — Endurecimiento `VERIFIED` (decisión de diferir)

| Entregable | Estado | Evidencia |
|---|---|---|
| Virtualización habilitada en el firmware | `VERIFIED` | 2026-09-15, por el Director. **Cierra D-SEC-2** |
| Decisión sobre WSL2 | `VERIFIED` | **ADR-0009: no se adopta todavía**, con cuatro disparadores escritos |
| Revisión de `bypassPermissions` | `VERIFIED` | Se mantiene. Las reglas de permisos matchean el texto del comando y son evadibles: darían fricción sin seguridad. Se reconsidera si aparece aislamiento real |

**El análisis dio vuelta la respuesta esperada.** WSL2 protege la shell, y la shell no es por donde entra el riesgo principal: la trifecta letal de este sistema pasa por los conectores, la web y el correo, que el sandbox no toca. Mudarse habría roto el guardia, la status line, el respaldo, `gitleaks`, el CLI y la memoria automática —huérfana otra vez por cambio de ruta, la lección de la Fase 3 repetida a mayor escala.

### Fase 11 — Autonomía `VERIFIED`

| Entregable | Estado | Evidencia |
|---|---|---|
| Contrato de iniciativa | `VERIFIED` | **ADR-0011** + `AGENTS.md` §10 |
| Criterio de admisión y de revocación | `VERIFIED` | Tres condiciones para entrar, una sola para salir |
| Tareas desatendidas | `VERIFIED` | Congeladas en una: el respaldo semanal. Ninguna procesa contenido externo |
| Documentos maestros sincronizados | `VERIFIED` | `README`, `ARCHITECTURE`, `ROADMAP` y `HANDOFF` decían Fase 1, R7 abierto y `uv` pendiente |

**La premisa de la fase había caducado antes de que la fase llegara.** Se planificó como *"subir el techo de permisos"*, pero `bypassPermissions` estaba activo desde antes de la Fase 0: no había techo que subir. Lo que faltaba escribir era la **iniciativa** —qué hace el agente sin que se lo pidan—, que hasta acá dependía del criterio de cada sesión.

Es además **la primera fase completada sin tocar la máquina del proyecto**: se escribió entera desde una sesión en la nube, con la computadora del Director apagada. El contrato resultó ser la capa más portable del sistema, que es exactamente lo que ADR-0001 predijo.

---

## NEXT

**La obra de infraestructura está cerrada.** Las once fases tienen entregables con evidencia.

Lo que sigue no es otra fase: es **usar el sistema para el trabajo real del Director** —campo, obra, legales, escritura— y dejar que el uso muestre qué falta. Toda mejora que aparezca entra por el criterio de siempre: solo con evidencia medida de que hace falta.

Lo único abierto son los pendientes que dependen del Director, en la tabla de arriba.

---

## RISKS

| # | Riesgo | Severidad | Estado |
|---|---|---|---|
| R1 | Saturación del presupuesto de tokens | **Alta** | **Materializado 2 veces.** Se ataca en Fase 2 |
| R3 | Cero aislamiento + `bypassPermissions` activo | **Alta** | **Riesgo aceptado** por el Director. Mitigación obligatoria: separación de roles (ADR-0006) |
| R8 | Token `gh` con scopes amplios, recuperable en claro | **Alta** | Abierto — D-SEC-3 sube de prioridad por la decisión sobre R3 |
| R2 | 19.7 GB de disco | Media | Controlado |
| R5 | Sin backup verificado | **CERRADO** | Bundle creado, verificado y restauración probada |
| R7 | Trabajo en workspace efímero | **CERRADO** | Repositorio en carpeta definitiva + espejo privado |
| R4 | Catálogo MCP local recortado sin Node | Baja | Resuelto en ADR-0005 |
| R6 | 6 conectores rotos | Baja | Reemplazo definido para Fase 5 |

---

## DECISIONS

| ADR | Decisión | Estado |
|---|---|---|
| 0001 | Bruno AI OS es un repositorio estructurado, no un programa | **ACEPTADA** |
| 0002 | El presupuesto de tokens es restricción de primer orden | **ACEPTADA** |
| 0003 | Memoria en markdown + git + ripgrep, sin embeddings | **ACEPTADA** |
| 0004 | `AGENTS.md` canónico con `CLAUDE.md` puntero | **ACEPTADA** |
| 0005 | No se instala Node.js; MCP remoto con token estático | **ACEPTADA** |
| 0006 | Diseñar asumiendo cero aislamiento; separación de roles | **ACEPTADA** |
| 0007 | No se agrega ningún MCP nuevo: los rotos duplican lo que ya funciona | **ACEPTADA** |
| 0008 | Segundo cerebro (Gemini) preparado, condicionado a mostrar ventaja medible | **ACEPTADA** |
| 0009 | El aislamiento se difiere, con cuatro disparadores escritos | **ACEPTADA** |
| 0010 | MarkItDown como comando para abaratar documentos | **ACEPTADA** |
| 0011 | La autonomía que falta es de iniciativa, no de permisos | **ACEPTADA** |

---

## Costos acumulados

| Fase | Tokens de subagente | Agentes | % del semanal | Nota |
|---|---|---|---|---|
| 0 — Replanteo | 1.864.545 | 22 lanzados, 10 completados, **11 muertos por límite** | **≈ 14 %** | La evidencia que justifica ADR-0002 |
| 1 — Cimientos | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 2 — Tablero | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 3 — Archivo de obra | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 4 — Oficios | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 5 — Herramientas | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 6 — Cuadrillas | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 7 — Multi-modelo | **0** | 0 | ≈ 0 % | Decisión de no instalar |
| 8 — Automatización | **0** | 0 | ≈ 0 % | Trabajo determinista |
| 9 — Evaluación | **0** | 0 | ≈ 0 % *(+ USD 0,66 de la medición de skills)* | Evaluación determinista |
| 10 — Endurecimiento | **0** | 0 | ≈ 0 % | Decisión documentada |
| 11 — Autonomía | **0** | 0 | ≈ 0 % | Contrato escrito; no se instaló nada |

Once fases de construcción real a cero tokens de subagente. No es casualidad: era trabajo determinista hecho con herramientas deterministas. Es la escalera de costo de `AGENTS.md` §5 aplicada a la propia obra.

Detalle por tramo en [`logs/libro-de-obra.md`](logs/libro-de-obra.md); método y limitaciones en [`COST_MODEL.md`](COST_MODEL.md).
