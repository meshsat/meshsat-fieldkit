#!/usr/bin/env python3
"""l8gnd_drafts.py: what the Layer 8 record l8gnd drafts, proved on scratch copies (MESHSAT-1357, 3 October 2026).

It prints, deterministically and without touching the tree:
  1. the inputs it read, each pinned by sha256 (the generators, every board A power draft of L4-E4 to L4-E11, this record's
     drafts and land, the pages the drafts rest on and the makers' sheets they quote);
  2. the four board changes of GND-002 and the SLOT_EN hold as the drafts add them: every part call and every net it touches,
     read from the text each draft writes (a parse of the composed generator's part calls, never a prose grep);
  3. the keeper's arithmetic from printed figures, each with its class;
  4. the composition on board A: L4-E9's change-list order (r12, guard, charger, r11, bank, r138, u17) with this record's two
     drafts last applies step by step; this record's drafts first and then every power draft in that order applies too (every
     anchor of theirs survives this record's edits); each power draft alone after this record's two; this record's two in either
     order;
  5. the designators each board A draft adds, and that no two drafts add the same one (L6P-F01's method, H pads included);
  6. board B: this record's draft alone, and the nets C33 and J_ETH's shield sit on before and after;
  7. the netlist check (check_gnd002_netlist.py) on the committed netlists, which read NOT DRAWN on A and B today, and on two
     fixture netlists that carry the drafted changes, which read DRAWN.
Run it from the repository root:  python3 v2/docs/records/l8gnd/l8gnd_drafts.py  (the committed l8gnd_drafts.out is its output,
regenerated with _bin/regen_out.py). Nothing here has been built or measured: every statement is about generator text and netlists."""
import glob
import hashlib
import importlib.util
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
RECS = os.path.join(ROOT, "v2", "docs", "records")
GEN_A = os.path.join(TOOLS, "gen_sch_a.py")
GEN_B = os.path.join(TOOLS, "gen_sch_b.py")

# L4-POWER-ARCHITECTURE.md section 3, the board A rows in application order: 3a R-01 (r12), R-124 (guard), R-157 (charger);
# 3b R-04 (r11); 3c R-07 (bank, after r12); 3d R-05 (r138); 3e R-06 (u17, after 3a to 3d).
POWER_ORDER = [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17")]
MINE_A = [("l8gnd", "gnd002"), ("l8gnd", "hotr1")]
MINE_B = [("l8gnd", "gnd002")]

INPUTS = [
    "v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_b.py", "v2/ecad/tools/gen_sch_c.py",
    "v2/ecad/tools/pcb_rules.yaml", "v2/ecad/tools/pcb_interfaces.yaml",
    "v2/docs/GROUNDING-AND-SHIELDS.md", "v2/docs/HW-FW-CONTRACT.md", "v2/docs/ARCHITECTURE.md", "v2/docs/CONOPS.md",
    "v2/docs/handover/LAYER-STATUS.md", "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
    "v2/vendor/cluster/ksz989x-hw-design-checklist.pdf", "v2/vendor/connectors/amphenol-rjhse5380-rj45-jack.pdf",
    "v2/vendor/pulse/pulse-h5007nl.pdf", "v2/vendor/rp2040/rpi-rp2040-datasheet.pdf", "v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf",
    "v2/vendor/diodes/diodes-ap64500.pdf", "v2/vendor/ti/lm5176-datasheet.pdf",
    "v2/docs/records/l8gnd/apply_gen_sch_a_gnd002.py", "v2/docs/records/l8gnd/apply_gen_sch_b_gnd002.py",
    "v2/docs/records/l8gnd/apply_gen_sch_a_hotr1.py", "v2/docs/records/l8gnd/check_gnd002_netlist.py",
    "v2/docs/records/l8gnd/footprints/ChassisLug_M4_CHASSIS.kicad_mod",
] + ["v2/docs/records/%s/apply_gen_sch_a_%s.py" % rn for rn in POWER_ORDER]

# The keeper's figures (apply_gen_sch_a_hotr1.py). Classes: MAKER (printed in a held sheet), INFERRED (derived from a printed
# figure under a stated assumption), BOUND (a limit this record states and the design is held to).
KEEPER = {
    "v33_min": (3.2, "BOUND", "board A's +3V3 at its low end (TPS62933, 3.3 V from 31.6k/10k); the keeper is judged at 3.2 V"),
    "voh_drop": (0.2, "MAKER", "SN74LVC08A VOH at least VCC - 0.2 V at IOH -100 uA, 2.7 to 3.6 V (TI SCAS283W)"),
    "vol": (0.2, "MAKER", "SN74LVC08A VOL at most 0.2 V at IOL 100 uA (TI SCAS283W)"),
    "rk": (4700.0, "BOUND", "the keeper's feedback resistor R230 to R232, 4.7 k"),
    "rpd_min": (50e3, "MAKER", "RP2040 pad pull-down RPD 50 to 80 kOhm (RP2040 datasheet Table 625); the reset state of every pad, PDE 0x1 (2.19.6.3)"),
    "rpd_max": (80e3, "MAKER", "the same row's maximum"),
    "rpull": (100e3, "MAKER", "R30, R34, R38, 100 k to GND (gen_sch_a.py)"),
    "ien_bound": (20e-6, "INFERRED", "the enable inputs' current at the held level: AP64500 IEN 5.5 uA typical at VEN 1.5 V and 1 to 2 uA at 1 V (Diodes DS41979), no figure at 2.6 V; bounded at 20 uA"),
    "vih": (2.0, "MAKER", "VIH 2.0 V: SN74LVC08A at 2.7 to 3.6 V (SCAS283W) and the RP2040 at IOVDD 3.3 V (Table 625)"),
    "vil": (0.8, "MAKER", "VIL 0.8 V: the same two rows"),
    "ap_ven_h_max": (1.25, "MAKER", "AP64500 VEN_H at most 1.25 V (DS41979)"),
    "ap_ven_l_min": (1.03, "MAKER", "AP64500 VEN_L at least 1.03 V (DS41979)"),
    "lm_ven_op_max": (1.29, "MAKER", "LM5176 VEN(OP) rising at most 1.29 V (TI SNVSAI1D)"),
    "lm_ven_stby_min": (0.55, "MAKER", "LM5176 VEN(STBY) at least 0.55 V (TI SNVSAI1D)"),
    "rp_voh_min": (2.62, "MAKER", "RP2040 VOH at least 2.62 V at IOVDD 3.3 V, IOH 2, 4, 8 or 12 mA (Table 625)"),
    "rp_vol_max": (0.5, "MAKER", "RP2040 VOL at most 0.5 V at IOVDD 3.3 V, IOL 2, 4, 8 or 12 mA (Table 625)"),
    "rp_drive_ma": (4.0, "MAKER", "the pad's default drive, DRIVE reset 0x1 = 4 mA (RP2040 datasheet 2.19.6.3)"),
    "v33_nom": (3.3, "MAKER", "the panel's IOVDD and board A's +3V3 nominal"),
}


def keeper():
    k = {n: v for n, (v, _c, _w) in KEEPER.items()}
    par = lambda a, b: a * b / (a + b)
    out = {}
    for tag, rpd in (("rpd_min", k["rpd_min"]), ("rpd_max", k["rpd_max"])):
        rdown = par(rpd, k["rpull"])
        voh = k["v33_min"] - k["voh_drop"]
        v_high_div = voh * rdown / (k["rk"] + rdown)
        v_high = v_high_div - k["ien_bound"] * par(k["rk"], rdown)
        v_low = k["vol"] * rdown / (k["rk"] + rdown)
        out[tag] = dict(rdown=rdown, v_high_div=v_high_div, v_high=v_high, v_low=v_low)
    out["i_override_ma"] = 1e3 * k["v33_nom"] / k["rk"]
    out["i_sink_held_high_ma"] = 1e3 * (k["v33_nom"] - k["voh_drop"]) / k["rk"]
    out["margin_high_vih"] = out["rpd_min"]["v_high"] - k["vih"]
    out["margin_high_en"] = out["rpd_min"]["v_high"] - max(k["ap_ven_h_max"], k["lm_ven_op_max"])
    out["margin_low_vil"] = k["vil"] - out["rpd_min"]["v_low"]
    out["margin_low_en"] = min(k["ap_ven_l_min"], k["lm_ven_stby_min"]) - out["rpd_min"]["v_low"]
    out["panel_drive_high_margin"] = k["rp_voh_min"] - k["vih"]
    out["panel_drive_low_margin"] = k["vil"] - k["rp_vol_max"]
    out["drive_ok"] = out["i_override_ma"] < k["rp_drive_ma"] and out["i_sink_held_high_ma"] < k["rp_drive_ma"]
    return out


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def draft(rec, name, board):
    return os.path.join(RECS, rec, "apply_gen_sch_%s_%s.py" % (board, name))


def run(script, target, write=True):
    r = subprocess.run([sys.executable, "-B", script, target] + (["--write"] if write else []), capture_output=True)
    return r.returncode, r.stderr.decode("utf-8", "replace").strip().splitlines()[-1:] or [""]


STMT = re.compile(r'^\s*(ic|part|c|r|tp|nfet|vh2|synth|q|esd)\(\s*"([A-Z#][A-Z0-9_]*)"\s*,(.*)$')
TOKEN = re.compile(r"\b([RCDLQUH]\d{1,3}|J_[A-Z0-9]+|TP\d{1,3})\b(?!-)")
NETSTR = re.compile(r'"([A-Z+][A-Z0-9_+]*)"')


def strip_comments(s):
    return "\n".join("" if l.lstrip().startswith("#") else l.split("#")[0] for l in s.splitlines())


def calls(text):
    """ref -> (helper, the upper-case quoted strings of the call: nets, land keys and codes) for every part call in part-call
    position, comments stripped; a line's several statements are read one by one (the generators put two or three calls on a line)."""
    out = {}
    for line in strip_comments(text).splitlines():
        for stmt in line.split(";"):
            m = STMT.match(stmt)
            if not m or m.group(2).startswith("#"):
                continue
            helper, ref, rest = m.groups()
            out[ref] = (helper, NETSTR.findall(rest))
    return out


def added_calls(before, after):
    cb, ca = calls(before), calls(after)
    return {r: ca[r] for r in sorted(set(ca) - set(cb))}


def added_tokens(before, after):
    return set(TOKEN.findall(strip_comments(after))) - set(TOKEN.findall(strip_comments(before)))


def multiline_calls(text):
    """The ic() calls span two lines; read them whole: ref -> sorted set of net names in its pin map."""
    out = {}
    for m in re.finditer(r'ic\(\s*"(U\d+)"\s*,\s*\d+\s*,\s*"[^"]*"\s*,\s*"[^"]*"\s*,\s*\{(.*?)\}', strip_comments(text), re.S):
        out[m.group(1)] = sorted(set(re.findall(r':\s*"([^"]+)"', m.group(2))) - {"NC"})
    return out


def fixture_a():
    """A minimal board A netlist carrying GND-002's two changes as drafted."""
    return b"""(export (version "E")
  (components
    (comp (ref "H1") (value "M4 bonding pad") (footprint "meshsat:ChassisLug_M4_CHASSIS"))
    (comp (ref "R229") (value "0R 2512 (CHASSIS bond link)") (footprint "Resistor_SMD:R_2512_6332Metric"))
    (comp (ref "J_DOCK") (value "dock") (footprint "meshsat:POGO12"))
    (comp (ref "C4") (value "1u") (footprint "Capacitor_SMD:C_0603_1608Metric")))
  (nets
    (net (code "1") (name "/CHASSIS") (node (ref "H1") (pin "1")) (node (ref "R229") (pin "1")))
    (net (code "2") (name "GND") (node (ref "R229") (pin "2")) (node (ref "J_DOCK") (pin "1")) (node (ref "C4") (pin "2")))
    (net (code "3") (name "/VBAT") (node (ref "C4") (pin "1")))))
"""


def fixture_b():
    """A minimal board B netlist carrying GND-002's two changes as drafted."""
    return b"""(export (version "E")
  (components
    (comp (ref "C33") (value "1n 2kV") (footprint "Capacitor_SMD:C_1812_4532Metric"))
    (comp (ref "R9") (value "75") (footprint "Resistor_SMD:R_0603_1608Metric"))
    (comp (ref "R10") (value "75") (footprint "Resistor_SMD:R_0603_1608Metric"))
    (comp (ref "J_ETH") (value "RJ45") (footprint "Connector_RJ:RJ45_Amphenol_RJHSE5380"))
    (comp (ref "T1") (value "H5007NL") (footprint "meshsat:H5007")))
  (nets
    (net (code "1") (name "/CHASSIS") (node (ref "C33") (pin "2")) (node (ref "J_ETH") (pin "SH")))
    (net (code "2") (name "/BOB") (node (ref "C33") (pin "1")) (node (ref "R9") (pin "2")) (node (ref "R10") (pin "2")))
    (net (code "3") (name "/MCT3") (node (ref "R9") (pin "1")) (node (ref "T1") (pin "18")))
    (net (code "4") (name "/MCT4") (node (ref "R10") (pin "1")) (node (ref "T1") (pin "15")))
    (net (code "5") (name "GND") (node (ref "T1") (pin "1")))))
"""


def main():
    w = sys.stdout.write
    w("l8gnd_drafts: the Layer 8 record l8gnd's drafts proved on scratch copies (MESHSAT-1357)\n")
    w("prototype design; nothing built, powered or measured; nothing applied to the tree\n\n")
    w("1. INPUTS, pinned by sha256\n")
    missing = [p for p in INPUTS if not os.path.isfile(os.path.join(ROOT, p))]
    if missing:
        sys.stderr.write("l8gnd_drafts: inputs missing: %s\n" % missing)
        return 3
    for p in INPUTS:
        w("%s %s\n" % (sha(os.path.join(ROOT, p))[:16], p))

    # the record's own drafts as modules (their EDITS, ADDS, NETS)
    mods = {}
    for rec, name in MINE_A + [("l8gnd", "b_gnd002")]:
        path = draft(rec, name, "a") if name != "b_gnd002" else draft(rec, "gnd002", "b")
        sp = importlib.util.spec_from_file_location("l8gnd_" + name, path)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        mods[name] = m

    gen_a = open(GEN_A, encoding="utf-8").read()
    gen_b = open(GEN_B, encoding="utf-8").read()
    w("\n2. WHAT EACH DRAFT ADDS (part calls read from the text each draft writes, comments stripped)\n")
    for name, gen, letter in (("gnd002", gen_a, "a"), ("hotr1", gen_a, "a"), ("b_gnd002", gen_b, "b")):
        m = mods[name]
        new = m.patched(gen)
        w("  %s on board %s: %d edit(s), adds %s, nets %s\n" % (m.NAME, letter.upper(), len(m.EDITS),
                                                             ", ".join(getattr(m, "ADDS", ())) or "no part", ", ".join(getattr(m, "NETS", ()))))
        for ref, (helper, strs) in added_calls(gen, new).items():
            if strs:    # an ic() spans two lines and is listed from its pin map below
                w("    %s(%s): %s\n" % (helper, ref, " | ".join(strs[:6])))
        for ref, nets in multiline_calls(new).items():
            if ref not in multiline_calls(gen):
                w("    ic(%s) pins on: %s\n" % (ref, ", ".join(nets)))
        if letter == "b":
            before = calls(gen).get("C33", ("", []))[1]
            after = calls(new).get("C33", ("", []))[1]
            w("    C33: %s -> %s\n" % (" | ".join(before), " | ".join(after)))
            sh_b = re.search(r'"SH":\s*"([A-Z]+)"\}\)', strip_comments(gen)); sh_a = re.search(r'"SH":\s*"([A-Z]+)"\}\)', strip_comments(new))
            w("    J_ETH SH pin: %s -> %s\n" % (sh_b.group(1) if sh_b else "?", sh_a.group(1) if sh_a else "?"))

    w("\n3. THE KEEPER'S ARITHMETIC (apply_gen_sch_a_hotr1.py)\n")
    for n, (v, c, why) in KEEPER.items():
        w("  %-16s %-10g %-8s %s\n" % (n, v, c, why))
    K = keeper()
    for tag in ("rpd_min", "rpd_max"):
        d = K[tag]
        w("  with %s: pad pull-down in parallel with the 100 k = %.2f k; held HIGH %.3f V (divider %.3f V less the enable current's drop); held LOW %.3f V\n"
          % (tag, d["rdown"] / 1e3, d["v_high"], d["v_high_div"], d["v_low"]))
    w("  held HIGH margin over VIH 2.0 V: %.3f V; over the enables' highest ON threshold (1.29 V): %.3f V\n" % (K["margin_high_vih"], K["margin_high_en"]))
    w("  held LOW margin under VIL 0.8 V: %.3f V; under the enables' lowest OFF threshold (0.55 V): %.3f V\n" % (K["margin_low_vil"], K["margin_low_en"]))
    w("  the panel overriding the keeper: %.2f mA to drive against a held output, %.2f mA to sink a held high, both under the pad's 4 mA default drive: %s\n"
      % (K["i_override_ma"], K["i_sink_held_high_ma"], "OK" if K["drive_ok"] else "NOT OK"))
    w("  the panel's drive seen by the gate and the enables: high at least 2.62 V (margin %.2f V over VIH), low at most 0.5 V (margin %.2f V under VIL)\n"
      % (K["panel_drive_high_margin"], K["panel_drive_low_margin"]))

    w("\n4. COMPOSITION ON BOARD A (scratch copies of gen_sch_a.py; OK = the draft applied and the result parses)\n")
    mine = [draft("l8gnd", n, "a") for _r, n in MINE_A]
    theirs = [draft(r, n, "a") for r, n in POWER_ORDER]
    with tempfile.TemporaryDirectory() as d:
        def fresh(tag):
            p = os.path.join(d, tag + ".py"); shutil.copy(GEN_A, p); return p
        def seq(tag, scripts):
            p = fresh(tag); res = []
            for s in scripts:
                rc, err = run(s, p)
                res.append((os.path.relpath(s, RECS), "OK" if rc == 0 else "REFUSED (%s)" % err[0]))
                if rc != 0: break
            return p, res
        p1, r1 = seq("theirs_then_mine", theirs + mine)
        w("  L4-E9's order then this record's two:\n")
        for s, v in r1: w("    %-40s %s\n" % (s, v))
        p2, r2 = seq("mine_then_theirs", mine + theirs)
        w("  this record's two first, then L4-E9's order (every anchor of theirs survives this record's edits):\n")
        for s, v in r2: w("    %-40s %s\n" % (s, v))
        same_parts = sorted(calls(open(p1, encoding="utf-8").read())) == sorted(calls(open(p2, encoding="utf-8").read()))
        w("  the two results carry the same part calls: %s\n" % ("YES" if same_parts else "NO"))
        w("  each power draft alone after this record's two:\n")
        for s in theirs:
            p = fresh("alone_" + os.path.basename(s)[:-3])
            ok = all(run(m_, p)[0] == 0 for m_ in mine)
            rc, err = run(s, p)
            pre = [t for t in theirs if t != s and os.path.basename(s) == "apply_gen_sch_a_bank.py" and os.path.basename(t) == "apply_gen_sch_a_r12.py"]
            if rc != 0 and pre:   # the bank draft refuses a generator without R12 by design: give it R12 first
                p = fresh("alone2_" + os.path.basename(s)[:-3])
                ok = all(run(m_, p)[0] == 0 for m_ in mine) and run(pre[0], p)[0] == 0
                rc, err = run(s, p)
                w("    %-40s %s (after r12, which it requires)\n" % (os.path.relpath(s, RECS), "OK" if ok and rc == 0 else "REFUSED (%s)" % err[0]))
            else:
                w("    %-40s %s\n" % (os.path.relpath(s, RECS), "OK" if ok and rc == 0 else "REFUSED (%s)" % err[0]))
        w("  this record's two in either order:\n")
        for order in (mine, mine[::-1]):
            p = fresh("order_" + "_".join(os.path.basename(x)[13:-3] for x in order))
            rs = [run(s, p)[0] for s in order]
            w("    %-40s %s\n" % (" then ".join(os.path.basename(x)[13:-3] for x in order), "OK" if all(r == 0 for r in rs) else "REFUSED"))

        w("\n5. DESIGNATORS ADDED PER BOARD A DRAFT (part-call position and tokens outside comments; H pads included)\n")
        added = {}
        p = fresh("desig")
        before = open(p, encoding="utf-8").read()
        for s in theirs + mine:
            rc, err = run(s, p)
            after = open(p, encoding="utf-8").read()
            new_calls = set(added_calls(before, after)) | set(multiline_calls(after)) - set(multiline_calls(before))
            added[os.path.relpath(s, RECS)] = (set(new_calls) | added_tokens(before, after)) if rc == 0 else set()
            before = after
        for s in theirs + mine:
            k = os.path.relpath(s, RECS)
            w("  %-40s %s\n" % (k, ", ".join(sorted(added[k])) or "none"))
        clash = []
        names = sorted(added)
        for i, x in enumerate(names):
            for y in names[i + 1:]:
                both = added[x] & added[y]
                if both: clash.append((x, y, sorted(both)))
        w("  pairwise intersections: %s\n" % ("none (DISJOINT)" if not clash else "; ".join("%s and %s both add %s" % c for c in clash)))

        w("\n6. BOARD B (a scratch copy of gen_sch_b.py)\n")
        pb = os.path.join(d, "b.py"); shutil.copy(GEN_B, pb)
        rc, err = run(draft("l8gnd", "gnd002", "b"), pb)
        w("  apply_gen_sch_b_gnd002.py: %s; no other record drafts board B, so there is no order to keep\n" % ("OK" if rc == 0 else "REFUSED (%s)" % err[0]))
        tb = open(pb, encoding="utf-8").read()
        w("  C33 after: %s; J_ETH SH after: %s; part calls added: %s\n"
          % (" | ".join(calls(tb)["C33"][1]), re.search(r'"SH":\s*"([A-Z]+)"\}\)', strip_comments(tb)).group(1), ", ".join(sorted(added_calls(gen_b, tb))) or "none"))

    w("\n7. THE NETLIST CHECK (check_gnd002_netlist.py)\n")
    sp = importlib.util.spec_from_file_location("l8gnd_check", os.path.join(HERE, "check_gnd002_netlist.py"))
    chk = importlib.util.module_from_spec(sp); sp.loader.exec_module(chk)
    w("  on the committed netlists:\n")
    buf = io.StringIO(); chk.run(chk.committed(ROOT), ROOT, buf)
    for l in buf.getvalue().splitlines(): w("    %s\n" % l)
    w("  on fixture netlists that carry the drafted changes (built inside this script, not files of the tree):\n")
    for letter, fx in (("a", fixture_a()), ("b", fixture_b())):
        v, lines = chk.judge(letter, chk.read_netlist(fx))
        for l in lines: w("    %s\n" % l)
        w("    fixture %s: %s\n" % (letter.upper(), v))
    w("\nEND\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
