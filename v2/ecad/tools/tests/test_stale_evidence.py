#!/usr/bin/env python3
"""Evidence about a board a directory no longer holds is not that board's evidence (17 September 2026).

THE DEFECT: a phase directory holds one board and its routed/ snapshot holds the verdicts about it. When a new
board is adopted, the chain writes its own and everything the previous board's sweep left behind stays, beside
a board it was never taken on. Board B's snapshot carries a gate reading from the 951-footprint B19 while the
design being routed is the 957-footprint B21, and until today no gate named the board it read, so nothing
could tell them apart.
"""
import os, sys, json, tempfile, hashlib
import prune_stale_evidence as P

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _dir(tmp, board=b"(kicad_pcb v1)\n", verdicts=()):
    """A project directory the manifest can name: the tool refuses to judge one it cannot."""
    tmp = os.path.join(tmp, "pcb-d-aprs-d9")
    os.makedirs(os.path.join(tmp, "routed"), exist_ok=True)
    bp = os.path.join(tmp, "pcb-d-aprs.kicad_pcb")
    open(bp, "wb").write(board)
    for name, rec in verdicts:
        json.dump(rec, open(os.path.join(tmp, "routed", name + ".verdict.json"), "w"))
    return bp


def t_a_verdict_naming_another_board_is_stale():
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d, verdicts=[("check_pcb_d", {"verdict": "PASS",
                                                "inputs": {"board": {"sha256_16": "0" * 16}}})])
        stale, kept, unknown = P.judge(os.path.dirname(bp))
        assert [t for t, _ in stale] == ["check_pcb_d"], (stale, kept, unknown)


def t_a_verdict_naming_this_board_is_kept():
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d)
        sha = P.sha16(bp)
        json.dump({"verdict": "PASS", "inputs": {"board": {"sha256_16": sha}}},
                  open(os.path.join(os.path.dirname(bp), "routed", "check_pcb_d.verdict.json"), "w"))
        stale, kept, unknown = P.judge(os.path.dirname(bp))
        assert not stale and ("check_pcb_d", "names this board") in kept, (stale, kept)


def t_the_letter_is_an_identity_too():
    """A gate given `--board d` writes "d" where another writes a sha, and both say which board they judged.
    The first version called board D's own ground_system stale because of it."""
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d, verdicts=[("sensitive_nodes", {"verdict": "PASS", "inputs": {"board": "d"}})])
        stale, kept, unknown = P.judge(os.path.dirname(bp))
        assert not stale, stale


def t_a_set_level_verdict_is_never_stale():
    """The contracts, the certification and the energy chain are judged on netlists and folders: they are as
    true beside one board as another, and the registry says so through their evidence scope."""
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d, verdicts=[("check_contracts", {"verdict": "PASS", "inputs": {"board": {"sha256_16": "0" * 16}}})])
        stale, kept, unknown = P.judge(os.path.dirname(bp))
        assert not stale, stale


def t_an_anonymous_board_specific_verdict_is_reported_and_not_removed():
    """Until today no gate named the board it read. Removing every anonymous verdict would throw away the
    evidence of every board cut before this morning, so they are listed and kept unless --unnamed is given."""
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d, verdicts=[("check_pcb_d", {"verdict": "PASS", "inputs": {}})])
        stale, kept, unknown = P.judge(os.path.dirname(bp))
        assert not stale and [t for t, _ in unknown] == ["check_pcb_d"], (stale, unknown)
        stale2, _k, _u = P.judge(os.path.dirname(bp), unnamed=True)
        assert [t for t, _ in stale2] == ["check_pcb_d"], stale2


def t_nothing_is_removed_without_apply():
    import subprocess
    with tempfile.TemporaryDirectory() as d:
        bp = _dir(d, verdicts=[("check_pcb_d", {"verdict": "PASS", "inputs": {"board": {"sha256_16": "0" * 16}}})])
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "prune_stale_evidence.py"), os.path.dirname(bp)],
                           capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
        assert os.path.isfile(os.path.join(os.path.dirname(bp), "routed", "check_pcb_d.verdict.json")), "the default deleted a file"
        assert "STALE" in r.stdout, r.stdout


def t_every_committed_snapshot_is_clean_today():
    """The tree's own state: no board carries a verdict that names another board."""
    import glob
    ecad = os.path.dirname(TOOLS)
    bad = []
    for d in sorted(glob.glob(os.path.join(ecad, "pcb-*"))):
        if not os.path.isdir(os.path.join(d, "routed")): continue
        stale, _k, _u = P.judge(d)
        bad += ["%s: %s (%s)" % (os.path.basename(d), t, why) for t, why in stale]
    assert not bad, "a snapshot carries evidence about another board:\n  " + "\n  ".join(bad)


def t_a_directory_the_manifest_cannot_name_is_not_judged_at_all():
    """Absence must never become a deletion any more than it becomes a pass: with no identities to compare
    against, every verdict that names its board would read as another board's."""
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "routed"))
        json.dump({"verdict": "PASS", "inputs": {"board": {"sha256_16": "0" * 16}}},
                  open(os.path.join(d, "routed", "check_pcb_d.verdict.json"), "w"))
        stale, kept, unknown = P.judge(d)
        assert not stale and not kept and unknown and "names no board for this directory" in unknown[0][1], (stale, kept, unknown)
