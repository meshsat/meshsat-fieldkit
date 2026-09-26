# Battery and protection review packet (board P and the pack)

Prototype design: nothing here has been built or measured, and this packet does not release anything to fabrication.
It is prepared for the qualified battery-and-protection review the owner approved (D-09) and answers section 2 of the
review of 26 September 2026 (`v2/docs/reviews/2026-09-26-foundation-progress-review.md`).

Start at **`REVIEW-REQUEST.md`**: the index, the findings, the questions for the reviewer and the review route.
Round 8 (26 September 2026) adds **`THERMAL-COORDINATION.md`**, the pack's temperature thresholds as one coordinated
ladder, for finding B of the second checkpoint review (`v2/docs/reviews/2026-09-26-second-checkpoint-review.md`); the
ladder is not closed while finding BAT-F20 is open (the charge FET held off during discharge, `REVIEW-REQUEST.md` Q-P18).
`MANIFEST.md` names the exact revision and the sha256 of every file and of every document cited; the packet is sent only
after `python3 v2/docs/review-packets/battery/evidence/check_manifest.py` prints `RELEASE CHECK PASS` at the commit whose
link is sent (`REVIEW-REQUEST.md` section 5).
