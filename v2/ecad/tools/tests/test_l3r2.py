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
    for s in ("apply_l3r2_session.py", "apply_l3r2_d23.py", "apply_l3r2_d24.py", "apply_l3r2_r3b.py", "apply_layer_status_l3.py",
              "apply_layer_status_l3_r3.py", "apply_layer_status_l3_r3b.py"):
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
            assert "held (%s)" % ("D-23, D-24" if row == "L3-OD6" else "D-22, D-24") in str(e), str(e)   # CHECK-2 minor 2
        else:
            raise AssertionError("held row %s would be written into the tree's registry" % row)


FIX = {"mean-day": ("619.0", "4S13P", 76, "916.6", "3.80", "1.3", "1.7", "0.89", "0.90"),
       "50": ("981.8", "4S26P", 128, "1543.7", "6.40", "2.3", "2.9", "1.42", "1.52")}


def _rows():
    """A fixture of row L3-OD6's table (not the basis): the mean day in TYP carried by the tablet-out and QMX-out lids,
    in WAB by the QMX-out lid only, and no coverage target carried by any lid."""
    out = []
    for basis in ("mean-day", "50", "80", "95"):
        for build in ("TYP", "WAB"):
            f = FIX.get(basis, FIX["50"])
            fits = (["tablet-out", "qmx-out"] if build == "TYP" else ["qmx-out"]) if basis == "mean-day" else []
            out.append({"id": "%s-%s" % (basis if basis == "mean-day" else "cov-" + basis, build),
                        "option": "mean-day" if basis == "mean-day" else "coverage",
                        "share": None if basis == "mean-day" else int(basis), "build": build,
                        "usable_wh": f[0], "lid_block": f[1], "cells": f[2], "nominal_wh": f[3], "mass_kg": f[4],
                        "volume_cyl_l": f[5], "volume_box_l": f[6], "x_wh": f[7], "x_cells": f[8], "fits": fits,
                        "evidence": "fixture B"})
    return out


def _copy_registry():
    d = tempfile.mkdtemp(prefix="l3r2-reg-")
    p = os.path.join(d, "pcb_requirements.yaml")
    shutil.copy(os.path.join(TOOLS, "pcb_requirements.yaml"), p)
    ev = os.path.join(d, "basis.md")
    open(ev, "w", encoding="utf-8").write('TEST BASIS (a fixture, not the energy basis): the band "%s"; the array 1100 Wp, '
                                          'entry 80 A.\n' % BAND)
    import yaml
    open(os.path.join(d, "table.yaml"), "w", encoding="utf-8").write(yaml.safe_dump({"rows": _rows()}))
    return d, p, ev


def _decided(reg):
    import yaml
    d = yaml.safe_load(open(reg, encoding="utf-8"))
    return {str(r["decides"]).split(":")[0]: str(r["decides"]).split(":")[1] for r in d["owner_rulings"]
            if ":" in str(r.get("decides") or "")}


def _step(script, option, reg, *extra, expect=0):
    r = _run([os.path.join(COND, script), "--option", option, "--words", "test words", "--date", "2026-10-01",
              "--registry", reg] + list(extra))
    assert r.returncode == expect, "%s --option %s exit %d (expected %d):\n%s" % (
        script, option, r.returncode, expect, (r.stdout + r.stderr)[-500:])
    return r.stdout


def _extra(script, option, ev, share="50", build="TYP"):
    table = os.path.join(os.path.dirname(ev), "table.yaml")
    if script == "od_l3_4.py" and option == "adopt": return ["--band", BAND, "--band-evidence", ev, "--push-n", "20"]
    if script == "od_l3_3.py" and option == "keep": return ["--array-wp", "1100", "--entry-a", "80", "--evidence", ev]
    if script == "od_l3_6.py":
        return ["--build", build] + (["--share", share] if option == "coverage" else []) + ["--table", table]
    if script == "od_l3_2.py": return ["--table", table]
    return []


def _chain(steps, reg, ev):
    """Apply each (row, script, option[, build[, share]]) on the copy unless the row is already decided there; a row
    decided with another option makes the chain not applicable (Skip), so the test stays green in any decided state."""
    for s in steps:
        row, script, option = s[:3]
        dec = _decided(reg)
        if row in dec:
            if dec[row] != option: raise Skip("%s is decided %s in this tree; the chain needs %s" % (row, dec[row], option))
            continue
        kw = {"build": s[3]} if len(s) > 3 else {}
        if len(s) > 4: kw["share"] = s[4]
        _step(script, option, reg, *_extra(script, option, ev, **kw))


def _conflicts(reg, words):
    import yaml
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    return [r["id"] for r in y["records"] if r.get("status") == "CONFLICT_OPEN" and words in " ".join(str(r["statement"]).split())]


# An example chain, not a recommendation: row L3-OD6's recommendation is HELD (CHECK-2 minor 3).
EXAMPLE = [("L3-OD6", "od_l3_6.py", "mean-day", "TYP"), ("L3-OD1", "od_l3_1.py", "approve"),
           ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p"), ("L3-OD4", "od_l3_4.py", "adopt"),
           ("L3-OD5", "od_l3_5.py", "reading-c")]


def t_l3r2_an_example_chain_applies_on_a_copy_and_renders():
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain(EXAMPLE, reg, ev)
    import yaml
    y = yaml.safe_load(open(reg, encoding="utf-8"))
    assert any(c["id"] == "M-02" for c in y["closed_items"]), "M-02 is not closed once rows 1 to 4 are decided"
    r072 = next(r for r in y["records"] if r["id"] == "REQ-072")
    acc = " ".join(r072["acceptance"].split())
    assert "400 Wp at STC" in acc and "(row L3-OD3)" not in acc, "REQ-072 does not name the one array row L3-OD3 decided"
    assert not _conflicts(reg, "weather basis"), "the QMX-out lid carries the mean day in TYP, yet a conflict was recorded"
    RL = _render_mod()
    pages = RL.render_all(registry=reg)
    assert "DECIDED" in pages["OWNER-DECISIONS-L3.md"], "the decided rows do not render as decided"
    assert "| Target unambiguous | NOT MET |" in pages["REQUIREMENTS-L3-R2.md"], \
        "the target reads unambiguous with no energy basis filed"


def t_l3r2_the_band_never_precedes_the_weather_answer():
    """CHECK-2 of L3-R2, B1 (path A): rows 1 to 3 decided and row L3-OD6 undecided, adopt is refused, so the band cannot
    select the average-day benchmark without the owner; a coverage answer then still applies."""
    need(os.path.join(COND, "od_l3_4.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    if "L3-OD6" in _decided(reg): raise Skip("row L3-OD6 is decided in this tree")
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p")], reg, ev)
    out = _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)
    assert "L3-OD6" in out, out
    _step("od_l3_6.py", "coverage", reg, *_extra("od_l3_6.py", "coverage", ev, share="80"))
    _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)


def t_l3r2_a_lid_that_does_not_carry_the_weather_basis_never_reads_coherent():
    """CHECK-2 of L3-R2, B2 (path B): the mean day in the WAB build is carried by the QMX-out lid only (fixture). With the
    tablet-out lid an open conflict is recorded whichever row is answered first, and coherent() reads the set
    incoherent; the QMX-out lid reads coherent."""
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    if any(r in _decided(reg) for r in ("L3-OD1", "L3-OD2", "L3-OD6")): raise Skip("rows 1, 2 or 6 are decided in this tree")
    _chain([("L3-OD6", "od_l3_6.py", "mean-day", "WAB"), ("L3-OD1", "od_l3_1.py", "approve"),
            ("L3-OD2", "od_l3_2.py", "tablet-out")], reg, ev)
    assert len(_conflicts(reg, "weather basis")) == 1, "the tablet-out lid under the WAB mean day records no conflict"
    d2, reg2, ev2 = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "tablet-out"),
            ("L3-OD6", "od_l3_6.py", "mean-day", "WAB")], reg2, ev2)
    assert len(_conflicts(reg2, "weather basis")) == 1, "row L3-OD6 answered after the lid records no conflict"
    RL = _render_mod()
    data = RL.load_data()
    next(x for x in data["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"] = _rows()
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    base = {"L3-OD1": x("approve"), "L3-OD3": x("2s2p"), "L3-OD4": x("reject"), "L3-OD5": x("reading-c"),
            "L3-OD6": x("mean-day", build="WAB", share=None)}
    assert not RL.coherent(dict(base, **{"L3-OD2": x("tablet-out")}), data)[1], "path B reads coherent"
    assert RL.coherent(dict(base, **{"L3-OD2": x("qmx-out")}), data)[1], "the QMX-out lid reads incoherent"
    assert not RL.coherent(dict(base, **{"L3-OD2": x("qmx-out")}))[1], "an unfilled fit reads coherent"


def t_l3r2_a_coverage_target_no_lid_carries_is_a_conflict():
    """A coverage target no lid of the table carries records an open conflict; row L3-OD1 applied after it keeps the
    target in REQ-072; row L3-OD4's band is refused beside it."""
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    import yaml
    d, reg, ev = _copy_registry()
    if any(r in _decided(reg) for r in ("L3-OD1", "L3-OD6")): raise Skip("rows L3-OD1 or L3-OD6 are decided in this tree")
    _chain([("L3-OD6", "od_l3_6.py", "coverage", "WAB", "95")], reg, ev)
    assert len(_conflicts(reg, "weather basis")) == 1, "no open conflict for a target no lid carries"
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "2s2p")], reg, ev)
    assert len(_conflicts(reg, "weather basis")) == 1, "row L3-OD2 recorded a second conflict for the same answer"
    r072 = next(r for r in yaml.safe_load(open(reg, encoding="utf-8"))["records"] if r["id"] == "REQ-072")
    for f in ("statement", "acceptance"):
        assert "at least 95 percent" in " ".join(str(r072[f]).split()), "row L3-OD1 dropped the target from REQ-072's %s" % f
    _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)


def t_l3r2_row6_figures_are_held_until_filled():
    """D-23: row L3-OD6's figures stay placeholders bound to the energy basis; an answer reads only filled figures, and a
    held target, an unknown target, a missing share or build are refused."""
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    RL = _render_mod()
    data = RL.load_data()
    q = next(d for d in data["decisions"] if d["id"] == "L3-OD6")["quantified"]
    assert sorted({str(r["share"]) for r in q["rows"]}) == ["50", "80", "95", "None"], "the targets are not the basis's"
    assert {r["build"] for r in q["rows"]} == {"TYP", "WAB"} and set(q["builds"]) == {"TYP", "WAB"}, "a build is missing"
    if not data.get("energy_basis"):
        for r in q["rows"]:
            assert all(r.get(k) is None for k in ("usable_wh", "cells", "nominal_wh", "mass_kg", "fits")), \
                "row L3-OD6's %s carries a figure before the checked basis" % r["id"]
    d, reg, ev = _copy_registry()
    if "L3-OD6" in _decided(reg): raise Skip("row L3-OD6 is decided in this tree")
    out = _step("od_l3_6.py", "mean-day", reg, "--build", "TYP", expect=2)          # the tree's table: HELD
    assert "HELD" in out, out
    tb = os.path.join(d, "table.yaml")
    _step("od_l3_6.py", "coverage", reg, "--build", "TYP", "--share", "70", "--table", tb, expect=2)
    _step("od_l3_6.py", "coverage", reg, "--build", "TYP", "--table", tb, expect=2)
    _step("od_l3_6.py", "mean-day", reg, "--table", tb, expect=2)


def t_l3r2_the_gate_verifies_the_basis_check_and_the_reissue_ruling():
    """CHECK-2 of L3-R2, B3: an energy basis whose check reads 'accepted: no' is not filed for the gate or the hold; a
    definition_reissue naming the baselined text, or approved by a ruling that does not decide it (D-21), does not close
    L3-C26; a different file approved by a ruling that decides it, dated after the rows, does."""
    RL = _render_mod()
    sys.path.insert(0, COND)
    import cond as C
    d = tempfile.mkdtemp(prefix="l3r2-gate-")
    files = {}
    for n, body in (("EB.md", "basis\n"), ("w.out", "w\n"), ("no.md", "accepted: no\n"), ("yes.md", "accepted: yes\n"),
                    ("reissue.md", "a change record\n")):
        files[n] = os.path.join(d, n)
        open(files[n], "w", encoding="utf-8").write(body)
    sha = lambda n: RL.sha16_bytes(open(files[n], "rb").read())
    data = RL.load_data()
    for chk, want in (("no.md", False), ("yes.md", True)):
        data["energy_basis"] = {"record": files["EB.md"], "sha16": sha("EB.md"), "check": files[chk], "check_sha16": sha(chk),
                                "outputs": [{"path": files["w.out"], "sha16": sha("w.out")}]}
        assert RL.basis_ok(data)[0] is want, "the gate reads a check that says %s as %s" % (chk, not want)
        assert C.basis_state(data)[0] is want, "the hold reads a check that says %s as %s" % (chk, not want)
    data["energy_basis"]["sha16"] = "0" * 16
    assert C.basis_state(data)[0] is False, "the hold accepts a record not at its sha"
    import rules_lib as R
    req = R.load_requirements()
    dec = {"L3-OD1": ("approve", "D-98", "2026-10-01", "", {})}
    conops = os.path.join(ROOT, "v2", "docs", "CONOPS.md")
    data["definition_reissue"] = {"record": "v2/docs/CONOPS.md", "sha16": RL.sha16_bytes(open(conops, "rb").read()), "approved_by": "D-21"}
    if data["definition_reissue"]["sha16"] in data["baseline_definition"].values():
        assert RL.reissue_ok(req, data, dec)[0] is False, "the baselined CONOPS reads as a re-issue"
    data["definition_reissue"] = {"record": files["reissue.md"], "sha16": sha("reissue.md"), "approved_by": "D-21"}
    assert RL.reissue_ok(req, data, dec)[0] is False, "D-21 approves a re-issue"
    req2 = dict(req, owner_rulings=list(req["owner_rulings"]) + [
        {"id": "D-99", "ruled_on": "2026-10-02", "decides": "definition_reissue", "title": "t", "ruling": "r"}])
    data["definition_reissue"]["approved_by"] = "D-99"
    assert RL.reissue_ok(req2, data, dec)[0] is True, "a re-issue approved by a ruling that decides it is refused"
    req2["owner_rulings"][-1]["ruled_on"] = "2026-09-30"
    assert RL.reissue_ok(req2, data, dec)[0] is False, "a ruling dated before the rows approves the re-issue"


def t_l3r2_figures_bind_exactly():
    """CHECK-2 of L3-R2, minor 6: a figure or a band binds as a whole token, line, cell or quoted phrase, never as a
    substring of a longer one."""
    sys.path.insert(0, COND)
    import cond as C
    assert C.exact_token("the array 1100 Wp, entry 80 A", "1100", "Wp")
    assert not C.exact_token("the array 11100 Wp", "1100", "Wp") and not C.exact_token("the array 1.1100 Wp", "1100", "Wp")
    assert not C.exact_token("entry 800 A", "80", "A") and not C.exact_token("entry 80 Ah", "80", "A")
    assert C.exact_phrase('band "30 to 50 degrees" held', "30 to 50 degrees")
    assert C.exact_phrase("| x | 30 to 50 degrees | y |", "30 to 50 degrees")
    assert not C.exact_phrase("slope 130 to 50 degrees and more", "30 to 50 degrees")
    need(os.path.join(COND, "od_l3_3.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    open(ev, "w", encoding="utf-8").write("TEST: the array 11100 Wp, entry 800 A.\n")
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out")], reg, ev)
    if "L3-OD3" in _decided(reg): raise Skip("row L3-OD3 is decided in this tree")
    _step("od_l3_3.py", "keep", reg, "--array-wp", "1100", "--entry-a", "80", "--evidence", ev, expect=2)


def t_l3r2_the_fill_reads_the_basis_by_exact_keys():
    """set_energy_basis.py and fill_l3r2_from_basis.py on a copy of l3r2.yaml and a scratch tree holding the basis's
    third issue (fnd/l3plane 868c321f, the format basis_reader.py is written for) and a fixture check: every row of row
    L3-OD6 is filled from weather_basis.out B and reads back equal; a second run of either is refused."""
    import yaml
    g = subprocess.run(["git", "-C", ROOT, "cat-file", "-e", "868c321f"], capture_output=True)
    if g.returncode: raise Skip("the basis's third issue (868c321f) is not in this repository")
    d = tempfile.mkdtemp(prefix="l3r2-fill-")
    os.makedirs(os.path.join(d, "v2/docs/records/l3plane"))
    for f in ("ENERGY-BASIS.md", "weather_basis.out", "energy_basis.out"):
        body = subprocess.run(["git", "-C", ROOT, "show", "868c321f:v2/docs/records/l3plane/" + f], capture_output=True).stdout
        open(os.path.join(d, "v2/docs/records/l3plane", f), "wb").write(body)
    open(os.path.join(d, "CHECK.md"), "w", encoding="utf-8").write("accepted: yes\n\nFIXTURE, tip `868c321f` (confirmed).\n")
    data = os.path.join(d, "l3r2.yaml")
    shutil.copy(os.path.join(L3, "l3r2.yaml"), data)
    if yaml.safe_load(open(data, encoding="utf-8")).get("energy_basis"): raise Skip("the tree's energy basis is named")
    args = ["--record", "v2/docs/records/l3plane/ENERGY-BASIS.md", "--outputs",
            "v2/docs/records/l3plane/weather_basis.out,v2/docs/records/l3plane/energy_basis.out", "--check", "CHECK.md",
            "--tip", "868c321f", "--data", data, "--root", d]
    s1 = _run([os.path.join(REC, "set_energy_basis.py")] + args)
    assert s1.returncode == 0, s1.stdout + s1.stderr
    assert _run([os.path.join(REC, "set_energy_basis.py")] + args).returncode == 2, "set_energy_basis.py ran twice"
    f1 = _run([os.path.join(REC, "fill_l3r2_from_basis.py"), "--data", data, "--root", d])
    assert f1.returncode == 0, f1.stdout + f1.stderr
    assert _run([os.path.join(REC, "fill_l3r2_from_basis.py"), "--data", data, "--root", d]).returncode == 2
    sys.path.insert(0, REC)
    import basis_reader as BR
    siz = BR.sizing(open(os.path.join(d, "v2/docs/records/l3plane/weather_basis.out"), encoding="utf-8").read())
    y = yaml.safe_load(open(data, encoding="utf-8"))
    for r in next(x for x in y["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]:
        key = ("mean-day" if r["option"] == "mean-day" else str(r["share"]), r["build"])
        assert all(r[k] == v for k, v in siz[key].items()), "row %s does not read back as the basis prints it" % r["id"]
    assert y["basis_figures"]["reference_plane"], "basis_figures is empty"
    bad = os.path.join(d, "bad.out")
    open(bad, "w", encoding="utf-8").write(open(os.path.join(d, "v2/docs/records/l3plane/weather_basis.out"), encoding="utf-8")
                                           .read().replace("(ii) 95 % of the windows", "(ii) 96 % of the windows"))
    try:
        BR.sizing(open(bad, encoding="utf-8").read())
    except BR.BasisError:
        pass
    else:
        raise AssertionError("a target the table does not name was read")


def t_l3r2_the_incoherent_combinations_are_refused():
    """CHECK-1, B1: keep needs the basis's figures; adopt needs 2S2P (1S4P or REQ-016 kept refused); row 2 needs row 1
    approved; both lid items kept records its conflict and adopts no band."""
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-out")], reg, ev)
    if "L3-OD3" in _decided(reg): raise Skip("row L3-OD3 is decided in this tree")
    _step("od_l3_3.py", "keep", reg, expect=2)                                   # no basis figures: refused
    _chain([("L3-OD3", "od_l3_3.py", "keep"), ("L3-OD6", "od_l3_6.py", "mean-day", "TYP")], reg, ev)
    out = _step("od_l3_4.py", "adopt", reg, *_extra("od_l3_4.py", "adopt", ev), expect=2)
    assert "2s2p" in out, out
    d2, reg2, ev2 = _copy_registry()
    _chain([("L3-OD6", "od_l3_6.py", "mean-day", "TYP"), ("L3-OD1", "od_l3_1.py", "approve"),
            ("L3-OD2", "od_l3_2.py", "qmx-out"), ("L3-OD3", "od_l3_3.py", "1s4p")], reg2, ev2)
    _step("od_l3_4.py", "adopt", reg2, *_extra("od_l3_4.py", "adopt", ev2), expect=2)
    d3, reg3, ev3 = _copy_registry()
    if "L3-OD1" not in _decided(reg3):
        _chain([("L3-OD1", "od_l3_1.py", "reject")], reg3, ev3)
        _step("od_l3_2.py", "tablet-out", reg3, expect=2)
    d4, reg4, ev4 = _copy_registry()
    _chain([("L3-OD6", "od_l3_6.py", "mean-day", "TYP"), ("L3-OD1", "od_l3_1.py", "approve"),
            ("L3-OD2", "od_l3_2.py", "both-kept"), ("L3-OD3", "od_l3_3.py", "2s2p")], reg4, ev4)
    assert _conflicts(reg4, "both approved lid items kept"), "both lid items kept records no conflict"
    _step("od_l3_4.py", "adopt", reg4, *_extra("od_l3_4.py", "adopt", ev4), expect=2)
    if "L3-OD4" not in _decided(reg4): _step("od_l3_4.py", "reject", reg4)


def t_l3r2_the_gate_reads_an_incoherent_set_as_not_unambiguous():
    """Sets the scripts refuse, written as rulings here, keep the gate's first condition NOT MET."""
    RL = _render_mod()
    data = RL.load_data()
    next(x for x in data["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"] = _rows()
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    base = {"L3-OD1": x("approve"), "L3-OD2": x("qmx-out"), "L3-OD3": x("2s2p"), "L3-OD4": x("adopt"),
            "L3-OD6": x("mean-day", build="TYP", share=None)}
    assert RL.coherent(base, data)[1], "the example set reads incoherent"
    for bad in ({"L3-OD6": x("coverage", build="TYP", share=50)}, {"L3-OD2": x("both-kept")}, {"L3-OD3": x("keep")},
                {"L3-OD1": x("reject")}):
        assert not RL.coherent(dict(base, **bad), data)[1], "a set with %s reads coherent" % bad
    import rules_lib as R
    req = R.load_requirements()
    data["energy_basis"] = None
    g = RL.gate(req, dict(base, **{"L3-OD3": x("keep")}), data, RL.load_h3())
    assert g[0][1] is False, "the gate reads the target unambiguous on an incoherent set"


def t_l3r2_the_other_answers_apply_on_a_copy():
    need(os.path.join(COND, "od_l3_1.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "tablet-out"), ("L3-OD3", "od_l3_3.py", "keep"),
            ("L3-OD4", "od_l3_4.py", "reject"), ("L3-OD5", "od_l3_5.py", "measure")], reg, ev)
    d2, reg2, ev2 = _copy_registry()
    _chain([("L3-OD1", "od_l3_1.py", "approve"), ("L3-OD2", "od_l3_2.py", "qmx-outside"), ("L3-OD3", "od_l3_3.py", "1s4p"),
            ("L3-OD5", "od_l3_5.py", "cells"), ("L3-OD6", "od_l3_6.py", "coverage", "TYP", "50")], reg2, ev2)


def t_l3r2_the_table_has_six_rows_each_with_its_parts():
    """D-23 and D-24: the six-row table gives each row its options, the recommendation, quantified consequences and
    dependencies, and names the requirement it changes with the consequence (D-25); every row that rests on board A's
    front end carries its four cases (the circuit as drawn, a derated variant, the
    resistor-only proposal, a hypothetical corrected power path) and the corrections case (c) assumes are tracked as
    downstream closure items with a criterion each; every relative link on the pages resolves."""
    RL = _render_mod()
    data = RL.load_data()
    rows = data["decisions"]
    assert [d["id"] for d in rows] == ["L3-OD%d" % i for i in range(1, 7)], "the table is not the six rows"
    for d in rows:
        for k in ("question", "owner_test", "recommendation", "consequences", "dependencies", "affected"):
            assert str(d.get(k) or "").strip(), "%s has no %s" % (d["id"], k)
        assert d.get("options"), "%s has no options" % d["id"]
    for rid in ("L3-OD1", "L3-OD2", "L3-OD4", "L3-OD6"):
        r11 = next(d for d in rows if d["id"] == rid).get("r11") or {}
        assert r11.get("held") and r11.get("derated") and r11.get("resistor") and r11.get("corrected"), "%s does not carry the four cases" % rid
        assert "power_path_check" in next(d for d in rows if d["id"] == rid)["held_until"], "%s is not held for the power path" % rid
    closure = {c["id"]: c for c in data["closure"]}
    for c in data["power_path_corrections"]:
        assert c.get("criterion") and closure.get(c["closure"], {}).get("state") == "DOWNSTREAM", \
            "%s has no criterion or no downstream closure item" % c["id"]
    od1 = next(d for d in rows if d["id"] == "L3-OD1")
    assert "not a sufficient solution" in od1["consequences"] and "HELD" in od1["recommendation"], \
        "row L3-OD1 presents the resistor-only proposal as sufficient or recommends on the energy balance"
    assert "coordination only" in od1["r11"]["derated"], "the derated variant is not labelled as fixing coordination only"
    pp2 = next(c for c in data["power_path_corrections"] if c["id"] == "PP-02")
    assert "implementation requirement" in pp2["item"] and "not a defect" in pp2["item"], "Kelvin sensing reads as a defect (D-25)"
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    for rid in ("L3-OD1", "L3-OD2"):
        assert "CANNOT MEET M1" in [l for l in page.split("\n") if l.startswith("| %s |" % rid)][0], \
            "%s's options do not flag the option that cannot meet M1" % rid
    for name in RL.PAGES.values():
        RL.check_links(name, open(os.path.join(L3, name), encoding="utf-8").read())
