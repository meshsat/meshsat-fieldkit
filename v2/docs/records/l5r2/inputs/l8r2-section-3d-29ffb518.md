<!-- COPIED INPUT (MESHSAT-1357, Layer 5 round 3, record l5r2, 3 October 2026). Source: branch fnd/l8r2 at commit 29ffb518, file v2/docs/records/l8r2/L8R2-KNOWN-DEFECTS.md, whose sha256 at that commit is adefb01c376d298d98791b68bc5cd5e044d75d167c8ab00c98fd0915ae75eb4f. Copied: section 3d (board C's PI button), from its heading to the line before section 4's, verbatim between the two markers below; the body's own sha256 is 37066a69ca7183f3f7e2272de1779d4d83647137a24c6849953eb2bd96a1322c (l5r3_panel.py recomputes it and refuses a copy that differs). Copied because the commit is not in this branch's history; no git command reads it. -->
<!-- BODY BEGIN -->
## 3d. Item 4: board C's PI button reaches no controller pin (the panel firmware's F-01)

**The defect as found** (fnd/fw-panel at `42c27369`, `v2/firmware/panel/README.md` finding F-01, copied in
`inputs/fw-panel-F01-42c27369.md`). SW_PI's contacts (PIJ2_A, PIJ2_B) pass FB3 and FB4 to J_PIJ2's two lands (PIJ2_A2, PIJ2_B2) and
U11's clamps only: no RP2040 GPIO, no expander input, neither line on GND, no other board with a mating lead. All 30 GPIOs are used;
the expanders' port 1 spares are free.

**The decision: route it to the controller (SESSION), on the evidence.**
- PANEL.md section 5: "The PI button: short press = `PI_SHDN_REQ` (clean shutdown of every module), hold 8 s = `PI_KILL`. The MAIN PWR
  button is hardware to A22's power controller and the controller only sees its effect". HW-FW-CONTRACT FW-C03 says the same.
  Only the controller can tell a short press from an 8 s hold.
- ASSEMBLY.md's leads table (line 127): "PI button | SW_PI's contacts | C7 `J_PIJ2` lands (the panel controller reads it; nothing
  leaves the backer)". **ASSEMBLY.md is right.**
- The generator's own note (line 333: "PIJ2_A2 is the same part's open-drain INT output, held at +3V3 by R3 on board A") is the stale
  statement. No board carries that lead. Were it built, a press would pull PI_SHDN_REQ, which the controller reads as a MAIN tap
  (PANEL.md section 3, GPIO 18, and FW-A10: "it reads the pin as an input to see MAIN taps"), so the 8 s hold could not be told apart
  from MAIN. The LTC2954 path stays what PANEL.md says: MAIN alone, hardware to A22.
- The J_PIJ2 lands are kept (the switch's lead lands); only the stale note is corrected.

**The circuit drawn (`apply_gen_sch_c_pibtn.py`).**
- **The input:** PIJ2_A2 goes to U1 (PCA9555, 0x22) P1.3, pin 16, until now SPARE1. That is the inputs port, beside LIGHT_DAY_n and
  LIGHT_NIGHT_n. The bit is named **PI_BTN_n** (low = pressed).
- **The pull-up:** R57, 10 k (C25804) to +3V3.
- **The return:** PIJ2_B2 is tied to this board's GND (FB4 pin 2, C27, J_PIJ2 pin 2, U11's second channel), so a press pulls
  PIJ2_A2 low through FB3.
- **The debounce:** C27, the 100 nF already across the pair, now runs from PIJ2_A2 to GND. With R57 it gives **tau 1.00 ms**.
  - A release reaches VIH (2.31 V, 0.7 VCC, TI SCPS131J 6.3) after 1.20 ms.
  - A press pulls under VIL (0.99 V) through the contact, which carries 0.33 mA.
  - The board's other inputs use 10 k with 10 nF; the longer tau here suits a lead that passes the antenna feeds.
- **The interrupt:** the expander raises EXP_INT on the change (SCPS131J 8.4.1), the controller's GPIO24, which FW-C14 already
  services.
- **Kept and moved:** SPARE1's test point moves to PIJ2_A2, so the button keeps test access, and U11's clamp stays on the A line.

**The proof** (`l8r2_drafts.out` section 7b). Layer 6's `apply_gen_sch_c_lcsc.py`, the only other board C draft (fnd/l6r2 at
`7633ae0a`, copied in `inputs/` with the helper `l6r2_apply.py` it imports, run in a scratch git repository because the helper asks
git for its top level), and this draft give **the same generator in either order**. Layer 6's draft anchors on the layout's import
line and keys codes by designator and value, and touches none of these lines. Designators: this draft adds **R57**, Layer 6's adds
none; no literal designator is drawn twice.

**The acceptance.** The regenerated board C netlist shows U1 pin 16 on PIJ2_A2, R57 between PIJ2_A2 and +3V3, and C27, FB4 pin 2 and
J_PIJ2 pin 2 on GND (`check_l8r2_netlist.py` PIBTN: NOT DRAWN today, U1.16 on SPARE1). Bench (V-C03): a short press raises
PI_SHDN_REQ for at least 200 ms and the 8 s hold raises PI_KILL; U1 P1.3 reads 0 with the button held and 1 released, through EXP_INT.

**Texts for their owners (not edits).**
- **PANEL.md section 4, U1's port 1 row 3:** "PI_BTN_n: the PI button, low = pressed (PIJ2_A2; R57 10 k to +3V3, C27 100 nF to GND,
  tau 1.0 ms); raises EXP_INT on a change". The SPARE1 test point becomes the button's.
- **PANEL.md section 1, the switches row:** "`SW_PI` (16 mm, lead pads `PIJ2_A/B`, read by U1 P1.3)".
- **PANEL.md section 5:** add after the PI button's sentence "(read on U1 P1.3, PI_BTN_n, at every EXP_INT and the once-a-second
  poll)".
- **The firmware's hal.h:** the expander bit `U1 P1.3 = PI_BTN_n`, active low; `HAL_PI_BUTTON_WIRED` becomes 1 once the draft is
  released and board C regenerated.
- **The firmware's check:** "the PI button reaches no controller pin" is F-01's evidence and fails, as designed, on the regenerated
  netlist; replace it with the bit check against U1 pin 16.
- **ASSEMBLY.md line 127:** "(the panel controller reads it on U1 P1.3; nothing leaves the backer)". The row is already right in
  substance.
- **HW-FW-CONTRACT FW-C03:** "`C:J_PIJ2`" becomes "`C:U1` P1.3 (PI_BTN_n)".

<!-- BODY END -->
