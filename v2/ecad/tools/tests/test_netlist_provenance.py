#!/usr/bin/env python3
"""A committed netlist travels with its provenance sidecar (17 September 2026).

`sch_prov` records which schematic and which generator wrote a netlist, and `check_contracts` refuses a netlist
whose sidecar names a schematic or a generator this tree does not hold, falling back to the mtime rule only where
there is no sidecar at all. The sidecars live in `out/`, which is gitignored, so every clone had six netlists with
no identity and the contract gate judged them by their mtimes, which is the rule that refused one board and passed
five in the identical state this morning. The sidecar is force-added beside its netlist now, and this holds it."""
import os, subprocess

ECAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def t_every_committed_netlist_has_its_provenance_sidecar_committed_beside_it():
    r = subprocess.run(["git", "ls-files", "--", "."], cwd=ECAD, capture_output=True, text=True)
    files = set(r.stdout.split())
    nets = sorted(f for f in files if f.endswith(".net") and "/out/" in f)
    assert nets, "no committed netlist found under v2/ecad (the git index is unreadable here?)"
    missing = [n for n in nets if n + ".prov.json" not in files]
    assert not missing, "committed netlists with no committed provenance sidecar: %s" % missing
