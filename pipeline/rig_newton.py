"""Arma el "rig" 2D de cada pose de Newton: base, boca cerrada, boca abierta y ojos cerrados.

Las variantes vienen de ediciones de la hoja de poses (más pequeñas y no alineadas). Para que
Newton no tiemble al hablar, no se cambia la imagen entera: se alinea la variante con la base
en la zona de la cara y se injerta solo la boca (o los ojos) con bordes suaves.

Uso:
    python3 pipeline/rig_newton.py            # usa las piezas recortadas en --cuts
Salida: assets/art/newton/rig/<pose>/{base,boca_cerrada,boca_abierta,ojos_cerrados}.png
"""
import os
import sys

import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets", "art")


def face_box(rgba):
    """Caja de la cara: el mayor componente de piel en el 40 % superior de la imagen."""
    a = rgba.astype(int)
    h = a.shape[0]
    r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    skin = (r > 190) & (g > 130) & (b > 95) & (r > g + 15) & (g > b) & (al > 200)
    skin[int(h * 0.42):] = False
    skin = ndimage.binary_opening(skin, iterations=2)
    lab, n = ndimage.label(skin)
    if n == 0:
        raise RuntimeError("No se encontró la cara")
    sizes = ndimage.sum(skin, lab, range(1, n + 1))
    sl = ndimage.find_objects(lab)[int(np.argmax(sizes))]
    return sl[0].start, sl[0].stop, sl[1].start, sl[1].stop  # y0, y1, x0, x1


def shift_to_match(base, var, box):
    """Desplazamiento (dy, dx) que alinea var con base en la caja, por correlación de fase."""
    y0, y1, x0, x1 = box
    pad = 20
    y0, x0 = max(0, y0 - pad), max(0, x0 - pad)
    y1, x1 = min(base.shape[0], y1 + pad), min(base.shape[1], x1 + pad)
    gb = base[y0:y1, x0:x1, :3].mean(axis=2)
    gv = var[y0:y1, x0:x1, :3].mean(axis=2)
    win = np.outer(np.hanning(gb.shape[0]), np.hanning(gb.shape[1]))
    fb, fv = np.fft.fft2(gb * win), np.fft.fft2(gv * win)
    cross = fb * np.conj(fv)
    corr = np.fft.ifft2(cross / (np.abs(cross) + 1e-9)).real
    dy, dx = np.unravel_index(np.argmax(corr), corr.shape)
    if dy > gb.shape[0] // 2:
        dy -= gb.shape[0]
    if dx > gb.shape[1] // 2:
        dx -= gb.shape[1]
    return int(dy), int(dx)


def fit_variant(base_img, var_img):
    """Escala la variante al tamaño de la base y la alinea en la cara."""
    base = np.array(base_img)
    s = base_img.height / var_img.height
    v = var_img.resize((round(var_img.width * s), base_img.height), Image.LANCZOS)
    canvas = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    canvas.paste(v, ((base_img.width - v.width) // 2, 0))
    var = np.array(canvas)
    box = face_box(base)
    dy, dx = shift_to_match(base, var, box)
    var = np.roll(np.roll(var, dy, axis=0), dx, axis=1)
    return base, var, box


def graft(base, var, region, feather=6):
    """Copia var sobre base dentro de la región (y0,y1,x0,x1) con borde suave."""
    y0, y1, x0, x1 = region
    m = np.zeros(base.shape[:2], np.float32)
    m[y0:y1, x0:x1] = 1
    m = np.array(Image.fromarray((m * 255).astype(np.uint8)).filter(
        ImageFilter.GaussianBlur(feather))).astype(np.float32)[..., None] / 255
    out = base.astype(np.float32) * (1 - m) + var.astype(np.float32) * m
    return out.clip(0, 255).astype(np.uint8)


def regions(box):
    """Zonas de boca y ojos relativas a la caja de la cara (vista de 3/4)."""
    y0, y1, x0, x1 = box
    fh, fw = y1 - y0, x1 - x0
    mouth = (y0 + int(fh * 0.60), y0 + int(fh * 0.97), x0 + int(fw * 0.12), x1 - int(fw * 0.05))
    eyes = (y0 + int(fh * 0.12), y0 + int(fh * 0.52), x0 + int(fw * 0.02), x1)
    return mouth, eyes


def diff_region(base, var, pad=10):
    """Zona donde la variante cambia respecto a la base (la boca o los ojos), ya alineadas."""
    d = np.abs(base[..., :3].astype(int) - var[..., :3].astype(int)).sum(axis=2)
    both = (base[..., 3] > 200) & (var[..., 3] > 200)
    m = ndimage.binary_opening((d > 60) & both, iterations=1)
    m = ndimage.binary_dilation(m, iterations=6)
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    sl = ndimage.find_objects(lab)[int(np.argmax(sizes))]
    h, w = m.shape
    return (max(0, sl[0].start - pad), min(h, sl[0].stop + pad),
            max(0, sl[1].start - pad), min(w, sl[1].stop + pad))


def build(pose, base_path, closed, opened, blink):
    out_dir = os.path.join(ART, "newton", "rig", pose)
    os.makedirs(out_dir, exist_ok=True)
    base_img = Image.open(base_path).convert("RGBA")
    base_img.save(os.path.join(out_dir, "base.png"))
    for name, path, which in (("boca_cerrada", closed, "mouth"), ("boca_abierta", opened, "mouth"),
                              ("ojos_cerrados", blink, "eyes")):
        if not path:
            continue
        base, var, box = fit_variant(base_img, Image.open(path).convert("RGBA"))
        mouth, eyes = regions(box)
        region = diff_region(base, var) or (mouth if which == "mouth" else eyes)
        res = graft(base, var, region, feather=4)
        Image.fromarray(res).save(os.path.join(out_dir, f"{name}.png"))
    print("rig:", pose)


if __name__ == "__main__":
    cuts = sys.argv[sys.argv.index("--cuts") + 1]
    order = ["explicando_pluma", "senalando", "asustado", "pensando"]
    for i, pose in enumerate(order, 1):
        f = lambda v: os.path.join(cuts, f"newton_poses_{v}", f"{i:02d}.png")
        build(pose, os.path.join(ART, "newton", f"pose_{pose}.png"),
              f("boca_cerrada"), f("boca_abierta"), f("ojos_cerrados"))
    build("manzana_pensando", os.path.join(ART, "newton", "pose_manzana_pensando.png"), None,
          os.path.join(cuts, "newton_manzana_boca_abierta", "01.png"),
          os.path.join(cuts, "newton_manzana_ojos_cerrados", "01.png"))
