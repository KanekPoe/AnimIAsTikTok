"""Arma y anima la escena de un episodio a partir de su timeline.json.

Uso (desde la raíz del repo):
    blender -b --python blender/scene.py -- output/ep01_control_mundial            # arma y guarda scene.blend
    blender -b --python blender/scene.py -- output/ep01_control_mundial --still 120 # prueba un frame
    blender -b --python blender/scene.py -- output/ep01_control_mundial --render    # renderiza todo
Opciones: --percent 67 (resolución), --frames 1:300, --portraits (tarjetas del cierre)

Requiere antes: pipeline/voices.py (timeline.json) y pipeline/holo.py (imágenes del holograma).
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_models as bm  # noqa: E402

ORDER = ["claude", "deepseek", "mistral", "chatgpt", "grok", "gemini"]
XS = [-7.0, -4.3, -1.6, 1.6, 4.3, 7.0]
YS = [1.2, 2.4, 3.2, 3.2, 2.4, 1.2]
FAN = 0.12               # cuánto se "abren" los robots hacia el público
PEDESTAL_TOP = 1.42
GLOBE_REST = Vector((0, 0, 2.05))
UN_BLUE = "#4B92DB"

rng = random.Random(7)


# ----------------------------------------------------------------------------
# Utilidades de animación
# ----------------------------------------------------------------------------
def fcurves(id_data):
    act = id_data.animation_data.action
    try:
        return list(act.fcurves)
    except (AttributeError, TypeError):  # Blender 5: acciones por capas
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    out += list(bag.fcurves)
        return out


def kf(obj, attr, frame, value, interp=None):
    setattr(obj, attr, value)
    obj.keyframe_insert(attr, frame=frame)
    if interp:
        for fc in fcurves(obj):
            if fc.data_path == attr:
                for kp in fc.keyframe_points:
                    if abs(kp.co.x - frame) < 0.01:
                        kp.interpolation = interp


def set_interp(id_data, interp, path=None):
    if not id_data.animation_data or not id_data.animation_data.action:
        return
    for fc in fcurves(id_data):
        if path is None or fc.data_path == path:
            for kp in fc.keyframe_points:
                kp.interpolation = interp


def pop_in(obj, f, s=1.0):
    kf(obj, "scale", 1, (0, 0, 0), "CONSTANT")
    kf(obj, "scale", f, (0.01 * s,) * 3)
    kf(obj, "scale", f + 3, (1.15 * s,) * 3)
    kf(obj, "scale", f + 6, (s,) * 3)


def pop_out(obj, f, s=1.0):
    kf(obj, "scale", f - 1, (s,) * 3, "CONSTANT")
    kf(obj, "scale", f, (0, 0, 0), "CONSTANT")


def frame_of(t, fps):
    return int(round(t * fps)) + 1


def face_angle(d):
    """Ángulo Z para que el frente (-Y local) mire en la dirección d."""
    return math.atan2(d.x, -d.y)


def wrap(a):
    return (a + math.pi) % math.tau - math.pi


# ----------------------------------------------------------------------------
# Materiales especiales
# ----------------------------------------------------------------------------
def transparent_setup(m):
    if hasattr(m, "surface_render_method"):
        m.surface_render_method = "BLENDED"
    if hasattr(m, "blend_method"):
        try:
            m.blend_method = "BLEND"
        except TypeError:
            pass
    if hasattr(m, "shadow_method"):
        m.shadow_method = "NONE"


def image_mat(name, path, strength=1.6):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(path)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Strength"].default_value = strength
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    nt.links.new(tex.outputs["Alpha"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    transparent_setup(m)
    return m


def globe_mat():
    m = bpy.data.materials.new("globe")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 2.6
    noise.inputs["Detail"].default_value = 8.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = 0.52, bm.rgba("#1A4FA8")
    els[1].position, els[1].color = 0.55, bm.rgba("#3FA35B")
    els.new(0.68).color = bm.rgba("#8A9A5B")
    nt.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    key = "Emission Color" if "Emission Color" in bsdf.inputs else "Emission"
    nt.links.new(ramp.outputs["Color"], bsdf.inputs[key])
    bsdf.inputs["Emission Strength"].default_value = 0.6
    bsdf.inputs["Roughness"].default_value = 0.45
    return m


def atmosphere_mat():
    m = bpy.data.materials.new("atmosphere")
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.45
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = bm.rgba("#7FD3FF")
    em.inputs["Strength"].default_value = 4.0
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
    nt.links.new(tr.outputs[0], mix.inputs[1])
    nt.links.new(em.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    transparent_setup(m)
    return m


def text_obj(b, name, body, size, m, loc, rot=(math.pi / 2, 0, 0), parent=None):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.align_x, cu.align_y = "CENTER", "CENTER"
    cu.extrude = size * 0.06
    o = bpy.data.objects.new(name, cu)
    o.data.materials.append(m)
    bpy.context.scene.collection.objects.link(o)
    o.location, o.rotation_euler = loc, rot
    return b._link(o, name, parent)


def arc_block(b, n, m, r_in, r_out, a0, a1, z0, z1, segs=48):
    """Bloque curvo (sector de anillo) para gradas y muro."""
    bmsh = bmesh.new()
    verts = []
    for i in range(segs + 1):
        a = math.radians(a0 + (a1 - a0) * i / segs)
        for r in (r_in, r_out):
            for z in (z0, z1):
                verts.append(bmsh.verts.new((r * math.cos(a), r * math.sin(a), z)))
    for i in range(segs):
        q = [verts[i * 4 + k] for k in range(4)]
        w = [verts[(i + 1) * 4 + k] for k in range(4)]
        for a, c in ((0, 1), (1, 3), (3, 2), (2, 0)):
            bmsh.faces.new((q[a], q[c], w[c], w[a]))
    bmsh.faces.new([verts[k] for k in (0, 1, 3, 2)])
    bmsh.faces.new([verts[segs * 4 + k] for k in (0, 2, 3, 1)])
    bmesh.ops.recalc_face_normals(bmsh, faces=bmsh.faces)
    me = bpy.data.meshes.new(n)
    bmsh.to_mesh(me)
    bmsh.free()
    me.materials.append(m)
    o = bpy.data.objects.new(n, me)
    bpy.context.scene.collection.objects.link(o)
    return b._link(o, n, None)


# ----------------------------------------------------------------------------
# Escenario
# ----------------------------------------------------------------------------
def build_hall():
    hb = bm.B("hall")
    floor_m = bm.mat("hall_floor", "#090A10", 0.42, 0.2, coat=0.1)
    fb = floor_m.node_tree.nodes["Principled BSDF"]
    for key in ("Specular IOR Level", "Specular"):
        if key in fb.inputs:
            fb.inputs[key].default_value = 0.15
            break
    wall_m = bm.mat("hall_wall", "#0B1428", 0.6)
    tier_m = bm.mat("hall_tier", "#141B2E", 0.5, 0.2)
    glow_m = bm.mat("hall_glow", UN_BLUE, 0.3, emit=3.0)
    dim_m = bm.mat("hall_dim", "#2A4D7A", 0.3, emit=1.2)

    hb.cyl("floor", floor_m, (0, 0, -0.01), 30, 0.02)
    hb.torus("floor_ring", glow_m, (0, 0, 0.01), 1.55, 0.03)
    hb.torus("floor_ring2", dim_m, (0, 0, 0.01), 5.6, 0.02)
    arc_block(hb, "wall", wall_m, 13.0, 13.4, 12, 168, 0, 10)
    for i, r in enumerate((8.8, 9.8, 10.8)):
        z = 0.5 * (i + 1)
        arc_block(hb, f"tier_{i}", tier_m, r, r + 1.0, 18, 162, 0, z)
        arc_block(hb, f"tier_edge_{i}", dim_m, r - 0.02, r + 0.03, 18, 162, z - 0.05, z)
    for k in range(17):  # franjas de luz en el muro
        a = math.radians(20 + k * 140 / 16)
        hb.box(f"strip_{k}", glow_m if k % 4 == 0 else dim_m,
               (12.95 * math.cos(a), 12.95 * math.sin(a), 5.0), (0.08, 0.08, 9.0),
               rot=(0, 0, a))
    banner_m = bm.mat("hall_banner", "#CFE3FF", 0.3, emit=2.5)
    text_obj(hb, "banner", "ASAMBLEA MUNDIAL", 0.75, banner_m, (0, 11.4, 9.4))

    # pedestal
    ped_m = bm.mat("ped_metal", "#1B1F2A", 0.25, 0.9, coat=0.5)
    ring_m = bm.mat("ped_ring", UN_BLUE, 0.3, emit=4.0)
    hb.cyl("ped_base", ped_m, (0, 0, 0.1), 1.0, 0.2, bevel=0.04)
    hb.cyl("ped_column", ped_m, (0, 0, 0.75), 0.38, 1.1, r2=0.28, bevel=0.03)
    hb.cyl("ped_top", ped_m, (0, 0, 1.36), 0.68, 0.12, bevel=0.03)
    hb.torus("ped_glow", ring_m, (0, 0, PEDESTAL_TOP), 0.64, 0.035)
    return hb, ring_m


def build_lights(sc):
    def area(name, energy, loc, target, size, color="#FFFFFF"):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy, ld.size, ld.color = energy, size, bm.rgba(color)[:3]
        ld.shape = "DISK"
        o = bpy.data.objects.new(name, ld)
        o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(o)
        return o

    area("key", 3200, (-7, -9, 9), (0, 2, 1), 7, "#FFF1E0")
    area("fill", 1300, (9, -8, 4), (0, 2, 1.5), 9, "#D8E4FF")
    area("rim_L", 1800, (-9, 9, 6), (-2, 2, 1.5), 6, UN_BLUE)
    area("rim_R", 1800, (9, 9, 6), (2, 2, 1.5), 6, "#9B72CB")
    area("top", 900, (0, 1, 11), (0, 1, 0), 10)
    fl = bpy.data.lights.new("flash", "POINT")
    fl.energy, fl.color, fl.shadow_soft_size = 0, (0.6, 0.85, 1.0), 0.5
    fo = bpy.data.objects.new("flash", fl)
    fo.location = (0, 0, 2.2)
    sc.collection.objects.link(fo)
    return fo


def setup_render(sc, percent):
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            sc.render.engine = eng
            break
        except TypeError:
            continue
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.resolution_percentage = percent
    sc.render.fps = 30
    ee = sc.eevee
    for attr, val in (("use_bloom", True), ("bloom_intensity", 0.06), ("bloom_threshold", 0.9),
                      ("taa_render_samples", 8), ("use_gtao", True), ("use_soft_shadows", True)):
        if hasattr(ee, attr):
            setattr(ee, attr, val)
    try:
        sc.view_settings.view_transform = "AgX"
    except TypeError:
        sc.view_settings.view_transform = "Filmic"
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    w = bpy.data.worlds.new("world")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = bm.rgba("#05070D")
    w.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    sc.world = w


# ----------------------------------------------------------------------------
# Escena principal
# ----------------------------------------------------------------------------
class Stage:
    def __init__(self, out_dir, percent=100):
        self.out = out_dir
        with open(os.path.join(out_dir, "timeline.json")) as f:
            self.tl = json.load(f)
        self.fps = self.tl["fps"]
        self.blocks = self.tl["blocks"]
        self.turns = [bl for bl in self.blocks if bl["type"] == "turn"]
        self.hook = self.blocks[0]
        self.outro = self.blocks[-1]
        self.end_frame = frame_of(self.outro["start"], self.fps) - 1

        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.sc = bpy.context.scene
        setup_render(self.sc, percent)
        self.sc.frame_start, self.sc.frame_end = 1, self.end_frame
        self.hall, self.ped_ring = build_hall()
        self.flash = build_lights(self.sc)
        self.props = bm.B("props")
        self.build_robots()
        self.build_globe()
        self.build_holo()
        self.build_props()
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
        cam.data.sensor_fit = "VERTICAL"
        cam.data.sensor_height = 36
        self.sc.collection.objects.link(cam)
        self.sc.camera = self.cam = cam

    # --- construcción ------------------------------------------------------
    def build_robots(self):
        self.r = {}
        for i, n in enumerate(ORDER):
            b = bm.B(n)
            bm.BUILDERS[n](b)
            p = Vector((XS[i], YS[i], 0))
            f = Vector((XS[i] * FAN, -1, 0)).normalized()
            theta = face_angle(f)
            if n == "deepseek":
                theta += math.radians(35)  # 3/4: se ve la cara y el visor lateral
            b.root.location = p
            b.root.rotation_euler = (0, 0, theta)
            self.r[n] = {"b": b, "p": p, "f": f, "theta": theta, "root": b.root,
                         "head": b.parts.get("head_pivot")}
        bpy.context.view_layer.update()
        for n, d in self.r.items():
            ho = d["b"].parts.get("head") or d["b"].parts["body"]
            cs = [ho.matrix_world @ Vector(c) for c in ho.bound_box]
            d["head_z"] = sum(c.z for c in cs) / 8
            d["base_rot"] = {k: tuple(o.rotation_euler) for k, o in d["b"].parts.items()}
            # el globo flota al lado interior del robot (no le tapa la cara)
            f, p = d["f"], d["p"]
            side = Vector((-f.y, f.x, 0)) * (1 if p.x < 0 else -1)
            gz = {"deepseek": 1.4, "mistral": 1.5, "gemini": 1.45}.get(n, 1.35)
            dist = 1.6 if n == "deepseek" else 1.15
            d["offer"] = p + f * dist + side * (0.6 if n == "deepseek" else 0.95) + Vector((0, 0, gz))
            d["side"] = side
            if n == "deepseek":  # su "cara" es el visor lateral que mira al público
                d["face"] = d["root"].matrix_world @ Vector((-0.85, -0.55, 1.15))

    def build_globe(self):
        pb = self.props
        self.globe = pb.pivot("globe_ctrl", tuple(GLOBE_REST))
        self.globe_spin = pb.sphere("globe", globe_mat(), (0, 0, 0), 0.55, parent=self.globe)
        pb.sphere("globe_atmo", atmosphere_mat(), (0, 0, 0), 0.62, parent=self.globe)
        spark_m = bm.mat("spark", "#9FE0FF", 0.2, emit=12.0)
        self.sparks = [pb.sphere(f"spark_{i}", spark_m, (0, 0, 0), 0.06, parent=None)
                       for i in range(26)]

    def build_holo(self):
        pb = self.props
        self.holo = pb.pivot("holo")
        self.holo_imgs = {}
        hdir = os.path.join(self.out, "holo")
        for fn in sorted(os.listdir(hdir)):
            k = fn[:-4]
            bpy.ops.mesh.primitive_plane_add(size=1)
            o = bpy.context.active_object
            for v in o.data.vertices:  # plano vertical 3.2 x 2.0 mirando a -Y
                v.co = Vector((v.co.x * 3.2, 0, v.co.y * 2.0))
            o.data.materials.append(image_mat(f"holo_{k}", os.path.join(hdir, fn)))
            pb._link(o, f"holo_{k}", self.holo)
            o.location = (0, 0, 0)
            kf(o, "scale", 1, (0, 0, 0), "CONSTANT")
            self.holo_imgs[k] = o
        kf(self.holo, "scale", 1, (0, 0, 0), "CONSTANT")

    def build_props(self):
        pb = self.props
        dark = bm.mat("prop_dark", "#22252E", 0.35, 0.6)
        red = bm.mat("prop_red", "#FF2E2E", 0.25, emit=2.5)
        white = bm.mat("prop_white", "#F4F4F4", 0.4)
        white_e = bm.mat("prop_white_e", "#FFFFFF", 0.3, emit=2.0)
        yellow = bm.mat("prop_yellow", "#FFC21A", 0.3, 0.1, coat=0.6)
        steel = bm.mat("prop_steel", "#9AA3AE", 0.25, 0.9)
        drop_m = bm.mat("prop_drop", "#7FD8FF", 0.1, emit=1.5)
        P = {}
        c, g, mi = self.r["claude"]["b"], self.r["grok"], self.r["mistral"]["b"]

        # Claude: control remoto "APAGAR" en la mano derecha + cartel "CERRADO"
        rem = pb.pivot("remote", (0, -0.16, -0.98), parent=c.parts["shoulder_R"])
        pb.box("remote_body", dark, (0, 0, 0), (0.18, 0.08, 0.36), parent=rem, bevel=0.03)
        pb.cyl("remote_btn", red, (0, -0.05, 0.08), 0.06, 0.04, (math.pi / 2, 0, 0), parent=rem)
        text_obj(pb, "remote_txt", "APAGAR", 0.055, white_e, (0, -0.05, -0.06), parent=rem)
        P["remote"] = rem
        info = self.r["claude"]
        sign = pb.pivot("closed_sign", (0, -0.66, 1.15), parent=info["root"])
        pb.box("sign_board", white, (0, 0, 0), (0.86, 0.05, 0.34), parent=sign, bevel=0.03)
        text_obj(pb, "sign_txt", "CERRADO", 0.2, red, (0, -0.04, 0), parent=sign)
        pb.cyl("sign_cord", dark, (0, 0.05, 0.3), 0.015, 0.5, (0, math.pi / 2.6, 0), parent=sign)
        P["closed_sign"] = sign

        # Grok: botón rojo "REMOVERME" que sube del suelo
        side = Vector((-g["f"].y, g["f"].x, 0))
        bp = g["p"] + g["f"] * 1.3 - side * 1.05
        btn = pb.pivot("red_button", (bp.x, bp.y, 0))
        btn.rotation_euler = (0, 0, g["theta"])
        pb.cyl("btn_col", dark, (0, 0, 0.5), 0.26, 1.0, bevel=0.03, parent=btn)
        pb.sphere("btn_dome", red, (0, 0, 1.02), 0.24, (1, 1, 0.55), parent=btn)
        pb.box("btn_plate", dark, (0, -0.3, 0.72), (0.95, 0.05, 0.22), parent=btn, bevel=0.02)
        text_obj(pb, "btn_txt", "REMOVERME", 0.13, white_e, (0, -0.335, 0.72), parent=btn)
        P["red_button"] = btn

        # Mistral: gotas de sudor, casco y llave
        hp = mi.parts["head_pivot"]
        P["drops"] = [pb.box(f"drop_{k}", drop_m, (0.62, -0.25, 0.8), (0.1, 0.1, 0.14), parent=hp)
                      for k in range(2)]
        hat = pb.pivot("hardhat", (0, 0, 0.84), parent=hp)
        pb.sphere("hat_dome", yellow, (0, 0, 0), 0.55, (1, 0.9, 0.62), parent=hat)
        pb.cyl("hat_brim", yellow, (0, -0.08, -0.02), 0.62, 0.05, scale=(1.05, 1.15, 1), parent=hat)
        P["hardhat"] = hat
        wr = pb.pivot("wrench", (0.08, -0.22, -0.85), parent=mi.parts["shoulder_R"])
        pb.cyl("wr_handle", steel, (0, 0, 0.18), 0.04, 0.5, parent=wr)
        pb.torus("wr_head", steel, (0, 0, 0.48), 0.1, 0.035, (math.pi / 2, 0, 0), parent=wr)
        P["wrench"] = wr

        # Gemini: cargador universal que cae
        gm = self.r["gemini"]
        cp = gm["p"] + gm["f"] * 1.7
        ch = pb.pivot("charger", (cp.x, cp.y, 0.2))
        ch.rotation_euler = (0, 0, gm["theta"] + 0.4)
        pb.box("ch_body", white, (0, 0, 0), (0.34, 0.2, 0.4), parent=ch, bevel=0.05)
        for sx in (-1, 1):
            pb.cyl(f"ch_prong_{sx}", steel, (sx * 0.07, 0, 0.28), 0.025, 0.18, parent=ch)
        pb.torus("ch_cable", white, (0.25, 0.1, -0.15), 0.25, 0.03, scale=(1, 1.6, 1), parent=ch)
        text_obj(pb, "ch_txt", "USB-UNIVERSAL", 0.045, dark, (0, -0.105, 0), parent=ch)
        P["charger"] = ch

        for k, o in P.items():
            for x in (o if isinstance(o, list) else [o]):
                kf(x, "scale", 1, (0, 0, 0), "CONSTANT")
        self.P = P

    # --- animación -----------------------------------------------------------
    def F(self, t):
        return frame_of(t, self.fps)

    def animate(self):
        self.anim_globe()
        self.anim_robots()
        self.anim_gags()
        self.anim_camera()

    def anim_globe(self):
        g, F = self.globe, self.F
        imp = F(0.9)
        self.impact_frame = imp
        kf(g, "location", 1, (0, 0, 13.0), "QUAD")
        for fc in fcurves(g):
            for kp in fc.keyframe_points:
                kp.easing = "EASE_IN"
        kf(g, "location", imp, tuple(GLOBE_REST))
        kf(g, "location", imp + 4, tuple(GLOBE_REST + Vector((0, 0, 0.3))))
        kf(g, "location", imp + 9, tuple(GLOBE_REST))
        pos = GLOBE_REST.copy()
        for tr in self.turns:
            d = self.r[tr["robot"]]
            f0 = F(tr["start"])
            kf(g, "location", f0, tuple(pos))
            mid = (pos + d["offer"]) / 2 + Vector((0, 0, 0.9))
            kf(g, "location", f0 + 5, tuple(mid))
            kf(g, "location", f0 + 10, tuple(d["offer"]))
            pos = d["offer"].copy()
            if tr["lines"][0].get("gag") == "globe_return":
                fl = F(tr["lines"][0]["start"]) + 6
                kf(g, "location", fl, tuple(pos))
                kf(g, "location", fl + 6, tuple((pos + GLOBE_REST) / 2 + Vector((0, 0, 0.7))))
                kf(g, "location", fl + 13, tuple(GLOBE_REST))
                pos = GLOBE_REST.copy()
        # giro continuo
        kf(self.globe_spin, "rotation_euler", 1, (0, 0, 0), "LINEAR")
        kf(self.globe_spin, "rotation_euler", self.end_frame, (0, 0, self.end_frame / 30 * 0.9),
           "LINEAR")
        # destello al impacto
        fl = self.flash.data
        kf(fl, "energy", 1, 0)
        kf(fl, "energy", imp - 1, 0)
        kf(fl, "energy", imp, 4000)
        kf(fl, "energy", imp + 12, 0)
        es = self.ped_ring.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        for fr, v in ((1, 1.0), (imp - 1, 1.0), (imp, 25.0), (imp + 15, 4.0)):
            es.default_value = v
            es.keyframe_insert("default_value", frame=fr)

    def line_at(self, t):
        for bl in self.blocks:
            for ln in bl.get("lines", []):
                if ln["start"] <= t < ln["end"]:
                    return ln
        return None

    def focus_at(self, t):
        if t < 0.9:
            return None
        for tr in self.turns:
            if tr["start"] <= t < tr["end"]:
                return tr["robot"]
        return "pedestal"

    def anim_robots(self):
        F, fps = self.F, self.fps
        hops = {}  # inicio de cada frase por robot
        for tr in self.turns:
            hops.setdefault(tr["robot"], []).extend(ln["start"] for ln in tr["lines"])
        nod_windows = []
        last = self.turns[-1]
        if last["reactor"] == "all_nod":
            l3 = last["lines"][-1]
            nod_windows.append((l3["start"] + (l3["end"] - l3["start"]) * 0.4, l3["end"] + 0.4))
        mistral_l1 = next(tr for tr in self.turns if tr["robot"] == "mistral")["lines"][0]

        for n, d in self.r.items():
            root, head = d["root"], d["head"]
            phase = rng.random() * 6
            amp = {"gemini": 0.09, "deepseek": 0.07}.get(n, 0.025)
            yaw = 0.0
            for fr in range(1, self.end_frame + 2, 2):
                t = (fr - 1) / fps
                z = amp * math.sin(t * 2.6 + phase)
                z += sum(0.13 * math.exp(-((t - h - 0.08) / 0.07) ** 2) for h in hops.get(n, []))
                rz = d["theta"]
                if n == "mistral" and mistral_l1["start"] <= t < mistral_l1["end"]:
                    rz += 0.05 * math.sin(t * 70)
                rx = 0.04 * math.sin(t * 1.9 + phase) if n == "deepseek" else 0
                kf(root, "location", fr, (d["p"].x, d["p"].y, z))
                kf(root, "rotation_euler", fr, (rx, 0, rz))
                if head is None:
                    continue
                foc = self.focus_at(t)
                if foc is None or foc == n:
                    target = 0.0
                else:
                    q = GLOBE_REST if foc == "pedestal" else self.r[foc]["p"]
                    dv = q - d["p"]
                    target = max(-1.0, min(1.0, wrap(face_angle(dv) - d["theta"])))
                yaw += (target - yaw) * 0.45
                ln = self.line_at(t)
                pitch = 0.0
                if ln and ln["speaker"] == n:
                    i = int((t - ln["start"]) * fps)
                    pitch = -0.07 * ln["env"][min(i, len(ln["env"]) - 1)]
                for a, b in nod_windows:
                    if a <= t < b:
                        pitch -= 0.22 * max(0, math.sin((t - a) * 2 * math.pi * 1.6))
                kf(head, "rotation_euler", fr, (pitch, 0, yaw))

            # boca sincronizada
            mouth = d["b"].parts.get("mouth")
            if mouth:
                kf(mouth, "scale", 1, (1, 1, 1))
                for bl in self.blocks:
                    for ln in bl.get("lines", []):
                        if ln["speaker"] != n:
                            continue
                        f0 = F(ln["start"])
                        kf(mouth, "scale", f0 - 1, (1, 1, 1))
                        for i, e in enumerate(ln["env"]):
                            kf(mouth, "scale", f0 + i, (1 + 0.3 * e, 1, 1 + 2.0 * e))
                        kf(mouth, "scale", f0 + len(ln["env"]), (1, 1, 1))

            # parpadeos
            eyes = [d["b"].parts.get(k) for k in ("eye_L", "eye_R")]
            t = rng.uniform(0.5, 2.5)
            while t < self.outro["start"]:
                fr = F(t)
                for e in eyes:
                    if e is None or e.type == "EMPTY":
                        continue
                    s = tuple(e.scale)
                    kf(e, "scale", fr, s)
                    kf(e, "scale", fr + 2, (s[0], s[1], s[2] * 0.08))
                    kf(e, "scale", fr + 4, s)
                t += rng.uniform(2.2, 4.0)

            # cola y aletas de la ballena
            if n == "deepseek":
                tail, fins = d["b"].parts["tail_pivot"], [d["b"].parts[f"fin_pivot_{s}"] for s in "LR"]
                for fr in range(1, self.end_frame + 2, 4):
                    t = (fr - 1) / fps
                    speaking = (self.line_at(t) or {}).get("speaker") == n
                    k = 2.2 if speaking else 1.0
                    kf(tail, "rotation_euler", fr, (0, math.radians(-20 + 12 * k * math.sin(t * 3)), 0))
                    for s, fp in zip((1, -1), fins):
                        kf(fp, "rotation_euler", fr, (s * math.radians(14 * k * math.sin(t * 4)), 0, 0))

        self.anim_arms()

    def anim_arms(self):
        F = self.F
        hold = {"remote": ("claude", 1, -1.35), "red_button": ("grok", 1, -0.75),
                "hardhat": ("mistral", 1, -0.55)}
        for tr in self.turns:
            n = tr["robot"]
            parts = self.r[n]["b"].parts
            if "shoulder_L" not in parts:
                continue
            base = self.r[n]["base_rot"]
            shL = parts["shoulder_L"]
            b0 = base["shoulder_L"]
            for ln in tr["lines"]:  # gesto con el brazo izquierdo en cada frase
                f0 = F(ln["start"])
                kf(shL, "rotation_euler", f0, b0)
                kf(shL, "rotation_euler", f0 + 6, (b0[0] - 0.55, b0[1], b0[2]))
                kf(shL, "rotation_euler", f0 + 16, b0)
            for ln in tr["lines"]:  # sostener un objeto con el derecho
                g = ln.get("gag")
                if g in hold:
                    shR, b1 = parts["shoulder_R"], base["shoulder_R"]
                    f0, f1 = F(ln["start"]), F(tr["end"])
                    kf(shR, "rotation_euler", f0, b1)
                    kf(shR, "rotation_euler", f0 + 7, (b1[0] + hold[g][2], b1[1], b1[2]))
                    kf(shR, "rotation_euler", f1 - 4, (b1[0] + hold[g][2], b1[1], b1[2]))
                    kf(shR, "rotation_euler", f1 + 6, b1)

    def holo_show(self, robot, frames_imgs, f_end):
        """frames_imgs: [(frame, imagen)], abre el holograma detrás del robot."""
        d = self.r[robot]
        h = self.holo
        pos = d["p"] - d["f"] * 2.3 + Vector((0, 0, 4.6))
        f0 = frames_imgs[0][0]
        kf(h, "location", f0 - 1, tuple(pos), "CONSTANT")
        kf(h, "rotation_euler", f0 - 1, (0, 0, d["theta"] if robot != "deepseek"
                                          else face_angle(d["f"])), "CONSTANT")
        kf(h, "scale", f0 - 1, (0, 0, 0), "CONSTANT")
        kf(h, "scale", f0, (1, 1, 0.03))
        kf(h, "scale", f0 + 5, (1, 1, 1))
        kf(h, "scale", f_end - 4, (1, 1, 1))
        kf(h, "scale", f_end - 1, (1, 1, 0.03), "CONSTANT")
        kf(h, "scale", f_end, (0, 0, 0), "CONSTANT")
        prev = None
        for i, (fr, img) in enumerate(frames_imgs):
            o = self.holo_imgs[img]
            if prev:
                kf(prev, "scale", fr, (0, 0, 0), "CONSTANT")
            kf(o, "scale", fr, (1, 1, 1), "CONSTANT")
            prev = o
        kf(prev, "scale", f_end, (0, 0, 0), "CONSTANT")

    def anim_gags(self):
        F, P = self.F, self.P
        for tr in self.turns:
            n = tr["robot"]
            f_end = F(tr["end"])
            screen, screen_end = [], None
            for ln in tr["lines"]:
                g = ln.get("gag")
                f0, f1 = F(ln["start"]), F(ln["end"])
                if not g:
                    continue
                if g == "screen:off":
                    screen_end = f0 + 2
                    continue
                if g.startswith("screen:"):
                    k = g.split(":")[1]
                    if k == "slides":
                        step = (f1 - f0) / 5
                        screen += [(int(f0 + i * step), f"slide{i + 1}") for i in range(5)]
                    elif k == "tanks":
                        screen += [(f0, "tanks_a"), (int(f0 + (f1 - f0) * 0.45), "tanks_b")]
                    else:
                        screen.append((f0, k))
                elif g in ("remote", "closed_sign"):
                    pop_in(P[g], f0 + (6 if g == "remote" else 0))
                    pop_out(P[g], f_end)
                elif g == "red_button":
                    b = P[g]
                    z0 = b.location.z
                    kf(b, "scale", f0, (1, 1, 1), "CONSTANT")
                    kf(b, "location", f0, (b.location.x, b.location.y, z0 - 1.3))
                    kf(b, "location", f0 + 8, (b.location.x, b.location.y, z0 + 0.08))
                    kf(b, "location", f0 + 12, (b.location.x, b.location.y, z0))
                    pop_out(b, f_end)
                elif g == "sweat":
                    for k, drop in enumerate(P["drops"]):
                        a = f0 + k * 9
                        x0 = drop.location.copy()
                        kf(drop, "scale", a - 1, (0, 0, 0), "CONSTANT")
                        kf(drop, "scale", a, (1, 1, 1))
                        kf(drop, "location", a, tuple(x0))
                        kf(drop, "location", a + 16, tuple(x0 + Vector((0.05, 0, -0.55))))
                        kf(drop, "scale", a + 15, (1, 1, 1))
                        kf(drop, "scale", a + 18, (0, 0, 0), "CONSTANT")
                elif g == "hardhat":
                    hat, wr = P["hardhat"], P["wrench"]
                    kf(hat, "scale", f0, (1, 1, 1), "CONSTANT")
                    kf(hat, "location", f0, (0, 0, 2.2))
                    kf(hat, "location", f0 + 6, (0, 0, 0.84))
                    kf(hat, "location", f0 + 9, (0, 0, 0.95))
                    kf(hat, "location", f0 + 12, (0, 0, 0.84))
                    pop_out(hat, f_end)
                    pop_in(wr, f0 + 6)
                    pop_out(wr, f_end)
                elif g == "charger":
                    ch = P["charger"]
                    x, y = ch.location.x, ch.location.y
                    kf(ch, "scale", f0, (1, 1, 1), "CONSTANT")
                    kf(ch, "location", f0, (x, y, 6.0), "QUAD")
                    kf(ch, "location", f0 + 9, (x, y, 0.2))
                    kf(ch, "location", f0 + 13, (x, y, 0.45))
                    kf(ch, "location", f0 + 17, (x, y, 0.2))
                elif g == "globe_split":
                    gpos = self.r[n]["offer"]
                    for s in self.sparks:
                        dvec = Vector((rng.uniform(-1, 1), rng.uniform(-1, 0.4), rng.uniform(-0.2, 1)))
                        dvec = dvec.normalized() * rng.uniform(2.5, 5.0)
                        a = f0 + rng.randint(0, 6)
                        kf(s, "scale", a - 1, (0, 0, 0), "CONSTANT")
                        kf(s, "location", a, tuple(gpos))
                        kf(s, "scale", a, (1, 1, 1))
                        kf(s, "location", a + 26, tuple(gpos + dvec))
                        kf(s, "scale", a + 24, (0.6, 0.6, 0.6))
                        kf(s, "scale", a + 27, (0, 0, 0), "CONSTANT")
            if screen:
                self.holo_show(n, screen, screen_end or f_end)
        for s in self.sparks:
            if not s.animation_data:
                kf(s, "scale", 1, (0, 0, 0), "CONSTANT")

    # --- cámara ----------------------------------------------------------------
    def pose(self, kind, n=None):
        """Devuelve (posición, objetivo, lente) para un tipo de plano."""
        if kind == "wide":
            return Vector((0, -10.5, 5.8)), Vector((0, 1.8, 1.5)), 22
        if kind == "hook_pan_a":
            return Vector((-5.5, -6.0, 1.3)), Vector((-2.0, 2.0, 1.8)), 24
        if kind == "hook_pan_b":
            return Vector((5.5, -6.0, 1.3)), Vector((2.0, 2.0, 1.8)), 24
        if kind == "group":
            return Vector((0, -9.0, 3.0)), Vector((0, 2.0, 1.6)), 22
        d = self.r[n]
        p, f, hz = d["p"], d["f"], d["head_z"]
        if kind == "medium":
            return p + f * 5.6 + Vector((0, 0, 2.1)), p + Vector((0, 0, 2.5)), 26
        if kind == "holo":
            return p + f * 5.2 + Vector((0, 0, 2.7)), p - f * 1.2 + Vector((0, 0, 3.6)), 27
        if kind == "close":
            if "face" in d:
                tgt = d["face"]
                return tgt + f * 3.4 + Vector((0, 0, 0.4)), tgt, 30
            side = Vector((-f.y, f.x, 0)) * 0.35
            return p + f * 3.3 + side + Vector((0, 0, hz + 0.05)), p + Vector((0, 0, hz - 0.3)), 30
        raise ValueError(kind)

    def shot_list(self):
        S, F = [], self.F
        h = self.hook
        S.append((1, F(1.15), "wide", None))
        S.append((F(1.15), F(h["end"]), "hook_pan", None))
        for tr in self.turns:
            n, L = tr["robot"], tr["lines"]
            g = [ln.get("gag") or "" for ln in L]
            fa, f2, f3, fe = F(tr["start"]), F(L[1]["start"]), F(L[2]["start"]), F(tr["end"])
            S.append((fa, f2, "medium", n))
            kind2 = ("holo" if g[1].startswith("screen:") and g[1] != "screen:off"
                     else "medium" if g[1] == "red_button" else "close")
            S.append((f2, f3, kind2, n))
            fr = int(f3 + (F(L[2]["end"]) - f3) * 0.6)
            kind3 = "medium" if g[2] in ("globe_split", "charger") else "close"
            S.append((f3, fr, kind3, n))
            if tr["reactor"] == "all_nod":
                S.append((fr, fe, "group", None))
            else:
                S.append((fr, fe, "close", tr["reactor"]))
        return S

    def anim_camera(self):
        cam = self.cam
        for f0, f1, kind, n in self.shot_list():
            if kind == "hook_pan":
                a, b = self.pose("hook_pan_a"), self.pose("hook_pan_b")
                loc0, tgt0, lens = a
                loc1, tgt1, _ = b
            else:
                loc0, tgt0, lens = self.pose(kind, n)
                loc1 = loc0 + (tgt0 - loc0) * 0.07
                tgt1 = tgt0
            for fr, loc, tgt in ((f0, loc0, tgt0), (f1 - 1, loc1, tgt1)):
                rot = (tgt - loc).to_track_quat("-Z", "Y").to_euler()
                kf(cam, "location", fr, tuple(loc), "LINEAR")
                kf(cam, "rotation_euler", fr, tuple(rot), "LINEAR")
                cam.data.lens = lens
                cam.data.keyframe_insert("lens", frame=fr)
        set_interp(cam, "LINEAR")
        set_interp(cam.data, "CONSTANT")

    # --- salida -----------------------------------------------------------------
    def save(self):
        path = os.path.join(self.out, "scene.blend")
        bpy.ops.wm.save_as_mainfile(filepath=path)
        print("Escena guardada:", path)

    def render(self, frames=None, still=None):
        sc = self.sc
        if still:
            sc.frame_set(still)
            sc.render.filepath = os.path.join(self.out, f"still_{still:04d}.png")
            bpy.ops.render.render(write_still=True)
            print("Still:", sc.render.filepath)
            return
        a, b = frames or (1, self.end_frame)
        sc.frame_start, sc.frame_end = a, b
        sc.render.filepath = os.path.join(self.out, "frames", "f_")
        sc.render.use_overwrite = False  # permite reanudar un render interrumpido
        bpy.ops.render.render(animation=True)

    def portraits(self):
        """Renderiza una tarjeta por robot para el cierre (output/<slug>/portraits)."""
        sc = self.sc
        sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 500, 620, 100
        sc.frame_set(1)
        for o in self.props.col.all_objects:
            o.hide_render = True
        cam = self.cam
        if cam.animation_data:
            cam.animation_data_clear()
            cam.data.animation_data_clear()
        for n, d in self.r.items():
            for m, other in self.r.items():
                for o in other["b"].col.all_objects:
                    o.hide_render = m != n
            p, f = d["p"], d["f"]
            top = 3.6 if n not in ("deepseek",) else 2.5
            cam.location = p + f * 6.2 + Vector((0, 0, top * 0.55))
            tgt = p + Vector((0, 0, top * 0.48))
            cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
            cam.data.lens = 50
            sc.render.filepath = os.path.join(self.out, "portraits", f"{n}.png")
            bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.abspath(argv[0])

    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default

    st = Stage(out, int(opt("--percent", 100)))
    st.animate()
    # pantalla de los robots en el cierre (para las etiquetas del compose)
    if "--portraits" in argv:
        st.portraits()
        return
    st.save()
    if "--still" in argv:
        for fr in opt("--still").split(","):
            st.render(still=int(fr))
    elif "--render" in argv:
        fr = opt("--frames")
        st.render(tuple(int(x) for x in fr.split(":")) if fr else None)


if __name__ == "__main__":
    main()
