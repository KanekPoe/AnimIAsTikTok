"""Pruebas de regresión del audio (sin internet, sin gastar créditos).

Correr:  python3 tests/test_audio.py        (o: python3 -m unittest discover tests)

Cubren la lección 1 de docs/LECCIONES.md: el TTS entregaba un WAV completo que se leía como PCM
crudo (chasquido al inicio + ruido a todo volumen al final de cada frase) y un "whoosh" que
filtraba por bloques (cortes periódicos). Si alguna prueba falla, NO renderices: arregla primero.
"""
import io
import os
import struct
import sys
import tempfile
import unittest
import wave

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import audio_qc  # noqa: E402
import sfx  # noqa: E402
from tts_gemini import decode_to_wav  # noqa: E402

SR = 24000


def fake_speech(d=1.2, sr=SR):
    """Algo parecido a una frase: tono con armónicos y envolvente silábica."""
    t = np.arange(int(d * sr)) / sr
    x = sum(np.sin(2 * np.pi * f * t) / k for k, f in enumerate((180, 360, 540, 900), 1))
    x *= 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t) ** 2
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.05)
    x = x / np.abs(x).max() * 0.6
    return np.concatenate([np.zeros(int(0.2 * sr)), x, np.zeros(int(0.2 * sr))])


def wav_bytes(x, sr=SR, trailing_junk=True):
    """WAV como el que entrega Gemini: encabezado RIFF + datos (+ un chunk extra al final)."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())
    data = buf.getvalue()
    if trailing_junk:  # chunk de metadatos al final (lo que se volvía ruido)
        junk = b"LIST" + struct.pack("<I", 4000) + bytes([0xFF, 0x7F]) * 2000
        data = data[:4] + struct.pack("<I", len(data) - 8 + len(junk)) + data[8:] + junk
    return data


def decode(data, mime):
    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "o.wav")
        decode_to_wav(data, mime, out)
        return audio_qc.read(out)[0]


class TestDecodificacionTTS(unittest.TestCase):
    def test_wav_completo_no_mete_chasquidos(self):
        x = decode(wav_bytes(fake_speech()), "audio/wav")
        self.assertEqual(audio_qc.check_voice(x), [])

    def test_wav_detectado_por_firma_aunque_el_tipo_diga_pcm(self):
        # si Google vuelve a cambiar el tipo declarado, la firma RIFF nos salva
        x = decode(wav_bytes(fake_speech()), "audio/L16;rate=24000")
        self.assertEqual(audio_qc.check_voice(x), [])

    def test_pcm_crudo_sigue_funcionando(self):
        pcm = (fake_speech() * 32767).astype(np.int16).tobytes()
        x = decode(pcm, "audio/L16;codec=pcm;rate=24000")
        self.assertEqual(audio_qc.check_voice(x), [])

    def test_el_error_original_se_detecta(self):
        # reproducir el bug: leer el WAV como PCM crudo
        data = wav_bytes(fake_speech())
        buggy = np.frombuffer(data[: len(data) // 2 * 2], np.int16).astype(np.float32) / 32768
        self.assertTrue(audio_qc.check_voice(buggy), "el control no detectó el error original")


class TestControlDeVoz(unittest.TestCase):
    def test_voz_limpia_pasa(self):
        x = fake_speech(sr=48000)
        x = x[int(0.2 * 48000):-int(0.2 * 48000)]
        fade = np.minimum(1, np.arange(len(x)) / 480) * np.minimum(1, (len(x) - np.arange(len(x))) / 1440)
        self.assertEqual(audio_qc.check_voice(x * fade, 48000), [])

    def test_ruido_al_final_falla(self):
        x = fake_speech(sr=48000)
        x[-int(0.15 * 48000):] = np.sign(np.sin(np.arange(int(0.15 * 48000)) * 0.02))
        self.assertTrue(audio_qc.check_voice(x, 48000))

    def test_golpe_al_inicio_falla(self):
        x = fake_speech(sr=48000)
        x[:60] = 0.9
        self.assertTrue(audio_qc.check_voice(x, 48000))


class TestEfectos(unittest.TestCase):
    EFECTOS = {"whoosh": lambda: sfx.whoosh(0.35), "whoosh_bajada": lambda: sfx.whoosh(0.4, up=False),
               "pop": sfx.pop, "stamp": sfx.stamp, "thud": sfx.thud, "chime": sfx.chime,
               "impact": sfx.impact, "click": sfx.click}

    def test_ningun_efecto_tiene_cortes_ni_clics(self):
        for name, f in self.EFECTOS.items():
            with self.subTest(efecto=name):
                self.assertEqual(audio_qc.check_sfx(f(), name=name), [])

    def test_el_whoosh_viejo_se_detecta(self):
        # reproducir el bug: filtrar ruido por bloques de 512 muestras
        n = sfx.noise(0.35)
        out = np.concatenate([sfx.lowpass(n[i:i + 512], 8) for i in range(0, len(n), 512)])
        out *= np.sin(np.linspace(0, np.pi, len(out))) ** 1.5
        self.assertTrue(audio_qc.check_sfx(out), "el control no detectó los cortes por bloques")


if __name__ == "__main__":
    unittest.main(verbosity=2)
