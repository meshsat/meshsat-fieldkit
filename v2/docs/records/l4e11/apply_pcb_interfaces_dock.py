#!/usr/bin/env python3
"""apply_pcb_interfaces_dock.py: DRAFT for the Layer 4 coordinator and the interface owner (task L4-E11, MESHSAT-1357, the fix
round for the consolidation review cx36, B1, 2 October 2026). NOT APPLIED to the tree by L4-E11; its author ran it only on scratch
copies (the tests write scratch copies).

Why (L4E11-SOURCE-ONLY-AND-ENTRY.md section 15a): board E's auxiliary domain moves from CELL_F to board A's VSYS over the dock's
pin 1 (apply_gen_sch_a_charger.py and apply_gen_sch_e_aux.py), behind board A's eFuse U42 (the review of the provisional fixes,
L4-F03, section 16e). The A/E contract records it: IF-AE-DOCK's pin 1 becomes VSYS_DOCK (A's VBAT through U42; E's VSYS_E),
BAT-F06's charge share is reversed, the feed, its protection and the ground return with seven 813 contacts are stated; and
check_contracts.py (v2/ecad/tools/check_contracts.py, in this tree) learns that VSYS_DOCK on A and VSYS_E on E are one contact.

TARGET selects the edit set by its file name:
  pcb_interfaces.yaml   IF-AE-DOCK: the alias, pin 1, pins_history, charge_share, the new aux_feed, the findings list;
                        the result must load as YAML and read pin 1 as VSYS_DOCK.
  check_contracts.py    the ALIAS table gains {"VSYS_DOCK", "VSYS_E"}; the result must parse as Python.

ORDER: with the two generator drafts (the dock's pin 1 on both boards at once).

Usage:  apply_pcb_interfaces_dock.py TARGET [--check | --write]     (default --check: nothing is written)
Each edit's old text must occur exactly once and its new text must differ and must not occur yet; the result must parse.
Exit 0: checked (or written); 3: refused (the target is not the expected text, the change is already applied, or the
repository's own file is named before RELEASE.md releases it)."""
import ast
import difflib
import os
import sys

import yaml

NAME = "apply_pcb_interfaces_dock"
YAML_EDITS = [
    ('aliases: [["DOCK_SPARE", "BLK_SPARE"], ["CELL+", "CELL_F", "E\'s pack positive after its F3 blade"]]',
     'aliases: [["DOCK_SPARE", "BLK_SPARE"], ["CELL+", "CELL_F", "E\'s pack positive after its F3 blade"], ["VSYS_DOCK", "VSYS_E", "A\'s VSYS through its eFuse U42 to E\'s auxiliary domain on pin 1 (L4-E11)"]]'),
    ("pins: {1: GND, 2: GND, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,",
     "pins: {1: VSYS_DOCK, 2: GND, 3: GND, 4: GND, 5: GND, 6: GND, 7: GND, 8: SHORE_INHIBIT, 9: USB_E6_P,"),
    ('the control line since, beside 5 to 7 and 11"',
     'the control line since, beside 5 to 7 and 11; pin 1 carries VSYS (A\'s VSYS_DOCK behind the eFuse U42, E\'s VSYS_E) since\n'
     '        L4-E11\'s fix rounds (drafted 2 October 2026), board E\'s auxiliary domain\'s feed"'),
    ('charge_share: "BAT-F06, taken by the session under the owner\'s standing rule (ARCHITECTURE.md section 4.4): board E\'s\n'
     '        always-on domain and fans sit on CELL_F, the pack side of A\'s charge shunt R17, so they share the charger\'s host-free\n'
     '        256 mA; stated, and the host sets ChargeCurrent to cover them; the VSYS-side feed through this contract is not taken"',
     'charge_share: "BAT-F06 reversed by L4-E11\'s fix round (the consolidation review cx36, B1; drafted 2 October 2026): with TI\'s\n'
     '        BQ25730 and its battery FETs between VSYS and R17, board E\'s always-on domain and fans leave CELL_F for VSYS on pin 1 (E\'s\n'
     '        VSYS_E), so the source carries them while the charge is held and the pack feeds none of them; on CELL_F remain the pack\n'
     '        path, D3, C1 and the pack monitor R42 and R43 (0.14 mA at 16.884 V)"\n'
     '      aux_feed: "pin 1, one 813 contact: 1.32 A declared (U12 0.8 A, the mixers\' 12.0 V rail U22 0.52 A at the floor with both\n'
     '        fans at full speed; L4-E11 section 18b), 38 percent of 3.5 A, about 8.5 K by w3de\'s assumed I2 rise; VSYS 9.688 to 17.375 V\n'
     '        (L4-E11 section 15d). Protected on board A by the eFuse U42 (TI TPS16630,\n'
     '        R(ILIM) 11.0k: a sustained overload regulated to 1.47 to 1.80 A, a steady setting and not an instantaneous ceiling;\n'
     '        current limiting at most 202 ms, auto-retry after 500 to 800 ms): in a sustained overload the contact at most 51.5\n'
     '        percent of 3.5 A; a short applied while on, a start into a short and the retry are left to the bench\'s qualification (L4-E11\n'
     '        E11-38); VSYS_E at least 9.508 V at 1.32 A (L4-E11 sections 16e, 17a and 18b). The ground return keeps seven 813 contacts: at the\n'
     '        32.1 A coincidence with every Mill-Max pin at 20 mOhm an 813 ground contact carries 2.238 A, 2.406 A with one open (64\n'
     '        and 69 percent), 75.5 and 79.3 C at the 51 C inside air and 89.5 and 93.3 C at the +55 C margin\'s 65 C (w3de\'s model\n'
     '        and assumptions; W3DE-DOCK-R1\'s residual moves by one contact\'s step). A lost pin 1 unpowers E\'s controller, which A\n'
     '        reads on HOT-R1 as the detector lost"'),
    ("findings: [R4A-N13, R4A-N12, R8E-N01, EQ-16, W3DE-DOCK-R1, A04-D2, W3-F09, BAT-F06, PWR-F12]",
     "findings: [R4A-N13, R4A-N12, R8E-N01, EQ-16, W3DE-DOCK-R1, A04-D2, W3-F09, BAT-F06, PWR-F12, L4-E11-B1]"),
]
PY_EDITS = [
    ('         ({"DOCK_SPARE", "BLK_SPARE"}, "the spare contact, named after the connector on each side")]',
     '         ({"DOCK_SPARE", "BLK_SPARE"}, "the spare contact, named after the connector on each side"),\n'
     '         ({"VSYS_DOCK", "VSYS_E"}, "A\'s VSYS through its eFuse U42 feeds E\'s auxiliary domain on the dock\'s pin 1; each board names its branch (L4-E11)")]'),
]


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def edits_for(target):
    base = os.path.basename(target)
    if base == "pcb_interfaces.yaml" or base.endswith("interfaces.yaml"):
        return "yaml", YAML_EDITS
    if base == "check_contracts.py" or base.endswith("contracts.py"):
        return "py", PY_EDITS
    refuse("TARGET is neither pcb_interfaces.yaml nor check_contracts.py")


def patched(text, kind, edits):
    new = text
    for old, rep in edits:
        if rep == old:
            refuse("an edit's new text equals its old text")
        if new.count(rep) != 0:
            refuse("already applied (the new text is present)")
        if new.count(old) != 1:
            refuse("the old text occurs %d times, not once" % new.count(old))
        new = new.replace(old, rep)
    if new == text:
        refuse("the result does not differ")
    if kind == "yaml":
        try:
            doc = yaml.safe_load(new)
        except yaml.YAMLError as e:
            refuse("the result does not load as YAML: %s" % e)
        dock = [v for k, v in _walk(doc) if k == "IF-AE-DOCK"]
        if len(dock) != 1 or dock[0].get("pins", {}).get(1) != "VSYS_DOCK" or "aux_feed" not in dock[0]:
            refuse("IF-AE-DOCK does not read pin 1 as VSYS_DOCK with its aux_feed")
    else:
        try:
            ast.parse(new)
        except SyntaxError as e:
            refuse("the result does not parse: %s" % e)
    return new


def _walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


# NOT RELEASED: task L4-E11 drafts this change for the interface owner and never applies it. Writing the repository's own
# pcb_interfaces.yaml or check_contracts.py is refused until RELEASE.md beside this script reads "released: yes" on its first line
# and names an accepted check of L4-E11 ("check: <repository path whose first line is 'accepted: yes'>"). A copy elsewhere may
# be written (the tests do, on scratch copies).
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
TREE = [os.path.join(REPO, "v2", "ecad", "tools", "pcb_interfaces.yaml"), os.path.join(REPO, "v2", "ecad", "tools", "check_contracts.py")]
RELEASE = os.path.join(HERE, "RELEASE.md")


def released():
    if not os.path.isfile(RELEASE):
        refuse("NOT RELEASED: no RELEASE.md; L4-E11's values wait on an accepted check")
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
    kind, edits = edits_for(target)
    if write and any(os.path.realpath(target) == os.path.realpath(t) for t in TREE):
        released()
    text = open(target, encoding="utf-8").read()
    new = patched(text, kind, edits)
    base = os.path.basename(target)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/" + base, "b/" + base, n=0))
    if not write:
        print("%s: CHECK OK, %d edit(s), nothing written" % (NAME, len(edits)))
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or any(back.count(rep) != 1 for _o, rep in edits):
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN, %d edit(s)" % (NAME, len(edits)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
