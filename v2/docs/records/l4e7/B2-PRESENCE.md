# Route B2: the solar receptacle's presence pair feeding U21's INP (P0-7, MESHSAT-1357; an unapproved PARTIAL proposal)

Prepared 5 October 2026 by task P0-7 at the coordinator's instruction of 17:12 CEST (route B2 selected by the coordinator as the
bounded PROVISIONAL desk route for D-10's port-level residual, under the owner's rules of 21 September and 5 October part 19, with
`SUPPLIER-P1-1-P0SOL.md` as its validation). Prototype design: nothing is built, bought, mated or measured. Every figure below is
printed by `l4e7_p0sol.py` (section 5 of `l4e7_p0sol.out`). Correspondence and orders: none; this page is drafts only.

**Standing of this route (the owner's review of checkpoint 4, part 23):** D-10 is an UNRESOLVED PROTECTION DEFECT in the present
model, carried as the receiving company's remaining engineering item E-1 (`SUPPLIER-P1-1-P0SOL.md`). Route B2 is an unapproved
PARTIAL interface proposal: it would prevent the guard-on step only for a source that arrives through a mating point of the
presence loop, it does not change the port's response when a step happens, and adopting or declining it does not resolve D-10.

**After Astra's focused check cx45 (5 October 2026, item Q6): NO PROTECTION CREDIT is taken for B2.** Its cold-connection
GUARANTEE is WITHDRAWN: no sequenced connector is selected and no worst-case contact and control timing proof exists, so no claim
that an arriving source meets Q12 off stands, and every claim resting on it is PROVISIONAL (section 5a). Round 2's statement that a
shorted presence core can only hold INP low was FALSE and is withdrawn: the two cores shorted together defeat the loop silently,
and a presence core shorted to a positive core of the lead puts INP over its 20 V absolute maximum, an OPEN defect the draft
introduces (section 5b). The guard-on case stays with E-1.

**The baseline does not depend on B2 (the owner's review, part 24: "Do not make the baseline depend on an unapproved
proposal").** Nothing on this page enters L4-E9's change list, Layer 6, Layer 7 or the register: the baseline's R-180 is not
replaced, no Layer 6 row is added, and the baseline composition of board E (`ORDER_E` in `l4e7_p0sol.py`) has no B2 step (the
draft is composed only in the separate check `ORDER_E_B2`). D-10 stays open either way until its remaining failing cases are
actually resolved (E-1).

## 1. Authority: is the receptacle's contact arrangement protected?

- **reserved.json** (`v2/ecad/tools/reserved.json`, the never-auto floor): nine classes (impedance targets, net class widths, fab
  rules, layer count and stackup, the intra-pair gap, the packer's regions, the DRC policy, the order set, the design record's 32.x
  headings). **None names a connector, an insert or a contact arrangement.** The board E draft touches no reserved line.
- **The owner's rulings on the connector plate:** ruling 6 of appendix 32.13 (4 September 2026) puts shore DC on "a keyed sealed
  circular wall connector" (MIL-DTL-38999); 32.32 closes ruling 4 with the panel "an accessory of the owner's choice ... on the shore
  plug's second pair" (BUILD.md); the part picks of 32.21, which the owner accepted on 4 September, name the Glenair
  D38999/20FC4PN receptacle and D38999/26FC4SN plug, shell 13, insert 13-4, four size 16 contacts. The insert is already reopened by
  D-06's consequence R-129 (the DC pair to size 12 contacts, insert 17-6 or 13-26; MISSING DRAFT).
- **The owner's two-part test (21 September 2026):** B2 changes what the kit is claimed to accept at its solar input (a panel then
  charges only through a plug that bridges the presence pair, where the accepted text says a panel of the owner's choice on the
  plug's second pair), changes an owner-accepted pick (the insert's contact count) and adds cost; and more than one option is still
  standing after the measurement (B2, or the drawn interface with the guard-on residual left to the supplier's S1). **Both halves
  hold: the interface decision is the owner's.** B2 therefore stands as a PROPOSAL, with the owner item of section 2. What is not
  the owner's and is taken here as SESSION decisions (section 6): how board E implements the loop.

## 2. The owner item (the smallest concrete decision, with its consequences)

**Decision asked:** may the kit's solar input carry a presence contact pair, with the intent that a source arriving through the
solar lead's mating points arrives with the guard off? (A partial measure, and an intent NOT PROVEN, section 5a; D-10 stays an
unresolved protection defect either way, E-1.)

| | (a) Adopt the presence pair (recommended) | (b) Keep the drawn interface |
|---|---|---|
| What changes | The wall receptacle's insert gains two contacts: with R-129's size 12 DC pair, insert 17-6 (six size 12 contacts, Amphenol's insert table, MAKER) carries DC A/B, solar C/D and the presence pair E/F with no further count change; the DC lead's cable goes from four to six cores; the solar tail ends in a connector whose presence contacts make last; the panel connects through a kit-supplied adapter lead that bridges the pair; board E gains J_SOLP and C80 and moves R96 (section 6) | nothing |
| What it would prevent | intended: the guard-on step for a source that arrives through a mating point of the loop. NOT PROVEN (cx45): the cold-connection guarantee is withdrawn until a sequenced connector is selected and the contact and control timing is proven (section 5a); IF an arrival meets Q12 off, the model's cold connection holds every absolute rating over the whole envelope (0.30 to 10.20 uH, section 5d of the .out). No protection credit as drafted (the pair's faults, section 5b); D-10 is not resolved by it (E-1) | nothing; the guard-on step stays a modelled absolute-rating violation below the port's floors (PV_F over 100 V below about 2.4 uH), E-1 |
| What stays | D-10 as an unresolved protection defect (E-1): the port's response to any step that still happens, a second stiff source added on the same lead while a panel holds the loop closed (OPEN, S1); the arriving source's slew margin line under 0.33 uH and PV_F over the recommended 80 V row under 0.78 uH (inside the absolute ratings, under 5d's condition; S2); the timing proof (section 5a) and the pair's fault detection and INP's protection (section 5b), engineering not yet drafted | everything of D-10's port residual (S1) |
| Cost | not quoted: one insert size up (shell 13 to 17 is already R-129's question), two crimp contacts, two cable cores, a 4-pole sequenced connector at the solar tail and an adapter lead per panel, an XH socket, a capacitor and a lead on board E, and the monitored detection and INP protection section 5b owes (ASSUMPTION: tens of euros a kit, before section 5b's parts) | none now; the residual's validation (S1) stays |
| Claim change | "a panel through the kit's adapter lead" instead of "a panel of the owner's choice on the plug's second pair" | none |

Recommendation (revised after cx45): NOT (a) as drafted. The drafted loop has no protection credit (section 5b: P1 defeats it
silently, P2 and P3 put INP over its absolute maximum) and no proven cold arrival (section 5a). (a) becomes a candidate to put to
the owner only with monitored or fault-tolerant detection and INP's protection drafted and checked, and the timing proof done; even
then it is a partial measure beside E-1's correction, never in place of it. Until then the board E draft is a PROPOSAL and nothing
of it is released.

## 3. B2's contact requirement (a PROPOSAL; NOT entered in L4-E9's change list)

**Text that would replace R-180 ("a stiff source's loop at J_SOLAR bounded and measured") only if the owner adopts B2 and its
section 5 engineering is done; until then the baseline's R-180 stands unchanged:**

> R-180 (Layer 7, the harness and the external connectors; a named prerequisite of the Layer 4 power gate under the owner's P0
> instruction of 5 October 2026, section 4; PROPOSAL until the owner rules section 2's item): **every mating point that the solar
> input's presence loop passes (the wall receptacle and the solar tail's connector) closes the presence pair only after both of the
> solar pair's power contacts carry the source (make-last), and opens at least 0.544 ms (the drafted turn-off, the .out's 5c)
> before either power contact parts (break-first), at the fastest mating and unmating speed the acceptance establishes.** The leads
> are TIMES: a spatial lead counts only with a speed bound (1 mm is 0.50 ms at 2 m/s, under the turn-off; the .out's 5e (ii)), and
> the sequence must be the selected part's printed one; no presence contact closes before either power contact. Where a mating point cannot sequence its
> contacts (the held D38999 sheets print no first-mate-last-break contact), that point is declared not a field mating point: the
> kit's DC lead stays mated at the wall, its coupling secured, and the requirement applies at the solar tail, where sources are
> connected. The presence pair is a twisted pair inside the lead, 22 to 24 AWG, insulated for the lead's voltage, with no
> connection to either power conductor or the shell; the panel adapter lead bridges it inside its plug.
> **Reason (PROVISIONAL; the cold-connection guarantee is WITHDRAWN after cx45):** the sequence is the intended means for a source
> to arrive on PV_F before INP can rise, so that U21's OV (at most 31.06 V, within 4 us) holds Q12 off above the cut-off and a source
> under it starts the stage through the gate slew. It is necessary, NOT shown sufficient: a power contact's bounce or interruption
> after the pair has made, with BST kept charged from the back-fed VS (TI SLUSEE5E p.17), can close the guard before the source
> re-arrives (the .out's 5e (iii) and (iv)); the complete enable path is not simulated; and the pair's faults P1 to P3 defeat it or
> overstress INP (section 5b). R-180 therefore also requires, before any protection credit: the selected parts' printed sequences,
> bounded opening, remating and bounce times, the enable path simulated at their extremes, and section 5b's detection and INP
> protection (part of D-10, B6, L4-F01; D-10 itself stays E-1's).
> **Acceptance:** on three specimens of each mating point, fifty mating and fifty unmating cycles each at the fastest hand speed
> (the speed measured): the presence pair's closure at least 1 ms after both power contacts and its opening at least 0.6 ms before
> either parts (the 0.544 ms turn-off with a SESSION margin), every bounce of every contact recorded (a four-channel continuity recorder at 1 MHz or faster), and on the assembled
> kit (S2) a 36 V source mated at the solar tail through a 0.30 uH loop leaves Q12's gate below its threshold and PV_F inside its
> absolute ratings, including a remating within 1 s of a withdrawal (BST charged). Each presence fault P1 to P6 applied on the
> specimen gives the response section 5b's corrected circuit claims.

## 4. The Layer 6 rows B2 would need (a PROPOSAL; NOT entered in Layer 6)

| Item | Selection | Basis | Owed |
|---|---|---|---|
| Wall receptacle | MIL-DTL-38999 series III, wall mount, the insert carrying six contacts: 17-6 (six size 12, MAKER: Amphenol series III insert table) with R-129's size 12 DC pair; or 17-8 (eight size 16) if the DC pair stays on paralleled size 16 contacts | ruling 6 of 32.13 (the 38999 family); R-129 (D-06's insert) | the MPN (CASE-MARGINS.md section 6), the plate cut-out for shell 17, the contacts' installed rating (R-129) |
| Plug | the matching D38999/26 straight plug, shell 17, socket contacts, with its M85049 strain relief | 32.32 (the plug family) | the MPN |
| Presence contacts | E and F of the insert, crimped on 22 to 24 AWG with the size's reducing sleeve or the insert's own contact size; not sequenced at the wall (section 3) | R-180 | the contacts' wire range |
| DC lead cable | six cores: the DC pair and the solar pair at the gauge R-129 and R-29 set, the presence pair as a twisted pair | R-180 | the cable's MPN |
| Solar tail connector | a 4-pole connector, IP67 mated, whose maker prints a first-mate-last-break sequence giving the presence contacts the time leads of section 3 at the acceptance's speed, keyed so that the DC tail's plug cannot mate it | R-180 | the family and MPN (NOT selected; no held sheet prints such a sequence) |
| Panel adapter lead | the tail connector's mate, the presence pair bridged inside it, to the panel's own connector | R-180 | the panel's connector (PANEL-ACC) |
| Board E | J_SOLP, JST-XH 1x2 B2B-XH-A (C158012, J_TAMP's part); C80 10 nF C0G 100 V 1206 (C184799, C127's part); R96 and R97 as drafted (R97 24.9k C136967) | `apply_gen_sch_e_p0sol_b2.py` | R96's LCSC code (owed since round 5) |

## 5. The board E draft and its checks (the .out's section 5)

`apply_gen_sch_e_p0sol_b2.py` (4 edits), composed in L4-E9's order after `apply_gen_sch_e_p0sol.py`: all seventeen drafts apply, the
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
the claims resting on it (the .out's 5d condition, R-180's reason, the owner item's benefit) are PROVISIONAL. A proof needs, and
this record holds:

1. **The contact sequence:** no sequenced connector is selected. The held Glenair D38999 sheets print no first-mate-last-break
   contact (so the wall receptacle cannot sequence the pair) and the solar tail's connector is not selected (section 4).
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

### 5b. The presence pair's faults (cx45, Q6; the .out's 5f): no protection credit

Round 2's "a shorted or broken presence core can only hold INP low" was FALSE and is withdrawn. The loop solved as a circuit (R96
at its least, R97 at its highest, a 10 mOhm short, U21's own pull-down not credited):

| Fault | INP | Consequence | Detection |
|---|---|---|---|
| P1, the two presence cores shorted together (or the pair's contacts welded) | 0.1997 x PV_F whatever the plug does: the guard on from PV_F 10.02 V at INP's highest corner (by 10.05 V at the most); 3.39 V at the hold's least 16.97 V | B2's function lost: with the plug withdrawn the back-fed PV_F holds the guard on and E-1's guard-on step returns | none on board E: LATENT |
| P2, INP's core shorted to a positive core of the lead (solar or DC) | PV_F: over INP's 20 V absolute maximum from PV_F 20.0 V (25 V at a 25 V source, 36 V at 36 V, 84.62 V at the arriving ring's worst) | U21 overstressed; the guard forced on; a hazard the draft INTRODUCES (without B2, INP's net never leaves board E): an OPEN defect of the B2 draft | none |
| P3, R96's core shorted to a positive core, the pair bridged | PV_F (R96 bypassed): as P2 | as P2 | none |
| P4, INP's core to the return | 0 | the guard held off, the solar input lost; fail-safe for D-10 | unmonitored (no charging is the only symptom) |
| P5, R96's core to the return | 0 (R96 dissipates PV_F squared over 99.9 kOhm) | as P4 | as P4 |
| P6, either core open | 0 | as P4 | as P4 |

If B2 is pursued, owed before any credit: **monitored or fault-tolerant presence detection** (for example a coded resistance in
the plug's bridge read by a window comparator, so that a short, a short to a positive core, a short to the return and an open all
read as faults and hold the guard off) and **INP held inside its absolute maximum** for a core at the lead's highest voltage (a
series resistance at J_SOLP pin 2 and a clamp), each drafted, composed in L4-E9's order and checked with failing mutations like
this draft, then the timing proof of section 5a. Neither is drafted here; the guard-on case stays with E-1.

## 6. SESSION decisions of the board E implementation

| Decision | Reason | How to reverse | authority | ruled_by | ruled_on |
|---|---|---|---|---|---|
| The loop sits between R96 and INP (R96 stays on PV_F; the pair carries the divider's node, not PV_F) | the loop carries at most PV_F / 100 kOhm, never the port's current, and R96's top on the contact would put PV_F itself on the lead. NOT a fail-safe arrangement (cx45): P1 defeats it silently and P2 and P3 put INP over its absolute maximum (section 5b); no protection credit is taken | move R96's top to the loop's return (the coordinator's literal wording) if a layout or EMC reason prefers it, with the fault current through a damaged core bounded first; section 5b's detection and INP protection are owed either way | SESSION | P0-7 (Claude), under the owner's rule of 21 September 2026 | 5 October 2026 |
| C80 10 nF C0G at INP | filters what the external pair picks up while keeping the withdrawn-plug turn-off under 0.6 ms | a larger C80 also delays INP's rise (a means, not shown sufficient: with the pair making first INP rises from the back-fed PV_F), at the cost of a slower turn-off | SESSION | P0-7 | 5 October 2026 |
| J_SOLP a JST-XH 1x2 (J_TAMP's part) | a signal pair, microamps; a part board E already carries | any 2-pole signal socket the harness prefers | SESSION | P0-7 | 5 October 2026 |
| U21's turn-on stays at INP (10.05 V at the most) | no change of the window; the loop only adds a series switch | none needed | SESSION | P0-7 | 5 October 2026 |

## 7. What B2 does not cover (OPEN)

- **A second stiff source added on the same lead while a panel holds the presence loop closed** (a parallel connection behind the
  plug, or a source spliced onto the panel's own lead): the guard is on and the step is section 2b's guard-on case (at the reference
  loop every rating but PV_F's recommended row holds; at the least loop the port fails). OPEN; validation P1-1's S1.
- **A stiff source below the stage's voltage arriving after a withdrawal:** while the guard is off, PV_P back-feeds PV_F through Q12's
  body diode, so such a source draws the stage's charge back through it (the reverse of the step; it would flow through the closed
  channel without B2). Not computed here; validation P1-1's S1 (row added).
- **The presence loop under CS114** (bulk cable injection on the lead now covers the pair): C80 is a means, not evidence; M3 reads
  INP on the specimen (S2 row added).
- **The timing proof (section 5a) and the pair's fault detection and INP's protection (section 5b):** engineering, not validation;
  OPEN, owed before any protection credit for B2. P2 and P3 are an OPEN defect of the B2 draft itself.
