#!/usr/bin/env python3
"""Which nets of a board are SIGNALS, for the two return-current gates (MESHSAT-862, owner ruling 15 September 2026 20:15 CEST:
"every signal net" under the return-path rule, "every signal via" under the return-via rule).

A net is a signal unless the board's own data says it carries power or ground:
  - its name is GND, or KiCad's unconnected-pin placeholder;
  - it OWNS A FILLED ZONE (a plane, an island, a band: the rails' locked copper of power_copper.py and the ground pours);
  - it is a rail named in the intent file (out/<stem>-intent.json, the currents of the record);
  - its net class is one of the power classes the placement generators write (HV, NODE, PWR, RAIL, SW, BANK, GNDC), read
    through netclass.class_of from the project file beside the board.
Every exclusion is read off the board, the project file or the intent file: there is no literal list of net names here, so a
renamed rail cannot fall through into the signal set unnoticed (the test suite holds that).

Used by intent_checks.py (rule 1) and return_via.py (rule 2). classify(board, path) returns (signal_names, why) where `why`
maps every excluded net to its reason, so a report can print the denominators."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import netclass

POWER_CLASSES = {"HV", "NODE", "PWR", "RAIL", "SW", "BANK", "GNDC"}


def _assign(path):
    pro = os.path.splitext(path)[0] + ".kicad_pro"
    if not os.path.exists(pro): return {}
    return json.load(open(pro)).get("net_settings", {}).get("netclass_assignments", {}) or {}


def classify(b, path=None, intent_rails=()):
    """(signals, why): `signals` is the set of net names (as the board spells them, with any leading slash) that are
    signals; `why` maps every other named net to the reason it is not."""
    path = path or b.GetFileName(); assign = _assign(path)
    owners = set()
    for z in b.Zones():
        if z.GetIsRuleArea(): continue
        n = z.GetNetname()
        if n: owners.add(n.lstrip("/"))
    rails = {r.lstrip("/") for r in intent_rails}
    signals, why = set(), {}
    ni = b.GetNetInfo()
    for k in range(1, ni.GetNetCount()):
        item = ni.GetNetItem(k)
        if item is None: continue
        n = item.GetNetname(); s = n.lstrip("/")
        if not s: continue
        if s == "GND": why[n] = "ground"; continue
        if s.startswith("unconnected-"): why[n] = "unconnected pin"; continue
        if s in owners: why[n] = "owns a filled zone"; continue
        if s in rails: why[n] = "rail of the intent file"; continue
        c = netclass.class_of(assign, n, "Default")
        if str(c).upper() in POWER_CLASSES: why[n] = "class %s" % c; continue
        signals.add(n)
    return signals, why


def is_signal(netname, signals):
    return netname in signals or ("/" + netname.lstrip("/")) in signals or netname.lstrip("/") in signals
