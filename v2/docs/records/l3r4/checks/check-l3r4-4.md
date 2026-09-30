mergeable: yes

# CHECK-4 of layer 3 round 4 (`fnd/l3r4` at `a547fe1d`): the delta check of round 4d

An AI check by a session that wrote none of the round, not a qualified review. Written 30 September 2026, 12:52 CEST.
Scope: `git diff e8e3ef57..a547fe1d` only (four files: `reissue.py`, `PASSAGE-MAP.md`, `README.md`, `test_l3r4.py`),
checked against CHECK-3's four minors. Everything below was run in a `--no-local --single-branch` clone of `fnd/l3r4`
with the set 17 evidence archive (`int17-evidence-de11cc4e.tar`) installed, or read from it. Nothing was committed or
pushed; the clone is removed.

## Verdict

The four minors of CHECK-3 are answered. There is no blocking item. Two small residuals remain; neither changes what
the proposed texts say, because the head note's general sentences already govern the lines they concern.

## 1. PACK completeness

- **The map** has 128 passages, counted from its headings: 51 DEFINITION, 19 HF, 37 PACK, 1 SOLAR and 20 CELL. The
  new PACK passages are 310, 349, 468, 890 and 914.
- **The test now searches `VOCAB_RX` itself.** `uncovered()` returns nothing for PACK or for CELL.
- **The four new exemptions hold.** Each is a behaviour or condition that the head note reads per pack, as its reason
  says:
  - 205: the gauge holding the charge on the cells' measured temperature;
  - 289: the pack gauge holding charging off below 0 C;
  - 819: the voltage line standing in for the gauge's state of charge until the learning cycle;
  - 1014: the pack replaced when the gauge's learned capacity falls below the aged line.
- **My own removals.** I took out each of the 37 PACK and 20 CELL passages in turn. Every removal is caught: 56 by the
  pattern and one (PACK) by the designator fallback. I also took out each of the 13 exemptions in turn, and every one
  is caught. The test's pinning of the passage list against the headings of `PASSAGE-MAP.md` holds, and
  `--map --check` reads current.
- **Lines that still escape.** I searched with the pattern's blind spots and with wider wordings (minor 1).

## 2. CELL ageing

- CONOPS 1015 ("60 % after 500 cycles (7.9)") and 1103 ("80 % of the cell's specification minimum capacity") are now
  CELL passages; the group has 20.
- `VOCAB_RX["CELL"]` adds `\b\d+ % after \d+ cycles\b` and `\bthe cell's specification minimum\b`.
- The test requires "60 % after 500 cycles" and "the cell's specification minimum" in the CELL vocabulary.
- Residual: minor 2.

## 3. B06

- **Under `reading-c`** (recommended answers): "... packs to be built for the kit rather than bought, of the Samsung
  INR18650-35E cells: a base 4S6P ...". The test asserts it.
- **Under `cells`** (the tests' third set): "... of cells of the Samsung INR18650-35E as held, the cell of D-06 that
  owner ruling D-31 on row L3-OD5 reopens (CFL-017 kept open): a base 4S6P ...". It reads correctly, if a little
  heavily.

## 4. Link tests and the guard

**No test can write into a baselined file of the tree.** I read every write in `test_l3r4.py`:
- temporary registry copies and fixtures;
- the approval fixtures, including one append to the draft in a temporary out-dir;
- the incoherent registry copy;
- the copy of LAYER-STATUS.md;
- the symlink and hard link. Both now point at `_docs_copy()`, a temporary copy of the two baselined files, which the
  generator reads through `--docs-root`.

The generator itself opens only `MAP` and its two fixed output names for writing; the test asserts that from the
source. The only `--map` call in the suite is `--map --check`. Running the full suite left `CONOPS.md` and
`PRODUCT-BRIEF.md` at `6cb7b241cb84d729` and `85513b92ed0daf55`, and the clone clean.

**The guard in normal use** (no `--docs-root`) still refuses the tree's own files:
- `guard_out` on the tree's `CONOPS.md` and `PRODUCT-BRIEF.md` refuses both as "a baselined file".
- A draft name symlinked to the tree's brief is refused as "is a link", exit 2.
- A record name hard linked to the tree's brief (inside the clone) is refused as "the same file as a baselined file (a
  hard link)", exit 2.

**With `--docs-root`**, the guard compares against the copy, not the tree. The tree's files stay protected all the
same:
- A hard link to the tree's brief is refused as "has more than one link".
- A symlink is refused as a link.
- The output names are fixed.
- A copy whose `CONOPS.md` differs by one byte is refused as not the baselined text.

## 5. Reruns

On registry copies built by the prepared scripts, all three counts reproduce:

| Answer set | Restated | CURRENT | CURRENT by group |
|---|---|---|---|
| Recommended | 50 | 57 | 19 HF, 37 PACK, 1 SOLAR |
| The other set | 45 | 39 | 1 HF, 37 PACK, 1 SOLAR |
| The tablet with `cells` | 41 | 57 | 37 PACK, 20 CELL |

No generated file carries an en or em dash.

## 6. Gates

- `rules_lib.py requirements`: 144 records, 0 errors, 0 warnings.
- `rules_render.py --requirements --check`: current.
- `render_l3r2.py --check`: 0 out of date.
- `reissue.py --map --check`: current.
- `dryrun.py`: byte identical.
- Tests: 106 passed, 0 failed, 0 skipped.
- The 190 added lines carry no en or em dash, no internal host name and no absolute path.
- `CONOPS.md`, `PRODUCT-BRIEF.md`, the registry and `v2/release/` (H3) are unchanged.
- The author is the owner's identity, with no trailer.
- The README's integrator run order ran on a branch from main `8fec0733` with no failure (106 tests) and left a tree
  identical to `fnd/l3r4`.

## Minors

1. **Two blind spots in the PACK pattern.** The pattern needs "the charger" or "the gauge" on one line, followed by a
   space and a word. It misses:
   - **Line 885**, the fault row for a stuck kit I2C bus: "the secure element, the charger, the supervisors' status and
     board A's expanders are unreachable". Here "the charger" is followed by a comma. This is the one generated charger
     on the kit bus, the same statement 881 and 882 make, and both of those are PACK.
   - **Lines 233 and 234**: "its pack in the / gauge's shutdown", split by the line break. This is a Transport
     procedure that reads per pack, and it would be exempt.

   Wordings the pattern does not cover at all name the same chain in other words, all harmless under the head note:
   - "OTD" alone, the gauge's discharge cut at 57.5 C (580 to 582, 731, 732, in the paragraph whose 571 to 578 are
     PACK);
   - "the pack's XT60" (322) and "the pack's arming jumper", which is JP1 in words (323), both procedures;
   - "the pack's FETs" (647).

   The remedy is small: let the pattern accept punctuation after the noun, match across line breaks, and list or
   exempt 885, 233 and 234.
2. **CELL misses one ageing figure.** CONOPS 342 ("the sheet's own stated minimum after 500 cycles (7.9), kept as the
   lower bracket") is the same figure as 1015. The new pattern needs "N % after", so it does not match. The line sits
   in section 4a, whose runtime figures C23 already marks as D-06's pack's.
