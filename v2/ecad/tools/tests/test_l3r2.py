"""Layer 3's second issue (L3-R2) is generated from the registry, and its prepared restatements apply only on coherent
combinations (MESHSAT-1357, 30 September 2026; second round, after the independent check CHECK-1).

`v2/docs/handover/layer3/render_l3r2.py` renders REQUIREMENTS-L3-R2.md, OWNER-DECISIONS-L3.md and L3-RECONCILIATION.md
from the requirements registry, `l3r2.yaml` and H3's registry as released. These tests hold the three pages to what the
inputs render (a hand edit is refused, on a copy), keep them free of unqualified claims and dash characters, hold the
frozen H3 digest to the released ZIP, run the prepared owner-decision scripts on a COPY of the registry, refuse the
incoherent combinations CHECK-1 found (B1), keep the gate from reading the target unambiguous on one, and stay green
whatever rows the tree's registry has already decided (CHECK-1, minor 2). Nothing here writes into the tree.
"""
import os, re, shutil, subprocess, sys, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
L3 = os.path.join(ROOT, "v2", "docs", "handover", "layer3")
REC = os.path.join(ROOT, "v2", "docs", "records", "l3r2")
COND = os.path.join(REC, "conditional")
sys.dont_write_bytecode = True   # the renderer lives in v2/docs/handover/layer3: no cache is left there
sys.path.insert(0, TOOLS)
sys.path.insert(0, L3)
from harness import need, Skip  # noqa: E402
import claims_check as CC  # noqa: E402

RENDER = os.path.join(L3, "render_l3r2.py")
DASHES = ("–", "—")
BAND = "30 to 50 degrees of slope, facing between south and 15 degrees west of south"


def _render_mod():
    need(RENDER, "the L3-R2 renderer is not in this tree")
    import render_l3r2 as RL
    return RL


def _run(args, cwd=None):
    return subprocess.run([sys.executable] + args, capture_output=True, text=True, cwd=cwd or tempfile.gettempdir())


def t_l3r2_pages_are_generated_not_hand_kept():
    RL = _render_mod()
    pages = RL.render_all()
    for name, body in pages.items():
        p = os.path.join(L3, name)
        assert os.path.exists(p) and open(p, encoding="utf-8").read() == body, \
            "%s differs from what the registry and l3r2.yaml render: run render_l3r2.py" % name


def t_l3r2_check_refuses_a_hand_edited_copy():
    _render_mod()
    d = tempfile.mkdtemp(prefix="l3r2-pages-")
    for n in ("REQUIREMENTS-L3-R2.md", "OWNER-DECISIONS-L3.md", "L3-RECONCILIATION.md"):
        shutil.copy(os.path.join(L3, n), os.path.join(d, n))
    good = _run([RENDER, "--check", "--out-dir", d])
    assert good.returncode == 0, "--check refused an untouched copy:\n%s" % (good.stdout + good.stderr)[-400:]
    open(os.path.join(d, "OWNER-DECISIONS-L3.md"), "a", encoding="utf-8").write("\n<!-- a hand edit -->\n")
    bad = _run([RENDER, "--check", "--out-dir", d])
    assert bad.returncode == 1, "--check did not refuse a hand-edited copy (exit %d)" % bad.returncode


def t_l3r2_pages_state_requirements_not_claims():
    _render_mod()
    files = ["v2/docs/handover/layer3/%s" % n for n in ("REQUIREMENTS-L3-R2.md", "L3-RECONCILIATION.md",
                                                         "OWNER-DECISIONS-L3.md", "OWNER-INSTRUCTION-2026-09-30.md")]
    n, bad = CC.check(files)
    assert not bad, "an L3-R2 page carries an unqualified claim: %s" % bad[:3]


def t_l3r2_carries_no_dash_character():
    paths = [os.path.join(L3, f) for f in os.listdir(L3)] if os.path.isdir(L3) else []
    for base in (REC, COND):
        if os.path.isdir(base): paths += [os.path.join(base, f) for f in os.listdir(base) if f.endswith((".py", ".md", ".out"))]
    if not paths: raise Skip("no L3-R2 files in this tree")
    for p in paths:
        if os.path.isfile(p):
            t = open(p, encoding="utf-8", errors="replace").read()
            assert not any(d in t for d in DASHES), "%s carries a dash character" % os.path.relpath(p, ROOT)


def t_l3r2_no_case_is_called_adverse_on_the_pages():
    """D-22: 'Define adverse.' Until the energy basis names its cases, no L3 page calls a case adverse or typical, the
    owner's own quoted words and the explanation of that rule aside."""
    _render_mod()
    for n in ("REQUIREMENTS-L3-R2.md", "L3-RECONCILIATION.md", "OWNER-DECISIONS-L3.md"):
        for line in open(os.path.join(L3, n), encoding="utf-8"):
            if re.search(r"\badverse\b", line, re.I):
                assert "typical or adverse until the basis names" in line or "Define 'adverse" in line, \
                    "%s calls a case adverse: %s" % (n, line[:160])


def t_l3r2_h3_digest_is_the_released_registry():
    RL = _render_mod()
    data = RL.load_data()
    z = os.path.join(ROOT, data["h3"]["zip"])
    need(z, "the H3 release is not in this tree (a snapshot does not carry an earlier one)")
    assert open(RL.DIGEST, encoding="utf-8").read() == RL.freeze(data), "h3_registry_digest.json is not H3.zip's registry"


def t_l3r2_every_named_decision_script_and_record_exists():
    RL = _render_mod()
    data = RL.load_data()
    import rules_lib as R
    req = R.load_requirements()
    ids = {r["id"] for r in req["records"]}
    later = set(data.get("impacts") or {})
    for d in data["decisions"]:
        assert os.path.exists(os.path.join(COND, d["script"])), "%s names %s, which is not in conditional/" % (d["id"], d["script"])
    for pr in data["proposals"]:
        for x in pr.get("affects") or []:
            assert x in ids or x in later, "%s affects %s, which neither the registry nor a conditional change holds" % (pr["id"], x)
    for c in data["closure"]:
        if c.get("record"): assert c["record"] in ids, "%s names %s, not a record" % (c["id"], c["record"])


def t_l3r2_session_scripts_refuse_a_second_run():
    for s in ("apply_l3r2_session.py", "apply_layer_status_l3.py"):
        p = os.path.join(REC, s)
        need(p, "%s is not in this tree" % s)
        r = _run([p, "--check"])
        assert r.returncode == 2 and ("already" in r.stdout or "has run" in r.stdout), \
            "%s did not refuse a second run:\n%s" % (s, (r.stdout + r.stderr)[-300:])


def t_l3r2_a_held_row_is_never_written_into_the_tree():
    """D-22 holds rows L3-OD1, L3-OD2 and L3-OD4: while l3r2.yaml names no filed energy basis, cond.hold refuses a write
    to the tree's registry (asked directly, so nothing is written)."""
    need(os.path.join(COND, "cond.py"), "the conditional scripts are not in this tree")
    sys.path.insert(0, COND)
    import cond as C
    data = C.l3data()
    if data.get("energy_basis"): raise Skip("the energy basis is filed: the hold is lifted")
    try:
        C.hold({"check": False, "registry": C.E.REGISTRY}, "L3-OD1")
    except C.E.Refused as e:
        assert "held" in str(e), str(e)
    else:
        raise AssertionError("a held row would be written into the tree's registry")


def _copy_registry():
    d = tempfile.mkdtemp(prefix="l3r2-reg-")
    p = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(os.path.join(TOOLS, "pcb_requirements.yaml"), p)
    ev = os.path.join(d, "basis.md")
    open(ev, "w", encoding="utf-8").write("TEST BASIS (a fixture, not the energy basis): the band %s; the array 1100 Wp, "
                                          "entry 80 A.\n" % BAND)
    return d, p, ev


def _decided(reg):
    import yaml
    d = yaml.safe_load(open(reg, encoding="utf-8"))
    return {str(r["decides"]).split(":")[0]: str(r["decides"]).split(":")[1] for r in d["owner_rulings"] if r.get("decides")}


def _step(script, option, reg, *extra, expect=0):
    r = _run([os.path.join(COND, script), "--option", option, "--words", "test words", "--date", "2026-10-01",
              "--registry", reg] + list(extra))
    assert r.returncode == expect, "%s --option %s exit %d (expected %d):\n%s" % (
        script, option, r.returncode, expect, (r.stdout + r.stderr)[-500:])
    return r.stdout


def _chain(steps, reg, ev):
    """Apply each (row, script, option) on the copy unless the row is already decided there; a row decided with another
    option makes the chain not applicable (Skip), so the test stays green in any decided state."""
    for row, script, option in steps:
        dec = _decided(reg)
        if row in dec:
            if dec[row] != option: raise Skip("%s is decided %s in this tree; the chain needs %s" % (row, dec[row], option))
            continue
        extra = []
        if script == "od_l3_4.py" and option == "adopt": extra = ["--band", BAND, "--band-evidence", ev, "--push-n", "20"]
        if script == "od_l3_3.py" and option == "keep": extra = ["--array-wp", "1100", "--entry-a", "80", "--evidence", ev]
        _step(script, option, reg, *extra)


RECOMMENDED = [("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p"),
               ("L3-OD4", "od_l3_4.py", "adopt"), ("L3-OD5", "od_l3_5.py", "reading-c")]


def t_l3r2_a_coherent_chain_applies_on_a_copy_and_renders():
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain(RECOMMENDED, reg, ev)
    import yaml
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    assert any(c["id"] == "M-02" for c in y["closed_items"]), "M-02 is not closed once rows 1 to 4 are decided"
    r072 = next(r for r in y["records"] if r["id"] == "REQ-072")
    acc = " ".join(r072["acceptance"].split())
    assert "400 Wp at STC" in acc and "(row L3-OD3)" not in acc, "REQ-072 does not name the one array row L3-OD3 decided"
    RL = _render_mod()
    pages = RL.render_all(registry=reg)
    assert "DECIDED" in pages["OWNER-DECISIONS-L3.md"], "the decided rows do not render as decided"
    assert "| Target unambiguous | NOT MET |" in pages["REQUIREMENTS-L3-R2.md"], \
        "the target reads unambiguous with no energy basis filed"


def t_l3r2_the_incoherent_combinations_are_refused():
    """CHECK-1, B1: approve, qmx-out, keep, adopt, reading-c left two rulings on the array and a 2S2P band on a 1600 Wp
    array; 1S4P with a band has no grid; keep needs the basis's figures; row 2 needs row 1 approved."""
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain(RECOMMENDED[:2], reg, ev)
    dec = _decided(reg)
    if "L3-OD3" in dec: raise Skip("row L3-OD3 is decided in this tree")
    _step("od_l3_3.py", "keep", reg, expect=2)                                   # no basis figures: refused
    _chain([("L3-OD3", "od_l3_3.py", "keep")], reg, ev)
    out = _step("od_l3_4.py", "adopt", reg, "--band", BAND, "--band-evidence", ev, "--push-n", "20", expect=2)
    assert "2s2p" in out, out
    d2, reg2, ev2 = _copy_registry()
    _chain(RECOMMENDED[:2] + [("L3-OD3", "od_l3_3.py", "1s4p")], reg2, ev2)
    _step("od_l3_4.py", "adopt", reg2, "--band", BAND, "--band-evidence", ev2, "--push-n", "20", expect=2)
    d3, reg3, ev3 = _copy_registry()
    if "L3-OD1" not in _decided(reg3):
        _chain([("L3-OD1", "od_l3_1.py", "reject")], reg3, ev3)
        _step("od_l3_2.py", "tablet-out", reg3, expect=2)


def t_l3r2_the_gate_reads_an_incoherent_set_as_not_unambiguous():
    """A registry whose rulings name an incoherent combination (written by hand here, since the scripts refuse it) keeps
    the gate's first condition NOT MET, even with an energy basis filed."""
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain(RECOMMENDED[:4], reg, ev)
    t = open(reg, encoding="utf-8").read()
    t2 = re.sub(r'decides: "L3-OD3:2s2p"', 'decides: "L3-OD3:keep"', t, count=1)
    if t2 == t: raise Skip("row L3-OD3 is not decided 2s2p here")
    open(reg, "w", encoding="utf-8").write(t2)
    RL = _render_mod()
    import yaml
    req = yaml.safe_load(t2)
    data = RL.load_data()
    data["energy_basis"] = None
    dec = RL.decided(req, data)
    why, ok = RL.coherent(dec)
    assert not ok and why, "the incoherent set reads coherent"
    g = RL.gate(req, dec, data, RL.load_h3())
    assert g[0][1] is False, "the gate reads the target unambiguous on an incoherent set"


def t_l3r2_the_other_answers_apply_on_a_copy():
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "tablet-out"), ("L3-OD3", "od_l3_3.py", "keep"),
            ("L3-OD4", "od_l3_4.py", "reject"), ("L3-OD5", "od_l3_5.py", "measure")], reg, ev)
    d2, reg2, ev2 = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-outside"), ("L3-OD3", "od_l3_3.py", "1s4p"),
            ("L3-OD5", "od_l3_5.py", "cells")], reg2, ev2)
