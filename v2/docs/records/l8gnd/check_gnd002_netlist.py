#!/usr/bin/env python3
"""check_gnd002_netlist.py: what GND-002's tool reads on a board's netlist (Layer 8 record l8gnd, MESHSAT-1357, 3 October 2026).

Rule GND-002 (pcb_rules.yaml) has implementation_location NONE_YET and verification MANUAL_REVIEW; its acceptance is a written
chassis-bond statement, which v2/docs/GROUNDING-AND-SHIELDS.md gives. This script is the netlist-level half of that check: it
PARSES a KiCad netlist (an s-expression reader, never a grep) and judges, board by board, whether the strategy's four board changes
are drawn and drawn once:

  A  net CHASSIS exists; its pins are exactly H1 pin 1 and R229 pin 1; R229's other pin is GND and its value begins "0R"; H1's
     footprint is meshsat:ChassisLug_M4_CHASSIS; and NO OTHER part has pins on both CHASSIS and GND (point 4: one bond).
  B  net CHASSIS exists; its pins are exactly C33's cold end and J_ETH pin SH; C33's other pin is BOB, and R9 and R10 each join
     a line-side centre tap (MCT3, MCT4) to BOB (DS00004151A p.10); and NO part has pins on both CHASSIS and GND (no bond on B).
  C  the eight H pads are on GND (the face-plate bond as built, point 2) and there is no chassis, shield or earth net.
  E  there is no chassis, shield or earth net (point 6: the pack has no enclosure and nothing of the case metal touches its return).
  D, P  informational: no chassis net is expected on them.

A board whose netlist has no CHASSIS net where one is expected reads NOT DRAWN; one that has it but not as the strategy says reads
FAIL (drawn wrong); one that has it as the strategy says reads DRAWN. The kit reads DRAWN only when A and B read DRAWN and C and
E hold. Nothing here has been built or measured: the statements are about netlists.

Usage:  check_gnd002_netlist.py [--repo DIR] [LETTER=path.net ...]
Without arguments it reads the committed netlists under v2/ecad/pcb-*/out/ of the repository that holds this script. It prints
each netlist with its sha256 (so a record output that includes these lines is pinned to the files it judged) and exits 0 when
the kit reads DRAWN, 4 when any board reads NOT DRAWN or FAIL, 2 on a usage error."""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
CHASSIS_LIKE = re.compile(r"CHASSIS|SHIELD|EARTH|PE\b", re.I)
EXPECT = {"a": "a chassis bond", "b": "a chassis net", "c": "no chassis net", "d": "no chassis net", "e": "no chassis net", "p": "no chassis net"}


def sexp(text):
    """A KiCad s-expression as nested lists of atoms (strings unquoted). Parsed, never grepped."""
    tok = re.compile(r'\(|\)|"((?:[^"\\]|\\.)*)"|([^\s()"]+)')
    stack, cur = [], []
    for m in tok.finditer(text):
        t = m.group(0)
        if t == "(":
            stack.append(cur); cur = []
        elif t == ")":
            done = cur; cur = stack.pop() if stack else []; cur.append(done)
        elif m.group(1) is not None:
            cur.append(m.group(1).replace('\\"', '"'))
        else:
            cur.append(m.group(2))
    return cur


def kv(node, key):
    for x in node[1:] if isinstance(node, list) else []:
        if isinstance(x, list) and x and x[0] == key:
            return x
    return None


def read_netlist(raw):
    """{"footprint": {ref: fpid}, "value": {ref: value}, "nets": {net: {(ref, pin), ...}}} of a KiCad netlist's bytes; every net is
    read, the last one included (a parse has no look-ahead to defeat)."""
    tree = sexp(raw.decode("utf-8", "replace"))
    root = tree[0] if tree and isinstance(tree[0], list) else tree
    fps, vals, nets = {}, {}, {}
    for sec in (root[1:] if isinstance(root, list) else []):
        if not (isinstance(sec, list) and sec):
            continue
        if sec[0] == "components":
            for c in sec[1:]:
                if not (isinstance(c, list) and c and c[0] == "comp"):
                    continue
                ref, fp, val = kv(c, "ref"), kv(c, "footprint"), kv(c, "value")
                if ref and len(ref) > 1:
                    fps[ref[1]] = fp[1] if fp and len(fp) > 1 else ""
                    vals[ref[1]] = val[1] if val and len(val) > 1 else ""
        elif sec[0] == "nets":
            for n in sec[1:]:
                if not (isinstance(n, list) and n and n[0] == "net"):
                    continue
                name = str((kv(n, "name") or [None, ""])[1]).lstrip("/")
                s = nets.setdefault(name, set())
                for x in n[1:]:
                    if isinstance(x, list) and x and x[0] == "node":
                        r, p = kv(x, "ref"), kv(x, "pin")
                        if r and p and len(r) > 1 and len(p) > 1:
                            s.add((r[1], p[1]))
    return {"footprint": fps, "value": vals, "nets": nets}


def pins_of(nl, ref):
    return {p: n for n, nodes in nl["nets"].items() for r, p in nodes if r == ref}


def bridges(nl, a, b):
    """Parts with a pin on net a and a pin on net b."""
    ra = {r for r, _p in nl["nets"].get(a, set())}
    rb = {r for r, _p in nl["nets"].get(b, set())}
    return sorted(ra & rb)


def judge(letter, nl):
    """-> (verdict, [lines]). verdict in DRAWN, NOT DRAWN, FAIL, HOLDS (for the boards that must carry no chassis net)."""
    L = []
    nets = nl["nets"]
    like = sorted(n for n in nets if CHASSIS_LIKE.search(n))
    letter = letter.lower()
    if letter == "a":
        if "CHASSIS" not in nets:
            L.append("A: no net CHASSIS: the plate's strap has nowhere to land and the one bond is not drawn (changes 1 and 4)")
            return "NOT DRAWN", L
        ok = True
        want = {("H1", "1"), ("R229", "1")}
        got = nets["CHASSIS"]
        if got != want:
            ok = False; L.append("A: CHASSIS carries %s, the strategy asks exactly H1.1 and R229.1" % sorted(got))
        r229 = pins_of(nl, "R229")
        if r229.get("2") != "GND":
            ok = False; L.append("A: R229's other pin is on %r, not GND" % r229.get("2"))
        if not nl["value"].get("R229", "").startswith("0R"):
            ok = False; L.append("A: R229's value %r does not begin with 0R (the bond is a link)" % nl["value"].get("R229"))
        if nl["footprint"].get("H1") != "meshsat:ChassisLug_M4_CHASSIS":
            ok = False; L.append("A: H1's land is %r, not meshsat:ChassisLug_M4_CHASSIS" % nl["footprint"].get("H1"))
        br = bridges(nl, "CHASSIS", "GND")
        if br != ["R229"]:
            ok = False; L.append("A: the parts bridging CHASSIS and GND are %s; the strategy asks R229 alone (one bond)" % br)
        if ok:
            L.append("A: CHASSIS on H1.1 (meshsat:ChassisLug_M4_CHASSIS) and R229.1; R229 %s to GND is the one bridge; changes 1 and 4 DRAWN" % nl["value"]["R229"])
        return ("DRAWN" if ok else "FAIL"), L
    if letter == "b":
        if "CHASSIS" not in nets:
            where = [n for n in ("GND",) if ("C33", "2") in nets.get(n, set())]
            L.append("B: no net CHASSIS: C33 returns to %s and J_ETH SH sits on %s (changes 2 and 3 not drawn)"
                     % (where[0] if where else pins_of(nl, "C33").get("2"), pins_of(nl, "J_ETH").get("SH")))
            return "NOT DRAWN", L
        ok = True
        c33 = pins_of(nl, "C33")
        cold = [p for p, n in c33.items() if n == "CHASSIS"]
        if len(cold) != 1 or set(c33.values()) != {"BOB", "CHASSIS"}:
            ok = False; L.append("B: C33 sits on %s, the clause asks BOB to CHASSIS" % sorted(c33.values()))
        want = {("C33", cold[0]) if cold else ("C33", "?"), ("J_ETH", "SH")}
        if nets["CHASSIS"] != want:
            ok = False; L.append("B: CHASSIS carries %s, the strategy asks exactly C33's cold end and J_ETH.SH" % sorted(nets["CHASSIS"]))
        for r, tap in (("R9", "MCT3"), ("R10", "MCT4")):
            pr = set(pins_of(nl, r).values())
            if pr != {tap, "BOB"}:
                ok = False; L.append("B: %s sits on %s, the clause asks %s to BOB through 75 Ohm" % (r, sorted(pr), tap))
        br = bridges(nl, "CHASSIS", "GND")
        if br:
            ok = False; L.append("B: %s bridge CHASSIS and GND; the strategy puts the kit's one bond on board A" % br)
        if ok:
            L.append("B: CHASSIS on C33.%s (%s) and J_ETH.SH; no part bridges it to GND; changes 2 and 3 DRAWN" % (cold[0], nl["value"].get("C33")))
        return ("DRAWN" if ok else "FAIL"), L
    if letter == "c":
        gnd = nets.get("GND", set())
        hs = [("H%d" % i, "1") for i in range(1, 9)]
        missing = [h for h in hs if h not in gnd]
        ok = not missing and not like
        if missing:
            L.append("C: face-plate rings not on GND: %s" % missing)
        if like:
            L.append("C: carries a chassis-like net %s where the plate bonds to GND directly (point 2)" % like)
        if ok:
            L.append("C: H1 to H8 on GND (the face-plate bond as built, point 2); no chassis net")
        return ("HOLDS" if ok else "FAIL"), L
    # D, E, P: nothing of the case metal may touch them (E: point 6)
    if like:
        L.append("%s: carries a chassis-like net %s; the strategy draws none here" % (letter.upper(), like))
        return "FAIL", L
    L.append("%s: no chassis, shield or earth net (%s)" % (letter.upper(), "point 6, the pack's return enters only on the dock block's return pins" if letter == "e" else "none expected"))
    return "HOLDS", L


def committed(repo):
    out = {}
    for p in sorted(glob.glob(os.path.join(repo, "v2", "ecad", "pcb-*", "out", "*.net"))):
        m = re.match(r"pcb-([a-z])\d?-", os.path.basename(os.path.dirname(os.path.dirname(p))))
        if m and m.group(1) in EXPECT and not os.path.basename(p).startswith("pcb-e5"):
            out[m.group(1)] = p
    return out


def run(paths, repo=REPO, out=sys.stdout):
    verdicts = {}
    for letter in sorted(paths):
        p = paths[letter]
        raw = open(p, "rb").read()
        rel = os.path.relpath(p, repo) if os.path.commonpath([os.path.abspath(p), repo]) == repo else p
        out.write("%s sha256 %s\n" % (rel, hashlib.sha256(raw).hexdigest()[:16]))
        v, lines = judge(letter, read_netlist(raw))
        verdicts[letter] = v
        for l in lines:
            out.write("  %s\n" % l)
        out.write("  board %s: %s\n" % (letter.upper(), v))
    kit = "DRAWN" if all(verdicts.get(k) == "DRAWN" for k in ("a", "b")) and all(verdicts.get(k, "HOLDS") == "HOLDS" for k in ("c", "d", "e", "p")) else "NOT DRAWN"
    if any(v == "FAIL" for v in verdicts.values()):
        kit = "FAIL"
    out.write("GND-002 on the kit: %s (A %s, B %s, C %s, E %s)\n" % (kit, verdicts.get("a", "no netlist"), verdicts.get("b", "no netlist"),
                                                                    verdicts.get("c", "no netlist"), verdicts.get("e", "no netlist")))
    return kit, verdicts


def main(argv):
    repo = REPO
    paths = {}
    args = list(argv)
    while args:
        a = args.pop(0)
        if a == "--repo":
            if not args:
                sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n"); return 2
            repo = os.path.abspath(args.pop(0))
        elif "=" in a and a[0].lower() in EXPECT and a[1] == "=":
            paths[a[0].lower()] = a[2:]
        else:
            sys.stderr.write(__doc__.split("Usage:")[1].split("\n")[0] + "\n"); return 2
    if not paths:
        paths = committed(repo)
    kit, _v = run(paths, repo)
    return 0 if kit == "DRAWN" else 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
