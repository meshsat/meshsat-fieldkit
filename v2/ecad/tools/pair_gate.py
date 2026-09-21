#!/usr/bin/env python3
"""Which _P/_N pairs the 1 mm length rule is about (decision 47, ruled 21 September 2026).

THE DEFECT. Both board gates enumerate every net of the netlist whose name ends `_P` or `_N` and holds the
pair to a 1.00 mm length match, and `pair_match.sh` refuses the finish on any line that reads WARN. Board A's
ten LM5176 current-sense taps were given `_P`/`_N` names when the ISNS filter went in on 18 September, so the
gate started holding a KELVIN TAP to a differential pair's rule. A Kelvin tap's two legs run to OPPOSITE ENDS
of a shunt by construction: `PA_ISNS` reads a 58.38 mm mismatch and no meander can close it, because closing
it would mean running the two sense lines together, which is the one thing a Kelvin connection must not do.
Every board A finish since has ended PAIRS NOT MATCHED for that reason, which is a gate refusing a board for
satisfying the requirement the taps were added to satisfy.

THE RULING (the session's, on the evidence in the tree; appendix 32.350 and decision 47). The 1 mm rule is
about a pair whose CLASS declares an impedance target: that is what a differential pair is, and the target is
where the matching requirement comes from. A `_P`/`_N` name is a naming convention and is not a claim about
the copper. So a pair is JUDGED when either leg is assigned to a net class the intent declares with a
`z_diff` or `z_se`, and MEASURED AND REPORTED otherwise.

FAIL CLOSED. Where the class table or the intent cannot be read, the pair is judged as before. A declaration
that cannot be found must never be the reason a rule stops applying, which is `sense_reach`'s lesson of this
morning in another place: an undeclared zero is not a pass.

REVERSAL: delete the `pair_gate.judged` call from `check_pcb_a.py` and `check_pcb_b.py` and both gates hold
every `_P`/`_N` pair to 1.00 mm again, which is what they did before this commit.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)


def judged(pair, class_of, pair_classes):
    """Is this pair one the length rule is about? -> (bool, reason)

    `pair` is the stem without `_P`/`_N`. `class_of` is a callable taking a net name and returning its class
    name or None. `pair_classes` is the intent's map of class name to its impedance targets.
    """
    if class_of is None or pair_classes is None:
        return True, "judged: the class table or the intent could not be read, so the rule applies as before"
    targets = []
    for leg in (pair + "_P", pair + "_N"):
        cn = class_of(leg)
        if not cn:
            continue
        z = pair_classes.get(cn) or {}
        if z.get("z_diff") is not None or z.get("z_se") is not None:
            targets.append("%s in %s" % (leg, cn))
    if targets:
        return True, "judged: " + ", ".join(targets)
    return False, ("not judged: neither leg is in a net class that declares an impedance target, so this is a "
                   "two-net name and not a controlled pair (decision 47; a Kelvin tap's legs run to opposite "
                   "ends of its shunt)")


def from_board(board_path):
    """(class_of, pair_classes) for a board file, or (None, None) when either cannot be read."""
    try:
        pro = os.path.splitext(os.path.abspath(board_path))[0] + ".kicad_pro"
        ns = json.load(open(pro)).get("net_settings", {})
        assign = ns.get("netclass_assignments") or {}
        pats = [(e.get("pattern"), e.get("netclass")) for e in (ns.get("netclass_patterns") or [])]
    except Exception:
        return None, None
    try:
        import intent as _intent
        it = _intent.load(board_path)
        pair_classes = (it or {}).get("pair_classes")
    except Exception:
        pair_classes = None
    if pair_classes is None:
        return None, None

    import netclass as _nc

    def class_of(net):
        c = _nc.class_of(assign, net)
        if c:
            return c
        for pat, cls in pats:
            if not pat or not cls:
                continue
            try:
                if re.fullmatch(pat.replace("*", ".*"), net) or re.fullmatch(pat.replace("*", ".*"), "/" + net):
                    return cls
            except re.error:
                continue
        return None

    return class_of, pair_classes
