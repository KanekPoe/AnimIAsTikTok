# AnimIAsTikTok

Animaciones para TikTok donde 6 robots (Claude, ChatGPT, Gemini, DeepSeek, Grok y Mistral)
responden la misma pregunta. Todo se genera con código: Blender + Python + ffmpeg.

## Requisitos

- Blender 4.x (`blender` en el PATH)
- Python 3 con `numpy`, `Pillow` y `piper-tts` (`pip install numpy pillow piper-tts`)
- ffmpeg
- Voces en español: `bash pipeline/get_voices.sh`

## Flujo de un episodio

```bash
EP=output/ep01_control_mundial
python3 pipeline/voices.py episodes/ep01_control_mundial.py      # voces + timeline.json
python3 pipeline/holo.py $EP                                     # imágenes del holograma
blender -b --python blender/scene.py -- $EP --still 120          # (opcional) probar un frame
blender -b --python blender/scene.py -- $EP --render             # render (reanudable)
blender -b --python blender/scene.py -- $EP --portraits          # tarjetas del cierre
python3 pipeline/compose.py $EP                                  # final.mp4 y final_sin_musica.mp4
```

- `final.mp4`: voces + efectos + base musical.
- `final_sin_musica.mp4`: voces + efectos, para ponerle un audio en tendencia desde TikTok.

## Estructura

| Ruta | Qué es |
|---|---|
| `blender/build_models.py` | Modelos 3D de los robots |
| `blender/render_preview.py` | Vista previa de los modelos |
| `blender/scene.py` | Sala, animación, cámara y render de un episodio |
| `episodes/*.py` | Guion de cada episodio (frases, gags, voces) |
| `pipeline/voices.py` | TTS (Piper) + efectos de voz + línea de tiempo |
| `pipeline/holo.py` | Gráficos de la pantalla holográfica |
| `pipeline/sfx.py` | Efectos de sonido y base musical sintetizados |
| `pipeline/compose.py` | Subtítulos, textos, mezcla y exportación |
| `.claude/skills/tiktok-retention` | Reglas de edición para retención |

Para un episodio nuevo: copia `episodes/ep01_control_mundial.py`, cambia frases/gags y
sigue el mismo flujo. Los gags nuevos se agregan en `blender/scene.py` (`anim_gags`) y
`pipeline/holo.py`.

Fuentes incluidas: Inter y JetBrains Mono (licencia OFL, ver `assets/fonts`).
