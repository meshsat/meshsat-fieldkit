#!/usr/bin/env python3
"""Re-read every page citation of the review's ledger (section 8): for each row, extract the cited PDF pages with
pdftotext and look for every verbatim quote ("...") and every decimal figure of the "what is quoted" cell on them.
A parse of the markdown table, not a grep of prose: the rows are read from the table under the heading."""
import os, re, subprocess, sys
review, vendor = sys.argv[1], sys.argv[2]
txt = open(review, encoding="utf-8").read()
sec = txt.split("## 8. The ratings ledger")[1].split("## 9.")[0]
rows = [l for l in sec.splitlines() if l.startswith("| ") and not l.startswith("| part") and not l.startswith("|---")]
doc = None
def norm(s):
    return re.sub(r"\s+", " ", s.replace("±", "+-").replace("\u2013", "-").replace("−", "-").replace("µ", "u").replace("μ", "u").replace("Ω", "ohm")).lower()
bad = 0
for row in rows:
    cells = [c.strip() for c in row.strip().strip("|").split("|")]
    part, docc, pages, quoted = cells
    m = re.search(r"`([^`]+)`", docc)
    if m: doc = m.group(1)
    if not doc or not doc.endswith(".pdf") or not pages.strip():
        print("SKIP  %-28s %-45s pages %r" % (part[:28], doc, pages)); continue
    path = os.path.join(vendor, doc)
    if not os.path.exists(path): print("MISSING %s" % doc); bad += 1; continue
    pg = [int(x) for x in re.findall(r"\d+", pages)]
    text = ""
    for n in pg:
        text += subprocess.run(["pdftotext", "-layout", "-f", str(n), "-l", str(n), path, "-"], capture_output=True, text=True).stdout
    nt = norm(text)
    quotes = re.findall(r'"([^"]+)"', quoted)
    nums = sorted(set(re.findall(r"\d+\.\d+", quoted)))
    def present(q):
        # "..." is an elision in the review's quote: every piece around it must be on the page, in order
        pieces = [norm(x).strip() for x in q.split("...") if x.strip()]
        pos = 0
        for pc in pieces:
            i = nt.find(pc, pos)
            if i < 0: return False
            pos = i + len(pc)
        return True
    miss_q = [q for q in quotes if not present(q)]
    miss_n = [x for x in nums if x not in nt]
    flag = "ok  " if not (miss_q or miss_n) else "LOOK"
    if flag == "LOOK": bad += 1
    print("%s %-28s %-42s p.%-8s quotes %d/%d figures %d/%d%s%s" % (flag, part[:28], doc.split("/")[-1][:42], pages[:8], len(quotes) - len(miss_q), len(quotes), len(nums) - len(miss_n), len(nums),
          ("  MISSING QUOTES: " + " | ".join(q[:60] for q in miss_q)) if miss_q else "", ("  MISSING FIGURES: " + ", ".join(miss_n)) if miss_n else ""))
print("rows to look at:", bad)
