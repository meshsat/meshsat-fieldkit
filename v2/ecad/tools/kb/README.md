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
- **gold** ten real questions with the document that answers each, every accepted path found
  mechanically from the indexed text rather than written from memory, and each checked to exist so
  the gold set cannot become a test that can never fail.

## What it is made of

MariaDB 11.8 native `VECTOR(768)` with a cosine vector index, plus InnoDB full text over the same
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
