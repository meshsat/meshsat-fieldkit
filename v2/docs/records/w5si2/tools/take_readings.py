#!/usr/bin/env python3
"""SI-001 taken on the six boards of a tree INTO A SCRATCH DIRECTORY, and listed (stream w5si2, 28 September 2026,
MESHSAT-1357). It runs the tree's own tools/edge_length.py in memory on each board's declared-phase netlist and
writes the verdict and the table under <out>/<project>/, never under the tree. It prints the counts, the state of the
models the reading was taken in, the undecided nets by the kind of their reason, and with --nets <letter> every net
of that board that is not decided by a published figure: what decides it, the record and the documents behind it.

Usage: take_readings.py <tree> <out directory> <label> [--nets <letter> ...]
"""
import os, sys, json, collections


def main(a):
    tree, out, label = os.path.abspath(a[0]), os.path.abspath(a[1]), a[2]
    assert not out.startswith(tree + os.sep), "the readings go outside the tree"
    tools = os.path.join(tree, "v2", "ecad", "tools")
    sys.path.insert(0, tools)
    import edge_length as E, phase_artefacts as PA
    assert os.path.abspath(E.REPO) == tree, (E.REPO, tree)
    want = set()
    if "--nets" in a:
        for x in a[a.index("--nets") + 1:]:
            if x.startswith("--"): break
            want.add(x)
    rates = E.RATES
    recs = {r["id"]: r for sect in E.SECTIONS for r in rates[sect]}
    print("SI-001 AT THE SCHEMATIC PHASE, taken in scratch outside any tree: %s" % label)
    print("Prototype design work: nothing has been built or measured. tools/pcb_edge_rates.yaml sha256/16 %s." % rates.get("sha16"))
    print()
    print("board | netlist sha256/16 | signal | slow | non-slow | by a published figure | by a bound | undecided "
          "(no declaration + model absent + other) | answered | layout-bound (figure-held + BOUND_DECIDES) | models: state, asked, absent | verdict")
    tot = collections.Counter()
    res = {}
    for L in "abcdep":
        net = PA.netlist(L)
        if not (net and os.path.exists(net)): print("%s | no netlist" % L.upper()); continue
        r = E.schematic_table(net, L)
        od = os.path.join(out, os.path.splitext(os.path.basename(net))[0])
        os.makedirs(od, exist_ok=True)
        E.write_schematic_verdict(r, out_dir=od, quiet=True)
        v = json.load(open(os.path.join(od, "edge_length.verdict.json")))
        c, ms = r["counts"], r["inputs"]["model_state"]
        assert c["signal_nets"] == c["low_speed_nets"] + c["decided_nets"] + c["undecided_nets"] + c["contradicted_nets"], c
        assert c["decided_nets"] == c["maker_edge_nets"] + c["bound_edge_nets"], c
        assert c["undecided_nets"] == c["undecided_no_declaration_nets"] + c["undecided_model_absent_nets"] + c["undecided_other_nets"], c
        assert c["layout_bound_nets"] == c["maker_held_nets"] + c["bound_decided_nets"], c
        non = c["signal_nets"] - c["low_speed_nets"]
        print("%s | %s | %d | %d | %d | %d | %d | %d (%d + %d + %d) | %d | %d (%d + %d) | %s, %d, %d | %s%s" % (
            L.upper(), r["inputs"]["netlist"]["sha256_16"], c["signal_nets"], c["low_speed_nets"], non, c["maker_edge_nets"],
            c["bound_edge_nets"], c["undecided_nets"], c["undecided_no_declaration_nets"], c["undecided_model_absent_nets"],
            c["undecided_other_nets"], c["answered_nets"], c["layout_bound_nets"], c["maker_held_nets"], c["bound_decided_nets"],
            ms["state"], ms["asked"], ms["absent"], v["verdict"], (" FAILS: %s" % r["fails"][:2]) if r["fails"] else ""))
        for k, x in c.items(): tot[k] += x
        tot["non_slow"] += non
        res[L] = r
    print("all | | %d | %d | %d | %d | %d | %d (%d + %d + %d) | %d | %d (%d + %d) | |" % (
        tot["signal_nets"], tot["low_speed_nets"], tot["non_slow"], tot["maker_edge_nets"], tot["bound_edge_nets"],
        tot["undecided_nets"], tot["undecided_no_declaration_nets"], tot["undecided_model_absent_nets"], tot["undecided_other_nets"],
        tot["answered_nets"], tot["layout_bound_nets"], tot["maker_held_nets"], tot["bound_decided_nets"]))
    # a published figure: by what
    by = collections.Counter()
    for L, r in res.items():
        for row in r["rows"]:
            for n, e in (row.get("net_edges") or {}).items():
                if e["decided_by"] == "MAKER": by[e["basis"]] += 1
    print()
    print("DECIDED BY A PUBLISHED FIGURE, by what kind of figure: %s" % (", ".join("%s %d" % kv for kv in sorted(by.items())) or "none"))
    for L in sorted(res):
        r = res[L]
        und = [(n, row["undecided_kind"].get(n), rs, row) for row in r["rows"] for n, rs in sorted((row.get("undecided") or {}).items())]
        if und:
            print()
            print("BOARD %s, UNDECIDED (%d):" % (L.upper(), len(und)))
            for kind in ("NO_DECLARATION", "MODEL_ABSENT", "OTHER"):
                these = [(n, rs) for n, k, rs, _row in und if k == kind]
                if not these: continue
                print("  %s (%d): %s" % (kind, len(these), ", ".join(n for n, _ in these)))
                if L in want or kind == "OTHER":
                    for n, rs in these: print("    %s: %s" % (n, " | ".join(str(x) for x in rs)[:400]))
        if L not in want: continue
        print()
        print("BOARD %s, NET BY NET, every net outside LOW_SPEED_OR_DC that is not decided by a published figure:" % L.upper())
        for row in r["rows"]:
            for n, e in sorted((row.get("net_edges") or {}).items()):
                if e["decided_by"] == "MAKER": continue
                ans = (row.get("answered") or {}).get(n)
                rec = recs.get(e["source"]) or {}
                docs = ["%s%s (sha256/16 %s)" % (c["document"], (" p. %s" % c["page"]) if c.get("page") else "", c.get("sha256_16"))
                        for c in (rec.get("checked") or []) if isinstance(c, dict) and c.get("document")]
                print("  %s [entry %s, %s]: %s ns, %s %s; %s" % (
                    n, row["pattern"], row["class"], e["edge_ns"], e["basis"], e["source"],
                    ("ANSWERED in the netlist: %s" % ans) if ans else
                    ("LAYOUT-BOUND, BOUND_DECIDES" if n in (row.get("bound_decides") or []) else "never long on this board")))
                print("      governed by: %s" % "; ".join(e["bound_drivers"]))
                if e.get("maker_edge_ns") is not None: print("      a published figure beside it, deciding nothing: %s ns (%s)" % (e["maker_edge_ns"], e["maker_by"]))
                print("      why a bound: %s" % " ".join(str(rec.get("derivation") or "").split())[:420])
                print("      documents searched: %s" % ("; ".join(docs) or str(rec.get("no_document") or "none named")))
        print()
        print("BOARD %s, decided by a published figure:" % L.upper())
        for row in r["rows"]:
            for n, e in sorted((row.get("net_edges") or {}).items()):
                if e["decided_by"] == "MAKER":
                    print("  %s [entry %s]: %s ns, %s %s (%s)%s" % (n, row["pattern"], e["edge_ns"], e["basis"], e["source"], e["by"],
                          "; answered: %s" % (row.get("answered") or {}).get(n) if (row.get("answered") or {}).get(n) else
                          ("; LAYOUT-BOUND, held by the figure" if n in (row.get("maker_holds") or []) else "")))
        for x in r.get("notes") or []: print("  note: %s" % x)


if __name__ == "__main__":
    if len(sys.argv) < 4: print(__doc__); sys.exit(2)
    main(sys.argv[1:])
