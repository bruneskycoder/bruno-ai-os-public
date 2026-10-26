# MCP_ARCHITECTURE.md — Qué está conectado y qué no

| Campo | Valor |
|---|---|
| Propósito | Mapa real de las integraciones disponibles, y la política para agregar más |
| Fecha | 2026-09-15 |
| Versión | 1.0 |
| Clasificación | INTERNO |
| Fuentes | Estado de conectores de la sesión, medido el 2026-09-15 |
| Estado | **VERIFIED** |
| Relaciones | ADR-0005 · ADR-0007 · `docs/security/THREAT_MODEL.md` |

---

## Qué dice

La Fase 5 se planeó para "conectar herramientas". La medición mostró otra cosa:

> **No falta nada por conectar. Lo que está roto es redundante, y lo que funciona ya alcanza.**

**141 herramientas funcionando** en 8 conectores. **22 servidores MCP traídos por plugins: cero funcionando.**

## Lo que funciona — 141 herramientas

Conectores nativos de claude.ai, autenticados y vivos:

| Conector | Herramientas | Para qué sirve en esta obra |
|---|---|---|
| **Notion** | 43 | Base de conocimiento, páginas, bases de datos |
| **Canva** | 32 | Diseño y documentos visuales |
| **Gmail** | 29 | Correo — ⚠️ datos `PERSONAL` |
| **Google Drive** | 11 | Documentos — ⚠️ datos `PERSONAL` |
| **Google Calendar** | 9 | Agenda — ⚠️ datos `PERSONAL` |
| **AccuWeather** | 9 | Clima — relevante para trabajo de campo |
| **scheduled-tasks** | 6 | Tareas programadas (Fase 8) |
| **visualize** | 2 | Gráficos y diagramas embebidos |

Más las herramientas nativas de Claude Code (Read, Write, Edit, Glob, Grep, Bash) y las CLI deterministas (`git`, `gh`, `python`, `rg`).

## Lo que no funciona — 22 servidores, ninguno operativo

| Causa | Cuántos | Cuáles | ¿Se puede arreglar? |
|---|---|---|---|
| **Sin autenticar** | 10 | slack, notion, linear, atlassian, monday, clickup, datadog, hex, amplitude, amplitude-eu | Solo el Director, y **no hace falta** |
| **Sin URL configurada** | 6 | gmail ×2, google calendar ×2, snowflake, databricks | No: son plantillas sin configurar |
| **Sin registro dinámico de cliente** | 4 | github, asana, pagerduty, bigquery | **No desde esta máquina** |
| Endpoint inexistente | 1 | definite | No |
| Conexión cerrada | 1 | pdf | Posiblemente, pero el visor ya funciona sin él |

### El detalle importante sobre los cuatro del error de DCR

El mensaje `Incompatible auth server: does not support dynamic client registration` no es un problema del entorno del Director. Es una negociación OAuth que falla del lado del cliente, sobre una práctica —**Dynamic Client Registration (RFC 7591)**— que la propia especificación de MCP **deprecó en su versión 2026-07-28**, reemplazándola por Client ID Metadata Documents.

**Ningún cambio en esta máquina lo resuelve.** No es algo para arreglar: es algo para esperar o rodear.

### Y el detalle que cambia la decisión

Los servidores de plugin **duplican conectores que ya funcionan**:

| El plugin ofrece | Estado | Pero ya hay |
|---|---|---|
| `plugin:productivity:notion` | necesita auth | **Notion conectado, 43 herramientas** |
| `plugin:productivity:gmail` | sin URL | **Gmail conectado, 29 herramientas** |
| `plugin:productivity:google calendar` | sin URL | **Calendar conectado, 9 herramientas** |
| `plugin:engineering:github` | error de DCR | **`gh` CLI autenticada y funcionando** |

> Los 22 servidores rotos **no representan capacidad perdida**. Representan capacidad duplicada que además carga el contexto y suma superficie de ataque.

## La política

Orden de preferencia, de más barato y seguro a menos:

| # | Vía | Cuándo |
|---|---|---|
| 1 | **Nativas de Claude Code** | Siempre que alcancen |
| 2 | **CLI determinista** (`git`, `gh`, `python`, `rg`) | Resultado exacto y verificable, cero tokens de razonamiento |
| 3 | **Conectores de claude.ai ya autenticados** | Notion, Gmail, Drive, Calendar |
| 4 | **MCP remoto por HTTP con token estático** | Solo si 1–3 no cubren la necesidad |
| 5 | **MCP local en Python, versión pineada** | Último recurso |
| ❌ | **MCP vía npx / Node / Docker** | No se instala (ADR-0005) |

**Hoy no se agrega ningún servidor MCP.** Ver ADR-0007.

## Regla de clasificación de datos sobre conectores

Gmail, Drive y Calendar contienen datos `PERSONAL`. Según `AGENTS.md` §6:

- Nunca salen hacia un modelo gratuito de terceros.
- El agente que los lee **no tiene herramientas de escritura ni credenciales de salida** (separación de roles, ADR-0006).
- Enviar correo, crear eventos o compartir archivos es **acción irreversible**: requiere aprobación explícita del Director.

Y una advertencia del threat model que aplica exactamente acá: **Anthropic no audita la seguridad de los conectores del directorio**. Que estén listados no significa que sean seguros. El correo y los documentos son a la vez datos privados y **contenido no confiable escrito por terceros**: son un vector de inyección indirecta.

## Lo que quedó pendiente, y por qué no se hizo

| Candidato | Decisión | Motivo |
|---|---|---|
| MCP remoto de GitHub con PAT | **No se agrega** | `gh` ya hace lo mismo, autenticado, más barato en tokens. Ver ADR-0007 |
| `mcp-server-fetch` (pip) | **No se instala** | Sin Node cae a un extractor degradado; `WebFetch` nativo da mejor calidad. Sin caso de uso, no entra |
| `uv` | **Diferido** | Desbloquearía el catálogo MCP de Python, pero **hoy no hay ningún servidor de ese catálogo que se necesite**. Se instala cuando exista el caso, no antes |

## Cuándo revisar esto

- Si aparece una necesidad que las 141 herramientas actuales no cubren.
- Si Claude Code incorpora Client ID Metadata Documents: ahí los cuatro conectores con error de DCR podrían conectar solos.
- En la Fase 9, con datos de uso reales.
