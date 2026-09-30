#!/usr/bin/env python3
"""Name a checked record in l3r2.yaml: the energy basis (`energy_basis`) or the power path at Option A(i)'s currents
(`power_path_check`, D-24) (L3-R2, MESHSAT-1357, 30 September 2026). PREPARED, NOT RUN: the coordinator sends the final tip
after its confirmation; until then both stay null.

It refuses unless (CHECK-3 of L3-R2, B1: the accepted check is bound to the files filed):
  - the record, each output and the check are files of this tree;
  - the record and each output are byte identical to the file of that path at the tip the check checked, read with
    `git show <tip>:<path>` from this repository;
  - the check's first line reads "accepted: yes" and its head names that tip ("tip `<tip>`");
  - the key is null (a second run is refused).
It writes {record, sha16, tip, outputs: [{path, sha16}], check, check_sha16}; for the energy basis it also adds the check to
`energy_basis_checks` if it is not listed. The hold (conditional/cond.py basis_state) and the gate (render_l3r2.py basis_ok)
verify all of it again, from the recorded tip, every time they run (basis_binding.py).

Usage: python3 set_energy_basis.py [--key energy_basis|power_path_check] --record PATH --outputs PATH[,PATH...]
         --check PATH --tip <sha> [--check-only]
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
import basis_binding as BB  # noqa: E402


def arg(argv, k, default=None):
    return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else default


def main(argv):
    import yaml
    key = arg(argv, "--key", "energy_basis")
    data_path = arg(argv, "--data", C.L3DATA)
    root = arg(argv, "--root", E.TOP)
    rec, outs, chk, tip = arg(argv, "--record"), arg(argv, "--outputs"), arg(argv, "--check"), arg(argv, "--tip")
    try:
        if key not in ("energy_basis", "power_path_check"): E.refuse("--key is energy_basis or power_path_check")
        if not (rec and outs and chk and tip): E.refuse("--record, --outputs, --check and --tip are all required")
        raw = open(data_path, encoding="utf-8").read()
        data = yaml.safe_load(raw)
        if data.get(key): E.refuse("%s is already named: this script has run" % key)
        outl = outs.split(",")
        for f in [rec] + outl + [chk]:
            if os.path.isabs(f) or not os.path.isfile(os.path.join(root, f)): E.refuse("%s is not a file of this tree" % f)
        sha = lambda f: E.sha16(os.path.join(root, f))
        for f in [rec] + outl:
            at = BB.tip_sha16(E.TOP, tip, f)
            if at is None: E.refuse("the tip %s carries no %s in this repository" % (tip, f))
            if at != sha(f): E.refuse("%s is not byte identical to the file of that path at the checked tip %s" % (f, tip))
        head = open(os.path.join(root, chk), encoding="utf-8").read().split("\n")
        if head[0].strip() != "accepted: yes": E.refuse("%s reads %r on its first line, not 'accepted: yes'" % (chk, head[0].strip()))
        if not BB.names_tip(head, tip): E.refuse("%s does not name tip `%s` as the one it checked" % (chk, tip))
        listed = BB.listed_sha256("\n".join(head))
        for f in [rec] + outl:
            if f in listed and listed[f] != __import__("hashlib").sha256(open(os.path.join(root, f), "rb").read()).hexdigest():
                E.refuse("%s lists %s at another sha256" % (chk, f))
        block = ("%s:\n  record: %s\n  sha16: %s\n  tip: %s\n  outputs:\n%s  check: %s\n  check_sha16: %s\n"
                 % (key, rec, sha(rec), tip, "".join("    - {path: %s, sha16: %s}\n" % (o, sha(o)) for o in outl), chk, sha(chk)))
        line = "%s: null\n" % key
        if raw.count("\n" + line) != 1: E.refuse("'%s' is not where l3r2.yaml puts it" % line.strip())
        new = raw.replace("\n" + line, "\n" + block, 1)
        if key == "energy_basis" and not any(str(c.get("record")) == chk for c in data.get("energy_basis_checks") or []):
            anchor = "\n# The baselined definition documents"
            if new.count(anchor) != 1: E.refuse("the energy_basis_checks list's end is not where l3r2.yaml puts it")
            new = new.replace(anchor, "\n  - {record: %s, sha16: %s, of: \"stream l3plane's ENERGY-BASIS.md, branch fnd/l3plane at %s\", "
                              "verdict: ACCEPTED}%s" % (chk, sha(chk), tip, anchor), 1)
        ok, why = C.basis_state(yaml.safe_load(new), root, key)
        if not ok: E.refuse("the named %s does not verify: %s" % (key, why))
    except E.Refused as e:
        print("set_energy_basis: REFUSED: %s" % e)
        return 2
    print("set_energy_basis: %s names %s at %s, %d outputs, check %s (accepted: yes, tip %s, every file identical at the tip)%s"
          % (key, rec, sha(rec), len(outl), chk, tip, " (check only, nothing written)" if "--check-only" in argv else ""))
    if "--check-only" not in argv:
        open(data_path, "w", encoding="utf-8").write(new)
        print("set_energy_basis: written %s" % os.path.relpath(data_path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
