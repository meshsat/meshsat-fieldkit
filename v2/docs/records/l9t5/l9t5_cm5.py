#!/usr/bin/env python3
"""l9t5_cm5.py: Layer 9 record l9t5, task T5 round 4 part 3: finding SDR3-F02 assessed (MESHSAT-1357, 4 October 2026). PROTOTYPE
DESIGN: nothing in this kit has been built, bought, powered or measured.

SDR3-F02 (the three-SDR research, fnd/sdr3 at 72457223, cited as text only): the Compute Module 5 datasheet held in the tree prints
"Power supply designs should accommodate 5 V at up to 2.5 A" (its appendix B.3), while the budgets take a module at the generator's
declared 1.6 A and the generator's comment says no maximum is given. This script reads the sheet, says what kind of figure that is,
and computes what the budget's states, the slot stages' limits (L9P-F02) and the case row C-ALLTX rev 3 owe to it: each as a
LABELLED SCENARIO or a bound, never as a change of a case row (a case row's change is the coordinator's). It writes nothing but
its output (l9t5_cm5.out, regenerated with _bin/regen_out.py).

Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_cm5.py"""
import hashlib
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
PINS = {"cm5": "v2/vendor/cm5/cm5-datasheet.pdf", "gen_b": "v2/ecad/tools/gen_sch_b.py", "rvpwr": "v2/docs/records/rv-pwr/pwr_budget.py",
        "budget": "v2/docs/records/l9pwr/l9pwr_budget.py", "budget_out": "v2/docs/records/l9pwr/l9pwr_budget.out",
        "cases": "v2/docs/records/l9t5/inputs/coordinator-cases-2026-10-04-rev3.md"}


def refuse(msg):
    sys.stderr.write("l9t5_cm5: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def sha(rel, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:n]


def text(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def flat(t):
    return " ".join(t.split())


def main():
    for rel in PINS.values():
        if not os.path.isfile(os.path.join(ROOT, rel)):
            refuse("input %s is missing" % rel)
    try:
        t = subprocess.run(["pdftotext", "-layout", os.path.join(ROOT, PINS["cm5"]), "-"], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    except (OSError, subprocess.CalledProcessError) as e:
        refuse("pdftotext could not read the CM5 sheet (%s)" % e)
    rel_no = need(t, r"Release\s+(\d+)", "the sheet's release").group(1)
    f = flat(t)
    m = need(f, r"B\.3\. Power budget (CM5 delivers significantly more performance than CM4, and therefore consumes more power\. Power supply designs should "
                r"accommodate 5 V at up to ([\d.]+) A\. If this creates an issue with an existing board design, lowering the CPU clock rate can reduce the peak "
                r"power consumption\.)", "appendix B.3")
    b3, a_design = m.group(1), float(m.group(2))
    need(f, r"Appendix B\. CM4 and CM5 differences", "appendix B's title")
    i_idle = float(need(t, r"Iidle\s+Idle current\s+PMIC_ENABLE > 2 V\s+-\s+(\d+)\s+-\s+mA", "Table 9's idle row").group(1)) / 1000.0
    i_op = float(need(t, r"Iload\s+Operation current\s+PMIC_ENABLE > 2 V\s+-\s+(\d+)\s+-\s+mA", "Table 9's operation row (typical only)").group(1)) / 1000.0
    need(f, r"Operating power consumption is typically around 900 mA, but this depends on the operating system and running tasks", "section 3.3's operating figure")
    gb = text(PINS["gen_b"])
    need(gb, r"typical, no maximum given\. Ours is declared at 1\.6 A, which is the typical with headroom for the SoC under", "the generator's comment")
    rv = text(PINS["rvpwr"])
    need(rv, r"operation 900 mA typical at 5 V, no maximum; 8 W = board B's declared 1\.6 A", "rv-pwr's CM5 source line")
    c = flat(text(PINS["cases"]))
    need(c, r"the compute modules at typical \(4\.5 W each\) is CONOPS's definition, but nothing drawn holds them there", "C-ALLTX's unsettled item on the modules")
    sp = importlib.util.spec_from_file_location("l9pwr_budget_for_cm5", os.path.join(ROOT, PINS["budget"]))
    bm = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(bm)
    B = bm.compute()
    pb, F, Dc = B["d11_rv_record"], B["F"], B["cfgs"]["DRAFTED"]
    w_design, w_high, w_typ = 5.0 * a_design, 8.0, bm.CASE_CM5
    ca = B["calltx"]
    row_typ, row_8 = ca["new"], ca["cm5_8"]
    row_d = bm.case_row(pb, F, Dc, bm.case_vals(Dc, cm5=w_design)[0])
    out = []
    w = out.append
    w("l9t5_cm5: Layer 9 record l9t5, round 4 part 3: finding SDR3-F02, the Compute Module 5's supply design figure (MESHSAT-1357)")
    w("prototype design; nothing built, bought, powered or measured; a case row's change is the coordinator's and none is made here")
    w("")
    w("1. INPUTS, pinned by sha256")
    for rel in PINS.values():
        w("   %s %s" % (sha(rel), rel))
    w("")
    w("2. WHAT THE SHEET PRINTS (Raspberry Pi Compute Module 5 datasheet, Release %s)" % rel_no)
    w("   appendix B, 'CM4 and CM5 differences', B.3 'Power budget': '%s'" % b3)
    w("   section 4.3.3, Table 9: idle %.0f mA and operation %.0f mA, TYPICAL; its Minimum and Maximum columns are empty; section 3.3: 'Operating" % (i_idle * 1000, i_op * 1000))
    w("   power consumption is typically around 900 mA, but this depends on the operating system and running tasks'")
    w("   WHAT KIND OF FIGURE %.1f A IS: a SUPPLY DESIGN FIGURE, the maker's advice to a carrier's designer in a migration appendix, tied by its" % a_design)
    w("   own next sentence to the module's PEAK power consumption. It is not a row of the consumption table, not a printed maximum and not a")
    w("   typical; the sheet prints no consumption limit at all. So it is the nearest figure the maker gives to an upper bound of a module's")
    w("   draw, and a supply sized under it is sized under the maker's own advice")
    w("   the tree: gen_sch_b.py declares a module at 1.6 A ('the typical with headroom') and says 'no maximum given', which is true of Table 9 and")
    w("   silent on B.3; rv-pwr takes %.1f W typical and %.1f W HIGH (1.6 A at 5 V); the maker's figure is %.1f W, %.1f W over the budget's HIGH" % (w_typ, w_high, w_design, w_design - w_high))
    w("")
    w("3. THE SLOT STAGES (L9P-F02: slots 1 and 3 on board A's LM5176 stages in record l8r2's draft; slot 2 on U5), each module at %.1f W" % w_design)
    w("   a LABELLED SCENARIO beside L9P-F02's rows, not a change of them: the stage's current at HIGH at the least load voltage with the module's")
    w("   HIGH figure (%.1f W, or the state's own where the budget puts less) replaced by %.1f W in every state the module is on, every other" % (w_high, w_design))
    w("   load as the budget has it, against the loop's least (PRINTED VSNS, DECLARED shunt):")
    worst, hc = {}, B["hc"]
    hi_vals = {}
    for rail in ("S1", "S2", "S3"):
        rows = []
        for k, x in sorted(B["stages"].items()):
            if k[0] != "DRAFTED" or k[2] != rail or not x["lm"]:
                continue
            if k[1] not in hi_vals:
                hi_vals[k[1]] = bm.run_state(Dc, hc, k[1], "hi")[0]
            mod = hi_vals[k[1]]["CM5 slot %s" % rail[1]]
            if mod < 0.0 or mod > w_high:
                refuse("the budget's HIGH for the module in slot %s, state %s, is %r W, outside 0 to %.1f W" % (rail[1], k[1], mod, w_high))
            d_i = (w_design - mod) / x["v_least"] if mod else 0.0
            rows.append((round(x["lim"][1] - x["i_least"] - d_i, 6), -mod, k[1], x["i_least"], d_i, x["lim"][1], x.get("start"), x.get("degraded")))
        if not rows:
            refuse("the budget carries no LM5176 stage for %s on DRAFTED" % rail)
        _, _, st, i0, d_i, lim, start, deg = min(rows)
        mg = lim - i0 - d_i
        if start is None or deg is None or not d_i:
            refuse("the worst state of %s carries no cooler rows or no module" % rail)
        worst[rail] = {"steady": mg, "start": lim - start - d_i, "deg": lim - deg - d_i, "state": st, "d_i": d_i, "lim": lim}
        w("   %s  worst state %-6s steady %.4f A as budgeted, %.4f A at the maker's figure (%+.4f A), against %.4f A: %+.4f A" % (rail, st, i0, i0 + d_i, d_i, lim, mg))
        w("       with a cooler's bounded start (record l8r2, a 100 us average) %.4f A: %+.4f A; with a degraded cooler %.4f A: %+.4f A" % (
            start + d_i, lim - start - d_i, deg + d_i, lim - deg - d_i))
    steady_ok = all(v["steady"] > 0 for v in worst.values())
    start_bad = sorted(r for r, v in worst.items() if v["start"] < 0)
    deg_least = min(v["deg"] for v in worst.values())
    slot_decl = need(gb, r'"U3%dA" % \(s - 1\): ([\d.]+),', "board B's declared module current")
    a_decl = float(slot_decl.group(1))
    blk = need(gb, r"_SLOT_LOADS = lambda s: \{\n(.*?)\n\}", "board B's slot loads", re.S).group(1)
    loads = [float(x) for x in re.findall(r'^\s+"[^"]+" % [^:]+: ([\d.]+),', blk, re.M)]
    if len(loads) != 6 or a_decl not in loads:
        refuse("board B's slot loads no longer read as six branches with the module among them")
    pk = need(gb, r'_intent\.rail\("\+5V_S%d" % _n, 5\.1, [\d.]+ if _n == 2 else [\d.]+, ([\d.]+) if _n == 2 else ([\d.]+), "J_5V_S%d" % _n, loads=_SLOT_LOADS\(_n\)', "board B's slot rail declaration")
    pk2, pk13 = float(pk.group(1)), float(pk.group(2))
    sum_decl = sum(loads)
    sum_design = sum_decl - a_decl + a_design
    w("   READ: at the maker's supply design figure every slot stage still carries its steady load (%s, least %+.4f A). With a cooler's bounded" % (
        "yes" if steady_ok else "NO", min(v["steady"] for v in worst.values())))
    w("   start coinciding %s; with a degraded cooler the least margin is %+.4f A." % (
        "the stage%s of %s pass%s the loop's least (PRINTED VSNS over the DECLARED shunt)" % (
            "s" if len(start_bad) > 1 else "", ", ".join(start_bad), "" if len(start_bad) > 1 else "es") if start_bad else "every stage stays under its loop's least", deg_least))
    w("   What the slot stages owe to it is a BOUND, and it is a finding: L9T5-F15 for record l8r2 (L9P-F02's conditions on the coolers' start")
    w("   are stated with the module at %.1f W) and for board B's generator owner (the declared %.1f A against the maker's %.1f A). The slot rail's" % (w_high, a_decl, a_design))
    w("   branches, as drawn in the tree's generator, sum to %.3f A against a declared peak of %.2f A (slot 2: %.2f A); with the module at the maker's" % (sum_decl, pk13, pk2))
    w("   figure they sum to %.3f A: over the %.3f A that the %.2f A declaration of slots 1 and 3 may carry (1.02 times the peak), inside slot 2's %.4f A." % (
        sum_design, 1.02 * pk13, pk13, 1.02 * pk2))
    w("   No draft is written here: neither the declaration nor L9P-F02's rows are this record's to change")
    w("")
    w("4. THE CASE ROW C-ALLTX REV 3 (its definition unchanged: the compute modules at typical, %.1f W, CONOPS 4a)" % w_typ)
    w("   the case:                                   %.3f W at VBAT, %.4f V rest needed at %.0f A (F01 / D-17 OPEN)" % (row_typ["p"], row_typ["need"], bm.CASE_I))
    w("   LABELLED SCENARIO, the budget's HIGH (%.1f W):  %.3f W, %.4f V (the row's own sensitivity)" % (w_high, row_8["p"], row_8["need"]))
    w("   LABELLED SCENARIO, the maker's figure (%.1f W): %.3f W, %.4f V (%+.4f V over REQ-018's %.1f V rest)" % (
        w_design, row_d["p"], row_d["need"], row_d["need"] - bm.CASE_V_REST, bm.CASE_V_REST))
    w("   what the case owes to it: nothing in its definition (typical is CONOPS's word). Its UNSETTLED item on the modules ('nothing drawn holds")
    w("   them there'; K4's 'no compute stress' has no numerical ceiling) gains an upper figure from the maker: unless firmware holds the modules'")
    w("   load, the all-transmit state can need %.4f V, not %.4f V. Whether the row quotes that scenario is the coordinator's" % (row_d["need"], row_typ["need"]))
    w("")
    w("5. THE BUDGET'S STATES")
    w("   rv-pwr's HIGH for a module (%.1f W) is the generator's allowance, not a maker's bound. Record l9pwr's HIGH totals are sums of maxima where" % w_high)
    w("   makers print them and of declared figures where they do not; for the modules the maker's design figure is %.1f W higher each, %.1f W for" % (w_design - w_high, 3 * (w_design - w_high)))
    w("   three at the loads. What the states owe: a labelled scenario row ('modules at the maker's supply design figure') beside HIGH, in the")
    w("   budget's next round; HIGH itself is not changed here, because L9P-F02's rows and D-11's scenario are stated on it")
    w("")
    w("6. THE ASSESSMENT")
    w("   SDR3-F02 is CONFIRMED as a finding: the figure exists, is the maker's, and is above every figure the tree uses for a module.")
    w("   - a supply design figure, not a consumption limit: it bounds what the SUPPLY should carry, and the slot stages do carry it steadily")
    w("   - C-ALLTX rev 3: a labelled scenario only (%.4f V); no change of the row is decided here" % row_d["need"])
    w("   - the slot stages (L9P-F02): a bound: steady inside (least %+.4f A), a cooler's start coinciding outside on %s (least %+.4f A),"
      % (min(v["steady"] for v in worst.values()), ", ".join(start_bad) or "no stage", min(v["start"] for v in worst.values())))
    w("     a degraded cooler at %+.4f A: L9T5-F15" % deg_least)
    w("   - the generator's comment and declaration: a finding for board B's generator owner (the comment cites Table 9 only)")
    w("   - what would settle it: the modules' measured peak input current under the kit's own workload (a bench row), or a firmware ceiling on")
    w("     the CPU clock, which the maker's own sentence names as the lever ('lowering the CPU clock rate can reduce the peak power consumption')")
    w("")
    pred = {
        "the sheet's B.3 sentence and Table 9's typical-only rows are read from the held file": a_design == 2.5 and abs(i_op - 0.9) < 1e-9,
        "the maker's figure is over the budget's HIGH and over the generator's declared allowance": w_design > w_high and a_design > a_decl and abs(5.0 * a_decl - w_high) < 1e-9,
        "every slot stage holds its steady load at the maker's figure": steady_ok,
        "with a cooler's bounded start coinciding at least one slot stage passes its loop's least": bool(start_bad),
        "board B's slot loads with the module at the maker's figure pass what slots 1 and 3's declared peak may carry": sum_design > 1.02 * pk13 and sum_decl <= 1.02 * pk13 and sum_design <= 1.02 * pk2,
        "C-ALLTX rev 3 at the maker's figure needs more than at the budget's HIGH, which needs more than the case": row_d["need"] > row_8["need"] > row_typ["need"],
    }
    w("7. THE PREDICATES")
    for k, v in pred.items():
        w("   %-112s %s" % (k, "yes" if v else "NO"))
    w("")
    w("l9t5_cm5: done")
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 4


if __name__ == "__main__":
    sys.exit(main())
