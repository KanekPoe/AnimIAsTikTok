"""Newton Bien Loco #6 — Física cotidiana: la Torre Eiffel crece en verano.

Dato: la torre es de hierro (pudelado); el hierro se dilata con el calor. Las estimaciones más
citadas dan una diferencia de altura de entre ~12 y ~15 cm entre los días más fríos y los más
calurosos. No se encontró la cifra en el sitio oficial, por eso el guion dice "según estimaciones"
y "hasta unos 15 cm".
"""
SLUG = "nbl06_eiffel"
BADGE = "FÍSICA COTIDIANA"
SOURCE = "Fuente: estimaciones por dilatación térmica del hierro"
CTA = "¿Qué dato de física cotidiana sigue? 👇"
GOLD = (255, 194, 26, 255)
N = {"x": 0.34, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "paris_vertical", "newton": N, "lines": [
        {"say": "La Torre Eiffel… ¡crece en verano!", "pose": "asustado", "key": ["crece", "verano"],
         "cam": {"zoom": 1.12, "fx": 0.45, "fy": 0.36},
         "events": []},
        {"say": "Está hecha de hierro… y el hierro se estira un poquito cuando se calienta.",
         "pose": "explicando_pluma", "key": ["hierro", "calienta"], "cam": {"zoom": 1.0},
         "events": [{"img": "objetos/sol_2", "h": 170, "anim": "pop", "x": 0.73, "y": 0.30, "at": 0.55,
                     "until": 1},
                    {"img": "objetos/termometro_caliente", "h": 260, "anim": "pop", "x": 0.72, "y": 0.47,
                     "at": 0.7, "until": 1}]},
        {"say": "Según estimaciones, con el calor puede ganar hasta unos quince centímetros de altura.",
         "text": "Según estimaciones, con el calor puede ganar hasta unos 15 centímetros de altura.",
         "pose": "senalando", "key": ["15", "centímetros"],
         "events": [{"kind": "arrow", "length": 200, "down": False, "anim": "pop", "x": 0.76, "y": 0.27,
                     "at": 0.5},
                    {"kind": "label", "text": "+15 cm", "size": 70, "color": GOLD, "anim": "pop",
                     "x": 0.70, "y": 0.36, "at": 0.6}]},
        {"say": "Y en invierno, con el frío… se encoge otra vez.", "pose": "pensando",
         "key": ["invierno", "encoge"],
         "events": [{"img": "objetos/copo_nieve", "h": 160, "anim": "pop", "x": 0.73, "y": 0.30, "at": 0.3},
                    {"img": "objetos/termometro_frio", "h": 250, "anim": "pop", "x": 0.72, "y": 0.47,
                     "at": 0.45}]},
        {"say": "¿Qué otro dato de física cotidiana quieres? Escríbelo en los comentarios.",
         "pose": "explicando_pluma", "key": ["física"]},
    ]},
]
