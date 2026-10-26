"""Mide si las skills del repositorio disparan cuando corresponde.

Por que existe este script y no el harness oficial: `claude plugin eval` esta en
acceso anticipado y esta cuenta no lo tiene. Esto es una version minima y barata
del mismo experimento -- suficiente para responder la unica pregunta que importa:
cuando el Director pide algo que la skill deberia cubrir, la skill se activa?

Metodo: se lanza una sesion headless por caso y se inspecciona el flujo de
eventos buscando una invocacion de Skill. Se limita a pocos turnos para que el
agente no ejecute la tarea entera: alcanza con ver si la eligio.

ADVERTENCIA DE DISENO, documentada por Anthropic y confirmada en la practica:
los agentes solo consultan skills para tareas que EXCEDEN lo que pueden hacer
solos. Un pedido trivial de un paso no dispara nada, por buena que sea la
descripcion. Por eso los casos positivos son pedidos no triviales.

Uso:
  python tests/medir-disparo.py            corre todos los casos
  python tests/medir-disparo.py --caso N   corre solo uno
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]

CANDIDATOS_CLI = [
    Path.home() / "AppData/Local/Microsoft/WinGet/Packages"
    / "Anthropic.ClaudeCode_Microsoft.Winget.Source_8wekyb3d8bbwe" / "claude.exe",
    Path.home() / ".local/bin/claude.exe",
]

# (skill esperada o None, prompt, deberia_disparar)
CASOS = [
    ("checkpoint-de-fase",
     "Termine el trabajo de la fase actual. Cerrala como corresponde y prepara el pedido de autorizacion.",
     True),
    ("investigacion-con-artefacto",
     "Necesito saber que alternativas hay hoy para versionar archivos grandes en git, comparadas entre si, y que me quede documentado.",
     True),
    ("explicar-concepto",
     "No termino de entender por que este sistema usa separacion de roles entre agentes en vez de reglas de permisos. Explicamelo.",
     True),
    (None,
     "Cuantos archivos .md hay en la carpeta docs?",
     False),
    (None,
     "Corregi el error de tipeo 'recuros' por 'recursos' en el README.",
     False),
]


def encontrar_cli():
    for p in CANDIDATOS_CLI:
        if p.is_file():
            return str(p)
    hallado = shutil.which("claude")
    return hallado


def correr(cli: str, prompt: str):
    """Devuelve (skills_invocadas, herramientas, costo_usd, tokens_salida)."""
    r = subprocess.run(
        [cli, "-p", prompt, "--output-format", "stream-json", "--verbose", "--max-turns", "2"],
        cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
        errors="replace", stdin=subprocess.DEVNULL, timeout=300,
    )
    skills, tools, costo, salida = [], [], None, None
    for linea in (r.stdout or "").splitlines():
        linea = linea.strip()
        if not linea.startswith("{"):
            continue
        try:
            e = json.loads(linea)
        except json.JSONDecodeError:
            continue
        for c in ((e.get("message") or {}).get("content") or []):
            if isinstance(c, dict) and c.get("type") == "tool_use":
                nombre = c.get("name", "")
                tools.append(nombre)
                texto = json.dumps(c.get("input") or {}, ensure_ascii=False)
                if nombre == "Skill" or "skill" in nombre.lower():
                    skills.append(texto[:120])
        if e.get("type") == "result":
            costo = e.get("total_cost_usd")
            salida = (e.get("usage") or {}).get("output_tokens")
    return skills, tools, costo, salida


def main() -> int:
    ap = argparse.ArgumentParser(description="Mide el disparo de las skills")
    ap.add_argument("--caso", type=int, help="correr solo el caso N (1-based)")
    a = ap.parse_args()

    cli = encontrar_cli()
    if not cli:
        print("No se encontro el CLI de Claude Code.", file=sys.stderr)
        print("Instalar con: winget install --id Anthropic.ClaudeCode", file=sys.stderr)
        return 1

    casos = CASOS if not a.caso else [CASOS[a.caso - 1]]
    aciertos, total_costo = 0, 0.0

    print(f"Midiendo {len(casos)} caso(s). Cada uno es una sesion headless real.\n")
    for i, (skill, prompt, esperado) in enumerate(casos, 1):
        etiqueta = skill or "(ninguna — no deberia disparar)"
        print(f"{i}. {etiqueta}")
        print(f"   pedido: {prompt[:78]}...")
        try:
            skills, tools, costo, salida = correr(cli, prompt)
        except subprocess.TimeoutExpired:
            print("   FALLO: timeout\n")
            continue
        total_costo += costo or 0
        disparo = bool(skills)
        ok = disparo == esperado
        aciertos += ok
        print(f"   disparo skill: {'SI' if disparo else 'no'}   esperado: {'SI' if esperado else 'no'}   -> {'OK' if ok else 'FALLA'}")
        if skills:
            print(f"   invocacion: {skills[0]}")
        if tools:
            print(f"   herramientas: {', '.join(dict.fromkeys(tools))}")
        print(f"   costo: ${costo:.4f}  salida: {salida} tokens\n" if costo else "")

    print(f"RESULTADO: {aciertos}/{len(casos)} casos correctos")
    print(f"Costo total de la medicion: ${total_costo:.4f}")
    if aciertos < len(casos):
        print("\nUna skill que no dispara es peso muerto: cuesta contexto en cada")
        print("sesion y no aporta nada. Revisar su description o darla de baja.")
    return 0 if aciertos == len(casos) else 1


if __name__ == "__main__":
    raise SystemExit(main())
