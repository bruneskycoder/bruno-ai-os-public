# Auditoría de free-claude-code y protocolo de prueba

| Campo | Valor |
|---|---|
| Propósito | Decidir si probar `free-claude-code` y cómo, sin poner en riesgo la máquina ni los datos del Director |
| Fecha | 2026-10-26 |
| Versión | 1 |
| Clasificación | INTERNO |
| Fuentes | Repositorio `Alishahryar1/free-claude-code`, commit `707b6dd` (2026-10-25), leído con `grep` sin ejecutar nada; `AGENTS.md` §5–§7; guía en `docs/research/guia-claude-code-2026-10.md` |
| Estado | **PARTIALLY VERIFIED** — auditoría dirigida, no lectura completa (≈265.000 líneas con tests, ≈80.000 en `src/`). **Descartado por ahora** (decisión del Director, 2026-10-26) |
| Relaciones | `artifacts/guia-claude-code-vs-bruno-ai-os.md` · `AGENTS.md` §6 (clasificación de datos) |

## Conclusión

**No instalar tal como viene. Probarlo es defendible, con condiciones estrictas y solo con trabajo `PÚBLICO`.** La ventaja esperable para este sistema es **baja** (inferencia, ver más abajo). Se decide midiendo, con un criterio fijado antes.

## Qué es

Un proxy local en Python (FastAPI) que hace que Claude Code y otros clientes hablen con modelos de otros proveedores. No hace más barata una sesión con Claude: **la reemplaza** por otro modelo. Licencia **AGPL-3.0-only**; el README declara que es independiente de Anthropic.

## Hechos verificados en el código

| Hecho | Evidencia |
|---|---|
| **Escucha en todas las interfaces por defecto** (`0.0.0.0`), puerto 8082 | `src/free_claude_code/config/settings.py:744-745` |
| **La autenticación del proxy viene desactivada** y el token por defecto es el conocido `freecc` | `settings.py:746-753` |
| Abre el panel de administración en el navegador al arrancar | `settings.py`, `open_admin_browser` por defecto `True` |
| Por defecto **no** registra el contenido de los prompts: solo metadatos | `settings.py:668-692`, todas las opciones `log_raw_*` en `False` |
| Desactiva la telemetría de los clientes que lanza | `cli/managed/claude.py:110` (`DISABLE_TELEMETRY=1`) |
| **Exige Python exacto 3.14.9**; esta máquina usa 3.13 | `pyproject.toml`, `requires-python` |
| **30 dependencias directas y 165 paquetes** instalados | `pyproject.toml`, `uv.lock` |
| Incluye bots de Telegram y Discord, voz, y conexión por OAuth con cuentas de ChatGPT y GitHub Copilot | dependencias (`python-telegram-bot`, `discord.py`, `github-copilot-sdk`) y README |
| **Instalador de ≈4.000 líneas** (1.874 en shell y 2.182 en PowerShell) que descarga `uv` de `astral.sh` y modifica el `PATH` del usuario | `scripts/install.sh`, `scripts/install.ps1` |
| El README manda ejecutar ese instalador directo desde la red | README, sección Install (`curl … \| sh` e `irm … \| scriptblock`) |
| Promete «61 proveedores» y «1,3 mil millones de tokens gratis por mes» | README; **es afirmación del proyecto, no verificada** |

## Qué no pude verificar

- Si el panel de administración queda protegido por la autenticación del proxy: no encontré dónde se aplica.
- Qué hacen en detalle las 4.000 líneas de instalador ni todo lo que descargan (menciona herramientas de terceros).
- Los términos de cada proveedor, y si usar cuentas por OAuth respeta sus condiciones.
- Que los 61 proveedores existan y rindan como dice el README.

## Qué ganás y qué no

| Con free-claude-code | Sin él |
|---|---|
| Parte del trabajo sale del cupo de Claude Pro y va a cuotas gratuitas de otros | Sigue todo en Claude, con tu escalera de costo |
| Los modelos gratis suelen rendir menos y fallar más con herramientas | La calidad es conocida y medida |
| **Vos no leés código:** un modelo más débil te cuesta más, porque no podés detectar sus errores | Los controles de `bruno-ai-os` (tests, chequeos) ya compensan a Claude |
| Los tiers gratuitos pueden usar tus prompts para mejorar sus productos (`AGENTS.md` §6) | Solo Claude ve tus datos |
| Costo oculto: instalar, configurar y mantener, pagado con tu cupo o tu tiempo | Sin mantenimiento |

**Inferencia (no medida):** el beneficio es chico hoy por tres motivos. (1) La escalera de `AGENTS.md` §5 ya manda lo mecánico a herramientas y Haiku. (2) Lo caro fue la investigación, y ya se delega a Gemini y ChatGPT (ADR-0012: un fan-out sin tope cuesta 14 % del semanal). (3) La mayor parte de tu trabajo es `PERSONAL` o `INTERNO` y no puede salir de Claude.

## Protocolo de prueba propuesto

**Condiciones de seguridad (todas, o no se prueba):**
1. Solo trabajo `PÚBLICO`, en un repositorio de práctica.
2. **No ejecutar el instalador directo de la red.** Descargarlo, leerlo y fijar la versión al commit `707b6dd`.
3. Respaldo previo con `python config/backup.py`.
4. Configurar `HOST=127.0.0.1` y `PROXY_AUTH_ENABLED=true` con un token largo y aleatorio, **antes** de la primera ejecución.
5. Claves **nuevas**, de cuota gratuita, sin tarjeta y revocables. Nada de OAuth con tus cuentas principales (ChatGPT, GitHub Copilot). No conectar Claude Desktop. No activar Telegram ni Discord.
6. Sesiones de prueba **sin** `bypassPermissions` (esta máquina no usa sandbox: la virtualización está habilitada, pero WSL2 está diferido, ADR-0009).

**Tareas (las mismas por las dos vías, con la condición de terminación declarada antes):**
1. Mecánica: ordenar archivos de un repo de práctica y actualizar los enlaces.
2. Corregir un error sembrado en un script chico que tenga un test.
3. Generar una hoja HTML que pase el chequeo de maquetación del constructor.

**Se mide por tarea y por vía:** si cumplió la condición, vueltas, minutos, consumo (`python config/consumo.py --marcar/--diferencia` para Claude; cuota usada en el proveedor para la otra) y cuántas correcciones tuviste que pedir.

**Criterio fijado antes:** se adopta **solo para tareas mecánicas públicas** si cumple las tres tareas con a lo sumo dos vueltas más que Claude **y** el ahorro medido supera lo que costó instalarlo y configurarlo, contando ese costo. Se descarta si falla una tarea o si la configuración gastó más de lo que ahorra. Tope de la prueba: **5 % del semanal**.

**Salida:** leer `scripts/uninstall.*` antes de instalar, borrar `%USERPROFILE%\.fcc` y revocar las claves.

## Decisión del Director (2026-10-26)

Se **descarta por ahora**. El protocolo queda como referencia por si cambian las condiciones.

## ¿Hay algo valioso para aprovechar sin instalarlo?

Sí, pero no es el proxy. El README integra dos herramientas de terceros que apuntan al problema de los tokens. Datos según la página de cada proyecto, resumidos con una herramienta; **no auditados**:

| Herramienta | Qué hace | Cómo se conecta | Lo que se sabe | Lo que no |
|---|---|---|---|---|
| **RTK** (`rtk-ai/rtk`) | Filtra y comprime la salida de comandos de shell antes de que el agente la lea | Un hook `PreToolUse` que reescribe los comandos Bash; binario en Rust | Apache-2.0 en el binario, pero **BUSL-1.1** en dos componentes. Promete 60 a 90 % menos **solo en la salida de comandos**, no en la cuenta total; es afirmación de sus autores | Fecha del último commit, benchmark independiente, comportamiento en Windows y convivencia con el guardia |
| **Headroom** (`headroomlabs-ai/headroom`) | Comprime salidas de herramientas, logs y contexto | Un **proxy local** (`headroom wrap claude`), una librería y un servidor MCP | Apache-2.0; **telemetría anónima activada por defecto**. Promete «20 % menos» en agentes de código, con evidencia débil | Fecha del último commit y ahorro real en tu trabajo |

**Lectura (inferencia):** RTK es el más liviano y no usa proxy, pero ataca solo la salida de comandos, que es una parte del gasto. Headroom vuelve a ser un proxy entre Claude Code y Anthropic, con la misma clase de riesgo que se descartó. **Antes de sumar cualquiera, medir dónde se van los tokens** (`AGENTS.md` §4.7, `python config/consumo.py`): si los comandos de shell no son una parte grande, el ahorro prometido no te alcanza. Si lo son, RTK se audita aparte, como exige el contrato, con costo declarado.

Lo que sí se aprovecha sin instalar nada: la idea de **elegir modelo e intensidad por tipo de tarea y tener un respaldo ordenado**. Ya está adoptada como aviso de modelo (ADR-0015).

## Cómo se verificó

```
git ls-files … | xargs wc -l                       # tamaño
grep -n "host:\|proxy_auth" src/free_claude_code/config/settings.py
grep -n "log_raw_" src/free_claude_code/config/settings.py
wc -l scripts/install.sh scripts/install.ps1
```
