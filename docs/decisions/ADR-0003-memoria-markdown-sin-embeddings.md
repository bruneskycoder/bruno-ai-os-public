# ADR-0003 — Memoria en markdown + git + ripgrep, sin embeddings

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

La memoria y el conocimiento persistente se implementan con **archivos markdown versionados en git, buscados con ripgrep**. Cero embeddings, cero base vectorial, cero sistema de memoria de terceros.

## Contexto

- El umbral medido a partir del cual RAG empieza a pagar es **~1.500–2.000 documentos markdown (30–50 MB de prosa)**. Una base personal realista arranca en decenas o pocos cientos: dos órdenes de magnitud por debajo.
- La evidencia de *context rot* (18 modelos, 4 familias) muestra que **los distractores degradan más que la ausencia de documentos**: un recuperador semántico que devuelve 5 documentos "parecidos" puede rendir peor que un `ripgrep` que devuelve 1 exacto.
- La posición oficial de Anthropic sobre context engineering es *just-in-time*: identificadores livianos (rutas de archivo) y carga bajo demanda, en vez de precarga.
- Claude Code ya implementa una taxonomía de memoria en archivos markdown con frontmatter (`user`, `feedback`, `project`, `reference`) e índice `MEMORY.md`.

## Opciones consideradas

1. **mem0** — requiere un LLM externo de pago que el Director no tiene.
2. **letta / MemGPT** — migró su distribución a npm; sin Node queda fuera.
3. **zep / cognee** — servidores con base de datos: disco, mantenimiento y un servicio corriendo.
4. **Markdown + git + ripgrep** — cero dependencias nuevas.

## Enfoque elegido

Opción 4.

## Por qué

Gana sin empate técnico a esta escala, y además es lo único legible por el Director, versionable, portable y buscable sin infraestructura. El historial de git aporta memoria episódica gratis.

## Trade-offs

- **Se gana:** cero costo, cero mantenimiento, portabilidad total, auditabilidad.
- **Se pierde:** búsqueda semántica. Una consulta conceptual que no comparte vocabulario con el texto puede no encontrarse.
- **Mitigación:** nombres de archivo descriptivos, índice curado y enlaces `[[wiki]]` entre archivos.

## Consecuencias

- Tres almacenes con oficios distintos: auto memory (hechos entre sesiones), `memory/` del repo (estado y decisiones), `artifacts/` (resultados).
- El índice `MEMORY.md` tiene techo duro: **200 líneas o 25 KB**. Eso define la escala del índice plano.
- **Señal de reconsideración**, registrada en `ARCHITECTURE_EVOLUTION.md`: cuando se cumplan las dos condiciones a la vez — más de 1.500 archivos en `memory/` + `artifacts/`, y búsquedas que fallan de forma reiterada por ser conceptuales y no léxicas.
