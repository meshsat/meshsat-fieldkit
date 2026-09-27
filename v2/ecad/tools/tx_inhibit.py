#!/usr/bin/env python3
"""Every transmitter on the netlists, and the hardware path from EMCON to it (rule RF-002, S-02 of MESHSAT-1357,
26 September 2026).

WHY THIS EXISTS. RF-002 says every transmitter can be inhibited by a hardware path that does not depend on
software. Until today it was judged by the `inhibit` contracts of check_contracts.py, which ask about the LINE:
it is present on each board, it reaches board D's keying gate, the panel toggle is its only driver, its sense is a
buffer, and every consumer pulls it down. None of them asks the rule's own question, which is about the
TRANSMITTERS. Board B read PASS of 3 while its three Compute Modules' own WiFi and Bluetooth radios were disabled
only by a software I/O expander (U6, a PCA9555 on the kit bus), and its two AsiaRF AW7915-AED cards were "disabled"
through a W_DISABLE1# pin their maker does not document (CONOPS section 4b, adjudication A11). That was a false PASS.

WHAT IT CHECKS. The TRANSMITTERS table below is CONOPS section 4b's list, one entry per radio, each with the part
that anchors it on a netlist and the ways EMCON may reach it:
  power       every supply rail of the anchor is the output of a switch this file knows (eFuse, load switch,
              converter), EMCON forces that switch's enable pin to its OFF level, and nothing else feeds the rail;
  rf_disable  EMCON forces a pin of the anchor to the level at which the radio's MAKER says the RF is off, and the
              citation is written beside it. A pin whose effect no maker document states does not count. An option
              may also say how the pin may be driven (`drive="open_drain"` for the Compute Module 5's WL_nDisable and
              BT_nDisable, which "may only be driven low"), and then the last element before the pin must be an
              open-drain output or an N-channel switch to ground;
  key         EMCON forces the transmitter's own keying pin to its receive level.
An entry passes when ONE of its options is proved on the netlist. The proof is a forward walk from the asserted
line (`EMCON_HW` and `TX_INHIBIT_n`, both LOW when EMCON is on) through parts whose pin maps are known from their
datasheets: an AND gate forced low by a low input, an inverter, a buffer, an N-channel level shifter with its gate
on a rail or an N-channel switch to ground, a series resistor.

AND EVERY NET ON THE WAY IS DRIVEN BY NOTHING ELSE (review fix-up of round 4, 26 September 2026). A gate net that
another active part can also drive is not a hardware gate, because the two drivers fight and the software one can
win. The first version asked that only of the LAST net, so board D's keying path passed while KEY also reached a
PCA9555 pin through a level-shifter FET, and board B's and C's paths passed while EMCON_HW itself carried three
STM32 pins and an RP2040 pin. Now every net of an accepted path is taken as a CONDUCTOR: from the net, across the
mated board-to-board connectors (the four ribbons whose maps check_contracts proves identical) and through series
resistors, beads, level-shifter channels and any diode that can pull it away from the level EMCON forces, every pin
found must be known to only READ it (a logic input on the land its pin map is for, wired as its row holds where the
part's function is set by its wiring (EQ-18), a FET gate, a switch enable, a pin a maker document calls an input, or
a tap declared in READER_TAPS with the resistor that makes the gate win).
A pin whose direction firmware sets (a controller, an expander) FAILS the path; any other pin nobody has shown to be
an input leaves it UNDECIDED, named, which check_contracts counts as INCONCLUSIVE and never as a pass. The two
asserted lines are judged once each as a set-wide conductor ("line" results), and a path inherits its line's answer.

AND THE LINE IS ASSERTED WHEN ITS SOURCE IS GONE (second fix-up of round 4, 26 September 2026). RF-002 also asks that
"the inhibit is asserted by the unpowered and disconnected states". With the panel unplugged or unpowered the line is
held only by its own pull-downs, and each of its fail-safe states (every subset of its ribbons unplugged, and its
source's board unpowered) is solved as a resistive network with every pull-up, firmware pin, maker-stated internal
pull-up and FET or diode that can pass current toward it; the line must stay under the gates' 0.8 V VIL in every one
(fail_safe() below). Board B's level shifters Q106, Q206 and Q306, whose body diodes source EMCON_HW from the slot
rails, were the case that made this necessary. Since round 6 (26 September 2026) every pin on the conductor also
passes the current its sheet guarantees (II of a powered input, Ioff of an unpowered part, a switch enable's current,
a module's own pull), because at 100 kOhm the SN74LVC08A inputs alone lift EMCON_HW to 1.5 V; a pin whose current no
held sheet bounds leaves the state UNDECIDED. Since round 6's second pass every part but the reader is taken powered
or unpowered, whichever is worse, because an unpowered LVC1G part passes twice the current it passes powered and any
board, or any one rail of a board, can be down while another reads the line (the review of round 6, blocking 1: with
boards B and C unpowered and A powered the 47k/22k kit read 1.05 V in a state round 6 never solved); resistors and
rails are taken at the adverse end of their tolerance (R4T-D36).

AND A GATE THAT LOSES ITS OWN SUPPLY LEAVES NOTHING FLOATING (round 6, R4T-F9, ruled in scope by the review of the
second fix-up). Every element on an accepted path that has a supply of its own is taken down, and the enable or keying
pin it drove must then be held at EMCON's level by what else is on its net, against every pin's stated current, at the
threshold of whatever reads it (own_supply() below). Board B's LIME_EN, RB_EN and E22_EN (switches on +5V_DEV, their
gate on +3V3_DEV) and board D's SA_PTT_n (the SA868 on +5V_SA, its inverter on +3V3_D8) were held by nothing at main
faf8c981; main 458b2873 carries board B's pull-downs R514 to R517 and board D's open-drain U13 with its R88/R89 divider.

AND A PART RUNS FROM ITS SUPPLY PIN, WHATEVER THE NET IS CALLED (round 6 third pass, R4T-D41, the review of round 6's
second pass, blocking 1). A logic part's supply is its VCC pin and a switch's its input pin, as their makers' pin tables
give them; a reader whose supply the netlist does not show is bounded on its own. A reader on VBAT, VCC_X or 3V3_DEV used
to have no supply at all and was never judged, so a line with nothing holding it read PASS. A net is a supply when it is
a '+' rail, when its name says so, or when a VCC or VIN pin sits on it; only a '+' rail's name is read for a voltage, so a
live supply whose name states none leaves a state UNDECIDED where it used to be walked as a signal and ignored. The name
test knows VDD, VCC, VIO, VBUS, 3V3, 1V8, 5V0 and 5V; a net named VBAT, VIN, VSYS or 12V is a supply only where a logic VCC
or a switch VIN pin sits on it on the same board (at main 458b2873, board A's and board E's VIN_RAW, board B's VBAT, board
D's PCM_VIN and board E's VIN_MON are not), and is otherwise walked as a conductor, which meets its parts and can only
FAIL or leave a path UNDECIDED.

AND A SUPPLY IS JUDGED BY HOW IT IS KNOWN (round 6 fourth pass, R4T-D42 and R4T-D43, the review of the third pass). The
third pass counted any supply as a harmless pull on a net EMCON holds high and stopped the walk at a supply known only by
its name, so a link from SA_PTT_n to a sensor rail a GPIO powers read PASS; and its second-feed check read only a '+'
rail at a resistor's far end and no transistor at all, so a resistor from the gated switch's own VIN and a P-channel FET
around the switch read PASS. Now a pull on a net EMCON holds high is harmless only to a '+' rail at or above the level
EMCON holds, a pull to a supply whose voltage no name states is UNDECIDED and a 0 Ohm link to one FAILS, a supply known
only by its name is walked for its drivers as well, and a resistor from a pin-map supply or a transistor channel onto a
gated rail is a second feed.

AND WHAT IS BEHIND A RESISTOR ON A GATED RAIL IS READ (round 6 fifth pass, R4T-D49, the review of the fourth pass, blocking
1). The fourth pass read a resistor's far end only through the three supply tests, so a resistor to any other net was "not
a feed": a second load switch's output or a P-channel FET behind a 0 Ohm or 1 Ohm link onto a net named X_ALT, and an
RP2040 GPIO on the rail itself, read PASS where the same parts on +5V_ALT FAILED. Now the far net of every such resistor,
and every net further resistors join to it, is read with the rail's own rules, a pin of a part firmware sets FAILS on the
rail's conductor and is UNDECIDED behind a resistor, and a shunt or a 0 Ohm link on the conductor joins the net on its
other side to the conductor in either direction.

AND A FIRMWARE PART'S PIN IS A LOAD ONLY BY ITS MAKER'S ROW (round 6 sixth pass, R4T-D50, the review of the fifth pass,
blocking 1). The fifth pass let a firmware part's pin on the rail through as a load whenever its name looked like a supply,
so a Compute Module 5's CM5_3.3V or CM5_1.8V (regulator outputs of up to 600 mA, CM5 datasheet 3.4, pins 84, 86, 88
and 90 "(Output)"), a CP2102N's VDD with its regulator powered (CP2102N Rev 1.5, Table 3.6 and note 1) and an RP2040 pin named
GPIO24_VBUS read PASS on a gated rail. Now a pin is a load only where a held pin table (FW_PIN_TABLES: RP2040, STM32H7,
PCA9555, CP2102N, Compute Module 5) gives it as a supply input; its supply outputs, its ground, and a pin tied to another
(a CP2102N's VDD to VREGIN, an STM32H7's VREF+ to VDDA) with that other pin powered from elsewhere FAIL; a supply word the
tables cannot place is UNDECIDED.

AND A BATTERY PIN IS TIED TO THE SUPPLY ITS CHARGER RUNS FROM, AND A PART IS READ BY WHAT IT IS (round 6 seventh pass, R4T-D51
and R4T-D52, the review of the sixth pass, blocking 1 and 2). The sixth pass counted both parts' VBAT as plain supply inputs,
where firmware can switch on a charger that drives current OUT of each: an STM32H7 connects VDD to VBAT through 5 or 1.5
kOhm (DS12110 Table 95, VBRS in PWR_CR3), and a Compute Module 5's RTC has a 3 mA constant-current, constant-voltage
charger switched on from config.txt (rtc_bbat_vchg). Each VBAT is now tied, to VDD and to the module's 5V: a load only
with its partner on the rail's conductor, FAIL with the partner on another live net, UNDECIDED otherwise. And a part whose
VALUE only mentioned the Compute Module ("on the Compute Module 5 PCIe lane") was read with the module's pin numbers, so a
PCIe switch's VDDR at pin 77 passed as the module's 5V: now a family, and whether firmware sets a part's pins at all, is
found by the part itself (its library symbol, the start of its value, or a receptacle's "(CM5 pins" form), and a row read
by the maker's pin number counts only when the symbol names the same row there.

AND A PART THAT ONLY MENTIONS A FIRMWARE FAMILY IS NAMED, A ROW'S PINS ARE EVERY PIN ITS MAKER NUMBERS THERE, AND A TIE IS READ
BOTH WAYS WHERE ITS DIRECTION IS NOT STATED (round 6 eighth pass, R4T-D53 to R4T-D55, the review of the seventh pass, blocking
1 to 3). Anchoring the firmware class (R4T-D52) let a part whose value only began with a descriptor ("I/O supervisor
STM32H743VIT6" on a custom symbol, "Slot S1 compute: CM5108032") sit on a gated rail as a silent load by any pin, VCAP and pin
84 CM5_3.3V among them: such a part is now UNDECIDED wherever an active pin of it is met, naming the family it mentions. A
supply row's other pins are every pin the maker's number places in it, whatever the symbol calls them, so a Compute Module
5V pin misnamed '+5V' or left unnamed on another net is named, not dropped. And an STM32H7's VDD on a gated rail with its
VBAT on another live net is UNDECIDED, since the held sheets draw the charger between the two pins with no direction marked.

AND THE MENTION IS SEARCHED AS THE SIXTH PASS SEARCHED IT, VDD'S EVERY JOIN IS READ, AND A GATE'S OUTPUT, A P-PORT AND AN
ADC INPUT ARE READ ON A GATED RAIL (round 6 ninth pass, R4T-D56 to R4T-D59, the review of the eighth pass, blocking 1 and 2
and minor 3 and 4). The eighth pass said the mention was searched as the sixth pass searched it, and searched it with the
narrowed SOFTWARE_IO, so 'Raspberry Pi CM5 8GB/64GB wireless', a bare 'CM5' or 'Raspberry Pi Compute Module (8GB)' with pin
84 CM5_3.3V or a GPIO on a gated rail read PASS in silence: FW_MENTION adds back the sixth pass's 'CM5' with any digits
and 'Compute Module', for the naming only (R4T-D56). The STM32H7's VDD had one join read, to VBAT; the same section 3.5.1
gives it a second, to VDDA, VDD33USB and VDD50USB, which must stay under VDD + 300 mV while VDD is below 1 V (DS12110
Figure 3, 'Invalid supply area'), so VDD on a gated rail with any of them live elsewhere is UNDECIDED (R4T-D57). A PCA9555
with VCC on a gated rail and a P-port pin held elsewhere feeds the rail through the 100 kOhm pull-up SCPS131J Figure 8-2
draws, and an RP2040's ADC input above IOVDD leaks into it through its ESD diodes (datasheet 2.9.5): each is UNDECIDED unless
that pin's net is shown to carry only loads (R4T-D58). And a logic gate's push-pull output, which LOGIC's pin maps give,
FAILS on a gated rail's conductor and is UNDECIDED behind a resistor, where a plain '74LVC1G34 buffer' with Y on the rail
read PASS (R4T-D59). No result moves on main 44cfa045's six netlists: no firmware supply row, P-port, ADC input or gate
output sits on a gated transmitter conductor there.

AND VDD'S VDDLDO, THE MODULE'S GPIO_VREF AND EVERY OTHER SUPPLY PIN OF A PART ON A GATED RAIL ARE READ (round 6 tenth pass,
R4T-D60 to R4T-D62, the review of the ninth pass, its two items and its suggestion). The ninth pass excused VDDLDO beside a
gated VDD, saying 3.5.1 names only VDDA, VDD33USB and VDD50USB; the same sheets tie it: Table 24 'General operating
conditions' gives VDDLDO the condition 'VDDLDO <= VDD' (DS12110 Rev 10 6.3.1, page 106; DS12117 Rev 9 Table 23, page 106),
and 'When it is not available on a package, the VDDLDO pin is internally tied to VDD' (DS12110 Table 9 note 8, page 87), so
VDD on a gated rail with VDDLDO live elsewhere is UNDECIDED (R4T-D60). A Compute Module 5's 5V on a gated rail with GPIO_VREF
on an external supply read PASS, while 2.9 (page 11) allows an external GPIO_VREF 'only ... while CM5_1.8v is on' and 3.1
(page 15) says 'No pins should be powered before the 5 V rail is active': the 5V is now a load only with GPIO_VREF on the
rail, on ground, nowhere, or on a net fed only by the module's own CM5_3.3V or CM5_1.8V, which it makes from the 5V
(R4T-D61). And, closing the class instead of one row per review, a supply input on a gated rail is now UNDECIDED while ANY
other supply pin of the part sits on a live net off the rail's conductor, unless that net is fed only by the part's own
outputs made from a supply on the rail (_own_fed), or a held sentence of its maker's lets the two fall in that order: the
STM32H7's 'When VDD is above 1 V, all power supplies are independent' (3.5.1, with VDD up), the RP2040's 'power supplies may
be powered up or down in any order' (2.9.6), the Compute Module 5's VBAT that keeps the RTC 'even when the board is off'
(2.12.2 Table 3) (R4T-D62). It reads VREF+ above a gated VDDA (Tables 87 and 89), a CP2102N's VREGIN beside a VDD fed from
elsewhere, its VIO (Table 3.1: 1.71 V to VDD) and its VBUS (2.3: leakage into the unpowered part; a case the sixth pass
wrote as ACCEPTABLE, R4T-F35), VDD50USB beside VDD33USB with VDD not up, GPIO_VREF on a gated rail with the module's 5V
elsewhere, and any pin with a supply word the table does not place. No result moves on main 44cfa045's six netlists: no
option gates a rail that carries a firmware part's supply, and fw_pin_role() is not reached there.

AND A FIRMWARE PART ON THE MODULE'S OWN OUTPUT, A PULL FROM IT, A PART WHOSE MAKER STATES A PATH BACK INTO ITS SUPPLY, A
SUPPLY WORD WITH A SEPARATOR, AN OUTPUT HELD FROM OUTSIDE AND EVERY I/O OF A SUPPLY'S DOMAIN ARE READ (round 6 eleventh pass,
the final one, R4T-D63 to R4T-D68: the review of the tenth pass, its blocking item and the minors it listed as named limits
that still read PASS in silence, under the stop rule of the review of 26 September 2026 22:35: no case reads PASS in silence
where a held maker document says the part can feed or drive the path, and one the held documents cannot decide reads
UNDECIDED). The tenth pass's own-output test took another firmware part's supply input on the module's CM5_3.3V as unable to
feed it on its table row alone, so a PCA9555, an RP2040, an STM32H7 or a CP2102N there held GPIO_VREF's net up through a join
its maker documents and the module's 5V read PASS: fw_pin_role() now judges that pin with all its joins, and any verdict but a
load is a source (R4T-D63). A pull from that net to a net a regulator or a buffer drives read PASS: the pull is read through
(R4T-D64). A logic part or a switch running from the rail or from the module's own output with an output held up read PASS,
where its maker states a path from that output into its supply or rates the output by that supply: the SN74LVC08A's positive
clamps (SCAS283W 7.3.3), the SN74LVC08A's, 32A's and 00A's outputs at most VCC + 0.5 V with no Ioff (5.1), the TPS22810's body
diode (SLVSDH0C 10.4), the TPS2596's and the AP64500's outputs at most their input plus 0.3 V (SLVSET8A 7.1, DS41979): each is
read now (R4T-D65). A supply name with an underscore ('VDD_IO', 'VDD_A', 'VDD33_USB') and a module named 'RPi_CM5_8GB' or on
the library 'meshsat:RPi_CM5' were not found (R4T-D66). A sentence that lets a part's supplies fall in any order excused the
part's own output held up by another regulator (an STM32H7's VCAP, an RP2040's VREG_VOUT against 2.9.7.2), and a PASS that
rested on such a sentence said nothing: the first is UNDECIDED and the second names the sentence in its text (R4T-D67). And an
I/O of a firmware part held up while its supply falls with the rail read PASS, where the part's maker bounds what that pin may
carry then (RP2040 Table 622, STM32H7 Tables 21 and 22, CP2102N Table 3.10, CM5 4.2.1): UNDECIDED now, but the RP2040's fault-
tolerant pins (Table 614) and the PCA9555's INT and address pins (SCPS131J 6.1; its SCL too until R4T-D73), which their
sheets decide (R4T-D68). No
result moves on main fc144600's six netlists: no option gates a rail that carries a firmware part's supply, a logic part's VCC
or a switch's input, and the new branches return nothing there.

AND A PIN ON A GATED RAIL IS A LOAD ONLY WHERE A ROW OF ITS MAKER'S CLEARS IT (round 6 twelfth pass, R4T-D70 to R4T-D73: the
review of the eleventh pass, its three blocking items closed as classes and not case by case, by the session's decision of 27
September 2026 under the owner's standing rule of 26 Sep 2026, following the second checkpoint review's findings D and G, that
verification-tool work must not dominate the schedule). The default is inverted. A pin on a gated rail's conductor, behind a
resistor from it, or on a net that falls with it reads as a load only where a class row whose held maker document states the
pin sources no current into the net clears it, and the PASS carries that row's words ("taken on its maker's words"); every
other pin reads UNDECIDED, named with the part, the pin and the reason, which check_contracts counts as INCONCLUSIVE and never
as PASS. The rows (R4T-D71): a logic input by its sheet's II; an open-drain output by its maker's words; a logic VCC by its
Ioff row, or with nothing holding its outputs up (the SN74LVC08A's and 00A's inputs having negative clamps only); a switch's
enable its maker states only leaks (the TPS22810, the TPS25963); a switch's input with nothing holding up an output or a pin
no row clears; the USBLC6-2's VBUS with nothing holding its I/O up (DS4260's topology); a firmware part's supply input by its
table (FW_PIN_TABLES), as before. So a part in no class (board B's USBLC6 U33 and E72 modules, board A's INA226, until now
limit (1), R4T-F23), a switch's pin other than its outputs, its input and an enable that only leaks (the AP64500's and the
LM5176's enables, whose makers state a current sourced out of the pin; the LM5176's VCC), a logic part's pin its map does not
place, a declared accessory's connector, and any pin of a transistor this file cannot read, read UNDECIDED; a logic part's or
a switch's ground with the part's supply up FAILS, as a firmware part's ground does. Every pin of every part that carries the
same module (board B's U30B beside U30A: pins 101 to 200 beside 1 to 100) is read as the module's own (R4T-D72). And the
maker's words a load rests on reach the PASS from the nets read off the rail too (R4T-D73: the eleventh pass dropped them on
the module's own-output path), an `io` pin a `free` row clears is named with its words when something holds it up, and the
PCA9555's SCL is read as its SDA is (SCPS131J 6.3 note (1)). No verdict moves on main a6f87e9d's six netlists: the options
this touches (board B's J_LIME, U13 and U14, board A's J_PA) read FAIL on their lines or UNDECIDED already, and their texts
now name U33, the E72 modules, J_ZBDBG1, J_ZBDBG2 and the INA226.

AND A CONFIGURABLE GATE IS READ ONLY IN THE WIRING ITS ROW HOLDS (EQ-18, stream w3t, 27 September 2026; taken by the session
under the owner's standing rule of 26 Sep 2026). Board C's round 8 put its hardware EMCON lamp's gate U14, a TI SN74LVC1G57,
on both asserted lines (In0 pin 3 on TX_INHIBIT_n, In2 pin 6 on EMCON_HW), and with no row for it the walk read both lines
UNDECIDED at U14 ("an active pin no held document shows to be an input"). Its function is set by how its inputs are wired
(SCES414P 8.1), so its row carries its maker's pin map (Pin Functions, DBV and DCK), its II, Ioff and input clamp rows (6.5,
6.1) and one configuration, Figure 7's: In1 (pin 1) tied to the part's own GND pin on a ground net, where Table 1 gives Y =
NOR(In0, In2). logic_of() gives the part that NOR only where its netlist carries that wiring; any other wiring reads
`unwired`, and every reader of LOGIC then takes it as a gate on a land its map is not for: the walk stops there, and a pin of
it on a conductor, a line or a gated rail is UNDECIDED, named with the wiring found (limit 13). Its Schmitt inputs are read at
VIL_LOW, VT- being 0.84 V minimum at VCC 3 V, and it and the 74LVC1G17 never pass a HIGH, VT+ being stated at VCC 3 V and 4.5 V
only (`vih_gap`, limit 14). On main 38dcd764's six netlists U14 is wired as Figure 7 draws: the EMCON_HW line reads PASS (was
UNDECIDED at U14 pin 6), and the TX_INHIBIT_n line reads FAIL (was UNDECIDED at U14 pin 3): with board C unpowered, its three
100 kOhm pull-downs (A R145, B R59, D R2) against 31 uA of stated pin current (C U9's and U14's Ioff, 10 uA each, D U12's 10
uA, A U35's and U37's 0.5 uA each) reach 1.09 V over the gates' 0.8 V VIL; without U14 the same state read 0.74 V. That is a
circuit finding (the line's pull-downs against the input round 8 added), not the tool's; board D's SA868 inherits it, and
board B's RockBLOCK 9704 and E22-900M30S, which rode only the EMCON_HW line, read PASS.

WHAT THE WALK DOES NOT READ (named; RF-002's coverage row carries the same list with gap SOURCE_OR_APPLICABILITY_UNRESOLVED.
Since the twelfth pass no pin on a gated conductor is a load without a word: each item is a clearance that rests on something
other than a maker's row, named here so that none is silent, a size or a state the walk does not judge, or a false UNDECIDED,
seen):
  (1) Clearances by what a part is, not by a maker's row: a capacitor (it passes no direct current), a test point or a power
      flag, a MOSFET's gate (fet_of: an N- or P-channel MOSFET by its symbol or part number), a resistor, a discharge FET or a
      diode to ground or to nothing, a diode whose anode is on the net, and the parts that carry the switch's output to the
      rail. A capacitor fitted reversed, its leakage and a diode's reverse leakage are not judged (7). The transmitter's own
      anchor part is not read on its own rail, so its own I/O lines (an E22's or an E72's UART held up by its host while its
      rail is off) are not read there.
  (2) The rows clear by a stated leakage or rating whose size is not judged (7): a logic input by II, a logic VCC by Ioff, a
      switch's enable by IEN or IENLKG; II is stated with VCC in its range, and an input of a part with no Ioff row whose VCC
      is down is read on it too. A switch's input is cleared only with nothing holding up a pin of it that no row clears (the
      LM5176 has no row but its enable's, so its input is a load only with every other pin of it held by nothing). The I/O of
      an STM32H7 with VDDA or VDD33USB on the rail and VDD up are read with VDD, and its analogue and USB pins are not told
      apart. A logic part's or a switch's ground is found by its pin's name; a ground pin named otherwise is UNDECIDED.
  (3) The own-output net and the nets behind its pulls are read in the second-feed check's words (R4T-D63, R4T-D64), which
      counts as a source what the reading cannot show unable to feed them. False UNDECIDEDs follow: an N-channel level shifter
      whose gate is on the own-output net (its channel and its body diode cannot lift that net), a fan connector's PWM pin and
      a converter with no row behind a pull: board B's Q102 to Q105, J_FAN1 and U105 behind R154 to R157, R151 and R111 would
      make its modules' 5V UNDECIDED if a slot rail were ever gated (none is). Behind R111 also sits U104's enable, the
      AP64500's stated current source (DS41979 3 Enable), which the eleventh pass skipped and which is a source now, not a
      false one. The reading stops at _NS_DEPTH (4) steps and counts what lies beyond as a source. A sentence that lets two
      supplies fall in any order (the STM32H7's 3.5.1 with VDD up, the RP2040's 2.9.6, the module's 2.12.2 for its RTC cell) is
      still read as saying nothing flows between them then, a statement about sequence taken as one about current; each PASS
      that rests on one quotes it (R4T-D67, and since R4T-D73 on the own-output path too).
  (4) The RP2040's ADC_AVDD transient when it outlives DVDD (datasheet 2.9.6, page 152).
  (5) FW_MENTION searches the whole value and library string, the library's nickname before the colon included, and
      SOFTWARE_IO's 'CM5' with three digits anywhere, so a part mentioning a family for another reason ('TXS0102 level
      shifter for the RP2040', a library 'RP2040_support', 'SCM5100') is UNDECIDED on a rail where it may be a plain load;
      the PCIe coupling capacitors that cite the CM5 datasheet and board B's J_PANEL mention one and are handled as a
      capacitor and a connector first. A firmware part whose value and symbol name no family FW_MENTION knows (an RP2350, a
      custom 'I/O supervisor A') is a part in no class, UNDECIDED on a gated rail since the twelfth pass, and not named as
      firmware.
  (6) The rows of the RP2040, STM32H7, PCA9555 and CP2102N go by the symbol's pin names, and the RP2040's fault-tolerant pins
      by name (GPIO0 to GPIO25, SWCLK, SWD, RUN); only the Compute Module 5's go by the maker's numbers, and a receptacle's
      declared pin range is not checked against its numbering. The parts that carry one module are found only in one form
      (_module_refs, R4T-D72): a family its maker numbers (the Compute Module 5 alone), a reference ending in one letter A to H
      right after a digit, and a sibling whose own value or symbol names the same family; board B's U30A plus U30B (and U31,
      U32) is that form. Every other drawing of a split symbol is read part by part, see (8). A supply name with a separator is read (R4T-D66); a supply pin whose name carries none of the supply words
      ('PWR', 'POWER') is outside the class. A supply pin of a part on any live net off the rail is read whether or not
      anything holds that net up (a false UNDECIDED where nothing does).
  (7) A charger's current and a feed's size (an Ioff, an II, an enable's leakage, an off-state leakage, a clamp current) are
      not judged; a tied pin is judged by where its partner is drawn, not by whether the partner's net is live while the rail
      is off; a firmware pin behind a resistor is UNDECIDED whatever its row; the second-feed check follows resistors, not FET
      channels or diodes, past the first part; a gate on a land its map is not for, or a configurable gate wired as its row
      does not hold (13), is UNDECIDED by any pin; the census takes
      a '+' rail as always up; the second-feed check reads this file's ACCESSORIES, not the list a caller passes judge()
      (every accessory on a gated rail reads UNDECIDED either way since the twelfth pass).
  NAMED AT INTEGRATION (27 September 2026, the final independent check of the twelfth pass; its blocking item and four of
  its minors, each named here and in RF-002's coverage note rather than closed, by the session's decision under the owner's
  standing rule of 26 September 2026; no board on the six committed netlists is read through any of them):
  (8) A SPLIT SYMBOL IN ANY OTHER FORM READS PASS, mostly with no word. Only (6)'s one form is joined, so the Compute Module
      5 drawn as U30 (pins 1 to 100) plus U30B, or as U30-A plus U30-B, or U30A plus a U30B on a generic connector symbol
      that names no family, and an STM32H7, an RP2040, a PCA9555 or a 74LVC32A drawn with its power unit as its own
      reference (U41A with VDD on the rail, U41B with an I/O held up), each read the part carrying the supply alone: the
      pin held up on the other part is not read, where the same part drawn whole reads UNDECIDED with its maker's limit
      (the checker's probes rv16/probe4.py and probe5.py; the 74LVC32A case even quotes 'no output of it is held up', which is
      false). _net_sources() keeps its module skip to the Compute Module, so two distinct chips named U5A and U5B are not
      merged there. On the six committed netlists the only split references are board B's U30A/B, U31A/B and U32A/B, all
      of that one form; tests/test_tx_inhibit_split_guard.py fails if any board carries another, so a split drawing is
      loud on the real design before it can be read part by part.
  (9) A PART'S KIND IS READ FROM ITS DESIGNATOR PREFIX in the second-feed check: a two-pin part whose reference begins D,
      LED, L, FB or F is cleared as a clamp to ground when its far pin is on ground or dead, and a reference beginning #, TP
      or C followed by a digit is skipped, whatever the part is; so a fan (FAN1, Motor:Fan), a supercapacitor module (DC1),
      a cell (LB1, Device:Battery_Cell) or a supervisor designated TPS1 on a gated rail reads PASS with no word, where a
      battery designated BT1 reads UNDECIDED. _net_sources() needs a digit after the prefix and _second_sources() does not.
      No part on the six committed netlists is misread this way (the checker scanned them).
  (10) A FIRMWARE PART'S SUPPLY INPUT CLEARED BY ITS FW_PIN_TABLES ROW ALONE passes with no quote of that row: fw_pin_role()
      returns a load with no words where the tied partner is on the rail and where no other supply pin is live, so a
      PCA9555's VDD alone on the rail, a CP2102N with VDD, VREGIN and VBUS on it, or an STM32H753's VDD alone PASS without
      'taken on its maker's words'. A row does clear them (traceability, not a silent load).
  (11) A NET THAT IS ITSELF A SUPPLY IS NOT COUNTED AS A SOURCE by _net_sources(): only the parts drawn on it are, and a
      resistor from a supply is. A pin of a switch or logic part on a '+12V' net that holds nothing else on the board (an
      LM5176's BIAS, probe B2-9) reads 'no other pin of it is held up by anything on its net'. On the committed netlists
      the supply's regulator or connector is always drawn on the net, so no reading moves.
  (12) A SWITCH WITH NO ENABLE ROW (no _EN_ROWS entry): its enable held up beside its input on the falling net reads
      UNDECIDED, named, as _class_pin reads it; before the integration this raised KeyError and stopped the walk. All five
      SWITCHES rows carry an enable row today.
  NAMED WITH EQ-18 (stream w3t, 27 September 2026):
  (13) A CONFIGURABLE GATE IS READ IN ONE WIRING. The SN74LVC1G57 row holds Figure 7's NOR alone: In1 on the same net as the
      part's own GND pin, that net a ground. In1 to ground through a resistor or a link, on a ground net other than its GND pin's,
      on VCC, on a signal or floating, and every other configuration its maker's Table 2 lists (AND, NAND and OR with an
      inverted input, XNOR), read UNDECIDED by any pin, which is a false UNDECIDED where that wiring would have held. The part's
      VCC pin is still read from its pin map in any wiring (_supply_nets). The condition is read from the netlist's nets, not
      from the pin names the symbol carries (board C's symbol names its pins after their nets). On the six committed netlists
      the only configurable gate is board C's U14, wired as Figure 7 draws.
  (14) A HIGH AT A SCHMITT INPUT NEVER PASSES. The 74LVC1G17 (DS35124) and the SN74LVC1G57 (SCES414P) state VT+ at VCC 3 V and
      4.5 V and at no VCC between, and their 4.5 V rows (2.74 V maximum) are above VIH_HIGH, so a net EMCON holds HIGH at such an
      input is UNDECIDED at any level at or above 2.0 V and FAILS under it (_threshold, `vih_gap`): a false UNDECIDED for a net
      driven to the reader's own rail. Their VT- is read at the 3 V row over the whole band (0.80 V and 0.84 V minimum, at or
      above VIL_LOW, as every row either sheet states at 3 V and above is), an inference from rows that rise with VCC, not a
      stated band. No held net on the six committed netlists is read HIGH at either family.

AND IT WALKS WHAT MAIN 458b2873's BOARD B DRAWS (round 6 fourth pass, R4T-D46 and R4T-D47). S-01 inverts EMCON_HW once with a
2N7002 switch to ground (Q11, EMCON_ON pulled up by R513) and gates each module radio with an SN74LVC32A OR; the WiFi cards'
supplies reach their sockets through 5 mOhm shunts. A FET EMCON holds off now releases its drain to the level its pulls
set, as an open-drain output does (R4T-D38), and is judged the same way: with its pull-up's rail down, and with its own
off-state current, which the fitted 2N7002 states at 25 C only; the OR has its TI pin map; and a rail is traced to its
switch through one current-sense shunt. The fourth pass said the second-feed check then read "every net of that
conductor"; it read only the nets from the switch to the rail, so where the switch is found by a sense pin on the rail
itself (board A's LM5176s, by VOSNS) the power stage's own node behind the sense resistor (PA_OUT behind R55, HF_OUT behind
R65, with the boost-leg FETs Q14 and Q24 on them) was never read. Since the fifth pass (R4T-D49) the conductor is the path
and every net a shunt or a 0 Ohm link joins to it, either way, unless that net is a supply.

AND IT FINDS WHAT THE TABLE FORGOT. Every part whose value names a radio is claimed by an entry, declared an
accessory (a debug header, a data lead, a coax pigtail) with the reason, or declared receive-only with the reason.
A part that is none of these is a transmitter nobody classified, and it fails. A declaration that rests on an
inference rather than a maker statement is listed in OWED and leaves its board UNDECIDED until the statement is held.

Each result is dict(ok, text, detail, boards), where ok is True, False, or None for UNDECIDED. This module writes no
verdict of its own: check_contracts.py runs it inside its `inhibit` group, which writes `inhibit_chain_<letter>`,
the verdict RF-002 reads. Usage for a report: tx_inhibit.py <netlist.net>..."""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

SOURCES = ("EMCON_HW", "TX_INHIBIT_n")        # asserted LOW (PANEL.md; C's SW_EMCON closes to ground)
GROUND = re.compile(r"^(GND|AGND|DGND|PGND|GNDA|VSS|EARTH|CHASSIS)([_\-].*)?$", re.I)


# ---------------------------------------------------------------- the netlist
def parse_netlist(path):
    """{"comps": {ref: {value, fp, lib}}, "nets": {name: [(ref, pin, func)]}, "pin": {(ref, pin): net},
    "func": {(ref, pin): pinfunction}}, or None when the file is absent."""
    if not path or not os.path.isfile(path): return None
    txt = open(path, encoding="utf-8", errors="replace").read()
    comps = {}
    for ch in re.split(r"\(comp ", txt)[1:]:
        m = re.match(r'\(ref "([^"]+)"\)\s*\(value "((?:[^"\\]|\\.)*)"\)', ch)
        if not m: continue
        head = ch[:4000]
        ls = re.search(r'\(libsource \(lib "([^"]*)"\) \(part "([^"]*)"\)', head)
        fp = re.search(r'\(footprint "([^"]*)"\)', head)
        comps[m.group(1)] = {"value": m.group(2), "fp": fp.group(1) if fp else "",
                             "lib": ("%s:%s" % ls.groups()) if ls else ""}
    nets, pin, func = {}, {}, {}
    for m in re.finditer(r'\(net \(code "?\d+"?\) \(name "([^"]*)"\)(.*?)(?=\(net \(code|\Z)', txt, re.S):
        name = m.group(1).lstrip("/")
        nodes = re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?', m.group(2))
        nets[name] = [(r, p, f) for r, p, f in nodes]
        for r, p, f in nodes:
            pin[(r, p)] = name; func[(r, p)] = f
            comps.setdefault(r, {"value": "", "fp": "", "lib": ""})
    return {"comps": comps, "nets": nets, "pin": pin, "func": func}


def is_ground(n): return bool(GROUND.match((n or "").strip()))
def is_rail(n): return (n or "").startswith("+")
def value(nl, ref): return (nl["comps"].get(ref) or {}).get("value", "")
def pins_of(nl, ref): return sorted(p for (r, p) in nl["pin"] if r == ref)
def _dead(n): return not n or n.startswith("unconnected-")


# ---------------------------------------------------------------- parts whose pin maps are known
# Each map is the maker's own Pin Functions table for the package the land is; a part of the family on another
# land is not walked through, because the map would be a guess there. Only the LVC parts whose TI sheets are held
# are matched (review fix-up of round 4, 26 September 2026: the first version also matched 74HC and 74AHC values,
# whose sheets are not held).
LOGIC = [
    dict(name="74LVC08 quad AND", value=r"74LVC08", fp=r"(TSSOP|SOIC|SSOP|SO)-14",
         gates=[(("1", "2"), "3", "AND"), (("4", "5"), "6", "AND"), (("9", "10"), "8", "AND"), (("12", "13"), "11", "AND")],
         cite="TI SN74LVC08A, SCAS283W (July 2024), Table 4-1 (SOIC, SSOP, SOP, TSSOP): 1A 1, 1B 2, 1Y 3, 2A 4, "
              "2B 5, 2Y 6, GND 7, 3Y 8, 3A 9, 3B 10, 4Y 11, 4A 12, 4B 13, VCC 14 (v2/vendor/ti/ti-sn74lvc08a-quad-and.pdf)",
         vcc=("14",), ii=5e-6, ioff=None, vil_ceiling=0.8,
         leak_cite="SCAS283W 5.7, -40 to +85 C: II +-5 uA at VCC 3.6 V; no Ioff row, and 7.3.3 gives the outputs positive "
                   "and negative clamp diodes, so it is not specified for partial power down",
         # R4T-D65 (round 6 eleventh pass): the one held LVC sheet that states a path from an output into VCC outright
         vcc_path="SCAS283W 7.3.3 Clamp Diodes (page 11): 'The outputs to this device have both positive and negative "
                  "clamping diodes' (Figure 7-2), 5.1 (page 5) rates 'Output voltage' at most 'VCC + 0.5' V, and 5.7 states "
                  "no Ioff, so an output held above VCC by another part drives current into VCC through its positive clamp "
                  "once VCC falls"),
    dict(name="74LVC1G08 AND", value=r"74LVC1G08", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("1", "2"), "4", "AND")],
         cite="TI SN74LVC1G08, SCES217AA (August 2026), Pin Functions (DBV, DCK): A 1, B 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES217AA 5.5, -40 to +85 C: II +-5 uA, Ioff +-10 uA (VCC 0)"),
    # BOARD A's U35 TO U38 SINCE ITS ROUND 8 (26 September 2026, MESHSAT-1357; the board A author's draft, applied by hand at
    # integration on 27 September 2026 because its base was an earlier file of this tool): the PA and HF rails' EMCON gates
    # are TI SN74AUP1G08DBVR, each rail's first gate reading TX_INHIBIT_n AND EMCON_HW and its second the software hold. A
    # walk that does not know the family stops at both lines and reads J_PA and J_HF unreached. The sheet is filed as
    # v2/vendor/ti/ti-sn74aup1g08.pdf (sha256 6d3ebde0); vil_ceiling is its highest VIL row, 0.9 V at VCC 3 V to 3.6 V (5.3).
    dict(name="74AUP1G08 AND", value=r"74AUP1G08", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("1", "2"), "4", "AND")],
         cite="TI SN74AUP1G08, SCES502Q (March 2024), Table 4-1 (DRL, DCK, DBV): A 1, B 2, GND 3, Y 4, VCC 5 "
              "(v2/vendor/ti/ti-sn74aup1g08.pdf)",
         vcc=("5",), ii=0.5e-6, ioff=0.6e-6, vil_ceiling=0.9,
         leak_cite="SCES502Q 5.5, -40 to +85 C: II +-0.5 uA (VCC 0 to 3.6 V), Ioff +-0.6 uA (VCC 0); 5.3: VIL 0.9 V at "
                   "VCC 3 V to 3.6 V, 0.7 V at 2.3 V to 2.7 V, 0.35 x VCC at 1.1 V to 1.95 V"),
    dict(name="74LVC1G04 inverter", value=r"74LVC1G04", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("2",), "4", "INV")],
         cite="TI SN74LVC1G04, SCES214AF (October 2025), Pin Functions (DBV, DCK): NC 1, A 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES214AF 5.5, -40 to +85 C: II +-5 uA, Ioff +-10 uA (VCC 0)"),
    dict(name="74LVC1G34 buffer", value=r"74LVC1G34", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("2",), "4", "BUF")],
         cite="TI SN74LVC1G34, SCES519O (October 2025), Table 4-1 (DBV, DCK): NC 1, A 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=1e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES519O 5.5, -40 to +85 C: II +-1 uA, Ioff +-10 uA (VCC 0)"),
    # BOARD C's U9 AND U12 SINCE MAIN faf8c981 (round 6): the panel's EMCON_HW buffer became a Schmitt 74LVC1G17 in
    # round 4, and a walk that does not know it neither finds the line's source nor reads TX_INHIBIT_n at its input.
    # The fitted part is Diodes Incorporated's 74LVC1G17W5-7 (LCSC C151394, SOT25), so its maker's sheet is the one read.
    dict(name="74LVC1G17 Schmitt buffer", value=r"74LVC1G17", fp=r"SOT-23-5|SC-70-5|SOT-353|SOT-?25",
         gates=[(("2",), "4", "BUF")],
         cite="Diodes Incorporated 74LVC1G17, DS35124 Rev. 8-2 (April 2021), Pin Assignments and Pin Descriptions, "
              "SOT25/SOT353: NC 1, A 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.45, leak_cite="DS35124 Rev. 8-2, Electrical Characteristics, -40 to +85 C: II +-5 uA, IOFF +-10 uA "
                                        "(VCC 0); VT- 0.80 V minimum and VT+ 2.00 V maximum at VCC 3 V",
         vih_gap="DS35124 Rev. 8-2, Electrical Characteristics (both temperature columns), states VT+ at VCC 3 V (2.00 V "
                 "maximum) and 4.5 V (2.74 V maximum) and at no VCC between, so VIH_HIGH's 2.0 V is not a stated maximum over "
                 "3 V to 3.6 V"),
    # BOARD C's U14 SINCE ITS ROUND 8 (EQ-18; stream w3t, 27 September 2026): the hardware EMCON lamp's gate is a TI
    # SN74LVC1G57, a configurable gate whose FUNCTION is chosen by how its inputs are wired (SCES414P 8.1: "The output state
    # is determined by eight patterns of 3-bit input"). Its pin map holds for any wiring, its function for one: `configs`
    # lists the wirings this row reads and the gates each selects, and logic_of() gives the part those gates only where its
    # netlist carries that wiring. Any other wiring reads `unwired` (_unmapped()): no pin of it is walked or cleared, as a
    # gate on a land its map is not for. The one wiring held is Figure 7's, In1 (pin 1) tied to the part's own GND (pin 2)
    # on a ground net: Table 1's four rows with In1 L give Y = H only for In2 L and In0 L, which is NOR(In0, In2). With In1
    # H the same table gives Y = In2 OR NOT In0 (the rows In2 H, In1 H, In0 L -> H), which no row here reads.
    dict(name="74LVC1G57 configurable gate", value=r"74LVC1G57", fp=r"SOT-23-6|SC-70-6|SOT-363",
         gates=[], gnd="2",
         configs=[dict(low=("1",), gates=[(("3", "6"), "4", "NOR")],
                       words="SCES414P Table 1 (page 8): with In1 L, Y is H for In2 L and In0 L and L in the other three "
                             "rows, Y = NOR(In0, In2); Figure 7 (page 9), '2-Input NOR Gate', ties In1 (pin 1) to GND "
                             "(pin 2) with A on In0 (pin 3) and B on In2 (pin 6)")],
         cite="TI SN74LVC1G57, SCES414P (November 2016), Pin Functions (DBV, DCK, DRL): In1 1 'Logic input 1' (I), GND 2, "
              "In0 3 'Logic input 0' (I), Y 4 'Logic output' (O), VCC 5, In2 6 'Logic input 2' (I) "
              "(v2/vendor/ti/ti-sn74lvc1g57.pdf)",
         vcc=("5",), ii=1e-6, ioff=10e-6, vil_ceiling=1.87,
         leak_cite="SCES414P 6.5 (page 5), over the recommended operating free-air range (6.3: -40 to +125 C for every "
                   "package but BGA): II +-1 uA (VCC 0 V to 5.5 V, VI 5.5 V or GND), Ioff +-10 uA (VCC 0 V, VI or VO 5.5 V; "
                   "page 1: 'The Ioff circuitry disables the outputs, preventing damaging current backflow through the "
                   "device when it is powered down'); 6.1 (page 4): input clamp current IIK -50 mA for VI < 0 only, "
                   "and the input voltage rated to 6.5 V with no condition on VCC ('Inputs are over-voltage tolerant up "
                   "to 5.5 V', 8.3.2); Schmitt inputs, VT- 0.84 V minimum and VT+ 1.87 V maximum at VCC 3 V",
         vih_gap="SCES414P 6.5 (page 5) states VT+ at VCC 3 V (1.87 V maximum) and 4.5 V (2.74 V maximum) and at no VCC "
                 "between, so VIH_HIGH's 2.0 V is not a stated maximum over 3 V to 3.6 V (gen_sch_c.py's U14 note, linear "
                 "between the two rows, reads about 2.04 V at 3.3 V)"),
    # BOARD B's U111, U211 AND U311 SINCE MAIN 458b2873 (round 6 fourth pass): S-01's module WiFi and Bluetooth kill gates,
    # KILL = OFF OR EMCON_ON, are SN74LVC32APWR on TSSOP-14. A walk that does not know the OR stops at EMCON_ON and reads
    # every Compute Module radio "EMCON does not reach it".
    dict(name="74LVC32A quad OR", value=r"74LVC32A", fp=r"(TSSOP|SOIC|SSOP|SO)-14",
         gates=[(("1", "2"), "3", "OR"), (("4", "5"), "6", "OR"), (("9", "10"), "8", "OR"), (("12", "13"), "11", "OR")],
         cite="TI SN74LVC32A, SCAS286U (July 2024), Table 4-1 (D, DB, NS, PW): 1A 1, 1B 2, 1Y 3, 2A 4, 2B 5, 2Y 6, "
              "GND 7, 3Y 8, 3A 9, 3B 10, 4Y 11, 4A 12, 4B 13, VCC 14 (v2/vendor/ti/ti-sn74lvc32a-quad-or.pdf)",
         vcc=("14",), ii=5e-6, ioff=None, vil_ceiling=0.8,
         leak_cite="SCAS286U 5.7, -40 to +85 C: II +-5 uA at VCC 3.6 V; no Ioff row, so it is not specified for partial "
                   "power down; 5.4: VCC 1.65 V to 3.6 V, VIL 0.8 V at 2.7 V to 3.6 V",
         # R4T-D65: the output's rating is bounded by VCC, with no power-off rating
         vcc_path="SCAS286U 5.1 Absolute Maximum Ratings (page 4): 'Output voltage' at most 'VCC + 0.5' V, with no rating "
                  "for the power-off state and no Ioff row (the '5.5-V tolerant' outputs of its Application Information are, "
                  "in its own note, 'not part of the TI component specification'), so an output held above VCC by another "
                  "part once VCC falls stands above that rating, and no held page says what it then passes into VCC"),
    # The families below were added before any board used them, as the parts S-01 was likely to use for the Compute
    # Modules' WL_nDisable and BT_nDisable, which "may only be driven low" (an open-drain output, or a NAND into an
    # N-FET to ground), so the walk could follow that design the day it landed. At main 458b2873 board A's U30 is a
    # 74LVC1G00 and board D's U13 a 74LVC1G06 (with board D's U11, a 74LVC1G04, above).
    dict(name="74LVC00 quad NAND", value=r"74LVC00", fp=r"(TSSOP|SOIC|SSOP|SO)-14",
         gates=[(("1", "2"), "3", "NAND"), (("4", "5"), "6", "NAND"), (("9", "10"), "8", "NAND"), (("12", "13"), "11", "NAND")],
         cite="TI SN74LVC00A, SCAS279U (July 2024), Table 4-1 (D, DB, NS, PW): 1A 1, 1B 2, 1Y 3, 2A 4, 2B 5, 2Y 6, "
              "3Y 8, 3A 9, 3B 10, 4Y 11, 4A 12, 4B 13, VCC 14",
         vcc=("14",), ii=5e-6, ioff=None, vil_ceiling=0.8, leak_cite="SCAS279U 5.7, -40 to +85 C: II +-5 uA; no Ioff row",
         # R4T-D65: as the SN74LVC32A
         vcc_path="SCAS279U 5.1 Absolute Maximum Ratings (page 4): 'Output voltage' at most 'VCC + 0.5' V, with no rating "
                  "for the power-off state and no Ioff row, and 7.3.3 (page 9) names negative clamping diodes only, so an "
                  "output held above VCC by another part once VCC falls stands above that rating, and no held page says what "
                  "it then passes into VCC"),
    dict(name="74LVC1G00 NAND", value=r"74LVC1G00", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("1", "2"), "4", "NAND")],
         cite="TI SN74LVC1G00, SCES212AC (August 2026), Pin Functions (DBV, DCK): A 1, B 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES212AC, Electrical Characteristics, -40 to +85 C: II +-5 uA, Ioff +-10 uA"),
    dict(name="74LVC1G07 open-drain buffer", value=r"74LVC1G07", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("2",), "4", "BUF_OD")],
         cite="TI SN74LVC1G07, SCES296AG (October 2025), Pin Functions (DBV, DCK): NC 1, A 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES296AG 5.5, -40 to +85 C: II +-5 uA, Ioff +-10 uA (VCC 0)"),
    dict(name="74LVC1G06 open-drain inverter", value=r"74LVC1G06", fp=r"SOT-23-5|SC-70-5|SOT-353",
         gates=[(("2",), "4", "INV_OD")],
         cite="TI SN74LVC1G06, SCES295AB (October 2025), Table 4-1 (DBV, DCK): NC 1, A 2, GND 3, Y 4, VCC 5",
         vcc=("5",), ii=1e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES295AB 5.5: II +-1 uA, Ioff +-10 uA"),
    dict(name="74LVC2G07 dual open-drain buffer", value=r"74LVC2G07", fp=r"SOT-23-6|SC-70-6|SOT-363",
         gates=[(("1",), "6", "BUF_OD"), (("3",), "4", "BUF_OD")],
         cite="TI SN74LVC2G07, SCES308L (May 2015), Pin Functions: 1A 1, GND 2, 2A 3, 2Y 4, VCC 5, 1Y 6",
         vcc=("5",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCES308L 6.5, -40 to +85 C: II +-5 uA, Ioff +-10 uA"),
    dict(name="74LVC07 hex open-drain buffer", value=r"74LVC07", fp=r"(TSSOP|SOIC|SSOP|SO)-14",
         gates=[(("1",), "2", "BUF_OD"), (("3",), "4", "BUF_OD"), (("5",), "6", "BUF_OD"), (("9",), "8", "BUF_OD"),
                (("11",), "10", "BUF_OD"), (("13",), "12", "BUF_OD")],
         cite="TI SN74LVC07A, SCAS595W (October 2016), Pin Functions: 1A 1, 1Y 2, 2A 3, 2Y 4, 3A 5, 3Y 6, 4Y 8, 4A 9, "
              "5Y 10, 5A 11, 6Y 12, 6A 13, VCC 14",
         vcc=("14",), ii=5e-6, ioff=10e-6, vil_ceiling=1.65, leak_cite="SCAS595W 6.5, -40 to +125 C: II +-5 uA, Ioff +-10 uA"),
]
# `vil_ceiling` (round 6 fourth pass, R4T-D45; the review of the third pass, minor 2) is the highest input level at which
# the family's sheet still guarantees a LOW at ANY supply voltage it allows: a line at or above it is not a logic low
# whatever the reader's VCC is, so a reader whose supply states no voltage (or one outside VCC_RANGE) FAILS there
# instead of being left UNDECIDED. The TI single and dual gates and the SN74LVC07A run from 1.65 V to 5.5 V and state
# VIL 0.3 x VCC at VCC 4.5 V to 5.5 V (SCES217AA, SCES214AF, SCES519O, SCES212AC, SCES296AG, SCES295AB, SCES308L and
# SCAS595W, Recommended Operating Conditions): 1.65 V. The SN74LVC08A and SN74LVC00A run from 1.65 V to 3.6 V and state
# VIL 0.35 x VCC, 0.7 V and 0.8 V over their three bands (SCAS283W, SCAS279U): 0.8 V. The Diodes 74LVC1G17 is a Schmitt
# input, which reads LOW once it falls below VT-, and its VT- minimum is highest at VCC 5.5 V, 1.45 V (DS35124 Rev. 8-2,
# Electrical Characteristics, both temperature columns): 1.45 V. The TI SN74LVC1G57 has Schmitt inputs too, and its VT-
# minimum is highest at VCC 5.5 V, 1.87 V (SCES414P 6.5, page 5): 1.87 V (EQ-18, stream w3t, 27 September 2026).
# `vih_gap` (EQ-18, stream w3t, 27 September 2026) is set on a family whose sheet does not state VIH_HIGH as a maximum over
# VCC_RANGE: the two Schmitt families state VT+ at VCC 3 V and 4.5 V and at no VCC between, and their 4.5 V row (2.74 V
# maximum for both) is above 2.0 V. A net held HIGH at such an input is then never read as passing (_threshold). Their VT-
# at 3 V (0.80 V and 0.84 V minimum) is still read as VIL_LOW over the band, as it was for the 74LVC1G17 since round 6:
# every row either sheet states at 3 V and above is at or above 0.8 V.
# `in_clamp` and `od_words` (round 6 twelfth pass, R4T-D71): the maker's words for the inputs of a family with no Ioff row (the
# SN74LVC08A's and SN74LVC00A's inputs have negative clamping diodes only; the SN74LVC32A's sheet has no clamp-diode section,
# R4T-F43, so it has none), which decide that an input held up passes nothing into VCC; and for an open-drain output, the
# maker's statement that it is one, which clears it on a gated net (it only pulls low). Set below the list.
# `vcc_path` (round 6 eleventh pass, R4T-D65) is the family's own words for an output held above VCC once VCC falls: the
# SN74LVC08A's positive output clamps (SCAS283W 7.3.3), and for it, the SN74LVC32A and the SN74LVC00A an output rated at most
# VCC + 0.5 V with no power-off rating and no Ioff (SCAS283W, SCAS286U and SCAS279U 5.1), a bound by the falling supply with
# no current stated. The single and dual gates, the 74LVC1G17 and the SN74LVC07A rate their outputs to 6.5 V in the power-off
# state (or whatever VCC is) and state Ioff, which bounds what an input or output passes with VCC at 0 V: for those the held
# sheets decide that no output feeds VCC beyond that bound, and they carry no `vcc_path`.
_LOGIC_ROWS = {
    "74LVC08 quad AND": dict(in_clamp="SCAS283W 7.3.3 Clamp Diodes (page 11): 'The inputs to this device have negative clamping "
                                      "diodes', and 5.1 (page 5) rates the input voltage to 6.5 V with no condition on VCC"),
    "74LVC00 quad NAND": dict(in_clamp="SCAS279U 7.3.3 Clamp Diodes (page 9): 'The inputs and outputs to this device have "
                                       "negative clamping diodes'"),
    "74LVC1G07 open-drain buffer": dict(od_words="SCES296AG, page 1: 'SN74LVC1G07 Single Buffer/Driver With Open-Drain Output' "
                                                 "and 'The output of the SN74LVC1G07 device is open drain'"),
    "74LVC1G06 open-drain inverter": dict(od_words="SCES295AB, page 1: 'The output of the SN74LVC1G06 device is open-drain'"),
    "74LVC2G07 dual open-drain buffer": dict(od_words="SCES308L, page 1: 'SN74LVC2G07 Dual Buffer and Driver With Open-Drain "
                                                      "Outputs' and 'SN74LVC2G07 device is open drain'"),
    "74LVC07 hex open-drain buffer": dict(od_words="SCAS595W, page 1: 'SN74LVC07A Hex Buffer and Driver With Open-Drain "
                                                   "Outputs'"),
}
for _fam in LOGIC:
    _fam.update(_LOGIC_ROWS.get(_fam["name"]) or {})
# The level a gate's output is FORCED to by one input at `lvl`, whatever its other inputs do; None when that
# input alone decides nothing (an AND with a high input follows its other inputs).
# An open-drain output only ever pulls LOW; high is released to whatever pulls it up, which forces nothing.
FORCE = {"AND": {0: 0}, "OR": {1: 1}, "NAND": {0: 1}, "NOR": {1: 0}, "INV": {0: 1, 1: 0}, "BUF": {0: 0, 1: 1},
         "BUF_OD": {0: 0}, "INV_OD": {1: 0}}
# AN OPEN-DRAIN OUTPUT EMCON RELEASES (round 6 second pass, 26 September 2026). Board D's author made SA_PTT_n an open-drain
# 74LVC1G06 (U13) with a divider from +5V_SA holding it at receive: under EMCON, KEY is low and U13 RELEASES the pin,
# so the level is set by the passive pulls, not forced by a gate. The walk used to stop there and call it "EMCON does not
# reach it", a false FAIL. Now the input level that releases each open-drain kind is known, the released net is given
# the level its pulls set at their nominal values (_released_level) with the hop kind "OD_REL", and whether the pulls
# really hold it there, against every pin's current (the released output's own off-state current included, which the
# LVC1G06 and LVC1G07 sheets state only for VCC 0), at its reader's threshold, is judged by own_supply()'s "released"
# state. A released net that nothing pulls, or whose divider sits between VIL_LOW and VIH_HIGH, is not reached.
RELEASE = {"BUF_OD": 1, "INV_OD": 0}
# The elements that can only ever pull a net LOW: an open-drain output, and an N-channel FET with its source on
# ground and its gate driven. A push-pull logic output and a level shifter are not among them: the first drives
# high, and the second passes whatever its other side drives (review fix-up of round 4, 26 September 2026).
OPEN_DRAIN = ("BUF_OD", "INV_OD", "SW_GND")

SWITCHES = [
    dict(name="TPS22810 load switch (WSON)", value=r"TPS22810", fp=r"WSON|SON-6", en="5", out=["1"], sw=[], vin=["6"],
         cite="TI TPS22810, SLVSDH0C (January 2018), Pin Functions, WSON: EN/UVLO 5 'Active high switch control "
              "input', VOUT 1 'Switch output', VIN 6 'Switch input'",
         en_off=1.08, en_leak=0.1e-6,
         off_cite="SLVSDH0C 7.5: VENF 1.08 V minimum, 'A voltage V(EN/UVLO) < V(ENF) on this pin turns off the internal "
                  "FET' (8.3); IEN/UVLO 0.1 uA maximum, -40 to +105 C",
         reverse=None),
    dict(name="TPS22810 load switch (SOT-23)", value=r"TPS22810", fp=r"SOT-23-6", en="3", out=["6"], sw=[], vin=["1"],
         cite="TI TPS22810, SLVSDH0C (January 2018), Pin Functions, SOT23: EN/UVLO 3, VOUT 6, VIN 1",
         en_off=1.08, en_leak=0.1e-6, off_cite="SLVSDH0C 7.5: VENF 1.08 V minimum; IEN/UVLO 0.1 uA maximum, -40 to +105 C",
         reverse=None),
    dict(name="TPS25963x eFuse", value=r"TPS25963", fp=r"SOIC-8|SO-8", en="3", out=["5"], sw=[], vin=["4"],
         cite="TI TPS25963x, SLVSET8A (August 2019), Pin Functions: EN/UVLO 3 'Active High Enable for the Device', "
              "OUT 5 'Power Output', IN 4 'Power Input'",
         en_off=1.08, en_leak=0.1e-6,
         off_cite="SLVSET8A 7.5: VUVLO(F) 1.08 V minimum, 'Whenever the voltage at the EN/UVLO pin falls below a threshold "
                  "VUVLO(F), the device turns OFF the FET'; IENLKG +-0.1 uA, -40 to +125 C junction"),
    dict(name="LM5176 buck-boost controller", value=r"LM5176", fp=r"HTSSOP-28", en="1", out=["12"], sw=[], vin=["2"],
         cite="TI LM5176, SNVSAI1D (August 2021), Pin Functions, HTSSOP: EN/UVLO 1 ('For EN/UVLO < 0.4 V, the "
              "LM5176 is in a low current shutdown mode'), VOSNS 12 'VOUT sense input. Connect to the power stage "
              "output rail', VIN 2 'The input supply pin to the IC'",
         # THE CURRENT AT THE THRESHOLD FROM ABOVE (round 6 second pass, review minor 1): an enable that was ON when its
         # gate died is dragged down through VEN(OP) while the part still counts as operating, and SNVSAI1D sources
         # dIHYS(OP) out of the pin then ON TOP OF IEN(STBY), which is how its UVLO hysteresis works (7.3.3, Equation 2:
         # VHYS(UV) = dIHYS(OP) x RUV2). So the bound is 3 uA + 4.25 uA
         en_off=1.17, en_leak=7.25e-6,
         off_cite="SNVSAI1D 6.5 and 7.3.3: VEN(OP) 1.17 V minimum, below which 'the PWM controller is disabled'; out of the "
                  "pin, IEN(STBY) 3 uA maximum in standby (VEN/UVLO 1.1 V) plus dIHYS(OP) 4.25 uA maximum once EN/UVLO "
                  "exceeds the operating threshold (VEN/UVLO 1.5 V), 7.25 uA at the threshold from above, -40 to +125 C "
                  "junction"),
    dict(name="AP64500 buck", value=r"AP64500", fp=r"SOIC-8|SO-8", en="3", out=[], sw=["8"], vin=["2"],
         cite="Diodes AP64500, DS41979 Rev. 5-2, Pin Descriptions: EN 3 'Drive EN high to turn on the regulator and "
              "low to turn it off', SW 8 'the switching node that supplies power to the output', VIN 2 'Power Input'",
         # NOT BOUNDED FROM ABOVE (round 6 second pass, review minor 1): the sheet's IEN row gives 1 to 2 uA at VEN 1 V
         # (off) and 5.5 uA TYPICAL, no maximum, at VEN 1.5 V (on). An enable dragged down from ON meets the second
         # figure at the threshold, so the current is not bounded (R4T-D29) and a hold of it is UNDECIDED
         en_off=1.03, en_leak=None,
         off_cite="DS41979 Rev. 5-2, Electrical Characteristics, -40 to +85 C: VEN_L 1.03 V minimum; IEN 1 to 2 uA at VEN "
                  "1 V and 5.5 uA typical with no maximum at VEN 1.5 V, out of the pin ('Connect to VIN or leave floating "
                  "for automatic startup')"),
]
OFF_LEVEL = 0      # every enable in SWITCHES is active high
# A SWITCH'S OUTPUT HELD ABOVE ITS INPUT (round 6 eleventh pass, R4T-D65, the review of the tenth pass, minor L1: "consider
# naming logic parts and load switches on an own-output net explicitly"; taken by the session under the owner's standing rule
# of 26 Sep 2026). `reverse` is the maker's words for it: the TPS22810's body diode (SLVSDH0C 10.4), and the TPS2596's and
# the AP64500's output rated at most their input plus 0.3 V (SLVSET8A 7.1; DS41979 Absolute Maximum Ratings), a bound by the
# falling supply with no current stated. The LM5176 has none: its power path is its external FETs, which the walks read as
# transistor channels, and its sense pins take up to 60 V whatever VIN is (SNVSAI1D 6.1, page 5).
_TPS22810_REVERSE = ("SLVSDH0C 10.4 Output Capacitor (page 18): 'Due to the integrated body diode in the NMOS switch, a CIN "
                     "greater than CL is highly recommended. A CL greater than CIN can cause VOUT to exceed VIN when the system "
                     "supply is removed. This can result in current flow through the body diode from VOUT to VIN'")
_REVERSE = {r"TPS22810": _TPS22810_REVERSE,
            r"TPS25963": "SLVSET8A 7.1 Absolute Maximum Ratings (page 5): VOUT at most 'min (21, VIN + 0.3)' V, so an OUT held "
                         "above IN once IN falls with the rail stands above that rating, and no held page says what the part "
                         "then passes from OUT to IN",
            r"AP64500": "DS41979 Rev. 5-2 Absolute Maximum Ratings (page 5 of 26): VSW at most 'VIN + 0.3 (DC)' V, so a switch "
                        "node held above VIN once VIN falls with the rail (its output held up through the inductor) stands "
                        "above that rating, and no held page says what the part then passes into VIN"}
for _sw in SWITCHES:
    _sw["reverse"] = _REVERSE.get(_sw["value"])
# THE ENABLE PIN ON A GATED NET IS READ BY ITS MAKER'S WORDS (round 6 twelfth pass, R4T-D71; the review of the eleventh pass,
# blocking 2; taken by the session under the owner's standing rule of 26 Sep 2026). `en_clear` is the maker's statement that
# the enable is an input with a leakage only, which clears it (its words carried into the PASS); `en_source` the maker's
# statement of a current sourced OUT of the pin, which leaves it UNDECIDED unless `en_from_vin` says where that source runs
# from and that supply falls with the net. The eleventh pass read every enable as a silent load there, and _net_sources()
# skipped it outright.
_EN_ROWS = {
    r"TPS22810": dict(en_clear="SLVSDH0C 7.5 Electrical Characteristics (page 5): IEN/UVLO 'EN/UVLO pin input leakage', 0.1 uA "
                               "maximum (VIN = 18 V, -40 to +105 C), and Pin Functions: EN/UVLO 'Active high switch control "
                               "input' (I); no pull-up and no current source is stated at the pin"),
    r"TPS25963": dict(en_clear="SLVSET8A 7.5 Electrical Characteristics (page 7): IENLKG 'EN leakage current', -0.1 to 0.1 uA, "
                               "and Pin Functions (page 4): EN/UVLO 'Analog Input'; no pull-up and no current source is stated "
                               "at the pin"),
    r"LM5176": dict(en_source="SNVSAI1D 7.3.3 Enable/UVLO (page 15): 'A pullup current IEN(STBY) is sourced out of the EN/UVLO "
                              "pin in standby mode' and 'A hysteresis current dIHYS(OP) is sourced out of the EN/UVLO pin when "
                              "the EN/UVLO input exceeds the operating threshold'; the bias it runs from may come from VIN, from "
                              "BIAS ('Optional input to the VCC bias regulator') or from VCC ('Output of the VCC bias regulator') "
                              "held from outside (Pin Functions), so no one supply falling with the net takes it down"),
    r"AP64500": dict(en_source="DS41979 Rev. 5-2, 3 Enable (page 11): 'An internal 1.5uA pullup current source connected from "
                               "the internal LDO-regulated VCC to the EN pin', and 5 Adjusting Undervoltage Lockout (page 12): "
                               "'A 4uA hysteresis pullup current source on the EN pin'",
                     en_from_vin="Pin Descriptions (page 3): VIN 'supplies the power to the IC as well as the step-down "
                                 "converter power MOSFETs', so the internal VCC those sources run from is made from VIN"),
}
for _sw in SWITCHES:
    _sw.update(_EN_ROWS.get(_sw["value"]) or {})


def logic_of(nl, ref):
    c = nl["comps"].get(ref) or {}
    for fam in LOGIC:
        if re.search(fam["value"], c.get("value", ""), re.I):
            if not re.search(fam["fp"], c.get("fp", "") or "", re.I): return dict(fam, wrong_land=True)
            return _wired(nl, ref, fam) if fam.get("configs") else fam
    return None


def _wired(nl, ref, fam):
    """A configurable family (`configs`) as this part is wired (EQ-18, stream w3t, 27 September 2026): the family with the gates
    of the first configuration whose `low` pins sit on the same net as the part's own GND pin (`gnd`), that net being a ground;
    otherwise the family with no gates and `unwired` saying why, which every reader of LOGIC takes as it takes a wrong land
    (_unmapped): no pin of the part is walked through or cleared."""
    g = nl["pin"].get((ref, fam["gnd"]), "")
    for cfg in fam["configs"]:
        if is_ground(g) and all(nl["pin"].get((ref, p), "") == g for p in cfg["low"]):
            return dict(fam, gates=cfg["gates"], config=cfg["words"])
    at = "; ".join("pin %s on %s" % (p, nl["pin"].get((ref, p)) or "no net")
                   for p in sorted({p for cfg in fam["configs"] for p in cfg["low"]}, key=lambda x: (len(x), x)))
    return dict(fam, gates=[], unwired="a %s whose function is set by its wiring, and this one is wired %s with its GND pin %s "
                "on %s, which is not a configuration its row holds (the row reads only %s), so which pin decides its output "
                "is not known" % (fam["name"], at, fam["gnd"], g or "no net",
                                  "; ".join(c["words"].split(";")[0] for c in fam["configs"])))


def _unmapped(fam):
    """Why no pin of a logic part is read through its family's map, or None when the map and the gates hold for it: a land
    the map is not for (`wrong_land`), or a configurable part wired in a configuration its row does not hold (`unwired`)."""
    if not fam: return None
    if fam.get("wrong_land"):
        return "a %s on a land its pin map is not for, so which pin is an output is not known" % fam["name"]
    return fam.get("unwired")


def switch_of(nl, ref):
    c = nl["comps"].get(ref) or {}
    for sw in SWITCHES:
        if re.search(sw["value"], c.get("value", ""), re.I) and re.search(sw["fp"], c.get("fp", "") or "", re.I):
            return sw
    return None


def fet_of(nl, ref):
    """("N" | "P", {G, S, D: pin}) for a FET whose netlist names its pins G/S/D, else None."""
    c = nl["comps"].get(ref) or {}
    if not ref.startswith("Q"): return None
    txt = c.get("lib", "") + " " + c.get("value", "")
    kind = "P" if re.search(r"PMOS|BSS84|P-FET|P-channel|Q_PMOS", txt, re.I) else \
           "N" if re.search(r"NMOS|2N7002|BSS138|N-FET|N-channel|Q_NMOS", txt, re.I) else None
    if not kind: return None
    m = {nl["func"].get((ref, p), ""): p for p in pins_of(nl, ref)}
    return (kind, {k: m[k] for k in ("G", "S", "D")}) if all(k in m for k in ("G", "S", "D")) else None


def nfet_pins(nl, ref):
    """{G, S, D: pin} for an N-channel FET whose netlist names its pins G/S/D, else None."""
    f = fet_of(nl, ref)
    return f[1] if f and f[0] == "N" else None


# ---------------------------------------------------------------- what a part runs from, and what a supply is (R4T-D41)
# A PART'S SUPPLY IS READ FROM ITS PIN MAP, NOT FROM A '+' IN A NET'S NAME (round 6 third pass, 26 September 2026; the
# review of round 6's second pass, blocking 1). The per-reader bound (_fs_bound) grouped the readers of a line by the
# '+' rails on their pins. A gate or a switch whose supply pin sits on a net named VBAT, VCC_X, 3V3_DEV or SAU_3V3 had
# none, fell into an empty domain whose run reused the network in which it was only "either", and was never judged:
# with no pull-down at all such a line read PASS, where round 6's first pass had read FAIL. And a supply whose name has
# no '+' was walked as a plain signal node, so a pull-up to it lifted nothing and a 0 Ohm link from it onto a forced
# net was followed as a conductor. Now:
#   * a logic part runs from its VCC pin (`vcc` in LOGIC) and a switch from its input pins (`vin` in SWITCHES, never
#     its output, which is what EMCON switches: the review's minor on the switch domain), as their makers' pin tables
#     give them and whatever the nets are called; any other part from its '+' rails (_supply_nets);
#   * a part none of whose supply is on the netlist is its own domain (_SELF): the bound solves it in a run of its own
#     with only itself taken powered, so every reader is judged;
#   * a net is a SUPPLY when it is a '+' rail, when its name says so (_supply_name) and carries no control word
#     (_CONTROL_WORD), or when a logic VCC pin or a switch input sits on it (_pinmap_supplies). In the fail-safe and
#     own-supply networks a supply is never a signal node: only a '+' rail's name is read for a voltage (rail_volts), so
#     a live supply whose name states none, met through a resistor, a bead, a diode or a FET channel, leaves the state
#     UNDECIDED (and a reader running from one is not judged at the LVC VIL, R4T-D39; it still FAILS at its family's
#     vil_ceiling, R4T-D45); a dead one is neither a pull nor a source. In the census a supply known only by its NAME is
#     judged as a pull AND walked for its drivers (R4T-D42, corrected in the fourth pass: the third pass stopped there).
_SELF = "#self:"


def _pin_nets(nl, ref, pins):
    return sorted({n for n in (nl["pin"].get((ref, p), "") for p in pins) if not _dead(n) and not is_ground(n)})


def _supply_nets(nl, ref):
    """The nets part `ref` runs from: a switch's input pins, a logic part's VCC pin, else its '+' rails (R4T-D41)."""
    sw = switch_of(nl, ref)
    if sw and sw.get("vin"): return _pin_nets(nl, ref, sw["vin"])
    fam = logic_of(nl, ref)
    # an `unwired` configurable part keeps its VCC pin: its maker's pin table holds whatever its inputs are wired to (EQ-18)
    if fam and not fam.get("wrong_land") and fam.get("vcc"): return _pin_nets(nl, ref, fam["vcc"])
    return _part_rails(nl, ref)


def _pinmap_supplies(nl):
    """{net} on a logic part's VCC pin or a switch's input pin, whatever its name (R4T-D41)."""
    out = set()
    for ref in nl["comps"]:
        if not ref.startswith("U"): continue
        sw = switch_of(nl, ref)
        fam = None if sw else logic_of(nl, ref)
        if sw and sw.get("vin"): out |= set(_pin_nets(nl, ref, sw["vin"]))
        elif fam and not fam.get("wrong_land") and fam.get("vcc"): out |= set(_pin_nets(nl, ref, fam["vcc"]))
    return out


# A NAME THAT CARRIES A CONTROL WORD IS A SIGNAL, whatever voltage it also names ("EN_3V3", "PWR_ON_5V", "PG_1V8"): the
# name test is for supplies, and an enable named after the rail it switches is the net EMCON drives. Such a net is still
# a supply when a VCC or VIN pin sits on it.
_CONTROL_WORD = re.compile(r"(^|_)(EN|ENA|ENABLE|ON|OFF|CTRL|CTL|SW|SEL|PG|PGOOD|GOOD|FLT|FAULT|ALERT|INT|DIS|DISABLE|"
                           r"KEY|PTT|RST|RESET|SENSE|SNS|MON)(_|$)", re.I)


def _supply_test(boards):
    """is_supply(k, net) over `boards`, with each board's pin-map supplies computed once per call (R4T-D41).
    is_supply.kind(k, net) says HOW the net is known to be a supply (round 6 fourth pass, R4T-D42), because the census
    and the second-feed check treat the three differently:
      "rail"    a '+' name, the only kind whose name is read for a voltage (rail_volts);
      "pinmap"  a logic part's VCC pin or a switch's input pin sits on it, the maker's pin table says so;
      "name"    its name alone says so (_supply_name, no control word): the net may be a supply, or a signal a firmware
                pin drives, or a switched rail, so the census walks it for what drives it as well as judging the pull;
    or None for a net that is not a supply by any of the three."""
    cache = {}

    def kind(k, n):
        if not n or _dead(n) or is_ground(n): return None
        if is_rail(n): return "rail"
        if k not in cache:
            nl = boards.get(k)
            cache[k] = _pinmap_supplies(nl) if nl is not None else set()
        if n in cache[k]: return "pinmap"
        if _supply_name(n) and not _CONTROL_WORD.search(n): return "name"
        return None

    def is_supply(k, n):
        return kind(k, n) is not None
    is_supply.kind = kind
    return is_supply


# ---------------------------------------------------------------- the walk
def reach(nl, only=None):
    """{net: dict(level, path, driver, kinds, nets)} for every net EMCON forces: the level, the readable path of
    parts it took, the (ref, pin) that forces it, the kind of each hop and the nets from the asserted line to it;
    plus a list of the parts the walk stopped at because no pin map is known for them.
    only: walk from that one asserted line (board A's round 8 author's draft, applied at integration on 27 September
    2026). The walk keeps ONE path per net, the first it reaches, so a gate both lines force (board A's U35 and U37 since
    round 8: TX_INHIBIT_n AND EMCON_HW) inherited the answer of whichever line the queue took first, EMCON_HW, and a rail
    forced LOW by either line read FAIL on that line's L1 while the other line, which holds, was never asked. judge()
    now also asks each line alone and takes the best answer an option has on any one line."""
    got, stopped = {}, []
    todo = []
    is_supply = _supply_test({"_": nl})           # a supply is not a net EMCON forces, whatever its name (R4T-D41)
    for s in (SOURCES if only is None else (only,)):
        if s in nl["nets"]:
            got[s] = dict(level=0, path=[s + " (asserted LOW)"], driver=None, kinds=[], nets=[s]); todo.append(s)
    while todo:
        n = todo.pop(0)
        cur = got[n]
        lvl = cur["level"]

        def push(n2, l2, hop, drv, kind):
            if not n2 or is_rail(n2) or is_ground(n2) or n2.startswith("unconnected-") or is_supply("_", n2): return
            if n2 in got: return
            got[n2] = dict(level=l2, path=cur["path"] + [hop], driver=drv, kinds=cur["kinds"] + [kind],
                           nets=cur["nets"] + [n2])
            todo.append(n2)

        for ref, pin, _f in nl["nets"].get(n, []):
            fam = logic_of(nl, ref)
            if fam is not None:
                if fam.get("wrong_land"):
                    stopped.append("%s (%s): its land %s is not the package %s's pin map is for"
                                   % (ref, value(nl, ref)[:40], nl["comps"][ref].get("fp"), fam["name"])); continue
                if fam.get("unwired"):
                    stopped.append("%s (%s): %s" % (ref, value(nl, ref)[:40], fam["unwired"])); continue
                for ins, outp, kind in fam["gates"]:
                    if pin in ins:
                        l2 = FORCE[kind].get(lvl)
                        if l2 is not None:
                            push(nl["pin"].get((ref, outp)), l2, "%s %s %s->%s" % (ref, kind, pin, outp), (ref, outp), kind)
                        elif RELEASE.get(kind) == lvl:
                            on = nl["pin"].get((ref, outp))
                            l3, why = _released_level(nl, on)
                            if l3 is not None:
                                push(on, l3, "%s %s %s->%s released, %s" % (ref, kind, pin, outp, why), (ref, outp), "OD_REL")
                continue
            q = nfet_pins(nl, ref)
            if q is not None:
                g_net, s_net = nl["pin"].get((ref, q["G"]), ""), nl["pin"].get((ref, q["S"]), "")
                if pin in (q["D"], q["S"]) and is_rail(g_net) and lvl == 0:
                    other = q["S"] if pin == q["D"] else q["D"]
                    push(nl["pin"].get((ref, other)), 0, "%s level shifter %s->%s" % (ref, pin, other), (ref, other), "LS")
                elif pin == q["G"] and is_ground(s_net) and lvl == 1:
                    push(nl["pin"].get((ref, q["D"])), 0, "%s switch to ground G->D" % ref, (ref, q["D"]), "SW_GND")
                elif pin == q["G"] and is_ground(s_net) and lvl == 0:
                    # A SWITCH TO GROUND EMCON HOLDS OFF RELEASES ITS DRAIN (round 6 fourth pass, R4T-D46): board B's Q11
                    # makes EMCON_ON = NOT EMCON_HW with R513 10 kOhm to +3V3_DEV since main 458b2873 (S-01). Like an
                    # open-drain output EMCON releases (R4T-D38), the drain takes the level its pulls set, and whether
                    # they hold it there, against the FET's off-state current, is own_supply()'s released state
                    on = nl["pin"].get((ref, q["D"]))
                    l3, why = _released_level(nl, on)
                    if l3 is not None:
                        push(on, l3, "%s switch to ground held off G->D released, %s" % (ref, why), (ref, q["D"]), "OD_REL")
                continue
            if re.match(r"^R\d", ref):
                ps = pins_of(nl, ref)
                if len(ps) == 2:
                    other = ps[1] if ps[0] == pin else ps[0]
                    push(nl["pin"].get((ref, other)), lvl, "%s series" % ref, (ref, other), "R")
                continue
            if re.match(r"^(C|TP|J|#|D|LED|FB|L)\w*", ref): continue
            sw = switch_of(nl, ref)
            if sw and pin == sw["en"]: continue          # an enable is where a power gate ends, not where it stopped
            if (ref, pin) != cur["driver"]:
                stopped.append("%s (%s) pin %s" % (ref, value(nl, ref)[:48], pin))
    return got, stopped


def _released_level(nl, net):
    """(level, why) that the passive pulls on a net an open-drain output has released set it to, at their nominal values;
    (None, why) when nothing pulls it or the divider sits between VIL_LOW and VIH_HIGH. Whether they HOLD it there against
    the pins' currents at the reader's threshold is own_supply()'s "released" state.
    A PULL TO A SUPPLY WHOSE NAME STATES NO VOLTAGE (round 6 third pass, the review of round 6's second pass, minor 7):
    the first version skipped it, so a divider from SAU_3V3 read "nothing pulls it" (a false FAIL), and a pull-up to
    VCC_X beside a pull-down read 0 V, a released enable EMCON would then have counted as forced OFF while VCC_X holds it
    ON. Now the level is not known (None, and the path is not reached: EMCON does not reach the pin, which can refuse a
    board that works and cannot pass one that does not); a '+' rail's name makes it readable."""
    g = vs = 0.0
    parts = []
    is_supply = _supply_test({"_": nl})
    for ref, pin, _f in nl["nets"].get(net or "", []):
        ps = pins_of(nl, ref)
        if not (re.match(r"^R\d", ref) and len(ps) == 2): continue
        m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
        v = 0.0 if is_ground(m2) else (rail_volts(m2) if is_supply("_", m2) else None)
        if v is None and is_supply("_", m2):
            return None, "pulled to %s through %s, a supply whose name states no voltage" % (m2, ref)
        ohm = _ohms(value(nl, ref))
        if v is None or not ohm: continue
        g += 1.0 / ohm; vs += v / ohm; parts.append("%s %s to %s" % (ref, value(nl, ref)[:10], m2))
    if not g: return None, "nothing pulls it"
    vth = vs / g
    return (1 if vth >= VIH_HIGH else 0 if vth < VIL_LOW else None), "held at %.2f V by %s" % (vth, ", ".join(parts))


# ---------------------------------------------------------------- who else can drive a gate net
# The four board-to-board ribbons: pin n on one end is pin n on the other, which check_contracts proves (contracts
# 1, 7, 7b and 8: "map identical"). A conductor followed across one of them continues on the other board's netlist.
MATES = [
    dict(a=("A", "J_AB1"), b=("B", "J_AB1"), why="the A to B ribbon, map identical (check_contracts contract 7)"),
    dict(a=("A", "J_AB2"), b=("B", "J_AB2"), why="the wall-port ribbon, map identical (check_contracts contract 7b)"),
    dict(a=("B", "J_PANEL"), b=("C", "J_PANEL"), why="the panel ribbon, map identical (check_contracts contract 1)"),
    dict(a=("A", "J_MEZZ1"), b=("D", "J_HARN1"), why="the mezzanine harness, map identical (check_contracts contract 8)"),
]
# A pin at the far end of a connector that no mate continues (a module plugged into the board), which its maker's
# document calls an input.
PIN_READERS = [
    dict(board="B", ref="J_M2C2", pin="8",
         why="the RM520N-GL's W_DISABLE1#: Quectel RM520N-GL Hardware Design v1.0 (v2/vendor/quectel), pin table: "
             "'8 W_DISABLE1# DI, PU ... 1.8/3.3 V ... Internally pulled up to 1.8 V with a 100 kOhm resistor'",
         pull_up=(1.8, 100e3)),        # the pull-up the same row states; fail_safe() counts it as a source
]
# Protection parts on a gate net: they conduct only outside the rails or above their breakdown, so they cannot drive
# a logic net that sits between its rails. ST USBLC6-2 "Very low capacitance ESD protection", I/O pins 1, 3, 4 and 6
# steered to VBUS and GND (v2/vendor/st/st-usblc6-2-esd-protection.pdf); Nexperia PESD5V0S1BA "Bidirectional ESD
# protection diode" (v2/vendor/nexperia/nexperia-pesd5v0s1ba.pdf); the SMBJ and SMCJ suppressors (kisch.tvs_direction).
PROTECTION = re.compile(r"^(USBLC6|PESD\d|SMBJ|SMCJ)", re.I)
# A PROTECTION PART ON A GATED RAIL IS READ BY ITS MAKER'S TOPOLOGY (round 6 twelfth pass, R4T-D71; the review of the eleventh
# pass, blocking 1: board B's U33 sat on +5V_LIME as a silent load while the held sheet joins its I/O to VBUS; taken by the
# session under the owner's standing rule of 26 Sep 2026). The USBLC6-2's VBUS is a load only while nothing holds any of its
# I/O pins up: its maker draws each I/O joined to VBUS by a diode (Dhigh) and to GND by another (Dlow), with a Zener from GND
# to VBUS, and no other element at VBUS. Any other pin of it on a gated net is UNDECIDED. Pins by the sheet's SOT-23-6 pinout.
PROTECTION_ROWS = [
    dict(name="USBLC6-2 ESD protection", value=r"^USBLC6-2", fp=r"SOT-23-6", io=("1", "3", "4", "6"), vbus=("5",), gnd=("2",),
         topology="ST DS4260 Rev 7 (v2/vendor/st/st-usblc6-2-esd-protection.pdf), page 1 pinout: I/O1 1 and 6, GND 2, I/O2 3 "
                  "and 4, VBUS 5; 2.1 Surge protection (page 10): 'optimized to perform surge protection based on the rail to "
                  "rail topology', 'VCL+ = VTRANSIL + VF for positive surges'; 2.6 PSpice model, Figure 15 (page 10): each I/O "
                  "joined to VBUS by a diode (Dhigh) and to GND by another (Dlow), and a Zener (Dzener) between GND and VBUS, "
                  "which is all the model draws at VBUS"),
]


def protection_of(nl, ref):
    """The PROTECTION_ROWS row for a part, by its value and its land, else None (R4T-D71)."""
    c = nl["comps"].get(ref) or {}
    return next((r for r in PROTECTION_ROWS if re.search(r["value"], c.get("value", ""), re.I)
                 and re.search(r["fp"], c.get("fp", "") or "", re.I)), None)
# A pin whose direction firmware sets, declared a reader because a series resistor makes the gate's own driver win
# whatever firmware does: dict(board, ref, pin, through=<resistor ref>, r_min=<ohms>, why=<the arithmetic>). The
# census accepts it only when the conductor reaches the pin through that resistor at that value or more. No board
# carries one today; it is the table the remedy for board B's STM32 and board C's RP2040 taps goes into.
READER_TAPS = []
# The parts whose pins firmware can turn into outputs. A match FAILS a path; an unknown active part only leaves it
# UNDECIDED, because nothing says it can drive.
# A PART IS ONE OF THESE BY WHAT IT IS, NOT BY WHAT ITS VALUE MENTIONS (round 6 seventh pass, R4T-D52, closing R4T-F22;
# taken by the session under the owner's standing rule of 26 Sep 2026). The pattern used to be searched anywhere in the
# value and the library name, so every part whose value mentioned the Compute Module ("up = CM5 lane", "ports 1-3 the CM5
# slots") or the panel controller ("the RP2040 panel controller's USB") was read as that part. Now software_io() asks the
# part itself: its library symbol's name begins with one of these, or its value does (after at most a maker's name), or
# the value has the form of a receptacle that carries the Compute Module's own pins ("(CM5 pins 1-100"). Board B's switch,
# PCIe switches and USB hubs stay in by their own part numbers, each on its maker's words for a pin software sets:
# KSZ9897 (Microchip DS00002330D, v2/vendor/microchip/microchip-ksz9897-datasheet.pdf, 5.1.2.6 LED Override Register:
# "each LEDx_0 and LEDx_1 pin will function as an LED or General Purpose Output (GPO) ... controlled via the LED Output
# Register"); PI7C9X2G404SL (Diodes datasheet revision 5, July 2025, v2/vendor/diodes/diodes-pi7c9x2g404sl.pdf, pin
# description GPIO[7:0]: "programmed as either input-only or bi-directional pins by writing the GPIO output enable control
# register"); TUSB8041 (TI SLLSEE4E, v2/vendor/ti/ti-tusb8041.pdf, PWRCTL1 to PWRCTL4 "Power On Control for Downstream
# Power", and "An individually port power controlled hub switches power on or off to each downstream port as requested
# by the USB host").
SOFTWARE_IO = re.compile(r"STM32|RP2040|PCA95\d\d|PCAL\d{4}|TCA\d{4}|MCP23\d\d|ESP32|ATmega|ATSAM|nRF5\d|SC16IS\d+|"
                         r"CP210\d|FT2\d\d|CH34\d|KSZ9897|PI7C9X2G404|TUSB8041|"
                         r"CM5\d{3}|CM5\s+(?:socket|receptacle|module|connector)\b|Compute Module 5\b", re.I)
SOFTWARE_IO_LIB = re.compile(r"(%s|CM5[AB]?$)" % SOFTWARE_IO.pattern, re.I)   # board B's receptacle symbols CM5A, CM5B
CM5_RECEPTACLE = re.compile(r"\(CM5 pins \d", re.I)
# the makers' names a value may begin with before the part number ("Microchip KSZ9897RTXI", "Diodes PI7C9X2G404SL")
_MAKER = r"(?:(?:Raspberry Pi|Microchip|Diodes|TI|Texas Instruments|ST|STMicroelectronics|NXP|Silicon Labs|SiLabs|" \
         r"Espressif|WCH|FTDI|Nordic|Atmel)\s+)?"


def _is_part(nl, ref, ident, lib_ident=None, receptacle=None):
    """True when the part ITSELF is `ident` (R4T-D52): its library symbol's name begins with `lib_ident` (or `ident`),
    or its value begins with `ident` after at most a maker's name, or its value has the `receptacle` form. A value that
    only mentions a part names something else."""
    c = nl["comps"].get(ref) or {}
    v, part = (c.get("value") or "").strip(), (c.get("lib") or "").split(":")[-1]
    if re.match(r"(?:%s)" % (lib_ident or ident), part, re.I) or re.match(_MAKER + r"(?:%s)" % ident, v, re.I):
        return True
    return bool(receptacle and re.search(receptacle, v))


def software_io(nl, ref):
    """True for a part whose pins firmware sets, found by the part itself (SOFTWARE_IO, R4T-D52)."""
    return _is_part(nl, ref, SOFTWARE_IO.pattern, SOFTWARE_IO_LIB.pattern, CM5_RECEPTACLE)


# A PART THAT ONLY MENTIONS A FIRMWARE FAMILY IS NEVER PASSED WITHOUT A WORD (round 6 eighth pass, R4T-D53, the review of the
# seventh pass, blocking 1; taken by the session under the owner's standing rule of 26 Sep 2026). R4T-D52 anchored
# software_io() to the start of the value or of the library symbol's name, which is right for which ROWS are loads
# (fw_family) and for which parts a path FAILS on. But _second_sources() reads no pin of a part outside the classes it
# knows (R4T-F23), so an 'I/O supervisor STM32H743VIT6' on a custom symbol (meshsat_ic:U41), a 'Panel controller RP2040',
# a 'USB-UART bridge CP2102N', an 'I2C expander PCA9555PW', 'Slot S1 compute: CM5108032', a 'WeAct STM32H743VIT6 core
# board' or a 'Seeed XIAO ESP32S3' sat on a gated rail as a silent load by any pin, VCAP, VREG_VOUT, a GPIO and pin 84
# CM5_3.3V among them, where the sixth pass's file FAILED them (R4T-F26). The family is still anchored; what changed is
# that a part whose value or symbol MENTIONS one (FW_MENTION searched anywhere, below) and that software_io() does not read
# as one is UNDECIDED wherever the walks meet an active pin of it (_second_sources() on the conductor and behind a
# resistor, census(), _network()), and the result names the family mentioned and says the part is not read as one. Board
# B's J_PANEL and its PCIe coupling capacitors (C151 to C352) still never get here: every walk handles a connector and
# skips a capacitor by its reference first. A level shifter 'for the RP2040' is named the same way.
# THE MENTION IS SEARCHED WITH THE SIXTH PASS'S WORDS FOR THE MODULE (round 6 ninth pass, R4T-D56, the review of the eighth
# pass, blocking 1; taken by the session under the owner's standing rule of 26 Sep 2026). The eighth pass searched the
# mention with SOFTWARE_IO, which R4T-D52 had narrowed for the Compute Module to 'CM5' plus three digits, 'CM5' before
# socket, receptacle, module or connector, and 'Compute Module 5', while its own comment said the sixth pass's search was
# kept. The sixth pass's pattern ended in '\bCM5\d*|Compute Module' (4836c42c, line 553), so 'Raspberry Pi CM5 8GB/64GB
# wireless' (the V2 device set's own words for the part), a bare 'CM5', 'Raspberry Pi Compute Module (8GB)' and 'Slot S1
# compute: Raspberry Pi CM5 8GB' with pin 84 CM5_3.3V (a 600 mA regulator output, CM5 datasheet 3.4) or a GPIO on a gated
# rail read FAIL on the sixth pass's file and PASS, silently, on the seventh and eighth. FW_MENTION is SOFTWARE_IO OR those
# two alternatives. It is used only for the naming; software_io() and fw_family() stay anchored as R4T-D52 left them, so
# a part is still READ as a firmware part only by its own symbol or part number. It searches the whole library string,
# the nickname before the colon included (limit (5) of the header's list of what the walk does not read: a false
# UNDECIDED, seen).
# A NAME JOINED BY AN UNDERSCORE IS SEARCHED TOO (round 6 eleventh pass, R4T-D66, the review of the tenth pass, its ninth-review
# minor not carried; taken by the session under the owner's standing rule of 26 Sep 2026). '\bCM5' needs a word boundary
# before the C, and an underscore is a word character, so the value 'RPi_CM5_8GB' and the library 'meshsat:RPi_CM5' with pin 84
# CM5_3.3V on a gated rail read PASS in silence on every earlier file (probes B1-10 and B1-11), while the module's datasheet
# 3.4 makes pin 84 a regulator output. The module's short name is now found wherever no letter or digit stands before it.
FW_MENTION = re.compile(r"%s|(?<![A-Za-z0-9])CM5\d*|Compute Module" % SOFTWARE_IO.pattern, re.I)


def fw_mention(nl, ref):
    """The text of a firmware family (FW_MENTION) that part `ref`'s value or library symbol mentions while software_io()
    does not read the part as one of them, else None (R4T-D53; the search pattern since R4T-D56)."""
    if software_io(nl, ref): return None
    c = nl["comps"].get(ref) or {}
    txt = "%s %s" % (c.get("value") or "", c.get("lib") or "")
    m = FW_MENTION.search(txt)
    return (m.group(0) + re.match(r"[\w\-]*", txt[m.end():]).group(0)) if m else None     # the whole part number


def _mention_why(nl, ref, fam):
    """The sentence naming a part that only mentions firmware family `fam` (R4T-D53)."""
    c = nl["comps"].get(ref) or {}
    return ("its value or library symbol mentions %s, a family whose pins firmware sets, and the part is not read as one "
            "(its library symbol %r does not begin with a part number of that family, nor does its value %r after at most a "
            "maker's name), so which of its pins firmware drives, and which are its supply, is not known; a firmware part's "
            "value begins with its part number" % (fam, (c.get("lib") or "").split(":")[-1], (c.get("value") or "")[:40]))


def _mate(k, ref):
    for m in MATES:
        if m["a"] == (k, ref): return m["b"], m["why"]
        if m["b"] == (k, ref): return m["a"], m["why"]
    return None, None


def _ohms(v):
    """Ohms from a resistor value: "10k", "4k7", "100", "0R", "1M", "2m shunt" (second fix-up of round 4, 26
    September 2026: the letter's case is the unit, so "2m" is two milliohms and "1M" one megohm; the first version
    lower-cased it and read board P's 2 mOhm shunt as 2 MOhm)."""
    m = re.match(r"^\s*(\d+(?:\.\d+)?)\s*([RrKkMm]?)(\d*)", v or "")
    if not m: return None
    x = float(m.group(1) + ("." + m.group(3) if m.group(3) else ""))
    return x * {"": 1, "R": 1, "r": 1, "k": 1e3, "K": 1e3, "M": 1e6, "m": 1e-3}[m.group(2)]


def rail_volts(n):
    """The voltage a rail's name states ("+3V3_S1A" 3.3, "+5V_DEV" 5.0, "+13V8_PA" 13.8), 0.0 for a ground, or
    None when the name states none."""
    if is_ground(n): return 0.0
    m = re.match(r"^\+(\d+)V(\d*)", n or "")
    return float(m.group(1) + ("." + m.group(2) if m.group(2) else "")) if m else None


# THE PULL A FORCED NET MAY CARRY (second fix-up of round 4, 26 September 2026). The census took every resistor from
# a gate net to a rail as a harmless pull, whatever its value, so a 0 Ohm link from +3V3 onto an enable EMCON forces
# low read PASS. A pull against the forced level is harmless only while the driver can hold its level against it:
# every logic sheet the walk crosses guarantees VOL at most 0.45 V at 4 mA even at VCC 1.65 V (TI SCES519O and
# SCES296AG, the 74LVC1G34 and 1G07, IOL 4 mA), and at the kit's 3.3 V far more (SCAS283W, the SN74LVC08A: VOL 0.4 V
# at 12 mA with VCC 2.7 V), which stays under the readers' 0.8 V VIL. The pulls against the forced level on one
# conductor (the net and what the census follows from it) are summed and held to 4 mA; a 0 Ohm or unreadable value is
# named.
PULL_MA_MAX = 4.0
# THE LEVEL EVERY GATE ON THE ASSERTED LINES READS AS LOW: VIL 0.8 V. TI SN74LVC08A, SCAS283W, Recommended Operating
# Conditions, VCC 2.7 V to 3.6 V (board A's U26, board B's U19 and U20, v2/vendor/ti); TI SN74LVC1G08, SCES217AA,
# VCC 3 V to 3.6 V (board D's U12). Board C's Schmitt readers are read at their VCC 3 V rows, the only rows their sheets
# state in the band: Diodes 74LVC1G17 VT- 0.80 V minimum (DS35124 Rev. 8-2; U9, U13) and TI SN74LVC1G57 VT- 0.84 V minimum
# (SCES414P 6.5; U14, EQ-18). A line has to stay under it in its fail-safe states (fail_safe() below).
VIL_LOW = 0.8
# A pin whose direction firmware sets is taken at its part's own supply when it drives high, and at this when no rail
# on the part names its voltage.
V_FIRMWARE_HIGH = 3.3
# WHAT A PULL TO A SUPPLY DOES TO A FORCED NET, BY HOW THE SUPPLY IS KNOWN (round 6 fourth pass, R4T-D42; the review of
# the third pass, blocking 1, taken by the session under the owner's standing rule of 26 Sep 2026). The third pass made
# every supply a harmless pull on a net EMCON holds HIGH, whatever it was: a 0 Ohm or 1 kOhm link from SA_PTT_n to
# VCC_SENSOR, GPS_3V3 or SIM1_VCC read PASS, although a sensor rail a GPIO powers, or a modem's SIM supply, sits at 0 V
# whenever firmware turns it off and then keys an active-low PTT. And a supply known only by its name stopped the walk,
# so the firmware pin on it was never met. Now, for a resistor (or a P-channel switch) from the forced net to a supply:
#   * a '+' rail whose name states a voltage v: on a net EMCON holds LOW it is a pull against the level (v / R, summed to
#     PULL_MA_MAX); on a net EMCON holds HIGH it is harmless only when v is at or above V_FIRMWARE_HIGH, the level the
#     census takes a driven-high net at (the level it already takes a pull to ground against); a lower rail is a pull
#     against the level, (V_FIRMWARE_HIGH - v) / R, and a 0 Ohm link or a switch channel to it FAILS. Below the reader's
#     own threshold matters once the driver is gone, which own_supply() and fail_safe() judge at that threshold;
#   * any other supply (a '+' name with no voltage, a pin-map supply, a name-only supply): its voltage is not stated, so
#     a pull to it is UNDECIDED at either level and a 0 Ohm link or a switch channel to it FAILS at either level;
#   * a name-only supply is ALSO walked as a conductor, as the round-6 second pass (e88aa46b) walked it, so a firmware
#     pin on it FAILS the path and an unknown driver leaves it UNDECIDED, named;
#   * a released open-drain net (own_supply()'s released state) still takes its pulls to ground and to a '+' rail that
#     states its voltage as what sets its level; a pull to any other supply is judged as above.
_SUPPLY_WHY = {"rail": "a '+' rail whose name states no voltage", "pinmap": "a supply by its maker's pin table (a logic VCC "
               "or a switch VIN pin sits on it) whose name states no voltage", "name": "a supply by its name only, whose "
               "voltage the name does not state"}


def census(boards, walks, k0, n0, level, allowed, target=None, fet_forced=None, released=False):
    """Everything on the conductor of net `n0` (board `k0`) that could drive it besides `allowed`, the (board, ref,
    pin) triples that are its own drivers. `level` is what EMCON forces the net to; a part that can only pull it
    that way is no threat to it. Returns dict(fail, undecided, boards, absent, reach): two lists of sentences, the
    boards whose parts they name, the boards the conductor enters whose netlists are absent, and the (board, net)
    pairs followed."""
    fail, und, named, absent = [], [], set(), set()
    seen = set()
    todo = [(k0, n0, (), frozenset())]
    # the pulls against the forced level anywhere on the conductor: the gate that forces it sinks all of them, those
    # reached through a level shifter's channel included (a pull behind a series resistor is counted at its full
    # value, which can only overstate what the gate is asked)
    acc = {"ma": 0.0, "pulls": [], "named": False}
    is_supply = _supply_test(boards)            # a '+' rail, a supply-named net, or a VCC or VIN pin's net (R4T-D41)
    while todo:
        k, n, chain, links = todo.pop(0)
        if (k, n) in seen or _dead(n): continue
        seen.add((k, n))
        nl = boards.get(k)
        if nl is None:
            absent.add(k); continue
        got = walks[k][0] if k in walks else {}

        def go(k2, n2, hop, ref):
            if not _dead(n2) and (k2, n2) not in seen:
                todo.append((k2, n2, chain + (hop,), links | {(k, ref)}))

        for ref, pin, fn in nl["nets"].get(n, []):
            if (k, ref, pin) in allowed or (k, ref, pin) == target or (k, ref) in links: continue
            where = "%s %s pin %s (%s) on %s%s" % (k, ref, pin, value(nl, ref)[:40], n,
                                                   (", reached through " + " > ".join(chain)) if chain else "")

            def bad(why): fail.append(where + ": " + why); named.add(k)

            def unk(why): und.append(where + ": " + why); named.add(k)
            if re.match(r"^(#|TP|FID|MH|H\d|C\d)", ref): continue          # flags, test points, capacitors
            if PROTECTION.match(value(nl, ref)): continue                        # a clamp cannot drive a net inside its rails
            if [d for d in PIN_READERS if (d["board"], d["ref"], str(d["pin"])) == (k, ref, pin)]: continue
            g = got.get(n)
            if g and g["driver"] == (ref, pin) and g["level"] == level: continue   # forced by EMCON the same way
            # a declared tap: accepted only behind its resistor
            tap = [t for t in READER_TAPS if (t["board"], t["ref"], str(t["pin"])) == (k, ref, pin)]
            if tap:
                t = tap[0]; r_ok = (k, t["through"]) in links and (_ohms(value(nl, t["through"])) or 0) >= t["r_min"]
                if r_ok: continue
                bad("declared a sense tap behind %s of at least %g ohm, and the conductor reaches it %s"
                    % (t["through"], t["r_min"], "through a smaller one" if (k, t["through"]) in links else "without it"))
                continue
            fam = logic_of(nl, ref)
            if fam is not None:
                if fam.get("wrong_land"):
                    unk("a %s on a land its pin map is not for, so which pin is an output is not known" % fam["name"]); continue
                if fam.get("unwired"):
                    unk(fam["unwired"]); continue
                if any(pin in ins for ins, _o, _k in fam["gates"]): continue          # a logic input only reads
                outs = [(ins, kind) for ins, o, kind in fam["gates"] if o == pin]
                if outs:
                    ins, kind = outs[0]
                    # the panel's buffer is the line's own source: an output on an asserted line whose input sits on
                    # the other asserted line, forced to the same asserted level
                    if n in SOURCES and any(nl["pin"].get((ref, i)) in SOURCES and nl["pin"].get((ref, i)) != n
                                            and FORCE[kind].get(0) == 0 for i in ins):
                        continue
                    if kind in ("BUF_OD", "INV_OD") and level == 0: continue        # can only pull it low
                    bad("a second %s output on the net (%s)" % (kind, fam["name"])); continue
                continue                                                           # NC, VCC or GND pin
            fq = fet_of(nl, ref)
            if fq is not None:
                t, pp = fq
                if pin == pp["G"]: continue                                       # a FET gate only reads
                other = pp["D"] if pin == pp["S"] else pp["S"]
                g_net, o_net = nl["pin"].get((ref, pp["G"]), ""), nl["pin"].get((ref, other), "")
                if t == "N" and pin == pp["D"] and is_ground(o_net):
                    if level == 0: continue                                       # it can only pull the net low
                    bad("an N-channel switch to ground, gate on %s, pulls the net low against the level EMCON forces" % g_net); continue
                sk = is_supply.kind(k, o_net)
                if sk == "name":
                    # a supply known only by its name is walked for what drives it as well (R4T-D42)
                    go(k, o_net, "%s %s-channel %s->%s onto %s, a supply by its name only" % (ref, t, pin, other, o_net), ref)
                if t == "P" and sk:
                    v_sup = rail_volts(o_net) if sk == "rail" else None
                    if level == 1 and v_sup is not None and v_sup >= V_FIRMWARE_HIGH: continue    # it lifts the net EMCON's way
                    if level == 1:
                        bad("a P-channel switch from %s (%s), gate on %s, ties the net %s the %g V at which the census takes a "
                            "net EMCON holds high" % (o_net, ("%g V" % v_sup) if v_sup is not None else _SUPPLY_WHY[sk], g_net,
                                                          "under" if v_sup is not None else "to a level not shown to reach",
                                                          V_FIRMWARE_HIGH)); continue
                    bad("a P-channel switch from %s, gate on %s, pulls the net high against the level EMCON forces" % (o_net, g_net)); continue
                if sk or is_ground(o_net):
                    bad("its channel ties the net to %s" % o_net); continue
                # a level shifter (gate on a rail) or any other channel conducts both ways while it is on
                go(k, o_net, "%s %s-channel %s->%s" % (ref, t, pin, other), ref); continue
            sw = switch_of(nl, ref)
            if sw:
                if pin == sw["en"]: continue                                      # an enable only reads
                unk("a pin of %s that is not its enable" % sw["name"]); continue
            ps = pins_of(nl, ref)
            if re.match(r"^R\d", ref) and len(ps) == 2:
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if m2 == n or _dead(m2): continue                                  # both ends here, or nothing there
                sk = is_supply.kind(k, m2)
                if is_ground(m2) or sk:
                    # a pull (R4T-D42, above): EMCON's way it is harmless; against the forced level it is summed
                    # (PULL_MA_MAX). On a net an open-drain output has released (`released`) the pulls to ground and to
                    # a '+' rail that states its voltage ARE what sets the level, and their hold is judged by
                    # own_supply()'s released state, so none of them is a load on a driver here. A supply whose voltage
                    # no name states is never harmless: a pull to it is UNDECIDED and a 0 Ohm link to it FAILS, at either
                    # level; and one known only by its name is walked for its drivers as well
                    if sk == "name":
                        go(k, m2, "%s %s to %s, a supply by its name only" % (ref, value(nl, ref)[:12], m2), ref)
                    v_far = 0.0 if is_ground(m2) else (rail_volts(m2) if sk == "rail" else None)
                    if released and v_far is not None: continue
                    if level == 0 and is_ground(m2): continue
                    if level == 1 and v_far is not None and v_far >= V_FIRMWARE_HIGH: continue
                    ohm = _ohms(value(nl, ref))
                    if ohm is not None and ohm <= 0:
                        bad("a %s link ties the net to %s against the level EMCON forces%s" % (
                            value(nl, ref)[:12], m2, "" if v_far is not None else " (%s)" % _SUPPLY_WHY[sk])); continue
                    v_against = v_far if level == 0 else (V_FIRMWARE_HIGH - v_far if v_far is not None else None)
                    if ohm is None or v_against is None:
                        unk("a pull to %s through %s whose value or voltage cannot be read (%r)%s" % (
                            m2, ref, value(nl, ref)[:20], "" if v_far is not None else ": " + _SUPPLY_WHY[sk])); continue
                    acc["ma"] += 1e3 * v_against / ohm; acc["pulls"].append("%s %s %s to %s" % (k, ref, value(nl, ref)[:12], m2))
                    if fet_forced and not acc.get("fet_named"):
                        # THE 4 mA FLOOR IS THE LVC SHEETS' VOL (review of the second fix-up, minor 1). A net forced by
                        # a FET (a level shifter or a switch to ground) holds its level through the FET's channel,
                        # and the fitted 2N7002 states its on resistance only at VGS 5 V and 10 V.
                        unk("a pull against the forced level on a net a FET forces (%s): %s" % (fet_forced[0], fet_forced[1]))
                        acc["fet_named"] = True
                    if acc["ma"] > PULL_MA_MAX and not acc["named"]:
                        bad("the pulls against the forced level on this conductor (%s) ask %.1f mA of the gate, above the "
                            "%.0f mA at which every held logic sheet still guarantees the level"
                            % (", ".join(acc["pulls"]), acc["ma"], PULL_MA_MAX))
                        acc["named"] = True                                       # named once per conductor
                    continue
                go(k, m2, "%s %s" % (ref, value(nl, ref)[:12]), ref); continue
            if re.match(r"^(L|FB)\d", ref) and len(ps) == 2:
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if is_ground(m2) and level == 0: continue
                if is_supply(k, m2) or is_ground(m2):
                    bad("tied to %s through %s" % (m2, ref)); continue
                go(k, m2, "%s bead" % ref, ref); continue
            if re.match(r"^(D|LED)\w*", ref) and len(ps) == 2:
                o = ps[1] if ps[0] == pin else ps[0]
                m2, fo = nl["pin"].get((ref, o), ""), nl["func"].get((ref, o), "")
                if _dead(m2): continue
                known = {fn, fo} == {"K", "A"}
                can_raise = (fn == "K") if known else True                        # a cathode here lets the far side lift it
                can_lower = (fn == "A") if known else True
                if is_supply(k, m2) or is_ground(m2):
                    # A FIXED FAR SIDE IS A SOURCE TOO (second fix-up of round 4, 26 September 2026). The first fix-up
                    # skipped a diode to a rail or ground before asking its orientation, so a BAT54 with its anode on
                    # +3V3 and its cathode on an enable EMCON holds low read PASS, and so did a forward diode to ground
                    # on a net EMCON holds high. A diode that can pull the net toward its far side, against EMCON's
                    # level, fails; one whose orientation the drawing does not give is undecided.
                    if not known:
                        unk("a diode to %s whose drawing names no cathode, so whether it can pull the net against "
                            "EMCON's level is not known" % m2); continue
                    v_far = rail_volts(m2)
                    if level == 0 and can_raise and not is_ground(m2):
                        bad("a diode from %s (anode) onto the net (cathode) lifts it against the level EMCON forces" % m2); continue
                    if level == 1 and can_lower:
                        if is_ground(m2) or (v_far is not None and v_far < V_FIRMWARE_HIGH):
                            bad("a diode from the net (anode) to %s (cathode) pulls it down against the level EMCON "
                                "forces" % m2); continue
                        if v_far is None:
                            unk("a diode from the net to %s, whose voltage its name does not state" % m2); continue
                    continue                                                      # a clamp: it only conducts EMCON's way
                if not (can_raise if level == 0 else can_lower): continue         # it can only pull the net EMCON's way
                go(k, m2, "%s diode" % ref, ref); continue
            if re.match(r"^(SW)\w*", ref) and n in SOURCES:
                continue                                                          # the panel toggle is the line's source
            if re.match(r"^(J|P)\w*", ref):
                mate, _why = _mate(k, ref)
                if mate:
                    k2, r2 = mate
                    if boards.get(k2) is None: absent.add(k2); continue
                    go(k2, boards[k2]["pin"].get((r2, pin), ""), "%s %s pin %s = %s %s pin %s" % (k, ref, pin, k2, r2, pin), ref)
                    continue
                unk("the conductor leaves the board here and neither a mated connector nor a maker document says "
                    "what the far end does with it"); continue
            if software_io(nl, ref):
                bad("a pin whose direction firmware sets: a firmware error drives the gate net, so the gate depends "
                    "on software"); continue
            fm = fw_mention(nl, ref)                                              # R4T-D53: named, never passed
            unk("an active pin no held document shows to be an input" + ("; " + _mention_why(nl, ref, fm) if fm else ""))
    return dict(fail=fail, undecided=und, boards=named, absent=absent, reach=seen)


def line_census(boards, walks):
    """{line: census} for each asserted line, over every board that carries it: who else can drive it while its source
    drives it (census), and what it reads with its source unpowered or unplugged and every other part powered or not,
    whichever is worse (fail_safe)."""
    out = {}
    for s in SOURCES:
        start = [(k, s) for k, nl in sorted(boards.items()) if nl is not None and s in nl["nets"]]
        if not start: continue
        acc = dict(fail=[], undecided=[], boards=set(), absent=set(), reach=set(), carriers=set())
        for k, n in start:
            if (k, n) in acc["reach"]: continue
            c = census(boards, walks, k, n, 0, set())
            for key in ("fail", "undecided"): acc[key] += c[key]
            for key in ("boards", "absent", "reach"): acc[key] |= c[key]
        fs = fail_safe(boards, s)
        acc["fail"] += fs["fail"]; acc["undecided"] += fs["undecided"]
        acc["boards"] |= fs["boards"]; acc["absent"] |= fs["absent"]
        acc["carriers"] = {k for k, n in acc["reach"] if n == s} | {k for k, _n in start}
        out[s] = acc
    return out


# ---------------------------------------------------------------- the fail-safe states
# RF-002 ASKS FOR MORE THAN ONE DRIVER: "the inhibit is asserted by the unpowered and disconnected states" (second
# fix-up of round 4, 26 September 2026). The census above asks who else can drive a line WHILE its source drives it.
# With the panel unplugged, or its own 3.3 V down, the source drives nothing: board C's U9 (a 74LVC1G17 since main
# faf8c981, a 74LVC1G34 before it; both are specified for partial power down, "Ioff") is out of the circuit or high
# impedance, and the line is held only by its own pull-downs. Anything on its conductor that can source current then
# decides it. On board B at main 82dd1e4d the three level-shifter FETs Q106, Q206 and Q306 have their drains on
# EMCON_HW and their sources pulled up to the slot rails through 10 kOhm; the fitted 2N7002 (JSCJ, LCSC C8545, sheet
# dated J,Sep,2016, v2/vendor/power/jscj-2n7002-c8545.pdf, on main since ccf5808e)
# has its body diode with the anode on S and the cathode on D (the Equivalent Circuit, page 1), so each one lifts the
# line, and the two 100 kOhm pull-downs cannot hold it under the gates' 0.8 V. Nothing checked that, so every gate on A
# and B read "released" with the panel out while RF-002 read PASS.
#
# What is judged: the line's conductor across the mated ribbons, in every state where its source does not drive it:
# each subset of those ribbons unplugged, and in each fragment of the conductor that still carries the source, the
# source's board unpowered (the rails it makes down, its parts unpowered; a rail it receives over a plugged ribbon stays
# up while the board at the other end is up, as board C's +5V does from B's PANEL_5V while C's own +3V3, and U9 with
# it, is down).
#
# EVERY OTHER PART IS TAKEN POWERED OR UNPOWERED, WHICHEVER IS WORSE (round 6 second pass, 26 September 2026, review of
# round 6, blocking 1). Round 6 took every board but the source's as powered and said that "can only add sources". It
# cannot: an unpowered LVC1G part passes its Ioff (10 uA, SCES217AA, SCES296AG, DS35124), twice the II it passes
# powered (5 uA), and an unpowered SN74LVC08A is not bounded at all (R4T-D29). With boards B and C unpowered and A
# powered, the review's 47k/22k kit read 1.05 V, a FAIL in a state the tool never solved. Enumerating whole boards (the
# review's 16 x 16 solves) would still miss a board that loses ONE rail: board A makes +3V3 (its buck through L7, U26's
# supply) apart from the +5V_DEV its eFuse U23 hands to board B, so A's gates can be unpowered while B's read the line.
# So each part is bounded on its own (_fs_bound): for each reader, a gate input, a switch enable or a FET gate, the
# network is solved with that reader's own supply up and every other part at the worse of its two states. The reader's
# supply is its VCC pin (a logic part) or its input pins (a switch, never its output), whatever the nets are called, and a
# reader with none of its supply on the netlist is a domain of its own (R4T-D41, round 6 third pass: a reader on VBAT,
# VCC_X or 3V3_DEV used to fall into an empty domain and was never judged; a FET gate has no supply and reads in every
# run). A logic input
# passes max(II, Ioff), or leaves the state UNDECIDED if its part states no Ioff; a firmware pin is a source at its
# supply AND passes an unpowered current nobody bounds; a module input carries its maker's pull AND that unpowered
# current; a level shifter's channel is taken on AND, where its sheet states no off-state current over the envelope,
# off with that current unbounded; a push-pull output is a source at its supply. That covers every subset of the carrier
# boards unpowered and every rail lost on its own. The whole-board states are still solved exactly when the bound does
# not pass (_fs_state, the review's enumeration), so the result names a physical state a board author can picture, and
# one of them failing fails the line even if the bound were to miss it.
#
# RESISTOR VALUES AND RAILS THE ADVERSE WAY (round 6 second pass, review minor 2; R4T-D36). A resistor from the net to a
# fixed node is taken at the end of its tolerance that hurts: a pull toward the level the net must hold at its maximum,
# a pull against it at its minimum. The tolerance is read from the value ("62k 1%") and is TOL_DEFAULT where the value
# states none. A rail is taken at the voltage its name states plus RAIL_TOL against a net held low, minus it for a net
# held high. A resistor between two unfixed nodes (a series tap), a ribbon or a bead, and a maker's own pull (no maker
# here states a tolerance for one) are taken at their nominal values, and every result says so.
# Each part of the conductor that has no driving source is a small resistive network (_network below): its
# pull-downs to ground; every pull-up, internal pull-up a maker states, firmware pin (at its supply) and push-pull
# output as a source; every FET or diode that can pass current toward the line as an IDEAL one-way element with no
# forward drop (the 2N7002's sheet gives VSD 0.55 V to 1.2 V at IS 115 mA and no minimum at the microamps a pull-up
# passes, and its channel conducts while VGS exceeds Vth(GS), 1.0 V to 2.5 V, so no drop is the bound that holds for
# every part); AND EVERY PIN'S OWN CURRENT (round 6, below). The line must stay under VIL_LOW (0.8 V) at every powered
# gate that reads it in every state, or the line FAILS; a pin whose current no document bounds leaves it UNDECIDED
# unless the known currents alone already lift it; a line with nothing holding it low FAILS as floating.
#
# THE PINS ON A HELD NET ARE NOT IDEAL (round 6, 26 September 2026, review of the second fix-up, blocking 1). The
# first model took every CMOS input as drawing no current, and the line's pull-downs are 100 kOhm on each board: at the
# SN74LVC08A's guaranteed II of 5 uA (TI SCAS283W 5.7, -40 to +85 C), the six inputs on boards A and B give 30 uA x
# 50 kOhm = 1.5 V with nothing else on the line, and the three 74LVC1G07 the second fix-up recommended add 15 uA more.
# So every pin a held net meets now passes its sheet's ADVERSE-SIGN MAXIMUM current into the network (into the net
# when it must stay low, out of it when it must stay high): II for a powered logic input, Ioff for any pin of an
# unpowered part that states one, the enable-pin current of a switch, the pull a module's maker states for its own
# pin. A pin whose current no held sheet bounds leaves the state UNDECIDED unless the known currents decide it: an
# unpowered SN74LVC08A or SN74LVC00A (their sheets have no Ioff row, and SCAS283W 7.3.3 gives the outputs clamp diodes
# to VCC, so they are not specified for partial power down: a supply back-fed through another pin can half-power
# them); a FET whose sheet states its leakage at 25 C only (the JSCJ 2N7002); a diode's reverse current; an unpowered
# controller or module; a module input whose maker states nothing. The column read is -40 to +85 C (R4T-D28, taken by
# the session under the owner's standing rule of 26 Sep 2026): it covers the envelope and its qualification margin
# (-20 to +40 C in use, +55 C operating, owner ruling D-02a), a 25 C figure does not, and the -40 to +125 C column
# (SN74LVC08A II 20 uA) asks for pull-downs the envelope does not need. A current stated at one voltage is used as the
# bound where the sheet states it at or across the threshold the net is judged against: a pin that cannot push the
# net past the threshold with the current it passes AT the threshold cannot push it there at all.
_FS_INERT = re.compile(r"^(#|TP|FID|MH|H\d|C\d)")
VIH_HIGH = 2.0          # the gates' VIH at VCC 3 V to 3.6 V (every LVC sheet in LOGIC but the two Schmitt families,
# which state VT+ at VCC 3 V and 4.5 V only, Diodes DS35124 2.00 V and TI SCES414P 1.87 V maximum at 3 V, 2.74 V at 4.5 V:
# a HIGH at their inputs is not read as passing, `vih_gap`, EQ-18)
# VIL_LOW AND VIH_HIGH HOLD ONLY AT VCC 3 V TO 3.6 V (round 6 second pass, review minor 3): the same LVC sheets give VIL
# 0.35 VCC at 1.65 V to 1.95 V (about 0.63 V) and 0.3 VCC at 4.5 V to 5.5 V. A reader whose supply's name states a
# voltage outside this range, or none, is not judged at 0.8 V or 2.0 V: it leaves the state UNDECIDED and is named. Its
# supply is its VCC pin's net, and a name with no '+' (VCC_X, 3V3_DEV) states none (R4T-D41). A line that FLOATS at such
# a reader still FAILS: nothing holds it at any VCC. One that reads at or above its family's vil_ceiling FAILS too, since
# no VCC the sheet allows reads it as low (R4T-D45, round 6 fourth pass: 1.65 V for the single and dual gates, 0.3 x
# 5.5 V; 0.8 V for the quads, which stop at 3.6 V; 1.45 V for the 74LVC1G17's VT-; 1.87 V for the SN74LVC1G57's VT-,
# EQ-18). Between 0.8 V and that ceiling it is
# UNDECIDED, because some VCC reads it as low and the name does not say which.
VCC_RANGE = (3.0, 3.6)
LEAK_COLUMN = "-40 to +85 C"
# R4T-D36 (round 6 second pass, taken by the session under the owner's standing rule of 26 Sep 2026). TOL_DEFAULT is
# the tolerance of a resistor whose value states none: 5 percent, wider than the 1 percent parts the generators draw
# wherever they state one. RAIL_TOL is every rail's allowance: 5 percent, wider than the output accuracy of the
# regulator sheets held in v2/vendor for rails these lines meet (TI TLV755P, SBVS320D, v2/vendor/power: 1 percent
# maximum, -40 to +85 C, DBV; Diodes AP64500, DS41979 Rev. 5-2, v2/vendor/diodes: feedback reference 792 to 808 mV,
# 1 percent, before its 1 percent divider). Options were the per-regulator figure (each sheet read for each rail, and
# not every rail's regulator sheet is held) or one allowance above all of them.
TOL_DEFAULT = 0.05
RAIL_TOL = 0.05


def _tol(v):
    """The tolerance a resistor's value states ("62k 1%" 0.01), or TOL_DEFAULT."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", v or "")
    return float(m.group(1)) / 100.0 if m else TOL_DEFAULT


def _vcc_ok(nl, ref, rail_up=None, k=None):
    """(ok, vcc) for a logic part: ok when the supply its VCC pin's net names lies in VCC_RANGE, where VIL_LOW and VIH_HIGH
    hold; a supply whose name states no voltage (no '+', or none in it) is not ok (R4T-D39, R4T-D41)."""
    vs = [rail_volts(r) for r in _supply_nets(nl, ref) if rail_up is None or rail_up(k, r)]
    vs = [v for v in vs if v is not None]
    if not vs: return False, None
    v = max(vs)
    return VCC_RANGE[0] <= v <= VCC_RANGE[1], v
# The FETs whose sheets are held, with what they state about the currents a held net meets. The JSCJ 2N7002 states
# IGSS +-80 nA and IDSS 80 nA at Ta 25 C only, so neither bounds a pin over the envelope, and its channel's on
# resistance only at VGS 5 V and 10 V.
FETS = [dict(value=r"2N7002", vth=(1.0, 2.5), ron_vgs=5.0, leak=None,
             cite="JSCJ 2N7002 (LCSC C8545), sheet J,Sep,2016, page 2: Vth(GS) 1.0 to 2.5 V at 250 uA; IGSS +-80 nA "
                  "and IDSS 80 nA at Ta 25 C only; RDS(on) at VGS 5 V (7 Ohm) and 10 V (5 Ohm) only",
             file="v2/vendor/power/jscj-2n7002-c8545.pdf")]


def fet_family(nl, ref):
    c = nl["comps"].get(ref) or {}
    for f in FETS:
        if re.search(f["value"], c.get("value", "") + " " + c.get("lib", ""), re.I): return f
    return None


def _line_sources(nl, s):
    """[(ref, why)] of the parts on net s that make the asserted line: a switch (the panel toggle) and a logic output
    whose input sits on the other asserted line (the panel's buffer)."""
    out = []
    for ref, pin, _f in nl["nets"].get(s, []):
        if re.match(r"^SW\w*", ref):
            out.append((ref, "the toggle")); continue
        fam = logic_of(nl, ref)
        if fam and not _unmapped(fam):
            for ins, o, kind in fam["gates"]:
                if o == pin and any(nl["pin"].get((ref, i)) in SOURCES and nl["pin"].get((ref, i)) != s for i in ins):
                    out.append((ref, "the %s from %s" % (fam["name"], "/".join(nl["pin"].get((ref, i)) for i in ins))))
    return out


def _part_rails(nl, ref):
    return sorted({nl["pin"][(ref, p)] for p in pins_of(nl, ref) if is_rail(nl["pin"].get((ref, p), ""))})


def _solve(nodes, fixed, res, diodes, inj=None):
    """Node voltages of a resistive network with ideal one-way elements and current sources. nodes: ids of unknown
    nodes; fixed: {id: volts}; res: [(a, b, ohms)]; diodes: [(from, to, label)] conducting from -> to only, with no
    drop; inj: {node: amps into it}. Returns ({id: volts or None when floating}, [labels of the one-way elements that
    conduct]) or (None, why)."""
    inj = inj or {}
    on = [True] * len(diodes)
    for _it in range(64):
        g = [(a, b, 1.0 / max(r, 1e-3)) for a, b, r in res] + [(d[0], d[1], 1e3) for d, o in zip(diodes, on) if o]
        # the nodes that reach a fixed node through this state's conductors; the rest float
        adj = {}
        for a, b, _ in g:
            adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
        live, todo = set(fixed), list(fixed)
        while todo:
            x = todo.pop()
            for y in adj.get(x, ()):
                if y not in live: live.add(y); todo.append(y)
        unk = [x for x in nodes if x in live and x not in fixed]
        ix = {x: i for i, x in enumerate(unk)}
        n = len(unk)
        A = [[0.0] * (n + 1) for _ in range(n)]
        for x, i in ix.items(): A[i][n] += inj.get(x, 0.0)
        for a, b, c in g:
            for p, q in ((a, b), (b, a)):
                if p in ix:
                    A[ix[p]][ix[p]] += c
                    if q in ix: A[ix[p]][ix[q]] -= c
                    elif q in fixed: A[ix[p]][n] += c * fixed[q]
        for i in range(n):                                   # Gauss-Jordan with partial pivoting
            piv = max(range(i, n), key=lambda r: abs(A[r][i]))
            if abs(A[piv][i]) < 1e-15: return None, "the network is singular"
            A[i], A[piv] = A[piv], A[i]
            for r in range(n):
                if r != i and A[r][i]:
                    f = A[r][i] / A[i][i]
                    A[r] = [x - f * y for x, y in zip(A[r], A[i])]
        v = dict(fixed)
        for x, i in ix.items(): v[x] = A[i][n] / A[i][i]
        changed = False
        for j, (a, b, _l) in enumerate(diodes):
            va, vb = v.get(a), v.get(b)
            want = va is not None and (vb is None or va > vb + 1e-9) if not on[j] else \
                not (va is not None and vb is not None and va < vb - 1e-9)
            if want != on[j]: on[j] = want; changed = True
        if not changed:
            return {x: v.get(x) for x in list(nodes) + list(fixed)}, [d[2] for d, o in zip(diodes, on) if o]
    return None, "the one-way elements did not settle"


ASSUMED = "orientation not drawn"


def _solve_net(net):
    """_solve over a _network result, and a second solve without the one-way elements whose orientation the drawing
    does not give (taken the adverse way in the first): (got, on, got_without) where got_without is None when no
    such element conducts. A failure that holds only with them is undecided, not a failure: it rests on which way a
    part points, which nobody has drawn."""
    got, on = _solve(net["nodes"], net["fixed"], net["res"], net["diodes"], net["inj"])
    if got is None or not any(ASSUMED in x for x in on):
        return got, on, None
    g2, _o2 = _solve(net["nodes"], net["fixed"], net["res"], [d for d in net["diodes"] if ASSUMED not in d[2]], net["inj"])
    return got, on, g2


def _reaches_fixed(start, res, fixed, skip):
    """True when node `start` reaches a fixed node through the resistors of `res` other than those labelled in `skip`
    (a maker's own pull on a module pin: a pin held only by it is the maker's "left floating")."""
    adj = {}
    for i, (a, b, _r) in enumerate(res):
        if i in skip: continue
        adj.setdefault(a, set()).add(b); adj.setdefault(b, set()).add(a)
    seen, todo = {start}, [start]
    while todo:
        x = todo.pop()
        if x in fixed: return True
        for y in adj.get(x, ()):
            if y not in seen: seen.add(y); todo.append(y)
    return False


def _network(boards, start, level, st, anchors=None):
    """The network seen from the (board, net) nodes `start` in one state `st`: dict(rail_up(k, n), board_up(k), cut,
    sources, off, domain, on) where `sources` are the parts to take as absent (an open toggle), `off` the parts taken
    unpowered whatever their rails do (the line's own buffer), and `on` the parts taken powered (a transmitter judged
    while it runs). `domain` selects the power model: absent, every part is powered exactly when a rail on it is up
    (_fs_state, own_supply before round 6's second pass); a frozenset of (board, rail), the parts whose every live rail
    is in it are powered and every other part with a live rail is taken at the worse of powered and unpowered
    (_fs_bound). `level` is what the net must hold: 0 (a current into it is adverse) or 1 (a current out of it is).
    `anchors` {(k, ref, pin): model} carries a transmitter pin's maker-stated model (`pull`: (volts, ohms)) where a path
    ends on it. Returns a dict with the network (nodes, fixed, res, diodes, inj), the powered readers per node (`gates`)
    and their supplies (`vcc`), the readers that may be powered and the supplies that would power them (`cands`), what
    holds it and what lifts it (`pulls`, `lifts`), the pins no document bounds (`unsure`), and `stated`, the resistors
    that are a maker's own pull."""
    anchors = anchors or {}
    sgn = 1.0 if level == 0 else -1.0
    nodes, fixed, res, diodes, inj = set(), {"GND": 0.0}, [], [], {}
    pulls, lifts, unsure, absent, named, leaks, stated = [], [], [], set(), set(), [], set()
    gates, vcc, cands, ceil = {}, {}, {}, {}
    # EACH PART ENTERS THE NETWORK ONCE, from the side the walk meets first (the side nearer the line). Met from both
    # of its nets, a resistor counted twice would halve, and a FET or an unoriented diode entered both ways would be a
    # short that lets the far side's pull-downs help hold the line, which no bound may assume.
    done = set()
    rail_up, board_up, cut = st["rail_up"], st["board_up"], st["cut"]
    domain = st.get("domain")
    off, forced_on = st.get("off", set()), st.get("on", set())

    is_supply = _supply_test(boards)

    def fix(v):
        key = "V%.3f" % v; fixed[key] = v; return key

    def rail_v(v):
        # a rail the adverse way (R4T-D36): higher against a net held low, lower under a net held high
        return v * (1 + RAIL_TOL) if level == 0 else v * (1 - RAIL_TOL)

    def node_of(k, n):
        # a supply is a fixed node or unknown, never a signal node, whatever its name (R4T-D41)
        if is_ground(n): return "GND"
        if is_supply(k, n):
            if not rail_up(k, n): return None
            v = rail_volts(n)
            return fix(rail_v(v)) if v is not None else ("?", k, n)
        return (k, n)

    def pstate(k, nl, ref):
        """'on', 'off' or 'either' (only with a domain: the part may be powered or not, and both are taken). A part runs
        from _supply_nets (R4T-D41); one with none on the netlist is its own domain, powered only in its own run."""
        if (k, ref) in off: return "off"
        if (k, ref) in forced_on: return "on"
        rails = _supply_nets(nl, ref)
        if not rails:
            if not board_up(k): return "off"
            return "on" if domain is None or (k, _SELF + ref) in domain else "either"
        live = [r for r in rails if rail_up(k, r)]
        if not live: return "off"
        if domain is None or all((k, r) in domain for r in live): return "on"
        return "either"

    def supply_of(k, nl, ref):
        live = frozenset((k, r) for r in _supply_nets(nl, ref) if rail_up(k, r))
        return live or frozenset({(k, _SELF + ref)})

    def leak(k, n, amps, label):
        inj[(k, n)] = inj.get((k, n), 0.0) + sgn * amps
        leaks.append("%s %s %.1f uA" % (k, label, amps * 1e6))

    def unknown(k, what):
        unsure.append("%s %s" % (k, what)); named.add(k)

    def reader(k, n, nl, ref, label, state, logic=False):
        """A pin that reads the net: judged when powered, a candidate for its own domain's solve when it may be. A logic
        reader's supply is recorded, because VIL_LOW holds only in VCC_RANGE, and so is its family's vil_ceiling, the
        level no VCC reads as low (R4T-D45); a switch enable's stated off level is above VIL_LOW on every part in
        SWITCHES, so VIL_LOW is the stricter reading for it."""
        if state == "on":
            gates.setdefault((k, n), []).append(label)
            if logic:
                vcc.setdefault((k, n), []).append((label, _vcc_ok(nl, ref, rail_up, k)))
                ceil.setdefault((k, n), []).append((label, (logic_of(nl, ref) or {}).get("vil_ceiling")))
        elif state == "either":
            cands.setdefault(supply_of(k, nl, ref), []).append(((k, n), label))

    seen, todo = set(), list(start)
    while todo:
        k, n = todo.pop(0)
        if (k, n) in seen: continue
        seen.add((k, n)); nodes.add((k, n))
        nl = boards.get(k)
        if nl is None:
            absent.add(k); continue

        def edge(n2, ohms, label, is_stated=False, tol=0.0):
            t = node_of(k, n2)
            if t is None: return                                        # a rail that is down: neither a pull nor a source
            if isinstance(t, tuple) and t and t[0] == "?":
                unknown(k, "%s ties it to %s, whose voltage its name does not state" % (label, n2)); return
            if is_stated: stated.add(len(res))
            elif tol and (t == "GND" or t in fixed):
                # the end of the tolerance that hurts (R4T-D36): a pull toward the held level at its maximum, one
                # against it at its minimum
                weaker = (t == "GND") == (level == 0)
                ohms = ohms * (1 + tol) if weaker else ohms * (1 - tol)
            res.append(((k, n), t, ohms))
            if t == "GND": pulls.append("%s %s" % (k, label))
            elif t in fixed and fixed[t] > 0: (lifts if level == 0 else pulls).append("%s %s from %s" % (k, label, n2))
            elif t not in fixed: todo.append(t)

        for ref, pin, fn in nl["nets"].get(n, []):
            v = value(nl, ref)
            if _FS_INERT.match(ref): continue
            if (k, ref) in st.get("sources", set()): continue            # the line's own toggle, open
            if PROTECTION.match(v):
                # a clamp from the net to ground only takes current off a net that must stay low; elsewhere its reverse
                # current is not tabulated here
                others = [nl["pin"].get((ref, p), "") for p in pins_of(nl, ref) if p != pin]
                if level == 0 and all(is_ground(o) or _dead(o) for o in others): continue
                unknown(k, "%s (%s): a clamp whose reverse current toward the net is not tabulated here" % (ref, v[:24])); continue
            if len(pins_of(nl, ref)) == 2 or fet_of(nl, ref) is not None:
                if (k, ref) in done: continue
                done.add((k, ref))
            am = anchors.get((k, ref, pin))
            if am is not None:
                # the transmitter's own pin: its maker's model or nothing known; judged while the transmitter runs
                if am.get("pull") and pstate(k, nl, ref) != "off":
                    pv, po = am["pull"]
                    edge_t = fix(pv) if pv > 0 else "GND"
                    stated.add(len(res)); res.append(((k, n), edge_t, po))
                    (lifts if (pv > 0) == (level == 0) else pulls).append(
                        "%s %s pin %s's own pull (%g V through %g ohm, its maker)" % (k, ref, pin, pv, po))
                elif am.get("leak") is not None:
                    leak(k, n, am["leak"], "%s pin %s (its maker)" % (ref, pin))
                else:
                    unknown(k, "%s pin %s (%s): its maker states no input current for it" % (ref, pin, v[:30]))
                continue
            pr = [d for d in PIN_READERS if (d["board"], d["ref"], str(d["pin"])) == (k, ref, pin)]
            if pr:
                # the maker's stated pull-up IS the pin's DC model while the module runs; unpowered, nothing is stated
                state = pstate(k, nl, ref)
                if state != "on":
                    unknown(k, "%s pin %s: a module input%s whose maker states no off-state current" % (
                        ref, pin, "" if state == "off" else " that may be unpowered while the line is read,"))
                if state != "off" and pr[0].get("pull_up"):
                    pv, po = pr[0]["pull_up"]
                    res.append(((k, n), fix(pv), po))
                    (lifts if level == 0 else pulls).append("%s %s pin %s's own pull-up (%g V through %g ohm)" % (k, ref, pin, pv, po))
                continue
            ps = pins_of(nl, ref)
            if re.match(r"^(R\d)", ref) and len(ps) == 2:
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if _dead(m2) or m2 == n: continue
                ohm = _ohms(v)
                if ohm is None:
                    unknown(k, "%s (%r) has a value that cannot be read" % (ref, v[:20])); continue
                edge(m2, ohm, "%s %s" % (ref, v[:12]), tol=_tol(v)); continue
            if re.match(r"^(L|FB)\d", ref) and len(ps) == 2:
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if not _dead(m2): edge(m2, 0.01, "%s bead" % ref)
                continue
            fq = fet_of(nl, ref)
            if fq is not None:
                t, pp = fq
                ff = fet_family(nl, ref)
                if pin == pp["G"]:                                            # a gate only reads, and it is decided here
                    gates.setdefault((k, n), []).append("%s %s gate" % (k, ref))
                    if not (ff and ff.get("leak") is not None):
                        unknown(k, "%s gate (%s): %s" % (ref, v[:16], "its sheet states IGSS at 25 C only" if ff else
                                                      "no held sheet states its gate current"))
                    else:
                        leak(k, n, ff["leak"], "%s gate" % ref)
                    continue
                other = pp["D"] if pin == pp["S"] else pp["S"]
                o_net, g_net = nl["pin"].get((ref, other), ""), nl["pin"].get((ref, pp["G"]), "")
                s_net = nl["pin"].get((ref, pp["S"]), "")
                if _dead(o_net): continue
                # N: body diode anode S, cathode D; P: anode D, cathode S. It passes current TOWARD the net when the net
                # is its cathode side, and AWAY from it when the net is its anode side.
                diode_toward = (pin == pp["D"]) if t == "N" else (pin == pp["S"])
                diode_adverse = diode_toward if level == 0 else not diode_toward
                gate_off = g_net == s_net or (t == "N" and (is_ground(g_net) or (is_supply(k, g_net) and not rail_up(k, g_net))))
                # a FET EMCON holds off (own_supply's released state, R4T-D46): its gate sits at EMCON's low, so its
                # channel is off and passes only its off-state current, which the fitted 2N7002 states at 25 C only
                held_off = (k, ref) in st.get("released", set())
                gate_off = gate_off or held_off
                adverse = diode_adverse or not gate_off
                far = node_of(k, o_net)
                # THE CHANNEL'S OFF STATE IS A STATE TOO (round 6 second pass): with a domain, a gate on a live rail can
                # lose that rail on its own, and the channel then passes its off-state current, which the fitted
                # 2N7002's sheet states at 25 C only
                if domain is not None and t == "N" and not gate_off and not diode_adverse and is_supply(k, g_net) \
                        and not (ff and ff.get("leak") is not None):
                    unknown(k, "%s (%s) %s: with its gate rail %s lost on its own the channel is off, and its off-state "
                               "current %s" % (ref, v[:16], pin, g_net, "is stated at 25 C only" if ff else "is stated by no held sheet"))
                if far is None:
                    if not adverse or level == 0: continue                 # a dead rail neither lifts it nor takes it
                if isinstance(far, tuple) and far and far[0] == "?":
                    unknown(k, "%s passes %s, whose voltage its name does not state" % (ref, o_net)); continue
                if adverse and far is not None:
                    how = "its body diode (anode on %s)" % ("S" if t == "N" else "D") if diode_adverse \
                        else "its channel (gate on %s)" % g_net
                    a, b = (far, (k, n)) if level == 0 else ((k, n), far)
                    diodes.append((a, b, "%s %s (%s, %s on %s, %s on the line side): %s"
                                   % (k, ref, v[:30], other == pp["S"] and "S" or "D", o_net, pin == pp["D"] and "D" or "S", how)))
                    if far not in fixed: todo.append(far)
                    continue
                unknown(k, "%s (%s) %s: %sits off-state channel current %s" % (
                    ref, v[:16], pin, "a FET EMCON holds off, and " if held_off else "",
                    "is stated at 25 C only" if ff else "is stated by no held sheet"))
                continue
            if re.match(r"^(D|LED)\w*", ref) and len(ps) == 2:
                o = ps[1] if ps[0] == pin else ps[0]
                m2, fo = nl["pin"].get((ref, o), ""), nl["func"].get((ref, o), "")
                if _dead(m2): continue
                known = {fn, fo} == {"K", "A"}
                # for a net that must stay low the adverse way is a cathode here (the far side can lift it); for one
                # that must stay high it is an anode here (the net can drain into the far side)
                adverse = (not known) or (fn == ("K" if level == 0 else "A"))
                far = node_of(k, m2)
                if far is None: continue
                if isinstance(far, tuple) and far and far[0] == "?":
                    unknown(k, "%s from %s, whose voltage its name does not state" % (ref, m2)); continue
                if adverse:
                    a, b = (far, (k, n)) if level == 0 else ((k, n), far)
                    diodes.append((a, b, "%s %s (%s) %s %s%s" % (k, ref, v[:30], "from" if level == 0 else "to", m2,
                                                                  "" if known else ", " + ASSUMED + ", taken the adverse way")))
                    if far not in fixed: todo.append(far)
                    continue
                if level == 1 or not (is_ground(m2)):
                    unknown(k, "%s (%s): a diode whose reverse current no held sheet states" % (ref, v[:24]))
                continue
            if re.match(r"^(J|P)\w*", ref):
                mate, _w = _mate(k, ref)
                if mate:
                    mi = [i for i, m in enumerate(MATES) if (k, ref) in (m["a"], m["b"])][0]
                    k2, r2 = mate
                    if mi in cut: continue                                       # unplugged: the pin is open
                    if boards.get(k2) is None: absent.add(k2); continue
                    n2 = boards[k2]["pin"].get((r2, pin), "")
                    if _dead(n2): continue
                    t2 = (k2, n2) if not (is_supply(k2, n2) or is_ground(n2)) else None
                    if t2 is None: continue                                      # a rail or ground pin is the same conductor as ours only if our net is one
                    mk = frozenset({(k, ref, pin), (k2, r2, pin)})
                    if mk in done: continue
                    done.add(mk)
                    res.append(((k, n), t2, 1e-3)); todo.append(t2); continue
                if pstate(k, nl, ref) == "off": continue
                unknown(k, "%s pin %s: the conductor leaves the board and nothing says what the far end drives" % (ref, pin)); continue
            state = pstate(k, nl, ref)
            fam = logic_of(nl, ref)
            if fam is not None:
                if fam.get("wrong_land"):
                    unknown(k, "%s: a %s on a land its pin map is not for" % (ref, fam["name"])); continue
                if fam.get("unwired"):
                    unknown(k, "%s pin %s: %s" % (ref, pin, fam["unwired"])); continue
                is_in = any(pin in ins for ins, _o, _k in fam["gates"])
                outs = [kind for ins, o, kind in fam["gates"] if o == pin]
                if not (is_in or outs): continue                                  # NC, VCC or GND pin
                if (k, ref) in st.get("released", set()) and outs and outs[0] in ("BUF_OD", "INV_OD") and state != "off":
                    # an open-drain output EMCON releases (own_supply's released state): it drives nothing, and its
                    # powered off-state output current is stated by no LVC sheet held (only Ioff, at VCC 0)
                    unknown(k, "%s pin %s: an open-drain output EMCON releases, whose off-state current while powered its "
                               "sheet does not state" % (ref, pin))
                    continue
                # AN UNPOWERED PART PASSES ITS Ioff, IF IT STATES ONE (round 6). One that does not is not specified for
                # partial power down: a supply back-fed through another pin can half-power it. A part that may be
                # either (a domain's solve) is taken both ways.
                if state != "on" and fam.get("ioff") is None:
                    unknown(k, "%s pin %s: %s, whose sheet states no Ioff, so what it passes unpowered is not bounded (%s)"
                               % (ref, pin, ("an unpowered " + fam["name"]) if state == "off" else
                                  ("a %s that may be unpowered while the line is read" % fam["name"]),
                                  fam.get("leak_cite", "")[:90]))
                if state == "off":
                    if fam.get("ioff") is not None:
                        leak(k, n, fam["ioff"], "%s pin %s unpowered (Ioff, %s)" % (ref, pin, fam["name"]))
                    continue
                if is_in:                                                        # an input only reads, and leaks
                    label = "%s %s pin %s" % (k, ref, pin)
                    reader(k, n, nl, ref, label, state, logic=True)
                    if state == "on" or fam.get("ioff") is None:
                        leak(k, n, fam["ii"], "%s pin %s (II, %s)" % (ref, pin, fam["name"]))
                    else:                                                        # either: the worse of II and Ioff
                        amps = max(fam["ii"], fam["ioff"])
                        leak(k, n, amps, "%s pin %s (%s, %s, powered or not)" % (
                            ref, pin, "Ioff" if fam["ioff"] >= fam["ii"] else "II", fam["name"]))
                    continue
                if outs[0] in ("BUF_OD", "INV_OD"):
                    if level == 0:
                        unknown(k, "%s pin %s: a%s open-drain output whose off-state current its sheet does not "
                                   "state" % (ref, pin, " powered" if state == "on" else "n"))
                        continue
                    res.append(((k, n), "GND", 1e-3)); pulls.append("%s %s pin %s, an open-drain output that can pull it low" % (k, ref, pin))
                    continue
                # its VCC pin's voltage (R4T-D41); where that name states none, the firmware figure, and it is named
                vcs = [rail_volts(r) for r in _supply_nets(nl, ref) if rail_up(k, r)]
                if any(x is None for x in vcs):
                    unknown(k, "%s pin %s: a push-pull %s output whose supply's name states no voltage" % (ref, pin, fam["name"]))
                vc = max([x for x in vcs if x is not None] or [V_FIRMWARE_HIGH])
                if level == 0:
                    res.append(((k, n), fix(rail_v(vc)), 1e-3)); lifts.append("%s %s pin %s, a push-pull %s output (%g V)" % (k, ref, pin, fam["name"], vc))
                else:
                    res.append(((k, n), "GND", 1e-3)); pulls.append("%s %s pin %s, a push-pull %s output that can drive it low" % (k, ref, pin, fam["name"]))
                continue
            sw = switch_of(nl, ref)
            if sw and pin == sw["en"]:
                if state != "on":
                    unknown(k, "%s enable: a%s %s, whose off-state enable current its sheet does not state" % (
                        ref, "n unpowered" if state == "off" else " possibly unpowered", sw["name"]))
                    if state == "off": continue
                reader(k, n, nl, ref, "%s %s enable" % (k, ref), state)
                if sw.get("en_leak") is None:
                    unknown(k, "%s enable (%s): its sheet bounds no enable current at the off threshold (%s)" % (
                        ref, sw["name"], sw.get("off_cite", "")[:120]))
                else:
                    leak(k, n, sw["en_leak"], "%s enable (%s)" % (ref, sw["name"]))
                continue
            if software_io(nl, ref):
                if state != "on":
                    unknown(k, "%s pin %s (%s): a%s controller pin whose off-state current no held sheet states" % (
                        ref, pin, v[:24], "n unpowered" if state == "off" else " possibly unpowered"))
                    if state == "off": continue
                vh = max([rail_volts(r) or 0 for r in _part_rails(nl, ref) if rail_up(k, r) and (rail_volts(r) or 0) <= 3.6]
                         or [V_FIRMWARE_HIGH])
                if level == 0:
                    res.append(((k, n), fix(rail_v(vh)), 1e-3)); lifts.append("%s %s pin %s, a pin firmware can drive high (%g V)" % (k, ref, pin, vh))
                else:
                    res.append(((k, n), "GND", 1e-3)); pulls.append("%s %s pin %s, a pin firmware can drive low" % (k, ref, pin))
                continue
            if re.match(r"^SW\w*", ref): continue                                 # a switch that is not the source: open
            fm = fw_mention(nl, ref)                                              # R4T-D53: named, never passed
            fmw = ("; " + _mention_why(nl, ref, fm)) if fm else ""
            if state == "off":
                unknown(k, "%s pin %s (%s): an unpowered part whose off-state current no held document bounds%s" % (
                    ref, pin, v[:30], fmw))
                continue
            unknown(k, "%s pin %s (%s): an active pin no held document bounds%s" % (ref, pin, v[:30], fmw))
    return dict(nodes=nodes, fixed=fixed, res=res, diodes=diodes, inj=inj, gates=gates, vcc=vcc, ceil=ceil, cands=cands, pulls=pulls,
                lifts=lifts, unsure=unsure, absent=absent, named=named, leaks=leaks, stated=stated)


def fail_safe(boards, s):
    """dict(fail, undecided, boards, absent) for the asserted line `s` in its fail-safe states (see above)."""
    fail, und, named, absent = [], [], set(), set()
    carriers = [k for k, nl in sorted(boards.items()) if nl is not None and s in nl["nets"]]
    if not carriers: return dict(fail=fail, undecided=und, boards=named, absent=absent)
    # the line's conductor over the ribbons, and the ribbons it uses
    cond, used, todo = set(), set(), [(k, s) for k in carriers]
    while todo:
        k, n = todo.pop()
        if (k, n) in cond: continue
        cond.add((k, n))
        nl = boards.get(k)
        for ref, pin, _f in (nl["nets"].get(n, []) if nl else []):
            mate, _w = _mate(k, ref)
            if not mate: continue
            k2, r2 = mate
            mi = [i for i, m in enumerate(MATES) if (k, ref) in (m["a"], m["b"])][0]
            if boards.get(k2) is None:
                absent.add(k2); continue
            used.add(mi)
            n2 = boards[k2]["pin"].get((r2, pin), "")
            if not _dead(n2): todo.append((k2, n2))
    src = {(k, ref): why for k, n in cond for ref, why in _line_sources(boards[k], n)}
    used = sorted(used)
    results = {}
    for mask in range(1 << len(used)):
        cut = {used[i] for i in range(len(used)) if mask >> i & 1}
        # the line's fragments with these ribbons out
        lk = {}
        for k, n in cond: lk.setdefault(k, set()).add(n)
        parent = {k: k for k in lk}

        def root(x):
            while parent[x] != x: x = parent[x]
            return x
        for i in used:
            if i in cut: continue
            a, b = MATES[i]["a"][0], MATES[i]["b"][0]
            if a in parent and b in parent: parent[root(a)] = root(b)
        frags = {}
        for k in lk: frags.setdefault(root(k), set()).add(k)
        for frag in frags.values():
            # the source's board is unpowered in every fragment that carries it: powered, it drives the line, which is
            # the census's question and not a fail-safe state
            down = {k for k, _r in src if k in frag}
            key = (frozenset(frag), frozenset(down), frozenset(cut))
            if key in results: continue
            line = sorted(x for x in cond if x[0] in frag)
            r = _fs_bound(boards, s, line, down, cut, src)
            if r.get("na") or r["ok"] is True:
                results[key] = r; continue
            # THE WHOLE-BOARD STATES (the review's enumeration, round 6 second pass): every subset of the fragment's
            # other boards unpowered, solved exactly. They name a physical state for the board authors, and one that
            # fails fails the line whatever the bound says.
            others = sorted(set(frag) - down)
            phys = []
            for m2 in range(1 << len(others)):
                d2 = set(down) | {others[i] for i in range(len(others)) if m2 >> i & 1}
                e = _fs_state(boards, s, line, d2, cut, src)
                if not e.get("na"): phys.append((d2, e))
            bad = [(d2, e) for d2, e in phys if e["ok"] is False]
            if bad:
                bad.sort(key=lambda de: -(de[1].get("v") or 0))
                shown = "; ".join("%s %.2f V" % (_boards_named(frag, d2), e.get("v") or 0) for d2, e in bad[:3])
                r = dict(r, ok=False, text=("%s. The whole-board state%s that also fail%s: %s" % (
                    r["text"] if r["ok"] is False else "%s; an exact whole-board state fails as well" % r["text"],
                    "s" if len(bad) > 1 else "", "" if len(bad) > 1 else "s", shown))[:1600],
                    boards=r["boards"] | set().union(*[e["boards"] for _d, e in bad]))
            results[key] = r
    for r in results.values(): absent |= r["absent"]
    states = sorted(results.items(), key=lambda kv: (len(kv[0][2]), -len(kv[0][0]), sorted(kv[0][0])))
    states = [(k, r) for k, r in states if not r.get("na")]         # the simplest states first
    bad = [(k, r) for k, r in states if r["ok"] is False]
    unsure = [(k, r) for k, r in states if r["ok"] is None]
    for (frag, down, cut), r in bad[:3]:
        fail.append("with %s: %s" % (_state_name(frag, down, cut), r["text"])); named |= set(frag) | r["boards"]
    if len(bad) > 3:
        fail.append("and %d more fail-safe state(s) of %s fail as well" % (len(bad) - 3, s))
    if not bad:
        for (frag, down, cut), r in unsure[:3]:
            und.append("with %s: %s" % (_state_name(frag, down, cut), r["text"])); named |= set(frag) | r["boards"]
    return dict(fail=fail, undecided=und, boards=named, absent=absent)


def _boards_named(frag, down):
    up = sorted(set(frag) - set(down))
    if not down: return "board%s %s powered" % ("s" if len(up) > 1 else "", ", ".join(up))
    return "board%s %s unpowered%s" % ("s" if len(down) > 1 else "", ", ".join(sorted(down)),
                                        (" and %s powered" % ", ".join(up)) if up else "")


def _state_name(frag, down, cut):
    """The state a fail-safe result is for: the ribbons out, the source's board unpowered, and the boards on the
    conductor's fragment. Every OTHER part is bounded (_fs_bound), which the result's own text says."""
    parts = []
    if cut: parts.append("%s unplugged" % " and ".join("the %s-%s ribbon %s" % (MATES[i]["a"][0], MATES[i]["b"][0], MATES[i]["a"][1])
                                                      for i in sorted(cut)))
    if down: parts.append("board %s unpowered (the line's source there is off)" % ", ".join(sorted(down)))
    if not parts: parts.append("no source on the line at all")
    return "%s, boards %s" % ("; ".join(parts), ", ".join(sorted(frag)))


def _near(line, net):
    """The (board, net) nodes the line reaches through resistors: the nets whose readers the line decides."""
    near, todo = set(line), list(line)
    while todo:
        x = todo.pop()
        for a, b, _r in net["res"]:
            for p, q in ((a, b), (b, a)):
                if p == x and isinstance(q, tuple) and q not in near and q not in net["fixed"]:
                    near.add(q); todo.append(q)
    return near


def _judge_fs(net, judged, s, frag, how, exact=False):
    """dict(ok, text, boards, v) for one solved fail-safe network read at the reader nodes `judged`. `how` says which
    power model the voltage is for; `exact` marks a whole-board state (_fs_state) rather than the bound (_fs_bound)."""
    named = net["named"]
    got, on, got2 = _solve_net(net)
    if got is None:
        return dict(ok=None, text="the network could not be solved (%s)" % on, boards=named, v=None)
    # a reader whose supply is outside the range VIL_LOW is stated for is not judged at it (review minor 3)
    off_range = ["%s (VCC %s)" % (lab, ("%g V" % vv) if vv is not None else "not named")
                 for x in judged for lab, (ok, vv) in net["vcc"].get(x, []) if not ok]
    vl = [got.get(x) for x in judged]
    if any(x is None for x in vl):
        return dict(ok=False, text="%s floats at %s: nothing on the conductor holds it low" % (
            s, ", ".join("; ".join(net["gates"][x]) for x in judged if got.get(x) is None)), boards=named | set(frag), v=None)
    vmax = max(vl)
    detail = "pull-downs %s; %s; pin currents %s" % (
        ", ".join(net["pulls"]) or "none", ("sources: " + "; ".join(net["lifts"] + on)) if (net["lifts"] or on) else "nothing lifts it",
        ", ".join(net["leaks"]) or "none")
    bound = "%s: %s; ideal one-way elements, no forward drop; every pin's stated current, %s; pulls to a fixed node at " \
            "the adverse end of their tolerance (%g percent where the value states none) and rails %g percent high; series " \
            "resistors and a maker's own pull nominal" % ("the whole-board state" if exact else "the bound", how,
                                                          LEAK_COLUMN, TOL_DEFAULT * 100, RAIL_TOL * 100)
    if vmax >= VIL_LOW and got2 is not None and all((got2.get(x) is not None and got2.get(x) < VIL_LOW) for x in judged):
        return dict(ok=None, text="%s rises to %.2f V only if a part whose orientation is not drawn points the way that "
                    "lifts it (%s); %s" % (s, vmax, "; ".join(x for x in on if ASSUMED in x), detail)[:1400],
                    boards=named | set(frag), v=vmax)
    in_range = [x for x in judged if all(ok for _l, (ok, _v) in net["vcc"].get(x, []))]

    def strict(x):
        # THE READERS JUDGED AT VIL_LOW ON A NODE: every reader but a logic one whose supply is off VCC_RANGE (round 6
        # fourth pass: the node used to be exempt as a whole once ONE of its readers was off the range, so an in-range
        # gate or a switch enable beside it at 0.8 V or more read UNDECIDED instead of FAIL)
        off = {l for l, (ok, _v) in net["vcc"].get(x, []) if not ok}
        return [g for g in net["gates"].get(x, []) if g not in off]
    top = [x for x, vv in zip(judged, vl) if vv >= VIL_LOW and strict(x)]
    if top:
        return dict(ok=False, text="%s rises to %.2f V (%s), at or above the %.1f V VIL of the gates that read it (%s); %s" % (
                        s, max(got[x] for x in top), bound, VIL_LOW, "; ".join(g for x in top for g in strict(x))[:300],
                        detail)[:1400], boards=named | set(frag), v=max(got[x] for x in top))
    # A READER OFF THE RANGE IS STILL REFUSED WHERE NO VCC READS THE LINE AS LOW (R4T-D45): at or above its family's
    # vil_ceiling, whatever its supply is
    over = [(x, lab, c) for x in judged if x not in in_range for lab, c in net.get("ceil", {}).get(x, [])
            if c is not None and got[x] >= c and any(lab == l2 and not ok for l2, (ok, _v) in net["vcc"].get(x, []))]
    if over:
        return dict(ok=False, text="%s rises to %.2f V (%s), at or above the highest VIL any supply voltage gives the gates "
                    "that read it (%s), so it is not a logic low whatever their supply; %s" % (
                        s, max(got[x] for x, _l, _c in over), bound, "; ".join("%s %.2f V" % (lab, c) for _x, lab, c in over)[:300],
                        detail)[:1400], boards=named | set(frag), v=max(got[x] for x, _l, _c in over))
    if net["unsure"] or off_range:
        return dict(ok=None, text="%s reads %.2f V from the currents that are known (%s), and %s" % (
            s, vmax, how, "; ".join((["a reader whose supply is outside %g V to %g V, where the %.1f V VIL is stated: %s"
                                      % (VCC_RANGE[0], VCC_RANGE[1], VIL_LOW, ", ".join(off_range))] if off_range else [])
                                    + net["unsure"][:4])), boards=named | set(frag), v=vmax)
    return dict(ok=True, text="%s reads %.2f V (%s); %s" % (s, vmax, bound, detail), boards=set(), v=vmax)


def _fs_base(boards, line, down, cut, src):
    """The rail model of a fail-safe state: the boards in `down` unpowered, the ribbons in `cut` unplugged."""
    live_rail = {}

    def rail_up(k, n):
        # a rail on an unpowered board stays up only when a plugged ribbon joins it to a powered board's rail
        if k not in down: return True
        if (k, n) in live_rail: return live_rail[(k, n)]
        live_rail[(k, n)] = False
        nl = boards[k]
        for ref, pin, _f in nl["nets"].get(n, []):
            mate, _w = _mate(k, ref)
            if not mate: continue
            mi = [i for i, m in enumerate(MATES) if (k, ref) in (m["a"], m["b"])][0]
            k2, r2 = mate
            if mi in cut or boards.get(k2) is None: continue
            n2 = boards[k2]["pin"].get((r2, pin), "")
            if n2 and rail_up(k2, n2): live_rail[(k, n)] = True; break
        return live_rail[(k, n)]
    # the line's own source is off in these states: an open toggle is absent, and a logic source is an unpowered part
    # whose Ioff the network counts
    toggles = {x for x in src if re.match(r"^SW", x[1])}
    return dict(rail_up=rail_up, board_up=lambda k: k not in down, cut=cut, sources=toggles, off=set(src) - toggles)


def _fs_state(boards, s, line, down, cut, src):
    """One whole-board fail-safe state, solved EXACTLY: the network seen from the line's own (board, net) nodes `line`
    (one fragment of its conductor), with the boards in `down` unpowered, every other board powered, and the ribbons in
    `cut` unplugged. The verdict comes from _fs_bound; this names the physical state that shows a failure."""
    frag = sorted({k for k, _n in line})
    net = _network(boards, list(line), 0, _fs_base(boards, line, down, cut, src))
    # WHAT THE LINE DECIDES IS THE GATES IT REACHES: the powered gate inputs on its own nets or behind a series
    # resistor from them. A fragment with none (the panel on its own once unplugged, where only a controller's sense
    # pin sits on the line) un-inhibits nothing, so it is not judged.
    near = _near(line, net)
    judged = sorted(x for x in near if net["gates"].get(x))
    if not judged:
        return dict(ok=True, na=True, text="no powered gate reads %s on these boards" % s, boards=set(), absent=net["absent"])
    r = _judge_fs(net, judged, s, frag, "%s, every part powered exactly when its board is" % _boards_named(frag, down), exact=True)
    return dict(r, absent=net["absent"])


def _fs_bound(boards, s, line, down, cut, src):
    """The fail-safe verdict for one fragment of the line (see "EVERY OTHER PART IS TAKEN POWERED OR UNPOWERED" above):
    for each reader, the network with that reader's own supply up and every other part at the worse of its powered and
    unpowered states; the worst reading of them all. A reader's domain is its supply_of() key: its live supply nets, or
    itself (_SELF) when none of its supply is on the netlist, so no reader falls into the empty domain (R4T-D41)."""
    frag = sorted({k for k, _n in line})
    base = _fs_base(boards, line, down, cut, src)
    net0 = _network(boards, list(line), 0, dict(base, domain=frozenset()))
    near = _near(line, net0)
    doms = sorted({d for d, items in net0["cands"].items() if any(x in near for x, _l in items)},
                  key=lambda d: sorted(d))
    fixed_readers = [x for x in near if net0["gates"].get(x)]           # readers with no supply of their own (a FET gate)
    if not doms and not fixed_readers:
        return dict(ok=True, na=True, text="no gate that can be powered reads %s on these boards" % s, boards=set(),
                    absent=net0["absent"])
    runs = []
    for d in (doms or [frozenset()]):
        net = _network(boards, list(line), 0, dict(base, domain=d)) if d else net0
        judged = sorted(x for x in _near(line, net) if net["gates"].get(x))
        if not judged: continue
        how = ("with %s and every other part at the worse of its powered and unpowered current" % (
            " and ".join(("%s's %s powered (none of its supply pins is on the netlist)" % (k, r[len(_SELF):]))
                         if r.startswith(_SELF) else "%s's %s up" % (k, r) for k, r in sorted(d))) if d else
            "every part at the worse of its powered and unpowered current")
        runs.append(_judge_fs(net, judged, s, frag, how))
    absent = net0["absent"]
    if not runs:
        return dict(ok=True, na=True, text="no gate that can be powered reads %s on these boards" % s, boards=set(), absent=absent)
    bad = [r for r in runs if r["ok"] is False]
    if bad:
        return dict(max(bad, key=lambda r: r.get("v") or 99), absent=absent)
    und = [r for r in runs if r["ok"] is None]
    if und:
        return dict(max(und, key=lambda r: r.get("v") or 0), absent=absent)
    return dict(max(runs, key=lambda r: r.get("v") or 0), absent=absent)


# ---------------------------------------------------------------- a gate that loses its own supply (R4T-F9)
# RULED IN SCOPE BY THE REVIEW OF THE SECOND FIX-UP (26 September 2026, blocking 2; taken as the evidence recommends
# under the owner's standing rule of 26 Sep 2026). RF-002's "the inhibit is asserted by the unpowered and disconnected
# states" also covers the GATE's own supply. A logic part whose VCC fails stops driving its output, so the enable or
# keying pin it drove is held only by what else is on that net, and TI's switch sheets forbid exactly that: "This pin
# cannot be left floating and must be driven either high or low" (TPS22810, SLVSDH0C 9.3.1), "Do not leave floating"
# (TPS2596x, SLVSET8A, Pin Functions). Board B's LIME_EN, RB_EN and E22_EN are driven only by U19 on +3V3_DEV while
# their switches take +5V_DEV, and board D's SA_PTT_n only by U13 on +3V3_D8 while the SA868 runs on +5V_SA.
#
# What is judged, for every accepted path: each element on it that has a supply of its own (a logic gate's VCC pin's
# net whatever its name, R4T-D41; a level shifter's gate rail) is taken down, one rail at a time with the rails a bead or a 0 Ohm link joins to it, and
# the path is followed again. An element whose supply is down drives nothing, so the net it drove must be HELD at the
# level EMCON forces there by what else is on it (a passive pull, against every pin's stated current, the dead
# element's own Ioff included), judged at the threshold of whatever reads it next: the next gate's VIL or VIH (TI's
# LVC sheets, 0.8 V and 2.0 V at VCC 3 V to 3.6 V), a switch enable's stated off level, or the level the transmitter's
# maker states for its pin. A reader that is itself down leaves the question to the next element. The state is not
# judged when the transmitter loses its own supply with the element (a shared rail, or for a supply switch its input
# rail): it cannot transmit then. A pin held only by its maker's own pull is the maker's "left floating", and a
# threshold no document states leaves the path UNDECIDED. Since round 6's second pass the held net's network is the
# bound of _fs_bound: the reader and the transmitter run, the dead element is off, and any other part on the net is
# taken powered or unpowered, whichever is worse (board D's U14 on PA_EN, over the harness from board A, is one), with
# resistors and rails at the adverse end of their tolerance (R4T-D36).
LOGIC_KINDS = ("AND", "OR", "NAND", "NOR", "INV", "BUF", "BUF_OD", "INV_OD", "OD_REL")


def _rail_conductor(boards, k, rail):
    """{(board, net)} of a rail and every rail a bead, an inductor or a 0 Ohm link joins to it, across the ribbons. A
    supply whose name has no '+' is a rail here too (R4T-D41)."""
    out, todo = set(), [(k, rail)]
    is_supply = _supply_test(boards)
    while todo:
        kk, n = todo.pop()
        if (kk, n) in out: continue
        out.add((kk, n))
        nl = boards.get(kk)
        if nl is None: continue
        for ref, pin, _f in nl["nets"].get(n, []):
            ps = pins_of(nl, ref)
            if len(ps) == 2 and (re.match(r"^(L|FB)\d", ref) or (re.match(r"^R\d", ref) and _ohms(value(nl, ref)) == 0)):
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if is_supply(kk, m2): todo.append((kk, m2))
                continue
            mate, _w = _mate(kk, ref)
            if mate and boards.get(mate[0]) is not None:
                n2 = boards[mate[0]]["pin"].get((mate[1], pin), "")
                if is_supply(mate[0], n2): todo.append((mate[0], n2))
    return out


def _pull_rails(nl, net):
    """The supply nets a two-pin resistor joins `net` to (its pull-ups), ground left out (R4T-D46)."""
    is_supply = _supply_test({"_": nl})
    out = set()
    for ref, pin, _f in nl["nets"].get(net or "", []):
        ps = pins_of(nl, ref)
        if not (re.match(r"^R\d", ref) and len(ps) == 2): continue
        m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
        if is_supply("_", m2): out.add(m2)
    return sorted(out)


def _element(nl, k, got, n):
    """(ref, kind, [its own supply rails] or None when it has none of its own) for the element that drives path net n."""
    g = got[n]
    ref = g["driver"][0] if g["driver"] else None
    kind = g["kinds"][-1] if g["kinds"] else None
    if kind == "OD_REL" and fet_of(nl, ref) is not None:
        # a FET EMCON holds off has no supply of its own: what holds the level it releases is its net's pull-ups, so the
        # rails they go to are its supplies here (R4T-D46): with one of them down the released net is held by nothing
        return ref, kind, _pull_rails(nl, n)
    if kind in LOGIC_KINDS: return ref, kind, _supply_nets(nl, ref)     # its VCC pin, whatever the net is named
    if kind == "LS":
        q = nfet_pins(nl, ref)
        return ref, kind, [nl["pin"].get((ref, q["G"]), "")] if q else []
    return ref, kind, None                                   # a series resistor or a switch to ground: no supply of its own


def _threshold(nl, k, reader, level, anchor_opt):
    """dict(pass_v, fail_v, why) for the level a held net must reach for `reader` to read it EMCON's way: level 0
    passes under pass_v and fails at or above fail_v, level 1 passes at or above pass_v and fails under fail_v, and
    between the two (or with no stated level) it is undecided. reader: ("logic", ref) | ("fet", ref) | ("ls", ref) |
    ("switch", record) | ("anchor", None)."""
    kind, x = reader
    if kind == "logic":
        ok, vc = _vcc_ok(nl, x)
        if not ok:
            # VIL_LOW and VIH_HIGH are the LVC figures at VCC 3 V to 3.6 V (round 6 second pass, review minor 3); held
            # low, the line still fails at the family's vil_ceiling, which no supply voltage reads as low (R4T-D45)
            ceil = (logic_of(nl, x) or {}).get("vil_ceiling") if level == 0 else None
            return dict(pass_v=None, fail_v=ceil, why="%s runs from %s, outside the %g V to %g V at which the LVC sheets "
                        "state VIL 0.8 V and VIH 2.0 V%s" % (x, ("%g V" % vc) if vc is not None else "a rail whose name "
                                                            "states no voltage", VCC_RANGE[0], VCC_RANGE[1],
                                                            (", and no supply voltage reads %g V or more as low" % ceil) if ceil else ""))
        gap = (logic_of(nl, x) or {}).get("vih_gap") if level == 1 else None
        if gap:
            # A SCHMITT FAMILY WHOSE SHEET STATES VT+ AT VCC 3 V AND 4.5 V ONLY (EQ-18, stream w3t, 27 September 2026): the
            # 74LVC1G17 and the SN74LVC1G57. Their 4.5 V row is above VIH_HIGH, so a net held HIGH at their input is not
            # shown to read high anywhere in VCC_RANGE: it never passes, and it still fails under VIH_HIGH as any gate's does
            return dict(pass_v=None, fail_v=VIH_HIGH, why="the VIH of %s, which its sheet does not state over VCC %g V to %g V: "
                        "%s" % (x, VCC_RANGE[0], VCC_RANGE[1], gap))
        v = VIL_LOW if level == 0 else VIH_HIGH
        return dict(pass_v=v, fail_v=v, why="the %s of %s (TI's LVC sheets, VCC 3 V to 3.6 V)" % ("VIL" if level == 0 else "VIH", x))
    if kind == "fet":
        # THE FET'S THRESHOLD IS A 25 C FIGURE (round 6 second pass, review minor 4): the JSCJ 2N7002 states Vth(GS) 1.0
        # to 2.5 V at Ta 25 C only, as it does its IGSS, which R4T-D28 refuses. Vth falls as the part warms, so a hold
        # under the 25 C minimum is not proved OFF over the envelope: level 0 never passes here, and fails only at or
        # above the 25 C maximum. At level 1 (SW_GND: the gate held high to pull its drain low, the only case a path
        # produces) it passes only at the VGS the on resistance is stated at and fails under the 25 C minimum, which
        # can refuse a FET that would conduct warm and cannot pass one that would not.
        f = fet_family(nl, x)
        if not f: return dict(pass_v=None, fail_v=None, why="no held sheet states %s's threshold" % x)
        if level == 0:
            return dict(pass_v=None, fail_v=f["vth"][1], why="%s's Vth(GS), stated at 25 C only (%s)" % (x, f["cite"][:60]))
        # ON: guaranteed only at the VGS its on resistance is stated at; off at 25 C under Vth(GS) minimum
        return dict(pass_v=f["ron_vgs"], fail_v=f["vth"][0], why="%s's on resistance, stated only at VGS %g V, and its "
                    "Vth(GS) minimum %g V (25 C)" % (x, f["ron_vgs"], f["vth"][0]))
    if kind == "ls":
        return dict(pass_v=None, fail_v=None, why="%s is a level shifter that passes the net on, and a hold through it is "
                    "not modelled" % x)
    if kind == "switch":
        if x is None or level != 0:
            return dict(pass_v=None, fail_v=None, why="the switch's off level is not a low one this file knows")
        return dict(pass_v=x["en_off"], fail_v=x["en_off"], why="the %s enable's stated off level (%s)" % (x["name"], x["off_cite"]))
    v = (anchor_opt or {}).get("v_safe")
    if v is not None: return dict(pass_v=v, fail_v=v, why="the level its maker states")
    return dict(pass_v=None, fail_v=None, why="its maker states no input threshold for this pin")


def own_supply(boards, walks, k, opt, lv, anchor_pin, anchor_dead_rails):
    """(fail, undecided) for the accepted path lv on board k with each of its elements' own supply down (R4T-F9).
    anchor_pin (ref, pin) is the pin the path ends on; anchor_dead_rails are the (board, net) rails whose loss takes
    the transmitter down with the element (its own supply, or a supply switch's input)."""
    nl = boards[k]; got = walks[k][0]
    nets = lv["nets"]
    fail, und = [], []
    elems = [_element(nl, k, got, n) for n in nets[1:]]
    states = {}
    for (ref, kind, rails) in elems:
        if rails is None: continue
        if not rails:
            und.append("%s drives the path and has no supply pin on the netlist, so what it does when its supply "
                       "fails cannot be judged" % ref); continue
        for r in rails:
            states.setdefault(frozenset(_rail_conductor(boards, k, r)), r)
    order = sorted(states.items(), key=lambda kv: kv[1])
    # THE RELEASED STATE (round 6 second pass): an open-drain element EMCON releases drives nothing while EMCON is on,
    # with every rail up, so what it released is judged the same way as a dead element's net
    rel_refs = {ref for ref, kind, _r in elems if kind == "OD_REL"}
    if rel_refs: order.append((frozenset(), None))
    for dead, rname in order:
        if dead & set(anchor_dead_rails):
            continue                                           # the transmitter loses its supply with the element
        dead_keys = {(kk, n) for kk, n in dead}
        released = set(rel_refs) if rname is None else set()

        def rail_up(kk, n, _d=dead_keys): return (kk, n) not in _d
        # A FET EMCON HOLDS OFF STAYS OFF WHILE WHAT DRIVES ITS GATE IS UP (R4T-D46): its gate is the previous net of the
        # path (or the asserted line itself), so in a state where only its pull-up rail is down it is still off, and the
        # net it released is held by nothing, not pulled to ground through a channel the solve would take as on
        for i_, (r_, k_, rl_) in enumerate(elems):
            if k_ == "OD_REL" and fet_of(nl, r_) is not None:
                prev = elems[i_ - 1] if i_ else None
                if prev is None or prev[2] is None or not prev[2] or any(rail_up(k, x) for x in prev[2]):
                    released.add(r_)

        def alive(ref, kind, rails, _rel=released):
            if ref in _rel: return False                       # released by EMCON: it drives nothing
            # no supply of its own (a resistor, a switch to ground), or none on the netlist (already named undecided)
            if not rails: return True
            return any(rail_up(k, r) for r in rails)
        # EVERY OTHER PART IS BOUNDED (round 6 second pass): the reader and the transmitter run, the dead element is
        # off, and anything else on the held net is taken at the worse of powered and unpowered, as in _fs_bound
        base = dict(rail_up=rail_up, board_up=lambda kk: True, cut=set(), sources=set())
        j = 0
        while j < len(elems):
            ref, kind, rails = elems[j]
            if alive(ref, kind, rails):
                j += 1; continue
            # the element that drives nets[j + 1] is down: the net is held only by what else is on it. Its reader is
            # the next element after any series resistors, or the anchor.
            j2 = j + 1
            while j2 < len(elems) and elems[j2][1] == "R": j2 += 1
            n_read = nets[j2]                                  # the net the reader sits on (after the resistors)
            lvl = got[nets[j + 1]]["level"]
            if j2 < len(elems):
                r2, k2, rails2 = elems[j2]
                if not alive(r2, k2, rails2):
                    j = j2; continue                           # the reader is down too: the next element decides
                reader = ("logic", r2) if k2 in LOGIC_KINDS else ("fet", r2) if k2 == "SW_GND" else ("ls", r2)
            else:
                sw = switch_of(nl, anchor_pin[0]) if opt["kind"] == "power" else None
                reader = ("switch", sw) if sw else ("anchor", None)
            th = _threshold(nl, k, reader, lvl, opt)
            amodel = {}
            if opt["kind"] != "power" and opt.get("pin_model"):
                amodel[(k, anchor_pin[0], anchor_pin[1])] = opt["pin_model"]
            elif opt["kind"] != "power":
                amodel[(k, anchor_pin[0], anchor_pin[1])] = {}
            r_ref = reader[1] if reader[0] in ("logic", "fet", "ls") else anchor_pin[0]
            # the reader's own supply is up: a logic part's VCC pin, a switch's input (never its output), or the part
            # itself when none of its supply is on the netlist (R4T-D41)
            dom = frozenset()
            if reader[0] in ("logic", "switch"):
                dom = frozenset((k, r) for r in _supply_nets(nl, r_ref) if rail_up(k, r)) or frozenset({(k, _SELF + r_ref)})
            st = dict(base, domain=dom, on={(k, anchor_pin[0])} if opt["kind"] != "power" else set(),
                      released={(k, x) for x in released})
            net = _network(boards, [(k, nets[j + 1])], lvl, st, anchors=amodel)
            got_v, on, got2 = _solve_net(net)
            if rname is None:
                where = "with EMCON on, the open-drain %s is released and %s is held only by what else is on it" % (ref, nets[j + 1])
            elif kind == "OD_REL" and fet_of(nl, ref) is not None:
                where = ("with %s down (the rail %s's released net is pulled up to, and every rail it feeds through a bead "
                         "or a link), %s is held only by what else is on it" % (rname, ref, nets[j + 1]))
            else:
                where = ("with %s's supply %s down (and every rail it feeds through a bead or a link), %s no longer drives "
                         "%s" % (ref, rname, ref, nets[j + 1]))
            if got_v is None:
                und.append("%s, and the network could not be solved (%s)" % (where, on)); break
            vv = got_v.get((k, n_read))
            if vv is None:
                fail.append("%s: %s floats, nothing on it holds it %s (the reader: %s)" % (
                    where, n_read, "LOW" if lvl == 0 else "HIGH", th["why"]))
                break
            if net["stated"] and not _reaches_fixed((k, n_read), net["res"], net["fixed"], net["stated"]):
                fail.append("%s: %s is held only by its maker's own pull, which is the pin left floating (%.2f V)"
                            % (where, n_read, vv)); break
            detail = "pulls %s; pin currents %s" % (", ".join(net["pulls"]) or "none", ", ".join(net["leaks"]) or "none")
            fv, pv = th["fail_v"], th["pass_v"]
            bad_at = lambda x: x is not None and fv is not None and ((lvl == 0 and x >= fv) or (lvl == 1 and x < fv))
            if bad_at(vv) and got2 is not None and not bad_at(got2.get((k, n_read))):
                und.append("%s: %s sits at %.2f V only if a part whose orientation is not drawn points the adverse way (%s)"
                           % (where, n_read, vv, "; ".join(x for x in on if ASSUMED in x))); break
            if bad_at(vv):
                fail.append("%s: %s sits at %.2f V, %s %.2f V, %s; %s" % (
                    where, n_read, vv, "at or above" if lvl == 0 else "under", fv, th["why"], detail)); break
            passed = pv is not None and ((lvl == 0 and vv < pv) or (lvl == 1 and vv >= pv))
            if not passed or net["unsure"]:
                und.append("%s: %s sits at %.2f V from the currents that are known, and %s" % (
                    where, n_read, vv, "; ".join(([th["why"]] if not passed else []) + net["unsure"][:3]))); break
            j = j2
    return fail, und


# ---------------------------------------------------------------- the transmitters (CONOPS section 4b)
_CM5_WL = ("Raspberry Pi Compute Module 5 datasheet, release 3 (v2/vendor/cm5/cm5-datasheet.pdf), section 2.1.1: "
           "'When driven or tied low (logic 0), the pin prevents Wi-Fi from powering up ... to physically disable "
           "Wi-Fi'; pin 89 WL_nDisable. The pin 'may only be driven low; it can't be driven high. The software "
           "driver drives it high internally when required', and it is 'Internally pulled up through 1.8 kOhm to "
           "CM5_3.3V'")
_CM5_BT = ("Raspberry Pi Compute Module 5 datasheet, release 3, section 2.1.2: 'When driven or tied low (logic 0), the "
           "pin prevents Bluetooth from powering up ... to physically disable Bluetooth'; pin 91 BT_nDisable. The "
           "pin 'may only be driven low; it can't be driven high. The software driver drives it high internally "
           "when required', and it is 'internally pulled up through 1.8 kOhm to CM5_3.3V'")
_CM5_VBAT = ("Raspberry Pi Compute Module 5 datasheet, release 3, pinout table: '76 VBAT RTC battery input 2.5 V to 3.5 V; "
             "typically 3 V', and section 2.12.2: 'Supply 2.5 V to 3.5 V to power the on-board RTC. Provides backup power "
             "for RTC so that it can keep time even when the board is off'. The module's 'main power input' is its 5V pins "
             "(77, 79, 81, 83, 85 and 87, '4.75 V to 5.25 V'), so losing VBAT does not stop its radios")
_AW_NONE = ("no maker document states what W_DISABLE1# does on this card: AsiaRF's AW7915-AED datasheet "
            "(v2/vendor/wifi/asiarf-AW7915-AED-datasheet.pdf) does not mention the pin, and the mainline mt7915 "
            "driver has no code for it (adjudication A11). It counts once the card's supply is gated or the pin is "
            "proved on the bench (owner ruling D-05, 26 September 2026)")
TRANSMITTERS = [
    dict(name="LimeSDR Mini 2.4 in its USB 3 bay", options=[dict(board="B", ref="J_LIME", kind="power")]),
    dict(name="RockBLOCK 9704 (Iridium)", options=[dict(board="B", ref="J_RB9704", kind="power")]),
    dict(name="E22-900M30S LoRa", options=[dict(board="B", ref="U12", kind="power")]),
    dict(name="E72 CC2652P Zigbee coordinator", options=[dict(board="B", ref="U13", kind="power")]),
    dict(name="E72 CC2652P OpenThread RCP", options=[dict(board="B", ref="U14", kind="power")]),
    dict(name="RM520N-GL 5G module", options=[
        dict(board="B", ref="J_M2C2", kind="rf_disable", pin="8", func=r"W_DISABLE1", safe=0,
             cite="Quectel RM520N-GL Hardware Design v1.0 (v2/vendor/quectel), section 4.4.1: 'Driving it LOW will set "
                  "the module to airplane mode. In airplane mode, the RF function will be disabled.'",
             pin_model=dict(pull=(1.8, 100e3))),        # the same document's pin table: pulled up to 1.8 V through 100 kOhm
        dict(board="B", ref="J_M2C2", kind="power")]),
    dict(name="AW7915-AED WiFi link card, slot 1", options=[
        dict(board="B", ref="J_M2C1", kind="rf_disable", pin="56", func=r"W_DISABLE1", safe=0, cite=None, uncited=_AW_NONE),
        dict(board="B", ref="J_M2C1", kind="power")]),
    dict(name="AW7915-AED WiFi link card, slot 3", options=[
        dict(board="B", ref="J_M2C3", kind="rf_disable", pin="56", func=r"W_DISABLE1", safe=0, cite=None, uncited=_AW_NONE),
        dict(board="B", ref="J_M2C3", kind="power")]),
] + [dict(name="Compute Module 5 slot S%d on-module %s" % (s, radio), options=[
        dict(board="B", ref="U%dA" % (29 + s), kind="rf_disable", pin=pin, func=fn, safe=0, cite=cite, drive="open_drain",
             pin_model=dict(pull=(3.3, 1.8e3)),       # "Internally pulled up through 1.8 kOhm to CM5_3.3V"; "Can be left floating"
             backup_pins=("76",), backup_cite=_CM5_VBAT)])
     for s in (1, 2, 3) for radio, pin, fn, cite in (("WiFi", "89", r"WL_nDisable", _CM5_WL),
                                                     ("Bluetooth", "91", r"BT_nDisable", _CM5_BT))] + [
    dict(name="SA868 VHF exciter", options=[
        dict(board="D", ref="U2", kind="key", pin="5", func=r"PTT", safe=1,
             cite="NiceRF SA868 datasheet v1.3 (v2/vendor/nicerf), pin table: pin 5 PTT, 'Module Input, "
                  "Transmitting/receiving control, \"0\" force the module to enter TX state; and \"1\" to Rx state'",
             # the same sheet states no input current, no internal pull and no '1' level for PTT (round 6): a hold of
             # this pin with its driver unpowered can FAIL (floating, or a pull on a rail that dies with the driver)
             # and cannot PASS until NiceRF states them or the bench measures them
             pin_model=None, v_safe=None)]),
    dict(name="30 W VHF power amplifier (RA30H1317M1 on the plate)", options=[dict(board="A", ref="J_PA", kind="power")]),
    dict(name="QMX HF transceiver", options=[dict(board="A", ref="J_HF", kind="power")]),
]

# A part whose value names a radio and which is not the radio's supply or keying point, with why.
ACCESSORIES = [
    dict(board="B", ref="J_GNSS2", value=r"LG290P UART2", why="the GNSS receiver's bench UART header"),
    dict(board="B", ref="J_ZBDBG1", value=r"CC2652P cJTAG", why="a cJTAG bench header of an E72, on the gated +3V3_ZB"),
    dict(board="B", ref="J_ZBDBG2", value=r"CC2652P cJTAG", why="a cJTAG bench header of an E72, on the gated +3V3_ZB"),
    dict(board="D", ref="J_PAIN", value=r"PA drive", why="the PA's RF input coax; the PA's supply is board A's J_PA"),
    dict(board="D", ref="J_PAOUT", value=r"PA output", why="the PA's RF output coax; the PA's supply is board A's J_PA"),
    dict(board="D", ref="J_VGG", value=r"PA gate bias", why="the PA's gate-bias lead, switched on this board by "
         "PA_KEY; the PA's supply is board A's J_PA, which is the gate this table relies on"),
]
# A declaration that rests on an inference, not on a maker statement: the part is not unclassified, and it is not
# proved either, so its board stays UNDECIDED until the statement is held (review fix-up of round 4, 26 September
# 2026). The QMX manual gives the DC connector's range ("The supply voltage range for QMX is 6.0 to 12.0V", operating
# manual 1.04.004, v2/vendor/qrp-labs, page 8) and describes the USB-C connector only as a sound card and serial port
# (page 9); it does not say that 5 V on USB cannot run the transmitter, and VBUS_QMX stays live under EMCON.
OWED = [
    dict(board="B", ref="J_QMX", value=r"QMX USB lead", why="the QMX's USB data lead",
         owed="a QRP Labs statement that USB VBUS does not power the QMX's transmitter, or VBUS_QMX switched off by "
              "EMCON on board B; until then the QMX's hardware gate (board A's J_HF) covers only its DC input"),
]
RECEIVE_ONLY = [
    dict(board="B", ref="U11", value=r"LG290P", why="a GNSS receiver (Quectel LG290P); it has no transmitter"),
    dict(board="E", ref="J_DCF", value=r"DCF77 receiver", why="a DCF77 time-signal receiver"),
    dict(board="E", ref="J_LTG", value=r"AS3935 lightning", why="the AS3935 lightning sensor, a receiver"),
]
# The vocabulary a radio is found by. Parts that only MENTION a radio (a logic gate whose value names what it gates,
# an expander, a USB bridge) are not radios and are left out by family.
RADIO = re.compile(r"SA868|RM520|AW79\d\d|\bE22-|\bE72-|CC26\d\d|RockBLOCK|RB9704|\b9603\b|LimeSDR|\bQMX\b|RA30H|"
                   r"CM5\d{3}|LG290|DCF77|AS3935|SX12\d\d|SX127\d|ESP32|nRF52|Wio-SX", re.I)
NOT_A_RADIO = re.compile(r"74(LVC|HC|AHC)\w*|PCA95\d\d|CP210\d|TUSB\d|PI7C|KSZ\d", re.I)
SUPPLY_FN = re.compile(r"^(VCC\w*|VDD\w*|VIN\w*|VBAT\w*|VBUS\w*|PWR\w*|3\.3V|3V3\w*|5V\w*|V\+|\+.+)$", re.I)
OUTPUT_FN = re.compile(r"^(V?OUT\d*|VO\d*|OUTPUT\d*|SW\d*|LX\d*|PH\d*)$", re.I)


def _supply_name(n):
    """A net whose name says it is a supply: a '+' rail, or VDD, VCC, VIO, 3V3 or 1V8 in the name."""
    return bool(n) and (is_rail(n) or bool(re.search(r"(^|_)(VDD|VCC|VIO|VBUS)|3V3|3\.3V|1V8|5V0|(^|_)5V($|_)", n, re.I)))


def _anchor_rails(nl, opt):
    """Every supply the anchor takes: a net whose name is a rail, or a net on a pin whose function names a supply
    (review fix-up of round 4, 26 September 2026: the first version read only '+' nets). A pin the option lists in
    `backup_pins` is left out: its maker says it only keeps something alive while the part is off (the Compute Module 5's
    VBAT, pin 76, the RTC battery), so losing it does not take the transmitter down (round 6 fourth pass, R4T-D44)."""
    ref = opt["ref"]
    if opt.get("supply_pins"):
        return sorted({nl["pin"].get((ref, p), "") for p in opt["supply_pins"]} - {""})
    out = set()
    backup = {str(p) for p in opt.get("backup_pins") or ()}
    for p in pins_of(nl, ref):
        n = nl["pin"][(ref, p)]
        if _dead(n) or is_ground(n) or p in backup: continue
        if is_rail(n) or SUPPLY_FN.match(nl["func"].get((ref, p), "") or ""): out.add(n)
    return sorted(out)


SHUNT_MAX_OHM = 1.0


def _source_switch(nl, rail, _hop=True):
    """(switch ref, switch record, how, path) for the part whose OUTPUT is this rail, directly or through one inductor,
    and since round 6's fourth pass also behind one current-sense shunt (a resistor under SHUNT_MAX_OHM, R4T-D47: board
    B's +3V3_M2C1 and +3V3_M2C3 are the card sockets' side of R165 and R365, 5 mOhm, from the AP64500 bucks' +3V3_S1A and
    +3V3_S3A). `path` is dict(nets, refs): the nets from the switch to the rail and the parts that join them, which the
    second-feed check reads as the conductor and not as feeds; _second_sources() adds every net a shunt or a 0 Ohm link
    joins to them, either way (R4T-D49: a switch found by a sense pin on the rail has an empty path, and the stage's own
    node behind its sense resistor is still part of the rail)."""
    for ref, pin, _f in nl["nets"].get(rail, []):
        sw = switch_of(nl, ref)
        if sw and pin in sw["out"]: return ref, sw, "%s pin %s is its output" % (ref, pin), dict(nets=[rail], refs=set())
    for ref, pin, _f in nl["nets"].get(rail, []):
        if re.match(r"^L\d", ref) and len(pins_of(nl, ref)) == 2:
            other = [p for p in pins_of(nl, ref) if p != pin][0]
            for r2, p2, _ in nl["nets"].get(nl["pin"].get((ref, other), ""), []):
                sw = switch_of(nl, r2)
                if sw and p2 in sw["sw"]:
                    return r2, sw, "%s pin %s switches it through %s" % (r2, p2, ref), dict(nets=[rail], refs={ref})
    if _hop:
        for ref, pin, _f in nl["nets"].get(rail, []):
            ps = pins_of(nl, ref)
            ohm = _ohms(value(nl, ref)) if re.match(r"^R\d", ref) and len(ps) == 2 else None
            if ohm is None or not 0 < ohm < SHUNT_MAX_OHM: continue
            up = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
            sref, sw, how, path = _source_switch(nl, up, _hop=False)
            if sref:
                return sref, sw, "%s, then through the shunt %s (%s)" % (how, ref, value(nl, ref)[:16]), \
                    dict(nets=path["nets"] + [rail], refs=path["refs"] | {ref})
    return None, None, "no switch this file knows has its output on %s" % rail, dict(nets=[rail], refs=set())


def _load_only(nl, net, via):
    """[] when every part on `net` besides `via` can only take current off it (a capacitor, a resistor to ground or to
    nothing, a diode or LED with its anode here and its cathode on ground or on nothing), else the parts that are not
    shown to be loads, named (R4T-D43: a net only NAMED like a supply at the far end of a resistor from a gated rail)."""
    out = []
    for ref, pin, fn in nl["nets"].get(net, []):
        if ref == via or re.match(r"^(#|TP|C\d)", ref): continue
        ps = pins_of(nl, ref)
        if len(ps) == 2:
            o = ps[1] if ps[0] == pin else ps[0]
            far = nl["pin"].get((ref, o), "")
            if re.match(r"^R\d", ref) and (is_ground(far) or _dead(far)): continue
            if re.match(r"^(D|LED)\w*", ref) and fn == "A" and nl["func"].get((ref, o)) == "K" and (is_ground(far) or _dead(far)):
                continue
        out.append("%s pin %s (%s)" % (ref, pin, value(nl, ref)[:30]))
    return out


# THE MAKERS' OWN SUPPLY PINS OF THE PARTS FIRMWARE SETS (round 6 sixth pass, R4T-D50, correcting R4T-D49; corrected in
# the seventh pass, R4T-D51 and R4T-D52; each taken by the session under the owner's standing rule of 26 Sep 2026). A part
# whose pins firmware sets (software_io) may run from a gated rail, and a pin its maker's table gives as a supply INPUT is
# then a load; a pin the same table gives as a supply OUTPUT is a source that EMCON does not switch. R4T-D49 told the two
# apart by a pattern on the pin's NAME (_POWER_FN), which read "CM5_3.3V" as a supply the part runs from, where the Compute
# Module 5 datasheet makes it a regulator output of up to 600 mA, and which read any name merely ENDING in a supply word
# (GPIO24_VBUS, ADC_VIN, SENSE_3V3) as a load. Now a pin is a load only when the row of a held pin table says so, per
# family, in the maker's words:
#   inputs    supply inputs (or fixed-direction inputs, the CP2102N's VBUS) by the maker's table: a load, unless another
#             pin of the same row sits on a live net off the rail's conductor (R4T-D51 (e): a part's pins of one supply
#             are joined inside it, so it can carry that net onto the rail), which is UNDECIDED. The row's other pins are
#             every pin the maker's number places in it, whatever the symbol calls them (R4T-D54, round 6 eighth pass): the
#             seventh pass kept only those whose symbol agreed, so a sibling misnamed or unnamed on another net was dropped
#             and the split read PASS; such a pin off the conductor is now UNDECIDED, named with its number, its row and
#             the symbol's name. The same holds for a tied pin's partner;
#   outputs   supply outputs by the maker's table: a feed, FAIL on the conductor;
#   tied      {pin: (partner, words)}: an input only while `partner`, a pin of the same part, sits on the rail's conductor
#             (the net itself, the nets of the switch-to-rail path, or a net a 0 Ohm link or a shunt joins to one of
#             them, R4T-D51 (d)); with the partner on another live net the pin is what `words` say firmware can make it,
#             and FAILS; with the partner on ground, unconnected or not drawn, UNDECIDED; with a partner the maker's number
#             places there but the symbol names otherwise on another live net, UNDECIDED, named (R4T-D54). Since the
#             seventh pass (R4T-D51) this holds both parts' VBAT: the STM32H7's is tied to VDD (a battery charger firmware
#             switches on, VDD to VBAT through 5 or 1.5 kOhm) and the Compute Module 5's to its 5V (the RTC's 3 mA
#             constant-current, constant-voltage charger, switched on from config.txt);
#   reverse   {pin: [(partner, words[, options]), ...]} (R4T-D55, round 6 eighth pass; a list since R4T-D57, the ninth
#             pass): a supply INPUT the maker joins to each `partner` inside the part by a stated requirement, the STM32H7's
#             VDD to its VBAT through the battery charger (DS12110 Figure 15 and Table 95), to its VDDA, VDD33USB and
#             VDD50USB by the power sequence of 3.5.1 (Figure 3, 'Invalid supply area') and to its VDDLDO by Table 24's
#             'VDDLDO <= VDD' (R4T-D60, the tenth pass), its VDDA to its VREF+ (Tables 87 and 89, R4T-D62), a CP2102N's
#             VREGIN to its VDD and VIO, and a Compute Module 5's 5V to its GPIO_VREF (2.9 and 3.1, R4T-D61): a load only
#             while EVERY partner sits on the rail's conductor, on ground, unconnected or not drawn; with any partner on
#             another live net UNDECIDED, naming each such partner and the maker's words for its join. The option
#             own_outputs=True (the Compute Module's GPIO_VREF) also accepts a partner on a net fed only by the part's own
#             supply outputs made from a supply on the rail (_own_fed);
#   named     names the table knows only to find a partner (the STM32H7's VDD33USB, R4T-D57; a CP2102N's VIO, R4T-D62): a
#             pin by such a name is never a row, and on the rail it is UNDECIDED with the words given for it;
#   sense     rows the table lists among `inputs` that the maker calls a signal, not a supply (the CP2102N's VBUS, 'Digital
#             Input. VBUS Sense Input', and one of the 'non-power' pins of Table 3.10): on the rail a load, and never a
#             supply for the class below (R4T-D62);
#   independent [dict(x, y, when, words)] (R4T-D62, the tenth pass): the maker's sentences that let supply rows fall in any
#             order: an input of a row in `x` on the rail with a pin of a row in `y` on another live net is not judged by
#             the class below, provided a pin of row `when` (None for none) also sits on a live net off the conductor
#             (the STM32H7's 'When VDD is above 1 V, all power supplies are independent': VDD must stay up for it to
#             hold). A `reverse` row is never excused by it: a stated requirement is read before a general sentence;
#   output_from {output: (row, ...)} (R4T-D61, R4T-D62): the supply row each supply OUTPUT is made from, the first the part
#             has a pin of (the Compute Module 5's CM5_3.3V and CM5_1.8V from its 5V, 3.1 and 3.4; the RP2040's
#             VREG_VOUT from VREG_VIN, Table 1; the STM32H7's VCAP from VDDLDO, or from VDD where the package has no
#             VDDLDO pin, 3.5.1 and Table 9 note 8). A net carrying such an output whose row has a pin on the rail's
#             conductor, and nothing else that can feed it (_net_sources), goes down with the rail (_own_fed);
#   backfeed  {supply input: (pin-name pattern, what they are, words)} (R4T-D58, the ninth pass): pins the maker joins to
#             that supply inside the part, the PCA9555's P-port pins through the 100 kOhm pull-up of SCPS131J Figure 8-2 and
#             the RP2040's ADC inputs through the ESD diodes of its datasheet's 2.9.5. The input is UNDECIDED while such a
#             pin sits on a live net off the rail's conductor where anything besides the part is not shown to be a load
#             (_load_only: a capacitor, a resistor to ground or nothing, an LED or diode with its anode there and its
#             cathode on ground), since whatever holds that pin up feeds the rail;
#   io        [dict(supply, free, words)] (R4T-D68, the eleventh pass): every other pin of the part that is no supply of it (no
#             row, no supply or ground word, no `backfeed` pin), read when one of `supply` is the input on the rail: on a live
#             net off the rail and off every net fed only by the part's own outputs made from it, where _net_sources() finds
#             something that can hold it up, the input is UNDECIDED with `words`, the maker's limit on such a pin with its
#             supply off (RP2040 Table 622, STM32H7 Tables 21 and 22, CP2102N Table 3.10, CM5 4.2.1). `free` names the pins
#             the maker states pass no current then (the RP2040's fault-tolerant pins, Table 614; the PCA9555's INT and
#             address pins, rated to 6 V whatever VCC is with a clamp only below 0 V, SCPS131J 6.1; its SCL until the twelfth
#             pass, R4T-D73), and `free_words` their words, which a PASS carries when such a pin is held up (R4T-D73);
#   outside   {output: words} (R4T-D67): the maker's words for its own supply output held up from outside, which an
#             `independent` sentence then does not excuse (the RP2040's VREG_VOUT, 2.9.7.2; the STM32H7's VCAP);
#   grounds   the part's ground: on a gated rail it returns whatever powers the part onto the rail (FAIL);
#   numbers   {pin number: table name} for a part whose maker numbers its pins once, whatever carries them (the
#             Compute Module 5: board B's receptacles carry the module's own pin numbers, 1 to 100 on A, 101 to 200
#             on B). An output by number FAILS whatever the symbol calls it. An input or a tied pin by number is that
#             row only when the symbol's pin function names the same row, or is only the net's name (a generated
#             symbol); a symbol that calls pin 77 anything else disagrees with the maker, and the pin is UNDECIDED, named
#             (R4T-D52: a symbol numbered from the wrong side is not read as the module's 5V).
# A family is found by the part itself (R4T-D52, _is_part): its library symbol's name, or the start of its value after at
# most a maker's name, or, for the Compute Module, a receptacle's "(CM5 pins" form. A value that only MENTIONS a family
# does not make the part one (board B's PCIe switches say "up = CM5 lane", its KSZ9897 "ports 1-3 the CM5 slots"); since
# R4T-D53 such a part is not passed either: an active pin of it on a path or a gated rail is UNDECIDED, named. A pin
# whose whole name is a supply word (_SUPPLY_WORD, anchored: VDD, AVDD, VDD3P3, 3V3, a '+' name) on a part with no table
# here, or one its table does not list, is UNDECIDED, named, and so is a pin named only after its net (a generated
# symbol); a pin named as a ground FAILS as the part's ground; any other name is a pin firmware can drive, and FAILS. A
# false FAIL or UNDECIDED is named and seen; a false load is silent, so nothing is a load without a row.
# EVERY OTHER SUPPLY PIN OF THE PART IS READ (round 6 tenth pass, R4T-D62, the review of the ninth pass's suggestion; taken by
# the session under the owner's standing rule of 26 Sep 2026). The ninth pass read a supply input's joins only where a
# `reverse` or `backfeed` row named them, and each review found one more (VDDLDO beside VDD, GPIO_VREF beside the module's
# 5V). Now a supply input on the rail is UNDECIDED while ANY other supply pin of the part (a row in `inputs`, `tied`,
# `named` or `outputs`, or a pin whose name is a supply word the table does not place) sits on a live net off the rail's
# conductor, unless that net is fed only by the part's own outputs made from a supply on the rail (`output_from`), or a
# maker's sentence in `independent` lets the two fall in that order; `sense` rows and pins a `backfeed` row reads are left
# to those rows. Since the eleventh pass (R4T-D67) such a sentence excuses an OUTPUT of the part only while nothing else feeds
# its net (`outside`), a load that rests on one is named in the PASS it gives (fw_pin_role() returns its words, the power
# option's text quotes them), and a net fed only by the part's own outputs is read before any sentence is; and every I/O of
# the input's domain is read (`io`, R4T-D68).
# THE MAKERS' WORDS THE ROWS BELOW QUOTE (the tenth pass). Each names the page of the held file it comes from.
_W_VDDLDO = ("the held sheets bound VDDLDO by VDD: Table 24 'General operating conditions' gives VDDLDO, 'Supply voltage for "
             "the internal regulator', the operating condition 'VDDLDO <= VDD' (the sheet prints the less-than-or-equal "
             "sign; DS12110 Rev 10 6.3.1 Table 24, page 106; DS12117 Rev 9 6.3.1 Table 23, page 106), and 'When it is not "
             "available on a package, the VDDLDO pin is internally tied to VDD' (DS12110 Rev 10 Table 9 note 8, page 87; "
             "DS12117 Rev 9 Table 8 note 8, page 87); with the rail's switch open and VDD falling, VDDLDO stands above VDD, "
             "outside the maker's condition, and no held page says whether the part then passes that supply out through "
             "its VDD pins onto the rail")
_W_VREF = ("the held sheets bound VREF+ by VDDA: 'VREF+ Positive reference voltage', maximum VDDA (DS12110 Rev 10 6.3.20 "
           "Table 87 'ADC characteristics', page 168, and 6.3.21 Table 89 'DAC characteristics', page 173; DS12117 Rev 9 "
           "Tables 86 and 88, pages 168 and 173); with the rail's switch open and VDDA falling, a reference held from "
           "elsewhere stands above it, outside the maker's condition, and no held page says whether the part then passes it "
           "out through its VDDA pins onto the rail")
_W_STM_IND = ("DS12110 Rev 10 3.5.1, page 28 (DS12117 Rev 9 3.5.1, page 27): 'When VDD is above 1 V, all power supplies are "
              "independent', which Figure 3 draws as 'VDDX independent from VDD'; the supplies are those 3.5.1 lists (VDD, "
              "VDDLDO, VDDA, VDD33USB, VDD50USB, VBAT, VCAP), and for VDDLDO against VDD Table 24's 'VDDLDO <= VDD' (page "
              "106) holds as VDDLDO falls")
_W_RP_IND = ("RP2040 Datasheet 2.9.6 Power Supply Sequencing (page 152): 'RP2040's power supplies may be powered up or down in "
             "any order' (the transient it names in the ADC supply is limit (4)); 2.9.5 (page 152): 'It is safe to supply "
             "ADC_AVDD at a higher or lower voltage than IOVDD'; and the regulator output pin 'must be connected to the "
             "chip's DVDD pins off-chip' (2.9.7.1, page 152), so VREG_VOUT's net is DVDD's")
_W_GPIO_VREF = ("the module's maker ties GPIO_VREF to the module's own supplies and bounds any other supply on it by them: "
                "'GPIO_VREF must be connected to either CM5_3.3v or CM5_1.8v. It's possible to use 2.5 V signalling by "
                "supplying an external 2.5 V supply to GPIO_VREF. This external supply must only be active while CM5_1.8v "
                "is on and must be fully discharged within 1 ms after CM5_1.8v is going low' (CM5 datasheet 2.9, page 11), "
                "and 'No pins should be powered before the 5 V rail is active' (3.1 Power-up sequencing, page 15; 4.2.1, "
                "page 23: 'when CM5 is powered-down or off, there must be no external voltage applied to any pin'); with "
                "the rail's switch open the module's 5V and its CM5_1.8V go down while that net stays up, which the maker "
                "forbids, and no held page says whether the GPIO bank then passes it out through the module's 5V pins onto "
                "the rail")
_W_CM5_VBAT_IND = ("CM5 datasheet 2.12.2 Table 3 'System control signals' (page 14): VBAT 'Provides backup power for RTC so "
                   "that it can keep time even when the board is off' and 'A typical CR2032 lasts > 3 years when CM5 is "
                   "unpowered'; 4.3.3 (page 27): IVBAT 'RTC current', 6 uA typical at Vin = 0 V, into the pin")
_W_CP_VDD = ("the output of its 5 V regulator whenever VREGIN is powered (CP2102N Rev 1.5 Table 3.6, page 12: VREGOUT 'Output "
             "Voltage on VDD'; note 1: 'If the 5 V voltage regulator is not used, VREGIN should be tied to VDD'), and no held "
             "page says whether the regulator conducts from its output back to its input once VREGIN falls with the rail "
             "while VDD is held from elsewhere")
_W_CP_VIO = ("the held sheet bounds VIO by VDD: 'Operating Supply Voltage on VIO', 1.71 V minimum and VDD maximum (CP2102N Rev "
             "1.5 Table 3.1 Recommended Operating Conditions, page 10; note 3: 'On devices without a VIO pin, VIO = VDD'); "
             "with the rail's switch open and VDD falling with VREGIN, VIO stands above VDD, outside the maker's condition, "
             "and no held page says whether it then leaves through VREGIN onto the rail")
_W_CP_VBUS = ("CP2102N Rev 1.5 2.3 USB (page 8): 'the absolute maximum voltage on the VBUS pin, which is defined as VIO + 2.5 V "
              "in Table 3.10 Absolute Maximum Ratings ... the current limitation of the resistor divider prevents high VBUS "
              "pin leakage current, even though the VIO + 2.5 V specification is not strictly met while the device is not "
              "powered' (Table 3.10, page 15, and 'On devices without a VIO pin, VIO = VDD'), so whatever holds VBUS up once "
              "EMCON has opened the rail's switch drives current into the unpowered part, and no held page says where that "
              "current goes")
# THE MAKERS' WORDS FOR A LEVEL HELD ON AN I/O OF THE PART WHILE THE SUPPLY OF THAT I/O FALLS (round 6 eleventh pass, R4T-D68;
# the rows' `io`). Each names the page of the held file it comes from; printed page numbers.
_W_RP_IO = ("RP2040 Datasheet 5.5.3.1 Table 622 (page 614): 'Voltage at IO' at most 'IOVDD + 0.5' V, where 5.5.2 Table 614 (page "
            "612) says only of the fault-tolerant pins that 'very little current flows into the pin whilst it is below 3.63V and "
            "IOVDD is 0V' (GPIO0 to GPIO25, SWCLK, SWD and RUN, Tables 615, 618 and 619, pages 612 and 613); the QSPI pins, "
            "TESTEN, XIN, XOUT and the USB pins are not fault-tolerant, so with the rail's switch open and IOVDD falling a level "
            "held on one of them stands above that limit, and no held page says what it then passes into the part's supply")
_W_STM_IO = ("DS12110 Rev 10 6.2 Table 21 (page 104): 'Input voltage on FT_xxx pins' at most 'Min(VDD, VDDA, VDD33USB, VBAT) +4.0' "
             "V, with note 4: 'To sustain a voltage higher than 4V the internal pull-up/pull-down resistors must be disabled', "
             "and Table 22 note 3 (page 105): 'Positive injection is not possible on these I/Os and does not occur for input "
             "voltages lower than the specified maximum value' (DS12117 Rev 9, the same rows); no held page states what an I/O "
             "whose internal pull-up firmware has enabled passes into VDD once VDD falls, and whether each pin is FT or TT is in "
             "the pin table, which this file does not read")
_W_CP_IO = ("CP2102N Rev 1.5 Table 3.10 Absolute Maximum Ratings (page 15): 'Voltage on UART pins, GPIO, VBUS, RSTb, or any other "
            "non-power, non-USB pin' at most 'VIO+2.5' V where VIO is below 3.3 V, and 'Voltage on D+ or D-' at most 'VDD+0.3' V; "
            "with the rail's switch open VDD and VIO fall with VREGIN, a level held on such a pin stands above that limit, and no "
            "held page says what it then passes into the part's supply (2.3 says it only of VBUS behind its divider)")
_W_PCA_IO = ("TI SCPS131J 6.1 Absolute Maximum Ratings (page 5): 'IIOK Input/output clamp current', 'VO < 0 or VO > VCC', "
             "+-20 mA, a clamp above VCC on the part's input/output pins that the table does not assign pin by pin; and 6.3 "
             "Recommended Operating Conditions (page 5) gives SCL and SDA a VIH maximum of VCC with note (1): 'For voltages "
             "applied above VCC, an increase in ICC will result', so an SCL or SDA held up by the bus once VCC falls with the "
             "rail passes current into the part's supply, and no held page says how much or where it goes")
# THE PINS ITS MAKER DECIDES (R4T-D68, `free`; since the twelfth pass, R4T-D73, the words that clear them are carried into the
# PASS when such a pin is held up)
_W_PCA_FREE = ("TI SCPS131J Table 5-1 (page 4): INT 'Interrupt output. Connect to VCC through a pullup resistor.', A0 to A2 "
               "'Address input'; 6.1 (page 5): VI and VO -0.5 V to 6 V, IIK only for 'VI < 0' and IOK only for 'VO < 0'; 6.3 "
               "(page 5): A2-A0 VIH maximum 5.5 V, with no note on voltages above VCC")
_W_RP_FREE = ("RP2040 Datasheet 5.5.2 Table 614 (page 612): of the fault-tolerant pins, 'very little current flows into the pin "
              "whilst it is below 3.63V and IOVDD is 0V' (GPIO0 to GPIO25, SWCLK, SWD and RUN, Tables 615, 618 and 619)")
_W_CM5_IO = ("CM5 datasheet 4.2.1 (page 23): 'Reverse voltage. Don't apply reverse voltage on any pin. This means that when CM5 is "
             "powered-down or off, there must be no external voltage applied to any pin, otherwise CM5 might not power up again'; "
             "with the rail's switch open the module's 5V falls, a level held on one of its pins is what the maker forbids, and "
             "no held page says what that pin then passes into the module")
FW_PIN_TABLES = [
    dict(family="RP2040", ident=r"RP2040\b",
         inputs=("IOVDD", "DVDD", "ADC_AVDD", "USB_VDD", "VREG_VIN"),
         outputs={"VREG_VOUT": "'Power output for the internal core voltage regulator, nominal voltage 1.1V, 100mA max "
                               "current'"},
         grounds=("GND",),
         # R4T-D58: the ADC inputs leak into IOVDD through their ESD diodes whenever they sit above it
         backfeed={"IOVDD": (r"^GPIO(26|27|28|29)(?:[_/]?ADC[0-3])?$", "ADC input",
                             "RP2040 Datasheet 2.9.5 ADC Supply (page 152): 'the voltage on the ADC analogue inputs must "
                             "not exceed IOVDD ... Voltages greater than IOVDD will result in leakage currents through the "
                             "ESD protection diodes', so anything that holds such a pin up once EMCON has opened the rail's "
                             "switch feeds IOVDD, and the rail, through those diodes")},
         # R4T-D62: the maker lets every supply fall in any order, and the core regulator runs from VREG_VIN
         independent=[dict(x=("IOVDD", "DVDD", "ADC_AVDD", "USB_VDD", "VREG_VIN"),
                           y=("IOVDD", "DVDD", "ADC_AVDD", "USB_VDD", "VREG_VIN", "VREG_VOUT"), when=None, words=_W_RP_IND)],
         output_from={"VREG_VOUT": ("VREG_VIN",)},
         # R4T-D68: every I/O of the IOVDD and USB_VDD domains held up elsewhere, but the fault-tolerant pins the maker states
         io=[dict(supply=("IOVDD", "USB_VDD"), free=r"^(GPIO([0-9]|1[0-9]|2[0-5])|SWCLK|SWD|SWDIO|RUN)$", words=_W_RP_IO,
                  free_words=_W_RP_FREE)],
         # R4T-D67: the maker's words for its regulator's output held up from outside
         outside={"VREG_VOUT": "RP2040 Datasheet 2.9.7.2 External Core Supply (page 153) rules out: 'If an external core "
                               "supply is used, the output of on-chip voltage regulator (VREG_VOUT) should be left "
                               "unconnected', and 2.10.2.2 High Impedance Mode (page 156) allows two regulators on its load "
                               "only 'with only one regulator supplying the load at a time'"},
         cite="RP2040 Datasheet (v2/vendor/rp2040/rpi-rp2040-datasheet.pdf, build-version 3184e62-clean), 1.4.2 Pin "
              "Descriptions, Table 1: IOVDD 'Power supply for digital GPIOs', USB_VDD 'Power supply for internal USB Full "
              "Speed PHY', ADC_AVDD 'Power supply for analogue-to-digital converter', VREG_VIN 'Power input for the "
              "internal core voltage regulator', DVDD 'Digital core power supply'; VREG_VOUT the regulator's output; GND "
              "'Single external ground connection'; 2.9.5, 2.9.6 and 2.9.7.1 (page 152) for the order the supplies may fall "
              "in"),
    # the three parts whose sheets are held (R4T-D51 (c)): the STM32H72x and H73x lines add VDDSMPS, VLXSMPS and VFBSMPS
    # under sheets not held here, so a part of theirs has no table and its supply words are UNDECIDED
    dict(family="STM32H7", ident=r"STM32H7(?:42|43|53)",
         inputs=("VDD", "VDDLDO", "VDDA", "VDD50USB"),
         outputs={"VCAP": "'VCAP: VCORE supply voltage' (3.5.1), the internal regulator's output"},
         tied={"VREF+": ("VDDA", "the output of the voltage reference buffer when firmware enables it (DS12110 6.3.22 "
                                 "Table 91, DS12117 Table 90: VREFBUF_OUT 'Voltage Reference Buffer Output', up to VDDA, "
                                 "Iload 4 mA, IINRUSH 8 mA, IDDA(VREFBUF) 'consumption from VDDA')"),
               "VBAT": ("VDD", "the far end of the battery charger firmware can switch on from VDD (DS12110 6.3.24 Table "
                               "95, DS12117 Table 94, 'VBAT charging characteristics': RBC 'Battery charging resistor' 5 "
                               "kOhm with VBRS in PWR_CR3 = 0 and 1.5 kOhm with VBRS = 1, about 2.2 mA from 3.3 V; the "
                               "power supply scheme, DS12110 Figure 15 and DS12117 Figure 14, draws 'VBAT charging' from "
                               "VDD; page 1: 'VBAT battery operating mode with charging capability')")},
         # R4T-D55: the same join read from the VDD side. Figure 15 draws the charger BETWEEN the two pins, a resistor with
         # no direction marked, so a live VBAT elsewhere may feed a VDD on a gated rail once firmware has switched it on.
         # R4T-D57 (round 6 ninth pass, the review of the eighth pass, blocking 2): the same section R4T-D55 cites for the
         # rows, 3.5.1, gives VDD a second join, to VDDA, VDD33USB and VDD50USB, by the power sequence the maker requires
         # (Figure 3, 'Invalid supply area'); a VDD on a gated rail with any of them live elsewhere is what EMCON makes
         reverse={"VDD": [("VBAT", "the held sheets draw the battery charger between VDD and VBAT with no direction marked "
                                   "(DS12110 Rev 10 Figure 15, page 103, 'VBAT charging', DS12117 Rev 9 Figure 14) and name "
                                   "it a resistor (DS12110 Table 95, DS12117 Table 94: RBC 'Battery charging resistor', 5 "
                                   "kOhm with VBRS in PWR_CR3 = 0 and 1.5 kOhm with VBRS = 1); neither says that it opens "
                                   "when VDD falls (RM0433, the reference manual, is not held), so once firmware has "
                                   "switched charging on, what is on VBAT can feed the rail through it after EMCON has "
                                   "opened the rail's switch, and which way it conducts is not stated")]
                         + [(_x, "the maker's power sequence ties VDDA, VDD33USB and VDD50USB to VDD: 'When VDD is below "
                                 "1 V, other power supplies (VDDA, VDD33USB, VDD50USB) must remain below VDD + 300 mV' and "
                                 "'During the power-down phase, VDD can temporarily become lower than other supplies only if "
                                 "the energy provided to the microcontroller remains below 1 mJ' (DS12110 Rev 10 3.5.1, page "
                                 "28, and Figure 3, which labels that region 'Invalid supply area', note 1: 'VDDx refers to "
                                 "any power supply among VDDA, VDD33USB, VDD50USB'; DS12117 Rev 9 3.5.1, page 27, and Figure "
                                 "2, page 28), so with the rail's switch open and VDD falling the part takes energy in from "
                                 "them beyond what the maker allows, and no held sheet says whether it leaves through the VDD "
                                 "pins onto the rail") for _x in ("VDDA", "VDD33USB", "VDD50USB")]
                         # R4T-D60 (round 6 tenth pass, the review of the ninth pass): the same sheets tie VDDLDO to VDD
                         # by Table 24's operating condition and Table 9's note 8, which the ninth pass's header denied
                         + [("VDDLDO", _W_VDDLDO)],
                  # R4T-D62: VREF+ is tied to VDDA from VDDA's side too (the maximum of Tables 87 and 89)
                  "VDDA": [("VREF+", _W_VREF)]},
         independent=[dict(x=("VDDLDO", "VDDA", "VDD50USB"),
                           y=("VDD", "VDDLDO", "VDDA", "VDD33USB", "VDD50USB", "VBAT", "VCAP"), when="VDD", words=_W_STM_IND)],
         output_from={"VCAP": ("VDDLDO", "VDD")},
         io=[dict(supply=("VDD",), free=None, words=_W_STM_IO)],                         # R4T-D68
         # R4T-D67: the held sheets describe VCAP only as the internal regulator's output
         outside={"VCAP": "the held sheets do not describe: DS12110 Rev 10 3.5.1 (page 27; DS12117 Rev 9 3.5.1) gives VCAP only "
                          "as 'VCORE supply voltage' from the internal regulator that VDDLDO supplies, and describes no supply "
                          "on VCAP from outside (RM0433, the reference manual, is not held)"},
         # VDD33USB is no row: 3.5.1 makes it the USB regulator's output or, bypassed, a supply input (R4T-D57)
         named={"VDD33USB": "is the output of the USB regulator from VDD50USB or, with that regulator bypassed, a 3.3 V "
                            "supply input ('VDD50USB can be supplied through the USB cable to generate the VDD33USB via "
                            "the USB internal regulator ... The USB regulator can be bypassed to supply directly VDD33USB', "
                            "DS12110 Rev 10 3.5.1, page 27, DS12117 Rev 9 3.5.1, page 27), so whether it takes power from "
                            "the rail or gives it is not known"},
         grounds=("VSS", "VSSA", "VREF-"),
         cite="STM32H742xI/G STM32H743xI/G datasheet DS12110 Rev 10 (v2/vendor/st/st-stm32h743xi-datasheet.pdf) and "
              "STM32H753xI datasheet DS12117 Rev 9 (v2/vendor/st/st-stm32h753xi-datasheet.pdf), the same rows in both: "
              "3.5.1 Power supply scheme: VDD 'external power supply for I/Os', VDDLDO 'supply voltage for the internal "
              "regulator supplying VCORE', VDDA 'external analog power supplies', VDD50USB 'can be supplied through the "
              "USB cable', VDD33USB the USB regulator's output or, bypassed, a supply input, VBAT 'power supply for the "
              "VSW domain when VDD is not present', and the power sequence tying VDDA, VDD33USB and VDD50USB to VDD "
              "(DS12110 Figure 3, DS12117 Figure 2); 3.19 'The voltage on the VBAT "
              "pin could be provided by an external battery, a supercapacitor or directly by VDD'; VCAP the VCORE "
              "regulator's output; VREF+ the VREFBUF output unless it shares the net of VDDA, which the buffer runs from; "
              "VBAT the charger's far end unless it shares the net of VDD, which the charger runs from; 6.3.1 Table 24 "
              "(DS12117 Table 23, page 106): 'VDDLDO <= VDD', and Table 9 note 8 (DS12117 Table 8, page 87): VDDLDO "
              "'internally tied to VDD' where a package has no such pin; Tables 87 and 89 (DS12117 86 and 88): VREF+ at "
              "most VDDA"),
    # R4T-D68: its INT and A0 to A2 take an input or output voltage of -0.5 V to 6 V whatever VCC is, with a clamp only below
    # 0 V (SCPS131J 6.1, page 5: VI, VO, IIK 'VI < 0', IOK 'VO < 0'), so the held sheet decides that they pass nothing into
    # VCC (`free`); its P-ports are the `backfeed` row's; SDA and, since the twelfth pass (R4T-D73, the review of the eleventh
    # pass: 6.3 gives SCL a VIH maximum of VCC with note (1), 'For voltages applied above VCC, an increase in ICC will
    # result'), SCL are read
    dict(family="PCA9555", ident=r"PCA9555",
         inputs=("VCC", "VDD"), grounds=("GND", "VSS"),
         io=[dict(supply=("VCC", "VDD"), free=r"^(~?\{?INT\}?|/?INT#?|A[0-2])$", words=_W_PCA_IO, free_words=_W_PCA_FREE)],
         # R4T-D58 (round 6 ninth pass, the review of the eighth pass, minor 4): the maker draws a resistor from every
         # P-port pin to VCC, so a P-port pin held up by another part is a way onto a gated rail that carries VCC
         backfeed={_x: (r"^(P[01][0-7]|IO[01]_[0-7])$", "P-port",
                        "TI SCPS131J Figure 8-2 (Simplified Schematic Of P-Port I/Os, page 15) draws a 100 kOhm resistor "
                        "between VCC and every P-port pin, whose current is 6.5's IIL, -100 uA at VI = GND (page 7), and "
                        "no held page says it opens when VCC is off, so anything that holds such a pin up feeds VCC, and "
                        "the rail, through it once EMCON has opened the rail's switch") for _x in ("VCC", "VDD")},
         cite="TI PCA9555 SCPS131J (v2/vendor/ti/ti-pca9555.pdf), Table 5-1 Pin Functions: VCC (24 on PW) 'Supply "
              "voltage', GND (12) 'Ground', P00 to P07 (4 to 11) and P10 to P17 (13 to 20) 'P-port input/output'; "
              "Figure 8-2, the P-port's pull-up to VCC; KiCad's Interface_Expansion:PCA9555PW names the same pins VDD, "
              "VSS and IO0_0 to IO1_7"),
    dict(family="CP2102N", ident=r"CP2102N",
         inputs=("VREGIN", "VBUS"), grounds=("GND",),
         tied={"VDD": ("VREGIN", "the output of its 5 V regulator whenever VREGIN is powered (Table 3.6: VREGOUT, "
                                 "'Output Voltage on VDD', 3.1 to 3.6 V at 1 to 100 mA; note 1: 'If the 5 V voltage "
                                 "regulator is not used, VREGIN should be tied to VDD')")},
         # R4T-D62 (round 6 tenth pass): the tie read from VREGIN's side, VIO where a package has one, and VBUS, a
         # 'Digital Input. VBUS Sense Input' that Table 3.10 counts among the 'non-power' pins, whose leakage into the
         # unpowered part 2.3 states
         # VDD is the regulator's output made from VREGIN (Table 3.6), so a VDD net fed by nothing else goes down with it
         reverse={"VREGIN": [("VDD", _W_CP_VDD, dict(own_outputs=True)), ("VIO", _W_CP_VIO)]},
         output_from={"VDD": ("VREGIN",)},
         named={"VIO": "is the supply of its I/O on the packages that have one, 'Operating Supply Voltage on VIO', 1.71 V to "
                       "VDD (CP2102N Rev 1.5 Table 3.1, page 10), which the QFN28 table of 5.1 does not list, so whether it "
                       "takes power from the rail or gives it is not known here"},
         sense=("VBUS",),
         backfeed={"VREGIN": (r"^VBUS$", "VBUS sense input", _W_CP_VBUS)},
         io=[dict(supply=("VREGIN",), free=None, words=_W_CP_IO)],                        # R4T-D68
         cite="CP2102N Data Sheet Rev. 1.5 (v2/vendor/silabs/silabs-cp2102n.pdf), 5.1 QFN28 Pin Definitions: VDD (6) "
              "'Supply Power Input / 5V Regulator Output', VREGIN (7) '5V Regulator Input', VBUS (8) 'Digital Input. VBUS "
              "Sense Input', GND (3) 'Ground'; Table 3.6 and its note 1; Table 3.1 (page 10): VIO 1.71 V to VDD and 'On "
              "devices without a VIO pin, VIO = VDD'; 2.3 (page 8) and Table 3.10 (page 15): VBUS among the 'non-power' "
              "pins, at most VIO + 2.5 V, and its leakage 'while the device is not powered'"),
    dict(family="Compute Module 5", ident=r"CM5\d{3}|CM5\s+(?:socket|receptacle|module|connector)\b|Compute Module 5\b",
         lib=r"CM5[AB]?$|CM5\d{3}",
         receptacle=r"\(CM5 pins \d",
         inputs=("5V", "GPIO_VREF"),
         outputs={"CM5_3.3V": "3.4 'Regulator outputs': 'can each deliver up to 600 mA of current to external devices'; "
                              "pins 84 and 86 'CM5_3.3V (Output) 3.3 V +-5%. Power output max 300 mA per pin'",
                  "CM5_1.8V": "3.4 'Regulator outputs': 'can each deliver up to 600 mA of current to external devices'; "
                              "pins 88 and 90 'CM5_1.8V (Output) 1.8 V +-5%. Power output max 300 mA per pin'"},
         tied={"VBAT": ("5V", "the output of the RTC's battery charger, 'a constant-current (3 mA) constant-voltage "
                              "charger' that firmware switches on from config.txt with rtc_bbat_vchg ('If set to 0 or not "
                              "specified, the trickle charger is disabled. (2712 only)'), at up to 4.4 V "
                              "(charging_voltage_max 4400000); the module's own device tree, bcm2712-rpi-cm5.dtsi, "
                              "includes bcm2712-rpi.dtsi, which declares rpi_rtc with trickle-charge-microvolt and the "
                              "rtc_bbat_vchg parameter")},
         # R4T-D61 (round 6 tenth pass, the review of the ninth pass): 5V is a load only with GPIO_VREF on the rail, on
         # ground, nowhere, or on the module's own CM5_3.3V or CM5_1.8V, which go down with the 5V (3.1, 3.2, 3.4)
         reverse={"5V": [("GPIO_VREF", _W_GPIO_VREF, dict(own_outputs=True))]},
         # R4T-D62: the RTC battery keeps the RTC with the module off, which is the order EMCON makes
         independent=[dict(x=("5V", "GPIO_VREF"), y=("VBAT",), when=None, words=_W_CM5_VBAT_IND)],
         output_from={"CM5_3.3V": ("5V",), "CM5_1.8V": ("5V",)},
         io=[dict(supply=("5V", "GPIO_VREF"), free=None, words=_W_CM5_IO)],              # R4T-D68
         grounds=("GND",),
         numbers={"76": "VBAT", "77": "5V", "78": "GPIO_VREF", "79": "5V", "81": "5V", "83": "5V", "84": "CM5_3.3V",
                  "85": "5V", "86": "CM5_3.3V", "87": "5V", "88": "CM5_1.8V", "90": "CM5_1.8V"},
         cite="Raspberry Pi Compute Module 5 datasheet, release 3, build date 08/06/2026 "
              "(v2/vendor/cm5/cm5-datasheet.pdf), 4.2 Pinout, Table 4: 76 VBAT 'RTC battery input', 77 to 87 odd '5V "
              "(Input) ... main power input', 78 GPIO_VREF ('The GPIO bank is powered by the GPIO_VREF supply', 2.9), 84 "
              "and 86 'CM5_3.3V (Output)', 88 and 90 'CM5_1.8V (Output)'; 3.4 'Regulator outputs'; 2.9 (page 11) and 3.1 "
              "(page 15) for GPIO_VREF and the order the supplies may rise and fall in, 4.2.1 (page 23), 2.12.2 Table 3 "
              "(page 14) and 4.3.3 (page 27) for VBAT with the module off. VBAT's charger: "
              "Raspberry Pi documentation, computers/raspberry-pi/rtc.adoc, 'Enable battery charging' "
              "(v2/vendor/cm5/doc-rtc.adoc); raspberrypi/firmware boot/overlays/README, rtc_bbat_vchg "
              "(v2/vendor/cm5/rpi-firmware-overlays-README.txt); raspberrypi/linux rpi-6.18.y, "
              "arch/arm64/boot/dts/broadcom/bcm2712-rpi.dtsi and bcm2712-rpi-cm5.dtsi "
              "(v2/vendor/cm5/linux-bcm2712-rpi.dtsi, v2/vendor/cm5/linux-bcm2712-rpi-cm5.dtsi)"),
]
_SUPPLY_WORD = re.compile(r"^((A|D|IO|P)?V(DD|CC|IN|BAT|BUS|REF|REG|SYS|IO)[A-Z0-9]*\+?|\d+(\.\d+)?V\d*|\+.+)$", re.I)
# THE SAME WORDS JOINED BY AN UNDERSCORE OR A HYPHEN (round 6 eleventh pass, R4T-D66, the review of the tenth pass, minor B5;
# taken by the session under the owner's standing rule of 26 Sep 2026): a module pin a symbol calls 'VDD_IO', or an STM32H7
# VDDA called 'VDD_A', stood outside the class, so a part on a gated rail with such a pin held up elsewhere read PASS in
# silence. The class and the own-output test read these names as supplies; a pin firmware can drive that happens to carry
# such a name ('VBUS_DET') is then UNDECIDED there, a false UNDECIDED, seen. fw_pin_role()'s last fallback, for a pin ON the
# rail, keeps _SUPPLY_WORD (such a pin there FAILS as one firmware can drive, which no name weakens).
_SUPPLY_NAME = re.compile(r"^((A|D|IO|P)?V(DD|CC|IN|BAT|BUS|REF|REG|SYS|IO)[A-Z0-9_\-]*\+?|\d+(\.\d+)?V[\d_\-A-Z]*|\+.+)$", re.I)
_GROUND_WORD = re.compile(r"^(A|D|P)?(GND|VSS)[A-Z0-9]*$", re.I)


def fw_family(nl, ref):
    """The FW_PIN_TABLES row for a part, or None (R4T-D50; by the part itself since R4T-D52): a family whose library
    symbol the part carries, else one whose part number its value begins with (after at most a maker's name), else the
    Compute Module by a receptacle's "(CM5 pins" form. A value that only mentions a family does not make the part one."""
    part = ((nl["comps"].get(ref) or {}).get("lib") or "").split(":")[-1]
    for t in FW_PIN_TABLES:
        if re.match(r"(?:%s)" % t.get("lib", t["ident"]), part, re.I): return t
    return next((t for t in FW_PIN_TABLES if _is_part(nl, ref, t["ident"], t.get("lib"), t.get("receptacle"))), None)


def _table_name(t, pin, fn):
    """(the table's name for this pin, how it was read): by the maker's pin number where the family has one, else by the
    symbol's pin function, matched whole and without regard to case; (None, None) when the table names neither."""
    num = (t.get("numbers") or {}).get(str(pin))
    if num: return num, "number"
    f = (fn or "").strip().upper()
    names = list(t["inputs"]) + list(t.get("outputs") or {}) + list(t.get("tied") or {}) + list(t.get("grounds") or ()) \
        + list(t.get("named") or {})
    return next(((n, "name") for n in names if n.upper() == f), (None, None))


def _only_net(f, net):
    """True when a pin function is only its net's name (a generated symbol)."""
    return bool(f) and bool(net) and f.lstrip("/") == net.lstrip("/")


def _row(t, nl, ref, pin, fn=None):
    """(row, how, agrees) for a pin of a part of family `t`: the table's name for it and how it was read (_table_name),
    and whether the symbol agrees. A row read by name always agrees; a row read by the maker's pin number agrees only when
    the symbol's pin function names the same row or is only its net's name (R4T-D52)."""
    f = ((nl["func"].get((ref, pin)) if fn is None else fn) or "").strip()
    name, how = _table_name(t, pin, f)
    if how != "number": return name, how, True
    return name, how, f.upper() == name.upper() or _only_net(f, nl["pin"].get((ref, pin), ""))


def _linked(nl, net):
    """`net` and every net a resistor under SHUNT_MAX_OHM (a 0 Ohm link, a current-sense shunt) joins to it, either way
    and through any number of them; ground and dead ends are not joined (R4T-D51 (d))."""
    seen, todo = {net}, [net]
    while todo:
        n = todo.pop()
        for ref, pin, _f in nl["nets"].get(n, []):
            if not re.match(r"^R\d", ref): continue
            ps = pins_of(nl, ref)
            ohm = _ohms(value(nl, ref)) if len(ps) == 2 else None
            if ohm is None or ohm >= SHUNT_MAX_OHM: continue
            m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
            if m2 in seen or _dead(m2) or is_ground(m2): continue
            seen.add(m2); todo.append(m2)
    return seen


# A NET FED ONLY BY THE PART'S OWN OUTPUTS (round 6 tenth pass, R4T-D61 and R4T-D62; taken by the session under the owner's
# standing rule of 26 Sep 2026). The Compute Module 5's GPIO_VREF "must be connected to either CM5_3.3v or CM5_1.8v" (2.9),
# both made from the module's 5V (3.1, 3.4), so a GPIO_VREF on the module's own CM5_3.3V net goes down with a gated 5V and
# is no way onto the rail, while one on an external supply stays up. What may sit on such a net besides the part, and what
# may not, is read on the net itself, in the second-feed check's words. The tenth pass differed from those words in three
# ways (the review of the tenth pass, its blocking item and minors B7 to B9), and since the eleventh pass (R4T-D63 to R4T-D65)
# none remains: another firmware part's supply input on the net is judged by fw_pin_role() with all its joins, a pull to a
# net no supply test knows is read through, and a logic part's VCC or a switch's input is read for the path its maker
# states from its outputs back. A net or part that falls with the rail (the conductor, the net judged) feeds nothing.
def _bjt_pins(nl, ref):
    """{B, C, E: pin} for a bipolar transistor whose netlist names its pins B, C and E, else None."""
    m = {nl["func"].get((ref, p), ""): p for p in pins_of(nl, ref)}
    return {k: m[k] for k in ("B", "C", "E")} if ref.startswith("Q") and all(k in m for k in ("B", "C", "E")) else None


def _anode_to_ground(nl, ref, pin, fn):
    """True for an LED's or diode's anode whose cathode is on ground or on nothing: it only takes current off its net."""
    ps = pins_of(nl, ref)
    if not (re.match(r"^(D|LED)\w*", ref) and len(ps) == 2 and fn == "A"): return False
    o = ps[1] if ps[0] == pin else ps[0]
    far = nl["pin"].get((ref, o), "")
    return nl["func"].get((ref, o)) == "K" and (is_ground(far) or _dead(far))


def _quiet_own(nl, ref, pin):
    """True for a pin of part `ref` that is no supply of it (no row of its table's supplies, no supply word)."""
    t = fw_family(nl, ref)
    row = _row(t, nl, ref, pin)[0] if t else None
    fn = (nl["func"].get((ref, pin)) or "").strip()
    if row is not None:
        return row in (t.get("outputs") or {})
    return not _SUPPLY_NAME.match(fn)


def _local(nl, ref, net, via):
    """True when `net` holds nothing but `via`, capacitors, the quiet pins of part `ref` (_quiet_own), LED or diode anodes
    whose cathode is on ground, and resistors whose far net holds only the same (one hop): a transistor whose other pins
    reach only these is powered by the part alone (board B's Q101, the module's LED_nPWR buffer, R149 from pin 95 and R150
    to LED17)."""
    if _dead(net) or is_ground(net): return True
    if is_rail(net): return False

    def quiet(r2, p2, f2, skip):
        return r2 in skip or re.match(r"^(#|TP|C\d)", r2) or (r2 == ref and _quiet_own(nl, ref, p2)) \
            or _anode_to_ground(nl, r2, p2, f2)
    for r2, p2, f2 in nl["nets"].get(net, []):
        if quiet(r2, p2, f2, {via}): continue
        ps = pins_of(nl, r2)
        if re.match(r"^R\d", r2) and len(ps) == 2:
            far = nl["pin"].get((r2, ps[1] if ps[0] == p2 else ps[0]), "")
            if _dead(far) or is_ground(far): continue
            if not is_rail(far) and all(quiet(r3, p3, f3, {r2}) for r3, p3, f3 in nl["nets"].get(far, [])): continue
        return False
    return True


# HOW DEEP THE OWN-OUTPUT READING GOES (round 6 eleventh pass, R4T-D63 and R4T-D64). _net_sources() reads the parts on a net, the
# nets behind its pulls, the supply pins of other firmware parts (through fw_pin_role(), which may read their own outputs' nets
# again) and the outputs of logic parts and switches that run from it. Each step adds one to the depth; a step that would go
# past _NS_DEPTH is a source, named as not read that deep, so the reading ends and never passes what it did not read.
_NS_DEPTH = 4


def _src_list(src):
    """The sources _net_sources() found, named for a sentence: the first three and a count of the rest."""
    return "; ".join(src[:3]) + ("; and %d more" % (len(src) - 3) if len(src) > 3 else "")


def _merge(notes, more):
    """Add the maker's words in `more` to `notes`, each once (R4T-D73)."""
    if notes is None: return
    for m in more:
        if m not in notes: notes.append(m)


def _head(cite):
    """A citation's source, the words before its first colon."""
    return (cite or "").split(":")[0]


def _module_refs(nl, ref, t):
    """[ref] and every other part that carries the same module (round 6 twelfth pass, R4T-D72; the review of the eleventh pass,
    blocking 3): board B draws each Compute Module 5 as two parts, U30A for pins 1 to 100 and U30B for pins 101 to 200, and
    the module's maker numbers its pins once, whatever carries them. A sibling shares the base designator (the reference
    without its last letter) and reads as the same family, and only a family numbered by its maker (`numbers`) has them."""
    m = re.match(r"^(.*\d)([A-H])$", ref or "")
    if not (t and t.get("numbers") and m): return [ref]
    fam = t["family"]
    return [ref] + sorted(r for r in nl["comps"] if r != ref and re.match(r"^%s[A-H]$" % re.escape(m.group(1)), r)
                          and (fw_family(nl, r) or {}).get("family") == fam)


def _held(nl, ref, n, falling, _depth, _seen, notes):
    """What _net_sources() finds able to hold net `n` up, a pin of part `ref` being on it; [] for a dead net, a ground, a net
    that falls with the rail or one already read. The words of the loads cleared there reach `notes` only when nothing does."""
    if _dead(n) or is_ground(n) or n in falling or n in _seen: return []
    tmp = []
    src = _net_sources(nl, ref, n, falling, _depth + 1, set(_seen) | {n}, notes=tmp)
    if not src: _merge(notes, tmp)
    return src


def _ground_read(nl, ref, supply_pins, what, falling):
    """A pin named as a ground, of a logic part or a switch, on a net that falls with a gated rail (R4T-D71): the part's supply
    current returns through it, so with the supply up it feeds the net (as a firmware part's ground, R4T-D50)."""
    up = [n for n in _pin_nets(nl, ref, supply_pins) if n not in falling]
    if up:
        return "feed", "is the ground of %s by its pin's name, with its supply on %s: the part's supply current returns " \
            "through it onto the net whatever the rail's switch does" % (what, ", ".join(up))
    return "undecided", "is the ground of %s by its pin's name, and its supply pin is %s, so what returns through it is not " \
        "known" % (what, "on the net as well" if _pin_nets(nl, ref, supply_pins) else "on no live net of this netlist")


def _supply_read(nl, ref, pin, sw, fam, falling, _depth, _seen, notes):
    """A logic part's VCC or a switch's input on a net that falls with a gated rail (R4T-D65; since the twelfth pass, R4T-D71,
    a load only by its maker's words, carried into the PASS). UNDECIDED where an output its maker states a path back from is
    held up (_feeds_back), or where another pin of the part is held up that no maker's word clears: a switch's enable with a
    current source out of it, its other input pins on another live net, an output of a switch with no stated reverse, any
    pin its entry does not place; an input of a logic family with no Ioff row and no statement of its inputs' clamps."""
    row = sw or fam
    what = "%s (%s)" % (ref, row["name"])
    path = (sw or {}).get("reverse") or (fam or {}).get("vcc_path")
    ioff = fam is not None and fam.get("ioff") is not None
    if _depth + 1 > _NS_DEPTH:
        return "undecided", "is the supply of %s, whose other pins are not read this deep" % what
    tmp = []
    fb = _feeds_back(nl, ref, pin, falling, _depth, _seen, notes=tmp)
    if fb: return "undecided", fb[0]
    outs = set(sw["out"]) | set(sw["sw"]) if sw else {g[1] for g in fam["gates"]}
    ins = set() if sw else {i for g in fam["gates"] for i in g[0]}
    blocks, cleared = [], []
    for p in pins_of(nl, ref):
        if p == str(pin): continue
        n, f = nl["pin"].get((ref, p), ""), (nl["func"].get((ref, p)) or "").strip()
        src = _held(nl, ref, n, falling, _depth, _seen, tmp)
        if not src: continue
        at = "its pin %s (%r) is on %s, where %s %s not shown to be unable to hold it up" % (
            p, f, n, _src_list(src), "is" if len(src) == 1 else "are")
        if sw:
            if p == sw["en"] and sw.get("en_source"):
                blocks.append("%s, and its maker states a current source at that pin (%s)" % (at, _head(sw["en_source"])))
            elif p == sw["en"] and sw.get("en_clear"):
                cleared.append("its enable (pin %s) is held on %s, and its maker states that pin only leaks (%s)" % (
                    p, n, _head(sw["en_clear"])))
            elif p == sw["en"]:
                # A SWITCH WITH NO ENABLE ROW (integration of 27 September 2026, the final check's minor: this indexed
                # sw["en_clear"] and raised KeyError for a switch added without an _EN_ROWS entry). Read as _class_pin
                # reads the same missing row: UNDECIDED, named.
                blocks.append("%s, and no held page of its maker's says what current that enable pin passes" % at)
            elif p in sw["vin"]:
                blocks.append("%s: its input row is split across two live nets" % at)
            elif p in outs:
                blocks.append("%s, and no held page of its maker's says what that output then passes into its input" % at)
            else:
                blocks.append("%s, a pin its entry here does not place" % at)
        elif p in outs or p in ins:
            if ioff: continue                                           # the Ioff row bounds it, named below
            if p in ins and fam.get("in_clamp"):
                cleared.append("its input pin %s is held on %s, and %s" % (p, n, fam["in_clamp"]))
            else:
                blocks.append("%s, and its sheet states no Ioff and nothing on its inputs' clamps, so what that pin passes into "
                              "VCC once VCC falls is not known (%s)" % (at, fam["leak_cite"]))
        else:
            blocks.append("%s, a pin its pin map here does not place" % at)
    if blocks:
        return "undecided", "is the supply pin of %s, and %s" % (what, "; ".join(blocks))
    words = "is the supply pin of %s by its maker's pin table (%s)" % (what, _head(row["cite"]))
    if ioff:
        words += ", and its maker states Ioff for the partial-power-down state, which bounds what any input or output of it " \
            "passes with VCC at 0 V (%s)" % fam["leak_cite"]
    elif path:
        words += ", and no output of it is held up by anything on its net, the only way back into it its maker states (%s)" % \
            _head(path)
    else:
        words += ", and no other pin of it is held up by anything on its net"
    if cleared: words += "; " + "; ".join(cleared)
    _merge(notes, tmp)
    return "load", words


def _class_pin(nl, ref, pin, fn, falling, _depth=0, _seen=(), notes=None):
    """(verdict, words) for a pin of a part in one of the classes this file reads by its makers' rows, a switch (SWITCHES), a
    logic part (LOGIC) or a protection part (PROTECTION_ROWS), on a net that falls with a gated rail (`falling`: the rail's
    conductor, or a net fed only by a gated part's own outputs); (None, None) for a part in none of them (round 6 twelfth
    pass, R4T-D70 and R4T-D71; the review of the eleventh pass, blocking 1 and 2; taken by the session under the owner's
    standing rule of 26 Sep 2026). verdict: "load" where a row of its maker's clears the pin, `words` being those words, which
    the caller carries into the PASS (`notes` takes the words of what the reading cleared on the nets it read); "feed" where
    it feeds the net with the rail's switch open (a switch output, a push-pull output, a ground with the part's supply up);
    "undecided" otherwise, `words` saying why. Every pin of these parts that no row clears is "undecided": a switch's pin
    other than its outputs, input and enable, a logic part's pin its map does not place, a protection part's pin other than
    VBUS, an enable whose maker states a current out of it."""
    sw = switch_of(nl, ref)
    fam = None if sw else logic_of(nl, ref)
    prot = None if (sw or fam) else protection_of(nl, ref)
    fn = (fn or "").strip()
    if sw:
        what = "%s (%s)" % (ref, sw["name"])
        if pin in sw["out"] or pin in sw["sw"]:
            return "feed", "is an output of %s" % what
        if pin in sw["vin"]:
            return _supply_read(nl, ref, pin, sw, None, falling, _depth, _seen, notes)
        if pin == sw["en"]:
            if sw.get("en_source"):
                up = [n for n in _pin_nets(nl, ref, sw["vin"]) if n not in falling]
                if sw.get("en_from_vin") and not up:
                    return "load", "is the enable of %s, whose maker states a current source out of the pin (%s), run from its " \
                        "input (%s), and its input falls with the net or is on no live net" % (
                            what, sw["en_source"], sw["en_from_vin"])
                return "undecided", "is the enable of %s, and its maker states a current sourced out of the pin: %s%s" % (
                    what, sw["en_source"], ("; its input is on %s, which stays up" % ", ".join(up)) if up else "")
            if sw.get("en_clear"):
                return "load", "is the enable input of %s, which its maker states only leaks: %s" % (what, sw["en_clear"])
            return "undecided", "is the enable of %s, and no held page of its maker's says what current the pin passes" % what
        if _GROUND_WORD.match(fn): return _ground_read(nl, ref, sw["vin"], what, falling)
        return "undecided", "is pin %s (%r) of %s, which its entry here does not place (it names the enable, the input and " \
            "the outputs), so whether it can feed the net is not known" % (pin, fn, what)
    if fam:
        what = "%s (%s)" % (ref, fam["name"])
        if fam.get("wrong_land"):
            return "undecided", "is a pin of %s on a land its pin map is not for, so which pin is an output is not known" % what
        if fam.get("unwired"):
            return "undecided", "is a pin of %s: %s" % (what, fam["unwired"])
        gate = next((g for g in fam["gates"] if g[1] == pin), None)
        if gate and gate[2] not in OPEN_DRAIN:
            return "feed", "is the push-pull output of %s" % what
        if gate:
            if not fam.get("od_words"):
                return "undecided", "is an open-drain output of %s by this file's map, and no maker's sentence held here says so" % what
            return "load", "is the open-drain output of %s, which only pulls low: %s; %s" % (what, fam["od_words"], fam["leak_cite"])
        if pin in (fam.get("vcc") or ()):
            return _supply_read(nl, ref, pin, None, fam, falling, _depth, _seen, notes)
        if any(pin in g[0] for g in fam["gates"]):
            return "load", "is an input of %s by its maker's pin map (%s), whose held sheet states only its leakage there: %s" % (
                what, _head(fam["cite"]), fam["leak_cite"])
        if _GROUND_WORD.match(fn): return _ground_read(nl, ref, fam["vcc"], what, falling)
        return "undecided", "is pin %s (%r) of %s, which its pin map here does not give as an input, an output or VCC, so " \
            "whether it can feed the net is not known" % (pin, fn, what)
    if prot:
        what = "%s (%s)" % (ref, prot["name"])
        if pin not in prot["vbus"]:
            return "undecided", "is pin %s (%r) of %s, whose row here clears only its VBUS, and only with its I/O pins held " \
                "by nothing: %s" % (pin, fn, what, prot["topology"])
        tmp, held = [], []
        for p in prot["io"]:
            n = nl["pin"].get((ref, p), "")
            if _depth + 1 > _NS_DEPTH and not (_dead(n) or is_ground(n) or n in falling):
                held.append("its I/O pin %s is on %s, which is not read this deep" % (p, n)); continue
            src = _held(nl, ref, n, falling, _depth, _seen, tmp)
            if src:
                held.append("its I/O pin %s is on %s, where %s %s not shown to be unable to hold it up" % (
                    p, n, _src_list(src), "is" if len(src) == 1 else "are"))
        if held:
            return "undecided", "is the VBUS of %s, and %s; and %s, so whatever holds an I/O up once EMCON has opened the " \
                "rail's switch feeds the net through the diode to VBUS" % (what, "; ".join(held), prot["topology"])
        _merge(notes, tmp)
        return "load", "is the VBUS of %s, and nothing holds its I/O pins up, while %s" % (what, prot["topology"])
    return None, None


def _join(what, w):
    """A pin named, then what a class reading says of it: 'what: it is ...' for _feeds_back's words, else 'what, which is ...'."""
    return ("%s: %s" if w.startswith("it is ") else "%s, which %s") % (what, w)


def _feeds_back(nl, ref, pin, falling, _depth=0, _seen=(), notes=None):
    """[why] for pin `pin` of part `ref` where it is the part's supply and the part's maker states a path from its outputs back
    into that supply, or rates an output by it (R4T-D65, the review of the tenth pass, minor L1): a logic part's VCC where its
    family has `vcc_path` (the SN74LVC08A's positive output clamps, SCAS283W 7.3.3; its, the SN74LVC32A's and the SN74LVC00A's
    outputs at most VCC + 0.5 V with no Ioff, 5.1), a switch's input where its entry has `reverse` (the TPS22810's body diode,
    SLVSDH0C 10.4; the TPS2596's and the AP64500's outputs at most their input plus 0.3 V). Each output of the part on a live net outside `falling` (the nets that fall with the rail) where
    _net_sources() finds something that can hold it up is named, with the maker's words. [] when no path is stated, when
    nothing holds an output up, or for any other pin."""
    fam, sw = logic_of(nl, ref), switch_of(nl, ref)
    if sw and pin in (sw.get("vin") or ()) and sw.get("reverse"):
        outs, words, what = list(sw.get("out") or ()) + list(sw.get("sw") or ()), sw["reverse"], sw["name"]
    elif not sw and fam and not _unmapped(fam) and pin in (fam.get("vcc") or ()) and fam.get("vcc_path"):
        outs, words, what = [o for _i, o, _k in fam["gates"]], fam["vcc_path"], fam["name"]
    else:
        return []
    held = []
    for o in sorted(set(outs), key=lambda x: (len(x), x)):
        n = nl["pin"].get((ref, o), "")
        if _dead(n) or is_ground(n) or n in falling or n in _seen: continue
        tmp = []
        src = _net_sources(nl, ref, n, falling, _depth + 1, set(_seen) | {n}, notes=tmp)
        if src:
            held.append("its output pin %s is on %s, where %s %s not shown to be unable to hold it up" % (
                o, n, _src_list(src), "is" if len(src) == 1 else "are"))
        else:
            _merge(notes, tmp)
    return ["it is the supply pin of a %s, %s, and %s" % (what, "; ".join(held), words)] if held else []


def _net_sources(nl, ref, net, on=None, _depth=0, _seen=None, notes=None):
    """[what on `net`, besides part `ref`, is not shown to be unable to feed it] (R4T-D61), each named: a resistor from a
    supply by the three tests (any value), a 0 Ohm link, shunt, bead, inductor or fuse to a live net, a diode whose cathode
    is here, a transistor channel from a net that is not ground or local to the part (_local), a transistor this file
    cannot read, a connector, a switch output, a logic gate's push-pull output or one on a land its map is not for, an
    output-named pin, a pin of a part firmware sets other than a supply input or tied pin its maker's table gives, a part
    that only mentions a firmware family, and a pin of any other part (R4T-F23's class, which is not read here either).
    Since the eleventh pass (round 6, 26 September 2026) also: ANOTHER FIRMWARE PART'S SUPPLY INPUT OR TIED PIN is judged by
    fw_pin_role() as if the net were its gated rail, with its backfeed, reverse and class readings, and any verdict but
    "load" makes it a source (R4T-D63, the review of the tenth pass, its blocking item: a PCA9555, an RP2040 or an STM32H7 on
    the module's own CM5_3.3V held GPIO_VREF's net up through a join its maker documents and read PASS); A PULL TO A NET NO
    SUPPLY TEST KNOWS is read through, the far net with these same rules, as the second-feed check reads through a
    resistor (R4T-D64, minor B7 to B9: a 1 kOhm to a regulator's output or a buffer's output read PASS); and A LOGIC PART'S
    VCC OR A SWITCH'S INPUT is a source where its maker states a path from its outputs into it and an output is held up
    (_feeds_back, R4T-D65, minor L1). `on` is the nets that fall with the rail (the rail's conductor and the net judged):
    a pull, link, diode or channel to one of them feeds nothing. A capacitor, a test point, a FET's gate, an LED's or
    diode's anode, a switch's enable, a logic gate's input or open-drain output, a logic gate's or switch's supply with no
    stated path back, and another firmware part's supply input its maker's table and joins read as a load, are not.
    SINCE THE TWELFTH PASS (R4T-D70 to R4T-D73; the review of the eleventh pass): a switch's, a logic part's and a protection
    part's pins are read by _class_pin(), so a switch's enable is a source unless its maker states it only leaks, a logic
    part's ground is a source with its supply up, and each is a load only by its maker's words, which reach `notes` (a list
    the caller carries into the PASS), as do the words of another firmware part's supply input read as a load (R4T-D73: the
    eleventh pass dropped them here, so a PASS resting on the RP2040's 2.9.6 on a module's own output did not quote it). A pin
    of any other part that carries the same module as `ref` (U30B beside U30A, R4T-D72) is the part's own, as `ref`'s are."""
    kind = _supply_test({"_": nl}).kind
    on = set(on or ())
    seen = set(_seen or ()) | {net}
    falling = on | seen
    out = []
    deep = _depth + 1 > _NS_DEPTH
    mods = set(_module_refs(nl, ref, fw_family(nl, ref)))
    for r2, p2, f2 in nl["nets"].get(net, []):
        if r2 in mods or re.match(r"^(#|TP|C\d)", r2): continue
        ps, v2 = pins_of(nl, r2), value(nl, r2)[:30]
        what = "%s pin %s (%s, %r)" % (r2, p2, v2, f2)
        if re.match(r"^R\d", r2):
            far = nl["pin"].get((r2, ps[1] if ps[0] == p2 else ps[0]), "") if len(ps) == 2 else ""
            if len(ps) == 2 and (_dead(far) or is_ground(far) or far in falling): continue
            ohm = _ohms(value(nl, r2)) if len(ps) == 2 else None
            if ohm is None: out.append("%s, a resistor this file cannot read" % what)
            elif ohm < SHUNT_MAX_OHM: out.append("%s, a link from %s" % (what, far))
            elif kind("_", far): out.append("%s, a resistor from %s, a supply" % (what, far))
            elif deep: out.append("%s, a pull to %s, which is not read this deep" % (what, far))
            else:
                # R4T-D64: read through, as _second_sources() reads through a resistor (R4T-D49)
                tmp = []
                behind = _net_sources(nl, ref, far, on, _depth + 1, seen | {far}, notes=tmp)
                if behind:
                    out.append("%s, a pull to %s, behind which %s" % (what, far, _src_list(behind)))
                else:
                    _merge(notes, tmp)
            continue
        if re.match(r"^(L|FB|F)\d", r2) and len(ps) == 2:
            far = nl["pin"].get((r2, ps[1] if ps[0] == p2 else ps[0]), "")
            if not (_dead(far) or is_ground(far) or far in falling): out.append("%s, which joins %s to it" % (what, far))
            continue
        if re.match(r"^(D|LED)\w*", r2) and len(ps) == 2:
            far = nl["pin"].get((r2, ps[1] if ps[0] == p2 else ps[0]), "")
            if f2 == "A" or _dead(far) or is_ground(far) or far in falling: continue
            out.append("%s, a diode from %s" % (what, far)); continue
        if r2.startswith("Q"):
            fq, bj = fet_of(nl, r2), _bjt_pins(nl, r2)
            if fq:
                if p2 == fq[1]["G"]: continue
                o = nl["pin"].get((r2, fq[1]["D"] if p2 == fq[1]["S"] else fq[1]["S"]), "")
                if o not in falling and not _local(nl, ref, o, r2): out.append("%s, a channel from %s" % (what, o))
            elif bj:
                others = [nl["pin"].get((r2, bj[x]), "") for x in ("B", "C", "E") if bj[x] != p2]
                if not all(o in falling or _local(nl, ref, o, r2) for o in others):
                    out.append("%s, a bipolar transistor whose other pins reach %s" % (what, ", ".join(others)))
            else:
                out.append("%s, a transistor whose type or pin map this file cannot read" % what)
            continue
        if re.match(r"^(J|P)\w*", r2):
            out.append("%s, which leaves the board" % what); continue
        sw = switch_of(nl, r2)
        if sw and (p2 in sw["out"] or p2 in sw["sw"]):
            out.append("%s, a switch output" % what); continue
        fam = None if sw else logic_of(nl, r2)
        if fam and fam.get("wrong_land"):
            out.append("%s, a gate on a land its pin map is not for" % what); continue
        if fam and fam.get("unwired"):
            out.append("%s, %s" % (what, fam["unwired"])); continue
        gate = next((g for g in fam["gates"] if g[1] == p2), None) if fam else None
        if gate and gate[2] not in OPEN_DRAIN:
            out.append("%s, the push-pull output of %s" % (what, fam["name"])); continue
        # R4T-D65, and since the twelfth pass (R4T-D70, R4T-D71) every other pin of a switch, a logic part or a protection
        # part: a load only by its maker's words, which reach `notes`
        tmp = []
        v, w = _class_pin(nl, r2, p2, f2, falling, _depth + 1, seen, notes=tmp)
        if v == "load":
            _merge(notes, tmp + ["%s on %s %s" % (what, net, w)]); continue
        if v is not None:
            out.append(_join(what, w)); continue
        if OUTPUT_FN.match(f2 or ""):
            out.append("%s, an output" % what); continue
        if software_io(nl, r2):
            t2 = fw_family(nl, r2)
            row = _row(t2, nl, r2, p2)[0] if t2 else None
            if not (t2 and (row in t2["inputs"] or row in (t2.get("tied") or {}))):
                out.append("%s, a pin of a part whose pins firmware sets" % what); continue
            # R4T-D63: a supply input or a tied pin by its maker's table, judged as on a gated rail, with its joins
            if deep:
                out.append("%s, a firmware part's supply pin whose own joins are not read this deep" % what); continue
            tmp = []
            v3, w3 = fw_pin_role(nl, r2, p2, f2, net, falling, _depth + 1, notes=tmp)
            if v3 != "load":
                out.append("%s, which %s" % (what, w3 or "the walk reads as a pin firmware can drive"))
            elif w3:                                          # R4T-D73: the maker's sentence it rests on, carried
                _merge(notes, tmp + ["%s on %s %s" % (what, net, w3)])
            else:
                _merge(notes, tmp)
            continue
        fm = fw_mention(nl, r2)
        out.append("%s, %s" % (what, ("a part whose value or symbol mentions %s and that is not read as one" % fm) if fm
                                else "a part no class here reads"))
    return out


def _own_fed(t, nl, ref, net, on, _depth=0, notes=None):
    """(True, "") when `net` carries a supply OUTPUT of part `ref` (family `t`) made from a supply row with a pin on the rail's
    conductor `on` (output_from), and nothing else on it can feed it (_net_sources): it goes down with the rail. Else
    (False, why). On True, the maker's words the reading of that net rested on reach `notes` (R4T-D73)."""
    outs = set(t.get("outputs") or {}) | set(t.get("output_from") or {})   # the CP2102N's VDD is its regulator's output
    own = sorted({_row(t, nl, ref, p)[0] for p in pins_of(nl, ref) if nl["pin"].get((ref, p)) == net} & outs)
    if not own:
        return False, "no supply output of the part itself is on it"

    def made_from(o):
        for row in (t.get("output_from") or {}).get(o) or ():
            ps = [p for p in pins_of(nl, ref) if _row(t, nl, ref, p)[0] == row]
            if ps: return row, any(nl["pin"].get((ref, p)) in on for p in ps)
        return None, False
    for o in own:
        row, up = made_from(o)
        if not up:
            return False, "its %s is on it, which the part makes from %s" % (o, ("its %s, not on the rail" % row) if row
                                                                              else "a supply no row here names")
    tmp = []
    src = _net_sources(nl, ref, net, on, _depth + 1, notes=tmp)
    if src:
        return False, "besides its %s, %s %s not shown to be unable to feed it" % (
            " and ".join(own), _src_list(src), "is" if len(src) == 1 else "are")
    _merge(notes, tmp)
    return True, ""


def fw_pin_role(nl, ref, pin, fn, net, cond=None, _depth=0, notes=None):
    """What a pin of a part firmware sets is, on a gated rail's conductor `net` (R4T-D50 to R4T-D52, R4T-D54, R4T-D55, R4T-D57,
    R4T-D58, R4T-D60 to R4T-D62, R4T-D67): (verdict,
    why), verdict one of "load" (a supply or fixed input by its maker's table), "fail" (a supply output, a tied pin whose
    partner is powered from elsewhere, or the part's ground), "undecided" (the table cannot say, or the symbol disagrees
    with it), or "io" (a pin firmware can drive). `cond` is the rail's conductor as the caller walked it (the nets of the
    switch-to-rail path and those its shunts and 0 Ohm links join); the nets `net` itself is linked to are added here.
    A "load" carries a non-empty `why` where a sentence of its maker's (`independent`) let another supply pin of the part
    stay up off the rail (R4T-D67): the caller names it in the PASS, so no such acceptance is silent. `_depth` is the
    own-output reading's depth (R4T-D63, _NS_DEPTH).
    SINCE THE TWELFTH PASS (R4T-D72, R4T-D73; the review of the eleventh pass, blocking 3 and its minors on the own-output path
    and on SCL): every pin of every part that carries the same module (_module_refs: board B's U30B beside U30A) is read as the
    part's own, in the class, `io` and tied-partner readings, since the module's maker numbers its pins once and its 4.2.1
    covers pins 101 to 200 as it covers 1 to 100; a load's `why` also carries the maker's words the readings of the nets that
    fall with it rested on (another firmware part's supply input read as a load by a sentence, a class row that cleared a
    pin), and an `io` pin a `free` row clears while something holds it up is named with those words (`free_words`). `notes`,
    when given, takes the same words as a list."""
    t = fw_family(nl, ref)
    f = (fn or "").strip()
    if t:
        name, how, agrees = _row(t, nl, ref, pin, f)
        outs, tied = t.get("outputs") or {}, t.get("tied") or {}
        by = ("pin %s is %s by its maker's pin number" % (pin, name)) if how == "number" else ("%s" % name)
        if name in outs:
            return "fail", "is a supply OUTPUT by its maker's table (%s%s; %s): it feeds the rail whatever EMCON does" % (
                by, "" if agrees else ", which the symbol calls %r" % f, t["family"] + ", " + outs[name])
        if name in (t.get("named") or {}):                                   # a partner only, never a row (R4T-D57)
            return "undecided", "is %s's %s, which %s" % (t["family"], name, t["named"][name])
        if name is not None and not agrees:
            return "undecided", "is pin %s, which %s's table gives as %s by its maker's pin number, but the symbol calls " \
                "it %r, so the maker's number and the symbol's name disagree and the pin is not taken as %s" % (
                    pin, t["family"], name, f, name)
        if (name in tied or name in t["inputs"]) and how == "name" and t.get("numbers") and str(pin) not in t["numbers"]:
            return "undecided", "names %s, which %s's table gives at pin %s, not at pin %s, so the symbol and the " \
                "maker's table disagree" % (name, t["family"], "/".join(sorted(p for p, n in t["numbers"].items()
                                                                                if n == name)), pin)
        on = {net} | _linked(nl, net) | set(cond or ())
        mods = _module_refs(nl, ref, t)                                  # R4T-D72: U30A and U30B are one module
        allp = [(r_, p_) for r_ in mods for p_ in pins_of(nl, r_) if not (r_ == ref and p_ == str(pin))]
        sub = []                                                         # R4T-D73: the words the readings below rest on

        def lab(r_, p_): return p_ if r_ == ref else "%s of %s" % (p_, r_)

        def live(n): return not (_dead(n) or is_ground(n))

        def members(row):
            """[(pin, net, agrees, the symbol's name)] for every OTHER pin of the part that the table places in `row`: by
            the maker's pin number whatever the symbol calls it, else by the symbol's name (R4T-D54: the seventh pass kept
            only the pins whose symbol agreed, so a misnamed or unnamed sibling off the rail was dropped without a word).
            Since R4T-D72 every part that carries the same module is read; a pin of another is named 'N of U30B'."""
            out = []
            for r_, p in allp:
                r, _how, ag = _row(t, nl, r_, p)
                if r == row:
                    out.append((lab(r_, p), nl["pin"].get((r_, p), ""), ag, (nl["func"].get((r_, p)) or "").strip()))
            return out

        def off_rail(ms, what, row_txt):
            """Why the pins `ms` of one row leave this pin UNDECIDED: one the symbol agrees on (`what` names it), or one the
            maker's number places in the row whatever the symbol calls it (`row_txt` names the row), on a live net off the
            rail's conductor (R4T-D51 (e), R4T-D54)."""
            why = []
            agree = sorted({n for _p, n, ag, _f in ms if ag and live(n) and n not in on})
            if agree:
                why.append("%s on %s, off the rail: a part's pins of one supply are joined inside it, so it can carry that "
                           "net onto the rail, and no held sheet here states otherwise" % (what, ", ".join(agree)))
            mis = [(p, n, f) for p, n, ag, f in ms if not ag and live(n) and n not in on]
            if mis:
                why.append("the maker's pin number puts %s in %s, off the rail, and the symbol does not give %s that row's "
                           "name: the row is one supply inside the part, so it can carry that net onto the rail, and a "
                           "drawing that disagrees with the maker's numbering is named here, not resolved" % (
                               ", ".join("pin %s (%s) on %s" % (p, ("the symbol calls it %r" % f) if f else
                                                                 "unnamed in the symbol", n) for p, n, f in mis),
                               row_txt, "it" if len(mis) == 1 else "them"))
            return why
        if name in tied:
            partner, words = tied[name]
            ms = members(partner)
            if {n for _p, n, _a, _f in ms} & on:
                why = off_rail(ms, "its %s, which it is tied to, sits" % partner, "the %s row it is tied to" % partner)
                return ("undecided", "is %s's %s, and %s" % (t["family"], name, "; and ".join(why))) if why else ("load", "")
            agree_live = sorted({n for _p, n, ag, _f in ms if ag and live(n)})
            if agree_live:
                return "fail", "is %s's %s, %s, and its %s is on %s, not on the rail" % (
                    t["family"], name, words, partner, ", ".join(agree_live))
            why = off_rail(ms, "", "the %s row it is tied to" % partner)
            if why:
                return "undecided", "is %s's %s, %s, and %s" % (t["family"], name, words, why[0])
            gnd = sorted({n for _p, n, _a, _f in ms if is_ground(n)})
            return "undecided", "is %s's %s, %s, unless its %s is tied to it, and its %s is %s" % (
                t["family"], name, words, partner, partner, ("on ground (%s)" % ", ".join(gnd)) if gnd else
                ("unconnected" if ms else "not on this netlist"))
        if name in t["inputs"]:
            notes_ = {}                                       # the maker's sentences a load rests on (R4T-D67)
            freed = []                                        # `io` pins a `free` row clears while held up (R4T-D73)
            why = off_rail(members(name), "its other %s pins sit" % name, "its %s row" % name)
            # THE REVERSE OF A TIE (R4T-D55): a supply input the maker draws joined to another pin (the STM32H7's VDD to its
            # VBAT through the battery charger) is a load only while that pin is on the rail, on ground, unconnected or
            # not drawn; on another live net the held sheets do not say which way the join conducts. Since R4T-D57 every
            # join of the pin is asked (the STM32H7's VDD to VBAT, VDDA, VDD33USB and VDD50USB), each named where it fails.
            # Since the tenth pass also VDD to VDDLDO (R4T-D60, Table 24), VDDA to VREF+ and a CP2102N's VREGIN to its VDD
            # and VIO (R4T-D62), and a Compute Module 5's 5V to its GPIO_VREF (R4T-D61, 2.9 and 3.1), which is accepted on a
            # net fed only by the module's own CM5_3.3V or CM5_1.8V made from the 5V on the rail (_own_fed)
            rev = (t.get("reverse") or {}).get(name) or ()
            by_words = {}                                     # partners that share one citation are named together
            for entry in rev:
                partner, words, opts = entry[0], entry[1], (entry[2] if len(entry) > 2 else {})
                far = []
                for n in sorted({n for _p, n, _a, _f in members(partner) if live(n) and n not in on}):
                    if not opts.get("own_outputs"):
                        far.append(n); continue
                    tmp = []
                    ok, why_own = _own_fed(t, nl, ref, n, on, _depth, notes=tmp)
                    if not ok: far.append("%s (%s)" % (n, why_own))
                    else: _merge(sub, tmp)
                if far: by_words.setdefault(words, []).append("its %s is on %s" % (partner, ", ".join(far)))
            for words, where_ in by_words.items():
                why.append("%s, off the rail, and %s" % (" and ".join(where_), words))
            # A PIN THE MAKER DRAWS JOINED TO THIS SUPPLY INSIDE THE PART (R4T-D58: the PCA9555's P-port pull-ups to VCC):
            # on a live net off the rail it is a way onto the rail unless everything else on that net is shown to be a load
            bf = (t.get("backfeed") or {}).get(name)
            if bf:
                io = []
                for p in pins_of(nl, ref):
                    fp, n2 = (nl["func"].get((ref, p)) or "").strip(), nl["pin"].get((ref, p), "")
                    if re.match(bf[0], fp, re.I) and live(n2) and n2 not in on:
                        other = _load_only(nl, n2, ref)
                        if other: io.append("%s (pin %s) is on %s, off the rail, where %s %s not shown to be a load" % (
                            fp, p, n2, ", ".join(other[:2]), "is" if len(other) == 1 else "are"))
                if io:
                    why.append("its %s %s %s; and %s" % (
                        bf[1], "pin" if len(io) == 1 else "pins", "; ".join(io[:4]) + ("; and %d more" % (len(io) - 4)
                                                                                      if len(io) > 4 else ""), bf[2]))
            # EVERY OTHER SUPPLY PIN OF THE PART (R4T-D62, round 6 tenth pass; the review of the ninth pass's suggestion,
            # taken by the session under the owner's standing rule of 26 Sep 2026): a supply input is not a load while any
            # other supply pin of the part (a row of `inputs`, `tied`, `named` or `outputs`, or a pin named with a supply
            # word the table does not place) sits on a live net off the rail's conductor, unless that net is fed only by
            # the part's own outputs made from a supply on the rail (_own_fed), or a sentence of its maker's in
            # `independent` lets this row fall while that one stays up. The rows `reverse`, `backfeed` and `sense` read
            # are left to them. A signal input (`sense`, the CP2102N's VBUS) is no supply here and is not asked.
            # THE NETS THAT FALL WITH THE RAIL (R4T-D68): the rail's conductor, and every net fed only by the part's own
            # outputs made from a supply on it (_own_fed), which a pull from an I/O to the part's own CM5_3.3V reaches
            outs_all = set(t.get("outputs") or {}) | set(t.get("output_from") or {})
            falling = set(on)
            for r_, p_ in allp:
                n_ = nl["pin"].get((r_, p_), "")
                if _row(t, nl, r_, p_)[0] in outs_all and live(n_) and n_ not in falling:
                    tmp = []
                    if _own_fed(t, nl, ref, n_, on, _depth, notes=tmp)[0]:
                        falling.add(n_); _merge(sub, tmp)
            if name not in (t.get("sense") or ()):
                skip = {name} | {e[0] for e in rev} | set(t.get("grounds") or ()) | set(t.get("sense") or ())
                ind = [d for d in t.get("independent") or () if name in d["x"]]
                hcls = {}                                     # the part's own outputs held up from outside (R4T-D67)

                def up(row):
                    """A pin of `row` sits on a live net off the rail: it stays up when the rail falls."""
                    return any(live(n) and n not in on for _p, n, _a, _f in members(row))
                cls = {}
                for r_, p_ in allp:
                    p = lab(r_, p_)
                    row = _row(t, nl, r_, p_)[0]
                    fp2, n2 = (nl["func"].get((r_, p_)) or "").strip(), nl["pin"].get((r_, p_), "")
                    if row in skip or not live(n2) or n2 in on: continue
                    # R4T-D66: a supply word joined by an underscore or a hyphen ('VDD_IO', 'VDD_A') is a supply word too
                    if row is None and (not _SUPPLY_NAME.match(fp2) or _GROUND_WORD.match(fp2)
                                        or (bf and re.match(bf[0], fp2, re.I))): continue
                    # a net fed only by the part's own outputs made from the rail goes down with it: decided on the walk
                    tmp = []
                    ok, why_own = _own_fed(t, nl, ref, n2, on, _depth, notes=tmp)
                    if ok:
                        _merge(sub, tmp); continue
                    d_ind = next((d for d in ind if row is not None and row in d["y"]
                                  and (d["when"] is None or up(d["when"]))), None)
                    if d_ind is not None:
                        # R4T-D67: an OUTPUT of the part is excused by such a sentence only while nothing else feeds its
                        # net; held up from outside it is a drawing its maker's held pages do not describe (RP2040 2.9.7.2:
                        # VREG_VOUT 'should be left unconnected' with an external core supply)
                        tmp = []
                        held = _net_sources(nl, ref, n2, on, _depth + 1, notes=tmp) if row in outs_all else []
                        if not held:
                            _merge(sub, tmp)
                            notes_.setdefault(d_ind["words"], {}).setdefault((n2, row), []).append(p); continue
                        hcls.setdefault((n2, row), [held, d_ind["words"], []])[2].append(p)
                        continue
                    cls.setdefault(n2, [why_own, {}])[1].setdefault(row or (p, fp2), []).append(p)
                for n2, (why_own, rows) in sorted(cls.items()):
                    whats = [("its %s (pin%s %s)" % (key, "" if len(ps_) == 1 else "s", ", ".join(ps_))) if isinstance(key, str)
                             else ("its pin %s, named %r, a supply word %s's table does not place" % (key[0], key[1], t["family"]))
                             for key, ps_ in rows.items()]
                    why.append("%s on %s, off the rail%s: both are supplies of one part, and no held page of its maker's "
                               "lets its %s fall while %s stay%s up, so what that net does to the part once EMCON "
                               "has opened the rail's switch, and whether it leaves through the %s pins onto the rail, is "
                               "not known" % (" and ".join(whats), n2, "" if why_own.startswith("no supply output") else
                                              ", where %s" % why_own, name, "it" if len(whats) == 1 else "they",
                                              "s" if len(whats) == 1 else "", name))
                # EVERY I/O OF THE SUPPLY'S DOMAIN (round 6 eleventh pass, R4T-D68; taken by the session under the owner's
                # standing rule of 26 Sep 2026): a pin of the part that is no supply of it, on a live net off the rail where
                # something can hold it up, is UNDECIDED with its maker's words (`io`), unless the maker states that pin
                # passes no current with the supply at 0 V (`free`: the RP2040's fault-tolerant pins); the `backfeed` rows'
                # pins are theirs
                bpat = [b[0] for b in (t.get("backfeed") or {}).values()]
                for io in t.get("io") or ():
                    if name not in io["supply"]: continue
                    held_io = []
                    for r_, p_ in allp:
                        p = lab(r_, p_)
                        row = _row(t, nl, r_, p_)[0]
                        fp2, n2 = (nl["func"].get((r_, p_)) or "").strip(), nl["pin"].get((r_, p_), "")
                        if row is not None or not live(n2) or n2 in on: continue
                        if _SUPPLY_NAME.match(fp2) or _GROUND_WORD.match(fp2): continue      # the class reads these
                        if any(re.match(b, fp2, re.I) for b in bpat): continue
                        tmp = []
                        src = _net_sources(nl, ref, n2, falling, _depth + 1, notes=tmp)
                        if io.get("free") and re.match(io["free"], fp2, re.I):
                            # R4T-D73: a pin its maker decides, named with those words when something holds it up
                            if src: freed.append("its I/O pin %s (%s) is held up on %s, and its maker states that pin passes "
                                                 "nothing into the part's supply then: %s" % (p, fp2, n2, io.get("free_words")
                                                                                             or "the row's `free` sentence"))
                            continue
                        if src:
                            held_io.append("pin %s (%s) is on %s, off the rail, where %s %s not shown to be unable to hold "
                                           "it up" % (p, fp2 or "unnamed in the symbol", n2, _src_list(src),
                                                      "is" if len(src) == 1 else "are"))
                        else:
                            _merge(sub, tmp)
                    if held_io:
                        why.append("its I/O %s; and %s" % ("; its I/O ".join(held_io[:3]) + (
                            "; and %d more I/O pins held up the same way" % (len(held_io) - 3) if len(held_io) > 3 else ""),
                            io["words"]))
                for (n2, row), (held, words, ps_) in sorted(hcls.items()):
                    why.append("its %s (pin%s %s) on %s, off the rail, where besides its %s, %s %s not shown to be unable to "
                               "feed it: its maker lets its %s fall while that supply stays up (%s), but not with the part's "
                               "own %s held up from outside, which %s, so whether that net then leaves through the %s pins "
                               "onto the rail is not known" % (
                                   row, "" if len(ps_) == 1 else "s", ", ".join(ps_), n2, row, _src_list(held),
                                   "is" if len(held) == 1 else "are", name, words,
                                   row, (t.get("outside") or {}).get(row) or "no held page of its maker's describes", name))
            if why: return "undecided", "is %s's %s, and %s" % (t["family"], name, "; and ".join(why))
            # R4T-D67: a load that rests on a sentence of its maker's says so; since R4T-D73 so does one that rests on a `free`
            # row, or on the words the readings of the nets it joins rested on
            parts = ["is %s's %s, a load with %s off the rail, which its maker lets stay up while the %s falls: %s" % (
                t["family"], name, " and ".join("its %s (pin%s %s) on %s" % (row, "" if len(ps_) == 1 else "s", ", ".join(ps_), n2)
                                                for (n2, row), ps_ in sorted(ws.items())), name, words)
                     for words, ws in notes_.items()]
            if freed: parts.append("is %s's %s, a load with %s" % (t["family"], name, "; and ".join(freed)))
            if sub:
                _merge(notes, sub)
                parts.append("%s, and the readings of the nets it joins rest on: %s" % (
                    ("is %s's %s, a load" % (t["family"], name)) if not parts else "the reading rests", "; ".join(sub)))
            return "load", "; ".join(parts)
        if name in (t.get("grounds") or ()):
            return "fail", "is %s's ground (%s): a ground pin on the rail returns whatever powers the part onto the " \
                "rail" % (t["family"], name)
    if _only_net(f, net):
        return "undecided", "its function is only its net's name, so whether it is the part's supply or a pin firmware " \
            "can drive is not known"
    if _GROUND_WORD.match(f):
        return "fail", "names a ground: a ground pin on the rail returns whatever powers the part onto the rail"
    if _SUPPLY_WORD.match(f):
        return "undecided", "names a supply, and %s, so whether it takes power from the rail or gives it is not " \
            "known" % (("%s's table held here does not list it" % t["family"]) if t else
                       "no maker's pin table held here (FW_PIN_TABLES) covers this part")
    return "io", ""


def _supplyish(nl, k, net, via, kind):
    """How `net` is known to be a supply ("rail", "pinmap", "name", or "pins" when only a pin whose function names a
    supply sits on it, SUPPLY_FN), or None: the second-feed check judges a resistor to one as a feed and does not read
    past it (R4T-D43)."""
    sk = kind(k, net)
    if sk: return sk
    return "pins" if any(r2 != via and SUPPLY_FN.match(f2 or "") for r2, _p2, f2 in nl["nets"].get(net, [])) else None


def _second_sources(nl, k, rail, sref, anchor, accessories, path_refs=None):
    """(fail, undecided) for anything that could feed a gated rail besides its switch (review fix-up of round 4,
    26 September 2026: the check used to stop at the first switch it found on the rail). `rail` is one net or the list of
    nets from the switch to the rail (_source_switch's path); `path_refs` are the parts that join them.

    WHAT A FEED IS (round 6 fourth pass, R4T-D43; corrected in the fifth pass, R4T-D49; both taken by the session under the
    owner's standing rule of 26 Sep 2026). The kit's own topology is the reason: board A's +13V8_PA and +12V_HF come from
    LM5176 stages that run from VBAT (at main 458b2873 their VIN pins sit on PA_VINP and HF_VINP, fed from VBAT through
    the blocking diodes D20 and D21, and VISNS on VBAT), and the power stage's own output node, PA_OUT and HF_OUT, reaches
    the rail through a 6 mOhm and a 10 mOhm sense resistor (R55, R65) while the controller is found by its VOSNS pin on the
    rail itself. The rules, on every net of the rail's CONDUCTOR:
      * THE CONDUCTOR (R4T-D49, correcting R4T-D47): the nets of the path, and every net a resistor under SHUNT_MAX_OHM (a
        current-sense shunt or a 0 Ohm link) joins to one of them, in either direction, unless that net is a supply by
        one of the three tests or carries a supply pin (a link to a supply is a feed, judged below). R4T-D47 read only
        the nets from the switch to the rail, so where the switch was found by a sense pin ON the rail (VOSNS) the power
        stage's own node behind the shunt was never read: board A's PA_OUT and HF_OUT, which carry Q14 and Q24;
      * a resistor whose far end is a '+' rail or a pin-map supply (_pinmap_supplies: a logic VCC or a switch VIN pin sits
        on it) is a feed and FAILS, whatever its value; one whose far end is a supply by its name only, or a net a pin
        whose function names a supply sits on (SUPPLY_FN), is UNDECIDED unless everything else on that net is shown to
        be a load (_load_only: board B's LED_5V_A1, LED11's anode behind R101, with its cathode on ground);
      * A RESISTOR TO ANY OTHER NET IS READ THROUGH (R4T-D49, correcting R4T-D43, which read such a resistor as "not a
        feed" and so let a switch output, a FET or a GPIO behind a 0 Ohm or 1 Ohm link onto a net named X_ALT feed the
        rail with nothing said): its far net is read with the rules below, as the rail is, and so is every net a further
        resistor joins to it (a feed behind two resistors is still a feed; the walk stops at a ground, a dead end, a
        supply, which the rule above judges, and a net already read). A feedback divider, a current-sense filter and an
        LED's anode are read and hold nothing that feeds;
      * a transistor with a channel pin on the net is a feed unless its other channel pin is on ground or on nothing (a
        discharge FET only takes current off the rail): it FAILS, or is UNDECIDED when its gate is driven by the gated
        switch itself (a controller's own gate drive: SNVSAI1D 7.4.1 gives the LM5176's shutdown as "VCC off, No
        switching" and states no level for HDRV1 and HDRV2). A FET's gate on the net only reads it (board B's Q106, Q206
        and Q306). A transistor whose type or pins this file cannot read (fet_of) is UNDECIDED by any pin (since R4T-D70 a
        pin named G too: no proof of an insulated gate), and the result names the nets its other pins sit on that the gated
        switch drives;
      * a second switch output or SW pin, an OUTPUT_FN pin and a diode with its cathode toward the rail FAIL; a connector
        leaves the board and is UNDECIDED, a declared accessory too since R4T-D70 (its declaration says what the far end is
        for, not that nothing plugged there feeds the rail);
      * A PIN OF A PART WHOSE PINS FIRMWARE SETS (software_io, R4T-D49; judged by its maker's table since R4T-D50; the
        part found by what it is since R4T-D52) on the conductor itself is a load only when its maker's pin table gives
        it as a supply input (FW_PIN_TABLES, fw_pin_role: the RP2040's IOVDD, DVDD, ADC_AVDD, USB_VDD and VREG_VIN; an
        STM32H742, H743 or H753's VDD, VDDLDO, VDDA and VDD50USB; a PCA9555's VCC; a CP2102N's VREGIN and VBUS; a Compute
        Module 5's 5V and GPIO_VREF by their pin numbers, where the symbol names the same row), and no other pin of that
        row sits on a live net off the conductor. A tied pin is a load only with its partner on the conductor (the path,
        and every net a shunt or a 0 Ohm link joins to it or to the pin's own net): a CP2102N's VDD with its VREGIN, an
        STM32H7's VREF+ with its VDDA and its VBAT with its VDD (the battery charger, R4T-D51), a Compute Module 5's VBAT
        with its 5V (the RTC's 3 mA charger, R4T-D51); with the partner on another live net it FAILS, on ground or not
        drawn it is UNDECIDED. The reverse: an STM32H7's VDD is a load only with its VBAT (R4T-D55), its VDDA, VDD33USB
        and VDD50USB (R4T-D57, 3.5.1's power sequence) and its VDDLDO (R4T-D60, Table 24) each on the conductor, on ground
        or nowhere, else UNDECIDED; its VDDA only so with VREF+, a CP2102N's VREGIN with VDD and VIO, and a Compute Module
        5's 5V with GPIO_VREF, which may also sit on the module's own CM5_3.3V or CM5_1.8V (R4T-D61) with nothing else on
        that net, or behind a pull from it, able to feed it (R4T-D63, R4T-D64: another firmware part's supply input there
        is judged with all its joins, and a pull is read through); a PCA9555's VCC, an
        RP2040's IOVDD or a CP2102N's VREGIN is UNDECIDED while a P-port pin, an ADC input or VBUS sits on a live net off the
        conductor whose other parts are not shown to be loads (R4T-D58, R4T-D62); and any supply input is UNDECIDED while
        any other supply pin of its part sits on a live net off the conductor, unless that net is fed only by the part's own
        outputs made from the rail or a maker's sentence lets the two fall in that order (R4T-D62; the sentence excuses an
        output of the part only while nothing else feeds it, and is named in the PASS, R4T-D67); and any supply input of an
        I/O domain is UNDECIDED while an I/O of that domain is held up off the conductor, unless its maker states the pin
        passes no current then (R4T-D68, the rows' `io`). A supply OUTPUT by the
        same table FAILS: the
        Compute Module 5's CM5_3.3V and CM5_1.8V (pins 84, 86, 88 and 90, up to 600 mA, CM5 datasheet 3.4), the RP2040's
        VREG_VOUT, an STM32H7's VCAP. The part's ground
        FAILS (it returns the part's supply current onto the rail). A pin whose function is only its net's name, a row by
        pin number the symbol names otherwise, a supply word the table does not list, or any supply word on a part with
        no table, is UNDECIDED; any other pin FAILS as one firmware can drive (a name only ENDING in a supply word,
        GPIO24_VBUS or ADC_VIN, among them). Behind a resistor any such pin is UNDECIDED whatever its function, since the
        resistor bounds what it can feed and nothing here judges whether that matters. The census FAILS the same pin on
        a net EMCON forces.
      * A LOGIC GATE'S PUSH-PULL OUTPUT (R4T-D59, round 6 ninth pass): by LOGIC's pin maps, FAILS on the conductor and is
        UNDECIDED behind a resistor; an open-drain output feeds nothing; any pin of a gate on a land its map is not for is
        UNDECIDED. A gate's other pins are read by the rows of the last rule but one;
      * A PART THAT RUNS FROM THE RAIL AND WHOSE MAKER STATES A PATH BACK INTO IT (R4T-D65, round 6 eleventh pass): a logic
        part's VCC where its sheet states a path from an output into VCC or rates the output by VCC (the SN74LVC08A's
        positive output clamps, SCAS283W 7.3.3; the SN74LVC08A's, 32A's and 00A's outputs at most VCC + 0.5 V with no Ioff)
        and a switch's input where its sheet states one from its output or rates the output by the input (the TPS22810's
        body diode, SLVSDH0C 10.4; the TPS2596's and the AP64500's outputs at most their input plus 0.3 V) are UNDECIDED
        while an output of the part sits on a live net off the conductor that _net_sources() finds something able to hold
        up; with no such words (the parts with Ioff and a power-off output rating; the LM5176, whose power path is its
        external FETs) or nothing holding an output up, a load;
      * A PIN OF A PART THAT ONLY MENTIONS A FIRMWARE FAMILY (R4T-D53, round 6 eighth pass; the search since R4T-D56): a
        part software_io() does not read as a firmware part while its value or library symbol names one anywhere
        (fw_mention: "I/O supervisor STM32H743VIT6" on meshsat_ic:U41, "Slot S1 compute: CM5108032", "Raspberry Pi CM5
        8GB/64GB wireless", "Seeed XIAO ESP32S3", "TXS0102 level shifter for the RP2040") is UNDECIDED on the conductor
        and behind a resistor, naming the family and saying the part is not read as one. The seventh pass (R4T-D52) took
        such a pin as a load without a word (R4T-F26), and the eighth still did for a module named 'CM5' or 'Compute
        Module' without a part number (R4T-F29);
      * A PIN IS A LOAD ONLY WHERE A ROW OF ITS MAKER'S CLEARS IT (round 6 twelfth pass, R4T-D70 and R4T-D71; the review of
        the eleventh pass, its three blocking items closed as classes): every other pin of a switch, a logic part or a
        protection part is read by _class_pin(), a load only by its maker's words (a logic input by II, an open-drain output
        by its maker's words, a logic VCC by Ioff or with nothing holding its outputs, a switch's enable its maker states only
        leaks, a switch's input with nothing holding a pin of it no row clears, the USBLC6-2's VBUS with nothing holding its
        I/O), which the PASS carries; a ground with the part's supply up FAILS on the conductor and is UNDECIDED behind a
        resistor; any other pin of such a part is UNDECIDED, named;
      * ANY OTHER PIN IS UNDECIDED, NAMED (R4T-D70, closing R4T-F23): a pin of a part in none of the classes above, which the
        eleventh pass took as a load without a word. At main a6f87e9d (the six netlists of fc144600) the walk meets ten such
        pins on four parts: board A's INA226 U14 (its three pins on PA_OUT and +13V8_PA, which its symbol names after their
        nets), board B's E72 modules U13 and U14 (each one's +3V3_ZB pin while the other is judged, and their RST and BSL
        pins behind R28 to R31) and board B's USBLC6 U33 (VBUS, on +5V_LIME, read now by its row and UNDECIDED: its I/O sit
        on the hub's DN1 and on J_LIME)."""
    fail, und, notes = [], [], {}
    kind = _supply_test({k: nl}).kind
    starts = [rail] if isinstance(rail, str) else list(rail)
    # the parts that carry the switch's output to the rail (an inductor, a shunt): the conductor, not a feed
    cond_refs = set(path_refs) if path_refs is not None else \
        {r for n in starts for r, _p, _f in nl["nets"].get(n, []) if re.match(r"^L\d", r)}
    # THE CONDUCTOR, both directions through shunts and 0 Ohm links (R4T-D49)
    seen, queue = set(starts), [(n, n, True) for n in starts]
    i = 0
    while i < len(queue):
        n = queue[i][0]; i += 1
        for ref, pin, _f in nl["nets"].get(n, []):
            if ref in cond_refs or ref in (sref, anchor) or not re.match(r"^R\d", ref): continue
            ps = pins_of(nl, ref)
            ohm = _ohms(value(nl, ref)) if len(ps) == 2 else None
            if ohm is None or ohm >= SHUNT_MAX_OHM: continue
            m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
            if m2 in seen or _dead(m2) or is_ground(m2) or _supplyish(nl, k, m2, ref, kind): continue
            cond_refs.add(ref); seen.add(m2)
            queue.append((m2, "%s, joined to %s through %s (%s)" % (m2, n, ref, value(nl, ref)[:16]), True))
    cond_nets = set(seen)                         # the conductor, before the read-through below adds the nets behind resistors
    # the nets the gated switch has a pin on (its gate drives and switch nodes among them), ground left out
    drives = {}
    for p in (pins_of(nl, sref) if sref else []):
        dn = nl["pin"].get((sref, p), "")
        if not (_dead(dn) or is_ground(dn)): drives.setdefault(dn, p)
    i = 0
    while i < len(queue):
        net, where, on_cond = queue[i]; i += 1
        for ref, pin, fn in nl["nets"].get(net, []):
            if ref in (sref, anchor) or ref in cond_refs or re.match(r"^(#|TP|C\d)", ref): continue
            ps = pins_of(nl, ref)
            if re.match(r"^R\d", ref):
                # A RESISTOR TO ANOTHER SUPPLY IS A FEED (second fix-up of round 4, 26 September 2026; R4T-D43): a 0 Ohm
                # link or a bleed from another supply keeps the gated rail up when its switch is off. A resistor to any
                # other net is read through (R4T-D49)
                if len(ps) != 2:
                    # R4T-D70: a resistor designator with other than two pins (a network, a trimmer) is not placed
                    und.append("%s: %s pin %s (%s) is a resistor with %d pins, which this file does not read, so what its other "
                               "pins join to the rail is not known" % (where, ref, pin, value(nl, ref)[:30], len(ps))); continue
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if m2 == net or m2 in seen or _dead(m2) or is_ground(m2): continue
                sk = _supplyish(nl, k, m2, ref, kind)
                if sk in ("rail", "pinmap"):
                    fail.append("%s: joined to %s through %s (%s)%s" % (where, m2, ref, value(nl, ref)[:16],
                                "" if sk == "rail" else ", a supply by its maker's pin table"))
                elif sk:
                    sup_pins = sorted({r2 for r2, _p2, f2 in nl["nets"].get(m2, []) if r2 != ref and SUPPLY_FN.match(f2 or "")})
                    other = _load_only(nl, m2, ref)
                    if other:
                        und.append("%s: joined through %s (%s) to %s, %s, where %s %s not shown to be a load" % (
                            where, ref, value(nl, ref)[:16], m2, "a supply by its name only" if sk == "name" else
                            "a net a supply pin sits on (%s)" % ", ".join(sup_pins[:3]), ", ".join(other[:4]),
                            "is" if len(other) == 1 else "are"))
                else:
                    seen.add(m2)
                    queue.append((m2, "%s through %s (%s) to %s" % (where, ref, value(nl, ref)[:16], m2), False))
                continue
            if ref.startswith("Q"):
                fq = fet_of(nl, ref)
                if fq is None:
                    # R4T-D70: a pin named G of a transistor whose type this file cannot read is no proof of an insulated
                    # gate (a junction FET's gate conducts forward), so it is named as the rest of such a part is
                    own = sorted({nl["pin"].get((ref, p), "") for p in ps} & set(drives) - {net})
                    und.append("%s: %s pin %s (%s, %r) is a transistor whose type or pin map this file cannot read, so whether "
                               "it can feed the rail is not known%s" % (where, ref, pin, value(nl, ref)[:30], fn,
                               ("; its other pins sit on %s, where %s, the gated switch itself, has its pins %s, and no "
                                "table here states that its drive is off with its enable" % (", ".join(own), sref,
                                ", ".join(drives[x] for x in own))) if own else "")); continue
                t, pp = fq
                if pin == pp["G"]: continue                                          # a gate only reads the rail
                other = pp["D"] if pin == pp["S"] else pp["S"]
                o_net, g_net = nl["pin"].get((ref, other), ""), nl["pin"].get((ref, pp["G"]), "")
                if _dead(o_net) or is_ground(o_net) or o_net == net: continue        # a discharge FET only takes current off
                if sref and any(r2 == sref for r2, _p2, _f2 in nl["nets"].get(g_net, [])):
                    und.append("%s: fed from %s through %s's channel (%s-channel), whose gate %s is driven by %s, the gated "
                               "switch itself; that its gate drive is off with its enable is not stated here"
                               % (where, o_net, ref, t, g_net, sref)); continue
                fail.append("%s: fed from %s through %s's channel (%s-channel, gate on %s), a second switch around the gated one"
                            % (where, o_net, ref, t, g_net)); continue
            sw = switch_of(nl, ref)
            if sw and (pin in sw["out"] or pin in sw["sw"]):
                fail.append("%s: a second switch output, %s pin %s" % (where, ref, pin)); continue
            # A PART THAT RUNS FROM THE RAIL AND WHOSE MAKER STATES A PATH BACK INTO IT (round 6 eleventh pass, R4T-D65, the
            # review of the tenth pass, minor L1; taken by the session under the owner's standing rule of 26 Sep 2026): a
            # switch's input or a logic part's VCC whose maker states a path from an output back into it, or rates the output
            # by it (`reverse`, `vcc_path`), is UNDECIDED while an output of it sits on a live net off the conductor that
            # something can hold up; with no such words, or nothing holding an output up, it is a load
            fb = _feeds_back(nl, ref, pin, cond_nets)
            if fb:
                und.append("%s: %s pin %s (%s, %r) sits %s, and %s, so once EMCON has opened the rail's switch what holds "
                           "that output up feeds the rail through it" % (
                               where, ref, pin, value(nl, ref)[:30], fn, "on the rail's conductor" if on_cond else
                               "behind a resistor from it", fb[0])); continue
            if re.match(r"^(D|LED|L|FB|F)\w*", ref) and len(ps) == 2:
                m2 = nl["pin"].get((ref, ps[1] if ps[0] == pin else ps[0]), "")
                if is_ground(m2) or _dead(m2): continue                              # a clamp to ground
                if re.match(r"^(D|LED)", ref) and fn == "K" and nl["func"].get((ref, [p for p in ps if p != pin][0])) == "A":
                    fail.append("%s: fed from %s through %s (anode there, cathode on the rail)" % (where, m2, ref)); continue
                if re.match(r"^(D|LED)", ref) and fn == "A": continue                # it can only take current off the rail
                fail.append("%s: joined to %s through %s" % (where, m2, ref)); continue
            if re.match(r"^(J|P)\w*", ref):
                acc = [a for a in accessories if a["board"] == k and a["ref"] == ref]
                if acc:
                    # R4T-D70: a declared accessory names what its far end is for, not that nothing there feeds the rail
                    und.append("%s: leaves the board through %s pin %s, declared an accessory (%s): the declaration says what "
                               "the far end is for, not that nothing plugged there feeds the rail, and the far end is not on "
                               "this netlist" % (where, ref, pin, acc[0]["why"])); continue
                und.append("%s: leaves the board through %s pin %s, and what is at the far end is not on this netlist"
                           % (where, ref, pin)); continue
            if OUTPUT_FN.match(fn or ""):
                fail.append("%s: %s pin %s (%s, %s) is an output on the rail" % (where, ref, pin, fn, value(nl, ref)[:30])); continue
            # A LOGIC GATE'S PUSH-PULL OUTPUT (R4T-D59, round 6 ninth pass, the review of the eighth pass, minor 3; taken by
            # the session under the owner's standing rule of 26 Sep 2026). LOGIC gives every gate's output pin from its
            # maker's pin table, and a push-pull output drives high from the gate's own VCC, so on the conductor it feeds
            # the rail whatever the rail's switch does (FAIL, as an OUTPUT_FN pin does) and behind a resistor it is
            # UNDECIDED, as a firmware pin is. An open-drain output only pulls low and feeds nothing. A plain '74LVC1G34
            # buffer' with Y on the rail read PASS here before (R4T-F31). A gate on a land its map is not for is UNDECIDED
            # by any pin, as census() reads it: the map would be a guess there, so which pin is its output is not known.
            fam = logic_of(nl, ref)
            if fam and fam.get("wrong_land"):
                und.append("%s: %s pin %s (%s, %r) is a pin of a %s on a land its pin map is not for, so which pin is an "
                           "output is not known" % (where, ref, pin, value(nl, ref)[:30], fn, fam["name"])); continue
            if fam and fam.get("unwired"):
                und.append("%s: %s pin %s (%s, %r) is a pin of %s" % (where, ref, pin, value(nl, ref)[:30], fn, fam["unwired"]))
                continue
            gate = next((g for g in fam["gates"] if g[1] == pin), None) if fam else None
            if gate and gate[2] not in OPEN_DRAIN:
                txt = "%s pin %s (%s, %r) is the push-pull output of %s %s gate (%s)" % (
                    ref, pin, value(nl, ref)[:30], fn, "an" if gate[2][0] in "AEIOU" else "a", gate[2],
                    fam["cite"].split(",")[0])
                if on_cond:
                    fail.append("%s: %s: driven high it feeds the rail from the gate's own supply with the rail's switch "
                                "off" % (where, txt))
                else:
                    und.append("%s: %s, behind a resistor from it: driven high it feeds the rail through the resistor, "
                               "and nothing here judges what that current can do" % (where, txt))
                continue
            if software_io(nl, ref):
                what = "%s pin %s (%s, %r)" % (ref, pin, value(nl, ref)[:30], fn)
                if not on_cond:
                    und.append("%s: %s is a pin of a part whose pins firmware sets; driven high it feeds the rail through "
                               "the resistor, and nothing here judges what that current can do" % (where, what))
                    continue
                # THE MAKER'S TABLE DECIDES (R4T-D50): a supply input is a load, a supply output a feed
                verdict, why = fw_pin_role(nl, ref, pin, fn, net, cond_nets)
                if verdict == "load" and why:                            # R4T-D67: the maker's sentence it rests on
                    notes.setdefault((ref, fn, why), []).append(pin)
                if verdict == "fail":
                    fail.append("%s: %s %s" % (where, what, why))
                elif verdict == "undecided":
                    und.append("%s: %s is a pin of a part whose pins firmware sets, and it %s" % (where, what, why))
                elif verdict == "io":
                    fail.append("%s: %s is a pin whose direction firmware sets, on the rail: driven high it feeds the rail "
                                "with its switch off, so the gate depends on software" % (where, what))
                continue
            # A PART THAT ONLY MENTIONS A FIRMWARE FAMILY (R4T-D53): not read as one, and never passed as a load
            fm = fw_mention(nl, ref)
            loc = "on the rail's conductor" if on_cond else "behind a resistor from it"
            if fm:
                und.append("%s: %s pin %s (%s, %r) sits %s, and %s" % (
                    where, ref, pin, value(nl, ref)[:30], fn, loc, _mention_why(nl, ref, fm)))
                continue
            # A PIN IS A LOAD ONLY WHERE A ROW OF ITS MAKER'S CLEARS IT (round 6 twelfth pass, R4T-D70 and R4T-D71; the review of
            # the eleventh pass, its three blocking items, closed as classes; taken by the session under the owner's standing
            # rule of 26 Sep 2026, following the second checkpoint review's findings D and G). A switch's, a logic part's or a
            # protection part's pin is read by _class_pin(): a load only by its maker's words, carried into the PASS; a feed
            # FAILS on the conductor and is UNDECIDED behind a resistor; anything else UNDECIDED. A pin of a part in no class
            # is UNDECIDED, named: the eleventh pass took it as a load without a word (R4T-F23).
            tmp = []
            v, w = _class_pin(nl, ref, pin, fn, cond_nets, 0, (), notes=tmp)
            what = "%s pin %s (%s, %r)" % (ref, pin, value(nl, ref)[:30], fn)
            if v == "load":
                notes.setdefault((ref, fn, w + (("; and the readings of the nets it joins rest on: %s" % "; ".join(tmp)) if tmp
                                                else "")), []).append(pin)
            elif v == "feed" and on_cond:
                fail.append("%s: %s %s: it feeds the rail with its switch open" % (where, what, w))
            elif v == "feed":
                und.append("%s: %s sits behind a resistor from it and %s: it feeds the rail through the resistor, and nothing "
                           "here judges what that current can do" % (where, what, w))
            elif v == "undecided":
                und.append("%s: %s sits %s and %s" % (where, what, loc, w))
            else:
                und.append("%s: %s sits %s, and it is a pin of a part no class here reads (no pin map, switch entry, "
                           "protection row or firmware table of its maker's is held here for it), so whether it can feed the "
                           "rail is not known" % (where, what, loc))
    return fail, und, ["%s pin%s %s (%s, %r) %s" % (r_, "" if len(ps_) == 1 else "s", ", ".join(ps_), value(nl, r_)[:30], f_, w_)
                       for (r_, f_, w_), ps_ in sorted(notes.items())]


def _path_census(boards, walks, lines, k, g, target):
    """(fail, undecided, boards named, absent) over every net of an accepted path: its asserted line's set-wide
    census, and each later net's conductor with that net's own driver allowed."""
    fail, und, named, absent = [], [], set(), set()
    src = g["nets"][0]
    lc = lines.get(src)
    if lc:
        if lc["fail"]: fail.append("its line %s fails: another driver can reach it, or its fail-safe states do not hold "
                                   "it low (the line result names which)" % src)
        elif lc["undecided"]: und.append("its line %s is undecided (the line result names why)" % src)
        absent |= lc["absent"]
    got = walks[k][0]
    # THE ANCHOR PIN IS THE PATH'S TARGET ON EVERY NET (second fix-up of round 4, 26 September 2026). It was passed
    # only to the census of the path's last net, so a series resistor in front of the anchor put the anchor on an
    # EARLIER net's conductor with no target set, and a correct path failed: a CM5 pin read as "a pin whose direction
    # firmware sets", the SA868 PTT as "an active pin no held document shows to be an input". The target is one fixed
    # (board, ref, pin), so it is the same on every net.
    nl = boards[k]
    for n in g["nets"][1:]:
        drv = got[n]["driver"]
        kind = got[n]["kinds"][-1] if got[n]["kinds"] else None
        ff = None
        if kind in ("LS", "SW_GND") and drv:
            q = nfet_pins(nl, drv[0]) or {}
            gn = nl["pin"].get((drv[0], q.get("G", "")), "")
            fam = fet_family(nl, drv[0])
            if kind == "LS":
                vg = rail_volts(gn)
            else:
                gd = got.get(gn, {}).get("driver")
                vg = max([rail_volts(r) or 0 for r in _supply_nets(nl, gd[0])] or [0]) if gd else None
            if not fam or vg is None or vg < fam["ron_vgs"]:
                ff = (drv[0], "its gate is driven to %s and %s" % ("%g V" % vg if vg is not None else "a level no rail names",
                      fam["cite"][fam["cite"].find("RDS"):] if fam else "no held sheet states its channel"))
        c = census(boards, walks, k, n, got[n]["level"], {(k, drv[0], drv[1])} if drv else set(), target=target, fet_forced=ff,
                   released=(kind == "OD_REL"))
        fail += c["fail"]; und += c["undecided"]; named |= c["boards"]; absent |= c["absent"]
    return fail, und, named, absent


def _released_why(nl, got, net):
    """Why a net EMCON does not reach is left alone when an open-drain output EMCON RELEASES drives it (round 6 third
    pass, the review of round 6's second pass, minor 7): what its pulls do, from _released_level, so a board author
    reads "pulled to SAU_3V3 ..., a supply whose name states no voltage" rather than only "EMCON does not reach it"."""
    out = []
    for ref, pin, _f in nl["nets"].get(net or "", []):
        q = nfet_pins(nl, ref)
        if q is not None and pin == q["D"] and is_ground(nl["pin"].get((ref, q["S"]), "")) \
                and (got.get(nl["pin"].get((ref, q["G"]), "")) or {}).get("level") == 0:
            # a switch to ground EMCON holds off (R4T-D46)
            out.append("EMCON holds the switch to ground %s off and leaves %s to its pulls: %s" % (ref, net, _released_level(nl, net)[1]))
            continue
        fam = logic_of(nl, ref)
        if not fam or _unmapped(fam): continue
        for ins, o, kind in fam["gates"]:
            if o != pin or kind not in RELEASE: continue
            if any((got.get(nl["pin"].get((ref, i), "")) or {}).get("level") == RELEASE[kind] for i in ins):
                out.append("EMCON releases the open-drain %s and leaves %s to its pulls: %s" % (ref, net, _released_level(nl, net)[1]))
    return ("; " + "; ".join(out)) if out else ""


def _judge_option(boards, walks, lines, opt):
    """(ok, sentence, boards named, absent): ok is True, False, or None for undecided."""
    k = opt["board"]; nl = boards[k]; got = walks[k][0]
    ref = opt["ref"]
    if ref not in nl["comps"] or not pins_of(nl, ref):
        return False, "%s is not on board %s's netlist" % (ref, k), set(), set()
    if opt["kind"] == "power":
        rails = _anchor_rails(nl, opt)
        if not rails: return False, "%s carries no supply rail" % ref, set(), set()
        why, und, good, named, absent = [], [], [], set(), set()
        for rail in rails:
            sref, sw, how, spath = _source_switch(nl, rail)
            if not sref:
                why.append("%s: %s" % (rail, how)); continue
            en_net = nl["pin"].get((sref, sw["en"]), "")
            lv = got.get(en_net)
            if not lv or lv["level"] != OFF_LEVEL:
                why.append("%s comes from %s (%s, %s), whose enable %s (pin %s) EMCON does not force off%s"
                           % (rail, sref, value(nl, sref)[:40], how, en_net or "?", sw["en"],
                              "" if lv else _released_why(nl, got, en_net))); continue
            # every net of the rail's conductor, from the switch to the rail and through any shunt either way (R4T-D49)
            f2, u2, n2 = _second_sources(nl, k, spath["nets"], sref, ref, ACCESSORIES, path_refs=spath["refs"])
            f3, u3, nm, ab = _path_census(boards, walks, lines, k, lv, (k, sref, sw["en"]))
            named |= nm; absent |= ab
            # R4T-F9 (round 6): the elements on the path losing their own supply; the switch cannot pass power when
            # its own input is down, so that rail takes the transmitter down with the element
            vin = set()
            for vn in _pin_nets(nl, sref, sw.get("vin") or []):           # whatever its name (R4T-D41)
                vin |= _rail_conductor(boards, k, vn)
            f9, u9 = own_supply(boards, walks, k, opt, lv, (sref, sw["en"]), vin)
            if f2 or f3 or f9:
                why.append("%s: %s" % (rail, "; ".join(f2 + f3 + f9))); continue
            if u2 or u3 or u9:
                und.append("%s: %s" % (rail, "; ".join(u2 + u3 + u9)))
            good.append("%s off: %s enable pin %s through %s%s%s" % (
                rail, sref, sw["en"], " > ".join(lv["path"]), (" (%s)" % how) if spath["refs"] else "",
                # R4T-D67: a load on the rail that rests on its maker's sentence is named in the PASS, never silent
                ("; taken on its maker's words: %s" % "; ".join(n2)) if n2 else ""))
        if why: return False, "power: " + "; ".join(why), named | {k}, absent
        if und: return None, "power: " + "; ".join(good) + "; UNDECIDED: " + "; ".join(und), named | {k}, absent
        return True, "power: " + "; ".join(good), named | {k}, absent
    # rf_disable and key: a pin of the anchor itself
    p = opt["pin"]
    fn = nl["func"].get((ref, p), "")
    if fn and not re.search(opt["func"], fn, re.I):
        return False, "%s pin %s is %r on this netlist, not the %s the table expects" % (ref, p, fn, opt["func"]), set(), set()
    net = nl["pin"].get((ref, p), "")
    if opt["kind"] == "rf_disable" and not opt.get("cite"):
        return False, "%s pin %s (%s): %s" % (ref, p, net, opt.get("uncited") or "no maker statement is cited"), set(), set()
    lv = got.get(net)
    if not lv:
        drv = [r for r, _p, _f in nl["nets"].get(net, []) if r != ref and not re.match(r"^(R|C|TP|#)\w*", r)]
        return False, ("%s pin %s (%s): EMCON does not reach it%s%s" % (ref, p, net, (", it is driven by %s" % ", ".join(
            "%s (%s)" % (r, value(nl, r)[:40]) for r in drv)) if drv else "", _released_why(nl, got, net))), set(), set()
    if lv["level"] != opt["safe"]:
        return False, "%s pin %s (%s): EMCON drives it %s where the safe level is %s" % (ref, p, net, lv["level"], opt["safe"]), set(), set()
    extra = []
    if opt.get("drive") == "open_drain":
        # THE PIN MAY ONLY BE DRIVEN LOW (review fix-up of round 4, 26 September 2026). A 74LVC1G08 or 1G34 on the
        # pin drives it high whenever EMCON is released, against the module that "drives it high internally when
        # required", and a level shifter passes whatever its other side drives. The last element before the pin,
        # series resistors aside, must be one that can only pull low.
        last = [x for x in lv["kinds"] if x != "R"]
        if not last or last[-1] not in OPEN_DRAIN:
            extra.append("the last element before the pin is %s, and the maker allows this pin only to be driven low: "
                         "it needs an open-drain output or an N-channel switch to ground there"
                         % ({"AND": "a push-pull AND output", "NAND": "a push-pull NAND output", "INV": "a push-pull "
                             "inverter output", "BUF": "a push-pull buffer output", "LS": "an N-channel level shifter, "
                             "which passes its other side's push-pull drive", "OD_REL": "an open-drain output EMCON "
                             "releases, which leaves the pin to whatever pulls it"}.get(last[-1] if last else "",
                                                                                         last[-1] if last else "nothing")))
        # A PULL-UP ANYWHERE AFTER THE LAST OPEN-DRAIN ELEMENT IS ON THE PIN (second fix-up of round 4, 26 September
        # 2026): the first version looked only at the pin's own net and only for '+' rails, so a pull-up in front of
        # a series resistor, or one to a supply named VDD_3V3, read PASS.
        od = [i for i, x in enumerate(lv["kinds"]) if x in OPEN_DRAIN]
        after = sorted(set(lv["nets"][od[-1] + 1:] if od else []) | {net})   # nets[i + 1] is hop i's output
        ups = sorted({r for nn in after for r, _p, _f in nl["nets"].get(nn, []) if re.match(r"^R\d", r)
                      and len(pins_of(nl, r)) == 2 and any(_supply_name(nl["pin"].get((r, q), "")) for q in pins_of(nl, r))})
        if ups:
            extra.append("it is pulled up on the carrier by %s, and the maker says it 'can't be driven high' and pulls "
                         "it up itself" % ", ".join(ups))
    f3, u3, named, absent = _path_census(boards, walks, lines, k, lv, (k, ref, p))
    # R4T-F9 (round 6): the elements on the path losing their own supply, unless the transmitter shares it. The
    # transmitter's supplies are the nets on its supply pins by their function, whatever the nets are called (round 6
    # fourth pass, R4T-D44, the review of the third pass, minor 5: filtering them by the name test dropped a net such as
    # RF_3V3_SW, whose name carries a control word, and own_supply() then judged states in which the transmitter is off)
    ar = set()
    for r_ in _anchor_rails(nl, opt):
        ar |= _rail_conductor(boards, k, r_)
    f9, u9 = own_supply(boards, walks, k, opt, lv, (ref, p), ar)
    f3 = f3 + f9; u3 = u3 + u9
    if extra or f3:
        return False, "%s pin %s (%s): EMCON forces it through %s, and %s" % (
            ref, p, net, " > ".join(lv["path"]), "; ".join(extra + f3)), named | {k}, absent
    if u3:
        return None, "%s: %s pin %s through %s; UNDECIDED: %s" % (opt["kind"], ref, p, " > ".join(lv["path"]),
                                                                  "; ".join(u3)), named | {k}, absent
    return True, "%s: %s pin %s through %s" % (opt["kind"], ref, p, " > ".join(lv["path"])), named | {k}, absent


def judge(boards, table=None, accessories=None, receivers=None, owed=None):
    """boards: {letter: parsed netlist or None}. One result per asserted line, one per transmitter and one per
    board's classification: dict(ok, text, detail, boards), ok True, False or None (undecided). The tables default
    to this file's own; a fixture passes its own."""
    table = TRANSMITTERS if table is None else table
    accessories = ACCESSORIES if accessories is None else accessories
    receivers = RECEIVE_ONLY if receivers is None else receivers
    owed = OWED if owed is None else owed
    res, walks, walks1 = [], {}, {}
    for k, nl in boards.items():
        if nl is not None: walks[k] = reach(nl)
    present_boards = {k for k, nl in boards.items() if nl is not None}
    lines = line_census(boards, walks)
    for s, lc in sorted(lines.items()):
        ok = False if lc["fail"] else (None if lc["undecided"] else True)
        res.append(dict(ok=ok, text="the asserted line %s: nothing on any board but its own source can drive it, and with "
                        "that source unpowered or unplugged its own pull-downs hold it under %.1f V against every pin's stated current, "
                        "every other part powered or not" % (s, VIL_LOW),
                        detail=" | ".join(lc["fail"] + ["UNDECIDED " + u for u in lc["undecided"]]),
                        boards=sorted((lc["carriers"] | lc["boards"] | lc["absent"])), absent=sorted(lc["absent"])))
    for t in table:
        bds = {o["board"] for o in t["options"]}
        present = [o for o in t["options"] if boards.get(o["board"]) is not None]
        if not present:
            res.append(dict(ok=False, text="%s: EMCON reaches it in hardware" % t["name"], detail="board absent", boards=sorted(bds),
                            absent=sorted(bds)))
            continue
        tried, oks, named, absent = [], [], set(), set()
        for o in present:
            good, why, nm, ab = _judge_option(boards, walks, lines, o)
            if good is not True:
                # EACH ASSERTED LINE ALONE (see reach()): an option a gate forces from either line passes when its path from
                # ONE line passes every check; the combined walk's answer stands otherwise, and an undecided answer on one
                # line replaces a combined FAIL, since the line that holds was never asked in the combined walk.
                for s1 in SOURCES:
                    if s1 not in walks1:
                        walks1[s1] = {kk: reach(nn, only=s1) for kk, nn in boards.items() if nn is not None}
                    g1, why1, nm1, ab1 = _judge_option(boards, walks1[s1], lines, o)
                    if g1 is True or (g1 is None and good is False):
                        good, why, nm, ab = g1, why1 + " (walked from %s alone)" % s1, nm1, ab1
                    if good is True: break
            tried.append("board %s, %s" % (o["board"], why)); oks.append(good)
            if good is True:
                named, absent = nm, ab; break
            named |= nm; absent |= ab
        ok = True if True in oks else (None if None in oks else False)
        res.append(dict(ok=ok, text="%s: EMCON reaches it in hardware (%s)" % (
            t["name"], " or ".join("%s %s on %s" % (o["board"], o["kind"], o["ref"]) for o in t["options"])),
            detail=" | ".join(tried), boards=sorted(bds | named | absent), absent=sorted(absent)))
    # classification: every part that names a radio is claimed, an accessory or a receiver
    claimed = {(o["board"], o["ref"]) for t in table for o in t["options"]}
    for k, nl in sorted(boards.items()):
        if nl is None: continue
        uncl, wrong, owing = [], [], []
        for ref, c in sorted(nl["comps"].items()):
            v = c.get("value", "")
            if not re.match(r"^(U|J|M|MOD|A)\w*", ref) or not RADIO.search(v) or NOT_A_RADIO.search(v): continue
            if (k, ref) in claimed: continue
            dec = [d for d in list(accessories) + list(receivers) + list(owed) if d["board"] == k and d["ref"] == ref]
            if not dec: uncl.append("%s (%s)" % (ref, v[:60])); continue
            if not re.search(dec[0]["value"], v, re.I):
                wrong.append("%s is declared as %r and its value now reads %r" % (ref, dec[0]["value"], v[:60])); continue
            if dec[0].get("owed"):
                owing.append("%s (%s) is declared %s, and what that rests on is owed: %s" % (ref, v[:40], dec[0]["why"], dec[0]["owed"]))
        ok = False if (uncl or wrong) else (None if owing else True)
        res.append(dict(ok=ok,
                        text="%s: every part that names a radio is a listed transmitter, an accessory or a receiver" % k,
                        detail="; ".join(["unclassified: " + u for u in uncl] + wrong + ["UNDECIDED " + o for o in owing]),
                        boards=[k], absent=[]))
    return res


def report(paths):
    """A readable table for the box logs: tx_inhibit.py <netlist>... (the letter is read from the file name)."""
    import boardtable as _bt
    boards = {}
    for p in paths:
        l = (_bt.letter_for(os.path.basename(p).replace(".net", ".kicad_pcb")) or "").upper()
        if l: boards[l] = parse_netlist(p)
    for r in judge(boards):
        # A RESULT THAT NEEDED AN ABSENT BOARD IS NOT A PASS (review of the second fix-up, minor 4): check_contracts
        # turns it into UNJUDGED through MISSING, and this report now says the same thing
        lab = "UNJUDGED" if r.get("absent") else {True: "PASS", False: "FAIL", None: "UNDECIDED"}[r["ok"]]
        print("%s  %s  [%s]%s" % (lab, r["text"], ",".join(r["boards"]),
                                  (" (absent: %s)" % ",".join(r["absent"])) if r.get("absent") else ""))
        if r["detail"]: print("      " + r["detail"][:1600])
    for k, nl in sorted(boards.items()):
        if nl is None: continue
        _got, stopped = reach(nl)
        for s in sorted(set(stopped)): print("  %s: the walk stopped at %s (no pin map)" % (k, s))
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    sys.exit(report(sys.argv[1:]))
