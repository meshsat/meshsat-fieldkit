#!/usr/bin/env bash
# Usage: build_sch.sh <project-dir> <name>  (ERC + netlist + PDF of the schematic)
set -euo pipefail
D="$1"; N="$2"; cd "$D"; mkdir -p out
kicad-cli sch erc --severity-all --exit-code-violations --format report -o "out/$N-erc.rpt" "$N.kicad_sch" && echo "ERC: clean" || echo "ERC: violations (see out/$N-erc.rpt)"
kicad-cli sch export netlist --format kicadsexpr -o "out/$N.net" "$N.kicad_sch" >/dev/null && echo "netlist: out/$N.net"
kicad-cli sch export pdf -o "out/$N-schematic.pdf" "$N.kicad_sch" >/dev/null && echo "pdf: out/$N-schematic.pdf"
kicad-cli sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by Value,Footprint --sort-field Reference -o "out/$N-bom.csv" "$N.kicad_sch" >/dev/null 2>&1 && echo "bom: out/$N-bom.csv" || true
