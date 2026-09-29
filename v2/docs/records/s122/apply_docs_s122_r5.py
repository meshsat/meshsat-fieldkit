#!/usr/bin/env python3
"""Stream s122, round 5 (S-122, MESHSAT-1357, 29 September 2026): the answer to the independent check of fnd/s122c at
edead832 (`checks/check-s122-4.md`: B1, m1 to m3).

B1 found two parts named in roles the netlists no longer give them, both judged TRUE because round 4's judgement asked
only whether a part number is on the board: V2-SPEC.md line 84 called the TPS22810 D8's gate-bias switch (board D's
gate bias is `U15`, a TLV75801 LDO enabled by `PA_KEY`, since `faf8c981`; the TPS22810 is `U21`, the load switch of the
exciter's `+5V_TX`), and line 81 gave all three slot rails and the device rail to the AP64500 (board A's `U4` and `U6`
are AP64500, `U5` and `U7` LM5176 stages; all four were AP64500 at `b2709118`). `verdicts.check_roles` now judges a part
named in a role against the designators whose values state that role, and this script corrects both rows, with the two
minors of the same table: line 86's magnetometer (board E carries none; `gen_sch_e.py` puts it in the outside pod,
reached through `J_POD`) and line 83's sixteen LEDs (board C carries seventeen, `D22` the seventeenth). V2-SPEC.md
records the four as correction 35.
Every part, pin, value and generator text the new text names is asserted first (the assertion language of
`verdicts.py`); every old passage is found once and every new one reads back once; no dash; the document re-parses.
Refuses a second run. Run: python3 apply_docs_s122_r5.py [--check]."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

TAG = "apply_docs_s122_r5"
SPC = "v2/docs/V2-SPEC.md"
DOCS = {SPC: "75bc0742812bbb7d"}
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "c9f7394594201045", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}

ASSERT = {
    "line 84": ["D:U15~TLV75801", "D:U15~PA gate bias", "D:U15.4=PA_KEY", "D:U21~TPS22810DRV load switch, +5V_TX",
                "D:#val~TPS22810=1", "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~PA gate bias switched by a TPS22810 on PA_KEY",
                "DOC@faf8c981:v2/ecad/tools/gen_sch_d.py~TLV75801", "DOC@faf8c981^:v2/ecad/tools/gen_sch_d.py!~TLV75801"],
    "line 81": ["A:U4~AP64500", "A:U4~+5V_S1", "A:U6~AP64500", "A:U6~+5V_S3", "A:U5~LM5176", "A:U5~+5V_S2", "A:U7~LM5176",
                "A:U7~+5V_DEV", "A:U8~INA226 rail monitor +5V_S1", "A:U9~INA226 rail monitor +5V_S2",
                "A:U10~INA226 rail monitor +5V_S3", "A:U11~INA226 rail monitor +5V_DEV",
                "DOC@b2709118:v2/ecad/tools/gen_sch_a.py~SLOT RAIL S2: AP64500 5.1 V",
                'DOC@b2709118:v2/ecad/tools/gen_sch_a.py~buck5("D", "U7", "DEV_EN", "+5V_DEV"'],
    "line 83": ["C:#fp~LED_D3.0mm=17", "C:D22~EMCON", "REG:S-44.status=OPEN",
                "DOC:v2/docs/V2-SPEC.md~since board C's round 8, a seventeenth, the amber hardware EMCON lamp"],
    "line 86": ["E:U14~BME688", "E:U15~BMI270", "E:!~magnetometer", "E:!~LIS3MDL", "E:J_POD?", "E:J_POD~",
                "DOC:v2/ecad/tools/gen_sch_e.py~the magnetometer sits in the outside pod (32.57)"],
}
ASSERT["line 86"] = [a for a in ASSERT["line 86"] if a != "E:J_POD~"] + ["E:SDA1>J_POD,U14,U15"]

S84_OLD = "the TPS22810 gate-bias switch, a PCA9555 |"
S84_NEW = ("the TLV75801 gate-bias LDO on `PA_KEY` (`U15`; on 7 September a TPS22810 switched the bias, correction 35), the "
           "TPS22810 load switch of the exciter's `+5V_TX` (`U21`), a PCA9555 |")
S81_OLD = "three 5.1 V slot rails and a device rail (AP64500, INA226 monitored),"
S81_NEW = ("three 5.1 V slot rails and a device rail (the AP64500 buck on slots 1 and 3, `U4` and `U6`, and LM5176 stages "
           "on slot 2 and the device rail, `U5` and `U7`, all four AP64500 on 7 September, correction 35; INA226 monitored),")
S83_OLD = "sixteen LEDs under light guides, two PCA9555,"
S83_NEW = ("seventeen 3 mm LEDs under light guides (`D1` to `D16` and, since board C's round 8, the hardware EMCON lamp "
           "`D22`, whose guide in the plate is owed, open item S-44; correction 35), two PCA9555,")
S86_OLD = "the sensor controller with the BME688, BMI270 and magnetometer,"
S86_NEW = ("the sensor controller with the BME688 and BMI270 (`U14`, `U15`; the magnetometer is in the outside pod, reached "
           "through `J_POD`, correction 35),")
C34_END = ("    today: line 82's DS3231M, now board B's DS3231SN `U9`, and line 84's TUSB2046B, now board D's TUSB2046I `U4`\n"
           "    (TUSB2046IBVFR, since 26 September 2026). Nothing is built.\n")
C35 = ("\n35. **Parts in their roles (lines 81, 83, 84 and 86).** Session reading of stream s122, round 5 (29 September\n"
       "    2026, MESHSAT-1357, open item S-122; its independent check, `v2/docs/records/s122/checks/check-s122-4.md`,\n"
       "    B1 and m2, m3), whose judgement asks since that round that a part named in a role hold that role on its board.\n"
       "    Line 84 called the TPS22810 the gate-bias switch: board D's gate bias is `U15`, a TLV75801 LDO enabled by\n"
       "    `PA_KEY`, since `faf8c981`, and its TPS22810 is `U21`, the load switch of the exciter's `+5V_TX`; on 7\n"
       "    September (`b2709118`) a TPS22810 switched the bias. Line 81 gave the three slot rails and the device rail to\n"
       "    the AP64500: board A's `U4` and `U6` are AP64500 bucks for slots 1 and 3, and `U5` and `U7` are LM5176 stages\n"
       "    for slot 2 and the device rail; all four were AP64500 at `b2709118`. Line 86 put a magnetometer on the sensor\n"
       "    controller; board E carries the BME688 `U14` and the BMI270 `U15`, and `gen_sch_e.py` puts the magnetometer in\n"
       "    the outside pod, reached through `J_POD`. Line 83 counted sixteen LEDs; board C carries seventeen, `D22` the\n"
       "    seventeenth. Nothing is built.\n")
EDITS = [(SPC, S84_OLD, S84_NEW, "line 84"), (SPC, S81_OLD, S81_NEW, "line 81"), (SPC, S83_OLD, S83_NEW, "line 83"),
         (SPC, S86_OLD, S86_NEW, "line 86"), (SPC, C34_END, C34_END + C35, "correction 35")]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    raise SystemExit(2)


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    nls = L.netlists()
    for b, s in NETS.items():
        if nls[b]["sha16"] != s: refuse("board %s's netlist is %s, not set 14's %s" % (b, nls[b]["sha16"], s))
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    n = 0
    for what, al in ASSERT.items():
        for a in al:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (what, msg))
            n += 1
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    for rel, old, new, why in EDITS:
        if any(d in new for d in L.DASHES): refuse("%s: a dash in the new text" % why)
        if texts[rel].count(old) != 1: refuse("%s: the old passage is found %d times" % (why, texts[rel].count(old)))
        texts[rel] = texts[rel].replace(old, new)
    for rel, old, new, why in EDITS:
        if texts[rel].count(new) != 1: refuse("%s: the new passage does not read back once" % why)
    if check:
        print("%s: --check at %s: %d edits located, %d assertions hold; nothing written" % (TAG, head, len(EDITS), n))
        return 0
    for rel, txt in texts.items():
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(txt)
        L.md_blocks(rel)
    print("%s: at %s %d edits written, %d assertions held first; %s" % (
        TAG, head, len(EDITS), n, ", ".join("%s to %s" % (os.path.basename(r), L.sha16(r)) for r in DOCS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
