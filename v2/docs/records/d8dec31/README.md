# Records of stream d8dec31: the review of decision 31 (MESHSAT-1357, 28 September 2026)

The review itself is `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` (an AI review, the file name the holds of
boards A, D and E ask for). Everything here is what it was written from, what it hands on, and what was run.

**Where it comes from, and what it closes.** The independent review of handover H3
(`v2/docs/reviews/2026-09-27-h3-independent-review.md`) found **H3-02**: TRN-001 on board A judged nothing of
VIN_RAW's entry, because `boards/a.json` named J_DOCK pins 1 and 2, ground since SC-55. `v2/docs/handover/RELEASE-H3.md`
carries it as **erratum f**; the requirements registry as open item **S-88**, whose condition is the declaration
corrected, the checker refusing a declared port that names no conductor and reporting a connector pin no entry covers,
a regression that moving or omitting a declared entry demands reconciliation and never shrinks the coverage in silence,
and TRN-001 re-taken on board A. This stream delivers the first three (the declaration by `apply_port_declarations.py`,
the checker in `port_protect.py` commits `d3125b1e` and the reviewed set of the second pass, the regression in
`tests/test_port_protect.py` and `regress_reclassify.py`); the re-take is the integrator's on the KiCad host, and
**S-88 closes only by `apply_registry_d31.py --close-s88 <commit>` once that reading is in the tree**. The fresh check
of this branch at `f8e61f05` (`v2/docs/records/int7/checks/d8dec31-check-1.md`, an AI review) is answered by the second
pass: its blocking item B1 (the third shape of moving an entry, into `internal_ports`) and its ten minor items.

| file | what it is |
|---|---|
| `netread.py` | the S-expression reader of a KiCad netlist the review parsed with (components with their fields and pins, nets with their nodes) |
| `dump_connectors.py`, `readings/connectors-{a,d,e}.txt` | every connector-class part of the three boards, pin by pin, with the other nodes of each net |
| `walk.py`, `readings/walk-{a,d,e}.txt` | every candidate exposed conductor walked from its pin through its series parts |
| `readings/actives.txt` | the integrated circuits, transistors, inductors, relay and crystals of the three boards, by value |
| `make_pin_tables.py`, `readings/pin-tables.md` | the review's connector tables, written from the netlists and the corrected declarations; it stops, keyed by pin, if a pin carrying a supply or a signal is in no entry; its class column says "protection claimed off this board, not judged here" for the 13 off_board entries the review could not judge, and "read on board C's netlist" for J_MAINSW |
| `ledger_pages.py`, `readings/ledger-pages.txt` | the review's ledger (section 8) re-read against the held PDFs: every verbatim quote and decimal figure of each row looked for on the cited pages with pdftotext (elisions honoured); the rows it flags were then opened by hand (quotes split across layout columns, "100%avalanchetested", the image-only TECH PUBLIC page): one page citation was wrong (LM74700-Q1, page 5 not 4) and is corrected |
| `apply_port_declarations.py` | the three board tables corrected and completed (board A's external list; `internal_ports` on A, D and E). The integrator's files |
| `make_port_reviews.py`, `v2/ecad/tools/pcb_port_reviews.json` | **the reviewed set**: the external pins this review enumerated from each netlist, pin by pin with the net each carried (22 on A, 8 on D, 5 on E), the review it rests on and the netlist's sha256/16. `port_protect.py` holds every declaration against it and reads INCONCLUSIVE by name for a reviewed pin declared internal, left out, gone or moved to ground, and for a declared external pin no review holds, until the set is changed with its reason and its review (a `changes` entry). The file is committed on this branch; the script's `--check` confirms it is what the corrected declarations give |
| `regress_reclassify.py`, `readings/regress-reclassify.txt` | the three shapes of moving an entry (onto ground pins, out of the declaration, into `internal_ports`), the narrowing by pins, the declared zero and the reconciled change, on the three REAL corrected tables in a scratch tree: 21 cases, 0 failed; the checker's counter-example (J_USBW into `internal_ports` on A) reads INCONCLUSIVE of 38 with its three pins named, PASS of 38 only once the reviewed set carries the change |
| `apply_config_inputs_port_reviews.py` | declares `tools/pcb_port_reviews.json` a configuration input of `port_protect.py` in `rules_status.CONFIG_INPUTS` (the integrator's file), so a change to the reviewed set makes TRN-001's readings stale as a change to a board table does |
| `genpatch.py` | what the circuit apply scripts share: an edit with its old text asserted once, the syntax tree read back, a marker against a second run |
| `apply_gen_sch_e_cin.py` | finding E-F1: the LM74700-Q1's input capacitor on DC_F (board E's generator owner); the code C382212 is board A's C207's, said so |
| `apply_gen_sch_e_pod.py` | finding E-F3 (a conservative bound): two 10 uF at the pod header's 3.3 V pin (board E's generator owner) |
| `apply_gen_sch_a_mainpb.py` | finding A-F2: the maker's 5.1 k and 100 nF at the LTC2954's PB pin, the two nodes and the signal class (board A's generator owner); its docstring names the contract change below |
| `apply_interfaces_mainsw.py` | IF-AC-MAINSW's board A end after A-F2 (pin 1 on MAIN_PB_LEAD), the integrator's file; it refuses while board A's netlist still has J_MAINSW.1 on MAIN_PB, so it runs after the generator |
| `apply_gen_sch_d_ptt.py` | finding D-F1: 1 k and two BAT46W per push-to-talk line (board D's generator owner) |
| `apply_registry_d31.py` | stage 1: fourteen open items at the next free S- numbers at apply time, each linked from the record(s) whose verdict it can move (REQ-029, REQ-015, REQ-009, REQ-041, REQ-058, REQ-007, CHO-003), the mapping printed and written under the given root as `ids-registry.json`; stage 2 `--close-s88 <commit>`: closes S-88 and refuses until the re-taken reading of TRN-001 on board A is in the tree (PASS, the declared phase's netlist, the changed tool by sha and by its syntax tree, 0 disagreements) |
| `apply_holds_review_pin.py` | the review's sha256 and the three netlists it read, into the three holds (the integrator's file); it refuses a netlist the review did not read |
| `apply_sources_d31.py` | the `v2/vendor/SOURCES.yaml` entries of the two sheets this stream filed (the integrator's file) |
| `run_scratch_sequence.sh`, `readings/apply-scratch.txt` | the integrator's whole sequence rehearsed on a scratch tree of main plus this branch: every script in order, the validator (0 errors), the regression, every refusal of the closure stage and the closure itself (0 errors after it) |
| `readings/test-port-protect-before.txt`, `-after.txt` | `python3 tests/run.py port_protect` on the tool at `73ae2f21` (40 passed, 7 failed) and on the changed tool (61 passed, 0 failed) |
| `readings/trn001-scratch/` | TRN-001's writer run in a scratch copy of the tree with `VERDICT_DIR` set: on the committed declarations of six boards and on the corrected declarations of A, D and E (the verdict files are renamed `.verdict.scratch.json` so nothing reads them as evidence); the first pass's readings, before the reviewed set |

**The integrator's order** (each on the tree after this branch is merged; each refuses a second run):
1. `apply_port_declarations.py <root>` (the three tables), then `make_port_reviews.py <root> --check` (must print "exactly what this script would write").
2. `apply_config_inputs_port_reviews.py <root>` (rules_status.py).
3. `apply_registry_d31.py <root>` (the fourteen items, linked), then `rules_lib.py requirements` (0 errors on the rehearsal).
4. `apply_sources_d31.py <root>` (SOURCES.yaml); `apply_holds_review_pin.py <root>` (the holds; the review's sha is taken from the tree at apply time).
5. On the KiCad host: TRN-001 re-taken on board A (and D and E) with the merged tool and the corrected tables; commit the reading. Then `apply_registry_d31.py <root> --close-s88 <that commit>`, then `rules_lib.py requirements`.
6. In the next circuit round, for the generator owners: `apply_gen_sch_e_cin.py`, `apply_gen_sch_e_pod.py`, `apply_gen_sch_a_mainpb.py`, `apply_gen_sch_d_ptt.py`; after board A's generator has run, `apply_interfaces_mainsw.py <root>`. Every one of them moves its board's netlist, after which the holds' pin reads "re-review it" and the reviewed set's `netlist_sha256_16` is a note, never a refusal.

**Not run:** any schematic generator (this host has no KiCad); the full test suite (the KiCad host's). Each circuit
apply script was tested on a copy of its generator: the edit is made, the file parses, the calls it added are in the
syntax tree with the arguments meant, a second run is refused, and the two board E scripts compose in either order.

**Filed under `v2/vendor/` by this stream** (with their lines in `v2/vendor/sources.txt`): the Infineon BSC039N06NS
sheet (Rev.2.4, with a text layer, the distributor's copy) and the TI TPS37 sheet (SNVSBJ1E, the same bytes r4a's
draft cited). Their entries in `v2/vendor/SOURCES.yaml` are `apply_sources_d31.py`.

**Commits of this stream** are on branch `fnd/d8dec31`, from `73ae2f21`.
