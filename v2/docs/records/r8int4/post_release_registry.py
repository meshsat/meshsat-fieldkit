"""After edit_release_fixes.py (the release check of layers 1 to 3, 27 September 2026, MESHSAT-1357, fnd/r8int4 at
6209ec7e): (1) the readings whose bound files those wording fixes changed, each re-read by hand against the sections the
fixes touched (CONOPS: the status header, M4, section 4's Reduced row, 4a's A06 sentence, 4b.1, 4c's opening and 4f's
5G row; V2-SPEC lines 10, 23, 24, 59 and 76, correction 20's last sentence and a new correction 30; PANEL section 1's
Indicators row and section 9's lamp-test sentence; TEST-PLAN section 4's trace line; OPERATING-ENVELOPE section 4's
pack row and operating-modes paragraph); (2) S-01's and S-44's titles restated to what remains after the round 8
circuits (layer 2 release check, finding B4 (b)); (3) the CONOPS needs pin (the needs table is unchanged) and the
envelope's two pins. Edits by record id with asserted old text. Run from the worktree root."""
import hashlib
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
    assert entry.split('\n')[1].strip().startswith(path), (rid, path)
    return t[:i] + r[:k] + entry + r[k:] + t[j:]


I = ("re-read at the release check of layers 1 to 3 of 27 September 2026 (fnd/r8int4, after the release reviews at "
     "f2b7fa66, v2/docs/reviews/REVIEW-LAYER-1-RELEASE-2026-09-27.md and REVIEW-LAYER-2-RELEASE-2026-09-27.md): ")
CON_CH = ("the status header (the filed Review A records and the release review), section 3's M4 (the 5G row's 20 s as "
          "REQ-071's with board B's round 8 supply removal), section 4's Reduced row (FW-C09 and ARCHITECTURE's PS-RED row "
          "named as hand-offs), section 4a's A06 sentence (its records filed), section 4b.1 (the 5G row, the lamp D22 drawn, "
          "the operator's lead as REQ-071's bound, the state at 15 of 17 local), section 4c's opening (the hand-offs) and "
          "section 4f's 5G EMCON cell change; ")
SPEC_CH = ("lines 10 (the case generators carry C2 since c351115d), 23 (the CONOPS runtime cross-reference), 24 and 76 "
           "(the hardware EMCON lamp drawn on board C, its light guide owed), 59 (a seventeenth LED) and correction 20's "
           "last sentence change and correction 30 is added; ")
PANEL_CH = ("section 1's Indicators row (D22 counted as the face's seventeenth LED, its light guide owed) and section 9's "
            "lamp-test sentence (D22 not among the seventeen controller-lit indicators; the lamp test cannot light it) "
            "change; ")
TP_CH = ("only section 4's trace line changes (the EMCON lamp named D22, REQ-071 added to what the functional check "
         "verifies); ")
OE_CH = ("only section 4 changes: the pack row names the filed A06 records (v2/docs/records/adj/A06-pack-geometry/), and "
         "the operating-modes paragraph states board B's round 8 removal of the 5G module's supply and names what EMCON "
         "work remains; no number changed; ")

C = 'v2/docs/CONOPS.md'; S = 'v2/docs/V2-SPEC.md'; PN = 'v2/docs/PANEL.md'; T = 'v2/docs/TEST-PLAN.md'
O = 'v2/docs/OPERATING-ENVELOPE.md'
OLD = {C: '4887ada07f50d808', S: '73a797e44d42fa6d', PN: '4bcbf31f44560ee1', T: 'a0de0b12ff06ba4e',
       O: '6e4bbde9dbf7e136'}

# (1) the rebinds, one entry per record and file, each saying what that record rests on
t = rebind(t, 'REQ-005', C, OLD[C], C + " " + I + CON_CH + "section 2a, which this reading rests on, is byte-identical to "
           "the file at 4887ada07f50d808, so it stands on the file at %s")
t = rebind(t, 'REQ-005', S, OLD[S], S + " " + I + SPEC_CH + "line 32 and correction 6, which this reading rests on, are "
           "byte-identical to the file at 73a797e44d42fa6d, so it stands on the file at %s")
t = rebind(t, 'CFL-001', PN, OLD[PN], PN + " " + I + PANEL_CH + "line 5 (bank 1's home and failover hosts) and section 2's "
           "ribbon table with its pin 15 row, which this reading rests on, are byte-identical, and section 1 changes only "
           "in its Indicators row, which this reading does not cite, so it stands on the file at %s")
t = rebind(t, 'CON-018', T, OLD[T], T + " " + I + TP_CH + "the M7 row, which this reading rests on, is byte-identical to "
           "the file at a0de0b12ff06ba4e, so it stands on the file at %s")
t = rebind(t, 'CFL-005', PN, OLD[PN], PN + " " + I + PANEL_CH + "section 7's panel-absent paragraph, which this reading "
           "cites, is byte-identical, so it stands on the file at %s")
t = rebind(t, 'REQ-050', T, OLD[T], T + " " + I + TP_CH + "every table still carries its Purpose and Verifies columns, "
           "each filled on every row (46 rows, E10 out of scope), section 4 still states its purpose and the requirements "
           "it verifies, now naming REQ-071, a live record, beside REQ-030 to REQ-032, and no row's purpose changed, so "
           "it stands on the file at %s")
t = rebind(t, 'CFL-016', PN, OLD[PN], PN + " " + I + PANEL_CH + "section 1's Indicators row describes board C's round 8 "
           "lamp D22 through U14 and Q7 as the committed netlist v2/ecad/pcb-c-display-c8/out/pcb-c-display.net at "
           "11eabc2dddca5161 carries it, which is this record's acceptance, and sections 6 and 7 are byte-identical, so it "
           "stands on the file at %s")
t = rebind(t, 'CFL-016', C, OLD[C], C + " " + I + CON_CH + "M4, section 4b.1 and section 4f's 5G cell now state the 5G "
           "module's supply removed by hardware at once (U215, U220, Q212 and R295 on the committed netlist "
           "v2/ecad/pcb-b-compute-b19/out/pcb-b-compute.net at adcc3c6736c90e9f) and the lamp D22 drawn on board C, "
           "which is this record's acceptance, the Reduced row changes only in naming the hand-offs, and section 4's other "
           "rows, section 4a's PS-EMCON row, section 4b and section 5 are byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-016', S, OLD[S], S + " " + I + SPEC_CH + "line 24 keeps its description of the circuit as generated "
           "and changed only in saying the lamp is drawn (D22 on the committed board C netlist at 11eabc2dddca5161), line 76 "
           "now names the lamp's light guide as the owed item, and lines 34, 41 and 43 and corrections 2, 4, 7, 9, 12, 13, "
           "19, 26, 27 and 28 are byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-016', O, OLD[O], O + " " + I + OE_CH + "section 4's EMCON paragraph now also states the 5G module's "
           "supply removed by hardware at once (board B's round 8, as generated), which is this record's acceptance, and "
           "section 2's protection-board row and section 3 are byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-016', T, OLD[T], T + " " + I + TP_CH + "the EMCON sentence of section 4's functional check (measured "
           "with a receiver outside the kit, never the kit's own SDR), which this reading rests on, is byte-identical, so "
           "it stands on the file at %s")
for rid, what in (('CFL-007', "every test row's purpose and the requirements it verifies (46 rows)"),
                  ('CFL-008', "rows E5 (the sealed kit) and E8 (Peli's pressure valve)"),
                  ('CFL-009', "section 1's deployed closed-lid state and section 6's closed-lid thermal test E3-L")):
    t = rebind(t, rid, T, OLD[T], T + " " + I + TP_CH + what + ", which this reading rests on, byte-identical to the "
               "file at a0de0b12ff06ba4e, so it stands on the file at %s")
t = rebind(t, 'CFL-010', S, OLD[S], S + " " + I + SPEC_CH + "line 41 (the one dual-SIM description, SC-13), which this "
           "reading rests on, is byte-identical to the file at 73a797e44d42fa6d, so it stands on the file at %s")
t = rebind(t, 'CFL-013', S, OLD[S], S + " " + I + SPEC_CH + "line 35 and correction 8, which this reading rests on, are "
           "byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-014', PN, OLD[PN], PN + " " + I + PANEL_CH + "section 10, which this reading cites, is byte-identical, "
           "so it stands on the file at %s")
t = rebind(t, 'CFL-014', C, OLD[C], C + " " + I + CON_CH + "section 4's Charging row and section 5's case S4, which this "
           "reading rests on, are byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-014', O, OLD[O], O + " " + I + OE_CH + "section 3's paragraph beginning '**Corrected 26 September "
           "2026.** This pa', which this reading rests on, is byte-identical, so it stands on the file at %s")
t = rebind(t, 'CFL-015', PN, OLD[PN], PN + " " + I + PANEL_CH + "section 10's SMBus sentences, which this reading cites, "
           "are byte-identical, so it stands on the file at %s")

# (2) S-01 and S-44 restated to what remains (layer 2 release check, B4 (b)); the ids and classes are unchanged
t = sub_in(t, 'S-01', """      EMCON reaches every transmitter (D-05), what is left after 458b2873 gated the compute modules' radios and the
      WiFi card supplies: SD-EMC-1's two stages for the 5G module drawn on board B; the shared-line items L1 to L4 and
      L7 of EMCON.md section 7 remedied (firmware pins on EMCON_HW, the line's hold with its source gone, the +3V3_DEV
      loss that releases nine radios, gate supplies outside their range, the 2N7002 drive); the back-feed paths of
      SD-EMC-2.""",
"""      EMCON reaches every transmitter (D-05), what is left after 458b2873 gated the compute modules' radios and the
      WiFi card supplies and the round 8 circuits of boards A to D drew the rest of this item (EMCON.md sections 4a, 4b
      and 7: the 5G module's supply removed by hardware at once on board B, SD-EMC-1r8, in place of SD-EMC-1's two
      stages; L1 remedied on boards B and C, L2 on boards A and B, L3 and L7 on board B, L4 on boards A and D): L4 case
      (2), the gate supplies of U501 to U505 below their specified range on board B (bench E-11), and the back-feed
      paths of SD-EMC-2 into the RockBLOCK, the E22 and both E72 (open) and both AW7915 cards (no maker floor to judge
      against). Restated 27 September 2026 at the release check of layer 2 (finding B4 (b)); the item's scope is
      unchanged.""")
t = sub_in(t, 'S-44', """      The hardware EMCON lamp on board C, driven from the line state with no processor in its path, and its light-guide
      hole in the face plate (SD-EMC-6, EMCON.md section 7).""",
"""      The hardware EMCON lamp's light-guide hole in the face plate beside SW_EMCON (SD-EMC-6, EMCON.md section 7). The
      lamp itself, driven from the line state with no processor in its path, is drawn on board C since its round 8 (D22
      through U14 and Q7). Restated 27 September 2026 at the release check of layer 2 (finding B4 (b)).""")

# (3) the CONOPS needs pin: the needs table (section 2) is unchanged
old_pin = "needs_document_sha256: 4887ada07f50d808c019129322fc3fde642b83e8de627033c7180eb1c94e8238"
assert t.count(old_pin) == 1; t = t.replace(old_pin, "needs_document_sha256: " + full(C))
open(P, 'w').write(t)
# the envelope's two pins: OPERATING-ENVELOPE changed in section 4 only, no number
OLDF = "6e4bbde9dbf7e136fee540b0418edbaaf5007f6ad604d5783d747b4102c0c4e6"; NEWF = full(O)
for p, a, b in (('v2/ecad/tools/pcb_envelope.yaml',
                 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after section 4\'s pack row took' % OLDF,
                 'document_sha256: "%s"   # re-read and re-pinned 27 September 2026 by the integrator after the release check of layer 2 (section 4\'s operating-modes paragraph states board B\'s round 8 removal of the 5G module\'s supply and the pack row names the filed A06 records; no number changed), before it after section 4\'s pack row took' % NEWF),
                ('v2/ecad/tools/pcb_rules_coverage.yaml', 'verified_sha: "%s",' % OLDF, 'verified_sha: "%s",' % NEWF)):
    s = open(p).read(); assert s.count(a) == 1, p; open(p, 'w').write(s.replace(a, b))
print("post_release_registry: 20 rebinds, S-01 and S-44 restated, needs pin and envelope pins re-taken")
