"""Convierte una foto o ilustración real (NASA, etc.) en una "tarjeta" para el video, con su crédito.

Uso:  python3 pipeline/tarjeta_foto.py entrada.jpg nombre "FOTO REAL · NASA / NEW HORIZONS" [--recorte]

Sale en assets/art/objetos/<nombre>.png (borde blanco redondeado y el crédito abajo).
--recorte: recorta el fondo negro alrededor del objeto (útil para fotos de cuerpos en el espacio).
Regla del canal: si NO es una foto, la etiqueta debe decir "ILUSTRACIÓN"; anotar el crédito y la
licencia en assets/art/raw/fotos/CREDITOS.md.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textfx import draw_text, font, text_width  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tarjeta(src, name, label, recorte=False, max_side=960):
    im = Image.open(src).convert("RGB")
    if recorte:
        a = np.array(im).astype(int).sum(2)
        ys, xs = np.nonzero(a > 60)
        pad = int(0.08 * max(xs.max() - xs.min(), ys.max() - ys.min()))
        im = im.crop((max(0, xs.min() - pad), max(0, ys.min() - pad),
                      min(im.width, xs.max() + pad), min(im.height, ys.max() + pad)))
    im.thumbnail((max_side, max_side))
    w, h = im.size
    b, cap = 16, 60
    card = Image.new("RGBA", (w + 2 * b, h + 2 * b + cap), (0, 0, 0, 0))
    m = Image.new("L", card.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, card.width - 1, card.height - 1), 36, fill=255)
    card.paste(Image.new("RGBA", card.size, (255, 255, 255, 255)), (0, 0), m)
    inner = Image.new("L", (w, h), 0)
    ImageDraw.Draw(inner).rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=255)
    card.paste(im, (b, b), inner)
    size = 40
    while text_width(label, font("InterDisplay-Black.otf", size)) > card.width - 30:
        size -= 2
    f = font("InterDisplay-Black.otf", size)
    draw_text(card, ((card.width - text_width(label, f)) / 2, h + 2 * b + (cap - size * 1.2) / 2 - 6),
              label, f, fill=(20, 20, 20, 255))
    out = os.path.join(ROOT, "assets", "art", "objetos", name + ".png")
    card.save(out)
    return out


if __name__ == "__main__":
    print(tarjeta(sys.argv[1], sys.argv[2], sys.argv[3], "--recorte" in sys.argv))
