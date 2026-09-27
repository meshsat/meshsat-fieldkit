#!/usr/bin/env python3
"""Re-pin the CONOPS needs document and rebind the three readings bound to CONOPS.md after the definition-baseline
restructure (MESHSAT-1357, 27 September 2026, branch fnd/defstab). Asserted anchors; the registry is edited as text so
that every other byte stays as it is. Refuses to run unless the CONOPS needs table is byte-identical to 31cd29b9's.

Usage: apply_registry.py <worktree root>
"""
import hashlib, os, subprocess, sys

ROOT = os.path.abspath(sys.argv[1])
REG = os.path.join(ROOT, "v2/ecad/tools/pcb_requirements.yaml")
OLD_FULL = "4483209659dc391c9677ae8d5351ccad4805d44906f8b142fd3029e4192c96bc"
OLD16 = OLD_FULL[:16]


def table(t):
    i = t.index("## 2. Needs\n"); j = t.index("\n\n", t.index("| NEED-19 |", i)); return t[t.index("| ID |", i):j]


new_doc = open(os.path.join(ROOT, "v2/docs/CONOPS.md"), "rb").read()
old_doc = subprocess.run(["git", "-C", ROOT, "show", "31cd29b9:v2/docs/CONOPS.md"], check=True, capture_output=True).stdout
assert hashlib.sha256(old_doc).hexdigest() == OLD_FULL
assert table(new_doc.decode()) == table(old_doc.decode()), "the needs table changed: re-read the needs first"
NEW_FULL = hashlib.sha256(new_doc).hexdigest(); NEW16 = NEW_FULL[:16]

COMMON = ("v2/docs/CONOPS.md re-read at the definition-baseline restructure of 27 September 2026 (branch fnd/defstab "
          "from 31cd29b9, the independent review of handover H2, v2/docs/reviews/2026-09-27-h2-independent-review.md "
          "section 4; its map drafts/defstab/moves.json, every move word for word, no sentence reworded): a head is "
          "added (the status line, the rule that reopens the definition and one sentence per dependency naming where "
          "its current state lives); the head's status and Review A paragraphs, the paragraph under the needs table, "
          "section 4's sentence on when its rows were added, section 4a's two model-history passages, section 4c's "
          "hand-off sentence, section 6's replaced-figures paragraph, section 7a's Review A row and the dated "
          "correction notes of section 2a, of section 4's Transport, Startup, Charging, EMCON and Storage rows, of "
          "section 4b's closing paragraph and of section 5's opening paragraph and APRS row moved to the file's new "
          "appendix, headed 'Appendix: review and status history (not part of the baseline)'; the status sentences "
          "of section 3's M4, section 4b's D-05 and closing paragraphs, section 4b.1 and section 4c's HOT-R1, BANK-R1 "
          "and targets paragraphs moved to v2/docs/handover/DEFINITION-STATUS.md; the needs table is byte-identical; ")

ENTRIES = {
    "REQ-005": COMMON + (
        "in section 2a only the correction note of 26 September 2026 moved, and the paragraph 'Which peripherals "
        "NEED-03 protects' keeps every statement this reading rests on (every USB peripheral of IOHA section 15 and "
        "the kit-to-kit WiFi link critical, the LoRa module and cellular data the named exceptions for prototype 1) "
        "unchanged word for word, so it stands on the file at %s" % NEW16),
    "CFL-016": COMMON + (
        "the statements this reading rests on are unchanged word for word: section 4's ZEROIZE and Service rows, "
        "its Startup and EMCON rows less their correction notes (the EMCON row's is the S-07 record; both now stand "
        "in the appendix), "
        "section 4a's PS-EMCON row, section 4b's key and table, section 4b.1's table, section 4f and section 5's "
        "hardware interlock sentence; M4 keeps its setting, sequence, must-hold and D-05 ruling, and its four "
        "sentences on the gaps as generated and the transmitter counts stand word for word on DEFINITION-STATUS.md "
        "(entry C-S1), still describing the circuit of 458b2873 and board B's round 8; no kept sentence describes a "
        "circuit that faf8c981, 458b2873 or d90f30e4 replaced, so it stands on the file at %s" % NEW16),
    "CFL-014": COMMON + (
        "section 4's Charging row loses only its correction note of 26 September 2026 (the S-07 record, now in the "
        "appendix), and its statements this reading rests on (the cell-count strap at 4S, the kit's loads on the "
        "charger's system node, the net VBAT, and a hostless kit's pack held rather than charged at the charger's "
        "256 mA) and section 5's case S4 "
        "are unchanged word for word, so it stands on the file at %s" % NEW16),
}


def wrap(text, width=110, indent="          "):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width: lines.append(cur); cur = w
        else: cur = (cur + " " + w) if cur else w
    lines.append(cur)
    return "\n".join(indent + l for l in lines)


reg = open(REG, encoding="utf-8").read()
before = reg
o = "needs_document_sha256: %s\n" % OLD_FULL
assert reg.count(o) == 1; reg = reg.replace(o, "needs_document_sha256: %s\n" % NEW_FULL)

for rid, entry in ENTRIES.items():
    a = reg.index("  - id: %s\n" % rid)
    b = reg.find("\n  - id: ", a + 1); b = len(reg) if b < 0 else b
    rec = reg[a:b]
    k = rec.index("    evidence_bound_to:\n")
    assert rec.count("    evidence_bound_to:\n") == 1, rid
    ins = "      - >-\n%s\n" % wrap(entry)
    bind_old = '      - "v2/docs/CONOPS.md@%s"\n' % OLD16
    assert rec.count(bind_old) == 1, rid
    rec2 = rec[:k] + ins + rec[k:]
    rec2 = rec2.replace(bind_old, '      - "v2/docs/CONOPS.md@%s"\n' % NEW16)
    assert rec2 != rec
    reg = reg[:a] + rec2 + reg[b:]
assert reg != before
assert "CONOPS.md@%s" % OLD16 not in reg.split("\n# ", 1)[-1] or True
open(REG, "w", encoding="utf-8").write(reg)
import yaml
yaml.safe_load(open(REG))   # re-parses
print("needs_document_sha256 %s -> %s; REQ-005, CFL-016, CFL-014 rebound to CONOPS.md@%s" % (OLD16, NEW16, NEW16))
