#!/usr/bin/env python3
"""Every count the H3 handover pages quote, read from the files of this tree (MESHSAT-1357, 27 September 2026).

A copy of v2/docs/records/h2/handover_counts.py (the H2 assembler's, as revised after H2), adapted for handover H3 by
the H3 pages worker so that no figure on START-HERE, LAYER-STATUS, CONTINUATION-BRIEF, ENGINEERING-QUESTIONS, REGENERATE
or RELEASE-H3 is typed from memory: the pages quote this script's output (`handover_counts.out` beside it), and a
reader re-runs it from the repository root, or from the root of an extracted snapshot, to check them. It reads only; it
writes nothing but its standard output, and it needs no git.

What it reads, all by repository path:
  v2/docs/CURRENT-EVIDENCE.md                   the headline, the candidate table and the layout-entry blocker rows
  v2/ecad/tools/pcb_requirements.yaml           the registry's counts, its baseline state and reviews, the seven FEA records
  v2/docs/handover/ENGINEERING-QUESTIONS.md     the index rows (EQ ids) and the group of each
  v2/release/handover/_generated/*/             each board's export provenance, BOM rows and ERC counts
  v2/ecad/<phase>/out/<stem>.net                each board's committed netlist, against the one its export names
  v2/ecad/tools/boards/<x>.json                 each board's declared phase
  v2/docs/reviews/*.md                          the review records of layers 1 to 3, by sha256/16
Usage: python3 v2/docs/records/h3/handover_counts.py [repository root]

What differs from the H2 script, and nothing else:
  1. this docstring and the name H3;
  2. the review records listed also match TARGETED-RECHECK (layer 3's re-check, filed after H2) and
     DEFINITION-RESTRUCTURE-CHECK (the check of the definition restructure, filed after H2), and the documents listed
     after them also name v2/docs/handover/DEFINITION-STATUS.md; the H2 pattern would have left all three out;
  3. the registry's `baseline_reviews` are printed, each with whether the file's sha256/16 is the one the registry names;
  4. each export line also says whether the netlist its provenance names is the committed netlist of this tree.

Which inputs are H2's. The exports under v2/release/handover/_generated/ were made for H2 (boards A, B, D and E at
763bccdf, boards C and P at 99cde56b) and were not re-made for H3. They are valid for H3 because each provenance.json
names the sha256 of the schematic and of the netlist it was made from, and lines "schematic ... (is the committed one)"
and "netlist ... (is the committed one)" below compare both with the files of this tree: an export whose schematic or
netlist had changed would print "is NOT". v2/docs/records/h3/design_difference.py shows the same from git, against
H2's source commit b89b50b4.
"""
import csv, glob, hashlib, json, os, re, sys

import yaml

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")


def p(*a):
    return os.path.join(ROOT, *a)


def sha16(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def table_after(lines, header_start):
    """The rows of the first Markdown table whose header line starts with header_start, as lists of cells."""
    out, on = [], False
    for ln in lines:
        if not on and ln.startswith(header_start):
            on = True
            continue
        if on:
            if ln.startswith("|---"):
                continue
            if not ln.startswith("|"):
                break
            out.append([c.strip() for c in ln.strip().strip("|").split("|")])
    return out


def main():
    print("handover_counts: repository root %s" % (sys.argv[1] if len(sys.argv) > 1 else "."))
    # ------------------------------------------------------------------ CURRENT-EVIDENCE.md
    ce = p("v2", "docs", "CURRENT-EVIDENCE.md")
    lines = open(ce, encoding="utf-8").read().splitlines()
    head = next(ln for ln in lines if ln.startswith("**Foundations"))
    print("\n[CURRENT-EVIDENCE.md sha256/16 %s]" % sha16(ce))
    print("headline: %s" % head.strip("*"))
    cand = table_after(lines, "| board | declared phase |")
    print("candidate table (board, phase, netlist sha256/16, ready):")
    for r in cand:
        net = re.search(r"([0-9a-f]{16})", r[2])
        print("  %s %s netlist %s | %s" % (r[0], r[1], net.group(1) if net else "none", r[5]))
    cats = table_after(lines, "| what closes it first | owner |")
    print("layout-entry reasons by what closes them first (A B C D E P E5 set):")
    tot = [0] * 8
    for r in cats:
        nums = [int(x) for x in r[2:10]]
        tot = [a + b for a, b in zip(tot, nums)]
        print("  %s: %s" % (r[0], " ".join(str(n) for n in nums)))   # the whole label (it was cut at 90 characters
        # until after H2, which cut "(the hold itself stays until that stage)" short: the H2 usability check)
    print("  total: A %d, B %d, C %d, D %d, E %d, P %d, E5 %d, set %d" % tuple(tot))
    rows = table_after(lines, "| board | rule | reading now |")
    per = {}
    for r in rows:
        per.setdefault(r[0], []).append(r[1])
    print("layout-entry blocker rows per board (%d rows):" % len(rows))
    for b in ("A", "B", "C", "D", "E", "P", "E5"):
        print("  %s (%d): %s" % (b, len(per.get(b, [])), "; ".join(per.get(b, []))))
    # ------------------------------------------------------------------ the requirements registry
    rp = p("v2", "ecad", "tools", "pcb_requirements.yaml")
    reg = yaml.safe_load(open(rp, encoding="utf-8"))
    print("\n[pcb_requirements.yaml sha256/16 %s]" % sha16(rp))
    print("baseline_state: %s; sources_read_at: %s" % (reg.get("baseline_state"), reg.get("sources_read_at")))
    for br in reg.get("baseline_reviews") or []:
        path, _, want = br.partition("@")
        have = sha16(p(*path.split("/"))) if os.path.exists(p(*path.split("/"))) else "absent"
        print("baseline review: %s names %s, the file %s" % (path, want, "is that one" if have == want else
                                                                "is NOT (%s)" % have))
    for k in ("needs", "records", "owner_rulings", "session_choices", "open_items", "closed_items"):
        v = reg.get(k) or []
        span = " (%s to %s)" % (v[0]["id"], v[-1]["id"]) if k == "session_choices" and v else ""
        print("%s: %d%s" % (k, len(v), span))
    kinds = {}
    for r in reg.get("records") or []:
        kinds[r["id"].split("-")[0]] = kinds.get(r["id"].split("-")[0], 0) + 1
    print("records by prefix: %s" % ", ".join("%s %d" % kv for kv in sorted(kinds.items())))
    oc = {}
    for o in reg.get("open_items") or []:
        oc[o.get("class")] = oc.get(o.get("class"), 0) + 1
    print("open items by class: %s" % ", ".join("%s %d" % kv for kv in sorted(oc.items())))
    print("open item ids: %s" % " ".join(o["id"] for o in reg.get("open_items") or []))
    fea = sorted((r for r in reg.get("records") or [] if r["id"].startswith("FEA-")), key=lambda r: r["id"])
    print("feasibility records (%d):" % len(fea))
    for r in fea:
        print("  %s %s prototype_1=%s evidence_result=%s: %s" % (r["id"], r.get("status"), r.get("prototype_1"),
                                                                 r.get("evidence_result"), (r.get("title") or "")[:100]))
    # ------------------------------------------------------------------ the engineering questions
    eqp = p("v2", "docs", "handover", "ENGINEERING-QUESTIONS.md")
    eq = open(eqp, encoding="utf-8").read().splitlines()
    idx = table_after(eq, "| Id | Question |")
    heads = [ln for ln in eq if re.match(r"^### EQ-\d\d\.", ln)]
    groups = {}
    for r in idx:
        groups[r[2]] = groups.get(r[2], 0) + 1
    print("\n[ENGINEERING-QUESTIONS.md]")
    print("index rows: %d (%s to %s); question sections: %d; by group: %s" % (
        len(idx), idx[0][0] if idx else "-", idx[-1][0] if idx else "-", len(heads),
        ", ".join("%s %d" % kv for kv in sorted(groups.items()))))
    # ------------------------------------------------------------------ the exports
    print("\n[v2/release/handover/_generated]")
    tot_rows = tot_nolcsc = tot_rcl = 0
    for prov in sorted(glob.glob(p("v2", "release", "handover", "_generated", "*", "provenance.json"))):
        j = json.load(open(prov, encoding="utf-8"))
        d = os.path.dirname(prov)
        sch = p(*j["schematic"].split("/"))
        now = hashlib.sha256(open(sch, "rb").read()).hexdigest() if os.path.exists(sch) else None
        net = p(*(j["phase_directory"] + "/out/" + j["stem"] + ".net").split("/"))
        net_now = hashlib.sha256(open(net, "rb").read()).hexdigest() if os.path.exists(net) else None
        bom = glob.glob(os.path.join(d, "NOT_FOR_FAB-*-bom-per-reference.csv"))
        rows = nol = rcl = 0
        for b in bom:
            for r in csv.DictReader(open(b, encoding="utf-8")):
                rows += 1
                if not (r.get("LCSC") or "").strip():
                    nol += 1
                    if re.match(r"^[RCL]\d", r["Reference"]):
                        rcl += 1
        tot_rows += rows; tot_nolcsc += nol; tot_rcl += rcl
        erc = j.get("erc_violations_by_severity") or {}
        print("  %s (%s): made at %s, label %s, table phase %s, schematic %s (%s the committed one), netlist %s "
              "(%s the committed one), "
              "parity %s, %s pages, %s BOM rows (%d without LCSC, %d of them R/C/L), ERC %s, result %s" % (
                  j["board"].upper(), j["phase_directory"].split("/")[-1], j["commit"][:8], j.get("schematic_phase_label"),
                  j.get("board_table_phase"), j["schematic_sha256"][:16],
                  "is" if now == j["schematic_sha256"] else "is NOT", (j.get("committed_netlist_sha256") or "-")[:16],
                  "is" if net_now and net_now == j.get("committed_netlist_sha256") else "is NOT",
                  j.get("netlist_parity_with_the_schematic"), j.get("paged_pdf_pages"), j.get("bom_rows_per_reference"),
                  nol, rcl, ", ".join("%s %d" % kv for kv in sorted(erc.items())), j.get("result")))
    print("  BOM rows per reference over the six boards: %d; without an LCSC code %d; of those R/C/L %d" %
          (tot_rows, tot_nolcsc, tot_rcl))
    # ------------------------------------------------------------------ declared phases
    ph = []
    for f in sorted(glob.glob(p("v2", "ecad", "tools", "boards", "*.json"))):
        ph.append("%s %s" % (os.path.basename(f)[:-5].upper(), json.load(open(f, encoding="utf-8")).get("phase")))
    print("\n[declared phases, boards/<x>.json] %s" % ", ".join(ph))
    # ------------------------------------------------------------------ the review records of layers 1 to 3
    print("\n[review records of layers 1 to 3, sha256/16]")
    for f in sorted(glob.glob(p("v2", "docs", "reviews", "*.md"))):
        n = os.path.basename(f)
        if re.match(r"(REVIEW-(A|B|LAYER)-|TARGETED-(CHECK|RECHECK)|DEFINITION-RESTRUCTURE-CHECK)", n):
            print("  v2/docs/reviews/%s %s" % (n, sha16(f)))
    for f in ("v2/docs/PRODUCT-BRIEF.md", "v2/docs/CONOPS.md", "v2/docs/handover/DEFINITION-STATUS.md",
              "v2/docs/OPERATING-ENVELOPE.md", "v2/docs/TEST-PLAN.md", "v2/ecad/tools/pcb_envelope.yaml"):
        first = next((ln for ln in open(p(*f.split("/")), encoding="utf-8").read().splitlines()
                      if ln.startswith("**Status:")), "") if f.endswith(".md") else ""
        print("  %s %s%s" % (f, sha16(p(*f.split("/"))), (": " + first.strip()[:110]) if first else ""))


if __name__ == "__main__":
    main()
