# Cómo trabajo con IA

> Propósito: describir con exactitud cómo se reparte el trabajo entre una persona y los agentes de IA en este repositorio, y qué se comprueba y qué no.
> Clasificación: PÚBLICO · Estado: vigente · Relaciones: [`AGENTS.md`](AGENTS.md), [`docs/decisions/`](docs/decisions/), [`tests/`](tests/)

Esta página no agrega reglas: reúne las que ya existen y dice dónde verlas.

## Quién hace qué

| Rol | Qué hace | Qué no hace |
|---|---|---|
| **Director** (yo) | Define qué se construye y para quién, fija cómo se demuestra que está terminado, decide lo irreversible (credenciales, compras, publicar). | No escribe ni revisa el código línea por línea. |
| **Claude Code** | Diseña, escribe, ejecuta, prueba, depura y documenta. | No declara algo terminado sin una prueba que lo respalde. |
| **Subagentes** | Investigan (solo web y lectura), critican (solo lectura) o ejecutan (solo escritura, sin web). | Ninguno combina escritura y navegación: una prueba falla si se rompe esa separación. |

## El ciclo

1. **Condición de terminación primero.** Antes de construir se declara qué se ejecuta y qué resultado se espera ([`ADR-0014`](docs/decisions/)).
2. **Construir, probar, revisar, corregir, documentar**, con tope de iteraciones y de consumo. Al llegar al tope se frena y se informa el estado.
3. **Reutilizar antes de construir.** Se busca qué existe, con tope de búsquedas y de repositorios leídos, y se deja un informe corto.
4. **Reporte de cierre** con cinco partes: estado, cambios, verificación, riesgos y próxima fase. Siempre incluye lo que **no** se pudo comprobar.

## Cómo se verifica sin leer el código

Como no leo el código, la confianza sale de resultados que se pueden comprobar:

- **Estados de evidencia en cada afirmación:** `VERIFIED`, `PARTIALLY VERIFIED`, `ASSUMED` o `BLOCKED`. Está prohibido escribir «funciona» o «seguro» sin una prueba.
- **Pruebas automáticas.** [`tests/validar-componentes.py`](tests/validar-componentes.py) verifica el formato de skills y subagentes y la separación de roles. Un workflow de GitHub Actions lo corre en cada subida.
- **Revisión por pares de otra IA.** Los resultados importantes se contrastan con modelos distintos del que los produjo.
- **Comprobación desde afuera.** Lo que se publica se verifica clonándolo de forma anónima, para ver lo mismo que ve un visitante.

## Un caso real

Los documentos de la obra decían que la virtualización de la máquina estaba apagada. Al contrastarlo con la configuración real resultó que se había habilitado semanas antes. Se corrigieron seis lugares y se dejó escrito qué sí está en uso (nada de aislamiento) y qué no. El detalle está en [`PROGRESS.md`](PROGRESS.md).

## Límites que declaro

- **El que escribe y el que audita puede ser el mismo modelo.** Por eso los hallazgos de mayor impacto se contrastan con una IA distinta y con herramientas deterministas.
- **La decisión de permisos ([`ADR-0016`](docs/decisions/)) está registrada, pero falta verificarla en la máquina de trabajo.**
- **Los números de costo son mediciones de una cuenta concreta.** No se pueden generalizar.
- **Esto es una edición pública curada** de un repositorio privado: ver «Qué no se publica» en el [`README`](README.md).
