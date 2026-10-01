# l4e10: the cell and thermal design of the battery path (layer 4 task L4-E10, MESHSAT-1357, FEA-008)

Prototype design, desk arithmetic. This folder carries FEA-008, the open Layer 4 obligation of DR-06: the present cell
and thermal design against the temperature requirements with the pack fitted, mode by mode (LO-01a to LO-01h of
`v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md` section 2.5), worked in the order of the owner's refinement of
2 October 2026: a feasibility screen of every condition, the thermal measures only where a route exists, the cells
alongside, the simplest defensible selection, and the conflict with at most three options where none qualifies.

| File | What it is |
|---|---|
| `L4E10-CELL-THERMAL.md` | The page: the collisions restated, the feasibility screen of every condition, the thermal routes bounded (LO-01a's three thresholds, LO-01g's self-heating candidate, E5's cycle, powered cooling), the cell comparison with the protection redesign as its entry cost, the decision per row with its complete acceptance, why no owner decision is forced and the remaining gap, F2 and PWR-F12, the downstream items, check 1's items mapped |
| `l4e10_cell_thermal.py` | The script, run from the repository root: `python3 v2/docs/records/l4e10/l4e10_cell_thermal.py > v2/docs/records/l4e10/l4e10_cell_thermal.out`. Section 0 reproduces `../rv-pwr/pwr_budget.out` and `.json`, `../hc2/pwr_red2.out` and `../hc2/hotstop_bounds.out` byte for byte and imports the two models unchanged; 31 inputs are pinned by sha256; the makers' clauses are read back from the PDFs with pdftotext. A few seconds |
| `l4e10_cell_thermal.out` | Its output, committed |
| `fetch_held_back.py` | Fetches the four cell specifications read but held back by their terms (Samsung INR18650-30Q: the 2020 V1.0, the 2015 Version 1.0 and the 2024 draft; LG INR18650HG2) into the ignored `v2/vendor/battery/held/`, checked by sha256; never run by a test |
| `inputs/` | The readings of 1 October 2026: the HL18650V product page's specification lines (`topwell-hl18650v-page-2026-10-01.json`) and the distributor and marketplace prices (`prices-2026-10-01.json`), each with its page's sha256 |
| `clarification/` | Drafts for the owner to send (the session contacts no outside party): Topwell for the HL18650V's signed specification, Eaton for F2's storage line and its behaviour above +60 C |
| `checks/astra-check-l4e10-1.md` | The engineering collaborator's one check at `9fe3b632` (NOT YET: R1, LO-01a's closure condition incomplete; R2, the screen missed E3-P, E4-P, P13, E3-A's and E3-L's sequences and E3-H; R3, thermal rejections not bounded, the whole-kit heating figure presented as the pack's; R4, a missing cell rating presented as a contradiction between owner requirements; R5, option B's protection not coordinated; minors M1 to M3), filed by the coordinator's instruction byte for byte from its result, `accepted: no`. The page's section 12 maps each item to its change |
| `README.md` | This list |

Filed with this task: `v2/vendor/battery/molicel-inr18650-p28a-v1.pdf` (the maker's own public sheet) and five lines of
`v2/vendor/sources.txt`. No generator, BOM, registry or Layer 3 file is changed, so there is no draft apply script.
The predicates are held by `v2/ecad/tools/tests/test_l4e10.py`; run them with
`env -C v2/ecad/tools/tests python3 run.py test_l4e10 test_public_hygiene`.
