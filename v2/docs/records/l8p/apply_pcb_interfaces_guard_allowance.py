#!/usr/bin/env python3
"""apply_pcb_interfaces_guard_allowance.py: DRAFT for Layer 5, the owner of v2/ecad/tools/pcb_interfaces.yaml (Layer 8 record l8p,
MESHSAT-1357, round 11, 7 October 2026; finding L8P-R9-F2, register row L4A-68). NOT APPLIED by this record; the integrator runs it
for Layer 5 (Layers 5 to 12 are paused: this is the named prerequisite text, applied when the owner's gate lets Layer 5 take it).

What it states: the thermal guard's allowance on the dock's enable loop, which record l8p's section 7 owed to Layer 5 since round 8
(L8P-R8-F4: 30 uA and C261's 1 uF, round 8's single path) and its round 9 restated for the fail-safe delta (10c: at most 40 uA cold and
50 uA tripped, printed maxima with the off leakage at the doubling; C261 and C268, 330 nF each). One field is added to IF-AE-DOCK,
dock_en_guard, before its vin_raw block, as pin1_vsys_dock states a drafted change beside the committed pins map: the loop's pins stay
the committed netlists' (GND) until record l8p's drafts apply.

l8p_cprot.py prints this TEXT in its output's section 7 (it imports it: one source).

Usage:  apply_pcb_interfaces_guard_allowance.py TARGET [--check | --write]     (default --check: nothing is written)
The anchor must occur exactly once; the new text must not occur yet; the result must parse as YAML and carry the field under
board_to_board.contracts.IF-AE-DOCK with the text below.
Exit 0: checked (or written); 3: refused (the target is not the expected text, or the change is already applied)."""
import difflib
import sys

import yaml

NAME = "apply_pcb_interfaces_guard_allowance"
TEXT = ("DOCK_EN_OUT on board A carries the thermal guard's draw: at most 40 uA with the guard cold and 50 uA tripped (record l8p 10c: "
        "printed maxima, the off leakage at the doubling, the worst single fault), C261 and C268 330 nF each and U61's 4.7 uF "
        "behind them; path 2's regulator and switch load VBAT, not the loop; DOCK_EN_RET may be held at ground by board A's Q60, "
        "Q44 and board P's Q107 with Q108, and DOCK_EN_OUT by board A's Q61 (path 2 tripped); DRAFTED (R-222, R-244), applied with "
        "record l8p's drafts; replaces round 8's 30 uA and 1 uF")
ANCHOR = '      vin_raw: {voltage: "as declared 9 to 36 V (v_work 36 V). Layer 4 (L4-E9 1d IF-06; LH-03): solar 7.378 V (the corrected knee\'s\n'


def block():
    words = TEXT.split(" ")
    lines, cur = [], '      dock_en_guard: "RECORD l8p ROUND 11 (7 October 2026; L8P-R9-F2, register row L4A-68):'
    for w in words:
        if len(cur) + 1 + len(w) > 136:
            lines.append(cur)
            cur = "        " + w
        else:
            cur += " " + w
    lines.append(cur + '"')
    return "\n".join(lines) + "\n"


NEW = block()


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(text):
    if "dock_en_guard:" in text:
        refuse("already applied (dock_en_guard is present)")
    if text.count(ANCHOR) != 1:
        refuse("the anchor (IF-AE-DOCK's vin_raw line) occurs %d times, not once" % text.count(ANCHOR))
    new = text.replace(ANCHOR, NEW + ANCHOR)
    if new == text:
        refuse("the result does not differ")
    try:
        doc = yaml.safe_load(new)
        got = doc["board_to_board"]["contracts"]["IF-AE-DOCK"]["dock_en_guard"]
    except Exception as e:  # noqa: BLE001  any parse or shape failure refuses
        refuse("the result does not parse as YAML with the field in place: %s" % e)
    if " ".join(got.split()) != " ".join(("RECORD l8p ROUND 11 (7 October 2026; L8P-R9-F2, register row L4A-68): " + TEXT).split()):
        refuse("the field does not read back as the text")
    old = yaml.safe_load(text)["board_to_board"]["contracts"]["IF-AE-DOCK"]
    if {k: v for k, v in doc["board_to_board"]["contracts"]["IF-AE-DOCK"].items() if k != "dock_en_guard"} != old:
        refuse("another field of IF-AE-DOCK moved")
    return new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/pcb_interfaces.yaml", "b/pcb_interfaces.yaml", n=0))
    if not write:
        print("%s: CHECK OK, 1 edit, nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    back = open(target, encoding="utf-8").read()
    if back != new or back.count(NEW) != 1:
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN, 1 edit" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
