"""The registry the prepared owner-decision chains of layer 3 start from (MESHSAT-1357, round 5, the closure).

While the tree's rows are undecided, the tree's own registry. Once the closure decided them (the owner's clarifications
D-28 and D-29), the registry as it stood before the closure, read from git at l3r2.yaml's closure_cycle.pre_closure_commit,
so the prepared scripts and the re-issue generator stay under test on the options they were written for. Not a test
module: test_l3r2.py, test_l3r4.py and test_l3r5.py import it.
"""
import os
import subprocess
import tempfile

import yaml
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REG = os.path.join(TOOLS, "pcb_requirements.yaml")
_CACHE = {}


def tree_decided():
    y = yaml.safe_load(open(REG, encoding="utf-8"))
    return any(str(r.get("decides") or "").startswith("L3-OD") for r in y["owner_rulings"])


def base_registry():
    """A path holding the registry the chains start from (never the tree's own file when the tree is decided)."""
    if not tree_decided(): return REG
    if "base" in _CACHE: return _CACHE["base"]
    data = yaml.safe_load(open(os.path.join(ROOT, "v2", "docs", "handover", "layer3", "l3r2.yaml"), encoding="utf-8"))
    sha = ((data.get("closure_cycle") or {}).get("pre_closure_commit"))
    if not sha: raise Skip("the tree's rows are decided and l3r2.yaml names no pre-closure commit")
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:v2/ecad/tools/pcb_requirements.yaml" % sha], capture_output=True)
    if r.returncode != 0: raise Skip("the pre-closure registry %s is not in this repository" % sha[:12])
    # the readings' bindings carried to the tree's where the tree has rebound them since (round 5's fix round: CFL-016 to
    # the status page DEFINITION-STATUS.md as it now stands, which a PASS bound to the older sha fails on)
    import sys
    sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "l3r2"))
    import l3edit as E
    raw = E.rebind_to_tree(r.stdout.decode("utf-8"), open(REG, encoding="utf-8").read())
    path = os.path.join(tempfile.mkdtemp(prefix="l3-pre-closure-"), "pcb_requirements.yaml")
    open(path, "w", encoding="utf-8").write(raw)
    _CACHE["base"] = path
    return path
