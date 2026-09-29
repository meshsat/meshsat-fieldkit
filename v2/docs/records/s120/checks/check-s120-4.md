mergeable: yes

# Independent check of stream s120, round 4 (S-120, fourth issue: CHECK-3's r1 to r3)

AI review (reproduced by running), not a qualified engineering review. 29 September 2026, 19:17 CEST. Checker did not
write the work.

Checked: `fnd/s120` at `1561ff88d89296037b9dd32c2d95b26f628baede` (confirmed), three commits on `8c504a24` (`2ab673ab`,
`a997d08a`, `1561ff88`), all as the owner, no trailer, only the six s120 records touched, no en or em dash in them. Clone
`<scratch>/chk-s120` detached at the tip; `_int14` at `b874b744` for main's tools.

## Blocking

None.

## Minors

None new.

## The four items

1. **S-124's closing condition.** As the script writes it, it equals the README's quotation word for word (compared as
   parsed strings on the applied registry). A word level diff against round 3's applied text shows three insertions and no
   deletion:
   * "of CH_SW1, CH_ACN and U3's VBUS pin" (the bus referred readings);
   * the CH_SW2 clause with Q9 and Q10, plus "ACP less ACN read across U3's pins";
   * "ACP less ACN inside 0.5 V".

   The rating list gains "ACP less ACN 0.5 V absolute". Every round 3 clause is kept: Q7 from CH_ACN to CH_SW1, the 20.96
   and 23.40 V references, 30 V and 32 V, the minus 2 V and minus 4 V (25 ns) limits, the OVP trip reading, and remedies
   measured the same way. The rest of S-124's text is unchanged. The S-120 closing evidence and S-111's addition equal round
   3's apart from the commit sha.
2. **r1's basis is right.**
   * Q9 is drain CH_SW2, source GND (netlist): its VDS is CH_SW2's peak.
   * Q10 is drain VBAT, source CH_SW2: its VDS is VBAT less CH_SW2's lowest.
   * SW2 sits at VBAT with Q10 on in buck mode and switches only in buck boost (Table 9-3 p.27).
   * SYSOVP's 20.0 V maximum (p.14) turns the converter off, so it is the highest VBAT at which SW2 can still switch and
     ring. Referring the overshoot over the measured VBAT to 20.0 V is the right ceiling.
   * The pack open event's 24.27 V at D1 comes after the converter has stopped, so it carries no switching ring.

   The r2 estimate reproduces. The CH_ACN ring (1 nH against 11 nF) is 4.74 V at 48.0 MHz. Through the pin filter
   (200 ns, R146, R147, C121) it arrives as 0.079 V, the same with the exact single pole; labelled INFERRED.
3. **`vbus20_bound.py`** reprints the committed `.out` byte for byte (exit 0). Against round 3's output only the header
   ("fourth issue") and four added lines in section 10 differ; every figure is unchanged.
4. **Registry.** The tip's registry equals `b874b744`'s (sha256/16 1dde1fd16f4e260e); `--check` wrote nothing. On scratch
   copies of both:
   * S-120 closed by `commit 1561ff88d89296037b9dd32c2d95b26f628baede`.
   * S-124 opened (SESSION, OPEN).
   * REQ-015 waits on S-106, S-107, S-111, S-124.
   * The two applied copies are byte identical; a second run refuses, and `8c504a24` is refused (README differs).
   * `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings on all four copies (main's tools at `b874b744` and
     the tip's).

## Counts

Blocking 0. Minor 0. CHECK-3's r1, r2, r3 answered (r4 was mine). Clauses of the round 3 closing test lost: 0; clauses
added: 3. `.out` reprinted byte for byte. Registry copies 4 of 4 at 0 errors and 0 warnings; S-124 opened on both;
`closed_by` 40 characters.

<!-- Filed from the checker's report; local paths replaced by <scratch>/ and <local path> (records/int15/apply_check15*.py). Where the report itself spoke of that substitution, its words read garbled. -->
