# routeflow phases, the notes of the per-phase profiles (15 September 2026)

Until 15 September 2026 the supervisor carried one profile per PHASE (`routeflow/a22.json` to `a35.json`, 34 files), each differing
from the last in the phase string and a note (red team round four H1). There is one profile per LETTER now, with `<PHASE>`
where the phase was typed, resolved from `--phase`, `ROUTEFLOW_PHASE` or `boards/<letter>.json`. The notes those files carried
are kept here, oldest first per board, because they are the record of what each phase changed.

## a22 (A22, pcb-a-power)

route: attempts [120], threads 1, timeout 7200 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A22 (7 Sep 2026, appendix 32.55, 32.56, 32.61): six layers since run 10 (JLC06161H-3313 as B16): In1 and In4 solid ground planes handed to Freerouting as power layers with GND as the plane net, In2 carries the VBAT plane and GND islands and stays routable, In3 routable; single thread on 1.9.0 (the blessed production jar); the finish is finish_a22.sh (stub router on F, In2, In3, B; cleanup, quality pass, pair report on the three USB pairs, the A gate, finish_board into the A22 deliverable). History: eight four-layer 1.9.0 rounds left 4 to 11 opens in the packed converter zones (run 8 also 36 hard: overlapping tracks of two nets at three spots), run 9 on 2.4.1 sat at 153 unrouted after four passes and was stopped. Run 11 (250 passes) converged at pass about 150 ('19 changes in 60 passes') and would have hit the 2 h limit before writing its session: 120 passes since run 12.

## a23 (A24, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

## a25 (A25, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A25, 13 September 2026 (MESHSAT-862): A24's copper plus power copper for VBUS20 and +12V_HF, which had none, a 7.0 mm PA band fed over a front, and a track keep-out on the VBAT In2 plane's neck. The density measure that asked for all four was itself corrected the same day (appendix 32.164): A24 as cut reads 7 of 12 rails MET rather than 2.

## a26 (A26, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A26, 13 September 2026 (MESHSAT-862): A25's copper with the four places the density pass measured on the routed board. The PA band starts at its shunt's own output pad instead of 15 mm east of the head it feeds; VIN_RAW's west band covers the head island, with a second via row at the north end where the neck was; VBUS20's second layer leaves B.Cu, where it had cut VBAT's 10 A trunk in two and left 3.29 A to a 0.500 mm In3 router track; and the HF east run steps north of J_AB2's pin field instead of threading it.

## a27 (A27, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A27, 13 September 2026 (MESHSAT-862): A26's copper with the VBAT comb's bay. A26 measured its own B.Cu comb in TWO pieces, cut by the charger's east escape column (seven 0.45 mm vias at x 57.5 to 57.8 between y 95.6 and 100.4), which is why the pack's 10 A was in the In2 plane and in a 0.500 mm In3 router track. The comb takes a bay east of that column, where B.Cu is empty for 12 by 12 mm.

## a28 (A28, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A28, 14 September 2026 (MESHSAT-862): A27's routed copper with three things added and nothing moved. The length matcher, once it was allowed to see the pair's own locked copper, put one bump on /USB_D8_N and one on /USB_WALL_P and the three pairs read 0.01, 0.13 and 0.00 mm apart. /POE_SW2 closed as a short run with a via down to In2, and /VBUS20 as a 1.635 mm B.Cu run between the two islands' own vias, which is the pair that was 0.800 mm away on F.Cu and walled in by U3's pad 2. 0 hard, 0 unrouted.

## a29 (A29, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A29, 14 September 2026 (MESHSAT-862): A28's copper with four layer transitions given the barrel they never had. Fifteen vias hand VBAT's B.Cu trunk to its In2 plane at the source instead of eighty millimetres north; six more tie VBUS20's F.Cu island to its In3 polygon between the output capacitors, and the island gets the track keep-out every band on this board has carried since 32.39; VIN_RAW's two head rows go from three vias to six; and the PA rail's right-angled turn gets a 2.5 by 4 mm chamfer. Measured on A28, which reads 0 hard, 0 unrouted, every pair inside 1 mm and 8 of 12 rails MET.

## a30 (A30, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A30, 14 September 2026 (MESHSAT-862): A29's copper routed with the via-cost remedy from the first round instead of after a refused one. A29's copper is right and its route is not. The four rails it was cut for all improved on their own numbers, measured on A29's routed board: VBAT's worst conductor 2.96 to 1.33 and its pour 1.36 to 1.04, VBUS20's conductor 3.23 to 0.99, VIN_RAW's pour 2.06 to 1.61. What A29 did not do is route: the session came back 10 hard of one kind and 10 unrouted, the finish closed four, and five of the rest are further than twelve millimetres, which is the router's work and not a closure's. via_costs 100 is the one remedy this project has measured as a different solution rather than a longer search.

## a31 (A31, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A31, 14 September 2026 (MESHSAT-862): A30's copper with a track keep-out on each VBAT slot island's via column. A30 routed 0 hard and 8 unrouted with via_costs 100 and its finish closed five (the stub router seven of eight DRC pairs, the closure ladder three more), leaving two GND pads and a VBUS20 gap; its round two at 23 passes came back worse (13) and the supervisor of that run finished the worse board, which is fixed in this tree. The SD island had read 10.7 of 22 mm2 with 65 mm of other nets' track through it, the one gate failure in 835; the column keep-out is the answer every band has carried since 32.39.

## a32 (A32, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory.

- A32, 15 September 2026 (MESHSAT-862): A30's copper with the three gaps 32.191 measured closed at the source. The In2 VBAT plane reaches F1's pad; VBUS20's In3 polygon carries a track keep-out; the In2 under VIN_RAW's head is closed to tracks. A30 closed to 0 hard and 0 unrouted by hand and its rails read VBAT 2.25, VBUS20 8.61, VIN_RAW 3.57 on router tracks bridging exactly those three gaps.

## a33 (A33, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory. | A33 (15 Sep 2026): the four rails A32 missed after rail_prune, each at a named neck (32.193): the VBUS20 leg and column widened with four vias a shunt and a foot at the corner, the F.Cu leg under a track keep-out; the In2 VBAT plane gets tongues under the PA head and the converter row; the VIN_RAW head grows north; the PA run gets a foot at J_PA's pin.

- A33, 15 September 2026 (MESHSAT-862): A32 closed to 0/0 by hand and four rails still missed on pour cells at named necks after rail_prune took the router's parallel copper off (32.193); A33 is the copper at those four places.

## a34 (A34, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory. | A33 (15 Sep 2026): the four rails A32 missed after rail_prune, each at a named neck (32.193): the VBUS20 leg and column widened with four vias a shunt and a foot at the corner, the F.Cu leg under a track keep-out; the In2 VBAT plane gets tongues under the PA head and the converter row; the VIN_RAW head grows north; the PA run gets a foot at J_PA's pin.

- A34, 15 September 2026 (MESHSAT-862): A33 measured the four rails again after rail_prune; vias in Q2's drain tab, a via row across the VBUS20 leg, the PA run doubled south of J_AB2's pins, the In2 VBAT plane kept off U2's escape fan.

## a35 (A35, pcb-a-power)

route: attempts [18], threads 1, timeout 18000 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- A23 (8 Sep 2026, MESHSAT-862 rule 3, appendix 32.69): the A22 profile on the pcb-a-power-a23 copy with the power copper of gen_pcb_a3.py; finish_a23.sh is finish_a22.sh on that directory. | A33 (15 Sep 2026): the four rails A32 missed after rail_prune, each at a named neck (32.193): the VBUS20 leg and column widened with four vias a shunt and a foot at the corner, the F.Cu leg under a track keep-out; the In2 VBAT plane gets tongues under the PA head and the converter row; the VIN_RAW head grows north; the PA run gets a foot at J_PA's pin.

- A35, 15 September 2026 (MESHSAT-862): A34 routed 0 hard, 4 open (three GND pads a via short of their plane, one 0.5 mm VBUS20 gap) and its gate refused two pour items: the PA rail head island filled 51 of 102 mm2 with router tracks across it (a track keep-out on the island now), and a locked VBAT stitch via the In2 fill had abandoned, which stitch_prune could only remove after rail_prune had taken the router track ending on it (the finish prunes twice now). Its rails read 9 of 12 MET before the rail prune, the three misses all router conductors the prune removes.

## b16 (B16, pcb-b-compute)

route: attempts [100], threads 1, timeout 14400 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- B16 (7 Sep 2026, appendix 32.52 and 32.58): 330 x 200, six layers as B15 (In1 solid ground, In4 the four 5 V planes, both handed to Freerouting as power layers, GND as a plane net); single thread on 1.9.0; three CM5 slots with a PCIe switch and a USB 3 hub each, the Ethernet and HDMI switches, the radios. One automatic round: the via_costs remedy hurt A22 (7 Sep 01:33, GND pads left open), the session audits the leftovers.

## b17 (B18, pcb-b-compute)

route: attempts [8], threads 1, timeout 14400 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- B17 (8 Sep 2026, MESHSAT-862, appendix 32.70): the B16 profile on the pcb-b-compute-b17 copy; the HDMI switches at 16 mm pitch, the pair pre-router in the chain.

## b19 (B19, pcb-b-compute)

route: attempts [12], threads 1, timeout 21600 s, power layers ['In1.Cu', 'In4.Cu'], plane nets ['GND'], rules None

- B19 (9 September 2026, MESHSAT-862, appendix 32.86): the first B phase with the I/O high-availability layer. The board builds and check_pcb_b.py prints ALL PASS on it; this profile measures how the new DSN routes. B18 is superseded and no release is cut against it.

## c7 (C7, pcb-c-display)

route: attempts [100], threads 1, timeout 5400 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C7 (7 Sep 2026): the backer ring of the A22 generation (RP2040 panel controller, PDi e-paper driver, Xenarc face, headset jacks); four layers, In1 the ground plane as a power layer, one attempt on 1.9.0 single thread as the other boards of the campaign.

## c8 (C10, pcb-c-display)

route: attempts [30], threads 1, timeout 10800 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C8 (8 Sep 2026, MESHSAT-862, appendix 32.70): the C7 profile on the v2/ecad/pcb-c-display-c8 copy.

## c11 (C11, pcb-c-display)

route: attempts [30], threads 1, timeout 10800 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C8 (8 Sep 2026, MESHSAT-862, appendix 32.70): the C7 profile on the v2/ecad/pcb-c-display-c8 copy.

- C11, 13 September 2026 (MESHSAT-862): C10's copper with the USB net class actually REGISTERED. It was built and configured in gen_pcb_c3.py and the call that registers it sat inside a comment, so every USB net on C, D and E had been taking the Default 0.25 mm instead of the class's 0.30 (appendix 32.167).

## c12 (C12, pcb-c-display)

route: attempts [45], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C8 (8 Sep 2026, MESHSAT-862, appendix 32.70): the C7 profile on the v2/ecad/pcb-c-display-c8 copy.

- C12, 14 September 2026 (MESHSAT-862): the same copper as C11 with more router passes. C11 routed 0 hard and 3 unrouted, its finish closed two of them, and the one left is `/EPD_SDA`, 249 mm from J_EPD pin 14 in the top strip to U3 pad 5 in the bottom-right corner, both ends already escaped to vias. Drawn and read: the panel is a U and that connection has one corridor, the top strip east then the right strip south, and the corridor is a dense parallel bundle. Neither the stub router at scale 25 on a 0.2 mm grid nor a continuation of eight passes closed it, so what is left is the router's own rip-up, which is what more passes buy. 45 passes at C's measured eight minutes a pass is six hours, inside the three-hour-per-attempt cap only because a session is written per pass.

## c13 (C13, pcb-c-display)

route: attempts [45], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- 14 September 2026: C12 ended 0 hard with two opens, /PWM1 and /HB2, and both pads sit in open ground (nothing within 2.12 mm of TP29, nothing but its partner's tracks within 1.65 mm of R44). A board-wide stub search at a 0.1 mm grid on all three routing layers, at the panel's own class clearance of 0.127 rather than the tool's old 0.16 literal, finds no path for either: the lanes are not there and no closure will make them. The router is deterministic, so more passes repeat the result and only a different rules file is a different solution. via_costs 100 was round two's remedy and took 12 opens to 4; the rip-up cost is the second lever fr_rules writes and has never been moved on this board. 10 against the default 100 makes the router far more willing to tear up and re-lay, which is what a board whose strips are full needs.

## c14 (C14, pcb-c-display)

route: attempts [30], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- C14, 14 September 2026 (MESHSAT-862): C11's recipe on today's copper, which is the best this board has ever routed. Thirty passes with the via-cost remedy applied from the first round instead of the second, because on C11 that remedy is what took 7 unrouted to 3. Forty-five passes were tried twice and did worse both times, once at the default rip-up cost (4 unrouted) and once at 10 (59): this board is at a congestion cliff where more search wanders.

## c15 (C15, pcb-c-display)

route: attempts [30], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- C15, 14 September 2026 (MESHSAT-862): C14's recipe with `/EPD_SDA` PRE-LAID. Four routes of this copper have each left one or two long panel nets open and never the same ones: the strips are the only corridors on a ring-shaped board and whoever reaches them first takes them. The lane is searched on the PLACED board, where the strips are empty, and locked, so the router works around it instead of competing for it. If the remaining opens on this route are the test-point branches rather than the long hauls, the next change is where those test points sit, not how the board is routed.

## c16 (C16, pcb-c-display)

route: attempts [30], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- C16, 14 September 2026 (MESHSAT-862): the whole six-wire e-paper bus pre-laid, not one line of it. C15 pre-laid /EPD_SDA alone and the round-one route left /EPD_DC, /EPD_RST and /EPD_SCL open, the lines beside it in the same corridor, which had never been open before: a lane taken by hand moves the shortage to the next net. A bus is pre-laid as a bus.

## c17 (C17, pcb-c-display)

route: attempts [30], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- C17, 15 September 2026 (MESHSAT-862): C14's recipe with the forty test points placed beside the nets they tap, two columns on the underside of the right strip beside the RP2040, instead of a row in the bottom strip fifty millimetres from everything they probe. Every C route since C12 lost one or two of those branches. The e-paper panel-voltage points go to the boost cluster in the top strip.

## c18 (C18, pcb-c-display)

route: attempts [30], threads 1, timeout 21600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- C13, 14 September 2026 (MESHSAT-862): C12's copper routed with the rip-up cost at 10 instead of the default 100, in an isolated tree so the tools can move under the rest of the work. Everything else is C12's.

- C18, 15 September 2026 (MESHSAT-862, appendix 32.198): the same routed board as C17 re-finished under the two return-current gates of the owner ruling of 20:15 CEST (a plane under every signal net, a ground via beside every signal via, placed by the finish). 

## d8 (D8, pcb-d-aprs)

route: attempts [100], threads 1, timeout 3600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- D8 (7 Sep 2026): the APRS mezzanine of the A22 generation (SA868 exciter, T/R relay, LPF, USB audio and control set; the 30 W PA on the face plate, 32.56); four layers, In1 the ground plane as a power layer, one attempt on 1.9.0 single thread.

## d9 (D10, pcb-d-aprs)

route: attempts [100], threads 1, timeout 3600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- D9 (8 Sep 2026, MESHSAT-862 rules 1 and 2, appendix 32.70): the D8 profile on the pcb-d-aprs-d9 copy with the USB cluster on the top layer and the pair pre-router in the chain; the USB and RF classes on F.Cu and In2.Cu.

## d11 (D11, pcb-d-aprs)

route: attempts [100], threads 1, timeout 3600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- D9 (8 Sep 2026, MESHSAT-862 rules 1 and 2, appendix 32.70): the D8 profile on the pcb-d-aprs-d9 copy with the USB cluster on the top layer and the pair pre-router in the chain; the USB and RF classes on F.Cu and In2.Cu.

- D11, 13 September 2026 (MESHSAT-862): OWNER RULING 15 implemented. The PWR class goes back to 0.5 mm and +5V_D8's trunk and west branch are locked In2 copper at 1.7 and 1.5 mm, sized to the current the rail's declared loads actually put in them (1.0 A and 0.75, not the rail's total in one conductor). Measured in an isolated tree first: 0 hard, 0 unrouted after the finish, the board gate ALL PASS, the rail MET, 4 of 4 pairs.

## d12 (D12, pcb-d-aprs)

route: attempts [100], threads 1, timeout 3600 s, power layers ['In1.Cu'], plane nets ['GND'], rules None

- D9 (8 Sep 2026, MESHSAT-862 rules 1 and 2, appendix 32.70): the D8 profile on the pcb-d-aprs-d9 copy with the USB cluster on the top layer and the pair pre-router in the chain; the USB and RF classes on F.Cu and In2.Cu.

- D12, 15 September 2026 (MESHSAT-862, appendix 32.198): the same routed board as D11 re-finished under the two return-current gates of the owner ruling of 20:15 CEST (a plane under every signal net, a ground via beside every signal via, placed by the finish). 

## e6 (E7, pcb-e1-dock)

route: attempts [250], threads 1, timeout 10800 s, power layers ['In1.Cu', 'In2.Cu'], plane nets ['GND', 'CELL_F', 'VIN_RAW', 'PV_P', 'TRK_OUT'], rules None

- E6 (7 Sep 2026): the dock strip of the A22 generation with the sensor controller folded in (32.57); four layers, In1 the ground plane and In2 the power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT) as power layers, one attempt on 1.9.0 single thread.

## e8 (E8, pcb-e1-dock)

route: attempts [250], threads 1, timeout 10800 s, power layers ['In1.Cu', 'In2.Cu'], plane nets ['GND', 'CELL_F', 'VIN_RAW', 'PV_P', 'TRK_OUT'], rules None

- E6 (7 Sep 2026): the dock strip of the A22 generation with the sensor controller folded in (32.57); four layers, In1 the ground plane and In2 the power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT) as power layers, one attempt on 1.9.0 single thread.

- E8, 13 September 2026 (MESHSAT-862): VIN_RAW's copper. The In2 pour reaches the block lands, L2's source pad carries ten 0.9/0.5 barrels where it had one 0.45, each J_BLK land has two, and a small F.Cu island sits over the source pad because the rail had no copper at all on the layer its own pad is on and 2.23 A of 8 was on a 0.400 mm escape stub. Measured in an isolated tree: both rails MET, conductor 0.60 and 0.51, pours 0.69 and 1.00.

## e9 (E9, pcb-e1-dock)

route: attempts [250], threads 1, timeout 10800 s, power layers ['In1.Cu', 'In2.Cu'], plane nets ['GND', 'CELL_F', 'VIN_RAW', 'PV_P', 'TRK_OUT'], rules None

- E6 (7 Sep 2026): the dock strip of the A22 generation with the sensor controller folded in (32.57); four layers, In1 the ground plane and In2 the power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT) as power layers, one attempt on 1.9.0 single thread.

- E9, 13 September 2026 (MESHSAT-862): E8's copper with the VIN_RAW In2 pour taken north to y -71. E8 routed 0 hard and its finish closed all but one connection; its VIN_RAW pour read 1.14 of the cell bar in the strip its own ten via heads stand in, and In2 is empty for 3 mm north of them. CELL_F read MISSED on a stale fill and MET on the same board refilled, which is fixed in finish.sh rather than here.

## e10 (E10, pcb-e1-dock)

route: attempts [250], threads 1, timeout 10800 s, power layers ['In1.Cu', 'In2.Cu'], plane nets ['GND', 'CELL_F', 'VIN_RAW', 'PV_P', 'TRK_OUT'], rules None

- E6 (7 Sep 2026): the dock strip of the A22 generation with the sensor controller folded in (32.57); four layers, In1 the ground plane and In2 the power pours (CELL_F, VIN_RAW, PV_P, TRK_OUT) as power layers, one attempt on 1.9.0 single thread.

- E10, 15 September 2026 (MESHSAT-862, appendix 32.198): the same routed board as E9 re-finished under the two return-current gates of the owner ruling of 20:15 CEST (a plane under every signal net, a ground via beside every signal via, placed by the finish). 

## p1 (P1, pcb-p-pack)

route: attempts [60], threads 1, timeout 1800 s, power layers [], plane nets [], rules None

- P1 (7 Sep 2026, appendix 32.62): the pack BMS board (BQ4050 gauge and protection for the built 4S pack), two layers, 2 oz; the power path in locked bands, no plane in the DSN (the ground pour on B.Cu fills around the route), one attempt on 1.9.0 single thread.

## p2 (P3, pcb-p-pack)

route: attempts [60], threads 1, timeout 1800 s, power layers [], plane nets [], rules None

- P2 (8 Sep 2026, MESHSAT-862, appendix 32.70): the P1 profile on the v2/ecad/pcb-p-pack-p2 copy.

## p4 (P4, pcb-p-pack)

route: attempts [60], threads 1, timeout 1800 s, power layers [], plane nets [], rules None

- P2 (8 Sep 2026, MESHSAT-862, appendix 32.70): the P1 profile on the v2/ecad/pcb-p-pack-p2 copy.

- P4, 13 September 2026 (MESHSAT-862): the pack current enters its bands through wider copper and far more barrels. The three 0.6 mm source runs are 1.2 mm, each FET's three source tracks carry two 0.9/0.5 vias at the one place the current must change layer, and the bands' own stitch is three across at 1.0 mm. Measured in an isolated tree: 0 hard, 0 unrouted, the gate ALL PASS and 3 of 3 rails MET.

## p5 (P5, pcb-p-pack)

route: attempts [60], threads 1, timeout 1800 s, power layers ['B.Cu'], plane nets ['GND'], rules None

- P2 (8 Sep 2026, MESHSAT-862, appendix 32.70): the P1 profile on the v2/ecad/pcb-p-pack-p2 copy.

- P5, 15 September 2026 (MESHSAT-862, appendix 32.198): owner scope answer 1 of the return-current ruling, P keeps two layers at 2 oz and is re-routed with its SIGNALS ON THE TOP LAYER over a solid back-side ground pour: B.Cu is a power layer in the DSN (the router lays no wire there, vias pass) and the ground pour is its plane; the pack path's locked bands on both layers are tracks the router keeps. If the router cannot close the board this way the numbers go back to the owner.

- 15 September 2026, owner scope answer 1 of the return-current ruling: P1 to P4 routed both layers freely; P5 makes B.Cu a power layer with the ground pour as its plane so every signal stays on the top layer over solid ground (rule 1 cannot hold for a back-side track on a two-layer board).
