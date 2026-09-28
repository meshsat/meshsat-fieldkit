"""intent.bypass takes a class and a basis, and intent.write refuses an entry without one (decision 42, T5).

DECOUPLING.md 8.1 T5: "`intent.bypass` takes a class and a basis (the maker clause), and `intent.write` refuses an entry
without one." Until 29 September 2026 the call took neither, and each of the six generators set the two keys on the
entry after the call. Both ways are read here: the keywords, and a key set before `write()`.

No KiCad: intent.py is plain Python. Every test restores the module's collected bypass list, because the suite runs
every test file in one process and the list is module state."""
import os, sys, json, tempfile, contextlib, io

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import intent
import decoupling_rules as dr

HERE = os.path.dirname(os.path.abspath(__file__))
BOARDS = [("pcb-a-power-a23", "pcb-a-power"), ("pcb-b-compute-b19", "pcb-b-compute"), ("pcb-c-display-c8", "pcb-c-display"),
          ("pcb-d-aprs-d9", "pcb-d-aprs"), ("pcb-e1-dock-e7", "pcb-e1-dock"), ("pcb-p-pack-p2", "pcb-p-pack")]


@contextlib.contextmanager
def _collected():
    saved = list(intent._I["bypass"]); intent._I["bypass"][:] = []
    try: yield
    finally: intent._I["bypass"][:] = saved


def _write():
    d = tempfile.mkdtemp(prefix="intent-t5-")
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        p = intent.write(os.path.join(d, "fixture.kicad_sch"), "fixture")
    return json.load(open(p)), out.getvalue()


def t_bypass_takes_a_class_and_a_basis_as_keywords():
    with _collected():
        intent.bypass("C1", "U1", 1, "+3V3", cls="D", basis="TI SCAA082A 2.4 p.13: 'directly with a via'")
        intent.bypass("C2", "U2", "5", "+3V3", **{"class": "L", "basis": "Diodes DS39724 p.1: 1.0 uF",
                                                   "value_floor": "1u", "esr_max": dr.NOT_STATED})
        e1, e2 = intent._I["bypass"]
        assert e1 == {"cap": "C1", "part": "U1", "pin": "1", "net": "+3V3", "class": "D",
                      "basis": "TI SCAA082A 2.4 p.13: 'directly with a via'"}, e1
        assert e2["class"] == "L" and e2["value_floor"] == "1u" and e2["esr_max"] == dr.NOT_STATED, e2
        d, _ = _write()
        assert [e["class"] for e in d["bypass"]] == ["D", "L"], d["bypass"]


def t_write_refuses_an_entry_with_no_class():
    with _collected():
        intent.bypass("C1", "U1", "1", "+3V3", basis="the maker's clause")
        try: _write()
        except SystemExit as x:
            assert "C1 -> U1.1" in str(x) and "class None" in str(x), str(x)
        else: raise AssertionError("an entry with no class was written")


def t_write_refuses_a_class_that_is_not_ruled_and_an_entry_with_no_basis():
    with _collected():
        intent.bypass("C1", "U1", "1", "+3V3", cls="bulk", basis="the maker's clause")
        intent.bypass("C2", "U1", "2", "+3V3", cls="D", basis="   ")
        try: _write()
        except SystemExit as x:
            m = str(x)
            assert "2 bypass entries" in m and "class 'bulk'" in m and "C2 -> U1.2: no basis" in m, m
        else: raise AssertionError("an unruled class and an empty basis were written")


def t_a_class_set_on_the_entry_before_write_is_read_as_the_generators_set_it():
    with _collected():
        intent.bypass("C1", "U1", "1", "+3V3")
        intent._I["bypass"][-1].update({"class": "D", "basis": "the maker's clause"})   # gen_sch_c.py's idiom
        d, _ = _write()
        assert d["bypass"][0]["class"] == "D"


def t_a_class_L_entry_without_its_floor_is_noted_by_name_and_not_refused():
    with _collected():
        intent.bypass("C9", "U9", "5", "+3V3", cls="L", basis="LDO output, the maker's 1 uF")
        d, printed = _write()
        assert d["bypass"][0]["cap"] == "C9"
        assert "C9: class L without `value_floor`" in printed and "C9: class L without `esr_max`" in printed, printed
        assert "noted, not refused" in printed, printed


def t_every_committed_intent_carries_a_ruled_class_and_a_basis_on_every_entry():
    # the property write() now enforces, read on the six boards' committed intent files (round 8 onward)
    bad = []
    for phase, stem in BOARDS:
        it = json.load(open(os.path.join(HERE, "..", "..", phase, "out", stem + "-intent.json"), encoding="utf-8"))
        for e in it.get("bypass", []):
            if e.get("class") not in dr.CLASSES or not str(e.get("basis") or "").strip():
                bad.append("%s %s" % (stem, e.get("cap")))
    assert not bad, bad
