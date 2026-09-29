#!/usr/bin/env python3
"""OD-01 after the owner's review of 29 September 2026 (finding T1 and the lid-pack question; MESHSAT-1357). T1: section 8
said a step stopped at a thermal limit gives readings that "bound the conductance from below". That does not follow: while
the case warms, part of the input goes into storage (P = G (T - T_room) + C dT/dt), so P over the rise can exceed the true
conductance (the review's counterexample: 64 W, 20 K and 24 W still stored is G = 2 W/K, not 3.2), and with several nodes
and a local trip no general bound holds. The statement and every instruction that relies on it are corrected together:
section 8 (the stopped step), section 5.4 (only a steady step yields G), section 1 (what a step gives and what may close)
and the brief. Also: section 1 gains the applicability of each OD-01 test to Option A(i)'s proposed lid pack (a proposal
awaiting the owner's decisions; nothing here adopts it), and the README says how verifying this package differs from
verifying the full case release (the package carries 30 of the release's 50 files). Old texts matched with any
whitespace between words, each exactly once; refuses a second run. Run: python3 <this file>."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OD = "v2/docs/records/od01/"
DASHES = ("—", "–")


def refuse(m):
    print("patch_od01j: REFUSED: %s" % m)
    sys.exit(2)


def once(t, old, new, where):
    pat = r"\s+".join(re.escape(w) for w in old.split())
    hits = list(re.finditer(pat, t))
    if len(hits) != 1: refuse("%s: expected once, found %d: %r" % (where, len(hits), old[:70]))
    m = hits[0]
    return t[:m.start()] + new + t[m.end():]


def edit(path, pairs):
    p = os.path.join(TOP, path)
    t = open(p, encoding="utf-8").read()
    t2 = t
    for old, new in pairs:
        t2 = once(t2, old, new, path)
    if t2 == t or any(d in t2 for d in DASHES): refuse("%s unchanged or a dash" % path)
    open(p, "w", encoding="utf-8").write(t2)


LIDPACK = """
**Applicability to Option A(i)'s proposed lid pack (29 September 2026).** Option A(i) (a 400 Wp array into a 200 W stage,
`v2/docs/records/a1solar/`, `a1elec/`, `a1mech/` and `a1int/` on branch `fnd/a1int`, not yet on main) proposes a second
pack of 56 or 60 cells in the lid over the face, a harness across the hinge and a stay; it waits on the owner's decisions
(which lid function leaves, REQ-016, D-06, the deployment rule: `v2/docs/EXECUTION-PLAN.md`, the standing rule of 29
September). Nothing below adopts it. What each OD-01 test still gives if it is adopted:

| Test | Applies unchanged? | Why, and what the lid pack would add |
|---|---|---|
| Receipt checks R1 to R8 | yes | the case, the frame and the walls are the same |
| H1, C6 and the gates of RFQ section 6 | yes | the heat-test plate and the legs do not meet the lid |
| C1 (face plate) for the mock-up | yes for T2 and T4 | as drawn it has no sealed crossing for the lid's lead (not designed, S-95): it is a mock-up plate, not the kit's final face under Option A(i) |
| Shutdown V1 to V4, stop limits, records | yes | the test rig, not the kit |
| Test A, lid-open steps S1, S4, S5 | yes | the open lid stands away from the base volume the test measures (INFERRED; the lid pack's own heat when charging is not in the test) |
| Test A, lid-closed steps S2, S3, S6 | no, as a measure of Option A(i) | with the lid pack the closed lid's space over the face is mostly cells; the conductance with the lid closed would need a lid-pack thermal dummy in the lid (a new step) |
| Patch runs | yes | the plate's spreading under the PA flange site does not depend on the lid |
| Test B: T1, T2, T5, T11 | yes | case, frame, legs, walls, arrestor |
| Test B: T4 and T6 | partly | T4 has no lid-pack stand-in; T6's open-lid clearance to the mated plugs would change with a lid pack |
| New for the lid pack (not in OD-01) | none yet | `records/a1mech/README.md` names T-A1-1 (the lid's depth to the ceiling), T-A1-2 (the U-174/U jack), T-A1-3 (the stop, the hinge axis, the open case on a slope) and T-A1-4 (200 lid cycles with a dummy module and the harness), plus the sealed lid-lead crossing (S-95) |
"""


def main():
    p = os.path.join(TOP, OD, "TEST-PROCEDURE.md")
    if "Applicability to Option A(i)'s proposed lid pack" in open(p, encoding="utf-8").read(): refuse("already applied")
    edit(OD + "TEST-PROCEDURE.md", [
        # section 1: what a step gives
        ("At steady state each step gives one number:",
         "At steady state each step gives one number (a step\nstopped at a limit before steady state gives none, section 8):"),
        # section 1: the applicability table, before the uncertainty budget
        ("**Its uncertainty (the session's budget, INFERRED",
         LIDPACK.strip("\n") + "\n\n**Its uncertainty (the session's budget, INFERRED"),
        # section 5.4
        ("`P` = the mean of the readings in that window. Uncertainty per section 1.",
         "`P` = the mean of the readings in that window. Uncertainty per section 1. Only a step with `steady_utc` yields `G`;\n"
         "a step stopped at a limit yields none (section 8)."),
        # section 8: the stopped step
        ("A trip in S3 to S6 is a result, not a fault: the step is recorded as \"stopped at the limit\" with its readings up to "
         "the trip, which bound the conductance from below.",
         "A trip in S3 to S6 is recorded, not treated as a fault: the step is recorded as \"stopped at the\nlimit\" with "
         "every reading up to the trip, the time and what tripped. Those readings are kept as transient data and are **not** a\n"
         "steady-state result. While the case still warms, part of the input goes into storage (`P = G (T - T_room) + C dT/dt`),\n"
         "so `P / (T - T_room)` before steady state can exceed the true conductance (64 W, a 20 K rise and 24 W still stored is\n"
         "2 W/K, not 3.2), and with several temperature nodes and a local trip no general bound holds in either direction. A\n"
         "stopped step therefore yields no `G`; any conductance the session infers from it needs a stated transient model with\n"
         "its uncertainty, is labelled so, and closes no row of section 1 until that model is itself checked."),
        ("so TS1 may open in S6: that is the arrangement doing its job.",
         "so TS1 may open in S6: that is the arrangement doing its job, and\nthen S6 gives no `G`: the 64 W lid-closed point stays open until the session plans a replacement step at desk."),
    ])
    edit(OD + "TEST-BRIEF.md", [
        ("- **What it can prove:** the enclosure's conductance for heat released into the inside air,",
         "- **What it can prove:** from each step that reaches steady state (a step stopped at a limit gives no conductance,\n"
         "  procedure section 8), the enclosure's conductance for heat released into the inside air,"),
    ])
    edit(OD + "README.md", [
        ("## What remains open for the session (no money involved)",
         "**Verifying this package and the case release.** `sha256sum -c v2/docs/records/od01/PACKAGE.sha256` (from the\n"
         "repository root, or from `repo/` of the exported copy) verifies this package's files. The case release's own\n"
         "`v2/release/case-2026-09-27/MANIFEST.sha256` verifies the full release only in a complete clone: the package carries\n"
         "30 of its 50 files, the ones the quotes and checks use. The proposed lid pack of Option A(i) and what it leaves of each\n"
         "test: `TEST-PROCEDURE.md` section 1.\n\n## What remains open for the session (no money involved)"),
    ])
    print("patch_od01j: T1 corrected in sections 8, 5.4 and 1 and the brief; the lid-pack applicability and the verification scope added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
