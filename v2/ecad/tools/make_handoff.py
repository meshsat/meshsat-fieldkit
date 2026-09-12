#!/usr/bin/env python3
"""Build v2/release/<rev>/order (JLCPCB order files) and v2/release/<rev>/review (prints for the design review)
from the deliverable folders in v2/release/<rev>/boards. Run on the laptop from anywhere: python3 make_handoff.py
(rev = $MESHSAT_FK_REV, default revA; every path is derived from this file's location in the meshsat-fieldkit repo)."""
import re, os, csv, shutil, subprocess, sys, pcbnew
HOME = os.path.expanduser("~")
RT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))                     # v2/ecad (projects, tools, meshsat.pretty)
V2 = os.path.dirname(RT)                                                             # v2/
RELEASE = os.path.join(V2, "release", os.environ.get("MESHSAT_FK_REV", "revA"))
DL = os.path.join(RELEASE, "boards")                                                 # deliverable folders

# bench-fitted or non-part references that must not reach the JLC BOM / CPL (the deliverable BOM keeps them)
EXCLUDE = {"pcb-a-power": {"J_DOCK", "J_PRE1", "F1"} | {"J_CP%d" % k for k in range(1, 5)} | {"J_CN%d" % k for k in range(1, 5)} | {"J_BM%d" % k for k in range(1, 12)},   # A22: the spring pins, the blade holder and the eleven blind-mate receptacles are bench parts
           "pcb-d-aprs": {"U2"},   # D8: the SA868 exciter is bench-fitted
           "pcb-c-display": {"SW_MAIN", "SW_PI", "SW_TEST", "SW_LIGHT", "SW_SOS", "SW_EMCON", "SW_ZERO", "BZ1", "J_HSJ1", "J_HSJ2", "CAM_H1", "CAM_H2", "J_MAINSW", "J_PIJ2"},   # C7: the switches, the sounder, the headset jacks and the camera are plate parts; the lead lands have no BOM line
           "pcb-e1-dock": {"F1", "F2", "F3", "J_BLK", "P_CP", "P_CN", "PAD_W1", "PAD_W2", "J_BATT", "U5"},   # E7: the blade holders, the block lands, the pack cable connector, the 12 AWG lands, and OWNER RULING 12 of 13 September 2026: the LT8705A, whose QFN JLCPCB stocks 3 of against a need of 5, is hand-fitted on all five boards
           "pcb-p-pack": {"W_BP", "W_BN", "W_P", "W_N"},   # P1: the wire lands are bench joints; the blade holder, the headers and the gauge are assembled   # E6: the blade holders, the block lands, the pack cable connector and the 12 AWG lands are bench parts
           "pcb-e5-block": set()}
NONPART_PREFIX = ("TP", "H", "JP", "#")
def norm_refs(field, stem):
    """KiCad writes 'R1-R5' ranges and 'J_PANEL?' for references without a number; JLC wants plain comma-separated designators."""
    out = []
    for tok in field.split(","):
        tok = tok.strip().rstrip("?")
        if not tok: continue
        m = re.match(r"^([A-Za-z_]+?)(\d+)-([A-Za-z_]*)(\d+)$", tok)
        if m and (m.group(3) == "" or m.group(3) == m.group(1)): out += ["%s%d" % (m.group(1), i) for i in range(int(m.group(2)), int(m.group(4)) + 1)]
        else: out.append(tok)
    return [r for r in out if r not in EXCLUDE.get(stem, set()) and not any(r.startswith(x) and (len(r) == len(x) or r[len(x):len(x) + 1].isdigit()) for x in NONPART_PREFIX)]

# JLC placement rotation offsets (degrees, added to KiCad's CPL rotation), verified by the ordering session against JLC's previews on 3 Sep 2026 (jlc-rotations.csv)
JLC_ROT = [("^IDC-Header_2x", 270), ("^SOIC-8", 270), ("^SSOP-28", 270), ("^TSSOP-24", 270), ("^LQFP-48", 270), ("^Texas_VQFN", 0), ("^WSON-6", 270), ("^SOT-23-[568]", 270), ("^SOT-23", 180), ("^SOT-223", 180), ("^LED_0603", 180), ("^USB_C_Receptacle", 180), ("^SOP-4", 0)]
def jlc_rot(fpname, rot):
    for pat, off in JLC_ROT:
        if re.search(pat, fpname): return (rot + off) % 360.0
    return rot

BOARDS = [  # (deliverable folder, file stem, project dir, title, phase, hand-fitted list)
    ("meshsat-pcb-a-revA-A22", "pcb-a-power", "pcb-a-power", "PCB-A POWER + I/O", "A22", "A22 is the power board of the MESHSAT-830 generation (appendix 32.55, 32.56, 32.61): 240 x 160 on the JLC06161H-3313 six-layer stack (In1 and In4 solid ground). Bench-fitted: the twelve Preci-Dip spring pins, four node and four return Mill-Max pins and the pre-charge pin pressed in from the underside; the eleven Radiall SMP-MAX receptacles on the underside under the eleven SMA jacks on top; the 25 A blade in F1; the D8 mezzanine on four M3 x 22.6 standoffs with the 2x8 harness and the VH 5 V lead; the 2x13 ribbon J_AB1 to B16; the VH leads of the three slot rails, the device rail, the PA rail (to the module on the plate), the HF rail (lid harness), the PoE rail and the monitor; the MAIN button lead; the heater lead; the wall USB-C outlet leads (J_USBC_OUT, J_USBW). Some ground pads carry a via in the pad (fanout fallback), counted in the order notes"),
    ("meshsat-pcb-b-revA-B16", "pcb-b-compute", "pcb-b-compute", "PCB-B COMPUTE", "B16", "B16 is the three-slot Compute Module 5 carrier of the MESHSAT-830 generation (appendix 32.52, 32.58, 32.61): 330 x 200 on the JLC06161H-3313 six-layer stack (In1 solid ground, In4 the 5 V planes). Bench-fitted: three Compute Module 5 (CM5108064, 8 GB, 64 GB eMMC, wireless) pressed onto their receptacle pairs and screwed to four M2.5 x 4.0 standoffs each, three CM5 Coolers with their fan leads in J_FAN1..3; three NVMe 2242 drives in J_M2N1..3; the AsiaRF AW7915-AED WiFi link card in J_M2C1 with two MHF4 pigtails to the P2P A and B jacks; the Quectel RM520N-GL 5G module in J_M2C2 with its two SIMs and two pigtails; the LimeSDR Mini 2.4 in J_LIME; the RockBLOCK 9704 on its bracket into J_RB9704; the CR2032; the GNSS and LoRa pigtails from J_GNSS1 and J_LORA1 to A22's jacks; the rail and PoE leads from A22; the HDMI cable to the monitor; the camera and QMX leads; the panel ribbon and the A22 ribbon. The LG290P, E22-900M30S and two E72 modules are assembled where JLCPCB stocks them, else hand-soldered"),
    ("meshsat-pcb-c-revA-C7", "pcb-c-display", "pcb-c-display", "PCB-C PANEL BACKER", "C7", "C7 is the backer ring under the 3 mm aluminium face plate of the Peli 1450 (appendix 32.56, 32.60, 32.61; the plate set is in release/revA/case/face-plate/): 344 x 228 with a 240 x 176 void, four layers, hanging 10 mm under the plate on eight PEM SO-M3-10 standoffs (M3 x 6 through H1 to H8, the ground bond to the plate). It carries the RP2040 panel controller (a USB device on the panel ribbon), the two PCA9555, the PDi E2370KS0C1 e-paper ZIF and boost stage, the VEML7700, the sounder driver and the sixteen 3 mm LEDs standing on the top face under the plate's Mentor 1282.5004 light guides (bench-soldered, beaded to height). The switches, the sounder, the two U-174/U headset jacks and the camera module mount in the PLATE and only their leads reach the board: SW_MAIN C&K ATP19-SL1-603-B0SA-03G, SW_PI C&K ATP16-SL1-403-M0SA-04G, SW_TEST C&K ATP16-SL1-203-M0SA-04G, SW_LIGHT NKK M2044SD3A01, SW_SOS, SW_EMCON and SW_ZERO APEM 5636ADKB-2V, BZ1 Floyd Bell MC-09-530-Q; the Xenarc 709GNK sits in the plate with its glass level with the face and its body passes the ring's notch"),
    ("meshsat-pcb-d-revA-D10", "pcb-d-aprs", "pcb-d-aprs", "PCB-D APRS MEZZANINE", "D10", "D10 is the APRS mezzanine of the MESHSAT-830 generation (appendix 32.56, 32.60): the NiceRF SA868 VHF exciter is bench-fitted on its castellated land (U2), the RA30H1317M1 PA module bolts to the face plate and reaches this board by two coax leads and the gate-bias lead (J_PAIN, J_PAOUT, J_VGG), the two headset jacks on the face plate wire to J_HS1 and J_HS2, the antenna SMA J_ANT takes the pigtail to A22's VHF jack; six ground vias sit in their 0603 pads (via-in-pad, accepted on the prototype); the LPF values are to be verified in MESHSAT-818. D10 is the phase that ships (appendix 32.133): 0 hard, 0 unrouted, four of four differential pairs within 1 mm and on their impedance target, and its last connection /HUB_DM1 closed by hand with a locked via and a 0.25 mm track at R13 pad 1 after the stub router, more room at the station and three more router passes had each been measured and refused"),
    ("meshsat-pcb-e-revA-E7", "pcb-e1-dock", "pcb-e1-dock", "PCB-E1 DOCK STRIP", "E7", "E7 is the dock strip of the MESHSAT-830 generation (appendix 32.56, 32.57, 32.60): the pack's XT60 lead lands on J_BATT (pin 2 is +) behind the 25 A blade F3 (the built 4S pack of appendix 32.62), the 9 to 36 V shore entry and its filter, the LT8705A solar tracker, the raised block's standoffs, the eleven float clamps for the blind-mate plugs, and the sensor controller (RP2040 U10 on USB through the dock) with the inside climate, IMU, water, gas, lightning and Geiger headers and the two mixer fan headers; the pack node CELL_F, VIN_RAW, PV_P and TRK_OUT are In2 pours; five ground vias sit in their pads. E7 is the phase that ships (appendix 32.125): 0 hard, 0 unrouted, 415 vias, both rails MET, and the last connection /USB_E6_P closed by the stub router in 63 tracks over 2,036 cells"),
    ("meshsat-pcb-p-revA-P3", "pcb-p-pack", "pcb-p-pack", "PCB-P PACK BMS", "P3", "P3 is the BMS board of the built 4S smart pack (appendix 32.62): the TI BQ4050 SMBus gauge with primary protection and internal balancing, two CSD17570Q5B N-FETs in series on the high side (common drain), a 2 mohm 2512 shunt in the return, the 25 A mini blade holder, the cell tap header J_CELL (JST-XH 1x5, sense only), the thermistor header J_TS, the SMBus lead header J_SMB (JST-XH 1x4 to E6 J_SMB), and four 2.5 mm2 solder lands for the block's B+ and B- straps and the pack's two leads (12 AWG to the XT60 on E6 J_BATT). Two layers on JLC's 2 oz stack, the power path in locked 3 mm bands on both layers. Bench-fitted: the blade, the four lead wires, the tap and thermistor wires from the block; the board lies parts-up in the enclosure bay of v2/cad/pack_4s.py on four M3 bosses. P3 is the phase that ships (appendix 32.116): the three pack connectors carry the codes read back from JLCPCB with their pin count, pitch and stock (C157991, C594232, C5251182), and verify_deliverable accepts the folder on all 35 of its properties"),
    ("meshsat-pcb-e5-revA-E5", "pcb-e5-block", "pcb-e5-block", "PCB-E5 DOCK BLOCK", "E5", "bare 2 oz board, no assembly: it sits on four M3 standoffs 6 mm above the dock strip so its face is at 7.4 mm, PCB-A's spring pins land on the twelve signal targets and the nine power targets, and the wires from the strip are soldered into the plated lands underneath (the underside legend names each one)"),
]
# board-specific fabrication options that the generic README cannot know (C6: the backer under the aluminium face; B15: six layers)
PCB_OPTIONS = {"pcb-a-power": ["FABRICATION NOTES (A22, the power board on the six-layer stack, appendix 32.55, 32.61)",
    "- Six layers on the JLC06161H-3313 stack (1.6 mm): F.Cu, In1 = solid ground plane, In2 (the node plane and ground islands) and In3 signal, In4 = solid ground plane, B.Cu. The gerber zip carries all six copper layers; check the layer count on the order form (6) and quote the six-layer price in the order log.",
    "- The fine-pitch parts (LM5176 controllers, INA226 monitors, PCA9555, the USB-C controller) are escaped with 0.45/0.25 mm vias, 0.127 mm tracks and clearance; some ground pads carry a 0.45/0.25 via in the pad (the fanout fallback; plain through vias, no filling). All within the standard capability; do not let a DFM tool widen them.",
    "- Differential pairs: USB 2.0 pairs 0.20/0.15 mm (90 ohm) on the outer layers over the In1 ground.",
    "- The spring-pin connector, the nine Mill-Max pins, the eleven SMP-MAX receptacles and the blade fuse holder are fitted at the bench (not in the BOM/CPL); the SMA jacks are assembled.", ""],
    "pcb-b-compute": ["FABRICATION NOTES (B16, the three-slot Compute Module 5 carrier on the six-layer stack, appendix 32.52, 32.58, 32.61)",
    "- Six layers on the JLC06161H-3313 stack (1.6 mm): F.Cu, In1 = solid ground plane (windows around the six receptacles), In2 and In3 signal, In4 = the four 5 V planes, B.Cu. The gerber zip carries all six copper layers; check the layer count on the order form (6) and quote the six-layer price in the order log.",
    "- The six Compute Module receptacles (Amphenol 10164227-1004A1RLF, 0.40 mm pitch) are escaped as on Raspberry Pi's own CM5 IO board: 0.40 mm vias with 0.20 mm drills at the pad tips, 0.127 mm tracks, 0.127 mm clearance, 0.19 mm hole-to-copper clearance; the PCIe switches, hubs and M.2 sockets take the same rules. All within the standard capability; do not let a DFM tool widen them.",
    "- Differential pairs: USB 2.0 pairs 0.20/0.15 mm (90 ohm); PCIe, USB 3 and HDMI pairs 0.127/0.127 over the In1 ground (100 ohm); ask for impedance tuning on the JLC06161H-3313 stack if offered.",
    "- The three Compute Modules, their coolers, the drives, the two cards, the SIMs, the LimeSDR, the RockBLOCK and the CR2032 are fitted at the bench (not in the BOM/CPL).", ""],
    "pcb-p-pack": ["FABRICATION NOTES (P3, the pack BMS board, appendix 32.62 and 32.116)",
    "- Two layers, 1.6 mm, 2 oz outer copper (the power path carries the pack current in 3 mm bands on both faces); ENIG; vias 0.5/0.3 mm at the finest, 0.127 mm tracks and clearance at the QFN gauge; the gerber zip carries both copper layers, check the layer count on the order form (2) and the copper weight (2 oz).",
    "- The four 2.5 mm2 solder lands (W_BP, W_BN, W_P, W_N) and the 25 A blade are fitted at the bench; the gauge needs its golden image from bqStudio before the pack is closed (a bench step of the software list).", ""],
    "pcb-d-aprs": ["FABRICATION NOTES (D10, the APRS mezzanine, appendix 32.56, 32.60, 32.133)",
    "- A four-layer 1.6 mm board on JLC's standard four-layer stack (JLC04161H-7628): F.Cu, In1 = solid ground plane, In2 signal, B.Cu; the gerber zip carries all four copper layers, check the layer count on the order form (4). ENIG; the VHF section wants the ground plane continuous under the exciter and the filter, which is what the fourth layer buys here.",
    "- Six ground vias sit inside their own 0603 pads (via-in-pad) and are accepted on this prototype: no filling or capping is ordered, so the assembler should expect a via in those pads.",
    "- Outline 100 x 80 mm with the mezzanine standoff holes; nothing is routed inside the outline.", ""],
    "pcb-e1-dock": ["FABRICATION NOTES (E7, the dock strip, appendix 32.56, 32.57, 32.60, 32.125)",
    "- A four-layer 1.6 mm board on JLC's standard four-layer stack (JLC04161H-7628): F.Cu, In1 = solid ground plane, In2 carries the four power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT), B.Cu; the gerber zip carries all four copper layers, check the layer count on the order form (4). ENIG.",
    "- A 267 x 68 mm strip: long, thin, and several of its signals cross nearly its whole length, so keep the panel rails on the long edges if the fab adds any.",
    "- Five ground vias sit inside their own pads (via-in-pad), accepted on this prototype as on D.", ""],
    "pcb-c-display": ["FABRICATION NOTES (C7, the backer ring under the aluminium face plate, appendix 32.60)",
    "- A four-layer 1.6 mm board on JLC's standard four-layer stack (JLC04161H-7628): F.Cu, In1 = solid ground plane (bands), In2 signal, B.Cu; the gerber zip carries all four copper layers, check the layer count on the order form (4). Any colour, ENIG; nothing on it is a weather face (the aluminium plate is), so no via plugging and no special mask rules. The RP2040 (0.4 mm QFN) is escaped with 0.40/0.20 mm vias, 0.127 mm tracks and clearance and 0.19 mm hole-to-copper clearance, within the standard capability.",
    "- Outline: a ring (344 x 228 outside, 240 x 176 void) with R3 corners and the notch for the monitor's connector block; the toggle body slots, the 19.2, 16.2, 16.2, 28.6 and two 17 mm holes are on Edge.Cuts (routed). The eight 3.2 mm holes H1 to H8 carry 6.0 mm rings on both faces: they are the ground bond to the plate through the PEM standoffs.",
    "- The face plate is a separate CNC part (release/revA/case/face-plate/: STEP, STL, DXF, marking SVG, drawing); it is not a JLC PCB order.", ""]}
# ------------------------------------------------------------------ the table against the tree (11 September 2026, MESHSAT-862)
# BOARDS names a phase per board and that phase goes into ORDER-NOTES.txt, the document a person reads while placing
# the order. The table drifts: it said D8 and P1 while the tree held D9 and P3, so a rebuilt order set would have
# carried D10 gerbers under a note describing D8. The phase is resolved from the tree now, and the prose has to have
# been written for the phase it describes, or this refuses. A wrong order note is not a cosmetic defect: it is the
# one artefact that travels to the fab with the board.
def _phases_in_tree(letter):
    """Every deliverable phase of one board in the release folder, newest last. `-quote` folders count as their phase."""
    out = []
    for fn in sorted(os.listdir(DL)) if os.path.isdir(DL) else []:
        m = re.fullmatch(r"meshsat-pcb-%s-revA-([A-Z]+\d+)(-quote)?" % re.escape(letter), fn)
        if m: out.append(m.group(1))
    return sorted(set(out), key=lambda ph: int(re.sub(r"^[A-Z]+", "", ph)))

def _resolve(folder, prj, phase, hand):
    letter = re.match(r"meshsat-pcb-([a-z0-9]+)-revA-", folder).group(1)
    seen = _phases_in_tree(letter)
    if not seen or seen[-1] == phase: return folder, phase
    newest = seen[-1]; nf = "meshsat-pcb-%s-revA-%s" % (letter, newest)
    # the prose has to be about the board being shipped. Both texts open with the phase token by construction.
    for what, text in (("the hand-fitted list", hand[:80]), ("PCB_OPTIONS", (PCB_OPTIONS.get(prj) or [""])[0])):
        if newest not in text:
            sys.exit("make_handoff: the tree's newest %s deliverable is %s, the table says %s, and %s still describes %s.\n"
                     "  An order set built now would attach %s notes to %s gerbers. Update BOARDS and PCB_OPTIONS for %s, then rerun."
                     % (letter.upper(), newest, phase, what, phase, phase, newest, newest))
    print("make_handoff: %s advanced %s -> %s (the tree's newest, and the notes are written for it)" % (letter.upper(), phase, newest))
    return nf, newest

def _rows(rows):
    out = []
    for f, stem, prj, title, ph, hand in rows:
        nf, nph = _resolve(f, prj, ph, hand)   # once per board: it lists the release folder and may print
        out.append((nf, stem, prj, title, nph, hand))
    return out

BOARDS = _rows(BOARDS)

JLC = os.path.join(RELEASE, "order"); REV = os.path.join(RELEASE, "review")
# The deliverable folders are written by finish_board.sh on the laptop. Building order/ and review/ from a clone that has
# not received them yet silently falls back to the project board file (older, and with no gerbers), so stop here instead.
# 8 Sep 2026 (MESHSAT-776): a board that is held (B16) may carry a QUOTE-ONLY folder `<folder>-quote` exported from its placed pre-route board, so the
# JLCPCB cart can be priced for the whole set; its order line is marked QUOTE ONLY in every file and is rebuilt from the real deliverable before any payment
QUOTE = {f: f + "-quote" for f, stem, *_ in BOARDS if not os.path.exists(os.path.join(DL, f, stem + "-gerbers.zip")) and os.path.exists(os.path.join(DL, f + "-quote", stem + "-gerbers.zip"))}
missing = [f for f, stem, *_ in BOARDS if f not in QUOTE and not os.path.exists(os.path.join(DL, f, stem + "-gerbers.zip"))]
if missing and os.environ.get("HANDOFF_ALLOW_MISSING") != "1":
    sys.exit("make_handoff: no finished deliverable for %s in %s.\n"
             "Finish those boards and commit their folders from the laptop first, then pull here and rerun.\n"
             "Set HANDOFF_ALLOW_MISSING=1 only if you mean to build the set without them." % (", ".join(missing), DL))
# 11 September 2026 (MESHSAT-862), two defects in the line this replaces. It looked the status file up
# under the plain folder name while every other line in this file uses QUOTE.get(folder, folder), so the
# ONE board that most needed the gate, B16's quote folder with 79 uncoded lines, was never looked at. And
# a MISSING status file passed silently, which is the state of nineteen of the twenty three deliverable
# folders: a finish that died before writing one looked exactly like a finish that passed.
def _status(f, stem):
    return os.path.join(DL, QUOTE.get(f, f), stem + "-bom.status")
blank = [f for f, stem, *_ in BOARDS if os.path.exists(_status(f, stem)) and open(_status(f, stem)).read().strip() != "OK"]
nostatus = [f for f, stem, *_ in BOARDS if not os.path.exists(_status(f, stem))]
if blank and os.environ.get("HANDOFF_ALLOW_BLANK") != "1":   # 8 Sep 2026 (MESHSAT-862): lcsc_fill's blank count used to be printed and read by nobody
    sys.exit("make_handoff: the BOM of %s carries LCSC blanks that no lcsc-allow.txt line explains (see <deliverable>/<stem>-bom.status).\n"
             "Fill the codes in tools/lcsc_fill.py or allow-list the bench-fitted lines with a reason, refinish, then rerun; HANDOFF_ALLOW_BLANK=1 only to build the set regardless." % ", ".join(blank))
if nostatus and os.environ.get("HANDOFF_ALLOW_BLANK") != "1":
    sys.exit("make_handoff: no BOM status file for %s (expected <deliverable>/<stem>-bom.status).\n"
             "That file is written by finish_board.sh after lcsc_fill.py passes, so its absence means the BOM was never checked.\n"
             "Refinish those boards, then rerun; HANDOFF_ALLOW_BLANK=1 only to build the set regardless." % ", ".join(nostatus))
shutil.rmtree(REV, ignore_errors=True); os.makedirs(REV, exist_ok=True); os.makedirs(JLC, exist_ok=True)   # JLCPCB/ is never wiped: ORDER-LOG.md and upload/ copies live there
def run(cmd): r = subprocess.run(cmd, capture_output=True, text=True); return r.returncode == 0, (r.stdout + r.stderr)[-300:]
order_index = ["# MeshSat field-kit carrier boards, JLCPCB order set (generated %s)" % subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip(), "",
               "One sub-folder per board. Upload the Gerber zip first, then (for the assembled boards) the BOM and CPL files in the assembly step.", "",
               "| Folder | Board | Size | Layers | Assembly | Files |", "|---|---|---|---|---|---|"]
review_index = ["# MeshSat field-kit carrier boards, review prints (generated)", "",
                "Print everything at 100 % scale (no fit-to-page). The 1:1 sheets are for laying the real devices on paper; the copper sheets and the assembly drawings are for the design review (appendix section 21.3 / 22.4: the six order-gate items are the agenda).", ""]
for folder, stem, prj, title, phase, hand in BOARDS:
    quote = folder in QUOTE; src = os.path.join(DL, QUOTE.get(folder, folder)); board_file = os.path.join(src, stem + ".kicad_pcb")
    if not os.path.exists(board_file): board_file = os.path.join(RT, prj, stem + ".kicad_pcb")
    b = pcbnew.LoadBoard(board_file); bb = b.GetBoardEdgesBoundingBox(); fps = list(b.GetFootprints())
    W, H, NL, T = bb.GetWidth() / 1e6, bb.GetHeight() / 1e6, b.GetCopperLayerCount(), b.GetDesignSettings().GetBoardThickness() / 1e6
    top = [f for f in fps if not f.IsFlipped() and len(list(f.Pads())) > 0]; bot = [f for f in fps if f.IsFlipped() and len(list(f.Pads())) > 0]
    top = [f for f in top if norm_refs(f.GetReference(), stem)]; bot = [f for f in bot if norm_refs(f.GetReference(), stem)]   # assembled parts only
    dnp = sorted(f.GetReference() for f in fps if f.GetValue().upper().startswith("DNP"))
    diff = sorted({str(n) for n in b.GetNetInfo().NetsByName().keys() if (str(n).endswith("_P") or str(n).endswith("_N")) and "USB" in str(n)})
    tag = "%s-%s" % (stem.replace("pcb-", "PCB-").upper().split("-")[0] + "-" + stem.split("-")[1] if False else stem.upper().replace("PCB-", "PCB-"), phase)
    tag = "%s-%s" % (stem.upper(), phase)
    # ---------------- JLCPCB
    jd = os.path.join(JLC, tag); os.makedirs(jd, exist_ok=True)
    ger = os.path.join(src, stem + "-gerbers.zip"); shutil.copy(ger, jd)
    bom_src, cpl_src = os.path.join(src, stem + "-bom.csv"), os.path.join(src, stem + "-cpl.csv"); assembled = os.path.exists(bom_src)
    files = [os.path.basename(ger)]; removed = []
    if assembled:
        rows = list(csv.reader(open(bom_src))); keep = [rows[0]]; dnp_refs = set()
        for r in rows[1:]:
            if r[0].strip().upper().startswith("DNP"):
                removed.append("%s (%s)" % (r[1], r[0][:50])); dnp_refs |= {x.strip().rstrip("?") for x in r[1].split(",")}
            else:
                refs = norm_refs(r[1], stem)
                if refs: r[1] = ",".join(refs); keep.append(r)
        with open(os.path.join(jd, stem + "-bom.csv"), "w", newline="") as f: csv.writer(f).writerows(keep)
        drop = dnp_refs | EXCLUDE.get(stem, set()); rows = list(csv.reader(open(cpl_src))); keep = [rows[0]]
        fpname = {f.GetReference(): f.GetFPIDAsString().split(":")[-1] for f in fps}
        for r in rows[1:]:
            if r[0].strip().rstrip("?") in drop or not norm_refs(r[0], stem): continue
            try: r[4] = "%.6f" % jlc_rot(fpname.get(r[0].strip(), ""), float(r[4]))
            except (ValueError, IndexError): pass
            keep.append(r)
        with open(os.path.join(jd, stem + "-cpl.csv"), "w", newline="") as f: csv.writer(f).writerows(keep)
        files += [stem + "-bom.csv", stem + "-cpl.csv"]
        nb = len(open(os.path.join(jd, stem + "-bom.csv")).read().splitlines()) - 1; nl = sum(1 for r in csv.reader(open(os.path.join(jd, stem + "-bom.csv")))) - 1
        lcsc = sum(1 for r in list(csv.reader(open(os.path.join(jd, stem + "-bom.csv"))))[1:] if r[3].strip())
    notes = ["MeshSat field-kit carrier %s Rev A, phase %s: JLCPCB order notes" % (title, phase), ""] + (["QUOTE ONLY: this line is priced from the PLACED, UNROUTED pre-route board of %s (8 Sep 2026, MESHSAT-776). Size, layers, stack, finish and parts are the design's, the copper is not. Never pay this line; rebuild it from the routed deliverable first." % phase, ""] if quote else []) + [
             "PCB", "- Gerbers + Excellon drill: %s (KiCad 9, Protel extensions .gtl .g1 .g2 .gbl .gts .gbs .gto .gbo .gtp .gbp .gm1, every copper layer of the board, Excellon .drl, drill map .gbr)" % os.path.basename(ger),
             "- Size %.1f x %.1f mm, %d copper layers, %.1f mm FR-4%s" % (W, H, NL, T, ", JLC04161H-7628 stackup" if NL == 4 else ""),
             ("- 1 oz outer copper, surface finish ENIG, matte black solder mask, white silkscreen, no castellations, remove order number: yes (or specify location)" if (top or bot) else "- no copper on this board: any surface finish (pick the cheapest, HASL lead-free), matte black solder mask, white silkscreen, no castellations, remove order number: yes"),
             "- Impedance control: %s" % ("USB 2.0 pairs %s designed 0.2 mm track / 0.15 mm gap on the outer layers; ask JLC to tune for 90 ohm differential on the 7628 stackup" % ", ".join(diff) if diff else "none (no controlled-impedance nets)"),
             "- Quantity: 5 (JLC minimum); confirm the board fits the rod holes of the case before ordering more", ""]
    if assembled:
        notes += ["ASSEMBLY (standard PCBA; the economic tier is not offered for these boards; the sides are the counts below)",
                  "- BOM: %s-bom.csv (%d lines, %d with an LCSC number, the rest must be matched in the JLC parts library at order time)" % (stem, nl, lcsc),
                  "- CPL: %s-cpl.csv (JLC format: Designator, Mid X, Mid Y, Layer, Rotation; rotations already carry the JLC offsets verified against their preview on 3 Sep for box headers, SOIC, SSOP, TSSOP, LQFP, WSON, SOT-23, SOT-223, LED 0603, USB-C; do not add them again); still check pin 1 in the JLC preview" % stem,
                  "- Parts on the TOP side: %d, on the BOTTOM side: %d%s" % (len(top), len(bot), (" (" + ", ".join(sorted(f.GetReference() for f in bot))[:200] + ")") if bot and len(bot) <= 40 else ""),
                  "- Those are footprint counts; the CPL lists only the parts JLCPCB places (BOM-listed, not bench-fitted, not DNP), so it has fewer rows (ORDER-LOG.md, 3 Sep, checked per board).",
                  "- Removed from the JLC BOM/CPL as DNP (they stay in the full BOM in the deliverable folder): %s" % ("; ".join(removed) if removed else "none"),
                  "- Left out of the JLC BOM/CPL as bench-fitted parts (they stay in the full BOM in the deliverable folder, LCSC field empty where JLC has no equivalent): %s" % (", ".join(sorted(EXCLUDE.get(stem, set()))) or "none"),
                  "- Not assembled by JLC, fitted at the bench: %s" % hand, ""]
    else:
        notes += ["ASSEMBLY", "- None: mechanical board (holes, window, tabs). PCB only.", "- Fitted at the bench: %s" % hand, ""]
    notes += PCB_OPTIONS.get(stem, [])
    notes += ["SOURCE", "- Deliverable folder: v2/release/%s/boards/%s in the meshsat-fieldkit repo (KiCad 9 project, schematic PDF, DRC report, renders, 1:1 prints)" % (os.path.basename(RELEASE), folder),
              "- Design record: v2/docs/MESHSAT-709-geometry-appendix.md (sections 18 to 25; 25 = case, panel, dock, single-pack ruling), YouTrack MESHSAT-709"]
    open(os.path.join(jd, "ORDER-NOTES.txt"), "w").write("\n".join(notes) + "\n")
    order_index.append("| `%s/` | %s Rev A (%s)%s | %.0f x %.0f mm | %d | %s | %s |" % (tag, title, phase, " QUOTE ONLY, unrouted pre-route board" if quote else "", W, H, NL, ("top %d + bottom %d parts, %d DNP removed" % (len(top), len(bot), len(removed))) if assembled else "none (PCB only)", ", ".join(files)))
    # ---------------- Review
    rd = os.path.join(REV, tag); os.makedirs(rd)
    for f in os.listdir(src):
        if f.endswith((".pdf", ".png", ".rpt")): shutil.copy(os.path.join(src, f), rd)
    made = []
    for side, layers, mirror, name in (("top", "F.Fab,F.SilkS,F.Paste", False, "assembly-top"), ("bottom", "B.Fab,B.SilkS,B.Paste", True, "assembly-bottom-mirrored")):
        out = os.path.join(rd, "%s-%s.pdf" % (stem, name))
        cmd = ["kicad-cli", "pcb", "export", "pdf", "--mode-single", "-l", layers, "--cl", "Edge.Cuts", "--sp", "--cdnp", "--ibt", "--black-and-white", "-o", out, board_file] + (["-m"] if mirror else [])
        ok, msg = run(cmd); made.append((name, ok, msg))
    cu = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"] if NL == 4 else ["F.Cu", "B.Cu"]
    out = os.path.join(rd, "%s-copper-layers.pdf" % stem); tmpd = os.path.join(rd, "_cu"); os.makedirs(tmpd, exist_ok=True)
    ok, msg = run(["kicad-cli", "pcb", "export", "pdf", "--mode-multipage", "-l", ",".join(cu), "--cl", "Edge.Cuts", "--ibt", "--erd", "--ev", "-o", tmpd, board_file])
    produced = [f for f in os.listdir(tmpd) if f.endswith(".pdf")]        # multipage mode writes <stem>.pdf into the output directory
    if ok and produced: shutil.move(os.path.join(tmpd, produced[0]), out)
    else: ok = False
    shutil.rmtree(tmpd, ignore_errors=True); made.append(("copper", ok, msg))
    for side in ("top", "bottom"):
        out = os.path.join(rd, "%s-render-%s-A4.png" % (stem, side))
        ok, msg = run(["kicad-cli", "pcb", "render", "-w", "3508", "-h", "2480", "--side", side, "--background", "opaque", "--quality", "high", "--zoom", "1.1", "-o", out, board_file]); made.append(("render-" + side, ok, msg))
    bad = [(n, m) for n, ok, m in made if not ok]
    review_index += ["## %s Rev A (%s), folder `%s/`, %.0f x %.0f mm, %d layers" % (title, phase, tag, W, H, NL), "",
                     "- `%s-1to1-top.pdf`, `%s-1to1-bottom-mirrored.pdf`: 1:1 device-layout sheets (bottom is mirrored so it reads through the paper); lay the real devices on them" % (stem, stem),
                     "- `%s-assembly-top.pdf`, `%s-assembly-bottom-mirrored.pdf`: fab drawings with reference designators, pad outlines and pad numbers; DNP parts crossed out" % (stem, stem),
                     "- `%s-copper-layers.pdf`: one page per copper layer (%s) with the outline; check the planes, the USB pairs, the cell straps and the boost loop here" % (stem, ", ".join(cu)),
                     "- `%s-render-top-A4.png`, `%s-render-bottom-A4.png`: 3D renders at A4 300 dpi; the small `-render-*.png` are the originals" % (stem, stem),
                     "- `%s-schematic.pdf`: full schematic; `%s-drc.rpt`: the DRC report of the exported board" % (stem, stem) if assembled else "- `%s-drc.rpt`: DRC report (mechanical board, no schematic)" % stem, ""]
    if bad: review_index.append("- generation problems: " + "; ".join("%s: %s" % (n, m.strip().replace("\n", " ")[-120:]) for n, m in bad) + "\n")
    if stem == "pcb-c-display" and False:                                  # (C6 and earlier carried the Touch Display 2 documents here; C7 has the Xenarc and PDi sheets in vendor/xenarc and vendor/pdi)
        docs = os.path.join(V2, "vendor", "td2")
        if os.path.isdir(docs):
            review_index += ["### Official Raspberry Pi documents for the Touch Display 2 (7-inch), kept in `v2/vendor/td2/` (not copied into this folder)", "",
                "Raspberry Pi publishes no schematic for the Touch Display 2 (the driver board is closed) and no separate mechanical-drawing PDF; the drawing is a page inside the 2024 and 2025 product-brief editions, and the 3D geometry is the STEP model. The 2026 editions (\"7-inch Portrait\") carry photos, specification and safety text only.", "",
                "- `raspberry-pi-touch-display-2-7inch-RP-009154-DD-1.step`: the official 7-inch STEP model. PCB-C is derived from it (appendix 14.1, 14.5, 14.6).",
                "- `RPi-Touch-Display-2-product-brief-2025-08-(design-source).pdf`: the edition whose page 4 drawing was read with the STEP.",
                "- `RP-008387-DS-1-touch-display-2-product-brief.pdf` (November 2024): the original edition, same drawing numbers.",
                "- `RP-009106-MM-8-touch-display-2-product-brief.pdf` (June 2026), `RP-010429-MM-1-touch-display-2-7-inch-product-brief.pdf` (August 2026) and `RPi-Touch-Display-2-product-brief-2026-08-datasheets.raspberrypi.com.pdf`: current editions, no drawing.",
                "", "Sources: https://pip.raspberrypi.com/categories/1083-raspberry-pi-touch-display-2 and https://datasheets.raspberrypi.com/display/touch-display-2-product-brief.pdf (checked 2 Sep 2026).", ""]
    print("%s: %s -> JLCPCB/%s (%s) and Review/%s (%s)" % (stem, os.path.basename(board_file), tag, ", ".join(files), tag, ", ".join("%s %s" % (n, "ok" if ok else "FAILED") for n, ok, m in made)))
order_index += ["", "Common options for all boards: 1 oz outer copper, ENIG, matte black mask, white silk; 4-layer boards on the JLC04161H-7628 stackup (impedance-tuned USB pairs where the notes say so).",
                "The BOM/CPL copies here have the DNP and bench-fitted lines removed; each board's ORDER-NOTES.txt lists its own designators by name, and the full BOMs stay in the deliverable folders.",   # 8 Sep 2026: the old sentence still named the DMR858M, which left PCB-D with the device set of 6 Sep, and an R46 that is now a slot-rail resistor
                "Order after the 12 Sep design review (appendix section 21 / 22)."]
open(os.path.join(JLC, "README.md"), "w").write("\n".join(order_index) + "\n")
review_index += ["## Review agenda (MESHSAT-830 generation, appendix 32.52 to 32.61)", "", "1. PCB-A (A22): the 14.4 V node and the BQ25731 charger, the LM5176 front-end and PA/HF/PoE stages, the four AP64500 rails and their INA226 monitors, the TPS25740 and TPS55288 outlet stage, the EMCON gates, the eleven blind-mate sites, the dock contacts.",
                 "2. PCB-B (B16): the three receptacle pairs and their escapes, the per-slot PCIe switch, hub and NVMe, the KSZ9897 and TMDS341A, the radio sites, the PCIe, USB 3 and HDMI pairs, the panel and A22 ribbons.",
                 "3. PCB-D (D8): the SA868 site, the G6K relay and the LPF against the PA module's sheet, the PCM2912A and TPA6132A2 audio path, the PTT and EMCON gate logic, the TPS22810 bias switch.",
                 "4. PCB-C (C7): every site against panel1450.py and the plate drawing, the RP2040 and its escapes, the PDi boost stage against the driving note, the eight ground-bond holes, the notch and the jack holes, the stack height map.",
                 "5. PCB-E1 (E6) and E5: the front end and the tracker, the pack entry and its fuse, the sensor controller's headers, the eleven clamps, the block targets against A22's pins.", ""]
open(os.path.join(REV, "README.md"), "w").write("\n".join(review_index) + "\n")
print("done:", JLC, REV)
