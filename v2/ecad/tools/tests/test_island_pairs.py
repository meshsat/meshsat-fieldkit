#!/usr/bin/env python3
"""The closest two pieces of two islands can be the one place a closure cannot go (MESHSAT-862, 14 Sep 2026).

`direct_close.py` reads the DRC's own unconnected pair, walks it out to the two ISLANDS of the net's copper,
and then takes the closest pair of pieces between them. On A27's `/VBUS20` that pair is pad 3 and pad 1 of the
same QFN, 0.800 mm apart with pad 2 (`/CH_ACN`) between them: every shape bridges pad 2's solder mask and the
tool printed "no shape the DRC accepts" on three runs. The second-closest pair is the two islands' own vias,
1.635 mm apart, on a back side that carries under six percent of this board's copper.

"Further but legal beats closer but illegal" was already written into this tool for the hop at a walled-in pad.
It was never applied to the PAIRING, only to the anchor at one end of it. These rules hold the generalisation:
the ladder is one function used by every attempt, the further pairs are offered in order of distance, the count
is an option rather than a literal, and a net with plane-sized copper is not walked this way at all.
"""
import os

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DC = open(os.path.join(TOOLS, "direct_close.py")).read()


def t_there_is_one_shape_ladder_and_every_attempt_uses_it():
    assert "def _shapes(" in DC, "the ladder is not a function"
    # the first attempt, the hop, and the island pairs must all go through it
    assert DC.count("_shapes(") >= 4, "some attempt still builds its own shapes, which is how two ladders drift apart"
    for stale in ('_sh = [("from %s, direct"', 'shapes = [("direct"'):
        assert stale not in DC, "a second copy of the ladder is still in the file: %s" % stale


def t_further_pairs_of_the_two_islands_are_offered():
    assert "ca_cb" in DC, "the two islands are not carried past the closest-pair choice"
    i = DC.find("if got is None and ca_cb is not None:")
    assert i > 0, "a refused closure never looks past the closest pair"
    body = DC[i:i + 3400]
    assert "_cands.sort(key=lambda c: c[0])" in body, "the further pairs are not tried in order of distance"
    assert "ISLAND_TRIES" in body, "the number of further pairs tried is not bounded"


def t_the_count_is_an_option_and_not_a_literal():
    assert 'ISLAND_TRIES = int(opt("island-tries"' in DC, "the cap cannot be given on the command line"
    assert "--island-tries" in DC.split('"""')[1], "the option is not documented in the usage line"


def t_a_plane_sized_net_is_not_walked_pair_by_pair():
    i = DC.find("if got is None and ca_cb is not None:")
    body = DC[i:i + 3400]
    assert "len(_items) > 600" in body, (
        "every pair of every piece of a plane net would be built, which is quadratic in a net with thousands "
        "of pieces and answers nothing: a plane's open is not a two-island gap")


def t_the_further_pairs_are_judged_the_same_way():
    i = DC.find("if got is None and ca_cb is not None:")
    body = DC[i:i + 3400]
    assert "got = _try(" in body, "an island pair is accepted without the DRC deciding"
    assert "MAXD" in body, "an island pair beyond the tool's own reach is still offered"


def t_a_trial_board_is_built_in_its_own_process():
    """A27's /VBUS20 took the island ladder to a fortieth LoadBoard-fill-SaveBoard in one interpreter and
    pcbnew died of a segmentation fault, after the run had already closed /POE_SW2 and written it to disk.
    A crash in one trial must be a refused shape, not the end of the pass."""
    assert 'if argv[:1] == ["--lay"]' in DC, "there is no one-trial mode to spawn"
    assert "def lay(" in DC, "the trial board is not built by a function of its own"
    i = DC.find("def _try(")
    body = DC[i:i + 2200]
    assert '"--lay"' in body and "subprocess.run([sys.executable" in body, (
        "the judging process still lays the trial board itself, so one pcbnew crash ends the whole pass")
    assert "pcbnew.LoadBoard" not in body, "the judge still loads a board it is about to throw away"
    assert "could not be built" in body, "a crashed trial is not reported as a refused shape"


def t_every_shared_layer_is_offered_not_only_the_first():
    """A27's /VBUS20: both anchors of its cheapest island pair are THROUGH VIAS, so every copper layer is
    shared, and the run was laid on cm_[0], which is F.Cu, straight back through the QFN pad row that
    refused it. The back side of that board carries under six percent of its copper."""
    i = DC.find("def _shapes(")
    body = DC[i:DC.find("\n        tried += 1", i)]
    assert "for Lc in order:" in body, "the ladder is built on one shared layer only"
    assert "order = [L_] + [l for l in cm_ if l != L_]" in body, (
        "the layer the anchors prefer must still be tried first, and the rest after it")
