# Integration set 10: closure record (MESHSAT-1357, 29 September 2026)

Branch `fnd/int11` onto main `c5f93464`; the final candidate is the commit that carries this file. Prototype design:
nothing here has been built, ordered or measured. The checks named below are AI reviews, not qualified reviews.

## What the set changes, by class

| Class | Change | Commits |
|---|---|---|
| Tools | stream d6dec: decision 42's decoupling rules as one library, the fan selection, the escape cost that shuts an opening while its costed part stays, far-side seats priced at their via pair's pitch, `intent.bypass` taking a class and a basis and `intent.write` refusing an entry without them (DECOUPLING.md 8.1 T1 to T6, T9, T10); the EMC sheet tool knows the BQ25731 | `32adc424`, `36ac4bef` |
| Registry | DEC-001's text, sources and coverage row from DECOUPLING.md 8.2 (T7) with the pages (T8); S-117 opened (board A's charger frequency against its 3.3 uH inductor) | `682c68ac`, `36ac4bef` |
| Declarations and sheets | set 9's carried M2 (IF-AB-POWER's +5V_DEV row cites `gen_sch_a.py:140`), M10 (U3 in board A's EMC sheet) and M11 (U41's row, the sheet's paths no longer count converters) | `36ac4bef` |
| Regeneration | the decoupling tools sit inside every generator's import closure, so every netlist's provenance named a generator the tree no longer had and check_contracts refused all six ("UNKNOWN GENERATOR"). All six schematics regenerated on the KiCad box (`box_regen_all.sh`): schematic, netlist and intent identical apart from their export date, BOMs identical, the provenance naming the new generator; check_contracts PASS of 99 on the regenerated set | `13b5352b`, `d41f85ec` |
| Pins and bindings | every board's netlist pins in the holds, the reliability list and the port reviews, 25 registry records and the six layout constraint sheets re-bound, each after a proof that only the export's date and source lines differ; CON-010 and REQ-044 to the final page | `958a7de7`, `559a072d` |
| Evidence | two re-takes (the first found the netlists refused; the second at `958a7de7`: 73 steps, 0 errors, no verdict moved); 34 layout-entry reasons, as on main; DEC-001 reads INCONCLUSIVE on the six boards ("taken under a different version of DEC-001") until each board's next placement under its new text, which moves the open-pairs table from 200 to 195 PASS and 40 to 39 FAIL (board A's DEC-001 FAIL was a reading under the old rule version, and it awaits the same re-read as the others) | `8cb89eaf`, `559a072d` |
| Records | stream energy's section 9 (the reference analysis the owner accepted on 29 September) and the rebuilt diagrams; the records index | `5329ad2e`, `532807f0` |

## Gates

| Gate | Result |
|---|---|
| Validators on the candidate | rules_lib 59 rules and 144 records, 0 errors; every `--check` exit 0; constraints_bound PASS |
| Isolated clone at `559a072d` with only its archive (935 files) | status 0 lines after status x3 and render x2; every check exit 0 |
| Full suite on the box at `559a072d` | recorded in `v2/docs/EXECUTION-PLAN.md`'s milestone entry for set 10 |
| Fresh AI check | owed when a worker slot frees (the owner assigned both slots to Option A(i) on 29 September) |

## What it does not claim

DEC-001 is not passed anywhere: its readings await each board's next placement. No layer closes.

## Carried

The sheet script `apply_sheets_int11.py` writes the sheets before its final binding check, so its first run wrote them and then
refused on `calc/rail_widths.out`; the second run regenerated that file and found nothing more to move. The result is the
committed state; the order is to be fixed in its successor. Board E's regeneration reports 18 pins on a pad its land does not
carry, as the committed board did (parity PARITY_AFTER_NOISE, BOM identical).
