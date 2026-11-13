"""Recorta las piezas de una hoja con fondo verde (chroma) en PNGs con transparencia.

Uso:
    python3 pipeline/cutout.py assets/art/raw/objetos.jpg assets/art/objetos [--keep-border]

Pasos:
  1. Fondo verde -> transparente (por distancia de color al verde de la hoja).
  2. Quita el borde blanco tipo "sticker": crece el fondo sobre píxeles casi blancos
     conectados al verde, hasta BORDER píxeles (el contorno oscuro del dibujo lo detiene).
  3. Suprime el halo verde en los bordes y suaviza el alfa.
  4. Separa cada pieza (componentes conectados) y guarda un PNG por pieza, más una hoja
     de contacto numerada para identificarlas.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from scipy import ndimage

BORDER = 22       # grosor máximo del borde blanco a quitar (px)
MIN_AREA = 2500   # piezas más pequeñas se descartan (ruido)
PAD = 6


STRICT = False  # --strict: solo el verde exacto del fondo (para objetos verdes, p. ej. pasto)


def key_mask(rgb):
    """True donde hay fondo verde (o magenta, detectado por la esquina)."""
    r, g, b = (rgb[..., i].astype(np.int32) for i in range(3))
    bg = np.median(rgb[:8, :8].reshape(-1, 3), axis=0).astype(np.int32)
    dist = np.sqrt((r - bg[0]) ** 2 + (g - bg[1]) ** 2 + (b - bg[2]) ** 2)
    if bg[0] > 150 and bg[2] > 150 and bg[1] < 100:  # fondo magenta (objetos verdes)
        core = dist < 90
        magentish = (r > g + 60) & (b > g + 60) & (r > 140) & (b > 140)
        lab, _ = ndimage.label(core | magentish)
        touching = np.unique(lab[core])  # solo el halo magenta pegado al fondo, no lo rosa del dibujo
        return np.isin(lab, touching[touching > 0])
    if STRICT:
        return dist < 70
    greenish = (g > r + 40) & (g > b + 40)
    return (dist < 90) | (greenish & (g > 150))


def strip_border(rgb, bg):
    """Agrega al fondo el borde blanco conectado al verde."""
    r, g, b = (rgb[..., i].astype(np.int32) for i in range(3))
    whiteish = (r > 200) & (g > 200) & (b > 195) & (np.abs(r - b) < 40)
    cur = bg.copy()
    for _ in range(BORDER):
        grown = ndimage.binary_dilation(cur) & whiteish & ~cur
        if not grown.any():
            break
        cur |= grown
    # una pasada extra para los píxeles de antialias entre blanco y verde
    edge = ndimage.binary_dilation(cur) & ~cur & (r + g + b > 600)
    return cur | edge


def despill(rgba):
    """Quita el tinte verde de los bordes."""
    a = rgba[..., 3]
    edge = ndimage.binary_dilation(a < 255, iterations=3) & (a > 0)
    r, g, b = (rgba[..., i].astype(np.int32) for i in range(3))
    g2 = np.where(edge, np.minimum(g, np.maximum(r, b) + 10), g)
    rgba[..., 1] = np.clip(g2, 0, 255).astype(np.uint8)
    return rgba


def cut(path, out_dir, keep_border=False):
    os.makedirs(out_dir, exist_ok=True)
    rgb = np.array(Image.open(path).convert("RGB"))
    bg = key_mask(rgb)
    if not keep_border:
        bg = strip_border(rgb, bg)
    bg = ndimage.binary_opening(bg, iterations=1)
    fg = ~bg
    # huecos internos (brillos blancos) siguen opacos, pero los huecos verdes
    # (p. ej. entre el brazo y el cuerpo) quedan transparentes
    fg = ndimage.binary_fill_holes(fg) & ~bg
    alpha = (fg * 255).astype(np.uint8)
    alpha = np.array(Image.fromarray(alpha).filter(ImageFilter.GaussianBlur(0.8)))
    rgba = np.dstack([rgb, alpha])
    rgba = despill(rgba)

    labels, n = ndimage.label(fg)
    pieces = []
    for i, sl in enumerate(ndimage.find_objects(labels), 1):
        area = (labels[sl] == i).sum()
        if area < MIN_AREA:
            continue
        y0, y1 = max(0, sl[0].start - PAD), min(rgb.shape[0], sl[0].stop + PAD)
        x0, x1 = max(0, sl[1].start - PAD), min(rgb.shape[1], sl[1].stop + PAD)
        crop = rgba[y0:y1, x0:x1].copy()
        own = ndimage.binary_dilation(labels[y0:y1, x0:x1] == i, iterations=3)
        crop[..., 3] = np.where(own, crop[..., 3], 0)  # solo esta pieza
        pieces.append(((y0 + y1) / 2, (x0 + x1) / 2, crop, (x0, y0, x1, y1)))
    pieces.sort(key=lambda p: (round(p[0] / 150), p[1]))  # orden de lectura
    names = []
    for k, (_, _, crop, box) in enumerate(pieces, 1):
        name = f"{k:02d}.png"
        Image.fromarray(crop).save(os.path.join(out_dir, name))
        names.append((name, box))
    contact_sheet(out_dir, names)
    print(f"{path}: {len(names)} piezas -> {out_dir}")
    return names


def contact_sheet(out_dir, names):
    """Hoja de contacto numerada sobre fondo de cuadros (para revisar la transparencia)."""
    thumbs = []
    for name, _ in names:
        im = Image.open(os.path.join(out_dir, name))
        im.thumbnail((240, 240))
        thumbs.append((name, im))
    cols = 5
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 260, rows * 280), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for y in range(0, sheet.height, 20):  # cuadros grises
        for x in range(0, sheet.width, 20):
            if (x // 20 + y // 20) % 2:
                d.rectangle((x, y, x + 19, y + 19), fill=(225, 225, 225))
    for i, (name, im) in enumerate(thumbs):
        x, y = (i % cols) * 260 + 10, (i // cols) * 280 + 10
        sheet.paste(im, (x, y), im)
        d.text((x, y + 245), name, fill=(0, 0, 0))
    sheet.save(os.path.join(out_dir, "_hoja.png"))


if __name__ == "__main__":
    STRICT = "--strict" in sys.argv
    cut(sys.argv[1], sys.argv[2], "--keep-border" in sys.argv)
