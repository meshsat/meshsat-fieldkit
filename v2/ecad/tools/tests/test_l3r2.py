"""Layer 3's second issue (L3-R2) is generated from the registry, and its prepared restatements apply only on coherent
combinations (MESHSAT-1357, 30 September 2026; second round, after the independent check CHECK-1; third round, the
six-row table of the owner's instruction D-23).

`v2/docs/handover/layer3/render_l3r2.py` renders REQUIREMENTS-L3-R2.md, OWNER-DECISIONS-L3.md and L3-RECONCILIATION.md
from the requirements registry, `l3r2.yaml` and H3's registry as released. These tests hold the three pages to what the
inputs render (a hand edit is refused, on a copy), keep them free of unqualified claims and dash characters, hold the
frozen H3 digest to the released ZIP, run the prepared owner-decision scripts on a COPY of the registry, refuse the
incoherent combinations CHECK-1 found (B1), keep the gate from reading the target unambiguous on one, and stay green
whatever rows the tree's registry has already decided (CHECK-1, minor 2). The third round adds the table's form (six
rows, each with options, recommendation, quantified consequences and dependencies, every link resolving), row L3-OD6's
held figures and its coverage targets read only from filled figures, and the both-kept lid flagged and recorded as a
conflict. Nothing here writes into the tree.
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
DASHES = ("\u2013", "\u2014")
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
    for s in ("apply_l3r2_session.py", "apply_l3r2_d23.py", "apply_layer_status_l3.py", "apply_layer_status_l3_r3.py"):
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
    for row in ("L3-OD1", "L3-OD2", "L3-OD4", "L3-OD6"):
        try:
            C.hold({"check": False, "registry": C.E.REGISTRY}, row)
        except C.E.Refused as e:
            assert "held" in str(e), str(e)
        else:
            raise AssertionError("held row %s would be written into the tree's registry" % row)


def _copy_registry():
    d = tempfile.mkdtemp(prefix="l3r2-reg-")
    p = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(os.path.join(TOOLS, "pcb_requirements.yaml"), p)
    ev = os.path.join(d, "basis.md")
    open(ev, "w", encoding="utf-8").write("TEST BASIS (a fixture, not the energy basis): the band %s; the array 1100 Wp, "
                                          "entry 80 A. Coverage 90: 3000 Wh usable, 4000 Wh nominal, 20.5 kg, 12.5 "
                                          "litres. Coverage 50: 900 Wh usable, 1100 Wh nominal, 6.5 kg, 3.5 litres.\n" % BAND)
    import yaml
    open(os.path.join(d, "table.yaml"), "w", encoding="utf-8").write(yaml.safe_dump({"rows": [
        {"id": "cov-90", "option": "coverage", "share": 90, "usable_wh": 3000, "nominal_wh": 4000, "mass_kg": 20.5,
         "volume_l": 12.5, "fits": "NO", "evidence": ev},
        {"id": "cov-50", "option": "coverage", "share": 50, "usable_wh": 900, "nominal_wh": 1100, "mass_kg": 6.5,
         "volume_l": 3.5, "fits": "YES", "evidence": ev},
        {"id": "cov-80", "option": "coverage", "share": 80, "usable_wh": None, "nominal_wh": None, "mass_kg": None,
         "volume_l": None, "fits": None, "evidence": None}]}))
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
        _step(script, option, reg, *_extra(script, option, ev))


def _extra(script, option, ev, share="90"):
    if script == "od_l3_4.py" and option == "adopt": return ["--band", BAND, "--band-evidence", ev, "--push-n", "20"]
    if script == "od_l3_3.py" and option == "keep": return ["--array-wp", "1100", "--entry-a", "80", "--evidence", ev]
    if script == "od_l3_6.py" and option == "coverage":
        return ["--share", share, "--table", os.path.join(os.path.dirname(ev), "table.yaml")]
    return []


RECOMMENDED = [("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p"),
               ("L3-OD4", "od_l3_4.py", "adopt"), ("L3-OD5", "od_l3_5.py", "reading-c"), ("L3-OD6", "od_l3_6.py", "mean-day")]


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
    RL = _render_mod()
    x = lambda o: (o, "D-99", "2026-10-01", "")
    base = {"L3-OD1": x("approve"), "L3-OD2": x("qmx-out"), "L3-OD3": x("2s2p"), "L3-OD4": x("adopt")}
    assert RL.coherent(dict(base, **{"L3-OD6": x("mean-day")}))[1], "the recommended set reads incoherent"
    for bad in ({"L3-OD6": x("coverage")}, {"L3-OD2": x("both-kept")}, {"L3-OD3": x("keep")}):
        assert not RL.coherent(dict(base, **bad))[1], "an adopted band beside %s reads coherent" % bad
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


def t_l3r2_the_table_has_six_rows_each_with_its_parts():
    """D-23: the six-row table gives each row its options, the recommendation, quantified consequences and dependencies,
    carries board A's R11 as two results, and every relative link on the pages resolves (the renderer refuses one that
    does not)."""
    RL = _render_mod()
    data = RL.load_data()
    rows = data["decisions"]
    assert [d["id"] for d in rows] == ["L3-OD%d" % i for i in range(1, 7)], "the table is not the six rows"
    for d in rows:
        for k in ("question", "recommendation", "consequences", "dependencies", "affected"):
            assert str(d.get(k) or "").strip(), "%s has no %s" % (d["id"], k)
        assert d.get("options"), "%s has no options" % d["id"]
    for rid in ("L3-OD1", "L3-OD2", "L3-OD4", "L3-OD6"):
        r11 = next(d for d in rows if d["id"] == rid).get("r11") or {}
        assert r11.get("held") and r11.get("drafted"), "%s does not carry R11 as two results" % rid
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    for rid in ("L3-OD1", "L3-OD2"):
        assert "CANNOT MEET M1" in [l for l in page.split("\n") if l.startswith("| %s |" % rid)][0], \
            "%s's options do not flag the option that cannot meet M1" % rid
    for name in RL.PAGES.values():
        RL.check_links(name, open(os.path.join(L3, name), encoding="utf-8").read())


def t_l3r2_row6_figures_are_held_until_filled():
    """D-23: row L3-OD6's figures stay placeholders bound to the energy basis; a coverage target is applied only from
    filled figures (a fixture here), and a held or unknown target is refused."""
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    RL = _render_mod()
    q = next(d for d in RL.load_data()["decisions"] if d["id"] == "L3-OD6")
    if not RL.load_data().get("energy_basis"):
        for r in q["quantified"]["rows"]:
            assert all(r.get(k) is None for k in ("usable_wh", "nominal_wh", "mass_kg", "volume_l", "fits")), \
                "row L3-OD6's %s carries a figure before the checked basis" % r["id"]
    d, reg, ev = _copy_registry()
    if "L3-OD6" in _decided(reg): raise Skip("row L3-OD6 is decided in this tree")
    out = _step("od_l3_6.py", "coverage", reg, "--share", "90", expect=2)          # the tree's table: HELD
    assert "HELD" in out, out
    _step("od_l3_6.py", "coverage", reg, *_extra("od_l3_6.py", "coverage", ev, "80"), expect=2)   # fixture, held target
    _step("od_l3_6.py", "coverage", reg, *_extra("od_l3_6.py", "coverage", ev, "70"), expect=2)   # no such target
    _step("od_l3_6.py", "coverage", reg, expect=2)                                 # no --share


def t_l3r2_a_coverage_target_that_does_not_fit_is_a_conflict():
    """A coverage target whose store does not fit records an open conflict; row L3-OD1 applied after it keeps the target
    in REQ-072; row L3-OD4's band is refused beside it; a target that fits leaves a note and no conflict."""
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    import yaml
    d, reg, ev = _copy_registry()
    if any(r in _decided(reg) for r in ("L3-OD1", "L3-OD6")): raise Skip("rows L3-OD1 or L3-OD6 are decided in this tree")
    n0 = len(yaml.safe_load(open(reg, encoding="utf-8"))["records"])
    _chain([("L3-OD6", "od_l3_6.py", "coverage")], reg, ev)
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    cfl = [r for r in y["records"] if r.get("kind") == "conflict" and r.get("status") == "CONFLICT_OPEN"
           and "historical coverage" in " ".join(str(r["statement"]).split())]
    assert len(cfl) == 1 and len(y["records"]) == n0 + 1, "no open conflict for a target that does not fit"
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p")], reg, ev)
    r072 = next(r for r in yaml.safe_load(open(reg, encoding="utf-8"))["records"] if r["id"] == "REQ-072")
    for f in ("statement", "acceptance"):
        assert "at least 90 percent" in " ".join(str(r072[f]).split()), "row L3-OD1 dropped the coverage target from REQ-072's %s" % f
    out = _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)
    assert "coverage" in out, out
    d2, reg2, ev2 = _copy_registry()
    _step("od_l3_6.py", "coverage", reg2, *_extra("od_l3_6.py", "coverage", ev2, "50"))
    y2 = yaml.safe_load(open(reg2, encoding="utf-8"))
    assert len(y2["records"]) == n0, "a target that fits recorded a conflict"
    r072 = next(r for r in y2["records"] if r["id"] == "REQ-072")
    assert "which fits the case" in " ".join(str(r072.get("notes")).split()), "the fitting target's figures are not in REQ-072's notes"


def t_l3r2_both_lid_items_kept_is_flagged_and_recorded():
    """Row L3-OD2 both-kept: no function leaves the kit, M1 cannot be met, an open conflict is recorded, and row L3-OD4
    adopts no band for it (reject stands)."""
    need(os.path.join(COND, "od_l3_2.py"), "the conditional scripts are not in this tree")
    import yaml
    d, reg, ev = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "both-kept"), ("L3-OD3", "od_l3_3.py", "2s2p")], reg, ev)
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    assert any(r.get("status") == "CONFLICT_OPEN" and "both approved lid items kept" in " ".join(str(r["statement"]).split())
               for r in y["records"]), "both lid items kept records no conflict"
    _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)
    if "L3-OD4" not in _decided(reg): _step("od_l3_4.py", "reject", reg)

