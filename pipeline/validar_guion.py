"""Valida guiones base (guiones/NNN_slug.md) contra el formato de guiones/GUIA.md.

Uso:  python3 pipeline/validar_guion.py guiones/047_cielo_azul.md [...]
      python3 pipeline/validar_guion.py guiones/          (todos)
Sale con código 1 si algún guion tiene errores. Las advertencias no bloquean.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ART = os.path.join(ROOT, "assets", "art")

NEWTON_POSES = {"explicando_pluma", "senalando", "asustado", "pensando", "manzana_pensando"}
COLEGA_POSES = {"presentando", "explicando", "senalando", "asustado", "pensando"}
COLEGAS = {"darwin", "tesla", "curie", "turing", "godel", "ada", "hipatia", "anning", "franklin"}
FIELDS = ["n", "slug", "categoria", "idea", "colega", "badge", "cta", "estado"]
SECTIONS = ["Guion", "Datos que hay que verificar", "Imágenes nuevas", "Notas"]
TAGS = {"gancho", "dato", "giro", "cierre"}
BAD_WORDS = ["pedo", "cabrón", "cabron", "verga", "chingar", "chingad", "chingón", "chingon", "pinche",
             "mierda", "culero", "wey", "güey", "guey", "puta", "puto", "pendej", "joder", "coño", "sangre a chorros"]
MIN_WORDS, MAX_WORDS, MAX_LINE_WORDS = 70, 120, 25
LINE_RE = re.compile(r"^(\d+)\. \[(\w+)\] (NEWTON|COLEGA:(\w+)) \(([\w]+)\) \| fondo: ([\w]+)\s*$")


def fondos():
    return {f[:-len("_vertical.png")] for f in os.listdir(os.path.join(ART, "fondos"))
            if f.endswith("_vertical.png")}


def objetos():
    return {f[:-4] for f in os.listdir(os.path.join(ART, "objetos")) if f.endswith(".png")}


def words(s):
    return len(re.findall(r"[\wáéíóúñü°%]+", s, re.I))


def validate(path):
    errs, warns = [], []
    txt = open(path, encoding="utf-8").read()
    name = os.path.basename(path)
    m = re.match(r"^---\n(.*?)\n---\n", txt, re.S)
    if not m:
        return ["falta el encabezado entre líneas ---"], warns, None
    meta = {}
    for ln in m.group(1).splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    for f in FIELDS:
        if not meta.get(f):
            errs.append(f"falta el campo '{f}'")
    fm = re.match(r"^(\d{3})_([a-z0-9_]+)\.md$", name)
    if not fm:
        errs.append("nombre de archivo debe ser NNN_slug.md (minúsculas, sin acentos)")
    else:
        if meta.get("n", "").isdigit() and int(meta["n"]) != int(fm.group(1)):
            errs.append(f"n={meta.get('n')} no coincide con el archivo")
        if meta.get("slug") and meta["slug"] != fm.group(2):
            errs.append(f"slug '{meta.get('slug')}' no coincide con el archivo")
    colega = meta.get("colega", "")
    if colega and colega != "ninguno" and colega not in COLEGAS:
        errs.append(f"colega desconocido: {colega}")

    body = txt[m.end():]
    heads = re.findall(r"^## (.+?)\s*$", body, re.M)
    for s in SECTIONS:
        if s not in heads:
            errs.append(f"falta la sección '## {s}'")
    sec = {h: c for h, c in re.findall(r"^## (.+?)\s*\n(.*?)(?=^## |\Z)", body, re.M | re.S)}
    new_imgs = set(re.findall(r"^- (objetos|fondos)/([\w]+)\s*:", sec.get("Imágenes nuevas", ""), re.M))
    new_obj = {n for k, n in new_imgs if k == "objetos"}
    new_bg = {n.replace("_vertical", "") for k, n in new_imgs if k == "fondos"}
    if len(new_obj) > 4:
        errs.append(f"{len(new_obj)} objetos nuevos (máximo 4)")
    if len(new_bg) > 1:
        errs.append(f"{len(new_bg)} fondos nuevos (máximo 1)")
    if not re.search(r"^- .+", sec.get("Datos que hay que verificar", ""), re.M):
        errs.append("'Datos que hay que verificar' está vacío")

    lines = []
    cur = None
    for raw in sec.get("Guion", "").splitlines():
        if not raw.strip():
            continue
        lm = LINE_RE.match(raw.strip())
        if lm:
            cur = {"n": int(lm.group(1)), "tag": lm.group(2), "who": lm.group(3), "col": lm.group(4),
                   "pose": lm.group(5), "bg": lm.group(6), "dice": None, "pantalla": None}
            lines.append(cur)
        elif raw.strip().startswith("DICE:") and cur:
            cur["dice"] = raw.strip()[5:].strip()
        elif raw.strip().startswith("PANTALLA:") and cur:
            cur["pantalla"] = raw.strip()[9:].strip()
        else:
            errs.append(f"línea con formato inválido: '{raw.strip()[:70]}'")
    if not 6 <= len(lines) <= 10:
        errs.append(f"{len(lines)} líneas de guion (deben ser 6 a 10)")
    if lines:
        if [l["n"] for l in lines] != list(range(1, len(lines) + 1)):
            errs.append("la numeración de líneas no es 1, 2, 3…")
        if lines[0]["tag"] != "gancho":
            errs.append("la línea 1 debe ser [gancho]")
        if lines[-1]["tag"] != "cierre":
            errs.append("la última línea debe ser [cierre]")
    total = 0
    colega_lines = 0
    stamps = 0
    bgs, objs = fondos() | new_bg, objetos() | new_obj
    for l in lines:
        tag = f"línea {l['n']}"
        if l["tag"] not in TAGS:
            errs.append(f"{tag}: etiqueta [{l['tag']}] inválida")
        if l["tag"] == "gancho" and l["n"] != 1 or l["tag"] == "cierre" and l["n"] != len(lines):
            errs.append(f"{tag}: [{l['tag']}] fuera de lugar")
        if l["who"] == "NEWTON":
            if l["pose"] != "voz" and l["pose"] not in NEWTON_POSES:
                errs.append(f"{tag}: pose de Newton inválida '{l['pose']}'")
        else:
            colega_lines += 1
            if l["col"] not in COLEGAS:
                errs.append(f"{tag}: colega desconocido '{l['col']}'")
            elif l["col"] != colega:
                errs.append(f"{tag}: el colega '{l['col']}' no es el del encabezado ('{colega}')")
            if l["pose"] not in COLEGA_POSES:
                errs.append(f"{tag}: pose de colega inválida '{l['pose']}'")
        if l["bg"] not in bgs:
            errs.append(f"{tag}: fondo '{l['bg']}' no existe ni está en 'Imágenes nuevas'")
        if l["pose"] != "voz" and l["bg"] not in {"estudio"} | new_bg:
            warns.append(f"{tag}: personaje de cuerpo entero en fondo '{l['bg']}' (¿no sería 'voz'?)")
        if not l["dice"]:
            errs.append(f"{tag}: falta DICE")
            continue
        if l["pantalla"] is None:
            errs.append(f"{tag}: falta PANTALLA")
        else:
            for o in re.findall(r"objetos/([\w]+)", l["pantalla"]):
                if o not in objs:
                    errs.append(f"{tag}: objetos/{o} no existe ni está en 'Imágenes nuevas'")
            stamps += len(re.findall(r"\bsello\b", l["pantalla"]))
        w = words(l["dice"])
        total += w
        if w > MAX_LINE_WORDS:
            errs.append(f"{tag}: {w} palabras (máximo {MAX_LINE_WORDS})")
        low = l["dice"].lower()
        for b in BAD_WORDS:
            if re.search(r"\b" + re.escape(b), low):
                errs.append(f"{tag}: palabra prohibida '{b}'")
    if lines and not lines[-1].get("dice", "").rstrip().endswith(("?", "👇")) and "?" not in lines[-1].get("dice", ""):
        warns.append("el cierre no tiene pregunta para comentarios")
    if colega == "ninguno" and colega_lines:
        errs.append("hay líneas de colega pero el encabezado dice 'ninguno'")
    if colega_lines > 2:
        errs.append(f"el colega tiene {colega_lines} líneas (máximo 2)")
    if stamps > 1:
        errs.append(f"{stamps} sellos (máximo 1)")
    if lines and not MIN_WORDS <= total <= MAX_WORDS:
        errs.append(f"{total} palabras en total (deben ser {MIN_WORDS}–{MAX_WORDS})")
    first = lines[0]["dice"].lower() if lines and lines[0]["dice"] else ""
    if re.match(r"^(hola|qué onda,? (amigos|banda|gente)|hoy (les|te) (traigo|voy))", first):
        errs.append("el gancho empieza con saludo/presentación")
    return errs, warns, {"palabras": total, "lineas": len(lines), "colega": colega, "nuevas": len(new_imgs)}


def main(args):
    paths = []
    for a in args or [os.path.join(ROOT, "guiones")]:
        if os.path.isdir(a):
            paths += sorted(os.path.join(a, f) for f in os.listdir(a) if re.match(r"^\d{3}_.*\.md$", f))
        else:
            paths.append(a)
    bad = 0
    for p in paths:
        errs, warns, info = validate(p)
        name = os.path.basename(p)
        if errs:
            bad += 1
            print(f"✗ {name}")
            for e in errs:
                print(f"    ERROR: {e}")
        else:
            print(f"✓ {name}  ({info['palabras']} palabras, {info['lineas']} líneas, colega {info['colega']}, "
                  f"{info['nuevas']} imágenes nuevas)")
        for w in warns:
            print(f"    aviso: {w}")
    print(f"\n{len(paths) - bad}/{len(paths)} OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
