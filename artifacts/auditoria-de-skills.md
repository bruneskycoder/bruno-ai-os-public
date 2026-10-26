# Auditoría de capacidad instalada

| Campo | Valor |
|---|---|
| Propósito | Saber qué cuesta, en contexto y en superficie de ataque, la capacidad ya instalada — antes de agregar más |
| Fecha | 2026-09-15 |
| Versión | 1.0 |
| Clasificación | INTERNO |
| Fuentes | `claude plugin details --plugin-dir` (herramienta oficial) sobre los 7 plugins instalados · archivos `SKILL.md` en el directorio de datos de la app |
| Estado | **VERIFIED** para los plugins (números de la herramienta oficial) · `PARTIALLY VERIFIED` para las skills de cuenta (estimación propia) |
| Relaciones | `COST_MODEL.md` · `.claude/rules/escritura-de-skills.md` · `docs/security/THREAT_MODEL.md` |

---

## Qué dice

El Director tiene **56 skills disponibles** en cada sesión. Dos plugins —`bio-research` y `finance`— aportan **1.339 tokens fijos de contexto y 17 servidores MCP declarados**, para capacidades que no tienen ninguna relación con su vida ni con este proyecto.

Las tres skills creadas para Bruno AI OS cuestan **378 tokens**. El intercambio está a favor: **se puede sacar 3,5 veces más de lo que se agrega.**

## Costo por plugin — números oficiales

| Plugin | Siempre en contexto | Skills | MCP declarados | Relevancia para el Director |
|---|---|---|---|---|
| `data` | 868 tok | 10 | 8 | Baja — son skills de data warehouse; no tiene uno |
| `bio-research` | **756 tok** | 6 | **11** | **Nula** — genómica, Nextflow, single-cell RNA |
| `engineering` | 695 tok | 10 | 10 | Media — algunas aplican a este proyecto |
| `finance` | **583 tok** | 8 | **6** | **Nula** — SOX, asientos contables, cierre corporativo |
| `productivity` | 270 tok | 4 | 9 | Media — se solapa con `memory/` del repositorio |
| `cowork-plugin-management` | 179 tok | 2 | 0 | Potencial — si Bruno AI OS se empaqueta como plugin |
| `pdf-viewer` | 146 tok | 5 | 1 | Alta — tiene documentos legales y resúmenes en PDF |
| **Total plugins** | **3.497 tok** | 45 | 45 | |
| Skills de la cuenta claude.ai | ~1.784 tok *(est.)* | 15 | — | Alta — incluye las tres propias del Director |
| **TOTAL** | **≈ 5.280 tok** | 60 | | |

## Cómo leer estos números, sin exagerarlos

El costo en dinero de esos 5.280 tokens es **bajo**: viven en el prefijo estable del prompt, así que el caché los sirve a 0,1x después de la primera lectura de cada sesión.

**El costo real es otro, y es peor: dilución del disparo.**

Las skills se eligen únicamente por su descripción. Cuantas más descripciones parecidas compiten, peor es la selección — y la evidencia de *context rot* muestra que **los documentos casi-relevantes degradan más que la ausencia de documentos**. Tener ocho skills de contabilidad corporativa disponibles no es neutral: compiten por el disparo con las que sí sirven.

Y hay un costo de seguridad: los plugins irrelevantes **declaran 17 servidores MCP** que, según el threat model, son superficie de ataque (tool poisoning, rug pull) sin ningún beneficio compensatorio.

## Recomendación

**Desinstalar `bio-research` y `finance`.** Es decisión del Director —es su cuenta— y es reversible en cualquier momento.

- Recupera 1.339 tokens fijos por sesión.
- Saca 17 servidores MCP de la superficie de ataque.
- Mejora el disparo de las skills que sí sirven.
- No pierde nada: 0 usos registrados desde que se instalaron.

**`data` y `productivity` quedan a revisión**, no a descarte: `data` tiene dos o tres skills de visualización que podrían servir, y `productivity` se solapa con el archivo de obra que ya se construyó. Decisión para la Fase 9, con datos de uso reales.

## Las tres skills nuevas

| Skill | Descripción | Costo | Reutilización demostrada |
|---|---|---|---|
| `checkpoint-de-fase` | Cierra una fase con evidencia y arma el reporte | 122 tok | **4 veces** en este proyecto |
| `investigacion-con-artefacto` | Investiga con presupuesto acotado y deja artefacto | 136 tok | **2 veces**, con la lección de costo incorporada |
| `explicar-concepto` | Explica con analogías de obra y Mermaid | 120 tok | Requisito permanente del mandato (§15, §32) |

Se descartaron deliberadamente las demás del catálogo del mandato (§12): **no hay evidencia de reutilización todavía**. Cada skill es un impuesto fijo sobre cada sesión; se agregan cuando un trabajo se repite, no por anticipado.

## Lo que no se pudo verificar

- **Que las tres skills disparen bien.** El harness oficial `claude plugin eval` existe y está documentado, pero necesita un CLI autenticado: el binario embebido en la app responde `Not logged in` en modo headless. Medir el disparo requiere instalar el CLI (`winget install Anthropic.ClaudeCode`) y que el Director haga login una vez.
- **Que las skills del repositorio se carguen.** Viven en `.claude/skills/`, que es la ruta documentada de proyecto. La herramienta oficial reporta `Skills (0)` al cargar el repositorio **como plugin**, porque un plugin las busca en `<plugin>/skills/` — eso es esperable y no indica un problema, pero deja la carga sin confirmar hasta verla en una sesión nueva.
- **El costo de las skills de cuenta** es estimación propia (3,3 caracteres por token). Contrastada contra la herramienta oficial en los plugins, la estimación quedó **13 % alta**.

## Cómo se usa

```
python config/auditar-skills.py --detalle     estimación rápida, local
claude --plugin-dir <ruta> plugin details <n> números oficiales de un plugin
```

Repetir esta auditoría antes de instalar cualquier plugin nuevo, y en la Fase 9 con datos de uso reales.
