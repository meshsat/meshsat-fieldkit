#!/usr/bin/env python3
"""The IF-AB-POWER row of v2/docs/ARCHITECTURE.md (the contracts table, "Open items" column) brought to the interim
alignment of S-98 and to the held JST VH catalogue (stream s98, MESHSAT-1357, 28 September 2026; finding I-03; the
Codex pilot's correction item M8 and its check).

The row's open-items cell said "the two ends' current declarations disagree (I-03 ...); the JST-VH rating document is
not held". Both halves are stale: the two generators carry the interim alignment (fnd/s98) and the catalogue is held
(v2/vendor/connectors/jst-vh-catalogue.pdf, page 1: 10 A per contact at AWG 16 on the standard header; page 3 the
fitted B2P-VH; no rating is stated for AWG 18 on the standard header, so J_54V's lead stays INCONCLUSIVE).

THE BINDING. The integrator's notes say this page is bound by a registry record (evidence_bound_to); on the tree this
stream was cut from (dcf04c90) NO record of tools/pcb_requirements.yaml binds v2/docs/ARCHITECTURE.md by sha
(`git log -S"docs/ARCHITECTURE.md@"` finds no such binding in the file's history either). So this script REFUSES to run
if a binding exists (it names the record: a rebind entry on the pattern of v2/docs/records/int7/apply_rebind_final_page.py
is then owed before the page is changed), and otherwise says plainly that no record is rebound. It also compares the
page's sections before and after and asserts that exactly one line, the row, differs, so any record that cites a
section of this page by content can see that nothing else moved.

Usage: python3 apply_architecture_i03.py [--root <repository root>]   (default: the git top level of this file)
Refuses a second run (the old row is gone, the new row is present).
"""
import hashlib, os, re, subprocess, sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

OLD = ("| IF-AB-POWER | A and B J_5V_S1..3, J_5V_DEV, J_54V (VH) | slot rails, device rail, 54 V | section 3 (net presence) | "
       "the two ends' current declarations disagree (I-03: +5V_S2 A 2.5 A against B 4.2 A typical, 5.63 A coincident; +5V_DEV "
       "A 3.2 A against B 3.8 A); the JST-VH rating document is not held |\n")
NEW = ("| IF-AB-POWER | A and B J_5V_S1..3, J_5V_DEV, J_54V (VH) | slot rails, device rail, 54 V | section 3 (net presence) | "
       "the two ends' current declarations AGREE since S-98 (28 September 2026), INTERIM: +5V_S2 4.2 A typical and 5.63 A peak "
       "at both ends, +5V_DEV 3.8 A at the lead, with the PS-ALLTX mode figures INCONCLUSIVE at both ends (v2/docs/records/cx1/); "
       "the converter-side peak of +5V_DEV is S-99's; the JST VH catalogue is held (page 1: 10 A per contact at AWG 16 on the "
       "standard header; no rating is stated for the AWG 18 lead of J_54V on the standard header, INCONCLUSIVE) |\n")


def refuse(msg):
    print("apply_architecture_i03: REFUSED: %s" % msg); sys.exit(2)


def sections(page):
    out = [["the head", []]]
    for line in page.split("\n"):
        if line.startswith("## ") or line.startswith("### "): out.append([line.lstrip("# ").strip(), []])
        else: out[-1][1].append(line)
    return [(h, "\n".join(b)) for h, b in out]


def main(argv):
    root = argv[argv.index("--root") + 1] if "--root" in argv else subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
    P = os.path.join(root, "v2/docs/ARCHITECTURE.md"); REG = os.path.join(root, "v2/ecad/tools/pcb_requirements.yaml")
    if re.search("[\\u2013\\u2014]", NEW): refuse("the new text carries a dash")
    reg = open(REG, encoding="utf-8").read()
    bound = re.findall(r'"v2/docs/ARCHITECTURE\.md@([0-9a-f]{16})"', reg)
    if bound:
        recs = [m.group(1) for m in re.finditer(r"(?m)^  - id: (\S+)\n(?:(?!^  - id: ).*\n)*?.*v2/docs/ARCHITECTURE\.md@", reg)]
        refuse("the registry binds v2/docs/ARCHITECTURE.md by sha (%s) in record(s) %s: write the rebind entry first "
               "(pattern: v2/docs/records/int7/apply_rebind_final_page.py), then run this" % (sorted(set(bound)), recs))
    t = open(P, encoding="utf-8").read()
    if t.count(OLD) != 1:
        if t.count(NEW) == 1: refuse("already applied")
        refuse("the old row occurs %d time(s)" % t.count(OLD))
    out = t.replace(OLD, NEW, 1)
    if out == t: refuse("the new text does not differ from the old")
    ol, nl = t.split("\n"), out.split("\n")
    if len(ol) != len(nl): refuse("the line count changed")
    changed = [k + 1 for k, (x, y) in enumerate(zip(ol, nl)) if x != y]
    if len(changed) != 1: refuse("%d lines differ, one expected" % len(changed))
    so, sn = sections(t), sections(out)
    if [h for h, _ in so] != [h for h, _ in sn]: refuse("the headings changed")
    differ = [h for (h, x), (_, y) in zip(so, sn) if x != y]
    if len(differ) != 1: refuse("%d sections differ, one expected" % len(differ))
    open(P, "w", encoding="utf-8").write(out)
    if open(P, encoding="utf-8").read() != out: refuse("the file written differs from what was checked")
    print("apply_architecture_i03: ARCHITECTURE.md line %d (the IF-AB-POWER row) rewritten; of %d sections only %r differs, %d byte-identical"
          % (changed[0], len(sn), differ[0], len(sn) - 1))
    print("apply_architecture_i03: sha256/16 %s -> %s; no registry record binds this page by sha, so no rebind is made"
          % (hashlib.sha256(t.encode("utf-8")).hexdigest()[:16], hashlib.sha256(out.encode("utf-8")).hexdigest()[:16]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
