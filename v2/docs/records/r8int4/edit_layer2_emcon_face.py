"""hc1's held layer2-emcon-face.patch (Review A layer 1, finding B1; I5 waits on it), re-derived on main 38dcd764,
where board B's round 8 (b76c18cb) already closed the 5G row at desk. Each edit asserts its old text and that the new
text differs; run from the worktree root."""
import sys
def sub(t, a, b, n=1):
    assert t.count(a) == n, (t.count(a), a[:90]); assert a != b
    return t.replace(a, b)
p = 'v2/docs/CONOPS.md'; t = open(p).read(); t0 = t
# M4, the D-05 paragraph (section 3)
t = sub(t, """session work under the ruling (S-01): the 5G module, whose only path was its disable pin, a firmware-mediated
airplane mode, and the items every row of the EMCON line shares (section 4b). **Since board B's round 8 (27 September
2026) the 5G module's supply is removed by hardware at once and board B's shared items are drawn (section 4b)**; no row
has been shown on a bench.""",
"""session work under the ruling (S-01), read transmitter by transmitter in `feasibility/EMCON.md` section 0a: the 5G
module, whose only path was its disable pin, a firmware-mediated airplane mode, and the items every row of the EMCON
line shares (section 4b). **Since board B's round 8 (27 September 2026) the 5G module's supply is removed by hardware
at once and board B's shared items are drawn (section 4b)**, so the radio's own chain is closed at desk for 15 of the
17 transmitters and open for two: the SA868 (its PTT pin's receive threshold is unpublished) and the RockBLOCK 9704
(once its supply is cut it runs on its own supercapacitors with its ENABLE held by firmware). No row is closed end to
end, from the toggle to silence at the antenna port, so NEED-08 is not met for any transmitter until the design closes
it, and no row has been shown on a bench.""")
# section 4, the EMCON row
t = sub(t, "the compute modules' own WiFi and Bluetooth disabled through open drains; the 5G module in airplane mode through its disable pin; the PA rail and keying off; software holds every send, an SOS included | HW for the gated rails, the module radio disables and the VHF keying; the 5G row rests on the module's firmware until its supply removal is drawn; SW hold on top |",
"the compute modules' own WiFi and Bluetooth disabled through open drains; the 5G module's supply removed by hardware with its disable pins pulled low at the same moment (since board B's round 8, section 4b); the PA rail and keying off; software holds every send, an SOS included | HW for the gated rails, the module radio disables and the VHF keying, and the RockBLOCK keeps running on its own stored energy with its ENABLE held by firmware until that ENABLE is forced low in hardware (`feasibility/EMCON.md` section 4.4); SW hold on top |")
t = sub(t, "| session work owed under D-05 (S-01): the 5G module's staged supply removal (SD-EMC-1), the line's shared items (`feasibility/EMCON.md` section 7) and the back-feed paths (SD-EMC-2); a hardware EMCON lamp on board C (SD-EMC-6); twelve bench tests,",
"| session work owed under D-05 (S-01): the RockBLOCK's ENABLE forced low by the EMCON hardware with its stored energy bounded (EMCON.md section 4.4), the SA868's PTT threshold (bench E-01), the line's shared items left open after board B's round 8 (the gate supplies of `U501` to `U505`, `feasibility/EMCON.md` sections 4b and 7) and the back-feed paths into the RockBLOCK, the E22 and the E72 (SD-EMC-2); the hardware EMCON lamp's plate light guide (SD-EMC-6; the lamp is drawn on board C since its round 8); the 5G module's staged supply removal (SD-EMC-1) is drawn since board B's round 8 (SD-EMC-1r8); twelve bench tests,")
# section 4, the Service row: case choice C1
t = sub(t, "| Service | face plate off (ten M3), rod stack", "| Service | face plate off (ten 6-32 screws, case choice C1 of `CASE-MARGINS.md` section 4), rod stack")
# section 4b, the RockBLOCK row
t = sub(t, "| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired (`U503`) | power | lost |",
"| RockBLOCK 9704 | the enable of the eFuse that feeds its external supply pin, the only supply wired (`U503`) | power at that pin; the module's own two 10 F supercapacitors (about 16 J) keep it running after the gate opens, with its ENABLE driven only by the firmware expander `U6`, so its local chain is OPEN until ENABLE is forced low in hardware (`feasibility/EMCON.md` section 4.4) | lost once its own stored energy is spent (about 4.5 minutes idle, INFERRED, EMCON.md section 4.4) |")
# the D-05 paragraph after 4b's table
t = sub(t, """transmit side only; GNSS, DCF77 and the lightning sensor continue. Since `458b2873` the table met that meaning at
desk in every row but one, the 5G module, whose only EMCON path was its disable pin; since board B's round 8 (27
September 2026) its supply is removed by hardware at once with a bounded time to RF off (`feasibility/EMCON.md`
section 4b, SD-EMC-1r8), so the 5G row meets it at desk as well; the RockBLOCK's own supercapacitors, which keep the
module running after its supply gate opens, stay EMCON.md section 4.4's open item. What every row""",
"""transmit side only; GNSS, DCF77 and the lightning sensor continue. Read transmitter by transmitter
(`feasibility/EMCON.md` section 0a, sixth revision), the radio's own chain meets that meaning at desk for 15 of the 17
transmitters. The 5G module's is among them since board B's round 8 (27 September 2026): its only EMCON path had been
its disable pin, and its supply is now removed by hardware at once with a bounded time to RF off (EMCON.md section 4b,
SD-EMC-1r8). Two stay open: the SA868, whose PTT pin's receive threshold its maker does not publish (bench E-01), and
the RockBLOCK 9704, whose own supercapacitors keep the module running after its supply gate opens, with its ENABLE held
by firmware (EMCON.md section 4.4). What every row""")
t = sub(t, """RockBLOCK, the E22 and the E72 (EMCON.md section 4b); and no row has been shown on a bench (EMCON.md section 6, twelve
tests, none of which can use the kit's own SDR, whose supply EMCON removes).""",
"""RockBLOCK, the E22 and the E72 (EMCON.md section 4b); end to end, from the toggle to silence at the antenna port within
the latency of REQ-071, no row is closed; and no row has been shown on a bench (EMCON.md section 6, twelve tests, none
of which can use the kit's own SDR, whose supply EMCON removes).""")
t = sub(t, """a converter enable for the WiFi card). The WiFi cards' converter enables are drawn since `458b2873`; the 5G supply
switch is SD-EMC-1's and is owed.""",
"""a converter enable for the WiFi card). The WiFi cards' converter enables are drawn since `458b2873`; the 5G supply
switch, SD-EMC-1's, is drawn since board B's round 8 (SD-EMC-1r8, EMCON.md section 4b).""")
assert t != t0; open(p, 'w').write(t)
# PANEL.md line 5 (the patch's first PANEL hunk; its second is superseded by board C's round 8 text on main)
p = 'v2/docs/PANEL.md'; t = open(p).read(); t0 = t
t = sub(t, "The lines that act without any software are MAIN PWR, EMCON and the TX lamp (section 6). The ZEROIZE",
"The lines that act without any software are MAIN PWR and EMCON (section 6). The TX lamp's sink follows D8's real KEY line in hardware, but its feed, `LED_RAIL`, exists only while the controller drives `PANEL_PWM` (section 3, GPIO 8), so as drawn the lamp needs the controller; moving its feed to `LED_RAIL_SW` is the board C author's open choice (`feasibility/EMCON.md` section 8). The ZEROIZE")
assert t != t0; open(p, 'w').write(t)
print("edit_layer2_emcon_face: CONOPS 8 edits, PANEL 1 edit")
