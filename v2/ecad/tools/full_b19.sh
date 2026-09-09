#!/usr/bin/env bash
# PCB-B B19 (MESHSAT-862): the B16 chain with the phase this board actually is. B19 is the first B phase carrying the I/O
# high-availability layer of ARCH-PCB-B-IOHA (the per-bank host-selection fabric, the three supervisors, the voters, the
# duplicated WiFi card and its antenna changeover). Nothing else differs: the chain, its gates and their order are B16's.
# Usage: full_b19.sh <project dir>
set -uo pipefail
export PHASE=B19
# 300 s per pair (pair_preroute's PAIR_BUDGET). Measured on the B19 board: the long pairs take about 2.5 minutes each, so
# this bounds the tail without biting the normal case, and 113 pairs cannot turn into an open-ended night again.
export PAIR_BUDGET=${PAIR_BUDGET:-300}
exec bash "$(dirname "$0")/full_b16.sh" "$@"
