"""Record l4lim (Layer 4 task L4A-101, MESHSAT-1357, 7 October 2026; v2/docs/records/l4lim/): the limiter window screen before
L4A-56 and L4A-57 (W127's finding 3 on method M-A for RE-6 and RE-7). A screen, not an acceptance.

The predicates: the committed .out is what the script prints (where the held-back sheets and pdftotext are present); the band
functions reproduce the makers' tested rows from their own equations and widen with the resistor's tolerance; the window check
FAILS on the failure case the screen exists for (the AP2112K's 125 C current at the corner against row 7's peak: no band) and
holds once the regulator's junction-to-ambient is low enough, while the AP2112's own packages do not; T10-A3's requirement
reproduces from record l9t5's modules; the screen refuses a maker's sheet without its latch-off sentence and a record l9t5 output
whose served rows no longer read; the fetch script pins exactly the held sheets the screen reads; the page carries the output's
key figures, no em or en dash and no claim word. Nothing here writes the tree."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys

TESTS = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(TESTS)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = os.path.join(ROOT, "v2", "docs", "records", "l4lim")
SCRIPT = os.path.join(REC, "l4lim_screen.py")
OUT = os.path.join(REC, "l4lim_screen.out")
PAGE = os.path.join(REC, "L4LIM-SCREEN.md")
FETCH = os.path.join(REC, "fetch_held_back.py")
sys.path.insert(0, TESTS)
from harness import need, Skip  # noqa: E402

CLAIM = re.compile(r"\b(certified|compliant|qualified|proven|guaranteed|withstands|survives)\b|\brated for\b", re.I)
TI = {"min": (25230.0, 1.016), "max": (22980.0, 0.94)}       # SLVS841F 9.5.1 equation (1), as the script parses them
_C = {}


def _M():
    if "m" not in _C:
        need(SCRIPT, "record l4lim's screen script")
        sp = importlib.util.spec_from_file_location("l4lim_screen_under_test", SCRIPT)
        m = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(m)
        _C["m"] = m
    return _C["m"]


def _have_sheets():
    m = _M()
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is not on this host: the makers' rows cannot be read")
    absent = [v[0] for v in m.SHEETS.values() if not os.path.isfile(os.path.join(ROOT, v[0]))]
    if absent:
        raise Skip("held-back sheets absent (%s): fetch with v2/docs/records/l4lim/fetch_held_back.py" % ", ".join(sorted(absent)))


def t_the_committed_output_is_what_the_script_prints():
    _have_sheets()
    r = subprocess.run([sys.executable, "-B", SCRIPT], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr.decode()[-400:]
    assert r.stdout == open(OUT, "rb").read(), "l4lim_screen.out is not what l4lim_screen.py prints; regenerate it with _bin/regen_out.py"
    t = r.stdout.decode()
    for s in ("8. THE LINE FOR L4A-56\n   CHANGE-METHOD", "so W1 is CLOSED at 184 C/W for both candidates", "W1 holds on the served side",
              "l4lim_screen: done"):
        assert s in t, s
    # the T10 line the screen cites is read, not typed (W159 on W157-F3: on row (b)'s composite it is 643, on fnd/l4lim's base 612)
    mm = re.search(r"\(T10 line (\d+) prints 3\.6524 against 3\.5213\): EQUAL", t)
    assert mm, "the screen's T10-A3 reproduction is not printed"
    t10 = open(os.path.join(ROOT, "v2", "docs", "records", "l9t5", "l9t5_t10.out"), encoding="utf-8").read().splitlines()
    i = int(mm.group(1)) - 1                                         # the statement starts on the cited line and may wrap once
    pair = [t10[i]] + ([t10[i + 1]] if i + 1 < len(t10) else [])   # the cited line and the one it may wrap onto
    assert "3.6524 V against 3.5213 V" in " ".join(" ".join(pair).split()), "the cited T10 line does not carry the figures"
    assert " NO\n" not in t.split("9. THE PREDICATES")[1], "a predicate reads NO"


def t_the_band_functions_reproduce_the_makers_rows():
    m = _M()
    lo, hi = m.band_eq(TI, 210.0, 0.0)                     # TI's own tested row at 210 kOhm: 110 / 130 / 150 mA
    assert abs(lo - 0.110) < 0.002 and abs(hi - 0.150) < 0.002, (lo, hi)
    lo0, hi0 = m.band_eq(TI, 102.0, 0.0)
    lo1, hi1 = m.band_eq(TI, 102.0, 0.01)
    assert lo1 < lo0 < hi0 < hi1, "the resistor's tolerance must widen the band both ways"
    lo, hi = m.band_row((0.475, 0.520, 0.565), TI, 0.01)    # the 49.9 kOhm tested row, widened through the exponents
    assert 0.469 < lo < 0.475 and 0.565 < hi < 0.571, (lo, hi)
    assert m.band_row((0.475, 0.520, 0.565), TI, 0.0) == (0.475, 0.565)


def t_the_window_fails_on_its_failure_case_and_holds_with_the_companion():
    m = _M()
    drop, air, tj = 0.8669, 76.25, 125.0
    i125 = lambda th: (tj - air) / (th * drop)             # noqa: E731
    assert abs(i125(184.0) - 0.3056) < 5e-5
    # the failure case: the AP2112K's 125 C current against row 7's peak (S3' 0.4240 A): no E96 band at any resistor
    assert m.best_r(TI, (15.0, 232.0), i125(184.0), 0.4240) is None
    # with the sustained served state as the floor a band exists, but its minimum is under normal service's own peak (S2)
    r = m.best_r(TI, (15.0, 232.0), i125(184.0), 0.1855)
    assert r is not None and r[0] == 102.0 and r[2] <= i125(184.0) and r[1] < 0.2839, r
    # the companion: the 49.9 kOhm row clears row 7's peak; 98 C/W holds 125 C at its maximum, every AP2112 package fails
    lo, hi = m.band_row((0.475, 0.520, 0.565), TI, 0.01)
    assert lo > 0.4240 and i125(98.0) >= hi
    assert all(i125(th) < hi for th in (184.0, 114.0, 120.0))


def t_t10_a3_reproduces_from_record_l9t5():
    if shutil.which("pdftotext") is None:
        raise Skip("pdftotext is not on this host")
    m = _M()
    P = m.T.figures()
    assert abs(m.need_at(P, 0.2452) - 3.5213) < 5e-5
    assert m.need_at(P, 0.5704) > m.need_at(P, 0.3002) > m.need_at(P, 0.2452), "the requirement must rise with the current"


def t_a_sheet_without_its_latch_sentence_is_refused():
    _have_sheets()
    m = _M()
    t = m.pdf("tps2553")
    m._PDF["tps2553"] = t.replace("is reached and the device is latched off", "is reached and the device restarts")
    try:
        m.sheets()
    except SystemExit as e:
        assert e.code == 2
    else:
        raise AssertionError("the screen read a TPS255x sheet without its latch-off sentence")
    finally:
        m._PDF["tps2553"] = t
    m.sheets()                                              # and the true sheet reads


def t_an_output_whose_served_rows_no_longer_read_is_refused():
    m = _M()
    need(os.path.join(ROOT, m.T10_OUT), "record l9t5's T10 output")
    orig = m.text
    m.text = lambda p: orig(p).replace("none trips", "one trips") if p == m.T10_OUT else orig(p)
    try:
        m.edges()
    except SystemExit as e:
        assert e.code == 2
    else:
        raise AssertionError("the screen read a T10 output whose served rows no longer read")
    finally:
        m.text = orig
    assert m.edges()["s1"][0] == 0.1855


def t_the_fetch_script_pins_the_held_sheets_the_screen_reads():
    src = open(FETCH, encoding="utf-8").read()
    pins = dict(re.findall(r'\("(v2/vendor/[^"]+)", "https://[^"]+",\s*\n\s*"([0-9a-f]{64})"\)', src))
    held = sorted(v[0] for v in _M().SHEETS.values() if v[1])
    assert sorted(pins) == held, (sorted(pins), held)
    for rel, want in pins.items():
        p = os.path.join(ROOT, rel)
        if os.path.isfile(p):
            assert hashlib.sha256(open(p, "rb").read()).hexdigest() == want, rel


def t_the_page_carries_the_output_figures_and_no_dash():
    page = open(PAGE, encoding="utf-8").read()
    out = open(OUT, encoding="utf-8").read()
    assert chr(0x2014) not in page and chr(0x2013) not in page and chr(0x2014) not in out
    assert not CLAIM.search(page) and not CLAIM.search(out), (CLAIM.search(page) or CLAIM.search(out)).group(0)
    assert page.startswith("**Status: DONE")
    for s in ("CHANGE-METHOD", "0.3056 A", "0.4240 A", "98.6 C/W", "103.3 C/W", "62.5 uF", "121.4 uF", "3.6936 V", "0.2399 V",
              "23.5 mJ", "0.4702 to 0.5704 A", "1.7111 A"):
        assert s in page and s in out, s
