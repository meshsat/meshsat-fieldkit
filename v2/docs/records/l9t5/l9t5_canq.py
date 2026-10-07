#!/usr/bin/env python3
"""l9t5_canq.py: Layer 9 record l9t5, task T10, Layer 4 task L4A-55 (MESHSAT-1357, 7 October 2026, W139): the quorum service of the
three I/O supervisors under method M-B (the peers' buffered TXD observation and 2-of-2 SHDN vote on BOTH CAN fabrics, CON-004's two
fabrics kept). PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered or measured; no figure here is a measurement.

The ledger's RE-5 and HO-C (v2/docs/records/l4close/REMAINING-ENGINEERING.md) hand over "the peer-silence or diagnostic circuit and
the recovery proof", accepted when CON-004's quorum service holds under every row of the fault table including the GPIO-toggled TX,
with any automatic diagnostic carrying "a bounded detection/response interval, including faults that arise after startup and faults
affecting the diagnostic itself" (the owner's part 24). Task L4A-54 (W137, fnd/l4canmb 0d079eaf) drafts M-B's circuit; its output is
copied verbatim into inputs/ and read from there (the twelve votes, the TXD buffers, the TXD pull-ups, the self-test and its four
residuals, finding W137-F1). Task L4A-56 (W138, fnd/l4reg 86dbcdff) drafts the regulator stage whose TPS2553-1 may latch a supervisor
off in row 8; its output is copied the same way. It prints, deterministically:
  1. the inputs, pinned by sha256;
  2. the fixed interface read where it is written: CON-004 (restated verbatim, NOT amended), IOHA rows 3, 4, 5, 7, 8 and test A7,
     FW-B21 and FW-B22 as drafted (apply_hw_fw_contract_t10.py), the draft circuit's facts (inputs/);
  3. the makers' printed figures the timing rests on, each read from its committed text with its quote;
  4. the attribution rule (which TXD activity is out of contract; a strike needs the reader's own FDCAN error or lost scheduled frame,
     explained by the target's deviation: never a TXD reading alone) and the containment chain on printed timing;
  5. FW-B22 restated on the two fabrics (the window, the slots, a state frame taken from either fabric, the loss count, the test
     segment, DAR = 1 with ES0392 2.24.5's printed workaround) and the figures the contract draft must carry;
  6. THE FAULT TABLE: an event model of the two fabrics, the three controllers, each transceiver's SHDN (own request, the 2-of-2 gate),
     the twelve votes, the self-test and FW-B21's stop and probe, run for every IOHA row (3, 5, 7, 8; 4 for reference), every fault of
     M-B's vote path, W137's four residuals, W137-F1 and W138's latch, the onset scanned over the window and the self-test cycle, under
     both self-test schedules (W137's as drafted, and this round's restatement); each row's outcome (quorum held / a node out and
     contained / quorum lost) against its required outcome;
  7. the self-test's interval and every latent fault of the vote path with its bounded detection interval (simulated where a phase
     detects it), and the residuals;
  8. the recovery proof: each contained state, its exit and its bound, simulated, the latched supervisor's included;
  9. the acceptance predicates (it FAILS on any row that needs a third fabric or a removed fabric), what stays open.
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_canq.py  (l9t5_canq.out is its output, regenerated with
_bin/regen_out.py). Labels: PRINTED (a maker's limit), TYPICAL, DRAFTED (a contract row, not applied), MODEL, ASSUMPTION, SESSION.
Tests: v2/ecad/tools/tests/test_l9t5_canq.py. Stdlib only."""
import ast
import hashlib
import heapq
import importlib.util
import math
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True

# The makers' PDFs read as committed text (v2/docs/records/_lib/pdftext.py; re-take: python3 v2/docs/records/_lib/retake_pdf_text.py
# v2/docs/records/l9t5). This script never runs pdftotext and reads no held-back sheet.
PDFTEXT = {
    "v2/vendor/st/st-es0392-rev15.pdf": [["-layout", "-f", "48", "-l", "48"]],
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "533", "-l", "533"], ["-layout", "-f", "2469", "-l", "2469"],
                                        ["-layout", "-f", "2470", "-l", "2470"], ["-layout", "-f", "2532", "-l", "2532"],
                                        ["-layout", "-f", "2533", "-l", "2533"], ["-layout", "-f", "2534", "-l", "2534"],
                                        ["-layout", "-f", "2535", "-l", "2535"]],
    "v2/vendor/st/st-stm32h743xi-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/ti-sn74lvc1g08.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
REC = "v2/docs/records/l9t5"
DOCS = {"trace": "v2/docs/REQUIREMENTS-TRACE.md", "ioha": "v2/docs/ARCH-PCB-B-IOHA.md", "contract": "v2/docs/HW-FW-CONTRACT.md",
        "contract_t10": REC + "/apply_hw_fw_contract_t10.py", "contract_canq": REC + "/apply_hw_fw_contract_canq.py",
        "t10_out": REC + "/l9t5_t10.out", "t10_page": REC + "/T10-ROUND5.md",
        "canmb": REC + "/inputs/l4canmb-l9t5_canmb-5d14cc85.out", "l4reg": REC + "/inputs/l4reg-l4reg_compare-9fbda7a6.out",
        "ledger": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "cx46": "v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md",
        "compat": "v2/docs/parts/STM32H743-COMPATIBILITY.md", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "gen_a_buck": REC + "/apply_gen_sch_a_iocbuck.py"}
SHEETS = {"tcan": "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf", "h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf",
          "gate": "v2/vendor/ti/ti-sn74lvc1g08.pdf", "rm": "v2/vendor/st/st-rm0433-rev8.pdf", "es": "v2/vendor/st/st-es0392-rev15.pdf"}
NODES = ("A", "B", "C")
PHASES = ("S", "P1", "P2", "V")
OUTCOME = {2: "quorum held", 1: "a node out and contained", 0: "quorum lost"}
INF = float("inf")


def refuse(msg):
    sys.stderr.write("l9t5_canq: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def sha(rel, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:n]


def text(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def pdf(key, opts=("-layout",)):
    return PDFT.pdf_text(ROOT, SHEETS[key], list(opts), PDFTEXT, REC)


def page(key, n):
    return pdf(key, ("-layout", "-f", str(n), "-l", str(n)))


def one(s):
    return " ".join(s.split())


def literal(src, name):
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and any(isinstance(x, ast.Name) and x.id == name for x in node.targets):
            return ast.literal_eval(node.value)
    refuse("%s not found as a literal" % name)


# ---------------------------------------------------------------------------------------------------------------- 3. printed figures
def figures():
    """The makers' printed rows the timing rests on, each read from its committed text (a changed sheet refuses, never drifts)."""
    P, Q = {}, {}
    t = pdf("tcan")
    need(t, r"SLLSEQ7F", "the TCAN334 sheet's revision")
    m = need(t, r"tTXD_DTO\s+Driver dominant time out \(1\)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+ms", "tTXD_DTO")
    P["dto_min_ms"], P["dto_max_ms"] = float(m.group(1)), float(m.group(3))
    Q["dto"] = "tTXD_DTO, driver dominant time out: %s ms minimum, %s ms maximum (SLLSEQ7F 5.6)" % (m.group(1), m.group(3))
    m = need(t, r"tMODE\s+Mode change time\s+RL = 60.\s*, CL = 100pF,\s+(\d+)\s+(\d+)\s+.s", "tMODE")
    P["tmode_us"] = float(m.group(2))
    Q["tmode"] = "tMODE, mode change time: %s us maximum (SLLSEQ7F 5.6)" % m.group(2)
    m = need(t, r"The CAN protocol allows a maximum of eleven successive dominant bits \(on TXD\) for the\s*\n\s*worst case, where five "
               r"successive dominant bits are followed immediately by an error frame", "the eleven-bit TXD maximum")
    P["txd_max_bits"] = 11
    Q["eleven"] = "'" + one(m.group(0)) + "' (SLLSEQ7F 5.6, note 1)"
    need(t, r"HIGH\s+Lowest Current\s+Disabled \(OFF\)\(2\)\s+Disabled \(OFF\)\s+High \(Recessive\)", "Table 6-5's shutdown row")
    Q["shdn"] = "Table 6-5: SHDN HIGH, driver Disabled (OFF), receiver Disabled (OFF), RXD High (Recessive)"
    need(t, r"Bus and logic pins are high impedance \(no load", "the unpowered behaviour")
    Q["unpowered"] = "unpowered: 'Bus and logic pins are high impedance (no load to operating bus or application)' (SLLSEQ7F 1)"
    t = pdf("h743")
    need(t, r"DS12110 Rev 10", "DS12110's revision")
    blk = need(t, r"Table 160\. Output timing characteristics \(HSLV OFF\)\(1\)\(2\)\n(.*?)\n\s*01\n", "Table 160", re.S).group(1)
    m = need(blk, r"\n\s*00\s*\n\s*C=50 pF, 2\.7 V. VDD.3\.6 V\s+-\s+(\d+\.\d+)", "Table 160 speed 00 tr/tf at 50 pF")
    P["gpio_tr_ns"] = float(m.group(1))
    Q["gpio"] = "Table 160 (HSLV OFF), speed 00, tr/tf at 50 pF and 2.7 to 3.6 V: %s ns maximum (DS12110 Rev 10)" % m.group(1)
    t = pdf("gate")
    need(t, r"SCES217AA", "the SN74LVC1G08 sheet's revision")
    m = need(t, r"5\.8 Switching Characteristics, 3\.3V and 5V.*?tpd\s+A or B\s+Y\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s+(\d+)\s", "tpd", re.S)
    P["gate_tpd_ns"] = float(m.group(4))
    Q["gate"] = "tpd A or B to Y at 3.3 V +-0.3 V, 30 or 50 pF: %s ns maximum to 85 C, %s ns to 125 C (SCES217AA 5.8)" % (m.group(2), m.group(4))
    p = page("rm", 2469)
    m = need(p, r"In bus monitoring mode \(For more details\s*\n\s*refer to ISO11898-1, 10\.12 bus monitoring\), the FDCAN is able to receive valid data frames"
               r"\s*\n\s*and valid remote frames, but cannot start a transmission\. In this mode, it sends only\s*\n\s*recessive bits on the CAN bus",
             "bus monitoring mode")
    Q["mon"] = "'" + one(m.group(0)) + "' (RM0433 Rev 8 p.2469)"
    p = page("rm", 2470)
    m = need(p, r"In DAR mode all transmissions are automatically canceled after they started on the CAN\s*\n\s*bus\.", "DAR")
    Q["dar"] = "'" + one(m.group(0)) + "' (RM0433 Rev 8 p.2470)"
    p = page("rm", 2532)
    need(p, r"The receive error counter has reached the error passive level of 128", "the error passive level")
    P["ep_level"] = 128
    m = need(p, r"Actual state of the transmit error counter, values between 0 and (255)\.", "TEC's range")
    P["tec_top"] = int(m.group(1))
    p = page("rm", 2533)
    m = need(p, r"At least one of error counter has reached the Error_Warning limit of (\d+)", "Error_Warning")
    P["ew_level"] = int(m.group(1))
    p = page("rm", 2534)
    m = need(p, r"waits for (129) occurrences of bus Idle \(129 . (11)\s*\n\s*consecutive recessive bits\)", "the bus-off recovery")
    P["busoff_idles"], P["idle_bits"] = int(m.group(1)), int(m.group(2))
    Q["busoff"] = "after Bus_Off, once INIT is cleared, 'the device waits for 129 occurrences of bus Idle (129 x 11 consecutive recessive bits)' (RM0433 Rev 8 p.2534)"
    p = page("rm", 2535)
    need(p, r"Bit 27 PEA: Protocol error in arbitration phase \(nominal bit time is used\)", "PEA")
    Q["pea"] = "FDCAN_IR bit 27 PEA, 'Protocol error in arbitration phase detected (PSR.LEC different from 0,7)' (RM0433 Rev 8 p.2535)"
    page("rm", 533)
    p = page("es", 48)
    m = need(p, r"2\.24\.5\s+DAR mode transmission failure due to lost arbitration\s*\n\s*\n\s*Description\s*\n\s*(In DAR mode, the transmission may fail "
               r"due to lost arbitration at the first two identifier bits\.)\s*\n\s*\n\s*Workaround\s*\n\s*(Upon failure, clear the corresponding Tx "
               r"buffer transmission request bit TRPx of the FDCAN_TXBRP register and)\s*\n\s*(set the corresponding cancellation finished bit CFx of the "
               r"FDCAN_TXBCF register, then restart the transmission\.)", "ES0392 2.24.5")
    Q["es"] = "ES0392 Rev 15 2.24.5: '%s' Workaround: '%s %s'" % (m.group(1), m.group(2), m.group(3))
    # the draft circuit's own figures (W137, inputs/): read, never retyped
    t = text(DOCS["canmb"])
    P["mb_interval_s"] = float(need(t, r"DETECTED WITHIN (\d+\.\d+) s of its onset", "W137's interval").group(1))
    P["mb_cycle_s"] = float(need(t, r"one cycle is 6 transceivers x 4 phases x 1 window\(s\) x 100 ms = (\d+\.\d+) s", "W137's cycle").group(1))
    P["mb_on_us"] = float(need(t, r"silence takes effect within (\d+\.\d+) us of the second vote", "W137's silence").group(1))
    P["mb_off_us"] = float(need(t, r"it ends within (\d+\.\d+) us of the release", "W137's release").group(1))
    need(t, r"its readers read at least 2\.7200 V, RECESSIVE", "a dark controller reads recessive")
    need(t, r"one reader cannot frame a healthy controller, in service or while that controller is in reset", "the buffer's isolation")
    res = re.findall(r"^\s+(a vote pull-down \(10 kOhm\)|SD's 100 kOhm|an isolation resistor|a TXD pull-up \(10 kOhm\))\s+(open|short)\s.*NOT in service: RESIDUAL",
                     t, re.M)
    if len(res) != 4:
        refuse("W137's four residuals are not read")
    P["mb_residuals"] = res
    need(t, r'contract draft reads "FDCAN_CCCR\.DAR = 1" and the compatibility page\'s ES0392 2\.24\.5 row "firmware does not use DAR"', "W137-F1")
    t = text(DOCS["l4reg"])
    m = need(t, r"TPS2553-1 tlatch\s+\((\d\.\d+), (\d\.\d+), (\d\.\d+)\)\s+PRINTED\s+SLVS841F 7\.5", "the limiter's latch timer")
    P["latch_min_ms"], P["latch_max_ms"] = 1000 * float(m.group(1)), 1000 * float(m.group(3))
    m = need(t, r"IOS (\d\.\d+) to (\d\.\d+) A \(MODEL: the PRINTED row", "the limiter's band")
    P["ios_min"], P["ios_max"] = float(m.group(1)), float(m.group(2))
    need(t, r"nothing in this draft drives EN", "W138: nothing drives EN")
    t = text(DOCS["t10_out"])
    P["f2_a"] = float(need(t, r"\(f2\) both fabrics faulted, both transceivers driving into their faults: (\d\.\d+) A", "(f2)").group(1))
    P["f2v_a"] = float(need(t, r"rev V: held (\d\.\d+) A, 184\.2 C", "rev V held").group(1))
    t = text(DOCS["gen_a_buck"])
    need(t, r'"2": "RAIL_EN"', "U601's EN on RAIL_EN")
    return P, Q


# ------------------------------------------------------------------------------------------------------------- 2. the fixed interface
def interface():
    I = {}
    t = text(DOCS["trace"])
    m = need(t, r"^\*\*CON-004\*\* \(constraint\)\. (.+)$", "CON-004")
    I["con004"] = m.group(1)
    I["con004_accept"] = need(t[m.end():], r"\*Accept when:\* (.+)$", "CON-004's acceptance").group(1)
    I["con004_fabrics"] = 2 if "two independent CAN-FD fabrics" in I["con004"] else 0
    t = text(DOCS["ioha"])
    rows = {}
    for line in t.splitlines():
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(c) == 6 and c[0].isdigit():
            rows[int(c[0])] = c
    for k in (3, 4, 5, 6, 7, 8):
        if k not in rows:
            refuse("IOHA section 12 row %d missing" % k)
    I["rows"] = rows
    I["a7"] = [x.strip() for x in need(t, r"^\| A7 \|(.+)\|$", "test A7").group(1).split("|")]
    t = text(DOCS["contract_t10"])
    for name in ("FW_B21", "FW_B22", "V_B22"):
        I[name] = literal(t, name)
    I["share_quote"] = one(need(text(DOCS["t10_out"]), r"each window carries at most 2 ms of own dominant drive by the schedule, so a fault's current is\s*\n\s*averaged over the window whatever the detection time", "t10 10h (3)").group(0))
    t = text(DOCS["gen_b"])
    need(t, r'_seg = "1" if _tag == "A" else ""   # controller A sits on its own segment, behind the break links below', "A7's segments")
    t = text(DOCS["compat"])
    I["compat_dar"] = one(need(t, r"^\| 2\.24\.5 DAR mode transmission failure due to lost arbitration .*$", "the compatibility page's DAR row").group(0))
    return I


# --------------------------------------------------------------------------------- 5. the restated schedule and the drafted figures
# DRAFTED by this round (the restated FW-B22 and its attribution rule) or SESSION; each printed with its reason in section 5 and carried
# by the contract draft apply_hw_fw_contract_canq.py (section 9 reads the draft for them).
CFG = {
    "fabrics": ("A", "B"),          # CON-004's two fabrics (FDCAN1 = fabric A, FDCAN2 = fabric B); a mutant changes this
    "rate": 500e3,                  # FW-B21's least rate: every bit-time figure is longest there
    "window_us": 100000.0,          # FW-B22's window
    "frame_bits": 135,              # FW-B22's classic 8-byte frame with stuffing (MODEL, t10 10j (a))
    "slot_us": {"A": 10000.0, "B": 20000.0, "C": 30000.0},   # restated: a controller's frames only in its own 10 ms slot
    "slot_len_us": 10000.0,
    "hold_us": (52000.0, 88000.0),  # restated: the self-test's hold, in its own segment, off every state slot
    "probe_us": {"A": 60000.0, "B": 70000.0, "C": 80000.0},  # restated: one test frame per controller inside the hold
    "w137_state_us": 50000.0,       # W137's draft: the state frames at mid-window, inside the hold on the tested fabric
    "w137_hold_us": (10000.0, 90000.0),
    "variant": "restated",          # or "w137": the self-test as W137's draft words it
    "n_loss": 3,                    # a peer is lost after 3 consecutive windows with no valid state frame from it on either fabric
    "t_eval_us": 1000.0,            # each reader classifies its captures and its FDCAN's protocol-error events within 1 ms
    "t_err_bits": 150,              # a corrupted frame's error is reported by that frame's end (135 bits, the 6-bit flag, margin)
    "k": 1,                         # explained strikes before a reader votes
    "t_hold_us": 1.0e6, "t_prob_us": 10.0e6, "t_hold_cap_us": 64.0e6,   # a vote's hold, doubled within probation, its cap
    "stop_windows": 3,              # FW-B21's stop RESTATED: no valid frame for more than the loss count (3 windows); drafted: 100 ms
    "probe_period_us": 1.0e6, "probe_len_us": 100000.0,   # FW-B21's probe as drafted (t10 10f)
    "evidence": True,               # a strike needs the reader's own FDCAN error or lost frame, explained by the target
    "vote_rule": "2of2",            # the gate: the AND of the other two controllers' votes (W137's draft)
    "t_boot_us": 500000.0,          # a returning controller's start to its first listening window (ASSUMPTION; FW-B10's boot)
    "mon_windows": 2,               # a returning controller listens in bus monitoring mode for 2 windows before it sends
    "dar": 1,                       # FDCAN_CCCR.DAR (W137-F1): 1 with ES0392 2.24.5's workaround; a row tries 0
    "w137_literal": False,          # W137's precondition read literally (its own S and V silences fail the next window's check)
    "cycle_test": True,
    "scan": "full",
}
SCAN = {"full": ((0.0, 9500.0, 15000.0, 25000.0, 35000.0, 55000.0, 62000.0, 75000.0, 90000.0), 12),
        "quick": ((9500.0, 25000.0, 62000.0), 4)}
ONSET_WIN, HORIZON = 10, 40
# ISO 11898-1 is NOT held: its fault confinement increments are an ASSUMPTION (+8 a failed transmission, -1 a success); RM0433 prints
# the levels the counters meet (96, 128, 255) and the bus-off recovery. A failed attempt with DAR = 0 is retried at once; each attempt
# is taken as at least 18 bit-times (its start, an error flag of 6 and a delimiter of 8, intermission 3: the frame format, MODEL).
TEC_UP, TEC_DOWN, ATTEMPT_BITS = 8, 1, 18


def nxt(x):
    return NODES[(NODES.index(x) + 1) % 3]


def peers(x):
    return (nxt(x), nxt(nxt(x)))


def chain(cfg, P):
    """the containment chain on printed timing, us: evidence, evaluation, the vote's edge, the gate, tMODE."""
    bit = 1e6 / cfg["rate"]
    ev = cfg["t_err_bits"] * bit
    path = P["gpio_tr_ns"] / 1000.0 + P["gate_tpd_ns"] / 1000.0 + P["tmode_us"]
    held = (P["txd_max_bits"] + 1) * bit
    return {"bit": bit, "ev": ev, "eval": cfg["t_eval_us"], "path": path, "held": held, "total": ev + cfg["t_eval_us"] + path,
            "total_held": held + cfg["t_eval_us"] + path, "release": P["mb_off_us"]}


class Scenario:
    """One fault row; times in microseconds. faulty(): the controllers the row's fault is in (never part of the healthy pair)."""

    def __init__(self, rid, title, required, **kw):
        self.rid, self.title, self.required = rid, title, required
        self.ioha = kw.pop("ioha", "")
        self.dark = kw.pop("dark", {})              # node -> (t_dark, t_back or INF)
        self.wedged = kw.pop("wedged", {})          # node -> (t0, t_end or INF): no frames, no reasoned votes
        self.wedge_votes = kw.pop("wedge_votes", {})  # node -> "high": its four vote outputs stuck asserted
        self.jam = kw.pop("jam", [])                # dicts: node, fabrics, pattern, t0, t_end, victims
        self.twofaced = kw.pop("twofaced", None)    # (node, t0, t_end)
        self.phys = kw.pop("phys", {})              # fabric -> dict(kind, t0, t_end)
        self.vote_fault = kw.pop("vote_fault", {})  # (voter, target, fabric) -> "low" | "high"
        self.gate_fault = kw.pop("gate_fault", {})  # (target, fabric) -> "low" | "high"
        self.obs_fault = kw.pop("obs_fault", {})    # (reader, target, fabric) -> "open" | "stuck_dom"
        self.att_dead = kw.pop("att_dead", set())   # readers whose attribution path never votes (latent)
        self.own_dead = kw.pop("own_dead", set())   # (node, fabric): its own SHDN request never acts
        self.ignores = kw.pop("ignores", set())     # (node, fabric): the transceiver ignores SHDN
        self.extra_faulty = kw.pop("extra_faulty", set())
        self.double = kw.pop("double", False)       # a double fault: printed, never in the acceptance set
        self.latched = kw.pop("latched", None)      # (t, nodes): W138's limiter latched off; nothing drives EN
        self.cfg = kw.pop("cfg", {})                # row-specific configuration (W137-F1's DAR = 0)
        self.end = kw.pop("end", None)              # the fault's end, for the recovery rows
        self.info = kw.pop("info", False)           # a configuration the record rejects, shown with its consequence
        if kw:
            raise TypeError("unknown scenario field %s" % sorted(kw))

    def faulty(self):
        f = set(self.dark) | set(self.wedged) | {j["node"] for j in self.jam} | set(self.extra_faulty)
        if self.twofaced:
            f.add(self.twofaced[0])
        f |= set(self.wedge_votes)
        return f


class Sim:
    """The event model: per window and fabric the state frames (and the self-test's test frames) with their delivery; the jammers'
    deviations; the readers' strikes and votes; the 2-of-2 gates; FW-B21's stop and probe; the error counters."""

    def __init__(self, sc, cfg, P, test_offset=0, horizon=HORIZON):
        self.sc, self.cfg, self.P = sc, dict(cfg, **sc.cfg), P
        cfg = self.cfg
        self.F = tuple(cfg["fabrics"])
        self.W = cfg["window_us"]
        self.ch = chain(cfg, P)
        self.bit = self.ch["bit"]
        self.frame_us = cfg["frame_bits"] * self.bit
        self.dto_us = P["dto_max_ms"] * 1000.0
        self.off, self.NW = test_offset, horizon
        self.votes = defaultdict(list)       # (voter, target, fabric) -> [(on, off)] as the transceiver sees them
        self.hold = {}
        self.last_rel = {}
        self.stopped = {}                    # (node, fabric) -> t of FW-B21's stop
        self.last_ok = defaultdict(float)
        self.rx = defaultdict(dict)          # window -> {(R, X): {fabric: content}}
        self.prx = defaultdict(set)          # window -> {(R, X, fabric)} test frames delivered
        self.tests = {}
        self.tec = defaultdict(float)
        self.tec_max = defaultdict(float)
        self.destroyed = defaultdict(int)
        self.verdicts = defaultdict(list)    # (target, fabric, phase) -> [(window, ok)]
        self.ev = []
        self.seq = 0
        self.first_dev = {}                  # (node, fabric) -> t of its first deviation on the bus
        self.silenced_at = {}                # (node, fabric) -> t its gate first rises by attribution
        self.held_ep = {}
        self.now = 0.0
        self.releases = []
        self.holds = []
        self.faulty = sc.faulty()
        self.wrongly = []                    # (t, node, fabric): a conforming controller silenced by attribution votes

    # ---- states
    def dark(self, x, t):
        d = self.sc.dark.get(x)
        if d and d[0] <= t < d[1]:
            return True
        la = self.sc.latched
        return bool(la) and x in la[1] and t >= la[0]

    def wedged(self, x, t):
        w = self.sc.wedged.get(x)
        return w is not None and w[0] <= t < w[1]

    def back(self, x):
        d = self.sc.dark.get(x)
        if d and d[1] < INF:
            return d[1]
        w = self.sc.wedged.get(x)
        if w and w[1] < INF:
            return w[1]
        return None

    def functional(self, x, t):
        if self.dark(x, t) or self.wedged(x, t):
            return False
        b = self.back(x)
        if b is not None and t >= b:
            return t >= b + self.cfg["t_boot_us"] + self.cfg["mon_windows"] * self.W
        return True

    def listening(self, x, t):
        if self.dark(x, t) or self.wedged(x, t):
            return False
        b = self.back(x)
        if b is not None and t >= b:
            return t >= b + self.cfg["t_boot_us"]
        return True

    def jams(self, x):
        return [j for j in self.sc.jam if j["node"] == x]

    def active(self, j, t):
        return j["t0"] <= t < j.get("t_end", INF)

    def faulty_now(self, x, t):
        if any(self.active(j, t) for j in self.jams(x)) or self.dark(x, t) or self.wedged(x, t):
            return True
        tf = self.sc.twofaced
        return bool(tf) and tf[0] == x and tf[1] <= t < tf[2]

    def vin(self, p, tg, f, t, test=True):
        key = (p, tg, f)
        if key in self.sc.vote_fault:
            return self.sc.vote_fault[key] == "high"
        if self.dark(p, t):
            return False                     # a dark voter's line rests on its 10 kOhm pull-down
        if self.sc.wedge_votes.get(p) == "high" and (p not in self.sc.wedged or self.wedged(p, t)):
            return True
        if self.wedged(p, t):
            return False
        for on, off in self.votes[key]:
            if on <= t < off:
                return True
        return test and self.test_vote(p, tg, f, t)

    def hold_win(self):
        return self.cfg["hold_us"] if self.cfg["variant"] == "restated" else self.cfg["w137_hold_us"]

    def test_vote(self, p, tg, f, t):
        n = int(t // self.W)
        te = self.tests.get((n, f))
        if not isinstance(te, tuple) or te[0] != tg:
            return False
        h0, h1 = self.hold_win()
        u = t - n * self.W
        if not (h0 <= u < h1):
            return False
        ph = te[1]
        if ph == "P1":
            return p == nxt(tg)
        if ph == "P2":
            return p == nxt(nxt(tg))
        if ph == "V":
            if self.cfg["variant"] == "restated":
                # the restated V phase runs the ATTRIBUTION path end to end: the target's deliberate malformed test frame at the hold's
                # start is struck by each reader whose path works, and its vote acts from strike and evaluation to the hold's end
                if p in self.sc.att_dead or (p, tg, f) in self.sc.obs_fault:
                    return False
                return u >= h0 + self.ch["total"]
            return True
        return False

    def gate(self, x, f, t, test=True):
        if (x, f) in self.sc.gate_fault:
            return self.sc.gate_fault[(x, f)] == "high"
        a, b = (self.vin(p, x, f, t, test) for p in peers(x))
        return (a or b) if self.cfg["vote_rule"] == "1of1" else (a and b)

    def own(self, x, f, t):
        if (x, f) in self.sc.own_dead or self.faulty_now(x, t) and not self.sc.twofaced:
            return False                     # a faulty controller is never trusted to silence itself
        st = self.stopped.get((x, f))
        if st is not None and not self.in_probe(x, f, t):
            return True
        n = int(t // self.W)
        te = self.tests.get((n, f))
        if isinstance(te, tuple) and te[0] == x and te[1] == "S":
            h0, h1 = self.hold_win()
            if h0 <= t - n * self.W < h1:
                return True
        return False

    def in_probe(self, x, f, t):
        st = self.stopped.get((x, f))
        if st is None or t - st < self.cfg["probe_period_us"]:
            return False
        return ((t - st) % self.cfg["probe_period_us"]) < self.cfg["probe_len_us"]

    def shut(self, x, f, t):
        if (x, f) in self.sc.ignores:
            return False
        return self.own(x, f, t) or self.gate(x, f, t)

    def drives(self, x, f, t):
        return not self.dark(x, t) and not self.shut(x, f, t)

    def hears(self, x, f, t):
        return self.listening(x, t) and not self.shut(x, f, t)

    def phys(self, f, t):
        p = self.sc.phys.get(f)
        if p and p["t0"] <= t < p.get("t_end", INF):
            return p
        return None

    def same_seg(self, f, t, a, b):
        p = self.phys(f, t)
        if not p:
            return True
        if p["kind"] == "cut":
            return (a == "A") == (b == "A")
        if p["kind"] == "sever":
            return a == b
        return True

    def blocked(self, f, t):
        p = self.phys(f, t)
        return bool(p) and p["kind"] in ("stuck_rec", "stuck_dom")

    # ---- events
    def push(self, t, kind, *a):
        self.seq += 1
        heapq.heappush(self.ev, (t, self.seq, kind, a))

    def choose_test(self, n, f):
        if not self.cfg["cycle_test"]:
            return None
        if self.cfg["variant"] == "restated":
            idx = (n + self.off) % 12
            tg = NODES[idx // 4] if f == "A" else nxt(NODES[idx // 4])
            ph, fabs = PHASES[idx % 4], (f,)
        else:
            idx = (n + self.off) % 24
            tg, g = [(x, h) for x in NODES for h in ("A", "B")][idx // 4]
            if g != f:
                return None
            ph, fabs = PHASES[idx % 4], tuple(self.F)
        t = n * self.W
        if n == 0 or not all(self.functional(x, t) for x in NODES):
            return "skip"
        for g in fabs:
            if g not in self.F or any(self.stopped.get((x, g)) is not None for x in NODES):
                return "skip"
            prev = self.tests.get((n - 1, g))
            quiet = prev[0] if isinstance(prev, tuple) and prev[1] in ("S", "V") and self.cfg["w137_literal"] is False else None
            for r in NODES:
                for x in NODES:
                    if r != x and quiet not in (r, x) and g not in self.rx[n - 1].get((r, x), {}):
                        return "skip"
        for (p, tgt, g), iv in self.votes.items():
            if g in fabs and any(on <= t < off for on, off in iv):
                return "skip"
        return (tg, ph)

    def run(self):
        for n in range(self.NW):
            self.push(n * self.W, "wstart", n)
        for j in self.sc.jam:
            for f in j["fabrics"]:
                if f in self.F:
                    self.push(j["t0"], "jamstart", j["node"], f)
        if not self.cfg["evidence"]:
            for (r, x, f), kind in sorted(self.sc.obs_fault.items()):
                if kind == "stuck_dom" and f in self.F:
                    for n in range(ONSET_WIN, self.NW):
                        self.push(n * self.W + 5000.0, "phantom", r, x, f)
        end = self.NW * self.W
        while self.ev:
            t, _, kind, a = heapq.heappop(self.ev)
            if t >= end:
                break
            getattr(self, "on_" + kind)(t, *a)
        return self

    def on_wstart(self, t, n):
        for f in self.F:
            self.tests[(n, f)] = self.choose_test(n, f)
        for f in self.F:
            for x in NODES:
                ts = self.cfg["slot_us"][x] if self.cfg["variant"] == "restated" else self.cfg["w137_state_us"] + NODES.index(x) * self.frame_us
                self.push(t + ts, "frame", x, f, "state")
            te = self.tests[(n, f)]
            if isinstance(te, tuple):
                if self.cfg["variant"] == "restated":
                    for x in NODES:
                        self.push(t + self.cfg["probe_us"][x], "frame", x, f, "probe")
                self.push(t + self.hold_win()[1], "devcheck", f)
        self.push(t + self.W - 1.0, "wend", n)

    def on_wend(self, t, n):
        for f in self.F:
            te = self.tests.get((n, f))
            if not isinstance(te, tuple):
                continue
            tg, ph = te
            p1, p2 = peers(tg)
            if self.cfg["variant"] == "restated":
                got = lambda r, x: (r, x, f) in self.prx[n]
            else:
                got = lambda r, x: f in self.rx[n].get((r, x), {})
            if ph in ("S", "V"):
                ok = not (got(p1, tg) or got(p2, tg)) and not (got(tg, p1) or got(tg, p2))
            else:
                ok = got(p1, tg) and got(p2, tg) and got(tg, p1) and got(tg, p2)
            self.verdicts[(tg, f, ph)].append((n, ok))

    def on_devcheck(self, t, f):
        self.continuous(t, f)

    def continuous(self, t, f):
        for j in self.sc.jam:
            if f in j["fabrics"] and j["pattern"] in ("dense", "fast") and self.active(j, t):
                self.deviate(t, j["node"], f, self.ch["ev"])

    def on_jamstart(self, t, x, f):
        for j in self.jams(x):
            if f not in j["fabrics"] or not self.active(j, t):
                continue
            if j["pattern"] in ("dense", "fast"):
                self.deviate(t, x, f, self.ch["ev"])
            elif j["pattern"] == "held" and self.drives(x, f, t):
                self.held_ep[(x, f)] = t
                self.deviate(t, x, f, self.ch["held"])

    def on_phantom(self, t, r, x, f):
        # attribution on a TXD reading alone (the mutant): a reader whose view of x is stuck dominant strikes with no bus error behind it
        self.deviate(t, x, f, self.ch["held"], readers=(r,))

    def on_rel(self, t, x, f):
        self.last_rel[(x, f)] = t
        self.releases.append((t, x, f))
        self.continuous(t, f)
        for j in self.jams(x):
            if f in j["fabrics"] and j["pattern"] == "held" and self.active(j, t) and self.drives(x, f, t + 1.0):
                self.held_ep[(x, f)] = t
                self.deviate(t + 1.0, x, f, self.ch["held"])

    def on_probe(self, t, x, f):
        self.continuous(t, f)

    def deviate(self, t, j, f, ev_delay, readers=None):
        """a deviation by controller j on fabric f at t: each reader whose observation and evidence hold strikes and votes."""
        if readers is None:
            if not self.drives(j, f, t):
                return
            self.first_dev.setdefault((j, f), t)
        new = []
        lr = self.last_rel.get((j, f))
        h = self.cfg["t_hold_us"]
        if lr is not None and t - lr < self.cfg["t_prob_us"]:
            h = min(2 * self.hold.get((j, f), h), self.cfg["t_hold_cap_us"])
        for r in (readers or peers(j)):
            if r in self.sc.att_dead or self.sc.obs_fault.get((r, j, f)) == "open" or not self.functional(r, t):
                continue
            if readers is None and self.cfg["evidence"]:
                if not (self.hears(r, f, t) and self.same_seg(f, t, j, r) and not self.blocked(f, t)):
                    continue
            on = t + ev_delay + self.cfg["t_eval_us"] + self.ch["path"]
            if any(b > t for a, b in self.votes[(r, j, f)]):
                continue
            self.hold[(j, f)] = h
            if not new:
                self.holds.append((t, j, f, h))
            self.votes[(r, j, f)].append((on, on + h + self.ch["release"] - self.ch["path"]))
            new.append(r)
        if new:
            iv = [[v for v in self.votes[(p, j, f)] if v[1] > t] for p in peers(j)]
            if self.cfg["vote_rule"] == "1of1":
                both = [v[-1] for v in iv if v]
                self.silenced_at.setdefault((j, f), min(v[0] for v in both))
                self.push(max(v[1] for v in both), "rel", j, f)
            elif iv[0] and iv[1]:
                self.silenced_at.setdefault((j, f), max(iv[0][-1][0], iv[1][-1][0]))
                self.push(min(iv[0][-1][1], iv[1][-1][1]), "rel", j, f)
            if readers is not None or not self.faulty_now(j, t):
                if self.gate(j, f, on + 1.0, test=False):
                    self.wrongly.append((on, j, f))

    def on_frame(self, t, x, f, kind):
        n = int(t // self.W)
        if kind == "state" and not self.faulty_now(x, t) and self.functional(x, t):
            self.fwb21(t, x, f)
        if not self.functional(x, t):
            return
        if self.stopped.get((x, f)) is not None and not self.in_probe(x, f, t) and not self.faulty_now(x, t):
            return                           # stopped by FW-B21: INIT set, no attempt
        lost = False
        for j in self.sc.jam:
            jx = j["node"]
            if jx == x or f not in j["fabrics"] or not self.active(j, t) or not self.drives(jx, f, t):
                continue
            pat = j["pattern"]
            if pat in ("dense", "fast"):
                lost = True
                self.deviate(t, jx, f, self.ch["ev"])
            elif pat == "sparse" and x in j.get("victims", ()) and kind == "state":
                lost = True
                self.deviate(t, jx, f, self.ch["ev"])
            elif pat == "held":
                t0 = self.held_ep.get((jx, f))
                if t0 is not None and t0 <= t <= t0 + self.dto_us:
                    lost = True
            elif pat == "babble":
                lost = True                  # the babbler's frames win arbitration: under DAR this frame is cancelled
                self.deviate(t, jx, f, self.frame_us)
        if lost and kind == "state":
            self.destroyed[f] += 1
        sent = self.drives(x, f, t) and not self.blocked(f, t) and not lost
        got = []
        if sent:
            for r in NODES:
                if r != x and self.hears(r, f, t) and self.same_seg(f, t, x, r):
                    got.append(r)
        if not got:
            self.fail_attempt(t, x, f)
            return
        self.count_tec(x, f, -TEC_DOWN)
        self.last_ok[(x, f)] = t
        content = "x"
        tf = self.sc.twofaced
        if tf and tf[0] == x and tf[1] <= t < tf[2]:
            content = "face-" + f
        for r in got:
            self.last_ok[(r, f)] = t
            if self.stopped.get((r, f)) is not None and self.in_probe(r, f, t):
                self.stopped.pop((r, f), None)
            if kind == "state":
                self.rx[n].setdefault((r, x), {})[f] = content
            else:
                self.prx[n].add((r, x, f))
        if self.stopped.get((x, f)) is not None and self.in_probe(x, f, t):
            self.stopped.pop((x, f), None)

    def fail_attempt(self, t, x, f):
        if x in self.faulty:
            return
        if self.cfg["dar"] == 0 and self.shut(x, f, t):
            # DAR = 0: the failed frame is retried at once while the transceiver stays shut: 32 attempts of at least 18 bit-times each
            # reach Bus_Off (TEC over 255); FW-B21 then stops the fabric and probes it once a second
            self.tec[(x, f)] = 256.0
            self.tec_max[(x, f)] = 256.0
            if self.stopped.get((x, f)) is None:
                self.stop(t + 32 * ATTEMPT_BITS * self.bit, x, f)
            return
        self.count_tec(x, f, +TEC_UP)

    def count_tec(self, x, f, d):
        if x in self.faulty:
            return
        self.tec[(x, f)] = min(256.0, max(0.0, self.tec[(x, f)] + d))
        self.tec_max[(x, f)] = max(self.tec_max[(x, f)], self.tec[(x, f)])
        if self.tec[(x, f)] >= 256.0 and self.stopped.get((x, f)) is None:
            self.stop(self.now, x, f)        # Bus_Off: the device sets INIT itself (RM0433 p.2534); FW-B21 keeps it stopped

    def stop(self, t, x, f):
        self.stopped[(x, f)] = t
        k = 1
        while t + k * self.cfg["probe_period_us"] < self.NW * self.W:
            self.push(t + k * self.cfg["probe_period_us"] + 1.0, "probe", x, f)
            k += 1

    def fwb21(self, t, x, f):
        """FW-B21's stop: a fabric with a frame pending and no valid frame for more than the loss count (RESTATED; drafted: for 100 ms,
        one window) is stopped (INIT, own SHDN) and probed once a second for 100 ms."""
        lim = self.cfg["stop_windows"] * self.W
        late = (t - self.last_ok[(x, f)] > lim) if self.cfg["stop_windows"] > 1 else (t - self.last_ok[(x, f)] >= lim)
        if self.stopped.get((x, f)) is None and late and t >= lim:
            self.stop(t, x, f)

    # ---- the reading of a run
    def present(self, r, x, n):
        c = self.rx[n].get((r, x), {})
        return bool(c) and len(set(c.values())) == 1   # two copies that differ: the sender's state is discarded that window

    def summary(self, n_from):
        """the outcome: the largest set of controllers that keep each other (no pair missing each other for the loss count in either
        direction); 3: quorum held; 2 that are the healthy ones (or any 2 when the row has no faulty controller): a node out and
        contained; else quorum lost."""
        healthy = [x for x in NODES if x not in self.faulty]
        worst = {}
        for r in NODES:
            for x in NODES:
                if r == x:
                    continue
                run, wv = 0, 0
                for n in range(n_from, self.NW - 1):
                    run = 0 if self.present(r, x, n) else run + 1
                    wv = max(wv, run)
                worst[(r, x)] = wv
        nl = self.cfg["n_loss"]
        conn = lambda a, b: worst[(a, b)] < nl and worst[(b, a)] < nl
        best = ()
        for S in (("A", "B", "C"), ("A", "B"), ("A", "C"), ("B", "C")):
            if all(conn(a, b) for a in S for b in S if a < b):
                if len(S) == 3 or not self.faulty or set(S) == set(healthy):
                    best = S
                    break
        oc = 2 if len(best) == 3 else (1 if len(best) == 2 else 0)
        pairs = [(a, b) for a in (best or healthy) for b in (best or healthy) if a != b]
        gap = max([worst[p] for p in pairs] or [0])
        out = sorted(set(NODES) - set(best)) if best else sorted(NODES)
        single = 0
        tf = self.sc.twofaced
        if tf:
            for n in range(n_from, self.NW - 1):
                seen = {len(self.rx[n].get((r, tf[0]), {})) for r in healthy}
                if 1 in seen and 2 in seen:
                    single += 1
        both = []
        for x in healthy:
            for n in range(n_from, self.NW - 1):
                t = n * self.W + 5000.0
                if all(self.gate(x, f, t, test=False) for f in self.F):
                    both.append((n, x))
                    break
        sil = [self.silenced_at[k] - self.first_dev[k] for k in self.silenced_at if k in self.first_dev and k[0] in self.faulty]
        return {"outcome": oc, "gap": gap, "out": out, "both": both, "silence_us": max(sil) if sil else None,
                "destroyed": sum(self.destroyed.values()), "tec": max(self.tec_max.values()) if self.tec_max else 0.0,
                "wrongly": len(self.wrongly), "single": single}


# --------------------------------------------------------------------------------------------------------------- 6. the fault rows
def ms(x):
    return x * 1000.0


def rows():
    """(builder, the row's id) for every row; a builder takes the onset t0 (us) and returns the Scenario."""
    R = []

    def add(rid, title, req, ioha="", **kw):
        R.append((rid, lambda t0, kw=kw: Scenario(rid, title, req, ioha=ioha, **{k: (v(t0) if callable(v) else v) for k, v in kw.items()})))

    J = lambda node, fabs, pat, victims=(), dur=INF: (lambda t0: [{"node": node, "fabrics": fabs, "pattern": pat, "t0": t0, "t_end": t0 + dur,
                                                                    "victims": victims}])
    add("R3", "controller C unpowered (dark)", 1, "row 3", dark=lambda t0: {"C": (t0, INF)})
    add("R4", "controllers B and C unpowered (reference)", 0, "row 4", dark=lambda t0: {"B": (t0, INF), "C": (t0, INF)})
    add("R5a", "controller C wedged, its TXDs recessive on their pull-ups, its votes low", 1, "row 5", wedged=lambda t0: {"C": (t0, INF)})
    add("R5b", "controller C wedged with both TX pins driven dominant (held)", 1, "row 5", wedged=lambda t0: {"C": (t0, INF)},
        jam=J("C", ("A", "B"), "held"))
    add("R5c", "controller C wedged with its four vote outputs stuck asserted", 1, "row 5", wedged=lambda t0: {"C": (t0, INF)},
        wedge_votes={"C": "high"})
    add("R7a", "A7 as written: fabric A cut at its break links (controller A alone on its segment)", 2, "row 7, A7",
        phys=lambda t0: {"A": {"kind": "cut", "t0": t0}})
    add("R7b", "A7 as written: fabric B cut at its break links", 2, "row 7, A7", phys=lambda t0: {"B": {"kind": "cut", "t0": t0}})
    add("R7c", "fabric A shorted so no bit reads dominant (B1 CANH-GND, B2 CANH-CANL, B5 CANL-rail)", 2, "row 7",
        phys=lambda t0: {"A": {"kind": "stuck_rec", "t0": t0}})
    add("R7d", "fabric A shorted with the bus still working (B3 CANL-GND, B4 CANH-rail)", 2, "row 7",
        phys=lambda t0: {"A": {"kind": "works", "t0": t0}})
    add("R7e", "controller B's fabric A transceiver failed dominant, its time-out and SHDN dead (B7b)", 2, "row 7",
        phys=lambda t0: {"A": {"kind": "stuck_dom", "t0": t0}}, ignores={("B", "A")})
    add("R7f", "controller B's fabric A TXD held low by a pin fault (B7a)", 2, "row 7", jam=J("B", ("A",), "held"))
    add("R7g", "fabric A open between every controller (B6)", 2, "row 7", phys=lambda t0: {"A": {"kind": "sever", "t0": t0}})
    add("R8a", "both fabrics shorted so no bit reads dominant", 0, "row 8",
        phys=lambda t0: {"A": {"kind": "stuck_rec", "t0": t0}, "B": {"kind": "stuck_rec", "t0": t0}})
    add("R8b", "row 8 with W138's TPS2553-1 latched off on all three (the (f2) state inside its band; nothing drives EN)", 0, "row 8",
        phys=lambda t0: {"A": {"kind": "stuck_rec", "t0": t0}, "B": {"kind": "stuck_rec", "t0": t0}},
        latched=lambda t0: (t0 + 10000.0, ("A", "B", "C")))
    add("R8c", "A7 as written on both fabrics: both break-link pairs out (controller A alone on both)", 0, "row 8, A7",
        phys=lambda t0: {"A": {"kind": "cut", "t0": t0}, "B": {"kind": "cut", "t0": t0}})
    add("M1a", "GPIO-toggled TX: controller A's fabric A TX pin toggled as a GPIO, one deviation a window into B's state frame", 1, "",
        jam=J("A", ("A",), "sparse", ("B",)))
    add("M1b", "GPIO-toggled TX on both fabrics, B's state frames hit", 1, "", jam=J("A", ("A", "B"), "sparse", ("B",)))
    add("M1c", "GPIO-toggled TX on both fabrics, B's and C's state frames hit", 1, "", jam=J("A", ("A", "B"), "sparse", ("B", "C")))
    add("M1d", "GPIO-toggled TX on both fabrics at the bit rate, every frame hit", 1, "", jam=J("A", ("A", "B"), "dense"))
    add("M1e", "GPIO-toggled TX on both fabrics faster than a bit", 1, "", jam=J("A", ("A", "B"), "fast"))
    add("M1f", "TX pins held low as GPIOs on both fabrics", 1, "", jam=J("A", ("A", "B"), "held"))
    add("M2a", "a babbler: controller A's FDCANs send frames over the schedule at a winning priority on both fabrics", 1, "",
        jam=J("A", ("A", "B"), "babble"))
    add("M2b", "a babbler at a losing priority on both fabrics", 1, "", jam=J("A", ("A", "B"), "babble_low"))
    add("M3a", "a stuck vote output: B's vote on A's fabric A transceiver stuck high", 2, "", vote_fault={("B", "A", "A"): "high"})
    add("M3b", "a stuck vote output: B's vote on A's fabric A transceiver stuck low", 2, "", vote_fault={("B", "A", "A"): "low"})
    add("M3c", "controller B's firmware asserts all four of its votes (its bus behaviour conforms)", 1, "",
        vote_fault={("B", x, f): "high" for x in ("A", "C") for f in ("A", "B")}, extra_faulty={"B"})
    add("M3d", "the 2-of-2 gate of A's fabric A transceiver, output stuck high", 2, "", gate_fault={("A", "A"): "high"})
    add("M3e", "the 2-of-2 gate of A's fabric A transceiver, output stuck low", 2, "", gate_fault={("A", "A"): "low"})
    add("M4a", "a two-faced controller: A's state frames differ between the fabrics (each fabric's frame common to its receivers)", 1, "",
        twofaced=lambda t0: ("A", t0, INF))
    add("M5a", "the self-test silences a fabric A transceiver while fabric B shorts (no dominant)", 2, "row 7",
        phys=lambda t0: {"B": {"kind": "stuck_rec", "t0": t0}})
    add("M5b", "the self-test silences a fabric A transceiver while fabric B is cut (A7)", 2, "row 7, A7", phys=lambda t0: {"B": {"kind": "cut", "t0": t0}})
    add("M5c", "the self-test silences a fabric A transceiver while A toggles its fabric B TX into B's frames", 1, "",
        jam=J("A", ("B",), "sparse", ("B",)))
    add("M5d", "the self-test silences a fabric A transceiver while A jams fabric B at the bit rate", 1, "", jam=J("A", ("B",), "dense"))
    add("M5e", "the self-test silences a fabric A transceiver while controller C goes dark", 1, "row 3", dark=lambda t0: {"C": (t0, INF)})
    add("Q1", "W137 residual: an open vote pull-down (C's vote on A, fabric A) floating high while C is dark", 1, "row 3",
        dark=lambda t0: {"C": (t0, INF)}, vote_fault={("C", "A", "A"): "high"})
    add("Q2", "W137 residual: a shorted isolation resistor with its reader B driving its input (B's firmware), C's copy of A moved", 1, "",
        obs_fault={("C", "A", "A"): "stuck_dom"}, vote_fault={("B", "A", "A"): "high"}, extra_faulty={"B"})
    add("Q3", "W137 residual: an open SD resistor, A's fabric A SHDN floating high", 2, "", gate_fault={("A", "A"): "high"})
    add("Q4", "W137 residual: an open TXD pull-up while controller C resets for 50 ms, its TXDs floating dominant", 1, "",
        wedged=lambda t0: {"C": (t0, t0 + 50000.0)}, jam=J("C", ("A", "B"), "held", (), 50000.0))
    add("O1", "the observation: A's fabric A TXD buffer output stuck dominant (both readers see it; the bus is fine)", 2, "",
        obs_fault={("B", "A", "A"): "stuck_dom", ("C", "A", "A"): "stuck_dom"}, extra_faulty=set())
    add("O2", "the observation: B's reading of A's fabric A TXD open", 2, "", obs_fault={("B", "A", "A"): "open"})
    add("F1", "W137-F1: DAR = 0 (the compatibility page's row), no other fault: the self-test's silenced attempts retried", 2, "",
        cfg={"dar": 0}, info=True)
    add("F2", "FW-B21's stop as drafted (no valid frame for 100 ms, one window) under M1c's GPIO-toggled TX", 1, "",
        cfg={"stop_windows": 1}, jam=J("A", ("A", "B"), "sparse", ("B", "C")), info=True)
    add("D1", "DOUBLE: B's vote on A's fabric A stuck low (latent), then A jams fabric A at the bit rate", 2, "",
        vote_fault={("B", "A", "A"): "low"}, jam=J("A", ("A",), "dense"), double=True)
    add("D2", "DOUBLE: B's attribution path dead (latent), then A jams both fabrics at the bit rate", 0, "",
        att_dead={"B"}, jam=J("A", ("A", "B"), "dense"), double=True)
    add("D3", "DOUBLE: controller C dark (row 3), then A jams both fabrics at the bit rate", 0, "row 3",
        dark=lambda t0: {"C": (t0 - 2.0e6, INF)}, jam=J("A", ("A", "B"), "dense"), double=True)
    add("D4", "DOUBLE: B's reading of A on fabric A open (latent), then A jams fabric A at the bit rate", 2, "",
        obs_fault={("B", "A", "A"): "open"}, jam=J("A", ("A",), "dense"), double=True)
    add("D5", "DOUBLE: fabric A cut (A7), then A jams fabric B at the bit rate", 1, "row 7, A7",
        phys=lambda t0: {"A": {"kind": "cut", "t0": t0 - 2.0e6}}, jam=J("A", ("B",), "dense"), double=True)
    return R


def run_row(builder, cfg, P, scan=None):
    """the row over the scan: every onset offset in the window and every self-test cycle position; the worst of each figure."""
    offs, nto = SCAN[scan or cfg["scan"]]
    agg = None
    W = cfg["window_us"]
    for o in offs:
        for k in range(nto):
            to = k if cfg["variant"] == "restated" else 2 * k
            sc = builder(ONSET_WIN * W + o)
            s = Sim(sc, cfg, P, to).run().summary(ONSET_WIN)
            if agg is None:
                agg = dict(s, both=list(s["both"]), runs=1, sc=sc)
                continue
            agg["runs"] += 1
            agg["outcome"] = min(agg["outcome"], s["outcome"])
            for key in ("gap", "destroyed", "tec", "wrongly", "single"):
                agg[key] = max(agg[key], s[key])
            if s["silence_us"] is not None:
                agg["silence_us"] = max(agg["silence_us"] or 0.0, s["silence_us"])
            agg["out"] = sorted(set(agg["out"]) | set(s["out"]))
            agg["both"] += s["both"]
    return agg


# ------------------------------------------------------------------------------------------------- 7. the latent faults of the vote path
LATENT = [
    # element, fault, effect, how found (a phase, at once, the continuous reading, a residual), scenario fields (None: not by a phase)
    ("a vote output, its line or its gate input", "stuck low or open", "that peer's vote cannot silence the target", "V fails",
     {"vote_fault": {("B", "A", "A"): "low"}}),
    ("a vote output, its line or its gate input", "stuck high", "the other peer alone silences the target", "the other peer's P fails",
     {"vote_fault": {("B", "A", "A"): "high"}}),
    ("a vote pull-down (10 kOhm)", "short", "as its vote stuck low", "V fails", {"vote_fault": {("C", "A", "A"): "low"}}),
    ("a vote pull-down (10 kOhm)", "open", "floats only while its voter is in reset or dark", "RESIDUAL (W137)", None),
    ("the 2-of-2 gate", "output stuck low", "the vote cannot silence the target", "V fails", {"gate_fault": {("A", "A"): "low"}}),
    ("the 2-of-2 gate", "output stuck high", "the target off that fabric (row 7)", "its frames absent: at once", "once"),
    ("the vote diode", "open", "the vote cannot silence the target", "V fails", {"gate_fault": {("A", "A"): "low"}}),
    ("the own-request diode", "open", "the target's own request fails", "S fails", {"own_dead": {("A", "A")}}),
    ("SD's 100 kOhm", "open", "SD on TI's internal pull-down", "RESIDUAL (W137)", None),
    ("the transceiver's SHDN input", "ignored", "neither request nor vote silences", "S and V fail", {"ignores": {("A", "A")}}),
    ("a reader's attribution path (capture, classifier, evidence, decision)", "dead", "that reader never votes on attribution",
     "V fails (restated: V runs the attribution path)", {"att_dead": {"B"}}),
    ("an isolation resistor or a reading input", "open or stuck", "its reader blind to that TXD", "continuous reading", "cont"),
    ("a TXD buffer", "stuck or open", "both its readers see a wrong copy; the bus is fine", "continuous reading", "cont"),
    ("an isolation resistor", "short", "a driving reader reaches the buffer's output, never the TXD", "RESIDUAL (W137)", None),
    ("a TXD pull-up (10 kOhm)", "open", "the TXD on TI's own pull-up while its controller resets", "RESIDUAL (W137)", None),
    ("a node's self-test schedule", "stalled or out of turn", "phases skipped", "the published phase counter", "counter"),
    ("a node's test verdict", "wrong", "outvoted: verdicts taken 2 of 3", "the confirmation", "verdict"),
]


def detect(fields, cfg, P, scan=None):
    """the latest declaration of a latent fault over the scan: the onset anywhere in the cycle, the phase exercised, judged at the
    window's end, declared on the second consecutive failure, the verdict exchanged in the next window's state frames."""
    offs, nto = SCAN[scan or cfg["scan"]]
    W = cfg["window_us"]
    worst = 0.0
    for o in offs:
        for k in range(nto):
            to = k if cfg["variant"] == "restated" else 2 * k
            t0 = ONSET_WIN * W + o
            kw = dict(fields)
            sc = Scenario("L", "latent", 2, **kw)
            sim = Sim(sc, cfg, P, to, horizon=ONSET_WIN + 80)
            sim.faulty = set()
            # the latent fault arises at t0: before it the paths are healthy (the scenario's faults apply from t0)
            sim.sc = LatentWrap(sc, t0)
            sim.run()
            dec = None
            for key, vs in sim.verdicts.items():
                fails = [n for n, ok in vs if not ok and n * W + W > t0]
                seq = [n for n, ok in vs if n * W + W > t0]
                for a, b in zip(seq, seq[1:]):
                    if a in fails and b in fails:
                        cand = (b + 2) * W - t0
                        dec = cand if dec is None else min(dec, cand)
                        break
            if dec is None:
                return None
            worst = max(worst, dec)
    return worst


class LatentWrap:
    """a scenario whose faults exist only from t0 (a latent fault arising after start-up)."""

    def __init__(self, sc, t0):
        self._sc, self._t0 = sc, t0
        self.dark, self.wedged, self.wedge_votes, self.jam, self.twofaced, self.phys = {}, {}, {}, [], None, dict(sc.phys)
        self.extra_faulty, self.latched, self.cfg = set(), None, {}

    def faulty(self):
        return set()

    def __getattr__(self, name):
        v = getattr(self._sc, name)
        return v

    @property
    def vote_fault(self):
        return self._sc.vote_fault if self._now() else {}

    @property
    def gate_fault(self):
        return self._sc.gate_fault if self._now() else {}

    @property
    def obs_fault(self):
        return self._sc.obs_fault if self._now() else {}

    @property
    def att_dead(self):
        return self._sc.att_dead if self._now() else set()

    @property
    def own_dead(self):
        return self._sc.own_dead if self._now() else set()

    @property
    def ignores(self):
        return self._sc.ignores if self._now() else set()

    def _now(self):
        return LatentWrap.clock >= self._t0

    clock = 0.0


def _tick(sim_run):
    """run a Sim while LatentWrap.clock follows the event time (the latent fault's onset)."""
    return sim_run


# make the Sim advance LatentWrap.clock as it pops events
_orig_run = Sim.run


def _run_with_clock(self):
    for n in range(self.NW):
        self.push(n * self.W, "wstart", n)
    for j in self.sc.jam:
        for f in j["fabrics"]:
            if f in self.F:
                self.push(j["t0"], "jamstart", j["node"], f)
    if not self.cfg["evidence"]:
        for (r, x, f), kind in sorted(self.sc.obs_fault.items()):
            if kind == "stuck_dom" and f in self.F:
                for n in range(ONSET_WIN, self.NW):
                    self.push(n * self.W + 5000.0, "phantom", r, x, f)
    end = self.NW * self.W
    while self.ev:
        t, _, kind, a = heapq.heappop(self.ev)
        if t >= end:
            break
        LatentWrap.clock = t
        self.now = t
        getattr(self, "on_" + kind)(t, *a)
    return self


Sim.run = _run_with_clock


def latent_table(cfg, P, scan=None):
    W = cfg["window_us"]
    out = []
    for el, fault, eff, how, fields in LATENT:
        if isinstance(fields, dict):
            d = detect(fields, cfg, P, scan)
            bound = None if d is None else d / 1e6
        elif fields == "once":
            bound = 2 * W / 1e6           # its frames absent in the next state slot: judged at that window's end, exchanged in the next
        elif fields == "cont":
            bound = 3 * W / 1e6           # the frames of the target arrive every window; two windows that disagree, then the exchange
        elif fields == "counter":
            bound = 2 * W / 1e6
        elif fields == "verdict":
            bound = "phase"               # bounded by the phase that produced it: that phase's own bound
        else:
            bound = "residual"
        out.append((el, fault, eff, how, bound))
    return out


# --------------------------------------------------------------------------------------------------------------- 8. the recovery rows
def recovery(cfg, P):
    W = cfg["window_us"]
    t0 = ONSET_WIN * W + 15000.0
    R = []

    def ret(sim, x, t_end):
        """the first window from the fault's end in which x's state is received by both others, and on both fabrics by both."""
        first = both = None
        others = [r for r in NODES if r != x]
        for n in range(int(t_end // W), sim.NW - 1):
            if n * W + cfg["slot_us"][x] < t_end:
                continue
            ok = all(sim.present(r, x, n) for r in others)
            if first is None and ok:
                first = n
            if ok and all(len(sim.rx[n].get((r, x), {})) == len(sim.F) for r in others):
                both = n
                break
        f = lambda n: None if n is None else (n * W + cfg["slot_us"][x]) - t_end
        return f(first), f(both)

    cases = [
        ("RC1", "a transient jammer: A toggles both fabrics at the bit rate for 0.3 s, then conforms", "A", 0.3e6,
         Scenario("RC1", "", 1, jam=[{"node": "A", "fabrics": ("A", "B"), "pattern": "dense", "t0": t0, "t_end": t0 + 0.3e6}]), 80),
        ("RC2", "a dark controller: C unpowered for 2 s, then powered (boot, then bus monitoring for 2 windows)", "C", 2.0e6,
         Scenario("RC2", "", 1, dark={"C": (t0, t0 + 2.0e6)}), 80),
        ("RC3", "a fabric repaired: fabric A open between every controller for 2 s", None, 2.0e6,
         Scenario("RC3", "", 2, phys={"A": {"kind": "sever", "t0": t0, "t_end": t0 + 2.0e6}}), 80),
        ("RC5", "a two-faced controller: A's copies differ for 1 s, then agree", "A", 1.0e6,
         Scenario("RC5", "", 1, twofaced=("A", t0, t0 + 1.0e6)), 60),
        ("RC6", "W137's TXD pull-up residual: C resets for 50 ms with its TXDs floating dominant", "C", 0.05e6,
         Scenario("RC6", "", 1, wedged={"C": (t0, t0 + 0.05e6)},
                  jam=[{"node": "C", "fabrics": ("A", "B"), "pattern": "held", "t0": t0, "t_end": t0 + 0.05e6}]), 80),
    ]
    for rid, title, x, dur, sc, hz in cases:
        sim = Sim(sc, cfg, P, 0, horizon=ONSET_WIN + hz).run()
        s = sim.summary(ONSET_WIN)
        t_end = t0 + dur
        if x is None:
            back = None
            for n in range(int(t_end // W), sim.NW - 1):
                if all(sim.rx[n].get((r, y), {}).get("A") for r in NODES for y in NODES if r != y):
                    back = n * W + cfg["slot_us"]["A"] - t_end
                    break
            R.append((rid, title, back, back, s))
        else:
            a, b = ret(sim, x, t_end)
            R.append((rid, title, a, b, s))
    # a persistent jammer: the holds double within probation; the cost per release
    sc = Scenario("RC4", "", 1, jam=[{"node": "A", "fabrics": ("A", "B"), "pattern": "dense", "t0": t0}])
    sim = Sim(sc, cfg, P, 0, horizon=ONSET_WIN + 700).run()
    s = sim.summary(ONSET_WIN)
    holds = [round(h / 1e6, 1) for (t, j, f, h) in sim.holds if f == "A"]
    nrel = len({round(t / 1e5) for (t, x, f) in sim.releases if f == "A"})
    R.append(("RC4", "a persistent jammer: A toggles both fabrics at the bit rate for 70 s", None, None, dict(s, holds=holds, nrel=nrel)))
    return R


def bounds(cfg, P):
    """the recovery bounds on printed timing and the drafted rows (us)."""
    bit = 1e6 / cfg["rate"]
    busoff = P["busoff_idles"] * P["idle_bits"] * bit
    return {"busoff_us": busoff,
            "silenced": cfg["t_hold_us"] + P["mb_off_us"] + cfg["probe_period_us"] + cfg["probe_len_us"] + busoff + cfg["window_us"],
            "dark": cfg["t_boot_us"] + cfg["mon_windows"] * cfg["window_us"] + cfg["window_us"],
            "fabric": cfg["probe_period_us"] + cfg["probe_len_us"] + cfg["window_us"]}


# --------------------------------------------------------------------------------------------------- 9. the contract draft and acceptance
CONTRACT_FIGS = ("100 ms", "10 ms", "52 ms to 88 ms", "3 consecutive windows", "either fabric", "two copies that differ", "1 ms",
                 "1 s", "doubled", "64 s", "DAR = 1", "2.24.5", "bus monitoring mode", "2 windows", "never on a TXD reading alone",
                 "11 bit-times", "2 of 3")


def contract_check():
    """the draft's text carries the figures; t10's draft then this one on a scratch copy of the page: check, write, a second write
    refused, this draft alone on the tree's page refused (t10's rows absent), the tree's page untouched."""
    import shutil
    import subprocess
    import tempfile
    src = text(DOCS["contract_canq"])
    row = literal(src, "FW_B22_CANQ")
    vrow = literal(src, "V_B22_CANQ")
    missing = [f for f in CONTRACT_FIGS if f not in row]
    if "more than 3 windows" not in literal(src, "FW_B21_NEW"):
        missing.append("FW-B21's stop at the loss count")
    before = sha(DOCS["contract"], 64)
    steps = []
    with tempfile.TemporaryDirectory() as d:
        cp = os.path.join(d, "HW-FW-CONTRACT.md")
        shutil.copy(os.path.join(ROOT, DOCS["contract"]), cp)
        run = lambda script, *a: subprocess.run([sys.executable, "-B", os.path.join(ROOT, script), cp] + list(a), capture_output=True,
                                               text=True).returncode
        steps.append(("this draft on the page without t10's rows", run(DOCS["contract_canq"], "--check")))
        steps.append(("t10's draft written", run(DOCS["contract_t10"], "--write")))
        steps.append(("this draft checked", run(DOCS["contract_canq"], "--check")))
        steps.append(("this draft written", run(DOCS["contract_canq"], "--write")))
        steps.append(("a second application", run(DOCS["contract_canq"], "--write")))
        out = open(cp, encoding="utf-8").read()
        steps.append(("the written page carries the restated FW-B22 and FW-B21", 0 if row.strip() in out and "more than 3 windows" in out else 1))
    r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, DOCS["contract_canq"])], capture_output=True, text=True).returncode
    steps.append(("this draft on the tree's page", r))
    steps.append(("the tree's page untouched", 0 if sha(DOCS["contract"], 64) == before else 1))
    return row, vrow, missing, steps


def analyse(cfg=None, scan=None, only=None):
    """everything section 6 to 9 prints, as data (the tests call this with mutated configurations)."""
    cfg = dict(CFG, **(cfg or {}))
    P, Q = figures()
    I = interface()
    res = {"P": P, "Q": Q, "I": I, "cfg": cfg, "rows": {}}
    for variant in ("restated", "w137"):
        c = dict(cfg, variant=variant)
        for rid, b in rows():
            if only and rid not in only:
                continue
            res["rows"][(variant, rid)] = run_row(b, c, P, scan)
    res["latent"] = {v: latent_table(dict(cfg, variant=v), P, scan) for v in ("restated", "w137")}
    res["latent_dar0"] = detect({"vote_fault": {("B", "A", "A"): "low"}}, dict(cfg, variant="restated", dar=0), P, scan)
    res["latent_degraded"] = {v: detect({"vote_fault": {("B", "A", "B"): "low"}, "phys": {"A": {"kind": "stuck_rec", "t0": 0.0}}},
                                        dict(cfg, variant=v), P, scan) for v in ("restated", "w137")}
    res["latent_literal"] = detect({"own_dead": {("A", "A")}}, dict(cfg, variant="w137", w137_literal=True), P, scan)
    res["recovery"] = recovery(dict(cfg, variant="restated"), P)
    res["bounds"] = bounds(cfg, P)
    res["contract"] = contract_check()
    res["acceptance"] = acceptance(res)
    return res


def acceptance(res):
    cfg, I = res["cfg"], res["I"]
    A = []
    A.append(("A1 the design has exactly CON-004's two fabrics: none removed, no third",
              tuple(cfg["fabrics"]) == ("A", "B") and I["con004_fabrics"] == 2))
    bad = [(v, rid, OUTCOME[r["outcome"]]) for (v, rid), r in res["rows"].items() if not (r["sc"].double or r["sc"].info) and r["outcome"] < r["sc"].required]
    A.append(("A2 every single-fault row, on both schedules, reaches at least its required outcome", not bad))
    third = [(v, rid) for (v, rid), r in res["rows"].items() if any(f not in ("A", "B") for f in cfg["fabrics"])]
    A.append(("A3 no row relies on a fabric outside CON-004's two", not third and len(cfg["fabrics"]) == 2))
    both = [(v, rid) for (v, rid), r in res["rows"].items() if not (r["sc"].double or r["sc"].info) and r["both"]]
    A.append(("A4 no single fault silences a healthy controller on both fabrics at once", not both))
    wrong = [(v, rid) for (v, rid), r in res["rows"].items() if not (r["sc"].double or r["sc"].info) and r["wrongly"]]
    A.append(("A5 no single fault gets a controller whose bus behaviour conforms voted off", not wrong))
    gaps = [(v, rid, r["gap"]) for (v, rid), r in res["rows"].items()
            if not (r["sc"].double or r["sc"].info) and r["sc"].required >= 1 and r["gap"] >= cfg["n_loss"]]
    A.append(("A6 no single fault of a row that requires a quorum takes the surviving pair to the loss count", not gaps))
    lat = [x for x in res["latent"]["restated"] if x[4] is None]
    A.append(("A7 every latent fault of the vote path is found within a bound on the restated schedule, or is a named residual", not lat))
    rec = [r for r in res["recovery"] if r[0] not in ("RC4",) and r[2] is None]
    A.append(("A8 every contained state returns within a bound once its cause ends (RC1 to RC3, RC5, RC6)", not rec))
    want = [3, 0, 0, 0, 3, 0, 3, 0]
    A.append(("A9 the contract draft carries this record's figures, composes after t10's, refuses twice and refuses the tree",
              not res["contract"][2] and [c for _, c in res["contract"][3]] == want))
    A.append(("A10 CON-004 read as written: restated, not amended",
              "two independent CAN-FD fabrics with separate transceivers and termination" in I["con004"]))
    return A, bad


# ----------------------------------------------------------------------------------------------------------------------- printing
def fmt_t(us):
    if us is None:
        return "none"
    if us < 1000.0:
        return "%.1f us" % us
    if us < 1.0e6:
        return "%.3f ms" % (us / 1000.0)
    return "%.3f s" % (us / 1.0e6)


def main():
    res = analyse()
    P, Q, I, cfg = res["P"], res["Q"], res["I"], res["cfg"]
    out = []
    w = out.append
    w("l9t5_canq: T10 round 8, Layer 4 task L4A-55 (the ledger's RE-5 and HO-C by method M-B): the quorum service of the three I/O")
    w("supervisors under every fault row, the vote path's latent faults, the recovery proof and FW-B22 restated on the two fabrics")
    w("(MESHSAT-1357; desk analysis on printed figures; prototype design, nothing built, bought, powered or measured; it closes nothing")
    w("until independently checked)")
    w("")
    w("1. INPUTS (sha256/16)")
    for k in sorted(DOCS):
        w("   %s %s" % (sha(DOCS[k]), DOCS[k]))
    for t, h, held in PDFT.inputs(ROOT, PDFTEXT):
        w("   %s %s" % (h[:16], t))
    for k in sorted(SHEETS):
        w("   %s %s" % (sha(SHEETS[k]), SHEETS[k]))
    w("")
    w("2. THE FIXED INTERFACE (read where it is written; restated, never amended)")
    w("   CON-004 (REQUIREMENTS-TRACE.md, constraint): \"%s\"" % I["con004"])
    w("     accepted when: \"%s\"" % I["con004_accept"])
    w("     fabrics it names: %d; this round keeps both, adds none and removes none" % I["con004_fabrics"])
    for k in (3, 4, 5, 6, 7, 8):
        r = I["rows"][k]
        w("   IOHA row %d: \"%s\" -> \"%s\" (detected by: %s)" % (k, r[1], r[3], r[4]))
    w("   IOHA test A7: \"%s\" -> \"%s\"" % (I["a7"][1], I["a7"][2]))
    w("     as drawn (gen_sch_b.py): controller A sits alone on its segment behind each fabric's break links (R508/R509, R511/R512), so A7's")
    w("     cut separates A from B and C, who keep that fabric; with both links out only A is cut off (row R8c below, finding W139-F4)")
    w("   FW-B22 as drafted (apply_hw_fw_contract_t10.py, unapplied): \"%s\"" % one(I["FW_B22"].split("|")[3]))
    w("   the compatibility page's DAR row: \"%s\"" % I["compat_dar"][:160])
    w("   M-B as drafted by W137 (inputs/l4canmb-l9t5_canmb-5d14cc85.out, fnd/l4canmb 0d079eaf, unchecked): each TXD buffered (74LVC1G34 on")
    w("     its own rail) to its two peers' TIM3 captures through 2.2 kOhm; each TXD held recessive in reset by 10 kOhm; twelve votes, one per")
    w("     transceiver per peer, into an SN74LVC1G08 2-of-2 gate on the target's rail lifting SHDN through a diode; the share limiter removed;")
    w("     a dark controller reads RECESSIVE at its readers; one reader cannot frame a healthy controller; silence within %.3f us of the" % P["mb_on_us"])
    w("     second vote, released within %.2f us; the self-test's cycle %.4f s, a latent fault DETECTED WITHIN %.2f s" % (P["mb_off_us"], P["mb_cycle_s"], P["mb_interval_s"]))
    w("     its four residuals: %s" % "; ".join("%s %s" % r for r in P["mb_residuals"]))
    w("   W138's regulator stage (inputs/l4reg-l4reg_compare-9fbda7a6.out, fnd/l4reg 86dbcdff, unchecked): TPS2553-1, IOS %.4f to %.4f A," % (P["ios_min"], P["ios_max"]))
    w("     latch-off after %.0f to %.0f ms (SLVS841F 7.5, PRINTED as that record quotes it; the held sheet is not read here); 'nothing in" % (P["latch_min_ms"], P["latch_max_ms"]))
    w("     this draft drives EN'; row 8's held states %.4f A ((f2)) and %.4f A (rev V held, t10 10e) lie inside the band" % (P["f2_a"], P["f2v_a"]))
    w("")
    w("3. THE PRINTED FIGURES THE TIMING RESTS ON")
    for k in ("dto", "tmode", "eleven", "shdn", "unpowered", "gpio", "gate", "mon", "dar", "busoff", "pea", "es"):
        w("   " + Q[k])
    w("   RM0433 Rev 8 pp.2532 and 2533: error passive at %d, Error_Warning at %d, TEC 0 to %d (PRINTED); the increments (+8 a failed"
      % (P["ep_level"], P["ew_level"], P["tec_top"]))
    w("     transmission, -1 a success) are ISO 11898-1's, which is not held: ASSUMPTION")
    ch = chain(cfg, P)
    ch1 = chain(dict(cfg, rate=1e6), P)
    w("")
    w("4. THE ATTRIBUTION RULE AND THE CONTAINMENT CHAIN (DRAFTED for FW-B22 restated; the hardware figures PRINTED)")
    w("   each controller reads both other controllers' TXDs on both fabrics (its own it knows), so it sees every transmitter's intent;")
    w("   a target's TXD activity is OUT OF CONTRACT (a violation) when, on one fabric, it shows:")
    w("     V1 a dominant run longer than %d bit-times plus 0.25 us (TI: the protocol allows at most eleven successive dominant bits on TXD)" % P["txd_max_bits"])
    w("     V2 edges closer than half a bit-time (faster than any CAN bit stream)")
    w("     V3 a malformed stream where the target owns the frame (stuffing, a fixed field, its CRC, decoded from its TXD)")
    w("     V4 a dominant bit where the frame's owner sends recessive, other than the ACK slot, before any other deviation in that frame")
    w("        (the FIRST deviation: the flags of the controllers that answer it begin after it and are legal)")
    w("     V5 a start of frame outside its own slot, or more frames in a window than its slot allows (1 state and 5 event frames)")
    w("   a STRIKE needs the violation AND the reader's own evidence on that fabric: its FDCAN's protocol error (FDCAN_IR.PEA, PSR.LEC) or its")
    w("     own scheduled frame lost, inside the frame the violation hit, explained by the target's deviation; NEVER a TXD reading alone: a")
    w("     dark controller (its buffer reads recessive), a stuck buffer or a stuck reading input moves no bus bit and yields no strike;")
    w("     an error nobody's TXD explains (a physical fabric fault) yields no strike: FW-B21's stop handles it")
    w("   a reader votes on its own strike (k = %d), never on a message received over a fabric (a jammer may deny both); the 2-of-2 gate needs"
      % cfg["k"])
    w("     both peers' own strikes, so no single faulty controller silences a healthy one")
    w("   the chain at %d kbit/s: evidence %s (the frame's end, %d bit-times, MODEL) + evaluation %s (DRAFTED) + the vote's edge %.1f ns"
      % (cfg["rate"] / 1000, fmt_t(ch["ev"]), cfg["t_err_bits"], fmt_t(ch["eval"]), P["gpio_tr_ns"]))
    w("     (PRINTED) + the gate %.1f ns (PRINTED, to 125 C) + tMODE %.0f us (PRINTED) = %s from a deviation to the target's driver off;"
      % (P["gate_tpd_ns"], P["tmode_us"], fmt_t(ch["total"])))
    w("     a held TXD: %s (V1 at 12 bit-times); at 1 Mbit/s %s and %s; the TCAN334's own DTO frees a held bus after %.1f to %.1f ms"
      % (fmt_t(ch["total_held"]), fmt_t(ch1["total"]), fmt_t(ch1["total_held"]), P["dto_min_ms"], P["dto_max_ms"]))
    w("   the vote is held %s, doubled for each strike within %s of a release, at most %s; a healthy controller's error counter: each"
      % (fmt_t(cfg["t_hold_us"]), fmt_t(cfg["t_prob_us"]), fmt_t(cfg["t_hold_cap_us"])))
    w("     lost own frame +8 (ASSUMPTION), so the containment acts long before FW-B21's stop or error passive (128, PRINTED)")
    w("")
    w("5. FW-B22 RESTATED ON THE TWO FABRICS (DRAFTED, apply_hw_fw_contract_canq.py; CON-004 restated, not amended)")
    w("   the window %s on each fabric: guard 0 to 10 ms; state slots A %s, B %s, C %s, each %s, a controller's frames only in its own"
      % (fmt_t(cfg["window_us"]), fmt_t(cfg["slot_us"]["A"]), fmt_t(cfg["slot_us"]["B"]), fmt_t(cfg["slot_us"]["C"]), fmt_t(cfg["slot_len_us"])))
    w("     slot (1 state frame and at most 5 event frames, as drafted), so healthy controllers never arbitrate against each other")
    w("   the self-test's hold %s to %s in its own segment with one test frame per controller at %s, %s and %s: no state frame is ever"
      % (fmt_t(cfg["hold_us"][0]), fmt_t(cfg["hold_us"][1]), fmt_t(cfg["probe_us"]["A"]), fmt_t(cfg["probe_us"]["B"]), fmt_t(cfg["probe_us"]["C"])))
    w("     silenced by the test (W137's draft holds 10 to 90 ms with the state frames at mid-window); both fabrics tested in parallel, fabric B's")
    w("     target the next controller; a cycle is 3 targets x 4 phases = 12 windows; the restated V phase runs the attribution path end to")
    w("     end (the target's deliberate malformed test frame, struck by both readers, their votes acting to the hold's end)")
    w("   the decision: a peer's state frame for window n taken from EITHER fabric; two copies that differ discard that peer's state for n;")
    w("     a peer is lost after %d consecutive windows with no valid state frame on either fabric; 2 of 3 as drafted" % cfg["n_loss"])
    w("   DAR = 1 kept (L9T5-D2) with ES0392 2.24.5's printed workaround inside the controller's own slot: with slots healthy controllers")
    w("     never lose arbitration to each other, so 2.24.5 is met only against a faulty one; the compatibility page's 'firmware does not")
    w("     use DAR' is to be restated (W137-F1; finding W139-F1); row F1 below shows why DAR = 0 does not serve the self-test")
    w("   FW-B21's stop RESTATED at the loss count: 'no valid frame for more than 3 windows' in place of the drafted 'for 100 ms', which is one")
    w("     window of this schedule: one lost state frame then stopped a fabric for a second and the GPIO jammer of M1c took the quorum (row")
    w("     F2); the stop's delay moves no thermal figure, because \"%s\" (t10 10h (3))" % I["share_quote"])
    w("   a returning controller (a reset, a latch released, power back) listens in bus monitoring mode (MON) for %d windows, takes the epoch"
      % cfg["mon_windows"])
    w("     and the window's timing from the state frames, sets its votes and voted outputs to the read-back, and only then sends: it moves nothing")
    w("")
    w("6. THE FAULT TABLE: each row run with its onset at 9 positions in the window and 12 positions in the self-test cycle (108 runs a row")
    w("   and schedule; MODEL on the printed timing above and the DRAFTED rows); the worst of each figure; gap = the longest run of windows a")
    w("   healthy controller missed a healthy peer (the loss count is %d); contain = a deviation to the jammer's driver off on its last fabric;"
      % cfg["n_loss"])
    w("   tec = a healthy controller's largest error counter (ASSUMPTION increments) against %d (warning) and %d (passive)"
      % (P["ew_level"], P["ep_level"]))
    w("   row  IOHA        restated: outcome             W137's schedule: outcome      req  gap  contain (r/W137)      tec out   title")
    for rid, b in rows():
        r1 = res["rows"][("restated", rid)]
        r2 = res["rows"][("w137", rid)]
        sc = r1["sc"]
        req = "-" if (sc.double or sc.info) else str(sc.required)
        c = lambda r: "-" if r["silence_us"] is None else fmt_t(r["silence_us"])
        w("   %-4s %-11s %-29s %-29s %-4s %-4s %-20s %3d %-5s %s" % (
            rid, sc.ioha or "-", OUTCOME[r1["outcome"]], OUTCOME[r2["outcome"]], req, "%d/%d" % (r1["gap"], r2["gap"]),
            "%s/%s" % (c(r1), c(r2)), int(max(r1["tec"], r2["tec"])), ",".join(r1["out"]) or "-", sc.title))
    w("   required: 2 quorum held, 1 a node out and contained (or better), 0 quorum lost accepted (rows 4 and 8); DOUBLE rows print their")
    w("   outcome and are never in the acceptance set")
    two = res["rows"][("w137", "M4a")]["single"]
    w("   the two-faced controller: windows in which one healthy controller took its single copy while the other discarded both: restated %d,"
      % res["rows"][("restated", "M4a")]["single"])
    w("     W137's schedule %d (its S and V phases silence a receiver's state frames on the tested fabric)" % two)
    w("   row 8 with W138's limiter (R8b): if the TPS2553-1 latches all three, every supervisor is dark until EN or power is cycled: 'nothing")
    w("     moves' holds (the voters at the home assignment), and the return is section 8's; the held states reach the band only while both")
    w("     transceivers drive into their faults, which a healthy controller does for at most an attempt's bits; a held TXD is ended by the DTO")
    w("     after at most %.1f ms, under the latch's %.1f ms minimum: whether the latch timer restarts when the current falls is the held" % (P["dto_max_ms"], P["latch_min_ms"]))
    w("     sheet's (SLVS841F) and is NOT read here, so R8b takes W138's 'MAY latch' as written")
    w("")
    w("7. THE SELF-TEST'S INTERVAL AND THE LATENT FAULTS OF THE VOTE PATH (onset anywhere in the cycle; a phase judged at its window's end,")
    w("   declared on the second consecutive failure, the verdict exchanged in the next window: simulated where a phase finds it)")
    w("   element                                       fault                   found by                                    restated   W137's")
    for (a, b) in zip(res["latent"]["restated"], res["latent"]["w137"]):
        el, fault, eff, how, x = a
        y = b[4]
        f = lambda v: v if v in ("residual", "phase") else ("NOT FOUND" if v is None else "%.2f s" % v)
        w("   %-45s %-23s %-43s %-10s %s" % (el[:45], fault, how[:43], f(x), f(y)))
    w("   the cycle: restated 12 windows (%s), both fabrics in parallel; W137's 24 windows (%.4f s, inputs/); the interval: restated" % (fmt_t(12 * cfg["window_us"]), P["mb_cycle_s"]))
    d = res["latent_degraded"]
    g = lambda v: "NOT FOUND" if v is None else "%.2f s" % (v / 1e6)
    worst_r = max(x[4] for x in res["latent"]["restated"] if isinstance(x[4], float))
    worst_w = max(x[4] for x in res["latent"]["w137"] if isinstance(x[4], float))
    w("     %.2f s (simulated), W137's %.2f s simulated against its own %.2f s; DEGRADED (fabric A down at every controller, a fabric B vote"
      % (worst_r, worst_w, P["mb_interval_s"]))
    w("     stuck low): restated %s (the test runs on the fabric that is up, no state frame silenced), W137's %s (its precondition needs"
      % (g(d["restated"]), g(d["w137"])))
    w("     both fabrics: while one fabric is down its latent faults have no bound)")
    w("   W137's precondition read LITERALLY ('in the previous window every controller heard every other on both fabrics'): its own S and V")
    w("     phases silence the target's state frame on the tested fabric, so the phase after each is skipped and no S phase ever runs: an")
    w("     open own-request diode is then found in %s (finding W139-F5; the table above reads the precondition as W137 meant it)"
      % g(res["latent_literal"]))
    w("   with DAR = 0 (W137-F1) a silenced attempt is retried to Bus_Off in %s (32 attempts of 18 bit-times, MODEL) and FW-B21 keeps the"
      % fmt_t(32 * ATTEMPT_BITS * ch["bit"]))
    w("     fabric stopped for at least 1 s: a fabric A vote stuck low then found in %s (restated schedule)" % g(res["latent_dar0"]))
    w("   the residuals (W137's four), each needing further faults: rows Q1 to Q4 above run each with the fault that makes it act")
    w("")
    w("8. THE RECOVERY PROOF (simulated on the restated schedule; bounds on printed timing and the drafted rows)")
    bd = res["bounds"]
    w("   a controller silenced by votes on a fabric: released %s after its silence (no strike can arrive while it is silenced), SHDN low"
      % fmt_t(cfg["t_hold_us"]))
    w("     within %.2f us (W137); its own FW-B21 has meanwhile stopped that fabric (no valid frame for 3 windows) and probes it once a second;"
      % P["mb_off_us"])
    w("     a Bus_Off it reached is left in %s (129 x 11 bit-times, PRINTED); bound: hold + probe period + probe + Bus_Off + a window = %s"
      % (fmt_t(bd["busoff_us"]), fmt_t(bd["silenced"])))
    w("   a dark or reset controller: boot %s (ASSUMPTION) + MON %d windows + its slot: %s; no vote stands against it (a dark controller"
      % (fmt_t(cfg["t_boot_us"]), cfg["mon_windows"], fmt_t(bd["dark"])))
    w("     makes no strike), and it sets its outputs to the read-back before it sends: it moves nothing (IOHA A4)")
    w("   a fabric repaired: each controller's next FW-B21 probe: %s" % fmt_t(bd["fabric"]))
    w("   case  return (both peers)  on both fabrics   title")
    for rid, title, a, b, s in res["recovery"]:
        if rid == "RC4":
            w("   %-5s holds %s s on fabric A; %d releases in 70 s; the surviving pair's gap %d windows; state frames lost %d: %s" % (
                rid, ", ".join("%g" % h for h in s["holds"]), s["nrel"], s["gap"], s["destroyed"], title))
        else:
            w("   %-5s %-20s %-17s %s" % (rid, fmt_t(a), fmt_t(b), title))
    w("   a supervisor LATCHED by W138's TPS2553-1 (row 8, R8b): W138's draft drives no EN, so it returns only when +5V_IOC or its EN is")
    w("     cycled; +5V_IOC is U601's, enabled by RAIL_EN, the kit's own power: no automatic return, an operator's power cycle (finding W139-F2)")
    w("")
    A, bad = res["acceptance"]
    w("9. ACCEPTANCE (it FAILS on any row that needs a third fabric or a removed fabric)")
    for name, ok in A:
        w("   %-115s %s" % (name, "yes" if ok else "FAILS"))
    if bad:
        w("   rows under their required outcome: %s" % ", ".join("%s/%s %s" % b for b in bad))
    row, vrow, missing, steps = res["contract"]
    w("   the contract draft's FW-B22 and FW-B21 carry: %s" % ("every figure" if not missing else "MISSING " + ", ".join(missing)))
    for name, code in steps:
        w("     %-62s exit %d" % (name, code))
    w("")
    w("l9t5_canq: done")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
