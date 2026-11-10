"""Personajes 2D del canal Newton Bien Loco: Newton y Manzanita (Grease Pencil).

Estilo: caricatura con proporciones realistas, contorno fino café oscuro y sombreado de
dos tonos (cel shading). Newton en vista de tres cuartos mirando a la derecha.

Uso (hoja de personajes de prueba):
    blender45 -b --python blender/characters2d.py -- output/personajes.png

Partes animables (prefijo = nombre del personaje):
    <n>_root                         mover el personaje
    <n>_head_pivot                   inclinar la cabeza
    <n>_eye_L/R                      parpadeo (escala Z)
    <n>_mouth_closed / _mouth_open   hablar: alternar la escala Z entre ambas (0 ↔ 1)
    <n>_shoulder_L/R, <n>_elbow_L/R  brazos (rotación Y)
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gp2d import Kit, arc, circle, ellipse, setup_2d_scene, smooth  # noqa: E402

OUT = "#2B2024"  # contorno café oscuro (más suave que el negro)
LW = 0.022       # grosor del contorno

SKIN, SKIN_SH = "#F3CDB1", "#DFA98A"
HAIR, HAIR_SH, HAIR_HI = "#B9BCC2", "#8D9097", "#DCDEE2"
COAT, COAT_SH, COAT_HI = "#A8323A", "#7E222A", "#C4474F"
VEST, VEST_SH = "#F2ECDF", "#D8CFBD"
WHITE, WHITE_SH = "#FBFAF7", "#DCD8D0"
OCHRE, OCHRE_SH = "#D9A441", "#B3832B"
SHOE, GOLD = "#6B4A2E", "#E3B341"
EYE_D, BROW = "#3A2A22", "#7E8189"
MOUTH, TONGUE = "#7A2430", "#E06A6A"
APPLE, APPLE_SH, APPLE_HI = "#D7263D", "#A3162A", "#FF7A85"
LEAF, STEM = "#5DA640", "#6B4226"


def S(k, n, pts, fill, loc=(0, 0), parent=None, depth=0.0, it=2):
    """Forma suavizada con el contorno del estilo."""
    return k.shape(n, smooth(pts, it) if it else pts, fill, OUT, LW, loc, parent, depth)


def A(k, o, pts, fill=None, stroke=OUT, width=LW, cyclic=True, it=2):
    """Agrega un trazo suavizado a una pieza (sombra sin contorno: stroke=None)."""
    if it and cyclic:
        pts = smooth(pts, it)
    return k.add(o, pts, fill, stroke, width, cyclic)


def wavy(pts, amp=0.05, waves=10, it=2):
    """Contorno ondulado (cabello): desplaza los puntos sobre su normal con una senoide."""
    pts = smooth(pts, it)
    n = len(pts)
    out = []
    for i, (x, z) in enumerate(pts):
        (x0, z0), (x1, z1) = pts[i - 1], pts[(i + 1) % n]
        nx, nz = z1 - z0, -(x1 - x0)
        ln = math.hypot(nx, nz) or 1
        a = amp * math.sin(i / n * math.tau * waves)
        out.append((x + nx / ln * a, z + nz / ln * a))
    return out


def L(k, o, pts, color=OUT, width=LW):
    """Línea abierta (pliegues, cejas, detalles)."""
    return k.add(o, pts, None, color, width, False)


# ----------------------------------------------------------------------------
# Newton
# ----------------------------------------------------------------------------
def newton_arm(k, side, shoulder, upper, elbow_local, forearm, hand_fn, depth):
    """Brazo con pivote en hombro y codo. upper/forearm: polígonos locales."""
    sh = k.pivot(f"shoulder_{side}", shoulder, depth=depth)
    up = S(k, f"upper_{side}", upper, COAT, parent=sh)
    el = k.pivot(f"elbow_{side}", elbow_local, parent=sh, depth=-0.07)  # antebrazo al frente
    fo = S(k, f"forearm_{side}", forearm, COAT, parent=el)
    hand_fn(el)
    return sh, el, up, fo


def build_newton(x=0.0):
    """Isaac Newton: peluca larga gris ondulada, abrigo rojo, corbatín, calzón ocre."""
    k = Kit("newton")
    k.root.location.x = x

    # --- zapatos y medias -------------------------------------------------
    for n, cx in (("L", -0.45), ("R", 0.42)):
        leg = S(k, f"stocking_{n}", [(cx - 0.19, 0.2), (cx + 0.19, 0.2), (cx + 0.2, 1.95),
                                     (cx - 0.2, 1.95)], WHITE, depth=0.03, it=1)
        A(k, leg, [(cx + 0.06, 0.25), (cx + 0.17, 0.25), (cx + 0.18, 1.9), (cx + 0.08, 1.9)],
          WHITE_SH, None, it=1)
        shoe = S(k, f"shoe_{n}", [(cx - 0.3, 0.02), (cx + 0.42, 0.02), (cx + 0.45, 0.14),
                                  (cx + 0.15, 0.3), (cx - 0.25, 0.3)], SHOE, depth=0.02)
        A(k, shoe, [(cx - 0.04, 0.22), (cx + 0.14, 0.22), (cx + 0.14, 0.32), (cx - 0.04, 0.32)],
          GOLD, it=0)

    # --- calzón (breeches) ------------------------------------------------
    br = S(k, "breeches", [(-0.7, 1.82), (-0.22, 1.82), (0.0, 2.45), (0.2, 1.82), (0.66, 1.82),
                           (0.8, 3.35), (-0.82, 3.35)], OCHRE, depth=0.025, it=1)
    A(k, br, [(0.35, 1.9), (0.62, 1.9), (0.74, 3.2), (0.45, 3.2)], OCHRE_SH, None, it=1)
    for cx in (-0.46, 0.43):  # ligas de la rodilla
        A(k, br, [(cx - 0.24, 1.8), (cx + 0.24, 1.8), (cx + 0.24, 1.97), (cx - 0.24, 1.97)],
          OCHRE_SH, it=0)

    # --- abrigo largo -----------------------------------------------------
    coat = S(k, "coat", [(-1.38, 2.25), (1.32, 2.25), (1.02, 3.6), (0.97, 4.3), (1.15, 4.88),
                         (0.55, 5.15), (-0.55, 5.15), (-1.15, 4.88), (-0.97, 4.3), (-1.03, 3.6)],
             COAT)
    A(k, coat, [(0.72, 2.3), (1.25, 2.3), (0.96, 3.6), (0.92, 4.3), (1.08, 4.8), (0.8, 4.85),
                (0.66, 3.6)], COAT_SH, None)
    A(k, coat, [(-1.25, 2.35), (-0.95, 2.35), (-0.85, 3.5), (-0.9, 4.5), (-1.05, 4.5),
                (-0.95, 3.5)], COAT_HI, None)
    vest = S(k, "vest", [(-0.38, 2.55), (0.38, 2.55), (0.33, 4.9), (-0.33, 4.9)], VEST,
             depth=-0.01, it=1)
    A(k, vest, [(0.12, 2.6), (0.34, 2.6), (0.3, 4.85), (0.15, 4.85)], VEST_SH, None, it=1)
    trim = k.piece("coat_trim", depth=-0.012)
    for sx in (-1, 1):
        L(k, trim, [(sx * 0.4, 2.3), (sx * 0.38, 4.95)], COAT_SH, 0.03)
    for z in (3.0, 3.45, 3.9, 4.35):  # botones dorados
        A(k, trim, circle(-0.5, z, 0.07), GOLD, width=0.015, it=0)
    for sx in (-1, 1):  # solapas de bolsillo
        A(k, trim, [(sx * 0.55, 3.0), (sx * 0.98, 3.05), (sx * 0.96, 3.2), (sx * 0.55, 3.15)],
          COAT_SH, it=0)
    # corbatín largo (jabot)
    cr = S(k, "cravat", [(-0.3, 5.12), (0.3, 5.12), (0.22, 4.62), (0.32, 4.15), (0.04, 3.98),
                         (-0.22, 4.18), (-0.26, 4.64)], WHITE, depth=-0.02)
    A(k, cr, [(0.05, 4.9), (0.2, 4.6), (0.26, 4.2), (0.08, 4.05)], WHITE_SH, None)
    L(k, cr, [(-0.05, 4.95), (-0.1, 4.5), (-0.02, 4.1)], WHITE_SH, 0.018)

    # --- cabeza (3/4 hacia la derecha) ------------------------------------
    S(k, "neck", [(-0.2, 4.95), (0.22, 4.95), (0.22, 5.4), (-0.18, 5.4)], SKIN, depth=0.01, it=0)
    hp = k.pivot("head_pivot", (0.05, 5.32), depth=-0.03)
    hb = k.shape("hair_back", wavy([(-0.15, 1.52), (0.35, 1.48), (0.72, 1.18), (0.88, 0.7),
                                    (0.92, 0.22), (1.02, -0.25), (0.8, -0.66), (0.58, -0.35),
                                    (0.45, 0.02), (-0.38, 0.02), (-0.55, -0.42), (-0.92, -0.74),
                                    (-1.08, -0.2), (-1.0, 0.3), (-0.9, 0.82), (-0.72, 1.24),
                                    (-0.45, 1.46)], 0.035, 14), HAIR, OUT, LW, parent=hp,
                 depth=0.02)
    A(k, hb, [(-0.9, -0.55), (-0.62, -0.38), (-0.62, 0.3), (-0.8, 0.85), (-0.95, 0.3)],
      HAIR_SH, None)
    A(k, hb, [(0.62, -0.5), (0.85, -0.2), (0.82, 0.6), (0.66, 0.2)], HAIR_SH, None)
    for lx in (-0.82, -0.7, 0.75):  # mechones (ondas)
        L(k, hb, [(lx, 1.0), (lx - 0.06, 0.6), (lx + 0.02, 0.2), (lx - 0.05, -0.2)], HAIR_SH, 0.018)
    face = S(k, "face", [(0.05, 1.25), (0.5, 1.05), (0.56, 0.62), (0.47, 0.26), (0.22, 0.06),
                         (-0.02, 0.1), (-0.3, 0.32), (-0.42, 0.72), (-0.36, 1.12)],
             SKIN, parent=hp, depth=-0.01)
    A(k, face, [(-0.36, 1.08), (-0.41, 0.72), (-0.29, 0.34), (-0.21, 0.42), (-0.3, 0.72),
                (-0.27, 1.02)], SKIN_SH, None)  # sombra del lado lejano
    nose = k.piece("nose", (0, 0), hp, -0.025)  # nariz de perfil: solo línea del puente
    A(k, nose, [(0.45, 0.72), (0.6, 0.55), (0.53, 0.5), (0.45, 0.52)], SKIN, None, it=1)
    L(k, nose, [(0.44, 0.76), (0.6, 0.56), (0.54, 0.5), (0.47, 0.51)], OUT, 0.02)
    L(k, face, arc(0.47, 0.42, 0.08, 0.06, 200, 320), SKIN_SH, 0.016)  # pliegue de la mejilla
    hf = k.shape("hair_front", wavy([(-0.5, 1.06), (-0.2, 1.2), (0.2, 1.22), (0.5, 1.08),
                                     (0.6, 1.28), (0.3, 1.5), (-0.2, 1.53), (-0.58, 1.34)],
                                    0.025, 7), HAIR, OUT, LW, parent=hp, depth=-0.03)
    A(k, hf, [(-0.35, 1.32), (0.05, 1.43), (0.3, 1.38), (-0.05, 1.3)], HAIR_HI, None)

    # ojos (almendrados, mirando de lado), cejas y boca con media sonrisa
    for n, cx, rx in (("L", -0.04, 0.085), ("R", 0.32, 0.1)):
        e = k.piece(f"eye_{n}", (cx, 0.78), hp, -0.04)
        A(k, e, ellipse(0, 0, rx, 0.06), WHITE, it=0)
        A(k, e, circle(rx * 0.35, -0.005, 0.045), EYE_D, None, it=0)
        A(k, e, circle(rx * 0.35 + 0.015, 0.015, 0.013), WHITE, None, it=0)
        L(k, e, arc(0, 0.0, rx * 1.05, 0.075, 15, 165), OUT, 0.02)  # párpado
    br_ = k.piece("brows", (0, 0), hp, -0.04)
    L(k, br_, [(-0.16, 0.92), (-0.04, 0.95), (0.06, 0.93)], BROW, 0.035)
    L(k, br_, [(0.2, 0.95), (0.34, 1.0), (0.46, 0.96)], BROW, 0.035)  # ceja levantada
    closed = k.piece("mouth_closed", (0, 0), hp, -0.04)
    L(k, closed, [(0.02, 0.36), (0.14, 0.33), (0.28, 0.34), (0.37, 0.4)], OUT, 0.02)
    opened = k.piece("mouth_open", (0.17, 0.33), hp, -0.04)
    A(k, opened, [(-0.15, 0.03), (0.2, 0.06), (0.15, -0.12), (-0.08, -0.13)], MOUTH, it=2)
    A(k, opened, ellipse(0.03, -0.09, 0.08, 0.03), TONGUE, None, it=0)
    opened.scale = (1, 1, 0)

    # --- brazos -------------------------------------------------------------
    def apple_hand(el):  # mano derecha (lado izquierdo del cuadro) sostiene la manzana
        cuff = k.piece("cuff_R", parent=el, depth=-0.01)
        A(k, cuff, [(0.3, 0.42), (0.58, 0.2), (0.7, 0.32), (0.42, 0.55)], WHITE, it=1)
        ap = k.piece("apple", (0.52, 0.76), el, -0.02)
        A(k, ap, [(-0.24, 0.02), (-0.18, 0.2), (-0.03, 0.22), (0.0, 0.17), (0.04, 0.22),
                  (0.2, 0.2), (0.25, 0.02), (0.14, -0.2), (0.0, -0.17), (-0.14, -0.2)], APPLE)
        A(k, ap, [(0.08, -0.15), (0.2, -0.05), (0.2, 0.12), (0.12, 0.0)], APPLE_SH, None)
        A(k, ap, ellipse(-0.11, 0.08, 0.05, 0.07, rot=0.4), APPLE_HI, None, it=0)
        L(k, ap, [(0.0, 0.17), (0.03, 0.32)], STEM, 0.025)
        A(k, ap, ellipse(0.12, 0.3, 0.09, 0.04, rot=0.4), LEAF, it=0)
        hand = k.piece("hand_R", (0.52, 0.52), el, -0.03)  # dedos sujetando la manzana
        A(k, hand, [(-0.2, 0.0), (0.0, -0.12), (0.2, 0.0), (0.18, 0.14), (-0.18, 0.14)], SKIN)
        for fx in (-0.1, 0.0, 0.1):
            L(k, hand, [(fx, 0.14), (fx, 0.06)], SKIN_SH, 0.015)
        A(k, hand, ellipse(-0.24, 0.12, 0.07, 0.11, rot=-0.5), SKIN, it=0)  # pulgar

    def hip_hand(el):  # mano izquierda en la cadera
        cuff = k.piece("cuff_L", parent=el, depth=-0.01)
        A(k, cuff, [(-0.42, -0.08), (-0.55, -0.3), (-0.72, -0.2), (-0.6, 0.02)], WHITE, it=1)
        S(k, "hand_L", ellipse(-0.74, -0.2, 0.15, 0.12, rot=0.3), SKIN, parent=el, depth=-0.02)

    newton_arm(k, "R", (-0.95, 4.8),
               [(0.22, 0.12), (-0.25, 0.1), (-0.55, -0.9), (-0.12, -1.05)], (-0.35, -1.0),
               [(-0.2, -0.12), (0.18, -0.2), (0.6, 0.27), (0.38, 0.46)], apple_hand, 0.01)
    newton_arm(k, "L", (0.95, 4.8),
               [(-0.22, 0.12), (0.25, 0.1), (0.7, -0.88), (0.38, -1.05)], (0.55, -0.98),
               [(0.18, 0.1), (0.05, -0.22), (-0.6, -0.32), (-0.45, 0.05)], hip_hand, 0.01)
    for n in ("upper_R", "forearm_R", "upper_L", "forearm_L"):  # sombra en las mangas
        o = k.parts[n]
        pts = [tuple((p.position.x, p.position.z)) for p in o.data.layers[0].frames[0].drawing.strokes[0].points]
        cx = sum(p[0] for p in pts) / len(pts)
        cz = sum(p[1] for p in pts) / len(pts)
        A(k, o, [(cx + (px - cx) * 0.55 + 0.05, cz + (pz - cz) * 0.55 - 0.03) for px, pz in pts[::4]],
          COAT_SH, None, it=1)
    return k


# ----------------------------------------------------------------------------
# Manzanita
# ----------------------------------------------------------------------------
def build_manzanita(x=0.0, z=0.0, scale=1.0):
    """Manzanita: manzana roja escéptica, con hoja, ojos grandes y bracitos."""
    k = Kit("manzanita")
    k.root.location = (x, -0.5, z)
    k.root.scale = (scale,) * 3
    pts = []
    for i in range(80):
        t = i / 80 * math.tau
        dip = 0.22 * math.exp(-((t - math.pi / 2) / 0.32) ** 2)
        dip += 0.1 * math.exp(-((t - 3 * math.pi / 2) / 0.3) ** 2)
        pts.append((1.05 * math.cos(t) * (1 - 0.05 * math.sin(t)), math.sin(t) - dip * math.sin(t)))
    for s, sx in (("L", -1), ("R", 1)):
        arm = k.pivot(f"shoulder_{s}", (sx * 0.98, -0.05), depth=0.02)
        L(k, k.piece(f"armline_{s}", parent=arm), [(0, 0), (sx * 0.3, -0.2), (sx * 0.5, -0.4)],
          OUT, 0.035)
        S(k, f"hand_{s}", circle(sx * 0.52, -0.43, 0.1), "#C62F3B", parent=arm, it=0)
    body = k.shape("body", pts, APPLE, OUT, LW * 1.4)
    A(k, body, [(0.35, -0.85), (0.85, -0.45), (0.98, 0.2), (0.8, 0.6), (0.75, 0.0), (0.55, -0.55)],
      APPLE_SH, None)
    A(k, body, ellipse(-0.5, 0.42, 0.18, 0.28, rot=0.5), APPLE_HI, None, it=0)
    hp = k.pivot("head_pivot", (0, 0), depth=-0.02)
    stem = k.piece("stem", (0, 0), hp, 0.02)
    A(k, stem, [(-0.05, 0.75), (0.05, 0.75), (0.12, 1.25), (0.04, 1.27)], STEM)
    A(k, stem, ellipse(0.45, 1.15, 0.3, 0.13, rot=0.4), LEAF, it=0)
    L(k, stem, [(0.2, 1.08), (0.68, 1.22)], "#3E7A2A", 0.015)
    for s, cx in (("L", -0.3), ("R", 0.3)):
        e = k.piece(f"eye_{s}", (cx, 0.2), hp, -0.04)
        A(k, e, ellipse(0, 0, 0.2, 0.24), WHITE, it=0)
        A(k, e, circle(-0.03, -0.03, 0.11), EYE_D, None, it=0)
        A(k, e, circle(0.01, 0.02, 0.035), WHITE, None, it=0)
    brows = k.piece("brows", (0, 0), hp, -0.05)  # cejas escépticas
    L(k, brows, [(-0.5, 0.56), (-0.14, 0.48)], OUT, 0.045)
    L(k, brows, [(0.14, 0.53), (0.5, 0.62)], OUT, 0.045)
    closed = k.piece("mouth_closed", (0, -0.35), hp, -0.04)
    L(k, closed, [(-0.18, 0.02), (0.0, -0.02), (0.2, 0.06)], OUT, 0.03)  # mueca escéptica
    opened = k.piece("mouth_open", (0, -0.35), hp, -0.04)
    A(k, opened, [(-0.2, 0.05), (0.2, 0.05), (0.12, -0.18), (-0.12, -0.18)], MOUTH)
    A(k, opened, ellipse(0, -0.12, 0.08, 0.035), TONGUE, None, it=0)
    opened.scale = (1, 1, 0)
    return k


# ----------------------------------------------------------------------------
def character_sheet(out):
    """Hoja de prueba: Newton con la manzana y Manzanita escéptica a su lado."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_2d_scene("#DCEBF2")
    build_newton(-1.15)
    m = build_manzanita(1.95, 1.6, 0.75)
    m.parts["shoulder_L"].rotation_euler = (0, math.radians(35), 0)
    sc = bpy.context.scene
    sc.camera.location.x = 0.3
    sc.camera.location.z = 3.55
    sc.camera.data.ortho_scale = 10.5
    sc.render.filepath = out
    bpy.ops.render.render(write_still=True)
    print("Hoja:", out)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    character_sheet(os.path.abspath(argv[0] if argv else "output/personajes.png"))
