# Is everything orderable? Read back from JLCPCB, 12 September 2026

Written by the runner under the owner's instruction of 12 September: *"I will not read anything, you do
it and approve it, and check if everything is orderable or not before you finalise the draft order."*

**The answer is NO, not yet, and every reason is named and counted below.** Nothing is ordered, no cart
line has been touched, and the draft order is not finalised. What follows is what would happen if it
were, so that the gap is a list rather than a feeling.

## How this was checked

`tools/jlc_certify.py` reads every BOM line of the newest deliverable folder of each of the seven boards
and asks JLCPCB's own parts API about it: the part, its package against the land we drew, its stock
against a need of five boards, and its price. A line is settled only if one of three things is true.

- **CERTIFIED**: JLCPCB has that exact part, in that package, in stock for the order.
- **HAND_FIT**: we do not buy it through JLCPCB, and `tools/jlc-handfit.txt` says where we do.
- **BENCH_FITTED**: a header, test point or solder land that JLC places on nothing and we fit by hand.

**469 rows. 432 settled: 376 certified, 41 hand-fit with a written purchase route, 15 bench-fitted.
37 open.** The certified parts come to about **2,690 GBP for five of every board** at single-unit prices,
before assembly, shipping and VAT.

| board | open rows | what they are |
|---|---:|---|
| A power | 5 | **A24 was cut at 18:10 and took A from 17 to 5.** All five are the same row nine times over: the SMA jacks, whose prose named the radio at the far end of the pigtail. Corrected in the generator; they clear on A's next re-finish |
| B compute | 22 | the shipped folder is B16-QUOTE of 8 September, superseded by B19, which is held by owner decision 13 |
| C panel backer | 3 | the shipped folder is C7. **C10 is at 0 hard and 1 unrouted**, its best ever, and that last connection needs an escape or a placement change at U3 pad 10 |
| D APRS | 3 | fixed at source today; D's re-route is held by the PWR width question below |
| E1 dock | 3 | fixed at source today, waiting on the re-cut that is running |
| P pack BMS | 1 | the same |

**A24 IS CUT (18:10 CEST):** hard 0, unrouted 0, `check_pcb_a` ALL PASS on 798 checks, `dc_drop` 12 of 12
rails MET, impedance 3 of 3 pairs, `netlist_board` 2004 of 2004, `verify_deliverable` ALL PASS on 35 of 35.
It carries owner ruling 10's parts, **C596319** on the twenty-two 10 uF 50 V and **C5156756** on the three
100 V parts of the PoE stage's output, and **no copper moved to get them**: 5,212 tracks and vias, every
zone's filled area and all 400 footprint positions identical across the change.

## The three reasons, in order of size

**1. Three of the seven folders describe a board we are not building.** The certifier reads the newest
deliverable on disk, and for A, B and C that is A22, B16-QUOTE and C7. Their BOMs carry codes that were
corrected in the generators days ago: four JLCPCB house-brand M.2 sockets where the schematic names TE
and Amphenol parts, an 0805 ferrite on four 0603 lands, an SMCJ15A where an SMCJ18A is named. **Every one
of those codes is already on `tools/lcsc-blocked.txt` and in no generator**, so they cannot come back;
they are simply still sitting in folders nobody has re-cut. **A24, B19 and C10 have to be cut before this
question can be answered for those boards**, and B is held by decision 13 below.

**2. Twenty defects that were real were fixed today, at source, and reach the folders on the next cut.**
Found by reading every non-certified row rather than by trusting the count:

- **Eleven connector rows named no part at all.** E's DC inlet read "vehicle and shore DC in 9-36 V, lead
  from the D38999 wall receptacle DC pair (JST-VH, 10 A)" and carried no code. The D38999 is the
  receptacle at the far end of the lead; the part on the board is a JST B2P-VH. JLCPCB answered the
  search with a 34.57 GBP Amphenol circular MIL connector at stock 0. Every such row now names its own
  socket first and carries its code, and all eleven were put back through the live API: ten certified
  with stock covering the order, one hand-fit with its route.
- **Eight more connector bodies were exempted from the BOM as though they were wire**, on four boards,
  through `lcsc-allow.txt` lines that meant the LEAD and said the part. Each is a JST socket in stock.
- **A wrong package on a part that matters.** E's U5, the solar tracker's LT8705A, carried the TSSOP-38
  order code on a QFN-38 land. Corrected, the wrong code blocked, and the stock problem behind it is
  **decision 12**.
- **A part that would not have turned on.** C's Q6 asked for a FET under 200 mOhm at 2.5 V of gate drive
  and carried a 2N7002, whose threshold runs to 3 V. It is a Vishay Si2302 now, same land, same pin
  order.
- **Five panel and dock parts had no purchase route written down**, so they read as unchosen: A's Mill-Max
  spring pins and pre-charge pin, C's sounder and its two headset jacks.

**3. Three rows are genuinely still open, and two of them are a document rather than a decision.**

| row | what is owed |
|---|---|
| B's `J_RB9704`, the RockBLOCK 9704 16-pin IDC header | a part against our own narrow-pad 2x8 land. It is NOT in B's CPL exclusion list, so JLC would be asked to place it. B is blocked by decision 13 anyway |
| C's sounder, Floyd Bell MC-09-530-Q **class** | the dash number, picked from Floyd Bell's IP67 range against 5 V DC continuous. Declared hand-fit with its route; the row says "class" on purpose |
| C's two U-174/U headset jacks | Amphenol Nexus's drawing, which this tree does not hold. The 17 mm panel hole rests on it. They are mounting holes with no BOM line, so they block no assembly, only the plate |

## What blocks the order beyond the parts

1. **Owner decision 12**: JLCPCB stocks three of E's LT8705A against a need of five. Whether `U5` leaves
   the CPL is a change to what is bought, which is on the never-auto floor.
2. **Owner decision 13**: seven of B's packer regions are smaller than the parts assigned to them, and
   have been since they were drawn. B's placement is blocked until the rectangles are sized.
3. **The four-against-six layer price has never been taken.** No like-for-like quote exists for any board
   at its real outline and quantity five. JLCPCB's parts API answers without a login and its PCB pricing
   path does not, and the runner never logs into JLCPCB by standing rule, so this number has to come from
   the ordering session on the laptop. Until it does, "too many layers" has no price in this record.
4. **D's re-route answers owner ruling 9 and the answer is not free.** Widening the PWR class to 1.2 mm on
   the inner layers leaves **twelve connections open, and all twelve are power nets** (`/+5V_D8` six, GND
   three, `/+3V3_D8` two, `/PCM_VDD` one) where D reached 0 and 0 at 0.5 mm. An arm at the old width is
   running to prove the width is the cause rather than the tools; the result goes to the owner with the
   number, because 1.2 mm was ruled and the board cannot route it.
5. **Two deliverables are being re-cut as this is written** (E7, P3) and one is not cut at all (C10, one
   connection short). **A24 is cut.**

## What I will do next, without being asked

Re-cut D, E and P; re-certify all seven; and report the residue against this document. The draft order
is not finalised and no cart line is touched until that residue is empty or declared, decisions 12 and 13
are answered, and the layer price is in.
