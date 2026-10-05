### 22g. What stays open, and E11-45 (f) and (h)

- **V2-B1's claim is corrected:** the bleed counts the sources, and the record states one coupled limit (520.7 uA) beside the static
  one (0.846 mA).
- **OPEN:** the latch's timing with the breaker off at the hot bound, on record l8p's **E-14c** (the breaker pair's IDSS hot) and on
  this record's **E11-45 (f2)** (the bleed timed against the unit's own hold, the current into CELL+ read with both FET groups hot, at
  most 521 uA; U47's RESET current read at the set and with the breaker restarted, at most 5 mA) and **(h)** (each hold at least 0.1 s
  longer than (f2)'s bleed on the same unit). CELL_FUSED's 104 uF at +20 % is an ASSUMPTION.
- **Between 520.7 uA and 0.846 mA** (not reached at the hot bound): the hold may end with CELL+ still read alive and the breaker off;
  the inhibit releases, and a charge over board P's threshold (0.368 to 1.213 A) sets it again within 1.41 ms, once a hold; under
  the threshold it is the named residual of 20l (the latched FET at most 139.9 C, record l8p). That repeated cycle is not analysed
  further.
- **For record l8p (L8P-F06 and E-14c; nothing of its is edited here):** the latch's budget is two limits, the static 0.846 mA
  (round 10's again, so its 12j figures stand for the static room) and the timing 520.7 uA, which the pair alone fills from a
  103.9 C case, 2.9 K over its held case. E-14c's acceptance (the pair at most 388 uA at 101 C) keeps the timing with 85.9 uA in
  hand. Its copies of 20c to 20e and of this record's drafts are round 10's and are taken again at this round (the check V2's V2-B2,
  its owner's).

