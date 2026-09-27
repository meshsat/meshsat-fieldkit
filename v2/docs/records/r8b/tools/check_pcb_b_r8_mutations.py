#!/usr/bin/env python3
"""Mutation controls for drafts/b/check_pcb_b-r8.patch (MESHSAT-1357 round 8, board B author, 26 September 2026).
Runs the patched gate's NET section (check_pcb_b_emul.py, round 4's emulator: the gate's own statements, ast-extracted)
on the round-8 netlist, then on thirteen mutated copies of its maps, and requires each mutation to add at least one FAIL
naming its subject. Usage: check_pcb_b_r8_mutations.py <patched check_pcb_b.py> <round-8 netlist>"""
import copy, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_pcb_b_emul as E

def run(code, bynet, bypad, byval):
    res = []
    exec(code, {"bynet": bynet, "bypad": bypad, "byval": byval, "check": lambda c, m: res.append((bool(c), m)), "sorted": sorted})
    return [m for c, m in res if not c], len(res)

def move(bynet, bypad, ref, pin, frm, to):
    bypad[frm].discard((ref, pin)); bypad.setdefault(to, set()).add((ref, pin))
    if not any(r == ref for r, _ in bypad[frm]): bynet[frm].discard(ref)
    bynet.setdefault(to, set()).add(ref)

def main(gate, net):
    code, a, b = E.net_section(open(gate).read()); code = compile(code, gate, "exec")
    bynet, bypad = E.netlist_maps(net); byval = E.netlist_values(net)
    base, n = run(code, bynet, bypad, byval)
    print("baseline: %d checks, %d FAIL" % (n, len(base)))
    muts = []
    def m_r500(bn, bp, bv): bv["R500"] = "100k"                                            # FAB-04: a value left at 100 k
    muts.append(("R500 back to 100k", "WSEC_C", m_r500))
    def m_r498(bn, bp, bv):                                                                # FAB-04: the pull-down renamed
        for net_ in list(bp):
            if ("R498", "1") in bp[net_] or ("R498", "2") in bp[net_]:
                for pn in ("1", "2"):
                    if ("R498", pn) in bp[net_]: bp[net_].discard(("R498", pn)); bp[net_].add(("R598", pn))
                bn[net_].discard("R498"); bn[net_].add("R598")
        bv["R598"] = bv.pop("R498")
    muts.append(("R498 renamed R598", "WSEC_A", m_r498))
    def m_r15(bn, bp, bv): bv["R15"] = "100k"
    muts.append(("R15 back to 100k", "HDMI_SEL1", m_r15))
    def m_test2(bn, bp, bv): move(bn, bp, "U101", "16", "S1_TEST2", "S1_TESTL")             # FAB-01: TEST2 pulled low again
    muts.append(("U101 TEST2 on S1_TESTL", "U101 TEST2", m_test2))
    def m_tck(bn, bp, bv): move(bn, bp, "U201", "89", "unconnected-(U201-TCK-Pad89)", "S2_JTAGL")   # FAB-01: TCK strapped
    muts.append(("U201 TCK on S2_JTAGL", "U201 TCK", m_tck))
    def m_pc5(bn, bp, bv): move(bn, bp, "U51", "33", "EMCON_SUP", "EMCON_HW")               # L1: a firmware pin back on the line
    muts.append(("U51 PC5 on EMCON_HW", "EMCON_HW", m_pc5))
    def m_dev(bn, bp, bv): move(bn, bp, "U212", "5", "+3V3_CM2", "+3V3_DEV")                # L3: slot 2's inverter on the shared rail
    muts.append(("U212 VCC on +3V3_DEV", "EMCON_ON2", m_dev))
    def m_wd(bn, bp, bv): move(bn, bp, "U315", "6", "WIFI2_W_DIS_n", "unconnected-mut")     # L7: W_DISABLE1# left without its driver
    muts.append(("U315 1Y off W_DISABLE1#", "WIFI2_W_DIS_n", m_wd))
    # round 8, second pass (FAB-03, FAB-02): the break-before-make structure
    def m_armmov(bn, bp, bv): move(bn, bp, "U84", "2", "BBM1_ARM", "BBM1_MOV")           # ARM's OR gate shared with MOV
    muts.append(("U84.2 ARM -> MOV", "bank 1 motion", m_armmov))
    def m_nolock(bn, bp, bv): move(bn, bp, "R474", "1", "BSEL1_H", "BSEL1")               # main's wiring: the delay from the vote
    muts.append(("R474 driven by the vote", "bank 1 select", m_nolock))
    def m_movlock(bn, bp, bv): move(bn, bp, "U527", "6", "BBM1_MOV", "GND")               # the second half of the lock defeated
    muts.append(("U527 select tied low", "bank 1 select", m_movlock))
    def m_oesel(bn, bp, bv): move(bn, bp, "U516", "6", "BBM1", "PGSEL1_n")                # the enable mux selected by the power-good
    muts.append(("U516 select on PGSEL1_n", "bank 1 enable", m_oesel))
    def m_pg(bn, bp, bv): move(bn, bp, "U519", "3", "PG1_S", "PG1")                       # the slow node into a 74LVC1G157
    muts.append(("U519 I0 on PG1", "PG1 (FAB-02)", m_pg))
    bad = 0
    for name, subj, f in muts:
        bn, bp, bv = copy.deepcopy(bynet), copy.deepcopy(bypad), dict(byval)
        f(bn, bp, bv)
        fails, _n = run(code, bn, bp, bv)
        new = [m for m in fails if m not in base]
        hit = [m for m in new if subj in m]
        print("%-28s %s  (%d new FAIL: %s)" % (name, "CAUGHT" if hit else "MISSED", len(new), (hit or new or ["-"])[0][:120]))
        bad += 0 if hit else 1
    return 1 if (bad or base) else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
