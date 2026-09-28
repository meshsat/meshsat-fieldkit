#!/usr/bin/env python3
"""S-98 (finding I-03's interim alignment of the A to B power declarations) closed on the regenerated candidate (MESHSAT-1357,
integration set 8, 28 September 2026), by the text of v2/docs/records/s98/registry_s98_closure.md. Every figure of the
closing evidence is READ here from the tree (the intents, the readings, the contract), never typed; the script refuses unless
all four preconditions hold: the five leads AGREE by lead_ends.py on the tree's intents; check_contracts PASS with 0 fail;
interfaces_a and interfaces_b PASS recording the contract's current sha; intent_rails PASS on A and B. It closes S-98 ONLY:
I-03's adequacy (S-99, the mode currents, the lead drop) stays open. Usage (repository root):
python3 <this file> <commit that installed the re-take>. Refuses a second run."""
import hashlib, json, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
import apply_check1_answers as A
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
E = os.path.join(TOP, "v2/ecad")


def refuse(m):
    print("apply_close_s98: REFUSED: %s" % m)
    sys.exit(2)


def sha16(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]


def verdict(rel):
    p = os.path.join(E, rel)
    if not os.path.exists(p): refuse("%s is not in the tree" % rel)
    return json.load(open(p, encoding="utf-8"))


def is_commit(c): return 8 <= len(c) <= 40 and all(ch in "0123456789abcdef" for ch in c)


def main():
    if len(sys.argv) != 2 or not is_commit(sys.argv[1]): refuse("give the commit that installed the re-take")
    commit = sys.argv[1]
    if subprocess.run(["git", "-C", TOP, "cat-file", "-e", commit + "^{commit}"]).returncode: refuse("%s is not in this history" % commit)
    reg = open(REG, encoding="utf-8").read()
    d = yaml.safe_load(reg)
    if any(x["id"] == "S-98" for x in d["closed_items"]): refuse("S-98 is already closed")
    if not any(x["id"] == "S-98" for x in d["open_items"]): refuse("S-98 is not an open item")
    ia = os.path.join(E, "pcb-a-power-a23/out/pcb-a-power-intent.json")
    ib = os.path.join(E, "pcb-b-compute-b19/out/pcb-b-compute-intent.json")
    lo = subprocess.run([sys.executable, os.path.join(TOP, "v2/docs/records/s98/lead_ends.py")], cwd=TOP, capture_output=True, text=True)
    m = re.search(r"(\d+) of (\d+) leads AGREE", lo.stdout)
    if not m or m.group(1) != m.group(2): refuse("lead_ends does not read every lead AGREE: %s" % lo.stdout.strip()[-200:])
    cc = verdict("pcb-a-power-a23/routed/check_contracts.verdict.json")
    if cc.get("verdict") != "PASS" or (cc.get("counts") or {}).get("fail"): refuse("check_contracts reads %s" % cc.get("verdict"))
    spec = sha16(os.path.join(E, "tools/pcb_interfaces.yaml"))
    ivs = {}
    for L, pd in (("a", "pcb-a-power-a23"), ("b", "pcb-b-compute-b19")):
        v = verdict("%s/routed/interfaces_%s.verdict.json" % (pd, L))
        if v.get("verdict") != "PASS" or spec not in json.dumps(v.get("inputs") or {}):
            refuse("interfaces_%s reads %s or does not record the contract %s" % (L, v.get("verdict"), spec))
        ivs[L] = v.get("denominator")
        r = verdict("%s/routed/intent_rails.verdict.json" % pd)
        if r.get("verdict") != "PASS": refuse("intent_rails on %s reads %s" % (L.upper(), r.get("verdict")))
    ev = ("The interim alignment applied by the generator owners of boards A and B (stream s98, c098b8f3, merged into integration set 8): "
          "board A's +5V_S2 4.2 A typical and 5.63 A peak with J_5V_S2 5.63 A and the VBAT load Q28 2.22 A, board B's +5V_S2 peak 5.63 A, "
          "board A's J_5V_DEV 3.8 A and +5V_DEV typical 5.1 A, the notes rewritten INTERIM with the PS-ALLTX mode figures INCONCLUSIVE, "
          "board B's M7 branches reconciled (U21 0.70 A, U40, U50 and U60 0.12 A, U25's comment at the declared 1.2 A). Regenerated on the "
          "KiCad box (records/s98/box_regen_ab.sh at fff04e64; the netlists PARITY_AFTER_NOISE, content unchanged; "
          "v2/docs/records/int9/box/regen-s98-summary.txt) and committed; every schematic-phase reading re-taken at the commit carrying them, "
          "landed by %s: intents intent_a %s and intent_b %s; lead_ends.py %s of %s leads AGREE; check_contracts PASS of %s with 0 fail "
          "(v2/ecad/pcb-a-power-a23/routed/check_contracts.verdict.json); "
          "interfaces_a PASS of %s and interfaces_b PASS of %s on the rewritten contract v2/ecad/tools/pcb_interfaces.yaml (spec %s, "
          "apply_contract_i03.py; v2/ecad/pcb-a-power-a23/routed/interfaces_a.verdict.json, v2/ecad/pcb-b-compute-b19/routed/interfaces_b.verdict.json); intent_rails PASS "
          "on A and B (PWR-001). ARCHITECTURE.md's IF-AB-POWER row brought to the same statement and to the held JST VH catalogue "
          "(apply_architecture_i03.py). DECLARATION CONSISTENCY ONLY: the electrical adequacy of the converters against their loads is "
          "S-99's, the PS-ALLTX mode currents are the bench's (TEST-PLAN power rows), and the +5V_S2 all-peak bound of 7.28 A against the "
          "loop minimum and the lead's own drop stay open with I-03."
          % (commit, sha16(ia), sha16(ib), m.group(1), m.group(2), cc.get("denominator"), ivs["a"], ivs["b"], spec))
    A.screen(ev, "S-98's closing evidence")
    i, j = A.span(reg, "S-98")
    blk = reg[i:j]
    tm = re.search(r"(?m)^    title: >-\n", blk)
    title = blk[tm.end():].rstrip("\n")
    out = reg[:i] + reg[j:]
    k = out.index("\nrecords:\n")
    closed = "  - id: S-98\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s\n" % (commit, A.fold(ev, 6, 120), title)
    out = out[:k + 1] + closed + out[k + 1:]
    after = yaml.safe_load(out)
    if [x["id"] for x in after["open_items"]] != [x["id"] for x in d["open_items"] if x["id"] != "S-98"]: refuse("open items changed beyond S-98")
    if [x["id"] for x in after["closed_items"]] != [x["id"] for x in d["closed_items"]] + ["S-98"]: refuse("closed items changed beyond S-98")
    for sec in d:
        if sec not in ("open_items", "closed_items") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    open(REG, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(REG, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("apply_close_s98: S-98 closed by commit %s (leads %s of %s AGREE; check_contracts PASS of %s; interfaces_a %s, interfaces_b %s; "
          "spec %s); I-03's adequacy stays open" % (commit[:8], m.group(1), m.group(2), cc.get("denominator"), ivs["a"], ivs["b"], spec))
    return 0


if __name__ == "__main__":
    sys.exit(main())
