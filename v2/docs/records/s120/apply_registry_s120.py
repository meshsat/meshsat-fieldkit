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
                   Then: S-120 moves to closed_items (closed by <commit> resolved to its full sha; its closing evidence
                   names the files, states the bound as INFERRED with its sensitivity, and every figure in it is read from
                   vbus20_bound.FIG here, never typed); a new SESSION item (the next free S number: S-124 on the line that
                   carries set 13) carries the switch nodes' ringing budget and the bench reading of the front end's OVP
                   trip, closes only on the prototype, and takes S-120's place in REQ-015's waits_on; S-111's title gains
                   S-120's residual (the single faults that blind or bypass the front end's protection). Nothing else
                   moves; the registry is re-parsed and compared.

Second issue (29 September 2026, the check of stream s120: B1 Q7 carries Q8's body diode, B2 the INFERRED label and the
OVP bench reading reach the registry, B3 the new item closes only on a measurement referred to both bus levels, m1 the
single-fault order held to the Q2 short, m2 SW2 and BTST1 stated as they are, m3 the full sha, m7 Q7's turn-on and U3's
VBUS pin, m8 the pages). Third issue (the re-check CHECK-2.md): B1 the new item's closing test and rating list carry SW1 and
SW2's -2 V and -4 V (25 ns) limits; n1 the Q2 short's order claimed only once ACOV has stopped the charger; n2 the bound
takes a first on-time of a period (23.40 V); n7 Q7's VDS read from CH_ACN to CH_SW1.

WHICH COMMIT: pass the tip of fnd/s120 or a merge that carries it. An earlier commit of this branch is refused, because the
evidence gate asks that README.md, LOG.md, vbus20_bound.py and vbus20_bound.out be byte for byte the same at <commit> and at
HEAD.

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
    """Refuse unless the records are committed and identical at <commit> and HEAD; return <commit>'s full sha (the
    check of stream s120, m3: closed_by carries the 40 characters every closed item carries)."""
    if not re.match(r"^[0-9a-f]{8,40}$", commit or ""): refuse("give the commit that carries this stream's records")
    if git("cat-file", "-e", commit + "^{commit}").returncode: refuse("%s is not in this history" % commit)
    full = git("rev-parse", commit + "^{commit}").stdout.decode().strip()
    if len(full) != 40: refuse("%s does not resolve to a full sha" % commit)
    for f in EVIDENCE:
        path = "%s/%s" % (REC, f)
        if git("ls-files", "--error-unmatch", path).returncode: refuse("%s is not committed" % path)
        if git("diff", "--quiet", "HEAD", "--", path).returncode: refuse("%s has an uncommitted change" % path)
        at_c = git("rev-parse", "%s:%s" % (commit, path))
        at_h = git("rev-parse", "HEAD:%s" % path)
        if at_c.returncode: refuse("%s is not carried by %s" % (path, commit[:8]))
        if at_c.stdout != at_h.stdout: refuse("%s at %s differs from HEAD's" % (path, commit[:8]))
    return full


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
    """The three registry texts, every figure read from vbus20_bound.FIG (third issue: the re-check CHECK-2.md, B1 the
    negative SW limits, n1 the Q2 short's order, n2 the first on-time, n7 the VDS reading). The bound is written INFERRED
    wherever it is stated, with its sensitivity."""
    r = F["ring_A2"]
    s29, s30 = F["sens29"] * 100, F["sens30"] * 100
    ring = (
        "(stream s120, S-120's switch nodes; the independent re-check of stream s117, minor n1, and the checks of stream "
        "s120) Board A's charger switch nodes against the 30 V FETs of decision 57 (Q7 CSD17578Q5A, Q8 to Q10 CSD17577Q5A; "
        "VDS 30 V absolute, TI SLPS526 and SLPS516 page 1) and the BQ25731's own pins (VBUS, ACP, ACN, SW1 and SW2 32 V "
        "absolute; SW1 and SW2 26 V recommended, and no lower than -2 V, or -4 V for at most 25 ns, below PGND; SLUSE66A "
        "8.1 and 8.3, printed page 8). S-120 holds the bus VBUS20 at %.2f V in steady service and bounds it at %.2f V, a "
        "bound INFERRED from the LM5176's output over-voltage threshold, which TI gives as a typical 10 percent over VREF "
        "only (SNVSAI1D 6.5 page 8), with L1's energy for a first on-time of a period as a MODEL term (%.2f V in the steady "
        "current-limit cycle): 30 V is reached only if the trip sits %.1f percent over VREF for Q7 or %.1f percent for Q8 "
        "(v2/docs/records/s120/vbus20_bound.out sections 3 and 8). Q7 holds the bus plus Q8's body diode in every dead time "
        "(VSD 1.0 V maximum, SLPS516 page 3), and SW1 then sits at minus that VSD. The ringing on top is not bounded at "
        "desk: no layout exists and no TI note giving a layout-independent bound is held. TI prefers 30 V FETs for a 19 to "
        "20 V input (SLUSE66A 10.2.2.6, page 86) in the topology board A draws, the input loop running through R16 with only "
        "C190 10 nF and C191 1 nF after it (page 86, Figure 10-3 page 85); board A's band tops out %.2f V above TI's 20 V, "
        "and board A as generated draws no capacitor from CH_ACN_F or CH_ACP_F to GND (Figure 10-3's CACP and CACN, 33 nF), "
        "so U3's ACN pin sees CH_ACN's ring through R146 and C121 alone. Budget over the steady bus: %.2f V for Q7, %.2f V "
        "for Q8, %.2f V to SW1's recommended 26 V, and %.1f V from SW1's minus VSD to U3's -4 V; over the bound %.2f V for "
        "Q7 and %.2f V for Q8. A model for the layout writer (vbus20_bound.out section 10, not a bound, typical driver "
        "figures): Q7's turn-off current falls in about %.1f ns, so at Option A(i)'s bound (L2 peak %.2f A) each nH of the "
        "loop C190 and C191, Q7, Q8 adds about %.1f V to Q7, whose budget allows about %.2f nH, and each nH between Q8's "
        "source and U3's PGND takes SW1 as much further below minus VSD, which the -4 V limit allows for about %.2f nH, the "
        "tightest figure of the model; Q7's turn-on rises in about %.1f ns from the valley current into Q8's reverse "
        "recovery, whose charge TI states only at 300 A/us. Owner: board A's layout writer (S-115's pass, where a "
        "routed-board reading of the loops' inductance is recorded as the layout step and does not close this item) and "
        "the bench. Closed only on the prototype: CH_SW1, CH_ACN, CH_SW2 and U3's VBUS pin read against U3's PGND at the "
        "charger's largest current; Q7's VDS taken from CH_ACN to CH_SW1 (CH_ACN's peak less CH_SW1's lowest, which already "
        "holds Q8's body diode) and Q8's from CH_SW1's peak; each overshoot over the measured bus added to %.2f V for "
        "steady service and to %.2f V for the over-voltage excursion; each FET's VDS then inside 30 V, U3's VBUS, ACP, ACN, "
        "SW1 and SW2 inside 32 V, and CH_SW1 and CH_SW2 no lower than -2 V, or -4 V for at most 25 ns (SLUSE66A page 8); "
        "and the front end's OVP trip read on the prototype (FB driven through R6 and R7), which replaces the INFERRED "
        "%.2f V and with it the %.2f V reference. A snubber, a gate-drive change or FETs of a higher voltage, drawn and "
        "read back on the regenerated netlist, are measured the same way."
        % (F["v_hi"], F["bound"], F["v_steady"], s29, s30, F["v_hi"] - 20.0, F["b_q7"][0], F["b_q8"][0], F["b_sw1r"][0],
           F["b_swneg"][0], F["b_q7"][1], F["b_q8"][1], F["t_fi"] * 1e9, r["i"], r["vpn"], r["l30"], r["lneg"],
           F["t_ri"] * 1e9, F["v_hi"], F["bound"], F["ovp_hi"], F["bound"]))
    ev = (
        "Stream s120 (v2/docs/records/s120/README.md, vbus20_bound.py and its .out, merged at %s; third issue after the "
        "checks of stream s120): the committed netlists of boards A (sha256/16 %s) and E (%s) parsed, %d of %d circuit "
        "facts holding, among them VBUS20's whole membership (39 pins, no clamp) and U3's OTG/VAP/FRS pin on GND, so the "
        "charger cannot drive the bus. The front end U2 (LM5176) regulates VBUS20 at %.2f to %.2f V (VREF 0.788 to 0.812 V, "
        "TI SNVSAI1D 6.5 page 6; R6 240k over R7 10k at 1 percent, 100 ppm/K over 65 K INFERRED; IBIAS(FB) 25 nA). Its "
        "output over-voltage protection turns the gate drives off above VREF plus 10 percent, a TYPICAL figure with no "
        "limits (6.5 page 8; 7.3.11 page 18), read on the same divider, so the bound is INFERRED: %.2f V at VREF's maximum "
        "and the worst ratio; %.2f V with L1's energy in the steady current-limit cycle (buck mode at 60 V, %.2f A, page "
        "7); %.2f V with the energy of a first on-time of a period after a valley crossing, the buck high side being turned "
        "off only by the clock (7.3.1 page 14, 7.3.5 page 16; %.2f A, a MODEL term), which is the bound. 30 V is reached "
        "only if the trip sits %.1f percent over VREF for Q7 or %.1f percent for Q8, against the typical 10; the bench "
        "reading of the trip is carried by %s. The bound holds whatever the load, the line or the loop does while U2 is "
        "inside its ratings: a load dump when the charger stops at 8.0 A reads %.2f V on the front end's loop model and a "
        "line step to U2's 60 V %.2f V (both MODEL); the charger's own inductor returns to VBAT, not to the bus; an idle "
        "stage blocks VIN_RAW (Q2's body diode); board E delivers 9 to 36 V with the LM5069's lockout at %.1f to %.1f V and "
        "SMCJ40A class clamps at 64.5 V (S-111 owns U2 against them). Margins at the INFERRED bound, before ringing: Q8 "
        "%.2f V and Q7 %.2f V to their 30 V (SLPS526 and SLPS516 page 1; Q7 carries Q8's body diode, VSD 1.0 V maximum, "
        "SLPS516 page 3); %.2f V to the BQ25731's absolute 32 V on VBUS, ACP, ACN and SW1, and %.2f V to its recommended "
        "26 V and to ACOV's 26.0 V minimum (SLUSE66A 8.1 and 8.3 page 8, 8.5 page 14); BTST1 at the bound plus REGN's 6.3 V "
        "sits %.2f V under its recommended 32 V and %.2f V under its absolute 38 V. The pack side, SW2 with it, stays at or "
        "under %.1f V by SYSOVP (page 14) and %.2f V by D1 (SMCJ18A, INFERRED straight line) if the pack opens while "
        "charging: Q9 and Q10 %.2f V under 30 V, SW2 %.2f V under 32 V. No clamp or setting is added and the FETs' rating "
        "stands (decision 57). The switch nodes' ringing and SW1's undershoot against U3's -2 V and -4 V (25 ns) are not "
        "bounded at desk and are carried by %s, which closes only on the prototype. The single faults that blind or bypass "
        "the protection are outside every requirement (ASM-001, SC-39) and noted on S-111: for a Q2 short no order is "
        "claimed while the charger still switches through ACOV's deglitch (Q7 at 28.7 V or more before ringing), and once "
        "ACOV has stopped it U3 passes its own 32 V before Q7 reaches 30 V while the pack is above about 1.2 V; for R6 open "
        "or FB shorted no order is claimed. AI desk work on the makers' figures, nothing built or measured."
        % (commit, F["sha_a"], F["sha_e"], F["facts"] - F["facts_bad"], F["facts"], F["v_lo"], F["v_hi"], F["ovp_hi"],
           F["v_steady"], F["i_l1_max"], F["v_first"], F["i_first"], s29, s30, ring_id, F["dump"], F["line"], F["ov_lo"],
           F["ov_hi"], F["q8_m"][2], F["q7_m"][2], F["vbus_abs_m"][2], F["rec26_m"][2], F["btst_rec_m"][2],
           F["btst_abs_m"][2], F["sysovp"], F["d1_a2"], F["q9_d1"], F["sw2_abs_d1"], ring_id))
    s111 = (
        " S-120's residual (stream s120, v2/docs/records/s120/vbus20_bound.out section 11): a U2 or Q2 failure, which a "
        "surge past U2's 60 V could cause, passes VIN_RAW onto VBUS20 less a body diode's drop (%.1f V at 36 V in and %.1f V "
        "at the lockout's maximum, the drop INFERRED). On the way the bus passes the charger's ACOV (26.0 to 27.7 V, 100 us "
        "deglitch, SLUSE66A page 14) while the charger still switches, and Q7 then holds the bus plus Q8's body diode, 28.7 "
        "V or more before any ringing, so no order is claimed for that phase; once ACOV has stopped the charger, U3's VBUS, "
        "ACP and ACN (32 V absolute, page 8) pass their rating before Q7 reaches 30 V while the pack is above about 1.2 V, "
        "since Q10's body diode then holds SW1 near VBAT. With R6 open or FB shorted the stage runs the bus up with nothing "
        "on board A to stop it, since the LM5176's over-voltage protection reads the same FB pin, and the same switching "
        "phase leaves the FETs possibly first. Board A has no clamp on VBUS20. Options to weigh: an independent over-voltage "
        "trip on VBUS20 (U34's channel 1 re-armed while the stage runs) for the FB faults, and an SMCJ22A on VBUS20 (22 V "
        "standoff over the %.2f V band), which holds a Q2 short at about 28 V at board E's 6.15 A hot-swap limit (INFERRED) "
        "until the LM5069's timer opens."
        % (36.0 - 0.8, F["ov_hi"] - 0.8, F["v_hi"]))
    return ring, ev, s111


def phase_close(commit, check, reg):
    commit = evidence_gate(commit)
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
    print("apply_registry_s120 close: S-120 closed by commit %s (bus bound %.2f V INFERRED; at it Q8 %.2f V and Q7 %.2f V "
          "under 30 V); %s opened (the switch nodes, closed only on the prototype; budget over the steady bus %.2f V for Q7, "
          "%.2f V for Q8, %.1f V from SW1's minus VSD to -4 V), REQ-015 waits on %s; S-111's title carries S-120's residual"
          % (commit, F["bound"], F["q8_m"][2], F["q7_m"][2], ring_id, F["b_q7"][0], F["b_q8"][0], F["b_swneg"][0],
             ", ".join(ra_["REQ-015"]["waits_on"])))
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
