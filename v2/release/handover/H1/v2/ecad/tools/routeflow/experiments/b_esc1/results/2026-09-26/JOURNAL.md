# Q-B-ESC-1 journal (EXPERIMENTAL)

Board B escape trial, v2/docs/B-FEASIBILITY.md section 7. EXPERIMENTAL: never a phase, a promotion or a layout candidate.

- start: 2026-09-26T18:48:19+00:00
- commit: 44cfa0450c74e26e7e8d48261d9f7209404ccd98; tools tree: ee1906fab4cbaad78133316d1f06176288e1d8d0
- trial scripts sha256/16: run.sh a7e32b812e5b559a; count_open.py 093839e72286f50c; judge.py 0d849b2577171e79; make_arm8.py e1482746504485a7; plateau_watch.py 0a7d15af2178078e; 
- run.sh tracked at this commit: yes
- jar: freerouting-1.9.0-mesh.jar sha256/16 82753043cb9da3ae; java: openjdk version "25.0.4.1" 2026-08-18
- kicad-cli: 9.0.9; host: d7e94791178c; cores: 64
- caps: passes 20, job timeout 9000 s, first pass 5400 s, plateau 3, budget 6 h / 10 USD at 0.142 USD/h, cap 21600 s, route deadline 2026-09-27T00:03:19+00:00
- one job per arm: the router is deterministic (tests/test_driver_hygiene.py), so a repeat is the same number twice

- input: pcb-b-compute-b19/routed/pcb-b-compute-preroute.kicad_pcb sha256 62facf0952ff4c01cb0a47698ec6870b5fae0f0d9b836bf95db6c3c7bae166dd; project file sha256 c2c6e771722d9f53
make_arm8: a8 enabled copper F.Cu In1.Cu In2.Cu In3.Cu In4.Cu In5.Cu In6.Cu B.Cu; arms agree
- ESCAPE_SKIP (tools/boards/b.json escape_env): U3,U4,J_HDMI
- integrity: groups {'S1': 158, 'S2': 157, 'DEVW': 116, 'S3': 146, 'GLOBAL': 183, 'DEVE': 84} place_audit {'collisions': 10, 'fine_pitch': 75, 'footprints': 957, 'measured': 75}
- a6 pass 0: count_open: group S3 open 290 over 146 nets (135 split by the walk), residue {'U301': 36, 'U302': 8, 'U309': 5, 'U32B': 11}, vias 184, 19.9 s
- a8 pass 0: count_open: group S3 open 290 over 146 nets (135 split by the walk), residue {'U301': 36, 'U302': 8, 'U309': 5, 'U32B': 11}, vias 184, 19.9 s
- a6: route_part pid 746586 on F.Cu In2.Cu In3.Cu B.Cu, watcher pid 746587, start 2026-09-26T18:50:31+00:00
- a8: route_part pid 746595 on F.Cu In2.Cu In3.Cu In5.Cu In6.Cu B.Cu, watcher pid 746596, start 2026-09-26T18:50:31+00:00
- operator 2026-09-26T19:47:02+00:00: both routers idle since 18:50:37 on Freerouting's modal "DSN file reader" warning (net normalization); fr_watch never fired because the idle JVM's CPU ticks still move; Return sent to each display by hand, the action fr_watch is written to take
- operator watcher 2026-09-26T21:20:45+00:00: no router left, exiting
- a6: plateau_watch: stop JOB_ENDED after 12 session(s), counts [138, 111, 84, 71, 66, 56, 42, 39, 40, 37, 38, 33]
- a8: plateau_watch: stop PLATEAU after 14 session(s), counts [106, 66, 40, 28, 29, 28, 22, 25, 21, 18, 16, 23, 18, 18]
- a6 final: count_open: group S3 open 33 over 146 nets (23 split by the walk), residue {'U301': 3, 'U302': 1, 'U309': 1, 'U32B': 2}, vias 440, 8.2 s
- a6 hard set: 0 499 (H U, board-wide U includes every group the trial did not route)
- a8 final: count_open: group S3 open 18 over 146 nets (16 split by the walk), residue {'U301': 4, 'U309': 1}, vias 398, 5.8 s
- a8 hard set: 0 499 (H U, board-wide U includes every group the trial did not route)
judge: INCONCLUSIVE: an arm is not settled: it ended or was cut by a cap while its count was still falling (a6 stop JOB_ENDED, falling True; a8 stop PLATEAU, falling False)
- end: 2026-09-26T21:21:46+00:00; wall 9207 s
- fetch, file by file, then destroy the box and read the instance list: JOURNAL.md integrity.json arm8.json outcome.json and, per arm, base.json final.json s3-counts.txt s3-drc.json place_audit.txt route.log watch.log watch/passes.csv watch/watch.json run/S3/fr.log
