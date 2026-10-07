"""Layer 4 task L4A-55, record l9t5 (MESHSAT-1357, 7 October 2026, W139; v2/docs/records/l9t5/): the quorum service of the three I/O
supervisors under method M-B, held as predicates on what l9t5_canq.py computes and on the files of the round, with MUTANTS that must
FAIL the acceptance.

The predicates: the committed l9t5_canq.out is what the script prints, and every input it pins is present at the sha256 it names;
every acceptance predicate of its section 9 holds (CON-004's two fabrics kept, every single-fault row at its required outcome on both
self-test schedules, no healthy controller silenced on both fabrics, no conforming controller voted off, no surviving pair at the loss
count, every latent fault bounded or a named residual, every contained state returning, the contract draft composing after t10's and
refusing twice and the tree); the rows the brief names exist (IOHA rows 3, 5, 7, 8, A7 as written, the GPIO-toggled TX, the babbler,
a stuck vote output high and low, the two-faced controller, the self-test against a real fault on the other fabric, W137's four
residuals, W137-F1, W138's latch); the latent bounds and the recovery bounds. The mutants, each of which must FAIL: a removed fabric,
a third fabric, CON-004 read with another count, no attribution, a 1-of-1 vote, a strike on a TXD reading alone, a vote never
released, a loss count of one window, FW-B21's stop as drafted, W137's precondition read literally, a contract draft that lacks a
figure. These are predicates on a desk MODEL: they establish no electrical property and close nothing; nothing in the kit has been
built, bought, powered or measured.

Runs under the suite's runner (`env -C v2/ecad/tools python3 tests/run.py test_l9t5_canq.`); about three minutes (the full scan once,
the mutants on the quick scan)."""
import contextlib
import importlib.util
import io
import os
import re
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need, Skip  # noqa: E402

REC = os.path.join(ROOT, "v2", "docs", "records", "l9t5")
SCRIPT = os.path.join(REC, "l9t5_canq.py")
OUT = os.path.join(REC, "l9t5_canq.out")
DRAFT = os.path.join(REC, "apply_hw_fw_contract_canq.py")
PAGE = os.path.join(REC, "T10-CANQ.md")
_M = {}


def mod():
    if "m" not in _M:
        sp = importlib.util.spec_from_file_location("l9t5_canq_under_test", need(SCRIPT, "l9t5_canq.py"))
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _M["m"] = m
    return _M["m"]


def full():
    if "res" not in _M:
        _M["res"] = mod().analyse()
    return _M["res"]


def acc(res):
    return dict((name.split(" ")[0], ok) for name, ok in res["acceptance"][0])


def quick(cfg=None, only=None, latent=False, recover=False):
    return mod().analyse(cfg, scan="quick", only=only, latent=latent, recover=recover)


# ---------------------------------------------------------------------------------------------------------- the committed record
def t_out_is_the_script_output():
    m = mod()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m.render(full())
    assert buf.getvalue() == open(need(OUT, "l9t5_canq.out"), encoding="utf-8").read(), "l9t5_canq.out is not what the script prints"


def t_every_pin_holds():
    import hashlib
    t = open(need(OUT, "l9t5_canq.out"), encoding="utf-8").read()
    pins = re.findall(r"^\s+([0-9a-f]{16}) (v2/\S+)$", t, re.M)
    assert len(pins) >= 20, "too few inputs pinned"
    for h, p in pins:
        got = hashlib.sha256(open(need(os.path.join(ROOT, p), p), "rb").read()).hexdigest()[:16]
        assert got == h, "%s pinned %s, is %s" % (p, h, got)


def t_record_hygiene():
    for p in (SCRIPT, OUT, DRAFT, PAGE, os.path.abspath(__file__), os.path.join(REC, "inputs", "SOURCES-canq.txt")):
        t = open(need(p, os.path.basename(p)), encoding="utf-8").read()
        assert chr(0x2014) not in t and chr(0x2013) not in t, "a long dash in %s" % os.path.basename(p)
        for bad in ("/" + "home" + "/", "/" + "tmp" + "/"):
            assert bad not in t, "a private path in %s" % os.path.basename(p)


# ---------------------------------------------------------------------------------------------------------- the analysis itself
def t_acceptance_holds():
    A = acc(full())
    assert all(A.values()), "acceptance: %s" % [k for k, v in A.items() if not v]
    assert set(A) == {"A%d" % i for i in range(1, 11)}


def t_the_rows_the_brief_names():
    rows = {rid for (v, rid) in full()["rows"]}
    for rid in ("R3", "R5a", "R5b", "R5c", "R7a", "R7b", "R7c", "R7e", "R8a", "R8b", "R8c", "M1a", "M1b", "M1c", "M1d", "M1e", "M1f",
                "M2a", "M3a", "M3b", "M4a", "M5a", "M5b", "M5c", "M5d", "M5e", "Q1", "Q2", "Q3", "Q4", "F1", "F2"):
        assert rid in rows, rid
    sc = {rid: r["sc"] for (v, rid), r in full()["rows"].items()}
    assert "row 3" in sc["R3"].ioha and "row 5" in sc["R5a"].ioha and "row 7" in sc["R7a"].ioha and "row 8" in sc["R8a"].ioha
    assert "A7" in sc["R7a"].ioha and "A7" in sc["R7b"].ioha


def t_outcomes_as_required():
    res = full()
    O = {(v, rid): r["outcome"] for (v, rid), r in res["rows"].items()}
    for v in ("restated", "w137"):
        assert O[(v, "R3")] == 1 and O[(v, "R5a")] == 1 and O[(v, "R5b")] == 1
        for rid in ("R7a", "R7b", "R7c", "R7d", "R7e", "R7f", "R7g", "M3a", "M3b", "M5a", "M5b"):
            assert O[(v, rid)] == 2, (v, rid)
        for rid in ("M1b", "M1c", "M1d", "M1e", "M1f", "M2a", "M4a"):
            assert O[(v, rid)] == 1, (v, rid)
        assert O[(v, "R8a")] == 0 and O[(v, "R8b")] == 0      # row 8: 'nothing moves', accepted
        assert O[(v, "D2")] == 0 and O[(v, "D3")] == 0        # double faults print their loss
    assert O[("restated", "F2")] == 0                         # FW-B21's stop as drafted loses the quorum


def t_containment_on_printed_timing():
    m, res = mod(), full()
    ch = m.chain(res["cfg"], res["P"])
    assert abs(ch["path"] - (16.6e-3 + 6e-3 + 10.0)) < 1e-9
    assert abs(ch["total"] - 1310.0226) < 1e-3 and abs(ch["total_held"] - 1034.0226) < 1e-3
    for rid in ("M1a", "M1b", "M1c"):
        assert abs(res["rows"][("restated", rid)]["silence_us"] - ch["total"]) < 1e-6, rid


def t_latent_bounds():
    res = full()
    r = {(a[0], a[1]): a[4] for a in res["latent"]["restated"]}
    w = {(a[0], a[1]): a[4] for a in res["latent"]["w137"]}
    for k, v in r.items():
        assert v in ("residual", "phase") or (isinstance(v, float) and v <= 3.0), (k, v)
    residuals = [k for k, v in r.items() if v == "residual"]
    assert len(residuals) == 4, residuals
    att = [k for k in r if k[0].startswith("a reader's attribution path")][0]
    assert isinstance(r[att], float) and w[att] is None       # W139-F8: W137's V phase never runs the attribution path
    for k, v in w.items():
        if k != att and isinstance(v, float):
            assert v <= res["P"]["mb_interval_s"], (k, v)
    assert res["latent_degraded"]["restated"] is not None and res["latent_degraded"]["w137"] is None
    assert res["latent_literal"] is None                       # W139-F5
    assert res["latent_dar0"] is None                          # W137-F1: DAR = 0 breaks the restated cycle


def t_recovery():
    res = full()
    b = res["bounds"]
    R = {r[0]: r for r in res["recovery"]}
    assert R["RC1"][2] is not None and R["RC1"][2] <= b["silenced"]
    assert R["RC2"][2] is not None and R["RC2"][2] <= b["dark"]
    assert R["RC3"][2] is not None and R["RC3"][2] <= b["fabric"]
    assert R["RC5"][2] is not None and R["RC5"][2] <= res["cfg"]["window_us"]
    assert R["RC6"][2] is not None and R["RC6"][2] <= b["silenced"]
    s = R["RC4"][4]
    assert s["holds"][:7] == [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0] and s["gap"] < res["cfg"]["n_loss"]


def t_contract_draft_steps():
    row, vrow, missing, steps = full()["contract"]
    assert not missing
    assert [c for _, c in steps] == [3, 0, 0, 0, 3, 0, 3, 0], steps
    assert "never on a TXD reading alone" in row and "two copies that differ" in row


def t_con004_restated_not_amended():
    I = full()["I"]
    assert I["con004"] == ("Each I/O supervisor has its own regulator branch, reset supervisor, watchdog, crystal and SWD pads, and the "
                           "three talk over two independent CAN-FD fabrics with separate transceivers and termination.")
    assert I["con004_fabrics"] == 2


# ---------------------------------------------------------------------------------------------------------- mutants: each FAILS
def t_mutant_removed_fabric_fails():
    res = quick({"fabrics": ("A",)}, only=("R7a", "R7c", "M1a"))
    A = acc(res)
    assert A["A1"] is False and A["A2"] is False


def t_mutant_third_fabric_fails():
    res = quick({"fabrics": ("A", "B", "C")}, only=("R3",))
    A = acc(res)
    assert A["A1"] is False and A["A3"] is False


def t_mutant_con004_other_count_fails():
    m = mod()
    res = quick(only=("R3",))
    res["I"] = dict(res["I"], con004_fabrics=0)
    A = dict((n.split(" ")[0], ok) for n, ok in m.acceptance(res)[0])
    assert A["A1"] is False


def t_mutant_no_attribution_fails():
    A = acc(quick({"k": 99}, only=("M1b", "M1d")))
    assert A["A2"] is False


def t_mutant_one_of_one_vote_fails():
    res = quick({"vote_rule": "1of1"}, only=("M3c",))
    A = acc(res)
    assert A["A4"] is False and A["A2"] is False


def t_mutant_txd_reading_alone_fails():
    A = acc(quick({"evidence": False}, only=("O1",)))
    assert A["A5"] is False


def t_mutant_vote_never_released_fails():
    res = quick({"t_hold_us": 1.0e12, "t_hold_cap_us": 1.0e12}, only=("R3",), recover=True)
    A = acc(res)
    assert A["A8"] is False


def t_mutant_loss_count_one_window_fails():
    A = acc(quick({"n_loss": 1}, only=("M1b", "M1c")))
    assert A["A2"] is False or A["A6"] is False


def t_mutant_fwb21_stop_as_drafted_fails():
    A = acc(quick({"stop_windows": 1}, only=("M1c",)))
    assert A["A2"] is False


def t_mutant_w137_literal_precondition_finds_nothing():
    m = mod()
    P, Q = m.figures()
    d = m.detect({"own_dead": {("A", "A")}}, dict(m.CFG, variant="w137", w137_literal=True), P, "quick")
    assert d is None
    d = m.detect({"own_dead": {("A", "A")}}, dict(m.CFG, variant="w137"), P, "quick")
    assert d is not None


def t_mutant_contract_lacking_a_figure_fails():
    m = mod()
    keep = m.CONTRACT_FIGS
    try:
        m.CONTRACT_FIGS = keep + ("a figure the draft does not carry",)
        res = quick(only=("R3",))
        A = acc(res)
        assert A["A9"] is False
    finally:
        m.CONTRACT_FIGS = keep


# pytest aliases
for _n, _f in list(globals().items()):
    if _n.startswith("t_") and callable(_f):
        globals()["test_" + _n[2:]] = _f
