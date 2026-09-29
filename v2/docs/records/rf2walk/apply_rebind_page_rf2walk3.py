#!/usr/bin/env python3
"""Stream rf2walk3 (MESHSAT-1357): the records bound to v2/docs/feasibility/EMCON.md, rebound to the page after this stream
added three items to section 4d.6 (the re-check of set 12: the declared toggle, B-4's margin and start-up case, the LED feed
loads) and one sentence to bench E-04. It writes only
v2/ecad/tools/pcb_requirements.yaml and uses the helpers of stream d4emcon's apply_registry_d4e.py (same folder layout; its
refusals and its YAML check: only the named records' evidence and bindings change, no result, status or title, no claim word).
Every record carrying the old binding gains one evidence entry that starts with the page's path, names the sections added and
those that differ (read from the two files, not typed), says that no result moves, and is rebound to the new sha. Run from the
repository root at the merge of fnd/rf2walk3, before rules_status; render the generated pages after it. A second run is refused.

usage: apply_rebind_page_rf2walk3.py [--dry-run]"""
import os, re, subprocess, sys
sys.dont_write_bytecode = True
sys.path.insert(0, "v2/docs/records/d4emcon")
import apply_registry_d4e as R   # refuse, sha16, rec_span, sections, add_entry, check_and_write, P, PAGE

MARK = "stream rf2walk3's items in section 4d.6"


def main(argv):
    dry = "--dry-run" in argv
    if not os.path.exists(R.P) or not os.path.exists(R.PAGE): R.refuse("run from the repository root")
    t = open(R.P, encoding="utf-8").read()
    if MARK in " ".join(t.split()): R.refuse("this rebind has run already (%r is in the registry)" % MARK)
    olds = sorted(set(re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(R.PAGE), t)))
    if len(olds) != 1: R.refuse("the records are bound to %d different EMCON.md files: %s" % (len(olds), olds))
    OLD = olds[0]
    new_page = open(R.PAGE, encoding="utf-8").read(); NEW = R.sha16(new_page.encode("utf-8"))
    if NEW == OLD: R.refuse("the tree's EMCON.md is the file the records are bound to: nothing to rebind")
    old_page = None
    for rev in subprocess.run(["git", "rev-list", "--max-count=80", "HEAD", "--", R.PAGE], capture_output=True, text=True).stdout.split():
        cand = subprocess.run(["git", "show", "%s:%s" % (rev, R.PAGE)], capture_output=True, text=True).stdout
        if R.sha16(cand.encode("utf-8")) == OLD: old_page = cand; break
    if old_page is None: R.refuse("no commit in the last 80 that touched EMCON.md carries the bound file %s" % OLD)
    so, ho = R.sections(old_page); sn, hn = R.sections(new_page)
    added = [h for h in hn if h not in so]
    if [h for h in ho if h not in sn]: R.refuse("sections removed")
    differ = [h for h in ho if so[h] != sn[h]]
    if not any(h.startswith("4d.6") for h in added + differ):
        R.refuse("section 4d.6 is neither added nor changed: added %s, changed %s" % (added, differ))
    rids = [m.group(1) for m in re.finditer(r"(?m)^  - id: (\S+)\n", t) if '"%s@%s"' % (R.PAGE, OLD) in t[slice(*R.rec_span(t, m.group(1)))]]
    note = ("%s re-read at the merge of %s (29 September 2026, MESHSAT-1357; the file at %s before): %d section(s) added (%s) "
            "and %d of the %d earlier sections differ (%s), the rest byte-identical. Section 4d.6 gains the re-check of set 12's "
            "items: RF-002's walk takes the line's source only from the declared toggle (board C's SW_EMCON), B-4's margin with "
            "every rail lost stated (30 mV) and its start-up case, and the LED feed loads drafted as a follow-up; bench E-04 "
            "gains the start-up dip. No row closes and no reading this record rests on moves, so its result is "
            "unchanged, bound to the file at %s."
            % (R.PAGE, MARK, OLD, len(added), "; ".join(added), len(differ), len(ho), "; ".join(differ) or "none", NEW))
    out = t
    for rid in rids:
        out = R.add_entry(out, rid, note, "%s@%s" % (R.PAGE, OLD), "%s@%s" % (R.PAGE, NEW))
    R.check_and_write(t, out, rids, dry)
    print("apply_rebind_page_rf2walk3: page %s -> %s; %d records rebound: %s" % (OLD, NEW, len(rids), ", ".join(rids)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
