# What moved between set 9 and set 10 on the EMCON paths (stream d4emcon, 29 September 2026)

Read on the committed netlists of main `7b2caadd` (merged into `fnd/d4emcon` as `da31586e`) against those of set 9
(`89815e4f`, which carried main `c5f93464`). Tools: `tools/netdiff.py` (parts by value, nets by node), then
`tools/path_walk.py`, `tools/walk_report.py` (RF-002's walk), `tools/fault_levels.py` and `tools/lamp_check.py`, all
pure Python on the committed files; nothing here needed KiCad.

| Board | set 9 sha256/16 | set 10 sha256/16 | What changed | Effect on an EMCON path |
|---|---|---|---|---|
| A | `599ee964a9c23d6e` | `30ad87746d1801ca` | the `source` and two `date` header lines only (set 10's regeneration after stream d6dec's decoupling tools entered every generator's import closure); `netdiff.py` prints no part and no net difference | none |
| B | `21a1f74a3ec1ae28` | `97823ef1171a61ce` | as A | none |
| C | `3fddbb3edcd4248a` | `fef4df255c00f4db` | as A | none |
| D | `7a2c0ac2190b141a` | `a2d48972d171aad1` | as A | none |
| E | `56adc9746d61c4e0` | `2ed95a0e8069ebf8` | as A | none |
| P | `760ac6f74d62d194` | `20c7b0795593d761` | as A | none |

Result of the re-run: `paths-set10.txt` (27 declared paths, every hop holds), `walk/walk-full.txt` (RF-002's walk:
A FAIL 0 PASS 3 UNDECIDED 2; B FAIL 0 PASS 9 UNDECIDED 8; C FAIL 0 PASS 3; D FAIL 0 PASS 3 UNDECIDED 1; E and P PASS 1),
`fault/fault-levels-set10.txt` and `lamp-check-set10.txt` (L-1 to L-4 PASS) are byte-identical to the set 9 readings
under `../set9/` apart from the netlist hashes in their headers. So every statement this stream's set 6 and set 9
readings support stands on set 10.
