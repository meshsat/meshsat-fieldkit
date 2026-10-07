#!/usr/bin/env python3
"""Set 32's rows for the adoption pages (MESHSAT-1357, 6 October 2026, W95): `v2/docs/records/int32/ENTRY-PAGES.patch.md` holds
exact rows (S-nn for START-HERE.md, U-nn for SUPPLIER-HANDOVER.md, L-nn for LAYER-STATUS.md, P-nn for EXECUTION-PLAN.md), each with
its page, its line, one line of old text, the new text and its basis, in the form of set 31's rows
(`records/int31/ENTRY-PAGES.patch.md`, W39, applied by W65).

The revision the rows are written for is the four pages as set 32's integration holds them before the rows are applied: main after
set 31's adoption (AT, ad757edb), merged with the four other branches set 32's chain pins (PINS) and the chain's step a5 (W42's
apply_supplier_0e_pointer.py); fnd/w34pdftext adds 7 lines to SUPPLIER-HANDOVER.md's section 7, so U-16 reads line 414 there, not
main's 407 (W99's B1). Which pages this test reads is decided by the tree's own START-HERE.md, its line 3:
  "Current revision: set 31"  the tree holds set 31's adoption (the integrated tree after the chain's merges): the rows are read
                              against the tree's own pages (W99: the right mechanism);
  "Current revision: set 32"  the rows are applied: every row's new text must stand on its page (a token or the value filled), and
                              set 32's blocks stand first under their headings and last in the plan;
  anything else               this branch before the integration: main's pages at AT, read through git with no fill (no token is left
                              on them; W99's C4, where W95 read fnd/adopt31's b06ee99f with set 31's fill in memory), each pinned
                              branch's own change to the page applied in memory (its diff from its merge base with AT; a change an
                              earlier pin already made is not applied twice) and step a5's apply() from the script at its pin. Where
                              AT or a pin is absent from the repository, Skip with that reason.
The record (its paragraph "What the rows are read against") gives why git and not copies under `inputs/` (taken under the owner's
standing rule of 26 September 2026, W95, restated by W102; reversal named there).

What fails here: a row whose page, line or old text does not hold on the pages read (the old text not exactly once on its line, or
not once on the line the rows before it on that line left, applied bottom-up per page); an old text that is not one line or carries a
token; a new text equal to its old text; an "after line" row whose new text does not begin with the whole old text; a row id out of
sequence or a page other than its prefix's; a token in a new text other than the CANDIDATE, ADOPTION and GATE tokens; a token of the
set left after the fill's stage (read from RESULT's section 1 role rows, as test_res32 reads them) or a filled value that is not the
role's commit at the place the template revision holds the token; a citation `<sha>:path:N` whose quote is not on that line at that
commit; a quote followed by its file and section that is not in that section of that file; a count the rows type that is not the
tree's classification's over the branch rows (the adopted one at the adoption, W99's C1), whitespace flattened, with every
occurrence required (C5), or not the pages' for sets 31 and 30, or a typed figure (generators, numbers, MiB, held-back texts) not
the record's; a claim the rows carry (the DESK gate, the three claims in full, no circuit change, no item raised to MET, no
independent check of the engineering, each "UNREVIEWED since cx46") missing from its row (W99's N2); set 31's known item without its
source (paragraph 0a of l4e7_p0sol.out at the candidate) or said to be corrected while that paragraph still names set 30's
integrator, or, after the fill, a value that is not in that paragraph (W99's C2); a set 32 block not directly under its layer's
heading above the set 31 block, or the plan's entry not after set 31's; the record not naming the patch file in the way the fill
tool finds it; an em or en dash; the paragraph after the title not the DONE / NOT DONE / NEXT line. Each predicate is also run on a
mutant it must refuse.

W113's restatement for W110's C2 (7 October 2026): after the fill the known item's value must also be absent from set 31's paragraph
0a (at d0e283aa, the candidate that carries the KNOWN ITEM), so that it is a clause the regenerated paragraph adds, not one both print;
the rows' words "is planned to be corrected" stay until the regenerated output exists (no basis can be stated before it), and the
coordinator restates them, with the pattern KNOWN, at the fill if paragraph 0a no longer names set 30's integrator.

W113's restatement (7 October 2026, from 01:50 CEST, on W106's N-c and W110's M3, which found a re-wrapped candidate_guard line passing
every test while the fill tool's three-host NOTE fell silent): P-01's candidate_guard line is one physical line holding its GATE token
(p_rows), and after the fill its value is three parts joined by "; ", each "candidate_guard: PASS candidate <the candidate>" as
candidate_guard prints it on each host (p_fill; set 31's guard logs give the form); each with a mutant it refuses.

W119's restatement at set 32's adoption (7 October 2026; W116's finding 1, W110's C2), written by apply_known32.py only when paragraph
0a of l4e7_p0sol.out at the candidate no longer prints set 31's history sentence (set 30's integrator) and prints WP-B's clause as
para_0a's source gives it: rows S-05, U-03, L-02 and P-01 say the known item is corrected (RESTATED, the same blocks on the pages);
KNOWN takes that wording only and p_known refuses the planned wording (KNOWN_PLANNED); p_fill reads its template through RESTATED.
The restated rows hold after the fill only: before it no candidate is named, so "is corrected" is refused there. W123 (W121's
findings 3 and 6): RESTATED also carries three blocks of the patch file's own prose (on no page), and a self-mutant pins p_known's
guard: set 31's paragraph 0a appended to the candidate's output (through _C) makes every restated row refused.

This file never writes a token of the fill tool literally (it builds them with T()), so the placeholder check of set 32's chain needs
no deferral row for it. Read-only: git is read with `git show`, `git log`, `git cat-file`; nothing is written. No pytest is needed
(tests/run.py runs the `t_` functions); `test_` aliases let pytest collect them."""
import os
import re
import subprocess

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
REC = "v2/docs/records/int32"
PATCH = REC + "/ENTRY-PAGES.patch.md"
RESULT = REC + "/RESULT.md"
CLASS = REC + "/CLASSIFICATION.md"
AT = "ad757edb1be7e0fe3b586f986d2d704c9836fdcf"      # main after set 31's adoption (the fill's second run), W99's C4
PINS = ("62300318cbf256a178659d7635ecfd4a318c47d3",   # set 32's chain pins other than this branch (_runs/int32/chain.sh SRC_*):
        "9210ab541e8144af530f928c1da98b96f90c89fd",   # fnd/w34pdftext, fnd/s32attr, fnd/s32small, fnd/l4e7cache
        "7b7219a7d0a695b6b866435116905964a68f5578",
        "5ee1e66eb8787a788647305509ae6c2700144d9a")
A5 = ("62300318cbf256a178659d7635ecfd4a318c47d3", "v2/docs/records/w42cite/apply_supplier_0e_pointer.py")  # the chain's step a5
P0SOL = "v2/docs/records/l4e7/l4e7_p0sol.out"         # set 31's known item: its paragraph 0a at the candidate (W99's C2)
S31_CAND = "d0e283aa52ceb7f303358862b539161b721475e5"  # W113 (W110's C2): set 31's candidate, whose paragraph 0a carries the KNOWN ITEM
KNOWN_ROWS = ("S-05", "U-03", "L-02", "P-01")
# W113 (W106's N-c, W110's M3): P-01's candidate_guard line stands as ONE physical line with its GATE on it, so the fill tool's suggestion
# (fill_res.py's "candidate_guard check, every host", hosts=3) reaches the token and its three-host NOTE fires; after the fill the value
# is the three hosts' PASS lines joined by "; ", each as candidate_guard prints it on set 31's hosts
# (`<worktrees>/_runs/int31s1/guard.log:2`, `candidate_guard: PASS candidate 5f25daf3762ecd69c8764bf60de81a80f4119eab: 997 evidence ...`)
GUARD_LINE = "The candidate_guard check, every host, its PASS line on each host in one value: `"
GUARD_HOSTS = 3
GUARD_PART = re.compile(r"candidate_guard: PASS candidate ([0-9a-f]{8,40})\b")
PAGES = {"S": "v2/docs/handover/START-HERE.md", "U": "v2/docs/handover/supplier/SUPPLIER-HANDOVER.md",
         "L": "v2/docs/handover/LAYER-STATUS.md", "P": "v2/docs/EXECUTION-PLAN.md"}
COUNTS = {"S": 15, "U": 16, "L": 6, "P": 1}
ALLOWED = ("CANDIDATE", "ADOPTION", "GATE")
LAYERS = ("## Layer 4. ", "## Layer 5. ", "## Layer 8. ", "## Layer 9. ", "## Layer 12. ")
TOK = re.compile(r"__([A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*)__")
HEAD = re.compile(r"^### ([SULP])-(\d\d)\. `([^`]+)`, (after )?line (\d+): (.+)$", re.M)
BODY = re.compile(r"\A\s*Old text:\n```text\n(.*?)\n```\nNew text:\n```text\n(.*?)\n```\nBasis: (\S.*?)\s*\Z", re.S)
GIT_ANCHOR = re.compile(r"`([0-9a-f]{8,40}):([^`:\s]+):(\d+)` `((?:[^`\\]|\\.)+)`")
QUOTE_SEC = (re.compile(r"((?:\"[^\"]+\"; )*\"[^\"]+\") \(`([^`]+\.md)`,\s+section (\w+)\)"),
             re.compile(r"`([^`]+\.md)`, section (\w+): \"([^\"]+)\"\)"))
DASHES = ("\u2014", "\u2013")


def T(name):
    """A fill-tool token by its name (never written literally in this file)."""
    return "__%s__" % name


def _git(*args):
    try:
        r = subprocess.run(["git", "-C", REPO] + list(args), capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    if r.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(args), r.stderr.strip()))
    return r.stdout


def _has(sha):
    try:
        r = subprocess.run(["git", "-C", REPO, "cat-file", "-e", sha + "^{commit}"], capture_output=True, text=True)
    except OSError as e:
        raise Skip("no git here: %s" % e)
    return r.returncode == 0


_C = {}


def _show(rev, path):
    k = (rev, path)
    if k not in _C:
        _C[k] = _git("show", "%s:%s" % (rev, path))
    return _C[k]


def _read(rel):
    p = os.path.join(REPO, rel)
    if not os.path.isfile(p):
        raise AssertionError("%s is missing" % rel)
    return open(p, encoding="utf-8").read()


# ---- the rows ----

def _rows(text):
    """[(id, prefix, number, page, after, line, old, new, basis)] in file order, or a list of problems (strings) where a row is malformed."""
    heads = list(HEAD.finditer(text))
    rows, bad = [], []
    ends, pos, fence = [], 0, False      # the headings outside the code fences end a row's body
    for ln in text.split("\n"):
        if ln.startswith("```"):
            fence = not fence
        elif not fence and re.match(r"#{2,3} ", ln):
            ends.append(pos)
        pos += len(ln) + 1
    for m in heads:
        end = min([e for e in ends if e > m.start()] + [len(text)])
        body = BODY.match(text[m.end():end])
        rid = "%s-%s" % (m.group(1), m.group(2))
        if not body:
            bad.append("%s: its body is not Old text / New text / Basis" % rid)
            continue
        rows.append((rid, m.group(1), int(m.group(2)), m.group(3), bool(m.group(4)), int(m.group(5)), body.group(1), body.group(2),
                     " ".join(body.group(3).split())))
    return rows if not bad else bad


def _tokens(s):
    return TOK.findall(s)


def p_rows(text):
    rows = _rows(text)
    if rows and isinstance(rows[0], str):
        return rows
    bad = []
    seen = {}
    for rid, pre, num, page, after, line, old, new, basis in rows:
        seen.setdefault(pre, []).append(num)
        if page != PAGES[pre]:
            bad.append("%s names %s, not its prefix's page %s" % (rid, page, PAGES[pre]))
        if not old or "\n" in old:
            bad.append("%s: the old text is not one line" % rid)
        if "__" in old:
            bad.append("%s: the old text carries a token" % rid)
        if new == old:
            bad.append("%s: the new text equals the old text" % rid)
        if after and not new.startswith(old + "\n"):
            bad.append("%s: an 'after line' row whose new text does not begin with the whole old text" % rid)
        for t in _tokens(new):
            if t not in ALLOWED:
                bad.append("%s: the token %s is not one of the rows' tokens %s" % (rid, T(t), ALLOWED))
        for p in re.findall(r"`(v2/[^`\s]+)`", basis):
            if not os.path.exists(os.path.join(REPO, p.rstrip("/"))) and p.split("/")[3:4] != ["int31"]:
                bad.append("%s: its basis names %s, absent from the tree" % (rid, p))
        if not basis:
            bad.append("%s: no basis" % rid)
        if rid == "P-01":       # W113 (W106's N-c): the guard line unwrapped, its GATE (or the value the fill wrote) on that line
            gl = [x for x in new.split("\n") if "candidate_guard check, every host" in x]
            if len(gl) != 1 or not re.fullmatch(re.escape(GUARD_LINE) + r"(?:%s|[^`\n]+)`\." % re.escape(T("GATE")), gl[0]):
                bad.append("P-01: the candidate_guard line is not one physical line %r<GATE or its value>`. (W106's N-c)" % GUARD_LINE[:40])
    for pre, n in COUNTS.items():
        if seen.get(pre) != list(range(1, n + 1)):
            bad.append("the %s rows are %s, not 01 to %02d in order" % (pre, seen.get(pre), n))
    return bad


def p_hygiene(text):
    bad = []
    if any(d in text for d in DASHES):
        bad.append("the patch file carries an em or en dash")
    paras = [" ".join(p.split()) for p in re.split(r"\n\s*\n", text) if p.strip()]
    first = paras[1] if len(paras) > 1 else ""
    if not first.startswith("**DONE:**") or "**NOT DONE:**" not in first or "**NEXT:**" not in first:
        bad.append("the paragraph after the title is not the DONE / NOT DONE / NEXT line")
    return bad


# ---- the pages ----

def _hunks(diff):
    """[(old lines, new lines)] of a unified diff of one file (context and removed lines; context and added lines)."""
    out, cur = [], None
    for ln in diff.split("\n"):
        if ln.startswith("@@"):
            cur = ([], [])
            out.append(cur)
        elif cur is not None and ln[:1] in (" ", "-", "+"):
            if ln[:1] in (" ", "-"):
                cur[0].append(ln[1:])
            if ln[:1] in (" ", "+"):
                cur[1].append(ln[1:])
    return out


def _find(ls, block):
    return [i for i in range(len(ls) - len(block) + 1) if ls[i:i + len(block)] == block]


def _apply_hunks(text, hunks, where):
    """The page with each hunk applied where its old lines stand exactly once; a hunk whose new lines already stand once (an earlier
    pin made the same change) is not applied again; anything else is a failure naming the page and the pin."""
    ls = text.split("\n")
    for old, new in hunks:
        at = _find(ls, old)
        if len(at) == 1:
            ls[at[0]:at[0] + len(old)] = new
        elif len(_find(ls, new)) != 1:
            raise AssertionError("%s: a hunk does not apply (its old lines stand %d times)" % (where, len(at)))
    return "\n".join(ls)


def _integrated():
    """Main's four pages at AT with each pin's own change to them and step a5, in memory (read-only: git show, git diff, merge-base)."""
    for c in (AT,) + PINS:
        if not _has(c):
            raise Skip("the tree's pages are not set 31's adoption and %s is not in this repository" % c[:8])
    out = {}
    for k, p in PAGES.items():
        t = _show(AT, p)
        for pin in PINS:
            mb = _git("merge-base", AT, pin).strip()
            t = _apply_hunks(t, _hunks(_git("diff", "-U3", mb, pin, "--", p)), "%s at %s" % (p, pin[:8]))
        out[k] = t
    ns = {"__name__": "a5_in_memory"}
    exec(compile(_show(A5[0], A5[1]), A5[1], "exec"), ns)
    out["U"] = ns["apply"](out["U"])
    return out


def _stage_pages():
    """("A", pages) on the tree's own pages at set 31 (the integrated tree); ("S", pages) once the rows are applied; ("P", pages):
    this branch before the integration, main's pages at AT with the pins and step a5 in memory (no fill: W99's C4)."""
    head = _read(PAGES["S"]).split("\n")[2]
    if head.startswith("**Current revision: set 31 "):
        return "A", {k: _read(p) for k, p in PAGES.items()}
    if head.startswith("**Current revision: set 32"):
        return "S", {k: _read(p) for k, p in PAGES.items()}
    if "P" not in _C:
        _C["P"] = _integrated()
    return "P", dict(_C["P"])


def p_pages(rows, pages):
    """Every old text exactly once on its line; the rows of a page applied bottom-up (rows on one line in the given order)."""
    bad = []
    work = {k: v.split("\n") for k, v in pages.items()}
    order = sorted(range(len(rows)), key=lambda i: (rows[i][1], -rows[i][5], i))
    for i in order:
        rid, pre, _n, _page, after, line, old, new, _b = rows[i]
        ls = work[pre]
        if line < 1 or line > len(ls):
            bad.append("%s: line %d is outside the page (%d lines)" % (rid, line, len(ls)))
            continue
        if ls[line - 1].count(old) != 1:
            bad.append("%s: the old text is %d times on line %d, not once: %r" % (rid, ls[line - 1].count(old), line, old[:60]))
            continue
        ls[line - 1] = ls[line - 1].replace(old, new, 1)
    for k, p in pages.items():     # untouched pages read the same; every token left is one the stage leaves
        for t in _tokens(p):
            if t not in ("ADOPTION", "GATE"):
                bad.append("%s's page carries %s on the revision read" % (k, T(t)))
    return bad


def _loose(new):
    """The new text as a pattern: each token stands for itself or a value the fill wrote (a commit, or a GATE's text)."""
    parts = re.split(r"(__(?:CANDIDATE|ADOPTION|GATE)__)", new)
    pat = ""
    for x in parts:
        if x == T("GATE"):
            pat += r"(?:%s|[^`\n]+?)" % re.escape(x)
        elif x in (T("CANDIDATE"), T("ADOPTION")):
            pat += r"(?:%s|[0-9a-f]{8,40})" % re.escape(x)
        else:
            pat += re.escape(x)
    return pat


def p_applied(rows, pages):
    """Stage S: every row's new text stands on its page (rows S-07 and S-08 and U-05 and U-06 each their own part)."""
    bad = []
    for rid, pre, *_r in rows:
        new = _r[-2]
        if not re.search(_loose(new), pages[pre]):
            bad.append("%s: its new text is not on %s" % (rid, PAGES[pre]))
    return bad


def p_placed_applied(pages):
    """Stage S: on the applied pages, set 32's head paragraph follows set 31's, each of the five layers' first block is set 32's, and the
    plan's last entry is set 32's milestone."""
    bad = []
    ls = pages["L"].split("\n")
    h31 = [i for i, x in enumerate(ls) if x.startswith("**After set 31 (6 October 2026, an adoption")]
    h32 = [i for i, x in enumerate(ls) if x.startswith("**After set 32 (an adoption")]
    if len(h31) != 1 or len(h32) != 1 or next((x for x in ls[h31[0] + 1:] if x.strip()), None) != ls[h32[0]]:
        bad.append("set 32's head paragraph does not follow set 31's")
    for lay in LAYERS:
        i = [k for k, x in enumerate(ls) if x.startswith(lay)]
        nxt = next((x for x in ls[i[0] + 1:] if x.strip()), "") if len(i) == 1 else ""
        if not nxt.startswith("**After set 32: IN_PROGRESS"):
            bad.append("%s: its first block is not set 32's" % lay.strip())
    heads = [x for x in pages["P"].split("\n") if x.startswith("### ")]
    if not heads or not heads[-1].startswith("### Milestone: integration set 32 promoted"):
        bad.append("the plan's last entry is not set 32's milestone")
    return bad


def p_placement(rows, pages):
    """The set 32 head paragraph after set 31's; each layer block directly under its heading above the set 31 block; the plan's entry
    after set 31's milestone, at the page's end."""
    bad = []
    by = {r[0]: r for r in rows}
    lines = {k: v.split("\n") for k, v in pages.items()}
    l1 = by.get("L-01")
    if not l1 or not lines["L"][l1[5] - 1].startswith("**After set 31 (") or not l1[7].split("\n", 2)[-1].startswith("**After set 32 ("):
        bad.append("L-01 is not set 32's head paragraph placed after set 31's")
    heads = [r for r in rows if r[1] == "L" and r[0] != "L-01"]
    if sorted(h[6].split(". ")[0] + ". " for h in heads) != sorted(LAYERS):
        bad.append("the layer rows are %s, not Layers 4, 5, 8, 9 and 12" % [h[6] for h in heads])
    for h in heads:
        ls, i = lines["L"], h[5]
        nxt = next((x for x in ls[i:] if x.strip()), "")
        if not ls[i - 1].startswith("## Layer ") or not nxt.startswith("**After set 31 ("):
            bad.append("%s: line %d is not a layer heading followed by its set 31 block" % (h[0], i))
        if not h[7].startswith(h[6] + "\n\n**After set 32: IN_PROGRESS"):
            bad.append("%s: the set 32 block is not directly under the heading" % h[0])
    p1 = by.get("P-01")
    if p1:
        ls = lines["P"]
        prev = [x for x in ls[:p1[5]] if x.startswith("### ")]
        if not prev or not prev[-1].startswith("### Milestone, 6 October 2026: integration set 31 promoted") \
                or any(x.strip() for x in ls[p1[5]:]):
            bad.append("P-01 is not after set 31's milestone at the plan's end")
        if "\n### Milestone: integration set 32 promoted" not in p1[7]:
            bad.append("P-01 is not set 32's milestone")
    return bad


# ---- what the new texts quote and count ----

def p_citations(rows):
    bad = []
    for rid, *_r in rows:
        for sha, path, n, q in GIT_ANCHOR.findall(_r[-2]):
            if not _has(sha):
                raise Skip("%s cites %s, which is not in this repository" % (rid, sha))
            ls = _show(sha, path).split("\n")
            n = int(n)
            if n > len(ls) or " ".join(q.replace("\\`", "`").split()) not in " ".join(ls[n - 1].split()):
                bad.append("%s: %r is not on %s:%s:%d" % (rid, q[:50], sha[:8], path, n))
    return bad


def _section(text, sec):
    ls = text.split("\n")
    lvl = "##" if sec.isdigit() else "###"
    start = next((i for i, x in enumerate(ls) if x.startswith("%s %s. " % (lvl, sec))), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(ls)) if ls[i].startswith("## ") or (lvl == "###" and ls[i].startswith("### "))), len(ls))
    return " ".join(" ".join(ls[start:end]).split())


def _file(path):
    """A quoted file: the tree's, else (int31's records before set 31's adoption is merged) fnd/adopt31's at AT."""
    path = ("v2/docs/" + path) if path.startswith("records/") else path
    if os.path.isfile(os.path.join(REPO, path)):
        return _read(path)
    if _has(AT):
        return _show(AT, path)
    raise Skip("%s is not in the tree and %s is absent" % (path, AT[:8]))


def p_quotes(rows):
    """A quote with its file and section ("..." (`path`, section N), or (`path`, section N: "...")) is in that section of that file."""
    bad = []
    for rid, *_r in rows:
        new = " ".join(_r[-2].split())
        found = [(q, p, s) for qs, p, s in QUOTE_SEC[0].findall(new) for q in re.findall(r"\"([^\"]+)\"", qs)]
        found += [(q, p, s) for p, s, q in QUOTE_SEC[1].findall(new)]
        for q, p, s in found:
            sec = _section(_file(p), s)
            if sec is None or " ".join(q.split()) not in sec:
                bad.append("%s: %r is not in %s, section %s" % (rid, q[:50], p, s))
    return bad


CELL_SPLIT = re.compile(r"(?<!\\)\|")


def _class_counts():
    """The branch rows' counts from the tree's classification (the adopted one at the adoption; W99's C1, not a fixed revision): the
    classified rows numbered below 31 (rows 31 to 33 and their sub-rows are the integration's), their total, how many touch a file
    cx46 read (their reason names "UNREVIEWED since cx46", as test_res32 reads it) and how many are REVIEWED-INPUT CHANGED first."""
    sec = _read(CLASS).split("## 1. ", 1)[1].split("\n## 2. ", 1)[0]
    tot = touch = ric = 0
    for line in sec.split("\n"):
        if not line.startswith("| ") or line.startswith("| # ") or line.startswith("|---"):
            continue
        c = [x.strip() for x in CELL_SPLIT.split(line.strip())[1:-1]]
        if not re.match(r"\d+(\.\d+)?$", c[0]) or float(c[0].split(".")[0]) >= 31 or not re.match(r"`[0-9a-f]{8}` / `[0-9a-f]{40}`$", c[1]):
            continue
        tot += 1
        touch += "UNREVIEWED since cx46" in c[7]
        ric += c[6].split(" + ")[0].strip() == "REVIEWED-INPUT CHANGED"
    return tot, ric, touch


def _flat(s):
    return " ".join(s.split())


TYPED = (re.compile(r"of the (\d+) commits of its five branches, (\d+) touch a file cx46 read, (\d+) of them REVIEWED-INPUT CHANGED"),
         re.compile(r"counts (\d+) REVIEWED-INPUT CHANGED commits among the (\d+) of its five branches and (\d+) that touch a file cx46 read"),
         re.compile(r"classes the (\d+) commits of its five branches, `[^`]+` `(\d+) of the \d+ touch a file cx46 read`, (\d+) of them REVIEWED-INPUT CHANGED"))
BESIDE = re.compile(r"set 31's (\d+),? (?:counted )?over all (\d+) of its commits")
BESIDE30 = re.compile(r"set 30's (\d+) over its (\d+)")
SCOPE = "counted over the branch commits alone"


def p_counts(text, pages):
    """The counts the rows type, whitespace flattened (W99's C5): the tree's classification's over the branch rows (34 rows, 2
    REVIEWED-INPUT CHANGED, 12 touching at this record), each of the four sentences stating that scope (C1); set 31's 25 over its 106
    commits and set 30's 14 over its 45 as the pages read them, every occurrence (S-10, U-09, L-02, P-01 for set 31; L-02, P-01 for
    set 30)."""
    tot, ric, touch = _class_counts()
    flat, bad, n = _flat(text), [], 0
    for i, order in ((0, (tot, touch, ric)), (1, (ric, tot, touch)), (2, (tot, touch, ric))):
        for m in TYPED[i].finditer(flat):
            n += 1
            if tuple(int(x) for x in m.groups()) != order:
                bad.append("typed %s, the classification's %s" % (m.groups(), order))
    if n != 4:
        bad.append("the classification's counts are typed %d times, not 4 (S-10, U-09, L-02, P-01)" % n)
    if flat.count(SCOPE) != 4:
        bad.append("the branch-only scope is stated %d times, not 4 (W99's C1)" % flat.count(SCOPE))
    s = _flat(pages["S"])
    m31 = re.search(r"Set 31 adds its own: (\d+) commits that change what cx46 read .*? over the (\d+) commits of `dd1aed00\.\.5f25daf3`", s)
    m30 = re.search(r"\((\d+) over the (\d+) commits of `4d0ff8a2\.\.dd1aed00`", s)
    if not m31 or not m30:
        return bad + ["the pages do not state set 31's and set 30's counts as these rows read them"]
    b31, b30 = BESIDE.findall(flat), BESIDE30.findall(flat)
    if len(b31) != 4 or any(x != m31.groups() for x in b31):
        bad.append("set 31's count over its commits is typed %s, not %s four times" % (b31, m31.groups()))
    if len(b30) != 2 or any(x != m30.groups() for x in b30):
        bad.append("set 30's count over its commits is typed %s, not %s twice" % (b30, m30.groups()))
    return bad


def p_figures(text):
    """The figures the rows type are the record's (W99's N2: E19 to E21): the converted generators, the numbers the KEY holds, the
    ZIP's cap and the held-back texts, each at every occurrence."""
    flat, res, bad = _flat(text), _flat(_read(RESULT)), []
    want = {"generators": re.search(r"committed verbatim inputs of (\d+) record generators", res),
            "numbers": re.search(r"KEY holding the (\w+) numbers the record reads", res),
            "MiB": re.search(r"raised to (\d+) MiB", res),
            "held": re.search(r"\(352 files\), (\d+) held back", res)}
    if not all(want.values()):
        return ["RESULT.md does not state %s" % [k for k, v in want.items() if not v]]
    for k, pat, least in (("generators", r"(\d+) record generators", 5), ("numbers", r"the (\w+) numbers (?:the record|it) reads", 4),
                          ("MiB", r"(\d+) MiB", 2), ("held", r"re-taken after the fetch(?:, as section 7 gives it)?: (\d+) texts", 4)):
        got = re.findall(pat, flat)
        if len(got) < least or any(g != want[k].group(1) for g in got):
            bad.append("%s typed %s, not the record's %s at least %d times" % (k, got, want[k].group(1), least))
    return bad


CLAIMS = {
    "P-01": ("engineering-handover readiness READY AS A DESK PACKAGE OF OPEN ITEMS; power-design closure BLOCKED; fabrication release "
             "BLOCKED. Layer 4's DESK gate NOT PASSED.", "\"Set 32 closes NO power item.\""),
    "U-16": ("No circuit change is applied, and nothing in it accepts, closes or promotes a design claim; Layer 4's DESK gate and the "
             "three completion claims stand as set 30's assessment gives them.",),
    "L-01": ("No item is raised to MET by set 32 and no layer from 4 on is COMPLETE",),
    "S-09": ("unchanged in set 31 and in set 32: no independent check of the engineering read a later revision",),
    "U-07": ("unchanged in set 31 and in set 32: no independent check of the engineering read a later revision",),
    "S-10": ("each \"UNREVIEWED since cx46\"",), "U-09": ("each \"UNREVIEWED since cx46\"",),
    "S-05": ("\"Layer 4's DESK gate: NOT PASSED\"", "\"Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS\"",
             "\"Power-design closure: BLOCKED. Fabrication release: BLOCKED.\"", "\"Set 32 closes NO power item.\""),
    "U-03": ("\"Layer 4's DESK gate: NOT PASSED\"", "\"Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN ITEMS\"",
             "\"Power-design closure: BLOCKED. Fabrication release: BLOCKED.\"", "\"Set 32 closes NO power item.\""),
}


def p_claims(rows):
    """Each claim a row carries stands in its new text exactly once, in full (W99's N2: E1 to E5, E7, E14, E28)."""
    by, bad = {r[0]: _flat(r[7]) for r in rows}, []
    for rid, claims in CLAIMS.items():
        for c in claims:
            if by.get(rid, "").count(c) != 1:
                bad.append("%s does not carry, once and in full: %r" % (rid, c[:70]))
    return bad


# W119 (W116's finding 1, W110's C2), restated at set 32's adoption by `<worktrees>/_runs/int32/freeze/apply_known32.py` because
# paragraph 0a of l4e7_p0sol.out at the candidate no longer names set 30's integrator and prints WP-B's clause (para_0a's source):
# the rows say the known item is corrected and KNOWN takes that wording only; KNOWN_PLANNED, W113's pattern, is refused by p_known;
# RESTATED is the change in the rows, on the pages and in p_fill's template alike; its last three blocks (W123, W121's finding 3)
# are the patch file's own prose (NEXT step (6), the paragraph "Filling the GATE tokens", S-05's basis), on no page.
KNOWN = re.compile(r"is corrected by (?:that|set 32's one|set 32's) re-key and (?:the regeneration of its dependents|its dependents' "
                   r"regeneration) \(paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption(?:, "
                   r"after these rows were written)?\); the regenerated `(?:v2/docs/)?records/l4e7/l4e7_p0sol\.out` at the candidate "
                   r"prints in its paragraph 0a: `([^`]+)`")
KNOWN_PLANNED = re.compile(r"is planned to be corrected by (?:that|set 32's one|set 32's) re-key and (?:the regeneration of its "
                           r"dependents|its dependents' regeneration)(?: \(no set had run it when these rows were written\))?; the "
                           r"regenerated `(?:v2/docs/)?records/l4e7/l4e7_p0sol\.out` at the candidate prints in its paragraph 0a: "
                           r"`([^`]+)`")
W119_READ = "paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption"
RESTATED = (   # W119: (the rows' planned text, the corrected text), the same blocks in the patch file and on the pages;
               # W123: the last three, the patch file's own prose only
    ("planned to be corrected by set 32's one re-key and the regeneration of its dependents (no set had run it when these rows were",
     "corrected by set 32's one re-key and the regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were"),
    ("\n".join(("31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section 4a), is planned to be corrected",
                 "by set 32's one re-key and the regeneration of its dependents (no set had run it when these rows were written); the regenerated")),
     "\n".join(("31's known item, record l4e7's paragraph 0a's history sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's one",
                 "re-key and the regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were written); the regenerated"))),
    ("\n".join(('  history sentence (the set 31 block below; `v2/docs/records/int31/RESULT.md`, section 4a), is planned to be corrected by that',
                 '  re-key and the regeneration of its dependents (no set had run it when these rows were written); the regenerated')),
     "\n".join(('  history sentence (the set 31 block below; `v2/docs/records/int31/RESULT.md`, section 4a), is corrected by that re-key and the',
                 "  regeneration of its dependents (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption, after these rows were written); the regenerated"))),
    ("sentence (`records/int31/RESULT.md`, section 4a), is planned to be corrected by set 32's re-key and its dependents' regeneration;",
     "sentence (`records/int31/RESULT.md`, section 4a), is corrected by set 32's re-key and its dependents' regeneration (paragraph 0a at the candidate no longer names set 30's integrator: read at the adoption);"),
    ("\n".join(('and, if paragraph 0a at the candidate no longer',
                 'names set 30\'s integrator, rows S-05, U-03, L-02 and P-01\'s "is planned to be corrected" restated with `test_patch32.py`\'s pattern',
                 "KNOWN (W110's C2: no basis for it exists before the regenerated output, so W113 left the words; the GATE value is a clause of the",
                 "regenerated paragraph 0a that set 31's paragraph 0a does not print, which `test_patch32.py` now requires); (7) the")),
     "\n".join(('and, since paragraph 0a at the candidate no longer',
                 'names set 30\'s integrator, rows S-05, U-03, L-02 and P-01\'s "is planned to be corrected" restated at the adoption as "is corrected",',
                 "with `test_patch32.py`'s pattern KNOWN, by `<worktrees>/_runs/int32/freeze/apply_known32.py` (W119, W123; W110's C2: the GATE",
                 "value is a clause of the regenerated paragraph 0a that set 31's paragraph 0a does not print, which `test_patch32.py` requires); (7) the"))),
    ("\n".join(('The rows never say the known item is corrected: they say a correction',
                 'is planned and quote what 0a prints, and `test_patch32` refuses the words "is corrected" there while paragraph 0a at the candidate',
                 'still names set 30\'s integrator; `records/int32/CLASSIFICATION.md`\'s row 33 keeps "planned to correct that item (no set has run it',
                 'yet)" until the adoption reads that paragraph.')),
     "\n".join(('The rows say the known item is corrected: the adoption read paragraph',
                 '0a at the candidate, which no longer names set 30\'s integrator, and `apply_known32.py` (W119, W123) restated "is planned to be',
                 'corrected"; `test_patch32` refuses "is corrected" there while paragraph 0a at the candidate names set 30\'s integrator, and the planned',
                 'wording once the adoption read it; `records/int32/CLASSIFICATION.md`\'s row 33 reads "no longer names set 30\'s integrator".'))),
    ('row 33 ("planned to correct that item (no set has run it yet)"); the GATE\'s source, the',
     'row 33 ("no longer names set 30\'s integrator"); the GATE\'s source, the'),
)


def _para_0a(cand):
    t = _show(cand, P0SOL)
    m = re.search(r"\n  0a (.*?)\n  0b ", t, re.S)
    return _flat(m.group(1)) if m else None


def p_known(rows, result):
    """Set 31's known item in S-05, U-03, L-02 and P-01: its GATE's source is paragraph 0a of l4e7_p0sol.out at the candidate, never the
    dependents' log; after the fill the value stands in that paragraph; "is corrected" only where that paragraph no longer names set
    30's integrator (W99's C2)."""
    by, bad = {r[0]: _flat(r[7]) for r in rows}, []
    st, cand, _a = _fill_stage(result)
    para = old = None
    if st in (1, 2):
        if not _has(cand):
            raise Skip("the candidate %s is not in this repository" % cand[:8])
        para = _para_0a(cand)
        if para is None:
            return ["%s at the candidate prints no paragraph 0a" % P0SOL]
        if not _has(S31_CAND):
            raise Skip("set 31's candidate %s is not in this repository" % S31_CAND[:8])
        old = _para_0a(S31_CAND)
    for rid in KNOWN_ROWS:
        txt = by.get(rid, "")
        if KNOWN_PLANNED.search(txt):     # W119: the planned wording once the adoption read the correction
            bad.append("%s: says the correction is planned, while the adoption read it in paragraph 0a at the candidate" % rid)
        ms = KNOWN.findall(txt)
        if len(ms) != 1:
            bad.append("%s: the known item is not stated once with paragraph 0a at the candidate as its source" % rid)
            continue
        if "dependents' log" in txt:
            bad.append("%s: the known item's source is the dependents' log" % rid)
        if st == 0 and ms[0] != T("GATE"):
            bad.append("%s: the known item's value is written before the fill" % rid)
        if para is not None and _flat(ms[0].strip('"')) not in para:
            bad.append("%s: the known item's value is not in paragraph 0a at the candidate: %r" % (rid, ms[0][:60]))
        if old is not None and _flat(ms[0].strip('"')) in old:     # W113 (W110's C2): a fragment set 31's 0a also prints shows nothing
            bad.append("%s: the known item's value also stands in set 31's paragraph 0a at %s, so it shows no change: %r"
                       % (rid, S31_CAND[:8], ms[0][:60]))
        if re.search(r"\bis corrected\b", txt) and (para is None or "set 30's integrator" in para):
            bad.append("%s: says the known item is corrected, which paragraph 0a at the candidate does not show" % rid)
    return bad


# ---- the fill ----

def _role(result, words):
    ls = [x for x in result.split("\n") if x.startswith(words)]
    if len(ls) != 1:
        return None
    m = re.match(r"`([^`]+)`$", re.split(r"(?<!\\)\|", ls[0].strip())[2].strip())
    return m.group(1) if m else None


def _fill_stage(result):
    cand = _role(result, "| INTEGRATED = CANDIDATE: the candidate commit |")
    adopt = _role(result, "| ADOPTED: the commit that adopts this record |")
    if cand is None or adopt is None:
        return None, cand, adopt
    st = {(True, True): 0, (False, True): 1, (False, False): 2}.get((cand.startswith("__"), adopt.startswith("__")))
    return st, cand, adopt


def _template():
    """The patch file at the newest commit touching it that still holds the CANDIDATE token (the template the fill filled)."""
    if "tmpl" not in _C:
        _C["tmpl"] = None
        for c in _git("log", "--format=%H", "--", PATCH).split():
            t = _show(c, PATCH)
            if "`%s`" % T("CANDIDATE") in t:
                _C["tmpl"] = t
                break
    return _C["tmpl"]


def p_fill(text, result):
    """Stage 0: the three tokens present and no other; stage 1: the ADOPTION token alone; stage 2: none; after the fill, each line is
    the template's with CANDIDATE the role's commit, ADOPTION the role's commit (stage 2) and GATE some text."""
    st, cand, adopt = _fill_stage(result)
    if st is None:
        return ["RESULT's section 1 role rows are neither all tokens, nor all but ADOPTION filled, nor all filled"]
    bad = []
    left = sorted(set(_tokens(text)))
    want = {0: list(ALLOWED), 1: ["ADOPTION"], 2: []}[st]
    if left != sorted(want):
        bad.append("fill stage %d leaves %s in the patch file, not %s" % (st, left, sorted(want)))
    if st == 0:
        return bad
    gl = [x for x in text.split("\n") if x.startswith(GUARD_LINE)]     # W113 (W106's N-c, W110's suggestion): the three hosts' lines
    parts = gl[0][len(GUARD_LINE):].rsplit("`.", 1)[0].split("; ") if len(gl) == 1 else []
    shas = [GUARD_PART.match(x) for x in parts]
    if len(parts) != GUARD_HOSTS or not all(shas) or any(not (m.group(1).startswith(cand) or cand.startswith(m.group(1))) for m in shas):
        bad.append("the candidate_guard value is not %d parts joined by '; ', each 'candidate_guard: PASS candidate <the candidate>': %r"
                   % (GUARD_HOSTS, (gl or [""])[0][len(GUARD_LINE):][:80]))
    tmpl = _template()
    if tmpl is None:
        return bad + ["after the fill, no committed revision of the patch file holds the template"]
    for old_, new_ in RESTATED:     # W119: the template read through the known item's restatement (apply_known32.py), its only change
        if tmpl.count(old_) != 1:
            return bad + ["the template does not hold the known item's planned text once (W119's RESTATED): %r" % old_[:60]]
        tmpl = tmpl.replace(old_, new_, 1)
    a, b = tmpl.split("\n"), text.split("\n")
    if len(a) != len(b):
        return bad + ["the filled patch file has %d lines, its template %d" % (len(b), len(a))]
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x == y:
            continue
        pat = ""
        for part in re.split(r"(__(?:CANDIDATE|ADOPTION|GATE)__)", x):
            if part == T("CANDIDATE"):
                pat += re.escape(cand)
            elif part == T("ADOPTION"):
                pat += re.escape(adopt if st == 2 else part)
            elif part == T("GATE"):
                pat += r".+?"
            else:
                pat += re.escape(part)
        if not re.fullmatch(pat, y):
            bad.append("line %d is not its template line with the stage's values: %r" % (i, y[:80]))
    return bad


def p_named(result, klass):
    """The record names the patch file the way the fill tool finds it (`int32/<name>.patch.md` in RESULT or CLASSIFICATION)."""
    names = set(re.findall(r"int32/([A-Za-z0-9_.-]+\.patch\.md)", result + "\n" + klass))
    return [] if "ENTRY-PAGES.patch.md" in names else ["neither RESULT.md nor CLASSIFICATION.md names int32/ENTRY-PAGES.patch.md"]


# ---- tests ----

def _mut(text, old, new):
    assert old in text, "the mutation's anchor %r is not in the text" % old[:50]
    return text.replace(old, new, 1)


def _pt():
    return _read(PATCH)


def t_the_patch_file_carries_no_dash_and_opens_with_its_state_line():
    t = _pt()
    assert not p_hygiene(t), p_hygiene(t)
    assert p_hygiene(_mut(t, "Record text only:", "Record text only \u2014")), "an em dash passed"
    assert p_hygiene(_mut(t, "**NOT DONE:**", "**NOT YET:**")), "a state line without NOT DONE passed"


def t_every_row_is_well_formed_with_its_tokens_and_basis():
    t = _pt()
    assert not p_rows(t), p_rows(t)
    s07 = [r for r in _rows(t) if r[0] == "S-07"][0]
    assert p_rows(_mut(t, "### S-03. ", "### S-04. ")), "a row id out of sequence passed"
    assert p_rows(_mut(t, "### U-02. `v2/docs/handover/supplier/SUPPLIER-HANDOVER.md`", "### U-02. `v2/docs/handover/START-HERE.md`")), \
        "a row naming another prefix's page passed"
    assert p_rows(_mut(t, "set 32's paragraph in the edition history\n\nOld text:\n```text\n(`v2",
                       "set 32's paragraph in the edition history\n\nOld text:\n```text\n(`%s` `v2" % T("GATE"))), "an old text with a token passed"
    assert p_rows(_mut(t, s07[7], s07[7].replace("set 32's adoption commit,", "set 32's adoption commit `%s`," % T("PROMOTED"), 1))), \
        "a PROMOTED token passed"
    assert p_rows(_mut(t, "netlist changed.\n\n**Set 32** (the revision", "netlist changed!\n\n**Set 32** (the revision")), \
        "an after-line row not beginning with its old text passed"
    assert p_rows(_mut(t, "Basis: the Tested row (S-06).", "Basis: `v2/docs/records/int32/NOWHERE.md`.")), "a basis naming no file passed"
    # W113 (W106's N-c, W110's M3): P-01's candidate_guard line wrapped back, so its value moves off the line the fill tool's
    # suggestion matches; and the line's words changed
    gl = [x for x in t.split("\n") if x.startswith(GUARD_LINE)]
    assert len(gl) == 1, "the patch file holds %d candidate_guard lines" % len(gl)
    assert p_rows(_mut(t, gl[0], gl[0].replace("in one value: `", "in one\nvalue: `", 1))), "P-01's guard line wrapped passed (N-c)"
    assert p_rows(_mut(t, gl[0], gl[0].replace("every host, its PASS line", "each host, its PASS line", 1))), \
        "P-01's guard line in other words passed"


def t_every_old_text_holds_once_on_its_line_of_the_pages_read():
    """The revision read: the integrated tree's own pages (set 31's adoption in the tree), else main's AT with the pins and step a5 in
    memory (W99's B1 and C4); or, once the rows are applied, every new text on its page."""
    t = _pt()
    rows = _rows(t)
    stage, pages = _stage_pages()
    if stage == "S":
        assert not p_applied(rows, pages), p_applied(rows, pages)
        assert p_applied(rows, dict(pages, U=pages["U"].replace("### 0e. How to reproduce set 32's figures", "### 0e. How to reproduce", 1))), \
            "a row's new text missing from its page passed"
        return
    assert not p_pages(rows, pages), p_pages(rows, pages)
    assert p_pages([x if x[0] != "S-06" else x[:6] + (x[6].replace("set 31's", "set 30's", 1),) + x[7:] for x in rows], pages), \
        "an old text not on its line passed"
    assert p_pages([x if x[0] != "U-13" else x[:5] + (x[5] + 1,) + x[6:] for x in rows], pages), "a row on the wrong line passed"
    assert p_pages([x if x[0] != "S-08" else x[:5] + (x[5], "` | set 31's adoption commit") + x[7:] for x in rows] +
                   [x for x in rows if x[0] == "S-08"], pages), "a second row whose old text the first consumed passed"
    assert p_pages([x if x[0] != "U-16" else x[:5] + (407,) + x[6:] for x in rows], pages), "U-16 on main's line 407 passed (W99's B1)"
    if stage == "P":
        assert p_pages(rows, dict(pages, U=_show(AT, PAGES["U"]))), "main's supplier page without the pinned branches' lines passed"


def t_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last():
    t = _pt()
    rows = _rows(t)
    stage, pages = _stage_pages()
    if stage == "S":
        assert not p_placed_applied(pages), p_placed_applied(pages)
        assert p_placed_applied(dict(pages, L=pages["L"].replace("\n\n**After set 32: IN_PROGRESS.** Set 32 carries Q-55", "\n\nmoved\n\n"
                                                                     "**After set 32: IN_PROGRESS.** Set 32 carries Q-55", 1))), "a block not first passed"
        return
    assert not p_placement(rows, pages), p_placement(rows, pages)
    assert p_placement(_rows(_mut(t, "\n\n**After set 32: IN_PROGRESS.** Set 32 carries Q-55",
                                  "\n\n**After set 31 (6 October 2026): IN_PROGRESS.** Set 32 carries Q-55")), pages), \
        "a set 32 block not headed After set 32 passed"
    assert p_placement(_rows(_mut(t, "after line 352: Layer 4's", "after line 354: Layer 4's").replace(
        "line 352", "line 354", 1)), pages), "a block placed under the set 31 block passed"


def t_every_citation_is_on_its_cited_line():
    t = _pt()
    rows = _rows(t)
    assert not p_citations(rows), p_citations(rows)
    assert p_citations(_rows(_mut(t, "`34 commits of the five branches over their bases`", "`35 commits of the five branches over their bases`"))), \
        "a changed quote passed"
    assert p_citations(_rows(_mut(t, "RESULT.md:385` `**Set 32 closes NO power item.**`", "RESULT.md:386` `**Set 32 closes NO power item.**`"))), \
        "a quote on the wrong line passed"


def t_every_quote_with_its_section_is_in_that_section():
    t = _pt()
    rows = _rows(t)
    assert not p_quotes(rows), p_quotes(rows)
    assert p_quotes(_rows(_mut(t, "\"Set 32 closes NO power item.\" (`v2/docs/records/int32/RESULT.md`,",
                               "\"Set 32 closes no power item.\" (`v2/docs/records/int32/RESULT.md`,"))), "a changed quote passed"
    assert p_quotes(_rows(_mut(t, "\"Layer 4's DESK gate: NOT PASSED\"; \"Engineering-handover\nreadiness",
                               "\"Layer 4's DESK gate: PASSED\"; \"Engineering-handover\nreadiness"))), "a changed claim passed"
    assert p_quotes(_rows(_mut(t, "section 1: \"no independent check of its engineering\") |",
                               "section 2: \"no independent check of its engineering\") |"))), "a quote in the wrong section passed"


def t_every_count_typed_is_the_classifications_and_the_pages():
    t = _pt()
    _stage, pages = _stage_pages()
    assert not p_counts(t, pages), p_counts(t, pages)
    assert p_counts(_mut(t, "of the 34 commits of its five branches, 12", "of the 35 commits of its five branches, 12"), pages), \
        "a wrong total passed"
    assert p_counts(_mut(t, "counts 2 REVIEWED-INPUT CHANGED commits", "counts 3 REVIEWED-INPUT CHANGED commits"), pages), "a wrong RIC count passed"
    assert p_counts(_mut(t, "of the 34 commits of its five branches, 12", "of the 34 commits of its branches, 12"), pages), \
        "a count dropped from the pattern passed"
    assert p_counts(_mut(t, "beside set 31's 25\n  over all 106", "beside set 31's 24\n  over all 106"), pages), "set 31's 25 typed 24 passed (E18)"
    assert p_counts(_mut(t, "beside set 31's 25 over all 106\nof its commits", "beside set 31's 26 over all 106\nof its commits"), pages), \
        "the wrapped occurrence typed 26 passed (W99's C5)"
    assert p_counts(_mut(t, "and set 30's 14 over its 45.", "and set 30's 15 over its 45."), pages), "set 30's 14 typed 15 passed"
    assert p_counts(_mut(t, "section 2), counted over the branch commits alone; the integration's own commits are that file's rows 31 to 33",
                         "section 2); the integration's own commits are that file's rows 31 to 33"), pages), "a count without its scope passed (C1)"


def t_every_figure_and_claim_the_rows_carry_is_the_records():
    """W99's N2: the typed figures (E19 to E21 and the held-back texts) and the claims in full (E1 to E5, E7, E14, E28)."""
    t = _pt()
    assert not p_figures(t), p_figures(t)
    for old, new, what in (("over set 31: 26 record generators read their\nmakers'", "over set 31: 27 record generators read their\nmakers'", "E19"),
                           ("keyed on the sixteen numbers the record reads of `l4e11_power.out` (WP-B), with ONE",
                            "keyed on the seventeen numbers the record reads of `l4e11_power.out` (WP-B), with ONE", "E20"),
                           ("ZIP's cap is raised to 100 MiB (Q-53)", "ZIP's cap is raised to 50 MiB (Q-53)", "E21"),
                           ("sheet and re-taken after the fetch: 57 texts), the verdict", "sheet and re-taken after the fetch: 52 texts), the verdict", "held")):
        assert p_figures(_mut(t, old, new)), "%s passed" % what
    rows = _rows(t)
    assert not p_claims(rows), p_claims(rows)
    for old, new, what in (("Layer 4's DESK gate NOT PASSED.\n", "Layer 4's DESK gate PASSED.\n", "E1"),
                           ("DESK PACKAGE OF OPEN ITEMS; power-design closure BLOCKED;", "DESK PACKAGE OF OPEN ITEMS; power-design closure CLOSED;", "E2"),
                           ("; unchanged in set 31 and in set 32: no independent check of the engineering read a later revision (`v2/docs/records/int31",
                            "; unchanged in set 31; in set 32 an independent check of the engineering read a later revision (`v2/docs/records/int31", "E3"),
                           ("No item is raised to MET by set 32", "Two items are raised to MET by set 32", "E4"),
                           ("(`v2/docs/records/int32/RESULT.md`). No circuit change is applied", "(`v2/docs/records/int32/RESULT.md`). A circuit change is applied", "E5"),
                           ("(reading A), each \"UNREVIEWED since cx46\" (`v2/docs/records/int32/CLASSIFICATION.md`",
                            "(reading A) (`v2/docs/records/int32/CLASSIFICATION.md`", "E7"),
                           ("; unchanged in set 31 and in set 32: no independent check of the engineering read a later revision (`records/int31",
                            "; unchanged in set 31, superseded in set 32 by W64's read (`records/int31", "E14"),
                           ("\"Engineering-handover readiness: READY AS A DESK PACKAGE OF OPEN\nITEMS\"", "\"Engineering-handover readiness: READY\"", "E28")):
        assert p_claims(_rows(_mut(t, old, new))), "%s passed" % what


def t_set_31s_known_item_reads_paragraph_0a_at_the_candidate():
    """W99's C2: the source is paragraph 0a of l4e7_p0sol.out at the candidate, never the dependents' log; the value (after the fill)
    stands in that paragraph; no row says the item is corrected while that paragraph still names set 30's integrator."""
    t = _pt()
    result = _read(RESULT)
    rows = _rows(t)
    assert not p_known(rows, result), p_known(rows, result)
    # W119: restated with the rows (apply_known32.py): the dependents' log as the source; the planned wording put back; the reading dropped
    assert p_known(_rows(_mut(t, "regeneration of its dependents (%s, after these rows were\nwritten); the regenerated" % W119_READ,
                                  "regeneration of its dependents, as the dependents' log shows; the regenerated")), result), \
        "the dependents' log as the source passed"
    assert p_known(_rows(_mut(t, "is corrected by that re-key and the\n  regeneration of its dependents (%s, after these rows were written)"
                                 % W119_READ, "is planned to be corrected by that re-key and the\n  regeneration of its dependents (no set had "
                                 "run it when these rows were written)")), result), "the planned wording put back passed"
    assert p_known(_rows(_mut(t, "regeneration (%s);" % W119_READ, "regeneration;")), result), "the correction without its reading passed"
    st = _fill_stage(result)[0]
    if st == 0:
        assert p_known(_rows(_mut(t, "candidate prints in its paragraph 0a: `%s`.\n```\nBasis: `v2/docs/records/int32/RESULT.md`, the paragraph" % T("GATE"),
                                  "candidate prints in its paragraph 0a: `a line`.\n```\nBasis: `v2/docs/records/int32/RESULT.md`, the paragraph")), result), \
            "a value written before the fill passed"
    else:
        m = re.search(r"records/l4e7/l4e7_p0sol\.out` at the candidate prints in its paragraph 0a: `([^`]+)`", t)
        assert p_known(_rows(t.replace("paragraph 0a: `%s`" % m.group(1), "paragraph 0a: `a sentence 0a never printed`", 1)), result), \
            "a value outside paragraph 0a passed"
        # W113 (W110's C2): a fragment that set 31's paragraph 0a prints too (WP-B's 0a and set 31's both begin so)
        assert p_known(_rows(t.replace("paragraph 0a: `%s`" % m.group(1), "paragraph 0a: `its KEY holds on this tree`", 1)), result), \
            "a fragment of set 31's paragraph 0a passed"
        # W123 (W121's finding 6): the rows say the item is corrected while paragraph 0a at the candidate still names set 30's
        # integrator: the candidate's output, as _show() caches it, read with set 31's paragraph 0a (S31_CAND) appended to its own
        k_ = (_fill_stage(result)[1], P0SOL)
        keep_ = _show(*k_)
        _C[k_] = keep_.replace("\n  0b ", "\n     %s\n  0b " % _para_0a(S31_CAND), 1)
        try:
            assert "set 30's integrator" in (_para_0a(k_[0]) or ""), "the mutant's paragraph 0a does not name set 30's integrator"
            bad_ = p_known(rows, result)
        finally:
            _C[k_] = keep_
        assert bad_ and all("says the known item is corrected" in b for b in bad_), \
            "the rows saying corrected while paragraph 0a at the candidate names set 30's integrator passed: %r" % bad_[:2]


def t_the_tokens_are_the_rows_and_the_fill_stage_is_resultss():
    t = _pt()
    result = _read(RESULT)
    assert not p_fill(t, result), p_fill(t, result)
    st = _fill_stage(result)[0]
    if st == 0:
        assert p_fill(t.replace(T("GATE"), "a log line"), result), "a GATE token removed before the fill passed"
        assert p_fill(_mut(t, "the gate lines |", "the gate lines `%s` |" % T("REKEY")), result), "a REKEY token passed"
    else:
        assert p_fill(_mut(t, "set 32, the revision `", "set 32, the revision `0"), result), "a wrong filled value passed"
        # W113 (W106's N-c): the guard value with one host's line only, and a host line naming another commit
        gl = [x for x in t.split("\n") if x.startswith(GUARD_LINE)][0]
        v = gl[len(GUARD_LINE):].rsplit("`.", 1)[0]
        assert p_fill(_mut(t, gl, gl.replace(v, v.split("; ")[0], 1)), result), "a one-part candidate_guard value passed"
        assert p_fill(_mut(t, gl, gl.replace("PASS candidate ", "PASS candidate 0", 1)), result), "a guard line naming another commit passed"


def t_the_record_names_the_patch_file_so_the_fill_reaches_it():
    result, klass = _read(RESULT), _read(CLASS)
    assert not p_named(result, klass), p_named(result, klass)
    # W154 (7 October 2026): the classification's rows 31.4.9 and 31.4.10 quote git's subjects of c0d0bb30 and 86da0523, which name
    # the patch file, and the fill reads the names in RESULT and CLASSIFICATION alike, so the mutant removes the name from both records
    assert p_named(result.replace("int32/ENTRY-PAGES.patch.md", "int32/ENTRY-PAGES.md"),
                   klass.replace("int32/ENTRY-PAGES.patch.md", "int32/ENTRY-PAGES.md")), "an unnamed patch file passed"


def _pytest(fn):
    def run():
        try:
            fn()
        except Skip as e:
            import pytest
            pytest.skip(str(e))
    run.__name__ = "test_" + fn.__name__[2:]
    run.__doc__ = fn.__doc__
    return run


test_the_patch_file_carries_no_dash_and_opens_with_its_state_line = _pytest(t_the_patch_file_carries_no_dash_and_opens_with_its_state_line)
test_every_row_is_well_formed_with_its_tokens_and_basis = _pytest(t_every_row_is_well_formed_with_its_tokens_and_basis)
test_every_old_text_holds_once_on_its_line_of_the_pages_read = _pytest(t_every_old_text_holds_once_on_its_line_of_the_pages_read)
test_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last = _pytest(
    t_the_set_32_blocks_are_placed_newest_first_and_the_plan_entry_last)
test_every_citation_is_on_its_cited_line = _pytest(t_every_citation_is_on_its_cited_line)
test_every_quote_with_its_section_is_in_that_section = _pytest(t_every_quote_with_its_section_is_in_that_section)
test_every_count_typed_is_the_classifications_and_the_pages = _pytest(t_every_count_typed_is_the_classifications_and_the_pages)
test_every_figure_and_claim_the_rows_carry_is_the_records = _pytest(t_every_figure_and_claim_the_rows_carry_is_the_records)
test_set_31s_known_item_reads_paragraph_0a_at_the_candidate = _pytest(t_set_31s_known_item_reads_paragraph_0a_at_the_candidate)
test_the_tokens_are_the_rows_and_the_fill_stage_is_resultss = _pytest(t_the_tokens_are_the_rows_and_the_fill_stage_is_resultss)
test_the_record_names_the_patch_file_so_the_fill_reaches_it = _pytest(t_the_record_names_the_patch_file_so_the_fill_reaches_it)
