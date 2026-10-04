### 20d. The delays (INFERRED; each element's bound named)

| Step, from the return falling under 0.7755 V | At most |
|---|---|
| U48's release (tCTR with no capacitor, MAKER) | 40 us |
| DD7_T to Q50's 2.5 V (R250 1 MOhm into 110 pF, ASSUMPTION: Q50's 50 pF typical Ciss doubled and U48's pin) | 41.2 us |
| Q51 on (R251 and R252 into 1.5 times its typical 645 pF) | 25.2 us |
| DD7_H over 0.808 V (the arm's time constant at most 71.5 us) | 5.6 us |
| U47's CTS1 (Equations 5 and 6, C248 +-5 %, RCTS 88 to 122 kOhm) | 0.382 to 0.710 ms |
| Q49 on (R82 and R83 into 1.5 times its typical Ciss) | 26 us |
| **the inhibit set** | **0.85 ms**, under the interface's 1 ms |

**The arm completes before the set:** the set comes at least 0.382 ms after DD7_H passes 0.808 V, and board P's pull holds the trigger
while the charge flows, i.e. until the inhibit stops it (Q44's own pull lasts at least 78.6 ms). With the arm's time constant at most
71.5 us (R84 into C241's 1.265 uF most) DD7_H is 0.99519 of the way, so the hold starts from at least **11.145 V** (VSYS_MIN's 12.054 V
less D26's 0.855 V at 10 mA). **The charge through the off breaker ends within 1.41 ms** of passing board P's threshold (its pull
0.56 ms and board A's set), against E-14's 10 ms.

**The hold.** DD7_H falls from 11.145 V through R85 (1 %) and C241 (0.6502 uF at its least: K, X7R's 15 % and 15 % under DC bias,
ASSUMPTION) to U47's OV release, 0.7924 V at most, against every sink on the node: D26's reverse leakage 0.807 uA at 86.25 C
(INFERRED, log-linear between the sheet's 25 nA at 25 C and 30 uA at 150 C), SENSE1's 100 nA (MAKER) and C241's insulation 0.292 uA
(ASSUMPTION). It lasts **at least 1.341 s** after the return rises: 0.341 s over the interface's 1.0 s and 0.393 s over the breaker's
restart (0.9477 s). At most 5.82 s (the clamp's VBAT, the sinks reversed). It still reaches 1.0 s with D26's leakage 2.76 times the
inferred figure. **It always ends:** Q51's off leakage, 43.6 uA at 86.25 C (the sheet's 55 C row doubled every 10 K, INFERRED), holds
DD7_K at 0.436 V through R253, 0.339 V under the OV release's least 0.7756 V.

