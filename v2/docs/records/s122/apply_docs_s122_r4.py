#!/usr/bin/env python3
"""Stream s122, round 4 (S-122, MESHSAT-1357, 29 September 2026): the answer to integration set 14's checks of S-122
(`v2/docs/records/int15/checks/check-int15-1.md` to `-3.md`, and the fourth check of set 14, q1 to q4) and to
check-s122-3's minors.

Since this round `s122lib.partnos` reads makers' part numbers by their shape, and `verdicts.py` judges each against the
part values of the six netlists. Its re-run found these sentences naming parts no generator carries, or not on the
board they name, or no longer carried, and this script corrects them:
  * V2-SPEC.md line 82 (B16 row): the TMDS341A display switch (no generator has carried one; board B's `U3` and `U4`
    are TS3DV642A0RUAR, as `gen_sch_b.py` was at `b2709118`, the commit that wrote the table), and the DS3231M clock
    (true on 7 September at `b2709118`; board B's `U9` is the DS3231SN);
  * line 84 (D8 row): the TUSB2046B hub (true on 7 September; board D's `U4` is the TUSB2046IBVFR, the industrial grade,
    since 26 September 2026, W6-F5);
  * line 86 (E6 row): the LM5176 front end on E6 (false on its date: at `b2709118` board E's generator carried the
    LM5069 hot swap and sent the bus up to A22's LM5176 front end; today E's `U6` and A's `U2`);
  * line 47 (APRS row): the WM8960 codec (it left `gen_sch_d.py` with the D8 generators at `bdfc7b3f`; D8's codec is the
    PCM2912A `U6`) and
    the RA30H1317M1's sheet called owed (held under `v2/vendor/mitsubishi/` and a row of OPERATING-ENVELOPE.md section 2
    since 27 September 2026);
  * V2-SPEC.md correction 34 records the four lines;
  * OPERATING-ENVELOPE.md line 77: the TRACO TEN 40-2412WIN row (no netlist carries a TRACO part; `gen_sch_e.py` says
    the TRACO converter of E4 is gone), replaced by board E's input part, the LM5069 `U6`, with TI's recommended
    junction range read from the held sheet (`ti/ti-lm5069.pdf`, SNVS452G 7.3); line 83: the Amphenol M.2 B-key socket
    (MDT420B01001, on no netlist), replaced by board B's TE 2199119-3 `J_M2C2` with TE's service temperature read from
    the held brochure (`m2/te-2199119-m2-b-key.pdf`); a correction paragraph after the table says so;
  * handover/DEFINITION-STATUS.md: row DC-10, CONOPS.md section 7's D-13 row (check-s122-3 m1: the STM32H753 in the
    schematic, which reads STM32H743VIT6 since `458b2873`), and the dependency row names it;
  * `v2/docs/records/int15/apply_check15c_fixes.py`'s docstring (the fourth check of set 14, q4): its filing note ends
    every filed check, where it said heading.
Every part, pin, value and generator text the new text names is asserted first (the assertion language of
`verdicts.py`, the held sheets read with pdftotext); every old passage is found once and every new one reads back once;
no dash; each document re-parses; CONOPS.md is unchanged. Refuses a second run.
Run: python3 apply_docs_s122_r4.py [--check]."""
import os, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

TAG = "apply_docs_s122_r4"
BASE = "1bafab8c"          # set 14's tip, fnd/int15
SPC = "v2/docs/V2-SPEC.md"
ENV = "v2/docs/OPERATING-ENVELOPE.md"
DST = "v2/docs/handover/DEFINITION-STATUS.md"
C15 = "v2/docs/records/int15/apply_check15c_fixes.py"
DOCS = {SPC: "1e1547e1462904f7", ENV: "a8e65995c594546b", DST: "2db0ad36da754fa4", C15: "e943f723d738c14b"}
CONOPS = ("v2/docs/CONOPS.md", "6cb7b241cb84d729")
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "c9f7394594201045", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}

# ------------------------------------------------------------------ what the new text names, asserted
ASSERT = {
    "the B16 row": ["B:U3~TS3DV642", "B:U4~TS3DV642", "B:U9~DS3231SN", "B:!~TMDS341", "B:!~DS3231M",
                    "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~TS3DV642", "DOC@b2709118:v2/ecad/tools/gen_sch_b.py~DS3231M",
                    "DOC@b2709118:v2/docs/V2-SPEC.md~the TMDS341A display switch"],
    "the D8 row": ["D:U4~TUSB2046IBVFR", "D:!~TUSB2046B", "DOC@b2709118:v2/ecad/tools/gen_sch_d.py~TUSB2046B",
                   "DOC:v2/ecad/tools/gen_sch_d.py~THE HUB'S OWN RAIL (W6-F5, 26 September 2026). The hub is now the industrial TUSB2046IBVFR"],
    "the E6 row": ["E:U6~LM5069", "E:!~LM5176", "A:U2~LM5176", "A:U2~VBUS20 from VIN_RAW",
                   "DOC@b2709118:v2/ecad/tools/gen_sch_e.py~LM5069 hot-swap",
                   "DOC@b2709118:v2/ecad/tools/gen_sch_e.py~into A22's LM5176 front end",
                   "DOC@b2709118:v2/docs/V2-SPEC.md~the LM5176 9 to 36 V front end"],
    "the APRS row": ["D:U6~PCM2912A", "D:!~WM8960", "D:*~RA30H1317M1", "DOC@bdfc7b3f^:v2/ecad/tools/gen_sch_d.py~WM8960",
                     "DOC@bdfc7b3f:v2/ecad/tools/gen_sch_d.py!~WM8960", "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1",
                     "DOC:v2/docs/OPERATING-ENVELOPE.md~| Mitsubishi RA30H1317M1 30 W VHF power amplifier |"],
    "the TRACO row": ["A:!~TRACO", "B:!~TRACO", "C:!~TRACO", "D:!~TRACO", "E:!~TRACO", "P:!~TRACO", "E:U6~LM5069MM-2",
                      "DOC:v2/ecad/tools/gen_sch_e.py~the isolated TRACO converter of E4 is gone",
                      "PDF:v2/vendor/ti/ti-lm5069.pdf~7.3 Recommended Operating Conditions|TJ Junction temperature \u201340 125 °C|SNVS452G"],
    "the B-key row": ["B:J_M2C2~TE 2199119-3", "B:!~MDT420B", "B:J_M2N1~Amphenol MDT420M02001",
                      "PDF:v2/vendor/m2/te-2199119-m2-b-key.pdf~Service Temperature -40 ~ +80|Product Specifications: 108-115042/ 108-115049",
                      "PDF:v2/vendor/m2/amphenol-mdt420b01001-m2-b-key.pdf~Operating Temperature: -40°C to +80°C"],
    "DC-10": ["B:U41~STM32H743VIT6", "B:U51~STM32H743VIT6", "B:U61~STM32H743VIT6", "B@458b2873:U41~STM32H743VIT6",
              "B@68bc9e8f:U41~STM32H753VITx", "REG:CON-017.evidence_result=PASS",
              "REG:CON-017.statement~the STM32H743VIT6 the project buys, in the schematic text, the symbol value and the BOM",
              "DOC@68bc9e8f:v2/docs/CONOPS.md~the component mismatch with the STM32H753 in the schematic closes only when",
              "DOC:v2/docs/V2-SPEC.md~the schematic text of `U41`, `U51` and `U61` reads H743 and CON-017 reads PASS"],
}
# no generator has ever held a TMDS341A (git log -S over every schematic generator)
NEVER = [("TMDS341", "v2/ecad/tools/gen_sch_*.py"), ("MDT420B", "v2/ecad/tools/gen_sch_*.py")]

S_APRS_OLD = ("NiceRF SA868 1 W with a 30 W VHF amplifier stage (RA30H1317M class, T/R relay, low-pass filter; sheet *owed*), "
              "Direwolf on the WM8960 codec, hardware PTT inhibit")
S_APRS_NEW = ("NiceRF SA868 1 W with a 30 W VHF amplifier stage (the Mitsubishi RA30H1317M1, T/R relay, low-pass filter; the "
              "amplifier's sheet held since 27 September 2026, `OPERATING-ENVELOPE.md` section 2), Direwolf on D8's PCM2912A "
              "USB codec (`U6`), hardware PTT inhibit (correction 34)")
S_B16_OLD = "the KSZ9897 Ethernet switch, the TMDS341A display switch, the LimeSDR bay"
S_B16_NEW = ("the KSZ9897 Ethernet switch, the two TS3DV642 display switches (`U3`, `U4`; correction 34), the LimeSDR bay")
S_RTC_OLD = "two E72, the DS3231M clock, the ATECC608B"
S_RTC_NEW = "two E72, the DS3231SN clock (`U9`; the DS3231M on 7 September, correction 34), the ATECC608B"
S_D8_OLD = "the TUSB2046B hub and CP2102N bridge"
S_D8_NEW = ("the TUSB2046I hub (`U4`, TUSB2046IBVFR, the industrial grade since 26 September 2026; the TUSB2046B on 7 "
            "September, correction 34) and CP2102N bridge")
S_E6_OLD = "and the block E5: the LM5176 9 to 36 V front end, the LT8705A solar tracker"
S_E6_NEW = ("and the block E5: the LM5069 hot swap on the 9 to 36 V input (`U6`), which passes the bus up to A22's LM5176 "
            "front end (`U2`; correction 34), the LT8705A solar tracker")
S_C33_END = ("    `feasibility/EMCON.md` section 0a.1 (`handover/DEFINITION-STATUS.md`, row DC-01), which line 24 now cites.\n"
             "    Nothing is built.\n")
S_C34 = ("\n34. **Part numbers (lines 47, 82, 84 and 86).** Session reading of stream s122, round 4 (29 September 2026,\n"
         "    MESHSAT-1357, open item S-122; the integration check of set 14,\n"
         "    `v2/docs/records/int15/checks/check-int15-1.md`, B1), whose inventory reads makers' part numbers since that\n"
         "    round. Line 82 named the TMDS341A display switch, which no schematic generator has carried: `gen_sch_b.py`\n"
         "    carried the TS3DV642 when this table was written (`b2709118`), and board B's display switches are `U3` and\n"
         "    `U4`, TS3DV642A0RUAR. Line 86 put the LM5176 front end on E6; at `b2709118` too board E's generator carried\n"
         "    the LM5069 hot swap and sent the bus up the dock contacts into A22's LM5176 front end, today board E's `U6`\n"
         "    and board A's `U2`. Line 47 named the WM8960 codec, which left `gen_sch_d.py` with the D8 generators at\n"
         "    `bdfc7b3f` (7 September);\n"
         "    D8's codec is the PCM2912A `U6`, and the RA30H1317M1's sheet, which the line called owed, is held (a row of\n"
         "    `OPERATING-ENVELOPE.md` section 2 since 27 September 2026). Two names were true on 7 September and are not\n"
         "    today: line 82's DS3231M, now board B's DS3231SN `U9`, and line 84's TUSB2046B, now board D's TUSB2046I `U4`\n"
         "    (TUSB2046IBVFR, since 26 September 2026). Nothing is built.\n")
E_TRACO_OLD = "| TRACO TEN 40-2412WIN | dock strip, inside | -40 to +75 C | `traco/ten40win_datasheet-3049699.pdf` |"
E_TRACO_NEW = ("| TI LM5069 hot-swap controller on the 9 to 36 V input (board E `U6`) | dock strip, inside | junction -40 to "
               "+125 C (its recommended operating conditions) | `ti/ti-lm5069.pdf` (SNVS452G, 7.3) |")
E_BKEY_OLD = "| Amphenol M.2 B-key socket | inside | -40 to +80 C | `m2/amphenol-mdt420b01001-m2-b-key.pdf` |"
E_BKEY_NEW = ("| TE 2199119-3 M.2 B-key socket (board B `J_M2C2`) | inside | -40 to +80 C (service temperature) | "
              "`m2/te-2199119-m2-b-key.pdf` (Performance Ratings, product specifications 108-115042 and 108-115049) |")
E_NOTE_AT = "\n**TWO OF THE SEVEN OWED RANGES WERE IN THE TREE ALL ALONG (20 September 2026).**"
E_NOTE = ("\n**Corrected 29 September 2026 (stream s122, round 4; the integration check of set 14,\n"
          "`v2/docs/records/int15/checks/check-int15-1.md`, B1):** two rows of the table named parts no generator carries.\n"
          "The TRACO TEN 40-2412WIN row is replaced by board E's input part, the LM5069 `U6` (`gen_sch_e.py` records that\n"
          "the isolated TRACO converter of E4 is gone); its range is the junction range TI's sheet recommends. The Amphenol\n"
          "M.2 B-key socket row (Amphenol's MDT420B01001) is replaced by board B's socket, TE 2199119-3 `J_M2C2`, whose\n"
          "service temperature is the same -40 to +80 C; board B's Amphenol sockets are the M-key MDT420M02001 of the NVMe\n"
          "slots. In that check's words, no envelope number depends on either row.\n")
D_DC10_AT = "the row was written at `68bc9e8f`, before `458b2873` drew it | this row |\n"
D_DC10 = ("| DC-10 | section 7's D-13 row: the STM32H753 in the schematic, the component mismatch with the H743 called open "
          "(check-s122-3 m1) | the three supervisors' schematic text is the H743 the project buys: board B's `U41`, `U51` "
          "and `U61` read STM32H743VIT6 since `458b2873` (STM32H753VITx at `68bc9e8f`, where the row was written), and "
          "CON-017, which asks that text, the BOM and regeneration parity, reads PASS | CON-017 in the registry; "
          "`V2-SPEC.md` correction 32 |\n")
D_DEP_OLD = "the fabric's break-before-make and back-power gating, board A's CC array) |"
D_DEP_NEW = "the fabric's break-before-make and back-power gating, board A's CC array, the supervisors' part of D-13) |"
C15_OLD = "  p5, p6  the records index row's word \"enforced\"; a filing note heading every filed check of int15 and s120."
C15_NEW = ("  p5, p6  the records index row's word \"enforced\"; a filing note ending every filed check of int15 and s120 (this\n"
           "          line said heading; corrected by stream s122, round 4, the fourth check of set 14, q4).")
EDITS = [(SPC, S_APRS_OLD, S_APRS_NEW, "V2-SPEC.md line 47"), (SPC, S_B16_OLD, S_B16_NEW, "V2-SPEC.md line 82, the switch"),
         (SPC, S_RTC_OLD, S_RTC_NEW, "V2-SPEC.md line 82, the clock"), (SPC, S_D8_OLD, S_D8_NEW, "V2-SPEC.md line 84"),
         (SPC, S_E6_OLD, S_E6_NEW, "V2-SPEC.md line 86"), (SPC, S_C33_END, S_C33_END + S_C34, "V2-SPEC.md correction 34"),
         (ENV, E_TRACO_OLD, E_TRACO_NEW, "OPERATING-ENVELOPE.md line 77"), (ENV, E_BKEY_OLD, E_BKEY_NEW, "OPERATING-ENVELOPE.md line 83"),
         (ENV, E_NOTE_AT, E_NOTE + E_NOTE_AT, "OPERATING-ENVELOPE.md's correction note"),
         (DST, D_DC10_AT, D_DC10_AT + D_DC10, "DEFINITION-STATUS.md row DC-10"), (DST, D_DEP_OLD, D_DEP_NEW, "the dependency row"),
         (C15, C15_OLD, C15_NEW, "apply_check15c_fixes.py's docstring")]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    raise SystemExit(2)


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    nls = L.netlists()
    for b, s in NETS.items():
        if nls[b]["sha16"] != s: refuse("board %s's netlist is %s, not set 14's %s" % (b, nls[b]["sha16"], s))
    if L.sha16(CONOPS[0]) != CONOPS[1]: refuse("CONOPS.md is not c5430071's file")
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    n = 0
    for what, al in ASSERT.items():
        for a in al:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (what, msg))
            n += 1
    for word, spec in NEVER:
        got = subprocess.run(["git", "-C", L.TOP, "log", "--all", "--format=%h", "-S", word, "--", spec],
                             capture_output=True, text=True).stdout.split()
        if got: refuse("a generator held %s at %s" % (word, ", ".join(got)))
        n += 1
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    for rel, old, new, why in EDITS:
        if any(d in new for d in L.DASHES): refuse("%s: a dash in the new text" % why)
        if texts[rel].count(old) != 1: refuse("%s: the old passage is found %d times" % (why, texts[rel].count(old)))
        texts[rel] = texts[rel].replace(old, new)
    for rel, old, new, why in EDITS:
        if texts[rel].count(new) != 1: refuse("%s: the new passage does not read back once" % why)
    if check:
        print("%s: --check at %s: %d edits located, %d assertions hold (set 14's netlists, the generators at the commits "
              "named, the held sheets); nothing written" % (TAG, head, len(EDITS), n))
        return 0
    for rel, txt in texts.items():
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(txt)
        if rel.endswith(".md"): L.md_blocks(rel)
        else: compile(txt, rel, "exec")
    if L.sha16(CONOPS[0]) != CONOPS[1]: refuse("CONOPS.md changed")
    print("%s: at %s %d edits written, %d assertions held first; CONOPS.md unchanged; %s" % (
        TAG, head, len(EDITS), n, ", ".join("%s to %s" % (os.path.basename(r), L.sha16(r)) for r in DOCS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
