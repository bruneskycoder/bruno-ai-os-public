# ADR-0015 — El agente avisa qué modelo e intensidad conviene, y abre cada respuesta con un canario

| Campo | Valor |
|---|---|
| Fecha | 2026-10-26 |
| Estado | ACEPTADA — decisión del Director |
| Fase | Operación |

## Decisión

1. El agente evalúa con la escalera de costo (`AGENTS.md` §5) qué modelo y qué intensidad convienen al abrir un tramo, al cerrarlo y cuando el trabajo cambie de naturaleza, y lo **avisa en una línea**. El Director cambia el modelo.
2. Toda respuesta empieza con la palabra «Bruno» (el canario de la mina). Si no aparece, el contexto se degradó.
3. Ambas reglas viven en `AGENTS.md` y en la plantilla de `config/nuevo-proyecto.py`, para que los proyectos nuevos las hereden.

## Contexto

- El plan es Claude Pro sin uso extra y ya se saturó; la ventana semanal ronda los 8 millones de tokens (`AGENTS.md` §4).
- Ya existía el precedente de un aviso de modelo en el contrato de otro proyecto.
- Una sesión larga degrada: el agente olvida instrucciones y detalles. Hoy el Director no tiene una señal barata para notarlo a tiempo.
- **Hechos que limitan la regla:** el agente no mide con exactitud cuánto contexto lleva usado, y no puede cambiar de modelo por su cuenta. La palabra canario vive en un archivo que se vuelve a leer al empezar la sesión y al compactar, así que detecta que el agente **deja de seguir instrucciones**, no que haya perdido datos de la conversación.

## Opciones consideradas

1. **Nada: confiar en que el Director note la degradación** — descartada: la señal llega tarde y cuesta tokens.
2. **Canario de conversación** (una palabra pactada en el chat) — detectaría mejor el olvido de lo conversado, pero se pierde con cada sesión y exige repetirlo; se deja como complemento posible.
3. **Aviso de modelo y canario permanentes en el contrato** — la elegida.

## Enfoque elegido

Dos reglas cortas en `AGENTS.md` (§2 y §5) y en la plantilla de proyectos nuevos. Para que valgan también en los chats fuera de los repositorios, el Director puede pegar la misma frase en las preferencias de claude.ai.

## Por qué

Es barato (dos párrafos), reversible y alineado con «medir antes de optimizar» (§4.7). El aviso pone el costo a la vista antes de gastarlo.

## Trade-offs

- **Se gana:** una alarma visible de degradación y un recordatorio sistemático de bajar de escalón.
- **Se pierde:** una palabra y una línea de más en cada respuesta, y que el agente deba estimar el contexto sin poder medirlo.
- **Se acepta:** que el canario tenga **falsos negativos** (puede seguir diciendo «Bruno» y estar equivocado) y que no pruebe la verdad de lo dicho.

## Consecuencias

- Los proyectos creados antes con `nuevo-proyecto.py` **no heredan** las reglas; propagarlas es una decisión aparte.
- **Señal de reconsideración:** si en dos semanas el canario no se corta nunca aunque haya olvidos comprobados, pasar al canario de conversación.
