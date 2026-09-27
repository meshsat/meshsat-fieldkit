# MIL-STD-810H, Method 514.8 (Vibration), Annex C: the composite wheeled vehicle levels the kit's E2 rests on

**What this file is.** A transcription of the lines this project CITES, not a copy of the standard. `v2/docs/TEST-PLAN.md` E2 names
"514, vibration, composite wheeled vehicle profile, 1 hour per axis" and states no level; the QMX lid tray r2's record
(`v2/cad/lid_tray_qmx_r2_check.py`, section D) reads the pads' preload against the level transcribed here. Filed 27 September 2026
(MESHSAT-1357, stream w5tray). The standard is a United States Department of Defense document published through the ASSIST database of
the Defense Logistics Agency; this folder transcribes standards rather than copying them, as for every file here.

| | |
|---|---|
| document | MIL-STD-810H, Environmental Engineering Considerations and Laboratory Tests; Method 514.8, Vibration (189 pages with its annexes) |
| edition read | the base issue of MIL-STD-810H as downloaded from ASSIST on 2019-03-04T16:12Z (every page carries "Source: http://assist.dla.mil -- Downloaded: 2019-03-04T16:12Z"); whether Change Notice 1 of MIL-STD-810H altered these lines was not checked |
| source | the file read is a copy of the ASSIST download published at `https://cvgstrategy.com/wp-content/uploads/2019/08/MIL-STD-810H-Method-514.8-Vibration.pdf`, the same publisher's copy as `mil-std-810h-method-516-8.md` |
| fetched | 27 September 2026 21:13 UTC, curl from the runner, HTTP 200, 3,564,432 bytes |
| sha256 of the file read | `cc8ec677d3b06eaab5c24244f10ee8acf52dba950ab25c645deeb99c9b177650` |
| clauses transcribed | Annex C, paragraph 2.1.3 b (2), composite wheeled vehicle: its first two sentences, "Test Schedule", "Test Time", "Recommended Control Scheme", and the RMS acceleration lines with their notes 1 and 3 (pages 514.8C-11 to 514.8C-13) |

## Annex C, the composite wheeled vehicle (pages 514.8C-11 to 514.8C-13)

> (2) Composite wheeled vehicle (CWV). Exposures are shown in Figure 514.8C-6, and are followed by the respective data table
> (Table 514.8C-VII). If the orientation of the test item is unknown or variable, see exposure levels shown in Figure 514.8C-7 and
> Table 514.8C-VIII.

> Test Schedule: Secured Cargo - Composite Wheeled Vehicle

> Test Time: 40 minutes per axis

> Recommended Control Scheme: Average (Extremal control may be appropriate for some applications). Based on the field data
> characteristics and the conservatism associated with the composite vehicle VSD process, drive limiting to 3 sigma is recommended.

> RMS Acceleration:1,3 (G-rms): Vertical - 2.24; Transverse - 1.45; Longitudinal - 1.32; Envelope - 2.24.

Note 1: "Approximate values for a Gaussian random distribution which may vary based on the control system and spectral resolution.
Peak velocity and displacement values are based on an acceleration maximum of three times the standard deviation (3 sigma) and a
spectral resolution of 1 Hz."

Note 3: "For test items for which the test item orientation is unknown or variable the Envelope profile should be run for all three
axes (Figure 514.8C-7 and Table 514.8C-VIII)."

The break points of Tables 514.8C-VII and 514.8C-VIII (the spectra themselves) are not transcribed: nothing in this tree reads them
yet. A shaker test of E2 needs them from the standard.

## What this project reads from it

The kit is carried in any orientation, so the envelope applies: 2.24 g rms on each axis, 6.72 g at the 3 sigma the standard limits the
drive to, measured at the vehicle's cargo bed, which is the input to the closed case. It is NOT the vibration at a part inside the
case: the case and the lid respond to it, and their response is not known until E2 is run. The standard's 40 minutes an axis stand for
805 km; `TEST-PLAN.md` E2 runs 1 hour an axis, which is longer at the same level.
