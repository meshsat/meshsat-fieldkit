# Handover release H1-R1: what it is and how to check it

Written 30 September 2026 (MESHSAT-1357) by the scrub of public files (`v2/docs/records/scrub/`), from the build's own figures (`reissue_snapshots.py build`). **H1-R1 is a redaction reissue of H1. It changes no engineering content and supersedes H1, which stays in `v2/release/handover/` byte for byte as published.** Everything recorded in H1's own `START-HERE.md` and `LAYER-STATUS.md` (H1 has no release page) about H1's layers, reviews, checks and errata holds for H1-R1 unchanged. Nothing in it has been built, ordered, powered or measured.

**Why.** The owner's rule is that public files carry no internal host names, user paths or addresses. H1 carried the runner's path, a session scratch path or a host name in 7 file(s). The owner's words of 29 September 2026: "Reissue affected handover snapshots with new version records and hashes rather than silently modifying accepted releases. This instruction does not authorize rewriting Git history."

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H1-R1.zip` (with `H1-R1.zip.sha256` and `H1-R1.MANIFEST.tsv` beside it) |
| sha256 | `f8566e274af3371ea0cb3b98b1a18af4daf64078eb751e76ddd8a14d8f312686` |
| Size | 47,072,838 bytes, 1644 entries (the same files as H1); the cap of `pack.yaml` is 52,428,800 bytes |
| Manifest | `H1-R1.MANIFEST.tsv`, sha256 `808eb29beaf573b55de209bc7e34f6e9c45bb7d6b8fbacf022a52f034b61cd52`, a byte copy of the ZIP's `MANIFEST.tsv` |
| Supersedes | `v2/release/handover/H1.zip`, sha256 `10598fc8799212415b3bf5f81a58405bc592c5eb443bfae0d05c9fd900ac31c8` |
| Source commit | `a256fb5e48fa2b34c89ddd18d71824ae0d5ff678`, the redaction commit (every file in the ZIP is its blob): its only parent is H1's source commit `8a19fe295f4f77b67366854d1006e1feff228fef`, and it changes the files below and `v2/docs/handover/START-HERE.md` |
| Snapshot commit | the commit of the scrub's set that adds this ZIP, its checksum, its manifest and this page |
| Builder | `v2/ecad/tools/handover_pack.py` sha256 `fd7e353f0fcaaba2a166997ad68403321a280368b8513100d4ae4e7002f7f5fe`, the packer that built H3; `SOURCE.txt` names it as the builder that ran, beside the older builder the commit holds |
| Public | the redaction commit reaches main's history through the merge that keeps main's tree (`git merge -s ours`) in the scrub's set; `SOURCE.txt` marks it `public no` because it was built before that merge was published |
| Check | `sha256sum -c H1-R1.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H1-R1.zip` |
| Rebuild | `python3 v2/ecad/tools/handover_pack.py build --commit a256fb5e48fa --version H1-R1 --zip-only --out <folder>`: the ZIP is deterministic per host; across hosts compare `H1-R1.MANIFEST.tsv` |

## What differs from H1

`MANIFEST.tsv` of H1-R1 has the same 1643 rows as H1's. 1635 are identical in every column. The others:

| File | sha256/16 in H1 | sha256/16 in H1-R1 | Why |
|---|---|---|---|
| `v2/docs/MESHSAT-709-geometry-appendix.md` | `5e942dd41e9e4ed0` | `852736b661a805e3` | 3 replacements: runner path prefix |
| `v2/docs/diagrams/README.md` | `c0ade5c7889b3786` | `f6e344fd96cf89ae` | 1 replacement: host name |
| `v2/docs/respin-footprints-2026-09-04.md` | `469a42d3360979dd` | `9b1a295133300fe2` | 1 replacement: laptop host name |
| `v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json` | `c2b8c4d55fd78f87` | `9787f6767d5428d7` | 1 replacement: session temp path |
| `v2/ecad/pcb-e5-block/routed/ledger_verify.verdict.json` | `9691276029e09fab` | `8ef5495682e031a8` | 1 replacement: runner path prefix |
| `START-HERE.md` and `v2/docs/handover/START-HERE.md` | | | opened by a box naming H1, why it is superseded, the table above and the files left |
| `SOURCE.txt` | | | the redaction commit, its tree and date, the builder and the tool versions of the host that built H1-R1 |

A hash that a page of H1-R1 cites for a changed file names H1's bytes; H1 and the public repository at `8a19fe29` hold them. Each replacement is listed by file, line and token class in `v2/docs/records/scrub/MAP.md`.

## Left as H1 carried them

The scrub of the tree leaves these files as they are (`v2/docs/records/scrub/README.md`, "What was left"), and H1-R1 keeps them the same way, so every hash that a page or a check cites for them still holds:

- `v2/docs/feasibility/fab/out/pulldowns.txt`: a reading FAILOVER-FABRIC.md cites by sha256; the requirements registry binds that page by sha, so a re-pin would change the baselined registry.
- `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md`: a filed review record of layer 1 whose sha256/16 the release records of H2 and H3, the H2 and H3 handover counts, the H3 coherence check, two later reviews and a candidate patch cite.

## What was not done

- No engineering file of H1 changed: no schematic, netlist, generator, board table, checking tool, registry, export or maker document. The redacted files are pages, records and readings, and in each only a path or a host name changed.
- No review or check read H1-R1 again: it is H1 with the redactions listed above, and what H1's records say was reviewed, repeated or found applies to it unchanged.
- The repository's history was not rewritten: H1's files and every earlier revision keep the old values there.
