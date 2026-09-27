#!/bin/bash
# r8int6: assemble the integration kit of one stream: its drafts as the stream left them plus the integrator's scripts.
# Usage: kitprep_r8int6.sh <stream>
set -e
SP=$SP
s=$1; K=$SP/r8int6/kit/$s
rm -rf "$K"; cp -a "$SP/wt/$s/drafts/$s" "$K"; find "$K" -name __pycache__ -type d -prune -exec rm -rf {} +
cp "$SP/r8int6/mine/$s/"* "$K/"
echo "kit $s: $(find "$K" -type f | wc -l) files"
