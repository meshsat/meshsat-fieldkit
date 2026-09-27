#!/usr/bin/env python3
"""Board A stream w3a (MESHSAT-1357, 27 September 2026): the requirements registry edits that go with the board A change.

r8int5 INTEGRATION COPY (27 September 2026, on main 953f5658 plus the w3t commit): the PANEL.md and EMCON.md bindings are
read from the registry and the edited files instead of 38dcd764's shas; the `source` line moves (1 and 1b) are NOT
applied, because the registry's citations are anchored at sources_read_at 08f3665a, where gen_sch_a.py equals
38dcd764's, so the anchored lines are still right; SC and S texts carry the independent checks' corrections (the
tOVLO bound, option (c) without the local clamp, U30 and U40 named, the partly seated pack).

Applied by the integrator to the tree the w3a files are merged into, AFTER drafts/w3a/apply_docs.py:
    python3 drafts/w3a/apply_docs.py <repo root>
    python3 drafts/w3a/apply_registry.py <repo root>
The order matters because apply_docs.py edits two files registry readings are bound to (v2/docs/PANEL.md and
v2/docs/feasibility/EMCON.md, step 1c): this refuses until the tree holds the edited files, so a reading is never bound
to a file the tree does not hold.

What it does, by record id with the old text asserted, in v2/ecad/tools/pcb_requirements.yaml:
  1. REBIND the seven records rules_lib.py requirements names once gen_sch_a.py and board A's netlist change
     (CON-010, CON-016, CON-018, CON-019, CFL-005, CFL-014, CFL-016): the evidence_bound_to shas move to the files the
     w3a stream wrote (asserted: the tree must hold exactly those files, or this refuses and the records are re-read by
     hand), a re-read line is added to each record's evidence naming what changed and why its reading stands, and the
     `source` line citations of gen_sch_a.py move to the new line numbers.
  1b. MOVE the gen_sch_a.py line citations in the `source` of REQ-049 and CON-014, which cite lines this change moved.
  1c. REBIND the records bound to the two documents apply_docs.py edits, each with a re-read line naming the lines that
     changed and the unchanged sections its reading rests on: v2/docs/PANEL.md (CFL-001, CFL-005, CFL-014, CFL-015,
     CFL-016; one line changes, section 7's bus-table row for 0x21 and 0x24) and v2/docs/feasibility/EMCON.md (REQ-012,
     REQ-030, REQ-032, REQ-071, CON-010, CON-021, FEA-002; section 4a's +3V3 overvoltage paragraph and section 7's row
     for it change). Added at the second pass (independent check of 27 September 2026): the first draft rebound only
     gen_sch_a.py and the netlist, so the five PASS readings on PANEL.md read as errors and the seven readings on EMCON.md
     as warnings once the documents draft was applied.
  2. ADD four session choices (the next free SC-nn in the tree it is applied to): EQ-17's decision, the PoE and USB-C
     enable dividers, the TPS25740A's EN9V, and the kinds and currents of the PWR-001 declarations.
  3. ADD six open items (the next free S-nn): what the w3a reading found and did not close.
Text edits only (the file's own formatting is kept); the result is parsed back as YAML and every id is checked unique.
Run `python3 v2/ecad/tools/rules_lib.py requirements` afterwards: on 38dcd764 with the w3a files and apply_docs.py
applied it reads 13 errors and 9 warnings before this and 0 and 0 after (main reads 0 and 0). Then re-render
v2/docs/REQUIREMENTS-TRACE.md (the normal render step), which names the new SC-nn and S-nn.
"""
import hashlib, os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
REG = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
GEN = "v2/ecad/tools/gen_sch_a.py"
NET = "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net"
OLD = {GEN: "5a97fed72c42b79d", NET: "3a786cf31614fe63"}          # main 38dcd764
NEW = {GEN: "62c9f38417412c04", NET: "c57d119d21f45fe9"}          # stream w3a's files (generator at the second pass)
PANEL = "v2/docs/PANEL.md"
EMCON = "v2/docs/feasibility/EMCON.md"
import yaml as _y
_REC = {r["id"]: r for r in _y.safe_load(open(REG, encoding="utf-8"))["records"]}
def _bound(rid, rel):
    for b in _REC[rid].get("evidence_bound_to") or []:
        if b.startswith(rel + "@"): return b.split("@")[1]
    raise SystemExit("apply_registry: %s is not bound to %s" % (rid, rel))
DOC_OLD = {PANEL: _bound("CFL-001", PANEL), EMCON: _bound("REQ-012", EMCON)}   # as the tree's registry binds them
DOC_NEW = {PANEL: hashlib.sha256(open(os.path.join(ROOT, PANEL), "rb").read()).hexdigest()[:16],
           EMCON: hashlib.sha256(open(os.path.join(ROOT, EMCON), "rb").read()).hexdigest()[:16]}
DAY = "2026-09-27"


def sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


for rel, want in NEW.items():
    have = sha16(rel)
    if have != want:
        raise SystemExit("apply_registry: %s is %s in this tree, not w3a's %s: re-read the records by hand" % (rel, have, want))
for rel, want in DOC_NEW.items():
    have = sha16(rel)
    if have == DOC_OLD[rel]:
        raise SystemExit("apply_registry: %s is still main's %s: run drafts/w3a/apply_docs.py first (it edits this file, "
                         "and the readings bound to it are rebound to the edited file here)" % (rel, have))

txt = open(REG, encoding="utf-8").read()
orig = txt

CHANGE = (
    "v2/ecad/tools/gen_sch_a.py and v2/ecad/pcb-a-power-a23/out/pcb-a-power.net re-read at board A's stream w3a of 27 "
    "September 2026, integrated in fnd/r8int5 on main 953f5658, where both files equal 38dcd764's (read against 38dcd764; the netlist regenerated on the KiCad box with main's chain, main's own "
    "regeneration equal to main's committed netlist but for its header, and compared component by component and net by "
    "net, pin, pinfunction and pintype, with an independent reader): it differs from 3a786cf31614fe63 only in U39 "
    "(TPS259631DDAR), U40 (SN74LVC2G07DBVR), R209 to R215 and C224 to C226 added; U35 to U38 pin 5 and C215 to C218 "
    "moved from +3V3 to +3V3_EMCON, behind U39 and R213 (EQ-17); U36 pin 2 and U38 pin 2 moved to PA_HOLD and HF_HOLD, "
    "PA_SW_EN and HF_SW_EN now read by U40; U16 pin 1, R74 and R75 moved from POE_EN to POE_UVLO and U19 pin 1, R133 and "
    "R134 from PD_EN to PD_UVLO, with R74 and R133 now 10 k 1% and R75 and R134 15 k 1%; U18 pin 8 (EN9V) moved from "
    "PD_DVDD to GND; U28 pin 15 and TP3 moved from EXP2_SP3 to EMCON_EF_FLT; and U36's, U38's and TP3's value text. The "
    "generator's inserted lines move every later line. At the second pass three comment lines of the generator's "
    "TPS25740A supply block were reworded (a semicolon before V(VTX), V(VAUX) and V(DVDD) became a comma, because "
    "test_swallowed_calls refuses a comment token that reads like a call after a semicolon); no call and no line number "
    "moved, and the schematic chain re-run on the KiCad box wrote the same schematic byte for byte and the same netlist "
    "but for its header's source path and date")

REBIND = {
    "CON-019": dict(
        why=("The interlock is unchanged: U30 still gives OUTLET_OK = NOT (TR_APRS AND PA_EN) and U26's sections 3 and 4 "
             "still give POE_EN and PD_EN, which now reach U16's and U19's EN/UVLO through 10 k over 15 k (EN at 0.6 of the "
             "gate output: 1.8 V or more high against VEN(OP)'s 1.29 V maximum and 0.16 V low against VEN(STBY)'s 0.55 V "
             "minimum, SNVSAI1D 6.5), so the outlets still drop with no processor in the path; PA_EN is still U36's output, "
             "TX_INHIBIT_n AND EMCON_HW AND the software hold, the hold now re-driven by U40. The lines this reading cites are "
             "now v2/ecad/tools/gen_sch_a.py:1291-1304 (S-14's comment), 1352-1353 (U26) and 1431 (U30)"),
        source=('"v2/ecad/tools/gen_sch_a.py:1177-1190, 1237-1245"', '"v2/ecad/tools/gen_sch_a.py:1291-1304, 1352-1353, 1431"')),
    "CON-018": dict(
        why=("U31 and its lines are unchanged (now v2/ecad/tools/gen_sch_a.py:1200-1210), and PD_CC1 and PD_CC2 are now "
             "declared in the intent as nodes at 5.5 V (SLVSDG8B 7.3), which settles them for PWR-001; port_protect on the new "
             "netlist reads PASS of 26 with 0 answered in part"),
        source=('"v2/ecad/tools/gen_sch_a.py:1104-1114"', '"v2/ecad/tools/gen_sch_a.py:1200-1210"')),
    "CFL-005": dict(
        why=("R102 (10 k 1% on EMCON_HW), R145 on TX_INHIBIT_n and the slot enable pull-downs are unchanged on the same "
             "nets (R102 now at v2/ecad/tools/gen_sch_a.py:1439), so the panel-absent state PANEL.md section 7 describes "
             "is the one generated"),
        source=('"v2/ecad/tools/gen_sch_a.py:1253"', '"v2/ecad/tools/gen_sch_a.py:1439"')),
    "CON-010": dict(
        why=("board A's PA_EN is U36's output, PA_TXOK AND PA_HOLD, with PA_TXOK = TX_INHIBIT_n AND EMCON_HW (U35) and "
             "PA_HOLD the software hold PA_SW_EN through U40's open drain, the same logic on a protected supply; the "
             "reading's result does not move: RF-002's walk (tools/tx_inhibit.py on the six committed netlists, board A's "
             "old and new) prints the same verdict lines before and after, UNDECIDED on A's PA and HF rows for the reasons "
             "named there (the INA226 and CSD18510Q5B rows, EQ-18's U14 on board C), and the SA868 row stays open on D"),
        source=None),
    "CFL-016": dict(
        why=("the published contracts' board A rows are unchanged in logic: the PA and HF rails are still gated by U35 to "
             "U38 on both EMCON lines, now on their own supply behind U39 (EQ-17), which no cited section describes; the "
             "PoE and USB-C enables and the outlet interlock are unchanged in function; so the reading stands"),
        source=None),
    "CFL-014": dict(
        why=("the charger strap R26/R27, R17 and F1 are unchanged on the same nets (now v2/ecad/tools/gen_sch_a.py:859-865; "
             "the VBAT declaration at lines 47-48 names one more load, U21, the monitor's eFuse, at 0.69 A)"),
        source=('"v2/ecad/tools/gen_sch_a.py:839-845"', '"v2/ecad/tools/gen_sch_a.py:859-865"')),
    "CON-016": dict(
        why=("board A's clamps D1 to D4 are unchanged on the same nets; port_protect on the new netlist reads 5 clamps, 0 "
             "reversed, 0 drawn with a mismatched symbol (PASS of 26)"),
        source=None),
}


def block(t, rid):
    """(start, end) of the record `  - id: <rid>` up to the next item at the same indent or the next top-level key."""
    m = re.search(r"^  - id: %s\n" % re.escape(rid), t, re.M)
    if not m: raise SystemExit("apply_registry: no record %s" % rid)
    n = re.search(r"^(  - id: |\S)", t[m.end():], re.M)
    return m.start(), (m.end() + n.start()) if n else len(t)


def wrap(text, indent="          ", width=118):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(indent) + len(cur) + 1 + len(w) > width: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    if cur: lines.append(cur)
    return "\n".join(indent + l for l in lines)


for rid, spec in REBIND.items():
    s, e = block(txt, rid)
    b = txt[s:e]
    nb = b
    for rel in (GEN, NET):
        old = '"%s@%s"' % (rel, OLD[rel])
        if old in nb: nb = nb.replace(old, '"%s@%s"' % (rel, NEW[rel]))
    if nb == b: raise SystemExit("apply_registry: %s carries neither old binding" % rid)
    if "\n    evidence_bound_to:\n" not in nb: raise SystemExit("apply_registry: %s has no evidence_bound_to list" % rid)
    bound = [rel for rel in (GEN, NET) if '"%s@%s"' % (rel, NEW[rel]) in nb]
    item = "      - >-\n" + wrap("%s. %s; the reading stands on %s." % (
        CHANGE, spec["why"], " and ".join("the file at %s" % NEW[r] for r in bound))) + "\n"
    nb = nb.replace("\n    evidence_bound_to:\n", "\n" + item.rstrip("\n") + "\n    evidence_bound_to:\n", 1)
    if spec["source"] and False:   # r8int5: anchored at sources_read_at 08f3665a, not moved
        o, n = spec["source"]
        if nb.count(o) != 1: raise SystemExit("apply_registry: %s: source text %s not found once" % (rid, o))
        nb = nb.replace(o, n)
    txt = txt[:s] + nb + txt[e:]

# ---- 1b. source pointers of records not bound to gen_sch_a.py by sha, whose cited lines moved (the lines are unchanged)
SOURCE_ONLY = {
    "REQ-049": [('"v2/ecad/tools/gen_sch_a.py:1293-1309"', '"v2/ecad/tools/gen_sch_a.py:1479-1495"')],   # D-12's wall data path
    "CON-014": [('"v2/ecad/tools/gen_sch_a.py:965"', '"v2/ecad/tools/gen_sch_a.py:997"'),              # R42 on DEV_EN
                ('"v2/ecad/tools/gen_sch_a.py:1253"', '"v2/ecad/tools/gen_sch_a.py:1439"')],            # R102 on EMCON_HW
}
for rid, pairs in ({} if True else SOURCE_ONLY).items():   # r8int5: not moved (anchored citations)
    s0, e0 = block(txt, rid)
    b0 = txt[s0:e0]
    for o, n in pairs:
        if b0.count(o) != 1: raise SystemExit("apply_registry: %s: source text %s not found once" % (rid, o))
        b0 = b0.replace(o, n)
    txt = txt[:s0] + b0 + txt[e0:]

# ---- 1c. the readings bound to the two documents drafts/w3a/apply_docs.py edits (second pass, 27 September 2026)
DOC_CHANGE = {
    PANEL: ("v2/docs/PANEL.md re-read at the r8int5 integration of board A's stream w3a (27 September 2026) with its "
            "document edits applied (read against the file at %s): one line changes, section 7's bus-table row for 0x21 and "
            "0x24, where U28's description gains the EMCON gates' supply fault EMCON_EF_FLT on P1.2, low when U39 has cut "
            "that supply on a +3V3 overvoltage (U28 pin 15, IO1_2, which board A's w3a netlist moves from EXP2_SP3 to "
            "EMCON_EF_FLT with TP3); every other line of the file is byte-identical" % DOC_OLD[PANEL]),
    EMCON: ("v2/docs/feasibility/EMCON.md re-read at the r8int5 integration of board A's stream w3a (27 September 2026) "
            "with its document edits applied (read against the file at %s): four places change, all about board A's +3V3 "
            "overvoltage (EQ-17): section 4a's paragraph 'A fault outside RF-002's named states: +3V3 overvoltage' now "
            "reads CLOSED AT DESK (local) with a bound, the four SN74AUP1G08 gates U35 to U38 on +3V3_EMCON behind the eFuse "
            "U39 (overvoltage lockout at 3.83 to 4.11 V of +3V3) with the software holds through U40's open drains, the "
            "gates kept under 4.6 V while D3 holds +3V3 at 9.2 V or less unless U39's tOVLO exceeds about 9.5 us, and the "
            "rest of +3V3 against D3 (U30 on PA_EN, U40) left as a registry open item; section 6's E-11 row gains that "
            "+3V3 injection on board A with its pass line; section 7's row for that fault reads closed at desk with the "
            "bound; section 8's board A bullet says so; every other line is byte-identical, among them sections 0 and 0a "
            "(its rows and counts), 1 to 4 with 4.1 to 4.18, the rest of 4a, 4b, 5, 5a, every other row of 6 and 7, the "
            "rest of 8, and 9 to 9d" % DOC_OLD[EMCON]),
}
DOC_REREAD = {
    "CFL-001": [(PANEL, "PASS", "line 5 (bank 1's home and failover hosts), section 1 and section 2's ribbon table with its "
                                "pin 15 row, which this reading rests on, are byte-identical")],
    "CFL-005": [(PANEL, "PASS", "section 7's panel-absent paragraph (R102 and R58 on EMCON_HW, R145, R59 and R2 on "
                                "TX_INHIBIT_n, R117, R118, the slot enables pulled low on A22), which this reading cites, "
                                "is a separate paragraph from the bus table and is byte-identical")],
    "CFL-014": [(PANEL, "PASS", "section 10, which this reading cites, is byte-identical")],
    "CFL-015": [(PANEL, "PASS", "section 10's SMBus sentences, which this reading cites, are byte-identical")],
    "CFL-016": [(PANEL, "PASS", "the changed row is in section 7's bus table, which this record's acceptance asks to "
                                "describe the circuit as generated, and it now names U28 P1.2 as EMCON_EF_FLT, which is "
                                "what board A's w3a netlist carries, where 'spares' no longer was; sections 1 and 6 are "
                                "byte-identical")],
    "REQ-012": [(EMCON, "FAIL", "section 0's TX-lamp sentence and bench E-02, on which this reading rests, are "
                                "byte-identical and no part of the lamp's path moved")],
    "REQ-030": [(EMCON, "FAIL", "what the FAIL rests on is unchanged: the RockBLOCK's local chain (its own supercapacitors, "
                                "ENABLE held by U6), the SA868's missing receive threshold and RF-002's reading of board B; "
                                "the PA and HF stages now also shut down on a +3V3 overvoltage, which none of those "
                                "depends on")],
    "REQ-032": [(EMCON, "FAIL", "sections 4.4, 4.5 and 4b and L3 and L4, on which this reading rests, are byte-identical")],
    "REQ-071": [(EMCON, "FAIL", "section 5a (every time term and fault condition) and section 0a's end-to-end column, which "
                                "closes no row, are byte-identical, so no row meets the requirement at desk")],
    "CON-010": [(EMCON, "INCONCLUSIVE", "sections 4.1 and 4.2, which this reading cites, are byte-identical")],
    "CON-021": [(EMCON, "FAIL", "section 7's common-element row (board C's lamp D22, U14 and Q7, its plate light guide "
                                "still owed), which this reading cites, is byte-identical")],
    "FEA-002": [(EMCON, "INCONCLUSIVE", "section 7 changes only in the +3V3 overvoltage row, which is not among the items "
                                        "this reading names as remaining (the RockBLOCK's ENABLE, the SA868's threshold, "
                                        "L4 on U501 to U505, the back-feed into the RockBLOCK, E22 and E72, the plate's "
                                        "light guide, RF-002's model gap on board B and every bench test), and each of "
                                        "those rows is byte-identical; bench E-11 gains a board A step and closes none")],
}
for rid, items in DOC_REREAD.items():
    s1, e1 = block(txt, rid)
    b1 = txt[s1:e1]
    nb1 = b1
    for rel, res, why in items:
        old = '"%s@%s"' % (rel, DOC_OLD[rel])
        if nb1.count(old) != 1: raise SystemExit("apply_registry: %s does not carry %s once" % (rid, old))
        nb1 = nb1.replace(old, '"%s@%s"' % (rel, DOC_NEW[rel]))
        if "\n    evidence_result: %s\n" % res not in nb1:
            raise SystemExit("apply_registry: %s no longer reads %s: re-read it by hand" % (rid, res))
        item = "      - >-\n" + wrap("%s; %s, so it stands %s on the file at %s." % (DOC_CHANGE[rel], why, res, DOC_NEW[rel]))
        nb1 = nb1.replace("\n    evidence_bound_to:\n", "\n" + item + "\n    evidence_bound_to:\n", 1)
    assert nb1 != b1
    txt = txt[:s1] + nb1 + txt[e1:]

# ---- 2. session choices and 3. open items, numbered in the tree this is applied to
sc_n = max(int(x) for x in re.findall(r"^  - id: SC-(\d+)$", txt, re.M)) + 1
s_n = max(int(x) for x in re.findall(r"^  - id: S-(\d+)$", txt, re.M)) + 1

CHOICES = [
    dict(q="How do board A's EMCON gates survive a +3V3 overvoltage between the SN74AUP1G08's 4.6 V absolute maximum "
           "and D3's 6.40 V breakdown (EQ-17)?",
         taken="Option (c) without the local clamp EQ-17 names, a series element and nothing of the +3V3 domain on the "
               "gates' pins, the eFuse's lockout and a filter bounding their supply instead: U35 to U38 run from "
               "+3V3_EMCON behind a TPS259631DDAR eFuse (U39) whose overvoltage lockout opens at 3.83 to 4.11 V of +3V3 "
               "(R211 23.2 k over R212 10 k, 1 percent), with EN on RAIL_EN, and a 100 Ohm filter (R213) into the gates' "
               "own 100 nF; an SN74LVC2G07 open-drain buffer (U40, rated 6.5 V) re-drives the software holds PA_SW_EN and "
               "HF_SW_EN into PA_HOLD and HF_HOLD, pulled up to the protected rail. U39's fault line goes to U28 P1.2 "
               "(EMCON_EF_FLT) with TP3.",
         why="The fault current is U12's 4.2 to 5.8 A high-side limit (SLUSEA4D 8.5), so no clamp in this tree holds "
             "under 4.6 V at it (option a), and the SN74LVC1G08 of option (b) is rated 6.5 V, still inside D3's 6.40 to "
             "7.00 V, with the II and Ioff that round 8's hold on TX_INHIBIT_n refused. The eFuse part is already "
             "used four times in board A's design (U21 to U23 and U32, order code C2155778, TI SLVSET8A); it cuts the gates' supply for any +3V3 above "
             "4.11 V, the gates' outputs fall with it and PA_UVLO and HF_UVLO go under VEN(STBY), so the PA and HF "
             "stages shut down for the duration: the EMCON-safe state. What the gates see during the cut is bounded by "
             "U39's tOVLO, which TI states only as 1.3 us typical: with D3 holding +3V3 at 9.2 V or less the 100 Ohm "
             "filter keeps them under 4.6 V unless tOVLO exceeds about 9.5 us (bench E-11's +3V3 injection checks it). The open-drain buffer keeps the +3V3 domain off "
             "the gates' inputs, which a supply cut alone did not. Reverse by putting U35 to U38 back on +3V3 with their "
             "B inputs on PA_SW_EN and HF_SW_EN and removing U39, U40, R209 to R215 and C224 to C226.",
         source=["v2/ecad/tools/gen_sch_a.py (EQ-17, TAKEN, above U39)", "v2/vendor/power/tps2596.pdf (SLVSET8A)",
                 "v2/vendor/ti/ti-sn74lvc2g07.pdf (SCES308L)", "v2/vendor/ti/ti-sn74aup1g08.pdf (SCES502Q)",
                 "v2/docs/handover/ENGINEERING-QUESTIONS.md (EQ-17)", "v2/docs/feasibility/EMCON.md sections 4a and 7"]),
    dict(q="What divider do the PoE and USB-C stages' EN/UVLO pins take, now that R74 and R133 had both pins on one net?",
         taken="Round 8's PA and HF divider: 10 k over 15 k, 1 percent (R74/R75, R133/R134), EN/UVLO on its own node "
               "POE_UVLO and PD_UVLO at 0.6 of the interlock gate's output; the lm5176 helper now refuses a stage with an "
               "EN divider that names no node.",
         why="Read on main 38dcd764's netlist: R74 on POE_EN and R133 on PD_EN at both pins, so U16's and U19's EN/UVLO "
             "sat on U26's outputs with a 10 k to ground and a dead 62 k. At 0.6 the enables still work (1.8 V or more "
             "high against VEN(OP)'s 1.29 V maximum, 0.16 V low against VEN(STBY)'s 0.55 V minimum, SNVSAI1D 6.5; the "
             "LVC08A's VOH and VOL at 100 uA, SCAS283W 5.7), and an LVC08A below its 1.65 V specified supply cannot "
             "start either stage (EN needs 1.88 V at the gate output). Reverse by en_node=None on the two calls (the "
             "helper's refusal must then be lifted).",
         source=["v2/ecad/tools/gen_sch_a.py (the PoE stage's call)", "v2/vendor/ti/lm5176-datasheet.pdf (SNVSAI1D)",
                 "v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf (SCAS283W)"]),
    dict(q="Does the TPS25740A's EN9V stay tied to DVDD, which removes the outlet's 9 V profile?",
         taken="No: U18 pin 8 (EN9V) is tied to GND, so the outlet advertises 5, 9 and 15 V as its header, its 9 V "
               "feedback leg R136 and PD_VPWR's declaration state.",
         why="SLVSDG8B's pin table (p.4): 'If it is pulled low, then the 9 V PDO may be transmitted. If it is not pulled "
             "low, the 9-V PDO will not be advertised'; EN9V's VIH is 1.4 V (7.3) and DVDD is 1.75 to 1.95 V (7.5), and "
             "Table 2 (p.28) gives High with HIPWR direct to DVDD as '5, 15'. Found while declaring PD_DVDD for PWR-001; "
             "it restores a function the design states and adds no part. Reverse by putting pin 8 back on PD_DVDD.",
         source=["v2/ecad/tools/gen_sch_a.py (EN9V IS TIED LOW)", "v2/vendor/ti/ti-tps25740.pdf (SLVSDG8B)"]),
    dict(q="How are the supplies PWR-001 named on board A declared, and with what currents?",
         taken="As nodes where a net carries one part's own supply with its capacitor (B33_BST and HT_BST riding on "
               "their SW at the TPS62933's 5.5 V BST-SW maximum; S1_BOOT and S3_BOOT at the AP64500's VSW + 6.0 V; PD_VTX "
               "1.2 V, PD_VAUX 4.1 V and PD_DVDD 2.0 V from SLVSDG8B 7.5; PD_CC1 and PD_CC2 5.5 V as signal lines); as rails "
               "where current passes to a load: VMON 0.69 A typical and 1.0 A peak (the Xenarc 709GNK's 10 W at 14.4 V and "
               "at its 10 V floor), PRECHG 0 A continuous and 1.68 A peak (the pack's 16.8 V over R1's 10 Ohm into a "
               "discharged CELL+, always on), and the EMCON gates' +3V3_EMCON_EF and +3V3_EMCON at 0.4 mA typical and "
               "2 mA peak. boards/a.json's signal table no longer calls VMON a monitor divider tap.",
         why="PWR-001 asks every power net to be a declared rail or a node supplying one part; each number is the maker's "
             "(the monitor's manual gives only a maximum power, so the typical is that maximum at the nominal pack). PWR-001 "
             "on A reads PASS of 35 after it, FAIL before. Reverse by removing the declarations, which reopens the FAIL.",
         source=["v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/boards/a.json (signal_classes: VMON)",
                 "v2/vendor/xenarc/xenarc-709gnk-product-manual-v2.pdf", "v2/vendor/ti/ti-tps62933.pdf (SLUSEA4D)",
                 "v2/vendor/diodes/diodes-ap64500.pdf (DS41979)", "v2/vendor/ti/ti-tps25740.pdf (SLVSDG8B)"]),
]

OPEN = [
    "Board A's +3V3 clamp D3 (SMBJ5.0A: VBR 6.40 to 7.00 V at 10 mA, 9.2 V at IPP, MDD SMBJ series) sits above the "
    "absolute maximum of the rest of the rail: U27 and U28 (PCA9555, 6.0 V, SCPS131J), the six INA226 (6.0 V, SBOS547C), "
    "U26, U30 and U40 (6.5 V). A +3V3 fault between 6.0 V and D3's clamp at the fault current (U12's 4.2 to 5.8 A) can "
    "damage them. Since EQ-17 the gates' supply is cut at 4.11 V or less, but two of these parts still reach EMCON: "
    "U30 (SN74LVC1G00 on +3V3) has an input on PA_EN itself, and U40's outputs are the software-hold inputs of U36 "
    "and U38, so a part damaged between 6.5 V and D3's clamp leaves those nets in an unstated state (the "
    "TX_INHIBIT_n AND EMCON_HW path through U35 and U37 is unaffected unless U40 fails shorted to its supply); open "
    "until the rail's "
    "protection is decided with the fault current bound (a clamp that holds at that current, a crowbar with the "
    "TPS62933's hiccup, or the fault accepted with its bound).",
    "R1, the pre-charge resistor (10 Ohm, 2 W, 2512) on PRECHG, takes the whole energy of charging CELL+'s capacitance "
    "from the pack, C V^2 / 2 at 16.8 V, in one pulse of about 10 Ohm x C: its single-pulse rating from its maker's "
    "sheet (none is held for the part fitted) against that energy is not checked, nor the partly seated pack (the "
    "pre-charge pin mated, the main pins not), where R1 carries the load. PRECHG is declared at 1.68 A peak.",
    "Board A's switching nodes fed from VBAT (B33_SW, S1_SW, S3_SW and the LM5176 stages' SW1 and BOOT1) are declared at "
    "VBAT's 14.4 V nominal (intent.net_volts reads `volts`), not its 16.8 V working maximum (`v_work`), and the new "
    "bootstrap nodes B33_BST, HT_BST, S1_BOOT and S3_BOOT follow them; no rated part's verdict moves today (the parts "
    "across them are judged at their bias, the rest carry no rating), but the declared peak understates the node.",
    "Board A's project netclass patterns PA_SW* and HF_SW* (class SW, the switch nodes) also catch the static enables "
    "PA_SW_EN and HF_SW_EN, so they take the switch-node class at layout; the new PA_HOLD and HF_HOLD are named out of "
    "it. A layout-stage item for the pattern list.",
    "power_path on board A reads VBAT declared at 10 A typical and 18 A peak against its eleven converters' input draw "
    "of 16.53 and 24.51 A (SHORT); 15.84 and 23.51 A on main before w3a, the monitor's eFuse U21 (0.69 / 1.0 A) now "
    "named. VBAT's declared currents against its loads are open.",
    "Firmware obligation from EQ-17: U28 (0x24) P1.2 is EMCON_EF_FLT, low when U39 has cut the EMCON gates' supply "
    "(+3V3 over 3.83 to 4.11 V, or U39's thermal shutdown); the panel firmware reads it, logs a +3V3 overvoltage and "
    "treats the PA and HF rails as unavailable while it is low. PANEL.md's bus table and the firmware contract carry it.",
]


def choice_text(n, c):
    out = ["  - id: SC-%02d" % n, "    authority: SESSION", "    under: standing-rule", '    taken_on: "%s"' % DAY,
           '    question: "%s"' % c["q"].replace('"', "'"), "    taken: >-", wrap(c["taken"], "      "),
           "    why: >-", wrap(c["why"], "      "), "    source:"]
    out += ['      - "%s"' % s.replace('"', "'") for s in c["source"]]
    return "\n".join(out) + "\n"


def open_text(n, t):
    return "\n".join(["  - id: S-%02d" % n, "    class: SESSION", "    status: OPEN", "    title: >-",
                      wrap(t, "      ")]) + "\n"


anchor = "\n# What is still open. SESSION items"
if txt.count(anchor) != 1: raise SystemExit("apply_registry: the session_choices section's end is not where it was")
new_sc = "".join(choice_text(sc_n + i, c) for i, c in enumerate(CHOICES))
txt = txt.replace(anchor, new_sc.rstrip("\n") + "\n" + anchor, 1)

anchor2 = "\n# Items that left the open list"
if txt.count(anchor2) != 1: raise SystemExit("apply_registry: the open_items section's end is not where it was")
new_s = "".join(open_text(s_n + i, t) for i, t in enumerate(OPEN))
txt = txt.replace(anchor2, new_s.rstrip("\n") + "\n" + anchor2, 1)

assert txt != orig
import yaml
d = yaml.safe_load(txt)
ids = [r["id"] for sec in ("session_choices", "open_items", "closed_items", "records") for r in (d.get(sec) or [])]
dup = sorted({i for i in ids if ids.count(i) > 1})
if dup: raise SystemExit("apply_registry: duplicate ids %s" % dup)
for rid in REBIND:
    r = [x for x in d["records"] if x["id"] == rid][0]
    for rel in (GEN, NET):
        assert "%s@%s" % (rel, OLD[rel]) not in r.get("evidence_bound_to", []), (rid, rel)
for rid, items in DOC_REREAD.items():
    r = [x for x in d["records"] if x["id"] == rid][0]
    for rel, _res, _why in items:
        assert "%s@%s" % (rel, DOC_NEW[rel]) in r.get("evidence_bound_to", []), (rid, rel)
        assert "%s@%s" % (rel, DOC_OLD[rel]) not in r.get("evidence_bound_to", []), (rid, rel)
left = [x["id"] for x in d["records"] for b in (x.get("evidence_bound_to") or [])
        if b in ("%s@%s" % (k, v) for k, v in list(OLD.items()) + list(DOC_OLD.items()))]
if left: raise SystemExit("apply_registry: still bound to a file w3a changed: %s" % sorted(set(left)))
open(REG, "w", encoding="utf-8").write(txt)
print("apply_registry (r8int5): rebound %s on gen_sch_a.py and the netlist; %s on PANEL.md or EMCON.md; source lines moved on %s; "
      "session choices SC-%02d to SC-%02d; open items S-%02d to S-%02d"
      % (", ".join(REBIND), ", ".join(DOC_REREAD), ", ".join(SOURCE_ONLY), sc_n, sc_n + len(CHOICES) - 1, s_n,
         s_n + len(OPEN) - 1))
