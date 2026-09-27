"""v2/docs/records/README.md after the second release attempt of layers 1 to 3 (27 September 2026, MESHSAT-1357,
fnd/rel2 from 953f5658): the worktree's row, one row per file of v2/docs/records/rel2/ (sha256 and bytes of the file as
filed; this script's own row is written from its own bytes), and a section for the first Review A pass of layer 2 and
its brief, filed byte for byte in v2/docs/reviews/ by 08f3665a, which layer 2's release check (B3) asked to carry here
with their sha256. Idempotent: rows already present are rewritten with the current sha256. Run from the worktree root,
after every file of rel2/ is final."""
import glob, hashlib, os, re

R = 'v2/docs/records/README.md'
s = open(R, encoding='utf-8').read()
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
SRC = "`fnd/rel2` (authored in the tree by the second release attempt of layers 1 to 3)"
CITED = {
    'apply_registry.py': "`v2/ecad/tools/pcb_requirements.yaml` (its header); `v2/docs/handover/LAYER-STATUS.md` (layer 3)",
    'edit_docs.py': "the second release attempt's commit (`v2/docs/handover/LAYER-STATUS.md`, its paragraph and layers 1 and 2)",
    'post_docs_registry.py': "`v2/docs/handover/LAYER-STATUS.md` (layer 2); `v2/ecad/tools/pcb_requirements.yaml` (fifteen rebinds and the needs pin), `pcb_envelope.yaml`, `pcb_rules_coverage.yaml` (ENV-001)",
    'edit_handover.py': "`v2/docs/handover/LAYER-STATUS.md` (its paragraph and the integrator lines of layers 1 to 5)",
    'tool_compat.py': "`v2/docs/evidence/COMPATIBILITY.md` (the two tool entries of 27 September 2026)",
    'tool_compat.out': "`v2/docs/evidence/COMPATIBILITY.md` (the two tool entries of 27 September 2026)",
    'file_records.py': "this README's rows for `rel2/` and for the two review files",
    'rebind_current_evidence.py': "`v2/ecad/tools/pcb_requirements.yaml` (CON-010 and REQ-044 after the render)",
}

# the worktree's row
WT = ("| `rel2/` | the second release attempt of layers 1 to 3 (27 September 2026, branch `fnd/rel2` from `953f5658`): "
      "the registry's apply script, the documents' and the handover's edit scripts, the rebinds with their asserted "
      "byte-identities, and the tool-compatibility evidence for the requirements validator's change; authored in the "
      "tree, not filed from drafts |\n")
if '| `rel2/` |' not in s:
    a = "| `rv-bat/` | review stream BAT, the battery and protection review packet |\n"
    assert s.count(a) == 1; s = s.replace(a, WT + a)

# one row per file of rel2/, inserted in path order before the first rv- row of the table of filed files
rows = []
for p in sorted(glob.glob('v2/docs/records/rel2/*')):
    n = os.path.basename(p)
    assert n in CITED, n
    rows.append("| `rel2/%s` | `%s` | %d | %s | %s |\n" % (n, sha(p), os.path.getsize(p), SRC, CITED[n]))
s = re.sub(r"\| `rel2/[^`]+` \| `[0-9a-f]{64}` \| \d+ \| [^\n]*\n", "", s)
anchor = s.index("\n| `rv-", s.index("## Filed files")) + 1
s = s[:anchor] + ''.join(rows) + s[anchor:]

# the two review files
REV = [('v2/docs/reviews/REVIEW-A-LAYER-2-2026-09-27-pass1.md',
        "the session's scratch `rvA2/REVIEW-A-LAYER-2-2026-09-27.pass1.md`, where the first pass was kept when pass 2 overwrote its path (pass 2's record, its opening paragraphs)",
        "`v2/docs/CONOPS.md` (status header and section 7a); `v2/docs/TEST-PLAN.md` (line 3); `v2/docs/OPERATING-ENVELOPE.md` (line 36); `v2/docs/handover/LAYER-STATUS.md` (layer 2)"),
       ('v2/docs/reviews/2026-09-27-review-A-layer2-brief.md',
        "`fnd/hc2` `drafts/REVIEW-A-BRIEF.md` (the brief the reviewers of Review A's layer 2 passes read)",
        "`v2/docs/CONOPS.md` (status header); `v2/docs/handover/LAYER-STATUS.md` (layer 2)")]
HEAD = "## Filed in `v2/docs/reviews/`: the first Review A pass of layer 2 and its brief\n"
body = (HEAD + "\nLayer 2's release check (`v2/docs/reviews/REVIEW-LAYER-2-RELEASE-2026-09-27.md`, finding B3) asked for the two "
        "files the Review A record of layer 2 left outside the repository to be filed with a row here and their sha256. "
        "`08f3665a` filed them byte for byte beside the other review records rather than in this folder; the second "
        "release attempt of 27 September 2026 adds their rows. Each was compared with its source by sha256 (equal).\n\n"
        "| file | sha256 | bytes | source | cited by |\n|---|---|---:|---|---|\n")
for p, src, cited in REV:
    body += "| `%s` | `%s` | %d | %s | %s |\n" % (p, sha(p), os.path.getsize(p), src, cited)
body += "\n"
if HEAD in s:
    a = s.index(HEAD); b = s.index("\n## ", a + 3) + 1; s = s[:a] + body + s[b:]
else:
    a = "## Maker documents: where each is filed in `v2/vendor/`\n"
    assert s.count(a) == 1; s = s.replace(a, body + a)
open(R, 'w', encoding='utf-8').write(s)

# this script's own row, from its own bytes (it does not change after it is written)
me = 'v2/docs/records/rel2/file_records.py'
t = open(R, encoding='utf-8').read()
assert t.count("| `rel2/file_records.py` |") == 1
print("file_records: %d rel2 rows, the worktree row and the reviews section" % len(rows))
