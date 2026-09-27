"""v2/docs/records/README.md after the release finalizer of layers 1 to 3 (27 September 2026, MESHSAT-1357, fnd/rel2
rebased onto main 391d8579 and then 91894cd7): the worktree's row, one row per file of v2/docs/records/rel2f/ (sha256 and bytes as filed;
this script's own row from its own bytes), and a section for the three records of the second release check, filed byte
for byte in v2/docs/reviews/ by the commit that carries this README change, with their sha256. Idempotent: rows already
present are rewritten with the current sha256. Run from the worktree root, after every file of rel2f/ is final."""
import glob, hashlib, os, re

R = 'v2/docs/records/README.md'
s = open(R, encoding='utf-8').read()
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
SRC = "`fnd/rel2` (authored in the tree by the release finalizer of layers 1 to 3)"
CITED = {
    'resolve_rebase.py': "the rebased second release attempt (`7dfbfb16`, first rebased onto `391d8579`); `v2/docs/handover/LAYER-STATUS.md` (layers 2 and 3); ENGINEERING-QUESTIONS (the baseline question)",
    'check_rebase.py': "the rebased second release attempt (`7dfbfb16`); `v2/docs/handover/LAYER-STATUS.md` (layer 2)",
    'apply_compat.py': "`v2/docs/evidence/COMPATIBILITY.md` (the third tool entry, `edge_length.py`, and its paragraph)",
    'tool_compat_edge_length.out': "`v2/docs/evidence/COMPATIBILITY.md` (the third tool entry)",
    'rebind_current_evidence.py': "`v2/ecad/tools/pcb_requirements.yaml` (CON-010 and REQ-044 after each render of the rebased branch)",
    'apply_registry.py': "`v2/ecad/tools/pcb_requirements.yaml` (its header and the three open items of the second release check)",
    'ids.json': "`apply_registry.py` and `edit_docs.py` (the open item and question ids they took)",
    'edit_docs.py': "the finalizer's commit (`v2/docs/CONOPS.md`, `v2/docs/handover/LAYER-STATUS.md`, `ENGINEERING-QUESTIONS.md`, `START-HERE.md`)",
    'post_docs_registry.py': "`v2/ecad/tools/pcb_requirements.yaml` (the needs pin and the three readings bound to CONOPS); `v2/docs/handover/LAYER-STATUS.md` (layer 2)",
    'file_records.py': "this README's rows for `rel2f/` and for the three records of the second release check",
}

WT = ("| `rel2f/` | the release finalizer of layers 1 to 3 (27 September 2026, branch `fnd/rel2` rebased onto `391d8579` and then `91894cd7`): "
      "the rebase's resolver and its line-by-line check, the third tool entry of COMPATIBILITY.md, the rebinds of the two readings bound to CURRENT-EVIDENCE.md, "
      "the registry's apply script for the items the second release check left, the documents' edit script, the needs "
      "pin and the CONOPS rebinds, and the ids they took; authored in the tree, not filed from drafts |\n")
if '| `rel2f/` |' not in s:
    a = "| `rv-bat/` | review stream BAT, the battery and protection review packet |\n"
    assert s.count(a) == 1; s = s.replace(a, WT + a)

rows = []
for p in sorted(glob.glob('v2/docs/records/rel2f/*')):
    n = os.path.basename(p)
    assert n in CITED, n
    rows.append("| `rel2f/%s` | `%s` | %d | %s | %s |\n" % (n, sha(p), os.path.getsize(p), SRC, CITED[n]))
s = re.sub(r"\| `rel2f/[^`]+` \| `[0-9a-f]{64}` \| \d+ \| [^\n]*\n", "", s)
anchor = s.index("\n| `rv-", s.index("## Filed files")) + 1
s = s[:anchor] + ''.join(rows) + s[anchor:]

REV = [('v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2-2026-09-27.md', 'layer 1: FAIL for release on R2-B1',
        "`v2/docs/handover/LAYER-STATUS.md` (layer 1); registry S-77; ENGINEERING-QUESTIONS EQ-27"),
       ('v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2-2026-09-27.md', 'layer 2: no blocking finding',
        "`v2/docs/CONOPS.md` (status header); `v2/docs/handover/LAYER-STATUS.md` (layer 2); the three readings bound to CONOPS"),
       ('v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2-2026-09-27.md', 'layer 3: NOT COMPLETE on B-1 and B-2',
        "`v2/docs/handover/LAYER-STATUS.md` (layer 3); registry S-78 and S-79; ENGINEERING-QUESTIONS EQ-28 and EQ-29")]
HEAD = "## Filed in `v2/docs/reviews/`: the second release check of layers 1 to 3\n"
body = (HEAD + "\nThree fresh reviewers (AI reviews, none of them a qualified review) judged layers 1, 2 and 3 at `eb9f9030`, the "
        "second release attempt on branch `fnd/rel2` before it was rebased onto main `391d8579` and then `91894cd7` (the judged commit is kept "
        "as the local branch `fnd/rel2-eb9f9030-judged`). Each wrote its record untracked in that worktree; the release "
        "finalizer filed them byte for byte (sha256 below, taken before and after filing), and they cite the "
        "second release attempt's ids as at `eb9f9030` (its SC-51 to SC-56 and EQ-25 are SC-58 to SC-63 and EQ-26 on the "
        "rebased branch).\n\n"
        "| file | sha256 | bytes | verdict | cited by |\n|---|---|---:|---|---|\n")
for p, verdict, cited in REV:
    body += "| `%s` | `%s` | %d | %s | %s |\n" % (p, sha(p), os.path.getsize(p), verdict, cited)
body += "\n"
if HEAD in s:
    a = s.index(HEAD); b = s.index("\n## ", a + 3) + 1; s = s[:a] + body + s[b:]
else:
    a = "## Maker documents: where each is filed in `v2/vendor/`\n"
    assert s.count(a) == 1; s = s.replace(a, body + a)
open(R, 'w', encoding='utf-8').write(s)
t = open(R, encoding='utf-8').read()
assert t.count("| `rel2f/file_records.py` |") == 1
print("file_records (rel2f): %d rel2f rows, the worktree row and the second release check's section" % len(rows))
