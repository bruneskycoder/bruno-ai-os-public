"""Replanteo del disco: la foto que la mudanza nunca tuvo.

Por que existe. La auditoria de organizar_archivos.ps1 dejo tres hallazgos en
estado BLOCKED por una sola razon: el log de la corrida grande se sobrescribio y
NO HAY CONTRA QUE COMPARAR. No se puede saber que se movio, ni si algo se perdio.

Eso ya no se puede reparar para el pasado. Para el futuro si: esto toma una foto
fechada del arbol de archivos -ruta, tamano, fecha, huella- y sabe comparar dos
fotos. Cualquier mudanza posterior queda auditable.

Es el replanteo antes de la excavacion. Se hace una vez y sirve para siempre.

DONDE SE GUARDA, Y POR QUE AHI. Las fotos van a ~/Backups/inventarios/, FUERA
del repositorio. Los nombres de archivo del Director son datos PERSONAL
(AGENTS.md seccion 6): un listado de sus documentos legales, medicos y
financieros no viaja a GitHub, ni siquiera a un repositorio privado.

Uso:
  python config/inventario.py                        foto del Escritorio y Descargas
  python config/inventario.py --listar               fotos existentes
  python config/inventario.py --comparar             ultima foto contra el disco de hoy
  python config/inventario.py --comparar A.json B.json   dos fotos entre si
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

for flujo in (sys.stdout, sys.stderr):
    try:
        flujo.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

DESTINO = Path.home() / "Backups" / "inventarios"
RAICES = [Path.home() / "Desktop", Path.home() / "Downloads"]

# Arriba de esto no se calcula huella: seria lento y el tamano mas la fecha ya
# identifican un instalador de 3 GB con sobrada certeza.
TOPE_HUELLA = 200 * 1024 * 1024

# Carpetas que no aportan nada a un inventario de documentos personales.
IGNORAR = {".git", "node_modules", "__pycache__", ".venv", "venv", ".claude"}


def huella(f: Path) -> str:
    h = hashlib.sha256()
    try:
        with f.open("rb") as fh:
            for bloque in iter(lambda: fh.read(1024 * 1024), b""):
                h.update(bloque)
    except OSError as e:
        return f"error:{type(e).__name__}"
    return h.hexdigest()[:16]


def recorrer(raiz: Path) -> dict:
    archivos, saltados = {}, 0
    if not raiz.is_dir():
        return archivos
    for base, dirs, nombres in os.walk(raiz):
        dirs[:] = [d for d in dirs if d not in IGNORAR]
        for n in nombres:
            f = Path(base) / n
            try:
                st = f.stat()
            except OSError:
                saltados += 1
                continue
            rel = str(f.relative_to(raiz)).replace("\\", "/")
            archivos[f"{raiz.name}/{rel}"] = {
                "bytes": st.st_size,
                "mod": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "huella": huella(f) if st.st_size <= TOPE_HUELLA else "sin-huella",
            }
    if saltados:
        print(f"  ({saltados} archivos inaccesibles en {raiz.name}, omitidos)")
    return archivos


def tomar_foto() -> int:
    print("REPLANTEO DEL DISCO\n")
    total = {}
    for r in RAICES:
        print(f"  recorriendo {r.name}...")
        parte = recorrer(r)
        total.update(parte)
        print(f"    {len(parte):,} archivos")

    DESTINO.mkdir(parents=True, exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d-%H%M")
    ruta = DESTINO / f"inventario-{sello}.json"
    ruta.write_text(
        json.dumps({"tomada": sello, "raices": [str(r) for r in RAICES], "archivos": total},
                   ensure_ascii=False, indent=1),
        encoding="utf-8", newline="\n",
    )
    bytes_totales = sum(a["bytes"] for a in total.values())
    sin_huella = sum(1 for a in total.values() if a["huella"] == "sin-huella")
    print(f"\n  {len(total):,} archivos · {bytes_totales / 2**30:.1f} GB")
    if sin_huella:
        print(f"  {sin_huella} sin huella por tamano (se identifican por bytes y fecha)")
    print(f"  guardado: {ruta}")
    print(f"  ({ruta.stat().st_size / 1024:.0f} KB, fuera del repositorio: son datos PERSONAL)")
    return 0


def fotos() -> list:
    if not DESTINO.is_dir():
        return []
    return sorted(DESTINO.glob("inventario-*.json"))


def listar() -> int:
    f = fotos()
    if not f:
        print("No hay fotos todavia. Tomar una con: python config/inventario.py")
        return 1
    for x in f:
        d = json.loads(x.read_text(encoding="utf-8"))
        print(f"  {x.name}  ·  {len(d['archivos']):,} archivos  ·  {x.stat().st_size / 1024:.0f} KB")
    return 0


def comparar(antes: dict, despues: dict, etiqueta_a: str, etiqueta_b: str) -> int:
    a, b = antes["archivos"], despues["archivos"]

    # Un archivo "movido" es el mismo contenido en otra ruta: misma huella,
    # distinta ubicacion. Es justo lo que el log del script nunca registro.
    por_huella_a = {}
    for ruta, meta in a.items():
        if meta["huella"] != "sin-huella":
            por_huella_a.setdefault(meta["huella"], []).append(ruta)

    faltan = [r for r in a if r not in b]
    nuevos = [r for r in b if r not in a]
    cambiados = [r for r in a if r in b and a[r]["huella"] != b[r]["huella"]]

    movidos = []
    for n in list(nuevos):
        h = b[n]["huella"]
        if h == "sin-huella":
            continue
        origenes = [o for o in por_huella_a.get(h, []) if o in faltan]
        if origenes:
            movidos.append((origenes[0], n))
            faltan.remove(origenes[0])
            nuevos.remove(n)

    print(f"COMPARACION\n  antes:   {etiqueta_a}\n  despues: {etiqueta_b}\n")
    print(f"  movidos (mismo contenido, otra ruta) : {len(movidos)}")
    print(f"  desaparecidos (sin rastro)           : {len(faltan)}")
    print(f"  nuevos                               : {len(nuevos)}")
    print(f"  modificados en el lugar              : {len(cambiados)}")

    def mostrar(titulo, items, fmt):
        if not items:
            return
        print(f"\n  {titulo}")
        for x in items[:15]:
            print(f"    {fmt(x)}")
        if len(items) > 15:
            print(f"    ... y {len(items) - 15} mas")

    mostrar("MOVIDOS", movidos, lambda m: f"{m[0]}  ->  {m[1]}")
    mostrar("DESAPARECIDOS — revisar", faltan, lambda r: f"{r}  ({a[r]['bytes']:,} bytes)")
    mostrar("NUEVOS", nuevos, lambda r: f"{r}  ({b[r]['bytes']:,} bytes)")
    mostrar("MODIFICADOS", cambiados, lambda r: r)

    if faltan:
        print("\n  ATENCION: los desaparecidos no se encontraron en ninguna otra ruta.")
        print("  Puede ser un borrado, o un archivo cuyo contenido cambio al moverse.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Replanteo del disco: fotos comparables del arbol de archivos")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--comparar", nargs="*", metavar="FOTO")
    a = ap.parse_args()

    if a.listar:
        return listar()

    if a.comparar is not None:
        if len(a.comparar) == 2:
            x, y = Path(a.comparar[0]), Path(a.comparar[1])
            return comparar(json.loads(x.read_text(encoding="utf-8")),
                            json.loads(y.read_text(encoding="utf-8")), x.name, y.name)
        f = fotos()
        if not f:
            print("No hay fotos para comparar.", file=sys.stderr)
            return 1
        print("Comparando la ultima foto contra el disco de hoy...\n")
        ahora = {"archivos": {}}
        for r in RAICES:
            ahora["archivos"].update(recorrer(r))
        return comparar(json.loads(f[-1].read_text(encoding="utf-8")), ahora, f[-1].name, "disco de hoy")

    return tomar_foto()


if __name__ == "__main__":
    raise SystemExit(main())
