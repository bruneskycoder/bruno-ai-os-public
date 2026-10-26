# ADR-0007 — No se agrega ningún servidor MCP; `gh` reemplaza al conector de GitHub

| Campo | Valor |
|---|---|
| Fecha | 2026-09-15 |
| Estado | ACEPTADA |
| Fase | 5 — Herramientas |

## Decisión

No se agrega ningún servidor MCP nuevo: ni el endpoint remoto de GitHub, ni `mcp-server-fetch`, ni `uv` para desbloquear el catálogo de Python. El acceso a GitHub se hace con la CLI `gh`, que ya está autenticada.

## Contexto

La Fase 5 se planeó para reemplazar los conectores rotos. La medición del 2026-09-15 mostró que el problema estaba mal planteado:

- **141 herramientas ya funcionan** en 8 conectores autenticados (Notion 43, Canva 32, Gmail 29, Drive 11, Calendar 9, AccuWeather 9, scheduled-tasks 6, visualize 2).
- **22 servidores MCP traídos por plugins: cero funcionando.** 10 sin autenticar, 6 sin URL configurada, 4 con error de registro dinámico de cliente, 2 con endpoint muerto.
- **Los rotos duplican lo que ya funciona**: el plugin de Notion pide autenticación mientras el conector de Notion ya da 43 herramientas; los de Gmail y Calendar no tienen URL mientras los conectores andan.
- El error `does not support dynamic client registration` viene de una práctica que la **spec MCP 2026-07-28 deprecó**. No se arregla desde esta máquina.
- `gh` está autenticada como `bruneskycoder` con scopes `gist`, `read:org`, `repo`, `workflow`.

## Opciones consideradas

1. **Agregar el MCP remoto de GitHub con un PAT por header** — funciona, pero duplica lo que `gh` ya hace, exige manejar un token estático más y agrega superficie de ataque.
2. **Instalar `uv` y traer servidores MCP de Python** — desbloquearía el catálogo, pero **hoy no hay ningún servidor de ese catálogo que se necesite**. Instalar por si acaso es exactamente lo que el mandato prohíbe.
3. **Instalar `mcp-server-fetch`** — sin Node cae a un extractor degradado; `WebFetch` nativo da mejor calidad.
4. **No agregar nada y documentar por qué.**

## Enfoque elegido

Opción 4.

## Por qué

`VALUE > COMPLEXITY + COST + RISK` no se cumple para ninguno de los candidatos. Ninguno aporta una capacidad que las 141 herramientas actuales no cubran, y los tres suman mantenimiento, superficie de ataque o ambos.

`gh` además es **más barato en tokens** que un servidor MCP: un comando devuelve exactamente lo pedido, mientras que un servidor MCP carga descripciones de herramientas en el contexto de cada sesión.

## Trade-offs

- **Se gana:** cero instalación, cero tokens nuevos, cero superficie de ataque, cero mantenimiento.
- **Se pierde:** las llamadas a GitHub pasan por shell en vez de por herramientas tipadas. Para un Director que no escribe comandos, es indistinto: en los dos casos el agente traduce su pedido.
- **Se acepta:** si algún día hace falta un servidor MCP de Python, habrá que instalar `uv` en ese momento. Postergar tiene un costo bajo y un beneficio cierto.

## Consecuencias

- La política de herramientas de `docs/MCP_ARCHITECTURE.md` queda como orden de preferencia vigente.
- **Se refuerza la recomendación B9:** los plugins `bio-research` y `finance` aportan 1.339 tokens fijos y 17 servidores MCP declarados, todos inútiles. A la luz de esta medición, `data`, `productivity` y `engineering` también traen servidores rotos o redundantes.
- Todo componente nuevo pasa por `docs/security/ADMISION-DE-COMPONENTES.md` antes de entrar.

### Señal de reconsideración

Se revisa esta decisión si ocurre **cualquiera** de estas tres:

1. Aparece una necesidad concreta que las 141 herramientas actuales no cubren.
2. Claude Code incorpora Client ID Metadata Documents y los conectores con error de DCR conectan solos.
3. La Fase 9 muestra, con datos de uso, que alguna integración faltante habría ahorrado trabajo real.
