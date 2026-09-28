#!/usr/bin/env python3
"""CON-010 and REQ-044 rebound to the FINAL v2/docs/CURRENT-EVIDENCE.md of integration set 7 (MESHSAT-1357, 28 September
2026; a copy of v2/docs/records/int7/apply_rebind_final_page.py with the entry's wording for this set). Both records are bound to the
page by sha256/16 and the integration re-rendered it (the set 6 line merged with the H3 line, the renderer's derived
head sentence and limit notices, CON-010's own re-decision, the dispositions). This script re-reads the rows each record
rests on in the NEW page and in the readings behind them, writes one evidence entry per record that starts with the
file's path and names the sections that differ and the rows re-read, and rebinds each record to the new page. It
changes no evidence_result and no other record.

Asserted before writing (every claim in an entry is read from the tree, never typed): the OLD binding is read from the
records themselves (both must carry the same page sha); the tree's page is not OLD and the page at HEAD is OLD (a second
run is refused); the rows named are on the new page with the result and class the readings give; the readings carry the
counts the entry states. Run from the repository root after the final render and before its commit; render once more
after it (REQUIREMENTS-TRACE.md prints the entries) and check that CURRENT-EVIDENCE.md does not move."""
import hashlib, json, os, re, subprocess, sys
sys.dont_write_bytecode = True

P = "v2/ecad/tools/pcb_requirements.yaml"
CE = "v2/docs/CURRENT-EVIDENCE.md"


def refuse(msg):
    print("apply_rebind_page_int8: REFUSED: %s" % msg); sys.exit(1)


def sha16(b): return hashlib.sha256(b).hexdigest()[:16]


def sections(page):
    out = [["the head (headline and introduction)", []]]
    for line in page.split("\n"):
        if line.startswith("## ") or line.startswith("### "): out.append([line.lstrip("# ").strip(), []])
        else: out[-1][1].append(line)
    return [(h, "\n".join(b)) for h, b in out]


def row(page, start):
    hits = [" ".join(l.split()) for l in page.split("\n") if l.startswith(start)]
    if len(hits) != 1: refuse("%d row(s) begin %r on the page, one expected" % (len(hits), start))
    return hits[0]


def reading(path):
    try: return json.load(open(path, encoding="utf-8"))
    except Exception as e: refuse("%s cannot be read (%s)" % (path, e))


def layout_reasons(page):
    n = {}; on = False
    for line in page.split("\n"):
        if line.startswith("| board | rule | reading now |"): on = True; continue
        if on:
            if not line.startswith("|"):
                if n: break
                continue
            c = [x.strip() for x in line.strip().strip("|").split("|")]
            if set(c[0]) <= set("-"): continue
            n[c[0]] = n.get(c[0], 0) + 1
    return n


def wrap(s):
    words = s.split(); lines = []; cur = "         "
    for w in words:
        if len(cur) + 1 + len(w) > 120: lines.append(cur); cur = "          " + w
        else: cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1; j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def main():
    if not (os.path.exists(P) and os.path.exists(CE)): refuse("run from the repository root")
    t = open(P, encoding="utf-8").read()
    new_page = open(CE, encoding="utf-8").read(); new = sha16(new_page.encode("utf-8"))
    old_page = subprocess.run(["git", "show", "HEAD:" + CE], capture_output=True, text=True, check=True).stdout
    olds = set()
    for rid in ("CON-010", "REQ-044"):
        i, j = rec_span(t, rid)
        m = re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(CE), t[i:j])
        if len(m) != 1: refuse("%s carries %d binding(s) to the page, one expected" % (rid, len(m)))
        olds.add(m[0])
    if len(olds) != 1: refuse("the two records are bound to different pages: %s" % sorted(olds))
    OLD = olds.pop()
    if new == OLD: refuse("the tree's page is the page the records are bound to (%s): nothing was rendered" % OLD)
    if sha16(old_page.encode("utf-8")) != OLD:
        refuse("the page at HEAD is %s, not %s: render, run this script, then commit page and registry together" % (sha16(old_page.encode("utf-8")), OLD))

    so, sn = sections(old_page), sections(new_page)
    if [h for h, _ in so] != [h for h, _ in sn]: refuse("the two pages do not carry the same headings: %s vs %s" % ([h for h, _ in so], [h for h, _ in sn]))
    differ = [h for (h, a), (_, b) in zip(so, sn) if a != b]
    same = [h for (h, a), (_, b) in zip(so, sn) if a == b]
    lo, ln = layout_reasons(old_page), layout_reasons(new_page)
    order = ["A", "B", "C", "D", "E", "P", "E5"]
    counts = "layout-entry reasons %d to %d (%s)" % (sum(lo.values()), sum(ln.values()),
             ", ".join("%s %d to %d" % (b, lo.get(b, 0), ln.get(b, 0)) for b in order))

    R = "v2/ecad/%s/routed/%s.verdict.json"
    d = reading(R % ("pcb-d-aprs-d9", "inhibit_chain_d")); a = reading(R % ("pcb-a-power-a23", "inhibit_chain_a"))
    c = reading(R % ("pcb-c-display-c8", "inhibit_chain_c")); p = reading(R % ("pcb-p-pack-p2", "pack_protection"))
    sd = reading(R % ("pcb-d-aprs-d9", "safe_lines_d")); sa = reading(R % ("pcb-a-power-a23", "safe_lines_a"))
    nd, na, nc = [x["inputs"]["netlist_%s" % l]["sha256_16"] for x, l in ((d, "d"), (a, "a"), (c, "c"))]
    np_ = (p["inputs"].get("netlist") or p["inputs"].get("netlist_p") or {}).get("sha256_16")
    # the rows the records rest on, as the readings say they must read
    def expect_rf(x): return "INCONCLUSIVE" if x["counts"].get("undecided") and not x["counts"].get("fail") else ("FAIL" if x["counts"].get("fail") else "PASS")
    want = {
        "| D | RF-002 ": "| D | RF-002 %s | CURRENT_CANDIDATE (BOUND) |" % expect_rf(d),
        "| A | RF-002 ": "| A | RF-002 %s | CURRENT_CANDIDATE (BOUND) |" % expect_rf(a),
        "| D | SCH-004 ": "| D | SCH-004 a safety line fails safe | SCHEMATIC | safe_lines_d: netlist %s is the current candidate's |" % nd,
        "| A | SCH-004 ": "| A | SCH-004 a safety line fails safe | SCHEMATIC | safe_lines_a: netlist %s is the current candidate's |" % na,
        "| P | BAT-001 ": "| P | BAT-001 %s | CURRENT_CANDIDATE (BOUND) |" % p["verdict"],
    }
    if c["verdict"] == "PASS":
        want["| C | RF-002 "] = "| C | RF-002 transmit inhibit is hardware | SCHEMATIC | inhibit_chain_c: netlist %s is the current candidate's |" % nc
    for start, begins in want.items():
        got = row(new_page, start)
        if not got.startswith(begins): refuse("the row %r reads %r, expected it to begin %r" % (start, got[:160], begins))
    if (sd["verdict"], sa["verdict"]) != ("PASS", "PASS"): refuse("safe_lines reads %s, %s" % (sd["verdict"], sa["verdict"]))

    how = ("%s re-read at integration set 7 of 28 September 2026 (branch fnd/int8: the lid tray stream w5tray with its two "
           "drafts, the third check's carried items, the Codex pilot's records on finding I-03 with its items S-98 and S-99, "
           "and the contract IF-AB-POWER's contact rating rewritten from the held JST VH catalogue, which is a configuration "
           "input of interfaces.py, so INT-001 reads CONFIG_CHANGED on every board until the set's re-take on the KiCad host), "
           "rules_status three times and rules_render on the tree with main's gitignored evidence installed (the file at %s before). Of "
           "the page's %d sections %d differ from that file (%s) and %d are byte-identical (%s); %s." % (
               CE, OLD, len(sn), len(differ), "; ".join(differ) or "none", len(same), "; ".join(same) or "none", counts))
    notes = {
        "CON-010": how + (
            " The rows this record rests on, re-read on the new page: RF-002 reads %s on CURRENT_CANDIDATE (BOUND) evidence "
            "on board D (inhibit_chain_d %d pass, %d failed, %d undecided of %d on netlist %s) and %s on board A "
            "(inhibit_chain_a %d pass, %d failed, %d undecided of %d on netlist %s); SCH-004 reads PASS on both (safe_lines_d "
            "on %s, safe_lines_a on %s); board C's inhibit_chain_c reads %s of %d on netlist %s. This entry rebinds the page and "
            "re-decides nothing: the result stands as the predicate of this integration's entry set it, bound to the file at %s."
            % (expect_rf(d), d["counts"].get("pass", 0), d["counts"].get("fail", 0), d["counts"].get("undecided", 0), d["denominator"], nd,
               expect_rf(a), a["counts"].get("pass", 0), a["counts"].get("fail", 0), a["counts"].get("undecided", 0), a["denominator"], na,
               nd, na, c["verdict"], c["denominator"], nc, new)),
        "REQ-044": how + (
            " The row this record rests on, re-read on the new page: board P's BAT-001 reads %s on CURRENT_CANDIDATE (BOUND) "
            "evidence (pack_protection on netlist %s, %d of %d checks failed: %s). The review D-09 asks for before the pack "
            "board is released is still not engaged, and a re-render changes nothing of that; this entry rebinds the page and "
            "re-decides nothing, so the record stays %s, bound to the file at %s."
            % (p["verdict"], np_, p["counts"].get("fail", 0), p["denominator"], "; ".join(str(e) for e in p["evidence"])[:600],
               re.search(r"(?m)^    evidence_result: (\S+)", t[slice(*rec_span(t, "REQ-044"))]).group(1), new)),
    }
    out = t
    sys.path.insert(0, "v2/ecad/tools")
    import claims_check as _cc
    for rid, note in notes.items():
        if not note.startswith(CE): refuse("the entry for %s does not start with the file's path" % rid)
        hit = _cc.CLAIM.search(note)
        if hit: refuse("the entry for %s carries the claim word %r" % (rid, hit.group(0)))
        i, j = rec_span(out, rid); r = out[i:j]
        res0 = re.search(r"(?m)^    evidence_result: (\S+)", r).group(1)
        r2 = r.replace('"%s@%s"' % (CE, OLD), '"%s@%s"' % (CE, new))
        k = r2.index("    evidence_bound_to:")
        r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
        assert r2 != r and re.search(r"(?m)^    evidence_result: (\S+)", r2).group(1) == res0
        out = out[:i] + r2 + out[j:]
    if out == t: refuse("the new text does not differ from the old")

    import yaml
    A, B = yaml.safe_load(t), yaml.safe_load(out)
    ra = {r["id"]: r for r in A["records"]}; rb = {r["id"]: r for r in B["records"]}
    if list(ra) != list(rb): refuse("the record list changed")
    if {k: v for k, v in A.items() if k != "records"} != {k: v for k, v in B.items() if k != "records"}: refuse("something outside the records changed")
    moved = [k for k in ra if ra[k] != rb[k]]
    if sorted(moved) != ["CON-010", "REQ-044"]: refuse("records changed: %s" % moved)
    for k in moved:
        x, y = ra[k], rb[k]
        keys = [f for f in set(x) | set(y) if x.get(f) != y.get(f)]
        if sorted(keys) != ["evidence", "evidence_bound_to"]: refuse("%s: fields changed: %s" % (k, keys))
        if y["evidence"][:-1] != x["evidence"] or not str(y["evidence"][-1]).startswith(CE): refuse("%s: the evidence list is not the old list plus one entry" % k)
        if sorted(set(x["evidence_bound_to"]) ^ set(y["evidence_bound_to"])) != sorted(["%s@%s" % (CE, OLD), "%s@%s" % (CE, new)]):
            refuse("%s: the bindings changed by more than the page's" % k)
    open(P, "w", encoding="utf-8").write(out)
    if yaml.safe_load(open(P, encoding="utf-8").read()) != B: refuse("the file written does not re-parse to what was checked")
    for k in moved: print("apply_rebind_page_int8: %s rebound from %s to %s, evidence_result %s unchanged" % (k, OLD, new, rb[k]["evidence_result"]))
    print("apply_rebind_page_int8: sections that differ: %s" % ("; ".join(differ) or "none"))
    print("apply_rebind_page_int8: %s" % counts)


if __name__ == "__main__":
    main()
