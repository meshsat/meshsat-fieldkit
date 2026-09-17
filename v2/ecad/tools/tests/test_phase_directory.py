"""The netlist a cross-board contract reads comes from the DECLARED phase directory, and that resolution had
stopped working (MESHSAT-862, 17 September 2026).

`check_contracts.netlist_path` was written on 14 September because the newest `<stem>*/out/<stem>.net` is the
wrong file on a box: forty-one directories match `pcb-b-compute*` there, every one an arm laid down to measure
a knob, and the newest is whichever arm ran last. It reads the phase from `boards/<letter>.json` and finds the
routeflow profile of that phase to learn the project directory.

On 15 September the profiles became ONE PER LETTER with the literal placeholder `<PHASE>`, which a run fills
in from --phase or the board file. From that day `(profile phase) != (declared phase)` was true of every
profile, the loop selected nothing, and every call fell through to the newest-by-mtime fallback the function
exists to avoid. A resolver whose condition can no longer be true is the same shape as the fallback nested
inside the try of the thing it guards (13 September): the code is there, it reads correctly, and it runs never.
"""
import os, re, sys, json, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(TOOLS, "check_contracts.py")


def _resolver(src_text, ecad, here):
    """`netlist_path` alone, with its module's globals given rather than imported: importing
    check_contracts RUNS every contract and writes a verdict, which is how a tool run for a look destroyed
    per-board readings on 17 September."""
    m = re.search(r"^def netlist_path\(stem\):.*?(?=\n\ndef )", src_text, re.S | re.M)
    assert m, "netlist_path is not in check_contracts.py under that name"
    ns = {"os": os, "ECAD": ecad, "NETS": {"X": "pcb-x"}, "__file__": os.path.join(here, "check_contracts.py")}
    exec(m.group(0), ns)
    return ns["netlist_path"]


def _tree(d):
    """A board with two candidate directories: the declared phase's, and an arm's that is NEWER."""
    ecad, here = os.path.join(d, "ecad"), os.path.join(d, "ecad", "tools")
    for p in ("pcb-x/out", "pcb-x-x9/out", "tools/routeflow", "tools/boards"):
        os.makedirs(os.path.join(ecad, p))
    open(os.path.join(ecad, "pcb-x-x9", "out", "pcb-x.net"), "w").write("(export)\n")
    json.dump({"phase": "X9"}, open(os.path.join(here, "boards", "x.json"), "w"))
    json.dump({"board": "pcb-x", "phase": "<PHASE>", "project": "v2/ecad/pcb-x-x9"},
              open(os.path.join(here, "routeflow", "x.json"), "w"))
    # the arm directory is written last, so it is the newest by mtime
    import time; time.sleep(0.02)
    open(os.path.join(ecad, "pcb-x", "out", "pcb-x.net"), "w").write("(export)\n")
    return ecad, here


def t_the_phase_directory_comes_from_the_profile_and_not_from_a_timestamp():
    with tempfile.TemporaryDirectory() as d:
        ecad, here = _tree(d)
        got = _resolver(open(SRC, encoding="utf-8").read(), ecad, here)("pcb-x")
        assert os.path.basename(os.path.dirname(os.path.dirname(got))) == "pcb-x-x9", \
            "the resolver took %r, which is the newest directory rather than the declared phase's" % got


def t_a_profile_that_names_a_real_phase_is_still_held_to_it():
    """The placeholder is what a one-profile-per-letter tree carries; a profile that names an actual phase
    other than the declared one is still not this phase's directory."""
    with tempfile.TemporaryDirectory() as d:
        ecad, here = _tree(d)
        json.dump({"board": "pcb-x", "phase": "X4", "project": "v2/ecad/pcb-x-x9"},
                  open(os.path.join(here, "routeflow", "x.json"), "w"))
        got = _resolver(open(SRC, encoding="utf-8").read(), ecad, here)("pcb-x")
        assert os.path.basename(os.path.dirname(os.path.dirname(got))) == "pcb-x", \
            "a profile for phase X4 answered for the declared X9: %r" % got


def t_every_routeflow_profile_is_reachable_by_the_board_it_routes():
    """The property the fix rests on: one profile per board stem, so naming the board identifies it. If a
    second profile for one stem is ever added, this resolution becomes ambiguous and must be revisited."""
    import glob, collections
    by = collections.defaultdict(list)
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        try: d = json.load(open(p, encoding="utf-8"))
        except ValueError: continue
        if d.get("board"): by[d["board"]].append(os.path.basename(p))
    dupes = {k: v for k, v in by.items() if len(v) > 1}
    assert not dupes, "more than one routeflow profile names the same board: %s" % dupes
    assert by, "no routeflow profile names a board at all"
