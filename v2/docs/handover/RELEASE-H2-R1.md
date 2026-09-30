# Handover release H2-R1: what it is and how to check it

Written 30 September 2026 (MESHSAT-1357) by the scrub of public files (`v2/docs/records/scrub/`), from the build's own figures (`reissue_snapshots.py build`). **H2-R1 is a redaction reissue of H2. It changes no engineering content and supersedes H2, which stays in `v2/release/handover/` byte for byte as published.** Everything recorded in `v2/docs/handover/RELEASE-H2.md` about H2's layers, reviews, checks and errata holds for H2-R1 unchanged. Nothing in it has been built, ordered, powered or measured.

**Why.** The owner's rule is that public files carry no internal host names, user paths or addresses. H2 carried the runner's path, a session scratch path or a host name in 6 file(s). The owner's words of 29 September 2026: "Reissue affected handover snapshots with new version records and hashes rather than silently modifying accepted releases. This instruction does not authorize rewriting Git history."

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H2-R1.zip` (with `H2-R1.zip.sha256` and `H2-R1.MANIFEST.tsv` beside it) |
| sha256 | `e12a6f1cc0066e0a195210ae1fd0323d4309fa3c046a5ae937941106b341a7ee` |
| Size | 51,910,286 bytes, 2234 entries (the same files as H2); the cap of `pack.yaml` is 52,428,800 bytes |
| Manifest | `H2-R1.MANIFEST.tsv`, sha256 `933dcb1b76ca6a31108a231f007b5085917d4386cbd5aee96ed175d274757243`, a byte copy of the ZIP's `MANIFEST.tsv` |
| Supersedes | `v2/release/handover/H2.zip`, sha256 `20072be74852ec56d818d094d150a382143d95527dd28599b22eee84c3a5cf35` |
| Source commit | `b290170750bf26fb04a12aad0fbd01a38fa7e1d7`, the redaction commit (every file in the ZIP is its blob): its only parent is H2's source commit `b89b50b4421fd882967b390a09c21dbd307ca98e`, and it changes the files below and `v2/docs/handover/START-HERE.md` |
| Snapshot commit | the commit of the scrub's set that adds this ZIP, its checksum, its manifest and this page |
| Builder | `v2/ecad/tools/handover_pack.py` sha256 `fd7e353f0fcaaba2a166997ad68403321a280368b8513100d4ae4e7002f7f5fe`, the packer that built H3; `SOURCE.txt` names it as the builder that ran, beside the older builder the commit holds |
| Public | the redaction commit reaches main's history through the merge that keeps main's tree (`git merge -s ours`) in the scrub's set; `SOURCE.txt` marks it `public no` because it was built before that merge was published |
| Check | `sha256sum -c H2-R1.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H2-R1.zip` |
| Rebuild | `python3 v2/ecad/tools/handover_pack.py build --commit b290170750bf --version H2-R1 --zip-only --out <folder>`: the ZIP is deterministic per host; across hosts compare `H2-R1.MANIFEST.tsv` |

## What differs from H2

`MANIFEST.tsv` of H2-R1 has the same 2233 rows as H2's. 2226 are identical in every column. The others:

| File | sha256/16 in H2 | sha256/16 in H2-R1 | Why |
|---|---|---|---|
| `v2/docs/MESHSAT-709-geometry-appendix.md` | `5e942dd41e9e4ed0` | `852736b661a805e3` | 3 replacements: runner path prefix |
| `v2/docs/respin-footprints-2026-09-04.md` | `469a42d3360979dd` | `9b1a295133300fe2` | 1 replacement: laptop host name |
| `v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json` | `c2b8c4d55fd78f87` | `9787f6767d5428d7` | 1 replacement: session temp path |
| `v2/ecad/pcb-e5-block/routed/ledger_verify.verdict.json` | `9691276029e09fab` | `8ef5495682e031a8` | 1 replacement: runner path prefix |
| `START-HERE.md` and `v2/docs/handover/START-HERE.md` | | | opened by a box naming H2, why it is superseded, the table above and the files left |
| `SOURCE.txt` | | | the redaction commit, its tree and date, the builder and the tool versions of the host that built H2-R1 |

A hash that a page of H2-R1 cites for a changed file names H2's bytes; H2 and the public repository at `b89b50b4` hold them. Each replacement is listed by file, line and token class in `v2/docs/records/scrub/MAP.md`.

## Left as H2 carried them

The scrub of the tree leaves these files as they are (`v2/docs/records/scrub/README.md`, "What was left"), and H2-R1 keeps them the same way, so every hash that a page or a check cites for them still holds:

- `v2/docs/feasibility/fab/out/pulldowns.txt`: a reading FAILOVER-FABRIC.md cites by sha256; the requirements registry binds that page by sha, so a re-pin would change the baselined registry.
- `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md`: a filed review record of layer 1 whose sha256/16 the release records of H2 and H3, the H2 and H3 handover counts, the H3 coherence check, two later reviews and a candidate patch cite.

## What was not done

- No engineering file of H2 changed: no schematic, netlist, generator, board table, checking tool, registry, export or maker document. The redacted files are pages, records and readings, and in each only a path or a host name changed.
- No review or check read H2-R1 again: it is H2 with the redactions listed above, and what H2's records say was reviewed, repeated or found applies to it unchanged.
- The repository's history was not rewritten: H2's files and every earlier revision keep the old values there.
