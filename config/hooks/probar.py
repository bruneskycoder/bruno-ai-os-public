"""Verifica que el hook pre-commit realmente bloquea un secreto.

No es una formalidad: un hook que no bloquea es peor que no tener hook,
porque da sensacion de proteccion. Este script lo comprueba de verdad.

Uso:  python config/hooks/probar.py
Salida: 0 si el hook bloquea correctamente, 1 si no.
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PRUEBA = RAIZ / "tests" / "_secreto-de-prueba.txt"

# El senuelo se ARMA EN TIEMPO DE EJECUCION, nunca se guarda como literal.
# Motivo: si estuviera escrito entero, gitleaks lo detectaria en este mismo
# archivo y bloquearia todo commit del repositorio. La alternativa seria poner
# una excepcion en la configuracion del escaner, y debilitar el escaner para
# que pase su propia prueba es exactamente lo que no hay que hacer.
_PREFIJO = "gh" + "p_"
_CUERPO = "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6Q7r8"
CARNADA = f"GITHUB_TOKEN={_PREFIJO}{_CUERPO}\n"


def git(*args, **kw):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, **kw)


def limpiar():
    git("reset", "-q", "HEAD", str(PRUEBA))
    PRUEBA.unlink(missing_ok=True)


def main() -> int:
    if not (RAIZ / ".git" / "hooks" / "pre-commit").is_file():
        print("FALLO: no hay hook pre-commit instalado.", file=sys.stderr)
        print("Instalar con: python config/hooks/instalar.py", file=sys.stderr)
        return 1

    PRUEBA.parent.mkdir(parents=True, exist_ok=True)
    PRUEBA.write_text(CARNADA, encoding="utf-8", newline="\n")
    try:
        git("add", str(PRUEBA))
        r = git("commit", "-m", "test: no debe pasar")
        if r.returncode == 0:
            # El commit paso: hay que deshacerlo y avisar fuerte.
            git("reset", "-q", "--mixed", "HEAD~1")
            print("FALLO: el hook NO bloqueo el commit. El repositorio esta desprotegido.", file=sys.stderr)
            return 1
        print("OK: el hook bloqueo el commit con el secreto de prueba.")
        print("     codigo de salida del commit:", r.returncode)
        return 0
    finally:
        limpiar()


if __name__ == "__main__":
    raise SystemExit(main())
