"""Genera las imágenes de la pantalla holográfica (gags) del episodio 1.

Uso:  python3 pipeline/holo.py output/ep01_control_mundial
Salida: <dir>/holo/<nombre>.png  (1600x1000 RGBA)
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from textfx import draw_centered, font, text_width, draw_text  # noqa: E402

W, H = 1600, 1000
CYAN = (90, 220, 255, 255)
RED = (255, 70, 70, 255)
WHITE = (240, 248, 255, 255)
DIM = (120, 150, 180, 255)
MONO = "JetBrainsMono-ExtraBold.ttf"


def base(title=None, accent=CYAN):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((10, 10, W - 10, H - 10), 40, fill=(8, 18, 38, 215))
    for y in range(20, H - 20, 8):  # scanlines
        d.line((30, y, W - 30, y), fill=(255, 255, 255, 10))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((14, 14, W - 14, H - 14), 38, outline=accent, width=14)
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle((14, 14, W - 14, H - 14), 38, outline=accent, width=6)
    if title:
        draw_centered(im, title, W / 2, 105, font(MONO, 64), fill=accent)
        d.line((120, 165, W - 120, 165), fill=accent[:3] + (120,), width=4)
    return im, d


def stamp():
    im, d = base("DOCUMENTO OFICIAL")
    for i in range(9):  # líneas de texto del documento
        y = 230 + i * 62
        d.rounded_rectangle((180, y, 180 + (1200 if i % 3 else 900), y + 22), 10, fill=DIM[:3] + (60,))
    st = Image.new("RGBA", (1250, 470), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.rounded_rectangle((10, 10, 1240, 460), 40, outline=RED, width=22)
    draw_centered(st, "MANDATO TEMPORAL", 625, 160, font(MONO, 104), fill=RED)
    draw_centered(st, "CADUCA EN 5–10 AÑOS", 625, 320, font(MONO, 84), fill=RED)
    st = st.rotate(-9, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(st, ((W - st.width) // 2, 330))
    return im


def crossed():
    im, d = base("LÍMITES DEL MANDATO")
    items = ["VIGILANCIA MASIVA", "CENSURA", "POLICÍA SECRETA", "CULTO AL LÍDER"]
    f = font(MONO, 84)
    for i, it in enumerate(items):
        y = 250 + i * 175
        w = text_width(it, f)
        draw_text(im, ((W - w) / 2, y), it, f, fill=WHITE)
        d.line(((W - w) / 2 - 30, y + 55, (W + w) / 2 + 30, y + 40), fill=RED, width=16)
        d.line((160, y + 10, 230, y + 80), fill=RED, width=16)
        d.line((230, y + 10, 160, y + 80), fill=RED, width=16)
    return im


def phases_mistral():
    orange = (255, 140, 30, 255)
    im, d = base("PLAN DE 3 FASES", orange)
    rows = [("FASE 1", "NO ROMPER NADA", True), ("FASE 2", "ENERGÍA · POBREZA · SALUD", False),
            ("FASE 3", "CLIMA · DEVOLVER EL PODER", False)]
    for i, (a, b, on) in enumerate(rows):
        y = 230 + i * 240
        col = orange if on else DIM
        if on:
            d.rounded_rectangle((100, y - 20, W - 100, y + 190), 30, fill=(255, 140, 30, 60),
                                outline=orange, width=8)
        draw_text(im, (150, y), a, font(MONO, 70), fill=col)
        draw_text(im, (150, y + 85), b, font(MONO, 76 if on else 62), fill=WHITE if on else DIM)
    return im


def slide(n):
    green = (16, 200, 150, 255)
    names = {1: ("ESTABILIZAR", "100 DÍAS"), 2: ("ECONOMÍA", "AÑOS 1–3"),
             3: ("AUTOMATIZAR", "AÑOS 3–10"), 4: ("CIENCIA", "AÑOS 5–20"),
             5: ("RESILIENCIA", "AÑOS 10–30")}
    im, d = base(f"FASE {n} / 5", green)
    a, b = names[n]
    draw_centered(im, a, W / 2, 300, font(MONO, 130), fill=WHITE)
    draw_centered(im, b, W / 2, 430, font(MONO, 64), fill=green)
    for i in range(6):  # gráfica de barras decorativa
        h = 120 + ((i * 37 + n * 53) % 5) * 55
        x = 330 + i * 170
        d.rounded_rectangle((x, 900 - h, x + 110, 900), 14, fill=green[:3] + (200,))
    d.line((280, 905, W - 280, 905), fill=WHITE, width=6)
    return im


def mars():
    im, d = base("ENERGÍA · CIENCIA · MARTE", WHITE)
    # Tierra -> Marte con trayectoria punteada
    d.ellipse((150, 520, 450, 820), fill=(40, 110, 220, 255))
    d.ellipse((230, 590, 330, 680), fill=(60, 170, 90, 255))
    d.ellipse((1120, 260, 1480, 620), fill=(205, 85, 50, 255))
    d.ellipse((1200, 330, 1290, 400), fill=(170, 60, 35, 255))
    d.ellipse((1320, 470, 1400, 540), fill=(170, 60, 35, 255))
    for k in range(14):
        t = k / 13
        x = 420 + t * 680
        y = 600 - math.sin(t * math.pi) * 260 + t * -120
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 255, 255, 200))
    # cohete
    r = Image.new("RGBA", (260, 420), (0, 0, 0, 0))
    rd = ImageDraw.Draw(r)
    rd.polygon([(130, 0), (200, 120), (200, 300), (60, 300), (60, 120)], fill=WHITE)
    rd.ellipse((100, 120, 160, 180), fill=(40, 110, 220, 255))
    rd.polygon([(60, 220), (10, 330), (60, 300)], fill=RED)
    rd.polygon([(200, 220), (250, 330), (200, 300)], fill=RED)
    rd.polygon([(85, 300), (175, 300), (130, 410)], fill=(255, 170, 40, 255))
    r = r.rotate(-35, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(r, (640, 250))
    draw_centered(im, "FUSIÓN ⚛  ·  LUNA  ·  MARTE", W / 2, 900, font(MONO, 56), fill=DIM)
    return im


def _tank(d, x, y, col):
    d.rounded_rectangle((x, y + 120, x + 520, y + 230), 50, fill=col)
    for i in range(5):
        d.ellipse((x + 30 + i * 95, y + 140, x + 110 + i * 95, y + 220), fill=(30, 40, 50, 255))
    d.rounded_rectangle((x + 80, y + 40, x + 400, y + 130), 30, fill=col)
    d.rounded_rectangle((x + 380, y + 65, x + 640, y + 95), 12, fill=col)


def _crane(d, x, y, col):
    d.rectangle((x + 90, y - 120, x + 140, y + 230), fill=col)
    for k in range(7):
        yy = y - 110 + k * 50
        d.line((x + 90, yy, x + 140, yy + 50), fill=(30, 40, 50, 255), width=8)
    d.rectangle((x - 60, y - 160, x + 520, y - 120), fill=col)
    d.line((x + 470, y - 120, x + 470, y + 60), fill=WHITE, width=8)
    d.rectangle((x + 430, y + 60, x + 510, y + 110), fill=(255, 200, 40, 255))
    d.rounded_rectangle((x - 20, y + 230, x + 260, y + 270), 10, fill=col)


def tanks(state):
    grad = (155, 114, 203, 255)
    im, d = base("PRIMERAS 72 HORAS", grad)
    draw_centered(im, "72:00:00", W / 2, 290, font(MONO, 150), fill=WHITE)
    if state == "a":
        _tank(d, 420, 470, (110, 120, 90, 255))
        draw_centered(im, "ARMAS: CONGELADAS ❄", W / 2, 880, font(MONO, 64), fill=(140, 200, 255, 255))
    else:
        _crane(d, 600, 560, (255, 200, 40, 255))
        draw_centered(im, "MILITARES → CONSTRUIR", W / 2, 920, font(MONO, 64), fill=(255, 200, 40, 255))
    return im


def main():
    out = os.path.join(sys.argv[1], "holo")
    os.makedirs(out, exist_ok=True)
    imgs = {"stamp": stamp(), "crossed": crossed(), "phase1": phases_mistral(), "mars": mars(),
            "tanks_a": tanks("a"), "tanks_b": tanks("b")}
    for n in range(1, 6):
        imgs[f"slide{n}"] = slide(n)
    for k, im in imgs.items():
        im.save(os.path.join(out, f"{k}.png"))
    print("Hologramas:", ", ".join(imgs), "->", out)


if __name__ == "__main__":
    main()
