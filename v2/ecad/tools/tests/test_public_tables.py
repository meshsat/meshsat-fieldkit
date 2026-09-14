#!/usr/bin/env python3
"""The public board tables name a folder a reader can open (MESHSAT-862, 14 September 2026).

`README.md` and `v2/README.md` carry a table of the seven boards with a revision column, and `v2/README.md`
links each row to its deliverable folder. Both had drifted five generations: A22 against A24 in the tree, D8
against D11, E6 against E9, P1 against P4, and **`meshsat-pcb-b-revA-B16/`, which has never existed** at all,
as a link in a public README of a repository that mirrors to GitHub within minutes.

CLAUDE.md's rule for these files is that they must stay true. That was a sentence and this makes it a floor:
every revision named in either table must be the newest deliverable folder for that board, and every folder a
row links to must exist. Nothing here judges whether a board is good, only that the document points at what is
in the tree.
"""
import os, re

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(TOOLS)))
BOARDS = os.path.join(REPO, "v2", "release", "revA", "boards")
STEM = {"PCB-A": "meshsat-pcb-a-revA-", "PCB-B": "meshsat-pcb-b-revA-", "PCB-C": "meshsat-pcb-c-revA-",
        "PCB-D": "meshsat-pcb-d-revA-", "PCB-E1": "meshsat-pcb-e-revA-", "PCB-E5": "meshsat-pcb-e5-revA-",
        "PCB-P": "meshsat-pcb-p-revA-"}


def _newest(prefix):
    """the newest deliverable folder for a board, by the number in its phase"""
    names = [n for n in os.listdir(BOARDS) if n.startswith(prefix) and os.path.isdir(os.path.join(BOARDS, n))]
    def key(n):
        m = re.search(r"-([A-Z])(\d+)", n[len(prefix) - 1:] or n)
        return int(m.group(2)) if m else -1
    return max(names, key=key) if names else None


def _rows(path):
    for line in open(os.path.join(REPO, path), encoding="utf-8").read().splitlines():
        if not line.startswith("| PCB-"): continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3 or not cells[1]: continue
        key = cells[0].split()[0]
        if key in STEM: yield path, key, cells


def t_every_revision_named_is_the_newest_deliverable_folder():
    seen = 0
    for path, key, cells in list(_rows("README.md")) + list(_rows("v2/README.md")):
        newest = _newest(STEM[key])
        if newest is None: continue
        want = newest[len(STEM[key]):]
        got = cells[1].split()[0]
        seen += 1
        assert want.startswith(got) or got == want.split("-")[0], (
            "%s names %s for %s and the newest folder in the tree is %s" % (path, cells[1], key, newest))
    assert seen >= 10, "the tables were not read at all (%d rows)" % seen


def t_every_folder_a_public_table_links_to_exists():
    for path in ("README.md", "v2/README.md"):
        txt = open(os.path.join(REPO, path), encoding="utf-8").read()
        for m in re.finditer(r"release/revA/boards/(meshsat-[A-Za-z0-9-]+)", txt):
            assert os.path.isdir(os.path.join(BOARDS, m.group(1))), (
                "%s links to release/revA/boards/%s and there is no such folder" % (path, m.group(1)))
