#!/usr/bin/env python3
"""What KIND of signal a net carries, so that the return-path rule can ask the right question of it
(rule RET-001, MESHSAT-862, 16 September 2026; owner instruction of 16 September).

THE PROBLEM THIS EXISTS TO FIX, in the owner's words: a plane under every signal is not a universal rule, and
turning it into one is turning a heuristic into a law. The governing principle is RETURN-PATH ADEQUACY FOR THE
SIGNAL'S SPECTRAL CONTENT. A 12 mm stretch of trace without an adjacent reference is a serious defect under a
USB 3 pair and is nothing at all under a water-level sense line, and the rule as first written could not tell
them apart: it refused board E for SHORE_INHIBIT, WATER_SENSE and TRK_INTVCC, which are an opto inhibit, a
sensor input and an LDO output.

WHAT IT REFUSES TO DO. It does not guess. A net's class comes from evidence or it comes out UNKNOWN, and an
UNKNOWN net makes the gate INCONCLUSIVE rather than passing: this is a classifier, never a way to wave a net
through. The evidence, in order:

  1. THE BOARD'S OWN CLASS. A net in a net class carrying an impedance target is CONTROLLED_IMPEDANCE. Nothing
     is declared for it anywhere: the board says so itself, through the project file the router reads.
  2. THE BOARD'S DECLARATION. `boards/<letter>.json` may carry `signal_classes`, a list of
     {pattern, class, basis} entries. `pattern` is a shell glob over the net name, `class` one of the classes
     below, and `basis` is a SENTENCE SAYING WHY, naming the part or the interface that decides it. An entry
     without a basis is refused, because an exemption nobody can audit is how the four floors of 12 September
     came to have holes in them.
  3. Everything else is UNKNOWN.

THE CLASSES, and what each one means for a return path:

  CONTROLLED_IMPEDANCE  a pair or line with an impedance target. Its return is part of the impedance; a break in
                        the adjacent reference changes the characteristic impedance of that stretch.
  HIGH_SPEED_DIGITAL    a fast single-ended line with no impedance target declared (a clock, a strobe, a bus at
                        tens of MHz). Same question, same criterion.
  CLOCKED_DIGITAL       a bus running at or under a few MHz: I2C, SPI at low rates, UART, an expander's outputs.
                        The edges are slow enough that a short reference break is not a transmission-line event,
                        but a LONG one is still a loop that radiates.
  LOW_SPEED_OR_DC       an enable, an inhibit, a sense line, a thermistor, an analogue level, a rail's feedback.
                        There is no edge to speak of. The question that remains is whether a return path EXISTS
                        at all, not whether it is adjacent.
  UNKNOWN               no evidence. INCONCLUSIVE, and the board is asked to declare it.

WHAT IS NOT DECIDED HERE, and is said out loud rather than buried: the NUMBERS attached to each class are this
project's own, not a standard's. The per-class tolerances live in the registry beside the rule that uses them,
they are marked MUST_JUSTIFY rather than BLOCKER until an authoritative source backs them, and the criterion
for LOW_SPEED_OR_DC is deliberately a different QUESTION (does a reference exist) rather than a looser version
of the same number, so that relaxing it cannot silently relax the fast classes.

Usage: signal_class.py <board.kicad_pcb> [--json]      a report; the gate is intent_checks.py
"""
import os, sys, json, fnmatch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

CLASSES = ("CONTROLLED_IMPEDANCE", "HIGH_SPEED_DIGITAL", "CLOCKED_DIGITAL", "LOW_SPEED_OR_DC", "UNKNOWN")

# The question each class asks of a return path. ADJACENT means a filled reference on a neighbouring copper
# layer along the track; EXISTS means the net's copper is somewhere over or under a reference at all.
QUESTION = {"CONTROLLED_IMPEDANCE": "ADJACENT", "HIGH_SPEED_DIGITAL": "ADJACENT",
            "CLOCKED_DIGITAL": "ADJACENT", "LOW_SPEED_OR_DC": "EXISTS", "UNKNOWN": "UNDECIDED"}

# The tolerance for a break, per class, as (absolute mm, fraction of the net's own length); the larger wins.
# THESE ARE THIS PROJECT'S NUMBERS AND NOT A STANDARD'S. The first pair is the one the 15 September ruling was
# measured with (10 mm or 5 percent, calibrated against board A's anti-pad rows); CLOCKED_DIGITAL is given
# three times that span because a break is judged against the edge and not the bit rate, and the registry
# records both as MUST_JUSTIFY with no source until one is obtained.
TOLERANCE = {"CONTROLLED_IMPEDANCE": (10.0, 0.05), "HIGH_SPEED_DIGITAL": (10.0, 0.05),
             "CLOCKED_DIGITAL": (30.0, 0.15), "LOW_SPEED_OR_DC": (None, None)}


def board_letter(path):
    """The letter from the BOARD TABLE, matched on the board's own stem.

    Not from the directory: the first version read the phase directory's name, and the gate sweep runs every
    gate in a COPY of the project under out/sweep/, so the directory was called "sweep", no declarations were
    found, and all 76 of board E's signal nets came out UNKNOWN and were judged at the strictest bar. The gate
    then read 54 failures on a board with ten. The board table is the one place that says which file belongs to
    which letter, and every other tool in this project reads it for exactly that reason.
    """
    stem = os.path.splitext(os.path.basename(os.path.abspath(path)))[0]
    d = os.path.join(HERE, "boards")
    if not os.path.isdir(d): return ""
    for f in sorted(os.listdir(d)):
        if not f.endswith(".json"): continue
        try: name = (json.load(open(os.path.join(d, f), encoding="utf-8")) or {}).get("name")
        except (ValueError, OSError): continue
        if name and stem == name: return os.path.splitext(f)[0]
    return ""


def declarations(letter):
    """[(pattern, class, basis)] from the board table, validated. A declaration with no basis is refused."""
    p = os.path.join(HERE, "boards", "%s.json" % letter)
    if not letter or not os.path.exists(p): return [], []
    rows = (json.load(open(p)).get("signal_classes") or [])
    out, bad = [], []
    for i, r in enumerate(rows):
        pat, cls, basis = r.get("pattern"), r.get("class"), (r.get("basis") or "").strip()
        if not pat or cls not in CLASSES: bad.append("entry %d: pattern %r class %r is not one of %s" % (i, pat, cls, ", ".join(CLASSES)))
        elif cls == "UNKNOWN": bad.append("entry %d (%s): UNKNOWN cannot be declared, it is the absence of a declaration" % (i, pat))
        elif len(basis) < 12: bad.append("entry %d (%s): no basis. Say WHY this net has that spectral content, naming the part or the interface" % (i, pat))
        else: out.append((pat, cls, basis))
    return out, bad


def classify(b, path=None, targets=None, cls_of=None):
    """{net: (class, basis)} for every net on the board, and the declaration errors.

    `targets` is the set of net-class names carrying an impedance target and `cls_of` maps a net to its class
    name; both come from the caller, which already reads the project file, so this tool opens nothing twice.
    """
    path = path or b.GetFileName()
    letter = board_letter(path)
    decls, bad = declarations(letter)
    out = {}
    ni = b.GetNetInfo()
    for code in range(ni.GetNetCount()):
        name = ni.GetNetItem(code).GetNetname()
        if not name: continue
        bare = name.lstrip("/")
        if targets and cls_of and cls_of(name) in targets:
            out[name] = ("CONTROLLED_IMPEDANCE", "the board's own net class %s carries an impedance target" % cls_of(name))
            continue
        hit = None
        for pat, cls, basis in decls:
            if fnmatch.fnmatchcase(bare, pat) or fnmatch.fnmatchcase(name, pat): hit = (cls, basis); break
        out[name] = hit or ("UNKNOWN", "")
    return out, bad


def limit(cls, length_mm):
    """The break a net of this class may carry, in mm, or None where the question is not a length."""
    t = TOLERANCE.get(cls)
    if not t or t[0] is None: return None
    return max(t[0], t[1] * length_mm)


def main(argv):
    if not argv: print(__doc__); return 2
    import pcbnew, netclass, intent_checks
    path = argv[0]; b = pcbnew.LoadBoard(path)
    it = intent_checks.load_intent(path) if hasattr(intent_checks, "load_intent") else {}
    targets = set((it.get("pair_classes") or {}).keys())
    co = netclass.class_of_map(path) if hasattr(netclass, "class_of_map") else {}
    cls_of = (lambda n: co.get(n, "Default")) if co else None
    m, bad = classify(b, path, targets, cls_of)
    from collections import Counter
    c = Counter(v[0] for v in m.values())
    print("signal_class: %s" % ", ".join("%s %d" % (k, c.get(k, 0)) for k in CLASSES))
    for x in bad: print("  REFUSED %s" % x)
    if "--json" in argv: print(json.dumps({k: {"class": v[0], "basis": v[1]} for k, v in sorted(m.items())}, indent=1))
    else:
        for n in sorted(m):
            if m[n][0] == "UNKNOWN": print("  UNKNOWN %s" % n.lstrip("/"))
    return 1 if bad else 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
