"""Lectura del consumo real del plan, a partir de la telemetria que la app ya escribe.

La app de escritorio de Claude guarda muestras periodicas en plan-usage-history.json:
  fh = % consumido de la ventana rodante de 5 horas
  sd = % consumido de la ventana larga (semanal)

No hay que construir telemetria: hay que leerla. Este script la interpreta y
permite dejar marcas en el libro de obra antes y despues de un trabajo caro,
para saber cuanto costo de verdad en vez de suponerlo.

Uso:
  python config/consumo.py                      estado actual y ultimas muestras
  python config/consumo.py --historial          todas las muestras
  python config/consumo.py --marcar "texto"     deja una marca en logs/consumo.csv
  python config/consumo.py --diferencia         cuanto se consumio desde la ultima marca
"""
import argparse
import csv
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# La consola de Windows usa cp1252 y no puede codificar los caracteres de barra.
# No se depende de que alguien exporte PYTHONIOENCODING: se resuelve aca.
for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

RAIZ = Path(__file__).resolve().parents[1]
TELEMETRIA = Path(os.environ.get("APPDATA", "")) / "Claude" / "plan-usage-history.json"
REGISTRO = RAIZ / "logs" / "consumo.csv"
CAMPOS = ["momento", "fh_pct", "sd_pct", "marca"]


def local(ms: float) -> datetime:
    return datetime.fromtimestamp(ms / 1000, timezone.utc).astimezone()


def leer_muestras() -> list:
    if not TELEMETRIA.is_file():
        print(f"ERROR: no se encontro la telemetria en {TELEMETRIA}", file=sys.stderr)
        return []
    try:
        datos = json.loads(TELEMETRIA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR al leer la telemetria: {e}", file=sys.stderr)
        return []
    muestras = []
    for x in datos.get("samples", []):
        u = x.get("u") or {}
        if "t" not in x:
            continue
        muestras.append({"t": x["t"], "fh": u.get("fh"), "sd": u.get("sd")})
    muestras.sort(key=lambda m: m["t"])
    return muestras


def barra(pct) -> str:
    if pct is None:
        return "?"
    p = max(0, min(100, int(pct)))
    return "▓" * (p // 10) + "░" * (10 - p // 10)


def estado(muestras: list) -> None:
    if not muestras:
        return
    u = muestras[-1]
    antiguedad = datetime.now(timezone.utc).astimezone() - local(u["t"])
    print("ESTADO DEL PLAN")
    print(f"  ventana 5 horas   {barra(u['fh'])} {u['fh']}%")
    print(f"  ventana semanal   {barra(u['sd'])} {u['sd']}%")
    print(f"  medido            {local(u['t']):%Y-%m-%d %H:%M} (hace {int(antiguedad.total_seconds() // 60)} min)")
    if antiguedad > timedelta(hours=1):
        print("  AVISO: la muestra es vieja. La app la actualiza mientras esta abierta.")


def resets(muestras: list) -> None:
    """Un reset se detecta cuando un porcentaje BAJA respecto de la muestra anterior."""
    hallados = []
    for a, b in zip(muestras, muestras[1:]):
        for clave, nombre in (("fh", "5 horas"), ("sd", "semanal")):
            va, vb = a.get(clave), b.get(clave)
            if va is not None and vb is not None and vb < va:
                hallados.append((local(b["t"]), nombre, va, vb))
    if not hallados:
        return
    print("\nRESETS DETECTADOS")
    for cuando, nombre, antes, despues in hallados[-8:]:
        print(f"  {cuando:%Y-%m-%d %H:%M}  ventana {nombre:<8} {antes}% -> {despues}%")


def tabla(muestras: list, cuantas: int) -> None:
    if not muestras:
        return
    print(f"\nULTIMAS {min(cuantas, len(muestras))} MUESTRAS")
    anterior = None
    for m in muestras[-cuantas:]:
        delta = ""
        if anterior and m["fh"] is not None and anterior["fh"] is not None:
            d = m["fh"] - anterior["fh"]
            if d > 0:
                delta = f"   (+{d} pts en la ventana de 5h)"
        print(f"  {local(m['t']):%Y-%m-%d %H:%M}   5h={str(m['fh']):>4}%   sem={str(m['sd']):>4}%{delta}")
        anterior = m


def marcar(texto: str, muestras: list) -> int:
    if not muestras:
        return 1
    u = muestras[-1]
    REGISTRO.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not REGISTRO.exists()
    with REGISTRO.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        if nuevo:
            w.writeheader()
        w.writerow({
            "momento": f"{local(u['t']):%Y-%m-%d %H:%M}",
            "fh_pct": u["fh"],
            "sd_pct": u["sd"],
            "marca": texto,
        })
    print(f"marca registrada en logs/consumo.csv  ->  5h={u['fh']}%  sem={u['sd']}%  \"{texto}\"")
    return 0


def diferencia(muestras: list) -> int:
    if not REGISTRO.exists():
        print("No hay marcas todavia. Dejar una con: python config/consumo.py --marcar \"texto\"")
        return 1
    filas = list(csv.DictReader(REGISTRO.open(encoding="utf-8")))
    if not filas or not muestras:
        return 1
    ultima, actual = filas[-1], muestras[-1]
    try:
        d_fh = int(actual["fh"]) - int(ultima["fh_pct"])
        d_sd = int(actual["sd"]) - int(ultima["sd_pct"])
    except (TypeError, ValueError):
        print("No se pudo comparar: faltan datos en la marca o en la telemetria.", file=sys.stderr)
        return 1
    print(f"Desde la marca \"{ultima['marca']}\" ({ultima['momento']}):")
    print(f"  ventana 5 horas   {d_fh:+d} puntos   (ahora {actual['fh']}%)")
    print(f"  ventana semanal   {d_sd:+d} puntos   (ahora {actual['sd']}%)")
    if d_fh < 0 or d_sd < 0:
        print("  (un valor negativo significa que la ventana se reseteo en el medio)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Consumo real del plan Claude")
    p.add_argument("--historial", action="store_true", help="mostrar todas las muestras")
    p.add_argument("--marcar", metavar="TEXTO", help="registrar una marca en el libro de obra")
    p.add_argument("--diferencia", action="store_true", help="consumo desde la ultima marca")
    a = p.parse_args()

    muestras = leer_muestras()
    if not muestras:
        return 1

    if a.marcar:
        return marcar(a.marcar, muestras)
    if a.diferencia:
        return diferencia(muestras)

    estado(muestras)
    resets(muestras)
    tabla(muestras, len(muestras) if a.historial else 12)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
