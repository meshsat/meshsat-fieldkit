"""S-61 carried as board D's layout-entry item (hc5 review 2, HF-F06's severity), and HW-FW-CONTRACT.md's change record
for the integration. Run from the worktree root."""
P = 'v2/ecad/tools/pcb_requirements.yaml'; t = open(P).read()
a = """      controller's measured draw, which USB 2.0 section 7.2.1 bounds at 100 mA unconfigured and 500 mA configured (V-B19).
"""
b = """      controller's measured draw, which USB 2.0 section 7.2.1 bounds at 100 mA unconfigured and 500 mA configured (V-B19).
      Carried before board D's layout entry (r8int4, after hc5's second review: a fault on the touch lead removes board D,
      whose APRS path is a prototype 1 core function under D-01, so HF-F06 is major).
"""
i = t.index('\n  - id: S-61\n'); j = t.index('\n  - id: ', i + 5) + 1
assert t[i:j].count(a) == 1; t = t[:i] + t[i:j].replace(a, b) + t[j:]; open(P, 'w').write(t)
H = 'v2/docs/HW-FW-CONTRACT.md'; h = open(H).read()
last = [l for l in h.split('\n') if l.startswith('| 1 (second review fixes) |')]; assert len(last) == 1
row = ("| 1 (integration) | 27 September 2026 | Merged at the r8int4 integration onto `main` `38dcd764` (board B's round 8 there): "
       "the registry takes S-59 (SC-HF-02), S-60 (HF-F02), S-61 (SC-HF-06 and HF-F06), S-62 (HF-F07) and CON-026 (the kit bus "
       "rise time); PANEL.md section 7's new paragraph gives the weakest targets' 3 mA as the sink their datasheets rate at "
       "0.4 V (the claims screen, ENV-002); V-B19 moved into section 5; FW-A08 counts six expanders; HF-F06 raised to major "
       "and carried before board D's layout entry; `ARCHITECTURE.md` section 12 keeps board B's round 8 facts on IF-BC-PANEL; "
       "IF-AE-RF and the section 2 and W4-F10 lines of `ARCHITECTURE.md` say board E's cavity at X 46 is drawn; IF-E-WATER, "
       "IF-E-SENSORS, IF-DA-VHF, IF-MON and IF-EXT-DC take the second review's wording items; the handover pages carry "
       "SC-HF-06 where they named the touch lead |")
h = h.replace(last[0], last[0] + '\n' + row, 1); open(H, 'w').write(h)
print("post_c5_registry2: done")
