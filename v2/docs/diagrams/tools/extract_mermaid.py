#!/usr/bin/env python3
"""Copy every Mermaid diagram out of the architecture page and the battery review packet (MESHSAT-1357, layer 4).

The Markdown documents stay the editable originals: each ```mermaid block is written unchanged to
v2/docs/diagrams/src/<name>.mmd, preceded only by a Mermaid front-matter title that names the document, the section, the
line range and the document's sha256/16, and says it is a design diagram of an unbuilt prototype. The rendered SVG and
PDF (tools/render.sh) therefore carry their source document's identity; the tree revision they were drawn at is in
MANIFEST.json (a commit cannot be named inside a file it contains).

A block is named after its document and the section heading above it; the names are listed in SOURCES so that a new
block or a moved one is reported instead of silently renamed.

Usage: python3 v2/docs/diagrams/tools/extract_mermaid.py [--check]
  --check writes nothing and exits 1 when a committed src/*.mmd no longer matches its block in the document (the
          block's text, not the title line): the sign that the document changed and the SVGs must be re-rendered."""
import os, re, sys
sys.dont_write_bytecode = True   # nothing written into the tree beside the sources read
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netlist as N

SRC = os.path.join(N.REPO, "v2/docs/diagrams/src")
# document -> the names of its blocks, in order
SOURCES = {
    "v2/docs/ARCHITECTURE.md": ["arch-2-context", "arch-3-2-board-interconnect", "arch-4-1-power-tree",
                                "arch-4-3-power-up", "arch-5-5-lanes-and-fabric"],
    "v2/docs/review-packets/battery/PROTECTION-ARCHITECTURE.md": ["battery-protection-states"],
    "v2/docs/review-packets/battery/CHARGER-STATE-SEQUENCE.md": ["battery-charger-states"],
}


def blocks(relpath):
    """(first line, last line, heading, text) of every ```mermaid block, lines 1-based, fences excluded."""
    lines = open(os.path.join(N.REPO, relpath), encoding="utf-8").read().split("\n")
    out, heading, i = [], "", 0
    while i < len(lines):
        if lines[i].startswith("#"):
            heading = lines[i].lstrip("#").strip()
        if lines[i].strip() == "```mermaid":
            j = i + 1
            while lines[j].strip() != "```":
                j += 1
            out.append((i + 2, j, heading, "\n".join(lines[i + 1:j])))
            i = j
        i += 1
    return out


def render_src(relpath, first, last, heading, text, head):
    doc = relpath.replace("v2/docs/", "")
    # the document's content identity only: a commit cannot be named by a file it contains, and MANIFEST.json holds the tree
    title = ("%s, %s (lines %d to %d of the document with sha256/16 %s): design diagram of an unbuilt prototype"
             % (doc, heading, first, last, N.sha16(relpath)))
    return "---\ntitle: \"%s\"\n---\n%s\n" % (title.replace('"', "'"), text)


def main():
    check = "--check" in sys.argv
    head, dirty = N.git_rev()
    stale, problems = [], []
    for relpath, names in SOURCES.items():
        found = blocks(relpath)
        if len(found) != len(names):
            problems.append("%s has %d mermaid blocks, SOURCES names %d: name the new block" % (relpath, len(found), len(names)))
            continue
        for name, (first, last, heading, text) in zip(names, found):
            path = os.path.join(SRC, name + ".mmd")
            body = render_src(relpath, first, last, heading, text, head)
            if check:
                old = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
                if old.split("---\n", 2)[-1] != body.split("---\n", 2)[-1]:
                    stale.append(name)
                continue
            os.makedirs(SRC, exist_ok=True)
            open(path, "w", encoding="utf-8").write(body)
            print("%-32s %s lines %d-%d (%s)" % (name, relpath, first, last, heading))
    for p in problems:
        print("PROBLEM: " + p)
    if check:
        print("mermaid sources: %s" % ("current" if not stale else "STALE: " + ", ".join(stale)))
    return 1 if problems or stale else 0


if __name__ == "__main__":
    sys.exit(main())
