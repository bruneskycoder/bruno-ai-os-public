---
name: implementar-con-evidencia
description: Construye, corrige o depura algo con un ciclo de leer, declarar cómo se demuestra que terminó, actuar en pasos chicos, comprobar con una prueba real y corregir, con tope de iteraciones y de consumo. Úsese cuando Bruno pide implementar, arreglar, depurar o generar un entregable que se puede comprobar (un script, una hoja, un PDF, un dato, una página). No sirve para diseñar qué construir (eso es plan-before-build), para investigar ni para pedidos triviales de un solo paso.
---

# Implementar con evidencia

Terminar no es haber escrito. Es haber **demostrado** que anda. Esta skill cubre lo que `plan-before-build` no: el ciclo de ejecución, sus topes y el reporte final.

## Cuándo usarla y cuándo no

| Pedido | Qué usar |
|---|---|
| Hay que decidir qué construir o cómo | `plan-before-build` (esta skill arranca cuando el plan ya existe o la tarea es chica y clara) |
| Hay que averiguar algo | `investigacion-con-artefacto` |
| Construir, arreglar, depurar o generar algo comprobable | **Esta** |
| Un solo paso obvio (renombrar, mover) | Ninguna: hacerlo y listo |

## El ciclo

1. **Leer.** Mirar el estado real antes de tocar: archivos, `git status`, el último `PROGRESS.md`. Lo escrito puede estar desactualizado.
2. **Declarar la condición de terminación.** Una frase: qué se ejecuta y qué resultado prueba que terminó. Si `PLAN.md` ya la tiene, usarla. Si no se puede comprobar, decirlo ahora y pedirle al Director otra condición. No se empieza sin una.
3. **Actuar chico.** El cambio mínimo que acerca a la condición. Sin ampliar el alcance por iniciativa propia.
4. **Comprobar con algo real**, no con la afirmación de que terminó:

   | Nivel | Qué prueba | Ejemplos |
   |---|---|---|
   | Calidad | Que no haya errores básicos | Chequeos del repo, formato, escaneo de secretos |
   | Comportamiento | Que haga lo pedido | Correr el script o los tests, entradas buenas y malas |
   | Resultado | Que sirva de verdad | Abrir la página, renderizar el PDF y mirarlo, medir el archivo |

5. **Corregir o parar.** Si la comprobación falla, buscar la causa y volver al paso 3. Si pasa, detenerse.

## Topes: cuándo se frena

- **Tres vueltas seguidas sin avance** sobre la misma falla: parar, decir qué se probó y qué se descartó. Ninguna cuarta vuelta sin una idea nueva.
- **Consumo:** declarar el costo esperado antes de empezar. Una fase no debería pasar del 10 % del semanal (`AGENTS.md` §4); si se acerca, partirla en dos.
- **Irreversible o externo** (borrar fuera del repo, publicar, credenciales, compras): no es un paso del ciclo. Se frena y lo decide el Director (`AGENTS.md` §10).
- **Bloqueo** (falta un dato, una herramienta no está, no se puede verificar): detenerse y explicarlo. No fingir éxito.

## Reporte final

Siempre estas cuatro líneas, sin mostrar código al Director salvo que haga falta:

- **Condición de terminación:** la que se declaró.
- **Comprobado:** qué se ejecutó y la salida real, con su estado (`VERIFIED` / `PARTIALLY VERIFIED`).
- **Sin comprobar:** lo que quedó afuera y por qué (`ASSUMED` / `BLOCKED`). Esta línea nunca se omite; si está vacía, decir «nada».
- **Archivos tocados.**

Una comprobación que no se corrió no se informa como exitosa.

## Qué no se midió

Esta skill no superó una prueba contra un baseline (`claude plugin eval` sigue en acceso anticipado, B12). Entra por decisión del Director (ADR-0014) y se reconsidera según la señal que ese ADR fija.
