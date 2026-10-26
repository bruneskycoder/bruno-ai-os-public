# ADR-0005 — No se instala Node.js; MCP por servidores remotos con token estático

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

**No se instala Node.js.** La integración por MCP se hace preferentemente con **servidores remotos por HTTP autenticados con header estático**, y solo excepcionalmente con servidores locales en Python de versión pineada.

## Contexto

- No hay Node.js, npm ni npx en la máquina. La vía canónica del ecosistema MCP (`npx -y <paquete>`) está cerrada.
- De los 7 servidores MCP de referencia, solo **`fetch`, `git` y `time`** son Python/pip. `filesystem`, `memory`, `sequential-thinking` y `everything` son TypeScript.
- `filesystem` es redundante: Claude Code ya tiene Read/Write/Edit/Glob/Grep nativos. `memory` se resuelve con archivos (ADR-0003).
- Cuatro conectores fallan con `Incompatible auth server: does not support dynamic client registration`. **La spec MCP 2026-07-28 deprecó DCR**, reemplazándola por Client ID Metadata Documents: el problema es del cliente que la exige, y ningún cambio local lo resuelve.
- Claude Code acepta `claude mcp add --transport http <nombre> <url> --header "Authorization: Bearer <token>"`, y GitHub publica un endpoint MCP remoto que acepta PAT.
- **Hallazgo de seguridad:** el vector de supply-chain más activo de 2026 contra agentes de código es el typosquatting de npm que instala servidores MCP falsos. **No tener npm inmuniza de ese vector.**

## Opciones consideradas

1. **Instalar Node LTS** — abre el catálogo completo, a cambio de disco, mantenimiento y **la superficie de ataque más activa del ecosistema**.
2. **Solo servidores Python locales** — catálogo muy recortado; además el verdadero peaje de ese catálogo es `uv`, no Node.
3. **Servidores remotos por HTTP con token estático, y Python local como excepción.**

## Enfoque elegido

Opción 3.

## Por qué

Consigue casi todo el valor de MCP sin instalar runtime, sin gastar disco y **reduciendo** la superficie de ataque en vez de ampliarla. Además resuelve los 4 conectores rotos por una vía que no depende de que se arregle la negociación OAuth.

## Trade-offs

- **Se gana:** cero instalación, menor superficie, portabilidad, resolución inmediata de los conectores rotos.
- **Se pierde:** los servidores MCP que solo existen como paquete npm. Se acepta: ninguno de los evaluados aporta algo que no se cubra de otra forma.
- **Nuevo riesgo:** manejar tokens estáticos. Se mitiga con `keyring` sobre el Credential Manager y `gitleaks` en pre-commit; nunca tokens en archivos versionados.

## Consecuencias

- `gh` CLI es la vía preferente para GitHub: ya está autenticada y es más barata en tokens que un MCP.
- Todo servidor MCP local en Python se instala con **versión exacta pineada** y se lanza como `python -m <módulo>`, con `PYTHONIOENCODING=utf-8`.
- Si alguna vez se levanta un servidor HTTP local: bindear a `127.0.0.1` y validar el header `Origin`.
- **`uv` queda como decisión abierta de Fase 5**: binario estático, sin admin, desbloquea el catálogo MCP de Python. Es la instalación de mayor palanca de la auditoría, pero requiere un caso de uso concreto antes de entrar.
- Esta decisión se revisa si aparece un servidor MCP solo-Node con valor que nada más cubra.
