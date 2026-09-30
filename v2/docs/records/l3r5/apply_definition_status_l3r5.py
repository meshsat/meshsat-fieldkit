#!/usr/bin/env python3
"""DEFINITION-STATUS.md after layer 3's definition re-issue is authorised (MESHSAT-1357, layer 3 round 5's fix round, 30
September 2026; the engineering collaborator's closure check astra-check-l3r5-1, B3). CONOPS.md and PRODUCT-BRIEF.md
are baselined and are not edited by layer 3; their re-stamp with the approved texts is a follow-on of layers 1 and 2
(closure item L3-C63). So that an engineer is not misled meanwhile, this script adds to the status page, from the files
themselves: one row in "Where the current state lives" pointing at the change record, and a section stating that the
re-issue is authorised by owner ruling D-38 and accepted by the targeted independent review, that neither document is
re-stamped yet, that until then the approved change record governs where a document differs, and the rows the draft
proposes for this page's current values (read from DEFINITION-REISSUE-DRAFT.md, byte for byte).

The page is bound by CFL-016's reading (its `evidence_bound_to`, the status page at its sha256/16), so the same run
rebinds it in the registry with one evidence entry, as the s122 rebinds did: the change only inserts lines (none
removed), and the section the s122 verdicts read on this page (s122lib.STATUS_KEY, CONOPS's current circuit values)
is byte-identical, both asserted before anything is written; the entry changes no result.

It refuses unless l3r2.yaml's `definition_reissue` names the change record at its sha256/16 with a ruling that decides
the re-issue, and a second run is refused. No dash character is written.

Usage: python3 apply_definition_status_l3r5.py [--check] [--page PATH]   (--page: a copy of the page, for the tests)
"""
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "l3r2"))
import l3edit as E  # noqa: E402
import yaml  # noqa: E402

PAGE = os.path.join(E.TOP, "v2/docs/handover/DEFINITION-STATUS.md")
DATA = os.path.join(E.TOP, "v2/docs/handover/layer3/l3r2.yaml")
RECORD = "v2/docs/handover/layer3/DEFINITION-CHANGE-RECORD-L3.md"
DRAFT = "v2/docs/handover/layer3/DEFINITION-REISSUE-DRAFT.md"
HEADING = "## Layer 3's definition re-issue (30 September 2026): the approved change record governs until the re-stamp"
BEFORE = "## What the two documents carried at their baselines\n"
LAST_ROW_START = "| CONOPS's circuit passages whose values differ from the committed netlists ("
ROWS_HEAD = "## Rows proposed for `handover/DEFINITION-STATUS.md`'s current values"
STATUS_KEY = "## Current values of CONOPS's circuit passages (stream s122, 29 September 2026)"
REL = "v2/docs/handover/DEFINITION-STATUS.md"
CFL = "CFL-016"


def restated(rec_text):
    """[(pid, doc, lines, what)] from the change record's table 'The passages restated'."""
    out = []
    sec = rec_text.split("## The passages restated", 1)[1].split("\n## ", 1)[0]
    for l in sec.split("\n"):
        m = re.match(r"^\| (\w\d\d) \| `([^`]+)` \| ([^|]+) \| ([^|]+) \| `[0-9a-f]{16}` \| `[0-9a-f]{16}` \|$", l.strip())
        if m: out.append((m.group(1), m.group(2), m.group(3).strip(), m.group(4).strip()))
    if not out: E.refuse("the change record lists no restated passage")
    return out


def draft_rows(draft_text):
    if ROWS_HEAD not in draft_text: E.refuse("the draft proposes no rows for this page")
    sec = draft_text.split(ROWS_HEAD, 1)[1].split("\n## ", 1)[0]
    rows = [l for l in sec.split("\n") if l.startswith("| DC-L3-")]
    if not rows: E.refuse("the draft's row table is empty")
    return rows


def build(page):
    if HEADING in page: E.refuse("the page already carries the re-issue section: this script has run")
    data = yaml.safe_load(open(DATA, encoding="utf-8"))
    dr = data.get("definition_reissue")
    if not dr: E.refuse("l3r2.yaml's definition_reissue is not filed: the re-issue is not authorised")
    if str(dr.get("record")) != RECORD: E.refuse("definition_reissue names %s, not %s" % (dr.get("record"), RECORD))
    rec_path, draft_path = os.path.join(E.TOP, RECORD), os.path.join(E.TOP, DRAFT)
    if E.sha16(rec_path) != str(dr.get("sha16")): E.refuse("%s is not at the sha256/16 definition_reissue files" % RECORD)
    rec = open(rec_path, encoding="utf-8").read()
    m = re.findall(r"`DEFINITION-REISSUE-DRAFT\.md` \(sha256/16 `([0-9a-f]{16})`\)", rec)
    if len(m) != 1 or E.sha16(draft_path) != m[0]: E.refuse("the draft is not at the sha256/16 the change record names")
    req = E.parse(open(E.REGISTRY, encoding="utf-8").read())
    rul = next((r for r in req["owner_rulings"] if r["id"] == str(dr.get("approved_by"))), None)
    if rul is None or str(rul.get("decides")) != "definition_reissue":
        E.refuse("%s does not decide the re-issue" % dr.get("approved_by"))
    rid = rul["id"]
    ps = restated(rec)
    by_doc = {}
    for pid, doc, lines, what in ps: by_doc.setdefault(os.path.basename(doc), []).append("%s (%s)" % (pid, lines.replace(" to ", " to ")))
    rows = draft_rows(open(draft_path, encoding="utf-8").read())
    if page.count(BEFORE) != 1: E.refuse("the heading %r is not on the page once" % BEFORE.strip())
    lines = page.split("\n")
    last = [i for i, l in enumerate(lines) if l.startswith(LAST_ROW_START)]
    if len(last) != 1: E.refuse("the last row of 'Where the current state lives' is not on the page once")
    row = ("| The passages of both documents that layer 3's closure restates (%d passages; the re-issue authorised by owner "
           "ruling %s, not yet re-stamped into either document) | the section \"%s\" below; `handover/layer3/%s` and "
           "`handover/layer3/%s` | `CONOPS.md`, passage (baselined line): %s; `PRODUCT-BRIEF.md`, passage (baselined line): %s |" % (
               len(ps), rid, HEADING[3:], os.path.basename(RECORD), os.path.basename(DRAFT),
               ", ".join(by_doc.get("CONOPS.md", [])), ", ".join(by_doc.get("PRODUCT-BRIEF.md", []))))
    section = [HEADING, "",
               E.fold("Layer 3's closure (owner rulings D-28 to D-37, `handover/layer3/`) restates %d passages of the two "
                      "documents, each listed with its lines, its baselined and its proposed text in the change record "
                      "`handover/layer3/%s` (sha256/16 `%s`) and the draft `handover/layer3/%s` (sha256/16 `%s`). The re-issue is "
                      "authorised by owner ruling %s, his closure instructions of 30 September 2026 (the affected CONOPS and "
                      "product-brief passages generated from his choices and accepted by one targeted acceptance review; the "
                      "session's reading is labelled as such in `handover/layer3/OWNER-INSTRUCTION-2026-09-30.md`), and its "
                      "acceptance is the targeted independent review of layer 3's closure (closure item L3-C27 of "
                      "`handover/layer3/L3-RECONCILIATION.md`); `handover/layer3/l3r2.yaml` names the record with that ruling "
                      "(`definition_reissue`). **Neither document is re-stamped yet**: the proposed texts are written into "
                      "`CONOPS.md` and `PRODUCT-BRIEF.md` by their re-stamp through layers 1 and 2, each issued again with the "
                      "change stated in it (the rule above), an open obligation of the integrator (closure item L3-C63). "
                      "**Until that re-stamp, where either document differs from the approved change record, the change "
                      "record governs.** The rows the draft proposes for this page's current values, copied from it:"
                      % (len(ps), os.path.basename(RECORD), dr["sha16"], os.path.basename(DRAFT), m[0], rid), 0).rstrip("\n"),
               "", "| Row | Where | Current value |", "|---|---|---|"] + rows + [""]
    for t in [row] + section:
        for d in E.DASHES:
            if d in t: E.refuse("a written text carries a dash character")
    lines = lines[:last[0] + 1] + [row] + lines[last[0] + 1:]
    new = "\n".join(lines)
    return new.replace(BEFORE, "\n".join(section) + "\n" + BEFORE, 1)


def status_section(page):
    if page.count(STATUS_KEY) != 1: E.refuse("the section %r is not on the page once" % STATUS_KEY[3:])
    i = page.index(STATUS_KEY)
    j = page.find("\n## ", i + 3)
    return page[i:j if j > 0 else len(page)]


def only_inserts(old, new):
    """True when every line of `old` stands in `new` in the same order (the change inserts lines and removes none)."""
    it = iter(new.split("\n"))
    return all(any(x == y for y in it) for x in old.split("\n"))


def rebind(raw, old_sha, new_sha, added):
    d = E.parse(raw)
    rec = next((r for r in d["records"] if r["id"] == CFL), None)
    if rec is None: E.refuse("%s is not in the registry" % CFL)
    want = "%s@%s" % (REL, old_sha)
    if want not in (rec.get("evidence_bound_to") or []): E.refuse("%s is not bound to %s" % (CFL, want))
    entry = ("v2/docs/handover/DEFINITION-STATUS.md re-read at layer 3's round 5 fix round (MESHSAT-1357, 30 September "
             "2026; v2/docs/records/l3r5/apply_definition_status_l3r5.py, %s to %s): the change inserts %d lines and removes "
             "none, one row in the section Where the current state lives and the section %s, which points at layer 3's "
             "approved change record until CONOPS.md and PRODUCT-BRIEF.md are re-stamped; the section of CONOPS's current "
             "circuit values, the only section of this page the s122 verdicts read (s122lib.STATUS_KEY), is byte-identical, "
             "its DC rows unchanged; none of the places this record's evidence names in this document is among the "
             "changed ones. This entry does not re-read the rest of this record's argument; rebound to %s. This entry "
             "changes no result." % (old_sha, new_sha, added, HEADING[3:], new_sha))
    E.screen(entry, CFL)

    def f(block):
        if block.count('      - "%s"' % want) != 1: E.refuse("%s's binding line is not in its block once" % CFL)
        block = block.replace('      - "%s"' % want, '      - "%s@%s"' % (REL, new_sha))
        return E.add_list_entry(block, "evidence", entry)
    return E.replace_entry(raw, CFL, f, "records")


def main(argv):
    path = argv[argv.index("--page") + 1] if "--page" in argv else PAGE
    old = open(path, encoding="utf-8").read()
    try:
        new = build(old)
        if not only_inserts(old, new): E.refuse("the change removes or reorders a line of the page")
        if status_section(old) != status_section(new): E.refuse("the section of CONOPS's current circuit values changed")
        added = len(new.split("\n")) - len(old.split("\n"))
        reg_old = reg_new = None
        if path == PAGE:
            import hashlib
            sha = lambda s: hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]
            reg_old = open(E.REGISTRY, encoding="utf-8").read()
            reg_new = rebind(reg_old, sha(old), sha(new), added)
            got = set(E.diff_entries(E.parse(reg_old), E.parse(reg_new)))
            if got != {("records", CFL, "changed")}: E.refuse("the registry entries changed are not the list: %s" % sorted(got))
            if E.changed_fields(E.parse(reg_old), E.parse(reg_new), "records", CFL) != ["evidence", "evidence_bound_to"]:
                E.refuse("the fields of %s changed are not evidence and evidence_bound_to" % CFL)
    except E.Refused as e:
        print("apply_definition_status_l3r5: REFUSED: %s" % e)
        return 2
    print("apply_definition_status_l3r5: %d line(s) added (one row and the re-issue section)%s%s" % (
        added, "; %s rebound" % CFL if reg_new else "", " (check only, nothing written)" if "--check" in argv else ""))
    if "--check" not in argv:
        E.commit_text(path, old, new)
        print("apply_definition_status_l3r5: written %s" % os.path.relpath(path, E.TOP))
        if reg_new:
            # the rebound registry is validated with the new page in place (the binding reads the file), and the page
            # is put back if it does not validate
            errs, warns = E.validate(reg_new)
            if errs:
                open(path, "w", encoding="utf-8").write(old)
                print("apply_definition_status_l3r5: REFUSED: the rebound registry does not validate (%s); the page is "
                      "restored" % "; ".join(errs[:3]))
                return 2
            E.commit_text(E.REGISTRY, reg_old, reg_new)
            print("apply_definition_status_l3r5: written %s (%s rebound; validator 0 errors, %d warnings)" % (
                os.path.relpath(E.REGISTRY, E.TOP), CFL, len(warns)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
