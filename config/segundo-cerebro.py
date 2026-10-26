"""Segundo cerebro: Gemini para trabajo con datos NO personales.

Preparado, no instalado. Ver docs/decisions/ADR-0008-segundo-cerebro-condicionado.md

Existe para un problema concreto y medido: cuando el plan Claude Pro se satura,
la semana se frena. Esto da una valvula de escape para trabajo de lectura
publica -- y SOLO para eso.

    REGLA QUE NO SE NEGOCIA
    Los terminos del tier gratuito de la API de Gemini dicen que Google usa los
    prompts para mejorar sus productos y que revisores humanos pueden leerlos.
    Por lo tanto: datos PERSONAL (finanzas, legales, correo, salud, campo,
    credenciales) NUNCA salen por aca. Sin clasificacion declarada, se asume
    PERSONAL y no sale.

Uso:
    python config/segundo-cerebro.py --estado          que hay instalado
    python config/segundo-cerebro.py --instalar        instala llm + llm-gemini
    python config/segundo-cerebro.py --guardar-clave   guarda la clave en el
                                                       Credential Manager
    python config/segundo-cerebro.py --probar          verifica de punta a punta
"""
import argparse
import getpass
import os
import shutil
import subprocess
import sys

SERVICIO = "bruno-ai-os"
USUARIO = "gemini-api-key"
PAQUETES = ["llm==0.35", "llm-gemini==0.34", "keyring"]
# Google retira modelos para cuentas nuevas sin avisar en la documentacion.
# El 2026-09-15, gemini-2.5-flash respondio "no longer available to new users"
# y el propio error recomendo este. Ver los disponibles con: llm models
MODELO = "gemini-3.6-flash"

AVISO = """
  RECORDATORIO DE CLASIFICACION DE DATOS
  Todo lo que mandes por aca lo puede usar Google para mejorar sus productos, y
  revisores humanos pueden leerlo. Solo datos PUBLICO, o INTERNO anonimizado con
  decision explicita del Director. Nunca PERSONAL.
"""


def hay(mod: str) -> bool:
    try:
        __import__(mod)
        return True
    except ImportError:
        return False


def limpiar(clave: str) -> str:
    """Saca caracteres de control y espacios de una clave pegada.

    Motivo real, encontrado el 2026-09-15: al pegar con Ctrl+V en un campo de
    contraseña oculto de la consola de Windows, la terminal captura las TECLAS
    (\\x16 = Ctrl+V, \\x1a = Ctrl+Z) en vez de pegar el contenido. La clave
    quedaba guardada con basura invisible adelante y Google devolvia un 400 de
    HTML que no decia nada util. Un .strip() no alcanza: no toca los caracteres
    de control del medio.
    """
    return "".join(c for c in clave if c.isprintable() and not c.isspace())


def leer_clave():
    if not hay("keyring"):
        return None
    import keyring
    try:
        bruta = keyring.get_password(SERVICIO, USUARIO)
    except Exception:
        return None
    return limpiar(bruta) if bruta else None


def estado() -> int:
    print("ESTADO DEL SEGUNDO CEREBRO")
    print()
    llm_bin = shutil.which("llm")
    print(f"  llm instalado        {'si -> ' + llm_bin if llm_bin else 'NO'}")
    print(f"  keyring disponible   {'si' if hay('keyring') else 'NO'}")
    clave = leer_clave()
    print(f"  clave guardada       {'si (no se muestra)' if clave else 'NO'}")
    print()
    if not llm_bin:
        print("  Siguiente paso: python config/segundo-cerebro.py --instalar")
    elif not clave:
        print("  Siguiente paso: python config/segundo-cerebro.py --guardar-clave")
    else:
        print("  Siguiente paso: python config/segundo-cerebro.py --probar")
    return 0


def instalar() -> int:
    print("Se van a instalar 34 paquetes, todos wheels precompilados:")
    print(f"  {', '.join(PAQUETES)}")
    print()
    print("Esto cambia el entorno Python del sistema.")
    print("Revertir con: pip uninstall llm llm-gemini")
    print()
    r = subprocess.run([sys.executable, "-m", "pip", "install", *PAQUETES])
    if r.returncode != 0:
        print("FALLO la instalacion.", file=sys.stderr)
        return 1
    print()
    print("Instalado. Siguiente: python config/segundo-cerebro.py --guardar-clave")
    return 0


def guardar_clave() -> int:
    if not hay("keyring"):
        print("Falta keyring. Correr primero --instalar", file=sys.stderr)
        return 1
    import keyring
    print("Pega la clave de Google AI Studio.")
    print("No se muestra en pantalla ni queda en el historial de la terminal.")
    print("Se guarda en el Credential Manager de Windows, nunca en un archivo del repositorio.")
    print()
    print("  IMPORTANTE en Windows: pega con CLIC DERECHO, no con Ctrl+V.")
    print("  En un campo oculto, Ctrl+V se guarda como caracter de control y")
    print("  rompe la clave sin que se note.")
    print()
    bruta = getpass.getpass("  clave: ")
    clave = limpiar(bruta)
    if not clave:
        print("Vacia: no se guardo nada.", file=sys.stderr)
        return 1
    if len(clave) != len(bruta):
        print(f"  (se limpiaron {len(bruta) - len(clave)} caracteres invisibles del pegado)")
    keyring.set_password(SERVICIO, USUARIO, clave)
    print()
    print(f"Guardada: {len(clave)} caracteres. Siguiente: python config/segundo-cerebro.py --probar")
    return 0


def probar() -> int:
    clave = leer_clave()
    if not clave:
        print("No hay clave guardada. Correr --guardar-clave", file=sys.stderr)
        return 1
    if not shutil.which("llm"):
        print("Falta llm. Correr --instalar", file=sys.stderr)
        return 1

    print(AVISO)
    print(f"  probando {MODELO} con un prompt publico...")
    entorno = dict(os.environ)
    entorno["LLM_GEMINI_KEY"] = clave
    r = subprocess.run(
        ["llm", "-m", MODELO, "Responde solamente con la palabra: ok"],
        capture_output=True, text=True, env=entorno,
    )
    # Redaccion en TODOS los caminos de salida, no solo en los de error.
    # Leccion del 2026-09-15: un script de diagnostico redactaba la clave en la
    # rama de HTTPError pero no en la rama de excepcion generica, y el mensaje
    # la imprimio entera. Hubo que rotar la clave. La redaccion va una sola vez,
    # sobre todo lo que se imprime.
    salida = (r.stdout or r.stderr).strip().replace(clave, "[CLAVE]")
    print(f"  respuesta: {salida[:200]}")

    # No alcanza con el codigo de salida: hay herramientas que devuelven 0 con error.
    ok = r.returncode == 0 and "ok" in salida.lower() and "error" not in salida.lower()
    print()
    if ok:
        print("  OK: el segundo cerebro responde.")
        print("  Falta lo importante: demostrar VENTAJA MEDIBLE en una tarea real")
        print("  (ADR-0008). Si no la muestra, no se integra.")
    else:
        print("  FALLO: revisar la clave o el nombre del modelo.")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Segundo cerebro (Gemini) para datos no personales")
    ap.add_argument("--estado", action="store_true")
    ap.add_argument("--instalar", action="store_true")
    ap.add_argument("--guardar-clave", dest="guardar", action="store_true")
    ap.add_argument("--probar", action="store_true")
    a = ap.parse_args()
    if a.instalar:
        return instalar()
    if a.guardar:
        return guardar_clave()
    if a.probar:
        return probar()
    return estado()


if __name__ == "__main__":
    raise SystemExit(main())
