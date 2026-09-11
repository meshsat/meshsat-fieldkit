#!/usr/bin/env python3
"""The board against the schematic it was placed from (round-two M4).

Nothing compared the two. check_contracts reads netlists and never the board; verify_deliverable reads the
deliverable's files and never their contents against each other; the golden test compares a schematic with
itself. So a board placed from a STALE netlist passed every gate, and the chain has produced exactly that
twice: once when a generator died mid-line and the next stage rebuilt from the previous schematic, and once
when build_sch.sh's exit code was an echo nobody read.

The netlist half is pure text and runs anywhere; the board half needs pcbnew and skips without it.
"""
import os, sys, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip
import netlist_board as nb

NET = '''(export (version "E")
  (nets
    (net (code "1") (name "/USB_P")
      (node (ref "U1") (pin "1"))
      (node (ref "R1") (pin "2"))
    )
    (net (code "2") (name "GND")
      (node (ref "U1") (pin "2"))
    )
  )
)
'''


def _net(txt=NET):
    d = tempfile.mkdtemp(prefix="nb-"); p = os.path.join(d, "b.net"); open(p, "w").write(txt); return p


def t_the_netlist_parses_to_reference_pin_net():
    got = nb.read_netlist(_net())
    assert got == {"U1": {"1": "USB_P", "2": "GND"}, "R1": {"2": "USB_P"}}, got


def t_the_root_sheet_slash_is_stripped_once():
    """Board net names of root-sheet labels carry a leading slash and the netlist's do too; comparing one
    stripped against one unstripped is a mismatch on every net, which is a gate that cries wolf."""
    got = nb.read_netlist(_net())
    assert all(not n.startswith("/") for pins in got.values() for n in pins.values()), got


def t_a_missing_netlist_is_inconclusive_not_a_match():
    d = tempfile.mkdtemp(prefix="nb2-")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_board.py"), os.path.join(d, "b.kicad_pcb")],
                       capture_output=True, text=True, timeout=60, cwd=d)
    assert r.returncode == 3, (r.returncode, r.stdout)
    assert "compared with nothing" in r.stdout, r.stdout


def t_an_empty_netlist_is_inconclusive():
    p = _net('(export (version "E")\n  (nets\n  )\n)\n')
    d = os.path.dirname(p)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_board.py"), os.path.join(d, "b.kicad_pcb"), p],
                       capture_output=True, text=True, timeout=60, cwd=d)
    assert r.returncode == 3, (r.returncode, r.stdout)
    assert "no nodes" in r.stdout, r.stdout


def t_bench_prefixes_are_declared_not_guessed():
    assert "TP" in nb.BENCH and "H" in nb.BENCH and "JP" in nb.BENCH, nb.BENCH
    assert "U" not in nb.BENCH and "R" not in nb.BENCH, "a real component prefix must never be exempt"


def t_a_stale_netlist_is_caught_on_a_real_board():
    """The defect this exists for: the board carries one net and the netlist says another."""
    try: import pcbnew
    except Exception as e: raise Skip("no pcbnew here (%s)" % type(e).__name__)
    d = tempfile.mkdtemp(prefix="nb3-")
    b = pcbnew.BOARD()
    fp = pcbnew.FOOTPRINT(b); fp.SetReference("U1"); b.Add(fp)
    board = os.path.join(d, "b.kicad_pcb"); pcbnew.SaveBoard(board, b)
    p = _net()
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_board.py"), board, p],
                       capture_output=True, text=True, timeout=120, cwd=d)
    assert r.returncode == 1, (r.returncode, r.stdout)
    assert "R1 is in the netlist and not on the board" in r.stdout, r.stdout
