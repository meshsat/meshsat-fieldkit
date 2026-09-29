#!/usr/bin/env python3
"""OD-01 after the targeted check 10 (`checks/check-10.md`, MESHSAT-1357, 29 September 2026). B1: the applicability table
described Option A(i) as the lid pack only, leaving out the base pockets' second 4S3P block in the west pocket, which moves
the west RF jumpers and so the west wall's T5 and entry plate; the table is replaced whole (the method of patch_od01e.py),
with the west block, T5 partly, C4-W a mock-up plate, T4's west-block stand-in, T6's change stated (m6), a1mech's extended
checks (m7), S-95's age (m8), the pack size cited from RECONCILE.md (m5) and the standing rule cited on main (m4). m1: the
physics sentence of section 8 states the right reason (a warming step's one-node reading is at most an upper bound; room
drift, a cooling step and a point reading of stratified air remove even that). m2: the "not yet steady" row says the rise
reads low, so G reads high. m3: the release manifest's directory and scope. Text only; old texts matched with any whitespace
between words, each exactly once; refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01k: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs, fn=None):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = fn(t) if fn else t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t or any(d in t2 for d in DASHES): refuse("%s unchanged or a dash" % path)
    open(p, "w", encoding="utf-8").write(t2)


TABLE = """**Applicability to Option A(i)'s proposal (29 September 2026, second issue after check 10).** Option A(i) (a 400 Wp
array into a 200 W stage; `v2/docs/records/a1solar/`, `a1elec/`, `a1mech/` and `a1int/` on branch `fnd/a1int`, not yet on
main) proposes two changes inside the case: the base pockets' 4S6P, a second 4S3P block in the west pocket beside the
east one, and a lid pack of 4S14P or 4S15P (`a1int/RECONCILE.md`) over the face, with a harness across the hinge and a lid
stay. It waits on the owner's decisions (which lid function leaves, REQ-016, D-06, the deployment rule: the standing rule
of 29 September in `v2/docs/EXECUTION-PLAN.md` on main, commit `bf68ad9e`). Nothing below adopts it. What each OD-01 test
still gives if it is adopted:

| Test | Applies unchanged? | Why, and what Option A(i) would add |
|---|---|---|
| Receipt checks R1 to R8 | yes | the case, the frame and the walls are the same |
| H1, C6 and the gates of RFQ section 6 | yes | the heat-test plate and the legs meet neither the lid nor the west block |
| C1 (face plate) for the mock-up | yes for T2 and T4 | as drawn it has no sealed crossing for the lid's lead nor for the QMX leads (S-95, which predates Option A(i)): a mock-up plate, not the kit's final face |
| C4-W (west entry plate) for the mock-up | no, as the kit's plate | the west block takes the room the west RF jumpers were planned in; the west RF entry is re-planned before the west block is taken (`a1mech/README.md` item 6): C4-W as drawn is a mock-up plate; C4-E is unchanged |
| Shutdown V1 to V4, stop limits, records | yes | the test rig, not the kit |
| Test A, lid-open steps S1, S4, S5 | yes, for the base as set up | the open lid stands away from the base volume the test measures (INFERRED; the lid pack's own heat when charging is not in the test); the west block is not in the set-up (H3 stands for the east block only), so the steps measure the base without it |
| Test A, lid-closed steps S2, S3, S6 | no, as a measure of Option A(i) | with the lid pack the closed lid's space over the face is mostly cells; the conductance with the lid closed would need a lid-pack thermal dummy in the lid and the west block's twin of H3 (new steps) |
| Patch runs | yes | the plate's spreading under the PA flange site does not depend on the lid or the pockets |
| Test B: T1, T2, T11 | yes | case, frame, legs, the arrestor on the east plate |
| Test B: T5 | partly | the end wall east and the back wall unchanged; the west wall's holes wait on the west RF re-plan |
| Test B: T4 | partly | it has no lid-pack stand-in and no stand-in for the west block |
| Test B: T6 | yes, as a bound (INFERRED) | the lid pack is inside the lid and leaves its outer skin unchanged; the stay stops the lid at 100 degrees, short of Peli's stop, so T6's open-lid reading at Peli's stop bounds Option A(i) unless T-A1-3 finds otherwise |
| New for Option A(i) (not in OD-01) | none yet | `records/a1mech/README.md` section 7: T-A1-1 (the lid's depth to the ceiling), T-A1-2 (the U-174/U jack), T-A1-3 (the stop, the hinge axis, the open case on a slope), T-A1-4 (200 lid cycles with a dummy module and the harness); T9 with a dummy module; T8's pull test at the module's load; E1 and E2 with an accelerometer on the lid; T10 and T5 at the west wall after the west RF re-plan; the sealed lid-lead crossing (S-95) |
"""


def table(t):
    i = t.index("**Applicability to Option A(i)'s proposed lid pack (29 September 2026).**")
    j = t.index("**Its uncertainty (the session's budget, INFERRED", i)
    return t[:i] + TABLE + "\n" + t[j:]


def main():
    p = os.path.join(TOP, OD, "TEST-PROCEDURE.md")
    if "second issue after check 10" in open(p, encoding="utf-8").read(): refuse("already applied")
    edit(OD + "TEST-PROCEDURE.md", [
        ("| Not yet steady at the criterion of section 5.3 | at most 0.33 K = 1.1 % low | at most 0.33 K = 3.3 % low |",
         "| Not yet steady at the criterion of section 5.3 | the rise up to 0.33 K low, so `G` up to 1.1 % high | the rise up to 0.33 K low, so `G` up to 3.3 % high |"),
        ("2 W/K, not 3.2), and with several temperature nodes and a local trip no general bound holds in either direction.",
         "2 W/K, not 3.2). For a step that warms from below its own steady state, that reading is at most an upper bound on\n"
         "`G`; room drift, a step that starts above its steady state and cools (S4 after S3), and a point reading of stratified\n"
         "air under natural convection remove even that."),
    ], table)
    edit(OD + "README.md", [
        ("The case release's own `v2/release/case-2026-09-27/MANIFEST.sha256` verifies the full release only in a complete clone: "
         "the package carries 30 of its 50 files, the ones the quotes and checks use.",
         "The case release's own manifest verifies the 50 files it\n"
         "lists, run inside `v2/release/case-2026-09-27/` of a complete clone (`sha256sum -c MANIFEST.sha256`); the package carries\n"
         "30 of them, the ones the quotes and checks use, and the release's two later folders, `h1-heat-test-plate/` and\n"
         "`lid-tray-qmx-r2/`, each carry their own `MANIFEST.sha256`."),
        ("The proposed lid pack of Option A(i) and what it leaves of each test:",
         "Option A(i)'s proposal (the west pocket's second block and the lid pack) and what it leaves of each test:"),
    ])
    print("patch_od01k: the applicability table replaced whole with the west block; m1 to m8 answered")
    return 0


if __name__ == "__main__":
    sys.exit(main())
