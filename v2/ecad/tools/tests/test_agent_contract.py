#!/usr/bin/env python3
"""The contract tier 2 and tier 2b run under (MESHSAT-862, 12 September 2026).

A model in the loop is safe here because of properties of the CODE, not because of instructions in a
prompt, and this file is where each property stops being an intention. Every rule below is written as
a fixture that MUST be refused, or as a text check over the files themselves, so it runs on any host
with no network, no endpoint and no KiCad.

  the proposer cannot actuate            propose/schema/evidence contain no subprocess, exec or delete
  the model owns three fields            a proposal that picks its own board is refused
  a knob nobody reads is refused         the authority is pair_preroute.py, parsed, never the document
  a reserved knob is refused with its    the never-auto floor, applied to the agent the way reserved.py
    reason                                applies it to a commit
  a basis-locked knob is refused         a row that changes the kernel is not comparable with one that does not
  an arm with no prediction is refused   an arm nobody predicted cannot disappoint
  a basis that says nothing is refused   "it should help" is not a basis
  an arm name is a slug                  it becomes a directory that arms.py removes with rmtree
  a repeat is refused                    measuring the same knobs twice is not learning
  the judge is never the model           the loop grades with arms.grade; the reviewer cannot move it
  a review must say where                a REJECT with no finding, or a finding with no location, is refused
  nothing about the endpoint is in the   the repo mirrors publicly within minutes
    tree
  the config is outside the tree, 600    a key in a world-readable file is refused before any call
  no gate imports the agent              a model may inform a proposal and may never judge a board
"""
import os, re, sys, json, glob, stat, tempfile
from harness import Skip   # noqa: F401

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENT = os.path.join(TOOLS, "agent")
REPO = os.path.dirname(os.path.dirname(TOOLS))
sys.path.insert(0, AGENT)
import schema, client                                              # noqa: E402
import review as reviewmod                                         # noqa: E402

TEMPLATE = {"board": "pcb-b-compute", "letter": "b", "source_project": "pcb-b-compute-b19",
            "placed": "out/pcb-b-compute-placed.kicad_pcb", "passes": [{"classes": "DIFF100"}],
            "_denominator": 48, "_stamp": "test"}
GOOD = {"arms": [{"name": "slack0055", "env": {"PAIR_CORRIDOR_SLACK": 0.055},
                  "predict": {"metric": "pairs", "op": ">=", "value": 24,
                              "basis": "the slack curve peaks at 0.06 with 57 of 113 and 0.05 lays 53, so a point "
                                       "between them should land at or above the 22 of 48 the couple gap measured"}}],
        "why": ["the corridor slack is the only knob that has ever moved this number"]}


def _refuses(proposal, needle, **kw):
    ok, errs, _ = schema.validate(proposal, TEMPLATE, **kw)
    if ok:
        raise AssertionError("the validator ACCEPTED a proposal it must refuse: %s" % json.dumps(proposal)[:160])
    if not any(needle.lower() in e.lower() for e in errs):
        raise AssertionError("refused, but for the wrong reason. Wanted %r, got: %s" % (needle, errs))


def t_the_good_fixture_is_accepted():
    """The passing half. A rule with no passing fixture refuses everything and looks strict."""
    ok, errs, arms = schema.validate(GOOD, TEMPLATE)
    if not ok:
        raise AssertionError("the good proposal was refused: %s" % errs)
    spec = schema.build_spec(GOOD, TEMPLATE, arms)
    if spec["board"] != "pcb-b-compute" or spec["arms"][0]["name"] != "slack0055":
        raise AssertionError("build_spec did not carry the template and the arm: %s" % json.dumps(spec)[:200])
    if "_denominator" in spec:
        raise AssertionError("build_spec leaked a private template field into the runnable spec")


def t_the_model_owns_three_fields():
    p = json.loads(json.dumps(GOOD)); p["source_project"] = "pcb-a-power-a23"
    _refuses(p, "does not own")
    q = json.loads(json.dumps(GOOD)); q["arms"][0]["timeout_s"] = 1
    _refuses(q, "does not own")


def t_a_knob_nobody_reads_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["env"] = {"PAIR_MAGIC_MODE": 1}
    _refuses(p, "no tool in this tree reads")


def t_a_reserved_knob_is_refused_with_its_reason():
    for k in ("PAIR_INNER", "PAIR_LAYERS", "PAIR_INNER_GAP"):
        p = json.loads(json.dumps(GOOD)); p["arms"][0]["env"] = {k: "x"}
        _refuses(p, "RESERVED")
        ok, errs, _ = schema.validate(p, TEMPLATE)
        if not any("OWNER-DECISIONS" in e for e in errs):
            raise AssertionError("%s was refused without saying where the decision belongs: %s" % (k, errs))


def t_a_basis_locked_knob_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["env"] = {"PAIR_VENV": 0}
    _refuses(p, "basis-locked")


def t_an_arm_without_a_prediction_is_refused():
    p = json.loads(json.dumps(GOOD)); del p["arms"][0]["predict"]
    _refuses(p, "carries no prediction")


def t_a_prediction_that_is_not_a_number_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["predict"]["value"] = "more"
    _refuses(p, "not a number")


def t_a_prediction_outside_the_denominator_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["predict"]["value"] = 900
    _refuses(p, "denominator")


def t_a_basis_that_says_nothing_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["predict"]["basis"] = "it should help"
    _refuses(p, "basis")


def t_an_arm_name_must_be_a_slug():
    for bad in ("../../../etc", "Slack 006", "a" * 40, ""):
        p = json.loads(json.dumps(GOOD)); p["arms"][0]["name"] = bad
        _refuses(p, "slug")


def t_an_empty_env_is_refused():
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["env"] = {}
    _refuses(p, "measures nothing")


def t_a_repeat_is_refused_and_allowed_on_purpose():
    sig = json.dumps({"PAIR_CORRIDOR_SLACK": "0.055"}, sort_keys=True)
    _refuses(GOOD, "repeats knobs already graded", graded=[sig])
    ok, errs, _ = schema.validate(GOOD, TEMPLATE, graded=[sig], allow_repeat=True)
    if not ok:
        raise AssertionError("--allow-repeat did not allow a deliberate repeat: %s" % errs)


def t_more_arms_than_the_cap_are_refused():
    p = json.loads(json.dumps(GOOD))
    second = json.loads(json.dumps(p["arms"][0])); second["name"] = "slack0065"
    second["env"] = {"PAIR_CORRIDOR_SLACK": 0.065}
    p["arms"].append(second)
    _refuses(p, "cap")


def t_the_proposer_cannot_actuate():
    """A text check, because 'tier 2 never actuates' must be a property of the file."""
    banned = re.compile(r"\b(subprocess|os\.system|os\.popen|os\.remove|os\.unlink|shutil\.rmtree|exec\(|eval\()")
    for f in ("propose.py", "schema.py", "evidence.py", "client.py"):
        src = open(os.path.join(AGENT, f), errors="replace").read()
        body = src.split('"""', 2)[2] if src.count('"""') >= 2 else src      # skip the module docstring
        hits = [m.group(0) for m in banned.finditer(body)]
        if hits:
            raise AssertionError("%s can actuate: %s" % (f, sorted(set(hits))))


def t_the_judge_is_never_the_model():
    src = open(os.path.join(AGENT, "loop.py"), errors="replace").read()
    if "armsmod.grade(" not in src:
        raise AssertionError("the loop does not grade with the mechanical judge")
    # The failure this guards against is one line: the reviewer's answer written into an arm's grade.
    for m in re.finditer(r"""^.*\[["']verdict["']\]\s*=(?!=).*$""", src, re.M):
        line = m.group(0).strip()
        if "rev" in line and "armsmod.grade" not in line and not line.startswith("#"):
            raise AssertionError("the reviewer's answer reaches an arm's grade: %s" % line)
    if not re.search(r"r\[.verdict.\],\s*r\[.note.\]\s*=\s*armsmod\.grade|v,\s*note\s*=\s*armsmod\.grade", src):
        raise AssertionError("the loop does not write the mechanical grade onto the row it reports")


def t_a_review_must_say_where():
    bad = {"verdict": "REJECT", "findings": [], "summary": "looks wrong"}
    if not reviewmod.validate_review(bad):
        raise AssertionError("a REJECT with no finding was accepted")
    bad2 = {"verdict": "APPROVE", "findings": [{"severity": "critical", "where": "x", "what": "y", "why": "z"}],
            "summary": "fine"}
    if not reviewmod.validate_review(bad2):
        raise AssertionError("an APPROVE carrying a critical finding was accepted")
    bad3 = {"verdict": "REVISE", "findings": [{"severity": "major", "what": "y", "why": "z"}], "summary": "s"}
    if not any("where" in e for e in reviewmod.validate_review(bad3)):
        raise AssertionError("a finding with no location was accepted")
    good = {"verdict": "APPROVE", "findings": [{"severity": "minor", "where": "loop.py:1", "what": "a", "why": "b"}],
            "summary": "ok"}
    if reviewmod.validate_review(good):
        raise AssertionError("a well formed review was refused: %s" % reviewmod.validate_review(good))


def t_nothing_about_the_endpoint_is_in_the_tree():
    """The repo mirrors publicly within minutes, so neither the host nor a key may be committed."""
    host = re.compile(r"nllei\d|nlgrs\d|grskg\d|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+", re.I)
    keyish = re.compile(r"sk-[A-Za-z0-9_\-]{12,}")
    # It scanned agent/*.py only, and tier 2b found what that misses: the mutation script sitting beside
    # the tests carried an estate-shaped hostname, so the change whose stated property is that nothing
    # about the endpoint is in the tree published the naming scheme itself. Everything the agent work
    # added is scanned now, whatever its extension (12 September 2026).
    bad = []
    scan = [os.path.join(r, f) for r, _, fs in os.walk(AGENT) for f in fs if not f.endswith(".pyc")]
    scan += [os.path.join(TOOLS, "tests", f) for f in ("test_agent_contract.py", "mutate_agent.sh")]
    scan += [os.path.join(REPO, "v2", "docs", "AGENTIC-SYSTEM.md")]
    for path in scan:
        if not os.path.exists(path):
            continue
        txt = open(path, errors="replace").read()
        for pat, what in ((host, "an estate host or a private address"), (keyish, "something shaped like a key")):
            for m in pat.finditer(txt):
                bad.append("%s: %s (%s)" % (os.path.basename(path), m.group(0)[:20], what))
    if bad:
        raise AssertionError("the tree names infrastructure it must not: %s" % bad)


def t_the_client_carries_no_default_endpoint_or_key():
    src = open(os.path.join(AGENT, "client.py"), errors="replace").read()
    for m in re.finditer(r'MESHSAT_LLM_(BASE|KEY|MODEL)[^\n]*', src):
        line = m.group(0)
        if re.search(r'(get|environ)\([^)]*MESHSAT_LLM_(BASE|KEY)[^)]*,\s*["\']', line):
            raise AssertionError("client.py carries a default for the endpoint or the key: %s" % line)
    if "http://" in src or "https://" in src:
        raise AssertionError("client.py names a URL")


def t_the_client_refuses_a_config_anyone_can_read():
    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as fh:
        fh.write("MESHSAT_LLM_BASE=x\nMESHSAT_LLM_KEY=y\nMESHSAT_LLM_MODEL=z\n")
        p = fh.name
    try:
        os.chmod(p, 0o644)
        try:
            client.load_config(p)
        except client.Infra as e:
            if "600" not in str(e):
                raise AssertionError("refused for the wrong reason: %s" % e)
        else:
            raise AssertionError("a world-readable config holding a key was accepted")
        os.chmod(p, 0o600)
        cfg = client.load_config(p)
        if cfg["MESHSAT_LLM_MODEL"] != "z":
            raise AssertionError("a 600 config was not read: %s" % cfg)
    finally:
        os.unlink(p)


def t_a_missing_config_is_infra_fail_and_never_a_fallback():
    try:
        client.load_config(os.path.join(tempfile.gettempdir(), "meshsat-no-such-agent-config.env"))
    except client.Infra:
        return
    raise AssertionError("a missing config did not raise Infra")


def t_no_gate_or_chain_imports_the_agent():
    """A model may inform a proposal. It may never be on the path that judges a board."""
    globs = ("check_pcb_*.py", "*_gate.py", "hardset.py", "verdict.py", "impedance_check.py", "dc_drop.py",
             "intent_checks.py", "check_contracts.py", "verify_deliverable.py", "place_audit.py", "routeflow.py",
             "arms.py", "bench_compare.py", "finish*.sh", "full*.sh", "route_*.sh", "drc.sh", "quality_pass.sh")
    hits = []
    for pat in globs:
        for path in glob.glob(os.path.join(TOOLS, pat)):
            txt = open(path, errors="replace").read()
            for m in re.finditer(r"^(?!\s*#).*\b(agent\.client|agent\.propose|agent\.review|agent/loop|agent/propose|import propose|import review)\b.*$", txt, re.M):
                hits.append("%s: %s" % (os.path.basename(path), m.group(0).strip()[:100]))
    if hits:
        raise AssertionError("a gate or chain reaches the agent: %s" % hits)


def t_the_budget_is_counted_in_work():
    """Calls and tokens, never seconds, and counted for the RUN rather than for one conversation.

    Tier 2b found the difference: one loop run builds several Clients (the proposer, each draft, each
    review cycle), so a per-instance cap let a run with revisions spend several multiples of the number
    the document states. The counters are module level now and every HTTP attempt is counted, including
    the retries, so a retrying endpoint cannot spend the budget invisibly.
    """
    src = open(os.path.join(AGENT, "client.py"), errors="replace").read()
    if "max_calls" not in src or "max_tokens_total" not in src:
        raise AssertionError("the client has no work budget")
    if not re.search(r'SPENT\["calls"\]\s*>=\s*self\.max_calls', src):
        raise AssertionError("the call budget is declared and not enforced against the run's own counter")
    if not re.search(r'SPENT\["requests"\]\s*\+=', src):
        raise AssertionError("retries are not counted, so a retrying endpoint spends the budget invisibly")
    if not re.search(r'SPENT\["tokens"\]\s*\+=\s*int\(usage\.get\("total_tokens"\)\s*or\s*max_tokens\)', src):
        raise AssertionError("an answer with no usage block leaves the token cap unenforced")
    # the cap is shared across Clients, which is the property the document claims
    c1 = client.Client.__init__
    before = dict(client.SPENT)
    try:
        client.SPENT.update({"calls": 10 ** 9})
        c = client.Client(role="propose", cfg={"MESHSAT_LLM_BASE": "x", "MESHSAT_LLM_KEY": "y",
                                               "MESHSAT_LLM_MODEL": "z"}, max_calls=1)
        try:
            c.ask("a", "b")
        except client.Infra as e:
            if "cap for this run" not in str(e):
                raise AssertionError("a fresh Client did not see the run's spend: %s" % e)
        else:
            raise AssertionError("a fresh Client ignored the run's spend and called anyway")
    finally:
        client.SPENT.update(before)
    assert c1 is client.Client.__init__


def t_every_call_records_what_was_sent_and_what_came_back():
    src = open(os.path.join(AGENT, "client.py"), errors="replace").read()
    for field in ("prompt_sha", "reply_sha", "prompt_tokens"):
        if field not in src:
            raise AssertionError("a call does not record %s, so the ledger cannot prove which bytes were used" % field)


def t_arms_refuses_an_unsafe_arm_name():
    sys.path.insert(0, TOOLS)
    import importlib.util
    sp = importlib.util.spec_from_file_location("armsmod_for_test", os.path.join(TOOLS, "arms.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    for bad in ("../../etc", "Up", "x" * 40, ""):
        if m.safe_name(bad):
            raise AssertionError("arms.py accepts the name %r, which becomes a directory it rmtrees" % bad)
    if not m.safe_name("slack006"):
        raise AssertionError("arms.py refuses a legitimate name")


def t_a_knob_that_never_arrived_is_not_a_measurement():
    """Tier 2b's first real finding, turned into a mechanical guard (12 September 2026).

    The reviewer read a cycle that reported five pairs under a knob and said, correctly, that nothing
    in the result showed the knob had reached the tool. So the pre-router echoes what its process
    received and the runner refuses a row whose arm knob is missing or different: a pair count under a
    knob that never arrived is INFRA_FAIL, never a number.
    """
    import importlib.util
    sp = importlib.util.spec_from_file_location("armsmod_knobs", os.path.join(TOOLS, "arms.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    if m.knobs_arrived({"PAIR_CORRIDOR_SLACK": 0.06}, {"PAIR_CORRIDOR_SLACK": "0.06"}):
        raise AssertionError("a knob that did arrive was called missing")
    if not m.knobs_arrived({"PAIR_CORRIDOR_SLACK": 0.06}, {"PAIR_CORRIDOR_SLACK": "0.12"}):
        raise AssertionError("a knob the tool saw at a DIFFERENT value was accepted")
    if not m.knobs_arrived({"PAIR_CORRIDOR_SLACK": 0.06}, {}):
        raise AssertionError("a run with no knob echo at all was accepted")
    row = {"arm": "x", "error": m.knobs_arrived({"PAIR_CORRIDOR_SLACK": 0.06}, {}),
           "predict": {"op": ">=", "value": 1}}
    if m.grade(row)[0] != "INFRA_FAIL":
        raise AssertionError("a row whose knob never arrived was graded as a measurement: %s" % (m.grade(row),))
    src = open(os.path.join(TOOLS, "pair_preroute.py"), errors="replace").read()
    if "knobs this process received" not in src:
        raise AssertionError("the pre-router no longer echoes the knobs it received, so the guard cannot fire")


def t_a_tool_change_is_proved_in_a_worktree_never_the_working_tree():
    """Tier 2's third product. The plan's words are 'a git worktree at a stated sha and never a file copy'."""
    src = open(os.path.join(AGENT, "patch.py"), errors="replace").read()
    body = src.split('"""', 2)[2]
    if "worktree" not in body:
        raise AssertionError("patch.py does not cut a worktree")
    if "copytree" in body or "shutil.copy" in body:
        raise AssertionError("patch.py copies the repository instead of cutting a worktree")
    if "reserved._matches" not in body and "reserved.load" not in body:
        raise AssertionError("patch.py does not read the diff against the never-auto floor")
    if "cwd=wt" not in body:
        raise AssertionError("patch.py does not run the suite inside the worktree")
    for m in re.finditer(r'run\(\["git", "-C", REPO,[^\]]*"(commit|checkout|apply|reset|merge)"', body):
        raise AssertionError("patch.py runs %s against the real repository, not the worktree" % m.group(1))
    if 'worktree", "remove"' not in body:
        raise AssertionError("patch.py does not remove its worktree")


def t_the_reviewers_refusal_gates_the_write_up():
    """A verdict file reading PASS over a refused entry is a claim the code does not make good on."""
    src = open(os.path.join(AGENT, "loop.py"), errors="replace").read()
    if 'refused = bool(rev) and rev["verdict"] != "APPROVE"' not in src:
        raise AssertionError("the loop does not compute whether the reviewer refused")
    if "verdict.FAIL if refused" not in src:
        raise AssertionError("a refused write-up does not make the cycle FAIL")


def t_a_row_belongs_to_the_cycle_that_produced_it():
    """The arm name is chosen by the model, so name alone cannot identify this cycle's measurement."""
    src = open(os.path.join(AGENT, "loop.py"), errors="replace").read()
    if "after_seq" not in src or "ledger.head(result)" not in src:
        raise AssertionError("rows are selected by name alone, so an older row with the same name would be read")


def t_a_flag_given_a_threshold_is_refused():
    """The first arm an automated tier 2 ever wrote for board B, turned into a rule.

    It proposed PAIR_OWN_CLEAR=0.09, reasoning carefully in millimetres about a 3 to 38 micrometre miss.
    The tool reads that name as `os.environ.get("PAIR_OWN_CLEAR", "1") != "0"`, so 0.09 sets it ON,
    which is its default: the arm could only ever measure nothing, and a null result reads exactly like
    a knob that does not pay. The type is in the source, so the validator reads it from the source.
    """
    types = schema.knob_types()
    if not types.get("PAIR_OWN_CLEAR", {}).get("type", "").startswith("flag"):
        raise AssertionError("PAIR_OWN_CLEAR is no longer typed as a flag: %s" % types.get("PAIR_OWN_CLEAR"))
    if types.get("PAIR_CORRIDOR_SLACK", {}).get("type") != "number":
        raise AssertionError("PAIR_CORRIDOR_SLACK is no longer typed as a number")
    if types.get("PAIR_VIA_CANDS", {}).get("type") != "integer":
        raise AssertionError("PAIR_VIA_CANDS is no longer typed as an integer")
    p = json.loads(json.dumps(GOOD)); p["arms"][0]["env"] = {"PAIR_OWN_CLEAR": "0.09"}
    _refuses(p, "FLAG")
    q = json.loads(json.dumps(GOOD)); q["arms"][0]["env"] = {"PAIR_OWN_CLEAR": 0}
    ok, errs, _ = schema.validate(q, TEMPLATE)
    if not ok:
        raise AssertionError("a flag given a real flag value was refused: %s" % errs)


def t_the_pair_count_alone_is_not_the_objective():
    """An arm that lowers a legality bar buys pairs with copper the board cannot have.

    Nothing in a pair count says so, which makes the count gameable, and the first automated proposal
    for board B reached for exactly such a knob. The DRC runs on the board the arm laid and its hard
    count travels in the row; an arm above the baseline is ILLEGAL whatever its number, and a board
    whose DRC could not be read is UNMEASURED rather than assumed clean.
    """
    import importlib.util
    sp = importlib.util.spec_from_file_location("armsmod_legal", os.path.join(TOOLS, "arms.py"))
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    base = {"pairs": 40, "predict": {"op": ">=", "value": 32, "basis": "b"}}
    if m.grade(dict(base, hard=7), 0)[0] != "ILLEGAL":
        raise AssertionError("an arm that laid hard violations was graded on its pair count")
    if m.grade(dict(base, hard=0), 0)[0] != "MET":
        raise AssertionError("a legal arm that met its prediction was not graded MET")
    if m.grade(dict(base, drc_error="kicad-cli died"), 0)[0] != "UNMEASURED":
        raise AssertionError("an unreadable DRC was assumed clean")
    src = open(os.path.join(TOOLS, "arms.py"), errors="replace").read()
    if "drc.sh" not in src or "hardset.py" not in src:
        raise AssertionError("arms.py no longer measures the legality of what the arm laid")
