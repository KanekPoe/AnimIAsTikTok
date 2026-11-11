"""Newton Bien Loco #7 — ¿Verdad o mito? Solo usamos el 10 % del cerebro.

Falso. La neuroimagen (EEG, PET, resonancia funcional) muestra actividad en prácticamente todas
las regiones, incluso en tareas simples; y lesiones mucho menores que el 90 % del cerebro tienen
consecuencias graves. Fuentes: Scientific American (Barry Beyerstein); University of Texas.
"""
SLUG = "nbl07_cerebro"
BADGE = "¿VERDAD O MITO?"
SOURCE = "Fuente: Scientific American (B. Beyerstein)"
CTA = "¿Qué otro mito desmiento? 👇"
GOLD = (255, 194, 26, 255)
N = {"x": 0.36, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "laboratorio_vertical", "newton": N, "lines": [
        {"say": "¿De verdad solo usamos el diez por ciento del cerebro?",
         "text": "¿De verdad solo usamos el 10% del cerebro?", "pose": "pensando",
         "key": ["10%", "cerebro"],
         "events": [{"img": "objetos/cerebro", "h": 300, "anim": "pop", "x": 0.77, "y": 0.42, "at": 0.3,
                     "until": 1}]},
        {"say": "¡Falso!", "pose": "asustado", "key": ["falso"], "cam": {"zoom": 1.15, "fx": 0.4, "fy": 0.36},
         "events": [{"kind": "stamp", "text": "FALSO", "anim": "stamp", "x": 0.70, "y": 0.30,
                     "size": 150, "rot": 12}]},
        {"say": "Los escáneres muestran actividad en casi todo el cerebro… incluso al hablar o caminar.",
         "pose": "explicando_pluma", "key": ["casi", "todo"], "cam": {"zoom": 1.0},
         "events": [{"img": "objetos/cerebro_colores", "h": 320, "anim": "pop", "x": 0.77, "y": 0.42,
                     "at": 0.15, "until": 1},
                    {"img": "objetos/lupa", "h": 200, "anim": "pop", "x": 0.88, "y": 0.52, "at": 0.3}]},
        {"say": "Y si sobrara el noventa por ciento, perder un pedacito no importaría… pero un daño pequeño puede afectar mucho.",
         "text": "Y si sobrara el 90%, perder un pedacito no importaría… pero un daño pequeño puede afectar mucho.",
         "pose": "senalando", "key": ["90%", "daño"],
         "events": [{"img": "objetos/cerebro_colores", "h": 300, "anim": "pop", "x": 0.77, "y": 0.42}]},
        {"say": "¿Qué otro mito quieres que desmienta? Escríbelo en los comentarios.",
         "pose": "explicando_pluma", "key": ["mito"]},
    ]},
]
