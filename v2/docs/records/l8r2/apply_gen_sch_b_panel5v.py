#!/usr/bin/env python3
"""apply_gen_sch_b_panel5v.py: DRAFT for board B's generator owner (Layer 8 record l8r2, item 3, finding L5R2-F03, MESHSAT-1357,
3 October 2026). NOT APPLIED to the tree by this record; its author ran it only on scratch copies.

The defect (L5R2-F03): PANEL_5V reaches board C on two conductors of the panel ribbon (J_PANEL pins 1 and 2), Wurth WR-CAB
63912615521CAB flat cable (1 A per conductor maximum) and WR-BHD 61202623021 sockets (1 A per contact maximum). Its only limit is
F1, a Bourns MF-MSMF110-2 polyfuse that holds 1.10 A and trips at 2.20 A at 23 C: a fault drawing up to 2.2 A (in its
time-to-trip) puts up to 1.1 A on each conductor, over the cable's and the socket's printed 1 A. (The brief named board A or C;
the limiter is on board B, `gen_sch_b.py`'s F1 between +5V_DEV and PANEL_5V, so the correction is on board B.)

The correction: a TPS259631 eFuse U901 (the part board B fits as U23 and U24, TI SLVSET8A) from +5V_DEV ahead of F1, so the
panel's current is limited to 1.375 to 1.613 A (R901 604 Ohm by Equation 7, 1.506 A nominal; the tolerance interpolated between
the printed 909 Ohm row, 0.949 to 1.051 A, and the 453 Ohm row, 1.83 to 2.147 A: INFERRED), at most 0.81 A on each of the two
conductors with an equal split and 0.88 A with a 20 percent resistance mismatch (INFERRED), under the 1 A, and over board C's
1.0 A declared peak (gen_sch_c.py's +5V rail). The current limit responds in 87 us typical, the short circuit in 5 us (SLVSET8A
7.6). F1 stays as the backstop (its 2.2 A trip now coordinated behind the eFuse's 1.613 A), so the energy chain and the placement
keep their F1; its pin 1 moves to the eFuse's output PANEL_5V_EF. The OVLO divider is 42.2k over 10k (the pin at 0.98 V on 5.1 V,
inside SLVSET8A's 0.5 to 2 V; cut at 6.11 to 6.50 V), not the helper's 100k over 10k, which leaves the pin at 0.46 V on a 5 V
input (the U23 and U24 finding of board A's comment). EN to +5V_DEV through R905 100 k (note 2); FLT to +3V3_DEV through R902.

Usage:  apply_gen_sch_b_panel5v.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused."""
import ast
import difflib
import os
import re
import sys

NAME = "apply_gen_sch_b_panel5v"
GEN = "gen_sch_b.py"
ADDS = ("U901", "R901", "R902", "R903", "R904", "R905", "C901", "C902")
NETS = ("PANEL_5V_EF", "PANEL_EF_EN", "PANEL_EF_FLT")
_EF = ('# L5R2-F03, drafted by Layer 8 record l8r2 (MESHSAT-1357, 3 October 2026): the panel ribbon carries PANEL_5V on two conductors\n'
       '# of 1 A each (Wurth WR-CAB 63912615521CAB, WR-BHD 61202623021); F1 alone let a fault reach 2.2 A, 1.1 A a conductor. U901 limits\n'
       '# it to 1.375 to 1.613 A (R901 604 R, TPS2596 Equation 7; tolerance interpolated between SLVSET8A\'s printed rows: INFERRED), at\n'
       '# most 0.81 A a conductor, over board C\'s 1.0 A peak; F1 stays behind it as the backstop. OVLO 42.2k over 10k (0.98 V on the pin).\n'
       'ic("U901", 9, "TPS259631DDAR eFuse +5V_DEV -> PANEL_5V_EF (ILM 1.506 A): the panel ribbon\'s two conductors under 1 A each", "DDA8", '
       '{"1": "GND", "2": "U901_DVDT", "3": "PANEL_EF_EN", "4": "+5V_DEV", "5": "PANEL_5V_EF", "6": "PANEL_EF_FLT", "7": "U901_ILM", "8": "U901_OVLO", "9": "GND"}, "C2155778")\n'
       'c("C901", "10n", "U901_DVDT", "GND"); r("R901", "604R 1% (ILM: 1.506 A)", "U901_ILM", "GND"); r("R902", "10k", "PANEL_EF_FLT", "+3V3_DEV")\n'
       'r("R903", "42.2k 1%", "+5V_DEV", "U901_OVLO"); r("R904", "10k 1% (OVLO)", "U901_OVLO", "GND", "R", "C25804"); c("C902", "100n", "+5V_DEV", "GND")\n'
       'r("R905", "100k", "PANEL_EF_EN", "+5V_DEV")   # SLVSET8A note 2: EN pulled to a supply under 6 V through 100 k or more\n'
       '_intent.rail("PANEL_5V_EF", 5.0, 0.60, 1.0, "U901", loads={"F1": 0.60}, series_of="+5V_DEV", converted=False,\n'
       '             source_ic="U901 is a TPS2596 eFuse: its OUT pin IS the power path",\n'
       '             note="the panel feed between the eFuse U901 (1.375 to 1.613 A) and the backstop polyfuse F1 (L5R2-F03, record l8r2)")\n')
EDITS = [
    ('"F1": 0.60,            # polyfuse -> PANEL_5V, board C\'s own 5 V rail (its intent declares 0.6 A)',
     '"U901": 0.60,          # eFuse U901 then the polyfuse F1 -> PANEL_5V, board C\'s own 5 V rail (its intent declares 0.6 A; L5R2-F03)'),
    ('_GND_LOADS = {k: v for k, v in _DEV_LOADS.items() if k not in ("F1", "F2", "F3")}',
     '_GND_LOADS = {k: v for k, v in _DEV_LOADS.items() if k not in ("U901", "F2", "F3")}'),
    ('_GND_LOADS["J_PANEL"] = _DEV_LOADS["F1"]', '_GND_LOADS["J_PANEL"] = _DEV_LOADS["U901"]'),
    ('part("F1", "Device", "Polyfuse", "1.1A hold 1812 (Bourns MF-MSMF110-2)", "F1812", {"1": "+5V_DEV", "2": "PANEL_5V"}, "C89647")',
     _EF + 'part("F1", "Device", "Polyfuse", "1.1A hold 1812 (Bourns MF-MSMF110-2), the backstop behind U901", "F1812", {"1": "PANEL_5V_EF", "2": "PANEL_5V"}, "C89647")'),
    ('_intent.rail("PANEL_5V", 5.0, 0.60, 0.60, "F1", loads={"J_PANEL": 0.60}, series_of="+5V_DEV", converted=False,',
     '_intent.rail("PANEL_5V", 5.0, 0.60, 0.60, "F1", loads={"J_PANEL": 0.60}, series_of="PANEL_5V_EF", converted=False,'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def in_use(text, ref):
    return re.search(r'(?:part|ic|r|c|tp|nfet|vh2|synth|q|esd|efuse)\(\s*"%s"' % re.escape(ref), text) is not None


def patched(text):
    for ref in ADDS:
        if in_use(text, ref):
            refuse("designator %s is already in use in the target" % ref)
    for net in NETS:
        if re.search(r'"%s"' % re.escape(net), text):
            refuse("net %s already exists in the target" % net)
    new = text
    for old, rep in EDITS:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    try:
        ast.parse(new)
    except SyntaxError as e:
        refuse("the result does not parse: %s" % e)
    return new


# NOT RELEASED: record l8r2 drafts this change for the board's generator owner and never applies it. Writing the repository's own
# generator is refused until RELEASE.md beside this script reads "released: yes" on its first line and names an accepted check of
# this record ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may be written (the tests do).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE_GEN = os.path.join(REPO, "v2", "ecad", "tools", GEN)
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
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + GEN, "b/" + GEN, n=0))
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
