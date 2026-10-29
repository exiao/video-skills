"""Build the editable Blender scene from timeline.py and the HTML textures.

    blender -b --factory-startup -P scene.py            # writes clawd.blend

Every animated value is baked per frame (1..360) from timeline.py, so the .blend is
seekable and repeatable: frame f shows wall time (f - 1) / 30.
"""
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import timeline as T  # noqa: E402

TEX = os.environ.get("CLAWD_TEX", os.path.join(ROOT, "textures"))
BLEND_OUT = os.environ.get("CLAWD_BLEND", os.path.join(ROOT, "clawd.blend"))

UI_EMIT = 1.1          # emission strength of the UI texture
UI_DIFFUSE = 0.55      # diffuse share of the UI texture so shadows and contact read
COMP_EMIT = 1.6
EXPOSURE = 0.15        # follow-up 2
F_STOP = 2.8


def srgb(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in range(3):
        c = int(h[2 * i:2 * i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def m(u, v, z=0.0):
    x, y = T.ui_to_m(u, v)
    return Vector((x, y, z))


def px(n):
    return n * T.M_PER_PX


# ------------------------------------------------------------------ reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = "Clawd"
scene.render.fps = T.FPS
scene.frame_start, scene.frame_end = 1, T.FRAMES
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.resolution_percentage = 100

coll_ui = bpy.data.collections.new("UI_slabs")
coll_hero = bpy.data.collections.new("Clawd")
coll_fx = bpy.data.collections.new("FX")
coll_rig = bpy.data.collections.new("Camera_Lights")
for c in (coll_ui, coll_hero, coll_fx, coll_rig):
    scene.collection.children.link(c)


def link(obj, coll):
    coll.objects.link(obj)
    return obj


# ------------------------------------------------------------------ images
def load_image(path, seq=False, colorspace="sRGB"):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    if seq:
        img.source = "SEQUENCE"
    return img


IMG_BASE = load_image(os.path.join(TEX, "ui_base.png"))
IMG_ACTIVE = load_image(os.path.join(TEX, "ui_active.png"))


# ------------------------------------------------------------------ materials
def node(nt, kind, loc=(0, 0), **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def glass_principled(nt, loc=(300, 0)):
    """Black glossy screen glass; follow-up 2: specular 0.1, roughness 0.32."""
    p = node(nt, "ShaderNodeBsdfPrincipled", loc)
    p.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    p.inputs["Roughness"].default_value = 0.32
    p.inputs["Specular IOR Level"].default_value = 0.1
    return p


def obj_attr(nt, name, loc):
    a = node(nt, "ShaderNodeAttribute", loc)
    a.attribute_type = "OBJECT"
    a.attribute_name = name
    return a


def make_ui_material():
    """Shared by every slab/cap/overlay. Object custom props: power (0..1), active (0/1)."""
    mat = bpy.data.materials.new("UI_glass")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    uv = node(nt, "ShaderNodeTexCoord", (-900, 0))
    base = node(nt, "ShaderNodeTexImage", (-650, 150), image=IMG_BASE, interpolation="Cubic")
    act = node(nt, "ShaderNodeTexImage", (-650, -150), image=IMG_ACTIVE, interpolation="Cubic")
    nt.links.new(uv.outputs["UV"], base.inputs["Vector"])
    nt.links.new(uv.outputs["UV"], act.inputs["Vector"])
    a_active = obj_attr(nt, "active", (-650, 350))
    a_power = obj_attr(nt, "power", (-650, 500))
    mixc = node(nt, "ShaderNodeMix", (-350, 0), data_type="RGBA")
    nt.links.new(a_active.outputs["Fac"], mixc.inputs["Factor"])
    nt.links.new(base.outputs["Color"], mixc.inputs[6])
    nt.links.new(act.outputs["Color"], mixc.inputs[7])
    p = glass_principled(nt, (300, 0))
    dif = node(nt, "ShaderNodeMath", (0, 200), operation="MULTIPLY")
    dif.inputs[1].default_value = UI_DIFFUSE
    # diffuse share is a colour multiply: use a MixRGB multiply
    dmul = node(nt, "ShaderNodeMix", (0, 100), data_type="RGBA", blend_type="MULTIPLY")
    dmul.inputs["Factor"].default_value = 1.0
    nt.links.new(mixc.outputs[2], dmul.inputs[6])
    dmul.inputs[7].default_value = (UI_DIFFUSE, UI_DIFFUSE, UI_DIFFUSE, 1)
    nt.nodes.remove(dif)
    pw = node(nt, "ShaderNodeMath", (0, 350), operation="MULTIPLY")
    nt.links.new(a_power.outputs["Fac"], pw.inputs[0])
    pw.inputs[1].default_value = UI_EMIT
    # base colour also dims when powered down so dead panels read black
    dpow = node(nt, "ShaderNodeMix", (150, 100), data_type="RGBA")
    nt.links.new(a_power.outputs["Fac"], dpow.inputs["Factor"])
    dpow.inputs[6].default_value = (0.004, 0.004, 0.004, 1)
    nt.links.new(dmul.outputs[2], dpow.inputs[7])
    nt.links.new(dpow.outputs[2], p.inputs["Base Color"])
    nt.links.new(mixc.outputs[2], p.inputs["Emission Color"])
    nt.links.new(pw.outputs[0], p.inputs["Emission Strength"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_seq_material(name, folder, strength, extra_power=True):
    """Emissive screen fed by a numbered PNG sequence (0001.png .. 0360.png)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputMaterial", (900, 0))
    img = load_image(os.path.join(TEX, folder, "0001.png"), seq=True)
    tex = node(nt, "ShaderNodeTexImage", (-400, 0), image=img, interpolation="Cubic")
    tex.image_user.frame_duration = T.FRAMES
    tex.image_user.frame_start = 1
    tex.image_user.frame_offset = 0
    tex.image_user.use_auto_refresh = True
    tex.image_user.use_cyclic = False
    p = glass_principled(nt, (300, 0))
    pw = node(nt, "ShaderNodeMath", (0, 300), operation="MULTIPLY")
    a_power = obj_attr(nt, "power", (-400, 300))
    nt.links.new(a_power.outputs["Fac"], pw.inputs[0])
    pw.inputs[1].default_value = strength
    dmul = node(nt, "ShaderNodeMix", (0, 100), data_type="RGBA", blend_type="MULTIPLY")
    dmul.inputs["Factor"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], dmul.inputs[6])
    dmul.inputs[7].default_value = (UI_DIFFUSE * 0.5,) * 3 + (1,)
    nt.links.new(dmul.outputs[2], p.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
    nt.links.new(pw.outputs[0], p.inputs["Emission Strength"])
    nt.links.new(p.outputs["BSDF"], out.inputs["Surface"])
    return mat


def make_basic(name, rgb, rough=0.4, emit=None, emit_strength=0.0, coat=0.0, spec=0.5, alpha_img=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    p = nt.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = rgb
    p.inputs["Roughness"].default_value = rough
    p.inputs["Specular IOR Level"].default_value = spec
    p.inputs["Coat Weight"].default_value = coat
    if emit is not None:
        p.inputs["Emission Color"].default_value = emit
        p.inputs["Emission Strength"].default_value = emit_strength
    if alpha_img is not None:
        tex = node(nt, "ShaderNodeTexImage", (-500, 0), image=alpha_img, interpolation="Cubic")
        nt.links.new(tex.outputs["Color"], p.inputs["Base Color"])
        nt.links.new(tex.outputs["Color"], p.inputs["Emission Color"])
        nt.links.new(tex.outputs["Alpha"], p.inputs["Alpha"])
        p.inputs["Emission Strength"].default_value = emit_strength
    return mat


MAT_UI = make_ui_material()
MAT_EDGE = make_basic("Slab_edge", (0.012, 0.012, 0.013, 1), rough=0.35, spec=0.3)
MAT_COMP = make_seq_material("Comp_screen", "comp", COMP_EMIT)
MAT_TC_COMP = make_seq_material("TC_comp", "tc_comp", UI_EMIT)
MAT_TC_TL = make_seq_material("TC_timeline", "tc_tl", UI_EMIT)
MAT_BODY = make_basic("Clawd_body", (*T.BODY_BASE_RGB, 1), rough=0.45, coat=0.08, spec=0.35)
MAT_EYE = make_basic("Clawd_eye", (0.005, 0.004, 0.004, 1), rough=0.18, spec=0.6)
MAT_PLAYHEAD = make_basic("Playhead", (0.25, 0.55, 1.0, 1), rough=0.2,
                          emit=(0.35, 0.65, 1.0, 1), emit_strength=6.0)
MAT_PLAYLINE = make_basic("Playhead_line", (0.2, 0.5, 1.0, 1), rough=0.3,
                          emit=(0.3, 0.6, 1.0, 1), emit_strength=5.0)
MAT_GEM = make_basic("Keyframe_gem", (0.9, 0.9, 0.92, 1), rough=0.25,
                     emit=(1, 1, 1, 1), emit_strength=2.2)
MAT_SHARD = make_basic("Glass_shard", (0.6, 0.75, 0.9, 1), rough=0.05, spec=1.0,
                       emit=(0.55, 0.75, 1.0, 1), emit_strength=0.8)
IMG_CARD = load_image(os.path.join(TEX, "clawd_card.png"))
MAT_CARD = make_basic("Clawd_card", (1, 1, 1, 1), rough=0.4, emit_strength=0.45, alpha_img=IMG_CARD)
IMG_CHIP = load_image(os.path.join(TEX, "glow_chip.png"))
MAT_CHIP_FACE = make_basic("Glow_chip_face", (1, 1, 1, 1), rough=0.3, emit_strength=2.0, alpha_img=IMG_CHIP)
MAT_CHIP_BODY = make_basic("Glow_chip_body", (0.05, 0.25, 0.6, 1), rough=0.25,
                           emit=(0.1, 0.35, 0.9, 1), emit_strength=1.0)


# ------------------------------------------------------------------ mesh helpers
def box_mesh(name, w, d, h, uv_rect=None, z0=0.0):
    """Box w (x) x d (y) x h (z), origin at top-centre minus h (top at z0).

    uv_rect = (x, y, w, h) in UI px maps the top face onto the UI texture; the
    top face uses material slot 0, sides slot 1.
    """
    bm = bmesh.new()
    hw, hd = w / 2, d / 2
    zt, zb = z0, z0 - h
    co = [(-hw, -hd, zb), (hw, -hd, zb), (hw, hd, zb), (-hw, hd, zb),
          (-hw, -hd, zt), (hw, -hd, zt), (hw, hd, zt), (-hw, hd, zt)]
    vs = [bm.verts.new(c) for c in co]
    faces = [(4, 5, 6, 7), (3, 2, 1, 0), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    fs = [bm.faces.new([vs[i] for i in f]) for f in faces]
    uv_layer = bm.loops.layers.uv.new("UVMap")
    for i, f in enumerate(fs):
        f.material_index = 0 if i == 0 else 1
        for loop in f.loops:
            if uv_rect is not None and i == 0:
                x, y, rw, rh = uv_rect
                lx, ly = loop.vert.co.x, loop.vert.co.y
                upx = x + (lx + hw) / w * rw
                vpx = y + (hd - ly) / d * rh
                loop[uv_layer].uv = (upx / T.UI_W, 1 - vpx / T.UI_H)
            else:
                loop[uv_layer].uv = (0.0, 0.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def plane_mesh(name, w, d, uv=((0, 0), (1, 0), (1, 1), (0, 1)), origin="center"):
    bm = bmesh.new()
    if origin == "bottom":  # hinge on the -y edge
        co = [(-w / 2, 0, 0), (w / 2, 0, 0), (w / 2, d, 0), (-w / 2, d, 0)]
    else:
        co = [(-w / 2, -d / 2, 0), (w / 2, -d / 2, 0), (w / 2, d / 2, 0), (-w / 2, d / 2, 0)]
    vs = [bm.verts.new(c) for c in co]
    f = bm.faces.new(vs)
    uvl = bm.loops.layers.uv.new("UVMap")
    for loop, uvc in zip(f.loops, uv):
        loop[uvl].uv = uvc
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return me


def rect_uv(x, y, w, h):
    return ((x / T.UI_W, 1 - (y + h) / T.UI_H), ((x + w) / T.UI_W, 1 - (y + h) / T.UI_H),
            ((x + w) / T.UI_W, 1 - y / T.UI_H), (x / T.UI_W, 1 - y / T.UI_H))


def add_bevel(obj, width, segments=3):
    mod = obj.modifiers.new("Bevel", "BEVEL")
    mod.width = width
    mod.segments = segments
    mod.limit_method = "ANGLE"
    mod.harden_normals = False
    return mod


def new_obj(name, me, coll, mats=()):
    obj = bpy.data.objects.new(name, me)
    for mt in mats:
        obj.data.materials.append(mt)
    link(obj, coll)
    return obj


def set_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True


def ui_props(obj, power=1.0, active=0.0):
    obj["power"] = power
    obj["active"] = active


# ------------------------------------------------------------------ UI slabs
GAP = 1.0  # UI px inset on each side -> visible seams between slabs
SLABS = {}
for name, (x, y, w, h) in T.PANELS.items():
    rect = (x + GAP, y + GAP, w - 2 * GAP, h - 2 * GAP)
    me = box_mesh("slab_" + name, px(rect[2]), px(rect[3]), T.SLAB_THICK, uv_rect=rect)
    ob = new_obj("Slab_" + name, me, coll_ui, (MAT_UI, MAT_EDGE))
    ob.location = m(rect[0] + rect[2] / 2, rect[1] + rect[3] / 2, 0.0)
    add_bevel(ob, 0.0035, 2)
    ui_props(ob)
    SLABS[name] = ob


def child_of(obj, parent):
    obj.parent = parent
    obj.matrix_parent_inverse = parent.matrix_world.inverted()


# Toolbar + preview keycaps
CAPS = {}


def make_cap(name, cu, cv, w, h, parent):
    rect = (cu - w / 2 + 1, cv - h / 2 + 1, w - 2, h - 2)
    me = box_mesh("cap_" + name, px(rect[2]), px(rect[3]), T.CAP_TOP_Z, uv_rect=rect)
    ob = new_obj("Cap_" + name, me, coll_ui, (MAT_UI, MAT_EDGE))
    ob.location = m(cu, cv, T.CAP_TOP_Z)
    add_bevel(ob, 0.0016, 2)
    ui_props(ob)
    bpy.context.view_layer.update()
    child_of(ob, parent)
    CAPS[name] = ob
    return ob


bpy.context.view_layer.update()
for name, (cu, cv) in T.TOOLS.items():
    make_cap(name, cu, cv, T.CAP_W, T.CAP_H, SLABS["topbar"])
for name, (cu, cv) in T.PREVIEW_BUTTONS.items():
    make_cap(name, cu, cv, T.PREVIEW_CAP_W, T.PREVIEW_CAP_H, SLABS["preview"])


def overlay_plane(name, rect, mat, parent, z=0.0007, coll=coll_ui):
    x, y, w, h = rect
    ob = new_obj(name, plane_mesh(name, px(w), px(h), rect_uv(*rect)), coll, (mat,))
    ob.location = m(x + w / 2, y + h / 2, z)
    ui_props(ob)
    bpy.context.view_layer.update()
    child_of(ob, parent)
    return ob


GLOW_OVERLAY = overlay_plane("Overlay_glow_row", T.GLOW_ROW, MAT_UI, SLABS["effects"])
VIEWER = overlay_plane("Comp_viewer", T.COMP_VIEW, MAT_COMP, SLABS["comp"], z=T.COMP_GLASS_Z)
VIEWER.data.polygons[0].vertices  # uv already 0..1 from rect_uv -> fix to full image
for loop_uv, uvc in zip(VIEWER.data.uv_layers[0].data, ((0, 0), (1, 0), (1, 1), (0, 1))):
    loop_uv.uv = uvc
TC1 = overlay_plane("Timecode_comp", T.TC_COMP, MAT_TC_COMP, SLABS["comp"], z=0.0006)
TC2 = overlay_plane("Timecode_timeline", T.TC_TL, MAT_TC_TL, SLABS["timeline"], z=0.0006)
for ob in (TC1, TC2):
    for loop_uv, uvc in zip(ob.data.uv_layers[0].data, ((0, 0), (1, 0), (1, 1), (0, 1))):
        loop_uv.uv = uvc


# ------------------------------------------------------------------ playhead + keyframe gems
def rounded_box(name, w, d, h, mat, coll, bevel):
    me = box_mesh(name, w, d, h, z0=h)
    ob = new_obj(name, me, coll, (mat, mat))
    add_bevel(ob, bevel, 3)
    set_smooth(ob)
    return ob


PLAYHEAD = bpy.data.objects.new("Playhead", None)
link(PLAYHEAD, coll_fx)
PLAYHEAD.location = m(T.comp_t_to_u(0), T.PLAYHEAD_HEAD_Y, 0)
ph_head = rounded_box("Playhead_head", px(13), px(15), T.PLAYHEAD_TOP_Z, MAT_PLAYHEAD, coll_fx, 0.004)
ph_head.parent = PLAYHEAD
line_len = px(T.UI_H - 6 - T.PLAYHEAD_HEAD_Y)
ph_line = rounded_box("Playhead_line", px(2.2), line_len, 0.0035, MAT_PLAYLINE, coll_fx, 0.0008)
ph_line.parent = PLAYHEAD
ph_line.location = (0, -line_len / 2, 0)
bpy.context.view_layer.update()
child_of(PLAYHEAD, SLABS["timeline"])

GEMS = []
for i, kt in enumerate(T.KEY_TIMES):
    bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=px(7), depth=T.KEY_GEM_TOP_Z,
                                        location=m(T.comp_t_to_u(kt), T.POSITION_ROW_Y, T.KEY_GEM_TOP_Z / 2))
    g = bpy.context.active_object
    g.name = "Keyframe_%d" % (i + 1)
    for c in g.users_collection:
        c.objects.unlink(g)
    link(g, coll_fx)
    g.data.materials.append(MAT_GEM)
    add_bevel(g, 0.0015, 2)
    bpy.context.view_layer.update()
    child_of(g, SLABS["timeline"])
    GEMS.append(g)


# ------------------------------------------------------------------ Clawd
U = T.UNIT_M
BODY_CZ = T.LEG_H + T.BODY_H / 2

CLAWD = bpy.data.objects.new("Clawd_root", None)       # feet position + yaw + pop scale
link(CLAWD, coll_hero)
CLAWD_SQ = bpy.data.objects.new("Clawd_squash", None)  # squash/stretch about the feet
link(CLAWD_SQ, coll_hero)
CLAWD_SQ.parent = CLAWD
CLAWD_TILT = bpy.data.objects.new("Clawd_tilt", None)  # flips, lean, roll about the body centre
link(CLAWD_TILT, coll_hero)
CLAWD_TILT.parent = CLAWD_SQ
CLAWD_TILT.location = (0, 0, BODY_CZ)


def part(name, w, d, h, loc, mat, bevel, parent=CLAWD_TILT, segs=4):
    me = box_mesh(name, w, d, h, z0=h / 2)
    ob = new_obj(name, me, coll_hero, (mat, mat))
    ob.location = loc
    add_bevel(ob, bevel, segs)
    set_smooth(ob)
    ob.parent = parent
    return ob


body = part("Clawd_body", T.BODY_W, T.BODY_D, T.BODY_H, (0, 0, 0), MAT_BODY, 1.6 * U, segs=6)
# side nubs (arms); the right one waves around a shoulder pivot
NUB_L = part("Clawd_nub_L", 1.8 * U, 2.4 * U, 2.4 * U, (-(T.BODY_W / 2 + 0.6 * U), 0, 0.4 * U), MAT_BODY, 0.8 * U)
SHOULDER_R = bpy.data.objects.new("Clawd_shoulder_R", None)
link(SHOULDER_R, coll_hero)
SHOULDER_R.parent = CLAWD_TILT
SHOULDER_R.location = (T.BODY_W / 2 - 0.3 * U, 0, 0.4 * U)
NUB_R = part("Clawd_nub_R", 1.8 * U, 2.4 * U, 2.4 * U, (0.9 * U, 0, 0), MAT_BODY, 0.8 * U, parent=SHOULDER_R)
# four short legs
LEGS = []
for sx in (-1, 1):
    for sy in (-1, 1):
        hip = bpy.data.objects.new("Clawd_hip_%s%s" % ("L" if sx < 0 else "R", "F" if sy < 0 else "B"), None)
        link(hip, coll_hero)
        hip.parent = CLAWD_TILT
        hip.location = (sx * (T.BODY_W / 2 - 2.0 * U), sy * (T.BODY_D / 2 - 1.3 * U), -T.BODY_H / 2 + 0.3 * U)
        leg = part(hip.name.replace("hip", "leg"), 1.5 * U, 1.5 * U, T.LEG_H + 0.4 * U,
                   (0, 0, -(T.LEG_H + 0.4 * U) / 2), MAT_BODY, 0.45 * U, parent=hip)
        LEGS.append(hip)
# eyes: narrow vertical slits on the front (-y) face, plus ^^ happy eyes for the ending
EYES_OPEN, EYES_HAPPY = [], []
for sx in (-1, 1):
    e = part("Clawd_eye_%s" % ("L" if sx < 0 else "R"), 0.75 * U, 0.5 * U, 1.9 * U,
             (sx * 2.6 * U, -T.BODY_D / 2 - 0.05 * U, 0.9 * U), MAT_EYE, 0.2 * U, segs=2)
    EYES_OPEN.append(e)
    for side in (-1, 1):  # two strokes form a ^
        h = part("Clawd_happy_%s%d" % ("L" if sx < 0 else "R", side), 1.3 * U, 0.5 * U, 0.45 * U,
                 (sx * 2.6 * U + side * 0.5 * U, -T.BODY_D / 2 - 0.05 * U, 0.9 * U), MAT_EYE, 0.15 * U, segs=2)
        h.rotation_euler = (0, side * math.radians(38), 0)
        EYES_HAPPY.append(h)

# flat card that peels off the comp (1.5 -> 2.0 s)
CARD_W = px(66)  # clawd_card.png covers comp rect 264 x 198 px = 66 x 49.5 UI px
CARD_H = CARD_W * IMG_CARD.size[1] / max(IMG_CARD.size[0], 1)
CARD = new_obj("Clawd_card", plane_mesh("card", CARD_W, CARD_H, origin="bottom"), coll_hero, (MAT_CARD,))
cu, cv = T.COMP_CENTER_UI
CARD_HINGE = m(cu, cv + (CARD_H / T.M_PER_PX) / 2, T.COMP_GLASS_Z + 0.0008)

# glow chip
CHIP = bpy.data.objects.new("Glow_chip", None)
link(CHIP, coll_fx)
chip_body = rounded_box("Glow_chip_body", 0.13, 0.049, 0.009, MAT_CHIP_BODY, coll_fx, 0.003)
chip_body.parent = CHIP
chip_body.location = (0, 0, -0.004)
chip_face = new_obj("Glow_chip_face", plane_mesh("chip_face", 0.125, 0.047), coll_fx, (MAT_CHIP_FACE,))
chip_face.parent = CHIP
chip_face.location = (0, 0, 0.0062)  # just above the body top (z 0.005)

# glass shards (seeded), burst from the comp on the pop
rng = random.Random(7)
SHARDS = []
for i in range(46):
    bm = bmesh.new()
    s = rng.uniform(0.012, 0.034)
    pts = [(rng.uniform(-s, s), rng.uniform(-s, s), 0) for _ in range(3)]
    vs = [bm.verts.new(p) for p in pts]
    f = bm.faces.new(vs)
    bmesh.ops.solidify(bm, geom=[f], thickness=0.0015)
    me = bpy.data.meshes.new("shard_%02d" % i)
    bm.to_mesh(me)
    bm.free()
    ob = new_obj("Shard_%02d" % i, me, coll_fx, (MAT_SHARD,))
    ang = rng.uniform(0, 2 * math.pi)
    speed = rng.uniform(0.5, 1.6)
    SHARDS.append(dict(ob=ob, vx=math.cos(ang) * speed * 0.8, vy=math.sin(ang) * speed * 0.55,
                       vz=rng.uniform(0.6, 1.7), spin=Vector((rng.uniform(-14, 14), rng.uniform(-14, 14), rng.uniform(-10, 10))),
                       r0=Vector((rng.uniform(0, 6), rng.uniform(0, 6), rng.uniform(0, 6))),
                       off=Vector((rng.uniform(-0.1, 0.1), rng.uniform(-0.06, 0.06), 0))))


# ------------------------------------------------------------------ world + lights
def build_world():
    w = bpy.data.worlds.new("Studio")
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = node(nt, "ShaderNodeOutputWorld", (900, 0))
    tc = node(nt, "ShaderNodeTexCoord", (-900, 0))
    sep = node(nt, "ShaderNodeSeparateXYZ", (-700, 0))
    nt.links.new(tc.outputs["Window"], sep.inputs[0])
    # screen-space warm gradient: brighter toward the upper right, like the reference backdrop
    mth = node(nt, "ShaderNodeMath", (-500, 0), operation="MULTIPLY_ADD")
    nt.links.new(sep.outputs["X"], mth.inputs[0])
    mth.inputs[1].default_value = 0.55
    mth.inputs[2].default_value = 0.0
    add = node(nt, "ShaderNodeMath", (-350, 0), operation="MULTIPLY_ADD")
    nt.links.new(sep.outputs["Y"], add.inputs[0])
    add.inputs[1].default_value = 0.45
    nt.links.new(mth.outputs[0], add.inputs[2])
    ramp = node(nt, "ShaderNodeValToRGB", (-150, 0))
    ramp.color_ramp.elements[0].position = 0.15
    ramp.color_ramp.elements[0].color = srgb("#140d0a")
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = srgb("#4a3427")
    nt.links.new(add.outputs[0], ramp.inputs[0])
    lp = node(nt, "ShaderNodeLightPath", (-150, 300))
    bg_cam = node(nt, "ShaderNodeBackground", (200, 100))
    nt.links.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
    bg_cam.inputs["Strength"].default_value = 1.0
    bg_light = node(nt, "ShaderNodeBackground", (200, -100))
    bg_light.inputs["Color"].default_value = srgb("#3a2a20")
    bg_light.inputs["Strength"].default_value = 0.35
    mix = node(nt, "ShaderNodeMixShader", (500, 0))
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs["Fac"])
    nt.links.new(bg_light.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])


build_world()


def area_light(name, loc, target, size, energy, color, glossy=False, size_y=None):
    ld = bpy.data.lights.new(name, "AREA")
    ld.shape = "RECTANGLE"
    ld.size = size
    ld.size_y = size_y or size
    ld.energy = energy
    ld.color = color
    ob = bpy.data.objects.new(name, ld)
    link(ob, coll_rig)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    ob.visible_glossy = glossy  # follow-up 2: keep big lights out of the glossy UI
    return ob


KEY = area_light("Key", (-1.6, -2.2, 2.6), (0, 0, 0), 2.0, 380, (1.0, 0.92, 0.84))
TOP = area_light("Top", (0.3, 0.4, 3.2), (0.2, 0.2, 0), 3.0, 260, (1.0, 0.95, 0.9))
RIM = area_light("Rim", (1.8, 2.6, 1.2), (0, 0, 0.1), 1.5, 380, (1.0, 0.78, 0.6))
# Small studio highlight that only Clawd receives (light linking), so he keeps a toy sheen.
SPEC = area_light("Clawd_spec", (-0.9, -1.6, 1.8), (0, 0, 0), 0.8, 90, (1.0, 0.96, 0.92), glossy=True)
try:
    SPEC.light_linking.receiver_collection = coll_hero
except AttributeError:
    pass
# warm spill from the comp once the glow is on; flash on Play
COMP_LIGHT_D = bpy.data.lights.new("Comp_spill", "AREA")
COMP_LIGHT_D.shape = "RECTANGLE"
COMP_LIGHT_D.size, COMP_LIGHT_D.size_y = px(T.COMP_VIEW[2]), px(T.COMP_VIEW[3])
COMP_LIGHT_D.color = (1.0, 0.55, 0.25)
COMP_LIGHT = bpy.data.objects.new("Comp_spill", COMP_LIGHT_D)
link(COMP_LIGHT, coll_rig)
COMP_LIGHT.location = m(*T.COMP_CENTER_UI, 0.01)
COMP_LIGHT.rotation_euler = (math.pi, 0, 0)  # facing +z? area lights emit along -Z; flip to face up
COMP_LIGHT.rotation_euler = (0, 0, 0)
COMP_LIGHT.scale = (1, 1, -1)
COMP_LIGHT.visible_glossy = False
COMP_LIGHT.visible_camera = False


# ------------------------------------------------------------------ camera
CAM_D = bpy.data.cameras.new("Camera")
CAM_D.lens = 35
CAM_D.sensor_width = 36
CAM_D.dof.use_dof = True
CAM_D.dof.aperture_fstop = F_STOP
CAM_D.clip_start = 0.01
CAM = bpy.data.objects.new("Camera", CAM_D)
link(CAM, coll_rig)
scene.camera = CAM
FOCUS = bpy.data.objects.new("Focus", None)
link(FOCUS, coll_rig)
CAM_D.dof.focus_object = FOCUS


def mascot_world(t):
    st = T.mascot_state(t)
    return m(st["u"], st["v"], st["z"]), st


def smoothed_mascot(t, half=0.25, n=9, z_keep=0.45):
    """Low-passed hero position for the camera target (no jitter on hops)."""
    acc = Vector((0, 0, 0))
    wsum = 0.0
    for i in range(n):
        dt = -half + 2 * half * i / (n - 1)
        w = math.cos(dt / half * math.pi / 2) ** 2 + 1e-3
        p, _ = mascot_world(min(max(t + dt, T.T_POP), T.DURATION))
        acc += p * w
        wsum += w
    p = acc / wsum
    p.z = p.z * z_keep + BODY_CZ
    return p


C = m(*T.COMP_CENTER_UI)
# (time, target-mode, target point or None, eye offset from target, lens)
# target-mode "fix" = fixed point, "hero" = smoothed Clawd.
CAM_KEYS = [
    (0.00, "fix", Vector((0.08, -0.02, 0.0)), Vector((-0.35, -2.35, 1.10)), 32),
    (1.30, "fix", C + Vector((0, 0.0, 0)), Vector((-0.10, -1.30, 0.80)), 35),
    (1.85, "fix", C + Vector((0, -0.02, 0.04)), Vector((-0.05, -0.80, 0.36)), 35),
    (2.15, "hero", None, Vector((0.10, -0.75, 0.30)), 35),
    (2.55, "hero", None, Vector((0.30, -0.62, 0.18)), 40),
    (3.45, "hero", None, Vector((0.26, -0.64, 0.19)), 40),
    (3.80, "hero", None, Vector((-0.10, -1.05, 0.42)), 32),
    (4.45, "hero", None, Vector((-0.28, -0.64, 0.28)), 38),
    (4.95, "hero", None, Vector((-0.28, -0.64, 0.28)), 38),
    (5.45, "fix", m(760, 300, 0.16), Vector((0.10, -1.25, 0.50)), 33),
    (6.00, "hero", None, Vector((-0.06, -0.62, 0.16)), 36),
    (7.55, "hero", None, Vector((-0.04, -0.62, 0.16)), 36),
    (8.00, "hero", None, Vector((0.02, -0.60, 0.15)), 36),
    (9.55, "hero", None, Vector((0.02, -0.60, 0.15)), 36),
    (10.00, "hero", None, Vector((-0.26, -0.64, 0.28)), 36),
    (10.40, "hero", None, Vector((0.10, -0.70, 0.28)), 35),
    (11.00, "fix", C + Vector((0.17, -0.03, 0)), Vector((0.10, -1.42, 0.74)), 35),
    (12.00, "fix", C + Vector((0.17, -0.02, 0)), Vector((0.12, -1.36, 0.70)), 35),
]


def cam_eval(t):
    keys = CAM_KEYS
    if t <= keys[0][0]:
        i = 0
        s = 0.0
    elif t >= keys[-1][0]:
        i = len(keys) - 2
        s = 1.0
    else:
        i = max(j for j in range(len(keys) - 1) if keys[j][0] <= t)
        s = (t - keys[i][0]) / (keys[i + 1][0] - keys[i][0])
    s = T.ease_in_out(s) if (keys[i + 1][0] - keys[i][0]) < 0.7 else T.smooth(s)  # short gaps = whips

    def target_of(k):
        return smoothed_mascot(t) if k[1] == "hero" else k[2]

    ka, kb = keys[i], keys[i + 1]
    tgt = target_of(ka).lerp(target_of(kb), s)
    off = ka[3].lerp(kb[3], s)
    lens = ka[4] + (kb[4] - ka[4]) * s
    for window, dz, back in CAM_LIFTS:  # rise and ease back with each high leap so its apex stays in frame
        w = lift_weight(t, window)
        tgt = tgt + Vector((0, 0, dz * w))
        off = off * (1 + back * w)
    return tgt + off, tgt, lens


# (window a, b, c, d; lift dz; pull-back): weight is exactly 0 for t <= a and t >= d. Camera keys are baked per
# frame and linearly interpolated, so motion blur reaches one frame past each window edge.
CAM_LIFTS = [
    ((2.0, 2.15, 2.36, 2.46), 0.09, 0.25),    # pop -> Type: keys f62-74 change, renders f61-75
    ((3.85, 4.05, 4.30, 4.42), 0.07, 0.20),   # Pen -> Glow flip: keys f117-133, renders f116-134
    ((9.60, 9.70, 9.86, 9.95), 0.07, 0.20),   # timeline -> Play leap: keys f290-299, renders f289-300
]


def lift_weight(t, window):
    a, b, c, d = window
    if t <= a or t >= d:
        return 0.0
    u = min((t - a) / (b - a), 1.0, (d - t) / (d - c))
    return u * u * u * (u * (6 * u - 15) + 10)


# ------------------------------------------------------------------ bake per frame
def key(obj, path, frame, index=-1):
    obj.keyframe_insert(data_path=path, frame=frame, index=index)


def key_prop(obj, prop, value, frame):
    obj[prop] = value
    obj.keyframe_insert(data_path='["%s"]' % prop, frame=frame)


panel_members = {name: [SLABS[name]] for name in SLABS}
for name, cap in CAPS.items():
    panel_members["preview" if name in T.PREVIEW_BUTTONS else "topbar"].append(cap)
panel_members["effects"].append(GLOW_OVERLAY)
panel_members["timeline"] += [TC2]
panel_members["comp"] += [VIEWER, TC1]

slab_rest = {name: ob.location.copy() for name, ob in SLABS.items()}
cap_rest = {name: ob.location.copy() for name, ob in CAPS.items()}
gem_rest = [g.location.copy() for g in GEMS]
ph_rest = PLAYHEAD.location.copy()

for f in range(1, T.FRAMES + 1):
    t = T.f2t(f)
    scene.frame_set(f) if False else None

    # panels: power-down then fall
    for name, ob in SLABS.items():
        power, drop, tilt = T.panel_fall(name, t)
        ob.location = slab_rest[name] + Vector((0, 0, -drop))
        ob.rotation_euler = (tilt, tilt * 0.35, 0)
        key(ob, "location", f)
        key(ob, "rotation_euler", f)
        for mem in panel_members[name]:
            key_prop(mem, "power", power, f)
    # caps: press + active state
    tool = T.active_tool(t)
    for name, ob in CAPS.items():
        ob.location = cap_rest[name] + Vector((0, 0, -T.CAP_PRESS * T.cap_press(name, t)))
        key(ob, "location", f, 2)
        if name == "Selection":
            act = 0.0 if tool == "Selection" else 1.0
        elif name in ("Type", "Rectangle", "Pen"):
            act = 1.0 if tool == name else 0.0
        elif name == "Play":
            act = 1.0 if t >= T.T_PLAY else 0.0
        else:
            act = 0.0
        key_prop(ob, "active", act, f)
    key_prop(GLOW_OVERLAY, "active", 1.0 if t >= T.T_GLOW_LAND else 0.0, f)

    # playhead + keyframe gems
    PLAYHEAD.location = ph_rest + Vector((px(T.comp_t_to_u(T.playhead_t(t)) - T.comp_t_to_u(0)), 0, 0))
    key(PLAYHEAD, "location", f, 0)
    for i, g in enumerate(GEMS):
        tk = T.T_KEYS[i]
        sc = T.ease_out_back(T.lin(t, tk, tk + 0.12)) if t >= tk else 0.0
        g.scale = (max(sc, 1e-4),) * 3
        key(g, "scale", f)

    # Clawd
    p, st = mascot_world(t)
    CLAWD.location = p
    CLAWD.rotation_euler = (0, 0, st["yaw"])
    vis = 1.0 if st["visible"] else 0.0
    sc = st["scale"] * vis if vis else 1e-4
    CLAWD.scale = (sc, sc, sc)
    key(CLAWD, "location", f)
    key(CLAWD, "rotation_euler", f)
    key(CLAWD, "scale", f)
    sq = st["squash"]
    CLAWD_SQ.scale = (1 + sq * 0.5, 1 + sq * 0.5, 1 - sq)
    key(CLAWD_SQ, "scale", f)
    CLAWD_TILT.rotation_euler = (-st["pitch"] + st["lean"], st["roll"], 0)
    key(CLAWD_TILT, "rotation_euler", f)
    SHOULDER_R.rotation_euler = (0, -T.wave_angle(t), 0)
    key(SHOULDER_R, "rotation_euler", f)
    for hip in LEGS:  # front-right leg kicks the chip
        k = st["kick"] if hip.name.endswith("LF") else 0.0
        hip.rotation_euler = (-1.1 * k, 0, 0)
        key(hip, "rotation_euler", f)
    happy = st["eyes"] == "happy"
    for e in EYES_OPEN:
        e.hide_render = happy
        e.hide_viewport = happy
        key(e, "hide_render", f)
        key(e, "hide_viewport", f)
    for e in EYES_HAPPY:
        e.hide_render = not happy
        e.hide_viewport = not happy
        key(e, "hide_render", f)
        key(e, "hide_viewport", f)

    # peel card
    cs = T.card_state(t)
    CARD.location = CARD_HINGE + Vector((0, 0, cs["lift"]))
    CARD.rotation_euler = (cs["angle"], 0, 0)
    s = cs["scale"] if cs["visible"] else 1e-4
    CARD.scale = (s, s, s)
    key(CARD, "location", f)
    key(CARD, "rotation_euler", f)
    key(CARD, "scale", f)

    # glow chip
    ch = T.chip_state(t)
    if ch["visible"]:
        CHIP.location = m(ch["u"], ch["v"], ch["z"])
        stand = 1.05 * T.smooth(T.lin(t, T.T_GLOW_LAND, T.T_GLOW_LAND + 0.18))  # card stands up to face the camera
        CHIP.rotation_euler = (stand + ch["tilt"], 0, ch["spin"])
        CHIP.scale = (ch["scale"],) * 3
    else:
        CHIP.scale = (1e-4,) * 3
    key(CHIP, "location", f)
    key(CHIP, "rotation_euler", f)
    key(CHIP, "scale", f)

    # shards: ballistic from the comp centre, fade out by scaling
    age = t - T.T_POP
    for sh in SHARDS:
        ob = sh["ob"]
        if 0 <= age < 1.2:
            pos = C + sh["off"] + Vector((sh["vx"] * age, sh["vy"] * age, 0.01 + sh["vz"] * age - 2.2 * age * age))
            ob.location = pos
            ob.rotation_euler = Euler(tuple(sh["r0"] + sh["spin"] * age))
            k = 1.0 - T.smooth(T.lin(age, 0.7, 1.2))
            ob.scale = (max(k, 1e-4),) * 3
        else:
            ob.location = C
            ob.scale = (1e-4,) * 3
        key(ob, "location", f)
        key(ob, "rotation_euler", f)
        key(ob, "scale", f)

    # comp spill light: glow on + Play flash
    cst = T.comp_state(t)
    COMP_LIGHT_D.energy = 6.0 * cst["glow"] + 60.0 * cst["flash"] + 8.0 * cst["shimmer"]
    COMP_LIGHT_D.keyframe_insert("energy", frame=f)

    # camera
    eye, tgt, lens = cam_eval(t)
    CAM.location = eye
    CAM.rotation_euler = (tgt - eye).to_track_quat("-Z", "Y").to_euler()
    CAM_D.lens = lens
    key(CAM, "location", f)
    key(CAM, "rotation_euler", f)
    CAM_D.keyframe_insert("lens", frame=f)
    FOCUS.location = (p + Vector((0, 0, BODY_CZ))) if st["visible"] else (C if t < 2 else tgt)
    key(FOCUS, "location", f)

# Linear interpolation everywhere: values are already sampled per frame, so no Bezier overshoot.
for action in bpy.data.actions:
    for fc in getattr(action, "fcurves", []):
        for kp in fc.keyframe_points:
            kp.interpolation = "LINEAR"
try:  # Blender 5 layered actions
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for kp in fc.keyframe_points:
                            kp.interpolation = "CONSTANT" if fc.data_path.startswith(("hide", '["active"]')) else "LINEAR"
except AttributeError:
    pass


# ------------------------------------------------------------------ render settings
scene.render.engine = "CYCLES"
cy = scene.cycles
cy.device = "GPU"
cy.samples = 96
cy.use_adaptive_sampling = True
cy.adaptive_threshold = 0.03
cy.use_denoising = True
cy.denoiser = "OPENIMAGEDENOISE"
cy.max_bounces = 4
cy.diffuse_bounces = 2
cy.glossy_bounces = 2
cy.transmission_bounces = 2
cy.transparent_max_bounces = 4
cy.caustics_reflective = False
cy.caustics_refractive = False
cy.blur_glossy = 1.0
scene.render.use_motion_blur = True
scene.render.motion_blur_shutter = 0.5
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Medium High Contrast"
except TypeError:
    pass
scene.view_settings.exposure = EXPOSURE
scene.render.film_transparent = False
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.render.filepath = os.path.join(ROOT, "build", "frames", "")
scene.render.use_persistent_data = True


def setup_compositor():
    """Bloom on the screens (Glare/Bloom). Blender 5 uses compositing node groups."""
    try:
        tree = bpy.data.node_groups.new("Bloom", "CompositorNodeTree")
        scene.compositing_node_group = tree
        rl = tree.nodes.new("CompositorNodeRLayers")
        glare = tree.nodes.new("CompositorNodeGlare")
        out = tree.nodes.new("NodeGroupOutput")
        tree.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
        tree.links.new(glare.outputs["Image"], out.inputs[0])
        _set_glare(glare)
    except (AttributeError, TypeError, RuntimeError):
        scene.use_nodes = True
        tree = scene.node_tree
        tree.nodes.clear()
        rl = tree.nodes.new("CompositorNodeRLayers")
        glare = tree.nodes.new("CompositorNodeGlare")
        comp = tree.nodes.new("CompositorNodeComposite")
        tree.links.new(rl.outputs["Image"], glare.inputs["Image"])
        tree.links.new(glare.outputs["Image"], comp.inputs["Image"])
        _set_glare(glare)


def _set_glare(glare):
    vals = {"Type": "Bloom", "Quality": "High", "Threshold": 0.85, "Size": 0.55, "Strength": 0.35,
            "Saturation": 1.0}
    for k, v in vals.items():
        if k in glare.inputs:
            try:
                glare.inputs[k].default_value = v
                continue
            except TypeError:
                pass
        attr = {"Type": "glare_type", "Quality": "quality", "Threshold": "threshold", "Size": "size",
                "Strength": "strength"}.get(k)
        if attr and hasattr(glare, attr):
            try:
                if attr == "glare_type":
                    setattr(glare, attr, "BLOOM")
                elif attr == "quality":
                    setattr(glare, attr, "HIGH")
                elif attr == "size":
                    setattr(glare, attr, 7)
                else:
                    setattr(glare, attr, v)
            except (TypeError, ValueError):
                pass


setup_compositor()
scene.frame_set(1)
bpy.ops.file.pack_all() if False else None
bpy.ops.wm.save_as_mainfile(filepath=BLEND_OUT, relative_remap=True)
print("saved", BLEND_OUT)
