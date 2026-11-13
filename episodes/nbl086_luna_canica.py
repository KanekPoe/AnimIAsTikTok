"""Generado automáticamente desde guiones/086_luna_canica.md por pipeline/guion2ep.py.

No editar a mano: corrige el guion y vuelve a convertir.
"""
SLUG = 'nbl086_luna_canica'
BADGE = 'TAMAÑOS'
SOURCE = None
CTA = '¿Cuántas canicas caben entre la Tierra y el Sol? 👇'
SCENES = [{'bg': 'estudio_vertical',
  'cast': [['newton', {'x': 0.31, 'feet': 1790, 'h': 1300}]],
  'lines': [{'who': 'newton',
             'say': 'Imagina que la Tierra es una canica de dos centímetros. ¿Qué tan lejos crees que '
                    'quedaría la Luna?',
             'pose': 'senalando',
             'key': [],
             'events': [{'kind': 'label',
                         'text': '¿A CUÁNTO?',
                         'size': 72,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.6,
                         'y': 0.2281,
                         'at': 0.12}]}]},
 {'bg': 'espacio_vertical',
  'cast': [],
  'lines': [{'who': 'newton',
             'say': 'La Tierra mide unos doce mil setecientos cuarenta y dos kilómetros de diámetro. La Luna '
                    'está a unos trescientos ochenta y cuatro mil cuatrocientos kilómetros.',
             'text': 'La Tierra mide unos 12,742 kilómetros de diámetro. La Luna está a unos 384,400 '
                     'kilómetros.',
             'key': ['12,742', '384,400'],
             'events': [{'img': 'objetos/tierra', 'h': 373, 'anim': 'pop', 'x': 0.27, 'y': 0.4, 'at': 0.05},
                        {'img': 'objetos/luna', 'h': 391, 'anim': 'pop', 'x': 0.65, 'y': 0.4, 'at': 0.3}]},
            {'who': 'newton',
             'say': 'Eso son unos treinta diámetros de la Tierra. Hay que cruzar treinta canicas para '
                    'llegar.',
             'text': 'Eso son unos 30 diámetros de la Tierra. Hay que cruzar 30 canicas para llegar.',
             'key': ['30', '30', 'canicas'],
             'events': [{'kind': 'label',
                         'text': '30 CANICAS',
                         'size': 100,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.46,
                         'y': 0.2505,
                         'at': 0.12}]}]},
 {'bg': 'estudio_vertical',
  'cast': [['newton', {'x': 0.26, 'feet': 1790, 'h': 1180}], ['godel', {'x': 0.75, 'feet': 1790, 'h': 1180}]],
  'lines': [{'who': 'godel',
             'say': 'En tu canica, la Luna quedaría a unos sesenta centímetros: casi la altura de tu brazo '
                    'estirado.',
             'text': 'En tu canica, la Luna quedaría a unos 60 centímetros: casi la altura de tu brazo '
                     'estirado.',
             'pose': 'explicando',
             'key': ['60'],
             'events': [{'kind': 'label',
                         'text': '60 cm',
                         'size': 100,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.5,
                         'y': 0.2405,
                         'at': 0.12}]},
            {'who': 'newton',
             'say': 'Y el Sol, con esa misma escala, quedaría a unos doscientos treinta y cinco metros: como '
                    'dos o tres cuadras.',
             'text': 'Y el Sol, con esa misma escala, quedaría a unos 235 metros: como dos o tres cuadras.',
             'pose': 'asustado',
             'key': ['235'],
             'events': [{'kind': 'label',
                         'text': '¿Y EL SOL?',
                         'size': 92,
                         'color': (255, 194, 26, 255),
                         'anim': 'pop',
                         'x': 0.5,
                         'y': 0.237,
                         'at': 0.12}]},
            {'who': 'newton',
             'say': '¿Te parece lejos o cerca? Cuéntame en los comentarios.',
             'pose': 'explicando_pluma',
             'key': [],
             'events': []}]}]
