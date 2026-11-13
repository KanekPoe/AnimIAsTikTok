# Lecciones aprendidas (errores que no deben repetirse)

Cada lección: qué pasó, cómo se detectó, la causa, el arreglo y la protección automática.

---

## Lección 1 — "Chik-chik" metálico en los videos (noviembre 2026)

**Síntoma (lo notó el creador):** un sonido tipo "chik-chik", metálico, como de estaca, que
aparecía muchas veces por video y sobre todo en cada cambio de escena.

**Primer diagnóstico (incompleto):** se pensó que eran demasiados efectos de sonido. Se limitó
a 3 por video (`MAX_ACCENTS` en `pipeline/nbl.py`) y el problema siguió. **Moraleja: medir antes
de suponer.**

**Causas reales (había dos):**

1. **Voz mal decodificada (la principal).** El modelo de voz de Gemini (`gemini-3.8-flash-tts`)
   entrega cada frase como **WAV completo** (`audio/wav`, con encabezado RIFF y un chunk de
   metadatos al final). El código lo leía como **PCM crudo** (formato de modelos anteriores).
   Resultado: el encabezado se oía como un **chasquido al inicio** y la cola como **~0.2 s de
   ruido a todo volumen al final de CADA frase**. Como las escenas cambian justo al terminar una
   frase, se oía sobre todo en las transiciones.
2. **"Whoosh" de transición con cortes.** `sfx.whoosh()` filtraba ruido por bloques de 512
   muestras sin continuidad entre bloques: **~94 cortes por segundo**, sonido áspero.

**Cómo se encontró:** midiendo energía de agudos (>6 kHz) en ventanas de 20 ms alrededor de cada
cambio de escena → los picos estaban justo al final de cada frase → al pedir el audio crudo a la
API se vio `audio/wav` y amplitud 1.0 en la cola.

**Arreglo:**
- `tts_gemini.decode_to_wav()`: detecta WAV por el tipo **y por la firma `RIFF`** de los bytes;
  solo trata como PCM crudo lo que no es WAV. Añade fundidos de 10 ms (entrada) y 30 ms (salida).
- La caché de voces cambió de versión (`v2|…` en la clave) para no reutilizar audios dañados.
- `sfx.whoosh()`: ruido rosa con barrido de paso de banda hecho con STFT (sin cortes).
- `sfx.click()`: tono suave en lugar de ruido blanco sin filtrar.

**Protección automática (para que no vuelva a pasar):**
- `pipeline/audio_qc.py`: control de calidad de audio (saturación, golpes en bordes, ruido agudo
  en la cola, saltos bruscos, cortes periódicos).
- Se ejecuta **solo** en dos lugares:
  - al generar cada voz (`tts_gemini`): si falla, se descarta y se reintenta;
  - antes de exportar cada video (`nbl.py`): si alguna voz o la mezcla falla, **no se exporta**.
- `tests/test_audio.py`: 9 pruebas sin internet. Reproducen el error original (WAV leído como
  PCM, whoosh por bloques) y verifican que el control lo detecta. Comprobado: con el código viejo
  las pruebas fallan; con el arreglo pasan.
- Calibrado con audio real: detecta 59/59 voces dañadas de la caché vieja y deja pasar 11/11
  voces correctas.

**Reglas que salen de aquí:**
1. Nunca asumir el formato de audio de una API: revisar el tipo **y** los bytes (firma).
2. Todo efecto sintetizado debe empezar y terminar en silencio y no procesarse por bloques sin
   continuidad.
3. Ante un problema de sonido, **medir** (agudos por ventana, amplitud de bordes) antes de cambiar
   cosas a ciegas.
4. Correr `python3 tests/test_audio.py` antes de renderizar después de tocar el audio.

**Pendiente:** los episodios 1–4 y 6–8 se renderizaron con voces dañadas. Al regenerarlos, la
caché `v2` y el control de audio harán que salgan limpios automáticamente.

---

## Nota — velocidad de la voz (noviembre 2026)

El creador pidió los videos 25 % más rápidos. Se subió `TARGET_RATE` de 5.5 a 6.9 sílabas/s
(`pipeline/tts_gemini.py`). Desde entonces la caché de voces (`v3`) guarda la voz **sin acelerar**
y la aceleración se aplica al copiarla: cambiar la velocidad ya no cuesta volver a pedir voces.
La voz acelerada también pasa por `audio_qc.check_voice`.
