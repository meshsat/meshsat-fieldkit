accepted: yes

# Layer 4, L4-E7: Claude's check of the panel-lead surge derivation and the solar-fault remedies at b726d63c (the coordinator's check; not a model review, not an Astra check)

MESHSAT-1357, 2 October 2026.
- The surge round (`6d76453e`) derived the panel entry's disturbances under MIL-STD-461G's CS116 and CS115 (REQ-063, the Ground,
  Army row) and found two single faults NOT MET: a 36 V source on the port, and a reversed panel.
- The remedies round (`b726d63c`, the owner's amendment of 14:20, item 3) selects one remedy for each, from parts already in the design,
  as a release-guarded draft (`apply_gen_sch_e_solar_guard.py`), never applied.

**Verified by the coordinator:**
- *Reproduction:* `l4e7_stage_settings.py` re-run at `b726d63c`, its output equal to the committed `.out` byte for byte; `test_l4e7`
  with `test_public_hygiene` 43 passed, 0 failed. No em or en dash.
- *The over-voltage cut-off on TI's sheet* (TPS4811-Q1, SLUSEE5E, held): V(OVR) rising 1.16 / 1.18 / 1.20 V, V(OVF) falling
  1.10 / 1.11 / 1.13 V, OV leakage 60 to 300 nA.
  - The divider R100 / (R98 + R99 + R100) = 7.68 / 193.88 = 0.039612 places the rising threshold at 29.28 to 30.29 V on the printed
    row alone. The round's 28.55 to 31.06 V widens that for the resistors' tolerance and printed aging, and for the pin's leakage.
  - The band's low edge stays above CS101's 27.82 V input peak, its falling edge (27.07 V or more) above REQ-016's 25 V, and its high
    edge 0.737 V under the SMCJ30A's least cold breakdown.
  - The drafted SMCJ28A could not hold that coordination once the divider's aging is carried (-0.282 V), which is why D4 changes.
- *The selection's reasons are on the sheets:*
  - the TPS48110 alone on back-to-back FETs exposes its -1 V rated input pins to a reversal;
  - the LM74700 pair sees 76.21 V across CATHODE to ANODE under CS116's negative lobes, against its 75 V;
  - the selected arrangement (U21 with Q12 for over-voltage, Q13 a CSD19532Q5B in the return for reversal) is linear when on, and
    holds 36 V and 25 V on 100 V FETs.
- *The accepted results re-run where the block changes them:*
  - CS101's worst ripple is 0.0591 A against the 0.1130 A margin (0.0585 A without the block, reproduced);
  - check (b)'s response allowance is 1.021 ms, still over ten times the typical response;
  - the static bound is 93.5954 W;
  - the window is unchanged, and the cut-off never trips inside it.

**Accepted:** both single faults have a selected remedy with a bounded analysis that MEETS. The reversed panel is CONDITIONAL on Q13's
leakage above +25 C, which its sheet prints only at 25 C.

**Owed with the draft:**
- the SMCJ30A's LCSC code;
- U21's DGX-19 land (as E11-01);
- the regeneration;
- the bench rows.

**Named for layer 8, not hidden:** a stiff source between 25 V and the cut-off is outside REQ-016's window but still runs the stage, up to
116.5 W under the backstop's current trip. Fault protection does not extend the operating range, but in that band the protection does
not stop the stage either. Layer 8's judgement under TRN-001 decides whether that single fault needs a lower cut-off. The cut-off cannot
go lower than CS101's 27.82 V input peak without a different immunity basis, which is why it sits where it does.

L4-E9 and L4-E13 must re-pin L4-E7's output.
