#!/usr/bin/env bash
# Render every Mermaid source in v2/docs/diagrams/src/ to svg/ and pdf/ (MESHSAT-1357, handover layer 4).
#
# Tool: @mermaid-js/mermaid-cli, pinned below, run through npx; it drives a headless Chromium through Puppeteer.
# Chromium: set CHROME_BIN to a local Chromium or chrome-headless-shell binary; without it Puppeteer uses the browser
# it downloads itself on first run. The runner used for the committed files had Playwright's chrome-headless-shell
# (Chrome for Testing 151.0.7922.34) and Node 20.20.2 (see ../README.md, "Toolchain").
# Usage: bash v2/docs/diagrams/tools/render.sh [name ...]   (names without .mmd; default: every source)
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
D=$(dirname "$HERE")
MMDC_VERSION=${MMDC_VERSION:-11.12.0}
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
if [ -n "${CHROME_BIN:-}" ]; then
  printf '{"executablePath":"%s","args":["--no-sandbox"]}\n' "$CHROME_BIN" > "$TMP/puppeteer.json"
else
  printf '{"args":["--no-sandbox"]}\n' > "$TMP/puppeteer.json"
fi
# The PDF pass renders at the drawing's natural size: Mermaid's useMaxWidth (true by default) fits a diagram to the
# 800 px page of mermaid-cli, which printed the wide diagrams at 1 to 2 pt text (review of 27 September 2026). The SVGs
# keep useMaxWidth, so a browser scales them to its window; the layout is the same in both (useMaxWidth sets only the
# SVG's width attribute).
python3 - "$HERE/mermaid.json" "$TMP/mermaid-pdf.json" <<'PY'
import json, sys
c = json.load(open(sys.argv[1]))
for k in ("flowchart", "state"):
    c.setdefault(k, {})["useMaxWidth"] = False
json.dump(c, open(sys.argv[2], "w"), indent=1)
PY
names=("$@")
if [ ${#names[@]} -eq 0 ]; then for f in "$D"/src/*.mmd; do names+=("$(basename "$f" .mmd)"); done; fi
mkdir -p "$D/svg" "$D/pdf"
for n in "${names[@]}"; do
  src="$D/src/$n.mmd"
  npx -y "@mermaid-js/mermaid-cli@$MMDC_VERSION" -q -p "$TMP/puppeteer.json" -c "$HERE/mermaid.json" -b white \
      -i "$src" -o "$D/svg/$n.svg"
  npx -y "@mermaid-js/mermaid-cli@$MMDC_VERSION" -q -p "$TMP/puppeteer.json" -c "$TMP/mermaid-pdf.json" -b white -f \
      -i "$src" -o "$D/pdf/$n.pdf"
  echo "rendered $n"
done
