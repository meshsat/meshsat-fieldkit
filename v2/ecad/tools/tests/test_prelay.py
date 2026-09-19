#!/usr/bin/env python3
"""A long net the router will not take is laid before the router runs (MESHSAT-862, 14 September 2026).

Board C's `/EPD_SDA` runs 249 mm from J_EPD pin 14 to U3 pad 5 across a panel whose outline is a ring with a
240 by 176 mm display window through the middle, so it has exactly one corridor: east along the top strip,
then south down the right strip. Four routes left it or left another net exactly like it (C11 left EPD_SDA,
C12 left /PWM1 and /HB2, C13 left fifty-nine, C14 left EPD_SDA and /HB3), and a board-wide search at a 0.1 mm
grid on all three routing layers finds no path on the ROUTED board even at the panel's own 0.127 clearance.

On the PLACED board those strips are empty. The lane is laid there, locked, and the router works around it.
That is `bus_a21.py`'s pattern of 5 September with the waypoints searched instead of typed, and these rules
hold the three things that make it safe: it is declared per board and off everywhere else, it is restricted
to the named nets rather than let loose on a board where every net is unconnected, and the board is kept only
if the hard count does not rise.
"""
import os, json

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FULL = open(os.path.join(TOOLS, "full.sh")).read()
SR = open(os.path.join(TOOLS, "stub_router.py")).read()

GUARD = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "guarded.sh"), errors="replace").read()


def t_the_search_can_be_restricted_to_named_nets():
    """A FIXED BYTE WINDOW IS NOT A RULE ABOUT THE CODE, it is a rule about how much prose sits between two
    lines (18 September 2026, the second time in one evening: `test_stub_zone_obstacle` failed the same way when
    a comment pushed `zpoly(via` past its 2,500-character slice, and this one failed when the pour-obstacle and
    lock flags landed between the declaration and the filter). What the rule means is that the filter is read
    where the pairs are chosen and AFTER the set is built, so it asks for the order of the two lines and for
    nothing about their distance."""
    assert 'os").environ.get("STUB_NETS"' in SR, "there is no net filter, so a placed board would be routed whole"
    i = SR.find("_WANT = ")
    j = SR.find("if _WANT and netname(its[0][\"net\"]) not in _WANT: continue")
    assert j > 0, "the filter does not actually skip the pairs of other nets"
    assert i > 0 and i < j, "the filter reads a set that is not built yet"


def t_the_stage_is_declared_per_board_and_off_by_default():
    assert 'PRELAY="$(cfg prelay_nets)"' in FULL, "the stage does not read its declaration"
    assert 'if [ -n "$PRELAY" ]; then' in FULL, "the stage runs on boards that never asked for it"
    for letter in ("a", "b", "d", "e", "p"):
        d = json.load(open(os.path.join(TOOLS, "boards", letter + ".json")))
        assert not d.get("prelay_nets"), "board %s declares a pre-lay and nothing has measured one there" % letter


def t_the_board_is_kept_only_if_the_hard_count_does_not_rise():
    """15 September 2026: the pre-lay runs under the one guard on the pre-route basis; the guard restores its snapshot
    when hard or unrouted rose against the board it was handed."""
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    body = FULL[i:i + 2200]
    assert "GUARD_MODE=pre guarded prelay" in body, "the pre-lay does not run under the guard on the pre-route basis"
    assert '"$AH" -gt "$BH"' in GUARD and "restored as it was handed in" in GUARD, "a refused lane is not taken back and reported"


def t_it_runs_before_the_pre_route_drc_that_judges_the_board():
    i = FULL.find('PRELAY="$(cfg prelay_nets)"')
    j = FULL.find("--label 'pre-route DRC'")
    assert 0 < i < j, "the pre-lay runs after the gate that would have to judge its copper"


def t_no_board_declares_a_pre_lay_and_c_carries_the_measurement_that_says_why():
    """C15 pre-laid /EPD_SDA alone and ended at 8 open against C14's 2; C16 pre-laid the whole six-wire bus,
    5 of 7 laid on the placed board, and routed 15 and 16 open against C14's 12 and 4. A lane taken by hand
    on a board whose strips are its only corridors costs the router more than it buys. The stage stays for
    the board that measures otherwise; today none does."""
    for letter in ("a", "b", "c", "d", "e", "p"):
        d = json.load(open(os.path.join(TOOLS, "boards", letter + ".json")))
        assert not d.get("prelay_nets"), "board %s declares a pre-lay and the only measurements say it costs opens" % letter
    d = json.load(open(os.path.join(TOOLS, "boards", "c.json")))
    assert "C16 MEASURED" in d.get("_prelay_why", "") and "C15" in d.get("_prelay_why", ""), (
        "the declaration was removed without the two measurements that removed it")


def t_a_pre_lay_group_may_ask_for_more_room_than_its_class_carries():
    """Board E's current-sense pair is why. ANA-001 wants 0.50 mm from switching copper; the SENSE class carries
    the board's 0.127; a 0.50 mm class clearance refuses the escape at the controller's own pins (measured on
    board A, 18 September); and a DSN class-pair rule does not reach Freerouting (measured on E17, the same
    day, a run laid 0.171 mm away with the rule in its DSN). A LOCKED run laid to the number before the router
    starts is the one instrument left, so the group carries its own clearance and the stub router takes it as a
    floor on the laid net's own side, leaving KiCad's larger-of-the-two rule intact against every obstacle."""
    import os
    T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full = open(os.path.join(T, "full.sh"), encoding="utf-8").read()
    assert "g.get('clearance','')" in full, "a pre-lay group cannot declare a clearance"
    assert 'STUB_NET_CLEAR="${GCLR:-0}"' in full, "the group's clearance does not reach the stub router"
    src = open(os.path.join(T, "stub_router.py"), encoding="utf-8").read()
    i = src.index("_me = max(net_clr(net)")
    j = src.index("def clr_to(other)")
    assert i < j, "the floor is applied after the comparison that uses it"
    assert 'STUB_NET_CLEAR' in src[i:j], "the floor does not read the knob"
    assert "max(_me, net_clr(other))" in src, "the floor replaced KiCad's larger-of-the-two rule instead of feeding it"


# --------------------------------------------------------- every group keeps its own reading (19 September 2026)
# Board E declares THREE pre-lay groups and all three ran under the one guard label `prelay-group`, so the guard
# wrote `guard-prelay-group.verdict.json` three times and only the last survived. That is not a logging nicety:
# the guard's verdict is how a reverted group is reported, so a group that RAISED the hard count and was
# correctly restored left a FAIL that the next group's PASS overwrote, and the stage that carries board A's
# eleven RF drops and board E's whole ANA-001 answer reported one of its three measurements. These two rules
# are a real run of `guarded` in a fixture tree, one with two distinct labels and one with the same label twice.

def _guard_tree():
    """A directory `guarded` can run in: stub drc.sh and hardset.py, the real verdict writer."""
    import tempfile, shutil, os
    d = tempfile.mkdtemp(prefix="guard-label-")
    t = os.path.join(d, "tools"); os.makedirs(t)
    prj = os.path.join(d, "prj"); os.makedirs(os.path.join(prj, "out"))
    shutil.copy(os.path.join(TOOLS, "guarded.sh"), t)
    shutil.copy(os.path.join(TOOLS, "verdict.py"), t)
    open(os.path.join(t, "drc.sh"), "w").write('#!/bin/bash\nprintf "{}" > "$2"\n')
    os.chmod(os.path.join(t, "drc.sh"), 0o755)
    # the stub hard set: whatever the label, hard 0 and unrouted 0, so the guard keeps every stage
    open(os.path.join(t, "hardset.py"), "w").write(
        "import sys\n"
        "a = sys.argv\n"
        "p = a[a.index('--counts') + 1]\n"
        "open(p, 'w').write('0 0\\n')\n")
    open(os.path.join(prj, "b.kicad_pcb"), "w").write("(kicad_pcb)\n")
    return d, t, prj


def _run_guard(labels):
    """Run `guarded` once per label in one project directory; return the verdict files left behind."""
    import subprocess, shutil, os, sys, glob
    d, t, prj = _guard_tree()
    script = ("set -e\ncd '%s'\nN=b\nT='%s'\n. \"$T/guarded.sh\"\nstage () { echo ran \"$1\"; }\n" % (prj, t)
              + "".join('GUARD_MODE=pre guarded "%s" stage "%s"\n' % (l, l) for l in labels))
    r = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                       env=dict(os.environ, VERDICT_DIR=os.path.join(prj, "out")))
    left = sorted(os.path.basename(p) for p in glob.glob(os.path.join(prj, "out", "guard-*.verdict.json")))
    logs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(prj, "out", "guard-*.log")))
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout + r.stderr, left, logs


def t_two_guarded_stages_under_one_label_keep_one_verdict_between_them():
    """THE DEFECTIVE FIXTURE, which is what board E's three pre-lay groups were doing: expected verdict FAIL,
    two stages ran and the evidence channel holds one reading."""
    rc, out, left, logs = _run_guard(["prelay-group", "prelay-group"])
    assert rc == 0, out
    assert left == ["guard-prelay-group.verdict.json"], (left, out)
    assert logs == ["guard-prelay-group.log"], (logs, out)


def t_two_guarded_stages_under_their_own_labels_each_keep_theirs():
    """THE ACCEPTABLE FIXTURE: expected verdict PASS, two stages and two readings."""
    rc, out, left, logs = _run_guard(["prelay-group-1-SHORE_INHIBIT", "prelay-group-2-TRK_SW1"])
    assert rc == 0, out
    assert left == ["guard-prelay-group-1-SHORE_INHIBIT.verdict.json",
                    "guard-prelay-group-2-TRK_SW1.verdict.json"], (left, out)
    assert len(logs) == 2, (logs, out)


def t_the_chain_labels_every_pre_lay_group_with_its_own_index_and_net():
    """And the chain uses that: the label and the group's own log both carry the index and the first net it
    names, so a reader can tell which declaration a verdict is about without counting groups by hand."""
    assert 'guarded "prelay-group-$GTAG" gstage' in FULL, "the pre-lay groups still share one guard label"
    assert "out/$N-prelay-group-$GTAG.log" in FULL, "the pre-lay groups still share one log file"
    assert "for i, g in enumerate(json.load(open(sys.argv[1])).get('prelay_groups') or [], 1)" in FULL, \
        "the group index is not computed where the groups are read"
    i, j = FULL.index("get('prelay_groups')"), FULL.index('guarded "prelay-group-$GTAG"')
    assert "[^A-Za-z0-9_]" in FULL[i:j], "the label is built from a net name without making it a safe filename"


def t_a_group_may_ask_for_the_pours_and_for_the_landing_reach():
    """Both are per BOARD and the two boards that have measured them want opposite answers (19 September 2026).

    `pour_obstacle`: board D had 5,140 free cells of 834,561 with the pours in the obstacle map and laid
    nothing, which is why the stage's default is 0. `land_reach`: the search ends at a goal cell and the
    landing lays a short segment from each path end to the net's own copper, and board A's ends are 0.153 to
    4.409 mm from theirs against a reach that had been a silent 1.2 mm since the day it was written.

    NEITHER DEFAULT MOVES, so no board that worked changes, and board A DECLARES NEITHER. Both were written
    into its switching group during the afternoon of 19 September and both came back out when their own arm
    refused them: three arms one variable apart, on the same placed board, all closed 20 of 20 at hard 0, with
    the pours as obstacles at a 5.0 mm reach (91 locked pieces), the pours free at 5.0 (94) and the pours free
    at the default 1.2 (92). What unlocked that board was the closure acceptance and nothing else. The knobs
    stay because board D is a real case for the first; a knob is offered here, never declared on a board
    without a number that says it matters."""
    assert "g.get('pour_obstacle','')" in FULL, "a pre-lay group cannot declare the pours"
    assert "g.get('land_reach','')" in FULL, "a pre-lay group cannot declare the landing's reach"
    assert 'STUB_POUR_OBSTACLE="${GPOUR:-${PRELAY_POUR_OBSTACLE:-0}}"' in FULL, \
        "the group's pour setting does not reach the stub router, or it changed the default"
    assert 'STUB_LAND_REACH="${GREACH:-${PRELAY_LAND_REACH:-1.2}}"' in FULL, \
        "the group's landing reach does not reach the stub router, or it changed the default"
    src = open(os.path.join(TOOLS, "stub_router.py"), encoding="utf-8").read()
    assert 'os.environ.get("STUB_LAND_REACH", "1.2")' in src, "the tool does not read it, or its default moved"
    assert "reach=LAND_REACH_MM" in src, "the landing does not use the knob"


def t_an_empty_field_in_a_group_does_not_shift_the_ones_after_it():
    """TAB IS IFS WHITESPACE AND BASH COLLAPSES A RUN OF IT (19 September 2026, caught on A50 twelve minutes
    after it launched). The per-group fields were tab separated, a group with no `clearance` emitted two tabs
    in a row, `read` swallowed the empty field, and every field after it shifted left: board A's RF and
    switching groups took their own TAG as their clearance (`STUB_NET_CLEAR=2-FE_SW2`), lost the tag, and the
    switching group laid NOTHING and returned in 21 seconds against A49's 577. This rule runs the real
    emitter over the real board file and reads the fields back through a real `read`, because that is where
    the defect lived: both halves were correct on their own."""
    import json, re, subprocess, sys
    cfg = os.path.join(TOOLS, "boards", "a.json")
    groups = json.load(open(cfg, encoding="utf-8")).get("prelay_groups") or []
    assert any(not g.get("clearance") for g in groups), "board A no longer has a group without a clearance"
    emit = re.search(r"python3 -c \"\nimport json,re,sys\n(.*?)\" \"\$CFG\"", FULL, re.S)
    assert emit, "the group emitter moved; this rule reads it out of full.sh"
    script = "import json,re,sys\n" + emit.group(1)
    out = subprocess.run([sys.executable, "-c", script, cfg], capture_output=True, text=True).stdout
    sh = ("while IFS='|' read -r GNETS GLAYERS GCLR GTAG GPOUR GREACH; do "
          "printf '%s;%s;%s\\n' \"$GNETS\" \"$GCLR\" \"$GTAG\"; done")
    back = subprocess.run(["bash", "-c", sh], input=out, capture_output=True, text=True).stdout.strip().splitlines()
    assert len(back) == len(groups), (back, out)
    for line, g in zip(back, groups):
        nets, clr, tag = line.split(";")
        assert nets == g["nets"], (nets, g["nets"])
        assert clr == str(g.get("clearance", "") or ""), ("the clearance field shifted: %r" % line)
        assert re.fullmatch(r"\d+-[A-Za-z0-9_]+", tag), ("the tag is empty or malformed: %r" % line)


def t_a_board_that_declares_pre_lay_groups_requires_the_per_group_chain():
    """E23 AND A49 LOST THEIR PRE-LAY EVIDENCE TO A TREE THAT PREDATED THE PER-GROUP CHAIN (19 September
    2026). The older loop runs once per group but writes every one of them to the same
    `out/<N>-prelay-group.log` under the same guard label, so each group overwrites the one before it, and
    routeflow saved no generator log either: on E23 the only surviving pre-lay output is the LAST group's,
    and what the six switching nets laid is unrecoverable. The rule above already holds the CURRENT tree to
    per-group logs and labels; this one makes an ARM prove its own staged tree carries them, through the
    mechanism that exists for exactly this (`routeflow ... --requires`, or `requires:` in the profile).
    A board that declares no group needs nothing."""
    import json, os
    for letter in sorted(os.path.splitext(f)[0] for f in os.listdir(os.path.join(TOOLS, "boards"))
                         if f.endswith(".json")):
        bf = os.path.join(TOOLS, "boards", letter + ".json")
        try: groups = json.load(open(bf)).get("prelay_groups") or []
        except Exception: continue
        if not groups: continue
        pf = os.path.join(TOOLS, "routeflow", letter + ".json")
        if not os.path.exists(pf): continue
        req = json.load(open(pf)).get("requires") or []
        assert any("prelay-group-$GTAG" in r for r in req), (
            "board %s declares %d pre-lay group(s) and its profile does not require the per-group chain, so an "
            "arm staged from an older tree would silently overwrite every group's evidence but the last"
            % (letter, len(groups)))
