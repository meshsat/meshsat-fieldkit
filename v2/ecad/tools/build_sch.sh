#!/usr/bin/env bash
# Usage: build_sch.sh <project-dir> <name>  (ERC + netlist + PDF of the schematic)
set -euo pipefail
D="$1"; N="$2"; cd "$D"; mkdir -p out
kicad-cli sch erc --severity-all --format report -o "out/$N-erc.rpt" "$N.kicad_sch" >/dev/null 2>&1 || true
# 8 Sep 2026 (MESHSAT-862): the exit code used to become an echo that no chain read; erc_gate.py reads the JSON and blocks on errors not allow-listed
rm -f "out/$N-erc.json"; if kicad-cli sch erc --severity-all --exit-code-violations --format json -o "out/$N-erc.json" "$N.kicad_sch" >/dev/null 2>&1; then echo "ERC: clean"; else echo "ERC: violations (out/$N-erc.json, out/$N-erc.rpt; erc_gate.py decides)"; fi
kicad-cli sch export netlist --format kicadsexpr -o "out/$N.net" "$N.kicad_sch" >/dev/null && echo "netlist: out/$N.net"
# WHICH GENERATOR WROTE IT (16 September 2026). A netlist copied into another tree keeps its timestamp beside
# its own schematic's, so the staleness guard in check_contracts.py cannot see that both are old: that is how
# a set-level contract verdict came to fail twelve contracts about six capacitors that had been in the design
# since 02:40. The sidecar names the generator by content, and a check that runs under different content says
# so instead of deciding. The letter is the second field of the stem, `pcb-b-compute` -> `b`.
python3 "$(dirname "$0")/sch_prov.py" write "out/$N.net" "$(echo "$N" | cut -d- -f2)" || true
# 15 Sep 2026 (MESHSAT-862, 32.196): the sheet is a grid of A3 cells (schlayout.py), so the PDF a reader opens is that grid cut into
# A3 pages, one block per page, no drawing-sheet border across the cells. The whole sheet stays beside it for a viewer that wants it.
kicad-cli sch export pdf --exclude-drawing-sheet -o "out/$N-schematic-sheet.pdf" "$N.kicad_sch" >/dev/null && echo "sheet pdf: out/$N-schematic-sheet.pdf"
python3 "$(dirname "$0")/sch_pages.py" "$N.kicad_sch" "out/$N-schematic-sheet.pdf" "out/$N-schematic.pdf" && echo "pdf: out/$N-schematic.pdf"
kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "out/$N-bom.csv" "$N.kicad_sch" >/dev/null 2>&1 && echo "bom: out/$N-bom.csv" || true
