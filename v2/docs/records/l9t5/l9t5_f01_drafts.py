#!/usr/bin/env python3
"""Record l9t5, P0-1 part 1c (MESHSAT-1357, 5 October 2026): the F01 / D-17 drafts (the PA drain-current cap, round 2 of the
selection) composed with every pending draft of boards A and D, regenerated without KiCad (record l8p's gen_netlist.py), read on the
netlists (check_f01_netlist.py), the old states that must not read DRAWN, the mutations that must FAIL, and the electrical acceptance on
C-ALLTX rev 3 with every term labelled. PROTOTYPE DESIGN, DESK ARITHMETIC: nothing is built, bought, powered or measured.

Run from the repository root: python3 v2/docs/records/l9t5/l9t5_f01_drafts.py (stdlib, PyYAML, pdftotext; about a minute, single
process). The committed output is regenerated only through _bin/regen_out.py. Nothing in the tree is written: every generator is a copy
in a temporary directory, and the tree's generators are checked unchanged at the end.
"""
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REC = os.path.join(ROOT, "v2", "docs", "records")
TOOLS = os.path.join(ROOT, "v2", "ecad", "tools")
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REC, "l8p"))
import check_f01_netlist as CHK  # noqa: E402
import check_l8p_netlist as L8P  # noqa: E402
import l9t5_paloop as PL  # noqa: E402

NET = {"a": "v2/ecad/pcb-a-power-a23/out/pcb-a-power.net", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs.net"}
PRJ = {"a": "pcb-a-power", "d": "pcb-d-aprs"}
# L4-E9's change-list order with each author's placement (V6's composition, the check of 5 October 2026): board A's round 3a to 3g,
# record l9t5's I-03 and T10 drafts, record l8r2's gndrtn, record efuse's u23ilm (round 2, EF-F03), THIS draft, d8dec31's mainpb (the
# last next-free taker), Layer 6's table
ORDER = {"a": ["l4e6/r12", "l4e11/guard", "l4e11/charger", "l4e4/r11", "l4e8/bank", "l4e4/r138", "l4e9/u17", "l8gnd/gnd002",
               "l8gnd/hotr1", "l8r2/d8v3", "l8r2/vbus20ov", "l8r2/packrtn", "l8r2/slotlm", "l8r2/fb01", "l8p/ptc", "l4e11/dd7",
               "l8p/thguard", "l9t5/iocbuck", "l9t5/iocpre", "l8r2/gndrtn", "efuse/u23ilm", "l9t5/paloop", "d8dec31/mainpb", "l6r2/lcsc"],
         "d": ["d8dec31/ptt", "l9t5/paloop", "l6r2/intent", "l6r2/lcsc"]}
OWN = {"a": "apply_gen_sch_a_paloop.py", "d": "apply_gen_sch_d_paloop.py"}
PINS = ["v2/docs/records/l9t5/apply_gen_sch_a_paloop.py", "v2/docs/records/l9t5/apply_gen_sch_d_paloop.py",
        "v2/docs/records/l9t5/check_f01_netlist.py", "v2/docs/records/l9t5/l9t5_paloop.py", "v2/docs/records/l9t5/l9t5_f01.py",
        "v2/docs/records/l8p/gen_netlist.py", "v2/ecad/tools/gen_sch_a.py", "v2/ecad/tools/gen_sch_d.py", NET["a"], NET["d"]]
# mutations of the fully composed generators: (board, label, old text, new text); each must not read DRAWN (FAIL or refused)
MUT = [
    ("a", "the sense bypassed: J_PA back on +13V8_PA", 'J_PA", "13.8 V to the PA module on the face plate (JST-VH, 16 AWG): + -", "+13V8_PAJ")',
     'J_PA", "13.8 V to the PA module on the face plate (JST-VH, 16 AWG): + -", "+13V8_PA")'),
    ("a", "positive feedback: the integrator's inputs swapped", '"2": "PA_INTN", "3": "PA_ISP"', '"2": "PA_ISP", "3": "PA_INTN"'),
    ("a", "the set point raised: R552 549 to 499 Ohm (7.38 A)", 'r("R552", "549 0.1% 25ppm"', 'r("R552", "499 0.1% 25ppm"'),
    ("a", "round 1's divider: no preload (51.1k over 10.0k)", 'r("R551", "2.80k 0.1% 25ppm", "PA_ISET", "PA_ISFB"); r("R552", "549 0.1% 25ppm"',
     'r("R551", "51.1k 0.1% 25ppm", "PA_ISET", "PA_ISFB"); r("R552", "10.0k 0.1% 25ppm"'),
    ("a", "U13's divider left at 1 %", ' rfb_val="10k 0.1%", rfb_tol="0.1%", bias="PA_OUT",', ' bias="PA_OUT",'),
    ("a", "U13's BIAS left behind R55", ' rfb_val="10k 0.1%", rfb_tol="0.1%", bias="PA_OUT",', ' rfb_val="10k 0.1%", rfb_tol="0.1%",'),
    ("a", "the hold lost: Q551's gate on ground", '{"1": "OUTLET_OK", "2": "GND", "3": "PA_ISP"}', '{"1": "GND", "2": "GND", "3": "PA_ISP"}'),
    ("d", "the injection on U15's output: R57 to VGG_SW", 'r("R57", "110k 1%", "PA_ILIM", "VGG_FB")', 'r("R57", "110k 1%", "PA_ILIM", "VGG_SW")'),
    ("d", "R83 left at 10.0k (the band moves up)", 'r("R83", "11.0k 1%", "VGG_FB", "GND")', 'r("R83", "10.0k 1%", "VGG_FB", "GND")'),
    ("d", "the bleed lost: R58 to PA_ILIM", 'r("R58", "470 1%", "VGG_SW", "GND")', 'r("R58", "470 1%", "VGG_SW", "PA_ILIM")'),
    ("d", "the harness pin left on AB_SPARE", '"15": "ZEROIZE_HW", "16": "PA_ILIM"})', '"15": "ZEROIZE_HW", "16": "AB_SPARE"})'),
]


def rel(p):
    return os.path.join(ROOT, p)


def sha(p, n=16):
    return hashlib.sha256(open(rel(p), "rb").read()).hexdigest()[:n]


def load(path, name):
    sp = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


GN = load(os.path.join(REC, "l8p", "gen_netlist.py"), "gn_for_f01")


def apply(board, key, gen):
    rec, name = key.split("/")
    script = os.path.join(REC, rec, "apply_gen_sch_%s_%s.py" % (board, name))
    args = [script, gen, rel(NET[board])] if rec == "d8dec31" else [script, gen, "--write"]
    r = subprocess.run([sys.executable, "-B"] + args, capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    last = ((r.stderr if r.returncode else r.stdout).decode("utf-8", "replace").strip().splitlines() or [""])[-1]
    return r.returncode, last


def compose(board, d, keys, tag):
    gen = os.path.join(d, "%s-gen_sch_%s.py" % (tag, board))
    shutil.copy(os.path.join(TOOLS, "gen_sch_%s.py" % board), gen)
    steps = []
    for k in keys:
        rc, last = apply(board, k, gen)
        steps.append((k, rc, last))
        if rc:
            break
    return gen, steps


def regen(board, gen, d, tag):
    out = os.path.join(d, "%s-%s.net" % (tag, PRJ[board]))
    rc, log, table = GN.run(gen, out, PRJ[board])
    if rc != 0:
        tail = [l for l in log.strip().splitlines() if l.strip()][-1:] if log else []
        return None, rc, tail, None
    return out, 0, [], table


def judge(board, path, S):
    nl = L8P.read_netlist(open(path, "rb").read())
    st, msgs, info = (CHK.check_a if board == "a" else CHK.check_d)(nl, S)
    return st, msgs, info, nl


def main():
    S = PL.read_sheets()
    tree_sha = {b: sha("v2/ecad/tools/gen_sch_%s.py" % b, 64) for b in "ad"}
    out = []
    w = out.append
    w("l9t5_f01_drafts: P0-1 part 1c, the F01 / D-17 drafts (the PA drain-current cap, round 2 of the selection) composed, regenerated, read and")
    w("judged (record l9t5, Slot A, MESHSAT-1357, 5 October 2026). PROTOTYPE DESIGN, DESK ARITHMETIC: nothing built, bought, powered or measured.")
    w("A netlist reading is not electrical qualification; the electrical acceptance is section 5, and F01 / D-17 stays PROVISIONAL on the")
    w("supplier's tasks B-PA1 and B-PA2 (l9t5_f01.out section 6).")
    w("")
    w("0. PINS (sha256/16  path)")
    for p in PINS:
        w("   %s %s" % (sha(p), p))
    w("")
    tmp = tempfile.mkdtemp(prefix="l9t5_f01_")
    try:
        # 1. the old states
        w("1. THE OLD STATES (they must not read DRAWN)")
        for b in "ad":
            st, msgs, _i, _n = judge(b, rel(NET[b]), S)
            w("   the tree's committed board %s netlist: %s (%s)" % (b.upper(), st, msgs[0]))
        gen_wo, steps = compose("a", tmp, [k for k in ORDER["a"] if k != "l9t5/paloop"], "wo")
        p_wo, rc, tail, _t = regen("a", gen_wo, tmp, "wo")
        st_wo = judge("a", p_wo, S)[0] if p_wo else "REFUSED"
        w("   board A with every other pending draft, without this one: %d steps %s, regenerated rc %d: %s" % (
            len(steps), "OK" if all(s[1] == 0 for s in steps) else "REFUSED", rc, st_wo))
        w("")
        # 2. each alone
        w("2. EACH DRAFT ALONE ON THE TREE'S GENERATOR, AND BOARD A'S WITH ITS ONE DEPENDENCY")
        g, steps = compose("a", tmp, ["l9t5/paloop"], "aloneA")
        w("   board A alone: %s (%s)" % ("composes" if steps[-1][1] == 0 else "REFUSED as it must: it needs record l8r2's fb01 keyword", steps[-1][2][:120]))
        g, steps = compose("a", tmp, ["l8r2/fb01", "l9t5/paloop"], "fbA")
        p_, rc, tail, _t = regen("a", g, tmp, "fbA")
        w("   board A after fb01 alone: steps %s; regenerated rc %d; %s" % (", ".join("%s rc %d" % (s[0], s[1]) for s in steps), rc,
                                                                            judge("a", p_, S)[0] if p_ else "no netlist " + " ".join(tail)))
        g, steps = compose("d", tmp, ["l9t5/paloop"], "aloneD")
        p_, rc, tail, _t = regen("d", g, tmp, "aloneD")
        w("   board D alone: steps %s; regenerated rc %d; %s" % (", ".join("%s rc %d" % (s[0], s[1]) for s in steps), rc,
                                                                 judge("d", p_, S)[0] if p_ else "no netlist " + " ".join(tail)))
        w("")
        # 3. the full composition
        w("3. THE FULL COMPOSITION (L4-E9's change-list order with each author's placement; this draft after record l8r2's gndrtn, before")
        w("   d8dec31's mainpb; board D after d8dec31's ptt, before Layer 6's two)")
        full = {}
        for b in "ad":
            gen, steps = compose(b, tmp, ORDER[b], "full")
            p_, rc, tail, table = regen(b, gen, tmp, "full")
            ok = all(s[1] == 0 for s in steps)
            w("   board %s: %d steps %s; regenerated rc %d, %s parts, %s unplaced, intent written %s" % (
                b.upper(), len(steps), "every step OK" if ok else "REFUSED at %s: %s" % (steps[-1][0], steps[-1][2][:100]), rc,
                len(table["parts"]) if table else "-", len(table["unplaced"]) if table else "-", bool(table and table.get("intent_written"))))
            st, msgs, info, nl = judge(b, p_, S)
            w("     F01 check: %s (%s)" % (st, "; ".join(msgs)))
            full[b] = (gen, p_, st, info, nl, table)
        pa, pd = CHK.pin(full["a"][4], "J_MEZZ1", "16"), CHK.pin(full["d"][4], "J_HARN1", "16")
        w("   the harness pair J_MEZZ1.16 / J_HARN1.16: %s (%s / %s)" % ("HOLDS" if pa == pd == "PA_ILIM" else "FAIL", pa, pd))
        mp = [r for r in ("R603", "C607") if r in full["a"][4]["comps"]]
        w("   mainpb's next-free picks on the full composition: %s (V6 read R603 and C607 before this draft: unmoved)" % ", ".join(mp))
        w("")
        # 4. mutations
        w("4. MUTATIONS OF THE FULL COMPOSITION (each must not read DRAWN)")
        nfail = 0
        for i, (b, label, old, new) in enumerate(MUT, 1):
            text = open(full[b][0], encoding="utf-8").read()
            if text.count(old) != 1:
                w("   M%02d board %s, %s: the anchor occurs %d times: NOT RUN" % (i, b.upper(), label, text.count(old)))
                continue
            g = os.path.join(tmp, "mut%02d-gen_sch_%s.py" % (i, b))
            open(g, "w", encoding="utf-8").write(text.replace(old, new))
            p_, rc, tail, _t = regen(b, g, tmp, "mut%02d" % i)
            if p_ is None:
                verdict = "the generator REFUSES (%s)" % (" ".join(tail)[:110])
                nfail += 1
            else:
                st, msgs, _i, _n = judge(b, p_, S)
                verdict = "%s: %s" % (st, msgs[0][:110])
                nfail += st != "DRAWN"
            w("   M%02d board %s, %s: %s" % (i, b.upper(), label, verdict))
        w("   %d of %d mutations fail" % (nfail, len(MUT)))
        w("")
        # 5. the electrical acceptance
        f01 = load(os.path.join(HERE, "l9t5_f01.py"), "l9t5_f01_for_drafts")
        R = f01.compute()
        L, V = R["L"], R["V"]
        ia = full["a"][3]
        nl_d = full["d"][4]
        r82, r83, r57 = (CHK.ohm(CHK.value(nl_d, r)) for r in ("R82", "R83", "R57"))
        band = PL.vgg_band(S, r82=r82, r83=r83, rinj=r57)
        w("5. THE ELECTRICAL ACCEPTANCE ON C-ALLTX REV 3 (the values read from the composed netlists; labels as l9t5_f01.out section 4)")
        w("   the set point from R551 and R552 on the netlist: %.4f A nominal (no R560 term) ; the cap %.4f to %.4f A (MODEL on PRINTED terms with" % (
            ia["i_set"], ia["i_min"], ia["i_max"]))
        w("     TYPICAL allowances); U13's average loop least %.4f A with R55 hot: the cap's top and R55's other loads %.4f A under it (BIAS on" % (
            ia["u13_min"], ia["u13_min"] - ia["i_max"] - L["r55_other"]))
        w("     PA_OUT on the netlist)")
        w("   THE CASE at 15.5 V rest and the indicated 18 A, every transmitter keyed, fans running, the standby card off, the other loads typical,")
        w("     the gauge's uncalibrated %.4f A and the dock contacts' maximum, the PA at the cap's top %.2f W and the loop's own %.3f W: need %.4f V:" % (
            R["gu"], L["p_max"], L["loop_w"], L["bnd"]["need"]))
        w("     %s 15.5 V on the MODEL, margin %.4f V (nominal %.4f V); no other load reduced (the budget's loads unchanged but the PA's);" % (
            "MEETS" if L["bnd"]["need"] < V else "NOT MET", V - L["bnd"]["need"], L["nom"]["need"]))
        w("     F01 / D-17 PROVISIONAL (below), never closed on printed limits")
        w("   the rails in regulation through the 60 s: U13 (the PA rail) at the cap stays under its own current loop's least (above); every")
        w("     other rail carries the case's own load (the budget's model: unchanged); +5V_D8IN carries %.2f mA more, under its 2.0 A declared peak" % (
            L["supply_a"] * 1e3))
        w("   board D's VGG from R82 %s, R83 %s and R57 %s on the netlist: at rest %.3f / %.4f / %.3f V (the drawn %.3f / %.4f / %.3f V), the top under" % (
            CHK.value(nl_d, "R82"), CHK.value(nl_d, "R83"), CHK.value(nl_d, "R57"), band[0], band[1], band[2], L["band_drawn"][0], L["band_drawn"][1], L["band_drawn"][2]))
        w("     the module's VGG<5V; the loop's authority %.3f V" % band[3])
        w("   EMCON and the key, read on the netlists: U15's EN on %s; PA_ILIM's only source U553 through R558 (its supply +5V_D8IN); R57 enters" % (
            CHK.pin(nl_d, "U15", "4")))
        w("     U15's feedback node only; Q551's gate on %s (the set point held while the PA is not keyed)" % CHK.pin(full["a"][4], "Q551", "1"))
        w("   PROVISIONAL (the owner's part 19): the 30 W service under the cap's least %.4f A (B-PA1, a feasibility task); the dynamics (B-PA2 and" % L["i_min"])
        w("     record l9stk's E-10); the case's own assumptions (R_cell 0.060 Ohm, the converters' declared and extrapolated efficiencies, U5)")
        w("")
        # 6. the declarations
        w("6. THE DECLARATIONS THE DRAFT WRITES, HELD TO THEIR BASIS")
        intent = full["a"][5].get("intent") if full["a"][5] else None
        rails = (intent or {}).get("rails", {})
        for net in ("+13V8_PA", "+13V8_PAJ"):
            r_ = rails.get(net) or rails.get("/" + net) or {}
            w("   %s: peak %s A (the cap's top %.4f A rounded up to 0.01 A: %s)" % (net, r_.get("amps_peak"), L["i_max"],
                                                                                 "HOLDS" if r_.get("amps_peak") and float(r_["amps_peak"]) >= L["i_max"] and float(r_["amps_peak"]) - L["i_max"] < 0.01 else "FAIL"))
        w("")
        w("7. THE PREDICATES")
        P = {
            "the tree's netlists read NOT DRAWN on both boards": all(judge(b, rel(NET[b]), S)[0] == "NOT DRAWN" for b in "ad"),
            "board A without this draft reads NOT DRAWN": st_wo == "NOT DRAWN",
            "both boards compose with every pending draft and read DRAWN": full["a"][2] == "DRAWN" and full["d"][2] == "DRAWN",
            "the harness pair holds": pa == pd == "PA_ILIM",
            "every mutation fails": nfail == len(MUT),
            "the case at the cap's top passes 15.5 V on the bounded terms (MODEL)": L["bnd"]["need"] < V,
            "the cap's top and R55's other loads stay under U13's least": ia["i_max"] + L["r55_other"] < ia["u13_min"],
            "board D's VGG top at rest stays under 5 V and the authority under 3.5 V": band[2] < 5.0 and band[3] < 3.5,
        }
        for k, v in P.items():
            w("   %-120s %s" % (k, "yes" if v else "NO"))
        for b in "ad":
            if sha("v2/ecad/tools/gen_sch_%s.py" % b, 64) != tree_sha[b]:
                raise SystemExit("l9t5_f01_drafts: the tree's gen_sch_%s.py changed during the run" % b)
        w("")
        w("l9t5_f01_drafts: done")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(P.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
