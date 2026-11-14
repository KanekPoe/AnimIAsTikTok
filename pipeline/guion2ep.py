"""Convierte un guion base (guiones/NNN_slug.md) en un episodio del motor (episodes/nblNNN_slug.py).

Uso:  python3 pipeline/guion2ep.py guiones/123_usb_agujero_negro.md [...]

Reglas de acomodo (para que nadie tenga que poner coordenadas a mano):
- Las líneas seguidas con el mismo fondo forman una escena.
- Fondo "estudio": salen los personajes. Si en la escena habla un colega, salen Newton (izquierda)
  y el colega (derecha); si no, Newton solo (al centro, o a la izquierda si hay objetos o textos).
- Otros fondos: voz en off, sin personajes, con los objetos al centro.
- PANTALLA: `objetos/x`, `texto "..."` y `sello "..."` se acomodan en la zona libre de cada
  disposición, escalados para que quepan y sin encimarse (el sello sí va encima, a propósito).
- La voz ("say") lleva los números en palabras (numeros.py); el subtítulo ("text") lleva cifras.
"""
import os
import pprint
import re
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from numeros import a_palabras  # noqa: E402
from textfx import font, text_width  # noqa: E402
from validar_guion import LINE_RE, validate  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets", "art")
W, H = 1080, 1920
GOLD = (255, 194, 26, 255)
WHITE = (255, 255, 255, 255)

# Disposición de personajes en el estudio
SOLO_CENTER = {"newton": {"x": 0.5, "feet": 1790, "h": 1466}}
SOLO_SIDE = {"newton": {"x": 0.31, "feet": 1790, "h": 1300}}
DUO = {"newton": {"x": 0.26, "feet": 1790, "h": 1180}, "colega": {"x": 0.75, "feet": 1790, "h": 1180}}
# Zonas libres para objetos y textos (fracciones de pantalla: x0, y0, x1, y1).
# Respetan la zona segura de TikTok: insignia arriba (~y 0.17), botones a la derecha (x > 0.84),
# subtítulos abajo (y > 0.64).
ZONES = {"voz": (0.08, 0.20, 0.84, 0.60), "solo_side": (0.52, 0.20, 0.86, 0.58),
         "duo": (0.22, 0.19, 0.78, 0.335)}
# Colegas que en su dibujo miran a la izquierda del espectador: a la derecha de Newton van bien;
# los que miran a la derecha se voltean para que lo vean a él.
LOOKS_RIGHT = set()


def parse(path):
    txt = open(path, encoding="utf-8").read()
    meta = dict(re.findall(r"^(\w+): (.*)$", txt.split("---")[1], re.M))
    body = txt.split("## Guion", 1)[1].split("## Datos que hay que verificar")[0]
    lines, cur = [], None
    for raw in body.splitlines():
        s = raw.strip()
        m = LINE_RE.match(s)
        if m:
            cur = {"tag": m.group(2), "who": (m.group(4) or "newton"), "pose": m.group(5),
                   "bg": m.group(6), "dice": "", "pantalla": ""}
            lines.append(cur)
        elif s.startswith("DICE:"):
            cur["dice"] = s[5:].strip()
        elif s.startswith("PANTALLA:"):
            cur["pantalla"] = s[9:].strip()
    return meta, lines


def items(pantalla):
    out = []
    for part in [p.strip() for p in re.split(r"\s*·\s*", pantalla) if p.strip()]:
        m = re.match(r'^(texto|sello|anim)\s+"(.*)"$', part)
        if m:
            out.append((m.group(1), m.group(2)))
        elif part.startswith("objetos/"):
            out.append(("obj", part))
    return out


def label_size(text, max_w, size=100):
    """Tamaño de letra para que el texto (con contorno y margen) quepa en max_w píxeles."""
    while size > 40:
        if text_width(text, font("InterDisplay-Black.otf", size)) + 0.7 * size + 24 <= max_w:
            return size
        size -= 4
    return size


def layout_events(its, zone):
    """Eventos del motor para los objetos/textos de una línea dentro de la zona dada."""
    x0, y0, x1, y1 = zone[0] * W, zone[1] * H, zone[2] * W, zone[3] * H
    zw, zh = x1 - x0, y1 - y0
    labels = [t for k, t in its if k == "texto"]
    stamps = [t for k, t in its if k == "sello"]
    objs = [o for k, o in its if k == "obj"]
    evs, y = [], y0
    anims = [t for k, t in its if k == "anim"]
    if anims:  # animación a pantalla completa (p. ej. "sistema_solar"); los textos van arriba
        for i, t in enumerate(labels):
            size = min(label_size(t, zw), 96)
            evs.append({"kind": "label", "text": t, "size": size, "color": GOLD, "anim": "pop",
                        "x": 0.5, "y": 0.215 + 0.075 * i, "at": 0.05})
        for a in anims:
            if a == "sistema_solar":
                evs.append({"kind": "sistema_solar", "x": 0.5, "y": 0.43, "scale": 36, "tilt": 0.45,
                            "star_au": 9.0, "grow_at": 0.45, "grow": 1.5, "at": 0})
        return evs
    if labels and objs and zw > 1.8 * zh:  # zona baja y ancha (dos personajes): todo en una fila
        row = []
        for t in labels:
            size = min(label_size(t, zw / (len(labels) + len(objs))), int((zh - 24) / 1.7))
            fw = text_width(t, font("InterDisplay-Black.otf", size)) + 0.7 * size + 24
            row.append(("texto", t, fw, size))
        for o in objs:
            im = Image.open(os.path.join(ART, o + ".png"))
            hh = zh * 0.95
            row.append(("obj", o, hh * im.width / im.height, hh))
        k = min(1.0, zw * 0.96 / sum(r[2] for r in row))
        x = x0 + (zw - k * sum(r[2] for r in row)) / 2
        for i, (kind, v, w, a) in enumerate(row):
            cx = (x + k * w / 2) / W
            if kind == "texto":
                evs.append({"kind": "label", "text": v, "size": max(40, int(a * k)), "color": GOLD, "anim": "pop",
                            "x": round(cx, 4), "y": round((y0 + zh / 2) / H, 4), "at": 0.12 + 0.1 * i})
            else:
                evs.append({"img": v, "h": int(a * k), "anim": "pop", "x": round(cx, 4),
                            "y": round((y0 + zh / 2) / H, 4), "at": 0.05 + 0.1 * i})
            x += k * w
        labels, objs = [], []
    for i, t in enumerate(labels):
        size = min(label_size(t, zw), 96 if objs else 120)
        lh = 1.7 * size + 24
        evs.append({"kind": "label", "text": t, "size": size, "color": GOLD, "anim": "pop",
                    "x": round((x0 + zw / 2) / W, 4), "y": round((y + lh / 2) / H, 4), "at": 0.12 + 0.1 * i})
        y += lh
    if objs:
        rest = y1 - y
        cell_w = zw / len(objs)
        for i, o in enumerate(objs):
            im = Image.open(os.path.join(ART, o + ".png"))
            h = min(rest * 0.95, (cell_w * 0.92) * im.height / im.width, 640 if len(objs) == 1 else 460)
            evs.append({"img": o, "h": int(h), "anim": "pop", "x": round((x0 + cell_w * (i + 0.5)) / W, 4),
                        "y": round((y + rest / 2) / H, 4), "at": 0.05 + 0.25 * i})
    for t in stamps:
        size = label_size(t, 0.7 * W, 130)  # el sello va al centro de la pantalla, encima de todo
        evs.append({"kind": "stamp", "text": t, "anim": "stamp", "size": size, "rot": -6,
                    "x": 0.5, "y": round((y0 + zh / 2) / H, 4), "at": 0.45,
                    "color": (220, 30, 45, 255)})
    return evs


def keys_for(dice, its):
    shown = " ".join(t for k, t in its if k != "obj").lower()
    keys = []
    for w in dice.split():
        c = w.lower().strip("¿?¡!.,:;…\"'()")
        if c and (any(ch.isdigit() for ch in c) or (len(c) > 3 and c in shown)):
            keys.append(c)
    return keys[:4]


def convert(path):
    errs, _, _ = validate(path)
    if errs:
        raise SystemExit(f"{path}: el guion no pasa el validador:\n  " + "\n  ".join(errs))
    meta, lines = parse(path)
    colega = meta.get("colega", "ninguno")
    # Portada: TikTok usa el primer cuadro como miniatura. Para que cada video se distinga en el
    # perfil, el gancho abre en el fondo del tema (el primer fondo que no es el estudio), con su
    # objeto y su texto visibles desde el cuadro 0; Newton aparece desde la segunda frase.
    # Se desactiva con "portada: estudio" en el encabezado del guion.
    # "portada: <fondo> [objetos/<x>]" elige el fondo y el objeto de la portada a mano.
    port = meta.get("portada", "").split()
    alt = port[0] if port else next((l["bg"] for l in lines if l["bg"] != "estudio"), None)
    if alt != "estudio" and alt and lines[0]["bg"] == "estudio" and lines[0]["who"] == "newton":
        first = dict(lines[0], bg=alt, pose="voz")
        if not any(k == "obj" for k, _ in items(first["pantalla"])):
            obj = port[1] if len(port) > 1 else next(
                (o for l in lines for k, o in items(l["pantalla"]) if k == "obj"), None)
            if obj:
                first["pantalla"] = obj + (" · " + first["pantalla"] if first["pantalla"] else "")
        lines = [first] + lines[1:]
    # escenas: líneas seguidas con el mismo fondo
    groups = []
    for ln in lines:
        if groups and groups[-1][0]["bg"] == ln["bg"]:
            groups[-1].append(ln)
        else:
            groups.append([ln])
    scenes = []
    for g in groups:
        bg = g[0]["bg"]
        has_vis = any(items(l["pantalla"]) for l in g)
        if bg != "estudio":
            mode, cast = "voz", []
        elif colega != "ninguno" and any(l["who"] == colega for l in g):
            mode = "duo"
            cfg_c = dict(DUO["colega"], **({"flip": True} if colega in LOOKS_RIGHT else {}))
            cast = [["newton", DUO["newton"]], [colega, cfg_c]]
        elif has_vis:
            mode, cast = "solo_side", [["newton", SOLO_SIDE["newton"]]]
        else:
            mode, cast = "solo_center", [["newton", SOLO_CENTER["newton"]]]
        out_lines = []
        for l in g:
            its = items(l["pantalla"])
            if l["tag"] == "cierre":  # al final la pregunta (CTA) ya ocupa la parte de arriba
                its = [it for it in its if it[0] != "texto"]
            say = a_palabras(l["dice"])
            ln = {"who": l["who"], "say": say}
            if say != l["dice"]:
                ln["text"] = l["dice"]
            if l["pose"] != "voz":
                ln["pose"] = l["pose"]
            ln["key"] = keys_for(l["dice"], its)
            zone = ZONES.get(mode, ZONES["solo_side"]) if mode != "solo_center" else ZONES["voz"]
            if mode == "solo_side" and its and all(k == "texto" for k, _ in its):
                zone = (0.34, 0.19, 0.86, 0.30)  # solo texto: ancho completo arriba de la cabeza de Newton
            ln["events"] = layout_events(its, zone)
            if l is lines[0]:  # portada: todo visible desde el primer cuadro
                for ev in ln["events"]:
                    if ev.get("anim") == "pop":
                        ev["anim"], ev["at"], ev["dt"] = "static", 0, -1.0  # ya está en el cuadro 0
            out_lines.append(ln)
        scenes.append({"bg": bg + "_vertical", "cast": cast, "lines": out_lines})
    n = int(meta["n"])
    slug = f"nbl{n:03d}_{meta['slug']}"
    ep = {"SLUG": slug, "BADGE": meta["badge"], "SOURCE": None, "CTA": meta["cta"], "SCENES": scenes}
    out = os.path.join(ROOT, "episodes", slug + ".py")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f'"""Generado automáticamente desde {os.path.relpath(path, ROOT)} por pipeline/guion2ep.py.\n\n'
                f'No editar a mano: corrige el guion y vuelve a convertir.\n"""\n')
        for k in ("SLUG", "BADGE", "SOURCE", "CTA"):
            f.write(f"{k} = {ep[k]!r}\n")
        f.write("SCENES = " + pprint.pformat(scenes, width=110, sort_dicts=False) + "\n")
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("Episodio:", convert(p))
