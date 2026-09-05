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
    ("meshsat-pcb-a-revA-A21", "pcb-a-power", "pcb-a-power", "PCB-A POWER + I/O", "A21", "A21 is A20 re-routed with the net classes applied (appendix 32.39: the Pi rail and the cell node in their 2.0 and 1.0 mm classes, the USB pairs at 0.2/0.15). no pack on the board: the battery module plugs into the dock block; the twelve Preci-Dip spring pins, four CELL+ and four return Mill-Max pins and the pre-charge pin are pressed in from the underside; the seven Radiall SMP-MAX receptacles on the underside and the seven SMA jacks on top; the DMR858M mezzanine (PCB-D) on four M3 standoffs with the 2x8 harness (I2S, I2C, the gated 3.3 V from B13) and the VH cell lead; the J_AB1 2x9 ribbon up to PCB-B; the wall host port cable from J_WALL1 to the Glenair receptacle; the thermistor lead into the module; blade fuses in F2 to F5 (appendix 32.35, 32.36)"),
    ("meshsat-pcb-b-revA-B15", "pcb-b-compute", "pcb-b-compute", "PCB-B COMPUTE", "B15", "B15 is B14 on the JLC06161H-3313 six-layer stack (F.Cu, In1 solid ground plane, In2 and In3 signal, In4 +5V_M1 plane, B.Cu; appendix 32.40 decision 3 and 32.42) with the same parts and the same hand-fitted list. B14 adds the M.2 E-key socket J_WIFI1 on the CM5 PCIe lane for the AsiaRF AW7915-AED WiFi P2P card (own 3.3 V buck on PCIE_PWR_EN, INA219 0x45, two IPEX pigtails to the east wall). Compute Module 5 (CM5108064, 8 GB, 64 GB eMMC, wireless) pressed onto the two Amphenol receptacles and screwed to four M2.5 x 4.0 standoffs, the CM5 Cooler on it with its fan lead in J_FAN and its antenna lead to the WiFi bulkhead; Quectel EG25-G mini PCIe card in J_LTE1 on two M2.5 standoffs with a nano-SIM in J_SIM1 and pigtails to the LTE bulkhead; RTL-SDR or LimeSDR in the SDR bay; RockBLOCK on its site; the Touch Display 2 flex in J_DISP; CR2032 in BT1; the three JST-VH rail leads from PCB-A into J_5V_M1, J_5V_M2 and J_5V_PI (no plug on the module); J_AB1 2x9 and J_PANEL ribbons; NEO-M9N, Wio-SX1262 and E72 antenna pigtails to their bulkheads (appendix 32.35)"),
    ("meshsat-pcb-c-revA-C6", "pcb-c-display", "pcb-c-display", "PCB-C PANEL BACKER", "C6", "C6 is the U-shaped backer board under the 3 mm aluminium face plate of the Peli 1450 (appendix 32.40 item 5, 32.42; the plate set is in release/revA/case/face-plate/): it hangs 10 mm under the plate on six PEM SO-M3-10 standoffs (M3 x 6 screws through H1 to H6, which bond the plate to GND) and carries the panel electronics, the sixteen 3 mm LEDs standing on the top face under the plate's Mentor 1282.5004 light guides (bench-soldered, beaded to height), J_PANEL and J_EPD SMD on the underside, the driver cluster on the underside of the right strip. The switches and the sounder mount in the PLATE, not on this board: SW_MAIN C&K ATP19-SL1-603-B0SA-03G, SW_PI C&K ATP16-SL1-403-M0SA-04G, SW_TEST C&K ATP16-SL1-203-M0SA-04G (silicone washer under the bezel), SW_LIGHT NKK M2044SD3A01 (O-ring, AT401A boot), SW_SOS, SW_EMCON and SW_ZERO APEM 5636ADKB-2V (K seal in the keyway), BZ1 Floyd Bell MC-09-530-Q (61663 gasket); their bodies pass the backer through the body slots and their own holes and their leads go to the solder lands beside each site; MAIN and PI leads on J_MAINSW and J_PIJ2 lands"),
    ("meshsat-pcb-d-revA-D7", "pcb-d-aprs", "pcb-d-aprs", "PCB-D APRS", "D7", "D7 fits the DMR858M V1.0 board as delivered (MESHSAT-804): carrier detect and channel code read on a PCA9555 (0x26), the control UART on an SC16IS740 I2C bridge (0x48), mic level divider 47k/1k, no channel jumpers, no bench UART header. DMR858M on 2 x 1x12 female headers 8.5 mm + 2 x M2.5 x 11 mm standoffs (male headers soldered into the module rows from its back face), the boost inductor L1 (Coilcraft XAL6030-152MEB, no JLC equivalent, hand-soldered; left out of the JLC BOM/CPL), SMA pigtail, four M3 x 6 into the PCB-A standoffs"),
    ("meshsat-pcb-e-revA-E4", "pcb-e1-dock", "pcb-e1-dock", "PCB-E1 DOCK STRIP", "E4", "TRACO TEN 40-2412WIN under the gap, Keystone 3568 holders with a 7.5 A blade in F1 and a 10 A in F2, JST-VH shore lead from the MIL-DTL-38999 wall receptacle to J_DCIN and the panel lead to J_SOLAR, the XT60 module entry J_BATT with its 12 AWG pair, twelve hook-up wires from J_BLK and two 12 AWG wires from P_CP and P_CN up to the dock block, the seven printed float clamps holding the Radiall R222M80500 right-angle plugs, four VHB pads to the floor, the two rods through H1 and H2; the EL817 optocoupler and the LT8705A tracker are JLC-fitted"),
    ("meshsat-pcb-e5-revA-E5", "pcb-e5-block", "pcb-e5-block", "PCB-E5 DOCK BLOCK", "E5", "bare 2 oz board, no assembly: it sits on four M3 standoffs 6 mm above the dock strip so its face is at 7.4 mm, PCB-A's spring pins land on the twelve signal targets and the nine power targets, and the wires from the strip are soldered into the plated lands underneath (the underside legend names each one)"),
]
# board-specific fabrication options that the generic README cannot know (C6: the backer under the aluminium face; B15: six layers)
PCB_OPTIONS = {"pcb-b-compute": ["FABRICATION NOTES (B15, Compute Module 5 carrier with the M.2 WiFi socket on the six-layer stack, appendix 32.35, 32.37, 32.40 and 32.42)",
    "- Six layers on the JLC06161H-3313 stack (1.6 mm): F.Cu, In1 = solid ground plane, In2 and In3 signal, In4 = +5V_M1 plane, B.Cu. The gerber zip carries all six copper layers; check the layer count on the order form (6) and quote the six-layer price in the order log.",
    "- The two Compute Module receptacles U30A and U30B (Amphenol 10164227-1004A1RLF, 0.40 mm pitch) are escaped as on Raspberry Pi's own CM5 IO board: 0.40 mm vias with 0.20 mm drills at the pad tips, 0.127 mm tracks, 0.127 mm clearance, 0.19 mm hole-to-copper clearance. All within the standard four-layer capability; do not let a DFM tool widen them.",
    "- Differential pairs: USB 2.0 pairs 0.20/0.15 mm (90 ohm), display DSI pairs 0.17/0.15 mm (100 ohm), PCIe pairs 0.15/0.15 over the In1 ground; ask for impedance tuning on the JLC06161H-3313 stack if offered.",
    "- The Compute Module itself, its cooler, the LTE card, the SIM, the SDR stick, the RockBLOCK, the display flex and the CR2032 are fitted at the bench (not in the BOM/CPL).", ""],
    "pcb-c-display": ["FABRICATION NOTES (C6, the backer under the aluminium face plate)",
    "- A plain two-layer 1.6 mm board (any colour, HASL or ENIG); nothing on it is a weather face any more (the aluminium plate is), so no via plugging and no special mask rules.",
    "- Outline: a U (344 x 228 outside, 252 x 202 void open toward +Y) with R3 outer corners; the two 15 x 22 and one 15 x 12 body slots and the 19.2, 16.2, 16.2 and 28.6 mm holes are on Edge.Cuts (routed). The six 3.2 mm holes H1 to H6 carry 6.0 mm rings on both faces: they are the ground bond to the plate through the PEM standoffs.",
    "- The face plate is a separate CNC part (release/revA/case/face-plate/: STEP, DXF, marking SVG, drawing); it is not a JLC PCB order.", ""]}
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
                 "4. PCB-C (C6): the backer under the 1450 face plate: every site against panel1450.py and the plate drawing, the body slots, the six ground-bond holes, the deep parts outside PCB-B's outline, the stack height map (32.42).", ""]
open(os.path.join(REV, "README.md"), "w").write("\n".join(review_index) + "\n")
print("done:", JLC, REV)
