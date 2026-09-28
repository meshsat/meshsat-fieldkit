# Integration set 9: the apply scripts that land S-99's shared-file texts (stream s99reg)

MESHSAT-1357, 29 September 2026, branch `fnd/s99reg` from `605ece61` (set 9's line: main `20afa7a4` plus `fnd/s99a`).
**AI engineering work**, not a qualified review. Prototype design: nothing built, ordered or measured. This stream edits
no shared file: the integrator runs the scripts below. Every script takes `--root <tree>` (default: the repository it
is in), `--check` (build and assert everything, write nothing), asserts each old text, asserts the new text differs,
re-parses what it writes, and refuses a second run by content (no marker files). Helpers: `_int10.py` (its `write`
refuses a path that resolves outside the root or through a link). Sources: `v2/docs/records/s99a/REGISTRY-DRAFT.md`
(supersedes `records/s99/REGISTRY-DRAFT.md` where they differ), `records/s99a/OPEN-ITEM-LAYOUT-A.md`,
`OPEN-ITEM-CODEC-FLOOR.md`, `apply_if_ab_power_dev.py`, `records/s99/checks/check-2-claude.md`, and the check of s99a
(`_scratch/chk-s99a/RESULT.md`: accepted, no blocking item).

## 1. Order, and what each needs in the tree first

Run from anywhere, on the integration tree, in this order (they are independent of each other in content, and each
checks the registry fresh, but this is the order the dry run proved):

| # | Script | Changes | Needs first |
|---|---|---|---|
| 1 | `apply_rebind_generator_a_s99.py` | `pcb_requirements.yaml`: CON-019, CON-018, CFL-014, REQ-077 rebound from `gen_sch_a.py@ebb5c0f250780a48` (set 8) to the tree's, one evidence entry each | `gen_sch_a.py` as s99a left it (sha256/16 `eb2e347e4d371e0f` on this line; any further change must still pass its proof); commit `20afa7a4` in the history |
| 2 | `apply_s99_registry.py` | `pcb_requirements.yaml`: S-99's title re-stated (no disposition; REQ-018 keeps `waits_on: S-99`); S-115 opened (LAYOUT_STAGE, with its reason); S-116 opened; REQ-018, REQ-009, REQ-002 gain `waits_on: S-116` | S-114 the highest S id (no other stream took S-115 or S-116); S-99 as on main (title only) |
| 3 | `apply_decision_55.py` | `pcb_decisions.yaml`: decision 55 appended (SESSION, ruled 2026-09-28); `pcb_requirements.yaml`: CFL-016 rebound to the new `pcb_decisions.yaml` with one evidence entry | decision 54 the last; every record bound to `pcb_decisions.yaml` bound to the tree's version (CFL-016 at `4e1ff91f98e06b72`) |
| 4 | `apply_if_ab_power_s99.py` | `pcb_interfaces.yaml`: s99a's two replacements (the +5V_DEV currents row, IF-AB-WALL's "limit 0.89 A"), imported verbatim from `records/s99a/apply_if_ab_power_dev.py`, plus every generator cite of IF-AB-POWER, IF-AD-HARNESS and IF-AB-WALL read from the generators by `ast`, and IF-AD-HARNESS's power lead naming U23's input +5V_D8IN | s99a's two texts both pending or both applied (run THIS script, not s99a's; if s99a's was run, this one applies the rest: shown on a second overlay, result identical); the generators of A, B and D as on this line |
| 5 | `apply_pages_s99.py` | `HW-FW-CONTRACT.md` FW-A07 and `ASSEMBLY.md`'s Wall USB host row (0.9142 A nominal, and ASSEMBLY's generator cite read by `ast`); `records/s98/README.md` R3 and `records/s98/LAYER-ROWS.md` row 4.10 (the lead drop wording); `pcb_requirements.yaml`: CFL-015 rebound to the new `ASSEMBLY.md` with one evidence entry | `ERRATA-DECISION-31-REVIEW.md` in this folder; the decision 31 review byte-identical to its three pins; CFL-015 bound to the tree's `ASSEMBLY.md` (`0ca504d746b427cb`) |

After them the integrator owes (each script prints its OWED line): `decisions_render.py` (the closed table of
`OWNER-DECISIONS-OPEN.md` gains decision 55's row, so `--check` reads the page stale until it is re-rendered);
`rules_render.py --requirements` (the registry changed); the readings that record `pcb_interfaces.yaml` by sha
(`interfaces.py`, rules_status CONFIG_INPUTS) re-taken; then, from s99a's README section 7, board A's regeneration on
the box and its re-takes (PWR-001, INT-001), after which the records bound to board A's netlist are rebound as set 8
did (`records/int9/apply_rebind_netlists_s98.py`'s pattern; not written here, because the new netlist does not exist
yet), and `rules_lib.py requirements` is read again.

## 2. The dry run (scratch copies only)

`dryrun.py <scratch folder>` builds an overlay of the repository in `_scratch/s99reg/ov`: the seven edited files are
real copies, everything else is a link, `.git` a link so git answers for commits. It runs every script with `--check`,
for real, and a second time, then `rules_lib.py requirements` FROM the overlay (the overlay's registry, decisions,
interfaces, pages and bindings). Transcript: `dryrun.out`. The repository's copies were asserted unchanged
(`repository copies of the edited files unchanged: True`), and `git status` showed only this folder.

Exact last lines (each script: `--check` exit 0, run exit 0, second run exit 2):

- validator before the scripts: exit 1, `rules_lib: 144 requirement record(s), 3 error(s), 1 warning(s)` (CON-019,
  CON-018, CFL-014 and the warning REQ-077: bound to set 8's `gen_sch_a.py`, which s99a changed; script 1 is for them)
- 1: `apply_rebind_generator_a_s99: 4 records rebound (CFL-014, CON-018, CON-019, REQ-077); v2/ecad/tools/gen_sch_a.py ebb5c0f250780a48 -> eb2e347e4d371e0f`;
  second run `apply_rebind_generator_a_s99: REFUSED: already applied (a second run)`
- 2: `apply_s99_registry: S-99's title re-stated (no disposition; REQ-018 still waits on it); S-115 opened (LAYOUT_STAGE); S-116 opened and REQ-018, REQ-009, REQ-002 wait on it`;
  second run `apply_s99_registry: REFUSED: S-115 exists already (a second run)`
- 3: `apply_decision_55: decision 55 appended (SESSION, ruled 2026-09-28); v2/ecad/tools/pcb_decisions.yaml@4e1ff91f98e06b72 -> @ad64649584227d29; 1 record(s) rebound with an evidence entry: CFL-016`;
  second run `apply_decision_55: REFUSED: decision 55 is in the file (a second run)`
- 4: `apply_if_ab_power_s99: 002ae8575028468a -> 363af4715553e42b; 13 replacement(s) (s99a's two included); ...`; second
  run `apply_if_ab_power_s99: REFUSED: already applied (a second run)`. On a second overlay where s99a's own script ran
  first: `11 replacement(s) (s99a's two already applied)`, the same result `363af4715553e42b`, then refused.
- 5: `apply_pages_s99: ... ASSEMBLY.md 0ca504d746b427cb -> ee4eff52fc5df307; rebound: CFL-015; the review of decision 31 left as filed (pinned 094817023210d1b0), ...`;
  second run `apply_pages_s99: REFUSED: already applied (a second run)`
- validator after all five: exit 0, `rules_lib: 144 requirement record(s), 0 error(s), 0 warning(s)` (the one line
  `warn  out/rule-audit is not in this tree` is printed outside the count, as on every worker tree)

The cites read from this line's generators: IF-AB-POWER A `gen_sch_a.py:1051-1052, 1149`, B `gen_sch_b.py:551, 1119,
1210`, slot rails 119, Q28's VBAT load 54, +54V_POE 152 (board B's 85, 111 and 271 asserted current); IF-AD-HARNESS A
`1387, 1598-1599`, D `gen_sch_d.py:259-261`, U23 1387; IF-AB-WALL A `1596-1597`, B `gen_sch_b.py:1637-1638`, the D-12
block `1613-1618` (also ASSEMBLY.md's cite).

## 3. Ids and decisions taken (authority SESSION, under the owner's standing rule of 26 September 2026)

- **Ids:** S-115, S-116 (asserted next free: the highest S id was S-114), decision 55 (asserted next: 54 was the last).
- **The decision 31 review is NOT edited; an erratum is filed** (`ERRATA-DECISION-31-REVIEW.md`). Its sha256 is pinned
  three times in `pcb_board_holds.yaml` and the pinning script refuses to re-pin unless the netlists are the ones the
  review read (board A's has moved and moves again with the regeneration), so editing it would turn three holds'
  review requirement to "re-review it", re-opening an accepted review for a context figure that enters none of its
  conclusions. `apply_pages_s99.py` asserts the review still matches its pins and that the erratum is present.
- **S-116 is linked, not disposed:** REQ-018 (PS-ALLTX, every rail in regulation: the codec's supply is lowest while
  the exciter keys), REQ-009 (both headset jacks key the VHF path and carry audio on their codec channels) and REQ-002
  (a VHF voice exchange over a headset, through the same codec). So it carries no disposition; the draft's word
  DECLARATION is not written. Reverse: drop S-116 from the three `waits_on` lists and give it `disposition:
  DECLARATION` with the draft's reason.
- **S-99's text against the s99a draft:** "not a guaranteed 1 kOhm maximum" is written "no maximum at 1 kOhm is
  published" (the claims screen refuses the word); item (d) gains U41's PFM ripple and load-step overshoot (s99a README
  section 9 item 5 said they sit under (d); SLUSEA4D 9.3.2) and names C231/C232's part C2918511 (25 V; check minor item 10).
- **S-116's text:** "neither code certified today" is written "neither code in the project's parts certification
  today" (the screen), and one sentence names the three records that wait on it.
- **Decision 55:** "board D already certifies" is written "board D already uses as R80 and R81" (the fact the check
  read); authority_why says the mezzanine "keeps" its 6 percent budget, not "improves" (S-116 shows the floor at the
  peak); reversed_by cites the rebased draft actually applied (`records/s99a/apply_d8_split_rebased.py`) and s99a's
  VBAT commit `80ebde44`.
- **Scope added beyond the brief, both needed for the validator's 0 errors or in the same fields:** script 1 (the
  three PASS records bound to set 8's `gen_sch_a.py` were already errors on this line); the cites of IF-AD-HARNESS's D
  end and of IF-AB-WALL's two ends and D-12 block (stale in the same fields the brief named; read by `ast`, not typed).
- **The s98 lead-drop wording** is corrected in place with a sentence saying so (both files are records nobody pins or
  cites by line): 0.2252 V is the contacts alone; 5.63 x (0.004128 + 0.040) = 0.248441 V, 4.87 percent of 5.1 V at 20 C
  copper, 0.252094 V (4.94 percent) at 60 C, computed in the script from ANALYSIS.md's inputs and asserted.

## 4. Not done here, with the next action

- No suite, no KiCad, no `decisions_render.py` or `rules_render.py` run (they are the integrator's, after the scripts).
- Board A's netlist rebind after the box regeneration (next action: the integrator, int9's netlist pattern, once the
  regenerated netlist is committed).
- Left as written, outside this brief: IF-AB-POWER's `converters` text ("a 7.2 to 9.5 A average current limit") and the
  +5V_S2 row's "7.10 to 7.17 A", which are initial-tolerance figures without the assumed 50 K term; other stale
  generator cites in ASSEMBLY.md (for example the heater row's `gen_sch_a.py:1047-1076`); the historical records r4a and
  r4b and the H1 snapshot that quote 0.89 A (listed in the erratum).
- The S-98 sentence of `records/s99/REGISTRY-DRAFT.md` section 4 is not written: S-98 is closed on this line.
