# Approved amendments to the Layer 1 to 3 baseline (handover of 10 October 2026)

The baselines in this folder are the accepted texts. The two items below were approved later and change what those texts
mean; each is stated with its exact recorded scope and its status. Nothing here is a new approval: this page only records
where the owner's approvals already stand. Wherever an accepted text conflicts with an item below, the item governs.

## A-1. The second battery pack (owner, 9 October 2026, 18:52:19 CEST)

**Source (copied as received):** `v2/docs/handover/OWNER-INSTRUCTION-2026-10-09-AS-RECEIVED.md`, **Part 6**, in this
folder. The file comes from the candidate commit `a6274bf77f2c6d3ffa898e34f7bfa47aede3bda4`, which carries the filing but
was never promoted to `main`; the owner's words in it are: "ok second battery approved". The relayed instruction reads:
"Owner APPROVES engineering the second battery inside the unchanged Peli1450, as two identical and interchangeable
complete packs in the discussed4S3P35E baseline."

**What it approves, exactly:**
- engineering a **second** battery pack **inside the unchanged Peli 1450** case;
- as **two identical, interchangeable, complete packs**, each the 4S3P Samsung INR18650-35E block of the D-06 baseline with
  its own pack board (protection and gauge);
- it **amends D-06** (one pack in the east pocket) and **takes up D-01's deferred second pack**. The accepted texts that
  read "D-06's one pack" (for example `l3r2.yaml`, `REQUIREMENTS-L3-R2.md`, `DEFINITION-REISSUE-DRAFT.md`) are read with
  this amendment; the single-pack restriction is **not** current.

**What it does not approve, and what it does not establish:**
- it is permission to engineer, **not proof of fit**: the second pocket's room for a complete pack with its board and
  wiring, the per-pack protection, the way two packs combine, cell qualification (U-01) and the record conflict on the
  buildable volume (268.9 Wh in appendix 32.62 against 215.8 Wh in a later pocket-fit check) stay open;
- it approves **no** reduced service, relaxed runtime (REQ-072 stays as written), altered safety requirement, hot-swap,
  larger case, supplier contact, purchase or fabrication;
- the copper note in the same message was a question, not a selection (copper became an engineering choice under the
  delegation below).

**Status:** recorded as an owner ruling; not yet written into the registry or the definition texts (a Layer 3 registry
amendment entry is owed; see `04_Review_and_Open_Issues.md` I-02).

## A-2. The definition re-issue on the owner's Layer 3 answers (D-32 to D-38, 30 September 2026)

**Source:** `v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md` and `DEFINITION-REISSUE-DRAFT.md` in this folder.
The owner's rulings D-32 to D-37 change passages of `CONOPS.md` and `PRODUCT-BRIEF.md` (among them: the 48 to 72 hour
runtime as a design objective under a stated operating profile, REQ-072; battery storage inside the Peli 1450; no external
battery; battery and solar required; HF and the tablet functions kept, optional tablet charging reducing endurance).

**Status:** authorised by owner ruling D-38; its acceptance is the targeted independent review of Layer 3's closure,
recorded CLOSED (L3-C26). It is **not yet written into the baselined documents**: the re-stamp of `CONOPS.md` and
`PRODUCT-BRIEF.md` is closure item **L3-C63**, an integrator item still open. Until it is done, the change record governs
wherever the two baselined texts differ from it.

## Later process rulings (not amendments of the definition or the requirements)

- 9 October 2026, 18:55:30 (same file, Part 7): routine engineering implementation choices (copper weights, stackup and
  routing details, their validation) belong to the engineering team; only a real change to requirements or service,
  product scope, protected external interfaces or the enclosure, or spending, contact or fabrication authority goes to the
  owner.
- 9 October 2026, Parts 1 to 5 of the same file, and the owner's instructions of 10 October (delivery-first execution;
  this handover): they govern how the agentic process worked and do not change any requirement.
