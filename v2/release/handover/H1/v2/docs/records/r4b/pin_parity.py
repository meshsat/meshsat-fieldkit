# W6 scratch, 25 Sep 2026: compare gen_sch_b.py H743 pin table (round 4 copy of W6's script) with an ST LQFP100 pinout page.
# Usage: pdftotext -f 55 -l 55 -bbox <datasheet.pdf> page.html; python3 lqfp100_pin_parity.py page.html v2/ecad/tools/gen_sch_b.py
# Page 55 is Figure 5 (DS12110 Rev 10, STM32H743) and Figure 4 (DS12117 Rev 9, STM32H753). Reads the page by word coordinates.
import re, sys, ast
html = open(sys.argv[1]).read()
W = [(float(a),float(b),float(c),float(d),t) for a,b,c,d,t in re.findall(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)', html)]
nums = [w for w in W if w[1] < 700 and re.fullmatch(r'\d{1,3}', w[4]) and 1 <= int(w[4]) <= 100]
names = [w for w in W if not re.fullmatch(r'\d{1,3}', w[4])]
cx = lambda w: (w[0]+w[2])/2; cy = lambda w: (w[1]+w[3])/2
res = {}
# numbers along top row (76..100) and bottom (26..50) are horizontal text; sides (1..25, 51..75) share a line with the name
for n in nums:
    k = int(n[4])
    if 1 <= k <= 25:   # left side: name immediately left on the same line
        cand = [w for w in names if abs(cy(w)-cy(n)) < 3 and w[2] <= n[0]+1]
        cand.sort(key=lambda w: n[0]-w[2]); res[k] = cand[0][4] if cand else None
    elif 51 <= k <= 75:
        cand = [w for w in names if abs(cy(w)-cy(n)) < 3 and w[0] >= n[2]-1]
        cand.sort(key=lambda w: w[0]-n[2]); res[k] = cand[0][4] if cand else None
    else:  # rotated names: vertical labels share the column x
        cand = [w for w in names if abs(cx(w)-cx(n)) < 4 and w[4] not in ('100-pins',)]
        # top row: names above the numbers; bottom row: names below
        if 76 <= k <= 100: cand = [w for w in cand if cy(w) < cy(n)]
        else: cand = [w for w in cand if cy(w) > cy(n)]
        cand.sort(key=lambda w: abs(cy(w)-cy(n))); res[k] = cand[0][4] if cand else None
norm = lambda s: (s or '').split('-')[0]
src = open(sys.argv[2]).read()
m = re.search(r'^H743 = (\{.*?\})$', src, re.M)
gen = ast.literal_eval(m.group(1))
bad = [(k, gen.get(k), res.get(k)) for k in range(1,101) if norm(res.get(k)) != gen.get(k)]
print("pins parsed:", sum(1 for k in range(1,101) if res.get(k)), "mismatches:", bad)
