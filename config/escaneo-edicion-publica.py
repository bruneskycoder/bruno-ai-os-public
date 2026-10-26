#!/usr/bin/env python3
"""Escaneo previo al push de una edición pública. Sale con código 1 si encuentra algo.

Uso:
  python3 -I config/escaneo-edicion-publica.py <directorio> <lista-permitida.txt>
      [--nuevos README.md 'docs/*' ...]  archivos o globs escritos para la edición, que no vienen del taller
      [--excepciones excepciones.txt]    líneas "ruta<TAB>texto" aceptadas a propósito
      [--extra patrones.txt]             un regex por línea; va FUERA del repositorio
      [--omitir "nombre propio,rol del contrato"]   nombres de patrones base que no aplican a esta edición

Chequea (1) que el contenido sea exactamente la lista permitida más los archivos nuevos y
(2) patrones sensibles en texto, en texto extraído de PDF y en cadenas internas de PDF y fuentes.
Los identificadores personales concretos (números de trámite, teléfonos) van en --extra,
en un archivo que no se versiona. Requiere pdftotext, pdfinfo y strings."""
import argparse, fnmatch, re, subprocess, sys
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument('directorio'); ap.add_argument('lista')
ap.add_argument('--nuevos', nargs='*', default=[])
ap.add_argument('--excepciones'); ap.add_argument('--extra'); ap.add_argument('--omitir', default='')
a = ap.parse_args()

raiz = Path(a.directorio).resolve()
lista = [l.strip() for l in Path(a.lista).read_text(encoding='utf-8').splitlines()
         if l.strip() and not l.lstrip().startswith('#')]
nuevos = set(a.nuevos)
excepciones = set()
if a.excepciones:
    for l in Path(a.excepciones).read_text(encoding='utf-8').splitlines():
        if l.strip() and not l.startswith('#'):
            ruta, texto = l.split('\t', 1)
            excepciones.add((ruta, texto))

PATRONES = {
    'nombre propio': r'\bBruno\b|Guti[eé]rrez',
    'rol del contrato': r'\bDirector\b|\bAGENTS\b',
    'email': r'[\w.+-]+@[\w-]+\.[A-Za-z]{2,}\b',
    'telefono': r'\+?\d{2,3}[ -]?\d{3,4}[ -]?\d{4,}',
    'digitos largos': r'\b\d{8,}\b',
    'ruta local': r'/home/|/Users/|C:\\|\\Users\\|Desktop|scratchpad',
    'clave': r'AKIA[0-9A-Z]{16}|ghp_\w{20,}|github_pat_\w+|xox[bap]-|sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*KEY|api[_-]?key\s*[:=]|secret\s*[:=]|password\s*[:=]',
}
for _n in filter(None, (x.strip() for x in a.omitir.split(','))):
    PATRONES.pop(_n, None)
if a.extra:
    for i, l in enumerate(Path(a.extra).read_text(encoding='utf-8').splitlines(), 1):
        if l.strip() and not l.startswith('#'):
            PATRONES[f'extra-{i}'] = l.strip()
rx = {k: re.compile(v, 0 if k == 'nombre propio' else re.I) for k, v in PATRONES.items()}
NUMERICOS = {'telefono', 'digitos largos'}
hallazgos = []

archivos = sorted(p for p in raiz.rglob('*')
                  if p.is_file() and '.git' not in p.parts and 'node_modules' not in p.parts)
rel = {str(p.relative_to(raiz)).replace('\\', '/') for p in archivos}
for r in sorted(rel):
    if not any(fnmatch.fnmatch(r, pat) for pat in lista + sorted(nuevos)):
        hallazgos.append(('archivo fuera de la lista', r, ''))

def revisar(nombre, texto, origen):
    binario = origen in ('fuente-cadenas', 'pdf-cadenas')
    for n, linea in enumerate(texto.splitlines(), 1):
        for k, r in rx.items():
            if binario and k in NUMERICOS:
                continue
            m = r.search(linea)
            if m and (nombre, m.group(0)) not in excepciones:
                hallazgos.append((f'{k} [{origen}]', f'{nombre}:{n}', linea.strip()[:110]))

def cadenas(p):
    return subprocess.run(['strings', '-n', '8', str(p)], capture_output=True, text=True).stdout

for p in archivos:
    r = str(p.relative_to(raiz)).replace('\\', '/')
    suf = p.suffix.lower()
    if suf in {'.html', '.css', '.js', '.mjs', '.py', '.json', '.md', '.txt'} or p.name in {'LICENSE', 'LICENSE-CODIGO', '.gitignore'}:
        revisar(r, p.read_text(encoding='utf-8', errors='replace'), 'texto')
    elif suf == '.pdf':
        revisar(r, subprocess.run(['pdftotext', '-q', str(p), '-'], capture_output=True, text=True).stdout, 'pdf-texto')
        revisar(r, subprocess.run(['pdfinfo', str(p)], capture_output=True, text=True).stdout, 'pdf-meta')
        revisar(r, cadenas(p), 'pdf-cadenas')
    elif suf in {'.ttf', '.png'}:
        revisar(r, cadenas(p), 'fuente-cadenas')

print(f'archivos revisados: {len(archivos)}  ·  patrones: {len(PATRONES)}  ·  hallazgos: {len(hallazgos)}')
for k, donde, linea in hallazgos[:80]:
    print(f'  [{k}] {donde}  {linea}')
sys.exit(1 if hallazgos else 0)
