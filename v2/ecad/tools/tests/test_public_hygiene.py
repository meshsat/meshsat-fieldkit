#!/usr/bin/env python3
"""No tracked file names the runner's user path, a session's scratch path, an internal host, the laptop or the laptop's
user path (MESHSAT-1357, 30 September 2026).

The repository is public: GitLab project 64 mirrors to github.com/meshsat/meshsat-fieldkit within minutes. The owner's
standing rule is that public files carry no internal host names, user paths or addresses. On 29 September 2026 the
tree still carried them in 71 files and in the four handover ZIPs, mostly in session records and readings that quoted
where a worker had run. The scrub of 30 September 2026 (v2/docs/records/scrub/) replaced them by neutral tokens or
derived the paths, and reissued the four snapshots; this test keeps the tree that way.

WHAT IS LEFT, AND WHY (ALLOWED below; v2/docs/records/scrub/README.md gives each in full): a filed check or record whose
bytes another file cites by sha, a reading that a registry-bound page cites by sha, the candidate patch as it was
reviewed, a binary scene file, the accepted release H1 committed unzipped, and the four accepted snapshot ZIPs as they
were published. A reissued snapshot may carry exactly the files the tree leaves, under its own version folder. Every
entry of the list must still carry a pattern: an entry whose file was fixed is removed, so the list only shrinks.

THE PATTERNS ARE STORED ENCODED, as in the scrub's own module: a test that spelled them out would be a public copy of
what it keeps out. They are decoded in memory and never written. Git history keeps the old values (the owner did not
authorize a rewrite); this test is about the tracked tree and the ZIPs in it.
"""
import base64, os, re, subprocess, zipfile
from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))

_ENC = [("runner path prefix", "L2hvbWUvY2xhdWRlLXJ1bm5lcg==", False),
        ("session temp path", "L3RtcC9jbGF1ZGUt", False),
        ("host name", "bmxsZWkwMQ==", False),
        ("laptop host name", "YW5raA==", True),
        ("laptop user path", "L2hvbWUva3lyaWFrb3Nw", False)]
PATTERNS = [(c, base64.b64decode(e).decode(), w) for c, e, w in _ENC]
_RX = re.compile(b"|".join((rb"\b%s\b" if w else b"%s") % re.escape(v.encode()) for _, v, w in PATTERNS))

ALLOWED = {
    "v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md": "a filed review record of layer 1, cited by sha256/16 in the H2 and H3 release records and elsewhere",
    "v2/docs/records/handover/H2-USABILITY-CHECK.md": "a filed check, its sha256 pinned by v2/docs/records/README.md",
    "v2/docs/records/handover/H3-COHERENCE-CHECK.md": "a filed check, its sha256 pinned by v2/docs/records/README.md",
    "v2/docs/records/handover/H3-USABILITY-CHECK.md": "a filed check, its sha256 pinned by v2/docs/records/README.md",
    "v2/docs/handover/candidates/hc3.patch": "the H1.1 candidate as reviewed, its sha256 pinned by candidates/README.md",
    "v2/docs/feasibility/fab/out/pulldowns.txt": "a reading cited by sha in FAILOVER-FABRIC.md, a page the requirements registry binds",
    "v2/cad/render/meshsat-v2-concept.blend": "a binary Blender scene; not editable as text",
}
ALLOWED_FOLDERS = {"v2/release/handover/H1/": "the accepted release H1, committed unzipped; superseded by H1-R1"}
ALLOWED_ZIPS = {"v2/release/handover/H1.zip": "accepted release H1, superseded by H1-R1",
                "v2/release/handover/H1.1.zip": "accepted release H1.1, superseded by H1.1-R1",
                "v2/release/handover/H2.zip": "accepted release H2, superseded by H2-R1",
                "v2/release/handover/H3.zip": "accepted release H3, superseded by H3-R1"}


def _git(*a):
    r = subprocess.run(["git", "-C", REPO] + list(a), capture_output=True)
    if r.returncode not in (0, 1): raise Skip("not a git checkout (%s)" % r.stderr.decode()[:80].strip())
    return r.stdout


def _hit_files():
    """Tracked files (their working-tree bytes, binaries included) that carry any pattern."""
    plain = [a for c, v, w in PATTERNS if not w for a in ("-e", v)]
    word = [a for c, v, w in PATTERNS if w for a in ("-e", v)]
    out = set(p for p in _git("grep", "-l", "-z", "-F", *plain).decode().split("\0") if p)
    out |= set(p for p in _git("grep", "-l", "-z", "-w", "-F", *word).decode().split("\0") if p)
    return out


def _allowed(p):
    return p in ALLOWED or any(p.startswith(f) for f in ALLOWED_FOLDERS)


def t_the_patterns_find_what_they_are_for():
    """A guard that matches nothing passes everything: each pattern is found in a line built from it, and the tokens
    the scrub writes are not."""
    for c, v, w in PATTERNS:
        assert _RX.search(("x %s/y" % v).encode()), "the %s pattern finds nothing" % c
    clean = "the runner; the laptop; <worktrees>/int7; <repo>/v2/ecad; /tmp/<scratchpad>/wt; <runner home>; <laptop home>"
    assert not _RX.search(clean.encode()), "a token the scrub writes reads as a hit"


def t_no_tracked_file_carries_a_private_path_or_host():
    bad = sorted(p for p in _hit_files() if not _allowed(p))
    assert not bad, ("%d tracked file(s) carry the runner's path, a session temp path, a host name or the laptop's "
                     "path; write a token instead (v2/docs/records/scrub/scrub_lib.py): %s" % (len(bad), ", ".join(bad[:8])))


def t_every_allowed_file_still_carries_what_it_was_left_for():
    hits = _hit_files()
    gone = sorted(p for p in ALLOWED if p not in hits)
    assert not gone, "allowed but clean now, remove from ALLOWED: %s" % ", ".join(gone)
    for f in ALLOWED_FOLDERS:
        assert any(p.startswith(f) for p in hits), "the folder %s carries no pattern now; remove it from the list" % f


def t_the_snapshots_carry_only_the_files_the_tree_leaves():
    """Every tracked ZIP is read entry by entry. The accepted releases stay as published; any other ZIP (a reissue, a
    gerber set) may carry a pattern only in an entry whose path under its top folder is a file the tree leaves."""
    zips = [p for p in _git("ls-files", "-z", "--", "*.zip").decode().split("\0") if p]
    assert all(z in zips for z in ALLOWED_ZIPS), "an accepted snapshot ZIP is missing from the tree"
    bad = []
    for z in zips:
        if z in ALLOWED_ZIPS: continue
        with zipfile.ZipFile(os.path.join(REPO, z)) as zf:
            for e in zf.namelist():
                if e.endswith("/") or not _RX.search(zf.read(e)): continue
                inner = e.split("/", 1)[1] if "/" in e else e
                if not (z.startswith("v2/release/handover/") and inner in ALLOWED): bad.append("%s:%s" % (z, e))
    assert not bad, "%d ZIP entr(ies) carry a pattern: %s" % (len(bad), ", ".join(bad[:6]))
