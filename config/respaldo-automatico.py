"""Registra el respaldo semanal como tarea programada de Windows.

Por que asi y no como tarea de Claude: el respaldo es trabajo puramente
determinista. Una tarea del Programador de tareas de Windows lo corre sin gastar
un solo token del plan. Usar un agente para esto seria pagar por algo gratis.

Corre los domingos a las 20:00, solo si la maquina esta encendida. No despierta
el equipo ni exige privilegios de administrador: es una tarea de usuario.

Uso:
  python config/respaldo-automatico.py --estado      ver si esta registrada
  python config/respaldo-automatico.py --registrar   crearla
  python config/respaldo-automatico.py --quitar      eliminarla
"""
import argparse
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TAREA = "BrunoAIOS-RespaldoSemanal"
SCRIPT = RAIZ / "config" / "backup.py"


def schtasks(*args):
    return subprocess.run(
        ["schtasks", *args], capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )


def estado() -> int:
    r = schtasks("/query", "/tn", TAREA, "/fo", "list")
    if r.returncode != 0:
        print(f"La tarea '{TAREA}' NO esta registrada.")
        print("Registrarla con: python config/respaldo-automatico.py --registrar")
        return 1
    for linea in r.stdout.splitlines():
        if linea.strip():
            print(f"  {linea.strip()}")
    return 0


def registrar() -> int:
    if not SCRIPT.is_file():
        print(f"ERROR: no existe {SCRIPT}", file=sys.stderr)
        return 1
    accion = f'"{sys.executable}" "{SCRIPT}"'
    r = schtasks(
        "/create", "/tn", TAREA, "/tr", accion,
        "/sc", "weekly", "/d", "SUN", "/st", "20:00", "/f",
    )
    if r.returncode != 0:
        print("FALLO el registro de la tarea:", file=sys.stderr)
        print((r.stderr or r.stdout).strip()[:500], file=sys.stderr)
        return 1
    print(f"Tarea '{TAREA}' registrada: domingos 20:00.")
    print("Verificar con: python config/respaldo-automatico.py --estado")
    print("Quitar con:    python config/respaldo-automatico.py --quitar")
    return 0


def quitar() -> int:
    r = schtasks("/delete", "/tn", TAREA, "/f")
    if r.returncode != 0:
        print("No se pudo eliminar (quiza no existia).", file=sys.stderr)
        return 1
    print(f"Tarea '{TAREA}' eliminada.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Respaldo semanal como tarea de Windows")
    ap.add_argument("--estado", action="store_true")
    ap.add_argument("--registrar", action="store_true")
    ap.add_argument("--quitar", action="store_true")
    a = ap.parse_args()
    if a.registrar:
        return registrar()
    if a.quitar:
        return quitar()
    return estado()


if __name__ == "__main__":
    raise SystemExit(main())
