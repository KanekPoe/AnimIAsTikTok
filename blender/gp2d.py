"""Utilidades de dibujo 2D con Grease Pencil v3 (Blender 4.5+).

Todo se dibuja en el plano XZ (la cámara mira hacia +Y). Cada "pieza" es un objeto
Grease Pencil con uno o varios trazos rellenos y con contorno; las piezas se parentan a
pivotes (empties) para animarlas igual que en el 3D.

Profundidad: cuanto más negativo el `depth` de una pieza, más al frente se dibuja.
"""
import math

import bpy

OUTLINE = "#1E1E28"
LINE = 0.035  # grosor de contorno por defecto (radio en unidades de escena)


# ----------------------------------------------------------------------------
# Color
# ----------------------------------------------------------------------------
def lin(h, a=1.0):
    """Hex sRGB -> RGBA lineal (los materiales de Blender trabajan en lineal)."""
    h = h.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (a,)


_MATS = {}


def gp_mat(fill=None, stroke=OUTLINE):
    """Material de Grease Pencil (cacheado por colores). fill/stroke = hex o None."""
    key = (fill, stroke)
    if key not in _MATS:
        m = bpy.data.materials.new(f"gp_{fill}_{stroke}")
        bpy.data.materials.create_gpencil_data(m)
        g = m.grease_pencil
        g.show_fill = fill is not None
        g.show_stroke = stroke is not None
        if fill:
            g.fill_color = lin(fill)
        if stroke:
            g.color = lin(stroke)
        _MATS[key] = m
    return _MATS[key]


# ----------------------------------------------------------------------------
# Formas (listas de puntos 2D (x, z))
# ----------------------------------------------------------------------------
def ellipse(cx, cz, rx, rz, n=48, rot=0.0):
    c, s = math.cos(rot), math.sin(rot)
    pts = []
    for i in range(n):
        t = i / n * math.tau
        x, z = rx * math.cos(t), rz * math.sin(t)
        pts.append((cx + x * c - z * s, cz + x * s + z * c))
    return pts


def circle(cx, cz, r, n=40):
    return ellipse(cx, cz, r, r, n)


def rrect(x0, z0, x1, z1, r=0.15, n=6):
    """Rectángulo con esquinas redondeadas."""
    r = min(r, abs(x1 - x0) / 2, abs(z1 - z0) / 2)
    pts = []
    for cx, cz, a0 in ((x1 - r, z1 - r, 0), (x0 + r, z1 - r, 90), (x0 + r, z0 + r, 180),
                       (x1 - r, z0 + r, 270)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    return pts


def arc(cx, cz, rx, rz, a0, a1, n=16):
    """Arco abierto (para cejas, sonrisas). Ángulos en grados."""
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             cz + rz * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


def smooth(pts, iters=2):
    """Suaviza un polígono cerrado (Chaikin)."""
    for _ in range(iters):
        out = []
        for i in range(len(pts)):
            (x0, z0), (x1, z1) = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * x0 + 0.25 * x1, 0.75 * z0 + 0.25 * z1),
                    (0.25 * x0 + 0.75 * x1, 0.25 * z0 + 0.75 * z1)]
        pts = out
    return pts


# ----------------------------------------------------------------------------
# Piezas
# ----------------------------------------------------------------------------
class Kit:
    """Crea piezas y pivotes dentro de una collection, con prefijo de nombre."""

    def __init__(self, name):
        self.name = name
        self.col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(self.col)
        self.parts = {}
        self.root = self.pivot("root", parent=False)

    def _link(self, obj, n, parent):
        obj.name = f"{self.name}_{n}"
        self.col.objects.link(obj)
        if parent is not False:
            obj.parent = parent or self.root
        self.parts[n] = obj
        return obj

    def pivot(self, n, loc=(0, 0), parent=None, depth=0.0):
        e = bpy.data.objects.new(n, None)
        e.empty_display_size = 0.2
        e.location = (loc[0], depth, loc[1])
        return self._link(e, n, parent)

    def piece(self, n, loc=(0, 0), parent=None, depth=0.0):
        """Pieza vacía; se le agregan trazos con add()."""
        gp = bpy.data.grease_pencils_v3.new(n) if hasattr(bpy.data, "grease_pencils_v3") \
            else bpy.data.grease_pencils.new(n)
        gp.stroke_depth_order = "2D"
        obj = bpy.data.objects.new(n, gp)
        obj.location = (loc[0], depth, loc[1])
        layer = gp.layers.new("capa")
        layer.use_lights = False
        layer.frames.new(1)
        obj["_mats"] = []
        return self._link(obj, n, parent)

    def add(self, obj, pts, fill=None, stroke=OUTLINE, width=LINE, cyclic=True):
        """Agrega un trazo (puntos en coords locales de la pieza)."""
        gp = obj.data
        m = gp_mat(fill, stroke)
        if m.name not in [x.name for x in gp.materials]:
            gp.materials.append(m)
        idx = [x.name for x in gp.materials].index(m.name)
        d = gp.layers[0].frames[0].drawing
        d.add_strokes([len(pts)])
        s = d.strokes[len(d.strokes) - 1]
        s.cyclic = cyclic
        s.material_index = idx
        for p, (x, z) in zip(s.points, pts):
            p.position = (x, 0, z)
            p.radius = width
        return obj

    def shape(self, n, pts, fill, stroke=OUTLINE, width=LINE, loc=(0, 0), parent=None,
              depth=0.0, cyclic=True):
        """Atajo: pieza nueva con un solo trazo."""
        o = self.piece(n, loc, parent, depth)
        return self.add(o, pts, fill, stroke, width, cyclic)


# ----------------------------------------------------------------------------
# Escena 2D
# ----------------------------------------------------------------------------
def setup_2d_scene(bg="#CFE8F3", ortho=16.0, size=(1080, 1920), fps=30):
    """Cámara ortográfica vertical y render plano (Workbench) para 2D."""
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.fps = fps
    sc.view_settings.view_transform = "Standard"
    sh = sc.display.shading
    sh.light = "FLAT"
    sh.color_type = "MATERIAL"
    sh.background_type = "WORLD"
    w = bpy.data.worlds.new("fondo")
    w.color = lin(bg)[:3]
    sc.world = w
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho  # alto visible en unidades (marco 9x16 si ortho=16)
    cam.location = (0, -20, ortho / 2)
    cam.rotation_euler = (math.radians(90), 0, 0)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.film_transparent = False
    return cam
