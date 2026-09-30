"""Fixture commits for the layer 3 amendment's acceptance tests (MESHSAT-1357, 1 October 2026; L3-R04). Not a test module:
test_l3am.py and test_l3r5.py import it.

An acceptance binds a revision that holds the reviewed content, so a test of the positive path needs a commit holding the
content under test: the working tree's before the author commits, or a fixture copy's. `commit_with` builds one with git's
plumbing on a temporary index: HEAD's tree, the four files the acceptance's manifest names taken from the working tree,
then the overrides given. It writes unreferenced objects into the repository's object store and nothing else (no ref, no
index of the worktree, no working file); git's garbage collection prunes them.
"""
import os
import subprocess
import tempfile

from harness import Skip

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
MANIFEST_FILES = ("v2/ecad/tools/pcb_requirements.yaml", "v2/docs/handover/layer3/OWNER-INSTRUCTION-2026-09-30.md",
                  "v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md", "v2/docs/handover/layer3/l3r2.yaml")
ID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid"]


def _git(args, env=None, data=None):
    r = subprocess.run(["git", "-C", ROOT] + ID + args, capture_output=True, env=env, input=data)
    if r.returncode != 0: raise Skip("git cannot build a fixture commit here: %s" % r.stderr.decode()[:120].strip())
    return r.stdout.decode().strip()


def commit_with(overrides=None):
    """The sha of a commit whose tree is HEAD's with the manifest's four files as the working tree holds them and each
    {path: bytes} of `overrides` in place."""
    files = {p: open(os.path.join(ROOT, p), "rb").read() for p in MANIFEST_FILES}
    files.update(overrides or {})
    env = dict(os.environ, GIT_INDEX_FILE=os.path.join(tempfile.mkdtemp(prefix="l3am-index-"), "index"))
    _git(["read-tree", "HEAD"], env=env)
    for path, b in files.items():
        blob = _git(["hash-object", "-w", "--stdin"], data=b)
        _git(["update-index", "--add", "--cacheinfo", "100644,%s,%s" % (blob, path)], env=env)
    tree = _git(["write-tree"], env=env)
    return _git(["commit-tree", tree, "-p", _git(["rev-parse", "HEAD"]), "-m", "fixture: the content under test"])


def root_commit():
    return _git(["rev-list", "--max-parents=0", "HEAD"]).split("\n")[0]
