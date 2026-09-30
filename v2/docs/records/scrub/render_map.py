#!/usr/bin/env python3
"""Renders records/scrub/MAP.md from map_tree.tsv (apply_scrub.py) and map_reissue.tsv (reissue_snapshots.py).

Usage: render_map.py [--check]      --check exits 1 when MAP.md is not what the two tables give.
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_lib as S

TOKENS = [(S.RUNNER, "`<worktrees>` (the folder that holds the worktrees), `<repo>` (the main clone), `<projects>` (the folder that holds the MeshSat repositories), `<runner home>`; in a script, a path derived from an environment variable whose default sits under the home directory, or from git"),
          (S.TEMP, "`/tmp/<scratchpad>` (a session's scratch folder), `/tmp/<session temp>` (a session's temporary root); in a script, a path derived from `$SCRATCH` or `$TMPDIR`, or read from the transcript the script replays"),
          (S.HOSTC, "\"the runner\""),
          (S.LAPTOPC, "\"the laptop\", or nothing where the sentence already names the laptop session"),
          (S.LHOMEC, "`<laptop home>` (in XML written escaped); in a script, a path derived from an environment variable whose default sits under the home directory")]


def cell(s): return str(s).replace("|", "\\|")


def render():
    tree = list(csv.DictReader(open(os.path.join(HERE, "map_tree.tsv"), encoding="utf-8"), delimiter="\t"))
    re_ = list(csv.DictReader(open(os.path.join(HERE, "map_reissue.tsv"), encoding="utf-8"), delimiter="\t"))
    L = ["# The scrub's map: every replacement, by file, line and token class", "",
         "MESHSAT-1357, 30 September 2026. Rendered by `render_map.py` from `map_tree.tsv` (written by `apply_scrub.py`) "
         "and `map_reissue.tsv` (written by `reissue_snapshots.py`); `README.md` beside it gives the decisions. A removed "
         "value is never written here: each row names the token class and the token that replaced it. The removed values "
         "stay in the repository's history, which the owner did not authorize rewriting.", "",
         "## Token classes", "", "| Class | Written as |", "|---|---|"]
    L += ["| %s | %s |" % (c, t) for c, t in TOKENS]
    cls = [r["token class"] for r in tree if r["token class"] in S.CLASSES]
    L += ["", "## The tree", "",
          "%d replacement(s) in %d file(s) (%s), and %d row(s) of `v2/docs/records/README.md` re-pinned. The line is the "
          "file's line after the scrub." % (len(cls), len({r["file"] for r in tree if r["token class"] in S.CLASSES}),
                                            ", ".join("%s %d" % (c, cls.count(c)) for c in S.CLASSES if cls.count(c)),
                                            sum(1 for r in tree if r["token class"] == "(re-pin)")), "",
          "| File | Line | Token class | Written as | Note | Treatment |", "|---|---|---|---|---|---|"]
    for r in tree:
        L.append("| `%s` | %s | %s | %s | %s | %s |" % (r["file"], r["line"], r["token class"], cell(
            "`%s`" % r["token"] if r["token"].startswith(("<", "/", "(")) else r["token"]), cell(r["note"]), cell(r["treatment"])))
    L += ["", "## The reissued snapshots", "",
          "Each file is the one inside the reissue (the redaction commit's blob); the line is its line there. The files a "
          "snapshot keeps as it carried them are named in its version record, `v2/docs/handover/RELEASE-<version>.md`.", ""]
    for snap in sorted({r["snapshot"] for r in re_}, key=lambda s: [int(x) if x.isdigit() else x for x in s.replace("-R", ".").split(".")]):
        rows = [r for r in re_ if r["snapshot"] == snap]
        L += ["### %s" % snap, "", "| File | Line | Token class | Written as | Note |", "|---|---|---|---|---|"]
        for r in rows:
            L.append("| `%s` | %s | %s | %s | %s |" % (r["file"], r["line"], r["token class"], cell(
                "`%s`" % r["token"] if r["token"].startswith(("<", "/", "(")) else r["token"]), cell(r["note"])))
        L.append("")
    return "\n".join(L).rstrip("\n") + "\n"


def main(argv):
    p = os.path.join(HERE, "MAP.md")
    t = render()
    assert not S.count(t), "the map would carry a pattern"
    if "--check" in argv:
        ok = os.path.exists(p) and open(p, encoding="utf-8").read() == t
        print("render_map: MAP.md %s" % ("current" if ok else "out of date")); return 0 if ok else 1
    open(p, "w", encoding="utf-8").write(t)
    print("render_map: wrote MAP.md (%d lines)" % t.count("\n"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
