#!/usr/bin/env python3
"""cmp_gen_sch_a.py (stream s119, S-119, MESHSAT-1357, 29 September 2026): energy_4s6p.py parses three calls of
v2/ecad/tools/gen_sch_a.py (the VHEAT and VHEAT_IN rails and the U22 efuse) and pins the file by sha256. Set 12's S-117
edits (decisions 56 and 57) moved the file from eb2e347e (commit c74d6129) to 6a136fee (e553e43a), so energy_4s6p.py
refused to run on this line before any change of this stream. This compares those three calls as ast dumps between two
copies of the file and prints IDENTICAL or DIFFERENT for each; energy_4s6p.py is re-pinned only on ALL IDENTICAL.
Usage (repository root): git show c74d6129:v2/ecad/tools/gen_sch_a.py > /tmp/pinned.py;
python3 v2/docs/records/s119/cmp_gen_sch_a.py /tmp/pinned.py v2/ecad/tools/gen_sch_a.py"""
import ast, sys
def calls(path, names, first):
    tree = ast.parse(open(path, encoding="utf-8").read())
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nm in names and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value == first:
                hits.append(ast.dump(node, include_attributes=False))
    return hits
a, b = sys.argv[1], sys.argv[2]
ok = True
for names, first in (({"rail"}, "VHEAT"), ({"rail"}, "VHEAT_IN"), ({"efuse"}, "U22")):
    x, y = calls(a, names, first), calls(b, names, first)
    same = x == y and len(x) == 1
    ok &= same
    print(first, len(x), len(y), "IDENTICAL" if same else "DIFFERENT")
print("ALL IDENTICAL" if ok else "NOT IDENTICAL")
