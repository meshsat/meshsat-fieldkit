### 20e. L8P-F05 corrected: the release on CELL+ alive (INFERRED)

**A dead CELL+ never sets the inhibit.** U47's channel 2 reads alive while R254 lifts its foot, that is while nothing is asked. It
**keeps** an inhibit that is set: Q52 then grounds the foot through DD7_N, and Q48 loads CELL+ through R256, so CELL+ reads alive
only when the breaker itself drives it. Round 9's dead point leant on board A's 200 kOhm against the LM5069's internal 1 MOhm, whose
tolerance is not printed; the latch leans on R256's 4.7 kOhm:

| BRK_VIN | The LM5069's resistor may fall to | CELL+ at 1 MOhm with the three FETs' 3 uA (25 C) | Round 9 |
|---|---|---|---|
| 16.8 V | 19.9 kOhm (0.020 of 1 MOhm) | **0.154 V**, 3.922 V under the dead reading | 2.80 V against 1.98 V |
| 29.2 V (the clamp) | 34.5 kOhm (0.035) | **0.213 V**, 3.864 V under it | 3.34 V against 1.98 V |

The latch reads dead while every source into CELL+ stays under **0.846 mA** together; the battery FETs' hot off leakage (not printed)
may reach 272 uA each before it matters. By the hold's end CELL+ has fallen under the dead reading unless the breaker drives it:
from VSYS's 17.375 V through R256 into CELL_FUSED's 104 uF (+20 %, ASSUMPTION) within 0.859 s, under the hold's least 1.341 s. The
release: the breaker's restart drives CELL+ over 4.774 V against R256's 3.57 mA at 16.8 V, inside IF-1's 0.81 A room.

