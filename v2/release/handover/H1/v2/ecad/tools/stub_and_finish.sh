#!/usr/bin/env bash
# Usage: stub_and_finish.sh <dir> <name> <postfix> <downloads-name> : close the DRC-listed gaps with the grid router, then re-finish the board
cd "$1"; N="$2"
cp $N.kicad_pcb out/$N-before-stubs.kicad_pcb
nice -n 10 python3 ../tools/stub_router.py $N.kicad_pcb out/$N-drc.json 2>&1 | grep -vE 'Debug|memory leak|assert'
cd ..; ./tools/finish_board.sh "$1" "$2" "$3" "$4" 2>&1 | tail -16
echo STUB-FINISH-DONE
