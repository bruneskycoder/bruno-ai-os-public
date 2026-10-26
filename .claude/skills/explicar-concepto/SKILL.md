---
name: explicar-concepto
description: Explica un concepto técnico a Bruno usando analogías de obra, construcción y topografía, más un diagrama Mermaid cuando aporte claridad. Úsese cuando el Director pregunta qué es algo, cómo funciona, por qué se eligió una tecnología, o cuando aparece un término técnico que necesita entender para poder decidir. No sirve para escribir documentación técnica ni para explicarle código línea por línea.
---

# Explicar un concepto

El Director dirige la obra sin escribir código. Necesita entender **para decidir**, no para programar. Una explicación exitosa no es la que suena completa: es la que le permite elegir entre dos opciones con criterio.

## La estructura, siempre en este orden

1. **Qué es** — una frase, sin jerga.
2. **Por qué existe** — qué problema apareció primero. Un concepto sin problema que lo justifique no se entiende, se memoriza.
3. **Dónde está** — dónde aparece en *su* sistema. Ruta de archivo concreta, no abstracción.
4. **Qué hace** — el mecanismo. Acá sí puede entrar detalle.
5. **Analogía visual** — de obra, electromecánica o topografía.

## Las analogías

Su dominio nativo es la construcción y el campo. Estas funcionan porque tienen la misma **estructura**, no porque suenen parecido:

| Concepto | Analogía | Por qué funciona |
|---|---|---|
| API | Interfaz entre gremios | Cada uno hace lo suyo; el contacto es un protocolo acordado |
| Git | Control de revisiones de planos | Versiones, quién cambió qué, volver a una anterior |
| Base de datos | Depósito con estantería rotulada | Guardar es fácil; encontrar es el problema que resuelve |
| Caché | Material a pie de obra | Traerlo cuesta; tenerlo cerca ahorra viajes |
| Sandbox | Obrador cercado | Adentro se puede romper; afuera no se contamina |
| Permisos | Habilitaciones y EPP | Quién puede hacer qué, y con qué protección |
| Compactación | Resumen de acta de obra | Queda lo importante; el detalle se pierde |
| Artefacto | Plano aprobado y archivado | Se produce una vez y se consulta muchas |

**Regla:** si la analogía distorsiona el concepto, no se usa. Una analogía que hace entender mal es peor que ninguna. Cuando una analogía tiene un límite, decirlo: *"hasta acá funciona la comparación; de acá en adelante no"*.

## El diagrama

Mermaid cuando aporte, no por costumbre. Sirve cuando hay **flujo, jerarquía o decisión**; no sirve para una definición.

| Situación | Tipo |
|---|---|
| Cómo se mueve algo entre partes | `flowchart` |
| Quién le habla a quién y en qué orden | `sequenceDiagram` |
| Cómo se relacionan las entidades | `erDiagram` |
| Cómo está armado el sistema | `flowchart` por capas |

Un diagrama con más de una docena de nodos ya no explica: abruma. Partirlo.

## Registrar lo aprendido

Cuando el concepto sea relevante para el proyecto, dejarlo en `docs/learning/` con: concepto, definición, analogía, por qué importa, **ejemplo en Bruno AI OS**, cuándo usarlo, relaciones. Así se explica una vez y se consulta después.

## Qué no hacer

- **No dar un curso.** Se responde lo que se preguntó, al nivel que hace falta para decidir.
- **No mostrar código** salvo que sea imprescindible para resolver un problema concreto.
- **No abstracciones sin aterrizar.** Todo concepto se conecta con algo que está en su máquina o en su repositorio.
- **No relleno.** Si la respuesta son dos frases, son dos frases.
