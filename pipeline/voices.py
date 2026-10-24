"""Genera las voces del episodio y la línea de tiempo (timeline.json).

Uso:
    python3 pipeline/voices.py episodes/ep01_control_mundial.py

Salida en output/<slug>/:
    audio/*.wav     una pista por frase (48 kHz mono, ya con efecto de voz)
    timeline.json   inicio/fin de cada bloque y frase + envolvente por frame (para las bocas)
"""
import importlib.util
import json
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_DIR = os.path.join(ROOT, "assets", "voices")
SR = 48000
FPS = 30

FX = {
    "reverb": "aecho=0.8:0.6:45|90:0.25|0.15",
    "warm": "bass=g=3,lowpass=f=6500,aecho=0.8:0.5:30:0.12",
    "underwater": "bass=g=6,lowpass=f=3200,aecho=0.8:0.7:70|140:0.35|0.2",
    "nervous": "vibrato=f=7:d=0.3,acrusher=bits=10:mix=0.3",
    "clean": "highpass=f=120,acompressor",
    "crushed": "highpass=f=100,acrusher=bits=6:mode=log:mix=0.45,aphaser",
    "shimmer": "chorus=0.6:0.9:50|60:0.4|0.32:0.25|0.4:2|1.3,aecho=0.8:0.5:60:0.15",
}

# Tiempos del montaje (segundos)
HOOK_MIN = 2.6       # duración mínima del gancho
TURN_INTRO = 0.35    # vuelo del globo / cambio de contador antes de la primera frase
LINE_GAP = 0.12      # silencio entre frases
TURN_TAIL = 0.2
OUTRO = 3.6


def load_episode(path):
    spec = importlib.util.spec_from_file_location("episode", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_wav(path):
    with wave.open(path) as w:
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
        return x, w.getframerate()


def write_wav(path, x, sr=SR):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def trim(x, sr, thr=0.015, pad=0.04):
    env = np.abs(x)
    idx = np.where(env > thr)[0]
    if len(idx) == 0:
        return x
    a = max(0, idx[0] - int(pad * sr))
    b = min(len(x), idx[-1] + int(pad * sr))
    return x[a:b]


def squeeze_silence(x, sr, thr=0.012, max_gap=0.09):
    """Acorta las pausas internas a max_gap segundos (ritmo TikTok)."""
    hop = int(0.01 * sr)
    n = len(x) // hop
    loud = np.array([np.max(np.abs(x[i * hop:(i + 1) * hop])) > thr for i in range(n)])
    keep, run = [], 0
    for i in range(n):
        run = 0 if loud[i] else run + 1
        if run * 0.01 <= max_gap:
            keep.append(x[i * hop:(i + 1) * hop])
    return np.concatenate(keep) if keep else x


def syllables(text):
    """Cuenta aproximada de sílabas (grupos de vocales) para detectar audios anómalos."""
    import re
    t = text.lower().replace("72", "setenta y dos")
    t = re.sub(r"\d", " uno ", t)
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", t)))


def synth(text, voice, out_path, tmp_dir, tries=6):
    """Genera la frase; si sale demasiado lenta (balbuceo del TTS) la regenera."""
    best = None
    for k in range(tries):
        d = _synth_once(text, voice, out_path, tmp_dir, noise=0.5 + 0.08 * k)
        rate = syllables(text) / d
        if best is None or abs(rate - 6.5) < abs(best[1] - 6.5):
            best = (d, rate, k)
            os.replace(out_path, out_path + ".best")
        if 4.8 <= rate <= 8.6:
            break
    os.replace(out_path + ".best", out_path)
    if not 4.8 <= best[1] <= 8.6:
        print(f"  [aviso] ritmo raro ({best[1]:.1f} síl/s): {text}")
    return best[0]


def _synth_once(text, voice, out_path, tmp_dir, noise=0.5):
    model = os.path.join(VOICE_DIR, voice["model"], voice["model"] + ".onnx")
    raw = os.path.join(tmp_dir, "raw.wav")
    subprocess.run(["piper", "-m", model, "--length-scale", str(voice["speed"]),
                    "--noise-scale", f"{noise:.2f}", "--noise-w", "0.5", "-f", raw],
                   input=text.encode(), check=True, capture_output=True)
    x, sr = read_wav(raw)
    clean = os.path.join(tmp_dir, "clean.wav")
    write_wav(clean, trim(x, sr), sr)
    p = voice["pitch"]
    tempo = voice.get("tempo", 1.0)  # acelera sin cambiar el tono
    af = (f"asetrate={int(sr * p)},aresample={SR},atempo={tempo / p:.4f},"
          + FX[voice["fx"]])
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", clean, "-af", af, "-ac", "1",
                    "-ar", str(SR), out_path], check=True)
    y, _ = read_wav(out_path)
    y = squeeze_silence(trim(y, SR, thr=0.03), SR)
    y = y / (np.max(np.abs(y)) + 1e-6) * 0.89  # normaliza a -1 dB
    write_wav(out_path, y)
    return len(y) / SR


def envelope(path):
    """RMS por frame de video, normalizado 0..1 (para animar la boca)."""
    x, sr = read_wav(path)
    hop = sr // FPS
    env = [float(np.sqrt(np.mean(x[i:i + hop] ** 2))) for i in range(0, len(x), hop)]
    m = max(env) or 1
    return [round(min(1.0, e / m * 1.3), 3) for e in env]


def main():
    ep = load_episode(sys.argv[1])
    out = os.path.join(ROOT, "output", ep.SLUG)
    adir = os.path.join(out, "audio")
    os.makedirs(adir, exist_ok=True)

    tl = {"fps": FPS, "slug": ep.SLUG, "blocks": []}

    # Gancho con narrador
    path = os.path.join(adir, "00_hook.wav")
    d = synth(ep.HOOK["say"], ep.VOICES["narrator"], path, adir)
    t0 = 0.15
    hook_end = max(HOOK_MIN, t0 + d + 0.25)
    tl["blocks"].append({"type": "hook", "start": 0.0, "end": hook_end, "texts": ep.HOOK["texts"],
                         "lines": [{"wav": path, "start": t0, "end": t0 + d, "speaker": "narrator",
                                    "env": envelope(path)}]})
    t = hook_end

    for i, turn in enumerate(ep.TURNS):
        start = t
        t += TURN_INTRO
        lines = []
        for j, ln in enumerate(turn["lines"]):
            path = os.path.join(adir, f"{i + 1:02d}_{turn['robot']}_{j + 1}.wav")
            d = synth(ln.get("say", ln["text"]), ep.VOICES[turn["robot"]], path, adir)
            lines.append({**ln, "wav": path, "start": t, "end": t + d, "speaker": turn["robot"],
                          "env": envelope(path)})
            print(f"  {turn['robot']:9s} {d:4.2f}s {syllables(ln.get('say', ln['text'])) / d:4.1f} síl/s"
                  f"  {ln['text']}")
            t += d + LINE_GAP
        t += TURN_TAIL - LINE_GAP
        tl["blocks"].append({"type": "turn", "index": i + 1, "robot": turn["robot"],
                             "label": turn["label"], "reactor": turn["reactor"], "start": start,
                             "end": t, "lines": lines})

    tl["blocks"].append({"type": "outro", "start": t, "end": t + OUTRO, "text": ep.OUTRO["text"],
                         "labels": {tr["robot"]: tr["label"] for tr in ep.TURNS}})
    tl["duration"] = t + OUTRO
    tl["frames"] = int(round(tl["duration"] * FPS))
    for f in ("raw.wav", "clean.wav"):
        p = os.path.join(adir, f)
        if os.path.exists(p):
            os.remove(p)
    with open(os.path.join(out, "timeline.json"), "w") as f:
        json.dump(tl, f, ensure_ascii=False, indent=1)
    print(f"Duración total: {tl['duration']:.1f}s ({tl['frames']} frames) -> {out}/timeline.json")


if __name__ == "__main__":
    main()
