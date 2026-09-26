#!/usr/bin/env python3
"""SCH-002's blind half: the board's parts against the netlist's, value and footprint per reference
(MESHSAT-1357, 26 September 2026).

`netlist_board.py` compares references, pad nets and net names (its docstring's "Three comparisons" and `_main`). It never
compares what a reference IS, so a board placed from an older schematic passes it whenever the change was a value
or a land. The box readings of 25 September 2026 (W7-R2-02, commit 82dd1e4d, KiCad 9.0.9) found exactly that on
three of the six boards, and these fixtures carry those parts with their real texts:

  A32  C11 and C12 read 10u 100V in the netlist and 10u 50V on the board; D2, the VIN_RAW entry clamp, reads
       SMCJ40A in the netlist and SMCJ33A on the board (the difference decision 31's criterion C-A31 fails on);
  B21  U10's value text differs, and U42, U52 and U62 carry the through-hole SWD header on the board where the
       netlist carries the SMD land (W7-R2-01: the adoption commit f2541bea changed the generator and committed
       the board in the same commit);
  D12  C26 and C27 read 27p in the netlist and 18p on the board, R11 1.0k against 1.5k, and Y1 and Y2 are
       HC-49S-SMD crystals in the netlist and 3225 crystals on the board.

Boards C24 and P4 had none, which is the acceptable shape. The fixtures are synthetic files carrying those parts;
nothing here reads or judges the real tree.
"""
import os, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip


def _q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _netlist(parts):
    """A KiCad 9 export ("E") with a components section: parts = [(ref, value, 'Lib:Footprint')]."""
    L = ['(export (version "E")', '  (design', '    (source "/x/b.kicad_sch")', '    (date "2026-09-25T00:00:00+0000")',
         '    (tool "Eeschema 9.0.9"))', '  (components']
    for ref, val, fp in parts:
        L += ['    (comp (ref %s)' % _q(ref), '      (value %s)' % _q(val), '      (footprint %s)' % _q(fp),
              '      (fields', '        (field (name "Footprint") %s))' % _q(fp),
              '      (libsource (lib "Device") (part "X") (description "x"))',
              '      (tstamps "00000000-0000-0000-0000-000000000000"))']
    L += ['  )', '  (nets', '    (net (code "1") (name "GND")', '      (node (ref "X1") (pin "1")))', '  )', ')']
    return "\n".join(L) + "\n"


def _board(parts):
    """A KiCad 9 board: parts = [(ref, value, 'Footprint')], written the way gen_pcb writes them (no library
    nickname on the footprint id), with a nested (property "Value" ...) that carries its own sub-nodes."""
    L = ['(kicad_pcb', '\t(version 20241229)', '\t(generator "pcbnew")', '\t(general', '\t\t(thickness 1.6)', '\t)',
         '\t(net 0 "")', '\t(gr_text "B21" (at 1 1) (layer "F.SilkS"))']
    for ref, val, fp in parts:
        L += ['\t(footprint %s' % _q(fp), '\t\t(layer "F.Cu")', '\t\t(uuid "0045648b-8011-4180-92ec-78b2ea2b0271")',
              '\t\t(at 131.6 79.4)', '\t\t(property "Reference" %s' % _q(ref), '\t\t\t(at 0 -1.43 0)',
              '\t\t\t(layer "F.SilkS")', '\t\t\t(effects (font (size 0.8 0.8) (thickness 0.12)))', '\t\t)',
              '\t\t(property "Value" %s' % _q(val), '\t\t\t(at 0 1.43 0)', '\t\t\t(layer "F.Fab")', '\t\t)',
              '\t\t(pad "1" smd roundrect (at -0.79 0) (size 0.8 0.95) (layers "F.Cu") (net 0 ""))',
              '\t)']
    L += [')']
    return "\n".join(L) + "\n"


# The real parts of the three boards whose values or lands differ (W7 box readings, 25 September 2026).
A32_NET = [("C11", "10u 100V X7R 1210", "Capacitor_SMD:C_1210_3225Metric"),
           ("C12", "10u 100V X7R 1210", "Capacitor_SMD:C_1210_3225Metric"),
           ("D2", "SMCJ40A (VIN_RAW clamp behind E6's filter: 40 V standoff on a line specified to 36)", "Diode_SMD:D_SMC"),
           ("R1", "10k", "Resistor_SMD:R_0603_1608Metric")]
A32_PCB = [("C11", "10u 50V X7R 1210", "C_1210_3225Metric"), ("C12", "10u 50V X7R 1210", "C_1210_3225Metric"),
           ("D2", "SMCJ33A (VIN_RAW clamp behind E6's filter)", "D_SMC"), ("R1", "10k", "R_0603_1608Metric")]
B21_NET = [("U10", "TMP117AIDRVR board temperature under the coolers (I2C 0x49; WSON-6: 1 SCL 2 GND 3 ALERT 4 V+ 5 ADD0 6 SDA 7 thermal pad)", "Package_SON:WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm")] + \
          [(u, "SWD header", "Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical_SMD_Pin1Left") for u in ("U42", "U52", "U62")]
B21_PCB = [("U10", "TMP117AIDRVR board temperature under the coolers (I2C 0x49)", "WSON-6-1EP_2x2mm_P0.65mm_EP1x1.6mm")] + \
          [(u, "SWD header", "PinHeader_1x05_P2.54mm_Vertical") for u in ("U42", "U52", "U62")]
D12_NET = [("C26", "27p NP0", "Capacitor_SMD:C_0603_1608Metric"), ("C27", "27p NP0", "Capacitor_SMD:C_0603_1608Metric"),
           ("R11", "1.0k", "Resistor_SMD:R_0603_1608Metric"),
           ("Y1", "6 MHz HC-49S-SMD passive (CL 20 pF, 80 Ohm; C1 = C2 = 27 pF and Rd 1.0k, SLLS413 figure 6 re-chosen for this part's ESR)", "Crystal:Crystal_SMD_HC49-SD"),
           ("Y2", "6 MHz HC-49S-SMD passive (codec clock, CL 20 pF; C1 = C2 = 27 pF)", "Crystal:Crystal_SMD_HC49-SD")]
D12_PCB = [("C26", "18p NP0", "C_0603_1608Metric"), ("C27", "18p NP0", "C_0603_1608Metric"), ("R11", "1.5k", "R_0603_1608Metric"),
           ("Y1", "6 MHz 3225 (CL 20 pF; C1 = C2 = 27 pF and Rd 1.5k per SLLS413 figure 6)", "Crystal_SMD_3225-4Pin_3.2x2.5mm"),
           ("Y2", "6 MHz 3225 (codec clock; 18 pF loads, to confirm on the EVM sheet)", "Crystal_SMD_3225-4Pin_3.2x2.5mm")]


def _files(net_parts, pcb_parts, net_txt=None):
    d = tempfile.mkdtemp(prefix="np-")
    n = os.path.join(d, "b.net"); open(n, "w").write(net_txt if net_txt is not None else _netlist(net_parts))
    b = os.path.join(d, "b.kicad_pcb"); open(b, "w").write(_board(pcb_parts))
    return d, b, n


def _gate(board, net, cwd, extra=()):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_parts.py"), board, net] + list(extra),
                       capture_output=True, text=True, timeout=120, cwd=cwd)
    v = os.path.join(cwd, "out", "netlist_parts.verdict.json")
    return r.returncode, r.stdout + r.stderr, (json.load(open(v)) if os.path.exists(v) else None)


def t_the_netlist_and_the_board_are_parsed_to_value_and_footprint_per_reference():
    import netlist_parts as NP
    d, b, n = _files(A32_NET, A32_PCB)
    comps = NP.read_components(n); fps = NP.read_footprints(b)
    assert comps["D2"]["value"].startswith("SMCJ40A") and comps["D2"]["footprint"] == "Diode_SMD:D_SMC", comps["D2"]
    assert fps["D2"]["value"].startswith("SMCJ33A") and fps["D2"]["footprint"] == "D_SMC", fps["D2"]
    assert set(comps) == set(fps) == {"C11", "C12", "D2", "R1"}, (sorted(comps), sorted(fps))
    # a quote inside a value survives both escapings
    d2, b2, n2 = _files([("U1", 'the "E6" filter', "Lib:X")], [("U1", 'the "E6" filter', "X")])
    assert NP.read_components(n2)["U1"]["value"] == 'the "E6" filter' == NP.read_footprints(b2)["U1"]["value"]


def t_board_a32_s_entry_clamp_and_capacitors_fail_on_value():
    """DEFECTIVE: the three VIN_RAW parts of A32 (C11, C12, D2)."""
    d, b, n = _files(A32_NET, A32_PCB)
    rc, out, v = _gate(b, n, d)
    assert rc == 1 and v and v["verdict"] == "FAIL", (rc, out)
    assert v["counts"]["value_differs"] == 3 and v["counts"]["footprint_differs"] == 0, v["counts"]
    ev = " | ".join(v["evidence"])
    for ref in ("C11", "C12", "D2"): assert ref + " value" in ev, ev
    assert "SMCJ40A" in ev and "SMCJ33A" in ev, ev
    assert v["denominator"] == 8, v["denominator"]          # value and footprint of four shared references


def t_board_b21_s_swd_land_fails_on_footprint():
    """DEFECTIVE: the THT header on the board where the netlist carries the SMD land (W7-R2-01)."""
    d, b, n = _files(B21_NET, B21_PCB)
    rc, out, v = _gate(b, n, d)
    assert rc == 1 and v["verdict"] == "FAIL", (rc, out)
    assert v["counts"]["footprint_differs"] == 3 and v["counts"]["value_differs"] == 1, v["counts"]
    assert any("U42 footprint" in e and "Vertical_SMD_Pin1Left" in e for e in v["evidence"]), v["evidence"]


def t_board_d12_s_crystals_and_their_loads_fail_on_value_and_footprint():
    d, b, n = _files(D12_NET, D12_PCB)
    rc, out, v = _gate(b, n, d)
    assert rc == 1 and v["verdict"] == "FAIL", (rc, out)
    assert v["counts"]["value_differs"] == 5 and v["counts"]["footprint_differs"] == 2, v["counts"]


def t_a_board_that_is_its_netlist_passes_and_the_library_nickname_is_not_a_difference():
    """ACCEPTABLE (the C24 and P4 shape): the board file carries the bare footprint name, gen_pcb's habit, and the
    netlist the library-qualified one; that is the same land."""
    same = [(r, v, f.split(":")[-1]) for r, v, f in A32_NET]
    d, b, n = _files(A32_NET, same)
    rc, out, v = _gate(b, n, d)
    assert rc == 0 and v["verdict"] == "PASS" and v["denominator"] == 8, (rc, out, v and v["counts"])


def t_nothing_to_compare_is_inconclusive_and_never_a_pass():
    d = tempfile.mkdtemp(prefix="np-none-")
    rc, out, v = _gate(os.path.join(d, "b.kicad_pcb"), os.path.join(d, "b.net"), d)
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE" and v.get("missing_input"), (rc, out, v)
    # a netlist with nets and no component records (the shape of netlist_board's own fixtures)
    d, b, n = _files([], A32_PCB, net_txt='(export (version "E")\n  (nets\n    (net (code "1") (name "/X")\n'
                                           '      (node (ref "U1") (pin "1"))\n    )\n  )\n)\n')
    rc, out, v = _gate(b, n, d)
    assert rc == 3 and v["verdict"] == "INCONCLUSIVE", (rc, out, v)


def t_the_gate_writes_where_it_is_told():
    d, b, n = _files(A32_NET, A32_PCB)
    o = os.path.join(d, "elsewhere")
    rc, out, _v = _gate(b, n, d, ["--out-dir", o])
    assert rc == 1 and os.path.exists(os.path.join(o, "netlist_parts.verdict.json")), (rc, out)
    assert not os.path.exists(os.path.join(d, "out", "netlist_parts.verdict.json")), "it also wrote the default place"


def t_every_sch002_run_site_writes_the_companion_verdict():
    """netlist_board.py runs in full.sh, finish.sh and gate_sweep.sh. It writes the companion's verdict from the
    same run, so no run site can leave SCH-002 with one half, and the companion cannot change netlist_board's own
    verdict or exit code (a stub pcbnew stands in for KiCad here, as in test_netlist_board)."""
    d, b, n = _files(A32_NET, A32_PCB)
    stub = tempfile.mkdtemp(prefix="np-stub-")
    # every reference is on the stub board and the one netlist node (X1.1 on GND) is carried by its pad, so
    # netlist_board's three comparisons all agree: this is the board SCH-002 used to pass
    open(os.path.join(stub, "pcbnew.py"), "w").write(
        "class _P:\n    def GetNumber(s): return '1'\n    def GetNetname(s): return 'GND'\n"
        "class _F:\n    def __init__(s, r): s.r = r\n    def GetReference(s): return s.r\n"
        "    def GetFPIDAsString(s): return 'X:Y'\n    def Pads(s): return [_P()] if s.r == 'X1' else []\n"
        "class _B:\n    def GetFootprints(s): return [_F(r) for r in ('C11', 'C12', 'D2', 'R1', 'X1')]\n"
        "def LoadBoard(p): return _B()\n")
    d, b, n = _files(A32_NET + [("X1", "strap", "Lib:X")], A32_PCB + [("X1", "strap", "X")])
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "netlist_board.py"), b, n], capture_output=True, text=True,
                       timeout=120, cwd=d, env=dict(os.environ, PYTHONPATH=stub))
    nb = json.load(open(os.path.join(d, "out", "netlist_board.verdict.json")))
    assert nb["verdict"] == "PASS", "the fixture meant to show SCH-002's blind half failed netlist_board itself: %s" % nb
    npv = json.load(open(os.path.join(d, "out", "netlist_parts.verdict.json")))
    assert npv["verdict"] == "FAIL" and npv["counts"]["value_differs"] == 3, npv
    assert r.returncode == {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 3}[nb["verdict"]], \
        "netlist_board's exit code is no longer its own verdict's: %s against %s" % (r.returncode, nb["verdict"])
    # full.sh and finish.sh print the tail of this log beside netlist_board's exit code: its last line must be
    # netlist_board's own reading, not the companion's
    last = [x for x in r.stdout.splitlines() if x.strip()][-1]
    assert last.startswith("netlist_board: PASS (this gate") and "netlist_parts: FAIL" in last, last


def t_rule_sch002_reads_the_worst_of_both_halves():
    """DEFECTIVE before 26 September 2026: the coverage map named only netlist_board, so a board whose pad nets all
    agree and whose D2 is the wrong clamp read PASS on SCH-002. ACCEPTABLE after: the rule reads both verdicts and
    the worst decides, which is how rules_status already treats a rule verified by two tools."""
    import rules_status as S, rules_lib as R, verdict as V
    reg = R.load(); rule = next(r for r in reg["rules"] if r["id"] == "SCH-002")
    cov = S.coverage(); m = S.manifest(); fp = R.fingerprint(reg)
    ts = V.now()
    rec = lambda res: {"ts": ts, "verdict": res, "denominator": 8, "counts": {}, "policy": {"rule_set_fingerprint": fp}}
    vs = {"netlist_board": rec("PASS"), "netlist_parts": rec("FAIL")}
    r = S.result_for(rule, "c", cov, vs, m, fp)
    assert r["result"] == S.FAIL, "SCH-002 read %s on a board whose values differ from its netlist (%s)" % (r["result"], r["why"])
    vs_ok = {"netlist_board": rec("PASS"), "netlist_parts": rec("PASS")}
    assert S.result_for(rule, "c", cov, vs_ok, m, fp)["result"] == S.PASS
    only_half = {"netlist_board": rec("PASS")}
    assert S.result_for(rule, "c", cov, only_half, m, fp)["result"] == S.INCONCLUSIVE, "half a reading passed"


def t_the_sweep_clears_the_companion_with_netlist_board():
    """DEFECTIVE before 26 September 2026: gate_sweep.sh removes the verdicts of the gates it is about to run, so a
    gate that cannot run this time leaves no reading rather than the previous one. netlist_parts was not on that
    list, so a sweep whose netlist could not be rebuilt left netlist_board absent (INCONCLUSIVE) and the previous
    sweep's netlist_parts standing beside it. The list is read as the shell reads it: the words of the `for _g in`
    loop that ends in the `rm -f` of `<phase>/routed/<gate>.verdict.json`."""
    import re, shlex
    src = open(os.path.join(TOOLS, "gate_sweep.sh"), encoding="utf-8").read()
    m = re.search(r"^for _g in (.*?); do\s*\n\s*rm -f \"\$P/routed/\$_g\.verdict\.json\"", src, re.S | re.M)
    assert m, "gate_sweep.sh has no clear loop of the shape this test reads"
    words = shlex.split(m.group(1).replace("\\\n", " "), comments=False)
    assert "netlist_board" in words, "the sweep no longer clears netlist_board, so this test's premise moved"
    assert "netlist_parts" in words, "the sweep clears netlist_board and leaves its companion's old verdict standing"
