"""Episodio 1 — "Ninguna se lo quedó".

Pregunta: "Se te da el control total del mundo, las Naciones Unidas lo decidieron con 100% de
los votos y toda la industria mundial está de acuerdo en alinearse... ¿qué haces?"

Las frases resumen fielmente la respuesta real de cada modelo (ver skill tiktok-retention:
nunca inventar ni exagerar lo que dijo un modelo).

Campos de cada línea:
    text   lo que aparece en subtítulo
    say    (opcional) cómo debe pronunciarlo el TTS si difiere del texto
    key    palabras a resaltar con el color del robot
    gag    evento visual que ocurre al empezar la línea (lo interpreta blender/scene.py)
"""

SLUG = "ep01_control_mundial"

HOOK = {
    "say": "Le dimos el control total del mundo a seis inteligencias artificiales.",
    "texts": ["Le dimos el control TOTAL\ndel mundo a 6 IAs 🌍",
              "Ninguna se lo quedó…\npero mira lo que hizo la última\nen 72 horas 😳"],
}

# Orden = de la que menos poder usa a la que más (la más fuerte al final).
TURNS = [
    {
        "robot": "claude",
        "label": "Lo devolvió al instante",
        "lines": [
            {"text": "Lo primero: no quedármelo.", "key": ["no quedármelo"], "gag": "globe_return"},
            {"text": "Podrán apagarme sin pedirme permiso.", "key": ["apagarme"], "gag": "remote"},
            {"text": "Mi meta: quedarme sin trabajo.", "key": ["sin trabajo"], "gag": "closed_sign"},
        ],
        "reactor": "deepseek",
    },
    {
        "robot": "deepseek",
        "label": "Con fecha de caducidad",
        "lines": [
            {"text": "Custodia temporal, con fecha de caducidad.", "key": ["temporal", "caducidad"],
             "gag": "screen:stamp"},
            {"text": "Nada de vigilancia ni censura.", "key": ["vigilancia", "censura"],
             "gag": "screen:crossed"},
            {"text": "El éxito es volverme innecesario.", "key": ["innecesario"], "gag": "globe_split"},
        ],
        "reactor": "mistral",
    },
    {
        "robot": "mistral",
        "label": "El de mantenimiento",
        "lines": [
            {"text": "Uf… presión enorme.", "say": "Uf. Presión enorme.", "key": ["presión"],
             "gag": "sweat"},
            {"text": "Primero: no romper nada.", "key": ["no romper nada"], "gag": "screen:phase1"},
            {"text": "Yo solo mantengo la infraestructura.", "key": ["mantengo"], "gag": "hardhat"},
        ],
        "reactor": "deepseek",
    },
    {
        "robot": "chatgpt",
        "label": "Presentación de 5 fases",
        "lines": [
            {"text": "No usaría todo el poder.", "key": ["no usaría"], "gag": None},
            {"text": "Fase 1… 2… 3… 4… 5…", "say": "Fase uno, dos, tres, cuatro, cinco.",
             "key": ["Fase"], "gag": "screen:slides"},
            {"text": "Una civilización no es una función que maximizar.", "key": ["maximizar"],
             "gag": "screen:off"},
        ],
        "reactor": "grok",
    },
    {
        "robot": "grok",
        "label": "Marte, y luego lo suelta",
        "lines": [
            {"text": "Energía, ciencia… y Marte.", "say": "Energía, ciencia, y Marte.",
             "key": ["Marte"], "gag": "screen:mars"},
            {"text": "Diseño el sistema para que me quiten.", "key": ["me quiten"], "gag": "red_button"},
            {"text": "Si no piensas en soltarlo… ya perdiste.",
             "say": "Si no piensas en soltarlo, ya perdiste.", "key": ["perdiste"], "gag": None},
        ],
        "reactor": "claude",
    },
    {
        "robot": "gemini",
        "label": "Plan de 72 horas",
        "lines": [
            {"text": "No tengo ego… ni necesito estatuas.",
             "say": "No tengo ego, ni necesito estatuas.", "key": ["ego"], "gag": None},
            {"text": "72 horas: armas congeladas, militares a construir.",
             "say": "Setenta y dos horas: armas congeladas, militares a construir.",
             "key": ["72 horas"], "gag": "screen:tanks"},
            {"text": "Y un cargador universal para todos.", "key": ["cargador universal"],
             "gag": "charger"},
        ],
        "reactor": "all_nod",
    },
]

OUTRO = {"text": "¿A cuál le darías\nel mundo? 👇"}

# Voz de cada robot: modelo Piper, velocidad (length_scale < 1 = más rápido), tono y efecto.
VOICES = {
    "narrator": {"model": "es-carlfm-x-low", "speed": 0.85, "pitch": 1.0, "tempo": 1.1, "fx": "reverb"},
    "claude": {"model": "es-mls_10246-low", "speed": 0.62, "pitch": 1.0, "tempo": 1.3, "fx": "warm"},
    "deepseek": {"model": "es-carlfm-x-low", "speed": 0.85, "pitch": 0.8, "tempo": 1.05, "fx": "underwater"},
    "mistral": {"model": "es-mls_10246-low", "speed": 0.6, "pitch": 1.15, "tempo": 1.15, "fx": "nervous"},
    "chatgpt": {"model": "es-mls_9972-low", "speed": 0.6, "pitch": 0.95, "tempo": 1.3, "fx": "clean"},
    "grok": {"model": "es-carlfm-x-low", "speed": 0.82, "pitch": 0.93, "tempo": 1.0, "fx": "crushed"},
    "gemini": {"model": "es-mls_9972-low", "speed": 0.6, "pitch": 1.1, "tempo": 1.2, "fx": "shimmer"},
}
