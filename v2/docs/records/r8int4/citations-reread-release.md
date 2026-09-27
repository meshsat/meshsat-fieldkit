# The registry's citations re-anchored from 95e078a1 to 08f3665a at the release check of layers 1 to 3

MESHSAT-1357, 27 September 2026, branch `fnd/r8int4` (not pushed). The layer 3 release review
(`v2/docs/reviews/REVIEW-LAYER-3-RELEASE-2026-09-27.md`, finding R3) found the registry's citation anchor stated three
ways and eleven citations in eight records landing on other text at `f2b7fa66`, because the layer 5 and layer 7 merges
(`0da2778b`, `c351115d`) moved `PANEL.md` two lines down after its line 175, `ASSEMBLY.md` 21 lines down from its line 32,
and rewrote `ARCH-PCB-B-IOHA.md` line 169 in place, after the re-anchoring of `53292f81` had set `sources_read_at` to
`95e078a1`. Prototype design: nothing here is measured.

**What was run.** The layer 3 closer's apply script's `reanchor()` as a preview (`reanchor_preview.py`, the diff it
would write, nothing written) on the committed `08f3665a`, then `reanchor_release.py`, which applies the ten moves the
preview found by record id with asserted old text, sets `sources_read_at: 08f3665a`, and compares EVERY `file:line` in
every `source` field that names no commit of its own: the lines at `95e078a1` under the old number against the lines at
`08f3665a` under the new one. 280 citations compared; 21 name their own commit ("as read at ...") and are left.

**One defect of the apply script's re-anchoring, not taken.** On a citation that already names the commit it was read
at (for example `"v2/docs/V2-SPEC.md:76 (as read at eadbe571)"` in CFL-016 and SPD-006), the preview appended a second
"(as read at 95e078a1)" whenever the cited line had changed since. Such a citation says what the source SAID at the
commit it names, so it stays as it is; the five the preview would have doubled are left unchanged.

**The ten moves** (text only moved; the cited lines read the same, byte for byte):

| Record | Citation at `95e078a1` | At `08f3665a` | What it cites |
|---|---|---|---|
| REQ-012, REQ-033 | `PANEL.md:187` | `PANEL.md:189` | section 8's dimmer paragraph (the TX lamp never below 10 %, dark in BLACKOUT) |
| REQ-013, REQ-060 | `PANEL.md:191` | `PANEL.md:193` | section 9's indicator semantics |
| REQ-033 | `PANEL.md:185` | `PANEL.md:187` | the BLACKOUT row of section 8's lighting table |
| REQ-034 | `PANEL.md:184` | `PANEL.md:186` | the NVG row (2 % duty, red and amber only) |
| REQ-060 | `PANEL.md:197` | `PANEL.md:199` | the SOS indications paragraph |
| CON-006 | `ASSEMBLY.md:81` | `ASSEMBLY.md:102` | the corrected paragraph on the pack pocket under B21 |
| REQ-066 | `ASSEMBLY.md:159` | `ASSEMBLY.md:180` | the dock interface paragraph |
| REQ-066 | `ASSEMBLY.md:173` | `ASSEMBLY.md:194` | section 7's removal procedure (read by hand, below) |

**Read by hand: the three whose text changed where it stands.**

| Record | Citation | What changed | What the record relies on | Read |
|---|---|---|---|---|
| CON-004 | `ARCH-PCB-B-IOHA.md:169-173`, same lines | line 169 names the part as the STM32H743VIT6 ("an STM32H753VITx in this build of 9 September"); lines 170 to 173 unchanged | each supervisor's own AP2112K-3.3 branch off `+5V_DEV` and its two TCAN334D transceivers on two independent fabrics with separate termination (three supply branches, two fabrics) | the same sentences, the part name aside: holds |
| REQ-007 | `V2-SPEC.md:53-62`, same lines | line 59 (the release check, correction 30) names the hardware EMCON lamp `D22` beside the sixteen LEDs; the rest of the panel table is unchanged | the panel's controls and indicators: MAIN, PI and TEST, the three locking toggles, LIGHTING, sixteen indicator LEDs `D1` to `D16`, the sounder, the e-paper, the ambient light sensor | the sixteen LEDs and every other item are still stated; the lamp added beside them is CON-021's and S-44's subject, not this record's: holds |
| REQ-066 | `ASSEMBLY.md:173`, now `:194` | the case set's correction (`c351115d`) adds the frame's 8.25 mm margin (M7), that the frame and its setting legs stay in the case and that the ten plate screws are 6-32 from above | the removal order: lid, the plate's screws, the plate lifted, the stack lifted straight up, the pack out after its XT60 and SMBus are unplugged | the order and every step are unchanged: holds |

**The anchor stated once.** `sources_read_at` names `08f3665a`; `START-HERE.md` section 9 now says a registry citation
is at the commit `sources_read_at` names, and the handover pages' own `file:line` citations stay at `e3aedb25`. The
commit is on no remote branch until the integrating session pushes the branch (this finalizer does not push).
