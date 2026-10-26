# Costo de retomar el trabajo

| Campo | Valor |
|---|---|
| Proposito | Medir si el handoff realmente ahorra contexto frente a reconstruirlo |
| Fecha | 2026-09-15 |
| Version | 1.0 |
| Clasificacion | INTERNO |
| Fuentes | Conteo de caracteres del propio repositorio |
| Estado | PARTIALLY VERIFIED — conteo exacto, conversion a tokens estimada |
| Relaciones | ADR-0003 · COST_MODEL.md · memory/README.md |

Generado por `python config/costo-de-retomar.py --guardar`.

```
RUTA A — reconstruir el contexto leyendo la documentacion
  AGENTS.md                            8,828 chars  ~ 2,675 tokens
  SYSTEM_AUDIT.md                     14,264 chars  ~ 4,322 tokens
  ARCHITECTURE.md                     20,098 chars  ~ 6,090 tokens
  ROADMAP.md                          11,064 chars  ~ 3,352 tokens
  PROGRESS.md                          8,426 chars  ~ 2,553 tokens
  COST_MODEL.md                        5,550 chars  ~ 1,681 tokens
  docs/security/THREAT_MODEL.md       13,088 chars  ~ 3,966 tokens
  docs/research/FINDINGS.md           24,967 chars  ~ 7,565 tokens
  memory/README.md                     4,789 chars  ~ 1,451 tokens
  TOTAL                                              ~33,655 tokens

RUTA B — retomar leyendo el handoff
  memory/HANDOFF.md                    2,859 chars  ~   866 tokens
  TOTAL                                              ~   866 tokens

RESULTADO
  El handoff cuesta 39 veces menos que reconstruir.
  Ahorro por retomada: ~32,789 tokens  (~0.41% de la ventana semanal)
  Cada 10 retomadas: ~327,890 tokens  (~4.1% del semanal)
  Cada 50 retomadas: ~1,639,450 tokens  (~20% del semanal)

  Metodo: 3.3 caracteres por token (estimacion declarada).
  Los conteos de caracteres son exactos; la relacion entre rutas no depende del ratio.
```
