# Integration notes for stream ZER (for the integrating writer only; not a public document)

Source of every change below: `v2/docs/feasibility/ZEROIZE.md` in worktree `rv-zer` (branch `fnd/rv-zer`, base
`1f614233`). This stream wrote only that file and `drafts/*`. Nothing here edits a shared file; each item is text the
integrator may apply, with the reason. Rulings taken under the owner's standing rule of 26 September 2026 are marked.

## 1. Files to file

| Draft | Proposed home | Note |
|---|---|---|
| `drafts/datasheets/microchip-*.pdf` | `v2/vendor/microchip/` | add `sources.txt`, `vendor-status.txt` and `SOURCES.yaml` lines from `drafts/datasheets/SOURCES.md` (URL, capture, sha256) |
| `drafts/datasheets/infineon-slb9673-fw26-datasheet-rev1.4.pdf` | `v2/vendor/infineon/` (new folder) | the fallback part |
| `drafts/datasheets/nxp-*.pdf` | `v2/vendor/nxp/` (new folder) | the second fallback |
| `drafts/datasheets/tcg-*.pdf` | integrator's call (7.6 MB); the document cites them by URL, revision and sha256 | |
| `drafts/datasheets/SOURCES.md` | fold into `v2/vendor/SOURCES.yaml` and `sources.txt` | |
| `drafts/zeroize/zer_config.py` | `v2/docs/feasibility/zeroize/zer_config.py` | stdlib only; `python3 zer_config.py` exits 0 with "PASS: 9 planted defects caught, 0 checks failed" |
| `drafts/zeroize/zer_budget.py` | `v2/docs/feasibility/zeroize/zer_budget.py` | stdlib only; `python3 zer_budget.py` exits 0 with "PASS: 10 planted defects caught, each by its own check; 0 checks failed"; it is the source of the REQ-035 numbers below |
| `drafts/prices/jlc-*.json` | `v2/docs/feasibility/evidence/zeroize/` | the raw catalogue reads the document quotes |

If the homes differ, rewrite the `drafts/...` paths in `ZEROIZE.md` (the header, the revision note and sections 1,
2, 3.1, 3.4, 5, 7 and 9).

## 2. Requirements registry (`v2/ecad/tools/pcb_requirements.yaml` in `i1`, rendered to `REQUIREMENTS-TRACE.md`)

- **ASM-005 `acceptance`** (was "TBD: confirmed from the full ATECC608B datasheet ... or by a bench test on a
  provisioned part"): "Desk: SUPPORTED by public Microchip documentation (ATECC508A complete data sheet DS20005927A
  Tables 2-8, 2-10, 2-15 and section 9.7; ATECC608B-TNGTLS DS40002250B p. 8 and -TFLXTLS DS40002249B p. 9, GenKey mode
  0x04 'to enable key deletion'; ATECC608B summary DS40002239A pp. 12-13) and by Microchip's CryptoAuthLib v3.8.0 test
  that regenerates a slot on a data-locked device (`atca_tests_ecdh.c:62-119`); `v2/docs/feasibility/ZEROIZE.md`
  sections 3 and 4. Physical: Z-EXP-A and Z-EXP-B of ZEROIZE.md section 5 pass on ATECC608B-SSHDA-T parts provisioned
  with the section 3.1 slot map." Keep `status: TBD` until the bench records exist; add the document to `source`.
- **S-35 `title`**: "The ATECC608B slot map of `ZEROIZE.md` section 3.1 shown on the fitted MPN to let both KEKs be
  destroyed after every zone lock, including across an interrupted GenKey (Z-EXP-A and Z-EXP-B), with the SLB 9673
  TPM 2.0 on board B's U8 site as the fallback under switch conditions S1 and S2." Status stays OPEN.
- **REQ-035 `acceptance`**, replace the last sentence ("The time from the end of the hold to the key's destruction is
  TBD ...") with: "(6) Both key-encryption keys are destroyed and verified within 1.5 s of the end of the 5 s hold,
  and (7) the slot rails are cut within 3.0 s of it by a hardware timer that does not wait on the secure element,
  the kit bus or any module (taken by the session under the owner's standing rule of 26 September 2026, from the
  worst case, not the nominal: about 0.52 s with no retry, at most 0.82 s with every retry the wipe allows (at most 6
  GenKey commands in the timed phase, CryptoAuthLib bounded to one bus retry and a 200 ms polling cap, 100 kHz);
  every bus operation ends within 10 ms and the timed phase ends at a 1.5 s deadline whatever the secure element or
  the bus does, so the modules are told to drop their keys before the cut; `ZEROIZE.md` section 3.4,
  `zer_budget.py`)." Then drop `tbd_effect`, or make it "none" as the validator requires. **Corrections of the
  earlier drafts:** the first proposed 1.0 s from "about 0.51 s worst case", which was the nominal figure with no
  retry in it, while the same sequence allowed ten tries per slot (worst case about 2.8 s, above its 1.0 s line; with
  its slot cut 2 s after DONE the slots would have been cut near 4.8 s); the second gave "the timed phase gives up by
  1.88 s", a bound that modelled only a part refusing every poll on a free bus and did not hold on a held bus. Carry
  none of the 1.0 s line, the 0.51 s "worst case", the 1.09 s worst case or the 1.88 s bound anywhere.
- **REQ-035 or REQ-038 `notes`**, one sentence: "Enrolment uses one LUKS keyslot per drive, derived from ECDH with both
  KEKs; no recovery keyslot (`ZEROIZE.md` section 3.3)."
- **Residual risk extension (a consequence, not a new ruling):** the D-03 residual's "a module that reboots while any
  of them is down" also depends, for a module that does not host bank 1, on the bank-1 host module and the KSZ9897R
  (`ZEROIZE.md` section 3.3, from `PANEL.md:5` and `ARCH-PCB-B-IOHA.md:311`). Record it under ASM-002 or S-36 (the
  common modes), not as a change to D-03. It adds no module-power common mode: a normal boot with the secure element
  not answering powers the slots into the recovery state, and only a boot with a wipe due keeps them off
  (`ZEROIZE.md` section 3.5).
- **Residual R7, for the D-09 security-review packet (new this cycle; carry this sentence as written, it is the
  opening sentence of R7 in `ZEROIZE.md` section 8):**

  > The three STM32H743 I/O supervisors share SDA and SCL with the secure element (`gen_sch_b.py:824`, U8 at
  > `:750`), so "only the panel controller commands the part" (P8) holds for them only through firmware rule Z-C3
  > under the owner's D-13 floor of software-verified boot; a supervisor whose firmware breaks it can hold the bus,
  > so the wipe ends ZEROIZE INCOMPLETE with both KEKs intact (the slots are still cut at 3.0 s), or run ECDH on
  > slots 0 and 1 (ReqAuth is clear) and so obtain every drive's unlock secret, or answer in the secure element's
  > place so that the panel records a verified wipe that did not happen.

  Record it in REQ-035's `notes` (or as a residual of S-35) with a pointer to `ZEROIZE.md` section 8, R7; it is a
  residual stated with the design, not a new owner ruling. Firmware rule Z-C3 (I2C target at 0x30 to 0x32 only, never
  a master, never address 0x60) belongs in whatever registry item carries the supervisor firmware's requirements
  (D-13).

## 3. `v2/vendor/SOURCES.yaml`

- `secure-element` (`:834-862`): add the documents of section 1 above; replace `matches_fitted`'s clause "the slot-erase
  behaviour decision 30 depends on are not settled by it (the full datasheet is under NDA)" with "the slot-erase
  behaviour decision 30 depends on is settled at desk level by DS20005927A and the ATECC608B Trust&GO and TrustFLEX data
  sheets (v2/docs/feasibility/ZEROIZE.md section 4), and on the part by Z-EXP-A and Z-EXP-B (owed)"; in `decision_30`,
  replace "PRECONDITION, TBD: ... which only the full (NDA) datasheet settles" with "PRECONDITION: supported by public
  documentation (ZEROIZE.md), bench confirmation owed (Z-EXP-A, Z-EXP-B); fallback SLB 9673 on the U8 site under
  switch conditions S1 and S2".
- `owed` (`:865`): replace "the full ATECC608B datasheet (under NDA) for owner ruling D-03's precondition that the slot
  map is erasable" with "Z-EXP-A and Z-EXP-B records (ZEROIZE.md section 5); the NDA data sheet is no longer needed for
  D-03's precondition".
- The H743 entry (`:304-307`), after "(TBD; effect: a wipe step that needs CRYP, HASH or secure access mode would reopen
  the mismatch)": add "Resolved for ZEROIZE on 26 September 2026: the design of v2/docs/feasibility/ZEROIZE.md uses no
  supervisor function (the panel RP2040, the ATECC608B and the modules' LUKS do the whole job; firmware rule Z-C3 only
  restricts what the supervisors' firmware may do on the kit bus, which needs no H753-only unit), so this reopen
  condition does not fire; the secure-boot condition is unaffected."
- `lcsc_reading` for C1518769 may be refreshed: JLCPCB 2,344 in stock at 0.9955 USD, read 2026-09-26T12:27:48Z
  (`drafts/prices/jlc-ATECC608B-SSHDA-T.json`). `PARTS.md:118-119` still shows WRONG_MODEL C2836813 for this part:
  that is W6's certification row, not touched by this stream.

## 4. Narrative documents (one sentence each; the same fact everywhere)

The fact: "The precondition is supported by public Microchip documentation (GenKey over an updatable, non-lockable
slot after every zone lock; `v2/docs/feasibility/ZEROIZE.md`); the bench confirmation on the fitted part (Z-EXP-A and
Z-EXP-B) is owed; the TPM 2.0 fallback is the SLB 9673 on board B's U8 site."

- `PANEL.md:129`, replace "it rests on one precondition still TBD: the secure element's slot map must let that key be
  erased (the full ATECC608B datasheet is under NDA; a TPM 2.0 is the fallback)" with the fact.
- `CONOPS.md:212` last cell and `CONOPS.md:394` ("the secure element's erasable slot map is a precondition still
  TBD"), `V2-SPEC.md:34` ("precondition: an erasable ATECC608B slot map (NDA datasheet), a TPM 2.0 the fallback"),
  `V2-SPEC.md:76` ("ATECC608B (its full datasheet is under NDA)") and `pcb_decisions.yaml:219-221` (decision 30's
  outcome: "which the summary datasheet ... does not state and the full datasheet, under NDA, is needed for"): the fact.
- `ARCHITECTURE.md` (worktree `i3`) section 10.3, row "precondition": "As generated today" becomes "supported at desk
  level by public documentation (ZEROIZE.md sections 3 and 4)"; "Owed" becomes "Z-EXP-A and Z-EXP-B on the fitted MPN
  before board B's layout entry; the SLB 9673 fallback under S1 and S2". Section 12 or wherever the feasibility
  blockers are listed: add FB-ZER-1 with the table of `ZEROIZE.md` section 7.
- `TEST-PLAN.md:46` (functional check): the owed ZEROIZE demonstration (the architecture page says so) can cite REQ-035's
  five clauses plus the two timing pass lines; Z-EXP-A to C are pre-build experiments, not TEST-PLAN rows.
- `ARCH-PCB-B-IOHA.md:147` ("The kit I2C bus is one bus with one master on another board"): add "The single master
  is a firmware property for the three supervisors, which share the bus as targets at 0x30 to 0x32 (firmware rule
  Z-C3 of `v2/docs/feasibility/ZEROIZE.md`, under D-13; residual R7 there)."
- `PANEL.md` section 7 (`:137-150`, the kit bus address table) does not list the supervisors at 0x30, 0x31 and 0x32
  that `ARCH-PCB-B-IOHA.md:96` gives them; add the row ("0x30, 0x31, 0x32 | STM32H743 I/O supervisors, I2C targets
  (status); firmware rule Z-C3 | B16") so the only table of who is on the bus names every part with firmware on it.
- `RED-TEAM-2026-09-09.md:420` is a dated record; leave it, and let `ZEROIZE.md` section 1 item 2 carry the correction.

## 5. Execution log line (`v2/docs/EXECUTION-PLAN.md`)

"26 Sep: review section 3, ZEROIZE: the ATECC608B precondition closed at desk level from public Microchip documents
and CryptoAuthLib (GenKey mode 0x04 over an updatable, non-lockable slot after every zone lock); design, slot map,
wipe sequence and boot logic written; bench experiments Z-EXP-A to C specified with pass lines; SLB 9673 fallback
assessed (board B's U8 site only, no JLC stock); FB-ZER-1 recorded in `v2/docs/feasibility/ZEROIZE.md`. Checker
corrections the same day: P8 is settled by the netlist for the modules only, and by firmware rule Z-C3 under D-13
for the three supervisors that share the kit bus (residual R7, for the D-09 packet); the wipe budget now counts
every retry (0.52 s nominal, pass lines 1.5 s and 3.0 s, the slot cut on a hardware alarm). Second check the same
day: the timed phase is bounded on a held bus too (10 ms HAL timeout, 1.5 s deadline, 6 GenKey commands, worst case
0.82 s), and a normal boot with the secure element silent powers the slots into the recovery state."

## 6. Items that are the owner's (not decided by this stream)

- The spend for Z-EXP-A and Z-EXP-B (D-09: "nothing is spent beyond the voucher without a quote and the owner's
  approval", `CONOPS.md:400`). Prepared list: one Microchip DM320118, one MikroElektronika Secure SOIC click, ten
  ATECC608B-SSHDA-T, one Raspberry Pi Pico, one load-switch breakout, jumpers. Prices other than the SE's: TBD.

## 7. Main moved to `458b2873` during the third cycle: where the cited lines went

`ZEROIZE.md` cites repository lines at `1f614233`. `458b2873` (boards A, B and D take their round-4 and round-6
circuit corrections) moved the lines below; the gen_sch_c.py lines, `ARCH-PCB-B-IOHA.md`, `PANEL.md`, `CONOPS.md`,
`pcb_decisions.yaml` and `v2/vendor/SOURCES.yaml` did not change. Each new line number was found by matching the
cited line's text in `458b2873`. If the integrator rebases the document, rewrite the citations with this table.

| Cited at `1f614233` | At `458b2873` | Note |
|---|---|---|
| `gen_sch_b.py:750` (U8) | `:1046` | unchanged text |
| `gen_sch_b.py:824` (supervisor pins 35 and 36 on SDA and SCL, PB1 and PB2) | `:1140` (pins 92 and 93, SCL on PB6 and SDA on PB7, I2C1; comment `:1137-1139`) | the round-6 move, now committed; R7 and Z-C3 already describe it, and it changes no conclusion |
| `gen_sch_b.py:261` (H753 pin map) | the H743 map at `:287` | same names for pins 35, 36, 92 and 93 |
| `gen_sch_b.py:816-828` (supervisor pin map), `:823` (HB1..3) | `:1129-1144`, `:1136` | |
| `gen_sch_b.py:832` (BOOT0 pull-down), `:840` (SWD pads) | `:1149`, `:1157` | |
| `gen_sch_b.py:847-854` (CAN termination) | `:1165-1179` | controller A's end now sits behind 0 Ohm break links (`:1169-1177`) |
| `gen_sch_b.py:767` (panel connector: HB, SLOT_EN) | `:1063` | |
| `gen_sch_b.py:360`, `:571` (module I2C to the bench headers) | `:403`, `:816` | |
| `gen_sch_b.py:507-513`, `:613`, `:639`, `:653-655`, `:786` | `:748-754`, `:858`, `:884`, `:898-900`, `:1085` | |
| `gen_sch_a.py:407` (100k on SLOT_EN1..3 in `buck5`) | `:821` for slots 1 and 3; slot 2 is now an LM5176 stage and keeps its 100k as R34 at `:879` | the watchdog backstop of 3.4 step 0 still holds on all three enables |
| `gen_sch_a.py:573`, `:581` | `:1150`, `:1174` | |
