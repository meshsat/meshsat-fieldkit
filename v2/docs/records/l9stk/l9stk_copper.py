#!/usr/bin/env python3
"""Layer 9 item 9.12, record l9stk, the copper question (MESHSAT-1357; revision of 4 October 2026 after the independent check
COPPER: NOT CONFIRMED): the pack path's copper on boards A and E, sized on its actual basis. A candidate copper-sizing result,
not completed fault-protection verification.

Round 3 (4 October 2026, the integration of set 29): L4-E11's round 9 drafts a third battery FET, Q42, beside Q39 and Q40 and
restates E11-29 as section 15.5's junction limit. The draft is now PARSED (the designators and their count are read from the
nfet calls it writes on the battery nets, not from a quoted sentence, which refused the moment the sentence said three), the coordination
table's battery FET rows are judged on the circuit as drafted, and section 9a prints each of those rows on the pair it was
first judged on beside its reading now, both derived from the pinned files.

Desk arithmetic on committed files. Nothing here was built, routed, measured or bought. It reads its inputs, every one pinned
by sha256 in section 0, and prints:

  1. the currents each conductor carries, by class: the continuous load, the transient demand with its duration, and the
     fault current with the time its protection takes to clear it, where an assured time exists at all;
  2. the method: decision 35's model (track_current.conservative, outer copper at the external factor) applied to the two
     outer faces of a band AS ONE CONDUCTOR of their combined section (they share one footprint and its cooling), and to a
     band and its adjacent return AS ONE CONDUCTOR of their combined section carrying their combined dissipation; an uneven
     split between the faces enters as its extra dissipation; Onderdonk's adiabatic bound (records/l7pwr/inputs) for the
     temperature reached before a timed clearance, the smaller of it and the steady rise; the limit of each band the lowest
     printed limit of the parts it joins, from the worst inside air the tree holds;
  3. the split between the faces (resistance and transfer barrels) and the barrels' two annulus conventions;
  4. the widths per conductor at 1 oz and 2 oz, each class on them with every failing row, and the widths quoted judged;
  5. the series parts and lands; board E's cross-section; the owner's coordination table, one row per case with its
     protective device, its assured clearing time or "none assured", every component's reading and the limiting one; the
     battery FETs' rows as they were on the pair (section 9a);
  6. the predicates test_l9stk.py holds.

Run from the repository root: python3 v2/docs/records/l9stk/l9stk_copper.py
The committed output is regenerated only through _bin/regen_out.py. Stdlib, PyYAML, pdftotext (poppler) and the tool modules;
no KiCad, no network, no date, no host name, so a second run prints the same bytes.
"""
import ast
import hashlib
import importlib.util
import math
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.path.insert(0, TOOLS)
sys.dont_write_bytecode = True
import track_current as tc  # noqa: E402
import via_current as vc    # noqa: E402
import stackup_write as sw  # noqa: E402

# W34 (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its pdftotext options ([] is pdftotext's
# plain reading order). Each text is a verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its
# PDF (a held-back sheet's text is held back with it, under held/); _lib/pdftext.py returns it byte for byte and refuses when it is
# absent, so this script never runs pdftotext; section 0 prints each text's sha256 among the pins (keys pdftext NN).
# Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l9stk
PDFTEXT = {
    "v2/vendor/battery/amass-xt60-spec-tme.pdf": [["-layout"]],
    "v2/vendor/connectors/jst-vh-catalogue.pdf": [["-layout"]],
    "v2/vendor/keystone/littelfuse-297-ficcorp.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PT)
PINS = {
    "track_current": "v2/ecad/tools/track_current.py",
    "via_current": "v2/ecad/tools/via_current.py",
    "stackup_write": "v2/ecad/tools/stackup_write.py",
    "dc_drop": "v2/ecad/tools/dc_drop.py",
    "stackups": "v2/docs/records/l9stk/l9stk_stackups.py",
    "ecss_70_12c": "v2/vendor/standards/ecss-q-st-70-12c-2014-07-14.md",
    "decisions": "v2/ecad/tools/pcb_decisions.yaml",
    "chain": "v2/ecad/tools/pcb_energy_chain.yaml",
    "pack_protection": "v2/ecad/tools/pcb_pack_protection.yaml",
    "gauge_image": "v2/docs/review-packets/battery/PRIMARY-CONFIGURATION.md",
    "mini_297": "v2/vendor/keystone/littelfuse-297-ficcorp.pdf",
    "xt60": "v2/vendor/battery/amass-xt60-spec-tme.pdf",
    "vh": "v2/vendor/connectors/jst-vh-catalogue.pdf",
    "sources": "v2/vendor/SOURCES.yaml",
    "l4e11_out": "v2/docs/records/l4e11/l4e11_power.out",
    "l4e12_out": "v2/docs/records/l4e12/l4e12_thermal.out",
    "l9pwr_out": "v2/docs/records/l8r2/inputs/l9pwr_budget-38ef774c.txt",
    "power_thermal": "v2/docs/feasibility/POWER-THERMAL.md",
    "fusing": "v2/docs/records/l7pwr/inputs/fusing-current-sources-2026-10-03.md",
    "lcsc_fill": "v2/ecad/tools/lcsc_fill.py",
    "gen_sch_a": "v2/ecad/tools/gen_sch_a.py",
    "gen_sch_e": "v2/ecad/tools/gen_sch_e.py",
    "charger_draft": "v2/docs/records/l4e11/apply_gen_sch_a_charger.py",
    "board_a": "v2/ecad/pcb-a-power-a23/pcb-a-power.kicad_pcb",
    "board_e": "v2/ecad/pcb-e1-dock-e7/pcb-e1-dock.kicad_pcb",
}
S_MAX = 0.55            # SESSION: the most either outer face may carry where a one-face part ends a band (section 3)
LENGTHS = (5.0, 10.0, 20.0, 40.0, 80.0)   # band lengths the transfer field is tabled at; the layout sets the real one
OZ1, OZ2 = 1.0, 2.0


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def refuse(msg):
    sys.stderr.write("l9stk_copper: REFUSED: %s\n" % msg)
    sys.exit(2)


def text(key):
    return open(rel(PINS[key]), encoding="utf-8").read()


def need(t, pat, what, flags=re.M | re.S):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def pdf(key):
    return PT.pdf_text(ROOT, PINS[key], ["-layout"], PDFTEXT, "v2/docs/records/l9stk")


BAT_NETS = ("CH_BATDRV", "CH_BATQ", "VBAT")     # nfet's gate, drain and source for a battery FET (TI's Figure 9-1: BATDRV, toward RSR, VSYS)


def nfet_calls(draft):
    """Every nfet(ref, part, gate, drain, source, ...) a draft would write into a generator, PARSED: the draft is read as text
    and parsed with ast (a draft is never run); each of its string constants that mentions nfet is parsed again as generator
    source (whole, or line by line where a constant is a fragment); a `for` over a literal tuple is unrolled with its names
    bound, so the loop's variable names and the part's sentence decide nothing. Returns (ref, part, gate, drain, source) per
    call whose five arguments are literals once the loop is bound."""
    found = []

    def walk(stmts, env):
        for st in stmts:
            if isinstance(st, ast.For):
                try:
                    vals = ast.literal_eval(st.iter)
                except (ValueError, SyntaxError):
                    continue
                for v in vals:
                    e2 = dict(env)
                    if isinstance(st.target, ast.Name):
                        e2[st.target.id] = v
                    elif isinstance(st.target, ast.Tuple) and isinstance(v, tuple) and len(v) == len(st.target.elts):
                        e2.update({e.id: x for e, x in zip(st.target.elts, v) if isinstance(e, ast.Name)})
                    walk(st.body, e2)
            elif isinstance(st, ast.Expr) and isinstance(st.value, ast.Call) and isinstance(st.value.func, ast.Name) \
                    and st.value.func.id == "nfet" and len(st.value.args) >= 5:
                try:
                    args = tuple(eval(compile(ast.Expression(x), "<nfet>", "eval"), {"__builtins__": {}}, dict(env)) for x in st.value.args[:5])
                except Exception:
                    continue
                if all(isinstance(x, str) for x in args):
                    found.append(args)
    for node in ast.walk(ast.parse(draft)):
        if not (isinstance(node, ast.Constant) and isinstance(node.value, str) and "nfet(" in node.value):
            continue
        try:
            body = ast.parse(node.value).body
        except SyntaxError:
            body = []
            for line in node.value.splitlines():
                try:
                    body += ast.parse(line.strip()).body
                except SyntaxError:
                    continue
        walk(body, {})
    return found


def battery_fets(draft):
    """The charger's battery FETs as L4-E11's draft writes them into board A's generator: the nfet calls whose gate is
    CH_BATDRV, drain CH_BATQ and source VBAT. Returns the designators in the draft's order and the part's text; refuses on
    fewer than two, on a designator written twice, on two different parts, or on a part that is not the BUK6Y10-30PX."""
    fets = [(c[0], c[1]) for c in nfet_calls(draft) if c[2:5] == BAT_NETS]
    refs, parts = tuple(r for r, _p in fets), sorted({p for _r, p in fets})
    if len(refs) < 2:
        refuse("the charger draft writes %d battery FET(s) on %s; two or more are read" % (len(refs), ", ".join(BAT_NETS)))
    if len(set(refs)) != len(refs):
        refuse("the charger draft writes a battery FET twice (%s)" % ", ".join(refs))
    if len(parts) != 1 or "BUK6Y10-30PX" not in parts[0]:
        refuse("the charger draft's battery FETs did not read as one part, the BUK6Y10-30PX")
    return refs, parts[0]


def stackups_module():
    sp = importlib.util.spec_from_file_location("l9stk_stackups_for_copper", rel(PINS["stackups"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ 1. the inputs, read
def read_inputs():
    I = {}
    # the energy chain: the stages this record's conductors sit in
    ch = yaml.safe_load(text("chain"))
    st = {s["id"]: s for s in ch["stages"]}
    for sid in ("PACK_CELLS", "PACK_LEAD", "DOCK_ENTRY", "DOCK_BLOCK", "BOARD_A_NODE", "BOARD_A_CONVERTERS", "SHORE_INPUT"):
        if sid not in st:
            refuse("the energy chain has no stage %s" % sid)
    I["chain"] = st
    I["blade_a"] = float(st["DOCK_ENTRY"]["protection"]["rating_a"])
    for sid in ("BOARD_A_NODE", "PACK_CELLS"):
        if float(st[sid]["protection"]["rating_a"]) != I["blade_a"]:
            refuse("the pack path's blades are not one rating")
    I["shore_fuse_a"] = float(st["SHORE_INPUT"]["protection"]["rating_a"])
    I["pf_low"], I["pf_high"] = float(st["PACK_CELLS"]["prospective_fault_a"]["low"]), float(st["PACK_CELLS"]["prospective_fault_a"]["high"])
    I["xt60_a"], I["xt60_peak"] = float(st["PACK_LEAD"]["connector"]["rating_a"]), float(st["PACK_LEAD"]["connector"]["peak_a"])
    m = need(st["DOCK_BLOCK"]["conductor"]["basis"], r"Continuous (\d+) amps @ (\d+) C temperature rise", "the dock pins' rating")
    I["pin_a"], I["pin_rise"] = float(m.group(1)), float(m.group(2))
    I["pins"] = int(round(float(st["DOCK_BLOCK"]["conductor"]["rating_a"]) / I["pin_a"]))
    # the pack's declared currents and its hardware level
    pp = yaml.safe_load(text("pack_protection"))
    I["cont"], I["peak"] = float(pp["pack"]["declared_continuous_a"]), float(pp["pack"]["declared_peak_a"])
    f2 = pp["devices"]["F2"]["why"]
    m = need(f2, r"(\d+) A, 4 to 5 cells, (\d+) percent of rating for (\d+) hour minimum and (\d+) percent opens within (\d+) s maximum, (\d+) A breaking", "F2's rows")
    I["f2"] = dict(a=float(m.group(1)), hold_pct=float(m.group(2)), hold_h=float(m.group(3)), open_pct=float(m.group(4)),
                   open_s=float(m.group(5)), break_a=float(m.group(6)))
    # the gauge's image (PRIMARY-CONFIGURATION.md): OCD1, OCD2, AOLD, ASCD
    g = text("gauge_image")
    m1 = need(g, r"^\| OCD1 \(14\.9\.6\) \| [^|]*\| -(\d+) mA, (\d+) s \|", "OCD1")
    m2 = need(g, r"^\| OCD2 \(14\.9\.7\) \| [^|]*\| -(\d+) mA, (\d+) s", "OCD2")
    m3 = need(g, r"^\| AOLD threshold and delay [^|]*\| [^|]*\| (\d+) A class, (\d+) ms", "AOLD")
    m4 = need(g, r"^\| ASCD1/2 threshold and delay [^|]*\| [^|]*\| about ([0-9.]+) or [0-9.]+ A .*? at about (\d+) to (\d+) us \|", "ASCD")
    I["gauge"] = [("OCD1", float(m1.group(1)) / 1000.0, float(m1.group(2))), ("OCD2", float(m2.group(1)) / 1000.0, float(m2.group(2))),
                  ("AOLD", float(m3.group(1)), float(m3.group(2)) / 1000.0), ("ASCD", float(m4.group(1)), float(m4.group(3)) * 1e-6)]
    # the 25 A MINI (Littelfuse 297): the time-current rows, the 25 A and 10 A rows, the operating range
    t = pdf("mini_297")
    rows = []
    m = need(t, r"^\s*110\s+([0-9,]+) s / ", "the 297's 110 percent row")
    rows.append((110.0, float(m.group(1).replace(",", "")), None))
    for pct in ("135", "200", "350", "600"):
        m = need(t, r"^\s*%s\s+([0-9.]+) s / ([0-9.]+) s\s*$" % pct, "the 297's %s percent row" % pct)
        rows.append((float(pct), float(m.group(1)), float(m.group(2))))
    I["mini_rows"] = rows
    for amps in (25, 10):
        m = need(t, r"^\s*0297%03d\._\s+%d A\s+(\d+) mV\s+([0-9.]+) m\S+\s+(\d+) A\S*s\s*$" % (amps, amps), "the 297's %d A row" % amps)
        I["mini_%d" % amps] = dict(mv=float(m.group(1)), mohm=float(m.group(2)), i2t=float(m.group(3)))
    m = need(t, r"Operating Temperature Range:\s+-40\S+C to \+(\d+)\S+C", "the 297's operating range")
    I["mini_max_c"] = float(m.group(1))
    # record L4-E11: the docking pulse, the mixed-air line, the shore fuse's envelope and the interconnect's selection
    o = text("l4e11_out")
    m = need(o, r"the WHOLE hot docking waveform accepted \(sections 16d and 17b\): ([0-9.]+) A peak, time constant ([0-9.]+) us", "the docking pulse")
    I["dock_pk"], I["dock_tau"] = float(m.group(1)), float(m.group(2)) * 1e-6
    I["air_c"] = float(need(o, r"the consolidation's \+(\d+) C mixed-air line", "the mixed-air line").group(1))
    m = need(o, r"0997010\.WXN time-current \(MAKER, held sheet p\.3\): 110 %: (\d+) to - s; 135 %: ([0-9.]+) to ([0-9.]+) s; "
             r"200 %: ([0-9.]+) to ([0-9.]+) s; 350 %: ([0-9.]+) to ([0-9.]+) s; 600 %: ([0-9.]+) to ([0-9.]+) s", "the shore fuse's rows")
    I["shore_rows"] = [(110.0, float(m.group(1)), None), (135.0, float(m.group(2)), float(m.group(3))), (200.0, float(m.group(4)), float(m.group(5))),
                       (350.0, float(m.group(6)), float(m.group(7))), (600.0, float(m.group(8)), float(m.group(9)))]
    I["shore_stiff_a"] = float(need(o, r"up to the specified worst stiff-source current (\d+) A", "the stiff source").group(1))
    I["shore_i2t_typ"] = float(need(o, r"the sheet's (\d+) A2s is a typical melting figure", "the shore fuse's I2t").group(1))
    I["shore_withstand_a"] = float(need(o, r"board E's copper J_DCIN to F1 to the clamps\s+at least (\d+) A continuous", "L4-E11's D-06 selection").group(1))
    need(o, r"F1's holder, Keystone 3568\s+no rating \(the page prints a UL current rating for other MINI clips and holders", "the holder's rating")
    # record l9pwr (Layer 8's copy): the pack current per state, DRAFTED, at the stack voltages 16.8 / 14.4 / 12.0 / 10.0 V
    p = text("l9pwr_out")
    sec = need(p, r"^6\. THE PACK CURRENT \(A\).*?(?=^7\. )", "l9pwr's section 6").group(0)
    states = {}
    for b in re.finditer(r"^   (\S[^\n]*?)\s{2,}(sustained|key-down)\s*\n(?:.*\n){2}      DRAFTED  PLAN\s+([0-9. ]+?)\s+HIGH\s+([0-9. ]+?)\s*$", sec, re.M):
        states[b.group(1).strip()] = (b.group(2), [float(x) for x in b.group(3).split()], [float(x) for x in b.group(4).split()])
    if len(states) < 15:
        refuse("l9pwr's section 6 read %d states" % len(states))
    I["states"] = states
    # POWER-THERMAL: PWR-F12's 18 A for 60 s and the PA's key-on step
    pt = text("power_thermal")
    m = need(pt, r"PWR-F12 drafts (\d+) A for (\d+) s", "PWR-F12's key-down")
    I["kd_a"], I["kd_s"] = float(m.group(1)), float(m.group(2))
    m = need(pt, r"^\| PA key-on step at the pack \| [^|]*\| \| \| ([0-9.]+) to ([0-9.]+) A \|", "the key-on step")
    I["step"] = (float(m.group(1)), float(m.group(2)))
    # Onderdonk as the tree holds it
    f = text("fusing")
    m = need(f, r"Ifuse = Area x SQRT\(LOG\(\(Tmelt - Tambient\) / \((\d+) \+ Tambient\) \+ 1\) / \(Time x (\d+)\)\)", "Onderdonk's general form")
    I["k234"], I["k33"] = float(m.group(1)), float(m.group(2))
    I["t_melt"] = float(need(f, r"\((\d+) C for copper\)", "copper's melting point").group(1))
    # the parts in the path
    l = text("lcsc_fill")
    m = need(l, r'\(r"\^(\d+)mOhm 1% 2512 \\\(RSR", "R_2512"\): "(C\d+)",\s+# [^\n]*?: ([A-Z][A-Z0-9 ]+), \d+ mOhm 1 % (\d+) W, board A R17', "R17's part")
    I["r17"] = dict(code=m.group(2), w=float(m.group(4)), mohm=float(m.group(1)), mpn=m.group(3))
    m = need(l, r'\(r"\^(\d+)mOhm 1% 2512", "R_2512"\): "(C\d+)",\s+# ([^,\n]+), (\d+) W,', "R19's part")
    I["r19"] = dict(code=m.group(2), w=float(m.group(4)), mohm=float(m.group(1)), mpn=m.group(3))
    a = text("gen_sch_a")
    need(a, r'r\("R17", "5mOhm 1% 2512 \(RSR, charge current sense\)", "VBAT", "CELL_FUSED", "RS2512"\)', "R17 in the pack path")
    need(a, r'part\("F1", "Device", "Fuse", "25 A mini blade \(Keystone 3568 holder\): pack node to the RSR shunt", "FUSE", \{"1": "CELL\+", "2": "CELL_FUSED"\}\)', "board A's F1")
    if not re.search(r'for k in range\(1, %d\):\s*\n\s*part\("J_CP%%d" %% k' % (I["pins"] + 1), a):
        refuse("board A's dock pins are not %d" % I["pins"])
    I["fet_refs"], I["fet_part"] = battery_fets(text("charger_draft"))      # round 3: parsed, as the draft now is (Q39, Q40, Q42)
    m = need(o, r"\(Q-c\) Nexperia BUK6Y10-30P, two in parallel \(MAKER, INFERRED\):\n\s+printed maxima:[^\n]*\n\s+limit 150 C[^\n]*?gate factor [0-9.]+, ([0-9.]+) mOhm per FET", "the pair's RDS(on) bound")
    I["pair_mohm_each"] = float(m.group(1))
    I["fet_mohm_each"] = float(need(o, r"reproduced on this record's RDS\(on\) allowance ([0-9.]+) mOhm \(section 16a\)", "the battery FETs' RDS(on) allowance (L4-E11 19b)").group(1))
    e = text("gen_sch_e")
    need(e, r'part\("F3", "Device", "Fuse", "25 A mini blade \(Keystone 3568 holder\): pack to the block", "FUSE", \{"1": "CELL\+", "2": "CELL_F"\}\)', "board E's F3")
    need(e, r'part\("F1", "Device", "Fuse", "10 A mini blade \(Keystone 3568 holder\): vehicle input", "FUSE", \{"1": "DC_IN", "2": "DC_F"\}\)', "board E's F1")
    need(e, r'r\("R19", "10mOhm 1% 2512 \(hot-swap sense\)", "DC_P", "HS_S", "RS2512"\)', "R19")
    I["veh"] = float(need(e, r"^_VEH_T, _VEH_P = ([0-9.]+), ([0-9.]+)$", "_VEH_T").group(1))
    I["trk_valley"] = float(need(e, r"valley threshold \(8705af p\.3\) over R5's 5 mOhm is ([0-9.]+) A", "the tracker's valley").group(1))
    I["vin_raw"] = float(need(e, r"_VIN_T = _VIN_P = min\(round\(_VEH_T \+ _TRK_A, 2\), _FE_A\)  # R4A-N12: ([0-9.]+) A", "VIN_RAW").group(1))
    m = need(e, r"^_TRK_A = round\(([0-9.]+) \* ([0-9.]+) / ([0-9.]+), 2\)", "_TRK_A")
    I["trk"] = round(float(m.group(1)) * float(m.group(2)) / float(m.group(3)), 2)
    # the ECSS fits' stated data ranges
    ec = text("ecss_70_12c")
    I["ipc2152_a"], I["ipc2152_k"] = (float(x) for x in need(ec, r"valid for a range up to (\d+) A and up to (\d+)degC", "IPC-2152's range").groups())
    I["cnes_a"] = float(need(ec, r"experimental data ranging up to (\d+) A and up to", "CNES's range").group(1))
    # dc_drop's raster cell (the routed-board judge of PI-001)
    I["cell"] = float(need(text("dc_drop"), r'cell = float\(_v\.opt\(a, "--cell", ([0-9.]+)\)\)', "dc_drop's cell").group(1))
    # the decisions this record builds on
    d = yaml.safe_load(text("decisions"))
    if 35 not in {int(x["n"]) for x in d["decisions"]}:
        refuse("decision 35 is not in the register")
    return I


def read_more(I):
    """The inputs the revision added: the inside air without the hold, the pair's installed target, the parts' printed limits,
    the blade's plating and its identity, the dock contacts' resistance."""
    m = need(text("l4e12_out"), r"E3-O ([0-9.]+) C, E5's dwell ([0-9.]+) C \(steady", "L4-E12's mixed inside air")
    I["air_e3o"], I["air_e5"] = float(m.group(1)), float(m.group(2))
    I["t0"] = max(I["air_c"], I["air_e3o"], I["air_e5"])
    o = text("l4e11_out")
    I["pair_rth"] = float(need(o, r"the installed \(Zself \+ Zmut\) at steady state at most ([0-9.]+) K/W", "E11-29's target").group(1))
    m = need(o, r"20 A held under OCD1 reaches (\d+) C at most \((\d+) K under the (\d+) C limit", "the pair's limit")
    I["pair_tj_20"], I["pair_limit"] = float(m.group(1)), float(m.group(3))
    I["pair_zjmb"] = [(float(w) * (1e-3 if u == "ms" else (1e-6 if u == "us" else 1.0)), float(z)) for w, u, z in re.findall(
        r"for ([0-9.]+) (s|ms|us): per FET [0-9.]+ W; \(Zself \+ Zmut\) at [0-9.]+ s at most [0-9.]+ K/W \([^)]*\), the device alone ([0-9.]+) K/W", o)]
    if len(I["pair_zjmb"]) != 3:
        refuse("L4-E11's three device impedances did not read")
    I["pair_tj_18"] = float(need(o, r"THE SERVICE, 18 A FOR 60 S FROM THE HOT STATE [^:]*: TJ ([0-9.]+) C", "the pair's 18 A service").group(1))
    # round 3: L4-E11's round 9 (its section 19c) restates E11-29 for the three battery FETs as this record's junction limit and
    # withdraws the pair's targets; the lines above stay in L4-E11's output as its dated sections 15 and 16 and are read as such
    m = need(o, r"the installed three, each FET's \(Zself \+ 2 Zmut\) at most ([0-9.]+) K/W steady with R17 placed apart, R17's coupling into each junction at most ([0-9.]+) K/W\s+"
             r"\(heat R17 alone\): so the hottest junction stays at most (\d+) C held at ([0-9.]+) A from ([0-9.]+) C with the band and R17 in place", "E11-29 restated (L4-E11 19c)")
    I["fet_rth"], I["fet_r17c"], I["fet_limit"], I["fet_i_held"], I["fet_t0"] = (float(m.group(k)) for k in range(1, 6))
    m = need(o, r"the pair's former steady target ([0-9.]+) K/W at \+(\d+) C air and its 1 s, 20 ms and 244 us targets are WITHDRAWN", "the pair's targets withdrawn (L4-E11 19c)")
    I["pair_rth_withdrawn"] = float(m.group(1))
    if len(I["fet_refs"]) != 3:
        refuse("L4-E11's section 19c states E11-29 for three battery FETs and its charger draft draws %d" % len(I["fet_refs"]))
    t = pdf("xt60")
    I["xt60_max_c"] = float(need(t, r"\.-20\S to (\d+)\S", "the XT60's operating range").group(1))
    t = pdf("vh")
    I["vh_a"] = float(need(t, r"Current rating: (\d+) A", "the VH's current rating").group(1))
    I["vh_max_c"] = float(need(t, r"Temperature range: \S40\S to \+(\d+)\S", "the VH's range").group(1))
    t = pdf("mini_297")
    I["mini_sn_max_c"] = float(need(t, r"\(Sn=-40\S+C to \+(\d+)\S+C\)", "the tin blade's range").group(1))
    I["mini_ag_order"] = need(t, r"0297xxx\.(WXNV)\s+3000", "the 297's first ordering row").group(1)
    I["mini_sn_order"] = need(t, r"MINI\S* Sn Fuse\s+0297xxx\.(WXT)\s+3000", "the tin blade's ordering row").group(1)
    need(t, r"Terminals:\s+Ag plated zinc alloy", "the 297's terminals")
    src = yaml.safe_load(text("sources"))
    ent = [e for e in (src.get("entries") or src.get("parts") or (src if isinstance(src, list) else [])) if isinstance(e, dict) and e.get("id") == "pack-blade-fuse-holder"]
    if len(ent) != 1:
        refuse("SOURCES.yaml has %d pack-blade-fuse-holder entries" % len(ent))
    e = ent[0]
    I["blade_entry"] = dict(fitted=e["fitted_mpn"], boards=list(e["boards"]))
    I["holder_max_c"] = float(need(e["grade_vs_envelope"], r"holder UL temperature rating -50 to \+(\d+) C", "the holder's range").group(1))
    I["blade_pinned"] = ("0297025." + I["mini_ag_order"]) in e["fitted_mpn"]
    m = need(I["chain"]["DOCK_BLOCK"]["conductor"]["basis"], r"Contact Resistance: (\d+) mOhm max", "the dock pins' resistance")
    I["pin_mohm_max"] = float(m.group(1))
    pp = yaml.safe_load(text("pack_protection"))
    I["cells_a"] = pp["cell"]["limits"]["max_continuous_discharge_ma"]["value"] / 1000.0 * pp["pack"]["parallel_min"]
    return I


# ------------------------------------------------------------------------------------------------ 2. the ruled method
def t_out(oz):
    return dict(sw.STACKS["JLC04161H-7628"][0:1])["F.Cu"] * oz        # 0.035 mm a 1 oz outer face


def t_in_half():
    return dict(x for x in sw.STACKS["JLC04161H-7628"] if len(x) == 2)["In1.Cu"]


def rating(width, oz, dT, internal=False):
    a = width * (t_in_half() if internal else t_out(oz))
    amps, model = tc.conservative(a, dT)
    return (amps if internal else amps * tc.EXTERNAL_FACTOR), model


def rise_steady(amps, width, oz, internal=False):
    """The rise at which the ruled model rates one conductor of this width and copper weight at `amps` (None over 300 K)."""
    if amps <= 0:
        return 0.0
    lo, hi = 1e-4, 300.0
    if rating(width, oz, hi, internal)[0] < amps:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if rating(width, oz, mid, internal)[0] < amps:
            lo = mid
        else:
            hi = mid
    return hi


def k_share(s):
    """An uneven split's extra dissipation: the current an even split would need to dissipate as much."""
    return math.sqrt(2.0 * (s * s + (1.0 - s) ** 2))


def i_lump(amps, k_f, k_r):
    """A band and its adjacent return, each on two faces, as one conductor of twice the width and both faces' copper: the
    current that dissipates in it what the two bands dissipate (each band's faces at their split)."""
    return amps * math.sqrt(2.0 * (k_f * k_f + k_r * k_r))


def w_pair(amps, oz_face, k=1.0):
    """The width of each band, on each face, when a band and its adjacent return are one conductor (both faces of both)."""
    return tc.width_for_current(i_lump(amps, k, k), oz=2.0 * oz_face) / 2.0


def w_alone(amps, oz_face, k=1.0):
    """The width on each face of a band whose two faces are one conductor, its return laid apart (no credit held for apart)."""
    return tc.width_for_current(amps * k, oz=2.0 * oz_face)


def rise_pair(amps, w, oz_face, k=1.0):
    return rise_steady(i_lump(amps, k, k), 2.0 * w, 2.0 * oz_face)


def rise_alone(amps, w, oz_face, k=1.0):
    return rise_steady(amps * k, w, 2.0 * oz_face)


def cmil(area_mm2):
    return area_mm2 * tc.C1 * 4.0 / math.pi


def rise_adiabatic(i2t, area_mm2, I):
    """Onderdonk's adiabatic rise from the worst inside air for an I2t on a section of copper (no cooling: the upper bound)."""
    c = cmil(area_mm2)
    x = I["k33"] * i2t / (c * c)
    if x > 50:
        return float("inf")
    return (I["k234"] + I["t0"]) * (10.0 ** x - 1.0)


def fusing_i2t(area_mm2, I):
    c = cmil(area_mm2)
    return c * c * math.log10(1.0 + (I["t_melt"] - I["t0"]) / (I["k234"] + I["t0"])) / I["k33"]


def i2t_to(area_mm2, limit_c, I):
    """The I2t that takes a section of copper adiabatically from the worst inside air to a temperature."""
    c = cmil(area_mm2)
    return c * c * math.log10(1.0 + (limit_c - I["t0"]) / (I["k234"] + I["t0"])) / I["k33"]


# ------------------------------------------------------------------------------------------------ 3. the split and the barrels
_S = {}


def stk():
    if "S" not in _S:
        _S["S"] = stackups_module()
    return _S["S"]


def drill():
    return stk().DRILL           # record l9stk's 0.4 mm drill, the same the stackup record sizes every transition with


def annulus(conv):
    """A barrel's copper: 'outward' takes the 0.4 mm as the finished hole with the plating outside it (via_current's
    pi (d + t) t); 'inward' takes it as the drill with the plating inside (pi (d - t) t), the smaller."""
    t = vc.PLATING_UM / 1000.0
    d = drill()
    return math.pi * (d + t) * t if conv == "outward" else math.pi * (d - t) * t


def barrel_amps(conv):
    return tc.conservative(annulus(conv), 10.0)[0]


def barrels(amps, conv):
    return int(math.ceil(amps / barrel_amps(conv) - 1e-12))


def r_barrel(h):
    """One barrel's resistance between the outer faces, in units of rho per mm (outward convention; rho cancels in a share)."""
    return h / annulus("outward")


def r_band(L, w, oz):
    return L / (w * t_out(oz))


def share_one_end(L, w, oz, n, h):
    rb, rv = r_band(L, w, oz), r_barrel(h) / n
    return (rb + rv) / (2 * rb + rv)


def share_both_ends(L, w, oz, n, h):
    rb, rv = r_band(L, w, oz), r_barrel(h) / n
    return (rb + 2 * rv) / (2 * rb + 2 * rv)


def n_for(L, w, oz, h, s, both):
    rb = r_band(L, w, oz)
    k = (2 * s - 1) / (2 * (1 - s)) if both else (2 * s - 1) / (1 - s)
    return int(math.ceil(r_barrel(h) / (k * rb) - 1e-9))


# ------------------------------------------------------------------------------------------------ 4. the events
def envelope(rating_a, rows, high_a):
    """A blade read monotone (a larger current clears no later than a smaller one, as L4-E11 section 6 reads its fuse): up to
    the first row with a maximum time no opening is assured; each later interval may last as long as the maximum of the
    row below it, its top current being the next row's; above the last row, to the prospective high end."""
    out = []
    timed = [(p, b) for p, a, b in rows if b is not None]
    first = timed[0][0]
    out.append(("up to %g %%, no opening assured" % first, rating_a * first / 100.0, None))
    for (p0, t0), (p1, _t1) in zip(timed, timed[1:]):
        out.append(("%g to %g %%, at most %g s" % (p0, p1, t0), rating_a * p1 / 100.0, t0))
    out.append(("over %g %% to %g A, at most %g s" % (timed[-1][0], high_a, timed[-1][1]), high_a, timed[-1][1]))
    return out


def events_pack(I):
    b = I["blade_a"]
    ev = [("10 A continuous (declared)", I["cont"], None, "load"),
          ("18 A for 60 s (PWR-F12, judged steady)", I["kd_a"], I["kd_s"], "transient"),
          ("held just under the gauge's OCD1", I["gauge"][0][1], None, "gauge")]
    for name, a, s in I["gauge"][1:]:
        ev.append(("gauge %s" % name, a, s, "gauge"))
    ev.append(("25 A held (the blades' rating, the chain's check 3)", b, None, "coordination"))
    for lab, a, s in envelope(b, I["mini_rows"], I["pf_high"]):
        ev.append(("gauge failed: blade " + lab, a, s, "backstop"))
    ev.append(("hard short at the blade's nominal melting I2t (not a clearing figure)", I["pf_high"], I["mini_25"]["i2t"] / I["pf_high"] ** 2, "nominal"))
    ev.append(("hard short cleared by the gauge's ASCD", I["pf_high"], I["gauge"][-1][2], "short"))
    ev.append(("docking pulse", I["dock_pk"], None, "pulse"))
    return ev


def events_shore(I):
    f = I["shore_fuse_a"]
    ev = [("6.15 A continuous (_VEH_T)", I["veh"], None, "load"),
          ("10 A held (F1's rating, the chain's check 3)", f, None, "coordination"),
          ("20 A held (L4-E11's D-06 withstand)", I["shore_withstand_a"], None, "coordination")]
    for lab, a, s in envelope(f, I["shore_rows"], I["shore_stiff_a"]):
        ev.append(("Q7 shorted: fuse " + lab, a, s, "backstop"))
    ev.append(("stiff source at the fuse's nominal melting I2t (not a clearing figure)", I["shore_stiff_a"], I["shore_i2t_typ"] / I["shore_stiff_a"] ** 2, "nominal"))
    return ev


def judge(ev, w, oz_face, k, lumped, s, I, limit_c):
    """Each event on a band family: the steady rise of the family's conductor (lumped with its return or alone), the
    adiabatic rise of the governing face, the reading (held: steady; timed: the smaller), the final temperature from the
    worst inside air, and the verdict against 10 K (load, transient, gauge, coordination) or the band's limit (the rest)."""
    out = []
    face = w * t_out(oz_face)
    for lab, a, dur, cls in ev:
        if cls == "pulse":
            i2t = a * a * I["dock_tau"] / 2.0
            ad = rise_adiabatic(i2t * s * s, face, I)
            out.append(dict(lab=lab, a=a, dur=dur, cls=cls, i2t=i2t, st=None, ad=ad, r=ad))
            continue
        st = rise_pair(a, w, oz_face, k) if lumped else rise_alone(a, w, oz_face, k)
        if dur is None:
            out.append(dict(lab=lab, a=a, dur=None, cls=cls, i2t=None, st=st, ad=None, r=st))
            continue
        i2t = a * a * dur
        ad = rise_adiabatic(i2t * s * s, face, I)
        r = ad if st is None else min(st, ad)
        out.append(dict(lab=lab, a=a, dur=dur, cls=cls, i2t=i2t, st=st, ad=ad, r=r))
    for x in out:
        x["T"] = None if x["r"] is None or x["r"] == float("inf") else I["t0"] + x["r"]
        if x["cls"] in ("load", "transient", "gauge", "coordination"):
            x["ok"] = x["r"] is not None and x["r"] <= 10.0 + 1e-6
        else:
            x["ok"] = x["T"] is not None and x["T"] <= limit_c + 1e-6
    return out


# ------------------------------------------------------------------------------------------------ 5. the board geometry
def footprints(path, refs):
    t = open(rel(path), encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
        i, d = m.start() + 1, 0
        while True:
            c = t[i]
            if c == "(":
                d += 1
            elif c == ")":
                d -= 1
                if d == 0:
                    break
            i += 1
        b = t[m.start() + 1:i + 1]
        r = re.search(r'\(property "Reference" "([^"]+)"', b)
        if not r or r.group(1) not in refs:
            continue
        at = re.search(r'\n\t\t\(at ([-0-9.]+) ([-0-9.]+)', b)
        layer = re.search(r'\n\t\t\(layer "([^"]+)"\)', b).group(1)
        pads = []
        for p in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)\s*\(at ([-0-9. ]+)\)\s*\(size ([0-9.]+) ([0-9.]+)\)(?:\s*\(drill ([0-9.]+)\))?', b):
            net = re.search(r'\(net \d+ "([^"]+)"\)', b[p.start():p.start() + 1500])
            xy = [float(v) for v in p.group(4).split()[:2]]
            pads.append(dict(num=p.group(1), kind=p.group(2), x=float(at.group(1)) + xy[0], y=float(at.group(2)) + xy[1],
                             w=float(p.group(5)), h=float(p.group(6)), drill=float(p.group(7)) if p.group(7) else None,
                             net=(net.group(1) if net else "").lstrip("/")))
        out[r.group(1)] = dict(lib=m.group(1), layer=layer, pads=pads)
    missing = [x for x in refs if x not in out]
    if missing:
        refuse("%s has no %s" % (path, ", ".join(missing)))
    return out


def kind(fp, ref):
    return "TH" if all(p["kind"] == "thru_hole" for p in fp[ref]["pads"]) else "1F"


def length_between(fp, a, b):
    ax = [(p["x"] - p["w"] / 2.0, p["x"] + p["w"] / 2.0) for p in fp[a]["pads"]]
    bx = [(p["x"] - p["w"] / 2.0, p["x"] + p["w"] / 2.0) for p in fp[b]["pads"]]
    lo, hi = (ax, bx) if min(x[0] for x in ax) < min(x[0] for x in bx) else (bx, ax)
    return round(min(x[0] for x in hi) - max(x[1] for x in lo), 2)


# ------------------------------------------------------------------------------------------------ compute
def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing" % (k, p))
    R = {"pins": dict({k: (p, sha(p)) for k, p in PINS.items()},
                      **{"pdftext %02d" % i: (t, (h or "ABSENT")[:16]) for i, (t, h, _held) in enumerate(PT.inputs(ROOT, PDFTEXT), 1)})}
    I = read_inputs()
    read_more(I)
    R["in"] = I
    S = stk()
    h_a, h_e = sw.total("JLC06161H-3313"), sw.total("JLC04161H-7628")
    R["h"] = (h_a, h_e)
    blade, shore, wst = I["blade_a"], I["shore_fuse_a"], I["shore_withstand_a"]
    ks = k_share(S_MAX)
    R["ks"] = ks
    # the states
    sus = [(k, v[1][3], v[2][3]) for k, v in I["states"].items() if v[0] == "sustained"]
    kd = [(k, v[1][3], v[2][3]) for k, v in I["states"].items() if v[0] == "key-down"]
    base = [x for x in sus if "plus" not in x[0]]
    R["sustained_plan_base"] = max(base, key=lambda x: x[1])
    R["sustained_high_base"] = max(base, key=lambda x: x[2])
    R["sustained_plan_max"] = max(sus, key=lambda x: x[1])
    R["keydown_plan_max"] = max(kd, key=lambda x: x[1])
    # the limits: the lowest printed limit of the parts each band joins (the blade's as fitted, its plating unpinned, and pinned)
    blade_c = I["mini_max_c"] if I["blade_pinned"] else I["mini_sn_max_c"]
    R["blade_c"] = dict(fitted=blade_c, pinned=I["mini_max_c"])
    L = {"pack A": [("the blade (MINI 297)", blade_c), ("the 3568 holder", I["holder_max_c"])],
         "pack E": [("the blade (MINI 297)", blade_c), ("the 3568 holder", I["holder_max_c"]), ("the XT60", I["xt60_max_c"])],
         "shore E": [("the blade (MINI, 10 A; the 297's figures, the 997's not held)", blade_c), ("the 3568 holder", I["holder_max_c"]), ("J_DCIN (JST VH, as drawn)", I["vh_max_c"])]}
    R["limits"] = {k: (min(v for _n, v in x), min(x, key=lambda y: y[1])[0], x) for k, x in L.items()}
    R["limits_pinned"] = {k: min([v for n, v in x if "blade" not in n] + [I["mini_max_c"]]) for k, x in L.items()}
    lim_pack = min(R["limits"]["pack A"][0], R["limits"]["pack E"][0])
    lim_shore = R["limits"]["shore E"][0]
    # the widths: what each current asks, the quoted ones, and this revision's
    W = {}
    W["svc_even"] = tc.width_for_current(I["kd_a"] / 2.0, oz=OZ1)          # 6.72: each face rated alone at half
    W["svc_one_2oz"] = tc.width_for_current(I["kd_a"], oz=OZ2)              # 11.95
    W["cand_even"] = tc.width_for_current(blade / 2.0, oz=OZ1)              # 12.26: f76564eb, each face alone at half
    W["cand_smax"] = tc.width_for_current(blade * S_MAX, oz=OZ1)            # 14.60
    W["alone_1"] = w_alone(blade, OZ1)                                      # 21.81: the two faces as one conductor
    W["alone_1k"] = w_alone(blade, OZ1, ks)
    W["pair_1"] = w_pair(blade, OZ1)                                        # a band and its adjacent return as one conductor
    W["pair_1k"] = w_pair(blade, OZ1, ks)
    W["pair_2"] = w_pair(blade, OZ2)
    W["pair_2k"] = w_pair(blade, OZ2, ks)
    W["alone_2k"] = w_alone(blade, OZ2, ks)
    W["sh_pair_1k"] = w_pair(wst, OZ1, ks)
    W["sh_pair_1"] = w_pair(wst, OZ1)
    W["sh_pair_2k"] = w_pair(wst, OZ2, ks)
    W["sh_alone_1k"] = w_alone(wst, OZ1, ks)
    W["vin_pair_1k"] = w_pair(I["vin_raw"], OZ1, ks)
    W["vin_pair_2k"] = w_pair(I["vin_raw"], OZ2, ks)
    W["trk_pair_1k"] = w_pair(I["trk"], OZ1, ks)
    R["w"] = W
    nf = blade * I["mini_rows"][0][0] / 100.0
    R["ask"] = [(lab, a, w_alone(a, OZ1), w_pair(a, OZ1), w_pair(a, OZ2)) for lab, a in (
        ("the continuous load", I["cont"]), ("the transient (PWR-F12)", I["kd_a"]), ("held just under the gauge's OCD1", I["gauge"][0][1]),
        ("the blades' rating (the coordination current)", blade), ("the blades' %g %% current, no opening assured" % I["mini_rows"][0][0], nf))]
    # the band families
    pe, se = events_pack(I), events_shore(I)
    fam = [
        ("A1", "6.72 mm a face, 1 oz (l9stk at 18 A), with its adjacent return", W["svc_even"], OZ1, 1.0, True, 0.5, pe, lim_pack),
        ("C1", "12.26 mm a face, 1 oz (f76564eb), its two faces as one conductor, return apart", W["cand_even"], OZ1, 1.0, False, 0.5, pe, lim_pack),
        ("C2", "12.26 mm a face, 1 oz (f76564eb), with its adjacent return", W["cand_even"], OZ1, 1.0, True, 0.5, pe, lim_pack),
        ("D1", "%.2f mm a face, 1 oz, with its adjacent return (this revision)" % W["pair_1k"], W["pair_1k"], OZ1, ks, True, S_MAX, pe, lim_pack),
        ("D2", "%.2f mm a face, 2 oz, with its adjacent return (this revision)" % W["pair_2k"], W["pair_2k"], OZ2, ks, True, S_MAX, pe, lim_pack),
        ("D3", "%.2f mm a face, 1 oz, return laid apart (no credit held for apart)" % W["alone_1k"], W["alone_1k"], OZ1, ks, False, S_MAX, pe, lim_pack),
        ("H1", "%.2f mm a face, 1 oz, the shore input with its adjacent return (DC_HS included)" % W["sh_pair_1k"], W["sh_pair_1k"], OZ1, ks, True, S_MAX, se, lim_shore),
        ("H2", "%.2f mm a face, 2 oz, the shore input with its adjacent return" % W["sh_pair_2k"], W["sh_pair_2k"], OZ2, ks, True, S_MAX, se, lim_shore),
    ]
    F = {}
    for key, lab, w, oz, k, lumped, s, ev, lim in fam:
        lp = min(R["limits_pinned"]["pack A"], R["limits_pinned"]["pack E"]) if ev is pe else R["limits_pinned"]["shore E"]
        rows_ = judge(ev, w, oz, k, lumped, s, I, lim)
        for x in rows_:
            x["ok_pin"] = x["ok"] if x["cls"] in ("load", "transient", "gauge", "coordination") else (x["T"] is not None and x["T"] <= lp + 1e-6)
        F[key] = dict(label=lab, w=w, oz=oz, k=k, lumped=lumped, s=s, lim=lim, lim_pin=lp, rows=rows_, fusing=fusing_i2t(w * t_out(oz), I))
    R["fam"] = F
    vin = [("14.10 A declared", I["vin_raw"], None, "load"), ("the tracker's minimum valley limit, held", I["trk_valley"], None, "coordination")]
    R["vin"] = dict(w=W["vin_pair_1k"], rows=judge(vin, W["vin_pair_1k"], OZ1, ks, True, S_MAX, I, lim_shore),
                    sum_a=I["veh"] + I["trk_valley"])
    R["vin"]["sum_rise"] = rise_pair(R["vin"]["sum_a"], W["vin_pair_1k"], OZ1, ks)
    # the split and the barrels
    R["barrel"] = {c: dict(area=annulus(c), amps=barrel_amps(c)) for c in ("outward", "inward")}
    R["thermal_barrels"] = {k: {c: barrels(a / 2.0, c) for c in ("outward", "inward")} for k, a in (("pack", blade), ("shore", wst), ("vin", I["vin_raw"]))}
    def field_for(rows_, lim):
        """The least inward-annulus barrels that keep one barrel within the band's limit at every (current, time) given:
        steady at a second and longer, adiabatic below."""
        n = 1
        while True:
            ok = True
            for a_, d_ in rows_:
                per = 0.5 * a_ / n
                r = barrel_rise(per, "inward") if (d_ is None or d_ >= 1.0) else rise_adiabatic(per * per * d_, annulus("inward"), I)
                if r is None or I["t0"] + r > lim:
                    ok = False
                    break
            if ok:
                return n
            n += 1
    penv = envelope(blade, I["mini_rows"], I["pf_high"])
    senv = envelope(I["shore_fuse_a"], I["shore_rows"], I["shore_stiff_a"])
    R["field_pack_600"] = field_for([(a_, d_) for _l, a_, d_ in penv if d_ is None or d_ >= 60.0], min(R["limits_pinned"]["pack A"], R["limits_pinned"]["pack E"]))
    R["field_pack"] = max(R["thermal_barrels"]["pack"]["inward"], R["field_pack_600"])
    R["field_shore_600"] = field_for([(a_, d_) for _l, a_, d_ in senv if d_ is None or d_ >= 0.5], R["limits"]["shore E"][0])
    R["field_shore"] = max(R["thermal_barrels"]["shore"]["inward"], R["field_shore_600"])
    if R["thermal_barrels"]["pack"]["outward"] != vc.barrels_for(blade / 2.0, drill()):
        refuse("the outward count disagrees with via_current.barrels_for")
    T = []
    for name, w, hh in (("pack, board A, 1 oz", W["pair_1k"], h_a), ("pack, board E, 1 oz", W["pair_1k"], h_e),
                        ("pack, board E, 2 oz", W["pair_2k"], h_e), ("shore, board E, 1 oz", W["sh_pair_1k"], h_e)):
        oz = OZ2 if "2 oz" in name else OZ1
        T.append((name, w, hh, oz, [(Lx, n_for(Lx, w, oz, hh, S_MAX, False), n_for(Lx, w, oz, hh, S_MAX, True)) for Lx in LENGTHS]))
    R["transfer"] = T
    R["r_barrel"] = (r_barrel(h_a), r_barrel(h_e))
    R["barrel_mm_eq"] = r_barrel(h_e) * W["pair_1k"] * t_out(OZ1)
    R["no_field"] = {Lx: share_one_end(Lx, W["pair_1k"], OZ1, 1, h_e) for Lx in LENGTHS}
    R["no_field_k"] = {Lx: k_share(v) for Lx, v in R["no_field"].items()}
    # the parts on the boards as pinned
    fa = footprints(PINS["board_a"], ("F1", "R17", "J_CP1", "J_CN1"))
    fe = footprints(PINS["board_e"], ("J_BATT", "F3", "P_CP", "P_CN", "J_DCIN", "F1", "Q1", "R19", "Q7", "L2"))
    R["fp"] = dict(a=fa, e=fe)
    R["e7_cellf_len"] = length_between(fe, "F3", "P_CP")
    R["e7_ret_len"] = round([p for p in fe["P_CN"]["pads"]][0]["x"] - fe["P_CN"]["pads"][0]["w"] / 2.0
                            - ([p for p in fe["J_BATT"]["pads"] if p["net"] == "GND"][0]["x"] + [p for p in fe["J_BATT"]["pads"] if p["net"] == "GND"][0]["w"] / 2.0), 2)
    R["e7_dchs_len"] = length_between(fe, "Q7", "L2")
    R["e7_dcf_len"] = length_between(fe, "F1", "Q1")
    # the conductors (one row each): board, net, ends, protection, coordination A, k, widths, field, limit
    def fld(L, w, oz, hh, both, key):
        n = n_for(L, w, oz, hh, S_MAX, both)
        return max(n, R["field_" + key]), n
    rows = []
    cf = fld(R["e7_cellf_len"], W["pair_1k"], OZ1, h_e, False, "pack")
    for b, net, fr, to, ek, prot, coord, k, wk, lk, fieldtxt in (
        ("A", "CELL+", "J_CP1 to J_CP4", "F1", "%s / %s" % (kind(fa, "J_CP1"), kind(fa, "F1")), "E's F3 (upstream), the gauge", blade, 1.0, "pair", "pack A", "none (both ends through-hole)"),
        ("A", "CELL_FUSED", "F1", "R17", "%s / %s" % (kind(fa, "F1"), kind(fa, "R17")), "A's F1, the gauge", blade, ks, "pair", "pack A", "at R17, out 3's count at the band's length"),
        ("A", "CH_BATQ (drafted)", "R17", ", ".join(I["fet_refs"]), "1F / 1F", "A's F1, the gauge", blade, ks, "hop", "pack A", "a one-face hop at the parts' lands"),
        ("A", "VBAT trunk", "%s (R17 as drawn)" % ", ".join(I["fet_refs"]), "the first branch", "1F / loads", "A's F1, the gauge", blade, ks, "pair", "pack A", "at the FETs, out 3's count"),
        ("A", "GND (pack return)", "J_CN1 to J_CN4", "the returns and planes", "%s / planes" % kind(fa, "J_CN1"), "the loop's blades, the gauge", blade, 1.0, "pair", "pack A", "none at the pins"),
        ("E", "CELL+", "J_BATT pin 2", "F3", "%s / %s" % (kind(fe, "J_BATT"), kind(fe, "F3")), "P's F1 (upstream), the gauge", blade, 1.0, "pair", "pack E", "none (both ends through-hole)"),
        ("E", "CELL_F", "F3", "P_CP", "%s / %s" % (kind(fe, "F3"), kind(fe, "P_CP")), "E's F3, the gauge", blade, ks, "pair", "pack E", "E7: %d at P_CP (%.2f mm, split %d)" % (cf[0], R["e7_cellf_len"], cf[1])),
        ("E", "GND (pack return)", "J_BATT pin 1", "P_CN", "%s / %s" % (kind(fe, "J_BATT"), kind(fe, "P_CN")), "the loop's blades, the gauge", blade, ks, "pair", "pack E", "E7: %d at P_CN (%.2f mm, split %d)" % (fld(R["e7_ret_len"], W["pair_1k"], OZ1, h_e, False, "pack")[0], R["e7_ret_len"], fld(R["e7_ret_len"], W["pair_1k"], OZ1, h_e, False, "pack")[1])),
        ("E", "DC_IN", "J_DCIN pin 1", "F1", "%s / %s" % (kind(fe, "J_DCIN"), kind(fe, "F1")), "the source's own; F1 behind it", wst, 1.0, "shpair", "shore E", "none (both ends through-hole)"),
        ("E", "DC_F", "F1", "Q1, D10", "%s / %s" % (kind(fe, "F1"), kind(fe, "Q1")), "E's F1", wst, ks, "shpair", "shore E", "E7: %d at Q1 and D10 (%.2f mm, split %d)" % (fld(R["e7_dcf_len"], W["sh_pair_1k"], OZ1, h_e, False, "shore")[0], R["e7_dcf_len"], fld(R["e7_dcf_len"], W["sh_pair_1k"], OZ1, h_e, False, "shore")[1])),
        ("E", "DC_P", "Q1", "R19, D1", "%s / %s" % (kind(fe, "Q1"), kind(fe, "R19")), "E's F1", wst, ks, "hop", "shore E", "a one-face hop at the parts' lands"),
        ("E", "HS_S", "R19", "Q7", "%s / %s" % (kind(fe, "R19"), kind(fe, "Q7")), "E's F1", wst, ks, "hop", "shore E", "a one-face hop at the parts' lands"),
        ("E", "DC_HS", "Q7", "L2", "%s / %s" % (kind(fe, "Q7"), kind(fe, "L2")), "the hot-swap; F1 with Q7 shorted", wst, ks, "shpair", "shore E", "E7: %d at each end (%.2f mm, split %d)" % (max(n_for(R["e7_dchs_len"], W["sh_pair_1k"], OZ1, h_e, S_MAX, True), R["field_shore"]), R["e7_dchs_len"], n_for(R["e7_dchs_len"], W["sh_pair_1k"], OZ1, h_e, S_MAX, True))),
        ("E", "GND_V (shore return)", "J_DCIN pin 2", "the clamps, L2 pin 3", "%s / 1F" % kind(fe, "J_DCIN"), "E's F1 (the clamp-fault loop)", wst, ks, "shpair", "shore E", "at the clamps, out 3's count"),
        ("E", "VIN_RAW", "L2 and the tracker's Q2", "P_VR", "1F / 1F", "the sources' limits", I["vin_raw"], ks, "vinpair", "shore E", "at each end, out 3's count"),
    ):
        if wk == "pair":
            w1, w2, wa = W["pair_1k"] if k != 1.0 else W["pair_1"], W["pair_2k"] if k != 1.0 else W["pair_2"], W["alone_1k"] if k != 1.0 else W["alone_1"]
        elif wk == "shpair":
            w1, w2, wa = W["sh_pair_1k"] if k != 1.0 else W["sh_pair_1"], W["sh_pair_2k"] if k != 1.0 else w_pair(wst, OZ2), W["sh_alone_1k"] if k != 1.0 else w_alone(wst, OZ1)
        elif wk == "vinpair":
            w1, w2, wa = W["vin_pair_1k"], W["vin_pair_2k"], w_alone(I["vin_raw"], OZ1, ks)
        else:
            w1 = w2 = wa = None
        rows.append(dict(b=b, net=net, fr=fr, to=to, ends=ek, prot=prot, coord=coord, k=k, w1=w1, w2=w2, wa=wa, lim=R["limits"][lk][0],
                         lim_part=R["limits"][lk][1], lim_pinned=R["limits_pinned"][lk], field=fieldtxt))
    R["conductors"] = rows
    # board E's cross-section and board A's corridor
    R["e_pack_end"] = {"1 oz": 2 * W["pair_1k"], "2 oz": 2 * W["pair_2k"], "1 oz apart": 2 * W["alone_1k"]}
    R["e_shore"] = {"1 oz": 2 * W["sh_pair_1k"] + 2 * W["vin_pair_1k"], "2 oz": 2 * W["sh_pair_2k"] + 2 * W["vin_pair_2k"]}
    R["strip"] = S.outline(S.PINS["board_e"])[1]
    R["a_short"] = S.outline(S.PINS["board_a"])[1]
    R["gap_max"] = R["strip"] - R["e_pack_end"]["1 oz apart"]
    # the series parts
    r17, r19 = I["r17"], I["r19"]
    R["r17_limit_a"] = math.sqrt(r17["w"] / (r17["mohm"] / 1000.0))
    R["r19_limit_a"] = math.sqrt(r19["w"] / (r19["mohm"] / 1000.0))
    each = I["pair_mohm_each"] / 1000.0

    def pair_tj(a, air):
        return air + I["pair_rth"] * (a / 2.0) ** 2 * each

    def pair_i150(air):
        return 2.0 * math.sqrt((I["pair_limit"] - air) / (I["pair_rth"] * each))
    R["pair_i150"] = {"70": pair_i150(I["air_c"]), "t0": pair_i150(I["t0"])}
    # round 3: the battery FETs as L4-E11's round 9 drafts them, on E11-29 as its section 19c restates it
    nf, each_f, r17_ohm = len(I["fet_refs"]), I["fet_mohm_each"] / 1000.0, r17["mohm"] / 1000.0

    def band_rise(a):
        rr = [rise_pair(a, W["pair_1k"], OZ1, ks), rise_pair(a, W["pair_2k"], OZ2, ks)]
        return float("inf") if None in rr else max(rr)

    def fet_tj(a, air):
        """The hottest battery FET's junction, held: the air, the band's own rise at this current (the larger of the two copper
        weights), each FET's loss at an even split through the restated allowance, and R17's loss through its coupling."""
        return air + band_rise(a) + I["fet_rth"] * (a / nf) ** 2 * each_f + I["fet_r17c"] * a * a * r17_ohm

    def fet_i_limit(air):
        lo, hi = 0.0, 200.0
        for _ in range(80):
            mid = (lo + hi) / 2.0
            if fet_tj(mid, air) < I["fet_limit"]:
                lo = mid
            else:
                hi = mid
        return lo
    R["fet_i150"] = {"70": fet_i_limit(I["air_c"]), "t0": fet_i_limit(I["t0"])}
    R["fet_tj"] = {"cont": fet_tj(I["cont"], I["t0"]), "service": fet_tj(I["kd_a"], I["t0"]), "held": fet_tj(I["fet_i_held"], I["t0"]),
                   "band_held": band_rise(I["fet_i_held"])}
    R["pin_worst_ratio"] = None     # unbounded: the sheet prints a maximum and no minimum
    # the acceptance figures the dispositions quote
    R["pin_ratio_need"] = (blade / I["pin_a"] - 1.0) / (I["pins"] - 1)
    R["lim_pack_pin"] = min(R["limits_pinned"]["pack A"], R["limits_pinned"]["pack E"])
    R["i2t_allow_pack"] = i2t_to(W["pair_1k"] * t_out(OZ1), R["lim_pack_pin"], I) / (S_MAX * S_MAX)
    R["lim_sh"] = lim_shore
    R["i2t_allow_shore"] = i2t_to(W["sh_pair_1k"] * t_out(OZ1), lim_shore, I) / (S_MAX * S_MAX)
    # the owner's coordination table
    R["coord"] = coordination(R, I, W, F, pair_tj, fet_tj)
    # the predicates
    pred = predicates(R, I, W, F)
    R["pred"] = pred
    return R


# ------------------------------------------------------------------------------------------------ 6. the coordination table
def barrel_rise(amps, conv):
    """A barrel is an internal conductor (via_current): the rise at which the ruled internal fit rates its annulus at amps."""
    a = annulus(conv)
    lo, hi = 1e-4, 300.0
    if tc.conservative(a, hi)[0] < amps:
        return None
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if tc.conservative(a, mid)[0] < amps:
            lo = mid
        else:
            hi = mid
    return hi


def copper_reading(a, dur, w, oz, k, s, I):
    """(rise, how) for the decided band with its adjacent return: held is the steady rise; timed is the smaller of the steady
    rise and the governing face's adiabatic rise (the temperature reached before the clearance)."""
    st = rise_pair(a, w, oz, k)
    if dur is None:
        return st, "steady"
    ad = rise_adiabatic(a * a * dur * s * s, w * t_out(oz), I)
    if st is None or ad < st:
        return ad, "before clearance, adiabatic"
    return st, "steady (reached before clearance)"


def coordination(R, I, W, F, pair_tj, fet_tj):
    blade, shore, wst = I["blade_a"], I["shore_fuse_a"], I["shore_withstand_a"]
    ks = R["ks"]
    cells_a = I["cells_a"]
    lim_pack_fit = min(R["limits"]["pack A"][0], R["limits"]["pack E"][0])
    lim_pack_pin = min(R["limits_pinned"]["pack A"], R["limits_pinned"]["pack E"])
    lim_sh = R["limits"]["shore E"][0]
    env = envelope(blade, I["mini_rows"], I["pf_high"])
    senv = envelope(shore, I["shore_rows"], I["shore_stiff_a"])
    rows = []

    def rated(name, applied, rating, unit, dur):
        """A continuous rating covers any duration; above it, a time under 60 s needs a short-time rating, which no held sheet prints."""
        if applied <= rating or dur is None or dur >= 60.0:
            return (name, "%.3f %s" % (applied, unit), applied / rating)
        return (name, "%.3f %s for %s: over the continuous rating, no short-time rating held" % (applied, unit, dur_s(dur, "", I)), None)

    def pair_comp(a, dur, gauge_on):
        if dur is None or dur >= 60.0:
            tj = pair_tj(a, I["t0"])
            return ("Q39/Q40 (E11-29: %g K/W, %g mOhm each at 150 C)" % (I["pair_rth"], I["pair_mohm_each"]),
                    "TJ %s C held from %.2f C air (%s C from %g C)" % (f2(tj), I["t0"], f2(pair_tj(a, I["air_c"])), I["air_c"]), (tj - I["t0"]) / (I["pair_limit"] - I["t0"]))
        if gauge_on:
            return ("Q39/Q40", "L4-E11 15c: the gauge's levels at 150 C or under at E11-29's bar (CONDITIONAL on E11-29)", None)
        under = [(ww, zz) for ww, zz in I["pair_zjmb"] if ww <= dur]
        z = max(under)[1] if under else min(I["pair_zjmb"])[1]
        tj = I["t0"] + (a / 2.0) ** 2 * I["pair_mohm_each"] / 1000.0 * z
        return ("Q39/Q40 (INFERRED estimate: the 150 C RDS bound, the device's own Zth(j-mb) %g K/W, no board credit)" % z, "TJ about %s C for %s" % (f2(tj), dur_s(dur, "", I)),
                (tj - I["t0"]) / (I["pair_limit"] - I["t0"]))

    refs, nf, calls = ", ".join(I["fet_refs"]), len(I["fet_refs"]), []

    def fet_comp(a, dur, gauge_on):
        """The battery FETs as drafted (round 3): held rows on E11-29 as L4-E11's 19c restates it, with the band and R17 in
        place; timed rows with the gauge working carry no figure (19c withdrew the pair's timed targets and states none for
        the three); timed rows with the FETs failed short keep the device-alone estimate, each FET at its share."""
        if dur is None or dur >= 60.0:
            tj = fet_tj(a, I["t0"])
            return ("%s (E11-29 restated: %g K/W each with R17 apart, %g mOhm each at 150 C)" % (refs, I["fet_rth"], I["fet_mohm_each"]),
                    "TJ %s C held from %.2f C air, the band and R17 in place (%s C from %g C)" % (f2(tj), I["t0"], f2(fet_tj(a, I["air_c"])), I["air_c"]),
                    (tj - I["t0"]) / (I["fet_limit"] - I["t0"]))
        if gauge_on:
            return (refs, "L4-E11 19c: the pair's 1 s, 20 ms and 244 us targets are withdrawn and none is stated for the three; the held limit governs "
                          "behind the breaker (drafted), CONDITIONAL on E11-29", None)
        under = [(ww, zz) for ww, zz in I["pair_zjmb"] if ww <= dur]
        z = max(under)[1] if under else min(I["pair_zjmb"])[1]
        tj = I["t0"] + (a / nf) ** 2 * I["fet_mohm_each"] / 1000.0 * z
        return ("%s (INFERRED estimate: the 150 C RDS allowance, the device's own Zth(j-mb) %g K/W, no board credit)" % (refs, z), "TJ about %s C for %s" % (f2(tj), dur_s(dur, "", I)),
                (tj - I["t0"]) / (I["fet_limit"] - I["t0"]))

    def pack_comps(a, dur, cls, gauge_on):
        calls.append((a, dur, gauge_on))
        c = []
        for lab, w, oz in (("copper, 1 oz (%.2f mm a face)" % W["pair_1k"], W["pair_1k"], OZ1), ("copper, 2 oz (%.2f mm a face)" % W["pair_2k"], W["pair_2k"], OZ2)):
            r, how = copper_reading(a, dur, w, oz, ks, S_MAX, I)
            if cls in ("load", "transient", "coordination"):
                frac = None if r is None or r == float("inf") else r / 10.0
                txt = "%s K (%s) against 10 K" % (f2(r), how)
            else:
                frac = None if r is None or r == float("inf") else r / (lim_pack_pin - I["t0"])
                txt = "%s C (%s) against %g C (plating pinned; %g C as fitted)" % (f2(None if r is None else I["t0"] + r), how, lim_pack_pin, lim_pack_fit)
            c.append((lab, txt, frac))
        n = R["field_pack"]
        per = 0.5 * a / n
        r = rise_adiabatic(per * per * dur, annulus("inward"), I) if (dur is not None and dur < 1.0) else barrel_rise(per, "inward")
        frac = None if r is None or r == float("inf") else (r / 10.0 if cls in ("load", "transient", "coordination") else r / (lim_pack_pin - I["t0"]))
        c.append(("barrel field, %d of 0.4 mm (inward annulus)" % n, "%.2f A a barrel, %s K" % (per, f2(r)), frac))
        c.append(rated("R17 (%s, %g W; derating NOT HELD)" % (I["r17"]["mpn"], I["r17"]["w"]), a * a * I["r17"]["mohm"] / 1000.0, I["r17"]["w"], "W", dur))
        c.append(rated("XT60 (board E, %g A, %g C)" % (I["xt60_a"], I["xt60_max_c"]), a, I["xt60_a"], "A", dur))
        p = rated("dock contacts (%d Mill-Max, %g A each at a %g C rise)" % (I["pins"], I["pin_a"], I["pin_rise"]), a / I["pins"], I["pin_a"], "A a pin", dur)
        c.append((p[0], p[1] + " at an even split; the split is unbounded (%g mOhm maximum, no minimum)" % I["pin_mohm_max"], p[2]))
        c.append(fet_comp(a, dur, gauge_on))
        c.append(("Keystone 3568 holder", "no current rating printed (NOT HELD)", None))
        return c

    def limiting(c):
        """The component furthest over a printed rating; else one above its continuous rating with no short-time rating held;
        else the largest fraction."""
        held = [(f, n) for n, _t, f in c if f is not None]
        f, n = max(held)
        if f > 1.0 + 1e-9:
            return n, f
        unrated = [n2 for n2, t2, f2_ in c if f2_ is None and "no short-time rating held" in t2]
        if unrated:
            return unrated[0] + " (above its continuous rating, no short-time rating held)", float("nan")
        return n, f

    # R1, R2, R3
    rows.append(dict(case="10 A continuous", a=I["cont"], dur=None, basis="the pack's declared continuous current; the drafted states at 10.0 V reach %.2f A at PLAN, held under 10 A by the shedding control" % R["sustained_plan_base"][1],
                     device="none needed: a load", clearing="not a fault", comps=pack_comps(I["cont"], None, "load", True)))
    rows.append(dict(case="18 A for 60 s", a=I["kd_a"], dur=I["kd_s"], basis="PWR-F12 / D-11: every transmitter keyed, ended early above 18 A (judged steady: no transient credit)",
                     device="the key-down limit K1 (firmware); no hardware element acts at 18 A", clearing="none assured by hardware (60 s by firmware)",
                     comps=pack_comps(I["kd_a"], None, "transient", True)))
    rows.append(dict(case="the 25 A case, the gauge working", a=blade, dur=I["gauge"][1][2], basis="the blades' rating, which the chain's check 3 asks the copper for; a fault drawing it",
                     device="the gauge's OCD2 (%g A, %g s), firmware-configured" % (I["gauge"][1][1], I["gauge"][1][2]), clearing="%g s (the image's setting, not a hardware assurance)" % I["gauge"][1][2],
                     comps=pack_comps(blade, I["gauge"][1][2], "coordination", True)))
    rows.append(dict(case="the 25 A case, the gauge failed", a=blade, dur=None, basis="the same current with board P's FETs welded: the blade does not open (110 %% holds %g s at least); the rating is not a clamp" % I["mini_rows"][0][1],
                     device="none", clearing="none assured", comps=pack_comps(blade, None, "coordination", False)))
    top = blade * I["mini_rows"][1][0] / 100.0
    rows.append(dict(case="sustained overloads %g to %g A, no fuse opening assured" % (I["gauge"][0][1], top), a=top, dur=None,
                     basis="the gauge holds just under %g A with no trip; with it failed, no blade row opens below %g %%" % (I["gauge"][0][1], I["mini_rows"][1][0]),
                     device="the gauge's OCD1/OCD2 when it works (firmware-configured); none when it has failed", clearing="none assured",
                     comps=pack_comps(top, None, "backstop", False)))
    for lab, a, dur in env[1:]:
        rows.append(dict(case="board P's FETs failed short, blade %s" % lab, a=a, dur=dur, basis="a fault behind the welded FETs, read on the blade's monotone envelope",
                         device="the 25 A MINI blades (F2's element opens later at every current both tables state)", clearing="at most %g s (the row's maximum; the nominal melting I2t %g A2s is no clearing assurance)" % (dur, I["mini_25"]["i2t"]),
                         comps=pack_comps(a, dur, "backstop", False)))
    # the shore input with Q7 shorted
    for lab, a, dur in senv:
        c = []
        for clab, w, oz in (("copper, 1 oz (%.2f mm a face)" % W["sh_pair_1k"], W["sh_pair_1k"], OZ1), ("copper, 2 oz (%.2f mm a face)" % W["sh_pair_2k"], W["sh_pair_2k"], OZ2)):
            r, how = copper_reading(a, dur, w, oz, ks, S_MAX, I)
            frac = None if r is None or r == float("inf") else r / (lim_sh - I["t0"])
            c.append((clab, "%s C (%s) against %g C (J_DCIN's VH as drawn)" % (f2(None if r is None or r == float("inf") else I["t0"] + r), how, lim_sh), frac))
        nsh = R["field_shore"]
        per = 0.5 * a / nsh
        r = barrel_rise(per, "inward") if (dur is None or dur >= 1.0) else rise_adiabatic(per * per * dur, annulus("inward"), I)
        c.append(("barrel field, %d of 0.4 mm (inward annulus)" % nsh, "%.2f A a barrel, %s K" % (per, f2(r)),
                  None if r is None or r == float("inf") else r / (lim_sh - I["t0"])))
        c.append(rated("R19 (%s, %g W; derating NOT HELD)" % (I["r19"]["mpn"], I["r19"]["w"]), a * a * I["r19"]["mohm"] / 1000.0, I["r19"]["w"], "W", dur))
        c.append(rated("J_DCIN, JST VH (%g A with AWG 16; the drawn lead AWG 18 prints none; %g C)" % (I["vh_a"], I["vh_max_c"]), a, I["vh_a"], "A", dur))
        c.append(("Keystone 3568 holder", "no current rating printed (NOT HELD)", None))
        rows.append(dict(case="the shore input, Q7 shorted, fuse %s" % lab, a=a, dur=dur, basis="F1's monotone envelope (L4-E11 section 6) with the hot-swap's limit lost; a clamp failed short ahead of Q7 (one fault) meets the same envelope",
                         device="F1, %g A MINI" % shore, clearing="none assured" if dur is None else "at most %g s (the row's maximum)" % dur, comps=c))
    for i, r in enumerate(rows):
        r["limit_comp"], r["limit_frac"] = limiting(r["comps"])
        r["not_held"] = [n for n, _t, f in r["comps"] if f is None]
        r["disp"] = disposition(r, R, I)
        if i < len(calls):
            # round 3: the same row with the battery FETs as the pair it was first judged on (L4-E11's draft until its round 9)
            now = [x for x in r["comps"] if x[0].startswith(refs)][0]
            was = pair_comp(*calls[i])
            r["fet_now"], r["fet_was"] = now, was
            r["limit_was"] = limiting([was if x is now else x for x in r["comps"]])
    if len(calls) != len([r for r in rows if "fet_now" in r]) or any("fet_now" in r for r in rows[len(calls):]):
        refuse("the pack rows and their battery FET readings do not pair up")
    return rows


def disposition(r, R, I):
    """One disposition per row: (a) supported by the evidence, (b) a design correction with its owner, (c) a qualification
    gap with its specimen, acceptance and supplier task. A coupon never stands in for a known rating violation."""
    c = r["case"]
    pins = ("(c) the dock contacts' split: specimen, the four-pin set of the fitted lot (and E5's targets); acceptance, the lowest "
            "pin resistance at least %.3f of the highest so no pin passes %g A at %g A; supplier task, each pin's contact resistance at "
            "mid-stroke" % (R["pin_ratio_need"], I["pin_a"], I["blade_a"]))
    holder = "(b) the 3568 holder prints no current rating: a MINI 297/997 holder whose maker prints at least the coordination current, Layer 6/7"
    r17 = "(c) R17's maker sheet and its derating at the band's temperature (Layer 6)"
    refs = ", ".join(I["fet_refs"])
    if c == "10 A continuous":
        return ["(a) the copper at either weight, the barrels, R17's watts, the XT60 and the even split of the dock contacts", pins, holder, r17]
    if c == "18 A for 60 s":
        return ["(a) the copper at either weight (steady, no transient credit) and the barrels",
                "(c) %s at %.1f C from %.2f C at E11-29's restated allowance, the band and R17 in place: E11-29's specimen, measured with the band carrying "
                "its current and R17 dissipating (L4-E11 19c)" % (refs, R["fet_tj"]["service"], I["t0"]), pins, holder, r17]
    if c.startswith("the 25 A case, the gauge working"):
        return ["(a) the copper at either weight and the barrels within 10 K for the gauge's 1 s",
                "(c) %s for the gauge's 1 s: no timed target is held (L4-E11 19c withdrew the pair's); E11-29's specimen at the held limit, which governs "
                "behind the breaker (drafted)" % refs, pins, holder]
    if c.startswith("the 25 A case, the gauge failed"):
        return ["(a) the copper at either weight at 10 K (the width is sized to it)",
                "(b) %s pass %g C held (the limit is met at %.2f A from %.2f C): W4DP-F2's element (the battery stream with L4-E11)" % (
                    refs, I["fet_limit"], R["fet_i150"]["t0"], I["t0"]), pins, holder, r17]
    if c.startswith("sustained overloads"):
        return ["(b) W4DP-F2: %s pass %g C at %.2f A held from %.2f C with the band and R17 in place (%.2f A from the +%g C line); R17 passes %g W at "
                "%.2f A; the XT60 passes %g A; no firmware-independent element opens in this band (the battery stream with L4-E11)" % (
                    refs, I["fet_limit"], R["fet_i150"]["t0"], I["t0"], R["fet_i150"]["70"], I["air_c"], I["r17"]["w"], R["r17_limit_a"], I["xt60_a"]), holder]
    if c.startswith("board P's FETs failed short"):
        cu = [x for x in r["comps"] if x[0].startswith("copper, 1 oz")][0]
        out = []
        if r["dur"] is not None and r["dur"] >= 60.0:
            out.append("(b) W4DP-F2's element removes the row: R17, the XT60, the dock contacts and %s are over their printed "
                       "ratings or limit for up to the row's time (the battery stream with L4-E11; a coupon does not stand in for it)" % refs)
        else:
            out.append("(b) W4DP-F2's element removes the row: the barrel field passes the band's limit, and R17, the XT60 and the "
                       "dock contacts carry currents above their continuous ratings with no short-time rating held (the battery "
                       "stream with L4-E11; a coupon does not stand in for it)")
        if cu[2] is not None and cu[2] <= 1.0:
            out.append("(a) the copper bands at either weight, with the blade's plating pinned")
        if R["blade_c"]["fitted"] < R["lim_pack_pin"] and cu[2] is not None and I["t0"] + cu[2] * (R["lim_pack_pin"] - I["t0"]) > R["blade_c"]["fitted"]:
            out.append("(b) the blade's plating pinned to silver, 0297025.%s (Layer 6; apply_blade_plating_l9stk.py): as fitted the tin "
                       "part's %g C is passed" % (I["mini_ag_order"], R["blade_c"]["fitted"]))
        if r["dur"] is not None and r["dur"] <= 0.1:
            out.append("(c) the blade's total clearing I2t at %g A and 16.8 V (not printed; %g A2s is nominal melting): specimen, the fitted lot "
                       "in the 3568 holder on a band coupon; acceptance, at most %.0f A2s (the governing 1 oz face to %g C from %.2f C); supplier "
                       "task, Littelfuse's clearing data or a short-circuit test" % (I["pf_high"], I["mini_25"]["i2t"], R["i2t_allow_pack"], R["lim_pack_pin"], I["t0"]))
        return out
    if c.startswith("the shore input"):
        out = []
        if r["a"] > I["vh_a"]:
            out.append("(b) J_DCIN over the VH's %g A: L4-E11's D-06 30 A class connector (L4-E11, Layer 7)" % I["vh_a"])
        if r["a"] > R["r19_limit_a"]:
            out.append("(b) R19 over its %g W from %.2f A: a shunt whose rating covers %g A held (L4-E11)" % (I["r19"]["w"], R["r19_limit_a"], I["shore_withstand_a"]))
        if r["dur"] is not None and r["dur"] <= 0.1:
            out.append("(c) F1's total clearing I2t at %g A and 58 V DC (E11-16, L4-E11): acceptance at most %.0f A2s on the governing 1 oz face to %g C" % (
                I["shore_stiff_a"], R["i2t_allow_shore"], R["lim_sh"]))
        out.append(holder)
        if not out[:-1]:
            out.insert(0, "(a) the copper at either weight, R19 and the barrels")
        return out
    return ["(c) unclassified"]


def f2(x):
    if x is None:
        return "-"
    if x == float("inf") or x > 9999:
        return ">9999"
    return "%.2f" % x


# ------------------------------------------------------------------------------------------------ the predicates
def predicates(R, I, W, F):
    def row(k, start):
        return [x for x in F[k]["rows"] if x["lab"].startswith(start)][0]
    C = R["coord"]
    over = [r for r in C if r["limit_frac"] != r["limit_frac"] or r["limit_frac"] > 1.0 + 1e-9]
    return {
        "each face rated alone reproduces the candidate's widths: 6.72, 11.95, 12.26 and 14.60 mm":
            [round(W[k], 2) for k in ("svc_even", "svc_one_2oz", "cand_even", "cand_smax")] == [6.72, 11.95, 12.26, 14.60],
        "the candidate's two 12.26 mm faces as one conductor read 18.9 K at 25 A and 12.0 K at 20 A": round(row("C1", "25 A held")["r"], 1) == 18.9 and round(row("C1", "held just under")["r"], 1) == 12.0,
        "the candidate's 600 s point reads 147.1 C from the +70 C line as one conductor": round(I["air_c"] + row("C1", "gauge failed: blade 135 to 200")["r"], 1) == 147.1,
        "two 1 oz faces as one conductor need 21.81 mm each at 25 A": round(W["alone_1"], 2) == 21.81,
        "the decided pair at 1 oz and at 2 oz is at 10 K at 25 A": all(abs(row(k, "25 A held")["r"] - 10.0) < 1e-3 for k in ("D1", "D2")),
        "on D1 and D2 every load, transient, gauge level and the 25 A case is within 10 K":
            all(x["ok"] for k in ("D1", "D2") for x in F[k]["rows"] if x["cls"] in ("load", "transient", "gauge", "coordination")),
        "an uneven split of 0.55 dissipates one percent more than an even one": abs(R["ks"] ** 2 - 1.01) < 1e-9,
        "board E's pack end at 1 oz with its return adjacent exceeds the strip; at 2 oz it fits": R["e_pack_end"]["1 oz"] > R["strip"] > R["e_pack_end"]["2 oz"],
        "the blade's plating is not pinned in the tree, so the fitted limit is the tin blade's": (not I["blade_pinned"]) and R["blade_c"]["fitted"] == I["mini_sn_max_c"],
        "the outward annulus count is via_current's and the inward count is no smaller":
            all(v["inward"] >= v["outward"] for v in R["thermal_barrels"].values()),
        "the pair L4-E11 drafted until its round 9 passed 150 C held between the gauge's OCD1 and the cells' continuous rating": I["gauge"][0][1] < R["pair_i150"]["70"] < I["cells_a"],
        "the battery FETs as drafted now meet their junction limit between the gauge's OCD1 and the blades' least assured opening":
            I["gauge"][0][1] < R["fet_i150"]["t0"] < I["blade_a"] * I["mini_rows"][1][0] / 100.0,
        "L4-E11's restated E11-29 starts from this record's worst inside air and reads its limit at its held current, to 0.05 K":
            abs(I["fet_t0"] - I["t0"]) < 1e-9 and abs(R["fet_tj"]["held"] - I["fet_limit"]) < 0.05,
        "the target L4-E11 withdrew is the pair's target this record read, and the allowance per FET is the pair's bound":
            I["pair_rth_withdrawn"] == I["pair_rth"] and I["fet_mohm_each"] == I["pair_mohm_each"],
        "every coordination row carries a disposition, and every row over a printed rating a design correction or a gap":
            all(r["disp"] for r in C) and all(any(d.startswith("(b)") or d.startswith("(c)") for d in r["disp"]) for r in over),
        "with the gauge failed the 25 A case is over a printed rating": [r for r in C if r["case"].startswith("the 25 A case, the gauge failed")][0]["limit_frac"] > 1.0,
        "the 10 A continuous row is within every held rating": [r for r in C if r["case"] == "10 A continuous"][0]["limit_frac"] <= 1.0,
        "R17 reaches its rating inside the blade's no-opening band": I["blade_a"] < R["r17_limit_a"] < I["blade_a"] * I["mini_rows"][1][0] / 100.0,
        "R19 reaches its rating inside the shore fuse's 600 s interval": I["shore_fuse_a"] * I["shore_rows"][1][0] / 100.0 < R["r19_limit_a"] < I["shore_fuse_a"] * I["shore_rows"][2][0] / 100.0,
        "the transfer field's split count falls with length":
            all(x[4][i][1] >= x[4][i + 1][1] and x[4][i][2] >= x[4][i + 1][2] for x in R["transfer"] for i in range(len(LENGTHS) - 1)),
        "with one barrel the part's face carries more than the governing share at every tabled length": all(v > S_MAX for v in R["no_field"].values()),
        "VIN_RAW's declared current covers the tracker's minimum valley limit": I["vin_raw"] >= I["trk_valley"],
    }


# ------------------------------------------------------------------------------------------------ render
def dur_s(d, cls, I):
    if cls == "pulse":
        return "tau %gus" % (I["dock_tau"] * 1e6)
    if d is None:
        return "held"
    if d >= 1.0:
        return "%gs" % d
    return ("%.3gms" % (d * 1e3)) if d >= 0.001 else ("%.0fus" % (d * 1e6))


def render(R):
    I, W, F = R["in"], R["w"], R["fam"]
    L = []
    P = L.append
    P("l9stk_copper: the pack path's copper on boards A and E, on its basis (record l9stk, MESHSAT-1357), revised after the check")
    P("COPPER: NOT CONFIRMED. A candidate copper-sizing result, not completed fault-protection verification. Desk arithmetic on")
    P("committed files: nothing was built, routed, measured or bought, and no figure below is a measurement.")
    P("Round 3 (4 October 2026): the battery FETs are read from L4-E11's round 9 draft as it is, %s (%d x BUK6Y10-30PX), and judged on" % (", ".join(I["fet_refs"]), len(I["fet_refs"])))
    P("E11-29 as its section 19c restates it; no width, limit, split, field or barrel figure moved; the rows that moved are in section 9a.")
    P("")
    P("0. PINS (path  sha256/16)")
    for k, (p, s) in sorted(R["pins"].items()):
        P("   %-15s %s  sha256 %s" % (k, p, s))
    P("")
    P("1. THE CURRENTS BY CLASS (each from its pinned source)")
    P("   continuous: the pack's declared %.1f A; the drafted states at the gauge's 10.0 V floor (record l9pwr section 6): the largest" % I["cont"])
    P("     sustained PLAN %.2f A (%s), at HIGH %.2f A (%s), with the outlets %.2f A (%s); above %.1f A the shedding control holds a state" % (
        R["sustained_plan_base"][1], R["sustained_plan_base"][0], R["sustained_high_base"][2], R["sustained_high_base"][0],
        R["sustained_plan_max"][1], R["sustained_plan_max"][0], I["cont"]))
    P("   transient: %.1f A for at most %.0f s (PWR-F12, every transmitter; ended early above %.1f A by firmware), judged as if steady; the" % (I["kd_a"], I["kd_s"], I["kd_a"]))
    P("     largest key-down row %.2f A at PLAN at 10.0 V (%s); the PA's key-on step %.1f to %.1f A; the docking pulse %.1f A peak, %.1f us" % (
        R["keydown_plan_max"][1], R["keydown_plan_max"][0], I["step"][0], I["step"][1], I["dock_pk"], I["dock_tau"] * 1e6))
    P("     time constant, I2t %.4f A2s, once per docking (L4-E11 E11-30)" % (I["dock_pk"] ** 2 * I["dock_tau"] / 2.0))
    P("   fault, the gauge working (the image): " + "; ".join("%s %.1f A, %s" % (n, a, ("%g s" % s) if s >= 0.001 else ("%g us" % (s * 1e6))) for n, a, s in I["gauge"]))
    P("     so %.1f A may be held with no trip; every level is firmware-configured (W4DP-F2)" % I["gauge"][0][1])
    P("   fault, board P's FETs failed short: the %.0f A MINI blades read monotone (Littelfuse 297): " % I["blade_a"] + "; ".join(
        "%s" % lab for lab, _a, _d in envelope(I["blade_a"], I["mini_rows"], I["pf_high"])))
    P("     nominal melting I2t %g A2s (no clearing I2t printed); F2 (Eaton SCF9550, %g A) %g %% for %g h minimum, %g %% within %g s" % (
        I["mini_25"]["i2t"], I["f2"]["a"], I["f2"]["hold_pct"], I["f2"]["hold_h"], I["f2"]["open_pct"], I["f2"]["open_s"]))
    P("     the cells' continuous rating at 3P: %.0f A (pcb_pack_protection.yaml); prospective fault %.0f to %.0f A" % (I["cells_a"], I["pf_low"], I["pf_high"]))
    P("   the shore input: %.2f A continuous; F1 %g A MINI read monotone: " % (I["veh"], I["shore_fuse_a"]) + "; ".join(lab for lab, _a, _d in envelope(I["shore_fuse_a"], I["shore_rows"], I["shore_stiff_a"])))
    P("     (L4-E11 section 6); its D-06 selection: board E's copper from J_DCIN to F1 to the clamps at least %g A continuous" % I["shore_withstand_a"])
    P("   VIN_RAW: declared %.2f A; the tracker's minimum valley limit %.1f A; with the hot-swap %.2f A until its fault time" % (I["vin_raw"], I["trk_valley"], I["veh"] + I["trk_valley"]))
    P("   the inside air: the consolidation's +%g C line (with the hold); L4-E12's E3-O %.2f C and E5's dwell %.2f C (steady, without the" % (I["air_c"], I["air_e3o"], I["air_e5"]))
    P("     hold): every final temperature below starts from %.2f C" % I["t0"])
    P("")
    P("2. THE METHOD (decision 35's model, applied to the copper as it is stacked)")
    P("   rating: track_current.conservative at each area, outer copper at EXTERNAL_FACTOR %.1f once; widths track_current.width_for_current" % tc.EXTERNAL_FACTOR)
    P("     at its 10 K default; the fits' data: IPC-2152 to %.0f A and %.0f K, CNES to %.0f A (ECSS-Q-ST-70-12C D.2, D.3)" % (I["ipc2152_a"], I["ipc2152_k"], I["cnes_a"]))
    P("   the two outer faces of a band share one footprint and its two cooling surfaces, so they are ONE conductor of their combined")
    P("     section (a 1 oz pair is a 2 oz conductor of the band's width); a band and its return run side by side at both connector ends,")
    P("     so the pair is ONE conductor of twice the width and both faces' copper carrying their combined dissipation (the current %s x I)" % "sqrt(2 (kf^2 + kr^2))")
    P("     and its width per band per face is half of width_for_current at that current and twice the face weight; no credit is held for")
    P("     laying the return apart, so the widths 'apart' are printed for comparison only")
    P("   an uneven split s between the faces dissipates k^2 = 2 (s^2 + (1 - s)^2) of an even one: %.4f at s %.2f" % (R["ks"] ** 2, S_MAX))
    P("   before a timed clearance: the smaller of the steady rise and the governing face's adiabatic rise (Onderdonk, constants %.0f and" % I["k234"])
    P("     %.0f, copper melting %.0f C, as records/l7pwr/inputs holds it); a constant current never passes its steady rise" % (I["k33"], I["t_melt"]))
    P("   the limit of a band: the lowest printed limit of the parts it joins (the laminate's is NOT HELD):")
    for k, (lim, part, parts) in sorted(R["limits"].items()):
        P("     %-8s %g C, %s (%s); with the blade's plating pinned %g C" % (k, lim, part, "; ".join("%s %g C" % x for x in parts), R["limits_pinned"][k]))
    P("     the blade: fitted as %s; silver terminals %g C, tin %g C; the MPN that pins silver: 0297025.%s (tin: 0297025.%s)" % (
        I["blade_entry"]["fitted"], I["mini_max_c"], I["mini_sn_max_c"], I["mini_ag_order"], I["mini_sn_order"]))
    P("     the parts with no printed limit held: R17 (%s), R19 (%s), the Mill-Max pins' range (unreadable in the filed page)" % (I["r17"]["mpn"], I["r19"]["mpn"]))
    P("   criteria (SESSION): the continuous load, the transient, every gauge level and the 25 A case within the ruled 10 K; every")
    P("     backstop interval and short at or under the band's limit from %.2f C; every part against its printed rating" % I["t0"])
    P("")
    P("3. THE SPLIT, THE TRANSFER FIELDS AND THE BARRELS")
    P("   through-hole at both ends: equal faces share evenly; a one-face part at one end: the part's face carries (Rb + Rv) / (2 Rb + Rv);")
    P("     at both ends (Rb + 2 Rv) / (2 Rb + 2 Rv); stitching along such a band moves current onto the part's face early, so the transfer")
    P("     barrels sit in a field at the part. With the faces as one conductor the split matters through its dissipation: one barrel of")
    P("     %.4f mm2 is worth %.1f mm of a %.2f mm band, and with one barrel the part's face carries %s (k %s)" % (
        R["barrel"]["outward"]["area"], R["barrel_mm_eq"], W["pair_1k"], ", ".join("%.2f at %.0f mm" % (v, Lx) for Lx, v in sorted(R["no_field"].items())),
        ", ".join("%.3f" % R["no_field_k"][Lx] for Lx in sorted(R["no_field_k"]))))
    P("   the barrel's annulus, two conventions (via_current's 18 um average plating):")
    for conv, v in R["barrel"].items():
        P("     %-8s %.5f mm2, %.3f A at 10 K; thermal counts at half the coordination current: pack %d, shore %d, VIN_RAW %d" % (
            conv, v["area"], v["amps"], R["thermal_barrels"]["pack"][conv], R["thermal_barrels"]["shore"][conv], R["thermal_barrels"]["vin"][conv]))
    P("     (outward: the 0.4 mm is the finished hole and the plating lies outside it, via_current's pi (d + t) t; inward: the 0.4 mm is the")
    P("     drill and the plating lies inside, pi (d - t) t; the field takes the inward count until the fabricator states which)")
    P("   the field at each one-face end: the inward count at 10 K (pack %d, shore %d) or the count that holds the blade's 600 s point within" % (
        R["thermal_barrels"]["pack"]["inward"], R["thermal_barrels"]["shore"]["inward"]))
    P("     the band's limit (pack: every interval to the blade's 600 s point, %d; shore: every interval to F1's 0.5 s one, %d), whichever" % (
        R["field_pack_600"], R["field_shore_600"]))
    P("     is more: pack %d, shore %d; and the split count below where it is more" % (R["field_pack"], R["field_shore"]))
    P("   the split count each one-face end needs for the part's face to carry at most %.2f (one end / both ends):" % S_MAX)
    for name, w, hh, oz, rows in R["transfer"]:
        P("     %-22s %.2f mm, %.4f mm board: %s" % (name, w, hh, ", ".join("%.0f mm %d / %d" % (Lx, a, b) for Lx, a, b in rows)))
    P("")
    P("4. THE BAND FAMILIES: each class on the governing conductor, final temperature from %.2f C, verdict against 10 K or the limit" % I["t0"])
    for key in ("A1", "C1", "C2", "D1", "D2", "D3", "H1", "H2"):
        f = F[key]
        P("   %s %s: limit %g C as fitted, %g C with the blade's plating pinned; the governing face's fusing I2t %.0f A2s" % (
            key, f["label"], f["lim"], f["lim_pin"], f["fusing"]))
        for x in f["rows"]:
            P("     %-74s %7.2f A %-10s steady %-7s adiabatic %-7s -> %-7s %s" % (
                x["lab"], x["a"], dur_s(x["dur"], x["cls"], I), f2(x["st"]), f2(x["ad"]), f2(x["r"]),
                (("within" if x["ok"] else "OVER") + " 10 K") if x["cls"] in ("load", "transient", "gauge", "coordination") else
                "%s C: %s as fitted, %s pinned" % (f2(x["T"]), "within" if x["ok"] else "OVER", "within" if x["ok_pin"] else "OVER")))
    v = R["vin"]
    P("   V  VIN_RAW %.2f mm a face, 1 oz, with its adjacent return:" % v["w"])
    for x in v["rows"]:
        P("     %-74s %7.2f A held       steady %-7s -> %s" % (x["lab"], x["a"], f2(x["st"]), "within 10 K" if x["ok"] else "OVER 10 K"))
    P("     both sources' limits, %.2f A, for at most the hot-swap's fault time: %.2f K steady (an upper bound on any duration)" % (v["sum_a"], v["sum_rise"]))
    P("")
    P("5. THE CONDUCTORS (TH through-hole, 1F one face; the width on each face with the adjacent return as one conductor)")
    for c in R["conductors"]:
        P("   %s %-22s %s to %s [%s]; %s; coordination %.2f A, k %.3f" % (c["b"], c["net"], c["fr"], c["to"], c["ends"], c["prot"], c["coord"], c["k"]))
        if c["w1"] is None:
            P("       a one-face hop between two one-face parts: at least the larger land, as short as the parts allow; %s" % c["field"])
        else:
            P("       1 oz %.2f mm, 2 oz %.2f mm (apart, 1 oz, no credit: %.2f mm); field: %s; limit %g C (%s), %g C pinned" % (
                c["w1"], c["w2"], c["wa"], c["field"], c["lim"], c["lim_part"], c["lim_pinned"]))
    P("")
    P("6. THE WIDTHS EACH CURRENT ASKS AND THE WIDTHS QUOTED, JUDGED")
    P("   the width on each face at 10 K: two 1 oz faces as one conductor, return apart / with the return adjacent, 1 oz / 2 oz:")
    for lab, a, wa, w1, w2 in R["ask"]:
        P("     %-52s %6.2f A  %6.2f / %6.2f / %6.2f mm" % (lab, a, wa, w1, w2))
    c1, a1 = F["C1"]["rows"], F["A1"]["rows"]
    P("   6.72 mm a face (l9stk at 18 A, each face alone): with its return %s K at 18 A, %s K at 25 A" % (
        f2([x for x in a1 if x["lab"].startswith("18 A")][0]["r"]), f2([x for x in a1 if x["lab"].startswith("25 A held")][0]["r"])))
    P("   12.26 mm a face (f76564eb, each face alone at 12.5 A): as one conductor %s K at 25 A, %s K at the gauge's held 20 A, %.1f C at the" % (
        f2([x for x in c1 if x["lab"].startswith("25 A held")][0]["r"]), f2([x for x in c1 if x["lab"].startswith("held just under")][0]["r"]),
        I["air_c"] + [x for x in c1 if x["lab"].startswith("gauge failed: blade 135 to 200")][0]["r"]))
    P("     blade's 600 s point from the +%g C line (%s C from %.2f C); with its return adjacent %s K at 25 A" % (
        I["air_c"], f2([x for x in c1 if x["lab"].startswith("gauge failed: blade 135 to 200")][0]["T"]), I["t0"],
        f2([x for x in F["C2"]["rows"] if x["lab"].startswith("25 A held")][0]["r"])))
    P("   14.60 mm, 11.95 mm on one 2 oz face, 23.44 mm and 2.76 mm: rated on the same single-face basis, superseded by section 5")
    P("")
    P("7. THE SERIES PARTS AND THE LANDS")
    P("   R17 (%s, %g mOhm, %g W, %s; derating NOT HELD): its %g W at %.2f A" % (I["r17"]["mpn"], I["r17"]["mohm"], I["r17"]["w"], I["r17"]["code"], I["r17"]["w"], R["r17_limit_a"]))
    P("   R19 (%s, %g mOhm, %g W, %s; derating NOT HELD): its %g W at %.2f A" % (I["r19"]["mpn"], I["r19"]["mohm"], I["r19"]["w"], I["r19"]["code"], I["r19"]["w"], R["r19_limit_a"]))
    P("   %s, the battery FETs as L4-E11's round 9 drafts them (%d x BUK6Y10-30PX; E11-29 restated in its 19c: each FET's (Zself + 2 Zmut) at most" % (
        ", ".join(I["fet_refs"]), len(I["fet_refs"])))
    P("     %g K/W with R17 apart, R17's coupling at most %g K/W; %g mOhm each at 150 C): %g C held at %.2f A from %.2f C with the band (%.2f K) and" % (
        I["fet_rth"], I["fet_r17c"], I["fet_mohm_each"], I["fet_limit"], R["fet_i150"]["t0"], I["t0"], R["fet_tj"]["band_held"]))
    P("     R17 in place (%.2f A from the +%g C line); %.1f C at %g A, %.1f C at the %g A service; L4-E11 prints %g A, which reads %.2f C here" % (
        R["fet_i150"]["70"], I["air_c"], R["fet_tj"]["cont"], I["cont"], R["fet_tj"]["service"], I["kd_a"], I["fet_i_held"], R["fet_tj"]["held"]))
    P("   dated, the pair Q39/Q40 as drafted until L4-E11's round 9 (E11-29's former %g K/W, withdrawn in its 19c; FETs only): 150 C held at" % I["pair_rth"])
    P("     %.2f A from +%g C, %.2f A from %.2f C; L4-E11's 18 A for 60 s %.1f C and 20 A held %.0f C (from +%g C): W4DP-F2 was found on it" % (
        R["pair_i150"]["70"], I["air_c"], R["pair_i150"]["t0"], I["t0"], I["pair_tj_18"], I["pair_tj_20"], I["air_c"]))
    P("   the XT60: %g A, %g A instantaneous (no duration), %g C; the JST VH (J_DCIN as drawn): %g A with AWG 16, %g C" % (I["xt60_a"], I["xt60_peak"], I["xt60_max_c"], I["vh_a"], I["vh_max_c"]))
    P("   the dock contacts: %d Mill-Max pins, %g A each at a %g C rise, %g mOhm maximum and no minimum, so the split is unbounded; no pin" % (I["pins"], I["pin_a"], I["pin_rise"], I["pin_mohm_max"]))
    P("     passes %g A at %g A only if the lowest pin resistance is at least %.3f of the highest" % (I["pin_a"], I["blade_a"], R["pin_ratio_need"]))
    P("   the Keystone 3568 holder: no current rating printed; UL temperature %g C" % I["holder_max_c"])
    P("")
    P("8. BOARD E'S CROSS-SECTION AND BOARD A'S CORRIDOR (each face)")
    P("   board E's pack end, the forward band and its return: 1 oz %.2f mm, 2 oz %.2f mm, 1 oz laid apart (no credit) %.2f mm plus the gap;" % (
        R["e_pack_end"]["1 oz"], R["e_pack_end"]["2 oz"], R["e_pack_end"]["1 oz apart"]))
    P("     the strip is %.0f mm: at 1 oz the pair cannot be laid side by side" % R["strip"])
    P("   the zero-cost route, (L9STK CU)'s option (4): the band and its return each %.2f mm at 1 oz, laid apart, fit the strip with a gap up to" % W["alone_1k"])
    P("     %.2f mm; decision 35's model holds no term for the distance between two conductors, so no gap is credited as apart: the route" % R["gap_max"])
    P("     needs a coupon (a board E strip at 1 oz with the band and its return at the gap carrying %g A, each at most 10 K)" % I["blade_a"])
    P("   board E's shore chain and VIN_RAW, each with its return, in one section: 1 oz %.2f mm, 2 oz %.2f mm" % (R["e_shore"]["1 oz"], R["e_shore"]["2 oz"]))
    P("   board A's pack corridor, forward and return: 1 oz %.2f mm, 2 oz %.2f mm, of the board's %.0f mm short side" % (2 * W["pair_1k"], 2 * W["pair_2k"], R["a_short"]))
    P("")
    P("9. THE COORDINATION TABLE (the owner's rows; the limiting component is the largest fraction of a printed rating or limit)")
    for r in R["coord"]:
        P("   %s: %.2f A, %s" % (r["case"], r["a"], dur_s(r["dur"], "", I)))
        P("     basis: %s" % r["basis"])
        P("     protective device: %s; assured maximum clearing: %s" % (r["device"], r["clearing"]))
        for n, t, f in r["comps"]:
            P("       %-62s %s%s" % (n, t, "" if f is None else "  [%.2f]" % f))
        if r["limit_frac"] != r["limit_frac"]:
            P("     limiting: %s" % r["limit_comp"])
        else:
            P("     limiting: %s at %.2f of its rating%s" % (r["limit_comp"], r["limit_frac"], " (OVER)" if r["limit_frac"] > 1.0 + 1e-9 else ""))
        for d in r["disp"]:
            P("     disposition: %s" % d)
    P("   W4DP-F2 stays open; its closure is a current-and-time criterion for every series part with board P's FETs welded and no firmware,")
    P("     not one current: the pair it was found on passed 150 C held at %.2f A from +%g C and %.2f A from %.2f C (derived on E11-29's" % (R["pair_i150"]["70"], I["air_c"], R["pair_i150"]["t0"], I["t0"]))
    P("     former target), under the cells' %.0f A; the three drafted since meet their limit at %.2f A from %.2f C, under the blades' least" % (I["cells_a"], R["fet_i150"]["t0"], I["t0"]))
    P("     assured opening %.2f A; the selected element and its table are l9stk_protection.py's (the page's section 15)" % (I["blade_a"] * I["mini_rows"][1][0] / 100.0))
    P("")
    P("9a. THE BATTERY FETS' ROWS: THE CIRCUIT AS DRAFTED NOW AGAINST THE PAIR THE TABLE WAS FIRST JUDGED ON (round 3)")
    P("   the cause: L4-E11's round 9 draft writes %s (it wrote Q39 and Q40), and its 19c restates E11-29 from the pair's %g K/W (FETs only," % (", ".join(I["fet_refs"]), I["pair_rth"]))
    P("     from the +%g C line) to %g K/W a FET with R17 apart, the band and R17 in place, from %.2f C; both columns are computed here" % (I["air_c"], I["fet_rth"], I["t0"]))
    for r in R["coord"]:
        if "fet_now" not in r:
            continue
        was, now = r["fet_was"], r["fet_now"]

        def lim(x):
            return x[0] if x[1] != x[1] else "%s at %.2f%s" % (x[0], x[1], " (OVER)" if x[1] > 1.0 + 1e-9 else "")
        P("   %s: %.2f A, %s" % (r["case"], r["a"], dur_s(r["dur"], "", I)))
        P("     the pair:  %s%s" % (was[1], "" if was[2] is None else "  [%.2f]" % was[2]))
        P("     now:       %s%s" % (now[1], "" if now[2] is None else "  [%.2f]" % now[2]))
        lw, ln = lim(r["limit_was"]), lim((r["limit_comp"], r["limit_frac"]))
        P("     limiting:  %s" % ("unchanged: %s" % ln if lw == ln else "was %s; now %s" % (lw, ln)))
    P("   not moved by the draft's change: every width, limit, split, transfer field and barrel count of sections 2 to 8, and every copper, barrel,")
    P("     R17, XT60, dock contact, R19 and J_DCIN reading of section 9 (none reads the battery FETs)")
    P("")
    P("10. PREDICATES")
    for k, val in R["pred"].items():
        P("   %-120s %s" % (k, "yes" if val else "NO"))
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    return 1 if [k for k, v in R["pred"].items() if not v] else 0


if __name__ == "__main__":
    sys.exit(main())
