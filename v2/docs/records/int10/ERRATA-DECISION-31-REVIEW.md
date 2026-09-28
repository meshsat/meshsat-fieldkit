# Erratum: the review of decision 31, the wall port eFuse's limit

MESHSAT-1357, integration set 9, stream s99reg, 29 September 2026. AI engineering work; prototype design, nothing
built, ordered or measured.

**Where:** `v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md` line 244, the VBUS_WALL paragraph of board A's wall USB
host port: "VBUS_WALL is 5.0 V behind the eFuse U32 (limit 0.89 A)".

**Correction:** U32's limit is **0.9142 A nominal**. TPS2596 equation 7 (TI SLVSET8A, May 2019, revised August 2019,
printed p.28) is RILM = 903 / (ILIM - 0.0112); the page's worked example, 903 / (1 - 0.0112) = 913.2 ohm, fixes the
sign. With R186 at 1.00 kOhm, ILIM = 903 / 1000 + 0.0112 = 0.9142 A. The 0.89 A came from the generator's comment,
which carried the sign as + (stream s99a corrected the generator, `v2/docs/records/s99a/README.md` section 2; the
independent check of s99a reproduced it). No maximum at 1 kOhm is published: the 909 ohm row of SLVSET8A p.6 scaled to
1 kOhm gives about 0.956 A, an estimate.

**What the correction changes in the review:** nothing it concludes. The paragraph reads the ESD array's clamping
voltage against U32's output rating and C156's hold-up in a discharge; the limit is quoted as context and enters no
figure of the paragraph (0.055 V at 8 kV and 0.10 V at 15 kV are C156's, independent of the limit).

**Why the review is not edited:** its sha256 (`0948170232...`) is pinned three times in `v2/ecad/tools/pcb_board_holds.yaml`,
as the review requirement of the holds of boards A, D and E, and the reviewed port set cites the review. Editing it
turns each hold's review requirement to "re-review it", and the pinning script
(`v2/docs/records/d8dec31/apply_holds_review_pin.py`) cannot re-pin: it refuses unless the netlists in the tree are the
ones the review read (board A's has moved since, and moves again with decision 55's regeneration). The review stays as
filed; `v2/docs/records/int10/apply_pages_s99.py` asserts it is byte-identical to its pins and that this erratum is
present. Any later review of board A should quote 0.9142 A; none is owed by the regeneration itself, since the decision 31 hold's review pin moved to the new netlist on a parsed proof and reads met (set 9's AI check, minor item M4).

**Other places the wrong-sign figure stays, as history (not edited):** `v2/docs/records/r4a/r4-decisions.md` line 196
("ILM 1.00 k = 0.89 A") and `v2/docs/records/r4b/r4-interfaces.md` line 11 (records of round 4 streams), and the frozen
handover snapshot `v2/release/handover/H1/` (its copies of `gen_sch_a.py`, `pcb_interfaces.yaml`, `ASSEMBLY.md` and the
two records). Each reads 0.9142 A nominal by this erratum. The live pages are corrected by
`v2/docs/records/int10/apply_pages_s99.py` (HW-FW-CONTRACT.md FW-A07, ASSEMBLY.md section 4) and
`apply_if_ab_power_s99.py` (pcb_interfaces.yaml IF-AB-WALL).
