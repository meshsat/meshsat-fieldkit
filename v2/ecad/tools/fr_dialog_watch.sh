#!/usr/bin/env bash
# fr_dialog_watch.sh: what every Freerouting launcher runs beside its router (fr_watch) and before it (fr_import_probe).
# Sourced by route_one.sh, route_part.sh, cont_route.sh, route_pcb.sh and fr_probe.sh, after fr_jar.sh.
#
# HISTORY, SHORT. 15 September 2026: board B's router sat three hours on a Freerouting warning dialog under Xvfb and
# route_one.sh got a CPU-stall watchdog that pressed Return. 16 September: that watchdog watched the `timeout` wrapper
# instead of the JVM (so it pressed Return every minute whatever happened) and gave up after twenty minutes; it became
# this shared file, selecting the JVM by name and by the DSN in its own command line. 26 September: both arms of board
# B's escape trial sat 57 minutes on the "DSN file reader" dialog with the CPU trigger silent, because an idle JVM's
# garbage collector still ticks; the window was then looked for by its title.
#
# ROUND 8 OF MESHSAT-1357 (review finding F, 26 September 2026: "automatically pressing Return on a DSN file reader
# warning should require understanding that warning"), and what was MEASURED on the KiCad box the same night on board
# B's committed pre-route board, S3 confined, in /root/r8-fr:
#
#   * The dialog is `import_design`'s (freerouting v1.9.0 interactive/BoardHandling.java:836-878): every WARNING or
#     ERROR FRLogger collects while the DSN is read raises it, it lists them, and log4j writes each of them to the
#     router's log first. On board B it listed exactly the seven lines the log holds, "The normalization of net
#     '/ETH2_P2_N' failed." and six more, and nothing else (screenshot taken at the dialog). fr_import_check.py
#     carries the source reading, the one warning that is understood (FR-NORMALISE-NET) and why its consequence is
#     bounded; everything else refuses.
#   * THE TITLE PATH OF 26 SEPTEMBER NEVER DISMISSED ANYTHING. `xdotool windowactivate` needs a window manager's
#     _NET_ACTIVE_WINDOW and Xvfb has none, so it fails, and xdotool abandons the chained `key Return`. `windowfocus` on
#     the dialog's frame moves X focus off Java's focus proxy and the key is then swallowed; Escape the same. Return
#     reaches the dialog only through its own FocusProxy child window, which held focus until something moved it.
#     So a dismissal here puts focus back on that proxy if it moved, presses Return, and CHECKS that the window is
#     gone; if it is not, it clicks the dialog's OK button, and if that fails too the job is stopped as unanswerable.
#   * Freerouting's own non-modal frames appear on every run ("Board Layout - Freerouting", "General Settings", which
#     BoardFrame.initialize_windows shows), as do Java's internal windows ("Content window", "FocusProxy"). They are
#     ignored by name. ANY OTHER TITLED WINDOW is a modal nobody has read ("Exception Occurred", a "Select an Option"
#     confirmation that Return would answer YES to, a rules-file prompt): the router is stopped and the window is
#     recorded with a screenshot. Nothing here presses Return on a window it has not identified.
#   * The CPU-flat trigger is gone. It could only ever press Return blindly, and it did not fire when it was needed.
#     Stage progress replaces it: the load stage has its own limit (FRW_LOAD_MAX_S, default 1800 s; board B's
#     confined S3 DSN imports in about 4 s after a 1 s JVM start), the whole import window of the log is classified
#     when routing starts (a warning that raised no dialog is still a warning), and once more after the router ended
#     when no poll saw routing start (a job that imports, routes and ends between two polls), the first per-pass session is checked
#     by `fr_import_check.py survive`, and FRW_PASS_MAX_S (default 0, off) can bound the time between passes.
#   * fr_import_probe, run by every launcher before its route: the jar imports a copy of the DSN whose settings turn the
#     autorouter and the optimiser off and writes back the board it holds; `fr_import_check.py import` compares that
#     with the DSN (layers, nets with their pins, classes with width, clearance, layers and vias, keep-outs, planes,
#     every wire and via with its fixed state). On board B: 844 nets with 3,959 pins, 25 classes, 178 keep-outs,
#     4,011 wires and 2,218 vias all came back, including the copper of the seven nets whose normalisation failed.
#   * Stage timing goes into the run log ("fr_stage ...": JVM start, input load, time blocked on a dialog, active
#     routing, optimiser) and into <log>.watch.json with every event.
#
# fr_watch <pid of the backgrounded launcher> <display number> <dsn path> <label> <router log>
#   returns 0, or 3 when it stopped the router over the import (refused) or, the router having ended before any poll
#   saw its routing start, the import it left in the log is refused, or 4 when a stage limit stopped it.
# fr_import_probe <dsn> <work dir> <label> [extra jar arguments, e.g. -dr rules]
#   returns 0 when the router holds what the DSN declares, 3 when it does not or the import was refused, 2 when it
#   could not be measured. FR_IMPORT_PROBE=0 skips it and says so in the log.

_FRW_TOOLS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_FRW_CHECK="$_FRW_TOOLS/fr_import_check.py"
# Freerouting's own non-modal frames (titles from its resource bundles, gui/*_en.properties) and Java's internal
# windows. None of them can block a thread; the modal dialogs are JOptionPanes and none of their titles is here.
_FRW_BENIGN='^(Board Layout - Freerouting|General Settings|Routing Settings|Auto-router Settings|Control Settings|Display Miscellaneous|Object Visibility|Clearance Matrix|Via Rules|Via Rule|Edit Vias|Net Classes|Assign Net Class|Nets|Selected Items|Clearance Violations|Length Violations|Manual Rules|Detail Route Parameter|Snapshots|Snapshot Settings|Content window|FocusProxy|java|app-freerouting-gui-MainApplication|sun-awt-X11-.*)$'
_FRW_DSN_DIALOG='DSN file reader - Freerouting'

_frw_x() { XAUTHORITY="$_X" DISPLAY="$_D" xdotool "$@" 2>/dev/null; }
_frw_ev() { python3 "$_FRW_CHECK" event "$_EV" "$@" >/dev/null 2>&1 || true; }
_frw_visible() { _frw_x search --onlyvisible --name '' | grep -qx "$1"; }

_frw_shot() {   # <file stem>: a screenshot of the router's display, where xwd exists
  command -v xwd >/dev/null 2>&1 || return 0
  XAUTHORITY="$_X" DISPLAY="$_D" xwd -root -silent > "$1.xwd" 2>/dev/null && echo "$1.xwd"
}

_frw_stop() {   # <code> <reason> <event> [window title]: stop the router this watcher guards, and say why
  local _C="$1" _R="$2" _E="$3" _T="${4:-}" _S
  _S=$(_frw_shot "$_LOG.stopped")
  _frw_ev "event=$_E" "title=$_T" "reason=$_R" "decision=$([ "$_C" = 3 ] && echo REFUSED || echo STOPPED)" "screenshot=$_S"
  echo "$([ "$_C" = 3 ] && echo IMPORT-REFUSED || echo STAGE-STOPPED) $_LBL: $_R${_T:+ (window '$_T')}; the router is stopped${_S:+, screenshot $_S}"
  if [ -n "$_J" ]; then
    kill -TERM "$_J" 2>/dev/null; sleep "${FRW_STOP_GRACE:-3}"; kill -0 "$_J" 2>/dev/null && kill -KILL "$_J" 2>/dev/null
  else kill -TERM "$_RPID" 2>/dev/null; fi   # no JVM found (a load that never started): the launcher itself
  _RC="$_C"
}

_frw_dismiss() {   # <dialog window id>: 0 when it is gone
  local _W="$1" _i _F _P _q WIDTH HEIGHT X Y SCREEN WINDOW
  for _i in 1 2 3; do
    # the dialog's own focus proxy: the first FocusProxy the JVM created after the dialog (one client's X ids rise)
    _P=$(for _q in $(_frw_x search --name '^FocusProxy$'); do [ "$_q" -gt "$_W" ] && echo "$_q"; done | sort -n | head -1)
    _F=$(_frw_x getwindowfocus)
    [ -n "$_P" ] && [ "$_F" != "$_P" ] && _frw_x windowfocus --sync "$_P"
    _KEYT=$(date +%s.%N)
    _frw_x key --clearmodifiers Return
    sleep 2
    _frw_visible "$_W" || { _HOW="Return on its focus proxy"; return 0; }
  done
  eval "$(_frw_x getwindowgeometry --shell "$_W")"
  if [ -n "${WIDTH:-}" ]; then   # JOptionPane's one button, bottom centre
    _KEYT=$(date +%s.%N)
    _frw_x mousemove --window "$_W" $((WIDTH / 2)) $((HEIGHT - 25)) click 1
    sleep 2
    _frw_visible "$_W" || { _HOW="a click on its OK button"; return 0; }
  fi
  return 1
}

fr_watch() {
  local _RPID="$1" _XDISP="$2" _DSN="$3" _LBL="${4:-router}" _LOG="${5:-}"
  local _EV _RC=0 _J="" _D _X _W _N _STAGE=load _T0 _SURV=0 _INC="" _WARNED="" _SEEN="" _HOW _OUT _SES _LASTP=0 _NP=0 _NP0=0
  local _OPT_T0="" _OPT_CAP=0 _AUTO _DT0 _DC _BENIGN_SEEN="" _P _rc _SL _s _KEYT=""
  _T0=$(date +%s)
  if [ -z "$_LOG" ]; then
    echo "$_LBL: fr_watch was given no router log, so no dialog can be read and none will be dismissed"; _LOG=/dev/null
  fi
  _EV="$_LOG.watch.jsonl"; [ "$_LOG" = /dev/null ] && _EV=/dev/null
  [ "$_EV" = /dev/null ] || rm -f "$_EV" "$_LOG.watch.json"
  _frw_ev event=start "label=$_LBL" "dsn=$_DSN" "log=$_LOG" "display=$_XDISP"
  command -v xdotool >/dev/null 2>&1 || echo "$_LBL: xdotool is not on this host: a dialog will be detected by the load-stage limit only, and never answered"
  while kill -0 "$_RPID" 2>/dev/null; do
    # one second at a time, so a router that has ended is noticed at once (the probe's 30 s wall on board B was
    # mostly this sleep); the poll itself is every FRW_POLL s while loading, FRW_POLL_ROUTE s while routing
    if [ "$_STAGE" = load ]; then _SL=${FRW_POLL:-5}; else _SL=${FRW_POLL_ROUTE:-20}; fi
    for _s in $(seq 1 "${_SL%.*}"); do kill -0 "$_RPID" 2>/dev/null || break; sleep 1; done
    case "$_SL" in *.*) sleep "0.${_SL#*.}";; esac
    [ "$_RC" = 0 ] || continue
    if [ -z "$_J" ] || ! kill -0 "$_J" 2>/dev/null; then
      _J=""
      for _P in $(pgrep -x java 2>/dev/null); do
        # the JVM's own -de argument, exactly: a substring test would take the import probe's JVM, whose copy of the
        # DSN keeps the DSN's file name (import-probe-in/<name>), for a router given that bare file name
        [ "$(tr '\0' '\n' < /proc/$_P/cmdline 2>/dev/null | grep -A1 -x -- '-de' | sed -n 2p)" = "$_DSN" ] || continue
        # a relative DSN path is the same string in every clone that runs the same driver (two trials in two trees
        # both route out/routeflow/.../job.dsn): the JVM must also be working in THIS directory
        case "$_DSN" in /*) ;; *) [ "$(readlink /proc/$_P/cwd 2>/dev/null)" = "$(pwd -P)" ] || continue;; esac
        _J=$_P; break
      done
      [ -n "$_J" ] || continue
      _D=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^DISPLAY=' | cut -d= -f2)
      _X=$(tr '\0' '\n' < /proc/$_J/environ 2>/dev/null | grep '^XAUTHORITY=' | cut -d= -f2)
      [ -n "$_D" ] || _D=":$_XDISP"
      _INC=$(tr '\0' '\n' < /proc/$_J/cmdline 2>/dev/null | grep -A1 -x -- '-inc' | tail -n +2 | head -1)
      _frw_ev event=jvm "pid=$_J" "display=$_D"
    fi
    # 1. every window on the router's own display, by its title
    if command -v xdotool >/dev/null 2>&1; then
      for _W in $(_frw_x search --onlyvisible --name ''); do
        [ "$_RC" = 0 ] || break                     # the router is already stopped: one refusal, one record
        _N=$(_frw_x getwindowname "$_W")
        case "$_N" in ""|" "*) continue;; esac
        if [[ "$_N" =~ $_FRW_BENIGN ]]; then
          case " $_BENIGN_SEEN " in *" $_W "*) ;; *) _BENIGN_SEEN="$_BENIGN_SEEN $_W"; _frw_ev event=window-benign "title=$_N";; esac
          continue
        fi
        if [ "$_N" = "$_FRW_DSN_DIALOG" ]; then
          case " $_SEEN " in *" $_W "*) ;; *) _SEEN="$_SEEN $_W"; _DT0=$(date +%s.%N);; esac
          _DC="$_LOG.dialog-$_W.json"
          _OUT=$(python3 "$_FRW_CHECK" classify "$_LOG" "$_DSN" --title "$_N" --stage dialog --json "$_DC" 2>&1); _rc=$?
          echo "$_LBL: $_OUT"
          if [ "$_rc" = 0 ]; then
            _WARNED=$(python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1])).get('warned_nets', [])))" "$_DC" 2>/dev/null)
            _HOW=""
            if _frw_dismiss "$_W"; then
              _frw_ev event=dialog-dismissed "title=$_N" "record=$_DC" "how=$_HOW" "answered_wall=$_KEYT" \
                "blocked_s=$(python3 -c "import sys,time; print(round(time.time()-float(sys.argv[1]),1))" "$_DT0")" decision=CONTINUE
              echo "$_LBL: dialog '$_N' dismissed ($_HOW) after its content was read: every entry is a known, bounded warning (record $_DC)"
            else
              _frw_stop 3 "the dialog's warnings are known but the dialog could not be dismissed (Return on its focus proxy and a click on OK both failed)" dialog-stuck "$_N"
            fi
          else
            _frw_stop 3 "the DSN reader's dialog says something that is not understood (record $_DC)" dialog-refused "$_N"
          fi
          continue
        fi
        _frw_stop 3 "a window nobody has read is open on the router's display" window-refused "$_N"
      done
    fi
    [ "$_RC" = 0 ] || continue
    [ -r "$_LOG" ] || continue
    [ "${FRW_STAGES:-1}" = 0 ] && continue   # a jar whose log is not 1.9.0's (route_one.sh, FR_IMPORT_PROBE=0 on a 2.x build)
    # 2. the stages, from the router's own log
    if [ "$_STAGE" = load ]; then
      if grep -q "Starting auto-routing" "$_LOG" 2>/dev/null; then
        _OUT=$(python3 "$_FRW_CHECK" classify "$_LOG" "$_DSN" --stage import --json "$_LOG.import.json" 2>&1); _rc=$?
        if [ "$_rc" != 0 ]; then echo "$_LBL: $_OUT"; _frw_stop 3 "the import logged something that is not understood (record $_LOG.import.json)" import-refused; continue; fi
        _STAGE=route; _LASTP=$(date +%s)
        _frw_ev event=routing-started "load_s=$(( $(date +%s) - _T0 ))"
      elif [ "${FRW_LOAD_MAX_S:-1800}" != 0 ] && [ $(( $(date +%s) - _T0 )) -ge "${FRW_LOAD_MAX_S:-1800}" ]; then
        _frw_stop 4 "the import did not finish in ${FRW_LOAD_MAX_S:-1800} s and no window explains why" load-stalled
        continue
      fi
    fi
    if [ "$_STAGE" = route ]; then
      _NP=$(grep -c "MeshSat: session written after pass" "$_LOG" 2>/dev/null); _NP=${_NP:-0}
      [ "$_NP" != "$_NP0" ] && { _NP0=$_NP; _LASTP=$(date +%s); }
      if [ "$_SURV" = 0 ] && [ "$_NP" -gt 0 ] 2>/dev/null; then
        _SES=$(grep -m1 "MeshSat: session written after pass" "$_LOG" | sed 's/.* to //')
        if [ -s "$_SES" ]; then
          _OUT=$(python3 "$_FRW_CHECK" survive "$_DSN" "$_SES" ${_INC:+--ignore-classes "$_INC"} ${_WARNED:+--warned-nets "$_WARNED"} --json "$_LOG.survive.json" 2>&1); _rc=$?
          echo "$_LBL: first session: $_OUT"; _SURV=1
          _frw_ev event=first-session-checked "result=$_rc" "record=$_LOG.survive.json"
          [ "$_rc" = 3 ] && { _frw_stop 3 "the router's first session lost something the DSN declares (record $_LOG.survive.json)" session-lost; continue; }
        fi
      fi
      if [ "${FRW_PASS_MAX_S:-0}" != 0 ] && ! grep -q "Auto-routing was completed" "$_LOG" 2>/dev/null \
         && [ $(( $(date +%s) - _LASTP )) -ge "${FRW_PASS_MAX_S:-0}" ]; then
        _frw_stop 4 "no pass finished in ${FRW_PASS_MAX_S} s" pass-stalled; continue
      fi
      # THE OPTIMISER BOUND (route_one.sh, 16 September 2026, moved here with the watchdog it lived in): our build
      # writes the session after every autoroute pass, so the optimiser only improves length and vias, and only if
      # the whole job ends before the time limit. It gets the autoroute's own duration, with a five-minute floor,
      # then the JVM is stopped by the pid this watcher holds and the last pass's session is kept.
      # FR_OPT_MAX_S sets the bound directly; FR_OPT_MAX_S=0 removes it. Only launchers that set FRW_OPT_BOUND=1.
      if [ "${FRW_OPT_BOUND:-0}" = 1 ]; then
        if [ -z "$_OPT_T0" ] && grep -q "Auto-routing was completed" "$_LOG" 2>/dev/null; then
          _OPT_T0=$(date +%s); _AUTO=$(( _OPT_T0 - _T0 ))
          _OPT_CAP=${FR_OPT_MAX_S-$_AUTO}; [ "$_OPT_CAP" -lt 300 ] && [ "$_OPT_CAP" != 0 ] && _OPT_CAP=300
          echo "$_LBL: the autoroute finished in ${_AUTO}s and the optimiser has started; it is bounded to ${_OPT_CAP}s (0 = unbounded)"
        fi
        if [ -n "$_OPT_T0" ] && [ "$_OPT_CAP" != 0 ] && [ -s "${FRW_SES:-/nonexistent}" ] \
           && [ $(( $(date +%s) - _OPT_T0 )) -ge "$_OPT_CAP" ]; then
          echo "$_LBL: stopping the optimiser after ${_OPT_CAP}s; the session the last autoroute pass wrote is kept"
          _frw_ev event=optimiser-bounded "cap_s=$_OPT_CAP"
          kill -TERM "$_J" 2>/dev/null || true
          break
        fi
      fi
    fi
  done
  # THE LAST READING (round 8, pass 2, from the independent check of the same night). The loop above reads the import
  # on a poll, so a router that logs its import, starts routing and ends between two polls left the loop with the
  # import unread and this function returned 0: every import probe without a dialog (it ends about 1 s after its
  # import, so a -dr rules-file warning in it was never read) and every short route (board E5's took 4.1 s, and its
  # directory held no fr.log.import.json). Whatever the loop did not classify is classified here, once, from the log
  # the router left: an unknown warning, an error, a frame the jar could not build, or an import that never reached its
  # end refuses (3) exactly as it would have inside the loop. A log with no "Opening" line had no import to read.
  if [ "$_RC" = 0 ] && [ "$_STAGE" = load ] && [ "${FRW_STAGES:-1}" != 0 ] && [ -r "$_LOG" ] && [ "$_LOG" != /dev/null ]; then
    if grep -Eq "\] INFO +Opening '" "$_LOG" 2>/dev/null; then
      _rc=0
      # a JVM still alive here (its launcher ended first) may still be importing: only a router that has ended is
      # held to an import that reached its end
      if [ -n "$_J" ] && kill -0 "$_J" 2>/dev/null; then
        _OUT=$(python3 "$_FRW_CHECK" classify "$_LOG" "$_DSN" --stage import --json "$_LOG.import.json" 2>&1) || _rc=$?
      else
        _OUT=$(python3 "$_FRW_CHECK" classify "$_LOG" "$_DSN" --stage import --exited --json "$_LOG.import.json" 2>&1) || _rc=$?
      fi
      echo "$_LBL: read after the router ended: $_OUT"
      if [ "$_rc" != 0 ]; then
        _frw_ev event=import-refused when=after-exit "record=$_LOG.import.json" decision=REFUSED \
          "reason=the import logged something that is not understood, read after the router ended"
        echo "IMPORT-REFUSED $_LBL: the import logged something that is not understood (read after the router ended; record $_LOG.import.json)"
        _RC=3
      else
        _frw_ev event=import-read when=after-exit "record=$_LOG.import.json"
      fi
    else
      _frw_ev event=no-import "reason=the log has no Opening line: the router never began an import"
    fi
  fi
  _frw_ev event=end "rc=$_RC" "stage=$_STAGE"
  if [ "$_LOG" != /dev/null ]; then
    python3 "$_FRW_CHECK" timing "$_LOG" --events "$_EV" --json "$_LOG.watch.json" --label "$_LBL" 2>&1 | head -2
  fi
  return "$_RC"
}

fr_import_probe() {
  local _PDSN="$1" _PW="$2" _PLB="$3"; shift 3
  if [ "${FR_IMPORT_PROBE:-1}" = 0 ]; then
    echo "$_PLB: import probe SKIPPED by FR_IMPORT_PROBE=0: nothing confirms that the router holds what the DSN declares"
    return 0
  fi
  # THE COPY KEEPS THE DSN'S FILE NAME (round 8, pass 2, measured on board E5 the same night): Freerouting names the
  # design after the DSN's file name up to its first dot (gui/MainApplication.java:597-599) and compares a -dr rules
  # file's name with it (designforms/specctra/RulesFile.java:71-74, a WARN when they differ). A copy named
  # import-probe-in.dsn raised "RulesFile.read: design_name not matching" on EVERY rules file, which the route itself
  # would not; the probe must say what the route will say. So the copy is <work dir>/import-probe-in/<the DSN's name>,
  # a directory of its own (the route's DSN often sits in the probe's work dir) with no <name>.rules beside it.
  mkdir -p "$_PW/import-probe-in"
  local _PIN="$_PW/import-probe-in/$(basename "$_PDSN")" _POUT="$_PW/import-probe.dsn" _PLOG="$_PW/import-probe.log" _PJAR _PXD _PP _PWR _PX _PR
  rm -f "$_POUT" "$_PLOG" "$_PLOG".* "$_PW/import-probe.json" "$_PW/import-probe-in.dsn"
  python3 "$_FRW_CHECK" probe-dsn "$_PDSN" "$_PIN" || { echo "$_PLB: the import probe could not write its copy of the DSN"; return 2; }
  _PJAR="${FR_PROBE_JAR:-}"; [ -n "$_PJAR" ] || _PJAR="$(fr_jar "$_PLB")" || return 2   # fr_probe.sh names its jar itself
  _PXD=$(( 200 + ($$ + RANDOM) % 700 ))
  # a rules file (-dr) is read AFTER the import and can switch the autorouter back on (its autoroute_settings scope
  # defaults to on), so the probe gets a copy of it with the autorouter and the optimiser off and all else unchanged
  local _PA=() _PN=0 _A
  for _A in "$@"; do
    if [ "$_PN" = 1 ]; then
      python3 "$_FRW_CHECK" probe-rules "$_A" "$_PW/import-probe.rules" || { echo "$_PLB: the probe's copy of $_A could not be written"; return 2; }
      _PA+=("$_PW/import-probe.rules"); _PN=0; continue
    fi
    [ "$_A" = -dr ] && _PN=1; _PA+=("$_A")
  done
  # the copy differs from the DSN in one settings block (autoroute off, postroute off), so the job imports, routes
  # nothing, optimises nothing, and writes back the board it holds through -do (MainApplication's autorouter listener)
  timeout "${FR_PROBE_TIMEOUT:-900}" xvfb-run -n "$_PXD" -a java -jar "$_PJAR" -de "$_PIN" -do "$_POUT" -mp 1 -mt 1 -oit 100 -dct 0 "${_PA[@]}" > "$_PLOG" 2>&1 &
  _PP=$!
  FRW_OPT_BOUND=0 fr_watch "$_PP" "$_PXD" "$_PIN" "$_PLB import probe" "$_PLOG"; _PWR=$?
  wait "$_PP"; _PX=$?
  if [ "$_PWR" = 4 ]; then echo "$_PLB: the import probe stalled (records $_PLOG.watch.json), so the import cannot be confirmed"; return 2; fi
  if [ "$_PWR" != 0 ]; then echo "$_PLB: IMPORT-REFUSED by the import probe (records $_PLOG.watch.json)"; return 3; fi
  if [ ! -s "$_POUT" ]; then echo "$_PLB: the import probe wrote no DSN (exit $_PX, log $_PLOG), so the import cannot be confirmed"; return 2; fi
  python3 "$_FRW_CHECK" import "$_PDSN" "$_POUT" --json "$_PW/import-probe.json" | sed "s|^|$_PLB: |"; _PR=${PIPESTATUS[0]}
  [ "$_PR" = 3 ] && echo "$_PLB: IMPORT-REFUSED: the router does not hold what the DSN declares (record $_PW/import-probe.json)"
  return "$_PR"
}

# fr_after_route <dsn> <session> <label> <router log> [ignored classes]: the final session against the DSN, after the
# run; 0 when it may be used, 3 when it lost something (the caller must not import it), 2 when it could not be read.
fr_after_route() {
  local _A_DSN="$1" _A_SES="$2" _A_LB="$3" _A_LOG="$4" _A_INC="${5:-}" _A_W _A_R
  [ -s "$_A_SES" ] || return 0
  _A_W=$(python3 -c "import json,sys; print(','.join(json.load(open(sys.argv[1])).get('warned_nets', [])))" "$_A_LOG.import.json" 2>/dev/null)
  python3 "$_FRW_CHECK" survive "$_A_DSN" "$_A_SES" ${_A_INC:+--ignore-classes "$_A_INC"} ${_A_W:+--warned-nets "$_A_W"} --json "$_A_LOG.final-survive.json" | sed "s|^|$_A_LB: final session: |"
  _A_R=${PIPESTATUS[0]}
  return "$_A_R"
}
