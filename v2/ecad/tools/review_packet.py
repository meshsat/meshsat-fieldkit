#!/usr/bin/env python3
"""A compact review packet for one board at an exact revision (MESHSAT-1357, 26 September 2026).

WHY. The review of 26 September 2026 (v2/docs/reviews/2026-09-26-foundation-progress-review.md, section 5) found
finding references in the progress report and no corrected schematic a reviewer could open without KiCad, and
asked for a packet built from the exact candidate revision: schematic PDFs and the matching native files; the BOM,
an exact part identity and footprint map with primary-source references; a changed netlist, footprint and value
report with a finding ID for each intentional change; the cross-board and harness contracts that touch the board;
and a manifest naming the source revision and every artefact. This tool builds that and nothing else. It decides
nothing: it writes no verdict, moves no hold and releases nothing. A packet is a REVIEW INPUT for an unbuilt
prototype design and never a release to fabrication; every README it writes says so first.

HOW. Two steps, so the KiCad host never needs the repository:
  stage   (any host with git) reads the two revisions from git objects only, never from a working tree:
          at REV the tools directory, meshsat.pretty, v2/vendor/SOURCES.yaml, the certification table and, for
          every board the revision's own routeflow profiles name, its schematic project directory minus the board
          file and the routed verdicts; at PREV each board's committed netlist, schematic, generator and board
          declaration. STAGE.json records both full commit ids and the sha256 of every staged file.
  build   (a KiCad host for the full packet) checks the stage against STAGE.json, then for one board:
          exports the schematic (the paged A3 PDF through the revision's own sch_pages.py, and the whole sheet),
          the netlist, the BOM and the ERC report from the COMMITTED schematic with kicad-cli; compares the exported
          netlist with the committed one (regen_compare, so the report below is about the schematic and not about a
          stale file); copies the native files; writes the change report against PREV, the identity map, the
          interface and contract sections, the holds and open decisions; and hashes everything into MANIFEST.json
          and SHA256SUMS. With --no-kicad the KiCad artefacts are skipped and the manifest says the packet is
          INCOMPLETE; it is never presented as whole.
  verify  re-hashes a packet against its MANIFEST.json and SHA256SUMS.
  all     stage into a temporary directory, then build.

THE FINDING IDS. Every schematic here is written by a generator (gen_sch_<letter>.py) and every correction is a
generator change whose comment should carry the finding it answers. Two readings, never mixed:
  automatic  for each changed reference the tool finds the statement(s) that create it at REV (the reference as a
             string literal, or for a reference made in a loop, an ADDED statement that builds that prefix and names
             one of its nets or its value) and reads, with `tokenize` and `ast` (never a grep), ONLY that statement's
             own comments: the block directly above it and the comments on its lines. IDs there on lines ADDED
             between PREV and REV are credited (status TRACED, read `direct` or `loop`). A block reached by walking up
             past another statement (`nearby`), the block above an enclosing if/try/for (`enclosing`), an added
             comment that names the reference (`mention`) and the added run holding the statement (`hunk`) are
             CANDIDATES: the row is UNVERIFIED_ATTRIBUTION and its IDs are listed as candidates, never credited,
             because a generator comment often speaks for several statements below it.
  by hand    --attribution FILE gives a reading of every changed reference (IDs, the generator lines that carry them,
             the reason in words, and where a round record names more than the generator does, that record). The
             build refuses the file unless every ID is written on its cited lines and every cited range is tied to the
             change: it names the reference (or a range holding it, "C15..C18") or one of its nets, is the defining
             statement's own comment, is the '# ---' section header the statement sits under, or the row states the
             tie in words. A hand row overrides the automatic reading, which stays in the record beside it with a
             flag saying whether the two agree.
Statuses: TRACED (at least one ID; the counts say how many rows carry a FINDING ID and how many only a ruling,
decision or rule), NO_ID_OF_ANY_KIND, UNVERIFIED_ATTRIBUTION. IDs found only on unchanged lines are context. The ID
forms are the review records' own (W6-F5, F-IN-01, S-09, round records R4E-02, R4D-1 and RP-17, O-12, C-05, DC-C1,
SD-B-22, adjudications A01 to A11, owner rulings D-03.2, "decision 40"); a rule ID (TRN-001) counts only if the
revision's rule registry holds it, so SOD-323 or DFN-6 never read as one.

THE PART IDENTITY MAP. One row per BOM line (value, footprint, LCSC code), joined to v2/vendor/SOURCES.yaml. A line WITH
a code joins only the entries whose code fields hold that exact code (never a prefix, a code named in prose or an
alternative the entry weighed). A line WITHOUT a code joins only an entry that names the board (its `boards`, or an update
block's) and is on the revision's generators (not on_main false, not NOT_FITTED), and then only when the entry's `where`,
read at the revision its line number was written against (`where_rev`, else the file's `tree`), falls inside a
reference's defining statement while the entry names the reference or the part the line carries, or when an order code
of its fitted_mpn is written in the line's value as a whole token. Every join says how it was made, and
bom/sources-coverage.json lists the entries that name the board and joined no line.

THE CONTRACTS. check_contracts.py (the revision's own) runs in the build's work copy under a trace that records every
contract it evaluates with the boards the contract names, so the packet lists exactly the contracts that touch its
board, each PASS, FAIL or UNJUDGED as the tool itself decided. Its verdict files go to a scratch directory, never to
the tree's evidence. A board whose committed netlist predates the widened generator identity is UNJUDGED there;
--regen-siblings a,b regenerates such boards from their UNCHANGED generators in the work copy (never in the repository),
records the parity of each regenerated netlist with the committed one, and only then runs the contracts.

Usage:
  review_packet.py stage --repo REPO --rev REV --prev PREV --out STAGE
  review_packet.py build --stage STAGE --board L (--out DIR | --out-root ROOT) [--sources SOURCES.yaml]
                         [--attribution FILE] [--regen-siblings a,b] [--no-kicad]
  review_packet.py all   --repo REPO --rev REV --prev PREV --board L (--out DIR | --out-root ROOT) [...build options]
  review_packet.py verify PACKET
exit 0 on success; build exits 1 when a KiCad step failed and 2 on a usage or stage error; verify exits 1 on any
mismatch.
"""
import ast, csv, difflib, fnmatch, hashlib, io, json, os, re, shutil, subprocess, sys, tempfile, time, tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import regen_compare  # noqa: E402  (the netlist parser and comparator of the parity runs)

BANNER = ("UNBUILT PROTOTYPE DESIGN. No board of this set has been fabricated, assembled or tested; nothing in this "
          "packet is physical evidence. A review packet is a review input: it does NOT release this board to "
          "fabrication, layout or ordering, and it approves nothing.")
PACKET_KIND = "meshsat-fieldkit review packet"
SCHEMA = 1
# the tree's own quarantine marker (tools/order_readiness.py HEAD), for a packet: a board held by an open decision
# permits only "a review package clearly quarantined as NOT_FOR_FAB" (tools/pcb_board_holds.yaml), and no packet of
# any board is fabrication input, so every packet carries it on its front page, in its manifest and in the names of
# its two BOM files, the one marker that travels with a copied file without changing its bytes
READINESS = "READINESS OF THIS PACKET: QUARANTINED, NOT_FOR_FAB"
IDENTITY_CSV = "bom/NOT_FOR_FAB-parts-identity.csv"


# ------------------------------------------------------------------------------------------------ small helpers
def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def _git(repo, *args, binary=False):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.decode(errors="replace").strip()[:300]))
    return r.stdout if binary else r.stdout.decode("utf-8", errors="replace")


def git_show(repo, rev, path):
    """The committed bytes of `path` at `rev`, or None when the revision does not hold it."""
    r = subprocess.run(["git", "-C", repo, "show", "%s:%s" % (rev, path)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def git_ls(repo, rev, path):
    out = _git(repo, "ls-tree", "-r", "--name-only", rev, "--", path)
    return [l for l in out.splitlines() if l]


def write_bytes(p, b):
    os.makedirs(os.path.dirname(p) or ".", exist_ok=True)
    with open(p, "wb") as fh: fh.write(b)


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _load_yaml(p):
    import yaml
    with open(p, encoding="utf-8") as fh: return yaml.safe_load(fh)


# ------------------------------------------------------------------------------------------------ boards at a revision
def boards_at(get, listdir):
    """{letter: {"project": dir name, "stem": board stem}} from a revision's routeflow profiles. `get(path)` returns
    bytes or None and `listdir(path)` the file names under a directory, both at that revision. The board table is the
    revision's own; a project directory is never guessed from a listing of pcb-* folders."""
    out = {}
    for name in sorted(listdir("v2/ecad/tools/routeflow")):
        if not name.endswith(".json") or "/" in name: continue
        try: p = json.loads(get("v2/ecad/tools/routeflow/" + name) or b"{}")
        except ValueError: continue
        letter, stem = name[:-5], p.get("board")
        proj = os.path.basename(str(p.get("project") or "").rstrip("/"))
        if stem and proj: out[letter] = {"project": proj, "stem": stem}
    return out


def _repo_listdir(repo, rev):
    def f(path):
        return [l[len(path) + 1:] for l in git_ls(repo, rev, path)]
    return f


# ------------------------------------------------------------------------------------------------ stage
STAGE_SKIP = re.compile(r"(\.kicad_pcb$|(^|/)routed/|\.verdict\.json$|\.kicad_prl$|-backups/)")


def stage(repo, rev, prev, out):
    repo = os.path.abspath(repo)
    full = {"rev": _git(repo, "rev-parse", rev + "^{commit}").strip(), "prev": _git(repo, "rev-parse", prev + "^{commit}").strip()}
    if os.path.exists(out) and os.listdir(out):
        raise RuntimeError("stage directory %s is not empty" % out)
    os.makedirs(out, exist_ok=True)
    files = {}

    def put(side, path, data):
        write_bytes(os.path.join(out, side, path), data)
        files["%s/%s" % (side, path)] = sha256_bytes(data)

    R, P = full["rev"], full["prev"]
    # REV: the tools directory and the project footprints in full (the generator identity sch_prov checks reads both)
    for top in ("v2/ecad/tools", "v2/ecad/meshsat.pretty"):
        for path in git_ls(repo, R, top):
            if "/__pycache__/" in path: continue
            put("rev", path, git_show(repo, R, path))
    for path in (".gitignore", "v2/vendor/SOURCES.yaml", "v2/release/revA/order/JLC-CERTIFIED.tsv"):
        b = git_show(repo, R, path)
        if b is not None: put("rev", path, b)
    rb = boards_at(lambda p: git_show(repo, R, p), _repo_listdir(repo, R))
    for L, b in sorted(rb.items()):
        for path in git_ls(repo, R, "v2/ecad/" + b["project"]):
            if STAGE_SKIP.search(path): continue
            put("rev", path, git_show(repo, R, path))
    # PREV: what the change report compares against, per board, from PREV's own board table
    pb = boards_at(lambda p: git_show(repo, P, p), _repo_listdir(repo, P))
    for L, b in sorted(pb.items()):
        for path in ("v2/ecad/tools/gen_sch_%s.py" % L, "v2/ecad/tools/boards/%s.json" % L, "v2/ecad/tools/routeflow/%s.json" % L,
                     "v2/ecad/%s/%s.kicad_sch" % (b["project"], b["stem"]), "v2/ecad/%s/%s.kicad_pro" % (b["project"], b["stem"]),
                     "v2/ecad/%s/out/%s.net" % (b["project"], b["stem"])):
            data = git_show(repo, P, path)
            if data is not None: put("prev", path, data)
    rec = {"kind": "stage", "schema": SCHEMA, "rev": R, "prev": P,
           "rev_subject": _git(repo, "log", "-1", "--format=%s", R).strip(),
           "prev_subject": _git(repo, "log", "-1", "--format=%s", P).strip(),
           "rev_date": _git(repo, "log", "-1", "--format=%cI", R).strip(),
           "staged_utc": utc_now(), "boards_rev": rb, "boards_prev": pb, "files": files,
           "note": "read from git objects only; the working tree of %s was not read" % repo}
    with open(os.path.join(out, "STAGE.json"), "w", encoding="utf-8") as fh: json.dump(rec, fh, indent=1, sort_keys=True)
    return rec


def load_stage(stage_dir):
    rec = json.load(open(os.path.join(stage_dir, "STAGE.json"), encoding="utf-8"))
    bad = []
    for rel, want in rec["files"].items():
        p = os.path.join(stage_dir, rel)
        if not os.path.isfile(p) or sha256_file(p) != want: bad.append(rel)
    if bad:
        raise RuntimeError("the stage does not match its STAGE.json (%d file(s), first %s)" % (len(bad), bad[0]))
    return rec


# ------------------------------------------------------------------------------------------------ generator reading
_ID_RULES = [
    ("finding", re.compile(r"\bW\d+-[A-Z]+\d*(?:-\d+)?[a-z]?\b")),     # W6-F5, W3-F12, W5-ZEROIZE-4, W7-R2-01
    ("finding", re.compile(r"\bF-[A-Z]{2}-\d{2}\b")),                  # F-IN-01, F-PR-02
    ("finding", re.compile(r"\bS-\d{2}\b")),                           # S-09
    ("finding", re.compile(r"\bR\d[A-Z]-[A-Z]?\d+\b")),                # R4E-02, R4A-N1, R4D-1 (round records)
    ("finding", re.compile(r"\bRP-\d{2}\b")),                          # RP-17 (round 4 board P record)
    ("finding", re.compile(r"\bO-[A-Z]?\d+\b")),                       # O-12, O-C9
    ("finding", re.compile(r"\bC-\d{2}\b")),                           # C-05
    ("finding", re.compile(r"\bDC-[A-Z]\d+\b")),                       # DC-C1
    ("finding", re.compile(r"\bSD-[A-Z]-\d+\b")),                      # SD-B-22
    ("adjudication", re.compile(r"\bA(?:0[1-9]|1[01])\b")),            # A01 to A11
    ("owner_ruling", re.compile(r"\bD-\d{2}(?:\.\d)?[a-z]?(?:-R\d)?\b")),
    ("decision", re.compile(r"\bdecision \d+\b")),
]
_RULE_ID = re.compile(r"\b[A-Z]{3}-\d{3}\b")
FINDING_KINDS = ("finding", "adjudication")
AUTHORITY_KINDS = ("owner_ruling", "decision")


def extract_ids(text, rule_ids):
    """{category: sorted IDs} in `text`. A rule ID counts only when the registry holds it."""
    out = {}
    for cat, rx in _ID_RULES:
        for m in rx.findall(text): out.setdefault(cat, set()).add(m)
    for m in _RULE_ID.findall(text):
        if m in rule_ids: out.setdefault("rule", set()).add(m)
    return {k: sorted(v) for k, v in out.items()}


def _flat(ids):
    return sorted({x for v in ids.values() for x in v})


def names_token(token, text):
    """True when `text` names `token` as a word, or inside a range written with its own prefix ("C15..C18",
    "C15 to C18", "TS2 to TS4", "R24-R27"). A number alone ("15 to 18") is never read as a range of references."""
    if not token: return False
    if re.search(r"(?<![A-Za-z0-9_])%s(?![A-Za-z0-9_])" % re.escape(token), text): return True
    m = re.match(r"(.*?[A-Za-z_])(\d+)$", token)
    if not m: return False
    pre, n = m.group(1), int(m.group(2))
    rx = r"(?<![A-Za-z0-9_])%s(\d+)\s*(?:\.\.|to|-)\s*%s(\d+)(?![0-9])" % (re.escape(pre), re.escape(pre))
    return any(int(a) <= n <= int(b) for a, b in re.findall(rx, text))


_BODIES = ("body", "orelse", "finalbody")


def _starts_paragraph(t):
    """A comment line that opens a new paragraph in the generators' style: an ID first ("S-09 / A03 ...", "F-BP-01
    (round 4 ...)"), a date first ("26 September 2026 (...)"), or two capitalised words ("FIX-UP OF ...", "A RECORDED
    DEVIATION ...")."""
    if any(rx.match(t) for _c, rx in _ID_RULES): return True
    if re.match(r"\(?\d{1,2} [A-Z][a-z]+ \d{4}", t): return True
    w = t.split()
    return len(w) >= 2 and all(re.search(r"[A-Z]", x) and not re.search(r"[a-z]", x) for x in w[:2])


def _paragraphs(numbered):
    out = []
    for ln, t in numbered:
        if not out or _starts_paragraph(t): out.append([ln])
        else: out[-1].append(ln)
    return out


class Generator:
    """A generator's source at one revision, read with tokenize and ast.

    Statements are kept with their place in the tree (parent statement and previous sibling), so a reading can say
    exactly which comment belongs to which statement: the block directly above a statement, or a comment on the
    statement's own lines, is DIRECT; anything reached by walking up past other statements is not."""

    def __init__(self, text, added_lines=None):
        self.text = text
        self.lines = text.splitlines()
        self.added = set(added_lines or ())
        self.comments = {}                   # line -> comment text
        self.code_lines = set()
        self.literals = {}                   # line -> [string values]
        try:
            for tok in tokenize.generate_tokens(io.StringIO(text).readline):
                if tok.type == tokenize.COMMENT:
                    self.comments.setdefault(tok.start[0], []).append(tok.string.lstrip("#").strip())
                elif tok.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT,
                                      tokenize.ENDMARKER, tokenize.ENCODING):
                    for ln in range(tok.start[0], tok.end[0] + 1): self.code_lines.add(ln)
                    if tok.type == tokenize.STRING:
                        try: v = ast.literal_eval(tok.string)
                        except Exception: v = None
                        if isinstance(v, str): self.literals.setdefault(tok.start[0], []).append(v)
        except (tokenize.TokenError, IndentationError):
            pass
        self.comments = {k: " ".join(v) for k, v in self.comments.items()}
        self.stmts = []                      # [{"a", "b", "compound", "parent", "prev"}]
        self.defines = {}                    # reference -> lines of calls whose FIRST argument is that literal
        try:
            tree = ast.parse(text)
            self._walk(tree.body, None)
            for n in ast.walk(tree):
                if isinstance(n, ast.Call) and n.args and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
                    self.defines.setdefault(n.args[0].value, set()).add(n.lineno)
        except SyntaxError:
            pass
        self.headers = sorted(ln for ln, t in self.comments.items() if ln not in self.code_lines and t.startswith("---"))

    def _walk(self, body, parent):
        prev = None
        for n in body:
            if not isinstance(n, ast.stmt): continue
            idx = len(self.stmts)
            compound = isinstance(n, (ast.For, ast.While, ast.If, ast.With, ast.FunctionDef, ast.ClassDef, ast.Try))
            self.stmts.append({"a": n.lineno, "b": getattr(n, "end_lineno", n.lineno), "compound": compound,
                               "parent": parent, "prev": prev})
            for attr in _BODIES:
                sub = getattr(n, attr, None)
                if isinstance(sub, list) and sub: self._walk(sub, idx)
            for h in getattr(n, "handlers", None) or []:
                self._walk(h.body, idx)
            prev = idx

    def stmt_index_at(self, line):
        """The innermost simple statement holding `line` (a compound one only when nothing simpler holds it)."""
        best = None
        for i, s in enumerate(self.stmts):
            if s["a"] <= line <= s["b"]:
                key = (s["compound"], s["b"] - s["a"])
                if best is None or key < best[0]: best = (key, i)
        return best[1] if best else None

    def stmt_at(self, line):
        i = self.stmt_index_at(line)
        return (self.stmts[i]["a"], self.stmts[i]["b"]) if i is not None else (line, line)

    def comment_block_above(self, first):
        """The comment-only lines directly above line `first`, top to bottom."""
        out, ln = [], first - 1
        while ln >= 1 and ln in self.comments and ln not in self.code_lines:
            out.append(ln); ln -= 1
        return sorted(out)

    def direct_lines(self, line):
        """The comment lines that belong to the statement holding `line`: the block directly above it and the
        comments on its own lines. Nothing above another statement is included."""
        a, b = self.stmt_at(line)
        return self.comment_block_above(a) + [x for x in range(a, b + 1) if x in self.comments]

    def own_paragraphs(self, line, ref, all_refs, own_nets=()):
        """The statement's own comment lines split into what speaks for `ref` and what speaks for another part. A
        block above a statement often holds several paragraphs, one per fix, and only some of them are about this
        statement: a paragraph is this reference's when it names it (or a range holding it) or one of its own nets
        (never a ground or a board rail), or names no reference of the board at all; a paragraph naming only other
        references is theirs. Comments on the statement's own lines are always its own."""
        a, b = self.stmt_at(line)
        blk = self.comment_block_above(a)
        own = [x for x in range(a, b + 1) if x in self.comments]
        other = []
        for para in _paragraphs([(x, self.comments[x]) for x in blk]):
            t = " ".join(self.comments[x] for x in para)
            words = set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*", t))
            if (names_token(ref, t) or any(names_token(n, t) for n in own_nets)
                    or not any(r != ref and r in words for r in all_refs)): own += para
            else: other += para
        return sorted(own), sorted(other)

    def weaker_blocks(self, line, limit=3):
        """Comment blocks reached by walking up from the statement holding `line` past other statements: the block
        above the nearest previous sibling ('nearby'), or above an enclosing compound statement ('enclosing'), within
        `limit` statements. Never credited: these are candidates for a reader."""
        out, i, steps = [], self.stmt_index_at(line), 0
        while i is not None and steps < limit:
            s = self.stmts[i]
            j = s["prev"]
            while j is not None and steps < limit:
                steps += 1
                blk = self.comment_block_above(self.stmts[j]["a"])
                if blk: out.append(("nearby", blk)); return out
                j = self.stmts[j]["prev"]
            p = s["parent"]
            if p is None: break
            steps += 1
            blk = self.comment_block_above(self.stmts[p]["a"])
            if blk: out.append(("enclosing", blk)); return out
            i = p
        return out

    def section_header(self, line):
        """The '# --- ...' section header governing `line` (the last one above it), or None."""
        hs = [h for h in self.headers if h < line]
        return hs[-1] if hs else None

    def text_of(self, lines, with_literals_from=None):
        parts = []
        for ln in lines:
            if ln in self.comments: parts.append(self.comments[ln])
            if with_literals_from and with_literals_from[0] <= ln <= with_literals_from[1]:
                parts += self.literals.get(ln, [])
        return " ".join(parts)

    def ids_on(self, lines, rule_ids, only_added=None):
        """IDs on `lines` (comments, and the string literals of those lines), split by whether the line is added."""
        intro, ctx = [], []
        for ln in lines:
            t = " ".join(([self.comments[ln]] if ln in self.comments else []) + self.literals.get(ln, []))
            if not t: continue
            (intro if ln in self.added else ctx).append(t)
        i = extract_ids(" ".join(intro), rule_ids)
        c = extract_ids(" ".join(ctx), rule_ids)
        c = {k: [x for x in v if x not in i.get(k, [])] for k, v in c.items()}
        return i, {k: v for k, v in c.items() if v}, " | ".join(intro)[:700]

    def anchor_lines(self, ref):
        """The statements that DEFINE `ref` (a call whose first argument is the literal, part("U12", ...)); only
        when none does, every line that carries the literal (a helper that takes the reference second)."""
        if self.defines.get(ref): return sorted(self.defines[ref])
        return sorted(ln for ln, vals in self.literals.items() if ref in vals)

    def loop_anchor_lines(self, ref, hints):
        """For a reference built from a prefix pattern ("TP%d" % i, "R%d" % rn): ADDED statements that carry the
        pattern and name one of `hints` (a net or the value) as a literal."""
        m = re.match(r"([A-Za-z_]+)\d+$", ref)
        if not m: return []
        pat = m.group(1) + "%d"
        out = []
        for s in self.stmts:
            a, b = s["a"], s["b"]
            if not any(ln in self.added for ln in range(a, b + 1)): continue
            vals = [v for ln in range(a, b + 1) for v in self.literals.get(ln, [])]
            if pat in vals and any(h in vals or any(h and h in v for v in vals) for h in hints if h):
                out.append(a)
        return sorted(set(out))

    def mention_lines(self, ref):
        """ADDED comment lines that name `ref` as a word."""
        return [ln for ln, c in sorted(self.comments.items()) if ln in self.added and names_token(ref, c)]

    def hunk_lines(self, line):
        """The comment lines of the contiguous ADDED run that ends at the statement holding `line`, down to the
        statement and never below it. A statement on an unchanged line has no hunk."""
        a, b = self.stmt_at(line)
        if not any(x in self.added for x in range(a, b + 1)): return []
        lo = a
        while lo - 1 in self.added: lo -= 1
        return [x for x in range(lo, b + 1) if x in self.comments]


def added_line_numbers(old_text, new_text):
    a, b = (old_text or "").splitlines(), new_text.splitlines()
    out = set()
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag in ("replace", "insert"): out.update(range(j1 + 1, j2 + 1))
    return out


def vendor_docs_cited(text):
    """Vendor documents a comment names (folder/file.pdf, with or without v2/vendor/); a draft or output path is not one."""
    out = set()
    for m in re.finditer(r"(?:v2/vendor/)?([a-z0-9_-]+)/[A-Za-z0-9_.-]+\.pdf", text):
        if m.group(1) in ("datasheets", "drafts", "out", "render", "img", "box", "jlc"): continue
        out.add(m.group(0))
    return sorted(out)

# ------------------------------------------------------------------------------------------------ netlist changes
def pin_map(nets):
    m = {}
    for name, nodes in nets.items():
        for ref, pin, _pf, _pt in nodes: m[(ref, pin)] = name.lstrip("/")
    return m


def netlist_changes(prev_text, rev_text):
    ca, na = regen_compare.parse_net(prev_text)
    cb, nb = regen_compare.parse_net(rev_text)
    pa, pb = pin_map(na), pin_map(nb)
    refs = sorted(set(ca) | set(cb), key=lambda r: (re.sub(r"\d+", "", r), int(re.sub(r"\D", "", r) or 0), r))
    ch = []
    for r in refs:
        if r.startswith("#"): continue
        a, b = ca.get(r), cb.get(r)
        pins_a = {p: n for (rr, p), n in pa.items() if rr == r}
        pins_b = {p: n for (rr, p), n in pb.items() if rr == r}
        if a is None:
            ch.append({"ref": r, "kind": "ADDED", "value": b["value"], "footprint": b["footprint"],
                       "lcsc": b["fields"].get("LCSC", ""), "pins": dict(sorted(pins_b.items()))}); continue
        if b is None:
            ch.append({"ref": r, "kind": "REMOVED", "value": a["value"], "footprint": a["footprint"],
                       "lcsc": a["fields"].get("LCSC", ""), "pins": dict(sorted(pins_a.items()))}); continue
        fields = {}
        for f, va, vb in (("value", a["value"], b["value"]), ("footprint", a["footprint"], b["footprint"]),
                          ("lcsc", a["fields"].get("LCSC", ""), b["fields"].get("LCSC", ""))):
            if va != vb: fields[f] = [va, vb]
        moved = {p: [pins_a.get(p), pins_b.get(p)] for p in sorted(set(pins_a) | set(pins_b)) if pins_a.get(p) != pins_b.get(p)}
        if fields or moved:
            ch.append({"ref": r, "kind": "CHANGED", "fields": fields, "pins_moved": moved, "value": b["value"],
                       "footprint": b["footprint"], "lcsc": b["fields"].get("LCSC", "")})
    sa = {k: frozenset((x[0], x[1]) for x in v) for k, v in na.items()}
    sb = {k: frozenset((x[0], x[1]) for x in v) for k, v in nb.items()}
    only_a, only_b = sorted(set(sa) - set(sb)), sorted(set(sb) - set(sa))
    renamed = [[x, y] for x in only_a for y in only_b if sa[x] == sb[y]]
    summary = {"components": [len([c for c in ca if not c.startswith("#")]), len([c for c in cb if not c.startswith("#")])],
               "nets": [len(na), len(nb)], "added": sum(c["kind"] == "ADDED" for c in ch),
               "removed": sum(c["kind"] == "REMOVED" for c in ch), "changed": sum(c["kind"] == "CHANGED" for c in ch),
               "nets_only_prev": only_a, "nets_only_rev": only_b, "nets_renamed": renamed,
               "content_hash": [regen_compare.content_hash(prev_text), regen_compare.content_hash(rev_text)]}
    return ch, summary, (cb, nb), (pa, pb)


TRACED, NO_ID, UNVERIFIED = "TRACED", "NO_ID_OF_ANY_KIND", "UNVERIFIED_ATTRIBUTION"
COMMON_NET_NODES = 12   # a net on more pins than this (a ground, a board rail) is not evidence that a comment is about one part


def _split_ids(ids):
    return (sorted({x for k in FINDING_KINDS for x in ids.get(k, [])}),
            sorted({x for k in AUTHORITY_KINDS for x in ids.get(k, [])}),
            sorted(ids.get("rule", [])))


def _nets_of(ref, pins):
    return sorted({n for (r, _p), n in pins.items() if r == ref and n and not n.startswith("unconnected-")})


def read_automatic(c, gen_rev, gen_prev, rule_ids, nets, all_refs=(), own_nets=()):
    """The mechanical reading of one change. Only a DIRECT comment (the block directly above the defining
    statement, or a comment on its own lines) or a LOOP anchor's direct comment can credit an ID; every weaker
    reading (a neighbour's block, the block above an enclosing statement, an added comment that mentions the
    reference, the added hunk) is a candidate for a reader and never credited."""
    removed = c["kind"] == "REMOVED"
    g = gen_prev if removed else gen_rev
    lines = g.anchor_lines(c["ref"]) if g is not None else []
    how = "literal"
    if not lines and g is not None and not removed:
        lines = g.loop_anchor_lines(c["ref"], list(nets) + [c.get("value") or ""]); how = "loop"
    ev = {"anchor": how if lines else "none", "generator_side": "prev" if removed else "rev",
          "spans": [list(g.stmt_at(ln)) for ln in lines] if g is not None else [],
          "direct": {"lines": [], "introduced": {}, "context": {}, "excerpt": ""}, "candidates": []}
    if g is not None and lines:
        split = [g.own_paragraphs(ln, c["ref"], all_refs, own_nets) for ln in lines]
        dl = sorted({x for own, _o in split for x in own})
        others = sorted({x for _own, o in split for x in o})
        intro, ctx, exc = g.ids_on(dl, rule_ids)
        if others and not removed:
            i, _c, t = g.ids_on(others, rule_ids)
            if any(i.values()):
                ev["candidates"].append({"kind": "other_paragraph", "lines": [others[0], others[-1]], "ids": i, "excerpt": t[:300]})
        if removed:
            # a removal is explained by what the NEW revision says; the removed statement's own comment is context
            for k, v in intro.items(): ctx[k] = sorted(set(ctx.get(k, [])) | set(v))
            intro, exc = {}, ""
        ev["direct"] = {"lines": dl, "introduced": intro, "context": ctx, "excerpt": exc, "other_paragraph_lines": others}
        if not removed:
            for ln in lines:
                # a statement with its own comment is not read past it: the blocks above other statements are theirs
                for kind, blk in ([] if g.direct_lines(ln) else g.weaker_blocks(ln)):
                    i, _c, t = g.ids_on(blk, rule_ids)
                    if any(i.values()):
                        ev["candidates"].append({"kind": kind, "lines": [blk[0], blk[-1]], "ids": i, "excerpt": t[:300]})
                hl = g.hunk_lines(ln)
                i, _c, t = g.ids_on(hl, rule_ids)
                if hl and any(i.values()):
                    ev["candidates"].append({"kind": "hunk", "lines": [hl[0], hl[-1]], "ids": i, "excerpt": t[:300]})
    if gen_rev is not None:
        ml = gen_rev.mention_lines(c["ref"])
        i, _c, t = gen_rev.ids_on(ml, rule_ids)
        if any(i.values()):
            ev["candidates"].append({"kind": "mention", "lines": ml[:24], "ids": i, "excerpt": t[:300]})
    if any(ev["direct"]["introduced"].values()):
        status, credited, read = TRACED, ev["direct"]["introduced"], ("loop" if how == "loop" else "direct")
    elif ev["candidates"]:
        status, credited, read = UNVERIFIED, {}, "automatic"
    else:
        status, credited, read = NO_ID, {}, ("loop" if how == "loop" else ("direct" if lines else "none"))
    return status, credited, read, ev


def load_hand_map(path, stage_rec, letter):
    """A reading of every changed reference by a person or a session, with the generator lines that carry each ID.
    The file names its board and both revisions; a mismatch refuses the build."""
    hm = _load_yaml(path) or {}
    bad = []
    if str(hm.get("board", "")).lower() != letter.lower(): bad.append("board %r, building %r" % (hm.get("board"), letter))
    for k in ("rev", "prev"):
        v = str(hm.get(k) or "")
        if len(v) < 8 or not stage_rec[k].startswith(v): bad.append("%s %r does not name the stage's %s" % (k, v, stage_rec[k][:12]))
    if not isinstance(hm.get("rows"), dict): bad.append("no rows")
    if bad: raise RuntimeError("attribution map %s: %s" % (path, "; ".join(bad)))
    return hm


def _ranges(cite):
    out = []
    for x in cite if isinstance(cite, list) else [cite]:
        if isinstance(x, int): out.append((x, x))
        elif isinstance(x, list) and len(x) == 2 and all(isinstance(y, int) for y in x): out.append((min(x), max(x)))
        else: raise RuntimeError("cite %r is not a line or a [first, last] pair" % (x,))
    return out


def apply_hand(c, row, gen_rev, gen_prev, rule_ids, nets, anchors):
    """Check one hand-read row against the generator at the new revision and return what it establishes. Every ID
    must be written on the cited lines, and every cited range must be tied to the change: it names the reference or
    one of its nets, it is the defining statement's own comment, it is the section header the statement sits under,
    or the row states the tie in words. Anything else refuses the build."""
    errs = []
    why = str(row.get("why") or "").strip()
    if not why: errs.append("no 'why'")
    try: rng = _ranges(row.get("cite") or [])
    except RuntimeError as e: rng, errs = [], errs + [str(e)]
    if not rng: errs.append("no cite")
    n = len(gen_rev.lines)
    for a, b in rng:
        if not (1 <= a <= b <= n): errs.append("cite %d-%d outside the generator (1-%d)" % (a, b, n))
    declared = [str(x) for x in (row.get("ids") or [])]
    cited_lines = sorted({x for a, b in rng for x in range(a, b + 1) if 1 <= x <= n})
    found_by_line = {}
    for ln in cited_lines:
        t = " ".join(([gen_rev.comments[ln]] if ln in gen_rev.comments else []) + gen_rev.literals.get(ln, []))
        for x in _flat(extract_ids(t, rule_ids)): found_by_line.setdefault(x, []).append(ln)
    ids = {}
    unchanged = []
    for x in declared:
        kind = [k for k, v in extract_ids(x, rule_ids).items() if x in v]
        if not kind: errs.append("%s is not an ID form this tool reads" % x); continue
        if x not in found_by_line: errs.append("%s is not written on the cited lines %s" % (x, ", ".join("%d-%d" % r for r in rng))); continue
        ids.setdefault(kind[0], []).append(x)
        if not any(ln in gen_rev.added for ln in found_by_line[x]): unchanged.append(x)
    removed = c["kind"] == "REMOVED"
    near = set()
    if not removed:
        for ln in anchors:
            a, b = gen_rev.stmt_at(ln)
            near |= set(range(a, b + 1)) | set(gen_rev.direct_lines(ln))
    ties = []
    for a, b in rng:
        t = gen_rev.text_of(range(a, b + 1))
        how = []
        if names_token(c["ref"], t): how.append("names_ref")
        hit = [nn for nn in nets if names_token(nn, t)]
        if hit: how.append("names_net:" + ",".join(hit[:3]))
        if near & set(range(a, b + 1)): how.append("at_anchor")
        if not removed:
            hs = {gen_rev.section_header(ln) for ln in anchors} - {None}
            if hs & set(range(a, b + 1)): how.append("in_section")
        ties.append({"lines": [a, b], "tie": how})
    stated = str(row.get("tie") or "").strip()
    if any(not t["tie"] for t in ties) and not stated:
        errs.append("cite %s is not tied to %s (it names neither the reference nor its nets, is not its statement's "
                    "comment or section header) and the row states no tie" % (
                        ", ".join("%d-%d" % tuple(t["lines"]) for t in ties if not t["tie"]), c["ref"]))
    if errs: raise RuntimeError("attribution map, %s: %s" % (c["ref"], "; ".join(errs)))
    ids = {k: sorted(set(v)) for k, v in ids.items()}
    return ids, {"cite": [list(r) for r in rng], "ties": ties, "tie_stated": stated, "why": why,
                 "record": str(row.get("record") or "").strip(), "ids_on_unchanged_lines": sorted(unchanged)}


def attribute(changes, gen_rev, gen_prev, rule_ids, pins_rev=None, pins_prev=None, hand=None):
    pins_rev, pins_prev = pins_rev or {}, pins_prev or {}
    all_refs = sorted({r for (r, _p) in list(pins_rev) + list(pins_prev) if not r.startswith("#")} | {c["ref"] for c in changes})
    rows = (hand or {}).get("rows") or {}
    refs = {c["ref"] for c in changes}
    # a net shared by many parts (a ground, a board rail) names no part in particular, so it never ties a citation
    size = {}
    for pins in (pins_rev, pins_prev):
        for (_r, _p), n in pins.items(): size[n] = max(size.get(n, 0), sum(1 for v in pins.values() if v == n))
    common = {n for n, k in size.items() if k > COMMON_NET_NODES}
    stray = sorted(set(rows) - refs)
    if stray: raise RuntimeError("attribution map names references that did not change: %s" % ", ".join(stray))
    for c in changes:
        nets = _nets_of(c["ref"], pins_prev if c["kind"] == "REMOVED" else pins_rev)
        if c["kind"] != "ADDED": nets = sorted(set(nets) | set(_nets_of(c["ref"], pins_prev)))
        status, credited, read, ev = read_automatic(c, gen_rev, gen_prev, rule_ids, nets, all_refs, [n for n in nets if n not in common])
        f, a, r = _split_ids(credited)
        auto = {"status": status, "read": read, "finding_ids": f, "authority_ids": a, "rule_ids": r,
                "candidate_ids": sorted({x for cd in ev["candidates"] for x in _flat(cd["ids"])})}
        if c["ref"] in rows:
            anchors = [] if c["kind"] == "REMOVED" else [s[0] for s in ev["spans"]]
            ids, hand_ev = apply_hand(c, rows[c["ref"]], gen_rev, gen_prev, rule_ids, [n for n in nets if n not in common], anchors)
            f, a, r = _split_ids(ids)
            status = TRACED if (f or a or r) else NO_ID
            read = "hand"
            ev["hand"] = hand_ev
            auto["agrees"] = (auto["status"] == status and auto["finding_ids"] == f and auto["authority_ids"] == a
                              and auto["rule_ids"] == r)
        ev["automatic"] = auto
        c["evidence"] = ev
        c["finding_ids"], c["authority_ids"], c["rule_ids"] = f, a, r
        c["status"], c["read"] = status, read
    return changes


def change_counts(changes):
    n = len(changes)
    fid = sum(1 for c in changes if c["status"] == TRACED and c["finding_ids"])
    auth = sum(1 for c in changes if c["status"] == TRACED and not c["finding_ids"])
    return {"changes": n, "with_finding_id": fid, "authority_or_rule_only": auth,
            "no_id_of_any_kind": sum(1 for c in changes if c["status"] == NO_ID),
            "unverified_attribution": sum(1 for c in changes if c["status"] == UNVERIFIED),
            "without_finding_id": n - fid,
            "read_by_hand": sum(1 for c in changes if c["read"] == "hand"),
            "hand_disagrees_with_automatic": sum(1 for c in changes if c["read"] == "hand" and not c["evidence"]["automatic"].get("agrees"))}


# ------------------------------------------------------------------------------------------------ identity map
def _strings(o):
    if isinstance(o, str): yield o
    elif isinstance(o, dict):
        for v in o.values(): yield from _strings(v)
    elif isinstance(o, list):
        for v in o: yield from _strings(v)


_CODE = re.compile(r"\bC\d{3,9}\b")
_CODE_KEYS = ("lcsc", "code", "lcsc_1f614233")


def entry_codes(e):
    """The LCSC codes an entry COVERS: the values of its code fields (`lcsc`, `code` in a parts list, an update
    block's codes), never a code named in prose and never an alternative the entry weighed and did not fit."""
    out = set()

    def walk(o, key=None):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("alternative_readings", "lcsc_reading", "lcsc_readings"): continue
                walk(v, k)
        elif isinstance(o, list):
            for v in o: walk(v, key)
        elif isinstance(o, str) and key in _CODE_KEYS:
            out.update(_CODE.findall(o))
    walk(e)
    return out


def sources_index(sources):
    """LCSC code -> [entry], joined on the exact code token of an entry's code fields."""
    idx = {}
    for e in (sources or {}).get("parts", []) or []:
        for code in entry_codes(e): idx.setdefault(code, []).append(e)
    return idx


def _docs_of(e, code=None):
    """The entry's documents (its own and its update blocks'). In an entry that covers several codes and whose
    documents say which code each describes, only the documents naming `code` are listed."""
    docs = list(e.get("documents") or [])
    for k, v in e.items():
        if k.startswith("update_") and isinstance(v, dict): docs += list(v.get("documents_added") or [])
    docs = [d for d in docs if isinstance(d, dict)]
    named = [d for d in docs if _CODE.search(" ".join(str(d.get(k) or "") for k in ("matches_fitted", "url")))]
    if code and named:
        docs = [d for d in named if code in _CODE.findall(" ".join(str(d.get(k) or "") for k in ("matches_fitted", "url")))]
    return [{"path": d.get("path"), "doc_id": d.get("doc_id"), "revision": d.get("revision"), "url": d.get("url"),
             "sha256": d.get("sha256"), "matches_fitted": d.get("matches_fitted")} for d in docs]


def _identity_of(e):
    """An entry's identity verdict, the newest update block's where it restates one."""
    for k in sorted((k for k in e if k.startswith("update_")), reverse=True):
        v = e[k]
        if isinstance(v, dict):
            for kk, vv in v.items():
                if kk.startswith("identity_"): return vv
    return e.get("identity")


def _boards_of(e):
    """The boards an entry names, the newest update block's `boards` where it restates them (a part a board no
    longer fits leaves that board's list in the update block, not by rewriting the entry's history)."""
    for k in sorted((k for k in e if k.startswith("update_")), reverse=True):
        v = e[k]
        if isinstance(v, dict) and isinstance(v.get("boards"), list): return [str(b).upper() for b in v["boards"]]
    return [str(b).upper() for b in (e.get("boards") or [])]


def _where_of(e, tree=""):
    """(where text, the revision its line numbers were read at) of an entry: the newest update block that restates
    both (`where`, `where_rev`), else the entry's own schematic_name.where with its `where_rev`, else the file's tree."""
    for k in sorted((k for k in e if k.startswith("update_")), reverse=True):
        v = e[k]
        if isinstance(v, dict) and v.get("where") and v.get("where_rev"): return str(v["where"]), str(v["where_rev"])
    return str((e.get("schematic_name") or {}).get("where") or ""), str(e.get("where_rev") or tree or "")


def _placed(e):
    """False when the entry declares its part is not placed on any schematic (a cell of the pack build, a module
    bolted to the plate): such an entry joins no BOM line by design and is reported as such, not as a gap."""
    return e.get("placed_part") is not False


_WHERE_ITEM = re.compile(r"gen_sch_([a-z0-9]+)\.py(?::(\d+)(?:-(\d+))?)?|(?<![\w.:/-]):(\d+)(?:-(\d+))?")


def where_items(where):
    """[(board letter, first line, last line)] of an entry's `where` text. A bare ':540' continues the generator
    named before it ("gen_sch_e.py:218 (J_SMB), :540 (J_TAMP); gen_sch_p.py:159"); a line of any other file
    (kisch.py:345) is never read as a generator's."""
    out, cur = [], None
    for m in _WHERE_ITEM.finditer(str(where or "")):
        if m.group(1):
            cur, a, b = m.group(1), m.group(2), m.group(3)
        else:
            a, b = m.group(4), m.group(5)
        if cur and a: out.append((cur, int(a), int(b or a)))
    return out


def _order_code_tokens(e):
    """The order-code tokens of an entry's fitted_mpn ("B4B-XH-A (E J_SMB), B2B-XH-A (E J_TAMP)" gives B4B-XH-A and
    B2B-XH-A): parenthesised notes dropped, split at commas and spaces, a token has a digit and a capital letter."""
    s = re.sub(r"\([^)]*\)", " ", str(e.get("fitted_mpn") or ""))
    return sorted({t.strip(".:;") for t in re.split(r"[\s,;]+", s)
                   if len(t.strip(".:;")) >= 5 and re.search(r"\d", t) and re.search(r"[A-Z]", t)})


def _name_chunks(e):
    """The part names of an entry's schematic_name text, parenthesised notes dropped ("JST-XH 1x4 (B4B-XH-A),
    JST-XH 1x5" gives "JST-XH 1x4" and "JST-XH 1x5")."""
    s = re.sub(r"\([^)]*\)", " ", str((e.get("schematic_name") or {}).get("text") or ""))
    return sorted({" ".join(c.split()) for c in re.split(r"[,;]", s) if len(" ".join(c.split())) >= 6})


def _in_value(token, value):
    return bool(re.search(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(token), value or ""))


def _join_without_code(e, letter, refs, value, gen_rev, rev, tree):
    """How an entry covers a BOM line that carries NO LCSC code, or None. The entry must name this board, be on
    this revision's generators (not a candidate: on_main false, or NOT_FITTED) and then either
      * its `where` names this board's generator at a line inside a reference's DEFINING statement, read only at
        the revision the line number was written against (`where_rev`, else the file's `tree`), and the entry
        itself names the reference or the part the line carries (the reference in the `where` text, or a part
        name of its schematic_name text or an order code of its fitted_mpn in the line's value), because a
        generator line can hold several statements; or
      * an order code of its fitted_mpn is written, as a whole token, in the line's value.
    A line WITH a code is joined by the code alone, never by these."""
    if letter.upper() not in _boards_of(e): return None
    if e.get("on_main") is False or _identity_of(e) == "NOT_FITTED" or not _placed(e): return None
    tokens = _order_code_tokens(e)
    named_in_value = [t for t in tokens if _in_value(t, value)] + [c for c in _name_chunks(e) if c in (value or "")]
    where, wrev = _where_of(e, tree)
    if gen_rev is not None and where and len(wrev) >= 7 and rev.startswith(wrev):
        for L, a, b in where_items(where):
            if L != letter.lower(): continue
            for ref in refs:
                for ln in gen_rev.anchor_lines(ref):
                    s0, s1 = gen_rev.stmt_at(ln)
                    if s0 <= b and a <= s1 and (names_token(ref, where) or named_in_value):
                        return "where gen_sch_%s.py:%s at %s (%s)" % (L, a if a == b else "%d-%d" % (a, b), wrev[:8],
                                                                    "names %s" % ref if names_token(ref, where) else
                                                                    "the value names " + named_in_value[0])
    hit = [t for t in tokens if _in_value(t, value)]
    if hit: return "fitted order code %s written in the value" % hit[0]
    return None


def jlc_table(path):
    out = {}
    if not path or not os.path.isfile(path): return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh, delimiter="\t"):
            code = (row.get("code") or row.get("bom_code") or "").strip()
            if code: out.setdefault(code, row)
    return out


def identity_map(comps, gen_rev, sources, jlc, letter="", rev=""):
    """One row per BOM line (value, footprint, LCSC code), joined to SOURCES.yaml: by the exact LCSC code of a
    code field when the line has one, and otherwise only as `_join_without_code` allows. Each joined entry says how
    it was joined (`joined_by`) and a row says whether the line carries an order code at all."""
    groups = {}
    for ref, c in comps.items():
        if ref.startswith("#"): continue
        key = (c["value"] or "", c["footprint"] or "", c["fields"].get("LCSC", ""))
        groups.setdefault(key, []).append(ref)
    idx = sources_index(sources)
    tree = str((sources or {}).get("tree") or "")
    rows = []
    for (value, fp, code), refs in sorted(groups.items(), key=lambda kv: sorted(kv[1])[0]):
        refs = sorted(refs, key=lambda r: (re.sub(r"\d+", "", r), int(re.sub(r"\D", "", r) or 0)))
        if code:
            entries = [(e, "LCSC code %s" % code) for e in idx.get(code, [])]
        else:
            entries = []
            for e in (sources or {}).get("parts", []) or []:
                how = _join_without_code(e, letter, refs, value, gen_rev, rev, tree) if letter else None
                if how: entries.append((e, how))
        cited = set()
        if gen_rev is not None:
            for ln in gen_rev.anchor_lines(refs[0]):
                a, b = gen_rev.stmt_at(ln)
                txt = " ".join(gen_rev.comments.get(x, "") for x in gen_rev.comment_block_above(a) + list(range(a, b + 1)))
                cited.update(vendor_docs_cited(txt))
        j = jlc.get(code) if code else None
        rows.append({
            "refs": refs, "qty": len(refs), "value": value, "footprint": fp, "lcsc": code,
            "order_code_on_line": bool(code),
            "jlc_certified_row": ({"verdict": j.get("verdict"), "model": j.get("model"), "brand": j.get("brand"),
                                   "pkg": j.get("pkg"), "asked": j.get("asked")} if j else None),
            "sources_entries": [{"id": e.get("id"), "fitted_mpn": e.get("fitted_mpn"), "identity": _identity_of(e),
                                 "on_main": e.get("on_main"), "status": e.get("status"), "joined_by": how,
                                 "documents": _docs_of(e, code or None)}
                                for e, how in entries],
            "generator_cited_documents": sorted(cited),
        })
    return rows


def identity_coverage(rows, sources, letter, rev=""):
    """Every entry that names this board and is on the revision's generators, with the BOM lines it joined. An entry
    that names the board and joined NO line is listed apart with the reason read from the entry itself: either the
    board no longer fits the part (its update block should say so), or the entry's code or `where` does not reach the
    line that carries it. An entry that declares its part is not placed on a schematic is listed as such."""
    joined = {}
    for r in rows:
        for e in r["sources_entries"]: joined.setdefault(e["id"], []).append(" ".join(r["refs"]))
    tree = str((sources or {}).get("tree") or "")
    codes_here = {r["lcsc"] for r in rows if r["lcsc"]}
    names, unjoined, unplaced = [], [], []
    for e in (sources or {}).get("parts", []) or []:
        if letter.upper() not in _boards_of(e): continue
        if e.get("on_main") is False or _identity_of(e) == "NOT_FITTED": continue
        if not _placed(e):
            unplaced.append(e.get("id")); continue
        names.append(e.get("id"))
        if e.get("id") in joined: continue
        where, wrev = _where_of(e, tree)
        mine = [x for x in where_items(where) if x[0] == letter.lower()]
        codes = sorted(entry_codes(e))
        if codes and not (set(codes) & codes_here): why = "none of its codes (%s) is on this board's BOM" % ", ".join(codes)
        elif not mine: why = "its `where` names no line of gen_sch_%s.py" % letter.lower()
        elif not (len(wrev) >= 7 and rev.startswith(wrev)): why = "its `where` was read at %s, not at this revision" % (wrev[:8] or "no revision")
        else: why = "its `where` at this revision reaches no code-less line it names"
        unjoined.append({"id": e.get("id"), "boards": _boards_of(e), "lcsc": e.get("lcsc"), "where": where,
                         "where_rev": wrev, "why": why})
    return {"entries_naming_this_board": names, "joined": {k: v for k, v in sorted(joined.items())},
            "entries_naming_this_board_that_joined_no_line": unjoined,
            "entries_declaring_no_placed_part": unplaced,
            "rule": "a line with an LCSC code joins by that exact code; a line without one joins only an entry that "
                    "names this board and either points its `where` (read at its own revision) at the line's defining "
                    "statement while naming the reference or the part, or writes its fitted order code in the value"}


# ------------------------------------------------------------------------------------------------ interfaces, holds
def interfaces_for(spec, letter, net_names):
    b = ((spec or {}).get("boards") or {}).get(letter) or {}
    out = []
    for a in b.get("assignments") or []:
        name = a.get("interface")
        itf = ((spec or {}).get("interfaces") or {}).get(name) or {}
        nets = sorted(n for n in net_names if any(fnmatch.fnmatch(n, p) for p in a.get("patterns") or []))
        out.append({"interface": name, "what": itf.get("what"), "patterns": a.get("patterns"), "class": a.get("class"),
                    "impedance_ohm": itf.get("impedance_ohm"), "impedance_tol_percent": itf.get("impedance_tol_percent"),
                    "intra_pair_mm": itf.get("intra_pair_mm"), "max_length_mm": itf.get("max_length_mm"),
                    "sources": [{"title": s.get("title"), "clause": s.get("clause"), "path": s.get("url_or_path")}
                                for s in itf.get("sources") or []],
                    "nets_on_this_board": nets})
    return out


def holds_and_decisions(tools, letter):
    out = {"holds": [], "open_decisions": []}
    try:
        h = (_load_yaml(os.path.join(tools, "pcb_board_holds.yaml")) or {}).get("holds") or {}
        if letter in h: out["holds"].append(dict(h[letter], board=letter))
    except Exception as e:
        out["holds_error"] = repr(e)[:200]
    try:
        for d in (_load_yaml(os.path.join(tools, "pcb_decisions.yaml")) or {}).get("decisions") or []:
            if d.get("status") == "open":
                out["open_decisions"].append({"n": d.get("n"), "title": d.get("title"), "status": d.get("status"),
                                              "boards": d.get("boards") or "not declared; the text names them"})
    except Exception as e:
        out["decisions_error"] = repr(e)[:200]
    return out


# ------------------------------------------------------------------------------------------------ contracts
_CONTRACT_TRACE = r'''
import json, os, runpy, sys
path, ecad, out = sys.argv[1:4]
code, rec, box = os.path.realpath(path), [], {"exit": None}
def tracer(frame, event, arg):
    if event == "call" and frame.f_code.co_name == "check" and os.path.realpath(frame.f_code.co_filename) == code:
        loc, g, caller = frame.f_locals, frame.f_globals, frame.f_back
        boards = sorted(loc.get("boards") or [])
        missing = [b for b in boards if b in (g.get("MISSING") or [])]
        rec.append({"text": loc.get("text"), "boards": boards, "group": loc.get("group"),
                    "result": "UNJUDGED" if missing else ("PASS" if loc.get("ok") else "FAIL"),
                    "detail": (loc.get("detail") or "") if not loc.get("ok") else "", "absent_boards": missing,
                    "defined_at": "check_contracts.py:%d" % (caller.f_lineno if caller else 0)})
    return None
sys.argv = [path, ecad]
sys.settrace(tracer)
try:
    runpy.run_path(path, run_name="__main__")
except SystemExit as e:
    box["exit"] = e.code
finally:
    sys.settrace(None)
    json.dump({"contracts": rec, "exit": box["exit"]}, open(out, "w"), indent=1)
'''


def run_contracts(ecad, scratch):
    """Run the revision's own check_contracts.py in a child process under a trace that records every contract it
    evaluates with the boards it names. The child's cwd and VERDICT_DIR are a scratch directory, so its verdicts
    never reach any tree's evidence, and no module of this tool's own directory leaks into the revision's run."""
    path = os.path.join(ecad, "tools", "check_contracts.py")
    if not os.path.isfile(path):
        return {"status": "NOT_RUN", "why": "tools/check_contracts.py is absent at this revision", "contracts": []}
    os.makedirs(scratch, exist_ok=True)
    wrapper, result = os.path.join(scratch, "trace_contracts.py"), os.path.join(scratch, "contracts.json")
    with open(wrapper, "w") as fh: fh.write(_CONTRACT_TRACE)
    env = dict(os.environ, VERDICT_DIR=scratch)
    r = subprocess.run([sys.executable, wrapper, path, ecad, result], cwd=scratch, env=env, capture_output=True,
                       text=True, timeout=900)
    try:
        got = json.load(open(result))
    except Exception as e:
        return {"status": "CRASHED", "why": "no trace record (%r); exit %s" % (e, r.returncode), "contracts": [],
                "log": (r.stdout + r.stderr)[-4000:]}
    return {"status": "RUN", "exit": got.get("exit"), "contracts": got.get("contracts", []), "log": r.stdout + r.stderr}


# ------------------------------------------------------------------------------------------------ kicad
def kicad_version():
    try:
        r = subprocess.run(["kicad-cli", "version"], capture_output=True, text=True, timeout=60)
        return r.stdout.strip() or None
    except Exception:
        return None


def _run(cmd, cwd=None, env=None, timeout=1800):
    r = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout + r.stderr)[-4000:]


def phase_label(sch_text):
    m = re.search(r'\(comment 1 "Phase ([A-Za-z0-9]+)', sch_text)
    return m.group(1) if m else ""


def annotation_scan(sch_text):
    """What a text reading of the committed schematic says about annotation, beside KiCad's own warning: symbol
    instances whose (reference, unit) repeats, and references still carrying a '?'. KiCad's warning does not say
    which symbol it means, so a clean scan leaves its cause NOT ESTABLISHED rather than explained."""
    inst = re.findall(r'\(reference "([^"]+)"\)\s*\(unit (\d+)\)', sch_text)
    seen, dup = set(), set()
    for k in inst:
        (dup if k in seen else seen).add(k)
    return {"instances": len(inst), "duplicate_reference_unit": sorted("%s unit %s" % k for k in dup),
            "unannotated": sorted({r for r, _u in inst if "?" in r})}


def regen_board(work_ecad, letter, proj, stem):
    """Regenerate one board's schematic, netlist and sidecar from its generator in the WORK copy."""
    d = os.path.join(work_ecad, proj)
    sch = os.path.join(d, stem + ".kicad_sch")
    committed_net = os.path.join(d, "out", stem + ".net")
    keep = committed_net + ".committed"
    shutil.copyfile(committed_net, keep)
    env = dict(os.environ, PHASE=phase_label(open(sch, encoding="utf-8", errors="replace").read()))
    rc1, log1 = _run([sys.executable, os.path.join("..", "tools", "gen_sch_%s.py" % letter), stem + ".kicad_sch", stem], cwd=d, env=env)
    os.remove(committed_net)
    rc2, log2 = _run(["bash", os.path.join("..", "tools", "build_sch.sh"), ".", stem], cwd=d)
    res = {"board": letter, "gen_sch_exit": rc1, "build_sch_exit": rc2, "phase_label": env["PHASE"],
           "log_tail": (log1[-600:] + "\n" + log2[-600:])}
    if os.path.isfile(committed_net):
        res["parity_with_committed_netlist"] = regen_compare.cmp_net(keep, committed_net)["result"]
    else:
        res["parity_with_committed_netlist"] = "NOT_PRODUCED"
    return res


# ------------------------------------------------------------------------------------------------ build
def _rel(p, root):
    return os.path.relpath(p, root).replace(os.sep, "/")


def build(stage_dir, letter, out_dir, sources_path=None, regen_siblings=(), no_kicad=False, attribution_path=None):
    st = load_stage(stage_dir)
    letter = letter.lower()
    if letter not in st["boards_rev"]:
        raise RuntimeError("board %r is not in the revision's board table (%s)" % (letter, ", ".join(sorted(st["boards_rev"]))))
    hand = load_hand_map(attribution_path, st, letter) if attribution_path else None
    b = st["boards_rev"][letter]; proj, stem = b["project"], b["stem"]
    rev_root, prev_root = os.path.join(stage_dir, "rev"), os.path.join(stage_dir, "prev")
    tools_rev = os.path.join(rev_root, "v2", "ecad", "tools")
    bj = json.load(open(os.path.join(tools_rev, "boards", "%s.json" % letter), encoding="utf-8"))
    phase = bj.get("phase") or "UNDECLARED"
    if os.path.exists(out_dir) and os.listdir(out_dir):
        raise RuntimeError("packet directory %s is not empty" % out_dir)
    os.makedirs(out_dir, exist_ok=True)
    work = tempfile.mkdtemp(prefix="review-packet-")
    notes, failures, artefacts = [], [], {}
    finished = False

    def art(rel, what, produced_by):
        artefacts[rel] = {"what": what, "produced_by": produced_by}

    try:
        shutil.copytree(os.path.join(rev_root, "v2"), os.path.join(work, "v2"))
        ecad = os.path.join(work, "v2", "ecad")
        pd = os.path.join(ecad, proj)
        sch_path = os.path.join(pd, stem + ".kicad_sch")
        net_committed = os.path.join(pd, "out", stem + ".net")
        sch_text = open(sch_path, encoding="utf-8", errors="replace").read()
        label = phase_label(sch_text)

        # native files
        nat = os.path.join(out_dir, "native")
        for src, rel, what in (
                (sch_path, "native/%s.kicad_sch" % stem, "the committed schematic at the source revision (KiCad 9 native)"),
                (os.path.join(pd, stem + ".kicad_pro"), "native/%s.kicad_pro" % stem, "its KiCad project file"),
                (os.path.join(pd, "fp-lib-table"), "native/fp-lib-table", "the project's footprint library table"),
                (net_committed, "native/netlist/%s.net" % stem, "the committed netlist (KiCad s-expression) the change report reads"),
                (os.path.join(pd, "out", stem + "-intent.json"), "native/netlist/%s-intent.json" % stem, "the generator's intent file (rails, nodes, bypass declarations)"),
                (os.path.join(pd, "out", stem + ".net.prov.json"), "native/netlist/%s.net.prov.json" % stem, "the netlist's provenance sidecar (generator identity, schematic sha)"),
                (os.path.join(tools_rev, "gen_sch_%s.py" % letter), "native/gen_sch_%s.py" % letter, "the generator that writes the schematic: the design's source of truth, with the finding IDs in its comments"),
                (os.path.join(tools_rev, "boards", "%s.json" % letter), "native/boards-%s.json" % letter, "the board declaration (declared phase, classes)")):
            if os.path.isfile(src):
                write_bytes(os.path.join(out_dir, rel), open(src, "rb").read()); art(rel, what, "copied from the stage (git objects of the source revision)")
            else:
                notes.append("absent at the source revision: %s" % rel)
        comps_rev, nets_rev = regen_compare.parse_net(open(net_committed, encoding="utf-8", errors="replace").read())
        pretty = os.path.join(ecad, "meshsat.pretty")
        used = sorted({c["footprint"].split(":", 1)[1] for c in comps_rev.values()
                       if (c.get("footprint") or "").startswith("meshsat:")})
        for fp in used:
            p = os.path.join(pretty, fp + ".kicad_mod")
            if os.path.isfile(p):
                rel = "native/meshsat.pretty/%s.kicad_mod" % fp
                write_bytes(os.path.join(out_dir, rel), open(p, "rb").read()); art(rel, "project footprint used by this board", "copied from the stage")
            else:
                notes.append("footprint named by the netlist and absent from meshsat.pretty at the source revision: %s" % fp)

        # KiCad exports of the committed schematic
        kv = None if no_kicad else kicad_version()
        kicad = {"version": kv, "steps": {}}
        if kv is None:
            kicad["status"] = "SKIPPED" if no_kicad else "KICAD_CLI_ABSENT"
            notes.append("no KiCad exports: the packet is INCOMPLETE (schematic PDFs, exported netlist parity, BOM, ERC)")
        else:
            kicad["status"] = "RUN"
            xd = os.path.join(work, "export"); os.makedirs(xd, exist_ok=True)
            # kicad-cli runs FROM the schematic's own directory on the bare file name, as build_sch.sh does: given a
            # path from elsewhere, KiCad writes that path into every component's Sheetfile property, and the export
            # then differs from the committed netlist by nothing but the directory it was typed from.
            sch_name = stem + ".kicad_sch"
            steps = [
                ("netlist", ["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", os.path.join(xd, stem + ".net"), sch_name]),
                ("pdf_sheet", ["kicad-cli", "sch", "export", "pdf", "--exclude-drawing-sheet", "-o", os.path.join(xd, stem + "-schematic-sheet.pdf"), sch_name]),
                ("bom", ["kicad-cli", "sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC,${QUANTITY}",
                         "--group-by", "Value,Footprint", "--sort-field", "Reference", "-o", os.path.join(xd, stem + "-bom.csv"), sch_name]),
                ("erc", ["kicad-cli", "sch", "erc", "--severity-all", "--format", "json", "-o", os.path.join(xd, stem + "-erc.json"), sch_name]),
            ]
            for name, cmd in steps:
                rc, log = _run(cmd, cwd=pd)
                kicad["steps"][name] = {"exit": rc, "log_tail": log[-300:]}
            if os.path.isfile(os.path.join(xd, stem + "-schematic-sheet.pdf")):
                rc, log = _run([sys.executable, os.path.join(tools_rev, "sch_pages.py"), sch_path,
                                os.path.join(xd, stem + "-schematic-sheet.pdf"), os.path.join(xd, stem + "-schematic.pdf")])
                kicad["steps"]["pdf_paged"] = {"exit": rc, "tool": "the revision's own tools/sch_pages.py", "log_tail": log[-300:]}
            for fn, rel, what in ((stem + "-schematic.pdf", "schematic/%s-schematic.pdf" % stem,
                                   "the schematic, paged into A3 blocks by the revision's own sch_pages.py (what build_sch.sh publishes)"),
                                  (stem + "-schematic-sheet.pdf", "schematic/%s-schematic-sheet.pdf" % stem, "the whole schematic as one sheet"),
                                  (stem + "-bom.csv", "bom/NOT_FOR_FAB-%s-bom.csv" % stem, "the BOM exported from the committed schematic (build_sch.sh's own fields and grouping), byte for byte as KiCad wrote it; NOT_FOR_FAB in its name because it is a review input, never an order file"),
                                  (stem + "-erc.json", "schematic/%s-erc.json" % stem, "KiCad ERC of the committed schematic, every severity; a report, not a verdict")):
                p = os.path.join(xd, fn)
                if os.path.isfile(p) and os.path.getsize(p) > 0:
                    write_bytes(os.path.join(out_dir, rel), open(p, "rb").read()); art(rel, what, "kicad-cli %s on the committed schematic" % kv)
                else:
                    failures.append("KiCad step did not produce %s" % fn)
            p = os.path.join(xd, stem + ".net")
            if os.path.isfile(p):
                kicad["export_vs_committed_netlist"] = regen_compare.cmp_net(net_committed, p)
                kicad["export_vs_committed_netlist"] = {k: kicad["export_vs_committed_netlist"].get(k) for k in ("result", "content_hash", "comps_changed", "nets_changed", "comps_only_committed", "comps_only_other")}
                if not str(kicad["export_vs_committed_netlist"]["result"]).startswith("PARITY"):
                    failures.append("the netlist exported from the committed schematic differs from the committed netlist")
            ercp = os.path.join(xd, stem + "-erc.json")
            if os.path.isfile(ercp):
                from collections import Counter
                cnt = Counter()
                for sh in json.load(open(ercp)).get("sheets", []):
                    for v in sh.get("violations", []): cnt["%s:%s" % (v.get("severity"), v.get("type"))] += 1
                kicad["erc_by_type"] = dict(sorted(cnt.items()))
            # the previous revision's netlist against its own schematic, so both ends of the report are schematic content
            pb = st["boards_prev"].get(letter)
            if pb:
                psch = os.path.join(prev_root, "v2", "ecad", pb["project"], pb["stem"] + ".kicad_sch")
                pnet = os.path.join(prev_root, "v2", "ecad", pb["project"], "out", pb["stem"] + ".net")
                if os.path.isfile(psch) and os.path.isfile(pnet):
                    pd2 = os.path.join(work, "prev-export"); os.makedirs(pd2, exist_ok=True)
                    shutil.copyfile(psch, os.path.join(pd2, pb["stem"] + ".kicad_sch"))
                    ppro = os.path.join(prev_root, "v2", "ecad", pb["project"], pb["stem"] + ".kicad_pro")
                    if os.path.isfile(ppro):
                        # the net classes of the export live in the project file, not the schematic
                        shutil.copyfile(ppro, os.path.join(pd2, pb["stem"] + ".kicad_pro"))
                    rc, log = _run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o",
                                    os.path.join(pd2, pb["stem"] + ".net"), pb["stem"] + ".kicad_sch"], cwd=pd2)
                    if rc == 0:
                        kicad["prev_export_vs_prev_committed_netlist"] = regen_compare.cmp_net(pnet, os.path.join(pd2, pb["stem"] + ".net"))["result"]

        # the change report
        pb = st["boards_prev"].get(letter)
        chg = {"prev": st["prev"], "rev": st["rev"]}
        gen_rev_text = open(os.path.join(tools_rev, "gen_sch_%s.py" % letter), encoding="utf-8").read()
        gp = os.path.join(prev_root, "v2", "ecad", "tools", "gen_sch_%s.py" % letter)
        gen_prev_text = open(gp, encoding="utf-8").read() if os.path.isfile(gp) else ""
        gen_rev = Generator(gen_rev_text, added_line_numbers(gen_prev_text, gen_rev_text))
        gen_prev = Generator(gen_prev_text, ()) if gen_prev_text else None
        rules = _load_yaml(os.path.join(tools_rev, "pcb_rules.yaml")) or {}
        rule_ids = {r.get("id") for r in (rules.get("rules") if isinstance(rules, dict) else rules) or [] if isinstance(r, dict)}
        if pb:
            pnet = os.path.join(prev_root, "v2", "ecad", pb["project"], "out", pb["stem"] + ".net")
            if os.path.isfile(pnet):
                changes, summary, _, (pins_prev, pins_rev) = netlist_changes(
                    open(pnet, encoding="utf-8", errors="replace").read(), open(net_committed, encoding="utf-8", errors="replace").read())
                chg["summary"] = summary
                chg["changes"] = attribute(changes, gen_rev, gen_prev, rule_ids, pins_rev, pins_prev, hand)
                chg["generator_lines_added"] = len(gen_rev.added)
                chg["attribution"] = ({"by_hand": True, "file": os.path.basename(attribution_path),
                                       "read_by": (hand or {}).get("read_by"), "sha256": sha256_file(attribution_path),
                                       "rows_missing": sorted({c["ref"] for c in changes} - set(hand.get("rows") or {}))}
                                      if hand else {"by_hand": False})
                if hand:
                    write_bytes(os.path.join(out_dir, "changes", "attribution-read-by-hand.yaml"), open(attribution_path, "rb").read())
                    art("changes/attribution-read-by-hand.yaml", "the reading of every changed reference by hand: IDs, the generator "
                        "lines that carry them, the reason in words; the build checked every ID against its lines", "copied from --attribution")
                write_bytes(os.path.join(out_dir, "changes", "prev-%s.net" % st["prev"][:8]), open(pnet, "rb").read())
                art("changes/prev-%s.net" % st["prev"][:8], "the committed netlist at the previous revision", "copied from the stage")
                if gen_prev_text:
                    write_bytes(os.path.join(out_dir, "changes", "prev-%s-gen_sch_%s.py" % (st["prev"][:8], letter)), gen_prev_text.encode("utf-8"))
                    art("changes/prev-%s-gen_sch_%s.py" % (st["prev"][:8], letter), "the generator at the previous revision", "copied from the stage")
                    diff = "".join(difflib.unified_diff(gen_prev_text.splitlines(True), gen_rev_text.splitlines(True),
                                                        "a/gen_sch_%s.py (%s)" % (letter, st["prev"][:8]), "b/gen_sch_%s.py (%s)" % (letter, st["rev"][:8])))
                    write_bytes(os.path.join(out_dir, "changes", "gen_sch_%s.diff" % letter), diff.encode("utf-8"))
                    art("changes/gen_sch_%s.diff" % letter, "the generator diff between the two revisions", "difflib")
        if "changes" not in chg:
            chg["summary"] = None; chg["changes"] = []
            notes.append("no netlist at the previous revision for this board: no change report")

        # identity map
        src_path = sources_path or os.path.join(rev_root, "v2", "vendor", "SOURCES.yaml")
        sources = _load_yaml(src_path) if os.path.isfile(src_path) else {}
        jlc = jlc_table(os.path.join(rev_root, "v2", "release", "revA", "order", "JLC-CERTIFIED.tsv"))
        ident = identity_map(comps_rev, gen_rev, sources, jlc, letter, st["rev"])
        coverage = identity_coverage(ident, sources, letter, st["rev"])

        # interfaces, holds, open decisions
        try: spec = _load_yaml(os.path.join(tools_rev, "pcb_interfaces.yaml"))
        except Exception: spec = {}
        itf = interfaces_for(spec, letter, [n.lstrip("/") for n in nets_rev])
        hd = holds_and_decisions(tools_rev, letter)

        # contracts
        regen = []
        for s in [x.strip().lower() for x in regen_siblings if x.strip()]:
            if kv is None:
                regen.append({"board": s, "result": "NOT_RUN", "why": "no KiCad on this host"}); continue
            sb = st["boards_rev"].get(s)
            if not sb:
                regen.append({"board": s, "result": "NOT_RUN", "why": "not in the revision's board table"}); continue
            regen.append(regen_board(ecad, s, sb["project"], sb["stem"]))
        con = run_contracts(ecad, os.path.join(work, "verdicts-scratch"))
        mine = [c for c in con.get("contracts", []) if letter.upper() in c["boards"]]
        write_bytes(os.path.join(out_dir, "contracts", "check_contracts.log"), con.get("log", "").encode("utf-8"))
        art("contracts/check_contracts.log", "the revision's check_contracts.py output in the packet's work copy", "check_contracts.py, traced")

        # the machine-readable records
        recs = {"changes/changes.json": chg, "bom/parts-identity.json": ident, "bom/sources-coverage.json": coverage,
                "contracts/contracts.json": {"status": con.get("status"), "exit": con.get("exit"), "why": con.get("why"),
                                             "regenerated_siblings": regen, "this_board": mine,
                                             "all_boards_count": len(con.get("contracts", []))},
                "interfaces/interfaces.json": {"interfaces": itf}, "open/holds-and-decisions.json": hd}
        for rel, obj in recs.items():
            write_bytes(os.path.join(out_dir, rel), (json.dumps(obj, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8"))
            art(rel, "machine-readable record, see README.md", "review_packet.py")
        write_bytes(os.path.join(out_dir, IDENTITY_CSV), _identity_csv(ident).encode("utf-8"))
        art(IDENTITY_CSV, "the part identity and footprint map, one row per BOM line (NOT_FOR_FAB: a review input, "
            "never an order file)", "review_packet.py")

        manifest = {
            "kind": PACKET_KIND, "schema": SCHEMA, "banner": BANNER, "readiness": READINESS,
            # the published counts are a reviewed attribution only when a hand reading was supplied and checked; a
            # packet without one says so on its front page (the review cycle of 26 September 2026)
            "change_attribution": "READ_BY_HAND" if hand else "MECHANICAL_ONLY",
            "hold": ([{k: h.get(k) for k in ("decision", "title", "ROUTING_STATUS", "ELECTRICAL_PROTECTION_STATUS",
                                            "FAB_READINESS", "PUBLICATION_STATUS", "permitted", "forbidden")}
                      for h in hd.get("holds", [])] or None),
            "annotation_scan": annotation_scan(sch_text),
            "board": {"letter": letter.upper(), "stem": stem, "project_dir": "v2/ecad/" + proj,
                      "declared_phase": phase, "declared_phase_why": bj.get("_phase_why", "")[:400],
                      "schematic_phase_label": label},
            "source": {"rev": st["rev"], "rev_subject": st["rev_subject"], "rev_date": st["rev_date"],
                       "prev": st["prev"], "prev_subject": st["prev_subject"], "stage_staged_utc": st["staged_utc"]},
            "tool": {"path": "v2/ecad/tools/review_packet.py", "sha256": sha256_file(os.path.abspath(__file__)),
                     "regen_compare_sha256": sha256_file(os.path.join(HERE, "regen_compare.py"))},
            "sources_yaml": {"read": ("a SOURCES.yaml supplied with --sources, identified by its sha256" if sources_path
                                      else "v2/vendor/SOURCES.yaml at the source revision"),
                             "sha256": sha256_file(src_path) if os.path.isfile(src_path) else None},
            "kicad": kicad, "built_utc": utc_now(),
            "host": "not recorded: a packet is public, and a host name says nothing a reviewer can check",
            "complete": bool(kv) and not failures,
            "failures": failures, "notes": notes,
            "counts": dict(change_counts(chg["changes"]),
                       bom_lines=len(ident),
                       bom_lines_joined_by_code=sum(1 for r in ident if r["sources_entries"] and r["order_code_on_line"]),
                       bom_lines_joined_without_code=sum(1 for r in ident if r["sources_entries"] and not r["order_code_on_line"]),
                       sources_entries_naming_board_unjoined=len(coverage["entries_naming_this_board_that_joined_no_line"]),
                       contracts_this_board=len(mine),
                       contracts_pass=sum(c["result"] == "PASS" for c in mine),
                       contracts_fail=sum(c["result"] == "FAIL" for c in mine),
                       contracts_unjudged=sum(c["result"] == "UNJUDGED" for c in mine)),
        }
        # the revision's own .gitignore, read by git's own matcher: a packet file it would keep out of a commit is a
        # packet that would arrive incomplete (26 September 2026: `out/` had kept every native netlist out)
        prefix = "v2/release/review-packets/%s/" % os.path.basename(os.path.normpath(out_dir))
        ign = ignored_paths(os.path.join(stage_dir, "rev", ".gitignore"),
                            [prefix + r for r in sorted(list(artefacts) + ["README.md", "MANIFEST.json", "SHA256SUMS"])])
        manifest["gitignore_check"] = {"as_path": prefix, "ignored": ign if ign is not None else "NOT_RUN (no .gitignore in the stage, or no git)"}
        if ign:
            manifest["failures"].append("the revision's .gitignore would keep %d packet file(s) out of a commit, first %s" % (len(ign), ign[0]))
            manifest["complete"] = False
        sums = {rel: sha256_file(os.path.join(out_dir, rel)) for rel in artefacts}
        readme = render_readme(manifest, chg, ident, mine, regen, con, itf, hd, artefacts, sums, coverage)
        write_bytes(os.path.join(out_dir, "README.md"), readme.encode("utf-8"))
        art("README.md", "this packet's front page: what it is, what it is not, how to verify it", "review_packet.py")
        manifest["artefacts"] = {rel: dict(meta, sha256=sha256_file(os.path.join(out_dir, rel)),
                                           bytes=os.path.getsize(os.path.join(out_dir, rel)))
                                 for rel, meta in sorted(artefacts.items())}
        write_bytes(os.path.join(out_dir, "MANIFEST.json"), (json.dumps(manifest, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8"))
        sums = "".join("%s  %s\n" % (sha256_file(os.path.join(out_dir, r)), r) for r in sorted(list(artefacts) + ["MANIFEST.json"]))
        write_bytes(os.path.join(out_dir, "SHA256SUMS"), sums.encode("utf-8"))
        finished = True
        return manifest
    finally:
        shutil.rmtree(work, ignore_errors=True)
        if not finished:
            shutil.rmtree(out_dir, ignore_errors=True)   # never leave half a packet behind a refusal


def ignored_paths(gitignore_path, rels):
    """The paths of `rels` that `gitignore_path` would keep out of a commit, by git's own matcher, or None when the
    check cannot run (no file, no git)."""
    if not gitignore_path or not os.path.isfile(gitignore_path) or shutil.which("git") is None: return None
    d = tempfile.mkdtemp(prefix="review-packet-ignore-")
    try:
        subprocess.run(["git", "init", "-q", d], check=True, capture_output=True)
        shutil.copyfile(gitignore_path, os.path.join(d, ".gitignore"))
        r = subprocess.run(["git", "-C", d, "check-ignore", "--no-index", "--stdin"], input="\n".join(rels) + "\n",
                           capture_output=True, text=True)
        return sorted(l for l in r.stdout.splitlines() if l)
    finally:
        shutil.rmtree(d, ignore_errors=True)


def _identity_csv(rows):
    s = io.StringIO(); w = csv.writer(s)
    w.writerow(["refs", "qty", "value", "footprint", "lcsc", "sources_entries", "joined_by", "fitted_mpn", "identity",
                "documents (path | revision | sha256)", "jlc_certified_row", "generator_cited_documents"])
    for r in rows:
        ents = r["sources_entries"]
        w.writerow([" ".join(r["refs"]), r["qty"], r["value"], r["footprint"], r["lcsc"],
                    " ".join(e["id"] or "" for e in ents), " / ".join(str(e.get("joined_by") or "") for e in ents),
                    " / ".join(str(e["fitted_mpn"] or "") for e in ents),
                    " / ".join(str(e["identity"] or "") for e in ents),
                    " ; ".join("%s | %s | %s" % (d["path"], d["revision"], d["sha256"]) for e in ents for d in e["documents"]),
                    ("%s %s %s (asked %s)" % (r["jlc_certified_row"]["verdict"], r["jlc_certified_row"]["model"],
                                              r["jlc_certified_row"]["brand"], r["jlc_certified_row"]["asked"])
                     if r["jlc_certified_row"] else ""),
                    " ".join(r["generator_cited_documents"])])
    return s.getvalue()


def ev_excerpt(c):
    d = (c.get("evidence") or {}).get("direct") or {}
    return (d.get("excerpt") or "")[:300]


def _md(s):
    return str(s if s is not None else "").replace("|", "/").replace("\n", " ")


def render_readme(m, chg, ident, mine, regen, con, itf, hd, artefacts, sums, coverage=None):
    b, src = m["board"], m["source"]
    L = []
    w = L.append
    w("# Review packet: board %s (%s) at %s\n" % (b["letter"], b["stem"], src["rev"][:8]))
    w("**%s**\n" % m["banner"])
    w("**%s.**" % m["readiness"] + " No file here is an order file; the two BOM files carry NOT_FOR_FAB in their names.")
    if m.get("change_attribution") == "MECHANICAL_ONLY":
        w("**CHANGE ATTRIBUTION: MECHANICAL ONLY.** No hand reading was supplied (`--attribution`): the change counts below "
          "credit only the IDs written in each part's own comment, which can include IDs cited there as context. They are "
          "not a reviewed attribution; do not send this packet to a reviewer as one.")
    for h in m.get("hold") or []:
        w("This board is HELD by decision %s (%s), in the hold's own words: ROUTING_STATUS %s, ELECTRICAL_PROTECTION_STATUS %s, "
          "FAB_READINESS %s, PUBLICATION_STATUS %s. The hold permits: \"%s\". It forbids: \"%s\"." % (
              h.get("decision"), _md(h.get("title")), h.get("ROUTING_STATUS"), h.get("ELECTRICAL_PROTECTION_STATUS"),
              h.get("FAB_READINESS"), h.get("PUBLICATION_STATUS"), _md(" ".join(str(h.get("permitted") or "").split())),
              _md(" ".join(str(h.get("forbidden") or "").split()))))
    w("")
    w("| | |\n|---|---|")
    w("| Board | %s, `%s` |" % (b["letter"], b["project_dir"]))
    w("| Source revision | `%s` (%s), %s |" % (src["rev"], _md(src["rev_subject"]), src["rev_date"]))
    w("| Compared with | `%s` (%s) |" % (src["prev"], _md(src["prev_subject"])))
    w("| Declared phase | %s, from `tools/boards/%s.json`: the phase of the board's committed LAYOUT. The layout is not part of this packet and is not judged by it (rule SCH-002 decides whether it carries this netlist). The schematic's own title-block label is %s |"
      % (b["declared_phase"], b["letter"].lower(), b["schematic_phase_label"] or "absent"))
    w("| Complete | %s |" % ("yes" if m["complete"] else "NO: " + _md("; ".join(m["failures"] + m["notes"]) or "see MANIFEST.json")))
    w("| Built | %s with KiCad %s, tool sha256 `%s` |" % (m["built_utc"], m["kicad"].get("version") or "(none)", m["tool"]["sha256"][:16]))
    w("| Part sources read | %s, sha256 `%s` |\n" % (m["sources_yaml"]["read"], (m["sources_yaml"]["sha256"] or "none")[:16]))
    w("## What this packet is, and is not\n")
    w("- It is a review input for a qualified reviewer: the schematic of one board exactly as committed at the source revision, "
      "with what changed since the previous revision and why, the parts and their primary sources, and the interfaces it shares with other boards.")
    w("- It is NOT a release. No layout, fabrication, order or approval follows from it. Hardware state: unbuilt prototype design.")
    w("- It is desk material only: no bench measurement, EMC, thermal or environmental test exists for this board.")
    w("- The review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`, section 5) asked for it.\n")
    w("## Contents\n")
    w("| File | What | sha256 (first 16) |\n|---|---|---|")
    for rel, meta in sorted(artefacts.items()):
        if rel == "README.md": continue
        w("| `%s` | %s | `%s` |" % (rel, _md(meta["what"]), (sums.get(rel) or "")[:16]))
    w("\nVerify: `python3 v2/ecad/tools/review_packet.py verify <this folder>` or `sha256sum -c SHA256SUMS` inside it. "
      "`MANIFEST.json` carries the full record.\n")
    k = m["kicad"]
    w("## Schematic exports\n")
    if k.get("status") == "RUN":
        e = k.get("export_vs_committed_netlist") or {}
        w("- KiCad %s exported the PDFs, BOM, ERC and netlist from the committed schematic." % k.get("version"))
        w("- The exported netlist against the committed netlist: **%s** (regen_compare; PARITY_AFTER_NOISE means only the export's own path, date and tool differ)." % e.get("result"))
        if k.get("prev_export_vs_prev_committed_netlist"):
            w("- At the previous revision, the same comparison: **%s**, so both ends of the change report are schematic content." % k["prev_export_vs_prev_committed_netlist"])
        if k.get("erc_by_type"):
            w("- ERC, every severity, as a report and not a verdict (the project's gate `erc_gate.py` applies the board's allow list): " +
              ", ".join("%s %d" % (t, n) for t, n in k["erc_by_type"].items()) + ".")
        warned = sorted(n for n, s in (k.get("steps") or {}).items() if "annotation errors" in (s.get("log_tail") or ""))
        if warned:
            a = m.get("annotation_scan") or {}
            w("- kicad-cli printed \"schematic has annotation errors\" on the %s export%s. KiCad does not say which symbol it means. "
              "A text reading of the committed schematic finds %s repeated (reference, unit) and %s unannotated reference among "
              "%d symbol instances, so the cause is NOT ESTABLISHED; the exported netlist's parity above is what shows the "
              "export carries the committed circuit." % (
                  " and ".join(warned), "s" if len(warned) > 1 else "",
                  ", ".join(a.get("duplicate_reference_unit") or []) or "no", ", ".join(a.get("unannotated") or []) or "no",
                  a.get("instances", 0)))
    else:
        w("- **No KiCad exports in this packet (%s).** The schematic PDFs, the BOM export and the ERC report are missing; the packet is incomplete." % k.get("status"))
    w("")
    s = chg.get("summary")
    w("## Changes against `%s`\n" % src["prev"][:8])
    if s:
        w("Components %d to %d, nets %d to %d: %d added, %d removed, %d changed. Generator lines added or changed: %d. "
          "Details per reference, with the generator lines and the comment each ID was read from, are in `changes/changes.json`.\n"
          % (s["components"][0], s["components"][1], s["nets"][0], s["nets"][1], s["added"], s["removed"], s["changed"],
             chg.get("generator_lines_added", 0)))
        at = chg.get("attribution") or {}
        cn = change_counts(chg["changes"])
        if at.get("by_hand"):
            w("**How each row was read.** Every changed reference was read by hand (`changes/attribution-read-by-hand.yaml`, %s): "
              "the IDs, the generator lines at `%s` that carry them, and the reason in words. The build refused the file unless every ID "
              "is written on its cited lines and every cited range is tied to the change (it names the reference or one of its nets, "
              "is the statement's own comment or its section header, or the row states the tie). The mechanical reading stays in "
              "`changes/changes.json` (`evidence.automatic`) beside each row, with `agrees` saying whether it matches; it differs on "
              "%d of %d rows, mostly because it credits every ID written in a part's own comment, including IDs cited there as "
              "context.%s\n"
              % (_md(at.get("read_by") or "reader not named"), src["rev"][:8], cn["hand_disagrees_with_automatic"], cn["changes"],
                 (" Rows not in the file, read mechanically only: " + ", ".join(at["rows_missing"]) + ".") if at.get("rows_missing") else ""))
        else:
            w("**How each row was read.** Mechanically only: an ID is credited when it sits in the defining statement's OWN comment "
              "(the block directly above it or a comment on its lines) on a line added since `%s`. A comment reached past another "
              "statement, above an enclosing if/try/for, or only mentioning the reference is a candidate: the row reads "
              "UNVERIFIED_ATTRIBUTION and its IDs are candidates, never credited.\n" % src["prev"][:8])
        w("**Counts.** %d changes: %d carry a finding ID; %d carry only an owner ruling, a decision or a rule ID; %d carry no ID of "
          "any kind; %d are UNVERIFIED_ATTRIBUTION. So **%d changes have no finding ID**. Finding IDs include the round records' own "
          "item IDs (R4D-1, R4E-02, RP-17), which are the session's records of that round.\n"
          % (cn["changes"], cn["with_finding_id"], cn["authority_or_rule_only"], cn["no_id_of_any_kind"], cn["unverified_attribution"],
             cn["without_finding_id"]))
        w("| Ref | Kind | What changed | Finding IDs | Rulings and decisions | Rules | Status | Read | Generator lines (%s) |\n|---|---|---|---|---|---|---|---|---|"
          % ("cited" if at.get("by_hand") else "statement"))
        for c in chg["changes"]:
            if c["kind"] == "CHANGED":
                what = "; ".join(["%s: %s -> %s" % (f, _md(v[0])[:60], _md(v[1])[:60]) for f, v in c["fields"].items()] +
                                 ["pin %s: %s -> %s" % (p, v[0], v[1]) for p, v in list(c["pins_moved"].items())[:6]] +
                                 (["and %d more pins" % (len(c["pins_moved"]) - 6)] if len(c["pins_moved"]) > 6 else []))
            else:
                what = "%s, %s, %s" % (_md(c["value"])[:80], _md(c["footprint"]), c["lcsc"] or "no LCSC code")
            ev = c["evidence"]
            spans = ev["hand"]["cite"] if "hand" in ev else ev["spans"]
            lines = ", ".join("%d-%d" % (a, b_) if a != b_ else str(a) for a, b_ in spans[:4]) or "not found"
            fid = ", ".join(c["finding_ids"]) or "none"
            if c["status"] == UNVERIFIED:
                fid = "none credited; candidates " + (", ".join(ev["automatic"]["candidate_ids"]) or "none")
            w("| %s | %s | %s | %s | %s | %s | %s | %s | %s %s |" % (
                c["ref"], c["kind"], _md(what), fid, ", ".join(c["authority_ids"]), ", ".join(c["rule_ids"]), c["status"], c["read"],
                "gen_sch_%s.py%s" % (b["letter"].lower(), "" if ev.get("hand") or ev["generator_side"] == "rev" else " (prev)"), lines))
        nof = [c for c in chg["changes"] if not c["finding_ids"]]
        if nof:
            w("\n**The %d changes with no finding ID, and their reason**\n" % len(nof))
            for c in nof:
                h = c["evidence"].get("hand") or {}
                if c["status"] == TRACED: kind = "ruling, decision or rule only: " + ", ".join(c["authority_ids"] + c["rule_ids"])
                elif c["status"] == NO_ID: kind = "no ID of any kind"
                else: kind = "attribution unverified; candidates " + (", ".join(c["evidence"]["automatic"]["candidate_ids"]) or "none")
                extra = ("; round record: " + h["record"]) if h.get("record") else ""
                w("- %s (%s): %s%s" % (c["ref"], _md(kind + extra), _md(h.get("why") or ev_excerpt(c) or "no reason in words on its statement"), ""))
            w("")
        w("IDs found only on unchanged lines are listed in `changes/changes.json` as `context` and never counted as the change's. "
          "The generator diff is `changes/gen_sch_%s.diff`.\n" % b["letter"].lower())
        if s["nets_renamed"]:
            w("Nets renamed (same pins, new name): " + ", ".join("%s -> %s" % tuple(x) for x in s["nets_renamed"]) + ".\n")
    else:
        w("No change report: the previous revision holds no netlist for this board.\n")
    w("## Part identity and footprints\n")
    by_code = [r for r in ident if r["sources_entries"] and r["order_code_on_line"]]
    no_code = [r for r in ident if r["sources_entries"] and not r["order_code_on_line"]]
    rest = [r for r in ident if not r["sources_entries"]]
    w("%d BOM lines. %d carry an entry in `v2/vendor/SOURCES.yaml` (identity, grade and the held documents with revision and sha256): "
      "%d joined by the exact LCSC code of the line, and %d lines that carry NO LCSC code, joined because the entry names this board "
      "and either its `where`, read at the revision its line number was written against, points at the line's defining statement "
      "while naming the reference or the part, or its fitted order code is written in the line's value. The other %d lines carry no "
      "entry. SOURCES.yaml's own header says which parts it covers (its criteria (a) to (c)) and its `owed` list names the entries "
      "still owed; this packet does not judge criticality. `jlc_certified_row` is the certification table's row where it has one: "
      "that table was cut from older deliverables and a CERTIFIED there is not proof of identity (SOURCES.yaml header). "
      "Full map: `%s` and `bom/parts-identity.json`; which entries name this board and what each joined: `bom/sources-coverage.json`.\n"
      % (len(ident), len(by_code) + len(no_code), len(by_code), len(no_code), len(rest), IDENTITY_CSV))

    def table(rows, with_how):
        w("| Refs | Value | Footprint | LCSC | SOURCES.yaml | %sDocuments |\n|---|---|---|---|---|%s---|" % (
            "Joined by | " if with_how else "", "---|" if with_how else ""))
        for r in rows:
            docs = "; ".join("`%s` (%s)" % (d["path"], _md(d["revision"])[:40]) for e in r["sources_entries"] for d in e["documents"])
            how = ("%s | " % _md("; ".join(e["joined_by"] for e in r["sources_entries"]))) if with_how else ""
            w("| %s | %s | `%s` | %s | %s | %s%s |" % (" ".join(r["refs"][:8]) + (" ..." if len(r["refs"]) > 8 else ""),
                                                     _md(r["value"])[:60], r["footprint"], r["lcsc"] or "none",
                                                     ", ".join(e["id"] for e in r["sources_entries"]), how, docs))
        w("")
    if by_code:
        w("**Joined by the line's LCSC code**\n")
        table(by_code, False)
    if no_code:
        w("**Lines with no LCSC code, joined to the entry that covers them.** No order code fixes the maker of such a line, so "
          "the entry's identity verdict speaks for the part it names, not for a purchase; the entry says what the line's order "
          "code is, or that it is not pinned.\n")
        table(no_code, True)
    un = (coverage or {}).get("entries_naming_this_board_that_joined_no_line") or []
    if coverage is not None:
        if un:
            w("**Entries that name board %s and joined no BOM line**, each with the reason read from the entry: %s.\n" % (
                b["letter"], "; ".join("`%s` (%s)" % (u["id"], _md(u["why"])) for u in un)))
        else:
            w("Every entry of SOURCES.yaml that names board %s (and is on this revision's generators) joined at least one BOM "
              "line here (%d entries).\n" % (b["letter"], len(coverage.get("entries_naming_this_board") or [])))
        if coverage.get("entries_declaring_no_placed_part"):
            w("Entries that name board %s for a part placed on no schematic (by their own `placed_part: false`), so they join "
              "no BOM line by design: %s.\n" % (b["letter"], ", ".join("`%s`" % x for x in coverage["entries_declaring_no_placed_part"])))
    w("## Cross-board and harness contracts that touch this board\n")
    if con.get("status") == "RUN":
        p_ = sum(c["result"] == "PASS" for c in mine); f_ = sum(c["result"] == "FAIL" for c in mine); u_ = sum(c["result"] == "UNJUDGED" for c in mine)
        w("The revision's own `check_contracts.py`, run in this packet's work copy (never in the repository), traced so each contract carries "
          "the boards it names: %d name board %s: **%d PASS, %d FAIL, %d UNJUDGED**." % (len(mine), b["letter"], p_, f_, u_))
        for r in regen:
            w("- Board %s was regenerated from its generator at the source revision in the work copy, because its committed netlist "
              "predates the widened generator identity: gen_sch exit %s, build_sch exit %s, regenerated netlist against the committed one: **%s**. "
              "Board %s's contracts are therefore judged against its circuit AS COMMITTED at the source revision (its own corrections are not in it)."
              % (r.get("board", "?").upper(), r.get("gen_sch_exit"), r.get("build_sch_exit"), r.get("parity_with_committed_netlist", r.get("result")), r.get("board", "?").upper()))
        w("\n| Result | Contract | Boards | Where |\n|---|---|---|---|")
        for c in mine:
            w("| %s | %s%s | %s | `%s` |" % (c["result"], _md(c["text"]), (" (" + _md(c["detail"])[:120] + ")") if c["detail"] else "",
                                           ", ".join(c["boards"]), c["defined_at"]))
    else:
        w("Not run: %s." % con.get("why"))
    w("")
    w("## Interfaces declared for this board (`tools/pcb_interfaces.yaml`)\n")
    if itf:
        for i in itf:
            ns = lambda v, unit: ("%s %s" % (v, unit)) if v is not None else "not stated"
            w("- **%s**: %s. Impedance %s (tolerance %s), intra-pair %s, maximum length %s. Nets here: %s. Source: %s." % (
                i["interface"], _md(i["what"]), ns(i["impedance_ohm"], "ohm"), ns(i["impedance_tol_percent"], "%"),
                ns(i["intra_pair_mm"], "mm"), ns(i["max_length_mm"], "mm"),
                ", ".join(i["nets_on_this_board"][:12]) + (" ..." if len(i["nets_on_this_board"]) > 12 else "") or "none match",
                "; ".join("%s, %s (`%s`)" % (_md(x["title"]), _md(x["clause"]), x["path"]) for x in i["sources"])))
    else:
        w("- None declared.")
    w("")
    w("## Holds and open decisions\n")
    for h in hd.get("holds", []):
        w("- Hold on this board: decision %s, %s: %s, %s, %s." % (h.get("decision"), _md(h.get("title")), h.get("ELECTRICAL_PROTECTION_STATUS"),
                                                                 h.get("FAB_READINESS"), h.get("PUBLICATION_STATUS")))
    if not hd.get("holds"): w("- No hold in `tools/pcb_board_holds.yaml` names this board.")
    for d in hd.get("open_decisions", []):
        w("- Open decision %s: %s (boards: %s)." % (d["n"], _md(d["title"]), _md(d["boards"])))
    w("")
    w("## Not in this packet\n")
    w("- A layout. The board file of the declared phase is not included and nothing here judges it; whether it carries this netlist is rule SCH-002's question.")
    w("- Change marks on the schematic sheets. The PDFs are plain exports of the committed schematic; what changed is marked in "
      "the change table above, by reference, with the generator lines that carry each finding ID.")
    w("- Calculations and fault-state diagrams. Where the review asks for them (battery protection, board P; the charger state sequence, board A) "
      "they are separate work items with their own owner; this packet carries the circuit they will be judged against.")
    w("- Physical evidence of any kind.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ verify
def verify(packet):
    m = json.load(open(os.path.join(packet, "MANIFEST.json"), encoding="utf-8"))
    bad = []
    for rel, meta in m.get("artefacts", {}).items():
        p = os.path.join(packet, rel)
        if not os.path.isfile(p): bad.append("missing " + rel)
        elif sha256_file(p) != meta["sha256"]: bad.append("changed " + rel)
    sums = os.path.join(packet, "SHA256SUMS")
    if os.path.isfile(sums):
        for line in open(sums, encoding="utf-8"):
            h, rel = line.rstrip("\n").split("  ", 1)
            p = os.path.join(packet, rel)
            if not os.path.isfile(p) or sha256_file(p) != h: bad.append("SHA256SUMS: " + rel)
    else:
        bad.append("missing SHA256SUMS")
    listed = set(m.get("artefacts", {})) | {"MANIFEST.json", "SHA256SUMS"}
    for d, _, fs in os.walk(packet):
        for f in fs:
            rel = _rel(os.path.join(d, f), packet)
            if rel not in listed: bad.append("not in the manifest: " + rel)
    return bad


# ------------------------------------------------------------------------------------------------ command line
def _opt(argv, name, default=None):
    if name in argv:
        i = argv.index(name)
        if i + 1 < len(argv): return argv[i + 1]
    return default


def _out_for(argv, stage_rec, letter):
    out = _opt(argv, "--out")
    if out: return out
    root = _opt(argv, "--out-root")
    if not root: raise RuntimeError("give --out DIR or --out-root ROOT")
    tools = stage_rec["_tools"]
    phase = json.load(open(os.path.join(tools, "boards", "%s.json" % letter.lower()))).get("phase") or "UNDECLARED"
    return os.path.join(root, "%s-%s-%s" % (letter.upper(), phase, stage_rec["rev"][:8]))


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__); return 2
    cmd, a = argv[0], argv[1:]
    try:
        if cmd == "stage":
            rec = stage(_opt(a, "--repo", "."), _opt(a, "--rev"), _opt(a, "--prev"), _opt(a, "--out"))
            print("staged %s (prev %s): %d files, boards %s" % (rec["rev"][:12], rec["prev"][:12], len(rec["files"]), ",".join(sorted(rec["boards_rev"]))))
            return 0
        if cmd in ("build", "all"):
            letter = _opt(a, "--board")
            if not letter: raise RuntimeError("give --board L")
            tmp = None
            if cmd == "all":
                tmp = tempfile.mkdtemp(prefix="review-packet-stage-")
                sd = os.path.join(tmp, "stage")
                stage(_opt(a, "--repo", "."), _opt(a, "--rev"), _opt(a, "--prev"), sd)
            else:
                sd = _opt(a, "--stage")
            try:
                rec = load_stage(sd); rec["_tools"] = os.path.join(sd, "rev", "v2", "ecad", "tools")
                out = _out_for(a, rec, letter)
                regen = (_opt(a, "--regen-siblings", "") or "").split(",")
                m = build(sd, letter, out, _opt(a, "--sources"), regen, "--no-kicad" in a, _opt(a, "--attribution"))
            finally:
                if tmp: shutil.rmtree(tmp, ignore_errors=True)
            k = m["counts"]
            print("packet %s: complete=%s, %d artefacts, %d changes (%d with a finding ID, %d ruling/decision/rule only, %d NO_ID_OF_ANY_KIND, "
                  "%d UNVERIFIED_ATTRIBUTION; %d read by hand), contracts %d (%d PASS, %d FAIL, %d UNJUDGED)" % (
                out, m["complete"], len(m["artefacts"]), k["changes"], k["with_finding_id"], k["authority_or_rule_only"],
                k["no_id_of_any_kind"], k["unverified_attribution"], k["read_by_hand"],
                m["counts"]["contracts_this_board"], m["counts"]["contracts_pass"], m["counts"]["contracts_fail"], m["counts"]["contracts_unjudged"]))
            return 0 if (m["complete"] or "--no-kicad" in a) else 1
        if cmd == "verify":
            bad = verify(a[0])
            print("OK" if not bad else "MISMATCH:\n  " + "\n  ".join(bad))
            return 0 if not bad else 1
    except RuntimeError as e:
        print("review_packet: %s" % e, file=sys.stderr); return 2
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
