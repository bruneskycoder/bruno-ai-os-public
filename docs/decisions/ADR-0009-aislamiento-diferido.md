# ADR-0009 — No se adopta WSL2 todavía: el aislamiento se difiere con un disparador explícito

| Campo | Valor |
|---|---|
| Fecha | 2026-09-15 |
| Estado | ACEPTADA |
| Fase | 10 — Endurecimiento |

## Decisión

**No se instala WSL2 ni se muda el flujo de trabajo.** El aislamiento queda diferido, con un disparador escrito: se instala la primera vez que haya que **ejecutar código que no escribimos nosotros**. Antes de eso, se investiga una vía más barata que la propia app ya parece traer.

## Contexto

La habilitación de la virtualización en el firmware (2026-09-15) abrió por primera vez la puerta al aislamiento real. La pregunta natural era: *¿adoptamos WSL2 ya?*

El análisis dio vuelta la respuesta. Tres hechos lo explican.

### Hecho 1 — El sandbox solo funciona si la sesión corre adentro

El sandbox de Bash de Claude Code no existe en Windows nativo. Para tenerlo, **la sesión entera tiene que correr dentro de WSL2** — es decir, trabajar desde una terminal de Linux, no desde la app de escritorio que el Director usa hoy.

### Hecho 2 — El sandbox protege menos de lo que parece

Restringe red y filesystem **para los comandos de shell**. No alcanza a las otras herramientas del agente: `Read`, `Write`, `Edit`, `WebFetch` ni los conectores de claude.ai.

> Y ahí está el problema: **la trifecta letal de este sistema no pasa por la shell.** Pasa por los conectores (Gmail, Drive, Notion) como fuente de datos privados, por la web y el correo como contenido no confiable, y por `gh` y los propios conectores como canal de salida. **WSL2 no toca nada de eso.**

Lo que sí protege es la ejecución de código desconocido — que es real, pero es un riesgo que **hoy no estamos corriendo**.

### Hecho 3 — Mudarse rompe casi todo lo construido

| Pieza | Qué pasa dentro de WSL2 |
|---|---|
| Guardia de comandos | Instalado en el `~/.claude` de Windows: deja de aplicar |
| Status line | Ruta `C:/...` en la configuración de usuario |
| Respaldo semanal | Tarea del Programador de **Windows** |
| Detección de secretos | `gitleaks` instalado por winget, binario de Windows |
| CLI de Claude Code | Instalado por winget, `.exe` |
| **Memoria automática** | Se indexa por ruta: **quedaría huérfana otra vez** |
| Rendimiento | El acceso a `/mnt/c` es lento; lo recomendable es mover el repositorio adentro de WSL, lo que agrava todo lo anterior |

Costo: 2–4 GB de los 20,3 GB libres, más reconstruir el andamiaje entero. Y la lección de la Fase 3 —mover el proyecto deja la memoria huérfana sin avisar— se repetiría, ahora a mayor escala.

### Hecho 4 — La app ya trae algo parecido `INFERENCE`

En el directorio de datos de la app hay un **binario ELF de Claude Code para Linux, de 224 MB**, en una carpeta llamada `claude-code-vm/`. Y la configuración tiene una clave `lastSeenRequireCoworkFullVmSandbox`, hoy en `null`.

**Inferencia, no verificación:** la app parece capaz de correr sesiones dentro de una máquina virtual Linux, sin que nadie instale WSL2. Si es así, existe un camino al aislamiento que **no cuesta disco ni rompe nada**. No está confirmado que esté disponible en este plan.

## Opciones consideradas

| # | Opción | Veredicto |
|---|---|---|
| 1 | **Mudanza completa a WSL2** | **Descartada.** Rompe el andamiaje entero, cuesta 2–4 GB, obliga a abandonar la app de escritorio, y no cubre el riesgo principal |
| 2 | **WSL2 como celda de ejecución**, sin mover el flujo | **Diferida.** Es la forma proporcionada, pero **hoy no hay código ajeno que ejecutar**: instalarla ahora violaría la Puerta 0 del checklist de admisión |
| 3 | **Investigar el sandbox de VM de la app** | **Elegida como primer paso.** Es la única vía que podría dar aislamiento sin costo de disco ni de mudanza |
| 4 | **Segunda cuenta de Windows** | Reservada. Es el único aislamiento real de secretos —DPAPI es por usuario—, pero cambia mucho el día a día |
| 5 | **No hacer nada** | Rechazada: dejaría el riesgo sin disparador y se olvidaría |

## Enfoque elegido

**Opción 3 primero, opción 2 cuando se dispare el gatillo.**

## Por qué

Porque el criterio de este proyecto es `VALUE > COMPLEXITY + COST + RISK`, y hoy el valor de WSL2 es **menor de lo que parecía**: protege la shell, y la shell no es por donde entra el riesgo principal.

Y porque hay una regla propia que aplica sin excepción, incluso cuando la mejora suena a seguridad: **no se instala infraestructura sin una necesidad concreta demostrada.** Instalar WSL2 "por si acaso" sería exactamente lo que este sistema viene rechazando desde la Fase 0 — con el agravante de que aquí el argumento emocional ("es por seguridad") hace más fácil saltarse el criterio.

## Trade-offs

- **Se gana:** cero disco, cero mudanza, cero andamiaje roto, cero memoria huérfana. Y queda un disparador escrito en vez de una tarea olvidada.
- **Se pierde:** el sistema sigue sin aislamiento. La prueba de aceptación **G — Seguridad** sigue en `PARTIALLY VERIFIED`, y el mandato §42 no llega a "seguro".
- **Se acepta a sabiendas:** si mañana hay que ejecutar código ajeno, hay que instalar antes, no en el momento. El disparador existe para que esa decisión no se tome con apuro.

## Consecuencias

1. La prueba **G** queda parcial **por decisión registrada**, no por olvido.
2. El control principal sigue siendo la **separación de roles** (ADR-0006) — que, dado el Hecho 2, resulta ser **el control adecuado para el riesgo real**, no un sustituto de segunda del sandbox.
3. Se agrega al checklist de admisión: **ningún componente de terceros se ejecuta sin aislamiento previo.**
4. La virtualización queda habilitada: el costo de instalar WSL2 cuando haga falta bajó de "entrar al BIOS y reiniciar" a "un comando y un reinicio".

### Disparadores — se instala WSL2 cuando ocurra **cualquiera** de estos

1. Hay que **ejecutar código que no escribimos**: un servidor MCP de terceros, una skill de un repositorio ajeno, un script de una fuente externa.
2. Hay que **procesar contenido no confiable con herramientas de escritura** en el mismo agente.
3. Se confirma que el sandbox de VM de la app **no** está disponible en este plan **y** el Director quiere cerrar la prueba G.
4. El repositorio deja de ser solo texto y pasa a ejecutar servicios.

### Tarea previa, barata

Verificar si el **sandbox de VM de la app** está disponible en este plan. Es una pregunta acotada, y si la respuesta es sí, vuelve innecesaria toda esta discusión.
