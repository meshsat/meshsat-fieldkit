# l4e13: U-03, the solar panel's open circuit inside REQ-016's window (layer 4 task L4-E13, MESHSAT-1357)

Prototype design, desk arithmetic; no physical unit is accepted. This folder settles L4-E9's unresolved choice U-03
(finding O-1 of `../l4e/L4-ENERGY-ARCHITECTURE.md`): a panel whose open-circuit voltage at -20 C, over the irradiance the
panel can see, is at or under REQ-016's 25 V, held at the stage's 17.6 V and portable, either by its maker's document
(route 1) or by the measurement of one identified unit (route 2, PANEL-ACC). U-03 reads CONDITIONAL DOWNSTREAM UNIT
SELECTION (PANEL-ACC).

| File | What it is |
|---|---|
| `L4E13-PANEL.md` | The one page: the requirement and the envelope (-20 C, 2111.4 W/m2), the three candidates' maker rows and bounds, PANEL-ACC's contract for one SunPower SPR-E-Flex-100 (the measurements, the specification, A-1 to A-4, the window, the worst accepted units' energy through the replay), the classification of U-03, the decisions taken, and the check's items mapped to their changes |
| `l4e13_panel.py` | The script, run from the repository root: `python3 v2/docs/records/l4e13/l4e13_panel.py > v2/docs/records/l4e13/l4e13_panel.out`. It runs `l4e_replay.main()` in-process with its locals captured (it must print `../l4e/l4e_replay.out` byte for byte), checks its own trace and day sums against the replay's and L4-E7's, reads the makers' rows from the pinned documents, and prints every figure. About a minute and a half |
| `l4e13_panel.out` | Its output, committed |
| `clarification/` | `sunpower-spr-e-flex-100.txt` and `solbian-sx-156.txt`: requests for a warranted Voc band, drafted for the owner to send (the session contacts no outside party) |
| `inputs/screen-2026-10-02.json` | The fourteen makers' documents read and set aside, each with its address and sha256 (search history) |
| `fetch_held_back.py` | Fetches Solbian's SX sheet, held back by its terms, into `v2/vendor/solar/held/` and checks its sha256; never run by a test (SunPower's two documents: `../a1solar/fetch_held_back.py`) |
| `checks/astra-check-l4e13-1.md` | The engineering collaborator's focused check at `b3e01e25` (NOT YET: B1, the acceptance windows lacked a justified maximum irradiance and bounded coefficient and model uncertainty; B2, U-03's classification left out the controlled-unit route; minors on the scenario and the extrapolation, Solbian's labels and the screen), filed by the coordinator's instruction byte for byte from its result, `accepted: no`. `L4E13-PANEL.md`'s last section maps each item to its change |

Tests: `v2/ecad/tools/tests/test_l4e13.py` (`env -C v2/ecad/tools/tests python3 run.py test_l4e13`).
