#!/usr/bin/env python3
"""Name the checked energy basis in l3r2.yaml's `energy_basis` (L3-R2, MESHSAT-1357, 30 September 2026). PREPARED, NOT RUN:
the coordinator sends the basis's final tip after its confirmation; until then energy_basis stays null.

It refuses unless: the basis record, each output and the check are files of this tree; the check's first line reads
"accepted: yes"; the check names the basis's tip as checked (the text "tip `<tip>`" in its head, exactly); energy_basis is
null (a second run is refused). It writes {record, sha16, outputs: [{path, sha16}], check, check_sha16, tip} and adds the
check to `energy_basis_checks` if it is not listed. The hold (conditional/cond.py basis_state) and the gate
(render_l3r2.py basis_ok) verify the same things again whenever they run.

Usage: python3 set_energy_basis.py --record v2/docs/records/l3plane/ENERGY-BASIS.md \\
         --outputs v2/docs/records/l3plane/weather_basis.out,v2/docs/records/l3plane/energy_basis.out \\
         --check v2/docs/records/l3r2/checks/energy-basis-check-N/CHECK-N.md --tip <sha> [--check-only]
       [--data PATH --root DIR]   (a copy of l3r2.yaml and the tree its paths resolve against: the tests)
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402


def arg(argv, k, default=None):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else default


def main(argv):
    import yaml
    data_path = arg(argv, "--data", C.L3DATA)
    root = arg(argv, "--root", E.TOP)
    rec, outs, chk, tip = arg(argv, "--record"), arg(argv, "--outputs"), arg(argv, "--check"), arg(argv, "--tip")
    try:
        if not (rec and outs and chk and tip): E.refuse("--record, --outputs, --check and --tip are all required")
        raw = open(data_path, encoding="utf-8").read()
        data = yaml.safe_load(raw)
        if data.get("energy_basis"): E.refuse("energy_basis is already named: this script has run")
        files = [rec] + outs.split(",") + [chk]
        for f in files:
            if os.path.isabs(f) or not os.path.isfile(os.path.join(root, f)): E.refuse("%s is not a file of this tree" % f)
        head = open(os.path.join(root, chk), encoding="utf-8").read().split("\n")
        if head[0].strip() != "accepted: yes": E.refuse("%s reads %r on its first line, not 'accepted: yes'" % (chk, head[0].strip()))
        if not any(("tip `%s`" % tip) in l for l in head[:12]): E.refuse("%s does not name tip `%s` as the one it checked" % (chk, tip))
        sha = lambda f: E.sha16(os.path.join(root, f))
        block = ("energy_basis:\n  record: %s\n  sha16: %s\n  tip: %s\n  outputs:\n%s  check: %s\n  check_sha16: %s\n"
                 % (rec, sha(rec), tip, "".join("    - {path: %s, sha16: %s}\n" % (o, sha(o)) for o in outs.split(",")),
                    chk, sha(chk)))
        new = E.set_top_scalar(raw, "energy_basis", "null").replace("energy_basis: null\n", block, 1)
        if not any(str(c.get("record")) == chk for c in data.get("energy_basis_checks") or []):
            anchor = "\n# The baselined definition documents"
            if new.count(anchor) != 1: E.refuse("the energy_basis_checks list's end is not where l3r2.yaml puts it")
            new = new.replace(anchor, "\n  - {record: %s, sha16: %s, of: \"stream l3plane's ENERGY-BASIS.md, branch fnd/l3plane at %s\", "
                              "verdict: ACCEPTED}%s" % (chk, sha(chk), tip, anchor), 1)
        d2 = yaml.safe_load(new)
        ok, why = C.basis_state(d2, root)
        if not ok: E.refuse("the named basis does not verify: %s" % why)
    except E.Refused as e:
        print("set_energy_basis: REFUSED: %s" % e)
        return 2
    print("set_energy_basis: energy_basis names %s at %s, %d outputs, check %s (accepted: yes, tip %s)%s"
          % (rec, sha(rec), len(outs.split(",")), chk, tip, " (check only, nothing written)" if "--check-only" in argv else ""))
    if "--check-only" not in argv:
        open(data_path, "w", encoding="utf-8").write(new)
        print("set_energy_basis: written %s" % os.path.relpath(data_path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
