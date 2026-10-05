#!/usr/bin/env python3
"""apply_gen_sch_a_gndrtn.py: DRAFT for board A's generator owner (Layer 8 record l8r2, round 8, finding L8R2-F31, MESHSAT-1357,
4 October 2026), board A's half of apply_gen_sch_b_gndrtn.py. NOT APPLIED to the tree by this record; its author ran it only on
scratch copies (the tests write scratch copies).

The defect and the correction are apply_gen_sch_b_gndrtn.py's: the supply return between boards A and B divided, by nothing but
contact resistance, over the VH leads' pin 2 contacts and the two ribbons' ground conductors; a dedicated ground return of three
leads (each an Amass XT60 pair with both contacts on GND and two 12 AWG conductors of 150 mm) carries it at every vertex of the
contact-resistance box (the record's section 3g; l8r2_gndret.out section 6). What this draft draws on board A:
  J_GR1 to J_GR3  Amass XT60-F, pins 1 and 2 both on GND, beside J_54V (the other end of board B's J_GR1 to J_GR3), in their own
                schematic section. FEMALE on the boards and male on the leads, so the pack lead (an XT60-F, for board E's J_BATT)
                cannot be plugged into either. The land is KiCad's Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical (NOT READ on
                the record's host: the box's generation checks it); no LCSC code is carried (Layer 6 names it).
What it does not change: board A's GND declaration. As generated it is a node, and this record's round 3 draft
(apply_gen_sch_a_packrtn.py) declares it the pack path's return; intent.rail cannot express a second loop on one net (the 5 V
returns entering at these sockets and closing at each stage's output), so the copper at J_GR1 to J_GR3 is a layout constraint
with its currents in l8r2_gndret.out (finding L8R2-F33), not a declared rail.

Order: board A's round, anywhere (its anchors are the land table, the PoE lead's line and the line that collects the unlisted
parts, which no other draft of the tree's round rewrites: l8r2_gndret.out section 5 composes it first and last). In one release with
apply_gen_sch_b_gndrtn.py.
Usage:  apply_gen_sch_a_gndrtn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, a designator is in
use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_a_gndrtn"
N_RETURN = 3
ADDS = tuple("J_GR%d" % k for k in range(1, N_RETURN + 1))
NETS = ()
LAND = "Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical"

_OLD_FP = '"XT60": "Connector_AMASS:AMASS_XT60-M_1x02_P7.20mm_Vertical", '
_NEW_FP = _OLD_FP + '"XT60F": "%s", ' % LAND
_OLD_AT = 'vh2("J_54V", "54 V to the PoE injector on B16 (JST-VH): + -", "+54V_POE")\n'
_NEW_AT = _OLD_AT + (
    "# L8R2-F31, RECORD l8r2 ROUND 8 (MESHSAT-1357, 4 October 2026): THE DEDICATED GROUND RETURN FROM B16. The grounds of this board and\n"
    "# board B are one net over the VH leads' pin 2 and the ribbons' ground conductors, and nothing set how board B's supply return\n"
    "# divided between them. Three return leads, each an Amass XT60 pair with both contacts on GND and two 12 AWG conductors, carry it\n"
    "# whatever the other contacts do (record l8r2, l8r2_gndret.out section 6). XT60-F here and XT60-M on the leads, so the pack lead\n"
    "# (an XT60-F, for board E's J_BATT) cannot be plugged into any of the sockets. DRAFTED, not applied.\n"
    + "".join('part("J_GR%d", "Connector_Generic", "Conn_01x02", "Amass XT60-F, both contacts GND: ground return %d from B16 J_GR%d (lead: XT60-M both ends, '
              '2 x 12 AWG, 150 mm)", "XT60F", {"1": "GND", "2": "GND"})\n' % (k, k, k) for k in range(1, N_RETURN + 1)))
_OLD_SEC = '_listed = {r for _, refs in SECTIONS for r in refs}\n'
_NEW_SEC = ('SECTIONS.insert(len(SECTIONS) - 1, ("GROUND RETURN FROM B16 (RECORD l8r2 ROUND 8, L8R2-F31): THREE XT60-F, BOTH CONTACTS ON GND", '
            '[%s]))   # its own block, ahead of the test points\n' % ", ".join('"%s"' % r for r in ADDS) + _OLD_SEC)
EDITS = [(_OLD_FP, _NEW_FP), (_OLD_AT, _NEW_AT), (_OLD_SEC, _NEW_SEC)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), text):
            refuse("already applied, or designator %s is in use in the target" % ref)
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
    drawn = [n.args[0].value for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "part" and n.args
             and isinstance(n.args[0], ast.Constant) and n.args[0].value in ADDS]
    if sorted(drawn) != sorted(ADDS):
        refuse("the patched generator does not draw %s once each" % (ADDS,))
    return new


# NOT RELEASED: record l8r2 drafts this change for board A's generator owner and never applies it. Writing the repository's own
# gen_sch_a.py is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check
# of this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_a.py")
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
