"""Newton Bien Loco #4 — ¿Verdad o mito? 10 veces más bacterias que células.

Dato verificado: Sender, Fuchs y Milo (2016, PLoS Biology) estimaron para un adulto de referencia
de 70 kg ~3.0×10^13 células humanas (30 billones) y ~3.8×10^13 bacterias (38 billones): una
proporción de ~1.3 a 1, no 10 a 1. "Billón" en español = 10^12.
"""
SLUG = "nbl04_bacterias"
BADGE = "¿VERDAD O MITO?"
SOURCE = "Fuente: Sender, Fuchs y Milo (2016), PLoS Biology"
CTA = "¿Qué otro mito del cuerpo desmiento? 👇"
GOLD = (255, 194, 26, 255)
N = {"x": 0.36, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "laboratorio_vertical", "newton": N, "lines": [
        {"say": "¿De verdad tienes diez veces más bacterias que células en tu cuerpo?",
         "text": "¿De verdad tienes 10 veces más bacterias que células en tu cuerpo?",
         "pose": "pensando", "key": ["10", "bacterias", "células"],
         "events": [{"img": "objetos/bacterias_grupo", "h": 330, "anim": "pop", "x": 0.76, "y": 0.42,
                     "at": 0.2, "until": 1}]},
        {"say": "¡Es un mito!", "pose": "asustado", "key": ["mito"],
         "cam": {"zoom": 1.15, "fx": 0.4, "fy": 0.36},
         "events": [{"kind": "stamp", "text": "MITO", "anim": "stamp", "x": 0.72, "y": 0.30,
                     "size": 160, "rot": 12}]},
        {"say": "Un estudio de dos mil dieciséis contó mejor: tienes unos treinta billones de células humanas…",
         "text": "Un estudio de 2016 contó mejor: tienes unos 30 billones de células humanas…",
         "pose": "explicando_pluma", "key": ["2016", "30", "billones"], "cam": {"zoom": 1.0},
         "events": [{"img": "objetos/celula_humana", "h": 240, "anim": "pop", "x": 0.74, "y": 0.30,
                     "at": 0.5, "until": 1},
                    {"kind": "label", "text": "30 billones", "size": 56, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.385, "at": 0.65, "until": 1}]},
        {"say": "…y unos treinta y ocho billones de bacterias.",
         "text": "…y unos 38 billones de bacterias.", "pose": "senalando", "key": ["38", "billones"],
         "events": [{"img": "objetos/bacterias_grupo", "h": 240, "anim": "pop", "x": 0.74, "y": 0.48,
                     "at": 0.2},
                    {"kind": "label", "text": "38 billones", "size": 56, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.575, "at": 0.35}]},
        {"say": "Casi uno a uno: en número, eres más o menos mitad tú… y mitad bacterias.",
         "pose": "explicando_pluma", "key": ["uno", "mitad"], "cam": {"zoom": 1.1, "fx": 0.4, "fy": 0.38}},
        {"say": "¿Qué otro mito del cuerpo quieres que desmienta? Escríbelo en los comentarios.",
         "pose": "senalando", "key": ["mito"], "cam": {"zoom": 1.0}},
    ]},
]
