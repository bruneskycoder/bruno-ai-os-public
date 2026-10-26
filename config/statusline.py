"""Status line de Bruno AI OS: el consumo del plan, siempre a la vista.

Claude Code invoca este script en cada turno y le pasa por stdin un JSON con el
estado de la sesion. Lo unico que importa aca es el bloque rate_limits.

Instalar: ya queda configurado en .claude/settings.json de este repositorio.
Probar:   python config/statusline.py < tests/statusline-ejemplo.json

Reglas de esta casa que aplican:
  - Nunca romper. Si algo falta o viene raro, se degrada y sigue: una status line
    que falla arruina cada turno de la sesion.
  - Nada de jq: el JSON se parsea con Python.
  - Salida en una sola linea.
"""
import json
import sys
from datetime import datetime, timezone

# Critico: si la status line no puede codificar su salida, se rompe en CADA turno.
# No se depende de PYTHONIOENCODING.
for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# Colores ANSI. El terminal de Claude Code los interpreta.
GRIS = "\033[90m"
VERDE = "\033[32m"
AMARILLO = "\033[33m"
ROJO = "\033[31m"
NEGRITA = "\033[1m"
FIN = "\033[0m"

ANCHO_BARRA = 10


def color_por_uso(pct: float) -> str:
    if pct >= 80:
        return ROJO
    if pct >= 50:
        return AMARILLO
    return VERDE


def barra(pct: float) -> str:
    pct = max(0.0, min(100.0, pct))
    llenos = int(round(pct / 100 * ANCHO_BARRA))
    return "▓" * llenos + "░" * (ANCHO_BARRA - llenos)


def medidor(etiqueta: str, bloque: dict) -> str:
    """Devuelve algo como:  5h ▓▓▓░░░░░░░ 32%"""
    if not isinstance(bloque, dict):
        return ""
    pct = bloque.get("used_percentage")
    if pct is None:
        return ""
    try:
        pct = float(pct)
    except (TypeError, ValueError):
        return ""
    c = color_por_uso(pct)
    texto = f"{GRIS}{etiqueta}{FIN} {c}{barra(pct)} {pct:.0f}%{FIN}"

    # Cuando queda poco, importa mas cuando se libera que cuanto se uso.
    if pct >= 80:
        cuando = reset_legible(bloque.get("resets_at"))
        if cuando:
            texto += f"{GRIS}→{cuando}{FIN}"
    return texto


def reset_legible(epoch) -> str:
    if epoch is None:
        return ""
    try:
        t = datetime.fromtimestamp(float(epoch), timezone.utc).astimezone()
    except (TypeError, ValueError, OSError):
        return ""
    ahora = datetime.now(timezone.utc).astimezone()
    faltan = (t - ahora).total_seconds()
    if faltan <= 0:
        return "ya"
    horas, minutos = divmod(int(faltan // 60), 60)
    return f"{horas}h{minutos:02d}m" if horas else f"{minutos}m"


def main() -> int:
    try:
        datos = json.load(sys.stdin)
    except Exception:
        # Sin datos utiles no hay nada que mostrar, pero tampoco se rompe nada.
        print(f"{GRIS}bruno-ai-os{FIN}")
        return 0

    partes = []

    modelo = (datos.get("model") or {}).get("display_name")
    if modelo:
        partes.append(f"{NEGRITA}{modelo}{FIN}")

    limites = datos.get("rate_limits") or {}
    for etiqueta, clave in (("5h", "five_hour"), ("sem", "seven_day")):
        m = medidor(etiqueta, limites.get(clave))
        if m:
            partes.append(m)

    if not limites:
        partes.append(f"{GRIS}(sin datos de limite){FIN}")

    print(f" {GRIS}·{FIN} ".join(partes) if partes else f"{GRIS}bruno-ai-os{FIN}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # Ultima red de seguridad: jamas dejar que un error corte la sesion.
        print(f"{GRIS}bruno-ai-os{FIN}")
