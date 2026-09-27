#!/usr/bin/env python3
"""Layer 5 closer hc5 (MESHSAT-1357, 27 September 2026): v2/docs/ARCHITECTURE.md.

  Section 12 (owned): replaced whole by drafts/hc5/ARCHITECTURE-section-12.md (thirty contracts, judged_by by section
      number, the kit bus budget pointer, round 8's R8E-N01). Board E's round 8 docs patch (r8e-4-docs) is on main since
      45f6d83f and its two section 12 rows (IF-AE-DOCK, IF-AE-RF) are carried in the replacement with their facts (the
      clamp bar at 45f6d83f, R8E-N01, 14.10 A), so nothing of it is left to drop. Section 12 is byte-identical from
      84e52461 to a8652172, so the replacement drops nothing main added there.
  Section 5.5 (outside; reason: the address block's "still name 0x30 to 0x32" is made false by the drafts filed with it,
      and the bus speed and budget belong beside the address table): two sentences and one paragraph.
  Section 10 (outside; reason: the summary must point at the itemised contract it summarises): one sentence.

Idempotent; every anchor asserted once. Run from the repository root:  python3 drafts/hc5/apply_architecture.py"""
import os

ROOT = os.getcwd()
P = os.path.join(ROOT, "v2/docs/ARCHITECTURE.md")
NEW12 = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ARCHITECTURE-section-12.r8int4.md")   # r8int4: section 12 three-way merged with board B round 8 IF-BC-PANEL row
s = open(P, encoding="utf-8").read()
log = []


def rep(old, new, marker=None):
    global s
    m = marker or new
    if m in s:
        log.append("already: " + m.strip()[:60]); return
    n = s.count(old)
    assert n == 1, "anchor found %d times: %r" % (n, old[:90])
    s = s.replace(old, new); log.append("edited: " + old.strip()[:60])


# section 12, whole
new12 = open(NEW12, encoding="utf-8").read().rstrip("\n") + "\n\n"
a, b = "\n## 12. Interface contracts\n", "\n## 13. Known design findings\n"
assert s.count(a) == 1 and s.count(b) == 1
i, j = s.index(a) + 1, s.index(b) + 1
if "**Thirty contracts since 27 September 2026.**" in s[i:j]:
    log.append("already: section 12")
else:
    s = s[:i] + new12 + s[j:]; log.append("replaced: section 12")

# section 5.5
# r8int4: board B's round 8 (b76c18cb) had already rewritten this row's IOHA clause on 38dcd764
rep("| **firmware, taken by the session (I3-F01, below)**; `ARCH-PCB-B-IOHA.md` section 6 names 0x34 to 0x36 since board B's round 8 (27 September 2026); `ZEROIZE.md` firmware rule Z-C3 still names 0x30 to 0x32 |",
    "| **firmware, taken by the session (I3-F01, below)**; `HW-FW-CONTRACT.md` FW-B08; `ARCH-PCB-B-IOHA.md` section 6 (since board B's round 8), `PANEL.md` section 7 and `ZEROIZE.md` rule Z-C3 carry the block since 27 September 2026 |")
rep("The IOHA note's section 6 and `ZEROIZE.md` section 9\n  item 8 are owed the same block by their writers.",
    "The IOHA note's section 6, `PANEL.md` section 7,\n  `ZEROIZE.md` Z-C3 and section 9 item 8, CON-020 and S-41 carry the same block since 27 September 2026 (layer 5 closer).")
rep("  0x20, which U6 holds) or by a separate supervisor bus.\n",
    "  0x20, which U6 holds) or by a separate supervisor bus.\n\n"
    "  **Speed, pull-ups and capacitance (27 September 2026, `HW-FW-CONTRACT.md` section 6).** Standard-mode, 100 kHz\n"
    "  programmed and at least 90 kHz achieved (FW-K01; `ZEROIZE.md`'s time budget re-run at 90 kHz holds). The pull-ups\n"
    "  are 2.2 k on B and 2.2 k on C, with the KSZ9897R's internal 58 k, already at the 3 mA the weakest targets sink at\n"
    "  0.4 V, so they cannot be made stronger. Four targets state a 300 ns rise at any clock (BQ25731, TPS23861,\n"
    "  ATECC608B and board D's round 8 ADS1115); as one segment the bus's pins and ribbons alone exceed the limit at their\n"
    "  published maxima, and the copper of the committed layouts exceeds it at typical ones (finding HF-F01). Taken by the\n"
    "  session (SC-HF-02): three segments behind two TCA9517A, board A's and D's targets behind one on A, the supervisors,\n"
    "  the TPS23861 and the KSZ9897R behind one on B that the panel opens only for its own transactions to them. Owed on\n"
    "  boards A and B, with the copper allowances handed to layout; until drawn, HF-F01 stands.\n",
    "  **Speed, pull-ups and capacitance (27 September 2026")

# section 10
rep("## 10. Hardware and firmware contract (summary)\n\n### 10.1 Who owns what",
    "## 10. Hardware and firmware contract (summary)\n\nThe itemised contract, each obligation with the hardware fact it rests on and its verification, is\n"
    "`HW-FW-CONTRACT.md` (version 1, 27 September 2026: FW-A01 to A16, FW-B, C, D, E, P and K rows, the kit bus budget);\n"
    "this section is its summary, and where the two differ the itemised page governs.\n\n### 10.1 Who owns what",
    "The itemised contract, each obligation with the hardware fact it rests on")

assert chr(0x2014) not in s and chr(0x2013) not in s
open(P, "w", encoding="utf-8").write(s)
print("\n".join(log))
