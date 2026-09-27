#!/usr/bin/env python3
"""kisch.tvs(): a clamp drawn so its polarity can be read (S-09 of MESHSAT-1357, 26 September 2026).

Every one-way suppressor on the set was drawn with Device:D_TVS, KiCad's BIDIRECTIONAL symbol (pins A1/A2), and seven
of sixteen had the band on the return (adjudication A03). The helper draws a one-way part with Device:D_Zener (K on
pin 1) from the part number, refuses the swapped call, and the gate reads the polarity back from the netlist. The
last fixture runs the whole road on KiCad itself where kicad-cli is installed."""
import os, sys, json, shutil, tempfile, subprocess

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TOOLS)
from harness import Skip


def _gen(body, env=None, want_intent=False):
    """Run a few kisch calls in a fresh process (the engine's state is module level: one process, one board)."""
    code = ("import sys, json; sys.path.insert(0, %r)\nimport kisch, intent\n"
            "kisch.configure(fp={'SMB': 'Diode_SMD:D_SMB', 'SOD323': 'Diode_SMD:D_SOD-323'})\n%s\n"
            "print('P=' + json.dumps([dict(ref=p['ref'], lib=p['lib'], sym=p['sym'], nets=p['nets']) for p in kisch.P]))\n"
            "print('I=' + json.dumps(intent._I.get('clamps') or {}))\n"
            % (TOOLS, body))
    r = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60, env=env)
    out = r.stdout + r.stderr
    parts, clamps = None, None
    for line in r.stdout.splitlines():
        if line.startswith("P="): parts = json.loads(line[2:])
        if line.startswith("I="): clamps = json.loads(line[2:])
    return (r.returncode, out, parts, clamps) if want_intent else (r.returncode, out, parts)


def t_a_one_way_part_is_drawn_with_a_cathode_on_the_protected_conductor():
    rc, out, P = _gen("kisch.tvs('D1', 'SMBJ5.0A', '+5V_D8', 'GND', 'SMB')")
    assert rc == 0, out
    assert P == [dict(ref="D1", lib="Device", sym="D_Zener", nets={"1": "+5V_D8", "2": "GND"})], P


def t_a_two_way_part_keeps_the_bidirectional_symbol():
    rc, out, P = _gen("kisch.tvs('D9', 'PESD5V0S1BA bidirectional ESD clamp', 'HS1_SPK', 'GND', 'SOD323', 'C19224')")
    assert rc == 0, out
    assert P[0]["sym"] == "D_TVS" and P[0]["nets"] == {"1": "HS1_SPK", "2": "GND"}, P


def t_the_swapped_call_is_refused():
    """DEFECTIVE: ground as the protected conductor is exactly the reversal A03 found."""
    rc, out, _ = _gen("kisch.tvs('D1', 'SMBJ5.0A', 'GND', '+5V_D8', 'SMB')")
    assert rc != 0 and "swapped" in out, out


def t_a_declared_return_rail_cannot_be_the_protected_conductor():
    """DEFECTIVE: board P's shape. PACK_N is declared the return of PACK_P in the board's intent."""
    decl = ("intent._I['rails']['PACK_P'] = {'volts': 14.4}\n"
            "intent._I['rails']['PACK_N'] = {'volts': 0.05, 'returns': 'PACK_P'}\n")   # what intent.rail(..., returns=) records
    rc, out, _ = _gen(decl + "kisch.tvs('D1', 'SMBJ20A', 'PACK_N', 'PACK_P', 'SMB')")
    assert rc != 0 and "declared as the return" in out, out
    rc, out, P = _gen(decl + "kisch.tvs('D1', 'SMBJ20A', 'PACK_P', 'PACK_N', 'SMB')")
    assert rc == 0 and P[0]["nets"] == {"1": "PACK_P", "2": "PACK_N"} and P[0]["sym"] == "D_Zener", (out, P)


def t_a_direction_that_contradicts_the_part_number_is_refused():
    rc, out, _ = _gen("kisch.tvs('D1', 'SMCJ40A', 'VIN', 'GND', 'SMB', direction='bi')")
    assert rc != 0 and "the part number says uni" in out, out
    rc, out, _ = _gen("kisch.tvs('D1', 'SMCJ40CA', 'VIN', 'GND', 'SMB', direction='uni')")
    assert rc != 0 and "the part number says bi" in out, out


def t_a_part_number_the_helper_cannot_read_needs_the_direction_said():
    rc, out, _ = _gen("kisch.tvs('D1', 'XYZ123 clamp', 'VIN', 'GND', 'SMB')")
    assert rc != 0 and "say direction=" in out, out
    rc, out, P = _gen("kisch.tvs('D1', 'XYZ123 clamp', 'VIN', 'GND', 'SMB', direction='uni', basis='maker sheet, rev 1')")
    assert rc == 0 and P[0]["sym"] == "D_Zener", (out, P)


def t_a_direction_said_for_an_unread_part_needs_its_datasheet_basis():
    """DEFECTIVE (review fix-up of round 4, 26 September 2026): a direction with no source is the drawing's claim
    over again, and the gate reads the declaration as the part's direction."""
    rc, out, _ = _gen("kisch.tvs('D1', 'P6KE18A', 'VIN', 'GND', 'SMB', direction='uni')")
    assert rc != 0 and "basis=" in out, out


def t_every_call_is_declared_in_the_intent_for_the_gate():
    """The gate reads what the generator declared as well as what it drew: direction, basis, both conductors."""
    rc, out, P, I = _gen("kisch.tvs('D1', 'P6KE18A', '/VIN', 'GND', 'SMB', direction='uni', basis='Littelfuse P6KE: uni')\n"
                         "kisch.tvs('D2', 'SMBJ5.0A', '+5V_X', 'GND', 'SMB')", want_intent=True)
    assert rc == 0, out
    assert I["D1"] == {"direction": "uni", "basis": "Littelfuse P6KE: uni", "protected": "VIN", "return": "GND",
                       "symbol": "Device:D_Zener"}, I
    assert I["D2"]["direction"] == "uni" and "no C in the suffix" in I["D2"]["basis"], I


def t_a_declared_return_is_found_under_either_key_intent_stores():
    """intent.py stores a rail as 'X' or '/X'; the helper looked up only the bare name (review fix-up of round 4)."""
    decl = "intent._I['rails']['/PACK_N'] = {'volts': 0.05, 'returns': 'PACK_P'}\n"
    rc, out, _ = _gen(decl + "kisch.tvs('D1', 'SMBJ20A', 'PACK_N', 'PACK_P', 'SMB')")
    assert rc != 0 and "declared as the return" in out, out


def t_the_part_number_reader():
    import kisch
    for v, want in (("SMCJ40A (input surge)", "uni"), ("SMBJ5.0A", "uni"), ("SMBJ58A-13-F", "uni"),
                    ("SMBJ20CA", "bi"), ("SMCJ40CA", "bi"), ("PESD5V0S1BA bidirectional", "bi"),
                    ("SMBJ20A (pack terminal clamp)", "uni"), ("SMBJ6.0A", "uni"),
                    ("SMAJ10A", None), ("P6KE18A", None), ("BAT54", None), ("", None),
                    # round 6: board D's D10 and D13, read from their own maker's sheet, and a sibling that is not held
                    ("PESD12VL1BA bidirectional ESD clamp at the jack: headset 1 microphone", "bi"),
                    ("PESD12VL1BA,115", "bi"), ("PESD12VS1UA", None),
                    # round 6 fourth pass: board A's D22 since main 458b2873, read from Diodes' DS18004, and a sibling
                    # type of the same sheet that no board fits, which is not read by family
                    ("BZT52C12-7-F zener, the restart guard's pull-up clamp", "uni"), ("BZT52C15-7-F", None)):
        assert kisch.tvs_direction(v)[0] == want, (v, kisch.tvs_direction(v))


def _kicad():
    kc = shutil.which("kicad-cli")
    sym = os.environ.get("KICAD_SYMBOLS", "/usr/share/kicad/symbols/")
    if not kc or not os.path.exists(os.path.join(sym, "Device.kicad_sym")):
        raise Skip("no kicad-cli or KiCad symbol library here")
    return kc


_SHEET = r'''
import sys, os, uuid
sys.path.insert(0, %(tools)r)
import kisch
kisch.configure(fp={"SMB": "Diode_SMD:D_SMB"}, power={}, stub=5.08, root=str(uuid.uuid5(kisch.UUID_NS, "t")),
                project="t", seed="t")
%(calls)s
kisch.reset_body()
x = 30.0
for p in kisch.P:
    kisch.emit_part(p, x, 40.0); x += 30.0
hdr = '(kicad_sch\n\t(version 20250114)\n\t(generator "eeschema")\n\t(generator_version "9.0")\n\t(uuid "%%s")\n\t(paper "A4")\n' %% kisch.ROOT
hdr += '\t(lib_symbols\n' + "".join("\t\t" + kisch.ser(v, 2).replace("\n", "\n\t\t") + "\n" for v in kisch.libsyms.values()) + '\t)\n'
body = "".join("\t" + s.replace("\n", "\n\t").rstrip("\t") for s in kisch.out)
open(sys.argv[1], "w").write(hdr + body + '\t(sheet_instances (path "/" (page "1")))\n)\n')
'''


def _roundtrip(calls, prefix):
    kc = _kicad()
    d = tempfile.mkdtemp(prefix=prefix)
    g = os.path.join(d, "gen.py"); open(g, "w").write(_SHEET % {"tools": TOOLS, "calls": calls})
    sch, net = os.path.join(d, "t.kicad_sch"), os.path.join(d, "t.net")
    r = subprocess.run([sys.executable, g, sch], capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stdout + r.stderr
    r = subprocess.run([kc, "sch", "export", "netlist", "--format", "kicadsexpr", "-o", net, sch],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0 and os.path.exists(net), r.stdout + r.stderr
    import port_protect
    return {c["ref"]: c for c in port_protect.clamp_rows(net)}, open(net).read()


def t_kicad_exports_the_helpers_cathode_and_the_gate_reads_it():
    """The whole road on KiCad 9: kisch.tvs() -> schematic -> kicad-cli netlist -> port_protect.clamp_rows."""
    rows, txt = _roundtrip("kisch.tvs('D1', 'SMBJ5.0A', '+5V_X', 'GND', 'SMB')\n"
                           "kisch.r('R1', '1k', '+5V_X', 'GND')", "tvs-rt-ok-")
    assert '(libsource (lib "Device") (part "D_Zener")' in txt, txt[:2000]
    assert '(pin "1") (pinfunction "K")' in txt, "KiCad did not export pin 1 as K"
    d1 = rows["D1"]
    assert d1["drawing"] == "K/A" and d1["cathode_net"] == "+5V_X" and d1["verdict"] == "OK", d1


def t_kicad_exports_the_old_drawing_and_the_gate_refuses_it():
    """DEFECTIVE, as board D drew D1 before: Device:D_TVS with ground on pin 1."""
    rows, txt = _roundtrip("kisch.part('D1', 'Device', 'D_TVS', 'SMBJ5.0A', 'SMB', {'1': 'GND', '2': '+5V_X'})\n"
                           "kisch.r('R1', '1k', '+5V_X', 'GND')", "tvs-rt-bad-")
    assert '(pinfunction "A1")' in txt, txt[:2000]
    d1 = rows["D1"]
    assert d1["orientation"] == "REVERSED" and d1["symbol"] == "MISMATCH", d1


def t_a_negative_conductor_is_refused_rather_than_drawn_the_wrong_way():
    """The helper draws K on the protected conductor, which is right only above the return (second fix-up of round
    4, 26 September 2026): -12V by name, and a rail the intent declares below zero, are refused."""
    rc, out, _ = _gen("kisch.tvs('D1', 'SMBJ12A', '-12V', 'GND', 'SMB')")
    assert rc != 0 and "negative conductor" in out, out
    rc, out, _ = _gen("intent._I['rails']['VNEG'] = {'volts': -5.0}\nkisch.tvs('D1', 'SMBJ5.0A', 'VNEG', 'GND', 'SMB')")
    assert rc != 0 and "negative conductor" in out, out
