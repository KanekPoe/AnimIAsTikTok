"""Genera objetos nuevos en hojas (varios por imagen) y los guarda con su nombre.

Uso:  python3 pipeline/objetos_lote.py lote.json [--solo HOJA]

lote.json: [{"hoja": "animales1", "fondo": "verde"|"magenta",
             "items": [["abeja", "a cartoon honeybee ..."], ...]}, ...]

Por hoja: 1 imagen (tope en imagegen.py) -> recorte (cutout.py) -> las piezas se ordenan por
filas y columnas y se nombran en el orden pedido. Si el número de piezas no coincide, la hoja
NO se guarda en assets/art/objetos (queda para revisión en output/objetos_lote/<hoja>/).
Siempre deja una hoja de contacto con nombres para revisar a ojo: output/objetos_lote/<hoja>.png
Es idempotente: no vuelve a pedir una hoja que ya existe en assets/art/raw/.
"""
import json
import os
import shutil
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutout  # noqa: E402
import imagegen  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OBJ = os.path.join(ROOT, "assets", "art", "objetos")
OUT = os.path.join(ROOT, "output", "objetos_lote")


def prompt_for(items):
    cols = 2
    rows = (len(items) + cols - 1) // cols
    desc = "; ".join(f"{i + 1}) {d}" for i, (_, d) in enumerate(items))
    return (f"Exactly {len(items)} separate items arranged in a grid of {cols} columns and {rows} rows, "
            f"in this exact order from left to right and top to bottom, each item centered in its own "
            f"cell with plenty of empty space around it, no text, no labels, no numbers: {desc}")


def order(names, n_rows):
    """Ordena piezas (nombre, caja) por filas (cortes en los saltos verticales más grandes) y x."""
    cy = [((b[1] + b[3]) / 2, (b[0] + b[2]) / 2, nm) for nm, b in names]
    cy.sort()
    gaps = sorted(range(1, len(cy)), key=lambda i: cy[i][0] - cy[i - 1][0], reverse=True)[:n_rows - 1]
    cuts = [0] + sorted(gaps) + [len(cy)]
    out = []
    for a, b in zip(cuts, cuts[1:]):
        out += [nm for _, _, nm in sorted(cy[a:b], key=lambda t: t[1])]
    return out


def contact(sheet, pieces, ok):
    cell = 240
    im = Image.new("RGB", (cell * 3, cell * ((len(pieces) + 2) // 3) + 30), (232, 238, 245))
    d = ImageDraw.Draw(im)
    d.text((8, 6), f"{sheet}: {'OK' if ok else 'REVISAR (piezas != pedidas)'}", fill=(0, 0, 0))
    for i, (label, path) in enumerate(pieces):
        p = Image.open(path)
        p.thumbnail((cell - 20, cell - 40))
        x, y = (i % 3) * cell, 30 + (i // 3) * cell
        im.paste(p, (x + (cell - p.width) // 2, y), p)
        d.text((x + 8, y + cell - 30), label, fill=(0, 0, 0))
    path = os.path.join(OUT, sheet + ".png")
    im.save(path)
    return path


def run(sheet):
    name, items = sheet["hoja"], sheet["items"]
    magenta = sheet.get("fondo") == "magenta"
    raw = os.path.join(ROOT, "assets", "art", "raw", f"objetos_{name}.jpg")
    if not os.path.exists(raw):
        imagegen.generate("sticker_magenta" if magenta else "sticker", prompt_for(items), raw)
    tmp = os.path.join(OUT, name)
    shutil.rmtree(tmp, ignore_errors=True)
    cutout.STRICT = magenta
    names = cutout.cut(raw, tmp)
    n_rows = (len(items) + 1) // 2
    ok = len(names) == len(items)
    pieces = []
    if ok:
        for (obj, _), piece in zip(items, order(names, n_rows)):
            dst = os.path.join(OBJ, obj + ".png")
            if os.path.exists(dst):
                print(f"  ya existe {obj}.png: no se sobrescribe")
            else:
                shutil.copy(os.path.join(tmp, piece), dst)
            pieces.append((obj, dst))
    else:
        pieces = [(nm, os.path.join(tmp, nm)) for nm, _ in names]
        print(f"  {name}: {len(names)} piezas para {len(items)} objetos -> revisar {tmp}")
    print("  hoja de contacto:", contact(name, pieces, ok))
    return ok


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    lote = json.load(open(sys.argv[1]))
    solo = sys.argv[sys.argv.index("--solo") + 1] if "--solo" in sys.argv else None
    bad = [s["hoja"] for s in lote if (not solo or s["hoja"] == solo) and not run(s)]
    print("Hojas a revisar:", bad or "ninguna")
