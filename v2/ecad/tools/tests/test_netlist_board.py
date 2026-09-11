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


# ---------------------------------------------------------------- the unconnected-pin placeholder (11 September 2026)
# KiCad gives every unconnected pin a synthetic net, `unconnected-(REF-PINNAME-PadN)`, and writes it into the
# netlist as though it were a net. It is not one: that pad carries no net on the board, and the two agreeing is
# what a correct board looks like. Comparing the placeholder against "no net" called 1,007 of B19's 6,716
# comparisons a failure and blocked a board whose every other gate passed, the first time this gate ran in a
# chain. These drive the real main() with a stub pcbnew, so they exercise the comparison rather than a copy.

UNCONN = '''(export (version "E")
  (nets
    (net (code "1") (name "/USB_P")
      (node (ref "U1") (pin "1"))
    )
    (net (code "2") (name "unconnected-(U1-COEX3-Pad44)")
      (node (ref "U1") (pin "44"))
    )
  )
)
'''


def _stub_board(pads, extra_fps=(), fpid="Package:Generic"):
    """A stub pcbnew whose board has U1 with `pads` = {pin: netname} plus any extra references."""
    d = tempfile.mkdtemp(prefix="nb-stub-")
    src = ['class _P:',
           '    def __init__(s, n, net): s.n, s.net = n, net',
           '    def GetNumber(s): return s.n',
           '    def GetNetname(s): return s.net',
           'class _F:',
           '    def __init__(s, r, pads): s.r, s.p = r, [_P(k, v) for k, v in pads.items()]',
           '    def GetReference(s): return s.r',
           '    def GetFPIDAsString(s): return %r' % fpid,
           '    def Pads(s): return s.p',
           'class _B:',
           '    def GetFootprints(s): return [_F("U1", %r)] + [_F(r, p) for r, p in %r]' % (pads, list(extra_fps)),
           'def LoadBoard(p): return _B()']
    open(os.path.join(d, "pcbnew.py"), "w").write("\n".join(src) + "\n")
    return d


def _run(netlist_txt, pads, extra_fps=(), fpid="Package:Generic"):
    np_ = _net(netlist_txt)
    stub = _stub_board(pads, extra_fps, fpid)
    board = os.path.join(os.path.dirname(np_), "b.kicad_pcb"); open(board, "w").write("(kicad_pcb)\n")
    env = dict(os.environ, PYTHONPATH=stub)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_board.py"), board, np_],
                       capture_output=True, text=True, env=env, cwd=os.path.dirname(np_))
    return r.returncode, r.stdout + r.stderr


def t_an_unconnected_pin_with_no_net_on_the_board_agrees():
    rc, out = _run(UNCONN, {"1": "/USB_P", "44": ""})
    assert rc == 0, out
    assert "2 of 2 comparisons agree" in out or "comparisons agree" in out, out
    assert "has no net on the board" not in out, out


def t_an_unconnected_pin_that_carries_a_net_on_the_board_fails():
    """The other direction is a real defect: the board is wired to something the schematic says is unconnected."""
    rc, out = _run(UNCONN, {"1": "/USB_P", "44": "/SPARE"})
    assert rc == 1, out
    assert "U1.44 carries SPARE on the board and is unconnected in the netlist" in out, out


def t_a_board_only_footprint_with_no_net_is_reported_and_does_not_block():
    rc, out = _run(UNCONN, {"1": "/USB_P", "44": ""}, extra_fps=[("U36", {"1": ""})])
    assert rc == 0, out
    assert "carry no net at all: U36" in out, out


def t_a_board_only_footprint_that_carries_a_net_blocks():
    rc, out = _run(UNCONN, {"1": "/USB_P", "44": ""}, extra_fps=[("U36", {"1": "/+3V3"})])
    assert rc == 1, out
    assert "U36 is on the board and not in the netlist, and its pads carry +3V3" in out, out


# ---------------------------------------------------------------- declared pad aliases (11 September 2026)
# KicAD's TDSON-8-1 brings a FET's drain out as one slug numbered 5 while the eight-pin symbol has drain on
# pins 5 to 8, so board E carried eighteen netlist nodes with nowhere to land and this gate refused it. They
# are DECLARED in tools/pad-aliases.txt rather than skipped: the aliased pad is still checked for the net, so
# a pin map naming a pad the footprint has not got keeps failing (the TPS2065CDBV trap of section 8).

TDSON = '''(export (version "E")
  (nets
    (net (code "1") (name "/DC_P")
      (node (ref "U1") (pin "5"))
      (node (ref "U1") (pin "6"))
      (node (ref "U1") (pin "7"))
      (node (ref "U1") (pin "8"))
    )
  )
)
'''


def t_a_declared_alias_moves_the_check_to_the_slug_pad():
    rc, out = _run(TDSON, {"5": "/DC_P"}, fpid="Package_TO_SOT_SMD:TDSON-8-1")
    assert rc == 0, out
    assert "3 pin(s) checked through a declared pad alias" in out, out


def t_a_declared_alias_still_fails_when_the_slug_carries_the_wrong_net():
    """The alias moves the check, it does not drop it."""
    rc, out = _run(TDSON, {"5": "/GND"}, fpid="Package_TO_SOT_SMD:TDSON-8-1")
    assert rc == 1, out
    assert "GND on the board and DC_P in the netlist" in out, out


def t_an_undeclared_missing_pad_still_fails():
    """The TPS2065CDBV class: a pin map that names a pad the footprint has not got."""
    rc, out = _run(TDSON, {"5": "/DC_P"}, fpid="Package_TO_SOT_SMD:SOT-23-6")
    assert rc == 1, out
    assert "U1.6 is on net DC_P in the netlist and has no net on the board" in out, out


def t_the_alias_file_gives_every_line_a_reason():
    import netlist_board as _nb
    p = os.path.join(TOOLS, "pad-aliases.txt")
    for ln in open(p):
        body = ln.split("#")[0].strip()
        if not body: continue
        assert "#" in ln, "an alias without a written reason waves a pad through silently: %r" % ln.strip()
        assert len(body.split()) == 3, ln
