#!/usr/bin/env python3
"""Where does TI's BQ4050 Technical Reference Manual (SLUUAQ3A) state a data-flash default two ways?

Review stream BAT, MESHSAT-1357, 26 September 2026. Third cycle: the second cycle compared only 92 section rows against
Table 14-1 and read the bit texts by eye; the checker found four words that reading missed (FET Options, Protection
Configuration, Enabled PF A, C and D, and the consequence of Manufacturing Status Init). This version asks the question
mechanically, for the whole of chapter 14 (14.2 to 14.14), in three ways:

  A. every parameter row of chapter 14 against its row in Table 14-1 (the data flash summary), by default value;
  B. every bit-field word (type H1, H2, H4) of chapter 14: the "(default)" marks and "Default is n." sentences of its
     own bit texts against its header default, over the bits that carry a mark (a word whose bit text marks no
     default is reported as unmarked, not as agreeing);
  C. the same bit marks against the Table 14-1 default, and any bit a word marks twice with different values.

Reads `pdftotext -layout` of the TRM. It prints every disagreement, the counts it compared, and every row it could not
parse or match, so its coverage is stated rather than assumed. Exit 0 always: it is an instrument, not a gate.

A section whose parameter block is a multi-row table (its header row carries a Description column, for example 14.13.3)
is not compared by name in A; it is counted and named in the output.

Run: python3 trm_defaults_check.py [trm.pdf]
Default input: the first of v2/vendor/battery/ti-sluuaq3a-bq4050-trm.pdf (filed in the same review by stream PKT) and
drafts/datasheets/ti-sluuaq3-bq4050-trm.pdf (the battery stream's byte-identical copy) found above this file, sha256
525d16b2bdee44e5b587ccf6800b9967bc524772d0b5a20937957ea2e738b7ad. The input's sha256 is printed.
"""
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _root():
    """The working tree this file sits in: the first directory above it that holds v2/vendor."""
    d = HERE
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, "v2", "vendor")):
            return d
        d = os.path.dirname(d)
    return HERE


ROOT = _root()
CANDIDATES = [os.path.join(ROOT, "v2", "vendor", "battery", "ti-sluuaq3a-bq4050-trm.pdf"),
              os.path.join(ROOT, "drafts", "datasheets", "ti-sluuaq3-bq4050-trm.pdf")]
TYPES = r"(?:H1|H2|H4|I1|I2|I4|U1|U2|U4|F4|S\d+|TBD)"
SEC_ROW = re.compile(r"^(?P<pre>.*?)\s{2,}(?P<type>" + TYPES + r")\s+(?P<min>\S+)\s+(?P<max>\S+)\s+(?P<dflt>\S+)")
TAB_ROW = re.compile(r"^(?P<pre>.*?)\s*(?P<addr>0x4[0-9a-fA-F]{3})\s+(?P<type>" + TYPES + r")\s+(?P<name>.+?)\s{2,}"
                     r"(?P<min>\S+)\s+(?P<max>\S+)\s+(?P<dflt>\S+)")
HEAD = re.compile(r"^(14\.\d+(?:\.\d+){1,2})\s+(\S.*?)\s*$")
FIELD = re.compile(r"^\s*(?P<name>[A-Za-z0-9_ ,]+?)\s*\(?Bits?\s*(?P<b>\d+)(?:\s*[–-]\s*(?P<e>\d+))?"
                   r"(?:\s*,\s*(?:Bit\s*)?(?P<b2>\d+))?\)?\s*:?")
MARK = re.compile(r"^\s*(?P<v>[01](?:\s*,\s*[01])?)\s*=.*\(default\)")
DEFAULT_IS = re.compile(r"Default is (?P<v>[01])\.")
PAGE = re.compile(r"SLUUAQ3A .* BQ4050\s+(\d+)\s*$|^\s*(\d+)\s+BQ4050\s+SLUUAQ3A")


def norm_name(s):
    s = s.lower().replace("sbs ", "sbs ").strip()
    aliases = {"mfg status init": "manufacturing status init", "pf fuse a": "permanent fail fuse a",
               "pf fuse b": "permanent fail fuse b", "pf fuse c": "permanent fail fuse c",
               "pf fuse d": "permanent fail fuse d", "cedv gauging configuration": "gauging configuration"}
    return aliases.get(s, s)


def num(v):
    v = v.replace("–", "-").replace("−", "-").strip().lower()
    try:
        return int(v, 16) if v.startswith("0x") else float(v)
    except ValueError:
        return v


def main():
    pdf = sys.argv[1] if len(sys.argv) > 1 else next(p for p in CANDIDATES if os.path.exists(p))
    L = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True, check=True).stdout.split("\n")
    L = [l.replace("\u2014", " - ") for l in L]   # TI's section titles use an em dash ("HWD\u2014Host Watchdog"); printed as " - "
    start = next(i for i, l in enumerate(L) if re.match(r"^14\.2 Settings\s*$", l))
    tstart = next(i for i, l in enumerate(L) if "Table 14-1. Data Flash Summary" in l and i > start)
    page_of = {}
    page = None
    for i in range(len(L) - 1, -1, -1):   # page footers follow their page's text; walk back so each line gets its page
        m = PAGE.search(L[i])
        if m:
            page = int(m.group(1) or m.group(2))
        page_of[i] = page

    # --- chapter 14 sections ---
    secs, unparsed, multirow = [], [], []
    heads = [(i, HEAD.match(L[i])) for i in range(start, tstart) if HEAD.match(L[i])]
    for k, (i, m) in enumerate(heads):
        end = heads[k + 1][0] if k + 1 < len(heads) else tstart
        body = L[i + 1:end]
        row = None
        if any("Class" in l and "Default" in l and "Description" in l for l in body[:3]):
            multirow.append("%s %s (p.%s)" % (m.group(1), m.group(2), page_of.get(i)))
            continue
        for j, l in enumerate(body[:8]):
            r = SEC_ROW.match(l)
            if r and "Class" not in l:
                row = (j, r)
                break
        if row is None:
            if any("Class" in l and "Default" in l for l in body[:4]):
                unparsed.append("%s %s (p.%s)" % (m.group(1), m.group(2), page_of.get(i)))
            continue
        j, r = row
        pre = [p for p in re.split(r"\s{2,}", r.group("pre").strip()) if p]
        rowname = pre[-1] if pre else ""
        sub = pre[-2] if len(pre) >= 2 else ""
        parent = next((h[1].group(2) for h in reversed(heads[:k]) if h[1].group(1).count(".") == m.group(1).count(".") - 1), "")
        s = {"sec": m.group(1), "title": m.group(2), "rowname": rowname, "sub": sub, "parent": parent,
             "type": r.group("type"), "dflt": r.group("dflt"), "page": page_of.get(i + 1 + j), "marks": {}, "dup": [],
             "fields": 0}
        if s["type"] in ("H1", "H2", "H4"):
            cur = None
            for l in body[j + 1:]:
                f = FIELD.match(l)
                if f and ("(Bit" in l or "Bit " in l.split(":")[0]):
                    b = int(f.group("b"))
                    e = f.group("e")
                    b2 = f.group("b2")
                    nm = f.group("name").strip()
                    if b2 is not None:
                        cur = ("pair", b, int(b2))
                    elif e is not None:
                        cur = ("range", b, int(e))
                    else:
                        cur = ("bit", b, nm)
                    s["fields"] += 1
                    continue
                if cur is None:
                    continue
                mk = MARK.match(l)
                dm = DEFAULT_IS.search(l)
                vals = None
                if mk:
                    vals = [int(x) for x in re.split(r"\s*,\s*", mk.group("v"))]
                elif dm:
                    vals = [int(dm.group("v"))]
                if vals is None:
                    continue
                if cur[0] == "bit" and len(vals) == 1:
                    put = {cur[1]: vals[0]}
                elif cur[0] == "bit" and len(vals) == 2:
                    # a one-bit field printed with its pair's code (BLT1/BLT0): the field whose name ends in 1 is the
                    # high member of the pair, the one ending in 0 the low member
                    put = {cur[1]: vals[0] if cur[2].endswith("1") else vals[1]}
                elif cur[0] == "pair" and len(vals) == 2:
                    put = {cur[1]: vals[0], cur[2]: vals[1]}
                else:
                    continue
                for bit, v in put.items():
                    if bit in s["marks"] and s["marks"][bit] != v:
                        s["dup"].append(bit)
                    s["marks"].setdefault(bit, v)
        secs.append(s)

    # --- Table 14-1 ---
    tab, tab_by_name = {}, {}
    for i in range(tstart, len(L)):
        r = TAB_ROW.match(L[i])
        if not r:
            continue
        # the subclass column starts at about column 16; a subclass printed over two or three lines (for example
        # "Maintenance" / "Charging", or "CEDV Smoothing" / "Config") is joined from the lines above and below
        frags = []
        for k in (i - 1, i, i + 1):
            if k != i and TAB_ROW.match(L[k]):
                continue
            text = r.group("pre") if k == i else L[k][:40]
            for m2 in re.finditer(r"\S+(?: \S+)*", text):
                if m2.start() >= 16:
                    frags.append(m2.group(0))
        sub = " ".join(frags)
        rec = {"addr": r.group("addr").lower(), "name": r.group("name").strip(), "sub": sub, "dflt": r.group("dflt"),
               "page": page_of.get(i)}
        tab.setdefault((norm_name(sub), norm_name(rec["name"])), rec)
        tab_by_name.setdefault(norm_name(rec["name"]), []).append(rec)

    def find(s):
        for sub in (s["sub"], s["parent"], s["title"]):
            for nm in (s["title"], s["rowname"]):
                t = tab.get((norm_name(sub), norm_name(nm)))
                if t:
                    return t
        for nm in (s["title"], s["rowname"]):
            c = tab_by_name.get(norm_name(nm), [])
            if len(c) == 1:
                return c[0]
        return None

    a_cmp = a_diff = 0
    lines_a, lines_b, lines_c, unmatched, unmarked, label = [], [], [], [], [], []
    b_words = b_marked = 0
    for s in secs:
        t = find(s)
        if s["rowname"] and norm_name(s["rowname"]) != norm_name(s["title"]) and \
                not norm_name(s["title"]).endswith(norm_name(s["rowname"])) and \
                not norm_name(s["rowname"]).endswith(norm_name(s["title"])):
            label.append("%-9s %-32s row named %r (p.%s)" % (s["sec"], s["title"], s["rowname"], s["page"]))
        if t is None:
            unmatched.append("%s %s (p.%s)" % (s["sec"], s["title"], s["page"]))
        else:
            a_cmp += 1
            if num(s["dflt"]) != num(t["dflt"]):
                a_diff += 1
                lines_a.append("A DIFFERS %-9s %-30s section %-8s (p.%s)  Table 14-1 %-8s at %s (p.%s)"
                               % (s["sec"], s["title"], s["dflt"], s["page"], t["dflt"], t["addr"], t["page"]))
        if s["type"] not in ("H1", "H2", "H4"):
            continue
        b_words += 1
        if not s["marks"]:
            unmarked.append("%s %s" % (s["sec"], s["title"]))
            continue
        b_marked += 1
        known = sum(1 << b for b in s["marks"])
        implied = sum(v << b for b, v in s["marks"].items())
        hd = num(s["dflt"])
        if isinstance(hd, int) and (hd & known) != implied:
            bad = sorted(b for b in s["marks"] if ((hd >> b) & 1) != s["marks"][b])
            lines_b.append("B DIFFERS %-9s %-30s header %-7s bit texts imply %-7s over mask %-7s; bits %s (p.%s)"
                           % (s["sec"], s["title"], s["dflt"], hex(implied), hex(known), bad, s["page"]))
        if t is not None:
            td = num(t["dflt"])
            if isinstance(td, int) and (td & known) != implied:
                bad = sorted(b for b in s["marks"] if ((td >> b) & 1) != s["marks"][b])
                lines_c.append("C DIFFERS %-9s %-30s Table 14-1 %-7s at %s (p.%s) against bit texts %-7s; bits %s"
                               % (s["sec"], s["title"], t["dflt"], t["addr"], t["page"], hex(implied), bad))
        if s["dup"]:
            lines_c.append("C SELF     %-9s %-30s a bit marked twice with different defaults: bits %s (p.%s)"
                           % (s["sec"], s["title"], sorted(set(s["dup"])), s["page"]))

    sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
    print("input: %s, sha256 %s" % (os.path.relpath(pdf, ROOT) if pdf.startswith(ROOT) else pdf, sha))
    for l in lines_a + lines_b + lines_c:
        print(l)
    print("label slips (row name differs from the section title):")
    for l in label:
        print("  " + l)
    print("A: %d chapter-14 parameters compared with Table 14-1, %d differ; %d sections not matched to a table row: %s"
          % (a_cmp, a_diff, len(unmatched), "; ".join(unmatched) or "none"))
    print("B/C: %d bit-field words, %d with at least one default mark, %d with none: %s"
          % (b_words, b_marked, len(unmarked), "; ".join(unmarked) or "none"))
    print("sections whose parameter row could not be parsed: %s" % ("; ".join(unparsed) or "none"))
    print("multi-row parameter tables not compared by name in A: %s" % ("; ".join(multirow) or "none"))


if __name__ == "__main__":
    main()
