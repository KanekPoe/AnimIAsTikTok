"""Genera los personajes 3D de los LLMs: Claude, ChatGPT, Gemini, DeepSeek, Grok y Mistral.

Uso (desde la raíz del repo):
    blender --background --python blender/build_models.py
    blender --background --python blender/build_models.py -- --only claude grok

Salida en ./output: llm_characters.blend (todos juntos) y un .glb por personaje.
Cada personaje es una Collection con un Empty "<nombre>_root" (muévelo/anímalo) y
partes con pivotes para animar: head_pivot, shoulder_L/R, hip_L/R, eye_L/R...
La escena queda en formato vertical 1080x1920 @ 30fps para TikTok.
"""
import math
import os
import sys

import bpy

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def rgba(h):
    h = h.lstrip("#")
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return (r, g, b, 1.0)


def mat(name, color, rough=0.45, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = rgba(color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[key].default_value = rgba(color)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m


class B:
    """Crea primitivas dentro de la collection del personaje, parentadas a un pivote."""

    def __init__(self, name):
        self.name = name
        self.col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(self.col)
        self.root = bpy.data.objects.new(f"{name}_root", None)
        self.col.objects.link(self.root)

    def _fin(self, name, m, loc, rot, scale, parent, smooth=True, bevel=0.0):
        o = bpy.context.active_object
        o.name = name
        o.location, o.rotation_euler, o.scale = loc, rot, scale
        for c in list(o.users_collection):
            c.objects.unlink(o)
        self.col.objects.link(o)
        o.data.materials.append(m)
        o.parent = parent or self.root
        if bevel:
            md = o.modifiers.new("bevel", "BEVEL")
            md.width, md.segments = bevel, 4
        if smooth:
            for p in o.data.polygons:
                p.use_smooth = True
        return o

    def sphere(self, n, m, loc=(0, 0, 0), r=1.0, scale=(1, 1, 1), rot=(0, 0, 0), parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=40, ring_count=20)
        return self._fin(n, m, loc, rot, scale, parent)

    def cube(self, n, m, loc=(0, 0, 0), size=1.0, scale=(1, 1, 1), rot=(0, 0, 0), parent=None,
             bevel=0.0):
        bpy.ops.mesh.primitive_cube_add(size=size)
        return self._fin(n, m, loc, rot, scale, parent, smooth=bool(bevel), bevel=bevel)

    def cyl(self, n, m, loc=(0, 0, 0), r=0.5, depth=1.0, rot=(0, 0, 0), scale=(1, 1, 1),
            parent=None):
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=32)
        return self._fin(n, m, loc, rot, scale, parent)

    def cone(self, n, m, loc=(0, 0, 0), r=0.2, depth=1.0, rot=(0, 0, 0), parent=None):
        """Cono con la base en loc y la punta hacia +Z local (antes de rotar)."""
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=0, depth=depth, vertices=24)
        o = self._fin(n, m, loc, rot, (1, 1, 1), parent)
        # desplaza la geometría para que el origen sea la base
        for v in o.data.vertices:
            v.co.z += depth / 2
        return o

    def torus(self, n, m, loc=(0, 0, 0), major=1.0, minor=0.1, rot=(0, 0, 0), scale=(1, 1, 1),
              parent=None):
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                         major_segments=64, minor_segments=16)
        return self._fin(n, m, loc, rot, scale, parent)

    def pivot(self, n, loc=(0, 0, 0), parent=None):
        e = bpy.data.objects.new(n, None)
        e.location = loc
        e.parent = parent or self.root
        self.col.objects.link(e)
        return e


def humanoid(b, body_c, head_c, limb_c=None, eye_bg="#FFFFFF", pupil_c="#111111"):
    """Cuerpo redondo + cabeza + ojos + brazos/piernas con pivotes. Devuelve head_pivot."""
    body_m, head_m = mat(f"{b.name}_body", body_c), mat(f"{b.name}_head", head_c)
    limb_m = mat(f"{b.name}_limb", limb_c or head_c)
    eye_m, pupil_m = mat(f"{b.name}_eye", eye_bg, rough=0.2), mat(f"{b.name}_pupil", pupil_c, 0.1)

    b.sphere("body", body_m, (0, 0, 1.0), 0.8, (1, 0.85, 1.1))
    hp = b.pivot("head_pivot", (0, 0, 2.05))
    b.sphere("head", head_m, (0, 0, 0.55), 0.75, (1.05, 0.95, 0.9), parent=hp)
    for s, sx in (("L", -1), ("R", 1)):
        b.sphere(f"eye_{s}", eye_m, (sx * 0.3, -0.62, 0.62), 0.2, (1, 0.6, 1.1), parent=hp)
        b.sphere(f"pupil_{s}", pupil_m, (sx * 0.3, -0.72, 0.62), 0.1, (1, 0.5, 1.1), parent=hp)
        sh = b.pivot(f"shoulder_{s}", (sx * 0.85, 0, 1.55))
        b.cyl(f"arm_{s}", limb_m, (sx * 0.12, 0, -0.35), 0.13, 0.8, (0, math.radians(sx * 12), 0),
              parent=sh)
        b.sphere(f"hand_{s}", limb_m, (sx * 0.2, 0, -0.78), 0.17, parent=sh)
        hip = b.pivot(f"hip_{s}", (sx * 0.35, 0, 0.45))
        b.cyl(f"leg_{s}", limb_m, (0, 0, -0.2), 0.16, 0.5, parent=hip)
        b.sphere(f"foot_{s}", limb_m, (0, -0.1, -0.5), 0.22, (1, 1.4, 0.6), parent=hip)
    return hp


def build_claude(b):
    """Claude: terracota con destello radial (el 'sparkle' de Anthropic) sobre la cabeza."""
    orange = "#D97757"
    hp = humanoid(b, "#F0EEE6", orange, orange, pupil_c="#2b1a12")
    spark = mat("claude_spark", orange, 0.35)
    n = 12
    for i in range(n):
        a = i * math.tau / n  # ángulo en el plano XZ, medido desde +X
        length = 0.55 if i % 2 == 0 else 0.4
        # el cono apunta a +Z; rotar en Y por (pi/2 - a) lo orienta hacia el ángulo a
        b.cone(f"spark_{i}", spark, (math.cos(a) * 0.1, 0, 1.7 + math.sin(a) * 0.1), 0.07, length,
               (0, math.pi / 2 - a, 0), parent=hp)


def build_chatgpt(b):
    """ChatGPT: verde azulado, 'flor' hexagonal de anillos en el pecho y diadema."""
    green = "#10A37F"
    hp = humanoid(b, "#FFFFFF", green, green)
    m = mat("gpt_ring", green, 0.25, 0.2)
    for i in range(6):
        a = i * math.tau / 6
        b.torus(f"petal_{i}", m, (math.cos(a) * 0.14, -0.76, 1.15 + math.sin(a) * 0.14), 0.17,
                0.035, (math.pi / 2, 0, 0), scale=(1, 1, 1), parent=None).rotation_euler = (
            math.pi / 2, a, 0)
    b.torus("headband", m, (0, 0, 0.62), 0.78, 0.05, (0, math.pi / 2, 0), (1.05, 0.95, 1),
            parent=hp)


def build_gemini(b):
    """Gemini: azul + violeta con estrella de 4 puntas brillante flotando sobre la cabeza."""
    hp = humanoid(b, "#4285F4", "#9B72CB", "#4285F4", pupil_c="#1b1b4a")
    star = mat("gemini_star", "#8AB4F8", 0.2, emit=3.0)
    for i in range(4):  # 4 puntas a 90°
        a = i * math.pi / 2
        b.cone(f"star_{i}", star, (0, 0, 1.75), 0.14, 0.6, (0, a, 0), parent=hp)
    # cada punta mira a +Z rotada alrededor de Y => arriba, derecha, abajo, izquierda


def build_deepseek(b):
    """DeepSeek: ballena azul con chorro de agua."""
    blue, belly = mat("ds_body", "#4D6BFE", 0.35), mat("ds_belly", "#DDE6FF", 0.5)
    white, pupil = mat("ds_eye", "#FFFFFF", 0.2), mat("ds_pupil", "#0A0F3A", 0.1)
    water = mat("ds_water", "#9FB4FF", 0.1, emit=1.0)
    b.sphere("body", blue, (0, 0, 1.0), 1.0, (1.5, 0.9, 0.85))
    b.sphere("belly", belly, (0, -0.2, 0.7), 0.95, (1.4, 0.75, 0.5))
    tp = b.pivot("tail_pivot", (1.5, 0, 1.15))
    b.sphere("tail_stem", blue, (0.3, 0, 0.1), 0.4, (1.3, 0.7, 0.7), parent=tp)
    for s, sy in (("L", 1), ("R", -1)):
        b.sphere(f"fluke_{s}", blue, (0.85, sy * 0.3, 0.45), 0.4, (0.4, 0.15, 1.2),
                 rot=(math.radians(sy * 35), 0, 0), parent=tp)
        fp = b.pivot(f"fin_pivot_{s}", (-0.2, sy * 0.75, 0.8))
        b.sphere(f"fin_{s}", blue, (0, sy * 0.25, -0.25), 0.4, (0.7, 0.2, 1.0), parent=fp)
        b.sphere(f"eye_{s}", white, (-1.05, sy * 0.5, 1.25), 0.2, (1, 0.5, 1))
        b.sphere(f"pupil_{s}", pupil, (-1.13, sy * 0.53, 1.25), 0.1, (1, 0.5, 1))
    b.cone("spout", water, (-0.1, 0, 1.75), 0.14, 0.7)
    for i, dx in enumerate((-0.28, 0.28)):
        b.sphere(f"drop_{i}", water, (dx - 0.1, 0, 2.65), 0.08)


def build_grok(b):
    """Grok: negro mate, visera blanca, antena y el aro con barra diagonal de xAI."""
    hp = humanoid(b, "#17171A", "#0B0B0D", "#2A2A2F", eye_bg="#0B0B0D", pupil_c="#FFFFFF")
    white = mat("grok_white", "#FFFFFF", 0.3, emit=0.6)
    b.torus("chest_ring", white, (0, -0.76, 1.15), 0.28, 0.04, (math.pi / 2, 0, 0))
    b.cube("chest_slash", white, (0, -0.8, 1.15), 1.0, (0.05, 0.04, 0.75),
           (0, math.radians(35), 0))
    b.cube("visor", white, (0, -0.7, 0.64), 1.0, (0.95, 0.04, 0.05), parent=hp, bevel=0.01)
    b.cyl("antenna", white, (0, 0, 1.35), 0.025, 0.5, parent=hp)
    b.sphere("antenna_tip", white, (0, 0, 1.62), 0.07, parent=hp)


def build_mistral(b):
    """Mistral: 'M' de bloques con degradado amarillo→rojo, con ojos, brazos y piernas."""
    cols = ["#FFD800", "#FFAF00", "#FF8205", "#FA500F", "#E10500"]
    ms = [mat(f"mistral_{i}", c, 0.5) for i, c in enumerate(cols)]
    dark = mat("mistral_dark", "#1A1A1A", 0.3)
    s = 0.5
    pattern = ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"]
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch == "X":
                b.cube(f"block_{r}_{c}", ms[c], ((c - 2) * s, 0, 2.6 - r * s), s * 0.95, bevel=0.03)
    for side, sx in (("L", -1), ("R", 1)):
        sh = b.pivot(f"shoulder_{side}", (sx * 1.5, 0, 2.5))
        b.cube(f"arm_{side}", ms[0 if sx < 0 else 4], (0, 0, -0.45), s * 0.95, (1, 1, 1.8),
               parent=sh, bevel=0.03)
        hip = b.pivot(f"hip_{side}", (sx * 0.5, 0, 0.9))
        b.cube(f"leg_{side}", ms[1 if sx < 0 else 3], (0, 0, -0.35), s * 0.95, (1.1, 1.1, 2.2),
               parent=hip, bevel=0.03)
        b.cube(f"eye_{side}", dark, (sx * 0.5, -0.26, 2.1), 0.18, (1, 0.4, 1.4), bevel=0.02)


BUILDERS = {"claude": build_claude, "chatgpt": build_chatgpt, "gemini": build_gemini,
            "deepseek": build_deepseek, "grok": build_grok, "mistral": build_mistral}


def setup_stage():
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.fps = 1080, 1920, 30
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    w = bpy.data.worlds.new("world")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = rgba("#14141C")
    sc.world = w
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    sun.data.energy = 3.0
    sun.rotation_euler = (math.radians(50), 0, math.radians(30))
    sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.location, cam.rotation_euler = (0, -12, 2.6), (math.radians(87), 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam


def export_glb(name, col):
    bpy.ops.object.select_all(action="DESELECT")
    for o in col.all_objects:
        o.select_set(True)
    try:
        bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, f"{name}.glb"),
                                  export_format="GLB", use_selection=True)
    except Exception as e:
        print(f"[aviso] no se pudo exportar GLB de {name}: {e}")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    only = [a.lower() for a in argv[argv.index("--only") + 1:]] if "--only" in argv else None
    names = [n for n in BUILDERS if not only or n in only]

    bpy.ops.wm.read_factory_settings(use_empty=True)
    setup_stage()
    os.makedirs(OUT_DIR, exist_ok=True)
    for i, name in enumerate(names):
        b = B(name)
        BUILDERS[name](b)
        b.root.location = ((i - (len(names) - 1) / 2) * 5.0, 0, 0)
        export_glb(name, b.col)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "llm_characters.blend"))
    print("Listo:", ", ".join(names), "->", OUT_DIR)


if __name__ == "__main__":
    main()
