# Engineer takeover from Layer 4 (handover of 10 October 2026)

The receiving engineer takes responsibility for **Layer 4 (system architecture) onward**, on the Layer 1 to 3 baseline in
this folder with its amendments (`03_Requirements/APPROVED-AMENDMENTS.md`). Everything below about Layer 4 is **working
input, not an accepted architecture**. No V2 board has been built; no software test here qualifies hardware or
authorises fabrication.

## 1. Suggested next steps

1. Read the baseline and the amendments, and hold your own review of them (all earlier reviews were AI reviews, I-11).
2. Bring the records up to date:
   - enter amendment A-1 (two identical packs) in the requirements registry (I-02);
   - write the authorised re-issue texts into `PRODUCT-BRIEF.md` and `CONOPS.md` (I-01);
   - correct the stale status row (I-03).
3. Settle the energy architecture against the requirements:
   - the power path (I-05);
   - runtime against service, REQ-072 (I-04 and the owner question in `04_Review_and_Open_Issues.md` section 3);
   - the two-pack fit and protection (I-08);
   - the battery-bay sensing (I-06);
   - thermal closure with its physical test (I-07).
4. Partitioning, interfaces and the board rounds follow only once the architecture holds. Board B must place with zero hard violations before any layout (I-09).
5. The external evidence still owed:
   - the cell bench test E-01 (U-01);
   - the thermal test T-H1;
   - fabricator quotations (EQ-14);
   - makers' answers drafted under `v2/docs/records/l4e12/clarification/` (unsent).

## 2. Layer 4 material already available

### 2a. On `main` (`c20c4b629ff4f4d06f82ef3fe98d59d313bab497`, integration set 33)
- The Layer 4 records under `v2/docs/records/` (the l4e* power, thermal and energy records among them) and the Layer 4 section of `v2/docs/handover/LAYER-STATUS.md`, which is supplied in `03_Requirements/`.
- Status at this handover: Layer 4's desk gate **NOT PASSED**; power closure **BLOCKED**; fabrication release **BLOCKED**.

### 2b. Integration set 34, prepared but NOT promoted
- Candidate `a6274bf77f2c6d3ffa898e34f7bfa47aede3bda4` (branch `fnd/int34`), frozen on 9 October 2026. It carries 9 October's Layer 4 records and the filed owner instructions.
- Independent read W304: "fit for the candidate, conditionally" (an AI read).
- Freeze passes all fetched with 0 failures: suite pass A 3131 passed, 2 skipped; pass B 26; records 379; runner 245 with 1 skipped.
- The suite gate, promotion and adoption were **not run**: the owner suspended Layer 4 integration on 10 October.
- This handover commit moves `main` past the candidate's base, so promoting set 34 now needs a merge or a re-cut, not a fast-forward.

### 2c. Reviewed but unintegrated working branches
Each branch was cut from `main` or from set 34's candidate. SWC means "supported with conditions" from an independent AI check.

| Branch | Full SHA | Content | Last independent verdict and later changes |
|---|---|---|---|
| fnd/l4rt72 | `667c297e1e13e7757be388b0eb2725f4635942b1` | REQ-072 runtime record (routes), with two-pack coverage (on fnd/l4rt `3964c68aea73df57a80f521decb736f937a1cfc4`) | l4rt SWC (W270); two-pack coverage SWC (W362), its conditions closed and verified |
| fnd/l4e11r20 | `b5691f790a1509cbd653e6899802e1475dc291b9` | board A RAIL_EN divider correction draft (R-270) | SWC (W267) |
| fnd/l4tpu01 | `30eaec24656008754e30fda475af4ac24375b66a` | TP-U01-CELL, the one-cell screen of U-01 | SWC (W274); later closures unverified |
| fnd/l4sa868 | `c0659fa592405b36be9cda63712472014f7fe1e6` | the SA868 inhibit decision (board D) | decision reviewed; acceptance needs bench E-01 |
| fnd/l4sdr | `e0800837a361300350a4dd40eabff1edadf21fb9` | SDR limiter elements on board B | SWC (W280); later closures unverified |
| fnd/l4trade | `518811f5d32cc210bbe3f4625a47b7cbb002b209` | U8 and F2 trade decisions | SWC (W282); later closures unverified |
| fnd/l4qy | `5053475bb00461ea2e1a6d77d090d800f74b95aa` | QMX tray placement source fix | SWC (W291) |
| fnd/l4cu | `668fdc95559ffda94fde44b41b737a74ff78feab` | outer copper weights of boards A and E (a session selection, conditional) | SWC (W309); later tally unverified; board A rework and USB at 2 oz open |
| fnd/l4pk2 | `bb89472c20838f17917761a3128abb1d4ee2ba16` | the second pack's screen (location, protection, combining) | SWC (W319); later guard unverified; fit unproven |
| fnd/l4case | `602511faf0148b2171d329bbb24d8797e35e6e50` | case rows to makers' drawings; the CM5 cooler correction draft (R-272) | SWC (W327; R-272 W351); later test unverified |
| fnd/l4pack | `53efb735da75bb0fcdc376a8db4b5153a6586f99` | the pack drawing as the ruled 4S3P block | SWC (W334); STEP/STL export owed |
| fnd/l4rowd | `0571ede2bc6a4fa3106e3100c782dda3d985b8a7` | energy row (d), method M-E | supported as conditional; later integration fixes unverified |
| fnd/l4cfl | `1eaf9d550fd10cbb5a9abf65af00cb92abc27002` | thermal record l4e12 (on fnd/l4therm `f74cacf7546f457d5b78287a9951291dad338c7a`) with CFL-002's sensing route | l4therm SWC (W326/W342); CFL-002 NOT (W363), then SWC on recheck (W366), its conditions closed and verified |
| fnd/l4checkb + fnd/l4emc | `6c9943a3db31d170213bf98a7bc94fc78a9a2897` + `9c10afcb3ee21897307bf07fa22775df6ebb94d7` | board B gate restated and the three EMCON circuit corrections (R-276), to be applied together | the pair SWC (W376), two nonblocking conditions open |
| fnd/l4bank | `dfe3151924f85652cb969c825ed87cebf01ad9ae` | BANK-R1 hub-port exchange draft (fills change-list row R-107) | SWC (W367), its blocking condition closed and verified |
| fnd/l8gndfix | `3b38638bf63a98760199bcf50411811e7a215223` | GND-002 (R-191) and the SLOT_EN hold (R-192), corrected | targeted recheck SWC with no blocking condition (W375); one tested test-bar fix uncommitted; release file not written |
| fnd/l4d16r | `fe8e63aaa06baa6d856492cb363f7f6c80e8134f` | D-16 read against U5's absolute maximum (L4A-75) | SWC (W371), its conditions closed and verified |

### 2d. In progress, not accepted
| Branch | Full SHA | State |
|---|---|---|
| fnd/l4seat | `dbc7b038e3cbb3386bb3d2355ba9f058da5f9d14` | board B seating rules (R-274). The round 2 box run seated 412 of 412, but the placed board had 6 copper-to-hole-edge violations and 178 decoupling-distance failures. Round 3's code is uncommitted and untested. No independent check |
| fnd/l4besc | `b7542a31385858b287d0f9f636c482d23efffc32` | board B escape experiment kit (L4A-28); the preparation never reached a placed board, so no stack is decided |
| fnd/l4hot | `e71f7b6b0f7e7e4ba71da1c56c70833cde849fbf` | establishes that HOT-R1 is already drawn in boards A and E and that the SLOT_EN hold is R-192's draft; verified by script, no independent check |

**Access.** These branches are not published. They are held in the programme's runner repository and in one local git bundle, `meshsat-fieldkit-layer4-working-20261010.bundle`:
- size 6,243,039 bytes; sha256 `1d87188907744cea226dc6fa0b5c2c259f0332c0d3d84016522b52d4f61abbc9`;
- 25 branch heads, prerequisite `c20c4b62`.

The bundle is shared only if the owner chooses. With it: `git fetch <bundle> 'refs/heads/fnd/*:refs/remotes/handover/*'`.

## 3. Known feasibility problems by requirement
`04_Review_and_Open_Issues.md` section 2, I-04 to I-09:
- the runtime REQ-072;
- the power path and outlet;
- the battery-bay sensing REQ-042;
- thermal closure;
- the cells and the two-pack fit;
- board B's EMCON lines and placement.

Each is stated there as missing information or an established failure.
