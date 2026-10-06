#!/usr/bin/env python3
"""W90's read of set 31's 25 REVIEWED-INPUT CHANGED commits, filed as received (MESHSAT-1357, 6 October 2026, worker W94), held
as predicates on the filed text: v2/docs/records/int31/RIC-READ-W90-AS-RECEIVED.md.

The record is a header written by W94, one separator line, a blank line, and then W90's report as the coordinator extracted it
verbatim from W90's transcript (the runner file `<worktree>/_runs/claude/w90ric31/REPORT-FULL-AS-RECEIVED.md`), with exactly one
edit: the runner's path of the folder that holds the worktrees, written once in that text, replaced by the token `<worktree>`, the
form the filed checks of record l4close write (CHECK-CX44, CX45, CX46 and V6 AS-RECEIVED).

The predicates: the separator stands once and splits a header from a body; the body's sha256 is the digest pinned here (of the
normalised body, never of the runner file), the token stands on the one line the edit put it on and no runner or session path is
left; where the runner file is on this host, the body equals it after exactly that replacement, made exactly once (a synthetic
received text exercises the same predicate where it is not); the header carries its framing words (an AI review, not a qualified
one, not cx46's method, read-only, nothing credited, UNREVIEWED since cx46, prototype framing), the five revisions W90 read, the
list of edits and the pinned digest; every commit the file names (a run of 7 to 40 lowercase hexadecimal characters standing alone
and not after a decimal point) resolves to one commit and stands in this tree's history, except the stream name d8dec31 (the folder
v2/docs/records/d8dec31/, quoted by W90 from L4-E9's register; not a commit) and fnd/adopt31's 4e274eb4 (W90 read the record
there; it lands with set 31's adoption, which the coordinator merges before this branch, and until then it must be a commit of this
checkout); no em or en dash. Each predicate is also run on a mutant it must refuse.

These are software predicates on record text: they establish no electrical or thermal property and accept, close, credit or
promote nothing. Prototype framing: nothing in the kit is built, bought, powered or measured.

Read-only: git is read with `git rev-parse` and `git merge-base`; nothing is written. Runs under the suite's runner
(`python3 v2/ecad/tools/tests/run.py test_w94ricread.`) and under pytest (each t_ function has a test_ alias)."""
import base64
import hashlib
import os
import re
import subprocess
import sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import need  # noqa: E402

REC = "v2/docs/records/int31/RIC-READ-W90-AS-RECEIVED.md"
SEP = "**The report as received follows: everything after the blank line below, to the end of this file, is its text.**"
BODY_SHA256 = "1eb756b3c9d496a239e45e813af4179e7c783f9c0580bfe4a3b726db11e57c8c"   # the normalised body (W94, 6 Oct 2026)
BODY_LINES = 226
TOKEN = "<worktree>"
EDITED_LINE = 3                                            # the body's line that carried the runner path, the only one
EDITED_SPAN = "`<worktree>/_runs/claude/w90ric31/REPORT.md`"
# The runner's user path and the session temp root, stored encoded as test_public_hygiene stores them, so that this module is no
# public copy of what the tree keeps out; decoded in memory only.
_HOME = base64.b64decode("L2hvbWUvY2xhdWRlLXJ1bm5lcg==").decode()
_TMPROOT = base64.b64decode("L3RtcC9jbGF1ZGUt").decode()
PREFIX = _HOME + "/worktrees/meshsat-fieldkit"             # the folder that holds the worktrees and _runs, as W90's text named it
RUNS = os.path.join(os.path.dirname(os.path.dirname(ROOT)), "meshsat-fieldkit", "_runs")
RECEIVED = os.path.join(RUNS, "claude", "w90ric31", "REPORT-FULL-AS-RECEIVED.md")

FRAMING = (
    "An AI review (Claude, worker W90), not a qualified review, and not cx46's method",
    "is not restarted here",
    "Read-only: W90 edited no git tree and no runner file",
    "Nothing credited: this file changes no verdict, class, count or state of set 31's record",
    "every change it describes stays UNREVIEWED since cx46 until a qualified check reads it",
    "Prototype framing: nothing in the kit is built, bought, powered or measured",
)
REVISIONS = (
    "fnd/adopt31 `4e274eb4b0fa8bc495ca536db1f0443148d22f0e`",     # set 31's record W90 read (CLASSIFICATION.md, RESULT.md)
    "`dd1aed00d0a0a521063b5792550bc510c4707c59`",                   # set 30's promoted revision, the range's start
    "`5f25daf3762ecd69c8764bf60de81a80f4119eab`",                   # set 31's second candidate, the range's end
    "`4d0ff8a2bf2b11941bab939d91c99a6d8de92e5e`",                   # cx46's base
    "`06077cee85d0ed44c74c2a06c9fbb2030a0dedbc`",                   # the start of cx46's delta
)
EDITS = (
    "**The edits to the received text, and the only ones:**",
    "is replaced by the token `<worktree>`",
    "2. Nothing else.",
    "The received text carries no em dash, no en dash and no other non-ASCII character",
    "which equals the sha256 of the runner file after edit 1 alone",
    "authority: SESSION, under the owner's standing rule of 26 September 2026",
)
SHA_RX = re.compile(r"(?<![0-9A-Za-z_.])[0-9a-f]{7,40}(?![0-9A-Za-z_])")
NOT_COMMITS = {"d8dec31": "v2/docs/records/d8dec31"}     # a stream name W90 quotes from L4-E9's register; its folder exists
PENDING = {"4e274eb4b0fa8bc495ca536db1f0443148d22f0e": "fnd/adopt31 (W91), merged at set 31's adoption before this branch"}
DASHES = (chr(0x2013), chr(0x2014))                        # the en dash and the em dash, by code point
_C = {}


def _norm(t):
    return " ".join(t.split())


def _text():
    if "t" not in _C:
        _C["t"] = open(need(os.path.join(ROOT, REC), "the filed read"), encoding="utf-8").read()
    return _C["t"]


def _git(*a):
    return subprocess.run(["git", "-C", ROOT] + list(a), capture_output=True, text=True)


def _resolve(tok):
    """The full sha of the one commit `tok` names in this checkout, or None (absent, ambiguous or not a commit)."""
    r = _git("rev-parse", "--verify", "-q", tok + "^{commit}")
    return r.stdout.strip() if r.returncode == 0 else None


def _in_history(full):
    return _git("merge-base", "--is-ancestor", full, "HEAD").returncode == 0


# ------------------------------------------------------------------------------------------------------------ the predicates
def split(text):
    """(header, body, errors): the separator line once, followed by one blank line; the header before it, the body after."""
    errs = []
    n = text.split("\n").count(SEP)
    if n != 1:
        errs.append("the separator line stands %d times, not once" % n)
    i = text.find("\n" + SEP + "\n\n")
    if i < 0:
        return None, None, errs + ["no separator line followed by a blank line"]
    header, body = text[:i + 1], text[i + 1 + len(SEP) + 2:]
    if not header.strip() or not body.strip():
        errs.append("an empty header or body")
    return header, body, errs


def body_errors(body):
    errs = []
    sha = hashlib.sha256(body.encode("utf-8")).hexdigest()
    if sha != BODY_SHA256:
        errs.append("the body's sha256 is %s, not the pinned %s" % (sha[:16], BODY_SHA256[:16]))
    if body.count("\n") != BODY_LINES or not body.endswith("\n"):
        errs.append("the body has %d lines, not %d ending in a newline" % (body.count("\n"), BODY_LINES))
    lines = body.split("\n")
    at = [k + 1 for k, ln in enumerate(lines) if TOKEN in ln]
    if at != [EDITED_LINE] or EDITED_SPAN not in lines[EDITED_LINE - 1]:
        errs.append("the token %s stands on lines %s, not once on line %d in %s" % (TOKEN, at, EDITED_LINE, EDITED_SPAN))
    if _HOME in body or _TMPROOT in body:
        errs.append("the body still carries a runner or session path")
    return errs


def received_errors(received, body):
    """The body is the received text after exactly the one replacement, made exactly once."""
    errs = []
    if received.count(PREFIX) != 1:
        errs.append("the received text names the runner folder %d times, not once" % received.count(PREFIX))
    if TOKEN in received:
        errs.append("the received text carries the token %s itself, so the replacement is not its only source" % TOKEN)
    if received.replace(PREFIX, TOKEN) != body:
        a, b = received.replace(PREFIX, TOKEN).split("\n"), body.split("\n")
        k = next((j for j, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
        errs.append("the body is not the received text after the one replacement (first difference at the body's line %d)" % (k + 1))
    return errs


def header_errors(header):
    h = _norm(header)
    errs = ["the header lacks %r" % w for w in FRAMING + EDITS if _norm(w) not in h]
    errs += ["the header does not name %s" % r for r in REVISIONS if r not in h]
    if BODY_SHA256 not in h:
        errs.append("the header does not state the body's sha256")
    return errs


def dash_errors(text):
    return ["an em or en dash at line %d" % (k + 1) for k, ln in enumerate(text.split("\n")) if any(d in ln for d in DASHES)]


def sha_errors(text, resolve=_resolve, in_history=_in_history, exists=lambda p: os.path.isdir(os.path.join(ROOT, p))):
    errs = []
    toks = set(SHA_RX.findall(text))
    for tok, folder in NOT_COMMITS.items():
        if tok in toks and not exists(folder):
            errs.append("%s is read as a stream name, but %s does not exist" % (tok, folder))
    for tok in sorted(toks - set(NOT_COMMITS)):
        full = resolve(tok)
        if full is None:
            errs.append("%s does not resolve to one commit of this checkout" % tok)
        elif not full.startswith(tok):
            errs.append("%s resolves to %s, which it does not prefix" % (tok, full[:12]))
        elif not in_history(full) and full not in PENDING:
            errs.append("%s (%s) is not in this tree's history" % (tok, full[:12]))
    return errs


# ------------------------------------------------------------------------------------------------------------------- tests
def t_the_separator_splits_a_header_from_a_body_once():
    header, body, errs = split(_text())
    assert not errs, errs


def t_the_body_is_the_received_text_after_the_one_replacement():
    _, body, errs = split(_text())
    assert not errs, errs
    errs = body_errors(body)
    assert not errs, errs
    if os.path.exists(RECEIVED):    # the runner file, read where the coordinator's runs are on this host
        received = open(RECEIVED, encoding="utf-8").read()
        errs = received_errors(received, body)
        assert not errs, errs


def t_the_header_carries_its_framing_the_revisions_read_and_the_edits():
    header, _, errs = split(_text())
    assert not errs, errs
    errs = header_errors(header)
    assert not errs, errs


def t_every_commit_the_file_names_resolves_in_this_trees_history():
    text = _text()
    errs = sha_errors(text)
    assert not errs, errs
    for full in PENDING:            # until set 31's adoption lands it must at least be a commit of this checkout
        assert _resolve(full) == full, "%s (%s) is not a commit of this checkout" % (full[:8], PENDING[full])


def t_no_em_or_en_dash():
    errs = dash_errors(_text())
    assert not errs, errs


def t_the_commit_pattern_finds_what_it_is_for():
    """A pattern that matched nothing would pass everything: it finds a row's sha, a full sha and an all-digit sha, and not the
    digits of a decimal figure, a word or a sha256 digest."""
    got = set(SHA_RX.findall("| 1.1 | `bf44eb8c` | at `14082416` and %s; 0.000181221 A; the R264; %s" % (REVISIONS[1], BODY_SHA256)))
    assert got == {"bf44eb8c", "14082416", REVISIONS[1].strip("`")}, got
    toks = set(SHA_RX.findall(_text()))
    assert "d8dec31" in toks and len(toks - set(NOT_COMMITS)) >= 30, "the file's commit tokens are %d" % len(toks)


def t_each_predicate_refuses_its_mutant():
    text = _text()
    header, body, errs = split(text)
    assert not errs, errs
    # the separator: doubled, and missing its blank line
    assert split(text.replace(SEP + "\n", SEP + "\n\n" + SEP + "\n", 1))[2]
    assert split(text.replace(SEP + "\n\n", SEP + "\n", 1))[2]
    # the body: one byte added, and the token on a second line
    assert body_errors(body + "x\n")
    assert body_errors(body.replace("| # | sha |", "| # | %s |" % TOKEN, 1))
    assert body_errors(body.replace(TOKEN, PREFIX))
    # the received text, synthesised from the body: the acceptable fixture passes; a second runner path, a changed word, and a
    # received text that already carried the token are refused
    synth = body.replace(TOKEN, PREFIX)
    assert not received_errors(synth, body)
    assert received_errors(synth + PREFIX + "/x\n", body)
    assert received_errors(synth.replace("FIGURE", "FIGURES", 1), body)
    assert received_errors(synth.replace("I edited nothing", "I edited nothing %s" % TOKEN, 1), body)
    # the header: a framing word, a revision, the digest and the edit list each dropped
    assert header_errors(header.replace("not a qualified review", "a qualified review"))
    assert header_errors(header.replace("Nothing credited:", "Credited:"))
    assert header_errors(header.replace("06077cee85d0ed44c74c2a06c9fbb2030a0dedbc", "06077cee"))
    assert header_errors(header.replace(BODY_SHA256, BODY_SHA256[:16]))
    assert header_errors(header.replace("2. Nothing else.", "2. Also reworded."))
    # the dashes
    assert dash_errors(header + "a " + chr(0x2014) + " b\n") and dash_errors(body + chr(0x2013) + "\n")
    # the commits: a token that resolves to nothing, one outside the history, a stream folder that is gone
    fake = next(t for t in ("fa11ed00", "0ddba11e", "c0ffee99") if _resolve(t) is None)
    assert sha_errors(text + " `%s`\n" % fake)
    assert sha_errors(text, in_history=lambda s: False)
    assert not [e for e in sha_errors(text, in_history=lambda s: False) if "4e274eb4" in e], "the pending commit was refused"
    assert sha_errors(text, exists=lambda p: False)


for _n in [n for n in list(globals()) if n.startswith("t_")]:
    globals()["test_" + _n[2:]] = globals()[_n]
