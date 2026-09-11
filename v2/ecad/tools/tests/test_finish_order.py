#!/usr/bin/env python3
"""One finish, its stage order, and the profile that dispatches it.

MESHSAT-862, 11 September 2026. There were fifteen finish_*.sh, 728 lines, clones of one another with a board
name changed, and the drift between the clones was not cosmetic:

  * FIVE ran the stub router BEFORE the clean-up. The order established with B13 on 5 September is clean up
    first, then the stub router, then a zone refill, then the check, and it has two written reasons, both paid
    for: the stub router's closing via counts as a plane clearance violation when the zone fill is stale, so a
    legal closure is reverted; and `cleanup_dangling.py` running afterwards can remove the very via the closure
    used. The five with the wrong order are the boards whose deliverables shipped.
  * TWELVE OF TWELVE never ran `netlist_board.py`, so a board could pass every gate carrying a phantom net or a
    footprint the netlist does not have. Found by a reviewer, not by a gate, which is why this file exists.
  * Nine never ran `pruned_gate.py`, four never ran `pour_stitch.py`, three never matched pairs.

The twelve are retired into `finish.sh`, which carries the order once and is driven by `boards/<letter>.json`.
These tests hold the collapse in place: the order, every gate present, and each routeflow profile agreeing with
itself about which phase it cuts (five did not, and one of those would have had the supervisor verify a folder
the finish never wrote).
"""
import os, re, json, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINISH = os.path.join(TOOLS, "finish.sh")

STAGES = ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch", "stub_router")

# Every gate that decides whether a board is finished. A gate absent from the finish is a bar nothing tests.
GATES = ("hardset.py", "check_pcb_", "dc_drop.py", "impedance_check.py", "netlist_board.py", "check_contracts.py",
         "pruned_gate.py", "pair_match.sh", "quality_pass.sh", "silk_fix_all.py", "stackup_write.py")


def _order(path):
    """The stages of a script, in the order they first appear, comments excluded."""
    seen, out = set(), []
    for line in open(path, errors="replace"):
        t = line.strip()
        if t.startswith("#"): continue
        for s in STAGES:
            if re.search(r"\b%s\.py" % s, t) and s not in seen: seen.add(s); out.append(s)
    return out


def t_the_one_finish_cleans_up_before_it_stubs():
    o = _order(FINISH)
    assert "stub_router" in o, o
    for before in ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch"):
        assert before in o, (before, o)
        assert o.index(before) < o.index("stub_router"), \
            "%s must run before the stub router: %s" % (before, o)


def t_the_finish_runs_every_gate():
    """The reviewer's finding as a rule: netlist_board.py was in finish.sh and in no clone, so the boards that
    shipped were never checked against their own netlists."""
    t = "".join(l for l in open(FINISH, errors="replace") if not l.strip().startswith("#"))
    missing = [g for g in GATES if g not in t]
    assert not missing, "finish.sh does not run %s" % missing


def t_a_gate_that_fails_stops_the_finish():
    """A gate whose exit code nothing reads is decoration. Every gate here must be followed by a test of its
    status; `stop` is the one way out."""
    t = open(FINISH, errors="replace").read()
    for g, var in (("dc_drop.py", "DC"), ("impedance_check.py", "IM"), ("netlist_board.py", "NB"), ("check_pcb_", "GATE")):
        assert re.search(r'\[ "\$%s" -eq 0 \] \|\| stop ' % var, t), "%s runs but its status %s is never tested" % (g, var)


def t_no_board_finish_clone_is_left():
    """The clones are retired, and a new one must not appear: the drift they carried is what these tests are for.
    finish_board.sh (the exporter), finish_a18.sh (a one-off re-export of a routed board) and finish_b_after.sh
    (a wrapper on stub_and_finish.sh) are different jobs and are named explicitly."""
    KEEP = {"finish_board.sh", "finish_a18.sh", "finish_b_after.sh", "finish.sh"}
    found = {os.path.basename(p) for p in glob.glob(os.path.join(TOOLS, "finish*.sh"))} - KEEP
    assert not found, "a per-board finish clone is back: %s (the finish is tools/finish.sh, driven by boards/<letter>.json)" % sorted(found)


def t_every_board_has_a_finish_block_with_every_key():
    need = {"stub_layers", "pour_nets", "pair_match", "pair_audit_nets", "post_fix", "pruned_gate", "gate_grep"}
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(p))
        assert "finish" in d, "%s has no finish block" % os.path.basename(p)
        missing = need - set(d["finish"])
        assert not missing, "%s finish block lacks %s" % (os.path.basename(p), sorted(missing))


def t_a_board_that_matches_pairs_names_the_pairs_it_audits():
    """The audit images are what a stopped chain is read from; a board that gates on pairs and names none would
    stop with nothing to look at."""
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        f = json.load(open(p))["finish"]
        if f["pair_match"]:
            assert f["pair_audit_nets"], "%s gates on pairs and names no audit net" % os.path.basename(p)


def t_a_declared_post_fix_exists():
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        pf = json.load(open(p))["finish"]["post_fix"]
        if pf and pf != "-":
            assert os.path.exists(os.path.join(TOOLS, pf)), "%s names a post fix that is not in the tree: %s" % (os.path.basename(p), pf)


def t_every_profile_dispatches_the_one_finish():
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        fin = (json.load(open(p)).get("finish") or {})
        if not fin.get("argv"): continue
        assert os.path.basename(fin["argv"][0]) == "finish.sh", \
            "%s dispatches %s; the finish is tools/finish.sh" % (os.path.basename(p), fin["argv"][0])


def t_a_profile_agrees_with_itself_about_the_phase_it_cuts():
    """`finish.sh` derives the deliverable folder from the phase argument, and routeflow verifies the folder
    named in `deliverable`. Five profiles named a phase one behind the folder their finish actually wrote, so
    the supervisor would have looked for a folder that was never going to exist."""
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        d = json.load(open(p)); fin = d.get("finish") or {}
        if not fin.get("argv") or os.path.basename(fin["argv"][0]) != "finish.sh": continue
        _, _, proj, letter, phase, _log = fin["argv"]
        b = os.path.basename(p)
        assert d.get("phase") == phase, "%s: phase %r, finish argv cuts %r" % (b, d.get("phase"), phase)
        assert os.path.basename(d.get("deliverable", "")) == "meshsat-pcb-%s-revA-%s" % (letter, phase), \
            "%s: deliverable %r against a finish that cuts meshsat-pcb-%s-revA-%s" % (b, d.get("deliverable"), letter, phase)
        assert fin.get("clean_flag") == "out/%s-clean.txt" % phase.lower(), \
            "%s: clean flag %r against phase %s" % (b, fin.get("clean_flag"), phase)
        assert os.path.basename(d.get("project", "").rstrip("/")) == proj, \
            "%s: project %r, the finish runs in %r" % (b, d.get("project"), proj)
        assert os.path.exists(os.path.join(TOOLS, "boards", "%s.json" % letter)), "%s: no board file for %s" % (b, letter)
        # argv[0] is a path relative to the ecad directory, so the working directory is not free. c7 named
        # <PROJECT> and would have died on its first line looking for ./tools there.
        assert fin.get("cwd") == "<ECAD>", "%s: finish cwd %r, but ./tools/finish.sh only resolves from <ECAD>" % (b, fin.get("cwd"))


def t_routeflow_validate_agrees_with_these_rules():
    """The same judgement at runtime, so a profile is checkable before an eight-hour wave rests on it.
    `--dry-run` was not that: it still created the run directory, wrote provenance, ran preflight and took the
    lock, so a box profile could not be checked from the runner at all. Ten of the twelve profiles as they
    stood before the collapse fail `routeflow.py validate`."""
    import subprocess
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "routeflow.py"), "validate", p],
                           capture_output=True, text=True)
        assert r.returncode == 0, "%s: %s" % (os.path.basename(p), (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else r.returncode)
