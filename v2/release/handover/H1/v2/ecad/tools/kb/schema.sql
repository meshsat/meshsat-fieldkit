-- meshsat_kb, the datasheet knowledge base (MESHSAT-862, 10 September 2026).
--
-- MariaDB 11.8 native VECTOR on the estate's shared cluster, in the same embedding space as the
-- sibling archive so one verification method covers both. Applied once, by hand, from the tools
-- directory; the connection details are NOT in this repository (it mirrors publicly within minutes)
-- and come from ~/.config/meshsat-fieldkit/kb.env.
--
-- What this store is for: telling a session WHICH PAGE of which vendor document to read. The
-- failures this repository has actually paid for were claims about parts that nobody checked
-- against the sheet (a TPS2065CDBV on a SOT-23-6 land for four board phases; a CM5 pin table whose
-- `else: NC` fallback made every PCIe net a one-pad orphan). Retrieval does not fix that. A
-- citation that names a page a human or a gate can re-open does.
--
-- What it is NOT for: deciding anything. See the CHECK constraints on `lookups`.
--
-- And it holds the whole history, not just the current design: the u-blox receiver the Quectel
-- ruling replaced, the Touch Display 2 the Xenarc replaced, the DMR858M dropped from both kits. So
-- every document carries the status of its vendor folder, declared with a reason in
-- v2/vendor/vendor-status.txt, and a hit is always labelled with it.

CREATE TABLE IF NOT EXISTS documents (
  id             BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  -- COLLATE utf8mb4_bin, and not the schema default: the tree is case sensitive and this folder
  -- proves it (weact/ carries both README.md and readme.md, two different files). Under the
  -- case-insensitive default the second one silently landed on the first one's row, taking its
  -- sha256 and deleting its chunks, with no error anywhere. kb_verify.py counts rows against files
  -- for exactly this reason.
  relpath        VARCHAR(768) COLLATE utf8mb4_bin NOT NULL,   -- relative to v2/vendor/
  sha256         CHAR(64) NOT NULL,
  size_bytes     BIGINT UNSIGNED NOT NULL,
  mtime          DATETIME NOT NULL,
  vendor         VARCHAR(64),                    -- the top folder: ti, cm5, quectel, peli, ...
  pages          INT UNSIGNED NULL,
  -- The revision a document declares about ITSELF, read from its first pages: TI's
  -- "SLVS490K, REVISED JUNE 2024", ST's "DS12117 Rev 9", Quectel's "Version: 1.1". About eight in
  -- ten yield one and the rest are written as unknown rather than omitted, because a blank field and
  -- a document with no revision string are different facts.
  revision       VARCHAR(64) NULL,
  -- Where the file came from. Authority is not a property of a PDF: two of ours are Wayback Machine
  -- copies because st.com refuses this host, and one is a distributor's mirror. A reader has to be
  -- able to see that.
  source         VARCHAR(512) NULL,
  -- When the source was last re-fetched and compared. Currency cannot be proved offline; what can be
  -- stated is the date it was last checked against the vendor.
  checked_at     DATETIME NULL,
  text_source    ENUM('pdftotext','direct','none') NOT NULL DEFAULT 'none',
  no_text_reason VARCHAR(255) NULL,              -- from v2/vendor/vendor-noindex.txt
  status         ENUM('current','v1','retired','tooling','undeclared') NOT NULL DEFAULT 'undeclared',
  status_reason  VARCHAR(255) NULL,              -- from v2/vendor/vendor-status.txt, with its ruling
  present        TINYINT(1) NOT NULL DEFAULT 1,  -- 0 = gone from the tree; the row stays, so a
                                                 -- vanished document cannot become a silent absence
  ingested_at    DATETIME NULL,
  UNIQUE KEY uq_relpath (relpath),
  KEY idx_sha (sha256), KEY idx_vendor (vendor), KEY idx_src (text_source), KEY idx_present (present),
  KEY idx_status (status)
) ENGINE=InnoDB;

-- One row per (document, page, chunk). The page is the whole point: a hit is only useful if it
-- says `pdftotext -f 41 -l 41 v2/vendor/ti/ti-tps2065.pdf -` and that page carries the claim.
CREATE TABLE IF NOT EXISTS chunks (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  document_id BIGINT UNSIGNED NOT NULL,
  page        INT UNSIGNED NOT NULL,             -- 1-based; 0 for a document that has no pages
  seq         INT UNSIGNED NOT NULL,             -- chunk within the page
  text        MEDIUMTEXT NOT NULL,
  token_est   INT UNSIGNED,
  UNIQUE KEY uq_doc_page_seq (document_id, page, seq),
  FULLTEXT KEY ft_text (text),
  CONSTRAINT fk_chunk_doc FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Separate from chunks because a vector-indexed column must be NOT NULL and chunks exist before
-- they are embedded: the embedding host is shared, is stopped during board runs on the VM, and
-- reboots daily, so an unembedded backlog is a normal state and must be resumable.
CREATE TABLE IF NOT EXISTS chunk_embeddings (
  chunk_id  BIGINT UNSIGNED PRIMARY KEY,
  model     VARCHAR(64) NOT NULL DEFAULT 'nomic-embed-text',
  embedding VECTOR(768) NOT NULL,
  VECTOR INDEX (embedding) M=8 DISTANCE=cosine,
  CONSTRAINT fk_emb_chunk FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Every lookup is recorded, and the record is where the truth-layer cap is enforced rather than
-- remembered: a retrieved signal is model-derived, so it is capped below the action threshold and
-- it is advisory, and both are CHECK constraints because an invariant survives only when something
-- guards it. There is no spelling of this table in which a lookup decides.
CREATE TABLE IF NOT EXISTS lookups (
  id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  asked_at      DATETIME NOT NULL,
  query         VARCHAR(1024) NOT NULL,
  hits          INT UNSIGNED NOT NULL,
  top_chunk_id  BIGINT UNSIGNED NULL,
  confidence    DECIMAL(4,3) NOT NULL,
  advisory      TINYINT(1) NOT NULL DEFAULT 1,
  caller        VARCHAR(64) NULL,
  CONSTRAINT ck_truth_cap CHECK (confidence <= 0.750),
  CONSTRAINT ck_advisory  CHECK (advisory = 1),
  KEY idx_asked (asked_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS ingest_log (
  id          BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  run_id      VARCHAR(64) NOT NULL,
  started_at  DATETIME NOT NULL,
  stage       VARCHAR(16) NOT NULL,              -- scan | text | embed
  document_id BIGINT UNSIGNED NULL,
  ok          TINYINT(1) NOT NULL,
  detail      VARCHAR(1024),
  KEY idx_run (run_id), KEY idx_doc (document_id)
) ENGINE=InnoDB;
