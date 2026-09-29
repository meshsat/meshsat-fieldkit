#!/usr/bin/env python3
"""S-122's closure (stream s122, MESHSAT-1357), for the integrator to run LAST: after fnd/s122 is merged, after
`apply_registry_s122.py`, and after an independent check of the corrected documents has been filed.

It closes S-122 and returns CFL-016 to PASS only when all of these hold, each read by this script:
  0. set 14's gate, `gate_set14` below (round 4: the part-number finder probed with made-up numbers, the corrected
     sentences found by what they say and TRUE on the netlists, the closing check's marker and provenance);
  1. the registry carries the rebinds of `apply_registry_s122.py` and `apply_registry_s122_r4.py` and every document
     CFL-016 is bound to is bound at the sha16 it has now (nothing changed after the rebind);
  2. it RE-RUNS the inventory and the verdicts itself (`inventory.render`, `verdicts.judge` and `verdicts.render`, on
     the committed netlists and documents at this commit) and finds 0 STALE and 0 UNJUDGED sentences, and the texts
     it writes are identical to the committed `inventory.out` and `verdicts.out` (so the committed record is this
     commit's);
  3. CONOPS.md is read under the baseline rule (CFL-016's baseline entry): a CONOPS sentence whose value differs from
     the netlists is BASELINE only with its row on the status page, and the status page's section and EMCON.md section
     0a.1, where the current values are kept, were judged directly (both carry sentences in verdicts.out); and every
     CONOPS sentence that states something absent, owed, not drawn or not connected, in any section, is inventoried and
     is TRUE or BASELINE, or binds each such word to a phrase not about the circuit (`verdicts.absent_rule`, round 3;
     a sentence that does neither is UNJUDGED, which step 2 refuses);
  4. the independent check named on the command line is committed at HEAD with the bytes the working file has (a file
     only staged is refused), its first line reads `mergeable: yes`, and its text names every document of the scope
     (PANEL.md, CONOPS.md, V2-SPEC.md, OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md, pcb_decisions.yaml, EMCON.md,
     DEFINITION-STATUS.md) and `verdicts.out`; what the check says it read is left in its own words, and this script
     quotes none of it.
Then it moves S-122 to closed_items (closed_by the current commit, the closing evidence naming the counts this run
read and the check's path), sets CFL-016's evidence_result to PASS, drops its waits_on and appends one entry. Every
other record and item is asserted unchanged; the registry re-parses. Refuses a second run.
Run: python3 close_s122.py <path of the filed check, relative to the repository>."""
import os, random, re, subprocess, sys

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
         "EMCON.md", "DEFINITION-STATUS.md", "verdicts.out")
OUTSIDE = ("PANEL.md's head and sections 4, 8 and 11; CONOPS.md's sections other than 2a, M2, M4, 4 with 4a to 4f, and 5, "
           "except its sentences that state something absent or owed (the wordings of s122lib.ABSENT), which are read in every section; "
           "OPERATING-ENVELOPE.md sections 1 and 5 to 8; ASSEMBLY.md's sections other than 2, 4, 8 and 9; EMCON.md's "
           "sections other than 0a.1; the status page's sections other than its section of CONOPS's current circuit values")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def gate_set14(chk):
    """Set 14's gate, as stream s122's round 4 rewrote it (the fourth check of set 14, q2 to q4; its first form was
    v2/docs/records/int15/apply_check15c_fixes.py's). S-122 closes only when all four hold, each read here:
      (a) the finder is an instrument: `s122lib.names` returns, under `parts`, the five part numbers check-int15-1 found
          in their probe sentences AND ten part numbers made up at run time in five shapes (a list of known strings
          cannot pass), and returns none of five non-parts made up at run time (a commit, a registry identifier, a
          designator, a net, an ingress code: a finder that returns every token cannot pass);
      (b) the corrected sentences, found by what they say and not by a row label: in V2-SPEC.md and
          OPERATING-ENVELOPE.md, outside the correction notes, every "<part> display switch", "<part> codec", "<part>
          hot swap", "<part> hot-swap controller" and "<part> M.2 B-key socket" names the generated part (TS3DV642,
          PCM2912A, LM5069, LM5069, 2199119), each such sentence is TRUE in this commit's verdicts, its judgement is not
          HISTORY, and its own assertions include the generated part on its board (B U3 and U4, D U6, E U6, B J_M2C2);
          at least one such sentence stands in each place; no sentence there names the TMDS341A, the WM8960, a TRACO
          part or the MDT420B, and a sentence that names the dock strip names the LM5176 only as A22's;
      (c) the filed check carries the closing check's marker, the heading "## S-122 closing check", and under it names
          each sentence of (b) by its document and current line ("V2-SPEC.md line 82"), so only a check written to close
          S-122 on these sentences passes;
      (d) the check names check-int15-1 and was committed on a line that carries 097d2517.
    The gate reads the verdicts; whether each corrected sentence is true in substance stays the filed check's to say."""
    rnd = random.SystemRandom()
    up = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    def word(n): return "".join(rnd.choice(up) for _ in range(n))
    def digs(n): return "".join(rnd.choice("0123456789") for _ in range(n))
    shapes = [lambda: word(rnd.randint(2, 4)) + digs(rnd.randint(3, 5)) + word(rnd.randint(0, 2)),
              lambda: digs(2) + word(3) + digs(1) + word(1) + digs(3) + word(2),
              lambda: word(3) + digs(4) + "-" + word(3),
              lambda: str(rnd.randint(1, 9)) + digs(6) + "-" + str(rnd.randint(1, 9)),
              lambda: word(3) + " " + digs(2) + "-" + digs(4) + word(3)]
    frames = ["the %s display switch", "Direwolf on the %s codec", "| %s | dock strip, inside |", "a socket, %s, on board B",
              "two %s switches and a relay"]
    probes = [("the WM8960 codec", "WM8960"), ("a TRACO TEN 40-2412WIN converter", "TEN 40-2412WIN"),
              ("an Amphenol M.2 B-key socket, MDT420B01001", "MDT420B01001"), ("the TMDS341A display switch", "TMDS341A"),
              ("two TS3DV642 switches", "TS3DV642")]
    for shape in shapes:
        for _ in range(2):
            p = shape()
            while not re.search(r"\d{3}", p) or re.split(r"[- /]", p)[0] in L.STDBODY: p = shape()
            probes.append((rnd.choice(frames) % p, p))
    nets = L.all_nets(L.netlists())
    for sent, part in probes:
        if part not in (L.names(sent, nets).get("parts") or []):
            refuse("the finder does not read the part number %s in %r (S-122's set 14 extension)" % (part, sent))
    nonparts = ["%07x" % rnd.randrange(0x1000000, 0xfffffff) + "a", "%s-%s" % (word(3), digs(3)), "U%s" % digs(3),
                "%s_%s" % (word(4), word(3)), "IP%s" % digs(2)]
    for np_ in nonparts:
        got = L.names("the part %s here" % np_, nets).get("parts") or []
        if got: refuse("the finder reads %r as a part number %s: it does not tell parts from other tokens" % (np_, got))
    # (b) the corrected sentences in this commit's verdicts, found by what they say
    nls = L.netlists()
    rows = V.judge(L.inventory(nls), nls)
    note = {}
    for rel in ("v2/docs/V2-SPEC.md", "v2/docs/OPERATING-ENVELOPE.md"):
        for key, title, kind, line, text, _rk in L.md_blocks(rel):
            if kind == "heading": continue
            note[(os.path.basename(rel), line)] = title.startswith("Corrections") or bool(re.match(r"^\**Corrected", text))
    rules = [("V2-SPEC.md", r"(\S+) display switch", "TS3DV642", ["B U3 value has 'TS3DV642", "B U4 value has 'TS3DV642"]),
             ("V2-SPEC.md", r"(\S+)(?: USB)? codec", "PCM2912A", ["D U6 value has 'PCM2912A"]),
             ("V2-SPEC.md", r"(\S+) hot swap", "LM5069", ["E U6 value has 'LM5069"]),
             ("OPERATING-ENVELOPE.md", r"(\S+) hot-swap controller", "LM5069", ["E U6 value has 'LM5069"]),
             ("OPERATING-ENVELOPE.md", r"(\S+) M\.2 B-key socket", "2199119", ["B J_M2C2 value has 'TE 2199119"])]
    found, lines = {i: 0 for i in range(len(rules))}, []
    for sid, d, verdict, det, s in rows:
        doc = sid.split("#")[0]
        if doc not in ("V2-SPEC.md", "OPERATING-ENVELOPE.md"): continue
        line = int(re.search(r":L(\d+):", sid).group(1))
        if note.get((doc, line)): continue
        for bad in ("TMDS341", "WM8960", "TRACO", "TEN 40", "MDT420B"):
            if bad in s: refuse("%s line %d still names %s outside a correction note" % (doc, line, bad))
        if "dock strip" in s and re.search(r"(?<!A22's )LM5176", s):
            refuse("%s line %d names the LM5176 in a dock strip sentence other than as A22's" % (doc, line))
        for i, (rdoc, rx, part, need) in enumerate(rules):
            if doc != rdoc: continue
            for m in re.finditer(rx, s):
                w = m.group(1).strip("`,;()")
                if not L.is_partno(w) and not L.partnos(w): continue
                if part not in w: refuse("%s line %d: %r names %s, not the generated %s" % (doc, line, m.group(0), w, part))
                judg = " ".join(x for x in det if x.startswith("judgement: "))
                asrt = " ".join(x for x in det if x.startswith("asserted ("))
                if verdict != "TRUE" or judg.startswith("judgement: HISTORY"):
                    refuse("%s line %d (%s) is %s%s, not TRUE on the netlists" % (doc, line, m.group(0), verdict,
                                                                                 ", HISTORY" if "HISTORY" in judg else ""))
                miss = [n for n in need if n not in asrt]
                if miss: refuse("%s line %d (%s): its judgement does not assert %s" % (doc, line, m.group(0), "; ".join(miss)))
                found[i] += 1
                lines.append("%s line %d" % (doc, line))
    empty = [rules[i][1] for i, n in found.items() if not n]
    if empty: refuse("no corrected sentence stands for %s" % "; ".join(empty))
    # (c) the closing check's marker, with the sentences by their lines, and (d) its provenance
    path = chk if os.path.isabs(chk) else os.path.join(L.TOP, chk)
    if not os.path.exists(path): refuse("no check at %s" % chk)
    txt = open(path, encoding="utf-8").read()
    if "\n## S-122 closing check" not in txt: refuse("the check carries no '## S-122 closing check' heading")
    under = txt.split("\n## S-122 closing check", 1)[1]
    miss = sorted(set(x for x in lines if x not in under))
    if miss: refuse("the check's closing section does not name %s" % ", ".join(miss))
    if "check-int15-1" not in txt: refuse("the check does not name check-int15-1")
    added = subprocess.run(["git", "-C", L.TOP, "log", "--diff-filter=A", "--format=%H", "--", os.path.relpath(path, L.TOP)],
                           capture_output=True, text=True).stdout.split()
    if not added or subprocess.run(["git", "-C", L.TOP, "merge-base", "--is-ancestor", "097d2517", added[-1]]).returncode:
        refuse("the check was not committed on a line that carries 097d2517 (set 14's extension of S-122)")


def main():
    if len(sys.argv) != 2: refuse("usage: close_s122.py <the filed independent check>")
    chk = sys.argv[1]
    gate_set14(chk)
    reg = open(REG, encoding="utf-8").read()
    before = yaml.safe_load(reg)
    if not any(x["id"] == "S-122" for x in before["open_items"]): refuse("S-122 is not open")
    rec = {r["id"]: r for r in before["records"]}["CFL-016"]
    if not any("apply_registry_s122" in str(e) for e in rec.get("evidence") or []): refuse("apply_registry_s122.py has not run")
    if not any("apply_registry_s122_r4" in str(e) for e in rec.get("evidence") or []): refuse("apply_registry_s122_r4.py has not run")
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
    # CONOPS.md under the baseline rule: every BASELINE sentence is CONOPS's and has its row on the status page (verdicts.py
    # turns one without a row into STALE), and the status page's section and EMCON.md section 0a.1 were judged directly
    if not any("The baseline rule (stream s122, round 2" in str(e) for e in rec.get("evidence") or []): refuse("CFL-016 has no baseline entry")
    if not V.status_rows(): refuse("the status page carries no row of CONOPS's current circuit values")
    for doc in ("EMCON.md", "DEFINITION-STATUS.md"):
        if not re.search(r"(?m)^%s: [1-9]\d* sentences" % re.escape(doc), ver_txt): refuse("%s was not judged" % doc)
    for name, txt in (("inventory.out", inv_txt), ("verdicts.out", ver_txt)):
        if open(os.path.join(HERE, name), encoding="utf-8").read() != txt: refuse("the committed %s is not this commit's: re-run %s" % (name, name.replace(".out", ".py")))
    # 3. the filed independent check
    p = os.path.join(L.TOP, chk)
    if not os.path.isfile(p): refuse("no check at %s" % chk)
    # committed means in HEAD's tree with the same bytes as the working file (a file only staged is refused: check m10)
    blob = subprocess.run(["git", "-C", L.TOP, "show", "HEAD:%s" % chk], capture_output=True)
    if blob.returncode or blob.stdout != open(p, "rb").read(): refuse("%s is not committed at HEAD as it stands" % chk)
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
    closing = ("Stream s122 (v2/docs/records/s122/README.md): the sentences of the documents CFL-016 names, in the scope "
               "s122lib.SCOPE sets (outside it the scripts read nothing: %s), were inventoried (inventory.py) and judged "
               "against the committed netlists of boards A, B, C, D, E and P and the generators (verdicts.py and "
               "judgements.py), makers' part numbers among what the finder reads since round 4; verdicts-base.out read %s STALE sentences of %s in the base's documents at e57a7365, and "
               "apply_docs_s122.py, apply_docs_s122_r2.py, apply_docs_s122_r3.py and apply_docs_s122_r4.py corrected the five correctable documents and the status page, asserting every part, "
               "pin, net, count and generator line their new text names before they wrote. CONOPS.md, a baselined "
               "definition, is restored to its text at c5430071 and read through handover/DEFINITION-STATUS.md: each of its "
               "passages whose value differs from the netlists is BASELINE with its current value kept on the status page "
               "and in feasibility/EMCON.md section 0a.1, both judged directly. At %s this closure re-ran the inventory and "
               "the verdicts and read %d sentences in that scope: %d TRUE, 0 STALE, %d BASELINE, %d NOT DERIVABLE, 0 "
               "UNJUDGED, %d assertions (%s), identical to the committed inventory.out and verdicts.out. The filed "
               "independent check is %s; this script reads only that it is committed at HEAD, that its first line is "
               "'mergeable: yes' and that it names each document; what it read is in its own words there."
               % (OUTSIDE, m0.group(2), m0.group(1), head[:8], tot["sentences"], tot["TRUE"], tot["BASELINE"],
                  tot["NOT DERIVABLE"], tot["asserted"], counts, chk))
    entry = ("v2/docs/records/s122/close_s122.py (S-122 closed at %s): the inventory and the verdicts re-run by the closure "
             "read %d sentences in the scope s122lib.SCOPE sets for the documents this record names (outside it the scripts "
             "read nothing: %s), 0 STALE and 0 UNJUDGED on the committed netlists (v2/docs/records/s122/verdicts.out); "
             "CONOPS.md is read through its status page under the baseline rule, %d of its sentences BASELINE with their "
             "current values kept on handover/DEFINITION-STATUS.md and in feasibility/EMCON.md section 0a.1, which were "
             "judged directly; and the independent check %s is filed. So in that scope no sentence of the five correctable "
             "documents and of decisions 28 and 40, and no place the status page names for CONOPS.md, is judged to describe "
             "a replaced circuit, and the envelope was re-pinned by apply_registry_s122.py. What is NOT DERIVABLE (held "
             "documents, firmware, procedures and dated history, %d sentences) is left as it stands and said so in "
             "verdicts.out. The result is PASS (was FAIL)." % (head[:8], tot["sentences"], OUTSIDE, tot["BASELINE"], chk,
                                                               tot["NOT DERIVABLE"]))
    for txt in (closing, entry):
        A.screen(txt, "S-122")
        if any(d in txt for d in L.DASHES): refuse("a dash")
    out = reg
    i, j = A.span(out, "S-122")
    title = yaml.safe_load(out[i:j])[0]["title"]
    out = out[:i] + out[j:]
    ci = out.index("\nrecords:\n") + 1   # the end of closed_items (check-int15-3 p4)
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
