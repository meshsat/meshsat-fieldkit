#!/usr/bin/env bash
# The one answer, on the shell side, to WHICH FREEROUTING JAR A RUN TAKES (12 September 2026, MESHSAT-862).
#
# `routeflow.py:jar_in_use()` is the same answer on the python side, and it exists because every place that
# RECORDED a jar carried its own default string and named the stock jar while the patched one ran. The shell
# side had the mirror of that defect: route_one.sh chose properly and the other four launchers did not.
# cont_route.sh, route_part.sh and long_route.sh each pinned the STOCK jar by name, and route_pcb.sh took
# `ls ~/bin/freerouting-*.jar | tail -1`, which is 2.4.1 on a host that has it, launched with 1.9.0 arguments
# under whatever `java` is first on PATH.
#
# It matters most exactly where it was wrong. Our build writes a Specctra session after every pass; the stock
# jar writes one only when the whole job ends. Every one of those launchers runs under a `timeout`, so on the
# stock jar a run that reaches its cap leaves NOTHING. cont_route.sh is declared as 80 passes in 900 seconds:
# on C10's board 60 passes took four hours, so that pass count cannot finish inside that cap on any board this
# set has, and on the stock jar the continuation could therefore never keep anything at all. The threshold that
# gates it was raised the same day for a different reason; this is the other half of why it never fired.
#
# Usage:  . "$(dirname "$0")/fr_jar.sh";  JAR="$(fr_jar route_one)" || exit 2
fr_jar () {
  local who="${1:-route}"
  if [ -n "${FR_JAR:-}" ]; then printf '%s\n' "$FR_JAR"; return 0; fi          # a deliberate pin always wins
  if [ -s "$HOME/bin/freerouting-1.9.0-mesh.jar" ]; then printf '%s\n' "$HOME/bin/freerouting-1.9.0-mesh.jar"; return 0; fi
  # THE FALLBACK IS NOT SILENT (round-two H5, 11 September 2026): `onstart.sh` never built our jar, so every
  # fresh box routed on stock while the pipeline behaved as though it had not, and that is hours of box time
  # per run with no artefact to show for it.
  if [ "${FR_REQUIRE_MESH:-1}" != 0 ]; then
    echo "$who: no $HOME/bin/freerouting-1.9.0-mesh.jar on this host." >&2
    echo "$who: that jar writes a session after every pass; the stock one writes one only at the end, so a" >&2
    echo "$who: cut run leaves nothing and the pass ceilings exist to work around it. Build it (see" >&2
    echo "$who: tools/freerouting/README.md) or set FR_REQUIRE_MESH=0 to route on stock deliberately." >&2
    return 2
  fi
  echo "$who: WARNING routing on the STOCK jar by FR_REQUIRE_MESH=0: no session until the job ends" >&2
  printf '%s\n' "$HOME/bin/freerouting-1.9.0.jar"
}
