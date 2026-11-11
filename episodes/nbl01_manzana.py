"""Newton Bien Loco #1 — ¿Verdad o mito? La manzana de Newton.

Dato verificado: según las memorias de William Stukeley (1752), Newton le contó que la idea de la
gravitación se le ocurrió al ver caer una manzana mientras estaba en un jardín, y se preguntó por
qué siempre cae perpendicular al suelo y no de lado o hacia arriba. Ningún relato de la época dice
que le cayera en la cabeza (eso es un adorno posterior).
Fuentes: memorias de Stukeley (Royal Society); Scientific American; Nature blogs.
"""
SLUG = "nbl01_manzana"
BADGE = "¿VERDAD O MITO?"
SOURCE = "Fuente: memorias de William Stukeley (1752)"
CTA = "¿Qué mito desmiento después? 👇"

N = {"x": 0.36, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "jardin_vertical", "newton": N, "lines": [
        {"say": "¿De verdad una manzana me cayó en la cabeza y así descubrí la gravedad?",
         "pose": "manzana_pensando", "key": ["manzana", "cabeza", "gravedad"]},
        {"say": "¡Es un mito!", "pose": "asustado", "key": ["mito"],
         "cam": {"zoom": 1.18, "fx": 0.4, "fy": 0.35},
         "events": [{"kind": "stamp", "text": "MITO", "anim": "stamp", "x": 0.72, "y": 0.30,
                     "size": 160, "rot": 12}]},
        {"say": "Según mi amigo William Stukeley, yo estaba en un jardín… y vi caer una manzana.",
         "pose": "explicando_pluma", "key": ["jardín", "manzana"], "cam": {"zoom": 1.0},
         "events": [{"img": "objetos/manzana_1", "h": 150, "anim": "drop", "x": 0.80, "from_y": 0.40,
                     "y": 0.80, "at": 0.55, "fall": 0.6, "until": 2}]},
        {"say": "Y me pregunté: ¿por qué siempre cae derecho hacia el suelo, y nunca de lado o hacia arriba?",
         "pose": "senalando", "key": ["derecho", "suelo"],
         "events": [{"kind": "arrow", "length": 240, "anim": "pop", "x": 0.80, "y": 0.63, "at": 0.15}]},
        {"say": "Esa pregunta me llevó a la idea de la gravedad: una fuerza que jala las cosas hacia la Tierra.",
         "pose": "pensando", "key": ["gravedad", "fuerza"],
         "events": [{"img": "objetos/tierra", "h": 300, "anim": "pop", "x": 0.78, "y": 0.36, "at": 0.4},
                    {"kind": "label", "text": "GRAVEDAD", "size": 70, "color": (255, 194, 26, 255),
                     "anim": "pop", "x": 0.78, "y": 0.47, "at": 0.45}]},
        {"say": "Así que la manzana sí existió… pero nunca me pegó en la cabeza.",
         "pose": "senalando", "key": ["nunca", "cabeza"], "cam": {"zoom": 1.12, "fx": 0.38, "fy": 0.36}},
        {"say": "¿Qué otro mito quieres que desmienta? Escríbelo en los comentarios.",
         "pose": "explicando_pluma", "key": ["mito"], "cam": {"zoom": 1.0}},
    ]},
]
