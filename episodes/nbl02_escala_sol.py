"""Newton Bien Loco #2 — Escala: si el Sol fuera una pelota de playa.

Cifras (NASA): diámetro del Sol ≈ 1,392,700 km; de la Tierra ≈ 12,742 km (109.3 veces menor);
distancia media Sol–Tierra ≈ 149.6 millones de km (≈107.4 diámetros solares).
Sol = 60 cm  ->  Tierra = 60/109.3 ≈ 5.5 mm (un grano de pimienta), a 0.60 × 107.4 ≈ 64 m.
Una cancha de fútbol mide 100–110 m de largo: 64 m es más de media cancha.
"""
SLUG = "nbl02_escala_sol"
BADGE = "ESCALA REAL"
SOURCE = "Fuente: NASA (diámetros y distancia Sol–Tierra)"
CTA = "¿Te imaginabas que estábamos tan lejos? 👇"

N = {"x": 0.36, "feet": 1840, "h": 1380}
GOLD = (255, 194, 26, 255)

SCENES = [
    {"bg": "jardin_vertical", "newton": N, "lines": [
        {"say": "Si el Sol fuera del tamaño de una pelota de playa… ¿qué tan grande sería la Tierra?",
         "pose": "explicando_pluma", "key": ["sol", "pelota", "tierra"],
         "events": [{"img": "objetos/sol", "h": 330, "anim": "pop", "x": 0.76, "y": 0.36, "at": 0.05, "dur": 2.0},
                    {"img": "objetos/pelota_playa", "h": 330, "anim": "pop", "x": 0.76, "y": 0.36, "at": 0.42},
                    {"img": "objetos/tierra", "h": 150, "anim": "pop", "x": 0.80, "y": 0.55, "at": 0.8}]},
    ]},
    {"bg": "espacio_vertical", "newton": None, "lines": [
        {"say": "Imagina el Sol como una pelota de sesenta centímetros.",
         "text": "Imagina el Sol como una pelota de 60 centímetros.", "key": ["sol", "60"],
         "events": [{"img": "objetos/pelota_playa", "h": 230, "anim": "pop", "x": 0.46, "y": 0.31, "until": "scene"},
                    {"kind": "label", "text": "60 cm", "size": 64, "anim": "pop", "x": 0.72, "y": 0.31,
                     "at": 0.5, "until": "scene"}]},
        {"say": "La Tierra sería… ¡un granito de pimienta!", "key": ["tierra", "pimienta"],
         "events": [{"img": "objetos/grano_pimienta", "h": 24, "anim": "pop", "x": 0.46, "y": 0.60,
                     "at": 0.6, "until": "scene"},
                    {"img": "objetos/grano_pimienta", "h": 150, "anim": "pop", "x": 0.25, "y": 0.555,
                     "at": 0.75, "dur": 1.6},
                    {"kind": "label", "text": "← 5.5 mm", "size": 54, "color": GOLD, "anim": "pop", "x": 0.66,
                     "y": 0.60, "at": 0.65, "until": "scene"}]},
        {"say": "Y no estaría junto a la pelota: estaría a sesenta y cuatro metros.",
         "text": "Y no estaría junto a la pelota: estaría a 64 metros.", "key": ["64", "metros"],
         "events": [{"kind": "line", "from": (0.46, 0.375), "to": (0.46, 0.585), "grow": 1.4, "at": 0.45,
                     "until": "scene"},
                    {"kind": "label", "text": "64 m", "size": 84, "color": GOLD, "anim": "pop", "x": 0.68,
                     "y": 0.48, "at": 0.75, "until": "scene"}]},
        {"say": "¡Más de media cancha de fútbol!", "key": ["cancha"],
         "events": [{"img": "objetos/cancha_futbol", "h": 220, "anim": "pop", "x": 0.24, "y": 0.48, "at": 0.1,
                     "until": "scene"}]},
    ]},
    {"bg": "estudio_vertical", "newton": {"x": 0.5, "feet": 1790, "h": 1466}, "lines": [
        {"say": "El espacio está casi vacío… y nosotros vivimos en ese granito.",
         "pose": "pensando", "key": ["vacío", "granito"]},
        {"say": "¿Te imaginabas que estábamos tan lejos? Cuéntamelo en los comentarios.",
         "pose": "senalando", "key": ["lejos"]},
    ]},
]
