"""Poses y rig 2D de los colegas (mismo método que Newton).

Por colega se generan 5 imágenes con la API (tope en imagegen.py):
  1. hoja 2x2 con 4 poses nuevas (modo "poses", referencia = su diseño aprobado)
  2-3. la hoja con boca abierta y con ojos cerrados (modo "edit")
  4-5. el diseño aprobado con boca abierta y con ojos cerrados (modo "edit")
Luego se recorta cada cuadrante y se arma el rig (base, boca_abierta, ojos_cerrados) con
rig_newton.build, que alinea la variante e injerta solo la zona que cambia.

Uso:  python3 pipeline/rig_colegas.py darwin [tesla ...]     (sin argumentos: todos)
Salida: assets/art/colegas/<nombre>/rig/<pose>/{base,boca_abierta,ojos_cerrados}.png
        output/colegas_poses/<nombre>.png   (hoja de revisión)
Es idempotente: no vuelve a pedir imágenes que ya existen en assets/art/raw/colegas/.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cutout  # noqa: E402
import imagegen  # noqa: E402
import rig_newton  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "assets", "art", "raw", "colegas")
COL = os.path.join(ROOT, "assets", "art", "colegas")

# diseño aprobado (raw con fondo verde) y su objeto distintivo
COLEGAS = {
    "darwin": ("darwin_v1", "the small Galapagos tortoise sitting on his shoulder"),
    "tesla": ("tesla_v1", "his electrified spiky hair with blue sparks"),
    "curie": ("curie_v1", "the small flask with glowing blue-green liquid"),
    "turing": ("turing_v2", "the open laptop with green code on the screen"),
    "godel": ("godel_v1", "the huge winter coat, scarf and the small chalkboard with the infinity symbol"),
    "ada": ("ada_v1", "the strip of punched cards"),
    "hipatia": ("hipatia_v1", "the golden brass astrolabe"),
    "anning": ("anning_v1", "the black top hat, the geologist hammer and the ammonite fossil"),
    "franklin": ("franklin_v1", "the X-ray photographic plate with the X-shaped pattern"),
}
# orden de lectura de la hoja 2x2 (igual vocabulario que Newton)
POSES = ["explicando", "senalando", "asustado", "pensando"]
POSES_PROMPT = ("top-left: explaining enthusiastically, one hand raised with open palm; top-right: "
                "pointing to the side with the index finger, confident smile; bottom-left: scared and "
                "surprised, both hands up, eyes wide open; bottom-right: thinking, hand on chin, looking "
                "up. Keep {item} in every pose")
OPEN = "change the mouth of every character to open as if speaking mid-word, showing a little tongue"
BLINK = "close the eyes of every character in a relaxed blink, eyelids down"


def gen(mode, prompt, out, ref):
    if not os.path.exists(out):
        imagegen.generate(mode, prompt, out, [os.path.relpath(ref, ROOT)])
    return out


def full_cut(path):
    """Imagen completa recortada (RGBA) y máscara de piezas grandes."""
    rgb = np.array(Image.open(path).convert("RGB"))
    bg = cutout.strip_border(rgb, cutout.key_mask(rgb))
    bg = ndimage.binary_opening(bg, iterations=1)
    fg = ndimage.binary_fill_holes(~bg) & ~bg
    lab, n = ndimage.label(fg)
    sizes = ndimage.sum(fg, lab, range(1, n + 1))
    keep = np.isin(lab, [i + 1 for i, s in enumerate(sizes) if s >= cutout.MIN_AREA])
    alpha = np.array(Image.fromarray((keep * 255).astype(np.uint8)).filter(
        __import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(0.8)))
    return cutout.despill(np.dstack([rgb, alpha])), keep, lab


def quadrants(path, layout=None):
    """Recorta cada personaje: agrupa las piezas por cuadrante (2x2) o todo junto (1 personaje).

    layout: lista de 4 cajas (x0, y0, x1, y1) de la imagen base; se reutiliza para las variantes,
    que la edición deja en el mismo lugar.
    """
    rgba, keep, lab = full_cut(path)
    h, w = keep.shape
    if layout is None:
        layout = []
        for qy in (0, 1):
            for qx in (0, 1):
                m = np.zeros_like(keep)
                m[qy * h // 2:(qy + 1) * h // 2, qx * w // 2:(qx + 1) * w // 2] = True
                ids = set(np.unique(lab[keep & m])) - {0}
                # una pieza pertenece al cuadrante de su centro de masa
                own = [i for i in ids if (lambda c: (int(c[0] >= h / 2), int(c[1] >= w / 2)))(
                    ndimage.center_of_mass(lab == i)) == (qy, qx)]
                ys, xs = np.nonzero(np.isin(lab, own))
                layout.append((max(0, xs.min() - 8), max(0, ys.min() - 8),
                               min(w, xs.max() + 9), min(h, ys.max() + 9)))
    out = []
    for x0, y0, x1, y1 in layout:
        crop = rgba[y0:y1, x0:x1].copy()
        out.append(Image.fromarray(crop))
    return out, layout


def single(path):
    rgba, keep, _ = full_cut(path)
    ys, xs = np.nonzero(keep)
    return Image.fromarray(rgba[max(0, ys.min() - 8):ys.max() + 9, max(0, xs.min() - 8):xs.max() + 9])


def review(name, rig_dir, poses):
    """Hoja: cada pose en fila con base / boca abierta / ojos cerrados."""
    cell = 300
    sheet = Image.new("RGB", (cell * 3 + 20, cell * len(poses) + 20), (232, 238, 245))
    d = ImageDraw.Draw(sheet)
    for r, pose in enumerate(poses):
        for c, st in enumerate(("base", "boca_abierta", "ojos_cerrados")):
            p = os.path.join(rig_dir, pose, st + ".png")
            if os.path.exists(p):
                im = Image.open(p)
                im.thumbnail((cell - 10, cell - 25))
                sheet.paste(im, (10 + c * cell + (cell - im.width) // 2, 10 + r * cell), im)
            d.text((14 + c * cell, r * cell + cell - 8), f"{pose} / {st}", fill=(0, 0, 0))
    os.makedirs(os.path.join(ROOT, "output", "colegas_poses"), exist_ok=True)
    out = os.path.join(ROOT, "output", "colegas_poses", name + ".png")
    sheet.save(out)
    return out


def make(name):
    design, item = COLEGAS[name]
    ref = os.path.join(RAW, design + ".jpg")
    sheet = gen("poses", POSES_PROMPT.format(item=item), os.path.join(RAW, f"{name}_poses.jpg"), ref)
    s_open = gen("edit", OPEN, os.path.join(RAW, f"{name}_poses_boca_abierta.jpg"), sheet)
    s_blink = gen("edit", BLINK, os.path.join(RAW, f"{name}_poses_ojos_cerrados.jpg"), sheet)
    d_open = gen("edit", OPEN.replace("every character", "the character"),
                 os.path.join(RAW, f"{design}_boca_abierta.jpg"), ref)
    d_blink = gen("edit", BLINK.replace("every character", "the character"),
                  os.path.join(RAW, f"{design}_ojos_cerrados.jpg"), ref)
    rig_dir = os.path.join(COL, name, "rig")
    bases, layout = quadrants(sheet)
    opens, _ = quadrants(s_open, layout)
    blinks, _ = quadrants(s_blink, layout)
    for pose, b, o, k in zip(POSES, bases, opens, blinks):
        rig_newton.build(pose, b, None, o, k, out_dir=os.path.join(rig_dir, pose))
    rig_newton.build("presentando", single(ref), None, single(d_open), single(d_blink),
                     out_dir=os.path.join(rig_dir, "presentando"))
    return review(name, rig_dir, ["presentando"] + POSES)


if __name__ == "__main__":
    for n in sys.argv[1:] or list(COLEGAS):
        print("Listo:", make(n))
