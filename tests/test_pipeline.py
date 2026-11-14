"""Pruebas del pipeline de guiones (sin internet, sin gastar créditos).

Correr:  python3 tests/test_pipeline.py
"""
import glob
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
from numeros import a_palabras  # noqa: E402
from tts_gemini import VOICES  # noqa: E402
import guion2ep  # noqa: E402


class TestNumeros(unittest.TestCase):
    CASOS = {
        "13,800 millones": "trece mil ochocientos millones",
        "-180 °C": "menos ciento ochenta grados",
        "2 cm": "dos centímetros",
        "1 cm": "un centímetro",
        "21 millones": "veintiún millones",
        "3.8 cm": "tres punto ocho centímetros",
        "en 2019": "en dos mil diecinueve",
        "107,000 km/h": "ciento siete mil kilómetros por hora",
        "1,000,000": "un millón",
        "100 billones": "cien billones",
        "99.8%": "noventa y nueve punto ocho por ciento",
        "10⁶⁶": "diez a la sesenta y seis",
        "1665–1666": "mil seiscientos sesenta y cinco a mil seiscientos sesenta y seis",
        "Cristal 5D": "Cristal cinco D",
        "el GTA 6?": "el GTA seis?",
        "Stephenson 2-18": "Stephenson dos dieciocho",
        "Sagitario B2": "Sagitario B dos",
        "de 10 - 20 km": "de diez a veinte kilómetros",
    }

    def test_casos(self):
        for src, want in self.CASOS.items():
            with self.subTest(src=src):
                self.assertEqual(a_palabras(src), want)

    def test_texto_sin_numeros_no_cambia(self):
        s = "¿Qué onda con los agujeros negros? Neta, wacha."
        self.assertEqual(a_palabras(s), s)


class TestConversion(unittest.TestCase):
    def test_todos_los_guiones_convierten_y_tienen_rig_y_voz(self):
        for g in sorted(glob.glob(os.path.join(ROOT, "guiones", "[0-9]*.md"))):
            with self.subTest(guion=os.path.basename(g)):
                ep_path = guion2ep.convert(g)
                spec = importlib.util.spec_from_file_location("ep", ep_path)
                ep = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(ep)
                for sc in ep.SCENES:
                    self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "art", "fondos", sc["bg"] + ".png")))
                    for ln in sc["lines"]:
                        who = ln.get("who", "newton")
                        self.assertIn(who, VOICES)
                        self.assertFalse(any(ch.isdigit() for ch in ln["say"]), ln["say"])
                        if "pose" in ln:
                            base = "newton/rig" if who == "newton" else f"colegas/{who}/rig"
                            self.assertTrue(os.path.isdir(os.path.join(ROOT, "assets", "art", base, ln["pose"])),
                                            f"{who}/{ln['pose']}")
                        for ev in ln["events"]:
                            if "img" in ev:
                                self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "art", ev["img"] + ".png")))


if __name__ == "__main__":
    unittest.main(verbosity=1)
