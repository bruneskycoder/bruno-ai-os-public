# ADR-0008 — Gemini como válvula de escape, preparado pero no instalado

| Campo | Valor |
|---|---|
| Fecha | 2026-09-15 |
| Estado | ACEPTADA |
| Fase | 7 — Multi-modelo |

## Decisión

Se **prepara** la integración de Gemini como segundo cerebro para trabajo con datos no personales, pero **no se instala todavía**. El procedimiento queda listo en `config/segundo-cerebro.py` y se ejecuta cuando exista una clave de API y un caso de uso concreto.

## Contexto

**El problema real que esto resolvería** no es "tener más modelos". Es uno solo, y es el problema número uno del Director: **cuando Claude Pro se satura, la semana se frena.** Ya pasó tres veces durante esta misma obra. Un segundo cerebro para trabajo de lectura pública sería una válvula de escape.

Hechos verificados que acotan la solución:

- **Gemini CLI quedó fuera**: exige Node.js 20+ y no hay binario, winget, scoop ni choco. El 18/06/2026 además dejó de servir a cuentas individuales.
- **Vía viable sin Node**: `llm` (Python puro) con el plugin `llm-gemini`. Verificado por resolución de dependencias: **llm 0.35 + llm-gemini 0.34, 34 paquetes, todos wheels precompilados, cero código a compilar.** No hace falta compilador de C en Windows.
- **Alternativa**: Antigravity CLI (`agy`), binario Go, se instala con `irm | iex` — un patrón de descarga-y-ejecución que esta obra no usa a ciegas.
- **Restricción dura e innegociable**: los términos del tier gratuito de la API de Gemini dicen que Google usa los prompts y las respuestas para mejorar sus productos, que revisores humanos pueden leerlos, y que no hay que enviar información sensible, confidencial ni personal.

## Opciones consideradas

1. **Instalar ahora y probar después** — 34 paquetes que no se pueden ejercitar sin clave. Viola la Puerta 0 del propio checklist de admisión: sin necesidad concreta demostrada, no entra.
2. **Descartar el multi-modelo** — deja al Director sin ninguna salida cuando el plan se agota, que es su restricción dominante.
3. **Preparar el procedimiento completo y condicionar la instalación** a que haya clave y caso de uso.

## Enfoque elegido

Opción 3.

## Por qué

Instalar 34 dependencias que no se pueden probar sería exactamente el tipo de decisión que este proyecto viene evitando desde la Fase 0. Pero descartar la integración también sería un error: el problema que resuelve es real y está medido.

Preparar cuesta cero y convierte una decisión futura en **un solo comando**, en vez de una investigación desde cero.

## Trade-offs

- **Se gana:** cero disco, cero dependencias, cero superficie de ataque hoy. La decisión queda tomada y documentada.
- **Se pierde:** no hay válvula de escape operativa **todavía**. Si el plan se satura mañana, no hay plan B automático.
- **Se acepta:** la verificación de que esto funciona de punta a punta queda pendiente, y se declara como tal.

## La regla de datos, que no es negociable

| Clase | ¿Puede ir a Gemini gratuito? |
|---|---|
| 🔴 `PERSONAL` — finanzas, legales, correo, salud, campo, credenciales, identidades | **NUNCA** |
| 🟡 `INTERNO` — notas, borradores, código propio | Solo anonimizado y con decisión explícita del Director |
| 🟢 `PÚBLICO` — documentación pública, artículos, open source | Sí |

**Sin clasificación declarada, se asume `PERSONAL`** y no sale de Claude.

Esto no es una guía de estilo: es la consecuencia directa de los términos de uso. Y la decisión de clasificación **la toma el orquestador con el Director mirando**, no un agente por su cuenta.

## Cómo se activa, cuando se decida

1. El Director genera una clave gratuita en Google AI Studio *(no me la pega en el chat: la guarda él)*.
2. `python config/segundo-cerebro.py --instalar`
3. `python config/segundo-cerebro.py --guardar-clave` — la pide sin mostrarla y la deja en el **Credential Manager de Windows**, nunca en un archivo.
4. `python config/segundo-cerebro.py --probar` — verifica de punta a punta con un prompt público.

## La prueba de aceptación

La Fase 7 **no se da por buena porque la instalación funcione.** Se da por buena si una tarea concreta muestra **ventaja medible** frente a hacerla solo con Claude:

- Una tarea de lectura pública, medida con `config/consumo.py --marcar` antes y `--diferencia` después.
- Comparación explícita: ¿ahorró consumo del plan? ¿el resultado fue igual de bueno?

> **Si no muestra ventaja, no se integra.** Y eso es un resultado válido, no un fracaso: es la respuesta a la pregunta del mandato §26 sobre si más modelos es mejor.

## Consecuencias

- `config/segundo-cerebro.py` queda en el repositorio, listo y sin ejecutar.
- La regla de clasificación de datos ya está activa en `AGENTS.md` §6 y `MODEL_ROUTING.md`.
- OpenAI queda fuera por ahora: Codex exige plan pago y lo único gratuito con valor —`AGENTS.md`— ya se adoptó en ADR-0004.

## Actualización — 2026-09-15: activado

La condición se cumplió (el Director generó la clave), así que se instaló y se verificó de punta a punta. **Responde.** Sigue pendiente lo que de verdad decide su permanencia: **demostrar ventaja medible en una tarea real**.

Tres cosas que salieron mal en el camino y quedaron documentadas:

1. **`Ctrl+V` en un campo oculto de la consola de Windows guarda caracteres de control** (`\x16`, `\x1a`) en lugar de pegar. La clave quedaba rota con basura invisible y Google devolvía un HTML 400 que no decía nada. Se corrigió filtrando todo lo no imprimible al guardar y al leer, y avisando que se pegue con clic derecho.
2. **Un script de diagnóstico propio filtró la clave**: redactaba en la rama de `HTTPError` pero no en la de excepción genérica. Hubo que rotar la clave. La redacción ahora va en el punto de impresión, no por rama.
3. **`gemini-2.5-flash` ya no está disponible para cuentas nuevas.** Lo dijo el propio error de Google, no la documentación. Se cambió a `gemini-3.6-flash`. Confirma el patrón detectado en la Fase 0: la documentación de Google sobre Gemini envejece mal y hay que verificar contra el comportamiento real.

### Señal de reconsideración

Se instala cuando ocurra **cualquiera** de estas:

1. El Director consigue la clave y quiere probar.
2. El plan se satura en medio de un trabajo que sea de datos `PÚBLICO`.
3. Aparece una tarea de lectura ancha y pública donde el ahorro sea previsible.
