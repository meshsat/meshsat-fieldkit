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
`gen_sch_<letter>.py` and every input of the schematic (since 26 September 2026 the modules it imports, the
footprint generators and lands, and the generator environment the board table declares; see `_labelled_inputs`). A reader that runs under a
different content is reading about a different design and says so, rather than deciding.

WHAT IT DELIBERATELY DOES NOT DO. It does not make a netlist valid: a sidecar says which code wrote the file,
not that the file is right. And it never guesses: a netlist with no sidecar is UNKNOWN, which for a gate means
INCONCLUSIVE, because "written by something we cannot name" is exactly the state that produced the twelve.

Usage: sch_prov.py write <netlist.net> <letter>     after the netlist is exported
       sch_prov.py read  <netlist.net>              prints the record, exit 1 if it is stale or absent
"""
import os, sys, json, glob, hashlib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
# The files whose content decides a netlist. Anything else in the tools tree may change without changing what
# a schematic connects; these cannot.
#
# WIDENED ON 26 SEPTEMBER 2026 (MESHSAT-1357, finding W7-F4). The identity was gen_sch_<x>.py, kisch.py and
# intent.py, and commit c26f6a22 (15 September) rewrote all six schematics while changing only schlayout.py and
# gen_sch_b.py, so five sidecars kept reading CURRENT over schematics their identity did not describe. It is now
# every input the schematic is made from, found by reading the generator rather than by a list kept beside it:
#   * the generator and every tools-local module it imports, transitively, by AST (schlayout.py, which writes the
#     connectivity-bearing wires; kisch.py; intent.py; idc_pads.py, which picks the IDC land; and whatever a
#     generator imports next);
#   * the footprint generators (gen_footprints_*.py) and every land in ../meshsat.pretty, because the netlist
#     names those lands and the board is placed on them;
#   * the generator environment boards/<letter>.json declares (`gen_env`, e.g. IDC_PADS), and ONLY that field of the
#     table: full.sh hands `gen_env` to the generator and nothing in any generator's import closure opens the table
#     (tests/test_sch_prov.py holds both by parsing). The rest of the table is routing, placement and stackup
#     (`pair_env`, `copper_layers`, `return_reach_mm`, the phase), and hashing the whole file made a routing-only
#     edit, such as the layer decisions of 25 September, stale every sidecar until a KiCad box regenerated it.
# NOT in it, and recorded by the regeneration parity run instead: the KiCad build and its symbol and footprint
# trees, which live outside this repository (W7's box record names them).
IDENTITY_SINCE = "2026-09-26"
GEN_ENV = "#gen_env"          # the label suffix of an input that is one field of a file, not the whole file


def _input_bytes(label, path):
    """The bytes an input contributes: the whole file, or for the board table its `gen_env` field alone, in one
    canonical spelling. A table that does not parse contributes its raw bytes, so a broken table still moves the
    identity rather than reading as an empty environment."""
    raw = open(path, "rb").read()
    if not label.endswith(GEN_ENV): return raw
    try: env = json.loads(raw.decode("utf-8")).get("gen_env") or {}
    except (ValueError, UnicodeDecodeError, AttributeError): return raw
    return json.dumps(env, sort_keys=True, separators=(",", ":")).encode()


def _local_imports(path, tools):
    """The tools-local modules one Python file imports, read from its AST (a detector parses, it never greps)."""
    import ast
    try: tree = ast.parse(open(path, encoding="utf-8").read())
    except (OSError, SyntaxError, ValueError): return set()
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): names |= {a.name.split(".")[0] for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level: names.add(n.module.split(".")[0])
        elif isinstance(n, ast.Call) and getattr(n.func, "id", "") == "__import__" and n.args \
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            names.add(n.args[0].value.split(".")[0])
    return {os.path.join(tools, m + ".py") for m in names if os.path.isfile(os.path.join(tools, m + ".py"))}


def _labelled_inputs(letter, tools=None):
    """[(label, path)] of every input of board <letter>'s schematic, or [] when this tree has no generator for it.
    The label is stable across trees (a basename in the tools directory, `boards/<x>.json`, `meshsat.pretty/<f>`),
    so two identical trees agree and a sidecar can name the input that moved."""
    t = tools or HERE
    own = os.path.join(t, "gen_sch_%s.py" % letter.lower())
    # THE BOARD'S OWN GENERATOR DECIDES WHETHER THERE IS AN IDENTITY AT ALL. The shared files exist in every
    # tree, so listing them alone would give board E5, which has no schematic generator, a perfectly stable
    # "identity" made of files that say nothing about it.
    if not os.path.exists(own): return []
    # the generator, plus the two engine files every schematic passes through whether or not a generator names
    # them directly (the identity before 26 September was exactly these three), then everything they import
    seen, todo = set(), [own] + [f for f in (os.path.join(t, "kisch.py"), os.path.join(t, "intent.py")) if os.path.exists(f)]
    while todo:                                     # the transitive import closure inside the tools directory
        f = todo.pop()
        if f in seen: continue
        seen.add(f); todo += sorted(_local_imports(f, t) - seen)
    out = [(os.path.basename(f), f) for f in sorted(seen)]
    out += [(os.path.basename(f), f) for f in sorted(glob.glob(os.path.join(t, "gen_footprints_*.py")))
            if f not in seen]
    bj = os.path.join(t, "boards", "%s.json" % letter.lower())
    if os.path.isfile(bj): out.append(("boards/%s.json%s" % (letter.lower(), GEN_ENV), bj))
    pretty = os.path.join(os.path.dirname(os.path.abspath(t)), "meshsat.pretty")
    if os.path.isdir(pretty):
        out += [("meshsat.pretty/" + n, os.path.join(pretty, n)) for n in sorted(os.listdir(pretty))
                if os.path.isfile(os.path.join(pretty, n))]
    return sorted(out)


def generator_files(letter, tools=None):
    return [p for _l, p in _labelled_inputs(letter, tools)]


def generator_file_shas(letter, tools=None):
    """{label: sha256_16} of every input, so a stale sidecar can say WHICH input moved."""
    return {lab: hashlib.sha256(_input_bytes(lab, p)).hexdigest()[:16] for lab, p in _labelled_inputs(letter, tools)}


def generator_sha(letter, tools=None):
    """The identity of the generator, by content. Returns None when the generator is not in this tree at all,
    which is itself an answer: a tree that cannot regenerate a board cannot judge whether its netlist is current."""
    fs = _labelled_inputs(letter, tools)
    if not fs: return None
    h = hashlib.sha256()
    for lab, f in fs:
        h.update(lab.encode())
        h.update(_input_bytes(lab, f))
    return h.hexdigest()[:16]


def letter_for(stem, tools=None):
    """The board letter of a project stem, from the board table rather than from the stem's own spelling.

    `pcb-e1-dock` is board E and the second field of its name is `e1`, so taking that field verbatim asked for
    a generator `gen_sch_e1.py` that does not exist, recorded a provenance with no generator sha, and made
    every contract that names board E read UNKNOWN GENERATOR (16 September 2026, the first run of the one-tree
    sweep). The board table declares `name` per letter, which is the authority; trimming the digits is the
    fall-back for a tree that has no table."""
    t = tools or HERE
    for f in sorted(glob.glob(os.path.join(t, "boards", "*.json"))):
        try:
            if json.load(open(f, encoding="utf-8")).get("name") == stem:
                return os.path.basename(f)[:-5]
        except Exception: pass
    # No entry in the table: the second field VERBATIM, digits and all. Trimming them would fold
    # `pcb-e5-block`, the bare dock block, into board E, and a wrong letter here reads as "current" against
    # another board's generator, which is worse than the honest answer that this tree cannot say.
    parts = stem.split("-")
    return parts[1] if len(parts) > 1 else stem


def path_for(netlist):
    return netlist + ".prov.json"


def write(netlist, letter, tools=None):
    sha = generator_sha(letter, tools)
    sch = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(netlist))),
                       os.path.basename(netlist)[:-4] + ".kicad_sch")
    rec = {"what": "the generator that wrote this netlist, by content",
           "letter": letter.lower(), "netlist": os.path.basename(netlist),
           "generator_sha": sha,
           "identity_since": IDENTITY_SINCE,
           "generator_files": [lab for lab, _p in _labelled_inputs(letter, tools)],
           "generator_file_sha": generator_file_shas(letter, tools),
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
        # SAY WHICH INPUT MOVED, or why nothing can say (26 September 2026). A sidecar written before the identity
        # was widened names three files and nothing about schlayout.py, the lands or the board table, so it cannot
        # be current under the wider identity whatever its schematic is; it is re-written after a regeneration
        # parity run shows the netlist is still what the generator produces (W7, box 52646493, 25 September).
        old = rec.get("generator_file_sha")
        if not old:
            return False, ("%s carries a sidecar written under the three-file identity (%s) before %s; it says "
                           "nothing about schlayout.py, idc_pads.py, the footprint lands or boards/%s.json's gen_env, so it "
                           "cannot be current. Regenerate, or re-write it with sch_prov.py after a regeneration "
                           "parity run" % (os.path.basename(netlist), ", ".join(rec.get("generator_files") or []),
                                           IDENTITY_SINCE, letter.lower()))
        now = generator_file_shas(letter, tools)
        moved = sorted(k for k in set(old) | set(now) if old.get(k) != now.get(k))
        return False, ("%s was written by generator %s and this tree's generator is %s: the two describe "
                       "different designs (changed inputs: %s)" % (os.path.basename(netlist), rec.get("generator_sha"),
                                                                    want, ", ".join(moved[:8]) or "none named"))
    return True, "%s was written by this tree's own generator (%s)" % (os.path.basename(netlist), want)


def main(argv):
    if len(argv) >= 2 and argv[0] == "write":
        # The caller may give the LETTER or the STEM; a stem is resolved through the board table, because a
        # stem's own second field is not always the letter (`pcb-e1-dock` is board E).
        who = argv[2] if len(argv) > 2 else os.path.basename(argv[1])[:-4]
        letter = who if len(who) <= 2 and "-" not in who else letter_for(who.replace(".net", ""))
        rec = write(argv[1], letter)
        _py = [f for f in rec["generator_files"] if not f.startswith("meshsat.pretty/")]
        print("sch_prov: %s written by generator %s (%s, and %d land(s) in meshsat.pretty)"
              % (rec["netlist"], rec["generator_sha"], ", ".join(_py), len(rec["generator_files"]) - len(_py)))
        return 0
    if len(argv) >= 2 and argv[0] == "read":
        letter = argv[2] if len(argv) > 2 else (os.path.basename(argv[1]).split("-")[1] if "-" in os.path.basename(argv[1]) else "")
        ok, why = current(argv[1], letter)
        print("sch_prov: %s" % why)
        return 0 if ok else 1
    print(__doc__)
    return 2


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
