#!/usr/bin/env bash
# fr_dialog_watch.sh: the one answer to Freerouting's modal warning under Xvfb (16 September 2026).
#
# Freerouting 1.9.0 raises a warning dialog for a net it cannot normalise ("The normalization of net
# '/X' failed") and WAITS FOR A CLICK. Under Xvfb nobody clicks, so the router holds its process at a
# few percent of one core and computes nothing until its time limit kills it. Board B lost three hours
# to it on 15 September and route_one.sh got a watchdog; route_part.sh, cont_route.sh, route_pcb.sh and
# fr_probe.sh launch the same jar the same way and did not, so the fix protected one launcher of five.
# The first confined partition run of board B stalled on exactly that warning at 6 percent of one core
# and went to 1.27 cores the moment Return reached its display by hand.
#
# fr_watch <router pid> <display number> <dsn path> <label>
# Poll the router's CPU time; when it has not moved for two checks inside the first twenty minutes, send
# Return to its display with the auth cookie xvfb-run wrote. Costs one `sleep 30` loop and nothing else.
fr_watch() {
  local _RPID="$1" _XDISP="$2" _DSN="$3" _LBL="${4:-router}"
  local _CPU0=-1 _STILL=0 _T0 _J _CPU _XA
  _T0=$(date +%s)
  while kill -0 "$_RPID" 2>/dev/null; do
    sleep 30
    _J=$(pgrep -f "[j]ava .*-de $(printf '%s' "$_DSN" | sed 's/[.]/\\./g')" | head -1)
    [ -n "$_J" ] || continue
    _CPU=$(awk '{print $14+$15}' /proc/$_J/stat 2>/dev/null || echo -1)
    if [ "$_CPU" = "$_CPU0" ]; then _STILL=$((_STILL+1)); else _STILL=0; fi; _CPU0=$_CPU
    if [ "$_STILL" -ge 2 ] && [ $(( $(date +%s) - _T0 )) -lt 1200 ]; then
      if command -v xdotool >/dev/null 2>&1; then
        for _XA in $(ls -t /tmp/xvfb-run.*/Xauthority 2>/dev/null); do
          XAUTHORITY="$_XA" DISPLAY=":$_XDISP" xdotool key --clearmodifiers Return >/dev/null 2>&1 && { echo "$_LBL: no CPU progress for 60 s on display :$_XDISP; Return sent (a modal warning Freerouting holds for a click)"; break; }
        done
      else echo "$_LBL: stalled on display :$_XDISP and xdotool is not on this host to dismiss a dialog"; fi
      _STILL=0
    fi
  done
}
