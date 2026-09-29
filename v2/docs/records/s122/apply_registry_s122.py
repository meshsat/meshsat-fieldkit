#!/usr/bin/env python3
"""Step 4 of stream s122 (S-122, MESHSAT-1357, 29 September 2026), for the integrator to run once the branch fnd/s122 is
merged: the registry follows the documents `apply_docs_s122.py` (round 1), `apply_docs_s122_r2.py` (round 2) and
`apply_docs_s122_r3.py` (round 3) changed.
Round 2 (the answer to `checks/check-s122-1.md` and the coordinator's ruling): CONOPS.md is restored to its baseline text
at `c5430071` and read through `handover/DEFINITION-STATUS.md`; the current circuit is kept in `feasibility/EMCON.md`
section 0a.1 and on the status page; the registry is set 13's as promoted on main (`32f26b41`, milestone `b874b744`), which fnd/s122b starts from.
Round 3 (the answer to `checks/check-s122-2.md`): the status page gains rows DC-07 to DC-09 and CONOPS.md's statements
of what is absent, owed, not drawn or not connected are judged against the netlists (the baseline entry says how).

It writes `v2/ecad/tools/pcb_requirements.yaml`, `v2/ecad/tools/pcb_envelope.yaml` and `v2/ecad/tools/pcb_rules_coverage.yaml`
and nothing else:
  1. REBIND: every record bound to a changed document (`evidence_bound_to` "<doc>@<the base sha16>") gains one evidence
     entry and moves to the new sha16. The entry's reason is read by this script from the diff (`git diff e57a7365 --
     <doc>`: the new line numbers and the sections they fall in) and from the record's own evidence text (the sections
     of that document it names); it says which of those are among the changed ones and does not re-read the rest of
     the record's argument. CONOPS.md's needs pin (`needs_document_sha256`) moves too, after the script asserts that the
     diff starts after the needs table (line 146).
  2. CFL-016: one entry naming `records/s122/inventory.out` and `verdicts.out` with the counts this script reads from
     them (and from `verdicts-base.out`); CFL-016 stays FAIL and waits on S-122, whose closure is `close_s122.py`.
  3. The four wording minors of `records/int13/checks/check-int13-4.md` (n1 to n4), by appended correcting text: an
     entry on CFL-016 for n1 and n2, and a sentence appended to S-122's title for n3 and n4. No earlier text is edited.
  4. OPERATING-ENVELOPE.md changed in text and in no number: the envelope's pin (`pcb_envelope.yaml` document_sha256)
     and ENV-001's `verified_sha` (`pcb_rules_coverage.yaml`) move to the new file, after the script asserts that every
     number the envelope carries is still in the document and that the diff removes no number the base file held
     only there.
Each new sentence is screened (claims_check's CLAIM words, dashes). Every other record, open item and closed item is
asserted unchanged, and each file re-parses. Refuses a second run. Run from anywhere: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402

sys.path.insert(0, os.path.join(L.TOP, "v2/docs/records/int7"))
import apply_check1_answers as A  # noqa: E402

TAG = "apply_registry_s122"
BASE = "e57a7365"
REG = os.path.join(L.TOP, "v2/ecad/tools/pcb_requirements.yaml")
ENV = os.path.join(L.TOP, "v2/ecad/tools/pcb_envelope.yaml")
COV = os.path.join(L.TOP, "v2/ecad/tools/pcb_rules_coverage.yaml")
DOCS = {"v2/docs/PANEL.md": "4647782f5aca7c13", "v2/docs/CONOPS.md": "3c5d49078ba6dbfd",
        "v2/docs/V2-SPEC.md": "e1fdcebe8638e471", "v2/docs/OPERATING-ENVELOPE.md": "43361b02743cf3af",
        "v2/docs/TEST-PLAN.md": "ae57da0b57e214f7", "v2/docs/ASSEMBLY.md": "ee4eff52fc5df307",
        "v2/docs/feasibility/EMCON.md": "e919e9b2c633deef"}
REF = "v2/docs/records/s122/apply_docs_s122.py, apply_docs_s122_r2.py and apply_docs_s122_r3.py"
CONOPS_BASELINE = "6cb7b241cb84d729"     # CONOPS.md at c5430071, the owner's rulings of 28 September
DASHES = ("\u2014", "\u2013")

N_ENTRY = (
    "Correction (v2/docs/records/int13/checks/check-int13-4.md, minors n1 and n2; appended by stream s122, "
    "v2/docs/records/s122/apply_registry_s122.py) of the entry filed by apply_cfl016_set12: its sentence 'check-int13-2 "
    "read CONOPS.md only, and says so' is corrected to: check-int13-3 records that check-int13-2 names, of these documents, "
    "CONOPS.md only (check-int13-2 itself does not say what it did not read); and its sentence 'PANEL.md lines 155 and 156 "
    "still name U26 and board A's round 8 candidate at gen_sch_a.py:1240-1243' is corrected to: PANEL.md line 156 names "
    "U26 (gen_sch_a.py:1102), and lines 155 and 156 cite board A's round 8 candidate at gen_sch_a.py:1240-1243. The "
    "entry's other sentences and its result are not changed by this correction.")

BASELINE_ENTRY = (
    "The baseline rule (stream s122, round 2; the coordinator's ruling on the independent check "
    "v2/docs/records/s122/checks/check-s122-1.md, blocking B1): CONOPS.md is a baselined layer 2 definition, and by the "
    "reopening rule its head states and v2/docs/handover/DEFINITION-STATUS.md keeps, a changed count or a circuit "
    "correction updates the status page and the records it names, not the baseline. Set 12's circuit edits to it "
    "(a46db71b, 7a9f7b5b) and stream s122's round 1 were made against that rule and are withdrawn: CONOPS.md is restored to "
    "its text at c5430071 (6cb7b241cb84d729), asserted byte for byte by v2/docs/records/s122/apply_docs_s122_r2.py with "
    "the needs table unchanged. So this record reads CONOPS.md's circuit statements through its status page and the "
    "records it names: a CONOPS passage whose value differs from the committed netlists, or that cites a generator line, "
    "is a baseline value (BASELINE in v2/docs/records/s122/verdicts.out) when the status page's section of CONOPS's "
    "current circuit values keeps its current value (rows DC-01 to DC-09), and STALE when it does not; the places those "
    "rows name, v2/docs/feasibility/EMCON.md section 0a.1 and the status page's own rows, are judged directly against the "
    "netlists and must describe the circuit as generated. The five other documents (PANEL.md, V2-SPEC.md, "
    "OPERATING-ENVELOPE.md, TEST-PLAN.md, ASSEMBLY.md) and decisions 28 and 40 are judged directly. Round 3 (the "
    "independent check v2/docs/records/s122/checks/check-s122-2.md, blocking B1: a CONOPS.md statement that the "
    "supervisors' I2C status path is absent as generated was judged NOT DERIVABLE and had no row): a statement of "
    "CONOPS.md that something is absent, owed, not drawn or not connected as generated is judged against the netlists, "
    "TRUE or BASELINE, never NOT DERIVABLE; every sentence of CONOPS.md with those words is inventoried, in any section, "
    "and a NOT DERIVABLE judgement of one must bind each such word to a phrase of the sentence that is not about the "
    "generated circuit (verdicts.py, absent_rule; sweep_absent.py counts them). This entry changes no result.")

S122_ADD = (
    " Correction (v2/docs/records/int13/checks/check-int13-4.md, minors n3 and n4; appended by stream s122): in the words "
    "of check-int13-3, PANEL.md line 63 stays true with an incomplete parts list (R52 and D23 not named) and line 155 "
    "describes the generated circuit under a stale candidate citation, so of the passages above those two are incomplete "
    "or carry a stale citation, while PANEL.md line 156, V2-SPEC.md line 76 and CONOPS.md line 883 describe replaced "
    "circuits; and the re-derivation this item asks for covers every subject of CFL-016's statement and notes, not only "
    "the EMCON line and the parts it gates: the startup enables, ZEROIZE, the Charging and Service rows, the outlets' "
    "tie to the PA, PANEL.md section 7's bus table and the outcomes of decisions 28 and 40.")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    sys.exit(2)


def screen(text, what):
    A.screen(text, what)
    if any(d in text for d in DASHES): refuse("%s carries a dash" % what)


def sha_full(rel):
    return hashlib.sha256(open(os.path.join(L.TOP, rel), "rb").read()).hexdigest()


def sections_of(rel):
    """[(first line, section key)] of a Markdown file as it stands."""
    out = []
    for n, l in enumerate(open(os.path.join(L.TOP, rel), encoding="utf-8").read().split("\n"), 1):
        m = L.HEAD.match(l)
        if m: out.append((n, L.sec_key(m.group(2))))
    return out


def sec_at(secs, line):
    k = "head"
    for n, key in secs:
        if n <= line: k = key
    return k


def diff_lines(rel):
    d = subprocess.run(["git", "-C", L.TOP, "diff", "-U0", BASE, "--", rel], capture_output=True, text=True, check=True).stdout
    old, new = [], []
    for m in re.finditer(r"(?m)^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", d):
        a, b = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        c, e = int(m.group(3)), int(m.group(4) if m.group(4) is not None else 1)
        old += list(range(a, a + b)) if b else [a]
        new += list(range(c, c + e))
    return old, new


def named_sections(texts, base):
    """Sections (or lines) of document `base` that the record's evidence text names, read with a regex over the
    sentences that name the document."""
    found = set()
    for t in texts:
        t = " ".join(str(t).split())
        for s in re.split(r"(?<=[.;])\s", t):
            if base not in s: continue
            for m in re.finditer(r"\bsections? ((?:\d+[a-z]?(?:\.\d+)?)(?:(?:, | and | to |, and )\d+[a-z]?(?:\.\d+)?)*)", s):
                found |= set(re.findall(r"\d+[a-z]?(?:\.\d+)?", m.group(1)))
            for m in re.finditer(r"\blines? ((?:\d+)(?:(?:, | and | to |, and )\d+)*)", s):
                found |= {"line " + x for x in re.findall(r"\d+", m.group(1))}
            for m in re.finditer(r"%s:(\d+)" % re.escape(base), s):
                found.add("line " + m.group(1))
    return found


def all_sentences(rel, at):
    """{digest: sentence} of every sentence of the document (every block, in scope or not), at a commit or as it stands."""
    keep = L.AT
    L.AT = at
    try:
        out = {}
        for _k, _t, kind, _l, text, _r in L.md_blocks(rel):
            if kind == "heading": continue
            for s in L.sentences(text):
                out[L.sid_digest(s)] = s
        return out
    finally:
        L.AT = keep


def verdict_map(path):
    """{digest: verdict} from a verdicts file."""
    out = {}
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^\S.* \[([0-9a-f]+)\] (TRUE|STALE|BASELINE|NOT DERIVABLE|UNJUDGED)$", l.rstrip("\n"))
        if m: out[m.group(1)] = m.group(2)
    return out


def tally(digests, vm):
    c = {}
    for d in digests:
        v = vm.get(d, "outside the inventory")
        c[v] = c.get(v, 0) + 1
    order = ("STALE", "TRUE", "BASELINE", "NOT DERIVABLE", "UNJUDGED", "outside the inventory")
    return ", ".join("%d %s" % (c[k], k) for k in order if k in c) or "none"


def append_entry(out, rid, entry, rebind=None):
    screen(entry, rid)
    i, j = A.span(out, rid)
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    if not m: refuse("%s has no evidence list" % rid)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
    if rebind:
        if t.count(rebind[0]) != 1: refuse("%s: the binding %s found %d times" % (rid, rebind[0], t.count(rebind[0])))
        t = t.replace(rebind[0], rebind[1])
    return out[:i] + t + out[j:]


def counts(path):
    c = {}
    for l in open(path, encoding="utf-8"):
        m = re.match(r"^([\w.-]+): (\d+) sentences, (\d+) TRUE, (\d+) STALE, (\d+) BASELINE, (\d+) NOT DERIVABLE, (\d+) UNJUDGED, (\d+) assertions", l)
        if m and m.group(1) != "total": c[m.group(1)] = tuple(int(x) for x in m.groups()[1:])
    return c


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    before = yaml.safe_load(reg)
    new = {rel: L.sha16(rel) for rel in DOCS}
    for rel, s in DOCS.items():
        if new[rel] == s: refuse("%s is unchanged: merge fnd/s122 first" % rel)
    rec = {r["id"]: r for r in before["records"]}
    global VB, VA, NLS
    NLS = L.netlists()
    VB, VA = verdict_map(os.path.join(HERE, "verdicts-base.out")), verdict_map(os.path.join(HERE, "verdicts.out"))
    out = reg
    touched = {}
    for rel, old16 in DOCS.items():
        base = os.path.basename(rel)
        oldb, newb = "%s@%s" % (rel, old16), "%s@%s" % (rel, new[rel])
        bound = sorted(r["id"] for r in before["records"] if oldb in (r.get("evidence_bound_to") or []))
        if not bound: refuse("no record is bound to %s" % oldb)
        _o, nl = diff_lines(rel)
        secs = sections_of(rel)
        sb, sa = all_sentences(rel, BASE), all_sentences(rel, None)
        gone, added = sorted(set(sb) - set(sa)), sorted(set(sa) - set(sb))
        change_txt = ("of the %d sentences the diff removes, verdicts-base.out holds %s; of the %d it adds, verdicts.out "
                      "holds %s" % (len(gone), tally(gone, VB), len(added), tally(added, VA)))
        changed = sorted({sec_at(secs, n) for n in nl}, key=lambda x: (len(x), x))
        lines_txt = ", ".join(str(x) for x in sorted(set(nl)))
        nets = L.all_nets(NLS)
        partset = set()
        for s in [sb[d] for d in gone] + [sa[d] for d in added]:
            nm = L.names(s, nets)
            partset |= set(nm["refs"]) | set(nm["nets"])
        why_doc = ""
        if rel == "v2/docs/CONOPS.md":
            if new[rel] != CONOPS_BASELINE: refuse("CONOPS.md is not c5430071's text")
            why_doc = (" The file is restored to its baseline text at c5430071 under the reopening rule (the baseline entry "
                       "of CFL-016 that this script appends), so the diff withdraws set 12's circuit edits a46db71b and "
                       "7a9f7b5b; their text is kept in v2/docs/feasibility/EMCON.md section 0a.1.")
        for rid in bound:
            r = rec[rid]
            own = " ".join(str(r.get(f) or "") for f in ("title", "statement", "acceptance", "notes")) + " " + \
                  " ".join(str(e) for e in r.get("evidence") or [])
            hitp = sorted(x for x in partset if re.search(r"(?<![\w+])%s(?![\w])" % re.escape(x), own))
            part_txt = ("the changed sentences name %d parts and nets, and this record's own text names %s" % (
                len(partset), ("none of them" if not hitp else "%s of them (%s)" % (len(hitp), ", ".join(hitp[:15])))))
            named = named_sections(rec[rid].get("evidence") or [], base)
            hit = sorted({x for x in named if not x.startswith("line ")} & set(changed))
            hitl = sorted({x for x in named if x.startswith("line ")} & {"line %d" % n for n in nl})
            if not named:
                rel_txt = "this record's evidence names no section or line of this document"
            elif hit or hitl:
                rel_txt = ("of the places this record's evidence names in this document, %s %s among the changed ones"
                           % (", ".join(["section " + x for x in hit] + hitl), "is" if len(hit) + len(hitl) == 1 else "are"))
            else:
                rel_txt = ("none of the places this record's evidence names in this document (%s) is among the changed ones"
                           % ", ".join(sorted(["section " + x for x in named if not x.startswith("line ")] +
                                              [x for x in named if x.startswith("line ")])))
            entry = ("%s re-read at stream s122 (%s, %s to %s; MESHSAT-1357, open item S-122): the diff, read by "
                     "v2/docs/records/s122/apply_registry_s122.py, changes lines %s (sections %s); %s (the verdicts of "
                     "v2/docs/records/s122, verdicts-base.out on the base's documents and verdicts.out on these, both on "
                     "the committed netlists of set 13; %s); %s; %s.%s This entry does not re-read the rest of this "
                     "record's argument; rebound to %s. This entry changes no result."
                     % (rel, REF, old16, new[rel], lines_txt, "; ".join(changed), change_txt,
                        ("the restoring script asserted the file equal to c5430071's byte for byte" if rel == "v2/docs/CONOPS.md"
                         else "the correcting scripts asserted every part their new text names before they wrote"),
                        rel_txt, part_txt, why_doc, new[rel]))
            out = append_entry(out, rid, entry, ('"%s"' % oldb, '"%s"' % newb))
            touched.setdefault(rid, []).append(base)
    # the needs pin
    con = "v2/docs/CONOPS.md"
    o, _n = diff_lines(con)
    if min(o) <= 146: refuse("the CONOPS diff reaches the needs table: %s" % o[:5])
    op = "needs_document_sha256: %s" % before["needs_document_sha256"]
    if out.count(op) != 1: refuse("the needs pin")
    out = out.replace(op + "\n", "needs_document_sha256: %s\n" % sha_full(con), 1)
    # CFL-016: the inventory and the verdicts, then the n1 and n2 correction
    vb = counts(os.path.join(HERE, "verdicts-base.out"))
    va = counts(os.path.join(HERE, "verdicts.out"))
    if not va or sum(v[2] for v in va.values()) or sum(v[5] for v in va.values()): refuse("verdicts.out holds STALE or UNJUDGED sentences")
    per = "; ".join("%s %d sentences, %d STALE at the base, %d TRUE, %d BASELINE and %d NOT DERIVABLE after" % (
        d, va[d][0], vb.get(d, (0, 0, 0))[2], va[d][1], va[d][3], va[d][4]) for d in va)
    entry = ("v2/docs/records/s122/inventory.out and v2/docs/records/s122/verdicts.out (stream s122, S-122, rounds 2 and 3; "
             "written by inventory.py and verdicts.py in that folder, with the base's documents at e57a7365 in "
             "inventory-base.out and verdicts-base.out): every sentence in the scope s122lib.SCOPE sets from this record's "
             "statement and notes, the brief of S-122 and the checks check-s122-1 and check-s122-2 (PANEL.md sections 1, 2, 3, 5, 6, 7, 9 and "
             "10; CONOPS.md sections 2a, M2, M4 and 4 with 4a to 4f, and 5; V2-SPEC.md and TEST-PLAN.md whole; "
             "OPERATING-ENVELOPE.md sections 2 to 4; ASSEMBLY.md sections 2, 4, 8 and 9; decisions 28 and 40; "
             "EMCON.md section 0a.1 and the status page's section of CONOPS's current circuit values), and every sentence of "
             "CONOPS.md in any section that states something is absent, owed, not drawn or not connected, that names a part, a "
             "net, a board, a rail, a gate function, a generator line, EMCON or a count of parts, judged against the "
             "committed netlists of boards A, B, C, D, E and P of set 13 and the generators, each judgement's assertions and "
             "every stated count of parts evaluated by the script: %s. Outside that scope the scripts read nothing: PANEL.md's "
             "head and sections 4, 8 and 11, CONOPS.md's other sections but for those sentences, OPERATING-ENVELOPE.md sections 1 and 5 to 8, "
             "ASSEMBLY.md's other sections. The stale sentences of the five correctable documents were corrected by "
             "v2/docs/records/s122/apply_docs_s122.py, apply_docs_s122_r2.py and apply_docs_s122_r3.py, which asserted every part, pin, net, count "
             "and generator line their new text names before they wrote; CONOPS.md is read under the baseline rule of the "
             "next entry. What TRUE, STALE, BASELINE and NOT DERIVABLE mean is set out in v2/docs/records/s122/README.md. "
             "This record stays FAIL and waits on S-122, whose closure (v2/docs/records/s122/close_s122.py) re-runs the "
             "inventory and the verdicts and needs a filed independent check; this entry changes no result." % per)
    out = append_entry(out, "CFL-016", entry)
    out = append_entry(out, "CFL-016", BASELINE_ENTRY)
    out = append_entry(out, "CFL-016", N_ENTRY)
    # S-122's title: an appended correction
    screen(S122_ADD, "S-122")
    i, j = A.span(out, "S-122")
    blk = out[i:j]
    if "    title: >-\n" not in blk or "Correction (v2/docs/records/int13/checks/check-int13-4.md" in blk: refuse("S-122's block")
    title = " ".join(l.strip() for l in blk.split("    title: >-\n", 1)[1].split("\n") if l.strip())
    blk = blk.split("    title: >-\n", 1)[0] + "    title: >-\n" + A.fold(title + S122_ADD, 6, 120)
    out = out[:i] + blk + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {r["id"]: r for r in before["records"]}, {r["id"]: r for r in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        allowed = {"evidence", "evidence_bound_to"} if rid in touched else set()
        if rid == "CFL-016": allowed = {"evidence", "evidence_bound_to"}
        if not dd <= allowed: refuse("%s: %s moved" % (rid, dd))
        oe_, ae_ = ob[rid].get("evidence") or [], ab[rid].get("evidence") or []
        if oe_ != ae_[:len(oe_)]: refuse("%s: older entries not kept as a prefix" % rid)
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(oi) != set(ai) or any(oi[x] != ai[x] for x in oi if x != "S-122"): refuse("open items other than S-122 moved")
    if " ".join(ai["S-122"]["title"].split()) != " ".join((" ".join(oi["S-122"]["title"].split()) + S122_ADD).split()): refuse("S-122's title")
    if before["closed_items"] != after["closed_items"]: refuse("closed items moved")
    top = {k for k in set(before) | set(after) if k not in ("records", "open_items") and before.get(k) != after.get(k)}
    if top != {"needs_document_sha256"}: refuse("top-level fields moved: %s" % top)
    # the envelope pin and ENV-001's verified_sha
    oe = "v2/docs/OPERATING-ENVELOPE.md"
    oldfull = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (BASE, oe)], capture_output=True, check=True).stdout
    oldfull = hashlib.sha256(oldfull).hexdigest()
    newfull = sha_full(oe)
    env = open(ENV, encoding="utf-8").read()
    envy = yaml.safe_load(env)
    if envy.get("document_sha256") != oldfull: refuse("pcb_envelope.yaml does not pin the base's OPERATING-ENVELOPE.md")
    doc_txt = open(os.path.join(L.TOP, oe), encoding="utf-8").read()
    nums = set(re.findall(r"(?<![\w.])[-+]?\d+(?:\.\d+)?(?![\w.])", yaml.safe_dump({k: v for k, v in envy.items() if k not in ("document_sha256", "adopted")})))
    base_txt = subprocess.run(["git", "-C", L.TOP, "show", "%s:%s" % (BASE, oe)], capture_output=True, text=True, check=True).stdout
    lost = sorted(x for x in nums if x.lstrip("+") in base_txt and x.lstrip("+") not in doc_txt)
    if lost: refuse("numbers of the envelope no longer in the document: %s" % lost)
    old_line = next(l for l in env.split("\n") if l.startswith("document_sha256:"))
    new_line = ('document_sha256: "%s"   # re-read and re-pinned 29 September 2026 by stream s122 (S-122: section 4\'s HOT-R1 '
                'sentence, the USB-C row\'s citation dated, the EMCON mode with the PA bias and the RockBLOCK item corrected '
                'to the netlists of sets 12 and 13; no number changed), before it %s' % (newfull, old_line.split("# ", 1)[1] if "# " in old_line else ""))
    env2 = env.replace(old_line, new_line, 1)
    if yaml.safe_load(env2).get("document_sha256") != newfull: refuse("the envelope pin does not read back")
    cov = open(COV, encoding="utf-8").read()
    if cov.count('verified_sha: "%s"' % oldfull) != 1: refuse("ENV-001's verified_sha")
    cov2 = cov.replace('verified_sha: "%s"' % oldfull, 'verified_sha: "%s"' % newfull, 1)
    cov2 = re.sub(r'(verified_on: ")2026-09-27(", verified_by: SESSION, verified_document: "v2/docs/OPERATING-ENVELOPE.md")',
                  r'\g<1>2026-09-29\2', cov2, count=1)
    cb, ca = yaml.safe_load(cov), yaml.safe_load(cov2)
    if cb == ca: refuse("the coverage file did not change")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("the registry re-parse differs")
    open(ENV, "w", encoding="utf-8").write(env2)
    open(COV, "w", encoding="utf-8").write(cov2)
    print("%s: %d records rebound (%s); the needs pin moved; CFL-016 gained the inventory entry and the n1/n2 correction; "
          "S-122's title gained the n3/n4 correction; the envelope and ENV-001 re-pinned to %s" % (
              TAG, len(touched), ", ".join("%s (%s)" % (k, "+".join(v)) for k, v in sorted(touched.items())), newfull[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
