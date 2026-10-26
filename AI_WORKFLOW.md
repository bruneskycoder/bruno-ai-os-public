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

## Cómo se verifica sin revisar el código línea por línea

Como no reviso el código línea por línea, la confianza sale de resultados que se pueden comprobar:

- **Estados de evidencia en cada afirmación:** `VERIFIED`, `PARTIALLY VERIFIED`, `ASSUMED` o `BLOCKED`. Está prohibido escribir «funciona» o «seguro» sin una prueba.
- **Pruebas automáticas.** [`tests/validar-componentes.py`](tests/validar-componentes.py) verifica el formato de skills y subagentes y la separación de roles. Un workflow de GitHub Actions lo corre en cada subida.
- **Revisión por pares de otra IA.** Los resultados importantes se contrastan con modelos distintos del que los produjo.
- **Comprobación desde afuera.** Lo que se publica se verifica clonándolo de forma anónima, para ver lo mismo que ve un visitante.

## Autoría de los commits

- La mayoría de los commits de estos repositorios figuran con el autor «Claude», porque el agente es quien escribe y commitea. Cada commit lleva una línea `Co-Authored-By` con el modelo y otra con la sesión de trabajo.
- Mi nombre aparece con distintas grafías según desde qué equipo o configuración se commiteó. No se reescribió el historial para unificarlas: hacerlo rompería enlaces y pull requests existentes.
- Los cambios del agente entran por pull request. Yo los reviso y los mergeo, o le pido al agente que lo haga. Las ramas de las sesiones con agente tienen un nombre generado (`claude/...`).

## Casos reales

Cuatro ejemplos, con lo que se sabe de cómo se detectó cada uno y lo que no se pudo comprobar:

| Caso | Qué pasó | Cómo se detectó | Dónde verlo |
|---|---|---|---|
| Virtualización | Los documentos de la obra decían que estaba apagada; se había habilitado semanas antes. Se corrigieron seis lugares. | Contraste con la configuración real. | [`PROGRESS.md`](PROGRESS.md) |
| Script que falla en un clon nuevo | `herramientas/fuentes_nz.py` suponía que la carpeta `salida/pruebas` ya existía. | Al correrlo en un clon nuevo, según el mensaje del commit. | Commit `82ceffe` de [`nz-printable-atlas`](https://github.com/bruneskycoder/nz-printable-atlas) |
| Pie desactualizado | La lámina ING-T-01 decía que las unidades del libro estaban sin verificar cuando ya lo estaban. | Revisión manual al preparar la edición pública, no un chequeo automático. | Commit `29cf3ac` de [`laminas-de-ingles`](https://github.com/bruneskycoder/laminas-de-ingles) |
| Reconstrucción no idéntica | Reconstruir ING-T-10 desde el HTML da 0,27 % de píxeles distintos respecto del PDF publicado. | Comparación de imágenes. No se corrigió: se declaró. | README de [`laminas-de-ingles`](https://github.com/bruneskycoder/laminas-de-ingles) |

## Límites que declaro

- **El que escribe y el que audita puede ser el mismo modelo.** Por eso los hallazgos de mayor impacto se contrastan con una IA distinta y con herramientas deterministas.
- **La decisión de permisos ([`ADR-0016`](docs/decisions/)) está registrada, pero falta verificarla en la máquina de trabajo.**
- **Los números de costo son mediciones de una cuenta concreta.** No se pueden generalizar.
- **Esto es una edición pública curada** de un repositorio privado: ver «Qué no se publica» en el [`README`](README.md).
