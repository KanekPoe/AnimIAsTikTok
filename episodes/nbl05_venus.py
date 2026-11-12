"""Newton Bien Loco #5 — Venus está re-loco (guion del creador, revisado).

Datos verificados (NASA y física básica):
- Rotación ~243 días terrestres (día sideral, sentido retrógrado); órbita ~225 días. Se dice "girar
  sobre sí mismo", no "día" (el día solar dura ~117 días).
- Temperatura superficial media ~464 °C. Plomo: punto de fusión 327.5 °C (464 − 327 = 137).
- Presión superficial ~92 atm ≈ 95 kg por cm². Acostado (~5,000 cm²) ≈ 475 t ≈ 80 elefantes de ~6 t.
- Atmósfera ~96 % CO2, por encima de su punto crítico: fluido supercrítico. Densidad ~65 kg/m³,
  unas 50 veces la del aire terrestre al nivel del mar. Es densa pero no viscosa ("como nadar").
"""
SLUG = "nbl05_venus"
BADGE = "DATO ESPACIAL"
SOURCE = "Fuente: NASA"
CTA = "¿Te irías de vacaciones a Venus? 👇"
GOLD = (255, 194, 26, 255)
ESTUDIO = {"x": 0.5, "feet": 1790, "h": 1466}

SCENES = [
    {"bg": "estudio_vertical", "newton": ESTUDIO, "lines": [
        {"say": "Venus está re-loco: tarda más en girar sobre sí mismo… que en darle la vuelta al Sol. Neta.",
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
        {"say": "Tons: en Venus, girar una sola vez dura más que un año entero.", "key": ["más", "año"],
         "events": [{"kind": "stamp", "text": "GIRO > AÑO", "anim": "stamp", "x": 0.5, "y": 0.575,
                     "size": 100, "rot": -6, "color": (230, 120, 20, 255), "until": "scene"}]},
    ]},
    {"bg": "venus_superficie_vertical", "newton": None, "lines": [
        {"say": "Wacha: en su superficie hay, en promedio, unos cuatrocientos sesenta y cuatro grados.",
         "text": "Wacha: en su superficie hay, en promedio, unos 464 °C.", "key": ["464"],
         "events": [{"img": "objetos/termometro_caliente", "h": 340, "anim": "pop", "x": 0.5, "y": 0.40,
                     "at": 0.3, "until": "line"},
                    {"kind": "label", "text": "464 °C", "size": 120, "color": GOLD, "anim": "stamp",
                     "x": 0.5, "y": 0.27, "at": 0.65, "until": 1}]},
        {"say": "Al plomo lo derrites a trescientos veintisiete… y todavía nos sobran ciento treinta y siete.",
         "text": "Al plomo lo derrites a 327… y todavía nos sobran 137.", "key": ["plomo", "327", "137"],
         "events": [{"img": "objetos/plomo_derretido", "h": 260, "anim": "pop", "x": 0.5, "y": 0.42,
                     "at": 0.1},
                    {"kind": "label", "text": "Pb: 327 °C", "size": 60, "color": (255, 255, 255, 255),
                     "anim": "pop", "x": 0.5, "y": 0.535, "at": 0.35},
                    {"kind": "label", "text": "+137 °C de sobra", "size": 60, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.59, "at": 0.75}]},
        {"say": "Y su aire está pasado de lanza: la presión es noventa y dos veces la de la Tierra.",
         "text": "Y su aire está pasado de lanza: la presión es 92 veces la de la Tierra.",
         "key": ["presión", "92"],
         "events": [{"kind": "label", "text": "92 ×", "size": 150, "color": GOLD, "anim": "stamp",
                     "x": 0.5, "y": 0.38, "at": 0.55}]},
        {"say": "Si te acostaras ahí, sería como tener unos ochenta elefantes encima.",
         "text": "Si te acostaras ahí, sería como tener unos 80 elefantes encima.", "key": ["80", "elefantes"],
         "events": [{"img": "objetos/elefante", "h": 150, "anim": "drop", "x": x, "y": y, "from_y": -0.1,
                     "fall": 0.35, "at": 0.25 + k * 0.05}
                    for k, (x, y) in enumerate([(0.30, 0.58), (0.50, 0.58), (0.70, 0.58), (0.40, 0.505),
                                                (0.60, 0.505), (0.50, 0.43)])]
                   + [{"kind": "label", "text": "× 80", "size": 120, "color": GOLD, "anim": "stamp",
                       "x": 0.5, "y": 0.30, "at": 0.65}]},
        {"say": "Su atmósfera es casi pura de CO2, y está tan apretada y caliente, así bien machín, que ya no es ni gas ni líquido: es un fluido supercrítico.",
         "text": "Su atmósfera es casi pura de CO₂, y está tan apretada y caliente, así bien machín, que ya no es ni gas ni líquido: es un fluido supercrítico.",
         "key": ["co₂", "supercrítico"],
         "events": [{"img": "objetos/molecula_co2", "h": 160, "anim": "pop", "x": 0.5, "y": 0.36, "at": 0.08},
                    {"kind": "label", "text": "NI GAS NI LÍQUIDO", "size": 64, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.47, "at": 0.65}]},
        {"say": "Es unas cincuenta veces más densa que nuestro aire: moverte ahí se sentiría más como nadar que como caminar.",
         "text": "Es unas 50 veces más densa que nuestro aire: moverte ahí se sentiría más como nadar que como caminar.",
         "key": ["50", "nadar"],
         "events": [{"kind": "label", "text": "50 × más densa", "size": 70, "color": GOLD, "anim": "pop",
                     "x": 0.5, "y": 0.30, "at": 0.1},
                    {"img": "objetos/persona_nadando", "h": 230, "anim": "slide", "from_dx": -1, "x": 0.5,
                     "y": 0.45, "at": 0.55}]},
    ]},
    {"bg": "estudio_vertical", "newton": ESTUDIO, "lines": [
        {"say": "¿Te irías de vacaciones allá… o nel?", "pose": "explicando_pluma", "key": ["vacaciones", "nel"]},
    ]},
]
