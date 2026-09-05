"""
Genera images/manifest.json a partir de las subcarpetas de images/ -- cada
subcarpeta es una categoria de "Trabajos terminados" en la landing
(index.html, sección #trabajos), y cada imagen adentro es una foto del
carrusel de esa categoria.

El sitio es estatico (GitHub Pages, sin backend ni build) -- no hay forma
de que el navegador liste carpetas por su cuenta, asi que este script
arma ese listado una vez y lo deja en un JSON que el navegador sí puede
leer con un fetch normal.

Uso: cada vez que agregues, saques o renombres fotos/carpetas dentro de
images/, corré:

    python scripts/generar_galeria.py

y commiteá + pusheá el manifest.json resultante junto con las fotos
nuevas -- el link de "Trabajos" del sitio no aparece hasta que haya al
menos una categoria con fotos.
"""

import json
import re
import sys
from pathlib import Path

EXTENSIONES_VALIDAS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
RAIZ = Path(__file__).resolve().parent.parent
IMAGES_DIR = RAIZ / "images"
MANIFEST_PATH = IMAGES_DIR / "manifest.json"


def _clave_orden_natural(nombre):
    """Para que 'foto2' ordene antes que 'foto10' -- separa el nombre en
    pedazos de texto/numero en vez de compararlo como string plano
    (donde '10' < '2' porque el caracter '1' es menor que '2')."""
    return [int(parte) if parte.isdigit() else parte.lower()
            for parte in re.split(r'(\d+)', nombre)]


def main():
    # En la consola de Windows (cp1252 por default) los acentos de este
    # mismo script salen como mojibake si no se fuerza UTF-8 -- no afecta al
    # manifest.json en si (ya se escribe con encoding="utf-8" mas abajo),
    # pero confunde al leer la salida del script en la terminal.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        pass  # Python < 3.7, no deberia pasar en este proyecto

    if not IMAGES_DIR.is_dir():
        print(f"No se encontró la carpeta {IMAGES_DIR}", file=sys.stderr)
        sys.exit(1)

    categorias = []
    for carpeta in sorted(IMAGES_DIR.iterdir(), key=lambda p: _clave_orden_natural(p.name)):
        # Solo subcarpetas cuentan como categoria -- los archivos sueltos que
        # ya viven en images/ (logo.png, iconos, etc.) se ignoran solos.
        if not carpeta.is_dir() or carpeta.name.startswith('.'):
            continue

        fotos = sorted(
            (f for f in carpeta.iterdir()
             if f.is_file() and f.suffix.lower() in EXTENSIONES_VALIDAS),
            key=lambda p: _clave_orden_natural(p.name),
        )

        if not fotos:
            print(f"Aviso: '{carpeta.name}' no tiene fotos (jpg/jpeg/png/webp/gif) -- se omite.")
            continue

        categorias.append({
            "nombre": carpeta.name,
            "fotos": [f"{carpeta.name}/{f.name}" for f in fotos],
        })

    MANIFEST_PATH.write_text(
        json.dumps({"categorias": categorias}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    total_fotos = sum(len(c["fotos"]) for c in categorias)
    print(f"Listo: {len(categorias)} categoría(s), {total_fotos} foto(s) -> {MANIFEST_PATH}")
    if categorias:
        print("Ahora: git add images/ && git commit -m '...' && git push")
    else:
        print("Todavía no hay ninguna carpeta con fotos dentro de images/ -- "
              "la sección 'Trabajos' del sitio queda oculta hasta que haya alguna.")


if __name__ == "__main__":
    main()
