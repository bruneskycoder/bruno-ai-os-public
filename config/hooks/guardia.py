"""Guardia: bloquea comandos irreversibles antes de que se ejecuten.

Por que existe. El Director decidio mantener bypassPermissions activo, asi que
no hay confirmaciones que frenen nada. Un hook PreToolUse que devuelve codigo 2
SI bloquea la herramienta, independientemente del modo de permisos. Es el unico
porton programatico que le queda a este sistema.

QUE PROTEGE Y QUE NO -- honestidad primero.
Esto protege contra ACCIDENTES: un agente que corre algo destructivo por error,
que fuerza un push, que borra un arbol, que imprime un token. Ese es el riesgo
realista aca.
NO protege contra un atacante decidido: como cualquier control basado en texto,
se evade con variables, codificacion o rutas absolutas. La documentacion oficial
dice lo mismo de las reglas de permisos. Es friccion y registro, no un muro.

Todo lo que pasa queda en logs/guardia.log, tambien lo permitido: el registro
sirve para auditar despues.

Instalar: python config/hooks/instalar.py
Probar:   python config/hooks/probar-guardia.py
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

def _donde_registrar() -> Path:
    """El registro va al repositorio si existe; si no, al lado de este script.

    Este archivo se instala en ~/.claude/guardia.py para que el hook global NO
    dependa de la ruta del repositorio. Si dependiera y la carpeta se moviera,
    Python fallaria con codigo 2 -- que es justo el codigo de BLOQUEAR -- y
    dejaria al Director sin poder ejecutar un solo comando en ningun proyecto.
    """
    repo = Path("<carpeta-del-proyecto>/logs")
    if repo.is_dir():
        return repo / "guardia.log"
    return Path(__file__).resolve().parent / "guardia.log"


REGISTRO = _donde_registrar()

# (patron, motivo). Se evalua sobre el comando tal como viene escrito.
BLOQUEOS = [
    (r"git\s+push\b[^|;&]*\s(--force|-f)\b", "push forzado: reescribe historial publicado"),
    (r"git\s+push\b[^|;&]*--force-with-lease", "push forzado: reescribe historial publicado"),
    (r"git\s+reset\b[^|;&]*--hard", "reset --hard: descarta trabajo sin confirmacion"),
    (r"git\s+clean\b[^|;&]*-[a-z]*f", "git clean -f: borra archivos no versionados"),
    (r"git\s+(commit|merge|rebase)\b[^|;&]*--no-verify", "saltea el hook de secretos"),
    (r"git\s+branch\b[^|;&]*\s-D\b", "borrado forzado de rama"),
    (r"\brm\s+-[a-z]*r[a-z]*f|\brm\s+-[a-z]*f[a-z]*r", "rm -rf: borrado recursivo"),
    (r"Remove-Item\b[^|;&]*-Recurse[^|;&]*-Force", "Remove-Item recursivo y forzado"),
    (r"\bgh\s+repo\s+delete\b", "borra un repositorio en GitHub"),
    (r"\bgh\s+auth\s+token\b", "imprime el token de GitHub en claro"),
    (r"\bgh\s+secret\s+set\b", "escribe un secreto en GitHub"),
    (r"git\s+config\b[^|;&]*--global\b[^|;&]*user\.(name|email)", "cambia la identidad global de git"),
    (r"\bcmdkey\s+/delete", "borra credenciales del Credential Manager"),
    # OJO: 'format' a secas matcheaba --output-format, --format, formato...
    # Un guardia con falsos positivos frena trabajo legitimo y termina siendo
    # peor que no tenerlo. Solo la forma realmente destructiva: format C:
    (r"\bformat\s+[a-zA-Z]:", "formateo de unidad"),
    (r"\b(diskpart|bcdedit)\b", "operacion de disco a nivel sistema"),
]

# Se registran pero no se bloquean: valen como senal de auditoria.
AVISOS = [
    (r"\bpip\s+install\b", "instala paquetes: cambia el entorno"),
    (r"\bwinget\s+install\b", "instala software en la maquina"),
    (r"\bgit\s+push\b", "publica en el remoto"),
    (r"\bcurl\b|\bInvoke-WebRequest\b|\bwget\b", "trafico de red saliente"),
]


def registrar(veredicto: str, comando: str, motivo: str) -> None:
    try:
        REGISTRO.parent.mkdir(parents=True, exist_ok=True)
        momento = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"{momento}\t{veredicto}\t{motivo}\t{comando[:400]}\n"
        with REGISTRO.open("a", encoding="utf-8", newline="\n") as f:
            f.write(linea)
    except OSError:
        # Que no se pueda registrar no puede romper la sesion.
        pass


def main() -> int:
    try:
        datos = json.load(sys.stdin)
    except Exception:
        # Sin entrada legible no se bloquea nada: fallar cerrado aca dejaria la
        # sesion inutilizable ante cualquier cambio de formato.
        return 0

    entrada = datos.get("tool_input") or {}
    comando = entrada.get("command") or ""
    if not isinstance(comando, str) or not comando.strip():
        return 0

    for patron, motivo in BLOQUEOS:
        if re.search(patron, comando, re.IGNORECASE):
            registrar("BLOQUEADO", comando, motivo)
            print(
                f"[guardia] BLOQUEADO: {motivo}\n"
                f"  comando: {comando[:300]}\n"
                f"  Esta accion es irreversible o toca secretos. Si hace falta de verdad,\n"
                f"  el Director tiene que ejecutarla o autorizarla explicitamente.\n"
                f"  No la reintentes reescribiendola para esquivar el guardia.",
                file=sys.stderr,
            )
            return 2  # codigo 2 = bloqueo duro

    for patron, motivo in AVISOS:
        if re.search(patron, comando, re.IGNORECASE):
            registrar("AVISO", comando, motivo)
            return 0

    registrar("ok", comando, "-")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        # Ante cualquier error inesperado, no bloquear: un guardia roto no puede
        # dejar al Director sin poder trabajar.
        raise SystemExit(0)
