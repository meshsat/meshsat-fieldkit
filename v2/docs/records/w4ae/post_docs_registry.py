#!/usr/bin/env python3
"""After edit_docs.py (stream w4ae, MESHSAT-1357, 27 September 2026): the registry follows the pages it edited.

CONOPS.md, PANEL.md and v2/docs/parts/grade-sources.yaml changed, so every reading bound to them must be re-read
(rules_lib refuses a stale binding). This script ASSERTS the extent of each change against the tree's git HEAD (the
commit before the edits), then re-pins CONOPS's needs table and rebinds each record with an evidence entry that starts
with the path and names what did not change:

  CONOPS.md          the revision note inserted under the title, the HOT-R1 paragraph and its closing sentence in
                     section 4c, the feasibility sentence of section 4c ("until then"), section 7a's HOT-R1 row; sections
                     1 and 2 (the needs table), 3, 4, 4a, 4b, 4d to 4f, 5 and 6 byte-identical.
  PANEL.md           two table rows (section 3's GPIO24 and section 7's 0x21 and 0x24 row); the line count unchanged.
  grade-sources.yaml C51897884's entry only.
Run from anywhere AFTER edit_docs.py and BEFORE the commit that carries the edits (it reads HEAD).
Usage: post_docs_registry.py <tree root>"""
import difflib, hashlib, json, os, re, subprocess, sys

ROOT = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(ROOT, "v2", "docs", "records", "r8int5"))
import edlib
import yaml

REG = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
ids = json.load(open(os.path.join(ROOT, "v2/docs/records/w4ae/ids.json")))
SCA, SCB = ids["SC_HOT_R1"], ids["SC_FAN"]
CO, PA, GS = "v2/docs/CONOPS.md", "v2/docs/PANEL.md", "v2/docs/parts/grade-sources.yaml"


def head(rel):
    return subprocess.run(["git", "-C", ROOT, "show", "HEAD:" + rel], capture_output=True, text=True, check=True).stdout


def now(rel):
    return open(os.path.join(ROOT, rel), encoding="utf-8").read()


def sections(text):
    """{heading: body} for every '## ' and '### ' heading, and '_top' for what precedes the first."""
    out, cur, buf = {}, "_top", []
    for l in text.split("\n"):
        if l.startswith("## ") or l.startswith("### "):
            out[cur] = "\n".join(buf); cur, buf = l, []
        else:
            buf.append(l)
    out[cur] = "\n".join(buf)
    return out


# ---- CONOPS: which sections changed
o, n = head(CO), now(CO)
so, sn = sections(o), sections(n)
assert list(so) == list(sn), "CONOPS's headings changed"
changed = [h for h in so if so[h] != sn[h]]
want = {"_top", "### 4c. The reduced mode, the heat stage, the hot and cold ends, and the targets (27 September 2026)",
        "### 7a. Choices the session took under the owner's standing rule of 26 September 2026"}
assert set(changed) == want, changed
_i, _j = sn["_top"].index("**Revised after its baseline"), sn["_top"].index("**Status: BASELINED")
assert "stream w4ae" in sn["_top"][_i:_j] and sn["_top"][:_i] + sn["_top"][_j:] == so["_top"], "the top changed beyond the note"
t = open(REG, encoding="utf-8").read()
o64, n64 = hashlib.sha256(o.encode()).hexdigest(), hashlib.sha256(n.encode()).hexdigest()
a = "needs_document_sha256: %s\n" % o64
assert t.count(a) == 1, "the needs pin is not HEAD's CONOPS"
open(REG, "w", encoding="utf-8").write(t.replace(a, "needs_document_sha256: %s\n" % n64))

# ---- PANEL: two rows
o, n = head(PA), now(PA)
ol, nl = o.split("\n"), n.split("\n")
assert len(ol) == len(nl)
diff = [k + 1 for k in range(len(ol)) if ol[k] != nl[k]]
assert len(diff) == 2 and nl[diff[0] - 1].startswith("| 24 | EXP_INT |") and nl[diff[1] - 1].startswith("| 0x21, 0x24 |"), diff

# ---- grade-sources: one entry
o, n = head(GS), now(GS)
yo, yn = yaml.safe_load(o), yaml.safe_load(n)
def by_code(y): return {e["code"]: e for e in (y.get("coded") or [])}
bo, bn = by_code(yo), by_code(yn)
assert set(bo) == set(bn) and [c for c in bo if bo[c] != bn[c]] == ["C51897884"], "grade-sources changed beyond C51897884"
assert {k: v for k, v in yo.items() if k != "coded"} == {k: v for k, v in yn.items() if k != "coded"}

W = "by stream w4ae on 27 September 2026 (HOT-R1 drawn on boards A and E, %s; board E's flyback sheet, %s)" % (SCA, SCB)
BASE = {
 CO: CO + " re-read " + W + ": a post-baseline revision note under the title, section 4c's HOT-R1 paragraph (the parts as "
     "drawn) and its closing sentence (the FAIL answered, REQ-077 INCONCLUSIVE held by FEA-004), section 4c's feasibility "
     "sentence and section 7a's HOT-R1 row change; sections 1 and 2 (the needs table, re-pinned), 3, 4, 4a, 4b, 4d, 4e, "
     "4f, 5 and 6 and every other part of 4c and 7a are byte-identical to the file at {OLD}",
 PA: PA + " re-read " + W + ": two table rows change, section 3's GPIO24 (EXP_INT also carries HOT-R1's edges) and section "
     "7's 0x21 and 0x24 row (U27's P1.5 reads HOT-R1), with the line count kept; every other line is byte-identical to the "
     "file at {OLD}",
 GS: GS + " re-read " + W + ": C51897884's entry (SS14, Zhengxin) gains its maker, its Tj range of -55 to +125 C and the "
     "filed sheet; every other entry is unchanged from the file at {OLD}",
}
WHY = {
 "REQ-005": {CO: "the critical peripherals of NEED-03 (section 2 and section 4f) are unchanged"},
 "CFL-014": {CO: "section 4's Charging row is unchanged", PA: "section 10 is unchanged"},
 "CFL-016": {CO: "sections 4, 4b and 5 are unchanged", PA: "sections 1 and 6 are unchanged, and section 7's bus table still "
             "carries the supervisors at 0x34 to 0x36"},
 "CFL-001": {PA: "no line this record reads is among the two"},
 "CFL-005": {PA: "section 7's pull statements and the panel-less kit's text are unchanged; only the U27 row names P1.5"},
 "CFL-015": {PA: "section 10 is unchanged"},
 "CON-009": {GS: "C51897884's -55 to +125 C Tj covers the envelope's -20 C floor and the 51 C inside air, and no other row "
             "moved"},
}
res = {x["id"]: x.get("evidence_result") for x in yaml.safe_load(open(REG, encoding="utf-8"))["records"]}
done = []
for rid, per in WHY.items():
    for path, why in per.items():
        try:
            old = edlib.rebind(REG, rid, path, ROOT, BASE[path] + "; " + why + ", so it stands " + str(res[rid]) +
                               " on the file at {NEW}")
        except AssertionError:
            continue   # this record is not bound to this path here
        done.append("%s:%s%s" % (rid, os.path.basename(path), "" if old else " (already current)"))
yaml.safe_load(open(REG, encoding="utf-8"))
print("post_docs_registry (w4ae): needs pin to %s; rebound %s" % (n64[:16], ", ".join(done)))
