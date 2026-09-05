# MeshSat field kit V2, concept renders: the Peli 1520EU case, the 1520PF frame with the sealed panel C5, the board stack (E4, E5, A20, D6, B13),
# the battery module, the end-wall antennas and the back-wall connectors. Case frame in mm: X along the long axis, +Y = back wall (hinge), Z up from the floor.
# Run headless: blender -b -P scene.py -- <out dir> [views...]   (views: overview, hero, top, detail, stack, closed, all)
import bpy, bmesh, math, os, sys, collections
from mathutils import Vector, Matrix, Euler
R = os.path.expanduser("~/render3d"); STL = R + "/stl"
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUT = args[0] if args else R + "/out"; VIEWS = args[1:] or ["all"]; os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
S = bpy.context.scene; S.unit_settings.system = "METRIC"; S.unit_settings.scale_length = 0.001; S.unit_settings.length_unit = "MILLIMETERS"
RIM = 124.87; FACE = RIM - 8.8            # cavity rim above the floor; the panel face (C5, 2.0 mm) sits 8.8 below the rim
# ------------------------------------------------------------------ materials
def mat(name, rgb, rough=0.5, metal=0.0, alpha=1.0, emit=0.0):
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; n = m.node_tree.nodes["Principled BSDF"]
    n.inputs["Base Color"].default_value = (*rgb, 1.0); n.inputs["Roughness"].default_value = rough; n.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        n.inputs["Alpha"].default_value = alpha; m.blend_method = "BLEND"
        try: m.shadow_method = "HASHED"
        except Exception: pass
    if emit: n.inputs["Emission Strength"].default_value = emit; n.inputs["Emission Color"].default_value = (*rgb, 1.0)
    return m
M = dict(orange=mat("peli_orange", (0.85, 0.30, 0.03), 0.55), black=mat("matte_black", (0.02, 0.02, 0.02), 0.65), mask=mat("mask_black", (0.03, 0.03, 0.035), 0.5),
         gold=mat("enig", (0.95, 0.75, 0.30), 0.35, 1.0), steel=mat("steel", (0.6, 0.6, 0.62), 0.35, 1.0), alu=mat("aluminium", (0.75, 0.76, 0.78), 0.4, 1.0),
         glass=mat("glass", (0.6, 0.7, 0.8), 0.05, 0.0, 0.18), lens=mat("lens", (0.8, 0.85, 0.9), 0.05, 0.0, 0.25), epaper=mat("epaper", (0.92, 0.92, 0.9), 0.7),
         green=mat("led_green", (0.1, 0.9, 0.2), 0.3, 0.0, 1.0, 2.0), amber=mat("led_amber", (1.0, 0.6, 0.05), 0.3, 0.0, 1.0, 2.0), white=mat("plastic_white", (0.9, 0.9, 0.88), 0.5),
         rubber=mat("rubber", (0.05, 0.05, 0.05), 0.9), dark=mat("dark_plastic", (0.08, 0.08, 0.09), 0.6), red=mat("red", (0.8, 0.05, 0.05), 0.4), blue=mat("blue", (0.1, 0.2, 0.7), 0.4),
         pcb=mat("pcb_green", (0.05, 0.25, 0.1), 0.5), tin=mat("tin", (0.7, 0.72, 0.72), 0.3, 1.0), gray=mat("gray_plastic", (0.35, 0.35, 0.37), 0.6), cell=mat("cell_blue", (0.15, 0.3, 0.75), 0.45))
def assign(o, m):
    o.data.materials.clear(); o.data.materials.append(m)
# ------------------------------------------------------------------ primitives (mm)
def box(name, size, at, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=at); o = bpy.context.object; o.name = name; o.scale = (size[0], size[1], size[2]); o.rotation_euler = rot
    assign(o, m); return o
def cyl(name, d, h, at, m, axis="Z", rot_extra=0.0):
    bpy.ops.mesh.primitive_cylinder_add(radius=d / 2, depth=h, location=at, vertices=48); o = bpy.context.object; o.name = name
    if axis == "X": o.rotation_euler = (0, math.pi / 2, 0)
    elif axis == "Y": o.rotation_euler = (math.pi / 2, 0, 0)
    assign(o, m); return o
def sphere(name, d, at, m):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=d / 2, location=at, segments=32, ring_count=16); o = bpy.context.object; o.name = name; assign(o, m); return o
def label(name, txt, at, size, m, rot=(0, 0, 0), align="CENTER"):
    bpy.ops.object.text_add(location=at); o = bpy.context.object; o.name = name; o.data.body = txt; o.data.size = size; o.data.align_x = align; o.rotation_euler = rot
    o.data.extrude = 0.05; assign(o, m); return o
# ------------------------------------------------------------------ imports
def import_stl(name, fn, m, matrix):
    bpy.ops.wm.stl_import(filepath=os.path.join(STL, fn)) if hasattr(bpy.ops.wm, "stl_import") else bpy.ops.import_mesh.stl(filepath=os.path.join(STL, fn))
    o = bpy.context.selected_objects[0]; o.name = name; o.matrix_world = matrix; assign(o, m)
    for p in o.data.polygons: p.use_smooth = False
    return o
def import_board(name, fn, z, extra=Matrix.Identity(4)):
    """A KiCad GLB exported with the case-frame user origin (case mm after the import, board bottom at z 0). Recoloured: the solder mask matte black, copper ENIG gold; component models get a dark plastic where KiCad exported none."""
    before = set(bpy.data.objects); bpy.ops.import_scene.gltf(filepath=os.path.join(R, fn)); new = [o for o in bpy.data.objects if o not in before]
    root = bpy.data.objects.new(name, None); S.collection.objects.link(root)
    for o in new:
        if o.parent is None: o.parent = root
    root.matrix_world = extra @ Matrix.Translation((0, 0, z))          # the importer already converts the GLB metres to the scene millimetres
    for o in new:
        if o.type != "MESH": continue
        if not o.material_slots or all(s.material is None for s in o.material_slots): o.data.materials.clear(); o.data.materials.append(M["dark"] if not o.name.startswith(("J_", "TP")) else M["white"]); continue
        for slot in o.material_slots:
            mm = slot.material
            if not mm or not mm.use_nodes: continue
            n = mm.node_tree.nodes.get("Principled BSDF")
            if not n: continue
            r, g, b = n.inputs["Base Color"].default_value[:3]
            if g > r * 1.3 and g > b * 1.3: slot.material = M["mask"]                 # KiCad's default green mask: the boards are ordered matte black
            elif r > 0.6 and g > 0.4 and b < 0.35 and r > b * 1.8: slot.material = M["gold"]   # copper: ENIG
            elif r > 0.85 and g > 0.85 and b > 0.85: slot.material = M["white"]      # silkscreen
    return root
# ------------------------------------------------------------------ the case
# Peli STEP frames (bounding boxes from step2stl.log): base x +-254 (long axis), y -150.3..0 (up, rim at 0), z +-188.9; lid x +-250.7, y 0..71.5, z +-186.7;
# frame 1523-PF x +-227.6, y +-161.9, z -8.8..9.3 with the rim plane at z 8.5 (its top ends 0.8 above the rim)
YUP = Matrix(((1, 0, 0, 0), (0, 0, 1, 0), (0, 1, 0, 0), (0, 0, 0, 1)))       # STEP (x, y up, z) -> case (X, Y = z, Z = y)
base = import_stl("case_base", "case_base.stl", M["orange"], Matrix.Translation((0, 0, RIM)) @ YUP)
frame = import_stl("panel_frame", "panel_frame.stl", M["black"], Matrix.Translation((0, 0, RIM - 8.5)))
lid_closed_m = Matrix.Translation((0, 0, RIM)) @ YUP
hinge = Vector((0, 189.0, RIM)); lid_open_m = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(-105), 4, "X") @ Matrix.Translation(-hinge) @ lid_closed_m   # swung back 105 degrees about the hinge line
lid_m = lid_open_m
lid = import_stl("case_lid", "case_lid.stl", M["orange"], lid_m)
# connector plate on the back wall (outside): 82 x 54 x 3 at X -133..-51, Z 28..82; shore DC and USB receptacles
WALL_Y = 188.0
plate = box("conn_plate", (82, 3, 54), (-92, WALL_Y + 1.5, 55), M["alu"])
for x, d, fl, nm in ((-110, 19.05, 28.9, "shore DC"), (-74, 23.01, 31.29, "USB host")):
    box("recept_flange_" + nm, (fl, 4, fl), (x, WALL_Y + 5, 55), M["steel"]); cyl("recept_" + nm, d + 4, 14, (x, WALL_Y + 12, 55), M["steel"], axis="Y")
    cyl("recept_cap_" + nm, d + 6, 4, (x, WALL_Y + 20, 55), M["dark"], axis="Y")
# ------------------------------------------------------------------ the floor: dock strip E4, block E5, rods, battery module
import_board("pcb_e4", "pcb-e1-dock.glb", 0.0)
import_board("pcb_e5", "pcb-e5-block.glb", 6.0)
for (x, y) in ((-155.5, -63.0), (-117.5, -63.0), (-155.5, -82.0), (-117.5, -82.0)): cyl("standoff_e5_%d" % int(x), 5.0, 6.0, (x, y, 3.0), M["steel"])
box("traco_ten40", (50.8, 25.4, 10.2), (-40, -81, 1.6 + 5.1), M["dark"])          # TRACO TEN 40WIN on the strip
for (x, y) in ((-110.5, -73.0), (110.5, -73.0), (-110.5, 73.0), (110.5, 73.0)):
    cyl("rod_%d_%d" % (x, y), 3.0, 118.0, (x, y, 59.0), M["steel"])
    for z in (1.6, 15.0 + 1.6, 51.6 + 1.6): cyl("nut_%d_%d_%d" % (x, y, z), 5.5, 2.4, (x, y, z + 1.2), M["steel"])
    cyl("spacer_%d_%d_a" % (x, y), 6.0, 13.4, (x, y, 1.6 + 6.7), M["alu"]); cyl("spacer_%d_%d_b" % (x, y), 6.0, 35.0, (x, y, 16.6 + 17.5), M["alu"])
# battery module in its cradle, east floor band: cradle X 120..202, Y -137..83, module 81 x 221 x 27.5
MOD = Matrix.Translation((121.0, -137.0, 6.0)); import_stl("module_base", "module_base.stl", M["gray"], MOD); import_stl("module_lid", "module_lid.stl", M["dark"], MOD)
import_stl("module_cradle", "module_cradle.stl", M["black"], Matrix.Translation((121.0, -137.0, 5.0)))
box("module_lead", (12, 40, 6), (161, -152, 12), M["rubber"]); cyl("xt60", 16, 18, (161, -125, 6.0 + 9), M["amber"], axis="Y")
# ------------------------------------------------------------------ PCB-A A20 at Z 15.0 (strip 1.6 + gap 13.4) with the mezzanine D6 6 mm above it
import_board("pcb_a20", "pcb-a-power.glb", 15.0)
import_board("pcb_d6", "pcb-d-aprs.glb", 16.6 + 6.0, Matrix.Translation((45.0, 0.0, 0.0)))
for (x, y) in ((10, -26), (80, -26), (10, 26), (80, 26)): cyl("standoff_d_%d_%d" % (x, y), 5.0, 6.0, (x, y, 16.6 + 3.0), M["steel"])
box("dmr858m", (48, 26, 6), (45 + 10.5, 0 - 2.0, 16.6 + 6 + 1.6 + 11.0 + 3.0), M["tin"]); box("dmr858m_sink", (48, 26, 8), (45 + 10.5, -2.0, 16.6 + 6 + 1.6 + 11 + 6 + 4), M["alu"])
for k, (x, y, nm) in enumerate(((-100, -56, "UHF"), (-84, -56, "WIFI 2.4"), (-26, -56, "WIFI 5.8"), (-12, -56, "SDR"), (70, -74, "LTE"), (92, -74, "IRIDIUM"), (103, -54, "LORA"))):
    cyl("sma_jack_%d" % k, 6.5, 9.0, (x, y, 16.6 + 4.5), M["gold"]); cyl("sma_nut_%d" % k, 8.0, 2.0, (x, y, 16.6 + 1.0), M["steel"])   # the seven SMA jacks on A20 (SMP-MAX receptacles underneath)
# ------------------------------------------------------------------ PCB-B B13 at Z 51.6 and what rides on it
import_board("pcb_b13", "pcb-b-compute.glb", 51.6)
ZB = 51.6 + 1.6
cm5 = box("cm5_module", (40, 55, 1.24), (-88, 0, ZB + 4.0 + 0.62), M["pcb"]); box("cm5_soc", (15, 15, 1.2), (-88, 6, ZB + 4.0 + 1.24 + 0.6), M["dark"]); box("cm5_emmc", (11, 13, 1.0), (-88, -12, ZB + 5.24 + 0.5), M["dark"])
box("cm5_cooler", (41, 56, 12.7), (-88, 0, ZB + 4.0 + 1.24 + 3.0 + 6.35), M["alu"]); box("cm5_fan", (30, 30, 6), (-88, 0, ZB + 4.0 + 1.24 + 3.0 + 12.7 + 3), M["dark"])
for i in range(12): box("cm5_fin_%d" % i, (1.2, 52, 9), (-88 - 18 + 3.3 * i, 0, ZB + 4.0 + 1.24 + 3.0 + 12.7 - 4.5), M["alu"])
for (x, y) in ((-104.5, -24), (-104.5, 24), (-71.5, -24), (-71.5, 24)): cyl("cm5_standoff_%d_%d" % (x, y), 4.0, 4.0, (x, y, ZB + 2.0), M["steel"])
box("lte_card", (50.95, 30, 1.0), (-3, 67, ZB + 4.0 + 0.5), M["pcb"]); box("lte_can", (30, 24, 2.5), (5, 67, ZB + 5.0 + 1.25), M["tin"]); box("lte_socket", (8, 22, 4.0), (-29.5, 67, ZB + 2.0), M["dark"])
box("sdr_stick", (69, 27, 13), (37, 0, ZB + 6.5), M["dark"]); cyl("sdr_sma", 6.5, 10, (76, 0, ZB + 6.5), M["gold"], axis="X"); box("usb_a_recept", (14, 13.5, 7), (-12, 0, ZB + 3.5), M["steel"])
RB = Matrix.Translation((52.0 - 90.3, -48.0 + 91.2, ZB + 6.0 + 10.3)); import_stl("rockblock9704", "rockblock9704.stl", M["dark"], RB)
for (x, y) in ((36, -64), (68, -64), (36, -32), (68, -32)): cyl("rb_standoff_%d_%d" % (x, y), 6.0, 6.0, (x, y, ZB + 3.0), M["steel"])
box("gnss_neo", (12.2, 16, 2.4), (-107, 55, ZB + 1.2), M["tin"]); box("lora_wio", (11.6, 11, 3), (-84, 55, ZB + 1.5), M["tin"]); box("zigbee_e72", (17.5, 28.7, 2.5), (94, 34, ZB + 1.25), M["tin"]); box("zigbee_can", (17.5, 20, 2.0), (94, 30, ZB + 2.5 + 1.0), M["tin"])
cyl("cr2032", 20, 3.2, (-46, 27, ZB + 1.6 + 1.6), M["steel"]); box("cr2032_holder", (24, 21, 5), (-46, 27, ZB + 2.5), M["dark"])
box("display_fpc", (16, 40, 0.3), (-50, 30, ZB + 6), M["amber"])
# ------------------------------------------------------------------ the panel C5 and everything on its face (Z: face at FACE)
PZ = FACE - 2.0
import_board("pcb_c5", "pcb-c-display.glb", PZ)
# Touch Display 2: STEP frame y long, glass on top at z 5.0; the panel puts the long axis along X (case X = STEP y - 2.95, case Y = -STEP x), glass 1.1 proud
TD2 = Matrix.Translation((0.0, -10.0, FACE + 1.1 - 5.0)) @ Matrix.Rotation(math.radians(-90), 4, "Z") @ Matrix.Translation((0, -2.95, 0))
import_stl("td2", "td2.stl", M["black"], TD2); box("td2_glass", (189.32, 120.24, 0.8), (0, -10, FACE + 1.7), M["glass"])
scr = box("td2_screen", (155, 87, 0.15), (0, -10, FACE + 1.2), mat("screen", (0.10, 0.22, 0.42), 0.3, 0.0, 1.0, 1.6))
try:
    img = bpy.data.images.load(os.path.join(R, "ui.png")); sm = scr.data.materials[0]; nt = sm.node_tree; tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = img
    pr = nt.nodes["Principled BSDF"]; nt.links.new(tex.outputs["Color"], pr.inputs["Emission Color"]); nt.links.new(tex.outputs["Color"], pr.inputs["Base Color"]); pr.inputs["Emission Strength"].default_value = 4.0
    bpy.context.view_layer.objects.active = scr; bpy.ops.object.mode_set(mode="EDIT"); bpy.ops.mesh.select_all(action="SELECT"); bpy.ops.uv.cube_project(cube_size=1.0, scale_to_bounds=True); bpy.ops.object.mode_set(mode="OBJECT")
except Exception as e: print("ui texture skipped:", e)
# WeAct 3.7 e-paper: STEP x long (105.8), glass side at z -3.0; centre (30, 100); glass flush with the face, the 2.0 mm PC lens on a 0.4 mm tape frame over it
EPD = Matrix.Translation((30.0, 100.0, FACE - 3.0)) @ Matrix.Rotation(math.pi, 4, "X") @ Matrix.Translation((-269.3, -177.4, 0.0)); import_stl("epaper", "epaper.stl", M["dark"], EPD)
box("epaper_glass", (92.99, 53.0, 0.6), (30, 100, FACE - 0.3), M["epaper"]); box("epaper_lens", (107.19, 66.6, 2.0), (30, 100, FACE + 0.4 + 1.0), M["lens"])
label("epaper_text", "MESHSAT  tesseract\nnode 2 of 3   mesh 7 peers\nsat OK   lte 4G   gps 11 sv", (30 - 40, 100 + 14, FACE + 0.1), 6.0, M["black"], align="LEFT")
# switches: C&K anti-vandal (19 and 16 mm), NKK M2044 toggle, APEM 5636 locking toggles, the Floyd Bell sounder
def pushbutton(name, x, y, d_bezel, cap, ring):
    cyl(name + "_bezel", d_bezel + 3, 4.0, (x, y, FACE + 2.0), M["steel"]); cyl(name + "_ring", d_bezel - 1, 0.6, (x, y, FACE + 4.3), ring); cyl(name + "_cap", d_bezel - 4, 3.5, (x, y, FACE + 5.5), cap)
    cyl(name + "_body", d_bezel + 1, 24, (x, y, FACE - 2 - 12), M["dark"])
pushbutton("sw_main", -150, 100, 19.2, M["dark"], M["green"]); pushbutton("sw_pi", -110, 100, 16.2, M["dark"], M["amber"]); pushbutton("sw_test", -70, 100, 16.2, M["dark"], M["white"])
def toggle(name, x, y, lever_len, tilt, locking=False):
    cyl(name + "_nut", 9.0, 2.5, (x, y, FACE + 1.25), M["steel"]); cyl(name + "_bush", 6.5, 9.0, (x, y, FACE + 2.5), M["steel"])
    if locking: cyl(name + "_lock", 9.5, 3.0, (x, y, FACE + 8.5), M["dark"])
    bpy.ops.mesh.primitive_cylinder_add(radius=1.6, depth=lever_len, location=(x, y, FACE + 9.0 + lever_len / 2), vertices=24); o = bpy.context.object; o.name = name + "_lever"; assign(o, M["steel"])
    o.rotation_euler = (math.radians(tilt), 0, 0); o.location = (x, y + math.sin(math.radians(tilt)) * lever_len / 2 * -1, FACE + 9.0 + math.cos(math.radians(tilt)) * lever_len / 2)
    sphere(name + "_tip", 4.5, (x, y - math.sin(math.radians(tilt)) * lever_len, FACE + 9.0 + math.cos(math.radians(tilt)) * lever_len), M["rubber"] if not locking else M["red"])
    cyl(name + "_body", 13, 22, (x, y, FACE - 2 - 11), M["dark"])
toggle("sw_light", 120, 100, 20, 25); toggle("sw_sos", 170, 42, 24, 22, True); toggle("sw_emcon", 170, 0, 24, -22, True); toggle("sw_zero", 170, -42, 24, 22, True)
cyl("sounder", 34, 3.0, (-180, -100, FACE + 1.5), M["black"]); cyl("sounder_grille", 26, 0.5, (-180, -100, FACE + 3.2), M["dark"]); cyl("sounder_body", 30, 20, (-180, -100, FACE - 2 - 10), M["dark"])
# LEDs (through the face): the eleven indicators at X -120, the five-LED bar at Y 123
LEDC = {"D1": "red", "D2": "amber", "D3": "red", "D4": "red", "D5": "green", "D6": "green", "D7": "green", "D8": "green", "D9": "amber", "D10": "amber", "D11": "green"}
for k, (ref, y, txt) in enumerate((("D1", 45, "MSTR WARN"), ("D2", 36, "MSTR CAUT"), ("D3", 27, "TX"), ("D4", 18, "SOS ACTIVE"), ("D5", 9, "SAT"), ("D6", 0, "MESH"), ("D7", -9, "LTE"), ("D8", -18, "GPS"), ("D9", -27, "SHORE"), ("D10", -36, "CHARGE"), ("D11", -45, "MSG"))):
    on = ref in ("D5", "D6", "D7", "D8", "D9", "D10"); cyl("led_" + ref, 3.0, 2.0, (-120, y, FACE + 1.0), M[{"red": "red", "amber": "amber", "green": "green"}[LEDC[ref]]] if on else M["gray"])
    label("lbl_" + ref, txt, (-126, y - 1.2, FACE + 0.05), 3.0, M["white"], align="RIGHT")
for ref, x in (("D12", -82), ("D13", -76), ("D14", -70), ("D15", -64), ("D16", -58)): cyl("led_" + ref, 3.0, 2.0, (x, 123, FACE + 1.0), M["green"] if x < -60 else M["gray"])
label("lbl_bar", "BATTERY", (-70, 128, FACE + 0.05), 3.5, M["white"])
label("nameplate", "MESHSAT FIELD KIT V2   S/N ______   NUCLEAR LIGHTERS", (0, -114, FACE + 0.05), 4.5, M["white"])
pass
for x, y, txt in ((-150, 86, "MAIN"), (-110, 86, "PI"), (-70, 86, "TEST"), (120, 86, "LIGHT"), (170, 55, "SOS"), (170, 13, "EMCON"), (170, -29, "ZEROIZE")): label("lbl_" + txt, txt, (x, y, FACE + 0.05), 4.0, M["white"])
# ------------------------------------------------------------------ end-wall antennas: SMA bulkheads at Z 55, Y -60, -30, +30, +60 on both end walls
WALL_X = 209.0
ANT = {"UHF": (170, 9, M["rubber"]), "WIFI 2.4": (110, 9, M["rubber"]), "SDR": (150, 9, M["rubber"]), "LTE": (200, 10, M["rubber"]), "IRIDIUM": (0, 0, None), "LORA": (140, 9, M["rubber"]), "GNSS": (0, 0, None), "SPARE": (0, 0, None)}
for sx, sites in ((-1, ((-60, "UHF"), (-30, "WIFI 2.4"), (30, "GNSS"), (60, "SDR"))), (1, ((-60, "LTE"), (-30, "IRIDIUM"), (30, "LORA"), (60, "SPARE")))):
    for y, nm in sites:
        cyl("bulk_" + nm, 9.0, 3.0, (sx * (WALL_X + 1.5), y, 55), M["steel"], axis="X"); cyl("bulk_sma_" + nm, 6.5, 12, (sx * (WALL_X + 7), y, 55), M["gold"], axis="X")
        L, d, m = ANT[nm]
        ax = sx * (WALL_X + 16)
        if L:      # right-angle SMA adapter at the bulkhead, the whip standing up beside the wall
            cyl("ant_elbow_" + nm, 8, 8, (ax, y, 55), M["gold"], axis="X"); cyl("ant_base_" + nm, 12, 24, (ax, y, 55 + 4 + 12), M["dark"]); cyl("ant_" + nm, d, L, (ax, y, 55 + 16 + L / 2), m)
            sphere("ant_tip_" + nm, d * 1.3, (ax, y, 55 + 16 + L), m)
        elif nm == "IRIDIUM": cyl("ant_elbow_iridium", 8, 8, (ax, y, 55), M["gold"], axis="X"); cyl("ant_iridium", 76, 18, (ax, y, 55 + 10 + 9), M["white"])
        elif nm == "GNSS": cyl("ant_elbow_gnss", 8, 8, (ax, y, 55), M["gold"], axis="X"); cyl("ant_gnss", 48, 14, (ax, y, 55 + 8 + 7), M["dark"])
        else: cyl("ant_plug", 9, 6, (sx * (WALL_X + 13), y, 55), M["steel"], axis="X")
# ------------------------------------------------------------------ world, lights, cameras
S.render.engine = "CYCLES"; S.cycles.samples = int(os.environ.get("SAMPLES", "256")); S.cycles.use_denoising = False; S.cycles.device = "CPU"
S.render.resolution_x = 2000; S.render.resolution_y = 1400; S.render.resolution_percentage = int(os.environ.get("RESPCT", "100")); S.render.film_transparent = False; S.view_settings.view_transform = "Filmic" if "Filmic" in [i.identifier for i in bpy.types.ColorManagedViewSettings.bl_rna.properties["view_transform"].enum_items] else "AgX"
world = bpy.data.worlds.new("w"); S.world = world; world.use_nodes = True; bg = world.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.85, 0.86, 0.9, 1); bg.inputs[1].default_value = 1.3
def light(name, at, energy, size):
    bpy.ops.object.light_add(type="AREA", location=at); L = bpy.context.object; L.name = name; L.data.energy = energy; L.data.size = size
    L.rotation_euler = (Vector((0, 0, 0)) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return L
light("key", (-600, -900, 1100), 6.0e6, 600); light("fill", (900, -400, 700), 2.5e6, 800); light("rim", (200, 900, 900), 2.5e6, 500)
bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, -30)); floor = bpy.context.object; floor.name = "ground"; assign(floor, mat("ground", (0.7, 0.7, 0.72), 0.9))
def camera(name, at, look, lens=50):
    bpy.ops.object.camera_add(location=at); c = bpy.context.object; c.name = name; c.data.lens = lens; c.data.clip_end = 20000
    c.rotation_euler = (Vector(look) - Vector(at)).to_track_quat("-Z", "Y").to_euler(); return c
CAMS = {"overview": camera("cam_overview", (-700, -900, 640), (0, 0, 90), 40), "hero": camera("cam_hero", (-400, -560, 470), (-20, 10, 105), 55),
        "top": camera("cam_top", (0, -120, 980), (0, 0, 100), 50), "detail": camera("cam_detail", (-215, 25, 285), (-112, 66, 116), 55),
        "stack": camera("cam_stack", (-380, -520, 400), (-20, 0, 45), 50), "closed": camera("cam_closed", (-720, -860, 560), (0, 0, 70), 42)}
PANEL_PREFIX = ("pcb_c5", "td2", "epaper", "sw_", "sounder", "led_", "lbl_", "nameplate", "logo")
CASE_PREFIX = ("recept_", "bulk_", "ant_", "conn_plate")
def hide(prefixes, flag):
    for o in bpy.data.objects:
        p = o
        while p is not None:
            if p.name.startswith(prefixes): o.hide_render = flag; break
            p = p.parent
def render(view):
    S.camera = CAMS[view]; lid.matrix_world = lid_closed_m if view == "closed" else lid_open_m
    hide(("ant_",), view == "closed")      # the whips come off for transport: the closed case shows the bulkheads only
    if view == "stack":     # the stack lifted out: no case, frame, lid, panel or wall parts; the boards, the module and the dock stay
        for o in (base, frame, lid): o.hide_render = True
        hide(CASE_PREFIX, True); hide(PANEL_PREFIX, True)
    S.render.filepath = os.path.join(OUT, "meshsat-v2-concept-%s.png" % view); bpy.ops.render.render(write_still=True); print("RENDERED", S.render.filepath, flush=True)
    if view == "stack":
        for o in (base, frame, lid): o.hide_render = False
        hide(CASE_PREFIX, False); hide(PANEL_PREFIX, False)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "meshsat-v2-concept.blend"))
for v in (["overview", "hero", "top", "detail", "stack", "closed"] if VIEWS == ["all"] else VIEWS): render(v)
print("SCENE-DONE")
