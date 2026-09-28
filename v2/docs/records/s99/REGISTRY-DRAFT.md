# Draft registry text for S-99 (for the integrator, the one writer of the shared files)

Stream s99, MESHSAT-1357, 28 September 2026. AI engineering analysis; prototype design, nothing built or measured.
Three texts: the re-statement of S-99 in `v2/ecad/tools/pcb_requirements.yaml`, decision 55 for
`v2/ecad/tools/pcb_decisions.yaml`, and the lines for IF-AB-POWER's currents row in `v2/ecad/tools/pcb_interfaces.yaml`
and for S-98. The integrator lands them by its own apply script (the pattern of the earlier streams); nothing here
edits a shared file.

## 1. S-99, re-stated (OPEN, class SESSION, disposition CIRCUIT)

    - id: S-99
      class: SESSION
      status: OPEN
      disposition: CIRCUIT
      disposition_why: 'A circuit item since stream s99 (28 September 2026): the fitted stage cannot be shown to carry
        the PS-ALLTX coincident demand at its average loop''s minimum, so board A''s generator changes (decision 55) and
        PWR-001 and INT-001 are re-taken on the regenerated board.'
      title: '(cx1 I-03, resolved against the actual circuit by stream s99, v2/docs/records/s99/ANALYSIS.md) Board A''s
        +5V_DEV converter U7 is an LM5176 in buck (VBAT 12.4 to 16.8 V to 5.088 V) whose average current loop senses the
        OUTPUT current across R43, 6 mOhm between Q35''s drain and the rail (netlist), and regulates it to 43 to 57 mV:
        7.06 A minimum (1 percent and a 50 K hot shunt), 8.33 A typical, 9.65 A maximum (SNVSAI1D p.7, Vishay 30100
        p.2); the cycle-by-cycle valley limit (R177 5 mOhm, 66 to 94 mV) sits at 13.1 to 19.0 A of inductor current and
        never acts at the demand. In PS-ALLTX the coincident demand is a 60 s plateau of 7.32 A with the makers'' figures
        and the boards'' typicals (board B 5.44 A with the LimeSDR at 0.9 A, the LoRa at 0.65 A, the RockBLOCK at its
        0.5 A input limit, the KSZ9897R at 1.21 A and both Zigbee radios transmitting; the D8 mezzanine 1.38 A with the
        SA868 keyed at 0.9 A; a USB 2.0 device on the wall port 0.5 A), 8.9 A at every declared limit and 9.74 A with
        board B''s declared child peaks: no tier is under the loop''s minimum, and the loop engages within 2 to 60 ms
        (CSS 47 nF, gm 1 mS, VSS(CL) 1.21 V), far inside any burst, then folds the rail back regeneratively on the bucks
        and LDOs behind it: the brown-out of the always-on fabric. Raising the loop by a 5 or 5.6 mOhm shunt is
        rejected: its maximum (11.5 or 10.3 A) would exceed the JST-VH lead''s 10 A contact rating in a board-B fault a
        CCM stage without hiccup holds indefinitely; 6 mOhm is pinned by the lead. DECISION 55 (authority SESSION): the
        D8 mezzanine leaves +5V_DEV for its own TPS62933 buck from VBAT (U41, the part board A fits twice), U23 kept as
        its eFuse; the converter''s demand returns to B plus the wall port, 6.9 A declared (0.16 A under the loop''s
        minimum) and 5.94 A with the makers'' figures (1.11 A under); the wall host port on the outlet interlock (U26''s
        spare section) is the fallback for 0.9 A more, not taken. Draft for board A''s owner:
        v2/docs/records/s99/apply_d8_split_draft.py (--check passes; it supersedes cx1''s B2-A-DEV entry). Closes when:
        (a) the draft is applied and board A regenerated (intent, netlist, ERC read); (b) PWR-001 and INT-001 re-taken
        on board A and the contract''s +5V_DEV currents row rewritten (A 4.1 A typical, 6.9 A peak, J_5V_DEV 3.8 A; the
        new rail +5V_D8IN 1.0 / 2.0 A); (c) board B''s +5V_DEV children reconciled with its rail (S-98 M7: the
        supervisor LDOs 0.05 against 0.12 / 0.25 A, U26 0.15 against the maker''s 0.34 A, U25''s 2.0 A peak), so that
        the child-peak tier (8.15 A after the split) is either under 7.06 A or shown non-coincident by a document; (d)
        dc_density reads +5V_DEV and SD_OUT at the corrected current when board A reaches layout. Kept separate as
        prototype verification: TEST-PLAN row PT-4 (the rail current at J_5V_DEV and at the mezzanine''s buck under
        PS-ALLTX with the LoRa, RockBLOCK, LimeSDR and Zigbee transmitting and the exciter keyed, averaged over the
        loop''s onset and at its peak; the rail voltage at board B''s C1 through the key-down). Observation for the
        stage owner, not this item''s verdict: at the tolerance corner (VCS 94 mV, R177 minus 1 percent, L minus 20
        percent, 180 kHz) the cycle-limit backstop''s inductor peak in a hard short reads 22.6 A against the XAL1010''s
        Isat 21.8 A (INFERRED), and the stage has no output capacitance before the ISNS shunt (SNVSAI1D 10.1 asks to
        divide COUT across it; the ISNS filter is fitted).'

## 2. Decision 55 for `pcb_decisions.yaml`

    - n: 55
      title: 'board A: the D8 mezzanine leaves the +5V_DEV LM5176 stage for its own 5 V buck from VBAT'
      asked: 2026-09-28
      status: ruled
      authority: SESSION
      authority_why: 'it changes no line the never-auto floor protects (no class of tools/reserved.json names
        gen_sch_a.py), spends nothing the owner decides (seven parts inside the board''s BOM, six of them types board A
        already fits; no purchase), changes no claim about the kit (the mezzanine keeps its 5.0 V and its 6 percent
        budget improves), and accepts no residual risk a measurement in this tree cannot remove (the remaining
        child-peak tier is board B''s declarations and the bench test PT-4).'
      ruled_by: SESSION
      ruled_on: 2026-09-28
      outcome: 'THE MEZZANINE''S 5 V IS ITS OWN RAIL, +5V_D8IN, FROM A TPS62933 (U41) ON VBAT AT 5.088 V (53.6k / 10k),
        6.8 uH XAL6060-682ME, 500 kHz, ENABLED WITH THE 3.3 V LOGIC (RAIL_EN), AND U23 STAYS THE MEZZANINE''S EFUSE
        (D8_EN, 2.0 A, OVLO) FED FROM IT. The +5V_DEV stage''s coincident PS-ALLTX demand returns to board B plus the
        wall host port: 6.9 A declared and 5.94 A with the makers'' figures against the average loop''s 7.06 A minimum
        (v2/docs/records/s99/ANALYSIS.md sections 3 to 5, dev_stage.out). The stage itself is unchanged: R43 6 mOhm
        stays because the loop''s 9.6 A maximum must stay under the JST-VH lead''s 10 A rating.'
      reversed_by: 'delete U41, L13, C227 to C232, R217 and R218, return U23''s input to +5V_DEV, restore the +5V_DEV
        loads (U23 at 1.0 A) and VBAT''s map (no U41), and re-take PWR-001 and INT-001: the four replacements of
        v2/docs/records/s99/apply_d8_split_draft.py in reverse.'
      ask: carry the mezzanine on the device rail (declare the 8.9 A bound with the fold-back named), re-rate the
        stage''s average loop (5 or 5.6 mOhm), interlock the wall host port with the outlets, or give the mezzanine its
        own converter
      recommendation: THE OWN CONVERTER, because it is the only option that puts the demand under the loop''s minimum
        at the declared tier without moving the lead''s protection point; the wall-port interlock is the fallback for
        0.9 A more and extends an owner ruling (D-11) to the console port, so it is not taken while the split suffices.
      evidence: board A''s netlist at 2b7c9374 (sha256 0a2b5908...), the intents of boards A, B and D (sha256 3422910a...,
        96ee391b..., 8d9f3b22...), TI SNVSAI1D pp.3 to 7, 16 to 17, 23 to 26, TI SLPS414B p.3, Coilcraft 804-1 and 887-1,
        Vishay 30100 pp.1 to 2, TI SLVSET8A, TI SLUSEA4D, NiceRF SA868 v1.3 p.4, Ebyte E22-900M30S v1.20, Ground
        Control''s RockBLOCK 9704 hardware page (snapshot 2026-09-27), MyriadRF''s LimeSDR Mini pages, Microchip
        DS00002330D p.169; v2/docs/records/s99/dev_stage.py (reproduced byte for byte, inputs refused by name when
        changed).
      blocks: {}
      holds_nothing_today: 'it releases no rule-board pair: PWR-001 and INT-001 on board A are re-taken after the
        regeneration; REQ-018 stays NOT_JUDGED under FEA-004 and S-99''s closure conditions.'

## 3. IF-AB-POWER's currents row for +5V_DEV, after the split (pcb_interfaces.yaml)

    - rail: +5V_DEV
      a_declares: 4.1 A typical, 6.9 A peak at the converter (B 6.0 + the wall host port 0.9; the D8 mezzanine on its own
        rail +5V_D8IN since decision 55), of which 3.8 A typical apportioned to J_5V_DEV (gen_sch_a.py, the S-99 lines)
      b_declares: 3.8 A typical, 6.0 A peak arriving (gen_sch_b.py:97)
      converter_limit: 'the LM5176 average loop on the OUTPUT side, 7.06 to 9.65 A over tolerance and a hot shunt
        (v2/docs/records/s99/ANALYSIS.md 4a); the declared 6.9 A is 0.16 A under its minimum; the mode current is
        INCONCLUSIVE until TEST-PLAN PT-4'
      status: 'ALIGNED at the lead (A 3.8 A, B 3.8 A typical); the child-peak tier of B (7.22 A on the lead) is above
        B''s own 6.0 A and is S-98''s reconciliation'
      enable: DEV_EN, ON by design since 458b2873 (R42)

## 4. S-98: one sentence to add

    The +5V_DEV entries of cx1''s draft (B2-A-DEV: J_5V_DEV 3.8 A, typical 5.1 A with U23 at 1.0 A) are superseded by
    stream s99''s apply_d8_split_draft.py entry S99-DEV (J_5V_DEV 3.8 A, typical 4.1 A, U23 no longer a load) once
    decision 55 is applied; the two drafts target the same line and only one is run.
