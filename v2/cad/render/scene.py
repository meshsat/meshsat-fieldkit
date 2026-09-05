# MeshSat field kit V2, concept renders, Blender scene: a modelled Peli 1520 (Peli's STEP is only an envelope), the 1520PF frame with the sealed panel C5,
# the board stack (E4, E5, A20, D6, B13), the battery module, end-wall antennas, the back-wall connector plate; a cutaway view shows the stack inside the case.
# Case frame in mm: X along the long axis, +Y = back wall (hinge), Z up from the cavity floor.
# Run headless: blender -b -P scene.py -- <out dir> [views...]   (views: overview, hero, top, detail, cutaway, closed, all)
import bpy, bmesh, math, os, sys
from mathutils import Vector, Matrix
R = os.path.expanduser("~/render3d"); STL = R + "/stl"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0] if args else R + "/out2"; VIEWS = args[1:] or ["all"]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.unit_settings.system = "METRIC"; S.unit_settings.scale_length = 0.001; S.unit_settings.length_unit = "MILLIMETERS"
RIM = 124.87; FACE = RIM - 8.8; PZ = FACE - 2.0
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
         black=mat("matte_black", (0.02, 0.02, 0.02), 0.65, bump=0.2), mask=mat("mask_black", (0.03, 0.03, 0.035), 0.45),
         gold=mat("enig", (0.95, 0.75, 0.30), 0.35, 1.0), steel=mat("steel", (0.62, 0.62, 0.64), 0.28, 1.0), steel_dark=mat("steel_dark", (0.3, 0.3, 0.32), 0.35, 1.0),
         alu=mat("aluminium", (0.75, 0.76, 0.78), 0.4, 1.0), chrome=mat("chrome", (0.85, 0.85, 0.87), 0.12, 1.0),
         glass=mat("glass", (0.6, 0.7, 0.8), 0.05, 0.0, 0.18), lens=mat("lens", (0.85, 0.88, 0.92), 0.05, 0.0, 0.2), paper=mat("epaper", (0.92, 0.92, 0.9), 0.75),
         green=mat("led_green", (0.15, 0.95, 0.25), 0.3, 0.0, 1.0, 3.0), amber=mat("led_amber", (1.0, 0.62, 0.06), 0.3, 0.0, 1.0, 3.0), redled=mat("led_red", (1.0, 0.1, 0.05), 0.3, 0.0, 1.0, 3.0),
         white=mat("plastic_white", (0.9, 0.9, 0.88), 0.5), rubber=mat("rubber", (0.04, 0.04, 0.04), 0.9, bump=0.3), dark=mat("dark_plastic", (0.08, 0.08, 0.09), 0.6),
         red=mat("red", (0.8, 0.05, 0.05), 0.4), pcb=mat("pcb_green", (0.05, 0.25, 0.1), 0.5), tin=mat("tin", (0.7, 0.72, 0.72), 0.3, 1.0), gray=mat("gray_plastic", (0.35, 0.35, 0.37), 0.6),
         ledoff=mat("led_off", (0.55, 0.55, 0.5), 0.25, 0.0, 0.7), wire_red=mat("wire_red", (0.7, 0.05, 0.05), 0.5), wire_blk=mat("wire_black", (0.05, 0.05, 0.05), 0.5), ribbon=mat("ribbon", (0.4, 0.4, 0.42), 0.6))
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
def import_stl(name, fn, m, matrix):
    bpy.ops.wm.stl_import(filepath=os.path.join(STL, fn)) if hasattr(bpy.ops.wm, "stl_import") else bpy.ops.import_mesh.stl(filepath=os.path.join(STL, fn))
    o = bpy.context.selected_objects[0]; o.name = name; o.matrix_world = matrix; assign(o, m)
    for p in o.data.polygons: p.use_smooth = False
    return o
def import_board(name, fn, z, extra=Matrix.Identity(4), hide_names=()):
    """A KiCad GLB exported with the case-frame user origin (case mm after the import, board bottom at z 0): mask matte black, pads gold, models dark."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(R, fn)); new = [o for o in bpy.data.objects if o not in before]
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
# ------------------------------------------------------------------ the Peli 1520: outer 508 x 378, base 150 tall (rim at Z 124.87, feet below), lid 71.5; cavity 413.8 x 283.6 at the floor, 448.4 x 318.1 at the rim
BW, BL, CR = 508.0, 378.0, 14.0
base = rounded_box("case_base", BW - 6, BL - 6, RIM + 22.0, CR, (0, 0, -22.0), M["orange"], top_scale=(BW / (BW - 6), BL / (BL - 6)))
cav = rounded_box("cavity", 413.8, 283.6, RIM + 5.0, 10.0, (0, 0, 0.0), M["orange"], top_scale=(448.4 / 413.8, 318.1 / 283.6)); cut(base, cav)
rim_step = rounded_box("rim_step", 454.1, 323.9, 8.0, 10.0, (0, 0, RIM - 7.92), M["orange"]); cut(base, rim_step)     # the rim step the frame skirt seats in
lid = rounded_box("case_lid", BW, BL, 71.5, CR, (0, 0, RIM), M["orange"], top_scale=((BW - 8) / BW, (BL - 8) / BL))
lcav = rounded_box("lid_cavity", 448.4, 318.1, 46.1, 10.0, (0, 0, RIM - 1.0), M["orange"], top_scale=(0.95, 0.94)); cut(lid, lcav)
field = rounded_box("lid_field", BW - 70, BL - 70, 14.0, 22.0, (0, 0, RIM + 71.5 - 9.0), M["orange"]); cut(lid, field)   # the recessed top field
# ribs on both end walls (base and lid), a Peli signature
for sx in (-1, 1):
    for k, y in enumerate((-135, -95, -55, -15, 25, 65, 105, 145)):
        box("rib_b_%d_%d" % (sx, k), (7.0, 9.0, 110.0), (sx * (BW / 2 + 1.0), y, 62.0), M["orange"], bevel=2.0)
        box("rib_l_%d_%d" % (sx, k), (7.0, 9.0, 40.0), (sx * (BW / 2 - 1.0), y, RIM + 34.0), M["orange"], bevel=2.0)
# corner bosses, rubber feet, padlock protectors
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl("foot_%d_%d" % (sx, sy), 28.0, 6.0, (sx * 200, sy * 140, -22.0 - 3.0), M["rubber"])
        box("corner_b_%d_%d" % (sx, sy), (34, 34, 60), (sx * (BW / 2 - 14), sy * (BL / 2 - 14), 30.0), M["orange2"], bevel=6.0)
        box("corner_l_%d_%d" % (sx, sy), (34, 34, 44), (sx * (BW / 2 - 14), sy * (BL / 2 - 14), RIM + 30.0), M["orange2"], bevel=6.0)
    box("padlock_%d" % sx, (36, 22, 26), (sx * (BW / 2 - 26), -BL / 2 - 8, RIM), M["orange2"], bevel=4.0); cyl("padlock_hole_%d" % sx, 8, 24, (sx * (BW / 2 - 26), -BL / 2 - 8, RIM), M["black"], axis="Y")
# two double-throw latches and the folding handle on the front wall, the pressure valve, the rear hinge
FY = -BL / 2
for sx in (-1, 1):
    x = sx * 118
    box("latch_base_%d" % sx, (56, 10, 40), (x, FY - 5, RIM - 26), M["orange2"], bevel=3.0)
    box("latch_lid_%d" % sx, (46, 11, 44), (x, FY - 6, RIM + 24), M["orange2"], bevel=4.0)
    box("latch_lever_%d" % sx, (54, 12, 70), (x, FY - 16, RIM - 4), M["black"], bevel=5.0)
    box("latch_pull_%d" % sx, (40, 6, 14), (x, FY - 24, RIM - 30), M["black"], bevel=2.5)
    cyl("latch_pin_%d" % sx, 7, 60, (x, FY - 14, RIM + 42), M["steel_dark"], axis="X")
box("handle_bar", (150, 22, 24), (0, FY - 16, 62), M["black"], bevel=6.0)
for sx in (-1, 1): box("handle_boss_%d" % sx, (26, 18, 36), (sx * 88, FY - 8, 62), M["orange2"], bevel=4.0)
cyl("valve", 30, 9, (-185, FY - 4.5, 70), M["black"], axis="Y", bevel=1.5); cyl("valve_cap", 22, 4, (-185, FY - 11, 70), M["steel_dark"], axis="Y")
cyl("hinge_bar", 15, 320, (0, BL / 2 + 4, RIM), M["orange2"], axis="X")
for x in (-140, 0, 140): box("hinge_knuckle_%d" % x, (44, 16, 30), (x, BL / 2 + 3, RIM), M["orange2"], bevel=4.0)
label("peli_text", "1520", (150, FY - 1.0, 100), 18.0, M["orange2"], rot=(math.pi / 2, 0, 0))
CASE = [o for o in bpy.data.objects if o.name.startswith(("case_", "rib_", "foot_", "corner_", "padlock", "latch_", "handle_", "valve", "hinge_", "peli_text"))]
LID = [o for o in CASE if o.name.startswith(("case_lid", "rib_l_", "corner_l_", "latch_lid", "latch_lever", "latch_pull", "latch_pin", "hinge_"))]
hinge = Vector((0, BL / 2 + 4, RIM)); CLOSED = {o.name: o.matrix_world.copy() for o in LID}
def set_lid(open_):
    for o in LID:
        base_m = CLOSED[o.name]
        o.matrix_world = (Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-100), 4, "X") @ Matrix.Translation(-hinge) @ base_m) if open_ else base_m
frame = import_stl("panel_frame", "panel_frame.stl", M["black"], Matrix.Translation((0, 0, RIM - 8.5)))
# connector plate on the back wall (outside): 82 x 54 x 3 at X -133..-51, Z 28..82
WALL_Y = BL / 2
plate = box("conn_plate", (82, 3, 54), (-92, WALL_Y + 1.5, 55), M["alu"])
for x, d, fl, nm in ((-110, 19.05, 28.9, "shore"), (-74, 23.01, 31.29, "usb")):
    box("recept_flange_" + nm, (fl, 4, fl), (x, WALL_Y + 5, 55), M["steel"], bevel=1.0); cyl("recept_" + nm, d + 4, 14, (x, WALL_Y + 12, 55), M["steel_dark"], axis="Y"); cyl("recept_cap_" + nm, d + 6, 4, (x, WALL_Y + 20, 55), M["dark"], axis="Y")
# ------------------------------------------------------------------ the floor: dock strip E4, block E5, rods, battery module
import_board("pcb_e4", "pcb-e1-dock.glb", 0.0); import_board("pcb_e5", "pcb-e5-block.glb", 6.0)
for (x, y) in ((-155.5, -63.0), (-117.5, -63.0), (-155.5, -82.0), (-117.5, -82.0)): cyl("standoff_e5_%d" % int(x), 5.0, 6.0, (x, y, 3.0), M["steel"])
box("traco_ten40", (50.8, 25.4, 10.2), (-40, -81, 1.6 + 5.1), M["dark"])
for (x, y) in ((-110.5, -73.0), (110.5, -73.0), (-110.5, 73.0), (110.5, 73.0)):
    cyl("rod_%d_%d" % (x, y), 3.0, 118.0, (x, y, 59.0), M["steel"])
    for z in (1.6, 16.6, 56.2): cyl("nut_%d_%d_%d" % (x, y, z), 5.5, 2.4, (x, y, z + 1.2), M["steel"], verts=6)
    cyl("spacer_%d_%d_a" % (x, y), 6.0, 13.4, (x, y, 1.6 + 6.7), M["alu"]); cyl("spacer_%d_%d_b" % (x, y), 6.0, 38.0, (x, y, 16.6 + 19.0), M["alu"])
MOD = Matrix.Translation((121.0, -137.0, 6.0)); import_stl("module_base", "module_base.stl", M["gray"], MOD); import_stl("module_lid", "module_lid.stl", M["dark"], MOD)
import_stl("module_cradle", "module_cradle.stl", M["black"], Matrix.Translation((121.0, -137.0, 5.0)))
cyl("xt60", 16, 18, (161, -125, 15), M["amber"], axis="Y"); cyl("module_lead_r", 3.2, 30, (158, -95, 4), M["wire_red"], axis="Y"); cyl("module_lead_b", 3.2, 30, (164, -95, 4), M["wire_blk"], axis="Y")
# ------------------------------------------------------------------ PCB-A A20, the mezzanine D6, PCB-B B13 and what rides on it
import_board("pcb_a20", "pcb-a-power.glb", 15.0)
import_board("pcb_d6", "pcb-d-aprs.glb", 22.6, Matrix.Translation((45.0, 0.0, 0.0)))
for (x, y) in ((10, -26), (80, -26), (10, 26), (80, 26)): cyl("standoff_d_%d_%d" % (x, y), 5.0, 6.0, (x, y, 19.6), M["steel"])
box("dmr858m", (48, 26, 6), (55.5, -2.0, 38.2), M["tin"]); box("dmr858m_sink", (48, 26, 8), (55.5, -2.0, 45.2), M["alu"])
for k, (x, y) in enumerate(((-100, -56), (-84, -56), (-26, -56), (-12, -56), (70, -74), (92, -74), (103, -54))):
    cyl("sma_jack_%d" % k, 6.5, 9.0, (x, y, 21.1), M["gold"]); cyl("sma_nut_%d" % k, 8.0, 2.0, (x, y, 17.6), M["steel"], verts=6)
for k, y in enumerate((-68, -58, -48)):     # the three rail leads A to B
    cyl("lead_r_%d" % k, 1.8, 36, (-92 - 1.5, y, 35), M["wire_red"]); cyl("lead_b_%d" % k, 1.8, 36, (-92 + 1.5, y, 35), M["wire_blk"])
import_board("pcb_b13", "pcb-b-compute.glb", 54.6)
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
box("display_flex", (16, 0.3, 58), (-50, 22, ZB + 29), M["amber"]); box("panel_ribbon", (0.9, 25.4, 58), (150, 72, ZB + 29), M["ribbon"])
# ------------------------------------------------------------------ the panel C5 and everything on its face
c5 = import_board("pcb_c5", "pcb-c-display.glb", PZ, hide_names=tuple("D%d" % k for k in range(1, 17)))
TD2 = Matrix.Translation((0.0, -10.0, FACE + 1.1 - 5.0)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Translation((0, -2.95, 0))
import_stl("td2", "td2.stl", M["black"], TD2)
scr = box("td2_screen", (160, 90, 0.15), (0, -10, FACE + 1.2), M["dark"]); textured(scr, "ui.png", 4.0)
box("td2_glass", (189.32, 120.24, 0.8), (0, -10, FACE + 1.7), M["glass"])
EPD = Matrix.Translation((30.0, 100.0, FACE - 3.0)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((-269.3, -177.4, 0.0)); import_stl("epaper", "epaper.stl", M["dark"], EPD)
epd = box("epaper_glass", (92.99, 53.0, 0.6), (30, 100, FACE - 0.3), M["paper"]); textured(epd, "epaper.png", 0.0)
box("epaper_lens", (107.19, 66.6, 2.0), (30, 100, FACE + 0.4 + 1.0), M["lens"], bevel=0.8)
def pushbutton(name, x, y, D, ring, on=True):
    """C&K ATP anti-vandal: stainless bezel with a bevel, the illuminated ring, a low domed cap, the body below the face."""
    cyl(name + "_bezel", D + 3.2, 3.0, (x, y, FACE + 1.5), M["steel"], bevel=1.0); cyl(name + "_body", D, 26, (x, y, FACE - 2 - 13), M["dark"])
    torus(name + "_ring", D / 2 - 1.6, 0.9, (x, y, FACE + 3.1), ring if on else M["ledoff"])
    cap = cyl(name + "_cap", D - 6.0, 3.0, (x, y, FACE + 4.2), M["steel_dark"], bevel=1.2); sphere(name + "_dome", D - 6.0, (x, y, FACE + 4.2 - (D - 6.0) / 2 + 3.4), M["steel_dark"])
pushbutton("sw_main", -150, 100, 19.2, M["green"]); pushbutton("sw_pi", -110, 100, 16.2, M["amber"]); pushbutton("sw_test", -70, 100, 16.2, M["white"], on=False)
def toggle(name, x, y, L, tilt, locking=False, boot=False):
    cyl(name + "_nut", 10.4, 2.8, (x, y, FACE + 1.4), M["chrome"], verts=6); cyl(name + "_bush", 6.35, 8.5, (x, y, FACE + 2.8), M["chrome"])
    if locking: cyl(name + "_lock", 9.0, 5.0, (x, y, FACE + 7.8), M["steel_dark"], bevel=0.8)
    t = math.radians(tilt); base_z = FACE + 9.0
    lever = cone(name + "_lever", 4.6, 6.4, L, (x, y - math.sin(t) * L / 2, base_z + math.cos(t) * L / 2), M["chrome"], rot=(t, 0, 0))
    sphere(name + "_tip", 7.2, (x, y - math.sin(t) * L, base_z + math.cos(t) * L), M["red"] if locking else M["chrome"])
    if boot: cone(name + "_boot", 15.0, 6.0, 14.0, (x, y - math.sin(t) * 5.5, base_z + math.cos(t) * 5.5), M["rubber"], rot=(t, 0, 0))
    cyl(name + "_body", 13, 22, (x, y, FACE - 2 - 11), M["dark"])
toggle("sw_light", 120, 100, 18, 25, boot=True); toggle("sw_sos", 170, 42, 22, 24, True); toggle("sw_emcon", 170, 0, 22, 24, True); toggle("sw_zero", 170, -42, 22, 24, True)
cyl("sounder", 34, 3.5, (-180, -100, FACE + 1.75), M["black"], bevel=1.2)
for k, rr in enumerate((5.0, 8.5, 12.0)): torus("sounder_ring_%d" % k, rr, 0.7, (-180, -100, FACE + 3.5), M["dark"])
cyl("sounder_body", 30, 20, (-180, -100, FACE - 2 - 10), M["dark"])
LEDS = [("D1", 45, "MSTR WARN", "redled", False), ("D2", 36, "MSTR CAUT", "amber", False), ("D3", 27, "TX", "redled", False), ("D4", 18, "SOS ACTIVE", "redled", False), ("D5", 9, "SAT", "green", True), ("D6", 0, "MESH", "green", True),
        ("D7", -9, "LTE", "green", True), ("D8", -18, "GPS", "green", True), ("D9", -27, "SHORE", "amber", True), ("D10", -36, "CHARGE", "amber", True), ("D11", -45, "MSG", "green", False)]
def led(name, x, y, m, on):
    cyl(name + "_bezel", 4.6, 1.0, (x, y, FACE + 0.5), M["black"]); sphere(name, 3.0, (x, y, FACE + 0.6), m if on else M["ledoff"])
for ref, y, txt, col, on in LEDS:
    led("led_" + ref, -120, y, M[col], on); label("lbl_" + ref, txt, (-126, y - 1.2, FACE + 0.05), 3.0, M["white"], align="RIGHT")
for ref, x in (("D12", -82), ("D13", -76), ("D14", -70), ("D15", -64), ("D16", -58)): led("led_" + ref, x, 123, M["green"], x < -60)
label("lbl_bar", "BATTERY", (-70, 128, FACE + 0.05), 3.5, M["white"])
label("nameplate", "MESHSAT FIELD KIT V2   S/N ______   NUCLEAR LIGHTERS", (0, -114, FACE + 0.05), 4.5, M["white"])
for x, y, txt in ((-150, 86, "MAIN"), (-110, 86, "PI"), (-70, 86, "TEST"), (120, 86, "LIGHT"), (170, 55, "SOS"), (170, 13, "EMCON"), (170, -29, "ZEROIZE")): label("lbl_" + txt, txt, (x, y, FACE + 0.05), 4.0, M["white"])
# ------------------------------------------------------------------ end-wall antennas: bulkheads at Z 55, Y -60, -30, +30, +60; whips upright on right-angle adapters
WX = BW / 2
ANT = {"UHF": (170, 9), "WIFI 2.4": (110, 9), "SDR": (150, 9), "LTE": (200, 10), "LORA": (140, 9), "WIFI P2P A": (120, 9), "WIFI P2P B": (120, 9)}
for sx, sites in ((-1, ((-60, "UHF"), (-30, "WIFI 2.4"), (30, "GNSS"), (60, "SDR"))), (1, ((-60, "LTE"), (-30, "IRIDIUM"), (30, "LORA"), (60, "WIFI P2P A"), (-45, "WIFI P2P B", 90)))):
    for site in sites:
        y, nm = site[0], site[1]; z = site[2] if len(site) > 2 else 55
        cyl("bulk_" + nm, 9.5, 3.0, (sx * (WX + 1.5), y, z), M["steel"], axis="X", verts=6); cyl("bulk_sma_" + nm, 6.5, 11, (sx * (WX + 7), y, z), M["gold"], axis="X")
        ax = sx * (WX + 15)
        if nm in ANT:
            L, d = ANT[nm]; cyl("ant_elbow_" + nm, 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_base_" + nm, 12, 24, (ax, y, z + 4 + 12), M["dark"]); cyl("ant_" + nm, d, L, (ax, y, z + 16 + L / 2), M["rubber"]); sphere("ant_tip_" + nm, d * 1.25, (ax, y, z + 16 + L), M["rubber"])
        elif nm == "IRIDIUM": cyl("ant_elbow_iridium", 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_iridium", 76, 18, (ax, y, z + 10 + 9), M["white"], bevel=2.0)
        elif nm == "GNSS": cyl("ant_elbow_gnss", 8, 9, (ax, y, z), M["gold"], axis="X"); cyl("ant_gnss", 48, 14, (ax, y, z + 8 + 7), M["dark"], bevel=2.0)
        else: cyl("ant_plug", 9, 6, (sx * (WX + 13), y, z), M["steel"], axis="X", verts=6)
# ------------------------------------------------------------------ world, lights, cameras, views
S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SAMPLES", "256")); S.cycles.use_denoising = False; S.cycles.device = "CPU"
S.render.resolution_x = 2000; S.render.resolution_y = 1400; S.render.resolution_percentage = int(os.environ.get("RESPCT", "100"))
S.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "AgX"
for lk in ("Medium High Contrast", "AgX - Medium High Contrast", "None"):
    try: S.view_settings.look = lk; break
    except TypeError: pass
world = bpy.data.worlds.new("w"); S.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.78, 0.8, 0.85, 1); bg.inputs[1].default_value = 1.1
def light(name, at, energy, size):
    bpy.ops.object.light_add(type="AREA", location=at); L = bpy.context.object; L.name = name; L.data.energy = energy; L.data.size = size
    L.rotation_euler = (Vector((0, 0, 60)) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return L
light("key", (-500, -900, 1000), 5.5e6, 700); light("fill", (900, -300, 700), 2.2e6, 900); light("rim", (200, 900, 800), 2.2e6, 500)
bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, -28)); floor = bpy.context.object; floor.name = "ground"; assign(floor, mat("ground", (0.62, 0.62, 0.64), 0.85))
def camera(name, at, look, lens=50):
    bpy.ops.object.camera_add(location=at); c = bpy.context.object; c.name = name; c.data.lens = lens; c.data.clip_end = 20000
    c.rotation_euler = (Vector(look) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return c
CAMS = {"overview": camera("cam_overview", (-720, -920, 640), (0, 0, 95), 40), "hero": camera("cam_hero", (-410, -570, 480), (-20, 10, 105), 55),
        "top": camera("cam_top", (0, -120, 980), (0, 0, 100), 50), "detail": camera("cam_detail", (-215, 25, 285), (-112, 66, 116), 55),
        "cutaway": camera("cam_cutaway", (-390, -660, 330), (-10, 0, 62), 46), "closed": camera("cam_closed", (-700, -860, 520), (0, 0, 80), 40)}
PANEL_PREFIX = ("pcb_c5", "td2", "epaper", "sw_", "sounder", "led_", "lbl_", "nameplate")
def walk(prefixes):
    for o in bpy.data.objects:
        p = o
        while p is not None:
            if p.name.startswith(prefixes): yield o; break
            p = p.parent
def hide(prefixes, flag):
    for o in walk(prefixes): o.hide_render = flag
set_lid(True)
def render(view):
    S.camera = CAMS[view]; set_lid(view != "closed"); hide(("ant_",), view == "closed"); hide(("peli_text",), view == "cutaway")
    if view == "cutaway":   # the front wall of the case and the frame's front bar removed (the floor and the other walls stay); the panel lifted 60 mm on its ribbon and flex
        tool = box("cut_tool", (700, 70, 400), (0, -BL / 2 - 20 + 35, 120), M["dark"]); keep = []
        for o in CASE + [frame]:
            if o.type != "MESH": continue
            md = o.modifiers.new("cutv", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = tool; md.solver = "EXACT"; keep.append((o, md))
        tool.hide_render = True
        for o in walk(PANEL_PREFIX):
            if o.parent is None or o.name == "pcb_c5": o.matrix_world = Matrix.Translation((0, 0, 60)) @ o.matrix_world
        for o in bpy.data.objects:
            if o.name in ("display_flex", "panel_ribbon"): o.scale.z *= 2.0; o.location.z += 30
    S.render.filepath = os.path.join(OUT, "meshsat-v2-concept-%s.png" % view); bpy.ops.render.render(write_still=True); print("RENDERED", S.render.filepath, flush=True)
    if view == "cutaway":
        for o, md in keep: o.modifiers.remove(md)
        bpy.data.objects.remove(tool, do_unlink=True)
        for o in walk(PANEL_PREFIX):
            if o.parent is None or o.name == "pcb_c5": o.matrix_world = Matrix.Translation((0, 0, -60)) @ o.matrix_world
        for o in bpy.data.objects:
            if o.name in ("display_flex", "panel_ribbon"): o.scale.z /= 2.0; o.location.z -= 30
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "meshsat-v2-concept.blend"))
for v in (["overview", "hero", "top", "detail", "cutaway", "closed"] if VIEWS == ["all"] else VIEWS): render(v)
print("SCENE-DONE")
