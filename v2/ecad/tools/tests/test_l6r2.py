#!/usr/bin/env python3
"""The Layer 6 record of the generic parts (MESHSAT-1357, record l6r2, 3 October 2026).

Properties, pinned on fixtures and on the committed record, never on today's counts:

  * a check refuses a part that misses a requirement: a lower rated voltage, a dielectric the rule does not accept, a looser
    tolerance, too little power, another value or package; and accepts one that meets every requirement;
  * rule I-1's order: a design code that meets everything wins over a basic-library part; a basic part over an extended one; a
    part under the five-kit need is never SELECTED while another line meets everything with stock;
  * the grade verdict is the envelope's (-20 to +62.1 C board air);
  * the draft's block sets a code only where the part has none AND its value is the value the code was selected for, and names the
    rest; an entry that names the code it replaces (round 4) changes only that code on that value; a second application, a missing anchor and a name already in use are refused; the repository's own generator is refused
    while RELEASE.md does not read released with an accepted check;
  * each board's draft is the record's render, and it COMMUTES with every other pending draft of its generator (identical text in
    either order, and the result parses);
  * the identity block in pcb_part_identities.yaml is the record's render, outside `selections`; every DECODED binding in it passes
    rule D-2 where its document is on this host;
  * the copied supplier BOM reader is the file of its recorded commit; the record carries no em or en dash and no private path;
  * the designator detector reads the changed lines' string tokens, never the prose around them;
  * round 3, the Coilcraft lands (criterion 6.4): every fitted row of the six boards whose value names an XAL part of one series
    and whose footprint is drawn for another is moved by a land draft, and only those rows; for each, the two KiCad footprints'
    pads and outlines are identical, the pads are the maker's one recommended land of the series, the footprint's series makes
    no part of that inductance, and the named footprint's model height is the maker's maximum for the named part; each land draft
    maps its rows to the named part's footprint, refuses the repository's generator until released and a second application,
    and commutes with every other pending draft of its generator, this record's LCSC draft included;
  * round 5, the open requirements of finding F3: every declaration is a valid intent.node, every figure that rests on a declared
    rail equals the derivation from the committed intent file, the overlay makes each declared net read DECLARED at exactly its
    figures and leaves the committed intent untouched; under the overlay no capacitor on a declared net is OPEN and each such row
    is SELECTED with a code that meets its requirement; each intent draft is the record's render, refuses the repository's
    generator until released and a second application, and commutes with every other pending draft; a jumper's rated current is
    read off the held Uniroyal table for UNI-ROYAL zero-ohm lines only; the harmonic filter's desk check reads the drawn values.
Run: env -C v2/ecad/tools/tests python3 run.py test_l6r2"""
import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(REPO, "v2", "docs", "records", "l6r2")
sys.path.insert(0, TOOLS)
sys.path.insert(0, REC)
import part_identities as PI  # noqa: E402

_CACHE = {}


def _M():
    if "m" not in _CACHE:
        p = os.path.join(REC, "l6r2_passives.py")
        if not os.path.exists(p): raise Skip("the record is not in the tree")
        sp = importlib.util.spec_from_file_location("l6r2_passives_t", p)
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        _CACHE["m"] = m
    return _CACHE["m"]


def _A():
    import l6r2_apply
    return l6r2_apply


def _B():
    if "B" not in _CACHE:
        _CACHE["B"] = _M().compute()[0]
    return _CACHE["B"]


def _cap(v="100nF", pkg="0603", vmin=25.0, diel="X7R", tol=10.0):
    return dict(cls="CAP", kind="capacitor", refs=["C1"], values=["100n"], lands=["C_0603_1608Metric"], design_codes=[], keywords=[],
                requirements=dict(value=v, package=pkg, construction="MLCC", dielectric=diel, v_rating_min=vmin, tolerance_max_pct=tol))


def _row(code="C1", cap="100nF", volt="50V", tc="X7R", tol="±10%", pkg="0603", lib="base", stock=10 ** 6, brand="YAGEO", pref=False):
    return dict(code=code, model="M" + code, brand=brand, package=pkg, stock=stock, lib=lib, preferred=pref,
                attributes={"Capacitance": cap, "Voltage Rating": volt, "Temperature Coefficient": tc, "Tolerance": tol},
                describe="%s %s %s Multilayer Ceramic Capacitors MLCC - SMD/SMT" % (cap, volt, tc), sort="", prices=[])


def t_a_capacitor_check_refuses_each_unmet_requirement():
    m = _M()
    d = _cap()
    assert m.check(d, _row())[0], "a part meeting every requirement is refused"
    for bad in (dict(volt="16V"), dict(tc="X5R"), dict(tc="Y5V"), dict(tol="±20%"), dict(cap="10nF"), dict(pkg="0805")):
        ok, lines, _ = m.check(d, _row(**bad))
        assert not ok, "accepted %s" % bad
    assert m.check(_cap(diel="X5R"), _row(tc="X7R"))[0], "rule C-D3's acceptance: an X7R part meets an X5R requirement"
    assert not m.check(_cap(diel="C0G", tol=5.0), _row(tc="X7R", tol="±5%"))[0], "an X7R part never meets a C0G requirement"
    assert m.check(_cap(diel="C0G", tol=5.0), _row(tc="NP0", tol="±5%"))[0], "NP0 is C0G"


def t_a_resistor_check_refuses_too_little_power_and_a_looser_tolerance():
    m = _M()
    d = dict(cls="RES", kind="resistor", refs=["R1"], values=["10k 1%"], lands=["R_0603_1608Metric"], design_codes=[], keywords=[],
             requirements=dict(value="10kOhm", package="0603", resistor_kind="general", tolerance_max_pct=1.0, power_min_w=0.1))
    good = dict(code="C2", model="X", brand="UNI-ROYAL", package="0603", stock=10 ** 6, lib="base", preferred=False, describe="", sort="", prices=[],
                attributes={"Resistance": "10kΩ", "Tolerance": "±1%", "Power(Watts)": "100mW", "Operating Temperature": "-55℃~+155℃"})
    ok, lines, grade = m.check(d, good)
    assert ok and grade[:2] == (-55.0, 155.0)
    for k, v in (("Tolerance", "±5%"), ("Power(Watts)", "62.5mW"), ("Resistance", "1kΩ")):
        bad = json.loads(json.dumps(good)); bad["attributes"][k] = v
        assert not m.check(d, bad)[0], "accepted %s %s" % (k, v)
    assert m.parse_power("1/4W") == 0.25 and m.parse_power("100mW") == 0.1 and m.ohms("40.2kΩ") == 40200.0 and m.ohms("10mOhm") == 0.01


def t_rule_i1_orders_the_eligible_lines_and_never_selects_short_stock_over_a_stocked_line():
    m = _M()
    d = _cap(); d["refs"] = ["C1", "C2"]   # need 10
    d["keywords"] = ["k"]
    cat = dict(codes={}, searches={"k": dict(rows=[_row("C10", lib="expand", stock=10 ** 7), _row("C11", lib="base", stock=10 ** 5),
                                                   _row("C12", lib="base", stock=3), _row("C13", volt="10V", lib="base", stock=10 ** 9)])})
    ch = m.choose(d, cat)
    assert ch["state"] == "SELECTED" and ch["pick"]["code"] == "C11", "the basic, stocked, meeting line is not first: %s" % ch["pick"]["code"]
    d["design_codes"] = [("C10", "fixture")]
    cat["codes"]["C10"] = cat["searches"]["k"]["rows"][0]
    assert m.choose(d, cat)["pick"]["code"] == "C10", "the design's own code that meets everything is not first"
    cat2 = dict(codes={}, searches={"k": dict(rows=[_row("C12", stock=3)])})
    d["design_codes"] = []
    ch2 = m.choose(d, cat2)
    assert ch2["state"] == "LOW_STOCK" and ch2["pick"]["code"] == "C12"
    cat3 = dict(codes={}, searches={"k": dict(rows=[_row("C13", volt="10V")])})
    assert m.choose(d, cat3)["state"] == "NO_MATCH"


def t_a_code_the_project_refused_is_never_selected():
    m = _M()
    d = _cap(); d["keywords"] = ["k"]
    cat = dict(codes={}, searches={"k": dict(rows=[_row("C50", lib="base", stock=10 ** 7), _row("C51", lib="expand", stock=10 ** 6)])})
    cat["_refusals"] = ({"C50": ("", "a fixture's refusal")}, [])
    assert m.choose(d, cat)["pick"]["code"] == "C51", "a blocked code was selected"
    cat["_refusals"] = ({"C50": ("0805", "refused on an 0805 land only")}, [])
    assert m.choose(d, cat)["pick"]["code"] == "C50", "a land-qualified block refused another land"
    cat["_refusals"] = ({}, [dict(id="MM-X", code="C50", reason="fixture", comment_re="^100n")])
    assert m.choose(d, cat)["pick"]["code"] == "C51", "a declared mismatch was selected"


def t_a_special_parts_value_is_read_for_what_it_names_never_selected():
    m = _M()
    assert "Keystone 3034" in m.special_why("CR2032 holder Keystone 3034: VBAT", "BatteryHolder")
    assert "BC857" in m.special_why("BC857: LED_nPWR must be buffered", "SOT-23")
    assert "no part by number" in m.special_why("24 MHz 3225", "Crystal_SMD_3225")
    assert "no part by number" in m.special_why("console UART0 (3.3 V, bench): GND TX RX IO23", "PinHeader_1x05")
    assert "HC6-SC-7" in m.special_why("A-B interconnect (IDC 2x13)", "IDC-Header_2x13_P2.54mm_Vertical_NarrowPad")


def t_the_grade_verdict_is_the_envelopes():
    m = _M()
    assert m.grade_verdict((-55, 125, "x")) == "INSIDE"
    assert m.grade_verdict((-20, 125, "x")) == "AT_LIMIT"
    assert m.grade_verdict((-10, 60, "x")) == "OUTSIDE"
    assert m.grade_verdict(None) == "NOT READ"


def t_the_block_sets_a_code_only_where_none_is_and_the_value_is_the_selected_one():
    A = _A()
    entries = {"R1": ("10k", "C25804"), "R2": ("10k", "C25804"), "R3": ("4.7k", "C23162"), "R9": ("1k", "C21190")}
    text = "P = [dict(ref='R1', value='10k', lcsc=''), dict(ref='R2', value='22k', lcsc=''), dict(ref='R3', value='4.7k', lcsc='C9')]\n" + A.ANCHOR
    st, new, why = A.apply_text(text, "a", entries)
    assert st == "OK", why
    out = []
    ns = {"print": lambda *a: out.append(" ".join(str(x) for x in a))}
    exec(new.replace(A.ANCHOR, ""), ns)
    got = {p["ref"]: p["lcsc"] for p in ns["P"]}
    assert got == {"R1": "C25804", "R2": "", "R3": "C9"}, got
    assert out and "R2" in out[0] and "R9" in out[0], "the skipped designators are not printed: %s" % out
    assert A.apply_text(new, "a", entries)[0] == "REFUSED", "a second application"
    assert A.apply_text("P = []\n", "a", entries)[0] == "REFUSED", "no anchor"
    assert A.apply_text("_p6 = 1\n" + A.ANCHOR, "a", entries)[0] == "REFUSED", "a name in use"


def t_an_entry_that_names_the_code_it_replaces_changes_only_that_code_on_that_value():
    A = _A()
    entries = {"C1": ("1u", "C559769", "C15849"), "C2": ("1u", "C559769", "C15849"), "C3": ("1u", "C559769", "C15849"), "C4": ("1n", "C113793")}
    text = ("P = [dict(ref='C1', value='1u', lcsc='C15849'), dict(ref='C2', value='1u', lcsc='C9'), dict(ref='C3', value='2.2u', lcsc='C15849'),"
            " dict(ref='C4', value='1n', lcsc='C1588')]\n" + A.ANCHOR)
    st, new, why = A.apply_text(text, "a", entries)
    assert st == "OK", why
    out = []
    ns = {"print": lambda *a: out.append(" ".join(str(x) for x in a))}
    exec(new.replace(A.ANCHOR, ""), ns)
    got = {p["ref"]: p["lcsc"] for p in ns["P"]}
    assert got == {"C1": "C559769", "C2": "C9", "C3": "C15849", "C4": "C1588"}, got
    assert out and all(r in out[0] for r in ("C2", "C3", "C4")) and "C1," not in out[0] + ",", "the entries not applied are not printed: %s" % out


def t_the_drafts_refuse_the_repositorys_own_generator_until_released():
    A = _A()
    if A.released(): raise Skip("RELEASE.md reads released: the guard is open by design")
    for b in ("a", "e"):
        gen = os.path.join(REPO, "v2", "ecad", "tools", "gen_sch_%s.py" % b)
        before = open(gen, "rb").read()
        r = subprocess.run([sys.executable, "-B", os.path.join(REC, "apply_gen_sch_%s_lcsc.py" % b), gen, "--write"], capture_output=True, text=True)
        assert r.returncode == 3 and "REFUSED" in r.stdout, r.stdout
        assert open(gen, "rb").read() == before


def t_each_draft_is_the_records_render_and_applies_to_a_scratch_copy():
    m, A = _M(), _A()
    B = _B()
    for b in m.ORDER:
        p = os.path.join(REC, "apply_gen_sch_%s_lcsc.py" % b)
        assert open(p, encoding="utf-8").read() == A.render_draft(b, m.entries_for(b, B)), "board %s's draft is not the record's render" % b
        with tempfile.TemporaryDirectory() as td:
            g = os.path.join(td, "gen.py")
            open(g, "w", encoding="utf-8").write(open(os.path.join(REPO, m.GEN[b]), encoding="utf-8").read())
            r = subprocess.run([sys.executable, "-B", p, g, "--write"], capture_output=True, text=True)
            assert r.returncode == 0, r.stdout + r.stderr
            r2 = subprocess.run([sys.executable, "-B", p, g, "--write"], capture_output=True, text=True)
            assert r2.returncode == 3, "a second application was not refused"


def t_each_draft_commutes_with_every_other_pending_draft_of_its_generator():
    m = _M()
    B = _B()
    for b in m.ORDER:
        res = m.compose(b, m.entries_for(b, B))
        assert res["ok"], "board %s: %s" % (b, res["notes"])
    assert m.change_chain("a") and m.change_chain("e"), "the change list names no draft of boards A and E"


def t_the_identity_block_is_the_records_render_and_its_decoded_bindings_hold():
    import yaml
    m = _M()
    t = yaml.safe_load(open(PI.TABLE, encoding="utf-8"))
    blk = t.get("drafted_identities_l6r2_passives")
    assert blk, "pcb_part_identities.yaml carries no drafted_identities_l6r2_passives block"
    want = m.identity_block(_B())["drafted_identities_l6r2_passives"]
    assert json.dumps(json.loads(json.dumps(want)), sort_keys=True) == json.dumps(blk, sort_keys=True), "the yaml block is not the record's render"
    ids = {s["id"] for s in t["selections"]}
    n = 0
    for row in blk["rows"]:
        assert row["id"] not in ids and row["id"].startswith("L6R2-")
        i = row["identity"]
        assert i["status"] in PI.STATUSES
        if i["status"] == "RESOLVED":
            ds = dict(i["datasheet"]); ds["fields"] = i["fields"]
            r = PI.read_binding(ds, i["mpn"], root=REPO, maker=i["maker"], req=row["requirements"], kind=row["kind"])
            assert r["state"] in ("DECODED", "UNREAD"), "%s: %s" % (row["id"], r.get("why"))
            n += r["state"] == "DECODED"
        else:
            assert i.get("reason_class") in PI.REASONS and i.get("reason") and i.get("next_action")
    assert n > 0, "no DECODED binding read on this host"


def t_the_copied_bom_reader_is_the_recorded_file_and_the_record_is_clean():
    m = _M()
    assert PI.sha256(os.path.join(REPO, m.BOM_TOOL)) == m.BOM_TOOL_FROM["sha256"]
    private = [base64.b64decode(e).decode() for e in ("L2hvbWUvY2xhdWRlLXJ1bm5lcg==", "L3RtcC9jbGF1ZGUt", "bmxsZWkwMQ==")]
    bad = []
    for root, _, files in os.walk(REC):
        for f in files:
            if f.endswith((".pdf", ".png")) or "__pycache__" in root: continue
            s = open(os.path.join(root, f), encoding="utf-8", errors="replace").read()
            if chr(0x2013) in s or chr(0x2014) in s: bad.append(("dash", f))
            if any(p in s for p in private): bad.append(("private", f))
    assert not bad, bad


def t_the_designator_detector_reads_string_tokens_not_prose():
    m = _M()
    old = 'x = 1\n# R5 in a comment\n'
    new = 'x = 1\n# R6 in a comment\nr("R7", "10k", "A", "B", lcsc="C25804"); c("C9", "1n", "A", "B", lcsc="C1588")\n'
    assert m.touched_refs(old, new) == {"R7", "C9"}, m.touched_refs(old, new)


def t_the_pages_table_is_the_records_render():
    m = _M()
    page = open(os.path.join(REC, "L6R2-PASSIVES.md"), encoding="utf-8").read()
    a, b = page.index("<!-- page-table:begin -->\n") + len("<!-- page-table:begin -->\n"), page.index("<!-- page-table:end -->")
    assert page[a:b] == m.page_table(_B()), "the page's coverage table is not the script's render"


def t_the_sets_need_sums_the_boards_that_share_a_code():
    m = _M()
    fake = {b: dict(sels=[], rows=[]) for b in m.ORDER}
    pick = dict(code="C9", stock=12, row=dict(model="X"), grade=(-55, 155, "fixture"))
    sel = lambda refs: dict(refs=refs, cls="RES", kind="resistor", values=["10k"], basis={}, choice=dict(state="SELECTED", pick=pick, need=5 * len(refs)))
    fake["a"]["sels"] = [sel(["R1", "R2"])]
    fake["b"]["sels"] = [sel(["R7"])]
    agg = m.aggregate_need(fake)
    assert agg == [("C9", "X", 15, 12)], agg
    F = m.findings(fake, {b: dict(ok=True, notes=[]) for b in m.ORDER})
    assert any(f[1].startswith("STOCK UNDER THE SET'S") and f[2] == "C9" for f in F), "a set short of stock is not a finding"


def _L():
    if "L" not in _CACHE:
        _CACHE["L"] = _M().lands()
    return _CACHE["L"]


def t_each_land_draft_moves_exactly_the_rows_drawn_on_another_series_body_and_the_evidence_holds():
    import l6r2_land
    L = _L()
    found = {(r["board"], r["ref"]) for r in L["rows"]}
    drafted = {(b, ref) for b, rows in l6r2_land.ROWS.items() for ref in rows}
    assert found == drafted, "the land drafts move %s; the netlists draw on another series' body %s" % (sorted(drafted), sorted(found))
    for r in L["rows"]:
        tag = "%s %s" % (r["board"].upper(), r["ref"])
        assert r["pads_eq"] and r["outline_eq"], "%s: the two footprints' copper or outlines differ: a land change, not a key change" % tag
        assert r["land_eq_sheet"] and r["land_printed"], "%s: the footprint's pads are not the maker's recommended land %s" % (tag, r["pad_fig"])
        assert not r["same_inductance_in_fp_series"], "%s: the footprint's series makes %s: the value, not the key, may be wrong" % (tag, r["same_inductance_in_fp_series"])
        assert r["h_named"] is not None and abs(r["h_named"] - r["h_named_model"]) < 1e-9, \
            "%s: the named footprint's model is %.2f mm, the maker's maximum %s mm" % (tag, r["h_named_model"], r["h_named"])
        assert r["drafted"][1] == "L_Coilcraft_%s-XXX" % r["named"].split("-")[0] and r["drafted"][2] == r["named"] + "ME", tag


def t_each_land_draft_maps_its_rows_to_the_named_parts_footprint_and_nothing_else_moves():
    import l6r2_land
    m = _M()
    for b, d in _L()["drafts"].items():
        assert d["state"] == "OK", "board %s: %s" % (b, d["why"])
        assert not d["keys_changed"], "board %s: the draft changes the footprint of keys %s" % (b, d["keys_changed"])
        targets = {v[1] for v in l6r2_land.ROWS[b].values()}
        assert {d["fp"][k].split(":", 1)[1] for k in d["keys_added"]} == targets, (b, d["keys_added"])
        g0 = open(os.path.join(REPO, m.GEN[b]), encoding="utf-8").read()
        new = l6r2_land.apply_text(g0, b)[1]
        for what, old, rep in l6r2_land.EDITS[b]:
            if old.startswith("part("):
                key = rep.rstrip(",").rsplit(",", 1)[1].strip().strip('"')
                assert d["fp"][key].split(":", 1)[1] in targets and new.count(rep) == 1 and new.count(old) == 0, what


def t_the_land_drafts_refuse_the_repository_generators_until_released_and_a_second_application():
    import l6r2_apply
    m = _M()
    for b in ("b", "e"):
        script = os.path.join(REC, "apply_gen_sch_%s_xal_land.py" % b)
        gen = os.path.join(REPO, m.GEN[b])
        if not l6r2_apply.released():
            before = open(gen, "rb").read()
            r = subprocess.run([sys.executable, "-B", script, gen, "--write"], capture_output=True, text=True)
            assert r.returncode == 3 and "REFUSED" in r.stdout, r.stdout
            assert open(gen, "rb").read() == before
        with tempfile.TemporaryDirectory() as td:
            g = os.path.join(td, "gen.py")
            open(g, "w", encoding="utf-8").write(open(gen, encoding="utf-8").read())
            r = subprocess.run([sys.executable, "-B", script, g, "--write"], capture_output=True, text=True)
            assert r.returncode == 0, r.stdout + r.stderr
            r2 = subprocess.run([sys.executable, "-B", script, g, "--write"], capture_output=True, text=True)
            assert r2.returncode == 3, "a second application was not refused"
    import l6r2_land
    assert l6r2_land.apply_text("x = 1\n", "e")[0] == "REFUSED", "a generator without the old texts was not refused"


def t_each_land_draft_commutes_with_every_other_pending_draft_and_the_records_lcsc_draft():
    import l6r2_land
    m = _M()
    for b in l6r2_land.EDITS:
        res = m.compose_land(b)
        assert res["ok"], "board %s: %s" % (b, res["notes"])
        assert any("apply_gen_sch_%s_lcsc.py" % b in n for n in res["notes"]), "board %s: the record's own LCSC draft was not composed" % b



def _I():
    import l6r2_intent
    return l6r2_intent


def t_every_declaration_is_a_valid_intent_node_and_its_rail_figures_follow_the_committed_intent():
    import intent as INT
    I = _I()
    D = I.declarations(REPO)
    assert set(D) == {"p", "d", "b"}, sorted(D)
    for b, decl in D.items():
        for net, vmax, vmin, basis in decl:
            INT.node(net, vmax, basis, v_min=vmin)          # raises on a declaration intent.py refuses
            assert vmin <= 0 <= vmax and basis.strip() and "round 5" in basis, (b, net)
    d = {n: (a, c) for n, a, c, _ in D["d"]}
    assert abs(d["MICAMP_AC"][0] - round(I._hi(REPO, "d", "+5V_D8") / 2, 3)) < 1e-9, "MICAMP_AC is not half of +5V_D8's declared maximum"
    assert d["PCM_R_AC"][0] == I._hi(REPO, "d", "PCM_VCCR") and d["MIC_SUM"][0] == max(d["MICAMP_AC"][0], d["PCM_R_AC"][0])
    bb = {n: (a, c) for n, a, c, _ in D["b"]}
    assert bb["LIME_SSTX_P"][0] == I._hi(REPO, "b", "+5V_LIME")
    v, v2 = I.rf_peak(24.5)
    assert abs(v - 5.308) < 0.01 and abs(bb["WA_ANT"][0] - round(v2, 2)) < 1e-9
    assert abs(bb["SWA_IN"][0] - round(I._hi(REPO, "b", "+3V3_DEV") + round(v2, 2), 2)) < 1e-9


def t_the_overlay_declares_exactly_the_drafted_figures_and_leaves_the_committed_intent_alone():
    I = _I()
    D = I.declarations(REPO)
    phases = {x[0]: x for x in PI.BOARDS}
    with I.overlay(PI, REPO):
        for b, decl in D.items():
            B = PI.Board(*phases[b])
            for net, vmax, vmin, _basis in decl:
                assert B.bound(net) == (vmax, vmin, "DECLARED"), (b, net, B.bound(net))
    for b in D:
        B = PI.Board(*phases[b])
        assert all(net not in B.nodes for net, *_ in D[b]), "the overlay leaked into the committed intent of board %s" % b


def t_under_the_overlay_no_capacitor_on_a_declared_net_is_open_and_each_is_selected_with_a_meeting_code():
    m, I = _M(), _I()
    D = I.declarations(REPO)
    B = _B()
    for b, decl in D.items():
        nets = {n for n, *_ in decl}
        on = {p["ref"]: set((p.get("nets_key") or ":").split(":", 1)[1].split("+")) for p in B[b]["rows"]}
        for d in B[b]["sels"]:
            if d["kind"] != "capacitor": continue
            refs = [r for r in d["refs"] if on.get(r) and on[r] & nets]
            if not refs: continue
            assert d["cls"] != "OPEN", "board %s %s is still OPEN under the declarations: %s" % (b, refs, d["why"])
            ch = d.get("choice") or {}
            assert ch.get("state") in ("SELECTED", "LOW_STOCK") and ch["pick"]["lines"] and all(x[3] == "MEETS" for x in ch["pick"]["lines"]), (b, refs, ch.get("state"))


def t_each_intent_draft_is_the_render_refuses_until_released_and_commutes():
    import l6r2_apply
    m, I = _M(), _I()
    D = I.declarations(REPO)
    for b in D:
        p = os.path.join(REC, "apply_gen_sch_%s_intent.py" % b)
        assert open(p, encoding="utf-8").read() == I.render_draft(b, D[b]), "board %s's intent draft is not the record's render" % b
        gen = os.path.join(REPO, m.GEN[b])
        if not l6r2_apply.released():
            before = open(gen, "rb").read()
            r = subprocess.run([sys.executable, "-B", p, gen, "--write"], capture_output=True, text=True)
            assert r.returncode == 3 and "REFUSED" in r.stdout and open(gen, "rb").read() == before, r.stdout
        with tempfile.TemporaryDirectory() as td:
            g = os.path.join(td, "gen.py")
            open(g, "w", encoding="utf-8").write(open(gen, encoding="utf-8").read())
            assert subprocess.run([sys.executable, "-B", p, g, "--write"], capture_output=True, text=True).returncode == 0
            assert subprocess.run([sys.executable, "-B", p, g, "--write"], capture_output=True, text=True).returncode == 3, "a second application"
        res = m.compose_intent(b)
        assert res["ok"] and res["notes"], "board %s: %s" % (b, res["notes"])
    assert I.apply_text("x = 1\n", "p", D["p"])[0] == "REFUSED", "a generator without the anchor"


def t_a_jumpers_rated_current_is_read_off_the_held_table_for_uniroyal_zero_ohm_lines_only():
    m = _M()
    if not os.path.exists(os.path.join(REPO, m.UNIROYAL_DOC)): raise Skip("the held Uniroyal sheet is not fetched here")
    row = lambda brand, model, res: dict(brand=brand, model=model, attributes={"Resistance": res})
    assert m.jumper_rating(row("UNI-ROYAL(Uniroyal Elec)", "0603WAF0000T5E", "0Ω"))[0] == 1.0
    assert m.jumper_rating(row("UNI-ROYAL(Uniroyal Elec)", "25121WJ0000T4E", "0Ω"))[0] == 2.0
    assert m.jumper_rating(row("YAGEO", "RC0603JR-070RL", "0Ω"))[0] is None, "a maker whose sheet is not held"
    assert m.jumper_rating(row("UNI-ROYAL(Uniroyal Elec)", "0603WAF1002T5E", "10kΩ"))[0] is None, "not a jumper"


def t_the_harmonic_filters_desk_check_reads_the_drawn_values():
    m = _M()
    L = m.lpf_check(_B())
    assert len(L["values"]) == 5 and all(v > 0 for v in L["values"])
    nom145 = L["points"][145e6]
    assert nom145[1] > -0.1 and L["points"][290e6][0][0] < -20 and L["points"][435e6][0][0] < L["points"][290e6][0][0]
    assert L["i_l2"] > L["i_load"] and L["i_l1"] > L["i_load"], "the ladder's reactive current must show in the inductors"
