# Regenerating and checking the V2 schematics from this snapshot

MESHSAT-1357, written 27 September 2026 by the handover packer. Prototype design: no V2 board has been fabricated,
ordered, assembled or measured.

**What this page proves.** A recipient holding only this snapshot and the tools named below can (1) confirm that the
files are the ones the manifest names, (2) regenerate every board's schematic and netlist from its generator and get
the committed design back, (3) re-export the readable PDFs and BOMs, (4) run the test suite, and (5) run one
representative calculation, the stored-energy chain. **What it does not prove.** Regeneration parity says the
committed files are what their generators write; it says nothing about whether the circuit is right. A clean ERC, a
passing fixture or a PASS from a checking tool is not a circuit review (the owner's prompt of 27 September 2026,
section 2). The layer status is `LAYER-STATUS.md`'s statement, not this page's.

**How it was verified.** Every command in a grey block of sections 2 to 7 (the ZIP route) was run exactly as written,
as one script cut from this page, between 04:50 and 05:04 UTC on 27 September 2026, on a rented Ubuntu 24.04 host
with 64 cores and KiCad 9.0.9, from a fresh extraction of a build of `H1` at commit `0778e1ab` of the handover branch.
That build's design files, tools and exports are byte for byte those of the H1 source commit named in `SOURCE.txt`:
the commits between them change only the four handover pages and this page. The exports and the six-board
regeneration had also been run once before, on a clean `git archive` of `99cde56b` (the last design change), with
the same results. A content hash or a count quoted below is what those runs printed; the RESULT classes (PARITY,
PARITY_AFTER_NOISE, the causes of the failures) are what to expect on another day. Commands outside the ZIP route
(section 7's repository route, section 8) say how far they were re-run.

**Edition H1.1.** The commands below name `H1`; for H1.1 read `H1.1` wherever a command names the ZIP or its folder.
H1.1's design files, tools and exports are H1's; it adds the candidate patches, the glossary, four filed records,
the case scripts' reference outputs and the packer's new `SOURCE.txt` lines. Sections 1a and 9 are new in H1.1. The
repository holds H1.1 as `v2/release/handover/H1.1.zip` with `H1.1.zip.sha256` and `H1.1.MANIFEST.tsv` beside it (the
packer's `--zip-only` mode), not as an unzipped folder; `unzip` creates the `H1.1/` folder the commands expect.

## 1. Prerequisites (the versions the commands were run with)

**Where the repository is.** The public repository is `https://github.com/meshsat/meshsat-fieldkit` (clone with
`git clone https://github.com/meshsat/meshsat-fieldkit.git`); one file at one commit is
`https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/<commit>/<path>`. The snapshot's `SOURCE.txt` names its
build commit on its `commit:` line and carries a commit timeline: every commit id the handover pages name, with its
date and subject, whether it is in the snapshot's history and whether it was on the public repository when the
snapshot was built. The H1 snapshot was filed by commit `a8652172` (its message, with the suite results of that day,
is filed as `v2/docs/records/handover/a8652172-commit-message.txt`).

| Tool | Version used | Needed for |
|---|---|---|
| Linux | Ubuntu 24.04.5 LTS, x86_64 | everything below; other systems were not tried |
| KiCad | 9.0.9: packages `kicad`, `kicad-symbols`, `kicad-footprints` at `9.0.9~ubuntu24.04.1` | `kicad-cli` exports and ERC; the generators copy symbols from `/usr/share/kicad/symbols` (or `$KICAD_SYMBOLS`) into the schematic, so another KiCad release can change the schematic bytes and the ERC. Parity is promised for 9.0.9 only |
| Python | 3.12.3 (3.10 or later is required by `handover_pack.py`) | the generators use the standard library only (`SOURCE.txt` lists every third-party import of the tools) |
| PyYAML | 6.0.1 | the registries, `energy_chain.py`, `handover_pack.py` |
| Pillow | 10.2.0 | `sch_pages.py` (cuts the schematic into A3 pages) |
| mupdf-tools | 1.23.10 (`mutool`) | `sch_pages.py` |
| poppler-utils | 24.02.0 (`pdftoppm`, `pdftotext`, `pdfinfo`) | `sch_pages.py`, the PDF read-back |
| KiCad's Python module `pcbnew` | 9.0.9 (ships with the `kicad` package) | the board-file fixtures of the test suite; they skip where it is absent |
| unzip, sha256sum, git | UnZip 6.00, coreutils, git 2.43.0 | unpacking and checking; git only for the repository route of section 7 and for section 8 |

Installing these is not covered by the verified commands. The versions of the host used are recorded, as
`dpkg-query` and the tools themselves reported them, in each `v2/release/handover/_generated/<board>/provenance.json`
under `versions`.

## 1a. Restore referenced maker documents (for the checks that need them)

A snapshot bundles the maker documents only where a rule of `pack.yaml` says so; the rest are listed in
`REFERENCED-SOURCES.tsv` with their git blob sha (column 2) and sha256. Three checks need some of them: the
requirements validator and `rules_render.py --requirements --check` need `v2/vendor/st/`'s documents (CON-017), and
the battery packet's `check_manifest.py` needs the 18 vendor documents its manifest cites. From the snapshot's root,
with network access (`REF` is the build commit when the timeline in `SOURCE.txt` marks it public, else the newest
public commit of the timeline; the blob check proves the bytes whichever commit served them):

```
REF=$(sed -n 's/^commit: //p' SOURCE.txt)
fetch() { for p in "$@"; do
  b=$(awk -F'\t' -v p="$p" '$1==p{print $2}' REFERENCED-SOURCES.tsv)
  [ -n "$b" ] || { echo "NOT LISTED $p"; continue; }
  mkdir -p "$(dirname "$p")"
  curl -fsSL -o "$p" "https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/$REF/$p" || { echo "FETCH FAILED $p"; continue; }
  got=$( (printf 'blob %s\0' "$(stat -c%s "$p")"; cat "$p") | sha1sum | cut -d' ' -f1)
  [ "$got" = "$b" ] && echo "OK $p" || echo "DIFFERS $p"
done; }
fetch $(awk -F'\t' 'NR>1 && $1 ~ /^v2\/vendor\/st\//{print $1}' REFERENCED-SOURCES.tsv)
fetch $(python3 v2/docs/review-packets/battery/evidence/check_manifest.py | awk '$1=="MISSING"{print $2}')
python3 v2/docs/review-packets/battery/evidence/check_manifest.py
(cd v2/ecad && python3 tools/rules_lib.py requirements)
python3 v2/ecad/tools/rules_render.py --requirements --check
```

Every fetched line must read `OK`. Expected afterwards: `RELEASE CHECK PASS` from the packet check, `132 requirement
record(s), 0 error(s)` (the 16 warnings stay: closed-by-commit checks and the gitignored readings, section 7) and
`REQUIREMENTS-TRACE.md is current`. The usability check of H1 restored the three ST documents this way (each sha256
matched) and read exactly that from the validator and the renderer; the packet route was not run as one script. The
eight ST files are about 83 MB (RM0433 alone 40.7 MB); fetch only what a check needs. A restored file makes the
snapshot folder differ from its manifest, so run `handover_pack.py verify` before restoring, or on a second copy.

## 2. Check the snapshot

From the directory holding `H1.zip` and `H1.zip.sha256`:

```
export PYTHONDONTWRITEBYTECODE=1
sha256sum -c H1.zip.sha256
unzip -q H1.zip
cd H1
HO="$PWD"
python3 v2/ecad/tools/handover_pack.py verify .
python3 v2/ecad/tools/sch_prov.py read v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net p
```

Expected: `H1.zip: OK`; `handover_pack: verify .: OK` (every file's bytes and sha256 against `MANIFEST.tsv`,
and no file the manifest does not name); `sch_prov: pcb-p-pack.net was written by this tree's own generator
(21640b801014107a)`, which says the netlist's recorded generator inputs (the generator, its imports, the board
table's `gen_env` and 59 land files) are byte-identical to the ones in this snapshot. `PYTHONDONTWRITEBYTECODE=1`
keeps Python's cache files out of the tree, so the second `verify` in section 3 lists only what regeneration wrote.

## 3. Regenerate board P and compare it with the committed design

These are the pipeline's own commands (`v2/ecad/tools/full.sh`, the part before placement, and
`v2/ecad/tools/build_sch.sh`); `PHASE` is the label the committed schematic carries (its title block, comment 1).

```
mkdir -p "$HO/../committed-p"
cp v2/ecad/pcb-p-pack-p2/pcb-p-pack.kicad_sch v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net v2/ecad/pcb-p-pack-p2/out/pcb-p-pack-intent.json v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net.prov.json "$HO/../committed-p/"
cd v2/ecad/pcb-p-pack-p2
python3 ../tools/gen_footprints_idc.py ../meshsat.pretty
PHASE=P4 python3 ../tools/gen_sch_p.py pcb-p-pack.kicad_sch pcb-p-pack
rm -f out/pcb-p-pack.net
bash ../tools/build_sch.sh . pcb-p-pack
VERDICT_DIR="$HO/../verdicts" python3 ../tools/erc_gate.py . pcb-p-pack --run
python3 ../tools/regen_compare.py pair netlist "$HO/../committed-p/pcb-p-pack.net" out/pcb-p-pack.net
python3 ../tools/regen_compare.py pair schematic "$HO/../committed-p/pcb-p-pack.kicad_sch" pcb-p-pack.kicad_sch
python3 ../tools/regen_compare.py pair intent "$HO/../committed-p/pcb-p-pack-intent.json" out/pcb-p-pack-intent.json
python3 ../tools/regen_compare.py pair provenance "$HO/../committed-p/pcb-p-pack.net.prov.json" out/pcb-p-pack.net.prov.json
sha256sum pcb-p-pack.kicad_sch "$HO/../committed-p/pcb-p-pack.kicad_sch"
grep schematic_sha256 out/pcb-p-pack.net.prov.json "$HO/../committed-p/pcb-p-pack.net.prov.json"
python3 ../tools/regen_compare.py pair bom "$HO/v2/release/handover/_generated/pcb-p-pack-p2/NOT_FOR_FAB-pcb-p-pack-bom.csv" out/pcb-p-pack-bom.csv
python3 ../tools/regen_compare.py pair erc "$HO/v2/release/handover/_generated/pcb-p-pack-p2/pcb-p-pack-erc.json" out/pcb-p-pack-erc.json
cd "$HO"
python3 v2/ecad/tools/handover_pack.py verify .
```

Expected, line by line:

- `gen_footprints_idc: 7 footprint(s)` (it rewrites the seven IDC lands in `meshsat.pretty` byte for byte).
- The generator prints `wrote pcb-p-pack.kicad_sch parts: 95 lib symbols: 21`, `lands: 21 footprint(s) judged, 0 pin(s)
  on a pad the land does not carry, 0 land(s) unreadable` and `layout: 2 A3 pages`.
- `build_sch.sh` prints `ERC: violations (...; erc_gate.py decides)`, `netlist: out/pcb-p-pack.net`, the provenance line
  `sch_prov: pcb-p-pack.net written by generator 21640b801014107a (...)`, `sch_pages: 2 x 1 cells, 2 pages kept of 2
  tiles` and `bom: out/pcb-p-pack-bom.csv`.
- `erc_gate`: `no blocking error (123 violations, 0 error(s) allow-listed with a reason, warnings 123)`, 106 of them
  `lib_symbol_issues` and 17 `unconnected_wire_endpoint`, and `verdict: erc_gate PASS of 123`. It writes its verdict
  under `../verdicts`, outside the snapshot.
- netlist `PARITY_AFTER_NOISE` with `content_hash` `efe60479293f0004` on both sides; intent and ERC
  `PARITY_AFTER_NOISE`; BOM `PARITY` (38 grouped rows each side, against the handover's own BOM export of the
  committed schematic).
- The schematic and the provenance depend on the DATE of the run, because the generator writes today's date into the
  title block and every page frame. On the calendar day the committed schematic was written (26 September 2026 for
  this design) the schematic reads `PARITY` and the provenance `PARITY_AFTER_NOISE`. On any later day the schematic
  reads `PARITY_AFTER_NOISE` (N1 once, N2 twice) and the provenance reads `DIFFERENT` with `keys_changed:
  ["schematic_sha256"]` and nothing else: the sidecar names the schematic beside it by the first 32 hex digits of its
  sha256, and that schematic's date changed. The `sha256sum` and `grep` lines show it: each sidecar's
  `schematic_sha256` is the start of its own schematic's sha256 (`47e0bc19e8e18cf0...` committed; the regenerated
  one's on 27 September was `a58d0eecc7abe768...`). That, with the schematics at `PARITY_AFTER_NOISE`, is the
  condition `regen_compare.py`'s docstring sets for the difference to be the date and nothing else.
- The second `verify` reports the regeneration's own writes and nothing else: `out/pcb-p-pack.net` (a few bytes
  longer: the export's own path and time), `out/pcb-p-pack-intent.json` and `out/pcb-p-pack.net.prov.json` (their
  `written` and `taken` times) differ from the manifest, eight new files appear under `out/` (the ERC reports and
  status, `erc_gate.verdict.json`, the BOM and the two PDFs), and on a later day `pcb-p-pack.kicad_sch` differs too:
  12 problems on the commit's day, 13 after it.

**The noise `regen_compare.py` removes, and nothing else** (its docstring is the full list): the dates the generator
writes into the title block and the page frames (N1, N2), the netlist export's own path, time and KiCad build (N3,
N4), the intent's `written` time (N5) and the provenance's `taken` time (N6); the phase label is reported and
normalised (L1, L2). Every other difference reads `DIFFERENT` and exits 1.

## 4. Regenerate every board

The same chain for all six boards with a schematic, driven by `handover_exports.py regen`, which reads each board's
footprint generators and `gen_env` from `v2/ecad/tools/boards/<letter>.json` and sets `PHASE` to the committed
schematic's label. It writes into the tree, so run it on a fresh extraction:

```
cd "$HO/.."
mkdir -p rg
unzip -q H1.zip -d rg
cd rg/H1
python3 v2/ecad/tools/handover_exports.py regen --out "$HO/../rg-out" --letters a,b,c,d,e,p
```

Expected, per board (`rg-out/<letter>/regen.json` holds each command, its exit status and every comparison):

| Board | Phase directory | PHASE used (the committed label) | Board table `phase` | Footprint generators | Netlist content hash | Result |
|---|---|---|---|---|---|---|
| A | `pcb-a-power-a23` | A65 | A32 | `gen_footprints_idc.py` | `66797255f4591a23` | schematic PARITY on the commit's day or PARITY_AFTER_NOISE later (the date), netlist, intent and ERC PARITY_AFTER_NOISE, BOM PARITY, no land changed: the driver prints `PARITY` |
| B | `pcb-b-compute-b19` | B21 | B21 | `gen_footprints_b16.py`, `gen_footprints_idc.py` | `70be33b07a339d6e` | the same |
| C | `pcb-c-display-c8` | C24 | C24 | none | `96c2678f4a3303b8` | the same |
| D | `pcb-d-aprs-d9` | D37P | D12 | `gen_footprints_b16.py`, `gen_footprints_idc.py` | `ecc07f382c735835` | the same |
| E1 | `pcb-e1-dock-e7` | E42P | E17 | `gen_footprints_e.py` | `256cc3f96d41dcab` | the same |
| P | `pcb-p-pack-p2` | P4 | P4 | `gen_footprints_idc.py` | `efe60479293f0004` | the same |

Two things a recipient should know. **The label**: for boards A, D and E1 the committed schematic carries a later
label than the board table's `phase` field; `full.sh` would use the table's value, and `regen_compare.py` would then
report `labels_differ` and still read PARITY_AFTER_NOISE, because the label is normalised. **Board E5** has no
schematic: `v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb` is its design (`readiness_manifest.json`, `no_chain`).

## 5. Re-export the readable PDFs and BOMs

`v2/release/handover/_generated/<phase directory>/` holds, for each board, the A3-paged schematic PDF, two BOMs
(named `NOT_FOR_FAB-*`: nothing here is released for fabrication), the ERC report in JSON and text, the netlist parity
of the committed netlist against a fresh export of the committed schematic, and `provenance.json` (schematic sha256,
every command and exit status, every output's sha256, the PDF page count and page-1 text read back). They were
made by:

```
cd "$HO/.."
mkdir -p ex
unzip -q H1.zip -d ex
cd ex/H1
python3 v2/ecad/tools/handover_exports.py exports --out "$HO/../ex-out" --commit "$(sed -n 's/^commit: //p' SOURCE.txt)"
for b in pcb-a-power-a23 pcb-b-compute-b19 pcb-c-display-c8 pcb-d-aprs-d9 pcb-e1-dock-e7 pcb-p-pack-p2; do for f in v2/release/handover/_generated/$b/NOT_FOR_FAB-*.csv; do cmp "$f" "$HO/../ex-out/$b/$(basename "$f")" && echo "same: $b/$(basename "$f")"; done; done
```

Expected: one line per board ending `: OK`, netlist parity `PARITY_AFTER_NOISE` for all six, and these counts:

| Board | Paged PDF pages | BOM rows (per reference) | ERC (kicad-cli, all severities) |
|---|---|---|---|
| A | 14 | 566 | 1528 warnings |
| B | 38 | 1015 | 5 errors, 2393 warnings; the 5 errors are the three PWR_FLAG pin-to-pin reports and the two SIM VCC pins that `pcb-b-compute-b19/erc-allow.txt` explains line by line (`erc_gate.py` decides) |
| C | 5 | 167 | 328 warnings |
| D | 7 | 218 | 445 warnings |
| E1 | 4 | 170 | 365 warnings |
| P | 2 | 69 | 123 warnings |

The loop prints twelve `same:` lines: both BOMs of every board re-export byte for byte. A re-exported PDF differs from
the committed one in its creation date; its page count and page-1 text are in `provenance.json`. **Read the BOMs for what they are**: the generators write
Reference, Value, Footprint, Description, Datasheet and, where one is chosen, an LCSC order code; they write no
manufacturer part number field. Of the 2205 per-reference rows of the six boards, 1497 carry no LCSC code, 1322 of
them resistors, capacitors and inductors named by value and land (at `e3aedb25` it was 1509 of 2157); `lcsc_fill.py` assigns codes to those at the JLC
BOM stage. The part identities that are decided are in `v2/vendor/SOURCES.yaml`.

## 6. The representative calculation: the stored-energy chain

`energy_chain.py` checks the chain from the cells to every protected branch (`v2/ecad/tools/pcb_energy_chain.yaml`,
rules BAT-002 and PWR-003): every rating names its source document and the document is present, every protective
element is on the board it claims in that board's committed netlist, each element opens before its conductor and
connector are over their rating, it does not open in normal use, and it can interrupt the prospective fault.

```
cd "$HO/v2/ecad/tools"
VERDICT_DIR="$HO/../verdicts" python3 energy_chain.py --ecad ..
echo "energy_chain exit $?"
```

Expected: `energy_chain: 12 stage(s), 98 check(s)`, fifteen `note` lines (for example `PACK_CELLS: F1 carries 10.0 A
of its 25.0 A rating (40 percent), inside the 65 percent ECSS-Q-ST-30-11C Rev.2 Table 6-17 sets for a fuse at or below
85 C`, `F1 melts in about 4.3 ms at 480 A (I2t 1000 A2s)`, and for `SHORE_INPUT` that the fault current available is
not established, owner decision 34), one finding `FAIL (coordination, rule PWR-003) B_PANEL_5V: the protection is
rated 2.0 A and the conductor only 1.2 A, so the conductor is the fuse`, and `verdict: energy_chain PASS of 98
{"checks": 98, "citations_unjudged": 0, "coordination_findings": 1, "fail": 0, "selection_findings": 0, "stages": 12}`,
exit 0. The chain end to end (BAT-002) passes; the coordination finding is board B's: `../verdicts/energy_chain_b.verdict.json`
reads FAIL (PWR-003, 1 of 3 stages), and `energy_chain_a`, `_e`, `_e5` and `_p` read PASS. `citations_unjudged: 0`
holds because this snapshot bundles the eight maker documents the chain cites (`pack.yaml`, layer 9 rule); without
them the tool reports each citation as missing.

## 7. The test suite

The suite is `v2/ecad/tools/tests/run.py` (plain Python, no pytest; a test is a `t_*` function and fails by raising;
board-file fixtures skip where `pcbnew` is not importable). From a fresh extraction:

```
cd "$HO/.."
mkdir -p suite
unzip -q H1.zip -d suite
cd suite/H1/v2/ecad/tools/tests
python3 run.py > "$HO/../suite.log" 2>&1
echo "suite exit $?"
tail -n 1 "$HO/../suite.log"
```

Expected: `suite exit 1` and `tests: 1913 passed, 17 failed, 22 skipped` (a skip is not a pass: the 22 name what
they could not run). **Every one of the 17 failures is caused by what the snapshot leaves out, none by a design
finding**, and each names its missing input:

| Failures | Tests | The input the snapshot does not carry |
|---|---|---|
| 11 | `test_requirements` (4: the registry validates, the trace page is generated, `--check`, the decision index), `test_layout_entry_stages`, `test_interfaces`, `test_emc_sheet`, `test_rails_census` (3), `test_evidence_class` (every declared writer's fixed input exists) | maker documents cited and referenced, not bundled. The seven the requirements registry cited at `e3aedb25` are bundled (`pack.yaml`, layer 3 rule), but since the layer 6 closer's merge CON-017 also binds ST's `st/st-rm0433-rev8.pdf` (40.7 MB), `st/st-stm32h743xi-datasheet-rev11.pdf` and `st/st-es0392-rev15.pdf`, about 21 MB compressed together, which the 50 MB cap of `pack.yaml` leaves out; so the registry reports 4 errors, all on CON-017. `pcb_interfaces.yaml` cites `quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf`; the EMC sheet cites `ti/lm5176-datasheet.pdf` and others; the rails census reads `ti/ti-tpa6132a2.pdf` and `power/tps2596.pdf`; `intent_checks.py` declares `battery/ti-bq77207.pdf`. A tree that holds part of `v2/vendor/` is judged as holding the library, so an absent citation is a failure there, not a skip |
| 3 | `test_block_contract` | board A's board file `pcb-a-power-a23/pcb-a-power.kicad_pcb`, excluded as a stale layout: board E5's pin map is compared with it, so from the snapshot its contract reads INCONCLUSIVE |
| 2 | `test_doc_provenance.t_the_tree_today_is_reported_rather_than_assumed`, `test_order_readiness` | the historical order folders under `v2/release/revA/order/`, excluded |
| 1 | `test_netlist_provenance` | the git index: it lists committed netlists with git, and an extraction has no `.git` |

The requirements validator on its own, from the extraction (`cd v2/ecad; python3 tools/rules_lib.py requirements`),
reads `132 requirement record(s), 4 error(s), 16 warning(s)`: the four errors are CON-017's ST documents, fifteen
warnings are closed items whose closing commits git cannot look up in an extraction, and one says `out/rule-audit` is
not in the tree (the readings are gitignored). Copying `v2/vendor/` from the repository at the snapshot's commit into
the extraction (every file's sha256 is in `REFERENCED-SOURCES.tsv`) supplies every cited document; that was run for
the `e3aedb25` design (its seven such failures then passed) and not repeated for H1. The route below, from the
repository itself, clears all but the git one.

**From the repository at the snapshot's commit** (where the maker documents, the earlier layouts and the order sets
are present), on a machine holding the repository and then on the KiCad host, with `<commit>` the `commit:` line of
`SOURCE.txt`:

```
git archive --format=tar <commit> | gzip -1 > tree.tgz
mkdir tree && tar xzf tree.tgz -C tree
cd tree/v2/ecad/tools/tests
python3 run.py > suite.log 2>&1
tail -n 1 suite.log
```

Expected, as run on `e3aedb25` with the handover files unpacked over it (this route was not re-run for H1):
`tests: 1666 passed, 1 failed, 17 skipped`, the one failure `test_netlist_provenance` (it lists committed netlists
through the git index, and an archive extraction has none). H1 adds tests (the packer's among them), so its counts
are higher; the result of the full suite in a git worktree of the repository at the H1 branch is recorded in the
message of the commit that files the H1 snapshot, `a8652172` (1889 passed, 0 failed, 63 skipped, every skip a missing
`pcbnew` or `kicad-cli`), filed as `v2/docs/records/handover/a8652172-commit-message.txt`.

**In a git checkout two further conditions hold.**
`test_netlist_provenance` reads the index; and `pcb_requirements.yaml` names, for each closed item, the commit that
closed it, which the validator looks up in the repository's history. A scratch repository holding the same files as
a single commit, with no history, read `1666 passed, 5 failed, 13 skipped`: the five are the registry refusing fifteen
closed items whose commits (`458b2873`, `93138ac1`, `9a151c78`, `3a1f6576`, `4ec785d8`, `faf8c981`, `68bc9e8f`) it
could not find (at `e3aedb25`; H1 adds S-43, closed on `dd39fb15`). All are ancestors of the H1 source commit, so a
full clone has them; a shallow clone or
a repository re-created from the files does not.

## 8. Build and check a snapshot

`handover_pack.py` builds a snapshot from one commit (never from a working tree) as `v2/docs/handover/pack.yaml`
describes it; see its docstring. In a clone of the repository:

```
python3 v2/ecad/tools/handover_pack.py plan --commit <commit>
python3 v2/ecad/tools/handover_pack.py build --commit <commit> --version <name> --out <dir>
python3 v2/ecad/tools/handover_pack.py verify <dir>/<name>.zip
```

`plan` must end `0 unclassified` (a file of the commit that no rule of `pack.yaml` classifies refuses the build).
`build` writes `<dir>/<name>/`, `<dir>/<name>.zip` and `<dir>/<name>.zip.sha256`, and refuses a name that exists;
with `--zip-only` it writes `<dir>/<name>.MANIFEST.tsv` (a byte copy of the ZIP's manifest) instead of the folder,
and `verify <dir>/<name>.zip` then also checks that copy against the ZIP's own. Two
builds of one commit on one host write the same MANIFEST.tsv and the same ZIP bytes (tested in
`tests/test_handover_pack.py`); on another host the ZIP's compressed bytes and `SOURCE.txt`'s host lines can differ, so
compare `MANIFEST.tsv` rows other than `SOURCE.txt`'s, not the ZIP's sha256. `SOURCE.txt`'s commit timeline marks a
commit public when it is an ancestor of the building clone's `refs/remotes/origin/main` (`pack.yaml` `public`), so it
says what that clone knew when it built, and "unknown" in a clone with no such ref.

## 9. Re-take the schematic-phase readings and re-render CURRENT-EVIDENCE

**Status in H1.1: the procedure is stated, its driver lands in the next snapshot.** The layout-entry status (0 boards
ready; reasons A 17, B 16, C 11, D 15, E 16, P 15, E5 5) and every `PCB-RULE-STATUS-<x>.md` verdict are rendered from
readings (`*.verdict.json`) in gitignored `out/` folders that no snapshot carries (START-HERE section 3a, known gap 1).
A driver that runs exactly the writers the layout-entry test reads, `v2/ecad/tools/retake_schematic_phase.py`, was being
written when H1.1 was cut and is not in it; until it lands, the order below is the procedure, and it is the order that
driver follows. None of it was run for H1.1.

1. **Work in a throwaway git clone outside `/tmp`, on a KiCad 9.0.9 host** (section 1). A reading taken on files under
   `/tmp` is classed TEMP_INPUT and never counts; a reading of an uncommitted netlist is evidence about nothing anyone
   can check out, so every input (netlist, provenance sidecar, intent file, schematic, project, allow-lists) must be
   tracked and unmodified (`git status --short` empty).
2. **List what to run per board from the registries, never by hand.** For board `<x>`: every rule
   `rules_lib.rules_for("<x>")` returns with `verification_phase: SCHEMATIC`, plus every rule a hold of
   `pcb_board_holds.yaml` names under `layout_entry_requires` as `rule_pass`; for each, `pcb_rules_coverage.yaml` names
   the verifying tool and the verdict names it writes. A rule verified by a desk review has no writer and is not run.
   Each writer must be declared in `rules_status.CONFIG_INPUTS`, or its reading can never bind.
3. **Run every writer on the committed netlist, in the board's declared phase directory, with `VERDICT_DIR` set to
   that directory's `out/`** (the place `full.sh`'s writers write, which `rules_status.py` reads), with the arguments
   `v2/ecad/tools/gate_sweep.sh` gives them: `erc_gate.py . <stem> --run` (with the schematic and `kicad-cli`),
   `safe_lines.py`, `pin_map_lands.py`, `derate.py`, `intent_checks.py --netlist`, `power_sequence.py`,
   `edge_length.py --netlist`, `clock_check.py`, `port_protect.py`, `pack_protection.py --netlist ... --check`,
   `energy_chain.py --ecad ..`, and the rest the coverage map names for that board. Never run a writer in a working
   checkout you keep: that writes the tree's own evidence (START-HERE section 6).
4. **Classify and render.** From `v2/ecad`: `python3 tools/rules_status.py` three times, the integrating session's practice
   (the last run must leave its outputs unchanged; if it does not, run it again and say so), then
   `python3 tools/rules_render.py` to write `CURRENT-EVIDENCE.md` and the per-board status pages, and
   `python3 tools/rules_render.py --check` to confirm they are current. Commit any configuration input
   (`pcb_rules_coverage.yaml` and the like) BEFORE running `rules_status.py`: an uncommitted configuration input
   reads CONFIG_CHANGED.
5. **Compare** the new layout-entry reasons per board with the figures above; a row that moved names the reading that
   moved it (`CURRENT-EVIDENCE.md`, "Layout entry, per board: the exact remaining blockers").
