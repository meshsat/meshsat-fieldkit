# Draft rows for LAYER-STATUS.md, items 4.10 and 5.5, after S-98 (stream s98, 28 September 2026)

Prototype design; AI engineering work, not a qualified review. Nothing built, ordered or measured. The integrator places
these rows in `v2/docs/handover/LAYER-STATUS.md` (the H2 tables of layers 4 and 5, lines 313 and 334 at dcf04c90) when
the box regeneration's pack is installed; before that, the state of each is the "before the pack" line.

The owner's instruction of 28 September asks for declaration consistency and electrical adequacy as SEPARATE evidence.
Each row below carries both halves, with what rests on which evidence.

## The acceptance criteria as written

- **4.10** "Rail and interconnect margins" (LAYER-STATUS.md Appendix A.4, the acceptance items table, line 896; the H2
  table's short form "rail and interconnect margins", line 313). The audit at `e3aedb25` read it "no" on five findings:
  PWR-F01 and F03, PWR-F02, R17 at 18 A, IF-AB-POWER's ends disagreeing (I-03), IF-AE-DOCK's contact margin, PWR-003 on
  B_PANEL_5V. At H2 it read PARTLY with "not re-checked at H2: R17's rating, IF-AB-POWER's two ends (I-03), PWR-F02".
- **5.5** "Power capacity of each power interface shown with margin" (Appendix A.5, line 1068; the H2 table's short form
  "power capacity of each power interface with margin", line 334). At H2 PARTLY with "open: E5's targets and the ground
  share (S-74, S-75), IF-AB-POWER (I-03), the ribbon and SMP-MAX ratings TBD".

This stream touches ONE of the interfaces each row names, IF-AB-POWER. Neither row can read MET from this stream alone.

## Item 4.10, draft row

| 4.10 | rail and interconnect margins | PARTLY | **IF-AB-POWER's two ends carry one figure per conductor since S-98 (declaration consistency):** +5V_S2 4.2 A typical and 5.63 A peak at both ends with J_5V_S2 5.63 A and Q28 2.22 A, +5V_DEV 3.8 A at the lead with A's typical 5.1 A, the notes INTERIM and the PS-ALLTX mode figures INCONCLUSIVE at both ends (`fnd/s98`, `records/s98/`; `lead_ends.py` 5 of 5 AGREE on the regenerated intents, `check_contracts` PASS re-taken, `interfaces_a` and `interfaces_b` PASS re-taken with the rewritten contract: the box pack of `box_regen_ab.sh`). **Electrical adequacy, OPEN:** +5V_S2's all-peak conditional bound 7.28 A sits above the LM5176 stage's average loop minimum, 7.10 A at the shunt's +1 percent and 7.17 A nominal (a bound against a limit, the mode current unmeasured: `records/cx1/CORRECTION.md` B1); +5V_DEV's coincident 7.9 A (D8 typical) and 8.9 A (every declared limit) sit above the same minimum while 6.9 A is declared, S-99 decides (REQ-018 waits on it); the leads' own drop (16 AWG pair 300 mm plus four VH contacts at their 10 mOhm maximum, 0.225 V at 5.63 A, 4.4 percent of 5.1 V) is in no board's share of the 2 percent budget (`records/cx1/ANALYSIS.md`, both checks); PWR-001 judges the declaration's form and dc_drop judges copper at the declared current, neither judges a converter against its loads. Still not re-checked: R17's rating, PWR-F02, the other interfaces of this row |

Before the pack is installed the row stays as at H2 with one sentence added: "IF-AB-POWER's two ends are aligned in the
generators (`fnd/s98`, INTERIM) and the tree's contract reading is INCONCLUSIVE until the box regenerates A and B (the
netlists' provenance names the previous generators, `check_contracts` MISSING A and B)".

What MET would need for this stream's part: (a) is met by the pack; (b) needs S-99's decision on the +5V_DEV stage
(sense resistor, an interlock, or the 8.9 A bound with the fold-back named) and the bench's PS-ALLTX currents at J_5V_S2
and J_5V_DEV (TEST-PLAN power tests, FW-A15 in POWER-THERMAL.md); a lead-drop share in the contract or the two boards'
budgets is a registry item the integrator may open (no id yet).

## Item 5.5, draft row

| 5.5 | power capacity of each power interface with margin | PARTLY | **IF-AB-POWER, capacity declared at both ends since S-98 (declaration consistency):** the five leads carry one figure per conductor, INTERIM, the PS-ALLTX mode figures INCONCLUSIVE (`records/s98/`, the box pack's `lead-ends.txt` 5 of 5 AGREE). **Its margin (electrical adequacy), PARTLY:** the JST VH catalogue is held (`v2/vendor/connectors/jst-vh-catalogue.pdf`, page 1: 10 A per contact at AWG 16 on the standard header), so the four 5 V leads' declared peaks, 5.0, 5.63, 5.0 and 6.0 A, are 50 to 60 percent of the contact rating, a margin from a held document against declared peaks that are themselves INTERIM; J_54V's AWG 18 lead on the standard header has NO stated rating (7 A is stated for the shrouded header only), INCONCLUSIVE at 0.6 A declared; the converter-side margins are 4.10's and S-99's. Unchanged by this stream: IF-AE-DOCK (SC-55; E5's targets and the ground share, S-74, S-75), IF-BC-PANEL (PWR-003 PASS at `b76c18cb`), the ribbon and SMP-MAX ratings TBD |

Before the pack: as at H2 with "IF-AB-POWER (I-03)" replaced by "IF-AB-POWER aligned in the generators (`fnd/s98`,
INTERIM), re-read at the box regeneration".

## What is MET, PARTLY and OPEN, in one list

| | Declaration consistency | Electrical adequacy |
|---|---|---|
| +5V_S1, +5V_S3 | MET (unchanged: 2.5 / 5.0 A at both ends; `lead_ends`) | OPEN as before (PWR-F02: +5V_S1 at 4.65 of 5 A in the registry's PS-ALLTX PLAN, not this stream's) |
| +5V_S2 | MET at the pack (4.2 / 5.63 A both ends, INTERIM) | OPEN: 7.28 A bound above the 7.10 to 7.17 A loop minimum; the mode current is the bench's |
| +5V_DEV | MET at the lead at the pack (3.8 A both ends, INTERIM) | OPEN: S-99 (7.9 and 8.9 A coincident against the loop minimum, 6.9 A declared); the U32 0.3 A allocation against VBUS_WALL's 0.5 A typical (`records/s98/README.md`, residual) |
| +54V_POE | MET (0.3 / 0.6 A both ends, unchanged) | INCONCLUSIVE: no stated rating for AWG 18 on the standard header |
| the leads' contacts | not a declaration question | PARTLY: 10 A per contact at AWG 16 (held), peaks 50 to 60 percent of it; the lead drop in no board's share |

No adequacy line above is claimed MET without a held source: the two sources are the JST VH catalogue (contact rating)
and TI SNVSAI1D (the loop's VSNS 43 to 57 mV, page 7), and both are compared with DECLARED figures, not measured ones.
