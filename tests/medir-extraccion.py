"""Compara cuanto cuesta, en tokens, meter un documento en el contexto.

La pregunta que responde: conviene convertir un PDF a markdown localmente antes
de que el modelo lo lea, o alcanza con que lo lea nativo?

NO imprime el contenido de los documentos. Solo mide tamanos. Los archivos del
Director son datos PERSONAL: se cuentan caracteres, no se leen.

Uso:
  python tests/medir-extraccion.py <archivo.pdf> [<archivo2> ...]
"""
import re
import subprocess
import sys
import time
from pathlib import Path

CHARS_POR_TOKEN = 3.3

# Una pagina de PDF leida de forma nativa se envia ademas como imagen. El costo
# depende de la resolucion; se usa un rango conservador declarado, no un numero
# inventado con precision falsa.
TOKENS_IMAGEN_POR_PAGINA = (1100, 1800)


def paginas(pdf: Path) -> int:
    """Cuenta paginas leyendo los bytes crudos, sin instalar una libreria de PDF."""
    try:
        crudo = pdf.read_bytes()
    except OSError:
        return 0
    n = len(re.findall(rb"/Type\s*/Page[^s]", crudo))
    if n == 0:
        m = re.search(rb"/Count\s+(\d+)", crudo)
        n = int(m.group(1)) if m else 0
    return n


def extraer(archivo: Path):
    inicio = time.monotonic()
    r = subprocess.run(
        [sys.executable, "-m", "markitdown", str(archivo)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        stdin=subprocess.DEVNULL, timeout=600,
    )
    return r.stdout or "", time.monotonic() - inicio, r.returncode


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    for ruta in sys.argv[1:]:
        f = Path(ruta)
        if not f.is_file():
            print(f"no existe: {f}")
            continue

        kb = f.stat().st_size / 1024
        pags = paginas(f) if f.suffix.lower() == ".pdf" else 0
        texto, segundos, codigo = extraer(f)

        print(f"\n{f.name}")
        print(f"  archivo: {kb:,.0f} KB" + (f"  ·  {pags} paginas" if pags else ""))
        if codigo != 0 or not texto.strip():
            print("  EXTRACCION FALLIDA (codigo {}). No se puede comparar.".format(codigo))
            continue

        tok_texto = int(len(texto) / CHARS_POR_TOKEN)
        print(f"  markitdown: {len(texto):,} caracteres  ->  ~{tok_texto:,} tokens   ({segundos:.1f} s)")

        if pags:
            bajo = tok_texto + pags * TOKENS_IMAGEN_POR_PAGINA[0]
            alto = tok_texto + pags * TOKENS_IMAGEN_POR_PAGINA[1]
            print(f"  lectura nativa: ~{bajo:,} a {alto:,} tokens   (texto + {pags} paginas como imagen)")
            print(f"  AHORRO estimado: {bajo - tok_texto:,} a {alto - tok_texto:,} tokens"
                  f"  ->  entre {bajo/tok_texto:.0f}x y {alto/tok_texto:.0f}x mas barato")
            # 1% del semanal ~ 80.000 tokens (COST_MODEL.md)
            print(f"  en plan: entre {(bajo-tok_texto)/80000:.2f}% y {(alto-tok_texto)/80000:.2f}% del semanal por documento")

        # Senal de calidad, sin mostrar contenido.
        lineas = texto.count("\n")
        vacio = sum(1 for l in texto.splitlines() if not l.strip())
        print(f"  calidad: {lineas:,} lineas, {vacio:,} vacias"
              f"  ·  {'estructura conservada' if '#' in texto or '|' in texto else 'texto plano, sin estructura'}")

    print(f"\n  Metodo: {CHARS_POR_TOKEN} caracteres por token; imagen por pagina"
          f" {TOKENS_IMAGEN_POR_PAGINA[0]}-{TOKENS_IMAGEN_POR_PAGINA[1]} tokens (rango declarado).")
    print("  Los conteos de caracteres y paginas son exactos; la conversion a tokens es estimada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
