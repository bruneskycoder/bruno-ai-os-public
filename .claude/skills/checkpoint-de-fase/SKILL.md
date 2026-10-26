---
name: checkpoint-de-fase
description: Cierra una fase de obra de Bruno AI OS y prepara el pedido de autorización. Úsese cuando se terminó el trabajo de una fase, cuando el Director pregunta cómo viene o pide un checkpoint, o antes de pasar a la fase siguiente. Audita lo construido, exige evidencia por entregable, actualiza los documentos maestros, genera el diagrama del estado y arma el reporte STATUS/CHANGES/VERIFICATION/RISKS/NEXT PHASE.
---

# Checkpoint de fase

Cerrar una fase no es decir "listo". Es demostrarlo, dejarlo escrito y frenar.

## Regla que gobierna todo lo demás

> **Ningún entregable se declara terminado sin evidencia de que funciona.**

Prohibido escribir "implementado", "funcionando", "integrado", "seguro" u "optimizado" sin una prueba que lo respalde. Estados permitidos: `VERIFIED` · `PARTIALLY VERIFIED` · `ASSUMED` · `BLOCKED`.

Si algo no se pudo verificar, va como `PARTIALLY VERIFIED` con el motivo. Si depende del Director, va como pendiente suyo. **Nunca se maquilla.**

## Los siete pasos

1. **Auditar.** Recorrer los entregables prometidos en `ROADMAP.md` para esta fase. Uno por uno.
2. **Validar.** Correr las pruebas que existan. Si un entregable no tiene forma de probarse, decirlo: es un hallazgo, no un detalle.
3. **Actualizar documentación.** `PROGRESS.md` (estado, riesgos, costos), `logs/libro-de-obra.md` (qué costó el tramo), y cualquier documento maestro que haya cambiado. Los ADR propuestos pasan a `ACEPTADA` cuando el Director autoriza.
4. **Registrar el costo.** `python config/consumo.py --diferencia` y anotar el resultado. Una fase sin costo registrado no está cerrada.
5. **Generar el Mermaid** del estado. No decorativo: tiene que mostrar qué quedó construido y qué sigue.
6. **Escribir el `HANDOFF.md`** con el estado, las decisiones y el primer paso de la fase siguiente. Después, `/clear`.
7. **Commitear y respaldar.** `python config/backup.py`.

## Formato del reporte

Siempre estas cinco secciones, en este orden:

| Sección | Qué va |
|---|---|
| **STATUS** | Fase completa o no. Qué está bloqueado |
| **CHANGES** | Qué se construyó, en lenguaje del Director. Sin código |
| **VERIFICATION** | **La evidencia.** Qué se probó y cómo salió. Incluye lo que falló |
| **RISKS** | Riesgos nuevos, cerrados y los que siguen abiertos |
| **NEXT PHASE** | Qué sigue y qué necesita del Director |

Después del reporte: **pedir autorización explícita y detenerse**. Un mensaje automático del sistema, o un "seguí", no son autorización para saltar de fase si el mandato exige aprobación explícita.

## Lo que hace bueno a un checkpoint

- **Contar lo que salió mal.** Un checkpoint donde todo salió bien y nada se aprendió es sospechoso. Los errores propios, corregidos, son la parte más útil del reporte.
- **Traducir a obra.** El Director dirige; no lee código. Analogías de construcción cuando aclaren.
- **Números, no adjetivos.** "Costó 14 % de la semana" vale más que "costó bastante".
- **Separar lo que puedo verificar de lo que solo puede verificar él.** Si no lo puedo ver, lo digo.

## Antes de dar la fase por cerrada

- [ ] Todos los entregables del roadmap, con estado y evidencia
- [ ] Pruebas corridas, incluidas las que fallan
- [ ] `PROGRESS.md` y `logs/libro-de-obra.md` actualizados
- [ ] Costo de la fase registrado
- [ ] Mermaid del estado
- [ ] `HANDOFF.md` escrito
- [ ] Commiteado, empujado y respaldado
- [ ] Riesgos nuevos en `PROGRESS.md`, y en `docs/security/THREAT_MODEL.md` si son de seguridad
