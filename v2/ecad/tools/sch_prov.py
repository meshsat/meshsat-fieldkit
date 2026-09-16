#!/usr/bin/env python3
"""Which generator wrote this netlist (MESHSAT-862, 16 September 2026).

THE DEFECT THIS CLOSES, measured today. The set-level cross-board contract check read FAIL on twelve contracts
and every one of them named board B's six PCIe receive coupling capacitors as missing. They are not missing:
board B's own netlist, generated at 04:34, carries `C151` in series on `/PCIE1_RX_P` exactly as the CM5
datasheet's section 2.3.1 asks, and board B's own contract verdict reads PASS on 37 of 37. What failed was the
SET verdict, taken inside board A's sweep tree, where the copy of board B's netlist came from a generation
made before the capacitors existed. Seven boards then carried a FAIL on rule SCH-003 for a defect that had
been fixed six hours earlier.

The existing guard cannot see this case and is right not to: it compares a netlist's timestamp with its own
schematic's, and in a copied tree both are old together. Age is not the property that matters. The property
that matters is WHICH GENERATOR WROTE IT, and until now nothing recorded that.

So a netlist gets a sidecar naming the generator that produced it, by content: a sha256 over
`gen_sch_<letter>.py` and the two files every schematic passes through, `kisch.py` (the drawing engine) and
`intent.py` (the rails and pair classes). A reader that runs under a different content is reading about a
different design and says so, rather than deciding.

WHAT IT DELIBERATELY DOES NOT DO. It does not make a netlist valid: a sidecar says which code wrote the file,
not that the file is right. And it never guesses: a netlist with no sidecar is UNKNOWN, which for a gate means
INCONCLUSIVE, because "written by something we cannot name" is exactly the state that produced the twelve.

Usage: sch_prov.py write <netlist.net> <letter>     after the netlist is exported
       sch_prov.py read  <netlist.net>              prints the record, exit 1 if it is stale or absent
"""
import os, sys, json, glob, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# The files whose content decides a netlist. Anything else in the tools tree may change without changing what
# a schematic connects; these three cannot.
def generator_files(letter, tools=None):
    t = tools or HERE
    fs = [os.path.join(t, "gen_sch_%s.py" % letter.lower()), os.path.join(t, "kisch.py"), os.path.join(t, "intent.py")]
    return [f for f in fs if os.path.exists(f)]


def generator_sha(letter, tools=None):
    """The identity of the generator, by content. Returns None when the generator is not in this tree at all,
    which is itself an answer: a tree that cannot regenerate a board cannot judge whether its netlist is current."""
    fs = generator_files(letter, tools)
    if not fs: return None
    h = hashlib.sha256()
    for f in sorted(fs):
        h.update(os.path.basename(f).encode())
        h.update(open(f, "rb").read())
    return h.hexdigest()[:16]


def path_for(netlist):
    return netlist + ".prov.json"


def write(netlist, letter, tools=None):
    sha = generator_sha(letter, tools)
    sch = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(netlist))),
                       os.path.basename(netlist)[:-4] + ".kicad_sch")
    rec = {"what": "the generator that wrote this netlist, by content",
           "letter": letter.lower(), "netlist": os.path.basename(netlist),
           "generator_sha": sha,
           "generator_files": [os.path.basename(f) for f in generator_files(letter, tools)],
           "schematic_sha256": (hashlib.sha256(open(sch, "rb").read()).hexdigest()[:32] if os.path.exists(sch) else None),
           "taken": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")}
    json.dump(rec, open(path_for(netlist), "w"), indent=1)
    return rec


def read(netlist):
    p = path_for(netlist)
    if not os.path.exists(p): return None
    try: return json.load(open(p, encoding="utf-8"))
    except Exception: return None


def current(netlist, letter, tools=None):
    """(True, why) when this netlist was written by the generator in THIS tree; (False, why) otherwise."""
    rec = read(netlist)
    if rec is None:
        return False, ("no provenance beside %s: nothing says which generator wrote it, and a contract judged "
                       "against a netlist of unknown origin is what produced the twelve false failures of "
                       "16 September" % os.path.basename(netlist))
    want = generator_sha(letter, tools)
    if want is None:
        return False, "this tree has no gen_sch_%s.py, so it cannot say whether that netlist is current" % letter.lower()
    if rec.get("generator_sha") != want:
        return False, ("%s was written by generator %s and this tree's generator is %s: the two describe "
                       "different designs" % (os.path.basename(netlist), rec.get("generator_sha"), want))
    return True, "%s was written by this tree's own generator (%s)" % (os.path.basename(netlist), want)


def main(argv):
    if len(argv) >= 3 and argv[0] == "write":
        rec = write(argv[1], argv[2])
        print("sch_prov: %s written by generator %s (%s)" % (rec["netlist"], rec["generator_sha"], ", ".join(rec["generator_files"])))
        return 0
    if len(argv) >= 2 and argv[0] == "read":
        letter = argv[2] if len(argv) > 2 else (os.path.basename(argv[1]).split("-")[1] if "-" in os.path.basename(argv[1]) else "")
        ok, why = current(argv[1], letter)
        print("sch_prov: %s" % why)
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
