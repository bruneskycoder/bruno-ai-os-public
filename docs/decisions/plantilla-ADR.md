# ADR-XXXX — <Decisión en una frase, en presente>

| Campo | Valor |
|---|---|
| Fecha | AAAA-MM-DD |
| Estado | PROPUESTA · ACEPTADA · REEMPLAZADA POR ADR-YYYY · REVERTIDA |
| Fase | N — Nombre |

## Decisión

Qué se decide, en dos o tres líneas. En presente y en afirmativo: "se usa X",
no "se evaluará usar X".

## Contexto

Los **hechos medidos** que obligan a decidir. Con números y fuentes cuando existan.
Si un hecho no está verificado, decirlo acá — no esconderlo.

## Opciones consideradas

1. **Opción A** — por qué se descarta, en una línea.
2. **Opción B** — por qué se descarta.
3. **Opción C** — la elegida.

Si solo hubo una opción, no era una decisión: era una consecuencia. No hace falta ADR.

## Enfoque elegido

Cuál, sin rodeos.

## Por qué

El argumento. Preferentemente atado a los principios de `ARCHITECTURE.md` o a una
restricción medida en `SYSTEM_AUDIT.md`.

## Trade-offs

- **Se gana:** …
- **Se pierde:** … *(si esta línea está vacía, la decisión no se pensó bien)*
- **Se acepta:** el costo que se asume a sabiendas.

## Consecuencias

Qué cambia de acá en adelante: en el código, en el proceso, en otras fases.
Incluir la **señal de reconsideración**: qué tendría que pasar para revisar esto.

---

<!--
Numeración correlativa, sin reutilizar números.
Un ADR no se edita para cambiar de opinión: se escribe uno nuevo que lo reemplaza,
y el viejo pasa a estado REEMPLAZADO. El historial de decisiones vale tanto como
la decisión vigente.
-->
