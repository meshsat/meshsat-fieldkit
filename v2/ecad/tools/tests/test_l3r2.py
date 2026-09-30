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
    for base in (REC, COND, os.path.join(REC, "prepared")):
        if os.path.isdir(base): paths += [os.path.join(base, f) for f in os.listdir(base) if f.endswith((".py", ".md", ".out", ".yaml"))]
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
    for s in ("apply_l3r2_session.py", "apply_l3r2_d23.py", "apply_l3r2_d24.py", "apply_l3r2_d25.py", "apply_l3r2_r3b.py",
              "apply_layer_status_l3_r3c.py", "apply_layer_status_l3_fill.py", "apply_layer_status_l3_r3d.py",
              "apply_l3r2_s127.py", "apply_layer_status_l3.py",
              "apply_layer_status_l3_r3.py", "apply_layer_status_l3_r3b.py"):
        p = os.path.join(REC, s)
        need(p, "%s is not in this tree" % s)
        r = _run([p, "--check"])
        assert r.returncode == 2 and ("already" in r.stdout or "has run" in r.stdout), \
            "%s did not refuse a second run:\n%s" % (s, (r.stdout + r.stderr)[-300:])


def t_l3r2_a_held_row_is_never_written_into_the_tree():
    """D-22, D-23 and D-24 hold rows L3-OD1, L3-OD2, L3-OD4 and L3-OD6 until the checked basis and the checked power path
    are filed: on a copy of l3r2.yaml with neither named (the data as round 3c left it before the fill), cond.hold refuses
    a write to the tree's registry for each, citing the ruling that holds it (asked directly, so nothing is written; CHECK-4
    of L3-R2, minor 6: the hold stays under test after the fill)."""
    need(os.path.join(COND, "cond.py"), "the conditional scripts are not in this tree")
    sys.path.insert(0, COND)
    import cond as C
    p = _unfilled_data(tempfile.mkdtemp(prefix="l3r2-hold-"))
    old = C.L3DATA
    C.L3DATA = p
    try:
        for row in ("L3-OD1", "L3-OD2", "L3-OD4", "L3-OD6"):
            try:
                C.hold({"check": False, "registry": C.E.REGISTRY}, row)
            except C.E.Refused as e:
                assert "held (%s)" % ("D-23, D-24" if row == "L3-OD6" else "D-22, D-24") in str(e), str(e)
            else:
                raise AssertionError("held row %s would be written into the tree's registry" % row)
    finally:
        C.L3DATA = old


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
    if script == "od_l3_4.py" and option == "adopt": return ["--push-n", "20"]
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
    data = RL.load_data()
    filled = RL.basis_ok(data)[0] and RL.basis_ok(data, "power_path_check")[0]
    want = "| Target unambiguous | %s |" % ("MET" if filled else "NOT MET")
    assert want in pages["REQUIREMENTS-L3-R2.md"], "the target's gate does not read %r on the example chain" % want
    assert "Status of L3-R2: IN_PROGRESS" in pages["REQUIREMENTS-L3-R2.md"], "the issue reads complete on an example chain"


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
    unfilled = RL.load_data()
    for r in next(x for x in unfilled["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]: r["fits"] = None
    assert not RL.coherent(dict(base, **{"L3-OD2": x("qmx-out")}), unfilled)[1], "an unfilled fit reads coherent"


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
    if RL.load_data().get("energy_basis"):                                        # the tree's table, filled and verified
        _step("od_l3_6.py", "mean-day", reg, "--build", "TYP")
        import yaml
        r072 = next(r for r in yaml.safe_load(open(reg, encoding="utf-8"))["records"] if r["id"] == "REQ-072")
        assert "619.0 Wh usable" in " ".join(str(r072.get("notes")).split()), "the filled mean day's store is not in REQ-072"
        d, reg, ev = _copy_registry()
    else:
        out = _step("od_l3_6.py", "mean-day", reg, "--build", "TYP", expect=2)      # the tree's table: HELD
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
    for n, body in (("reissue.md", "a change record\n"),):
        files[n] = os.path.join(d, n)
        open(files[n], "w", encoding="utf-8").write(body)
    sha = lambda n: RL.sha16_bytes(open(files[n], "rb").read())
    data = RL.load_data()
    root = _tip_tree(TIP4, ("v2/docs/records/l3plane/ENERGY-BASIS.md", "v2/docs/records/l3plane/weather_basis.out"))
    for body, want in (("accepted: no\n\ntip `%s`\n" % TIP4, False), ("accepted: yes\n\ntip `%s`\n" % TIP4, True),
                       ("accepted: yes\n\ntip `ec415c09`\n", False)):
        open(os.path.join(root, "CHECK.md"), "w", encoding="utf-8").write(body)
        data["energy_basis"] = _entry(root, TIP4, "v2/docs/records/l3plane/ENERGY-BASIS.md",
                                      ["v2/docs/records/l3plane/weather_basis.out"], "CHECK.md")
        assert RL.basis_ok(data, root=root)[0] is want, "the gate reads the check %r as %s" % (body[:40], not want)
        assert C.basis_state(data, root)[0] is want, "the hold reads the check %r as %s" % (body[:40], not want)
    data["energy_basis"]["sha16"] = "0" * 16
    assert C.basis_state(data, root)[0] is False, "the hold accepts a record not at its sha"
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


TIP3, TIP4, TIP2, TIP5 = "868c321f", "06b8ecea", "ec415c09", "cd8720a1ab6eed891b1afd8b5df3b8ceedf36c0f"
UNFILLED = "b0ccff61"   # l3r2.yaml as round 3c left it before the fill: a fixture for the fill's own tests


def _unfilled_data(d):
    """l3r2.yaml as it stood before the fill (UNFILLED), copied into `d`: set_energy_basis.py, restate_power_path.py and
    fill_l3r2_from_basis.py run on it as they ran on the tree."""
    _has(UNFILLED)
    p = os.path.join(d, "l3r2.yaml")
    open(p, "wb").write(subprocess.run(["git", "-C", ROOT, "show", UNFILLED + ":v2/docs/handover/layer3/l3r2.yaml"],
                                       capture_output=True).stdout)
    return p


def _has(*tips):
    for tip in tips:
        if subprocess.run(["git", "-C", ROOT, "cat-file", "-e", tip], capture_output=True).returncode:
            raise Skip("the tip %s is not in this repository" % tip)


def _tip_tree(tip, paths, d=None):
    """A scratch tree holding `paths` as they are at `tip` (read with git show)."""
    _has(tip)
    d = d or tempfile.mkdtemp(prefix="l3r2-tip-")
    for pth in paths:
        os.makedirs(os.path.dirname(os.path.join(d, pth)), exist_ok=True)
        open(os.path.join(d, pth), "wb").write(subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (tip, pth)],
                                                               capture_output=True).stdout)
    return d


def _entry(root, tip, record, outputs, check):
    sys.path.insert(0, REC)
    import basis_binding as BB
    s = lambda pth: BB.sha16_bytes(open(os.path.join(root, pth), "rb").read())
    return {"record": record, "sha16": s(record), "tip": tip, "outputs": [{"path": o, "sha16": s(o)} for o in outputs],
            "check": check, "check_sha16": s(check)}


def t_l3r2_an_accepted_check_is_bound_to_the_files_of_its_tip():
    """CHECK-3 of L3-R2, B1: the third issue's files (868c321f) with the check of the second (ec415c09) are refused
    whichever tip is named; files that are the checked tip's are accepted; a file changed afterwards, or a check that does
    not name the tip, lifts no hold and no gate; the same holds for the power path's check."""
    _has(TIP2, TIP3, TIP4)
    RL = _render_mod()
    sys.path.insert(0, COND)
    import cond as C
    L3P = "v2/docs/records/l3plane/"
    root = _tip_tree(TIP3, [L3P + f for f in ("ENERGY-BASIS.md", "weather_basis.out", "energy_basis.out")])
    shutil.copy(os.path.join(REC, "checks/energy-basis-check-2/CHECK-2.md"), os.path.join(root, "CHECK-2.md"))
    data = _unfilled_data(root)
    base = ["--record", L3P + "ENERGY-BASIS.md", "--outputs", L3P + "weather_basis.out," + L3P + "energy_basis.out",
            "--check", "CHECK-2.md", "--data", data, "--root", root]
    r = _run([os.path.join(REC, "set_energy_basis.py")] + base + ["--tip", TIP2])
    assert r.returncode == 2 and "not byte identical" in r.stdout, "868c321f's files were bound to ec415c09's check:\n" + r.stdout
    r = _run([os.path.join(REC, "set_energy_basis.py")] + base + ["--tip", TIP3])
    assert r.returncode == 2 and "does not name tip" in r.stdout, "a check was bound to a tip it did not check:\n" + r.stdout
    root4 = _tip_tree(TIP4, [L3P + f for f in ("ENERGY-BASIS.md", "weather_basis.out", "energy_basis.out", "three_cases.out")]
                      + ["v2/docs/records/r11dep/R11-DEPENDENCY.md", "v2/docs/records/r11dep/r11_dep.out"])
    open(os.path.join(root4, "CHECK.md"), "w", encoding="utf-8").write("accepted: yes\n\nFIXTURE, tip `%s` (confirmed).\n" % TIP4)
    d = RL.load_data()
    d["energy_basis"] = _entry(root4, TIP4, L3P + "ENERGY-BASIS.md", [L3P + "weather_basis.out"], "CHECK.md")
    d["power_path_check"] = _entry(root4, TIP4, "v2/docs/records/r11dep/R11-DEPENDENCY.md",
                                   ["v2/docs/records/r11dep/r11_dep.out", L3P + "three_cases.out"], "CHECK.md")
    for key in ("energy_basis", "power_path_check"):
        assert RL.basis_ok(d, key, root4)[0] and C.basis_state(d, root4, key)[0], "%s at its tip is refused" % key
    open(os.path.join(root4, L3P + "weather_basis.out"), "a", encoding="utf-8").write("changed after the check\n")
    d["energy_basis"]["outputs"][0]["sha16"] = RL.sha16_bytes(open(os.path.join(root4, L3P + "weather_basis.out"), "rb").read())
    assert not RL.basis_ok(d, "energy_basis", root4)[0], "the gate accepts an output that differs from the checked tip"
    assert not C.basis_state(d, root4, "energy_basis")[0], "the hold accepts an output that differs from the checked tip"
    d["power_path_check"]["tip"] = TIP3
    assert not C.basis_state(d, root4, "power_path_check")[0], "the hold accepts a check that does not name the recorded tip"
    import hashlib
    rec = os.path.join(root4, L3P + "ENERGY-BASIS.md")
    open(os.path.join(root4, "LISTING.md"), "w", encoding="utf-8").write(
        "accepted: yes\ntip: %s\n\n%s  %s\n" % (TIP4, hashlib.sha256(open(rec, "rb").read()).hexdigest(), L3P + "ENERGY-BASIS.md"))
    d2 = RL.load_data()
    d2["energy_basis"] = _entry(root4, TIP4, L3P + "ENERGY-BASIS.md", [L3P + "energy_basis.out"], "LISTING.md")
    ok, why = C.basis_state(d2, root4, "energy_basis")
    assert not ok and "but not" in why, "a check whose sha list leaves out a relied-on file is accepted (minor 7): %s" % why


def t_l3r2_the_reader_reads_the_fourth_issue_whole():
    """basis_reader.py reads the three outputs of the basis's fourth issue (06b8ecea) by exact keys, every table whole
    (CHECK-3 of L3-R2, minor 5): a table with a row missing is refused."""
    _has(TIP4)
    sys.path.insert(0, REC)
    import basis_reader as BR
    L3P = "v2/docs/records/l3plane/"
    root = _tip_tree(TIP4, [L3P + f for f in ("weather_basis.out", "energy_basis.out", "three_cases.out")])
    w, e, c = (open(os.path.join(root, L3P + f), encoding="utf-8").read() for f in ("weather_basis.out", "energy_basis.out", "three_cases.out"))
    assert len(BR.sizing(w)) == 8 and len(BR.coverage(w)) == 15 and len(BR.stores(w)) == 3 and len(BR.allowances(w)) == 2
    assert len(BR.reference_plane(e)) == 27 and len(BR.four_cases(c)) == 24 and len(BR.four_coverage(c)) == 16
    assert BR.derated_setting(c).replace(".", "", 1).isdigit()
    for fn, text, line in ((BR.coverage, w, "4S14P tablet out   WE WAB"), (BR.four_cases, c, "4S15P QMX out      TYP   74.3"),
                           (BR.four_coverage, c, "RESISTOR-ONLY lower bound, WE      4S15P")):
        cut = "\n".join(l for l in text.split("\n") if line not in l)
        assert cut != text, "the fixture line %r is not in the output" % line
        try:
            fn(cut)
        except BR.BasisError:
            pass
        else:
            raise AssertionError("%s read a table with a row missing" % fn.__name__)


def t_l3r2_the_power_path_list_is_restated_only_from_its_checked_record():
    """restate_power_path.py refuses until power_path_check is filed and verified; on a copy with the fourth issue's record
    and a fixture check of that tip it restates the list from the sixteen classes, anchors asserted, closure items
    restated and added, and refuses a second run."""
    _has(TIP5)
    import yaml
    L3P = "v2/docs/records/l3plane/"
    root = _tip_tree(TIP5, ["v2/docs/records/r11dep/R11-DEPENDENCY.md", "v2/docs/records/r11dep/r11_dep.out", L3P + "three_cases.out"])
    open(os.path.join(root, "CHECK.md"), "w", encoding="utf-8").write("accepted: yes\ntip: %s\n\nFIXTURE.\n" % TIP5)
    data = _unfilled_data(root)
    rs = [os.path.join(REC, "restate_power_path.py"), "--data", data, "--root", root]
    assert _run(rs).returncode == 2, "the list was restated with no power path check named"
    s = _run([os.path.join(REC, "set_energy_basis.py"), "--key", "power_path_check", "--record",
              "v2/docs/records/r11dep/R11-DEPENDENCY.md", "--outputs", "v2/docs/records/r11dep/r11_dep.out," + L3P + "three_cases.out",
              "--check", "CHECK.md", "--tip", TIP5, "--data", data, "--root", root])
    assert s.returncode == 0, s.stdout + s.stderr
    r = _run(rs)
    assert r.returncode == 0, r.stdout + r.stderr
    y = yaml.safe_load(open(data, encoding="utf-8"))
    assert [c["id"] for c in y["power_path_corrections"]][:3] == ["A-1", "A-2", "B-1"] and len(y["power_path_corrections"]) == 16
    assert {"L3-C46", "L3-C53"} <= {c["id"] for c in y["closure"]}
    assert _run(rs).returncode == 2, "restate_power_path.py ran twice"


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
    """set_energy_basis.py and fill_l3r2_from_basis.py on a copy of l3r2.yaml and a scratch tree holding the basis's fourth
    issue (06b8ecea) and a fixture check naming that tip: row L3-OD6's rows and the four-case cells are filled from
    weather_basis.out B and three_cases.out 2 and read back equal; a second run of either is refused."""
    _has(TIP4)
    import yaml
    L3P = "v2/docs/records/l3plane/"
    outs = [L3P + f for f in ("weather_basis.out", "energy_basis.out", "three_cases.out")]
    d = _tip_tree(TIP4, [L3P + "ENERGY-BASIS.md"] + outs)
    open(os.path.join(d, "CHECK.md"), "w", encoding="utf-8").write("accepted: yes\n\nFIXTURE, tip `%s` (confirmed).\n" % TIP4)
    data = _unfilled_data(d)
    args = ["--record", L3P + "ENERGY-BASIS.md", "--outputs", ",".join(outs), "--check", "CHECK.md", "--tip", TIP4,
            "--data", data, "--root", d]
    s1 = _run([os.path.join(REC, "set_energy_basis.py")] + args)
    assert s1.returncode == 0, s1.stdout + s1.stderr
    assert _run([os.path.join(REC, "set_energy_basis.py")] + args).returncode == 2, "set_energy_basis.py ran twice"
    f1 = _run([os.path.join(REC, "fill_l3r2_from_basis.py"), "--data", data, "--root", d])
    assert f1.returncode == 0, f1.stdout + f1.stderr
    assert _run([os.path.join(REC, "fill_l3r2_from_basis.py"), "--data", data, "--root", d]).returncode == 2
    sys.path.insert(0, REC)
    import basis_reader as BR
    siz = BR.sizing(open(os.path.join(d, L3P + "weather_basis.out"), encoding="utf-8").read())
    four = BR.four_cases(open(os.path.join(d, L3P + "three_cases.out"), encoding="utf-8").read())
    y = yaml.safe_load(open(data, encoding="utf-8"))
    for r in next(x for x in y["decisions"] if x["id"] == "L3-OD6")["quantified"]["rows"]:
        key = ("mean-day" if r["option"] == "mean-day" else str(r["share"]), r["build"])
        assert all(r[k] == v for k, v in siz[key].items()), "row %s does not read back as the basis prints it" % r["id"]
    for k, v in four.items():
        assert y["four_cases"]["reference_day"]["%s|%s|%s" % k] == v, "four-case cell %s does not read back" % (k,)
    RL = _render_mod()
    assert "DERATED VARIANT" in RL.four_cell(y["four_cases"], "a'") and "HYPOTHETICAL" in RL.four_cell(y["four_cases"], "c")


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
    assert "not a sufficient solution" in od1["consequences"] and "not as a feasible design" in od1["recommendation"], \
        "row L3-OD1 presents the resistor-only proposal as sufficient or recommends on the energy balance"
    assert "coordination only" in od1["r11"]["derated"], "the derated variant is not labelled as fixing coordination only"
    pp2 = next(c for c in data["power_path_corrections"] if c["id"] in ("PP-02", "C-1"))
    assert "implementation requirement" in pp2["item"] and "not a defect" in pp2["item"], "Kelvin sensing reads as a defect (D-25)"
    page = open(os.path.join(L3, "OWNER-DECISIONS-L3.md"), encoding="utf-8").read()
    for rid in ("L3-OD1", "L3-OD2"):
        assert "CANNOT MEET M1" in [l for l in page.split("\n") if l.startswith("| %s |" % rid)][0], \
            "%s's options do not flag the option that cannot meet M1" % rid
    for name in RL.PAGES.values():
        RL.check_links(name, open(os.path.join(L3, name), encoding="utf-8").read())


def t_l3r2_the_wab_build_with_the_tablet_out_is_never_coherent_on_the_checked_table():
    """CHECK-4 of L3-R2, B1: on the tree's own table, filled from the checked basis, the mean day in the WAB build is
    carried by the QMX-out lid only. So the WAB answer with the tablet out reads incoherent and records an open conflict,
    while the TYP answer keeps both lids open; the pairing is the owner's, and it is never silent."""
    RL = _render_mod()
    data = RL.load_data()
    if not (RL.basis_ok(data)[0] and RL.basis_ok(data, "power_path_check")[0]): raise Skip("the checked basis is not filed")
    x = lambda o, **f: (o, "D-99", "2026-10-01", "", f)
    base = {"L3-OD1": x("approve"), "L3-OD3": x("2s2p"), "L3-OD4": x("reject"), "L3-OD5": x("reading-c")}
    for build, lid, want in (("WAB", "tablet-out", False), ("WAB", "qmx-out", True), ("WAB", "qmx-outside", True),
                             ("TYP", "tablet-out", True), ("TYP", "qmx-out", True), ("TYP", "both-kept", False)):
        got = RL.coherent(dict(base, **{"L3-OD2": x(lid), "L3-OD6": x("mean-day", build=build, share=None)}), data)[1]
        assert got is want, "the mean day in %s with %s reads %s" % (build, lid, "coherent" if got else "incoherent")
    need(os.path.join(COND, "od_l3_6.py"), "the conditional scripts are not in this tree")
    d, reg, ev = _copy_registry()
    if any(r in _decided(reg) for r in ("L3-OD1", "L3-OD2", "L3-OD6")): raise Skip("rows 1, 2 or 6 are decided in this tree")
    _step("od_l3_6.py", "mean-day", reg, "--build", "WAB")                        # the tree's filled table, verified
    _step("od_l3_1.py", "approve", reg)
    _step("od_l3_2.py", "tablet-out", reg)                                        # the tree's filled table
    assert len(_conflicts(reg, "weather basis")) == 1, "the WAB mean day with the tablet out records no conflict"
    d2, reg2, ev2 = _copy_registry()
    _step("od_l3_6.py", "mean-day", reg2, "--build", "TYP")
    _step("od_l3_1.py", "approve", reg2)
    _step("od_l3_2.py", "tablet-out", reg2)
    assert not _conflicts(reg2, "weather basis"), "the TYP mean day with the tablet out records a conflict"

