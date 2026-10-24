"""Utilidades de texto con PIL: fuentes del proyecto, emoji a color, contorno y maquetado."""
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "assets", "fonts")
EMOJI_FONTS = ["/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
               "/System/Library/Fonts/Apple Color Emoji.ttc",
               "C:/Windows/Fonts/seguiemj.ttf"]


@lru_cache(None)
def font(name="InterDisplay-Black.otf", size=80):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


@lru_cache(None)
def _emoji_font():
    for p in EMOJI_FONTS:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, 109)
            except OSError:
                pass
    return None


def is_emoji(ch):
    o = ord(ch)
    return o >= 0x1F000 or 0x2600 <= o <= 0x27BF


@lru_cache(None)
def emoji_img(ch, size):
    ef = _emoji_font()
    if ef is None:
        return None
    im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((0, 0), ch, font=ef, embedded_color=True)
    im = im.crop(im.getbbox() or (0, 0, 1, 1))
    s = size / im.height
    return im.resize((max(1, int(im.width * s)), size), Image.LANCZOS)


def _runs(text):
    """Separa texto normal y emojis."""
    runs, buf = [], ""
    for ch in text:
        if ch == "\ufe0f":
            continue
        if is_emoji(ch):
            if buf:
                runs.append(("t", buf))
                buf = ""
            runs.append(("e", ch))
        else:
            buf += ch
    if buf:
        runs.append(("t", buf))
    return runs


def text_width(text, f):
    w = 0
    for kind, s in _runs(text):
        if kind == "t":
            w += f.getlength(s)
        else:
            im = emoji_img(s, int(f.size * 0.95))
            w += (im.width if im else 0) + f.size * 0.08
    return w


def draw_text(img, xy, text, f, fill=(255, 255, 255, 255), stroke=0,
              stroke_fill=(0, 0, 0, 255)):
    """Dibuja texto (con emojis) con la esquina superior izquierda en xy."""
    d = ImageDraw.Draw(img)
    x, y = xy
    for kind, s in _runs(text):
        if kind == "t":
            d.text((x, y), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
            x += f.getlength(s)
        else:
            im = emoji_img(s, int(f.size * 0.95))
            if im:
                img.alpha_composite(im, (int(x + f.size * 0.04), int(y + f.size * 0.12)))
                x += im.width + f.size * 0.08
    return x


def draw_centered(img, text, cx, cy, f, fill=(255, 255, 255, 255), stroke=0,
                  stroke_fill=(0, 0, 0, 255), line_gap=1.12):
    """Varias líneas (separadas por \\n) centradas en (cx, cy)."""
    lines = text.split("\n")
    lh = f.size * line_gap
    y = cy - lh * len(lines) / 2
    for ln in lines:
        w = text_width(ln, f)
        draw_text(img, (cx - w / 2, y), ln, f, fill, stroke, stroke_fill)
        y += lh


def wrap_words(words, f, max_w):
    """Agrupa palabras en líneas que no superen max_w píxeles."""
    lines, cur = [], []
    for w in words:
        test = " ".join(x for x in cur + [w])
        if cur and text_width(test, f) > max_w:
            lines.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        lines.append(cur)
    return lines
