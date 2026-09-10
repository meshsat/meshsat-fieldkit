#!/usr/bin/env bash
# PCB-E1 E6 pre-route chain. The sequence is tools/full.sh and this board's differences are tools/boards/e.json
# (10 September 2026, plan stage 7: twenty one chain clones, and the drift between clones is what split the DRC policy in two).
set -uo pipefail
exec bash "$(dirname "$0")/full.sh" "$1" e
