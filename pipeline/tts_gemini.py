"""Voz con Gemini TTS (Google). Devuelve WAV mono 48 kHz y guarda caché por texto.

Uso:  python3 pipeline/tts_gemini.py "Hola, soy Newton" salida.wav

La clave la inyecta el proxy del entorno (encabezado x-goog-api-key).
Cada llamada se registra en assets/art/ledger.json (tipo "tts") para llevar el gasto.
"""
import base64
import datetime
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio_qc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
CACHE = os.path.join(ROOT, "output", "_tts_cache")
LEDGER = os.path.join(ROOT, "assets", "art", "ledger.json")

# Voz fija de Newton: un sabio teatral y divertido.
NEWTON_VOICE = "Puck"
# Sin instrucciones de estilo: este modelo las lee en voz alta (en español o en inglés) y no
# admite instrucciones de sistema. El ritmo se ajusta después (TARGET_RATE) y cada frase se verifica.
NEWTON_STYLE = ""
TARGET_RATE = 5.5  # sílabas por segundo; si sale más lenta, se acelera sin cambiar el tono


def post(url, body, tries=6):
    """POST a la API de Gemini; espera y reintenta ante límites de frecuencia (429) o caídas (5xx)."""
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or k == tries - 1:
                raise
            wait = 20 * (k + 1)
            print(f"  Google respondió {e.code}; espero {wait} s")
            time.sleep(wait)


def verify(text, wav, threshold=0.8, alt=None):
    """Transcribe el audio con Gemini y compara con el texto esperado (proporción de coincidencia)."""
    import difflib
    import re
    with open(wav, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = {"contents": [{"parts": [{"inlineData": {"mimeType": "audio/wav", "data": b64}},
                                    {"text": "Transcribe exactamente todo lo que se escucha, sin comentarios."}]}]}
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent"
    heard = post(url, body)["candidates"][0]["content"]["parts"][0]["text"]
    norm = lambda s: re.sub(r"[^a-záéíóúñü ]", "", s.lower()).split()
    ratio = max(difflib.SequenceMatcher(None, norm(c), norm(heard)).ratio() for c in (text, alt) if c)
    return ratio >= threshold, ratio, heard


def decode_to_wav(data, mime, out):
    """Bytes de audio de Gemini -> WAV 48 kHz mono, sin silencios en los bordes y con fundidos.

    OJO (lección 1, docs/LECCIONES.md): según el modelo, Gemini entrega un WAV COMPLETO
    ("audio/wav", con encabezado RIFF y metadatos) o PCM crudo ("audio/L16;rate=24000").
    Leer un WAV como PCM crudo mete el encabezado y la cola como chasquidos y ruido a todo
    volumen. Por eso se detecta por el tipo Y por la firma "RIFF" de los bytes.
    """
    src_path = out + ".src"
    with open(src_path, "wb") as f:
        f.write(data)
    if data[:4] == b"RIFF" or "wav" in mime.lower():
        src = ["-f", "wav", "-i", src_path]
    else:
        rate = 24000
        for kv in mime.split(";"):
            if kv.strip().startswith("rate="):
                rate = int(kv.split("=")[1])
        src = ["-f", "s16le", "-ar", str(rate), "-ac", "1", "-i", src_path]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *src, "-ac", "1", "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
                    "afade=t=in:d=0.01,areverse,afade=t=in:d=0.03,areverse",
                    "-ar", "48000", out], check=True)
    os.remove(src_path)
    return out


def syllables(text):
    import re
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", text.lower())))


def synth(text, out, voice=NEWTON_VOICE, style=NEWTON_STYLE, tries=3, alt=None):
    """Genera la voz; si sale sospechosa (lee instrucciones, repite), reintenta."""
    for k in range(tries):
        try:
            return _synth(text, out, voice, style, alt)
        except RuntimeError as e:
            if k == tries - 1:
                raise
            print("  reintento:", e)


def _synth(text, out, voice, style, alt=None):
    key = hashlib.sha1(f"v2|{MODEL}|{voice}|{style}|{text}".encode()).hexdigest()[:16]  # v2: lectura WAV correcta
    os.makedirs(CACHE, exist_ok=True)
    cached = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(cached):
        body = {"contents": [{"parts": [{"text": style + text}]}],
                "generationConfig": {"responseModalities": ["AUDIO"],
                                     "speechConfig": {"voiceConfig": {
                                         "prebuiltVoiceConfig": {"voiceName": voice}}}}}
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
        data = post(url, body)
        part = next(p["inlineData"] for p in data["candidates"][0]["content"]["parts"]
                    if "inlineData" in p)
        decode_to_wav(base64.b64decode(part["data"]), part["mimeType"], cached)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                    "-of", "csv=p=0", cached], capture_output=True, text=True).stdout)
        tempo = min(1.6, max(1.0, TARGET_RATE / (syllables(text) / dur)))
        if tempo > 1.02:
            tmp = cached + ".tmp.wav"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", cached, "-af",
                            f"atempo={tempo:.3f}", tmp], check=True)
            os.replace(tmp, cached)
        # control: si dura mucho más de lo esperado (lee instrucciones o repite), se rechaza
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                    "-of", "csv=p=0", cached], capture_output=True, text=True).stdout)
        if dur > syllables(text) / 3.0 + 2.5:
            os.remove(cached)
            raise RuntimeError(f"Audio sospechoso ({dur:.1f}s para '{text[:40]}…'): revisar")
        probs = audio_qc.check_voice(audio_qc.read(cached)[0], name=f"'{text[:30]}…'")
        if probs:  # chasquidos, ruido o saturación: se descarta y se reintenta
            os.remove(cached)
            raise RuntimeError("; ".join(probs))
        ok, ratio, heard = verify(text, cached, alt=alt)  # alt: versión con cifras ("64 m")
        if not ok:
            os.remove(cached)
            raise RuntimeError(f"La voz no coincide con el texto ({ratio:.0%}): oí '{heard[:60]}'")
        led = json.load(open(LEDGER)) if os.path.exists(LEDGER) else []
        led.append({"date": datetime.datetime.now().isoformat(timespec="seconds"), "mode": "tts",
                    "model": MODEL, "prompt": text[:80],
                    "tokens": data.get("usageMetadata", {}).get("totalTokenCount")})
        with open(LEDGER, "w") as f:
            json.dump(led, f, indent=1, ensure_ascii=False)
    subprocess.run(["cp", cached, out], check=True)
    return out


if __name__ == "__main__":
    synth(sys.argv[1], sys.argv[2])
    print("Listo:", sys.argv[2])
