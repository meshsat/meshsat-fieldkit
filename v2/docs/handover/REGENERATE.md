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

**How it was verified (H2).** Every command in a grey block of sections 2 to 7 (the ZIP route) and of section 1a was
run as written (with `REF` set as section 1a says), with the snapshot's name H2, between 15:27 and 15:45 UTC on 27 September 2026, on a rented
Ubuntu 24.04 host with 64 cores and KiCad 9.0.9, from fresh extractions of a build of `H2` at commit `c5d09c78` of
branch `fnd/h2`: sections 2 to 7 as one script, section 1a and section 6's second block each in its own extraction
(the scripts and their logs are filed in `v2/docs/records/h2/box/`). That build's design files, tools and exports are byte for byte those of
the H2 source commit named in `SOURCE.txt`: the commits between them change only the handover pages (this one
among them), the wording of one exclusion reason in `pack.yaml` (the `routed/` rule) and the records they file
(`v2/docs/records/h2/box/` and the rows of `v2/docs/records/README.md`). The exports of boards A, B,
D and E and the six-board regeneration had also been run once before, each on a clean `git archive` of `763bccdf`,
with the same results. A content hash or a count quoted below is what those runs printed; the RESULT classes (PARITY,
PARITY_AFTER_NOISE, the causes of the failures) are what to expect on another day. Commands outside the ZIP route
(section 7's repository route, sections 8 and 9) say how far they were re-run. **H1's run** (04:50 to 05:04 UTC the
same day, from a build of `H1` at `0778e1ab`) is the source of the figures this page marks as H1's.

**Edition H2.** The commands below name `H2`; for an earlier snapshot read its name (`H1`, `H1.1`) wherever a command
names the ZIP or its folder, and that snapshot's own copy of this page for its expected values. H2 carries new exports
of boards A, B, D and E, the re-take driver of section 9 and its first full run (`8ea7867e`), and references the five
superseded candidate patches instead of bundling them. The repository holds it as `v2/release/handover/H2.zip` with
`H2.zip.sha256` and `H2.MANIFEST.tsv` beside it. **Edition H1.1.**
H1.1's design files, tools and exports are H1's; it adds the candidate patches, the glossary, four filed records,
the case scripts' reference outputs and the packer's new `SOURCE.txt` lines. Section 1a is new in H1.1. Section 9
stated the re-take in words only in H1.1; from the commit after H1.1 on it carries its driver,
`retake_schematic_phase.py`, and is run by it. The repository holds H1.1 as `v2/release/handover/H1.1.zip` with `H1.1.zip.sha256` and `H1.1.MANIFEST.tsv` beside it (the
packer's `--zip-only` mode), not as an unzipped folder; `unzip` creates the `H1.1/` folder the commands expect.

## 1. Prerequisites (the versions the commands were run with)

**Where the repository is.** The public repository is `https://github.com/meshsat/meshsat-fieldkit` (clone with
`git clone https://github.com/meshsat/meshsat-fieldkit.git`); one file at one commit is
`https://raw.githubusercontent.com/meshsat/meshsat-fieldkit/<commit>/<path>`. The snapshot's `SOURCE.txt` names its
build commit on its `commit:` line and carries a commit timeline: every commit id the handover pages name, with its
date and subject, whether it is in the snapshot's history and whether it was on the public repository when the
snapshot was built. The H1 snapshot was filed by commit `a8652172` (its message, with the suite results of that day,
is filed as `v2/docs/records/handover/a8652172-commit-message.txt`); H1.1 by `84d0a527`; H2 by the commit after its
source commit on branch `fnd/h2`, whose message names the source commit, the ZIP's sha256 and the verification.

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
`REFERENCED-SOURCES.tsv` with their git blob sha (column 2) and sha256. Since H2 the five superseded candidate patches
of H1.1 (`v2/docs/handover/candidates/*.patch`) are listed there too. Four checks need referenced files: the
requirements validator and `rules_render.py --requirements --check` need the documents the registry cites that the
snapshot does not bundle (in H2 eleven: `v2/vendor/st/`'s three for CON-017 and eight cited since H1, among them
TI's BQ4050 technical reference manual for REQ-042 and REQ-077); the battery packet's `check_manifest.py` needs the
vendor documents its manifest cites; and the energy chain of section 6 needs Mill-Max's catalogue page 28. From the
snapshot's root, with network access (`REF` is the build commit when the timeline in `SOURCE.txt` marks it public,
else the newest public commit of the timeline; the blob check proves the bytes whichever commit served them; the H2
run used `REF=62f26a44`, the newest public commit its timeline listed):

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
fetch $(cd v2/ecad && python3 tools/rules_lib.py requirements 2>&1 | awk '/^ERROR/' | grep -o 'v2/vendor/[^ ,]*' | sort -u)
fetch $(python3 v2/docs/review-packets/battery/evidence/check_manifest.py | awk '$1=="MISSING"{print $2}')
fetch v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf
python3 v2/docs/review-packets/battery/evidence/check_manifest.py
(cd v2/ecad && python3 tools/rules_lib.py requirements)
python3 v2/ecad/tools/rules_render.py --requirements --check
```

Every fetched line must read `OK`. Expected afterwards (the H2 run, 29 files fetched, every one `OK`): `checked 139
rows of MANIFEST.md` and `RELEASE CHECK PASS` from the packet check, `144 requirement record(s), 0 error(s), 17
warning(s)` from the validator (the warnings stay: closed-by-commit checks that need git history, section 7) and
`v2/docs/REQUIREMENTS-TRACE.md is current`. A candidate patch is fetched the same way by its path, for example `fetch
v2/docs/handover/candidates/r8b.patch`. The eight ST files are about 83 MB (RM0433 alone 40.7 MB); fetch only what a
check needs. A restored file makes the snapshot folder differ from its manifest, so run `handover_pack.py verify`
before restoring, or on a second copy.

## 2. Check the snapshot

From the directory holding `H2.zip` and `H2.zip.sha256`:

```
export PYTHONDONTWRITEBYTECODE=1
sha256sum -c H2.zip.sha256
unzip -q H2.zip
cd H2
HO="$PWD"
python3 v2/ecad/tools/handover_pack.py verify .
python3 v2/ecad/tools/sch_prov.py read v2/ecad/pcb-p-pack-p2/out/pcb-p-pack.net p
```

Expected: `H2.zip: OK`; `handover_pack: verify .: OK` (every file's bytes and sha256 against `MANIFEST.tsv`,
and no file the manifest does not name); `sch_prov: pcb-p-pack.net was written by this tree's own generator
(ee62fdb195a9f217)`, which says the netlist's recorded generator inputs (the generator, its imports, the board
table's `gen_env` and 60 land files) are byte-identical to the ones in this snapshot (H1 printed `21640b801014107a`
over 59 land files: board B's round 8, `b76c18cb`, changed shared generator inputs, added a land to `meshsat.pretty`
and re-stamped board P's sidecar with them). `PYTHONDONTWRITEBYTECODE=1`
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
  `sch_prov: pcb-p-pack.net written by generator ee62fdb195a9f217 (...)`, `sch_pages: 2 x 1 cells, 2 pages kept of 2
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
unzip -q H2.zip -d rg
cd rg/H2
python3 v2/ecad/tools/handover_exports.py regen --out "$HO/../rg-out" --letters a,b,c,d,e,p
```

Expected, per board (`rg-out/<letter>/regen.json` holds each command, its exit status and every comparison). In the
H2 run all six printed `PARITY` (A, B, D and E, whose schematics were written on 27 September 2026, with the schematic
at PARITY; C and P, written on 26 September, at PARITY_AFTER_NOISE); board D's netlist content hash is H1's because
set 5 changed only its intent declarations and noise lines:

| Board | Phase directory | PHASE used (the committed label) | Board table `phase` | Footprint generators | Netlist content hash | Result |
|---|---|---|---|---|---|---|
| A | `pcb-a-power-a23` | A65 | A32 | `gen_footprints_idc.py` | `2c5c1d5a388cc95f` (H1: `66797255f4591a23`) | schematic PARITY on the commit's day or PARITY_AFTER_NOISE later (the date), netlist, intent and ERC PARITY_AFTER_NOISE, BOM PARITY, no land changed: the driver prints `PARITY` |
| B | `pcb-b-compute-b19` | B21 | B21 | `gen_footprints_b16.py`, `gen_footprints_idc.py` | `39d83d25efcd75a6` (H1: `70be33b07a339d6e`) | the same |
| C | `pcb-c-display-c8` | C24 | C24 | none | `96c2678f4a3303b8` | the same |
| D | `pcb-d-aprs-d9` | D37P | D12 | `gen_footprints_b16.py`, `gen_footprints_idc.py` | `ecc07f382c735835` | the same |
| E1 | `pcb-e1-dock-e7` | E42P | E17 | `gen_footprints_e.py` | `b8d237f0b8d759f5` (H1: `256cc3f96d41dcab`) | the same |
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
unzip -q H2.zip -d ex
cd ex/H2
python3 v2/ecad/tools/handover_exports.py exports --out "$HO/../ex-out" --commit "$(sed -n 's/^commit: //p' SOURCE.txt)"
for b in pcb-a-power-a23 pcb-b-compute-b19 pcb-c-display-c8 pcb-d-aprs-d9 pcb-e1-dock-e7 pcb-p-pack-p2; do for f in v2/release/handover/_generated/$b/NOT_FOR_FAB-*.csv; do cmp "$f" "$HO/../ex-out/$b/$(basename "$f")" && echo "same: $b/$(basename "$f")"; done; done
```

Expected: one line per board ending `: OK`, netlist parity `PARITY_AFTER_NOISE` for all six, and these counts (H2's;
H1's were A 14, 566, 1528; B 38, 1015, 5 errors and 2393 warnings; E1 4, 170, 365; C, D and P unchanged):

| Board | Paged PDF pages | BOM rows (per reference) | ERC (kicad-cli, all severities) |
|---|---|---|---|
| A | 16 | 586 | 1522 warnings |
| B | 43 | 1179 | 7 errors, 2872 warnings; the 7 errors are the three PWR_FLAG pin-to-pin reports, the two SIM VCC pins and the two QOD-to-VOUT ties of U21 and U22 (round 8, the maker's own configuration) that `pcb-b-compute-b19/erc-allow.txt` explains line by line (`erc_gate.py` decides) |
| C | 5 | 167 | 328 warnings |
| D | 7 | 218 | 445 warnings |
| E1 | 4 | 174 | 367 warnings |
| P | 2 | 69 | 123 warnings |

The committed exports of A, B, D and E were made at `763bccdf` (their schematics changed in board B's round 8 and
set 5); C and P keep the exports made at `99cde56b`, whose `provenance.json` names the schematic sha256 this snapshot
still holds (`v2/docs/records/h2/handover_counts.py` checks it).

The loop prints twelve `same:` lines: both BOMs of every board re-export byte for byte (in the H1 and H2 runs alike). A re-exported PDF differs from
the committed one in its creation date; its page count and page-1 text are in `provenance.json`. **Read the BOMs for what they are**: the generators write
Reference, Value, Footprint, Description, Datasheet and, where one is chosen, an LCSC order code; they write no
manufacturer part number field. Of the 2393 per-reference rows of the six boards in H2, 1630 carry no LCSC code, 1446 of
them resistors, capacitors and inductors named by value and land (H1: 1497 of 2205, 1322; at `e3aedb25`: 1509 of
2157); `lcsc_fill.py` assigns codes to those at the JLC BOM stage. The part identities that are decided are in `v2/vendor/SOURCES.yaml`.

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

Expected from the ZIP alone (H2): `energy_chain: 12 stage(s), 98 check(s)`, fifteen `note` lines (for example
`PACK_CELLS: F1 carries 10.0 A of its 25.0 A rating (40 percent), inside the 65 percent ECSS-Q-ST-30-11C Rev.2 Table
6-17 sets for a fuse at or below 85 C`, `F1 melts in about 4.3 ms at 480 A (I2t 1000 A2s)`, and for `SHORE_INPUT`
that the fault current available is not established, owner decision 34), then one finding, `FAIL DOCK_BLOCK: the
conductor names v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf, which is not in this tree`, and
`verdict: energy_chain FAIL of 98 {"checks": 98, "citations_unjudged": 0, "coordination_findings": 0, "fail": 1, ...}`,
exit 1; `../verdicts/energy_chain_a.verdict.json` and `energy_chain_e5` read FAIL on that citation, `_b`, `_e` and `_p`
PASS. The cited page (Mill-Max's catalogue page 28, 3.8 MB) is the basis of the dock's VIN_RAW power pins since set 5
(`b7f96784`, EQ-16) and is referenced, not bundled, because the ZIP has no room for it under `pack.yaml`'s cap; the
eight documents `pack.yaml`'s layer 9 rule bundles are every other citation of the chain. Restore it with section
1a's `fetch` function (defined there; `REF` a public commit of the timeline) and run the chain again:

```
cd "$HO"
fetch v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf
cd "$HO/v2/ecad/tools"
VERDICT_DIR="$HO/../verdicts" python3 energy_chain.py --ecad ..
echo "energy_chain exit $?"
```

Expected then: `OK v2/vendor/connectors/millmax-rugged-power-spring-pins-page28.pdf`, the same fifteen notes, no
finding, and `verdict: energy_chain PASS of 98 {"checks": 98, "citations_unjudged": 0, "coordination_findings": 0,
"fail": 0, "selection_findings": 0, "stages": 12}`, exit 0; `energy_chain_a`, `_b`, `_e`, `_e5` and `_p` all read
PASS. Both runs were made in the H2 run (the second in its own extraction, the file fetched from `62f26a44`). H1's
run read PASS of 98 from the ZIP alone with one coordination finding on board B, `B_PANEL_5V` (2.0 A protection on a
1.2 A conductor); board B's round 8 (`b76c18cb`) closed it on the part (its F1 is an MF-MSMF110, 1.1 A hold, under
the 1.23 A track: `pcb_energy_chain.yaml`, `known_findings`), and the chain end to end (BAT-002) passes. A restored
file makes the extraction differ from its manifest, so run section 3's `verify` before restoring, or on a second
extraction.

## 7. The test suite

The suite is `v2/ecad/tools/tests/run.py` (plain Python, no pytest; a test is a `t_*` function and fails by raising;
board-file fixtures skip where `pcbnew` is not importable). From a fresh extraction:

```
cd "$HO/.."
mkdir -p suite
unzip -q H2.zip -d suite
cd suite/H2/v2/ecad/tools/tests
python3 run.py > "$HO/../suite.log" 2>&1
echo "suite exit $?"
tail -n 1 "$HO/../suite.log"
```

Expected, as run from the H2 extraction (15:35 to 15:42 UTC on the KiCad 9.0.9 host, where `pcbnew` imports):
`suite exit 1` and `tests: 1956 passed, 20 failed, 23 skipped` (a skip is not a pass: the 23 name what they could not
run, most of them the gitignored readings, the deliverable folders and the git checkout a snapshot does not carry).
**Every one of the 20 failures is caused by what the snapshot leaves out, none by a design finding**, and each names
its missing input (the table below). The packer's own tests, `python3 run.py test_handover_pack`, read 14 passed and
1 skipped, the skip being the test that applies `pack.yaml` to a git checkout's HEAD, which an extraction is not; each
of the others builds its own scratch repository with the `git` binary, so from an extraction they need `git` on the
path and nothing else. H1's run read `1913 passed, 17 failed, 22 skipped`; H2 adds tests (the case geometry's, the
re-take driver's, the validator's SC- id check among them) and the three failure causes marked new below.

| Failures | Tests | The input the snapshot does not carry |
|---|---|---|
| 11 | `test_requirements` (4: the registry validates, the trace page is generated, `--check`, the decision index), `test_layout_entry_stages`, `test_interfaces`, `test_emc_sheet`, `test_rails_census` (3), `test_evidence_class` (every declared writer's fixed input exists) | maker documents cited and referenced, not bundled. The seven the requirements registry cited at `e3aedb25` are bundled (`pack.yaml`, layer 3 rule); CON-017 binds ST's `st/st-rm0433-rev8.pdf` (40.7 MB), `st/st-stm32h743xi-datasheet-rev11.pdf` and `st/st-es0392-rev15.pdf`, about 21 MB compressed together, and since H1 eight more documents are cited (section 1a), all left out under the cap of `pack.yaml`; so the registry reports 13 errors. `pcb_interfaces.yaml` cites `quectel/quectel-rm520n-gl-hardware-design-v1.0.pdf`; the EMC sheet cites `ti/lm5176-datasheet.pdf` and others; the rails census reads `ti/ti-tpa6132a2.pdf` and `power/tps2596.pdf`; `intent_checks.py` declares `battery/ti-bq77207.pdf`. A tree that holds part of `v2/vendor/` is judged as holding the library, so an absent citation is a failure there, not a skip |
| 1 (new) | `test_energy_chain.t_the_committed_chain_fails_only_where_this_tree_says_it_does` | Mill-Max's catalogue page 28, which the chain's DOCK_BLOCK stage cites since set 5 (section 6) |
| 1 (new) | `test_case_geometry.t_a_makers_maximum_is_read_for_its_part` | ST's STM32H753 data sheet (DS12117), whose LQFP100 table gives the height maxima of board B's supervisors U41 and U61 |
| 1 (new) | `test_case_geometry.t_release_folder_is_immutable` | the case release's STL files, which `pack.yaml` leaves out as tessellations of the STEP beside them while the release's `MANIFEST.sha256` names them |
| 3 | `test_block_contract` | board A's board file `pcb-a-power-a23/pcb-a-power.kicad_pcb`, excluded as a stale layout: board E5's pin map is compared with it, so from the snapshot its contract reads INCONCLUSIVE |
| 2 | `test_doc_provenance.t_the_tree_today_is_reported_rather_than_assumed`, `test_order_readiness` | the historical order folders under `v2/release/revA/order/`, excluded (all but `JLC-CERTIFIED.tsv`, which is bundled and current) |
| 1 | `test_netlist_provenance` | the git index: it lists committed netlists with git, and an extraction has no `.git` |

The requirements validator on its own, from the extraction (`cd v2/ecad; python3 tools/rules_lib.py requirements`),
reads `144 requirement record(s), 13 error(s), 17 warning(s)`: every error names a maker document the snapshot
references (CON-017's three ST documents in four errors, and eight documents cited since H1 in nine), and the warnings
are closed items whose closing commits git cannot look up in an extraction, beside a note that `out/rule-audit` is
not in the tree (the readings are gitignored). Section 1a fetches the eleven documents and the validator then reads 0
errors. The route below, from the repository itself, clears every failure but the git one.

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

Expected, as run on `e3aedb25` with the handover files unpacked over it (this route was not re-run for H1 or H2):
`tests: 1666 passed, 1 failed, 17 skipped`, the one failure `test_netlist_provenance` (it lists committed netlists
through the git index, and an archive extraction has none). H1 and H2 add tests, so their counts are higher. The
result of the full suite in a git worktree of the repository at each snapshot's filing commit is recorded in that
commit's message: H1's `a8652172` (1889 passed, 0 failed, 63 skipped, every skip a missing `pcbnew` or `kicad-cli`,
filed as `v2/docs/records/handover/a8652172-commit-message.txt`); H2's is the commit that files `H2.zip`, run once on
the runner, which has no KiCad.

**In a git checkout two further conditions hold.**
`test_netlist_provenance` reads the index; and `pcb_requirements.yaml` names, for each closed item, the commit that
closed it, which the validator looks up in the repository's history. A scratch repository holding the same files as
a single commit, with no history, read `1666 passed, 5 failed, 13 skipped`: the five are the registry refusing fifteen
closed items whose commits (`458b2873`, `93138ac1`, `9a151c78`, `3a1f6576`, `4ec785d8`, `faf8c981`, `68bc9e8f`) it
could not find (at `e3aedb25`; H1 adds S-43, closed on `dd39fb15`, and H2 S-77, closed on `cecfd0f1`). All are
ancestors of the snapshot's source commit, so a full clone has them; a shallow clone or
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
says what that clone knew when it built, and "unknown" in a clone with no such ref. `build` exits 3 when the ZIP is
over `pack.yaml`'s `max_zip_bytes` (52,428,800) and still writes it so it can be read: a trial build of `763bccdf` read
54,938,457 bytes, so H2 moved the five superseded candidate patches from bundled to referenced (the rule and its
reason are in `pack.yaml`), and a build at `c5d09c78` read 51,846,825 bytes.

## 9. Re-take the schematic-phase readings and re-render CURRENT-EVIDENCE

`v2/docs/CURRENT-EVIDENCE.md` says, for every board, which schematic-phase rows a re-take alone would make current
evidence (`rules_status.retake_projection`). `v2/ecad/tools/retake_schematic_phase.py` is the command that takes those
re-takes. It was added after H1.1, so neither the H1 nor the H1.1 snapshot carries it (H2 does) (H1.1's section 9 stated the
procedure in words only); it is in the repository from the commit that adds this section on. It enumerates from the
registries the pages already use, never from a hand list: every applicable rule verified at SCHEMATIC (`rules_lib.rules_for` and each rule's `verification_phase`) and every rule a
hold names as a `rule_pass` layout-entry requirement; the coverage map `pcb_rules_coverage.yaml` for each rule's
maturity and verdict names; `rules_status.CONFIG_INPUTS`, which must declare every writer (or its reading could never
bind); and `readiness_manifest.json` with each board's routeflow profile for the phase directory. It then runs each
writer on the committed netlist and schematic of the board's declared phase with the pipeline's arguments
(`gate_sweep.sh` for every writer, `erc_gate.py --run` as `full.sh` runs it, `intent_checks.py` and `edge_length.py` in
their `--netlist` modes, which write the schematic-phase verdict alone). A verdict whose writer it does not know is an
error in the plan, never a skip. A rule verified by a desk review of a pinned document (ENV-001, INT-002, TST-001) is
listed and not run. It decides nothing: `rules_status.py` reads what it writes and `rules_render.py` renders the pages.

**Where it runs.** It needs a git clone outside `/tmp` (every input must be tracked and unmodified, `git status
--short` empty; an extraction without `.git` refuses every board; and `rules_status.py` classes a reading taken on
files under a temporary directory as TEMP_INPUT, which never counts) and `kicad-cli` 9.0.9 for `erc_gate.py --run`
(without it that step is reported SKIPPED and the run INCOMPLETE: a skip is not a pass). `--in-place` writes into the tree's own evidence folders, which nobody does by
hand in a working checkout, so it is run in a THROWAWAY CLONE and the clone is deleted afterwards. It opens no socket.

```
git clone <repository> ~/rtk
cd ~/rtk
git checkout <commit>
cd v2/ecad
python3 tools/retake_schematic_phase.py --plan --in-place
python3 tools/retake_schematic_phase.py --run --in-place --routed --json > ../../../retake.json 2> ../../../retake.log
echo "retake exit $?"
for i in 1 2 3; do python3 tools/rules_status.py > ../../../status-$i.log 2>&1; tail -n 1 ../../../status-$i.log; done
python3 tools/rules_render.py
python3 tools/rules_render.py --check
sed -n 5p ../docs/CURRENT-EVIDENCE.md
```

If you changed a configuration input (`pcb_rules_coverage.yaml` and the like), commit it BEFORE the first
`rules_status.py` run: an input no commit dates reads CONFIG_CHANGED. The last of the three runs must leave its
outputs unchanged; if it does not, run it again and say so. `rules_render.py --check` must then read the pages current.

`--plan` prints, per board, every rule in scope with its action and every command, and ends with the plan size;
`--board <x>` limits either mode to one board. `--run --in-place` runs each board's commands in its phase directory
with `VERDICT_DIR=<phase>/out` (where `rules_status.py` reads), refuses a board whose inputs are not committed or
changed under the run, and exits 1 if a step wrote no reading. `--routed` also copies the re-taken readings, and the
SI-001 table `edge_length.py` writes beside its verdict, into `<phase>/routed/`, the tracked evidence home
`gate_sweep.sh` copies to, so a clone's re-take can be committed; it is refused without `--in-place`. `--json` puts the
result alone on stdout (each step's command, exit status, time and readings) and the plan and progress on stderr.
The set-level writers (`energy_chain.py`, `check_contracts.py`, `interfaces.py`) also write into each board's
`<phase>/out`, once per board, as `gate_sweep.sh` runs them, rather than into `v2/ecad/out/` (H1.1's wording of this
section named `v2/ecad/out/`); `rules_status.py` reads both folders (`_project_dirs`). `--verdict-dir DIR`, instead of
`--in-place`, stages each board's committed inputs under `DIR` (outside the repository) and runs there, and the run fails if any writer touched the tree's evidence folders; those readings are for reading,
not for `rules_status.py`, which reads the tree only (and names a reading of a file under `/tmp` TEMP_INPUT). Three
`rules_status.py` runs, because the first writes the audit's own reading `rules_complete`, which the next one reads.

**The consolidated re-take (the evidence H2 carries).** Run as written above, in a clean clone of main at `391d8579`
(set 5 integrated) on the rented KiCad 9.0.9 box, built from the box's own clone plus an incremental git bundle, HEAD
checked and `git status` empty; committed as `8ea7867e` and installed on main at `5ca81eea`. `--plan`: 73 commands
over 7 boards (A 12, B 12, C 9, D 10, E 12, E5 6, P 12), 76 rule-board pairs re-taken, 14 desk-review pairs listed, 83
verdicts, 0 errors. `--run --in-place --routed --json` between 13:21:51 and 13:23:39 UTC on 27 September 2026: exit 0,
108 s, no board refused, no step skipped, 83 readings written and 89 files copied to `routed/`. Then `rules_status.py`
three times and `rules_render.py` twice; `rules_render.py --check` read 16 documents, 0 out of date. Results per board
(a FAIL or an INCONCLUSIVE is the design's or its declarations' answer, on current evidence):

| Board | Commands, rules re-taken, verdicts | Readings | Layout-entry reasons before, after | What holds layout entry after |
|---|---|---|---|---|
| A | 12, 13, 14 | 11 PASS; `inhibit_chain_a` FAIL (1 failed, 2 undecided of 9); `edge_length` INCONCLUSIVE (114 of 290 signal nets undecided); `clock_check` INCONCLUSIVE, read as not applicable (no crystal) | 18, 7 | SI-001 INCONCLUSIVE, RF-002 FAIL; decision 31's review; FEA-002, FEA-004, FEA-006, FEA-007 |
| B | 12, 12, 13 | 11 PASS (`intent_rails` 59 checks, `energy_chain_b` 3 stages, `clock_check`); `inhibit_chain_b` FAIL (11 failed, 3 undecided of 20); `edge_length` INCONCLUSIVE (532 of 882) | 17, 7 | SI-001 INCONCLUSIVE, RF-002 FAIL; FEA-001, FEA-002, FEA-003, FEA-006, FEA-007 |
| C | 9, 9, 10 | 7 PASS; `intent_rails` FAIL (5 of 7 checks; C_DVDD, EPD_VCC, LED_RAIL and LED_RAIL_SW declared by no rail; 11 nets undecided); `inhibit_chain_c` FAIL (1 of 6); `edge_length` INCONCLUSIVE (33 of 134) | 11, 5 | PWR-001 FAIL, SI-001 INCONCLUSIVE, RF-002 FAIL; FEA-002, FEA-006 |
| D | 10, 10, 11 | 8 PASS; `intent_rails` INCONCLUSIVE (RLY_K undecided, 0 failed of 7); `inhibit_chain_d` FAIL (2 of 8); `edge_length` INCONCLUSIVE (27 of 135) | 16, 8 | PWR-001 and SI-001 INCONCLUSIVE, RF-002 FAIL; decision 31's review; FEA-002, FEA-004, FEA-006, FEA-007 |
| E | 12, 13, 14 | 12 PASS (`inhibit_chain_e`, the first RF-002 verdict on E, among them); `intent_rails` INCONCLUSIVE (FAN1_SW and FAN2_SW undecided, 0 failed of 16); `edge_length` INCONCLUSIVE (37 of 82) | 17, 5 | PWR-001 and SI-001 INCONCLUSIVE; decision 31's review; FEA-006, FEA-007 |
| P | 12, 13, 14 | 11 PASS (`inhibit_chain_p` among them); `intent_rails` FAIL (6 of 11; BAT_F, PBI, SEC_VDD, SW and VCC_F declared by no rail); `pack_protection` FAIL (1 of 45); `edge_length` INCONCLUSIVE (22 of 44) | 16, 6 | PWR-001 FAIL, SI-001 INCONCLUSIVE, BAT-001 FAIL; FEA-005, FEA-006, FEA-007 |
| E5 | 6, 6, 7 | 7 PASS | 6, 2 | INT-001 PASS, still AWAITING_REVALIDATION (UNBOUND); FEA-007 |

In total the layout-entry reasons went from 101 to 40 (the clean clone's "before" equalled the committed page's).
After: 15 current readings that are not a PASS, 1 deciding verification (E5's INT-001), 3 decision 31's review on A, D
and E (its TRN-001 requirement is met: TRN-001 PASS on current evidence on every board), 21 the layout-entry stages
of FEA-001 to FEA-007. The row "a re-take alone" is empty. No board is ready for layout, before or after. The 278
gitignored readings the run wrote are kept outside the tree as a tar with its sha256 and manifest; main's working
checkout rendered the same layout-entry test, 81 current-candidate rows and 66 PASS on the current candidate
(`5ca81eea`). The historical mixed-revision aggregate is not a readiness figure and is not repeated here.

**The trial (how the driver was first verified).** The figures below are the trial's, on `a8652172`, before board B's
round 8, set 4 and set 5, and before FEA-007 existed (it joined at `c351115d`); the consolidated re-take above is the
current evidence. The commands above were run between 09:13 and 09:21 UTC on 27 September 2026 on the rented
64-core Ubuntu 24.04 host with KiCad 9.0.9 and Python 3.12.3, in a clean clone of main at `a8652172` (the H1 commit;
`git status` empty), built from that host's own clone of an earlier main plus an incremental git bundle, with the driver
copied in as the only untracked file (its code as committed; the committed file differs only in its docstring, and it
prints the same plan byte for byte). `rules_status.py` was also run three times before the re-take. Times: the plan
under 1 s; the run 113 s for 73 commands (11 to 22 s per board: `check_contracts.py` about 6 s and `erc_gate.py --run`
1.4 to 4.8 s of each); each `rules_status.py` 13 to 15 s; `rules_render.py` 18 s. The same run with
`--verdict-dir /root/rtk/vd` wrote the same 83 readings with the same results and touched none of the tree's evidence
folders. The clone was deleted afterwards; no reading of it was copied anywhere.

Plan size: 73 commands over 7 boards (A 12, B 12, C 9, D 10, E 12, E5 6, P 12), 76 rule-board pairs re-taken, 14
desk-review pairs listed, 83 verdicts. The results, per board (a FAIL or an INCONCLUSIVE is the design's or its
declarations' answer, now on current evidence, not the driver's):

| Board | Commands, rules re-taken, verdicts | Readings written | Layout-entry reasons before, after | What still holds layout entry |
|---|---|---|---|---|
| A | 12, 13, 14 | 14: 10 PASS; `intent_rails` FAIL (9 of 39 checks), `inhibit_chain_a` FAIL (1 failed, 3 undecided of 9), `edge_length` INCONCLUSIVE (118 of 283 signal nets undecided), `clock_check` INCONCLUSIVE, which `rules_status` reads as not applicable (no crystal) | 17, 7 | PWR-001 FAIL, SI-001 INCONCLUSIVE, RF-002 FAIL; decision 31's review requirement; FEA-002, FEA-004, FEA-006 |
| B | 12, 12, 13 | 13: 9 PASS; `intent_rails` FAIL (29 of 70), `energy_chain_b` FAIL (B_PANEL_5V: 2.0 A protection on a 1.2 A conductor), `inhibit_chain_b` FAIL (15 of 20), `edge_length` INCONCLUSIVE (492 of 835 undecided) | 16, 8 | PWR-001, PWR-003 and RF-002 FAIL, SI-001 INCONCLUSIVE; FEA-001, FEA-002, FEA-003, FEA-006 |
| C | 9, 9, 10 | 10: 7 PASS; `intent_rails` FAIL (5 of 7), `inhibit_chain_c` FAIL (1 failed, 1 undecided of 6), `edge_length` INCONCLUSIVE (33 of 134) | 11, 5 | PWR-001 and RF-002 FAIL, SI-001 INCONCLUSIVE; FEA-002, FEA-006 |
| D | 10, 10, 11 | 11: 8 PASS; `intent_rails` FAIL (10 of 16), `inhibit_chain_d` INCONCLUSIVE (2 undecided of 8), `edge_length` INCONCLUSIVE (27 of 135) | 15, 7 | PWR-001 FAIL, SI-001 and RF-002 INCONCLUSIVE; decision 31's review requirement; FEA-002, FEA-004, FEA-006 |
| E | 12, 13, 14 | 14: 12 PASS (`inhibit_chain_e` among them); `intent_rails` FAIL (6 of 20), `edge_length` INCONCLUSIVE (36 of 82) | 16, 4 | PWR-001 FAIL, SI-001 INCONCLUSIVE; decision 31's review requirement; FEA-006 |
| E5 | 6, 6, 7 | 7: 7 PASS | 5, 1 | INT-001: PASS, still AWAITING_REVALIDATION (UNBOUND) |
| P | 12, 13, 14 | 14: 11 PASS (`inhibit_chain_p` among them); `intent_rails` FAIL (6 of 11), `pack_protection` FAIL (9 of 9 functions have firmware thresholds, no second protector, no chemical fuse), `edge_length` INCONCLUSIVE (22 of 44) | 15, 5 | PWR-001 and BAT-001 FAIL, SI-001 INCONCLUSIVE; FEA-005, FEA-006 |

In total the layout-entry reasons went from 95 to 37, and the page's row "a re-take alone" (63 at H1) is empty: 18
reasons are current readings that are not a PASS (board streams), 3 are decision 31's review requirement on boards A,
D and E, 15 are the layout-entry stages of the feasibility blockers of that commit, FEA-001 to FEA-006 (FEA-007, the
seventh, was added later; the re-take above counts FEA-001 to FEA-007), and 1 is E5's INT-001. That is the
only schematic-phase reading of the set that a re-take leaves AWAITING_REVALIDATION: the coverage map reads
`check_contracts`'s set verdict for it, which records every netlist it read and no board file of E5 (it has none to
read), so it cannot bind; `block_contract.py` writes `check_contracts_e5` from E5's board file and board A's, and the
rule can bind once the coverage map names that per-board verdict (a change for the registry writer, through an apply
script). No board is ready for layout, before or after. The historical mixed-revision aggregate of `rules_status.py`
went from PASS 188, FAIL 38, INCONCLUSIVE 112 to PASS 190, FAIL 41, INCONCLUSIVE 107 of 338 (the first run before the
re-take read 181 and 119: see above); it is not a readiness figure.

The "before" above is the clean clone's, which holds only tracked readings. The committed `CURRENT-EVIDENCE.md` was
rendered in a working checkout that also holds gitignored readings under `out/`, so a row's result can differ from a
clean clone's: board A's and B's TRN-001 read FAIL there and PASS in the clean clone, both awaiting revalidation, and the
per-board reason counts were the same. After the re-take TRN-001 reads PASS on current evidence on all seven boards.

**Choices taken by the session in this driver** (under the owner's standing rule of 26 September 2026; ruled by the
session, not by the owner; each is reversed by the edit named):

- `--routed` is refused without `--in-place`: `routed/` is tracked evidence, and a copy there from a staged run would
  put readings of copies into the tree. Reversed by removing the `routed` clause of `check_call`.
- The set-level writers (`energy_chain.py`, `check_contracts.py`, `interfaces.py`) run once per board, as
  `gate_sweep.sh` runs them, so each board's evidence directory holds the reading its rules are read from, at about
  9 s per board. Reversed by running them once and copying their verdicts to each board.
- `--routed` copies `edge_length.table.json` with the `edge_length` verdict, only when the same step wrote it, as
  `gate_sweep.sh` copies it. Reversed by emptying `COMPANIONS`.
- An unknown or incomplete argument is refused (a misspelt `--in-place` is never read as "not in place"), and `--json`
  puts the result alone on stdout. Reversed in `main`.
