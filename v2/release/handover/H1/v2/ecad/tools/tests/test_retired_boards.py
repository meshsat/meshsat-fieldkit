#!/usr/bin/env python3
"""A retired board is not this board's identity, and its directory is not this board's evidence
(MESHSAT-1357, 26 September 2026).

Found by the regeneration parity run of 25 September 2026: `rules_status._project_dirs` globbed `<project>*`, so board A's evidence
directories were `pcb-a-power/` (the A18 board, MESHSAT-830's predecessor) as well as `pcb-a-power-a23/` (the phase
directory its routeflow profile names), and `_board_identities` hashed the board file of every one of them and of
their `routed/` snapshots. A verdict taken on A18, or on the E9 board that still sits in `pcb-e1-dock-e7/routed/`
while board E declares E17, would have been accepted as current evidence for the board being judged. It was
latent: on 26 September no verdict anywhere in the tree named one of those boards (613 tracked verdicts and the
784 in the main checkout were read). The rule is stated on fixtures so it holds the day one does.

The phase directory is the one `_phase_dir` already reads from the routeflow profile. Its own board is an identity;
a board in its `routed/` is one only when its silk carries the phase the board declares, which is where
`silk_fix_all.py` stamps it and where `subject()` already reads it.
"""
import os, sys, json, hashlib, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_status as S


def _board(path, legend):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write('(kicad_pcb\n\t(gr_text "MeshSat %s" (at 1 1) (layer "F.SilkS"))\n)\n' % legend)
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _world():
    """v2/ecad with a legacy directory (X1), the phase directory (X2) and a retired snapshot in its routed/."""
    ecad = tempfile.mkdtemp(prefix="retired-")
    tools = os.path.join(ecad, "tools"); os.makedirs(os.path.join(tools, "routeflow")); os.makedirs(os.path.join(tools, "boards"))
    json.dump({"board": "pcb-x", "project": "v2/ecad/pcb-x-x2"}, open(os.path.join(tools, "routeflow", "x.json"), "w"))
    json.dump({"name": "pcb-x", "phase": "X2"}, open(os.path.join(tools, "boards", "x.json"), "w"))
    sha = {"legacy": _board(os.path.join(ecad, "pcb-x", "pcb-x.kicad_pcb"), "X1"),
           "phase": _board(os.path.join(ecad, "pcb-x-x2", "pcb-x.kicad_pcb"), "X2"),
           "retired_snapshot": _board(os.path.join(ecad, "pcb-x-x2", "routed", "pcb-x.kicad_pcb"), "X1")}
    for d in ("pcb-x/out", "pcb-x-x2/out", "out"): os.makedirs(os.path.join(ecad, d), exist_ok=True)
    json.dump({"tool": "gate_legacy", "verdict": "PASS", "ts": "2026-09-25T00:00:00Z"},
              open(os.path.join(ecad, "pcb-x", "out", "gate_legacy.verdict.json"), "w"))
    json.dump({"tool": "gate_phase", "verdict": "PASS", "ts": "2026-09-25T00:00:00Z"},
              open(os.path.join(ecad, "pcb-x-x2", "routed", "gate_phase.verdict.json"), "w"))
    return ecad, tools, sha


def _in(world, fn):
    ecad, tools, sha = world
    saved = (S.ECAD, S.HERE, S.R.board_facts)
    S.ECAD, S.HERE = ecad, tools
    S.R.board_facts = lambda *a, **k: {"x": {"project": "pcb-x"}}
    try: return fn({"boards": {"x": {"project": "pcb-x"}}})
    finally: S.ECAD, S.HERE, S.R.board_facts = saved


def t_a_legacy_directory_is_not_a_board_s_evidence():
    """DEFECTIVE before the fix: `pcb-x*` matched the legacy `pcb-x/` and its verdicts were read."""
    w = _world()
    dirs = _in(w, lambda m: S._project_dirs("x", m))
    rel = sorted(os.path.relpath(d, w[0]) for d in dirs)
    assert "pcb-x/out" not in rel, "the retired directory pcb-x/ is still read as board X's evidence: %s" % rel
    assert "pcb-x-x2/routed" in rel and "out" in rel, rel
    vs = _in(w, lambda m: S._verdicts("x", m))
    assert "gate_legacy" not in vs and "gate_phase" in vs, sorted(vs)


def t_a_retired_board_is_not_an_identity_and_the_phase_board_is():
    """DEFECTIVE before the fix: the legacy board (X1) and the X1 snapshot in the phase directory's routed/ were
    both identities, so a verdict taken on either counted as current for X2."""
    w = _world(); sha = w[2]
    ident = _in(w, lambda m: S._board_identities("x", m))
    assert sha["phase"] in ident, "the phase directory's own board lost its identity"
    assert sha["legacy"] not in ident, "the legacy directory's board is still an identity"
    assert sha["retired_snapshot"] not in ident, "a routed/ snapshot of another phase is still an identity"


def t_a_routed_snapshot_of_the_declared_phase_is_an_identity():
    """ACCEPTABLE: the finished board of the declared phase, saved in routed/, is the board the routed-stage
    verdicts were taken on."""
    w = _world()
    sha = _board(os.path.join(w[0], "pcb-x-x2", "routed", "pcb-x.kicad_pcb"), "X2 routed")
    ident = _in(w, lambda m: S._board_identities("x", m))
    assert sha in ident, "the declared phase's routed board is not an identity"
