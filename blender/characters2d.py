"""Personajes 2D del canal Newton Bien Loco: Newton y Manzanita (Grease Pencil).

Uso (hoja de personajes de prueba):
    blender45 -b --python blender/characters2d.py -- output/personajes.png

Partes animables (prefijo = nombre del personaje):
    <n>_root            mover el personaje
    <n>_head_pivot      inclinar la cabeza
    <n>_eye_L/R         parpadeo (escala Z)
    <n>_mouth_closed / <n>_mouth_open   hablar: alternar escala entre ambas
    <n>_arm_L/R         brazos (rotación Y alrededor del hombro)
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gp2d import Kit, arc, circle, ellipse, rrect, setup_2d_scene, smooth  # noqa: E402

SKIN, SKIN_SHADE = "#F6D2B5", "#E8B596"
WIG, WIG_SHADE = "#F4F1EA", "#D9D3C7"
COAT, COAT_DARK = "#2D3E70", "#22305A"
GOLD, WHITE = "#E8B53A", "#FFFFFF"
STOCKING, SHOE = "#5A5F6E", "#2A2A2A"
BLACK, MOUTH, TONGUE, CHEEK = "#1E1E28", "#7A2430", "#E86A6A", "#F3A6A0"


def face_eyes(k, hp, z, dx, r=0.3, depth=-0.06, look=(0.04, -0.02)):
    """Ojos grandes estilo caricatura: blanco, pupila y brillo."""
    for s, sx in (("L", -1), ("R", 1)):
        e = k.piece(f"eye_{s}", (sx * dx, z), hp, depth)
        k.add(e, ellipse(0, 0, r * 0.85, r))
        k.add(e, circle(look[0], look[1], r * 0.48), fill=BLACK, stroke=None)
        k.add(e, circle(look[0] + r * 0.18, look[1] + r * 0.2, r * 0.15), fill=WHITE, stroke=None)


def mouths(k, hp, z, w=0.36, depth=-0.06):
    """Boca cerrada (sonrisa) y abierta; para hablar se alterna su escala."""
    closed = k.piece("mouth_closed", (0, z), hp, depth)
    k.add(closed, arc(0, 0.1, w, 0.18, 200, 340), fill=None, cyclic=False, width=0.045)
    opened = k.piece("mouth_open", (0, z), hp, depth)
    k.add(opened, smooth([(-w, 0.05), (w, 0.05), (w * 0.6, -0.3), (-w * 0.6, -0.3)], 3), fill=MOUTH)
    k.add(opened, ellipse(0, -0.2, w * 0.45, 0.08), fill=TONGUE, stroke=None)
    opened.scale = (1, 1, 0)  # empieza cerrada
    return closed, opened


# ----------------------------------------------------------------------------
def build_newton(x=0.0):
    """Isaac Newton chibi: peluca blanca rizada, abrigo azul con botones dorados."""
    k = Kit("newton")
    k.root.location.x = x

    # piernas y zapatos
    for sx in (-1, 1):
        k.shape(f"leg_{sx}", rrect(sx * 0.38 - 0.2, 0.25, sx * 0.38 + 0.2, 1.1, 0.12), STOCKING, depth=0.02)
        shoe = k.shape(f"shoe_{sx}", ellipse(sx * 0.42, 0.2, 0.36, 0.2), SHOE, depth=0.0)
        k.add(shoe, rrect(sx * 0.42 - 0.09, 0.25, sx * 0.42 + 0.09, 0.36, 0.03), fill=GOLD)

    # brazos (detrás del abrigo), pivote en el hombro
    for s, sx in (("L", -1), ("R", 1)):
        arm = k.pivot(f"arm_{s}", (sx * 0.95, 2.65), depth=0.03)
        k.shape(f"sleeve_{s}", rrect(-0.24, -1.15, 0.24, 0.1, 0.2), COAT, parent=arm)
        k.shape(f"cuff_{s}", rrect(-0.27, -1.3, 0.27, -1.05, 0.08), WHITE, parent=arm, depth=-0.01)
        k.shape(f"hand_{s}", circle(0, -1.5, 0.24), SKIN, parent=arm, depth=-0.02)

    # abrigo
    coat = k.shape("coat", smooth([(-1.3, 0.9), (1.3, 0.9), (0.9, 2.95), (-0.9, 2.95)], 2), COAT)
    k.add(coat, [(0, 1.0), (0, 2.75)], fill=None, stroke=COAT_DARK, width=0.03, cyclic=False)
    for i, z in enumerate((1.4, 1.85, 2.3)):
        k.add(coat, circle(0.22, z, 0.09), fill=GOLD, width=0.02)
    for sx in (-1, 1):  # bolsillos
        k.add(coat, [(sx * 0.55, 1.35), (sx * 1.0, 1.35)], fill=None, stroke=COAT_DARK, width=0.04,
              cyclic=False)
    # corbatín (jabot) con volantes
    jab = k.piece("jabot", depth=-0.02)
    for i, (dx, z, r) in enumerate(((0, 2.85, 0.28), (-0.12, 2.6, 0.22), (0.12, 2.6, 0.22),
                                    (0, 2.4, 0.2))):
        k.add(jab, circle(dx, z, r), fill=WHITE)

    # cabeza
    hp = k.pivot("head_pivot", (0, 2.9), depth=-0.05)
    back = k.piece("wig_back", (0, 0), hp, depth=0.04)  # rizos detrás de la cara
    for sx in (-1, 1):
        for i, z in enumerate((1.6, 1.15, 0.7, 0.3)):
            xo = sx * (1.25 + 0.12 * math.sin(i * 1.7))
            k.add(back, circle(xo, z, 0.42 - 0.03 * i), fill=WIG if i % 2 == 0 else WIG_SHADE)
    k.add(back, ellipse(0, 1.5, 1.35, 1.25), fill=WIG)
    face = k.shape("face", ellipse(0, 1.2, 1.12, 1.25), SKIN, parent=hp)
    k.add(face, ellipse(0.1, 0.95, 0.16, 0.12), fill=SKIN_SHADE, stroke=None)  # nariz
    for sx in (-1, 1):
        k.add(face, ellipse(sx * 0.68, 0.72, 0.2, 0.11), fill=CHEEK, stroke=None)
    top = k.piece("wig_top", (0, 0), hp, depth=-0.08)  # flequillo de rizos
    for i, xo in enumerate((-0.95, -0.5, 0.0, 0.5, 0.95)):
        k.add(top, circle(xo, 2.25 - 0.1 * abs(xo), 0.45), fill=WIG)
    for i, xo in enumerate((-0.72, -0.25, 0.25, 0.72)):
        k.add(top, circle(xo, 2.45, 0.38), fill=WIG_SHADE if i % 2 else WIG)
    brows = k.piece("brows", (0, 0), hp, depth=-0.07)
    for sx in (-1, 1):
        k.add(brows, arc(sx * 0.42, 1.55, 0.22, 0.08, 20, 160), fill=None, stroke="#8A8378",
              width=0.05, cyclic=False)
    face_eyes(k, hp, 1.25, 0.42, 0.28)
    mouths(k, hp, 0.5, 0.3)
    return k


def build_manzanita(x=0.0, z=0.0, scale=1.0):
    """Manzanita: manzana roja escéptica con hoja, ojos grandes y bracitos."""
    k = Kit("manzanita")
    k.root.location = (x, -0.5, z)
    k.root.scale = (scale,) * 3
    pts = []
    for i in range(80):
        t = i / 80 * math.tau
        rx, rz = 1.05, 1.0
        dip = 0.22 * math.exp(-((t - math.pi / 2) / 0.32) ** 2)   # hendidura de arriba
        dip += 0.1 * math.exp(-((t - 3 * math.pi / 2) / 0.3) ** 2)  # base
        pts.append((rx * math.cos(t) * (1 - 0.05 * math.sin(t)), rz * math.sin(t) - dip * math.sin(t)))
    for s, sx in (("L", -1), ("R", 1)):  # bracitos
        arm = k.pivot(f"arm_{s}", (sx * 0.95, 0.0), depth=0.02)
        k.add(k.piece(f"armline_{s}", parent=arm), [(0, 0), (sx * 0.45, -0.35)], fill=None,
              width=0.05, cyclic=False)
        k.shape(f"hand_{s}", circle(sx * 0.5, -0.4, 0.11), "#C62F3B", parent=arm)
    body = k.shape("body", pts, "#E63946")
    k.add(body, ellipse(-0.45, 0.45, 0.22, 0.32, rot=0.5), fill="#FF7A84", stroke=None)  # brillo
    hp = k.pivot("head_pivot", (0, 0), depth=-0.02)
    stem = k.piece("stem", (0, 0), hp, depth=0.02)
    k.add(stem, smooth([(-0.05, 0.75), (0.05, 0.75), (0.12, 1.25), (0.04, 1.27)], 2), fill="#6B4226")
    k.add(stem, ellipse(0.45, 1.15, 0.3, 0.13, rot=0.4), fill="#4CAF50")
    face_eyes(k, hp, 0.2, 0.32, 0.24, look=(-0.03, -0.02))
    brows = k.piece("brows", (0, 0), hp, depth=-0.05)  # cejas escépticas
    k.add(brows, [(-0.5, 0.58), (-0.15, 0.5)], fill=None, width=0.05, cyclic=False)
    k.add(brows, [(0.15, 0.55), (0.5, 0.62)], fill=None, width=0.05, cyclic=False)
    mouths(k, hp, -0.35, 0.2)
    return k


# ----------------------------------------------------------------------------
def character_sheet(out):
    """Hoja de prueba: Newton y Manzanita, neutros y hablando."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_2d_scene()
    n = build_newton(-1.5)
    m = build_manzanita(2.2, 2.0, 1.0)
    # pose: Newton levanta un brazo y habla; Manzanita escéptica
    n.parts["arm_R"].rotation_euler = (0, math.radians(-120), 0)
    n.parts["mouth_closed"].scale = (1, 1, 0)
    n.parts["mouth_open"].scale = (1, 1, 1)
    n.parts["head_pivot"].rotation_euler = (0, math.radians(-6), 0)
    m.parts["arm_L"].rotation_euler = (0, math.radians(40), 0)
    sc = bpy.context.scene
    sc.camera.location.x = 0.3
    sc.camera.location.z = 3.2
    sc.camera.data.ortho_scale = 14
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("Hoja:", out)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    character_sheet(os.path.abspath(argv[0] if argv else "output/personajes.png"))
