**DONE:** nine exact rows (R-01 to R-09) for the coordinator's adoption of the P0 list's revision 3 from Slot K's draft 2, each with its old and new text and the record lines that decide it; every decimal figure, quotation and line citation of draft 2 re-read against the record it cites (section 3). **NOT DONE:** nothing applied: `v2/docs/records/l4close/P0-POWER-LIST.md` is the coordinator's file. **NEXT:** the coordinator adopts revision 3 with R-01 to R-09 applied.

# The P0 list, revision 3: the corrections to Slot K's draft 2 before adoption (W7, MESHSAT-1357, 6 October 2026)

**What this is.** Row by row, the exact corrections to apply to Slot K's draft of the P0 list's revision 3, `v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md` on branch
`fnd/recpack` at `35dca639d1f7cbc72e9649b8bb327f65caa686c9` (draft 2; not in this branch's history, so cited as text only and read with `git show`), before the
coordinator adopts it as `v2/docs/records/l4close/P0-POWER-LIST.md`. Written by worker W7 on branch `fnd/w7rem` from set 30's
integration commit 2c, `53a68c7ce8a8b964d8d3905b4a769b50db096040`. It accepts, closes and promotes nothing, changes no state of any
row and no verdict of any check; every row restates a figure, a quotation or a citation as the record it cites prints it. Prototype
framing: nothing in the kit is built, bought, powered or measured.

**Line numbers.** "Line N" of a row is draft 2's line N at `35dca639`. A record line written `path:N` is at `bbba3e53` (draft 2's own
convention, its line 23); another revision is written `<sha>:path:N`. Kinds: **fragment** (the Old text occurs exactly once in draft
2, on that line; the New text replaces it), **every** (every occurrence), **carried** (draft 2 already carries the correction; the
adoption keeps it; nothing to apply).

## 1. The findings answered

- Slot H's set 31 record: "The case at the cap: 15.1307 V in the P0 list ([P0L:18]) against 15.1308 V in the F01 output ([F01:145]);
  the page uses F01's; the P0 list is the coordinator's" (`v2/docs/records/l4e9/SET31-CHANGES.md:109-110`), which the brief reads
  with Slot K's result draft (`v2/docs/records/int30/RESULT.draft2.md` at `35dca639`, text only; its section 2, row 5, keeps "C-ALLTX
  rev 3 at 15.1308 V" unmoved): R-01, with K-04's band R-02.
- The brief's second item: every other figure of draft 2 checked against the record it cites (section 3); each mismatch is a row.
- The DESK-gate draft's K items whose file is the P0 list (branch `fnd/dgate` at `249e9e47`,
  `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md:314` and `:325`, text only): K-04 (R-01, R-02) and K-15 (the list read as
  revision 2 until revision 3 is adopted: the adoption itself, the coordinator's; nothing to apply here). K-12 is carried on this
  list's side by R-08.

## 2. The rows

### R-01. P0-1: the case at the cap, 15.1307 V (revision 2) against 15.1308 V (the records); K-04

- Kind: carried
- Line: 51
- Check: `bbba3e53:v2/docs/records/l4close/P0-POWER-LIST.md:18` reads "the case at 15.1307 V, MODEL margin 0.369 V"
- Check: `bbba3e53:v2/docs/records/l9t5/l9t5_f01.out:145` reads "need 15.1308 V, a MODEL margin of 0.3692 V under 15.5 V"
- Check: `bbba3e53:v2/docs/records/l9t5/l9t5_case.out:193` reads "need 15.1308 V: MEETS against REQ-018's 15.5 V, margin 0.3692 V (MODEL;"
- Check: `53a68c7c:v2/docs/records/l9t5/l9t5_f01.out:145` reads "need 15.1308 V, a MODEL margin of 0.3692 V under 15.5 V"
- Check: `06077cee:v2/docs/records/l9t5/l9t5_f01.out:131` reads "need 15.1307 V, a MODEL margin of 0.3693 V under 15.5 V"
- Check: `35dca639:v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md:51` reads "C-ALLTX rev 3 at the cap: 15.1308 V, MODEL margin 0.3692 V"
- Check: `35dca639:v2/docs/records/l4close/P0-POWER-LIST.rev3.draft2.md:57-58` reads "row reads the case at 15.1307 V"
- Why: 15.1307 V (margin 0.3693 V) is round 2's print at cx45's revision `06077cee`, beside round 2's band; the records print 15.1308 V (MODEL) at `bbba3e53` and at this branch's base. Draft 2 already carries the records' figure (its line 51) and names revision 2's (its lines 57 to 58): no text change; the adoption keeps both sentences. The table's P0-1 cell prints no case voltage, so nothing there is corrected
- Class: PRESENTATION OR BINDING (the records' figure; no figure computed here)
- Old:

```text
the case at 15.1307 V, MODEL margin 0.369 V
```

- New:

```text
C-ALLTX rev 3 at the cap: 15.1308 V, MODEL margin 0.3692 V
```

### R-02. P0-1: the cap's band, 6.3522 to 6.9257 A (revision 2) against 6.3518 to 6.9259 A (the record); K-04's other half

- Kind: fragment
- Line: 58
- Check: `bbba3e53:v2/docs/records/l4close/P0-POWER-LIST.md:18` reads "cap 6.3522 to 6.9257 A"
- Check: `bbba3e53:v2/docs/records/l9t5/l9t5_f01.out:109-110` reads "round 2 held them nominal: 6.3522 to 6.9257 A"
- Check: `bbba3e53:v2/docs/records/l9t5/l9t5_f01.out:132` reads "6.3518 to 6.9259 A over every corner (MODEL"
- Check: `53a68c7c:v2/docs/records/l9t5/l9t5_f01.out:132` reads "6.3518 to 6.9259 A over every corner (MODEL"
- Why: draft 2 prints the record's band (its lines 47 to 48) but does not name revision 2's band as superseded, which the DESK-gate draft's K-04 lists beside the case figure (branch `fnd/dgate` at `249e9e47`, `v2/docs/records/l4close/L4-DESK-GATE-ASSESSMENT.draft.md:314`, text only)
- Class: PRESENTATION OR BINDING (the record's figure named beside revision 2's)
- Old:

```text
the revision 3 list carries the records' figure.
```

- New:

```text
the revision 3 list carries the records' figure. The same row reads the cap at 6.3522 to 6.9257 A, round 2's band with R553 and R559 held nominal (`v2/docs/records/l9t5/l9t5_f01.out:109-110`), where the record reads 6.3518 to 6.9259 A over every corner, MODEL (`:132`): the revision 3 list carries the record's band.
```

### R-03. The citation of 'the second negative on the method, which ends it' (draft 2's line 15)

- Kind: fragment
- Line: 15
- Check: `bbba3e53:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:3` reads "the second negative on the method, which ends it"
- Check: `bbba3e53:v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:206` reads "Do not repeat this review method"
- Why: the words sit on the filing's line 3; line 206 is cx46's smallest next action, which says "Do not repeat this review method" and not the words quoted
- Class: PRESENTATION OR BINDING (a citation re-pointed)
- Old:

```text
which ends it (`v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:206`)
```

- New:

```text
which ends it (the filing's head, `v2/docs/records/l4close/CHECK-CX46-P0-RECHECK-4d0ff8a2-AS-RECEIVED.md:3`; cx46's own "Do not repeat this review method", `:206`)
```

### R-04. A quotation of the connected output (draft 2's lines 106 to 107)

- Kind: fragment
- Line: 106
- Check: `bbba3e53:v2/docs/records/l9t5/l9t5_connected.out:362` reads "L4-E9's own output refuses on this tree at its L4-E11 pin"
- Why: the record's words; the draft's quotation dropped "on this tree"
- Class: PRESENTATION OR BINDING (a quotation made verbatim)
- Old:

```text
"L4-E9's own output refuses at its
```

- New:

```text
"L4-E9's own output refuses on this tree at its
```

### R-05. P0-6: the change list's count, which set 31 moved (not named by draft 2)

- Kind: fragment
- Line: 32
- Check: `bbba3e53:v2/docs/records/l4e9/l4e9_power_path.out:1310` reads "117 changes; none APPLIED"
- Check: `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:1310` reads "118 changes; none APPLIED"
- Check: `53a68c7c:v2/docs/records/l4e9/l4e9_power_path.out:1310` reads "118 changes; none APPLIED"
- Why: draft 2's own rule names a statement the set 31 merge changes, with its line at `6fe398e9` (its lines 7 to 8); this one was not named
- Class: PRESENTATION OR BINDING (both revisions' figures printed, each with its revision)
- Old:

```text
(`v2/docs/records/l4e9/l4e9_power_path.out:1310`: "117 changes; none APPLIED")
```

- New:

```text
(`v2/docs/records/l4e9/l4e9_power_path.out:1310`: "117 changes; none APPLIED"; after `6fe398e9`, with set 31's R-246, "118 changes; none APPLIED", `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:1310`)
```

### R-06. P0-7: D-16's state as L4-E9's output prints it after set 31 (not named by draft 2)

- Kind: fragment
- Line: 33
- Check: `bbba3e53:v2/docs/records/l4e9/l4e9_power_path.out:615` reads "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7"
- Check: `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:615` reads "ADDRESSED IN DRAFTS (P0-7, R-240, not applied): CORRECTED in draft by P0-7"
- Why: as R-05
- Class: PRESENTATION OR BINDING (as R-05)
- Old:

```text
since `7070f106` L4-E9's data reads "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7" (`v2/docs/records/l4e9/l4e9_power_path.out:615`)
```

- New:

```text
since `7070f106` L4-E9's data reads "ADDRESSED IN DRAFTS: CORRECTED in draft by P0-7" (`v2/docs/records/l4e9/l4e9_power_path.out:615`; after `6fe398e9` "ADDRESSED IN DRAFTS (P0-7, R-240, not applied): CORRECTED in draft by P0-7", `6fe398e9:v2/docs/records/l4e9/l4e9_power_path.out:615`)
```

### R-07. P0-7: R-240's name for D-10's item after set 31 (not named by draft 2)

- Kind: fragment
- Line: 115
- Check: `bbba3e53:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334` reads "the receiving company's engineering item E-1 (its later validation step is S1"
- Check: `6fe398e9:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336` reads "the receiving company's engineering item l4e7's E-1 (its later validation step is S1"
- Why: as R-05; the register's line moved by two with R-246 and set 31 named the item record l4e7's (PC-12, `v2/docs/records/l4e9/SET31-CHANGES.md:51` at `6fe398e9`)
- Class: PRESENTATION OR BINDING (as R-05)
- Old:

```text
names D-10 "the receiving company's engineering item E-1 (its later validation step is S1" (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334`)
```

- New:

```text
names D-10 "the receiving company's engineering item E-1 (its later validation step is S1" (`v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:334`; after `6fe398e9`, set 31's PC-12, "the receiving company's engineering item l4e7's E-1 (its later validation step is S1", `6fe398e9:v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md:336`)
```

### R-08. E11-29's fixture facts: the annex quotation and R17's two prints (K-12 on this list's side)

- Kind: fragment
- Line: 157
- Check: `bbba3e53:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:105` reads "Targets: Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm."
- Check: `686de0a2:v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:105` reads "Targets: Zw at most 37.59 K/W, R17 at most 0.294 K/W, the pours 0.1 mOhm (R17's 0.294 K/W is record l4e11's three-place print"
- Check: `bbba3e53:v2/docs/records/l4e11/l4e11_power.out:1922` reads "R17's coupling target: at most 0.294 K/W"
- Check: `bbba3e53:v2/docs/records/l4e11/l4e11_power.out:500` reads "R17's coupling at most 0.29 K/W"
- Why: the quotation holds at `bbba3e53`; W3's amendment of the annex for the next set (branch `fnd/w3annex` at `686de0a2`, cited as text only) continues the same line after "0.1 mOhm" with R17's note, so a quotation that closes after the full stop no longer matches there; closed before it, the quotation holds on both. The note added is the narrower reading W3 states for K-12 (one computed target, two prints; for layout the row's 0.29 K/W)
- Class: PRESENTATION OR BINDING (a quotation robust to the annex's amendment; K-12's reading carried)
- Old:

```text
the pours 0.1 mOhm." (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:103-105`)
```

- New:

```text
the pours 0.1 mOhm" (`v2/docs/records/l4close/SUPPLIER-VALIDATION-ANNEX-2026-10-05.md:103-105`); R17's 0.294 K/W is record l4e11's three-place print (`v2/docs/records/l4e11/l4e11_power.out:1922`) of the one computed target its row E11-29 prints as 0.29 K/W (`:500`)
```

### R-09. Revision 2's lines cited by path once revision 3 replaces the file (sixteen citations)

- Kind: every
- Check: `bbba3e53:v2/docs/records/l4close/P0-POWER-LIST.md:1` reads "revision 2, 5 October 2026, 16:50 CEST"
- Why: draft 2's rule "`path:N` is line N at `bbba3e53`" (its line 23) makes these citations correct as written; once the coordinator adopts the draft as `v2/docs/records/l4close/P0-POWER-LIST.md`, the same path names revision 3 itself, so the sha is written out (and any re-pointing of the other citations to the integrated revision leaves these on `bbba3e53`)
- Class: PRESENTATION OR BINDING (citations bound to their revision)
- Old:

```text
`v2/docs/records/l4close/P0-POWER-LIST.md:
```

- New:

```text
`bbba3e53:v2/docs/records/l4close/P0-POWER-LIST.md:
```


## 3. What was checked in draft 2, and what holds

Read at `35dca639` against the records at `bbba3e53` (and at `6fe398e9` or `53a68c7c` where draft 2 names them): 112 line citations,
each resolved to its file and lines; 85 quotations, each found word for word (whitespace and Markdown emphasis aside) in a cited
file at its revision, except the one of R-04; 19 decimal figures, each found on a line the same paragraph cites. The mismatches are
R-03 (a citation), R-04 (a quotation) and R-05 to R-07 (three statements the set 31 merge changed that draft 2's own rule should
have named); R-08 is a quotation that holds today and would not on the annex's next amendment; R-01 and R-02 are revision 2's figures
where draft 2 already prints the records'. Every other statement checked reads as its record prints it. Revision 2's "MODEL margin
0.369 V" is not a mismatch of its own: it is 0.3693 V rounded, the round 2 print R-01 replaces.

Not checked here: what draft 2 cites from Slot K's own result draft (`v2/docs/records/int30/RESULT.draft2.md`, sections 2, 3 and 5)
beyond the count "fourteen stale" read at its section 3; the classification of the intervening commits is that draft's and the
coordinator's.

## 4. Left out, and SESSION decisions

- **Left to the coordinator:** the adoption (K-15) and the State column's words, which this file does not touch; the line citations
  at `bbba3e53`, which draft 2's convention keeps valid (R-09 only binds revision 2's own lines).
- **SESSION decisions** (under the owner's standing rule of 26 September 2026): (1) R-01 changes no text: draft 2 already prints the
  records' 15.1308 V and names revision 2's 15.1307 V; adding the figure to the table's State cell would add a claim the cell does
  not make. Reversed by: the coordinator printing the case in the cell, with `v2/docs/records/l9t5/l9t5_f01.out:145`. (2) R-08
  carries K-12's reading (one computed target, two prints) rather than choosing one print; W3 reads the row's 0.29 K/W for layout.
  Reversed by: record l4e11 printing one figure.
