# MeshSat field kit V2: engineering handover of Layers 1 to 3 (10 October 2026)

**This is an engineering handover, not a fabrication approval.** Prototype framing applies throughout: no V2 board has
been built, ordered or measured, nothing here has been field deployed, and no software test in this repository qualifies
hardware, validates a physical fit or authorises fabrication.

## The product in one paragraph

The MeshSat field kit V2 is a portable communications gateway in a Peli 1450 case. It bonds LoRa mesh, Iridium satellite
messaging, cellular, Wi-Fi, APRS radio and HF behind three redundant Compute Module 5 slots, with an operator panel, a
display, a battery store and solar input inside the sealed case. The full definition is the product brief (Layer 1) and
the concept of operations (Layer 2); the requirements registry (Layer 3) states what the kit must do and how each item is
verified.

## What is supplied

| Folder or file | Content |
|---|---|
| `01_Product_Definition/` | Layer 1: the product brief, its definition status page, the glossary, and the review records it was accepted on |
| `02_Concept_of_Operations/` | Layer 2: the concept of operations, the operating envelope, the test plan, and the review records |
| `03_Requirements/` | Layer 3: the requirements registry (`l3r2.yaml`) and its rendered pages, the owner decisions, the reconciliation, the definition re-issue and its change record, the owner brief of 30 September, the requirements trace, the engineering questions, the layer status record, the acceptance evidence, every record the requirement pages link to, and `APPROVED-AMENDMENTS.md` |
| `04_Review_and_Open_Issues.md` | this handover's final review: each material issue, its consequence and the next engineering action |
| `05_Engineer_Takeover.md` | what to do next from Layer 4, and what Layer 4 work exists (working input, not an accepted architecture) |
| `06_Source_Manifest.md` | every supplied file with its repository path, source commit, blob and checksum |
| `CHECKSUMS.sha256` | sha256 of every supplied file except itself |

Inside each section folder the files sit at their **repository paths** (for example
`03_Requirements/v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md`), byte-identical to the source commit, so the documents'
own relative links resolve inside the folder. Many documents also cite repository paths in backticks (for example
`v2/docs/records/...` or `reviews/...`, relative to `v2/docs/`); those are citations, not links, and resolve in this
same repository at the source commit named in `06_Source_Manifest.md`. Makers' datasheets are not copied; they are in
the repository under `v2/vendor/`.

## Accepted versus provisional

| Layer | Verified status at this handover | Basis |
|---|---|---|
| 1. Product definition | **Accepted baseline**, with an approved but not yet written-in amendment (A-2) and a later owner approval (A-1, the second battery) | `PRODUCT-BRIEF.md` BASELINED at `a9f212c7` (definition baseline `6b2a9965`), AI release checks; unchanged since |
| 2. Concept of operations | **Accepted baseline**, with the same two amendments | `CONOPS.md` BASELINED at `a9f212c7` (definition baseline `79963b3b`), AI release checks; unchanged since |
| 3. Requirements | **Accepted baseline** at `3b4b92cf` (owner authorisation D-39; the owner's independent reviewer read it READY for Layer 4 work and handover), with A-1 and A-2 | `l3r2.yaml` `baseline_acceptance`; one stale status row in its rendered page (issue I-03) |

All reviews named in these documents are AI reviews or AI checks, labelled as such; none is a qualified engineering
review. "Accepted" means accepted as a requirements and definition baseline. **It does not mean the current design meets
the requirements**: several do not, and `04_Review_and_Open_Issues.md` says which. A requirement stays valid when the
design fails it.

## Reading order

1. This page, then `03_Requirements/APPROVED-AMENDMENTS.md` (what changed after the baselines).
2. `01_Product_Definition/v2/docs/PRODUCT-BRIEF.md`, then `.../handover/DEFINITION-STATUS.md` and `.../handover/GLOSSARY.md`.
3. `02_Concept_of_Operations/v2/docs/CONOPS.md`, then `OPERATING-ENVELOPE.md` and `TEST-PLAN.md`.
4. `03_Requirements/v2/docs/handover/layer3/REQUIREMENTS-L3-R2.md` (the readable registry), with `l3r2.yaml` (its source),
   `OWNER-DECISIONS-L3.md`, `DEFINITION-CHANGE-RECORD-L3.md` and `OWNER-INSTRUCTION-2026-09-30.md` (the owner brief).
5. `04_Review_and_Open_Issues.md`, then `05_Engineer_Takeover.md`.

## The takeover requested

The receiving engineer takes responsibility from **Layer 4 (system architecture) onward**, on the Layer 1 to 3 baseline
with its amendments. Earlier Layer 4 to 9 material produced by the agentic process is working input only: some of it is
integrated on `main`, more is reviewed but unintegrated, and none of it is an accepted architecture
(`05_Engineer_Takeover.md`). Routine technical choices (components, copper, stackup, routing, methods) are the engineer's;
the genuine product-scope questions are listed in `04_Review_and_Open_Issues.md` section 3.

Prepared 10 October 2026 by the coordinating agent session of the MESHSAT-1357 programme, from repository commit
`c20c4b629ff4f4d06f82ef3fe98d59d313bab497` (main) plus one owner-instruction file from the unpromoted candidate
`a6274bf77f2c6d3ffa898e34f7bfa47aede3bda4`.
