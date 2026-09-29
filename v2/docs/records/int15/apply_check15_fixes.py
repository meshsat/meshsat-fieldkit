#!/usr/bin/env python3
"""The integrator's answers to the integration check of set 14 (MESHSAT-1357, 29 September 2026; `checks/check-int15-1.md`).
S-122's closure (1f3dd306) was premature: the check found CFL-016 would read PASS while five sentences in its scope name
parts no generator carries, sentences S-122's inventory never read because it reads designators, nets and boards, not
makers' part numbers (B1); and CFL-016 not bound to three files its reading rests on (B2). The branch was rewound to
9eaf406f, before the closure, so S-122 stays open and CFL-016 stays FAIL. This script:
  B1  appends to CFL-016 an entry that corrects the inventory entry's "names a part" and names the five sentences in the
      check's own words; extends S-122 with them, with part numbers in its inventory, and with what its closure owes;
  B2  binds CFL-016 to handover/DEFINITION-STATUS.md, feasibility/EMCON.md and ASSEMBLY.md at their current sha;
  m5  files stream s120's four checks under records/s120/checks/ and adds the records index rows for s120/ and s122/;
  m4, m7  carried into S-122's extension; m1, m2, m6, m8 carried in this directory's README.
Every other record and item is asserted unchanged; the registry re-parses. Refuses a second run. Run: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A

TAG = "apply_check15_fixes"
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
BIND = ("v2/docs/handover/DEFINITION-STATUS.md", "v2/docs/feasibility/EMCON.md", "v2/docs/ASSEMBLY.md")
SCRATCH = os.path.join(os.path.expanduser("~"), "worktrees", "meshsat-fieldkit", "_scratch")
DASHES = ("\u2014", "\u2013")


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m)); sys.exit(2)


def sha16(rel): return hashlib.sha256(open(os.path.join(TOP, rel), "rb").read()).hexdigest()[:16]


def scrub(t):
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*?/_scratch/", "<scratch>/", t)
    t = re.sub(r"(?<![<\w/])_scratch/", "<scratch>/", t)
    t = re.sub(r"/(?:home|root|tmp)/[^\s`)]*", "<local path>", t)
    return t.replace("`claude-runner`", "the runner's account name").replace("claude-runner", "the runner's account")


ENTRY = (
    "v2/docs/records/int15/checks/check-int15-1.md (the integration check of set 14, blocking B1 and B2; answered by "
    "v2/docs/records/int15/apply_check15_fixes.py): stream s122's inventory entry above describes the inventory as reading "
    "every sentence that names a part; in the check's words the finder reads designators, nets and board names, not makers' "
    "part numbers, so that entry overstates it. The check names five sentences in this record's scope that name parts no "
    "generator carries: V2-SPEC.md line 82 (the TMDS341A display switch, where board B carries two TS3DV642, U3 and U4), "
    "line 86 (the LM5176 front end on the E6 dock strip, which is board A's U2, board E carrying the LM5069 U6) and line 47 "
    "(the WM8960 codec, where board D's codec is the PCM2912A U6), and OPERATING-ENVELOPE.md line 77 (a TRACO TEN 40 "
    "converter, on no netlist) and line 83 (an Amphenol M.2 B-key socket, where the socket is TE 2199119-3). S-122's closure "
    "at 1f3dd306 was therefore premature and is not on this line; this record reads FAIL and waits on S-122, extended with "
    "these sentences. Its reading also rests on v2/docs/handover/DEFINITION-STATUS.md (rows DC-01 to DC-09), "
    "v2/docs/feasibility/EMCON.md section 0a.1 and v2/docs/ASSEMBLY.md, which it is bound to here (%s).")
S122_ADD = (
    "Extended at integration set 14 (v2/docs/records/int15/checks/check-int15-1.md): the inventory reads makers' part "
    "numbers as well as designators, nets and board names; the five sentences named in CFL-016's set 14 entry (V2-SPEC.md "
    "lines 47, 82 and 86, OPERATING-ENVELOPE.md lines 77 and 83) are judged against the netlists and corrected, or dated "
    "where the document states their date; CFL-016 is re-read with handover/DEFINITION-STATUS.md, feasibility/EMCON.md and "
    "ASSEMBLY.md among its bound files; and the closure answers check-s122-3's three minors (CONOPS.md line 1056's D-13 row, "
    "the absent rule's four key words, the README's CON-003 quote) and check-int15-1's m7 (CFL-016's acceptance read "
    "literally against the baseline rule). S-122 closes only then.")


def main():
    reg = open(REG, encoding="utf-8").read()
    if TAG in reg: refuse("already applied")
    before = yaml.safe_load(reg)
    r = [x for x in before["records"] if x["id"] == "CFL-016"][0]
    if (r.get("evidence_result"), r.get("waits_on")) != ("FAIL", ["S-122"]): refuse("CFL-016 is not FAIL on S-122")
    if "S-122" not in {x["id"] for x in before["open_items"]}: refuse("S-122 is not open")
    if "names a part" not in " ".join(str(r["evidence"][-3]).split()): refuse("the inventory entry's phrase is not where the check read it")
    binds = ["%s@%s" % (p, sha16(p)) for p in BIND]
    if any(b.split("@")[0] in " ".join(r.get("evidence_bound_to") or []) for b in binds): refuse("CFL-016 already binds one of the three")
    entry = ENTRY % ", ".join(b.split("@")[1] for b in binds)
    for t in (entry, S122_ADD):
        A.screen(t, TAG)
        if any(d in t for d in DASHES): refuse("a dash")
    # the filed check first: the entry cites it
    src = os.path.join(SCRATCH, "chk-int15", "CHECK.md")
    c = scrub(open(src, encoding="utf-8").read())
    if not c.startswith("mergeable: no") or re.search(r"/(home|root|tmp)/|claude-runner", c): refuse("the check's text")
    open(os.path.join(HERE, "checks", "check-int15-1.md"), "w", encoding="utf-8").write(c)
    out = reg
    i, j = A.span(out, "CFL-016")
    t = out[i:j]
    m = re.search(r"(?m)^    evidence:\n", t)
    tail = t[m.end():]
    k = re.search(r"(?m)^    [a-z_]+:", tail)
    end = m.end() + (k.start() if k else len(tail))
    t = t[:end] + "      - >-\n" + A.fold(entry, 10, 120) + t[end:]
    m2 = re.search(r"(?m)^    evidence_bound_to:\n((?:      - .*\n)+)", t)
    if not m2: refuse("CFL-016's evidence_bound_to block")
    t = t[:m2.end()] + "".join('      - "%s"\n' % b for b in binds) + t[m2.end():]
    out = out[:i] + t + out[j:]
    i, j = A.span(out, "S-122")
    t = out[i:j]
    m3 = re.search(r"(?m)^    title: >-\n((?:      .*\n)+)", t)
    t = t[:m3.end()] + A.fold(S122_ADD, 6, 120) + t[m3.end():]
    out = out[:i] + t + out[j:]
    after = yaml.safe_load(out)
    ob, ab = {x["id"]: x for x in before["records"]}, {x["id"]: x for x in after["records"]}
    for rid in ob:
        dd = {f for f in set(ob[rid]) | set(ab[rid]) if ob[rid].get(f) != ab[rid].get(f)}
        if (rid == "CFL-016" and dd != {"evidence", "evidence_bound_to"}) or (rid != "CFL-016" and dd): refuse("%s: %s" % (rid, dd))
    if set(ab["CFL-016"]["evidence_bound_to"]) - set(ob["CFL-016"]["evidence_bound_to"]) != set(binds): refuse("the bindings added")
    oi, ai = {x["id"]: x for x in before["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(oi) != set(ai) or any(oi[x] != ai[x] for x in oi if x != "S-122"): refuse("open items moved")
    if " ".join(ai["S-122"]["title"].split()) != " ".join((oi["S-122"]["title"] + " " + S122_ADD).split()): refuse("S-122's title")
    if before["closed_items"] != after["closed_items"]: refuse("closed items moved")
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    # m5: stream s120's checks filed, the records index rows
    os.makedirs(os.path.join(TOP, "v2/docs/records/s120/checks"), exist_ok=True)
    for n, src in ((1, "CHECK.md"), (2, "CHECK-2.md"), (3, "CHECK-3.md"), (4, "CHECK-4.md")):
        s = scrub(open(os.path.join(SCRATCH, "chk-s120", src), encoding="utf-8").read())
        if re.search(r"/(home|root|tmp)/|claude-runner", s): refuse("chk-s120/%s holds a local path" % src)
        open(os.path.join(TOP, "v2/docs/records/s120/checks/check-s120-%d.md" % n), "w", encoding="utf-8").write(s)
    rp = os.path.join(TOP, "v2/docs/records/README.md")
    rt = open(rp, encoding="utf-8").read()
    anchor = "| `s119/` | stream s119"
    if rt.count(anchor) != 1 or "| `s120/` |" in rt or "| `s122/` |" in rt: refuse("the records index")
    rows = ("| `s120/` | stream s120 (29 September 2026, branch `fnd/s120`, four rounds, checked four times: `checks/`): board A's charge bus VBUS20 bounded at 23.40 V (INFERRED, the front end's typical 10 percent over-voltage trip) against the 30 V charger FETs of decision 57; S-120 closed and S-124 opened for the switch nodes, closed only on the prototype |\n"
            "| `s122/` | stream s122 (29 September 2026, branches `fnd/s122` and `fnd/s122b`, three rounds, checked three times: `checks/`): the documents CFL-016 names re-read against the netlists by an inventory and verdict script, stale sentences corrected, CONOPS restored to its baseline text with its current values on the status page; S-122 open until part numbers are inventoried (set 14's check) |\n")
    open(rp, "w", encoding="utf-8").write(rt.replace(anchor, rows + anchor, 1))
    print("%s: CFL-016 corrected and bound to the three files (FAIL on S-122); S-122 extended; check-int15-1 and s120's four checks filed; the index rows added" % TAG)
    return 0


if __name__ == "__main__":
    sys.exit(main())
