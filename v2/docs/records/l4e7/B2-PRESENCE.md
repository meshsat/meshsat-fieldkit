# Route B2: the solar receptacle's presence pair feeding U21's INP (P0-7, MESHSAT-1357; UNSELECTED, WITHDRAWN AS DRAFTED)

Prepared 5 October 2026 by task P0-7 on the coordinator's task of 17:12 CEST, which named route B2 as a bounded PROVISIONAL desk
route for D-10's port-level residual. **Route B2 is UNSELECTED and WITHDRAWN AS DRAFTED** (Astra's check cx45 and recheck cx46, item
Q6; the owner's reviews, parts 24 and 25). This page is kept as the record of what was drafted and why it was withdrawn: it asks no
decision, recommends nothing for adoption and credits B2 with no protection. Prototype design: nothing is built, bought, mated or
measured. Every figure below is printed by `l4e7_p0sol.py` (section 5 of `l4e7_p0sol.out`). Correspondence and orders: none.

**Set 30 note (6 October 2026; record text only, on branch `fnd/w4l4e7` from set 30's integration commit 2c `53a68c7c`; adopted in
the NEXT set, where the coordinator regenerates; the promoted sha `__INTEGRATED__`).** What moved since this page was written: the
candidate merged set 31 (`6fe398e9`), whose L4-E9 data now reads route B2 UNSELECTED and WITHDRAWN AS DRAFTED with no owner item and
D-10 "as P0-7 states it (E-1, F1 to F4, the lower-source back-feed)" (`v2/docs/records/l4e9/SET31-CHANGES.md:54`); and the
remaining-engineering ledger's HO-F (`v2/docs/records/l4close/REMAINING-ENGINEERING.md` on `fnd/ledgerfix` `99bbc0c6`, cited as text
only; its section 6, item E) places the lower-source back-feed as REMAINING ENGINEERING inside E-1, S1's row (b) its later
validation, on the owner's part 23 (`v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`). Section 7 now says the same for the
back-feed and for the parallel source (both cases E-1 carries, not validation-only items; the parallel source's placement is this
branch's reading, SESSION: it is E-1's guard-on step itself and the ledger's HO-F lists S1's row (a) under E-1's task; reversed by the
coordinator's revision of the placement). Nothing else on this page moved: B2 stays
UNSELECTED and WITHDRAWN AS DRAFTED, outside the baseline, with no protection credit and no owner item.

**Standing:** D-10 is an UNRESOLVED PROTECTION DEFECT in the present model, carried as the receiving company's remaining engineering
item E-1 (`SUPPLIER-P1-1-P0SOL.md`; the owner's review of checkpoint 4, part 23). The withdrawn draft was a presence loop intended
to hold the guard off between a withdrawal and the next plug; this record proves no such effect, it would not change the port's
response when a step happens, and D-10 stays open either way until its remaining failing cases are actually resolved (E-1).

**Why it is withdrawn (cx45, Q6), with NO PROTECTION CREDIT taken for B2:** its cold-connection GUARANTEE was claimed without a chosen sequenced connector or a worst-case
contact and control timing proof, so that GUARANTEE is WITHDRAWN and no claim that an arriving source meets Q12 off stands
(section 5a). Round 2's statement that a
shorted presence core can only hold INP low was FALSE and is withdrawn: the two cores shorted together defeat the loop silently, and
a presence core shorted to a positive core of the lead puts INP over its 20 V absolute maximum, a defect the draft introduces
(section 5b). **P2 and P3 are REMAINING ENGINEERING outside the baseline:** any presence-pair route taken up again (as E-1's
correction or otherwise, as a new route with its own check) owes their correction first. The guard-on case stays with E-1.

**The baseline does not depend on B2 (the owner's review, part 24: "Do not make the baseline depend on an unapproved
proposal").** Nothing on this page enters L4-E9's change list, Layer 6, Layer 7 or the register: the baseline's R-180 is not
replaced, no Layer 6 row is added, and the baseline composition of board E (`ORDER_E` in `l4e7_p0sol.py`) has no B2 step (the
draft is composed only in the separate check `ORDER_E_B2`).

**No owner item (the owner's review, part 25):** no owner action rests on B2; the approved interface stands (the panel, an
accessory of the owner's choice, on the shore plug's second pair: BUILD.md and appendix 32.32; the receptacle the owner accepted
in 32.21). Round 2's owner item and its recommendation are withdrawn.

## 1. Authority, as found in round 2 (a record)

- **reserved.json** (`v2/ecad/tools/reserved.json`, the never-auto floor): nine classes (impedance targets, net class widths, fab
  rules, layer count and stackup, the intra-pair gap, the packer's regions, the DRC policy, the order set, the design record's 32.x
  headings). **None names a connector, an insert or a contact arrangement.** The board E draft touches no reserved line.
- **The owner's rulings on the connector plate:** ruling 6 of appendix 32.13 (4 September 2026) puts shore DC on "a keyed sealed
  circular wall connector" (MIL-DTL-38999); 32.32 closes ruling 4 with the panel "an accessory of the owner's choice ... on the shore
  plug's second pair" (BUILD.md); the part picks of 32.21, which the owner accepted on 4 September, name the Glenair
  D38999/20FC4PN receptacle and D38999/26FC4SN plug, shell 13, insert 13-4, four size 16 contacts. The insert is already reopened by
  D-06's consequence R-129 (the DC pair to size 12 contacts, insert 17-6 or 13-26; MISSING DRAFT).
- **The owner's two-part test (21 September 2026):** a presence pair would change what the kit is claimed to accept at its solar
  input, an owner-accepted pick (the insert's contact count) and the cost, so its interface could only ever be the owner's. Under
  part 25 no such decision is pending: the approved interface stands. The SESSION decisions of section 6 concern only how the
  withdrawn draft implemented the loop.

## 2. What the withdrawn draft would have changed (a record, not a request)

The wall receptacle's insert would have gained two contacts (with R-129's size 12 DC pair, insert 17-6, six size 12 contacts,
Amphenol's insert table, MAKER); the DC lead's cable four to six cores; a sequenced connector at the solar tail and a kit-supplied
adapter lead bridging the pair at each panel; on board E, J_SOLP and C80 and R96 moved (section 6); and the kit's claim would have
read "a panel through the kit's adapter lead" instead of "a panel of the owner's choice on the plug's second pair". Cost not
quoted. None of it is requested; the approved interface stands.

## 3. The withdrawn draft's contact requirement (WITHDRAWN AS DRAFTED; NOT entered in L4-E9's change list)

**Not a requirement: the baseline's R-180 ("a stiff source's loop at J_SOLAR bounded and measured") stands unchanged.** Kept as the
record of what a presence-pair route would have to meet, with what it would still not show:

> (WITHDRAWN AS DRAFTED; would have been Layer 7, the harness and the external connectors): **every mating point that the solar
> input's presence loop passes (the wall receptacle and the solar tail's connector) closes the presence pair only after both of the
> solar pair's power contacts carry the source (make-last), and opens at least 0.544 ms (the drafted turn-off, the .out's 5c)
> before either power contact parts (break-first), at the fastest mating and unmating speed the acceptance establishes.** The leads
> are TIMES: a spatial lead counts only with a speed bound (1 mm is 0.50 ms at 2 m/s, under the turn-off; the .out's 5e (ii)), and
> the sequence must be the chosen part's printed one; no presence contact closes before either power contact. Where a mating point cannot sequence its
> contacts (the held D38999 sheets print no first-mate-last-break contact), that point is declared not a field mating point: the
> kit's DC lead stays mated at the wall, its coupling secured, and the requirement applies at the solar tail, where sources are
> connected. The presence pair is a twisted pair inside the lead, 22 to 24 AWG, insulated for the lead's voltage, with no
> connection to either power conductor or the shell; the panel adapter lead bridges it inside its plug.
> **Reason (the cold-connection guarantee is WITHDRAWN after cx45):** the sequence was the intended means for a source
> to arrive on PV_F before INP can rise, so that U21's OV (at most 31.06 V, within 4 us) holds Q12 off above the cut-off and a source
> under it starts the stage through the gate slew. It is necessary, NOT shown sufficient: a power contact's bounce or interruption
> after the pair has made, with BST kept charged from the back-fed VS (TI SLUSEE5E p.17), can close the guard before the source
> re-arrives (the .out's 5e (iii) and (iv)); the complete enable path is not simulated; and the pair's faults P1 to P3 defeat it or
> overstress INP (section 5b). Any protection credit would also need: the chosen parts' printed sequences,
> bounded opening, remating and bounce times, the enable path simulated at their extremes, and section 5b's detection and INP
> protection (part of D-10, B6, L4-F01; D-10 itself stays E-1's).
> **Acceptance:** on three specimens of each mating point, fifty mating and fifty unmating cycles each at the fastest hand speed
> (the speed measured): the presence pair's closure at least 1 ms after both power contacts and its opening at least 0.6 ms before
> either parts (the 0.544 ms turn-off with a SESSION margin), every bounce of every contact recorded (a four-channel continuity recorder at 1 MHz or faster), and on the assembled
> kit (S2) a 36 V source mated at the solar tail through a 0.30 uH loop leaves Q12's gate below its threshold and PV_F inside its
> absolute ratings, including a remating within 1 s of a withdrawal (BST charged). Each presence fault P1 to P6 applied on the
> specimen gives the response section 5b's corrected circuit claims.

## 4. The Layer 6 rows the withdrawn draft would have needed (a record; NOT entered in Layer 6)

| Item | What it would have been | Basis | Owed |
|---|---|---|---|
| Wall receptacle | MIL-DTL-38999 series III, wall mount, the insert carrying six contacts: 17-6 (six size 12, MAKER: Amphenol series III insert table) with R-129's size 12 DC pair; or 17-8 (eight size 16) if the DC pair stays on paralleled size 16 contacts | ruling 6 of 32.13 (the 38999 family); R-129 (D-06's insert) | the MPN (CASE-MARGINS.md section 6), the plate cut-out for shell 17, the contacts' installed rating (R-129) |
| Plug | the matching D38999/26 straight plug, shell 17, socket contacts, with its M85049 strain relief | 32.32 (the plug family) | the MPN |
| Presence contacts | E and F of the insert, crimped on 22 to 24 AWG with the size's reducing sleeve or the insert's own contact size; not sequenced at the wall (section 3) | section 3 | the contacts' wire range |
| DC lead cable | six cores: the DC pair and the solar pair at the gauge R-129 and R-29 set, the presence pair as a twisted pair | section 3 | the cable's MPN |
| Solar tail connector | a 4-pole connector, IP67 mated, whose maker prints a first-mate-last-break sequence giving the presence contacts the time leads of section 3 at the acceptance's speed, keyed so that the DC tail's plug cannot mate it | section 3 | the family and MPN (none chosen; no held sheet prints such a sequence) |
| Panel adapter lead | the tail connector's mate, the presence pair bridged inside it, to the panel's own connector | section 3 | the panel's connector (PANEL-ACC) |
| Board E | J_SOLP, JST-XH 1x2 B2B-XH-A (C158012, J_TAMP's part); C80 10 nF C0G 100 V 1206 (C184799, C127's part); R96 and R97 as drafted (R97 24.9k C136967) | `apply_gen_sch_e_p0sol_b2.py` | R96's LCSC code (owed since round 5) |

## 5. The withdrawn board E draft and its checks (the .out's section 5)

`apply_gen_sch_e_p0sol_b2.py` (4 edits, WITHDRAWN AS DRAFTED), composed only in the separate check `ORDER_E_B2`, after
`apply_gen_sch_e_p0sol.py`: all seventeen drafts apply, the
draft refuses a second application, the generator runs (298 parts). Four predicates hold in the netlist on top of section 2a's nine
(R96 from PV_F to the loop net and not to INP; J_SOLP the loop's only path to INP; INP's net exactly U21, R97, C80 and J_SOLP; U21's
OV and UVLO dividers as drafted). Four mutations each fail (R96 straight onto INP, the loop bridged on the board, R97 off INP, C80
off INP). The withdrawn plug, the pair intact: INP falls from its highest 6.20 V under V(INP_L)'s least 0.8 V in at most 0.543 ms
and Q12 is off at most 0.544 ms after the pair opens. The arriving source IF it meets Q12 off (a CONDITION the model sets, cold=True,
not derived from the contact or control timing; section 5a): over the record's whole grid (608 events, the worst equal to the
record's cold connection) every absolute rating held (PV_F 84.62 V of 100 V, slew 56.10 V/us of 60, INP 16.90 V of 20, EN 12.48 V
of 20, PV_F's least 0 V); the 90 V, 18 V lines held everywhere; the 54 V/us slew line holds from 0.33 uH and the recommended 80 V
VS row from 0.78 uH (PROVISIONAL, S2).

### 5a. The cold-connection guarantee, WITHDRAWN (cx45, Q6; the .out's 5e)

Round 2 claimed that every source arriving through a mating point of the loop meets Q12 off. Nothing in this record proves it, and
the claims resting on it (the .out's 5d condition, section 3's reason) are withdrawn with it. A proof would need, and this record
holds:

1. **The contact sequence:** no sequenced connector is chosen. The held Glenair D38999 sheets print no first-mate-last-break
   contact (so the wall receptacle cannot sequence the pair) and the solar tail's connector is not chosen (section 4).
2. **Time leads, not distances:** Q12 is off at most 0.544 ms after the pair opens, so the pair must open at least that long
   before either power contact parts. A spatial lead becomes a time only under a speed bound and no held sheet prints one; at the
   ASSUMED speeds 0.5, 1.0 and 2.0 m/s the turn-off needs 0.27, 0.54 and 1.09 mm, and round 2's 1 mm covers it only under 1.84 m/s.
3. **BST is not discharged by a withdrawal:** "A 12V, 100µA charge pump is derived from VS terminal" and "With VS applied and
   EN/UVLO pulled high, the charge pump turns ON" (TI SLUSEE5E p.17, PRINTED). The back-fed PV_F keeps VS and EN/UVLO supplied
   until it falls through U21's UVLO falling point (the band's least 7.46 V), so a remating turns Q12 on within tPU(INP_H), at most
   2 us (PRINTED), of INP crossing V(INP_H). Round 2's "BST until it charges, at least 50 ms from discharged" is withdrawn.
4. **Bounce and interruption are unbounded:** a power contact interrupted after the pair has made re-makes onto a closed guard
   (a source under the cut-off: Q12 already on; a source over it: once PV_F falls through OV's falling point, 27.07 to 29.26 V,
   with INP high and BST charged). PV_F's decay with Q12 off and the contacts' interruption times are not computed or printed here.
5. **The complete enable path is not simulated** (the sequence and bounce, the loop and C80, INP's thresholds and delays, OV,
   UVLO, the gate drive with BST charged, the port's ring) at the timing extremes.

### 5b. The presence pair's faults (cx45, Q6; the .out's 5f): no protection credit; P2 and P3 REMAINING ENGINEERING

Round 2's "a shorted or broken presence core can only hold INP low" was FALSE and is withdrawn. The loop solved as a circuit (R96
at its least, R97 at its highest, a 10 mOhm short, U21's own pull-down not credited):

| Fault | INP | Consequence | Detection |
|---|---|---|---|
| P1, the two presence cores shorted together (or the pair's contacts welded) | 0.1997 x PV_F whatever the plug does: the guard on from PV_F 10.02 V at INP's highest corner (by 10.05 V at the most); 3.39 V at the hold's least 16.97 V | B2's function lost: with the plug withdrawn the back-fed PV_F holds the guard on and E-1's guard-on step returns | none on board E: LATENT |
| P2, INP's core shorted to a positive core of the lead (solar or DC) | PV_F: over INP's 20 V absolute maximum from PV_F 20.0 V (25 V at a 25 V source, 36 V at 36 V, 84.62 V at the arriving ring's worst) | U21 overstressed; the guard forced on; a hazard the draft INTRODUCES (without B2, INP's net never leaves board E): a defect of the withdrawn draft, REMAINING ENGINEERING outside the baseline | none |
| P3, R96's core shorted to a positive core, the pair bridged | PV_F (R96 bypassed): as P2 | as P2 | none |
| P4, INP's core to the return | 0 | the guard held off, the solar input lost; fail-safe for D-10 | unmonitored (no charging is the only symptom) |
| P5, R96's core to the return | 0 (R96 dissipates PV_F squared over 99.9 kOhm) | as P4 | as P4 |
| P6, either core open | 0 | as P4 | as P4 |

**REMAINING ENGINEERING, outside the baseline:** P2 and P3 (and the latent P1) stay recorded against any presence-pair route. Any
such route taken up again, as a new route with its own check, owes before any credit: **monitored or fault-tolerant presence
detection** (for example a coded resistance in
the plug's bridge read by a window comparator, so that a short, a short to a positive core, a short to the return and an open all
read as faults and hold the guard off) and **INP held inside its absolute maximum** for a core at the lead's highest voltage (a
series resistance at J_SOLP pin 2 and a clamp), each drafted, composed in L4-E9's order and checked with failing mutations like
this draft, then the timing proof of section 5a. Neither is drafted here, and nothing in the baseline carries the draft; the
guard-on case stays with E-1.

## 6. SESSION decisions of the withdrawn board E draft (a record)

| Decision | Reason | How to reverse | authority | ruled_by | ruled_on |
|---|---|---|---|---|---|
| The loop sits between R96 and INP (R96 stays on PV_F; the pair carries the divider's node, not PV_F) | the loop carries at most PV_F / 100 kOhm, never the port's current, and R96's top on the contact would put PV_F itself on the lead. NOT a fail-safe arrangement (cx45): P1 defeats it silently and P2 and P3 put INP over its absolute maximum (section 5b); no protection credit is taken | move R96's top to the loop's return (the coordinator's literal wording) if a layout or EMC reason prefers it, with the fault current through a damaged core bounded first; section 5b's detection and INP protection are owed either way | SESSION | P0-7 (Claude), under the owner's rule of 21 September 2026 | 5 October 2026 |
| C80 10 nF C0G at INP | filters what the external pair picks up while keeping the withdrawn-plug turn-off under 0.6 ms | a larger C80 also delays INP's rise (a means, not shown sufficient: with the pair making first INP rises from the back-fed PV_F), at the cost of a slower turn-off | SESSION | P0-7 | 5 October 2026 |
| J_SOLP a JST-XH 1x2 (J_TAMP's part) | a signal pair, microamps; a part board E already carries | any 2-pole signal socket the harness prefers | SESSION | P0-7 | 5 October 2026 |
| U21's turn-on stays at INP (10.05 V at the most) | no change of the window; the loop only adds a series switch | none needed | SESSION | P0-7 | 5 October 2026 |

## 7. What stays OPEN whatever becomes of B2

- **A second stiff source added on the same lead while a panel holds the presence loop closed** (a parallel connection behind the
  plug, or a source spliced onto the panel's own lead): the guard is on and the step is section 2b's guard-on case (at the reference
  loop every rating but PV_F's recommended row holds; at the least loop the port fails). OPEN, inside E-1 (its guard-on step, cases
  F1 to F3 of `SUPPLIER-P1-1-P0SOL.md`); P1-1's S1 row (a) is the later validation of E-1's correction for it (set 30 note).
- **A stiff source below the stage's voltage arriving after a withdrawal:** while the guard is off, PV_P back-feeds PV_F through Q12's
  body diode, so such a source draws the stage's charge back through it (the reverse of the step; it would flow through the closed
  channel without B2). Not computed here: an OPEN case, not a failed one (no record computes it, so it neither fails nor passes), and
  REMAINING ENGINEERING inside E-1: the receiving company computes it on E-1's corrected circuit as part of E-1's correction, against
  E-1's requirements (`SUPPLIER-P1-1-P0SOL.md`, E-1 (a) and (b)); P1-1's S1 row (b) is the later validation of that computation, not
  a substitute for it (set 30 note, 6 October 2026, in place of "validation P1-1's S1 (row added)": the remaining-engineering
  ledger's HO-F and its section 6, item E, `fnd/ledgerfix` `99bbc0c6`; the owner's part 23, "Supplier item S1 must carry that
  engineering problem, rather than presenting it solely as an unperformed validation test.",
  `v2/docs/handover/OWNER-INSTRUCTION-2026-10-05.md:680`; cx46, "D-10's E-1 retains F1-F4 and the lower-source back-feed case.",
  `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:95`).
- **The presence loop under CS114** (bulk cable injection on the lead would cover the pair): C80 is a means, not evidence; no S2
  row rests on it while B2 is withdrawn.
- **P2 and P3, the withdrawn draft's own defect, with the timing proof (section 5a) and the pair's fault detection (section 5b):**
  REMAINING ENGINEERING outside the baseline, not validation; owed before any presence-pair route could claim anything.
