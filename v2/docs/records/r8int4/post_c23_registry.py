"""After fnd/hc3's apply_registry.py on the r8int4 tree: CFL-016's two hand re-reads (the script printed HAND RE-READ
for CONOPS and V2-SPEC), and verify c23's present-tense statements in REQ-024 and FEA-004 restated as what REQ-077
requires and the design intends. Edits by record id with asserted old text. Run from the worktree root."""
import hashlib
P = 'v2/ecad/tools/pcb_requirements.yaml'
t = open(P).read()
def rec(t, rid):
    i = t.index('\n  - id: %s\n' % rid) + 1
    j = t.find('\n  - id: ', i + 5)
    return i, (j + 1 if j > 0 else len(t))
def sub_in(t, rid, a, b):
    i, j = rec(t, rid); r = t[i:j]
    assert r.count(a) == 1, (rid, r.count(a), a[:80]); assert a != b
    return t[:i] + r.replace(a, b) + t[j:]
def sha16(p): return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
CON, SPEC = sha16('v2/docs/CONOPS.md'), sha16('v2/docs/V2-SPEC.md')
# CFL-016: the two bindings the script left for a hand re-read
t = sub_in(t, 'CFL-016', '      - "v2/docs/CONOPS.md@cedb60bf2ca88822"\n', '      - "v2/docs/CONOPS.md@%s"\n' % CON)
t = sub_in(t, 'CFL-016', '      - "v2/docs/V2-SPEC.md@41edfc2e2e3f1961"\n', '      - "v2/docs/V2-SPEC.md@%s"\n' % SPEC)
anchor = "          SDR), is byte-identical to the file at 86742b72d44adce6, so it stands on the file at a0de0b12ff06ba4e\n"
new = anchor + """      - >-
          v2/docs/CONOPS.md re-read by hand at the r8int4 integration of 27 September 2026 (branch fnd/r8int4, main
          38dcd764 with the layer-2 closer's pass-3 file merged and the layer-1 closer's held EMCON and face
          corrections re-derived onto board B's round 8): the apply script's anchors are present but one, the EMCON
          row's "the 5G module in airplane mode through its disable pin", which now reads that the 5G module's supply
          is removed by hardware with its disable pins pulled low at the same moment (board B's round 8: U215, U220,
          Q212 and R295 on the committed netlist at adcc3c6736c90e9f); the same row and section 4b's RockBLOCK row now
          say that the module runs on its own two 10 F supercapacitors with its ENABLE held by the firmware expander U6
          once its supply gate U503 opens (feasibility/EMCON.md section 4.4), the row's owed list follows
          feasibility/EMCON.md sections 0a and 4b, the paragraph after section 4b's table gives section 0a's counts (15
          of 17 local, 0 of 17 end to end) and the Service row names the ten 6-32 screws of case choice C1; the other
          section 4b rows, the ZEROIZE row, the device rail's pull-up R42, the wall data path at J_USBW, the outlet
          interlock U30, the lid switch (v2/ecad/tools/gen_sch_e.py:524-542) and the D-15 floor are as the script
          read them. Every changed sentence describes the circuit as generated at 38dcd764, so it stands on the file
          at %s
      - >-
          v2/docs/V2-SPEC.md re-read by hand at the r8int4 integration of 27 September 2026: line 41 changed only in its
          closing clause (the eSIM variant's order code owed under S-13, conflict CFL-010 resolved on this
          description, correction 22), line 29 gained NEED-03's failure set (correction 29), corrections 22 and 28
          now say the SIM TVS arrays are drawn since board B's round 8 and are carried outside CFL-010, and correction
          29 is new; lines 24, 34, 43 and 76 and corrections 2, 4, 7, 9, 12, 13, 19, 26 and 27, which this reading
          also rests on, are byte-identical to the file at 41edfc2e2e3f1961, and line 41's circuit description (the
          key-B socket, its locating holes, the two nano-SIM holders and their TPD4E001 arrays) is unchanged, so it
          stands on the file at %s
""" % (CON, SPEC)
t = sub_in(t, 'CFL-016', anchor, new)
# REQ-024: the hot stop as what REQ-077 requires and the design intends
t = sub_in(t, 'REQ-024', """      (the hot stop past the heat stage, REQ-077, keeps the cells inside +60 C and is not a carve-out: whether
      it acts inside the envelope is FEA-004's,""", """      (the hot stop past the heat stage is not a carve-out: REQ-077 requires the kit to act before any cell passes
      +60 C, and the design intends the stop to do so once HOT-R1 is drawn on boards A and E, S-57, REQ-077 reading
      FAIL on the generated boards until then, on the provisional error budget of TEST-PLAN P14; whether it acts
      inside the envelope is FEA-004's,""")
# FEA-004: the same sentence in its notes
t = sub_in(t, 'FEA-004', """      stage criteria (TEST-PLAN E3-L) and REQ-024's use at +40 C are not met there, while the stop keeps the cells
      inside +60 C; and NEED-03""", """      stage criteria (TEST-PLAN E3-L) and REQ-024's use at +40 C are not met there, while REQ-077 requires the stop to
      keep the cells inside +60 C and the design intends it to (REQ-077 reads FAIL on the generated boards until HOT-R1
      is drawn on boards A and E, S-57, and H2 leaves 0.93 K for the error budget's two TBD terms, TEST-PLAN P14): this
      feasibility is open; and NEED-03""")
open(P, 'w').write(t)
print("post_c23_registry: CFL-016 rebound to CONOPS %s and V2-SPEC %s; REQ-024 and FEA-004 restated" % (CON, SPEC))
