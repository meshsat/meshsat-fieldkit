#!/usr/bin/env python3
"""An independent check of the restructure's map (MESHSAT-1357, branch fnd/defstab): it reads the base documents
from git, the restructured files and the status page from the working tree, and moves.json, and asks three things
without using build.py's code.

1. Conservation: the whitespace-normalised text of each original document equals its restructured definition part
   with every moved block put back where the map says it stood (by old line range), so nothing was lost, added or
   reworded in the definition except the new head.
2. Every moved block's sha256 in the map is the sha256 of the text at its old line range, and the same bytes stand at
   its new location (the status page, or the file's appendix, a demoted heading or an added table header aside).
3. The CONOPS needs table is byte-identical, and every kept definition block's sha256_after is found as a block of the
   restructured file.

Usage: verify.py <worktree root>
"""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", ".."))
M = json.load(open(os.path.join(HERE, "moves.json")))
BASE = M["base"]


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def norm(s): return " ".join(s.split())


def show(p): return subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, p)], check=True,
                                   capture_output=True).stdout.decode("utf-8")


status = open(os.path.join(ROOT, M["status_page"]["path"]), encoding="utf-8").read()
ok = True
for fid, f in M["files"].items():
    orig = show(fid)
    new = open(os.path.join(ROOT, fid), encoding="utf-8").read()
    assert sha(orig) == f["sha256_before"] and sha(new) == f["sha256_after"], fid
    lines = orig.split("\n")
    # the definition part: from the first line after the head block to the appendix heading
    app = new.index("\n## Appendix: review and status history (not part of the baseline)\n")
    body = new[:app]
    # the head block ends at the first line that is the original's first kept line
    moved = sorted(f["moved"], key=lambda m: m["old_lines"][0])
    # 2. each moved block: its sha at the old line range, and its bytes at the new place
    for m in moved:
        a, b = m["old_lines"]
        seg = "\n".join(lines[a - 1:b])
        tgt = status if "DEFINITION-STATUS" in m["new_location"] else new
        found = None
        first_len = len(lines[a - 1]); last_start = len(seg) - len(lines[b - 1])
        for start in [k for k in range(first_len) if k == 0 or seg[k - 1] == " "]:
            for end in [k for k in range(len(seg), max(start, last_start - 1), -1) if k == len(seg) or seg[k] == " "]:
                t = seg[start:end]
                if sha(t) == m["sha256"]:
                    found = t; break
            if found: break
        if found is None:
            print("FAIL %s %s: no text at lines %d to %d has the recorded sha256" % (fid, m["id"], a, b)); ok = False; continue
        m["_text"] = found
        if found not in tgt:
            print("FAIL %s %s: its text is not at its new location" % (fid, m["id"])); ok = False
    # 1. conservation: remove the moved texts from the original and compare with the definition part less the head
    rest = orig
    for m in moved:
        if "_text" in m:
            assert rest.count(m["_text"]) == 1, m["id"]
            rest = rest.replace(m["_text"], "", 1)
    # the new definition part begins at the original's first kept words
    title = orig.split("\n", 1)[0]
    first_kept = norm(rest[len(title):])[:60]
    k = norm(body).index(first_kept)
    new_def = norm(body)[k:]
    old_def = norm(rest[len(title):])
    if new_def != old_def:
        # locate the first difference
        d = next((i for i, (x, y) in enumerate(zip(new_def, old_def)) if x != y), min(len(new_def), len(old_def)))
        print("FAIL %s: the definition part differs from the original less its moved blocks at %r / %r"
              % (fid, new_def[max(0, d - 60):d + 60], old_def[max(0, d - 60):d + 60])); ok = False
    else:
        print("PASS %s: the definition part is the original less its %d moved blocks, word for word (%d characters "
              "normalised)" % (fid, len(moved), len(new_def)))
    # 3. kept blocks
    nb = {sha(b.strip("\n")) for b in re.split(r"\n\n+", new)}
    miss = [e["old_lines"] for e in f["definition_blocks"] if e["kept"] and e["sha256_after"] not in nb]
    print(("PASS" if not miss else "FAIL") + " %s: %d kept blocks found by sha256_after%s" % (
        fid, sum(1 for e in f["definition_blocks"] if e["kept"]), "" if not miss else ", missing %s" % miss))
    ok = ok and not miss
    if fid.endswith("CONOPS.md"):
        def table(t):
            i = t.index("## 2. Needs\n"); j = t.index("\n\n", t.index("| NEED-19 |", i)); return t[t.index("| ID |", i):j]
        same = table(orig) == table(new)
        print(("PASS" if same else "FAIL") + " the needs table is byte-identical (sha256 %s)" % sha(table(new))[:16])
        ok = ok and same
print("verify:", "ALL PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
