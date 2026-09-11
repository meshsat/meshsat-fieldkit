#!/usr/bin/env python3
"""kb_inventory.py, everything V2 uses, enumerated from authority (MESHSAT-862, 11 September 2026).

WHY THIS EXISTS. On 10 September the store reported zero parts without a document. The number was
true and measured over one source, `gen_sch_*.py`. Asked whether that meant complete, checking found
four more parts with no datasheet inside a minute, and then eight more from the BOMs and five from the
design documents. A coverage number produced by one heuristic over one source is not a coverage
number; it is that heuristic's opinion of itself.

So this reads THREE independent sources and requires them to agree:

  bom    the shipped BOM of the newest deliverable per board, which is what an assembler places.
         PCB-E5 has no BOM at all and that is correct: it is a bare contact board with no parts.
  gen    the generators, through kb_parts, which is what the design instantiates.
  doc    V2-SPEC.md, ASSEMBLY.md, PANEL.md and BUILD.md, which carry everything that is never placed
         on a board: the case, the panel parts, the connectors, the antennas, the cables, the pack.
         The appendix is deliberately NOT read: it is the whole history including every retired part,
         and enumerating from it would enumerate the past.

Every extracted item is then one of four things, and the fourth is the only failure:

  DOCUMENTED   a document names its exact order code
  FAMILY       a document names its family and v2/vendor/family-matches.txt says why that is enough
  OPEN PICK    v2/vendor/open-picks.txt records that no part has been chosen yet, so no datasheet can
               exist; this is a design decision outstanding, not a missing file
  UNCOVERED    none of the above. FAIL.

Anything the extractor DROPS is written to out/kb_inventory-excluded.txt with the rule that dropped
it, because a hand-made exclusion list is exactly where a real part disappears quietly, and that is
the failure class both red teams keep naming.

Usage: kb_inventory.py [--write] [--out-dir out]     (--write regenerates v2/vendor/PARTS.md)
"""
import sys, os, re, csv, glob, argparse, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(TOOLS))
VENDOR = os.path.join(ROOT, "vendor")
BOARDS = os.path.join(ROOT, "release", "revA", "boards")
DOCS = [os.path.join(ROOT, "docs", n) for n in ("V2-SPEC.md", "ASSEMBLY.md", "PANEL.md")]
DOCS += [os.path.join(ROOT, "BUILD.md")]
PARTS_MD = os.path.join(VENDOR, "PARTS.md")
FAMILY = os.path.join(VENDOR, "family-matches.txt")
OPEN_PICKS = os.path.join(VENDOR, "open-picks.txt")
NOT_USED = os.path.join(VENDOR, "not-used.txt")

sys.path.insert(0, HERE)
sys.path.insert(0, TOOLS)
import kbdb, kbenv, kb_parts as K      # noqa: E402
import verdict                          # noqa: E402

NO_BOM = {"e5": "PCB-E5 is the bare dock contact board: gerbers only, no schematic, no placed parts"}


def declared(path):
    """`key   # reason` lines, the erc-allow.txt idiom. A line without a reason declares nothing."""
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "#" not in line:
            continue
        key, reason = line.split("#", 1)
        if key.strip() and reason.strip():
            out[key.strip()] = reason.strip()
    return out


def certified_verdicts():
    """Part token -> (verdict, code) from the dated certification, so PARTS.md can say whether a part
    this kit uses can actually be bought and not only whether a datasheet exists for it. The table is
    keyed by BOM comment and this inventory by part token, so the join is a containment test: the
    longest token that appears in a row's comment wins, which is how `CSD19532Q5B` finds its row and
    `CSD1` would not."""
    path = os.path.join(ROOT, "release", "revA", "order", "JLC-CERTIFIED.tsv")
    out = {}
    if not os.path.exists(path):
        return out
    import csv as _csv
    for row in _csv.DictReader(open(path, errors="replace"), delimiter="\t"):
        v = (row.get("verdict") or "").strip()
        c = " ".join((row.get("comment") or "").split())
        if v and c:
            out.setdefault(c.upper(), (v, (row.get("code") or "").strip()))
    return out


def buyable_of(token, table):
    """The verdict of the certified row whose comment contains this token, longest comment last so a
    specific row beats a generic one."""
    t = token.upper()
    hits = [(len(c), val) for c, val in table.items() if t in c]
    return max(hits)[1] if hits else ("", "")


def newest_deliverables():
    """{board letter: bom path}. The newest phase per letter by its number, so B16-quote beats B15,
    which matters: B15 is the newest ROUTED board but B16 is what the order set ships."""
    best = {}
    for d in sorted(glob.glob(os.path.join(BOARDS, "meshsat-pcb-*"))):
        m = re.match(r"meshsat-pcb-([a-z0-9]+)-revA-([A-Z]+)(\d+)", os.path.basename(d))
        if not m:
            continue
        letter, _pfx, num = m.group(1), m.group(2), int(m.group(3))
        boms = [b for b in glob.glob(os.path.join(d, "*bom.csv"))]
        if not boms:
            continue
        if letter not in best or num > best[letter][0]:
            best[letter] = (num, boms[0], os.path.basename(d))
    return {k: (v[1], v[2]) for k, v in best.items()}


def tokens(text, dropped, where):
    """Part-number-shaped tokens, with every rejection recorded so the exclusion list is reviewable."""
    out = []
    for t in K.PART.findall(text):
        if len(t) < 6:
            dropped.setdefault(t, ("shorter than six characters", where))
            continue
        if t.upper() in K.SKIP:
            dropped.setdefault(t, ("on the SKIP list", where))
            continue
        if K.NOT_A_PART.match(t):
            dropped.setdefault(t, ("matches the not-a-part pattern (net, package or literature name)", where))
            continue
        out.append(t)
    return out


def from_boms(dropped):
    items = {}
    for letter, (bom, folder) in sorted(newest_deliverables().items()):
        with open(bom, newline="", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                comment = (row.get("Comment") or "").strip()
                for t in tokens(comment, dropped, "BOM %s" % folder):
                    rec = items.setdefault(t, {"where": set(), "sources": set(), "note": ""})
                    rec["where"].add(letter.upper())
                    rec["sources"].add("bom")
                    if not rec["note"]:
                        rec["note"] = " ".join(comment.split())[:120]
    return items


def from_docs(dropped):
    items = {}
    for path in DOCS:
        if not os.path.exists(path):
            continue
        name = os.path.basename(path)
        for line in open(path, errors="replace"):
            for t in tokens(line, dropped, name):
                rec = items.setdefault(t, {"where": set(), "sources": set(), "note": ""})
                rec["where"].add(name.replace(".md", ""))
                rec["sources"].add("doc")
                if not rec["note"]:
                    rec["note"] = " ".join(line.split())[:120]
    return items


STOP = {"the", "a", "an", "and", "of", "its", "for", "on", "in", "with", "part", "picks", "owed",
        "s", "or", "to", "wall", "parts", "drawing", "module"}


def class_rows_from_boms():
    """BOM rows that name a CLASS or an owed drawing rather than a part.

    The open-picks list was derived from one paragraph in BUILD.md, and six of the fifteen class rows
    on the shipped BOMs were missing from it: the two Mill-Max spring pins, CSD19532Q5B class,
    CSD19536KTT class, Si1308EDL class, and E6's mixer fans as distinct from the cooler fans. A list of
    what is undecided, derived from one prose paragraph, is the same single-source mistake as the first
    coverage number and as the layer count. These come from the BOMs, which are what gets ordered."""
    out = []
    for letter, (bom, folder) in sorted(newest_deliverables().items()):
        try:
            fh = open(bom, newline="", encoding="utf-8", errors="replace")
        except OSError:
            continue
        for row in csv.DictReader(fh):
            c = " ".join((row.get("Comment") or "").split())
            if re.search(r"\bclass\b|\bowed\b", c, re.I):
                out.append((folder, c))
    return out


def owed_from_build():
    """The owed part picks as BUILD.md itself lists them.

    Without this the open-picks list is unguarded: deleting a line from it made the item vanish and
    the run still passed, which is the same defect as a gate that cannot fire. The design document
    already enumerates what is owed, so the list is checked against the document rather than trusted."""
    path = os.path.join(ROOT, "BUILD.md")
    if not os.path.exists(path):
        return []
    for line in open(path, errors="replace"):
        if "Part picks owed:" in line:
            body = line.split("Part picks owed:", 1)[1]
            body = body.split("(", 1)[0]
            return [p.strip(" .-\n") for p in re.split(r"[;,]| and ", body) if p.strip(" .-\n")]
    return []


def build(db):
    dropped = {}
    items = {}
    for src, got in (("bom", from_boms(dropped)), ("doc", from_docs(dropped))):
        for t, rec in got.items():
            cur = items.setdefault(t, {"where": set(), "sources": set(), "note": ""})
            cur["where"] |= rec["where"]
            cur["sources"] |= rec["sources"]
            cur["note"] = cur["note"] or rec["note"]
    for t, rec in K.parts_from_generators().items():
        cur = items.setdefault(t, {"where": set(), "sources": set(), "note": ""})
        cur["where"] |= {b.upper() for b in rec["boards"]}
        cur["sources"].add("gen")
        cur["note"] = cur["note"] or rec["note"]

    fam, picks, unused = declared(FAMILY), declared(OPEN_PICKS), declared(NOT_USED)
    buyable = certified_verdicts()
    # Open picks are NOT token-derived and cannot be: an item with no part number chosen has no token
    # to find. They are enumerated by hand in open-picks.txt and added here, because an inventory that
    # lists only what has been decided hides the part of the kit that is still undecided, which is the
    # opposite of what an enumeration is for.
    for slug, reason in picks.items():
        items.setdefault(slug, {"where": {"design documents"}, "sources": {"pick"}, "note": reason})
    for t, rec in items.items():
        rec["buyable"], rec["buy_code"] = buyable_of(t, buyable)
        if t in unused:
            # named in a document only to record that it was rejected; chasing its datasheet would
            # waste exactly the time this store exists to save
            rec.update({"doc": "", "state": "NOT USED", "reason": unused[t], "exact": False})
            continue
        if t in picks:
            # checked BEFORE the store: an open pick's slug is not a part number, and looking it up
            # let "tamper-switch" family-match its way to somebody else's document
            rec.update({"doc": "", "state": "OPEN PICK", "reason": picks[t], "exact": False})
            continue
        hit = K.lookup(db, t)
        if hit:
            rec["matched"], rec["doc"], rec["page"], rec["how"] = hit
            rec["exact"] = hit[0].upper() == t.upper()
            rec["state"] = "DOCUMENTED" if rec["exact"] else ("FAMILY" if t in fam else "UNDECLARED FAMILY")
            rec["reason"] = fam.get(t, "")
        else:
            rec.update({"doc": "", "state": "UNCOVERED", "reason": "", "exact": False})
    return items, dropped


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out-dir", default="out")
    a = ap.parse_args(argv)
    try:
        db = kbdb.connect()
    except kbenv.InfraFail as e:
        print(e, file=sys.stderr)
        return verdict.write("kb_inventory", verdict.INCONCLUSIVE, note=str(e), out_dir=a.out_dir)

    items, dropped = build(db)
    counts = {}
    for st in ("DOCUMENTED", "FAMILY", "UNDECLARED FAMILY", "OPEN PICK", "NOT USED", "UNCOVERED"):
        counts[st.lower().replace(" ", "_")] = sum(1 for r in items.values() if r["state"] == st)
    counts["items"] = len(items)
    for v in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED"):
        counts["buyable_" + v.lower()] = sum(1 for r in items.values() if r.get("buyable") == v)
    counts["buyable_unproved"] = sum(1 for r in items.values()
                                     if r.get("buyable") not in ("CERTIFIED", "HAND_FIT", "BENCH_FITTED"))
    counts["dropped_tokens"] = len(dropped)

    os.makedirs(a.out_dir, exist_ok=True)
    with open(os.path.join(a.out_dir, "kb_inventory-excluded.txt"), "w") as fh:
        fh.write("# Tokens the inventory extractor dropped, with the rule that dropped each one.\n"
                 "# Written by kb_inventory.py. Read it: a real part hidden here is exactly the defect\n"
                 "# this file exists to prevent, and it is invisible anywhere else.\n\n")
        for t in sorted(dropped):
            fh.write("%-28s %-62s first seen in %s\n" % (t, dropped[t][0], dropped[t][1]))

    # every phrase BUILD.md calls an owed pick must be claimed by a line in open-picks.txt
    picks_text = " ".join((k + " " + v).lower() for k, v in declared(OPEN_PICKS).items())
    unclaimed = []
    for phrase in owed_from_build():
        words = [w for w in re.split(r"[^a-z0-9]+", phrase.lower()) if w and w not in STOP and len(w) > 1]
        if words and not any(w in picks_text for w in words):
            unclaimed.append(phrase)
    # and every class-only row on a shipped BOM must be claimed too
    for folder, c in class_rows_from_boms():
        words = [w for w in re.split(r"[^a-z0-9]+", c.lower()) if w and w not in STOP and len(w) > 2]
        if words and not any(w in picks_text for w in words[:12]):
            unclaimed.append("%s: %s" % (folder.replace("meshsat-pcb-", ""), c[:70]))
    counts_unclaimed = len(unclaimed)
    for u in unclaimed:
        print("UNCLAIMED CLASS ROW  %s" % u)

    bad = sorted(t for t, r in items.items() if r["state"] in ("UNCOVERED", "UNDECLARED FAMILY"))
    for t in bad:
        r = items[t]
        print("%-14s %-26s %s" % (r["state"], t, r["note"][:70]))

    bad = bad + ["unclaimed owed pick: " + u for u in unclaimed]   # after the per-item print loop
    if a.write:
        write_parts_md(items, counts)
        print("wrote %s" % os.path.relpath(PARTS_MD, ROOT))

    counts["unclaimed_owed_picks"] = counts_unclaimed
    res = verdict.FAIL if bad else verdict.PASS
    return verdict.write("kb_inventory", res, counts=counts, denominator=len(items),
                         evidence=bad[:30], out_dir=a.out_dir,
                         note="" if not bad else "%d item(s) with no document and no declaration" % len(bad))


def write_parts_md(items, counts):
    L = []
    L.append("# Everything V2 uses")
    L.append("")
    L.append("Generated by `v2/ecad/tools/kb/kb_inventory.py`. **Never hand edited**: edit the")
    L.append("generators, the BOMs, the design documents or the declaration files beside this one, and")
    L.append("regenerate. It is the enumerated answer to what this kit is made of, and it is checked")
    L.append("against the datasheet store on every run.")
    L.append("")
    L.append("Three independent sources are read and must agree: **bom**, the shipped BOM of the newest")
    L.append("deliverable per board, which is what an assembler places; **gen**, the generators, which")
    L.append("is what the design instantiates; and **doc**, `V2-SPEC.md`, `ASSEMBLY.md`, `PANEL.md` and")
    L.append("`BUILD.md`, which carry everything never placed on a board. The design record appendix is")
    L.append("deliberately not read: it is the whole history, and enumerating it would enumerate the past.")
    L.append("")
    L.append("| state | meaning | count |")
    L.append("|---|---|---|")
    L.append("| DOCUMENTED | a document names its exact order code | %d |" % counts["documented"])
    L.append("| FAMILY | a family document covers it, with a declared reason | %d |" % counts["family"])
    L.append("| OPEN PICK | no part chosen yet, so no datasheet can exist | %d |" % counts["open_pick"])
    L.append("| NOT USED | named in a document only to record that it was rejected | %d |" % counts["not_used"])
    L.append("| UNCOVERED | no document and no declaration. This must be 0 | %d |" % counts["uncovered"])
    L.append("")
    L.append("Documented is not the same as buyable, so the purchase side is counted separately from")
    L.append("`v2/release/revA/order/JLC-CERTIFIED.tsv`, which is a dated reading of JLCPCB's catalogue")
    L.append("and not a promise about tomorrow.")
    L.append("")
    L.append("| purchase | meaning | count |")
    L.append("|---|---|---|")
    L.append("| CERTIFIED | JLCPCB returns this exact part, in our package, in stock | %d |" % counts.get("buyable_certified", 0))
    L.append("| HAND_FIT | bought elsewhere, with a distributor and a URL on record | %d |" % counts.get("buyable_hand_fit", 0))
    L.append("| BENCH_FITTED | a header, land or jumper that nobody places | %d |" % counts.get("buyable_bench_fitted", 0))
    L.append("| unproved | no certified row yet: an open pick, or a part still owed | %d |" % counts.get("buyable_unproved", 0))
    L.append("")
    L.append("%d items in all. %d tokens were dropped by the extractor and every one is listed with its"
             % (counts["items"], counts["dropped_tokens"]))
    L.append("reason in `out/kb_inventory-excluded.txt`, because a hand-made exclusion list is where a")
    L.append("real part disappears quietly.")
    L.append("")
    for state, title, note in (
            ("UNCOVERED", "Uncovered: no document, no declaration", "This section must be empty."),
            ("UNDECLARED FAMILY", "Family matches that are not declared", "Each needs a line in `family-matches.txt`."),
            ("OPEN PICK", "Open picks: named as a class, no part chosen",
             "No datasheet can exist for these until a part is ruled. Each says what it needs."),
            ("NOT USED", "Named only to record a rejection", "No datasheet is owed for these."),
            ("FAMILY", "Covered by a family document, with the reason",
             "A datasheet names the family; the order code names the reel."),
            ("DOCUMENTED", "Covered by a document naming the exact part", "")):
        rows = sorted((t, r) for t, r in items.items() if r["state"] == state)
        if not rows and state not in ("UNCOVERED", "UNDECLARED FAMILY"):
            continue
        L.append("## %s (%d)" % (title, len(rows)))
        L.append("")
        if note:
            L.append(note)
            L.append("")
        if not rows:
            L.append("None.")
            L.append("")
            continue
        L.append("| item | used in | source | document | buyable | note |")
        L.append("|---|---|---|---|---|---|")
        for t, r in rows:
            doc = r.get("doc", "") or ("_" + (r.get("reason", "") or "no part chosen")[:70] + "_")
            buy = r.get("buyable") or "-"
            if r.get("buy_code"):
                buy += " " + r["buy_code"]
            L.append("| `%s` | %s | %s | %s | %s | %s |"
                     % (t, ", ".join(sorted(r["where"]))[:40], "+".join(sorted(r["sources"])),
                        doc.replace("|", "/")[:70], buy,
                        (r.get("reason") or r["note"]).replace("|", "/")[:80]))
        L.append("")
    open(PARTS_MD, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
