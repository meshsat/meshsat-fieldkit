#!/usr/bin/env bash
# PCB-B B16 and later (B19 through full_b19.sh) pre-route chain. The sequence is tools/full.sh and this board's differences are tools/boards/b.json
# (10 September 2026, plan stage 7: twenty one chain clones, and the drift between clones is what split the DRC policy in two).
set -uo pipefail
exec bash "$(dirname "$0")/full.sh" "$1" b
