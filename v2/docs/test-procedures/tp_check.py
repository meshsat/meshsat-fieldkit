#!/usr/bin/env python3
"""tp_check.py: check every test procedure of v2/docs/test-procedures/ against its sources and print the index
(MESHSAT-1357, 3 October 2026; the supplier handover's phase 2).

Each procedure TP-<id>.md turns a specification that already exists in the records into an executable procedure. This script
holds each one to the records it rests on, reading them from this tree only:

  C1 the procedure's metadata block (<!-- tp ... -->) names its id, title, register rows, L4-E11 rows and 5d route rows;
  C2 every register row it names exists in v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md, every L4-E11 row in that record's
     section 8 table, every 5d route row in v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md section 5d's table;
  C3 every quote (<!-- q src="..." [row="..." col="..."] --> ... <!-- /q -->) is the source's text: a table quote equals
     its cell exactly (whitespace collapsed), a text quote is found verbatim in the source (whitespace collapsed);
  C4 the pass conditions are quoted, not restated: each register row's Acceptance, each L4-E11 row's Acceptance, and each
     5d row's Specimen, What transfers, Authorisation and What to buy cells appear as table quotes in the procedure;
  C5 every path written in backticks from v2/ exists in this tree;
  C6 every TBD is written "TBD (owed by <row>[, <row>]): ..." and each owing row exists (an R- or E11- row);
  C7 the procedure carries the mark "PROPOSED, for the supplier to review and agree before execution";
  C8 no em or en dash in any file of the folder;
  C9 the README names every procedure file, and every row of 5d's route table is covered exactly once: by a procedure, by
     the README's external entry (T-H1) or by its not-covered list with a reason.

It prints, for each procedure, its file's sha256/16 and path (regen_out.py checks those pins), the rows with their register
state and class, the counts, and the TBDs; then the index, the 5d coverage and the TBDs by owing row. It never prints an
absolute path and never writes a file. Exit 0 when every check passes, 1 otherwise.
Usage: python3 v2/docs/test-procedures/tp_check.py   (from the repository root; the .out is regenerated only through
_bin/regen_out.py)"""
import glob
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FOLDER = "v2/docs/test-procedures"
REG = "v2/docs/records/l4e9/DOWNSTREAM-REGISTER.md"
ARCH = "v2/docs/records/l4e9/L4-POWER-ARCHITECTURE.md"
E11 = "v2/docs/records/l4e11/L4E11-SOURCE-ONLY-AND-ENTRY.md"
MARK = "PROPOSED, for the supplier to review and agree before execution"
LONG_DASHES = (chr(0x2014), chr(0x2013))
KEYS = ("id", "title", "register", "e11", "route5d")
COLS_5D = ("Specimen", "What transfers to the final board", "Authorisation", "What to buy")
Q_RX = re.compile(r"<!-- q (.*?) -->\n(.*?)\n<!-- /q -->", re.S)
ATTR_RX = re.compile(r'(\w+)="([^"]*)"')
META_RX = re.compile(r"<!-- tp\n(.*?)\n-->", re.S)
INDEX_RX = re.compile(r"<!-- tp-index\n(.*?)\n-->", re.S)
PATH_RX = re.compile(r"`(v2/[^`\s]+)`")
TBD_RX = re.compile(r"TBD \(owed by ([^)]*)\)")


def norm(s):
    return " ".join(s.split())


def unquote(block):
    out = []
    for ln in block.split("\n"):
        ln = ln.strip()
        if ln.startswith(">"):
            ln = ln[1:]
        out.append(ln)
    return norm(" ".join(out))


def split_row(line):
    parts = re.split(r"(?<!\\)\|", line.strip())
    if parts and parts[0] == "":
        parts = parts[1:]
    if parts and parts[-1] == "":
        parts = parts[:-1]
    return [p.strip() for p in parts]


def tables(text):
    """Every markdown table: (header cells, [row cells]). A table is a header line, a |---| line, then rows."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines) - 1:
        a, b = lines[i].strip(), lines[i + 1].strip()
        if a.startswith("|") and b.startswith("|") and set(b.replace("|", "").replace(":", "").replace(" ", "")) == {"-"}:
            head = split_row(a)
            rows, j = [], i + 2
            while j < len(lines) and lines[j].strip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            out.append((head, rows))
            i = j
        else:
            i += 1
    return out


def key(cell):
    return cell.replace("**", "").strip()


class Sources:
    """The records, read once each, from the tree."""

    def __init__(self, root):
        self.root, self.text, self.tabs = root, {}, {}

    def read(self, rel):
        if rel not in self.text:
            p = os.path.join(self.root, rel)
            self.text[rel] = open(p, encoding="utf-8").read() if os.path.isfile(p) else None
        return self.text[rel]

    def cell(self, rel, row, col):
        """The one cell at (row, col) over every table of the file that has the column; (cell, error)."""
        t = self.read(rel)
        if t is None:
            return None, "the source %s is not in the tree" % rel
        if rel not in self.tabs:
            self.tabs[rel] = tables(t)
        hits = []
        for head, rows in self.tabs[rel]:
            if col not in head:
                continue
            ci = head.index(col)
            for r in rows:
                if r and key(r[0]) == row and ci < len(r):
                    hits.append(r[ci])
        if len(hits) != 1:
            return None, "%d cells at row %r, column %r of %s (one expected)" % (len(hits), row, col, rel)
        return hits[0], None

    def first_cells(self, rel, col):
        t = self.read(rel)
        if rel not in self.tabs:
            self.tabs[rel] = tables(t)
        return [key(r[0]) for head, rows in self.tabs[rel] if col in head for r in rows if r]

    def route_rows(self):
        for head, rows in tables(self.read(ARCH)):
            if head[:2] == ["Experiment", "Specimen"] and "What to buy" in head:
                return [key(r[0]) for r in rows if r]
        return []


def meta(text):
    m = META_RX.search(text)
    if not m:
        return None
    d = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def listed(v, sep=","):
    return [x.strip() for x in v.split(sep) if x.strip() and x.strip() != "none"]


def verify_quotes(src, rel, text):
    """C3 on one file: (the set of table quotes, table count, text count, failures)."""
    fails = []
    quotes = [(dict(ATTR_RX.findall(a)), unquote(b)) for a, b in Q_RX.findall(text)]
    if text.count("<!-- q ") != len(quotes):
        fails.append("%s: C3 %d quote marker(s) without a well-formed block" % (rel, text.count("<!-- q ") - len(quotes)))
    tq = {(q.get("src"), q.get("row"), q.get("col")) for q, _ in quotes if "row" in q}
    n_table = n_text = 0
    for q, body in quotes:
        s = q.get("src", "")
        if "row" in q:
            cell, err = src.cell(s, q["row"], q.get("col", ""))
            if err:
                fails.append("%s: C3 %s" % (rel, err))
            elif norm(cell) != body:
                fails.append("%s: C3 the quote of %s row %s column %s is not its cell" % (rel, s, q["row"], q.get("col")))
            else:
                n_table += 1
        else:
            t = src.read(s)
            if t is None:
                fails.append("%s: C3 the source %s is not in the tree" % (rel, s))
            elif body not in norm(t):
                fails.append("%s: C3 a text quote is not found verbatim in %s: %r" % (rel, s, body[:90]))
            else:
                n_text += 1
    return tq, n_table, n_text, fails


def check_procedure(src, rel, text):
    """(report lines, failures, facts) for one procedure."""
    fails, lines = [], []
    m = meta(text)
    if m is None or any(k not in m for k in KEYS):
        return [], ["%s: C1 the metadata block is missing or lacks one of %s" % (rel, ", ".join(KEYS))], None
    regs, e11s, routes = listed(m["register"]), listed(m["e11"]), listed(m["route5d"], ";;")
    if not regs:
        fails.append("%s: C1 no register row named" % rel)
    reg_rows, e11_rows, route_rows = set(src.first_cells(REG, "Acceptance")), set(src.first_cells(E11, "Acceptance")), set(src.route_rows())
    tq, n_table, n_text, qf = verify_quotes(src, rel, text)
    fails += qf
    for r in regs:
        if r not in reg_rows:
            fails.append("%s: C2 register row %s does not exist" % (rel, r))
        if (REG, r, "Acceptance") not in tq:
            fails.append("%s: C4 register row %s's Acceptance is not quoted" % (rel, r))
    for r in e11s:
        if r not in e11_rows:
            fails.append("%s: C2 L4-E11 row %s does not exist" % (rel, r))
        if (E11, r, "Acceptance") not in tq:
            fails.append("%s: C4 L4-E11 row %s's Acceptance is not quoted" % (rel, r))
    for r in routes:
        if r not in route_rows:
            fails.append("%s: C2 5d route row %r does not exist" % (rel, r))
        for c in COLS_5D:
            if (ARCH, r, c) not in tq:
                fails.append("%s: C4 5d row %r's %s cell is not quoted" % (rel, r, c))
    paths = sorted(set(PATH_RX.findall(text)))
    for p in paths:
        if not os.path.exists(os.path.join(src.root, p.rstrip(".,;:"))):
            fails.append("%s: C5 the path %s is not in the tree" % (rel, p))
    tbds = []
    for mm in TBD_RX.finditer(text):
        owners = listed(mm.group(1))
        tail = text[mm.end():mm.end() + 400]
        cut = min([i for i in (tail.find(". "), tail.find(".\n"), tail.find("\n\n")) if i >= 0] or [len(tail)])
        tbds.append((owners, norm(tail[:cut]).lstrip(": ")))
        for o in owners:
            ok = (o in reg_rows) if o.startswith("R-") else (o in e11_rows) if o.startswith("E11-") else False
            if not ok:
                fails.append("%s: C6 the TBD's owing row %s is not a register or L4-E11 row" % (rel, o))
        if not owners:
            fails.append("%s: C6 a TBD names no owing row" % rel)
    if text.count("TBD") != len(tbds):
        fails.append("%s: C6 %d TBD(s) not written 'TBD (owed by <row>): ...'" % (rel, text.count("TBD") - len(tbds)))
    if MARK not in norm(text):
        fails.append("%s: C7 the PROPOSED mark is missing" % rel)
    lines.append("  id %s: %s" % (m["id"], m["title"]))
    for r in regs:
        st, _ = src.cell(REG, r, "State")
        cl, _ = src.cell(REG, r, "Class")
        lines.append("  register %s: %s (%s, %s)" % (r, "exists" if r in reg_rows else "MISSING", st, cl))
    for r in e11s:
        lines.append("  L4-E11 %s: %s" % (r, "exists" if r in e11_rows else "MISSING"))
    for r in routes:
        lines.append("  5d row '%s': %s" % (r, "exists" if r in route_rows else "MISSING"))
    lines.append("  quotes: %d table (each equal to its cell), %d text (each found verbatim)" % (n_table, n_text))
    lines.append("  cross-references: %d paths from v2/, %s" % (len(paths), "all present" if not any(": C5" in f for f in fails) else "SOME MISSING"))
    lines.append("  TBD: %d" % len(tbds))
    for owners, t in tbds:
        lines.append("    - owed by %s: %s" % (", ".join(owners), t[:110]))
    lines.append("  PROPOSED mark: %s" % ("present" if MARK in norm(text) else "MISSING"))
    facts = {"id": m["id"], "title": m["title"], "regs": regs, "e11s": e11s, "routes": routes, "tbds": tbds,
             "quotes": n_table + n_text}
    return lines, fails, facts


def check(root=ROOT, folder=FOLDER):
    """(report lines, failures). `folder` is relative to root, or absolute (a test's fixture)."""
    src = Sources(root)
    fdir = folder if os.path.isabs(folder) else os.path.join(root, folder)
    shown = folder if not os.path.isabs(folder) else "<fixture>"
    out, fails, facts = [], [], []
    out.append("tp_check: the test procedures of %s (MESHSAT-1357), checked against the records in this tree" % shown)
    out.append("sources: %s; %s (section 5d); %s (section 8 and 17d); and each quote's own source" % (REG, ARCH, E11))
    out.append("")
    out.append("1. The procedures")
    files = sorted(glob.glob(os.path.join(fdir, "TP-*.md")))
    if not files:
        fails.append("no TP-*.md in the folder")
    for f in files:
        rel = "%s/%s" % (shown, os.path.basename(f))
        raw = open(f, "rb").read()
        text = raw.decode("utf-8")
        out.append("%s %s" % (hashlib.sha256(raw).hexdigest()[:16], rel))
        ln, fl, fa = check_procedure(src, rel, text)
        out += ln
        fails += fl
        if fa:
            facts.append((os.path.basename(f), fa))
    for f in sorted(glob.glob(os.path.join(fdir, "*"))):
        if os.path.isfile(f) and f.endswith((".md", ".py", ".out")):
            t = open(f, encoding="utf-8").read()
            for d in LONG_DASHES:
                if d in t:
                    fails.append("%s/%s: C8 carries a long dash (U+%04X)" % (shown, os.path.basename(f), ord(d)))
    readme_p = os.path.join(fdir, "README.md")
    covered = {}
    if not os.path.isfile(readme_p):
        fails.append("C9 the README is missing")
        readme = ""
    else:
        readme = open(readme_p, encoding="utf-8").read()
        out.append("")
        out.append("%s %s/README.md" % (hashlib.sha256(readme.encode("utf-8")).hexdigest()[:16], shown))
        _, a, b, qf = verify_quotes(src, "%s/README.md" % shown, readme)
        fails += qf
        out.append("  quotes: %d table, %d text, each checked against its source" % (a, b))
        out.append("  PROPOSED mark: %s" % ("present" if MARK in norm(readme) else "MISSING"))
        if MARK not in norm(readme):
            fails.append("%s/README.md: C7 the PROPOSED mark is missing" % shown)
        for p in sorted(set(PATH_RX.findall(readme))):
            if not os.path.exists(os.path.join(root, p.rstrip(".,;:"))):
                fails.append("%s/README.md: C5 the path %s is not in the tree" % (shown, p))
    for name, fa in facts:
        if name not in readme:
            fails.append("C9 the README does not name %s" % name)
        for r in fa["routes"]:
            covered.setdefault(r, []).append(fa["id"])
    im = INDEX_RX.search(readme)
    ext = []
    if not im:
        fails.append("C9 the README has no tp-index block")
    else:
        for ln in im.group(1).split("\n"):
            if ":" not in ln:
                continue
            k, v = ln.split(":", 1)
            parts = [p.strip() for p in v.split("|")]
            if k.strip() == "external" and len(parts) == 4:
                tid, path, rows, route = parts
                if not os.path.isfile(os.path.join(root, path)):
                    fails.append("C9 the external procedure %s is not in the tree" % path)
                for r in listed(rows):
                    if r not in set(src.first_cells(REG, "Acceptance")):
                        fails.append("C9 the external procedure's row %s does not exist" % r)
                covered.setdefault(route, []).append(tid)
                ext.append((tid, path, rows, route))
            elif k.strip() == "not-covered" and len(parts) == 2 and parts[1]:
                covered.setdefault(parts[0], []).append("not covered here: " + parts[1])
            else:
                fails.append("C9 a tp-index line is malformed: %r" % ln[:80])
    out.append("")
    out.append("2. The index")
    out.append("| Procedure | File | Register rows | L4-E11 rows | 5d route row | Quotes | TBDs |")
    out.append("|---|---|---|---|---|---|---|")
    for name, fa in facts:
        out.append("| %s | %s | %s | %s | %s | %d | %d |" % (fa["id"], name, ", ".join(fa["regs"]), ", ".join(fa["e11s"]) or "none",
                                                          "; ".join(fa["routes"]), fa["quotes"], len(fa["tbds"])))
    for tid, path, rows, route in ext:
        out.append("| %s | %s (not in this folder) | %s | none | %s | not checked here | not checked here |" % (tid, path, rows, route))
    out.append("")
    out.append("3. Coverage of section 5d's route table")
    for r in src.route_rows():
        c = covered.get(r, [])
        out.append("- %s: %s" % (r, "; ".join(c) if c else "NOT COVERED"))
        if len(c) != 1:
            fails.append("C9 5d row %r is covered %d times (once expected)" % (r, len(c)))
    for r in sorted(covered):
        if r not in src.route_rows():
            fails.append("C9 %r is not a row of 5d's route table" % r)
    out.append("")
    out.append("4. The TBDs by owing row")
    by = {}
    for name, fa in facts:
        for owners, t in fa["tbds"]:
            for o in owners:
                by.setdefault(o, []).append("%s: %s" % (fa["id"], t[:100]))
    for o in sorted(by, key=lambda s: (s.split("-")[0], int(re.sub(r"\D", "", s) or 0))):
        out.append("- %s" % o)
        for t in by[o]:
            out.append("  - %s" % t)
    out.append("")
    if fails:
        out.append("RESULT: FAIL (%d)" % len(fails))
        out += ["  " + f for f in fails]
    else:
        out.append("RESULT: ALL PASS (%d procedures, %d quotes, %d TBDs)" % (
            len(facts), sum(fa["quotes"] for _, fa in facts), sum(len(fa["tbds"]) for _, fa in facts)))
    return out, fails


def main():
    out, fails = check()
    sys.stdout.write("\n".join(out) + "\n")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
