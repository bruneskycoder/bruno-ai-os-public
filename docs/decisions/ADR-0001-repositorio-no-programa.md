# ADR-0001 — Bruno AI OS es un repositorio estructurado, no un programa

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

Bruno AI OS se implementa como un **repositorio de archivos versionado** que aprovecha el harness nativo de Claude Code, y **no** como software propio con router y orquestador.

## Contexto

El mandato (§6) propone una arquitectura con TASK ROUTER, ORCHESTRATOR y capas de agentes sobre Claude / Gemini / OpenAI. Es la arquitectura correcta para quien paga APIs por token. La auditoría mostró que el Director no está en ese caso:

- Claude Pro es una suscripción, no una API key. El Agent SDK exige `ANTHROPIC_API_KEY` de pago, y Anthropic prohíbe explícitamente usar el login de claude.ai para agentes construidos sobre él.
- Claude Code ya provee subagentes con contexto aislado, skills con carga progresiva, hooks, permisos, memoria automática y atribución de consumo por componente.
- No hay Node.js, ni Docker, ni WSL, ni presupuesto de tokens holgado.

## Opciones consideradas

1. **Construir el router/orquestador propuesto en el mandato** — requiere API keys de pago que no existen; duplica funcionalidad ya paga.
2. **Adoptar un framework multi-agente** (crewAI, langgraph, LiteLLM) — todos asumen API keys facturadas por agente y árboles de dependencias grandes.
3. **Repositorio estructurado sobre el harness nativo** — cero runtime propio.

## Enfoque elegido

Opción 3.

## Por qué

Cumple simultáneamente los ocho principios de arquitectura del mandato (§3), y es la única compatible con las tres restricciones duras medidas: sin API key de pago, sin Node, con presupuesto saturado. La regla "NO OVERENGINEERING" no admite construir un orquestador cuando ya hay uno pago y funcionando.

## Trade-offs

- **Se gana:** cero mantenimiento de infraestructura, portabilidad del contenido, legibilidad para el Director, costo cercano a cero.
- **Se pierde:** control fino sobre el ruteo (queda como tabla de decisión, no como código) y dependencia del harness de Claude Code para la ejecución.
- **Mitigación de la dependencia:** el contenido está en formatos abiertos. Si Claude desapareciera, el repositorio sigue siendo un cuerpo de conocimiento usable por otro agente.

## Consecuencias

- El "router" se implementa como tabla de ruteo + configuración de modelos y effort, no como programa.
- Se descarta la categoría completa de routers de modelos y frameworks multi-agente.
- La Fase 6 pasa a ser configuración y subagentes, no desarrollo.
