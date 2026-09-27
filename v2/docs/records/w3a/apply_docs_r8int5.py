"""r8int5 integration of board A stream w3a: its apply_docs.py re-derived on main 953f5658 plus the w3t commit, with
the independent checks' wording corrections (w3a check 1 and check 2 minors): the EQ-17 closure is stated with its
tOVLO bound, option (c) is recorded as taken without the local clamp, the rest of +3V3 is not called 'no EMCON path'
(U30 on PA_EN and U40 are named), bench E-11 carries the +3V3 overvoltage injection it is said to keep, and section 8's
board A bullet no longer says the item is owed. Run from the worktree root; idempotent by marker."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'common'))
from edlib import once
EM = 'v2/docs/feasibility/EMCON.md'
EQ = 'v2/docs/handover/ENGINEERING-QUESTIONS.md'
PA = 'v2/docs/PANEL.md'
MK = 'EQ-17, taken by board A stream w3a on 27 September 2026'

once(EM, """**A fault outside RF-002's named states: +3V3 overvoltage** (the independent check of 26 September 2026). The
SN74AUP1G08's absolute maximum VCC and VI are 4.6 V (SCES502Q 5.1 p.5), now the lowest rating on board A's +3V3,
beside D3, the SMBJ5.0A that clamps that rail and only starts to conduct at 6.40 to 7.00 V (VBR at 10 mA, MDD SMBJ
series, `v2/vendor/power/mdd-smbj-series-tvs.pdf`), and below the 6.5 V of the SN74LVC08A sections the gates replace.
A +3V3 overvoltage between 4.6 V and D3's clamp damages the EMCON gates first, and their output state after damage is
not stated. OPEN: a row in section 7 and in bench E-11; the options (a clamp at or under 4.6 V on board A's +3V3, or the
fault accepted with its bound) are the board A author's.""",
"""**A fault outside RF-002's named states: +3V3 overvoltage** (the independent check of 26 September 2026; EQ-17,
taken by board A stream w3a on 27 September 2026, integrated in `fnd/r8int5`). The SN74AUP1G08's absolute maximum VCC,
VI and VO are 4.6 V (SCES502Q 5.1 p.5), and D3, the SMBJ5.0A on board A's +3V3, only starts to conduct at 6.40 to
7.00 V and clamps at 9.2 V at its rated pulse current (MDD SMBJ series, `v2/vendor/power/mdd-smbj-series-tvs.pdf`).
CLOSED AT DESK (local), with a bound: the four gates U35 to U38 run from `+3V3_EMCON`, behind a TPS259631DDAR eFuse U39
whose overvoltage lockout cuts them off at 3.83 to 4.11 V of +3V3 (R211 23.2 k over R212 10 k; VOVLO(R) 1.17 to 1.22 V,
TI SLVSET8A 7.5) and a 100 Ohm filter R213 into their own 100 nF, with EN on `RAIL_EN`; the two software holds reach
the gates through U40, an SN74LVC2G07 open-drain buffer rated 6.5 V (SCES308L 6.1), as `PA_HOLD` and `HF_HOLD` pulled up
to `+3V3_EMCON`, so no pin of the gates is driven from the +3V3 domain. What the gates see while U39 cuts depends on
its tOVLO, which TI states only as 1.3 us typical (7.6, no maximum): with D3 holding +3V3 at 9.2 V or less the filter
keeps the gates under 4.6 V unless tOVLO exceeds about 9.5 us, while a fast step to U39's 21 V IN rating held for 5 us
would reach about 5.5 V at the gates. Option (c) of EQ-17 is taken without the local clamp it names: the lockout and
R213's filter bound the gates' supply instead. During the fault the gates' outputs fall, `PA_UVLO` and `HF_UVLO` go under
VEN(STBY) and the PA and HF stages shut down: the inhibited state. U39's fault line is `EMCON_EF_FLT` on U28 P1.2 (a
firmware log item). Not closed by this: the rest of +3V3 against D3's 6.40 V (the PCA9555s and INA226s at 6.0 V, the
LVC parts at 6.5 V), which still reaches EMCON through two parts: U30 (SN74LVC1G00 on +3V3) has an input on `PA_EN`
itself, and U40's outputs are the software-hold inputs of U36 and U38, so a part damaged between 6.5 V and D3's clamp
leaves those nets in an unstated state (the `TX_INHIBIT_n` AND `EMCON_HW` path through U35 and U37 is not affected
unless U40 fails shorted to its supply); a registry open item. Bench E-11 carries a +3V3 overvoltage injection
(section 6: the cut level, tOVLO and the gates' supply during it). Choices in `v2/ecad/tools/gen_sch_a.py` (EQ-17,
TAKEN) and the requirements registry.""", marker=MK)

once(EM, """| Board A's +3V3 overvoltage against the SN74AUP1G08's 4.6 V absolute maximum (round 8, section 4a) | D3 (SMBJ5.0A) starts to conduct at 6.40 to 7.00 V; between 4.6 V and that the EMCON gates are damaged first, their output after damage unstated; outside RF-002's named states | board A author (a clamp at or under 4.6 V, or the fault accepted with its bound); bench E-11 |""",
"""| Board A's +3V3 overvoltage against the SN74AUP1G08's 4.6 V absolute maximum (round 8, section 4a) | CLOSED at desk with a bound by board A stream w3a (27 September 2026, EQ-17): U39 cuts the gates' supply at 3.83 to 4.11 V of +3V3, and R213's filter keeps them under 4.6 V while D3 holds +3V3 at 9.2 V or less unless U39's tOVLO (1.3 us typical, no maximum stated) exceeds about 9.5 us; U40 keeps the +3V3 domain off their inputs; the rest of +3V3 against D3, U30 on `PA_EN` and U40 itself included, is a registry open item | bench E-11 (the +3V3 overvoltage injection, section 6) |""",
     marker="CLOSED at desk with a bound by board A stream w3a")

once(EM, """while +5V_D8 stays up (L4, round 8) | every gate reads EMCON asserted (after L1 to L4 and L7 are remedied); +5V_TX is under the exciter's 3.3 V floor whenever +3V3_D8 is under 1.65 V, including during the step |""",
"""while +5V_D8 stays up (L4, round 8); on board A, +3V3 stepped from 3.3 V to 9 V (under D3's clamp) with `+3V3_EMCON`, `EMCON_EF_FLT` (TP3), `PA_UVLO` and `HF_UVLO` recorded (EQ-17, stream w3a) | every gate reads EMCON asserted (after L1 to L4 and L7 are remedied); +5V_TX is under the exciter's 3.3 V floor whenever +3V3_D8 is under 1.65 V, including during the step; on board A, `+3V3_EMCON` stays under 4.6 V through the step, `EMCON_EF_FLT` asserts, and `PA_UVLO` and `HF_UVLO` stay under VEN(STBY) |""",
     marker="on board A, +3V3 stepped from 3.3 V to 9 V")

once(EM, """gate's output (section 4a). Owed: the +3V3 overvoltage item of section 7.""",
"""gate's output (section 4a). The +3V3 overvoltage item of section 7: closed at desk with a bound by stream w3a (EQ-17,
  U39 and U40, section 4a); owed: bench E-11's injection and the rest of +3V3 against D3 (a registry open item).""",
     marker="closed at desk with a bound by stream w3a (EQ-17,")

once(EQ, """| **Attempts and results** | Recorded OPEN in round 8; no change drawn. |""",
"""| **Attempts and results** | Recorded OPEN in round 8; no change drawn. **Set 5 (board A stream w3a, integrated in `fnd/r8int5`):** option (c) is taken without the local clamp it names; the eFuse's lockout and a filter bound the gates' supply instead. U35 to U38 run from `+3V3_EMCON` behind the eFuse U39 (TPS259631DDAR, overvoltage lockout at 3.83 to 4.11 V of +3V3, SLVSET8A) and a 100 Ohm filter into their own 100 nF, and the software holds reach them through U40 (SN74LVC2G07, open drain, 6.5 V) pulled up to the protected rail. The bound: with D3 holding +3V3 at 9.2 V or less the gates stay under 4.6 V unless U39's tOVLO (1.3 us typical, no maximum stated) exceeds about 9.5 us, which bench E-11's injection checks. (a) was refused because no clamp holds under 4.6 V at U12's 4.2 to 5.8 A, (b) because the SN74LVC1G08 is rated 6.5 V, inside D3's range, and undoes round 8's hold. Board A regenerated with parity; RF-002's walk on A prints the same verdicts before and after. The rest of +3V3 against D3 (U30 on `PA_EN`, U40) is a registry open item. **Status:** closed at desk with that bound; R-PWR (EQ-11) reviews it. |""",
     marker="**Set 5 (board A stream w3a, integrated in `fnd/r8int5`):**")

once(EQ, """| **Attempts and results** | The rule's instrument changed in `940cbcdf`; no board's intent has been extended yet. |""",
"""| **Attempts and results** | The rule's instrument changed in `940cbcdf`; no board's intent has been extended yet. **Set 5 (`fnd/r8int5`), board A (stream w3a):** VMON, PRECHG, +3V3_EMCON_EF and +3V3_EMCON declared as rails, B33_BST, HT_BST, S1_BOOT, S3_BOOT, PD_VTX, PD_VAUX, PD_DVDD, PD_CC1 and PD_CC2 as nodes, each from its maker's sheet; PWR-001 on A's regenerated netlist reads PASS of 35 (34 declared rails, 0 undecided). B, D and E stay open. |""",
     marker="**Set 5 (`fnd/r8int5`), board A (stream w3a):**")

once(PA, """and `U28` (power-good lines, the USB-C outlet's software enable, the Glenair host port's VBUS switch and its fault, spares) | A22 |""",
"""and `U28` (power-good lines, the USB-C outlet's software enable, the Glenair host port's VBUS switch and its fault, the EMCON gates' supply fault `EMCON_EF_FLT` on P1.2, low when U39 has cut it on a +3V3 overvoltage, spares) | A22 |""",
     marker="the EMCON gates' supply fault `EMCON_EF_FLT` on P1.2")
print("apply_docs_r8int5 (w3a): applied")
