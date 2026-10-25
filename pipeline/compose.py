"""Compone el video final: frames de Blender + textos + audio.

Uso:
    python3 pipeline/compose.py output/ep01_control_mundial            # video completo
    python3 pipeline/compose.py output/ep01_control_mundial --preview 300,900   # PNGs de prueba

Necesita: timeline.json, frames/f_####.png (blender/scene.py --render) y
portraits/<robot>.png (blender/scene.py --portraits).
Salida: final.mp4 (voces + efectos + base musical) y final_sin_musica.mp4.
"""
import json
import math
import os
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfx  # noqa: E402
from textfx import draw_centered, draw_text, font, text_width, wrap_words  # noqa: E402

W, H = 1080, 1920
SAFE_R = W - 175        # columna de botones de TikTok
SUB_Y = 1300            # centro vertical de subtítulos (encima del límite inferior ~1450)
SUB_CX = 490            # centro horizontal (corrido a la izquierda por los botones)
SUB_W = 800
NAMES = {"claude": "CLAUDE", "deepseek": "DEEPSEEK", "mistral": "MISTRAL", "chatgpt": "CHATGPT",
         "grok": "GROK", "gemini": "GEMINI", "narrator": ""}
COLORS = {"claude": (217, 119, 87), "deepseek": (123, 147, 255), "mistral": (250, 80, 15),
          "chatgpt": (16, 190, 140), "grok": (255, 255, 255), "gemini": (169, 139, 255)}
BLACK = (0, 0, 0, 255)


def ease_pop(x):
    """0..1 -> escala con rebote (para animaciones de entrada)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return 1 + 0.18 * math.sin(x * math.pi) * (1 - x) * 3 - (1 - x) ** 3


def paste_scaled(base, layer, cx, cy, s):
    """Pega una capa RGBA escalada s alrededor de (cx, cy)."""
    if s <= 0.01:
        return
    if abs(s - 1) > 0.01:
        w, h = layer.size
        layer = layer.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR)
    base.alpha_composite(layer, (int(cx - layer.width / 2), int(cy - layer.height / 2)))


class Composer:
    def __init__(self, out):
        self.out = out
        with open(os.path.join(out, "timeline.json")) as f:
            self.tl = json.load(f)
        self.fps = self.tl["fps"]
        self.blocks = self.tl["blocks"]
        self.turns = [b for b in self.blocks if b["type"] == "turn"]
        self.hook, self.outro = self.blocks[0], self.blocks[-1]
        self.n_frames = self.tl["frames"]
        self.last_render = int(round(self.outro["start"] * self.fps))
        self.cache = {}

    # --- capas de texto ---------------------------------------------------------
    def text_layer(self, text, size, fill=(255, 255, 255, 255), stroke=10, fname="InterDisplay-Black.otf"):
        key = ("t", text, size, fill, stroke)
        if key not in self.cache:
            f = font(fname, size)
            lines = text.split("\n")
            w = int(max(text_width(ln, f) for ln in lines) + stroke * 2 + 40)
            h = int(size * 1.15 * len(lines) + stroke * 2 + 40)
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw_centered(sh, text, w / 2 + 6, h / 2 + 8, f, fill=(0, 0, 0, 160), stroke=stroke)
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
            draw_centered(im, text, w / 2, h / 2, f, fill=fill, stroke=stroke, stroke_fill=BLACK)
            self.cache[key] = im
        return self.cache[key]

    def pill(self, robot, idx):
        key = ("pill", robot)
        if key not in self.cache:
            col = COLORS[robot]
            f = font("InterDisplay-Black.otf", 46)
            label = NAMES[robot]
            tw = text_width(label, f)
            w, h = int(tw + 190), 84
            im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, w - 1, h - 1), 42, fill=(10, 12, 20, 220), outline=col + (255,), width=4)
            d.ellipse((8, 8, 76, 76), fill=col + (255,))
            num = f"{idx}/6"
            nf = font("InterDisplay-Black.otf", 28)
            txt_col = (0, 0, 0, 255) if sum(col) > 500 else (255, 255, 255, 255)
            d.text((42 - nf.getlength(num) / 2, 24), num, font=nf, fill=txt_col)
            draw_text(im, (100, 14), label, f, fill=(255, 255, 255, 255))
            self.cache[key] = im
        return self.cache[key]

    # --- subtítulos -------------------------------------------------------------
    @staticmethod
    def _norm(w):
        return re.sub(r"[^\wáéíóúñü]", "", w.lower())

    def key_mask(self, words, keys):
        mask = [False] * len(words)
        nw = [self._norm(w) for w in words]
        for k in keys:
            kw = [self._norm(x) for x in k.split()]
            for i in range(len(nw) - len(kw) + 1):
                if nw[i:i + len(kw)] == kw:
                    for j in range(len(kw)):
                        mask[i + j] = True
        return mask

    def subtitle(self, img, ln, t):
        words = ln["text"].split()
        weights = np.cumsum([len(w) + 2 for w in words])
        dur = ln["end"] - ln["start"]
        starts = [ln["start"] + dur * (weights[i - 1] if i else 0) / weights[-1] for i in range(len(words))]
        mask = self.key_mask(words, ln.get("key", []))
        col = COLORS.get(ln["speaker"], (255, 220, 60))
        f = font("InterDisplay-Black.otf", 74)
        lines = wrap_words(list(range(len(words))) and words, f, SUB_W)
        # índice global de palabras por línea
        idx, rows = 0, []
        for row in lines:
            rows.append(list(range(idx, idx + len(row))))
            idx += len(row)
        # máximo 2 renglones en pantalla: se muestra la "página" de la palabra actual
        cur = max([i for i in range(len(words)) if t >= starts[i] - 0.02] or [0])
        pages = [rows[i:i + 2] for i in range(0, len(rows), 2)]
        rows = next(pg for pg in pages if any(cur in r for r in pg))
        lh = 88
        y0 = SUB_Y - lh * len(rows) / 2
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        for r, row in enumerate(rows):
            text = " ".join(words[i] for i in row)
            x = SUB_CX - text_width(text, f) / 2
            y = y0 + r * lh
            for i in row:
                wtxt = words[i] + " "
                ww = text_width(wtxt, f)
                if t >= starts[i] - 0.02:
                    age = t - starts[i]
                    is_key = mask[i]
                    fill = (col + (255,)) if is_key else (255, 255, 255, 255)
                    if is_key and ln["speaker"] == "grok":  # Grok: texto negro sobre caja blanca
                        ImageDraw.Draw(layer).rounded_rectangle(
                            (x - 8, y + 6, x + text_width(words[i], f) + 8, y + 86), 12,
                            fill=(255, 255, 255, 255))
                        fill = (0, 0, 0, 255)
                    dy = -10 * max(0, 1 - age / 0.12) if age < 0.12 else 0
                    sw, sf = (2, (255, 255, 255, 255)) if fill == (0, 0, 0, 255) else (9, BLACK)
                    draw_text(shadow, (x + 5, y + 7 + dy), words[i], f, fill=(0, 0, 0, 170), stroke=10,
                              stroke_fill=(0, 0, 0, 170))
                    draw_text(layer, (x, y + dy), words[i], f, fill=fill, stroke=sw, stroke_fill=sf)
                x += ww
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(5)))
        img.alpha_composite(layer)

    def active_line(self, t):
        for tr in self.turns:
            L = tr["lines"]
            for k, ln in enumerate(L):
                nxt = L[k + 1]["start"] if k + 1 < len(L) else tr["end"]
                if ln["start"] - 0.05 <= t < nxt:
                    return ln
        return None

    # --- frames -------------------------------------------------------------------
    def base_frame(self, fr):
        p = os.path.join(self.out, "frames", f"f_{fr:04d}.png")
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        im = Image.open(p).convert("RGBA")
        if im.size != (W, H):
            im = im.resize((W, H), Image.LANCZOS)
        return im

    def outro_bg(self):
        if "outro_bg" not in self.cache:
            im = self.base_frame(self.last_render).filter(ImageFilter.GaussianBlur(14))
            dark = Image.new("RGBA", (W, H), (5, 7, 14, 170))
            im.alpha_composite(dark)
            self.cache["outro_bg"] = im
        return self.cache["outro_bg"].copy()

    def card(self, robot, label):
        key = ("card", robot)
        if key not in self.cache:
            cw, ch = 400, 300
            col = COLORS[robot]
            im = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            d.rounded_rectangle((0, 0, cw - 1, ch - 1), 28, fill=(12, 14, 24, 235), outline=col + (255,), width=5)
            pp = os.path.join(self.out, "portraits", f"{robot}.png")
            if os.path.exists(pp):
                por = Image.open(pp).convert("RGBA")
                s = 196 / por.height
                por = por.resize((int(por.width * s), 196), Image.LANCZOS)
                mask = Image.new("L", por.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle((0, 0, por.width - 1, por.height - 1), 20, fill=255)
                im.paste(por, ((cw - por.width) // 2, 10), mask)
            draw_centered(im, NAMES[robot], cw / 2, 226, font("InterDisplay-Black.otf", 32), fill=col + (255,))
            lf = font("InterDisplay-ExtraBold.otf", 26)
            rows = [" ".join(r) for r in wrap_words(label.split(), lf, cw - 30)]
            draw_centered(im, "\n".join(rows), cw / 2, 268 if len(rows) > 1 else 262, lf,
                          fill=(255, 255, 255, 255), line_gap=1.05)
            self.cache[key] = im
        return self.cache[key]

    def frame(self, fr):
        """fr: 1..n_frames"""
        t = (fr - 1) / self.fps
        if fr <= self.last_render:
            img = self.base_frame(fr)
        else:
            img = self.outro_bg()

        h = self.hook
        if t < h["end"]:
            texts = h["texts"]
            split = 1.2
            i = 0 if t < split else 1
            t0 = 0 if i == 0 else split
            lay = self.text_layer(texts[i], 66 if i == 0 else 56, stroke=10)
            paste_scaled(img, lay, SUB_CX, 640, ease_pop((t - t0) / 0.18))
            return img

        for tr in self.turns:
            if tr["start"] <= t < tr["end"]:
                pl = self.pill(tr["robot"], tr["index"])
                s = ease_pop((t - tr["start"]) / 0.2)
                paste_scaled(img, pl, 60 + pl.width / 2, 300 + pl.height / 2, s)
        ln = self.active_line(t)
        if ln:
            self.subtitle(img, ln, t)

        o = self.outro
        if t >= o["start"]:
            to = t - o["start"]
            lay = self.text_layer(o["text"], 70, stroke=10)
            paste_scaled(img, lay, SUB_CX, 360, ease_pop(to / 0.2))
            if o.get("note"):
                paste_scaled(img, self.text_layer(o["note"], 28, fill=(200, 210, 230, 255), stroke=4,
                                                  fname="InterDisplay-ExtraBold.otf"), SUB_CX, 470, 1.0)
            for k, tr in enumerate(self.turns):
                c = self.card(tr["robot"], o["labels"][tr["robot"]])
                cx = 80 + (k % 2) * 420 + 200
                cy = 520 + (k // 2) * 320 + 150
                paste_scaled(img, c, cx, cy, ease_pop((to - 0.25 - k * 0.12) / 0.22))
        return img

    # --- audio ----------------------------------------------------------------------
    @staticmethod
    def read_wav(p):
        with wave.open(p) as w:
            return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768

    def mix(self, music=True):
        n = int(self.n_frames / self.fps * sfx.SR) + sfx.SR
        voice = np.zeros(n)
        fx = np.zeros(n)

        def add(buf, x, t, gain=1.0):
            s = int(t * sfx.SR)
            if s >= n:
                return
            x = x[: n - s]
            buf[s:s + len(x)] += x * gain

        for bl in self.blocks:
            for ln in bl.get("lines", []):
                add(voice, self.read_wav(ln["wav"]), ln["start"])
        add(fx, sfx.whoosh(0.85, up=False), 0.05, 0.7)
        add(fx, sfx.impact(), 0.9, 0.75)
        for tr in self.turns:
            add(fx, sfx.whoosh(0.4), tr["start"], 0.6)
            add(fx, sfx.pop(), tr["start"] + 0.05, 0.6)
            for ln in tr["lines"]:
                gl = ln.get("gag") or []
                for g in [gl] if isinstance(gl, str) else gl:
                    if g == "screen:slides":
                        for k in range(5):
                            add(fx, sfx.click(), ln["start"] + k * (ln["end"] - ln["start"]) / 5, 0.9)
                    elif g in sfx.GAG_SFX:
                        add(fx, sfx.GAG_SFX[g](), ln["start"], 0.8)
        o = self.outro["start"]
        add(fx, sfx.chime(), o, 0.8)
        for k in range(6):
            add(fx, sfx.pop(), o + 0.25 + k * 0.12, 0.45)

        out = voice + fx * 0.55
        if music:
            bed = sfx.music_bed(n / sfx.SR)[:n]
            # ducking: baja la música cuando hablan
            env = np.abs(voice)
            k = int(0.15 * sfx.SR)
            env = np.convolve(env, np.ones(k) / k, mode="same")
            duck = 1 - 0.6 * np.clip(env * 8, 0, 1)
            out += bed * duck * 0.9
        out = out[: int(self.n_frames / self.fps * sfx.SR)]
        out /= max(1e-6, np.max(np.abs(out))) / 0.89
        path = os.path.join(self.out, "mix.wav" if music else "mix_sin_musica.wav")
        with wave.open(path, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sfx.SR)
            w.writeframes((out * 32767).astype(np.int16).tobytes())
        return path

    # --- render -----------------------------------------------------------------------
    def encode(self):
        a_music, a_dry = self.mix(True), self.mix(False)
        video = os.path.join(self.out, "final.mp4")
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(self.fps), "-i", "-", "-i", a_music,
               "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-b:a", "192k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
               "-movflags", "+faststart", "-shortest", video]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for fr in range(1, self.n_frames + 1):
            proc.stdin.write(self.frame(fr).convert("RGB").tobytes())
            if fr % 100 == 0:
                print(f"  frame {fr}/{self.n_frames}")
        proc.stdin.close()
        proc.wait()
        dry = os.path.join(self.out, "final_sin_musica.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", a_dry, "-map", "0:v",
                        "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-shortest", dry], check=True)
        print("Listo:", video, "y", dry)


def main():
    out = os.path.abspath(sys.argv[1])
    c = Composer(out)
    if "--preview" in sys.argv:
        frames = [int(x) for x in sys.argv[sys.argv.index("--preview") + 1].split(",")]
        for fr in frames:
            p = os.path.join(out, f"compose_{fr:04d}.png")
            c.frame(fr).convert("RGB").save(p)
            print(p)
    elif "--audio" in sys.argv:
        print(c.mix(True), c.mix(False))
    else:
        c.encode()


if __name__ == "__main__":
    main()
