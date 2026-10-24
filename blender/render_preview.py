"""Renderiza una imagen con todos los personajes en fila (output/preview.png).

Uso:
    blender -b output/llm_characters.blend --python blender/render_preview.py
    blender -b output/llm_characters.blend --python blender/render_preview.py -- --only claude
"""
import math
import os
import sys

import bpy

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only = argv[argv.index("--only") + 1] if "--only" in argv else None

sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 48
sc.cycles.use_denoising = True

cam = sc.camera
if only:
    root = bpy.data.objects[f"{only}_root"]
    sc.render.resolution_x, sc.render.resolution_y = 800, 1000
    cam.location = (root.location.x + 2.2, -6.5, 2.3)
    cam.rotation_euler = (math.radians(86), 0, math.radians(18))
    sc.render.filepath = os.path.join(OUT, f"preview_{only}.png")
else:
    xs = [o.location.x for o in bpy.data.objects if o.name.endswith("_root")]
    sc.render.resolution_x, sc.render.resolution_y = 2400, 760
    cam.data.lens = 50
    cam.location = (sum(xs) / len(xs), -34, 2.4)
    cam.rotation_euler = (math.radians(89), 0, 0)
    sc.render.filepath = os.path.join(OUT, "preview.png")

try:
    bpy.ops.render.render(write_still=True)
except RuntimeError:  # algunos builds no traen OpenImageDenoise
    sc.cycles.use_denoising = False
    bpy.ops.render.render(write_still=True)
print("Preview ->", sc.render.filepath)
