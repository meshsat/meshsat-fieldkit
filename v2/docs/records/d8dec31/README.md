# Records of stream d8dec31: the review of decision 31 (MESHSAT-1357, 28 September 2026)

The review itself is `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` (an AI review, the file name the holds of
boards A, D and E ask for). Everything here is what it was written from, what it hands on, and what was run.

| file | what it is |
|---|---|
| `netread.py` | the S-expression reader of a KiCad netlist the review parsed with (components with their fields and pins, nets with their nodes) |
| `dump_connectors.py`, `readings/connectors-{a,d,e}.txt` | every connector-class part of the three boards, pin by pin, with the other nodes of each net |
| `walk.py`, `readings/walk-{a,d,e}.txt` | every candidate exposed conductor walked from its pin through its series parts |
| `readings/actives.txt` | the integrated circuits, transistors, inductors, relay and crystals of the three boards, by value |
| `make_pin_tables.py`, `readings/pin-tables.md` | the review's connector tables, written from the netlists and the corrected declarations; it stops if a pin carrying a supply or a signal is in no entry |
| `apply_port_declarations.py` | the three board tables corrected and completed (board A's external list; `internal_ports` on A, D and E). The integrator's files |
| `genpatch.py` | what the circuit apply scripts share: an edit with its old text asserted once, the syntax tree read back, a marker against a second run |
| `apply_gen_sch_e_cin.py` | finding E-F1: the LM74700-Q1's input capacitor on DC_F (board E's generator owner) |
| `apply_gen_sch_e_pod.py` | finding E-F3: two 10 uF at the pod header's 3.3 V pin (board E's generator owner) |
| `apply_gen_sch_a_mainpb.py` | finding A-F2: the maker's 5.1 k and 100 nF at the LTC2954's PB pin, the two nodes and the signal class (board A's generator owner) |
| `apply_gen_sch_d_ptt.py` | finding D-F1: 1 k and two BAT46W per push-to-talk line (board D's generator owner) |
| `apply_registry_d31.py` | fourteen open items at the next free S- numbers (the integrator's registry) |
| `apply_holds_review_pin.py` | the review's sha256 and the three netlists it read, into the three holds (the integrator's file); it refuses a netlist the review did not read |
| `readings/test-port-protect-before.txt`, `-after.txt` | `python3 tests/run.py port_protect` on the tool at `73ae2f21` (40 passed, 7 failed) and on the changed tool (48 passed, 0 failed) |
| `readings/trn001-scratch/` | TRN-001's writer run in a scratch copy of the tree with `VERDICT_DIR` set: on the committed declarations of six boards and on the corrected declarations of A, D and E (the verdict files are renamed `.verdict.scratch.json` so nothing reads them as evidence) |

**Not run:** any schematic generator (this host has no KiCad); the full test suite (the KiCad host's). Each circuit
apply script was tested on a copy of its generator: the edit is made, the file parses, the calls it added are in the
syntax tree with the arguments meant, a second run is refused, and the two board E scripts compose in either order.

**Filed under `v2/vendor/` by this stream** (with their lines in `v2/vendor/sources.txt`): the Infineon BSC039N06NS
sheet (Rev.2.4, with a text layer, the distributor's copy) and the TI TPS37 sheet (SNVSBJ1E, the same bytes r4a's
draft cited). Their entries in `v2/vendor/SOURCES.yaml` are owed to the integrator.

**Commits of this stream** are on branch `fnd/d8dec31`, from `73ae2f21`.
