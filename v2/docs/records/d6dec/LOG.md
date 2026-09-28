# d6dec running log (stream resumed 29 Sep 2026)

Times are CEST, read from `date` at the step.

| Time | Action | Result |
|---|---|---|
| 00:33 | Resumed author read BRIEF.md (_runs/claude/d6dec/20260929T0032) and WORKER-RULES.md | branch fnd/d6dec at 3c98a88e, 4 ahead of main, 130 behind; box/escape_parity.py modified, box/basis_check.py untracked |
| 00:36 | Checkpoint of the previous author's two files as they stand | committed (see git log) |
| 00:36 | Merged main 9147db5d into fnd/d6dec with `merge --no-ff` | no conflict; no file changed on both sides since the merge base 73ae2f21 (609 on main, 25 on the branch) |
| 00:36 | Ran tests test_decoupling_rules and test_escape_cost on this host | 30 passed, 0 failed, 0 skipped; 8 passed, 0 failed, 0 skipped |
| 00:36 | basis_check.py: quote extraction rewritten (an apostrophe in "maker's" opened a passage and swallowed the real opening quote), the page after a passage read first, TI literature numbers (SLUSC67B style) recognised, each document's text flattened once | first run 3 NOT_FOUND, 13 ELSEWHERE (all naming failures of the tool); after the fix 0 ELSEWHERE |
| 00:37 | basis_check.py on this host, `nice -n 19`, `--jobs 2`, over the six committed intents | 428 PDFs (13 no text layer), 440 declarations and loop rows, 125 bases: FOUND 262, PAGE 42, NOT_FOUND 3, NO_QUOTE 133 declarations; BASIS.md written by make_basis_md.py |
| 00:40 | Read the three NOT_FOUND passages in their PDFs with pdftotext | LTC2954 quote elides "(Pin 1/Pin 4)"; TMP117 basis writes "The" for the maker's "A"; SGP41 text layer drops the micro sign. None changes a value or a class |
| 00:42 | T5: intent.bypass takes `cls`, `basis` and the class fields; intent.write refuses an entry with no ruled class or no basis, and prints (does not refuse) class L's missing floor or ESR and class R's missing same_side | tests/test_intent_bypass_class.py 6 passed, 0 failed, 0 skipped |
| 00:41 | T7: apply_dec001_registry.py written (DEC-001's section 8.2 text into pcb_rules.yaml with the four source hashes read whole from the held files, and its coverage row naming the new tools, HEURISTIC_AS_LAW kept) | run on a scratch copy of the tools: applied, rules_lib.validate 0 errors, a second run refused |
| 00:42 | box/dec001_read.py written: each phase folder copied whole to a work directory on the box and this checkout's intent_checks.py run there, FAIL lines grouped by cause | not run yet |
| 00:44 | Box: bundle 73ae2f21..fnd/d6dec (63 MB) to /root/d6dec/bundles, old clone t1 removed, clone t3 at c1a1f28e; run_box.sh t3 run3 started (33 test files, then escape_parity, then dec001_read) | running |
| 00:46 | D3/T4 "closed again": escape_cost names the part(s) whose absence alone clears a lost pad (all of the cause's parts when none does alone) and records a `close` list; escape.py writes it to out/<stem>-escape-cost.json; bypass_search.closures() reads it and shuts that one opening while the costed part stands where it was measured (stale entries counted, not applied); bypass_place re-seats a capacitor sitting in a closed opening | test_escape_cost 11 passed, 0 failed, 0 skipped here; two board tests added to test_decoupling_board (pcbnew, box) |
| 00:47 | Box run3 test log: test_exposed_pad_vias.t_the_thermal_vias_are_asked_of_every_footprint... FAILS at c1a1f28e: a source check still looked for `if is_fine(fp)` in escape.py's coarse loop, which the previous author moved to `fan_select.is_escaped(fp)` (same selection) | test updated to accept either spelling; 9 passed, 0 failed, 0 skipped here |
