"""Control de calidad de audio: detecta chasquidos, ruido basura y cortes ANTES de publicar.

Nació de un error real (ver docs/LECCIONES.md, lección 1): el TTS de Gemini empezó a entregar un
WAV completo y el código lo leía como PCM crudo; el encabezado y la cola se colaban como un
chasquido al inicio y ~0.2 s de ruido a todo volumen al final de cada frase. Y el "whoosh"
sintetizado filtraba por bloques de 512 muestras, con cortes ~94 veces por segundo.

Uso:
    python3 pipeline/audio_qc.py archivo.wav [...]      # revisa archivos
    from audio_qc import check_voice, check_sfx, check_mix   # dentro del pipeline
"""
import sys
import wave

import numpy as np

SR = 48000


def read(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x, w.getframerate()


def _runs_above(x, thr):
    """Duración (s) de la racha más larga con |x| > thr."""
    m = np.abs(x) > thr
    if not m.any():
        return 0.0
    d = np.diff(np.concatenate([[0], m.astype(np.int8), [0]]))
    starts, ends = np.where(d == 1)[0], np.where(d == -1)[0]
    return float((ends - starts).max())


def _hf_rms(x, sr):
    """RMS por encima de ~6 kHz (diferencia de segundo orden: realza chasquidos y siseo)."""
    if len(x) < 3:
        return 0.0
    return float(np.sqrt(np.mean(np.diff(x, 2) ** 2)))


def check_voice(x, sr=SR, name="voz", speed=1.0):
    """Problemas de una frase de voz. Devuelve lista de textos (vacía = bien).

    speed: si la voz se aceleró (atempo), la ventana de la cola se acorta igual, para medir el
    mismo pedazo de habla que a velocidad normal (si no, una "s" final comprimida parece ruido).
    No cambia los umbrales.
    """
    probs = []
    if len(x) < sr * 0.15:
        return [f"{name}: audio demasiado corto ({len(x) / sr:.2f} s)"]
    clip = _runs_above(x, 0.98) / sr
    if clip > 0.002:
        probs.append(f"{name}: saturación/ruido a todo volumen durante {clip * 1000:.0f} ms")
    # con fundidos de 10 ms (entrada) y 30 ms (salida), los primeros 3 ms y los últimos 5 ms
    # deben ser casi silencio; si no, hay un golpe/encabezado colado.
    head, tail_e = x[:int(0.003 * sr)], x[-int(0.005 * sr):]
    if np.abs(head).max() > 0.35:
        probs.append(f"{name}: golpe al inicio ({np.abs(head).max():.2f})")
    if np.abs(tail_e).max() > 0.3:
        probs.append(f"{name}: golpe al final ({np.abs(tail_e).max():.2f})")
    tail = int(0.2 / speed * sr)
    body_hf = _hf_rms(x[:-tail], sr) + 1e-6
    tail_hf = _hf_rms(x[-tail:], sr)
    if tail_hf > 3.0 * body_hf and tail_hf > 0.02:
        probs.append(f"{name}: ruido agudo en la cola ({tail_hf / body_hf:.1f}× el cuerpo)")
    return probs


def check_sfx(x, sr=SR, name="efecto"):
    """Problemas de un efecto sintetizado: cortes (saltos bruscos) y bordes no silenciosos."""
    probs = []
    peak = float(np.abs(x).max()) + 1e-9
    jump = float(np.abs(np.diff(x)).max()) / peak
    if jump > 0.45:
        probs.append(f"{name}: salto brusco entre muestras ({jump:.2f} del pico): suena a chasquido")
    if abs(x[0]) > 0.05 * peak or abs(x[-1]) > 0.05 * peak:
        probs.append(f"{name}: no empieza/termina en silencio (clic)")
    # cortes periódicos (procesado por bloques): picos de |diff| espaciados regularmente
    d = np.abs(np.diff(x))
    big = np.where(d > 6 * (np.median(d) + 1e-9) + 0.1 * peak)[0]
    if len(big) >= 6:
        gaps = np.diff(big)
        common = np.bincount(gaps).argmax()
        if common > 32 and (gaps == common).mean() > 0.5:
            probs.append(f"{name}: cortes periódicos cada {common} muestras (procesado por bloques)")
    return probs


def check_mix(x, sr=SR, name="mezcla"):
    """Problemas de la mezcla final."""
    probs = []
    clip = _runs_above(x, 0.99) / sr
    if clip > 0.003:
        probs.append(f"{name}: saturación durante {clip * 1000:.0f} ms")
    return probs


def assert_ok(probs):
    if probs:
        raise RuntimeError("Control de audio falló:\n  - " + "\n  - ".join(probs))


if __name__ == "__main__":
    bad = 0
    for p in sys.argv[1:]:
        x, sr = read(p)
        probs = check_voice(x, sr, p)
        for pr in probs:
            print("✗", pr)
        bad += bool(probs)
    print("OK" if not bad else f"{bad} archivo(s) con problemas")
    sys.exit(1 if bad else 0)
