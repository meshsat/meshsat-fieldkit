#!/usr/bin/env python3
"""apply_set28_rebind.py: L5-F02 (MESHSAT-1357, set 28, 3 October 2026; the pattern of records/retake6/apply_rebind_current_evidence.py
and records/int7/apply_rebind_final_page.py). Five readings of the requirements registry (CFL-001, CFL-005, CFL-014, CFL-015,
CFL-016) are bound to v2/docs/PANEL.md by sha256/16, and Layer 5's power pass (records/l5pwr, applying L4-E11's finding E11-03) restated
section 10's charge-hold sentences, so `rules_lib.py requirements` reads five errors ("re-read it before it decides"). This script
re-reads each record's ground on the new page, writes one evidence entry per record that starts with the file's path, names the
sections that differ and the ones that are byte-identical, quotes the sentences replaced and the sentences written, states what the
record rests on and whether that text moved, and rebinds the record to the new page. It changes no evidence_result, no status and no
other record. The sha it binds is READ from the tree at run time; the old binding is read from the records; the old page is found in
the branch's history by that sha, so the coordinator re-runs it after re-basing onto set 27.

Asserted before writing (a claim in an entry is read from the tree, never typed): every record carries exactly one binding to the page
and all five carry the same one (OLD); the tree's page is not OLD (a second run is refused as already applied); a commit in the history
of PANEL.md carries the page at OLD; the two pages carry the same headings and exactly one section differs, section 10; the sentences
each record rests on (named below) are byte-identical between the pages or in a byte-identical section; no entry carries a word the
ENV-002 claims screen counts (claims_check.CLAIM, since REQUIREMENTS-TRACE.md prints every entry). After writing it re-parses the file
with PyYAML and asserts that only the five records changed, each by one evidence entry and the one binding, then re-reads the file.

Usage, from anywhere:  apply_set28_rebind.py [--check | --write]
  --check (default) prints the entries it would write and writes nothing. Exit 0 written or checked; 3 refused.
Afterwards: `env -C v2/ecad/tools python3 rules_lib.py requirements` reads 0 errors, `rules_render.py --requirements` re-renders
v2/docs/REQUIREMENTS-TRACE.md (it prints the entries), and apply_set28_repins.py re-pins pcb_requirements.yaml in L4-E9 and L4-E11."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = "v2/ecad/tools/pcb_requirements.yaml"
PAGE = "v2/docs/PANEL.md"
RECORDS = ("CFL-001", "CFL-005", "CFL-014", "CFL-015", "CFL-016")
# The ground each record's reading rests on, as its own evidence entries name it (sections by heading number; sentences by text).
GROUND = {
    "CFL-001": {"sections": ("1.", "2."), "why": "line 5 (bank 1's home and failover hosts), section 1 and section 2's ribbon table with its pin 15 row"},
    "CFL-005": {"sections": ("7.",), "why": "section 7 (EMCON_HW's pull and the panel-less kit)"},
    "CFL-014": {"sentences": ("the charger's cell-count strap is `R26` 13.3k over `R27` 40.2k, 75.1 % of VDDA, inside the BQ25731's 4S window",
                              "the kit's loads sit on the charger's system node VSYS (the net `VBAT`), with the pack beyond the charge shunt `R17` and the 25 A blade `F1`",
                              "whether the charger charges before any host write is a bench question (TBD)"),
                "why": "section 10's strap, VSYS and bench-question sentences"},
    "CFL-015": {"sentences": ("both ends of the pack's SMBus lead are the same JST-XH 1x4 in the pack board's order (1 SMBC, 2 SMBD, 3 the pack's own negative lead, 4 PRES), so a straight four-way lead mates them, and `check_contracts.py` checks the lead as a cross-board contract (ASSEMBLY.md section 4)",),
                "why": "section 10's pack SMBus lead sentences"},
    "CFL-016": {"sections": ("1.", "6.", "7."), "why": "sections 1, 6 and 7 (the radios' EMCON path, the toggles, the bus table)"},
}


def refuse(msg):
    print("apply_set28_rebind: REFUSED: %s" % msg)
    sys.exit(3)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def text(rel):
    return open(os.path.join(TOP, rel), encoding="utf-8").read()


def sections(page):
    """[(heading, body)] on the page's own '## ' headings; the text before the first is 'the head'."""
    out = [["the head", []]]
    for line in page.split("\n"):
        if line.startswith("## "):
            out.append([line[3:].strip(), []])
        else:
            out[-1][1].append(line)
    return [(h, "\n".join(b)) for h, b in out]


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1
    j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def wrap(s):
    words, lines, cur = s.split(), [], "         "
    for w in words:
        if len(cur) + 1 + len(w) > 120:
            lines.append(cur); cur = "          " + w
        else:
            cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def changed_sentences(old, new):
    """The replaced and the written text of one changed paragraph, widened to sentence boundaries."""
    pre = 0
    while pre < min(len(old), len(new)) and old[pre] == new[pre]:
        pre += 1
    suf = 0
    while suf < min(len(old), len(new)) - pre and old[-1 - suf] == new[-1 - suf]:
        suf += 1
    start = max(old.rfind(". ", 0, pre) + 2, 0)
    e_old = old.find(". ", len(old) - suf)
    e_new = new.find(". ", len(new) - suf)
    e_old = len(old) if e_old < 0 else e_old + 1
    e_new = len(new) if e_new < 0 else e_new + 1
    return old[start:e_old].strip(), new[start:e_new].strip()


def old_page_at(old16):
    log = subprocess.run(["git", "log", "--format=%H", "-n", "400", "--", PAGE], cwd=TOP, capture_output=True, text=True, check=True).stdout.split()
    for c in log:
        r = subprocess.run(["git", "show", "%s:%s" % (c, PAGE)], cwd=TOP, capture_output=True)
        if r.returncode == 0 and sha16(r.stdout) == old16:
            return r.stdout.decode("utf-8"), c[:8]
    refuse("no commit in the history of %s carries the page at %s" % (PAGE, old16))


def main(argv):
    mode = "--write" if "--write" in argv else "--check"
    t = text(P)
    new_page = text(PAGE)
    new = sha16(new_page.encode("utf-8"))
    olds = set()
    for rid in RECORDS:
        i, j = rec_span(t, rid)
        m = re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(PAGE), t[i:j])
        if len(m) != 1:
            refuse("%s carries %d binding(s) to %s, one expected" % (rid, len(m), PAGE))
        olds.add(m[0])
    if len(olds) != 1:
        refuse("the five records are bound to different pages: %s" % sorted(olds))
    old = olds.pop()
    if old == new:
        refuse("already applied: the five records are bound to the tree's %s (%s)" % (PAGE, new))
    old_page, old_commit = old_page_at(old)

    so, sn = sections(old_page), sections(new_page)
    if [h for h, _ in so] != [h for h, _ in sn]:
        refuse("the two pages do not carry the same headings")
    differ = [h for (h, a), (_, b) in zip(so, sn) if a != b]
    same = [h for (h, a), (_, b) in zip(so, sn) if a == b]
    if len(differ) != 1 or not differ[0].startswith("10."):
        refuse("the sections that differ are %s; this script's entries are written for a change in section 10 alone" % differ)
    body_old = dict(so)[differ[0]]
    body_new = dict(sn)[differ[0]]
    removed, written = changed_sentences(" ".join(body_old.split()), " ".join(body_new.split()))
    if not removed or not written:
        refuse("the changed span of section 10 could not be delimited")
    head = lambda h: h.split(" ")[0]
    for rid, g in GROUND.items():
        for s in g.get("sections", ()):
            if s not in [head(h) for h in same]:
                refuse("%s rests on section %s, which is not byte-identical between the pages" % (rid, s))
        for s in g.get("sentences", ()):
            if s not in body_old or s not in body_new:
                refuse("%s rests on a sentence that is not in both pages' section 10: %r" % (rid, s[:60]))

    how = ("%s re-read at the set 28 integration of 3 October 2026 (MESHSAT-1357, branch fnd/int28: Layer 5's power pass, "
           "records/l5pwr, applied by apply_l5pwr.py as L4-E11's finding E11-03 asked; the file before at %s, the page of %s). Of the "
           "page's %d sections (the head and the numbered sections) %d differs, %s, and %d are byte-identical (%s). In section 10 the "
           "text replaced is: '%s' and the text written is: '%s'. The sentences before and after that span are byte-identical."
           % (PAGE, old, old_commit, len(sn), len(differ), differ[0], len(same), "; ".join(head(h) for h in same if h != "the head"),
              removed, written))
    tail = {
        "CFL-001": (" This reading rests on %s; sections 1 and 2 are byte-identical, so the ground it was decided on is unchanged. "
                    "This entry rebinds the page and re-decides nothing: the result stands as set, bound to the file at %s."),
        "CFL-005": (" This reading rests on %s; section 7 is byte-identical, so the ground it was decided on is unchanged. This entry "
                    "rebinds the page and re-decides nothing: the result stands as set, bound to the file at %s."),
        "CFL-014": (" This reading rests on %s; each of those sentences is byte-identical in the new section 10, and the sentences "
                    "written name the firmware's charge holds (FW-A19's flag, the charger's CHRG_INHIBIT bit) and when SHORE_INHIBIT "
                    "is asserted, not the strap, the load node or the hostless charge that this record decided. This entry rebinds the "
                    "page and re-decides nothing: the result stands as set, bound to the file at %s."),
        "CFL-015": (" This reading rests on %s; those sentences are byte-identical in the new section 10 (the change is the charge-hold "
                    "span alone). This entry rebinds the page and re-decides nothing: the result stands as set, bound to the file at %s."),
        "CFL-016": (" This reading rests on %s, all byte-identical. Section 10 is in the sentence scope of stream s122, whose check "
                    "this record cites: the sentences written describe the firmware's hold policy over lines the drawn boards carry "
                    "(CHG_INHIBIT, SHORE_INHIBIT) and FW-A19's flag, and name L4-E11 7a's rule; whether they describe the circuit the "
                    "generators carry is that check's question at its next run, not this entry's. This entry rebinds the page and "
                    "re-decides nothing: the result stands as set, bound to the file at %s."),
    }
    notes = {rid: how + tail[rid] % (GROUND[rid]["why"], new) for rid in RECORDS}

    sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
    import claims_check as _cc
    out = t
    for rid in RECORDS:
        note = notes[rid]
        if not note.startswith(PAGE):
            refuse("the entry for %s does not start with the file's path" % rid)
        hit = _cc.CLAIM.search(note)
        if hit:
            refuse("the entry for %s carries the claim word %r, which the ENV-002 screen would count on the trace page" % (rid, hit.group(0)))
        for ch in ("\u2014", "\u2013"):
            if ch in note:
                refuse("the entry for %s carries a dash" % rid)
        i, j = rec_span(out, rid)
        r = out[i:j]
        res0 = re.search(r"(?m)^    evidence_result: (\S+)", r).group(1)
        r2 = r.replace('"%s@%s"' % (PAGE, old), '"%s@%s"' % (PAGE, new))
        k = r2.index("    evidence_bound_to:")
        r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
        assert r2 != r and re.search(r"(?m)^    evidence_result: (\S+)", r2).group(1) == res0
        out = out[:i] + r2 + out[j:]
    if out == t:
        refuse("the new text does not differ from the old")

    import yaml
    A, B = yaml.safe_load(t), yaml.safe_load(out)
    ra = {r["id"]: r for r in A["records"]}
    rb = {r["id"]: r for r in B["records"]}
    if list(ra) != list(rb):
        refuse("the record list changed")
    if {k: v for k, v in A.items() if k != "records"} != {k: v for k, v in B.items() if k != "records"}:
        refuse("something outside the records changed")
    moved = [k for k in ra if ra[k] != rb[k]]
    if sorted(moved) != sorted(RECORDS):
        refuse("records changed: %s" % moved)
    for k in moved:
        x, y = ra[k], rb[k]
        keys = [f for f in set(x) | set(y) if x.get(f) != y.get(f)]
        if sorted(keys) != ["evidence", "evidence_bound_to"]:
            refuse("%s: fields changed: %s" % (k, keys))
        if y["evidence"][:-1] != x["evidence"] or not str(y["evidence"][-1]).startswith(PAGE):
            refuse("%s: the evidence list is not the old list plus one entry that starts with the path" % k)
        if sorted(set(x["evidence_bound_to"]) ^ set(y["evidence_bound_to"])) != sorted(["%s@%s" % (PAGE, old), "%s@%s" % (PAGE, new)]):
            refuse("%s: the bindings changed by more than the page's" % k)
    if mode == "--check":
        print("apply_set28_rebind: --check, nothing written; --write would rebind %s from %s to %s (the page of %s) with these entries:"
              % (", ".join(RECORDS), old, new, old_commit))
        for rid in RECORDS:
            print("--- %s (evidence_result %s unchanged)\n%s" % (rid, rb[rid]["evidence_result"], notes[rid]))
        return 0
    with open(os.path.join(TOP, P), "w", encoding="utf-8") as fh:
        fh.write(out)
    if yaml.safe_load(text(P)) != B:
        refuse("the file written does not re-parse to what was checked")
    for k in RECORDS:
        print("apply_set28_rebind: %s rebound from %s to %s, evidence_result %s unchanged" % (k, old, new, rb[k]["evidence_result"]))
    print("apply_set28_rebind: the section that differs: %s; byte-identical: %s" % (differ[0], "; ".join(head(h) for h in same if h != "the head")))
    print("apply_set28_rebind: next: rules_lib.py requirements (0 errors), rules_render.py --requirements, apply_set28_repins.py --write")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
