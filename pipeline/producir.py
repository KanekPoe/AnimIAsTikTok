"""Producción en lote: guion -> episodio -> video, con todos los controles.

Uso:  python3 pipeline/producir.py guiones/121_*.md guiones/122_*.md ...
      python3 pipeline/producir.py --prioridad        (todas las ideas del creador, prioridad: creador)

Por guion: validar_guion -> guion2ep -> nbl.py (voces con audio_qc y verificación por
transcripción, QA visual, mezcla con audio_qc, export). Un guion que falla no detiene el lote;
al final imprime un resumen y lo guarda en output/produccion.log.
Es seguro repetirlo: las voces se reutilizan de la caché, solo se paga lo nuevo.
"""
import glob
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = sys.executable


def run(guion):
    t0 = time.time()
    r = subprocess.run([PY, os.path.join(ROOT, "pipeline", "guion2ep.py"), guion], capture_output=True, text=True)
    if r.returncode:
        return False, "conversión: " + (r.stderr or r.stdout).strip()[-400:], None
    ep = r.stdout.strip().split("Episodio: ")[-1]
    r = subprocess.run([PY, os.path.join(ROOT, "pipeline", "nbl.py"), ep], capture_output=True, text=True)
    log = (r.stdout + r.stderr).strip()
    video = re.search(r"Listo: (.*final\.mp4)", log)
    dur = re.search(r"Duración: ([\d.]+)s", log)
    if r.returncode or not video:
        return False, "render: " + log[-600:], None
    return True, f"{float(dur.group(1)):.0f} s, {time.time() - t0:.0f} s de proceso", video.group(1)


def main(args):
    if "--prioridad" in args:
        guiones = sorted(p for p in glob.glob(os.path.join(ROOT, "guiones", "[0-9]*.md"))
                         if "prioridad: creador" in open(p, encoding="utf-8").read())
    else:
        guiones = args
    res = []
    for g in guiones:
        print(f"== {os.path.basename(g)}", flush=True)
        ok, msg, video = run(g)
        print(("   OK  " if ok else "   FALLÓ  ") + msg, flush=True)
        res.append((g, ok, msg, video))
    lines = [f"{'OK ' if ok else 'XX '} {os.path.basename(g)}  {msg if ok else msg.splitlines()[-1][:200]}"
             + (f"  -> {os.path.relpath(v, ROOT)}" if v else "") for g, ok, msg, v in res]
    with open(os.path.join(ROOT, "output", "produccion.log"), "a") as f:
        f.write(time.strftime("\n# %Y-%m-%d %H:%M\n") + "\n".join(lines) + "\n")
    print("\nResumen:\n" + "\n".join(lines))
    return 0 if all(ok for _, ok, _, _ in res) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
