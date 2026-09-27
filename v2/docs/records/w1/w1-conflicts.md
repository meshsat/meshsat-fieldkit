# W1 conflict list (draft for the integrator, MESHSAT-1357)

Written 25 September 2026 by workstream W1; revised the same day (round 2) after the independent challenge
and eleven adjudications (A01 to A11, folders under the session scratchpad `adj/`). Base: main `82dd1e4d`.
Each entry names both sources with file and line, says whether the point was read in the artefact (VERIFIED)
or derived (INFERRED), what it blocks, and who resolves it. "Session" means an engineering fix the design
sessions own under the 21 September ruling; "owner" means product, money, scope or risk acceptance (the
two-part test of that ruling). Candidate records in `drafts/w1-requirements.yaml` point here through
`conflict_ref`. Owner decision IDs (D-nn) and session items (S-nn) are those of `drafts/w1-decisions.md`.

**Correction to the plan itself (C-04), restated in round 2:** the plan's bullet "PANEL.md says a kit
without its panel does not transmit, but only APRS is actually inhibited" repeats a stale sentence of
PANEL.md. The generated board A netlist pulls `EMCON_HW` LOW (inhibited), board D pulls `TX_INHIBIT_n` LOW,
and board A pulls `SLOT_EN1..3` LOW. With the panel unplugged, every EMCON-gated transmitter is inhibited
AND no compute slot powers, so nothing that hangs off a compute module (its own WiFi and Bluetooth, the M.2
cards) is powered either: the kit transmits nothing. Round 1 said the compute modules' own radios stay live
with the panel unplugged; that was wrong for the unplugged case (they are unpowered). The compute-radio gap
of C-03 is real with the panel present and EMCON closed. PANEL.md's same sentence also says the kit "charges
and computes" without its panel; it does neither as generated (C-04).

| ID | Topic | Severity | Status | Resolver |
|---|---|---|---|---|
| C-01 | Runtime and peak power carried from a withdrawn pack | major | VERIFIED | session (power states, done), owner (runtime target, D-06) |
| C-02 | IOHA failover mapping, section 4 against section 15 | major | VERIFIED | session (doc fix, S-06) |
| C-03 | EMCON does not reach the CM5 radios; U6 drives pins that may only be driven low; RF-002 reads a false PASS | critical | VERIFIED | session (board B, S-01; rule instrument, S-02) |
| C-04 | PANEL.md section 7 describes R102 backwards and says a panel-less kit charges and computes | major | VERIFIED | session (doc fix, S-07) |
| C-05 | Envelope hot end set by the SGP41, which 32.54 picked and the generator leaves out | major | VERIFIED | session (fit the part, S-10) |
| C-06 | TEST-PLAN limits outside the envelope; E5's vent step against the no-vent ruling | major | VERIFIED | W5 (purpose per test), owner (margins, D-02a) |
| C-07 | Vibration and shock severities: open in the envelope, specific in TEST-PLAN | minor | VERIFIED | session (severity mapping, S-15) |
| C-08 | Altitude: proposed, left open, and tested against | minor | VERIFIED | owner (air carriage, D-02c), session (values) |
| C-09 | ZEROIZE described inconsistently: who wipes and what is erased | critical | VERIFIED | owner (meaning, D-03), session (mechanism, decision 30) |
| C-10 | Tamper switch approved and sited, in no generator | major | VERIFIED | session (implement, S-11); owner only for its role as a trigger (D-03) |
| C-11 | Pack pocket: east 58 x 240 x 48 in the record, west 58 x 160 x 48 in the plan and handover | minor | VERIFIED | integrator (plan text) |
| C-12 | `_product` facts stale against decision 34 | minor | VERIFIED | session |
| C-13 | Storage charge "ex-factory 30 percent" for a built pack | minor | VERIFIED | session (W2) |
| C-14 | WITHDRAWN as a conflict; restated as the cold-soak start-up case | n/a | INFERRED | owner (D-02d) |
| C-15 | Pack headers name "about 200 Wh" without the cell; what physically fits | minor | INFERRED | session (headers), owner (D-06) |
| C-16 | Reduced mode defined two ways, no trigger sensor, no closed-lid test state | major | VERIFIED | owner (closed-lid use, D-02b), session |
| C-17 | Three wireless CM5, one WiFi 2.4 jack; antenna certification path | major | VERIFIED (jack), INFERRED (certification) | session (S-16), owner through D-04 |
| C-18 | Dual SIM: eSIM plus nano-SIM, or two nano-SIM; SIM 2 on the wrong pins | minor | VERIFIED | session (S-13) |
| C-19 | "5G hardware design owed" is stale; the 5G socket bought is key M | major | VERIFIED | session (socket, S-12), owner (jack count, D-07) |
| C-20 | EMCON removes power, so receivers stop too | major | VERIFIED | owner (D-05) |
| C-21 | Peak case against the declared pack peak current at end of discharge | major | INFERRED | owner (D-11), session (thresholds) |
| C-22 | Holdover clock: "TCXO-disciplined RTC fed by the GNSS pulse" against a DS3231M | minor | INFERRED | session |
| C-23 | Two charge-inhibit paths, PANEL.md describes one | minor | VERIFIED | session (doc) |
| C-24 | Public README device lines after 9d66316f | minor | VERIFIED | integrator (baseline hygiene) |
| C-25 | Items from the plan's list that W1 did not re-verify | n/a | not re-verified | W7 |
| C-26 | DCF77 pulse: "fanned out to every slot" against one sensor controller input | minor | VERIFIED | session (S-17) |
| C-27 | What the charger does without a host, and what it reads | major | VERIFIED (A02) | session (S-03, S-04, docs) |
| C-28 | The design record's EMCON gate list against the generated gates | major | VERIFIED (A11) | session (S-01, S-02) |
| C-29 | Pack SMBus lead: two ends of different families, and a third in ASSEMBLY.md | major | VERIFIED (A07) | session (S-05) |
| C-30 | ASSEMBLY.md's pack section and RockBLOCK standoffs against the committed boards | minor | VERIFIED (A06) | session (docs), owner (D-06) |
| C-31 | SOS has a switch, a lamp and a sounder pattern, and no defined action | major | VERIFIED | owner (D-10) |
| C-32 | Device-rail and slot power-up rest on the panel controller and an unspecified expander parameter | critical | INFERRED (A01) | session (S-08) |

---

### C-01 Runtime and peak power carried from a withdrawn pack

- **Source A:** `v2/docs/V2-SPEC.md:23`: "about 8 to 9.5 h typical (29 W: monitor on, radios idle, APRS
  beacons), 5 to 6 h with the three-CM5 cluster busy, 11 to 13.5 h dimmed; peak about 150 W".
- **Source B:** appendix `:2775` (32.49): the 29 W and 150 W are the one-CM5 set with one BB-2590; `:2846`
  (32.52 item 3): "about 50 W typical, about 200 W peak without the outlets, up to 290 W with them";
  `:3056` and `:3062` (32.62): the BB-2590/U is withdrawn and the pack is a built 4S pack.
- **Adjudicated (A05, VERIFIED arithmetic):** the 32.52 line items sum to 45.0 W and 178 W; with the 12 %
  allowance, 50.4 W and 199 W, so 32.52's figures are at the battery; the 290 W adds 90 W of outlets without
  the allowance. The record's runtimes divide nominal pack energy by these figures with no derating. On the
  current kit, V2-SPEC's words describe PS-IDLE-SPEC (32.4 W), the 5 to 6 h describes PS-TYP (60.1 W), and
  the 150 W is superseded by PS-ALLTX (227.0 W). All PROVISIONAL.
- **Also:** `:2932` (32.55) "4 to 17 A from the node at 12 V, inside the pack's 18 A peak" quotes the
  BB-2590's own rating (`:2913`).
- **Effect:** every runtime figure in public text is invalid until V2-SPEC line 23 is replaced; CONOPS
  section 4a carries the PROVISIONAL per-state figures.
- **Resolution:** the owner sets a runtime target (D-06) after the case measurement (D-08); V2-SPEC line 23
  is replaced then, not before.

### C-02 IOHA failover mapping

- **Source A:** `v2/docs/ARCH-PCB-B-IOHA.md:70-72` (section 4): bank 1 fails over to CM5-B (slot 2), bank 2
  to slot 3, bank 3 to slot 1. `v2/docs/PANEL.md:5` agrees for bank 1 ("failover host is slot 2").
- **Source B:** `v2/docs/ARCH-PCB-B-IOHA.md:292-303` (section 15, "read off the netlist"): bank 1 to slot 3,
  bank 2 to slot 1, bank 3 to slot 2.
- **The design:** `v2/ecad/tools/gen_sch_b.py:543` `f = s % 3 + 1` with the TMUXHS4212 port C on `HOST{f}_1*`
  (lines 544-547): bank 1 to slot 2, bank 2 to slot 3, bank 3 to slot 1. Section 4 is right; section 15's
  "after the home module is lost" column is wrong, and so are its "removed by one further failure" cells.
  W3 and W5 agree.
- **Effect:** anyone planning a degraded mission from section 15 picks the wrong surviving module. CONOPS M5
  follows the generator. The product brief's compute bullet was rewritten in round 2 to state the owner's
  requirement and name the two bearers with no second path, rather than rely on section 15.
- **Resolution:** correct section 15 (session; W3 owns the B documents).

### C-03 EMCON does not reach the CM5 radios; U6 drives pins that may only be driven low; RF-002 false PASS

- **Requirement:** appendix `:2787` (32.50 item 3): "EMCON kills every transmitter in hardware"; `V2-SPEC.md:24`;
  rule RF-002 ("every transmitter can be inhibited by a hardware path that does not depend on software").
- **Design (A11, VERIFIED on the regenerated netlist):** `WL_nDIS1..3` and `BT_nDIS1..3` have exactly two
  nodes each: the CM5 pin (89 or 91) and U6 `IO1_0..IO1_5` (`gen_sch_b.py:378`, `:743`). U6 is a PCA9555 on
  the kit I2C bus, powered from the always-on `+3V3_DEV`. The three modules' own WiFi and Bluetooth are
  silenced only by software, and not at all when the panel controller (the bus master) is dead. A firmware
  path exists (the panel RP2040 reads `EMCON_HW` on GPIO21 and masters U6), but it is software.
- **The push-pull defect (challenger, VERIFIED):** the CM5 datasheet (release 3, sections 2.1.1 and 2.1.2)
  says these pins "may only be driven low; can't be driven high" and pulls them up internally through 1.8 k
  to the module's own 3.3 V; section 3.1 says no pin should be powered before the module's 5 V rail is active.
  U6 is push-pull on an always-on rail, so writing a 1 drives the pin high, and into a slot that is switched
  off it back-feeds the module through that 1.8 k. Configuring U6's pin as an input does not cure it: the
  fitted TI PCA9555 has an internal pull-up of about 100 k to its supply on every I/O (SCPS131J section 8.1,
  Fig 8-2; A01), which still sources current into an unpowered module.
- **Fix (session, S-01):** no driver may source current into these six pins. Each pin is pulled low through
  an open-drain element (or two in parallel), released only when BOTH the software control from U6 and
  `EMCON_HW` are high; U6's own output and its internal pull-up never touch the CM5 pin. The part choice is the
  session's at Review D. The earlier recommendation to keep "the U6 software drive for normal control" is
  withdrawn.
- **RF-002 false PASS (challenger, VERIFIED):** `PCB-RULE-STATUS-B.md:53` reads "inhibit_chain_b PASS of 3"
  and `pcb_rules_coverage.yaml:607-615` marks RF-002 ENFORCED with gap NONE; the instrument checks the EMCON
  line's chain shape, not that every transmitter is gated. Fix (session, S-02): the instrument enumerates
  every transmitter (the section 4b table of CONOPS) and fails on any with no hardware gate; until then RF-002
  on board B reads FAIL or INCONCLUSIVE, not PASS.
- **Three different EMCON lists, none naming the CM5 radios:** `V2-SPEC.md:24`, `PANEL.md:111`, appendix
  `:2930`. See C-28 for the list against the generators.
- **Resolution:** session, board B schematic change and the rule instrument. Only if the owner wants the CM5
  radios outside EMCON does the requirement change, and then it must say so (no option in D-05 proposes it).

### C-04 PANEL.md section 7 describes R102 backwards and says a panel-less kit charges and computes

- **Source A:** `v2/docs/PANEL.md:130`: "With the ribbon unplugged the kit fails safe: A22 pulls `EMCON_HW`
  high (`R102`) and D8 pulls `TX_INHIBIT_n` low (`R2`), so every transmitter rail gate stays open and the PA
  cannot key ... A kit without its panel charges and computes but does not transmit."
- **Source B:** `v2/docs/PANEL.md:110`: "A22, B16 and D9 each hold it down with 100k so a cut ribbon
  inhibits"; `gen_sch_a.py:537` `r("R102", "100k", "EMCON_HW", "GND")`; `gen_sch_b.py:737` R58 the same;
  the committed netlist `v2/ecad/pcb-a-power-a23/out/pcb-a-power.net`: R102 pin 1 on `EMCON_HW`, pin 2 on
  `GND`.
- **"Computes" is false as generated (A01, VERIFIED wiring):** `SLOT_EN1..3` are held off by 100 k
  pull-downs on board A and raised only by the panel RP2040 (GPIO13 to 15); without the panel no slot powers.
- **"Charges" is false as generated (A02):** the charger needs its host (the panel RP2040 masters the bus);
  without writes it falls back to a 256 mA default below every power state's load, and as generated its
  cell-count strap selects 2S, so nothing charges the 4S pack at all (C-27).
- **Effect:** the design is fail-safe for transmission, and the document says the opposite for the rail
  gates while claiming two behaviours the design does not have. The plan's section 1 bullet inherited the
  stale sentence (see the correction at the top).
- **Resolution:** session doc fix of PANEL.md section 7 (S-07), after S-03, S-04 and S-08 decide what the
  true panel-less behaviour will be; the integrator restates the plan bullet. W3's proposal to pull SLOT_EN up
  is a session engineering choice (S-08), not an owner question.

### C-05 Envelope hot end set by the SGP41, which 32.54 picked and the generator leaves out

- **Source A (the envelope):** `OPERATING-ENVELOPE.md:42` names the Sensirion SGP41 in the battery bay
  (-20 to +55 C, `v2/vendor/sensirion/sgp41-datasheet.pdf`) as a bounding part; `:82-83` derive the +39 C and
  +45 C ambient ceilings from it; `:100` and `pcb_envelope.yaml:30` make the +35 C reduced-mode carve-out keep
  "the inside air under the +55 C that the battery-bay sensor and the pack need"; `pcb_part_temps.yaml:38-41`
  declares it; decision 34's evidence (`pcb_decisions.yaml:514`) repeats it.
- **Source B (the pick):** appendix `:2896` (32.54, the research gate's picks, 7 Sep 2026): "Bosch BME688 ...
  one inside, one in the outside pod, with the Sensirion SGP41 (C3659325 ...) in the battery bay". The design
  record picked BOTH parts. `V2-SPEC.md:86` lists "the gas sensor" separately from the BME688 on E6.
- **Source C (the generator):** no `gen_sch_*.py` names an SGP41; board E fits a BME688 (`gen_sch_e.py:367-369`,
  -40 to +85 C per BST-BME688-DS000-03 revision 1.3).
- **So the defect is the generator's omission, not the envelope.** Round 1 recommended recomputing the hot
  end from the fitted BME688; that is withdrawn. It would have treated an omission as the design and widened
  the envelope in the convenient direction.
- **Also:** the owner approved "battery-bay hydrogen + VOC" sensing (sensor walk-through, `:2802`); the SGP41
  is a VOC and NOx sensor, and whether it answers to hydrogen at the levels that matter is **TBD** (effect:
  whether CAND-066's hydrogen half has a sensor at all).
- **Resolution:** session fits the SGP41 in the battery bay (board E or the pack board, wherever the bay's air
  is sampled; S-10). The hot end stays as adopted until the part is fitted, or until a recorded owner ruling
  drops it (dropping an approved sensor changes what the kit is, so it would be the owner's). Decision 34's
  pin is not touched by this entry.

### C-06 TEST-PLAN limits outside the envelope, and the vent step

- **Source A (envelope):** `OPERATING-ENVELOPE.md:94` in use -20 to +40 C; `:103` storage -20 to +45 C for
  three months; `:106` non-condensing in use; appendix `:2864` (32.53) no vent opening anywhere.
- **Source B (tests):** `TEST-PLAN.md:18` E3 storage 24 h at +71 C, operation 4 h at +55 C; `:19` E4 storage
  24 h at -33 C; `:20` E5 95 % RH at 30 to 60 C "deployed with the vent open"; `:23` E8 "latches, vent and
  connectors operate".
- **Not assumed to be errors (plan condition 3):** +55, +71 and -33 C may be deliberate qualification
  margins; MIL-STD-810 is not held in the tree, so where the figures come from is not verified. No test
  states its purpose.
- **Stale:** E5's "deployed with the vent open": there is no vent to open (32.53 item 1).
- **Ambiguous, not stale (challenger):** E8's "vent" plausibly means Peli's pressure valve, which 32.53 keeps,
  E9 relies on, and blowing dust can foul. W5 resolves the wording.
- **Resolution:** W5 records each test's purpose and its limit source; E5's vent step is corrected. The owner
  rules the margins (D-02a).

### C-07 Vibration and shock severities

- **Source A:** `OPERATING-ENVELOPE.md:116-119` "No severity is chosen yet; choosing one is part of decision
  34"; `pcb_envelope.yaml:47-50` lists them as open.
- **Source B:** `TEST-PLAN.md:16-17`: E1 26 drops from 1.22 m, E2 composite wheeled vehicle 1 h per axis.
- **Effect:** REL-001 cannot close; TEST-PLAN's profiles look like requirements and are not.
- **Resolution (round 2):** the severity mapping is an engineering choice (challenger; 21 Sep ruling): the
  session declares E1 and E2 as the prototype's severities (S-15). It is the owner's only if he wants a
  qualification claim beyond the prototype, which D-04 covers.

### C-08 Altitude

- **Source A:** `OPERATING-ENVELOPE.md:111-114` proposes 0 to 3000 m in use, 0 to 4500 m in transport;
  decision 34 leaves altitude open (`pcb_envelope.yaml:47-48`).
- **Source B:** `TEST-PLAN.md:24` E9 tests storage at 4,500 m and operation at 3,000 m.
- **Resolution:** the one fact only the owner has: will the kit be carried in an unpressurised aircraft hold
  (D-02c). The values follow from the answer (session).

### C-09 ZEROIZE described inconsistently

- **A, V2-SPEC:** `V2-SPEC.md:33` the panel controller carries "the hardware EMCON and ZEROIZE logic
  independent of any module"; `:34` "secure element behind ZEROIZE (element wiped, disk-key wipe line
  asserted), encrypted drives". Appendix `:2840` (32.52) the same; `:2789` (32.50 item 5) "keys wiped in
  milliseconds"; `:2802` (16f) "ZEROIZE wipes element and disk keys".
- **B, PANEL.md section 6:** `PANEL.md:112`: "B16's secure element and the encrypted drives are wiped by the
  supervisor on the falling edge (hardware line to the slots)".
- **C, PANEL.md preamble:** `PANEL.md:5` lists ZEROIZE among the lines "that must work without any software".
- **D, decision 30:** `pcb_decisions.yaml:207-233`: the line reaches exactly one processor, the panel RP2040
  (board C U3 pin 34); on A, B and D it travels only to connectors, test points and pull-ups (board A R117,
  `gen_sch_a.py:573`); the drives hang off the modules, which do not see the line.
- **Checked:** `gen_sch_b.py:766`, `:783`, `:786`: on board B `ZEROIZE_HW` touches only J_PANEL, J_AB1 and a
  test point; the I/O supervisors are not on it. "The supervisor" of PANEL.md:112 is no device, and the
  "disk-key wipe line" of V2-SPEC:34 exists nowhere.
- **Not a conflict (challenger):** PANEL.md:112's falling edge and PANEL.md:147's 5 s hold fit together: the
  edge arms, the hold completes, flipping back aborts. Round 1's "four incompatible ways" overstated it; the
  real disagreements are who wipes and what is erased.
- **Effect:** no single statement of what is erased, by what, or what a power loss during the hold does.
  SCH-004 is blocked on six boards by decision 30.
- **Resolution:** owner rules what is erased, the triggers and the power-loss behaviour (D-03); the session
  closes decision 30 on the mechanism and chooses the success indications.

### C-10 Tamper switch approved and sited, in no generator

- **Required:** appendix `:2790` (32.50 item 6) "Case-open and tamper switch feeding ZEROIZE logic and the
  log | one sealed switch under the frame"; `:2848` (32.52 item 4, the approved floor plan) sites "the tamper
  switch input" on E6; `V2-SPEC.md:34`; `TEST-PLAN.md:46` "the tamper switch logs the lid".
- **Design:** no `gen_sch_*.py` contains tamper, case-open, lid or reed.
- **Effect:** the functional check line cannot pass; the reduced mode has no lid sensor (C-16).
- **Resolution (round 2):** implementing it is engineering: the function is approved and its input is sited
  (session, S-11; W5 recommends the always-powered sensor controller on E, `gen_sch_e.py:90`). Only its role
  as a ZEROIZE trigger (log only, or wipe) is the owner's, inside D-03. Withdrawing it would be the owner's,
  and nobody proposes that.

### C-11 Pack pocket

- **Record:** appendix `:3060-3062` (32.62): the pack goes in the EAST pocket, about 58 x 240 x 48 mm; the
  west pocket, about 58 x 160 x 48 mm, "stays for a second pack"; `V2-SPEC.md:20`; `gen_sch_p.py:6`.
- **Plan and handover:** plan section 4 W2 ("volume in the 58 x 160 x 48 mm pocket") and the fieldkit
  handover's 7 Sep 13:10 paragraph quote the first half of 32.62 only.
- **Adjudicated (A06, INFERRED from the committed B21 underside at Z 47.9):** nothing fits the west pocket
  (a 4S3P 18650 block with its board is 205.5 mm long against 160), so the "second pack in the west pocket"
  of 32.62 is not available as drawn.
- **Resolution:** integrator corrects the plan text; W2 and W4 use the east pocket; C-15 and D-06 carry the
  capacity consequence.

### C-12 `_product` facts stale

- `pcb_board_facts.yaml:282` "no temperature range ruled yet"; `:281` five operating modes.
- Against: decision 34 ruled 21 Sep 2026 (`pcb_envelope.yaml:14-17`); CONOPS section 4 names fifteen modes
  (fourteen in round 1, plus SOS) and eleven power states (section 4a).
- Resolution: session, when the CONOPS is accepted.

### C-13 Storage charge for a built pack

- `OPERATING-ENVELOPE.md:103-104`: storage "at the pack's ex-factory 30 percent charge".
- Against: appendix `:3058` and `:3064`: the pack is built, not bought; the gauge's golden image is loaded
  over SMBus by the builder. There is no ex-factory state.
- Resolution: session (W2) names the storage state of charge and the gauge's storage setting. Any edit to the
  envelope document takes pcb_envelope.yaml's pin away until it is re-read and re-pinned.

### C-14 WITHDRAWN as a conflict; restated as the cold-soak start-up case

- Round 1 called the -10 C ambient carve-out (`OPERATING-ENVELOPE.md:96-97`) loose wording against the 0 C
  cell charge limit. The challenger showed it is consistent: with one module the inside air runs about 10 K
  over ambient, so -10 C ambient puts the cells near their 0 C charge limit.
- What remains is a start-up case: a kit cold-soaked below the cells' own -10 C discharge limit (Samsung
  INR18650-35E specification 3.12 and 7.5, about 40 % capacity at -10 C) cannot start from its pack, and the
  heater mat needs power the gauge will not release. W2's finding F-PK-01.
- Resolution: owner, D-02d (in scope with a pre-warm path, or out of scope with the carve-out extended).

### C-15 Pack headers name "about 200 Wh" without the cell; what physically fits

- `V2-SPEC.md:20`, `pcb_pack_protection.yaml:24`, `pcb_energy_chain.yaml:46`, `gen_sch_p.py:7`: "4S3P or
  4S4P, about 200 Wh" or "4S4P 18650 or 4S3P 21700, about 200 Wh" (32.62 `:3062`: 4S4P 18650 3.5 Ah cells,
  14 Ah, about 200 Wh; or 21700 4S3P 5 Ah, 216 Wh). No 21700 cell sheet is held in `v2/vendor/battery/`.
- **Not a conflict (challenger, VERIFIED):** `pcb_pack_protection.yaml:17-18` declares 4S3P the WORST case
  for every current limit, and TEST-PLAN.md:54 says "the pack's worst parallel count". Round 1's "a
  configuration nobody proposed" is withdrawn.
- **Adjudicated (A06, INFERRED):** at most about 145 Wh fits: 4S3P 18650 (144.7 Wh minimum) or 4S2P 21700
  (about 144 Wh), in the east pocket only, shrink-wrapped, not in `pack_4s.py`'s walled box. The 4S3P fit
  leaves 1.35 mm across the pocket, less than the case wall uncertainty, so it waits on the case measurement.
  No 4S4P (193 Wh) fits either pocket while board P stays beside the cells.
- Resolution: session aligns the headers on one cell and parallel count once D-06 is ruled; owner D-06.

### C-16 Reduced mode, trigger, and closed-lid state

- `OPERATING-ENVELOPE.md:100` and `pcb_envelope.yaml:30`: reduced mode = "one module"; `:131` trigger
  "lid closed, or above +35 C ambient".
- Appendix `:2860` (32.53): "the closed-lid transport mode is the reduced mode (monitor off, cluster idle)".
- The two definitions are PS-RED 19.7 W and PS-RED-b 25.4 W at the battery (A05, PROVISIONAL).
- No generator senses the lid (C-10). `TEST-PLAN.md:8` has no closed-lid operating state (its transit state
  has antennas off and cables out).
- Resolution: owner says whether the kit must work lid-closed and with which bearers (D-02b); the session
  then writes one definition and wires the lid sense (S-11).

### C-17 Three wireless CM5, one WiFi 2.4 jack

- Appendix `:2758` (32.49 item 1): CM5 wireless; `:2764` (item 7) the certified antenna kit on the WIFI 2.4
  jack; `:2948` (32.56) one blind-mate path J_BM3 for "the CM5 kit antenna".
- `v2/vendor/cm5/cm5-datasheet.pdf` (release 3): "If you use a third-party antenna, you must obtain your own
  separate certification"; the antenna is selected at boot (`dtparam=ant1` internal, `ant2` U.FL).
- VERIFIED: `V2-SPEC.md:43` says "the CM5's own radio", singular, and no generator part says which slot's
  radio feeds the jack or what the other two use.
- INFERRED (challenger): whether a blind-mate plus bulkhead path keeps the kit antenna's certification. The
  appendix (`:2718`) claims "the antenna kit's own antenna keeps the module's certification"; the datasheet
  does not say whether an intermediate path voids it.
- Resolution: session names the slot and the other two radios' state (S-16); the certification question
  matters only through the market scope (D-04).

### C-18 Dual SIM, and SIM 2 on the wrong pins

- `V2-SPEC.md:41` and appendix `:2796` (32.50 item 12): "dual SIM (eSIM plus nano-SIM)".
- `gen_sch_b.py:474-485`: two nano-SIM holders, SIM 2 on the module's GPIO pins "to confirm".
- `quectel-rm520n-series-hardware-design-v1.1.pdf` (held): eSIM is optional and internal, on the SIM2
  interface.
- **Adjudicated (A08, VERIFIED in the generator and the committed B19 netlist):** SIM 2 is wired to the wrong
  pins: the generator puts SIM2_CLK on pin 40, IO on 42, RST on 44 and VCC on 46; the module has 40 USIM2_DET,
  42 USIM2_DATA, 44 USIM2_CLK, 46 USIM2_RST, 48 USIM2_VDD, and pin 48 is unconnected. SIM 2 cannot work as
  drawn.
- Resolution: session (S-13); if eSIM is kept, the ordered module variant must carry it.

### C-19 "5G hardware design owed" is stale; the 5G socket bought is key M

- `V2-SPEC.md:41`, `:76`; `ARCH-PCB-B-IOHA.md:198` (open ruling 4 "gated on Quectel's hardware design guide,
  which is not yet on file"); appendix `:2818`.
- Held now: `v2/vendor/quectel/quectel-rm520n-series-hardware-design-v1.1.pdf` (version 1.1, 2023-03-16) and
  `quectel-rm520n-gl-hardware-design-v1.0.pdf`: four antenna ports ANT0 to ANT3; operating -30 to +75 C.
- **Adjudicated (A08, VERIFIED):** TE 1-2199119-5 (LCSC C574849), named in `gen_sch_b.py` near line 479 as a
  "B-key 3052 socket", is a KEY M connector (TE drawing C-2199119 rev F, sheet 2); the RM520N-GL is key B
  only. The appendix pick (`:2884`) was conditional on the drawing confirming key B, and the condition fails.
  The file `v2/vendor/m2/te-2199119-m2-b-key.pdf` is TE's quick reference guide, not the drawing. No file
  records which ANTx port goes to which jack; `ASSEMBLY.md:99` names "MAIN and DIV" connectors that the
  RM520N-GL does not have (they are the EG25-G's names).
- Resolution: session replaces the socket (A08 recommends TE 2199119-3, LCSC C590866; a substitution stays a
  mismatch until its land is proven) and wires ANT0 and ANT2 if two jacks stay (S-12); the owner rules the
  jack count (D-07).

### C-20 EMCON removes power, so receivers stop too

- Need: appendix `:2787` asks EMCON to kill every TRANSMITTER.
- **Adjudicated (A11, VERIFIED):** the U19/U20 gates (`gen_sch_b.py:724-728`) drive the enables of eFuses and
  load switches that are the only supplies of the LimeSDR, the RockBLOCK, the E22 and both E72: power
  enables, so their receivers stop. The HF unit's DC input is switched off too (`gen_sch_a.py:536`). The 5G
  module goes to airplane mode (receive stops). Only the VHF path is gated on its transmit side alone.
  CONOPS section 4b is the table.
- Round 1's D-05 text also said the M.2 cards' hardware control under EMCON is "off"; that was wrong: EMCON
  never removes M.2 card power, it asserts W_DISABLE1# only.
- Effect: mission M4 (listen while silent) is impossible as generated for every radio but VHF.
- Resolution: owner decides what EMCON means operationally (D-05).

### C-21 Peak case against the declared pack peak (INFERRED arithmetic)

- Appendix `:2337` (owner, 4 Sep): no transmit serialisation; `:2846`: about 200 W peak without the outlets,
  already at the battery (A05); re-derived, PS-ALLTX is 227.0 W and PS-ALLTX-OUT 316.4 W (PROVISIONAL).
- `pcb_energy_chain.yaml:48-49`: declared continuous 10 A, peak 18 A; `TEST-PLAN.md:65-66` over-current trips
  at 20 A (2 s) and 30 A (20 ms).
- At end of discharge (2.5 V per cell, `TEST-PLAN.md:64`, a 10 V node) 200 W is about 20 A at the pack, and
  227 W about 23 A; at 3.0 V per cell (12 V) about 17 A and 19 A. Round 1's "before conversion losses" was
  misworded: the figures are already battery-side.
- Effect: the 18 A declaration and the 20 A trip sit inside the peak case's range; with the ~145 Wh pack
  that fits (A06) the headroom at low charge is smaller than W2's 4S4P case assumed.
- Resolution: owner rules how long "every transmitter at once" must last and at what charge (D-11); the
  session sets the thresholds and the outlet interlock (S-14).

### C-22 Holdover clock (INFERRED)

- Appendix `:2795` (32.50 item 11): "a TCXO-disciplined RTC fed by the LG290P pulse".
- `PANEL.md:127`: DS3231M on the kit I2C bus, CR2032 backed; `V2-SPEC.md:35` "a holdover RTC".
- The DS3231M is a temperature-compensated MEMS-resonator RTC with no discipline input (general knowledge of
  the part; no DS3231M datasheet was read for this entry). Whether "disciplined" is done in software by chrony
  is unstated. No holdover accuracy target exists (CAND-064).

### C-23 Two charge-inhibit paths

- `PANEL.md:155`: `SHORE_INHIBIT` high holds the shore and vehicle inputs off at the front end.
- Appendix `:2984` (32.57): "the charger is inhibited by pulling ILIM_HIZ low (CHG_INHIBIT on the 0x21
  expander) instead of the old SHORE_INHIBIT contact", while `J_DOCK` pin 8 keeps `SHORE_INHIBIT` as E6's
  hot-swap enable.
- Also (A01): at power-up `CHG_INHIBIT` sits at about 1.66 V inside the 2N7002's threshold spread until the
  panel firmware writes the expander; any error is toward the charger in HiZ.
- Effect: PANEL.md describes one path; the design has two with different effects (inputs off against charger
  off). Resolution: session doc fix, W5's hardware and firmware contract.

### C-24 Public README device lines after 9d66316f

- The layer columns of `README.md` and `v2/README.md` were corrected on main by 9d66316f; round 1's layer
  half is moot.
- The Rev columns (A24, B19, C24, D11, E9, E5, P4) name the promoted deliverable folders, and the working
  phases (A32, B21, C24, D12, E5, E17, P4 in `v2/ecad/tools/boards/*.json`) are unpromoted while promotion is
  frozen. That is accurate as it stands; round 1's "stale phases" is withdrawn.
- What remains for the integrator (VERIFIED at 82dd1e4d): `README.md:20` "a built 4S smart pack of about
  200 Wh" (at most about 145 Wh fits, C-15); `README.md:20` and `v2/README.md:5` say losing a module "moves
  its peripherals instead of removing them", which ARCH-PCB-B-IOHA section 15 qualifies (two bearers do not
  move); `v2/README.md:5` "EMCON a hardware line from the panel toggle to every transmitter rail gate" (the
  compute modules' radios are not on it, C-03).
- Resolution: integrator, baseline hygiene; the same wording as the product brief's compute and EMCON bullets.

### C-25 From the plan's list, not re-verified by W1

Stale `LAYER-DECISIONS-2026-09-11.md`; committed `.kicad_sch` files for A, C and D older than their
generators; `retake_gate.sh` and the B22/B23 box drivers absent from the repo. These belong to W7 and the
integrator.

### C-26 DCF77 pulse: "fanned out to every slot" against one sensor controller input

- `V2-SPEC.md:35`: "LG290P and DCF77 pulses fanned out to every slot".
- `gen_sch_e.py:349`, `:353`, `:381`, `:395`: `DCF_PULSE` runs from `J_DCF` pin 3 to the sensor controller
  RP2040 (GPIO6) with a 10 k pull-up, and nowhere else. Round 1's CAND-064 adopted the generator silently.
- Effect: the modules' chrony can take DCF77 time only through the sensor controller's USB link, not as a
  hardware pulse; whether that meets the holdover need depends on a target that does not exist (CAND-064).
- Resolution: session (S-17): route the pulse, or correct V2-SPEC to say the sensor controller serves it.

### C-27 What the charger does without a host, and what it reads

- **Documents:** `PANEL.md:155` "a kit with a crashed panel still charges" and "the pack thermistor (read by
  the BQ25731 over the bus)"; `PANEL.md:128` "the 4S pack's gauge ... answers on the charger's SMBus";
  appendix `:3062` "the charger BQ25731 of A22 already speaks SMBus to it"; `OPERATING-ENVELOPE.md:89` "the
  pack thermistor on the charger's JEITA input already does in hardware"; round 1's CONOPS Charging row.
- **Adjudicated (A02 and A07):**
  - the BQ25731 has no thermistor, TS or JEITA input (SLUSE66A pin table pp5-7) and is an I2C target at 6Bh;
    it reads nothing over any bus, and it has no conductor to board P (A07). Charge temperature is the pack
    gauge's alone (`pcb_pack_protection.yaml` CHARGE_TEMPERATURE_WINDOW, 0 to +45 C at the cells);
  - without host writes its charge current is 256 mA at power-on and after its 175 s watchdog (TI E2E
    1316778, 23 Jan 2024, correcting the datasheet's inherited "0 A"; INFERRED, bench owed);
  - the kit's loads sit on VBAT, the pack side of the charger's sense resistor R17, so shore carries the loads
    only up to the programmed charge current (VERIFIED on the A23 netlist); 256 mA is below every power
    state's load, so a hostless kit on shore still discharges;
  - as generated the cell-count strap (R26 60.4 k over R27 40.2 k, 39.96 %) selects 2S: ChargeVoltage 8.4 V,
    and a 4S pack is never charged (VERIFIED; the fix is a 75 % pair such as 13.3 k over 40.2 k);
  - only board E's sensor controller can read the gauge (A07).
- **Effect:** four documents claim hardware behaviour the design does not have; the charge path is not
  usable as generated.
- **Resolution:** session: the strap (S-03), the charger topology or host-computed charge current (S-04, A02
  leaves it to W2/W5), and the document corrections. `OPERATING-ENVELOPE.md:89` is pinned by
  `pcb_envelope.yaml` `document_sha256` and ENV-001; its correction must be re-pinned in the same change.
  Proposed replacement text for `:88-89`: "which the pack gauge's charge-temperature window (0 to +45 C at the
  cells, decision 40) does in the pack's own firmware; the charger BQ25731 has no thermistor input."

### C-28 The design record's EMCON gate list against the generated gates

- **Record:** appendix `:2787` (32.50 item 3): "EMCON kills every transmitter in hardware (5G, WiFi cards,
  LoRa, Iridium, the APRS PA bias)"; `:2930` (32.56): the gate list includes "the 5G module's supply switch
  and W_DISABLE; the WiFi card's 3.3 V buck enable on B16 and its W_DISABLE"; `PANEL.md:111` says "both M.2
  cards' W_DISABLE1#" and lists 5G and the WiFi link among the rail gates.
- **Generated (A11, VERIFIED):** three M.2 radio cards carry W_DISABLE1# (WiFi slot 1, 5G slot 2, WiFi slot
  3); no card rail is gated (the rails follow `PCIE_PWR_EN` only; 5G `FULL_CARD_POWER_OFF#` is driven only by
  U6); the WiFi cards' response to W_DISABLE1# is undocumented and the mainline mt7915 driver has no rfkill
  code; the CM5 radios are not gated (C-03).
- **Effect:** RF-002 cannot count the two WiFi link cards as inhibited without a bench test; the record
  describes supply gates that do not exist.
- **Resolution:** session: gate the WiFi card supplies (or prove W_DISABLE1# on the bench), decide whether the
  5G supply switch of 32.56 is built, and generate one EMCON table from the netlists (S-01, S-02). Recorded as
  a design-record-versus-generator mismatch, not as a fact about the boards.

### C-29 Pack SMBus lead (A07, VERIFIED)

- Board P `J_SMB`: JST-XH B4B-XH-A, 1x4, 2.50 mm (LCSC C594232): 1 SMBC, 2 SMBD, 3 GND (cell side, upstream
  of the 2 mOhm shunt), 4 PRES.
- Board E `J_SMB`: a 2.54 mm pin header 1x6 (the "PH6" key means pin header): 1 SDA0, 2 SCL0, 3 SDA1, 4
  SCL1, 5 GND, 6 GND; no PRES; kept from the withdrawn BB-2590/U's two SMBus sections.
- `ASSEMBLY.md:60`: "XH2.5 x 6", section A on the kit bus, section B spare: matches neither board.
- A straight lead would swap clock and data, ground the sensor bus data line and carry no ground.
- Resolution: session (S-05): E's `J_SMB` becomes an XH4 matching P, P's pin 3 moves to the pack side of the
  shunt, ASSEMBLY.md and PANEL.md are corrected, and a `J_SMB` contract is added to `check_contracts.py`.

### C-30 ASSEMBLY.md's pack section and RockBLOCK standoffs (A06, VERIFIED)

- `ASSEMBLY.md:21`: the RockBLOCK bracket on "four M2.5 standoffs"; board B21 carries H17 to H20 "M4, GC 9704
  bracket" holes of 4.3 mm.
- `ASSEMBLY.md` section 3 (from line 51) promises "4S4P ... or twelve 21700 cells (4S3P)" in `pack_4s.py`'s
  enclosure in a "Z 1 to 49" pocket; neither fits under B21 with board P, and Z 1 to 49 dates from B's
  underside at 54.4 (32.62), now 47.9.
- Resolution: session doc fix after D-06.

### C-31 SOS has a switch, a lamp and a sounder pattern, and no defined action

- `PANEL.md:14`, `:61` (SOS_SW), `:72` (SOS ACTIVE lamp), `:145` (MASTER WARN for SOS active), `:147` ("SOS
  closed 2 s = SOS mode (flipping back cancels; the e-paper confirms both)"), `:151` (sounder "1 s on 1 s off
  (SOS armed)"); `V2-SPEC.md:58` (covered locking toggle).
- Nowhere: what SOS sends, over which bearer, to whom, and whether it may transmit while EMCON is closed.
  The challenger found no mode, mission or requirement for it.
- Resolution: owner (D-10): what it sends and whether it may override EMCON are product and risk choices.
  The session then writes the firmware contract and, if SOS may override EMCON, the hardware path it needs
  (as generated nothing can transmit through the EMCON gates, so an override would be a design change).

### C-32 Device-rail and slot power-up (A01, INFERRED)

- `PANEL.md:102` "Boot: all three `SLOT_EN` high" (the panel raises them) and the power-controller design of
  board A.
- A01: `DEV_EN` (the device rail's enable, R42 100 k to ground) is raised at power-up only by the fitted TI
  PCA9555's internal pull-up (about 100 k; its minimum current is unspecified), reaching about 1.71 V against
  the converter's 1.25 V turn-on maximum; it fails only above about 181 k, so the kit boots nominally but not
  by design. POE_EN and PD_EN are OFF (guaranteed); PA_SW_EN, HF_SW_EN and CHG_INHIBIT sit in undefined
  bands until the panel firmware writes the expanders; `SLOT_EN1..3` are OFF until the panel drives them.
  A PCA9535 swap without re-terminating R42 would deadlock the kit.
- Also (W2 F-SQ-02, not settled by A01): RAIL_EN and KILL are pulled to VBAT (up to 16.8 V) against the
  TPS62933's 6 V and the LTC2954's absolute maximums, and the LTC2954 fitted is the 0 to 70 C grade.
- Also (A01): the monitor and heater eFuses U21/U22 lock out above about 13 V of VBAT (OVLO dividers 100 k
  over 10 k), so the monitor is dark over most of the 14.4 to 16.8 V pack range.
- Resolution: session (S-08): R42 re-terminated to board A's 3.3 V; defined pull-downs (4.7 k) on the other
  expander enables; the firmware writes output registers before configuration registers; the OVLO dividers
  resized; the SLOT_EN default decided with them (W3's proposal). None is an owner question (A01).

## Resolved by supersession (recorded so nobody re-opens them)

| Old statement | Source | Replaced by |
|---|---|---|
| USB-C PD 65 W | appendix `:2786` | 45 W, TPS25740A (`:2980`), back to 65 W when the B variant is buyable |
| Physical owner of a device is a HAL cabling choice | `:2837`, `:2844` | the voted hardware fabric (`ARCH-PCB-B-IOHA.md` sections 4 and 15; `V2-SPEC.md:32`) |
| Outside sensors behind a membrane vent | `:2802` sensor 8, `:2850` | sealed pod on an M8 receptacle (`:2867`) |
| BB-2590/U pack | `:2771` | built 4S pack (`:3062`) |
| Two cascaded ASM1184e switches | `:2769-2770` | one PI7C9X2G404SL per slot (`V2-SPEC.md:31`) |
| Electrical fast transient 2 kV | `OPERATING-ENVELOPE.md:165` | not a requirement (decision 34) |
| "Whether 32.52's 50 W is at the battery or at the loads is not established" (round 1, CAND-032) | CONOPS round 1 | battery-side: 45.0 W and 178 W of loads plus 12 % (A05) |
