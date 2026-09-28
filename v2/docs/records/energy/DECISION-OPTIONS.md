# Options: a second battery block for the 72-hour relay mission (M1)

MESHSAT-1357, 29 September 2026. Prototype design, nothing built. AI analysis on planning figures; numbers in
`ENERGY-RECONCILIATION.md` section 8. **In every option the mission as written (full kit, 72 hours, battery and
sun) still fails: requirement REQ-072 stays FAIL.**

1. **Second block wired to the first, one battery of 290 Wh under the existing protection board, plus a
   200-watt panel held to 100 W, the lower shutdown line, and the reduced state (one computer, 16 W: LoRa,
   Iridium, APRS, GNSS) whenever the sun alone cannot carry the full kit, about 16 hours of a September day.**
   Carries average September days only with the battery above 17 C, and average June days; never December. Costs under 150 EUR,
   0.6 kg; protection board additions; board A's heater limit; the west antenna cables must be re-planned (open);
   290 Wh in one pack (transport rules not held).
2. **The same battery, mission state unchanged.** About twice the runtime in every state; the full kit still stops
   in the first night in every month examined. Same costs.
3. **Keep one block.** The mission is recorded as unmet for prototype 1, an open limitation, not fulfilled. A 12 V
   external source may carry a night, optionally, never as the basis.

**Recommendation: 1**, the only option carrying a relay through a September night on battery and sun; it
reopens your deferral of the second pack (D-01) and changes the mission's operating state, both yours to rule.
