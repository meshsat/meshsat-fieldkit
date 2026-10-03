<!-- COPIED INPUT (MESHSAT-1357, Layer 5 round 2, record l5r2, 3 October 2026). Source: branch fnd/l4e11 at commit b929d8be, file v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md, whose sha256 at that commit is 9812b52424f1ae07bf018e1f082ade64252bc47a6b6c821554a197ed0cb57aeb. Copied: section 18 (18a to 18d), from its heading to the line before the closing 'Not claimed' paragraph, verbatim between the two markers below; the body's own sha256 is 12f7feedb75841fd1b1b235518673522b157a408bd56c266ea348910a5fbde6f (l5r2_interfaces.py recomputes it and refuses a copy that differs). Copied because the commit is not in this branch's history; no git command reads it. -->
<!-- BODY BEGIN -->
## 18. The fans' feed after Layer 7's selection (F-L7-01, F-L7-02, F-L7-04; the B1 topology kept; out 18)

**The facts, cited from Layer 7's record** (`v2/docs/records/l7pwr/L7-FANS-AND-TH1.md` at `2087060b`, sections 2d, 2e, 2f and 5; not in
this tree): D-18 settled on **Sanyo Denki 9WL0612P4H001** (the two mixers, board E's J_FAN1 and J_FAN2) and **9WPA0412P6G001** (the three
cooler fans, board B), both 12 V with a printed operating range of **10.8 to 13.2 V**, 0.17 A each at 12 V, four wires (12 V, GND, pulse
sensor, PWM), IP68, -20 to +70 C; no fan of any maker read prints a range covering VSYS_E's 9.494 to 17.375 V, and no 5 V IP68 40 mm fan
exists in the lines read. **Section 15a's two mixers directly on VSYS_E are withdrawn**, and the five fans at full speed would have drawn
1.277 A (Layer 7, at an efficiency of 0.90) on the branch this record declared at 1.0 A.

### 18a. The mixers' regulated 12.0 V rail on board E

A buck cannot hold 12.0 V from the 9.688 V supplement floor and a boost cannot from 17.375 V: the rail is a buck-boost from VSYS_E. Three
candidates on their makers' printed data (all three sheets fetched from the makers and filed held; prices NOT READ, LCSC's search refused
this host):

| | Input | Current limit | Package, thermal | What else it needs | Reads |
|---|---|---|---|---|---|
| (V1) ADI LTC3115-1 (Rev. E) | 2.7 to 40 V | inductor 2.4 / 3.0 / 3.7 A | FE TSSOP-20 EP, thetaJA 38 C/W; E grade -40 to 125 C | TA04's 12 V 1 MHz network: one 10 uH inductor, 10 uF in, 22 uF out, FB 1M / 90.9k, VC 40.2k and 820 pF, feed-forward 10k and 33 pF, RT 35.7k; internal 9 ms soft start | TA04b about 93 % at 0.34 A for 10.6 and 12 V in (typical); about 1.2 A of load at 12 V out near 9.5 V in (G12, 22 uH 500 kHz, typical) |
| (V2) TI TPS55340 (SLVSBD4E) as a SEPIC | 2.9 to 32 V | switch 5.25 to 7.75 A | RthJA 43.3 C/W | a coupled inductor and a coupling capacitor | efficiency printed for a boost only; the SEPIC's NOT PRINTED |
| (V3) TI TPS63070 (SLVSC58B) | 2 to 16 V | input 3.05 to 4.15 A | thetaJA 63 C/W | | **fails** VSYS_E's 17.375 V |

**SELECTED (SESSION): (V1)**, U22 LTC3115EFE-1 as ADI's TA04, with L4 Coilcraft XAL6060-103ME (10 uH, DCR 29.82 mOhm, Isat 5.0 A over the
3.7 A limit, Irms 7.0 A; Coilcraft 887-1, held), PWM/SYNC to VCC (fixed 1 MHz). *Why:* the only one of the three whose printed input range
covers VSYS_E and whose current limit is of the fans' order; one inductor and the maker's own 12 V network. The output is **12.001 V
(11.512 to 12.431 V at FB's limits with the drafted 1 % divider)**, inside the fans' 10.8 to 13.2 V by 0.71 V below and 0.77 V above. *Reverse:* a fan whose maker prints a range covering VSYS_E.

**Its RUN divider** (R103 1.5M / R104 255k): enabled at **8.33 V** (7.98 to 8.67 V at the comparator's limits), disabled at **6.89 V** (6.55 to
7.23 V), so under the floor and over U12's 3.8 V start. This is what breaks the interaction 17a could not: a fan fault that drives U22 to its
2.4 A limit against U42's limit lets VSYS_E fall only to U22's disable, where U22 stops and VSYS_E recovers; the controller stays up and
the fault appears as a rail hiccup, not a controller reset (INFERRED; the same model reproduces TA04's own 10.6 / 8.7 V within 0.15 V).

**Heat into the case** (MODELED; the efficiency 0.85 is an ASSUMPTION, read 5 points under TA04b's typical curves): **0.72 W** at full
speed (4.08 W of fans), 0.254 W at the plan's 1.44 W; TJ 97.4 C at +70 C air on thetaJA 38. **Its protection:** U22's own current limit and
soft start, behind U42, the branch's limiter; no fuse of its own.

**The draft** (`apply_gen_sch_e_aux.py`, rewritten; the generator's own text is unchanged where the edits do not reach): U22 and its network
(C135 to C141, R103 to R109, L4) on the FE and XAL6060 lands; J_FAN1 and J_FAN2 four pins (12 V, GND, PWM, TACH); Q9 and Q10 kept as open-drain
drivers of the fans' PWM inputs (the fan's PWM level NOT READ, Layer 7); D7 and D8 and the FANn_SW nodes removed (the old node loop is
emptied, its text left for board E's owner to delete); +12V_FAN declared (source L4, 0.34 A, converted at 0.85). The land key HTSSOP20EP
is the 4.4 x 6.5 mm 0.65 mm pitch exposed-pad land board A's draft uses for TI's PWP; the parts stream checks it against ADI's FE20 drawing.

### 18b. The branch's declared current and U42's setting, re-derived

At the floor with both fans at full speed U22's input is **0.5208 A** (4.08 W over 0.85 at 9.508 V, plus 16 mA of PWM-mode quiescent
current), and with U12's 0.8 A the branch is **1.3208 A, declared on IF-AE-DOCK pin 1** (was 1.0 A; Layer 7's 1.277 A at 0.90); at the
plan's duty 0.9942 A. Against **U42's least limit 1.4713 A: 89.8 %, 0.1504 A in hand: not exceeded, so R228 stays 11.0 kOhm** (I(OL)
1.4713 to 1.8018 A). The contact at 37.7 % of 3.5 A, 8.54 K by w3de's rise; the sustained-overload figures of 16e and the retry duty of
17a are unchanged. **The drop** at the floor with 1.3208 A is 0.1795 V, VSYS_E 9.508 V; at U42's least limit 9.494 V; U22 holds 12.0 V from
2.7 V up, so VSYS_E's floor no longer reaches the fans.

**The fans' start** (NOT READ, Layer 7): with one fan running and U12 on, U42's 0.1504 A of room leaves 1.21 W at the rail for the other
fan's start, 1.6 times its running power, before U42 limits; U22 itself delivers about 1.2 A at the floor. The fan, not the rail, is the
unknown (E11-35, E11-38 f).

### 18c. The stagger (E11-39) restated

U22's 9 ms soft start covers the rail's own rise only; a fan's start surge comes when its PWM duty rises. **The stagger stays**: one fan
at a time, each by a PWM-duty ramp into the fan's PWM input (Layer 7's F-L7-05), never while U12 or U22 starts.

### 18d. Board B's cooler fans: a finding, not a draft

Board B's generator (`gen_sch_b.py`, read): J_FAN1 to J_FAN3 carry the slot rail +5V_Sn at **5.1 V** on pin 1 and declare the fan at 0.1 A on
it; no +12V net is declared on the board. **The feed does not cover the coolers' 10.8 to 13.2 V and needs the same regulated 12.0 V**:
**E11-40**, a finding for board B's owner with the rows (Layer 7's F-L7-02): a per-slot step-up from +5V_Sn (Layer 7's 0.436 A each at
full speed, keeping an empty slot off) or a 12 V feed from board A over the bay harness; the header's pin 1 becomes 12 V, the slot
budget's fan row 2.0 W at 12 V, the module's Fan_PWM and Fan_Tacho kept.

**Status, section 18:** the mixers' feed SELECTED and DRAFTED (U22, applied with E11-33); the declared current 1.3208 A and U42's setting
kept; board B OPEN as E11-40; the fans' start current and PWM level stay Layer 7's and E11-35's.


<!-- BODY END -->
