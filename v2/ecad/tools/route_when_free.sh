#!/usr/bin/env bash
# Usage: route_when_free.sh <dir> <name> : serialise router runs (one Freerouting at a time: the watchdog kills every java router it sees)
cd "$1"; N="$2"
exec 9>/tmp/meshsat-freerouting.lock
flock 9
while pgrep -f '^java .*freerouting' >/dev/null || pgrep -f 'tools/full_route\.sh' >/dev/null || pgrep -f 'tools/full_a3\.sh' >/dev/null; do sleep 20; done
../tools/full_route.sh . "$N"
