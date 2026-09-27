#!/usr/bin/env python3
"""Board A stream w3a (MESHSAT-1357, 27 September 2026): the document edits that go with the board A change. Drafts,
because the files are not w3a's: v2/docs/feasibility/EMCON.md (section 4a's +3V3 overvoltage paragraph and its
section 7 row), v2/docs/handover/ENGINEERING-QUESTIONS.md (EQ-17's and EQ-19's attempts), v2/docs/PANEL.md (U28's line
in the bus table). Each edit asserts the old text and that the new text differs.

Usage: python3 apply_docs.py <repo root>, BEFORE drafts/w3a/apply_registry.py: that script rebinds the registry
readings bound to PANEL.md (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016) and to EMCON.md (REQ-012, REQ-030, REQ-032,
REQ-071, CON-010, CON-021, FEA-002) to the files this one writes, and refuses while the tree still holds main's.
"""
import os, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")

EDITS = {
    "v2/docs/feasibility/EMCON.md": [
        ("""**A fault outside RF-002's named states: +3V3 overvoltage** (the independent check of 26 September 2026). The
SN74AUP1G08's absolute maximum VCC and VI are 4.6 V (SCES502Q 5.1 p.5), now the lowest rating on board A's +3V3,
beside D3, the SMBJ5.0A that clamps that rail and only starts to conduct at 6.40 to 7.00 V (VBR at 10 mA, MDD SMBJ
series, `v2/vendor/power/mdd-smbj-series-tvs.pdf`), and below the 6.5 V of the SN74LVC08A sections the gates replace.
A +3V3 overvoltage between 4.6 V and D3's clamp damages the EMCON gates first, and their output state after damage is
not stated. OPEN: a row in section 7 and in bench E-11; the options (a clamp at or under 4.6 V on board A's +3V3, or the
fault accepted with its bound) are the board A author's.""",
         """**A fault outside RF-002's named states: +3V3 overvoltage** (the independent check of 26 September 2026; EQ-17,
taken by board A stream w3a on 27 September 2026). The SN74AUP1G08's absolute maximum VCC, VI and VO are 4.6 V
(SCES502Q 5.1 p.5), and D3, the SMBJ5.0A on board A's +3V3, only starts to conduct at 6.40 to 7.00 V (VBR at 10 mA, MDD
SMBJ series, `v2/vendor/power/mdd-smbj-series-tvs.pdf`). CLOSED AT DESK (local): the four gates U35 to U38 run from
`+3V3_EMCON`, behind a TPS259631DDAR eFuse U39 whose overvoltage lockout cuts them off at 3.83 to 4.11 V of +3V3
(R211 23.2 k over R212 10 k; VOVLO(R) 1.17 to 1.22 V, tOVLO 1.3 us typical, TI SLVSET8A 7.5 and 7.6) and a 100 Ohm
filter R213 into their own 100 nF, with EN on `RAIL_EN`; and the two software holds reach the gates through U40, an
SN74LVC2G07 open-drain buffer rated 6.5 V (SCES308L 6.1), as `PA_HOLD` and `HF_HOLD` pulled up to `+3V3_EMCON`, so no
pin of the gates is driven from the +3V3 domain. For any +3V3 up to U39's 21 V IN rating the gates lose their supply,
their outputs fall, `PA_UVLO` and `HF_UVLO` go under VEN(STBY) and the PA and HF stages shut down for the duration of
the fault: the inhibited state. U39's fault line is `EMCON_EF_FLT` on U28 P1.2 (a firmware log item). Not closed by
this: the rest of +3V3 (the PCA9555s and INA226s at 6.0 V, the LVC parts at 6.5 V) against D3's 6.40 V, which is no
EMCON path; a registry open item. The bench item E-11 keeps a +3V3 overvoltage injection (the cut level and the gates'
supply during it). Choices in `v2/ecad/tools/gen_sch_a.py` (EQ-17, TAKEN) and the requirements registry."""),
        ("""| Board A's +3V3 overvoltage against the SN74AUP1G08's 4.6 V absolute maximum (round 8, section 4a) | D3 (SMBJ5.0A) starts to conduct at 6.40 to 7.00 V; between 4.6 V and that the EMCON gates are damaged first, their output after damage unstated; outside RF-002's named states | board A author (a clamp at or under 4.6 V, or the fault accepted with its bound); bench E-11 |""",
         """| Board A's +3V3 overvoltage against the SN74AUP1G08's 4.6 V absolute maximum (round 8, section 4a) | CLOSED at desk by board A stream w3a (27 September 2026, EQ-17): the gates' supply is cut by U39 at 3.83 to 4.11 V of +3V3 for any fault up to 21 V, and U40 keeps the +3V3 domain off their inputs; the rest of +3V3 against D3 is a registry open item, not an EMCON path | bench E-11 (a +3V3 overvoltage injection) |"""),
    ],
    "v2/docs/handover/ENGINEERING-QUESTIONS.md": [
        ("""| **Attempts and results** | Recorded OPEN in round 8; no change drawn. |""",
         """| **Attempts and results** | Recorded OPEN in round 8; no change drawn. TAKEN by board A stream w3a (27 September 2026): option (c). U35 to U38 run from `+3V3_EMCON` behind the eFuse U39 (TPS259631DDAR, overvoltage lockout at 3.83 to 4.11 V of +3V3, SLVSET8A) and a 100 Ohm filter, and the software holds reach them through U40 (SN74LVC2G07, open drain, 6.5 V) pulled up to the protected rail; (a) was refused because no clamp holds under 4.6 V at U12's 4.2 to 5.8 A, (b) because the SN74LVC1G08 is rated 6.5 V, inside D3's range, and undoes round 8's hold. Board A regenerated with parity; RF-002's walk on A prints the same verdicts before and after. The rest of +3V3 against D3 is a registry open item. |"""),
        ("""| **Attempts and results** | The rule's instrument changed in `940cbcdf`; no board's intent has been extended yet. |""",
         """| **Attempts and results** | The rule's instrument changed in `940cbcdf`; no board's intent has been extended yet. Board A done by stream w3a (27 September 2026): VMON, PRECHG, +3V3_EMCON_EF and +3V3_EMCON declared as rails, B33_BST, HT_BST, S1_BOOT, S3_BOOT, PD_VTX, PD_VAUX, PD_DVDD, PD_CC1 and PD_CC2 as nodes, each from its maker's sheet; PWR-001 on A's regenerated netlist reads PASS of 35 (34 declared rails, 0 undecided). B, D and E stay open. |"""),
    ],
    "v2/docs/PANEL.md": [
        ("""and `U28` (power-good lines, the USB-C outlet's software enable, the Glenair host port's VBUS switch and its fault, spares) | A22 |""",
         """and `U28` (power-good lines, the USB-C outlet's software enable, the Glenair host port's VBUS switch and its fault, the EMCON gates' supply fault `EMCON_EF_FLT` on P1.2, low when U39 has cut it on a +3V3 overvoltage, spares) | A22 |"""),
    ],
}

for rel, edits in EDITS.items():
    p = os.path.join(ROOT, rel)
    t = open(p, encoding="utf-8").read(); o = t
    for old, new in edits:
        if t.count(old) != 1: raise SystemExit("apply_docs: %s: the old text is not there once (%r...)" % (rel, old[:60]))
        assert new != old
        t = t.replace(old, new)
    assert t != o
    open(p, "w", encoding="utf-8").write(t)
    print("apply_docs: %s, %d edit(s)" % (rel, len(edits)))
