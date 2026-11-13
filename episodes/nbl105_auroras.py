"""Generado automáticamente desde guiones/105_auroras.md por pipeline/guion2ep.py.

No editar a mano: corrige el guion y vuelve a convertir.
"""
SLUG = 'nbl105_auroras'
BADGE = 'DATO ESPACIAL'
SOURCE = None
CTA = '¿Dónde has visto una aurora? 👇'
SCENES = [{'bg': 'estudio_vertical',
  'cast': [['newton', {'x': 0.31, 'feet': 1790, 'h': 1300}]],
  'lines': [{'who': 'newton',
             'say': 'Esas luces verdes del cielo no son magia. Son el Sol chocando contra nuestra atmósfera.',
             'pose': 'senalando',
             'key': ['magia'],
             'events': [{'kind': 'label',
                         'text': '¿MAGIA?',
                         'size': 64,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.69,
                         'y': 0.2346,
                         'at': 0.12}]}]},
 {'bg': 'espacio_vertical',
  'cast': [],
  'lines': [{'who': 'newton',
             'say': 'El Sol lanza un viento de partículas cargadas que viajan a cientos de kilómetros por '
                    'segundo.',
             'key': [],
             'events': [{'img': 'objetos/sol', 'h': 460, 'anim': 'pop', 'x': 0.46, 'y': 0.4, 'at': 0.05}]},
            {'who': 'newton',
             'say': 'El campo magnético de la Tierra las desvía y las guía hacia los polos.',
             'key': [],
             'events': [{'img': 'objetos/tierra', 'h': 460, 'anim': 'pop', 'x': 0.46, 'y': 0.4, 'at': 0.05}]},
            {'who': 'newton',
             'say': 'Al llegar a unos cien a trescientos kilómetros de altura, chocan con el oxígeno y el '
                    'nitrógeno del aire, y brillan.',
             'text': 'Al llegar a unos 100 a 300 kilómetros de altura, chocan con el oxígeno y el nitrógeno '
                     'del aire, y brillan.',
             'key': ['100', '300'],
             'events': [{'img': 'objetos/aurora_boreal',
                         'h': 460,
                         'anim': 'pop',
                         'x': 0.46,
                         'y': 0.4,
                         'at': 0.05}]},
            {'who': 'newton',
             'say': 'El verde y el rojo vienen del oxígeno; el azul y el morado, del nitrógeno.',
             'key': [],
             'events': []}]},
 {'bg': 'estudio_vertical',
  'cast': [['newton', {'x': 0.31, 'feet': 1790, 'h': 1300}]],
  'lines': [{'who': 'newton',
             'say': 'Cuando hay una tormenta solar fuerte, las auroras bajan de latitud. Se han visto hasta '
                    'en México.',
             'pose': 'asustado',
             'key': ['méxico'],
             'events': [{'kind': 'label',
                         'text': '¿EN MÉXICO?',
                         'size': 44,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.69,
                         'y': 0.2257,
                         'at': 0.12}]},
            {'who': 'newton',
             'say': '¿Ya viste una aurora? Cuéntame en los comentarios dónde fue.',
             'pose': 'explicando_pluma',
             'key': [],
             'events': []}]}]
