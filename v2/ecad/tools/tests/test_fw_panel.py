#!/usr/bin/env python3
"""The panel controller's firmware (board C, U3 RP2040; MESHSAT-1357 Layer 12): `v2/firmware/panel/`.

Prototype firmware for an unbuilt board. These tests build and run its host unit tests, and bind the firmware to the
tree: every FW-C row of HW-FW-CONTRACT.md is cited by a host test or listed in the firmware README as not the
firmware's or owed; every pin and expander bit hal.h names matches the committed netlists; the e-paper's quoted
messages and the timing constants match the contract pages; the target build keeps FW-C01's two rules.

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
    ("PANEL_EPD_MIN_INTERVAL_MS", 60000, "PANEL.md", "refresh at most once a minute"),
    ("PANEL_EPD_FULL_INTERVAL_MS", 3600000, "PANEL.md", "full refresh once an hour"),
    ("PANEL_ZER_DEADLINE_MS", 1500, "feasibility/ZEROIZE.md", "A deadline D = 1.5 s after the end of the hold"),
    ("PANEL_ZER_KILL_AFTER_MS", 3000, "feasibility/ZEROIZE.md", "arms a hardware timer alarm 3.0 s after the end of the hold"),
    ("PANEL_DUTY_DAY", 1000, "PANEL.md", "duty 100 %"),
    ("PANEL_DUTY_NIGHT", 150, "PANEL.md", "duty 15 %"),
    ("PANEL_DUTY_NVG", 20, "PANEL.md", "duty 2 %"),
    ("PANEL_DUTY_TX_FLOOR", 100, "PANEL.md", "never dimmed below 10 % duty"),
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
