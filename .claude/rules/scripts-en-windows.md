---
description: Reglas para escribir scripts que funcionen en esta máquina Windows concreta
paths:
  - "**/*.py"
  - "**/*.ps1"
  - "**/*.sh"
  - "**/*.cmd"
---

# Scripts en esta máquina

Entorno real: Windows 11 Pro N, locale `es-419`, PowerShell 5.1, Git Bash, Python 3.13.2. **Sin Node, sin jq, sin uv, sin Docker.**

## Reglas duras

1. **Python es el lenguaje por defecto** para cualquier lógica. PowerShell solo para lo nativo de Windows; Bash solo para tuberías POSIX cortas.
2. **Nada de `jq`.** Parsear JSON con `python -c` o el módulo `json`.
3. **Nada de `npx` ni `npm`.** Si una receta empieza así, no aplica acá.
4. **Decidir por código de salida, nunca por texto de error.** La consola está en español: cualquier `grep` de mensajes en inglés falla en silencio.
5. **Encoding:** definir `PYTHONIOENCODING=utf-8` en todo proceso Python que escriba salida. La codepage del sistema no es UTF-8.
6. **Archivos sin BOM, finales de línea LF.** `Out-File` y `Set-Content` de PowerShell 5.1 escriben BOM o ANSI por defecto: usar `-Encoding utf8` explícito, o mejor escribir desde Python.
7. **PowerShell 5.1 no tiene** `&&`, `||`, operador ternario, `??` ni `?.`. Usar `;` con `if ($?)`.
8. **Rutas con barra normal** en configuraciones y documentación.
9. Si un script MCP local habla por stdio: **todo log va a stderr**. Un solo `print` a stdout rompe el canal JSON-RPC.

9. **Git Bash convierte los argumentos que empiezan con `/`.** `schtasks /run /tn X` se transforma en `schtasks "C:/Program Files/Git/run"` y falla. Para comandos nativos de Windows con flags al estilo `/flag`, usar **PowerShell**, o anteponer `MSYS_NO_PATHCONV=1`. Descubierto en la Fase 8 — borrando respaldos antes de comprobar que la tarea corriera.
10. **Los heredocs de Bash con contenido largo en español fallan de forma intermitente** en este entorno. Para escribir archivos, usar las herramientas de edición directas; dejar Bash para git y comandos cortos.

## Secretos en scripts — reglas que costaron una clave rotada

11. **La redacción va en el punto de impresión, no en cada rama de error.** Un script de diagnóstico redactaba la clave en la rama de `HTTPError` pero no en la de excepción genérica; el mensaje la imprimió entera y hubo que rotarla. Regla: una sola función de salida que redacta siempre, o directamente no imprimir el valor bajo ninguna circunstancia.
12. **Limpiar toda clave pegada antes de guardarla.** En un campo oculto de la consola de Windows, `Ctrl+V` se guarda como carácter de control (`\x16`, `\x1a`) en lugar de pegar. La clave queda rota con basura invisible y el servicio devuelve un error que no dice nada. `.strip()` no alcanza: hay que filtrar todo lo no imprimible. Y avisar al usuario que pegue con **clic derecho**.
13. **Nunca construir una URL con un secreto en la query.** Además de filtrarse en logs y en mensajes de error, es lo que hizo visible la clave en el caso anterior. Va en un header.

## Antes de commitear

El hook `pre-commit` corre `gitleaks` sobre lo preparado. Si detecta un secreto, **no** hay que sortear el hook: hay que sacar el secreto y guardarlo en el Credential Manager (`python -m keyring`).
