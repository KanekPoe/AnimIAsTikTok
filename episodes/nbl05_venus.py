"""Newton Bien Loco #5 — Espacio: en Venus, girar una vez dura más que un año.

Dato verificado (NASA): Venus tarda ~243 días terrestres en una rotación completa respecto a las
estrellas (día sideral) y ~225 días en orbitar el Sol. Además gira en sentido retrógrado (al revés
que la mayoría de los planetas). Temperatura media ~464 °C, más caliente que Mercurio (efecto
invernadero). Presión superficial ~92 atm ≈ 900 m bajo el mar (≈10 m de agua de mar por atmósfera).
Matiz: su día solar (de amanecer a amanecer) dura ~117 días; por eso
el guion habla de "girar sobre sí mismo", no de "día".
"""
SLUG = "nbl05_venus"
BADGE = "DATO ESPACIAL"
SOURCE = "Fuente: NASA"
CTA = "¿Qué planeta explico después? 👇"
GOLD = (255, 194, 26, 255)
WHITE_L = (255, 255, 255, 255)

SCENES = [
    {"bg": "estudio_vertical", "newton": {"x": 0.5, "feet": 1790, "h": 1466}, "lines": [
        {"say": "En Venus pasa algo rarísimo: tarda más en girar sobre sí mismo… que en darle la vuelta al Sol.",
         "pose": "senalando", "key": ["venus", "girar", "sol"]},
    ]},
    {"bg": "espacio_vertical", "newton": None, "lines": [
        {"say": "Una vuelta completa sobre sí mismo le toma doscientos cuarenta y tres días terrestres.",
         "text": "Una vuelta completa sobre sí mismo le toma 243 días terrestres.", "key": ["243", "días"],
         "events": [{"img": "objetos/flecha_giro", "h": 380, "anim": "pop", "x": 0.5, "y": 0.45, "at": 0.3,
                     "behind": True, "until": "line"},
                    {"img": "objetos/venus", "h": 260, "anim": "pop", "x": 0.5, "y": 0.45, "until": "scene"},
                    {"kind": "label", "text": "giro: 243 días", "size": 56, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.555, "at": 0.6, "until": 1}]},
        {"say": "Y una vuelta alrededor del Sol… solo doscientos veinticinco.",
         "text": "Y una vuelta alrededor del Sol… solo 225.", "key": ["sol", "225"],
         "events": [{"img": "objetos/sol", "h": 170, "anim": "pop", "x": 0.5, "y": 0.255, "until": "scene"},
                    {"img": "objetos/flecha_orbita", "h": 420, "anim": "pop", "x": 0.5, "y": 0.36, "at": 0.3,
                     "behind": True, "until": "scene"},
                    {"kind": "label", "text": "año: 225 días", "size": 56, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.60, "at": 0.6}]},
        {"say": "O sea: en Venus, girar una sola vez dura más que un año entero.", "key": ["más", "año"],
         "events": [{"kind": "stamp", "text": "GIRO > AÑO", "anim": "stamp", "x": 0.5, "y": 0.575,
                     "size": 100, "rot": -6, "color": (230, 120, 20, 255), "until": "scene"}]},
    ]},
    {"bg": "espacio_vertical", "newton": None, "lines": [
        {"say": "Y prepárate: en su superficie hay, en promedio, unos cuatrocientos sesenta y cuatro grados.",
         "text": "Y prepárate: en su superficie hay, en promedio, unos 464 °C.", "key": ["464"],
         "events": [{"img": "objetos/venus", "h": 300, "anim": "pop", "x": 0.5, "y": 0.42, "until": "scene"},
                    {"img": "objetos/termometro_caliente", "h": 280, "anim": "pop", "x": 0.74, "y": 0.42,
                     "at": 0.4, "until": "scene"},
                    {"kind": "label", "text": "464 °C", "size": 90, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.57, "at": 0.65, "until": "scene"}]},
        {"say": "Es más caliente que Mercurio… aunque Mercurio está más cerca del Sol.",
         "key": ["mercurio", "cerca"],
         "events": [{"img": "objetos/fuego", "h": 200, "anim": "pop", "x": 0.27, "y": 0.42, "at": 0.15},
                    {"kind": "stamp", "text": "MÁS QUE MERCURIO", "anim": "stamp", "x": 0.5, "y": 0.27,
                     "size": 70, "rot": -5, "color": (230, 80, 20, 255), "at": 0.2}]},
    ]},
    {"bg": "oceano_vertical", "newton": None, "lines": [
        {"say": "Y su aire pesa tanto que la presión es noventa y dos veces la de la Tierra…",
         "text": "Y su aire pesa tanto que la presión es 92 veces la de la Tierra…", "key": ["92", "presión"],
         "events": [{"kind": "label", "text": "92 atm", "size": 130, "color": GOLD, "anim": "stamp",
                     "x": 0.5, "y": 0.38, "until": "scene"}]},
        {"say": "Como estar a novecientos metros bajo el mar.",
         "text": "Como estar a 900 metros bajo el mar.", "key": ["900", "metros"],
         "events": [{"kind": "arrow", "length": 260, "anim": "pop", "x": 0.5, "y": 0.50, "at": 0.1},
                    {"kind": "label", "text": "≈ 900 m bajo el mar", "size": 66, "color": WHITE_L,
                     "anim": "pop", "x": 0.5, "y": 0.60, "at": 0.35}]},
    ]},
    {"bg": "estudio_vertical", "newton": {"x": 0.5, "feet": 1790, "h": 1466}, "lines": [
        {"say": "Ah, y además… ¡gira al revés que casi todos los planetas!", "pose": "asustado",
         "key": ["revés"]},
        {"say": "¿Qué planeta quieres que te explique después? Escríbelo en los comentarios.",
         "pose": "explicando_pluma", "key": ["planeta"]},
    ]},
]
