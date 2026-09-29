#!/usr/bin/env python3
"""S-120's closure in the requirements registry (stream s120, MESHSAT-1357, 29 September 2026). DRAFT for the integrator,
one phase.

  close <commit>   AFTER this stream's records are merged at <commit>. It refuses unless
                   (1) <commit> is in this history and carries README.md, LOG.md, vbus20_bound.py and vbus20_bound.out of
                       v2/docs/records/s120/ byte for byte as they are committed at HEAD, with no uncommitted change to any;
                   (2) vbus20_bound.py, re-run here on the committed netlists of boards A and E, reads every circuit fact it
                       rests on (exit 0) and prints the committed .out again, the two netlist sha lines aside: so a board A
                       or E regenerated since this stream changes nothing the bound depends on, or the closure refuses;
                   (3) S-120 is an open item, REQ-015 waits on it, and neither the switch-node item nor S-111's addition is
                       in the registry yet (a second run refuses).
                   Then: S-120 moves to closed_items (closed by <commit>; its closing evidence names the files, and every
                   figure in it is read from vbus20_bound.FIG here, never typed); a new SESSION item (the next free S
                   number) carries the switch nodes' ringing budget for board A's layout writer and the bench, and takes
                   S-120's place in REQ-015's waits_on; S-111's title gains S-120's residual (the single faults that blind
                   or bypass the front end's protection). Nothing else moves; the registry is re-parsed and compared.

No circuit change is drawn by this stream (the answer is (a), the bound holds), so no netlist read-back of a new part is
owed; check (2) is the netlist gate instead: it re-reads every part and net the bound rests on.

Every added text passes int7's screen (no claim word, no dash). --check validates in memory and writes nothing. --registry
PATH points the script at a copy of the registry (the dry run); the default is v2/ecad/tools/pcb_requirements.yaml.

Usage (anywhere in the tree): python3 apply_registry_s120.py close <commit> [--check] [--registry PATH]"""
import contextlib
import io
import os
import re
import subprocess
import sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REG_DEFAULT = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml")
REC = "v2/docs/records/s120"
EVIDENCE = ["README.md", "LOG.md", "vbus20_bound.py", "vbus20_bound.out"]
sys.path.insert(0, os.path.join(TOP, "v2/docs/records/int7"))
sys.path.insert(0, os.path.join(TOP, "v2/ecad/tools"))
sys.path.insert(0, HERE)
import apply_check1_answers as A  # noqa: E402  (span, fold, screen: the registry's own editing helpers)

RING_MARK = "(stream s120, S-120's switch nodes;"
S111_MARK = " S-120's residual (stream s120,"


def refuse(m):
    print("apply_registry_s120: REFUSED: %s" % m)
    sys.exit(2)


def git(*args):
    return subprocess.run(["git", "-C", TOP] + list(args), capture_output=True)


def evidence_gate(commit):
    if not re.match(r"^[0-9a-f]{8,40}$", commit or ""): refuse("give the commit that carries this stream's records")
    if git("cat-file", "-e", commit + "^{commit}").returncode: refuse("%s is not in this history" % commit)
    for f in EVIDENCE:
        path = "%s/%s" % (REC, f)
        if git("ls-files", "--error-unmatch", path).returncode: refuse("%s is not committed" % path)
        if git("diff", "--quiet", "HEAD", "--", path).returncode: refuse("%s has an uncommitted change" % path)
        at_c = git("rev-parse", "%s:%s" % (commit, path))
        at_h = git("rev-parse", "HEAD:%s" % path)
        if at_c.returncode or at_c.stdout != at_h.stdout: refuse("%s at %s differs from HEAD's" % (path, commit[:8]))


def rerun_bound():
    import vbus20_bound as VB
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = VB.main([])
    if rc != 0: refuse("vbus20_bound.py reads a circuit fact FAIL on the committed netlists (exit %d)" % rc)
    keep = lambda text: [l for l in text.split("\n") if not l.startswith(("netlist A ", "netlist E "))]
    committed = open(os.path.join(HERE, "vbus20_bound.out"), encoding="utf-8").read()
    if keep(buf.getvalue()) != keep(committed): refuse("vbus20_bound.py no longer prints the committed .out on this tree")
    return VB.FIG


def next_s(d):
    ids = [x["id"] for sec in ("open_items", "closed_items") for x in d.get(sec) or []]
    nums = [int(m.group(1)) for i in ids for m in [re.match(r"^S-(\d+)$", str(i))] if m]
    return "S-%d" % (max(nums) + 1)


def texts(F, commit, ring_id):
    r = F["ring_A2"]
    ring = (
        "(stream s120, S-120's switch nodes; the independent re-check of stream s117, minor n1) Board A's charger switch "
        "nodes against the 30 V FETs of decision 57 (Q7 CSD17578Q5A, Q8 to Q10 CSD17577Q5A; VDS 30 V absolute, TI SLPS526 "
        "and SLPS516 page 1) and the BQ25731's own SW1 and SW2 (32 V absolute, 26 V recommended, -4 V for 25 ns; SLUSE66A "
        "8.1 and 8.3, printed page 8). S-120 bounds the bus VBUS20 at %.2f V and holds it at %.2f V in steady service "
        "(v2/docs/records/s120/vbus20_bound.out); the ringing on top of the bus is not bounded at desk, since no layout "
        "exists and no TI note giving a layout-independent bound is held. TI prefers 30 V FETs for a 19 to 20 V input "
        "(SLUSE66A 10.2.2.6, page 86) in the topology board A draws, the input loop running through R16 with only C190 10 nF "
        "and C191 1 nF after it (page 86; Figure 10-1, page 83); board A's band tops out %.2f V above TI's 20 V. Budget over "
        "the steady bus: %.2f V to the FETs' 30 V, %.2f V to SW1's recommended 26 V. A model for the layout writer "
        "(vbus20_bound.out section 10, not a bound): Q7's current falls in about %.1f ns, so at Option A(i)'s bound (L2 peak "
        "%.2f A) each nH of the loop C190 and C191, Q7, Q8 adds about %.1f V, 1 nH between the VBUS20 bank (C20 to C22), "
        "R16 and C190 lifts CH_ACN by about %.1f V (growing as the square root of the inductance), and the 30 V budget allows "
        "about %.2f nH of the first loop. Owner: board A's layout writer "
        "(S-115's pass) and the bench. Closed when a routed-board reading of both loops' inductance, or a prototype "
        "measurement of CH_SW1, CH_ACN and CH_SW2 at the charger's largest current, keeps each FET's VDS and U3's SW pins "
        "inside their absolute ratings, or when a snubber, a gate-drive change or FETs of a higher voltage are drawn and "
        "read back on the regenerated netlist."
        % (F["bound"], F["v_hi"], F["v_hi"] - 20.0, 30.0 - F["v_hi"], 26.0 - F["v_hi"], F["t_fi"] * 1e9, r["i"], r["vpn"],
           r["vacn"], r["l30"]))
    ev = (
        "Stream s120 (v2/docs/records/s120/README.md, vbus20_bound.py and its .out, merged at %s): the committed netlists "
        "of boards A (sha256/16 %s) and E (%s) parsed, %d of %d circuit facts holding, among them no clamp on VBUS20 and "
        "U3's OTG/VAP/FRS pin on GND, so the charger cannot drive the bus. The front end U2 (LM5176) regulates VBUS20 at "
        "%.2f to %.2f V (VREF 0.788 to 0.812 V, TI SNVSAI1D 6.5 page 6; R6 240k over R7 10k at 1 percent, 100 ppm/K over "
        "65 K INFERRED; IBIAS(FB) 25 nA). Its output over-voltage protection turns the gate drives off above VREF plus 10 "
        "percent, a typical figure only (6.5 page 8; 7.3.11 page 18), read on the same divider: %.2f V at VREF's maximum and "
        "the worst ratio, and %.2f V with L1's energy at the boost peak limit (140 mV over 5 mOhm, page 7) into the six bulk "
        "parts at -20 percent. That bound holds whatever the load, the line or the loop does while U2 is inside its ratings: "
        "a load dump when the charger stops at 8.0 A reads %.2f V on the front end's loop model and a line step to U2's 60 V "
        "%.2f V (both MODEL); the charger's own inductor returns to VBAT, not to the bus; an idle stage blocks VIN_RAW (Q2's "
        "body diode); board E delivers 9 to 36 V with the LM5069's lockout at %.1f to %.1f V and SMCJ40A class clamps at "
        "64.5 V (S-111 owns U2 against them). Margins at the bound: %.2f V to the FETs' 30 V (SLPS526 and SLPS516 page 1), "
        "%.2f V to the BQ25731's 32 V on VBUS, ACP, ACN, SW1 and SW2 and %.2f V to its recommended 26 V and to ACOV's 26.0 V "
        "minimum (SLUSE66A 8.1 and 8.3 page 8, 8.5 page 14); BTST1 at the bound plus REGN's 6.3 V sits %.2f V under 32 V. "
        "The pack side stays at or under %.1f V by SYSOVP (page 14) and %.2f V by D1 (SMCJ18A, INFERRED straight line) if the "
        "pack opens while charging, %.2f V under 30 V. No clamp or setting is added and the FETs' rating stands (decision "
        "57). The switch nodes' ringing is not bounded at desk and is carried by %s; the single faults that blind or bypass "
        "the protection (Q2 short, R6 open, FB short) are outside every requirement (ASM-001, SC-39), take U3 past its own "
        "32 V before the FETs, and are noted on S-111. AI desk work on the makers' figures, nothing built or measured."
        % (commit, F["sha_a"], F["sha_e"], F["facts"] - F["facts_bad"], F["facts"], F["v_lo"], F["v_hi"], F["ovp_hi"],
           F["bound"], F["dump"], F["line"], F["ov_lo"], F["ov_hi"], 30.0 - F["bound"], 32.0 - F["bound"],
           26.0 - F["bound"], 32.0 - F["bound"] - 6.3, F["sysovp"], F["d1_a2"], 30.0 - F["d1_a2"], ring_id))
    s111 = (
        " S-120's residual (stream s120, v2/docs/records/s120/vbus20_bound.out section 11): a U2 or Q2 failure, which a "
        "surge past U2's 60 V could cause, passes VIN_RAW onto VBUS20 less a body diode (about %.1f V at 36 V in and %.1f V "
        "at the lockout's maximum) or, with R6 open or FB shorted, lets the stage run the bus up with nothing on board A to "
        "stop it, since the LM5176's over-voltage protection reads the same FB pin; board A has no clamp on VBUS20, and "
        "U3's VBUS, ACP and ACN (32 V absolute, SLUSE66A page 8) are the first parts past their rating. Options to weigh: an "
        "independent over-voltage trip on VBUS20 (U34's channel 1 re-armed while the stage runs) for the FB faults, and an "
        "SMCJ22A on VBUS20 (22 V standoff over the %.2f V band), which holds a Q2 short at about 28 V at board E's 6.15 A "
        "hot-swap limit (INFERRED) until the LM5069's timer opens."
        % (36.0 - 0.8, F["ov_hi"] - 0.8, F["v_hi"]))
    return ring, ev, s111


def phase_close(commit, check, reg):
    evidence_gate(commit)
    F = rerun_bound()
    t = open(reg, encoding="utf-8").read()
    d = yaml.safe_load(t)
    if any(x["id"] == "S-120" for x in d["closed_items"]): refuse("S-120 is already closed (a second run)")
    if not any(x["id"] == "S-120" for x in d["open_items"]): refuse("S-120 is not an open item")
    if RING_MARK in t: refuse("the switch-node item is already in the registry (a second run)")
    if S111_MARK in t: refuse("S-111 already carries S-120's residual (a second run)")
    req = [r for r in d["records"] if r["id"] == "REQ-015"]
    if len(req) != 1 or "S-120" not in (req[0].get("waits_on") or []): refuse("REQ-015 does not wait on S-120")
    ring_id = next_s(d)
    ring, ev, s111 = texts(F, commit, ring_id)
    A.screen(ring, "the switch-node item's title"); A.screen(ev, "S-120's closing evidence"); A.screen(s111, "S-111's addition")
    # 1. S-111's title gains the residual (the title is the last field of its block)
    i, j = A.span(t, "S-111")
    blk = t[i:j]
    k = blk.index("    title: >-\n")
    old_title = " ".join(l.strip() for l in blk[k + len("    title: >-\n"):].split("\n") if l.strip())
    if old_title != [x for x in d["open_items"] if x["id"] == "S-111"][0]["title"]: refuse("S-111's title is not its last field")
    t2 = t[:i] + blk[:k] + "    title: >-\n" + A.fold(old_title + s111, 6, 120) + t[j:]
    # 2. S-120 leaves open_items; the switch-node item takes its place there
    i, j = A.span(t2, "S-120")
    blk = t2[i:j]
    tm = re.search(r"(?m)^    title: >-\n", blk)
    title120 = blk[tm.end():].rstrip("\n")
    new_blk = "  - id: %s\n    class: SESSION\n    status: OPEN\n    title: >-\n%s" % (ring_id, A.fold(ring, 6, 120))
    t2 = t2[:i] + new_blk + t2[j:]
    # 3. S-120 at the end of closed_items (before records:)
    k = t2.index("\nrecords:\n")
    closed = "  - id: S-120\n    closed_by: commit %s\n    closing_evidence: >-\n%s    title: >-\n%s\n" % (commit, A.fold(ev, 6, 120), title120)
    t2 = t2[:k + 1] + closed + t2[k + 1:]
    # 4. REQ-015 waits on the switch-node item in S-120's place (the line read from the parsed record)
    waits = req[0]["waits_on"]
    old_w = "    waits_on: [%s]\n" % ", ".join(waits)
    new_w = "    waits_on: [%s]\n" % ", ".join(ring_id if w == "S-120" else w for w in waits)
    ri, rj = A.span(t2, "REQ-015")
    rb = t2[ri:rj]
    if rb.count(old_w) != 1: refuse("REQ-015's waits_on line is not as parsed")
    t2 = t2[:ri] + rb.replace(old_w, new_w) + t2[rj:]
    if t2 == t: refuse("nothing changed")
    # the re-parse: only what is named moved
    after = yaml.safe_load(t2)
    bo, ao = {x["id"]: x for x in d["open_items"]}, {x["id"]: x for x in after["open_items"]}
    if set(ao) != (set(bo) - {"S-120"}) | {ring_id}: refuse("open items changed beyond S-120 and %s" % ring_id)
    for k2 in ao:
        if k2 == ring_id:
            if ao[k2] != {"id": ring_id, "class": "SESSION", "status": "OPEN", "title": ring}: refuse("%s does not read as written" % ring_id)
        elif k2 == "S-111":
            if {f for f in set(bo[k2]) | set(ao[k2]) if bo[k2].get(f) != ao[k2].get(f)} != {"title"}: refuse("S-111 moved beyond its title")
            if ao[k2]["title"] != bo[k2]["title"] + s111: refuse("S-111's title does not read as the old title plus the addition")
        elif bo[k2] != ao[k2]: refuse("open item %s moved" % k2)
    if [x["id"] for x in after["closed_items"]] != [x["id"] for x in d["closed_items"]] + ["S-120"]: refuse("closed items changed beyond S-120")
    c120 = after["closed_items"][-1]
    if c120.get("closed_by") != "commit %s" % commit or c120.get("closing_evidence") != ev: refuse("S-120's closure does not read as written")
    if c120.get("title") != bo["S-120"]["title"]: refuse("S-120's title moved")
    rb_, ra_ = {r["id"]: r for r in d["records"]}, {r["id"]: r for r in after["records"]}
    for k2 in rb_:
        diff = {f for f in set(rb_[k2]) | set(ra_[k2]) if rb_[k2].get(f) != ra_[k2].get(f)}
        if diff and not (k2 == "REQ-015" and diff == {"waits_on"}): refuse("%s moved in %s" % (k2, diff))
    if ra_["REQ-015"]["waits_on"] != [ring_id if w == "S-120" else w for w in waits]: refuse("REQ-015's waits_on does not read as written")
    for sec in d:
        if sec not in ("open_items", "closed_items", "records") and d[sec] != after[sec]: refuse("section %s changed" % sec)
    print("apply_registry_s120 close: S-120 closed by commit %s (bus bound %.2f V, %.2f V under 30 V); %s opened (the switch "
          "nodes' ringing budget, %.2f V over the steady bus), REQ-015 waits on %s; S-111's title carries S-120's residual"
          % (commit[:8], F["bound"], 30.0 - F["bound"], ring_id, 30.0 - F["v_hi"], ", ".join(ra_["REQ-015"]["waits_on"])))
    if check:
        print("CHECK ONLY: %s not written." % os.path.relpath(reg, TOP))
        return 0
    open(reg, "w", encoding="utf-8").write(t2)
    if yaml.safe_load(open(reg, encoding="utf-8").read()) != after: refuse("re-parse differs")
    print("APPLIED. Next: python3 v2/ecad/tools/rules_lib.py requirements, then rules_render.py --requirements")
    return 0


def main(argv):
    check = "--check" in argv
    reg = REG_DEFAULT
    args = [x for x in argv[1:] if x != "--check"]
    if "--registry" in args:
        k = args.index("--registry")
        if k + 1 >= len(args): refuse("--registry needs a path")
        reg = os.path.abspath(args[k + 1])
        args = args[:k] + args[k + 2:]
    if args[:1] == ["close"] and len(args) == 2: return phase_close(args[1], check, reg)
    refuse("usage: apply_registry_s120.py close <commit> [--check] [--registry PATH]")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
