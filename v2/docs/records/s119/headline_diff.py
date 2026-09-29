#!/usr/bin/env python3
"""headline_diff.py (stream s119, S-119, MESHSAT-1357, 29 September 2026): the headline figures of every output of the
energy chain, before and after the charger rows were restated, read from git (the base of stream s119 against HEAD).

For each output it selects the headline lines by a pattern on the line (parsed per line, the line's own layout; nothing
in prose is interpreted) and prints the base's line and HEAD's line side by side, marked CHANGED or same; it also prints
how many lines of each output differ in all, and the charger rows of energy_inputs.yaml and energy_two_pack.py read with
a YAML reader and an ast reader. Usage (repository root): python3 v2/docs/records/s119/headline_diff.py [--base <rev>]
AI arithmetic on the record's model; nothing is measured.

Second round (item M5 of the stream's check): the first issue named HEAD's commit, which is one commit behind as soon as
its own output is committed; this issue names each file's sha256 (first 16) at the base and now instead, so the output
is true at any commit that carries these files, and it adds U3B's input limit and charge loop."""
import hashlib
import argparse
import ast
import difflib
import re
import subprocess
import sys

import yaml

OUTS = [
    ("v2/docs/records/energy/energy_budget.out",
     [r"^\s+Chain into the node", r"^\s+September\s+4\.01\s+1\.008\s+(100|200|400)\s", r"^\s+node in September and 90",
      r"^\s+The window's own ceiling", r"^\s+node in June, ", r"^\s+First stop at hour", r"^\s+in each period of sun",
      r"^\s+PS-IDLE-SPEC\s+42\.8\s+September\s", r"^\s+usable pack energy Wh", r"^\s+front end, chain", r"^\s+42\.8 W at the node only above"]),
    ("v2/docs/records/energy/energy_architecture.out",
     [r"^chain 0\.", r"^\s+42\.8\s+(100 W|200 W)", r"^\s+chain 0\.\d+ \((low|high) bracket\)",
      r"^\s+4S18P, window 200 W ,\s+400 Wp", r"^\s+4S1[5-9]P, \d+ Wp in the 100 W window", r"^\s+4S1[89]P, \d+ Wp, window 100 W: "]),
    ("v2/docs/records/energy/energy_4s6p.out", [r"^\s+September\s+\+20\s+(100 Wp|200 Wp)"]),
    ("v2/docs/records/energy/checks/recompute.out", [r"^own profile", r"^\s+(400|650) Wp, \+(20|15)\.0 C", r"^\s+4S19P, 1300 Wp"]),
    ("v2/docs/records/a1elec/energy_two_pack.out",
     [r"^\s+lid \+13\.23 C:", r"^\s+start (06|18) UTC:", r"^\s+3d\.", r"^\s+3f\.", r"^\s+U3B at 0\.9", r"^\s+at its minimum: ",
      r"^\s+(4\.3|5\.0|5\.7) A \(", r"^\s+front end loss .* U3 loss", r"^\s+U3B loss "]),
    ("v2/docs/records/a1elec/checks/recheck_two_pack.out", [r"^RESULT"]),
    ("v2/docs/records/a1solar/energy_runs.out",
     [r"^\s+energy_architecture 4S18P", r"^\s+energy_two_pack design case", r"^\s+[ABCF]\s+.*\+20 C (MEETS|NOT MET)", r"^\s+slope \d+: both"]),
    ("v2/docs/records/a1int/reconcile_lid.out", [r"^\s+at 13\.23 C:", r"^\s+650 Wp, lid 20\.00 C"]),
    ("v2/docs/records/a1int/reconcile_lid_panel.out", [r"^\s+[BC], U3 (minimum|bracket|nominal)", r"^\s+(lowest lid temperature|does not meet)"]),
    ("v2/docs/records/s117/efficiency.out", [r"^\s+The energy chain's rows"]),
]


def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)], capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write("headline_diff: %s:%s not found\n" % (rev, path))
        sys.exit(3)
    return r.stdout


def pick(text, pats):
    return [l for l in text.split("\n") if any(re.search(p, l) for p in pats)]


def par_value(src, key):
    """energy_two_pack.py's PAR[key][0], read with ast (the literal of the PAR dict)."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PAR" for t in node.targets):
            for k, v in zip(node.value.keys, node.value.values):
                if isinstance(k, ast.Constant) and k.value == key:
                    return v.elts[0].value
    raise KeyError(key)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="a1f8ec70")
    a = ap.parse_args()
    base = subprocess.run(["git", "rev-parse", "--short=8", a.base], capture_output=True, text=True, check=True).stdout.strip()
    o = ["HEADLINE FIGURES OF THE ENERGY CHAIN, base %s against the committed files (headline_diff.py, stream s119, S-119)" % base,
         "Each file is named with its sha256 (first 16) at the base and now.", ""]
    y0 = yaml.safe_load(show(a.base, "v2/docs/records/energy/energy_inputs.yaml"))
    y1 = yaml.safe_load(show("HEAD", "v2/docs/records/energy/energy_inputs.yaml"))
    c0, c1 = y0["solar"]["chain"][2], y1["solar"]["chain"][2]
    o.append("energy_inputs.yaml, U3's row (eta, low, high): %s, %s, %s  to  %s, %s, %s" % (c0["eta"], c0["low"], c0["high"], c1["eta"], c1["low"], c1["high"]))
    o.append("energy_inputs.yaml, vehicle_entry chain_eta: %s  to  %s" % (y0["solar"]["vehicle_entry"]["chain_eta"]["value"], y1["solar"]["vehicle_entry"]["chain_eta"]["value"]))
    tp = "v2/docs/records/a1elec/energy_two_pack.py"
    for key in ("eta_u3b", "iin_lid_a", "r_lid_chg"):
        o.append("energy_two_pack.py, %s: %s  to  %s" % (key, par_value(show(a.base, tp), key), par_value(show("HEAD", tp), key)))
    o.append("")
    for path, pats in OUTS:
        t0, t1 = show(a.base, path), show("HEAD", path)
        nd = sum(1 for l in difflib.unified_diff(t0.split("\n"), t1.split("\n"), lineterm="", n=0) if l.startswith("-") and not l.startswith("---"))
        h = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
        o.append("== %s (%s to %s): %d of %d lines differ" % (path, h(t0), h(t1), nd, len(t0.split("\n"))))
        l0, l1 = pick(t0, pats), pick(t1, pats)
        if len(l0) != len(l1):
            o.append("   headline line counts differ: %d against %d (printed unpaired)" % (len(l0), len(l1)))
        for i in range(max(len(l0), len(l1))):
            x = l0[i] if i < len(l0) else ""
            y = l1[i] if i < len(l1) else ""
            if x == y:
                o.append("   same     %s" % x.strip())
            else:
                o.append("   CHANGED  was: %s" % x.strip())
                o.append("            now: %s" % y.strip())
        o.append("")
    o.append("END.")
    sys.stdout.write("\n".join(o) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
