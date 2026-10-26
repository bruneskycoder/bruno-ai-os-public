"""Verifica que las skills y los subagentes del repositorio cumplan las reglas de la casa.

No es un linter de estilo. Chequea dos cosas que, si se rompen, rompen algo real:

  1. Formato: lo que la especificacion de Agent Skills exige para que una skill
     cargue y dispare (nombre valido, carpeta coincidente, sin BOM, LF).
  2. SEPARACION DE ROLES: que ningun subagente tenga a la vez herramientas de
     escritura o shell Y herramientas de navegacion web. Ese es el control de
     seguridad principal del sistema (ADR-0006) y con bypassPermissions activo
     es el unico que queda. Si se rompe, hay que enterarse aca y no despues.

Uso:  python tests/validar-componentes.py
Salida: 0 si todo pasa, 1 si hay algun error.
"""
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
ESCRITURA = {"Write", "Edit", "Bash", "NotebookEdit"}
EXTERNAS = {"WebSearch", "WebFetch"}
RE_NOMBRE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errores = []
avisos = []


def frontmatter(p: Path):
    crudo = p.read_bytes()
    txt = crudo.decode("utf-8", errors="replace")
    if crudo[:3] == b"\xef\xbb\xbf":
        errores.append(f"{p}: tiene BOM UTF-8; rompe el parseo del frontmatter")
        txt = txt.lstrip("﻿")
    if b"\r\n" in crudo:
        avisos.append(f"{p}: tiene finales de linea CRLF")
    if not txt.startswith("---"):
        errores.append(f"{p}: no empieza con frontmatter")
        return {}, txt
    partes = txt.split("---", 2)
    if len(partes) < 3:
        errores.append(f"{p}: frontmatter sin cerrar")
        return {}, txt
    campos, clave = {}, None
    for linea in partes[1].splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", linea)
        if m:
            clave = m.group(1)
            campos[clave] = m.group(2).strip().strip("\"'")
        elif clave and linea.startswith((" ", "\t")):
            campos[clave] = (campos[clave] + " " + linea.strip()).strip()
    return campos, partes[2]


def revisar_skills():
    dir_skills = RAIZ / ".claude" / "skills"
    if not dir_skills.is_dir():
        avisos.append("no hay .claude/skills/")
        return 0
    n = 0
    for skill in sorted(dir_skills.glob("*/SKILL.md")):
        n += 1
        campos, cuerpo = frontmatter(skill)
        carpeta = skill.parent.name
        nombre = campos.get("name", "")
        desc = campos.get("description", "")
        if nombre != carpeta:
            errores.append(f"{skill}: name '{nombre}' no coincide con la carpeta '{carpeta}'")
        if not RE_NOMBRE.fullmatch(nombre) or len(nombre) > 64:
            errores.append(f"{skill}: name '{nombre}' invalido (minusculas, digitos y guiones simples, max 64)")
        if not desc:
            errores.append(f"{skill}: sin description; sin ella la skill no dispara nunca")
        elif len(desc) > 1024:
            errores.append(f"{skill}: description de {len(desc)} chars, excede 1024")
        if len(cuerpo.splitlines()) > 500:
            avisos.append(f"{skill}: cuerpo de {len(cuerpo.splitlines())} lineas, supera las 500 recomendadas")
    return n


def revisar_agentes():
    dir_agentes = RAIZ / ".claude" / "agents"
    if not dir_agentes.is_dir():
        avisos.append("no hay .claude/agents/")
        return 0
    n = 0
    for agente in sorted(dir_agentes.glob("*.md")):
        n += 1
        campos, _ = frontmatter(agente)
        nombre = campos.get("name", "")
        if nombre != agente.stem:
            errores.append(f"{agente}: name '{nombre}' no coincide con el archivo '{agente.stem}'")
        if not campos.get("description"):
            errores.append(f"{agente}: sin description")

        tools = {t.strip() for t in campos.get("tools", "").split(",") if t.strip()}
        if not tools:
            errores.append(
                f"{agente}: sin 'tools' declarado. Hereda TODAS las herramientas y "
                f"rompe la separacion de roles del ADR-0006"
            )
            continue
        escribe = tools & ESCRITURA
        navega = tools & EXTERNAS
        if escribe and navega:
            errores.append(
                f"{agente}: VIOLA LA SEPARACION DE ROLES. Tiene herramientas de "
                f"escritura/shell ({', '.join(sorted(escribe))}) y de navegacion "
                f"({', '.join(sorted(navega))}) al mismo tiempo. Un agente que lee "
                f"contenido no confiable no puede tener con que actuar."
            )
    return n


def main() -> int:
    ns = revisar_skills()
    na = revisar_agentes()
    print(f"revisadas {ns} skills y {na} subagentes")
    for a in avisos:
        print(f"  AVISO  {a}")
    for e in errores:
        print(f"  ERROR  {e}", file=sys.stderr)
    if errores:
        print(f"\nFALLO: {len(errores)} error(es).", file=sys.stderr)
        return 1
    print("OK: formato valido y separacion de roles intacta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
