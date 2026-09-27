"""After fnd/hc7's patches and apply_registry.py --rebind on the r8int4 tree, and the integrator's timing edits:
(1) REQ-019's acceptance follows the adopted timing (verify c7: no fabrication-release fallback); (2) a new open item
for the QMX lid tray's fit (c7's finding); (3) the readings whose bound files these edits moved, each re-read by hand
(the changed lines are CONOPS 4a's pack paragraph and section 7's D-06 row, V2-SPEC correction 18, OPERATING-ENVELOPE
section 4's pack row, ASSEMBLY's case-set rows and pack_4s.py's banner); (4) the CONOPS needs pin (its needs table is
unchanged) and the envelope's two pins. Edits by record id with asserted old text. Run from the worktree root."""
import hashlib, re, subprocess
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
full = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1; j = t.find('\n  - id: ', i + 5); return i, (j + 1 if j > 0 else len(t))
def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]; assert r.count(a) == 1, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]
def rebind(t, rid, path, old, text):
    new = full(path)[:16]
    t = sub_in(t, rid, '"%s@%s"' % (path, old), '"%s@%s"' % (path, new))
    i, j = rec(t, rid); r = t[i:j]; k = r.index('    evidence_bound_to:')
    words = (text % new).split(); lines = []; cur = '         '
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = '          ' + w
        else: cur = cur + ' ' + w
    lines.append(cur)
    entry = '      - >-\n' + '\n'.join(lines) + '\n'
    return t[:i] + r[:k] + entry + r[k:] + t[j:]
I = "re-read at the r8int4 integration of 27 September 2026 after the layer 7 closer's case timing (fnd/hc7, c7) and the integrator's edits for verify c7: "
CON = ("v2/docs/CONOPS.md " + I + "only section 4a's pack paragraph and section 7's D-06 row change (the targeted mock-up before boards A and P "
       "enter layout, in place of 'a mock-up at the build'); the needs table and sections 2a, 3, 4, 4a's PS-EMCON row, 4b and 5, which this "
       "reading rests on, are byte-identical to the file at eb0eda7cacfe7156, so it stands on the file at %s")
SPEC = ("v2/docs/V2-SPEC.md " + I + "only correction 18 changes, gaining the mock-up's timing since 27 September 2026 (FEA-007); the lines and "
        "corrections this reading rests on are byte-identical to the file at a02ea1b6801f8916, so it stands on the file at %s")
OE = ("v2/docs/OPERATING-ENVELOPE.md " + I + "only section 4's pack row changes (M4a and M5 open until the targeted mock-up before boards A "
      "and P enter layout, in place of 'a mock-up at the build'); section 2's protection-board row, section 3 and section 4's EMCON "
      "paragraph are byte-identical to the file at 9f16f5b7d634764a, so it stands on the file at %s")
for rid in ('REQ-005', 'CFL-016', 'CFL-014'):
    t = rebind(t, rid, 'v2/docs/CONOPS.md', 'eb0eda7cacfe7156', CON)
for rid in ('REQ-005', 'CFL-016', 'CFL-010', 'CFL-013'):
    t = rebind(t, rid, 'v2/docs/V2-SPEC.md', 'a02ea1b6801f8916', SPEC)
for rid in ('CFL-016', 'CFL-014'):
    t = rebind(t, rid, 'v2/docs/OPERATING-ENVELOPE.md', '9f16f5b7d634764a', OE)
t = rebind(t, 'CFL-015', 'v2/docs/ASSEMBLY.md', '3a8897ef6d717a30',
    "v2/docs/ASSEMBLY.md " + I + "the case set C1 to C6 rows, step 0, the jumpers, the plate, the lid space, the pocket, the QMX tray row and "
    "notes (11) and (13) change, and build step 9 keeps the layer 5 closer's touch-lead clause beside the case set's; section 4's Pack SMBus "
    "row and build step 7, which this reading cites, are byte-identical to the file at 3a8897ef6d717a30, so it stands on the file at %s")
t = rebind(t, 'CFL-006', 'v2/cad/pack_4s.py', 'cfa8fed3affab289',
    "v2/cad/pack_4s.py " + I + "the layer 7 closer added a SUPERSEDED banner (lines 2 to 6) that names D-06's one 4S3P block and S-27; the "
    "box below it still draws the wrapped 4S4P block (line 10 and CELLS, line 20), and no enclosure or hold-down for the 4S3P block exists, "
    "so the FAIL stands on the file at %s")
# (1) REQ-019's acceptance: the adopted timing, with no fabrication-release fallback
t = sub_in(t, 'REQ-019', """      the OPEN rows shown on hardware in a new case of that moulding: the targeted checks of CASE-MARGINS.md section 7
      before the affected board outlines and connector placements freeze or, if they have not run by then, at the
      affected boards' fabrication release (CASE-MARGINS.md section 7), the rest at the build.""",
"""      the OPEN rows shown on hardware in a new case of that moulding: the targeted checks of CASE-MARGINS.md section 7 of
      the rows that can move a board before the layout entry of boards A, B, E and P, which is held on them (FEA-007,
      v2/docs/CASE-FIT-UNCERTAINTIES.md sections 1, 2 and 7), the rest at the build. Restated 27 September 2026 at the
      r8int4 integration (verify c7): the earlier clause carried the targeted checks to the affected boards' fabrication
      release if they had not run before the outlines froze; CASE-MARGINS.md section 7 withdrew that fallback, so it is
      withdrawn here too.""")
# (2) the QMX lid tray's fit, a new open item
ANCHOR = "\n# Items that left the open list, and what closed each"
nums = [int(x) for x in re.findall(r"\n  - id: S-(\d+)\n", t)]; sid = "S-%d" % (max(nums) + 1)
assert "(r8int4: the QMX lid tray)" not in t
block = """  - id: %s
    class: SESSION
    status: OPEN
    title: >-
      (r8int4: the QMX lid tray) The QMX lid tray released in v2/release/case-2026-09-27/lid-tray-qmx/ (sheet 14) does not
      fit the unit's connector layout: the held QRP Labs QMX manual (1_04_004, pages 7 to 9) puts the DC jack on the
      left panel and the BNC and USB-C on the right panel, and the tray has notches in one end wall only; the unit's
      95 x 63 x 25 and the notch heights are checked against no maker drawing. Revise the tray from the QMX enclosure
      drawing before it is printed (v2/docs/CASE-FIT-UNCERTAINTIES.md section 3; the layer 7 fixer c7). Desk work on a
      made part: no board moves (J_QMX, J_HF and J_RF2 stay) and nothing is bought. ENGINEERING-QUESTIONS EQ-24.
""" % sid
assert t.count(ANCHOR) == 1
t = t.replace(ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR, 1).replace("\n\n" + block.rstrip("\n") + "\n" + ANCHOR, "\n" + block.rstrip("\n") + "\n" + ANCHOR)
# (4) the CONOPS needs pin: the needs table is unchanged (only 4a's pack paragraph and section 7's D-06 row moved)
old_pin = "needs_document_sha256: eb0eda7cacfe71566135b12d1ca0d5bab5e1b0a63517b0e84af970d62853a20c"
assert t.count(old_pin) == 1; t = t.replace(old_pin, "needs_document_sha256: " + full('v2/docs/CONOPS.md'))
open(P, 'w').write(t)
# the envelope's two pins: OPERATING-ENVELOPE changed in section 4's pack row only, no number
OLD = "9f16f5b7d634764a7f4cc28f58bc9a76de93c6762da57b8ea7cd419e5790fa20"; NEW = full('v2/docs/OPERATING-ENVELOPE.md')
for p, a, b in (('v2/ecad/tools/pcb_envelope.yaml', 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after section 4\'s hot-stop paragraph' % OLD,
                 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after section 4\'s pack row took the mock-up\'s timing (before boards A and P enter layout; no number changed), before it after section 4\'s hot-stop paragraph' % NEW),
                ('v2/ecad/tools/pcb_rules_coverage.yaml', 'verified_sha: "%s",' % OLD, 'verified_sha: "%s",' % NEW)):
    s = open(p).read(); assert s.count(a) == 1, p; open(p, 'w').write(s.replace(a, b))
print("post_c7_registry: rebinds done; %s added; needs pin and envelope pins re-taken" % sid)
