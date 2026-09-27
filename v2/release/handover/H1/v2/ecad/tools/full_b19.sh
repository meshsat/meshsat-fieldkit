#!/usr/bin/env bash
# PCB-B B19 (MESHSAT-862): the B16 chain with the phase this board actually is. B19 is the first B phase carrying the I/O
# high-availability layer of ARCH-PCB-B-IOHA (the per-bank host-selection fabric, the three supervisors, the voters, the
# duplicated WiFi card and its antenna changeover). Nothing else differs: the chain, its gates and their order are B16's.
# Usage: full_b19.sh <project dir>
set -uo pipefail
export PHASE=B19
# No wall-clock budget per pair (10 September 2026, report 1's configuration finding and appendix 32.90). A clock decided the
# result here once: two runs of the same board with the same placement laid 38 and 33 of 113, and the only difference was how
# loaded the box was. The bound is PAIR_EXPANSIONS, which is counted in work and gives the same answer whatever else runs.
export PAIR_BUDGET=${PAIR_BUDGET:-0}
exec bash "$(dirname "$0")/full_b16.sh" "$@"
