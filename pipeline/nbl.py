"""Motor de videos de Newton Bien Loco (2D, por recortes).

Uso:
    python3 pipeline/nbl.py episodes/nbl01_manzana.py                 # video completo
    python3 pipeline/nbl.py episodes/nbl01_manzana.py --preview 1,4.5  # cuadros de prueba (segundos)

El episodio define escenas -> frases. Cada frase: texto (voz y subtítulo), pose de Newton,
palabras clave, cámara y eventos (objetos que aparecen, caen, sellos, líneas...).
Salida: output/<slug>/final.mp4
"""
import importlib.util
import json
import math
import os
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_qc  # noqa: E402
import sfx  # noqa: E402
from textfx import draw_text, font, text_width, wrap_words  # noqa: E402
from tts_gemini import VOICES, synth  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets", "art")
W, H, FPS = 1080, 1920, 30
GOLD = (255, 194, 26, 255)
WHITE = (255, 255, 255, 255)
BLACK = (0, 0, 0, 255)
GAP, LEAD, OUTRO = 0.18, 0.25, 1.6
MAX_ACCENTS = 3
SUB_Y, SUB_CX, SUB_W = 1330, 500, 820
rng = random.Random(4)


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def load_episode(path):
    spec = importlib.util.spec_from_file_location("ep", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ease_out_back(x):
    x = min(max(x, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def read_wav(p):
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


_IMG = {}


def img(name, height=None):
    """Imagen de la biblioteca (assets/art/<name>.png), opcionalmente escalada a una altura."""
    key = (name, height)
    if key not in _IMG:
        if (name, None) not in _IMG:
            p = name if os.path.isabs(name) else os.path.join(ART, name + ".png")
            _IMG[(name, None)] = Image.open(p).convert("RGBA")
        base = _IMG[(name, None)]
        if height:
            base = base.resize((max(1, round(base.width * height / base.height)), height), Image.LANCZOS)
        _IMG[key] = base
    return _IMG[key]


def text_sticker(text, size=110, fill=WHITE, stroke=12, box=None, rot=0):
    """Texto grande tipo sticker (opcionalmente dentro de una caja de color)."""
    f = font("InterDisplay-Black.otf", size)
    tw = int(text_width(text, f))
    pad = int(size * 0.35)
    im = Image.new("RGBA", (tw + pad * 2 + stroke * 2, int(size * 1.35) + pad + stroke * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle((stroke, stroke, im.width - stroke, im.height - stroke), size // 4,
                            fill=box, outline=WHITE, width=stroke)
        draw_text(im, (pad + stroke, pad * 0.35 + stroke), text, f, fill=fill)
    else:
        draw_text(im, (pad + stroke, pad * 0.35 + stroke), text, f, fill=fill, stroke=stroke,
                  stroke_fill=BLACK)
    return im.rotate(rot, expand=True, resample=Image.BICUBIC) if rot else im


def arrow(length=260, width=40, color=(255, 194, 26, 255), down=True):
    im = Image.new("RGBA", (width * 3 + 24, length + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = im.width // 2
    pts = [(cx - width // 2, 12), (cx + width // 2, 12), (cx + width // 2, length - width * 1.4),
           (cx + width * 1.5, length - width * 1.4), (cx, length + 10), (cx - width * 1.5, length - width * 1.4),
           (cx - width // 2, length - width * 1.4)]
    d.polygon(pts, fill=color, outline=BLACK, width=8)
    return im if down else im.rotate(180)


# ----------------------------------------------------------------------------
# Animación: sistema solar y estrella que crece (escala real de órbitas)
# ----------------------------------------------------------------------------
PLANETAS = [("Mercurio", 0.39, (170, 160, 150), 5), ("Venus", 0.72, (230, 200, 140), 7),
            ("Tierra", 1.0, (80, 150, 255), 7), ("Marte", 1.52, (220, 90, 50), 6),
            ("Júpiter", 5.2, (215, 170, 120), 13), ("Saturno", 9.54, (230, 210, 150), 11)]
ROTULOS = {"Tierra", "Júpiter", "Saturno"}


def draw_solar(layer, cx, cy, ev, age, dur):
    """Órbitas a escala (vista inclinada) y una estrella que crece de Sol a gigante.

    ev: "scale" px por UA, "tilt" achatamiento de las órbitas, "star_au" radio final en UA,
    "grow_at" fracción de la frase en que empieza a crecer, "grow" segundos que tarda.
    """
    d = ImageDraw.Draw(layer)
    S, tilt = ev.get("scale", 40), ev.get("tilt", 0.45)
    fade = min(1.0, max(age, 0) / 0.3)
    a = int(255 * fade)
    p = ease((age - ev.get("grow_at", 0.45) * dur) / ev.get("grow", 1.5))
    r_star = 9 + (ev.get("star_au", 9.0) * S - 9) * p
    for name, au, col, rad in PLANETAS:  # órbitas
        rx, ry = au * S, au * S * tilt
        d.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(255, 255, 255, int(110 * fade)), width=3)
    pos = []
    for k, (name, au, col, rad) in enumerate(PLANETAS):  # planetas (giran según Kepler, acelerado)
        ang = 0.9 + k * 1.7 + age * 1.6 / au ** 1.5
        x, y = cx + au * S * math.cos(ang), cy + au * S * tilt * math.sin(ang)
        pos.append((name, au, col, rad, x, y))
        if au * S <= r_star:  # dentro de la estrella: solo se ve si aún no lo alcanza
            if math.hypot(x - cx, y - cy) > r_star:
                d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col + (a,), outline=(0, 0, 0, a), width=2)
    # estrella: de amarilla a roja, con resplandor
    c0, c1 = (255, 220, 90), (235, 75, 40)
    col = tuple(int(c0[i] + (c1[i] - c0[i]) * p) for i in range(3))
    glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    gr = r_star * 1.10 + 6
    ImageDraw.Draw(glow).ellipse((cx - gr, cy - gr, cx + gr, cy + gr), fill=col + (int(90 * fade),))
    layer.alpha_composite(glow.filter(ImageFilter.GaussianBlur(14)))
    d.ellipse((cx - r_star, cy - r_star, cx + r_star, cy + r_star), fill=col + (a,), outline=(0, 0, 0, a), width=4)
    for name, au, col_p, rad, x, y in pos:  # órbitas más grandes que la estrella: el planeta va por fuera
        if au * S > r_star:
            d.ellipse((x - rad, y - rad, x + rad, y + rad), fill=col_p + (a,), outline=(0, 0, 0, a), width=2)
    f = font("InterDisplay-Black.otf", 34)
    for name, au, col_p, rad, x, y in pos:  # rótulos de los planetas que siguen a la vista
        if name in ROTULOS and (au * S > r_star or math.hypot(x - cx, y - cy) > r_star):
            draw_text(layer, (x - text_width(name, f) / 2, y + rad + 4), name, f, fill=(255, 255, 255, a),
                      stroke=6, stroke_fill=(0, 0, 0, a))


# ----------------------------------------------------------------------------
# Línea de tiempo
# ----------------------------------------------------------------------------
class Timeline:
    def __init__(self, ep, out, fake=False):
        """fake=True: sin voces (duración estimada por palabras), para revisar acomodo sin gastar."""
        self.ep = ep
        self.out = out
        os.makedirs(os.path.join(out, "audio"), exist_ok=True)
        self.lines = []
        t = LEAD
        for si, sc in enumerate(ep.SCENES):
            for li, ln in enumerate(sc["lines"]):
                wav = os.path.join(out, "audio", f"{si:02d}_{li:02d}.wav")
                if fake:
                    x = np.zeros(int(48000 * max(1.5, len(ln["say"].split()) / 2.6)), np.float32)
                else:
                    synth(ln["say"], wav, voice=VOICES[ln.get("who", "newton")], alt=ln.get("text"))
                    x = read_wav(wav)
                d = len(x) / 48000
                hop = 48000 // FPS
                env = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x), hop)])
                env = np.clip(env / (np.percentile(env, 95) + 1e-6), 0, 1)
                self.lines.append({**ln, "scene": si, "start": t, "end": t + d, "wav": wav, "env": env})
                if not fake:
                    print(f"  {d:4.1f}s  {ln['say']}")
                t += d + GAP
            t += 0.1
        self.duration = t + OUTRO
        self.frames = int(self.duration * FPS)
        # inicio/fin de cada escena
        self.scenes = []
        for si in range(len(ep.SCENES)):
            ls = [l for l in self.lines if l["scene"] == si]
            self.scenes.append((ls[0]["start"] - (LEAD if si == 0 else GAP), ls[-1]["end"] + GAP))
        self.scenes[-1] = (self.scenes[-1][0], self.duration)
        # eventos con tiempos absolutos
        self.events = []
        for li, ln in enumerate(self.lines):
            for ev in ln.get("events", []):
                t0 = ln["start"] + ev.get("at", 0) * (ln["end"] - ln["start"]) + ev.get("dt", 0)
                until = ev.get("until", "line")
                if "dur" in ev:
                    t1 = t0 + ev["dur"]
                elif until == "line":
                    t1 = ln["end"] + GAP
                elif until == "scene":
                    t1 = self.scenes[ln["scene"]][1]
                elif until == "end":
                    t1 = self.duration + 1
                else:
                    t1 = self.lines[min(li + int(until), len(self.lines) - 1)]["end"]
                self.events.append({**ev, "t0": t0, "t1": t1, "scene": ln["scene"]})

    def line_at(self, t):
        for ln in self.lines:
            if ln["start"] - GAP <= t < ln["end"] + GAP:
                return ln
        return None

    def scene_at(self, t):
        for i, (a, b) in enumerate(self.scenes):
            if a <= t < b:
                return i
        return len(self.scenes) - 1


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
class Renderer:
    """Dibuja cada cuadro. Personajes: Newton y colegas (rig en assets/art/.../rig/<pose>/).

    Cada frase lleva "who" (por defecto "newton"): solo ese personaje mueve la boca y su "pose"
    cambia; los demás conservan la última pose. Una escena pone personajes con "newton": cfg
    (formato viejo) o "cast": [[nombre, cfg], ...].
    """

    def __init__(self, ep, tl):
        self.ep, self.tl = ep, tl
        chars = {ln.get("who", "newton") for ln in tl.lines}
        for sc in ep.SCENES:
            chars |= {c for c, _ in self.cast(sc)}
        self.blinks, self.pose_changes = {}, {}
        for k, ch in enumerate(sorted(chars)):
            r = random.Random(4 + k)
            t, bl = 1.0 + 0.7 * k, []
            while t < tl.duration:
                bl.append(t)
                t += r.uniform(2.3, 4.2)
            self.blinks[ch] = bl
            changes, prev = [], None
            for ln in tl.lines:
                if ln.get("who", "newton") == ch and ln.get("pose") and ln["pose"] != prev:
                    changes.append((ln["start"] - 0.05, ln["pose"]))
                    prev = ln["pose"]
            if not changes:
                changes = [(0.0, "senalando" if ch == "newton" else "presentando")]
            self.pose_changes[ch] = changes

    @staticmethod
    def cast(sc):
        if sc.get("cast"):
            return [tuple(c) for c in sc["cast"]]
        return [("newton", sc["newton"])] if sc.get("newton") else []

    # --- personajes ---------------------------------------------------------------
    def pose_at(self, t, ch="newton"):
        changes = self.pose_changes[ch]
        pose, since = changes[0][1], -9
        for tc, p in changes:
            if t >= tc:
                pose, since = p, tc
        return pose, t - since

    def character(self, frame, t, ch, cfg):
        pose, age = self.pose_at(t, ch)
        rig = f"newton/rig/{pose}" if ch == "newton" else f"colegas/{ch}/rig/{pose}"
        ln = self.tl.line_at(t)
        talking = 0.0
        if ln and ln.get("who", "newton") == ch and ln["start"] <= t < ln["end"]:
            i = int((t - ln["start"]) * FPS)
            env = ln["env"]
            talking = float(np.mean(env[max(0, i - 1):i + 1])) if i < len(env) else 0
        state = "boca_abierta" if talking > 0.28 else "boca_cerrada"
        if any(0 <= t - b < 0.1 for b in self.blinks[ch]):
            state = "ojos_cerrados"
        if not os.path.exists(os.path.join(ART, rig, state + ".png")):
            state = "base"
        h = cfg["h"]
        base = img(f"{rig}/{state}", h)
        # respiración (desfasada por personaje), rebote al hablar y "pop" al cambiar de pose
        s = 1 + 0.008 * math.sin(t * 2.4 + (0 if ch == "newton" else 1.7))
        if age < 0.3:
            s *= 0.9 + 0.1 * ease_out_back(age / 0.3)
        sy = s * (1 + 0.012 * talking)
        sp = base.resize((max(1, round(base.width * s)), max(1, round(base.height * sy))), Image.BILINEAR)
        if cfg.get("flip"):
            sp = sp.transpose(Image.FLIP_LEFT_RIGHT)
        x = int(cfg["x"] * W - sp.width / 2)
        y = int(cfg["feet"] - sp.height - 6 * talking)
        # sombra
        sh = Image.new("RGBA", (int(sp.width * 0.8), 60), (0, 0, 0, 0))
        ImageDraw.Draw(sh).ellipse((0, 0, sh.width, sh.height), fill=(0, 0, 0, 90))
        frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)),
                              (int(cfg["x"] * W - sh.width / 2), int(cfg["feet"] - 34)))
        frame.alpha_composite(sp, (x, y))

    def newton(self, frame, t, cfg):  # compatibilidad
        self.character(frame, t, "newton", cfg)

    # --- eventos -----------------------------------------------------------------
    def event_image(self, ev):
        if "img" in ev:
            return img(ev["img"], ev.get("h"))
        key = ("ev", id(ev))
        if key not in _IMG:
            k = ev["kind"]
            if k == "stamp":
                _IMG[key] = text_sticker(ev["text"], ev.get("size", 150), WHITE, 12,
                                         box=ev.get("color", (220, 30, 45, 255)), rot=ev.get("rot", 10))
            elif k == "label":
                _IMG[key] = text_sticker(ev["text"], ev.get("size", 90), ev.get("color", WHITE), 10)
            elif k == "arrow":
                _IMG[key] = arrow(ev.get("length", 260), down=ev.get("down", True))
            elif k == "sistema_solar":  # estado final, para medir su tamaño en la QA
                S = ev.get("scale", 40)
                rx = max(9.54 * S, ev.get("star_au", 9.0) * S * 1.10) + 12
                ry = max(9.54 * S * ev.get("tilt", 0.45), ev.get("star_au", 9.0) * S * 1.10) + 12
                lay = Image.new("RGBA", (int(2 * rx), int(2 * ry)), (0, 0, 0, 0))
                draw_solar(lay, rx, ry, ev, 99.0, 1.0)
                _IMG[key] = lay
        return _IMG[key]

    def draw_event(self, frame, ev, t):
        age, left = t - ev["t0"], ev["t1"] - t
        if age < 0 or left < 0:
            return
        anim = ev.get("anim", "pop")
        x, y = ev.get("x", 0.5) * W, ev.get("y", 0.5) * H
        if ev.get("kind") == "sistema_solar":
            layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw_solar(layer, ev.get("x", 0.5) * W, ev.get("y", 0.46) * H, ev, age, ev["t1"] - ev["t0"])
            frame.alpha_composite(layer)
            return
        if ev.get("kind") == "line":  # línea punteada que crece (distancias)
            p = ease(age / ev.get("grow", 1.0))
            x0, y0, x1, y1 = ev["from"][0] * W, ev["from"][1] * H, ev["to"][0] * W, ev["to"][1] * H
            d = ImageDraw.Draw(frame)
            n = 26
            for i in range(n):
                a, b = i / n, (i + 0.55) / n
                if a > p:
                    break
                b = min(b, p)
                d.line((x0 + (x1 - x0) * a, y0 + (y1 - y0) * a, x0 + (x1 - x0) * b, y0 + (y1 - y0) * b),
                       fill=ev.get("color", GOLD), width=12)
            return
        im = self.event_image(ev)
        s, oy = 1.0, 0.0
        if anim == "pop":
            s = ease_out_back(age / 0.28)
            oy = 8 * math.sin(age * 2.5)
        elif anim == "static":  # visible desde el primer cuadro (portada del video)
            oy = 8 * math.sin(age * 2.5)
        elif anim == "stamp":
            s = 1 + 1.6 * (1 - ease(age / 0.16))
        elif anim == "drop":
            fall = ev.get("fall", 0.55)
            y_top = ev.get("from_y", 0.1) * H
            if age < fall:
                q = (age / fall) ** 2
                y = y_top + (y - y_top) * q
            else:
                b = age - fall
                y -= max(0.0, 90 * math.sin(min(b / 0.3, 1) * math.pi)) * (1 if b < 0.3 else 0)
        elif anim == "slide":
            x = x + (1 - ease(age / 0.35)) * W * ev.get("from_dx", -1)
        if left < 0.15:  # salida
            s *= max(0.0, left / 0.15)
        if s <= 0.02:
            return
        if abs(s - 1) > 0.01:
            im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
        frame.alpha_composite(im, (int(x - im.width / 2), int(y + oy - im.height / 2)))

    # --- textos -----------------------------------------------------------------
    def subtitles(self, frame, t):
        ln = self.tl.line_at(t)
        if not ln or t > ln["end"] + 0.1:
            return
        text = ln.get("text", ln["say"])
        words = text.split()
        dur = ln["end"] - ln["start"]
        w8 = np.cumsum([len(w) + 2 for w in words])
        starts = [ln["start"] + dur * (w8[i - 1] if i else 0) / w8[-1] for i in range(len(words))]
        keys = {k.lower() for k in ln.get("key", [])}
        f = font("InterDisplay-Black.otf", 76)
        rows, idx = [], 0
        for row in wrap_words(words, f, SUB_W):
            rows.append(list(range(idx, idx + len(row))))
            idx += len(row)
        cur = max([i for i in range(len(words)) if t >= starts[i] - 0.02] or [0])
        pages = [rows[i:i + 2] for i in range(0, len(rows), 2)]
        rows = next(p for p in pages if any(cur in r for r in p))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        y0 = SUB_Y - 90 * len(rows) / 2
        for r, row in enumerate(rows):
            line = " ".join(words[i] for i in row)
            x = SUB_CX - text_width(line, f) / 2
            for i in row:
                ww = text_width(words[i] + " ", f)
                if t >= starts[i] - 0.02:
                    clean = words[i].lower().strip("¿?¡!.,:;…")
                    col = GOLD if clean in keys else WHITE
                    pop = -8 * max(0.0, 1 - (t - starts[i]) / 0.1)
                    draw_text(lay, (x, y0 + r * 90 + pop), words[i], f, fill=col, stroke=10, stroke_fill=BLACK)
                x += ww
        frame.alpha_composite(lay)

    def overlays(self, frame, t):
        ep = self.ep
        last = self.tl.lines[-1]
        if t >= last["start"] and getattr(ep, "CTA", None):  # la pregunta final ocupa la parte de arriba
            c = _IMG.setdefault(("cta",), text_sticker(ep.CTA, 58, WHITE, 9))
            if c.width > W - 60:
                c = c.resize((W - 60, int(c.height * (W - 60) / c.width)), Image.LANCZOS)
                _IMG[("cta",)] = c
            s = ease_out_back((t - last["start"]) / 0.3)
            if s > 0.02:
                ci = c.resize((max(1, int(c.width * s)), max(1, int(c.height * s))), Image.BILINEAR)
                frame.alpha_composite(ci, (int(W / 2 - ci.width / 2), int(330 - ci.height / 2)))
            return
        if getattr(ep, "BADGE", None):
            b = _IMG.setdefault(("badge",), text_sticker(ep.BADGE, 58, BLACK, 8, box=GOLD))
            frame.alpha_composite(b, (int(SUB_CX - b.width / 2), 270))
        if getattr(ep, "SOURCE", None):
            s = _IMG.setdefault(("source",), text_sticker(ep.SOURCE, 30, WHITE, 5))
            frame.alpha_composite(s, (int(SUB_CX - s.width / 2), 395))

    # --- cuadro completo ------------------------------------------------------------
    def camera(self, t):
        """Zoom y foco interpolados entre frases."""
        z, fx, fy = 1.0, 0.5, 0.5
        for ln in self.tl.lines:
            cam = ln.get("cam")
            if cam and t >= ln["start"]:
                p = ease((t - ln["start"]) / 0.6)
                z = z + (cam.get("zoom", 1.0) - z) * p
                fx = fx + (cam.get("fx", 0.5) - fx) * p
                fy = fy + (cam.get("fy", 0.5) - fy) * p
        return z, fx, fy

    def frame(self, fr):
        t = fr / FPS
        si = self.tl.scene_at(t)
        sc = self.ep.SCENES[si]
        frame = img("fondos/" + sc["bg"]).copy()
        if frame.size != (W, H):
            frame = frame.resize((W, H), Image.LANCZOS)
        for ev in self.tl.events:  # eventos detrás de Newton
            if ev["scene"] == si and ev.get("behind"):
                self.draw_event(frame, ev, t)
        for ch, cfg in self.cast(sc):
            self.character(frame, t, ch, cfg)
        for ev in self.tl.events:
            if (ev["scene"] == si or ev.get("until") == "end") and not ev.get("behind"):
                self.draw_event(frame, ev, t)
        z, fx, fy = self.camera(t)
        if z > 1.001:
            cw, ch = W / z, H / z
            x0 = min(max(fx * W - cw / 2, 0), W - cw)
            y0 = min(max(fy * H - ch / 2, 0), H - ch)
            frame = frame.resize((W, H), Image.BILINEAR, box=(x0, y0, x0 + cw, y0 + ch))
        a, _ = self.tl.scenes[si]
        if si > 0 and t - a < 0.2:  # destello de transición
            frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(255 * (1 - (t - a) / 0.2)))))
        self.overlays(frame, t)
        self.subtitles(frame, t)
        return frame


# ----------------------------------------------------------------------------
# Audio y exportación
# ----------------------------------------------------------------------------
def mix(tl, path, music=True):
    n = int(tl.duration * sfx.SR)
    voice, fx = np.zeros(n), np.zeros(n)

    def add(buf, x, t, g=1.0):
        s = int(t * sfx.SR)
        if 0 <= s < n:
            x = x[: n - s]
            buf[s:s + len(x)] += x * g

    for ln in tl.lines:
        add(voice, read_wav(ln["wav"]), ln["start"])
    for i, (a, _) in enumerate(tl.scenes[1:], 1):
        add(fx, sfx.whoosh(0.35), a - 0.15, 0.3)  # transición suave entre escenas
    # Efectos de acento: máximo MAX_ACCENTS por video (pedido del creador: no saturar).
    # Prioridad: sellos > caídas (una por grupo) > líneas > apariciones. Los cambios de pose no suenan.
    cands, seen_drop = [], set()
    for ev in tl.events:
        a = ev.get("anim", "pop")
        if a == "stamp":
            cands.append((0, ev["t0"], "stamp", ev))
        elif a == "drop":
            key = round(ev["t0"] - ev.get("at", 0), 1)  # caídas de la misma frase = un solo sonido
            if key not in seen_drop:
                seen_drop.add(key)
                cands.append((1, ev["t0"], "drop", ev))
        elif ev.get("kind") == "line":
            cands.append((2, ev["t0"], "line", ev))
        elif a == "static" or ev["t0"] < 0 or ev.get("kind") == "sistema_solar":  # sin efecto propio
            continue
        else:
            cands.append((3, ev["t0"], "pop", ev))
    top = sorted(cands, key=lambda c: (c[0], c[1]))[:MAX_ACCENTS]  # sin comparar dicts en empates
    for _, t0, kind, ev in sorted(top, key=lambda c: c[1]):
        if kind == "stamp":
            add(fx, sfx.stamp(), t0, 1.0)
        elif kind == "drop":
            add(fx, sfx.thud(), t0 + ev.get("fall", 0.55), 0.9)
        elif kind == "line":
            add(fx, sfx.sweep(300, 900, ev.get("grow", 1.0)) * 0.15, t0, 1.0)
        else:
            add(fx, sfx.pop(), t0, 0.5)
    add(fx, sfx.chime(), tl.lines[-1]["start"], 0.5)
    out = voice + fx * 0.55
    if music:
        bed = sfx.music_bed(n / sfx.SR)[:n]
        bed = np.pad(bed, (0, n - len(bed)))  # el redondeo puede dejarla 1 muestra corta
        env = np.convolve(np.abs(voice), np.ones(7200) / 7200, mode="same")
        out += bed * (1 - 0.6 * np.clip(env * 8, 0, 1)) * 0.9
    out /= max(1e-6, np.max(np.abs(out))) / 0.89
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sfx.SR)
        w.writeframes((out * 32767).astype(np.int16).tobytes())
    return path


def main():
    ep = load_episode(sys.argv[1])
    out = os.path.join(ROOT, "output", ep.SLUG)
    print("Voces:")
    tl = Timeline(ep, out)
    r = Renderer(ep, tl)
    print(f"Duración: {tl.duration:.1f}s ({tl.frames} cuadros)")
    if "--preview" in sys.argv:
        for s in sys.argv[sys.argv.index("--preview") + 1].split(","):
            p = os.path.join(out, f"preview_{float(s):05.1f}.png")
            r.frame(int(float(s) * FPS)).convert("RGB").save(p)
            print(p)
        return
    # Control visual obligatorio: nada fuera de la zona segura, encimado ni duración rara.
    import qa_visual
    vprobs = qa_visual.check(r, tl)
    print("Hoja de revisión:", qa_visual.sheet(r, os.path.join(out, "qa_hoja.png")))
    if vprobs:
        raise SystemExit("QA visual falló, no se exporta:\n  " + "\n  ".join(vprobs))
    # Control de audio obligatorio (lección 1): ninguna voz con chasquidos ni mezcla saturada.
    probs = []
    for ln in tl.lines:
        meta = ln["wav"] + ".json"
        speed = json.load(open(meta))["tempo"] if os.path.exists(meta) else 1.0  # voz acelerada (lección 2)
        probs += audio_qc.check_voice(read_wav(ln["wav"]), name=f"voz '{ln['say'][:30]}…'", speed=speed)
    audio = mix(tl, os.path.join(out, "mix.wav"))
    probs += audio_qc.check_mix(read_wav(audio))
    audio_qc.assert_ok(probs)
    video = os.path.join(out, "final.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", audio, "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
           "-movflags", "+faststart", "-shortest", video]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fr in range(tl.frames):
        proc.stdin.write(r.frame(fr).convert("RGB").tobytes())
        if fr % 150 == 0:
            print(f"  cuadro {fr}/{tl.frames}")
    proc.stdin.close()
    proc.wait()
    print("Listo:", video)


if __name__ == "__main__":
    main()
