#!/usr/bin/env python3
"""The panel controller's firmware (board C, U3 RP2040; MESHSAT-1357 Layer 12): `v2/firmware/panel/`.

Prototype firmware for an unbuilt board. These tests build and run its host unit tests, and bind the firmware to the
tree: every FW-C row of HW-FW-CONTRACT.md is cited by a host test or listed in the firmware README as not the
firmware's or owed; every pin and expander bit hal.h names matches the committed netlists; the e-paper's quoted
messages and the timing constants match the contract pages; the target build keeps FW-C01's two rules; and every value
Layer 5's round 3 decided (record l5r2 `L5-PANEL-R3.md`, findings F-04 to F-13) is read from the contract's own words and
compared with what the core does, measured by the host program `tests/contract_probe.c`, so a contract row the code
contradicts fails by name (L5R3-F02; F-05 and F-11 first).

Each check PARSES what it reads: the netlists as S-expressions, gen_sch_c.py's RP2040 pin table with `ast`, hal.h's
two X-macro lists and test_list.h's T() list as C structures, the contract's and README's markdown tables by row.
Nothing here writes into the tree: the C build goes to a temporary directory. Usage: run.py fw_panel"""
import ast
import os
import re
import shutil
import subprocess
import tempfile

from harness import Skip, need

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
V2 = os.path.dirname(os.path.dirname(TOOLS))
FW = os.path.join(V2, "firmware", "panel")
DOCS = os.path.join(V2, "docs")
NET = {"a": "pcb-a-power-a23/out/pcb-a-power.net", "b": "pcb-b-compute-b19/out/pcb-b-compute.net",
       "c": "pcb-c-display-c8/out/pcb-c-display.net", "d": "pcb-d-aprs-d9/out/pcb-d-aprs.net"}
EXP_REF = {0x22: ("c", "U1"), 0x23: ("c", "U2"), 0x21: ("a", "U27"), 0x24: ("a", "U28"), 0x20: ("b", "U6"),
           0x25: ("b", "U7"), 0x26: ("d", "U16")}


# ---------------------------------------------------------------- readers

def _sexpr(text):
    """A KiCad netlist as nested lists (strings unquoted)."""
    stack, i, n = [[]], 0, len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            stack.append([]); i += 1
        elif ch == ")":
            top = stack.pop(); stack[-1].append(top); i += 1
        elif ch.isspace():
            i += 1
        elif ch == '"':
            j, buf = i + 1, []
            while text[j] != '"':
                if text[j] == "\\":
                    buf.append(text[j + 1]); j += 2
                else:
                    buf.append(text[j]); j += 1
            stack[-1].append("".join(buf)); i = j + 1
        else:
            j = i
            while j < n and not text[j].isspace() and text[j] not in "()":
                j += 1
            stack[-1].append(text[i:j]); i = j
    return stack[0][0]


_NET_CACHE = {}


def pins(board):
    """{(ref, pin): net name without the leading '/'} for one board's committed netlist."""
    if board in _NET_CACHE:
        return _NET_CACHE[board]
    path = need(os.path.join(V2, "ecad", NET[board]), "board %s's committed netlist" % board.upper())
    tree = _sexpr(open(path, encoding="utf-8").read())
    out = {}
    for sec in tree:
        if isinstance(sec, list) and sec and sec[0] == "nets":
            for net in sec[1:]:
                name = next(f[1] for f in net[1:] if isinstance(f, list) and f[0] == "name")
                for f in net[1:]:
                    if isinstance(f, list) and f[0] == "node":
                        d = {g[0]: g[1] for g in f[1:] if isinstance(g, list)}
                        out[(d["ref"], d["pin"])] = name.lstrip("/")
    _NET_CACHE[board] = out
    return out


def rp2040_pin_table():
    """gen_sch_c.py's RP2040 dict {QFN pin: pin name}, read with ast."""
    src = open(need(os.path.join(TOOLS, "gen_sch_c.py"), "board C's generator"), encoding="utf-8").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "RP2040" for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError("gen_sch_c.py has no RP2040 table")


def _strip_c_comments(src):
    return re.sub(r"/\*.*?\*/", " ", re.sub(r"//[^\n]*", " ", src), flags=re.S)


def xmacro(header, macro):
    """The entries of a C X-macro list `#define MACRO(X) X(a, b, ...) ...` as tuples of stripped strings."""
    src = _strip_c_comments(open(os.path.join(FW, "include", header), encoding="utf-8").read())
    m = re.search(r"#define\s+%s\(X\)((?:[^\n]*\\\n)*[^\n]*)" % macro, src)
    assert m, "%s has no %s" % (header, macro)
    body = m.group(1).replace("\\\n", " ")
    return [tuple(p.strip() for p in e.split(",")) for e in re.findall(r"X\(([^)]*)\)", body)]


def test_list():
    """test_list.h's T(name, "citation") entries."""
    src = open(os.path.join(FW, "tests", "test_list.h"), encoding="utf-8").read()
    return re.findall(r"\bT\((\w+),\s*\"([^\"]*)\"\)", src)


def md_table_rows(path, first_cell_pattern):
    """Every markdown table row whose first cell matches the pattern, as a list of cells."""
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and re.fullmatch(first_cell_pattern, cells[0]):
            rows.append(cells)
    return rows


def contract_fwc_ids():
    path = need(os.path.join(DOCS, "HW-FW-CONTRACT.md"), "the hardware and firmware contract")
    return sorted({r[0] for r in md_table_rows(path, r"FW-C\d\d")})


# ---------------------------------------------------------------- the host tests

def t_host_tests_build_and_pass():
    gcc = shutil.which("gcc") or shutil.which("cc")
    make = shutil.which("make")
    if not gcc or not make:
        raise Skip("no C compiler or make on this host: the host tests of v2/firmware/panel cannot run here")
    with tempfile.TemporaryDirectory(prefix="fw_panel_") as tmp:
        r = subprocess.run([make, "-s", "-C", FW, "test", "BUILD=" + tmp, "CC=" + gcc], capture_output=True,
                           text=True, timeout=300)
    out = r.stdout + r.stderr
    assert r.returncode == 0, "the host tests failed:\n" + out[-4000:]
    names = [n for n, _ in test_list()]
    for n in names:
        assert re.search(r"^ok\s+%s\b" % re.escape(n), out, re.M), "host test %s did not report ok" % n
    m = re.search(r"^(\d+) tests, (\d+) passed, 0 failed$", out, re.M)
    assert m and int(m.group(1)) == int(m.group(2)) == len(names), "the runner's count differs from test_list.h"


# ---------------------------------------------------------------- every FW-C row is implemented, or listed

STATUSES = ("IMPLEMENTED", "PARTLY", "NOT THE FIRMWARE'S", "OWED")


def t_every_fw_c_row_is_covered():
    ids = contract_fwc_ids()
    assert len(ids) >= 15, "fewer FW-C rows than the contract carried when this was written: %s" % ids
    cited = set()
    for _, cite in test_list():
        cited.update(re.findall(r"FW-C\d\d", cite))
    readme = os.path.join(FW, "README.md")
    rows = {r[0]: r for r in md_table_rows(readme, r"FW-C\d\d")}
    missing = [i for i in ids if i not in rows]
    assert not missing, "FW-C rows absent from README.md's row table: %s" % missing
    extra = [i for i in rows if i not in ids]
    assert not extra, "README.md lists FW-C rows the contract does not have: %s" % extra
    for i in ids:
        status = rows[i][1]
        assert status in STATUSES, "%s: status %r is none of %s" % (i, status, STATUSES)
        if status in ("IMPLEMENTED", "PARTLY"):
            assert i in cited, "%s is marked %s but no host test cites it" % (i, status)
        else:
            assert i not in cited, "%s is marked %s but a host test cites it" % (i, status)
    uncovered = [i for i in ids if i not in cited and rows[i][1] not in ("NOT THE FIRMWARE'S", "OWED")]
    assert not uncovered, "FW-C rows neither cited by a test nor listed as not the firmware's or owed: %s" % uncovered


def t_readme_names_every_host_test():
    readme = os.path.join(FW, "README.md")
    listed = {r[0] for r in md_table_rows(readme, r"t_\w+")}
    names = {n for n, _ in test_list()}
    assert names == listed, "README section 2 and test_list.h differ: only in the list %s, only in the README %s" % (
        sorted(names - listed), sorted(listed - names))


# ---------------------------------------------------------------- hal.h against the netlists

def t_hal_pins_match_board_c_netlist():
    table = rp2040_pin_table()
    gpio_of_pin = {}
    for pin, name in table.items():
        m = re.fullmatch(r"GPIO(\d+)(?:_A\d)?", name)
        if m:
            gpio_of_pin[int(m.group(1))] = str(pin)
    assert len(gpio_of_pin) == 30, "the RP2040 table names %d GPIOs, not 30" % len(gpio_of_pin)
    c = pins("c")
    hal = xmacro("hal.h", "HAL_PIN_LIST")
    assert len(hal) == 30, "hal.h names %d GPIOs, not 30" % len(hal)
    seen = set()
    for net, gpio, _direction in hal:
        g = int(gpio)
        assert g not in seen, "GPIO%d named twice in hal.h" % g
        seen.add(g)
        on_board = c.get(("U3", gpio_of_pin[g]))
        assert on_board == net, "GPIO%d: hal.h says %s, board C's netlist has %s on U3 pin %s" % (
            g, net, on_board, gpio_of_pin[g])


def _strap(board, ref, pin):
    net = pins(board).get((ref, pin), "")
    if net == "GND":
        return 0
    assert "3V3" in net, "%s %s pin %s on %s: neither GND nor a 3.3 V rail" % (board, ref, pin, net)
    return 1


def t_hal_expander_bits_match_netlists():
    for name, addr, port, bit, net in xmacro("hal.h", "HAL_EXP_BIT_LIST"):
        a = int(addr, 16)
        board, ref = EXP_REF[a]
        pin = str((4 if int(port) == 0 else 13) + int(bit))
        got = pins(board).get((ref, pin))
        assert got == net, "%s: hal.h says %s on %s %s pin %s, the netlist has %s" % (name, net, board.upper(), ref, pin, got)
    for a, (board, ref) in EXP_REF.items():
        strapped = 0x20 | _strap(board, ref, "3") << 2 | _strap(board, ref, "2") << 1 | _strap(board, ref, "21")
        assert strapped == a, "%s %s is strapped to 0x%02X, hal.h addresses it at 0x%02X" % (board.upper(), ref, strapped, a)


def t_pi_button_reaches_no_controller_pin():
    """Finding F-01's evidence: SW_PI's contacts end on J_PIJ2's lands and reach no controller or expander pin."""
    c = pins("c")
    nets = {c[("SW_PI", "1")], c[("SW_PI", "2")]}
    for (ref, pin), net in list(c.items()):
        if ref in ("FB3", "FB4") and net in nets:
            nets.add(c[(ref, "2" if pin == "1" else "1")])
    reached = sorted({ref for (ref, pin), net in c.items() if net in nets})
    controllers = [r for r in reached if r in ("U1", "U2", "U3")]
    hal = open(os.path.join(FW, "include", "hal.h"), encoding="utf-8").read()
    wired = re.search(r"#define\s+HAL_PI_BUTTON_WIRED\s+(\d)", hal).group(1) == "1"
    assert wired == bool(controllers), ("the PI button's wiring changed (it now reaches %s): update HAL_PI_BUTTON_WIRED, "
                                        "hal_rp2040.c and README finding F-01" % (controllers or "nothing"))
    assert "GND" not in nets, "a PI contact is on GND: F-01's evidence has changed"


def t_panel_3v3_cannot_be_switched_by_firmware():
    """FW-C11: no controller pin reaches the panel LDO's enable (U5 pin 3), so the firmware cannot switch its 3.3 V."""
    c = pins("c")
    en = c[("U5", "3")]
    assert en in ("+5V",), "U5's EN is on %s now: FW-C11 needs a firmware rule" % en
    assert not [k for k, n in c.items() if n == en and k[0] in ("U3", "U1", "U2")], "a controller pin reaches U5's EN"


# ---------------------------------------------------------------- the words and the numbers

def t_epaper_messages_match_the_contract():
    panel = open(need(os.path.join(DOCS, "PANEL.md"), "PANEL.md"), encoding="utf-8").read()
    contract = open(os.path.join(DOCS, "HW-FW-CONTRACT.md"), encoding="utf-8").read()
    core = open(os.path.join(FW, "src", "panel_core.c"), encoding="utf-8").read()
    s9 = panel[panel.index("## 9."):panel.index("## 10.")]
    quoted = set(re.findall(r"\"([A-Z][A-Z0-9 :,]+)\"", s9))
    fwc = "".join(r for r in contract.splitlines() if r.startswith("| FW-C13") or r.startswith("| FW-C15"))
    quoted |= set(re.findall(r"[\"']([A-Z][A-Z0-9 :,]{6,})[\"']", fwc))
    assert len(quoted) >= 11, "fewer quoted panel messages than expected: %s" % sorted(quoted)
    missing = [q for q in sorted(quoted) if q not in core]
    assert not missing, "e-paper messages of the contract the firmware does not carry: %s" % missing


CONSTANTS = [  # (panel.h name, value, page, words that must stand in the page)
    ("PANEL_DEBOUNCE_MS", 30, "PANEL.md", "Debounce 30 ms"),
    ("PANEL_TEST_LAMP_HOLD_MS", 2000, "PANEL.md", "hold 2 s = lamp test"),
    ("PANEL_TEST_QR_HOLD_MS", 5000, "PANEL.md", "hold 5 s within 60 s"),
    ("PANEL_QR_WINDOW_MS", 60000, "PANEL.md", "hold 5 s within 60 s"),
    ("PANEL_LAMPTEST_MS", 3000, "PANEL.md", "indicators for 3 s"),
    ("PANEL_BATBAR_MS", 5000, "PANEL.md", "BAT1..5 for 5 s"),
    ("PANEL_SOS_HOLD_MS", 2000, "PANEL.md", "SOS closed 2 s"),
    ("PANEL_ZEROIZE_HOLD_MS", 5000, "PANEL.md", "ZEROIZE closed 5 s"),
    ("PANEL_HB_LOST_MS", 3000, "HW-FW-CONTRACT.md", "declare it lost after 3 s without an edge"),
    ("PANEL_SLOT_FLAT_MS", 60000, "PANEL.md", "stays flat for 60 s"),
    ("PANEL_SLOT_CYCLE_OFF_MS", 5000, "PANEL.md", "rail off 5 s"),
    ("PANEL_SHDN_PULSE_MS", 200, "PANEL.md", "at least 200 ms"),
    ("PANEL_KILL_HOLD_MS", 3000, "PANEL.md", "held high 3 s"),
    ("PANEL_PI_KILL_PRESS_MS", 8000, "PANEL.md", "hold 8 s"),
    ("PANEL_MAIN_TAP_MS", 32, "HW-FW-CONTRACT.md", "INT low for at least 32 ms"),
    ("PANEL_HOT_RELEASE_MS", 1800000, "HW-FW-CONTRACT.md", "30 minutes have passed since the stop"),
    ("PANEL_HOT_TMP117_H1_MC", 55000, "HW-FW-CONTRACT.md", "+55.0 C in two readings"),
    ("PANEL_HOT_TMP117_H2_MC", 56000, "HW-FW-CONTRACT.md", "+56.0 C in two readings"),
    ("PANEL_HOT_TMP117_REL_MC", 45000, "HW-FW-CONTRACT.md", "+45.0 C or less"),
    ("PANEL_MARGIN_TRIGGER_MC", 68650, "HW-FW-CONTRACT.md", "at or over 68.65 C"),
    ("PANEL_MARGIN_RESTORE_DK_MC", 5000, "HW-FW-CONTRACT.md", "5 K under the trigger after 30 minutes"),
    ("PANEL_EPD_MIN_INTERVAL_MS", 60000, "PANEL.md", "the idle page's content at most once a minute"),
    ("PANEL_EPD_FULL_INTERVAL_MS", 3600000, "PANEL.md", "full refresh once an hour"),
    ("PANEL_ZER_DEADLINE_MS", 1500, "feasibility/ZEROIZE.md", "A deadline D = 1.5 s after the end of the hold"),
    ("PANEL_ZER_KILL_AFTER_MS", 3000, "feasibility/ZEROIZE.md", "arms a hardware timer alarm 3.0 s after the end of the hold"),
    ("PANEL_DUTY_DAY", 1000, "PANEL.md", "duty 100 %"),
    ("PANEL_DUTY_NIGHT", 150, "PANEL.md", "duty 15 %"),
    ("PANEL_DUTY_NVG", 20, "PANEL.md", "duty 2 %"),
]


def t_timing_constants_match_the_contract():
    src = _strip_c_comments(open(os.path.join(FW, "include", "panel.h"), encoding="utf-8").read())
    defs = {m.group(1): int(m.group(2)) for m in re.finditer(r"#define\s+(PANEL_\w+)\s+(\d+)u?\b", src)}
    for name, value, page, words in CONSTANTS:
        assert defs.get(name) == value, "%s is %s in panel.h, the contract's figure is %s" % (name, defs.get(name), value)
        text = " ".join(open(os.path.join(DOCS, page), encoding="utf-8").read().split())
        assert words in text, "%s no longer says %r: re-read the figure behind %s" % (page, words, name)


# ---------------------------------------------------------------- the target build's rules

def t_target_build_keeps_fw_c01_and_fw_c02():
    cmake = open(os.path.join(FW, "CMakeLists.txt"), encoding="utf-8").read()
    assert re.search(r"^\s*PICO_RP2040_USB_DEVICE_ENUMERATION_FIX=0\s*$", cmake, re.M), "FW-C01: the E5 fix must be off"
    for f in os.listdir(os.path.join(FW, "src")):
        if not f.endswith(".c"):
            continue
        code = _strip_c_comments(open(os.path.join(FW, "src", f), encoding="utf-8").read())
        for args in re.findall(r"\breset_usb_boot\s*\(([^)]*)\)", code):
            mask = args.split(",")[0].strip()
            assert mask in ("0", "1u << HAL_GPIO_LED_STAT", "1u << 25"), "FW-C01: a BOOTSEL activity mask %s in %s" % (mask, f)
        assert "i2c_write_blocking(" not in code and "i2c_read_blocking(" not in code, (
            "ZEROIZE.md 3.4 (a): no I2C call without a timeout (%s)" % f)
    hal = _strip_c_comments(open(os.path.join(FW, "src", "hal_rp2040.c"), encoding="utf-8").read())
    m = re.search(r"void\s+runtime_init_early_resets\s*\(void\)\s*\{(.*?)\n\}", hal, re.S)
    assert m and "RESET_IO_BANK0" in m.group(1) and "RESET_PADS_BANK0" in m.group(1), (
        "FW-C02 (finding F-03): the SDK's early resets must spare IO_BANK0 and PADS_BANK0")
    assert re.search(r"hw_clear_bits\s*\(\s*&resets_hw->wdsel\s*,[^;]*RESETS_WDSEL_IO_BANK0_BITS[^;]*"
                     r"RESETS_WDSEL_PADS_BANK0_BITS", hal), "FW-C02: the watchdog's RESETS scope"
    assert re.search(r"hw_clear_bits\s*\(\s*&psm_hw->wdsel\s*,[^;]*PSM_WDSEL_SIO_BITS", hal), "FW-C02: the PSM scope"


# ---------------------------------------------------------------- the contract's decided values against the running core
# Record l5r2 round 3 (L5-PANEL-R3.md) decided F-04 to F-13. Each case below reads the decided value from the contract's
# own sentence and compares it with what tests/contract_probe.c measures on the core. A sentence that no longer parses
# is a contract change: re-read the decision before touching the code.

_PROBE = {}


def probe():
    if _PROBE:
        return _PROBE
    gcc = shutil.which("gcc") or shutil.which("cc")
    make = shutil.which("make")
    if not gcc or not make:
        raise Skip("no C compiler or make on this host: the contract probe of v2/firmware/panel cannot run here")
    with tempfile.TemporaryDirectory(prefix="fw_panel_probe_") as tmp:
        r = subprocess.run([make, "-s", "-C", FW, "probe", "BUILD=" + tmp, "CC=" + gcc], capture_output=True,
                           text=True, timeout=300)
    assert r.returncode == 0, "the contract probe failed to build or run:\n" + (r.stdout + r.stderr)[-3000:]
    for line in r.stdout.splitlines():
        if "=" in line:
            k, v = line.split("=", 1)
            _PROBE[k.strip()] = v.strip()
    return _PROBE


def _page(name):
    return " ".join(open(need(os.path.join(DOCS, name), name), encoding="utf-8").read().split())


def _section(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i)]


def _contract_row(row_id):
    path = os.path.join(DOCS, "HW-FW-CONTRACT.md")
    rows = [r for r in md_table_rows(path, re.escape(row_id))]
    assert len(rows) == 1, "%s: %d rows in HW-FW-CONTRACT.md" % (row_id, len(rows))
    return " ".join(" | ".join(rows[0]).split())


def _hal_bits():
    return {name: (int(addr, 16), int(port), int(bit)) for name, addr, port, bit, _ in xmacro("hal.h", "HAL_EXP_BIT_LIST")}


def t_contract_f05_tx_lamp_follows_duty():
    """PANEL.md section 8 (F-05): the TX lamp follows the panel's duty in every position; dark in BLACKOUT. No floor."""
    s8 = _section(_page("PANEL.md"), "## 8. Lighting", "## 9.")
    m = re.search(r"The TX lamp follows the panel's duty in every position \(DAY (\d+) %, NIGHT (\d+) %, NVG (\d+) %\); "
                  r"in BLACKOUT it is dark", s8)
    assert m, "PANEL.md section 8's TX lamp sentence moved: re-read F-05 before changing panel_light_duty"
    want = {"DAY": int(m.group(1)) * 10, "NIGHT": int(m.group(2)) * 10, "NVG": int(m.group(3)) * 10, "BLACKOUT": 0}
    got = probe()
    for mode, permille in want.items():
        keyed = int(got["f05_duty_%s_keyed" % mode])
        idle = int(got["f05_duty_%s_idle" % mode])
        assert keyed == permille and idle == permille, (
            "F-05: in %s with D8 keyed PANEL.md section 8 gives the panel %d per mille, the core drives %d (idle %d): "
            "the TX lamp follows the duty, no floor" % (mode, permille, keyed, idle))


def t_contract_f11_board_d_boot_levels():
    """FW-D01 (F-11): board D's U16 at the generator's power-up levels, written before its configuration."""
    row = _contract_row("FW-D01")
    levels = {}
    for net in ("X_SA_PD", "X_AMP_EN", "X_MMUTE"):
        m = re.search(r"\b%s ([01]) \(" % net, row)
        assert m, "FW-D01 no longer states %s's boot level: re-read F-11 before changing EXP_BOOT" % net
        levels[net] = int(m.group(1))
    bits = _hal_bits()
    names = {"X_SA_PD": "D_SA_PD", "X_AMP_EN": "D_AMP_EN", "X_MMUTE": "D_MMUTE"}
    out0 = sum(levels[n] << bits[names[n]][2] for n in levels)
    outputs = sum(1 << bits[names[n]][2] for n in levels)
    got = probe()
    assert int(got["f11_d_u16_out0"]) == out0, "F-11: FW-D01 gives D:U16 output port 0 = 0x%02X, the core writes 0x%02X" % (
        out0, int(got["f11_d_u16_out0"]))
    assert int(got["f11_d_u16_cfg0"]) == (0xFF & ~outputs), "F-11: D:U16 configuration 0x%02X, FW-D01's three outputs give 0x%02X" % (
        int(got["f11_d_u16_cfg0"]), 0xFF & ~outputs)
    assert got["f11_d_u16_out_before_cfg"] == "1", "F-11, FW-D01: outputs before configuration"


def t_contract_f04_outputs_before_every_configuration():
    s4 = _section(_page("PANEL.md"), "## 4.", "## 5.")
    assert "every configuration write is preceded by an output write" in s4, "PANEL.md section 4 moved: re-read F-04"
    assert probe()["f04_every_cfg_after_out"] == "1", "F-04: a configuration write with no output write before it"


def t_contract_f06_double_chirp():
    s9 = _section(_page("PANEL.md"), "## 9.", "## 9a.")
    m = re.search(r"double chirp, (\d+) ms on, (\d+) ms off, (\d+) ms on \(lamp test", s9)
    assert m, "PANEL.md section 9's sounder patterns moved: re-read F-06"
    want = [int(m.group(i)) for i in (1, 2, 3)]
    got = [int(v) for v in probe()["f06_double_chirp"].split(",")]
    assert got == want, "F-06: the lamp test sounds %s ms, PANEL.md section 9 gives %s" % (got, want)


def t_contract_f07_one_lost_caut_two_lost_warn():
    s9 = _section(_page("PANEL.md"), "## 9.", "## 9a.")
    warn = _section(s9, "MASTER WARN flashes (3 to 5 Hz) for any unacknowledged red condition (", ";")
    caut = _section(s9, "MASTER CAUT for an unacknowledged amber one (", ")")
    warn_items = [x.strip() for x in warn.split("(", 1)[1].split(",")]
    caut_items = [x.strip() for x in caut.split("(", 1)[1].split(",")]
    got = probe()
    want_one_caut = "a slot fault" in caut_items
    want_one_warn = "a slot fault" in warn_items
    want_two_warn = "two compute modules lost" in warn_items
    assert want_one_caut and want_two_warn, "PANEL.md section 9's lists moved: re-read F-07 (%s; %s)" % (warn_items, caut_items)
    assert (got["f07_one_lost_caut"] == "1") == want_one_caut, "F-07: one module lost and MASTER CAUT disagree"
    assert (got["f07_one_lost_warn"] == "1") == want_one_warn, "F-07: one module lost raises MASTER WARN against section 9"
    assert (got["f07_two_lost_warn"] == "1") == want_two_warn, "F-07: two modules lost must raise MASTER WARN"


def t_contract_f08_page_change_at_once():
    s9 = _section(_page("PANEL.md"), "## 9.", "## 9a.")
    assert "a change of page refreshes at once and the idle page's content at most once a minute" in s9, (
        "PANEL.md section 9's e-paper pacing moved: re-read F-08")
    got = probe()
    assert int(got["f08_page_change_delay_ms"]) <= 100, "F-08: a change of page waited %s ms" % got["f08_page_change_delay_ms"]
    assert int(got["f08_idle_interval_ms"]) >= 60000, "F-08: the idle page refreshed after %s ms, under a minute" % (
        got["f08_idle_interval_ms"])


def t_contract_f10_boot_5hz_dated_at_start():
    row = _contract_row("FW-C14")
    m = re.search(r"at 5 Hz, enter H1 with the stop dated at the start-up and raise no slot until the line is back at "
                  r"1 Hz and (\d+) minutes have passed", row)
    assert m, "FW-C14's start-up rule moved: re-read F-10"
    floor_ms = int(m.group(1)) * 60000
    got = int(probe()["f10_first_slot_after_boot_ms"])
    assert got >= floor_ms, "F-10: a slot rose %d ms after a 5 Hz start-up, FW-C14 says not before %d" % (got, floor_ms)


def t_contract_f12_margin_sos_text():
    s9 = _section(_page("PANEL.md"), "## 9.", "## 9a.")
    m = re.search(r"Queued under the margin hold.*?\"([A-Z][A-Z :,]+)\"", s9)
    assert m, "PANEL.md section 9's margin hold sentence moved: re-read F-12"
    assert m.group(1) in _contract_row("FW-C15"), "PANEL.md and FW-C15 give different margin hold texts"
    assert probe()["f12_margin_sos_text"] == m.group(1), "F-12: the core shows %r, the contract %r" % (
        probe()["f12_margin_sos_text"], m.group(1))


def t_contract_f13_hdmi_encoding():
    s5 = _section(_page("PANEL.md"), "## 5.", "## 6.")
    assert re.search(r"slot 1 = both selects low; slot 2 = `HDMI_SEL1` high, `HDMI_SEL2` low; slot 3 = `HDMI_SEL2` high", s5), (
        "PANEL.md section 5's encoding moved: re-read F-13")
    assert "the controller drives `HDMI_SEL1` low" in s5, "PANEL.md section 5 no longer drives HDMI_SEL1 low for slot 3"
    want = {1: (0, 0), 2: (1, 0), 3: (0, 1)}
    got = probe()
    for slot, (a, b) in want.items():
        g = (int(got["f13_slot%d_sel1" % slot]), int(got["f13_slot%d_sel2" % slot]))
        assert g == (a, b), "F-13: slot %d encodes as %s, PANEL.md section 5 gives %s" % (slot, g, (a, b))


def t_contract_f14_one_slot_fault_rule():
    """FW-C05 (F-14, record l5r4): the one slot-fault rule, read from the row's own words and measured on the core."""
    row = _contract_row("FW-C05")
    lost = re.search(r"declare it lost after (\d+) s without an edge", row)
    rule = re.search(r"at (\d+) s without an edge, counted from the later of its rail coming up and its last edge, "
                     r"power-cycle it once \(SLOT_EN low (\d+) s\), its one retry; at the next such (\d+) s drop SLOT_EN "
                     r"and leave it off until the operator acts", row)
    keep = ("keep the spent retry and the left-off state with the wipe-pending record across a watchdog, RUN or SWD reset, "
            "cleared only by a power-on reset")
    rearm = "each act re-arming the retry" in row
    assert lost and rule and keep in row and rearm, (
        "FW-C05's slot-fault rule moved: re-read F-14 (record l5r4) before changing slots_policy")
    lost_ms, flat_ms, off_ms, next_ms = int(lost.group(1)) * 1000, int(rule.group(1)) * 1000, int(rule.group(2)) * 1000, \
        int(rule.group(3)) * 1000
    g = {k: int(v) for k, v in probe().items() if k.startswith("f14_")}
    tick = 50                                                   # the probe reads an output one tick late at most
    checks = [
        ("a running slot shown lost after %d ms" % lost_ms, lost_ms <= g["f14_lost_shown_after_ms"] <= lost_ms + tick),
        ("cycled %d ms after its last edge" % flat_ms, flat_ms <= g["f14_cycle_after_last_edge_ms"] <= flat_ms + tick),
        ("its rail off %d ms" % off_ms, off_ms - 2 <= g["f14_cycle_off_ms"] <= off_ms + 2),
        ("left off %d ms after its rail came back" % next_ms, next_ms <= g["f14_off_after_rail_back_ms"] <= next_ms + tick),
        ("cycled once", g["f14_cycles_before_off"] == 1 and g["f14_left_off"] == 1),
        ("lost again after a good cycle: left off at %d ms, no second cycle" % flat_ms,
         flat_ms <= g["f14_second_loss_after_last_edge_ms"] <= flat_ms + tick and g["f14_second_loss_cycles"] == 0
         and g["f14_second_loss_left_off"] == 1),
        ("lost at start-up: cycled %d ms after its rail came up" % flat_ms,
         flat_ms <= g["f14_startup_cycle_after_rail_ms"] <= flat_ms + tick),
        ("kept off across a controller reset", g["f14_reset_keeps_off"] == 1),
        ("cleared by a power-on reset", g["f14_power_on_clears"] == 1),
        ("the operator's retry raises the slot and re-arms its retry", g["f14_retry_rearms"] == 1),
    ]
    bad = [name for name, ok in checks if not ok]
    assert not bad, "F-14: the core contradicts FW-C05 on: %s (measured %s)" % ("; ".join(bad), g)
