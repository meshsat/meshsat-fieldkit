#!/usr/bin/env python3
"""The current-rating models, and the difference between a number and a sourced number.

MESHSAT-862, 16 September 2026, rule PI-001. `dc_drop.py` judged every rail on all seven boards against
`I = k dT^0.44 A^0.725` with k 0.024 internal and 0.048 external, written in a code comment as "IPC-2221".
No IPC document is in this tree and neither is buyable free, so the rule carried SOURCE_UNVERIFIED and every
board's power verdict rested on a constant nobody could look up.

ECSS-Q-ST-70-12C (14 July 2014), Annex D, publishes closed-form curve fits of three models with their
constants and a worked example. The clauses used are transcribed in v2/vendor/standards/. These rules hold the
three things that make the citation worth having: the tool reproduces the standard's own example, the
project's own bar IS the published model, and the places where the document does not cover us are named.
"""
import os, sys, math

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
import track_current as tc                                             # noqa: E402
import dc_drop                                                         # noqa: E402

DOC = os.path.join(os.path.dirname(TOOLS), "..", "vendor", "standards",
                   "ecss-q-st-70-12c-2014-07-14.md")


def _rating(consts, area_mm2, dT):
    """The Annex D formula with any constants, so a wrong set can be shown to fail."""
    k0, k1, m0, m1 = consts
    return k0 * (dT ** k1) * ((tc.C1 * area_mm2) ** (m0 * (dT ** m1)))


def t_the_tool_reproduces_the_standards_own_worked_example():
    """D.1.3: 1 A at 5 K on a 0.925 by 0.025 mm track, under the D.2 (IPC-2152) constants."""
    got = tc.rating(0.925 * 0.025, 5.0, "IPC-2152")
    assert abs(got - 1.0) < 0.002, got
    back = tc.area_for(1.0, 5.0, "IPC-2152") / 0.025
    assert abs(back - 0.925) < 0.002, back


def t_wrong_constants_fail_that_example():
    """The defective fixture. A formula that reproduces a published example is evidence; a formula that would
    reproduce it whatever its constants is not, and this rule is what tells the two apart."""
    for bad in ((0.0240, 0.4393, 0.7252, 0.0002),        # the IPC-2221A fit: a real set, the WRONG one here
                (0.0756, 0.4375, 0.5000, 0.0000),        # m1 dropped, which is the easy typo
                (0.0765, 0.4375, 0.5000, 0.0301)):       # two digits transposed in k0
        got = _rating(bad, 0.925 * 0.025, 5.0)
        assert abs(got - 1.0) >= 0.002, ("constants %s reproduce the example too, so the example proves "
                                         "nothing about the constants: %.4f A" % (bad, got))


def t_this_projects_own_bar_is_a_published_model_and_never_above_one():
    """RE-STATED FOR DECISION 35 (21 September 2026). It used to pin `dc_drop`'s internal bar to the D.4
    constants alone, which was right while IPC-2221A was the only model in use and became FALSE the moment the
    ruling took the most conservative of the three: above 0.1706 mm2 at 10 K the bar is CNES's and the old
    assertion fails on a tool that is doing what it was ruled to do.

    What survives, and is the property worth holding: the bar is one of the PUBLISHED Annex D models at every
    geometry these boards use, and it is never ABOVE any of them. A bar that reads higher than a published
    model is the thing decision 35 ruled out, and a bar that is not any model's number at all would be this
    project inventing one."""
    worst_above = 0.0
    for w in (0.2, 0.25, 0.4, 0.5, 1.0, 2.0, 3.0, 6.0):
        for t in (0.0152, 0.0175, 0.035, 0.070):
            for dT in (5.0, 10.0, 20.0):
                a = w * t
                mine = dc_drop.ipc_limit(a, dT, internal=True)
                published = [tc.rating(a, dT, m) for m in tc.MODELS]
                assert any(abs(mine - p) / p < 0.01 for p in published), \
                    "dc_drop's bar at %.4f mm2, %.0f K is no published model's number" % (a, dT)
                worst_above = max(worst_above, (mine - min(published)) / min(published))
    assert worst_above < 0.01, "dc_drop's bar reads %.2f percent ABOVE the lowest published model" % (100 * worst_above)


def t_the_external_factor_is_not_claimed_to_be_sourced():
    """Annex D fits the INTERNAL conductor curve only (D.4's first sentence), so the factor of two on an outer
    layer is still this project's own number. The rule must say so, and the transcription must say so."""
    assert abs(dc_drop.ipc_limit(1.0, 10.0, internal=False) /
               dc_drop.ipc_limit(1.0, 10.0, internal=True) - 2.0) < 1e-9
    body = open(DOC, encoding="utf-8").read()
    assert "external" in body.lower() and "PARTIALLY_VERIFIED" in body, \
        "the transcription does not record that the external factor is unsourced"
    import yaml
    reg = yaml.safe_load(open(os.path.join(TOOLS, "pcb_rules.yaml"), encoding="utf-8"))
    rule = {r["id"]: r for r in reg["rules"]}["PI-001"]
    assert rule["source_status"] == "PARTIALLY_VERIFIED", rule["source_status"]
    assert "external" in (rule.get("false_positive_analysis") or "").lower(), \
        "PI-001 does not name the constant it cannot cite"


def t_the_two_models_cross_and_the_tool_knows_where():
    """Both fits are functions of area alone, so the crossover is one area per temperature rise. Above it the
    model this project judges with reads HIGHER than the standard that supersedes it, which is a wrong PASS
    rather than a wrong refusal and is the reason it is reported on every conductor past the line."""
    for dT, want in ((5.0, 0.194), (10.0, 0.268), (20.0, 0.388)):
        got = tc.crossover(dT)
        assert abs(got - want) < 0.002, (dT, got, want)
        assert tc.rating(got * 0.9, dT, "IPC-2221A") < tc.rating(got * 0.9, dT, "IPC-2152")
        assert tc.rating(got * 1.1, dT, "IPC-2221A") > tc.rating(got * 1.1, dT, "IPC-2152")


def t_the_published_validity_range_is_recorded_and_this_project_is_outside_it():
    """D.4 a publishes the range the IPC-2221A fit is valid over: 1.2 A at 10 K. The pack node carries 10."""
    ok, why = tc.valid_for_ipc2221a(0.5, 10.0)
    assert ok, why
    ok, why = tc.valid_for_ipc2221a(10.0, 10.0)
    assert not ok and "OUTSIDE" in why, why


def t_the_transcription_carries_its_provenance():
    """A transcription without the document it came from is a claim. The file names the issuer, the issue date,
    the URL, the sha256 of the PDF that was read and the clauses taken."""
    body = open(DOC, encoding="utf-8").read()
    for token in ("ECSS-Q-ST-70-12C", "14 July 2014", "ecss.nl", "sha256",
                  "01d7fd413efd071c4c17d4bed80a72eadb582b73dbc72dfb7581d8a042ba026a",
                  "D.1.2", "D.2", "D.3", "D.4"):
        assert token in body, "the transcription does not carry %s" % token
    assert "0,0756" in body and "0,0240" in body, "the constants are not transcribed as the standard writes them"


def t_the_density_verdict_reports_the_density_and_not_the_drop():
    """Board A's four current-density misses read "MISSED VBAT on current density: 0.38% of 14.4 V", a voltage
    figure beside the word density, and 0.38 percent of 14.4 V is a PASS of the OTHER criterion. A verdict whose
    evidence is a number from a different rule cannot be read by anyone, and this is the third time in this tree
    that one rule's number has decided or described another's."""
    src = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    body = src[src.index("def _evidence("):src.index("dens_rows = _rows(")]
    assert 'kind == "current density"' in body, "the two verdicts still share one evidence format"
    assert "r[5]" in body, "the density evidence does not carry the density ratio"
    # the defective fixture: the line as it was, which formats r[4] for both kinds
    before = ('    def _evidence(rows, kind):\n'
              '        return [("%s %s NOT JUDGED" % (r[1], r[0])) if r[4] is None else\n'
              '                ("%s %s on %s: %.2f%% of %.1f V" % (r[1], r[0], kind, r[4] * 100, rails[r[0]]["volts"]))\n'
              '                for r in rows]\n')
    assert 'kind == "current density"' not in before and "r[5]" not in before, \
        "the rule does not distinguish the text it was written against"


def t_the_density_verdict_no_longer_calls_its_own_limit_unsourced():
    """The note said the limit "has no authoritative text in this tree". It has one now, and a verdict that
    disclaims its own source after the source arrives is as wrong as one that claims a source it lacks."""
    src = open(os.path.join(TOOLS, "dc_drop.py"), encoding="utf-8").read()
    i = src.index('_v.write("dc_density"')
    note = src[i:i + 2000]
    assert "ECSS-Q-ST-70-12C" in note, "the density verdict does not cite the document behind its limit"
    assert "no authoritative text in this tree" not in note, "the verdict still disclaims a source it has"
