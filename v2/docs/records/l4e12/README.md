# l4e12: the kit's electronics against the inside air at the margins (layer 4 task L4-E12)

MESHSAT-1478 under MESHSAT-1357, 2 October 2026, revised the same day after the collaborator's focused check and again after
its targeted recheck. Prototype design, desk arithmetic. This folder answers U-02 of L4-E9's gate:
at the enclosure conductance LO-01a already needs, the kit's own heat puts the inside air past the +70 C parts in E3-O
(D-02a's +55 C operating margin) and in E5's +60 C dwell, inside the sealed Peli 1450 (no vent, appendix 32.53). It reads the
acceptance first, screens every fitted part on every board and every bought module, compares three complete approaches and
selects a route that keeps E3-O exactly as TEST-PLAN states it and lets the hold act in E5 only, CONDITIONAL on T-H1 at 2.159
W/K and named items. Every judged limit names its rating category and an absolute rating clears nothing on its own. The
battery-bay SGP41 cannot be held inside its maker's conditions in the envelope at any location (lid closed at the hot end, and
in storage), so the page raises one owner question for it (CFL-002, three options). Its section 13 answers the owner's
questions on U-02: what supports 2.159 W/K, the configuration it assumes, the fans in the energy budget, T-H1's owner and
method, and what a failed reading changes with its fallbacks; section 14 bounds the conductance from first principles
and finds that T-H1 decides U-02 (E3-O short by 0.212 W/K with every session measure), with the smallest experiment;
section 15 compares three heat-rejection approaches for the approved profile at +40 C (none reaches it on bounded evidence);
section 16 reconciles T-H1's line with the requirements (the owner's amendment of 2 October 2026, 14:20): the heat counted once,
the nodes and every limit with its reference, a +55 C inside-air limit for the heat stage at +40 C (1.806 W/K), the bench's
translation to +40 C, what one point closes and what remains, and the revised procedure.

| File | What it is |
|---|---|
| `L4E12-ELECTRONICS-THERMAL.md` | The one page: the acceptance quoted and what it requires; the thermal state at the margins; the screen; the three approaches; the selection with its margins; what stays conditional and what could overturn it; the owner-question test; the downstream items with owner by layer and acceptance; the session's decisions |
| `l4e12_thermal.py` | The script, run from the repository root: `python3 v2/docs/records/l4e12/l4e12_thermal.py > v2/docs/records/l4e12/l4e12_thermal.out`. It pins 69 inputs by sha256, reproduces `../rv-pwr/pwr_budget.out` and `.json` and `../hc2/pwr_red2.out` byte for byte before any figure, imports `v2/docs/parts/grade_check.py`'s build (which writes nothing) for the parts list, and reads every maker's figure back from its document with its page. About fifteen seconds |
| `l4e12_thermal.out` | Its output, committed; section 8 is U-02 in depth (the dependency round), section 9 the conservative lower bound and U-02's class, section 10 the heat-rejection approaches, section 11 the thermal reconciliation, section 12 prints the predicates |
| `T-H1-PROCEDURE-DRAFT.md` | The draft test procedure for T-H1, the empty-case heat balance, revised for the reconciliation: authorisation (the owner's) kept apart from acceptance (the coordinator's check); the configuration, each point at its mode's heat with P = the heaters + the fans, the heaters' distribution, the channels, the run order and duration, the endpoint (drift or a first-order fit), pass, fail or inconclusive per point, and the record to keep; its figures are the `.out`'s sections 8 and 11 |
| `fetch_held_back.py` | Fetches TI's TLV755P sheet (read, not filed: its IMPORTANT NOTICE read conservatively) into the ignored `v2/vendor/ti/held/`, and Rittal's page of its enclosure climate-control calculation basis (cited in section 16, held back by its copyright) into the ignored `v2/vendor/rittal/held/`, each checked by sha256; never run by a test |
| `clarification/` | Requests drafted for the owner to send (the session contacts no outside party): Pervasive Displays (the e-paper's storage range) and Sensirion (the SGP41's short-term storage duration, storage and operation outside its Table 4), both needed by the route; Ground Control, NiceRF and Bulgin (the fallback's evidence) |
| `checks/astra-check-l4e12-1.md` | The engineering collaborator's focused check at `bcd23532` (NOT YET: B1, the hold changed E3-O's configuration without authority; B2, absolute maxima used as survival statements; B3, the SGP41 switched off too late; the eleven unrated lines; minors on W4's high case and on the ATP19 and e-paper), filed by the coordinator's instruction byte for byte from its result, `accepted: no`. The page's section 12 maps each item to its change |
| `checks/astra-check-l4e12-2.md` | The collaborator's targeted recheck at `39fe74c4` (NOT YET: B2, the SGP41 judged on Table 5's absolute +55 C and absolute-only rows such as CSD17577Q5A's +150 C given an ordinary NOT REACHED; B3, the BME688's +-0.5 C is typical, and the SGP41's restart threshold lay under the bay air the record predicts inside the envelope; minors on the exclusive owner-question condition and on rounding), filed byte for byte from its result, `accepted: no`. The page's section 12 maps each item to its change |
| `checks/check-l4e12-3.md` | Claude's (the coordinator's) closing check at `a86be47b`: the output reproduced, the conductance arithmetic and E3-O's configuration confirmed, the SGP41's Table 4 and Table 5 read on the sheet; the record accepted, U-02 CONDITIONAL, CFL-002 a genuine owner question; not a model review and not an Astra check |
| `checks/check-l4e12-4.md` | Claude's check of the U-02 round at `625e7222`, `accepted: yes`: the 2.159 W/K basis and its sensitivity, the fans read in the power budget, the fans-off temperatures and the deeper hold recomputed; T-H1's procedure drafted, the measurement and D-18's pick open, a session fallback documented |
| `checks/check-l4e12-5.md` | Claude's check of the U-02 bound at `aab69775`, `accepted: yes`: the conservative conductance bound reproduced in a separate series model (0.569 to 0.596 against 0.566 to 0.607 W/K lid open); T-H1 decides, U-02 a closure condition, one bounded experiment with acceptance bands |
| `checks/check-l4e12-6.md` | Claude's check of the heat-rejection comparison at `8dfaa311`, `accepted: yes`: the needs (1.447 W/K at +40 C, 1.507 to 1.832 W/K charging) recomputed, route (b)'s plate temperature in a separate estimate; no approach restores the profile on the bound (1.384 W/K combined, 1.252 W short); U-02 a closure condition decided by one bench point (1.509 / 1.575 / 1.930 W/K) |
| `README.md` | This list |

No generator, BOM, registry, interface or Layer 3 file is changed, and no draft is given: the route's circuit items (the
SGP41's switch and bus on board E, the two 3.3 V regulators) and the pushbuttons' swap need footprints and a KiCad run, so the
page specifies them for their generator owners. The predicates are held by `v2/ecad/tools/tests/test_l4e12.py`; run it with
`env -C v2/ecad/tools/tests python3 run.py test_l4e12 test_public_hygiene`.
