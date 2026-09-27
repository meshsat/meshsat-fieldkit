#!/usr/bin/env bash
# w3b (MESHSAT-1357, 27 Sep 2026): the netlist-phase gates that read board B's netlist or intent, run on a given netlist and
# intent with every verdict written under OUT (VERDICT_DIR / --out-dir), never into the tree's own evidence.
# Usage: gates.sh <ecad dir> <netlist> <intent> <out dir>
set -u
E=$1; NET=$(readlink -f "$2"); INT=$(readlink -f "$3"); O=$4; mkdir -p "$O"; O=$(readlink -f "$O")
cd "$E/pcb-b-compute-b19" || exit 2
run () { local nm=$1; shift; VERDICT_DIR="$O" timeout 900 "$@" > "$O/$nm.log" 2>&1; echo "exit $?" >> "$O/$nm.log"; }
run intent_rails python3 ../tools/intent_checks.py --netlist "$NET" --intent "$INT" --out-dir "$O"
run port_protect python3 ../tools/port_protect.py "$NET"
run pin_map_lands python3 ../tools/pin_map_lands.py "$NET" b
run derate python3 ../tools/derate.py "$NET" --intent "$INT"
run safe_lines python3 ../tools/safe_lines.py "$NET"
run power_sequence python3 ../tools/power_sequence.py "$NET" --intent "$INT"
run power_path python3 ../tools/power_path.py "$NET" --intent "$INT" --out-dir "$O"
run clock_check python3 ../tools/clock_check.py "$NET"
run ground_system python3 ../tools/ground_system.py "$NET" --board b
run review_nets python3 ../tools/review_nets.py "$NET"
run edge_length python3 ../tools/edge_length.py --netlist "$NET"
run tx_inhibit python3 ../tools/tx_inhibit.py ../pcb-a-power-a23/out/pcb-a-power.net "$NET" ../pcb-c-display-c8/out/pcb-c-display.net ../pcb-d-aprs-d9/out/pcb-d-aprs.net
( cd "$E" && VERDICT_DIR="$O" timeout 900 python3 tools/check_contracts.py "$E" > "$O/check_contracts.log" 2>&1; echo "exit $?" >> "$O/check_contracts.log" )
( cd "$E/tools" && VERDICT_DIR="$O" timeout 900 python3 energy_chain.py --ecad "$E" > "$O/energy_chain.log" 2>&1; echo "exit $?" >> "$O/energy_chain.log" )
