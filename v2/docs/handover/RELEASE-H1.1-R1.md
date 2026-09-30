# Handover release H1.1-R1: what it is and how to check it

Written 30 September 2026 (MESHSAT-1357) by the scrub of public files (`v2/docs/records/scrub/`), from the build's own figures (`reissue_snapshots.py build`). **H1.1-R1 is a redaction reissue of H1.1. It changes no engineering content and supersedes H1.1, which stays in `v2/release/handover/` byte for byte as published.** Everything recorded in H1.1's own `START-HERE.md`, `LAYER-STATUS.md` and `v2/docs/handover/H1.1-RESPONSE.md` (H1.1 has no release page) about H1.1's layers, reviews, checks and errata holds for H1.1-R1 unchanged. Nothing in it has been built, ordered, powered or measured.

**Why.** The owner's rule is that public files carry no internal host names, user paths or addresses. H1.1 carried the runner's path, a session scratch path or a host name in 8 file(s). The owner's words of 29 September 2026: "Reissue affected handover snapshots with new version records and hashes rather than silently modifying accepted releases. This instruction does not authorize rewriting Git history."

## The package

| Item | Value |
|---|---|
| File | `v2/release/handover/H1.1-R1.zip` (with `H1.1-R1.zip.sha256` and `H1.1-R1.MANIFEST.tsv` beside it) |
| sha256 | `5d6d018b8698aacf095ac06090d295b5cd494331901838c46a64970e96c44994` |
| Size | 51,145,129 bytes, 1660 entries (the same files as H1.1); the cap of `pack.yaml` is 52,428,800 bytes |
| Manifest | `H1.1-R1.MANIFEST.tsv`, sha256 `47b6060ddc2988c152f939e68e6f5118a3974ba9647f5e882dd209695afd3428`, a byte copy of the ZIP's `MANIFEST.tsv` |
| Supersedes | `v2/release/handover/H1.1.zip`, sha256 `fc563395439db348d070e5ae710014d354b907dc886287f6734f742e4e6ff6ca` |
| Source commit | `8dfdcb6217a045e09f2d0ad6d2a938c1fccc8b81`, the redaction commit (every file in the ZIP is its blob): its only parent is H1.1's source commit `98ce9f83269ef61d21b317d8eabbdf35a878923e`, and it changes the files below and `v2/docs/handover/START-HERE.md` |
| Snapshot commit | the commit of the scrub's set that adds this ZIP, its checksum, its manifest and this page |
| Builder | `v2/ecad/tools/handover_pack.py` sha256 `fd7e353f0fcaaba2a166997ad68403321a280368b8513100d4ae4e7002f7f5fe`, the packer that built H3; `SOURCE.txt` names it as the builder that ran, beside the older builder the commit holds |
| Public | the redaction commit reaches main's history through the merge that keeps main's tree (`git merge -s ours`) in the scrub's set; `SOURCE.txt` marks it `public no` because it was built before that merge was published |
| Check | `sha256sum -c H1.1-R1.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify H1.1-R1.zip` |
| Rebuild | `python3 v2/ecad/tools/handover_pack.py build --commit 8dfdcb6217a0 --version H1.1-R1 --zip-only --out <folder>`: the ZIP is deterministic per host; across hosts compare `H1.1-R1.MANIFEST.tsv` |

## What differs from H1.1

`MANIFEST.tsv` of H1.1-R1 has the same 1659 rows as H1.1's. 1651 are identical in every column. The others:

| File | sha256/16 in H1.1 | sha256/16 in H1.1-R1 | Why |
|---|---|---|---|
| `v2/docs/MESHSAT-709-geometry-appendix.md` | `5e942dd41e9e4ed0` | `852736b661a805e3` | 3 replacements: runner path prefix |
| `v2/docs/diagrams/README.md` | `c0ade5c7889b3786` | `f6e344fd96cf89ae` | 1 replacement: host name |
| `v2/docs/respin-footprints-2026-09-04.md` | `469a42d3360979dd` | `9b1a295133300fe2` | 1 replacement: laptop host name |
| `v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json` | `c2b8c4d55fd78f87` | `9787f6767d5428d7` | 1 replacement: session temp path |
| `v2/ecad/pcb-e5-block/routed/ledger_verify.verdict.json` | `9691276029e09fab` | `8ef5495682e031a8` | 1 replacement: runner path prefix |
| `START-HERE.md` and `v2/docs/handover/START-HERE.md` | | | opened by a box naming H1.1, why it is superseded, the table above and the files left |
| `SOURCE.txt` | | | the redaction commit, its tree and date, the builder and the tool versions of the host that built H1.1-R1 |

A hash that a page of H1.1-R1 cites for a changed file names H1.1's bytes; H1.1 and the public repository at `98ce9f83` hold them. Each replacement is listed by file, line and token class in `v2/docs/records/scrub/MAP.md`.

## Left as H1.1 carried them

The scrub of the tree leaves these files as they are (`v2/docs/records/scrub/README.md`, "What was left"), and H1.1-R1 keeps them the same way, so every hash that a page or a check cites for them still holds:

- `v2/docs/feasibility/fab/out/pulldowns.txt`: a reading FAILOVER-FABRIC.md cites by sha256; the requirements registry binds that page by sha, so a re-pin would change the baselined registry.
- `v2/docs/handover/candidates/hc3.patch`: the H1.1 candidate patch as it was reviewed; candidates/README.md pins its sha256.
- `v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md`: a filed review record of layer 1 whose sha256/16 the release records of H2 and H3, the H2 and H3 handover counts, the H3 coherence check, two later reviews and a candidate patch cite.

## What was not done

- No engineering file of H1.1 changed: no schematic, netlist, generator, board table, checking tool, registry, export or maker document. The redacted files are pages, records and readings, and in each only a path or a host name changed.
- No review or check read H1.1-R1 again: it is H1.1 with the redactions listed above, and what H1.1's records say was reviewed, repeated or found applies to it unchanged.
- The repository's history was not rewritten: H1.1's files and every earlier revision keep the old values there.
