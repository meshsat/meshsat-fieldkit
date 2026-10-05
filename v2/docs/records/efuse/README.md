# efuse: every eFuse and current-limit setting checked against its exact part's datasheet (task T12, MESHSAT-1357)

Record `efuse`, 5 October 2026, branch `fnd/efuse` from main `aa32332c`. Driven by finding SDR3-F04 (the three-SDR research,
confirmed by the collaborator's challenge cx42 and recheck cx43): board B's U23, a TPS259631 eFuse feeding the LimeSDR's USB, has
its current-limit resistor at 301 Ohm labelled "3.0 A", while TI's TPS2596 sheet (SLVSET8A) prints a 0.125 to 2 A range and a
453 to 7869 Ohm recommended resistance.

Prototype design, desk arithmetic: nothing in this kit has been built, bought, powered or measured. Nothing here is applied to
the tree; every draft refuses the repository's own generator until a `RELEASE.md` beside it names an accepted check.

STATE (checkpoint, 5 October 2026 11:45 CEST): the inventory and the sheets are read; the check script, the page, the draft and
the test are being written. Next action: `efuse_check.py`.
