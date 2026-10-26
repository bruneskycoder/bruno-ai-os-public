# ADR-0013 — El relevo automático se apaga; el código se conserva

| Campo | Valor |
|---|---|
| Fecha | 2026-10-17 |
| Estado | ACEPTADA — decisión del Director |
| Fase | Operación |

## Decisión

La tarea programada `relevo-bruno-ai-os` queda **desactivada**. El código (`config/relevo.py`, `tests/probar-relevo.py`) se versiona y se conserva, con dos correcciones: lee el testigo único de `memory/HANDOFF.md`, y su tope semanal por defecto baja de **90 %** a **40 %**.

## Contexto

El 2026-09-17, a pedido del Director, una sesión construyó un **relevo**: una tarea que despierta cinco veces por día y, si hay presupuesto, retoma el trabajo declarado en el testigo. El portero que decide si arrancar es determinista y cuesta cero tokens — buena idea, bien ejecutada, con once pruebas de las cuales cinco son negativas.

Un mes después, el 2026-10-17, la revisión encontró:

### El relevo nunca funcionó

| Evidencia | Valor |
|---|---|
| Estado de la tarea | Activa, disparando a las 02:55, 07:55, 12:55, 17:55 y 22:55 |
| Último disparo | 2026-10-17, minutos antes de la revisión |
| Ejecuciones registradas | **0** |
| `logs/relevo.csv` | **No existe.** Es lo primero que escribe cada despertar |
| Código | **Sin commitear** durante un mes |

El primer punto pendiente que la sesión dejó en el testigo era *"commitear el sistema de relevo"*. Lo esperaba hacer el propio relevo, que nunca arrancó.

La causa exacta no se determinó. La hipótesis más probable es que la tarea exige la app abierta en el horario de disparo. **No se investigó más porque la decisión no depende de eso.**

### Y si funcionara, competiría con el Director

| Parámetro | Valor |
|---|---|
| Tope semanal original | **90 %** — arrancaría hasta dejarle al Director el 10 % de su semana |
| Gasto por relevo | Hasta 45 % de una ventana de 5 h ≈ **6–8 % del semanal** (`COST_MODEL.md`) |
| Relevos por día | ~4, con el enfriamiento de 4 horas |
| **Consumo posible por día** | **≈ 25–30 % del semanal**, sin intervención humana |

> El relevo optimiza **la restricción equivocada**. Evita desperdiciar reinicios de la ventana de 5 horas — pero lo que deja al Director sin Claude es la ventana **semanal**: llegó al 97 % el 2026-09-13 y al 67 % en el día 3 el 2026-09-16. Cada ventana de 5 h que el relevo usa de noche es presupuesto que le saca de día.

Dispararía, solo, la señal de alarma de `AGENTS.md` §4.

### Y sería una sesión desatendida con permisos completos

Con `bypassPermissions` activo, cada despertar es una sesión que **commitea y empuja a GitHub sin nadie mirando**, cinco veces por día. Es exactamente el vector V6 del threat model. Y contradice `AGENTS.md` §10, que dice que la única tarea desatendida es el respaldo semanal: el relevo nunca se registró ahí.

## Opciones consideradas

1. **Apagar y conservar el código.**
2. **Arreglarla con techos seguros** — reduce el riesgo económico, no el de seguridad; y su valor es bajo con el plan actual.
3. **Dejarla como está** — inactiva en la práctica, pero con un tope de 90 % esperando el día que arranque.

## Enfoque elegido

Opción 1, decidida por el Director.

## Por qué

No se pierde nada —nunca funcionó—, se elimina un riesgo latente de presupuesto y de seguridad, y el código queda listo para el escenario donde sí tiene sentido.

## Trade-offs

- **Se gana:** cero riesgo de que una sesión automática consuma la semana o empuje sin supervisión.
- **Se pierde:** nada medible: no hubo una sola ejecución que perder.
- **Se acepta:** si el Director quiere retomar trabajo mientras duerme, no hay forma automática de hacerlo con el plan actual.

## Consecuencias

1. La tarea queda en la lista de la app, desactivada, con una descripción que remite a este ADR.
2. **Un solo testigo:** el relevo lee `memory/HANDOFF.md`. El `HANDOFF.md` de la raíz —que la sesión creó sin ver el existente— se eliminó; nunca estuvo versionado.
3. El tope semanal por defecto bajó a **40 %**: si alguien reactiva la tarea sin leer esto, al menos deja la mayor parte de la semana libre.
4. El libro de obra conserva la entrada original con una **corrección agregada**, no editada: lo que se afirmó y lo que era cierto quedan los dos.

### Para reactivarlo, deben cumplirse las cuatro

1. **Plan Max** o equivalente: con la semana 5× más grande, un relevo nocturno deja de competir con el Director.
2. **Diagnosticar por qué nunca se ejecutó**, y verificar una ejecución real: `logs/relevo.csv` tiene que existir.
3. `memory/HANDOFF.md` debe tener la sección *Próximo paso* en el formato que el portero lee (hoy no la reconoce).
4. Registrarlo en `AGENTS.md` §10 como **segunda tarea desatendida**, con sus límites escritos.
