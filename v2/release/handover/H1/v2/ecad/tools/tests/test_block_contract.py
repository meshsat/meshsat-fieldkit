#!/usr/bin/env python3
"""The dock block against the board whose pins land on it (rule SCH-003 for E5, MESHSAT-862, 17 Sep 2026).

Board E5 has no schematic and no netlist: `gen_pcb_e5.py` reads board A's BOARD FILE, finds the spring-pin
connector and puts a target under each pin carrying that pin's net. `check_contracts.py` had declared that
unjudgeable and written INCONCLUSIVE, which was honest and left the one BLIND-MATE interface in the kit with
no check on its pin map at all: the pins are hidden once it is assembled, so a target on the wrong net is
invisible until 9 A of pack current is on the wrong conductor.

The two proofs the standard asks for: an acceptable input whose verdict must be PASS (the boards in this
tree), and a defective one whose verdict must be FAIL (the same block with one target's net changed). Both
need KiCad, so both skip where pcbnew is not importable and run where the boards are.
"""
import os, sys, shutil, tempfile, subprocess, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip, need

ECAD = os.path.dirname(TOOLS)
E5 = os.path.join(ECAD, "pcb-e5-block", "pcb-e5-block.kicad_pcb")


def _run(board, out_dir, a=None):
    env = dict(os.environ, VERDICT_DIR=out_dir)
    args = [sys.executable, os.path.join(TOOLS, "block_contract.py"), board] + ([a] if a else [])
    p = subprocess.run(args, capture_output=True, text=True, env=env, cwd=ECAD)
    f = os.path.join(out_dir, "check_contracts_e5.verdict.json")
    rec = json.load(open(f)) if os.path.exists(f) else {}
    return p, rec


def _need_kicad():
    try: import pcbnew  # noqa: F401
    except Exception as e: raise Skip("no pcbnew here (%s)" % type(e).__name__)
    need(E5, "board E5 is not in this tree")


def t_the_block_as_built_passes_against_the_board_a_this_tree_holds():
    _need_kicad()
    d = tempfile.mkdtemp(prefix="block-ok-")
    p, rec = _run(E5, d)
    assert rec.get("verdict") == "PASS", ((p.stdout + p.stderr)[-600:], rec.get("counts"))
    assert (rec.get("counts") or {}).get("pass", 0) >= 20, rec


def t_a_target_on_the_wrong_net_is_refused():
    """The defective fixture: one signal target's net renamed in a copy of the block. Nothing about board A
    changes, so the only thing that can refuse it is the comparison itself."""
    _need_kicad()
    d = tempfile.mkdtemp(prefix="block-bad-")
    bad = os.path.join(d, "pcb-e5-block.kicad_pcb")
    txt = open(E5, encoding="utf-8", errors="replace").read()
    import re
    m = re.search(r'"(\w[\w+]*_P\d+)"', txt)
    assert m, "the block carries no <net>_P<pin> target net to damage"
    net = m.group(1)
    open(bad, "w", encoding="utf-8").write(txt.replace('"%s"' % net, '"WRONG_P99"'))
    p, rec = _run(bad, d, os.path.join(ECAD, "pcb-a-power-a23", "pcb-a-power.kicad_pcb"))
    assert rec.get("verdict") == "FAIL", \
        "a target carrying another net was accepted: %s\n%s" % (rec.get("counts"), (p.stdout + p.stderr)[-400:])
    assert any("WRONG_P99" in str(e) for e in (rec.get("evidence") or [])), rec.get("evidence")


def t_it_says_which_board_a_it_compared_against():
    """Board A is regenerated constantly and the block is generated from one of its phases. A verdict that does
    not name the board it compared against cannot be read a day later."""
    _need_kicad()
    d = tempfile.mkdtemp(prefix="block-inputs-")
    _p, rec = _run(E5, d)
    assert (rec.get("inputs") or {}).get("board_a"), rec.get("inputs")


def t_the_contract_check_no_longer_writes_this_board_s_verdict():
    """Two tools writing one verdict name is how a reading gets overwritten by a weaker one."""
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    i = src.index("for _bd in sorted(set(list(per_board)")
    assert 'if _bd == "E5": continue' in src[i:i + 400], \
        "check_contracts still writes board E5's verdict, which block_contract.py now decides"
    assert "check_contracts_e5" not in src[i:], "check_contracts still names board E5's verdict"
