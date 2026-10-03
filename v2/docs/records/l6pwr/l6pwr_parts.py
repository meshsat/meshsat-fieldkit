#!/usr/bin/env python3
"""l6pwr_parts.py: the component identities of every part Layer 4 selected for the power design (MESHSAT-1357, Layer 6 record
l6pwr, 3 October 2026; the owner's instruction of 2 October 2026, L6: "component selections and alternatives, exact parts/packages,
applicable ratings, derating, source evidence and qualification obligations").

PROTOTYPE DESIGN: nothing is bought, built, powered or measured. The parts are SELECTED BY LAYER 4 (L4-E5 to L4-E11) and exist
only in release-guarded drafts (the apply_*.py scripts of those records), on no committed netlist; this record RECORDS and SOURCES
them and reselects nothing. A mismatch is a FINDING with the Layer 4 row it affects. No generator, Layer 4 record, pcb_interfaces.yaml
or HW-FW-CONTRACT.md is edited.

What it prints, with the basis of every figure (MAKER: the document, revision and page, read here from the file by pdftotext;
RECORD: a Layer 4 record's figure, the page pinned; CATALOGUE: a dated public reading in inputs/; COMPUTED: arithmetic shown):
  0. the pins: every input file's sha256 (the held-back sheets by the sha256 their fetch script pins; a sheet not fetched here reads UNREAD);
  1. the envelope the grades are judged against (pcb_envelope.yaml);
  2. the parts, one block each: maker, MPN, package and land, grade (the maker's rows against the envelope: INSIDE, AT_LIMIT, OUTSIDE or
     NOT READ), the ratings the Layer 4 record used with its derating, the maker's document (title, revision, URL, sha256, the page
     that prints the part number: rule D-2 PRINTED read here, or how the page decodes it), the dated catalogue reading (LCSC code, stock,
     price), one alternative on the same footprint and what changes, the qualification obligation rows, the rationale in one sentence;
  3. the catalogue table;
  4. the FINDINGS, each computed or read here and named with the Layer 4 row it affects;
  5. the Layer 6 criteria (6.1, 6.2, 6.3, 6.6, 6.8) and what moved for these parts.
With --identities it prints the block for v2/ecad/tools/pcb_part_identities.yaml instead (apply_part_identities_block.py inserts it).

Run from the repository root:  python3 v2/docs/records/l6pwr/l6pwr_parts.py > v2/docs/records/l6pwr/l6pwr_parts.out
Needs pdftotext and pdfinfo (poppler) and PyYAML. Exit 2: a pinned file is not the pinned file; 3: an input cannot be parsed;
4: a cited page does not print what this record says it prints (the citation would be false)."""
import ast
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2", "ecad", "tools"))
import part_identities as PI  # noqa: E402  (the tool's own rule D-2 reader: page_text, names_part, find_pages)

REC = "v2/docs/records/l6pwr"
ENVELOPE = "v2/ecad/tools/pcb_envelope.yaml"
LCSC_READING = REC + "/inputs/lcsc-2026-10-02.json"
JLC_READING = REC + "/inputs/jlc-search-2026-10-02.json"
SAMSUNG_READING = REC + "/inputs/samsung-spec-pages-2026-10-02.json"
FETCH = REC + "/fetch_held_back.py"
# the Layer 4 pages, drafts and outputs this record reads (pinned: when one moves, regen_out refuses and the record is re-read)
L4 = {
    "l4e11": "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md",
    "l4e11_charger": "v2/docs/records/l4e11/apply_gen_sch_a_charger.py",
    "l4e11_entry": "v2/docs/records/l4e11/apply_gen_sch_e_entry.py",
    "l4e8": "v2/docs/records/l4e8/L4E8-BANK.md",
    "l4e8_bank": "v2/docs/records/l4e8/apply_gen_sch_a_bank.py",
    "l4e7_cd": "v2/docs/records/l4e7/L4E7-CONTROL-DECISION.md",
    "l4e7_guard": "v2/docs/records/l4e7/apply_gen_sch_e_solar_guard.py",
    "l4e7_backstop": "v2/docs/records/l4e7/apply_gen_sch_e_backstop.py",
    "l4e7_out": "v2/docs/records/l4e7/l4e7_stage_settings.out",
    "l4e9_entry": "v2/docs/records/l4e9/L4E9-ENTRY-PROPOSALS.md",
    "l4e9_reg": "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md",
    "l4e10": "v2/docs/records/l4e10/L4E10-CELL-THERMAL.md",
    "l4e6": "v2/docs/records/l4e6/L4E6-FAULT-HANDLING.md",
    "l4e5": "v2/docs/records/l4e5/L4E5-SOURCE-CONTROL.md",
    "gen_a": "v2/ecad/tools/gen_sch_a.py",
}
KITS = 5   # the owner's "minimum 5 of each"

# ---------------------------------------------------------------------------------------------------- the makers' documents
# path, doc_id, revision, url, pinned sha256 (None: computed here, the file is in the tree), held_back
DOCS = {
    "bq25730": ("v2/vendor/ti/held/ti-bq25730-sluse65a.pdf", "TI BQ25730 datasheet", "SLUSE65A, February 2021, revised January 2024",
                "https://www.ti.com/lit/ds/symlink/bq25730.pdf", "e41ef289ce1de377d7b92bce609177d924e149099d9c4424d88f6b21ad57153f", True),
    "buk6y10": ("v2/vendor/nexperia/held/nexperia-buk6y10-30p-2020-04-17.pdf", "Nexperia BUK6Y10-30P product data sheet",
                "17 April 2020", "https://assets.nexperia.com/documents/data-sheet/BUK6Y10-30P.pdf",
                "ba928dfe6a85134423562bd378bdfafafb26d857ba08b50560ce5aacb956da40", True),
    "tps1663": ("v2/vendor/ti/held/ti-tps1663-slvset9g.pdf", "TI TPS1663 datasheet", "SLVSET9G, September 2018, revised April 2026",
                "https://www.ti.com/lit/ds/symlink/tps1663.pdf", "8f91a0db2daf2da35abd335420ff9f8b4ac9a99c93dac93e215e0a75e9a866fe", True),
    "ds13012": ("v2/vendor/power/held/diodes-b520c-b560c-ds13012-rev18-2.pdf", "Diodes Incorporated B520C to B560C datasheet",
                "DS13012 Rev. 18-2, March 2023", "https://www.diodes.com/assets/Datasheets/ds13012.pdf",
                "1b1de94df0a7729f4a69a885edd54213594acdce3cd6d4fa072961431ddf71ff", True),
    "tps4811": ("v2/vendor/ti/held/ti-tps4811-q1-slusee5e.pdf", "TI TPS4811-Q1 datasheet", "SLUSEE5E, January 2022, revised April 2026",
                "https://www.ti.com/lit/ds/symlink/tps4811-q1.pdf", "3cfe41fef1407b85abaaee1e27a95ac3cf2cb1bdf218209b8578a835c4c9497f", True),
    "csd19536": ("v2/vendor/ti/held/ti-csd19536ktt-slps540c.pdf", "TI CSD19536KTT datasheet", "SLPS540C, March 2015, revised May 2025",
                 "https://www.ti.com/lit/ds/symlink/csd19536ktt.pdf", "19e1a9660fac8577743f40acc2cdc791539afd5232bbc1fc350e15fec735d78d", True),
    "csd19532": ("v2/vendor/power/ti-csd19532q5b-n-fet.pdf", "TI CSD19532Q5B datasheet", "SLPS414B, December 2013, revised May 2017",
                 "https://www.ti.com/lit/ds/symlink/csd19532q5b.pdf", None, False),
    "ina169": ("v2/vendor/ti/held/ti-ina169-sbos181f.pdf", "TI INA139, INA169 datasheet", "SBOS181F, December 2000, revised February 2017",
               "https://www.ti.com/lit/ds/symlink/ina169.pdf", "dbb74b6cdc5431353f17b044b7d762df1f2f9049d03d2d1611a53058e570d62c", True),
    "tps3701": ("v2/vendor/ti/held/ti-tps3701-sbvs240c.pdf", "TI TPS3701 datasheet", "SBVS240C, November 2014, revised February 2019",
                "https://www.ti.com/lit/ds/symlink/tps3701.pdf", "27c94a6c3a243bf539e98942d26f0bd9ed979c5775c12cf86b7c1a8c3d7d9560", True),
    "tps3808": ("v2/vendor/ti/ti-tps3808.pdf", "TI TPS3808 datasheet", "SBVS050N, May 2004, revised August 2026",
                "https://www.ti.com/lit/ds/symlink/tps3808.pdf", None, False),
    "smcj": ("v2/vendor/power/littelfuse-smcj-series-tvs.pdf", "Littelfuse SMCJ series 1500 W TVS datasheet", "Revised 11/20/15",
             "https://datasheet.lcsc.com/datasheet/pdf/4ffc39069ef6aef3785dfbfda82b9e7d.pdf?productCode=C224052 (LCSC's copy of the maker's sheet)",
             None, False),
    "wsl": ("v2/vendor/vishay/vishay-wsl-power-metal-strip.pdf", "Vishay Dale WSL Power Metal Strip resistors, Document 30100",
            "Revision 23-Nov-2023 (the legal page dated 01-Jan-2026)", "https://www.vishay.com/docs/30100/wsl.pdf", None, False),
    "wsl_held": ("v2/vendor/passives/held/vishay-wsl-30100-2023-11-23.pdf", "Vishay Dale WSL Document 30100, LCSC's copy as L4-E7 read it",
                 "Revision 23-Nov-2023 (the legal page dated 2023)",
                 "https://datasheet.lcsc.com/datasheet/pdf/548f4c1b2301e9c8a8b168347d5344c1.pdf?productCode=C844695",
                 "1b5c68910aa562a0dcce11ec572b4dd1febe63cfb90d20f3eaf5f9c7e01b59ac", True),
    "hojlr": ("v2/vendor/passives/milliohm-hojlr2512-series.pdf", "Shenzhen Milliohm Electronics HoJLR2512 series alloy current-sense resistor specification",
              "version Ho-A0, revision dated 2020-04-13 on page 1 (2019-04-13 on pages 2 and 3)",
              "https://datasheet.lcsc.com/datasheet/pdf/bf6eace094b76bcd756cc1a79c576936.pdf?productCode=C2903468 (the maker's sheet as LCSC hosts it)",
              None, False),
    "zk": ("v2/vendor/power/lcsc-panasonic-eehzk1v101xp.pdf", "Panasonic ZK series conductive polymer hybrid aluminium electrolytic capacitors",
           "no revision date printed (the sheet's RoHS note cites October 2017; LCSC's copy, filed before this record)", "NOT RECORDED in sources.txt (owed)",
           None, False),
    "35e": ("v2/vendor/battery/samsung-35e-orbtronic.pdf", "Samsung SDI INR18650-35E product specification (a distributor's copy)",
            "Ver. 1.1 (L4-E10 reads its date as 2015-07-09)", "TBD (SOURCES.yaml pack-cells: the maker's own copy is not held)", None, False),
    "saft": ("v2/vendor/battery/held/saft-mp176065xtd-31109-2-0625.pdf", "Saft MP 176065 xtd rechargeable Li-ion cell datasheet",
             "Doc. n 31109-2-0625, June 2025", "https://saft4u.saft.com/en/download_file/58d1fabc-9a46-4c07-8df1-0a00d3a1e7a9/English",
             "8ca0a3e09997a4a30567a4313cf83c2b6cf165543baf424e0ff788d5a8d27f8e", True),
}

ENV_IN_USE = (-20.0, 40.0)        # read back from pcb_envelope.yaml in section 1 (asserted)
BOARD_AIR_MAX = 62.1               # worst_inside_air_c.lid_closed, read back and asserted
STORAGE_3M = (-20.0, 45.0)
MARGINS = dict(operating_max=55, storage_max=71, storage_min=-33)


# ---------------------------------------------------------------------------------------------------- the parts
# Each part: id, board, refs, maker, mpn, package, land, draft (the Layer 4 draft that places it), selected_by, grade (op, stg: (lo, hi,
# "doc key", page, phrase) or None), ratings (list of strings: the L4 figure, the maker's rating, the derating), doc (key, page that
# prints the MPN or the scheme, binding PRINTED or DECODE_NOTE), cites (list of (doc key, page, phrase) that must be on the page),
# codes (LCSC codes to read), need_per_kit, alternative, obligations, rationale, provisional (trigger or None), identity (status,
# reason_class, reason, next_action for an UNRESOLVED one).
PARTS = [
    dict(id="L6P-01", board="A", refs=["U3"], maker="Texas Instruments", mpn="BQ25730RSNR", package="WQFN-32 RSN (4.0 x 4.0 mm, 0.4 mm pitch), RSN0032B",
         land="U3's RSN land as drawn for the BQ25731 (the same package; pin 21 NC becomes BATDRV)", draft="l4e11_charger",
         selected_by="L4-E11 section 14, arrangement (B1), the fix round 15 and the review round 16 (E11-27, R-157)",
         grade=dict(kind="industrial", op=(-20, 125, "bq25730", 9, "Junction temperature range, TJ"), electrical=(-40, 125, "bq25730", 9, "TJ = -40"),
                    stg=(-55, 150, "bq25730", 8, "Storage temperature, Tstg")),
         ratings=["VBUS 19.15 to 20.96 V (L4-E11 E11-31's start window) against the recommended ACN, ACP, VBUS 0 to 26 V (p.8): 80.6 percent, no further derating applied",
                  "VSYS_MIN 12.054 V, charge 3.0 A, BATDRV 8.5 / 10 / 11.5 V (p.17) at the pair's sources on VSYS; TI's rule 'Ciss ... less than 5 nF' (p.92), the pair 4.72 nF typical (OPEN, E11-37)",
                  "the register rules of E11-28 (EN_OOA, ChargeCurrent 0 A at POR, the watchdog); the three modes bounded piecewise (L4-E11 15d, E11-31)"],
         doc=("bq25730", 104, "PRINTED"), cites=[("bq25730", 8, "ACN, ACP, VBUS 0 26"), ("bq25730", 92, "Ciss of")],
         codes=["C5219071"], need_per_kit=1,
         alternative="BQ25731RSNR (LCSC C2871872, the part drawn today, the same RSN land; pin 21 NC): no battery FET, so arrangement (A) with E11-24's hold-up bank stands; its recommended TJ row is the same -20 to 125 C",
         obligations=["E11-27 (R-157) the draft applied", "E11-28 (R-158) firmware", "E11-31 (R-161) bench, the three modes", "E11-32 (R-162) supply for the build quantity: LCSC stock 0", "E11-37 (R-183) Ciss against TI's 5 nF, Q-TI-17 drafted"],
         rationale="L4-E11 selected (B1) because the BQ25730's sheet prints VSYS's regulation with no battery (p.1, 9.1) and drives an external battery FET for the pack's 18 A, which the drawn BQ25731 cannot (U-04).",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-02", board="A", refs=["Q39", "Q40"], maker="Nexperia", mpn="BUK6Y10-30P (the fitted code's model BUK6Y10-30PX)",
         package="LFPAK56 (Power-SO8), SOT669, 4 terminals", land="LFPAK56 lands checked against Nexperia's SOT669 drawing (E11-27)", draft="l4e11_charger",
         selected_by="L4-E11 section 15c, option (Q-c), two in parallel (E11-27, R-157)",
         grade=dict(kind="automotive (AEC-Q101 qualified, p.1)", op=(-55, 175, "buk6y10", 3, "junction temperature"), stg=(-65, 175, "buk6y10", 3, "storage temperature")),
         ratings=["VDS -30 V (p.1) against VBAT at most 17.375 V (L4-E11 15a): 58 percent",
                  "RDS(on) at most 10 mOhm at -10 V and 25 C, 16 mOhm at -10 V and 175 C, 25 mOhm at -4.5 V and 25 C (p.6, Table 7); the record's 21.136 mOhm at -8.5 V and 150 C is an ALLOWANCE no printed point bounds (E11-36)",
                  "ISM 320 A single pulse 10 us at Tmb 25 C (p.3) against the docking pulse 242.9 A peak, 33.8 us; derated x0.7 at the +70 C air (224 A), one FET takes at most 0.848 of it (E11-30); the junction limit 150 C, 25 K under the 175 C rating",
                  "Ciss 2.36 nF typical at -15 V (p.6 Table 7; about 2.87 nF near 0 V, Fig. 12), the pair 4.72 nF against TI's 5 nF (E11-37)"],
         doc=("buk6y10", 1, "PRINTED"), cites=[("buk6y10", 1, "AEC-Q101"), ("buk6y10", 3, "320"), ("buk6y10", 6, "- 13 16 m")],
         codes=["C3278350", "C2846047"], need_per_kit=2,
         alternative="Vishay SQJ403EP (option Q-b, held sheet 67109 Rev. A): a PowerPAK SO-8 single, the same 5 x 6 mm class but a different land drawing, one FET whose bar is 9.49 C/W (a heat path through the case, not a pour): not a drop-in",
         obligations=["E11-27 (R-157)", "E11-29 (R-159) the installed pair's Zself + Zmut", "E11-30 (R-160) the whole hot docking waveform; Q-NXP-1", "E11-32 (R-162) supply: LCSC stock 67 against a need of 10", "E11-36 (R-182) RDS(on) at -8.5 V and 150 C", "E11-37 (R-183) Ciss"],
         rationale="L4-E11 15c chose two BUK6Y10-30P because it is the only option inside TI's Ciss whose thermal bar (34.42 C/W per FET at +70 C air) a board pour gives, with a printed RDS(on) maximum to 175 C and a printed body-diode pulse rating over the docking pulse.",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED",
                   "the sheet prints BUK6Y10-30P (p.1, the ordering table p.2 names that type only); the fitted code C3278350 resolves to BUK6Y10-30PX, a suffix the sheet does not print (LCSC and JLCPCB list BUK6Y10-30P, SOT-669, stock 0, and BUK6Y10-30PX, LFPAK-56, stock 67, with the same ratings), so the X is INFERRED to be Nexperia's packing code",
                   "Nexperia's packing-code document or its written confirmation that BUK6Y10-30PX is BUK6Y10-30P on a reel (Q-NXP-1 can carry it); then the identity reads PRINTED by rule D-2's packing clause")),
    dict(id="L6P-03", board="A", refs=["U42"], maker="Texas Instruments", mpn="TPS16630PWPR", package="HTSSOP-20 PWP (6.50 x 4.40 mm), PWP0020T",
         land="the HTSSOP-20 land checked against TI's PWP0020 drawing (E11-27)", draft="l4e11_charger",
         selected_by="L4-E11 section 16e, option (E), and 17a (L4-F03, D-15; E11-27, R-181)",
         grade=dict(kind="industrial", op=(-40, 125, "tps1663", 7, "Operating Junction temperature"), stg=(-65, 150, "tps1663", 7, "Storage temperature")),
         ratings=["IN 4.5 to 60 V (p.7) against VSYS at most 17.375 V: 29 percent; the absolute maximum 67 V (p.7)",
                  "I(OL) 1.4713 to 1.8018 A at R(ILIM) 11.0 kOhm 0.1 percent, INFERRED between the printed 9 kOhm and 30 kOhm rows (p.8) by Equation 6 (p.20); the 813 contact at 51.5 percent of 3.5 A",
                  "limiting at most 202 ms, auto-retry after 500 to 800 ms with MODE to GND (p.10, p.26); RON at most 53 mOhm; the hard short's 566 A ceiling over 4.5 us (17a)"],
         doc=("tps1663", 36, "PRINTED"), cites=[("tps1663", 8, "R(ILIM) = 9k"), ("tps1663", 4, "Overvoltage cutoff, adjustable")],
         codes=["C1849461"], need_per_kit=1,
         alternative="none on the PWP land: the orderable addendum (p.36) lists TPS16630 alone in HTSSOP-20; TPS16632 (overvoltage clamp, power limiting) is VQFN-24 only. The latch-off response is MODE's setting, not another part",
         obligations=["E11-27 (R-157, R-181) the draft applied", "E11-38 (R-184) the whole fault envelope on the bench; Q-TI-18 the OUT undershoot", "E11-35 (R-179) the fans' start under the least limit 1.471 A", "E11-39 (R-188) the fans started one at a time"],
         rationale="L4-E11 16e selected the eFuse as the only protection of three whose printed rows keep the 813 contact, the 24 AWG and the copper inside their ratings in a sustained overload over temperature.",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-04", board="A", refs=["R221", "C237", "C238", "C239"], maker="not named", mpn="none (values only: 11k 0.1 percent; 22 nF 50 V C0G; 1 uF 50 V X7R; 100 nF 50 V X7R)",
         package="0603 or as lcsc_fill.py maps the value (not stated by the draft)", land="the draft's default lands", draft="l4e11_charger",
         selected_by="L4-E11 16e and 17a: U42's network (E11-27)", grade=None,
         ratings=["R221 sets I(OL) = 18 / R(ILIM): its 0.1 percent is inside the record's 1.4713 to 1.8018 A band; C237 TI's characterised 22 nF; C238 TI 9.4.1's 1 uF at IN; C239 TI 6.3's 0.1 uF at OUT"],
         doc=None, cites=[], codes=[], need_per_kit=1,
         alternative="none (no part named)", obligations=["E11-27 (R-157): the regenerated netlist reads each; lcsc_fill.py maps the values"],
         rationale="L4-E11 17a added TI's recommended network to U42's draft; the parts are values the pipeline maps by value, no maker's part is named.",
         provisional=None,
         identity=("UNRESOLVED", "CHOICE_OWED", "the draft names values and tolerances and no part number; a 0.1 percent 11k resistor and three capacitors are chosen by lcsc_fill.py's value map at the regeneration (Layer 8)",
                   "the board A generator owner names the parts or lets the value map choose them; the identity table's selection then resolves on the catalogue reading")),
    dict(id="L6P-05", board="A", refs=["D23"], maker="Diodes Incorporated", mpn="B540C-13-F", package="SMC (DO-214AB), 3,000 a reel",
         land="the land key SMC (E11-27)", draft="l4e11_charger", selected_by="L4-E11 17a (TI 9.4.1 and 9.5.1's Schottky at OUT; E11-27)",
         grade=dict(kind="commercial (the sheet: 'general requirements of commercial applications'; an automotive-compliant part exists under a separate sheet, p.1)",
                    op=(-55, 150, "ds13012", 2, "Operating Temperature Range"), stg=(-55, 150, "ds13012", 2, "Storage Temperature Range")),
         ratings=["VRRM 40 V, IO 5.0 A, VF at most 0.55 V, IR at most 0.5 mA (p.1) against VSYS at most 17.375 V: 43 percent; it clamps OUT's negative spike in a hard short (Equation 14, 17a)"],
         doc=("ds13012", 1, "DECODE_NOTE"), cites=[("ds13012", 1, "B5xxC-13-F"), ("ds13012", 1, "0.55")],
         codes=["C72264"], need_per_kit=1,
         alternative="B550C-13-F (the same sheet and SMC land, 50 V): VF at most 0.70 V, so the clamp level rises by 0.15 V",
         obligations=["E11-27 (R-157)", "E11-38 (R-184): D23's VF at 5 A within +5 percent after every case"],
         rationale="L4-E11 17a added TI's recommended Schottky at OUT for the negative spike of a hard short (SLVSET9G 9.4.1, 9.5.1).",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED",
                   "page 1 prints the ordering pattern 'B5xxC-13-F ... xx = Device type, e.g., B520C-13-F' and the marking code 'B540C', not the string B540C-13-F; the part number is decoded by the sheet's own pattern (x = 4 for B540C)",
                   "a DECODED scheme for Diodes' B5xxC-13-F pattern in part_identities.SCHEMES, or Diodes' orderable list naming B540C-13-F; until then the catalogue reading (C72264, DIODES B540C-13-F, SMC) is the only text that names it")),
    dict(id="L6P-06", board="A", refs=["R11"], maker="Shenzhen Milliohm Electronics", mpn="HoJLR2512-3W-8mR-1% (7 mOhm, HoJLR2512-3W-7mR-1%, only if bench V-A07 fails)",
         package="2512 (6.4 x 3.2 mm), 3 W", land="RS2512 (Kelvin taps R-37)", draft="l4e4 apply_gen_sch_a_r11.py (R-04), kept by L4-E5",
         selected_by="L4-E4 (R-04); L4-E5 'What would change' keeps 8 mOhm unless V-A07 (R-75) fails, then 7 mOhm (C2904239, R-155)",
         grade=dict(kind="industrial", op=(-50, 170, "hojlr", 2, "Operating Temperature Range"), stg=None),
         ratings=["3 W rated at 70 C, derated linearly to zero at 170 C (p.2; L4-E8's reading); at the highest permitted current 7.262 A (8 mOhm) 0.42 W, at 8.300 A (7 mOhm) 0.48 W",
                  "tolerance +-1 percent (F), TCR +-50 ppm/K for 2 to 500 mOhm (p.2); L4-E5's INFERRED 5.095 A through R11 at the pin's maximum"],
         doc=("hojlr", 1, "DECODE_NOTE"), cites=[("hojlr", 1, "3W"), ("hojlr", 2, "50")],
         codes=["C2904240", "C2904239"], need_per_kit=1,
         alternative="Vishay WSL2512R0080FEA (the same land; Document 30100): rated 1.0 W at 70 C against 3 W, TCR +-75 ppm/K for 7 to 500 mOhm, so the derating basis and the tap arithmetic change; not a drop-in on power",
         obligations=["R-04 the draft", "R-37, R-62 the Kelvin taps (0.38 mOhm)", "R-75 V-A07 (else 7 mOhm, R-155)", "R-73 (C-9)", "R-101 Milliohm's clarification: TCR from -40 to +25 C"],
         rationale="L4-E4 set R11 to 8 mOhm so U3's input limit stays inside the front end's band; L4-E5 keeps it pending V-A07.",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED",
                   "page 1 prints the numbering scheme (Ho JLR 2512 3W 100mR 1%: maker, series, size, power, value, tolerance F = +-1 percent) and not the part number; the string HoJLR2512-3W-8mR-1% appears nowhere in the sheet",
                   "a DECODED scheme for Milliohm's HoJLR numbering in part_identities.SCHEMES (the page prints the layout), or the maker's confirmation; the catalogue reading names the model")),
    dict(id="L6P-07", board="A", refs=["R12"], maker="Shenzhen Milliohm Electronics", mpn="HoJLR2512-3W-12mR-1%", package="2512, 3 W", land="RS2512",
         draft="l4e6 apply_gen_sch_a_r12.py and apply_lcsc_fill_r12.py (R-01, R-02)", selected_by="L4-E6, candidate (c): R12 12 mOhm, C147 330 pF (R-01)",
         grade=dict(kind="industrial", op=(-50, 170, "hojlr", 2, "Operating Temperature Range"), stg=None),
         ratings=["0.90 W at 9 V and 0.28 to 0.37 W at 36 V against 3 W derated from 70 C (the derating line's 33.3 K/W): at most 92 C (L4-E6)",
                  "the boost peak limit 8.06 / 10.00 / 11.99 A under L1's Isat, stacked at +-1 percent and 50 ppm/K over 75 K (L4-E6)"],
         doc=("hojlr", 1, "DECODE_NOTE"), cites=[("hojlr", 2, "0.5mR~500mR")],
         codes=["C2904242", "C500739"], need_per_kit=1,
         alternative="the drawn LR2512D-3W-5mR-1% (C500739) is the superseded 5 mOhm value, not an alternative; a WSL2512 at 12 mOhm fits the land at 1.0 W (70 C)",
         obligations=["R-01, R-02 the drafts", "R-64 (7b.5) L1's current with R12 fitted", "R-66 the loop's Bode row"],
         rationale="L4-E6 found 12 mOhm the smallest catalogue value closing B-1 and B-2 at both R11 outcomes (its out 5 scan).",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "as R11: the sheet prints the numbering scheme, not HoJLR2512-3W-12mR-1%", "as R11")),
    dict(id="L6P-08", board="A", refs=["R227"], maker="Shenzhen Milliohm Electronics", mpn="HoJLR2512-3W-5mR-1%", package="2512, 3 W", land="RS2512 with Kelvin taps (R-97)",
         draft="l4e9 apply_gen_sch_a_u17.py (R-06)", selected_by="L4-E9 round 2 part A, section 3 (U17 on R227 in the PoE stage's input; R-06)",
         grade=dict(kind="industrial", op=(-50, 170, "hojlr", 2, "Operating Temperature Range"), stg=None),
         ratings=["1.037 W at the stage's fault bound 14.33 A against 3 W at 62.1 C derated from 70 C (L4-E9 IF-13: MEETS, MAKER)",
                  "a hard VBAT connect: 2.879 mJ nominal through R227, its maximum UNRESOLVED until Milliohm's single-pulse rating (R-101)"],
         doc=("hojlr", 1, "DECODE_NOTE"), cites=[("hojlr", 2, "70")],
         codes=["C2903482"], need_per_kit=1,
         alternative="Vishay WSL2512R0050FEA (the same land, 1.0 W at 70 C): the 1.037 W fault-bound dissipation would exceed it, so not an alternative at this rating",
         obligations=["R-06 the draft", "R-27 firmware (FW-A09 recalibrated)", "R-84 V-A04 on R227", "R-97 the Kelvin taps and the lcsc_fill line", "R-101 Milliohm's pulse rating", "R-117 the loop's inductance", "R-120, R-121 L10's L(I)"],
         rationale="L4-E9 moved U17's shunt to the stage's input because the INA226's pins are 40 V absolute and the drawn rail is 54 V (HF-F02).",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "as R11: the sheet prints the numbering scheme, not HoJLR2512-3W-5mR-1%", "as R11")),
    dict(id="L6P-09", board="A", refs=["R221", "R222", "R223", "R224", "R225", "R226"], maker="Shenzhen Milliohm Electronics", mpn="HoJLR2512-3W-45mR-1%",
         package="2512, 3 W", land="RS2512, each beside its can (R-40)", draft="l4e8_bank", selected_by="L4-E8 'Status': six ballasts, one in series with each EEHZK1V331P (R-07)",
         grade=dict(kind="industrial", op=(-50, 170, "hojlr", 2, "Operating Temperature Range"), stg=None),
         ratings=["each can's current at most 2.4096 A (R11 8 mOhm) or 2.7661 A (7 mOhm) on L4-E8's bound: 0.26 to 0.35 W against 3 W; the ballast term at most 2.09 W in all at the bound's worst corner (R-51)"],
         doc=("hojlr", 1, "DECODE_NOTE"), cites=[("hojlr", 2, "3W")],
         codes=["C2903491"], need_per_kit=6,
         alternative="a WSL2512 at 45 mOhm fits the land (1.0 W at 70 C covers 0.35 W); its TCR +-75 ppm/K changes nothing the bound needs",
         obligations=["R-07 the draft (refuses before R12)", "R-09 the text corrections", "R-40 branch mismatch at layout", "R-68 (7b.8) the bank on the bench", "R-91 L4-E8's release guard"],
         rationale="L4-E8 put a 45 mOhm ballast in series with each can so no can's current depends on the cans matching (the conservative bound over independent branches).",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "as R11: the sheet prints the numbering scheme, not HoJLR2512-3W-45mR-1%", "as R11")),
    dict(id="L6P-10", board="A", refs=["C163", "C178", "C179", "C180", "C199", "C200"], maker="Panasonic", mpn="EEHZK1V331P",
         package="SMD can G, 10.0 mm diameter x 10.2 mm (CPOL10)", land="the generator's CPOL10 land (gen_sch_a.py V331 tuple)", draft="gen_a (drawn; kept by L4-E8 behind the ballasts)",
         selected_by="the drawn cans, kept by L4-E8 (B-4 closes on the bound at both R11 outcomes)",
         grade=dict(kind="industrial (AEC-Q200 compliant, p.1)", op=(-55, 125, "zk", 1, "Category temp. range"), stg=None),
         ratings=["330 uF +-20 percent, 35 V (p.2) against VBUS20 at most 20.96 V: 60 percent",
                  "ripple current 2800 mA rms at 100 kHz and +125 C, ESR 20 mOhm at 100 kHz and +20 C (p.2) against each can's bound 2.4096 A (8 mOhm; 86 percent) or 2.7661 A (7 mOhm; 98.8 percent, the rule's limit 2.7709 A, L4-E8)",
                  "endurance 4000 h at 125 C (p.1); the rated temperature rise is not printed, so the can's own rise is measured (L4-E8 CONDITIONAL B4, bench 7b.8)"],
         doc=("zk", 2, "PRINTED"), cites=[("zk", 2, "2800"), ("zk", 1, "4000 h")],
         codes=["C278516"], need_per_kit=6,
         alternative="EEHZK1V331V (the same row, the vibration-proof product, the same land and ratings): the mechanical build changes, nothing electrical",
         obligations=["R-07", "R-68 (7b.8): the ESR envelope at -20 C, each can's rise (the lifetime) and current", "R-102 the cans' own ESR, ESL and capacitance regions", "R-51 the ballast term in the budgets"],
         rationale="L4-E8 kept the six drawn EEHZK1V331P because, ballasted, every can stays under its 2.8 A rating on a bound over the sheet's whole printed range (0.56 to 1.56 x 330 uF, ESR 0 to the cold limit).",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-11", board="A", refs=["C236"], maker="Panasonic", mpn="EEHZK1V181P", package="SMD can F, 8.0 mm diameter x 10.2 mm (CPOL8)", land="CPOL8",
         draft="l4e11_charger", selected_by="L4-E11 section 12 (D5) and 14: VSYS's 50 uF effective by design (SLUSE65A 9.1); E11-27",
         grade=dict(kind="industrial (AEC-Q200 compliant, p.1)", op=(-55, 125, "zk", 1, "Category temp. range"), stg=None),
         ratings=["180 uF +-20 percent, 35 V (p.2) against VBAT at most 17.375 V: 50 percent; ripple 2000 mA rms, ESR 27 mOhm (p.2); 90.7 uF effective at its stacked worst (17a) against TI's 50 uF"],
         doc=("zk", 2, "PRINTED"), cites=[("zk", 2, "2000 27")],
         codes=["C242139"], need_per_kit=1,
         alternative="EEHZK1V181V (the same row, vibration-proof): mechanical only",
         obligations=["E11-27 (R-157)", "E11-07 VSYS's effective capacitance at 16.884 V (given by design with this part)"],
         rationale="L4-E11 added one 180 uF hybrid on VSYS so TI's 50 uF minimum holds by design at the pack's top voltage.",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-12", board="A", refs=["C6"], maker="Samsung Electro-Mechanics (the catalogue's model for C1613)", mpn="CL10B332KB8NNNC (3.3 nF 50 V X7R 0603, lcsc_fill.py's 0603 3.3 nF)",
         package="0603", land="C0603", draft="l4e8_bank", selected_by="L4-E8 'The choice (SESSION)': Cc2 from 680 pF to 3.3 nF (R-07)", grade=None,
         ratings=["the front end's compensation (type II): 3.3 nF with Rc1 15k and Cc1 220n kept; the loop re-verified by the generator's loop check (R-01, R-66)"],
         doc=None, cites=[], codes=["C1613"], need_per_kit=1,
         alternative="any 3.3 nF 50 V X7R 0603 (a compensation part; the loop check judges it)", obligations=["R-07", "R-66 the loop's Bode row"],
         rationale="L4-E8 took Cc2 ascending through lcsc_fill.py's 0603 capacitors until the loop held with the ballasts.",
         provisional=None,
         identity=("UNRESOLVED", "DOCUMENT_OWED", "the draft names the code C1613 and the value; the catalogue reads Samsung CL10B332KB8NNNC; no Samsung page for it is read here",
                   "read Samsung's specification page for CL10B332KB8NNN (read_catalogue.py's Samsung reader takes it) and bind it as the other CL parts are")),
    dict(id="L6P-13", board="E", refs=["U21 (guard)", "U6 (entry)"], maker="Texas Instruments", mpn="TPS48110AQDGXRQ1", package="VSSOP-19 DGX (5.10 x 3.00 mm), DGX0019A",
         land="DGX-19, to be added to meshsat.pretty from TI's DGX0019A drawing (E11-01)", draft="l4e7_guard (U21), l4e11_entry (U6)",
         selected_by="L4-E11 3c (the entry, E11-01, R-123); L4-E7's solar-fault remedies, check 5 (the guard, R-173)",
         grade=dict(kind="automotive (AEC-Q100 grade 1, -40 to +125 C ambient, p.1)", op=(-40, 125, "tps4811", 8, "TJ = -40"), stg=(-55, 150, "tps4811", 7, "Storage temperature, Tstg")),
         ratings=["V(VS) operating 3.5 to 80 V (p.8), absolute 100 V (p.7): the entry's OVLO maximum 43.18 V (54 percent); the guard's VS 36 V with a stiff source connected cold (45 percent); PV_F at most <<PVF_REF>> V at the modelled step with the guard on at round 2's <<LOOP>> uH reference loop and <<PVF_RING>> V at the cold connection's ring over the envelope (L4-E7's output, parsed), <<PVF_RING_ABS>> V under the 100 V absolute maximum and over the 80 V recommended operating row by <<PVF_OVER_REC>> V, which L4-E7 carries OPEN on the guard (FINDING L6P-F10)",
                  "the entry: OCP 29.2 / 30.6 / 31.5 mV at RSET 100 Ohm with R19 4.5 mOhm (6.36 to 7.14 A), the short-circuit trip 10.36 to 13.87 A on the filtered sense, CTMR 22 nF (0.247 to 0.49 ms), auto-retry 512 ms (p.4)",
                  "the guard: OV rising <<OV_RISE>> to <<OV_HIGH>> V, falling <<OV_FALL>> V or more; INP high from <<INP_ON>> V through R96 100k over R97 28.0k (both at <<INP_TOL>> percent); INP at most <<INP_REF>> V at the reference loop and <<INP_RING>> V at the cold connection's ring, <<INP_RING_ABS>> V under its 20 V absolute maximum (p.7) and over L4-E7's 18 V line (10 percent under) by up to <<INP_OVER>> V (FINDING L6P-F04)"],
         doc=("tps4811", 44, "PRINTED"), cites=[("tps4811", 8, "Operating input voltage 3.5 80"), ("tps4811", 7, "20"), ("tps4811", 4, "Auto-retry")],
         codes=["C17556513"], need_per_kit=2,
         alternative="TPS48111AQDGXRQ1 (the same DGX land; p.4): no overvoltage protection and latch-off, so the guard loses its OV cut-off (its whole function) and the entry latches after a fault until a re-plug",
         obligations=["E11-01 (R-123) the entry draft and the DGX-19 land", "E11-17 (R-118) the trip thresholds and the start at 43 V", "E11-20 the hard short's loop inductance", "R-153 (D9) the overcurrent delay's spread", "R-173 the guard draft, R-176 its seven bench rows, R-174 CS116 and CS115"],
         rationale="L4-E11 3c selected the TPS4811-Q1 because it starts from a 9.00 V plug, meets the 100 V class and 43.18 V OVLO and trips the breaker inside 0.247 ms where the LM5069 cannot; L4-E7 reused it as the panel port's over-voltage cut-off in TI's own topology.",
         provisional="the guard's instance (U21): re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1); the entry's instance (U6) is not under that trigger",
         identity=("RESOLVED", None, None, None)),
    dict(id="L6P-14", board="E", refs=["Q7"], maker="Texas Instruments", mpn="CSD19536KTT", package="D2PAK (TO-263) KTT, 3 pins",
         land="the D2PAK land checked against TI's KTT drawing (E11-01)", draft="l4e11_entry", selected_by="L4-E11 3c, the entry's pass FET (E11-01, R-123)",
         grade=dict(kind="industrial", op=(-55, 175, "csd19536", 1, "Operating Junction"), stg=None),
         ratings=["VDS 100 V (p.1) against the entry's OVLO maximum 43.18 V: 43 percent; RDS(on) at most 2.3 mOhm at 10 V (p.5); ID 272 A at TC 25 C (p.1)",
                  "Figure 4-10 (p.6, the SOA) read from TI's vector drawing and derated by L4-E9's 0.4454 for the whole pulse: a start into a hard short reaches 0.743 of the derated chart (L4-E11 3c); the transconductance 329 S typical only (D10, R-153)"],
         doc=("csd19536", 1, "PRINTED"), cites=[("csd19536", 6, "Figure 4-10"), ("csd19536", 1, "100")],
         codes=["C2687963"], need_per_kit=1,
         alternative="NOT READ: TI's other 100 V KTT (D2PAK) parts share the land, but each one's SOA figure decides E11-17's start into a short and none was read here",
         obligations=["E11-01 (R-123)", "E11-14 its D2PAK land's copper at 20 A", "E11-17 (R-118) the peaks held under the chart, Q7 unharmed", "E11-20 the hard short in service (at most 178 A, IDM derated)", "R-153 (D10) the transfer curve"],
         rationale="L4-E11 3c paired the breaker with the CSD19536KTT because the TPS4811-Q1 limits no power and this FET's printed SOA carries the start into a short with headroom (1.346) that the drawn CSD19532Q5B's does not (3.08 of its derated chart).",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-15", board="E", refs=["Q12 (guard pass)", "Q13 (guard return)", "Q1 (entry ideal diode, L4-E9)"], maker="Texas Instruments", mpn="CSD19532Q5B",
         package="VSON-CLIP 8 (DNK), 5 x 6 mm (SON-8 5x6)", land="the PPAK / SON 5x6 land Q7 carries today (R-17)", draft="l4e7_guard (Q12, Q13), l4e9 apply_gen_sch_e_q1.py (Q1)",
         selected_by="L4-E9 part A section 1 (Q1, R-17); L4-E7's remedies, check 5 (Q12, Q13; R-173)",
         grade=dict(kind="industrial", op=(-55, 150, "csd19532", 1, "Operating Junction"), stg=None),
         ratings=["VDS 100 V (p.1): Q1 holds 66.15 V reversed (66 percent, L4-E9); Q12 holds 36 V connected cold and at most <<Q12_VDS>> V across it at the step (<<Q12_VDS_PCT>> percent, L4-E7's table; PV_F <<PVF_REF>> V); Q13 holds 25 V reversed",
                  "RDS(on) at most 4.9 mOhm at VGS 10 V and 17 A (p.3); ID 140 A, IDM 400 A (p.1); Q12 turns off at most <<Q12_OFF_A>> A within <<Q12_OFF_US>> us at the reference loop (L4-E7); the series path 25.23 mOhm at the FETs' 150 C reading",
                  "Q13's leakage: 1 uA printed at 80 V and 25 C against 32.1 uA (the dividers' conductance); D-11 CONDITIONAL on the leakage above +25 C (L4-E7)",
                  "Q1: avalanche 83.6 mJ in the capability scenario against EAS 274 mJ; 100.5 V against 100 V, NOT MET by 0.5 V outside every requirement (L4-E9, DECISION-31)"],
         doc=("csd19532", 1, "PRINTED"), cites=[("csd19532", 3, "4.9"), ("csd19532", 1, "400")],
         codes=["C473333"], need_per_kit=3,
         alternative="NOT READ: TI's Q5B family (VSON-CLIP 5 x 6) shares the land; no other 100 V member was read, and Q13's hot leakage and Q1's avalanche figures are this part's",
         obligations=["R-17 (Q1) the draft and the reverse check", "R-173 the guard draft", "R-176 rows 1 to 7 (the cut-off's rise and fall, the 36 V source cold, Q12's waveforms, Q13's hot leakage)", "R-112 Q1's threshold against TI's 2.5 V recommendation"],
         rationale="L4-E9 chose the 100 V CSD19532Q5B for Q1 because a reversed 36 V input puts 66.15 V across it (over the drawn 60 V part), and L4-E7 reused the same part for the guard's pass and return switches.",
         provisional="Q12 and Q13 belong to the guard: re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("RESOLVED", None, None, None)),
    dict(id="L6P-16", board="E", refs=["D4"], maker="Littelfuse", mpn="SMCJ30A", package="DO-214AB (SMC)", land="TVS (the drawn D4 land)", draft="l4e7_guard",
         selected_by="L4-E7's remedies, check 5: D4 from the SMCJ28A to the SMCJ30A (R-173); its LCSC code 'owed' in the draft",
         grade=dict(kind="industrial", op=(-65, 150, "smcj", 1, "Operating Temperature Range"), stg=(-65, 175, "smcj", 1, "Storage Temperature Range")),
         ratings=["VR 30.0 V, VBR 33.30 to 36.80 V at 1 mA, VC 48.4 V at 31.0 A (p.2) over CS101's <<CS101_PEAK>> V input peak and the cut-off's band (<<OV_RISE>> to <<OV_HIGH>> V); the clamp under the 50 V bulk; at CS116's current it reads <<D4_CS116>> V (L4-E7)",
                  "a stiff 36 V source connected cold: the block never turns on and D4 carries nothing (L4-E7 D4 row); the breakdown falls about 0.1 percent/K cold (typical)"],
         doc=("smcj", 2, "PRINTED"), cites=[("smcj", 2, "33.30 36.80"), ("smcj", 1, "-65 to 150")],
         codes=["C224048", "C224047", "C135160"], need_per_kit=1,
         alternative="Diodes Incorporated SMCJ30A-13-F (C135160, SMC, -55 to +150 C): the same row by the series' naming, another maker, so a substitution under condition 1 until its sheet is read",
         obligations=["R-173 the guard draft (the code the draft owes: C224048 reads SMCJ30A, Littelfuse, this reading)", "R-174 CS116 and CS115 on the lead: D4's clamp at each disturbance", "R-176 row 2 (a 36 V supply cold: D4 carries nothing)"],
         rationale="L4-E7 raised D4 to the SMCJ30A as the least held Littelfuse row that leaves the cut-off's aged band room above CS101's peak.",
         provisional="the guard: re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)", identity=("RESOLVED", None, None, None)),
    dict(id="L6P-17", board="E", refs=["D11"], maker="Littelfuse", mpn="SMCJ40CA", package="DO-214AB (SMC)", land="TVS", draft="l4e7_guard",
         selected_by="L4-E7's remedies, check 5: the port's clamp when the cut-off is off (R-173); the entry's D10 part",
         grade=dict(kind="industrial", op=(-65, 150, "smcj", 1, "Operating Temperature Range"), stg=(-65, 175, "smcj", 1, "Storage Temperature Range")),
         ratings=["bidirectional, VR 40.0 V, VBR 44.40 to 49.10 V, VC 64.5 V at 23.3 A (p.2): clamps the port at <<D11_10A>> V at 10 A hot (<<D11_5A>> V at 5 A), at most <<D11_CS116_MJ>> mJ a pulse, under Q12's 100 V and U21's VS (L4-E7 CS116 off row); at most <<D11_RING_MJ>> mJ at the cold connection's ring and <<D11_STEP_MJ>> mJ against <<D11_LIM_MJ>> mJ at the step (L4-E7)"],
         doc=("smcj", 2, "PRINTED"), cites=[("smcj", 2, "44.40 49.10")],
         codes=["C80273"], need_per_kit=1,
         alternative="SMCJ40A (unidirectional, the same row and land): a reversed panel's ring would then be clamped at one diode drop instead of VC; not equivalent for D-11",
         obligations=["R-173", "R-176", "R-174"], rationale="L4-E7 placed the bidirectional clamp across the port for the cut-off's off state (night, after a cut) and a reversed panel's ring.",
         provisional="the guard: re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)", identity=("RESOLVED", None, None, None)),
    dict(id="L6P-18", board="E", refs=["C131", "C132", "C135", "C136"], maker="Samsung Electro-Mechanics", mpn="CL32B225KCJSNNE", package="1210 (3.2 x 2.5 x 2.5 mm)", land="C1210",
         draft="l4e7_guard", selected_by="L4-E7 round 2 for the review's B6 and L4-F01 (the port bank; R-173, R-176 row 3)", grade=None,
         ratings=["2.2 uF +-10 percent, 100 V, X7R (the maker's page) against PV_F at most <<PVF_REF>> V at the step (<<PVF_REF_PCT>> percent) and <<PVF_RING>> V at the cold connection's ring (<<PVF_RING_PCT>> percent); the bound on the maker's curves: 3.98 uF at 36 V for the four, 1.68 uF at 75 V (L4-E7's fetch_maker_curves.py, held back)"],
         doc=None, cites=[], codes=["C55151"], need_per_kit=4,
         alternative="another maker's 2.2 uF 100 V X7R 1210 fits the land, but the record's bound rests on Samsung's own DC-bias, bias-TCC and ESR curves, so a substitute is bounded again before it is a substitute",
         obligations=["R-173 the guard draft (the code the draft owes: C55151 reads CL32B225KCJSNNE, this reading)", "R-176 row 3 (the waveforms at the IC pins with the port bank)", "R-180, R-186, R-187 (B6-ENG-1: the source loop at least 3.30 uH)"],
         rationale="L4-E7's B6 round 2 chose the parts whose maker publishes the DC-bias curves the bound needs, four 2.2 uF 100 V on PV_F holding the high side while Q13 is off.",
         provisional="re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "Samsung's specification page prints CL32B225KCJSNN (the part number less its last character, the packaging code E the catalogue's model carries) and no temperature range; the page is date-stamped and not filed (the excerpt in inputs/ is the reading)",
                   "Samsung's part-number legend (the catalogue's packaging code) read and filed, or the catalogue reading accepted as the identity; the grade needs Samsung's MLCC catalogue (X7R: -55 to +125 C as the EIA class), NOT READ here")),
    dict(id="L6P-19", board="E", refs=["C133", "C134", "C71", "C72", "C73", "C74"], maker="Samsung Electro-Mechanics", mpn="CL32B106KBJNNNE", package="1210 (3.2 x 2.5 x 2.5 mm)", land="C1210",
         draft="l4e7_guard (edits the backstop draft's C71 to C74)", selected_by="L4-E7 round 2 (B6): C133 and C134 on PV_P beside the bulk, C71 to C74 on TRK_VS (R-173, R-21)", grade=None,
         ratings=["10 uF +-10 percent, 50 V, X7R (the maker's page) against PV_P at most <<PVP>> V (<<PVP_PCT>> percent) and TRK_VS at most <<TRKVS>> V (<<TRKVS_PCT>> percent, L4-E7's table); the bound on the maker's curves: 12.88 uF at 7.46 V, 5.07 uF at 30 V for the two on PV_P (L4-E7)"],
         doc=None, cites=[], codes=["C138687"], need_per_kit=6,
         alternative="as C131: another maker's 10 uF 50 V X7R 1210 fits the land and is bounded again on its own curves",
         obligations=["R-173, R-21 the drafts (the code the drafts owe: C138687 reads CL32B106KBJNNNE, this reading)", "R-176 row 3", "R-36 the MLCC ripple rating (board A's 10 uF 50 V 1210 rows, the same class)"],
         rationale="as C131: the part whose DC-bias curve the record bounds.", provisional="re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "as CL32B225KCJSNNE: the page prints CL32B106KBJNNN and no temperature range", "as CL32B225KCJSNNE")),
    dict(id="L6P-20", board="E", refs=["C13", "C14"], maker="Samsung Electro-Mechanics", mpn="CL31B106KBHNNNE", package="1206 (3.2 x 1.6 x 1.6 mm)", land="C1206 (drawn)",
         draft="gen_sch_e.py (drawn on TRK_VIN; L4-E7 bounds it)", selected_by="the drawn part; L4-E7 round 2 bounds its curve (TRK_VIN)", grade=None,
         ratings=["10 uF +-10 percent, 50 V, X7R (the maker's page) against TRK_VIN, fed from TRK_VS through R59 (RSENSE1) and so at most TRK_VS's <<TRKVS>> V (INFERRED: a node behind a series resistor; L4-E7's table): <<TRKVS_PCT>> percent; 23.51 uF at 7.46 V and 9.54 uF at 30 V for the bank with C15 and C64 (L4-E7)"],
         doc=None, cites=[], codes=["C89632"], need_per_kit=2,
         alternative="as C131", obligations=["R-176 row 3", "R-36"], rationale="the drawn part, kept; listed because L4-E7's bound rests on its curve.",
         provisional="the drawn part on TRK_VIN, bounded by L4-E7 (re-read at set 28, F-13: the bound read from its current output); the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "as CL32B225KCJSNNE: the page prints CL31B106KBHNNN and no temperature range", "as CL32B225KCJSNNE")),
    dict(id="L6P-21", board="E", refs=["R60", "R61", "R62", "R63", "R64"], maker="Vishay Dale", mpn="WSL2512R0700FEA", package="2512 (6.35 x 3.18 mm), 1.0 W at 70 C",
         land="RS2512", draft="l4e7_backstop", selected_by="L4-E7R, the 100 W backstop's sense bank (R-21, R-98)",
         grade=dict(kind="industrial", op=(-65, 170, "wsl", 2, "Operating temperature range"), stg=None),
         ratings=["70 mOhm +-1 percent (F), five in parallel 14 mOhm; P70 1.0 W each (p.1) against at most <<RS_EACH_W>> W each at the trip's highest <<TRIP_A>> A (<<RS_ALL_W>> W in all, COMPUTED: <<TRIP_A>> squared x 0.014, shared by five)",
                  "TCR +-75 ppm/K for 7 to 500 mOhm (p.2), the record's 75 ppm/K from -55 to +155 C; the warranted rows L4-E7's bound rests on"],
         doc=("wsl", 1, "DECODE_NOTE"), cites=[("wsl", 1, "WSL25124L000FEA"), ("wsl", 2, "-65 to +170"), ("wsl", 1, "1.0 (1)")],
         codes=["C2076144", "C844695"], need_per_kit=5,
         alternative="WSL2512R0700DEA (the same part at +-0.5 percent, tolerance code D; p.1 lists WSL2512 at +-0.5 percent from 0.0005 to 0.5 Ohm): the trip's resistor error halves; a different maker is a substitution under condition 1",
         obligations=["R-21 (apply_gen_sch_e_backstop.py), R-98", "R-101 Vishay's clarification (vishay-wsl2512.txt, the owner sends)", "R-70 bench rows 7b.10, 7b.11, 7b.14"],
         rationale="L4-E7R chose five WSL2512 70 mOhm in parallel because their rows (tolerance, TCR, power) are warranted where the LT8705A's own sense is not.",
         provisional=None,
         identity=("UNRESOLVED", "PART_NUMBER_INFERRED", "Document 30100 prints the global numbering example WSL25124L000FEA and the decode lines (R0100 = 0.01 Ohm; F = +-1 percent; EA = packaging) and not WSL2512R0700FEA; the catalogue reading names it",
                   "a DECODED scheme for Vishay's WSL global part number in part_identities.SCHEMES (the page prints the layout), as SOURCES.yaml's board A WSL entry already decodes by the example")),
    dict(id="L6P-22", board="E", refs=["U18"], maker="Texas Instruments", mpn="INA169NA/3K", package="SOT-23-5 DBV", land="SOT235", draft="l4e7_backstop",
         selected_by="L4-E7R control decision (C): the sense bank read by an INA169 (R-21)",
         grade=dict(kind="industrial", op=(-40, 85, "ina169", 6, "INA169 -40 85"), stg=(-65, 125, "ina169", 4, "Storage temperature, Tstg")),
         ratings=["supply and common mode 2.7 to 60 V (p.1, p.6), analog inputs -0.3 to 75 V absolute (p.4) against PV_P at most 30 V: 50 percent",
                  "the specified range TMIN to TMAX -40 to +85 C (p.6) covers the 62.1 C board air; its rows are printed at VSENSE 50 mV (the recheck's B1: the gain move at the trip's own sense voltage is an assumption with its break-even)"],
         doc=("ina169", 21, "PRINTED"), cites=[("ina169", 6, "INA169 2.7 60"), ("ina169", 4, "75")],
         codes=["C44322"], need_per_kit=1,
         alternative="INA139NA/3K (the same DBV land and sheet, 2.7 to 40 V): PV_P's 30 V is 75 percent of its range, the specified range widens to 125 C; INA169NA/250 is the same part on a 250 reel",
         obligations=["R-21", "R-33, R-101 TI's clarification (texas-instruments-ina169.txt)", "R-70 bench rows"],
         rationale="L4-E7R chose the INA169 because its rows cover the operating condition where the INA250's gain and offset rows are printed at other supplies (approach (B) refused).",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-23", board="E", refs=["U19"], maker="Texas Instruments", mpn="TPS3701DDCR", package="SOT-23-THIN-6 DDC", land="SOT236 (the draft's land)", draft="l4e7_backstop",
         selected_by="L4-E7R control decision (C): the window comparator (R-21)",
         grade=dict(kind="industrial", op=(-40, 125, "tps3701", 4, "Junction temperature"), stg=(-65, 150, "tps3701", 4, "Storage temperature, Tstg")),
         ratings=["VDD 1.8 to 36 V (p.4); VDD on TRK_LDO33 (C67 bypass): 3.3 V, 9 percent; INA watches TRK_VS through R67 110k over R68 9.53k",
                  "INB rising threshold 397 to 403 mV over TJ -40 to 125 C and VDD 1.8 to 36 V (p.5): warranted (L4-E7 CONTROL-DECISION)"],
         doc=("tps3701", 21, "PRINTED"), cites=[("tps3701", 4, "Supply pin voltage 1.8 36"), ("tps3701", 5, "397")],
         codes=["C132788"], need_per_kit=1,
         alternative="TPS3700DDCR (the same DDC land, VDD to 18 V): INSIDE on a 3.3 V supply; INA's divider ratio and the input absolute maximum change",
         obligations=["R-21", "R-70"], rationale="L4-E7R chose the TPS3701 for its warranted threshold rows over the full supply and temperature range.",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-24", board="E", refs=["U20"], maker="Texas Instruments", mpn="TPS3808G33DBVR", package="SOT-23-6 DBV", land="SOT236", draft="l4e7_backstop",
         selected_by="L4-E7R control decision (C): the off-time after a trip, default-off on TRK_LDO33 (R-21)",
         grade=dict(kind="industrial", op=(-40, 125, "tps3808", 6, "TJ = -40 C to 125 C"), stg=(-65, 150, "tps3808", 5, "Storage, Tstg")),
         ratings=["VDD 1.7 to 6.5 V (p.6) on TRK_LDO33 3.3 V; G33 threshold 3.07 V typical (p.3); td with CT = VDD 180 / 300 / 420 ms (p.7): the record's 'RESET low at least 180 ms after any trip'"],
         doc=("tps3808", 22, "PRINTED"), cites=[("tps3808", 7, "180 300 420"), ("tps3808", 3, "3.07V")],
         codes=["C43698", "C189211"], need_per_kit=1,
         alternative="TPS3808G33DBVT (the same part on a small reel, JLCPCB C702174); TPS3808G30DBVR (board B's part, C189211, VIT 2.79 V): the off-time's supply threshold moves",
         obligations=["R-21", "R-70"], rationale="L4-E7R chose the TPS3808G33 for a fixed, printed minimum off-time (180 ms) holding SWEN low after a trip.",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-25", board="E", refs=["R97"], maker="<<R97_MAKER>>", mpn="<<R97_MPN>> (28.0k <<INP_TOL>> percent 25 ppm/K, the guard draft's value text; R96 100k is <<R96_MPN>>)", package="0603", land="the draft's default (R_0603)",
         draft="l4e7_guard", selected_by="L4-E7 round 2 (B6): INP's bottom resistor 28.0k (39k before B6; 30.0k in round 1) (R-173)", grade=None,
         ratings=["INP high from <<INP_ON>> V (R96 100k over R97 28.0k at V(INP_H) 2.0 V); INP at most <<INP_REF>> V with both at <<INP_TOL>> percent at round 2's <<LOOP>> uH reference loop, over L4-E7's 18.0 V line by <<INP_REF_OVER>> V and <<INP_REF_ABS>> V under the 20 V absolute maximum (L4-E7 holds the line from <<INP_HOLDS>>); <<INP_RING>> V at the cold connection's ring (l4e7_stage_settings.out, parsed): FINDING L6P-F04"],
         doc=None, cites=[], codes=[], need_per_kit=1,
         alternative="none (no part named)", obligations=["R-173 the guard draft", "R-176 row 3"],
         rationale="L4-E7's B6 set R97 so U21 turns on by <<INP_ON>> V and INP stays 10 percent under its 20 V to 81 V on PV_F; its <<INP_ROUNDS>> put both divider resistors at <<INP_TOL>> percent and named the YAGEO RT parts.",
         provisional="re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("UNRESOLVED", "DOCUMENT_OWED", "the draft names YAGEO <<R97_MPN>> (28.0k, <<INP_TOL>> percent, 25 ppm/K) with its LCSC code owed; YAGEO's RT series specification is not held in the tree, so no page binds the part number",
                   "file YAGEO's RT series specification (the ordering code table) and read the LCSC code for <<R97_MPN>> (and <<R96_MPN>> for R96)")),
    dict(id="L6P-26", board="E", refs=["R19 (entry)", "R87 (guard)"], maker="Shenzhen Milliohm Electronics", mpn="HoLLR2512-3W-4.5mR-1% (the catalogue's model for C2985708; the drafts say '4.5mOhm 1% 2512 3W 50ppm')",
         package="2512, 3 W", land="RS2512", draft="l4e11_entry (R19), l4e7_guard (R87)", selected_by="L4-E11 3c (R19, the breaker's sense: 30.6 mV at 6.8 A; E11-01); L4-E7's remedies (R87; R-173)", grade=None,
         ratings=["4.5 mOhm +-1 percent: the breaker at 6.36 to 7.14 A with RSET 100 Ohm; at 7.14 A 0.23 W against 3 W (COMPUTED); the 50 ppm/K the drafts state is not read in any held sheet"],
         doc=None, cites=[], codes=["C2985708"], need_per_kit=2,
         alternative="HoJLR2512 at 4.5 mOhm if Milliohm makes it (the held HoJLR sheet's range 0.5 to 500 mOhm covers it; no catalogue reading of such a code is filed): the held sheet would then apply",
         obligations=["E11-01 (R-123), R-173 the drafts", "E11-17 the trip thresholds on a slow ramp"],
         rationale="L4-E11 3c sized R19 for a 30.6 mV sense at the panel's and the entry's current; the part is the catalogue's 4.5 mOhm 3 W 2512.",
         provisional="R87 belongs to the guard: re-read at set 28 (F-13): L4-E7's guard draft on this tree still names this part; the guard stays a release-guarded draft, its source loop open (B6-ENG-1)",
         identity=("UNRESOLVED", "DOCUMENT_OWED", "the code C2985708 resolves to Milliohm's HoLLR2512 series (LCSC: HoLLR2512-3W-4.5mR-1%), not the HoJLR2512 series whose sheet the tree holds; no HoLLR sheet is held, so the 3 W, 1 percent and 50 ppm/K the drafts state are the catalogue's words",
                   "fetch Milliohm's HoLLR2512 sheet from LCSC's datasheet link for C2985708 and read its power, tolerance and TCR rows; or the drafts name a HoJLR2512 4.5 mOhm code")),
    dict(id="L6P-27", board="P (pack build)", refs=["the 12 cells, 4S3P (D-06)"], maker="Samsung SDI", mpn="INR18650-35E", package="18650 cylindrical cell, at most 18.55 mm diameter x 65.25 mm (p.3)",
         land="not a placed part (the pack build; SOURCES.yaml pack-cells, placed_part false)", draft="none (the ruled cell, D-06; pcb_pack_protection.yaml and pcb_energy_chain.yaml)",
         selected_by="the owner's ruling D-06 (the 145 Wh 4S3P pack); L4-E10 FEA-008 final: 'suitable on published evidence' for the envelope rows, 'unsuitable on published evidence' for LO-01d, e, f, g (the margins)",
         grade=dict(kind="consumer or industrial cell (no grade word printed)", op=(-10, 60, "35e", 3, "Discharge : -10 to 60"), charge=(0, 45, "35e", 3, "Charge : 0 to 45"),
                    stg=(-20, 45, "35e", 3, "3 months : -20~45")),
         ratings=["capacity at least 3,350 mAh (p.3); the budget's 144.72 Wh nominal and 107.9 Wh usable at +20 C (L4-E10, MODELLED)",
                  "max. discharge 8,000 mA continuous, 13,000 mA not continuous (p.3): 4S3P at 10 A held is 3.33 A a cell (42 percent), 18 A for 60 s is 6 A a cell (75 percent)",
                  "standard charge 1,700 mA, max. 2,000 mA (p.3): the charger's 3.0 A is 1.0 A a cell (50 percent of the maximum); the discharge cut-off 2.65 V (p.3) against the pack's CUV 2.50 V (L4-E10: the 35E's pack guideline)",
                  "operating: charge 0 to 45 C, discharge -10 to 60 C at the cell surface (p.3): the envelope's -20 C floor is reached by the heater mat (REQ-046); storage 3 months -20 to 45 C, 1 month -20 to 60 C, 1 year -20 to 25 C (p.3): the +71 C and -33 C margins are outside every printed row (L4-E10, U-01)"],
         doc=("35e", 3, "PRINTED"), cites=[("35e", 3, "8,000mA"), ("35e", 3, "1,700mA")],
         codes=[], need_per_kit=12,
         alternative="Samsung INR18650-30Q (30Q6, the same 18650 format, compared by L4-E10 as S2 and not adopted); a cell change is the owner's (D-06), never the session's",
         obligations=["R-47 FEA-008's downstream evidence", "R-103 U-01's evidence (the HL18650V specification, F2's rating)", "R-109 the E3 and E5 runs with a thermocouple on every cell", "R-110 TEST-PLAN's cell-derived numbers", "U-01 itself is the owner's"],
         rationale="the owner ruled the 35E 4S3P pack (D-06); L4-E10 found it suitable on published evidence inside the envelope and not for the qualification margins, which U-01 carries.",
         provisional=None, identity=("RESOLVED", None, None, None)),
    dict(id="L6P-28", board="P (pack build)", refs=["the PROPOSAL only: 4 cells, 4S1P"], maker="Saft", mpn="MP 176065 xtd", package="prismatic cell, 18.65 x 60.5 x 68.7 mm (sleeved, including terminals), 135 g typical (p.1)",
         land="not a placed part; a prismatic holder and the pocket's fit are OPEN (R-167)", draft="none: a labelled PROPOSAL (L4-E10 section 15, U-01's supported route); adoption is the owner's",
         selected_by="L4-E10 section 15 (restated after Astra's B5) and 16: 'a supported route exists on published manufacturer evidence for the temperature windows'; NOT adopted",
         grade=dict(kind="industrial cell (the sheet: 'unregulated temperature environments from -40 C to +85 C')", op=(-40, 85, "saft", 1, "Discharge -40 C"),
                    charge=(-30, 85, "saft", 1, "Charge -30 C"), stg=(-40, 85, "saft", 1, "Allowable")),
         ratings=["typical capacity 5.6 Ah (C/5, +25 C, 2.5 V cut-off), 3.65 V, 20.4 Wh (p.1): 4S1P 81.6 Wh nominal against the 35E pack's 144.72 Wh; 53.5 to 58.8 Wh usable MODELLED (L4-E10 16)",
                  "recommended maximum discharge 11 A continuous, 22 A pulses, 'Can vary depending on temperatures. Consult Saft' (footnote 2, p.1): the pack's 10 A held and 18 A for 60 s on one cell AWAITING Saft or the sample qualification (R-168)",
                  "maximum continuous charge 5.6 A, 'for optimised operation below 0 C consult Saft' (footnote 4); charge -30 to +85 C, discharge -40 to +85 C, storage allowable -40 to +85 C, recommended +15 to +30 C (p.1): every window covers the envelope and the margins"],
         doc=("saft", 1, "PRINTED"), cites=[("saft", 1, "5.6 Ah"), ("saft", 1, "11 A"), ("saft", 2, "31109-2-0625")],
         codes=[], need_per_kit=4,
         alternative="none: it is itself the alternative to the ruled cell, recorded as a proposal",
         obligations=["R-167 the pocket mock-up (at most 1.40 mm of wrap along the axis)", "R-168 current at temperature and the storage dwell (Saft's statement, clarification/saft-mp176065xtd.txt, the owner sends)", "R-169 the lot's capacity at receipt", "U-01: the owner's adoption"],
         rationale="L4-E10 recorded the Saft as the one cell whose published windows cover every LO row including the margins, at less than half the usable energy and a price indicator of NZ$ 238.72 a cell.",
         provisional=None, identity=("RESOLVED", None, None, None)),
]


# ---------------------------------------------------------------------------------------------------- helpers
def die(code, msg):
    sys.stderr.write("l6pwr_parts: %s\n" % msg); sys.exit(code)


def sha256(rel):
    return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()


def clean(s):
    """ASCII the typographic characters a PDF's text layer carries (the record's rule: no em or en dashes, plain English)."""
    t = {chr(0x2013): "-", chr(0x2014): "-", chr(0x2012): "-", chr(0x2212): "-", chr(0xB0): " ", chr(0x2103): "C", chr(0x3A9): "Ohm", chr(0xB5): "u",
         chr(0x3BC): "u", chr(0xB1): "+-", chr(0x2264): "<=", chr(0x2265): ">=", chr(0x2019): "'", chr(0x2018): "'", chr(0x201C): '"', chr(0x201D): '"',
         chr(0x2122): "", chr(0xAE): "", chr(0x2026): "...", chr(0xA0): " "}
    for a, b in t.items(): s = s.replace(a, b)
    return s.encode("ascii", "replace").decode("ascii")


_PAGES = {}


def page(doc_key, pg):
    """The text layer of one page of a document, through the tool's own reader (part_identities.page_text)."""
    rel = DOCS[doc_key][0]
    k = (rel, pg)
    if k not in _PAGES:
        _PAGES[k] = PI.page_text(os.path.join(TOP, rel), pg)
    return _PAGES[k]


def doc_state(doc_key):
    """present and pinned, present and DIFFERENT (exit 2), or absent (held back and not fetched here)."""
    rel, _, _, _, pinned, held = DOCS[doc_key]
    full = os.path.join(TOP, rel)
    if not os.path.exists(full):
        if held: return "UNREAD"
        die(2, "%s is not in the tree" % rel)
    got = sha256(rel)
    if pinned and got != pinned: die(2, "%s is not the pinned file: sha256 %s, pinned %s" % (rel, got[:16], pinned[:16]))
    return "READ"


def cite_ok(doc_key, pg, phrase):
    """True when the page prints the phrase (whitespace-insensitive, case-insensitive); the record's citation is checked here."""
    if doc_state(doc_key) == "UNREAD": return None
    t = " ".join(clean(page(doc_key, pg)).split()).lower()
    return " ".join(clean(phrase).split()).lower() in t


def verdict(lo, hi):
    """A maker's operating range against the envelope's -20 C floor and the 62.1 C board air (COMPUTED)."""
    if lo is None or hi is None: return "NOT READ"
    if lo < ENV_IN_USE[0] and hi > BOARD_AIR_MAX: return "INSIDE"
    if lo <= ENV_IN_USE[0] and hi >= BOARD_AIR_MAX: return "AT_LIMIT"
    return "OUTSIDE"


def margins_covered(stg):
    if not stg: return "NOT READ (no storage row cited)"
    lo, hi = stg[0], stg[1]
    return "covers the -33 C and +71 C storage margins" if lo <= MARGINS["storage_min"] and hi >= MARGINS["storage_max"] else \
        "does NOT cover the storage margins (-33 to +71 C): %s to %s C printed" % (lo, hi)


def fmt_price(ladder):
    if not ladder: return "NOT READ (no ladder in the answer)"
    first = ladder[0]; ten = next((p for q, p in ladder if q == 10), None)
    return "USD %.4f at %s, %s" % (first[1], first[0], ("USD %.4f at 10" % ten) if ten is not None else "no 10-piece row")


def catalogue():
    lcsc = json.load(open(os.path.join(TOP, LCSC_READING), encoding="utf-8"))
    jlc = json.load(open(os.path.join(TOP, JLC_READING), encoding="utf-8"))
    sam = json.load(open(os.path.join(TOP, SAMSUNG_READING), encoding="utf-8"))
    rows = {r["code"]: r for r in lcsc["rows"]}
    jrows = {}
    for s in jlc["searches"]:
        for r in s["rows"]: jrows.setdefault(r["code"], r)
    return rows, jrows, jlc, sam


def designators_added(apply_rel):
    """The designators a draft ADDS to a generator: every r(...), c(...), ic(...), nfet(...) or part(...) call whose first argument
    is a literal designator inside the draft's string constants, read by PARSING the draft (ast), never by grepping its prose."""
    tree = ast.parse(open(os.path.join(TOP, apply_rel), encoding="utf-8").read())
    out = set()
    rx = re.compile(r"\b(?:r|c|ic|nfet|pfet|part)\(\\?\"([A-Z_]+\d+)\\?\"")
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.update(rx.findall(n.value))
    return out


def reserved_refs(apply_rel, name="RB_REFS"):
    """A module-level tuple of designators a draft reserves (L4-E8's RB_REFS), read by ast."""
    tree = ast.parse(open(os.path.join(TOP, apply_rel), encoding="utf-8").read())
    for n in tree.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in n.targets):
            return set(ast.literal_eval(n.value))
    return set()


def inp_line_from_out(rel):
    """The INP row of L4-E7's rating table (RECORD, pinned), as set 27 prints it: 'U21's INP (R96 over R97, both at 0.1 %)  18.2878 of
    18.0000, margin -0.2878; holds from 3.58 uH'. Returns (value, line, tolerance in percent or None, margin, holds-from text)."""
    for line in open(os.path.join(TOP, rel), encoding="utf-8"):
        m = re.search(r"U21's INP \(R96 over R97(?:, both at ([0-9.]+) %)?\)\s+(-?[0-9.]+) of\s+(-?[0-9.]+), margin\s+(-?[0-9.]+); holds from (.+?)\s*$", line)
        if m: return float(m.group(2)), float(m.group(3)), (float(m.group(1)) if m.group(1) else None), float(m.group(4)), m.group(5)
    die(3, "the INP line is not in %s" % rel)


def _need(rx, text, what, flags=0):
    m = re.search(rx, text, flags)
    if not m: die(3, "%s is not in %s" % (what, L4["l4e7_out"]))
    return m


def l4e7_figures():
    """Every L4-E7 figure this record states, PARSED from L4-E7's own output and guard draft (never re-typed): the rating table at
    round 2's reference loop, the guard's thresholds, the step's turn-off, the cold connection's ring, and the divider parts the draft
    names. Returns a dict of the figures and of the placeholders they fill in PARTS."""
    raw = open(os.path.join(TOP, L4["l4e7_out"]), encoding="utf-8").read()
    t = " ".join(raw.split())
    F = {}
    loop = _need(r"THE DRAFTED NETWORK \(A\) AT ([0-9.]+) uH", raw, "the rating table's reference loop")
    F["loop"] = float(loop.group(1))
    rows = {}
    for m in re.finditer(r"^\s+- (.+?)\s{2,}(-?[0-9.]+) (?:of|against)\s+(-?[0-9.]+), margin\s+(-?[0-9.]+); holds from (.+?)\s*$", raw[loop.start():], re.M):
        if m.group(1) not in rows: rows[m.group(1)] = (float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))
    F["rows"] = rows
    def row(prefix):
        k = [x for x in rows if x.startswith(prefix)]
        if len(k) != 1: die(3, "the rating table has %d rows starting %r" % (len(k), prefix))
        return rows[k[0]]
    F["pvf"], F["q12_vds"], F["pvp"], F["trkvs"] = row("PV_F (U21's VS"), row("Q12's VDS"), row("PV_P (bulk"), row("TRK_VS (C71")
    F["inp"] = inp_line_from_out(L4["l4e7_out"])
    F["inp_on"] = float(_need(r"U21 turns on at ([0-9.]+) V at the most", t, "U21's turn-on").group(1))
    ov = _need(r"The cut-off rises at ([0-9.]+) V at the least and falls back at ([0-9.]+) V at the least, .*? its highest, ([0-9.]+) V", t, "the guard's OV band")
    F["ov"] = tuple(float(ov.group(i)) for i in (1, 2, 3))
    st = _need(r"a reference loop only: Q12 turns off at most ([0-9.]+) A within ([0-9.]+) us, PV_F at most ([0-9.]+) V", t, "the step's turn-off")
    F["q12_off"] = (float(st.group(1)), float(st.group(2)))
    ring = _need(r"The connection's ring .*?PV_F at most ([0-9.]+) V, its slew ([0-9.]+) V/us of ([0-9.]+), INP ([0-9.]+) V", t, "the cold connection's ring")
    F["ring"] = dict(pvf=float(ring.group(1)), slew=float(ring.group(2)), inp=float(ring.group(4)))
    basis = _need(r"RECOMMENDED operating row for VS, CS\+ and CS- is ([0-9.]+) V \(SLUSEE5E ([0-9.]+)\), which the ([0-9.]+) V at round 2's reference loop exceeds by ([0-9.]+) V: (OPEN on the guard)", t, "PV_F's basis")
    F["pvf_basis"] = dict(row=float(basis.group(1)), section=basis.group(2), value=float(basis.group(3)), over=float(basis.group(4)), state=basis.group(5))
    F["cs101"] = float(_need(r"under CS101 the input reaches ([0-9.]+) V at most", t, "CS101's input peak").group(1))
    F["d4_cs116"] = float(_need(r"D4 \(SMCJ30A\) at the disturbance's current ([0-9.]+) V", t, "D4 at CS116's current").group(1))
    d11 = _need(r"D11 clamps the port: at 10 A at the hot end ([0-9.]+) V \(5 A, ([0-9.]+) V\).*?D11 takes at most ([0-9.]+) mJ", t, "D11's CS116 row")
    F["d11"] = dict(v10=float(d11.group(1)), v5=float(d11.group(2)), cs116=float(d11.group(3)),
                    ring=float(_need(r"The connection's ring .*?D11 at most ([0-9.]+) mJ", t, "D11 at the ring").group(1)))
    d11s = _need(r"D11 ([0-9.]+) A and ([0-9.]+) mJ against ([0-9.]+) mJ", t, "D11 at the step")
    F["d11"].update(step=float(d11s.group(2)), lim=float(d11s.group(3)))
    F["trip"] = float(_need(r"the trip's highest,? ([0-9.]+) A", t, "the trip's highest current").group(1))
    F["basis_round"] = _need(r"PV_F'S BASIS \(round ([0-9]+), L6P-F10\)", t, "PV_F's basis round").group(1)
    F["inp_rounds"] = _need(r"THE INP DIVIDER \((rounds? [0-9]+(?: and [0-9]+)?), L6P-F04\)", t, "the INP divider's rounds").group(1)
    g = open(os.path.join(TOP, L4["l4e7_guard"]), encoding="utf-8").read()
    for ref in ("R96", "R97"):
        m = re.search(r'r\("%s", "([^"]*)"' % ref, g)
        if not m: die(3, "the guard draft carries no %s call" % ref)
        mm = re.search(r"(YAGEO) (RT\w+)", m.group(1)); tol = re.search(r"\b([0-9.]+)%", m.group(1))
        F[ref] = dict(value=m.group(1), maker=mm.group(1) if mm else "not named", mpn=mm.group(2) if mm else "none", tol=float(tol.group(1)) if tol else None)
    v, line, tol, margin, holds = F["inp"]
    ph = {"LOOP": "%.2f" % F["loop"], "PVF_REF": "%.2f" % F["pvf"][0], "PVF_RING": "%.1f" % F["ring"]["pvf"],
          "PVF_RING_ABS": "%.1f" % (100.0 - F["ring"]["pvf"]), "PVF_OVER_REC": "%.2f" % F["pvf_basis"]["over"],
          "PVF_REF_PCT": "%.0f" % F["pvf"][0], "PVF_RING_PCT": "%.0f" % F["ring"]["pvf"],
          "OV_RISE": "%.2f" % F["ov"][0], "OV_FALL": "%.2f" % F["ov"][1], "OV_HIGH": "%.2f" % F["ov"][2],
          "INP_ON": "%.2f" % F["inp_on"], "INP_TOL": "%g" % tol if tol is not None else "an unstated", "INP_REF": "%.4f" % v,
          "INP_RING": "%.2f" % F["ring"]["inp"], "INP_RING_ABS": "%.2f" % (20.0 - F["ring"]["inp"]),
          "INP_OVER": "%.2f" % (max(v, F["ring"]["inp"]) - line), "INP_REF_OVER": "%.4f" % (v - line), "INP_REF_ABS": "%.4f" % (20.0 - v), "INP_HOLDS": holds,
          "Q12_VDS": "%.2f" % F["q12_vds"][0], "Q12_VDS_PCT": "%.0f" % F["q12_vds"][0], "Q12_OFF_A": "%.1f" % F["q12_off"][0], "Q12_OFF_US": "%.1f" % F["q12_off"][1],
          "PVP": "%.2f" % F["pvp"][0], "PVP_PCT": "%.0f" % (F["pvp"][0] / 50.0 * 100), "TRKVS": "%.2f" % F["trkvs"][0], "TRKVS_PCT": "%.0f" % (F["trkvs"][0] / 50.0 * 100),
          "R97_MAKER": F["R97"]["maker"], "R97_MPN": F["R97"]["mpn"], "R96_MPN": F["R96"]["mpn"], "INP_ROUNDS": F["inp_rounds"],
          "CS101_PEAK": "%.2f" % F["cs101"], "D4_CS116": "%.2f" % F["d4_cs116"], "D11_10A": "%.2f" % F["d11"]["v10"], "D11_5A": "%.2f" % F["d11"]["v5"],
          "D11_CS116_MJ": "%.1f" % F["d11"]["cs116"], "D11_RING_MJ": "%.1f" % F["d11"]["ring"], "D11_STEP_MJ": "%.1f" % F["d11"]["step"], "D11_LIM_MJ": "%.0f" % F["d11"]["lim"],
          "TRIP_A": "%.3f" % F["trip"], "RS_ALL_W": "%.3f" % (F["trip"] ** 2 * 0.014), "RS_EACH_W": "%.3f" % (F["trip"] ** 2 * 0.014 / 5)}
    F["placeholders"] = ph
    return F


_FILLED = []


def fill_parts():
    """Fill the PARTS fields that state an L4-E7 figure from l4e7_figures() (once). A placeholder left unfilled refuses (exit 3)."""
    if _FILLED: return _FILLED[0]
    F = l4e7_figures()
    def sub(x):
        if isinstance(x, str):
            for k, v in F["placeholders"].items(): x = x.replace("<<%s>>" % k, str(v))
            if "<<" in x: die(3, "an L4-E7 figure is not filled: %s" % x[x.index("<<"):x.index("<<") + 40])
            return x
        if isinstance(x, (list, tuple)): return type(x)(sub(y) for y in x)
        return x
    for p in PARTS:
        for k in list(p):
            p[k] = sub(p[k])
    texts = {k: open(os.path.join(TOP, L4[k]), encoding="utf-8").read() for k in ("l4e7_guard", "l4e7_backstop")}
    for p in PARTS:
        for k, txt in texts.items():
            if k not in (p.get("draft") or "") or "re-read at set 28" not in (p.get("provisional") or ""): continue
            names = [p["mpn"].split(" (")[0]] + list(p.get("codes") or [])
            if not any(n and n in txt for n in names):
                die(3, "%s: %s no longer names %s (re-read the selection)" % (p["id"], L4[k], " or ".join(n for n in names if n)))
    _FILLED.append(F)
    return F


# ---------------------------------------------------------------------------------------------------- the findings (computed or read)
def findings(rows, jrows, sam):
    F = []
    # F01 the designator collision between L4-E8's ballasts and L4-E11's eFuse resistor (both drafts for board A's generator)
    bank = reserved_refs(L4["l4e8_bank"]); charger = designators_added(L4["l4e11_charger"])
    both = sorted(bank & charger)
    F.append(("L6P-F01", "DESIGNATOR COLLISION, board A: L4-E8's bank draft reserves %s for the ballasts (RB_REFS, apply_gen_sch_a_bank.py, 'R221 to R226 must be unused') "
              "and L4-E11's charger draft names R221 for U42's ILIM resistor among the designators it adds (apply_gen_sch_a_charger.py: 'if another draft takes them first, renumber'); the common designator(s), read by parsing both drafts: %s. "
              "Whichever applies second refuses or renumbers, so the two drafts cannot both be applied as written. AFFECTS: register R-07 (the bank, order 3f) and R-157 / R-181 (E11-27, the charger and eFuse). "
              "Remedy: L4-E11's R221 renumbered (R-181's text and apply_gen_sch_a_charger.py), a Layer 4 edit this record does not make."
              % (", ".join(sorted(bank)), ", ".join(both) or "none (the collision is resolved)"), bool(both)))
    # F02 the battery FET's fitted code is a suffix the sheet does not print
    st = doc_state("buk6y10")
    if st == "READ":
        px = PI.find_pages(os.path.join(TOP, DOCS["buk6y10"][0]), "BUK6Y10-30PX"); p = PI.find_pages(os.path.join(TOP, DOCS["buk6y10"][0]), "BUK6Y10-30P", limit=1)
        F.append(("L6P-F02", "IDENTITY, board A Q39 and Q40: the fitted code C3278350 resolves to BUK6Y10-30PX (LCSC and JLCPCB, LFPAK-56, stock %s); Nexperia's sheet prints BUK6Y10-30P (pages %s) and never "
                  "BUK6Y10-30PX (pages %s); its ordering table (p.2) names the type without a suffix. The X is INFERRED to be a packing code. AFFECTS: E11-27 (R-157) and E11-32 (R-162): the identity "
                  "stays PART_NUMBER_INFERRED until Nexperia's packing-code legend is filed or Q-NXP-1 carries the question."
                  % (rows.get("C3278350", {}).get("stock"), p, px), not px))
    # F03 part numbers decoded from a numbering scheme, not printed (rule D-2)
    dec = []
    for pid, key, mpn in (("L6P-05", "ds13012", "B540C-13-F"), ("L6P-06", "hojlr", "HoJLR2512-3W-8mR-1%"), ("L6P-07", "hojlr", "HoJLR2512-3W-12mR-1%"),
                          ("L6P-08", "hojlr", "HoJLR2512-3W-5mR-1%"), ("L6P-09", "hojlr", "HoJLR2512-3W-45mR-1%"), ("L6P-21", "wsl", "WSL2512R0700FEA")):
        if doc_state(key) == "READ" and not PI.find_pages(os.path.join(TOP, DOCS[key][0]), mpn, limit=1): dec.append("%s %s" % (pid, mpn))
    F.append(("L6P-F03", "IDENTITY (rule D-2): six selections rest on sheets that print a numbering scheme and not the part number: %s. Each is PART_NUMBER_INFERRED in the identity block; "
              "the next action is a DECODED scheme in part_identities.SCHEMES for Milliohm's HoJLR, Vishay's WSL and Diodes' B5xxC-13-F patterns (a tool change, Layer 6 tools), which would bind them "
              "DECODED as the Yageo and Uniroyal resistors are. AFFECTS: R-04, R-01, R-06, R-07, R-21, R-157 (no circuit change)." % ("; ".join(dec) or "none"), bool(dec)))
    # F04 the INP divider's tolerance and L4-E7's own INP reading (PARSED from its output and its guard draft)
    FG = fill_parts()
    vinp, line, tol, imargin, iholds = FG["inp"]
    r96, r97 = 100.0, 28.0
    nom = r97 / (r96 + r97)
    def ratio(t): return (r97 * (1 + t)) / (r96 * (1 - t) + r97 * (1 + t))
    t_rec = (tol or 0.0) / 100.0
    v_nom = vinp * nom / ratio(t_rec); v_1pc = v_nom * ratio(0.01) / nom
    agree = tol is not None and FG["R96"]["tol"] == tol and FG["R97"]["tol"] == tol
    F.append(("L6P-F04", "TOLERANCE, board E R96 and R97: L4-E7's %s put both divider resistors at %s percent in its record and in the guard draft (%s: R96 '%s', %s; R97 '%s', %s); "
              "its rating table reads INP at %.4f V against its %.4f V line (10 percent under the TPS4811-Q1's 20 V absolute maximum on INP, SLUSEE5E p.7), margin %.4f V, at round 2's %.2f uH "
              "reference loop (the line holds from %s), and %.2f V at the cold connection's ring. COMPUTED from that reading: the divider at nominal gives %.4f V, and at 1 percent (the draft's "
              "tolerance before %s) %.4f V. The tolerance question is answered (the draft and the record agree: %s); INP over its own margin line, inside the absolute maximum by %.2f V at "
              "worst, is L4-E7's open item on the guard (R-176 row 3, B6-ENG-1), not this record's. AFFECTS: R-173 (the guard draft's R96 and R97 now name YAGEO %s and %s, codes owed)."
              % (FG["inp_rounds"], tol, L4["l4e7_guard"], FG["R96"]["value"].split(" (")[0], FG["R96"]["mpn"], FG["R97"]["value"].split(" (")[0], FG["R97"]["mpn"], vinp, line, imargin, FG["loop"], iholds, FG["ring"]["inp"], v_nom, "round " + re.findall(r"[0-9]+", FG["inp_rounds"])[0], v_1pc,
                 "yes" if agree else "NO", 20.0 - max(vinp, FG["ring"]["inp"]), FG["R96"]["mpn"], FG["R97"]["mpn"]), not agree))
    # F05 catalogue: stock below the five-kit need, codes the drafts do not carry, and the two stock pools
    short = []
    for p in PARTS:
        need = p["need_per_kit"] * KITS
        for c in p["codes"][:1]:
            r = rows.get(c) or {}
            if r.get("stock") is not None and r["stock"] < need:
                j = jrows.get(c, {}).get("stock")
                short.append("%s %s (%s): LCSC %s against a need of %d for %d kits%s" % (p["id"], r.get("model"), c, r["stock"], need, KITS, (", JLCPCB's assembly stock %s" % j) if j is not None else ""))
    F.append(("L6P-F05", "AVAILABILITY (readings of 2 October 2026, true at their time only): %s. AFFECTS: E11-32 (R-162) for the charger; the Samsung rows R-173; PROCUREMENT.md section 8 carries the table." % ("; ".join(short) or "every first code read covers the five-kit need"), bool(short)))
    uncoded = [("TPS16630PWPR", "C1849461", "E11-27 / R-181"), ("SMCJ30A (Littelfuse)", "C224048", "R-173"), ("CL32B225KCJSNNE", "C55151", "R-173"), ("CL32B106KBJNNNE", "C138687", "R-173, R-21")]
    F.append(("L6P-F06", "CODES THE DRAFTS OWE: %s. Each code is a catalogue reading made here (inputs/), not a selection; the generator edit is Layer 8's with the draft."
              % "; ".join("%s: the draft carries no LCSC code, %s reads it (%s)" % (m, c, row) for m, c, row in uncoded), True))
    # F07 the charger's recommended junction minimum equals the envelope floor
    F.append(("L6P-F07", "GRADE AT_LIMIT, board A U3: SLUSE65A's recommended operating junction temperature is -20 to 125 C (p.9), its electrical table is characterised over TJ -40 to +125 C (p.9) and Tstg "
              "is -55 to 150 C (p.8); the envelope's in-use floor is -20 C, so the recommended row is met with no margin at the cold end (the drawn BQ25731 prints the same row). No requirement is "
              "unmet; recorded for TEST-PLAN E4-O (the cold start, E11-23 / R-137). AFFECTS: none (information for the bench rows).", True))
    # F08 Samsung's pages print no temperature range
    nt = [p["part"] for p in sam["pages"] if not p.get("prints_a_temperature_range")]
    F.append(("L6P-F08", "GRADE NOT READ, board E's Samsung ceramics (%s): the maker's specification pages print capacitance, tolerance, rated Vdc, TCC and dimensions and no temperature range; X7R's "
              "-55 to +125 C is the EIA class, not a reading. AFFECTS: R-173 (the guard's capacitor set; re-read at set 28: L4-E7's guard draft still names them); next action: Samsung's MLCC catalogue filed." % ", ".join(nt), bool(nt)))
    # F09 R19 / R87's code resolves to another Milliohm series than the held sheet
    m = (rows.get("C2985708") or {}).get("model") or "NOT READ"
    hollr_held = any("hollr" in f.lower() for f in os.listdir(os.path.join(TOP, "v2", "vendor", "passives")))
    F.append(("L6P-F09", "DOCUMENT OWED, board E R19 and R87: the code C2985708 resolves to %s, Milliohm's HoLLR2512 series; the tree holds the HoJLR2512 series sheet only (%s), so the "
              "'3W 50ppm' the drafts state is the catalogue's description. AFFECTS: E11-01 (R-123) and R-173; next action: the HoLLR2512 sheet fetched from LCSC's link for C2985708 and read."
              % (m, "a HoLLR sheet is held" if hollr_held else "no HoLLR sheet held"), not hollr_held))
    # F10 the guard's VS excursion against the 80 V operating row, as L4-E7's output now states its basis (PARSED)
    FG = fill_parts()
    b = FG["pvf_basis"]
    F.append(("L6P-F10", "RATING BASIS, board E U21 and Q12: L4-E7's output (round %s, answering this finding) states the basis: the 100 V absolute maximum less 10 percent is an exclusion "
              "line only (the project's rule since L4-E12's B2), and the TPS4811-Q1's RECOMMENDED operating row for VS, CS+ and CS- is %.0f V (SLUSEE5E %s), which PV_F's %.2f V at round 2's "
              "%.2f uH reference loop exceeds by %.2f V: %s. PV_F reads %.2f V of the 90 V line (margin %.2f V) in the rating table and %.1f V at the cold connection's ring over the envelope. "
              "The question of basis is answered; the excursion over the recommended row is L4-E7's open item (R-176 row 3, B6-ENG-1). AFFECTS: R-173, R-176 row 3; no change is made here."
              % (FG["basis_round"], b["row"], b["section"], b["value"], FG["loop"], b["over"], b["state"], FG["pvf"][0], FG["pvf"][2], FG["ring"]["pvf"]), False))
    # F11 the ruled cell's own rows against the envelope (information: L4-E10's result and the envelope's carve-out, nothing new)
    v = verdict(-10, 60)
    F.append(("L6P-F11", "GRADE %s at the cell's own rows, the pack's INR18650-35E: discharge -10 to 60 C and charge 0 to 45 C at the cell surface (Ver. 1.1 p.3) against the envelope's -20 C "
              "floor; pcb_envelope.yaml carries the carve-out (below -10 C the pack is warmed by its heater mat before charge; discharge continues to the cells' own -10 C surface limit) and L4-E10 "
              "judges the margin rows (LO-01d to LO-01g) unsuitable on published evidence, which U-01 carries. Information only: no row moves here. AFFECTS: none new (R-47, R-103, U-01 as recorded)." % v, v == "OUTSIDE"))
    return F


# ---------------------------------------------------------------------------------------------------- the identity block (for pcb_part_identities.yaml)
def identity_block():
    fill_parts()
    rowsc, jrows, _, _ = catalogue()
    out = []
    for p in PARTS:
        st, rc, reason, nxt = p["identity"]
        ident = dict(status=st, maker=p["maker"], mpn=p["mpn"].split(" (")[0])
        if p["doc"]:
            key, pg, binding = p["doc"]
            rel, doc_id, rev, url, pinned, held = DOCS[key]
            ds = dict(path=rel, sha256=pinned or sha256(rel), page=pg, binding="PRINTED" if binding == "PRINTED" else "DECODE_NOTE", doc_id=doc_id, revision=rev)
            if held: ds.update(held_back=True, fetch=FETCH)
            ident["datasheet"] = ds
        if st == "UNRESOLVED":
            ident.update(reason_class=rc, reason=reason, next_action=nxt)
        codes = {}
        if p["codes"]:
            c = p["codes"][0]; r = rowsc.get(c) or {}
            codes = dict(code=c, route="the Layer 4 draft's LCSC field, or this record's catalogue reading where the draft carries none",
                         read="LCSC %s: %s, %s, %s, stock %s" % (r.get("read_utc"), r.get("model"), r.get("brand"), r.get("package"), r.get("stock")))
        out.append(dict(id=p["id"], board=p["board"], refs=p["refs"], draft=p["draft"], selected_by=p["selected_by"], identity=ident, order_code=codes,
                        provisional=p["provisional"] or "no", record="v2/docs/records/l6pwr/L6-POWER-PARTS.md"))
    block = dict(drafted_identities_l4_power=dict(
        what="The identities of the parts Layer 4 selected for the power design (L4-E5 to L4-E11), recorded by the Layer 6 record l6pwr (3 October 2026). These parts exist "
             "only in release-guarded drafts on no committed netlist, so they are no `selections` and part_identities.py check does not read them; test_l6pwr.py reads this block "
             "(rule D-2 on every RESOLVED binding where the document is present). When Layer 8 applies a draft and the table is re-derived, each row becomes a selection and leaves this block.",
        taken_by="MESHSAT-1357 Layer 6 record l6pwr, 3 October 2026, on the integration candidate fnd/l4e9 at 2c240414",
        authority="SESSION, under the owner's standing rule of 26 September 2026: identities and sources recorded, nothing reselected; reverse by removing the block (apply_part_identities_block.py --remove)",
        rendered_by="v2/docs/records/l6pwr/l6pwr_parts.py --identities",
        rows=out))
    return block


# ---------------------------------------------------------------------------------------------------- main
def main(argv):
    import yaml
    if "--identities" in argv:
        sys.stdout.write("# ADDED 3 October 2026 (MESHSAT-1357, Layer 6 record l6pwr). Outside `selections:` on purpose (see `what`). Rendered by l6pwr_parts.py --identities;\n"
                         "# build_table.py does not carry this block: re-apply it with v2/docs/records/l6pwr/apply_part_identities_block.py after a regeneration.\n")
        sys.stdout.write(yaml.safe_dump(json.loads(json.dumps(identity_block())), sort_keys=False, allow_unicode=False, width=140))
        return 0
    fill_parts()
    P = print
    P("L6: THE COMPONENT IDENTITIES OF THE PARTS LAYER 4 SELECTED FOR THE POWER DESIGN (l6pwr_parts.py, MESHSAT-1357, 3 October 2026).")
    P("PROTOTYPE DESIGN: nothing bought, built, powered or measured. The parts are Layer 4's selections in release-guarded drafts on no committed")
    P("netlist; this record records and sources them and reselects nothing. Basis per figure: MAKER (document, revision, page, read here by")
    P("pdftotext), RECORD (a Layer 4 record's figure, its page pinned), CATALOGUE (a dated public reading in inputs/), COMPUTED (shown).")
    P()
    P("0. THE PINS (sha256 of every input this record reads; a held-back sheet by the sha256 its fetch script pins)")
    for rel in [ENVELOPE, LCSC_READING, JLC_READING, SAMSUNG_READING, FETCH] + [L4[k] for k in sorted(L4)]:
        P("   %s %s" % (sha256(rel), rel))
    for key in sorted(DOCS):
        rel, doc_id, rev, url, pinned, held = DOCS[key]
        st = doc_state(key)
        if st == "UNREAD":
            P("   %s %s (held back, NOT FETCHED on this host: UNREAD; fetch with %s)" % (pinned, rel, FETCH))
        else:
            P("   %s %s%s" % (sha256(rel), rel, " (held back, fetched and matching its pin)" if held else ""))
    P()
    env = yaml.safe_load(open(os.path.join(TOP, ENVELOPE), encoding="utf-8"))
    iu = env["ambient_c"]["in_use"]; st3 = env["ambient_c"]["storage_3_months"]; wia = env["worst_inside_air_c"]["lid_closed"]
    qm = env["owner_rulings"]["qualification_margins_c"]
    if (iu["min"], iu["max"]) != ENV_IN_USE or (st3["min"], st3["max"]) != STORAGE_3M or wia != BOARD_AIR_MAX or \
            (qm["operating_max"], qm["storage_max"], qm["storage_min"]) != (MARGINS["operating_max"], MARGINS["storage_max"], MARGINS["storage_min"]):
        die(3, "pcb_envelope.yaml does not read as this record states: re-read it")
    P("1. THE ENVELOPE THE GRADES ARE JUDGED AGAINST (pcb_envelope.yaml, read back)")
    P("   in use %g to %g C ambient; the worst inside air, lid closed, %g C (the board air a part is judged against until T-H1); storage 3 months %g to %g C;" % (iu["min"], iu["max"], wia, st3["min"], st3["max"]))
    P("   the owner's qualification margins (D-02a): operate at +%d C, store at +%d C and %d C, survive and recover. Verdicts: INSIDE when the maker's" % (qm["operating_max"], qm["storage_max"], qm["storage_min"]))
    P("   operating row strictly covers -20 to 62.1 C; AT_LIMIT when it meets an end exactly; OUTSIDE otherwise; NOT READ when no row is read at the source.")
    P()
    rows, jrows, jlc, sam = catalogue()
    P("2. THE PARTS (one block each)")
    n_res = n_unres = 0; by_reason = {}
    for p in PARTS:
        st, rc, reason, nxt = p["identity"]
        if st == "RESOLVED": n_res += 1
        else:
            n_unres += 1; by_reason[rc] = by_reason.get(rc, 0) + 1
        P("   %s  board %s  %s" % (p["id"], p["board"], ", ".join(p["refs"])))
        P("      maker, MPN:     %s, %s" % (p["maker"], p["mpn"]))
        P("      package, land:  %s; %s" % (p["package"], p["land"]))
        P("      selected by:    %s" % p["selected_by"])
        P("      draft:          %s" % p["draft"])
        g = p["grade"]
        if g:
            op = g.get("op"); stg = g.get("stg")
            v = verdict(op[0], op[1]) if op else "NOT READ"
            P("      grade:          %s; operating %s to %s C (%s p.%s: '%s' %s) -> %s against -20 to 62.1 C" % (
                g["kind"], op[0], op[1], DOCS[op[2]][1], op[3], clean(op[4]), "printed" if cite_ok(op[2], op[3], op[4]) else ("UNREAD" if cite_ok(op[2], op[3], op[4]) is None else "NOT ON THE PAGE"), v))
            if op and cite_ok(op[2], op[3], op[4]) is False: die(4, "%s: the page does not print %r" % (p["id"], op[4]))
            if g.get("charge"):
                ch = g["charge"]; P("                      charge %s to %s C (p.%s) -> the envelope's cold end is reached by the heater mat (REQ-046)" % (ch[0], ch[1], ch[3]))
            if g.get("electrical"):
                e = g["electrical"]; P("                      electrical table over TJ %s to %s C (p.%s)" % (e[0], e[1], e[3]))
            if stg:
                ok = cite_ok(stg[2], stg[3], stg[4])
                if ok is False: die(4, "%s: the page does not print %r" % (p["id"], stg[4]))
                P("                      storage %s to %s C (p.%s): %s" % (stg[0], stg[1], stg[3], margins_covered(stg)))
            else:
                P("                      storage: %s" % margins_covered(None))
        else:
            P("      grade:          NOT READ at the source (%s)" % ("the maker's page prints no temperature range" if "Samsung" in p["maker"] else "no part named or no maker's document read"))
        for r in p["ratings"]: P("      rating used:    %s" % clean(r))
        if p["doc"]:
            key, pg, binding = p["doc"]; rel, doc_id, rev, url, pinned, held = DOCS[key]
            stt = doc_state(key)
            P("      document:       %s; %s; %s" % (doc_id, rev, url))
            P("                      %s sha256 %s%s" % (rel, (pinned or sha256(rel)), " (held back; %s)" % FETCH if held else ""))
            if stt == "UNREAD":
                P("                      rule D-2: UNREAD on this host (not fetched)")
            else:
                mpn_core = p["mpn"].split(" (")[0]
                ok, line = PI.names_part(page(key, pg), mpn_core)
                if binding == "PRINTED":
                    if not ok: die(4, "%s: page %d of %s does not print %s" % (p["id"], pg, rel, mpn_core))
                    P("                      rule D-2 PRINTED: p.%d prints %s: '%s'" % (pg, mpn_core, clean(line)))
                else:
                    P("                      rule D-2: p.%d prints the numbering scheme, not %s (%s); the identity is decoded, see the identity line" % (pg, mpn_core, "the part number is on the page after all" if ok else "confirmed: not printed"))
            for ck, cp, phrase in p["cites"]:
                r = cite_ok(ck, cp, phrase)
                if r is False: die(4, "%s: %s p.%d does not print %r" % (p["id"], DOCS[ck][0], cp, phrase))
                P("                      cited p.%d prints '%s': %s" % (cp, clean(" ".join(phrase.split())), "yes" if r else "UNREAD"))
        else:
            P("      document:       none bound (see the identity line)")
        for c in p["codes"]:
            r = rows.get(c) or {}
            j = jrows.get(c)
            P(clean("      catalogue:      %s = %s, %s, %s; LCSC stock %s%s; %s; min buy %s (read %s)" % (
                c, r.get("model"), r.get("brand"), r.get("package"), r.get("stock"), (", JLCPCB assembly stock %s" % j["stock"]) if j else "",
                fmt_price(r.get("price_usd")), r.get("min_buy"), r.get("read_utc"))))
        if not p["codes"]:
            P("      catalogue:      no LCSC code (%s)" % ("owner-side purchase; price indicators in L4-E10: USD 8.25 a cell (l3batt) for the 35E, NZ$ 238.72 a cell (SIMPOWER listing archived 2025-01-16) for the Saft" if "pack" in p["board"] else "the draft names a value only"))
        P("      need:           %d a kit, %d for %d kits" % (p["need_per_kit"], p["need_per_kit"] * KITS, KITS))
        P("      alternative:    %s" % p["alternative"])
        for o in p["obligations"]: P("      obligation:     %s" % o)
        P("      rationale:      %s" % p["rationale"])
        P("      provisional:    %s" % (p["provisional"] or "no"))
        if st == "RESOLVED":
            P("      identity:       RESOLVED (rule D-2 PRINTED on the page above)")
        else:
            P("      identity:       UNRESOLVED, %s: %s" % (rc, reason))
            P("                      next action: %s" % nxt)
        P()
    P("   identity count: %d parts; RESOLVED %d; UNRESOLVED %d (%s)" % (len(PARTS), n_res, n_unres, ", ".join("%s %d" % kv for kv in sorted(by_reason.items()))))
    P()
    P("3. THE CATALOGUE TABLE (LCSC public product detail, %s; JLCPCB public parts search for the uncoded rows; a stock figure is true at its time only)" % LCSC_READING)
    P("   %-11s %-26s %-28s %-18s %8s %8s  %s" % ("code", "model", "brand", "package", "LCSC", "JLCPCB", "price (USD at qty)"))
    for c in sorted(rows, key=lambda x: int(x[1:])):
        r = rows[c]; j = jrows.get(c)
        P(clean("   %-11s %-26s %-28s %-18s %8s %8s  %s" % (c, r.get("model"), r.get("brand"), r.get("package"), r.get("stock"), j["stock"] if j else "-", fmt_price(r.get("price_usd")))))
    P("   Samsung's pages (%s):" % SAMSUNG_READING)
    for s in sam["pages"]:
        pr = s.get("properties") or {}
        P(clean("   %-18s %s %s %s %s %s; prints a temperature range: %s; terms: %s" % (s["part"], pr.get("capacitance"), pr.get("tolerance"), pr.get("rated_vdc"), pr.get("tcc"), pr.get("size"), s.get("prints_a_temperature_range"), "; ".join(s.get("terms") or [])[:90])))
    P()
    P("4. FINDINGS (each computed or read here; a FINDING is recorded with the Layer 4 row it affects, never applied as a change)")
    for fid, text, stands in findings(rows, jrows, sam):
        P("   %s %s" % (fid, "STANDS" if stands else "does not stand on this tree"))
        P("      " + clean(text))
    P()
    P("5. THE LAYER 6 CRITERIA FOR THESE PARTS (LAYER-STATUS.md section 'Layer 6. Components', items 6.1, 6.2, 6.3, 6.6, 6.8)")
    P("   6.1 exact manufacturer, MPN, package and grade per fitted part: for the %d Layer 4 selections here, %d RESOLVED on a maker's page that prints the part" % (len(PARTS), n_res))
    P("       number (rule D-2), %d UNRESOLVED with their reason (PART_NUMBER_INFERRED %d on numbering-scheme sheets and Samsung's suffix, CHOICE_OWED %d value-only rows," % (n_unres, by_reason.get("PART_NUMBER_INFERRED", 0), by_reason.get("CHOICE_OWED", 0)))
    P("       DOCUMENT_OWED %d); grades read at the source for %d of them, NOT READ for %d. MOVED from OPEN toward PARTLY for the power parts: the block in pcb_part_identities.yaml holds them." % (
        by_reason.get("DOCUMENT_OWED", 0), sum(1 for p in PARTS if p["grade"]), sum(1 for p in PARTS if not p["grade"])))
    P("   6.2 supporting documents with revision, source and currency: %d makers' documents named with title, revision, URL and sha256; %d held back under their terms with one fetch" % (len(DOCS), sum(1 for d in DOCS.values() if d[5])))
    P("       script (fetch_held_back.py, the pins those of L4-E7, L4-E10 and L4-E11, every one fetched and matching on 3 October 2026); Samsung's three pages excerpted (date-stamped, not filed).")
    P("       MOVED: PARTLY, the power parts covered; the ZK sheet's URL and the 35E's maker copy stay owed.")
    P("   6.3 selection rationale recorded: one sentence per part pointing at its Layer 4 decision (%d of %d). MOVED to PARTLY for these parts (the passive majority of the boards is untouched)." % (len(PARTS), len(PARTS)))
    P("   6.6 procurement constraints and alternatives: dated LCSC and JLCPCB readings for %d codes, an alternative or NOT READ per part, the five-kit need against stock (finding L6P-F05);" % len(rows))
    P("       PROCUREMENT.md section 8 carries the table. MOVED to PARTLY for these parts.")
    P("   6.8 a current, versioned BOM with identity per board: NOT MOVED. These parts are on no committed BOM; their identities are staged for the Layer 8 regeneration.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
