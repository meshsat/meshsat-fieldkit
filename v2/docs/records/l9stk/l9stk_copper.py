#!/usr/bin/env python3
"""Layer 9 item 9.12, record l9stk, the copper question (MESHSAT-1357, 4 October 2026): the pack path's copper on boards A
and E, sized on its actual basis.

Desk arithmetic on committed files. Nothing here was built, routed, measured or bought. It reads its inputs, every one
pinned by sha256 in section 0, and prints:

  1. the currents each conductor carries, by class: the continuous load, the transient demand with its duration, and the
     fault current with the time its protection takes to clear it (the gauge's image levels; with the gauge failed, the
     25 A MINI blades' time-current rows and their I2t; the shore input's 10 A blade; the docking pulse);
  2. the rise each class gives in decision 35's model (track_current.conservative, the most conservative of the three
     ECSS-Q-ST-70-12C Annex D fits, outer copper at the external factor), and the adiabatic rise of a timed event
     (Onderdonk's relation as the tree holds it in records/l7pwr/inputs), the rise of a timed event being the smaller of
     the two, because a constant current never takes a conductor past its steady rise;
  3. the split between the two outer faces derived from resistance and the transfer barrels (not assumed 50/50), and the
     inner planes' share as record l9stk's plane_share screens it;
  4. the band families, each class's rise and final temperature on each, and the widths quoted in the conflict judged;
  5. the conductors of the pack path and the shore input on A and E, one row each, with their bottlenecks;
  6. the predicates test_l9stk.py holds.

Run from the repository root: python3 v2/docs/records/l9stk/l9stk_copper.py
The committed output is regenerated only through _bin/regen_out.py. Stdlib, PyYAML, pdftotext (poppler) and the tool
modules; no KiCad, no network, no date, no host name, so a second run prints the same bytes.
"""
import hashlib
import importlib.util
import json
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
    "l4e11_out": "v2/docs/records/l4e11/l4e11_power.out",
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
    try:
        r = subprocess.run(["pdftotext", "-layout", rel(PINS[key]), "-"], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read %s (%s)" % (PINS[key], e))
    return r.stdout.decode("utf-8", "replace")


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
    m = need(l, r'\(r"\^5mOhm 1% 2512 \\\(RSR", "R_2512"\): "(C\d+)",\s+# [^\n]*?5 mOhm 1 % (\d+) W, board A R17', "R17's part")
    I["r17"] = dict(code=m.group(1), w=float(m.group(2)), mohm=5.0)
    m = need(l, r'\(r"\^10mOhm 1% 2512", "R_2512"\): "(C\d+)",\s+# [^\n]*?(\d+) W,', "R19's part")
    I["r19"] = dict(code=m.group(1), w=float(m.group(2)), mohm=10.0)
    a = text("gen_sch_a")
    need(a, r'r\("R17", "5mOhm 1% 2512 \(RSR, charge current sense\)", "VBAT", "CELL_FUSED", "RS2512"\)', "R17 in the pack path")
    need(a, r'part\("F1", "Device", "Fuse", "25 A mini blade \(Keystone 3568 holder\): pack node to the RSR shunt", "FUSE", \{"1": "CELL\+", "2": "CELL_FUSED"\}\)', "board A's F1")
    if not re.search(r'for k in range\(1, %d\):\s*\n\s*part\("J_CP%%d" %% k' % (I["pins"] + 1), a):
        refuse("board A's dock pins are not %d" % I["pins"])
    need(text("charger_draft"), r'nfet\(_qb, \\"BUK6Y10-30PX 30 V P-FET \(the BQ25730\'s battery FET, one of two in parallel: S on VSYS, D toward RSR\)\\", \\"CH_BATDRV\\", \\"CH_BATQ\\", \\"VBAT\\"', "the pair's draft")
    m = need(o, r"\(Q-c\) Nexperia BUK6Y10-30P, two in parallel \(MAKER, INFERRED\):\n\s+printed maxima:[^\n]*\n\s+limit 150 C[^\n]*?gate factor [0-9.]+, ([0-9.]+) mOhm per FET", "the pair's RDS(on) bound")
    I["pair_mohm_each"] = float(m.group(1))
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
    """The rise at which the ruled model rates this conductor at `amps` (bisection in dT; None above 200 K)."""
    if amps <= 0:
        return 0.0, "-"
    lo, hi = 1e-4, 200.0
    if rating(width, oz, hi, internal)[0] < amps:
        return None, "-"
    for _ in range(80):
        mid = (lo + hi) / 2.0
        if rating(width, oz, mid, internal)[0] < amps:
            lo = mid
        else:
            hi = mid
    return hi, rating(width, oz, hi, internal)[1]


def cmil(area_mm2):
    return area_mm2 * tc.C1 * 4.0 / math.pi


def rise_adiabatic(i2t, width, oz, I):
    """Onderdonk's adiabatic rise from the air line for an I2t on one face (no cooling: the upper bound)."""
    c = cmil(width * t_out(oz))
    x = I["k33"] * i2t / (c * c)
    if x > 50:
        return float("inf")
    return (I["k234"] + I["air_c"]) * (10.0 ** x - 1.0)


def fusing_i2t(width, oz, I):
    c = cmil(width * t_out(oz))
    return c * c * math.log10(1.0 + (I["t_melt"] - I["air_c"]) / (I["k234"] + I["air_c"])) / I["k33"]


# ------------------------------------------------------------------------------------------------ 3. the split
def r_barrel(h):
    """One barrel's resistance between the outer faces, in units of rho per mm (copper; rho cancels in every share)."""
    tp = vc.PLATING_UM / 1000.0
    return h / (math.pi * (vc_drill() + tp) * tp)


_S = {}


def stk():
    if "S" not in _S:
        _S["S"] = stackups_module()
    return _S["S"]


def vc_drill():
    return stk().DRILL           # record l9stk's 0.4 mm drill, the same the stackup record sizes every transition with


def dcd_rho():
    """dc_drop's copper resistivity (ohm m), read from its source line rather than typed again."""
    m = need(text("dc_drop"), r"^RHO = ([0-9.e-]+)\s+# ohm m$", "dc_drop's RHO")
    return float(m.group(1))


def r_band(L, w, oz):
    return L / (w * t_out(oz))


def share_one_end(L, w, oz, n, h):
    """A band whose one end is through-hole (both faces) and whose other end is a part on one face, n barrels there."""
    rb, rv = r_band(L, w, oz), r_barrel(h) / n
    return (rb + rv) / (2 * rb + rv)


def share_both_ends(L, w, oz, n, h):
    rb, rv = r_band(L, w, oz), r_barrel(h) / n
    return (rb + 2 * rv) / (2 * rb + 2 * rv)


def n_for(L, w, oz, h, s, both):
    """The least barrels at each one-face end for the part's face to carry at most s."""
    rb = r_band(L, w, oz)
    k = (2 * s - 1) / (2 * (1 - s)) if both else (2 * s - 1) / (1 - s)
    return int(math.ceil(r_barrel(h) / (k * rb) - 1e-9))


# ------------------------------------------------------------------------------------------------ 4. events
def envelope(rating_a, rows, high_a):
    """The backstop read monotone (a larger current clears no later than a smaller one, as L4-E11 section 6 reads its fuse):
    up to the first row with a maximum time the current may be held; each later interval may last as long as the maximum of
    the row below it, its top current being the next row's; above the last row, to the prospective high end."""
    out = []
    timed = [(p, b) for p, a, b in rows if b is not None]
    first = timed[0][0]
    out.append(("up to %g %% held" % first, rating_a * first / 100.0, None))
    for (p0, t0), (p1, _t1) in zip(timed, timed[1:]):
        out.append(("%g to %g %%, at most %g s" % (p0, p1, t0), rating_a * p1 / 100.0, t0))
    out.append(("over %g %% to %g A, at most %g s" % (timed[-1][0], high_a, timed[-1][1]), high_a, timed[-1][1]))
    return out


def events_pack(I):
    """(label, current A, duration s or None for held, class, the source) on the pack path."""
    b = I["blade_a"]
    ev = [("continuous load (declared)", I["cont"], None, "load", "pcb_pack_protection.yaml declared_continuous_a"),
          ("key-down, every transmitter (PWR-F12)", I["kd_a"], I["kd_s"], "transient", "POWER-THERMAL.md: PWR-F12"),
          ("PA key-on step at the pack", I["step"][1], I["kd_s"], "transient", "POWER-THERMAL.md 7.3, inside the key-down")]
    for name, a, s in I["gauge"]:
        if name == "OCD1":
            ev.append(("held under the gauge's OCD1", a, None, "gauge", "PRIMARY-CONFIGURATION.md OCD1, never trips below it"))
        else:
            ev.append(("gauge %s" % name, a, s, "gauge", "PRIMARY-CONFIGURATION.md %s" % name))
    ev.append(("the blade's rating (the chain's check 3)", b, None, "coordination", "pcb_energy_chain.yaml, energy_chain.py check 3"))
    for lab, a, s in envelope(b, I["mini_rows"], I["pf_high"]):
        ev.append(("blade " + lab, a, s, "backstop", "Littelfuse 297 time-current, read monotone"))
    ev.append(("hard short, the blade's typical melting I2t", I["pf_high"], I["mini_25"]["i2t"] / I["pf_high"] ** 2, "short",
               "Littelfuse 297 25 A: typical I2t, the clearing I2t not printed"))
    ev.append(("hard short, the gauge's ASCD", I["pf_high"], I["gauge"][-1][2], "short", "PRIMARY-CONFIGURATION.md ASCD"))
    ev.append(("docking pulse", I["dock_pk"], None, "pulse", "L4-E11 E11-30"))
    return ev


def events_shore(I, withstand=True):
    f = I["shore_fuse_a"]
    ev = [("continuous load (_VEH_T)", I["veh"], None, "load", "gen_sch_e.py _VEH_T, the hot-swap's limit at VCL max"),
          ("the fuse's rating (the chain's check 3)", f, None, "coordination", "pcb_energy_chain.yaml SHORE_INPUT")]
    if withstand:
        ev.append(("L4-E11 D-06: held to the clamps", I["shore_withstand_a"], None, "coordination", "l4e11_power.out section 6, SELECTED"))
    for lab, a, s in envelope(f, I["shore_rows"], I["shore_stiff_a"]):
        ev.append(("fuse " + lab, a, s, "backstop", "L4-E11 section 6, read monotone"))
    ev.append(("stiff source, the fuse's typical melting I2t", I["shore_stiff_a"], I["shore_i2t_typ"] / I["shore_stiff_a"] ** 2, "short",
               "typical melting; the clearing I2t not printed (E11-16)"))
    return ev


def judge(ev, width, oz, faces, s, I, limit_c):
    """Rise of the governing face for each event: held = steady; timed = min(steady, adiabatic); the docking pulse = adiabatic."""
    out = []
    for lab, a, dur, cls, src in ev:
        i_f = a * (s if faces == 2 else 1.0)
        if cls == "pulse":
            i2t = a * a * I["dock_tau"] / 2.0
            r_ad = rise_adiabatic(i2t * (s if faces == 2 else 1.0) ** 2, width, oz, I)
            out.append((lab, a, dur, cls, i2t, None, r_ad, r_ad, src))
            continue
        st, model = rise_steady(i_f, width, oz)
        if dur is None:
            out.append((lab, a, dur, cls, None, st, None, st, src))
            continue
        i2t = a * a * dur
        r_ad = rise_adiabatic(i_f * i_f * dur, width, oz, I)
        r = r_ad if st is None else min(st, r_ad)
        out.append((lab, a, dur, cls, i2t, st, r_ad, r, src))
    return out


def verdict(cls, r, I, limit_c, design=10.0):
    if r is None:
        return "over the fits (> 200 K)"
    if cls in ("load", "transient", "gauge", "coordination"):
        return "within %g K" % design if r <= design + 1e-6 else "OVER %g K" % design
    t = I["air_c"] + r
    if r > 9999:
        return "beyond the fits, OVER %g C" % limit_c
    return ("%.1f C, within %g C" % (t, limit_c)) if t <= limit_c + 1e-6 else ("%.1f C, OVER %g C" % (t, limit_c))


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
    """through-hole when every pad of the part is plated through, else one face (the part's layer)."""
    return "TH" if all(p["kind"] == "thru_hole" for p in fp[ref]["pads"]) else "1F"


def length_between(fp, a, b):
    """The gap between two parts' nearest pad edges along x on the pinned board (E7's placement; the layout sets the real one)."""
    ax = [(p["x"] - p["w"] / 2.0, p["x"] + p["w"] / 2.0) for p in fp[a]["pads"]]
    bx = [(p["x"] - p["w"] / 2.0, p["x"] + p["w"] / 2.0) for p in fp[b]["pads"]]
    lo, hi = (ax, bx) if min(x[0] for x in ax) < min(x[0] for x in bx) else (bx, ax)
    return round(min(x[0] for x in hi) - max(x[1] for x in lo), 2)


def conductors(R, I, W, fa, fe, h_e):
    """One row per conductor of the pack path and the shore input on A and E: (board, net, from, to, end kinds, protection,
    continuous, transient, fault and clearing, coordination A, family, width a face, the transfer field)."""
    blade, shore, wst = I["blade_a"], I["shore_fuse_a"], I["shore_withstand_a"]
    pk_fault = "gauge OCD1 %g A held, OCD2 %g A 1 s, AOLD %g A 20 ms, ASCD %g A 244 us; gauge failed: the blades (%g A held to %g %%, %g A for 600 s)" % (
        I["gauge"][0][1], I["gauge"][1][1], I["gauge"][2][1], I["gauge"][3][1], blade * 1.35, 135, blade * 2.0)
    sh_fault = "F1 %g A: %g A held, %g A for 600 s, %g A for 5 s; the hot-swap limits a fault behind Q7 to %g A" % (
        shore, shore * 1.35, shore * 2.0, shore * 3.5, I["veh"])
    rows = []

    def field(L, w, both):
        if L is None:
            return "max(%d, the split count of section 3 at its length)" % R["thermal_barrels"]["pack" if w == W["coord_smax"] else ("sh20" if w == W["sh20_smax"] else ("sh10" if w == W["sh10_smax"] else "vin"))]
        key = "pack" if w == W["coord_smax"] else ("sh20" if w == W["sh20_smax"] else ("sh10" if w == W["sh10_smax"] else "vin"))
        n = n_for(L, w, OZ1, h_e, S_MAX, both)
        return "%d at each one-face end (E7: %.2f mm, split %d, thermal %d)" % (max(n, R["thermal_barrels"][key]), L, n, R["thermal_barrels"][key])
    pin_kind = kind(fa, "J_CP1")
    rows += [
        ("A", "CELL+", "J_CP1 to J_CP4", "F1", "%s / %s" % (pin_kind, kind(fa, "F1")), "E's F3 %g A (upstream) and the gauge" % blade,
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B1", W["coord_even"], "none needed (both ends through-hole)"),
        ("A", "CELL_FUSED", "F1", "R17", "%s / %s" % (kind(fa, "F1"), kind(fa, "R17")), "A's F1 %g A and the gauge" % blade,
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B2", W["coord_smax"], field(None, W["coord_smax"], False) + " at R17"),
        ("A", "CH_BATQ (drafted)", "R17", "Q39, Q40", "1F / 1F", "A's F1 and the gauge", I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]),
         pk_fault, blade, "hop", R["hops"][0][2], "a one-face hop at least as wide as R17's land, as short as the two parts allow"),
        ("A", "VBAT trunk", "Q39, Q40 (R17 as drawn)", "the node's first branch", "1F / the loads", "A's F1 and the gauge", I["cont"],
         "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B2", W["coord_smax"], field(None, W["coord_smax"], False) + " at the pair"),
        ("A", "GND (the pack return)", "J_CN1 to J_CN4", "the loads' returns, In1 and In4", "%s / planes" % kind(fa, "J_CN1"), "the loop's blades and the gauge",
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B1", W["coord_even"], "none at the pins; In1 and In4 not necked to 30 mm beside the band"),
        ("A", "VIN_RAW", "J_VR1 to J_VR4", "the front end", "%s / 1F" % pin_kind, "the sources' limits (hot-swap, tracker)", I["vin_raw"], "-",
         "the tracker's %g A minimum valley, the hot-swap's %g A until its fault time" % (I["trk_valley"], I["veh"]), I["vin_raw"], "V", W["vin_smax"],
         field(None, W["vin_smax"], False) + " at the front end"),
        ("E", "CELL+", "J_BATT pin 2", "F3", "%s / %s" % (kind(fe, "J_BATT"), kind(fe, "F3")), "P's F1 %g A (upstream) and the gauge" % blade,
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B1", W["coord_even"], "none needed (both ends through-hole)"),
        ("E", "CELL_F", "F3", "P_CP", "%s / %s" % (kind(fe, "F3"), kind(fe, "P_CP")), "E's F3 %g A and the gauge" % blade,
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B2", W["coord_smax"], field(length_between(fe, "F3", "P_CP"), W["coord_smax"], False) + " at P_CP"),
        ("E", "GND (the pack return)", "J_BATT pin 1", "P_CN", "%s / %s" % (kind(fe, "J_BATT"), kind(fe, "P_CN")), "the loop's blades and the gauge",
         I["cont"], "%g A %g s" % (I["kd_a"], I["kd_s"]), pk_fault, blade, "B2", W["coord_smax"], field(R["e7_ret_len"], W["coord_smax"], False) + " at P_CN"),
        ("E", "DC_IN", "J_DCIN pin 1", "F1", "%s / %s" % (kind(fe, "J_DCIN"), kind(fe, "F1")), "the source's own; F1 for a fault behind it",
         I["veh"], "-", sh_fault, wst, "S1", W["sh20_even"], "none needed (both ends through-hole)"),
        ("E", "DC_F", "F1", "Q1, D10", "%s / %s" % (kind(fe, "F1"), kind(fe, "Q1")), "E's F1 %g A" % shore, I["veh"], "-", sh_fault, wst, "S2", W["sh20_smax"],
         field(length_between(fe, "F1", "Q1"), W["sh20_smax"], False) + " at Q1 and D10"),
        ("E", "DC_P", "Q1", "R19, D1", "%s / %s" % (kind(fe, "Q1"), kind(fe, "R19")), "E's F1", I["veh"], "-", sh_fault, wst, "hop", R["hops"][1][2],
         "a one-face hop at least as wide as Q1's drain land, as short as the parts allow"),
        ("E", "HS_S", "R19", "Q7", "%s / %s" % (kind(fe, "R19"), kind(fe, "Q7")), "E's F1", I["veh"], "-", sh_fault, shore, "hop", R["hops"][2][2],
         "a one-face hop at least as wide as Q7's source land, as short as the parts allow"),
        ("E", "DC_HS", "Q7", "L2", "%s / %s" % (kind(fe, "Q7"), kind(fe, "L2")), "the hot-swap; E's F1 with Q7 shorted", I["veh"], "-", sh_fault, shore, "S3",
         W["sh10_smax"], field(length_between(fe, "Q7", "L2"), W["sh10_smax"], True) + ", or %.2f mm on one face" % W["sh10_one"]),
        ("E", "GND_V (the shore return)", "J_DCIN pin 2", "D10, D1, C2, L2 pin 3", "%s / 1F" % kind(fe, "J_DCIN"), "E's F1 (the clamp-fault loop)", I["veh"], "-",
         sh_fault, wst, "S2", W["sh20_smax"], field(None, W["sh20_smax"], False) + " at the clamps"),
        ("E", "VIN_RAW", "L2 and the tracker's Q2", "P_VR to the block", "1F / 1F", "the sources' limits", I["vin_raw"], "-",
         "the tracker's %g A minimum valley, the hot-swap's %g A until its fault time" % (I["trk_valley"], I["veh"]), I["vin_raw"], "V", W["vin_smax"],
         field(None, W["vin_smax"], True) + " at each end"),
    ]
    return rows


# ------------------------------------------------------------------------------------------------ compute
def compute():
    for k, p in PINS.items():
        if not os.path.isfile(rel(p)):
            refuse("pinned input %s (%s) is missing" % (k, p))
    R = {"pins": {k: (p, sha(p)) for k, p in PINS.items()}}
    I = read_inputs()
    R["in"] = I
    S = stk()
    h_a, h_e = sw.total("JLC06161H-3313"), sw.total("JLC04161H-7628")
    R["h"] = (h_a, h_e)
    blade, shore = I["blade_a"], I["shore_fuse_a"]
    # the states: the highest sustained and key-down pack currents, DRAFTED, at the gauge's 10.0 V
    sus = [(k, v[1][3], v[2][3]) for k, v in I["states"].items() if v[0] == "sustained"]
    kd = [(k, v[1][3], v[2][3]) for k, v in I["states"].items() if v[0] == "key-down"]
    R["sustained_plan_max"] = max(sus, key=lambda x: x[1])
    R["sustained_high_max"] = max(sus, key=lambda x: x[2])
    R["keydown_plan_max"] = max(kd, key=lambda x: x[1])
    base = [x for x in sus if "plus" not in x[0]]
    R["sustained_plan_base"] = max(base, key=lambda x: x[1])
    R["sustained_high_base"] = max(base, key=lambda x: x[2])
    # the widths: the quoted ones, re-derived, and this record's
    W = {}
    W["svc_even"] = tc.width_for_current(I["kd_a"] / 2.0, oz=OZ1)          # l9stk's 6.72 (18 A, two faces)
    W["svc_one"] = tc.width_for_current(I["kd_a"], oz=OZ1)                  # 23.91
    W["svc_one_2oz"] = tc.width_for_current(I["kd_a"], oz=OZ2)              # 11.95
    W["coord_even"] = tc.width_for_current(blade / 2.0, oz=OZ1)             # 12.26 (25 A, two faces, even)
    W["coord_one"] = tc.width_for_current(blade, oz=OZ1)                    # 43.62
    W["coord_smax"] = tc.width_for_current(blade * S_MAX, oz=OZ1)           # 14.60
    W["coord_even_2oz"] = tc.width_for_current(blade / 2.0, oz=OZ2)
    W["coord_smax_2oz"] = tc.width_for_current(blade * S_MAX, oz=OZ2)
    W["coord_one_2oz"] = tc.width_for_current(blade, oz=OZ2)
    W["held_even"] = tc.width_for_current(I["gauge"][0][1] / 2.0, oz=OZ1)  # OCD1's held 20 A, two faces
    W["sh20_even"] = tc.width_for_current(I["shore_withstand_a"] / 2.0, oz=OZ1)
    W["sh20_smax"] = tc.width_for_current(I["shore_withstand_a"] * S_MAX, oz=OZ1)
    W["sh20_one"] = tc.width_for_current(I["shore_withstand_a"], oz=OZ1)
    W["sh10_smax"] = tc.width_for_current(shore * S_MAX, oz=OZ1)
    W["sh10_one"] = tc.width_for_current(shore, oz=OZ1)
    W["vin_smax"] = tc.width_for_current(I["vin_raw"] * S_MAX, oz=OZ1)
    W["trk_smax"] = tc.width_for_current(I["trk"] * S_MAX, oz=OZ1)
    R["w"] = W
    # the band families
    limit = I["mini_max_c"]
    pe = events_pack(I)
    se = events_shore(I)
    se10 = events_shore(I, withstand=False)
    fam = [
        ("A1", "6.72 mm a face, two 1 oz faces, even (l9stk's 18 A width)", W["svc_even"], OZ1, 2, 0.5, pe),
        ("A2", "11.95 mm on one 2 oz face (l9stk's 18 A width)", W["svc_one_2oz"], OZ2, 1, 1.0, pe),
        ("B1", "12.26 mm a face, two 1 oz faces, even (25 A; through-hole ends)", W["coord_even"], OZ1, 2, 0.5, pe),
        ("B2", "%.2f mm a face, two 1 oz faces, the part's face at %.2f (25 A; a one-face part at an end)" % (W["coord_smax"], S_MAX), W["coord_smax"], OZ1, 2, S_MAX, pe),
        ("B3", "%.2f mm a face, two 2 oz faces, the part's face at %.2f (the 2 oz option)" % (W["coord_smax_2oz"], S_MAX), W["coord_smax_2oz"], OZ2, 2, S_MAX, pe),
        ("S1", "%.2f mm a face, two 1 oz faces, even (the shore's %g A, through-hole ends)" % (W["sh20_even"], I["shore_withstand_a"]), W["sh20_even"], OZ1, 2, 0.5, se),
        ("S2", "%.2f mm a face, the part's face at %.2f (the shore's %g A, a one-face part at an end)" % (W["sh20_smax"], S_MAX, I["shore_withstand_a"]), W["sh20_smax"], OZ1, 2, S_MAX, se),
        ("S3", "%.2f mm a face, the part's face at %.2f (F1's %g A after the hot-swap)" % (W["sh10_smax"], S_MAX, shore), W["sh10_smax"], OZ1, 2, S_MAX, se10),
    ]
    F = {}
    for key, lab, w, oz, faces, s, ev in fam:
        F[key] = dict(label=lab, w=w, oz=oz, faces=faces, s=s, rows=judge(ev, w, oz, faces, s, I, limit),
                      fusing=fusing_i2t(w, oz, I))
    R["fam"] = F
    # VIN_RAW: source-limited (the hot-swap and the tracker)
    vin_ev = [("declared (the hot-swap's 6.15 A and the tracker's 10.33 A at the 9 V floor)", I["vin_raw"], None, "load", "gen_sch_e.py _VIN_T"),
              ("the tracker's minimum valley limit, held", I["trk_valley"], None, "coordination", "gen_sch_e.py R4A-N12")]
    R["vin"] = dict(w=W["vin_smax"], rows=judge(vin_ev, W["vin_smax"], OZ1, 2, S_MAX, I, limit),
                    sum_a=I["veh"] + I["trk_valley"])
    R["vin"]["sum_rise"] = rise_steady(R["vin"]["sum_a"] * S_MAX, W["vin_smax"], OZ1)[0]
    # the split: the transfer field per end, tabled by length, both board thicknesses
    thermal = {k: vc.barrels_for(a / 2.0, vc_drill()) for k, a in (("pack", blade), ("sh20", I["shore_withstand_a"]), ("sh10", shore), ("vin", I["vin_raw"]))}
    R["thermal_barrels"] = thermal
    T = []
    for name, w, h in (("pack, board A", W["coord_smax"], h_a), ("pack, board E", W["coord_smax"], h_e),
                       ("shore 20 A, board E", W["sh20_smax"], h_e), ("shore 10 A, board E", W["sh10_smax"], h_e), ("VIN_RAW, board E", W["vin_smax"], h_e)):
        T.append((name, w, h, [(L, n_for(L, w, OZ1, h, S_MAX, False), n_for(L, w, OZ1, h, S_MAX, True)) for L in LENGTHS]))
    R["transfer"] = T
    R["r_barrel"] = (r_barrel(h_a), r_barrel(h_e))
    R["barrel_mm_eq"] = r_barrel(h_e) * W["coord_smax"] * t_out(OZ1)    # one barrel as millimetres of a 14.60 mm band
    # the split with no transfer field: the band's whole current on the part's face over the hop
    R["no_field"] = {L: share_one_end(L, W["coord_smax"], OZ1, 1, h_e) for L in LENGTHS}
    # the inner planes: record l9stk's plane_share screen, and the areal heating against the bands it relieves
    tin = S.INNER_HALF_OZ * 0.035
    P = {}
    for key, w, planes, widths in (("a", W["coord_even"], 2, (20.0, 30.0, 40.0, 80.0, 160.0)), ("e", W["coord_smax"], 1, (20.0, 40.0, 68.0))):
        rows = []
        for wp in widths:
            s, per, rat, mod = S.plane_share(blade, w, 2, t_out(OZ1), wp, tin, planes)
            band_per_face = blade * (1 - s) / 2.0
            q_band = band_per_face ** 2 / (w * w * t_out(OZ1))
            q_plane = per ** 2 / (wp * wp * tin)
            cell_bar = tc.conservative(I["cell"] * tin, 10.0)[0]
            rows.append((wp, s, per, rat, mod, per <= rat, q_plane / q_band, per * I["cell"] / wp, cell_bar))
        P[key] = dict(w=w, planes=planes, rows=rows, band=S.failing_band(blade, w, 2, t_out(OZ1), tin, planes))
    R["planes"] = P
    # board E's cross-section, redone
    cs = [("CELL_F (pack forward)", W["coord_smax"]), ("the pack return (GND)", W["coord_smax"]), ("VIN_RAW", W["vin_smax"]),
          ("TRK_OUT (declared 10.33 A)", W["trk_smax"]), ("the shore chain DC_IN to DC_P", W["sh20_smax"]), ("the shore return GND_V", W["sh20_smax"])]
    R["e_cross"] = dict(rows=cs, sum=sum(w for _n, w in cs), pack_end=W["coord_smax"] * 2, strip=S.outline(S.PINS["board_e"])[1])
    # the boards' parts: entry kinds and the bottlenecks
    fa = footprints(PINS["board_a"], ("F1", "R17", "J_CP1", "J_CN1"))
    fe = footprints(PINS["board_e"], ("J_BATT", "F3", "P_CP", "P_CN", "J_DCIN", "F1", "Q1", "R19", "Q7", "L2"))
    R["fp"] = dict(a=fa, e=fe)
    f3p2 = [p for p in fe["F3"]["pads"] if p["net"] == "CELL_F"]
    pcp = fe["P_CP"]["pads"][0]
    R["e7_cellf_len"] = round((pcp["x"] - pcp["w"] / 2.0) - (max(p["x"] for p in f3p2) + f3p2[0]["w"] / 2.0), 2)
    R["e7_cellf_n"] = n_for(R["e7_cellf_len"], W["coord_smax"], OZ1, h_e, S_MAX, False)
    jb = [p for p in fe["J_BATT"]["pads"] if p["net"] == "GND"][0]
    pcn = fe["P_CN"]["pads"][0]
    R["e7_ret_len"] = round((pcn["x"] - pcn["w"] / 2.0) - (jb["x"] + jb["w"] / 2.0), 2)
    R["e7_ret_n"] = n_for(R["e7_ret_len"], W["coord_smax"], OZ1, h_e, S_MAX, False)
    # the series parts against the classes
    r17, r19 = I["r17"], I["r19"]
    R["r17_at"] = [(lab, a, a * a * r17["mohm"] / 1000.0) for lab, a in (("continuous", I["cont"]), ("key-down", I["kd_a"]), ("OCD1 held", I["gauge"][0][1]),
                   ("blade rating", blade), ("blade 110 %", blade * 1.1), ("blade 135 % held", blade * 1.35), ("blade 200 %, the 600 s window top", blade * 2.0))]
    R["r17_limit_a"] = math.sqrt(r17["w"] / (r17["mohm"] / 1000.0))
    R["r19_limit_a"] = math.sqrt(r19["w"] / (r19["mohm"] / 1000.0))
    pair = I["pair_mohm_each"] / 2.0
    R["pair_at"] = [(lab, a, a * a * pair / 1000.0) for lab, a in (("OCD1 held", I["gauge"][0][1]), ("blade rating", blade), ("blade 135 % held", blade * 1.35))]
    R["pins_at"] = [(lab, a, a / I["pins"]) for lab, a in (("blade rating", blade), ("blade 135 % held", blade * 1.35), ("blade 200 %, the 600 s window top", blade * 2.0))]
    R["xt60_at"] = [(lab, a) for lab, a in (("blade 110 % held", blade * 1.1), ("blade 135 % held", blade * 1.35), ("blade 200 %, the 600 s window top", blade * 2.0))]
    # the one-face hops between two one-face parts (no transfer field can split a few millimetres): the hop's copper I2R
    # per millimetre of length at the larger land's width, against the series part's own I2R at the same current
    def land_w(fp, ref, net):
        return max(min(p["w"], p["h"]) if p["kind"] == "smd" else p["w"] for p in fp[ref]["pads"] if p["net"] == net)
    hops = []
    for lab, a, w, part_w in (("CH_BATQ, R17 to Q39 and Q40 (board A)", blade, max(p["h"] for p in fa["R17"]["pads"]), blade ** 2 * r17["mohm"] / 1000.0),
                              ("DC_P, Q1 to R19 (board E)", I["shore_withstand_a"], land_w(fe, "Q1", "DC_P"), I["shore_withstand_a"] ** 2 * r19["mohm"] / 1000.0),
                              ("HS_S, R19 to Q7 (board E)", shore, land_w(fe, "Q7", "HS_S"), shore ** 2 * r19["mohm"] / 1000.0)):
        per_mm = a * a * (dcd_rho() * 1e3) / (w * t_out(OZ1))          # W per mm: rho in ohm mm
        hops.append((lab, a, w, per_mm, part_w))
    R["hops"] = hops
    # the barrels in a transfer field: the share of each fault on one barrel, adiabatic, and the barrel's fusing I2t
    nb = thermal["pack"]
    bar_area = vc.ampacity(vc_drill(), 10.0)[1]
    bc = cmil(bar_area)
    bfuse = bc * bc * math.log10(1.0 + (I["t_melt"] - I["air_c"]) / (I["k234"] + I["air_c"])) / I["k33"]
    br = []
    for lab, i2t in (("docking pulse", I["dock_pk"] ** 2 * I["dock_tau"] / 2.0), ("blade typical melting", I["mini_25"]["i2t"]),
                     ("600 % row bound at the high fault", I["pf_high"] ** 2 * I["mini_rows"][-1][2])):
        per = (0.5 / nb) ** 2 * i2t
        x = I["k33"] * per / (bc * bc)
        br.append((lab, i2t, per, (I["k234"] + I["air_c"]) * (10 ** x - 1.0), per <= bfuse))
    R["barrel_faults"] = dict(n=nb, area=bar_area, fuse=bfuse, rows=br)
    R["conductors"] = conductors(R, I, W, fa, fe, h_e)
    # the predicates
    def row(k, start):
        return [r for r in F[k]["rows"] if r[0].startswith(start)][0]
    pred = {
        "the quoted widths re-derive from decision 35's model: 6.72, 23.91, 11.95, 12.26 and 43.62 mm":
            [round(W[k], 2) for k in ("svc_even", "svc_one", "svc_one_2oz", "coord_even", "coord_one")] == [6.72, 23.91, 11.95, 12.26, 43.62],
        "the blades on A, E and P are one rating and the chain's check 3 asks the conductor for it":
            blade == float(I["chain"]["DOCK_ENTRY"]["conductor"]["rating_a"]) == float(I["chain"]["BOARD_A_NODE"]["conductor"]["rating_a"]),
        "6.72 mm a face is over 10 K at the gauge's held OCD1 current": row("A1", "held under")[7] > 10.0,
        "6.72 mm a face is over 10 K at the blade's rating": row("A1", "the blade's rating")[7] > 10.0,
        "11.95 mm on one 2 oz face is over 10 K at the blade's rating": row("A2", "the blade's rating")[7] > 10.0,
        "12.26 mm a face at an even split is at 10 K at the blade's rating": abs(row("B1", "the blade's rating")[7] - 10.0) < 1e-3,
        "the 14.60 class at its governing share is at 10 K at the blade's rating": abs(row("B2", "the blade's rating")[7] - 10.0) < 1e-3,
        "on B1, B2 and B3 every load, transient and gauge level is within 10 K":
            all(r[7] is not None and r[7] <= 10.0 + 1e-6 for k in ("B1", "B2", "B3") for r in F[k]["rows"] if r[3] in ("load", "transient", "gauge")),
        "on B1, B2 and B3 the blade's 135 % held and its 600 s window top stay within the blade's printed maximum from the air line":
            all(I["air_c"] + row(k, s)[7] <= limit for k in ("B1", "B2", "B3") for s in ("blade up to 135", "blade 135 to 200")),
        "on A1 and A2 the blade's 600 s window top exceeds the blade's printed maximum":
            all(I["air_c"] + row(k, "blade 135 to 200")[7] > limit for k in ("A1", "A2")),
        "on every pack family the backstop's 5 s interval and faster are over the printed maximum by the tree's bounds":
            all(I["air_c"] + row(k, s)[7] > limit for k in ("A1", "A2", "B1", "B2", "B3") for s in ("blade 200 to 350", "blade 350 to 600", "blade over 600")),
        "every hard short on B1, B2 and B3 is within the printed maximum at the blade's typical I2t and the gauge's ASCD":
            all(I["air_c"] + row(k, s)[7] <= limit for k in ("B1", "B2", "B3") for s in ("hard short, the blade", "hard short, the gauge")),
        "the copper is not the fuse: the 600 % row's bound on B1 and B2 is under the governing face's fusing I2t":
            all((I["pf_high"] ** 2 * I["mini_rows"][-1][2]) * F[k]["s"] ** 2 < F[k]["fusing"] for k in ("B1", "B2")),
        "with one barrel the part's face carries more than the governing share at every tabled length": all(v > S_MAX for v in R["no_field"].values()),
        "the transfer field's split count falls with length (one end and both ends)":
            all(x[3][i][1] >= x[3][i + 1][1] and x[3][i][2] >= x[3][i + 1][2] for x in T for i in range(len(LENGTHS) - 1)),
        "the shore's 20 A families hold the fuse's 600 s window top at 10 K": all(abs(row(k, "fuse 135 to 200")[7] - 10.0) < 1e-3 for k in ("S1", "S2")),
        "R17 reaches its rating inside the blade's 110 to 200 % window": blade * 1.1 < R["r17_limit_a"] < blade * 2.0,
        "R19 reaches its rating inside the shore fuse's 135 to 200 % window": shore * 1.35 < R["r19_limit_a"] < shore * 2.0,
        "the dock pins stay within their 10 C rating up to the blade's 135 % row": blade * 1.35 / I["pins"] <= I["pin_a"],
        "the XT60 is over its rating inside the blade's held band": blade * 1.1 < I["xt60_a"] < blade * 1.35,
        "on board A two planes beside 12.26 mm faces are over the screen only in a band narrower than 30 mm":
            P["a"]["band"] is not None and P["a"]["band"][1] < 30.0,
        "a plane tied in parallel heats per square millimetre at the thickness ratio of the bands it relieves":
            all(abs(r[6] - t_in_half() / t_out(OZ1)) < 1e-9 for k in ("a", "e") for r in P[k]["rows"]),
        "VIN_RAW's declared current covers the tracker's minimum valley limit": I["vin_raw"] >= I["trk_valley"],
        "every one-face hop's copper dissipates under a tenth of its series part per millimetre":
            all(h[3] < 0.1 * h[4] for h in R["hops"]),
    }
    R["pred"] = pred
    return R


# ------------------------------------------------------------------------------------------------ render
def f2(x):
    if x is None:
        return "-"
    return ">9999" if x > 9999 else "%.2f" % x


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
    P("l9stk_copper: the pack path's copper on boards A and E, on its basis (record l9stk, MESHSAT-1357). Desk arithmetic on")
    P("committed files: nothing was built, routed, measured or bought, and no figure below is a measurement.")
    P("")
    P("0. PINS (path  sha256/16)")
    for k, (p, s) in sorted(R["pins"].items()):
        P("   %-14s %s  sha256 %s" % (k, p, s))
    P("")
    P("1. THE CURRENTS BY CLASS (each from its pinned source)")
    P("   continuous: the pack's declared %.1f A (pcb_pack_protection.yaml); the drafted states at the gauge's 10.0 V floor (record l9pwr" % I["cont"])
    P("     section 6, Layer 8's copy): the largest sustained PLAN %.2f A (%s), at HIGH %.2f A (%s); with the outlets PLAN %.2f A (%s);" % (
        R["sustained_plan_base"][1], R["sustained_plan_base"][0], R["sustained_high_base"][2], R["sustained_high_base"][0], R["sustained_plan_max"][1], R["sustained_plan_max"][0]))
    P("     above %.1f A a sustained state is held by the shedding control (rv-pwr 9.3), so %.1f A is the continuous design current" % (I["cont"], I["cont"]))
    P("   transient: every transmitter keyed, %.1f A for at most %.0f s (PWR-F12, D-11's key-down ended early above %.1f A); the largest" % (I["kd_a"], I["kd_s"], I["kd_a"]))
    P("     key-down row at PLAN at 10.0 V %.2f A (%s), held under %.1f A by D-11's floors; the PA's key-on step %.1f to %.1f A at the pack" % (
        R["keydown_plan_max"][1], R["keydown_plan_max"][0], I["kd_a"], I["step"][0], I["step"][1]))
    P("     (POWER-THERMAL 7.3); the docking pulse %.1f A peak with a %.1f us time constant, once per docking (L4-E11 E11-30), I2t %.4f A2s" % (
        I["dock_pk"], I["dock_tau"] * 1e6, I["dock_pk"] ** 2 * I["dock_tau"] / 2.0))
    P("   fault, the gauge working (PRIMARY-CONFIGURATION.md, the image): " + "; ".join(
        "%s %.1f A for %s" % (n, a, ("%g s" % s) if s >= 0.001 else ("%g us" % (s * 1e6))) for n, a, s in I["gauge"]))
    P("     so %.1f A may be held without a trip (OCD1 never trips below it)" % I["gauge"][0][1])
    P("   fault, the gauge failed (the hardware backstop): the %.0f A MINI blades in series (board P's F1, board E's F3, board A's F1;" % I["blade_a"])
    P("     Littelfuse 297): " + "; ".join("%g %% (%.2f A) %s" % (p, I["blade_a"] * p / 100.0, ("holds %g s at least" % a) if b is None else ("opens in %g to %g s" % (a, b)))
                                       for p, a, b in I["mini_rows"]))
    P("     typical I2t %g A2s, cold %.2f mOhm; F2 (Eaton SCF9550, board P) %g A: %g %% for %g h minimum, %g %% opens within %g s, breaks %g A" % (
        I["mini_25"]["i2t"], I["mini_25"]["mohm"], I["f2"]["a"], I["f2"]["hold_pct"], I["f2"]["hold_h"], I["f2"]["open_pct"], I["f2"]["open_s"], I["f2"]["break_a"]))
    P("     prospective fault %.0f to %.0f A (pcb_energy_chain.yaml PACK_CELLS)" % (I["pf_low"], I["pf_high"]))
    P("   the shore input: _VEH_T %.2f A (the hot-swap's limit at VCL max) continuous; F1 %.0f A MINI: " % (I["veh"], I["shore_fuse_a"]) + "; ".join(
        "%g %% %s" % (p, ("holds %g s" % a) if b is None else ("%g to %g s" % (a, b))) for p, a, b in I["shore_rows"]))
    P("     (L4-E11 section 6); a stiff source to %.0f A, %g A2s typical melting, the clearing I2t not printed; L4-E11's D-06 selection:" % (I["shore_stiff_a"], I["shore_i2t_typ"]))
    P("     board E's copper from J_DCIN to F1 to the clamps at least %.0f A continuous (a Layer 9 layout constraint)" % I["shore_withstand_a"])
    P("   VIN_RAW: declared %.2f A (the hot-swap and the tracker at the 9 V floor); the tracker's minimum buck valley limit %.1f A" % (I["vin_raw"], I["trk_valley"]))
    P("")
    P("2. THE RULED METHOD AND THE CRITERIA")
    P("   rating: track_current.conservative (decision 35: the most conservative of the three Annex D fits at each area), outer copper")
    P("     at track_current.EXTERNAL_FACTOR %.1f, the rise bisected so the rating equals the current; widths by track_current.width_for_current" % tc.EXTERNAL_FACTOR)
    P("     at its 10 K default; the fits' stated data: IPC-2152 to %.0f A and %.0f K, CNES to %.0f A (ECSS-Q-ST-70-12C D.2, D.3)" % (I["ipc2152_a"], I["ipc2152_k"], I["cnes_a"]))
    P("   adiabatic: Onderdonk's general form as records/l7pwr/inputs holds it, constants %.0f and %.0f, copper melting %.0f C, from the" % (I["k234"], I["k33"], I["t_melt"]))
    P("     consolidation's +%.0f C mixed-air line; a timed event's rise is the smaller of its adiabatic and its steady rise" % I["air_c"])
    P("   criteria (SESSION): the continuous load, the key-down, every gauge level and the blade's rating within the ruled 10 K (the rise")
    P("     every rating in the energy chain carries); the backstop's window and the hard short at or under %.0f C from the air line, the" % I["mini_max_c"])
    P("     blade's printed operating maximum (Littelfuse 297), the lowest printed limit of a part these bands join (the laminate's is NOT HELD);")
    P("     and every fault's I2t under the copper's own fusing I2t")
    P("")
    P("3. THE SPLIT BETWEEN THE OUTER FACES (derived; copper's resistivity cancels)")
    P("   through-hole at both ends: equal faces sit at one potential along the band, so each carries half and stitching moves nothing")
    P("   a one-face part at one end: the part's face carries (Rb + Rv) / (2 Rb + Rv); at both ends (Rb + 2 Rv) / (2 Rb + 2 Rv), where Rb is")
    P("     one face's band and Rv the transfer field (one barrel over n). Stitching along such a band moves current onto the part's face early")
    P("     (that face sits lower all along), so the transfer barrels belong in a field at the part and nowhere between")
    P("   one barrel of %.1f mm drill, %.0f um plating: %.2f (board A, %.4f mm) and %.2f (board E, %.4f mm) in rho per mm, as much as %.1f mm" % (
        vc_drill(), vc.PLATING_UM, R["r_barrel"][0], R["h"][0], R["r_barrel"][1], R["h"][1], R["barrel_mm_eq"]))
    P("     of a %.2f mm 1 oz band" % W["coord_smax"])
    P("   with no field (one barrel), the part's face of a %.2f mm band carries: %s" % (W["coord_smax"], ", ".join("%.2f at %.0f mm" % (v, L) for L, v in sorted(R["no_field"].items()))))
    P("   the field each one-face end needs for the part's face to carry at most %.2f (one end / both ends), and the thermal count:" % S_MAX)
    for name, w, h, rows in R["transfer"]:
        key = {"pack, board A": "pack", "pack, board E": "pack", "shore 20 A, board E": "sh20", "shore 10 A, board E": "sh10", "VIN_RAW, board E": "vin"}[name]
        P("     %-22s %.2f mm, %.4f mm board: %s; thermal %d (via_current.barrels_for at half the coordination current)" % (
            name, w, h, ", ".join("%.0f mm %d / %d" % (Lx, a, b) for Lx, a, b in rows), R["thermal_barrels"][key]))
    P("   on E7's placement CELL_F runs %.2f mm from F3's pad to P_CP's land: %d barrels at P_CP; the return %.2f mm from J_BATT pin 1 to" % (
        R["e7_cellf_len"], R["e7_cellf_n"], R["e7_ret_len"]))
    P("     P_CN: %d barrels at P_CN" % R["e7_ret_n"])
    P("   the inner planes (record l9stk's plane_share: one-dimensional, by cross-section, the internal fit over the plane's whole width),")
    P("   and the plane's heating per square millimetre against the outer bands it relieves, and its current per %.1f mm raster cell against" % I["cell"])
    P("   dc_drop's per-cell bar (the routed-board judge of PI-001):")
    for key, nm in (("a", "board A, In1 and In4 beside the return"), ("e", "board E, In1 beside the return")):
        p = R["planes"][key]
        P("     %s, outer %.2f mm a face; the screen's failing band %s" % (nm, p["w"], "none" if p["band"] is None else "%.2f to %.2f mm" % p["band"]))
        for wp, s, per, rat, mod, ok, q, cellA, bar in p["rows"]:
            P("       %6.1f mm: share %.2f, %.2f A a plane against %.2f (%s) %s; heating %.2f of the bands'; %.3f A a cell against %.3f" % (
                wp, s, per, rat, mod, "holds" if ok else "OVER", q, cellA, bar))
    P("")
    P("4. THE BAND FAMILIES: each class's rise on the governing face, and its final temperature from the +%.0f C air line" % I["air_c"])
    for key in ("A1", "A2", "B1", "B2", "B3", "S1", "S2", "S3"):
        f = F[key]
        P("   %s %s: %.2f mm, governing share %.2f, the face's fusing I2t %.0f A2s" % (key, f["label"], f["w"], f["s"], f["fusing"]))
        for lab, a, dur, cls, i2t, st, ad, r, src in f["rows"]:
            P("     %-58s %7.2f A %-10s %-12s steady %-7s adiabatic %-7s -> %-7s %s" % (
                lab, a, dur_s(dur, cls, I), cls, f2(st), f2(ad), f2(r), verdict(cls, r, I, I["mini_max_c"])))
    v = R["vin"]
    P("   V  VIN_RAW %.2f mm a face, the part's face at %.2f:" % (v["w"], S_MAX))
    for lab, a, dur, cls, i2t, st, ad, r, src in v["rows"]:
        P("     %-58s %7.2f A %-10s %-12s steady %-7s -> %s" % (lab, a, "held", cls, f2(st), verdict(cls, r, I, I["mini_max_c"])))
    P("     the sum of both sources' limits %.2f A for at most the hot-swap's fault time: %.2f K steady (an upper bound on any duration)" % (v["sum_a"], v["sum_rise"]))
    P("")
    P("5. THE CONDUCTORS (TH through-hole, 1F one face; widths are each outer face at 1 oz; the family's rows in section 4)")
    for b, net, fr, to, ek, prot, cont, trans, fault, coord, fam, w, fld in R["conductors"]:
        P("   %s %-24s %s to %s [%s]" % (b, net, fr, to, ek))
        P("       protection: %s; continuous %.2f A; transient %s" % (prot, cont, trans))
        P("       fault: %s" % fault)
        P("       coordination %.2f A; %s; %.2f mm a face; field: %s" % (coord, ("family " + fam) if fam != "hop" else "a one-face hop", w, fld))
    P("")
    P("6. THE WIDTHS QUOTED IN THE CONFLICT, JUDGED")
    P("   6.72 mm a face (l9stk at %.0f A): %.2f K at the gauge's held %.0f A, %.2f K at the blade's %.0f A, the 600 s window top %.1f C" % (
        I["kd_a"], [r for r in F["A1"]["rows"] if r[0].startswith("held under")][0][7], I["gauge"][0][1], [r for r in F["A1"]["rows"] if r[3] == "coordination"][0][7], I["blade_a"],
        I["air_c"] + [r for r in F["A1"]["rows"] if r[0].startswith("blade 135 to 200")][0][7]))
    P("   11.95 mm on one 2 oz face (l9stk at %.0f A): %.2f K at the blade's %.0f A; 2 oz on one face needs %.2f mm at %.0f A" % (
        I["kd_a"], [r for r in F["A2"]["rows"] if r[3] == "coordination"][0][7], I["blade_a"], W["coord_one_2oz"], I["blade_a"]))
    P("   12.26 mm a face (Layer 8 at %.0f A): holds where both ends are through-hole (an even split, derived); at a one-face part the" % I["blade_a"])
    P("     part's face carries more than half and needs %.2f mm at a %.2f share with the field of section 3" % (W["coord_smax"], S_MAX))
    P("   23.44 mm a face (l9stk's board E bound at %.0f A, every conductor in one section): superseded by section 8" % I["kd_a"])
    P("   2 oz (the reversal): %.2f mm a face at an even split, %.2f at %.2f, %.2f on one face" % (W["coord_even_2oz"], W["coord_smax_2oz"], S_MAX, W["coord_one_2oz"]))
    P("")
    P("7. THE SERIES PARTS AND THE LANDS (the bottlenecks)")
    P("   R17 (board A, %g mOhm, %s, %g W): " % (I["r17"]["mohm"], I["r17"]["code"], I["r17"]["w"]) + "; ".join("%s %.2f A %.3f W" % (l, a, p) for l, a, p in R["r17_at"][:4]))
    P("     " + "; ".join("%s %.2f A %.3f W" % (l, a, p) for l, a, p in R["r17_at"][4:]))
    P("     its %g W is reached at %.2f A, inside the blade's 110 to 200 %% window (the gauge failed)" % (I["r17"]["w"], R["r17_limit_a"]))
    P("   Q39 and Q40 (drafted, %g mOhm each at L4-E11's 150 C bound, in parallel): " % I["pair_mohm_each"] + "; ".join("%s %.2f A %.2f W" % (l, a, p) for l, a, p in R["pair_at"]))
    P("     E11-29's bar covers the gauge's levels (L4-E11 15c); the blade's window is outside it")
    P("   the dock pins (%d in parallel, %g A each at a %g C rise): " % (I["pins"], I["pin_a"], I["pin_rise"]) + "; ".join("%s %.2f A a pin" % (l, a) for l, a, p in [(x[0], x[2], 0) for x in R["pins_at"]]))
    P("   the XT60 (%g A, %g A instantaneous): " % (I["xt60_a"], I["xt60_peak"]) + "; ".join("%s %.2f A" % x for x in R["xt60_at"]))
    P("   R19 (board E, %g mOhm, %s, %g W): its %g W at %.2f A, inside F1's 135 to 200 %% window" % (I["r19"]["mohm"], I["r19"]["code"], I["r19"]["w"], I["r19"]["w"], R["r19_limit_a"]))
    P("   the Keystone 3568 holders (A's F1, E's F3 and F1, P's F1): no current rating printed (L4-E11 section 6, the maker's page)")
    for b, fp in (("A", R["fp"]["a"]), ("E", R["fp"]["e"])):
        for ref in sorted(fp):
            kinds = sorted({p["kind"] for p in fp[ref]["pads"] if p["net"]})
            sizes = sorted({"%gx%g%s" % (p["w"], p["h"], (" d%g" % p["drill"]) if p["drill"] else "") for p in fp[ref]["pads"] if p["net"]})
            P("   board %s %-6s %-44s %-8s %s; pads %s" % (b, ref, fp[ref]["lib"].split(":")[-1], fp[ref]["layer"], "/".join(kinds), ", ".join(sizes)))
    P("   one-face hops between two one-face parts (no field can split a few millimetres), copper I2R per millimetre at the larger land:")
    for lab, a, w, per_mm, part_w in R["hops"]:
        P("     %-40s %6.2f A on %.2f mm: %.4f W a mm against the series part's %.3f W" % (lab, a, w, per_mm, part_w))
    bf = R["barrel_faults"]
    P("   one barrel of a %d-barrel transfer field (%.4f mm2, fusing %.1f A2s from the air line): " % (bf["n"], bf["area"], bf["fuse"]) + "; ".join(
        "%s %.4f A2s, +%.2f K" % (lab, per, dt) for lab, i2t, per, dt, ok in bf["rows"]))
    P("")
    P("8. BOARD E'S CROSS-SECTION, REDONE AT THE COORDINATION CURRENTS AND THE DERIVED SHARE (1 oz, each face)")
    for n, w in R["e_cross"]["rows"]:
        P("   %-40s %6.2f mm" % (n, w))
    P("   every one in one section: %.2f mm a face of the %.0f mm strip (a bound the floor plan must avoid); the pack end alone (forward and" % (R["e_cross"]["sum"], R["e_cross"]["strip"]))
    P("   return): %.2f mm a face" % R["e_cross"]["pack_end"])
    P("")
    P("9. PREDICATES")
    for k, val in R["pred"].items():
        P("   %-118s %s" % (k, "yes" if val else "NO"))
    return "\n".join(L) + "\n"


def main():
    R = compute()
    sys.stdout.write(render(R))
    bad = [k for k, v in R["pred"].items() if not v]
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
