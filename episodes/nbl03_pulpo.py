"""Newton Bien Loco #3 — Animales: el pulpo tiene tres corazones y sangre azul.

Dato verificado: dos corazones branquiales bombean sangre a las branquias y un corazón sistémico
la manda al resto del cuerpo. La sangre es azul porque transporta el oxígeno con hemocianina, una
proteína con cobre (la nuestra usa hemoglobina, con hierro).
Fuentes: Smithsonian Ocean; Smithsonian Magazine.
"""
SLUG = "nbl03_pulpo"
BADGE = "DATO ANIMAL"
SOURCE = "Fuente: Smithsonian (Ocean Portal)"
CTA = "¿Qué animal raro explico después? 👇"
GOLD = (255, 194, 26, 255)
N = {"x": 0.36, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "oceano_vertical", "newton": N, "lines": [
        {"say": "Este animal tiene tres corazones… ¡y sangre azul!", "pose": "explicando_pluma",
         "key": ["tres", "corazones", "azul"],
         "events": [{"img": "objetos/pulpo", "h": 300, "anim": "pop", "x": 0.77, "y": 0.42, "at": 0.05,
                     "until": 1}]},
        {"say": "El pulpo usa dos corazones para mandar sangre a sus branquias… y uno para el resto del cuerpo.",
         "pose": "senalando", "key": ["dos", "branquias", "uno", "cuerpo"],
         "events": [{"img": "objetos/pulpo_corazones", "h": 330, "anim": "pop", "x": 0.77, "y": 0.42,
                     "at": 0.0, "until": 1},
                    {"kind": "label", "text": "2 ❤ branquias", "size": 50, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.555, "at": 0.25},
                    {"kind": "label", "text": "1 ❤ cuerpo", "size": 50, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.60, "at": 0.7}]},
        {"say": "¿Y por qué azul? Porque su sangre lleva el oxígeno con cobre, no con hierro como la nuestra.",
         "pose": "pensando", "key": ["azul", "cobre", "hierro"],
         "cam": {"zoom": 1.1, "fx": 0.5, "fy": 0.4},
         "events": [{"img": "objetos/gota_azul", "h": 230, "anim": "pop", "x": 0.77, "y": 0.42, "at": 0.15},
                    {"kind": "label", "text": "COBRE", "size": 80, "color": GOLD, "anim": "pop",
                     "x": 0.77, "y": 0.56, "at": 0.5}]},
        {"say": "¿Qué animal raro quieres que te explique? Escríbelo en los comentarios.",
         "pose": "explicando_pluma", "key": ["animal"], "cam": {"zoom": 1.0}},
    ]},
]
