"""Respaldo de Bruno AI OS: un unico archivo restaurable, fuera del alcance del agente.

Por que un bundle y no solo el remoto de GitHub: un agente con permiso de escritura
sobre el repositorio remoto puede forzar o borrar ramas. El bundle vive en una carpeta
que no es working dir de ningun agente, asi que sobrevive a ese escenario.

Uso:
    python config/backup.py            # crea un bundle nuevo
    python config/backup.py --listar   # muestra los respaldos existentes
    python config/backup.py --verificar # valida el ultimo bundle

Restaurar:  git clone <ruta-del-bundle> bruno-ai-os-restaurado
"""
import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = Path.home() / "Backups" / "bruno-ai-os"
CONSERVAR = 8  # ~2 meses de respaldos semanales


def git(*args):
    return subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)


def listar():
    if not DESTINO.is_dir():
        print(f"(no hay respaldos todavia en {DESTINO})")
        return []
    b = sorted(DESTINO.glob("bruno-ai-os-*.bundle"))
    for f in b:
        print(f"  {f.name}  {f.stat().st_size / 1024:.0f} KB")
    return b


def verificar(ruta: Path) -> bool:
    r = subprocess.run(["git", "bundle", "verify", str(ruta)], capture_output=True, text=True)
    return r.returncode == 0


def crear() -> int:
    DESTINO.mkdir(parents=True, exist_ok=True)
    ruta = DESTINO / f"bruno-ai-os-{date.today():%Y%m%d}.bundle"
    r = git("bundle", "create", str(ruta), "--all")
    if r.returncode != 0:
        print("ERROR al crear el bundle:", r.stderr.strip(), file=sys.stderr)
        return 1
    if not verificar(ruta):
        print("ERROR: el bundle se creo pero no pasa la verificacion.", file=sys.stderr)
        return 1
    print(f"OK: {ruta}  ({ruta.stat().st_size / 1024:.0f} KB, verificado)")

    viejos = sorted(DESTINO.glob("bruno-ai-os-*.bundle"))[:-CONSERVAR]
    for f in viejos:
        f.unlink()
        print(f"     rotado (eliminado): {f.name}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Respaldo de Bruno AI OS")
    p.add_argument("--listar", action="store_true")
    p.add_argument("--verificar", action="store_true")
    a = p.parse_args()

    if a.listar:
        listar()
        return 0
    if a.verificar:
        b = listar()
        if not b:
            return 1
        ok = verificar(b[-1])
        print("OK: bundle valido" if ok else "FALLO: bundle corrupto")
        return 0 if ok else 1
    return crear()


if __name__ == "__main__":
    raise SystemExit(main())
