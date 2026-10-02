# l4e12: the kit's electronics against the inside air at the margins (layer 4 task L4-E12)

MESHSAT-1478 under MESHSAT-1357, 2 October 2026. Prototype design, desk arithmetic. This folder answers U-02 of L4-E9's gate:
at the enclosure conductance LO-01a already needs, the kit's own heat puts the inside air past the +70 C parts in E3-O
(D-02a's +55 C operating margin) and in E5's +60 C dwell, inside the sealed Peli 1450 (no vent, appendix 32.53). It reads the
acceptance first, screens every fitted part on every board and every bought module, compares three complete approaches and
selects the simplest defensible one, the margin hold, CONDITIONAL on T-H1 and a few named items.

| File | What it is |
|---|---|
| `L4E12-ELECTRONICS-THERMAL.md` | The one page: the acceptance quoted and what it requires; the thermal state at the margins; the screen; the three approaches; the selection with its margins; what stays conditional and what could overturn it; the owner-question test; the downstream items with owner by layer and acceptance; the session's decisions |
| `l4e12_thermal.py` | The script, run from the repository root: `python3 v2/docs/records/l4e12/l4e12_thermal.py > v2/docs/records/l4e12/l4e12_thermal.out`. It pins 62 inputs by sha256, reproduces `../rv-pwr/pwr_budget.out` and `.json` and `../hc2/pwr_red2.out` byte for byte before any figure, imports `v2/docs/parts/grade_check.py`'s build (which writes nothing) for the parts list, and reads every maker's figure back from its document with its page. A few seconds |
| `l4e12_thermal.out` | Its output, committed; section 8 prints the predicates |
| `fetch_held_back.py` | Fetches TI's TLV755P sheet (read, not filed: its IMPORTANT NOTICE read conservatively) into the ignored `v2/vendor/ti/held/`, checked by sha256; never run by a test |
| `clarification/` | Requests drafted for the owner to send (the session contacts no outside party): Pervasive Displays (the e-paper's storage range, needed by the selection), Ground Control, NiceRF, Sensirion and Bulgin (the fallback's evidence) |
| `README.md` | This list |

No generator, BOM, registry, interface or Layer 3 file is changed, and no draft is given: the selection's circuit item (the
SGP41's switch and bus on board E) and the pushbuttons' swap need footprints and a KiCad run, so the page specifies them for
their generator owners. The predicates are held by `v2/ecad/tools/tests/test_l4e12.py`; run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e12 test_public_hygiene`.
