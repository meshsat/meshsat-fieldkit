"""Fixture commits and fixture checks for the layer 3 amendment's tests (MESHSAT-1357, 1 October 2026; L3-R04 and B2 of
the amendment's check astra-check-l3am-1). Not a test module: test_l3am.py and test_l3r5.py import it.

An acceptance binds a revision that holds the reviewed content, and an amendment check names the revision it read, so a
test of either positive path needs a commit holding the content under test: the working tree's before the author commits,
or a fixture copy's. `commit_with` builds one with git's plumbing on a temporary index: HEAD's tree (or a given parent's),
the files the acceptance's manifest names and the amendment's files (l3amlib.AMENDMENT_FILES) taken from the working tree,
then the overrides given. It writes unreferenced objects into the repository's object store and nothing else (no ref, no
index of the worktree, no working file); git's garbage collection prunes them. `tip` is HEAD itself when the working tree
holds HEAD's content for those files, and such a fixture commit otherwise. `amendment_check` writes a fixture check record
in a temporary directory, in the format apply_l3am_findings_closed.py states; `closed_copy` files it as the newest
independent check of a copy of l3r2.yaml and closes the findings there, as the coordinator's two steps would.
"""
import hashlib
import os
import subprocess
import sys
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "l3am"))
import l3amlib as L  # noqa: E402

MANIFEST_FILES = ("v2/ecad/tools/pcb_requirements.yaml", "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md",
                  "v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md", "v2/docs/handover/layer3/l3r2.yaml")
FILES = MANIFEST_FILES + tuple(L.AMENDMENT_FILES)
ID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid"]
SCOPE = "scope: Layer 3 amendment l3am (L3-R01 to L3-R05)"


def _git(args, env=None, data=None):
    r = subprocess.run(["git", "-C", ROOT] + ID + args, capture_output=True, env=env, input=data)
    if r.returncode != 0: raise Skip("git cannot build a fixture commit here: %s" % r.stderr.decode()[:120].strip())
    return r.stdout.decode().strip()


def commit_with(overrides=None, parent=None):
    """The sha of a commit, child of `parent` (default HEAD), whose tree is the parent's with FILES as the working tree
    holds them and each {path: bytes} of `overrides` in place."""
    parent = parent or _git(["rev-parse", "HEAD"])
    files = {p: open(os.path.join(ROOT, p), "rb").read() for p in FILES}
    files.update(overrides or {})
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tempfile.mkdtemp(prefix="l3am-index-"), "index"))
    _git(["read-tree", parent], env=env)
    for path, b in files.items():
        blob = _git(["hash-object", "-w", "--stdin"], data=b)
        _git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, path)], env=env)
    tree = _git(["write-tree"], env=env)
    return _git(["commit-tree", tree, "-p", parent, "-m", "fixture: the content under test"])


def tip():
    """HEAD when the working tree holds HEAD's content for FILES, else a fixture commit holding the working tree's."""
    r = subprocess.run(["git", "-C", ROOT, "diff", "--quiet", "HEAD", "--"] + list(FILES), capture_output=True)
    return _git(["rev-parse", "HEAD"]) if r.returncode == 0 else commit_with()


def root_commit():
    return _git(["rev-list", "--max-parents=0", "HEAD"]).split("\n")[0]


def amendment_check(rev, name="check-l3am-fixture.md", scope=SCOPE, first="accepted: yes"):
    """(absolute path, sha256/16) of a fixture check record naming `rev` as its reviewed revision."""
    p = os.path.join(tempfile.mkdtemp(prefix="l3am-check-"), name)
    open(p, "w", encoding="utf-8").write("%s\n%s\nreviewed-revision: %s\n\n# a fixture check of the amendment\n" % (first, scope, rev))
    return p, hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def with_check(raw, path, sha):
    """l3r2.yaml's text with the record filed as the newest independent check (ACCEPTED)."""
    lines = raw.split("\n")
    k = lines.index("independent_check:")
    while lines[k + 1].startswith("  - {record: "): k += 1
    return "\n".join(lines[:k + 1] + ["  - {record: %s, sha16: %s, verdict: ACCEPTED, scope: \"a fixture check of the amendment\"}" % (path, sha)]
                     + lines[k + 1:])


def closed_copy(raw, rev):
    """(text, check path): a copy of l3r2.yaml with a fixture check of `rev` filed as the newest independent check and
    the findings closed by it, as apply_l3am_findings_closed.py writes them."""
    path, sha = amendment_check(rev)
    text = with_check(raw, path, sha)
    rf = [l for l in text.split("\n") if l.startswith("review_findings: {")]
    if len(rf) != 1 or ", state: OPEN, status: " not in rf[0]: raise AssertionError("the findings are not filed OPEN")
    head, _, _ = rf[0].partition(", state: OPEN, status: ")
    closed = head + ", state: CLOSED, checked_by: %s, status: \"%s\"}" % (
        path, "Layer 3 amendment checked; independent review findings dispositioned (L3-R01 to L3-R05)")
    return text.replace(rf[0], closed, 1), path
