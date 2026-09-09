#!/usr/bin/env bash
# PCB-B B19 (MESHSAT-862): the B16 chain with the phase this board actually is. B19 is the first B phase carrying the I/O
# high-availability layer of ARCH-PCB-B-IOHA (the per-bank host-selection fabric, the three supervisors, the voters, the
# duplicated WiFi card and its antenna changeover). Nothing else differs: the chain, its gates and their order are B16's.
# Usage: full_b19.sh <project dir>
set -uo pipefail
export PHASE=B19
exec bash "$(dirname "$0")/full_b16.sh" "$@"
