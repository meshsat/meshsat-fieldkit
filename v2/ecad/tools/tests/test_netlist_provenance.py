#!/usr/bin/env python3
"""A committed netlist travels with its provenance sidecar (17 September 2026).

`sch_prov` records which schematic and which generator wrote a netlist, and `check_contracts` refuses a netlist
whose sidecar names a schematic or a generator this tree does not hold, falling back to the mtime rule only where
there is no sidecar at all. The sidecars live in `out/`, which is gitignored, so every clone had six netlists with
no identity and the contract gate judged them by their mtimes, which is the rule that refused one board and passed
five in the identical state this morning. The sidecar is force-added beside its netlist now, and this holds it."""
import os, sys, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip   # `Skip` was used below and never imported: without git this raised NameError,
                           # so the one branch that exists to DECLINE reported a failure instead (20 Sep 2026)

ECAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def t_every_committed_netlist_has_its_provenance_sidecar_committed_beside_it():
    r = subprocess.run(["git", "ls-files", "--", "."], cwd=ECAD, capture_output=True, text=True)
    files = set(r.stdout.split())
    nets = sorted(f for f in files if f.endswith(".net") and "/out/" in f)
    assert nets, "no committed netlist found under v2/ecad (the git index is unreadable here?)"
    missing = [n for n in nets if n + ".prov.json" not in files]
    assert not missing, "committed netlists with no committed provenance sidecar: %s" % missing


def t_every_committed_netlist_has_its_intent_committed_beside_it():
    """THE SAME GAP AS THE PROVENANCE SIDECAR, ONE FILE ALONG (20 September 2026, found by running the suite
    where KiCad is in a tree cleaned of everything untracked).

    `out/<stem>-intent.json` is the DECLARATION: every rail with its current, source, loads and budget, every
    node with the voltage a part on it can see, every bypass capacitor with the pin it serves, every pair
    class with its impedance target. `dc_drop`, `dc_density`, `via_current`, `derate`, `intent_checks`,
    `check_contracts` and the generated `PCB-BRING-UP.md` all read it, and `out/` is gitignored, so a fresh
    clone of this repo had six netlists, six provenance sidecars and NOT ONE declaration. Every one of those
    gates would declare its input absent there, and the bring-up sheet renders as six empty sections, which
    is what `test_rule_windows` refuses.

    The file is reproducible from the schematic generator, but only where KiCad is, and it is EVIDENCE as
    well as input: it says what current each rail was judged at. It is force-added for the same reason the
    provenance sidecars were on 17 September."""
    import subprocess
    r = subprocess.run(["git", "ls-files", "--", "."], cwd=ECAD, capture_output=True, text=True)
    if r.returncode != 0: raise Skip("no git index here")
    files = set(r.stdout.split("\n"))
    nets = [f for f in files if f.endswith(".net") and "/out/" in f]
    assert nets, "no committed netlist found under v2/ecad (the git index is unreadable here?)"
    missing = [n for n in nets
               if not any(f.startswith(n.rsplit("/out/", 1)[0] + "/out/") and f.endswith("-intent.json")
                          for f in files)]
    assert not missing, ("committed netlists with no committed intent declaration beside them: %s"
                         % sorted(missing))
