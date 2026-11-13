"""Convierte cifras a palabras en español (México) para que la voz las lea bien.

    >>> a_palabras("Hace 13,800 millones de años, a -180 °C y 2 cm.")
    'Hace trece mil ochocientos millones de años, a menos ciento ochenta grados y dos centímetros.'

Los subtítulos conservan las cifras (campo "text" del episodio); solo la voz ("say") usa esto.
Convenciones: coma = miles ("13,800"), punto = decimales ("3.8" -> "tres punto ocho").
"""
import re

_U = ["cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve", "diez", "once",
      "doce", "trece", "catorce", "quince", "dieciséis", "diecisiete", "dieciocho", "diecinueve", "veinte",
      "veintiuno", "veintidós", "veintitrés", "veinticuatro", "veinticinco", "veintiséis", "veintisiete",
      "veintiocho", "veintinueve"]
_D = {3: "treinta", 4: "cuarenta", 5: "cincuenta", 6: "sesenta", 7: "setenta", 8: "ochenta", 9: "noventa"}
_C = {1: "ciento", 2: "doscientos", 3: "trescientos", 4: "cuatrocientos", 5: "quinientos", 6: "seiscientos",
      7: "setecientos", 8: "ochocientos", 9: "novecientos"}

# unidad -> (singular, plural); se reconocen solo justo después de una cifra
UNITS = {"°C": ("grado", "grados"), "°": ("grado", "grados"), "km/h": ("kilómetro por hora", "kilómetros por hora"),
         "km/s": ("kilómetro por segundo", "kilómetros por segundo"), "m/s": ("metro por segundo", "metros por segundo"),
         "km": ("kilómetro", "kilómetros"), "cm": ("centímetro", "centímetros"), "mm": ("milímetro", "milímetros"),
         "m": ("metro", "metros"), "kg": ("kilo", "kilos"), "g": ("gramo", "gramos"), "mL": ("mililitro", "mililitros"),
         "TB": ("terabyte", "terabytes"), "GB": ("gigabyte", "gigabytes"), "V": ("voltio", "voltios"),
         "mA": ("miliamperio", "miliamperios"), "Hz": ("hercio", "hercios"), "K": ("kelvin", "kelvin"),
         "%": ("por ciento", "por ciento"), "lpm": ("latido por minuto", "latidos por minuto")}
_SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹", "0123456789")


def _lt100(n):
    if n < 30:
        return _U[n]
    d, u = divmod(n, 10)
    return _D[d] + ("" if u == 0 else " y " + _U[u])


def _lt1000(n):
    if n == 100:
        return "cien"
    c, r = divmod(n, 100)
    parts = ([_C[c]] if c else []) + ([_lt100(r)] if r else [])
    return " ".join(parts) or "cero"


def entero(n):
    """Entero a palabras (hasta billones, escala larga: 10^12 = un billón)."""
    if n < 0:
        return "menos " + entero(-n)
    if n < 1000:
        return _lt1000(n)
    for div, sing, plur in ((10 ** 12, "un billón", "billones"), (10 ** 6, "un millón", "millones")):
        if n >= div:
            q, r = divmod(n, div)
            head = sing if q == 1 else _apocope(entero(q)) + " " + plur
            return head + ("" if r == 0 else " " + entero(r))
    q, r = divmod(n, 1000)
    head = "mil" if q == 1 else _apocope(_lt1000(q)) + " mil"
    return head + ("" if r == 0 else " " + _lt1000(r))


def _apocope(words):
    """'uno' -> 'un' ante sustantivo ('veintiún mil', 'treinta y un millones')."""
    if words.endswith("veintiuno"):
        return words[:-len("veintiuno")] + "veintiún"
    if words.endswith("uno"):
        return words[:-1]
    return words


def numero(s, before_noun=False):
    """'13,800' -> 'trece mil ochocientos'; '3.8' -> 'tres punto ocho'."""
    s = s.replace(",", "")
    if "." in s:
        a, b = s.split(".", 1)
        dec = " ".join(_U[int(c)] for c in b) if len(b) > 2 or b.startswith("0") else entero(int(b))
        return entero(int(a or 0)) + " punto " + dec
    w = entero(int(s))
    return _apocope(w) if before_noun else w


_NUM = r"(?<![\w.,])(-|−)?(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?"
_UNIT_RE = "|".join(re.escape(u) for u in sorted(UNITS, key=len, reverse=True))
_TOKEN = re.compile(_NUM + r"(?:\s?(" + _UNIT_RE + r")(?![\wáéíóúñ]))?")


def a_palabras(text):
    # potencias "10⁶⁶" -> "diez a la sesenta y seis"
    text = re.sub(r"10([⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "diez a la " + entero(int(m.group(1).translate(_SUP))), text)
    text = text.translate(_SUP)
    text = re.sub(r"(\d)\s*[–-]\s*(\d)", r"\1 a \2", text)  # rangos "1665–1666"
    text = re.sub(r"\b(\d+)([A-Z])\b", r"\1 \2", text)  # "5D" -> "cinco D", "3D" -> "tres D"

    def rep(m):
        sign, ent, dec, unit = m.group(1), m.group(2), m.group(3) or "", m.group(4)
        nxt = text[m.end():m.end() + 2]
        noun_follows = bool(unit) or bool(re.match(r"\s[a-záéíóúñ]", nxt))
        w = numero(ent + dec, before_noun=noun_follows and not dec)
        if sign:
            w = "menos " + w
        if unit:
            sing, plur = UNITS[unit]
            one = ent.replace(",", "") == "1" and not dec
            w += " " + (sing if one else plur)
        return w

    return _TOKEN.sub(rep, text)


if __name__ == "__main__":
    import sys
    print(a_palabras(" ".join(sys.argv[1:])))
