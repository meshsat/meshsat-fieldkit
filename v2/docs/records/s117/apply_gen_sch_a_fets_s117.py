#!/usr/bin/env python3
"""S-117's finding F1 answered in board A's generator (stream s117, second issue, MESHSAT-1357, 29 September 2026): the
charger U3's four power FETs chosen for its own 6 V gate drive. DRAFT for board A's generator owner; the author ran --check
only. Apply AFTER apply_gen_sch_a_s117.py (either order works: the anchors do not overlap), in the same regeneration.

What it writes into v2/ecad/tools/gen_sch_a.py (every figure in v2/docs/records/s117/efficiency.out; the choice is the
session decision drafted by apply_decision_fets_s117.py):
  Q7   CSD18510Q5B 40 V N-FET  ->  CSD17578Q5A 30 V N-FET   (the buck leg's hard-switched high side)
  Q8   CSD18510Q5B 40 V N-FET  ->  CSD17577Q5A 30 V N-FET   (the buck leg's synchronous low side)
  Q9   CSD18510Q5B 40 V N-FET  ->  CSD17577Q5A 30 V N-FET   (the boost leg's low side)
  Q10  CSD18510Q5B 40 V N-FET  ->  CSD17577Q5A 30 V N-FET   (the boost leg's high side, on in buck mode)
Nets, land (the PowerPAK SO-8 land "PPAK" of nfet()) and pin map are unchanged. TI SLPS526 (CSD17578Q5A, March 2015) and
SLPS516 (CSD17577Q5A, August 2014), held back by TI's terms and pinned in v2/vendor/sources.txt: 5.1 p.3, Figures 4, 5 and
7 p.5, 7.2 p.9. TI SLUSE66A (BQ25731): 8.5 pp.11 and 16, Table 9-3 p.27, 10.2.2.6 pp.86 to 88.

HOW IT GUARDS. The old for-loop line must occur exactly once and differ from the new text; the result must parse (ast);
the parsed loop must carry exactly the four (reference, gate net, drain net, source net, value) tuples below and call
nfet(_qr, _v, _g, _d, _s) as its body; no other line may name CSD17578Q5A or CSD17577Q5A before; --check does it all in
memory and writes nothing; the write path creates an exclusive marker beside this file first, so a second run refuses.
Board A is regenerated on the KiCad box afterwards and readback_s117.py --fets reads the regenerated netlist.

Usage: python3 apply_gen_sch_a_fets_s117.py [--check]"""
import argparse, ast, hashlib, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
GEN = os.path.join(TOP, "v2/ecad/tools/gen_sch_a.py")
MARKER = os.path.join(HERE, "apply_gen_sch_a_fets_s117.applied")
FAST, LOWR = "CSD17578Q5A 30 V N-FET", "CSD17577Q5A 30 V N-FET"

OLD = ('for _qr, _g, _d, _s in (("Q7", "CH_HIDRV1", "CH_ACN", "CH_SW1"), ("Q8", "CH_LODRV1", "CH_SW1", "GND"), '
       '("Q9", "CH_LODRV2", "CH_SW2", "GND"), ("Q10", "CH_HIDRV2", "VBAT", "CH_SW2")): nfet(_qr, "CSD18510Q5B 40 V N-FET", '
       '_g, _d, _s)\n')
NEW = '''# S-117'S FINDING F1 (stream s117, second issue, 29 September 2026, MESHSAT-1357; the S-117 F1 session decision in
# tools/pcb_decisions.yaml): THE CHARGER'S FETS ARE CHOSEN FOR THE BQ25731'S OWN 6 V GATE DRIVE. All four were CSD18510Q5B
# (40 V, 0.79 mOhm, about 75 nC of gate charge at 6 V, SLPS632), a part for a slow high-current switch. The BQ25731 drives
# its FETs from REGN (SLUSE66A pin table pp.5 and 6); in buck mode Q7 and Q8 switch every cycle (Table 9-3, page 27), so
# REGN supplies 2 x Qg x fS: 60 mA at a typical 400 kHz and up to 89 mA at the makers' maxima, against VREGN_REG's 0 to 60
# mA condition and IREGN_LIM's 50 mA minimum (8.5, page 11; TI's own switching tests there use "MOSFET Qg = 4 nC"). And
# TI's Equations 6 to 22 (pages 86 to 88) put 4.8 W in Q7 at the energy model's peak hour: the charger reads 0.943 there,
# 0.92 to 0.96 across the readings, where the energy chain carries 0.98. Q7, the hard-switched high side of the buck leg,
# becomes a CSD17578Q5A (30 V; Qg 10.3 nC at 6 V, Qgd 2.0 and Qgs 3.1 nC, Qrr 6.5 nC, 6.6 mOhm at 6 V: SLPS526 p.3 and
# Figures 4 and 7, p.5). Q8, the synchronous low side, and Q9 and Q10, the boost leg that sits on in buck mode and switches
# in the buck-boost region whose threshold TI does not state (9.3.10, page 27), become CSD17577Q5A (30 V; 16 nC at 6 V, Qrr
# 8.2 nC, 3.9 mOhm at 6 V: SLPS516 p.3 and p.5). REGN then supplies 10.5 mA typical in buck mode and 36.5 mA at the
# maxima with all four switching at 460 kHz; the charger reads 0.979 at the peak by TI's method (0.972 to 0.983 across the
# readings; the day's energy-weighted 0.979 at entry E2), R16 and R17 counted, core loss excluded, and Q7 dissipates 1.0
# to 1.5 W there (v2/docs/records/s117/efficiency.out). 30 V at VBUS20's 20.7 V maximum is inside derate.py's 20 percent
# screen (24.8 V); the switch node's ringing is a layout and bench item. Both are TI's SON 5 x 6 mm (Q5A) with the Q5B's
# pin order (1 to 3 source, 4 gate, the drain tab) on the PowerPAK SO-8 land this board already uses for the Q5B parts;
# the land's fit to the Q5A pattern (SLPS526 and SLPS516 7.2, page 9) and both order codes are the parts stream's to
# confirm. The datasheets are held back by TI's terms (v2/vendor/sources.txt; records/s117/fetch_held_back.py).
for _qr, _g, _d, _s, _v in (("Q7", "CH_HIDRV1", "CH_ACN", "CH_SW1", "CSD17578Q5A 30 V N-FET"), ("Q8", "CH_LODRV1", "CH_SW1", "GND", "CSD17577Q5A 30 V N-FET"), ("Q9", "CH_LODRV2", "CH_SW2", "GND", "CSD17577Q5A 30 V N-FET"), ("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", "CSD17577Q5A 30 V N-FET")): nfet(_qr, _v, _g, _d, _s)
'''
EXPECT = [("Q7", "CH_HIDRV1", "CH_ACN", "CH_SW1", FAST), ("Q8", "CH_LODRV1", "CH_SW1", "GND", LOWR),
          ("Q9", "CH_LODRV2", "CH_SW2", "GND", LOWR), ("Q10", "CH_HIDRV2", "VBAT", "CH_SW2", LOWR)]


def refuse(m):
    print("apply_gen_sch_a_fets_s117: REFUSED: %s" % m)
    sys.exit(2)


def sha16(b): return hashlib.sha256(b.encode("utf-8")).hexdigest()[:16]


def charger_loops(tree):
    """The for-loops whose iterable is a literal tuple of tuples naming Q7: [(target names, the tuples, the body call)]."""
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.For) or not isinstance(n.iter, ast.Tuple): continue
        try: rows = ast.literal_eval(n.iter)
        except ValueError: continue
        if not rows or not isinstance(rows[0], tuple) or rows[0][0] != "Q7": continue
        tgt = [e.id for e in n.target.elts] if isinstance(n.target, ast.Tuple) else []
        body = n.body[0].value if n.body and isinstance(n.body[0], ast.Expr) else None
        out.append((tgt, list(rows), body))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    if not a.check and os.path.exists(MARKER): refuse("the marker %s exists (a second run)" % os.path.basename(MARKER))
    src = open(GEN, encoding="utf-8").read()
    ast.parse(src)
    if "CSD17578Q5A" in src or "CSD17577Q5A" in src: refuse("the generator already names a CSD17578Q5A or CSD17577Q5A")
    if src.count(OLD) != 1: refuse("the charger's FET line occurs %d times, not once" % src.count(OLD))
    out = src.replace(OLD, NEW)
    if out == src: refuse("nothing changed")
    loops = charger_loops(ast.parse(out))
    if len(loops) != 1: refuse("%d charger FET loops after the change, not one" % len(loops))
    tgt, rows, body = loops[0]
    if tgt != ["_qr", "_g", "_d", "_s", "_v"]: refuse("the loop's targets read %s" % tgt)
    if rows != EXPECT: refuse("the loop's rows read %r" % rows)
    if not (isinstance(body, ast.Call) and isinstance(body.func, ast.Name) and body.func.id == "nfet"
            and [x.id for x in body.args] == ["_qr", "_v", "_g", "_d", "_s"] and not body.keywords):
        refuse("the loop's body is not nfet(_qr, _v, _g, _d, _s)")
    if "\u2014" in NEW or "\u2013" in NEW: refuse("a dash character")
    print("apply_gen_sch_a_fets_s117: gen_sch_a.py sha256/16 %s -> %s; Q7 %s, Q8 to Q10 %s; nets, land and pin map unchanged; "
          "the loop read back from the parsed source" % (sha16(src), sha16(out), FAST, LOWR))
    if a.check:
        print("CHECK ONLY: 1 anchor, 4 rows read back, 1 generator; no writes, no marker.")
        return 0
    fd = os.open(MARKER, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, ("gen_sch_a.py %s -> %s\n" % (sha16(src), sha16(out))).encode())
    os.close(fd)
    open(GEN, "w", encoding="utf-8").write(out)
    if open(GEN, encoding="utf-8").read() != out: refuse("the written file differs from the text validated")
    print("APPLIED: v2/ecad/tools/gen_sch_a.py written once; marker %s. Next: apply_intent_checks_s117.py, then regenerate "
          "board A (schematic phase) and run readback_s117.py --fets." % os.path.basename(MARKER))
    return 0


if __name__ == "__main__":
    sys.exit(main())
