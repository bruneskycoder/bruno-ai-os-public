# COST_MODEL.md — Qué cuesta cada cosa

| Campo | Valor |
|---|---|
| Propósito | Línea base numérica del consumo del plan, medida en esta cuenta |
| Fecha | 2026-09-14 |
| Versión | 1.0 |
| Clasificación | INTERNO |
| Fuentes | `%APPDATA%\Claude\plan-usage-history.json` · contadores de los workflows de Fase 0 |
| Estado | **PARTIALLY VERIFIED** — una sola observación limpia. Ver §5 |
| Relaciones | ADR-0002 · `ARCHITECTURE.md` §6 · `logs/consumo.csv` |

---

## 1. Por qué este documento existe

Anthropic **no publica** cuántos mensajes, horas ni tokens entran en el plan Pro. Las cifras que circulan por foros son de julio de 2025 y describen modelos que ya no existen.

Así que no hay nada que investigar: **hay que medir.** Y se puede, porque la app ya guarda telemetría de consumo en disco.

## 2. Qué se mide

La app escribe muestras periódicas con dos porcentajes:

| Campo | Qué es |
|---|---|
| `fh` | % consumido de la **ventana rodante de 5 horas** |
| `sd` | % consumido de la **ventana larga (semanal)**, que resetea a hora fija de la cuenta |

Se leen con `python config/consumo.py`.

## 3. La observación

El 2026-09-14 la ventana semanal reseteó a las 13:22 ART, dejando la cuenta en cero. Sobre esa pizarra limpia se lanzó la primera tanda de investigación de Fase 0.

| Hora (ART) | 5 horas | Semanal | Qué estaba pasando |
|---|---|---|---|
| 13:22 | 0 % | 0 % | Semana reseteada |
| 13:37 | **80 %** | **10 %** | Tanda A a mitad de vuelo |
| 13:52 | **100 %** | **14 %** | Límite agotado; mueren 11 de 15 agentes |
| 16:22 | 100 % | 14 % | Ventana de 5 h todavía bloqueada |

**Trabajo realizado en esos 30 minutos:** la sesión principal (auditoría del entorno, ~40 comandos, redacción de `SYSTEM_AUDIT.md`) más un fan-out de 15 agentes de investigación web que consumió **1.115.458 tokens de subagente** en 318 llamadas a herramientas.

## 4. Lo que se deduce

Atribuyendo el grueso del consumo al fan-out:

| Magnitud | Estimación |
|---|---|
| **Ventana de 5 horas** | ≈ **1,1 – 1,4 millones de tokens** |
| **Ventana semanal** | ≈ **8 millones de tokens** |
| 1 % de la ventana de 5 horas | ≈ 11.000 – 14.000 tokens |
| 1 % de la ventana semanal | ≈ 80.000 tokens |
| Ventanas de 5 h completas que entran en una semana | ≈ **7** |

**Verificación cruzada:** una semana tiene 33 ventanas de 5 horas. Si el semanal alcanza para saturar unas 7, el límite semanal se agota trabajando fuerte **uno de cada cinco bloques**. Eso es consistente con lo que muestra la telemetría del Director: llegó al 96–97 % semanal el 13/09 y volvió a 14 % en media hora el 14/09.

### Traducido a decisiones

| Acción | Costo | Cuántas por semana |
|---|---|---|
| Fan-out de investigación sin tope (15 agentes) | **14 % del semanal** | **7** |
| Fan-out acotado (7 agentes, tope de recuperaciones) | ≈ 9 % del semanal | 11 |
| Fase 1 completa (repo, contrato, hooks, backup, GitHub) | **0 %** | ∞ |

> El dato más útil de toda la Fase 2: **la Fase 1 entera costó cero tokens de subagente.** No porque fuera chica, sino porque era trabajo determinista hecho con herramientas deterministas. Ahí está el margen.

## 5. Honestidad sobre estos números

Este modelo es **PARTIALLY VERIFIED**, y las limitaciones importan:

1. **Es una sola observación limpia.** Un punto no es una curva. Hace falta acumular marcas en `logs/consumo.csv` antes de tratar estos números como estables.
2. **Los porcentajes son enteros.** Granularidad de ±1 punto, que a escala semanal son ~80.000 tokens.
3. **El consumo de la sesión principal está incluido pero no separado.** Parte de ese 14 % fue la auditoría, no el fan-out. Los valores son un **techo** de lo que costó el fan-out.
4. **No todos los tokens valen igual.** El porcentaje del plan pondera por modelo: Opus consume mucho más por token que Haiku. "Tokens" acá significa *tokens de subagente a los modelos que efectivamente se usaron*, no una unidad universal.
5. **El tokenizador de los modelos 4.7+ produce ~30 % más tokens** para el mismo texto. Comparaciones con mediciones viejas no aplican.
6. **La telemetría se actualiza solo mientras la app está abierta.** Una muestra vieja no significa consumo cero.

## 6. Cómo se usa esto

**Antes de un trabajo caro:**
```
python config/consumo.py --marcar "descripcion del trabajo"
```

**Después:**
```
python config/consumo.py --diferencia
```

La marca queda en `logs/consumo.csv`. Con diez o quince marcas, estas estimaciones dejan de ser una deducción de un solo evento y pasan a ser un modelo real.

## 7. Reglas de gasto que salen de esto

1. **Ningún fan-out sin tope.** Declarar cuántos agentes, con qué límite de recuperaciones web y cuántos hallazgos como máximo. La tanda A sin tope costó 14 % del semanal; la tanda B con tope, 9 % — haciendo casi lo mismo.
2. **Bajar la escalera antes de subirla.** Si `ripgrep`, `git` o un script de Python resuelven, cuestan 0 %.
3. **Ráfagas de menos de una hora.** El TTL del cache en suscripción es de 1 hora; volver después reprocesa todo a precio completo.
4. **`/clear` + `HANDOFF.md`** en vez de dejar que dispare el auto-compact, que cuesta una request grande.
5. **Presupuesto por fase.** Ninguna fase debería costar más del **10 % del semanal**. Si lo supera, se parte en dos.
6. **Medir antes de optimizar.** `/usage` da atribución por skill, subagente, plugin y servidor MCP.

## 8. Señal de alarma

Si la ventana semanal supera el **60 %** antes del cuarto día del ciclo, hay que parar y revisar qué está consumiendo con `/usage` en vez de seguir construyendo. A ese ritmo la semana no llega.
