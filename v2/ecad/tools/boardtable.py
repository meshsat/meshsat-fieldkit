#!/usr/bin/env python3
"""The board table as the one place a board's own numbers live (MESHSAT-862, 16 September 2026).

`boards/<letter>.json` already carries what differs between boards for the chains. This is the same file read
from Python, for the facts a GATE has to assert.

WHY IT EXISTS. Six board gates each carried their board's copper layer count as a literal, so a layer decision
meant editing a gate's source. On 12 September the four-layer experiment on board A read "netlist_board 2004
of 2004, check_pcb_a 510 of 511, the one failure being the gate asserting six layers", and on 16 September the
six-layer measurement of board C read three failures of which one was the gate asserting four. A measurement
whose only failure is the gate describing the previous decision is a measurement nobody can read at a glance,
and under the P0 ruling of 11 September every board's layer count is open, so this will keep happening until
the number lives in a declaration.

A gate asks for a value it needs; a board that does not declare it gets the fallback the gate names, so no
board is refused for a field nobody has written yet.
"""
import os, json

HERE = os.path.dirname(os.path.abspath(__file__))


def table(letter):
    p = os.path.join(HERE, "boards", "%s.json" % letter)
    if not letter or not os.path.exists(p): return {}
    try: return json.load(open(p, encoding="utf-8")) or {}
    except (ValueError, OSError): return {}


def value(letter, key, default=None):
    v = table(letter).get(key)
    return default if v is None else v


def letter_for(board_path):
    """The letter whose table names this board file's stem. The stem, never the directory: a board is judged in
    a copy directory more often than in its own (the gate sweep, the re-finish trees, the experiment arms)."""
    stem = os.path.splitext(os.path.basename(os.path.abspath(board_path)))[0]
    d = os.path.join(HERE, "boards")
    if not os.path.isdir(d): return ""
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"): continue
        if table(os.path.splitext(f)[0]).get("name") == stem: return os.path.splitext(f)[0]
    return ""
