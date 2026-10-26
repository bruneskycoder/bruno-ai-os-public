# ADR-0018 — La investigación ancha y las imágenes las ejecuta el Director, con prompt y pasos listos

| Campo | Valor |
|---|---|
| Fecha | 2026-10-26 |
| Estado | ACEPTADA — decisión del Director. Extiende el ADR-0012 |
| Fase | Operación |

## Decisión

Para temas `PÚBLICO`, la **investigación ancha** y la **creación de imágenes** las ejecuta el Director en Deep Research de ChatGPT o de Gemini, o en un chat gratis. El agente entrega siempre el prompt listo, dónde pegarlo, pasos numerados y sencillos (seis como máximo) y qué traer de vuelta y en qué formato.

## Contexto

- El plan es Claude Pro sin uso extra y ya se saturó; la investigación fue el único gasto grande medido (un fan-out sin tope costó cerca de 14 % del semanal).
- El ADR-0012 ya delegaba la **recolección** a Deep Research. Faltaban las imágenes, los chats gratis y un formato fijo de entrega.
- La clasificación de datos (`AGENTS.md` §6) impide mandar `PERSONAL` a tiers gratuitos, cuyos términos permiten usar los prompts para mejorar sus productos.
- El método solo ahorra si el Director condensa antes de traer el resultado (ADR-0012).

## Opciones consideradas

1. **Seguir con el agente investigando y generando** — descartada: gasta el cupo escaso en lo que se puede hacer gratis afuera.
2. **Delegar sin formato** — descartada: sin prompt y pasos claros, la tarea vuelve mal hecha o cuesta más tokens corregirla.
3. **Delegar con entrega estandarizada** — la elegida.

## Enfoque elegido

Regla en `AGENTS.md` §5, entrega estandarizada en `artifacts/delegar-investigacion.md` §10, extensión del contrato de imágenes en `arrancar-proyecto` y mención en la plantilla de proyectos nuevos.

## Por qué

Mueve el gasto más grande a herramientas gratuitas, sin tocar lo que debe quedarse en Claude: la verificación y las decisiones.

## Trade-offs

- **Se gana:** tokens de Claude y una investigación más ancha de lo que el cupo permitiría.
- **Se pierde:** pasos manuales del Director (pegar, esperar, condensar, traer) y menos control sobre cómo se hizo la investigación.
- **Se acepta:** que lo que vuelve es contenido externo y puede estar mal o traer instrucciones; por eso es dato, no orden, y se verifica lo que gobierna decisiones. Los menús de esas herramientas cambian, así que los pasos pueden quedar desactualizados.

## Consecuencias

- Los proyectos creados antes no heredan la regla.
- **Señal de reconsideración:** si el Director declara que los pasos son demasiado engorrosos o si el condensado no se hace y los informes crudos vuelven a pegarse, revisar el formato.
