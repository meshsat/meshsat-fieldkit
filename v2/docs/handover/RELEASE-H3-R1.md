# Handover release H3-R1: what it is and how to check it

Written 30 September 2026 (MESHSAT-1357) by the scrub of public files (`v2/docs/records/scrub/`), from the build's own figures (`reissue_snapshots.py build`). **H3-R1 is a redaction reissue of H3. It changes no engineering content and supersedes H3, which stays in `v2/release/handover/` byte for byte as published.** Everything recorded in `v2/docs/handover/RELEASE-H3.md` about H3's layers, reviews, checks and errata holds for H3-R1 unchanged. Nothing in it has been built, ordered, powered or measured.

**Why.** The owner's rule is that public files carry no internal host names, user paths or addresses. H3 carried the runner's path, a session scratch path or a host name in 8 file(s). The owner's words of 29 September 2026: "Reissue affected handover snapshots with new version records and hashes rather than silently modifying accepted releases. This instruction does not authorize rewriting Git history."

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H3-R1.zip` (with `H3-R1.zip.sha256` and `H3-R1.MANIFEST.tsv` beside it) |
| sha256 | `3b5d9b79883adf43837b19cb50ee083de1be8238480179724e6ac3dc205e7525` |
| Size | 52,203,750 bytes, 2275 entries (the same files as H3); the cap of `pack.yaml` is 52,428,800 bytes |
| Manifest | `H3-R1.MANIFEST.tsv`, sha256 `c74930639fb009eb319e612ba6e00f1f78f94595041e5caf6616cece9c5ed724`, a byte copy of the ZIP's `MANIFEST.tsv` |
| Supersedes | `v2/release/handover/H3.zip`, sha256 `6922a96d732442e99a65d8db3f0734378bd7ea636894fca283a4b3ca424dd07a` |
| Source commit | `329fcfa64bdf27b86175ecdced361d954cab48e4`, the redaction commit (every file in the ZIP is its blob): its only parent is H3's source commit `75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669`, and it changes the files below and `v2/docs/handover/START-HERE.md` |
| Snapshot commit | the commit of the scrub's set that adds this ZIP, its checksum, its manifest and this page |
| Builder | `v2/ecad/tools/handover_pack.py` sha256 `fd7e353f0fcaaba2a166997ad68403321a280368b8513100d4ae4e7002f7f5fe`, the packer that built H3 |
| Public | the redaction commit reaches main's history through the merge that keeps main's tree (`git merge -s ours`) in the scrub's set; `SOURCE.txt` marks it `public no` because it was built before that merge was published |
| Check | `sha256sum -c H3-R1.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H3-R1.zip` |
| Rebuild | `python3 v2/ecad/tools/handover_pack.py build --commit 329fcfa64bdf --version H3-R1 --zip-only --out <folder>`: the ZIP is deterministic per host; across hosts compare `H3-R1.MANIFEST.tsv` |

## What differs from H3

`MANIFEST.tsv` of H3-R1 has the same 2274 rows as H3's. 2266 are identical in every column. The others:

| File | sha256/16 in H3 | sha256/16 in H3-R1 | Why |
|---|---|---|---|
| `v2/docs/EXECUTION-PLAN.md` | `b5ca0386d7ee5712` | `e768e25cfc0555e4` | 1 replacement: runner path prefix |
| `v2/docs/MESHSAT-709-geometry-appendix.md` | `5e942dd41e9e4ed0` | `852736b661a805e3` | 3 replacements: runner path prefix |
| `v2/docs/respin-footprints-2026-09-04.md` | `469a42d3360979dd` | `9b1a295133300fe2` | 1 replacement: laptop host name |
| `v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json` | `c2b8c4d55fd78f87` | `9787f6767d5428d7` | 1 replacement: session temp path |
| `v2/ecad/pcb-e5-block/routed/ledger_verify.verdict.json` | `9691276029e09fab` | `8ef5495682e031a8` | 1 replacement: runner path prefix |
| `START-HERE.md` and `v2/docs/handover/START-HERE.md` | | | opened by a box naming H3, why it is superseded, the table above and the files left |
| `SOURCE.txt` | | | the redaction commit, its tree and date, the builder and the tool versions of the host that built H3-R1 |

A hash that a page of H3-R1 cites for a changed file names H3's bytes; H3 and the public repository at `75ad6ee5` hold them. Each replacement is listed by file, line and token class in `v2/docs/records/scrub/MAP.md`.

## Left as H3 carried them

The scrub of the tree leaves these files as they are (`v2/docs/records/scrub/README.md`, "What was left"), and H3-R1 keeps them the same way, so every hash that a page or a check cites for them still holds:

- `v2/docs/feasibility/fab/out/pulldowns.txt`: a reading FAILOVER-FABRIC.md cites by sha256; the requirements registry binds that page by sha, so a re-pin would change the baselined registry.
- `v2/docs/records/handover/H2-USABILITY-CHECK.md`: a filed check whose sha256 records/README.md pins.
- `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md`: a filed review record of layer 1 whose sha256/16 the release records of H2 and H3, the H2 and H3 handover counts, the H3 coherence check, two later reviews and a candidate patch cite.

## What was not done

- No engineering file of H3 changed: no schematic, netlist, generator, board table, checking tool, registry, export or maker document. The redacted files are pages, records and readings, and in each only a path or a host name changed.
- No review or check read H3-R1 again: it is H3 with the redactions listed above, and what H3's records say was reviewed, repeated or found applies to it unchanged.
- The repository's history was not rewritten: H3's files and every earlier revision keep the old values there.
