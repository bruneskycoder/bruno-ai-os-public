"""Que cuesta, en contexto, la capacidad instalada.

Las descripciones de TODAS las skills disponibles estan siempre en el contexto de
cada sesion. No es una metafora: es un costo fijo que se paga en cada turno,
aunque la skill no se use nunca. Este script lo cuantifica.

Uso:
  python config/auditar-skills.py              resumen por origen
  python config/auditar-skills.py --detalle    una linea por skill
  python config/auditar-skills.py --guardar    escribe artifacts/auditoria-de-skills.md
"""
import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

RAIZ = Path(__file__).resolve().parents[1]
APPDATA = Path(os.environ.get("APPDATA", ""))
BASE = APPDATA / "Claude" / "local-agent-mode-sessions"
CHARS_POR_TOKEN = 3.3


def frontmatter(p: Path) -> dict:
    """Lee name/description del frontmatter YAML sin depender de un parser externo."""
    try:
        txt = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not txt.lstrip("﻿").startswith("---"):
        return {}
    cuerpo = txt.lstrip("﻿").split("---", 2)
    if len(cuerpo) < 3:
        return {}
    campos, clave = {}, None
    for linea in cuerpo[1].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", linea)
        if m:
            clave = m.group(1)
            campos[clave] = m.group(2).strip().strip("\"'")
        elif clave and linea.startswith((" ", "\t")) and campos.get(clave) is not None:
            campos[clave] = (campos[clave] + " " + linea.strip()).strip()
    return campos


def nombres_de_plugins(rpm: Path) -> dict:
    try:
        d = json.loads((rpm / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {p["id"]: p.get("name", p["id"]) for p in d.get("plugins", [])}


def recolectar() -> list:
    filas = []
    if not BASE.is_dir():
        return filas

    # Skills de la cuenta claude.ai
    for skill in BASE.glob("skills-plugin/*/*/skills/*/SKILL.md"):
        fm = frontmatter(skill)
        filas.append({
            "origen": "cuenta claude.ai",
            "nombre": fm.get("name") or skill.parent.name,
            "desc": fm.get("description", ""),
            "peso_dir": sum(f.stat().st_size for f in skill.parent.rglob("*") if f.is_file()),
        })

    # Skills que vienen dentro de plugins
    for rpm in BASE.glob("*/*/rpm"):
        nombres = nombres_de_plugins(rpm)
        for plugin_dir in rpm.glob("plugin_*"):
            nombre_plugin = nombres.get(plugin_dir.name, plugin_dir.name)
            for skill in plugin_dir.rglob("SKILL.md"):
                fm = frontmatter(skill)
                filas.append({
                    "origen": f"plugin: {nombre_plugin}",
                    "nombre": fm.get("name") or skill.parent.name,
                    "desc": fm.get("description", ""),
                    "peso_dir": sum(f.stat().st_size for f in skill.parent.rglob("*") if f.is_file()),
                })
    return filas


def informe(filas: list, detalle: bool, fn=print) -> None:
    if not filas:
        fn("No se encontraron skills. Revisar que la app de Claude este instalada.")
        return

    por_origen = {}
    for f in filas:
        por_origen.setdefault(f["origen"], []).append(f)

    total_chars = sum(len(f["desc"]) for f in filas)
    total_tokens = int(total_chars / CHARS_POR_TOKEN)

    fn("COSTO FIJO DE CONTEXTO POR SKILLS INSTALADAS")
    fn(f"  skills detectadas          {len(filas)}")
    fn(f"  caracteres de descripcion  {total_chars:,}")
    fn(f"  ~tokens en CADA sesion     {total_tokens:,}")
    fn("")
    fn("POR ORIGEN")
    fn(f"  {'origen':<34}{'skills':>7}{'~tokens':>10}   sin descripcion")
    for origen in sorted(por_origen, key=lambda o: -sum(len(f["desc"]) for f in por_origen[o])):
        g = por_origen[origen]
        t = int(sum(len(f["desc"]) for f in g) / CHARS_POR_TOKEN)
        vacias = sum(1 for f in g if not f["desc"])
        fn(f"  {origen:<34}{len(g):>7}{t:>10}   {vacias if vacias else '-'}")

    if detalle:
        fn("\nDETALLE")
        for f in sorted(filas, key=lambda x: -len(x["desc"])):
            t = int(len(f["desc"]) / CHARS_POR_TOKEN)
            fn(f"  {t:>5} tok  {f['nombre']:<34} {f['origen']}")

    fn(f"\n  Metodo: {CHARS_POR_TOKEN} caracteres por token (estimacion declarada).")
    fn("  Solo se cuenta la DESCRIPCION, que es lo que esta siempre en contexto.")
    fn("  El cuerpo del SKILL.md se carga solo cuando la skill se activa.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Auditoria de skills instaladas")
    ap.add_argument("--detalle", action="store_true")
    ap.add_argument("--guardar", action="store_true")
    a = ap.parse_args()

    filas = recolectar()
    if not a.guardar:
        informe(filas, a.detalle)
        return 0

    lineas = []
    informe(filas, True, lineas.append)
    destino = RAIZ / "artifacts" / "auditoria-de-skills.md"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        f"""# Auditoria de skills instaladas

| Campo | Valor |
|---|---|
| Proposito | Cuantificar el costo fijo de contexto de la capacidad instalada |
| Fecha | {date.today():%Y-%m-%d} |
| Version | 1.0 |
| Clasificacion | INTERNO |
| Fuentes | Archivos SKILL.md en el directorio de datos de la app |
| Estado | PARTIALLY VERIFIED — conteo exacto, conversion a tokens estimada |
| Relaciones | COST_MODEL.md · .claude/rules/escritura-de-skills.md |

Generado por `python config/auditar-skills.py --guardar`.

```
{chr(10).join(lineas)}
```
""",
        encoding="utf-8",
        newline="\n",
    )
    print("\n".join(lineas))
    print("\nguardado: artifacts/auditoria-de-skills.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
