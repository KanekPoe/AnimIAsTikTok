"""Control de calidad visual de un episodio (como audio_qc, pero de lo que se ve).

Uso:
    python3 pipeline/qa_visual.py episodes/nbl123_usb_agujero_negro.py   # revisa y hace hoja de cuadros
    (sin voces: usa duraciones estimadas, no gasta nada)

Revisa, frase por frase, los objetos y textos que coinciden en pantalla:
- que no se salgan de la zona segura de TikTok (arriba, botones a la derecha, subtítulos abajo);
- que no se encimen entre sí (el sello sí puede ir encima, es a propósito);
- que ningún texto sea más ancho que la pantalla;
y la duración total del video (en el render real). nbl.py lo corre antes de exportar: si hay
errores, no exporta. Además deja una hoja con un cuadro por frase para revisarla a ojo:
output/<slug>/qa_hoja.png
"""
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nbl  # noqa: E402

W, H = nbl.W, nbl.H
TOP, BOTTOM = 250, 1245          # insignia/arriba y subtítulos
RIGHT_UI_X, RIGHT_UI_Y = 925, 0.42 * H   # botones de TikTok (derecha, mitad baja)
MIN_DUR, MAX_DUR = 20, 65


def boxes(r, ln):
    out = []
    for ev in ln.get("events", []):
        if ev.get("kind") == "line":
            continue
        im = r.event_image(ev)
        cx, cy = ev.get("x", 0.5) * W, ev.get("y", 0.5) * H
        x0, y0 = cx - im.width / 2, cy - im.height / 2
        bb = im.getchannel("A").getbbox() or (0, 0, im.width, im.height)  # solo lo visible
        out.append((ev, (x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3])))
    return out


def overlap(a, b):
    w = min(a[2], b[2]) - max(a[0], b[0])
    h = min(a[3], b[3]) - max(a[1], b[1])
    if w <= 0 or h <= 0:
        return 0.0
    small = min((a[2] - a[0]) * (a[3] - a[1]), (b[2] - b[0]) * (b[3] - b[1]))
    return w * h / small


def name(ev):
    return ev.get("img") or f'{ev.get("kind")} "{ev.get("text", "")}"'


def check(r, tl=None):
    probs = []
    for i, ln in enumerate(r.tl.lines, 1):
        bx = boxes(r, ln)
        for ev, b in bx:
            if ev.get("anim") == "drop" or ev.get("anim") == "slide":
                continue
            tag = f"frase {i}: {name(ev)}"
            if b[2] - b[0] > W - 40:
                probs.append(f"{tag} es más ancho que la pantalla")
            if b[1] < TOP - 10:
                probs.append(f"{tag} invade la zona de arriba (y={b[1]:.0f})")
            if b[3] > BOTTOM + 10 and ev.get("kind") != "stamp":
                probs.append(f"{tag} tapa los subtítulos (y={b[3]:.0f})")
            if b[2] > RIGHT_UI_X and b[3] > RIGHT_UI_Y:
                probs.append(f"{tag} queda bajo los botones de TikTok (x={b[2]:.0f})")
        for j in range(len(bx)):
            for k in range(j + 1, len(bx)):
                (e1, b1), (e2, b2) = bx[j], bx[k]
                if "stamp" in (e1.get("kind"), e2.get("kind")) or e1.get("behind") or e2.get("behind"):
                    continue
                if overlap(b1, b2) > 0.12:
                    probs.append(f"frase {i}: {name(e1)} y {name(e2)} se enciman ({overlap(b1, b2):.0%})")
    if tl is not None and not MIN_DUR <= tl.duration <= MAX_DUR:
        probs.append(f"duración {tl.duration:.1f}s fuera de {MIN_DUR}–{MAX_DUR}s")
    return probs


def sheet(r, out_path):
    """Hoja con el cuadro a la mitad de cada frase (para revisar a ojo)."""
    frames = []
    for ln in r.tl.lines:
        t = ln["start"] + 0.75 * (ln["end"] - ln["start"])
        im = r.frame(int(t * nbl.FPS)).convert("RGB")
        im.thumbnail((270, 480))
        frames.append(im)
    cols = 4
    rows = (len(frames) + cols - 1) // cols
    s = Image.new("RGB", (cols * 280, rows * 505), (30, 30, 30))
    d = ImageDraw.Draw(s)
    for i, im in enumerate(frames):
        x, y = (i % cols) * 280 + 5, (i // cols) * 505 + 5
        s.paste(im, (x, y))
        d.text((x + 4, y + 482), f"frase {i + 1}", fill=(255, 255, 255))
    s.save(out_path)
    return out_path


def main(path):
    ep = nbl.load_episode(path)
    out = os.path.join(nbl.ROOT, "output", ep.SLUG)
    tl = nbl.Timeline(ep, out, fake=True)
    r = nbl.Renderer(ep, tl)
    probs = check(r)
    print("Hoja:", sheet(r, os.path.join(out, "qa_hoja.png")))
    for p in probs:
        print("  ERROR:", p)
    print("QA visual:", "OK" if not probs else f"{len(probs)} problemas")
    return 1 if probs else 0


if __name__ == "__main__":
    sys.exit(max(main(p) for p in sys.argv[1:]))
