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
EAST = [(-96.0, "LTE"), (-48.0, "IRIDIUM"), (0.0, "LORA"), (48.0, "WIFI P2P A"), (96.0, "WIFI P2P B")]
RIBS_X = (-170.0, -95.0, -18.0, 60.0, 137.0)
CPLATE = dict(cx=-56.0, cz=54.0, w=54.0, h=82.0)
GROUND = -8.0                         # the ground plane under the feet (reset from the case body when Peli's STL is used)
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
# ------------------------------------------------------------------ the Peli 1450: Peli's bodies when their STL exists (CASE_MODE=stl), else modelled from the numbers
CASE_MODE = os.environ.get("CASE_MODE", "stl" if os.path.exists(os.path.join(STL, "case1450_bottom.stl")) else "model")
base = lid = None
if CASE_MODE == "stl":
    # Peli's 1451-931 STEP frames: X the long axis, Y up, Z the short axis (bottom y -25.4..109.0 with the rim at 109; top y 0..70.9 with its latch straps
    # hanging LID_DROP below the lid rim). Rotated 90 degrees about X into the case frame; CASE_FLIP=1 turns the bodies 180 degrees about Z if the hinge
    # side comes out at the front (checked on the preview render).
    ROT = Matrix.Rotation(math.radians(90), 4, "X")
    if os.environ.get("CASE_FLIP"): ROT = Matrix.Rotation(math.pi, 4, "Z") @ ROT
    base = import_stl("case_base", "case1450_bottom.stl", M["orange"], matrix=ROT, fit=(True, "max", RIM), smooth=True)
    lid = import_stl("case_lid", "case1450_top.stl", M["orange"], matrix=ROT, fit=(True, "min", RIM - float(os.environ.get("LID_DROP", "0.0"))), smooth=True)   # 6 Sep 2026: the 1451-931 lid mesh spans 0 to 70.9 from its own rim (no straps below it), so it sits ON the rim; the 25.4 mm drop of the 1520 lid drew the seam under the antenna sockets
    if base is not None and (bbox(base)[5] - bbox(base)[4]) < 90: CASE_MODE = "model"; bpy.data.objects.remove(base, do_unlink=True); base = None
    if lid is not None and CASE_MODE == "model": bpy.data.objects.remove(lid, do_unlink=True); lid = None
if CASE_MODE == "stl":
    x0, x1, y0, y1, z0, z1 = bbox(base); BW, BL, GROUND = x1 - x0 - 12.0, y1 - y0, z0 - 0.4   # the body's own outline (the catalogue 411 x 329 counts the latch straps); the ground under its slab
    print("case from Peli's STEP: outer %.1f x %.1f, base bottom at %.1f" % (x1 - x0, y1 - y0, z0), flush=True)
if CASE_MODE == "model":
    CR = 12.0
    base = rounded_box("case_base", BW - 6, BL - 6, RIM + 6.0, CR, (0, 0, -6.0), M["orange"], top_scale=(BW / (BW - 6), BL / (BL - 6)))
    cav = rounded_box("cavity", FLOOR_W, FLOOR_L, RIM + 5.0, 10.0, (0, 0, 0.0), M["orange"], top_scale=(RIM_W / FLOOR_W, RIM_L / FLOOR_L)); cut(base, cav)
    rim_step = rounded_box("rim_step", SKIRT[0], SKIRT[1], SKIRT[2] + 1.0, 10.0, (0, 0, RIM - SKIRT[2]), M["orange"]); cut(base, rim_step)
    lid = rounded_box("case_lid", BW, BL, LIDH, CR, (0, 0, RIM), M["orange"], top_scale=((BW - 8) / BW, (BL - 8) / BL))
    lcav = rounded_box("lid_cavity", RIM_W, RIM_L, LIDH - 5.0, 10.0, (0, 0, RIM - 1.0), M["orange"], top_scale=(0.95, 0.94)); cut(lid, lcav)
    field = rounded_box("lid_field", BW - 60, BL - 60, 10.0, 20.0, (0, 0, RIM + LIDH - 6.0), M["orange"]); cut(lid, field)
# the features Peli's envelope STEP leaves out (and the modelled body needs): end-wall ribs, feet, corner bosses, padlock protectors, latches, handle, valve, hinge, the model text
FEET_Z = GROUND + 0.4
for sx in (-1, 1):
    for k, y in enumerate((-105, -75, -45, -15, 15, 45, 75, 105)):
        box("rib_b_%d_%d" % (sx, k), (6.0, 8.0, RIM - 12.0 - FEET_Z), (sx * (BW / 2 + 1.0), y, (RIM - 12.0 + FEET_Z) / 2), M["orange"], bevel=2.0)
        box("rib_l_%d_%d" % (sx, k), (6.0, 8.0, 30.0), (sx * (BW / 2 - 1.0), y, RIM + 22.0), M["orange"], bevel=2.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl("foot_%d_%d" % (sx, sy), 22.0, 3.0, (sx * 165, sy * 125, FEET_Z - 1.5), M["rubber"])
        box("corner_b_%d_%d" % (sx, sy), (30, 30, 50), (sx * (BW / 2 - 12), sy * (BL / 2 - 12), FEET_Z + 28.0), M["orange2"], bevel=6.0)
        box("corner_l_%d_%d" % (sx, sy), (30, 30, 34), (sx * (BW / 2 - 12), sy * (BL / 2 - 12), RIM + 20.0), M["orange2"], bevel=6.0)
    box("padlock_%d" % sx, (30, 20, 22), (sx * (BW / 2 - 22), -BL / 2 - 7, RIM), M["orange2"], bevel=4.0); cyl("padlock_hole_%d" % sx, 7, 22, (sx * (BW / 2 - 22), -BL / 2 - 7, RIM), M["black"], axis="Y")
FY = -BL / 2
for sx in (-1, 1):
    x = sx * 100
    box("latch_base_%d" % sx, (50, 10, 36), (x, FY - 5, RIM - 24), M["orange2"], bevel=3.0); box("latch_lid_%d" % sx, (42, 11, 30), (x, FY - 6, RIM + 17), M["orange2"], bevel=4.0)
    box("latch_lever_%d" % sx, (48, 12, 60), (x, FY - 16, RIM - 6), M["black"], bevel=5.0); box("latch_pull_%d" % sx, (36, 6, 12), (x, FY - 24, RIM - 30), M["black"], bevel=2.5)
    cyl("latch_pin_%d" % sx, 6, 54, (x, FY - 14, RIM + 30), M["steel_dark"], axis="X")
box("handle_bar", (140, 20, 22), (-9, FY - 15, 52), M["black"], bevel=6.0)
for sx in (-1, 1): box("handle_boss_%d" % sx, (24, 16, 32), (-9 + sx * 82, FY - 8, 52), M["orange2"], bevel=4.0)
cyl("valve", 26, 8, (-16, FY - 4.0, 62), M["black"], axis="Y", bevel=1.5); cyl("valve_cap", 19, 4, (-16, FY - 10, 62), M["steel_dark"], axis="Y")
cyl("hinge_bar", 13, 300, (0, BL / 2 + 3, RIM), M["orange2"], axis="X")
for x in (-120, 0, 120): box("hinge_knuckle_%d" % x, (40, 14, 26), (x, BL / 2 + 2.5, RIM), M["orange2"], bevel=4.0)
label("peli_text", "1450", (130, FY - 1.0, 88), 14.0, M["orange2"], rot=(math.pi / 2, 0, 0))
# the inner ribs of the long walls (1451-931 section B-B) in both modes: the connector plate stands between the ribs at X -95 and -18
for sy in (-1, 1):
    for x in RIBS_X: box("case_rib_in_%d_%d" % (sy, x), (5.0, 5.0, 94.0), (x, sy * (FLOOR_L / 2 + 2.0), 47.0), M["orange"])
CASE = [o for o in bpy.data.objects if o.name.startswith(("case_", "rib_", "foot_", "corner_", "padlock", "latch_", "handle_", "valve", "hinge_", "peli_text"))]
LID = [o for o in CASE if o.name.startswith(("case_lid", "rib_l_", "corner_l_", "latch_lid", "latch_lever", "latch_pull", "latch_pin", "hinge_"))]
hinge = Vector((0, BL / 2 + 3, RIM)); CLOSED = {o.name: o.matrix_world.copy() for o in LID}
def set_lid(open_):
    for o in LID:
        base_m = CLOSED[o.name]
        o.matrix_world = (Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-100), 4, "X") @ Matrix.Translation(-hinge) @ base_m) if open_ else base_m
frame = import_stl("panel_frame", "frame1450.stl", M["black"], fit=(True, "max", RIM))
# ------------------------------------------------------------------ the back wall: the upright connector plate between the ribs, the shore and USB receptacles, both cables plugged
WALL_Y = BL / 2
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
    cyl("rod_%d_%d" % (x, y), 3.0, 118.0, (x, y, 59.0), M["steel"])
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
label("nameplate", "MESHSAT FIELD KIT V2", (P.NAMEPLATE[0], P.NAMEPLATE[1] + 2.5, FACE + 0.05), 4.2, M["white"]); label("nameplate_2", "S/N ______   NUCLEAR LIGHTERS", (P.NAMEPLATE[0], P.NAMEPLATE[1] - 5.5, FACE + 0.05), 3.0, M["white"])
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
WX = BW / 2; WALL_IN = FLOOR_W / 2 + 4.0
ANT = {"VHF": (170, 9), "WIFI 2.4": (110, 9), "SDR": (150, 9), "LTE": (200, 10), "LORA": (140, 9), "WIFI P2P A": (120, 9), "WIFI P2P B": (120, 9)}
NEST = {"VHF": SMA_JACKS[0], "WIFI 2.4": SMA_JACKS[1], "GNSS": SMA_JACKS[2], "SDR": SMA_JACKS[3], "LTE": SMA_JACKS[4], "IRIDIUM": SMA_JACKS[5], "LORA": SMA_JACKS[6]}
for sx, sites in ((-1, WEST), (1, EAST)):
    for y, nm in sites:
        z = SMA_Z; tag = nm.replace(" ", "_").lower()
        cyl("bulk_" + tag, 9.5, 3.0, (sx * (WX + 1.5), y, z), M["steel"], axis="X", verts=6); cyl("bulk_sma_" + tag, 6.5, 11, (sx * (WX + 7), y, z), M["gold"], axis="X")
        cyl("bulk_in_" + tag, 8.0, 10, (sx * (WALL_IN + 3), y, z), M["gold"], axis="X"); cyl("bulk_nut_in_" + tag, 8.0, 2.0, (sx * (WALL_IN - 1), y, z), M["steel"], axis="X", verts=6)
        ax = sx * (WX + 15)
        # 6 Sep 2026 (owner, the first 1450 set): no invented antennas. The record fixes two forms only: the Iridium patch (its top at Z 82 on the east wall)
        # and the u-blox GNSS puck; every other port is drawn as its bulkhead jack, the whip parts are not chosen yet. WHIPS=1 restores the old stand-ins.
        if os.environ.get("WHIPS") and nm in ANT:
            L, d = ANT[nm]; cyl("ant_elbow_" + tag, 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_base_" + tag, 12, 24, (ax, y, z + 4 + 12), M["dark"]); cyl("ant_" + tag, d, L, (ax, y, z + 16 + L / 2), M["rubber"]); sphere("ant_tip_" + tag, d / 2 + 1.5, (ax, y, z + 16 + L), M["rubber"])
        elif nm == "IRIDIUM": cyl("ant_iridium", 76, 18, (sx * (WX + 9), y, 82 - 38), M["white"], bevel=2.0, axis="X")   # the patch flat on the east wall, its top at Z 82, fed by a short lead from the jack above it
        elif nm == "GNSS": cyl("ant_gnss", 48, 14, (sx * (WX + 7), y, 82 - 24), M["dark"], bevel=2.0, axis="X")          # the puck flat on the west wall below its jack
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
        else:      # the two WiFi P2P leads (ruling 5 Sep 05:45): MHF4 leads from the M.2 card on B15 to their end-wall couplers, not blind-mated
            p2 = (xdrop, y, ZB + 6.0); tube("pig_%s_1" % tag, p0, p1, 2.0, M["coax"]); sphere("pig_%s_k1" % tag, 2.0, p1, M["coax"]); tube("pig_%s_2" % tag, p1, p2, 2.0, M["coax"]); sphere("pig_%s_k2" % tag, 2.0, p2, M["coax"]); tube("pig_%s_3" % tag, p2, (66.0, 60.0 + (2 if "B" in nm else -2), ZB + 6.0), 2.0, M["coax"])
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
VIEWS = {}
# 6 Sep 2026, second set (owner: "the inside of the case is the most interesting part"): eight orbit views with the lid open at el 40, four closed
# views, and everything else inside: the stack level by level with the boards above removed, the face from both sides, the walls from inside.
for az in range(0, 360, 45): VIEWS["az%03d-el40-open" % az] = dict(cam=camera("cam_%03d_40" % az, orbit(az, 40), (0, 0, 70), 42), lid=True)
for az in (0, 90, 180, 270): VIEWS["az%03d-el20-closed" % az] = dict(cam=camera("cam_%03d_20c" % az, orbit(az, 20), (0, 0, 70), 42), lid=False)
B15_PARTS = ("pcb_b15", "cm5_", "cr2032", "display_flex", "gnss_neo", "lora_wio", "lte_", "panel_ribbon", "sdr_", "usb_a_recept", "wifi_m2_", "zigbee_e72", "rockblock9704")   # the board and everything drawn on it
D7_PARTS = B15_PARTS + ("pcb_d7", "dmr858m")
A21_PARTS = D7_PARTS + ("pcb_a21", "sma_jack", "sma_nut", "sma_nest")   # the wall pigtails end at the dock clamps (6 Sep 2026), so they stay when A21 is lifted
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
})
PANEL_PREFIX = ("plate", "pcb_c6", "standoff_c6", "screw_c6", "td2", "epaper", "sw_", "sounder", "led_", "lbl_", "nameplate", "logo_")
def walk(prefixes):
    for o in bpy.data.objects:
        p = o
        while p is not None:
            if p.name.startswith(prefixes): yield o; break
            p = p.parent
def hide(prefixes, flag):
    for o in walk(prefixes): o.hide_render = flag
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
