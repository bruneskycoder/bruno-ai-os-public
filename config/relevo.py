"""El relevo: decide si corresponde retomar el trabajo, antes de gastar un token.

El plan es Pro y la ventana de 5 horas se satura. La pregunta "se puede seguir
trabajando?" no se le puede hacer a un modelo: contestarla ya costaria parte de
lo que se quiere cuidar. Este script la contesta gratis, leyendo la telemetria
que la app ya escribe (la misma fuente que config/consumo.py) y el testigo que
dejo la sesion anterior (HANDOFF.md).

Decide con cinco reglas, en este orden:
  1. Nadie dejo testigo         no hay HANDOFF.md        -> NO
  2. Interruptor del Director   HANDOFF.md dice PAUSADO   -> NO
  3. Semanal casi agotado       sd >= tope semanal        -> NO
  4. Ventana de 5 h ya empezada fh >  techo de arranque   -> NO (ese consumo es del Director)
  5. Relevo demasiado reciente  ultimo SI hace < 4 h      -> NO

Codigos de salida:  0 = SI, hay relevo    10 = NO, no corresponde

Uso:
  python config/relevo.py                  decide y muestra el testigo
  python config/relevo.py --json           la misma decision, legible por maquina
  python config/relevo.py --registrar TXT  deja la marca del relevo en logs/relevo.csv
"""
import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

RAIZ = Path(__file__).resolve().parents[1]
# Un solo testigo para todo el repositorio: el de memory/, que existe desde la
# Fase 1 y es el que nombran CLAUDE.md y memory/README.md. La version original
# de este script leia un HANDOFF.md en la raiz y creo un duplicado (ADR-0013).
HANDOFF = RAIZ / "memory" / "HANDOFF.md"
BITACORA = RAIZ / "logs" / "relevo.csv"
TELEMETRIA = Path(os.environ.get("APPDATA", "")) / "Claude" / "plan-usage-history.json"

TECHO_ARRANQUE = 35   # % de la ventana de 5 h por encima del cual no se arranca
TECHO_GASTO = 45      # % de la ventana de 5 h donde el relevo corta y devuelve el turno
# El tope original era 90: el relevo seguia arrancando sesiones hasta dejarle al
# Director el 10 % de su semana. La restriccion que deja a Bruno sin Claude es la
# ventana SEMANAL, no la de 5 h; cada ventana de 5 h que el relevo usa de noche es
# presupuesto que le saca de dia. 40 deja la mayor parte de la semana para el.
TOPE_SEMANAL = 40     # % del semanal por encima del cual no se arranca nunca
HORAS_ENTRE_RELEVOS = 4
MUESTRA_VIEJA_H = 3   # telemetria mas vieja que esto no se cree


def ultima_muestra() -> dict:
    """Ultimo par (fh, sd) que la app escribio. {} si no hay lectura utilizable."""
    try:
        crudo = json.loads(TELEMETRIA.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if isinstance(crudo, list):
        filas = crudo
    elif isinstance(crudo, dict):
        filas = crudo.get("history") or crudo.get("samples") or []
    else:
        filas = []
    for x in reversed(filas):
        if not isinstance(x, dict):
            continue
        u = x.get("u") or x
        if u.get("fh") is None and u.get("sd") is None:
            continue
        try:
            cuando = datetime.fromtimestamp(x["t"] / 1000, tz=timezone.utc).astimezone()
        except (KeyError, TypeError, ValueError, OSError):
            continue
        return {"cuando": cuando, "fh": u.get("fh"), "sd": u.get("sd")}
    return {}


def testigo() -> dict:
    """Lee HANDOFF.md: interruptor, techos y el proximo paso escrito."""
    if not HANDOFF.exists():
        return {"existe": False, "modo": "SIN TESTIGO", "proximo": "", "techos": {}}
    texto = HANDOFF.read_text(encoding="utf-8", errors="replace")

    def campo(nombre, defecto=None):
        m = re.search(r"^\|\s*" + nombre + r"\s*\|\s*([^|]+?)\s*\|", texto, re.M | re.I)
        return m.group(1).strip() if m else defecto

    def numero(nombre, defecto):
        m = re.search(r"\d+", campo(nombre) or "")
        return int(m.group()) if m else defecto

    seccion = re.search(r"^##\s*Pr[oó]ximo paso\s*$(.*?)(?=^##\s|\Z)", texto, re.M | re.S)
    return {
        "existe": True,
        "modo": (campo("Relevo", "ACTIVO") or "ACTIVO").upper(),
        "proximo": seccion.group(1).strip() if seccion else "",
        "actualizado": campo("Actualizado", "sin fecha"),
        "techos": {
            "arranque": numero("Techo de arranque", TECHO_ARRANQUE),
            "gasto": numero("Techo de gasto", TECHO_GASTO),
            "semanal": numero("Tope semanal", TOPE_SEMANAL),
        },
    }


def ultimo_relevo():
    """Cuando fue el ultimo relevo que si arranco. None si no hubo ninguno."""
    if not BITACORA.exists():
        return None
    try:
        with BITACORA.open(encoding="utf-8", newline="") as f:
            filas = list(csv.DictReader(f))
    except OSError:
        return None
    for fila in reversed(filas):
        if (fila.get("decision") or "").upper() != "SI":
            continue
        try:
            return datetime.fromisoformat(fila["cuando"])
        except (ValueError, KeyError, TypeError):
            continue
    return None


def decidir() -> dict:
    t = testigo()
    m = ultima_muestra()
    techos = t["techos"] or {}
    arranque = techos.get("arranque", TECHO_ARRANQUE)
    tope_semanal = techos.get("semanal", TOPE_SEMANAL)
    ahora = datetime.now().astimezone()

    fh = m.get("fh")
    sd = m.get("sd")
    edad_h = (ahora - m["cuando"]).total_seconds() / 3600 if m else None

    base = {"fh": fh, "sd": sd, "modo": t["modo"], "proximo": t["proximo"],
            "techos": techos, "actualizado": t.get("actualizado")}

    def no(motivo):
        return dict(base, relevo=False, verificar=False, motivo=motivo)

    def si(motivo, verificar=False):
        return dict(base, relevo=True, verificar=verificar, motivo=motivo)

    if not t["existe"]:
        return no("no hay HANDOFF.md: nadie dejo testigo, no hay trabajo declarado que retomar")
    if t["modo"].startswith("PAUS"):
        return no("el Director dejo el relevo en PAUSADO en HANDOFF.md")
    if sd is not None and sd >= tope_semanal:
        return no("el semanal va " + str(sd) + "% (tope " + str(tope_semanal) +
                  "%): lo que queda es del Director, no mio")
    if fh is None:
        return si("no hay telemetria legible: el limite real sera el freno", verificar=True)
    if edad_h is not None and edad_h > MUESTRA_VIEJA_H:
        return si("telemetria vieja (ultima lectura hace %.1f h)" % edad_h, verificar=True)
    if fh > arranque:
        return no("la ventana de 5 h ya va " + str(fh) + "% (techo de arranque " +
                  str(arranque) + "%): ese consumo es del Director")
    reciente = ultimo_relevo()
    if reciente is not None and (ahora - reciente) < timedelta(hours=HORAS_ENTRE_RELEVOS):
        return no("ya hubo relevo hace %.1f h" % ((ahora - reciente).total_seconds() / 3600))
    return si("ventana de 5 h en " + str(fh) + "% y semanal en " + str(sd) +
              "%: hay con que trabajar")


def registrar(texto: str, d: dict) -> None:
    BITACORA.parent.mkdir(parents=True, exist_ok=True)
    nuevo = not BITACORA.exists()
    with BITACORA.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if nuevo:
            w.writerow(["cuando", "decision", "fh_pct", "sd_pct", "nota"])
        w.writerow([datetime.now().astimezone().isoformat(timespec="seconds"),
                    "SI" if d["relevo"] else "NO", d.get("fh"), d.get("sd"), texto])


def main() -> int:
    p = argparse.ArgumentParser(description="Decide si corresponde retomar el trabajo.")
    p.add_argument("--json", action="store_true", help="salida legible por maquina")
    p.add_argument("--registrar", metavar="TEXTO", help="deja la marca en logs/relevo.csv")
    args = p.parse_args()

    d = decidir()
    if args.registrar is not None:
        registrar(args.registrar, d)

    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0 if d["relevo"] else 10

    print("RELEVO: SI" if d["relevo"] else "RELEVO: NO")
    print("  motivo: " + d["motivo"])
    print("  plan:   5h=" + str(d.get("fh")) + "%   semanal=" + str(d.get("sd")) +
          "%   techo de gasto=" + str(d["techos"].get("gasto", TECHO_GASTO)) + "%")
    if d["relevo"]:
        if d["verificar"]:
            print("  ojo:    confirmar el consumo real antes de trabajar")
        print("\n--- proximo paso escrito en HANDOFF.md (" +
              str(d.get("actualizado")) + ") ---")
        print(d["proximo"] or "(el testigo no declara proximo paso: leer HANDOFF.md entero)")
    return 0 if d["relevo"] else 10


if __name__ == "__main__":
    raise SystemExit(main())
