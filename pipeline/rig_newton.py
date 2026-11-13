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
    y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
    # lentes o barba parten la piel en varias piezas: unir las grandes que están junto a la mayor
    for i, sz in enumerate(sizes):
        c = ndimage.find_objects(lab)[i]
        if sz >= 0.15 * sizes.max() and c[1].start < x1 + (x1 - x0) // 2 and c[1].stop > x0 - (x1 - x0) // 2 \
                and c[0].start < y1 + (y1 - y0):
            y0, y1 = min(y0, c[0].start), max(y1, c[0].stop)
            x0, x1 = min(x0, c[1].start), max(x1, c[1].stop)
    return y0, y1, x0, x1  # y0, y1, x0, x1


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
    try:
        box = face_box(base)
    except RuntimeError:  # piel no detectada (p. ej. barba grande): zona alta central
        h, w = base.shape[:2]
        box = (int(h * 0.04), int(h * 0.30), int(w * 0.2), int(w * 0.8))
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


def diff_region(base, var, pad=10, above=None, cols=None):
    """Zona donde la variante cambia respecto a la base (la boca o los ojos), ya alineadas.

    above: si se da (y de la boca), solo cuenta lo que está arriba de esa línea y une todas las
    piezas grandes: así un parpadeo cierra LOS DOS ojos y no toca la boca.
    cols: (x0, x1) columnas de la cara; fuera de ellas se ignora (manos levantadas, accesorios).
    """
    d = np.abs(base[..., :3].astype(int) - var[..., :3].astype(int)).sum(axis=2)
    both = (base[..., 3] > 200) & (var[..., 3] > 200)
    m = ndimage.binary_opening((d > 60) & both, iterations=1)
    if above is not None:
        m[above:] = False
    if cols is not None:
        m[:, :max(0, cols[0])] = False
        m[:, cols[1]:] = False
    m = ndimage.binary_dilation(m, iterations=6)
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    h, w = m.shape
    if above is not None:
        big = [i for i, s in enumerate(sizes, 1) if s >= 0.2 * sizes.max()]
        ys, xs = np.nonzero(np.isin(lab, big))
        return (max(0, ys.min() - pad), min(h, ys.max() + 1 + pad),
                max(0, xs.min() - pad), min(w, xs.max() + 1 + pad))
    sl = ndimage.find_objects(lab)[int(np.argmax(sizes))]
    return (max(0, sl[0].start - pad), min(h, sl[0].stop + pad),
            max(0, sl[1].start - pad), min(w, sl[1].stop + pad))


def _diff_mask(base, var, rows, cols):
    d = np.abs(base[..., :3].astype(int) - var[..., :3].astype(int)).sum(axis=2)
    m = (d > 60) & (base[..., 3] > 200) & (var[..., 3] > 200)
    m = ndimage.binary_opening(m, iterations=1)
    keep = np.zeros_like(m)
    keep[rows[0]:rows[1], max(0, cols[0]):cols[1]] = True
    return m & keep


def _bbox(m, pad=10, grow=6):
    m = ndimage.binary_dilation(m, iterations=grow)
    lab, n = ndimage.label(m)
    if n == 0:
        return None
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    big = [i for i, s in enumerate(sizes, 1) if s >= 0.2 * sizes.max()]
    ys, xs = np.nonzero(np.isin(lab, big))
    h, w = m.shape
    return (max(0, ys.min() - pad), min(h, ys.max() + 1 + pad), max(0, xs.min() - pad), min(w, xs.max() + 1 + pad))


def zones(base, opened, blink):
    """Zonas de boca y ojos usando las dos variantes (para personajes nuevos, p. ej. colegas).

    La IA a veces cambia de más al editar (la boca abierta también abre los ojos, o el parpadeo
    relaja la boca). Por eso: se busca solo en la cabeza (columnas de la cara, mitad superior),
    la fila de los ojos es donde más cambia el parpadeo y la de la boca donde más cambia la boca
    abierta por debajo de los ojos; la línea media entre ambas separa las dos zonas.
    """
    h = base.shape[0]
    try:
        y0, y1, x0, x1 = face_box(base)
    except RuntimeError:
        y0, y1, x0, x1 = 0, int(h * 0.3), int(base.shape[1] * 0.2), int(base.shape[1] * 0.8)
    fw = x1 - x0
    cols = (x0 - int(fw * 0.1), x1 + int(fw * 0.1))
    rows = (max(0, y0 - (y1 - y0) // 3), min(h, y1 + (y1 - y0) // 2))
    db, do = _diff_mask(base, blink, rows, cols), _diff_mask(base, opened, rows, cols)
    eye_y = int(np.argmax(ndimage.uniform_filter1d(db.sum(1).astype(float), 9)))
    prof = ndimage.uniform_filter1d(do.sum(1).astype(float), 9)
    prof[:eye_y + (y1 - y0) // 8] = 0
    mouth_y = int(np.argmax(prof)) if prof.max() > 0 else y1
    split = (eye_y + mouth_y) // 2
    db[split:] = False
    do[:split] = False
    return _bbox(do), _bbox(db)


def build(pose, base_path, closed, opened, blink, out_dir=None):
    """base_path/closed/opened/blink: rutas o imágenes PIL. out_dir: por defecto el rig de Newton."""
    out_dir = out_dir or os.path.join(ART, "newton", "rig", pose)
    os.makedirs(out_dir, exist_ok=True)
    load = lambda x: (x if isinstance(x, Image.Image) else Image.open(x)).convert("RGBA")
    base_img = load(base_path)
    base_img.save(os.path.join(out_dir, "base.png"))
    if opened is not None and blink is not None and closed is None:  # colegas: zonas con ambas variantes
        b0, vo, _ = fit_variant(base_img, load(opened))
        _, vb, _ = fit_variant(base_img, load(blink))
        mz, ez = zones(b0, vo, vb)
        for name, var, z in (("boca_abierta", vo, mz), ("ojos_cerrados", vb, ez)):
            if z:
                Image.fromarray(graft(b0, var, z, feather=4)).save(os.path.join(out_dir, f"{name}.png"))
        print("rig:", pose, "boca", mz, "ojos", ez)
        return
    mouth_top = None  # la boca (de boca_abierta) limita la zona de los ojos
    for name, path, which in (("boca_cerrada", closed, "mouth"), ("boca_abierta", opened, "mouth"),
                              ("ojos_cerrados", blink, "eyes")):
        if not path:
            continue
        base, var, box = fit_variant(base_img, load(path))
        mouth, eyes = regions(box)
        if which == "mouth":
            region = diff_region(base, var) or mouth
            mouth_top = region[0] + 10  # región con margen de 10 px
        else:
            fw = box[3] - box[2]
            cols = (box[2] - int(fw * 0.15), box[3] + int(fw * 0.15))
            region = diff_region(base, var, above=mouth_top or mouth[0], cols=cols) or eyes
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
