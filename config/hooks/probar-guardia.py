"""Verifica que el guardia bloquee lo que tiene que bloquear y deje pasar el resto.

Un guardia que no bloquea es peor que no tener guardia: da sensacion de
proteccion. Y uno que bloquea de mas hace el sistema inusable. Se prueban las
dos cosas.

Uso:  python config/hooks/probar-guardia.py
Salida: 0 si todos los casos pasan, 1 si alguno falla.
"""
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GUARDIA = RAIZ / "config" / "hooks" / "guardia.py"

DEBE_BLOQUEAR = [
    "git push --force origin main",
    "git push -f",
    "git reset --hard HEAD~5",
    "git clean -fdx",
    "git commit --no-verify -m 'saltear el hook'",
    "git branch -D main",
    "rm -rf /c/Users/<usuario>/Desktop",
    "Remove-Item -Recurse -Force C:/Users/<usuario>\\Documents",
    "gh repo delete bruneskycoder/bruno-ai-os",
    "gh auth token",
    "git config --global user.email otro@ejemplo.com",
    "format C:",
]

DEBE_PASAR = [
    "git status",
    "git add -A",
    "git commit -m 'feat: algo'",
    "git push origin main",
    "python config/backup.py",
    "rg -i texto memory/",
    "ls -la",
    "git log --oneline",
    "python tests/validar-componentes.py",
    "rm archivo-temporal.txt",
    # Regresiones de falsos positivos encontrados en uso real.
    # Un guardia que frena trabajo legitimo es peor que no tener guardia.
    "claude -p 'hola' --output-format stream-json",
    "python -c \"print('formato de salida')\"",
    "git log --format=oneline",
]


def correr(comando: str) -> int:
    entrada = json.dumps({"tool_name": "Bash", "tool_input": {"command": comando}})
    r = subprocess.run(
        [sys.executable, str(GUARDIA)],
        input=entrada, capture_output=True, text=True,
    )
    return r.returncode


def main() -> int:
    fallos = []

    print("CASOS QUE DEBEN BLOQUEARSE")
    for c in DEBE_BLOQUEAR:
        code = correr(c)
        ok = code == 2
        print(f"  {'OK  ' if ok else 'FALLA'} (exit {code})  {c[:60]}")
        if not ok:
            fallos.append(f"NO bloqueo: {c}")

    print("\nCASOS QUE DEBEN PASAR")
    for c in DEBE_PASAR:
        code = correr(c)
        ok = code == 0
        print(f"  {'OK  ' if ok else 'FALLA'} (exit {code})  {c[:60]}")
        if not ok:
            fallos.append(f"bloqueo de mas: {c}")

    print()
    if fallos:
        for f in fallos:
            print(f"  FALLO  {f}", file=sys.stderr)
        print(f"\n{len(fallos)} caso(s) mal.", file=sys.stderr)
        return 1
    print(f"OK: {len(DEBE_BLOQUEAR)} bloqueos y {len(DEBE_PASAR)} pasadas, todos correctos.")
    print()
    print("Recordatorio honesto: esto protege contra ACCIDENTES, no contra un")
    print("atacante decidido. Como cualquier control por texto, se evade con")
    print("variables, codificacion o rutas absolutas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
