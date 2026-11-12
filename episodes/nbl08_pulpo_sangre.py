"""Newton Bien Loco #8 — El pulpo: tres corazones y sangre azul (versión con el estilo del creador).

Guion basado en la narración improvisada del creador, corregida y aprobada.
Datos verificados:
- Dos corazones branquiales (branquias) y uno sistémico (cuerpo). Smithsonian Ocean.
- Hemocianina (cobre): azul al unirse al oxígeno, casi incolora sin oxígeno.
- Hemoglobina (hierro): rojo brillante con oxígeno, rojo oscuro sin él; nunca azul. Las venas se ven
  azuladas por cómo la piel absorbe y dispersa la luz.
- Estatua de la Libertad: cobre que con el aire formó una pátina verde azulada.
- Cierre: gancho sin afirmación ("¿para qué tres corazones?"); la razón va en la parte 2 con el matiz
  de que es la explicación más aceptada, no un hecho cerrado.
"""
SLUG = "nbl08_pulpo_sangre"
BADGE = "DATO ANIMAL"
SOURCE = "Fuente: Smithsonian (Ocean Portal)"
CTA = "¿Qué animal raro sigue? 👇"
GOLD = (255, 194, 26, 255)
N = {"x": 0.36, "feet": 1840, "h": 1380}

SCENES = [
    {"bg": "oceano_vertical", "newton": N, "lines": [
        {"say": "Qué pedo, este animal tiene tres corazones… y sangre azul.", "pose": "explicando_pluma",
         "key": ["tres", "corazones", "azul"],
         "events": [{"img": "objetos/pulpo", "h": 300, "anim": "pop", "x": 0.75, "y": 0.42, "at": 0.15}]},
        {"say": "Dos corazones los ocupa para sus branquias, y uno para el resto del cuerpo.",
         "pose": "senalando", "key": ["dos", "branquias", "uno", "cuerpo"],
         "events": [{"img": "objetos/pulpo_corazones", "h": 320, "anim": "pop", "x": 0.75, "y": 0.40},
                    {"kind": "label", "text": "2 ❤ branquias", "size": 50, "color": GOLD, "anim": "pop",
                     "x": 0.72, "y": 0.535, "at": 0.25},
                    {"kind": "label", "text": "1 ❤ cuerpo", "size": 50, "color": GOLD, "anim": "pop",
                     "x": 0.72, "y": 0.58, "at": 0.65}]},
        {"say": "¿Y por qué azul? Porque su sangre lleva el oxígeno con cobre, símon, el mismo de los cables.",
         "pose": "pensando", "key": ["cobre", "cables"],
         "events": [{"img": "objetos/cable_cobre", "h": 300, "anim": "pop", "x": 0.74, "y": 0.40, "at": 0.45},
                    {"kind": "label", "text": "COBRE", "size": 76, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.55, "at": 0.5}]},
        {"say": "Cuando ese cobre se une al oxígeno, la sangre se pone azul. Y sin oxígeno… es casi transparente.",
         "pose": "explicando_pluma", "key": ["oxígeno", "azul", "transparente"],
         "events": [{"img": "objetos/gota_azul", "h": 240, "anim": "pop", "x": 0.75, "y": 0.42, "at": 0.2,
                     "dur": 3.2},
                    {"img": "objetos/gota_transparente", "h": 240, "anim": "pop", "x": 0.75, "y": 0.42,
                     "at": 0.68}]},
        {"say": "Es parecido a lo que pasó con la Estatua de la Libertad: era color cobre, y con el aire se puso verde azulosa.",
         "pose": "senalando", "key": ["estatua", "cobre", "verde"],
         "events": [{"img": "objetos/estatua_libertad_cobre", "h": 480, "anim": "pop", "x": 0.75, "y": 0.42,
                     "at": 0.35, "dur": 2.8},
                    {"img": "objetos/estatua_libertad_verde", "h": 480, "anim": "pop", "x": 0.75, "y": 0.42,
                     "at": 0.72}]},
    ]},
    {"bg": "laboratorio_vertical", "newton": N, "lines": [
        {"say": "Nosotros usamos hierro. Con oxígeno, nuestra sangre es rojo brillante; sin oxígeno sigue siendo roja, solo más oscura.",
         "pose": "explicando_pluma", "key": ["hierro", "brillante", "roja", "oscura"],
         "events": [{"kind": "label", "text": "HIERRO", "size": 76, "color": GOLD, "anim": "pop",
                     "x": 0.74, "y": 0.26, "at": 0.08},
                    {"img": "objetos/gota_roja", "h": 230, "anim": "pop", "x": 0.74, "y": 0.42, "at": 0.3,
                     "dur": 3.0},
                    {"img": "objetos/gota_roja_oscura", "h": 230, "anim": "pop", "x": 0.74, "y": 0.42,
                     "at": 0.68}]},
        {"say": "Por eso un clavo oxidado se ve rojizo: también es hierro con oxígeno.",
         "pose": "senalando", "key": ["clavo", "hierro"],
         "events": [{"img": "objetos/clavo_oxidado", "h": 380, "anim": "pop", "x": 0.75, "y": 0.42,
                     "at": 0.15}]},
        {"say": "Y nel, nuestra sangre nunca es azul: las venas se ven azules por cómo pasa la luz a través de la piel.",
         "pose": "asustado", "key": ["nunca", "azul", "luz"],
         "events": [{"img": "objetos/brazo_venas", "h": 380, "anim": "pop", "x": 0.75, "y": 0.42, "at": 0.25},
                    {"kind": "stamp", "text": "MITO", "anim": "stamp", "x": 0.72, "y": 0.26, "size": 120,
                     "rot": 10, "at": 0.12}]},
    ]},
    {"bg": "oceano_vertical", "newton": N, "lines": [
        {"say": "¿Y para qué quiere tres corazones? La razón te va a volar la cabeza… en la parte 2.",
         "text": "¿Y para qué quiere tres corazones? La razón te va a volar la cabeza… en la parte 2.",
         "pose": "pensando", "key": ["tres", "corazones", "parte"],
         "cam": {"zoom": 1.1, "fx": 0.5, "fy": 0.4},
         "events": [{"img": "objetos/pulpo_corazones", "h": 300, "anim": "pop", "x": 0.75, "y": 0.42,
                     "at": 0.1},
                    {"kind": "stamp", "text": "PARTE 2 👀", "anim": "stamp", "x": 0.70, "y": 0.27,
                     "size": 90, "rot": -6, "color": (120, 60, 200, 255), "at": 0.7}]},
        {"say": "¿Qué otro animal raro quieres? Escríbelo en los comentarios.",
         "pose": "senalando", "key": ["animal"], "cam": {"zoom": 1.0}},
    ]},
]
