#!/usr/bin/env python3
"""l6r2_intent.py: round 5 of record l6r2 (MESHSAT-1357, 3 October 2026): the voltage DECLARATIONS a desk can derive for the nets
on which finding F3 left a capacitor's rated voltage open, the intent drafts that carry them, and the overlay through which the
record judges its selections as if the drafts were applied.

Each declaration is a node in the sense of intent.node (v_max, v_min, basis): the largest and lowest voltage a part on the net
can see in normal operation, derived from the circuit (the generator), the board's committed intent (the rails that drive the
net) and the makers' documents held in the tree, with the operating case named in its basis. Nothing is guessed: a figure that
rests on an undeclared upstream quantity is not declared here (the record lists it with the quantity named). The figures that
come from a declared rail are READ from the committed intent file when the declarations are built, so a changed rail moves them.

THE DRAFTS: apply_gen_sch_{p,d,b}_intent.py insert the board's `_intent.node(...)` calls once, immediately before the line
`_intent.write(OUT, PROJECT, P)` (the intent is written there, after every declaration), never touching any other line. RELEASE
GUARD as the record's other drafts (RELEASE.md, l6r2_apply.released). A second application is refused (the marker line is
present, or a net is already declared by name); the result must differ and parse.

THE OVERLAY: `overlay()` is a context manager under which part_identities.Board merges these nodes into the intent it reads,
exactly as the generator's intent.node would have written them; l6r2_passives.py computes its rows under it (round 5)."""
import ast
import contextlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import l6r2_apply  # noqa: E402

ANCHOR = "_intent.write(OUT, PROJECT, P)"
MARK = "# LAYER 6 RECORD l6r2 ROUND 5 (MESHSAT-1357"
INTENT = {"p": "v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json", "d": "v2/ecad/pcb-d-aprs-d9/out/pcb-d-aprs-intent.json",
          "b": "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute-intent.json"}
BQ4050 = "v2/vendor/battery/ti-bq4050.pdf"
AW7915 = "v2/vendor/wifi/asiarf-AW7915-AED_V1.pdf"
SKY13351 = "v2/vendor/rf/skyworks-sky13351-378lf-spdt.pdf"
PCM2912A = "v2/vendor/ti/ti-pcm2912a.pdf"
LIME_PAGE = "v2/vendor/limesdr/myriadrf-limesdr-mini-2-0-page-20260925.html"


def _hi(top, board, net):
    it = json.load(open(os.path.join(top, INTENT[board]), encoding="utf-8"))
    d = (it.get("rails") or {}).get(net) or (it.get("nodes") or {}).get(net) or {}
    vals = [float(d[k]) for k in ("volts", "v_max", "v_work") if d.get(k) is not None]
    if not vals: raise SystemExit("l6r2_intent: %s carries no declared maximum for %s" % (INTENT[board], net))
    return max(vals)


def rf_peak(dbm, ohms=50.0):
    """The peak voltage of a sine at `dbm` into `ohms`, and twice that, the standing-wave maximum on a fully reflecting lead."""
    p = 10 ** (dbm / 10.0) / 1000.0
    v = math.sqrt(2.0 * p * ohms)
    return v, 2.0 * v


def declarations(top):
    """board -> [(net, v_max, v_min, basis)], every figure derived here or read from the committed intent."""
    out = {}
    out["p"] = [(n, 0.2, -0.2, "%s: the BQ4050's %s input (pin %s) reached through %s, the coulomb counter's filtered side of the 2 mOhm "
                 "shunt R10 between GND and PACK_N. TI SLUSC67B 6.3 (p.8) recommends SRP and SRN within -0.2 to +0.2 V (6.1, absolute "
                 "maximum -0.3 to +0.3 V); the shunt drops 36 mV at the pack's declared 18 A peak (PACK_N's rail), and the AFE's "
                 "short-circuit trips SCD1 and SCC are at most 200 mV across it (6.31, p.16, CONTROL[RSNS] = 0). Operating case: "
                 "discharge or charge up to the short-circuit trip; round 5 of record l6r2" % (n, pin, pnum, via))
                for n, pin, pnum, via in (("SRP_F", "SRP", "8", "R8 100R from GND"), ("SRN_F", "SRN", "6", "R9 100R from PACK_N"))]
    v5 = _hi(top, "d", "+5V_D8")
    vref = round(v5 / 2.0, 3)
    vccr = _hi(top, "d", "PCM_VCCR")
    out["d"] = [
        ("MICAMP_AC", vref, -vref, "the coupled side of C46: the TLV9062 (U8) output sits at VREF (R38/R39, half of +5V_D8's declared "
         "%.2f V) and swings within its supply, so the side of C46 whose DC is ground through R45 and R47 moves at most %.3f V either "
         "way. Operating case: full-scale transmit audio; round 5 of record l6r2" % (v5, vref)),
        ("PCM_R_AC", vccr, -vccr, "the coupled side of C47: the PCM2912A's VOUTR (pin 22) swings within its R-channel supply PCM_VCCR "
         "(declared %.1f V, TI SLES230A note 10), so the side of C47 whose DC is ground through R46 and R47 moves at most %.1f V either "
         "way (the full regulator output, not half of it: the output's centre is not taken from the sheet). Operating case: "
         "full-scale codec playback; round 5 of record l6r2" % (vccr, vccr)),
        ("MIC_SUM", max(vref, vccr), -max(vref, vccr), "the summing node of R45, R46 and R47 (10k each, R47 to ground): a resistive "
         "combination of MICAMP_AC, PCM_R_AC and ground cannot exceed the larger of the two (%.3f and %.1f V). Operating case: both "
         "sources at full scale; round 5 of record l6r2" % (vref, vccr)),
    ]
    v_lime = _hi(top, "b", "+5V_LIME")
    v_ctl = _hi(top, "b", "+3V3_DEV")
    dbm = 23.0 + 1.5
    vpk, vrefl = rf_peak(dbm)
    vrefl = round(vrefl, 2)
    out["b"] = [(n, v_lime, 0.0, "%s: J_LIME pin %s, the LimeSDR Mini 2.4's USB 3 receive pair through the receptacle. The LimeSDR in "
                 "its bay has no supply but this receptacle's VBUS, +5V_LIME (declared %.1f V), so its pins stay within 0 V and that "
                 "supply (the premise rule V-1 applies to every active part, here to the module behind the connector; its USB 3.0 "
                 "controller is an FTDI FT601, whose own sheet is not held). Operating case: the LimeSDR enumerated at USB 3 speed; "
                 "round 5 of record l6r2" % (n, pin, v_lime))
                for n, pin in (("LIME_SSTX_P", "9"), ("LIME_SSTX_N", "8"))]
    for ch in ("A", "B"):
        for n, what in (("W1%s_CARD" % ch, "the slot 1 card's antenna lead (J_W1%s)" % ch), ("W3%s_CARD" % ch, "the slot 3 card's antenna lead (J_W3%s)" % ch),
                        ("W%s_ANT" % ch, "the lead to A22's P2P jack (J_WO%s)" % ch)):
            out["b"].append((n, vrefl, -vrefl, "%s, chain %s: the AsiaRF AW7915-AED's highest conducted output is 23 dBm +/- 1.5 dB (11b, "
                             "datasheet V1.0 p.3), %.1f dBm, which is %.2f V peak into 50 Ohm and %.2f V with the lead fully reflecting "
                             "(an open or shorted antenna, the case board B's LORA_ANT declares). DC: none (an antenna lead, DC blocked "
                             "on the switch side). Operating case: transmit at full power into any load; round 5 of record l6r2"
                             % (what, ch, dbm, vpk, vrefl)))
        for n, port in (("SW%s_O1" % ch, "OUTPUT1"), ("SW%s_O2" % ch, "OUTPUT2"), ("SW%s_IN" % ch, "INPUT")):
            out["b"].append((n, round(v_ctl + vrefl, 2), -vrefl, "the SKY13351-378LF's %s port, chain %s: the sheet requires every RF "
                             "port DC blocked, so the port's own DC is taken at most its control voltage (VCTL from +3V3_DEV, declared "
                             "%.1f V), plus the card's RF peak with the lead fully reflecting, %.2f V. Operating case: transmit at full "
                             "power into any load; round 5 of record l6r2" % (port, ch, v_ctl, vrefl)))
    return out


def node_dict(v_max, v_min, basis):
    return {"v_max": float(v_max), "v_min": float(v_min), "basis": basis}


@contextlib.contextmanager
def overlay(PI, top):
    """part_identities.Board reads these nodes on top of the committed intent, as intent.node would have written them."""
    D = declarations(top)
    orig = PI.Board.__init__

    def init(self, letter, phase, stem):
        orig(self, letter, phase, stem)
        for net, vmax, vmin, basis in D.get(letter, []):
            self.nodes[net] = node_dict(vmax, vmin, basis)
    PI.Board.__init__ = init
    try:
        yield D
    finally:
        PI.Board.__init__ = orig


def block(board, decl):
    lines = [MARK + ", 3 October 2026): the voltage of the nets on which a capacitor's rated voltage was open (finding F3),",
             "# derived from the circuit, this intent's rails and the makers' documents (v2/docs/records/l6r2/L6R2-PASSIVES.md section 8.4)."]
    for net, vmax, vmin, basis in decl:
        lines.append("_intent.node(%r, %r, %r, v_min=%r)" % (net, float(vmax), basis, float(vmin)))
    return "\n".join(lines) + "\n"


def apply_text(text, board, decl):
    if not decl:
        return "REFUSED", None, "no declaration for board %s" % board
    lines = text.split("\n")
    idx = [i for i, l in enumerate(lines) if l.startswith(ANCHOR)]
    if len(idx) != 1:
        return "REFUSED", None, "the anchor %r does not start exactly one line" % ANCHOR
    if MARK in text:
        return "REFUSED", None, "the block is already in the generator: a second application is refused"
    for net, _a, _b, _c in decl:
        if "_intent.node(%r" % net in text or '_intent.node("%s"' % net in text:
            return "REFUSED", None, "the generator already declares %s" % net
    new = "\n".join(lines[:idx[0]]) + "\n" + block(board, decl) + "\n".join(lines[idx[0]:])
    if new == text:
        return "REFUSED", None, "the new text does not differ"
    try:
        ast.parse(new)
    except SyntaxError as e:
        return "REFUSED", None, "the result does not parse: %s" % e
    return "OK", new, "%d declarations inserted before the intent is written" % len(decl)


def render_draft(board, decl):
    body = ["#!/usr/bin/env python3",
            '"""apply_gen_sch_%s_intent.py: DRAFT for board %s\'s generator owner (Layer 6 record l6r2 round 5, MESHSAT-1357, 3 October 2026).' % (board, board.upper()),
            "NOT APPLIED. It inserts %d intent declarations (intent.node) into v2/ecad/tools/gen_sch_%s.py, before the intent is written:" % (len(decl), board),
            "the voltage of nets on which a capacitor's rated voltage was open (finding F3), each derived from the circuit with its basis",
            "and operating case (l6r2_intent.py; the page's section 8.4). Rendered by `l6r2_passives.py --write-drafts`; test_l6r2.py holds",
            "this file equal to the render and proves its composition with every other pending draft of the generator.",
            "Usage:  apply_gen_sch_%s_intent.py TARGET [--check | --write]     (default --check: nothing is written)" % board,
            "Exit 0: checked (or written); 3: refused (the release guard, a second application, the anchor, the parse).\"\"\"",
            "import os", "import sys", "",
            "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))",
            "import l6r2_intent  # noqa: E402", "",
            "BOARD = %r" % board, "DECLARATIONS = ["]
    for net, vmax, vmin, basis in decl:
        body.append("    (%r, %r, %r," % (net, float(vmax), float(vmin)))
        body.append("     %r)," % basis)
    body += ["]", "", "", "if __name__ == \"__main__\":", "    sys.exit(l6r2_intent.main(BOARD, DECLARATIONS, sys.argv[1:]))", ""]
    return "\n".join(body)


def main(board, decl, argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        print(__doc__.split("\n")[0]); return 3
    target = os.path.realpath(args[0])
    own = os.path.realpath(os.path.join(l6r2_apply._top(), "v2", "ecad", "tools", "gen_sch_%s.py" % board))
    if target == own and not l6r2_apply.released():
        print("apply_gen_sch_%s_intent: REFUSED: the repository's own generator, and v2/docs/records/l6r2/RELEASE.md does not read "
              "'released: yes' with an accepted check" % board)
        return 3
    st, new, why = apply_text(open(target, encoding="utf-8").read(), board, decl)
    if st != "OK":
        print("apply_gen_sch_%s_intent: REFUSED: %s" % (board, why)); return 3
    if flags == ["--write"]:
        open(target, "w", encoding="utf-8").write(new)
        if open(target, encoding="utf-8").read() != new:
            print("apply_gen_sch_%s_intent: REFUSED: the written file does not read back as the patched text" % board); return 3
        print("apply_gen_sch_%s_intent: WRITTEN, %s" % (board, why))
    else:
        print("apply_gen_sch_%s_intent: checked, not written: %s" % (board, why))
    return 0
