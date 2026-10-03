# l6pwr: the component identities of the parts Layer 4 selected for the power design (Layer 6 record, MESHSAT-1357)

Prototype design: nothing is bought, built, powered or measured. The owner's instruction of 2 October 2026 asks Layer 6 for
"component selections and alternatives, exact parts/packages, applicable ratings, derating, source evidence and qualification
obligations". The parts here were SELECTED BY LAYER 4 (L4-E5 to L4-E11) and exist only in release-guarded drafts on no committed
netlist; this record records and sources them and reselects nothing. A mismatch is a FINDING with the Layer 4 row it affects (eleven
of them, L6P-F01 to L6P-F11, in the output's section 4). No generator, Layer 4 record, `pcb_interfaces.yaml` or `HW-FW-CONTRACT.md`
is edited. Based on the integration candidate `fnd/l4e9` at `2c240414`.

| File | What it is |
|---|---|
| `L6-POWER-PARTS.md` | The page: the parts table in short (MPN, package, grade, document, code, price, alternative, obligation), the findings, the Layer 6 criteria moved, the open items |
| `l6pwr_parts.py` | The script, run from the repository root: `python3 v2/docs/records/l6pwr/l6pwr_parts.py > v2/docs/records/l6pwr/l6pwr_parts.out` (regenerate only through `_bin/regen_out.py`). Section 0 pins every input (the Layer 4 pages and drafts it reads, the three catalogue readings, the seventeen makers' documents, the ten held-back ones by the sha256 their Layer 4 record pinned). It reads every cited page itself (pdftotext through `part_identities.page_text`), applies rule D-2 to every PRINTED binding, judges every grade against `pcb_envelope.yaml`, and refuses (exit 4) when a cited page does not print what the record says. `--identities` renders the block for `pcb_part_identities.yaml` |
| `l6pwr_parts.out` | Its output, committed: the pins, the envelope, 28 part blocks, the catalogue table, the findings, the criteria |
| `fetch_held_back.py` | Fetches the ten held-back sheets (TI BQ25730, TPS1663, TPS4811-Q1, CSD19536KTT, INA169, TPS3701; Nexperia BUK6Y10-30P; Diodes DS13012; Vishay 30100 as LCSC's copy; Saft MP 176065 xtd) into the ignored `held/` folders and checks the sha256 pins; never run by a test. Every one fetched and matching on 3 October 2026 |
| `read_catalogue.py` | Takes the three public catalogue readings in `inputs/`: LCSC's product detail for 32 codes, JLCPCB's parts search for 8 keywords, Samsung's specification pages for the three CL parts (the properties they print; the pages are date-stamped and read 'All rights reserved', so the excerpt is the reading) |
| `inputs/lcsc-2026-10-02.json`, `inputs/jlc-search-2026-10-02.json`, `inputs/samsung-spec-pages-2026-10-02.json` | The readings of 2 October 2026, 23:20 UTC |
| `apply_part_identities_block.py` | Puts the block `drafted_identities_l4_power` (rendered by the script) into `v2/ecad/tools/pcb_part_identities.yaml` outside `selections:`, or removes it; refuses a second application; re-parses the file and asserts `selections` and `counts` unchanged. APPLIED on this branch. `build_table.py` (stream w5identc) does not carry the block: after a regeneration of the table, run this script again (open item below) |
| `README.md` | This list |

Also on this branch, outside this folder: `v2/ecad/tools/pcb_part_identities.yaml` (the block), `v2/vendor/SOURCES.yaml` (sixteen
`parts:` entries added before `owed:`, an `update_l6pwr_2026_10_03` block on `pack-cells`, one owed item), `v2/docs/parts/PROCUREMENT.md`
(section 8), `v2/vendor/sources.txt` and `v2/vendor/vendor-status.txt` (the held files' lines), `v2/ecad/tools/tests/test_l6pwr.py`.

The predicates are held by `v2/ecad/tools/tests/test_l6pwr.py` (10 tests). Run `env -C v2/ecad/tools/tests python3 run.py test_l6pwr
test_part_identities test_public_hygiene`; on 3 October 2026 the three files read 39 passed, 0 failed, 2 skipped (Uniroyal's held sheet,
as before).

## Open items (concrete next action each)

1. **L6P-F01, the R221 collision** between L4-E8's ballasts and L4-E11's eFuse resistor: L4-E11's author renumbers R221 in
   `apply_gen_sch_a_charger.py` and R-181's text (or the coordinator decides the order and the renumbering at integration).
2. **L6P-F04, R97's tolerance:** L4-E7 states the tolerance its 18 V INP line assumes; at 1 percent the line is exceeded by 0.186 V at the
   modelled peak, at 0.1 percent it holds (the arithmetic is in the output).
3. **L6P-F10, the rating basis** for the guard's 80.6 V excursion (the recommended 80 V row against the 100 V absolute maximum less 10
   percent): L4-E7 states it.
4. **The identity block after a table regeneration:** `build_table.py` rewrites `pcb_part_identities.yaml` from its DECISIONS and would drop
   the block; `apply_part_identities_block.py --write` puts it back (test_l6pwr fails until it does, by design).
5. **DECODED schemes** for Milliohm's HoJLR, Vishay's WSL and Diodes' B5xxC-13-F numbering in `part_identities.SCHEMES` (L6P-F03): a tools
   change that would bind six identities DECODED.
6. **Documents owed** (SOURCES.yaml's owed list): the ZK sheet's URL, Samsung's MLCC catalogue (the temperature range), Milliohm's HoLLR2512
   sheet (C2985708), Nexperia's packing legend (the PX suffix).
7. **The guard's rows are PROVISIONAL** (U21, Q12, Q13, D4, D11, the Samsung ceramics, R97, R87): L4-E7's round 3 on the solar guard may
   change the capacitor set; when it lands, the affected rows are re-read against its draft and the output regenerated.
