#!/usr/bin/env python3
"""Build the restructured PRODUCT-BRIEF.md and CONOPS.md, the status page and the move map (MESHSAT-1357,
27 September 2026, branch fnd/defstab).

Reads both documents FROM THE BASE COMMIT (git show 31cd29b9:<path>), never from the working tree, so a second run
gives the same bytes. Every cut of cuts.py is asserted: its anchors occur once, cuts do not overlap, the kept text of
every block equals the original block with its cuts removed, every sentence of a kept block is a sentence of the
original block (whitespace-normalised), the moved text is written byte for byte at its new place, and the CONOPS needs
table (section 2, the table under '## 2. Needs') is byte-identical.

Usage: build.py <worktree root>
"""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cuts import CUTS, BRIEF, CONOPS  # noqa: E402
import heads  # noqa: E402

BASE = "31cd29b9"
ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", ".."))


def sha(s): return hashlib.sha256(s.encode("utf-8")).hexdigest()


def git_show(path):
    return subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, path)], check=True,
                          capture_output=True).stdout.decode("utf-8")


def line_of(text, off): return text.count("\n", 0, off) + 1


def _split(s):
    s = " ".join(s.split())
    return [x for x in re.split(r"(?<=[.!?])\s+", s) if x]


def sentences(block):
    """The sentences of a block, whitespace-normalised; a table row is split into its cells first, so that a sentence
    never runs from one cell into the next."""
    out, para = [], []
    for line in block.split("\n"):
        if line.lstrip().startswith("|"):
            if para: out += _split(" ".join(para)); para = []
            for cell in line.strip().strip("|").split(" | "):
                out += _split(cell)
        else:
            para.append(line)
    if para: out += _split(" ".join(para))
    return out


def blocks(text):
    """[(start offset, end offset, text)] of the blank-line separated blocks."""
    out, pos = [], 0
    for m in re.finditer(r"\n\n+", text):
        if m.start() > pos: out.append((pos, m.start(), text[pos:m.start()]))
        pos = m.end()
    if pos < len(text) and text[pos:].strip(): out.append((pos, len(text), text[pos:].rstrip("\n")))
    return out


def locate(text, fid):
    spans = []
    for (cid, f, start, end, dest, section, cat, why) in CUTS:
        if f != fid: continue
        n = text.count(start)
        assert n == 1, "%s: start anchor occurs %d times: %r" % (cid, n, start[:60])
        a = text.index(start)
        b = text.find(end, a)
        assert b >= 0, "%s: end anchor not found after start: %r" % (cid, end[:60])
        b += len(end)
        spans.append(dict(id=cid, a=a, b=b, dest=dest, section=section, category=cat, why=why))
    spans.sort(key=lambda s: s["a"])
    for x, y in zip(spans, spans[1:]):
        assert x["b"] <= y["a"], "cuts %s and %s overlap" % (x["id"], y["id"])
    return spans


def apply(text, spans):
    out, pos = [], 0
    for s in spans:
        out.append(text[pos:s["a"]]); pos = s["b"]
    out.append(text[pos:])
    return "".join(out)


def needs_table(text):
    i = text.index("## 2. Needs\n")
    j = text.index("\n\n", text.index("| NEED-19 |", i))
    return text[text.index("| ID |", i):j]


def build(fid, heads_text, appendix_intro, base_label):
    orig = git_show(fid)
    spans = locate(orig, fid)
    for s in spans:
        raw = orig[s["a"]:s["b"]]
        s["moved"] = raw.strip(" \n")
        ms = orig.index(s["moved"], s["a"])
        s["lines"] = [line_of(orig, ms), line_of(orig, ms + len(s["moved"]) - 1)]
        s["sha256"] = sha(s["moved"])
    kept = apply(orig, spans)
    # the title line stays first; the head block follows it; the definition part is the rest
    title, rest = kept.split("\n", 1)
    assert title.startswith("# MeshSat field kit V2"), title
    rest = rest.lstrip("\n").rstrip("\n")
    assert "\n\n\n" not in rest, "a cut left a double blank line in %s" % fid

    # blocks of the original (after the title) against the kept blocks
    orig_body_off = orig.index("\n") + 1
    while orig[orig_body_off] == "\n": orig_body_off += 1
    ob = blocks(orig[orig_body_off:])
    kb = [t for (_, _, t) in blocks(rest)]
    report = []
    kept_iter = iter(kb)
    for (a, b, t) in ob:
        a += orig_body_off; b += orig_body_off
        inside = [s for s in spans if s["a"] < b and s["b"] > a]
        new = apply(orig[a:b], [dict(a=max(s["a"], a) - a, b=min(s["b"], b) - a) for s in inside]).strip("\n")
        entry = dict(old_lines=[line_of(orig, a), line_of(orig, b - 1)], sha256_before=sha(t), cuts=[s["id"] for s in inside])
        if not new.strip():
            entry.update(kept=False, sha256_after=None)
        else:
            nxt = next(kept_iter)
            assert nxt == new, "%s: block at line %d does not close up as computed" % (fid, entry["old_lines"][0])
            before_s = set(sentences(t))
            for snt in sentences(new):
                assert snt in before_s, "%s: a kept sentence is not in the original block: %r" % (fid, snt[:80])
            entry.update(kept=True, sha256_after=sha(new), unchanged=(new == t))
        report.append(entry)
    assert next(kept_iter, None) is None, "%s: more kept blocks than original ones" % fid

    # the appendix, word for word; a moved section's own heading is demoted two levels, under its A-entry
    app = ["## Appendix: review and status history (not part of the baseline)", appendix_intro]
    n = 0
    for s in spans:
        if s["dest"] != "appendix": continue
        n += 1
        body = s["moved"]
        transform = None
        if body.startswith("## "):
            body = "##" + body
            transform = "its heading demoted from '## ' to '#### ' under its appendix entry; every other byte as it was"
        elif body.startswith("| ") and "\n" not in body:
            hdr = orig[:s["a"]].rsplit("\n|---", 1)
            hdr_line = hdr[0].rsplit("\n", 1)[1]
            sep = "|---" + orig[len(hdr[0]) + 5:].split("\n", 1)[0]
            body = hdr_line + "\n" + sep + "\n" + body
            transform = ("preceded by the header and separator lines of the table it stood in (%s), so that it renders "
                         "as a table; the row's own bytes as they were" % hdr_line)
        app.append("### A%d. From %s" % (n, s["section"]))
        app.append("*Lines %d to %d %s: %s.*" % (s["lines"][0], s["lines"][1], base_label, s["why"]))
        app.append(body)
        s["new_location"] = "%s, Appendix: review and status history (not part of the baseline), A%d" % (fid, n)
        s["transform"] = transform
        s["sha256_at_new_location"] = sha(body)
    text = title + "\n\n" + heads_text.strip("\n") + "\n\n" + rest + "\n\n" + "\n\n".join(app) + "\n"
    return orig, text, spans, report


def main():
    so = {}
    b_orig, b_text, b_spans, b_rep = build(BRIEF, heads.BRIEF_HEAD, heads.BRIEF_APPENDIX_INTRO, "at `31cd29b9`")
    c_orig, c_text, c_spans, c_rep = build(CONOPS, heads.CONOPS_HEAD, heads.CONOPS_APPENDIX_INTRO, "at `31cd29b9`")
    assert needs_table(c_orig) == needs_table(c_text), "the needs table changed"
    for t in (b_text, c_text):
        assert "—" not in t and "–" not in t, "a dash crept in"

    # the status page: the implementation status moved word for word, each under its label
    parts = [heads.STATUS_HEAD.strip("\n")]
    for fid, spans, base in ((BRIEF, b_spans, "PRODUCT-BRIEF.md"), (CONOPS, c_spans, "CONOPS.md")):
        parts.append("### From `%s`" % base)
        parts.append(heads.STATUS_FROM[fid])
        k = 0
        for s in spans:
            if s["dest"] != "status": continue
            k += 1
            parts.append("#### %s. From %s" % (s["id"], s["section"]))
            parts.append("*`%s` lines %d to %d at `31cd29b9`: %s.*" % (base, s["lines"][0], s["lines"][1], s["why"]))
            parts.append(s["moved"])
            s["new_location"] = "v2/docs/handover/DEFINITION-STATUS.md, %s" % s["id"]
            s["transform"] = None
            s["sha256_at_new_location"] = s["sha256"]
    if heads.STATUS_TAIL.strip(): parts.append(heads.STATUS_TAIL.strip("\n"))
    status = "\n\n".join(parts) + "\n"
    assert "—" not in status and "–" not in status

    for rel, t in ((BRIEF, b_text), (CONOPS, c_text), ("v2/docs/handover/DEFINITION-STATUS.md", status)):
        open(os.path.join(ROOT, rel), "w", encoding="utf-8").write(t)
    # every moved text is present byte for byte at its new place
    for s in b_spans + c_spans:
        tgt = status if s["dest"] == "status" else (b_text if s in b_spans else c_text)
        want = s["moved"] if not (s.get("transform") or "").startswith("its heading") else "##" + s["moved"]
        assert tgt.count(want) == 1, "%s is not at its new place exactly once" % s["id"]

    def mv(spans):
        return [dict(id=s["id"], category=s["category"], section=s["section"], why=s["why"],
                     old_lines=s["lines"], old_lines_at=BASE, sha256=s["sha256"], new_location=s["new_location"],
                     sha256_at_new_location=s["sha256_at_new_location"], transform=s["transform"]) for s in spans]

    doc = {
        "what": "the map of the definition-baseline restructure of PRODUCT-BRIEF.md and CONOPS.md (MESHSAT-1357)",
        "branch": "fnd/defstab", "base": BASE,
        "rule": ("independent review of handover H2, v2/docs/reviews/2026-09-27-h2-independent-review.md section 4: "
                 "the definition is reopened only when a requirement, scope, operating concept or product decision "
                 "changes; a changed count or circuit correction updates the status page, not the baseline"),
        "method": ("whole paragraphs, sections, list items, sentences or table-cell sentences move; no sentence is "
                   "split or reworded. Review and revision history goes to the same file's appendix; changing "
                   "implementation results in running text go to v2/docs/handover/DEFINITION-STATUS.md. A sentence "
                   "that carries definition content and a result together stays word for word, as does every table "
                   "row but its revision notes; the head of each file states that its figures are values at the "
                   "baseline. sha256 is over the UTF-8 bytes of the text named; a moved block's text is the cut "
                   "stripped of the separating spaces and newlines around it"),
        "files": {},
    }
    for fid, orig, text, spans, rep, head in ((BRIEF, b_orig, b_text, b_spans, b_rep, heads.BRIEF_HEAD),
                                             (CONOPS, c_orig, c_text, c_spans, c_rep, heads.CONOPS_HEAD)):
        doc["files"][fid] = {
            "sha256_before": sha(orig), "sha256_after": sha(text),
            "lines_before": orig.count("\n"), "lines_after": text.count("\n"),
            "moved": mv(spans),
            "definition_blocks": rep,
            "added_head_blocks": [dict(sha256=sha(t), first_words=" ".join(t.split()[:8]))
                                  for (_, _, t) in blocks(head.strip("\n") + "\n")],
        }
    doc["files"][CONOPS]["needs_table_sha256"] = sha(needs_table(c_orig))
    doc["files"][CONOPS]["needs_table_byte_identical"] = True
    doc["status_page"] = {"path": "v2/docs/handover/DEFINITION-STATUS.md", "sha256": sha(status)}
    json.dump(doc, open(os.path.join(HERE, "moves.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(HERE, "moves.json"), "a").write("\n")
    for fid in (BRIEF, CONOPS):
        f = doc["files"][fid]
        kb = [e for e in f["definition_blocks"] if e["kept"]]
        print("%s: %d moved (%d appendix, %d status); %d blocks kept (%d unchanged, %d closed up), %d dropped whole; "
              "sha256 %s -> %s; lines %d -> %d" % (
                  fid, len(f["moved"]), sum(1 for m in f["moved"] if "Appendix" in m["new_location"]),
                  sum(1 for m in f["moved"] if "DEFINITION-STATUS" in m["new_location"]), len(kb),
                  sum(1 for e in kb if e["unchanged"]), sum(1 for e in kb if not e["unchanged"]),
                  sum(1 for e in f["definition_blocks"] if not e["kept"]), f["sha256_before"][:16],
                  f["sha256_after"][:16], f["lines_before"], f["lines_after"]))
    print("needs table sha256", doc["files"][CONOPS]["needs_table_sha256"][:16], "byte-identical")
    print("status page sha256", doc["status_page"]["sha256"][:16])


if __name__ == "__main__":
    main()
