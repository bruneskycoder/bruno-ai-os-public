"""Prueba el portero del relevo: que diga NO cuando hay que decir NO.

Por que existe. `config/relevo.py` decide sola, de madrugada y sin nadie mirando,
si una sesion automatica arranca a gastar la ventana del plan. El unico modo de
falla caro es que diga SI cuando no corresponde: despierta, gasta el arranque de
sesion y se muere contra el limite. Un error al reves solo posterga trabajo.

Por eso la mayoria de los casos de abajo son **negativos**: comprueban que el
portero frena. Una prueba que solo confirma que el camino feliz funciona no
prueba nada -- es la misma regla con la que se valido la separacion de roles de
la Fase 6.

Metodo: se carga el modulo y se le cambian las tres rutas que lee (testigo,
telemetria, bitacora) por archivos temporales armados a proposito. No toca el
repositorio ni la telemetria real.

Uso:  python tests/probar-relevo.py        (codigo 0 si pasan todas)
"""
import csv
import importlib.util
import json
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

RAIZ = Path(__file__).resolve().parents[1]


def cargar():
    ruta = RAIZ / "config" / "relevo.py"
    spec = importlib.util.spec_from_file_location("relevo", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


TESTIGO = """# HANDOFF.md

| Campo | Valor |
|---|---|
| Relevo | {modo} |
| Techo de arranque | {arranque} % |
| Techo de gasto | 45 % |
| Tope semanal | {semanal} % |
| Actualizado | 2026-09-17 |

## Proximo paso

1. Medir el presupuesto.

## Estado

Cerrado.
"""


def escribir_testigo(carpeta, modo="ACTIVO", arranque=35, semanal=90):
    ruta = carpeta / "HANDOFF.md"
    ruta.write_text(TESTIGO.format(modo=modo, arranque=arranque, semanal=semanal),
                    encoding="utf-8")
    return ruta


def escribir_telemetria(carpeta, fh, sd, antiguedad_h=0.0):
    cuando = datetime.now() - timedelta(hours=antiguedad_h)
    ruta = carpeta / "plan-usage-history.json"
    ruta.write_text(json.dumps({"version": 1, "samples": [
        {"t": int((cuando - timedelta(hours=1)).timestamp() * 1000), "u": {"fh": 1, "sd": 1}},
        {"t": int(cuando.timestamp() * 1000), "u": {"fh": fh, "sd": sd}},
    ]}), encoding="utf-8")
    return ruta


def escribir_bitacora(carpeta, horas_atras):
    ruta = carpeta / "relevo.csv"
    with ruta.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cuando", "decision", "fh_pct", "sd_pct", "nota"])
        w.writerow([(datetime.now().astimezone() - timedelta(hours=horas_atras))
                    .isoformat(timespec="seconds"), "SI", 2, 40, "relevo anterior"])
    return ruta


def main() -> int:
    m = cargar()
    fallas = []

    def caso(nombre, esperado, testigo=None, telemetria=(2, 40, 0.0), bitacora=None,
             verificar=None):
        """Arma un escenario y comprueba la decision. esperado: True = arranca."""
        with tempfile.TemporaryDirectory() as tmp:
            carpeta = Path(tmp)
            m.HANDOFF = (escribir_testigo(carpeta, **testigo) if testigo is not None
                         else carpeta / "no-existe.md")
            m.TELEMETRIA = (escribir_telemetria(carpeta, *telemetria) if telemetria
                            else carpeta / "no-existe.json")
            m.BITACORA = (escribir_bitacora(carpeta, bitacora) if bitacora is not None
                          else carpeta / "sin-bitacora.csv")
            d = m.decidir()

        bien = d["relevo"] is esperado
        if bien and verificar is not None:
            bien = d["verificar"] is verificar
        print(("  OK   " if bien else "  FALLA") + "  " + nombre)
        print("         -> " + ("SI" if d["relevo"] else "NO") + ": " + d["motivo"])
        if not bien:
            fallas.append(nombre)

    print("Portero del relevo -- lo que tiene que frenar\n")
    caso("sin testigo no arranca (nadie declaro trabajo)", False, testigo=None)
    caso("el Director lo dejo en PAUSADO", False, testigo={"modo": "PAUSADO"})
    caso("el semanal esta al 92 % (tope 90 %)", False, testigo={}, telemetria=(2, 92, 0.0))
    caso("la ventana de 5 h ya va 80 % (techo 35 %)", False, testigo={}, telemetria=(80, 40, 0.0))
    caso("ya hubo relevo hace 1 h", False, testigo={}, bitacora=1)

    print("\nLo que tiene que dejar pasar\n")
    caso("ventana recien reiniciada, semanal con margen", True, testigo={})
    caso("relevo viejo (9 h) no bloquea", True, testigo={}, bitacora=9)
    caso("telemetria vieja: pasa, pero manda verificar", True, testigo={},
         telemetria=(2, 40, 6.0), verificar=True)
    caso("sin telemetria legible: pasa, pero manda verificar", True, testigo={},
         telemetria=None, verificar=True)

    print("\nLo que decide el Director desde la tabla del testigo\n")
    caso("con el techo en 60 %, una ventana al 50 % arranca", True,
         testigo={"arranque": 60}, telemetria=(50, 40, 0.0))
    caso("con el techo en 10 %, esa misma ventana no arranca", False,
         testigo={"arranque": 10}, telemetria=(50, 40, 0.0))

    if fallas:
        print("\nFALLARON " + str(len(fallas)) + " casos: " + ", ".join(fallas))
        return 1
    print("\nTodos los casos pasan. El portero frena donde tiene que frenar.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
