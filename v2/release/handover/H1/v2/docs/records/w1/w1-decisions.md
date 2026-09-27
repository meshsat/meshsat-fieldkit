# Foundation decision table, one ranked list (draft for the integrator, MESHSAT-1357)

Written 25 September 2026 by workstream W1, round 2. It replaces round 1's D-01 to D-09 table and merges the
owner candidates of W2 to W7 into one list. Every question rests on facts the eleven adjudications settled
(A01 to A11, folders under the session scratchpad `adj/`) or on a challenged and upheld finding; where a
premise is still INFERRED or TBD, the row says so. Base: main `82dd1e4d`.

**The test applied to every row (owner ruling of 21 September 2026).** A question goes to the owner only when
BOTH halves hold: (1) it changes a line a class in `reserved.json` protects, OR spends money, OR changes what the
kit is claimed to be, OR accepts a residual risk no measurement in this tree can remove; AND (2) more than one
option is still standing after the measurement. Promotion, publication, money and advertising the kit to its
envelope are never the session's. Everything else is the session's, recorded with `authority: SESSION` in
`tools/pcb_decisions.yaml`.

**Classes.** OWNER: asked, one per turn, with evidence, options and a recommendation, in rank order.
SESSION: an engineering choice; it arrives as a recommendation with evidence and is not asked. CONDITIONAL:
the session acts first and the owner is asked only if a named result comes back. NOTICE: told, not asked.
LATER: an owner money item that is asked when its quote exists, not now.

IDs: D-01 to D-09 keep their round-1 meaning where the question survives; D-10 onward are new owner rows;
S-nn are session items; N-nn notices; L-nn later items. `C-nn` are entries of `drafts/w1-conflicts.md`,
`CAND-nnn` records of `drafts/w1-requirements.yaml`, `NEED-nn` and `PS-...` the needs and power states of
`v2/docs/CONOPS.md`.

## 1. The ranked table

| Rank | ID | Class | Question or item | From | Why this class (the two halves) | Recommendation in one line | Rests on | Gates |
|---|---|---|---|---|---|---|---|---|
| 1 | D-01 | OWNER | Prototype scope: which functions the first build is accepted against, and which are built but reported NOT_YET_TESTED | W1 | scope of the claim; three options | full design, staged acceptance on a named core set (option 2) | device set 32.49 to 32.52; board B unrouted (plan section 1); every board but E5 owes a schematic change (A01, A02, A03, A07, A08) | Review A; which requirements gate prototype release |
| 2 | D-02a | OWNER | Are TEST-PLAN's +55 C and +71 C (E3), -33 C (E4) and 30 to 60 C (E5) qualification margins over the -20 to +40 C envelope? | W1, W5 | what the kit is claimed to survive; three options | margins, with survival and recovery criteria; acceptance runs at the envelope edge | C-06; W5: at +55 C the envelope's own arithmetic puts inside air at +65 to +71 C, over the cells' +60 C | TEST-PLAN rewrite (W5) |
| 3 | D-02b | OWNER | Must the kit operate with the lid closed, and with which bearers? | W1 | claim; three options | yes, in the reduced mode, with GNSS, LoRa mesh, Iridium and APRS beacons; monitor off | C-16; 32.53 lid-closed shedding; PS-RED 19.7 W and PS-RED-b 25.4 W (A05, PROVISIONAL) | reduced-mode definition (session); lid sense (S-11); a closed-lid test state |
| 4 | D-02c | OWNER | Will the kit be carried in an unpressurised aircraft hold? | W1 | a fact of intended use only the owner has; two answers | answer the fact; the session then sets 3000 m in use and 4500 m in transport, or higher | C-08 | altitude values; E9 |
| 5 | D-02d | OWNER | Cold start from the pack with the cells below their -10 C discharge limit: in scope or out? | W2 | changes the -20 C in-use claim; two options | out of scope for the prototype; the carve-out says a cold-soaked kit needs shore power or warming first | W2 F-PK-01 (cell sheet 3.12, 7.5); C-14 (withdrawn as a conflict) | envelope carve-out; pack board P and E hardware if in scope |
| 6 | D-02e | OWNER | Is "operated shaded" a stated operating condition, or must the kit work in full sun? | W4 | residual risk (an unshaded plate can exceed the monitor's 70 C and touch limits) and claim; three options | state it as a condition with a shade accessory now; full-sun design as a later qualification item | 32.53 ("the kit runs shaded"); W4 estimate 87 to 92 W absorbed on the plate lid open (PROVISIONAL, unmeasured) | envelope wording; accessory list |
| 7 | D-05 | OWNER | Under EMCON, keep receivers listening where a proven transmit-only gate exists, or put every radio dark? | W1, A11 | claim (what EMCON does); three options | dark, as generated and completed by the session (option 1); LoRa listening only after a bench proof (option 2 as an upgrade) | A11 table (CONOPS section 4b): only VHF is transmit-only today; PS-EMCON 47.6 W, PS-EMCON-L 52.5 W (A05) | board B EMCON gates; RF-002; M4 |
| 8 | D-03 | OWNER | ZEROIZE: what it erases, what triggers it, and what a power loss during the hold does | W1, W5 | residual risk (keys left on a powered-off module, or drives that cannot unlock without the panel); options standing | crypto-erase (Z-B), toggle held 5 s the only trigger, tamper logs only, level-sensitive resume | C-09; decision 30; W5 section 5; IOHA section 10 common modes | decision 30 mechanism (session); SCH-004 on six boards; SE provisioning |
| 9 | D-10 | OWNER | SOS: what it sends, over which bearers, to whom, and may it transmit while EMCON is closed? | W1 (challenger) | claim and risk; three options | a distress message with position over the available bearers to a configured recipient; never through EMCON (queued, operator told) | C-31; PANEL.md:14, :61, :145, :147, :151 | NEED-19; panel firmware; any EMCON bypass hardware |
| 10 | D-04 | OWNER | Markets and obligations: where the prototype operates, who operates it, is it ever sold; and is any EMC claim wanted, for which installation | W1, W5 | claim and money; three options | non-commercial prototype in the NL and EU, licensed amateur operator, no conformity marking, EU route kept open, no EMC claim yet | no RED, UN 38.3, IEC 62368 or FCC in the documents; 16a is HF only; VHF licence basis unrecorded | NEED-16, NEED-18; S-18 (edition), D-16 (surge) |
| 11 | D-08 | OWNER | Measure the owner's Peli 1450 and build a mock-up (frame bought later) | W1, W4 | owner's time and money; three options | measure and mock up now, buy the 1450PF frame later | A06: the 4S3P fit has 1.35 mm across the pocket, under the wall uncertainty; A09: D8 height and J_AB2 collision (INFERRED) | D-06; MEC-001; the face Z budget |
| 12 | D-06 | OWNER | Pack size and runtime target (asked after D-08) | W1, W2, A05, A06 | claim (runtime) and design change; three options | about 145 Wh (4S3P 18650) with a runtime requirement on PS-IDLE-SPEC and PS-TYP aged, plus a pack-and-solar energy balance over a mission duration the owner sets | A06 (4S4P fits neither pocket with board P beside it); A05 table; 32.62's own research gate asked for 100 to 150 Wh | NEED-05; board P; enclosure; V2-SPEC line 23 |
| 13 | D-11 | OWNER | Peak simultaneity: may every transmitter key together without a time limit, at any charge? | W2 | changes an owner ruling (4 Sep, no serialisation) and the claim; three options | all at once for a declared key-down time above a declared charge floor, outlets at minimum; the hardware interlock is the session's | C-21; PS-ALLTX 227 W (A05); 18 A declared, 20 A (2 s) gauge trip; smaller pack (A06) | pack thresholds; S-14 |
| 14 | D-07 | OWNER | 5G antenna jacks: two, three or four | W1, W4, A08 | money and case penetrations; three options | three jacks (ANT0, ANT2, ANT3), if the extra board A site and board E clamp fit at D-08; otherwise two (ANT0, ANT2) | A08: Table 32 band consequences; the socket is being replaced (S-12); 11 wall SMA today | case bulkheads; boards A and E sites |
| 15 | D-12 | OWNER | Which external USB data port the kit has | W3 | changes an approved feature (32.50: USB-C PD outlet and console); three options | data path to the Glenair 233-370 feed-through, USB-C as a power outlet; the console is designed by the session on the port kept | W3: the 233-370 has no data path; all twelve hub ports allocated; both external ports are host ports | board B, the A pigtail, the connector plate; S-21 |
| 16 | D-13 | OWNER | Firmware integrity: verified boot for the prototype, and does it need a hardware-isolated root of trust (the H753 against H743 mismatch)? | W6, red team S2 | residual risk; the owner set the H753 baseline himself; three options | software-verified boot on the H743 as the prototype's floor, hardware root of trust at a production trigger; the mismatch stays open until this is ruled and D-03 is settled | W6-F1 (pin parity 100 of 100, PROVISIONAL); red team S2 (RED-TEAM-2026-09-09.md:363); H753 0 stock at JLC | board B supervisor BOM line; firmware |
| 17 | D-14 | OWNER | Lifting the stack with the pack connected: accept the operator-dependent residual of procedure plus a cap, or require a hardware interlock? | W3 | residual risk; options standing | accept procedure plus cap for the prototype; study the interlock at Review D | ASSEMBLY.md:117, :131; J_DOCK pin 12 spare | boards A, E and P only if the interlock is chosen |
| 18 | D-15 | OWNER | Cell under-voltage protection resting on the gauge's firmware alone (decision 40 residual) | W2 | residual risk; three options | a secondary protector that also covers under-voltage if one is sourced near the OV-only part's cost, else accept with a data-flash check at commissioning | W2 decision 40 review (S-8261 and BQ2970 are single-cell; no 4S secondary protector held) | board P; decision 40 |
| 19 | D-16 | OWNER | Which vehicle surge standard the kit claims (the vehicle input itself is ruled, 16b) | W2 | claim; three options | no surge claim for the prototype ("9 to 36 V, not qualified"); MIL-STD-1275 only if military vehicles become a target market (with D-04) | W2 F-IN-03 (INFERRED: the entry would not survive the standard's pulses); appendix :1459; no standard held | board E entry parts |
| 20 | D-09 | OWNER | Independent review and test route | W1 | money; three options | SIDN fonds voucher on ZEROIZE and key fill, a paid battery and protection review before the pack is built, an EMC pre-compliance session after the prototype exists | decision 40 open; no EMC evidence; agent agreement is review, not evidence (plan section 3) | NEED-10, NEED-13, NEED-15 |
| 21 | D-17 | OWNER | Board A's USB-C CC pins protected only inside the TPS25740 (decision 31 item one): confirm the residual risk | W7 | residual risk no measurement in the tree removes; two options | confirm (accept), carried to the ESD gun at prototype test; the external array would ride on the A phase already owed | A04 (U18 present part for part); TI SLVSDG8B 7.2 footnote (application test board) | TEST-PLAN M7; board A's next phase |
| 22 | D-18 | CONDITIONAL | IP68 fans (32.53 item 2) | W4 | owner only if no 40 mm IP68 part fits (changes his ruling); otherwise one option stands | session retrieves Delta's 40 mm IP68 part first; the owner is asked only if none fits the cooler rectangles | open-picks.txt:17 lists Delta 40 mm IP68 (W4 challenger) | face Z budget; thermal bound |
| 23 | L-01 | LATER | Board B eight-layer fabrication price and any per-stackup fixed fee | A10, plan 6.6 | money; asked from a quote before any order | none now | A10: JLC's order form offers 13 eight-layer impedance stackups, four with a fixed fee | decision 43; any order |
| n/a | N-01 | NOTICE | Decision 28's cited evidence (P8) was taken on the wrong BQ4050 land (5 x 5 mm, 0.5 mm pitch, where the part is 4 x 4 mm, 0.4 mm) | W6, W6 challenger | not a question: the evidence is void until P is retaken on the right land | tell the owner; the retake follows the land fix | W6-F2 (SLUSC67B pp. 1, 47, 50, 52) | decision 28's evidence |
| n/a | N-02 | NOTICE | The plan's "panel unplugged: only APRS is inhibited" was wrong: with the panel unplugged the kit transmits nothing and no compute slot powers | W1, critic | a correction of a statement already made to him | tell the owner with the checkpoint | C-04; A01; A11 | plan section 1 |

Session items that were proposed as owner questions in round 1 and are not asked: the tamper switch (approved
and sited, S-11), the SLOT_EN default (restores documented behaviour, S-08), "50 W at the battery or at the loads"
(answered, battery-side, A05), the ZEROIZE success indications (S-19), the vibration and shock severity mapping
(S-15), the MIL-STD-461 edition once D-04 says whether a claim is wanted (S-18), the 5G port pairing (S-12), and
the 4S4P charge-current setting (S-20). W5 still lists the MIL-STD-461 edition as an owner question; W1 splits it:
the installation and whether any claim is wanted are the owner's (D-04), the edition that fits that installation
is the session's.

## 2. The owner questions in detail

### D-01 Prototype scope (rank 1)

**Evidence.**
- The ruled device set is large: 32.49 (`:2756-2771`), 32.50 (fourteen items plus 16a to 16g, `:2785-2804`), the
  three-slot fabric of 32.52 and the I/O high-availability layer (`ARCH-PCB-B-IOHA.md` section 14: +169 parts on
  board B).
- Board B has never routed (plan section 1: B21 with 416 unrouted; not re-derived by W1). Decision 43 authorises an
  eight-layer measurement first.
- Every board except E5 owes a schematic change found this round, all of them session fixes that do not change the
  scope: reversed clamps on C, D, E and P and the wrong clamp symbol on A, B, D, E and P (A03); the charger strap
  and the power-up enables on A (A01, A02); the 5G socket and SIM 2 on B (A08); the SMBus lead on E and P (A07).
- Parts cost is estimated at about 5,700 EUR per kit from remembered list prices, before the fabric and the second
  WiFi card (`V2-SPEC.md:88-116`); there is no cost target.
- Functions with no implementation yet: the tamper switch (S-11), the battery-bay SGP41 (S-10), the SOS action
  (D-10), the tablet bracket (`V2-SPEC.md:12`), the SOS and ZEROIZE covers (`V2-SPEC.md:58`).
- The plan forbids any feature reduction without an owner ruling (plan section 10).

**Options.**
1. Everything ruled, all accepted at the first build. Cost: the first prototype waits on the slowest function.
2. **Full design, staged acceptance (RECOMMENDED).** Every ruled function is designed and fitted where copper exists;
   prototype 1 is accepted against a named core and the rest stays visible as NOT_YET_TESTED. Suggested core, for
   the owner to edit: NEED-01 and NEED-02 over Iridium, 5G, LoRa and APRS; NEED-03 (the failover fabric, IOHA
   acceptance tests A1 to A14); NEED-05 (pack, vehicle and solar charging); NEED-08 (EMCON as D-05 rules it);
   NEED-10 (ZEROIZE as D-03 rules it); NEED-13 (pack safety); NEED-14 (service and programming access); NEED-19
   (SOS as D-10 rules it). Deferred acceptance: the Geiger counter, lightning detector, DCF77, outside pod, camera,
   net audio recording, tablet bracket, NVG compatibility and HF. (Round 1 also deferred "the second pack"; A06
   found that nothing fits the west pocket, so it is no longer an option to defer.)
3. Reduced first build (a design change): remove functions from the boards, for example the I/O fabric or two
   slots. Reverses rulings of 7 and 9 September; not justified until W3's diagnosis shows the removed function
   is what blocks board B.

**Consequences.** Requirements get a `prototype_1: core | deferred` attribute; TEST-PLAN's functional check splits
into core and deferred lines; readiness shows deferred lines as NOT_YET_TESTED, never as a pass.

### D-02 Envelope (ranks 2 to 6, asked as five questions, one at a time)

**D-02a Qualification margins.** Evidence: C-06; TEST-PLAN E3 (+71 C storage, +55 C operation), E4 (-33 C
storage), E5 (30 to 60 C cycles) against the envelope's -20 to +40 C in use and -20 to +45 C storage; W5 found
the probable source of +71 and -33 C is MIL-STD-810's climatic categories (TBD: the standard is not held) and that
at +55 C the envelope's own arithmetic puts the inside air at +65 to +71 C, above the cells' +60 C discharge limit,
so as an acceptance test E3 fails by design. Options: (1) declared margins, criterion "survive and recover fully
inside the envelope", with an acceptance run at the envelope edge (RECOMMENDED, W5 agrees); (2) acceptance at those
levels, which claims a wider envelope the part table does not support; (3) move the levels to the envelope edge
and lose the margin evidence. Plan condition 3 binds: no level is lowered without a stated purpose.

**D-02b Closed-lid operation.** Evidence: C-16; 32.53 (`:2860`): lid closed the walls shed about 1.5 to 2 W/K,
"one module is fine, three loaded modules at 40 C are not"; the antennas are on the end walls and work lid-closed;
mission M2. The two reduced definitions are PS-RED 19.7 W (one module) and PS-RED-b 25.4 W (cluster idle),
PROVISIONAL (A05). Options: (1) no closed-lid operation, closed means transport; (2) closed-lid operation in the
reduced mode with a named bearer set, for example GNSS, LoRa mesh, Iridium and APRS beacons, monitor off
(RECOMMENDED; it serves M2); (3) full operation lid-closed: not supported by the thermal estimate. Consequences of
(2): a closed-lid state and thermal test in TEST-PLAN; the session picks the reduced definition that meets the bearer
set thermally and wires the lid sense (S-11). Two consequences to accept or design out, stated with this question:
above +35 C ambient the envelope runs one module, so there is no compute redundancy in the heat (CAND-092); with
three loaded modules and the lid open, charging holds off above about +25 C ambient (CAND-093).

**D-02c Air carriage.** One fact: will the kit ever be carried in an unpressurised aircraft hold? If not, the
session adopts the envelope's proposed 0 to 3000 m in use and 0 to 4500 m in transport (C-08); if yes, the
transport altitude and E9 are re-set.

**D-02d Cold start from the pack (W2).** Evidence: the cells' discharge window ends at -10 C at the cell surface
(Samsung INR18650-35E sheet 3.12, 7.5: about 40 % capacity at -10 C; `pcb_pack_protection.yaml`
DISCHARGE_TEMPERATURE_WINDOW); the envelope's in-use floor is -20 C ambient; a kit cold-soaked below the cells'
limit cannot start from its pack, and its heater mat needs power the gauge will not release. Options: (1) in scope:
a pre-warm path the gauge allows (a heater fed from shore, a small separate cell) or a wider discharge window with
the cell maker's backing, each adding hardware to P or E; (2) out of scope: the envelope's carve-out says a
cold-soaked kit needs shore power or warming before start (RECOMMENDED for the prototype, W2 agrees).

**D-02e Direct sun (W4).** Evidence: 32.53 "the kit runs shaded" (a black plate absorbs about 60 W); W4 estimates
87 to 92 W absorbed on the plate with the lid open (PROVISIONAL, a scratch model, not measured); an unshaded plate
can exceed the Xenarc's 70 C and touch-temperature limits. Options: (1) a stated operating condition with a shade
accessory (RECOMMENDED now); (2) design for full sun (lighter finish, lid sun shield, reduced mode in sun) as a later
qualification item; (3) leave it unstated (a residual risk nobody accepted).

### D-05 EMCON meaning (rank 7)

**Evidence (A11, VERIFIED on the regenerated netlists of A, B and D).** CONOPS section 4b is the table. As
generated: power is removed from the LimeSDR, the RockBLOCK, the E22 LoRa module, both E72 radios and the QMX's
DC input; the 5G module goes to airplane mode (its receiver stops too, Quectel HD 4.4.1); the two AW7915 WiFi
link cards get W_DISABLE1# with an unproven effect (the maker's sheet is silent; mainline mt7915 has no rfkill);
the VHF path is gated on its transmit side only and keeps receiving (the resting relay joins antenna to exciter);
the three CM5 modules' own WiFi and Bluetooth are not gated. EMCON never removes M.2 card power (round 1 said it
did). PS-EMCON is 47.6 W as generated; a "keep listening" state would be about 52.5 W (A05, PROVISIONAL). The
owner's own ruling, 32.50 item 3 (`:2787`): "EMCON kills every transmitter in hardware".

**Options.**
1. **Radios dark, as generated and completed (RECOMMENDED for the prototype).** Every radio with any emission path
   is powered off or RF-disabled by the hardware line; VHF keeps listening because its gate is proven
   transmit-only. The session closes the two gaps under every option: the CM5 radios go on the line (S-01) and the
   WiFi cards' supplies are gated or their W_DISABLE1# proven on the bench (S-01). Receive is lost on the SDR,
   Iridium, LoRa, Zigbee, Thread, HF, 5G and WiFi; GNSS, DCF77 and the lightning sensor continue.
2. **Listen where a transmit-only gate can be proven.** Option 1, plus the LoRa module stays powered with its
   transmit enable (TXEN, today driven only by slot 3) gated by EMCON: a board B change, and whether TXEN low alone
   guarantees no emission is TBD (the held manual does not show the module's internal PA and switch; a bench
   measurement is needed). No other radio in the set has a hardware transmit-only control wired or documented:
   the USB SDR exposes none, the 5G module's W_DISABLE stops receive too, and none is wired for the RockBLOCK, the
   QMX or the E72 (whether their makers offer one is TBD; the held sheets show none that A11 found).
   Recommended only as an upgrade once the LoRa measurement passes.
3. **Listen everywhere, with transmit inhibited by software where no hardware gate exists.** Keeps the SDR,
   RockBLOCK, QMX, E72 and LoRa powered. It reverses 32.50 item 3 for those radios and makes their silence depend on
   software, which NEED-08 exists to avoid; it is a residual-risk acceptance for a 10 MHz to 3.5 GHz transmit-capable
   SDR among others.

**Consequences.** Option 1: no change beyond S-01 and S-02; M4's "listen while silent" is VHF only. Option 2: a
TXEN gate on board B and a bench test before it counts. Option 3: design changes on A and B and a written risk
acceptance. Round 1's recommended option contradicted itself (it kept the SDR powered with software-only transmit
inhibit while saying "radios off elsewhere"); that option no longer exists in this list.

### D-03 ZEROIZE (rank 8)

**Evidence.** C-09; decision 30 (`pcb_decisions.yaml:207-233`): the line reaches only the panel RP2040; on A, B and
D it runs to connectors, test points and a pull-up; the drives belong to the modules, which do not see the line;
V2-SPEC's "disk-key wipe line" exists nowhere; 32.50 item 5 asks "keys wiped in milliseconds" (`:2789`); W5 section 5
gives the options Z-A, Z-B, Z-C.

**Three sub-questions, one at a time.**
1. **What is erased.** (a) Z-A: the secure element's keys, plus a wipe message to running modules; a powered-off
   module keeps its drive keys (a named gap). (b) Z-B, crypto-erase (RECOMMENDED): every drive key is wrapped by a
   key only the secure element holds, so one erase makes every drive unreadable, a powered-off module's included; no
   board change. (c) Z-C: Z-B plus a hardware ZEROIZE line into the I/O supervisors and the modules (board B
   copper, more accidental-wipe paths; it would also give the supervisors a security role, which re-opens D-13).
   The consequence of Z-B that the owner accepts with it: every drive's unlock at boot depends on the secure
   element, the panel controller and the kit I2C bus, which ARCH-PCB-B-IOHA section 10 names as whole-kit common
   modes; a module that reboots while the panel or the bus is down cannot unlock its drive until they return, so
   NEED-03 is weaker for stored data than for compute. A running module keeps its unlocked drive.
2. **What triggers it.** The covered toggle held 5 s (PANEL.md:147; RECOMMENDED as the only trigger for the
   prototype); the tamper switch (RECOMMENDED as log only: a routine service opening must not wipe the kit); a remote
   command (defer: it is an authenticated remote-wipe path); pack loss or under-voltage (not recommended: a flat
   battery would wipe the kit).
3. **Power loss during the hold (W5).** Level-sensitive: a toggle still closed at the next boot completes the wipe
   (RECOMMENDED; it fails toward erasing); or edge-only: a wipe interrupted by power loss is abandoned (fails toward
   keeping keys).

**Session precondition, not the owner's:** whether the ATECC608B can erase or overwrite a wrapping key after its
zones are locked depends on its slot configuration, and the full datasheet is under NDA (only the summary
DS40002239A is held), so it is TBD; if it cannot, 32.50 item 5 already names a TPM 2.0 as the alternative. How
success is shown (a failed key operation, drives that do not unlock, ZEROIZE COMPLETE on the e-paper, the 3 s
sounder, a non-secret event in the panel controller's flash) is the session's (S-19).

### D-10 SOS (rank 9)

**Evidence.** C-31: the face carries a covered SOS locking toggle with a lamp, a MASTER WARN condition and a
sounder pattern, and "SOS closed 2 s = SOS mode (flipping back cancels; the e-paper confirms both)" (PANEL.md:147);
nothing says what SOS sends, to whom, or how it meets EMCON. As generated no board can pass a transmission through
the EMCON gates.

**Options.** (1) **A distress message with position over the available bearers (Iridium first when nothing free
is up) to a configured recipient; SOS never transmits through EMCON: under EMCON it is queued and the operator is
told (RECOMMENDED for the prototype; firmware only).** (2) As (1), and SOS may transmit through EMCON on one named
bearer: needs a hardware path through that radio's EMCON gate (a board B change) and accepts that a distress call
breaks emission control. (3) Local alarm only: MASTER WARN, sounder and log, no transmission.

**Consequences.** (1): NEED-19 acceptance is a functional check line; the recipient list and message format are the
session's. (2): a board change and a written exception to NEED-08.

### D-04 Markets and obligations (rank 10)

**Evidence.** None of the Radio Equipment Directive, UN 38.3, IEC 62368-1 or the FCC rules appears in the design
documents (grep of 25 Sep 2026); IEC 62133 appears once, about a bought pack not taken (`:3058`). Appendix 32.50 item
16a (`:2802`) puts HF on amateur bands "under the owner's licence"; the licence basis for the VHF APRS and voice
path is not recorded. Transmitters that need a scope: SA868 134 to 174 MHz with the 30 W PA covering 135 to 175
MHz (`nicerf-sa868-datasheet-v1.3.pdf`; `:2813`), LoRa capped to EU limits in software only (`:2761`), a
transmit-capable SDR (`V2-SPEC.md:49`), the 5G module, the WiFi cards, and the CM5 radios whose certification path
through a blind-mate is INFERRED (C-17). The built 4S pack has to travel (INFERRED: lithium-ion transport generally
needs a UN 38.3 test summary; no document in the tree states it). "Certification and support, not price, decide a
sale" (`:2804`).

**Options.** (1) **Non-commercial prototype in the Netherlands and the EU, operated by a licensed amateur operator,
no conformity marking claimed, the EU route kept open in the design, no EMC claim yet (RECOMMENDED).** (2) Plan for
EU market placement now: radio, EMC and safety conformity under the Radio Equipment Directive and its harmonised
standards (none held), a UN 38.3 test of the built pack, a technical file. (3) Several markets.

**Sub-question with it (merges W5's MIL-STD-461 candidate):** is an EMC claim wanted for the prototype, and for which
installation (for example a ground vehicle or a fixed ground site)? The installation decides the MIL-STD-461 limit
curves; the edition is then the session's (S-18). Under option 1 every M1 to M5 run is characterisation (ENV-002).

**Consequences of 1.** NEED-16 acceptance: every transmitter configured to the operator's licence and the EU limits,
with a band lock on the VHF path (CAND-082); EFT stays not required (CAND-047); the pack's transport route is stated;
D-16 is answered "no surge claim" by the same logic.

### D-08 Case measurement and mock-up (rank 11)

**Evidence.** Only the CAD and the 1451-931 drawing are held (`v2/vendor/peli/`); the 1450PF frame is not bought.
A06: the one pack that fits (4S3P 18650, shrink-wrapped) leaves 1.35 mm across the east pocket, less than the Peli
wall uncertainty (W4-F14, up to 2 mm) and the floor fillet, so the fit waits on a measurement. A09: the D8
mezzanine's height reading and a collision with A32's J_AB2 under it are INFERRED from CAD. The standing rule
against asking the owner to measure a COTS part gives way only for the case and a mock-up (plan section 7); W4's
request to weigh COTS parts (M11) and to design the rod feet (K1) is withdrawn from the owner's list (masses come
from maker documents, the rod feet are the session's design).

**Options.** (a) Measure the case and build a cardboard or printed mock-up now, buy the frame later (RECOMMENDED);
(b) buy the 1450PF first, then one session; (c) no physical check before boards are ordered (risk: a fit error
found at assembly).

### D-06 Pack size and runtime target (rank 12, after D-08)

**Evidence.**
- A06 (INFERRED, box reading of B21's underside): at most about 145 Wh of 4S fits, 4S3P 18650 (144.7 Wh at the cell
  sheet's minimum) or 4S2P 21700 (about 144 Wh, marginal, no 21700 sheet held), in the east pocket only,
  shrink-wrapped, not in `pack_4s.py`'s box; no 4S4P (193 Wh) fits either pocket while board P stays beside the
  cells; nothing fits the west pocket.
- 32.62's own research gate asked for "4S Li-ion, about 100 to 150 Wh" (`:3056`); the "about 200 Wh" came later
  from the session's pack proposal (`:3062`, "session decision under the ruling, veto open").
- A05 (PROVISIONAL, +20 C): 4S3P gives PS-IDLE-SPEC (V2-SPEC's own wording) 4.2 h new and 3.4 h aged, PS-TYP 2.2 h
  new and 1.8 h aged; 4S4P would give 5.6 / 4.5 h and 3.0 / 2.4 h. "Aged" is 80 % capacity, an assumption: the cell
  sheet guarantees only 60 % after 500 cycles. 12.2 W of PS-IDLE and 29.7 W of PS-TYP rest on parts with no power
  document (TBD).
- The published 8 to 9.5 h is invalid (C-01).

**Options.** (a) **About 145 Wh, one 4S3P 18650 pack of the held cell (RECOMMENDED):** no design change, inside the
owner's own 100 to 150 Wh research gate. (b) 4S4P, 193 Wh: the session engineers board P out of the pocket (where it
goes and what it costs are TBD). (c) (a) plus a stated reliance on vehicle or solar input for missions longer than
the pack.

**The requirement shape recommended with any option:** battery-only hours in PS-IDLE-SPEC and in PS-TYP at +20 C for
an aged pack, with the aged capacity defined; and, separately, M1's pack-plus-solar energy balance over a mission
duration the owner sets (TBD; no source in the tree states one; round 1's "24 h" had no source and is withdrawn).
Consequence noted by W2: 4S3P charges above the cells' cycle-life current at the 4 A design setting (the session
lowers the setting, S-20) and has less peak headroom (D-11).

### D-11 Peak simultaneity (rank 13, after D-06)

**Evidence.** The owner's ruling of 4 September (`:2337`, restated `:2465`): every radio may transmit at once, no
serialisation, made for the old 1S node. PS-ALLTX is about 227 W at the battery with the outlets off, PS-ALLTX-OUT
about 316 W (A05, PROVISIONAL); at a 10 V end-of-discharge node 227 W is about 23 A against an 18 A declared peak,
the gauge's 20 A (2 s) trip and the 25 A blade; the pack that fits is the smaller one (A06).

**Options (product only; W2's split).** (a) Everything at once for minutes at any charge: needs thresholds above
20 A, a fuse coordination review and probably a larger pack than fits. (b) **Everything at once for a declared
key-down time above a declared state of charge, the outlets at their minimum contract (RECOMMENDED).** (c) The 30 W
PA and the outlets are never on together (a partial serialisation that amends the 4 Sep ruling). The hardware
interlock that drops the outlets while the PA keys is the session's under any answer (S-14).

### D-07 5G antenna jacks (rank 14)

**Evidence (A08, VERIFIED).** The RM520N-GL has four ports ANT0 to ANT3; the socket bought is key M and is being
replaced (S-12). Per the held Table 32: two jacks on ANT0 and ANT2 keep every primary transmit path including both
n77/n78 paths, and lose 4x4 download (2x2 at most), low-band receive diversity (about 2.3 to 3.9 dB of conducted
sensitivity on B8, B20, B28, n8, n20, n28, Table 34), the B20+n28 dual-connectivity combinations and the module's
own GNSS (the kit uses the LG290P); three jacks (ANT0, ANT2, ANT3) recover low-band diversity, those combinations
and three of four receive branches; four give the module's full design. The walls carry 11 SMA today
(`panel1450.py:117-118`); each extra jack is a sealed bulkhead, a board A blind-mate site, a board E float clamp and
a jumper. W4 found one more board A site that fits at X +46 and a second that needs a layout change. The pairing
ANT0 and ANT2 for a two-jack build is not a question: only it survives Table 32 (S-12).

**Options.** (a) Two jacks, as today: no case change. (b) **Three jacks (RECOMMENDED if the extra A site and E
clamp fit when D-08 is measured; otherwise (a)):** one more bulkhead (12), low-band diversity back, the site W4 found
free. (c) Four jacks: two more bulkheads (13), the module's full design, a layout change on A.

### D-12 External USB data port (rank 15)

**Evidence (W3).** The Glenair 233-370 USB host feed-through is picked, drawn and sealed on the connector plate but
has no data path in any generator (no `J_USBX`); the wall USB data path (bank 3, port 3) goes to the USB-C outlet;
all twelve hub ports are allocated (`gen_sch_b.py:519-521`). Both external ports are host ports, so neither gives a
laptop a console, while 32.50's approved gap list names a "USB-C PD outlet and console" and key fill (16f) runs over
the console.

**Options.** (a) **Route the existing data path to the 233-370 and make the USB-C a power outlet (RECOMMENDED):**
no hub port spent; the A pigtail and USB-C lead change. (b) Keep the data path on the USB-C and remove the 233-370
(one fewer sealed penetration). (c) Keep both: a second external data path from a freed or added hub port (board B's
tightest region). Whatever the answer, the console that 16f needs is designed by the session on the port kept (S-21);
it is approved, so it is not re-asked.

### D-13 Firmware integrity and the supervisor part (rank 16)

**Evidence.** Red team S2 (`RED-TEAM-2026-09-09.md:363`): no secure-boot requirement anywhere while flashing is
deliberately exposed (`J_FLASH`, `J_RPIBOOT`, `J_DBG` per slot, `gen_sch_b.py:567-571`). W6-F1: the H743 and the
H753 are pin-compatible on LQFP-100 (100 of 100 pins), the H753's secure access mode and crypto accelerators are
the only differences that matter, the H753 is 0 stock on both JLC codes and the H743 has 4335; the verdict is
PROVISIONAL (condition 1) because two of its own reopen triggers are live (S2, and D-03's option Z-C). The W6
challenger: the H743 keeps read-out protection and proprietary code protection (DS12110 p.1), so a
software-verified boot needs neither CRYP nor HASH; the owner set the H753 baseline himself. The compute modules'
own verified-boot option is not documented in the tree (TBD).

**Options.** (A) No verified-boot requirement for the prototype; a deferred requirement with a production trigger;
the H743 accepted. (B) **Software-verified boot on the H743 (and on the modules if the maker's documentation
supports it) as the prototype's floor; a hardware-isolated root of trust at a production trigger (RECOMMENDED).**
(C) A hardware-isolated root of trust now: the H753 through a hand-fit purchase route, or an external secure element
per supervisor (a board B change, cost and lead time to price). Under condition 1 the part mismatch closes only
after this ruling and after D-03 (Z-C would give the supervisors ZEROIZE work).

### D-14 Dock lift with the pack connected (rank 17)

**Evidence (W3).** The stack lifts off Preci-Dip spring contacts whose targets carry VIN_RAW and the pack current
(`ASSEMBLY.md:117`, `:131`); `J_DOCK` pin 12 is spare. **Session floor under any answer (S-22):** ASSEMBLY section 7
says kit off, pack XT60 unplugged and shore removed before the lift, and an insulating cap covers the E5 block while
the stack is out. **Options.** (a) **Accept the operator-dependent residual of the floor for the prototype
(RECOMMENDED), study (c) at Review D;** (b) procedure only, no cap; (c) a hardware "stack present" interlock on the
spare contact that holds the input hot-swap and the pack discharge off (touches boards A, E, possibly P and
decision 40).

### D-15 Cell under-voltage on gauge firmware (rank 18)

**Evidence (W2, decision 40 review).** The two parts decision 40 names are single-cell protectors (ABLIC S-8261
Rev.5.5_00, TI BQ2970 SLUSBU9I) and cannot sit across a 4S block; a 4S secondary protector is not held. W2
recommends (engineering) a 4S secondary over-voltage protector driving a chemical fuse, the BQ4050's FUSE output on
the same fuse and the PTC input enabled; after that, cell under-voltage still rests on the gauge's firmware and data
flash. **Options.** (a) Accept, with a data-flash verification step at commissioning; (b) **a secondary protector
that also covers under-voltage, if W6 sources one near the OV-only part's cost (RECOMMENDED), else (a);** (c) a
hardware under-voltage cut on board A, which protects the cells only against the kit's own load.

### D-16 Vehicle surge claim (rank 19)

**Evidence (W2, reframed after its challenger).** The 9 to 36 V vehicle input with a NATO 2-pin plug is ruled (32.50
16b). The entry (SMCJ40A clamp, 60 V FET) would not survive MIL-STD-1275 or ISO 16750-2 pulses (INFERRED; neither
standard is held); appendix `:1459` records "9 to 36 V, 50 V surge, not qualified". **Options.** (a) Qualify and
claim MIL-STD-1275 (fetch the standard, a 100 V class entry, a surge-rated clamp or active surge stopper on board E);
(b) claim ISO 16750-2 for civil 12 and 24 V vehicles (a similar redesign, levels TBD); (c) **claim no surge standard
for the prototype, the entry recorded as not qualified (RECOMMENDED, W2), with (a) if military vehicles become a
target market under D-04.** A NATO plug invites the military use; the owner should see that (c) narrows the claim,
not the ruled input.

### D-09 Independent review and test route (rank 20)

**Evidence.** Decision 40 open; no EMC evidence beyond calculators; agreement between agents is review, never
physical evidence (plan section 3); MeshSat holds a SIDN fonds grant whose voucher buys half a day of an expert from
its network (internet, security and privacy, not PCB). **Options.** (1) **SIDN voucher on ZEROIZE and key fill, a
paid battery and protection review before the pack is built, an EMC pre-compliance session after the prototype
exists (RECOMMENDED);** (2) the battery review only; (3) no external review before the prototype (the pack and
ZEROIZE judged only by the agents that designed them). Nothing is spent without the ruling.

### D-17 Board A USB-C CC pins (rank 21)

**Evidence (A04, W7).** Decision 31's item for board A (the CC pins protected inside U18, the TPS25740) is present
part for part on the netlist and the A32 board. TI SLVSDG8B 9.1.1: "The device has ESD protection built into the CC1
and CC2 pins so that no external protection is necessary"; 7.2 gives IEC 61000-4-2 +-8 kV contact and +-15 kV air
on CC1 and CC2, with the footnote that these were measured "based on implementation" on the TPS25740EVM-741 and
TPS25740AEVM-741 application boards. Board A reaches the plate receptacle through a pigtail from a header, which
the EVM does not. Decision 31 was ruled with `authority: SESSION`; accepting a residual no measurement in the tree
removes is the owner's under the 21 Sep test. **Options.** (a) **Confirm: accept TI's internal protection, carried
to the ESD gun at prototype test (TEST-PLAN M7) (RECOMMENDED);** (b) add an external low-capacitance array at the
connector: a few cents, and it would ride on the board A phase that is owed anyway (36 netlist-only parts and the
D2 value, A04), so it costs no extra route.

### D-18 IP68 fans (conditional, rank 22)

The session first retrieves Delta's 40 mm IP68 part (open-picks.txt:17 lists it; W4's round-1 "does not exist" was
refuted by its challenger) and checks it against the cooler rectangles and the face Z budget. Only if none fits does
the owner get the question: (a) keep IP68 everywhere with 60 mm fans that do not fit the coolers; (b) IP68 on the two
mixer fans, standard fans on the CM5 coolers inside the sealed, coated case (W4's recommendation then); (c) passive
coolers and a lower power mode.

## 3. Session items (not asked; recommendations with evidence)

| ID | Item | Recommendation | Evidence | Replaces |
|---|---|---|---|---|
| S-01 | EMCON reaches every transmitter | Pull WL_nDIS1..3 and BT_nDIS1..3 low through open-drain elements released only when both U6's control and EMCON_HW are high; U6's push-pull output and its internal ~100 k pull-up never touch the CM5 pin (the pins "may only be driven low", and no pin may be powered before the module's 5 V); gate the two WiFi cards' supplies from EMCON (32.56 promised a buck enable) or prove W_DISABLE1# on the bench before RF-002 counts them; decide whether 32.56's 5G supply switch is built | C-03, C-28; CM5 datasheet release 3 sections 2.1.1, 2.1.2, 3.1; SCPS131J Fig 8-2; A11 | round 1's "keep the U6 software drive for normal control" (withdrawn) |
| S-02 | RF-002 instrument | Enumerate every transmitter from the netlists (CONOPS section 4b's list) and fail any without a hardware gate; RF-002 on board B is not PASS until then | `PCB-RULE-STATUS-B.md:53`; `pcb_rules_coverage.yaml:607-615` | the false PASS of 3 |
| S-03 | Charger cell-count strap | R26/R27 to a 75 % pair, for example 13.3 k over 40.2 k (74.8 to 75.5 % at 1 %); swapping the two gives 3S and is not a fix | A02; SLUSE66A p18; `gen_sch_a.py:350` | |
| S-04 | Charger topology and host duty | Loads on VSYS as TI draws it, or a host-computed charge current of load plus charge; the host writes RSNS_RAC for the 10 mOhm R16; the hostless 256 mA default and the adapter-removal value confirmed on the bench | A02; SLUSE66A Figure 10-1; TI E2E 1316778 | |
| S-05 | Pack SMBus lead | E's J_SMB becomes JST-XH 1x4 matching P; P's pin 3 to the pack side of the shunt; ASSEMBLY.md and PANEL.md corrected; a J_SMB contract in `check_contracts.py` | A07; C-29 | |
| S-06 | IOHA section 15 | Correct the failover column to f = s % 3 + 1 | C-02 | |
| S-07 | PANEL.md sections 7 and 10, the charger text, OPERATING-ENVELOPE.md:88-89 | Rewrite after S-03, S-04 and S-08; the envelope edit is re-pinned in `pcb_envelope.yaml` and ENV-001 in the same change | C-04, C-23, C-27 | |
| S-08 | Power-up | R42 re-terminated to board A's 3.3 V; 4.7 k pull-downs on A's R21, R103, R104, R111, R112, R113 and B's R48, R50 to R53; firmware writes output registers before configuration registers; U21/U22 OVLO dividers resized (for example 143 k over 10 k); the SLOT_EN default decided here (W3's pull-up proposal is this item, not an owner question); RAIL_EN and KILL within their absolute maxima and an industrial-grade LTC2954 (W2 F-SQ-02, F-SQ-03) | A01; C-32 | W3 owner candidate 2 |
| S-09 | Reversed clamps and the clamp symbol | Reverse C D19 to D21, D D1, E D1 to D4 and D10, P D1; draw all 16 one-way clamps with a K/A symbol; add an orientation check to the protection gate | A03 | |
| S-10 | Battery-bay gas sensor | Fit the SGP41 picked in 32.54 where the battery bay's air is sampled; the envelope's hot end is not recomputed | C-05; appendix `:2896` | round 1's "recompute the hot end from the BME688" (withdrawn) |
| S-11 | Tamper and lid switch | A sealed switch under the frame to the always-powered sensor controller on E (the approved floor plan sites it on E6); it logs the lid and is the reduced mode's trigger; its ZEROIZE role follows D-03 | C-10; `:2848`; `gen_sch_e.py:90` | round 1 and W5 owner candidates (withdrawn) |
| S-12 | 5G socket and ports | Replace TE 1-2199119-5 (key M) with a key-B 3052 socket (A08 recommends TE 2199119-3, LCSC C590866; a mismatch until its land is proven against sheet 3's locating holes); wire ANT0 and ANT2 for two jacks (ANT3 added for three); correct ASSEMBLY.md:99's MAIN and DIV names | A08; C-19 | the round-1 D-07 precondition |
| S-13 | SIM 2 and dual SIM | Move SIM 2 to pins 40 DET, 42 DATA, 44 CLK, 46 RST, 48 VDD; settle eSIM against a second nano-SIM and the ordered module variant | A08; C-18 | |
| S-14 | Outlet interlock and pack thresholds | Keying the PA drops the PoE and USB-C outlets in hardware; the gauge thresholds and fuse coordination follow D-11 | W2 F-PR-03; C-21 | the engineering half of W2's peak candidate |
| S-15 | Vibration and shock severities | Declare TEST-PLAN E1 and E2 as the prototype's severities against decision 34's open item | C-07 | round-1 D-02c severities |
| S-16 | CM5 antennas | Name the slot whose radio feeds the WIFI 2.4 jack and what the other two do (internal antenna in a sealed case, or disabled); record the certification position | C-17 | |
| S-17 | DCF77 pulse | Route it to every slot as V2-SPEC says, or correct V2-SPEC to say the sensor controller serves it | C-26 | |
| S-18 | MIL-STD-461 edition | Pick the edition and curves for the installation D-04 names; fetch the standard; until then every run is characterisation | W5 candidate 3; D-04 | W5 owner candidate (split) |
| S-19 | ZEROIZE success indications | A failed key operation, drives that do not unlock, ZEROIZE COMPLETE after a full refresh, the 3 s sounder, a non-secret event in the panel controller's flash | D-03 | round-1 D-03 sub-question 3 |
| S-20 | Charge current | Set the 4S3P charge current inside the cell's cycle-life rating (W2: the 4 A design setting is above it) | W2 runtime section 8 | |
| S-21 | Console for key fill | A console path on whichever external port D-12 keeps (both are host ports as drawn) | W3; 32.50 16f | |
| S-22 | Dock lift floor | ASSEMBLY section 7 procedure and an insulating cap for the E5 block | W3 ODC-3 | |
| S-23 | Board A decision-31 hold | Keep it; lift only on criterion C-A31 (identity, fresh TRN-001, node sets, part-for-part protection rows, clamp polarity, CMP-001 on the board's own values); today D2 reads SMCJ33A on A32 against SMCJ40A in the netlist, so it stays | A04 | W7's SCH-002-only criterion |
| S-24 | Reduced-mode definition | One definition after D-02b, picked so the named lid-closed bearer set stays inside the thermal bound | C-16 | |

## 4. Notices (told, not asked)

- **N-01.** Decision 28's cited evidence (the P8 route) was taken with the BQ4050 on a 5 x 5 mm, 0.5 mm-pitch QFN
  land, while the part is a 4 x 4 mm, 0.4 mm-pitch VQFN (SLUSC67B pp. 1, 47, 50, 52; `gen_sch_p.py:71`); the
  evidence is void until P is retaken on the right land. At 2 oz the correct land meets JLC's 0.20 mm mask-bridge
  floor exactly (W6 challenger). The ruling's direction (four layers at 2 oz) is not challenged by this notice.
- **N-02.** The plan's section 1 bullet "panel unplugged: only APRS is inhibited" was wrong. With the panel
  unplugged every EMCON-gated transmitter is inhibited and no compute slot powers, so the kit transmits nothing
  (C-04, A01, A11). The real EMCON gap is the compute modules' own radios with the panel present (C-03).

## 5. Changes from round 1

| Round-1 item | Round 2 | Why |
|---|---|---|
| D-01 | kept; core set adds NEED-19; "second pack" dropped from deferred | A06; new NEED-19 |
| D-02a/b/c | a and b kept; c split: air carriage stays owner, severities become S-15 | challenger (severity mapping is engineering) |
| D-02d, D-02e | new | W2 cold start; W4 sun |
| D-03 | success indications moved to S-19; power-loss behaviour added; Z-B consequence on NEED-03 added; ATECC608B datasheet NDA noted | challenger; W5 |
| D-04 | VHF licence basis unrecorded (16a is HF only); EMC installation sub-question added | challenger; W5 |
| D-05 | rebuilt on A11; the self-contradictory option removed; SDR is dark under options 1 and 2 | challenger; A11 |
| D-06 | rebuilt on A06 and A05; "24 h" removed; asked after D-08 | challenger; A05; A06 |
| D-07 | rebuilt on A08: two, three or four jacks; pairing is S-12 | A08; W4 challenger |
| D-08 | moved before D-06; COTS weighing and rod-foot design removed | A06; W4 challenger |
| D-09 | kept | |
| D-10 to D-17, D-18, L-01, N-01, N-02 | new | challenger missing items; W2, W3, W6, W7 candidates; A10; W6 challenger |
| Engineering table | became S-01 to S-24 | adjudications |
