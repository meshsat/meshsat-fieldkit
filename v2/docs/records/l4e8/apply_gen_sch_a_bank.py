#!/usr/bin/env python3
"""apply_gen_sch_a_bank.py: DRAFT for board A's generator owner (task L4-E8, MESHSAT-1357, 1 October 2026). NOT APPLIED to the
tree by L4-E8; its author ran it only on scratch copies (the tests also write scratch copies).

What it changes in v2/ecad/tools/gen_sch_a.py, and nothing else: the front end's (U2, LM5176) bank, three keyword arguments of
its lm5176() call, each on its own line:
  --bank 8 (the default; R11 8 mOhm, L4-E4's provisional value, highest permitted current 7.262 A):
    bulk=      the six EEHZK1V331P and one more, C236 (BULK_ZK["V331"], LCSC C278516, the same part number);
    cout_extra the fifteen and three more, C237 to C239 (the stage's own "10u 50V X7R 1210", C596319 by lcsc_fill.py);
    cout_pre=  C13 to C15 and C237 to C239: six ceramics on FE_OUT before R11 (SNVSAI1D 9.1's division), eighteen on VBUS20 as drawn.
  --bank 7 (R11 7 mOhm, only if bench V-A07 fails; 8.300 A): a superset of the 8 mOhm bank, its designators kept:
    bulk=      eight cans, C236 and C240; cout_extra and cout_pre as --bank 8 with nine more on VBUS20, C241 to C249.
Both banks are ripple_dense.out's section 6 (L4E8-BANK.md): every can at most 2.8 A less the rebuild's validation tolerance at
the matched, 1.5:1 and 2:1 ESR spreads. The third fix-up's comment block above the call is left as the record of 26 September
2026; the edited lines carry their own comment naming this record. The new designators must be unused in the target.

It is not the whole change. The same circuit round owes: L4-E4's R11 (apply_gen_sch_a_r11.py) and R138, L4-E6's R12 and C147
(apply_gen_sch_a_r12.py), L4-E5's ILIM_HIZ line on U3, board A's layout seating the new parts (placement is the generator
owner's), the soft start and the start-up totals re-taken (L4E8-BANK.md section 8), the loop re-verified on the regenerated
board, and the gates and evidence re-taken on a box. These drafts edit disjoint lines of the same call and apply in either
order (test_l4e8.py). After any application, ripple_dense.py, r11_dep.py and the L4-E4 to L4-E6 records refuse by design:
they pin the generator before the change.

Usage:  apply_gen_sch_a_bank.py TARGET [--check | --write] [--bank 8 | --bank 7]     (default --check, --bank 8)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; no new designator may occur in
the target; the result must parse. Exit 0: checked (or written); 2: usage; 3: refused (the target is not the expected text, the
change is already applied, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_bank"
OLD_BULK = '       comp=(("15k", "C22809"), ("220n", "C160828"), ("680p", "C30816")), bulk=("C163", "C178", "C179", "C180", "C199", "C200"), bulk_part="V331",\n'
OLD_EXTRA = ('       cout_extra=("C181", "C182", "C183", "C184", "C185", "C186", "C187", "C188", "C189", "C201", "C202", "C203", "C204", "C205",'
             ' "C206"),\n')
OLD_PRE = '       cout_pre=("C13", "C14", "C15"), css=("4.7u", "C354262", "C10u"), vin_block=("D19", "C207", "1u 100V 1210", "C382212", "C1210"),\n'
NOTE = "   # L4-E8 (MESHSAT-1357): %s; v2/docs/records/l4e8/L4E8-BANK.md\n"


def _edits(bank):
    if bank == "8":
        new_cans, new_pre, new_vbus = ("C236",), ("C237", "C238", "C239"), ()
        what = "seven EEHZK1V331P, eighteen ceramics on VBUS20 and six on FE_OUT, for R11 8 mOhm at 7.262 A"
    else:
        new_cans, new_pre, new_vbus = ("C236", "C240"), ("C237", "C238", "C239"), tuple("C%d" % n for n in range(241, 250))
        what = "eight EEHZK1V331P, twenty-seven ceramics on VBUS20 and six on FE_OUT, for R11 7 mOhm at 8.300 A"
    q = lambda refs: ", ".join('"%s"' % r for r in refs)
    new_bulk = OLD_BULK.replace('"C199", "C200")', '"C199", "C200", %s)' % q(new_cans)).rstrip("\n") + NOTE % what
    new_extra = OLD_EXTRA.replace('"C205", "C206")', '"C205", "C206", %s)' % q(new_pre + new_vbus)).rstrip("\n") + NOTE % "the added ceramics"
    new_pre_line = OLD_PRE.replace('cout_pre=("C13", "C14", "C15")', 'cout_pre=("C13", "C14", "C15", %s)' % q(new_pre)).rstrip("\n") + NOTE % "FE_OUT's six"
    return [(OLD_BULK, new_bulk), (OLD_EXTRA, new_extra), (OLD_PRE, new_pre_line)], new_cans + new_pre + new_vbus


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text, bank="8"):
    edits, refs = _edits(bank)
    new = text
    for old, rep in edits:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
    used = [r for r in refs if re.search(r"\b%s\b" % r, text)]
    if used:
        refuse("the new designators %s are already used in the target" % ", ".join(used))
    for old, rep in edits:
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


def main(argv):
    argv = list(argv)
    bank = "8"
    if "--bank" in argv:
        i = argv.index("--bank")
        if i + 1 >= len(argv) or argv[i + 1] not in ("8", "7"):
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
            return 2
        bank = argv[i + 1]
        del argv[i:i + 2]
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text, bank)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_a.py", "b/gen_sch_a.py", n=0))
    if not write:
        print("%s: CHECK OK, bank %s, %d edit(s), nothing written" % (NAME, bank, len(_edits(bank)[0])))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in _edits(bank)[0]):
        refuse("the written file does not read back as the patched text")
    ast.parse(back)
    print("%s: WRITTEN, bank %s, %d edit(s)" % (NAME, bank, len(_edits(bank)[0])))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
