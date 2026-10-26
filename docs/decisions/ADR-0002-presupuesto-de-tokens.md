# ADR-0002 — El presupuesto de tokens es restricción de primer orden

| Campo | Valor |
|---|---|
| Fecha | 2026-09-14 |
| Estado | PROPUESTA — pendiente de autorización del Director |
| Fase | 0 — Replanteo |

## Decisión

La economía de contexto deja de ser una preocupación transversal y pasa a ser un **eje de diseño con protocolo obligatorio y medición temprana**. La fase de medición se adelanta del puesto 9 al puesto 2.

## Contexto

- Plan **Claude Pro** con usage credits **deshabilitados a nivel organización**: no se puede comprar uso adicional.
- Telemetría local: la ventana larga llegó a **96–97 %** el 2026-09-13 antes de resetear.
- Durante esta misma Fase 0, un fan-out de 15 agentes **agotó la ventana de 5 horas**: 4 terminaron, 11 murieron. Consumo medido: 1.115.458 tokens de subagente en 11 minutos.
- Los modelos 4.7+ usan un tokenizador que produce **~30 % más tokens** para el mismo texto.
- Un sistema multiagente cuesta **~15x** un agente único; los agent teams declaran ~7x.
- El TTL del cache en suscripción es de **1 hora**: turnos separados por menos de una hora reutilizan el prefijo a 0.1x.

## Opciones consideradas

1. **Tratar el presupuesto como preocupación transversal** y evaluar recién en la fase 9, como indica el mandato.
2. **Adelantar la medición a la fase 2** y fijar un protocolo de sesión obligatorio.
3. **Recomendar subir a Max 5x** — traslada el problema en vez de resolverlo, y es gasto del Director.

## Enfoque elegido

Opción 2. La opción 3 queda registrada como camino disponible si el Director lo decide, no como recomendación.

## Por qué

Es la única restricción que ya se materializó dos veces de forma medible. Y la instrumentación es casi gratuita: la status line recibe `rate_limits.five_hour` y `rate_limits.seven_day`, y `/usage` atribuye consumo por skill, subagente, plugin y servidor MCP. No hay que construir telemetría: hay que conectarla.

## Trade-offs

- **Se gana:** decisiones posteriores basadas en números; detección temprana de componentes caros.
- **Se pierde:** la fase 2 no produce capacidad visible para el Director, solo instrumentos.
- **Se acepta:** el protocolo de sesión (ráfagas menores a una hora, `/clear` + `HANDOFF.md`) impone disciplina de trabajo.

## Consecuencias

- Protocolo de sesión obligatorio documentado en `ARCHITECTURE.md` §6.
- Regla de multiagente: fan-out solo para investigación de lectura breadth-first con ramas independientes.
- Todo fan-out declara su costo estimado antes de ejecutarse.
- Configuración objetivo: Sonnet 5 de sesión, Haiku 4.5 para subagentes, fast mode y Fable excluidos por requerir usage credits.
