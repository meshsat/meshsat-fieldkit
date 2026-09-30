#!/usr/bin/env python3
"""Close open item S-127, the energy basis, as a session closure (L3-R2, MESHSAT-1357, 30 September 2026; CHECK-4 of L3-R2,
minor 2). Applied once: a second run refuses.

S-127's own closing condition is "the basis and its check are filed and REQ-072 is re-read on them". The basis is filed
and bound in l3r2.yaml: stream l3plane's ENERGY-BASIS.md with weather_basis.out, energy_basis.out and three_cases.out, at
fnd/l3plane cd8720a1, with its accepted check (the energy stream's CHECK-5, filed as
v2/docs/records/l3r2/checks/energy-basis-check-5/CHECK-5.md), in commit 9493847c. This script verifies that binding again
(basis_binding.py, both energy_basis and power_path_check), reads REQ-072's four cases from three_cases.out by exact keys
(basis_reader.py), and then:
  1. moves S-127 to closed_items, closed by commit 9493847c with its closing evidence naming the files and their shas;
  2. REQ-072 stops waiting on S-127 and gains an evidence entry re-reading it on the basis, its bindings the three files;
     its statement, acceptance and verdict (FAIL) are not changed.
The result validates (0 errors) or nothing is written.

Usage: python3 apply_l3r2_s127.py [--check] [--registry PATH]
"""
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "conditional"))
import l3edit as E  # noqa: E402
import cond as C  # noqa: E402
import basis_reader as BR  # noqa: E402

COMMIT = "9493847ce78c2ef688d81b9e38e7585738d4c0d1"
BASIS = "v2/docs/records/l3plane/ENERGY-BASIS.md"
CASES = "v2/docs/records/l3plane/three_cases.out"
CHECK = "v2/docs/records/l3r2/checks/energy-basis-check-5/CHECK-5.md"
LIDS = ("4S14P tablet out", "4S15P QMX out", "4S9P both kept")


def num(v):
    return float(v.split(",")[1].split()[0]) if v.startswith("NOT MET") else None


def rng(F, case, inp):
    vals = [num(F[(case, inp, lid)][b]) for lid in LIDS for b in ("TYP", "WAB")]
    if any(v is None for v in vals): E.refuse("case %s %s does not read NOT MET on every lid" % (case, inp))
    return "%.1f to %.1f" % (min(vals), max(vals))


def build(raw):
    d = E.parse(raw)
    if not any(x["id"] == "S-127" for x in d["open_items"]): E.refuse("S-127 is not open: this script has run")
    data = C.l3data()
    for key in ("energy_basis", "power_path_check"):
        ok, why = C.basis_state(data, key=key)
        if not ok: E.refuse("the basis is not filed and verified: %s" % why)
    if data["energy_basis"]["check"] != CHECK: E.refuse("l3r2.yaml's energy_basis names another check than %s" % CHECK)
    if not E.git("cat-file", "-e", COMMIT).returncode == 0: E.refuse("commit %s is not in this repository" % COMMIT)
    F = BR.four_cases(open(os.path.join(E.TOP, CASES), encoding="utf-8").read())
    setting = BR.derated_setting(open(os.path.join(E.TOP, CASES), encoding="utf-8").read())
    c_nom = {lid: F[("c", "NOM", lid)] for lid in LIDS}
    if num(c_nom["4S9P both kept"]["TYP"]) is None: E.refuse("the 4S9P lid reads met on the corrected path")
    sha = lambda p: E.sha16(os.path.join(E.TOP, p))
    ev = ("%s, %s and %s read on 30 September 2026 (L3-R2, the energy basis S-127 asked for; bound in "
          "v2/docs/handover/layer3/l3r2.yaml to fnd/l3plane cd8720a1 and filed by commit %s): on SC-37's reference day, "
          "with the circuit as drawn every lid fails M1 (%s Wh unserved at nominal inputs, %s Wh at the worst established "
          "inputs), and so does the derated variant with U3 at %s A (%s Wh at nominal inputs); the resistor-only proposal is "
          "INCONCLUSIVE, its lower bound failing by %s Wh; only on the hypothetical corrected power path, with every finding "
          "of R11-DEPENDENCY.md closed, do the 4S14P and 4S15P lids meet at nominal inputs (%s and %s Wh, TYP), and at the "
          "worst established inputs only conditionally on three undocumented efficiencies. No figure is demonstrated "
          "capability. This entry changes no statement or acceptance: the verdict stays FAIL."
          % (BASIS, CASES, CHECK, COMMIT[:8], rng(F, "a", "NOM"), rng(F, "a", "WE"), setting, rng(F, "a'", "NOM"),
             rng(F, "b", "NOM"), c_nom["4S14P tablet out"]["TYP"].split()[0], c_nom["4S15P QMX out"]["TYP"].split()[0]))
    closing = ("The energy basis is filed and checked: %s (sha256/16 %s) with its outputs, among them %s (%s), at fnd/l3plane "
               "cd8720a1, and its accepted check %s (%s, 'accepted: yes', naming that tip), named and bound in "
               "v2/docs/handover/layer3/l3r2.yaml's energy_basis and power_path_check by commit %s, every file byte identical "
               "to the tip (basis_binding.py). REQ-072 was re-read on it in the evidence entry this closure adds and reads "
               "FAIL: on the circuit as drawn no lid meets M1." % (BASIS, sha(BASIS), CASES, sha(CASES), CHECK, sha(CHECK), COMMIT[:8]))
    for x in (ev, closing): E.screen(x, "an added text")
    it = next(x for x in d["open_items"] if x["id"] == "S-127")
    raw, _ = E.remove_entry(raw, "S-127", "open_items")
    raw = E.insert_at_section_end(raw, "closed_items", "  - id: S-127\n    closed_by: commit %s\n    closing_evidence: >-\n%s"
                                  "    title: >-\n%s" % (COMMIT, E.fold(closing, 6), E.fold(it["title"], 6)))
    binds = ['"%s@%s"' % (p, sha(p)) for p in (BASIS, CASES, CHECK)]
    def f(b):
        b = E.set_flow(b, "waits_on", [x for x in E.flow_items(b, "waits_on") if x != "S-127"])
        b = E.add_list_entry(b, "evidence", ev)
        lines, a, z = E._field_lines(b, "evidence_bound_to")
        cur = [l.strip()[2:].strip() for l in lines[a + 1:z]]
        return "\n".join(lines[:a] + ["    evidence_bound_to:"] + ["      - %s" % x for x in cur + [x for x in binds if x not in cur]] + lines[z:])
    return E.replace_entry(raw, "REQ-072", f, "records")


def main(argv):
    path = argv[argv.index("--registry") + 1] if "--registry" in argv else E.REGISTRY
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        before, after = E.parse(old), E.parse(new)
        got = set(E.diff_entries(before, after))
        want = {("open_items", "S-127", "removed"), ("closed_items", "S-127", "added"), ("records", "REQ-072", "changed")}
        if got != want: E.refuse("the entries changed are not the list: %s" % sorted(got))
        if set(E.changed_fields(before, after, "records", "REQ-072")) != {"waits_on", "evidence", "evidence_bound_to"}:
            E.refuse("REQ-072 changed beyond its waits, evidence and bindings")
        errs, warns = E.validate(new)
        if errs: E.refuse("the result does not validate: %s" % "; ".join(errs[:5]))
    except E.Refused as e:
        print("apply_l3r2_s127: REFUSED: %s" % e)
        return 2
    for sec, eid, kind in sorted(got):
        print("%-14s %-8s %s %s" % (sec, eid, kind, ",".join(E.changed_fields(before, after, sec, eid)) if kind == "changed" else ""))
    print("apply_l3r2_s127: S-127 closed by commit %s, REQ-072 re-read on the basis, validator 0 errors, %d warnings%s"
          % (COMMIT[:8], len(warns), " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_l3r2_s127: written %s" % os.path.relpath(path, E.TOP))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
