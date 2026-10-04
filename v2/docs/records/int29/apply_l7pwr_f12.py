#!/usr/bin/env python3
"""apply_l7pwr_f12.py: finding F-L7-12 corrected in record l7pwr (MESHSAT-1357, integration set 29, 4 October 2026; the coordinator's
correction of an integration regression, the owner's instruction of the same day: "establish whether F-L7-12's mixed thermal
assumptions affect any current acceptance claim; correct and verify affected claims before accepting them").

The cause. Record l8r2's round 6 restated the cooler step-up's slot row as a CURRENT DECLARATION for the slot leads (0.69 A at 5.0 V:
l8r2's 2.75 W fan envelope over the step-up's low 0.80). Layer 7's script took the step-up's loss from that row (its input power less
its fan power) and added it to the fan's RATED 2.0 W: a heat sum on two bases (7.50 W in the hold, 12.90 W in the profile), set 29's
first later stage printed it, and apply_l7pwr_set29.py restated the page on it. Round 2's 7.15 and 11.85 W had been on one basis.

The correction. The fans' heat is computed on one basis per use, each read from the draft Layer 7 already pins
(`apply_gen_sch_b_fans12.py`): AT FULL SPEED, the plan's basis (the maker's rated fan power through the step-up at the draft's typical
efficiency, `efficiency=0.85` in its rail call): the hold 7.15 W, the profile 11.86 W; AT THE BOUND (l8r2's 2.75 W envelope through
the step-up at its low 0.80, the row's own figures): the hold 8.24 W, the profile 15.11 W. The mixers are at their rated power in both:
no envelope of theirs is stated anywhere (a residual named on the page). The slot row's 0.69 A is printed as what it is, l8r2's
declared envelope current. Verification: record l9pwr reproduces both figures from its own inputs (R8: 11.8588 W at the maker's
2.0 W and the typical 0.85; 15.1125 W at the coolers' envelope, its HIGH), independently of this record.

Consumers checked (a grep of the tree for the sums and their names, 4 October 2026): no acceptance claim reads them. Record l9pwr's
R8 reconciliation reads the profile sum and the per-fan loss; L4-E12's thermal record and the T-H1 procedure use the model's
1.950 and 2.970 W and the fans' MEASURED draw; register row R-150 (OWED) is where E5's line will be restated on the picked fans, and
this record's two bases are the inputs it needs.

Edits: `l7pwr_fans_th1.py` (the typical efficiency parsed; the two bases computed and printed; the slot row named as a declaration),
`L7-FANS-AND-TH1.md` and `T-H1-MOCKUP-SPEC.md` (the current statements restated from the regenerated output, F-L7-12 marked
CORRECTED with what remains), `L9-POWER-BUDGET.md`'s R8 row (Layer 7's figure). Run from the repository root:
apply_l7pwr_f12.py [--check | --write | --pages]; --write patches the script; --pages, after the output is regenerated through
regen_out, restates the pages from it (each figure asserted to be printed by the output). A second run exits 3."""
import ast
import re
import sys

SCRIPT = "v2/docs/records/l7pwr/l7pwr_fans_th1.py"
OUT = "v2/docs/records/l7pwr/l7pwr_fans_th1.out"
PAGE = "v2/docs/records/l7pwr/L7-FANS-AND-TH1.md"
SPEC = "v2/docs/records/l7pwr/T-H1-MOCKUP-SPEC.md"
L9PAGE = "v2/docs/records/l9pwr/L9-POWER-BUDGET.md"

S_EDITS = [
    ('    bo = need(b, r"from \\+5V_Sn to C?FANs_12V at ([\\d.]+) to ([\\d.]+) V", "l8r2\'s boost output")\n',
     '    bo = need(b, r"from \\+5V_Sn to C?FANs_12V at ([\\d.]+) to ([\\d.]+) V", "l8r2\'s boost output")\n'
     '    be = need(b, r"converted=True, efficiency=([\\d.]+), fed_from=n5", "l8r2\'s step-up typical efficiency (its rail call)")\n'),
    ('        b_in_a=float(bl.group(1)), b_fan_w=float(bl.group(2)), b_eta=float(bl.group(3)), b_vin=float(bv.group(1)), b_vout=(float(bo.group(1)), float(bo.group(2))))\n',
     '        b_in_a=float(bl.group(1)), b_fan_w=float(bl.group(2)), b_eta=float(bl.group(3)), b_vin=float(bv.group(1)), b_vout=(float(bo.group(1)), float(bo.group(2))),\n'
     '        b_eta_typ=float(be.group(1)))\n'),
    ('    b_loss = rl["b_in_a"] * rl["b_vin"] - rl["b_fan_w"]           # l8r2\'s cooler step-up: its row\'s input power less the fan\'s\n'
     '    hold_full = c["w"] + b_loss + 2 * m["w"] + rl["u22_loss"]     # slot 3\'s cooler and the two mixers, each converter\'s loss counted (inside the case)\n'
     '    prof_full = 3 * (c["w"] + b_loss) + 2 * m["w"] + rl["u22_loss"]\n',
     '    # F-L7-12 (set 29): one basis per sum. At full speed: the maker\'s rated fan power through the step-up at the draft\'s typical\n'
     '    # efficiency. At the bound: l8r2\'s fan envelope through the step-up at its low efficiency (the slot row\'s own figures). The slot\n'
     '    # row\'s current is l8r2\'s DECLARATION for the leads (the envelope), never a heat figure. The mixers have no stated envelope.\n'
     '    b_loss = c["w"] / rl["b_eta_typ"] - c["w"]                    # the rated cooler fan through the step-up at its typical efficiency\n'
     '    b_loss_bound = rl["b_fan_w"] / rl["b_eta"] - rl["b_fan_w"]    # l8r2\'s envelope through the step-up at its low efficiency\n'
     '    hold_full = c["w"] + b_loss + 2 * m["w"] + rl["u22_loss"]     # slot 3\'s cooler and the two mixers, each converter\'s loss counted (inside the case)\n'
     '    prof_full = 3 * (c["w"] + b_loss) + 2 * m["w"] + rl["u22_loss"]\n'
     '    hold_bound = rl["b_fan_w"] + b_loss_bound + 2 * m["w"] + rl["u22_loss"]\n'
     '    prof_bound = 3 * (rl["b_fan_w"] + b_loss_bound) + 2 * m["w"] + rl["u22_loss"]\n'),
    ('        cooler_w_each=c["w"], cooler_i_slot_full=rl["b_in_a"], cooler_i_12v=c["a"], b_loss=b_loss, u22_loss=rl["u22_loss"],\n',
     '        cooler_w_each=c["w"], cooler_i_slot_full=rl["b_in_a"], cooler_i_12v=c["a"], b_loss=b_loss, u22_loss=rl["u22_loss"],\n'
     '        b_loss_bound=b_loss_bound, heat_hold_bound=hold_bound, heat_prof_bound=prof_bound,\n'
     '        line_shift_hold_bound=LINE_PER_W * (hold_bound - HOLD_FANS_W),\n'),
    ('    P("   the coolers\' feed as drafted by record l8r2: a per-slot step-up from +5V_Sn (the slot rails are %.1f V) declared %.2f A at %.1f V (%.1f W of fan over %.2f), so %.2f W lost in it per running fan;" % (SLOT_5V, rl["b_in_a"], rl["b_vin"], rl["b_fan_w"], rl["b_eta"], D["b_loss"]))\n',
     '    P("   the coolers\' feed as drafted by record l8r2: a per-slot step-up from +5V_Sn (the slot rails are %.1f V); the slot row declares %.2f A at %.1f V for the leads, l8r2\'s envelope (%.2f W of fan over %.2f),"\n'
     '      % (SLOT_5V, rl["b_in_a"], rl["b_vin"], rl["b_fan_w"], rl["b_eta"]))\n'
     '    P("   a declaration, not a heat figure (F-L7-12): at the maker\'s rated %.1f W and the draft\'s typical %.2f, so %.4f W lost in it per running fan; at the envelope %.4f W;"\n'
     '      % (D["cooler_w_each"], rl["b_eta_typ"], D["b_loss"], D["b_loss_bound"]))\n'),
    ('    P("   against %.3f W. The controls set the duty (R-150); T-H1 logs the fans\' real draw from a 12.0 V bench supply, so the converters\' losses are board heat its heaters carry." % D["heat_prof_plan"])\n',
     '    P("   against %.3f W. The controls set the duty (R-150); T-H1 logs the fans\' real draw from a 12.0 V bench supply, so the converters\' losses are board heat its heaters carry." % D["heat_prof_plan"])\n'
     '    P("   at the bound (F-L7-12: the coolers at l8r2\'s %.2f W envelope over its low %.2f, the mixers at their rated power, no envelope of theirs stated): the hold\'s fans %.2f W"\n'
     '      % (rl["b_fan_w"], rl["b_eta"], D["heat_hold_bound"]))\n'
     '    P("   (+%.2f W over the model, E5\'s line +%.3f W/K), the profile\'s five fans and their converters %.2f W. One basis per use: the plan\'s energy at the duty the controls set,"\n'
     '      % (D["heat_hold_bound"] - D["heat_hold_plan"], D["line_shift_hold_bound"], D["heat_prof_bound"]))\n'
     '    P("   the thermal bound on the envelope (R-150 restates E5\'s line on one of them, named).")\n'),
    ('           "a cooler fan\'s slot current at full speed (A)": D["cooler_i_slot_full"],\n',
     '           "a cooler fan\'s slot current at full speed (A)": D["cooler_i_slot_full"],   # l8r2\'s declared envelope current since its round 6\n'),
]


def refuse(msg):
    sys.stderr.write("apply_l7pwr_f12: REFUSED: %s\n" % msg)
    sys.exit(1)


def once(t, old, new, where):
    if t.count(old) != 1:
        refuse("%s: %d occurrence(s) of %r" % (where, t.count(old), old[:80]))
    assert new != old
    return t.replace(old, new)


def patch_script(write):
    t = open(SCRIPT, encoding="utf-8").read()
    if "b_eta_typ" in t:
        return 3
    for old, new in S_EDITS:
        t = once(t, old, new, SCRIPT)
    ast.parse(t)
    if re.search("[–—]", t):
        refuse("a dash character")
    if write:
        open(SCRIPT, "w", encoding="utf-8").write(t)
    print("apply_l7pwr_f12: script %s, %d edit(s)" % ("WRITTEN" if write else "CHECK OK", len(S_EDITS)))
    return 0


def patch_pages():
    out = " ".join(open(OUT, encoding="utf-8").read().split())
    m = re.search(r"the hold's fans \(slot 3's cooler and its step-up, the two mixers and U22\) ([\d.]+) W", out)
    mb = re.search(r"at the bound \(F-L7-12: .*?\): the hold's fans ([\d.]+) W \(\+([\d.]+) W over the model, E5's line \+([\d.]+) W/K\), "
                   r"the profile's five fans and their converters ([\d.]+) W", out)
    mp = re.search(r"the profile's five fans and their converters ([\d.]+) W against", out)
    ml = re.search(r"against the model's [\d.]+ W \(\+([\d.]+) W, E5's line \+([\d.]+) W/K", out)
    mloss = re.search(r"so ([\d.]+) W lost in it per running fan; at the envelope ([\d.]+) W", out)
    if not (m and mb and mp and ml and mloss):
        refuse("the regenerated output does not print the two bases: regenerate it first")
    hold, prof, dplan, lplan = m.group(1), mp.group(1), ml.group(1), ml.group(2)
    holdb, dbound, lbound, profb = mb.group(1), mb.group(2), mb.group(3), mb.group(4)
    loss, lossb = mloss.group(1), mloss.group(2)
    page = open(PAGE, encoding="utf-8").read()
    if "F-L7-12 (CORRECTED" in page:
        return 3
    P_EDITS = [
        ("**7.50 W** against the model's 1.950 W (+0.555 W/K on E5's line if run flat out;",
         "**%s W** at full speed and **%s W** at the coolers' envelope against the model's 1.950 W (+%s and +%s W/K on E5's line if run flat out;" % (hold, holdb, lplan, lbound)),
        ("| 9WPA0412P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 (a step-up from +5V_Sn) |",
         "| 9WPA0412P6G001 | cooler, 5.1 V | NO | yes | yes | yes | yes | yes | yes | 0.500 (a step-up from +5V_Sn) |"),
        ("the slot's load row 0.69 A at 5.0 V (2.8 W of fan over 0.80, record l8r2's round 6 envelope; 0.47 A in round 2), so 0.70 W lost per running fan;",
         "the slot's load row 0.69 A at 5.0 V, l8r2's round 6 DECLARATION for the leads (its 2.75 W fan envelope over 0.80; 0.47 A in round 2), not a heat figure; the step-up loses %s W per running fan at the maker's 2.0 W and the draft's typical 0.85, %s W at the envelope;" % (loss, lossb)),
        ("the hold's fans **7.50 W** (slot 3's cooler 2.0 and its step-up's 0.70, the two mixers 4.08 and U22's 0.72 from L4-E11 18a) against "
         "the model's 1.950 W (+5.55 W; E5's line +0.555 W/K at L4-E12's 0.100 W/K per W); the profile's five fans with their converters 12.90 W "
         "against 2.970 W (set 29, on record l8r2's round 6 row; the sums' basis is finding F-L7-12).",
         "the hold's fans **%s W** at full speed (slot 3's cooler 2.0 and its step-up's %s at the typical 0.85, the two mixers 4.08 and U22's 0.72 from L4-E11 18a) against "
         "the model's 1.950 W (+%s W; E5's line +%s W/K at L4-E12's 0.100 W/K per W), and **%s W** at the coolers' envelope (+%s W/K); the profile's five fans with their converters "
         "%s W at full speed and %s W at the envelope, against 2.970 W (set 29, F-L7-12 corrected: one basis per sum; the mixers at their rated power in both)." % (hold, loss, dplan, lplan, holdb, lbound, prof, profb)),
        ("set 29: with the converters' losses 7.50 W in the hold, 12.90 W in the profile (round 2: 7.15 and 11.85 W, before record l8r2's "
         "round 6 envelope; the sums' basis is F-L7-12);",
         "set 29: with the converters' losses %s W in the hold and %s W in the profile at full speed, %s and %s W at the coolers' envelope (F-L7-12 corrected);" % (hold, prof, holdb, profb)),
        ("so U22's and the step-ups' losses (0.72 and 0.70 W at full speed) are",
         "so U22's and the step-ups' losses (0.72 and %s W at full speed, %s W at the envelope) are" % (loss, lossb)),
    ]
    for old, new in P_EDITS:
        if old == new:
            continue
        page = once(page, old, new, PAGE)
    i = page.index("**At set 29 (4 October 2026; the coordinator's integration correction, finding F-L7-12).**")
    j = page.index("(F-L7-12).\n", i) + len("(F-L7-12).\n")
    page = page[:i] + (
        "**At set 29 (4 October 2026; finding F-L7-12, corrected by the coordinator).** Record l8r2's round 6 restated the coolers' slot row as a\n"
        "declaration for the leads (0.69 A at 5.0 V: the fan's 2.75 W envelope over 0.80). This record's script first took the step-up's\n"
        "loss from that row and added it to the fan's rated 2.0 W, a sum on two bases (7.50 W in the hold, 12.90 W in the profile). It now\n"
        "computes one basis per sum: at full speed, the rated fan through the step-up at the draft's typical 0.85 (the hold **%s W**, the\n"
        "profile **%s W**, E5's line +%s W/K, the table above unchanged); at the bound, l8r2's envelope through its low 0.80 (the hold\n"
        "**%s W**, the profile **%s W**, E5's line +%s W/K). Record l9pwr reproduces both from its own inputs (its R8: 11.8588 and 15.1125 W).\n"
        "The slot current of the table (0.69 A) is l8r2's declared envelope current since its round 6, not a running figure.\n" % (hold, prof, lplan, holdb, profb, lbound)) + page[j:]
    rows = [l for l in page.split("\n") if l.startswith("| F-L7-12 |")]
    if len(rows) != 1:
        refuse("%d F-L7-12 row(s)" % len(rows))
    page = page.replace(rows[0], (
        "| F-L7-12 (CORRECTED at set 29) | this record's next round, with L4-E12 (R-150) | set 29: the cooler chain's heat had been summed on two bases (the "
        "fan's rated 2.0 W with the step-up's loss taken from l8r2's envelope row); corrected to one basis per sum (full speed: hold %s W, profile %s W; "
        "the envelope: hold %s W, profile %s W), reproduced by record l9pwr's R8. No acceptance claim read the mixed sums. Remaining: the mixers have no "
        "stated envelope (their rated 2.04 W at 12 V is used in both bases, against U22's 12.431 V top); R-150 restates E5's line on one named basis |"
        % (hold, prof, holdb, profb)))
    spec = open(SPEC, encoding="utf-8").read()
    spec = once(spec, "and 0.70 W at full speed (record l7pwr section 11; 0.35 W before record l8r2's round 6):",
                "and %s W at full speed, %s W at the coolers' envelope (record l7pwr section 11, F-L7-12):" % (loss, lossb), SPEC)
    l9 = open(L9PAGE, encoding="utf-8").read()
    l9 = once(l9, "| R8 Layer 7, fans and converters at full speed | 11.85 W against 2.970 W | equal |",
              "| R8 Layer 7, fans and converters at full speed | %s W against 2.970 W (set 29: Layer 7 also prints %s W at the coolers' envelope, this record's HIGH; F-L7-12) | equal |" % (prof, profb), L9PAGE)
    for t in (page, spec, l9):
        if re.search("[–—]", t):
            refuse("a dash character")
    open(PAGE, "w", encoding="utf-8").write(page)
    open(SPEC, "w", encoding="utf-8").write(spec)
    open(L9PAGE, "w", encoding="utf-8").write(l9)
    print("apply_l7pwr_f12: pages WRITTEN: full speed hold %s W, profile %s W; envelope hold %s W, profile %s W" % (hold, prof, holdb, profb))
    return 0


def main(argv):
    if "--pages" in argv:
        return patch_pages()
    return patch_script("--write" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
