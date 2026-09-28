#!/usr/bin/env python3
"""Every maker's clause a decoupling declaration quotes, looked up in the document it names (MESHSAT-1357, d6dec).

FEA-006's layout-entry stage asks for "the per-class requirement ... written from each maker's own words ... with its
source per class". Round 8 wrote a `basis` on every one of the 425 declarations of the six boards, and this reads
them back against the PDFs held under v2/vendor/: for each basis, every passage in quotation marks is searched for
in the document the basis names (by its path, or by the literature number or part name it gives), and the page it is
found on is compared with the page the basis states. The rows of tools/pcb_decoupling.yaml are checked the same way.

WHAT A RESULT MEANS
  FOUND       every quoted passage is in the named document, word for word after the normalisation below
  PAGE        found, and on another page than the basis states (both are given; a basis may count printed pages
              where this counts the PDF's own)
  ELSEWHERE   found, in a held document the basis does not name
  NOT_FOUND   a quoted passage is in no held document as written: the quotation is a paraphrase, the document is not
              held, or its text layer does not carry the words (a figure); the row says which passages
  NO_QUOTE    the basis quotes nothing: it states a requirement in its own words, and nothing can be looked up
NORMALISATION, and nothing else: case, runs of white space, the typographic quotes, dashes and the micro sign to
their plain forms, a hyphen at a line's end joined. A passage broken by `...` is searched piece by piece, in order.

It needs poppler's pdftotext and runs where the full vendor tree is (the rented box). It writes its text cache and
its result where it is told and nothing in the tree.

Usage: basis_check.py <checkout root> <cache dir> <out.json> [--jobs N]"""
import os, sys, re, json, glob, hashlib, subprocess
from concurrent.futures import ProcessPoolExecutor

BOARDS = [("a", "pcb-a-power-a23", "pcb-a-power"), ("b", "pcb-b-compute-b19", "pcb-b-compute"),
          ("c", "pcb-c-display-c8", "pcb-c-display"), ("d", "pcb-d-aprs-d9", "pcb-d-aprs"),
          ("e", "pcb-e1-dock-e7", "pcb-e1-dock"), ("p", "pcb-p-pack-p2", "pcb-p-pack")]
TR = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-", "‑": "-", "‐": "-",
      "−": "-", "µ": "u", "μ": "u", "­": "", " ": " ", "Ω": "ohm", "Ω": "ohm", "×": "x",
      "ﬁ": "fi", "ﬂ": "fl", "™": "", "®": ""}


def norm(t):
    t = "".join(TR.get(c, c) for c in t)
    t = re.sub(r"-\s*\n\s*", "", t)            # a hyphen at a line's end
    t = re.sub(r"\s+", " ", t).lower().strip()
    t = re.sub(r"\s+([,.;:)])", r"\1", t); t = re.sub(r"\(\s+", "(", t)
    t = re.sub(r"(\d)\s*-\s*(uf|nf|pf|v|ohm|mm)\b", r"\1 \2", t)      # 0.1-uF and 0.1 uF are one spelling
    t = re.sub(r"(\d)\s+(uf|nf|pf)\b", r"\1\2", t)
    return t


def pdf_text(args):
    path, cache = args
    h = hashlib.sha256(open(path, "rb").read()).hexdigest()
    out = os.path.join(cache, h[:24] + ".txt")
    if not os.path.exists(out):
        r = subprocess.run(["pdftotext", path, out + ".tmp"], capture_output=True, text=True, timeout=1800)
        if r.returncode != 0 or not os.path.exists(out + ".tmp"):
            open(out + ".tmp", "w").write("")
        os.replace(out + ".tmp", out)
    return path, h, out


def quotes(basis):
    """The passages a basis puts in quotation marks, each as its pieces between ellipses, with the page it states.

    A single quote opens a passage only where no letter or digit stands before it and closes one only where no
    letter follows, so the apostrophe of "the maker's" neither opens nor closes a passage (the first version let
    it open one and swallow the real opening quote after it). The page is the reference that follows the passage
    within a few characters ("... (p.11)", board E's style), else the nearest one before it ("p.23: '...'")."""
    b = "".join(TR.get(c, c) if c in "\u2018\u2019\u201c\u201d" else c for c in basis)
    out = []
    pat = re.compile(r"(?<![A-Za-z0-9])'((?:[^']|(?<=[A-Za-z])'(?=[A-Za-z]))+)'(?![A-Za-z])|\"([^\"]+)\"")
    pref = re.compile(r"(?:pp?\.|pages?|printed pages?)\s*(\d+)(?:\s*(?:-|to|and|,)\s*(\d+))?")
    for m in pat.finditer(b):
        q = (m.group(1) or m.group(2) or "").strip()
        if len(q) < 12 or not re.search(r"[a-z]{3}", q): continue
        after = re.match(r"\s*\(\s*(?:[\d.]+,\s*)?(?:pp?\.)\s*(\d+)(?:\s*(?:-|to|and|,)\s*(\d+))?", b[m.end():m.end() + 60])
        pg = [after.groups()] if after else pref.findall(b[:m.start()])
        pages = []
        if pg:
            a, z = pg[-1]
            pages = list(range(int(a), int(z) + 1)) if z and 0 <= int(z) - int(a) < 12 else [int(a)] + ([int(z)] if z else [])
        pieces = [p.strip(" ,;:") for p in re.split(r"\s*\.\.\.\s*|\s*\[\.\.\.\]\s*|\s*\u2026\s*", q) if len(p.strip(" ,;:")) >= 8]
        if pieces: out.append({"quote": q, "pieces": pieces, "pages_stated": pages})
    return out


def doc_hints(basis):
    paths = re.findall(r"v2/vendor/[\w./\-]+\.pdf", basis)
    # TI literature numbers (SLUSC67B, SNVSAI1D, SLOS597B, SCAA082A: S, three letters, three letters or digits with
    # at least one digit, a revision letter), Diodes and Microchip DS numbers, application notes, ADI's 8705af style
    ids = re.findall(r"\b(?:S[A-Z]{3}(?=[A-Z0-9]{0,2}\d)[A-Z0-9]{3}[A-Z]?|DS\d{5}|AN\s?\d{3,4}|\d{4}a?f[a-z]?|BST-[A-Z0-9\-]+)\b", basis)
    parts = re.findall(r"\b(?:[A-Z]{2,}\d{2,}[A-Z0-9\-]*|RP2040|W25Q16JV|VEML7700|ATECC608B|DS3231\w*)\b", basis)
    return paths, [i.replace(" ", "") for i in ids], parts


def main(a):
    root, cache, out = a[0], a[1], a[2]
    jobs = int(a[a.index("--jobs") + 1]) if "--jobs" in a else 16
    os.makedirs(cache, exist_ok=True)
    pdfs = sorted(glob.glob(os.path.join(root, "v2", "vendor", "**", "*.pdf"), recursive=True))
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        texts = list(ex.map(pdf_text, [(p, cache) for p in pdfs], chunksize=4))
    docs = {}
    for path, h, tp in texts:
        raw = open(tp, encoding="utf-8", errors="replace").read()
        pages = [norm(p) for p in raw.split("\f")]
        rel = os.path.relpath(path, root)
        docs[rel] = {"sha256": h, "pages": pages, "head": " ".join(pages[:3])[:6000], "n": len(pages),
                     "chars": sum(len(p) for p in pages), "flat": " \f ".join(pages)}
    claims = []
    for letter, phase, stem in BOARDS:
        it = json.load(open(os.path.join(root, "v2", "ecad", phase, "out", stem + "-intent.json"), encoding="utf-8"))
        for e in it.get("bypass", []):
            claims.append({"where": "board %s %s at %s.%s class %s" % (letter.upper(), e.get("cap"), e.get("part"), e.get("pin"), e.get("class")),
                           "board": letter, "basis": e.get("basis") or ""})
        for lp in it.get("power_loops", []) or []:
            claims.append({"where": "board %s %s loop of %s" % (letter.upper(), lp.get("loop"), lp.get("converter")),
                           "board": letter, "basis": lp.get("basis") or ""})
    yp = os.path.join(root, "v2", "ecad", "tools", "pcb_decoupling.yaml")
    if os.path.exists(yp):
        import yaml
        y = yaml.safe_load(open(yp, encoding="utf-8")) or {}
        for fam in y.get("parts", []):
            for row in fam.get("rows", []):
                for cl in row.get("clauses", []):
                    claims.append({"where": "pcb_decoupling.yaml %s %s" % (fam.get("id"), row.get("pins")),
                                   "board": "table", "table": True,
                                   "basis": "%s p.%s: '%s'" % (cl.get("document") or fam.get("document"), cl.get("page"), cl.get("quote"))})
    seen = {}; rows = []
    for c in claims:
        key = c["basis"]
        if key in seen: seen[key]["used_by"].append(c["where"]); continue
        qs = quotes(c["basis"]); paths, ids, parts = doc_hints(c["basis"])
        named = [p for p in paths if p in docs]
        if not named:
            for rel, d in docs.items():
                fn = os.path.basename(rel).lower()
                if any(i.lower() in d["head"].replace(" ", "") or i.lower() in fn for i in ids): named.append(rel)
            if not named:
                for rel, d in docs.items():
                    fn = os.path.basename(rel).lower().replace("-", "").replace("_", "")
                    if any(p.lower().replace("-", "") in fn for p in parts if len(p) >= 5): named.append(rel)
        row = {"basis": c["basis"], "used_by": [c["where"]], "documents_named": sorted(set(named)), "paths_not_held": [p for p in paths if p not in docs],
               "quotes": []}
        if not qs: row["status"] = "NO_QUOTE"
        worst = "FOUND"
        for q in qs:
            res = {"quote": q["quote"], "pages_stated": q["pages_stated"], "found": []}
            pieces = [norm(p) for p in q["pieces"]]
            def look(cands):
                hits = []
                for rel in cands:
                    d = docs[rel]; pg = []
                    flat = d["flat"]
                    pos = 0; okp = True; where = []
                    for pc in pieces:
                        i = flat.find(pc, pos)
                        if i < 0: okp = False; break
                        where.append(flat.count("\f", 0, i) + 1); pos = i + len(pc)
                    if not okp:
                        # the pieces in any order, each on its own
                        where = []
                        for pc in pieces:
                            i = flat.find(pc)
                            if i < 0: where = None; break
                            where.append(flat.count("\f", 0, i) + 1)
                    if where: hits.append({"document": rel, "pages": sorted(set(where))})
                return hits
            hits = look(row["documents_named"]); st = "FOUND"
            if not hits:
                hits = look([r for r in docs if r not in row["documents_named"]]); st = "ELSEWHERE" if hits else "NOT_FOUND"
            if hits and q["pages_stated"] and st == "FOUND":
                if not any(set(h["pages"]) & set(q["pages_stated"]) for h in hits): st = "PAGE"
            if st == "NOT_FOUND":
                # which pieces are missing, against the named documents
                miss = []
                for pc in pieces:
                    if not any(pc in docs[r]["flat"] for r in (row["documents_named"] or docs)): miss.append(pc)
                res["pieces_not_found"] = miss
            res["status"] = st; res["found"] = hits[:4]
            row["quotes"].append(res)
            order = ["FOUND", "PAGE", "ELSEWHERE", "NOT_FOUND"]
            if order.index(st) > order.index(worst): worst = st
        row.setdefault("status", worst)
        seen[key] = row; rows.append(row)
    tally = {}
    for r in rows: tally[r["status"]] = tally.get(r["status"], 0) + 1
    ent = {}
    for r in rows: ent[r["status"]] = ent.get(r["status"], 0) + len(r["used_by"])
    json.dump({"what": "the quoted clauses of the decoupling declarations, looked up in the held documents",
               "documents": len(docs), "documents_with_no_text": sorted(r for r, d in docs.items() if d["chars"] < 200),
               "claims": len(claims), "distinct_bases": len(rows), "by_status_bases": tally, "by_status_declarations": ent,
               "rows": rows}, open(out, "w"), indent=1, ensure_ascii=False)
    print("basis_check: %d documents (%d with no text layer), %d declarations and table rows, %d distinct bases" % (
        len(docs), sum(1 for d in docs.values() if d["chars"] < 200), len(claims), len(rows)))
    print("basis_check: bases by status %s; declarations by status %s" % (json.dumps(tally, sort_keys=True), json.dumps(ent, sort_keys=True)))
    for r in rows:
        if r["status"] in ("NOT_FOUND", "ELSEWHERE", "PAGE"):
            for q in r["quotes"]:
                if q["status"] == r["status"]:
                    print("  %-9s %-44s | %s | stated p.%s found %s%s" % (q["status"], r["used_by"][0][:44], q["quote"][:70], q["pages_stated"],
                          [(h["document"].split("/")[-1], h["pages"]) for h in q["found"][:2]],
                          (" | missing: %s" % [m[:50] for m in q.get("pieces_not_found", [])]) if q.get("pieces_not_found") else ""))
    return 0


if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
