#!/usr/bin/env python3
"""apply_gen_sch_b_xal_land.py: DRAFT for board B's generator owner (Layer 6 record l6r2 round 3, MESHSAT-1357, 3 October 2026).
NOT APPLIED. A Layer 8 draft on the footprint key of board B's Coilcraft rows whose footprint names another body than the part
their value names (criterion 6.4); the edits, their evidence and the logic are in l6r2_land.py, the record in L6R2-PASSIVES.md
section 8.2. test_l6r2.py proves its composition with every other pending draft of the generator, this record's LCSC draft included.
Usage:  apply_gen_sch_b_xal_land.py TARGET [--check | --write]     (default --check: nothing is written)
Exit 0: checked (or written); 3: refused (the release guard, a second application, an old text not found once, the parse)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import l6r2_land  # noqa: E402

if __name__ == "__main__":
    sys.exit(l6r2_land.main("b", sys.argv[1:]))
