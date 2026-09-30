# Runtime and battery: Option A (48 h required, 72 h desired) against Option B (72 h required, upgraded battery) (stream l3batt, MESHSAT-1357)

**30 September 2026.** Branch `fnd/l3batt`, from main `db757e6b`. This page answers the owner's instruction of that day:

> "I am questioning the 72-hour requirement. Evaluate alternatives before asking me to sacrifice functions or accept
> restrictive deployment conditions."

**What this page is.** The author's analysis, AI arithmetic, not a qualified review and not the independent check.
- It is **prototype design**: nothing is bought, built, powered or measured. **Neither option is adopted**, and neither
  passes because its wording changes.
- HF and the tablet are kept in every row (a1mech arrangement A), with the same approved profile.
- Every figure is MAKER, NETLIST, MODELED or INFERRED. The sources are `runtime.out`, `lid_21700.out`, `load_trace.out`,
  `SHORTLIST.md` and `PROVENANCE.md` in this folder.

**Tablet charging, added on 30 September 2026: see `TABLET-BUDGET.md`.** The store figures on this page carry no tablet
energy. That page proposes a USB-C service budget (a PROPOSAL: 36 Wh a day at the outlet, 18 W peak, one 2 h daylight
window) and carries it through both options. With it, Option B's external store at TYP is about 190 Wh (WE, NOM90),
not about 120 Wh; Option A's is about 115 Wh.

## 0. The inputs, stated once

**The profile: PS-IDLE-SPEC, 42.8 W at the pack terminals** (`load_trace.out`).
- **The loads:** 39 of them, summing to 42.82 W. By tier: 16.8 W from a maker's figure, 11.3 W bounded by a maker, 6.3 W
  declared in a generator, and 8.4 W with no document (the monitor is 6.03 W of that).
- **Bounds:** 33.1 W LOW and 82.8 W HIGH.
- **HF:** in this state the QMX draws only its USB and HDMI 5 V (0.32 W). Its receiver (1.14 W) is a PS-TYP load; a
  sensitivity is given in 2c.
- **The tablet:** no load. It runs on its own battery, and the kit's USB-C outlet is off.
- **Additions:** the lid path's standby drain, 1.8 Wh over 72 h, is added where a lid pack exists (WE).

**The store:**
- ageing: aged to 80 % (REQ-014);
- shutdown: each pack stops at its own 3.00 V line with the 5 % reserve, and the kit runs on the other pack through the
  drafted join (TOPOLOGY.md 3c);
- temperatures: the base at +20 C and the lid at 13.23 C with solar; both at +20 C or both at -10 C battery-only.

**The sun (battery plus solar):**
- the day: SC-37's mean September day at Leiden, repeated, on ONE plane, 40 degrees facing south;
- the array: 400 Wp in 2S2P into the model's 200 W stage window;
- the build: TYP is the case, and WAB is a sensitivity only (its status as an acceptance condition is not established);
- the start: full packs at 06 and 18 UTC.

**The power path:**
- AS DRAWN: R11 10 mOhm, U3 4.15 A.
- The CORRECTED PATH: HYPOTHETICAL, with every correction of r11dep's R11-DEPENDENCY.md closed. It is **CONDITIONAL**
  on three undocumented efficiencies (stage and front end 0.93, charge 0.95); the 0.90 bracket is shown beside it.
- **A battery upgrade closes none of the electrical defects.**

## 1. Battery-only endurance (`runtime.out` 1; no solar)

| Arrangement | Usable Wh, +20 C / -10 C | Hours to the kit's shutdown, +20 C / -10 C |
|---|---|---|
| D-06's 4S3P of 35E alone (the ruled pack) | 107.9 / 44.5 | 2.52 / 1.04 |
| **Option A(i), both functions kept: base 4S6P + lid 4S9P of 35E** | **544.4 / 224.5** | **12.71 / 5.24** |
| the same with the lid in 21700 cells, 4S6P (P45B, 50E, M50LT) | 496.0 to 537.0 / 310.7 to 342.7 | 11.58 to 12.54 / 7.26 to 8.00 |
| + one or two external smart packs (PROPOSAL) | 611.6 / 678.7 at +20 C | 14.28 / 15.85 at +20 C |

**No arrangement runs 48 hours on battery alone.** The owner's options are battery-plus-solar options.

## 2. Battery plus solar (`runtime.out` 2 to 4; both functions kept)

### 2a. The present store (base 4S6P + lid 4S9P, 35E)

| Case | 48 h, TYP / WAB | 72 h, TYP / WAB |
|---|---|---|
| AS DRAWN (an upper bound) | NOT MET, 266.7 / 281.3 Wh unserved | NOT MET, 494.7 / 522.4 |
| CORRECTED PATH, NOM | NOT MET, 102.2 / 106.3 | NOT MET, 165.7 / 172.6 |
| the same at the 0.90 bracket | NOT MET, 105.5 / 109.3 | NOT MET, 171.1 / 177.6 |
| CORRECTED PATH, WE | NOT MET, 104.6 / 108.6 | NOT MET, 169.2 / 176.1 |
| the same at the 0.90 bracket | NOT MET, 112.5 / 136.5 | NOT MET, 184.1 / 230.8 |

**In every row the kit stops at 05 UTC of the first night:** hour 23 from a 06 UTC start and hour 11 from an 18 UTC
start.
- **Why:** with full packs at dusk the store holds 502.6 Wh at the reference temperatures (base 218.4, lid 284.2,
  `runtime.out` 2). The mean day has 14 hours at or under 60 W/m2 on the plane (17 to 06 UTC), and at 42.8 W that
  night asks more than the store holds.
- **The first night decides.** So the requirement's length (48 or 72 hours) does not.
- **Modelled historical coverage**, 864 past September windows (TYP, the corrected path included): **0 at 48 h and 0 at
  72 h** in every case.

### 2b. The store that would carry it (`runtime.out` 3)

The upgrade is found as the least store with the base held at 4S6P. It is written as the addition to the both-kept
store, in 35E-equivalent cells and usable Wh at the lid's 13.23 C, on the COMB line, with the kit never stopping:

| Corrected path | 48 h: TYP / WAB (sensitivity) | 72 h: TYP / WAB (sensitivity) |
|---|---|---|
| NOM | **+68.1 Wh** (+8.6 cells) / +70.9 | **+68.1 Wh** (+8.6 cells) / +85.0 |
| NOM at the 0.90 bracket | +80.1 / +116.3 | **+117.0** (+14.8 cells) / +188.7 |
| WE | **+79.6** (+10.1 cells) / +108.6 | **+116.2** (+14.7 cells) / +173.6 |

**Reading the table.**
- At NOM with TYP the two options need the **same** addition. Only the first night binds, and the days refill the
  packs.
- At WE, or at the 0.90 bracket, 72 hours asks about 36 Wh more than 48 hours, because the later nights start short.

### 2c. HF receiving continuously (a sensitivity, not the approved profile)

Adding the QMX receiver's 1.14 W raises the need, over the both-kept 4S9P lid:
- 48 h: to +10.7 cells, **+84.2 Wh** usable (NOM), and +15.5 cells, **+122.2 Wh** (WE);
- 72 h: to +12.0 cells, **+94.9 Wh** (NOM), and +23.7 cells, **+187.1 Wh** (WE).

## 3. Where an upgrade could come from (SHORTLIST.md)

- **In the Peli 1450 with both functions kept, no cell choice adds energy.**
  - The lid holds 36 cells of 35E. The same lid holds 24 of any 21700: two layers need 45.66 mm against its 44.39 mm at
    the worst (`lid_21700.out`, INFERRED).
  - A 21700 base block does not fit in the ruled orientation (INFERRED from a1mech's rows M4b, M5 and M6).
- **An external battery arrangement is the only route found, and it is a PROPOSAL.**
  - It could be complete smart packs (NH2054HD34, about 58 to 67 Wh usable each) or an equivalent external 4S pack.
  - It needs a wall connector, a join at VBAT limited under the pack's 8.25 A trip, a charge path and the host's SMBus.
  - **Neither way of joining it satisfies D-20; each is the owner's ruling to reopen.**
    - **Through the 9 to 36 V DC entry**, it is exactly D-20's "external DC source". EQ-13 route (b), which D-20
      answered, reads "(a vehicle, a shore supply or any DC source inside the entry's window, an external battery
      included ...)". It **falls under D-20's clause** ("requiring it overnight is not an acceptable substitute").
    - **Joined at VBAT** through a new wall connector, it is closest to EQ-13 route (d), "A larger pack: the owner's (it
      reopens D-06; the case never changes)". D-20 names "the pack of D-06" among the approved constraints.

## 4. The comparison, in one table

| | **Option A: 48 h required, 72 h desired** | **Option B: 72 h required, upgraded battery** |
|---|---|---|
| **Runtime requirement, and runtime modelled** | 48 h required. With the present store the kit runs **about 11 to 23 h** (to the first dawn, 05 UTC) as drawn and on the corrected path alike. **NOT MET** at 48 h and at 72 h; coverage 0 % | 72 h required. The same about 11 to 23 h with the present store: **NOT MET**. On the model it is met with the upgrade below (corrected path, CONDITIONAL on the three efficiencies) |
| **Battery arrangement, usable energy, mass, fit** | **Baseline: Option A(i)'s base 4S6P + lid 4S9P of 35E. It is not the ruled pack:** D-06 is one 4S3P, D-20 names "the pack of D-06" as a constraint, and A(i) itself awaits the owner's L3-OD1. 544 Wh usable aged at +20 C (225 at -10 C), 3.0 kg of cells; placement ESTABLISHED (a1mech A; three base rows OPEN). Every upgrade below is **added on top of A(i)**. **To meet 48 h:** **+68 Wh usable** (NOM TYP), +80 (WE TYP or NOM at 0.90), +109 to +116 (WAB). That is about 1.2 to 2 smart packs of 0.435 kg each at 58 to 67 Wh a pack (INFERRED), outside the case (PROPOSAL). **With the HF receiver on through M1** (a sensitivity, +1.14 W): **+84 Wh** (NOM TYP), **+122** (WE TYP) | The same present arrangement. **To meet 72 h:** **+68 Wh** (NOM TYP), **+116 to +117** (WE TYP, NOM at 0.90), +174 to +189 (WAB). That is about 2 smart packs at TYP and 3 to 4 with WAB (INFERRED, 58 to 67 Wh a pack), outside the case (PROPOSAL); **no in-case upgrade found**. **With the HF receiver on through M1:** **+95 Wh** (NOM TYP), **+187** (WE TYP), so **about 190 Wh at TYP** |
| **Retained functions** | all approved functions **kept in the kit and available**, at the approved profile's duties: **HF is not receiving and the tablet is not charged in this profile** (PS-IDLE-SPEC powers only the QMX's USB and HDMI 5 V, 0.32 W, and the USB-C outlet is off). HF receiving is the sensitivity figure above. **Tablet charging is UNQUANTIFIED:** REQ-011 has the tablet "fed by the USB-C outlet" but names no model (its acceptance "A tablet model is named" is open, SC-45). The missing figures are the tablet's battery energy and its daily use. The only bound held is the outlet's contract, 15 V at 3 A (45 W), which would be about 48 W at VBAT at the outlet stage's declared 0.93 (INFERRED) and exceeds the whole profile | the same |
| **Solar and operating assumptions** | SC-37's mean September day at Leiden, one plane 40/0, 400 Wp into a 200 W stage window, TYP (WAB a sensitivity), PS-IDLE-SPEC 42.8 W, starts 06 and 18 UTC, full aged packs, base +20 C, lid 13.23 C | the same |
| **Engineering changes, and feasibility unresolved** | the corrected power path (r11dep A-1, A-2, B-1 to B-5, C-1 to C-9); the external pack's join, connector, charge path and 8.25 A limit; the D-20 clause if fed through the DC entry. **Unresolved:** the three efficiencies (C-8); the corrected path itself; the base pockets' open rows; the weather beyond the mean day (coverage 0 today) | the same, with a larger external store |
| **Recommendation** | **Not recommended as relief.** 48 hours does not remove the need for more stored energy: the first September night fails at either length. It saves only about 36 Wh at WE or at the 0.90 bracket, and nothing at NOM TYP | **Recommended, but only with its store.** Keep 72 hours only together with an authorized external battery arrangement of about **120 Wh usable at its operating temperature** (the WE and 0.90 cases at TYP), or about 190 Wh if WAB becomes the acceptance condition or the HF receiver is to listen through M1, and with the corrected power path. Otherwise record M1 as not met (M-02) rather than shorten it |

## 5. The exact owner choice needed

**1. The runtime requirement.** Option A (48 hours required, 72 desired) or Option B (72 hours required). The record
shows the choice changes the needed store only at WE or at the 0.90 bracket (+80 against +116 Wh at TYP).

**2. Whether to authorize an external battery arrangement.** It is the only route found that keeps HF, the tablet, the
Peli 1450 and the approved load, and it is a **PROPOSAL**. Authorizing it would name four things:
- **the store it must add**: about +80 Wh usable for Option A and about +120 Wh for Option B at TYP. With the HF
  receiver on through M1, +122 and +187 Wh;
- **how it joins**. Neither way satisfies D-20:
  - through the DC entry it is D-20's "external DC source" (EQ-13 route (b)), which revisits D-20's "requiring it
    overnight is not an acceptable substitute";
  - joined at VBAT it reopens D-06 (EQ-13 route (d), "it reopens D-06").
- **whether WAB becomes an acceptance condition**, which raises both figures (to +109 and +189 Wh);
- **whether the tablet is to be charged through M1**, which adds an allowance not yet quantifiable (no tablet model);
  since quantified as a proposed budget in `TABLET-BUDGET.md`.

**3. If no external battery is authorized:** accepting that M1 is not met with HF and the tablet kept (owner action
M-02). No in-case arrangement found carries either 48 or 72 hours.

**The baseline itself is pending:** base 4S6P plus lid 4S9P is Option A(i), which awaits the owner's L3-OD1.

**Nothing else is asked.** The cell choice and the pack's integration are engineering tasks. The 72 hours themselves are
the session's figure (PROVENANCE.md): the owner's choice here sets M1's duration for the first time.

**Second issue** (CHECK-1 of `05ba0cf0`, minors 1 to 4): the HF-receiving store in Wh in the table; the profile's limits
named in the functions row (HF not receiving, the tablet not charged; tablet charging unquantified, its missing figures
named); the external pack's joins read against D-20 and EQ-13 routes (b) and (d); the baseline marked as Option A(i),
pending L3-OD1.
