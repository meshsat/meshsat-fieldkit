# Review stream BAT: proposed changes to files this stream does not own (for the integrator and each file's owner)

MESHSAT-1357, 26 September 2026 (third cycle). Worktree `fnd/rv-bat` at main `1f614233`. This stream wrote
`v2/docs/review-packets/battery/**`, `v2/ecad/tools/gen_sch_p.py`, `drafts/*`, the fixture
`v2/ecad/tools/tests/test_pack_secondary_ts.py` (section 9), and two documents filed into `v2/vendor/` with their
bookkeeping lines (section 6; coordination in `drafts/vendor-files.txt`). Everything below is PROPOSED text; the
owner of each file decides and writes it. Decisions marked "taken by the session under the owner's standing rule of 26
September 2026" are recorded as such in the packet.

## 1. `v2/docs/TEST-PLAN.md` E3 and E4 (owner: TEST-PLAN), BAT-F02

Current (`TEST-PLAN.md:18-19`): E3 stores the kit 24 h at +71 C closed and operates it 4 h at +55 C, with the pass line
"pack under 60 C"; E4 stores it 24 h at -33 C. A pack soaked at +71 C cannot be under 60 C, and the cells are rated for
storage at no more than +60 C for one month and discharge at no more than 60 C (Samsung INR18650-35E Ver. 1.1, 3.12 and
3.13; the 2016 Version 1.0 the same at the top end).

Proposed replacement rows (taken by the session under the owner's standing rule of 26 September 2026; D-02a's margins
stay for the kit, and the pack's margins are its cells' limits):

| ID | Test | Method | Pass |
|---|---|---|---|
| E3 | 501, high temperature: storage 24 hours at +71 C closed, then operation 4 hours at +55 C deployed with the monitor and radios on, **with the pack removed** (stored separately inside its envelope) and the kit on shore or vehicle input | in-house with a climate cabinet or a heated enclosure with the reference thermometer | inside temperature stays under the parts' limits (CM5 throttling logged but no shutdown), no deformation, functional check passes |
| E3-P | the pack's own high-temperature check: storage 24 hours at a **+58 C set point** in a cabinet holding +-2 K or better, with the reference thermometer on the hottest cell, so the cells never exceed their +60 C one-month storage limit; armed (JP1 closed); then discharge at 2 A until the cells reach their **60 C** discharge limit by their own heating | the same cabinet, the pack alone on a bench load | F2 intact; the gauge stops discharge at 60 C and recovers; the second level does not fire (its lowest trip is 62.7 C, reading B); capacity after recovery logged against the cells' 80 % recovery figure |
| E4 | 502, low temperature: storage 24 hours at -33 C closed **with the pack removed**, then operation 4 hours at -20 C with the pack fitted and its heater active | in-house with a freezer or winter exposure | the pack heats to its charge window before charging is allowed, the monitor and e-paper operate at -20 C, functional check passes |
| E4-P | the pack's own low-temperature storage at the lowest temperature of the governing cell specification (**-20 C** in Ver. 1.1, **0 C** in the 2016 Version 1.0; which governs the lot bought is TBD) | freezer, the pack alone | F2 intact, full function after return to 25 C |

`test_pack_protection.t_every_protection_function_is_in_the_test_plan` requires every function id of
`pcb_pack_protection.yaml` to appear in TEST-PLAN.md; if the yaml gains a SECONDARY_OVER_TEMPERATURE function (section 3),
TEST-PLAN needs the same words.

## 2. `v2/docs/OPERATING-ENVELOPE.md` (owner: envelope), BAT-F09 and a stale row

- Line 66, "the pack's protection board | east pocket | -40 to +85 C (storage -40 to +125) | battery/batteryspace-prod-spec-274.pdf":
  that is a COTS protection board from before board P existed. Board P's parts: BQ4050 -40 to 85 C operating (SLUSC67B
  6.3), BQ7720700 -40 to 110 C (SLUSEG7D section 4) with TA -40 to 85 C recommended (6.3), SCF9550-30-05 **-20 to +60 C**
  (ELX1135 page 4), PRF15BB103 -20 to +140 C. The narrowest is F2's, which the pack's cells bound anyway.
- Line 141, storage "-20 to +45 C for up to three months": true for the Ver. 1.1 cell sheet; the 2016 Version 1.0 in the
  tree gives 0 to 45 C. Add: "which cell specification revision governs the purchased cells is TBD; with the 2016 revision
  the pack's storage floor is 0 C".

## 3. `v2/ecad/tools/pcb_pack_protection.yaml` (owner: BAT-001), O-4, extended

- `pack.topology`: "4S3P (D-06), about 145 Wh" (it still says "4S3P or 4S4P, about 200 Wh").
- `secondary_protection.present: true`, with U2 BQ7720700 (OV 4.325 V 1 s, UV 2.25 V 1 s, open wire 4 s, OT 70 C 4 s on its
  own 103AT-2 through J_TS2 and the R34 270 ohm / R33 18 kohm network, window 62.7 to 77.5 C conservative), F2
  SCF9550-30-05, Q3, Q5, JP1, RT1.
- `devices.R10`: R10 is the 2 mohm shunt; the thermistors are four Semitec 103AT-2 on J_TS (the row cites a Murata
  NXRT15XH103 document).
- `devices.F1`: "25 A MINI blade (Littelfuse 297 class) in a Keystone 3568 holder", spec
  `v2/vendor/keystone/littelfuse-297-ficcorp.pdf` (the 287 ATOF is the regular size, which the 3568 does not take).
- A function SECONDARY_OVER_TEMPERATURE (device U2, threshold 70 C, window 62.7 to 77.5 C, delay 4 s, action COUT and
  DOUT: F2 open and Q2 off; test: E3-P plus a heated-NTC bench check with JP1 open reading TP11).
- `CHARGE_TEMPERATURE_WINDOW` and `DISCHARGE_TEMPERATURE_WINDOW`: add "requires FET Options[OTFET] = 1 in the golden image
  (SLUUAQ3A 14.2.1.1; default 0 = no FET action)".
- `PACK_OVER_CURRENT_DISCHARGE_2` (30 A / 20 ms): implemented by the AFE's AOLD, not firmware OCD2 (whose delay is in whole
  seconds, SLUUAQ3A 14.9.7).

## 4. `v2/ecad/tools/pcb_energy_chain.yaml` (owner: energy chain), BAT-F04, O-13

- Every F1 and F3 "25 A ATOF blade" with `i2t_a2s: 1000`, `cold_resistance_mohm: 2.52` and the 287 datasheet: the holder is
  a Keystone 3568 (MINI); the Littelfuse 297 25 A is `interrupting_a: 1000` at 32 VDC, typical `i2t_a2s: 625`,
  `cold_resistance_mohm: 2.36` (`v2/vendor/keystone/littelfuse-297-ficcorp.pdf`). The melting-time note becomes about 2.7
  ms at 480 A and 10.9 ms at 240 A.
- A stage entry for F2 (SCF9550-30-05): rating 30 A, breaking 80 A, below the node's 240 to 480 A prospective fault; the
  order F1 before F2 unproven (no F2 melting I2t published).

## 5. `v2/ecad/tools/gen_pcb_p3.py` and `check_pcb_p.py` (owner: board P placement), O-11

- J_TS2 (PH 1x2), R34 (0603) and TP15 (1.5 mm pad) are new and unplaced. R34 and R33 belong at U2 pin 12 (region SEC,
  `gen_pcb_p3.py:140`); J_TS2 at the board edge beside J_TS; TP15 in TPS2 (TS_SEC is at most about 1.5 V, harmless to
  bridge). The comments at `gen_pcb_p3.py:77` and `:106` still describe R33 as the fixed 10 kohm.
- check_pcb_p.py's SITES and present lists gain J_TS2 (O-1 already lists the round-4 literals).

## 6. `v2/vendor/` (third cycle): the cited documents are filed, split between two streams

Stream PKT files the PDFs (SLUSEG7D, SFFS317A, SLUUAQ3A, ELX1135, ITV9550, PRF, SLUUBF9, AO3400A, 2N7002, JST PH) with their
SOURCES.yaml entries; this stream files only the two TI E2E snapshots nobody else files, with lines in `sources.txt` and
`vendor-status.txt` and a top-level `battery_review_documents` block in `SOURCES.yaml` placed before `parts:` so that it
touches no entry PKT edits. Every hash is in `drafts/vendor-files.txt`, which also records a stale status for the owner of
`vendor-status.txt` (the Samsung 35E sheets marked retired although the ruled pack uses those cells). **Merge PKT and BAT
together and run `python3 v2/docs/review-packets/battery/evidence/check_manifest.py`: it must print RELEASE CHECK PASS**
(it fails in this worktree on PKT's ten rows by design). Simulated at about 17:05 CEST on a copy of this worktree's packet
and v2/vendor with PKT's ten files added from wt/rv-pkt: RELEASE CHECK PASS, 132 rows.

## 7. `v2/docs/CONOPS.md` Charging row (owner: CONOPS), BAT-F06

`CONOPS.md:206` still reads "the kit's loads sit on the pack side of the charger's sense resistor, so shore carries the loads
only up to the programmed charge current". With the round-6 board A (S-04) proposed: "the kit's loads sit on the charger's
VSYS and the pack beyond its sense resistor, so shore carries the loads up to the input limit the host sets (about 31 W
before the host has written it); board E's always-on domain (sensor controller and fans) still sits on the pack side and
shares the charge current; without its host the charger charges at 256 mA, which board E's always-on draw largely takes:
the pack is held, not charged (`review-packets/battery/CHARGER-STATE-SEQUENCE.md`)."

## 8. `v2/docs/EXECUTION-PLAN.md` log entry (owner: integrator)

"26 Sep, review stream BAT (review section 2, checkpoint 4): battery/protection review packet in
`v2/docs/review-packets/battery/`. Secondary over-temperature restored on board P (TS network R34 270R / R33 18k, own NTC on
J_TS2, TP15; the first cycle's 200R / 22k withdrawn because RUT_ACC had been read as the chip's UT accuracy, which is TUT_ACC,
+-5 C), regenerated on box 52646493 with parity of main's board P files first; netlist change J_TS2, R34, TP15 added, R33
10k to 18k, U2 value; gates unchanged except pin_map_lands 81 to 84 judged and lcsc_fill 34 to 37 rows. New fixture
tests/test_pack_secondary_ts.py (fails on main's generator and on the first cycle's netlist, passes on the candidate).
Golden-image requirements now written explicitly, word by word, because SLUUAQ3A states defaults two ways for thirteen
settings and six permanent-fail thresholds (a mechanical sweep of chapter 14, evidence/trm_defaults_check.py); TI's own image
holds both FETs off, so the hazard is a partial image; SUV permanent fail at 1.0 V against 0-V charging (BAT-F14). Findings
BAT-F01 to BAT-F14. The packet's release check (evidence/check_manifest.py) passes once stream PKT's vendor files are merged. Test-plan margins reconciled for the pack at the cells' limits. Review request text
and a named, not contacted, reviewer shortlist prepared; nothing sent."

## 9. New file for the integrator: `v2/ecad/tools/tests/test_pack_secondary_ts.py` (second cycle)

This stream's only file outside its three owned paths, written because the checker required a fixture for the generator
change; nobody else writes it. It reads `v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net` when that netlist's sidecar names this
tree's generator, otherwise the packet's `candidate/pcb-p-pack.net`, otherwise it skips with the reason. Once the candidate
board P files are committed to `pcb-p-pack-p2/`, the committed netlist is the one judged.

## 10. `v2/ecad/tools/pcb_decisions.yaml` or the appendix (owner: integrator), BAT-F01 and BAT-F10

Two session decisions under the owner's standing rule of 26 September 2026, for the decision register if the integrator
records them there: (a) the second level's over-temperature restored with a 270 ohm / 18 kohm TS network, the pack's test
margins reconciled at its cells' limits (`SECONDARY-OT-DECISION.md`); (b) the gauge's host watchdog enabled by an explicit
write (HWDF = 1, 10 s) and every data-flash word of `PRIMARY-CONFIGURATION.md` section 2 written explicitly, with the fresh
device's data flash archived first; (c) third cycle: Protection Configuration 0x03 (CUV recovery needs a charger; SUV checked
with the FETs off), SUV permanent fail at 1.0 V never mapped to the fuse, Shutdown Voltage 2.00 V (Samsung's guideline),
interim permanent-fail words A 0x53, B 0x00, C 0xFB, D 0xF0 pending the reviewer, Open Thermistor deltas at 20.0 C; (d) the
packet's release condition: not sent until its release check passes at the commit sent.

## 11. `v2/ecad/tools/gen_sch_p.py` comments to refresh at board P's next regeneration (owner: this generator's next author)

Two comments in the U2 block are left unchanged in the third cycle because any byte of the generator moves its identity
and would orphan the regenerated candidate netlist (`sch_prov`): the reference `drafts/scripts/ts_network.py` (the published
copy is `v2/docs/review-packets/battery/candidate/ts_network.py`), and "the TS voltage with J_TS2 plugged against unplugged"
for the TP15 check, which the packet now states as a scope reading of the bias pulse or a resistance reading before the cells
are connected (`SECONDARY-OT-DECISION.md` section 4). Board P's 4-layer regeneration (O-11) is the natural place.
