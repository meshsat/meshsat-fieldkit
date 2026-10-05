## C-DEV rev 2 (5 October 2026, 16:00 CEST; rev 1's SUPERVISOR term replaced, everything else of rev 1 stands)
Issued by the coordinator from Slot C's T10 round 5 (`fnd/p0t10` `5d772b24`, `T10-ROUND5.md` section 6, `l9t5_t10.out` 10g). Rev 1
carried rv-pwr's HIGH for the three STM32 supervisors (0.400 A a controller plus 0.060 A of its other parts, 0.46 A a regulator;
+5V_IOC 1.3800 A), the unbounded state that put the composed AP2112K LDOs at 160.1 C. Rev 2 carries the BOUNDED state of T10-A1's
contract row (FW-B20, FW-B21: VOS3, HCLK at most 144 MHz, the enabled peripherals named, each supervisor's own TXD dominant at most 2 %
of every 100 ms window per fabric; rev Y's rows as the cover, rev V smaller):
- for the thermal and the regulator rows: **0.2558 A a regulator** (rev Y; 0.1732 A rev V) with FW-B21's share and the circuit's own
  auxiliaries (0.0069 A at most, every resistor from the rail at the full rail, from the composed netlist); the controller alone
  0.2396 A at TJ 111.8 C at 76.25 C air;
- in the budget's own form (power only, conservative): 3 x (0.2396 + 0.060) x 3.3 = **2.966 W at +3V3_IOCx** in place of 4.554 W;
  **+5V_IOC 0.8989 A** in place of 1.3800 A (read as a regulator figure it would give 130.9 C because the declared 0.060 A over-covers
  the auxiliaries: it is not the thermal figure).
CONDITION: rev 2 holds only with FW-B20 and FW-B21 applied to `HW-FW-CONTRACT.md` (drafted in `records/l9t5/apply_hw_fw_contract_t10.py`,
unapplied, a Layer 5 row brought forward as a named prerequisite of the power gate) and the SHDN draft composed; until Layer 5 applies
them, a result on rev 2 is labelled "C-DEV rev 2 (conditional on FW-B20/B21)". A result on rev 1's HIGH is a LABELLED SCENARIO.
Consumers: P0-2 (the device rail I-03 and the return: Slot A recomputes U7's demand with the supervisor term of rev 2; rev 1's 7.472 A
at 4.9019 V is superseded for that term only), P0-3, P0-4 (eFuse U23/U24 downstream demands if the IOC rail is among them), P0-6, the
focused check cx45. L9P-F03's figures on rev 1 stay as given in the records that cite rev 1.

