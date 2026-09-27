"""The registry and document half of the QMX lid tray r2 (MESHSAT-1357, S-63 and EQ-24; branch fnd/w5tray from c23c5e76; first
drafted 27 September 2026 for the first pass of the design, recovered and corrected to its second pass the same day). DRAFT for the integrator:
every edit is made by record id or by an anchor whose old text is asserted, every new text is asserted to differ from the old, both
YAML files are re-parsed after they are written, a second run refuses, and every new id is the next free one of its kind in the file it
runs on, so the script applies on a main that has moved (tested on a copy of main 6ec37197 with this branch's files laid over it, where
it takes SC-64, S-82, S-83 and EQ-31). The ids it took are printed and written to the JSON file named as its argument. Run from the
root of the integration tree, AFTER the tree carries this branch's files (v2/cad/lid_tray_qmx_r2*.py,
v2/release/case-2026-09-27/lid-tray-qmx-r2/, v2/vendor/qrp-labs/, v2/vendor/materials/ and v2/vendor/standards/ additions). Taken by
the session under the owner's standing rule of 26 September 2026; nothing here is the owner's. Then:
`python3 v2/ecad/tools/rules_lib.py requirements` (0 errors), re-render v2/docs/REQUIREMENTS-TRACE.md, and run
`python3 v2/ecad/tools/tests/run.py lid_tray_qmx_r2 case_geometry requirements`.

  - registry: a session choice (the next free SC-nn, drafted_as SC-TR-01) records the r2 tray and closes S-63; S-63 moves to
    closed_items; two new open items (the next free S-nn): the lid harness's crossing of the sealed face (not designed anywhere),
    and the r2 tray's verification (the bond, E1's peak, the knob height, the harness picks);
  - ENGINEERING-QUESTIONS: EQ-24 answered (index row, attempts, next action); a new question (the next free EQ-nn) for the harness
    crossing; the preamble names this set;
  - ASSEMBLY.md: the QMX tray row, build steps 10 and 11, the lead table's three QMX rows, the removal paragraph, the parts list and
    note (13)'s last sentence;
  - v2/BUILD.md: the bill's QMX sentence AND build step 9 (the first draft missed step 9);
  - CASE-FIT-UNCERTAINTIES.md section 3: the QMX row restated for r2;
  - CASE-MARGINS.md: C5 gains the r2 note, T8 the lid plate's pull test, T9 the knob tips, the lookups the knob height;
  - v2/README.md: the QMX sentence points at r2;
  - v2/docs/handover/START-HERE.md: the case release row;
  - v2/vendor/README.md: a row for the new materials folder; v2/vendor/SOURCES.yaml: documents_filed_w5tray.
"""
import json, re, sys

OUT_JSON = sys.argv[1] if len(sys.argv) > 1 else "v2/docs/records/w5tray/drafts/ids-taken.json"


def rd(p): return open(p, encoding="utf-8").read()


def wr(p, t): open(p, "w", encoding="utf-8").write(t)


def sub(t, a, b, where=""):
    assert t.count(a) == 1, (where, t.count(a), a[:100]); assert a != b
    return t.replace(a, b)


def rec(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1
    j = t.find("\n  - id: ", i + 5)
    k = t.find("\n\n#", i)
    ends = [x for x in (j, k) if x > 0]
    return i, (min(ends) + 1 if ends else len(t))


def wrap(text, indent=6, width=120):
    words = text.split(); lines = []; cur = " " * indent
    for w in words:
        if len(cur) + 1 + len(w) > width and cur.strip(): lines.append(cur); cur = " " * indent + w
        else: cur = (cur + " " + w) if cur.strip() else cur + w
    lines.append(cur)
    return "\n".join(lines) + "\n"


def folded(key, text, indent=4):
    return " " * indent + key + ": >-\n" + wrap(text, indent + 2)


def next_free(prefix, t):
    return max(int(m) for m in re.findall(r"\n  - id: %s-(\d{2})\n" % prefix, t)) + 1


REL = "v2/release/case-2026-09-27/lid-tray-qmx-r2"
REC = REL + "/lid-tray-qmx-r2-check.out"

# ---------------------------------------------------------------------------------------------------------- the documents as found
import hashlib
def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
def section(text, head, nxt):
    i = text.index(head); j = text.index(nxt, i); return text[i:j]
BEFORE = {p: rd(p) for p in ("v2/docs/ASSEMBLY.md", "v2/docs/CASE-MARGINS.md", "v2/docs/CASE-FIT-UNCERTAINTIES.md")}
SHA_BEFORE = {p: sha16(p) for p in BEFORE}

# ---------------------------------------------------------------------------------------------------------- the registry
P = "v2/ecad/tools/pcb_requirements.yaml"
t = rd(P)
assert "\n  - id: S-63\n" in t, "S-63 is not an open item here: re-read the tree before applying"
assert "SC-TR-01" not in t, "already applied"
SC = "SC-%02d" % next_free("SC", t)
S_H = "S-%02d" % next_free("S", t)
S_V = "S-%02d" % (next_free("S", t) + 1)
EQF = "v2/docs/handover/ENGINEERING-QUESTIONS.md"
EQ = "EQ-%02d" % (max(int(x) for x in re.findall(r"^### EQ-(\d{2})\.", rd(EQF), re.M)) + 1)
print("apply_w5tray: session choice", SC, "(drafted_as SC-TR-01); open items", S_H, "(the harness crossing),", S_V, "(r2 verification); question", EQ)

sc_entry = ("  - id: %s\n    authority: SESSION\n    under: standing-rule\n    taken_on: \"2026-09-27\"\n    drafted_as: SC-TR-01\n" % SC
            + folded("question", "How the QMX lid tray fits the unit, which has jacks on both end panels, and how it keeps the unit through "
                     "TEST-PLAN E1 and E2 (S-63, ENGINEERING-QUESTIONS EQ-24).")
            + folded("taken", "The r2 set of v2/cad/lid_tray_qmx_r2.py, %s/ with sheets 14r2-1 to 14r2-3, which supersede the r1 tray and "
                     "sheet 14: both end panels open over their whole height above a 1.5 mm sill, the sill cut to the floor under the RF "
                     "jack; the unit top face out, its knob edge west and its right panel toward the hinge; LOWERED INTO AN OPEN POCKET FROM "
                     "ABOVE (a floor, two long walls buttressed by posts, a sill at each end) and held by a flat retaining frame laid on the "
                     "wall tops and screwed with six M3 x 10 into square nuts in the posts, its ledges clear of both knobs, with two Rogers "
                     "PORON 4701-30 pads pressing the unit to the ledges; both printed parts in Prusament PC Blend; the tray fixed by ten flush "
                     "M3 x 5 into a 2.0 mm 5052-H32 lid plate bonded to the lid with 3M DP8005; all sixteen M3 at 0.25 N m; the retention "
                     "designed to 100 g on the unit, the peak CASE-MARGINS.md assumes for E1; its east edge kept at X 171.0 (C5, M19 "
                     "unchanged) and grown west to X 83.2. The set stands beside the case release with its own manifest; no file of the "
                     "release is edited." % REL)
            + folded("why", "QRP Labs states the enclosure (95 x 63 x 25 without protrusions, 220 g) and draws both end panels undimensioned; "
                     "the jack places scaled from those figures and from the maker's photograph disagree by up to 3.8 mm (the RF jack), so a "
                     "tray open across each end admits every jack's plug whichever reading holds, which boolean checks on the built solids "
                     "confirm (%s). A first pass held the unit under ledges and end lintels that were part of the tray; its checker found "
                     "that the unit cannot pass under a lintel at the height of its top face, above which its knobs, encoder shafts and "
                     "button actuators stand, so the unit goes in from above and the frame is screwed on after it: the record sweeps the "
                     "unit at its largest and the frame along their way in (0.30 and 4.15 least clearance against a stated 0.20) and runs "
                     "the first pass's tray through the same check as a control that fails. The controls face the operator with the lid "
                     "open, and the VOL knob switches the radio (operating manual 1_04_004 section 4). PETG's heat deflection (68 C at 0.45 "
                     "MPa) is under TEST-PLAN E3-S's +71 C and PC Blend's is 113 C, 93 C at 1.80 MPa (v2/vendor/materials/). The case takes "
                     "no hole (ruling of 7 September 2026), so the plate is bonded. On the makers' typical figures every link holds 7.1 "
                     "times the 100 g load case or more (707 g, the frame's screws); E1's peak on the lid is stated by no held document and "
                     "its half-sine bound, 96 to 958 g over 20 to 2 mm of stopping distance, includes failure; no board, interface or "
                     "purchase depends on it, so the retention's verification stays open as %s. Reverse by a maker's dimensioned panel "
                     "drawing that lets an end wall stand clear of every plug, by E1 or E2 showing a lighter retention holds, or by a lid "
                     "item that needs X 83.2 to 102.0." % (REC, S_V))
            + "    source: [\"%s/README.md\", \"v2/cad/lid_tray_qmx_r2.py\", \"%s\", \"v2/vendor/qrp-labs/qmx-figures.out\"]\n" % (REL, REC)
            + "    closes: [S-63]\n")
anchor = "\n\n# What is still open. SESSION items are engineering the session decides"
assert t.count(anchor) == 1
t = t.replace(anchor, "\n" + sc_entry.rstrip("\n") + anchor)

i, j = rec(t, "S-63")
s63 = t[i:j]
assert s63.startswith("  - id: S-63\n    class: SESSION\n    status: OPEN\n    title: >-\n") and "does not\n" in s63, s63[:200]
t = t[:i] + t[j:]
s63_title = s63.split("    title: >-\n", 1)[1]
closed = "  - id: S-63\n    closed_by: %s\n    title: >-\n%s" % (SC, s63_title)
anchor = "\n\nrecords:\n"
assert t.count(anchor) == 1
t = t.replace(anchor, "\n" + closed.rstrip("\n") + anchor)

new_open = ("  - id: %s\n    class: SESSION\n    status: OPEN\n" % S_H
            + folded("title", "(w5tray, the QMX lid tray r2) The lid harness, the QMX's DC lead, USB-C lead and RG-316 jumper, has no designed "
                     "path from the lid to board B's J_QMX and board A's J_HF and J_RF2 under the face plate: C1's plate covers the frame "
                     "window and Peli's o-ring with no pass-through, and ASSEMBLY.md build step 10 ties the harness along the hinge side "
                     "without saying where it crosses the sealed face. Design the crossing (a sealed bulkhead connector set in the plate's top "
                     "strip near the hinge, or a sealed gland), its seal against REQ-021 and CON-008, its place in panel1450.py and the face "
                     "plate, the harness split and lengths and the lid's swing, then a new case release. It blocks the harness picks, "
                     "ASSEMBLY.md's lid harness steps and the closing of the lid on a wired QMX (so E6, E7 and E8 for a kit with its QMX "
                     "connected); it does not block printing or fitting the r2 set, and it moves no board connector. The tray is not changed "
                     "by it; its leads' admitted plug bodies and bend radii are %s section A. ENGINEERING-QUESTIONS %s." % (REC, EQ), indent=4)
            + "  - id: %s\n    class: SESSION\n    status: OPEN\n" % S_V
            + folded("title", "(w5tray, the QMX lid tray r2) What the desk cannot close on the r2 set (%s sections B, C and D): (1) the lid "
                     "plate's DP8005 bond on the case's polypropylene, bounded by no held figure (the adhesive's sheet gives a T-peel on HDPE "
                     "only), and across -33 to +71 C (no expansion figure of Peli's polypropylene or of PC Blend is held): a pull test with "
                     "CASE-MARGINS T8 after a thermal cycle; (2) the peak TEST-PLAN E1 puts on the lid, stated by no held document: E1 with an "
                     "accelerometer on the lid, against the 100 g the set is designed to and the 707 g its known links hold; (3) the QMX "
                     "knob's height above the top face, not stated by QRP Labs (11.6 scaled, INFERRED): the two knob rows are OPEN, 3.06 over "
                     "the flat face and 2.26 over the monitor's window at the worst, 0.35 and -0.45 with unstated allowances twice, MET there "
                     "for a knob up to 10.15 and at the plain worst up to 12.86: T9 with chalk on the knob tips, or the unit in hand; (4) the "
                     "lid's response in TEST-PLAN E2 (the pads' preload keeps the unit seated if the lid magnifies the case's 6.72 g by less "
                     "than 1.3 to 3.3) and the pads' preload and the frame's sustained stress at the pads' real compression, read in E2 and "
                     "after E3-S and E4-S; (5) the harness picks (the RG-316 BNC plug, the USB-C lead, the 2.1 x 5.5 plug lead) against the "
                     "admitted plug bodies and the lanes' R 20, and a threadlocker its maker states compatible with polycarbonate; (6) the "
                     "unit's own heat in the pocket, not assessed. No board, interface or purchase depends on (1) to (4): the remedy is a "
                     "made part (the same parts machined in 6061, a larger plate, a lid plate cut out under the unit)." % REC,
                     indent=4))
anchor = "\n\n# Items that left the open list, and what closed each"
assert t.count(anchor) == 1
t = t.replace(anchor, "\n" + new_open.rstrip("\n") + anchor)
wr(P, t)

# ---------------------------------------------------------------------------------------------------------- ENGINEERING-QUESTIONS
e = rd(EQF)
e = sub(e, "| EQ-24 | The QMX lid tray does not fit the unit's connector layout (jacks on both end panels) | A. design work | 7 | none (a made part) | printing the tray (S-63) |",
        "| EQ-24 | The QMX lid tray does not fit the unit's connector layout (jacks on both end panels) | A. design work | 7 | none (a made part) | answered by the r2 tray (`%s/`, SC-TR-01, S-63 closed); its verification is %s, the harness crossing %s (%s) |" % (REL, S_V, S_H, EQ), "EQ-24 row")
last_no = max(int(x) for x in re.findall(r"^\| EQ-(\d{2}) \|", e, re.M))            # the index's last row, whatever main has added
last_idx = [l for l in e.splitlines() if l.startswith("| EQ-%02d |" % last_no)]
assert len(last_idx) == 1 and last_no + 1 == int(EQ[3:]), (last_no, EQ)
e = sub(e, last_idx[0] + "\n", last_idx[0] + "\n| %s | The lid harness (the QMX's DC, USB-C and RF leads) has no designed crossing of the sealed face plate | A. design work | 7 | B, A (their QMX leads' ends); the face plate | the QMX's use in a closed case; a new case release (%s) |\n" % (EQ, S_H), "index")
old = "| **Recommended next action** | (a): desk work on a made part, no board moves and no money. |"
e = sub(e, old, old[:-2] + " **Answered on 27 September 2026 (set w5tray):** option (a) taken as the session's choice SC-TR-01 under the owner's standing rule of 26 September 2026: the r2 set `%s/` (sheets 14r2-1 to 14r2-3, `lid-tray-qmx-r2-check.out`), from the maker's enclosure figure (95 x 63 x 25, 220 g, `v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt` and the assembly manual's page 3) and its panel figures scaled and cross-checked on the maker's photograph (`qmx-figures.out`): open at both end panels, the unit lowered in from above and held by a screwed retaining frame; S-63 closed. What stays open: %s (the bond, E1's peak on the lid, the knob height, E2, the harness picks) and %s (%s, the harness's crossing of the sealed face). |" % (REL, S_V, S_H, EQ), "EQ-24 next action")
old_att = [l for l in e.splitlines() if l.startswith("| **Attempts and results** | Found by the layer 7 fixer c7 while drawing sheet 14")]
assert len(old_att) == 1
e = sub(e, old_att[0], old_att[0][:-2] + " **27 to 27 September 2026 (set w5tray):** the maker's enclosure figure is on qrp-labs.com (the product page) and in the assembly manual; neither states the jack places, so they were scaled from the operating manual's panel figures (to the maker's 63 x 25 within 0.4 percent) and read on the maker's photograph of the right panel, which disagree on the RF jack by 3.8 mm. Option (a) was then drawn so that no reading matters: both ends open above a 1.5 mm sill. A first pass held the unit under ledges and lintels that were part of the tray; its checker (an AI review) found that the unit cannot be fitted into it and that its face-room row for the buttons was measured from the wrong solid. The second pass lowers the unit in from above under a screwed frame, sweeps the unit and the frame along their way in, and reads every face-room row from the deepest solid over the part; boolean checks on the solids show every admitted plug body clear, and the first pass's tray fails both checks as a control. |", "EQ-24 attempts")
eq_sec = """### %(EQ)s. The lid harness has no designed crossing of the sealed face plate (%(S)s)

Added on 27 September 2026 by the QMX lid tray r2 (set w5tray), which found it while drawing the leads' lanes.

| | |
|---|---|
| **Exact issue** | The QMX rides in the lid (`%(REL)s/`). Its DC lead, USB-C lead and RG-316 jumper run to board A's `J_HF` and `J_RF2` and board B's `J_QMX`, which sit under the face plate. C1's plate lies on the 1450PF frame over Peli's o-ring and covers the whole frame window (377.2 x 263.0, `panel1450.py`); it has no pass-through, and `ASSEMBLY.md` build step 10 ties the three leads "along the hinge side with a service loop" without saying where they cross the sealed face. A lead pinched between the plate and the lid's rim would break the seal (REQ-021, CON-008) and the lead. |
| **Affected** | The face plate (a released CNC part, C1) and its seal; the lid harness (lengths, a split); the QMX's use with the lid closed; nothing on a board (`J_QMX`, `J_HF`, `J_RF2` stay). **It blocks** the harness picks, `ASSEMBLY.md`'s lid harness steps, the closing of the lid on a wired QMX, and E6, E7 and E8 for a kit with its QMX connected; it does not block printing or fitting the r2 set. |
| **Evidence** | `panel1450.py` (PLATE, FACE_ITEMS: no harness hole); `v2/release/case-2026-09-27/face-plate/`; `ASSEMBLY.md` step 10 and the removal paragraph; `%(REC)s` section A (the leads leave the tray toward the hinge at R 12.5 and R 20). |
| **Attempts and results** | None before this: the r1 tray and every case release placed the harness without a crossing. |
| **Viable options** | (a) A sealed panel-mount connector set in the plate's top strip near the hinge (a DC pair, a USB 2.0 pair and an RF coaxial contact, or one circular connector carrying all three), the lid half of the harness plugging into it, so the lid and the plate each stay separable; (b) a sealed cable gland in the plate with the harness permanent through it, unplugged at B16 and A22 when the plate is lifted; (c) a lid-side battery or radio independence: not viable, the QMX's power and data come from the boards. |
| **Recommended next action** | (a), for the case writer at the next case release: pick the connectors from makers' sheets (IP rating mated and unmated, the RF contact's frequency and loss at 30 MHz, the DC rating at 12 V and 1.5 A), place them clear of the top strip's parts (`panel1450.STRIP_T`, the camera, J_PANEL's ribbon) and of the lid's closed geometry, and add the hole to the face plate as a new version. |
| **Expertise or equipment** | The case writer; the makers' connector sheets. |
| **Cost and lead time** | Desk work; the connectors are a purchase at the build (their price is the pick's, TBD). |

""" % dict(EQ=EQ, S=S_H, REL=REL, REC=REC)
anchor = "\n## B. Physical evidence\n"
assert e.count(anchor) == 1
e = e.replace(anchor, "\n" + eq_sec.rstrip("\n") + "\n" + anchor)
pre = "Internal names are defined in `v2/docs/handover/GLOSSARY.md`."
e = sub(e, pre, "**The QMX lid tray r2 (27 September 2026, branch `fnd/w5tray`)** answers EQ-24 in its attempts and next-action rows and adds %s, the lid harness's crossing of the sealed face; its citations are at that branch's commits. " % EQ + pre, "preamble")
wr(EQF, e)

# ---------------------------------------------------------------------------------------------------------- ASSEMBLY.md
A = "v2/docs/ASSEMBLY.md"
a = rd(A)
i = a.index("| QMX tray on the lid, 4 x |"); j = a.index("\n", i)
row = a[i:j]
assert row.endswith("| 0.4 N m | Loctite 243 |") and "Its fit to the unit is OPEN" in row, row[-200:]
a = a[:i] + ("| QMX tray on the lid (r2), 10 x and 6 x | **Replaced 27 September 2026 (MESHSAT-1357, S-63, SC-TR-01): the r2 set** `v2/release/case-2026-09-27/lid-tray-qmx-r2/` "
             "(sheets 14r2-1 to 14r2-3; the r1 tray of `lid-tray-qmx/` and sheet 14 are superseded and not printed): a 2.0 mm 5052-H32 lid plate "
             "(`lid-plate-qmx-r2.dxf`, ten M3 tapped through) bonded to the lid's unribbed inner face with 3M DP8005 at case X 83.2 to 171.0, Y -45.9 "
             "to 65.9 (its east edge where C5 put r1's, M19 unchanged); the tray, printed in Prusament PC Blend (100 percent infill, 0.20 mm layers), "
             "on it with ten M3 x 5 countersunk hex socket (ISO 10642 class) A2; two Rogers PORON 4701-30 pads (3.18 mm, 24 x 20) in the floor "
             "windows; the unit, without its optional rubber feet and with its knobs on, top face out, its knob edge west and its right panel (RF, "
             "PTT, USB) toward the hinge, LOWERED INTO THE POCKET FROM ABOVE; the retaining frame (PC Blend, flat, 3.0) laid over it on the wall tops "
             "and screwed with six M3 x 10 button head (ISO 7380-1 class) A2 into six M3 square nuts (DIN 562 class) in the posts' slots, which "
             "compresses the pads by 1.08. Both end panels stay open: every jack takes its plug (`lid-tray-qmx-r2-check.out` section A) "
             "| 0.25 N m on all sixteen (INFERRED; the r1 row's 0.4 N m would load 1.4 mm of thread in 5052 to 67 percent of what it strips at) | a threadlocker whose maker states it compatible with polycarbonate (the pick is TBD; r1 named Loctite 243 for a PETG tray) |") + a[j:]
a = sub(a, "10. Lid: the QMX tray screwed to the lid's inner face over the right strip, the unit strapped in, its USB-C lead to B16 `J_QMX`, its 12 V lead to A22 `J_HF` and its BNC-to-SMA jumper to A22's HF jack `J_RF2`, the three in one lid harness tied along the hinge side with a service loop.",
        "10. Lid (**r2, 27 September 2026**): the lid plate bonded with DP8005 (clamped 2 h), the tray screwed to it, the pads laid in, a square nut in each of the six slots, the unit lowered in from above with the lid held level, and the frame screwed over it (the QMX tray row above; sheet 14r2-3 note 1); its USB-C lead to B16 `J_QMX`, its 12 V lead to A22 `J_HF` and its BNC-to-SMA jumper to A22's HF jack `J_RF2`, each tied within 60 mm of its plug to a tie mount bonded to the lid so that no lead pulls on a jack, the three in one lid harness tied along the hinge side with a service loop (as installed the RG-316 turns at R 12.5 and the DC and USB leads at R 20, so each lead's own least bend radius must be no larger than that; the harness's crossing of the sealed face is not designed yet, %s, %s). The Paddle, Audio and PTT jacks are the operator's and are unplugged before the lid closes." % (S_H, EQ), "step 10")
a = sub(a, "the QMX tray hangs 28 mm from that face and its plan window was sized against the old boxed monitor's east edge, which no longer constrains it (appendix 32.60 item 5, 32.85).",
        "the QMX tray hangs 28 mm from that face and its plan window was sized against the old boxed monitor's east edge, which no longer constrains it (appendix 32.60 item 5, 32.85). **r2 (27 September 2026):** with its lid plate the set's frame stands 32.30 below the ceiling, its six screw heads 33.95, the unit's top face 29.30 and its knob tips 40.90 (knob 11.6, INFERRED). Every face part under the set has its own row in `lid-tray-qmx-r2-check.out` section B, from the deepest solid over it and the part's height from its maker's sheet: the three buttons stand under the frame with heads of 3.50 and 2.50 (C&K ATP19 and ATP16 with their O-rings), 7.96 and 8.96 mm clear at the worst; the knob tips are 3.06 over the flat face and 2.26 over the monitor's window at the worst, 0.35 and -0.45 with every unstated allowance taken twice, so the two knob rows are OPEN until T9; the knobs sit west of the buttons' column.", "step 11")
a = sub(a, "| HF rail (12.0 V, EMCON gated) | A22 `J_HF` (VH) | the QMX's DC lead (2.1 mm barrel) in the lid harness | 18 AWG, 500 mm | VH at A22 |",
        "| HF rail (12.0 V, EMCON gated) | A22 `J_HF` (VH) | the QMX's DC lead (2.1 mm barrel) in the lid harness | 18 AWG, 500 mm, a lead whose least bend radius is 20 or under (it is installed at R 20, the r2 tray's loop) | VH at A22; at the unit a straight 2.1 x 5.5 plug within d 18.8 and 55.4 long (r2 record) |", "DC lead row")
a = sub(a, "| QMX USB | B16 `J_QMX` (PH 1x4) | the QMX's USB-C in the lid harness | USB 2.0 lead, 500 mm | PH at B16, USB-C at the unit |",
        "| QMX USB | B16 `J_QMX` (PH 1x4) | the QMX's USB-C in the lid harness | USB 2.0 lead, 500 mm, a lead whose least bend radius is 20 or under (installed at R 20) | PH at B16, USB-C at the unit, its overmold within 8.6 high, 12.35 wide and 35.4 long (r2 record) |", "USB lead row")
a = sub(a, "| HF antenna | the QMX's BNC in the lid harness | A22 `J_RF2` (HF jack) | RG-316, 500 mm | BNC male at the unit, SMA male at A22 |",
        "| HF antenna | the QMX's BNC in the lid harness | A22 `J_RF2` (HF jack) | RG-316, 500 mm, installed at R 12.5, the tree's figure for its least bend radius | BNC male at the unit within d 20.0 and 42.9 long (r2 record), SMA male at A22 |", "RF lead row")
a = sub(a, "Open the lid (the QMX tray swings with it; unplug the lid harness at B16 `J_QMX`, A22 `J_HF` and `J_RF2` if the lid is to come off its hinge)",
        "Open the lid (the QMX tray swings with it; unplug the lid harness at B16 `J_QMX`, A22 `J_HF` and `J_RF2` if the lid is to come off its hinge; the QMX itself comes out of the r2 tray by its three plugs, the frame's six screws and the frame)", "removal")
a = sub(a, "the QMX tray with its nut plates and strap", "the QMX tray r2 (the printed tray and retaining frame, the 5052 lid plate, ten M3 x 5 countersunk A2, six M3 x 10 button head A2 with six M3 square nuts, two PORON 4701-30 pads, DP8005 for the plate, bonded tie mounts for the lid harness)", "parts list")
a = sub(a, "blind-mate tolerance stack, the fans and the floor plan, and the QMX tray's fit to the unit (its fastener row). Nothing of it is",
        "blind-mate tolerance stack, the fans and the floor plan, and the QMX tray's fit to the unit (its fastener row; answered by the r2 set on 27 September 2026, whose verification is %s and whose leads' crossing of the face is %s). Nothing of it is" % (S_V, S_H), "note 13")
wr(A, a)

# ---------------------------------------------------------------------------------------------------------- CASE-FIT-UNCERTAINTIES.md
F = "v2/docs/CASE-FIT-UNCERTAINTIES.md"
f = rd(F)
i = f.index("| The QMX lid tray's fit to the unit (C5;"); j = f.index("\n", i)
assert f[i:j].endswith("it is revised before it is printed |"), f[j - 80:j]
f = f[:i] + ("| The QMX lid tray (C5). **Answered on 27 September 2026 by the r2 set** (`%s/`, SC-TR-01, S-63 closed): from the maker's enclosure "
             "figure (95 x 63 x 25, 220 g) and its panel figures scaled and cross-checked on the maker's photograph (`v2/vendor/qrp-labs/qmx-figures.out`), "
             "open across both end panels above a 1.5 mm sill, the unit lowered in from above and held by a screwed retaining frame, each jack "
             "admitting its plug and the leads their bend radii (the record's section A), the unit and the frame clear of every solid on their way in "
             "(section E), every face part under the set clear at the worst (section B, from the solid over each part; boolean checks on the solids); "
             "its east edge stays at X 171.0 (M19 unchanged), and it grows west to X 83.2. What stays open (%s): the lid plate's DP8005 bond on the "
             "case's polypropylene, the peak E1 puts on the lid (the set is designed to 100 g and its known links hold to 707 g, the drop's bound spans "
             "96 to 958 g), the knob's height (its two rows OPEN: MET with unstated allowances twice for a knob up to 10.15, at the plain worst up to "
             "12.86), E2, the harness picks; and the harness's crossing of the sealed face, which nothing designs (%s, %s) | desk: done for the fit; "
             "the crossing is desk work at the next case release | T8 (the plate's pull test, after a thermal cycle), T9 (the knob tips, chalk), E1 "
             "with an accelerometer on the lid, E2, the look after E3-S and E4-S | none: the set is made parts and the harness ends (B16 `J_QMX`, A22 "
             "`J_HF` and `J_RF2`) do not move; the crossing changes the face plate, a made part |" % (REL, S_V, S_H, EQ)) + f[j:]
wr(F, f)

# ---------------------------------------------------------------------------------------------------------- CASE-MARGINS.md
M = "v2/docs/CASE-MARGINS.md"
m = rd(M)
m = sub(m, "- **Files.** `ASSEMBLY.md:46`; the lid bracket's docstring. **Cost.** None.\n",
        "- **Files.** `ASSEMBLY.md:46`; the lid bracket's docstring. **Cost.** None.\n"
        "- **r2, 27 September 2026 (SC-TR-01, S-63 closed).** The tray that C5 placed is superseded by the r2 set (`v2/cad/lid_tray_qmx_r2.py`, "
        "`%s/`): its east edge stays at X 171.0, so M19 is unchanged, and it grows west to X 83.2 for its posts. Its stack from the lid "
        "ceiling is 32.30 at the retaining frame's face, 33.95 at its six screw heads and 29.30 at the unit's top face, with the knob tips 11.6 "
        "lower (INFERRED); its face-room rows (M3r2.<part>, one for every face part under the set, each from the deepest solid over the part, the "
        "part's height from its maker's sheet and the set's own allowances) are in `lid-tray-qmx-r2-check.out` section B on the room M3 was "
        "computed with. M3 below is the r1 tray's 28.0, which counted no lid plate, until `frame_seat.py` reads the r2 stack (drafted with the "
        "r2 set).\n" % REL, "C5")
m = sub(m, "| T8 | Floor flatness under the pack, the dock strip and the four feet; a VHB 5952 bond test on the case's polypropylene with and without primer, and on the 1450PF's polymer under a leg's pad |",
        "| T8 | Floor flatness under the pack, the dock strip and the four feet; a VHB 5952 bond test on the case's polypropylene with and without primer, and on the 1450PF's polymer under a leg's pad; a pull test of the QMX tray r2's lid plate bonded with DP8005 on a coupon of the case's polypropylene, before and after a thermal cycle between the storage limits (%s) |" % S_V, "T8")
m = sub(m, "| T9 | Lid closure over the tray, the buttons and the toggles (chalk on their tops) | the buttons' height above the face and the tablet bracket are TBD | no mark on the lid |",
        "| T9 | Lid closure over the tray, the buttons and the toggles (chalk on their tops), and over the QMX's knob tips in the r2 tray (chalk on the knobs) | the buttons' height above the face (read from the C&K sheets in the r2 record: 3.50 and 2.50 with their O-rings), the QMX knob's height above its top face (11.6, INFERRED) and the tablet bracket are TBD | no mark on the lid or the face; the unit still clamped under its frame |", "T9")
m = sub(m, "| C&K ATP19/ATP16 height above the panel; APEM 5636 lever height | M3, T9 | the makers' sheets |",
        "| C&K ATP19/ATP16 height above the panel; APEM 5636 lever height | M3, T9 | the makers' sheets |\n| The QMX knob's height above the unit's top face (QRP Labs states none; 11.6 scaled from a photograph of the sibling QCX-mini) | M3r2.FACE and M3r2.XENARC_WINDOW (`lid-tray-qmx-r2-check.out`), T9 | the unit in hand at the build (T9), or a maker's figure |", "lookups")
wr(M, m)

# ---------------------------------------------------------------------------------------------------------- v2/README.md, v2/BUILD.md, START-HERE
R = "v2/README.md"
r = rd(R)
r = sub(r, "the QMX HF unit rides in a printed tray on the lid's inner face (`release/case-2026-09-27/lid-tray-qmx/`, sheet 14 of its drawings, to be revised against the unit's jacks before it is printed, open item S-63),",
        "the QMX HF unit rides in a printed tray on the lid's inner face (`release/case-2026-09-27/lid-tray-qmx-r2/`, sheets 14r2-1 to 14r2-3, which supersede the r1 tray and sheet 14 of that set: open across both end panels so every jack takes its plug, the unit lowered in from above and held by a screwed frame, on a lid plate bonded to the lid; its verification is open item %s),", "README")
wr(R, r)
B = "v2/BUILD.md"
b = rd(B)
b = sub(b, "The QMX lid tray is printed from `release/case-2026-09-27/lid-tray-qmx/` (sheet 14; PETG, about 32 g) once it is revised against the unit's jacks on both end panels (open item S-63) with a 16 mm hook-and-loop strap;",
        "The QMX lid tray is the r2 set `release/case-2026-09-27/lid-tray-qmx-r2/` (sheets 14r2-1 to 14r2-3; the r1 tray and sheet 14 are superseded): the tray (68 g) and its retaining frame (12 g) printed in Prusament PC Blend at 100 percent infill, a 2.0 mm 5052-H32 lid plate cut from its DXF and bonded to the lid with DP8005, ten M3 x 5 countersunk A2, six M3 x 10 button head A2 with six M3 square nuts, and two PORON 4701-30 pads; the harness's crossing of the sealed face is not designed yet (%s);" % S_H, "BUILD")
b = sub(b, "9. Lid: the QMX tray screwed to the lid's inner face over the right strip (1.5 mm further west by case choice C5), the unit strapped in, its three leads in the lid harness",
        "9. Lid: the QMX tray r2 screwed to its lid plate, which is bonded to the lid's inner face over the right strip, the unit lowered in from above and the retaining frame screwed over it (`docs/ASSEMBLY.md` section 9, sheet 14r2-3), its three leads in the lid harness", "BUILD step 9")
wr(B, b)
H = "v2/docs/handover/START-HERE.md"
h = rd(H)
h = sub(h, "| current; the lid tray is not to be printed before S-63 (EQ-24) |",
        "| current; beside it, with its own manifest, `lid-tray-qmx-r2/` of 27 September 2026 (sheets 14r2-1 to 14r2-3) supersedes the r1 lid tray and sheet 14, which are not to be printed (EQ-24 answered; %s, %s) |" % (S_V, EQ), "START-HERE")
wr(H, h)

# ---------------------------------------------------------------------------------------------------------- the vendor index
VR = "v2/vendor/README.md"
v = rd(VR)
row = [l for l in v.splitlines() if l.startswith("| `seals/` |")]
assert len(row) == 1
v = sub(v, row[0] + "\n", row[0] + "\n| `materials/` | Prusa Polymers' technical data sheets for Prusament PC Blend and PETG (v1.1 of 16 February 2022), see `materials/README.md` | the QMX lid tray r2's material (PC Blend) and the reason it is not the r1 tray's PETG (heat deflection 68 C) |\n", "vendor README")
wr(VR, v)
SY = "v2/vendor/SOURCES.yaml"
y = rd(SY)
assert "documents_filed_w5tray" not in y
y = y.rstrip("\n") + "\n" + """
# ADDED 27 SEPTEMBER 2026 (MESHSAT-1357, the QMX lid tray r2, branch fnd/w5tray). Outside `parts:` on purpose, as the closers'
# documents_filed blocks above: the QMX is a bought unit in the lid and the filaments are a made part's material, so they join no BOM line.
documents_filed_w5tray:
  - for_entry: null
    role: "the QMX's enclosure, 95 x 63 x 25 mm without protrusions and 220 g with the enclosure, which the r1 tray typed from no held document (S-63)"
    path: "v2/vendor/qrp-labs/qmx-product-page-2026-09-27.txt"
    doc_id: "QRP Labs, QMX product page (Created 19 May 2023, Last Updated 24 September 2026), text extraction"
    url: "https://qrp-labs.com/qmx.html"
    fetched: "2026-09-27T16:38Z, curl from the runner, HTTP 200, 105306 bytes, HTML sha256 377a906c03afe46a (lost with the first worktree); again 2026-09-27T20:53:04Z, HTML sha256 7da9d31b052540e1, whose text differs in the page's hit counter only and gives this file byte for byte with that line set back"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "the unit as bought (the optional enclosure); the jack places are not stated here"
  - for_entry: null
    role: "the enclosure's size (page 3), its parts (page 21: left and right panels, eight M2.5 screws, four optional rubber feet, two 15 mm knobs), the countersunk panel screws and the knobs' fitting (pages 76 and 77) and photographs 13 and 15 of the sibling QCX-mini in the same enclosure family (what stands proud of the unit, INFERRED)"
    path: "v2/vendor/qrp-labs/qmx-assembly-1_04r-pages-1-3-20-21-75-78.pdf"
    doc_id: "QRP Labs, QMX assembly Rev 1.04r (PCB Rev 4/5), pages 1-3, 20-21 and 75-78, a page subset"
    url: "https://qrp-labs.com/images/qmx/manuals/assembly_1_04r.pdf"
    fetched: "2026-09-27T20:53:05Z, curl from the runner, HTTP 200, 16261051 bytes, sha256 55c08baaf6ca5fb23aa7bd131fb6200374536bf6ae0ac5759f31d742be282a2b (the same at the first fetch of 16:40:30Z); the subset made with Ghostscript 10.00.0 pdfwrite, which writes its run time into the file"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "PCB Rev 4/5; the enclosure is the same family on every revision"
  - for_entry: null
    role: "the maker's photograph of the right panel face on, which cross-checks the scaled panel figure (the RF jack 8.3 mm from the knob edge against the figure's 12.1)"
    path: "v2/vendor/qrp-labs/qmx-product-photo-qmx4-right-panel.jpg"
    doc_id: "QRP Labs, QMX product photograph qmx4.jpg"
    url: "https://qrp-labs.com/images/qmx/1/qmx4.jpg"
    fetched: "2026-09-27T20:53:05Z, curl from the runner, HTTP 200, 192643 bytes (the same bytes as the first fetch of 16:44Z)"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "an early unit's panel; the tray takes both the figure's and the photograph's places"
  - for_entry: null
    role: "the r2 tray's and frame's material: heat deflection 113 C at 0.45 MPa and 93 C at 1.80 MPa, interlayer adhesion 21 +-2 MPa, printed-specimen strengths"
    path: "v2/vendor/materials/prusament-pc-blend-tds-v1.1-2022-02-16.pdf"
    doc_id: "Prusa Polymers, Prusament PC Blend technical datasheet"
    revision: "Version 1.1, last update 16-02-2022"
    url: "https://prusament.com/wp-content/uploads/2022/10/PCBlend_Prusament_TDS_2022_16_EN.pdf"
    fetched: "2026-09-27T20:53:06Z, curl from the runner, HTTP 200, 1601329 bytes (the same bytes as the first fetch of 16:55:56Z)"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "the material the r2 drawing names; typical values of the maker's own specimens"
  - for_entry: null
    role: "the r1 tray's PETG: heat deflection 68 C at 0.45 MPa, under TEST-PLAN E3-S's +71 C (why r2 is PC Blend)"
    path: "v2/vendor/materials/prusament-petg-tds-v1.1-2022-02-16.pdf"
    doc_id: "Prusa Polymers, Prusament PETG technical datasheet"
    revision: "Version 1.1, last update 16-02-2022"
    url: "https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf"
    fetched: "2026-09-27T20:53:06Z, curl from the runner, HTTP 200, 1646301 bytes (the same bytes as the first fetch of 16:55:37Z)"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "not fitted: the superseded r1 tray's material"
  - for_entry: null
    role: "TEST-PLAN E2's level: the composite wheeled vehicle schedule, 2.24 g rms in the envelope for an unknown orientation, drive limited to 3 sigma, 40 minutes an axis (the r2 record's section D)"
    path: "v2/vendor/standards/mil-std-810h-method-514-8.md"
    doc_id: "MIL-STD-810H, Method 514.8 Vibration, Annex C paragraph 2.1.3 b (2); a TRANSCRIPTION of the lines cited (pages 514.8C-11 to 514.8C-13)"
    url: "https://cvgstrategy.com/wp-content/uploads/2019/08/MIL-STD-810H-Method-514.8-Vibration.pdf (a copy of the ASSIST download of 2019-03-04)"
    fetched: "2026-09-27T21:13:01Z, curl from the runner, HTTP 200, 3564432 bytes; sha256 of the file read cc8ec677d3b06eaab5c24244f10ee8acf52dba950ab25c645deeb99c9b177650"
    sha256: "{SHA}"
    status: VERIFIED
    matches_fitted: "a test level, not a part; whether Change Notice 1 altered these lines was not checked"
"""
import hashlib
blk = y[y.index("documents_filed_w5tray:"):]
parts = blk.split("  - for_entry: null\n")
for k in range(1, len(parts)):
    path = re.search(r'path: "([^"]+)"', parts[k]).group(1)
    parts[k] = parts[k].replace("{SHA}", hashlib.sha256(open(path, "rb").read()).hexdigest())
y = y[:y.index("documents_filed_w5tray:")] + "  - for_entry: null\n".join(parts)
assert "{SHA}" not in y and y.count("  - for_entry: null\n", y.index("documents_filed_w5tray:")) == 6
wr(SY, y)

# ---------------------------------------------------------------------------------------------------------- rebind the readings
# Four records read files this script changed. Each reading's own text is unchanged (asserted below on the sections it cites), so each
# is re-read and rebound with a note naming what changed and what did not (the integration recipe: a changed bound file is re-read).
AFT = {p: rd(p) for p in BEFORE}
ams = lambda x: [c for l in x.splitlines() for c in re.split(r"(?<=[.;]) ", l) if "SMBus" in c] + [l for l in x.splitlines() if l.startswith("7. ")]
assert ams(BEFORE["v2/docs/ASSEMBLY.md"]) == ams(AFT["v2/docs/ASSEMBLY.md"]), "ASSEMBLY.md's SMBus rows or build step 7 moved"
assert section(BEFORE["v2/docs/CASE-MARGINS.md"], "\n## 3. ", "\n## 4. ") == section(AFT["v2/docs/CASE-MARGINS.md"], "\n## 3. ", "\n## 4. "), "CASE-MARGINS.md section 3 moved"
assert section(BEFORE["v2/docs/CASE-FIT-UNCERTAINTIES.md"], "\n## 2. ", "\n## 3. ") == section(AFT["v2/docs/CASE-FIT-UNCERTAINTIES.md"], "\n## 2. ", "\n## 3. "), "CASE-FIT-UNCERTAINTIES.md section 2 moved"
t = rd(P)
def rebind(t, rid, path, note):
    i, j = rec(t, rid); r = t[i:j]
    old = '"%s@%s"' % (path, SHA_BEFORE[path]); new = '"%s@%s"' % (path, sha16(path))
    assert r.count(old) == 1, (rid, old)
    r = r.replace(old, new)
    k = r.index("    evidence_bound_to:\n")
    r = r[:k] + "      - >-\n" + wrap(note % sha16(path), 10) + r[k:]
    return t[:i] + r + t[j:]
t = rebind(t, "CFL-015", "v2/docs/ASSEMBLY.md",
           "v2/docs/ASSEMBLY.md re-read at the QMX lid tray r2 draft of 27 September 2026 (set w5tray, SC-TR-01): it changes the QMX "
           "tray row, build steps 10 and 11, section 4's three QMX lead rows, the removal paragraph's first clause, the parts list and note "
           "(13); every sentence naming the pack's SMBus lead and build step 7, which this reading cites, are byte-identical, so it stands on "
           "the file at %s")
for rid in ("CON-006", "REQ-019"):
    t = rebind(t, rid, "v2/docs/CASE-MARGINS.md",
               "v2/docs/CASE-MARGINS.md re-read at the QMX lid tray r2 draft of 27 September 2026 (set w5tray, SC-TR-01): it adds the r2 "
               "note to C5, the lid plate's pull test to T8, the QMX knob tips and the buttons' read heights to T9 and the knob height to "
               "the lookups; section 3, every margin and verdict this reading rests on, is byte-identical, so it stands on the file at %s")
t = rebind(t, "FEA-007", "v2/docs/CASE-FIT-UNCERTAINTIES.md",
           "v2/docs/CASE-FIT-UNCERTAINTIES.md re-read at the QMX lid tray r2 draft of 27 September 2026 (set w5tray, SC-TR-01): it restates "
           "section 3's QMX tray row for the r2 tray (answered; its verification and the harness's face crossing open, neither moving a "
           "board); section 2's allocation and its YES rows, which this reading rests on, are byte-identical, so it stands on the file at %s")
# the header states every difference this script makes (EQ-30's lesson: a difference the header does not state reopens the baseline)
hdr_anchor = "\n#\n# PART NAMES IN STATEMENTS."
assert t.count(hdr_anchor) == 1
hdr = ("\n#\n# THE QMX LID TRAY r2 (27 September 2026, set w5tray, v2/docs/records/w5tray/drafts/apply_w5tray.py). Session choice %s "
       "(drafted as SC-TR-01)\n# records the r2 tray of v2/release/case-2026-09-27/lid-tray-qmx-r2/ and closes S-63, which moves to closed_items with its "
       "title\n# unchanged; open items %s (the lid harness's crossing of the sealed face, ENGINEERING-QUESTIONS %s) and %s (the r2 tray's "
       "verification)\n# are added; CFL-015 (ASSEMBLY.md), CON-006 and REQ-019 (CASE-MARGINS.md) and FEA-007 (CASE-FIT-UNCERTAINTIES.md) are "
       "re-read and\n# rebound with a note each, the sections their readings cite asserted byte-identical. No record's reading, statement, "
       "acceptance,\n# applicability, allocation, verification or release effect changes, and no owner ruling. This is a registry change "
       "after\n# layer 3's reviewed file: the layer 3 re-baseline (S-80, S-51, S-78) reads it with the other differences." % (SC, S_H, EQ, S_V))
t = t.replace(hdr_anchor, hdr + hdr_anchor)
wr(P, t)

# ---------------------------------------------------------------------------------------------------------- read back what was written
import yaml
reg = yaml.safe_load(rd(P)); src = yaml.safe_load(rd(SY))
def ids(node, out):
    if isinstance(node, dict):
        if "id" in node: out.append(node["id"])
        for v in node.values(): ids(v, out)
    elif isinstance(node, list):
        for v in node: ids(v, out)
    return out
got = ids(reg, [])
assert got.count(SC) == 1 and got.count(S_H) == 1 and got.count(S_V) == 1 and got.count("S-63") == 1, "an id is missing or doubled after the write"
assert len(src["documents_filed_w5tray"]) == 6 and all(len(d["sha256"]) == 64 for d in src["documents_filed_w5tray"])
for p in (EQF, A, F, M, R, B, H):
    assert "lid-tray-qmx-r2" in rd(p), p
assert EQ in rd(EQF) and "materials/" in rd(VR)

json.dump({"session_choice": SC, "drafted_as": "SC-TR-01", "open_harness": S_H, "open_verification": S_V, "question": EQ}, open(OUT_JSON, "w"), indent=1)
print("apply_w5tray: done; ids in", OUT_JSON)
