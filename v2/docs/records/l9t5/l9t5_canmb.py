#!/usr/bin/env python3
"""l9t5_canmb.py: Layer 9 record l9t5, task T10 round 7; Layer 4 task L4A-54 (the ledger's RE-5 and HO-C by method M-B, re-selected
by W129 on W127's finding 1; MESHSAT-1357, 7 October 2026). PROTOTYPE DESIGN: nothing in this kit has been built, bought, powered or
measured; no figure printed here is a measurement.

It prints, deterministically and without touching the tree:
  1. the inputs, each pinned by sha256 (the makers' texts as the records' helper returns them);
  2. CON-004 and the fixed interface, read from the trace and the IOHA page (the constraint method M-B keeps);
  3. the draft apply_gen_sch_b_canmb.py composed on board B in L4-E9's change-list order (iocguard's successor), the generator run to
     its end through record l8p's gen_netlist.py, and the regenerated netlist read by pin: CON-004's three supply branches and two
     fabrics with their termination, the twelve observations, the twelve votes and the six 2-of-2 gates on the targets' own rails;
  4. the mutations that must FAIL (a draft that removes a fabric, a vote that does not reach its SHDN, an observation reading the
     node's own TXD, and four more) and the draft's refusals;
  5. the pin plan recounted on the composed candidate and read against DS12110 Rev 10 Table 9 and Table 12 (every pin a printed
     function, every observation a timer channel with its own DMA request in RM0433 Rev 8), and CON-017's count restated;
  6. the logic levels on the makers' printed rows (the vote, SHDN, the observation, a faulty reader, the dark cases);
  7. the vote path's in-service self-test, RESTATED in round 9 (W143, 7 October 2026) on W139's analysis: the 12-window cycle with both
     fabrics at once, every phase run as worded (enumerated, with the mutant of round 7's precondition), its timing on printed
     figures, its interval, the surviving fabric tested when one is down, its own faults with the attribution path, its coverage;
  8. what this closes once independently checked and what stays OPEN (L4A-55), the SESSION decisions and the findings;
  9. the predicates the test holds (v2/ecad/tools/tests/test_l9t5_canmb.py).
Run from the repository root:  python3 v2/docs/records/l9t5/l9t5_canmb.py  (about 6 s; l9t5_canmb.out is its output, regenerated
with _bin/regen_out.py). Labels: PRINTED (a maker's limit), TYPICAL, DECLARED, DRAFTED (a contract row, not applied), MODEL,
ASSUMPTION, SESSION."""
import hashlib
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import l9t5_drafts as D  # noqa: E402  (its compositions, netlists and mutations)
CHK = D.CHK

# W34's convention (Q-41 item 1, adopted in set 32): the makers' PDFs this script reads as text, each with its options. Each text is a
# verbatim input taken once on the runner by v2/docs/records/_lib/retake_pdf_text.py beside its PDF; _lib/pdftext.py returns it byte
# for byte and refuses when it is absent. Re-take after a sheet changes: python3 v2/docs/records/_lib/retake_pdf_text.py v2/docs/records/l9t5
PDFTEXT = {
    "v2/vendor/diodes/diodes-74lvc1g34.pdf": [["-layout"]],
    "v2/vendor/diodes/diodes-ap2112-ldo.pdf": [["-layout"]],
    "v2/vendor/power/st-semtech-1n4148w-c81598.pdf": [["-layout"]],
    "v2/vendor/st/st-es0392-rev15.pdf": [["-layout", "-f", "48", "-l", "48"]],
    "v2/vendor/st/st-rm0433-rev8.pdf": [["-layout", "-f", "533", "-l", "533"], ["-layout", "-f", "694", "-l", "696"]],
    "v2/vendor/st/st-stm32h743xi-datasheet.pdf": [["-layout"]],
    "v2/vendor/ti/ti-sn74lvc1g08.pdf": [["-layout"]],
    "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf": [["-layout"]],
}
_PTS = importlib.util.spec_from_file_location("records_pdftext", os.path.join(ROOT, "v2", "docs", "records", "_lib", "pdftext.py"))
PDFT = importlib.util.module_from_spec(_PTS)
_PTS.loader.exec_module(PDFT)
SHEETS = {"h743": "v2/vendor/st/st-stm32h743xi-datasheet.pdf", "tcan": "v2/vendor/ti/ti-tcan334-can-fd-transceiver.pdf",
          "g08": "v2/vendor/ti/ti-sn74lvc1g08.pdf", "ap2112": "v2/vendor/diodes/diodes-ap2112-ldo.pdf",
          "d4148": "v2/vendor/power/st-semtech-1n4148w-c81598.pdf", "g34": "v2/vendor/diodes/diodes-74lvc1g34.pdf"}
RM = "v2/vendor/st/st-rm0433-rev8.pdf"
ES = "v2/vendor/st/st-es0392-rev15.pdf"
REC = "v2/docs/records/l9t5"
DOCS = {"draft": REC + "/apply_gen_sch_b_canmb.py", "guard": REC + "/apply_gen_sch_b_iocguard.py", "shdn": REC + "/apply_gen_sch_b_canshdn.py",
        "drafts": REC + "/l9t5_drafts.py", "check": REC + "/check_l9t5_netlist.py", "gen_b": "v2/ecad/tools/gen_sch_b.py",
        "gennet": "v2/docs/records/l8p/gen_netlist.py", "trace": "v2/docs/REQUIREMENTS-TRACE.md", "ioha": "v2/docs/ARCH-PCB-B-IOHA.md",
        "compat": "v2/docs/parts/STM32H743-COMPATIBILITY.md", "ledger": "v2/docs/records/l4close/REMAINING-ENGINEERING.md",
        "t10out": REC + "/l9t5_t10.out", "contract": REC + "/apply_hw_fw_contract_t10.py", "changes": "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md",
        "u23": "v2/docs/records/efuse/apply_gen_sch_b_u23ilm.py", "u24": "v2/docs/records/efuse/apply_gen_sch_b_u24ilm.py",
        "canq": REC + "/l9t5_canq.py", "canqout": REC + "/l9t5_canq.out"}
EN = chr(0x2013)       # the sheets' minus sign and dash, written by its code point (no long dash in this file)
MINUS = chr(0x2212)    # ST's minus sign
EM = chr(0x2014)       # the empty cell of Diodes' tables
LE = chr(0x2264)       # the less-or-equal sign in ST's tables
MU = "[%s%s]" % (chr(0xB5), chr(0x3BC))
TAGS = "ABC"
# the session's choices for the self-test (SESSION, under the owner's standing rule of 26 September 2026; section 7 gives each reason).
# Round 9 (W143, 7 October 2026) restates the schedule on W139's analysis (T10-CANQ.md, W139-D1 to D3): round 7's GUARD_MS and its
# 24-window cycle are superseded (they stay in git history and in l9t5_canq.out's "W137's schedule" column)
EVERY = 1              # a test phase runs in every EVERY-th window of FW-B22's schedule
CYCLE_R = 12           # the restated cycle: 3 targets x 4 phases, both fabrics at once (fabric B's target the next controller), W139-D2
CYCLE_7 = 24           # round 7's cycle (6 transceivers x 4 phases, one at a time): SUPERSEDED, printed for comparison
N_CYCLES = 2           # the cycles the phase enumeration counts (after one cycle of warm-up)
ALIGN_MS = 1.0         # DRAFTED (round 9): each controller's window clock within 1 ms of its peers', set from their state frames' start of
                       # frame on TIM3 (W139-D12); a slot owner's frame starts within one frame time (0.27 ms at 500 kbit/s, MODEL) of its slot
PHASE_CODES = ("S", "P1", "P2", "V")
PHASES_R = (("S", "its own SHDN request over the hold: its test frame received by no peer, and it hears no peer's", "silenced"),
            ("P1", "the next controller's vote alone over the hold (commanded): every test frame received both ways", "not silenced"),
            ("P2", "the one after's vote alone over the hold (commanded): every test frame received both ways", "not silenced"),
            ("V", "its ONE malformed test frame (12 dominant bit-times, V1) at the hold's start, struck by both readers through their "
                  "attribution paths; their votes act to the hold's end and it hears no peer's test frame", "silenced"))
CONFIRM = 2            # a phase is declared failed on its CONFIRM-th consecutive failure (one corrupted frame never declares a fault)
C_SD_PF = 20.0         # ASSUMPTION: SD's node capacitance (TI prints none for the SHDN pin; the diodes' CT 2 pF each PRINTED, the trace)
C_VOTE_PF = 50.0       # ASSUMPTION, a Layer 10 bound: a vote line's capacitance, the gate's Ci and the voter's CIO included (Table 160's load)
C_OBS_PF = 46.0        # ASSUMPTION, a Layer 10 bound: an observation line's capacitance behind its isolation resistor, the reader's CIO included
TOL_PLAIN = 0.05       # ASSUMPTION: a resistor whose value names no tolerance ("10k", "100k") is taken at +-5 %


def refuse(msg):
    sys.stderr.write("l9t5_canmb: REFUSED: %s\n" % msg)
    sys.exit(2)


def need(t, pat, what, flags=re.M):
    m = re.search(pat, t, flags)
    if not m:
        refuse("%s: the pattern for it no longer matches its pinned input" % what)
    return m


def sha(relpath, n=16):
    return hashlib.sha256(open(os.path.join(ROOT, relpath), "rb").read()).hexdigest()[:n]


def text(relpath):
    return open(os.path.join(ROOT, relpath), encoding="utf-8").read()


_PDF = {}


def pdf(key):
    if key not in _PDF:
        _PDF[key] = PDFT.pdf_text(ROOT, SHEETS[key], ["-layout"], PDFTEXT, REC)
    return _PDF[key]


def rm_page(first, last):
    return PDFT.pdf_text(ROOT, RM, ["-layout", "-f", str(first), "-l", str(last)], PDFTEXT, REC)


def draft():
    sp = importlib.util.spec_from_file_location("l9t5_canmb_draft", os.path.join(ROOT, DOCS["draft"]))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


# ------------------------------------------------------------------------------------------------ the makers' printed rows
def block(t, title, what, n=1200):
    """the text of a table from its title (the occurrence followed by its header, not the list of tables) for n characters"""
    for m in re.finditer(re.escape(title), t):
        nxt = t[m.end():m.end() + 400]
        if "Symbol" in nxt or "Speed" in nxt or "PARAMETER" in nxt or "Parameter" in nxt:
            return t[m.start():m.start() + n]
    refuse("%s: no table titled %r" % (what, title))


def figures():
    F = {}
    h = pdf("h743")
    b157 = block(h, "Table 157. I/O static characteristics", "DS12110 Table 157 (rev V)", 7000)
    vil, vih = re.findall(r"(\d\.\d)VDD\(1\)", b157)[:2]
    F["vil_k"], F["vih_k"] = float(vil), float(vih)
    F["rpu"] = tuple(float(x) * 1e3 for x in need(b157, r"RPU\s+VIN=VSS\s+(\d+)\s+(\d+)\s+(\d+)", "RPU").groups())
    F["ilkg"] = float(need(b157, r"0< VIN %s Max\(VDDXXX\)\(9\)\s+-\s+-\s+\+/-(\d+)" % LE, "FT leakage").group(1)) * 1e-9
    F["cio"] = float(need(b157, r"CIO\s+I/O pin capacitance\s+-\s+-\s+(\d+)\s+-\s+pF", "CIO").group(1)) * 1e-12
    b120 = block(h, "Table 120. Current characteristics", "DS12110 Table 120 (rev V)", 2600)
    need(b120, r"3\. Positive injection is not possible on these I/Os and does not occur for input voltages lower than the",
         "DS12110 Table 120 note 3 (no positive injection)")
    b158 = block(h, "Table 158. Output voltage characteristics for all I/Os except PC13, PC14, PC15 and PI8(1)", "DS12110 Table 158", 1500)
    F["vol"] = float(need(b158, r"VOL\s+Output low level voltage\s+IIO=8 mA\s+-\s+([\d.]+)", "VOL at 8 mA").group(1))
    F["voh_drop"] = float(need(b158, r"VOH\s+Output high level voltage\s+IIO=-8 mA\s+VDD%s([\d.]+)" % MINUS, "VOH at -8 mA").group(1))
    F["iio"] = 8e-3
    b160 = block(h, "Table 160. Output timing characteristics (HSLV OFF)(1)(2)", "DS12110 Table 160", 2600)
    v50 = re.findall(r"C=50 pF, 2\.7 V%s VDD%s3\.6 V\s+-\s+([\d.]+)" % (LE, LE), b160)
    if len(v50) < 2:
        refuse("DS12110 Table 160: the speed 00 rows at 50 pF are not where they were")
    F["fmax00"], F["tr00"] = float(v50[0]) * 1e6, float(v50[1]) * 1e-9
    t = pdf("tcan")
    F["tmode"] = tuple(float(x) * 1e-6 for x in need(t, r"tMODE\s+Mode change time\s+RL = 60\S, CL = 100pF,\s+(\d+)\s+(\d+)\s+%ss" % MU, "tMODE").groups())
    F["dto"] = tuple(float(x) * 1e-3 for x in need(t, r"tTXD_DTO\s+Driver dominant time out \(1\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ms", "tTXD_DTO").groups())
    s = t[t.index("STB/S/SHDN Terminals"):]
    F["sd_vih"] = float(need(s, r"VIH\s+HIGH level input voltage\s+(\d+(?:\.\d+)?)\s+V", "SHDN VIH").group(1))
    F["sd_vil"] = float(need(s, r"VIL\s+LOW level input voltage\s+(\d+(?:\.\d+)?)\s+V", "SHDN VIL").group(1))
    m = need(s, r"IIH\s+HIGH level input leakage current\s+STB, S, SHDN = VCC = 3\.6V\s+%s(\d+)\s+0\s+(\d+)" % EN, "SHDN IIH")
    F["sd_iih"] = float(m.group(2)) * 1e-6
    m = need(s, r"IIL\s+LOW level input leakage current\s+STB, S, SHDN = 0V, VCC = 3\.6V\s+%s(\d+)\s+0\s+(\d+)" % EN, "SHDN IIL")
    F["sd_iil"] = float(m.group(1)) * 1e-6
    x = t[t.index("TXD Terminal (CAN Transmit Data Input)"):]
    F["tx_vih"] = float(need(x, r"VIH\s+HIGH level input voltage\s+(\d+(?:\.\d+)?)\s+V", "TXD VIH").group(1))
    F["tx_vil"] = float(need(x, r"VIL\s+LOW level input voltage\s+(\d+(?:\.\d+)?)\s+V", "TXD VIL").group(1))
    F["tx_iih"] = float(need(x, r"IIH\s+HIGH level input leakage current\s+TXD = VCC = 3\.6V\s+%s[\d.]+\s+0\s+([\d.]+)" % EN, "TXD IIH").group(1)) * 1e-6
    F["tx_off"] = float(need(x, r"ILKG\(OFF\)\s+Unpowered leakage current\s+TXD = 3\.6V, VCC = 0V\s+%s(\d+)\s+0\s+([\d.]+)" % EN, "TXD ILKG(OFF)").group(2)) * 1e-6
    need(t, r"Table 6-5\. CAN Transceivers with Shutdown Mode.*?HIGH\s+Lowest Current\s+Disabled \(OFF\)\(2\)\s+Disabled \(OFF\)\s+High \(Recessive\)",
         "TCAN334 Table 6-5 (SHDN high: driver off, receiver off, RXD high)", re.S)
    need(t, r"SHDN\s+5\s+\S+\s+5\s+\S+\s+I\s+Drive high for shutdown mode\. Internal pull-down\.", "TCAN334 pin 5")
    g = pdf("g08")
    F["g_vih"] = float(need(g, r"VIH\s+High-level input voltage\s+V\s*\n\s+VCC = 3V to 3\.6V\s+([\d.]+)\s*\n", "SN74LVC1G08 VIH").group(1))
    F["g_vil"] = float(need(g, r"VIL\s+Low-level input voltage\s+V\s*\n\s+VCC = 3V to 3\.6V\s+([\d.]+)\s*\n", "SN74LVC1G08 VIL").group(1))
    F["g_vcc"] = tuple(float(v) for v in need(g, r"Operating\s+([\d.]+)\s+([\d.]+)\s*\n\s*VCC\s+Supply voltage", "SN74LVC1G08 VCC").groups())
    F["g_slew"] = float(need(g, r"Input transition rise or fall rate\s+VCC = 3\.3V \S 0\.3V\s+(\d+)\s+ns/V", "SN74LVC1G08 transition rate").group(1)) * 1e-9
    F["g_ii"] = float(need(g, r"II\s+VI = 5\.5V or GND\s+0 to 5\.5V\s+\S(\d+)\s+\S\d+\s+%sA" % MU, "SN74LVC1G08 II").group(1)) * 1e-6
    F["g_ioff"] = float(need(g, r"Ioff\s+VI or VO = 5\.5V\s+0\s+\S(\d+)\s+\S\d+\s+%sA" % MU, "SN74LVC1G08 Ioff").group(1)) * 1e-6
    m = need(g, r"IOH = %s100%sA\s+1\.65V to 5\.5V\s+VCC %s ([\d.]+)\s+VCC %s ([\d.]+)" % (EN, MU, EN, EN), "SN74LVC1G08 VOH at -100 uA")
    F["g_voh_drop"] = (float(m.group(1)), float(m.group(2)))      # -40 to 85 C, -40 to 125 C
    F["g_vol"] = float(need(g, r"IOL = 100%sA\s+1\.65V to 5\.5V\s+([\d.]+)" % MU, "SN74LVC1G08 VOL at 100 uA").group(1))
    sw = need(g, r"5\.6 Switching Characteristics, CL = 15pF.*?VCC = 1\.8V\s+VCC = 2\.5V\s+VCC = 3\.3V\s+VCC = 5V.*?tpd\s+A or B\s+Y\s+"
                 r"([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+ns", "SN74LVC1G08 tpd", re.S)
    F["g_tpd"] = float(sw.group(6)) * 1e-9                        # VCC = 3.3 V +- 0.3 V, -40 to 85 C, MAX
    F["g_icc"] = float(need(g, r"ICC\s+VI = 5\.5V or GND,\s+IO = 0\s+1\.65V to 5\.5V\s+(\d+)\s+(\d+)\s+%sA" % MU, "SN74LVC1G08 ICC").group(1)) * 1e-6
    F["g_dicc"] = float(need(g, r"One input at VCC %s 0\.6V,\s*\n\s*%sICC\s+3V to 5\.5V\s+(\d+)\s+(\d+)\s+%sA" % (EN, chr(0x394), MU), "SN74LVC1G08 delta ICC").group(1)) * 1e-6
    F["g_ci"] = float(need(g, r"Ci\s+VI = VCC or GND\s+3\.3V\s+(\d+)\s+(\d+)\s+pF", "SN74LVC1G08 Ci").group(1)) * 1e-12
    b = pdf("g34")
    need(b, r"Document number: DS36108 Rev\. 10 - 2", "the 74LVC1G34 sheet's revision")
    F["b_vih"] = float(need(b, r"VCC = 3V to 3\.6V\s+(\d+)\s+%s\s*\n\s+VCC = 4\.5V to 5\.5V\s+0\.7 \S VCC" % EM, "74LVC1G34 VIH").group(1))
    F["b_vil"] = float(need(b, r"VCC = 3V to 3\.6V\s+%s\s+([\d.]+)\s*\n\s+VCC = 4\.5V to 5\.5V\s+%s\s+0\.3 \S VCC" % (EM, EM), "74LVC1G34 VIL").group(1))
    F["b_voh100"] = float(need(b, r"IOH = -100%sA\s+1\.65V to 5\.5V\s+VCC %s ([\d.]+)" % (MU, EN), "74LVC1G34 VOH at -100 uA").group(1))
    F["b_voh16"] = float(need(b, r"IOH = -16mA\s+([\d.]+)\s+%s\s+%s\s+([\d.]+)" % (EM, EM), "74LVC1G34 VOH at -16 mA").group(1))   # -40 to 85 C, VCC 3 V
    F["b_vol16"] = float(need(b, r"IOL = 16mA\s+%s\s+%s\s+([\d.]+)\s+%s\s+([\d.]+)" % (EM, EM, EM), "74LVC1G34 VOL at 16 mA").group(1))
    F["b_ii"] = float(need(b, r"II\s+Input Current\s+VI = 5\.5V or GND\s+0V to 5\.5V\s+%s\s+\S0\.1\s+\S(\d+)" % EM, "74LVC1G34 II").group(1)) * 1e-6
    F["b_ioff"] = float(need(b, r"IOFF\s+VI or VO = 5\.5V\s+0V\s+%s\s+%s\s+\S(\d+)" % (EM, EM), "74LVC1G34 IOFF").group(1)) * 1e-6
    F["b_icc"] = float(need(b, r"ICC\s+Supply Current\s+5\.5V\s+%s\s+0\.1\s+(\d+)" % EM, "74LVC1G34 ICC").group(1)) * 1e-6
    a = pdf("ap2112")
    sec = need(a, r"AP2112-3\.3 Electrical Characteristics.*?ISHORT\s+Short Current Limit", "the AP2112-3.3 table", re.S).group(0)
    m = need(sec, r"VOUT\s+VOUT\s*\n.*?\n.*?\*([\d.]+)%\s+\*([\d.]+)%", "the AP2112-3.3 VOUT band", re.S)
    F["vout"] = (float(m.group(1)) / 100.0, float(m.group(2)) / 100.0)
    m = need(sec, r"Load Regulation\s+VIN = 4\.3V, 1mA \S IOUT \S 600mA\s+(-?[\d.]+)\s+([\d.]+)\s+([\d.]+)\s+%/A", "the AP2112-3.3 load regulation")
    F["loadreg"] = (float(m.group(1)) / 100.0, float(m.group(3)) / 100.0)
    d = pdf("d4148")
    F["vf"] = float(need(d, r"at IF = 1 mA\s+-\s+([\d.]+)", "1N4148W VF at 1 mA").group(1))
    F["ct"] = float(need(d, r"CT\s+-\s+(\d+)\s+pF", "1N4148W CT").group(1)) * 1e-12
    F["vf_ta"] = need(d, r"Characteristics at Ta = (\d+)", "1N4148W conditions").group(1)
    r533 = rm_page(533, 533)
    need(r533, r"During and just after reset, the alternate functions are not active and most of the I/O ports\s+are configured in analog mode\.",
         "RM0433 p.533: the reset state")
    F["debug_pins"] = re.findall(r"(P[AB]\d+): N?J", r533)
    r694 = rm_page(694, 696)
    F["dma_tables"] = sorted(set(re.findall(r"Table (12[23])\. DMAMUX1: assignment of multiplexer inputs to resources", r694)))
    F["dma_tim3"] = {n: sorted(set(re.findall(r"(\d+)\s+TIM3_CH%d\b" % n, r694))) for n in (1, 2, 3, 4)}
    gen = text(DOCS["gen_b"])
    m = need(gen, r'_intent\.rail\("\+3V3_IOC%s" % _t, 3\.3, ([\d.]+), ([\d.]+)', "the +3V3_IOCx rail's declaration")
    F["i_rail"] = float(m.group(2))                                 # the rail's declared peak
    c = text(DOCS["compat"])
    F["xtal_ppm"] = float(need(c, r"ESR 30, \+-10/\+-(\d+) ppm: meets", "the fitted crystal's tolerance as the compatibility page reads it").group(1)) * 1e-6
    F["dar_compat"] = need(c, r"^\| 2\.24\.5 DAR mode transmission failure due to lost arbitration \|.*\| (firmware does not use DAR) \|$",
                           "the compatibility page's ES0392 2.24.5 row").group(1)
    F["dar_contract"] = need(text(DOCS["contract"]), r"(FDCAN_CCCR\.DAR = 1) on both fabrics", "the contract draft's DAR row").group(1)
    e = PDFT.pdf_text(ROOT, ES, ["-layout", "-f", "48", "-l", "48"], PDFTEXT, REC)
    m = need(e, r"^(2\.24\.5)\s+DAR mode transmission failure due to lost arbitration\s*\n.*?Workaround\s*\n\s+(Upon failure,.*?restart the transmission\.)",
             "ES0392 2.24.5's workaround", re.M | re.S)
    F["es_item"], F["es_work"] = m.group(1), " ".join(m.group(2).split())
    m = need(e, r"ES0392 - Rev (\d+)\s+page (\d+)/(\d+)", "ES0392's page footer")
    F["es_rev"], F["es_page"] = m.group(1), "page %s/%s" % (m.group(2), m.group(3))
    o = text(DOCS["t10out"])
    F["queue"] = float(need(o, r"a state frame waits at most ([\d.]+) ms behind every other frame of its window", "FW-B22's queue wait").group(1)) * 1e-3
    F["window"] = float(need(o, r"in every (\d+) ms window, one state\s*\n?\s*frame", "FW-B22's window").group(1)) * 1e-3
    F["i_r6"] = float(need(o, r"the bounded state with the limiters' pull-ups\s+([\d.]+) A", "round 6's bounded state").group(1))
    F["share_bits"] = int(need(o, r"(\d+) bit-times against FW-B21's (\d+)", "FW-B22's dominant bound").group(1))
    return F


def canq():
    """W139's restated schedule (round 8, L4A-55), which round 9 restates in section 7: the CFG literal of l9t5_canq.py read with ast
    (never run) and the figures its committed output prints (its event model of the schedule)"""
    import ast
    cfg = None
    for node in ast.parse(text(DOCS["canq"])).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "CFG":
            cfg = ast.literal_eval(node.value)
    if cfg is None:
        refuse("l9t5_canq.py carries no CFG literal")
    o = text(DOCS["canqout"])
    Q = {"cfg": cfg}
    Q["chain_ms"] = float(need(o, r"= ([\d.]+) ms from a deviation to the target's driver off", "canq's containment chain").group(1))
    Q["sim_s"] = float(need(o, r"the interval: restated\n\s+([\d.]+) s \(simulated\)", "canq's restated interval").group(1))
    Q["degraded_s"] = float(need(o, r"stuck low\): restated ([\d.]+) s \(the test runs on the fabric that is up", "canq's degraded interval").group(1))
    Q["literal"] = need(o, r"open own-request diode is then found in (NOT FOUND|[\d.]+ s)", "canq's literal precondition").group(1)
    Q["att_s"] = float(need(o, r"^\s+a reader's attribution path .*?\s([\d.]+) s\s+NOT FOUND$", "canq's attribution row").group(1))
    Q["f2"] = need(o, r"^\s+F2\s+-\s+(quorum lost)\s+(quorum lost)\s", "canq's row F2").groups()
    Q["fabric_s"] = float(need(o, r"a fabric repaired: each controller's next FW-B21 probe: ([\d.]+) s", "canq's fabric bound").group(1))
    return Q


def phases_run(variant, literal, down=()):
    """the phases a fault-free schedule runs over N_CYCLES cycles after one cycle of warm-up, per (target, fabric, phase): a MODEL of
    the schedule (no sheet's figure). 'restated': CYCLE_R windows, both fabrics at once (fabric A's target by (n mod 12) div 4, fabric
    B's the next controller), the state frames in their slots outside the hold, so no phase silences one; 'w137': round 7's CYCLE_7
    windows, one transceiver at a time (A on fabric A, A on B, B on A, ...), its state frames at mid-window inside the hold, so its S and
    V phases silence the target's state frame on the tested fabric. literal: the precondition as worded ("in the previous window every
    controller heard every other", on the tested fabric for the restated schedule, on both for round 7's); else round 7's as W137 meant
    it (the test's own silence excluded). down: fabrics on which no controller receives a state frame (down at every controller)."""
    from collections import Counter
    ran = Counter()
    L = CYCLE_R if variant == "restated" else CYCLE_7
    quiet = set()                                      # (node, fabric): a state frame the previous window's test silenced
    for n in range(L * (N_CYCLES + 1)):
        idx = n % L
        if variant == "restated":
            x = TAGS[idx // 4]
            tests = {"A": (x, PHASE_CODES[idx % 4]), "B": (TAGS[(TAGS.index(x) + 1) % 3], PHASE_CODES[idx % 4])}
        else:
            j = idx // 4
            tests = {"AB"[j % 2]: (TAGS[j // 2], PHASE_CODES[idx % 4])}
        now = set()
        for f, (x, ph) in sorted(tests.items()):
            fabs = (f,) if variant == "restated" else ("A", "B")
            ok = all(g not in down for g in fabs) and not (literal and any(q[1] in fabs for q in quiet))
            if ok:
                if n >= L:
                    ran[(x, f, ph)] += 1
                if variant == "w137" and ph in ("S", "V"):
                    now.add((x, f))
        quiet = now
    return ran


# ------------------------------------------------------------------------------------------------ the composition
def order(with_mb=True):
    """board B's drafts in L4-E9's change-list order: l9t5's after record l8r2's (R-233, R-234, R-243 or R-235, R-245), this record's
    canmb after iocguard (it edits iocguard's lines), the efuse record's R-236 and R-237 after l9t5's, Layer 6's three last"""
    seq = D.seq_of("b", "slot")
    at = seq.index(D.MINE["b"]) + 1
    mid = [os.path.join(ROOT, REC, f) for f in ("apply_gen_sch_b_iocpre.py", "apply_gen_sch_b_canshdn.py", "apply_gen_sch_b_iocset.py",
                                                "apply_gen_sch_b_iocguard.py")]
    if with_mb:
        mid.append(os.path.join(ROOT, DOCS["draft"]))
    mid += [os.path.join(ROOT, DOCS["u23"]), os.path.join(ROOT, DOCS["u24"])]
    return seq[:at] + mid + seq[at:]


def build(d, tag, with_mb=True, mutate_text=None):
    seq = order(with_mb)
    p, res, ok = D.compose("b", seq, d, tag)
    if not ok:
        return seq, res, ok, None, None
    if mutate_text:
        src = open(p, encoding="utf-8").read()
        old, new = mutate_text
        if src.count(old) != 1 or old == new:
            refuse("the mutant's old text is not in the composed generator once")
        open(p, "w", encoding="utf-8").write(src.replace(old, new))
    rc, net, _t = D.netlist("b", p, d, tag)
    if rc:
        return seq, res, False, None, net
    return seq, res, ok, net, CHK.read(open(net, "rb").read())


def mcu(k):
    return "U%d" % (41 + 10 * k)


def con004(nl):
    """CON-004's acceptance read on a netlist: three independent supply branches and two fabrics, each fabric carrying one transceiver
    of every controller, its own split termination at both ends and its own break links; no part joins the two fabrics"""
    why = []
    fab = {f: {"CANH_%s1" % f, "CANL_%s1" % f, "CANH_%s" % f, "CANL_%s" % f} for f in "AB"}
    rails = set()
    for k, t in enumerate(TAGS):
        v33 = "+3V3_IOC%s" % t
        rails.add(v33)
        outs = [m for m in CHK.members(nl, v33) if CHK.value(nl, m.split(".")[0]).startswith("AP2112K") and m.endswith(".5")]
        if outs != ["U%d.5" % (40 + 10 * k)]:
            why.append("%s's sources are %s, not its own LDO U%d alone" % (v33, outs, 40 + 10 * k))
        seg = "1" if t == "A" else ""
        for j, f in enumerate("AB"):
            x = "U%d" % (43 + j + 10 * k)
            why += CHK.rows(nl, [(x, "7", "CANH_%s%s" % (f, seg)), (x, "6", "CANL_%s%s" % (f, seg)), (x, "3", v33)])
            if not CHK.value(nl, x).startswith("TCAN334"):
                why.append("%s is %r, not a TCAN334" % (x, CHK.value(nl, x)[:20]))
    if len(rails) != 3:
        why.append("the three controllers do not have three rails")
    why += CHK.rows(nl, [("R470", "1", "CANH_A1"), ("R470", "2", "CANT_A"), ("R471", "1", "CANT_A"), ("R471", "2", "CANL_A1"), ("C460", "1", "CANT_A"),
                         ("R504", "1", "CANH_A"), ("R504", "2", "CANT2_A"), ("R505", "1", "CANT2_A"), ("R505", "2", "CANL_A"), ("C506", "1", "CANT2_A"),
                         ("R472", "1", "CANH_B1"), ("R472", "2", "CANT_B"), ("R473", "1", "CANT_B"), ("R473", "2", "CANL_B1"), ("C461", "1", "CANT_B"),
                         ("R506", "1", "CANH_B"), ("R506", "2", "CANT2_B"), ("R507", "1", "CANT2_B"), ("R507", "2", "CANL_B"), ("C507", "1", "CANT2_B"),
                         ("R508", "1", "CANH_A1"), ("R508", "2", "CANH_A"), ("R509", "1", "CANL_A1"), ("R509", "2", "CANL_A"),
                         ("R511", "1", "CANH_B1"), ("R511", "2", "CANH_B"), ("R512", "1", "CANL_B1"), ("R512", "2", "CANL_B")])
    for f in "AB":
        xs = sorted({m.split(".")[0] for n in fab[f] for m in CHK.members(nl, n) if CHK.value(nl, m.split(".")[0]).startswith("TCAN334")})
        if len(xs) != 3:
            why.append("fabric %s carries %d transceivers (%s), not one per controller" % (f, len(xs), ", ".join(xs)))
    for ref, pins in nl["pins"].items():
        on = {f for f in "AB" for n in pins.values() if n in fab[f]}
        if len(on) > 1:
            why.append("%s joins fabric A and fabric B" % ref)
    return ("HOLDS" if not why else "FAIL"), why


def mb_check(nl, M):
    """the draft read on a netlist by pin: for each controller X and fabric n, X's TXD reaches only its controller, its transceiver, its
    10 kOhm pull-up to X's own rail and the input of its buffer on X's own rail; the buffer's output reaches the other two through their
    own isolation resistors and nothing else; each reader's input is its planned pin; X's SD is lifted only by X's own request diode and
    the 2-of-2 gate's diode; the gate sits on X's own rail and its two inputs are the two OTHER controllers' planned vote pins, each held
    low by 10 kOhm; no TPS3701 but the rail trips remains, and the rail trips stay"""
    why = []
    obs_of = {(d_, f): p for p, (_port, d_, f, _af, _n) in M.OBS_PINS.items()}
    vote_of = {(d_, f): p for p, (_port, d_, f) in M.VOTE_PINS.items()}
    for k, t in enumerate(TAGS):
        v33 = "+3V3_IOC%s" % t
        for j, f in enumerate("AB"):
            n = j + 1
            tx, sd, mbn, txb = ("IOC%s_CAN%d_%s" % (t, n, x) for x in ("TX", "SD", "MB", "TXB"))
            gate, xcvr, buf = "U%d" % (47 + j + 10 * k), "U%d" % (43 + j + 10 * k), "U%d" % (580 + 2 * k + j)
            d_own, d_vote = "D%d" % (400 + 10 * k + 2 * j), "D%d" % (401 + 10 * k + 2 * j)
            r_sd, pu = "R%d" % (603 + 20 * k + 4 * j), "R%d" % (606 + 20 * k + 4 * j)
            pds = ("R%d" % (604 + 20 * k + 4 * j), "R%d" % (605 + 20 * k + 4 * j))
            isos = ("R%d" % (611 + 20 * k + 2 * j), "R%d" % (612 + 20 * k + 2 * j))
            cdec, cbuf = "C%d" % (944 + 10 * k + 2 * j), "C%d" % (943 + 10 * k + 2 * j)
            peers = (TAGS[(k + 1) % 3], TAGS[(k + 2) % 3])
            if sorted(CHK.members(nl, sd)) != sorted(["%s.5" % xcvr, "%s.1" % d_own, "%s.1" % d_vote, "%s.1" % r_sd]):
                why.append("%s reaches %s" % (sd, CHK.members(nl, sd)))
            why += CHK.rows(nl, [(d_own, "2", "IOC%s_CAN%d_SHDN" % (t, n)), (d_vote, "2", mbn), (r_sd, "2", "GND"),
                                 (gate, "3", "GND"), (gate, "4", mbn), (gate, "5", v33), (cdec, "1", v33), (cdec, "2", "GND"),
                                 (buf, "2", tx), (buf, "3", "GND"), (buf, "4", txb), (buf, "5", v33), (cbuf, "1", v33), (cbuf, "2", "GND"),
                                 (pu, "1", v33), (pu, "2", tx)])
            if sorted(CHK.members(nl, mbn)) != sorted(["%s.4" % gate, "%s.2" % d_vote]):
                why.append("%s reaches %s, not the gate's output and the vote diode alone" % (mbn, CHK.members(nl, mbn)))
            if not CHK.value(nl, gate).startswith(M.GATE) or nl["comps"].get(gate, {}).get("lcsc", M.GATE_LCSC) not in (M.GATE_LCSC, ""):
                why.append("%s is %r, not the %s" % (gate, CHK.value(nl, gate)[:24], M.GATE))
            if not CHK.value(nl, buf).startswith(M.BUF) or CHK.value(nl, pu) != M.R_TXPU:
                why.append("%s is %r and %s %r, not the %s and the %s TXD pull-up" % (buf, CHK.value(nl, buf)[:20], pu, CHK.value(nl, pu), M.BUF, M.R_TXPU))
            ins = [CHK.pin(nl, gate, "1"), CHK.pin(nl, gate, "2")]
            want = ["IOC%s_CAN%d_VOTE%s" % (t, n, p) for p in peers]
            if sorted(ins) != sorted(want) or len(set(ins)) != 2:
                why.append("%s's inputs are %s, not the two other controllers' votes %s" % (gate, ins, want))
            for p, pd, iso in zip(peers, pds, isos):
                kp = TAGS.index(p)
                dist = (k - kp) % 3                    # X seen from the voter and reader p: 1 the next controller, 2 the one after
                vnet, onet = "IOC%s_CAN%d_VOTE%s" % (t, n, p), "IOC%s_CAN%d_OBS%s" % (t, n, p)
                gp = "1" if CHK.pin(nl, gate, "1") == vnet else "2"
                if sorted(CHK.members(nl, vnet)) != sorted(["%s.%s" % (gate, gp), "%s.1" % pd, "%s.%d" % (mcu(kp), vote_of[(dist, f)])]):
                    why.append("%s reaches %s, not %s's planned vote pin %d, the gate and its pull-down" % (vnet, CHK.members(nl, vnet), mcu(kp), vote_of[(dist, f)]))
                if CHK.pin(nl, pd, "2") != "GND" or CHK.value(nl, pd) != M.R_VOTE:
                    why.append("%s is not the %s pull-down of %s" % (pd, M.R_VOTE, vnet))
                if CHK.pin(nl, iso, "1") != txb or CHK.pin(nl, iso, "2") != onet or CHK.value(nl, iso) != M.R_ISO:
                    why.append("%s is not the %s from %s to %s" % (iso, M.R_ISO, txb, onet))
                if sorted(CHK.members(nl, onet)) != sorted(["%s.2" % iso, "%s.%d" % (mcu(kp), obs_of[(dist, f)])]):
                    why.append("%s reaches %s, not %s's planned reading pin %d behind %s" % (onet, CHK.members(nl, onet), mcu(kp), obs_of[(dist, f)], iso))
            if sorted(CHK.members(nl, tx)) != sorted(["%s.%d" % (mcu(k), 82 if n == 1 else 52), "%s.1" % xcvr, "%s.2" % buf, "%s.2" % pu]):
                why.append("%s reaches %s, not the controller, its transceiver, its buffer's input and its pull-up" % (tx, CHK.members(nl, tx)))
            if sorted(CHK.members(nl, txb)) != sorted(["%s.4" % buf] + ["%s.1" % r for r in isos]):
                why.append("%s reaches %s, not the buffer's output and the two isolation resistors" % (txb, CHK.members(nl, txb)))
    # whose TXD each reading pin reads, traced through the netlist (the resistor, then the buffer to its input), never from the names:
    # never its own controller's
    for k, t in enumerate(TAGS):
        for p in M.OBS_PINS:
            net = CHK.pin(nl, mcu(k), str(p))
            rs = [m.split(".")[0] for m in CHK.members(nl, net or "") if m.startswith("R")]
            far = {CHK.pin(nl, r, q) for r in rs for q in ("1", "2")} - {net}
            src = set()
            for fn in far:
                bufs = [m.split(".")[0] for m in CHK.members(nl, fn or "") if m.endswith(".4") and CHK.value(nl, m.split(".")[0]).startswith(M.BUF)]
                src |= {CHK.pin(nl, b_, "2") for b_ in bufs} | ({fn} if fn and re.fullmatch(r"IOC[ABC]_CAN[12]_TX", fn) else set())
            if net is None or "IOC%s_CAN1_TX" % t in src or "IOC%s_CAN2_TX" % t in src:
                why.append("%s pin %d reads %r: its own controller's TXD, or nothing" % (mcu(k), p, net))
            if len(src) != 1 or not re.fullmatch(r"IOC[ABC]_CAN[12]_TX", next(iter(src), "") or ""):
                why.append("%s pin %d reads %s, not one other controller's TXD through a resistor and a buffer" % (mcu(k), p, sorted(x or "?" for x in src)))
    lim = [r for r, c in nl["comps"].items() if c.get("value", "").startswith("TPS3701") and r not in ("U46", "U56", "U66")]
    if lim:
        why.append("a TPS3701 other than the rail trips remains: %s" % lim)
    for k, t in enumerate(TAGS):
        u = 40 + 10 * k
        why += CHK.rows(nl, [("U%d" % (u + 6), "6", "IOC%s_LDO_EN" % t), ("U%d" % (u + 6), "4", "IOC%s_ISF" % t), ("U%d" % (u + 5), "4", "IOC%s_LDO_IN" % t)])
    return ("DRAWN" if not why else "FAIL"), why


# ------------------------------------------------------------------------------------------------ the pin plan
def h743_names():
    t = text(DOCS["gen_b"])
    m = need(t, r"^H743 = (\{.*?\})\s*$", "the generator's H743 pin table")
    import ast
    return ast.literal_eval(m.group(1))


SUPPLY = ("VDD", "VSS", "VSSA", "VDDA", "VREF+", "VBAT")


def counts(nl, names, ref):
    pins = nl["pins"].get(ref, {})
    conn = {int(p) for p, n in pins.items() if n != "NC" and not n.startswith("unconnected-")}   # a KiCad netlist gives a no-connect pin an 'unconnected-' net
    sup = {p for p in names if names[p] in SUPPLY}
    used = conn - sup
    return len(used), len(sup), 100 - len(used) - len(sup), conn


def table9(h, pin, port):
    m = re.findall(r"^%d\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(%s)\s+(I/O)\s+(\S+)" % (pin, port), h, re.M)
    return m[0] if len(m) == 1 else None


def af_of(h, port, func):
    """the AF number of func on port in DS12110's Port x alternate function table: the column of the header AFn nearest to where the
    function's name stands on the port's row (a single-line cell); None when the row does not carry it"""
    lines = h.splitlines()
    got = []
    for i, ln in enumerate(lines):
        if not re.match(r"^\s+%s\s" % port, ln) or not re.search(r"\b%s\b" % func, ln):
            continue
        hdr = next((lines[j] for j in range(i, max(0, i - 80), -1) if re.search(r"\bAF0\s+AF1\s+AF2\s+AF3", lines[j])), None)
        tbl = next((lines[j] for j in range(i, max(0, i - 120), -1) if re.search(r"Table 1[0-4]\. Port [A-E] alternate functions", lines[j])), "")
        if hdr is None:
            continue
        cols = [(mm.start() + len(mm.group(0)) / 2.0, int(mm.group(1))) for mm in re.finditer(r"AF(\d+)", hdr)]
        c = re.search(r"\b%s\b" % func, ln).start() + len(func) / 2.0
        got.append((min(cols, key=lambda x: abs(x[0] - c))[1], re.search(r"Table 1[0-4]", tbl).group(0) if tbl else "?"))
    return got[0] if len(got) == 1 else None


# ------------------------------------------------------------------------------------------------ the report
def main():
    out = []
    w = out.append
    F = figures()
    M = draft()
    names = h743_names()
    pred = {}
    w("l9t5_canmb: T10 round 7, Layer 4 task L4A-54 (the ledger's RE-5 and HO-C by method M-B): the peers' TXD observation and 2-of-2")
    w("SHDN vote on both fabrics, the pin plan and the vote path's in-service self-test (MESHSAT-1357; a DRAFT, NOT APPLIED; prototype design,")
    w("nothing built or measured)")
    w("")
    w("1. INPUTS (sha256/16)")
    for k in sorted(DOCS):
        w("   %s %s" % (sha(DOCS[k]), DOCS[k]))
    for rel_, h_, held in PDFT.inputs(ROOT, PDFTEXT):
        w("   %s %s%s" % ((h_ or "ABSENT")[:16], rel_, "  (held back)" if held else ""))
    for k in sorted(SHEETS):
        w("   %s %s" % (sha(SHEETS[k]), SHEETS[k]))
    w("   %s %s" % (sha(RM), RM))
    w("")
    # ---------------------------------------------------------------- 2. the constraint
    tr, io = text(DOCS["trace"]), text(DOCS["ioha"])
    c004 = need(tr, r"^\*\*CON-004\*\* \(constraint\)\. (.*)$", "CON-004's text").group(1)
    acc = need(tr, r"^\*\*CON-004\*\*.*?\n\n\*Accept when:\* (.*?)$", "CON-004's acceptance", re.M | re.S).group(1)
    row7 = need(io, r"^\| 7 \| (One CAN fabric breaks or a transceiver fails dominant) \| n/a \| (quorum continues on the other fabric) \|", "IOHA row 7")
    a7 = need(io, r"^\| A7 \| Heartbeat fabric break \| (cut fabric A, then fabric B, one at a time) \| (quorum survives each)", "IOHA test A7")
    c17 = need(tr, r"reads every pin the three supervisors use \((\d+) of 100; (\d+) supplies, (\d+) unconnected\)", "CON-017's count")
    w("2. THE FIXED INTERFACE M-B KEEPS (Layer 3, accepted; read from the trace and the IOHA page, never amended here)")
    w("   CON-004 (constraint, core, BLOCKER): \"%s\"" % c004)
    w("     accepted when: \"%s\"" % acc)
    w("   IOHA row 7: \"%s\" -> \"%s\"; test A7: \"%s\" -> \"%s\"" % (row7.group(1), row7.group(2), a7.group(1), a7.group(2)))
    w("   CON-017's evidence counts \"%s of 100; %s supplies, %s unconnected\" (the tree's board B, before any draft): restated in section 5" % c17.groups())
    w("")
    # ---------------------------------------------------------------- 3. the composition
    R = {}
    with tempfile.TemporaryDirectory(prefix="l9t5_canmb_") as d:
        seq0, res0, ok0, net0, nl0 = build(d, "mb0", with_mb=False)
        seq1, res1, ok1, net1, nl1 = build(d, "mb1", with_mb=True)
        if not (ok0 and ok1 and nl0 and nl1):
            refuse("board B did not compose or regenerate: %s" % "; ".join("%s %s" % (s, v) for s, v, _m in (res0 + res1) if v != "OK"))
        w("3. THE COMPOSITION: board B's drafts in L4-E9's change-list order, apply_gen_sch_b_canmb.py straight after iocguard (R-245), the efuse")
        w("   record's R-236 and R-237 after it, Layer 6's three last; the generator run to its end through record l8p's gen_netlist.py")
        for s, v, _m in res1:
            w("     %-44s %s" % (s, v))
        w("   %d drafts: %s; the netlist regenerated: %d parts and %d nets with canmb, %d and %d without it (iocguard's state)" % (
            len(seq1), "every step OK" if ok1 else "REFUSED", len(nl1["comps"]), len({n for p in nl1["pins"].values() for n in p.values() if n != "NC"}),
            len(nl0["comps"]), len({n for p in nl0["pins"].values() for n in p.values() if n != "NC"})))
        added = sorted(set(nl1["comps"]) - set(nl0["comps"]), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        removed = sorted(set(nl0["comps"]) - set(nl1["comps"]), key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        retyped = sorted([r for r in set(nl0["comps"]) & set(nl1["comps"]) if nl0["comps"][r].get("value") != nl1["comps"][r].get("value")
                          or nl0["pins"].get(r) != nl1["pins"].get(r)],
                         key=lambda r: (r[0], int(re.sub(r"\D", "", r) or 0)))
        w("   added %d: %s" % (len(added), ", ".join(added)))
        w("   removed %d: %s" % (len(removed), ", ".join(removed)))
        w("   kept with a new value or new nets %d: %s" % (len(retyped), ", ".join(retyped)))
        cv, cw = con004(nl1)
        cv0, _cw0 = con004(nl0)
        mv, mw = mb_check(nl1, M)
        w("   CON-004 read on the regenerated netlist (three supply branches, two fabrics, one transceiver of each controller on each, split")
        w("   termination at both ends of each, the A7 break links, no part joining the fabrics): %s%s (before canmb: %s)" % (
            cv, (": " + "; ".join(cw[:3])) if cw else "", cv0))
        w("   the draft read by pin (each TXD on its controller, its transceiver, its 10 kOhm pull-up and its buffer's input only; each buffer's")
        w("   output through two isolation resistors to the planned reading pins of the other two, traced back to never its own TXD; each SD")
        w("   lifted only by its own request's diode and its 2-of-2 gate's diode; each gate on its target's rail with the other two controllers'")
        w("   planned votes, each held low by 10 kOhm; no TPS3701 left but the rail trips, which stay): %s%s" % (mv, (": " + "; ".join(mw[:3])) if mw else ""))
        w("")
        # ------------------------------------------------------------ 4. mutations and refusals
        w("4. THE MUTATIONS (each must FAIL) AND THE REFUSALS")
        muts = []
        _s, _r, okf, _n, nlf = build(d, "mbfab", True, ('"6": "CANL_%s%s" % (_f, _seg), "7": "CANH_%s%s" % (_f, _seg)',
                                                         '"6": "CANL_A%s" % _seg, "7": "CANH_A%s" % _seg'))
        muts.append(("a draft that removes fabric B (every transceiver on fabric A)", con004(nlf)[0] if okf and nlf else "REFUSED", "CON-004"))
        swaps = (("a vote that does not reach its SHDN (A's fabric A vote diode on fabric B's SD)", [(("D401", "1"), ("D403", "1"))]),
                 ("an observation reading the node's own TXD (B's reader of A on B's own buffered TXD)", [(("R611", "1"), ("R631", "1"))]),
                 ("a 1-of-1 vote (both of A's fabric A gate inputs from B)", [(("U47", "2"), ("R604", "1"))]),
                 ("the gate on a peer's rail (U47 on +3V3_IOCB)", [(("U47", "5"), ("U57", "5"))]),
                 ("an observation without its isolation (B's pin 65 on A's buffered TXD directly)", [(("U51", "65"), ("R611", "1"))]),
                 ("an observation without its buffer (B's resistor on A's TXD itself)", [(("R611", "1"), ("U580", "2"))]))
        for i, (lab, sw) in enumerate(swaps):
            q = D.mutate(net1, d, "mbm%d" % i, sw)
            muts.append((lab, mb_check(CHK.read(open(q, "rb").read()), M)[0], "the draft's reading"))
        for lab, v, by in muts:
            w("   mutated, %-88s %s (%s)" % (lab + ":", v, by))
        bare = os.path.join(d, "bare_gen_sch_b.py")
        shutil.copy(D.GEN["b"], bare)
        mbp = os.path.join(ROOT, DOCS["draft"])
        r_bare = subprocess.run([sys.executable, "-B", mbp, bare, "--write"], capture_output=True)
        r_twice = subprocess.run([sys.executable, "-B", mbp, os.path.join(d, "mb1_gen_sch_b.py"), "--write"], capture_output=True)
        r_tree = subprocess.run([sys.executable, "-B", mbp, D.GEN["b"], "--write"], capture_output=True)
        refused = (r_bare.returncode == 3 and b"iocguard" in r_bare.stderr, r_twice.returncode == 3 and b"already applied" in r_twice.stderr,
                   r_tree.returncode == 3 and b"NOT RELEASED" in r_tree.stderr)
        w("   the draft on a generator without iocguard: %s; a second time: %s; on the tree's own generator: %s" % (tuple(
            "refused" if x else "NOT REFUSED" for x in refused[:2]) + ("refused (NOT RELEASED)" if refused[2] else "NOT REFUSED",)))
        w("")
        # ------------------------------------------------------------ 5. the pin plan
        h = pdf("h743")
        w("5. THE PIN PLAN on the composed candidate, read against DS12110 Rev 10 (Table 9 the pin and its I/O structure, Table 12 the")
        w("   alternate function) and RM0433 Rev 8 (p.533 the reset state; Tables 122 and 123 the DMA requests)")
        plan_ok = True
        for k, t in enumerate(TAGS):
            u = mcu(k)
            w("   controller %s (%s):" % (t, u))
            for p in sorted(M.PLANNED):
                if p in M.OBS_PINS:
                    port, dist, f, func, afn = M.OBS_PINS[p]
                    use = "reads %s's TXD on fabric %s" % (TAGS[(k + dist) % 3], f)
                else:
                    port, dist, f = M.VOTE_PINS[p]
                    func, afn = None, None
                    use = "votes to silence %s on fabric %s" % (TAGS[(k + dist) % 3], f)
                t9 = table9(h, p, port)
                af = af_of(h, port, func) if func else None
                before, after = CHK.pin(nl0, u, str(p)), CHK.pin(nl1, u, str(p))
                ok = (names.get(p) == port and t9 is not None and before in (None, "NC") and after not in (None, "NC")
                      and (func is None or af == (afn, "Table 12")) and port not in F["debug_pins"])
                plan_ok &= ok
                w("     pin %2d %-5s %-6s %-48s %-34s net %-18s %s" % (
                    p, port, t9[2] if t9 else "?", use, ("%s AF%d (%s)" % (func, af[0], af[1])) if af else ("GPIO output, " + (t9[1] if t9 else "?")),
                    after, "free before: yes" if before in (None, "NC") else "free before: NO (%s)" % before))
        cnt0 = {t: counts(nl0, names, mcu(k)) for k, t in enumerate(TAGS)}
        cnt1 = {t: counts(nl1, names, mcu(k)) for k, t in enumerate(TAGS)}
        tree_nl = CHK.read(open(os.path.join(ROOT, CHK.COMMITTED["b"]), "rb").read())
        cnt_t = counts(tree_nl, names, "U41")
        tim3 = all(len(F["dma_tim3"][n]) >= 1 for n in (1, 2, 3, 4)) and F["dma_tables"] == ["122", "123"]
        w("   every pin: the generator's port name, a Table 9 row with I/O, free on the candidate before canmb, no debug pin (RM0433 p.533 names")
        w("   %s), each reading pin's timer channel in Table 12 at AF2: %s" % (", ".join(F["debug_pins"]), "yes" if plan_ok else "NO"))
        w("   the reading pins' timer: TIM3_CH1 to TIM3_CH4 each carry a DMA request in RM0433's Tables %s (inputs %s): %s; so each" % (
            " and ".join(F["dma_tables"]), "; ".join("CH%d %s" % (n, "/".join(F["dma_tim3"][n])) for n in (1, 2, 3, 4)), "yes" if tim3 else "NO"))
        w("   reader can time-stamp every edge of the four TXDs it reads on one counter without a processor step per edge (the attribution")
        w("   firmware is L4A-55's and Layer 5's); the votes are plain outputs, analog (high impedance) during and just after reset (p.533), so")
        w("   the 10 kOhm holds each gate input low then")
        w("   THE COUNT (CON-017's convention: signal pins with the two VCAP pins, supplies apart, the rest unconnected), per controller:")
        w("     the tree's board B (U41, committed netlist)              %d of 100; %d supplies, %d unconnected" % cnt_t[:3])
        w("     the candidate with every draft before canmb (iocguard's)  %d of 100; %d supplies, %d unconnected" % cnt0["A"][:3])
        w("     the candidate with canmb                                  %d of 100; %d supplies, %d unconnected (the same for B and C: %s)" % (
            cnt1["A"][:3] + ("yes" if cnt1["A"][:3] == cnt1["B"][:3] == cnt1["C"][:3] else "NO",)))
        w("   CON-017 restated (for its owner; this record changes no registry text): \"%d of 100; %d supplies, %d unconnected\" on the composed" % cnt1["A"][:3])
        w("   candidate, the 8 new pins of each controller (4 readings, 4 votes) among them; the tree's count reproduces the evidence's: %s" % (
            "yes" if cnt_t[:3] == tuple(int(x) for x in c17.groups()) else "NO"))
        w("")
        R.update(cv=cv, cv0=cv0, mv=mv, muts=muts, refused=refused, plan_ok=plan_ok, tim3=tim3, cnt0=cnt0, cnt1=cnt1, cnt_t=cnt_t,
                 n_seq=len(seq1), ok1=ok1, added=added, removed=removed, retyped=retyped, nl1=nl1)
    # ---------------------------------------------------------------- 6. levels
    i_r = F["i_rail"]
    vdd_lo = 3.3 * (F["vout"][0] + F["loadreg"][0] * i_r)
    vdd_hi = 3.3 * (F["vout"][1] + F["loadreg"][1] * i_r)
    riso = float(re.match(r"([\d.]+)k", M.R_ISO).group(1)) * 1e3   # the draft's value, read, never typed
    riso_lo, riso_hi = riso * 0.99, riso * 1.01
    rpd_hi, rsd_lo, rsd_hi = 10e3 * (1 + TOL_PLAIN), 100e3 * (1 - TOL_PLAIN), 100e3 * (1 + TOL_PLAIN)
    L = {}
    L["vote_hi"] = vdd_lo - F["voh_drop"]
    L["vote_lo"] = (F["g_ii"] + F["ilkg"]) * rpd_hi
    L["vote_i"] = vdd_hi / (10e3 * (1 - TOL_PLAIN))
    L["sd_i"] = vdd_hi / rsd_lo + F["sd_iih"]
    L["sd_hi"] = vdd_lo - F["g_voh_drop"][1] - F["vf"]
    L["sd_lo"] = F["sd_iil"] * rsd_hi
    rpu_hi = 10e3 * 1.01                               # the TXD pull-up, 10 kOhm 1 %
    L["obs_hi"] = vdd_lo - F["b_voh100"]               # the buffer's high at its own rail; its load a few uA (the readers' pull-ups)
    L["obs_vih"] = F["vih_k"] * vdd_hi
    L["obs_lo"] = F["b_vol16"] + (vdd_hi - F["b_vol16"]) * riso_hi / (riso_hi + F["rpu"][0])
    L["obs_vil"] = F["vil_k"] * vdd_lo
    L["fault_i"] = vdd_hi / riso_lo + vdd_hi / (riso_lo + F["rpu"][0])
    L["tx_reset"] = vdd_lo - (F["tx_iih"] + F["b_ii"]) * rpu_hi
    L["tx_pu_i"] = vdd_hi / (10e3 * 0.99)
    L["dark_read"] = vdd_lo - F["b_ioff"] * (riso_hi + F["rpu"][2])
    lv_ok = (L["vote_hi"] > F["g_vih"] and L["vote_lo"] < F["g_vil"] and L["vote_i"] < F["iio"] and F["g_vcc"][0] <= vdd_lo and vdd_hi <= 3.6
             and L["sd_i"] < 100e-6 and L["sd_hi"] > F["sd_vih"] and L["sd_lo"] < F["sd_vil"] and L["obs_hi"] > L["obs_vih"]
             and L["obs_lo"] < L["obs_vil"] and L["fault_i"] < 16e-3 and F["b_voh16"] > L["obs_vih"] and L["tx_reset"] > max(F["tx_vih"], F["b_vih"])
             and F["vol"] < min(F["tx_vil"], F["b_vil"]) and L["tx_pu_i"] < F["iio"] and L["dark_read"] > F["vih_k"] * vdd_lo)
    w("6. THE LOGIC LEVELS on the makers' printed rows (MODEL from PRINTED figures; each controller's rail from its AP2112K-3.3: %.1f %% to" % (100 * F["vout"][0]))
    w("   %.1f %% PRINTED with the load regulation %+.0f to %+.0f %%/A PRINTED at the rail's declared %.2f A: %.4f V to %.4f V, inside the gate's %.2f to" % (
        100 * F["vout"][1], 100 * F["loadreg"][0], 100 * F["loadreg"][1], i_r, vdd_lo, vdd_hi, F["g_vcc"][0]))
    w("   %.1f V row; a resistor that names no tolerance at +-%.0f %% (ASSUMPTION))" % (F["g_vcc"][1], 100 * TOL_PLAIN))
    w("   the vote: a voter's high at least %.4f V (VDD %s %.1f V at 8 mA, DS12110 Table 158) against the SN74LVC1G08's VIH %.1f V; a voter in reset" % (
        L["vote_hi"], "-", F["voh_drop"], F["g_vih"]))
    w("     or dark: its input at most %.4f V (II %.0f uA and the pin's %.0f nA into %.1f kOhm) against VIL %.1f V; the voter's output current at" % (
        L["vote_lo"], F["g_ii"] * 1e6, F["ilkg"] * 1e9, rpd_hi / 1e3, F["g_vil"]))
    w("     most %.3f mA (inside Table 158's 8 mA)" % (L["vote_i"] * 1e3))
    w("   SHDN lifted by the vote: at least %.4f V (the gate's VCC %s %.2f V at -100 uA, -40 to 125 C, less the 1N4148W's %.3f V at 1 mA, both" % (
        L["sd_hi"], "-", F["g_voh_drop"][1], F["vf"]))
    w("     PRINTED; the diode's figure is printed at %s C and the diode carries at most %.1f uA here, so the 1 mA maximum is taken as its bound" % (
        F["vf_ta"], L["sd_i"] * 1e6))
    w("     at the kit's -20 C floor too: ASSUMPTION, margin %.3f V) against the TCAN334's VIH %.1f V; the gate's load %.1f uA, inside its 100 uA row" % (
        L["sd_hi"] - F["sd_vih"], F["sd_vih"], L["sd_i"] * 1e6))
    w("   SHDN at rest: at most %.3f V (the pin's %.0f uA out, IIL PRINTED, into %.0f kOhm) against VIL %.1f V (round 6's figure, unchanged)" % (
        L["sd_lo"], F["sd_iil"] * 1e6, rsd_hi / 1e3, F["sd_vil"]))
    w("   the observation (the reader's own pull-up enabled, RPU %.0f to %.0f kOhm PRINTED, a firmware row): the buffer's high reads at least %.4f V" % (
        F["rpu"][0] / 1e3, F["rpu"][2] / 1e3, L["obs_hi"]))
    w("     (VCC - %.1f V at -100 uA, 74LVC1G34 PRINTED) against 0.7 VDD = %.4f V at the reader's highest rail; its low at most %.4f V (VOL %.1f V" % (
        F["b_voh100"], L["obs_vih"], L["obs_lo"], F["b_vol16"]))
    w("     at 16 mA, VCC 3 V, PRINTED, plus the divider of %.0f Ohm against RPU's least) against 0.3 VDD = %.4f V at the reader's lowest rail" % (
        riso_hi, L["obs_vil"]))
    w("     (DS12110 Table 157, CMOS levels, tested)")
    w("   a FAULTY READER driving its input (an output where an input belongs) reaches only the buffer's output, through its %.0f Ohm: at most" % riso_lo)
    w("     %.3f mA with the other reader's pull-up, inside the 16 mA at which the buffer holds at least %.1f V high and at most %.1f V low (VCC 3 V," % (
        L["fault_i"] * 1e3, F["b_voh16"], F["b_vol16"]))
    w("     -40 to 85 C, PRINTED): the other reader still reads %.1f V against its %.4f V (margin %.3f V, on the 16 mA row for at most %.2f mA) and" % (
        F["b_voh16"], L["obs_vih"], F["b_voh16"] - L["obs_vih"], L["fault_i"] * 1e3))
    w("     %.4f V against its %.4f V; and the TXD and the transceiver's input are never reached (the buffer's input draws at most %.0f uA, PRINTED)," % (
        L["obs_lo"], L["obs_vil"], F["b_ii"] * 1e6))
    w("     so one reader cannot frame a healthy controller, in service or while that controller is in reset with its TX pin undriven")
    w("   the TXD itself: held at least %.4f V while its controller is in reset (10 kOhm 1 %% against the TCAN334's IIH %.0f uA and the buffer's" % (
        L["tx_reset"], F["tx_iih"] * 1e6))
    w("     II %.0f uA, both PRINTED; TI prints no minimum for its own pull-up) against VIH %.1f V of both; driven dominant, the controller sinks" % (
        F["b_ii"] * 1e6, F["tx_vih"]))
    w("     %.3f mA more and stays under %.1f V (Table 158) against VIL %.1f V of both" % (L["tx_pu_i"] * 1e3, F["vol"], F["tx_vil"]))
    w("   the dark cases: a dark TARGET's gate takes at most %.0f uA per input from a voter (Ioff PRINTED, 5.5 V), its transceiver's TXD at most" % (
        F["g_ioff"] * 1e6))
    w("     %.1f uA (ILKG(OFF) PRINTED), and it cannot drive its fabric (its transceiver's VCC is its own rail); its unpowered buffer's output" % (
        F["tx_off"] * 1e6))
    w("     takes at most %.0f uA (IOFF PRINTED), so its readers read at least %.4f V, RECESSIVE (0.7 VDD = %.4f V at their lowest rail): a dark" % (
        F["b_ioff"] * 1e6, L["dark_read"], F["vih_k"] * vdd_lo))
    w("     controller is defined at its readers. A dark VOTER's input reads low through 10 kOhm; a dark READER's pin sees at most %.4f V," % vdd_hi)
    w("     inside the FT pins' unpowered 4.0 V (STM32H743-COMPATIBILITY.md section 4, DS12110's absolute maximum and Table 120's note 3)")
    i_lim = 2 * vdd_hi / (10e3 * 0.99)                 # the two limiters' 10 kOhm 1 % pull-ups, removed (round 6 counted them at OUTB low)
    i_rpu = vdd_hi / (riso_lo + F["rpu"][0])           # one reading pin's pull-up while the TXD it reads is dominant
    L["rail"] = F["i_r6"] - i_lim + 2 * F["g_icc"] + 2 * F["b_icc"] + 2 * L["tx_pu_i"] + 4 * i_rpu + max(2 * L["vote_i"], 2 * F["g_dicc"])
    w("   the controller's own rail: round 6's bounded state %.4f A less its limiters' pull-ups %.3f mA, plus its two gates' and two buffers' ICC" % (
        F["i_r6"], i_lim * 1e3))
    w("     (%.0f uA and %.0f uA each, PRINTED), its two TXD pull-ups %.3f mA each while dominant, its four readings' pull-ups %.3f mA each while" % (
        F["g_icc"] * 1e6, F["b_icc"] * 1e6, L["tx_pu_i"] * 1e3, i_rpu * 1e3))
    w("     dominant, and the larger of two of its votes asserted at %.3f mA each (one peer contained on both fabrics) and its own gate's two" % (
        L["vote_i"] * 1e3))
    w("     inputs high from the peers' lower rails (the self-test's V phase on it: delta ICC %.0f uA an input at VCC - 0.6 V, PRINTED, taken" % (
        F["g_dicc"] * 1e6))
    w("     per input), all at once: at most %.4f A (MODEL; a labelled scenario for the coordinator's C-DEV, no case row changed here)" % L["rail"])
    w("   all levels hold: %s" % ("yes" if lv_ok else "NO"))
    w("")
    # ---------------------------------------------------------------- 7. the self-test, RESTATED (round 9, W143, on W139's analysis)
    import math
    Q = canq()
    QC = Q["cfg"]
    T_W = F["window"]
    if abs(QC["window_us"] * 1e-6 - T_W) > 1e-12:
        refuse("l9t5_canq.py's window is not FW-B22's")
    ppm = F["xtal_ppm"]
    t_cycle = CYCLE_R * EVERY * T_W * (1 + ppm)
    t_det = CONFIRM * (t_cycle + T_W * (1 + ppm))
    t_cycle7 = CYCLE_7 * EVERY * T_W * (1 + ppm)
    t_det7 = CONFIRM * (t_cycle7 + T_W * (1 + ppm))
    t_on = F["tr00"] + F["g_tpd"] + F["tmode"][1]
    t_off = rsd_hi * C_SD_PF * 1e-12 * math.log(vdd_hi / F["sd_vil"]) + F["tmode"][1]
    slew = F["tr00"] / (0.8 * vdd_hi)                  # Table 160's tr is a 10 to 90 % time at 50 pF (C_VOTE_PF, ASSUMPTION, held to it)
    tau_obs = riso_hi * C_OBS_PF * 1e-12
    drift = 2 * ppm * T_W
    h0, h1 = (x * 1e-6 for x in QC["hold_us"])
    probes = sorted(x * 1e-6 for x in QC["probe_us"].values())
    slot_end = max(QC["slot_us"].values()) * 1e-6 + QC["slot_len_us"] * 1e-6
    slot_first = min(QC["slot_us"].values()) * 1e-6
    frame = QC["frame_bits"] / QC["rate"]
    chain = Q["chain_ms"] * 1e-3
    align = ALIGN_MS * 1e-3
    margins = [("the hold opens after the last state slot closes", h0 - slot_end),
               ("V's votes act before the first peer test frame (the strike chain from the malformed frame at the hold's start)", probes[0] - (h0 + chain)),
               ("S's own request acts before the first peer test frame", probes[0] - (h0 + t_on)),
               ("the last test frame ends before the hold closes", h1 - (probes[-1] + frame) - max(t_on, t_off)),
               ("the release is complete before the next window's first state slot", T_W + slot_first - (h1 + t_off))]
    margins = [(lab, v - align - drift) for lab, v in margins]
    margin = min(v for _l, v in margins)
    tec_up = 2 * 8                                     # S: its test frame attempted while silenced; V: its malformed frame, its only frame there
    tec_down = CYCLE_R + (CYCLE_R - 2)                 # its state frame in every window, its test frame in the ten that are not its S or V
    tec_w139 = 3 * 8                                   # the wording of round 8 read with the test frame also attempted in V (finding W143-F1)
    runs_r = phases_run("restated", literal=True)
    runs_wm = phases_run("w137", literal=False)
    runs_wl = phases_run("w137", literal=True)
    runs_d = phases_run("restated", literal=True, down=("A",))
    runs_d7 = phases_run("w137", literal=False, down=("A",))
    every_r = all(runs_r[(t, f, p)] == N_CYCLES for t in TAGS for f in "AB" for p in PHASE_CODES)
    s_lit = sum(runs_wl[(t, f, "S")] for t in TAGS for f in "AB")
    deg_ok = (all(runs_d[(t, "B", p)] == N_CYCLES for t in TAGS for p in PHASE_CODES) and not any(runs_d[(t, "A", p)] for t in TAGS for p in PHASE_CODES))
    deg7 = sum(runs_d7.values())
    st_ok = (margin > 0 and slew < F["g_slew"] and C_VOTE_PF <= 50.0 and t_det < 10.0 and tec_down > tec_up and every_r and deg_ok
             and Q["sim_s"] <= t_det and Q["degraded_s"] <= t_det)
    w("7. THE VOTE PATH'S IN-SERVICE SELF-TEST, RESTATED IN ROUND 9 (W143, on W139's analysis in T10-CANQ.md; specified for the firmware stage,")
    w("   its contract text in apply_hw_fw_contract_canq.py; nothing applied). Round 7's schedule is SUPERSEDED: its precondition read as worded")
    w("   never runs an S phase (W139-F5), its V phase commands the votes so the attribution path is never exercised (W139-F8), and it stops")
    w("   testing whenever one fabric is down. The restated schedule is W139's (W139-D1 to D3), with its words made exact here:")
    w("   THE WINDOW (%.0f ms on each fabric, FW-B22 restated): the state slots A %.0f, B %.0f and C %.0f ms, %.0f ms each, are never touched by the test;" % (
        T_W * 1e3, QC["slot_us"]["A"] / 1e3, QC["slot_us"]["B"] / 1e3, QC["slot_us"]["C"] / 1e3, QC["slot_len_us"] / 1e3))
    w("     the test acts only in its own segment, the hold %.0f to %.0f ms, where each controller sends one test frame (A at %.0f, B at %.0f, C at %.0f ms)" % (
        h0 * 1e3, h1 * 1e3, QC["probe_us"]["A"] / 1e3, QC["probe_us"]["B"] / 1e3, QC["probe_us"]["C"] / 1e3))
    w("   THE CYCLE (%d windows): in window n the target on fabric A is A, B or C by (n mod %d) div 4 and on fabric B the next controller, and" % (CYCLE_R, CYCLE_R))
    w("     the phase is S, P1, P2 or V by n mod 4; both fabrics are tested at once, so each of the six transceivers meets each phase once a cycle:")
    import textwrap
    for code, how, want in PHASES_R:
        for i, ln in enumerate(textwrap.wrap("%s -> %s" % (how, want), 108)):
            w("     %-2s %s" % (code if i == 0 else "", ln))
    w("   THE PRECONDITION, per fabric (as worded, and run here literally): in the previous window every controller received every other")
    w("     controller's STATE frame on that fabric, no controller has stopped it (FW-B21), no vote on it is asserted outside the test, and")
    w("     all three controllers are functional; else that fabric's phase is skipped and every controller's published phase counter shows the")
    w("     skip. The state frames lie outside the hold, so no phase can fail the next window's precondition: the S phase runs as worded")
    w("   THE PHASES RUN, fault-free, over %d cycles (per transceiver and phase; MODEL of the schedule, no figure from a sheet):" % N_CYCLES)
    w("     restated schedule, precondition as worded:            every phase of every transceiver %d times: %s" % (N_CYCLES, "yes" if every_r else "NO"))
    w("     round 7's schedule, its precondition as W137 meant it: every phase %d times: %s" % (N_CYCLES, "yes" if all(
        runs_wm[(t, f, p)] == N_CYCLES for t in TAGS for f in "AB" for p in PHASE_CODES) else "NO"))
    w("     round 7's schedule, its precondition as worded:       S phases run %d times (the window after its V phase fails it): MUTANT, FAILS" % s_lit)
    w("     DEGRADED, fabric A down at every controller: the restated schedule runs every fabric B phase %d times and no fabric A phase: %s;" % (
        N_CYCLES, "yes" if deg_ok else "NO"))
    w("       round 7's runs %d phases (its precondition needs both fabrics)" % deg7)
    w("   TIMING on printed figures and the drafted rows (each margin less the window clocks' alignment %.1f ms, DRAFTED, and two crystals'" % ALIGN_MS)
    w("     drift over a window %.1f us):" % (drift * 1e6))
    for lab, v in margins:
        w("     %-112s %7.3f ms" % (lab, v * 1e3))
    w("     silence takes effect within %.3f us of the second vote or the own request: the GPIO edge %.1f ns (speed 00 at 50 pF, DS12110 Table 160" % (
        t_on * 1e6, F["tr00"] * 1e9))
    w("       PRINTED) + the gate's %.1f ns (tpd at 3.3 V +- 0.3 V, -40 to 85 C, PRINTED) + tMODE %.0f us (PRINTED maximum); it ends within %.2f us" % (
        F["g_tpd"] * 1e9, F["tmode"][1] * 1e6, t_off * 1e6))
    w("       of the release: SD's %.0f kOhm against %.0f pF (ASSUMPTION: TI prints no SHDN capacitance; the two diodes' CT %.0f pF each PRINTED)" % (
        rsd_hi / 1e3, C_SD_PF, F["ct"] * 1e12))
    w("       down to VIL, + tMODE; V's strike: %.3f ms from the malformed frame to the target's driver off (l9t5_canq.out section 4, MODEL on" % (chain * 1e3))
    w("       PRINTED parts); the vote line's edge %.2f ns/V against the gate's %.0f ns/V limit at 50 pF (C_VOTE %.0f pF, a Layer 10 bound: Ci %.0f pF" % (
        slew * 1e9, F["g_slew"] * 1e9, C_VOTE_PF, F["g_ci"] * 1e12))
    w("       and CIO %.0f pF PRINTED); a reader's copy of a TXD edge in about %.0f ns (%.1f kOhm against %.0f pF: ASSUMPTION, a Layer 10 bound)" % (
        F["cio"] * 1e12, tau_obs * 1e9 * 2.2, riso / 1e3, C_OBS_PF))
    w("   THE INTERVAL: one cycle is %d windows x %.0f ms = %.4f s; a latent fault of the vote path is exercised within one cycle, judged at its" % (
        CYCLE_R, T_W * 1e3, t_cycle))
    w("     window's end, declared when %d consecutive runs of that phase fail (one corrupted frame never declares one), the verdict exchanged in" % CONFIRM)
    w("     the next window: DETECTED WITHIN %.2f s of its onset (MODEL on the printed timing and the DRAFTED %.0f ms window; round 7's %.2f s)" % (
        t_det, T_W * 1e3, t_det7))
    w("     W139's event model of this schedule finds the latest declaration at %.2f s and, DEGRADED, a fabric B vote stuck low at %.2f s, both" % (
        Q["sim_s"], Q["degraded_s"]))
    w("     within it (l9t5_canq.out section 7); a dead attribution path at %.2f s (round 7's: NOT FOUND); round 7's precondition as worded: an open" % Q["att_s"])
    w("     own-request diode %s" % Q["literal"])
    w("   DEGRADED: with one fabric down its phases wait (they need its state frames) and the other fabric's run at the same interval, so every")
    w("     element of the surviving fabric keeps the %.2f s bound; the down fabric's elements are tested again within %.2f s of its return to" % (t_det, t_det))
    w("     service, which FW-B21's probe brings within %.3f s of a repair (l9t5_canq.out section 8); while a controller is out the test waits" % Q["fabric_s"])
    w("     (V needs both peers) and the bound restarts when the quorum is whole")
    w("   THE ERROR COUNT: per cycle and fabric a target loses two frames, +%d (S: its test frame; V: its malformed frame, its only frame in that" % tec_up)
    w("     hold), against at least %d successes (its %d state frames and its test frame in the other %d windows): bounded and error-active" % (
        tec_down, CYCLE_R, CYCLE_R - 2))
    w("     (+8 and -1 are ISO 11898-1's, which is not held: ASSUMPTION). Read with its test frame also sent in V, round 8's wording gives +%d" % tec_w139)
    w("     against the same %d and the count rises a cycle (finding W143-F1): the V phase's malformed frame is the target's only frame there" % tec_down)
    w("   DAR = 1 (L9T5-D2, W139-D8), so each failed attempt is one +8, with ES0392 Rev %s %s's printed workaround (%s):" % (
        F["es_rev"], F["es_item"], F["es_page"]))
    for ln in textwrap.wrap("\"%s\"" % F["es_work"], 120):
        w("     %s" % ln)
    w("     (W137-F1 answered; the compatibility page's row \"%s\" is Layer 6's to restate, W139-F1)" % F["dar_compat"])
    w("   THE RESTART ROUTE'S PHASES (record l4canen, apply_gen_sch_b_canen.py): in the windows of the fabric A target X, P1 and P2 pulse one")
    w("     peer's restart vote on X for 4 ms and V both peers', X reading its restart gate's output; they need only one fabric for the verdict,")
    w("     so they keep this interval with either fabric down")
    w("   timing and cost hold: %s" % ("yes" if st_ok else "NO"))
    # the self-test's own faults, element by element, and its coverage of the netlist
    rows = [("a vote output, its line or its gate input", "stuck low or open", "the target cannot be silenced by the vote", "V fails", "T"),
            ("a vote output, its line or its gate input", "stuck high", "the other peer alone silences the target", "the other peer's P fails", "T"),
            ("a vote pull-down (10 kOhm)", "short", "as its vote stuck low", "V fails", "T"),
            ("a vote pull-down (10 kOhm)", "open", "the input floats only while its voter is in reset or dark", "NOT in service: RESIDUAL", "-"),
            ("the 2-of-2 gate", "output stuck low", "the target cannot be silenced by the vote", "V fails", "T"),
            ("the 2-of-2 gate", "output stuck high", "the target silenced on that fabric at once (IOHA row 7)", "its frames absent", "W"),
            ("the gate's 100 nF", "short", "the target's own rail shorted: the target dark (IOHA row 3)", "its frames absent", "W"),
            ("the vote diode", "open", "the target cannot be silenced by the vote", "V fails", "T"),
            ("the vote diode", "short", "the gate's low holds SD: the target's own request fails", "S fails", "T"),
            ("the own-request diode", "open", "the target's own request fails", "S fails", "T"),
            ("the own-request diode", "short", "the request pin's low holds SD: the vote fails", "V fails", "T"),
            ("SD's 100 kOhm", "open", "SD rests on the pin's internal pull-down (TI: a fall-back)", "NOT in service: RESIDUAL", "-"),
            ("the transceiver's SHDN input", "ignored", "neither the request nor the vote silences", "S and V fail", "T"),
            ("a reader's attribution path", "dead", "it never strikes the target, so no vote follows a deviation", "V fails (V runs it end to end)", "T"),
            ("an isolation resistor", "open", "its reader sees no TXD edge while the frames arrive", "continuous reading", "C"),
            ("an isolation resistor", "short", "a faulty reader could move the buffer's output (not the TXD)", "NOT in service: RESIDUAL", "-"),
            ("a reading pin or its input stage", "stuck", "the two readers of one TXD disagree", "continuous reading", "C"),
            ("a TXD buffer", "stuck or open", "its readers see no edge while its frames arrive", "continuous reading", "C"),
            ("the buffer's 100 nF", "short", "the target's own rail shorted: the target dark (IOHA row 3)", "its frames absent", "W"),
            ("a TXD pull-up (10 kOhm)", "short", "the TXD held recessive: no frame on that fabric (IOHA row 7)", "its frames absent", "W"),
            ("a TXD pull-up (10 kOhm)", "open", "the TXD on TI's own pull-up only while its controller resets", "NOT in service: RESIDUAL", "-"),
            ("a node's test schedule", "stalled or out of turn", "phases fail or counters disagree", "the published phase counter", "W"),
            ("a node's verdict", "wrong (two-faced or corrupted)", "outvoted: verdicts are taken 2 of 3", "the confirmation", "T")]
    when = {"T": "within %.2f s" % t_det, "W": "within one window (%.0f ms)" % (T_W * 1e3),
            "C": "within %d windows (%.0f ms): every window carries a frame of each controller on each fabric" % (CONFIRM + 1, (CONFIRM + 1) * T_W * 1e3), "-": "none"}
    w("   THE SELF-TEST'S OWN FAULTS, element by element (per transceiver; the residuals are named, none defeats the containment alone):")
    for el, fl, eff, det, tt in rows:
        w("     %-42s %-30s %-62s %-30s %s" % (el, fl, eff, det, when[tt]))
    # coverage: every part the draft draws or re-uses in the vote and observation paths is the subject of a row above
    nl1 = R["nl1"]
    kinds = {"gate": ("U", "SN74LVC1G08"), "pd": ("R", "10k"), "iso": ("R", M.R_ISO), "vdiode": ("D", "1N4148W: the peers'"),
             "odiode": ("D", "1N4148W: controller"), "sdpd": ("R", "100k"), "cdec": ("C", "100n"), "buf": ("U", M.BUF), "cbuf": ("C", "100n"),
             "txpu": ("R", M.R_TXPU)}
    covered = {"gate": "the 2-of-2 gate", "pd": "a vote pull-down (10 kOhm)", "iso": "an isolation resistor", "vdiode": "the vote diode",
               "odiode": "the own-request diode", "sdpd": "SD's 100 kOhm", "cdec": "the gate's 100 nF", "buf": "a TXD buffer",
               "cbuf": "the buffer's 100 nF", "txpu": "a TXD pull-up (10 kOhm)"}
    path = []
    for k, t in enumerate(TAGS):
        for j in range(2):
            path += [("U%d" % (47 + j + 10 * k), "gate"), ("R%d" % (604 + 20 * k + 4 * j), "pd"), ("R%d" % (605 + 20 * k + 4 * j), "pd"),
                     ("R%d" % (611 + 20 * k + 2 * j), "iso"), ("R%d" % (612 + 20 * k + 2 * j), "iso"), ("D%d" % (401 + 10 * k + 2 * j), "vdiode"),
                     ("D%d" % (400 + 10 * k + 2 * j), "odiode"), ("R%d" % (603 + 20 * k + 4 * j), "sdpd"), ("C%d" % (944 + 10 * k + 2 * j), "cdec"),
                     ("U%d" % (580 + 2 * k + j), "buf"), ("C%d" % (943 + 10 * k + 2 * j), "cbuf"), ("R%d" % (606 + 20 * k + 4 * j), "txpu")]
    cov_ok = all(nl1["comps"].get(r, {}).get("value", "").startswith(kinds[kd][1]) and any(row[0] == covered[kd] for row in rows) for r, kd in path)
    cov_ok &= set(r for r, _k in path) >= set(R["added"]) and set(R["retyped"]) - {mcu(k) for k in range(3)} <= set(r for r, _k in path)
    att_ok = any(row[0] == "a reader's attribution path" and row[4] == "T" for row in rows) and any(c == "V" and "attribution" in h for c, h, _w in PHASES_R)
    w("   coverage: every one of the %d parts of the six vote and six observation paths (gates, pull-downs, both diodes, SD's resistor, buffers," % len(path))
    w("     TXD pull-ups, isolation resistors, the capacitors) is the subject of a row, and every part canmb adds or re-uses is among them: %s;" % (
        "yes" if cov_ok else "NO"))
    w("     the attribution path is a row and the V phase runs it: %s" % ("yes" if att_ok else "NO"))
    w("   the residuals, each needing further faults (W139's rows Q1 to Q4 run each with the fault that makes it act): an open vote pull-down")
    w("     acts only while its voter is in reset or dark AND the other peer votes wrongly; a shorted isolation resistor matters only when its")
    w("     reader also drives its input, and then reaches the buffer's output, never the TXD; an open SD resistor leaves the transceiver on TI's")
    w("     internal pull-down; an open TXD pull-up leaves the TXD on TI's own pull-up only while its controller resets, and a resetting")
    w("     controller that drives dominant is then contained by the vote; a voter that resets while asserting gives the gate a slow edge (10")
    w("     kOhm against the line) outside the gate's %.0f ns/V limit: the output may chatter for that edge, and only while the other peer" % (F["g_slew"] * 1e9))
    w("     asserts, so it can only end a silence early")
    w("")
    # ---------------------------------------------------------------- 8. disposition
    w("8. WHAT THESE ROUNDS CLOSE ONCE INDEPENDENTLY CHECKED, AND WHAT STAYS OPEN (a draft: nothing is closed by its author)")
    w("   L4A-54 (round 7, W137): the circuit of M-B drafted and composed (section 3), read by pin with failing mutations (section 4), the pin")
    w("     plan recounted and read against the makers' tables (section 5), the levels on printed rows (section 6). Round 9 (W143, on W139's")
    w("     L4A-55): the self-test restated (section 7: every phase runs as worded, the attribution path tested, the surviving fabric tested")
    w("     with one down, interval %.2f s); FW-B21's stop at the loss count and FW-B22's text in apply_hw_fw_contract_canq.py; the latched" % t_det)
    w("     supervisor's EN route and the composition with W138's regulator stage in record l4canen. CON-004, IOHA row 7 and test A7 are kept")
    w("     as accepted: %s" % ("yes" if R["cv"] == "HOLDS" else "NO"))
    w("   once independently checked it would answer, for the circuit's part: HO-C's undrafted \"2-of-2 peer observation and vote\" and the")
    w("     share half of HO-D (the limiter, and so its latent stuck comparator, is removed; the vote path's latent faults carry the interval")
    w("     above). The limiter's half of HO-D, RE-6, RE-7 and HO-E stay with L4A-56 to L4A-59 (W138's stage; record l4canen reads its EN route)")
    w("   OPEN: the independent check of M-B with W139's analysis and these corrections (L4A-62); FW-B20 to FW-B22, V-B20 to V-B23 and IOHA")
    w("     section 12 restated (L4A-61); the compatibility page's DAR row (W139-F1, Layer 6). cx46's item 5 stays NOT CLOSED, CON-004's quorum")
    w("     service OPEN, FW-B22 PROVISIONAL and L9T5-F21 OPEN until that check reads them")
    w("")
    # ---------------------------------------------------------------- 9. predicates
    pred["the composition: every draft of board B's change list applies in order with canmb after iocguard and the generator runs to its end"] = R["ok1"] and R["n_seq"] == 19
    pred["CON-004 holds on the regenerated netlist with canmb (three supply branches, two fabrics, termination, A7's links), as before it"] = R["cv"] == "HOLDS" and R["cv0"] == "HOLDS"
    pred["the draft reads DRAWN by pin (observations, votes, gates on the targets' rails, the limiter gone, the rail trips kept)"] = R["mv"] == "DRAWN"
    pred["every mutation FAILS: a removed fabric, a vote off its SHDN, a reader of its own TXD, a 1-of-1 vote, a gate on a peer's rail, no isolation, no buffer"] = (
        len(R["muts"]) == 7 and all(v == "FAIL" for _l, v, _b in R["muts"]))
    pred["the draft refuses a generator without iocguard, a second application and the tree's generator (NOT RELEASED)"] = all(R["refused"])
    pred["the pin plan: each new pin free before, a Table 9 I/O row, the reading pins TIM3_CH1 to CH4 at AF2 with DMA requests, no debug pin"] = R["plan_ok"] and R["tim3"]
    pred["the count: the tree reproduces CON-017's 30/14/56; with canmb 40 of 100, 14 supplies, 46 unconnected on each controller"] = (
        R["cnt_t"][:3] == tuple(int(x) for x in c17.groups()) and all(R["cnt1"][t][:3] == (R["cnt0"][t][0] + 8, 14, R["cnt0"][t][2] - 8) for t in TAGS)
        and R["cnt1"]["A"][:3] == (40, 14, 46))
    want_kept = {r for k in range(3) for j in range(2) for r in ("U%d" % (47 + j + 10 * k), "D%d" % (401 + 10 * k + 2 * j), "R%d" % (604 + 20 * k + 4 * j),
                 "R%d" % (605 + 20 * k + 4 * j), "R%d" % (606 + 20 * k + 4 * j), "C%d" % (943 + 10 * k + 2 * j), "C%d" % (944 + 10 * k + 2 * j))} | {mcu(k) for k in range(3)}
    pred["the parts: eighteen added (twelve isolation resistors, six buffers), none removed, the limiter's 42 places re-used, the three controllers' new pins"] = (
        len(R["added"]) == 18 and not R["removed"] and set(R["retyped"]) == want_kept)
    pred["the levels hold on the printed rows (the vote, SHDN, the observation, a faulty reader, the rails inside the gate's row)"] = lv_ok
    pred["the self-test RESTATED (round 9): every phase of every transceiver runs once a cycle as worded, the margins hold, the edge rate, the error count bounded"] = st_ok
    pred["the self-test's interval bounded under 10 s (W139's simulation within it), every part of the vote paths has a fault row, the attribution path tested, the residuals named"] = (
        cov_ok and att_ok and t_det < 10.0)
    pred["the mutant FAILS: round 7's schedule with its precondition as worded runs no S phase; with fabric A down it runs no phase at all"] = s_lit == 0 and deg7 == 0
    pred["nothing closes here: cx46's item 5, CON-004's quorum service, FW-B22 and L9T5-F21 keep their states for the check"] = True
    w("9. THE PREDICATES (v2/ecad/tools/tests/test_l9t5_canmb.py holds them)")
    for k_, v in pred.items():
        w("   %s: %s" % (k_, "yes" if v else "NO"))
    sys.stdout.write("\n".join(out) + "\n")
    return 0 if all(pred.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
