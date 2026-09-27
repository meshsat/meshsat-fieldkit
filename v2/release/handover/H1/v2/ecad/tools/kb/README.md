# The vendor datasheet knowledge base

A retrieval store over `v2/vendor/`, built 10 September 2026 (MESHSAT-862). It answers one
question: **which page of which vendor document should I read.** It is not on any path that judges
a board, and three separate mechanisms keep it there.

## Why this exists, and why it is shaped so defensively

The expensive mistakes in this project's record are not retrieval failures. They are verification
failures: a `TPS2065CDBV` sitting on a SOT-23-6 land for four board phases because a footprint key
was a claim nobody checked; a CM5 pin table whose `else: NC` fallback turned every PCIe net into a
one-pad orphan; a stripline impedance quoted from a closed form that reads 20 to 26 percent high.
Retrieval would have returned documents for all three and changed none of them.

So this store does not try to answer. It points at a page, prints the command that re-opens that
page, and says clearly when the part you asked about is not in it at all. The page is the answer.

## The three guards

1. **It cannot decide.** A retrieved passage is model-selected evidence, so it is capped at 0.75
   confidence, below the action threshold, and the cap is a `CHECK` constraint on the store's own
   `lookups` table (`ck_truth_cap`), not a number a caller is trusted to apply. Proved by a rejected
   write: an insert at 0.900 fails with `CONSTRAINT ck_truth_cap failed`.
2. **It cannot reach a verdict path.** No gate, check, finish or chain script may import it, and
   `tools/tests/test_kb_isolation.py` fails if one does. `kb_search.py` does not import `verdict.py`
   at all, so the thing that proposes evidence has no way to write a verdict about it. The topology
   agrees: boards are built and judged on a rented box that has no route to this store.
3. **It cannot present a retired part as current.** Every document carries the status of its vendor
   folder from `v2/vendor/vendor-status.txt`, declared with a reason and a ruling. A retired or
   V1-only document is pushed down the ranking and labelled in capitals, and when nothing current
   matches, the tool says so in those words rather than serving a retired page silently.

And the fourth, which is the one that matters most in practice:

4. **It says when the part is absent.** Every part-number-shaped token in the question is checked
   against the returned passages and against the whole store. Ask for the `TMUXHS4212` and the
   fused ranking will happily return the LT8705A's exposed-pad note and a TI mux's pin table, both
   real pages, both about something else. The tool prints:

   > `!! NO DOCUMENT IN THIS STORE MENTIONS TMUXHS4212.`

## Geometry, which is the other half of this folder

Half of what this project needs from `v2/vendor/` is not in a datasheet. The e-paper window, the case
ribs, the receptacle envelope: those live in STEP and DXF files, which are binary as far as search is
concerned, so the mechanical numbers in the record rested on whoever probed the model that day.

`geom_probe.py` reads them and writes the measurable facts beside each model as `<model>.geom.txt`,
which the store then indexes like any other document: the envelope, every hole diameter with its
count, and the pattern each hole group forms. STEP is ISO-10303-21 ASCII and DXF is group codes, so
this needs no CAD kernel and no venv, and it runs on the runner as well as on the box.

    python3 kb/geom_probe.py --selftest     # the WeAct hole pattern, the one number we can check
    python3 kb/geom_probe.py                # every model under v2/vendor/

The selftest is the point: the record established on 5 September, independently, that the WeAct 3.7
module's holes sit on 100.19 x 48.20 mm. The probe reproduces exactly that, so the tool is checked
against a fact rather than trusted.

**Four things it refuses to claim**, each one found by reading its own output and disbelieving it:

- **An assembly gets no envelope.** A STEP assembly holds every component in its own coordinates and
  places them through transforms this reader does not apply, so a raw box over its points is a number
  about nothing: the WeAct module, 105 x 54 mm, reads as 845 x 421 mm that way. The file says NOT
  MEASURED and gives the raw spread only as a labelled non-measurement. Hole patterns are still true
  *within* a component, which is why a module's mounting holes come out right.
- **Construction geometry is removed and counted.** The LimeSDR model puts 11.6 percent of its points
  at plus and minus 400,000 mm; the raw box reads 800 metres. The body is the box after points outside
  ten interquartile ranges are dropped, and the count of what was dropped is printed.
- **A DXF is a drawing sheet, not a part**, and its extents are the sheet with several views on it.
  Only the ENTITIES section is read: the HEADER uses the same group codes, and its `$EXTMIN`/`$EXTMAX`
  turned one Peli drawing into a part two hundred billion kilometres across.
- **Axes are the file's own.** A vendor model is often exported Y up and this reader does not turn it,
  so the three extents are sizes, not width, depth and height. And every number is a measurement of
  the file, never a specification: where the manufacturer publishes a drawing, the drawing wins.

## Using it

    python3 kb/kb_search.py "LG290P supply voltage and pin assignment" --k 6
    python3 kb/kb_search.py "SA868 transmit current" --vendor nicerf --json
    python3 kb/kb_search.py "Touch Display 2 dimensions" --all      # include retired and V1 docs

Each hit prints its file, its page, its status, and the `pdftotext -f N -l N` line that re-reads it.

## Keeping it honest

    python3 kb/kb_verify.py                 # coverage, embedding space and the gold set
    python3 kb/kb_verify.py --parts         # BOM parts this store holds no datasheet for
    python3 kb/kb_ingest.py --stage all     # rescan after adding or changing a vendor document

`kb_verify.py` writes `out/kb_verify.verdict.json` through `verdict.py`, and its exit code is the
verdict (0 PASS, 1 FAIL, 3 INCONCLUSIVE), so an unreachable store is never a pass.

- **coverage** rows against files, chunks against documents, declarations against reality. A file
  with no declared status fails. A PDF with no text layer fails unless `v2/vendor/vendor-noindex.txt`
  gives a reason. A current datasheet whose pages carry almost no text fails the same way, because a
  document that search can reach but cannot answer from must not count as covered.
- **space** re-embeds stored chunks and requires a median cosine of 0.9999 against what is stored.
  The model is the contract, not the host: a different model still answers, still returns 768
  numbers, and quietly ruins every distance. Measured sensitivity: keeping the same model and only
  swapping the asymmetric prefix moves the median to 0.958, far below the bar.
- **gold** twelve real questions, ten electrical and two mechanical, with the document that answers each, every accepted path found
  mechanically from the indexed text rather than written from memory, and each checked to exist so
  the gold set cannot become a test that can never fail.

## What it is made of

285 vendor PDFs and 34 probed geometry files, in MariaDB 11.8 native `VECTOR(768)` with a cosine index, plus InnoDB full text over the same
chunks, fused by reciprocal rank fusion and reranked when the rerank service answers. Embeddings
are `nomic-embed-text` with its asymmetric `search_document:` / `search_query:` prefixes. One row
per (document, page, chunk), because the page is the citation.

Connection details, the embedding endpoint and the rerank endpoint come from
`~/.config/meshsat-fieldkit/kb.env` (mode 600, outside the tree) or the environment:
`MESHSAT_KB_DB_HOST`, `_PORT`, `_USER`, `_PASS`, `_NAME`, `MESHSAT_KB_OLLAMA_URL`,
`MESHSAT_KB_RERANK_URL`. **There are no defaults in this code on purpose:** this repository is
mirrored publicly within minutes of every push, so no host, address or credential of the estate
appears in it, and a missing key is an `INFRA_FAIL` naming the key rather than a quieter path.

## What the first ingest found, before a single query

- `dmr858/dmr858m-datasheet.pdf` is a saved `404 Not Found` page, 552 bytes, not a document.
- `weact/` holds both `README.md` and `readme.md`, two different files. Under the schema's default
  case-insensitive collation the second silently landed on the first's row, took its hash and
  deleted its chunks, with no error anywhere. `relpath` is `utf8mb4_bin` now, and coverage counts
  rows against files so this cannot recur quietly.
- **No datasheet exists in this tree for the TMUXHS4212**, the USB mux of PCB-B's high-availability
  layer, whose pin table the record says was corrected by hand from the manufacturer's drawing.
- **No datasheet exists for the STM32H743**, the three I/O supervisors, which follows from
  `st.com` refusing both the runner and the box (section 7 of the handover).
- The SA868 datasheet, the ruled V2 radio, carries text only from page 2 and is largely images.
- Six documents are filed twice under different names, byte for byte.

## Where it may earn more, and where it may not

It may become a proposer aid: a tool an agent calls while drafting a change, always with the page
citation attached. It may not become a gate, a verdict, or an input to one, and no measurement of
its usefulness changes that, because what makes a board correct is a mechanical check of the board,
not a passage about a part.

## Is it complete, and how would you know

Ask it. `kb_confidence.py` prints the answer from the verdict JSONs the gates wrote, and every figure
in it is one of theirs; nothing in that report computes anything of its own, and a gate that did not
run says so rather than counting as a pass.

    python3 kb/kb_inventory.py --write   # regenerate v2/vendor/PARTS.md and check it against the store
    python3 kb/kb_recall.py              # ask every part's own question, report recall@k
    python3 kb/kb_recheck.py             # re-fetch from the recorded source, compare, date the check
    python3 kb/kb_confidence.py          # the one report, from the gates' own numbers

**The inventory** comes from three independent sources that must agree: the shipped BOM of the newest
deliverable per board, the generators, and the design documents. Each item is DOCUMENTED (a document
names its exact order code), FAMILY (a family document covers it, with the reason declared in
`family-matches.txt`), OPEN PICK (no part chosen yet, so no datasheet can exist, listed with what the
pick needs), NOT USED (a part number named only to record a rejection), or UNCOVERED, which fails.

**Why three sources.** On 10 September the store reported zero parts without a document. It was
measured over `gen_sch_*.py` alone and was wrong within a minute of being checked: four parts were
named only in the other generators, eight more only on the BOMs, five more only in the design
documents. One source is one heuristic's opinion of itself.

**What this does not claim.** That a document is the current revision: only that its bytes still
matched the vendor's on the date `kb_recheck` last ran, with hosts that refuse this runner recorded
as unreachable rather than as verified. That an OCR sidecar's numbers are right: they are an index to
a drawing, never a source. That the open picks are decided: they are not, and they are enumerated.
