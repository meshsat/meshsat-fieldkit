#!/usr/bin/env python3
"""A layout constraint sheet is bound to the inputs it was computed from (constraints_bound.py, MESHSAT-1357,
27 September 2026; the independent review of handover H2, finding 3 A).

THE DEFECT THESE HOLD. At H2 board A's sheet said VIN_RAW 12.31 A and 11.92 mm on one outer face while the committed
intent file declared 14.10 A, and nothing compared the two. The first fixture below is that defect with its own
numbers: a sheet written when the intent file said 12.31 A, and the intent file edited to 14.10 A afterwards.

THE FIXTURES are a tiny tree of their own in a temporary directory: one board (A, at the paths rail_widths.py names
for it), its netlist, its intent file, its sheet and the calculation's output, every one of them written by the
tools under test from the fixture's own intent file, never copied from this tree. The code is this tree's; the files
it reads are the fixture's. One test, the last group, judges the REAL tree, and it must pass at every commit that
touches a sheet, an intent file, a netlist or the calculation.
"""
import os, sys, json, shutil, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import constraints_bound as CB
from harness import Skip

RW = CB.load_calc()
A_DIR = ("v2", "ecad", "pcb-a-power-a23", "out")
SHEETS = ("v2", "docs", "layout-constraints")


def _intent(vin_raw=12.31, extra=None, drop=()):
    rails = {
        "CELL+": {"volts": 14.4, "v_work": 16.8, "amps_typ": 10.0, "amps_peak": 18.0},
        "CELL_FUSED": {"volts": 14.4, "v_work": 16.8, "amps_typ": 10.0, "amps_peak": 18.0, "series_of": "CELL+"},
        "VBAT": {"volts": 14.4, "v_work": 16.8, "amps_typ": 10.0, "amps_peak": 18.0, "fed_from": "CELL_FUSED"},
        "VIN_RAW": {"volts": 12.0, "v_work": 36.0, "amps_typ": vin_raw, "amps_peak": vin_raw},
        "+3V3": {"volts": 3.3, "amps_typ": 0.3, "amps_peak": 0.6},
    }
    rails.update(extra or {})
    for k in drop: rails.pop(k)
    return {"board": "pcb-a-power", "written": "2026-09-27 01:00", "rails": rails}


def _write_intent(root, **kw):
    p = os.path.join(root, *(A_DIR + ("pcb-a-power-intent.json",)))
    with open(p, "w", encoding="utf-8") as f: f.write(json.dumps(_intent(**kw), indent=1, ensure_ascii=False) + "\n")


def _write_out(root):
    with open(os.path.join(root, *(SHEETS + ("calc", "rail_widths.out"))), "w", encoding="utf-8") as f:
        f.write(RW.render(["a"], root))


def _write_sheet(root, notes=None):
    """The sheet as a session would write it: the opening paragraph closed by the bound block, a section 1, section 2
    with the tool's table and a note column, and a section 3 that is not the check's."""
    block = CB.emit_block("a", root, RW, today="2026-09-27")
    tab = []
    for l in CB.emit_tables("a", root, RW):
        cells = CB.split_row(l)
        if cells and not CB.is_rule(cells) and cells[0] != "rail":
            cells[-1] = (notes or {}).get(cells[0], "")
            l = "| " + " | ".join(cells) + " |"
        tab.append(l)
    text = "\n".join(["# Board A (power and I/O): layout constraints", "",
                      "**Bound to the fixture's candidate.** Section 2 is the tool's output; the rest is older.", ""]
                     + block + ["", "## 1. Stackup and layer use", "", "- six layers.", "",
                                "## 2. Power: band widths at the declared currents", "",
                                "From `calc/rail_widths.py`.", ""] + tab +
                     ["What the table asks of the layout:", "", "1. the pack path is outer copper.", "",
                      "## 3. Pairs and RF lines", "", "| Class / nets | Target |", "|---|---|", "| USB | 90 ohm |", ""])
    with open(os.path.join(root, *(SHEETS + ("A.md",))), "w", encoding="utf-8") as f: f.write(text)


def _tree(vin_raw=12.31, **kw):
    root = tempfile.mkdtemp(prefix="cbound-")
    os.makedirs(os.path.join(root, *A_DIR))
    os.makedirs(os.path.join(root, *(SHEETS + ("calc",))))
    with open(os.path.join(root, *(A_DIR + ("pcb-a-power.net",))), "w", encoding="utf-8") as f:
        f.write('(export (version "E")\n  (components\n    (comp (ref "R1") (value "10k")))\n  (nets\n  )\n)\n')
    _write_intent(root, vin_raw=vin_raw, **kw)
    _write_out(root)
    _write_sheet(root)
    return root


def _judge(root):
    try:
        return CB.judge("a", root, RW, git=False)
    finally:
        pass


def _sheet(root):
    return os.path.join(root, *(SHEETS + ("A.md",)))


def _edit(path, old, new, count=1):
    s = open(path, encoding="utf-8").read()
    assert s.count(old) >= 1, "the fixture does not carry %r" % old
    s2 = s.replace(old, new, count)
    assert s2 != s
    with open(path, "w", encoding="utf-8") as f: f.write(s2)


def _sha(path):
    return CB.sha16(path)


# ---------------------------------------------------------------------------------------------- the known good
def t_a_consistent_tree_passes():
    """KNOWN GOOD: the sheet, the output file and the inputs are one candidate's."""
    root = _tree()
    try:
        r = _judge(root)
        assert not r["fails"], r["fails"]
        assert r["missing_input"] is None
        assert r["checked"] >= 40, "only %d checks were made, so most of the sheet was not compared" % r["checked"]
        s = CB.judge_set(root, ["a"], RW)
        assert not s["fails"], s["fails"]
        # and it judged the H2 sheet's own numbers: 12.31 A is 11.92 mm on one outer face at 1 oz
        text = open(_sheet(root), encoding="utf-8").read()
        assert "| VIN_RAW | 12.0 (36.0) | 12.31 / 12.31 | 12.31, typical (PI-001) | 11.92 |" in text, text
    finally:
        shutil.rmtree(root)


def t_a_note_beside_a_row_is_the_sheets_own_and_is_not_compared():
    root = _tree()
    try:
        _write_sheet(root, notes={"VIN_RAW": "**SET 6**: the input filter's output \\| four 9 A pins"})
        r = _judge(root)
        assert not r["fails"], r["fails"]
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- the known bad
def t_KNOWN_BAD_1_the_intent_file_edited_after_the_sheet_was_written():
    """THE H2 DEFECT, with its own numbers. The sheet was written on an intent file that declared VIN_RAW at 12.31 A;
    the intent file now says 14.10 A and nobody touched the sheet."""
    root = _tree(vin_raw=12.31)
    try:
        intent = os.path.join(root, *(A_DIR + ("pcb-a-power-intent.json",)))
        was = _sha(intent)
        _write_intent(root, vin_raw=14.10)
        now = _sha(intent)
        assert was != now
        r = _judge(root)
        f = r["fails"]
        assert f, "a sheet computed on another intent file passed"
        named = [x for x in f if "the intent" in x and was in x and now in x and "A.md" in x]
        assert named, "no failure names the sheet, the input and both hashes (%s, %s): %s" % (was, now, f)
        rows = [x for x in f if "rail VIN_RAW" in x]
        assert any("'12.31 / 12.31'" in x and "'14.10 / 14.10'" in x for x in rows), rows
        assert any("column `outer mm`" in x and "'11.92'" in x and "'15.29'" in x for x in rows), rows
        assert any("barrels" in x and "'20 / 16 / 14'" in x for x in rows), rows
        # the rails that did not move are not named
        assert not [x for x in f if "rail CELL+" in x or "rail +3V3" in x], f
    finally:
        shutil.rmtree(root)


def t_KNOWN_BAD_2_a_width_narrowed_by_hand_in_the_sheet():
    root = _tree(vin_raw=12.31)
    try:
        _edit(_sheet(root), "| 11.92 |", "| 9.00 |")
        r = _judge(root)
        f = r["fails"]
        assert len(f) == 1, f
        assert "A.md" in f[0] and "rail VIN_RAW" in f[0] and "column `outer mm`" in f[0], f
        assert "'9.00'" in f[0] and "'11.92'" in f[0], f
    finally:
        shutil.rmtree(root)


def t_KNOWN_BAD_2b_a_current_a_barrel_count_or_a_governing_current_edited_by_hand():
    for k, new, col in ((2, "10.00 / 12.31", "typ / peak A"), (7, "1 / 1 / 1", "barrels"),
                        (3, "6.00, typical (PI-001)", "governing A"), (5, "0.10", "two outer faces"),
                        (6, "1.00", "inner mm"), (1, "5.00", "V (working)")):
        root = _tree(vin_raw=12.31)
        try:
            row = [l for l in open(_sheet(root), encoding="utf-8").read().split("\n") if l.startswith("| VIN_RAW |")][0]
            cells = CB.split_row(row)
            assert cells[k] != new
            cells[k] = new
            _edit(_sheet(root), row, "| " + " | ".join(cells) + " |")
            f = _judge(root)["fails"]
            assert len(f) == 1 and "rail VIN_RAW" in f[0] and col in f[0], (col, f)
        finally:
            shutil.rmtree(root)


def t_KNOWN_BAD_3_a_sheet_that_declares_no_input():
    root = _tree()
    try:
        s = open(_sheet(root), encoding="utf-8").read()
        a, b = s.index(CB.OPEN), s.index(CB.FENCE + "\n", s.index(CB.OPEN) + 1)
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(s[:a] + s[b + len(CB.FENCE) + 1:])
        r = _judge(root)
        assert len(r["fails"]) == 1 and "declares no input" in r["fails"][0] and "A.md" in r["fails"][0], r["fails"]
    finally:
        shutil.rmtree(root)


def t_KNOWN_BAD_3b_a_block_that_names_no_input_and_a_block_below_the_opening():
    root = _tree()
    try:
        s = open(_sheet(root), encoding="utf-8").read()
        kept = "\n".join(l for l in s.split("\n") if l.split()[:1] not in (["netlist"], ["intent"]))
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(kept)
        f1 = _judge(root)["fails"]
        assert any("declares no input" in x for x in f1), f1
        # the block moved under section 1: it is not the opening's, so the sheet is bound by nothing
        a, b = s.index(CB.OPEN), s.index(CB.FENCE + "\n", s.index(CB.OPEN) + 1) + len(CB.FENCE) + 1
        block = s[a:b]
        moved = (s[:a] + s[b:]).replace("- six layers.\n", "- six layers.\n\n" + block)
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(moved)
        f2 = _judge(root)["fails"]
        assert len(f2) == 1 and "declares no input" in f2[0] and "below the first section" in f2[0], f2
    finally:
        shutil.rmtree(root)


def t_KNOWN_BAD_4_the_output_file_is_stale():
    """rail_widths.out was written on the older intent file; the sheet was re-bound and the output was not."""
    root = _tree(vin_raw=12.31)
    try:
        out = os.path.join(root, *(SHEETS + ("calc", "rail_widths.out")))
        intent = os.path.join(root, *(A_DIR + ("pcb-a-power-intent.json",)))
        was = _sha(intent)
        _write_intent(root, vin_raw=14.10)
        _write_sheet(root)                                   # the sheet is the new candidate's; the output is not
        f = _judge(root)["fails"]
        assert f and all("calc/rail_widths.out" in x for x in f), f
        assert any(was in x and _sha(intent) in x and "intent" in x for x in f), f
        assert any("is not what rail_widths.py prints now" in x for x in f), f
        s = CB.judge_set(root, ["a"], RW)
        assert len(s["fails"]) == 1 and _sha(out) in s["fails"][0], s["fails"]
        _write_out(root)
        assert not _judge(root)["fails"] and not CB.judge_set(root, ["a"], RW)["fails"]
    finally:
        shutil.rmtree(root)


def t_one_digit_changed_in_the_output_file_is_found_with_its_line():
    root = _tree(vin_raw=12.31)
    try:
        _edit(os.path.join(root, *(SHEETS + ("calc", "rail_widths.out"))), "| 11.92 |", "| 11.93 |")
        f = _judge(root)["fails"]
        assert len(f) == 1 and "the first line that differs" in f[0] and "11.93" in f[0] and "11.92" in f[0], f
        assert CB.judge_set(root, ["a"], RW)["fails"]
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- the model's identity
def t_a_sheet_that_states_another_copper_or_another_stack_fails():
    for old, new, word in (("outer 0.0350 mm", "outer 0.0700 mm", "outer copper"),
                           ("inner 0.0152 mm", "inner 0.0350 mm", "inner copper"),
                           ("stack      JLC06161H-3313", "stack      JLC04161H-7628", "the stack"),
                           ("rise 10 K", "rise 20 K", "temperature rise"),
                           ("decision 35", "decision 28", "decision"),
                           ("plating 18 um", "plating 25 um", "hole plating"),
                           ("track_current.width_for_current", "dc_drop.ipc_limit", "function")):
        root = _tree()
        try:
            _edit(_sheet(root), old, new)
            f = _judge(root)["fails"]
            assert len(f) == 1 and word in f[0] and "A.md" in f[0], (word, f)
        finally:
            shutil.rmtree(root)


def t_the_calculations_copper_is_the_stack_tables_copper():
    """rail_widths.py types a thickness per board; stackup_write.STACKS is where a stack's copper is recorded. A
    calculation at 2 oz for a board whose stack is recorded at 1 oz would size every band at half its width."""
    import copy
    root = _tree()
    keep = copy.deepcopy(RW.BOARDS)
    try:
        b = list(RW.BOARDS["a"]); b[2] = 0.070
        RW.BOARDS["a"] = tuple(b)
        _write_out(root); _write_sheet(root)                 # a sheet and an output that agree with the wrong table
        f = _judge(root)["fails"]
        assert len(f) == 1 and "stackup_write.STACKS records JLC06161H-3313 at 0.035" in f[0], f
    finally:
        RW.BOARDS.clear(); RW.BOARDS.update(keep)
        shutil.rmtree(root)


def t_every_board_of_the_real_calculation_is_on_a_recorded_stack_at_its_copper():
    for letter in RW.ORDER:
        b = RW.NO_INTENT[letter] if letter in RW.NO_INTENT else None
        name, out, inn = (b["stack"], b["cu_out"], b["cu_in"]) if b else RW.BOARDS[letter][1:4]
        cu = CB.stack_copper(name)
        assert cu is not None, "board %s is computed on %s, which stackup_write.STACKS does not record" % (letter, name)
        assert CB._same(cu[0], out) and CB._same(cu[1], inn), (letter, name, cu, out, inn)


# ---------------------------------------------------------------------------------------------- rows and tables
def t_a_row_removed_a_row_added_and_rows_out_of_order_fail():
    root = _tree()
    try:
        s = open(_sheet(root), encoding="utf-8").read()
        rows = [l for l in s.split("\n") if l.startswith("| +3V3 |")]
        assert len(rows) == 1
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(s.replace(rows[0] + "\n", ""))
        f1 = _judge(root)["fails"]
        assert len(f1) == 1 and "does not carry: +3V3" in f1[0], f1
        with open(_sheet(root), "w", encoding="utf-8") as f:
            f.write(s.replace(rows[0] + "\n", rows[0] + "\n" + rows[0].replace("| +3V3 |", "| +1V8 |") + "\n"))
        f2 = _judge(root)["fails"]
        assert len(f2) == 1 and "the tool does not print: +1V8" in f2[0], f2
        vin = [l for l in s.split("\n") if l.startswith("| VIN_RAW |")][0]
        with open(_sheet(root), "w", encoding="utf-8") as f:
            f.write(s.replace(vin + "\n", "").replace(rows[0] + "\n", rows[0] + "\n" + vin + "\n"))
        f3 = _judge(root)["fails"]
        assert len(f3) == 1 and "not in the tool's order" in f3[0], f3
    finally:
        shutil.rmtree(root)


def t_a_table_of_widths_made_by_hand_in_section_2_fails():
    root = _tree()
    try:
        _edit(_sheet(root), "What the table asks of the layout:",
              "| rail | typ / peak A | one outer face, mm |\n|---|---|---:|\n| VIN_RAW | 12.31 | 11.92 |\n\n"
              "What the table asks of the layout:")
        f = _judge(root)["fails"]
        assert len(f) == 1 and "a power table that rail_widths.py does not print" in f[0], f
    finally:
        shutil.rmtree(root)


def t_a_sheet_with_no_power_table_fails():
    root = _tree()
    try:
        s = open(_sheet(root), encoding="utf-8").read()
        with open(_sheet(root), "w", encoding="utf-8") as f:
            f.write("\n".join(l for l in s.split("\n") if not (l.startswith("|") and "90 ohm" not in l
                                                               and "Class / nets" not in l and l != "|---|---|")))
        f = _judge(root)["fails"]
        assert len(f) == 1 and "does not carry the table rail_widths.py prints" in f[0], f
    finally:
        shutil.rmtree(root)


def t_the_table_of_another_section_is_not_the_checks():
    root = _tree()
    try:
        _edit(_sheet(root), "| USB | 90 ohm |", "| USB | 85 ohm |")
        assert not _judge(root)["fails"]
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- the declaration
def t_a_declared_path_that_is_not_the_file_the_calculation_reads_fails():
    root = _tree()
    try:
        other = os.path.join(root, "v2", "ecad", "pcb-a-power", "out")
        os.makedirs(other)
        shutil.copy(os.path.join(root, *(A_DIR + ("pcb-a-power-intent.json",))), other)
        _edit(_sheet(root), "v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json",
              "v2/ecad/pcb-a-power/out/pcb-a-power-intent.json")
        f = _judge(root)["fails"]
        assert len(f) == 1 and "rail_widths.py reads v2/ecad/pcb-a-power-a23/out/pcb-a-power-intent.json" in f[0], f
    finally:
        shutil.rmtree(root)


def t_an_input_with_no_commit_a_misspelt_key_and_a_malformed_line_fail():
    for old, new, word in ((" changed UNKNOWN", "", "names no commit"),
                           ("netlist    ", "netlst     ", "is no key of a bound block"),
                           ("sha256/16 ", "sha256 ", "an input reads")):
        root = _tree()
        try:
            _edit(_sheet(root), old, new)
            f = _judge(root)["fails"]
            assert any(word in x for x in f), (word, f)
        finally:
            shutil.rmtree(root)


def t_an_input_that_is_gone_is_a_failure_and_a_calculation_that_cannot_run_alone_is_inconclusive():
    """A declared intent file that is no longer in the tree has been judged: the sheet is bound to nothing. A host
    that cannot run the calculation (no PyYAML for board E5's chain) has judged nothing, and says so."""
    root = _tree()
    try:
        os.remove(os.path.join(root, *(A_DIR + ("pcb-a-power-intent.json",))))
        r = _judge(root)
        assert r["missing_input"] is None, r["missing_input"]
        assert any("is not in this tree" in x and "intent" in x for x in r["fails"]), r["fails"]
        assert any("could not be run" in x for x in r["fails"]), r["fails"]
    finally:
        shutil.rmtree(root)
    root = _tree()
    keep = RW.rows
    try:
        def refuse(letter, root=None): raise SystemExit("reading the chain needs PyYAML on this host")
        RW.rows = refuse
        r = _judge(root)
        assert r["missing_input"] and "PyYAML" in r["missing_input"], r
        assert len(r["fails"]) == 1 and "could not be run" in r["fails"][0], r["fails"]
    finally:
        RW.rows = keep
        shutil.rmtree(root)


def t_a_pack_root_the_intent_file_no_longer_declares_fails():
    """A typed list that has outlived its subject: board A's pack path names CELL_FUSED; a generator that renames
    the rail would leave nothing judged at the pack's service current in its place, and the table would still agree
    with the tool."""
    root = _tree(drop=("CELL_FUSED",))
    try:
        f = _judge(root)["fails"]
        assert len(f) == 1 and "CELL_FUSED" in f[0] and "pack path" in f[0], f
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- the calculation
def t_a_series_segment_at_the_pack_paths_own_currents_is_pack_path_and_a_branch_is_not():
    """Set 6 declared board P's SW, the common drain of the pack's two FETs, `series_of` SCP_OUT at 10 and 18 A, and
    the typed list did not know it. A branch behind a fuse is `series_of` its parent too, at its own current."""
    rails = {"SCP_OUT": {"amps_typ": 10.0, "amps_peak": 18.0},
             "SW": {"amps_typ": 10.0, "amps_peak": 18.0, "series_of": "SCP_OUT"},
             "SW2": {"amps_typ": 10.0, "amps_peak": 18.0, "series_of": "SW"},
             "PACK_N": {"amps_typ": 10.0, "amps_peak": 18.0, "returns": "SCP_OUT"},
             "BRANCH": {"amps_typ": 0.6, "amps_peak": 0.6, "series_of": "SCP_OUT"},
             "FED": {"amps_typ": 10.0, "amps_peak": 18.0, "fed_from": "SCP_OUT"}}
    p = RW.pack_path(rails, ("SCP_OUT", "GONE"))
    assert sorted(p) == ["PACK_N", "SCP_OUT", "SW", "SW2"], p
    assert p["SW"] == "series of SCP_OUT" and p["SW2"] == "series of SW" and p["PACK_N"] == "return of SCP_OUT", p
    root = _tree(extra={"SW": {"volts": 14.4, "v_work": 16.8, "amps_typ": 10.0, "amps_peak": 18.0, "series_of": "VBAT"},
                        "VMON": {"volts": 14.4, "v_work": 16.8, "amps_typ": 0.69, "amps_peak": 1.0, "series_of": "VBAT"}})
    try:
        t = {r["net"]: r for r in RW.rows("a", root)["rows"]}
        assert t["SW"]["pack"] and t["SW"]["gov_a"] == RW.PACK_SERVICE_A and abs(t["SW"]["w_out"] - t["VBAT"]["w_out"]) < 1e-9
        assert not t["VMON"]["pack"] and t["VMON"]["gov_a"] == 0.69
        assert not _judge(root)["fails"]
    finally:
        shutil.rmtree(root)


def t_the_output_is_the_same_bytes_on_a_second_run():
    root = _tree()
    try:
        a, b = RW.render(["a"], root), RW.render(["a"], root)
        assert a == b and a.encode("utf-8") == open(os.path.join(root, *(SHEETS + ("calc", "rail_widths.out"))), "rb").read()
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- the readers
def t_a_table_row_is_split_on_the_pipe_and_an_escaped_pipe_is_text():
    assert CB.split_row("| a \\| b |  c   d | e |") == ["a | b", "c d", "e"]
    assert CB.split_row("| a | | c |") == ["a", "", "c"]
    assert CB.split_row("| a | b") == ["a", "b"]
    assert CB.split_row("a | b |") is None and CB.split_row("") is None
    assert CB.is_rule(["---", "---:", ":--:"]) and not CB.is_rule(["---", "a"]) and not CB.is_rule([":", "---"])
    t = CB.tables(["text", "| h1 | h2 |", "|---|---|", "| 1 | 2 |", "| 3 \\| 4 | 5 |", "", "| x | y |", "not a rule"])
    assert len(t) == 1 and t[0]["head"] == ["h1", "h2"] and t[0]["rows"] == [["1", "2"], ["3 | 4", "5"]], t


def t_the_net_names_of_a_board_file_are_read_as_s_expressions():
    text = ('(kicad_pcb (net 0 "") (net 13 "CELL+") (net 14 "CELL_N")\n (footprint "x" (pad "1" smd (net 13 "CELL+")))\n'
            ' (gr_text "(net 99 \\"NOT_A_NET\\")" (at 1 2)) (net 7 "A\\"B"))')
    assert CB.sexp_nets(text) == {"", "CELL+", "CELL_N", 'A"B'}, CB.sexp_nets(text)


def t_the_tool_uses_no_regular_expression():
    """Detectors parse. The tool's verdict is decided by a table reader, a block reader, json and a hash; a
    regular expression over a sheet's prose is how a check comes to fire on its own docstring."""
    import ast
    tree = ast.parse(open(os.path.join(TOOLS, "constraints_bound.py"), encoding="utf-8").read())
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): names |= {a.name.split(".")[0] for a in n.names}
        if isinstance(n, ast.ImportFrom) and n.module: names.add(n.module.split(".")[0])
    assert "re" not in names and "fnmatch" not in names, sorted(names)


# ---------------------------------------------------------------------------------------------- where it writes
def _run(args, cwd, env_extra=None):
    env = {k: v for k, v in os.environ.items() if k not in ("VERDICT_DIR", "VERDICT_ADVISORY")}
    env.update(env_extra or {})
    return subprocess.run([sys.executable, os.path.join(TOOLS, "constraints_bound.py")] + args, cwd=cwd, env=env,
                          capture_output=True, text=True, timeout=120)


def _files(d):
    return sorted(os.path.join(dp, f)[len(d) + 1:] for dp, _dn, fs in os.walk(d) for f in fs)


def t_by_default_it_prints_and_writes_nothing():
    root = _tree()
    cwd = tempfile.mkdtemp(prefix="cbound-cwd-")
    try:
        before = _files(root)
        p = _run(["--board", "a", "--root", root, "--no-git"], cwd)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "PASS" in p.stdout and "nothing written" in p.stdout, p.stdout
        assert _files(cwd) == [] and _files(root) == before, (_files(cwd), _files(root))
        _edit(_sheet(root), "| 11.92 |", "| 9.00 |")
        p = _run(["--board", "a", "--root", root, "--no-git"], cwd)
        assert p.returncode == 1 and "FAIL" in p.stdout and "'9.00'" in p.stdout, p.stdout + p.stderr
        assert _files(cwd) == [] and _files(root) == before
    finally:
        shutil.rmtree(root); shutil.rmtree(cwd)


def t_given_an_out_dir_or_run_by_the_pipeline_it_writes_the_boards_verdict_there():
    root = _tree()
    cwd = tempfile.mkdtemp(prefix="cbound-cwd-")
    out = tempfile.mkdtemp(prefix="cbound-out-")
    try:
        for how in (["--out-dir", out], None):
            for f in _files(out): os.remove(os.path.join(out, f))
            p = _run(["--board", "a", "--root", root, "--no-git"] + (how or []), cwd,
                     None if how else {"VERDICT_DIR": out})
            assert p.returncode == 0, p.stdout + p.stderr
            assert _files(out) == ["constraints_bound_a.verdict.json"], _files(out)
            assert _files(cwd) == []
            rec = json.load(open(os.path.join(out, "constraints_bound_a.verdict.json")))
            assert rec["verdict"] == "PASS" and rec["denominator"] == rec["counts"]["checked"] >= 40, rec["counts"]
            inp = rec["inputs"]
            assert inp["board"] == "a"
            for k, end in (("netlist", "pcb-a-power.net"), ("intent", "pcb-a-power-intent.json"), ("sheet", "A.md"),
                           ("rail_widths_out", "rail_widths.out"), ("rail_widths", "rail_widths.py")):
                assert inp[k]["path"].endswith(end) and len(inp[k]["sha256_16"]) == 16, (k, inp.get(k))
            assert inp["netlist"].get("content16"), "the netlist is not recorded by content, so a re-take could not bind"
            assert rec["writer"]["file"] == "constraints_bound.py"
        _edit(_sheet(root), "| 11.92 |", "| 9.00 |")
        p = _run(["--board", "a", "--root", root, "--no-git", "--out-dir", out], cwd)
        rec = json.load(open(os.path.join(out, "constraints_bound_a.verdict.json")))
        assert p.returncode == 1 and rec["verdict"] == "FAIL" and rec["counts"]["fail"] == 1, (p.stdout, rec["counts"])
        assert "rail VIN_RAW" in rec["evidence"][0]
    finally:
        shutil.rmtree(root); shutil.rmtree(cwd); shutil.rmtree(out)


def t_an_unknown_argument_and_an_unknown_board_are_refused():
    cwd = tempfile.mkdtemp(prefix="cbound-cwd-")
    try:
        for args in (["--bord", "a"], ["--board"], ["--board", "z"], ["--emit", "z"]):
            p = _run(args, cwd)
            assert p.returncode == 2, (args, p.returncode, p.stdout)
        assert _files(cwd) == []
    finally:
        shutil.rmtree(cwd)


def t_emit_prints_what_the_sheet_should_carry_and_marks_what_moved():
    root = _tree(vin_raw=12.31)
    try:
        _write_sheet(root, notes={"+3V3": "the logic rail"})
        _write_intent(root, vin_raw=14.10, extra={"VMON": {"volts": 14.4, "amps_typ": 0.69, "amps_peak": 1.0}})
        before = _files(root)
        text = CB.emit("a", root, RW)
        assert _files(root) == before
        rows = {c[0]: c for c in (CB.split_row(l) for l in text.split("\n")) if c}
        assert rows["+3V3"][-1] == "the logic rail", rows["+3V3"]
        assert rows["VIN_RAW"][-1].startswith(CB.MARK_MOVED) and "was 11.92" in rows["VIN_RAW"][-1], rows["VIN_RAW"]
        assert rows["VMON"][-1].startswith(CB.MARK_NEW), rows["VMON"]
        assert rows["CELL+"][-1] == "", rows["CELL+"]
    finally:
        shutil.rmtree(root)


def t_a_sheet_re_bound_by_machine_fails_until_each_row_that_moved_is_explained():
    """--emit --sheet prints the whole sheet with the new hashes and the tool's cells, which is everything the check
    compares. If that passed, a re-binding would be one command and no reading: the H2 defect with a green check. A
    row that moved or is new carries the mark, and the mark fails."""
    root = _tree(vin_raw=12.31)
    try:
        _write_sheet(root, notes={"+3V3": "the logic rail", "VIN_RAW": "the input filter's output"})
        before = open(_sheet(root), encoding="utf-8").read()
        _write_intent(root, vin_raw=14.10, extra={"VMON": {"volts": 14.4, "amps_typ": 0.69, "amps_peak": 1.0}})
        _write_out(root)
        assert _judge(root)["fails"], "the sheet of the older intent file passed"
        files = _files(root)
        text = CB.emit_sheet("a", root, RW, today="2026-09-28")
        assert _files(root) == files and open(_sheet(root), encoding="utf-8").read() == before, "emit wrote something"
        # every line outside the block and section 2's table is the sheet's own
        a, b = before.split("\n"), text.split("\n")
        assert len(b) == len(a) + 1, (len(a), len(b))                       # one row more: VMON
        assert [l for l in a if l.startswith("## ") or "90 ohm" in l or "pack path is outer" in l] == \
               [l for l in b if l.startswith("## ") or "90 ohm" in l or "pack path is outer" in l]
        assert "read       2026-09-28 at UNKNOWN" in b and "current    section 2" not in text
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(text)
        f1 = _judge(root)["fails"]
        assert len(f1) == 2 and all("still opens with the re-binding's mark" in x for x in f1), f1
        assert any("rail VIN_RAW" in x for x in f1) and any("rail VMON" in x for x in f1), f1
        rows = {c[0]: c for c in (CB.split_row(l) for l in b) if c}
        assert rows["+3V3"][-1] == "the logic rail"
        assert rows["VIN_RAW"][-1].startswith(CB.MARK_MOVED) and rows["VIN_RAW"][-1].endswith("the input filter's output")
        assert "`outer mm` was 11.92" in rows["VIN_RAW"][-1] and rows["VIN_RAW"][4] == "15.29", rows["VIN_RAW"]
        # explained, it passes
        s2 = open(_sheet(root), encoding="utf-8").read()
        s2 = s2.replace(rows["VIN_RAW"][-1], "14.10 A since the front end's ISNS limit was declared (R4A-N12)")
        s2 = s2.replace(rows["VMON"][-1], "new: the monitor's supply behind the eFuse U21")
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(s2)
        assert not _judge(root)["fails"], _judge(root)["fails"]
        # and emitted again it is itself: nothing moved, nothing marked
        assert CB.emit_sheet("a", root, RW, today="2026-09-28") == s2
    finally:
        shutil.rmtree(root)


def t_a_sheet_with_no_block_is_not_emitted():
    root = _tree()
    try:
        s = open(_sheet(root), encoding="utf-8").read()
        a, b = s.index(CB.OPEN), s.index(CB.FENCE + "\n", s.index(CB.OPEN) + 1)
        with open(_sheet(root), "w", encoding="utf-8") as f: f.write(s[:a] + s[b + len(CB.FENCE) + 1:])
        try: CB.emit_sheet("a", root, RW)
        except ValueError as e: assert "no bound block" in str(e)
        else: raise AssertionError("a sheet nobody has bound was given a binding by machine")
    finally:
        shutil.rmtree(root)


# ---------------------------------------------------------------------------------------------- THE REAL TREE
def _yaml_or_skip():
    try:
        import yaml                                          # noqa: F401
    except ImportError:
        raise Skip("no PyYAML on this host: board E5's currents are read from pcb_energy_chain.yaml")


def t_THE_REAL_TREE_every_sheet_is_bound_to_the_committed_inputs():
    """Every sheet of this tree, every board, with git asked wherever it answers. This is the test that fails the
    day an intent file or a netlist moves and the sheets are not re-bound."""
    _yaml_or_skip()
    bad = []
    for letter in RW.ORDER:
        r = CB.judge(letter, None, RW)
        assert r["checked"] >= 20, (letter, r["checked"])
        bad += r["fails"]
        if r["missing_input"]: bad.append("board %s: %s" % (letter, r["missing_input"]))
    assert not bad, "%d failure(s):\n  %s" % (len(bad), "\n  ".join(bad))


def t_THE_REAL_TREE_the_output_file_reproduces_byte_for_byte_twice():
    _yaml_or_skip()
    s = CB.judge_set(None, None, RW)
    assert not s["fails"], s["fails"]
    a, b = RW.render(), RW.render()
    have = open(os.path.join(CB.ROOT, *(SHEETS + ("calc", "rail_widths.out"))), "rb").read()
    assert a == b and a.encode("utf-8") == have
    p = subprocess.run([sys.executable, CB.calc_path(), "--markdown"], capture_output=True, timeout=120)
    assert p.returncode == 0 and p.stdout == have, "rail_widths.py --markdown does not print the committed output"


def t_THE_REAL_TREE_every_sheet_says_what_was_re_read_and_what_is_older():
    """The bound block's `current` and `older` lines are the sheet's statement, at the point of use, of which of its
    sections were re-read on this candidate. They are a reader's, and their presence is held here."""
    for letter, name in sorted(CB.SHEETS.items()):
        lines = open(os.path.join(CB.ROOT, *(SHEETS + (name,))), encoding="utf-8").read().splitlines()
        b = CB.bound_blocks(CB.sections(lines)[0][2])
        assert b, "%s carries no bound block in its opening" % name
        keys = [raw.split()[0] for _n, raw in b[0]["body"]]
        assert "current" in keys and "older" in keys, (name, keys)


def t_THE_REAL_TREE_every_sheet_emitted_again_is_itself():
    """Nothing has moved since the sheets were bound, so the sheet the tool would print is the sheet, but for the
    commit and the date of its `read` line. The day this fails without the test above failing, --emit has drifted."""
    _yaml_or_skip()
    for letter, name in sorted(CB.SHEETS.items()):
        have = open(os.path.join(CB.ROOT, *(SHEETS + (name,))), encoding="utf-8").read().split("\n")
        want = CB.emit_sheet(letter, None, RW).split("\n")
        diff = [(a, b) for a, b in zip(have, want) if a != b]
        assert len(have) == len(want) and all(a.split()[:1] == ["read"] == b.split()[:1] for a, b in diff), (name, diff[:3])


def t_THE_REAL_TREE_a_longer_git_abbreviation_does_not_move_a_sheet():
    """A `changed` commit is written at a fixed 8 characters: git's own abbreviation grows with the repository (a box
    clone with more objects printed 9 on 29 September 2026 and every sheet read as moved). Forcing core.abbrev to 12
    for the emitting git must leave every sheet as committed but for its `read` line."""
    _yaml_or_skip()
    keys = ("GIT_CONFIG_COUNT", "GIT_CONFIG_KEY_0", "GIT_CONFIG_VALUE_0")
    saved = {k: os.environ.get(k) for k in keys}
    os.environ.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "core.abbrev", "GIT_CONFIG_VALUE_0": "12"})
    try:
        for letter, name in sorted(CB.SHEETS.items()):
            have = open(os.path.join(CB.ROOT, *(SHEETS + (name,))), encoding="utf-8").read().split("\n")
            want = CB.emit_sheet(letter, None, RW).split("\n")
            diff = [(a, b) for a, b in zip(have, want) if a != b]
            assert len(have) == len(want) and all(a.split()[:1] == ["read"] == b.split()[:1] for a, b in diff), (name, diff[:3])
            for l in want:
                if l.split()[:1] and l.split()[0] in CB.INPUT_ROLES and " changed " in l and not l.endswith("UNKNOWN"):
                    assert len(l.rsplit(" ", 1)[1]) == 8, (name, l)
    finally:
        for k, v in saved.items():
            if v is None: os.environ.pop(k, None)
            else: os.environ[k] = v


def t_THE_REAL_TREE_the_tool_by_default_leaves_the_tree_alone():
    _yaml_or_skip()
    cwd = tempfile.mkdtemp(prefix="cbound-cwd-")
    try:
        ev = os.path.join(CB.ECAD, "out")
        before = {f: os.stat(os.path.join(ev, f)).st_mtime_ns for f in os.listdir(ev)} if os.path.isdir(ev) else {}
        p = _run([], cwd)
        assert p.returncode == 0, p.stdout[-3000:] + p.stderr[-1000:]
        after = {f: os.stat(os.path.join(ev, f)).st_mtime_ns for f in os.listdir(ev)} if os.path.isdir(ev) else {}
        assert before == after and _files(cwd) == []
    finally:
        shutil.rmtree(cwd)
