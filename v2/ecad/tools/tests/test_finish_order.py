#!/usr/bin/env python3
"""One finish, its stage order, and the profile that dispatches it.

MESHSAT-862, 11 September 2026. There were fifteen finish_*.sh, 728 lines, clones of one another with a board
name changed, and the drift between the clones was not cosmetic:

  * FIVE ran the stub router BEFORE the clean-up. The order established with B13 on 5 September is clean up
    first, then the stub router, then a zone refill, then the check, and it has two written reasons, both paid
    for: the stub router's closing via counts as a plane clearance violation when the zone fill is stale, so a
    legal closure is reverted; and `cleanup_dangling.py` running afterwards can remove the very via the closure
    used. The five with the wrong order are the boards whose deliverables shipped.
  * TWELVE OF TWELVE never ran `netlist_board.py`, so a board could pass every gate carrying a phantom net or a
    footprint the netlist does not have. Found by a reviewer, not by a gate, which is why this file exists.
  * Nine never ran `pruned_gate.py`, four never ran `pour_stitch.py`, three never matched pairs.

The twelve are retired into `finish.sh`, which carries the order once and is driven by `boards/<letter>.json`.
These tests hold the collapse in place: the order, every gate present, and each routeflow profile agreeing with
itself about which phase it cuts (five did not, and one of those would have had the supervisor verify a folder
the finish never wrote).
"""
import os, re, sys, json, glob

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINISH = os.path.join(TOOLS, "finish.sh")

STAGES = ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch", "stub_router")

# Every gate that decides whether a board is finished. A gate absent from the finish is a bar nothing tests.
# Every gate that decides whether a board is finished. `stitch_prune.py` is NOT one: it is a cleanup that cuts
# copper, it is declared per board and off everywhere, and listing a cleanup among the gates is the drift this
# file exists to catch.
GATES = ("hardset.py", "check_pcb_", "dc_drop.py", "impedance_check.py", "netlist_board.py", "check_contracts.py",
         "pruned_gate.py", "pair_match.sh", "quality_pass.sh", "silk_fix_all.py", "stackup_write.py")


def _order(path):
    """The stages of a script, in the order they first appear, comments excluded."""
    seen, out = set(), []
    for line in open(path, errors="replace"):
        t = line.strip()
        if t.startswith("#"): continue
        for s in STAGES:
            if re.search(r"\b%s\.py" % s, t) and s not in seen: seen.add(s); out.append(s)
    return out


def t_the_one_finish_cleans_up_before_it_stubs():
    o = _order(FINISH)
    assert "stub_router" in o, o
    for before in ("unknot", "cleanup_dangling", "zone_pad_via", "pour_stitch"):
        assert before in o, (before, o)
        assert o.index(before) < o.index("stub_router"), \
            "%s must run before the stub router: %s" % (before, o)


def t_the_finish_runs_every_gate():
    """The reviewer's finding as a rule: netlist_board.py was in finish.sh and in no clone, so the boards that
    shipped were never checked against their own netlists."""
    t = "".join(l for l in open(FINISH, errors="replace") if not l.strip().startswith("#"))
    missing = [g for g in GATES if g not in t]
    assert not missing, "finish.sh does not run %s" % missing


def t_a_gate_that_fails_stops_the_finish():
    """A gate whose exit code nothing reads is decoration. Every gate here must be followed by a test of its
    status; `stop` is the one way out."""
    t = open(FINISH, errors="replace").read()
    for g, var in (("dc_drop.py", "DC"), ("impedance_check.py", "IM"), ("netlist_board.py", "NB"), ("check_pcb_", "GATE")):
        assert re.search(r'\[ "\$%s" -eq 0 \] \|\| stop ' % var, t), "%s runs but its status %s is never tested" % (g, var)


def t_no_board_finish_clone_is_left():
    """The clones are retired, and a new one must not appear: the drift they carried is what these tests are for.
    finish_board.sh (the exporter), finish_a18.sh (a one-off re-export of a routed board) and finish_b_after.sh
    (a wrapper on stub_and_finish.sh) are different jobs and are named explicitly."""
    KEEP = {"finish_board.sh", "finish_a18.sh", "finish_b_after.sh", "finish.sh"}
    found = {os.path.basename(p) for p in glob.glob(os.path.join(TOOLS, "finish*.sh"))} - KEEP
    assert not found, "a per-board finish clone is back: %s (the finish is tools/finish.sh, driven by boards/<letter>.json)" % sorted(found)


def t_every_board_has_a_finish_block_with_every_key():
    need = {"stub_layers", "pour_nets", "pair_match", "pair_audit_nets", "post_fix", "pruned_gate", "gate_grep"}
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        d = json.load(open(p))
        assert "finish" in d, "%s has no finish block" % os.path.basename(p)
        missing = need - set(d["finish"])
        assert not missing, "%s finish block lacks %s" % (os.path.basename(p), sorted(missing))


def t_a_board_that_matches_pairs_names_the_pairs_it_audits():
    """The audit images are what a stopped chain is read from; a board that gates on pairs and names none would
    stop with nothing to look at."""
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        f = json.load(open(p))["finish"]
        if f["pair_match"]:
            assert f["pair_audit_nets"], "%s gates on pairs and names no audit net" % os.path.basename(p)


def t_a_declared_post_fix_exists():
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        pf = json.load(open(p))["finish"]["post_fix"]
        if pf and pf != "-":
            assert os.path.exists(os.path.join(TOOLS, pf)), "%s names a post fix that is not in the tree: %s" % (os.path.basename(p), pf)


def t_every_profile_dispatches_the_one_finish():
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        fin = (json.load(open(p)).get("finish") or {})
        if not fin.get("argv"): continue
        assert os.path.basename(fin["argv"][0]) == "finish.sh", \
            "%s dispatches %s; the finish is tools/finish.sh" % (os.path.basename(p), fin["argv"][0])


def t_a_profile_agrees_with_itself_about_the_phase_it_cuts():
    """`finish.sh` derives the deliverable folder from the phase argument, and routeflow verifies the folder
    named in `deliverable`. Five profiles named a phase one behind the folder their finish actually wrote, so
    the supervisor would have looked for a folder that was never going to exist."""
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        d = json.load(open(p)); fin = d.get("finish") or {}
        if not fin.get("argv") or os.path.basename(fin["argv"][0]) != "finish.sh": continue
        _, _, proj, letter, phase, _log = fin["argv"]
        b = os.path.basename(p)
        assert d.get("phase") == phase, "%s: phase %r, finish argv cuts %r" % (b, d.get("phase"), phase)
        assert os.path.basename(d.get("deliverable", "")) == "meshsat-pcb-%s-revA-%s" % (letter, phase), \
            "%s: deliverable %r against a finish that cuts meshsat-pcb-%s-revA-%s" % (b, d.get("deliverable"), letter, phase)
        assert fin.get("clean_flag") == "out/%s-clean.txt" % phase.lower(), \
            "%s: clean flag %r against phase %s" % (b, fin.get("clean_flag"), phase)
        assert os.path.basename(d.get("project", "").rstrip("/")) == proj, \
            "%s: project %r, the finish runs in %r" % (b, d.get("project"), proj)
        assert os.path.exists(os.path.join(TOOLS, "boards", "%s.json" % letter)), "%s: no board file for %s" % (b, letter)
        # argv[0] is a path relative to the ecad directory, so the working directory is not free. c7 named
        # <PROJECT> and would have died on its first line looking for ./tools there.
        assert fin.get("cwd") == "<ECAD>", "%s: finish cwd %r, but ./tools/finish.sh only resolves from <ECAD>" % (b, fin.get("cwd"))


def t_routeflow_validate_agrees_with_these_rules():
    """The same judgement at runtime, so a profile is checkable before an eight-hour wave rests on it.
    `--dry-run` was not that: it still created the run directory, wrote provenance, ran preflight and took the
    lock, so a box profile could not be checked from the runner at all. Ten of the twelve profiles as they
    stood before the collapse fail `routeflow.py validate`."""
    import subprocess
    # `validate` judges a profile against the TREE, including the project directory its chain runs in, and
    # those are generated. On a code-only checkout this was a FAIL for a missing input, which is the shape
    # the suite exists to forbid (red team round three M1): it skips with the reason instead.
    ecad = os.path.dirname(TOOLS)
    if not glob.glob(os.path.join(ecad, "pcb-*-*")):
        raise Skip("no phase project directories in this checkout; routeflow validate judges profiles against them")
    for p in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "routeflow.py"), "validate", p],
                           capture_output=True, text=True)
        assert r.returncode == 0, "%s: %s" % (os.path.basename(p), (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else r.returncode)


def t_the_stitch_pruner_is_off_unless_a_board_asks_for_it_with_its_number():
    """It cuts copper out of a board bound for manufacture, and on 12 September it was measured finding sixteen
    abandoned vias on board E of which none was dead. That is fixed; what was not fixed then is that it had never
    removed a via that needed removing, so its risk was proved and its value was not, and no board declared it.

    A24 is the board that presented the case: the route laid two nets across In2 within 0.5 mm of a locked VBAT
    stitch via, the fill retreated, and the via ended 0.91 mm from the nearest copper of its own net with a 0.2 mm
    escape stub on its other end. The board gate refused the board for that one item of 799 checks. So the rule is
    not "no board may" any more; it is that a board turning it on carries the measurement that justified it, taken
    on a copy before it went into the path: how many vias it removed, of how many, and what that did to the opens."""
    t = open(FINISH, errors="replace").read()
    assert 'if [ -n "$(cfg x stitch_prune)" ]' in t, "the pruner runs on every board rather than on request"
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        f = json.load(open(p))["finish"]
        if not f.get("stitch_prune"): continue
        why = f.get("_stitch_prune_why", "")
        assert len(why) > 200 and re.search(r"\d+ locked via", why) and "unrouted" in why, \
            "%s turns the pruner on without the board's own number for it" % os.path.basename(p)

def t_the_stitch_pruner_is_reverted_when_it_opens_anything():
    """It removes copper, so it is judged the way the stub router is: the board before it is kept, and it goes
    back if hard or unrouted ROSE. A cleanup that can only be trusted when it happens to be right is a gamble."""
    t = open(FINISH, errors="replace").read()
    i = t.index("stitch_prune.py")
    after = t[i:i + 900]
    assert "-prestitch.kicad_pcb" in t[:i], "no copy of the board is taken before the pruner runs"
    assert "reverting" in after and "cp out/$N-prestitch.kicad_pcb" in after, \
        "the pruner's result is not reverted when it opens something"
    # and judged against the board BEFORE it, never against zero: written against zero it blamed the pruner
    # for an open the board already had, and could never help a board that was not already clean.
    assert '-gt "$BH"' in after and '-gt "$BU"' in after, \
        "the pruner is judged against zero rather than against the board it was given"


def t_a_continuation_route_gets_the_same_plane_treatment_as_the_route():
    """12 September 2026. `cont_route.sh` exports its OWN DSN from the routed board, so it needs the plane and
    power-layer treatment the route itself was given (`FR_PLANE_NETS`, `FR_POWER_LAYERS`) or Freerouting sees no
    plane and re-routes every plane pin as a wire. On C that is GND on In1, the majority of the board's
    connections; on E it is five nets over two layers.

    Nothing gave it that treatment. finish.sh passed none, and routeflow dispatches the finish with no environment
    at all (`sh(expand(fin["argv"] ...))` takes the route's env only for the route), so every continuation on every
    board since the stage was written ran against a planeless DSN. It is declared per board now, beside the
    threshold that gates the stage, and held equal to the profiles that declare it for the route."""
    treat = {}
    for f in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        try: d = json.load(open(f))
        except Exception: continue
        r = d.get("route") or {}
        if "power_layers" not in r and "plane_nets" not in r: continue
        b = d.get("board") or ""
        if not b.startswith("pcb-"): continue
        treat.setdefault(b.split("-")[1][0], {})[os.path.basename(f)] = (
            tuple(r.get("power_layers") or []), tuple(r.get("plane_nets") or []))
    for L, per in sorted(treat.items()):
        assert len(set(per.values())) == 1, "the %s profiles disagree about the plane treatment: %s" % (L, per)
        cfg = json.load(open(os.path.join(TOOLS, "boards", "%s.json" % L)))
        cont = (cfg.get("finish") or {}).get("cont_route")
        if not cont: continue
        got = (tuple(cont.get("power_layers") or []), tuple(cont.get("plane_nets") or []))
        assert got == list(per.values())[0], \
            "board %s's continuation would route against a different DSN than its route: %s against %s" % (L, got, list(per.values())[0])
    src = open(FINISH, errors="replace").read()
    i = src.index("$T/cont_route.sh")   # the invocation, not the comment that explains the stage
    line = src[max(0, src.rindex("\n", 0, i - 200)):i]
    assert "FR_PLANE_NETS" in line and "FR_POWER_LAYERS" in line, \
        "finish.sh runs the continuation without handing it the board's plane treatment"


def t_a_pass_that_lays_copper_after_the_router_is_declared_with_its_number():
    """The rule stitch_prune's admission taught, applied to the family rather than to one tool: any pass that adds
    or removes copper on a ROUTED board runs only where a board asks for it, and a board asking for it carries the
    measurement that justified it. `direct_close` joined that family on 12 September 2026 (A24: /CELL+ closed as a
    straight 9.59 mm locked track after the stub router refused it, hard 0 and the opens 3 to 2)."""
    t = open(FINISH, errors="replace").read()
    for key in ("stitch_prune", "direct_close"):
        assert 'cfg x %s' % key in t, "%s is not declared per board in the finish" % key
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        f = json.load(open(p))["finish"]
        for key in ("stitch_prune", "direct_close"):
            if not f.get(key): continue
            why = f.get("_%s_why" % key, "")
            assert len(why) > 200 and re.search(r"\d", why), \
                "%s turns %s on without the board's own number for it" % (os.path.basename(p), key)


def t_every_board_declares_the_phase_its_profile_cuts():
    """The phase reaches the silk, and `verify_deliverable` refuses a deliverable whose silk names another one, so
    a wrong phase is a board routed for hours and refused at its last step. It lived as a DEFAULT inside each
    generator: `gen_pcb_c.py` said C9 while C's deliverable is C10, and one wrapper of six set PHASE at all. A24's
    routed board carries A18 on its front silk for the same family of reason (12 September 2026).

    So the phase is declared in the board file, `full.sh` exports it, and it has to equal the phase the board's
    NEWEST routeflow profile cuts."""
    src = open(os.path.join(TOOLS, "full.sh"), errors="replace").read()
    assert 'export PHASE="${PHASE:-$(cfg phase)}"' in src, "full.sh does not take the phase from the board file"
    newest = {}
    for f in sorted(glob.glob(os.path.join(TOOLS, "routeflow", "*.json"))):
        try: d = json.load(open(f))
        except Exception: continue
        bd = d.get("board") or ""; ph = d.get("phase")
        if not bd.startswith("pcb-") or not ph: continue
        L = bd.split("-")[1][0]
        n = int(re.sub(r"\D", "", ph) or 0)
        if L not in newest or n > newest[L][0]: newest[L] = (n, ph, os.path.basename(f))
    for p in sorted(glob.glob(os.path.join(TOOLS, "boards", "*.json"))):
        L = os.path.basename(p)[0]
        d = json.load(open(p))
        assert d.get("phase"), "%s declares no phase" % os.path.basename(p)
        if L in newest:
            assert d["phase"] == newest[L][1], \
                "%s says phase %s and its newest profile %s cuts %s" % (os.path.basename(p), d["phase"], newest[L][2], newest[L][1])


def t_the_finish_stamps_the_phase_it_was_given_onto_the_silk():
    """`verify_deliverable` refuses a deliverable whose silk names another phase, and it is checked after the
    route, which is the most expensive moment to find out: A24's routed board carried A18 and C's generator
    default would have stamped C9 on a C10 deliverable. The generator writes the phase it was given, the legend
    pass now CORRECTS it from the phase the finish itself was called with, and the two together mean a board
    cannot reach the deliverable step carrying a phase nobody asked for (12 September 2026)."""
    src = open(FINISH, errors="replace").read()
    assert 'silk_fix_all.py $N.kicad_pcb $L "$PHASE"' in src, "the finish does not pass its phase to the legend pass"
    sfa = open(os.path.join(TOOLS, "silk_fix_all.py"), errors="replace").read()
    assert "PHASE = sys.argv[3]" in sfa, "the legend pass takes no phase"
    i = sfa.index("PHASE = sys.argv[3]")
    assert "REV" in sfa[i:i + 800], "the phase correction does not look at the title line"


def t_a_meander_is_locked_copper():
    """A meander is a deliberate length, not router copper. `straighten.py` shortcuts unlocked segments, and it
    runs BEFORE the pair gate in the finish, so on a board finished twice it removes the previous run's meander:
    A24 matched USB_WALL at 0.00 mm in its first finish by adding 7.54 mm to the P leg, and its second finish
    straightened 5.37 mm of that away, failed to place it again in three rounds and refused the board with every
    other gate passing (12 September 2026). Locked copper is exempt from the straightener and from the router's
    rip-up, which is what a matched length needs from both."""
    src = open(os.path.join(TOOLS, "meander.py"), errors="replace").read()
    i = src.index("PCB_TRACK(b)")
    assert "SetLocked(True)" in src[i:i + 700], "the meander's copper is not locked"
    st = open(os.path.join(TOOLS, "straighten.py"), errors="replace").read()
    assert "a.locked or c.locked" in st, "the straightener does not exempt locked copper"
    assert "PAIR_NETS" in st and st.count("a.net in PAIR_NETS") >= 2, \
        "the straightener still merges and shortcuts the nets of a differential pair class"
