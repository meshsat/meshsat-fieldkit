#!/usr/bin/env python3
"""Restate l3r2.yaml's power-path list from the checked classes of stream r11dep's second issue (L3-R2, MESHSAT-1357, 30
September 2026). PREPARED, NOT RUN: it refuses until l3r2.yaml's power_path_check names r11dep's record with an accepted
check, every file byte identical to the checked tip (basis_binding.py).

It reads prepared/power_path_classes.yaml (A-1 and A-2, existing defects of the circuit as drawn; B-1 to B-5, defects the
resistor-only proposal introduces; C-1 to C-9, missing evidence, not failures), asserts every item's anchor word for word
in the filed record, and then:
  1. replaces the `power_path_corrections` list (PP-01 to PP-08, the first issue's) with the sixteen classed items, each
     with its correction, closure criterion, layer, closure item and the record's section and tip as its source;
  2. restates closure items L3-C37 to L3-C44 to the items they now carry and adds L3-C46 to L3-C53 after them.
The result is re-parsed and read back; a second run is refused (the list already carries A-1).

Usage: python3 restate_power_path.py [--check] [--data PATH --root DIR]   (a copy and its tree: the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402

PREP = os.path.join(HERE, "prepared", "power_path_classes.yaml")
SECTION = {"existing": "2a", "introduced": "2b", "missing": "2c"}
CLASS = {"existing": "existing defect of the circuit as drawn", "introduced": "defect the resistor-only proposal introduces",
         "missing": "missing evidence, not a failure"}


def arg(argv, k, default=None):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else default


def q(s):
    return '"%s"' % str(s).replace('"', "'")


def main(argv):
    import yaml
    data_path = arg(argv, "--data", C.L3DATA)
    root = arg(argv, "--root", E.TOP)
    try:
        raw = open(data_path, encoding="utf-8").read()
        data = yaml.safe_load(raw)
        ok, why = C.basis_state(data, root, "power_path_check")
        if not ok: E.refuse("the power path's check is not filed and verified: %s" % why)
        if any(str(c.get("id")) == "A-1" for c in data.get("power_path_corrections") or []):
            E.refuse("power_path_corrections already carries the classes: this script has run")
        ppc = data["power_path_check"]
        rec = open(os.path.join(root, ppc["record"]), encoding="utf-8").read()
        classes = yaml.safe_load(open(PREP, encoding="utf-8"))["classes"]
        for c in classes:
            if c["anchor"] not in rec: E.refuse("%s does not carry %s's anchor %r" % (ppc["record"], c["id"], c["anchor"][:60]))
        lines = ["power_path_corrections:"]
        for c in classes:
            src = "%s section %s, at %s (%s, accepted)" % (ppc["record"], SECTION[c["class"]], ppc["tip"], ppc["check"])
            lines.append("  - {id: %s, class: %s, closure: %s, layer: %s, item: %s, criterion: %s, source: %s}"
                         % (c["id"], q(CLASS[c["class"]]), c["closure_item"], c["layer"], q(c["item"]), q(c["criterion"]), q(src)))
        a = raw.index("\npower_path_corrections:\n") + 1
        b = raw.index("\n\n", a)
        new = raw[:a] + "\n".join(lines) + raw[b:]
        # closure items: L3-C37 to L3-C44 restated, L3-C46 to L3-C53 added after L3-C44
        cl = []
        for c in classes:
            cl.append('  - {id: %s, item: %s, whose: SESSION, closes_by: %s, state: DOWNSTREAM}' % (
                c["closure_item"], q("%s, %s: %s (layer %s)" % (c["id"], CLASS[c["class"]], c["item"], c["layer"])),
                q("%s; an engineering task (D-24, D-25), not a layer 3 prerequisite" % c["criterion"])))
        old = [l for l in new.split("\n") if any(l.startswith("  - {id: L3-C%d, " % n) for n in range(37, 45))]
        if len(old) != 8: E.refuse("closure items L3-C37 to L3-C44 are not eight lines (%d)" % len(old))
        start = new.index(old[0]); end = new.index(old[-1]) + len(old[-1])
        if new[start:end].count("\n") != 7: E.refuse("closure items L3-C37 to L3-C44 are not contiguous")
        new = new[:start] + "\n".join(cl) + new[end:]
        for dch in E.DASHES:
            if dch in new: E.refuse("the result carries a dash character")
        d2 = yaml.safe_load(new)
        got = [c["id"] for c in d2["power_path_corrections"]]
        if got != [c["id"] for c in classes]: E.refuse("read back: the list reads %s" % got)
        ids = {c["id"] for c in d2["closure"]}
        if not {c["closure_item"] for c in classes} <= ids: E.refuse("read back: a closure item is missing")
    except E.Refused as e:
        print("restate_power_path: REFUSED: %s" % e)
        return 2
    print("restate_power_path: %d classed items from %s at %s; closure items L3-C37 to L3-C44 restated, L3-C46 to L3-C53 "
          "added%s" % (len(classes), ppc["record"], ppc["tip"], " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        open(data_path, "w", encoding="utf-8").write(new)
        print("restate_power_path: written %s" % os.path.relpath(data_path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
