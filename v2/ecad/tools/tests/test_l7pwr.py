"""Layer 7 record l7pwr (MESHSAT-1357, 3 October 2026; v2/docs/records/l7pwr/): the five IP68 fans selected (D-18, E11-35), the
T-H1 mock-up's bill and specimen, and the dock lead's pulse capability, held as predicates on what l7pwr_fans_th1.py computes.

The predicates: the committed .out is what the script prints and every pinned input is present with the sha256 the output names;
no candidate's printed operating range covers VSYS_E as drawn and no 5 V IP68 40 mm fan was read, so both picks need a 12 V feed
(the record's findings); the picks print REQ-043's -20 C and a life at 60 C and the alternatives do not; no maker prints a
starting current (E11-35's bench row stands); the picked mixers at full speed stay under L4-E11's per-fan start limit but take
VSYS_E over its declared 1.0 A while under U42's least limit; the picks add heat over the plan's fan figures; the cooler fan's
fit against the backer is a finding (under 3 mm); every T-H1 heater setting is sqrt(P x 6.8); the bill has totals and items
with no read price; the Onderdonk form reproduces its source's worked example, the hard short is a small fraction of the 24 AWG's
fusing current with a sub-kelvin adiabatic rise, and the retry setting is under the ECSS single-wire rating; the two pages carry
the output's figures; the record's files carry no long dashes and no claim words, the clarification is a plain-ASCII draft that
sends nothing; the filed documents are registered in SOURCES.yaml and sources.txt with their sha256; PROCUREMENT.md carries the
section. These are software predicates on the record's own text and arithmetic: they establish no property of any fan, case or
contact and buy nothing.
"""
import hashlib
import importlib.util
import os
import re
import shutil
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l7pwr")
SCRIPT = os.path.join(REC, "l7pwr_fans_th1.py")
OUT = os.path.join(REC, "l7pwr_fans_th1.out")
PAGE = os.path.join(REC, "L7-FANS-AND-TH1.md")
SPEC = os.path.join(REC, "T-H1-MOCKUP-SPEC.md")
CLAR = os.path.join(REC, "clarification", "preci-dip-813.txt")
sys.dont_write_bytecode = True
sys.path.insert(0, TOOLS)
from harness import need, Skip  # noqa: E402

_C = {}
CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)


def _M():
    if "M" not in _C:
        need(SCRIPT, "the l7pwr record")
        if shutil.which("pdftotext") is None:
            raise Skip("pdftotext is needed")
        sp = importlib.util.spec_from_file_location("l7pwr_fans_th1_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        for rel in m.PINS.values():
            need(os.path.join(ROOT, rel), "a pinned input of the l7pwr record")
        try:
            R = m.compute()
        except SystemExit as e:
            raise AssertionError("l7pwr_fans_th1.py refused (exit %s)" % e.code)
        _C.update(M=m, R=R, text=m.render(R))
    return _C["M"]


def _pred(key):
    _M()
    P = _C["R"]["pred"]
    assert key in P, "no predicate %r" % key
    return P[key]


def t_output_reproduced_byte_for_byte():
    _M()
    need(OUT, "the committed output")
    assert _C["text"] == open(OUT, encoding="utf-8").read(), "l7pwr_fans_th1.out is not what the script prints"


def t_every_input_is_pinned_and_present():
    m = _M()
    for key, rel in m.PINS.items():
        p = os.path.join(ROOT, rel)
        sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
        assert ("%s  sha256 %s" % (rel, sha[:16])) in _C["text"], "%s is not pinned at its current sha256" % rel


def t_no_candidate_covers_the_supply_and_the_picks_cover_the_cold_end():
    assert _pred("no candidate's printed range covers VSYS_E 9.494 to 17.375 V")
    assert _pred("no 5 V IP68 40 mm fan was read in the makers' lines")
    assert _pred("the picked mixer covers -20 C and prints a life at 60 C")
    assert _pred("the picked cooler fan covers -20 C and prints a life at 60 C")
    assert _pred("the alternatives fail REQ-043's -20 C or print no range")
    assert _pred("no candidate prints a starting current")
    R = _C["R"]
    assert R["sel"] == {"mixer": "9WL0612P4H001", "cooler": "9WPA0412P6G001"}
    for k in R["sel"].values():
        assert R["cands"][k]["ip"] == "IP68" and R["cands"][k]["tlo"] <= -20.0


def t_the_downstream_currents_and_heat():
    """Round 2 (set 28 F-14): the budget rests on the DRAFTED rails, parsed from L4-E11 section 18 and record l8r2; it must reproduce
    L4-E11's own figures, not a typed converter efficiency."""
    assert _pred("VSYS_E's drafted loads are U12 and U22, and +12V_FAN's the two mixers at the fan's printed current")
    assert _pred("U22's input recomputed from the parsed draft and L4-E11's floor equals L4-E11's printed input within 0.0005 A")
    assert _pred("VSYS_E at full speed equals L4-E11's declared current within 0.0005 A and the draft's declaration within 0.005 A, under U42's least limit")
    assert _pred("the start room recomputed matches L4-E11's multiple of the running power within 0.05")
    assert _pred("the drafted 12 V rails sit inside the picked fans' printed 10.8 to 13.2 V (D-18 holds)")
    assert _pred("the picked fans at full speed add heat over the plan's fan figures")
    m = _M()
    assert not hasattr(m, "BUCK_EFF"), "a typed converter efficiency is back: the drafts' own figures are the input"
    D = _C["R"]["down"]
    assert D["heat_hold_full"] > D["heat_hold_fans_only"], "the converters' losses must be counted in the heat"


def t_round_two_names_the_figures_that_moved():
    _M()
    t = _C["text"]
    assert "8. ROUND 2 (set 28 F-14): THE FIGURES THAT MOVED" in t
    old = _C["R"]["round1"]
    assert len(old) >= 10 and all(isinstance(v, float) for v in old.values()), "round 1's figures are parsed from its output"


def t_the_fit_is_a_finding_not_a_pass():
    assert _pred("the 40 x 40 x 20 fan on the cooler clears the backer's underside by under 3 mm (a fit finding)")
    M = _C["R"]["mount"]
    assert M["fan_in_cooler_width"] and 0.0 < M["clear_backer_env"] < 1.0


def t_the_th1_bill_and_heaters():
    assert _pred("every T-H1 heater setting is sqrt(P x 6.8) to 0.01 V")
    assert _pred("the bill's EUR total is over 600 and under 700")
    assert _pred("the bill has items with no read price")
    B = _C["R"]["bill"]
    assert set(B["totals"]) == {"EUR", "GBP", "USD"}
    assert len(_C["R"]["th1"]["lines"]) == 10 and len(_C["R"]["th1"]["rows"]) == 7


def t_the_dock_lead_relations():
    assert _pred("the Onderdonk form reproduces the note's worked example (178 A) within 1 A")
    assert _pred("the hard short is under 3 percent of the 24 AWG fusing current at 4.5 us and 70 C")
    assert _pred("the pulse's adiabatic rise in the 24 AWG is under 1 K")
    assert _pred("the retry setting is under the ECSS single-wire rating")
    K = _C["R"]["dock"]
    assert K["fus"][70.0] < K["fus_minus"], "the 234 + Ta form must be the conservative one"
    assert abs(K["cmil"] - 404.0) < 0.5


def t_the_pages_carry_the_outputs_figures():
    _M()
    R = _C["R"]
    page = open(PAGE, encoding="utf-8").read(); spec = open(SPEC, encoding="utf-8").read()
    for s in ("9WL0612P4H001", "9WPA0412P6G001", "%.4f A" % R["down"]["vsys_e_total_full"], "%.2f W" % R["down"]["heat_hold_full"], "%.2f" % R["bill"]["totals"]["EUR"], "%.0f" % R["dock"]["fus"][70.0],
              "%.3f K" % R["dock"]["rise_k"], "%.2f mm" % R["mount"]["clear_backer_cooler"], "GF60151B7-1E00U-AE9", "GF40282B3-1000U-SEP"):
        assert s in page, "the page does not carry %r" % s
    for s in ("%.2f" % R["bill"]["totals"]["EUR"], "%.2f" % R["bill"]["totals"]["GBP"], "%.2f" % R["bill"]["totals"]["USD"], "9WL0612P4H001", "9WPA0412P6G001", "13.07 V", "2.455 W/K"):
        assert s in spec, "the spec page does not carry %r" % s


def t_record_hygiene_no_long_dashes_no_claim_words_and_a_draft_that_sends_nothing():
    files = [PAGE, SPEC, SCRIPT, CLAR, os.path.join(REC, "README.md")] + [os.path.join(REC, "inputs", f) for f in os.listdir(os.path.join(REC, "inputs")) if f.endswith(".md")]
    for p in files:
        t = open(p, encoding="utf-8").read()
        assert "—" not in t and "–" not in t, "a long dash in %s" % os.path.basename(p)
        m = CLAIM.search(t)
        assert not m, "a claim word %r in %s" % (m.group(0), os.path.basename(p))
    c = open(CLAR, encoding="utf-8").read()
    assert all(ord(ch) < 128 for ch in c), "the clarification is not plain ASCII"
    assert c.startswith("Draft for the owner to send (the session contacts no outside party).")
    for s in ("566 A", "4.5 microseconds", "1.80 A", "0.75", "20 mOhm", "7A peak", "sales@precidip.com"):
        assert s in c, "the draft lacks %r" % s


def t_the_filed_documents_are_registered_with_their_sha256():
    import yaml
    d = yaml.safe_load(open(os.path.join(ROOT, "v2", "vendor", "SOURCES.yaml"), encoding="utf-8"))
    block = d.get("documents_filed_l7pwr")
    assert block and len(block) >= 6
    src = open(os.path.join(ROOT, "v2", "vendor", "sources.txt"), encoding="utf-8").read()
    seen = set()
    for e in block:
        p = os.path.join(ROOT, e["path"])
        assert os.path.exists(p), "%s is registered but absent" % e["path"]
        if e["path"].endswith(".pdf"):
            sha = hashlib.sha256(open(p, "rb").read()).hexdigest()
            assert e["sha256_of_the_file_read"] == sha, "%s: sha256 differs from the registered one" % e["path"]
            assert sha in src, "%s: no sources.txt line carries its sha256" % e["path"]
        seen.add(e["path"])
    for rel in ("v2/vendor/fans/sunon-ip56-ip68-gr487-fan-series-239-E-2023-04-07.pdf", "v2/vendor/fans/samesky-cfm-60bg68-dc-axial-fan-2024-09-12.pdf",
                "v2/vendor/cm5/rpi-cm5-cooler-product-brief-2024-12.pdf", "v2/vendor/precidip/precidip-catalog-slc-2018-03-20.pdf", "v2/vendor/fans/sanyo-denki-splash-proof-fan-pages-2026-10-03.md"):
        assert rel in seen, "%s is not in documents_filed_l7pwr" % rel
        assert rel[len("v2/vendor/"):] in src, "%s has no sources.txt line" % rel


def t_procurement_carries_the_section():
    t = open(os.path.join(ROOT, "v2", "docs", "parts", "PROCUREMENT.md"), encoding="utf-8").read()
    assert "## 8. Layer 7's fan picks and the T-H1 mock-up set (record l7pwr, 3 October 2026)" in t
    for s in ("9WL0612P4H001", "9WPA0412P6G001", "EUR 639.76", "documents_filed_l7pwr"):
        assert s in t, "PROCUREMENT.md section 8 lacks %r" % s
