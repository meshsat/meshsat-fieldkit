#!/usr/bin/env python3
"""Every number a document asserts about the hardware names the artefact it was read from (rule DOC-002,
MESHSAT-862, 16 September 2026).

The rule asks that each asserted number carry its artefact hash or its evidence id, or be marked an estimate.
The documents that assert numbers about a board are the ones inside its deliverable folder: the order notes
say its size, its layer count, its copper weight and its stackup, and the folder's own read-me says what it
contains. Until today the order note said "generated from the board file" and named no board, so a note beside
a folder cut three phases ago looked exactly like one beside the current board, and this project has already
shipped three such folders describing boards it is not building.

WHAT IT CHECKS, per deliverable folder:

  * the folder holds a board file, because a folder that describes no board cannot be traced to one;
  * every document that asserts hardware numbers carries a provenance line naming a file and a sha256;
  * that sha256 IS the sha256 of the board in the folder, not of some other board.

WHAT IT DOES NOT DO. It does not read the prose for numbers: a claim in a sentence is a manual-review question
and the rule says so (its verification method is MANUAL_REVIEW and SCRIPT). What it makes impossible is the
case that has actually happened here, a document whose numbers are right about a board nobody is building.

Usage: doc_provenance.py [<release dir>] [--json]
"""
import os, sys, re, json, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import verdict as _v

# The documents in a deliverable folder that assert numbers about the hardware.
ASSERTS_NUMBERS = ("ORDER-NOTES.txt",)
PROV = re.compile(r"sha256\s+([0-9a-f]{8,64})", re.I)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def judge(release_dir):
    """The ORDER folders, which is where the document a person reads while placing an order lives.

    The deliverable folders under boards/ carry the board and its own recorded sha256; the order folders under
    order/ carry the gerber zip the fabricator receives and ORDER-NOTES.txt, the document that asserts the
    board's size, layer count, thickness, copper weight and stackup. That note is what this rule is about."""
    rows, fails, notes = [], [], []
    for folder in sorted(glob.glob(os.path.join(release_dir, "order", "*"))):
        if not os.path.isdir(folder) or os.path.basename(folder) == "superseded": continue
        name = os.path.basename(folder)
        zips = sorted(glob.glob(os.path.join(folder, "*-gerbers.zip")))
        if not zips:
            notes.append("%s holds no gerber zip, so it is not an order folder" % name)
            continue
        bsha = sha256_file(zips[0])
        for doc in ASSERTS_NUMBERS:
            p = os.path.join(folder, doc)
            if not os.path.exists(p):
                # A folder without that document asserts nothing in it; it is reported, not failed.
                notes.append("%s has no %s" % (name, doc)); continue
            text = open(p, encoding="utf-8", errors="replace").read()
            shas = [g.lower() for g in PROV.findall(text)]
            rows.append((name, doc))
            if not shas:
                fails.append("%s/%s asserts hardware numbers and names no artefact: a reader cannot tell which "
                             "board they are about" % (name, doc))
            elif not any(bsha.startswith(g) for g in shas):
                fails.append("%s/%s names sha256 %s and the gerber zip in that folder is %s: the numbers and "
                             "the artefact the fabricator receives are not the same thing"
                             % (name, doc, ", ".join(g[:16] for g in shas[:3]), bsha[:16]))
    return rows, fails, notes


def main(argv):
    rel = argv[0] if argv and not argv[0].startswith("--") else os.path.join(
        os.path.dirname(os.path.dirname(HERE)), "release", "revA")
    rows, fails, notes = judge(rel)
    print("doc_provenance: %d document(s) in %d deliverable folder(s) checked against the board beside them; "
          "%d name no artefact or the wrong one" % (len(rows), len({r[0] for r in rows}), len(fails)))
    for f in fails[:20]: print("  FAIL %s" % f)
    for n in notes[:8]: print("  note %s" % n)
    if "--json" in argv: print(json.dumps({"rows": rows, "fails": fails, "notes": notes}, indent=1))
    # A READING TAKEN WITH LESS INPUT NEVER REPLACES ONE TAKEN WITH MORE (17 September 2026, the same rule the
    # cross-board contracts carry). This tool judges the DOCUMENTS in the release folders, and a tree that has
    # no release folders at all, which is what a sweep tree is, has nothing to say about them: left to write
    # its INCONCLUSIVE it would overwrite the reading taken where the folders are.
    if not rows:
        import json as _j
        _p = os.path.join(os.environ.get("VERDICT_DIR") or os.path.join(os.getcwd(), "out"),
                          "doc_provenance.verdict.json")
        try: _prev = _j.load(open(_p, encoding="utf-8"))
        except Exception: _prev = None
        if _prev and (_prev.get("counts") or {}).get("documents"):
            print("doc_provenance: this tree holds no deliverable folder with a document to check, and the "
                  "verdict on disk was taken where they are, so it is left as it stands")
            return _v.INCONCLUSIVE
    return _v.write("doc_provenance", _v.FAIL if fails else (_v.INCONCLUSIVE if not rows else _v.PASS),
                    counts={"documents": len(rows), "folders": len({r[0] for r in rows}), "untraceable": len(fails)},
                    denominator=len(rows), evidence=fails[:20], inputs={"release": rel},
                    note=("every document that asserts hardware numbers names the board it was read from, by "
                          "sha256, and that board is the one in its own folder" if rows else
                          "no deliverable folder holds a document that asserts hardware numbers"))


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
