#!/usr/bin/env python3
"""A BOARD FILE IS READ AS A DIFF, SO ITS FORMAT IS PART OF ITS CONTENT (20 September 2026).

`boards/<letter>.json` is where a board's measured facts and the reasons behind them are kept, and every one
of them is added by a session writing the file back out. Tonight one of those writes used `indent=2` where
all seven files are written at `indent=1`, and adding two keys produced a 1,284-line diff: 643 insertions and
641 deletions, of which two lines were the actual change. Nobody reviewing that diff can see what moved, and
the pre-commit check passes it, so the reformat would have gone in with the measurement buried inside it.

This is the formatting cousin of the rule the record already carries from 19 September, that a board file is
edited by ADDING to its list and never by rewriting it. The fix is to pin the format so that the next write
at the wrong indent fails here rather than in a review nobody can do.

Two fixtures, both ways: the ACCEPTABLE one is the seven committed files, which must all pass; the DEFECTIVE
one is a file written at another indent, which must be caught.
"""
import os, sys, json, glob, collections, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _canonical(raw):
    d = json.loads(raw, object_pairs_hook=collections.OrderedDict)
    return json.dumps(d, indent=1, ensure_ascii=False) + "\n"


def t_every_board_file_is_written_the_way_the_others_are():
    """ACCEPTABLE: the seven committed board files."""
    bad = []
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        raw = open(p, encoding="utf-8").read()
        if raw != _canonical(raw):
            bad.append("%s: not json.dumps(..., indent=1, ensure_ascii=False) plus a newline" % os.path.basename(p))
    assert not bad, ("a board file is reviewed as a diff and a reformat buries the measurement inside it: "
                     + "; ".join(bad))


def t_a_reformatted_board_file_is_caught():
    """DEFECTIVE: the same content at another indent, which is what produced tonight's 1,284-line diff."""
    d = collections.OrderedDict([("name", "pcb-a-power"), ("letter", "a"),
                                 ("_why", "a fact with its reason")])
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "a.json")
        open(p, "w", encoding="utf-8").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
        raw = open(p, encoding="utf-8").read()
        assert raw != _canonical(raw), "an indent=2 board file was not distinguished from an indent=1 one"
        # and the canonical form of the same content is what the rule asks for
        assert _canonical(raw) == json.dumps(d, indent=1, ensure_ascii=False) + "\n"
