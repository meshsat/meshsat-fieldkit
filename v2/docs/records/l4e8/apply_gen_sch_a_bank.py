#!/usr/bin/env python3
"""apply_gen_sch_a_bank.py: DRAFT for board A's generator owner (task L4-E8, MESHSAT-1357, 1 October 2026, the fix round). NOT
APPLIED to the tree by L4-E8; its author ran it only on scratch copies (the tests also write scratch copies).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: a ballast resistor in series with each of the front end's six
EEHZK1V331P, so that no can's current depends on the cans matching (L4E8-BANK.md; ripple_dense.out section 6). Three edits:
  - the lm5176() helper takes `bulk_ballast=None`, a tuple (references, value, LCSC code);
  - its bulk loop, when `bulk_ballast` is given, draws each can on its own node <p>_BULK<k> behind its resistor from the output
    rail, declares that node to the intent (the rail's voltage), and adds the resistors to the output power loop's parts; with
    `bulk_ballast` absent the helper draws exactly what it drew before (the other six stages are untouched);
  - the front end's call passes R221 to R226, "38mOhm 1% 2512 (bulk ballast)", Milliohm HoJLR2512-3W-38mR-1%, LCSC C2903481 (in
    stock in L4-E4's catalogue reading, v2/docs/records/l4e4/inputs/jlc-search-hojlr2512-3w-2026-10-01.json).
The cans, their part number and the ceramics stay as drawn. One value serves both R11 outcomes (8 mOhm and, if bench V-A07 fails,
7 mOhm). The third fix-up's comment block above the call is left as the record of 26 September 2026 (its corrections are drafted
in CORRECTIONS-DRAFT.md); the edited call line carries its own comment naming this record. R221 to R226 must be unused.

ORDER: the ballast goes in with L4-E6's R12 12 mOhm (apply_gen_sch_a_r12.py), never on the drawn 5 mOhm: there the ballast's
resistance moves the bank's zero down and the voltage loop's gain margin falls under 10 dB on the widened band even at the record's
loads (ripple_dense.out section 7). Writing the repository's own generator is refused until the front end's call carries
rcs="12m"; on a copy (the tests) the drafts still compose in any order.

It is not the whole change. The same circuit round owes: L4-E4's R11 (apply_gen_sch_a_r11.py) and R138, L4-E6's R12 and C147
(apply_gen_sch_a_r12.py), L4-E5's ILIM_HIZ line on U3, board A's layout seating the six resistors (each beside its can, the
branches within the layout rule of L4E8-BANK.md; placement is the generator owner's), lcsc_fill.py's line for the value if the
pipeline maps it by value as well as by the code given here, the loop re-verified on the regenerated board, and the gates and
evidence re-taken on a box. These drafts edit disjoint lines and apply in any order (test_l4e8.py). After any application,
ripple_dense.py, r11_dep.py and the L4-E4 to L4-E6 records refuse by design: they pin the generator before the change.

Usage:  apply_gen_sch_a_bank.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no new designator may occur in
the target; the result must parse. Exit 0: checked (or written); 2: usage; 3: refused (the target is not the expected text, the
change is already applied, or the repository's own generator is named before RELEASE.md releases it or before L4-E6's R12 is
in it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_bank"
RB_REFS = ("R221", "R222", "R223", "R224", "R225", "R226")
RB_VALUE = "38mOhm 1% 2512 (bulk ballast)"
RB_CODE = "C2903481"

OLD_SIG = '           bias_cap=None, css=("47n", ""), cout_pre=(), vin_block=None, visns_r=None, en_node=None, en_vals=None, vin_cap=None):\n'
NEW_SIG = ('           bias_cap=None, css=("47n", ""), cout_pre=(), vin_block=None, visns_r=None, en_node=None, en_vals=None, vin_cap=None,\n'
           '           bulk_ballast=None):   # L4-E8 (MESHSAT-1357): (references, value, LCSC code), a ballast resistor in series with each bulk can\n')
OLD_LOOP = ('    for cb in bulk:   # local bulk the stage\'s loop design asks for, (3) above; pad 1 is the positive terminal\n'
            '        part(cb, "Device", "C_Polarized", _bv, _bfp, {"1": vout, "2": "GND"}, _bl)\n'
            '    _loop(uref, "output", (co1, co2, co3) + tuple(cout_extra) + tuple(bulk), (qsl, qsh, rcs_), _LM_LOOP_OUT)   # round 8: COUT against the output loop (decision 42 R4)\n')
NEW_LOOP = ('    if bulk_ballast and len(bulk_ballast[0]) != len(bulk):\n'
            '        raise SystemExit("lm5176 %s: bulk_ballast names %d resistors for %d bulk parts" % (p, len(bulk_ballast[0]), len(bulk)))\n'
            '    for _bk, cb in enumerate(bulk):   # local bulk the stage\'s loop design asks for, (3) above; pad 1 is the positive terminal\n'
            '        if bulk_ballast:   # L4-E8 (MESHSAT-1357): each can behind its own ballast, so no can takes its siblings\' share whatever their\n'
            '            # ESR, ESL and C (the ZK sheet prints no ESR minimum); v2/docs/records/l4e8/L4E8-BANK.md\n'
            '            _bn = N("BULK%d" % (_bk + 1))\n'
            '            r(bulk_ballast[0][_bk], bulk_ballast[1], vout, _bn, "RS2512", bulk_ballast[2])\n'
            '            _intent.node(_bn, _intent.net_volts(vout), "LM5176 stage %s: bulk can %s behind its ballast %s, at the output rail\'s voltage"\n'
            '                         % (p, cb, bulk_ballast[0][_bk]))\n'
            '            part(cb, "Device", "C_Polarized", _bv, _bfp, {"1": _bn, "2": "GND"}, _bl)\n'
            '        else:\n'
            '            part(cb, "Device", "C_Polarized", _bv, _bfp, {"1": vout, "2": "GND"}, _bl)\n'
            '    _loop(uref, "output", (co1, co2, co3) + tuple(cout_extra) + tuple(bulk), (qsl, qsh, rcs_) + tuple(bulk_ballast[0] if bulk_ballast else ()),\n'
            '          _LM_LOOP_OUT)   # round 8: COUT against the output loop (decision 42 R4); L4-E8: the ballasts in the loop\n')
OLD_CALL = ('       comp=(("15k", "C22809"), ("220n", "C160828"), ("680p", "C30816")), bulk=("C163", "C178", "C179", "C180", "C199", "C200"),'
            ' bulk_part="V331",\n')
NEW_CALL = OLD_CALL.rstrip("\n") + (' bulk_ballast=((%s), "%s", "%s"),   # L4-E8 (MESHSAT-1357): a %s ballast per can;'
                                    ' v2/docs/records/l4e8/L4E8-BANK.md\n') % (", ".join('"%s"' % r_ for r_ in RB_REFS), RB_VALUE, RB_CODE, RB_VALUE.split()[0])
EDITS = [(OLD_SIG, NEW_SIG), (OLD_LOOP, NEW_LOOP), (OLD_CALL, NEW_CALL)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
    used = [r_ for r_ in RB_REFS if re.search(r"\b%s\b" % r_, text)]
    if used:
        refuse("the new designators %s are already used in the target" % ", ".join(used))
    for old, rep in EDITS:
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: task L4-E8 drafts this bank for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of L4-E8 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E8's bank waits on an accepted check")
    lines = [l.rstrip("\n") for l in open(RELEASE, encoding="utf-8")]
    if not lines or lines[0] != "released: yes":
        refuse("NOT RELEASED: RELEASE.md's first line is not 'released: yes'")
    rec = [l.split(":", 1)[1].strip() for l in lines if l.startswith("check:")]
    if len(rec) != 1:
        refuse("NOT RELEASED: RELEASE.md names no single check")
    path = os.path.join(REPO, rec[0])
    if ".." in rec[0].split("/") or not os.path.isfile(path):
        refuse("NOT RELEASED: check %s is not in this tree" % rec[0])
    if open(path, encoding="utf-8").readline().rstrip("\n") != "accepted: yes":
        refuse("NOT RELEASED: check %s is not accepted" % rec[0])


def fe_rcs(text):
    """The front end's R12 as the target draws it: the rcs keyword of the lm5176() call that carries bulk_part="V331" (None when
    absent, the helper's default)."""
    calls = [n for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "lm5176"
             and any(k.arg == "bulk_part" and isinstance(k.value, ast.Constant) and k.value.value == "V331" for k in n.keywords)]
    if len(calls) != 1:
        refuse("the front end's lm5176() call is not found once")
    rcs = [k.value.value for k in calls[0].keywords if k.arg == "rcs" and isinstance(k.value, ast.Constant)]
    return rcs[0] if rcs else None


def order_ok(text):
    if fe_rcs(text) != "12m":
        refuse("ORDER: L4-E6's R12 12 mOhm (apply_gen_sch_a_r12.py) is not in the front end's call; the ballast goes in with it")


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        order_ok(text)
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(EDITS)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in EDITS):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(EDITS)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
