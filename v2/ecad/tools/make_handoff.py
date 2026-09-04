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
EXCLUDE = {"pcb-a-power": {"J_DOCK", "J_PRE1", "RT1", "L2", "L3", "L4", "L5", "L6"} | {"J_CP%d" % k for k in range(1, 5)} | {"J_CN%d" % k for k in range(1, 5)} | {"J_BM%d" % k for k in range(1, 8)},
           "pcb-d-aprs": {"L1"},
           "pcb-c-display": {"SW_MAIN", "SW_PI", "SW_TEST", "SW_LIGHT", "SW_SOS", "SW_EMCON", "SW_ZERO", "BZ1"},   # C5: the sounder is a panel-mount part like the switches
           "pcb-e1-dock": {"U1", "F1", "F2", "J_BLK", "P_CP", "P_CN", "J_BATT", "L1"},
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
    ("meshsat-pcb-a-revA-A19", "pcb-a-power", "pcb-a-power", "PCB-A POWER + I/O", "A19", "no pack on the board: the battery module on the case floor reaches it through the dock. Bench-fitted: the Preci-Dip 813-S1-012-10-016101 spring connector in J_DOCK and the nine Mill-Max 0858 class power pins (J_CP1-4 CELL+, J_CN1-4 return, J_PRE1 pre-charge, all on the underside, tails soldered on the top face), the seven Radiall R222M00720 SMP-MAX receptacles J_BM1-7 on the underside, the Coilcraft inductors L2 to L4 (XAL1010-222MED, one per converter), L5 (XAL4030-222MEB) and L6 (XAL4020-332MEB), which have no JLC equivalent and are left out of the JLC BOM/CPL, the 103AT-2 thermistor RT1, three 10 A and one 15 A mini blade in the Keystone 3568 holders F2 to F5, VH leads from J_5V_M1, J_5V_M2 and J_5V_PI to PCB-B (the Pi lead ends in a USB-C plug), the XH lead to the heating pad on the module, the LED row lead on J_LEDS1, the MAIN button lead on J_MAINSW, seven SMA pigtails from the modules to J_RF1-7, GPS puck, WiFi dongle, the internal USB cable from J_WALL1 to the Glenair wall receptacle, PCB-D on its four M3 standoffs, harness ribbons"),
    ("meshsat-pcb-b-revA-B13", "pcb-b-compute", "pcb-b-compute", "PCB-B COMPUTE", "B13", "Compute Module 5 (CM5108064, 8 GB, 64 GB eMMC, wireless) pressed onto the two Amphenol receptacles and screwed to four M2.5 x 4.0 standoffs, the CM5 Cooler on it with its fan lead in J_FAN and its antenna lead to the WiFi bulkhead; Quectel EG25-G mini PCIe card in J_LTE1 on two M2.5 standoffs with a nano-SIM in J_SIM1 and pigtails to the LTE bulkhead; RTL-SDR or LimeSDR in the SDR bay; RockBLOCK on its site; the Touch Display 2 flex in J_DISP; CR2032 in BT1; the three JST-VH rail leads from PCB-A into J_5V_M1, J_5V_M2 and J_5V_PI (no plug on the module); J_AB1 2x9 and J_PANEL ribbons; NEO-M9N, Wio-SX1262 and E72 antenna pigtails to their bulkheads (appendix 32.35)"),
    ("meshsat-pcb-c-revA-C5", "pcb-c-display", "pcb-c-display", "PCB-C CONTROL PANEL", "C5", "sealed face (appendix 32.34): Touch Display 2 through the aperture on a die-cut 0.5 mm closed-cell foam tape frame (3M VHB class, outline on User.2 / pcb-c-display-seals.dxf), connector end to port, glass about 1.2 mm proud; SW_MAIN C&K ATP19-SL1-603-B0SA-03G (19 mm, green ring), SW_PI C&K ATP16-SL1-403-M0SA-04G (16 mm, orange ring as the amber), SW_TEST C&K ATP16-SL1-203-M0SA-04G (16 mm, white ring), each on a die-cut 1.0 mm silicone gasket washer under the bezel, flying leads to the solder lands on the underside; SW_LIGHT NKK M2044SD3A01 DPDT ON-ON-ON on the D3 splashproof bushing in the D hole (flat east), its O-ring under the nut, AT428H boot; SW_SOS, SW_EMCON and SW_ZERO APEM 5636ADKB-2V locking toggles with the K front seal keyed into the notch (both positions locked, 1/4-40 bushing 9 mm; SOS and ZEROIZE are maintained and the bridge times them, ruling 32.13); BZ1 IP67 panel-mount sounder in its own hole with its bezel gasket, two flying leads; WeAct 3.7 e-paper module under the panel: glass into the recessed window, both PCB lands taped, 1.5 mm hard-coated polycarbonate lens on a 0.5 mm foam tape frame over the window on the face, 1x8 lead to the SMD header J_EPD; a neutral-cure silicone bead on each of the 32 LED joints on the underside, then the acrylic conformal coat over the whole underside with the connector faces masked; the die-cut 0.5 mm PORON gasket ring on the frame's bearing ring (User.2 outline), 16 x M3 x 10 with bonded sealing washers from below, 0.4 N m; ribbon on J_PANEL (SMD box header), the MAIN and PI leads soldered to J_MAINSW and J_PIJ2 and beaded"),
    ("meshsat-pcb-d-revA-D5", "pcb-d-aprs", "pcb-d-aprs", "PCB-D APRS", "D5", "DMR858M on 2 x 1x12 female headers 8.5 mm + 2 x M2.5 x 11 mm standoffs (male headers soldered into the module rows from its back face), the boost inductor L1 (Coilcraft XAL6030-152MEB, no JLC equivalent, hand-soldered; left out of the JLC BOM/CPL), SMA pigtail, four M3 x 6 into the PCB-A standoffs"),
    ("meshsat-pcb-e-revA-E4", "pcb-e1-dock", "pcb-e1-dock", "PCB-E1 DOCK STRIP", "E4", "TRACO TEN 40-2412WIN under the gap, Keystone 3568 holders with a 7.5 A blade in F1 and a 10 A in F2, JST-VH shore lead from the MIL-DTL-38999 wall receptacle to J_DCIN and the panel lead to J_SOLAR, the XT60 module entry J_BATT with its 12 AWG pair, twelve hook-up wires from J_BLK and two 12 AWG wires from P_CP and P_CN up to the dock block, the seven printed float clamps holding the Radiall R222M80500 right-angle plugs, four VHB pads to the floor, the two rods through H1 and H2; the EL817 optocoupler and the LT8705A tracker are JLC-fitted"),
    ("meshsat-pcb-e5-revA-E5", "pcb-e5-block", "pcb-e5-block", "PCB-E5 DOCK BLOCK", "E5", "bare 2 oz board, no assembly: it sits on four M3 standoffs 6 mm above the dock strip so its face is at 7.4 mm, PCB-A's spring pins land on the twelve signal targets and the nine power targets, and the wires from the strip are soldered into the plated lands underneath (the underside legend names each one)"),
]
# board-specific fabrication options that the generic README cannot know (C5: the panel is the case's top bulkhead)
PCB_OPTIONS = {"pcb-c-display": ["FABRICATION OPTIONS (C5, sealed face)",
    "- Via covering: PLUGGED (solder-mask plugged and covered on both sides, IPC-4761 Type VI-b) on every via. The face of this board is the weather face of the case with the lid open and no open via barrel is acceptable. If the order form offers only tented or untented for this build (2 layers, 2.0 mm, black, ENIG), choose Epoxy Filled and Capped (Type VII) and record the price. The gerbers already tent every via on both faces; do not pick an option that reopens them.",
    "- Outline: three 6.5 mm switch holes carry a 2.70 x 1.10 mm keyway notch and one carries a D flat (5.8 across), all on Edge.Cuts over the drilled hole (routed; the router radius on the notch corners is accepted). The 16 frame screw holes are plated GND rings with the face-side mask closed.",
    "- pcb-c-display-seals.dxf in the deliverable folder carries the die-cut outlines (User.2: frame gasket ring, display tape frame, e-paper tape frame; User.3: the e-paper lens) for the gasket cutter and the lens supplier; it is not a JLC file.", ""]}
JLC = os.path.join(RELEASE, "order"); REV = os.path.join(RELEASE, "review")
# The deliverable folders are written by finish_board.sh on the laptop. Building order/ and review/ from a clone that has
# not received them yet silently falls back to the project board file (older, and with no gerbers), so stop here instead.
missing = [f for f, stem, *_ in BOARDS if not os.path.exists(os.path.join(DL, f, stem + "-gerbers.zip"))]
if missing and os.environ.get("HANDOFF_ALLOW_MISSING") != "1":
    sys.exit("make_handoff: no finished deliverable for %s in %s.\n"
             "Finish those boards and commit their folders from the laptop first, then pull here and rerun.\n"
             "Set HANDOFF_ALLOW_MISSING=1 only if you mean to build the set without them." % (", ".join(missing), DL))
shutil.rmtree(REV, ignore_errors=True); os.makedirs(REV, exist_ok=True); os.makedirs(JLC, exist_ok=True)   # JLCPCB/ is never wiped: ORDER-LOG.md and upload/ copies live there
def run(cmd): r = subprocess.run(cmd, capture_output=True, text=True); return r.returncode == 0, (r.stdout + r.stderr)[-300:]
order_index = ["# MeshSat field-kit carrier boards, JLCPCB order set (generated %s)" % subprocess.run(["date", "+%Y-%m-%d %H:%M"], capture_output=True, text=True).stdout.strip(), "",
               "One sub-folder per board. Upload the Gerber zip first, then (for the assembled boards) the BOM and CPL files in the assembly step.", "",
               "| Folder | Board | Size | Layers | Assembly | Files |", "|---|---|---|---|---|---|"]
review_index = ["# MeshSat field-kit carrier boards, review prints (generated)", "",
                "Print everything at 100 % scale (no fit-to-page). The 1:1 sheets are for laying the real devices on paper; the copper sheets and the assembly drawings are for the design review (appendix section 21.3 / 22.4: the six order-gate items are the agenda).", ""]
for folder, stem, prj, title, phase, hand in BOARDS:
    src = os.path.join(DL, folder); board_file = os.path.join(src, stem + ".kicad_pcb")
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
    notes = ["MeshSat field-kit carrier %s Rev A, phase %s: JLCPCB order notes" % (title, phase), "",
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
    order_index.append("| `%s/` | %s Rev A (%s) | %.0f x %.0f mm | %d | %s | %s |" % (tag, title, phase, W, H, NL, ("top %d + bottom %d parts, %d DNP removed" % (len(top), len(bot), len(removed))) if assembled else "none (PCB only)", ", ".join(files)))
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
    if stem == "pcb-c-display":                                            # official Touch Display 2 documents ride along with the display board
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
                "The BOM/CPL copies here have the DNP lines removed (U2 on PCB-D is the bench-fitted DMR858M, R46 on PCB-A is the PSEL alternative); the full BOMs stay in the deliverable folders.",
                "Order after the 12 Sep design review (appendix section 21 / 22)."]
open(os.path.join(JLC, "README.md"), "w").write("\n".join(order_index) + "\n")
review_index += ["## Review agenda (appendix 21.3 / 22.4)", "", "1. PCB-A: BQ25601 pin map (PSEL on R45/R46, /QON on TP11), 103AT-2 thermistor network, CSD17303Q5 cell switches, boost/buck chain on shore power.",
                 "2. PCB-B: no F1 (both XH inputs on +5V), 2 A polyfuse + TPS22810 per channel, T-Beam 1W strip and the dual SDR bay, USB pairs.",
                 "3. PCB-D: STM32F302CBT6 (128 KB) for the AIOC firmware, TPS61089 boost at 7.6 V with the 100k ILIM, DMR858M site on sockets and M2.5 x 11 standoffs (rows 36.15 mm, pin 1 north-east), heatsink clearance in the bottom bay (about 35 mm).",
                 "4. PCB-C (C5): the sealed face: seal bands and their die-cut outlines, keyed switch holes, the panel-mount sounder, via plugging, the frame gasket ring against the Z closure (32.30).", ""]
open(os.path.join(REV, "README.md"), "w").write("\n".join(review_index) + "\n")
print("done:", JLC, REV)
