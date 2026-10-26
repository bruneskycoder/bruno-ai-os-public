"""Cuanto cuesta retomar el trabajo: handoff contra reconstruir todo el contexto.

La Fase 3 se apoya en una afirmacion que seria facil dar por buena sin probar:
"leer un handoff sale mucho mas barato que releer la documentacion". Este script
la mide en vez de suponerla.

Metodo: cuenta caracteres reales de cada archivo y los convierte a tokens con un
ratio declarado. El ratio es una aproximacion; la RELACION entre ambas rutas es
exacta, y es lo que decide.

Uso:
  python config/costo-de-retomar.py
  python config/costo-de-retomar.py --guardar   escribe artifacts/costo-de-retomar.md
"""
import argparse
import sys
from datetime import date
from pathlib import Path

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

RAIZ = Path(__file__).resolve().parents[1]

# Prosa en espanol con el tokenizador de los modelos 4.7+, que produce ~30% mas
# tokens que el anterior. Es una estimacion declarada, no una medicion de la API.
CHARS_POR_TOKEN = 3.3

# Lo que habria que leer para reconstruir el contexto sin handoff.
RECONSTRUIR = [
    "AGENTS.md",
    "SYSTEM_AUDIT.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "PROGRESS.md",
    "COST_MODEL.md",
    "docs/security/THREAT_MODEL.md",
    "docs/research/FINDINGS.md",
    "memory/README.md",
]
RETOMAR = ["memory/HANDOFF.md"]


def medir(rutas):
    filas, total = [], 0
    for r in rutas:
        p = RAIZ / r
        if not p.is_file():
            filas.append((r, None, None))
            continue
        chars = len(p.read_text(encoding="utf-8", errors="replace"))
        tokens = int(chars / CHARS_POR_TOKEN)
        filas.append((r, chars, tokens))
        total += tokens
    return filas, total


def render(fn=print) -> int:
    f_rec, t_rec = medir(RECONSTRUIR)
    f_ret, t_ret = medir(RETOMAR)

    if t_ret == 0:
        fn("No hay HANDOFF.md. Sin handoff, la unica opcion es reconstruir.")
        return 1

    fn("RUTA A — reconstruir el contexto leyendo la documentacion")
    for r, c, t in f_rec:
        fn(f"  {r:<34} {'(falta)' if c is None else f'{c:>7,} chars  ~{t:>6,} tokens'}")
    fn(f"  {'TOTAL':<34} {'':>7}         ~{t_rec:>6,} tokens")

    fn("\nRUTA B — retomar leyendo el handoff")
    for r, c, t in f_ret:
        fn(f"  {r:<34} {'(falta)' if c is None else f'{c:>7,} chars  ~{t:>6,} tokens'}")
    fn(f"  {'TOTAL':<34} {'':>7}         ~{t_ret:>6,} tokens")

    factor = t_rec / t_ret
    ahorro = t_rec - t_ret
    # 1% de la ventana semanal ~ 80.000 tokens (COST_MODEL.md §4),
    # o sea que el ahorro en tokens dividido 80.000 YA da el porcentaje.
    TOKENS_POR_PUNTO_SEMANAL = 80_000
    pct = ahorro / TOKENS_POR_PUNTO_SEMANAL

    fn(f"\nRESULTADO")
    fn(f"  El handoff cuesta {factor:.0f} veces menos que reconstruir.")
    fn(f"  Ahorro por retomada: ~{ahorro:,} tokens  (~{pct:.2f}% de la ventana semanal)")
    fn(f"  Cada 10 retomadas: ~{ahorro * 10:,} tokens  (~{pct * 10:.1f}% del semanal)")
    fn(f"  Cada 50 retomadas: ~{ahorro * 50:,} tokens  (~{pct * 50:.0f}% del semanal)")
    fn(f"\n  Metodo: {CHARS_POR_TOKEN} caracteres por token (estimacion declarada).")
    fn("  Los conteos de caracteres son exactos; la relacion entre rutas no depende del ratio.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Costo de retomar el trabajo")
    ap.add_argument("--guardar", action="store_true", help="escribir artifacts/costo-de-retomar.md")
    a = ap.parse_args()

    if not a.guardar:
        return render()

    lineas = []
    codigo = render(lineas.append)
    destino = RAIZ / "artifacts" / "costo-de-retomar.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    cuerpo = "\n".join(lineas)
    destino.write_text(
        f"""# Costo de retomar el trabajo

| Campo | Valor |
|---|---|
| Proposito | Medir si el handoff realmente ahorra contexto frente a reconstruirlo |
| Fecha | {date.today():%Y-%m-%d} |
| Version | 1.0 |
| Clasificacion | INTERNO |
| Fuentes | Conteo de caracteres del propio repositorio |
| Estado | PARTIALLY VERIFIED — conteo exacto, conversion a tokens estimada |
| Relaciones | ADR-0003 · COST_MODEL.md · memory/README.md |

Generado por `python config/costo-de-retomar.py --guardar`.

```
{cuerpo}
```
""",
        encoding="utf-8",
        newline="\n",
    )
    print(cuerpo)
    print(f"\nguardado: artifacts/costo-de-retomar.md")
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
