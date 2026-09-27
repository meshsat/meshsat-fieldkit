#!/usr/bin/env python3
"""r8int6 (the integrator of set 6 of the handover, 27 September 2026): writes apply_registry_r8int6.py and
edit_docs_r8int6.py beside stream w4ae's apply_registry.py and edit_docs.py, by asserted text replacement, so the filed
copies are whole scripts. The corrections are the independent check's (w4ae check 1, an AI check):
  - REQ-077's desk reading: the stop's own detection counted by hotstop_bounds.py (1.2 s) predates FW-C14's 3 s
    held-line rule; with it the detection is about 4.2 s, 0.22 K at 3.2 K/min, the worst H2 cell 59.29 C with 0.71 K
    left for the TBD terms, still inside +60 C and still ahead of OTD; the re-run is owed to its owner;
  - SC for D7 and D8: the MBRS140T3G alternative is quoted only as far as its LCSC record states (no onsemi sheet filed);
  - gen_sch_a.py's re-read note: the lines after R110's move down by 19, not 18;
  - FW-E10: the watchdog's period plus the longest edge-to-kick interval stays under 3 s (a period under 3 s alone lets a
    hang read as H2);
  - sources.txt: the distributor-served sheet is marked lower confidence (its PDF title names another product; IO reads
    1.0 A in the ratings and 2.0 A on FIG1).
Usage: derive_w4ae_r8int6.py <kit dir>"""
import os, sys

K = sys.argv[1]


def derive(src, dst, swaps, head):
    s = open(os.path.join(K, src), encoding="utf-8").read()
    for old, new in swaps:
        assert s.count(old) == 1, "%s: %d of %r" % (src, s.count(old), old[:90])
        s = s.replace(old, new)
    first = s.index('"""')
    s = s[:first + 3] + head + "\n\n" + s[first + 3:]
    compile(s, dst, "exec")
    open(os.path.join(K, dst), "w", encoding="utf-8").write(s)
    print("wrote", dst)


derive("apply_registry.py", "apply_registry_r8int6.py", [
    ('      "MBRS140T3G (SMB, 40 V, 1 A, VF 0.6 V at 1.0 A, a maximum forward curve from -55 to +125 C; LCSC C133091), the "\n'
     '      "documented alternative on the same land.")',
     '      "MBRS140T3G (LCSC C133091, whose record gives SMB, 40 V, 1 A, VF 600 mV at 1 A and Tj -65 to +125 C; no onsemi "\n'
     '      "sheet is filed, so its forward curve is owed before it is used; corrected at integration from the independent "\n'
     '      "check), the documented alternative on the same land.")'),
    ('"57.0 C in the gauge\'s reading under its OTD of 57.5 C, and the hottest cell at most 58.57 and 59.07 C (0.06 K "\n'
     '        "more with the stop\'s own detection) inside +60 C on the published terms of 2.07 K "',
     '"57.0 C in the gauge\'s reading under its OTD of 57.5 C, and the hottest cell at most 58.57 and 59.07 C (0.06 K "\n'
     '        "more with the stop\'s own detection as hotstop_bounds.py counts it, 1.2 s; with FW-C14\'s 3 s held-line rule "\n'
     '        "the detection is about 4.2 s, 0.22 K at 3.2 K/min, so the worst H2 cell is 59.29 C with 0.71 K left for the "\n'
     '        "TBD terms, still inside +60 C and still ahead of OTD, and a re-run of hotstop_bounds.py with the 3 s rule is "\n'
     '        "owed to its owner; corrected at integration from the independent check) inside +60 C on the published terms of 2.07 K "'),
    ('"section list, and nothing else; the lines after the expanders\' line move down by 18",',
     '"section list, and nothing else; the lines after R110\'s line move down by 19 (corrected at integration from the "\n'
     '        "independent check, the stream\'s note said 18)",'),
], "r8int6 re-derivation of stream w4ae's apply_registry.py (beside it in this folder), written by derive_w4ae_r8int6.py "
   "with the independent check's corrections: REQ-077's detection time under FW-C14's 3 s rule, the MBRS140T3G quoted as "
   "far as its LCSC record states, and the line shift in gen_sch_a.py's note. The stream's text follows.")

derive("edit_docs.py", "edit_docs_r8int6.py", [
    ('         "; keep the watchdog\'s period under FW-C14\'s 3 s, so a controller that hangs with GPIO19 high is reset, and its "',
     '         "; keep the watchdog\'s period plus the longest interval between an edge of the line and the next watchdog kick "\n'
     '         "under FW-C14\'s 3 s (for example a period of at most 1.5 s with the kick in the reading loop; the timeout runs "\n'
     '         "from the last kick while the held-line clock runs from the last edge), so a controller that hangs with GPIO19 high is reset, and its "'),
    ('            "ZHENGXINSEMICONDUCTORS; cited by gen_sch_e.py D7, D8 and the FAN1_SW and FAN2_SW nodes, %s)" % (MARK, SCB))',
     '            "ZHENGXINSEMICONDUCTORS; cited by gen_sch_e.py D7, D8 and the FAN1_SW and FAN2_SW nodes, %s; lower confidence: "\n'
     '            "a distributor-served copy whose PDF title names another product and which reads IO 1.0 A in its ratings and "\n'
     '            "2.0 A on FIG1)" % (MARK, SCB))'),
], "r8int6 re-derivation of stream w4ae's edit_docs.py (beside it in this folder), written by derive_w4ae_r8int6.py with "
   "the independent check's corrections: FW-E10's watchdog bound counts the edge-to-kick interval, and the sheet's "
   "sources line says its confidence is lower. The stream's text follows.")


_pd = open(os.path.join(K, "post_docs_registry.py"), encoding="utf-8").read()
_blk = _pd[_pd.index("# ---- CONOPS: which sections changed"):_pd.index("# ---- PANEL: two rows")]
derive("post_docs_registry.py", "post_docs_registry_r8int6.py", [
    (_blk,
     '# ---- CONOPS: r8int6: not edited. Since the definition restructure (a9f212c7) a circuit correction updates\n'
     '# DEFINITION-STATUS.md and the records it names (HOT-R1: REQ-077), never the baseline, so edit_docs_r8int6.py runs\n'
     '# without its conops group; this asserts CONOPS is HEAD\'s and leaves the needs pin alone.\n'
     'o, n = head(CO), now(CO)\n'
     'assert o == n, "CONOPS changed; since the definition restructure the integration does not edit it"\n'
     'n64 = hashlib.sha256(n.encode()).hexdigest()\n\n'),
], "r8int6 re-derivation of stream w4ae's post_docs_registry.py (beside it in this folder), written by "
   "derive_w4ae_r8int6.py: CONOPS is not edited at integration (the definition restructure at a9f212c7 keeps circuit "
   "corrections out of the baseline; HOT-R1's current state is REQ-077's), so the CONOPS block asserts the file is "
   "HEAD's and the needs pin is left as it is. The stream's text follows.")
