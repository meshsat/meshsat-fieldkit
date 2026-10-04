#!/usr/bin/env python3
"""apply_gen_sch_b_fandec.py: DRAFT for board B's generator owner (Layer 8 record l8r2, round 7, task T5b, MESHSAT-1357, 4 October
2026), the companion of this record's apply_gen_sch_b_fans12.py. NOT APPLIED to the tree by this record; its author ran it only on
scratch copies (the tests write scratch copies).

The defect (finding L8R2-F32, found when the ground's stop was removed and the composed generator ran further): fans12 declares the
two capacitors of each cooler step-up U7x1 (TPS61089) with their class and maker's clause AT THE CALL, board A's form:
  _intent.bypass(C7x4, U7x1, "9", +5V_Sn, cls="D", basis="TI SLVSD38C (TPS61089) 9.2.2.6 p.16: ...")
  _intent.bypass(C7x2, U7x1, "2", CFANs_VCC, cls="L", basis="TI SLVSD38C (TPS61089) Table 6-1 and 9.2.2.6: ...", value_floor="1u")
Board B's generator writes every entry's class from its own table, _dec_rule (the decision 42 block, stream w3b), and stops on a
part the table does not name: "decoupling entry C704 -> U701.9 ... carries no class (decision 42): add its maker's clause to
_dec_rule". The table has no TPS61089 row, so board B's composed generator stopped there with fans12 applied. Record l8r2's
composition proof of rounds 1 to 6 read generator text and never ran the generator (no KiCad on its host; record l8p's
gen_netlist.py, which runs it, is of 4 October), so neither stop was seen.

The correction: one row in _dec_rule for the TPS61089, which returns the class, the clause and the value floor the entry already
carries from its call. The maker's words stay in one place (fans12's calls); a TPS61089 entry declared without them still stops the
generator. fans12 itself is left byte for byte (records l7pwr and l9pwr pin it by sha256).

What it changes in v2/ecad/tools/gen_sch_b.py, and nothing else: the row before _dec_rule's closing "return None". Order: board
B's round, with fans12, before or after it (the row is inert until a TPS61089 is drawn).

Usage:  apply_gen_sch_b_fandec.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the repository's
own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

NAME = "apply_gen_sch_b_fandec"
ADDS = ()
NETS = ()

_OLD = '    return None\n_DEC_RULED = ("R", "D", "L", "A", "B1", "B2")'
_NEW = ('    if pv.startswith("TPS61089") and e.get("class") and e.get("basis"):\n'
        '        # record l8r2 round 7 (L8R2-F32): the coolers\' step-ups U7x1 (apply_gen_sch_b_fans12.py) declare each capacitor\'s class and\n'
        '        # TI\'s clause at the call; this row hands them to the block below, with the value floor a class L entry must name\n'
        '        return (e["class"], e["basis"], {k: e[k] for k in ("value_floor", "esr_max", "same_side") if k in e})\n'
        + _OLD)
EDITS = [(_OLD, _NEW)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if 'pv.startswith("TPS61089")' in text:
        refuse("already applied (_dec_rule names the TPS61089)")
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once: %r" % (new.count(old), old[:60]))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        tree = ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    fn = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_dec_rule"]
    if len(fn) != 1 or "TPS61089" not in ast.unparse(fn[0]):
        refuse("the row is not inside _dec_rule")
    return new


# NOT RELEASED: record l8r2 drafts this change for board B's generator owner and never applies it. Writing the repository's own
# gen_sch_b.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_b.py")
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; l8r2's drafts wait on an accepted check")
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
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if write and os.path.realpath(target) == os.path.realpath(TREE_GEN):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/gen_sch_b.py", "b/gen_sch_b.py", n=0))
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
