"""verify c5's second new contradiction: the handover pages still said the monitor's touch USB has no board end, while
HW-FW-CONTRACT.md's change record says every page that names the lead carries SC-HF-06. Each line keeps its audit
wording (status at e3aedb25) and gains what changed at the layer 5 merge. Run from the worktree root."""
def edit(p, pairs):
    t = open(p).read()
    for a, b in pairs:
        assert t.count(a) == 1, (p, t.count(a), a[:90]); assert a != b; t = t.replace(a, b)
    assert chr(0x2014) not in t; open(p, 'w').write(t)
SC = "SC-HF-06, board D's spare hub port `J_USB3`, `HW-FW-CONTRACT.md` section 8"
edit('v2/docs/handover/LAYER-STATUS.md', [
    ("third RF site and the monitor's touch USB port are missing decisions or circuits that change interfaces. Supervisor",
     "third RF site and the monitor's touch USB port are missing decisions or circuits that change interfaces (the touch port\nis decided since the layer 5 merge of 27 September 2026: %s). Supervisor" % SC),
    ("line 125 monitor touch USB with no board end |",
     "line 125 monitor touch USB with no board end (D8 `J_USB3` since the layer 5 merge, SC-HF-06) |"),
    ("the monitor (power, HDMI, touch USB), the B-to-A RF pigtails,",
     "the monitor (power, HDMI, touch USB; IF-MON and seventeen more contracts added at the layer 5 merge, `pcb_interfaces.yaml`), the B-to-A RF pigtails,"),
    ("the touch USB row has no board end;", "the touch USB row had no board end (D8 `J_USB3` since the layer 5 merge, SC-HF-06);"),
    ("| no; unrecorded anywhere today |",
     "| no; decided at the layer 5 merge as the session's choice (%s, no board B change), its costs owed on board D (HF-F06, open item S-61) |" % SC),
    ("   HDMI_SEL); record as a SESSION decision. Board B author; after r8b (`candidates/r8b.patch`) and before Q-B-ESC-2 fixes B's netlist.",
     "   HDMI_SEL); record as a SESSION decision. Board B author; after r8b (`candidates/r8b.patch`) and before Q-B-ESC-2 fixes B's netlist.\n"
     "   **Ruled at the layer 5 merge** (%s): no port reallocation on B, the HAL shares the touch to the display owner\n"
     "   (FW-B19); board D's current limit on `J_USB3` and its budget line remain (HF-F06, S-61), before D's layout entry." % SC),
    ("FAB-04, addresses, EMCON L2, L3, L7, SD-EMC-1 and 2, touch USB with no port, GND-002,",
     "FAB-04, addresses, EMCON L2, L3, L7, SD-EMC-1 and 2, touch USB with no port (on board D since the layer 5 merge, SC-HF-06), GND-002,"),
])
edit('v2/docs/handover/CONTINUATION-BRIEF.md', [
    ("GND-002, the monitor touch USB port); the tools merges",
     "GND-002, the monitor touch USB port, decided since as SC-HF-06 on board D's `J_USB3` with HF-F06 owed on D); the tools merges"),
])
print("edit_c5_handover: done")
