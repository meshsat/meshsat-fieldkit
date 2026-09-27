#!/usr/bin/env python3
"""The rebinds the H3 pages need in the requirements registry: none, shown; and the script that would make one
(MESHSAT-1357, 27 September 2026, the H3 pages worker; the integrator runs it, the worker does not edit the registry).

The registry binds some readings to documents by content (`evidence_bound_to`, "path@sha256/16"), pins the needs
document (`needs_document_sha256`) and names the baseline's reviews by hash (`baseline_reviews`). A page edited for
H3 that is bound there would make `rules_lib.py requirements` refuse or warn ("its reading is bound to <path> at
<old> and the tree holds <new>: re-read it before it decides").

WHAT THIS SCRIPT FOUND FOR H3. None of the pages edited for H3 (EDITED below) is bound, pinned or named by hash in
the registry, and every binding of the registry is current in the tree, so REBINDS is empty and the registry is not
touched. `rules_lib.py requirements` read "144 requirement record(s), 0 error(s), 0 warning(s)" in the worker's tree
with every H3 page edit in place. Run without arguments, the script proves both statements again and exits 0; it
exits 1 and names each stale binding if a later edit makes one, and it still writes nothing in that case unless that
binding has a row in REBINDS.

HOW A REBIND IS MADE (the way REQ-005, CFL-014 and CFL-016 were rebound to CONOPS.md by
v2/docs/records/defstab/apply_registry.py, and CON-010 and REQ-044 to CURRENT-EVIDENCE.md at 79963b3b). A row of
REBINDS names the record, the bound path, the sha256/16 the registry holds, the commit whose copy of the file has that
hash, the section headings the reading rests on, and one sentence on why the reading stands. For each row the script
  1. asserts the registry holds "<path>@<old sha16>" in that record, exactly once, and that the file at the named
     commit has that hash (the old sha is asserted, never assumed);
  2. extracts each cited section, by its heading, from the old file and from the tree's file and compares them; a
     cited section that differs REFUSES the rebind (the reading must be re-read by its owner, not re-stamped);
  3. lists every other section of the file that differs, by heading;
  4. adds, above `evidence_bound_to`, an evidence entry that starts with the file path, says which sections changed
     and that the cited ones are unchanged word for word, and ends "so it stands on the file at <new sha16>";
  5. replaces the binding, asserts the registry text differs, writes it, and parses it again with a YAML reader;
  6. refuses a second run: a record that already holds "<path>@<new sha16>" is an error, not a no-op.
The registry is edited as text so that every other byte stays as it is. `--self-test` runs steps 1 to 6 on a scratch
registry and document in a temporary directory, and then the second run's refusal; it touches nothing in the tree.

Usage (from the repository root):
  python3 v2/docs/records/h3/apply_rebinds.py                 check; apply REBINDS if it has rows
  python3 v2/docs/records/h3/apply_rebinds.py --self-test     prove the rebind path on a scratch copy
"""
import hashlib, os, re, subprocess, sys, tempfile

import yaml

REG_PATH = "v2/ecad/tools/pcb_requirements.yaml"
# Every page the H3 pages worker edited or added (branch fnd/h3, from main 6ec37197).
EDITED = [
    "v2/docs/handover/START-HERE.md", "v2/docs/handover/CONTINUATION-BRIEF.md", "v2/docs/handover/LAYER-STATUS.md",
    "v2/docs/handover/ENGINEERING-QUESTIONS.md", "v2/docs/handover/REGENERATE.md", "v2/docs/handover/H2-RESPONSE.md",
    "v2/docs/handover/GLOSSARY.md", "v2/docs/handover/RELEASE-H3.md", "v2/docs/handover/pack.yaml",
    "v2/docs/EXECUTION-PLAN.md", "v2/docs/reviews/READY-TO-ACT.md", "v2/docs/layout-constraints/A.md",
]
# (record id, path, old sha16, commit holding the old file, [section headings the reading rests on], why it stands)
REBINDS = []

BINDING = re.compile(r"^(.+)@([0-9a-f]{16})$")


def s16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def sections(text):
    """{heading line: the text under it up to the next heading of any level}, for a Markdown file."""
    out, head, buf = {}, "(before the first heading)", []
    for ln in text.splitlines():
        if re.match(r"^#{1,6} ", ln):
            out[head] = "\n".join(buf).strip(); head, buf = ln.strip(), []
        else:
            buf.append(ln)
    out[head] = "\n".join(buf).strip()
    return out


def wrap(text, width=110, indent="          "):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    lines.append(cur)
    return "\n".join(indent + l for l in lines)


def bindings(reg):
    """[(where, path, recorded sha16)] for every content binding of the parsed registry."""
    out = []
    for r in reg.get("records") or []:
        for b in r.get("evidence_bound_to") or []:
            m = BINDING.match(str(b))
            if m: out.append((r["id"], m.group(1), m.group(2)))
    for b in reg.get("baseline_reviews") or []:
        m = BINDING.match(str(b))
        if m: out.append(("baseline_reviews", m.group(1), m.group(2)))
    if reg.get("needs_document"):
        out.append(("needs_document_sha256", reg["needs_document"], str(reg.get("needs_document_sha256"))[:16]))
    return out


def old_file(root, commit, path):
    return subprocess.run(["git", "-C", root, "show", "%s:%s" % (commit, path)], check=True, capture_output=True).stdout


def rebind(root, text, row, old_bytes=None):
    """The registry text with one rebind made; raises AssertionError with the reason where it is refused."""
    rid, path, old16, commit, cited, why = row
    new_bytes = open(os.path.join(root, path), "rb").read()
    new16 = s16(new_bytes)
    old_bytes = old_file(root, commit, path) if old_bytes is None else old_bytes
    assert s16(old_bytes) == old16, "%s: %s at %s is %s, not the %s the row names" % (rid, path, commit, s16(old_bytes), old16)
    a = text.index("  - id: %s\n" % rid)
    b = text.find("\n  - id: ", a + 1); b = len(text) if b < 0 else b + 1      # the record with its last newline,
    rec = text[a:b]                                                             # so a binding on its last line is found
    assert rec.count('"%s@%s"' % (path, new16)) == 0, "%s: already bound to %s@%s: a second run is refused" % (rid, path, new16)
    bind_old = '      - "%s@%s"\n' % (path, old16)
    assert rec.count(bind_old) == 1, "%s: the registry does not hold %s@%s exactly once" % (rid, path, old16)
    assert new16 != old16, "%s: %s is unchanged at %s, nothing to rebind" % (rid, path, old16)
    so, sn = sections(old_bytes.decode("utf-8")), sections(new_bytes.decode("utf-8"))
    for h in cited:
        assert h in so and h in sn, "%s: the cited section %r is not in both files" % (rid, h)
        assert so[h] == sn[h], "%s: the cited section %r CHANGED: the reading is re-read by its owner, not rebound" % (rid, h)
    changed = [h for h in sn if h not in so or so[h] != sn[h]] + [h + " (removed)" for h in so if h not in sn]
    entry = ("%s re-read at handover H3 (the H3 pages, MESHSAT-1357): against the file at %s (%s) these sections "
             "changed: %s; the sections this reading rests on (%s) are unchanged word for word. %s, so it stands on "
             "the file at %s" % (path, old16, commit, "; ".join(changed) or "none by heading", "; ".join(cited),
                                 why.rstrip("."), new16))
    assert rec.count("    evidence_bound_to:\n") == 1, rid
    k = rec.index("    evidence_bound_to:\n")
    rec2 = rec[:k] + "      - >-\n%s\n" % wrap(entry) + rec[k:]
    rec2 = rec2.replace(bind_old, '      - "%s@%s"\n' % (path, new16))
    assert rec2 != rec
    out = text[:a] + rec2 + text[b:]
    assert out != text
    got = yaml.safe_load(out)                                               # parses, and holds what was meant
    r = [x for x in got["records"] if x["id"] == rid][0]
    assert "%s@%s" % (path, new16) in r["evidence_bound_to"] and r["evidence"][-1].startswith(path), rid
    return out, new16, changed


def self_test():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "v2/ecad/tools")); os.makedirs(os.path.join(d, "v2/docs"))
        old = "# Page\n\nhead\n\n## 1. Kept\n\nthe statement the reading rests on\n\n## 2. Status\n\nold status\n"
        new = old.replace("old status", "new status")
        doc = os.path.join(d, "v2/docs/PAGE.md")
        reg = ("records:\n  - id: REQ-900\n    evidence:\n      - >-\n          first reading\n    evidence_bound_to:\n"
               '      - "v2/docs/PAGE.md@%s"\n  - id: REQ-901\n    evidence: []\n' % s16(old.encode()))
        row = ("REQ-900", "v2/docs/PAGE.md", s16(old.encode()), "scratch", ["## 1. Kept"], "The statement is unchanged")
        open(doc, "w").write(new)
        out, new16, changed = rebind(d, reg, row, old_bytes=old.encode())
        assert changed == ["## 2. Status"], changed
        assert new16 == s16(new.encode()) and ('"v2/docs/PAGE.md@%s"' % new16) in out
        assert yaml.safe_load(out)["records"][1] == {"id": "REQ-901", "evidence": []}      # the rest is untouched
        for bad_row, bad_reg, bad_new, what in (
                (row, out, new, "a second run"),
                (row, reg, new.replace("the statement", "another statement"), "a cited section that changed"),
                ((row[0], row[1], "0" * 16) + row[3:], reg, new, "an old sha the file does not have")):
            open(doc, "w").write(bad_new)
            try:
                rebind(d, bad_reg, bad_row, old_bytes=old.encode())
            except AssertionError as e:
                print("self-test: %s is REFUSED: %s" % (what, e))
            else:
                raise SystemExit("self-test FAILED: %s was accepted" % what)
    print("self-test: one rebind made on a scratch registry, its evidence entry starting with the path; three refusals")
    return 0


def main():
    if "--self-test" in sys.argv[1:]:
        return self_test()
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
    regp = os.path.join(root, REG_PATH)
    text = open(regp, encoding="utf-8").read()
    reg = yaml.safe_load(text)
    bs = bindings(reg)
    paths = sorted({p for _, p, _ in bs})
    print("apply_rebinds: %s sha256/16 %s; %d content binding(s) over %d file(s)" % (
        REG_PATH, s16(text.encode("utf-8")), len(bs), len(paths)))
    stale = []
    for where, p, want in bs:
        fp = os.path.join(root, p)
        if where == "needs_document_sha256":
            have = hashlib.sha256(open(fp, "rb").read()).hexdigest()[:16] if os.path.isfile(fp) else None
        else:
            have = s16(open(fp, "rb").read()) if os.path.isfile(fp) else None
        if have != want:
            stale.append((where, p, want, have))
    hit = [p for p in EDITED if p in paths]
    print("pages edited for H3 that the registry binds by content: %s" % (", ".join(hit) or "none of the %d" % len(EDITED)))
    for where, p, want, have in stale:
        print("STALE: %s is bound to %s at %s and the tree holds %s" % (where, p, want, have or "no such file"))
    if not stale and not REBINDS:
        print("result: every binding is current and no rebind is needed; the registry is not touched")
        return 0
    todo = {(r[0], r[1]) for r in REBINDS}
    unknown = [s for s in stale if (s[0], s[1]) not in todo]
    if unknown:
        print("result: REFUSED, %d stale binding(s) with no row in REBINDS: the owner of each reading re-reads it and "
              "writes its row; nothing was written" % len(unknown))
        return 1
    new = text
    for row in REBINDS:
        new, new16, changed = rebind(root, new, row)
        print("rebound %s to %s@%s (sections changed: %s)" % (row[0], row[1], new16, "; ".join(changed) or "none"))
    assert new != text
    open(regp, "w", encoding="utf-8").write(new)
    yaml.safe_load(open(regp, encoding="utf-8"))
    print("result: %d rebind(s) written; run rules_lib.py requirements and rules_render.py --requirements next" % len(REBINDS))
    return 0


if __name__ == "__main__":
    sys.exit(main())
