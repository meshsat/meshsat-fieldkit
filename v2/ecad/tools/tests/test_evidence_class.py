"""Evidence classes: a reading counts for the CURRENT candidate only when it was taken on it (MESHSAT-1357, 26 September
2026; review of that day, section 1: "Distinguish current-candidate evidence, valid historical evidence and evidence
awaiting revalidation", "Keep desk reviews and physical tests in distinct result categories").

Executed against synthetic verdicts and a synthetic candidate, never against source text. Each property has a
defective fixture that must NOT count as current (or as physical) and an acceptable one that must:

  * a verdict written by a tool whose file has changed since is AWAITING_REVALIDATION; the same verdict written by
    the byte-identical file is CURRENT_CANDIDATE; a recorded compatibility entry makes it VALID_HISTORICAL;
  * a verdict taken on another netlist sha is AWAITING_REVALIDATION; on the candidate's netlist it is current;
  * a layout reading is current only when the layout carries the current netlist;
  * a reading of a PROTOTYPE-phase rule is a DESK_REVIEW and never a PHYSICAL_TEST, which needs a measurement record,
    and only when it is bound like any other reading (an unbound one awaits revalidation);
  * a release-package reading binds by a file of the declared phase's folder recorded by sha, never by the folder's name;
  * a reading taken before a configuration input its writer reads changed is AWAITING_REVALIDATION, a `kind: config`
    entry pinned to the file's current sha makes it VALID_HISTORICAL, and a writer nobody declared cannot be current;
  * every configuration entry in the real register holds what it claims, re-derived from git, and names the one
    reading it vouches for (an entry never reuses another reading of the same rule and board);
  * SCH-002's pad-alias file is its configuration: a reading older than the file's last commit is not current;
  * `retake_projection` says what a re-take alone would read: current where the writer records the netlist by sha
    and is declared, UNBOUND where it records none, CONFIG_UNDECLARED for an undeclared writer, LAYOUT_NOT_CURRENT for
    a schematic-phase reading of the board file, OTHER_BOARD for another board's file;
  * the layout-entry table names the first step for each blocker and the stream that owns it;
  * an invalidated verdict is refused by content; an unreadable register refuses every current claim;
  * the readiness gate cannot read READY on a PASS that awaits revalidation;
  * the generated page's headline is the one the review prescribes and quotes no mixed-revision percentage.
"""
import os, sys, json, hashlib, tempfile, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import Skip
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import rules_status as S

EPOCH = "2026-09-16T00:35:00+02:00"
FP = "fingerprint0000"
NET = "aaaaaaaaaaaaaaaa"
BOARD = "bbbbbbbbbbbbbbbb"
EMPTY = {"invalidated": {}, "compatibility": [], "errors": []}


def _now16(name="rules_status.py"):
    return hashlib.sha256(open(os.path.join(TOOLS, name), "rb").read()).hexdigest()[:16]


def _manifest():
    return {"manifest_version": "test", "boards": {"x": {"project": "pcb-x", "required": True}},
            "promotion": {"frozen": False}, "evidence": {"epoch": EPOCH}}


def _rule(phase="SCHEMATIC", rid="R-1"):
    return {"id": rid, "domain": "SCHEMATIC", "short_name": "n", "release_effect": "BLOCKER", "verification_phase": phase}


def _cov(maturity="ENFORCED"):
    return {"R-1": {"verification": {"tool": "x.py", "verdict": "gate_x"}, "maturity": maturity},
            "SCH-002": {"verification": {"tool": "x.py", "verdict": "gate_x"}, "maturity": maturity}}


def _rec(net=NET, board=None, writer_sha=None, result="PASS", **extra):
    inputs = {}
    if net: inputs["netlist"] = {"path": "out/pcb-x.net", "sha256_16": net}
    if board: inputs["board"] = {"path": "pcb-x.kicad_pcb", "sha256_16": board}
    rec = {"tool": "gate_x", "ts": "2026-09-26T10:00:00Z", "verdict": result, "denominator": 3, "counts": {},
           "policy": {"rule_set_fingerprint": FP}, "inputs": inputs,
           "writer": {"file": "rules_status.py", "sha16": writer_sha or _now16()}}
    rec.update(extra)
    return {"gate_x": rec}


def _cand(net=NET, layout=False):
    return {"declared_phase": "X1", "netlist": "pcb-x/out/pcb-x.net", "netlist_sha16": net,
            "netlist_committed": "2026-09-26T09:00:00+00:00", "board_shas": [BOARD], "layout_current": layout,
            "layout_why": "fixture"}


# The fixtures' writer is this tree's rules_status.py (so its hash is "the tool here"); it is declared as reading no
# configuration unless a test says otherwise.
NO_CONFIG = {"rules_status.py": ()}


def _class(vs, rule=None, cov=None, cand=None, regs=EMPTY, tool_state=None, config=NO_CONFIG):
    rule = rule or _rule(); cov = cov or _cov()
    row = S.result_for(rule, "x", cov, vs, _manifest(), FP, None, {"x", BOARD})
    kw = {} if tool_state is None else {"tool_state": tool_state}
    return S.evidence_class(rule, "x", cov, vs, _manifest(), FP, {"x", BOARD}, row, cand or _cand(), regs,
                            config_inputs=config, **kw), row


def t_a_reading_under_the_byte_identical_tool_on_the_candidate_netlist_is_current():
    k, row = _class(_rec())
    assert row["result"] == S.PASS and k["evidence_class"] == S.CURRENT_CANDIDATE, (row, k)


def t_a_reading_under_a_changed_tool_does_not_count_as_current():
    """The review's words: a changed matching or polarity algorithm can invalidate a reading. The writer's own hash
    differs from the file here, so the reading is AWAITING_REVALIDATION, whatever its result says, and the result
    itself (the historical aggregate) is left as it was."""
    k, row = _class(_rec(writer_sha="0" * 16))
    assert row["result"] == S.PASS, "the historical result must not move"
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "TOOL_CHANGED", k
    assert k["evidence_class"] not in S.COUNTS_AS_CURRENT


def t_a_changed_tool_is_reused_only_under_a_rationale_that_pins_both_versions():
    regs = {"invalidated": {}, "errors": [], "compatibility": [
        {"kind": "tool", "tool": "rules_status.py", "then": "0" * 16, "now": _now16(), "rationale": "docstring only"}]}
    k, _ = _class(_rec(writer_sha="0" * 16), regs=regs)
    assert k["evidence_class"] == S.VALID_HISTORICAL and "docstring only" in k["evidence_why"], k
    # the same entry for another version of the file vouches for nothing
    regs["compatibility"][0]["now"] = "f" * 16
    k2, _ = _class(_rec(writer_sha="0" * 16), regs=regs)
    assert k2["evidence_class"] == S.AWAITING_REVALIDATION, k2


def t_a_netlist_sha_mismatch_does_not_count_as_current():
    k, row = _class(_rec(net="cccccccccccccccc"))
    assert row["result"] == S.PASS
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "NETLIST_MISMATCH", k
    k2, _ = _class(_rec(net=NET))
    assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2


def t_a_regenerated_netlist_binds_by_its_content_identity_and_not_by_a_file_sha():
    """gate_sweep regenerates the netlist before judging it, so the file sha it records carries a new export date.
    A reading that records regen_compare.content_hash as `content16` binds when the content is the candidate's."""
    cand = dict(_cand(), netlist_content16="1234567890abcdef")
    vs = _rec(net="cccccccccccccccc")
    vs["gate_x"]["inputs"]["netlist"]["content16"] = "1234567890abcdef"
    k, _ = _class(vs, cand=cand)
    assert k["evidence_class"] == S.CURRENT_CANDIDATE, k
    vs["gate_x"]["inputs"]["netlist"]["content16"] = "fedcba0987654321"
    k2, _ = _class(vs, cand=cand)
    assert k2["evidence_class"] == S.AWAITING_REVALIDATION and k2["evidence_cause"] == "NETLIST_MISMATCH", k2


def t_a_reading_that_records_no_netlist_is_not_bound_and_one_older_than_the_netlist_says_so():
    k, _ = _class(_rec(net=None, ts="2026-09-26T10:00:00Z"))
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "UNBOUND", k
    k2, _ = _class(_rec(net=None, ts="2026-09-26T08:00:00Z"))
    assert k2["evidence_cause"] == "PREDATES_ARTEFACT", k2


def t_a_document_rule_is_unbound_and_never_dated_against_the_netlist():
    """ENV-002 judges public documents; a claims reading that names its documents without their content cannot be
    shown current, and the netlist's commit date says nothing about it."""
    rule = _rule(phase="RELEASE_PACKAGE", rid="ENV-002")
    cov = {"ENV-002": {"verification": {"tool": "x.py", "verdict": "gate_x"}, "maturity": "ENFORCED"}}
    vs = _rec(net=None, ts="2026-09-26T08:00:00Z")
    vs["gate_x"]["inputs"]["documents"] = "README.md,v2/README.md"
    k, _ = _class(vs, rule=rule, cov=cov)
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "UNBOUND", k


def t_a_layout_reading_counts_only_when_the_layout_carries_the_current_netlist():
    rule = _rule(phase="ROUTED_BOARD")
    k, _ = _class(_rec(net=None, board=BOARD), rule=rule, cand=_cand(layout=False))
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "LAYOUT_NOT_CURRENT", k
    k2, _ = _class(_rec(net=None, board=BOARD), rule=rule, cand=_cand(layout=True))
    assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2
    k3, _ = _class(_rec(net=None, board="dddddddddddddddd"), rule=rule, cand=_cand(layout=True))
    assert k3["evidence_class"] == S.AWAITING_REVALIDATION, k3


def t_a_cross_board_reading_waits_for_the_other_board():
    """E5's contract reading also judged board A's file; A's layout is not current, so neither is the reading."""
    rule = _rule(phase="ROUTED_BOARD")
    vs = _rec(net=None, board=BOARD)
    vs["gate_x"]["inputs"]["board_a"] = {"path": "/root/sweep/pcb-a-power.kicad_pcb", "sha256_16": "eeeeeeeeeeeeeeee"}
    k, _ = _class(vs, rule=rule, cand=_cand(layout=True))
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "OTHER_BOARD", k
    k2, _ = _class(_rec(net=None, board=BOARD), rule=rule, cand=_cand(layout=True))
    assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2


def t_the_layout_rule_itself_needs_both_the_board_and_the_netlist():
    rule = _rule(phase="PLACED_BOARD", rid="SCH-002")
    k, _ = _class(_rec(net="cccccccccccccccc", board=BOARD), rule=rule)
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "NETLIST_MISMATCH", k
    k2, _ = _class(_rec(net=NET, board=BOARD), rule=rule)
    assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2


def t_a_desk_review_is_never_a_physical_test():
    """REL-001 at the PROTOTYPE phase reads a connector and load list: a desk check. Nothing is built."""
    rule = _rule(phase="PROTOTYPE")
    k, row = _class(_rec(), rule=rule)
    assert row["result"] == S.PASS
    assert k["evidence_class"] == S.DESK_REVIEW and k["evidence_class"] != S.PHYSICAL_TEST, k
    # a verdict that only SAYS it is physical, with no measurement record, is still not one
    k2, _ = _class(_rec(evidence_kind="PHYSICAL_TEST"), rule=rule)
    assert k2["evidence_class"] == S.DESK_REVIEW, k2
    # the acceptable fixture: a declared measurement with its record
    vs = _rec(evidence_kind="PHYSICAL_TEST")
    vs["gate_x"]["inputs"]["measurement_record"] = "bench/2027-01-01-rel001.csv"
    k3, _ = _class(vs, rule=rule)
    assert k3["evidence_class"] == S.PHYSICAL_TEST, k3
    # a measurement of an older revision is not a physical test of this one (third round)
    old = _rec(net="cccccccccccccccc", evidence_kind="PHYSICAL_TEST")
    old["gate_x"]["inputs"]["measurement_record"] = "bench/2027-01-01-rel001.csv"
    k3b, _ = _class(old, rule=rule)
    assert k3b["evidence_class"] == S.AWAITING_REVALIDATION and k3b["evidence_cause"] == "NETLIST_MISMATCH", k3b
    # a manually verified document is a desk review too
    k4 = S.evidence_class(_rule(), "x", _cov("VERIFIED_MANUALLY"), {}, _manifest(), FP, {"x"},
                          {"result": S.PASS, "why": "pinned"}, _cand(), EMPTY)
    assert k4["evidence_class"] == S.DESK_REVIEW, k4


def t_a_desk_review_that_is_not_bound_awaits_revalidation():
    """REL-001 read as a current desk review on all seven boards while it recorded no netlist and its list had changed
    since (faf8c981). A desk review is bound like any other reading: unbound, it is AWAITING_REVALIDATION."""
    rule = _rule(phase="PROTOTYPE")
    k, row = _class(_rec(net=None, ts="2026-09-26T10:00:00Z"), rule=rule)
    assert row["result"] == S.PASS
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "UNBOUND", k
    k2, _ = _class(_rec(net=None, ts="2026-09-26T08:00:00Z"), rule=rule)
    assert k2["evidence_class"] == S.AWAITING_REVALIDATION and k2["evidence_cause"] == "PREDATES_ARTEFACT", k2
    k3, _ = _class(_rec(net=NET), rule=rule)
    assert k3["evidence_class"] == S.DESK_REVIEW, k3


def _pkg_cand(files):
    return dict(_cand(layout=True), package={"folder": "release/revA/boards/meshsat-pcb-x-revA-X1", "files": files})


def t_a_release_package_reading_binds_by_the_folders_content_and_never_by_its_name():
    """E5's DFM-001 and DOC-001 recorded only {"folder": "meshsat-pcb-e5-revA-E5"} and read as current. A folder
    name says which phase somebody meant; a file of it recorded by sha says what was read."""
    rule = _rule(phase="RELEASE_PACKAGE")
    cand = _pkg_cand({"pcb-x-bom.csv": "1111111111111111", "pcb-x-gerbers.zip": "2222222222222222"})
    by_name = _rec(net=None, board=BOARD)
    by_name["gate_x"]["inputs"]["folder"] = "meshsat-pcb-x-revA-X1"
    k, row = _class(by_name, rule=rule, cand=cand)
    assert row["result"] == S.PASS
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "UNBOUND", k
    stale = _rec(net=None)
    stale["gate_x"]["inputs"]["bom"] = {"path": "meshsat-pcb-x-revA-X1/pcb-x-bom.csv", "sha256_16": "9999999999999999"}
    k2, _ = _class(stale, rule=rule, cand=cand)
    assert k2["evidence_class"] == S.AWAITING_REVALIDATION and k2["evidence_cause"] == "UNBOUND", k2
    good = _rec(net=None)
    good["gate_x"]["inputs"]["bom"] = {"path": "meshsat-pcb-x-revA-X1/pcb-x-bom.csv", "sha256_16": "1111111111111111"}
    k3, _ = _class(good, rule=rule, cand=cand)
    assert k3["evidence_class"] == S.CURRENT_CANDIDATE, k3
    # no folder of the declared phase in the tree: nothing to bind to
    k4, _ = _class(good, rule=rule, cand=_pkg_cand({}))
    assert k4["evidence_class"] == S.AWAITING_REVALIDATION and k4["evidence_cause"] == "UNBOUND", k4
    # THE BOM IS AMONG WHAT BINDS (third round): a reading of the gerbers alone does not bind a folder that holds a
    # BOM, and one stale file beside a current BOM means another copy was read
    zip_only = _rec(net=None)
    zip_only["gate_x"]["inputs"]["zip"] = {"path": "x/pcb-x-gerbers.zip", "sha256_16": "2222222222222222"}
    k5, _ = _class(zip_only, rule=rule, cand=cand)
    assert k5["evidence_cause"] == "UNBOUND" and "BOM" in k5["evidence_why"], k5
    mixed = _rec(net=None)
    mixed["gate_x"]["inputs"]["bom"] = {"path": "x/pcb-x-bom.csv", "sha256_16": "1111111111111111"}
    mixed["gate_x"]["inputs"]["zip"] = {"path": "x/pcb-x-gerbers.zip", "sha256_16": "9999999999999999"}
    k6, _ = _class(mixed, rule=rule, cand=cand)
    assert k6["evidence_cause"] == "UNBOUND", k6
    mixed["gate_x"]["inputs"]["zip"]["sha256_16"] = "2222222222222222"
    k7, _ = _class(mixed, rule=rule, cand=cand)
    assert k7["evidence_class"] == S.CURRENT_CANDIDATE, k7
    # a folder with no BOM at all (E5's: a bare contact board) binds by the files it has
    k8, _ = _class(zip_only, rule=rule, cand=_pkg_cand({"pcb-x-gerbers.zip": "2222222222222222"}))
    assert k8["evidence_class"] == S.CURRENT_CANDIDATE, k8


def t_a_changed_configuration_input_does_not_count_as_current():
    """TRN-001 on A read its port list from boards/a.json, which was committed again after the reading. A reading
    is current only when every configuration file its writer is declared to read is unchanged since."""
    d = tempfile.mkdtemp(prefix="evidence-config-")
    cfg = os.path.join(d, "x.json")
    open(cfg, "w").write('{"external_ports": []}')
    now = hashlib.sha256(open(cfg, "rb").read()).hexdigest()[:16]
    config = {"rules_status.py": (cfg,)}
    rel = os.path.relpath(cfg, S.ECAD)
    # by the sha the reading recorded
    vs = _rec(); vs["gate_x"]["inputs"]["list"] = {"path": "x.json", "sha256_16": "0" * 16}
    k, row = _class(vs, config=config)
    assert row["result"] == S.PASS
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "CONFIG_CHANGED", k
    vs["gate_x"]["inputs"]["list"]["sha256_16"] = now
    k2, _ = _class(vs, config=config)
    assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2
    # by the file's last commit, where the reading recorded nothing
    keep = S._config_when, S._git_dirty
    try:
        S._git_dirty = lambda p: False
        S._config_when = lambda p: "2026-09-26T12:00:00+02:00"      # 10:00Z, the reading's own instant: not after it
        k3, _ = _class(_rec(), config=config)
        assert k3["evidence_class"] == S.CURRENT_CANDIDATE, k3
        S._config_when = lambda p: "2026-09-26T12:32:33+02:00"      # 10:32Z, after the reading
        k4, _ = _class(_rec(), config=config)
        assert k4["evidence_class"] == S.AWAITING_REVALIDATION and k4["evidence_cause"] == "CONFIG_CHANGED", k4
        # reused only through an entry pinned to the file's CURRENT sha
        regs = {"invalidated": {}, "errors": [], "compatibility": [
            {"kind": "config", "rule": "R-1", "board": "x", "input": rel, "then": "0" * 16, "now": now,
             "reading": "2026-09-26T10:00:00Z", "summary": "prose keys only", "rationale": "the keys the tool reads are equal"}]}
        k5, _ = _class(_rec(), config=config, regs=regs)
        assert k5["evidence_class"] == S.VALID_HISTORICAL and "prose keys only" in k5["evidence_why"], k5
        # the entry names ONE reading: another reading of the same rule and board is not reused under it
        k5b, _ = _class(_rec(ts="2026-09-26T09:30:00Z"), config=config, regs=regs)
        assert k5b["evidence_cause"] == "CONFIG_CHANGED", k5b
        regs["compatibility"][0]["now"] = "f" * 16
        k6, _ = _class(_rec(), config=config, regs=regs)
        assert k6["evidence_class"] == S.AWAITING_REVALIDATION and k6["evidence_cause"] == "CONFIG_CHANGED", k6
        # an uncommitted edit cannot be dated and counts as changed
        S._config_when = lambda p: "2026-09-20T00:00:00+02:00"
        S._git_dirty = lambda p: True
        k7, _ = _class(_rec(), config=config)
        assert k7["evidence_cause"] == "CONFIG_CHANGED", k7
        # a recorded directory disambiguates files of one name (every board's ORDER-NOTES.txt): a reading that
        # recorded its own board's note is compared with that note only
        S._git_dirty = lambda p: False
        notes = [os.path.join(d, "PCB-X", "ORDER-NOTES.txt"), os.path.join(d, "PCB-Y", "ORDER-NOTES.txt")]
        for i, f in enumerate(notes):
            os.makedirs(os.path.dirname(f), exist_ok=True); open(f, "w").write("board %d\n" % i)
        vsn = _rec(); vsn["gate_x"]["inputs"]["notes"] = {"path": "order/PCB-X/ORDER-NOTES.txt",
                                                          "sha256_16": S._sha16_of(notes[0])}
        S._config_when = lambda p: "2026-09-26T12:32:33+02:00"          # both committed after the reading
        k7b, _ = _class(vsn, config={"rules_status.py": (os.path.join(d, "*", "ORDER-NOTES.txt"),)})
        assert k7b["evidence_cause"] == "CONFIG_CHANGED" and "PCB-Y" in k7b["evidence_why"], k7b
        S._config_when = lambda p: "2026-09-26T12:32:33+02:00" if "PCB-X" in p else "2026-09-20T00:00:00+02:00"
        k7c, _ = _class(vsn, config={"rules_status.py": (os.path.join(d, "*", "ORDER-NOTES.txt"),)})
        assert k7c["evidence_class"] == S.CURRENT_CANDIDATE, k7c
        # a glob declares every file it matches
        S._git_dirty = lambda p: False
        open(os.path.join(d, "y.json"), "w").write("{}")
        S._config_when = lambda p: "2026-09-26T12:32:33+02:00" if p.endswith("y.json") else "2026-09-20T00:00:00+02:00"
        k8, _ = _class(_rec(), config={"rules_status.py": (os.path.join(d, "*.json"),)})
        assert k8["evidence_cause"] == "CONFIG_CHANGED" and "y.json" in k8["evidence_why"], k8
    finally:
        S._config_when, S._git_dirty = keep


def t_a_writer_nobody_declared_cannot_be_current():
    k, _ = _class(_rec(), config={})
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "CONFIG_UNDECLARED", k


def t_every_configuration_entry_in_the_register_holds_what_it_claims():
    """A `kind: config` entry says a configuration file changed after a reading only where its tool does not look.
    That claim is re-derived here from git for every entry that still applies (its `now` is the file in this tree):
    `then` is the file in the tree of the commit that first recorded the reading, and either the JSON keys the tool
    reads are equal (absent in both counts as equal) or no line of `then` is removed in `now`."""
    import subprocess, difflib
    regs = S.registers()
    assert not regs["errors"], regs["errors"]
    entries = [e for e in regs["compatibility"] if e.get("kind") == "config"]
    top = subprocess.run(["git", "-C", S.ECAD, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if top.returncode != 0: raise Skip("no git here, so the register's claims cannot be re-derived")
    root = top.stdout.strip()
    for e in entries:
        p = os.path.normpath(os.path.join(S.ECAD, e["input"]))
        if S._sha16_of(p) != str(e["now"]): continue                  # inert: it applies to nothing any more
        then = subprocess.run(["git", "-C", root, "show", "%s:%s" % (e["recorded_in"], os.path.relpath(p, root))],
                              capture_output=True)
        if then.returncode != 0: raise Skip("commit %s is not in this clone" % e["recorded_in"])
        # the entry names the one reading it vouches for, and that reading is in the commit it names
        assert e.get("verdict") and e.get("reading"), "%s names no reading" % e["input"]
        rd = subprocess.run(["git", "-C", root, "show", "%s:%s" % (e["recorded_in"], os.path.relpath(
            os.path.normpath(os.path.join(S.ECAD, e["verdict"])), root))], capture_output=True)
        assert rd.returncode == 0, (e["input"], "the verdict is not in %s" % e["recorded_in"])
        assert json.loads(rd.stdout).get("ts") == str(e["reading"]), (e["input"], "the reading is not the recorded one")
        assert hashlib.sha256(then.stdout).hexdigest()[:16] == str(e["then"]), (e["input"], "then is not the recorded tree's")
        now_b = open(p, "rb").read()
        assert e.get("keys") or e.get("additions_only"), "%s states no checkable claim" % e["input"]
        if e.get("keys"):
            a, b = json.loads(then.stdout), json.loads(now_b)
            for key in e["keys"]:
                assert (key in a) == (key in b) and a.get(key) == b.get(key), (e["input"], key)
        if e.get("additions_only"):
            gone = [ln for ln in difflib.ndiff(then.stdout.decode().splitlines(), now_b.decode().splitlines()) if ln.startswith("- ")]
            assert not gone, (e["input"], gone[:3])
        for k in ("rule", "board", "summary", "rationale", "ruled_by", "ruled_on"):
            assert e.get(k), (e["input"], k)


def t_a_reading_of_a_temporary_directory_is_not_current():
    vs = _rec()
    vs["gate_x"]["inputs"]["release"] = {"path": "/tmp/somewhere/v2/release/revA", "sha256_16": None}
    k, _ = _class(vs)
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "TEMP_INPUT", k


def t_an_unreadable_register_refuses_every_current_claim():
    regs = {"invalidated": {}, "compatibility": [], "errors": ["COMPATIBILITY.md: compatibility block unreadable"]}
    k, _ = _class(_rec(), regs=regs)
    assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "REGISTER_UNREADABLE", k


def t_the_registers_are_read_from_fenced_blocks_and_a_broken_one_is_an_error():
    d = tempfile.mkdtemp(prefix="evidence-registers-")
    good = "a" * 64
    open(os.path.join(d, "INVALIDATED-X.md"), "w").write(
        "# t\n\n<!-- evidence-register: invalidated -->\n```yaml\ninvalidated:\n  - path: out/x.verdict.json\n    sha256: %s\n```\n" % good)
    open(os.path.join(d, "COMPATIBILITY.md"), "w").write(
        "# t\n\n<!-- evidence-register: compatibility -->\n```yaml\ncompatibility: []\n```\n")
    r = S.registers(d)
    assert good in r["invalidated"] and r["compatibility"] == [] and not r["errors"], r
    d2 = tempfile.mkdtemp(prefix="evidence-registers-bad-")
    open(os.path.join(d2, "INVALIDATED-Y.md"), "w").write(
        "<!-- evidence-register: invalidated -->\n```yaml\ninvalidated:\n  - path: out/x.verdict.json\n    sha256: short\n```\n")
    r2 = S.registers(d2)
    assert r2["errors"], "an invalidated entry without a full sha256 was accepted silently"


def t_an_invalidated_verdict_is_refused_by_content_wherever_it_sits():
    """The fixture output of 25 September (routeflow_validate in v2/ecad/out) must not be read by any checkout that
    still carries it; the register names it by sha256, and `_verdicts` skips the file."""
    d = tempfile.mkdtemp(prefix="evidence-refuse-")
    out = os.path.join(d, "out"); os.makedirs(out)
    body = json.dumps({"tool": "gate_x", "ts": "2026-09-26T10:00:00Z", "verdict": "PASS", "inputs": {}}).encode()
    open(os.path.join(out, "gate_x.verdict.json"), "wb").write(body)
    keep_dirs, keep_regs = S._project_dirs, dict(S._REGISTERS)
    try:
        S._project_dirs = lambda letter, m: [out]
        S._REGISTERS.clear(); S._REGISTERS[S.EVIDENCE_DOCS] = {"invalidated": {}, "compatibility": [], "errors": []}
        assert "gate_x" in S._verdicts("x", _manifest())
        S._REGISTERS[S.EVIDENCE_DOCS] = {"invalidated": {hashlib.sha256(body).hexdigest(): {}}, "compatibility": [], "errors": []}
        assert "gate_x" not in S._verdicts("x", _manifest()), "an invalidated verdict was read"
    finally:
        S._project_dirs = keep_dirs; S._REGISTERS.clear(); S._REGISTERS.update(keep_regs)


def t_the_gate_cannot_read_ready_on_a_pass_that_awaits_revalidation():
    m = _manifest()
    ok = [dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD", evidence_class=S.CURRENT_CANDIDATE)]
    assert S.gate_state(ok, m) == "READY_FOR_PROTOTYPE"
    stale = [dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD", evidence_class=S.AWAITING_REVALIDATION)]
    assert S.gate_state(stale, m) == "INCONCLUSIVE", "a PASS awaiting revalidation made the set READY"
    legacy = [dict(result=S.PASS, release_effect="BLOCKER", verification_phase="ROUTED_BOARD")]
    assert S.gate_state(legacy, m) == "READY_FOR_PROTOTYPE", "a row computed before classes existed changed meaning"


def _audit(letter, rows, cand=None):
    return {"board": letter, "candidate": cand or _cand(), "rows": rows}


def _row(rule, phase, result, cls, cause="BOUND", effect="BLOCKER", maturity="ENFORCED"):
    return dict(rule=rule, short_name="n", verification_phase=phase, result=result, release_effect=effect,
                evidence_class=cls, evidence_cause=cause, evidence_why="why", maturity=maturity)


def t_the_page_headline_is_the_reviewed_one_and_quotes_no_mixed_percentage():
    import rules_render as RR
    audits = {"x": _audit("x", [_row("R-1", "SCHEMATIC", "PASS", S.CURRENT_CANDIDATE),
                                _row("R-2", "ROUTED_BOARD", "PASS", S.AWAITING_REVALIDATION, "LAYOUT_NOT_CURRENT"),
                                _row("R-3", "PROTOTYPE", "PASS", S.DESK_REVIEW, "PROTOTYPE_DESK_CHECK")]),
              "y": _audit("y", [_row("R-1", "SCHEMATIC", "PASS", S.AWAITING_REVALIDATION, "NETLIST_MISMATCH")])}
    body = RR.current_evidence_doc(audits, holds={}, regs=EMPTY)
    assert "**Foundations incomplete; 1 boards ready for layout; 0 physically verified.**" in body, body[:600]
    head, _, tail = body.partition("## Historical aggregate, mixed revisions")
    assert tail, "the historical aggregate has lost its name"
    assert not re.search(r"\d+(\.\d+)?\s*(%|percent)", head), "a percentage is quoted outside the historical aggregate"
    assert "mixed revisions" in tail and "percent" in tail
    # a hold keeps a board out of layout whatever its evidence
    body2 = RR.current_evidence_doc(audits, holds={"x": {"decision": 31}}, regs=EMPTY)
    assert "**Foundations incomplete; 0 boards ready for layout; 0 physically verified.**" in body2


def t_a_board_is_physically_verified_only_by_physical_tests():
    import rules_render as RR
    desk = _audit("x", [_row("R-3", "PROTOTYPE", "PASS", S.DESK_REVIEW, "PROTOTYPE_DESK_CHECK")])
    assert not RR.physically_verified(desk), "a desk review counted as a physical test"
    phys = _audit("x", [_row("R-3", "PROTOTYPE", "PASS", S.PHYSICAL_TEST, "MEASURED")])
    assert RR.physically_verified(phys)


# ------------------------------------------------------------------------------------------------------------------
# Third round on this stream (26 September 2026): a checker found SCH-002's alias file undeclared and showed that the
# page's "re-take on the committed netlist" remedy was wrong for most of the rows it named.
# ------------------------------------------------------------------------------------------------------------------
def _netlist_board_rec(ts="2026-09-26T10:00:00Z"):
    vs = _rec(net=NET, board=BOARD, ts=ts)
    vs["gate_x"]["writer"] = {"file": "netlist_board.py", "sha16": _now16("netlist_board.py")}
    return vs


def t_the_pad_alias_file_binds_the_layout_rule():
    """netlist_board.py reads tools/pad-aliases.txt (read_aliases) to decide which pad a netlist pin must land on,
    and SCH-002 is the rule whose current PASS makes a layout the candidate's. A reading taken before the alias file
    was last committed is CONFIG_CHANGED; one taken after it is current. Judged with the REAL CONFIG_INPUTS, so the
    first audit's empty entry for netlist_board.py fails this."""
    rule = _rule(phase="PLACED_BOARD", rid="SCH-002")
    alias = os.path.join(TOOLS, "pad-aliases.txt")
    keep = S._config_when, S._git_dirty
    try:
        S._git_dirty = lambda p: False
        S._config_when = lambda p: "2026-09-26T12:32:33+02:00" if os.path.abspath(p) == alias else "2026-09-01T00:00:00+02:00"
        k, row = _class(_netlist_board_rec("2026-09-26T10:00:00Z"), rule=rule, config=None,
                        tool_state=lambda r: ("CURRENT", ""))
        assert row["result"] == S.PASS
        assert k["evidence_class"] == S.AWAITING_REVALIDATION and k["evidence_cause"] == "CONFIG_CHANGED", k
        assert "pad-aliases.txt" in k["evidence_why"], k
        k2, _ = _class(_netlist_board_rec("2026-09-26T11:00:00Z"), rule=rule, config=None,
                       tool_state=lambda r: ("CURRENT", ""))
        assert k2["evidence_class"] == S.CURRENT_CANDIDATE, k2
    finally:
        S._config_when, S._git_dirty = keep


def t_every_declared_writer_and_fixed_input_exists_in_this_tree():
    """A misspelt writer in CONFIG_INPUTS would leave the real one undeclared and read as nothing; a misspelt fixed
    input would be skipped as "never in history and absent now". Templates and globs are left to the fixtures."""
    for w, paths in S.CONFIG_INPUTS.items():
        assert os.path.isfile(os.path.join(TOOLS, w)), "CONFIG_INPUTS names %s, which is not a tool here" % w
        for p in paths:
            if "{" in p or "*" in p: continue
            assert os.path.exists(os.path.normpath(os.path.join(S.ECAD, p))), "%s declares %s, which is not here" % (w, p)


def _proj(vs, rule=None, cand=None, config=NO_CONFIG, cov=None):
    rule = rule or _rule(); cov = cov or _cov()
    row = S.result_for(rule, "x", cov, vs, _manifest(), FP, None, {"x", BOARD})
    return S.retake_projection(rule, "x", cov, vs, _manifest(), row, cand or _cand(), regs=EMPTY,
                               config_inputs=config, now="2026-09-26T12:00:00+00:00")


def t_a_retake_projection_says_what_a_retake_alone_would_read():
    """The page's remedies are computed from this, so each shape the checker simulated is fixed here both ways."""
    # a reading on an older netlist, whose writer records the netlist by sha and is declared: a re-take binds
    old = _rec(net="cccccccccccccccc")
    k, _ = _class(old)
    assert k["evidence_cause"] == "NETLIST_MISMATCH", k
    p = _proj(old)
    assert p["retake_class"] == S.CURRENT_CANDIDATE, p
    # the same reading from a writer nobody declared: a re-take still cannot be current
    p = _proj(old, config={})
    assert p["retake_class"] == S.AWAITING_REVALIDATION and p["retake_cause"] == "CONFIG_UNDECLARED", p
    # a writer that records the netlist by bare name (power_sequence's shape) or not at all: a re-take is UNBOUND,
    # and a PREDATES_ARTEFACT reading becomes UNBOUND and never current
    bare = _rec(net=None, ts="2026-09-26T08:00:00Z")
    bare["gate_x"]["inputs"]["netlist"] = "pcb-x.net"
    k, _ = _class(bare)
    assert k["evidence_cause"] == "PREDATES_ARTEFACT", k
    p = _proj(bare)
    assert p["retake_class"] == S.AWAITING_REVALIDATION and p["retake_cause"] == "UNBOUND", p
    assert p["retake_blockers"] == ["rules_status.py"], p
    # a schematic-phase reading that records only the board waits on a layout, whatever a re-take does
    p = _proj(_rec(net=None, board="dddddddddddddddd"), cand=_cand(layout=False))
    assert p["retake_cause"] == "LAYOUT_NOT_CURRENT", p
    # another board's file keeps its own identity: a cross-board reading still waits for that board
    vs = _rec(net=None, board="dddddddddddddddd")
    vs["gate_x"]["inputs"]["board_a"] = {"path": "/root/sweep/pcb-a-power.kicad_pcb", "sha256_16": "eeeeeeeeeeeeeeee"}
    p = _proj(vs, rule=_rule(phase="ROUTED_BOARD"), cand=_cand(layout=True))
    assert p["retake_cause"] == "OTHER_BOARD", p
    p2 = _proj(_rec(net=None, board="dddddddddddddddd"), rule=_rule(phase="ROUTED_BOARD"), cand=_cand(layout=True))
    assert p2["retake_class"] == S.CURRENT_CANDIDATE, p2
    # a configuration input committed after the reading does not hold a re-take back
    keep = S._config_when, S._git_dirty
    try:
        d = tempfile.mkdtemp(prefix="evidence-retake-")
        cfg = os.path.join(d, "x.json"); open(cfg, "w").write("{}")
        S._git_dirty = lambda p: False
        S._config_when = lambda p: "2026-09-26T11:00:00+00:00"
        k, _ = _class(_rec(), config={"rules_status.py": (cfg,)})
        assert k["evidence_cause"] == "CONFIG_CHANGED", k
        p = _proj(_rec(), config={"rules_status.py": (cfg,)})
        assert p["retake_class"] == S.CURRENT_CANDIDATE, p
    finally:
        S._config_when, S._git_dirty = keep


def _prow(rule, result, cls, cause, rcls, rcause, blockers=(), phase="SCHEMATIC"):
    r = _row(rule, phase, result, cls, cause)
    r.update(retake_class=rcls, retake_cause=rcause, writers=list(blockers) or ["gate.py"], retake_blockers=list(blockers))
    return r


def t_the_layout_entry_table_names_the_first_step_and_its_owner():
    """Checkpoint item 6 of the review: the exact remaining blockers per board. A row a re-take alone would make
    current goes to the board's own stream; one whose tool records no artefact goes to the tools stream with the
    place it records its inputs; one that reads only the board file goes to the tools stream to judge the netlist;
    an undeclared writer goes to the evidence stream. The count of boards re-takes alone would admit is computed."""
    import rules_render as RR
    A = S.AWAITING_REVALIDATION
    audits = {"x": _audit("x", [
        _prow("R-1", "PASS", A, "NETLIST_MISMATCH", S.CURRENT_CANDIDATE, "BOUND", ["safe_lines.py"]),
        _prow("R-2", "PASS", A, "UNBOUND", A, "UNBOUND", ["new_recorder.py"]),
        _prow("R-3", "INCONCLUSIVE", A, "LAYOUT_NOT_CURRENT", A, "LAYOUT_NOT_CURRENT", ["edge_length.py"]),
        _prow("R-4", "PASS", A, "NETLIST_MISMATCH", A, "CONFIG_UNDECLARED", ["new_tool.py"]),
        # the tools stream's recording round (26 September 2026): a re-take of erc_gate binds only with --run, and the
        # set verdict of check_contracts on a board it reads nothing of is the registry writer's step, not the tool's
        _prow("R-5", "PASS", A, "TOOL_CHANGED", S.CURRENT_CANDIDATE, "BOUND", ["erc_gate.py"]),
        _prow("R-6", "PASS", A, "TOOL_CHANGED", A, "UNBOUND", ["check_contracts.py"])]),
              "y": _audit("y", [_prow("R-1", "PASS", A, "NETLIST_MISMATCH", S.CURRENT_CANDIDATE, "BOUND", ["safe_lines.py"])])}
    kinds = {b["rule"]: (b["kind"], b["owner"], b["closes"]) for b in RR.entry_blockers(audits["x"], {})}
    assert kinds["R-1"][:2] == ("RETAKE", "board stream X"), kinds["R-1"]
    assert kinds["R-2"][:2] == ("TOOL", "tools stream") and "new_recorder.py taught to record" in kinds["R-2"][2], kinds["R-2"]
    assert kinds["R-5"][:2] == ("RETAKE", "board stream X") and "--run" in kinds["R-5"][2], kinds["R-5"]
    assert kinds["R-6"][0] == "REGISTRY" and "block_contract.py" in kinds["R-6"][2], kinds["R-6"]
    assert kinds["R-3"][:2] == ("LAYOUT_TOOL", "tools stream") and "INCONCLUSIVE" in kinds["R-3"][2], kinds["R-3"]
    assert kinds["R-4"][0] == "CONFIG" and "evidence stream" in kinds["R-4"][1], kinds["R-4"]
    body = RR.current_evidence_doc(audits, holds={}, regs=EMPTY)
    assert "Re-takes alone would bring 1 of the 2 boards to layout entry" in body, body[:900]
    assert "**Foundations incomplete; 0 boards ready for layout; 0 physically verified.**" in body
    head, _, _t = body.partition("## Historical aggregate, mixed revisions")
    assert not re.search(r"\d+(\.\d+)?\s*(%|percent)", head), "a percentage is quoted outside the historical aggregate"
    # a hold is a blocker of its own, owned by the holds file's writer
    hb = RR.entry_blockers(audits["y"], {"y": {"decision": 99, "lifts_when": "decision 99 is ruled"}})
    assert [b["kind"] for b in hb] == ["RETAKE", "HOLD"] and "pcb_board_holds.yaml" in hb[1]["owner"], hb
