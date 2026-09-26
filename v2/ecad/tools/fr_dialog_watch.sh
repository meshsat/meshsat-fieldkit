#!/usr/bin/env bash
# fr_dialog_watch.sh: the one answer to Freerouting's modal warning under Xvfb (16 September 2026).
#
# Freerouting 1.9.0 raises a warning dialog for a net it cannot normalise ("The normalization of net
# '/X' failed") and WAITS FOR A CLICK. Under Xvfb nobody clicks, so the router holds its process at a
# few percent of one core and computes nothing until its time limit kills it. Board B lost three hours
# to it on 15 September and route_one.sh got a watchdog; route_part.sh, cont_route.sh, route_pcb.sh and
# fr_probe.sh launch the same jar the same way and did not, so the fix protected one launcher of five.
#
# TWO THINGS THE FIRST WATCHDOG GOT WRONG, both measured on board B's partition run this morning:
#
#   * IT WATCHED THE WRONG PROCESS. `pgrep -f "java .*-de <dsn>"` matches the `timeout` and `xvfb-run`
#     wrappers as well as the JVM, and they start first, so they sort first and `head -1` returns a pid
#     whose CPU time never moves. The comparison then reads "stalled" on every poll, so the old watchdog
#     sent Return every sixty seconds whatever the router was doing. It dismissed dialogs by firing
#     blindly rather than by detecting anything, which is why it looked like it worked.
#   * IT STOPPED AFTER TWENTY MINUTES. Freerouting raises one dialog PER failing net, as the router
#     reaches it; board B has seven. A run stalls again at pass nine as readily as at pass one.
#
# So: select the JVM by name and confirm the DSN in its own command line, take its display and auth
# cookie from its own environment rather than guessing the newest file in /tmp, and never stop watching.
# A router that is working never satisfies the trigger, because its CPU time moves.
#
# A THIRD THING, 26 September 2026 (MESHSAT-1357, board B's escape trial Q-B-ESC-1): THE CPU TRIGGER NEVER
# FIRES ON A JVM WAITING ON A MODAL. An idle JVM's garbage collector and AWT threads still tick, so its CPU
# time moves by a few ticks every poll and "no progress for 40 s" is never true. Both arms of the trial sat
# 57 minutes on the "DSN file reader" warning at 0.7 percent of one core, with this watcher running and
# silent, until Return was sent by hand; B23's "S3 could not complete one pass in four hours" may have been
# the same stall. The modal is now found by what it IS, a window titled "DSN file reader" (or Warning,
# Message, Error) on the JVM's own display, and dismissed on the poll that sees it; the CPU trigger stays
# as the fallback for a dialog with another title.
#
# fr_watch <pid of the backgrounded launcher> <display number> <dsn path> <label>
fr_watch() {
  local _RPID="$1" _XDISP="$2" _DSN="$3" _LBL="${4:-router}"
  local _CPU0=-1 _STILL=0 _J _CPU _D _X _P _W _N
  while kill -0 "$_RPID" 2>/dev/null; do
    sleep 20
    _J=""
    for _P in $(pgrep -x java 2>/dev/null); do
      tr '\0' ' ' < /proc/$_P/cmdline 2>/dev/null | grep -qF -- "$_DSN" && { _J=$_P; break; }
    done
    [ -n "$_J" ] || continue
    _D=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^DISPLAY=' | cut -d= -f2)
    _X=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^XAUTHORITY=' | cut -d= -f2)
    [ -n "$_D" ] || _D=":$_XDISP"
    if command -v xdotool >/dev/null 2>&1; then
      for _W in $(XAUTHORITY="$_X" DISPLAY="$_D" xdotool search --name "DSN file reader|Warning|Message|Error" 2>/dev/null); do
        _N=$(XAUTHORITY="$_X" DISPLAY="$_D" xdotool getwindowname "$_W" 2>/dev/null)
        case "$_N" in ""|"Board Layout - Freerouting") continue;; esac
        XAUTHORITY="$_X" DISPLAY="$_D" xdotool windowactivate --sync "$_W" key --clearmodifiers Return >/dev/null 2>&1 \
          && echo "$_LBL: modal '$_N' on $_D dismissed (found by its title)"
      done
    fi
    _CPU=$(awk '{print $14+$15}' /proc/$_J/stat 2>/dev/null || echo -1)
    if [ "$_CPU" = "$_CPU0" ]; then _STILL=$((_STILL+1)); else _STILL=0; fi; _CPU0=$_CPU
    if [ "$_STILL" -ge 2 ]; then
      _D=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^DISPLAY=' | cut -d= -f2)
      _X=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^XAUTHORITY=' | cut -d= -f2)
      [ -n "$_D" ] || _D=":$_XDISP"
      if command -v xdotool >/dev/null 2>&1; then
        XAUTHORITY="$_X" DISPLAY="$_D" xdotool key --clearmodifiers Return >/dev/null 2>&1 \
          && echo "$_LBL: no CPU progress for 40 s on $_D; Return sent (a modal warning Freerouting holds for a click)"
      else echo "$_LBL: stalled on $_D and xdotool is not on this host to dismiss a dialog"; fi
      _STILL=0
    fi
  done
}
