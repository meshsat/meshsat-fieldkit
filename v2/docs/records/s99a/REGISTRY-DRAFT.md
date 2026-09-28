# Registry draft text after stream s99a (for the integrator, the one writer of the shared files)

Stream s99a, MESHSAT-1357, 28 September 2026. AI engineering work; prototype design, nothing built, ordered or
measured. These texts supersede the matching parts of `v2/docs/records/s99/REGISTRY-DRAFT.md` where they differ (the
wall limit, the declared peak and margin, U41's divider and voltage, the disposition word). Nothing here edits a
shared file; the integrator lands them by its own apply script.

## 1. S-99 re-stated (OPEN, class SESSION, disposition CIRCUIT_ITEM until the re-takes are read)

    - id: S-99
      class: SESSION
      status: OPEN
      disposition: CIRCUIT_ITEM
      disposition_why: >-
        Board A's circuit changed on branch fnd/s99a (decision 55 applied to gen_sch_a.py); the item stays a circuit
        item until board A is regenerated on the box and PWR-001 and INT-001 are re-taken on it. What remains after
        that is board B's child reconciliation (a declaration question) and prototype verification.
      title: >-
        (cx1 I-03; analysed by stream s99, applied by stream s99a, v2/docs/records/s99a/README.md) THE DECLARED-DEMAND
        QUESTION IS ANSWERED BY DECISION 55 AND THE CIRCUIT. The D8 mezzanine left board A's +5V_DEV for its own
        TPS62933 buck U41 from VBAT (rail +5V_D8IN, 56.2k over 10.7k at 0.1 percent: 5.002 V nominal, 4.872 to 5.133 V
        over VFB 784 to 816 mV, both tolerances, 25 ppm/C over 65 K and the FB leakage, SLUSEA4D p.6), with U23 kept as
        its eFuse. Board A's LM5176 device stage U7 now carries board B's 6.0 A and the wall host port's 0.9142 A (U32 at
        1.00 kOhm: TPS2596 equation 7 is RILM = 903 / (ILIM - 0.0112), SLVSET8A printed p.28, so ILIM = 0.9142 A
        nominal; the generator had the sign as + and read 0.89 A): 6.9142 A declared against the average loop's
        conditional minimum of 7.056897 A (43 mV over R43 6 mOhm at +1 percent and an assumed 50 K at +/-110 ppm/K;
        SNVSAI1D p.7, Vishay 30100 pp.1-2), a margin of 0.142697 A (0.181510 A at the initial 7.095710 A; 0.100853 A
        and 0.091314 A with the wall at the 909 ohm row's extrapolated 0.956044 A and with R186 at -1 percent, which
        are estimates, not a guaranteed 1 kOhm maximum). STILL OPEN, each with what decides it: (a) the M and P tiers
        against the loop: M 5.942235 A passes by 1.114661 A as a conditional allocation, P 8.171220 A (8.180759 A with
        R186 tolerance) exceeds the minimum by 1.114324 A (1.123863 A) on board B's declared child peaks; decided by
        board B's reconciliation of its +5V_DEV children (I-03's M/P adequacy: the supervisor LDOs' 0.12 A entries
        with their ground current, U26 against the maker's 0.34 A, U25's 2.0 A peak) or a document that makes the
        peaks non-coincident, and at the bench by the coincident current at R43 and J_5V_DEV under PS-ALLTX (PT-4);
        (b) timing and capacitor support: no closed-loop time constant or onset bound is published (CSS/gm = 47 us is
        a dimensional ratio); simultaneous SS, rail voltage and branch current through actual bursts and controlled
        steps (PT-2 for +5V_S2, PT-4 here); (c) collapse and recovery: current against falling voltage, dropout, UVLO
        and restart with the fitted loads (PT-4); (d) the new buck U41: its loss and temperature (only JEDEC and EVM
        RthJA are published, SLUSEA4D p.6), the output capacitors' DC-bias derating at 5 V (no curve held), the 0.90
        efficiency (a project figure), by calculation on the routed copper and by measurement on the prototype;
        (e) the stage's FET and shunt temperatures and switching waveforms (the 112 C figure is a scenario, SLPS414B
        p.3), PT-4 over VBAT, load and ambient including the 60 s key-down; (f) board A's layout generator does not
        yet place the ten new parts nor re-derive +5V_DEV's outlet island (S-115, layout stage). Closes when: board A
        is regenerated from fnd/s99a on the box and its intent, netlist and ERC are read; PWR-001 and INT-001 are
        re-taken on it; the IF-AB-POWER +5V_DEV row reads the new figures; (a) is decided by board B's declarations or
        a document. (b), (c), (d) and (e) are prototype verification in TEST-PLAN rows PT-2 and PT-4 (proposed in
        v2/docs/records/s99/RAILS-ACTIONABLE.md), kept separate from the desk closure. Record:
        v2/docs/records/s99/ANALYSIS.md, CORRECTION.md, checks/check-2-claude.md; v2/docs/records/s99a/README.md.

## 2. Decision 55: the fields that change against s99's draft

- `outcome`: replace "AT 5.088 V (53.6k / 10k)" with "AT 5.002 V NOMINAL (56.2k / 10.7k, both 0.1 percent 25 ppm/C,
  the codes C705784 and C861078 board D already certifies), 4.872 TO 5.133 V OVER EVERY TOLERANCE, SO BOARD D'S
  DECLARED v_work OF 5.23 V ON +5V_D8 STANDS"; replace "6.9 A declared" with "6.9142 A declared (the wall port at
  U32's corrected 0.9142 A)" and "0.16 A" margins with 0.142697 A.
- `reversed_by`: add "and restore Q32's VBAT share to 2.0 A" (it is 1.61 A after the split; U41 carries 0.4 A).
- `evidence`: add "TI SLVSET8A printed p.28 (equation 7 and its worked example), TI SLUSEA4D p.6 (VFB and IFB), TI
  SLES230A 7.3 p.5 (PCM2912A VBUS 4.35 to 5.25 V), v2/docs/records/s99a/u41_divider.out".
- `authority_why` is unchanged in substance; the divider choice is recorded in the generator comment as SESSION
  (board D's alternative, raising its v_work to 5.29 V, is refused on the PCM2912A's 5.25 V recommended maximum).

## 3. IF-AB-POWER (`pcb_interfaces.yaml`)

- The +5V_DEV currents row (line 391 on set 8's line): `a_declares: "4.1 A typical, 6.9142 A peak at the converter
  (B 6.0 + the wall host port 0.9142, U32's nominal limit by TPS2596 equation 7; the D8 mezzanine on its own rail
  +5V_D8IN since decision 55), of which 3.8 A apportioned to J_5V_DEV (gen_sch_a.py, the S-99 lines)"`;
  `converter_limit`: "the LM5176 average loop on the OUTPUT side, 7.056897 to 9.649029 A over tolerance and an
  assumed 50 K shunt temperature change; the declared 6.9142 A is 0.142697 A under its minimum; the mode current is
  INCONCLUSIVE until PT-4". `b_declares` is unchanged (3.8 A typical, 6.0 A peak arriving).
- Line 359: "through A's eFuse U32 (limit 0.89 A)" becomes "(limit 0.9142 A nominal, TPS2596 equation 7)".
- IF-AD-HARNESS (line 422): U23 stays the source of +5V_D8 (1.0 A declared, ILM 2.0 A); its cite
  "gen_sch_a.py:1171" is stale (U23's call follows the S-99 stage block now), and U23's input is +5V_D8IN.

## 4. Other pages that quote the wrong-sign 0.89 A (text only, no rule reads them)

`v2/docs/HW-FW-CONTRACT.md` line 85 (FW-A07, "eFuse U32 (0.89 A)"), `v2/docs/ASSEMBLY.md` line 151 (the wall USB
host row), `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` line 244 ("limit 0.89 A"). Each reads 0.9142 A
nominal (0.91 A at two figures) by SLVSET8A printed p.28.
