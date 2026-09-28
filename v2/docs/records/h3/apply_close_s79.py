#!/usr/bin/env python3
"""Close S-79 in the requirements registry with handover snapshot H3 (MESHSAT-1357, 27 September 2026).

S-79 (layer 3, finding B-2 of the second release check, acceptance item 3.18, ENGINEERING-QUESTIONS EQ-29) asked for
a versioned package cut from the pushed commit that carries the requirements registry's re-baseline. H3 is that
package. This script moves the item from open_items to closed_items and touches nothing else: it asserts the item's
block as it stands, asserts the counts before and after by parsing the file, asserts that no record, need, ruling or
choice changed, and refuses a second run. Run from any folder of the checkout by the integrating session.

Usage: python3 v2/docs/records/h3/apply_close_s79.py <source commit> <zip sha256> <zip bytes> <zip entries>
"""
import os, subprocess, sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")


def main(argv):
    commit, zsha, zbytes, zentries = argv
    assert len(commit) == 40 and len(zsha) == 64, "a full commit id and a full sha256 are asked for"
    subprocess.run(["git", "merge-base", "--is-ancestor", commit, "HEAD"], cwd=TOP, check=True)
    t = open(P, encoding="utf-8").read()
    before = yaml.safe_load(t)
    ids_open = [x["id"] for x in before["open_items"]]
    ids_closed = [x["id"] for x in before["closed_items"]]
    if "S-79" in ids_closed:
        print("apply_close_s79: S-79 is closed already; nothing written"); return 2
    assert ids_open.count("S-79") == 1, "S-79 is not an open item"
    a = t.index("\n  - id: S-79\n")
    b = t.index("\n  - id: ", a + 1)
    block = t[a:b]
    assert "status: OPEN" in block and "acceptance item 3.18" in block and t.index("\nclosed_items:") > b, "the block is not the one read"
    title = block[block.index("    title: >-"):]
    closed = (
        "\n  - id: S-79\n"
        "    closed_by: commit %s\n"
        "    closing_evidence: >-\n"
        "      Handover snapshot H3 (v2/release/handover/H3.zip, sha256 %s, %s bytes, %s entries, with H3.zip.sha256 and\n"
        "      H3.MANIFEST.tsv beside it) is cut from commit %s, which is on the public main of GitLab and of GitHub (both\n"
        "      read 27 September 2026 21:18 UTC, before the build, so its SOURCE.txt marks the commit public) and carries\n"
        "      the re-baseline of this registry (baseline_state BASELINED at a54b793b, written in 2c12be91) and its re-check\n"
        "      (v2/docs/reviews/TARGETED-RECHECK-LAYER-3-2026-09-27.md, filed in 24e7bf5a). Its manifest names every file\n"
        "      with its git blob sha and its sha256, and handover_pack.py verify reads OK on the ZIP. The test suite on that\n"
        "      exact commit reads 1998 passed, 0 failed, 2 skipped on the KiCad host and 1937 passed, 0 failed, 63 skipped\n"
        "      on the runner, which has no KiCad (a skip is not a pass). The package carries layers 1, 2 and 3 as COMPLETE,\n"
        "      each on its AI review records, never a qualified review; it proves no requirement met. The registry inside\n"
        "      the ZIP still lists this item as open, because a snapshot cannot carry the record of its own filing; the two\n"
        "      fresh checks of H3 are recorded in v2/docs/handover/RELEASE-H3.md.\n" % (commit[:8], zsha, zbytes, zentries, commit[:8])
    ) + title.rstrip("\n")
    c = t.index("\nrecords:\n")
    assert c > t.index("\nclosed_items:")
    head, tail = t[:c].rstrip("\n"), t[c:]
    new = head[:a] + head[b:] + closed + "\n" + tail
    assert new != t
    after = yaml.safe_load(new)
    assert [x["id"] for x in after["open_items"]] == [i for i in ids_open if i != "S-79"]
    assert [x["id"] for x in after["closed_items"]] == ids_closed + ["S-79"]
    for sec in ("needs", "owner_rulings", "session_choices", "records"):
        assert after[sec] == before[sec], sec
    for k in before:
        if k not in ("open_items", "closed_items"):
            assert after[k] == before[k], k
    got = [x for x in after["closed_items"] if x["id"] == "S-79"][0]
    was = [x for x in before["open_items"] if x["id"] == "S-79"][0]
    assert got["title"] == was["title"] and got["closed_by"] == "commit %s" % commit[:8]
    open(P, "w", encoding="utf-8").write(new)
    print("apply_close_s79: open items %d to %d, closed items %d to %d; S-79 closed by commit %s" % (
        len(ids_open), len(after["open_items"]), len(ids_closed), len(after["closed_items"]), commit[:8]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
