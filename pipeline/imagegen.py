"""Genera imágenes del canal con la API de Gemini (Google) y las deja listas para usar.

Uso:
    python3 pipeline/imagegen.py sticker "a cartoon octopus waving" assets/art/raw/pulpo.jpg
    python3 pipeline/imagegen.py fondo "an underwater ocean floor" assets/art/raw/oceano.jpg
    python3 pipeline/imagegen.py newton "Newton holding an apple, surprised" assets/art/raw/x.jpg

Modos:
    sticker  piezas sueltas sobre fondo verde (luego: pipeline/cutout.py)
    fondo    fondo vertical 9:16 sin personajes
    newton   Newton con sus imágenes de referencia, sobre verde (consistencia de personaje)

La clave la inyecta el proxy del entorno (encabezado x-goog-api-key); no se lee de ningún archivo.
Tope: MAX_PER_MONTH imágenes por mes, registradas en assets/art/ledger.json.
"""
import base64
import datetime
import json
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "assets", "art", "ledger.json")
MODEL = os.environ.get("IMAGEGEN_MODEL", "gemini-3.1-flash-image")
MAX_PER_MONTH = int(os.environ.get("IMAGEGEN_MAX_PER_MONTH", "60"))
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

STYLE = ("cartoon illustration, bold black outlines, flat vibrant colors with soft cel shading, "
         "same art style as the reference images if any")
STICKER = (STYLE + ", sticker style with thin white border, each item fully separated with space "
           "between them, isolated on a solid pure green background (#00FF00), no shadows on the "
           "background, high resolution")
BACKGROUND = (STYLE + ", vertical 9:16 composition, no characters, no text, empty open floor or "
              "ground in the center foreground where a character can stand, high resolution")
NEWTON = ("Isaac Newton cartoon character exactly like the reference images: long curly grey wig, "
          "dark navy coat with buttons, dark vest, white cravat, dark knee breeches, white stockings, "
          "black shoes with gold buckles. ")
NEWTON_REFS = ["assets/art/newton/pose_senalando.png", "assets/art/newton/cara_neutral.png"]


def _ledger():
    if os.path.exists(LEDGER):
        with open(LEDGER) as f:
            return json.load(f)
    return []


def used_this_month():
    month = datetime.date.today().strftime("%Y-%m")
    return sum(1 for e in _ledger() if e["date"].startswith(month))


def _inline(path):
    mime = "image/png" if path.endswith(".png") else "image/jpeg"
    with open(os.path.join(ROOT, path), "rb") as f:
        return {"inlineData": {"mimeType": mime, "data": base64.b64encode(f.read()).decode()}}


def generate(mode, prompt, out, refs=None):
    if used_this_month() >= MAX_PER_MONTH:
        raise SystemExit(f"Tope mensual alcanzado ({MAX_PER_MONTH} imágenes). No se generó nada.")
    if mode == "sticker":
        text, aspect, refs = f"{prompt}. {STICKER}", "9:16", refs or []
    elif mode == "fondo":
        text, aspect, refs = f"{prompt}. {BACKGROUND}", "9:16", refs or []
    elif mode == "newton":
        text, aspect = f"{NEWTON}{prompt}. {STICKER}", "9:16"
        refs = (refs or []) + NEWTON_REFS
    else:
        raise SystemExit(f"Modo desconocido: {mode}")
    parts = [_inline(r) for r in refs] + [{"text": text}]
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": aspect}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        data = json.load(r)
    img = next((p["inlineData"] for p in data["candidates"][0]["content"]["parts"]
                if "inlineData" in p), None)
    if not img:
        raise SystemExit("La API no devolvió imagen: " + json.dumps(data)[:300])
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "wb") as f:
        f.write(base64.b64decode(img["data"]))
    led = _ledger()
    led.append({"date": datetime.datetime.now().isoformat(timespec="seconds"), "mode": mode,
                "model": MODEL, "prompt": prompt, "out": os.path.relpath(out, ROOT),
                "tokens": data.get("usageMetadata", {}).get("totalTokenCount")})
    with open(LEDGER, "w") as f:
        json.dump(led, f, indent=1, ensure_ascii=False)
    print(f"Listo: {out} ({used_this_month()}/{MAX_PER_MONTH} este mes)")
    return out


if __name__ == "__main__":
    generate(sys.argv[1], sys.argv[2], sys.argv[3])
