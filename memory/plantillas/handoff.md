# HANDOFF — AAAA-MM-DD

> Para que la próxima sesión arranque sin reconstruir contexto.
> Leerlo, actuar, y **borrarlo al retomar**. Si está desactualizado, miente.

## Dónde quedó todo

Estado en una o dos frases. Qué fase, qué commit, si el árbol está limpio.

## Lo que hay que saber para seguir

Solo lo que **no** está escrito en otro archivo del repositorio. Si está en
`AGENTS.md`, `PROGRESS.md` o un ADR, no se repite: se enlaza.

## Primer paso

La acción concreta con la que arranca el próximo tramo. Una sola.

## Pendientes del Director

Lo que no puedo resolver yo: credenciales, decisiones irreversibles, cosas que
solo él puede ver o probar.

## Trampas conocidas

Lo que ya me hizo perder tiempo y volvería a hacerlo.

---

<!--
POR QUÉ ESTE ARCHIVO EXISTE

Reconstruir el contexto leyendo todos los documentos del repositorio cuesta unas
46 veces más que leer este handoff: ~33.000 tokens contra ~730
(medido: ver artifacts/costo-de-retomar.md).

Por retomada el ahorro es chico en términos del plan (~0,4% del semanal), pero
se acumula: cada 50 retomadas son ~20% de una semana entera. Y el handoff
además evita el error de arrancar sin saber dónde quedó todo.

Medir la diferencia en cualquier momento:
    python config/costo-de-retomar.py
-->
