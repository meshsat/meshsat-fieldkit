"""A cross-board contract says which boards it is about, and its verdict lands on those boards
(MESHSAT-862, 16 September 2026).

Board B was missing six PCIe coupling capacitors that the compute module's own datasheet requires. The
contract that found them is board B's, and `check_contracts` writes ONE verdict that every board reads as
evidence, so boards A, C, D, E, E5 and P all reported a failed rule for a defect on a board they do not
touch: four of the set's forty-five failing rule-board pairs were somebody else's.

Each contract now declares its boards and a per-board verdict is written beside the set's own, the pattern
`final_gate_<letter>` already uses. The declaration is explicit rather than read out of the sentence: the
first version inferred it, and it lost board A on two contracts within nine tries, because the English
article "A" has to be stripped before any such inference works at all.
"""
import os, re, sys, json, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
SRC = os.path.join(TOOLS, "check_contracts.py")


def t_every_contract_declares_the_boards_it_is_about():
    """Read statically: no call to check() may leave `boards` to a default, because there is no honest
    default. A contract with no board cannot be attributed and would silently land on none."""
    s = open(SRC, errors="replace").read()
    bad = []
    for m in re.finditer(r"^(?!def )\s*(?:\w+\s*=\s*)?check\(", s, re.M):
        # take the call's text up to the line that closes it
        rest = s[m.start():]
        depth = 0; end = 0
        for i, ch in enumerate(rest):
            if ch == "(": depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0: end = i; break
        call = rest[:end + 1]
        if "boards=" not in call:
            bad.append(call.replace("\n", " ")[:90])
    assert not bad, "contract(s) that do not declare their boards: %s" % bad


def t_a_contract_with_no_board_is_refused_rather_than_attributed_to_none():
    """Executed. The guard is in check() itself, so a contract added without boards fails loudly the first
    time it runs rather than quietly counting for no board."""
    ns = {}
    src = open(SRC, errors="replace").read()
    body = src[src.index("fails = []; checked = []"):src.index("def pinmap(")]
    import collections
    exec("import collections\nMISSING = []\n" + body, ns)   # no board is absent in these fixtures
    ns["check"](True, "B: something", boards={"B"})
    assert ns["per_board"]["B"]["pass"] == 1
    ns["check"](False, "A and B disagree", boards={"A", "B"})
    assert ns["per_board"]["A"]["fail"] and ns["per_board"]["B"]["fail"]
    try:
        ns["check"](True, "a contract with no board")
    except AssertionError as e:
        assert "declares no board" in str(e), e
    else:
        raise AssertionError("a contract with no board was accepted")


def t_a_failure_on_one_board_does_not_fail_another():
    """The property the whole change exists for, on the shape that caused it: board B's own contract fails
    and board A's verdict is unaffected."""
    ns = {}
    src = open(SRC, errors="replace").read()
    body = src[src.index("fails = []; checked = []"):src.index("def pinmap(")]
    exec("import collections\nMISSING = []\n" + body, ns)   # no board is absent in these fixtures
    ns["check"](True, "A: the pre-charge pin lands on a cell node net", boards={"A"})
    ns["check"](False, "B: PCIE1_RX_P has exactly one series AC coupling capacitor", boards={"B"})
    assert ns["per_board"]["A"]["fail"] == [], ns["per_board"]["A"]
    assert len(ns["per_board"]["B"]["fail"]) == 1, ns["per_board"]["B"]


def t_the_registry_reads_the_per_board_verdict_for_the_cross_board_rules():
    import rules_status as S
    cov = S.coverage()
    for rid in ("SCH-003", "RF-002"):
        v = (cov[rid].get("verification") or {}).get("verdict")
        assert v == "check_contracts_<letter>", "%s still reads the set verdict: %r" % (rid, v)


# ---------------------------------------------------------------------------------------------------------
# A CONTRACT THAT NAMES AN ABSENT BOARD IS UNJUDGED, NOT FAILED (17 September 2026).
#
# A contract is an agreement between two boards' netlists. With one of them missing from the tree the
# comparison was never made: its pin map reads as empty and every pin "disagrees". The per-board guard covered
# the board that is ABSENT and not the board at the other end, so a run on the runner, where no chain has
# written a netlist, put board B's absence on board C's page as two failed contracts and on board A's as
# twelve, over readings taken on the box WITH those netlists.

def t_a_contract_whose_other_board_is_absent_is_not_this_board_s_failure():
    import re, os
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    assert "_absent = [b for b in boards if b in MISSING]" in src, "the absent end is not detected"
    assert 'per_board[_b]["unjudged"].append(text)' in src, "an unjudged contract is not recorded as such"
    # and it must not also be counted as a failure
    i = src.index("_absent = [b for b in boards if b in MISSING]")
    j = src.index("print((\"PASS  \" if ok else \"FAIL  \")")
    assert "fails.append" not in src[i:j], "an unjudged contract still reaches the failure list"


def t_the_guard_covers_both_ends():
    import os
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    assert 'if (_bd in MISSING or _u) and _richer_on_disk(' in src, \
        "the per-board guard fires only when the board's OWN netlist is absent"


def t_a_board_with_unjudged_contracts_is_inconclusive_and_never_passing():
    """Absence is never a pass here either: a board whose contracts could not all be judged says so."""
    import os
    src = open(os.path.join(TOOLS, "check_contracts.py"), encoding="utf-8").read()
    assert "_v.INCONCLUSIVE if (not _n or _bd in MISSING or _u)" in src, src[src.index("_v.write(\"check_contracts_%s"):][:300]


def t_an_absent_board_makes_both_ends_unjudged_and_neither_failed():
    """Executed, on the exact shape that caused it: board B is absent, and the contract between B and C is
    counted against neither."""
    ns = {}
    src = open(SRC, errors="replace").read()
    body = src[src.index("fails = []; checked = []"):src.index("def pinmap(")]
    exec("import collections\nMISSING = ['B']\n" + body, ns)
    ns["check"](False, "panel controller USB pair USB_PNL_P on B and C J_PANEL", boards={"B", "C"})
    assert ns["per_board"]["C"]["fail"] == [], ns["per_board"]["C"]
    assert ns["per_board"]["B"]["fail"] == [], ns["per_board"]["B"]
    assert len(ns["per_board"]["C"]["unjudged"]) == 1, ns["per_board"]["C"]
    assert ns["fails"] == [] and ns["checked"] == [], (ns["fails"], ns["checked"])
    # a contract that names only present boards is judged exactly as before
    ns["check"](False, "C: something of C's own", boards={"C"})
    assert len(ns["per_board"]["C"]["fail"]) == 1 and len(ns["fails"]) == 1


def t_the_staleness_guard_reads_the_schematic_it_came_from_and_not_a_timestamp():
    """A NETLIST BELONGS TO THE SCHEMATIC WHOSE HASH ITS SIDECAR CARRIES (17 September 2026).

    Two failures of the timestamp version, both on the committed tree the same morning:

    - board B's schematic was rewritten with IDENTICAL content by a checkout, which made its mtime newer than
      the netlist, so the gate called the netlist stale and left every contract naming board B unjudged;
    - all six netlists had been regenerated and committed WITHOUT their schematics, so every one came from a
      schematic the tree does not hold, and five of the six passed the mtime test because their schematics
      happened to be older. One board refused and five passed in the identical state.

    `sch_prov.write` records the schematic's sha256 beside the netlist, so the fact is on disk and the mtime
    is only a proxy for it. Executed as the script runs, in a temporary ECAD directory holding one board:
    same content with a newer schematic must NOT be called stale, and a sidecar naming another schematic must
    be called stale however old that schematic is.
    """
    import shutil, time, hashlib
    d = tempfile.mkdtemp(prefix="stale-guard-")
    stem = "pcb-p-pack"                                   # a stem check_contracts knows, so the guard is reached
    try:
        proj = os.path.join(d, stem + "-t1"); os.makedirs(os.path.join(proj, "out"))
        sch = os.path.join(proj, stem + ".kicad_sch"); net = os.path.join(proj, "out", stem + ".net")
        open(sch, "w").write("(kicad_sch (version 20250114))\n")
        open(net, "w").write('(export (version "E")\n  (components\n    (comp (ref "R1")\n      (value "1k"))'
                             '\n  )\n  (nets\n    (net (code "1") (name "N1")\n      (node (ref "R1") (pin "1")))\n  )\n)\n')
        side = net + ".prov.json"
        sha = hashlib.sha256(open(sch, "rb").read()).hexdigest()[:32]

        def run():
            env = dict(os.environ, VERDICT_DIR=d)
            p = subprocess.run([sys.executable, SRC, d], capture_output=True, text=True, timeout=300, env=env)
            return p.stdout + p.stderr

        json.dump({"schematic_sha256": sha}, open(side, "w"))
        os.utime(sch, (time.time(), time.time()))          # the schematic is NEWER and its content is the same
        out = run()
        assert "STALE netlist for %s" % stem not in out, \
            ("a netlist whose sidecar names this exact schematic was called stale because the file's mtime is "
             "newer:\n%s" % "\n".join(l for l in out.splitlines() if "STALE" in l))

        json.dump({"schematic_sha256": "0" * 32}, open(side, "w"))
        os.utime(sch, (1, 1))                              # and now the schematic is OLD but is not the one
        out = run()
        assert "STALE netlist for %s" % stem in out, \
            "a netlist generated from a schematic this tree does not hold was accepted because its mtime is older"
    finally:
        shutil.rmtree(d, ignore_errors=True)
