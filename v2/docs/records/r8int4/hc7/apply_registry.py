#!/usr/bin/env python3
"""Registry changes of the layer 7 closer (MESHSAT-1357, fnd/hc7, 27 September 2026), for the registry writer to apply to
v2/ecad/tools/pcb_requirements.yaml. Idempotent: each edit is made by record id, inside that record's own block, and asserts the old text;
an edit already applied is recognised by its new text and skipped; anything else stops the script before it writes.

Usage (from the repository root, after the case release and v2/docs/CASE-FIT-UNCERTAINTIES.md have landed):
    python3 drafts/hc7/apply_registry.py [--registry v2/ecad/tools/pcb_requirements.yaml] [--rebind] [--dry-run]
then: python3 v2/ecad/tools/rules_lib.py requirements   (the registry's own checks)

What it changes, each the session's under the owner's standing rule of 26 September 2026 (never ask; take the recommended option), none
lowering a requirement or narrowing a scope:
 1. REQ-047: the statement's "(ten M3)" is the ten 6-32 UNC of C1 (SC-07); the acceptance's blind-mate stack is named as the owed dock and
    blind-mate tolerance stack, because CASE-MARGINS.md judges no blind-mate row (its section 6, last paragraph), so "closes on paper against
    CASE-MARGINS.md" pointed at an analysis that does not exist.
 2. CON-006: the pocket is bounded by board A's east edge and by Peli's fillet and east wall (X 178 is not a Peli surface, CASE-MARGINS.md
    2.6), and board B's underside is at Z 49.0 with the dock strip's VHB pads under the stack (C1 follow-on (a)), not 47.9.
 3. A new LATER open item (the next free L-number, L-07 on main 84e52461; its title fingerprint makes a re-run find it): the targeted case
    mock-up, not approved by D-09, needed before boards A, B, E and P enter layout, like L-04 and L-05 for their review routes.
 4. FEA-007, new: the kit's fit in the 1450 on the chosen arrangement, a feasibility blocker whose bounds include failure (M17g and M17x fail
    as laid out; 30 rows rest on unstated allowances). Staged (revised after the second review of the case release, 27 September 2026):
    LAYOUT_ENTRY holds A, B, D, E, E5 and P and needs DESK and BENCH_MOCKUP: the desk items for all six, and for A, B, E and P the mock-up's
    checks of the rows a failing reading would remedy by moving that board (CASE-FIT-UNCERTAINTIES.md section 2, the YES rows), because the
    owner's execution prompt of 27 September 2026 admits a deferred physical test only where the current stage's decision does not depend on
    it (section 2) and forbids moving a decisive uncertainty to a later phase to unblock a status (section 5). It waits on S-27 and on the
    item of 3, so those boards read BLOCKED on the owner's purchase decision; the compact question is CASE-FIT-UNCERTAINTIES.md section 7.
    FABRICATION_RELEASE re-reads each committed layout against the mock-up's readings; T3, T7, T8 and T9 at PROTOTYPE_VERIFICATION. This is
    the geometry item the computed layout-entry test lacked (the layer 7 audit, stage_gate_cycles). The first draft of the same morning put
    the mock-up at FABRICATION_RELEASE with purchase authority as its only reason; it is replaced, not kept beside this.
 5. CON-006's acceptance: the clause that carried the pack's rows to the fabrication release when the mock-up had not run is replaced by the
    mock-up before boards A and P enter layout (M4a and M5 are YES rows), and CON-006 waits on the item of 3 as well.
 6. --rebind (only when v2/docs/CASE-MARGINS.md has changed from 275a3083db30a7bf, i.e. drafts/hc7/CASE-MARGINS.md.patch landed): every
    record bound to CASE-MARGINS.md@275a3083db30a7bf is re-read and rebound to the file in the tree, with an evidence line naming what the
    edit changed (the CAD note, the AI-review label, the dock-stack pointer, section 7's timing: the mock-up before the layout entry of the
    boards a failing check would move, and with the frame_seat draft M18's part list and U51's 1.60 sourced to ST's maximum) and that no
    figure or verdict of section 3 moved; the record's evidence_result is not touched. Likewise every record bound to
    v2/docs/ASSEMBLY.md at 84e52461 (30db27eee509212c; or e3aedb25's e4a0b78616c69779) (CFL-015) is rebound once drafts/hc7/ASSEMBLY.md.patch has landed, after checking on the file that the
    lines that reading cites (the Pack SMBus row of section 4 and build step 7) are byte-identical; if they are not, it says so and rebinds nothing.
Tested on 27 September 2026 on an archive of main 84e52461 with the branch, drafts/hc7/CASE-MARGINS.md.patch,
CASE-MARGINS.frame_seat-draft.patch and ASSEMBLY.md.patch applied: see drafts/hc7/APPLY.txt for the counts; a second run changes nothing. After it, the registry's generated pages (REQUIREMENTS-TRACE.md, CURRENT-EVIDENCE.md) are re-rendered by
the integrator's usual step.
"""
import os, re, sys, hashlib

ARGS = sys.argv[1:]
REG = ARGS[ARGS.index("--registry") + 1] if "--registry" in ARGS else "v2/ecad/tools/pcb_requirements.yaml"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(REG)), "..", "..", ".."))
DRY = "--dry-run" in ARGS
OLD_CM = "v2/docs/CASE-MARGINS.md@275a3083db30a7bf"


def sha16(rel):
    return hashlib.sha256(open(os.path.join(ROOT, rel), "rb").read()).hexdigest()[:16]


text = open(REG, encoding="utf-8").read()
orig = text
log = []


def block(t, rid):
    """(start, end) of record rid's block: from its '  - id: <rid>' line to the next record's or the end of the file."""
    m = re.search(r"^  - id: %s\n" % re.escape(rid), t, re.M)
    if not m: return None
    n = re.search(r"^  - id: ", t[m.end():], re.M)
    return m.start(), (m.end() + n.start()) if n else len(t)


def edit(rid, old, new, what):
    global text
    b = block(text, rid)
    assert b, "%s is not in %s" % (rid, REG)
    body = text[b[0]:b[1]]
    if new in body and old not in body:
        log.append("%s: %s already applied" % (rid, what)); return
    assert body.count(old) == 1, "%s: the old text of '%s' is not in the record once (found %d); the record moved, re-read it" % (rid, what, body.count(old))
    text = text[:b[0]] + body.replace(old, new) + text[b[1]:]
    log.append("%s: %s" % (rid, what))


# ---------------------------------------------------------------- 1. REQ-047
edit("REQ-047",
     """      The face plate comes off (ten M3), the rod stack lifts straight up off the blind-mate joint without unscrewing a
      cable, and the pack comes out of its cradle.""",
     """      The face plate comes off (ten 6-32 UNC screws from above into Peli's inserts, C1 of SC-07), the rod stack lifts
      straight up off the blind-mate joint without unscrewing a cable, and the pack comes out of its cradle.""",
     "statement: the plate's ten screws are the 6-32 of C1")
edit("REQ-047",
     """      Demonstrated on the assembled prototype; the blind-mate float tolerance stack closes on paper against Peli's own
      figures (CASE-MARGINS.md), with any OPEN margin shown on hardware at the build.""",
     """      Demonstrated on the assembled prototype; the dock and blind-mate float tolerance stack (the SMP-MAX paths, the
      Preci-Dip 813 contacts and the Mill-Max power pins with the rods, spacers, VHB pads and laminates) closes on paper
      as its own analysis, which is owed (v2/docs/CASE-FIT-UNCERTAINTIES.md section 3, row DOCK; CASE-MARGINS.md judges
      no blind-mate row), and the case margins it rests on are held against Peli's own figures (CASE-MARGINS.md), with
      any OPEN margin shown on hardware at the build.""",
     "acceptance: the blind-mate stack is its own owed analysis")

# ---------------------------------------------------------------- 2. CON-006
edit("CON-006",
     """      The pack of D-06 (one shrink-wrapped 4S3P 18650 block), its board P, the heater mat and their mounting fit the
      east pocket (X +120 to +178, Y -120 to +120) under board B's underside at Z 47.9.""",
     """      The pack of D-06 (one shrink-wrapped 4S3P 18650 block), its board P, the heater mat and their mounting fit the
      east pocket, bounded by board A's east edge at X +120, by Peli's R 15.88 floor fillet and east wall and in Y by
      the frame's setting legs (CASE-MARGINS.md 2.6 and C6; the place is v2/ecad/tools/panel1450.py PACK_BLOCK,
      PACK_WEST_X and PACK_GROUP_LEN), under board B's underside at Z 49.0 (the dock strip's VHB pads lift the stack,
      C1 follow-on (a); 47.9 until 27 September 2026).""",
     "statement: the pocket's bounds are Peli's surfaces and B's underside is Z 49.0")

# ---------------------------------------------------------------- 3. the purchase of the mock-up, a LATER open item
L_FINGERPRINT = "The targeted case mock-up of CASE-MARGINS.md sections 5 and 7"
L_TITLE = """    title: >-
      The targeted case mock-up of CASE-MARGINS.md sections 5 and 7 (READY-TO-ACT.md section 6): a new Peli 1450 of the
      current moulding with its 1450PF frame (shared with the empty-case heat-balance test), the made parts of
      v2/release/case-2026-09-27/, one PolyPhaser GTH-SFF-AL, the picked jumper plugs on RG-316, the Xenarc 709GNK and a
      CM5 heatsink, and stand-ins for the boards and the pack: not approved by D-09; it needs the owner's spending
      approval before boards A, B, E and P enter layout, because a failing check of their YES rows moves board A's east
      edge, board B's edges, east-end parts and stack, board E's south edge and clamp lanes, or board P's place
      (CASE-FIT-UNCERTAINTIES.md sections 2 and 7; FEA-007).
"""
m = re.search(r"^open_items:\s*\n", text, re.M); assert m, "no open_items section"
end = re.search(r"^[a-z_]+:", text[m.end():], re.M); oi = (m.end(), m.end() + end.start() if end else len(text))
have = [mm.group(1) for mm in re.finditer(r"^  - id: (\S+)\n", text[oi[0]:oi[1]], re.M)]
L_ID = next((i for i in have if i.startswith("L-") and L_FINGERPRINT in text[block(text, i)[0]:block(text, i)[1]]), None)
if L_ID:
    log.append("%s: the mock-up purchase item is already present" % L_ID)
else:
    used = [int(i[2:]) for i in re.findall(r"^  - id: (L-\d+)\n", text, re.M)]
    L_ID = "L-%02d" % (max(used + [0]) + 1)
    lasts = [i for i in have if i.startswith("L-")]
    at = block(text, lasts[-1])[1] if lasts else oi[0]
    text = text[:at] + "  - id: %s\n    class: LATER\n    status: OPEN\n%s" % (L_ID, L_TITLE) + text[at:]
    log.append("%s: added, the mock-up purchase (not approved by D-09)" % L_ID)

# ---------------------------------------------------------------- 4. FEA-007
FEA_PAGE = "v2/docs/CASE-FIT-UNCERTAINTIES.md"
FEA = """  - id: FEA-007
    kind: feasibility
    parent: NEED-06
    title: "the kit's fit in the Peli 1450 on the chosen arrangement (C1 to C6)"
    statement: >-
      The case set is drawn and computed on the design basis only (v2/release/case-2026-09-27/, CASE-MARGINS.md): 35 of
      the 70 case margins are OPEN, two of them (M17g and M17x, the east jumpers under their plugs) fail with the
      jumper plug as laid out, and 30 rest on allowances no source states (Peli publishes no case tolerance); the pack's
      hold-down, the rod stack's retention and the dock and blind-mate tolerance stack are not designed, and board A's
      J_AB2 stands 3.10 into board D (W4-F17). Nominal CAD establishes no fit, seal or alignment, and the bounds of
      the open rows include failure: eleven of them (the YES rows of CASE-FIT-UNCERTAINTIES.md section 2) would be
      remedied, if their check failed, by moving a board outline, a connector or a board part of A, B, E or P.
    acceptance: >-
      Every desk item of CASE-FIT-UNCERTAINTIES.md section 2 closed before its board's layout entry; for boards A, B,
      E and P, the physical checks of their YES rows (A: T4; B: T2, T4, T5, T10, T11; E: T10; P: T2, T4; with T1 at
      purchase) run on a new case of the current moulding with the made parts and stand-ins, and each YES row read at
      or above its minimum, or the board's outline or placement changed, before that board's layout entry; every
      board's committed layout re-read against those readings before its fabrication release; T3, T7, T8 and T9 at
      the build.
    feasibility_page: "%(page)s"
    blocker_ids: [M17g, M17x, M17d, M17f, M17w, M18, M13, M1, M4a, M5, M15b, W4-F17, DOCK, S-27]
    closing_evidence: >-
      The jumper plug's drawing with M17g and M17x re-computed MET on the design basis by v2/vendor/peli/frame_seat.py;
      PolyPhaser's O-ring dimension (M13); the Xenarc rear frame, the CM5 Cooler drawing and the named spacers (M1); the
      pack hold-down (S-27: M4a, M5); J_AB2 moved or board D's standoff re-derived (W4-F17); the dock and blind-mate
      stack written with board E's clamp bar and an ANT3 clamp (DOCK); board E's clamp lanes and pad places (M17f,
      M15b); then the mock-up's readings recorded against the rows of CASE-MARGINS.md section 7.
    owner: >-
      The session (the picks, the lookups, the hold-down, the dock stack, the frame_seat.py re-runs); board A's and
      board D's owners (W4-F17); board E's owner (the clamp bar, the lanes, the pads); the owner for money (the case,
      the frame and the mock-up's parts, READY-TO-ACT.md section 6, D-09: %(litem)s) and for any acceptance of the
      residual risk of entering layout on the design basis; an assembler with gauges for the checks.
    blocks: [REQ-019, CON-006, REQ-047]
    holds_layout_entry: [a, b, d, e, e5, p]
    stages:
      - stage: LAYOUT_ENTRY
        holds: [a, b, d, e, e5, p]
        needs: [DESK, BENCH_MOCKUP]
        status: OPEN
        requires: >-
          Per board, the desk items of CASE-FIT-UNCERTAINTIES.md section 2: board B, the jumper plug picked from a
          maker's drawing with M17g and M17x MET on the design basis, M13 bounded by PolyPhaser's O-ring dimension and
          the M1 lookups (Xenarc rear frame, CM5 Cooler drawing, named spacers); boards A and P, the pack hold-down
          (S-27) with M4a and M5; boards A and D, W4-F17 resolved; boards A, E and E5, the dock and blind-mate
          tolerance stack with board E's clamp bar (R4E-07) and an ANT3 clamp at X +46; board E, the clamp lanes
          (M17f) and the VHB pad places (M15b). Then, for boards A, B, E and P, the mock-up's checks of their YES
          rows on a new case of the current moulding (D-08a) with the made parts of v2/release/case-2026-09-27/, the
          picked jumper plugs on RG-316, one arrestor and stand-ins: A, T4 (M4a); B, T2 and T4 (M1, M18), T5 and T11
          (M18, M17w, M17x through M13), T10 (M17d, M17g, M17w, M17x); E, T10 (M17f); P, T4 and T2 (M4a, M5); T1 at
          purchase. Each YES row read at or above its minimum, or the board's outline or placement changed before its
          layout entry. BLOCKED on the owner's purchase decision (%(litem)s, D-09). Boards D and E5 need the desk
          items only.
      - stage: FABRICATION_RELEASE
        holds: [a, b, c, e, p, case]
        needs: [BENCH_MOCKUP, DESK]
        status: OPEN
        requires: >-
          Every board's committed layout re-read against the mock-up's readings (v2/vendor/peli/frame_seat.py re-run
          with the measured numbers, no row below its minimum), the made parts of v2/release/case-2026-09-27/ drawn to
          those numbers before they are cut for the prototype, and the rows whose remedy is a made part or a cable
          route (CASE-FIT-UNCERTAINTIES.md section 2, NO) confirmed on the mock-up or carried to the build with the
          reason stated there.
      - stage: PROTOTYPE_VERIFICATION
        holds: [case, kit]
        needs: [BUILT_KIT]
        status: OPEN
        requires: >-
          T3 (the plate dry-fit over Peli's o-ring), T7 (TEST-PLAN E6 and E7 with the twelve arrestors and both entry
          plates), T8 (the floor and the VHB bonds through E1 and E2) and T9 (the lid over the tray and the toggles) at
          the build, and REQ-047's lift-out demonstrated on the assembled prototype.
    stages_note: >-
      Staged on 27 September 2026 by the layer 7 closer and revised the same morning after the second review of the
      case release (AI review), the session's application of the owner's execution prompt of 27 September 2026 under
      his standing rule of 26 September 2026. A row a failing check would remedy by moving a board (a YES row) decides
      that board's outline or placement, which is the layout-entry decision, so its check is required at LAYOUT_ENTRY:
      the prompt admits a deferred physical test only where the current stage's decision does not depend on it
      (section 2) and forbids moving a decisive uncertainty to a later phase merely to unblock a status (section 5).
      The mock-up needs no board of this set, so the stage does not need what only a later stage produces
      (rules_lib.STAGE_CANNOT_NEED; the second review of 26 September 2026, section 2A). Purchase authority is not a
      reason to defer it; the first draft's FABRICATION_RELEASE allocation, which gave only that reason, is replaced.
      Reversal: the mock-up's readings at or above the YES rows' minimums lift the hold; the owner alone may instead
      accept, as his residual risk (residual_risk_accepted by OWNER under a ruling), entering layout on the design
      basis, and BENCH_MOCKUP then moves to FABRICATION_RELEASE with the layout-change risk named per board.
    allocated_to: [case, a, b, c, d, e, e5, p]
    verification_method: [CALCULATION, MANUAL_REVIEW, PROTOTYPE_MEASUREMENT]
    verification_phase: PLACED_BOARD
    final_phase: ASSEMBLY
    prototype_1: core
    prototype_1_basis: SESSION
    prototype_1_choice: SC-04
    prototype_1_why: "Fitting the boards, the plate and the pack into the 1450 is a condition of every core function (CONOPS section 2a), as for REQ-019."
    satisfied_by:
      rules: [MEC-001]
      decisions: []
    rule_coverage: PARTIAL
    rulings: [D-08-reversal, D-08a, D-09]
    choices: [SC-07]
    waits_on: [S-27, %(litem)s]
    status: FEASIBILITY_OPEN
    evidence_result: INCONCLUSIVE
    evidence_phase: PLACED_BOARD
    evidence_class: DESK_REVIEW
    evidence:
      - >-
          %(page)s read at its landing (sha256 first 16 %(sha)s): every OPEN row of frame_seat.out allocated to its
          physical check, each marked YES or NO by whether a failing check would move a board outline, connector or
          part; eleven YES rows hold the layout entry of boards A, B, E and P on the mock-up, which waits on the
          owner's purchase decision; M17g and M17x OPEN, FAILS AS ASSUMED (board B's east edge waits on the plug
          pick); the pack hold-down, W4-F17 and the dock stack undesigned. Board C's gate (MEC-001), with the board
          reading recorded by sha, reads PASS of 48 on the chosen arrangement and INCONCLUSIVE without the reading, a
          scratch reading the consolidated re-take records. Nothing here is measured, so the record is INCONCLUSIVE.
    evidence_bound_to:
      - "%(page)s@%(sha)s"
    release_effect: BLOCKER
    source:
      - "v2/docs/CASE-MARGINS.md"
      - "%(page)s"
      - "v2/docs/reviews/2026-09-27-handover-execution-prompt.md"
      - "session choice SC-07"
    source_check: VERIFIED
    notes: >-
      Created by the layer 7 closer (MESHSAT-1357, fnd/hc7) from the layer 7 audit of 27 September 2026: the computed
      layout-entry test had no case-geometry item, so a board could read ready for layout on geometry whose rows fail
      as assumed. The compact engineering question of the BLOCKED purchase is CASE-FIT-UNCERTAINTIES.md section 7.
      The review behind the case analysis is AI review; no qualified mechanical route exists yet
      (CASE-FIT-UNCERTAINTIES.md section 5).
"""
if re.search(r"^  - id: FEA-007\n", text, re.M):
    log.append("FEA-007: already present, not re-added")
else:
    assert os.path.isfile(os.path.join(ROOT, FEA_PAGE)), "%s is not in the tree: land the case release first" % FEA_PAGE
    rec = FEA % dict(page=FEA_PAGE, sha=sha16(FEA_PAGE), litem=L_ID)
    if not text.endswith("\n"): text += "\n"
    assert re.search(r"^records:\s*$", text, re.M) and not re.search(r"^[a-z_]+:", text[re.search(r"^records:\s*$", text, re.M).end():], re.M), \
        "records is no longer the last top-level key: place FEA-007 inside it by hand"
    text += rec
    log.append("FEA-007: added (bound to %s@%s)" % (FEA_PAGE, sha16(FEA_PAGE)))

# ---------------------------------------------------------------- 5. CON-006's acceptance: the mock-up before A and P enter layout
edit("CON-006",
     """      margin MET, none OPEN or NOT MET, and the fit is shown on hardware in a new case of that moulding: on a targeted
      unpowered mock-up before board A's east edge and board P's place are frozen for routing or, if it has not run by
      then, at the affected boards' fabrication release, which carries the rows it would have closed (CASE-MARGINS.md
      section 7).""",
     """      margin MET, none OPEN or NOT MET, and the fit is shown on hardware in a new case of that moulding, on the targeted
      unpowered mock-up before boards A and P enter layout (FEA-007): M4a and M5 can move board A's east edge and board
      P's place, so their check is not deferred (the owner's execution prompt of 27 September 2026, sections 2 and 5;
      v2/docs/CASE-FIT-UNCERTAINTIES.md sections 1 and 2; CASE-MARGINS.md section 7).""",
     "acceptance: the mock-up before boards A and P enter layout, not at their fabrication release")
b_ = block(text, "CON-006"); body_ = text[b_[0]:b_[1]]
if ("waits_on: [S-27, %s]" % L_ID) in body_:
    log.append("CON-006: waits on %s already" % L_ID)
else:
    edit("CON-006", "    waits_on: [S-27]\n", "    waits_on: [S-27, %s]\n" % L_ID, "waits on %s, the mock-up purchase" % L_ID)

# ---------------------------------------------------------------- 6. --rebind
if "--rebind" in ARGS:
    now = sha16("v2/docs/CASE-MARGINS.md")
    if now == OLD_CM.split("@")[1]:
        log.append("rebind: CASE-MARGINS.md is still 275a3083db30a7bf, nothing to rebind")
    else:
        cm_now = open(os.path.join(ROOT, "v2/docs/CASE-MARGINS.md"), encoding="utf-8").read()
        fs_moved = ("M18's part list read from the committed board B and U51's 1.60 sourced to ST's maximum (DS12117 Rev 9 Table 217)"
                    if "the E72 module U14's 7.76" in cm_now else "")
        ids = [m.group(1) for m in re.finditer(r"^  - id: (\S+)\n", text, re.M)]
        for rid in ids:
            b = block(text, rid); body = text[b[0]:b[1]]
            if ('"%s"' % OLD_CM) not in body: continue
            note = ("      - >-\n          v2/docs/CASE-MARGINS.md re-read at %s (MESHSAT-1357 layer 7, 27 September 2026): the edit adds the note that "
                    "C1 to C6 are implemented in CAD (v2/release/case-2026-09-27/), labels the agent checks behind its revisions as AI review, "
                    "points the dock and blind-mate stack to CASE-FIT-UNCERTAINTIES.md and revises section 7's timing (the targeted mock-up "
                    "before the layout entry of the boards a failing check would move, A, B, E and P, BLOCKED on the owner's purchase "
                    "decision, where it had been carried to their fabrication release), and brings its opening summary, its paragraph on why "
                    "the document exists and finding 23 to that timing%s; no figure or verdict of section 3 moved, so this "
                    "reading stands on the file at %s\n" % (now, ("; with the frame_seat.py draft, " + fs_moved) if fs_moved else "", now))
            new = body.replace('"%s"' % OLD_CM, '"v2/docs/CASE-MARGINS.md@%s"' % now)
            k = new.find("    evidence_bound_to:")
            assert k > 0, "%s: bound to CASE-MARGINS.md without an evidence_bound_to list" % rid
            new = new[:k] + note + new[k:]
            text = text[:b[0]] + new + text[b[1]:]
            log.append("%s: rebound to CASE-MARGINS.md@%s" % (rid, now))

    # ASSEMBLY.md (drafts/hc7/ASSEMBLY.md.patch, made against main 84e52461): CFL-015 reads its Pack SMBus row and build step 7, which the
    # patch leaves byte-identical. The rebind is made only after checking that on the file in the tree, against the sha256/16 of the two lines
    # at the version the record is bound to (e3aedb25's e4a0b78616c69779 or 84e52461's 30db27eee509212c, whichever the registry carries).
    KNOWN_ASM = {"e4a0b78616c69779": {"smbus": "2bd3095d9c8cb35f", "step7": "5dc1d7d3f9e4be02"},
                 "30db27eee509212c": {"smbus": "93af769301e9db9f", "step7": "5dc1d7d3f9e4be02"}}
    now_a = sha16("v2/docs/ASSEMBLY.md")
    asm = open(os.path.join(ROOT, "v2/docs/ASSEMBLY.md"), encoding="utf-8").read().splitlines()
    got = {"smbus": [l for l in asm if l.startswith("| Pack SMBus ")], "step7": [l for l in asm if l.startswith("7. Pack into the east pocket")]}
    for old_sha, want in KNOWN_ASM.items():
        if now_a == old_sha: continue
        OLD_ASM = "v2/docs/ASSEMBLY.md@%s" % old_sha
        same = all(len(got[k]) == 1 and hashlib.sha256(got[k][0].encode("utf-8")).hexdigest()[:16] == want[k] for k in want)
        ids = [m.group(1) for m in re.finditer(r"^  - id: (\S+)\n", text, re.M)]
        for rid in ids:
            b = block(text, rid); body = text[b[0]:b[1]]
            if ('"%s"' % OLD_ASM) not in body: continue
            if not same:
                log.append("%s: bound to ASSEMBLY.md at %s and the Pack SMBus row or build step 7 changed: re-read by hand" % (rid, old_sha)); continue
            note = ("      - >-\n          v2/docs/ASSEMBLY.md re-read at %s (MESHSAT-1357 layer 7, 27 September 2026): the edit corrects the case rows to "
                    "C1 to C6 (the face plate, the legs and frame, the connector and RF entry plates, the jumpers, the QMX tray, the lid space, "
                    "the pack's pocket, the bench list), states the mock-up timing of CASE-FIT-UNCERTAINTIES.md in items (11) and (13) and "
                    "section 3's pack paragraph, and points the QMX tray row at the case release's lid-tray-qmx/ and sheet 14; the Pack "
                    "SMBus row of section 4 and build step 7, which this reading cites, are "
                    "byte-identical, so it stands on the file at %s\n" % (now_a, now_a))
            new_body = body.replace('"%s"' % OLD_ASM, '"v2/docs/ASSEMBLY.md@%s"' % now_a)
            k = new_body.find("    evidence_bound_to:")
            assert k > 0, "%s: bound to ASSEMBLY.md without an evidence_bound_to list" % rid
            new_body = new_body[:k] + note + new_body[k:]
            text = text[:b[0]] + new_body + text[b[1]:]
            log.append("%s: rebound to ASSEMBLY.md@%s" % (rid, now_a))

for line in log: print("apply_registry:", line)
if text == orig:
    print("apply_registry: nothing to change"); sys.exit(0)
if DRY:
    print("apply_registry: --dry-run, %s not written" % REG); sys.exit(0)
open(REG, "w", encoding="utf-8").write(text)
print("apply_registry: wrote %s; run python3 v2/ecad/tools/rules_lib.py requirements" % REG)
