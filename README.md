# Bruno AI OS — edición pública

[![Validar componentes](https://github.com/bruneskycoder/bruno-ai-os-public/actions/workflows/validar.yml/badge.svg)](https://github.com/bruneskycoder/bruno-ai-os-public/actions/workflows/validar.yml)

> **In English:** The operating contract and structure I use to work with AI agents (Claude Code). It is a repository that is read, not run: a work contract, a measured cost model, model routing, architecture decision records, skills, subagents with separated permissions, and tests. I am not a professional developer: I direct and verify, Claude writes. This is a curated public edition of a private repository. Documents are in Spanish.

## Qué es

**No es un programa: es un repositorio estructurado que se lee.** El orquestador ya existe (Claude Code). Acá viven las reglas que gobiernan cómo trabajan los agentes, lo que cuesta trabajar con ellos, las decisiones tomadas y las pruebas que vigilan que el sistema siga siendo lo que dice ser.

Lo armé para trabajar con un plan de suscripción de Claude sin posibilidad de comprar uso extra, donde los tokens son un recurso escaso. De ahí salen sus cuatro ideas:

1. **Nada se declara funcionando sin evidencia.** Cada afirmación lleva un estado: `VERIFIED`, `PARTIALLY VERIFIED`, `ASSUMED` o `BLOCKED`.
2. **Los tokens son material de obra.** El costo se mide, se declara antes de gastarlo y se ordena en una escalera: herramienta determinista, modelo chico, modelo mediano, modelo grande, persona.
3. **Quien lee contenido externo no escribe.** Los subagentes tienen permisos separados, y una prueba falla si esa separación se rompe.
4. **Si importa, está en un archivo.** Las decisiones quedan como ADR y el estado entre sesiones, en documentos.

## Por dónde entrar

| Si querés… | Leé |
|---|---|
| Ver cómo trabajo con IA, en una página | [`AI_WORKFLOW.md`](AI_WORKFLOW.md) |
| Entender las reglas de los agentes | [`AGENTS.md`](AGENTS.md) |
| Ver cómo está armado | [`ARCHITECTURE.md`](ARCHITECTURE.md) |
| Saber cuánto cuesta y cómo se ahorra | [`COST_MODEL.md`](COST_MODEL.md) y [`MODEL_ROUTING.md`](MODEL_ROUTING.md) |
| Saber por qué se decidió algo | [`docs/decisions/`](docs/decisions/) (18 ADR) |
| Ver las capacidades | [`.claude/skills/`](.claude/skills/), [`.claude/agents/`](.claude/agents/) y [`.claude/rules/`](.claude/rules/) |
| Ver cómo se verifica | [`tests/`](tests/) y [`artifacts/pruebas-de-aceptacion.md`](artifacts/pruebas-de-aceptacion.md) |
| Ver cómo se evalúa algo antes de instalarlo | [`artifacts/auditoria-free-claude-code.md`](artifacts/auditoria-free-claude-code.md) |
| Ver cómo se delega trabajo a otras IAs | [`artifacts/delegar-investigacion.md`](artifacts/delegar-investigacion.md) |
| Saber en qué estado está la obra | [`PROGRESS.md`](PROGRESS.md) y [`ROADMAP.md`](ROADMAP.md) |

## Cómo se hizo

No programo de oficio. Diseñé el sistema y tomé las decisiones, que quedan registradas como ADR: siete de los dieciocho están marcadas como decisión del Director. Claude Code escribió los documentos, los scripts y las pruebas.

Como no leo el código, la confianza no sale de revisarlo sino de lo que se puede comprobar: pruebas propias, estados de evidencia en cada afirmación y reglas que frenan lo que no debe pasar.

## Qué no se publica

Esta es una **edición curada**: se arma desde una lista de archivos permitidos y se escanea antes de cada subida. No se publican el inventario de la máquina de trabajo, el modelo de amenazas detallado, el archivo de obra con los estados de cada sesión, el libro de consumo, los informes de investigación en bruto ni las auditorías sobre archivos personales. Las rutas y los datos de la máquina están reemplazados por marcadores como `<usuario>` o `<carpeta-del-proyecto>`.

## Límites

- **Algunos documentos citan archivos que no están acá** (por ejemplo `SYSTEM_AUDIT.md`, `THREAT_MODEL.md`, `memory/` o `docs/research/`). Es esperable: son los privados.
- **Está hecho para una PC con Windows y un plan Claude Pro.** Los números de costo son mediciones de esa cuenta; no se pueden generalizar.
- **Los scripts no se ejecutan tal cual:** los marcadores reemplazan rutas y datos reales, y varios dependen de herramientas locales.
- **Varias decisiones no están medidas contra una alternativa.** Cada ADR dice qué se verificó y qué no.
- **La decisión de permisos (ADR-0016) está registrada, pero su verificación en la máquina de trabajo está pendiente.**

## Licencias

- **Documentos** (todo lo que no es código): [CC-BY-4.0](LICENSE). Podés usarlos y adaptarlos con atribución: «Bruno AI OS, de Bruno Gutiérrez ([@bruneskycoder](https://github.com/bruneskycoder)), CC-BY-4.0».
- **Código** (`config/`, `tests/`): [MIT](LICENSE-CODIGO).
