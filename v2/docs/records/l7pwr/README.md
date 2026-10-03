# l7pwr: the fans, the T-H1 mock-up bill and the dock lead's pulse capability (Layer 7, MESHSAT-1357)

3 October 2026, the Layer 7 author, worktree `l7pwr` on branch `fnd/l7pwr` from the integration candidate `fnd/l4e9` at
`2c240414`. Prototype design, desk arithmetic: nothing has been bought, built, powered or measured. This folder carries the three
Layer 7 items of L4-E9's prototype qualification route (`records/l4e9/L4-POWER-ARCHITECTURE.md` section 5d) that do not depend on
the solar guard's open round: the five IP68 fans selected (D-18 settled by the session; register rows E11-35 / R-179, R-142,
R-150), the T-H1 mock-up specified with its complete bill, and the dock lead's pulse and duty capability on published relations
with the question to Preci-Dip drafted. No L4 record, generator, CAD file, `pcb_interfaces.yaml` or `HW-FW-CONTRACT.md` is
edited: what those need is a FINDING naming its row (`L7-FANS-AND-TH1.md` section 5). Layer 6 (`records/l6pwr`, not in this
base) integrates the fans' identity rows.

| File | What it is |
|---|---|
| `L7-FANS-AND-TH1.md` | The one page: the sites as drawn and the supplies; the candidates row by row (MAKER) and the judgement; the selection per site with its authority fields and alternative; everything the picks change downstream (the dock feed's current, the firmware stagger, the layout footprint, the mounting); the T-H1 mock-up in short; the dock lead's pulse capability; the findings for other layers; the Layer 7 criteria moved; decisions; assumptions |
| `T-H1-MOCKUP-SPEC.md` | One page for the owner: the specimen and what transfers, the bill with every price read and dated (or NOT READ) and the totals per currency, the points, heaters and pass lines restated from the procedure |
| `l7pwr_fans_th1.py` | The script, run from the repository root: `python3 v2/docs/records/l7pwr/l7pwr_fans_th1.py` (the committed output is regenerated only through `_bin/regen_out.py`). It pins 24 inputs by sha256, reads every maker row from the pinned document (pdftotext) or the transcription, judges the candidates, computes the downstream currents and heat, the mounting clearances, the bill's totals, the heater settings' check and the dock lead's fusing relations, and prints the predicates the test reads |
| `l7pwr_fans_th1.out` | Its output, committed: section 0 the pins, 1 the sites, 2 the candidates and the selection, 3 downstream, 4 mounting, 5 the bill, 6 the specimen and the pass lines, 7 the dock lead, 8 the predicates |
| `inputs/prices-2026-10-03.json` | The makers' and sellers' pages read for the bill (Peli, Pico, Kiwi Electronics, reichelt, Metaalshopper, Rapid), each with its URL, figures and availability as printed |
| `inputs/findchips-fans-heaters-2026-10-03.json` | The FindChips aggregator rows for the fans and the heaters (distributor, stock, order code, price ladder), kept fields only; indicators, never quotes |
| `inputs/sunon-gf60151b6-spec-reading-2026-10-03.md` | Sunon's GF60151B6 specification for approval as a distributor hosts it: read for the GF60151 family's range, temperature and life; not filed under v2/vendor (not the maker's site) |
| `inputs/ecss-q-st-30-11c-rev2-wires-annex-c.md` | The project's transcription of ECSS-Q-ST-30-11C Rev.2 clause 6.32.4 and Annex C's AWG 24 rows (the free standard, not redistributed) |
| `inputs/fusing-current-sources-2026-10-03.md` | The published Onderdonk and Preece relations with their two public sources |
| `clarification/preci-dip-813.txt` | The question to Preci-Dip on the 813 contact's current-time capability (the hard short's 566 A for 4.5 us, the eFuse's retry duty, the resistance criterion), drafted for the owner to send; nothing sent |
| `../../../vendor/fans/`, `../../../vendor/cm5/rpi-cm5-cooler-product-brief-2024-12.pdf`, `../../../vendor/precidip/precidip-catalog-slc-2018-03-20.pdf` | The makers' documents filed (Sunon's IP56/68 brochure, Same Sky's CFM-60BG68 sheet, Sanyo Denki's pages transcribed, Raspberry Pi's cooler brief, Preci-Dip's SLC catalogue), registered in `v2/vendor/sources.txt` and `v2/vendor/SOURCES.yaml` (`documents_filed_l7pwr`) |
| `v2/docs/parts/PROCUREMENT.md` section 8 | The picks and the T-H1 set with their dated readings, for Layer 6 |

The predicates are held by `v2/ecad/tools/tests/test_l7pwr.py`: `env -C v2/ecad/tools/tests python3 run.py test_l7pwr test_public_hygiene`.

**Round 2 (3 October 2026, set 28 finding F-14; branch `fnd/l7pwr2` from `5515ecc0`):** the script read VSYS_E's loads as L4-E11 first drafted them and refused once L4-E11 section 18 rewrote the auxiliary domain (U22 and +12V_FAN). It now parses the draft with `ast`, reads L4-E11's section 18 figures and record l8r2's cooler step-up row, and restates the budget (`L7-FANS-AND-TH1.md` section 11, the output's section 8 lists every figure that moved against round 1's output at `2087060b`). D-18's settlement and the T-H1 bill hold.
