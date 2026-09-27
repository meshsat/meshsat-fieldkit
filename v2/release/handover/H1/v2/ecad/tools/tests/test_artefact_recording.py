#!/usr/bin/env python3
"""Every writer of a schematic-phase rule records the artefact it judged (MESHSAT-1357, 26 September 2026, the tools
stream's recording round). v2/docs/CURRENT-EVIDENCE.md listed 31 rule-board rows whose first step was "<tool> taught
to record by sha the netlist (or, on E5, the board file) that ties its reading to this board": erc_gate recorded a
project directory, power_sequence a bare file name, energy_chain a chain's name, check_contracts the letters of the
boards it read, interfaces a sheet's name, pack_protection a path relative to the repository root, and safe_lines and
port_protect the letter alone on board E5.

Executed, never read from source. Each tool is RUN, on a fixture or on this tree with its verdicts written to a
temporary directory, and the verdict it writes is handed to `rules_status._bound` against a candidate carrying the
artefact's sha. Both ways for each tool: the reading the tool writes now binds; the form it wrote before does not.

  * erc_gate: the netlist is recorded only when the ERC report's sidecar names the schematic the netlist's own
    provenance names; `--run` writes that sidecar (a stand-in kicad-cli plays KiCad on a host without it), and a
    report with no sidecar, or one taken on another schematic, is recorded and stays unbound;
  * power_sequence, pack_protection, safe_lines and port_protect: the netlist by sha and by content, and the intent;
    on E5, safe_lines and port_protect --board record its declared phase's board file;
  * energy_chain: the DECLARED phase's netlist of every board a stage names, never the newest by mtime, and E5's
    board file for the dock block's stage;
  * check_contracts: each board's netlist the contracts of a board read, and nothing of E5, which it does not read;
  * interfaces: the netlist beside the declared phase's intent, or E5's board file;
  * rules_status.RECORDS_ARTEFACT, which lets the re-take projection see what these writers record, names exactly
    the writers and the kinds these fixtures prove, and the projection reads CURRENT for them and UNBOUND otherwise;
  * a reading that recorded ANOTHER board's netlist is current only while that netlist is the other board's own
    (OTHER_DESIGN), and a re-take projects it at that board's candidate;
  * phase_artefacts.phase_dir is rules_status._phase_dir for every board, and a record inside this repository is
    relative, so a checkout under /tmp is not read as a temporary directory.
"""
import os, sys, json, hashlib, tempfile, subprocess, shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ECAD = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)
from harness import Skip
import rules_status as S
import phase_artefacts as PA

RULE = {"id": "R-1", "domain": "SCHEMATIC", "short_name": "n", "release_effect": "BLOCKER",
        "verification_phase": "SCHEMATIC"}
EMPTY = {"invalidated": {}, "compatibility": [], "errors": []}
NOBOARDS = {"boards": {}}
# The kinds each writer's fixtures below prove it records; rules_status.RECORDS_ARTEFACT must say exactly this.
PROVED = {"erc_gate.py": {"netlist"}, "power_sequence.py": {"netlist"}, "energy_chain.py": {"netlist", "board_file"},
          "check_contracts.py": {"netlist"}, "interfaces.py": {"netlist", "board_file"},
          "pack_protection.py": {"netlist"}, "safe_lines.py": {"netlist", "board_file"},
          "port_protect.py": {"netlist", "board_file"}}


def _sha(path, n=16):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:n]


def _bind(rec, letter, net=None, boards=(), content=None, m=NOBOARDS):
    """(bound, cause) of one reading against a candidate carrying these shas."""
    cand = {"netlist_sha16": net, "netlist_content16": content, "board_shas": sorted(boards), "layout_current": False,
            "netlist_committed": None, "package": {}}
    b, cause, _why, _e = S._bound(RULE, letter, "gate", rec, cand, EMPTY, m)
    return b, cause


def _unbound(rec, letter, net=None, boards=()):
    b, cause = _bind(rec, letter, net, boards)
    assert not b and cause in ("UNBOUND", "PREDATES_ARTEFACT"), (b, cause, rec.get("inputs"))


def _netlist(path, comps, nets):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    c = "".join('    (comp (ref "%s") (value "%s"))\n' % (r, v) for r, v in sorted(comps.items()))
    n = ""
    for i, (name, nodes) in enumerate(sorted(nets.items()), 1):
        body = "".join('      (node (ref "%s") (pin "%s"))\n' % (r, p) for r, p in nodes)
        n += '    (net (code "%d") (name "/%s")\n%s    )\n' % (i, name, body)
    open(path, "w").write("(export (version \"E\")\n  (components\n%s  )\n  (nets\n%s  )\n)\n" % (c, n))
    return path


def _verdict(d, name):
    return json.load(open(os.path.join(d, "%s.verdict.json" % name)))


def _real(letter):
    """(netlist path, sha) of the declared phase's netlist in this tree, or Skip where the tree holds none."""
    p = PA.netlist(letter)
    if not p or not os.path.isfile(p): raise Skip("this tree holds no netlist for board %s" % letter)
    return p, _sha(p)


def _real_board(letter):
    p = PA.board_file(letter)
    if not p or not os.path.isfile(p): raise Skip("this tree holds no board file for board %s" % letter)
    return p, _sha(p)


# ---------------------------------------------------------------------------------------------------- erc_gate
def _erc_project(tied=True, sidecar=True):
    d = tempfile.mkdtemp(prefix="rec-erc-"); os.makedirs(os.path.join(d, "out"))
    sch = os.path.join(d, "b.kicad_sch"); open(sch, "w").write("(kicad_sch (version 20250114))\n")
    net = _netlist(os.path.join(d, "out", "b.net"), {"R1": "10k"}, {"N1": [("R1", "1")]})
    json.dump({"schematic_sha256": _sha(sch, 32) if tied else "0" * 32}, open(net + ".prov.json", "w"))
    rep = os.path.join(d, "out", "b-erc.json"); json.dump({"sheets": [{"violations": []}], "source": "b.kicad_sch"}, open(rep, "w"))
    if sidecar:
        json.dump({"report_sha256_16": _sha(rep), "schematic_sha256": _sha(sch, 32)}, open(rep + ".prov.json", "w"))
    return d, net


def _erc(d, *extra, env=None):
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "erc_gate.py"), d, "b"] + list(extra),
                       capture_output=True, text=True, timeout=120, env=env)
    return r.returncode, _verdict(os.path.join(d, "out"), "erc_gate"), r.stdout + r.stderr


def t_erc_gate_records_the_netlist_only_when_the_report_is_of_its_schematic():
    d, net = _erc_project()
    rc, rec, out = _erc(d)
    assert rc == 0 and rec["verdict"] == "PASS", out
    assert rec["inputs"]["netlist_tie"]["proved"] is True, rec["inputs"]
    assert rec["inputs"]["netlist"]["sha256_16"] == _sha(net), rec["inputs"]
    assert _bind(rec, "x", _sha(net)) == (True, "BOUND")
    # THE OLD FORM: the project directory alone binds nothing
    old = dict(rec, inputs={"board": "x", "project": {"path": ".", "sha256_16": None}})
    _unbound(old, "x", _sha(net))


def t_erc_gate_does_not_tie_a_report_of_unknown_or_other_origin():
    """Main's ERC reports on 26 September were written on 11 September, before the schematics committed that day: a
    report whose sidecar is absent, or names another schematic than the netlist's provenance, is recorded (so the reader
    can see what was judged) and the netlist is not."""
    for tied, sidecar, why in ((True, False, "no provenance sidecar"), (False, True, "exported from schematic")):
        d, net = _erc_project(tied=tied, sidecar=sidecar)
        rc, rec, out = _erc(d)
        assert rec["verdict"] == "PASS", out
        assert "netlist" not in rec["inputs"] and rec["inputs"]["netlist_tie"]["proved"] is False, rec["inputs"]
        assert why in rec["inputs"]["netlist_tie"]["why"], rec["inputs"]["netlist_tie"]
        assert rec["inputs"]["erc_report"]["sha256_16"], rec["inputs"]
        _unbound(rec, "x", _sha(net))


def _fake_kicad_cli(writes=True):
    b = tempfile.mkdtemp(prefix="rec-kicad-")
    p = os.path.join(b, "kicad-cli")
    open(p, "w").write("#!%s\nimport sys, json\na = sys.argv[1:]\nif a[:1] == ['version']:\n    print('9.0.9-fixture'); sys.exit(0)\n"
                       "if %s and a[:2] == ['sch', 'erc']:\n    out = a[a.index('-o') + 1]\n"
                       "    json.dump({'sheets': [{'violations': [{'type': 'lib_symbol_issues', 'severity': 'warning', "
                       "'description': 'w', 'items': []}]}], 'source': a[-1]}, open(out, 'w'))\nsys.exit(0)\n"
                       % (sys.executable, "True" if writes else "False"))
    os.chmod(p, 0o755)
    return dict(os.environ, PATH=b + os.pathsep + os.environ.get("PATH", ""))


def t_erc_gate_run_takes_the_report_on_the_schematic_and_ties_the_netlist():
    d, net = _erc_project(sidecar=False)
    rc, rec, out = _erc(d, "--run", env=_fake_kicad_cli())
    assert rc == 0 and rec["verdict"] == "PASS" and rec["counts"]["violations"] == 1, out
    side = json.load(open(os.path.join(d, "out", "b-erc.json.prov.json")))
    assert side["schematic_sha256"] == _sha(os.path.join(d, "b.kicad_sch"), 32), side
    assert rec["inputs"]["netlist"]["sha256_16"] == _sha(net), rec["inputs"]
    assert _bind(rec, "x", _sha(net)) == (True, "BOUND")


def t_erc_gate_run_that_takes_no_report_reads_no_old_one():
    """A --run that could not take the ERC must not fall back on whatever report was there before."""
    d, net = _erc_project()
    rc, rec, out = _erc(d, "--run", env=_fake_kicad_cli(writes=False))
    assert rc == 3 and rec["verdict"] == "INCONCLUSIVE", out
    assert not os.path.exists(os.path.join(d, "out", "b-erc.json")), "the old report survived a --run"
    assert "netlist" not in rec["inputs"], rec["inputs"]


# ---------------------------------------------------------------------------------------------------- power_sequence
def t_power_sequence_records_the_netlist_and_its_intent_by_content():
    d = tempfile.mkdtemp(prefix="rec-seq-")
    net = _netlist(os.path.join(d, "out", "b.net"), {"U1": "ldo"}, {"+3V3": [("U1", "2")], "GND": [("U1", "1")]})
    json.dump({"rails": {"+3V3": {"source": "U1", "always_on": True, "always_on_why": "fixture"}}},
              open(os.path.join(d, "out", "b-intent.json"), "w"))
    v = os.path.join(d, "v")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "power_sequence.py"), "out/b.net"], cwd=d,
                       capture_output=True, text=True, timeout=120, env=dict(os.environ, VERDICT_DIR=v))
    rec = _verdict(v, "power_sequence")
    assert rec["verdict"] == "PASS", r.stdout + r.stderr
    assert rec["inputs"]["netlist"]["sha256_16"] == _sha(net), rec["inputs"]
    assert rec["inputs"]["intent"]["sha256_16"] == _sha(os.path.join(d, "out", "b-intent.json")), rec["inputs"]
    assert _bind(rec, "x", _sha(net)) == (True, "BOUND")
    # a netlist regenerated with the same design binds by its content identity
    c = rec["inputs"]["netlist"].get("content16")
    assert c and _bind(rec, "x", "f" * 16, content=c) == (True, "BOUND"), rec["inputs"]
    # THE OLD FORM: a bare file name verdict.write could not hash
    _unbound(dict(rec, inputs={"board": "x", "netlist": "b.net"}), "x", _sha(net))


def t_power_sequence_reads_the_last_net_of_a_kicad_9_netlist():
    """R4T-F1: KiCad 9 closes the nets section on the last net's own line, so the old look-ahead lost that net."""
    import power_sequence as P
    d = tempfile.mkdtemp(prefix="rec-last-")
    p = os.path.join(d, "b.net")
    open(p, "w").write('(export (version "E")\n  (components\n    (comp (ref "U1") (value "x")))\n  (nets\n'
                       '    (net (code "1") (name "/A")\n      (node (ref "U1") (pin "1")))\n'
                       '    (net (code "2") (name "/ZZ_LAST")\n      (node (ref "U1") (pin "2") (pinfunction "EN")))))\n')
    by_net, _v = P.netlist(p)
    assert "ZZ_LAST" in by_net and by_net["ZZ_LAST"] == [("U1", "2", "EN")], by_net


# ---------------------------------------------------------------------------------------------------- energy_chain
CHAIN_P = """
schema_version: "1.0.0"
stages:
 - id: ONE
   board: P
   from: "the cells"
   to: "the fuse"
   continuous_a: 10.0
   peak_a: 18.0
   conductor: {what: "a band", rating_a: 30.0, basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   prospective_fault_a: {low: 100, high: 300, basis: "v2/vendor/battery/samsung-35e-orbtronic.pdf"}
   protection: {ref: F1, what: "25 A blade", rating_a: 25.0, interrupting_a: 1000.0, i2t_a2s: 1000.0,
                basis: "v2/vendor/battery/littelfuse-287-atof.pdf"}
   protects: null
"""


def t_energy_chain_reads_and_records_the_declared_netlist_not_the_newest():
    import energy_chain as E
    ecad = tempfile.mkdtemp(prefix="rec-chain-")
    if not PA.stem("p"): raise Skip("the manifest names no board p")
    # the phase directory this tree's profile names for board P, laid down in the fixture tree
    decl = os.path.join(ecad, os.path.basename(PA.phase_dir("p")), "out", PA.stem("p") + ".net")
    os.makedirs(os.path.dirname(decl), exist_ok=True)
    assert PA.netlist("p", ecad) == decl, (PA.netlist("p", ecad), decl)
    _netlist(decl, {"F1": "25 A blade"}, {"PACK_P": [("F1", "1")]})
    arm = os.path.join(ecad, PA.stem("p") + "-arm9", "out", PA.stem("p") + ".net")
    _netlist(arm, {"R1": "x"}, {"N": [("R1", "1")]})
    os.utime(arm, (os.path.getmtime(decl) + 100, os.path.getmtime(decl) + 100))   # the arm is the NEWEST
    ch = os.path.join(ecad, "chain.yaml"); open(ch, "w").write(CHAIN_P)
    r = E.check(ch, ecad)
    assert not [f for f in r["fails"] if "has no F1" in f], "the newest netlist was read, not the declared one: %s" % r["fails"]
    inp = E.recorded_inputs(r, ["ONE"], ch, ecad)
    assert inp["netlist_p"]["sha256_16"] == _sha(decl), inp
    rec = {"inputs": inp, "ts": "2026-09-26T12:00:00Z"}
    assert _bind(rec, "p", _sha(decl)) == (True, "BOUND")
    _unbound({"inputs": {"chain": "pcb_energy_chain.yaml", "stages": "ONE"}, "ts": "2026-09-26T12:00:00Z"}, "p", _sha(decl))


def t_energy_chain_ties_the_dock_block_stage_to_e5s_board_file():
    import energy_chain as E
    bf, bsha = _real_board("e5")
    r = E.check()
    ids = (r.get("by_board") or {}).get("e5")
    if not ids: raise Skip("the chain names no stage on board E5")
    inp = E.recorded_inputs(r, ids)
    assert inp["board_file_e5"]["sha256_16"] == bsha and not os.path.isabs(inp["board_file_e5"]["path"]), inp
    assert _bind({"inputs": inp}, "e5", None, {bsha}) == (True, "BOUND")
    _unbound({"inputs": {"chain": "pcb_energy_chain.yaml", "stages": ",".join(ids)}}, "e5", None, {bsha})
    # and the set verdict, which BAT-002 reads on A, E, E5 and P, records each of those boards' artefact
    allids = sorted({s for v in r["by_board"].values() for s in v})
    whole = E.recorded_inputs(r, allids, stages=False)
    for L in ("a", "e", "p"):
        if PA.netlist(L) and os.path.isfile(PA.netlist(L)):
            assert whole["netlist_%s" % L]["sha256_16"] == _sha(PA.netlist(L)), (L, whole.keys())
    assert whole["board_file_e5"]["sha256_16"] == bsha, whole.keys()


# ---------------------------------------------------------------------------------------------------- check_contracts
def t_check_contracts_records_each_boards_netlist_and_nothing_of_e5():
    import test_smbus_lead_contract as SMB
    ecad = SMB._tree(SMB.XH4)
    v = os.path.join(ecad, "out")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "check_contracts.py"), ecad], cwd=ecad, capture_output=True,
                       text=True, timeout=300, env=dict(os.environ, VERDICT_DIR=v))
    rec = _verdict(v, "check_contracts_p")
    pn = os.path.join(ecad, "pcb-p-pack", "out", "pcb-p-pack.net")
    en = os.path.join(ecad, "pcb-e1-dock", "out", "pcb-e1-dock.net")
    assert rec["inputs"]["netlist_p"]["sha256_16"] == _sha(pn), (rec["inputs"], r.stdout[-800:])
    assert rec["inputs"]["netlist_e"]["sha256_16"] == _sha(en), rec["inputs"]
    assert _bind(rec, "p", _sha(pn)) == (True, "BOUND")
    _unbound(dict(rec, inputs={"boards": "A,B,C,D,E,P"}), "p", _sha(pn))
    whole = _verdict(v, "check_contracts")
    assert not [k for k in whole["inputs"] if "e5" in k], whole["inputs"]
    _unbound(whole, "e5", None, {"b" * 16})
    # ANOTHER BOARD'S NETLIST: current only while it is that board's own
    m = {"boards": {"p": {"project": "pcb-p-pack"}, "e": {"project": "pcb-e1-dock"}}}
    keep = dict(S._DESIGN_NOW)
    try:
        S._DESIGN_NOW[("e", "pcb-e1-dock")] = {"no_chain": False, "netlist_sha16": "f" * 16, "netlist_content16": None,
                                              "board_shas": set()}
        b, cause = _bind(rec, "p", _sha(pn), m=m)
        assert not b and cause == "OTHER_DESIGN", (b, cause)
        S._DESIGN_NOW[("e", "pcb-e1-dock")]["netlist_sha16"] = _sha(en)
        assert _bind(rec, "p", _sha(pn), m=m) == (True, "BOUND")
    finally:
        S._DESIGN_NOW.clear(); S._DESIGN_NOW.update(keep)


# ---------------------------------------------------------------------------------------------------- interfaces
def t_interfaces_records_the_netlist_beside_the_declared_intent_and_e5s_board_file():
    net, nsha = _real("a")
    _bf, bsha = _real_board("e5")
    v = tempfile.mkdtemp(prefix="rec-if-")
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "interfaces.py")], cwd=v, capture_output=True, text=True,
                       timeout=300, env=dict(os.environ, VERDICT_DIR=v))
    a, e5 = _verdict(v, "interfaces_a"), _verdict(v, "interfaces_e5")
    assert a["inputs"]["netlist"]["sha256_16"] == nsha, (a["inputs"], r.stdout[-500:])
    assert a["inputs"]["intent"]["path"] == PA.rel(PA.intent("a")), a["inputs"]
    assert _bind(a, "a", nsha) == (True, "BOUND")
    assert e5["inputs"]["board_file"]["sha256_16"] == bsha, e5["inputs"]
    assert _bind(e5, "e5", None, {bsha}) == (True, "BOUND")
    _unbound(dict(a, inputs={"spec": "pcb_interfaces.yaml", "board": "a"}), "a", nsha)
    _unbound(dict(e5, inputs={"spec": "pcb_interfaces.yaml", "board": "e5"}), "e5", None, {bsha})


# ---------------------------------------------------------------------------------------------------- pack_protection
def t_pack_protection_records_board_ps_declared_netlist():
    import pack_protection as PP
    net, nsha = _real("p")
    assert os.path.abspath(PP.NETLIST) == os.path.abspath(net), "the default netlist is not the declared phase's"
    v = tempfile.mkdtemp(prefix="rec-pack-")
    subprocess.run([sys.executable, os.path.join(TOOLS, "pack_protection.py"), "--check"], cwd=v, capture_output=True,
                   text=True, timeout=300, env=dict(os.environ, VERDICT_DIR=v))
    rec = _verdict(v, "pack_protection")
    assert rec["inputs"]["netlist"]["sha256_16"] == nsha and rec["inputs"]["table"]["sha256_16"], rec["inputs"]
    assert _bind(rec, "p", nsha) == (True, "BOUND")
    _unbound(dict(rec, inputs={"table": "v2/ecad/tools/pcb_pack_protection.yaml",
                               "netlist": "v2/ecad/" + PA.rel(net)}), "p", nsha)


# ---------------------------------------------------------------------------------------------------- safe_lines, port_protect
def _declared_zero_on_e5(tool, name):
    _bf, bsha = _real_board("e5")
    if not PA.no_schematic("e5"): raise Skip("the manifest no longer marks E5 as a board with no schematic")
    v = tempfile.mkdtemp(prefix="rec-%s-" % name)
    subprocess.run([sys.executable, os.path.join(TOOLS, tool), "--board", "e5"], cwd=v, capture_output=True, text=True,
                   timeout=120, env=dict(os.environ, VERDICT_DIR=v))
    rec = _verdict(v, "%s_e5" % name)
    assert rec["inputs"]["board_file"]["sha256_16"] == bsha, rec["inputs"]
    assert _bind(rec, "e5", None, {bsha}) == (True, "BOUND")
    _unbound(dict(rec, inputs={"board": "e5"}), "e5", None, {bsha})


def _on_a_copy_of_a(tool, name):
    net, nsha = _real("a")
    d = tempfile.mkdtemp(prefix="rec-%s-" % name); os.makedirs(os.path.join(d, "out"))
    shutil.copy(net, os.path.join(d, "out")); shutil.copy(PA.intent("a"), os.path.join(d, "out"))
    subprocess.run([sys.executable, os.path.join(TOOLS, tool), os.path.join("out", os.path.basename(net))], cwd=d,
                   capture_output=True, text=True, timeout=300, env=dict(os.environ, VERDICT_DIR=os.path.join(d, "out")))
    rec = _verdict(os.path.join(d, "out"), "%s_a" % name)
    assert rec["inputs"]["netlist"]["sha256_16"] == nsha and rec["inputs"]["netlist"].get("content16"), rec["inputs"]
    assert rec["inputs"]["intent"]["sha256_16"] == _sha(PA.intent("a")), rec["inputs"]
    assert _bind(rec, "a", nsha) == (True, "BOUND")


def t_safe_lines_records_the_netlist_and_on_e5_the_board_file():
    _on_a_copy_of_a("safe_lines.py", "safe_lines")
    _declared_zero_on_e5("safe_lines.py", "safe_lines")


def t_port_protect_records_the_netlist_and_on_e5_the_board_file():
    _on_a_copy_of_a("port_protect.py", "port_protect")
    _declared_zero_on_e5("port_protect.py", "port_protect")


# ---------------------------------------------------------------------------------------------------- rules_status
def t_the_projection_table_names_exactly_what_these_fixtures_prove():
    have = {k: set(v) for k, v in S.RECORDS_ARTEFACT.items()}
    assert have == PROVED, "rules_status.RECORDS_ARTEFACT %s and the fixtures here prove %s" % (have, PROVED)


def t_a_retake_of_a_writer_that_records_now_projects_current_and_of_another_does_not():
    import test_evidence_class as EC
    rule, cov = EC._rule(), EC._cov()

    def proj(vs, cand, m, config):
        row = S.result_for(rule, "x", cov, vs, m, EC.FP, None, {"x", EC.BOARD})
        return S.retake_projection(rule, "x", cov, vs, m, row, cand, regs=EMPTY, config_inputs=config,
                                   now="2026-09-26T12:00:00+00:00")
    # a reading in power_sequence's old shape, a bare file name
    vs = EC._rec(net=None, ts="2026-09-26T08:00:00Z")
    vs["gate_x"]["inputs"]["netlist"] = "pcb-x.net"
    for writer, want in (("power_sequence.py", S.CURRENT_CANDIDATE), ("rules_status.py", S.AWAITING_REVALIDATION)):
        vs["gate_x"]["writer"] = {"file": writer, "sha16": "0" * 16}
        p = proj(vs, EC._cand(), EC._manifest(), {writer: ()})
        assert p["retake_class"] == want, (writer, p)
    # a declaration read on a board with no schematic (safe_lines --board, the letter alone)
    m = EC._manifest(); m["boards"]["x"]["no_chain"] = True
    cand = dict(EC._cand(net=None), netlist_sha16=None)
    vs = EC._rec(net=None)
    vs["gate_x"]["inputs"] = {"board": "x"}
    for writer, want in (("safe_lines.py", S.CURRENT_CANDIDATE), ("check_contracts.py", S.AWAITING_REVALIDATION)):
        vs["gate_x"]["writer"] = {"file": writer, "sha16": "0" * 16}
        p = proj(vs, cand, m, {writer: ()})
        assert p["retake_class"] == want, (writer, p)


def t_a_retake_reads_another_boards_netlist_at_that_boards_candidate():
    import test_evidence_class as EC
    rule, cov = EC._rule(), EC._cov()
    m = EC._manifest(); m["boards"]["y"] = {"project": "pcb-y", "required": True}
    vs = EC._rec()
    vs["gate_x"]["inputs"]["netlist_y"] = {"path": "pcb-y/out/pcb-y.net", "sha256_16": "9" * 16}
    keep = dict(S._DESIGN_NOW)
    try:
        S._DESIGN_NOW[("y", "pcb-y")] = {"no_chain": False, "netlist_sha16": "7" * 16, "netlist_content16": None,
                                        "board_shas": set()}
        row = S.result_for(rule, "x", cov, vs, m, EC.FP, None, {"x", EC.BOARD})
        k = S.evidence_class(rule, "x", cov, vs, m, EC.FP, {"x", EC.BOARD}, row, EC._cand(), EMPTY,
                             config_inputs=EC.NO_CONFIG)
        assert k["evidence_cause"] == "OTHER_DESIGN", k
        p = S.retake_projection(rule, "x", cov, vs, m, row, EC._cand(), regs=EMPTY, config_inputs=EC.NO_CONFIG,
                                now="2026-09-26T12:00:00+00:00")
        assert p["retake_class"] == S.CURRENT_CANDIDATE, p
    finally:
        S._DESIGN_NOW.clear(); S._DESIGN_NOW.update(keep)


def t_the_phase_directory_is_the_one_rules_status_judges_against():
    m = S.manifest()
    for L in m["boards"]:
        assert PA.phase_dir(L) == S._phase_dir(L, m), (L, PA.phase_dir(L), S._phase_dir(L, m))


def t_a_record_inside_this_repository_is_relative_and_never_a_temporary_input():
    net, _s = _real("a")
    r = PA.record(net)
    assert not os.path.isabs(r["path"]) and r["path"].endswith(os.path.basename(net)), r
    assert S._temp_input({"inputs": {"netlist": r}}) is None
    assert PA.rel(os.path.join(PA.ROOT, "v2", "vendor", "x.pdf")) == os.path.join("..", "vendor", "x.pdf")
    outside = os.path.join(tempfile.mkdtemp(prefix="rec-out-"), "b.net"); open(outside, "w").write("x")
    assert PA.record(outside)["path"] == outside, "a file outside this repository must keep its own path"
