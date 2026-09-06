# MeshSat field kit V2, concept renders, Blender scene for the Peli 1450 (5 Sep 2026, appendix 32.40 items 4 to 9 and 32.42): Peli's own 1451-931 bodies
# (STL from the vendor STEP; a modelled fallback with the 1450 numbers), the 1450PF frame, the 3 mm aluminium face plate (v2/cad/face_plate.py) with the
# backer board C6 under it, the board stack (E4, E5, A21, D7, B15), the battery row along the west end wall, the nine end-wall antennas at Z 88 with
# their pigtails, the upright connector plate on the back wall with the shore and USB cables plugged, rulers and a 50 mm floor grid in every view.
# Case frame in mm: X along the long axis, +Y = back wall (hinge), Z up from the cavity floor.
# Run headless: blender -b -P scene.py -- <out dir> [views...]   (views: a name from VIEWS, "orbit", "closed", "details", "all")
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
R = os.path.expanduser("~/render3d"); STL = R + "/stl"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0] if args else R + "/out1450"; VIEWS_ASKED = args[1:] or ["all"]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.unit_settings.system = "METRIC"; S.unit_settings.scale_length = 0.001; S.unit_settings.length_unit = "MILLIMETERS"
for cand in (os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ecad", "tools"), os.path.expanduser("~/gitlab/products/meshsat/meshsat-fieldkit/v2/ecad/tools"), R):
    if os.path.exists(os.path.join(cand, "panel1450.py")): sys.path.insert(0, cand); break
import panel1450 as P
# ------------------------------------------------------------------ the 1450's numbers (appendix 32.41 and 32.42; Peli drawing 1451-931 and the STEP)
BW, BL = 411.0, 329.0                 # outer
RIM = 109.4                           # the rim (frame seat) above the cavity floor
LIDH = 45.5                           # lid outer height above the rim
FLOOR_W, FLOOR_L, RIM_W, RIM_L = 360.0, 246.0, 371.0, 259.0
SKIRT = (378.4, 262.5, 8.1)           # the frame skirt ring the rim step takes
FACE = P.FACE_TOP_Z                   # 101.4, the plate's top face on the frame lip
PLATE_UNDER = P.PLATE_UNDER_Z         # 98.4
BACKER_TOP = PLATE_UNDER - P.BACKER_GAP; BACKER_Z = BACKER_TOP - P.BACKER_T   # 88.4, 86.8
SMA_Z = 88.0
WEST = [(-72.0, "VHF"), (-24.0, "WIFI 2.4"), (24.0, "GNSS"), (72.0, "SDR")]
EAST = [(-96.0, "LTE"), (-48.0, "IRIDIUM"), (-24.0, "LORA"), (48.0, "WIFI P2P A"), (96.0, "WIFI P2P B")]   # LORA off Y 0: the 1450 end wall carries a nub there (drawing 1451-931, 6 Sep 2026)
RIBS_X = (-170.0, -95.0, -18.0, 60.0, 137.0)
CPLATE = dict(cx=-56.0, cz=54.0, w=54.0, h=82.0)
GROUND = -8.0                         # the ground plane under the feet pads (the shell's bottom at -5, pads 3 mm)
# ------------------------------------------------------------------ materials
def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=0.0, bump=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; n = nt.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*rgb, 1.0); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        n.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND"
    if emit: n.inputs["Emission Strength"].default_value = emit; n.inputs["Emission Color"].default_value = (*rgb, 1.0)
    if bump:      # fine plastic grain
        tex = nt.nodes.new("ShaderNodeTexNoise"); tex.inputs["Scale"].default_value = 90.0; tex.inputs["Detail"].default_value = 6.0
        bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = bump; bm.inputs["Distance"].default_value = 0.4
        nt.links.new(tex.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], n.inputs["Normal"])
    return m
M = dict(orange=mat("peli_orange", (0.97, 0.30, 0.015), 0.6, bump=0.35), orange2=mat("peli_orange_dark", (0.86, 0.25, 0.012), 0.68, bump=0.3),
         black=mat("matte_black", (0.02, 0.02, 0.02), 0.65, bump=0.2), mask=mat("mask_black", (0.03, 0.03, 0.035), 0.45), anod=mat("anodised", (0.05, 0.05, 0.055), 0.42, 0.55),
         gold=mat("enig", (0.95, 0.75, 0.30), 0.35, 1.0), steel=mat("steel", (0.62, 0.62, 0.64), 0.28, 1.0), steel_dark=mat("steel_dark", (0.3, 0.3, 0.32), 0.35, 1.0),
         alu=mat("aluminium", (0.75, 0.76, 0.78), 0.4, 1.0), chrome=mat("chrome", (0.85, 0.85, 0.87), 0.12, 1.0),
         glass=mat("glass", (0.6, 0.7, 0.8), 0.05, 0.0, 0.18), lens=mat("lens", (0.85, 0.88, 0.92), 0.05, 0.0, 0.2), paper=mat("epaper", (0.92, 0.92, 0.9), 0.75),
         green=mat("led_green", (0.15, 0.95, 0.25), 0.3, 0.0, 1.0, 3.0), amber=mat("led_amber", (1.0, 0.62, 0.06), 0.3, 0.0, 1.0, 3.0), redled=mat("led_red", (1.0, 0.1, 0.05), 0.3, 0.0, 1.0, 3.0),
         white=mat("plastic_white", (0.9, 0.9, 0.88), 0.5), rubber=mat("rubber", (0.04, 0.04, 0.04), 0.9, bump=0.3), dark=mat("dark_plastic", (0.08, 0.08, 0.09), 0.6),
         red=mat("red", (0.8, 0.05, 0.05), 0.4), pcb=mat("pcb_green", (0.05, 0.25, 0.1), 0.5), tin=mat("tin", (0.7, 0.72, 0.72), 0.3, 1.0), gray=mat("gray_plastic", (0.35, 0.35, 0.37), 0.6),
         ledoff=mat("led_off", (0.55, 0.55, 0.5), 0.25, 0.0, 0.7), wire_red=mat("wire_red", (0.7, 0.05, 0.05), 0.5), wire_blk=mat("wire_black", (0.05, 0.05, 0.05), 0.5), ribbon=mat("ribbon", (0.4, 0.4, 0.42), 0.6),
         coax=mat("coax", (0.55, 0.45, 0.25), 0.6), usb=mat("usb_cable", (0.2, 0.2, 0.22), 0.55), ruler=mat("ruler", (0.96, 0.96, 0.9), 0.6), tick=mat("tick", (0.02, 0.02, 0.02), 0.6), grid=mat("grid", (0.42, 0.42, 0.45), 0.8))
def assign(o, m):
    o.data.materials.clear(); o.data.materials.append(m)
# ------------------------------------------------------------------ primitives (mm)
def box(name, size, at, m, rot=(0, 0, 0), bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=at); o = bpy.context.object; o.name = name; o.scale = size; o.rotation_euler = rot; assign(o, m)
    if bevel:
        bpy.ops.object.transform_apply(scale=True); md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 4
    return o
def cyl(name, d, h, at, m, axis="Z", verts=64, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=h, location=at, vertices=verts); o = bpy.context.object; o.name = name
    if axis == "X": o.rotation_euler = (0, math.pi / 2, 0)
    elif axis == "Y": o.rotation_euler = (math.pi / 2, 0, 0)
    assign(o, m)
    if bevel: md = o.modifiers.new("bev", "BEVEL"); md.width = bevel; md.segments = 3
    return o
def tube(name, p1, p2, d, m):
    """A cylinder from p1 to p2 (cables and pigtails)."""
    a, b = Vector(p1), Vector(p2); v = b - a; L = v.length
    bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=L, location=(a + b) / 2, vertices=24); o = bpy.context.object; o.name = name
    o.rotation_euler = v.to_track_quat("Z", "Y").to_euler(); assign(o, m); return o
def cone(name, d1, d2, h, at, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=d1 / 2, radius2=d2 / 2, depth=h, location=at, vertices=48); o = bpy.context.object; o.name = name; o.rotation_euler = rot; assign(o, m); return o
def torus(name, R_, r_, at, m):
    bpy.ops.mesh.primitive_torus_add(major_radius=R_, minor_radius=r_, location=at, major_segments=64, minor_segments=16); o = bpy.context.object; o.name = name; assign(o, m); return o
def sphere(name, d, at, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=d / 2, location=at, segments=48, ring_count=24); o = bpy.context.object; o.name = name; assign(o, m)
    for p in o.data.polygons: p.use_smooth = True
    return o
def label(name, txt, at, size, m, rot=(0, 0, 0), align="CENTER"):
    bpy.ops.object.text_add(location=at); o = bpy.context.object; o.name = name; o.data.body = txt; o.data.size = size; o.data.align_x = align; o.rotation_euler = rot
    o.data.extrude = 0.04; assign(o, m); return o
def rounded_box(name, w, l, h, r, at, m, top_scale=(1.0, 1.0), segs=10):
    """A rounded-rectangle prism (radius r on the vertical edges) from z=0 to h at `at`; top_scale lofts the top outline (draft)."""
    bm = bmesh.new(); pts = []
    for cx, cy, a0 in ((w / 2 - r, l / 2 - r, 0), (-w / 2 + r, l / 2 - r, 90), (-w / 2 + r, -l / 2 + r, 180), (w / 2 - r, -l / 2 + r, 270)):
        for k in range(segs + 1):
            a = math.radians(a0 + 90 * k / segs); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    bot = [bm.verts.new((x, y, 0.0)) for x, y in pts]; top = [bm.verts.new((x * top_scale[0], y * top_scale[1], h)) for x, y in pts]
    n = len(pts); bm.faces.new(bot[::-1]); bm.faces.new(top)
    for i in range(n): bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i]))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); S.collection.objects.link(o); o.location = at; assign(o, m)
    for p in me.polygons: p.use_smooth = True
    if hasattr(me, "use_auto_smooth"): me.use_auto_smooth = True
    return o
def cut(o, tool, op="DIFFERENCE"):
    md = o.modifiers.new("bool", "BOOLEAN"); md.operation = op; md.object = tool; md.solver = "EXACT"
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=md.name); bpy.data.objects.remove(tool, do_unlink=True)
# ------------------------------------------------------------------ imports
def bbox(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (min(p.x for p in pts), max(p.x for p in pts), min(p.y for p in pts), max(p.y for p in pts), min(p.z for p in pts), max(p.z for p in pts))
def import_stl(name, fn, m, matrix=None, fit=None, smooth=False):
    """fit=(centre_xy, anchor, z): after the import the mesh is moved so its XY centre is 0 and its min ('min') or max ('max') Z sits at z."""
    fp = os.path.join(STL, fn)
    if not os.path.exists(fp): print("MISSING STL", fp, flush=True); return None
    bpy.ops.wm.stl_import(filepath=fp) if hasattr(bpy.ops.wm, "stl_import") else bpy.ops.import_mesh.stl(filepath=fp)
    o = bpy.context.selected_objects[0]; o.name = name; o.matrix_world = matrix or Matrix.Identity(4); assign(o, m)
    if fit:
        centre_xy, anchor, z = fit; x0, x1, y0, y1, z0, z1 = bbox(o)
        dx, dy = (-(x0 + x1) / 2, -(y0 + y1) / 2) if centre_xy else (0.0, 0.0); dz = z - (z0 if anchor == "min" else z1)
        o.matrix_world = Matrix.Translation((dx, dy, dz)) @ o.matrix_world
    for p in o.data.polygons: p.use_smooth = smooth
    x0, x1, y0, y1, z0, z1 = bbox(o); print("STL %-14s x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f (%d faces)" % (name, x0, x1, y0, y1, z0, z1, len(o.data.polygons)), flush=True)
    return o
def import_board(name, fn, z, extra=Matrix.Identity(4), hide_names=()):
    """A KiCad GLB exported with the case-frame user origin (case mm after the import, board bottom at z 0): mask matte black, pads gold, models dark."""
    fp = os.path.join(R, "glb", fn) if os.path.exists(os.path.join(R, "glb", fn)) else os.path.join(R, fn)
    if not os.path.exists(fp): print("MISSING GLB", fp, flush=True); return None
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=fp); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name, None); S.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    root.matrix_world = extra @ Matrix.Translation((0, 0, z))
    for o in new:
        if o.type != "MESH": continue
        if o.name.split(".")[0] in hide_names: o.hide_render = True; o.hide_viewport = True; continue
        if not o.material_slots or all(s.material is None for s in o.material_slots):
            o.data.materials.clear(); o.data.materials.append(M["white"] if o.name.startswith(("J_", "TP")) else M["dark"]); continue
        for slot in o.material_slots:
            mm = slot.material
            if not mm or not mm.use_nodes: continue
            n = mm.node_tree.nodes.get("Principled BSDF")
            if not n: continue
            r, g, b = n.inputs["Base Color"].default_value[:3]
            if g > r * 1.3 and g > b * 1.3: slot.material = M["mask"]
            elif r > 0.6 and g > 0.4 and b < 0.35 and r > b * 1.8: slot.material = M["gold"]
            elif r > 0.85 and g > 0.85 and b > 0.85: slot.material = M["white"]
    return root
def textured(o, image_fn, strength=0.0):
    """Image on an object's material (cube projection scaled to the object)."""
    img = bpy.data.images.load(os.path.join(R, image_fn)); m = bpy.data.materials.new(o.name + "_tex"); m.use_nodes = True; nt = m.node_tree; pr = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img; nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"])
    pr.inputs["Roughness"].default_value = 0.35 if strength else 0.8
    if strength: nt.links.new(tex.outputs["Color"], pr.inputs["Emission Color"]); pr.inputs["Emission Strength"].default_value = strength
    assign(o, m); bpy.context.view_layer.objects.active = o; bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.cube_project(cube_size=1.0, scale_to_bounds=True); bpy.ops.object.mode_set(mode="OBJECT")
# ------------------------------------------------------------------ the Peli 1450 from its customer drawing 1451-931 (6 Sep 2026 16:30, owner: "add the details of the
# case properly"). Peli's STEP bodies are envelopes (a slab, a drafted block and a rim ring; 75 and 39 faces), so the shell is modelled from the drawing's views and
# sections (`vendor/peli/1450/`): outer 375 x 261 at the bottom drafting to 383 x 269 under the seam flange, the flange ring 411 x 291 x 12 on each half, lid 45.5
# high with a 259 deep top; lid ladder rails at X +-114 and +-156 with rungs at Y +78 and -82; label recess 85 x 50 R3; two double-throw latches at X +-135 in
# 43 mm channels; padlock protectors at the front corners; the handle pocket 220 x 78 in the front wall with the U handle on pivots at X +-76 and the valve at
# (-16, 62); hinge blocks at X +-124 with four knuckles at 22 mm pitch; four feet pads 38 x 23 at (+-132, +-62); three nubs per end wall on each half (Y 0, +-83.5).
BODY_W0, BODY_L0 = 375.0, 261.0; BODY_W1, BODY_L1 = 383.0, 269.0; FL_W, FL_L, FL_H = 411.0, 291.0, 12.0; BOT = -5.0; CR = 24.0
def wall_x(z): return BODY_W0 / 2 + (BODY_W1 - BODY_W0) / 2 * (z - BOT) / (RIM - FL_H - BOT)     # the end walls' outer half-width at height z (draft)
def wall_y(z): return BODY_L0 / 2 + (BODY_L1 - BODY_L0) / 2 * (z - BOT) / (RIM - FL_H - BOT)     # the long walls' outer half-depth at height z
def lid_y(z): return BODY_L1 / 2 - (BODY_L1 - BODY_L0 + 2) / 2 * (z - (RIM + FL_H)) / (LIDH - FL_H)
def smooth_by_angle(o, deg=32.0):
    bpy.context.view_layer.objects.active = o; o.select_set(True)
    try: bpy.ops.object.shade_smooth_by_angle(angle=math.radians(deg))
    except Exception:
        try: bpy.ops.object.shade_smooth(use_auto_smooth=True, auto_smooth_angle=math.radians(deg))
        except Exception: bpy.ops.object.shade_smooth()
    o.select_set(False)
def bevel(o, width, segs=3, deg=35.0):
    md = o.modifiers.new("bev", "BEVEL"); md.width = width; md.segments = segs; md.limit_method = "ANGLE"; md.angle_limit = math.radians(deg)
    bpy.context.view_layer.objects.active = o; bpy.ops.object.modifier_apply(modifier=md.name)
# the base: drafted shell plus its flange, the cavity and the frame seat cut out, bottom edges rounded
base = rounded_box("case_base", BODY_W0, BODY_L0, RIM - FL_H - BOT + 0.2, CR, (0, 0, BOT), M["orange"], top_scale=(BODY_W1 / BODY_W0, BODY_L1 / BODY_L0))
cut(base, rounded_box("case_base_flange", FL_W, FL_L, FL_H, 32.0, (0, 0, RIM - FL_H), M["orange"]), op="UNION")
bevel(base, 5.0)
cut(base, rounded_box("cavity", FLOOR_W, FLOOR_L, RIM + 5.0, 10.0, (0, 0, 0.0), M["orange"], top_scale=(RIM_W / FLOOR_W, RIM_L / FLOOR_L)))
cut(base, rounded_box("rim_step", SKIRT[0], SKIRT[1], SKIRT[2] + 1.0, 10.0, (0, 0, RIM - SKIRT[2]), M["orange"]))
smooth_by_angle(base)
# the lid: flange, drafted body, the top edges rounded, the inside hollowed, the label recess on top and the nameplate recess on its front
LID_TOP = RIM + LIDH
lid = rounded_box("case_lid", BODY_W1, BODY_L1, LIDH - FL_H, CR, (0, 0, RIM + FL_H - 0.2), M["orange"], top_scale=(BODY_W0 / BODY_W1, (BODY_L0 - 2) / BODY_L1))
cut(lid, rounded_box("case_lid_flange", FL_W, FL_L, FL_H, 32.0, (0, 0, RIM), M["orange"]), op="UNION")
bevel(lid, 6.0)
cut(lid, rounded_box("lid_cavity", RIM_W, RIM_L, LIDH - 6.0, 10.0, (0, 0, RIM - 1.0), M["orange"], top_scale=(0.95, 0.94)))
cut(lid, rounded_box("label_tool", 85.0, 50.0, 4.0, 3.0, (-59.0, 77.0, LID_TOP - 1.2), M["orange"]))
cut(lid, box("nameplate_tool", (114.0, 6.0, 18.0), (0, -lid_y(RIM + 27.0), RIM + 27.0), M["orange"]))
smooth_by_angle(lid)
label("peli_text", "1450", (0, -lid_y(RIM + 27.0) + 3.2, RIM + 22.0), 9.0, M["orange2"], rot=(math.pi / 2, 0, 0))
for sx in (-1, 1):
    for rx in (114.0, 156.0): box("rail_%d_%d" % (sx, rx), (6.0, 250.0, 6.0), (sx * rx, -3.0, LID_TOP + 2.5), M["orange"], bevel=1.5)
    for ry in (78.0, -82.0): box("rung_%d_%d" % (sx, ry), (48.0, 6.0, 6.0), (sx * 135.0, ry, LID_TOP + 2.5), M["orange"], bevel=1.5)
# the front wall: handle pocket (a tray set into the shell), the U handle folded into it, the valve on the pocket floor
FY = -FL_L / 2
cut(base, box("pocket_tool", (220.0, 20.0, 78.0), (0, -wall_y(53.0) + 0.5, 53.0), M["orange"]))
tray = box("pocket_tray", (224.0, 10.0, 82.0), (0, -126.5, 53.0), M["orange"]); cut(tray, box("pocket_in", (220.0, 9.0, 78.0), (0, -128.0, 53.0), M["orange"]))
for sx in (-1, 1):
    cyl("handle_pivot_%d" % sx, 12.0, 9.0, (sx * 76.0, -128.0, 84.0), M["black"], axis="Y"); box("handle_arm_%d" % sx, (12.0, 7.0, 58.0), (sx * 76.0, -128.0, 55.0), M["black"], bevel=2.0)
box("handle_grip", (152.0, 9.0, 16.0), (0, -128.0, 30.0), M["black"], bevel=4.0)
for k in (-40, -20, 0, 20, 40): box("handle_rib_%d" % k, (7.0, 2.5, 12.0), (k, -132.8, 30.0), M["black"], bevel=0.8)
cyl("valve", 26.0, 5.0, (-16.0, -126.0, 62.0), M["black"], axis="Y", bevel=1.2); cyl("valve_cap", 19.0, 2.0, (-16.0, -129.5, 62.0), M["steel_dark"], axis="Y")
# the latches: channel rails on both halves, the keeper block on the flange, the lever on the lid with its pin
for sx in (-1, 1):
    x = sx * 135.0
    for k in (-21.5, 21.5):
        box("latch_rail_b_%d_%d" % (sx, k), (6.0, 5.0, RIM - FL_H - 16.0), (x + k, -wall_y(57.0) - 1.5, (RIM - FL_H + 16.0) / 2), M["orange"], bevel=1.2)
        box("latch_lidrail_%d_%d" % (sx, k), (6.0, 5.0, LIDH - FL_H - 10.0), (x + k, -lid_y(RIM + 28.0) - 1.5, (RIM + FL_H + 2.0 + LID_TOP - 8.0) / 2), M["orange"], bevel=1.2)
    box("latch_keeper_%d" % sx, (50.0, 6.0, FL_H), (x, FY - 3.0, RIM - FL_H / 2), M["orange2"], bevel=2.0); box("latch_lidkeep_%d" % sx, (50.0, 6.0, FL_H), (x, FY - 3.0, RIM + FL_H / 2), M["orange2"], bevel=2.0)
    box("latch_lever_%d" % sx, (36.0, 9.0, 66.0), (x, FY - 10.5, RIM - 6.0), M["orange2"], bevel=4.0); box("latch_pivot_%d" % sx, (40.0, 10.0, 12.0), (x, FY - 9.0, RIM + 33.0), M["orange2"], bevel=2.5)
    cyl("latch_pin_%d" % sx, 5.0, 46.0, (x, FY - 8.0, RIM + 38.0), M["steel_dark"], axis="X"); box("latch_notch_%d" % sx, (22.0, 3.0, 5.0), (x, FY - 15.0, RIM - 34.0), M["black"], bevel=1.0)
# padlock protectors at the front corners (section C-C), split at the seam, the hasp hole through both halves
for sx in (-1, 1):
    x = sx * 176.0
    box("padlock_b_%d" % sx, (44.0, 14.0, FL_H), (x, FY - 4.0, RIM - FL_H / 2), M["orange2"], bevel=4.5); cyl("padlock_hole_b_%d" % sx, 10.0, FL_H + 0.4, (x, FY - 6.0, RIM - FL_H / 2), M["black"])
    box("padlock_lid_%d" % sx, (44.0, 14.0, FL_H), (x, FY - 4.0, RIM + FL_H / 2), M["orange2"], bevel=4.5); cyl("padlock_lidhole_%d" % sx, 10.0, FL_H + 0.4, (x, FY - 6.0, RIM + FL_H / 2), M["black"])
# the hinge: two blocks behind the flange, four knuckles on the base and three lugs on the lid around one pin
HINGE_Y = FL_L / 2 + 8.0
for sx in (-1, 1):
    x = sx * 124.0
    box("hinge_block_%d" % sx, (69.0, 16.0, 14.0), (x, HINGE_Y, RIM - 7.0), M["orange2"], bevel=3.0)
    for k in (-33, -11, 11, 33): box("hinge_knuckle_%d_%d" % (sx, k), (5.0, 16.0, 12.0), (x + k, HINGE_Y, RIM + 6.0), M["orange2"], bevel=1.5)
    for k in (-22, 0, 22): box("hinge_lug_%d_%d" % (sx, k), (5.0, 16.0, 12.0), (x + k, HINGE_Y, RIM + 6.0), M["orange2"], bevel=1.5)
    cyl("hinge_pin_%d" % sx, 8.0, 74.0, (x, HINGE_Y, RIM + 6.0), M["steel_dark"], axis="X")
# feet pads and the end-wall nubs (three per half, at the seam line of the drawing: Y 0 and +-83.5)
FEET_Z = BOT - 1.5
for sx in (-1, 1):
    for sy in (-1, 1): box("foot_%d_%d" % (sx, sy), (38.0, 23.0, 3.0), (sx * 132.0, sy * 62.0, FEET_Z), M["orange2"], bevel=1.0)
    for y in (-83.5, 0.0, 83.5):
        sphere("nub_b_%d_%d" % (sx, y), 9.0, (sx * (wall_x(83.0) + 1.0), y, 83.0), M["orange"]); sphere("nub_l_%d_%d" % (sx, y), 9.0, (sx * (wall_x(RIM - FL_H) + 1.0), y, RIM + FL_H + 8.0), M["orange"])
# the inner ribs of the long walls (1451-931 section B-B): the connector plate stands between the ribs at X -95 and -18
for sy in (-1, 1):
    for x in RIBS_X: box("case_rib_in_%d_%d" % (sy, x), (5.0, 5.0, 94.0), (x, sy * (FLOOR_L / 2 + 2.0), 47.0), M["orange"])
CASE = [o for o in bpy.data.objects if o.name.startswith(("case_", "rail_", "rung_", "foot_", "padlock", "latch_", "handle_", "valve", "hinge_", "peli_text", "nub_", "pocket_"))]
LID = [o for o in CASE if o.name.startswith(("case_lid", "rail_", "rung_", "latch_lever", "latch_pivot", "latch_pin", "latch_notch", "latch_lidrail", "latch_lidkeep", "padlock_lid", "hinge_lug", "hinge_pin", "nub_l_", "peli_text"))]
hinge = Vector((0, HINGE_Y, RIM + 6.0)); CLOSED = {o.name: o.matrix_world.copy() for o in LID}
def set_lid(open_):
    for o in LID:
        base_m = CLOSED[o.name]
        o.matrix_world = (Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-100), 4, "X") @ Matrix.Translation(-hinge) @ base_m) if open_ else base_m
frame = import_stl("panel_frame", "frame1450.stl", M["black"], fit=(True, "max", RIM))
# ------------------------------------------------------------------ the back wall: the upright connector plate between the ribs, the shore and USB receptacles, both cables plugged
WALL_Y = wall_y(54.0)   # the long wall's outer face at the plate's mid-height (the drafted shell of the drawing)
box("conn_plate", (CPLATE["w"], 3, CPLATE["h"]), (CPLATE["cx"], WALL_Y + 1.5, CPLATE["cz"]), M["alu"])
for (sx, sz) in ((-79, 82), (-33, 82), (-79, 54), (-33, 54), (-79, 26), (-33, 26)): cyl("cplate_screw_%d_%d" % (sx, sz), 7.0, 1.5, (sx, WALL_Y + 3.75, sz), M["steel"], axis="Y", verts=6)
for z, d, fl, nm, cm, cd in ((34, 19.05, 28.9, "shore", M["wire_blk"], 8.0), (74, 23.01, 31.29, "usb", M["usb"], 6.0)):
    box("recept_flange_" + nm, (fl, 4, fl), (CPLATE["cx"], WALL_Y + 5, z), M["steel"], bevel=1.0); cyl("recept_" + nm, d + 4, 14, (CPLATE["cx"], WALL_Y + 12, z), M["steel_dark"], axis="Y")
    cyl("plug_" + nm, d + 8, 26, (CPLATE["cx"], WALL_Y + 26, z), M["dark"], axis="Y", bevel=1.0); cyl("plug_nut_" + nm, d + 10, 6, (CPLATE["cx"], WALL_Y + 16, z), M["steel_dark"], axis="Y", verts=6)
    tube("cable_%s_1" % nm, (CPLATE["cx"], WALL_Y + 39, z), (CPLATE["cx"] + 30, WALL_Y + 150, z - 10), cd, cm); sphere("cable_%s_k" % nm, cd, (CPLATE["cx"] + 30, WALL_Y + 150, z - 10), cm)
    tube("cable_%s_2" % nm, (CPLATE["cx"] + 30, WALL_Y + 150, z - 10), (CPLATE["cx"] + 60, WALL_Y + 230, GROUND + cd / 2), cd, cm); sphere("cable_%s_k2" % nm, cd, (CPLATE["cx"] + 60, WALL_Y + 230, GROUND + cd / 2), cm)
    tube("cable_%s_3" % nm, (CPLATE["cx"] + 60, WALL_Y + 230, GROUND + cd / 2), (CPLATE["cx"] + 60, WALL_Y + 420, GROUND + cd / 2), cd, cm)
# ------------------------------------------------------------------ the floor: dock strip E4, block E5, rods, the battery row along the west end wall
import_board("pcb_e4", "pcb-e1-dock.glb", 0.0); import_board("pcb_e5", "pcb-e5-block.glb", 6.0)
for (x, y) in ((-155.5, -63.0), (-117.5, -63.0), (-155.5, -82.0), (-117.5, -82.0)): cyl("standoff_e5_%d" % int(x), 5.0, 6.0, (x, y, 3.0), M["steel"])
box("traco_ten40", (50.8, 25.4, 10.2), (-40, -81, 1.6 + 5.1), M["dark"])
for (x, y) in ((-110.5, -73.0), (110.5, -73.0), (-110.5, 73.0), (110.5, 73.0)):
    cyl("rod_%d_%d" % (x, y), 3.0, 64.0, (x, y, 32.0), M["steel"])   # 6 Sep 2026 (owner, item 2): the rods end 5 mm above the B15 nuts, never through the face
    for z in (1.6, 16.6, 56.2): cyl("nut_%d_%d_%d" % (x, y, z), 5.5, 2.4, (x, y, z + 1.2), M["steel"], verts=6)
    cyl("spacer_%d_%d_a" % (x, y), 6.0, 13.4, (x, y, 1.6 + 6.7), M["alu"]); cyl("spacer_%d_%d_b" % (x, y), 6.0, 38.0, (x, y, 16.6 + 19.0), M["alu"])
MOD = Matrix.Translation((-174.0, -114.5, 5.0))    # module frame: X across the width, Y along the row from the south (lead) end, Z from the cradle's underside
import_stl("module_base", "module_base.stl", M["gray"], MOD); import_stl("module_lid", "module_lid.stl", M["dark"], MOD); import_stl("module_cradle", "module_cradle.stl", M["black"], MOD)
tube("module_lead_r", (-163, -113, 68), (-163, -104, 30), 3.2, M["wire_red"]); tube("module_lead_b", (-161, -113, 68), (-161, -104, 30), 3.2, M["wire_blk"])
tube("module_lead_r2", (-163, -104, 30), (-146, -98, 12), 3.2, M["wire_red"]); tube("module_lead_b2", (-161, -104, 30), (-144, -98, 12), 3.2, M["wire_blk"]); box("xt60", (16, 16, 8), (-138, -98, 10), M["amber"], bevel=1.0)
# ------------------------------------------------------------------ PCB-A A21, the mezzanine D7, PCB-B B15 and what rides on it
import_board("pcb_a21", "pcb-a-power.glb", 15.0)
import_board("pcb_d7", "pcb-d-aprs.glb", 22.6, Matrix.Translation((45.0, 0.0, 0.0)))
for (x, y) in ((10, -26), (80, -26), (10, 26), (80, 26)): cyl("standoff_d_%d_%d" % (x, y), 5.0, 6.0, (x, y, 19.6), M["steel"])
box("dmr858m", (48, 26, 6), (55.5, -2.0, 38.2), M["tin"]); box("dmr858m_sink", (48, 26, 8), (55.5, -2.0, 45.2), M["alu"])
SMA_JACKS = ((-100, -56), (-84, -56), (-26, -56), (-12, -56), (70, -74), (92, -74), (103, -54))
for k, (x, y) in enumerate(SMA_JACKS):
    cyl("sma_jack_%d" % k, 6.5, 9.0, (x, y, 21.1), M["gold"]); cyl("sma_nut_%d" % k, 8.0, 2.0, (x, y, 17.6), M["steel"], verts=6)
for k, y in enumerate((-68, -58, -48)):     # the three rail leads A to B
    cyl("lead_r_%d" % k, 1.8, 36, (-92 - 1.5, y, 35), M["wire_red"]); cyl("lead_b_%d" % k, 1.8, 36, (-92 + 1.5, y, 35), M["wire_blk"])
import_board("pcb_b15", "pcb-b-compute.glb", 54.6)
ZB = 56.2
box("cm5_module", (40, 55, 1.24), (-88, 0, ZB + 4.62), M["pcb"]); box("cm5_soc", (15, 15, 1.2), (-88, 6, ZB + 5.84), M["dark"]); box("cm5_emmc", (11, 13, 1.0), (-88, -12, ZB + 5.74), M["dark"])
box("cm5_cooler", (41, 56, 4.0), (-88, 0, ZB + 8.24 + 2.0), M["alu"]); box("cm5_fan", (30, 30, 6), (-88, 0, ZB + 8.24 + 12.7 + 3), M["dark"]); cyl("cm5_fan_rotor", 26, 5, (-88, 0, ZB + 8.24 + 12.7 + 3.5), M["gray"], verts=7)
for i in range(13): box("cm5_fin_%d" % i, (1.2, 52, 8.7), (-88 - 18 + 3.0 * i, 0, ZB + 8.24 + 4.0 + 4.35), M["alu"])
for (x, y) in ((-104.5, -24), (-104.5, 24), (-71.5, -24), (-71.5, 24)): cyl("cm5_standoff_%d_%d" % (x, y), 4.0, 4.0, (x, y, ZB + 2.0), M["steel"])
box("wifi_m2_socket", (10, 22, 4.2), (32.4, 60, ZB + 2.1), M["dark"]); box("wifi_m2_card", (26.6, 22, 0.8), (53.7, 60, ZB + 4.6), M["pcb"]); box("wifi_m2_sink", (24, 20, 4.0), (54, 60, ZB + 7.0), M["alu"]); cyl("wifi_m2_standoff", 4.5, 2.4, (65.25, 60, ZB + 5.2), M["steel"], verts=6)
box("lte_card", (50.95, 30, 1.0), (-3, 67, ZB + 4.5), M["pcb"]); box("lte_can", (30, 24, 2.5), (5, 67, ZB + 6.25), M["tin"]); box("lte_socket", (8, 22, 4.0), (-29.5, 67, ZB + 2.0), M["dark"])
box("sdr_stick", (69, 27, 13), (37, 0, ZB + 6.5), M["dark"], bevel=2.0); cyl("sdr_sma", 6.5, 10, (76, 0, ZB + 6.5), M["gold"], axis="X"); box("usb_a_recept", (14, 13.5, 7), (-12, 0, ZB + 3.5), M["steel"])
import_stl("rockblock9704", "rockblock9704.stl", M["dark"], Matrix.Translation((52.0 - 90.3, -48.0 + 91.2, ZB + 6.0 + 10.3)))
for (x, y) in ((36, -64), (68, -64), (36, -32), (68, -32)): cyl("rb_standoff_%d_%d" % (x, y), 6.0, 6.0, (x, y, ZB + 3.0), M["steel"])
box("gnss_neo", (12.2, 16, 2.4), (-107, 55, ZB + 1.2), M["tin"]); box("lora_wio", (11.6, 11, 3), (-84, 55, ZB + 1.5), M["tin"]); box("zigbee_e72", (17.5, 28.7, 2.5), (94, 34, ZB + 1.25), M["tin"])
cyl("cr2032", 20, 3.2, (-46, 27, ZB + 3.2), M["steel"]); box("cr2032_holder", (24, 21, 5), (-46, 27, ZB + 2.5), M["dark"])
box("display_flex", (16, 0.3, BACKER_Z - ZB - 2), (-50, 22, (ZB + BACKER_Z) / 2), M["amber"]); box("panel_ribbon", (0.9, 25.4, BACKER_Z - ZB - 2), (P.J_PANEL_POS[0], 72, (ZB + BACKER_Z) / 2), M["ribbon"])
# ------------------------------------------------------------------ the face: the aluminium plate, the backer C6 on its standoffs, the display, the e-paper, switches, light guides, legends
plate = import_stl("plate", "face_plate.stl", M["anod"], fit=(True, "min", PLATE_UNDER))
if plate is None: plate = box("plate", (P.PLATE[0], P.PLATE[1], P.PLATE[2]), (0, 0, PLATE_UNDER + P.PLATE[2] / 2), M["anod"])
c6 = import_board("pcb_c6", "pcb-c6-backer.glb", BACKER_Z, hide_names=tuple("D%d" % k for k in range(1, 17)))
if c6 is None:      # stand-in U until the C6 GLB exists
    for nm, (x0, y0, x1, y1) in (("L", P.STRIP_L), ("B", P.STRIP_B), ("R", P.STRIP_R)): box("pcb_c6_strip_" + nm, (x1 - x0, y1 - y0, P.BACKER_T), ((x0 + x1) / 2, (y0 + y1) / 2, BACKER_Z + P.BACKER_T / 2), M["mask"])
for k, (x, y) in enumerate(P.STANDOFFS): cyl("standoff_c6_%d" % k, 5.0, P.BACKER_GAP, (x, y, PLATE_UNDER - P.BACKER_GAP / 2), M["steel"], verts=6); cyl("screw_c6_%d" % k, 5.5, 2.0, (x, y, BACKER_Z - 1.0), M["steel_dark"])
# Touch Display 2: the glass in the plate's 1 mm pocket (its top 1 mm inside the plate), the picture through the aperture
DX, DY = P.DISPLAY["c"]; GT = PLATE_UNDER + P.DISPLAY["pocket_depth"]
TD2 = Matrix.Translation((DX, DY, GT - 5.0)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Translation((0, -2.95, 0))
import_stl("td2", "td2.stl", M["black"], TD2)
scr = box("td2_screen", (160, 90, 0.15), (DX, DY, GT - 0.5), M["dark"]); textured(scr, "ui.png", 4.0)
box("td2_glass", (P.DISPLAY["glass"][0], P.DISPLAY["glass"][1], 0.8), (DX, DY, GT - 0.4), M["glass"])
# WeAct 3.7 e-paper: the module taped under the plate with its glass up in the window, the 2 mm lens in the top pocket
EX, EY = P.EPAPER["c"]; ET = FACE - P.EPAPER["pocket_depth"]
EPD = Matrix.Translation((EX, EY, ET - 3.0)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((-269.3, -177.4, 0.0)); import_stl("epaper", "epaper.stl", M["dark"], EPD)
epd = box("epaper_glass", (92.99, 53.0, 0.6), (EX, EY, ET - 0.3), M["paper"]); textured(epd, "epaper.png", 0.0)
box("epaper_lens", (P.EPAPER["lens"][0], P.EPAPER["lens"][1], 2.0), (EX, EY, ET + 1.0), M["lens"], bevel=0.8)
def pushbutton(name, x, y, D, ring, depth, on=True):
    """C&K ATP anti-vandal: stainless bezel with a bevel, the illuminated ring, a low domed cap, the body below the plate."""
    cyl(name + "_bezel", D + 3.2, 3.0, (x, y, FACE + 1.5), M["steel"], bevel=1.0); cyl(name + "_body", D - 1.0, depth - 3.0, (x, y, PLATE_UNDER - (depth - 3.0) / 2), M["dark"])
    torus(name + "_ring", D / 2 - 1.6, 0.9, (x, y, FACE + 3.1), ring if on else M["ledoff"])
    cyl(name + "_cap", D - 6.0, 3.0, (x, y, FACE + 4.2), M["steel_dark"], bevel=1.2); sphere(name + "_dome", D - 6.0, (x, y, FACE + 4.2 - (D - 6.0) / 2 + 3.4), M["steel_dark"])
RINGS = {"SW_MAIN": (M["green"], True), "SW_PI": (M["amber"], True), "SW_TEST": (M["white"], False)}
for ref, (x, y), hole, depth in P.BUTTONS: pushbutton(ref.lower(), x, y, hole, RINGS[ref][0], depth, RINGS[ref][1])
def toggle(name, x, y, L, tilt, depth, locking=False, boot=False):
    cyl(name + "_nut", 10.4, 2.8, (x, y, FACE + 1.4), M["chrome"], verts=6); cyl(name + "_bush", 6.35, 8.5, (x, y, FACE + 2.8), M["chrome"])
    if locking: cyl(name + "_lock", 9.0, 5.0, (x, y, FACE + 7.8), M["steel_dark"], bevel=0.8)
    t = math.radians(tilt); base_z = FACE + 9.0
    cone(name + "_lever", 4.6, 6.4, L, (x, y - math.sin(t) * L / 2, base_z + math.cos(t) * L / 2), M["chrome"], rot=(t, 0, 0))
    sphere(name + "_tip", 7.2, (x, y - math.sin(t) * L, base_z + math.cos(t) * L), M["red"] if locking else M["chrome"])
    if boot: cone(name + "_boot", 15.0, 6.0, 14.0, (x, y - math.sin(t) * 5.5, base_z + math.cos(t) * 5.5), M["rubber"], rot=(t, 0, 0))
    box(name + "_body", (12.5, 20.0 if locking else 10.0, depth - 2.0), (x, y, PLATE_UNDER - (depth - 2.0) / 2), M["dark"], bevel=1.0)
for ref, (x, y) in P.TOGGLES: toggle(ref.lower(), x, y, 22, 24, 26.0, locking=True)
for ref, (x, y) in P.TOGGLES:   # 6 Sep 2026 17:30 (owner, item 3): SOS and ZEROIZE under hinged safety covers, closed; the cover part is a pick owed (appendix 32.48)
    if ref not in ("SW_SOS", "SW_ZERO"): continue
    nm = ref.lower(); cm = M["red"] if ref == "SW_SOS" else mat("guard_yellow", (0.92, 0.72, 0.04), 0.45)
    box(nm + "_guard_base", (26.0, 30.0, 2.0), (x, y, FACE + 1.0), M["steel_dark"], bevel=0.8)
    for sx_ in (-1, 1): box(nm + "_guard_lug_%d" % sx_, (3.0, 5.0, 9.0), (x + sx_ * 12.5, y + 13.5, FACE + 6.5), M["steel_dark"], bevel=0.6)
    cyl(nm + "_guard_pin", 2.5, 30.0, (x, y + 13.5, FACE + 9.0), M["steel_dark"], axis="X")
    box(nm + "_guard_cover", (24.0, 28.0, 30.0), (x, y - 1.0, FACE + 17.0), cm, bevel=3.0); box(nm + "_guard_lip", (14.0, 4.0, 3.0), (x, y - 16.5, FACE + 4.0), cm, bevel=1.0)
toggle(P.LIGHT[0].lower(), P.LIGHT[1][0], P.LIGHT[1][1], 18, 25, 19.0, boot=True)
SX, SY = P.SOUNDER[1]
cyl("sounder", 34, 3.5, (SX, SY, FACE + 1.75), M["black"], bevel=1.2)
for k, rr in enumerate((5.0, 8.5, 12.0)): torus("sounder_ring_%d" % k, rr, 0.7, (SX, SY, FACE + 3.5), M["dark"])
cyl("sounder_body", P.SOUNDER[2] - 0.6, P.SOUNDER[3] - 3.0, (SX, SY, PLATE_UNDER - (P.SOUNDER[3] - 3.0) / 2), M["dark"])
LED_STATE = {"MSTR WARN": ("redled", False), "MSTR CAUT": ("amber", False), "TX": ("redled", False), "SOS ACTIVE": ("redled", False), "SAT": ("green", True), "MESH": ("green", True), "LTE": ("green", True),
             "GPS": ("green", True), "SHORE": ("amber", True), "CHARGE": ("amber", True), "MSG": ("green", False)}
def lightguide(name, x, y, m, on):
    """Mentor 1282.5004: the 3.2 mm spherical head on the face, the 2.5 mm shaft down to the LED on the backer."""
    cyl(name + "_shaft", 2.5, P.PLATE[2] + 4.5, (x, y, FACE - (P.PLATE[2] + 4.5) / 2 + 0.2), M["lens"]); sphere(name + "_head", 3.2, (x, y, FACE + 0.6), m if on else M["ledoff"])
    cyl(name + "_led", 3.0, 4.0, (x, y, BACKER_TOP + 2.0), m if on else M["ledoff"])
for ref, (x, y), txt in P.STATUS_LEDS:
    col, on = LED_STATE[txt]; lightguide("led_" + ref, x, y, M[col], on); label("lbl_" + ref, txt, (x - 5.5, y - 1.1, FACE + 0.05), 2.6, M["white"], align="RIGHT")
for k, (ref, (x, y), txt) in enumerate(P.BAR_LEDS): lightguide("led_" + ref, x, y, M["green"], k < 3)
label("lbl_bar", "BATTERY", (P.BAR_LEDS[2][1][0], P.BAR_LEDS[2][1][1] - 7.5, FACE + 0.05), 3.0, M["white"])
label("nameplate", "MESHSAT FIELD KIT V2", (P.NAMEPLATE[0], P.NAMEPLATE[1] + 2.5, FACE + 0.05), 4.2, M["white"]); label("nameplate_2", "S/N ______", (P.NAMEPLATE[0], P.NAMEPLATE[1] - 5.5, FACE + 0.05), 3.0, M["white"])
for ref, (x, y), hole, depth in P.BUTTONS: label("lbl_" + ref, {"SW_MAIN": "MAIN", "SW_PI": "PI", "SW_TEST": "TEST"}[ref], (x, y + hole / 2 + 4.0, FACE + 0.05), 3.6, M["white"])
for ref, (x, y) in P.TOGGLES: label("lbl_" + ref, {"SW_SOS": "SOS", "SW_EMCON": "EMCON", "SW_ZERO": "ZEROIZE"}[ref], (x, y + 14.0, FACE + 0.05), 3.6, M["white"])
label("lbl_light", "LIGHT", (P.LIGHT[1][0], P.LIGHT[1][1] + 14.0, FACE + 0.05), 3.6, M["white"])
(LX, LY), LD = P.LOGO
def logo_mark(name, cx, cy, width, z, m):
    """The MeshSat mark from tools/logo_meshsat.json (traced from the sticker master, never redrawn) as one filled 2D curve: outer loops and holes as closed splines, even-odd fill."""
    import json
    src = next(f for f in (os.path.join(R, "logo_meshsat.json"), os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ecad", "tools", "logo_meshsat.json")) if os.path.exists(f))
    d = json.load(open(src)); x0, y0, x1, y1 = d["bbox"]; sc = width / (x1 - x0); mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "2D"; cu.fill_mode = "BOTH"; cu.extrude = 0.03
    for poly in d["polys"]:
        for loop in [poly["ext"]] + list(poly.get("holes", [])):
            sp = cu.splines.new("POLY"); sp.points.add(len(loop) - 1); sp.use_cyclic_u = True
            for k, (x, y) in enumerate(loop): sp.points[k].co = ((x - mx) * sc, -(y - my) * sc, 0.0, 1.0)   # artwork y grows downward
    o = bpy.data.objects.new(name, cu); S.collection.objects.link(o); o.location = (cx, cy, z); assign(o, m); return o
logo_mark("logo_mark", LX, LY, LD, FACE + 0.05, M["white"])   # 6 Sep 2026 (owner): the official mark on the plate's upper left, not a ring with text
# ------------------------------------------------------------------ end-wall antennas: nine bulkheads at Z 88, whips upright on right-angle adapters, pigtails inside to the dock nests
WX = wall_x(SMA_Z); WALL_IN = FLOOR_W / 2 + 4.0   # the end wall's outer face at the jack line
# the antenna picks of appendix 32.46 (form, length, diameter): stubby = straight on the jack; dipole = hinged terminal mount stood upright; whip = the 2 m band
# placeholder (pick owed); magwhip = the magnetic-base SDR whip on its lead, set on the ground behind the west wall
ANT = {"LTE": ("stubby", 50.8, 12.4), "LORA": ("stubby", 50.8, 12.4), "WIFI P2P A": ("dipole", 135.0, 14.0), "WIFI P2P B": ("dipole", 135.0, 14.0), "WIFI 2.4": ("dipole", 110.0, 11.0), "VHF": ("whip", 400.0, 8.0), "SDR": ("magwhip", 82.2, 30.0)}
NEST = {"VHF": SMA_JACKS[0], "WIFI 2.4": SMA_JACKS[1], "GNSS": SMA_JACKS[2], "SDR": SMA_JACKS[3], "LTE": SMA_JACKS[4], "IRIDIUM": SMA_JACKS[5], "LORA": SMA_JACKS[6],
        "WIFI P2P A": (26.0, -56.0), "WIFI P2P B": (48.0, -74.0)}   # 6 Sep 2026 17:30 (owner, item 6): ALL nine cables end at the dock; the two WiFi P2P paths get their own blind-mate sites on A22 and in-stack jumpers to the M.2 card
for sx, sites in ((-1, WEST), (1, EAST)):
    for y, nm in sites:
        z = SMA_Z; tag = nm.replace(" ", "_").lower()
        cyl("bulk_" + tag, 9.5, 3.0, (sx * (WX + 1.5), y, z), M["steel"], axis="X", verts=6); cyl("bulk_sma_" + tag, 6.5, 11, (sx * (WX + 7), y, z), M["gold"], axis="X")
        cyl("bulk_in_" + tag, 8.0, 10, (sx * (WALL_IN + 3), y, z), M["gold"], axis="X"); cyl("bulk_nut_in_" + tag, 8.0, 2.0, (sx * (WALL_IN - 1), y, z), M["steel"], axis="X", verts=6)
        ax = sx * (WX + 15)
        # 6 Sep 2026 (owner, the first 1450 set): no invented antennas. The record fixes two forms only: the Iridium patch (its top at Z 82 on the east wall)
        # and the u-blox GNSS puck; every other port is drawn as its bulkhead jack, the whip parts are not chosen yet. WHIPS=1 restores the old stand-ins.
        if nm in ANT:
            form, L, d = ANT[nm]
            if form == "stubby": cyl("ant_" + tag, d, L, (sx * (WX + 12 + L / 2), y, z), M["dark"], axis="X", bevel=2.0)
            elif form in ("dipole", "whip"):
                cyl("ant_elbow_" + tag, 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_knuckle_" + tag, 10, 10, (ax, y, z + 4.5 + 5), M["dark"], bevel=1.0)
                cyl("ant_" + tag, d, L, (ax, y, z + 9.5 + L / 2), M["dark"], bevel=min(2.0, d / 3))
            else:   # the SDR whip on its magnetic base, on the ground behind the west wall, lead to the jack
                mx, my = sx * (WX + 70), BL / 2 + 90
                cyl("ant_" + tag + "_base", d, 22.0, (mx, my, GROUND + 11.0), M["dark"], bevel=3.0); cyl("ant_" + tag, 9.0, L - 22.0, (mx, my, GROUND + 22.0 + (L - 22.0) / 2), M["dark"], bevel=2.0)
                cyl("ant_" + tag + "_plug", 8.0, 12.0, (sx * (WX + 12), y, z), M["gold"], axis="X")
                q0 = (sx * (WX + 18), y, z); q1 = (sx * (WX + 44), y + 14, z - 42); q2 = (mx - sx * 22, my - 60, GROUND + 4); q3 = (mx, my - d / 2, GROUND + 5)
                tube("ant_" + tag + "_lead_1", q0, q1, 3.0, M["coax"]); sphere("ant_" + tag + "_lead_k1", 3.0, q1, M["coax"]); tube("ant_" + tag + "_lead_2", q1, q2, 3.0, M["coax"]); sphere("ant_" + tag + "_lead_k2", 3.0, q2, M["coax"]); tube("ant_" + tag + "_lead_3", q2, q3, 3.0, M["coax"])
        elif nm == "IRIDIUM":
            # 6 Sep 2026 16:20 (owner): the port is a plain SMA bulkhead like the other eight; the approved external antenna of the 9704 SMA variant is the
            # Maxtena M1621HCT-P-SMA helical (49 x dia 19 mm radome, SMA male; appendix 32.45), stood upright on a right-angle SMA adapter so its axis points
            # at the sky; drawn with the lid open only (the kit travels closed with its antennas off)
            cyl("ant_elbow_iridium", 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_elbow2_iridium", 8, 6, (ax, y, z + 4.5 + 3), M["gold"])
            cyl("ant_iridium", 19, 49, (ax, y, z + 4.5 + 6 + 24.5), M["dark"], bevel=3.0)
        elif nm == "GNSS":
            # 6 Sep 2026 16:20 (owner): the LG290P's active antenna, the Quectel YEGD006U1A puck (109.28 x 89 x 25.8 mm, SMA male on a 5 m RG174 lead; appendix
            # 32.46), set on the ground beyond the west wall with its lead to the jack; the jack itself is a plain SMA bulkhead; lid open only
            px, py = sx * (WX + 62), -(BL / 2 + 74)   # on the ground at the front-west corner, where the orbit views show it beside the case
            rounded_box("ant_gnss_puck", 109.28, 89.0, 25.8, 12.0, (px, py, GROUND), M["dark"], top_scale=(0.88, 0.88))
            cyl("ant_gnss_plug", 8.0, 12.0, (sx * (WX + 12), y, z), M["gold"], axis="X")
            q0 = (sx * (WX + 18), y, z); q1 = (sx * (WX + 44), y - 14, z - 42); q2 = (px + 24, py + 70, GROUND + 5); q3 = (px + 6, py + 44.5, GROUND + 6)
            tube("ant_gnss_lead_1", q0, q1, 3.0, M["coax"]); sphere("ant_gnss_lead_k1", 3.0, q1, M["coax"]); tube("ant_gnss_lead_2", q1, q2, 3.0, M["coax"]); sphere("ant_gnss_lead_k2", 3.0, q2, M["coax"]); tube("ant_gnss_lead_3", q2, q3, 3.0, M["coax"])
        # the pigtail (6 Sep 2026, owner): a right-angle plug at the coupler, down the wall, along the FLOOR to the dock strip's float clamp under A21's
        # receptacle (the blind-mate joint), never to a board; on the west side it drops into the 10 mm gap behind the battery row and runs under the module's
        # cradle (four 4 x 4 mm grooves in the cradle, owed in battery_module.py), so the module lifts out without touching a cable
        xdrop = -(WALL_IN - 5) if sx < 0 else (WALL_IN - 6); zf = 2.5
        p0 = (sx * (WALL_IN - 6), y, z); p1 = (xdrop, y, z); p2 = (xdrop, y, zf)
        cyl("pig_plug_" + tag, 8.0, 10.0, p0, M["gold"], axis="X")
        if nm in NEST:
            nx, ny = NEST[nm]; p3 = (nx, y, zf); p4 = (nx, ny, zf)
            tube("pig_%s_1" % tag, p0, p1, 3.0, M["coax"]); sphere("pig_%s_k1" % tag, 3.0, p1, M["coax"]); tube("pig_%s_2" % tag, p1, p2, 3.0, M["coax"]); sphere("pig_%s_k2" % tag, 3.0, p2, M["coax"])
            tube("pig_%s_3" % tag, p2, p3, 3.0, M["coax"]); sphere("pig_%s_k3" % tag, 3.0, p3, M["coax"]); tube("pig_%s_4" % tag, p3, p4, 3.0, M["coax"])
            box("dock_clamp_" + tag, (12, 12, 5), (nx, ny, 2.5), M["black"]); cyl("dock_plug_" + tag, 6.0, 8.0, (nx, ny, 5 + 4), M["gold"])   # the printed float clamp on E4 and the SMP-MAX plug standing up into A21
            if nm.startswith("WIFI P2P"):   # the in-stack jumper (6 Sep 2026 17:30): A22 passes the path through to a top-side MHF4, a 2 mm lead climbs to the M.2 card on B15
                za = 16.6 + 1.6; cyl("stack_mhf_" + tag, 4.0, 2.5, (nx, ny, za + 1.25), M["gold"]); j1 = (nx, ny, za + 2.5); j2 = (nx, ny, ZB - 10.0); j3 = (66.0, 60.0 + (2 if "B" in nm else -2), ZB + 6.0)
                tube("jumper_%s_1" % tag, j1, j2, 2.0, M["coax"]); sphere("jumper_%s_k" % tag, 2.0, j2, M["coax"]); tube("jumper_%s_2" % tag, j2, j3, 2.0, M["coax"])
# ------------------------------------------------------------------ rulers (10 mm ticks, numerals every 50) and the 50 mm floor grid
RULER_W, RULER_T = 14.0, 2.0
def ruler(name, origin, axis, length, m_up=(0, 0, 1)):
    """A white bar from `origin` along `axis` (unit vector) with black ticks every 10 mm (taller every 50) and numerals every 50 mm."""
    a = Vector(axis); o = Vector(origin); up = Vector(m_up); side = a.cross(up).normalized()
    mid = o + a * (length / 2); rot = a.to_track_quat("X", "Z").to_euler() if axis != (0, 0, 1) else (0, 0, 0)
    bar = box(name, (length, RULER_W, RULER_T) if axis != (0, 0, 1) else (RULER_W, RULER_T, length), tuple(mid), M["ruler"], rot=rot if axis != (0, 0, 1) else (0, 0, 0))
    for k in range(0, int(length) + 1, 10):
        big = k % 50 == 0; tl = RULER_W * (0.7 if big else 0.4); p = o + a * k + up * (RULER_T / 2 + 0.05) - side * (RULER_W / 2 - tl / 2) if axis != (0, 0, 1) else o + a * k + Vector((0, -RULER_T / 2 - 0.05, 0)) - side * (RULER_W / 2 - tl / 2)
        if axis != (0, 0, 1): box("%s_t%d" % (name, k), (1.0 if big else 0.6, tl, 0.2), tuple(p), M["tick"], rot=rot)
        else: box("%s_t%d" % (name, k), (tl, 0.2, 1.0 if big else 0.6), tuple(p), M["tick"])
        if big:
            if axis == (1, 0, 0): label("%s_n%d" % (name, k), str(k), (o.x + k, o.y - RULER_W / 2 + 1.5, o.z + RULER_T / 2 + 0.05), 4.0, M["tick"])
            elif axis == (0, 1, 0): label("%s_n%d" % (name, k), str(k), (o.x + 1.0, o.y + k - 1.5, o.z + RULER_T / 2 + 0.05), 4.0, M["tick"], align="LEFT")
            else: label("%s_n%d" % (name, k), str(k), (o.x + 1.0, o.y - RULER_T / 2 - 0.05, o.z + k + 1.0), 4.0, M["tick"], rot=(math.pi / 2, 0, 0), align="LEFT")
    label(name + "_unit", "mm", (o.x + (length + 8 if axis == (1, 0, 0) else 0), o.y + (length + 8 if axis == (0, 1, 0) else 0), o.z + (length + 8 if axis == (0, 0, 1) else RULER_T / 2 + 0.05)), 4.0, M["tick"], rot=(math.pi / 2, 0, 0) if axis == (0, 0, 1) else (0, 0, 0))
GZ = GROUND + 0.05
ruler("ruler_x", (-BW / 2, -BL / 2 - 40, GZ), (1, 0, 0), 450)          # along the front edge, 0 at the case's left end
ruler("ruler_x2", (-BW / 2, BL / 2 + 40, GZ), (1, 0, 0), 450)          # along the back edge
ruler("ruler_y", (-BW / 2 - 40, -BL / 2, GZ), (0, 1, 0), 350)          # along the left side, 0 at the front
ruler("ruler_y2", (BW / 2 + 40, -BL / 2, GZ), (0, 1, 0), 350)          # along the right side
ruler("ruler_z", (-BW / 2 - 40, -BL / 2 - 40, GROUND), (0, 0, 1), 300)   # standing at the front-left corner, 0 on the ground
ruler("ruler_z2", (BW / 2 + 40, -BL / 2 - 40, GROUND), (0, 0, 1), 300)   # and the front-right
label("ruler_note", "Peli 1450, catalogue 411 x 329 mm; floor grid 50 mm; Z 0 = the cavity floor", (0, -BL / 2 - 75, GZ), 6.0, M["tick"])
for k in range(-12, 13):
    box("grid_x_%d" % k, (1200, 0.8, 0.1), (0, k * 50.0, GROUND + 0.02), M["grid"]); box("grid_y_%d" % k, (0.8, 1200, 0.1), (k * 50.0, 0, GROUND + 0.02), M["grid"])
# ------------------------------------------------------------------ world, lights, cameras, views
S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SAMPLES", "256")); S.cycles.use_denoising = False; S.cycles.device = "CPU"
S.render.use_persistent_data = True   # 6 Sep 2026 16:58: keep the BVH between views (the drawing-built case is heavy; without this each view re-synced the scene for 80 s while the GPUs idled)
if os.environ.get("CYCLES_GPU"):   # the build host nllei01gpu01 (RTX 3090 Ti): OptiX, else CUDA; run with the service group stopped
    cp = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA"):
        try:
            cp.compute_device_type = dev_type; cp.get_devices()
            if any(d.type == dev_type for d in cp.devices): break
        except Exception: continue
    for d in cp.devices: d.use = d.type in ("OPTIX", "CUDA")
    S.cycles.device = "GPU"; print("cycles on", cp.compute_device_type, [d.name for d in cp.devices if d.use], flush=True)
S.render.resolution_x = 2000; S.render.resolution_y = 1400; S.render.resolution_percentage = int(os.environ.get("RESPCT", "100"))
S.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "AgX"
for lk in ("Medium High Contrast", "AgX - Medium High Contrast", "None"):
    try: S.view_settings.look = lk; break
    except TypeError: pass
world = bpy.data.worlds.new("w"); S.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.78, 0.8, 0.85, 1); bg.inputs[1].default_value = 1.1
def light(name, at, energy, size):
    bpy.ops.object.light_add(type="AREA", location=at); L = bpy.context.object; L.name = name; L.data.energy = energy; L.data.size = size
    L.rotation_euler = (Vector((0, 0, 60)) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return L
light("key", (-500, -900, 1000), 5.5e6, 700); light("fill", (900, -300, 700), 2.2e6, 900); light("rim", (200, 900, 800), 2.2e6, 500); light("top", (0, 0, 1400), 1.6e6, 1200)
bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, GROUND)); floor = bpy.context.object; floor.name = "ground"; assign(floor, mat("ground", (0.62, 0.62, 0.64), 0.85))
def camera(name, at, look, lens=50):
    bpy.ops.object.camera_add(location=at); c = bpy.context.object; c.name = name; c.data.lens = lens; c.data.clip_end = 20000
    c.rotation_euler = (Vector(look) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return c
def orbit(az, el, dist=1050, look=(0, 0, 70), lens=42):
    """az 0 = from the front (-Y), counter-clockwise seen from above; el above the ground plane."""
    a, e = math.radians(az), math.radians(el)
    return (look[0] - dist * math.cos(e) * math.sin(a) * -1.0, look[1] - dist * math.cos(e) * math.cos(a), look[2] + dist * math.sin(e))
PANEL_PREFIX = ("plate", "pcb_c6", "standoff_c6", "screw_c6", "td2", "epaper", "sw_", "sounder", "led_", "lbl_", "nameplate", "logo_")   # (moved above the views: the assembly sequence uses it)
VIEWS = {}
# 6 Sep 2026, second set (owner: "the inside of the case is the most interesting part"): eight orbit views with the lid open at el 40, four closed
# views, and everything else inside: the stack level by level with the boards above removed, the face from both sides, the walls from inside.
for az in range(0, 360, 45): VIEWS["az%03d-el40-open" % az] = dict(cam=camera("cam_%03d_40" % az, orbit(az, 40), (0, 0, 70), 42), lid=True)
for az in (0, 90, 180, 270): VIEWS["az%03d-el20-closed" % az] = dict(cam=camera("cam_%03d_20c" % az, orbit(az, 20), (0, 0, 70), 42), lid=False)
B15_PARTS = ("pcb_b15", "cm5_", "cr2032", "display_flex", "gnss_neo", "lora_wio", "lte_", "panel_ribbon", "sdr_", "usb_a_recept", "wifi_m2_", "zigbee_e72", "rockblock9704")   # the board and everything drawn on it
D7_PARTS = B15_PARTS + ("pcb_d7", "dmr858m")
A21_PARTS = D7_PARTS + ("pcb_a21", "sma_jack", "sma_nut", "sma_nest", "stack_mhf", "jumper_")   # the wall pigtails end at the dock clamps (6 Sep 2026), so they stay when A21 is lifted
DOCK_PARTS = A21_PARTS + ("battery", "module_")
UPPER = {"b15": B15_PARTS, "d7": D7_PARTS, "a21": A21_PARTS, "dock": DOCK_PARTS}
VIEWS.update({
    "top-face": dict(cam=camera("cam_top", (0, -60, 1150), (0, 0, 100), 50), lid=True),
    "face-detail-left": dict(cam=camera("cam_fdl", (-330, -230, 330), (-120, 0, 100), 60), lid=True),
    "face-detail-right": dict(cam=camera("cam_fdr", (330, -230, 330), (120, 0, 100), 60), lid=True),
    "face-underside": dict(cam=camera("cam_under", (-300, -520, 150), (0, 0, 190), 50), lid=True, lift=True),
    "face-underside-top": dict(cam=camera("cam_under_top", (60, -420, 520), (0, 0, 200), 50), lid=True, lift=True),
    "stack-no-face": dict(cam=camera("cam_stack", (-300, -480, 480), (-20, 0, 60), 46), lid=True, noface=True),
    "stack-no-face-top": dict(cam=camera("cam_stack_top", (0, -40, 900), (0, 0, 40), 50), lid=True, noface=True),
    "stack-no-face-east": dict(cam=camera("cam_stack_e", (520, -360, 360), (40, 0, 55), 46), lid=True, noface=True),
    "stack-no-face-back": dict(cam=camera("cam_stack_b", (-260, 560, 420), (-20, 40, 55), 46), lid=True, noface=True),
    "level-b15": dict(cam=camera("cam_l_b15", (-300, -480, 480), (-20, 0, 60), 46), lid=True, noface=True),
    "level-d7": dict(cam=camera("cam_l_d7", (-300, -480, 480), (-20, 0, 50), 46), lid=True, noface=True, hide=UPPER["b15"]),
    "level-a21": dict(cam=camera("cam_l_a21", (-300, -480, 480), (-20, 0, 40), 46), lid=True, noface=True, hide=UPPER["d7"]),
    "level-a21-top": dict(cam=camera("cam_l_a21_top", (0, -40, 800), (0, 0, 20), 50), lid=True, noface=True, hide=UPPER["d7"]),
    "level-dock": dict(cam=camera("cam_l_dock", (-220, -400, 560), (-20, -30, 10), 46), lid=True, noface=True, hide=UPPER["a21"]),
    "level-dock-top": dict(cam=camera("cam_l_dock_top", (0, -40, 800), (0, 0, 10), 50), lid=True, noface=True, hide=UPPER["a21"]),
    "battery-row": dict(cam=camera("cam_batt", (-420, -330, 330), (-160, 0, 50), 50), lid=True, lift=True),
    "battery-row-inside": dict(cam=camera("cam_batt_in", (-40, -200, 260), (-160, 0, 45), 50), lid=True, noface=True, hide=UPPER["d7"]),
    "dock-joint": dict(cam=camera("cam_dock", (40, -330, 150), (-45, -60, 10), 60), lid=True, cutaway=True, noface=True, hide=UPPER["a21"]),      # front wall removed: the float clamps and plugs on the dock strip
    "dock-joint-a21": dict(cam=camera("cam_dock_a", (40, -330, 170), (-45, -60, 20), 60), lid=True, cutaway=True, noface=True, hide=UPPER["d7"]),   # the same with A21 mated on them
    "connector-plate": dict(cam=camera("cam_cp", (-120, 470, 150), (-56, 168, 55), 60), lid=False),   # the upright plate on the back wall from outside, both cables plugged (the wall model is solid, so there is no inside view of it)
    "west-wall-inside": dict(cam=camera("cam_ww_in", (60, -180, 260), (-180, 0, 70), 50), lid=True, noface=True, hide=UPPER["d7"]),
    "east-wall-inside": dict(cam=camera("cam_ew_in", (-60, -180, 260), (180, 0, 70), 50), lid=True, noface=True, hide=UPPER["d7"]),
    "cutaway": dict(cam=camera("cam_cutaway", (-360, -640, 330), (-10, 0, 62), 46), lid=True, cutaway=True),
    "cutaway-east": dict(cam=camera("cam_cutaway_e", (420, -600, 330), (10, 0, 62), 46), lid=True, cutaway=True),
    "west-wall": dict(cam=camera("cam_west", (-780, -260, 260), (-205, 0, 110), 55), lid=False),
    "east-wall": dict(cam=camera("cam_east", (780, -260, 260), (205, 0, 110), 55), lid=False),
    "back-wall": dict(cam=camera("cam_back", (-160, 760, 260), (-56, 165, 60), 55), lid=False),
    "back-wall-nocables": dict(cam=camera("cam_back_nc", (-160, 760, 260), (-56, 165, 60), 55), lid=False, cables=False),
    "az135-el40-open-nocables": dict(cam=camera("cam_135_nc", orbit(135, 40), (0, 0, 70), 42), lid=True, cables=False),
    "antennas-az045": dict(cam=camera("cam_ant_045", orbit(45, 38, 1500), (0, 0, 120), 40), lid=True, antennas=True),
    "antennas-az315": dict(cam=camera("cam_ant_315", orbit(315, 38, 1500), (0, 0, 120), 40), lid=True, antennas=True),
    "antennas-az225": dict(cam=camera("cam_ant_225", orbit(225, 35, 1500), (0, 0, 120), 40), lid=True, antennas=True),
    "antennas-top": dict(cam=camera("cam_ant_top", (0, -60, 1500), (0, 0, 60), 40), lid=True, antennas=True),
})
# the disassembly sequence (owner, 6 Sep 2026 item 7): the same wide camera, one step per view, every removed part set down on the ground around the case
STACK = A21_PARTS + ("rod_", "nut_", "spacer_")
PLATE_DZ = GROUND + 0.5 - (BACKER_Z - 1.6); STACK_DZ = GROUND + 0.5 - 1.6; MODULE_DZ = GROUND + 0.5
MV_PLATE = (PANEL_PREFIX, (450.0, -40.0, PLATE_DZ)); MV_STACK = (STACK, (-460.0, 40.0, STACK_DZ)); MV_MODULE = (("module_",), (60.0, -360.0, MODULE_DZ))
ASM_CAM = lambda n: camera("cam_asm_%d" % n, (560, -1000, 720), (0, -50, 30), 32)
VIEWS.update({
    "assembly-1-closed": dict(cam=ASM_CAM(1), lid=False),
    "assembly-2-lid-open": dict(cam=ASM_CAM(2), lid=True),
    "assembly-3-plate-off": dict(cam=ASM_CAM(3), lid=True, moves=[MV_PLATE]),
    "assembly-4-stack-out": dict(cam=ASM_CAM(4), lid=True, moves=[MV_PLATE, MV_STACK]),
    "assembly-5-battery-out": dict(cam=ASM_CAM(5), lid=True, moves=[MV_PLATE, MV_STACK, MV_MODULE]),
    "assembly-6-dock": dict(cam=camera("cam_asm_6", (-260, -520, 520), (-20, -20, 10), 40), lid=True, moves=[MV_PLATE, MV_STACK, MV_MODULE]),
})
def walk(prefixes):
    for o in bpy.data.objects:
        p = o
        while p is not None:
            if p.name.startswith(prefixes): yield o; break
            p = p.parent
def hide(prefixes, flag):
    for o in walk(prefixes): o.hide_render = flag
def move_group(prefixes, vec):
    for o in walk(tuple(prefixes)):
        if o.parent is None: o.matrix_world = Matrix.Translation(vec) @ o.matrix_world
def move_face(dz):
    for o in walk(PANEL_PREFIX):
        if o.parent is None: o.matrix_world = Matrix.Translation((0, 0, dz)) @ o.matrix_world
    for o in bpy.data.objects:
        if o.name in ("display_flex", "panel_ribbon"):
            if dz > 0: o.scale.z *= 2.0; o.location.z += dz / 2
            else: o.scale.z /= 2.0; o.location.z += dz / 2
set_lid(True)
def render(view):
    v = VIEWS[view]; S.camera = v["cam"]; set_lid(v["lid"]); hide(("peli_text",), bool(v.get("cutaway")))
    hide(("ant_",), not v.get("antennas"))   # 6 Sep 2026 17:30 (owner, item 9): antennas only in the views flagged for them, all nine at once
    hide(("cable_", "plug_"), v.get("cables") is False)   # item 8: the shore and USB cables can be left out
    for prefixes, vec in v.get("moves", []): move_group(prefixes, Vector(vec))   # item 7: the disassembly sequence, parts set down around the case
    keep = []; tool = None
    if v.get("cutaway"):   # the front wall of the case and the frame's front bar removed; the face lifted 60 mm on its ribbon and flex
        tool = box("cut_tool", (700, 142, 400), (0, -BL / 2 - 25, 100), M["dark"])
        for o in CASE + ([frame] if frame else []):
            if o is None or o.type != "MESH": continue
            md = o.modifiers.new("cutv", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = tool; md.solver = "EXACT"; keep.append((o, md))
        tool.hide_render = True; move_face(60)
    if v.get("lift"): move_face(150)
    if v.get("noface"): hide(PANEL_PREFIX, True)
    if v.get("hide"): hide(tuple(v["hide"]), True)   # 6 Sep 2026: the stack level by level (object name prefixes hidden for this view only)
    S.render.filepath = os.path.join(OUT, "meshsat-1450-%s.png" % view); bpy.ops.render.render(write_still=True); print("RENDERED", S.render.filepath, flush=True)
    if v.get("cutaway"):
        for o, md in keep: o.modifiers.remove(md)
        bpy.data.objects.remove(tool, do_unlink=True); move_face(-60)
    if v.get("lift"): move_face(-150)
    if v.get("noface"): hide(PANEL_PREFIX, False)
    if v.get("hide"): hide(tuple(v["hide"]), False)
    for prefixes, vec in reversed(v.get("moves", [])): move_group(prefixes, -Vector(vec))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "meshsat-1450-concept.blend"))
if os.environ.get("DUMP_BBOX"):
    # stack height map input (5 Sep 2026, C6 gate): every mesh object's world bounding box, case frame in mm
    import json
    dump = []
    for o in bpy.data.objects:
        if o.type != "MESH" or not o.data.vertices: continue
        x0, x1, y0, y1, z0, z1 = bbox(o); dump.append({"name": o.name, "x": [round(x0, 2), round(x1, 2)], "y": [round(y0, 2), round(y1, 2)], "z": [round(z0, 2), round(z1, 2)]})
    json.dump(dump, open(os.environ["DUMP_BBOX"], "w"), indent=0); print("DUMPED", len(dump), "objects to", os.environ["DUMP_BBOX"]); sys.exit(0)
todo = []
for v in VIEWS_ASKED:
    if v == "all": todo += list(VIEWS)
    elif v == "orbit": todo += [k for k in VIEWS if k.endswith("-open") and k.startswith("az")]
    elif v == "closed": todo += [k for k in VIEWS if k.endswith("-closed")]
    elif v == "details": todo += [k for k in VIEWS if not k.startswith("az")]
    else: todo.append(v)
for v in todo: render(v)
print("SCENE-DONE", len(todo), "views")
