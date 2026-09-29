#!/usr/bin/env python3
"""S-122's closure (stream s122, MESHSAT-1357), for the integrator to run LAST: after fnd/s122 is merged, after
`apply_registry_s122.py`, and after an independent check of the corrected documents has been filed.

It closes S-122 and returns CFL-016 to PASS only when all of these hold, each read by this script:
  1. the registry carries `apply_registry_s122`'s rebinds and every document CFL-016 is bound to is bound at the sha16
     it has now (nothing changed after the rebind);
  2. it RE-RUNS the inventory and the verdicts itself (`inventory.render`, `verdicts.judge` and `verdicts.render`, on
     the committed netlists and documents at this commit) and finds 0 STALE and 0 UNJUDGED sentences, and the texts
     it writes are identical to the committed `inventory.out` and `verdicts.out` (so the committed record is this
     commit's);
  3. the independent check named on the command line is a file in the tree whose first line reads `mergeable: yes`
     and whose text names every document of the scope (PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md,
     TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml) and `verdicts.out`; what the check says it read is left in its own
     words, and this script quotes none of it.
Then it moves S-122 to closed_items (closed_by the current commit, the closing evidence naming the counts this run
read and the check's path), sets CFL-016's evidence_result to PASS, drops its waits_on and appends one entry. Every
other record and item is asserted unchanged; the registry re-parses. Refuses a second run.
Run: python3 close_s122.py <path of the filed check, relative to the repository>."""
import os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import inventory as I  # noqa: E402
import verdicts as V  # noqa: E402

sys.path.insert(0, os.path.join(L.TOP, "v2/docs/records/int7"))
import apply_check1_answers as A  # noqa: E402

TAG = "close_s122"
REG = os.path.join(L.TOP, "v2/ecad/tools/pcb_requirements.yaml")
NAMES = ("PANEL.md", "CONOPS.md", "V2-SPEC.md", "OPERATING-ENVELOPE.md", "TEST-PLAN.md", "ASSEMBLY.md", "pcb_decisions.yaml",
         "verdicts.out")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def main():
    if len(sys.argv) != 2: refuse("usage: close_s122.py <the filed independent check>")
    chk = sys.argv[1]
    reg = open(REG, encoding="utf-8").read()
    before = yaml.safe_load(reg)
    if not any(x["id"] == "S-122" for x in before["open_items"]): refuse("S-122 is not open")
    rec = {r["id"]: r for r in before["records"]}["CFL-016"]
    if not any("apply_registry_s122" in str(e) for e in rec.get("evidence") or []): refuse("apply_registry_s122.py has not run")
    if rec.get("evidence_result") != "FAIL" or rec.get("waits_on") != ["S-122"]: refuse("CFL-016's state")
    for b in rec.get("evidence_bound_to") or []:
        rel, s = b.rsplit("@", 1)
        if L.sha16(rel) != s: refuse("CFL-016 is bound to %s, and the file is now %s: re-read and rebind first" % (b, L.sha16(rel)))
    # 2. the inventory and the verdicts, re-run here
    nls = L.netlists()
    inv = L.inventory(nls)
    inv_txt = I.render(inv, nls)
    ver_txt, tot = V.render(V.judge(inv, nls), nls)
    if tot["STALE"] or tot["UNJUDGED"]: refuse("the verdicts read %d STALE and %d UNJUDGED" % (tot["STALE"], tot["UNJUDGED"]))
    for name, txt in (("inventory.out", inv_txt), ("verdicts.out", ver_txt)):
        if open(os.path.join(HERE, name), encoding="utf-8").read() != txt: refuse("the committed %s is not this commit's: re-run %s" % (name, name.replace(".out", ".py")))
    # 3. the filed independent check
    p = os.path.join(L.TOP, chk)
    if not os.path.isfile(p): refuse("no check at %s" % chk)
    if subprocess.run(["git", "-C", L.TOP, "ls-files", "--error-unmatch", chk], capture_output=True).returncode: refuse("%s is not committed" % chk)
    t = open(p, encoding="utf-8").read()
    if t.lstrip().split("\n", 1)[0].strip() != "mergeable: yes": refuse("the check's first line is not 'mergeable: yes'")
    missing = [n for n in NAMES if n not in t]
    if missing: refuse("the check names no %s" % ", ".join(missing))
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    counts = "; ".join(re.sub(r", \d+ assertions$", "", l).replace(": ", " ", 1) for l in ver_txt.split("\n")
                       if re.match(r"^[\w.-]+: \d+ sentences", l))
    base_tot = [l for l in open(os.path.join(HERE, "verdicts-base.out"), encoding="utf-8") if l.startswith("total: ")]
    m0 = re.match(r"^total: (\d+) sentences, \d+ TRUE, (\d+) STALE", base_tot[0]) if base_tot else None
    if not m0: refuse("verdicts-base.out has no total line")
    closing = ("Stream s122 (v2/docs/records/s122/README.md): the documents CFL-016 names were inventoried sentence by sentence "
               "(inventory.py, the scope in s122lib.SCOPE) and judged against the committed netlists of boards A, B, C, D, E "
               "and P and the generators (verdicts.py and judgements.py); verdicts-base.out read %s STALE sentences of %s at "
               "e57a7365, and apply_docs_s122.py corrected them, asserting every part, pin, net and generator line its new "
               "text names before it wrote. At %s this closure re-ran the inventory and the verdicts and read %d sentences: "
               "%d TRUE, 0 STALE, %d NOT DERIVABLE, 0 UNJUDGED, %d assertions (%s), identical to the committed inventory.out "
               "and verdicts.out. The filed independent check is %s; this script reads only that its first line is "
               "'mergeable: yes' and that it names each document; what it read is in its own words there."
               % (m0.group(2), m0.group(1), head[:8], tot["sentences"], tot["TRUE"], tot["NOT DERIVABLE"], tot["asserted"],
                  counts, chk))
    entry = ("v2/docs/records/s122/close_s122.py (S-122 closed at %s): the inventory and the verdicts re-run by the closure "
             "read %d sentences of the documents this record names, 0 STALE and 0 UNJUDGED on the committed netlists of set "
             "12 (v2/docs/records/s122/verdicts.out), and the independent check %s is filed; so no sentence of the named "
             "documents and outcomes that names a part, a net, a board, a rail, a gate function or a generator line is "
             "judged to describe a replaced circuit, and the envelope was re-pinned by apply_registry_s122.py. What is NOT "
             "DERIVABLE (held documents, firmware, procedures and dated history, %d sentences) is left as it stands and "
             "said so in verdicts.out. The result is PASS (was FAIL)." % (head[:8], tot["sentences"], chk, tot["NOT DERIVABLE"]))
    for txt in (closing, entry):
        A.screen(txt, "S-122")
        if any(d in txt for d in L.DASHES): refuse("a dash")
    out = reg
    i, j = A.span(out, "S-122")
    title = yaml.safe_load(out[i:j])[0]["title"]
    out = out[:i] + out[j:]
    ci = out.index("\nclosed_items:\n") + len("\nclosed_items:\n")
    item = ("  - id: S-122\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s"
            % (head, A.fold(closing, 6, 120), A.fold(title, 6, 120)))
    out = out[:ci] + item + out[ci:]
    i, j = A.span(out, "CFL-016")
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
    if t.count("\n    evidence_result: FAIL\n    waits_on:\n      - S-122\n") != 1: refuse("CFL-016's result lines")
    t = t.replace("\n    evidence_result: FAIL\n    waits_on:\n      - S-122\n", "\n    evidence_result: PASS\n", 1)
    out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        if (rid == "CFL-016" and dd != {"evidence", "evidence_result", "waits_on"}) or (rid != "CFL-016" and dd): refuse("%s: %s" % (rid, dd))
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(oi) - set(ai) != {"S-122"} or set(ai) - set(oi) or any(oi[x] != ai[x] for x in ai): refuse("open items other than S-122 moved")
    oc, ac = {x["id"]: x for x in before["closed_items"]}, {x["id"]: x for x in after["closed_items"]}
    if set(ac) - set(oc) != {"S-122"} or any(oc[x] != ac[x] for x in oc): refuse("closed items other than S-122 moved")
    if " ".join(ac["S-122"]["title"].split()) != " ".join(title.split()): refuse("S-122's title does not read back")
    top = {k for k in set(before) | set(after) if k not in ("records", "open_items", "closed_items") and before.get(k) != after.get(k)}
    if top: refuse("top-level fields moved: %s" % top)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("%s: S-122 closed at %s; CFL-016 reads PASS (was FAIL); %d sentences, 0 STALE, 0 UNJUDGED; check %s" % (
        TAG, head[:8], tot["sentences"], chk))
    return 0


if __name__ == "__main__":
    sys.exit(main())
