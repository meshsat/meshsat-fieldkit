#!/usr/bin/env python3
"""The obstacle map grows every obstacle by one literal, whatever class it belongs to (MESHSAT-862, 14 Sep 2026).

`CLR = 0.16` is the margin every pad, track, via and rule area is inflated by in the pre-router's occupancy
maps, on every board. `stub_router.py` carried the identical literal beside a class-aware width and via, and on
board C it closed the lanes the panel's own classes had been laid at. Here the same map is what the corridor
search and both leg searches read, so it decides pairs: B19's DIFF100 and USB classes ask for 0.127 mm, the
escape fans the legs must reach their own vias through are laid at 0.127 with 0.127 tracks, and a 0.254 mm lane
loses a quarter of its width to 0.033 mm of margin at each side. 18 of B19's 48 remaining refusals are `no stub
path at via`, which is that geometry exactly.

KiCad's rule is that the clearance between two items is the LARGER of their two classes'. `PAIR_CLASS_CLEAR`
makes the map say that. It is OFF by default, because a map read everywhere is not a thing to change untested,
and these rules hold the two properties that make the measurement meaningful: with the knob off nothing moves
at all, and with it on the clearance in force is part of every cache key, so a map built for one class is never
handed to another.
"""
import os, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = open(os.path.join(TOOLS, "pair_preroute.py")).read()


def t_the_knob_exists_and_is_off():
    assert 'CLASS_CLEAR = os.environ.get("PAIR_CLASS_CLEAR", "0")' in SRC, "the knob does not exist or is not off by default"


def t_with_the_knob_off_the_literal_is_returned_unchanged():
    i = SRC.find("def _obs_clr(")
    body = SRC[i:i + 400]
    assert "if not CLASS_CLEAR: return CLR" in body, (
        "with the knob off the map must be bit for bit what it was, or every number in the record is in doubt")


def t_the_bar_is_the_larger_of_the_two_classes():
    i = SRC.find("def _obs_clr(")
    body = SRC[i:i + 400]
    assert "max(_CLR_NOW[0], v)" in body, "the map does not take the larger of the two nets' clearances"


def t_no_obstacle_is_still_grown_by_the_literal():
    for fn in ("def _pad_stamp(", "def _track_stamp("):
        i = SRC.find(fn)
        body = SRC[i:SRC.find("\n\ndef ", i)]
        for line in body.splitlines():
            if "CLR + " in line and "HOLE_CLR" not in line and "_obs_clr" not in line:
                raise AssertionError("%s still grows an obstacle by the literal: %s" % (fn, line.strip()[:90]))


def t_the_clearance_in_force_is_part_of_every_cache_key():
    for anchor in ("_ALLMAPS.get(ck)", "_MAPS.get(ck)"):
        i = SRC.find(anchor)
        assert i > 0, "a map cache is gone"
        key = SRC[SRC.rfind("ck = ", 0, i):i]
        assert "_CLR_NOW[0]" in key, (
            "a map built at one class's clearance can be handed to another class's pass: %s" % anchor)


def t_the_layer_change_test_is_registered_and_off():
    reg = json.load(open(os.path.join(TOOLS, "agent", "knobs.json")))["knobs"]
    assert "PAIR_LAYER_CHANGE_FIT" in reg, "the layer-change knob is not in the agent's registry"
    assert reg["PAIR_LAYER_CHANGE_FIT"]["default"] == "0", "it is on by default and it costs 14 of B19's pairs"


def t_it_is_registered_and_documented():
    reg = json.load(open(os.path.join(TOOLS, "agent", "knobs.json")))["knobs"]
    assert "PAIR_CLASS_CLEAR" in reg, "the knob is not in the agent's registry"
    assert reg["PAIR_CLASS_CLEAR"]["type"] == "flag", "a flag given a threshold is the defect of 32.149"
    doc = open(os.path.join(TOOLS, "..", "..", "docs", "PAIR-PREROUTER-KNOBS.md")).read()
    assert "PAIR_CLASS_CLEAR" in doc, "the knob map does not carry it"
