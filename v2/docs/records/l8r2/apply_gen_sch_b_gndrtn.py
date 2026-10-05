#!/usr/bin/env python3
"""apply_gen_sch_b_gndrtn.py: DRAFT for board B's generator owner (Layer 8 record l8r2, round 8, finding L8R2-F31, MESHSAT-1357,
4 October 2026), board B's half of apply_gen_sch_a_gndrtn.py. NOT APPLIED to the tree by this record; its author ran it only on
scratch copies (the tests write scratch copies).

The defect (L8R2-F31, and the collaborator's recheck V3, checks/astra-check-t5-recheck-cx41.md). The grounds of boards A and B are
one net joined by the VH leads' pin 2 contacts and the seventeen ground conductors of the ribbons J_AB1 and J_AB2, in parallel, and
nothing sets how the supply return divides between them. Over the contact resistances their makers permit (JST VH: no minimum,
20 mOhm after test; Wurth IDC: no minimum, 20 mOhm) one lead's pin 2 carries more than its printed 10 A and a ribbon conductor more
than its printed 1 A (l8r2_gndret.out section 3d, every vertex enumerated).

The correction (the record's section 3g; l8r2_gndret.out sections 3j and 6): a DEDICATED GROUND RETURN between the two boards, three
leads, each an Amass XT60 pair with BOTH contacts on GND and two 12 AWG conductors of 150 mm: six conductors in parallel whose
resistance, with every termination at its maker's printed limit (1.0 mOhm a contact, Amass XT60 specification 2021V1), is low
enough that every VH pin 2, every ribbon conductor and every XT60 contact stays inside its printed rating at every vertex of the
contact-resistance box. Two leads hold every row on the printed ratings; the third makes the rows at the inside air hold on the
least rating consistent with each maker's sheet, where no derating curve is printed, and keeps the printed-rating rows with one
lead unmated. What this draft draws on board B:
  J_GR1 to J_GR3  Amass XT60-F, pins 1 and 2 both on GND, beside J_54V. FEMALE on the boards and male on the leads: the pack lead
                carries an XT60-F for board E's J_BATT (XT60-M), so it cannot be plugged into a ground return socket, and a return
                lead's XT60-M cannot be plugged into J_BATT. The land is KiCad's Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical
                (NOT READ on the record's host, which has no KiCad library: the box's generation checks it); no LCSC code is
                carried (Layer 6 names it).
  the return's declaration: _gnd_return (this record's apply_gen_sch_b_gndret.py, which must be applied first) names J_GR1 to
                J_GR3 beside the leads as the places the return leaves the board, so the copper rules solve the ground with the
                current leaving where it does; the peak, the typical and the loads are unchanged (they are the leads' sums).
What it does not change: no lead, no ribbon and no load; the VH pin 2 contacts and the ribbons' ground conductors stay (the leads'
returns stay beside their supplies; the ribbons' signal returns stay as they are).

Order: board B's round, after apply_gen_sch_b_gndret.py (it edits that draft's helper); otherwise anywhere. In one release with
apply_gen_sch_a_gndrtn.py: a return socket on one board alone is refused by check_gndret_netlist.py.
Usage:  apply_gen_sch_b_gndrtn.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the target is not the expected text, gndret is not applied, the change is already applied,
a designator is in use, or the repository's own generator is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_gndrtn"
N_RETURN = 3
ADDS = tuple("J_GR%d" % k for k in range(1, N_RETURN + 1))
NETS = ()
LAND = "Connector_AMASS:AMASS_XT60-F_1x02_P7.20mm_Vertical"

_OLD_FP = '"VH2": "Connector_JST:JST_VH_B2P-VH_1x02_P3.96mm_Vertical", "VH4": "Connector_JST:JST_VH_B4P-VH_1x04_P3.96mm_Vertical",'
_NEW_FP = _OLD_FP + ' "XT60F": "%s",   # l8r2 round 8: the ground return sockets\n' % LAND
_OLD_AT = 'part("J_54V", "Connector_Generic", "Conn_01x02", "JST-VH socket, 10 A: 54 V PoE feed from A22 J_54V: + -", "VH2", {"1": "+54V_POE", "2": "GND"}, "C274411")\n'
_NEW_AT = _OLD_AT + (
    "# L8R2-F31, RECORD l8r2 ROUND 8 (MESHSAT-1357, 4 October 2026): THE DEDICATED GROUND RETURN TO A22. Boards A and B share one ground\n"
    "# over the VH leads' pin 2 and the ribbons' ground conductors, and nothing set how the supply return divided between them: over\n"
    "# the contact resistances their makers permit, one lead's pin 2 passed 10 A and a ribbon conductor 1 A. Three return leads, each an\n"
    "# Amass XT60 pair with both contacts on GND and two 12 AWG conductors, carry the return whatever the other contacts do (record\n"
    "# l8r2, l8r2_gndret.out section 6: every vertex of the contact-resistance box). XT60-F here and XT60-M on the leads, so the pack\n"
    "# lead (an XT60-F, for board E's J_BATT) cannot be plugged into any of the sockets. DRAFTED, not applied.\n"
    + "".join('part("J_GR%d", "Connector_Generic", "Conn_01x02", "Amass XT60-F, both contacts GND: ground return %d to A22 J_GR%d (lead: XT60-M both ends, '
              '2 x 12 AWG, 150 mm)", "XT60F", {"1": "GND", "2": "GND"})\n' % (k, k, k) for k in range(1, N_RETURN + 1)))
_OLD_SRCS = '    _srcs = list(leads) + ["J_54V"]\n'
_NEW_SRCS = _OLD_SRCS + ('    _rets = [%s]   # record l8r2 round 8 (L8R2-F31): the dedicated return\'s sockets, where most of the '
                         'return leaves this board; they carry no rail, so the leads\' sums below are unchanged\n' % ", ".join('"%s"' % r for r in ADDS))
_OLD_RAIL = '    _intent.rail("GND", 0.0, _typ, _peak, _srcs, loads=_l,'
_NEW_RAIL = '    _intent.rail("GND", 0.0, _typ, _peak, _srcs + _rets, loads=_l,'
_OLD_NOTE = '                  "the lead contacts and the ribbons\' ground conductors by resistance, not lead by lead (record l8r2 round 7)")\n'
_NEW_NOTE = ('                  "the lead contacts and the ribbons\' ground conductors by resistance, not lead by lead (record l8r2 round 7); "\n'
             '                  "since round 8 the dedicated return J_GR1 to J_GR3 (three XT60 leads, six 12 AWG conductors) carries most of it")\n')
EDITS = [(_OLD_FP, _NEW_FP), (_OLD_AT, _NEW_AT), (_OLD_SRCS, _NEW_SRCS), (_OLD_RAIL, _NEW_RAIL), (_OLD_NOTE, _NEW_NOTE)]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    for ref in ADDS:
        if re.search(r'"%s"' % re.escape(ref), text):
            refuse("already applied, or designator %s is in use in the target" % ref)
    if "def _gnd_return(" not in text:
        refuse("apply_gen_sch_b_gndret.py is not applied to the target (the return's helper _gnd_return is absent): apply it first")
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
