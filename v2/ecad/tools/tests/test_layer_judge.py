#!/usr/bin/env python3
"""The layer count is judged and never changed (MESHSAT-862, P0, 12 September 2026).

The owner reopened every board's layer count on 11 September and ruled that each needs its own written
decision carrying the measurement that forced it. So the pipeline gained an instrument for the
measurement, and this file holds the line the instrument must not cross:

  it never says REDUCE                 a verdict is a measurement; adopting one is the owner's
  it changes no file                   it is a report, and a report that can edit is not one
  it refuses an unrouted board         judging what a layer NEEDS from what it CARRIES is meaningless
                                       on a board that was never routed, and the first version did it
  the floor refuses a layer change     `SetCopperLayerCount` and `STACKS` are a reserved class, checked
                                       before any mode, so no automatic path can adopt one
"""
import os, re, sys, json, subprocess, tempfile
from harness import Skip   # noqa: F401

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))   # tools -> ecad -> v2 -> the repo


def t_the_judge_never_says_reduce():
    src = open(os.path.join(TOOLS, "layer_judge.py"), errors="replace").read()
    body = src.split('"""', 2)[2]
    # The VERDICT STRINGS only. A comment saying the word must not appear is not the word appearing, and
    # the first version of this rule failed on exactly that line.
    code = "\n".join(l.split("#", 1)[0] for l in body.splitlines())
    bad = re.findall(r'["\']((?:REDUCE|DROP)\b[^"\']*)', code)
    if bad:
        raise AssertionError("layer_judge emits a decision rather than a measurement: %s" % bad[:2])
    for word in ("KEEP", "QUESTION"):
        if word not in body:
            raise AssertionError("layer_judge no longer emits %r" % word)


def t_the_judge_changes_nothing():
    src = open(os.path.join(TOOLS, "layer_judge.py"), errors="replace").read()
    body = src.split('"""', 2)[2]
    for bad in ("open(board, \"w\")", "shutil.copy", "os.remove", "os.unlink", ".Save(", "SetCopperLayerCount"):
        if bad in body:
            raise AssertionError("layer_judge can write a board or a generator: %s" % bad)


def t_the_judge_refuses_an_unrouted_board():
    """A placed board's copper is entirely locked escapes, and it carries no evidence about need."""
    sys.path.insert(0, TOOLS)
    import importlib.util
    sp = importlib.util.spec_from_file_location("layer_judge_t", os.path.join(TOOLS, "layer_judge.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    src = open(os.path.join(TOOLS, "layer_judge.py"), errors="replace").read()
    if "locked_share_pct" not in src:
        raise AssertionError("the judge does not measure how much of the copper is locked")
    if "this board is not routed" not in src:
        raise AssertionError("the judge does not refuse an unrouted board")
    if "locked_mm" not in open(os.path.join(TOOLS, "layer_audit.py"), errors="replace").read():
        raise AssertionError("layer_audit no longer reports locked length, so the refusal cannot fire")


def t_the_floor_refuses_a_layer_count_change():
    """Proved by running the floor over a real one-line change, in a worktree, not by reading a table."""
    if not os.path.isdir(os.path.join(REPO, ".git")):
        raise Skip("not a git worktree")
    tmp = tempfile.mkdtemp(prefix="meshsat-layer-floor-")
    wt = os.path.join(tmp, "wt")
    r = subprocess.run(["git", "-C", REPO, "worktree", "add", "--detach", wt, "HEAD"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode:
        raise Skip("could not cut a worktree: %s" % r.stderr.strip()[:80])
    try:
        g = os.path.join(wt, "v2", "ecad", "tools", "gen_pcb_a.py")
        s = open(g, errors="replace").read()
        s2 = s.replace("board.SetCopperLayerCount(6)", "board.SetCopperLayerCount(4)", 1)
        if s2 == s:
            raise Skip("gen_pcb_a.py no longer sets its layer count on one line")
        open(g, "w").write(s2)
        out = subprocess.run([sys.executable, os.path.join(wt, "v2", "ecad", "tools", "reserved.py"), "--diff"],
                             cwd=os.path.join(wt, "v2", "ecad", "tools"), capture_output=True, text=True, timeout=300)
        if out.returncode == 0:
            raise AssertionError("the floor ACCEPTED a layer-count change: %s" % out.stdout[-300:])
        if "layer count and stackup" not in out.stdout:
            raise AssertionError("refused, but not as a layer decision: %s" % out.stdout[-300:])
    finally:
        subprocess.run(["git", "-C", REPO, "worktree", "remove", "--force", wt], capture_output=True, timeout=300)
        subprocess.run(["git", "-C", REPO, "worktree", "prune"], capture_output=True, timeout=120)
