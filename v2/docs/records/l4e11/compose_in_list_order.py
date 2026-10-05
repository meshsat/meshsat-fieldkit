#!/usr/bin/env python3
"""compose_in_list_order.py: board A composed in L4-E9's change-list order as the candidate lists it (task L4-E11, MESHSAT-1357, round 12,
4 October 2026; the independent check V2's V2-m9).

Usage:  compose_in_list_order.py TREE WORK

TREE is a tree that holds every draft the list names: the candidate's files (fnd/v2cand at dfa1eef2, where record l8r2's packrtn, slotlm
and fb01 are), a checkout or an extraction of `git archive`, with this record's drafts and check laid over them. This branch's own tree
does not hold those three drafts, so its tests compose main's order; this script shows the list's order where the drafts are.
WORK is an empty scratch directory: the only place written. Nothing in TREE is changed.

The order (L4-E9's L4-POWER-ARCHITECTURE.md section 3, rows 24 to 33 for 3g and 3h): r12, guard, charger, r11, bank, r138, u17, gnd002,
hotr1, packrtn, slotlm, fb01, record l8p's ptc, this record's dd7, d8dec31's mainpb, l6r2's lcsc. Each draft is applied to a scratch copy
of TREE's gen_sch_a.py; the composed generator is run to its end by record l8p's gen_netlist.py; check_dd7_netlist.py reads the netlist;
then three mutations (R256 at 6.8k, a battery FET reversed, R84 without its pulse rating) must each read FAIL.
Record l6r2's draft asks git for the tree's top: where TREE is not a checkout, set L4E11_GIT_DIR to a repository's git directory (read
only: `git rev-parse --show-toplevel` with GIT_WORK_TREE set to TREE).
Exit 0: every draft applied, the generator ran, the netlist reads DRAWN and each mutation reads FAIL; 1 otherwise."""
import os
import shutil
import subprocess
import sys

ORDER = [("l4e6", "r12"), ("l4e11", "guard"), ("l4e11", "charger"), ("l4e4", "r11"), ("l4e8", "bank"), ("l4e4", "r138"), ("l4e9", "u17"),
         ("l8gnd", "gnd002"), ("l8gnd", "hotr1"), ("l8r2", "packrtn"), ("l8r2", "slotlm"), ("l8r2", "fb01"), ("l8p", "ptc"), ("l4e11", "dd7"),
         ("d8dec31", "mainpb"), ("l6r2", "lcsc")]
MUTATIONS = [("R256 at 6.8k", 'r("R256", "4.7k 1%", "CELL+", "DD7_BL", fp="RS")', 'r("R256", "6.8k 1%", "CELL+", "DD7_BL", fp="RS")'),
             ("a battery FET reversed", '"CH_BATDRV", "CH_BATQ", "VBAT", fp="LFPAK56"', '"CH_BATDRV", "VBAT", "CH_BATQ", fp="LFPAK56"'),
             ("R84 without its pulse rating", 'r("R84", "56R 1% pulse-rated", "DD7_K"', 'r("R84", "56R 1%", "DD7_K"')]


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0].strip() + "\n")
        return 2
    tree, work = os.path.abspath(argv[0]), os.path.abspath(argv[1])
    if not os.path.isdir(work) or os.listdir(work):
        sys.stderr.write("WORK must be an empty directory\n")
        return 2
    rec = os.path.join(tree, "v2", "docs", "records")
    net = os.path.join(tree, "v2", "ecad", "pcb-a-power-a23", "out", "pcb-a-power.net")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    if os.environ.get("L4E11_GIT_DIR"):
        env.update(GIT_DIR=os.environ["L4E11_GIT_DIR"], GIT_WORK_TREE=tree)
    run = lambda a: subprocess.run([sys.executable, "-B"] + a, capture_output=True, env=env)
    g = os.path.join(work, "gen_sch_a.py")
    shutil.copy(os.path.join(tree, "v2", "ecad", "tools", "gen_sch_a.py"), g)
    for r_, name in ORDER:
        s = os.path.join(rec, r_, "apply_gen_sch_a_%s.py" % name)
        if not os.path.isfile(s):
            print("%s/%s is not in this tree: the list's order cannot be shown here" % (r_, name))
            return 1
        r = run([s, g, net] if r_ == "d8dec31" else [s, g, "--write"])
        print("%-8s %-9s exit %d" % (r_, name, r.returncode))
        if r.returncode != 0:
            print(r.stderr.decode("utf-8", "replace")[-300:])
            return 1
    gen, chk = os.path.join(rec, "l8p", "gen_netlist.py"), os.path.join(rec, "l4e11", "check_dd7_netlist.py")

    def read(gp, tag):
        out = os.path.join(work, "a-%s.net" % tag)
        r = run([gen, gp, out, "pcb-a-power"])
        if r.returncode != 0:
            return r.returncode, None, (r.stdout + r.stderr).decode("utf-8", "replace")[-300:]
        c = run([chk, out])
        return 0, c.returncode, (r.stdout.decode().strip().splitlines() or [""])[-1].split(" ->")[0] + "; " + (c.stdout.decode().strip().splitlines() or [""])[-1]
    rc, cc, line = read(g, "drawn")
    print("the list's order: generator exit %d; %s" % (rc, line))
    ok = rc == 0 and cc == 0
    text = open(g, encoding="utf-8").read()
    for k, (why, old, rep) in enumerate(MUTATIONS):
        if text.count(old) != 1:
            print("mutation %s: its text is not in the composed generator once" % why)
            ok = False
            continue
        gm = os.path.join(work, "gen_sch_a_m%d.py" % k)
        open(gm, "w", encoding="utf-8").write(text.replace(old, rep))
        rc, cc, line = read(gm, "m%d" % k)
        print("mutation %s: generator exit %d; %s" % (why, rc, line))
        ok = ok and rc == 0 and cc == 4
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
