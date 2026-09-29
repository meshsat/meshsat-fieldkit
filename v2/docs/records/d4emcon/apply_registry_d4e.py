#!/usr/bin/env python3
"""Stream d4emcon (MESHSAT-1357): the registry's side of the stream, for the integrator, in two phases that are run at different
times. It writes only v2/ecad/tools/pcb_requirements.yaml, and every sentence it writes is built from what it reads in the tree.

PHASE page (run at the merge of fnd/d4emcon, before rules_status; it does not wait on any regeneration). EMCON.md gained section
4d and three pointer sentences on this branch, so every record bound to EMCON.md by sha256/16 is re-read: one evidence entry per
record, starting with the page's path, naming the sections added and the sections that differ, and saying that no result moves;
each record is rebound from the old sha to the new one. S-01's title gains one restating sentence that ADDS the two findings of
this stream (D4E-F1, D4E-F2) to its open scope and names the drafts, which are not applied; S-92's title gains one sentence
saying that bench E-01 now carries its ground (3). No evidence_result, status or stage changes: nothing here closes.
After it, render the generated pages (rules_render): tests/run.py test_requirements fails its two trace-page tests until
REQUIREMENTS-TRACE.md carries the new entries (tried on this branch: 63 pass, those 2 fail before the render).

PHASE after (run only after the integrator has applied apply_c_d4e_f1.py and apply_b_d4e.py, regenerated boards C and B on the
KiCad box with their chains, and committed the regenerated netlists). It runs tools/readback_d4e.py itself on both committed
netlists and refuses unless every check PASSES; then it writes FEA-002 one evidence entry per board (the read-back's result, the
netlist's sha, and what that closes at desk: SD-EMC-2's back-feed into the RockBLOCK, the E22 and both E72; L4 on U536; D4E-F1;
D4E-F2) and rebinds FEA-002's board B netlist binding to the regenerated file; S-01's title gains a sentence saying which of its
items the read-back closes at desk and which remain (the Iridium 9704's ENABLE document or E-04, S-93, every bench row). FEA-002
stays FEASIBILITY_OPEN and INCONCLUSIVE, its LAYOUT_ENTRY stage OPEN: rows 3 and 4 stay OPEN on desk items and every other row
needs hardware (EMCON.md 4d.1), which the stage's `needs: [DESK, DEVELOPMENT_HARDWARE]` names. S-01 stays OPEN.

Both phases assert: the anchors they edit are present once; the records' old bindings are read from the records; the new text
differs; no claim word (claims_check.CLAIM) is written; the YAML re-parses and only the named records' named fields changed; a
second run is refused (the phase's marker is already in the file).

usage: run from the repository root:  apply_registry_d4e.py page [--dry-run]
                                      apply_registry_d4e.py after [--dry-run]"""
import hashlib, os, re, subprocess, sys
sys.dont_write_bytecode = True

P = "v2/ecad/tools/pcb_requirements.yaml"
PAGE = "v2/docs/feasibility/EMCON.md"
NB = "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net"
NC = "v2/ecad/pcb-c-display-c8/out/pcb-c-display.net"
RB = "v2/docs/records/d4emcon/tools/readback_d4e.py"
MARK_PAGE = "stream d4emcon's section 4d"
MARK_AFTER = "read back by stream d4emcon's readback_d4e.py"


def refuse(msg):
    print("apply_registry_d4e: REFUSED: %s" % msg); sys.exit(1)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def wrap(s, first="         ", rest="          "):
    words = s.split(); lines = []; cur = first
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = rest + w
        else: cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def sections(page):
    out = [["the head", []]]
    for line in page.split("\n"):
        if line.startswith("## ") or line.startswith("### "): out.append([line.lstrip("# ").strip(), []])
        else: out[-1][1].append(line)
    return dict((h, "\n".join(b)) for h, b in out), [h for h, _ in out]


def add_entry(out, rid, note, old_bind=None, new_bind=None):
    i, j = rec_span(out, rid); r = out[i:j]
    r2 = r
    if old_bind:
        if r2.count('"%s"' % old_bind) != 1: refuse("%s does not carry the binding %s once" % (rid, old_bind))
        r2 = r2.replace('"%s"' % old_bind, '"%s"' % new_bind)
    k = r2.index("    evidence_bound_to:")
    r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
    return out[:i] + r2 + out[j:]


def restate_title(out, rid, sentence):
    i, j = rec_span(out, rid); r = out[i:j]
    m = re.search(r"(?m)^    title: >-\n((?:      .*\n)+)", r)
    if not m: refuse("%s has no folded title" % rid)
    r2 = r[:m.end(1)] + wrap(sentence, first="     ", rest="      ") + r[m.end(1):]   # appended lines; the folded title reads old + " " + sentence
    return out[:i] + r2 + out[j:]


def check_and_write(t, out, moved_expect, dry):
    import yaml
    sys.path.insert(0, "v2/ecad/tools")
    import claims_check as _cc
    A, B = yaml.safe_load(t), yaml.safe_load(out)
    LISTS = ("records", "open_items")
    ra = {r["id"]: r for L in LISTS for r in A[L]}; rb = {r["id"]: r for L in LISTS for r in B[L]}
    for L in LISTS:
        if [r["id"] for r in A[L]] != [r["id"] for r in B[L]]: refuse("the %s list changed" % L)
    if {k: v for k, v in A.items() if k not in LISTS} != {k: v for k, v in B.items() if k not in LISTS}: refuse("something outside the records and open items changed")
    moved = sorted(k for k in ra if ra[k] != rb[k])
    if moved != sorted(moved_expect): refuse("records changed: %s, expected %s" % (moved, sorted(moved_expect)))
    for k in moved:
        keys = sorted(f for f in set(ra[k]) | set(rb[k]) if ra[k].get(f) != rb[k].get(f))
        if not set(keys) <= {"evidence", "evidence_bound_to", "title"}: refuse("%s: fields changed: %s" % (k, keys))
        for f in ("evidence_result", "status"):
            if ra[k].get(f) != rb[k].get(f): refuse("%s: %s changed" % (k, f))
        new_txt = [e for e in (rb[k].get("evidence") or []) if e not in (ra[k].get("evidence") or [])]
        if "title" in keys: new_txt.append(rb[k]["title"][len(ra[k]["title"]):])
        for e in new_txt:
            hit = _cc.CLAIM.search(str(e))
            if hit: refuse("%s: the new text carries the claim word %r" % (k, hit.group(0)))
    if dry:
        print("apply_registry_d4e: dry run, every check holds; records that would change: %s" % ", ".join(moved)); return
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != B: refuse("the file written does not re-parse to what was checked")
    print("apply_registry_d4e: written; records changed: %s" % ", ".join(moved))


def phase_page(dry):
    t = open(P, encoding="utf-8").read()
    if MARK_PAGE in " ".join(t.split()): refuse("the page phase has run already (%r is in the registry)" % MARK_PAGE)
    olds = sorted(set(re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(PAGE), t)))
    if len(olds) != 1: refuse("the records are bound to %d different EMCON.md files: %s" % (len(olds), olds))
    OLD = olds[0]
    new_page = open(PAGE, encoding="utf-8").read(); NEW = sha16(new_page.encode("utf-8"))
    if NEW == OLD: refuse("the tree's EMCON.md is the file the records are bound to: nothing to rebind")
    old_page = None
    for rev in subprocess.run(["git", "rev-list", "--max-count=60", "HEAD", "--", PAGE], capture_output=True, text=True).stdout.split():
        cand = subprocess.run(["git", "show", "%s:%s" % (rev, PAGE)], capture_output=True, text=True).stdout
        if sha16(cand.encode("utf-8")) == OLD: old_page = cand; break
    if old_page is None: refuse("no commit in the last 60 that touched EMCON.md carries the bound file %s" % OLD)
    so, ho = sections(old_page); sn, hn = sections(new_page)
    added = [h for h in hn if h not in so]
    gone = [h for h in ho if h not in sn]
    if gone: refuse("sections removed: %s" % gone)
    differ = [h for h in ho if so[h] != sn[h]]
    if not any(h.startswith("4d.") for h in added): refuse("section 4d is not among the added sections: %s" % added)
    rids = [m.group(1) for m in re.finditer(r"(?m)^  - id: (\S+)\n", t) if '"%s@%s"' % (PAGE, OLD) in t[slice(*rec_span(t, m.group(1)))]]
    note = ("%s re-read at the merge of stream d4emcon (29 September 2026, MESHSAT-1357; %s, the file at %s before): %d "
            "section(s) added (%s) and %d of the %d earlier sections differ (%s), the rest byte-identical. The added section "
            "marks FEA-002's layout-entry stage row by row on the set 10 netlists (CLOSED AT DESK 0, OPEN 15, NEEDS HARDWARE 2 of "
            "17), completes SD-EMC-2's back-feed census and names two findings (D4E-F1, board C's U9 in its supply band; D4E-F2, "
            "the Tpr hold's level on board B) with their drafts, which are not applied, regenerated or read back; no row closes "
            "and no reading this record rests on moves, so its result is unchanged, bound to the file at %s."
            % (PAGE, MARK_PAGE, OLD, len(added), "; ".join(added), len(differ), len(ho), "; ".join(differ) or "none", NEW))
    out = t
    for rid in rids:
        out = add_entry(out, rid, note, "%s@%s" % (PAGE, OLD), "%s@%s" % (PAGE, NEW))
    s01 = ("Found by stream d4emcon (29 September 2026, EMCON.md 4d) and added to this item: D4E-F1, board C's U9 in its 0 to "
           "1.65 V supply band drives EMCON_HW to a level board B's readers cannot be shown to read LOW (draft "
           "v2/docs/records/d4emcon/apply_c_d4e_f1.py); D4E-F2, U221's Tpr hold on FULL_CARD_POWER_OFF# is not shown under "
           "Quectel's 0.2 V (draft B-5 of apply_b_d4e.py); the back-feed of SD-EMC-2 into the RockBLOCK, the E22 and both E72 and "
           "L4 on U536 are drafted as B-1 to B-4 of the same script; none is applied, regenerated or read back.")
    out = restate_title(out, "S-01", s01)
    if "d4emcon" not in open(PAGE, encoding="utf-8").read().split("| E-01 |", 1)[1].split("\n", 1)[0]:
        refuse("bench E-01 on the page does not carry stream d4emcon's addition (U13's off-state current)")
    s92 = ("Advanced by stream d4emcon (29 September 2026): bench E-01 of v2/docs/feasibility/EMCON.md section 6 now records "
           "U13 pin 4's off-state current while powered and released, ground (3) of this item, beside pin 5's threshold and input "
           "current, grounds (1) and (2); the item stays open until RF-002, re-taken on board D, reads the row decided.")
    out = restate_title(out, "S-92", s92)
    check_and_write(t, out, rids + ["S-01", "S-92"], dry)
    print("apply_registry_d4e: page %s -> %s; %d records rebound: %s" % (OLD, NEW, len(rids), ", ".join(rids)))


def phase_after(dry):
    t = open(P, encoding="utf-8").read()
    flat = " ".join(t.split())
    if MARK_PAGE not in flat: refuse("run the page phase first")
    if MARK_AFTER in flat: refuse("the after phase has run already")
    res = {}
    for board, net in (("B", NB), ("C", NC)):
        r = subprocess.run([sys.executable, RB, "--tools", "v2/ecad/tools", "--board", board, net], capture_output=True, text=True)
        if r.returncode != 0 or "RESULT: every check holds" not in r.stdout:
            refuse("the read-back of board %s does not hold on %s:\n%s" % (board, net, r.stdout[-1500:]))
        n = sum(1 for l in r.stdout.splitlines() if l.startswith("PASS"))
        res[board] = (n, sha16(open(net, "rb").read()))
    i, j = rec_span(t, "FEA-002")
    m = re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(NB), t[i:j])
    if len(m) != 1: refuse("FEA-002 carries %d binding(s) to board B's netlist, one expected" % len(m))
    OLDB = m[0]
    if OLDB == res["B"][1]: refuse("board B's netlist is the file FEA-002 is bound to: was board B regenerated?")
    nb = ("%s regenerated with stream d4emcon's draft apply_b_d4e.py (B-1 to B-5) and %s (tools/readback_d4e.py --board B): "
          "%d checks PASS on the file at %s, every node the draft makes present and every direct line it removes absent. At desk "
          "this closes on board B: SD-EMC-2's back-feed into the RockBLOCK 9704 (its inputs only while RB_GO, its outputs pulled "
          "down), both E72 (open drains pulled up to the gated rail, the rail bled to 0.56 V worst) and the E22 (every line gated or "
          "buffered on slot 3's own rail); L4 case (2) on U536 (U543 holds RB_IEN in the band); D4E-F2 (U554 holds the Tpr pin "
          "under 0.2 V). Rows 3 and 4 stay OPEN on desk items (S-93; the Iridium 9704's ENABLE document) and every other row needs "
          "hardware (EMCON.md 4d.1), so the stage stays OPEN and the result INCONCLUSIVE; the file at %s before."
          % (NB, MARK_AFTER, res["B"][0], res["B"][1], OLDB))
    nc = ("%s regenerated with stream d4emcon's draft apply_c_d4e_f1.py and %s (tools/readback_d4e.py --board C): %d checks PASS "
          "on the file at %s (U9 on EMCON_HW_DRV, R52 to EMCON_HW, D23 from EMCON_HW to TX_INHIBIT_n), which closes D4E-F1 at "
          "desk: EMCON_HW sits at most one Schottky drop above TX_INHIBIT_n whatever board C's +3V3 does. The result is unchanged."
          % (NC, MARK_AFTER, res["C"][0], res["C"][1]))
    out = add_entry(t, "FEA-002", nb, "%s@%s" % (NB, OLDB), "%s@%s" % (NB, res["B"][1]))
    out = add_entry(out, "FEA-002", nc)
    s01 = ("Read back by stream d4emcon's read-back on the regenerated netlists (board B at %s, board C at %s): D4E-F1, D4E-F2, "
           "L4 on U536 and SD-EMC-2's back-feed into the RockBLOCK, the E22 and both E72 are drawn and closed at desk; what stays "
           "in this item is the Iridium 9704's response to its ENABLE (a maker's document owed, or bench E-04) and every bench row."
           % (res["B"][1], res["C"][1]))
    out = restate_title(out, "S-01", s01)
    check_and_write(t, out, ["FEA-002", "S-01"], dry)


def main(argv):
    if not os.path.exists(P) or not os.path.exists(PAGE): refuse("run from the repository root")
    if not argv or argv[0] not in ("page", "after"): print(__doc__); return 2
    dry = "--dry-run" in argv[1:]
    (phase_page if argv[0] == "page" else phase_after)(dry)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
