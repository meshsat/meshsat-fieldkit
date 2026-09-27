# Carried citations re-read by hand (layer-3 closer, 27 September 2026)

The apply script re-anchors every file:line citation of the registry from the commit `sources_read_at` names (eadbe571) to the commit it runs at. A citation whose lines were rewritten where they stood is carried by line alignment, which gives only a position; each was read by hand, old text beside new (`--citation-report`), in two trees: this worktree (e3aedb25, with the closer's own in-place edits of the pack and facts files) and the integration simulation (main 53a98a71 with fnd/hc1 and fnd/hc2 merged, their patches applied, and this script's swaps). For every range below the carried lines hold the subject the record relies on (the S-07 and closer corrections rewrote those lines in place); records of kind conflict or superseded keep their old line with "(as read at eadbe571)", because they cite what a source said. Two carried positions were WRONG on the merged tree and are found by their opening text instead (`CITE_ANCHORS` in `ops_int.py`): REQ-043 (the envelope's list of documents not held, lines 103 to 108 there) and REQ-058 (the LimeSDR row the layer-2 closer added to section 2, line 80); REQ-050's TEST-PLAN title lines, which alignment cannot place, are anchored too. `reviewed-citations.json` lists each re-read citation with the sha256/16 of the file it was read on: the script accepts one without `--accept-rewritten` only on a byte-identical file, and refuses every other one for a person to read.

## This worktree (eadbe571 to e3aedb25)

| Cited at eadbe571 | Carried to | File sha256/16 | Records | Verdict |
|---|---|---|---|---|
| `v2/ecad/tools/pcb_decisions.yaml:863-915` | 891-952 | `1367edbf54a842d3` | D-15, CFL-016 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:52-92` | 52-92 | `1367edbf54a842d3` | decision-28 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:37-51` | 37-51 | `df8ac22603440bc5` | REQ-001, REQ-002, CHO-001 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:46-46` | 46-46 | `e7a90ba054150bb7` | REQ-001, REQ-002, REQ-003, REQ-030, REQ-031, REQ-035, REQ-036, CFL-016 | same subject, rewritten in place |
| `v2/docs/ARCH-PCB-B-IOHA.md:87-89` | 87-91 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/ARCH-PCB-B-IOHA.md:178-189` | 184-202 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:73-73` | 73-73 | `df8ac22603440bc5` | REQ-020, REQ-059, ASM-006 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:256-396` | 256-424 | `1367edbf54a842d3` | CON-018 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_board_facts.yaml:281-282` | 281-282 | `07af4d0f2b166694` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:15-19` | 15-19 | `bc78efbf633223b5` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_rules_coverage.yaml:636-644` | 637-645 | `9d6a40d0caa50a24` | REQ-030 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:33-34` | 33-34 | `df8ac22603440bc5` | REQ-035 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:34-34` | 34-34 | `df8ac22603440bc5` | REQ-036, REQ-037, REQ-038 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:48-77` | 48-84 | `e7a90ba054150bb7` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-40` | 17-40 | `2a16c1eb2205bcb5` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:13-22` | 13-22 | `39feae15de45d37e` | REQ-045 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-27` | 17-27 | `2a16c1eb2205bcb5` | CFL-006 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:46-46` | 46-46 | `39feae15de45d37e` | CFL-006 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:76-76` | 76-76 | `df8ac22603440bc5` | CFL-016, SPD-006 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:41-41` | 41-41 | `df8ac22603440bc5` | SPD-006, CFL-010 | same subject, rewritten in place |
| `v2/docs/ASSEMBLY.md:148-148` | 159-159 | `e4a0b78616c69779` | REQ-066 | the dock-interface paragraph (the E5 block REQ-066 caps), corrected by S-07 |

## The integration simulation, first build (eadbe571 to main 53a98a71 with the pass-1 files of fnd/hc1 and fnd/hc2)

| Cited at eadbe571 | Carried to | File sha256/16 | Records | Verdict |
|---|---|---|---|---|
| `v2/docs/TEST-PLAN.md:18-19` | 26-27 | `f42130c896295963` | D-02a, CFL-007, REQ-051, CFL-017 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:16-17` | 24-25 | `f42130c896295963` | D-02c, REQ-022 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:863-915` | 896-957 | `b5f7162443d5ad91` | D-15, CFL-016 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:52-92` | 52-92 | `b5f7162443d5ad91` | decision-28 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:20-20` | 28-28 | `f42130c896295963` | SC-03, REQ-026, CFL-008 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:37-51` | 37-51 | `dcca1c31a31cced0` | REQ-001, REQ-002, CHO-001 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:46-46` | 54-56 | `f42130c896295963` | REQ-001, REQ-002, REQ-003, REQ-030, REQ-031, REQ-035, REQ-036, CFL-016 | same subject, rewritten in place |
| `v2/docs/ARCH-PCB-B-IOHA.md:87-89` | 87-91 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/ARCH-PCB-B-IOHA.md:178-189` | 184-202 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:42-42` | 42-42 | `dcca1c31a31cced0` | CHO-002 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:31-31` | 39-39 | `f42130c896295963` | REQ-015 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:23-23` | 23-23 | `dcca1c31a31cced0` | SPD-003, CFL-012 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:64-66` | 74-76 | `f42130c896295963` | REQ-018 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:73-73` | 73-73 | `dcca1c31a31cced0` | REQ-020, REQ-059, ASM-006 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:21-22` | 29-30 | `f42130c896295963` | REQ-021 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:128-139` | 188-209 | `807e429a203a7ead` | REQ-024 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:27-34` | 27-35 | `53d682b96e281b9a` | REQ-024 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:141-142` | 211-218 | `807e429a203a7ead` | REQ-025 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:90-95` | 115-117 | `807e429a203a7ead` | ASM-004 | the same paragraph (appendix 32.53, the no-vent ruling), restated as bounds; ASM-004 is superseded in substance by the table after it |
| `v2/ecad/tools/pcb_envelope.yaml:36-41` | 37-72 | `53d682b96e281b9a` | ASM-004 | inside_air_rise_k, marked superseded, with the per-state bounds that replace it (the range widened by alignment over the new block) |
| `v2/docs/TEST-PLAN.md:24-24` | 32-32 | `f42130c896295963` | REQ-027 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:197-201` | 277-287 | `807e429a203a7ead` | REQ-028 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:36-36` | 44-44 | `f42130c896295963` | REQ-029 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_board_facts.yaml:281-282` | 281-282 | `07af4d0f2b166694` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:15-19` | 15-19 | `53d682b96e281b9a` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_rules_coverage.yaml:636-644` | 652-660 | `882e91982b10ead8` | REQ-030 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:33-34` | 33-34 | `dcca1c31a31cced0` | REQ-035 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:34-34` | 34-34 | `dcca1c31a31cced0` | REQ-036, REQ-037, REQ-038 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:37-37` | 45-45 | `f42130c896295963` | REQ-039, REQ-057, REQ-068 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:48-77` | 58-94 | `f42130c896295963` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-40` | 17-40 | `2a16c1eb2205bcb5` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:13-22` | 13-22 | `39feae15de45d37e` | REQ-045 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:69-70` | 79-80 | `f42130c896295963` | REQ-046 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-27` | 17-27 | `2a16c1eb2205bcb5` | CFL-006 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:46-46` | 46-46 | `39feae15de45d37e` | CFL-006 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:13-13` | 13-13 | `dcca1c31a31cced0` | REQ-047 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:76-76` | 76-76 | `dcca1c31a31cced0` | CFL-016, SPD-006 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:23-23` | 31-31 | `f42130c896295963` | CFL-008, REQ-064 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:8-8` | 16-16 | `f42130c896295963` | CFL-009 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:171-171` | 247-248 | `807e429a203a7ead` | CFL-009 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:171-172` | 247-249 | `807e429a203a7ead` | REQ-052, CFL-011 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:41-41` | 41-41 | `dcca1c31a31cced0` | SPD-006, CFL-010 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:51-51` | 51-51 | `dcca1c31a31cced0` | REQ-058 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:34-34` | 34-35 | `53d682b96e281b9a` | CFL-011 | same subject, rewritten in place |
| `v2/docs/PANEL.md:168-168` | 189-193 | `b90d8e54fac16722` | REQ-060 | the SOS indications paragraph the layer-2 closer inserted before the sounder line, with the sounder line: REQ-060 is SOS |
| `v2/docs/ASSEMBLY.md:148-148` | 159-159 | `e4a0b78616c69779` | REQ-066 | the dock-interface paragraph (the E5 block REQ-066 caps), corrected by S-07 |

## The integration simulation, final build (eadbe571 to main 53a98a71 with fnd/hc2 pass 2, fnd/hc2 ASSEMBLY patch, and the NEED-03 patch on fnd/hc1)

| Cited at eadbe571 | Carried to | File sha256/16 | Records | Verdict |
|---|---|---|---|---|
| `v2/docs/TEST-PLAN.md:18-19` | 26-27 | `17187f6718d1c476` | D-02a, CFL-007, REQ-051, CFL-017 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:16-17` | 24-25 | `17187f6718d1c476` | D-02c, REQ-022 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:863-915` | 896-957 | `b5f7162443d5ad91` | D-15, CFL-016 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_decisions.yaml:52-92` | 52-92 | `b5f7162443d5ad91` | decision-28 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:20-20` | 28-28 | `17187f6718d1c476` | SC-03, REQ-026, CFL-008 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:37-51` | 37-51 | `891d0eb40c32d0d9` | REQ-001, REQ-002, CHO-001 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:46-46` | 54-56 | `17187f6718d1c476` | REQ-001, REQ-002, REQ-003, REQ-030, REQ-031, REQ-035, REQ-036, CFL-016 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:29-29` | 29-29 | `891d0eb40c32d0d9` | REQ-006 | the same NEED-03 row, with the shared-elements note of correction 27 |
| `v2/docs/ARCH-PCB-B-IOHA.md:87-89` | 87-91 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/ARCH-PCB-B-IOHA.md:178-189` | 184-202 | `6c3c93b7f32f953a` | CON-003 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:42-42` | 42-42 | `891d0eb40c32d0d9` | CHO-002 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:31-31` | 39-39 | `17187f6718d1c476` | REQ-015 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:23-23` | 23-23 | `891d0eb40c32d0d9` | SPD-003, CFL-012 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:64-66` | 74-76 | `17187f6718d1c476` | REQ-018 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:73-73` | 73-73 | `891d0eb40c32d0d9` | REQ-020, REQ-059, ASM-006 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:21-22` | 29-30 | `17187f6718d1c476` | REQ-021 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:128-139` | 201-231 | `6930e4f05a59ac5c` | REQ-024 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:27-34` | 27-35 | `6333e5d212f57a78` | REQ-024 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:141-142` | 233-240 | `6930e4f05a59ac5c` | REQ-025 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:90-95` | 120-122 | `6930e4f05a59ac5c` | ASM-004 | the same paragraph (appendix 32.53, the no-vent ruling), restated as bounds; ASM-004 is superseded in substance by the table after it |
| `v2/ecad/tools/pcb_envelope.yaml:36-41` | 37-89 | `6333e5d212f57a78` | ASM-004 | inside_air_rise_k, marked superseded, with the per-state bounds that replace it (the range widened by alignment over the new block) |
| `v2/docs/TEST-PLAN.md:24-24` | 32-32 | `17187f6718d1c476` | REQ-027 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:197-201` | 299-309 | `6930e4f05a59ac5c` | REQ-028 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:36-36` | 44-44 | `17187f6718d1c476` | REQ-029 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_board_facts.yaml:281-282` | 281-282 | `07af4d0f2b166694` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:15-19` | 15-19 | `6333e5d212f57a78` | CFL-003 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_rules_coverage.yaml:636-644` | 652-660 | `04cac5f6670f1cd8` | REQ-030 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:33-34` | 33-34 | `891d0eb40c32d0d9` | REQ-035 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:34-34` | 34-34 | `891d0eb40c32d0d9` | REQ-036, REQ-037, REQ-038 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:37-37` | 45-45 | `17187f6718d1c476` | REQ-039, REQ-057, REQ-068 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:48-77` | 58-94 | `17187f6718d1c476` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-40` | 17-40 | `2a16c1eb2205bcb5` | REQ-044 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:13-22` | 13-22 | `39feae15de45d37e` | REQ-045 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:69-70` | 79-80 | `17187f6718d1c476` | REQ-046 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_pack_protection.yaml:17-27` | 17-27 | `2a16c1eb2205bcb5` | CFL-006 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_energy_chain.yaml:46-46` | 46-46 | `39feae15de45d37e` | CFL-006 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:13-13` | 13-13 | `891d0eb40c32d0d9` | REQ-047 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:76-76` | 76-76 | `891d0eb40c32d0d9` | CFL-016, SPD-006 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:23-23` | 31-31 | `17187f6718d1c476` | CFL-008, REQ-064 | same subject, rewritten in place |
| `v2/docs/TEST-PLAN.md:8-8` | 16-16 | `17187f6718d1c476` | CFL-009 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:171-171` | 269-270 | `6930e4f05a59ac5c` | CFL-009 | same subject, rewritten in place |
| `v2/docs/OPERATING-ENVELOPE.md:171-172` | 269-271 | `6930e4f05a59ac5c` | REQ-052, CFL-011 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:41-41` | 41-41 | `891d0eb40c32d0d9` | SPD-006, CFL-010 | same subject, rewritten in place |
| `v2/docs/V2-SPEC.md:51-51` | 51-51 | `891d0eb40c32d0d9` | REQ-058 | same subject, rewritten in place |
| `v2/ecad/tools/pcb_envelope.yaml:34-34` | 34-35 | `6333e5d212f57a78` | CFL-011 | same subject, rewritten in place |
| `v2/docs/PANEL.md:168-168` | 189-193 | `beeb6e399801007f` | REQ-060 | the SOS indications paragraph the layer-2 closer inserted before the sounder line, with the sounder line: REQ-060 is SOS |
| `v2/docs/ASSEMBLY.md:148-148` | 159-159 | `da8ceafde1bf34d2` | REQ-066 | the dock-interface paragraph (the E5 block REQ-066 caps), corrected by S-07 |


## Re-read by the targeted fixer c23 (27 September 2026, pass 3)

fnd/hc2's `OPERATING-ENVELOPE.md` and `pcb_envelope.yaml` changed at pass 3 (the hot stop past the heat stage, Review A
pass 2 P2-B2), so the five citations below, carried by line alignment into those two files, were refused by the apply
script on the simulation of main `a8652172` (sim commit `da704b11`) and read again by hand there, old lines against new
(the script's `--citation-report`). Each still names what its record rests on; the pair hashes are added to
`reviewed-pairs.json`.

| Citation at eadbe571 | Lines now | File sha256/16 | Record | Reading |
|---|---|---|---|---|
| `v2/docs/OPERATING-ENVELOPE.md:128-139` | 205-242 | `354bc222868bbfa9` | REQ-024 | section 4's in-use ambient and its carve-outs, the hot-end bullet now with the hot stop appended; same subject |
| `v2/docs/OPERATING-ENVELOPE.md:171-172` | 280-282 | `354bc222868bbfa9` | REQ-052, CFL-011 | the operating modes sentence, now naming the hot stop past the heat stage; same subject |
| `v2/ecad/tools/pcb_envelope.yaml:36-41` | 37-94 | `4b890dd5ea8ec858` | ASM-004 | inside_air_rise_k marked superseded, with the per-state bounds and the hot end (now with hot_stop) that replace it, the range widened by alignment; same subject |
| `v2/ecad/tools/pcb_envelope.yaml:15-19` | 15-19 | `4b890dd5ea8ec858` | CFL-003 | the header and the document pin, re-pinned to the pass-3 record; same subject |
