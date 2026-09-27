#!/usr/bin/env python3
"""Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): its drafted edits to four pages, as one idempotent script that
applies to main e3aedb25, to the tree after fnd/r8int1, to 84e52461, to a8652172 (H1), and after board B's round 8 page
patches alike. Every edit is skipped when its result (or board B round 8's or the layer 6 closer's wording of the same
fact) is already there, and otherwise asserts that its anchor occurs exactly once. Text only. Which edits are in the
closer's own sections and which are outside them, with the reason for each outside one, is drafts/hc5/README.md.

  PANEL.md section 7 (owned): the supervisors' row to 0x34 to 0x36; the 0x68 row names the part the code buys; the open
      finding of the S-07 correction closed (board B round 8's wording); a paragraph on speed, pull-ups and the budget.
  PANEL.md section 3 (outside; resolves the heartbeat source, the layer 5 goal): GPIO10 to 12's row.
  PANEL.md section 1 (outside; reason: its Pass-throughs row sent the monitor's touch lead to B16, against SC-HF-06;
      hc5 review 2, blocking item 1): the row's monitor clause.
  ARCH-PCB-B-IOHA.md sections 6 and 10a (owned): the H743, the address block (board B round 8's wording), the PB1/PB2
      finding closed at 458b2873 with SC-HF-02 added, the 10a part text brought to 458b2873 (on a8652172 the layer 6
      closer's wording already carries the H743 sentences, so only the address block, the SC-HF-02 and FW-B08 sentences
      and 10a's per-controller part are edited there).
  feasibility/ZEROIZE.md Z-C3 (owned) and the three places that repeat its block (sections 2, 4 row E17, 9 item 8);
      section 3.4's "the kit bus clock is not declared anywhere" (outside; the clock is now declared, FW-K01).
  ASSEMBLY.md section 4 and build step 9 (outside; reason: SC-HF-06 gives the monitor's touch USB its board end, and the
      leads table's row named "a B16 slot hub header" with no designator, which the layer 5 audit lists as a
      contradiction, and build step 9 repeated "the slot hub header"; hc5 review 2, blocking item 1): that row and
      step 9's clause on the monitor's leads.
  ARCHITECTURE.md section 12 is not here: it is a whole-section replacement, drafts/hc5/apply_architecture.py.

Run from the repository root:  python3 drafts/hc5/apply_docs.py"""
import os, sys

ROOT = os.getcwd()
log = []
import hashlib
DOCS = ("v2/docs/PANEL.md", "v2/docs/ARCH-PCB-B-IOHA.md", "v2/docs/feasibility/ZEROIZE.md", "v2/docs/ASSEMBLY.md")
PRE = {rel: hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16] for rel in DOCS}


def edit(rel, pairs):
    """`marker` is None (the new text itself), one string, or a tuple of strings: the edit is skipped when any of them is
    in the file (a tuple names another stream's wording of the same fact, e.g. the layer 6 closer's on a8652172)."""
    p = os.path.join(ROOT, rel)
    s = open(p, encoding="utf-8").read()
    for old, new, marker in pairs:
        ms = marker if isinstance(marker, tuple) else (marker or new,)
        hit = [m for m in ms if m in s]
        if hit:
            log.append("%s already: %s" % (rel, hit[0].strip()[:60])); continue
        n = s.count(old)
        assert n == 1, "%s: anchor found %d times: %r" % (rel, n, old[:90])
        s = s.replace(old, new); log.append("%s edited: %s" % (rel, old.strip()[:60]))
    assert chr(0x2014) not in s and chr(0x2013) not in s, rel
    open(p, "w", encoding="utf-8").write(s)


CONTRACT = "`HW-FW-CONTRACT.md`"

# ---------------------------------------------------------------------------------------------------------- PANEL.md
edit("v2/docs/PANEL.md", [
    ("| 0x30, 0x31, 0x32 | the three STM32H743 I/O supervisors `U41`, `U51`, `U61`, I2C1 targets on PB6 and PB7 for status only (`ARCH-PCB-B-IOHA.md` section 6; the addresses are the supervisors' firmware) | B16 |",
     "| 0x34, 0x35, 0x36 | the three STM32H743 I/O supervisors `U41`, `U51`, `U61`, I2C1 targets on PB6 and PB7 for status only (`ARCH-PCB-B-IOHA.md` section 6; the addresses are the supervisors' firmware contract, I3-F01: never 0x30 to 0x32, never a master, never 0x60) | B16 |",
     "| 0x34, 0x35, 0x36 | the three STM32H743 I/O supervisors"),
    ("| 0x68 | DS3231M holdover clock (CR2032 backed) | B16 |",
     "| 0x68 | DS3231 holdover clock `U9` (CR2032 backed): the part its code C9866 buys is the DS3231SN#, which board B's round 8 draws on its own SO-16 land; the netlist at `e3aedb25` still names a DS3231MZ+ | B16 |",
     # r8int4: on 38dcd764 board B's round 8 (b76c18cb) states the same part in its own words, so the edit is skipped
     ("| 0x68 | DS3231 holdover clock `U9`", "| 0x68 | DS3231SN holdover clock U9")),
    ("so it is supervisor 1's address that has to move, in the supervisors' firmware; nothing is resolved here. Three firmware-bearing",
     "so it is supervisor 1's address that has to move, in the supervisors' firmware. **Closed 27 September 2026 as a firmware contract (I3-F01, board B round 8, the block `ARCHITECTURE.md` section 5.5 records):** the supervisors answer at 0x34, 0x35 and 0x36; the bus is unchanged, and the panel firmware never writes 0x30 except to address every TPS23861 at once. Three firmware-bearing",
     "**Closed 27 September 2026 as a firmware contract (I3-F01"),
    ("(firmware rule Z-C3 of `feasibility/ZEROIZE.md`, residual R7).\n",
     "(firmware rule Z-C3 of `feasibility/ZEROIZE.md`, residual R7).\n\n"
     "**Speed, pull-ups and capacitance (27 September 2026, " + CONTRACT + " section 6).** The controller runs the bus in "
     "Standard-mode, 100 kHz programmed and at least 90 kHz achieved, the clock `feasibility/ZEROIZE.md`'s time budget holds "
     "at (FW-K01). The pull-ups are 2.2 k on B16 (`R54`, `R55`) and 2.2 k here (`R7`, `R8`), with the KSZ9897R's internal "
     "58 k: 2.94 mA at 0.4 V from the top of the 3.3 V tolerance, against the 3 mA the weakest targets are rated to sink at "
     "0.4 V (the minimum their datasheets state), so they "
     "cannot be made stronger, and no participant enables an internal pull-up (FW-K02). Four targets state a 300 ns rise at "
     "any clock (the BQ25731, the TPS23861, the ATECC608B and board D's round 8 ADS1115), and as one segment the bus cannot "
     "meet it: its pins and ribbons alone exceed the limit at their published maxima (finding HF-F01). The session took "
     "three segments behind two TCA9517A (SC-HF-02): A22's targets and D8's behind one on A22, the three supervisors, the "
     "PoE controller and the Ethernet switch behind one on B16 that this controller opens only for its own transactions to "
     "them and closes before every secure-element transaction (FW-K05). Owed on A22 and B16; until drawn, HF-F01 stands.\n",
     "**Speed, pull-ups and capacitance (27 September 2026"),
])
# PANEL.md section 3 (outside the owned section): the heartbeat source, resolved from the netlist
edit("v2/docs/PANEL.md", [
    ("| 10, 11, 12 | HB1, HB2, HB3 | heartbeat inputs, one per compute slot (a slot toggles its line at 1 Hz while its supervisor runs) |",
     "| 10, 11, 12 | HB1, HB2, HB3 | heartbeat inputs, one per compute slot: the slot's compute module toggles its line at 1 Hz from its GPIO16, through the level stage Q{s}05, while its bridge software runs; the three I/O supervisors listen on the same lines and drive none; a dark module leaves the line held high by B16's pull-up, so liveness is the toggle (" + CONTRACT + " section 2; corrected 27 September 2026 from \"while its supervisor runs\") |",
     None),
])

# ------------------------------------------------------------------------------------------------- ARCH-PCB-B-IOHA.md
# On a8652172 the layer 6 closer (hc6, 99cde56b) has already rewritten three of the places this script corrects (the
# section 6 part, 10a's pin-table sentence and 10a's D-13 sentence, all around v2/docs/parts/STM32H743-COMPATIBILITY.md)
# and headed the PB1/PB2 finding "CORRECTED at `458b2873`". Its wording carries the same facts, so those edits are
# skipped there (the tuple markers below), and the SC-HF-02 and FW-B08 sentences go after hc6's heading instead
# (c5, 27 September 2026). On e3aedb25 and 84e52461 the script edits as before.
_IOHA = open(os.path.join(ROOT, "v2/docs/ARCH-PCB-B-IOHA.md"), encoding="utf-8").read()
_SEG = (" The supervisors' firmware contract is " + CONTRACT + " FW-B08. **Added 27 September 2026 (SC-HF-02, " + CONTRACT
        + " section 6.5):** as one segment the kit bus cannot meet the 300 ns rise several of its targets require, so the"
        " three supervisors, with the PoE controller and the Ethernet switch, move behind a TCA9517A that the panel"
        " controller enables from U7 only for its own transactions to them (owed on the generator); outside those windows"
        " the supervisors can neither see nor reach the secure element, which narrows `feasibility/ZEROIZE.md`'s R7 and does"
        " not replace Z-C3.")
_HC6_HEAD = "(`gen_sch_b.py:1138-1139`; DS12110 Rev 11 Table 10 p.90).**"
if _HC6_HEAD in _IOHA:
    _finding = (_HC6_HEAD + " The finding read:", _HC6_HEAD + _SEG + " The finding read:", "(SC-HF-02, " + CONTRACT + " section 6.5)")
else:
    _finding = ("**OPEN DESIGN FINDING, 26 September 2026: as generated, the supervisors cannot be I2C targets at all.**",
                "**CLOSED at `458b2873` (W5-F3); kept for the record: as generated before that commit, the supervisors could not be I2C targets at all.** Since `458b2873` SCL is PB6 (pin 92) and SDA PB7 (pin 93), I2C1 at AF4 (DS12110 Rev 10 Table 11; `gen_sch_b.py:1136-1140`), both FT_f; the supervisors' firmware contract is " + CONTRACT + " FW-B08. **Added 27 September 2026 (SC-HF-02, " + CONTRACT + " section 6.5):** as one segment the kit bus cannot meet the 300 ns rise several of its targets require, so the three supervisors, with the PoE controller and the Ethernet switch, move behind a TCA9517A that the panel controller enables from U7 only for its own transactions to them (owed on the generator); outside those windows the supervisors can neither see nor reach the secure element, which narrows `feasibility/ZEROIZE.md`'s R7 and does not replace Z-C3. The text as it stood:",
                "**CLOSED at `458b2873` (W5-F3); kept for the record")
edit("v2/docs/ARCH-PCB-B-IOHA.md", [
    ("**Three equivalent supervisors, `IOCTRL-A/B/C`, baseline 3x STM32H753.**",
     "**Three equivalent supervisors, `IOCTRL-A/B/C`, three STM32H743VIT6** (the part bought; owner ruling D-13 of 26 September 2026 accepted it, and the generator and the BOM read it since `458b2873`; the H753 was the baseline until then).",
     ("**Three equivalent supervisors, `IOCTRL-A/B/C`, three STM32H743VIT6**",
      "**Three equivalent supervisors, `IOCTRL-A/B/C`, 3x STM32H743VIT6**")),
    ("(each of them a slave at its own address, 0x30, 0x31 and 0x32, which are free in the map of section 8 of the repo handover)",
     "(each of them a slave at its own address, 0x34, 0x35 and 0x36; **corrected 27 September 2026, I3-F01:** this text said 0x30, 0x31 and 0x32, and 0x30 is the broadcast address every TPS23861 answers whatever its A3 pin, so the supervisors' firmware contract is 0x34 to 0x36, the block `ARCHITECTURE.md` section 5.5 records)",
     "(each of them a slave at its own address, 0x34, 0x35 and 0x36;"),
    _finding,
    ("**Per controller:** an STM32H753VITx in LQFP-100,",
     "**Per controller:** an STM32H743VIT6 in LQFP-100 (an STM32H753VITx in this build of 9 September),", None),
    ("The pin table is KiCad's own `STM32H753VITx` symbol, which cites\n`https://www.st.com/resource/en/datasheet/stm32h753vi.pdf`; the alternate-function choices, FDCAN1 on PD0/PD1 and FDCAN2\non PB12/PB13, are the classic H7 mappings and are to be confirmed against the datasheet's AF table before release.",
     "The pin table was KiCad's own `STM32H753VITx` symbol in this build; since `458b2873` it is read from ST's DS12110 Rev 10 for\nthe H743 (`gen_sch_b.py:286-287`): FDCAN1 on PD0/PD1 and FDCAN2 on PB12/PB13 (AF9), I2C1 on PB6/PB7 (AF4).",
     ("The pin table was KiCad's own `STM32H753VITx` symbol in this build;",
      "are the classic H7 mappings; confirmed in the STM32H743's own AF table")),
    ("accepted formally as the supervisor part. This text, the generator and the BOM still say STM32H753, so the\ncomponent mismatch is not closed by the ruling: it closes when the schematic text and the BOM are aligned to the\nH743 and netlist parity is shown again by a diff, and neither has been done yet.",
     "accepted formally as the supervisor part. Since `458b2873` the schematic text and the BOM read STM32H743VIT6 and pin\nparity is 100 of 100 on both parts (`v2/docs/records/r4b/pin_parity.py`, RECORDED); owner condition 1 is still not\nclosed by the text, because the firmware and build evidence that would prove compatibility do not exist (S-41).",
     ("accepted formally as the supervisor part. Since `458b2873` the schematic text and the BOM read STM32H743VIT6",
      "The generator and the BOM were aligned to the H743 and netlist parity shown again at `458b2873`")),
])

# ------------------------------------------------------------------------------------------------------- ZEROIZE.md
edit("v2/docs/feasibility/ZEROIZE.md", [
    ("be set to master. The architecture makes the supervisors targets at 0x30, 0x31 and 0x32 on a bus \"which the panel",
     "be set to master. The architecture makes the supervisors targets at 0x34, 0x35 and 0x36 (0x30 to 0x32 until 27 September\n2026: 0x30 is the TPS23861's broadcast address, I3-F01) on a bus \"which the panel", None),
    ("targets at 0x30 to 0x32 (`ARCH-PCB-B-IOHA.md:96`), never sets its I2C controller to master mode, never drives SCL,",
     "targets at 0x34 to 0x36 (`ARCH-PCB-B-IOHA.md` section 6; " + CONTRACT + " FW-B08; never at 0x30 to 0x32, where the\n  TPS23861's broadcast address sits, I3-F01), never sets its I2C controller to master mode, never drives SCL,", None),
    ("the architecture makes them I2C targets at 0x30 to 0x32 on a bus the panel masters",
     "the architecture makes them I2C targets at 0x34 to 0x36 (0x30 to 0x32 until 27 September 2026, I3-F01) on a bus the panel masters", None),
    ("8. Write firmware rule Z-C3 into the supervisor firmware's requirements: I2C target at 0x30 to 0x32 only, never a\n   master, never address 0x60, under D-13's verified boot.",
     "8. Write firmware rule Z-C3 into the supervisor firmware's requirements: I2C target at 0x34 to 0x36 only (never 0x30 to\n   0x32, I3-F01), never a master, never address 0x60, under D-13's verified boot; written as " + CONTRACT + " FW-B08. Once\n   the session's three bus segments are drawn (SC-HF-02, " + CONTRACT + " section 6.5), the panel keeps the supervisors'\n   segment closed during every secure-element transaction (FW-K05), which narrows R7 and does not replace Z-C3.", None),
    ("The kit bus clock is not declared anywhere (TBD); the\nbudget assumes 100 kHz,",
     "The kit bus clock is declared since 27 September 2026: 100 kHz\nprogrammed, at least 90 kHz achieved (" + CONTRACT + " FW-K01), and this budget re-run at 90 kHz holds every pass line (worst case in\nspecification 0.825 s, step 5 by 1.504 s, longest transfer 6.72 ms; ibid. section 6.4). As first written, the\nbudget assumes 100 kHz,", None),
])

# ------------------------------------------------------------------------------------------ ASSEMBLY.md, the touch lead
edit("v2/docs/ASSEMBLY.md", [
    ("| Monitor touch USB | a B16 slot hub header | the Xenarc's USB lead | the monitor's own cable | PH at B16 |",
     "| Monitor touch USB (full speed, on board D's spare hub port: the session's choice SC-HF-06 of 27 September 2026, "
     "`HW-FW-CONTRACT.md` section 8, `pcb_interfaces.yaml` IF-MON; corrected from \"a B16 slot hub header\", which named no "
     "designator) | D8 `J_USB3` (PH 1x4: 5 V, D-, D+, GND) | the Xenarc's USB lead (a type A plug) | an adapter made up at "
     "build: a USB A receptacle to PH 1x4, 24 AWG, to the monitor's lead | PH at D8 |", None),
    # build step 9 (outside; reason: the same lead's board end, which step 9 still gave as "the slot hub header" on B16
    # after the row above was corrected; hc5 review 2, blocking item 1). D8 is on A22's standoffs from step 5, so the
    # lead reaches it at step 9, as the PA bias and headset leads of the same step do.
    ("the HDMI, USB touch and 12 V leads of the monitor below the plate to B16 `J_HDMI`, the slot hub header and A22 `J_MON`;",
     "the HDMI, USB touch and 12 V leads of the monitor below the plate to B16 `J_HDMI`, D8 `J_USB3` (the touch lead through "
     "its USB A to PH 1x4 adapter, section 4; the session's choice SC-HF-06 of 27 September 2026, `HW-FW-CONTRACT.md` section 8) "
     "and A22 `J_MON`;", None),
])

# ------------------------------------------------------------------------------ PANEL.md section 1, the touch lead
# (outside the owned sections 3 and 7; reason: section 1's Pass-throughs row sent all three monitor leads to "B16 and
# A22", which contradicts SC-HF-06's board end for the touch lead; hc5 review 2, blocking item 1)
edit("v2/docs/PANEL.md", [
    ("the Xenarc 709GNK monitor's connector block (its HDMI, USB touch and 12 V leads go below the plate to B16 and A22),",
     "the Xenarc 709GNK monitor's connector block (its HDMI and 12 V leads go below the plate to B16 `J_HDMI` and A22 "
     "`J_MON`, its USB touch lead to D8 `J_USB3` through the adapter of `ASSEMBLY.md` section 4: the session's choice "
     "SC-HF-06 of 27 September 2026, " + CONTRACT + " section 8),", None),
])

# ------------------------------------------------------------------------------------------ the registry's bindings
# A requirement reading bound to one of these pages at the sha this script edited is re-read here and rebound, with a
# note that names what this script changed; each note was judged record by record against the sections the reading
# cites. A reading bound to another sha was stale before this script ran and is left to its owner (printed).
CHANGED = {
    "v2/docs/PANEL.md": "section 1's Pass-throughs row (the monitor's touch lead to D8 J_USB3, SC-HF-06), section 3's GPIO10 to 12 "
                        "row (the heartbeat source) and section 7's new paragraph on speed, pull-ups and the budget (its "
                        "supervisors' row at 0x34 to 0x36, its 0x68 row and the S-07 finding closed as I3-F01 were already board B's "
                        "round 8 text, b76c18cb, and are unchanged here)",
    "v2/docs/ARCH-PCB-B-IOHA.md": "sections 6 and 10a only (the address block, the corrected PB1/PB2 finding with the FW-B08 "
                                  "pointer and the segment choice SC-HF-02 added, and 10a's per-controller part; on a tree "
                                  "before 99cde56b also the supervisors' part in section 6 and 10a's two H743 sentences)",
    "v2/docs/feasibility/ZEROIZE.md": "the supervisors' address block only, in section 2, Z-C3 (section 3.1), row E17 of "
                                      "section 4 and section 9 item 8, and section 3.4's sentence on the bus clock (now declared, "
                                      "the budget re-run at 90 kHz holds)",
    "v2/docs/ASSEMBLY.md": "section 4's Monitor touch USB row and build step 9's clause on the monitor's leads only (the "
                           "touch lead's board end, D8 J_USB3, SC-HF-06)",
}
WHY = {
    "REQ-005": "sections 4, 15 and 15a and line 17, which this reading cites, are unchanged",
    "CFL-001": "sections 4, 15 and 15a and line 17, which this reading cites, are unchanged",
    "CFL-005": "section 7's panel-absent paragraph, which this reading cites, is unchanged",
    "CFL-016": "section 1 changes only in its Pass-throughs row (the monitor's leads, which this reading does not cite; its ZEROIZE and EMCON logic rows are unchanged), section 6 is unchanged, and section 7's bus table still lists the supervisors, the Ethernet switch, the PoE controller and board A's expanders from the SDA and SCL nets, now with the supervisors at their corrected block, so the resolution stands",
    "CFL-014": "section 10, which this reading cites, is unchanged",
    "CFL-015": "section 10, which this reading cites, is unchanged",
    "ASM-005": "sections 1 and 7 are unchanged and section 4 changed only in row E17's address block, so the documentary result stands",
    "FEA-001": "sections 1 and 7, which this reading cites, are unchanged; Z-C3 keeps its substance with the corrected address block",
}
# where one reading is bound to two of these pages, the note for the second names that page's own sections
WHY_BY_DOC = {
    ("CFL-015", "v2/docs/ASSEMBLY.md"): "section 4's Pack SMBus row and build step 7, which this reading cites, are unchanged",
    ("CFL-001", "v2/docs/PANEL.md"): "line 5 (bank 1's home and failover hosts) and section 2's ribbon table with its pin 15 "
                                     "row, which this reading rests on, are unchanged, and section 1 changes only in its "
                                     "Pass-throughs row (the monitor's leads), which this reading does not cite",
}
rp = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
r = open(rp, encoding="utf-8").read()
for rel in DOCS:
    post = hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]
    if post == PRE[rel]: continue
    old_b, new_b = "%s@%s" % (rel, PRE[rel]), "%s@%s" % (rel, post)
    def block(rid):
        st = r.index("\n  - id: %s\n" % rid)
        nx = r.find("\n  - id: ", st + 1)
        return st, (nx if nx != -1 else len(r))
    ids = [m.split("\n")[0] for m in r.split("\n  - id: ")[1:] if old_b in m.split("\n  - id: ")[0]]
    for rid in ids:
        st, en = block(rid)
        blk = r[st:en]
        if old_b not in blk: continue
        why = WHY_BY_DOC.get((rid, rel)) or (WHY.get(rid) if rel != "v2/docs/ASSEMBLY.md" else None)
        if not why:
            log.append("REBIND NOT DONE for %s on %s: no judged note in this script; re-read it by hand" % (rid, rel)); continue
        note = ("      - >-\n          %s re-read at the layer 5 closer's edit of 27 September 2026 (hc5-layer5): it changed %s; %s, "
                "so this reading stands on the file at %s\n" % (rel, CHANGED[rel], why, post))
        i_b = blk.index("    evidence_bound_to:")
        r = r[:st] + (blk[:i_b] + note + blk[i_b:]).replace(old_b, new_b) + r[en:]
        log.append("rebound %s on %s to %s" % (rid, rel, post))
assert chr(0x2014) not in r and chr(0x2013) not in r
open(rp, "w", encoding="utf-8").write(r)
print("\n".join(log))
