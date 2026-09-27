#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): writes apply_registry_r8int6.py and
patch_docs_r8int6.py beside stream w4c's apply_registry.py and patch_docs.py, by asserted text replacement, so the filed
copies are whole scripts. What changes, and why:
  - W4C-F5's open item: the 24 mV figure is said to be at nominal capacitance (MLCC tolerance and DC bias lower it, and
    U5's current limit is not in the arithmetic), and the bring-up reading also captures Q5's and L1's peak current
    (PDi's 0.8 A inductor and UltraChip's 1.2 A Isat reference): the independent check (w4c check 2, an AI check).
  - RF-002's coverage row and EQ-25's attempts: board B's own ten failures on main's walk are named as stream w4b's,
    whose rows and circuit land in the same integration ahead of this stream (EMCON.md 4c).
  - FEA-002's EMCON.md re-read note: the items it names as remaining are the ones still remaining after stream w4b
    (which drew the RockBLOCK's ENABLE, closed L4 case (2) on U501 to U504 and landed the walk's rows).
  - HW-FW-CONTRACT.md: the fnd/w4c row follows the fnd/w4b row, and says no FW-C row covers RAIL_SENSE yet (the check).
Usage: derive_w4c_r8int6.py <kit dir>"""
import os, sys

K = sys.argv[1]


def derive(src, dst, swaps, head):
    s = open(os.path.join(K, src), encoding="utf-8").read()
    for old, new in swaps:
        assert s.count(old) == 1, "%s: %d of %r" % (src, s.count(old), old[:90])
        s = s.replace(old, new)
    assert s.startswith('#!/usr/bin/env python3\n"""')
    s = s.replace('#!/usr/bin/env python3\n"""', '#!/usr/bin/env python3\n"""' + head + "\n\n", 1)
    compile(s, dst, "exec")
    open(os.path.join(K, dst), "w", encoding="utf-8").write(s)
    print("wrote", dst)


derive("apply_registry.py", "apply_registry_r8int6.py", [
    ('"on-phase, is at most 0.35 uC, 24 mV on C2, C28 and C29 (14.8 uF nominal) against the rail\'s 99 mV budget, but what "',
     '"on-phase, is at most 0.35 uC, about 24 mV on C2, C28 and C29 at their nominal 14.8 uF (MLCC tolerance and DC bias at "\n'
     '        "3.3 V lower the effective capacitance, and the arithmetic leaves out U5\'s current limit, at least 560 mA; corrected "\n'
     '        "at integration from the independent check) against the rail\'s 99 mV budget, but what "'),
    ('"DAY: closed when +3V3 stays inside its 3 percent budget and U5\'s average at or under 500 mA; otherwise board C\'s "',
     '"DAY, capturing Q5\'s and L1\'s peak current as well (PDi\'s driving-circuit note specifies a 0.8 A inductor and "\n'
     '        "UltraChip\'s reference circuit asks for an Isat of at least 1.2 A, so the real peak may exceed the 0.5 A class "\n'
     '        "figure; added at integration from the independent check): closed when +3V3 stays inside its 3 percent budget "\n'
     '        "and U5\'s average at or under 500 mA; otherwise board C\'s "'),
    ('"6, 3), C FAIL (1, 5, 0), D FAIL (2, 6, 0) (v2/docs/records/w4c/readings/)." % (SCA, C_NET_SHA16))',
     '"6, 3), C FAIL (1, 5, 0), D FAIL (2, 6, 0) (v2/docs/records/w4c/readings/); board B\'s own failures on that walk are "\n'
     '                     "stream w4b\'s, whose rows and circuit landed ahead of this change in the same integration "\n'
     '                     "(EMCON.md section 4c)." % (SCA, C_NET_SHA16))'),
    ('        text = once(text, anchor, "\\n" + blocks + anchor[1:], "the open items\' header")',
     '        text = once(text, "\\n" + anchor, "\\n" + blocks + anchor, "the open items\' header")   # r8int6: keeps the blank line before the header'),
], "r8int6 re-derivation of stream w4c's apply_registry.py (beside it in this folder), written by derive_w4c_r8int6.py: "
   "W4C-F5's 24 mV figure is at nominal capacitance and its bring-up reading captures Q5's and L1's peak (the independent "
   "check), RF-002's row names board B's own failures as stream w4b's, and the three choices are inserted keeping the "
   "blank line before the open items' header (the stream's insertion removed it). The stream's text follows.")

derive("patch_docs.py", "patch_docs_r8int6.py", [
    ('"ten), C PASS (6 of 6), D INCONCLUSIVE (the SA868\'s own threshold).',
     '"ten on main\'s walk, which are stream w4b\'s: its rows and circuit landed ahead of this change in the same integration, "\n'
     '  "EMCON.md section 4c), C PASS (6 of 6), D INCONCLUSIVE (the SA868\'s own threshold).'),
    ('"FEA-002": "section 7 is byte-identical and none of the items this reading names as remaining moves (the RockBLOCK\'s "\n'
     '              "ENABLE, the SA868\'s threshold, L4 on U501 to U505, the back-feed, the plate\'s light guide, RF-002\'s model gap "\n'
     '              "on board B, every bench test); the changed places close W3T-F1 on the candidate only"}),',
     '"FEA-002": "section 7 is byte-identical and none of the items this reading names as remaining after stream w4b moves "\n'
     '              "(the Iridium 9704\'s response to its ENABLE, the SA868\'s threshold, L4 case (2) on U536, the back-feed, the "\n'
     '              "plate\'s light guide, the RF-002 walk\'s unread classes on board B, every bench test); the changed places close "\n'
     '              "W3T-F1 on the candidate only"}),'),
    (' ("v2/docs/HW-FW-CONTRACT.md", "| `fnd/w4c` |",\n'
     '  "| `fnd/r8bat` | FW-C09, FW-P01 | the pack readings\' 10 s fallback to the reduced mode; the round-8 charge window in the golden image |",\n'
     '  "| `fnd/r8bat` | FW-C09, FW-P01 | the pack readings\' 10 s fallback to the reduced mode; the round-8 charge window in the golden image |\\n"\n'
     '  "| `fnd/w4c` | FW-C07 | TX_INHIBIT_n',
     ' ("v2/docs/HW-FW-CONTRACT.md", "| `fnd/w4c` |",\n'
     '  "| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK\'s ENABLE is EMCON_HW AND U6\'s request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |",\n'
     '  "| `fnd/w4b` (r8int6) | FW-B13 | the RockBLOCK\'s ENABLE is EMCON_HW AND U6\'s request RB_SW_IEN in U536; the panel raises the request only with +5V_RB up and, after an EMCON, only once RB_STATUS reads low (`feasibility/EMCON.md` 4c) |\\n"\n'
     '  "| `fnd/w4c` | FW-C07; RAIL_SENSE, which no FW-C row covers yet (the contract writer\'s) | TX_INHIBIT_n'),
    ("\ndef has(text, marker):",
     "\n# r8int6: three ENGINEERING-QUESTIONS.md anchors moved on main after 62f26a44 (H2 appended to EQ-19's attempts and\n"
     "# EQ-25's next action, and rewrote EQ-25's index row); the stream's three edits are re-anchored on the current text,\n"
     "# the H2 sentences kept as the history they are, with the stream's own words and markers.\n"
     "def _r8int6_reanchor(edits):\n"
     "    out = []\n"
     "    for rel, mk, old, new in edits:\n"
     "        if mk == \"answered on board C by stream w4c\":\n"
     "            old = (\"| RF-002 FAIL on current evidence on boards A to D, a layout-entry reason on each; board D's SA868 \"\n"
     "                   \"keying; CON-010 FAIL (S-64) |\")\n"
     "            new = (\"| answered on board C by stream w4c (\" + SC + \", S-64 closed): R14 2.2 k and R50 10 k, the line PASS \"\n"
     "                   \"on the candidate; board D's SA868 keying back to its own UNDECIDED; RF-002 and CON-010 wait on the \"\n"
     "                   \"re-take |\")\n"
     "        elif mk == \"(a) drawn by stream w4c\":\n"
     "            old = (\"| **Recommended next action** | (a) at board C's next circuit round, regenerated with parity, then the \"\n"
     "                   \"RF-002 re-take on boards A to D. **H2:**\")\n"
     "            new = (\"| **Recommended next action** | (a) drawn by stream w4c (\" + SC + \", after H2); the RF-002 re-take on \"\n"
     "                   \"boards A to D at the integration that merges it, then bench E-01 and E-11 for the lines' real \"\n"
     "                   \"levels. **At H2:**\")\n"
     "        elif mk == \"**Board C (stream w4c, 27 September 2026):**\":\n"
     "            mid = new[new.index(\"(SC-56). \") + len(\"(SC-56). \"):new.index(\" **Status:**\")]\n"
     "            assert mid.startswith(mk), mid[:60]\n"
     "            old = \"which now need the same declarations. |\"\n"
     "            new = (\"which now need the same declarations. \" + mid + \" **Status after stream w4c:** C reads PASS of 6 \"\n"
     "                   \"in the stream's scratch; the consolidated re-take takes it in the tree. |\")\n"
     "        out.append((rel, mk, old, new))\n"
     "    return out\n\n\n"
     "EDITS = _r8int6_reanchor(EDITS)\n\n\ndef has(text, marker):"),
], "r8int6 re-derivation of stream w4c's patch_docs.py (beside it in this folder), written by derive_w4c_r8int6.py: EQ-25's "
   "attempts name board B's own failures as stream w4b's, FEA-002's re-read note lists what remains after stream w4b, and "
   "the HW-FW-CONTRACT row follows the fnd/w4b row and says no FW-C row covers RAIL_SENSE yet (the independent check); "
   "its three ENGINEERING-QUESTIONS.md edits are re-anchored on the text main holds after H2. The stream's text follows.")
