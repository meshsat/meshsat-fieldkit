#!/usr/bin/env python3
"""Stream s122, round 6 (S-122, MESHSAT-1357, 29 September 2026): the answer to the independent check of fnd/s122c at
a6429e66 (`checks/check-s122-5.md`, B1).

B1 found a figure the closing list carried unjudged: V2-SPEC.md line 47 named the NiceRF SA868 a 1 W part, the figure of
the device set of 6 September (appendix 32.49), while board D's `U2` is the SA868 VHF 2 W exciter, `gen_sch_d.py` has
said "2 W high / 0.5 W low" since `bdfc7b3f`, and the maker's sheet v1.3 gives 31 to 33 dBm on high power and 24 to 26
dBm on low. This script corrects the line to the 2 W exciter and records it as V2-SPEC.md's correction 36.
V2-SPEC.md is not a baselined definition: before it writes, the script reads the table of baselines of
`handover/DEFINITION-STATUS.md` ("## The two baselines") and refuses if V2-SPEC.md is among its documents, and refuses
if `s122lib.BASELINED` names it.
Every part, value, generator text and maker page the new text names is asserted first (the assertion language of
`verdicts.py`); the old passage is found once and the new one reads back once; no dash; the document re-parses. Refuses a
second run. Run: python3 apply_docs_s122_r6.py [--check]."""
import os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import s122lib as L  # noqa: E402
import verdicts as V  # noqa: E402

TAG = "apply_docs_s122_r6"
SPC = "v2/docs/V2-SPEC.md"
DST = "v2/docs/handover/DEFINITION-STATUS.md"
DOCS = {SPC: "9615190d8881790d"}
NETS = {"A": "6c40250c47195ebb", "B": "3ef9b8c49a01b728", "C": "c9f7394594201045", "D": "a2d48972d171aad1",
        "E": "2ed95a0e8069ebf8", "P": "20c7b0795593d761"}
SA868 = "v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf"
ASSERT = {
    "line 47": ["D:U2~NiceRF SA868 VHF 2 W exciter", "D:U6~PCM2912A",
                "PDF:v2/vendor/mitsubishi/ra30h1317m1-datasheet.pdf~RA30H1317M1 RoHS Compliance, 135-175MHz 30W 12.5V"],
    "correction 36": ["DOC:v2/docs/MESHSAT-709-geometry-appendix.md~### 32.49 The V2 device set, ruled device by device",
                      "DOC:v2/docs/MESHSAT-709-geometry-appendix.md~**NiceRF SA868 1 W module plus a 30 W VHF amplifier stage**",
                      "DOC:v2/ecad/tools/gen_sch_d.py~the NiceRF SA868 VHF exciter (bench-fitted, 2 W high / 0.5 W low)",
                      "DOC@bdfc7b3f:v2/ecad/tools/gen_sch_d.py~2 W high / 0.5 W low",
                      "DOC@bdfc7b3f^:v2/ecad/tools/gen_sch_d.py!~2 W high",
                      "PDF:%s~31 32.5 33 dBm|24 25 26 dBm" % SA868],
}
S47_OLD = "| APRS and VHF voice | NiceRF SA868 1 W with a 30 W VHF amplifier stage ("
S47_NEW = "| APRS and VHF voice | NiceRF SA868 VHF 2 W exciter (`U2`, correction 36) with a 30 W VHF amplifier stage ("
C35_END = ("    the outside pod, reached through `J_POD`. Line 83 counted sixteen LEDs; board C carries seventeen, `D22` the\n"
           "    seventeenth. Nothing is built.\n")
C36 = ("\n36. **The exciter's rating (line 47).** Session reading of stream s122, round 6 (29 September 2026, MESHSAT-1357,\n"
       "    open item S-122; its independent check, `v2/docs/records/s122/checks/check-s122-5.md`, B1), whose closing check\n"
       "    since that round asserts every figure and unit on the lines it closes. Line 47 named the NiceRF SA868 a 1 W\n"
       "    part, the figure of the device set of 6 September (appendix 32.49). Board D's `U2` is the SA868 VHF 2 W\n"
       "    exciter; `gen_sch_d.py` has said 2 W high and 0.5 W low since `bdfc7b3f` (7 September), and the maker's sheet\n"
       "    v1.3 (`v2/vendor/nicerf/nicerf-sa868-datasheet-v1.3.pdf`) gives 31 to 33 dBm on high power and 24 to 26 dBm on\n"
       "    low. Nothing is built.\n")
EDITS = [(SPC, S47_OLD, S47_NEW, "line 47"), (SPC, C35_END, C35_END + C36, "correction 36")]


def refuse(m):
    print("%s: REFUSED: %s" % (TAG, m))
    raise SystemExit(2)


def baselined():
    """The documents of DEFINITION-STATUS.md's table of baselines, read from its section '## The two baselines'."""
    txt = open(os.path.join(L.TOP, DST), encoding="utf-8").read()
    if "\n## The two baselines\n" not in txt: refuse("%s has no section '## The two baselines'" % DST)
    sec = txt.split("\n## The two baselines\n", 1)[1].split("\n## ", 1)[0]
    rows = [l for l in sec.split("\n") if l.startswith("| ") and not l.startswith("| Layer") and not l.startswith("|---")]
    docs = [re.findall(r"`([^`]+)`", l.split("|")[2]) for l in rows]
    if len(rows) != 2 or any(len(d) != 1 for d in docs): refuse("the table of baselines does not read as two rows of one document")
    return [d[0] for d in docs]


def main():
    check = "--check" in sys.argv
    head = subprocess.run(["git", "-C", L.TOP, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True).stdout.strip()
    base = baselined()
    if SPC in base or SPC in L.BASELINED: refuse("%s is a baselined document (%s); route the correction through the status page" % (SPC, base))
    nls = L.netlists()
    for b, s in NETS.items():
        if nls[b]["sha16"] != s: refuse("board %s's netlist is %s, not set 14's %s" % (b, nls[b]["sha16"], s))
    for rel, s in DOCS.items():
        if L.sha16(rel) != s: refuse("%s is %s, not the file this script corrects (%s): already applied, or changed" % (rel, L.sha16(rel), s))
    n = 0
    for what, al in ASSERT.items():
        for a in al:
            ok, msg = V.run_assert(a, nls)
            if not ok: refuse("%s: assertion fails: %s" % (what, msg))
            n += 1
    texts = {rel: open(os.path.join(L.TOP, rel), encoding="utf-8").read() for rel in DOCS}
    for rel, old, new, why in EDITS:
        if any(d in new for d in L.DASHES): refuse("%s: a dash in the new text" % why)
        if texts[rel].count(old) != 1: refuse("%s: the old passage is found %d times" % (why, texts[rel].count(old)))
        texts[rel] = texts[rel].replace(old, new)
    for rel, old, new, why in EDITS:
        if texts[rel].count(new) != 1: refuse("%s: the new passage does not read back once" % why)
    line47 = [l for l in texts[SPC].split("\n") if l.startswith("| APRS and VHF voice |")]
    if len(line47) != 1 or " 1 W" in line47[0]: refuse("line 47 does not read as one row without the 1 W figure")
    if check:
        print("%s: --check at %s: %s not among the baselines %s; %d edits located, %d assertions hold; nothing written" % (
            TAG, head, SPC, ", ".join(base), len(EDITS), n))
        return 0
    for rel, txt in texts.items():
        open(os.path.join(L.TOP, rel), "w", encoding="utf-8").write(txt)
        L.md_blocks(rel)
    print("%s: at %s %s is not among the baselines (%s); %d edits written, %d assertions held first; %s" % (
        TAG, head, SPC, ", ".join(base), len(EDITS), n, ", ".join("%s to %s" % (os.path.basename(r), L.sha16(r)) for r in DOCS)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
