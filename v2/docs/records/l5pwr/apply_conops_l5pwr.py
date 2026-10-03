#!/usr/bin/env python3
"""apply_conops_l5pwr.py: DRAFT for the CONOPS owner (Layer 5's power pass, MESHSAT-1357, set 27, 3 October 2026). NOT APPLIED to
the tree by Layer 5, whose brief owns pcb_interfaces.yaml, HW-FW-CONTRACT.md and PANEL.md section 10 and not CONOPS.md; run on
scratch copies only (the test does).

What it adds to v2/docs/CONOPS.md, at the end of section 4c and before 4d, as the two CONOPS halves of L4-E9's register:
  R-138 (LAYER5-HANDOVER LH-11; L4-E12 section 6): the margin hold as a mode beyond the envelope, with the SGP41's own shutdown;
  R-133 (L4-E11 7b): the source-only statement, the kit with no usable pack within the source envelope at its plug.
Both texts are Layer 4's as drafted; the figures are PROVISIONAL where L4-E12 marks them so. CONOPS.md is bound in the
requirements registry (pcb_requirements.yaml, CONOPS.md@6cb7b241) and pinned by L4-E12's l4e12_thermal.py, so the owner who
applies this rebinds those readings afterwards (the integration recipe for the evidence pages).

Usage:  apply_conops_l5pwr.py TARGET [--check | --write]     (default --check: nothing is written)
The anchor must occur exactly once and the new text must not occur yet; the result must differ; no em or en dash. A second run
refuses. Exit 0: checked (or written); 3: refused."""
import difflib
import os
import sys

NAME = "apply_conops_l5pwr"
ANCHOR = "### 4d. Commissioning (added 27 September 2026)\n"
NEW = """**Added 3 October 2026 (Layer 5's power pass, set 27; L4-E12 section 6 and L4-E11 7b, drafted for this page's owner by
`records/l5pwr/apply_conops_l5pwr.py`; nothing built or measured).**

**The margin hold (E5), a mode beyond the envelope.** When the mixed air near the +70 C parts reads 68.65 C plus the reference's
calibrated offset (the reference placed in that air, or board B's TMP117 calibrated at T-H1 to within 0.899099 K), the kit holds
the charge by the charger's inhibit bit, powers off board D and the PA rail through board A's expanders, the RockBLOCK, the LoRa
module, both E72 and the Geiger module through their enables, idles the running module with its logging kept, and queues an SOS
raised meanwhile as under EMCON (D-10) with the operator told; it restores 5 K under the trigger after 30 minutes (PROVISIONAL).
The hold acts under the heat stage and before the hot stop's H1, which overrides it (`HW-FW-CONTRACT.md` FW-C15; L4-E12 section
6, the trigger window of 2.45 K that exists only with that reference). The battery-bay gas sensor (the SGP41) is powered off at a
reading of 54.0 C on its carrier's sensor and its output used only at or under 49.0 C; between the two its channel is reported
as not covered (FW-E12; CFL-002 option C).

**With no usable pack** (absent, at its cutoff, or cold-soaked with its FETs open) the kit runs from its vehicle or shore input
within the source envelope at its input plug: about 29 W at 9 V, 32 W at 12 V and 70 W at 24 V on its bus at the least. At 9 V
it sheds to one module with its fans, HF, Geiger and 5G modules held and runs the pack heater on the headroom left, which warms
a cold-soaked pack at the plan load; the time is measured on the prototype. A pack self-discharged under about 2.4 V a cell
holds the system node under the converters' floor while it pre-charges, so the kit's loads wait for it. A brown-out on the input
alone may latch the charger off until the input is re-plugged (L4-E11 7b; `HW-FW-CONTRACT.md` FW-A19 to FW-A21).

"""


def refuse(msg):
    sys.stderr.write("%s: %s; refusing\n" % (NAME, msg))
    sys.exit(3)


def patched(t):
    if "**The margin hold (E5), a mode beyond the envelope.**" in t:
        refuse("already applied")
    if t.count(ANCHOR) != 1:
        refuse("the anchor occurs %d times, not once" % t.count(ANCHOR))
    out = t.replace(ANCHOR, NEW + ANCHOR)
    if out == t:
        refuse("the result does not differ")
    if chr(0x2014) in out or chr(0x2013) in out:
        refuse("a dash character in the result")
    return out


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = [a for a in argv if a.startswith("--")]
    if len(args) != 1 or any(f not in ("--check", "--write") for f in flags) or len(flags) > 1:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n")
        return 2
    target, write = args[0], flags == ["--write"]
    if os.path.basename(target) != "CONOPS.md":
        refuse("TARGET is not CONOPS.md")
    text = open(target, encoding="utf-8").read()
    new = patched(text)
    sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True), "a/CONOPS.md", "b/CONOPS.md", n=0))
    if not write:
        print("%s: CHECK OK, nothing written" % NAME)
        return 0
    open(target, "w", encoding="utf-8").write(new)
    if open(target, encoding="utf-8").read() != new:
        refuse("the written file does not read back as the patched text")
    print("%s: WRITTEN" % NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
