# Fresh check of stream d6rel at efd6899a (AI review), 28 September 2026 17:37 CEST

**This is an AI review, never a qualified engineering review.** Prototype design: no board built, ordered or measured. The worktree was only read (no file under it modified after my start at 17:18; tracked status clean). The apply script was not executed.

```
mergeable: yes
```

One thing to decide before merging: your item 3 says a class with no maker figure must never read PASS. At class level that holds. At board level it does not (m1). No board reads PASS today, so I rate it minor; if you meant the board reading, treat m1 as blocking.

## blocking

None. H3-01's three conditions are met and I reproduced each myself.

## minor

| id | item | note |
|---|---|---|
| m1 | 3, 10 | **A `none_published` class does not hold a board from PASS; only `owed` and `measure_owed` do** (`reliability.py:135-149`, `:345-347`). Counter-example P1: one JST connector, one `none_published` class, pinned netlist reads `PASS`, exit 0. The test `t_a_class_with_no_cycle_figure_must_say_why` (`test_reliability.py:138`) asserts that PASS, so it is deliberate. `records/d6rel/README.md:25` says the opposite ("UNDECIDED (INCONCLUSIVE) where the maker states none") and marks it done. 16 of 57 classes are `none_published`. Board D is held only by REL-O-10 and board P only by REL-O-11; P would then PASS with 0 cited figures. Either make `none_published` hold the board, or correct README row 1 and say so in the coverage note. |
| m2 | 10 | REL-O-07 and REL-O-08 are named by no class, so they hold no board. Counter-example P15: a list with an unreferenced open item and one cited class reads `PASS`. The apply script's fixed sentences say boards read INCONCLUSIVE on "REL-O-01 to REL-O-11" (`apply_rel001_coverage.py:254-255`, `:308`). |
| m3 | 2 | **Undisclosed population limit.** The declared-phase board files carry `H*` footprints that are in no netlist: A `H1`-`H8`, D and P `H1`-`H4`, B and E past `H20`. The inventory reads netlists for those boards and cannot see them, while C and E5 class the same kind of joint. Those board files also carry a few R, Q and C references absent from the netlists, so they are another generation. Worth an open item. |
| m4 | 2 | Board B's ten bench headers are excluded partly because "whether a header is fitted at all is a build choice not made". The same uncertainty is `owed` under REL-O-02 for the same kind of land. `J_SPI3`'s value does not say "bench". Visible reason and SESSION authority are recorded; safer as owed. |
| m5 | 1, 6 | Residual of the original defect. Counter-example P14: an `RJ45 MagJack` drawn as `U99` on `Package_SO:SOIC-8` reads `PASS`. The word net has no "jack", "RJ45" or "plug", though `wear_inventory.py:24-26` says it names a jack. Needs both reference and land wrong. |
| m6 | 10 | The list cites "the part identities table of stream w5ident" four times. That table (`v2/docs/parts/IDENTITIES.md`) is not on this branch or on the integration tip `1c4235ec`; it exists only in the unmerged w5ident worktree (`c08f4d5a`). The rows I read there (496, 505, 512, 518, 540, 574) say what the list claims. Nothing resting on it yields a figure or a PASS. |
| m7 | 3 | No citation carries a `revision`, which your item 3 and the worker rules ask for. The author discloses this as an open item; sha256 binds the bytes. |
| m8 | 10 | `rules_status.py:729-731` still declares the old tool's inputs for `reliability.py`: it names `pcb_board_facts.yaml`, which the repaired tool no longer reads, and its comment says the readings "do not bind anyway". The stream left no note or apply script for it. |
| m9 | 7 | Apply script details. (a) It changes REL-001's remediation from `owner: OWNER, execution: OWNER, p50_h 0, p80_h 0` to `SESSION, SEQUENTIAL, 4, 10` (disclosed in README section 8). (b) close-s89 accepts a `PASS` verdict (`:187`) while its closing text says "never PASS". (c) The evidence rows read `inputs["netlist"]` only (`:237`), so a set-level re-take would print sha `None`. (d) A `--floor` with no offset is read as UTC. (e) A reading INCONCLUSIVE only because the vendor folder was absent has `missing_input` None and would be accepted. |
| m10 | 3 | Two citations need care to re-verify: the Molex figure sits in the page's JSON-LD block, not visible text; the HRO drawing has no text layer and must be rendered. |

## verified

1. **Matrix.** Read the four cases in the review (section H3-01) and `matrix.py` (writes only to a temp directory and `VERDICT_DIR`). Ran it with `TMPDIR` in scratch: repaired tool `4 of 4`, exit 0 (PASS, FAIL, FAIL, INCONCLUSIVE); tool of `73ae2f21` `2 of 4`, exit 1, failing exactly cases 3 and 4. Not softened: my variants P11, P12, P13, P13b (undeclared class `CN1`, `U99` on a connector land, no land, undeclared land) all FAIL. Case 4 uses board A's declaration, which owes two figures, so I separated it: P3 (no netlist, nothing owed) reads INCONCLUSIVE with `missing_input` set.
2. **Inventory.** With my own S-expression reader: 2,647 parts, 175 references beginning with the eight prefixes, all in the tool's inventory, 0 refused. Tool totals 427 / 185 / 242 / 0 as claimed. Reproduced the 61 (my 69 less 6 `JP*` and 2 `PAD_W*`; A 18, B 18, C 12, E 11, P 2), every one disposed with a visible reason. Checked 14 exclusion groups against values and lands: 219 test points all `TestPoint_Pad_D1.5mm`, six solder jumpers, B's 1812 polyfuses, P's SCF9550, B's SWD pads; B's bench headers are the soft one (m4). A wider word net over the non-candidates found 87 hits; the de-duplicated sample I read was all soldered parts.
3. **Figures.** Opened all 30 cited documents. Every one of the 23 figures is at the cited page. Ranges carry the lowest and say so (Mill-Max 100,000 of 100,000 to 1,000,000; NKK 25,000). Variant-dependent figures match the fitted part: `ATP16-...-M0SA` decodes as momentary (200,000, not 100,000 lock); APEM 5636 is single pole (50,000); TE's 60 cycles covers both part numbers. The JST and Keystone documents carry no cycle figure in their text.
4. **Missing input.** INCONCLUSIVE, exit 3, for no netlist, zero bytes, no components, cut short, and a directory at the path (P3 to P6b). Re-export reads INCONCLUSIVE with the same `content16`; a changed value reads INCONCLUSIVE "design changed"; no pin reads INCONCLUSIVE. On a scratch copy of the real artefacts: B's netlist removed and C's changed both read INCONCLUSIVE with the reason. No `mtime` or `glob` in either tool (old tool: `max(..., key=os.path.getmtime)`); P10 reads `pcb-a-power-a23` over two newer decoys. All seven pins match this tree and the integration tip.
5. **Tests.** `tests: 56 passed, 0 failed, 0 skipped`. They cover the four cases, the no-wear-word connector, empty and unreadable netlists, sha mismatch in three forms, absent pin, declared phase. None trivially satisfied; the no-figure test pins PASS for `none_published` (m1).
6. **Parsing.** Netlist and board file are read as S-expressions, the list by `yaml.safe_load`. `re` over value text survives only as the second net (`reliability.py:72`, `wear_inventory.py:228-239`): it can add a candidate, never remove one.
7. **Apply script** (read, plus a static regex check on the integration tip's files). Floor: refuses unless after every unrepaired reading, reads every reliability verdict in the same folders `rules_status` uses, fails safe on a bad timestamp; timestamps are UTC with `Z`. The REL-001 block delimits to one rule key. close-s89 refuses without a floor, on any board reading before the floor, with another list sha, another artefact sha, a missing input, a refusal, or no inventory counts. Its regex finds exactly REQ-022, 024, 026, 028, 064. Both stages assert old text, require new text to differ, re-parse, refuse a second run.
8. **Vendor documents.** Seven added files, each with a `sources.txt` line carrying URL, fetch time and full sha256; 12 of 12 added lines match the bytes on disk.
9. **Prose.** 0 em dashes, 0 en dashes in added text; prototype framing and "AI review" present; no service-life claim; verdict note says it tests nothing.
10. **Misleading.** No board reads PASS while it owes anything. No class merges parts of different ratings. No file overlap with the integration line; no shared file touched; seven commits as the owner, no trailer.

## not_done

- **Full suite**: not run (box only). The author ran only the `reliability` subset, so nobody has run it on this branch.
- **Apply script**: not executed; I did not reproduce `apply-script-test.txt`.
- **REL-O-03**: the two Amphenol M.2 documents behind "25 to 60 mating cycles" were not opened.
- **Series-level figures**: FH34, RJHSE and U.FL sheets confirmed at the page, not against each order code's row.
- **`rules_status` on a merged tree**: only the in-memory consumers probe was run (it reproduces the committed record).

Scratch, with probes and outputs: `<worktrees>/_scratch/chk-d6rel/`. To reproduce P1 to P14:

`env -C <worktrees>/_scratch/chk-d6rel PYTHONDONTWRITEBYTECODE=1 python3 probe.py probes <worktrees>/d6rel/v2/ecad/tools`

P15 is `probe2.py` with the same arguments; it prints P15 and then stops on a traceback in my own summary table, which is a bug in my script and not a finding.

---
Filing note (scrub, 30 September 2026, MESHSAT-1357): 3 paths in this check are written as neutral tokens (`<worktrees>`) under the owner's rule that public files carry no internal host names, user paths or addresses; `v2/docs/records/scrub/MAP.md` lists each by line and token class. No other byte of the check changed; the check as filed is in the repository's history at commit `8fec0733` and before.
