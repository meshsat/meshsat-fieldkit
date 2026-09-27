"""r8int5: write only rules_render's group one (the pages the registry alone decides: GOLDEN-RULES, RULE-COVERAGE,
GAP-REGISTER, ETA, PROTOTYPE-UNKNOWNS, REQUIREMENTS-TRACE), with no audit refresh. The per-board status pages and
CURRENT-EVIDENCE are rendered at the integration's last step after rules_status. Run from v2/ecad/tools."""
import os, sys
sys.path.insert(0, os.getcwd())
import rules_render as RR
RR._write(RR.render(board_docs=False))
sys.exit(1 if RR.REFUSED else 0)
