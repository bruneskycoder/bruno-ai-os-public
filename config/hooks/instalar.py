"""Instala los hooks de git de Bruno AI OS.

Los hooks viven en config/hooks/ (versionado) y se copian a .git/hooks/ (no versionado).
Uso:  python config/hooks/instalar.py
"""
import shutil
import stat
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
ORIGEN = RAIZ / "config" / "hooks"
DESTINO = RAIZ / ".git" / "hooks"
HOOKS = ["pre-commit"]

# El guardia se instala fuera del repositorio, en la configuracion de usuario.
# Motivo: el hook global de Claude Code lo invoca en TODOS los proyectos. Si
# apuntara a una ruta del repositorio y esa carpeta se moviera, Python fallaria
# con codigo 2 -- el mismo codigo que significa BLOQUEAR -- y ningun comando
# Bash volveria a ejecutarse en ninguna sesion.
GUARDIA_DESTINO = Path.home() / ".claude" / "guardia.py"


def instalar_guardia() -> None:
    src = ORIGEN / "guardia.py"
    if not src.is_file():
        print(f"AVISO: no se encontro {src}; se omite el guardia.", file=sys.stderr)
        return
    GUARDIA_DESTINO.parent.mkdir(parents=True, exist_ok=True)
    GUARDIA_DESTINO.write_text(
        src.read_text(encoding="utf-8").replace("\r\n", "\n"),
        encoding="utf-8", newline="\n",
    )
    print(f"instalado: {GUARDIA_DESTINO}")


def main() -> int:
    instalar_guardia()
    if not DESTINO.is_dir():
        print(f"ERROR: no existe {DESTINO}. Esto no parece un repositorio git.", file=sys.stderr)
        return 1

    for nombre in HOOKS:
        src = ORIGEN / nombre
        if not src.is_file():
            print(f"ERROR: falta {src}", file=sys.stderr)
            return 1
        dst = DESTINO / nombre
        # Escribir con finales de linea LF: git ejecuta los hooks con sh.
        contenido = src.read_text(encoding="utf-8").replace("\r\n", "\n")
        dst.write_text(contenido, encoding="utf-8", newline="\n")
        dst.chmod(dst.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print(f"instalado: .git/hooks/{nombre}")

    print("Listo. Probar con: python config/hooks/probar.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
