#!/usr/bin/env bash
# PCB-P P1 and later pre-route chain. The sequence is tools/full.sh and this board's differences are tools/boards/p.json
# (10 September 2026, plan stage 7: twenty one chain clones, and the drift between clones is what split the DRC policy in two).
set -uo pipefail
exec bash "$(dirname "$0")/full.sh" "$1" p
