#!/usr/bin/env python3
"""Stream w3b (MESHSAT-1357, 27 September 2026): W3B-R1 renames board B's coin-cell net VBAT to VBAT_RTC. The comparator sees a
net removed and a net added; this holds the renamed net's nodes equal to the old net's plus W3B-F2's three capacitors, pin for
pin (ref, pin, pintype), with the comparator's own reader. A pin function may change only from VBAT to VBAT_RTC, on a part whose
symbol names its pins after their nets (gen_sch_b.py's ic(): U9, the DS3231SN). Usage: rename_check.py <indep_cmp.py> <old.net> <new.net>"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ic", sys.argv[1]); ic = importlib.util.module_from_spec(spec); spec.loader.exec_module(ic)
(_oc, on), (_nc, nn) = ic.load(sys.argv[2]), ic.load(sys.argv[3])
old, new = on.get("/VBAT"), nn.get("/VBAT_RTC")
assert old is not None and new is not None and "/VBAT" not in nn and "/VBAT_RTC" not in on
ko = {(r, p, t): f for r, p, f, t in old}; kn = {(r, p, t): f for r, p, f, t in new}
extra = sorted(set(kn) - set(ko)); missing = sorted(set(ko) - set(kn))
fn = sorted((k, ko[k], kn[k]) for k in set(ko) & set(kn) if ko[k] != kn[k])
print("old /VBAT %d nodes, new /VBAT_RTC %d nodes; only in the new: %s; only in the old: %s; pin functions changed: %s"
      % (len(old), len(new), extra, missing, fn))
ok = (not missing and {k[0] for k in extra} == {"C72", "C73", "C74"} and all(k[1] == "1" for k in extra)
      and all(a == "VBAT" and b == "VBAT_RTC" for _k, a, b in fn))
print("RENAME PARITY" if ok else "RENAME MISMATCH"); sys.exit(0 if ok else 1)
