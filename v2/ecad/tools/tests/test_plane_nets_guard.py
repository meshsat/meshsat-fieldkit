#!/usr/bin/env python3
"""A route that drops its board's plane nets measures the launcher, not the board (MESHSAT-862, 13 Sep 2026).

Twice in one afternoon. D's PWR class arm came back hard 0 with **121 unrouted and FOUR vias**, and C's route
hard 0 with **37 open**, both because the driver set neither `FR_PLANE_NETS` nor `FR_POWER_LAYERS` while the
board's own routeflow profile declares them. Without them every pin of those nets goes into the WIRE list at
the class width instead of being reached by a via into a plane: B15's DSN listed 258 GND pins that way, 37
percent of its connections. Both numbers were withdrawn, and the second one was made two hours after the
first was withdrawn, which is the argument for a guard rather than a note.

`route_one.sh` is the one place every launcher passes through, so the check lives there: if the environment
sets neither and some profile for this board declares either, the route is refused. `FR_PLANES_CHECKED=0`
says the omission is deliberate, which is the `erc-allow` idiom again.
"""
import os, re, subprocess, tempfile

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _fixture(stem):
    d = tempfile.mkdtemp()
    os.makedirs(os.path.join(d, "out", "par"), exist_ok=True)
    open(os.path.join(d, "out", "%s-preroute.kicad_pcb" % stem), "w").write("")
    open(os.path.join(d, "%s.kicad_pro" % stem), "w").write("{}")
    return d


def _run(project, stem, env):
    e = dict(os.environ); e.update(env)
    return subprocess.run(["bash", os.path.join(TOOLS, "route_one.sh"), project, stem, "1", "3"],
                          capture_output=True, text=True, env=e, timeout=120)


def t_a_route_without_the_plane_nets_its_profile_declares_is_refused():
    d = _fixture("pcb-d-aprs")
    r = _run(d, "pcb-d-aprs", {"FR_PLANE_NETS": "", "FR_POWER_LAYERS": "", "FR_PLANES_CHECKED": "1"})
    assert r.returncode == 2, "the route was not refused (exit %d)" % r.returncode
    assert "REFUSED" in r.stderr and "plane_nets" in r.stderr, "refused without saying what it wanted: %s" % r.stderr[:200]


def t_the_refusal_names_the_profile_that_declares_them():
    d = _fixture("pcb-d-aprs")
    r = _run(d, "pcb-d-aprs", {"FR_PLANE_NETS": "", "FR_POWER_LAYERS": "", "FR_PLANES_CHECKED": "1"})
    assert re.search(r"\b[a-z]\d*\.json\b", r.stderr), "the refusal does not name the profile: %s" % r.stderr[:200]


def t_setting_them_gets_past_the_check():
    d = _fixture("pcb-d-aprs")
    r = _run(d, "pcb-d-aprs", {"FR_PLANE_NETS": "GND"})
    assert "REFUSED" not in r.stderr, "a route that sets the plane nets was still refused"


def t_the_opt_out_is_explicit_and_works():
    d = _fixture("pcb-d-aprs")
    r = _run(d, "pcb-d-aprs", {"FR_PLANE_NETS": "", "FR_POWER_LAYERS": "", "FR_PLANES_CHECKED": "0"})
    assert "REFUSED" not in r.stderr, "the deliberate opt-out did not work"


def t_a_board_whose_profiles_declare_none_is_not_refused():
    """A board no profile declares a plane for must not be blocked by a guard about other boards. P was that board until
    15 September 2026 (P5 routes with B.Cu as a power layer, owner ruling 20:15 CEST); the bare contact board E5 has no
    routeflow profile at all and is the fixture now."""
    d = _fixture("pcb-e5-block")
    r = _run(d, "pcb-e5-block", {"FR_PLANE_NETS": "", "FR_POWER_LAYERS": "", "FR_PLANES_CHECKED": "1"})
    assert "REFUSED" not in r.stderr, "a board that declares no plane net was refused anyway: %s" % r.stderr[:200]
