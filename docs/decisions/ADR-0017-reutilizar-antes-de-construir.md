# ADR-0017 — Antes de construir algo nuevo se busca en internet lo que otros ya hicieron, con tope

| Campo | Valor |
|---|---|
| Fecha | 2026-10-26 |
| Estado | ACEPTADA — decisión del Director |
| Fase | Operación |

## Decisión

Al empezar algo nuevo, y al topar con un problema que otros probablemente resolvieron, se investiga en internet qué repositorios, librerías o datos abiertos existen y se toma lo valioso. Con un tope declarado antes (6 búsquedas y 5 repositorios leídos) y un informe corto. La regla vive en `AGENTS.md` §3 y en la plantilla de proyectos nuevos; el método, en `investigacion-con-artefacto/references/`.

## Contexto

Hechos verificados:

- En el atlas de Nueva Zelanda se evaluaron repositorios ajenos y se adoptaron tres: el chequeo de maquetación de `construir.mjs` está adaptado de EpicInfographics (MIT; consta en el encabezado del archivo y en el README del atlas), `geo-nz.py` usa Mapshaper y los mapas usan datos de Natural Earth.
- Ya existían piezas sueltas: la pregunta «¿ya existe algo parecido?» de `arrancar-proyecto` y el inventario de reutilización de `plan-before-build`. Faltaba hacerlo sistemático.
- Costo medido en esta cuenta (`COST_MODEL.md`): una búsqueda propia de 3 a 6 recuperaciones cuesta cerca de 0 % del semanal; un fan-out sin tope, cerca de 14 %.
- La guía de Claude Code (§2) recomienda el mismo flujo: seleccionar, inspeccionar sin modificar, informar con fuentes, integrar de forma selectiva y verificar.

**No medido:** que buscar mejore el resultado frente a no buscar. Que ayudó en el atlas es un caso, no una estadística.

## Opciones consideradas

1. **Dejarlo a criterio de cada sesión (lo de hoy)** — descartada: depende de que alguien se acuerde.
2. **Buscar siempre y sin tope** — descartada: es el patrón que agotó la ventana de 5 horas.
3. **Delegar siempre la búsqueda a Gemini o ChatGPT** — descartada como regla general: no sirve para trabajo `PERSONAL` y agrega pasos; queda como opción para temas anchos (`arrancar-proyecto`).
4. **Regla permanente con tope e informe** — la elegida.

## Enfoque elegido

Regla corta en el contrato, método en una referencia que se carga solo cuando hace falta (sin impuesto fijo de contexto) y tope explícito.

## Por qué

Reutilizar sale más barato que construir (`arrancar-proyecto`) y el costo medido de una búsqueda acotada es despreciable. El tope evita repetir el error del fan-out sin tope.

## Trade-offs

- **Se gana:** menos reinvención, mejores herramientas de partida y un registro de qué se evaluó y por qué se descartó.
- **Se pierde:** unos minutos y unas recuperaciones al inicio de cada trabajo nuevo.
- **Se acepta:** riesgo de contenido externo no confiable y de licencias incompatibles; por eso se lee sin ejecutar, se trata como dato y se verifica antes de copiar o instalar.

## Consecuencias

- Los proyectos creados antes no heredan la regla.
- **Señal de reconsideración:** si en cinco usos la búsqueda no cambia ninguna decisión, limitarla a proyectos nuevos; si el costo medio supera el 2 % del semanal, bajar el tope.
