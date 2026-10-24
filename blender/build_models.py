"""Genera los robots 3D de los LLMs: Claude, ChatGPT, Gemini, DeepSeek, Grok y Mistral.

Uso (desde la raíz del repo):
    blender --background --python blender/build_models.py
    blender --background --python blender/build_models.py -- --only claude grok

Salida en ./output: llm_characters.blend (todos juntos) y un .glb por personaje.

Cada personaje es una Collection. Todos los objetos llevan el prefijo del personaje
("claude_head_pivot", "grok_shoulder_L"...). Partes pensadas para animar:
    <n>_root               mover / girar el personaje entero
    <n>_head_pivot         girar o inclinar la cabeza
    <n>_shoulder_L/R       brazos (rotar en X para saludar, en Y para abrirlos)
    <n>_hip_L/R            piernas
    <n>_eye_L/R            parpadeo: escalar en Z
    <n>_mouth              hablar: escalar en Z / X
DeepSeek además tiene <n>_tail_pivot y <n>_fin_pivot_L/R.
La escena queda en formato vertical 1080x1920 @ 30fps para TikTok.
"""
import math
import os
import sys

import bpy

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")

JOINT = "#3A3D44"
SCREEN = "#0B0F14"


# ----------------------------------------------------------------------------
# Materiales
# ----------------------------------------------------------------------------
def rgba(h):
    h = h.lstrip("#")
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4))
    return (r, g, b, 1.0)


def _new_mat(name, rough, metal, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    key = "Coat Weight" if "Coat Weight" in bsdf.inputs else "Clearcoat"
    if key in bsdf.inputs:
        bsdf.inputs[key].default_value = coat
    return m, bsdf


def mat(name, color, rough=0.4, metal=0.0, emit=0.0, coat=0.0):
    m, bsdf = _new_mat(name, rough, metal, coat)
    bsdf.inputs["Base Color"].default_value = rgba(color)
    if emit:
        key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
        bsdf.inputs[key].default_value = rgba(color)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m


def grad_mat(name, stops, rough=0.35, metal=0.3, coat=0.3, axis=2):
    """Degradado vertical (por objeto) con varios colores: stops = [(pos, '#hex'), ...]."""
    m, bsdf = _new_mat(name, rough, metal, coat)
    nt = m.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = stops[0][0], rgba(stops[0][1])
    els[1].position, els[1].color = stops[-1][0], rgba(stops[-1][1])
    for pos, col in stops[1:-1]:
        els.new(pos).color = rgba(col)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs[axis], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def as_mat(x, name, **kw):
    return x if isinstance(x, bpy.types.Material) else mat(name, x, **kw)


# ----------------------------------------------------------------------------
# Formas 2D (en el plano XZ, mirando a cámara) para logos
# ----------------------------------------------------------------------------
def sparkle_pts(n=11, r_in=0.09, lengths=(0.42, 0.33, 0.4, 0.3, 0.44, 0.35, 0.38, 0.31, 0.43, 0.34,
                                          0.39), width=0.42, rot=0.3):
    """Destello radial irregular, estilo logo de Claude."""
    pts = []
    step = math.tau / n
    for i in range(n):
        a = rot + i * step
        r_out = lengths[i % len(lengths)]
        d = step * width / 2
        pts += [(r_in * math.cos(a - d), r_in * math.sin(a - d)),
                (r_out * math.cos(a - d * 0.25), r_out * math.sin(a - d * 0.25)),
                (r_out * math.cos(a + d * 0.25), r_out * math.sin(a + d * 0.25)),
                (r_in * math.cos(a + d), r_in * math.sin(a + d)),
                (r_in * 0.8 * math.cos(a + step / 2), r_in * 0.8 * math.sin(a + step / 2))]
    return pts


def star4_pts(r=0.4, e=2.6, steps=96):
    """Estrella de 4 puntas con lados cóncavos, estilo logo de Gemini."""
    pts = []
    for i in range(steps):
        t = i * math.tau / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((r * math.copysign(abs(c) ** e, c), r * math.copysign(abs(s) ** e, s)))
    return pts


# ----------------------------------------------------------------------------
# Constructor
# ----------------------------------------------------------------------------
def _smooth(obj, angle=35):
    for p in obj.data.polygons:
        p.use_smooth = True
    if hasattr(obj.data, "use_auto_smooth"):  # Blender <= 4.0
        obj.data.use_auto_smooth = True
        obj.data.auto_smooth_angle = math.radians(angle)
    else:  # Blender 4.1+
        try:
            with bpy.context.temp_override(active_object=obj, selected_editable_objects=[obj],
                                           object=obj):
                bpy.ops.object.shade_smooth_by_angle(angle=math.radians(angle))
        except Exception:
            pass


class B:
    """Crea primitivas dentro de la collection del personaje, parentadas a un pivote."""

    def __init__(self, name):
        self.name = name
        self.col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(self.col)
        self.root = bpy.data.objects.new(f"{name}_root", None)
        self.col.objects.link(self.root)
        self.parts = {}

    def _link(self, o, n, parent):
        o.name = f"{self.name}_{n}"
        for c in list(o.users_collection):
            c.objects.unlink(o)
        self.col.objects.link(o)
        o.parent = parent or self.root
        self.parts[n] = o
        return o

    def _fin(self, n, m, loc, rot, scale, parent, smooth=True, bevel=0.0, bake_scale=False):
        o = bpy.context.active_object
        if bake_scale:  # escala en la malla => biselado uniforme
            for v in o.data.vertices:
                v.co = (v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])
            scale = (1, 1, 1)
        o.location, o.rotation_euler, o.scale = loc, rot, scale
        o.data.materials.append(m)
        if bevel:
            md = o.modifiers.new("bevel", "BEVEL")
            md.width, md.segments, md.limit_method = bevel, 5, "ANGLE"
            if hasattr(md, "harden_normals"):
                md.harden_normals = True
        if smooth:
            _smooth(o)
        return self._link(o, n, parent)

    def sphere(self, n, m, loc=(0, 0, 0), r=1.0, scale=(1, 1, 1), rot=(0, 0, 0), parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=48, ring_count=24)
        o = self._fin(n, m, loc, rot, scale, parent, smooth=False)
        for p in o.data.polygons:
            p.use_smooth = True
        return o

    def box(self, n, m, loc=(0, 0, 0), dims=(1, 1, 1), rot=(0, 0, 0), parent=None, bevel=0.0):
        """Caja con dimensiones reales dims=(x, y, z) y bisel uniforme."""
        bpy.ops.mesh.primitive_cube_add(size=1.0)
        return self._fin(n, m, loc, rot, dims, parent, smooth=bool(bevel), bevel=bevel,
                         bake_scale=True)

    def cyl(self, n, m, loc=(0, 0, 0), r=0.5, depth=1.0, rot=(0, 0, 0), scale=(1, 1, 1),
            parent=None, r2=None, bevel=0.0):
        if r2 is None:
            bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, vertices=40)
        else:
            bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=depth, vertices=40)
        return self._fin(n, m, loc, rot, scale, parent, bevel=bevel, bake_scale=True)

    def torus(self, n, m, loc=(0, 0, 0), major=1.0, minor=0.1, rot=(0, 0, 0), scale=(1, 1, 1),
              parent=None):
        bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor,
                                         major_segments=64, minor_segments=16)
        o = self._fin(n, m, loc, rot, scale, parent, smooth=False, bake_scale=True)
        for p in o.data.polygons:
            p.use_smooth = True
        return o

    def flat(self, n, m, pts, depth=0.08, loc=(0, 0, 0), rot=(0, 0, 0), parent=None, bevel=0.015):
        """Forma 2D (plano XZ) extruida en Y: para logos y emblemas."""
        verts = [(0, 0, 0)] + [(x, 0, z) for x, z in pts]
        k = len(pts)
        faces = [(0, i + 1, (i + 1) % k + 1) for i in range(k)]
        me = bpy.data.meshes.new(n)
        me.from_pydata(verts, [], faces)
        me.update()
        me.materials.append(m)
        o = bpy.data.objects.new(n, me)
        bpy.context.scene.collection.objects.link(o)
        o.location, o.rotation_euler = loc, rot
        sd = o.modifiers.new("solid", "SOLIDIFY")
        sd.thickness, sd.offset = depth, 0
        if bevel:
            bv = o.modifiers.new("bevel", "BEVEL")
            bv.width, bv.segments, bv.limit_method = bevel, 3, "ANGLE"
        return self._link(o, n, parent)

    def pivot(self, n, loc=(0, 0, 0), rot=(0, 0, 0), parent=None):
        e = bpy.data.objects.new(n, None)
        e.location, e.rotation_euler = loc, rot
        e.empty_display_size = 0.2
        bpy.context.scene.collection.objects.link(e)
        return self._link(e, n, parent)


# ----------------------------------------------------------------------------
# Robot base (estilo chibi): cabeza grande con pantalla, torso compacto,
# brazos con codo, botas. Medidas: suelo z=0, cabeza hasta z≈3.
# ----------------------------------------------------------------------------
CHEST_Y, CHEST_Z = -0.57, 1.08  # dónde van los emblemas del pecho
HEAD_TOP = 1.24  # altura local de la parte superior de la cabeza (sobre head_pivot)


def robot(b, body, head, limb, accent, eye_c="#00E5FF", screen_c=SCREEN, metal=0.5,
          head_bevel=0.22, body_bevel=0.2, eyes="pill", antenna=True, ears=True):
    """Construye el robot base. Colores en hex o materiales ya creados."""
    n = b.name
    body_m = as_mat(body, f"{n}_body", rough=0.3, metal=metal, coat=0.4)
    head_m = as_mat(head, f"{n}_head", rough=0.3, metal=metal, coat=0.4)
    limb_m = as_mat(limb, f"{n}_limb", rough=0.35, metal=metal, coat=0.3)
    acc_m = as_mat(accent, f"{n}_accent", rough=0.3, metal=metal, coat=0.3)
    joint_m = mat(f"{n}_joint", JOINT, 0.35, 0.85)
    screen_m = mat(f"{n}_screen", screen_c, 0.08, coat=1.0)
    led_m = mat(f"{n}_led", eye_c, 0.2, emit=8.0)
    glint_m = mat(f"{n}_glint", "#FFFFFF", 0.1, emit=12.0)

    # torso + pelvis + placa del pecho
    b.box("body", body_m, (0, 0, 1.05), (1.3, 1.0, 1.1), bevel=body_bevel)
    b.box("pelvis", joint_m, (0, 0, 0.52), (0.9, 0.72, 0.22), bevel=0.08)
    b.box("chest_plate", acc_m, (0, -0.5, CHEST_Z), (0.82, 0.08, 0.6), bevel=0.04)
    b.cyl("neck", joint_m, (0, 0, 1.66), 0.2, 0.16)
    b.torus("neck_ring", acc_m, (0, 0, 1.62), 0.26, 0.045)

    # cabeza
    hp = b.pivot("head_pivot", (0, 0, 1.72))
    b.box("head", head_m, (0, 0, 0.62), (1.7, 1.3, 1.24), parent=hp, bevel=head_bevel)
    b.box("screen", screen_m, (0, -0.64, 0.64), (1.42, 0.06, 0.92), parent=hp,
          bevel=min(0.14, head_bevel * 0.7))
    if eyes == "pill":
        for s, sx in (("L", -1), ("R", 1)):
            b.sphere(f"eye_{s}", led_m, (sx * 0.32, -0.68, 0.72), 1.0, (0.13, 0.04, 0.19), parent=hp)
            b.sphere(f"glint_{s}", glint_m, (sx * 0.32 + 0.05, -0.715, 0.8), 0.035, parent=hp)
    else:  # visor de una sola ranura
        b.box("eye_L", led_m, (0, -0.68, 0.72), (1.0, 0.04, 0.14), parent=hp, bevel=0.03)
        b.pivot("eye_R", (0, 0, 0.72), parent=hp)  # para que existan ambos nombres
    b.box("mouth", led_m, (0, -0.68, 0.4), (0.26, 0.03, 0.05), parent=hp, bevel=0.02)
    if ears:
        for s, sx in (("L", -1), ("R", 1)):
            b.cyl(f"ear_{s}", acc_m, (sx * 0.88, 0, 0.64), 0.24, 0.12, (0, math.pi / 2, 0),
                  parent=hp, bevel=0.03)
            b.cyl(f"ear_cap_{s}", joint_m, (sx * 0.96, 0, 0.64), 0.12, 0.08, (0, math.pi / 2, 0),
                  parent=hp, bevel=0.02)
    if antenna:
        b.cyl("antenna", joint_m, (0, 0, HEAD_TOP + 0.14), 0.03, 0.3, parent=hp)
        b.sphere("antenna_tip", led_m, (0, 0, HEAD_TOP + 0.32), 0.07, parent=hp)

    # brazos (ligeramente abiertos) y piernas
    for s, sx in (("L", -1), ("R", 1)):
        sh = b.pivot(f"shoulder_{s}", (sx * 0.8, 0, 1.4), (0, -sx * math.radians(10), 0))
        b.sphere(f"shoulder_joint_{s}", joint_m, (0, 0, 0), 0.19, parent=sh)
        b.cyl(f"upper_arm_{s}", limb_m, (0, 0, -0.24), 0.1, 0.36, parent=sh)
        b.sphere(f"elbow_{s}", joint_m, (0, 0, -0.45), 0.12, parent=sh)
        b.cyl(f"forearm_{s}", limb_m, (0, 0, -0.66), 0.14, 0.34, r2=0.12, parent=sh, bevel=0.03)
        b.sphere(f"hand_{s}", joint_m, (0, 0, -0.9), 0.16, (1, 0.8, 1.1), parent=sh)
        b.sphere(f"thumb_{s}", joint_m, (-sx * 0.12, -0.06, -0.86), 0.06, parent=sh)

        hip = b.pivot(f"hip_{s}", (sx * 0.3, 0, 0.5))
        b.cyl(f"leg_{s}", joint_m, (0, 0, -0.14), 0.12, 0.28, parent=hip)
        b.box(f"foot_{s}", limb_m, (0, -0.08, -0.39), (0.42, 0.62, 0.22), parent=hip, bevel=0.09)
    return hp


# ----------------------------------------------------------------------------
# Personajes
# ----------------------------------------------------------------------------
def build_claude(b):
    """Claude: crema + terracota, destello irregular flotando sobre la antena y en el pecho."""
    orange = "#D97757"
    hp = robot(b, "#F0EEE6", orange, orange, "#E9E4D8", eye_c="#FFD9C2", screen_c="#1E1410")
    spark = mat("claude_spark", orange, 0.3, 0.2, coat=0.5)
    b.flat("spark", spark, sparkle_pts(), 0.1, (0, 0, HEAD_TOP + 0.75), parent=hp)
    b.flat("chest_spark", spark, sparkle_pts(lengths=(0.24, 0.19, 0.23, 0.17, 0.25, 0.2, 0.22, 0.18,
                                                      0.24, 0.19, 0.22), r_in=0.05),
           0.05, (0, CHEST_Y, CHEST_Z))


def build_chatgpt(b):
    """ChatGPT: blanco + verde OpenAI, 'flor' de 6 eslabones en el pecho, orejas de auricular."""
    green = "#10A37F"
    robot(b, "#F7F7F8", green, green, "#202123", eye_c="#B8FFE8", screen_c="#0A1F19")
    knot = mat("gpt_knot", "#FFFFFF", 0.25, 0.1, emit=0.0)
    for i in range(6):
        a = i * math.tau / 6
        b.torus(f"petal_{i}", knot, (math.cos(a) * 0.1, CHEST_Y, CHEST_Z + math.sin(a) * 0.1),
                0.1, 0.022, (math.pi / 2, -a, 0), scale=(1.7, 1.0, 1.0))


def build_gemini(b):
    """Gemini: degradado azul→violeta→rosa y estrella de 4 puntas luminosa."""
    stops = [(0.0, "#1C5BD8"), (0.5, "#4285F4"), (0.8, "#9B72CB"), (1.0, "#D96570")]
    g_body = grad_mat("gemini_body", stops)
    g_head = grad_mat("gemini_head", [(0.0, "#4285F4"), (0.6, "#9B72CB"), (1.0, "#D96570")])
    hp = robot(b, g_body, g_head, "#4285F4", "#E8EEFF", eye_c="#FFFFFF", screen_c="#0B0B2A")
    star = grad_mat("gemini_star", [(0.0, "#4285F4"), (0.5, "#9B72CB"), (1.0, "#D96570")], 0.2,
                    0.2, axis=0)
    glow = mat("gemini_glow", "#C9D8FF", 0.2, emit=4.0)
    b.flat("star", star, star4_pts(0.42), 0.12, (0, 0, HEAD_TOP + 0.8), parent=hp, bevel=0.02)
    b.flat("star_glow", glow, star4_pts(0.15), 0.14, (0, 0, HEAD_TOP + 0.8), parent=hp)
    b.flat("chest_star", star, star4_pts(0.26), 0.06, (0, CHEST_Y, CHEST_Z))


def build_deepseek(b):
    """DeepSeek: ballena robot azul con visor LED, costuras de panel y chorro luminoso."""
    blue = grad_mat("ds_body", [(0.0, "#C9D6FF"), (0.4, "#4D6BFE"), (1.0, "#2B44C9")], 0.3, 0.5)
    fin_m = mat("ds_fin", "#3C58E8", 0.3, 0.5, coat=0.4)
    joint = mat("ds_joint", JOINT, 0.35, 0.85)
    screen = mat("ds_screen", "#05081F", 0.08, coat=1.0)
    led = mat("ds_led", "#9FE0FF", 0.2, emit=8.0)
    glint = mat("ds_glint", "#FFFFFF", 0.1, emit=12.0)
    water = mat("ds_water", "#8FD8FF", 0.1, emit=3.0)

    b.sphere("body", blue, (0, 0, 1.0), 1.0, (1.5, 0.9, 0.85))
    # costuras de panel
    for i, x in enumerate((-0.35, 0.55)):
        k = math.sqrt(1 - (x / 1.5) ** 2)
        b.torus(f"seam_{i}", joint, (x, 0, 1.0), 1.0, 0.025, (0, math.pi / 2, 0),
                scale=(0.85 * k + 0.01, 0.9 * k + 0.01, 1))
    for i in range(4):  # remaches en el lomo
        x = -0.65 + i * 0.4
        z = 1.0 + 0.85 * math.sqrt(1 - (x / 1.5) ** 2)
        b.sphere(f"rivet_{i}", joint, (x, 0, z - 0.02), 0.055)

    # cola horizontal
    tp = b.pivot("tail_pivot", (1.35, 0, 1.1), (0, math.radians(-20), 0))
    b.cyl("tail_stem", fin_m, (0.35, 0, 0), 0.42, 0.8, (0, math.pi / 2, 0), r2=0.2, parent=tp)
    b.sphere("tail_joint", joint, (0.75, 0, 0), 0.14, parent=tp)
    for s, sy in (("L", 1), ("R", -1)):
        b.sphere(f"fluke_{s}", fin_m, (1.0, sy * 0.38, 0.02), 0.45, (0.6, 0.95, 0.14),
                 (0, 0, math.radians(sy * -30)), parent=tp)

    # aletas laterales y visor a ambos lados (el lado -Y mira a cámara)
    for s, sy in (("L", 1), ("R", -1)):
        fp = b.pivot(f"fin_pivot_{s}", (-0.35, sy * 0.78, 0.65))
        b.sphere(f"fin_{s}", fin_m, (0.1, sy * 0.18, -0.12), 0.38, (0.75, 0.55, 0.14),
                 (math.radians(sy * 60), math.radians(-20), 0), parent=fp)
        b.box(f"screen_{s}", screen, (-0.85, sy * 0.66, 1.18), (0.72, 0.14, 0.4), bevel=0.06,
              rot=(0, 0, math.radians(sy * 22)))
        b.sphere(f"eye_{s}", led, (-0.88, sy * 0.745, 1.2), 1.0, (0.1, 0.04, 0.14),
                 (0, 0, math.radians(sy * 22)))
        b.sphere(f"glint_{s}", glint, (-0.85, sy * 0.775, 1.26), 0.03)
    b.box("mouth", led, (-1.12, -0.58, 0.88), (0.3, 0.03, 0.05), bevel=0.02,
          rot=(0, math.radians(-12), math.radians(-40)))

    # chorro: tubo + gotas en abanico
    b.cyl("spout_pipe", joint, (-0.2, 0, 1.88), 0.09, 0.2)
    b.sphere("antenna_tip", led, (-0.2, 0, 2.02), 0.09)
    for i, (dx, dz, r) in enumerate(((-0.35, 2.35, 0.08), (0.0, 2.5, 0.1), (-0.05, 2.3, 0.07),
                                     (0.25, 2.32, 0.08))):
        b.sphere(f"drop_{i}", water, (dx - 0.2, 0, dz), r, (1, 1, 1.3))


def build_grok(b):
    """Grok: negro brillante, anguloso, visor de una ranura y logo de xAI en el pecho."""
    hp = robot(b, "#141417", "#141417", "#26262B", "#2E2E34", eye_c="#FFFFFF", screen_c="#000000",
               metal=0.35, head_bevel=0.06, body_bevel=0.06, eyes="visor", antenna=False)
    white = mat("grok_white", "#FFFFFF", 0.25, emit=1.5)
    dark = mat("grok_pad", "#26262B", 0.3, 0.8, coat=0.6)
    b.torus("chest_ring", white, (0, CHEST_Y, CHEST_Z), 0.2, 0.03, (math.pi / 2, 0, 0))
    b.box("chest_slash", white, (0, CHEST_Y - 0.01, CHEST_Z), (0.05, 0.04, 0.62),
          (0, math.radians(40), 0), bevel=0.01)
    # antena en forma de aleta y hombreras angulosas
    b.box("fin", dark, (0, 0.1, HEAD_TOP + 0.12), (0.08, 0.7, 0.3), (math.radians(-15), 0, 0),
          parent=hp, bevel=0.02)
    for s, sx in (("L", -1), ("R", 1)):
        b.box(f"pad_{s}", dark, (sx * 0.05, 0, 0.1), (0.42, 0.5, 0.18),
              (0, sx * math.radians(18), 0), parent=b.parts[f"shoulder_{s}"], bevel=0.03)


def build_mistral(b):
    """Mistral: robot pixel; cuerpo en forma de 'M' con degradado amarillo→rojo y cabeza encima."""
    cols = ["#FFD800", "#FFAF00", "#FF8205", "#FA500F", "#E10500"]
    ms = [mat(f"mistral_{i}", c, 0.35, 0.3, coat=0.4) for i, c in enumerate(cols)]
    joint = mat("mistral_joint", JOINT, 0.35, 0.85)
    screen = mat("mistral_screen", SCREEN, 0.08, coat=1.0)
    led = mat("mistral_led", "#FFE45C", 0.2, emit=8.0)
    s = 0.5
    pattern = ["X...X", "XX.XX", "X.X.X", "X...X", "X...X"]
    for r, row in enumerate(pattern):
        for c, ch in enumerate(row):
            if ch == "X":
                b.box(f"block_{r}_{c}", ms[c], ((c - 2) * s, 0, 2.6 - r * s), (s * 0.96,) * 3,
                      bevel=0.04)

    hp = b.pivot("head_pivot", (0, 0, 2.38))
    b.box("head", ms[2], (0, 0, 0.42), (1.0, 0.8, 0.8), parent=hp, bevel=0.06)
    b.box("screen", screen, (0, -0.4, 0.44), (0.8, 0.05, 0.56), parent=hp, bevel=0.03)
    for side, sx in (("L", -1), ("R", 1)):
        b.box(f"eye_{side}", led, (sx * 0.17, -0.43, 0.5), (0.12, 0.03, 0.16), parent=hp)
    b.box("mouth", led, (0, -0.43, 0.3), (0.2, 0.03, 0.05), parent=hp)
    b.cyl("antenna", joint, (0, 0, 0.92), 0.025, 0.25, parent=hp)
    b.box("antenna_tip", led, (0, 0, 1.08), (0.12, 0.12, 0.12), parent=hp)

    for side, sx in (("L", -1), ("R", 1)):
        c_arm = ms[0] if sx < 0 else ms[4]
        sh = b.pivot(f"shoulder_{side}", (sx * 1.38, 0, 2.5))
        b.box(f"arm_top_{side}", c_arm, (sx * 0.08, 0, -0.1), (0.36, 0.36, 0.36), parent=sh,
              bevel=0.03)
        b.box(f"arm_bot_{side}", c_arm, (sx * 0.08, 0, -0.48), (0.36, 0.36, 0.36), parent=sh,
              bevel=0.03)
        b.box(f"hand_{side}", joint, (sx * 0.08, 0, -0.82), (0.3, 0.3, 0.26), parent=sh, bevel=0.04)
        hip = b.pivot(f"hip_{side}", (sx * 1.0, 0, 0.36))
        b.box(f"leg_{side}", joint, (0, 0, -0.1), (0.26, 0.26, 0.16), parent=hip)
        b.box(f"foot_{side}", joint, (0, -0.06, -0.27), (0.46, 0.6, 0.18), parent=hip, bevel=0.05)


BUILDERS = {"claude": build_claude, "chatgpt": build_chatgpt, "gemini": build_gemini,
            "deepseek": build_deepseek, "grok": build_grok, "mistral": build_mistral}


# ----------------------------------------------------------------------------
# Escena
# ----------------------------------------------------------------------------
def area_light(name, energy, loc, rot, size, color="#FFFFFF"):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size, ld.color = energy, size, rgba(color)[:3]
    o = bpy.data.objects.new(name, ld)
    o.location, o.rotation_euler = loc, rot
    bpy.context.scene.collection.objects.link(o)


def setup_stage():
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y, sc.render.fps = 1080, 1920, 30
    try:
        sc.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        sc.render.engine = "BLENDER_EEVEE"
    if hasattr(sc.eevee, "use_bloom"):
        sc.eevee.use_bloom = True
    w = bpy.data.worlds.new("world")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = rgba("#14141C")
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    sc.world = w

    # iluminación de 3 puntos: principal cálida, relleno frío, contraluz
    area_light("key", 2500, (-6, -8, 7), (math.radians(55), 0, math.radians(-35)), 6, "#FFF1E0")
    area_light("fill", 900, (8, -7, 3), (math.radians(75), 0, math.radians(50)), 8, "#D8E4FF")
    area_light("rim", 2000, (0, 8, 6), (math.radians(-55), 0, 0), 10)

    floor = bpy.data.meshes.new("floor")
    floor.from_pydata([(-60, -30, 0), (60, -30, 0), (60, 30, 0), (-60, 30, 0)], [], [(0, 1, 2, 3)])
    fo = bpy.data.objects.new("floor", floor)
    floor.materials.append(mat("floor", "#1C1C26", 0.35))
    sc.collection.objects.link(fo)

    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.location, cam.rotation_euler = (0, -12, 2.2), (math.radians(86), 0, 0)
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
        b.root.location = ((i - (len(names) - 1) / 2) * 4.2, 0, 0)
        export_glb(name, b.col)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "llm_characters.blend"))
    print("Listo:", ", ".join(names), "->", OUT_DIR)


if __name__ == "__main__":
    main()
