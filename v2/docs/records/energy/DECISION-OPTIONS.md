# Options: the 72-hour relay mission (M1)

MESHSAT-1357, 29 September 2026 (replaces the sheet of 28 September). Prototype; AI analysis on the September
reference-day model (`ENERGY-RECONCILIATION.md` section 9, `energy_architecture.out`). Nothing is bought or built.

The mission as written (full kit at 42.8 W, 72 hours, battery and sun) needs at least 546 Wh of usable battery, about
655 Wh with margin, against today's 108 Wh, and at least 200 W of solar input where today's limit is 100 W.

**A. Full mission (recommended).** Two packs: the base pockets (4S6P) and a lid module (4S12P), 72 cells, 655 Wh usable
aged, about 3.6 kg of cells; four 100 W panels in two series pairs into a 200 W stage; the charger raised to about
125 W. On the model it meets September at +20 C (91 Wh left) and at +15 C (27 Wh left). Not yet drawn or tested:
REQ-072 stays FAIL until it is. Your decisions: **D-06**, the battery grows from 145 Wh to about 870 Wh nominal (it
travels by road or sea, not by air); **REQ-016**, solar input from 100 W and 25 V to 200 W and about 50 V; **D-01**, the
second pack moves into prototype 1 and takes the lid space of the deferred HF tray and tablet bracket.

**B. Keep today's limits.** M1 is not met; REQ-072 stays FAIL. Under them no design carries the full kit through a
September night.

**C. Reduced service (conditional, not a replacement).** Base pockets only, a 200 W panel held to 100 W, part of the kit
switched off 16 hours a day. REQ-072 stays FAIL. It holds on the average-day model only with cells at about 17 C or
warmer; its protection, harness, heater and mechanical findings stay open.
