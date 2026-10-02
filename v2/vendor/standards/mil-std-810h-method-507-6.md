# MIL-STD-810H, Method 507.6 (Humidity), Procedure II: the aggravated cycle the kit's E5 rests on

**What this file is.** A transcription of the lines this project CITES, not a copy of the standard. `v2/docs/TEST-PLAN.md` E5 names
"507, humidity: 10 cycles of 24 hours at 95 percent relative humidity, 30 to 60 C" and states no dwell or ramp; those levels are
Procedure II's aggravated cycle, whose profile is transcribed here so that task L4-E10 (`v2/docs/records/l4e10/`) can bound the
pack's temperature over it. Filed 2 October 2026 (MESHSAT-1357). The standard is a United States Department of Defense document
published through the ASSIST database of the Defense Logistics Agency; this folder transcribes standards rather than copying them, as
for every file here. Which edition and procedure E5 intends is the test plan owner's to confirm; the levels match this one.

| | |
|---|---|
| document | MIL-STD-810H, Environmental Engineering Considerations and Laboratory Tests; Method 507.6, Humidity (23 pages) |
| edition read | the base issue of MIL-STD-810H as downloaded from ASSIST on 2019-03-04T16:12Z (every page carries "Source: http://assist.dla.mil -- Downloaded: 2019-03-04T16:12Z"), the edition of `mil-std-810h-method-514-8.md` and `mil-std-810h-method-516-8.md`; whether Change Notice 1 altered these lines was not checked |
| source | the file read is a copy of the ASSIST download published at `https://cvgstrategy.com/wp-content/uploads/2019/08/MIL-STD-810H-Method-507.6-Humidity.pdf`, the same publisher's copies as the two files named above |
| fetched | 1 October 2026 23:27 UTC, curl from the runner, HTTP 200, 364,507 bytes |
| sha256 of the file read | `03ea61073665ff437b80f620cb1610df2c7995f999619d8030e523756c922441` |
| clauses transcribed | 2.3.2 c (Procedure II's number of cycles); 2.4.2 (operational checkout); Table 507.6-IX and the notes of Figure 507.6-7 (pages 507.6-13 and 507.6-14); 4.4.2.2 Steps 1 to 4 (pages 507.6-18 and 507.6-19) |

## 2.3.2 c, the number of cycles (page 507.6-7)

> c. Procedure II – Aggravated Cycle. For Procedure II, in addition to a 24-hour conditioning cycle (paragraph 4.4.2.2), the minimum
> number of 24-hour cycles for the test is ten.

## 2.4.2, operational checkout (page 507.6-7)

> If the test item is intended to be operated in a warm, humid environment, perform at least one operational checkout every five
> cycles during the periods shown on Figure 507.6-7.

## Table 507.6-IX, aggravated cycle, and the notes of Figure 507.6-7 (page 507.6-14)

| Time | Temp. (C) | RH |
|---|---|---|
| 0000 | 30 | constant at 95 percent |
| 0200 | 60 | |
| 0800 | 60 | |
| 1600 | 30 | |
| 2400 | 30 | |

> NOTES:
> 1. Maintain the relative humidity at 95 ±4 percent at all times except that during the descending temperature periods the relative
> humidity may drop to as low as 85 percent.
> 2. A cycle is 24 hours.
> 3. Perform operational checks near the end of the fifth and tenth cycles.

## 4.4.2.2, Procedure II, Steps 1 to 4 (pages 507.6-18 and 507.6-19)

> Step 1. With the test item installed in the test chamber in its required configuration, adjust the temperature to 23 ± 2 °C
> (73 ± 3.6 °F) and 50 ± 5 percent RH, and maintain for no less than 24 hours.

> Step 2. Adjust the chamber temperature to 30 °C (86 °F) and the RH to 95 percent.

> Step 3. Expose the test item(s) to at least ten 24-hour cycles ranging from 30-60 ºC (86-140 °F) (Figure 507.6-7) or as otherwise
> determined in paragraph 2.2.1.

> Step 4. At the completion of 10 or more successful cycles, adjust the temperature and humidity to 23 ±2 °C (73 ± 3.6 °F) and
> 50 ± 5 percent RH, and maintain until the test item has reached temperature stabilization (generally not more than 24-hours).
