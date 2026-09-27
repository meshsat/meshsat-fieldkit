# List every part() call in gen_sch_*.py whose lib/symbol or value looks like a diode (not LED).
import ast, sys, glob, re, os
root = sys.argv[1]
KEY = re.compile(r"TVS|Zener|Schottky|D_|USBLC|TPD\d|PRTR|ESD|RCLAMP|PESD|SMBJ|SMCJ|SMAJ|BAT54|SS\d\d|1N\d{4}|MBR|B5819|MMSZ|BZT|diode", re.I)
for f in sorted(glob.glob(os.path.join(root, "v2/ecad/tools/gen_sch_*.py"))):
    src = open(f).read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) == "part":
            seg = ast.get_source_segment(src, node)
            args = node.args
            try:
                lib = ast.literal_eval(args[1]); sym = ast.literal_eval(args[2]); val = ast.literal_eval(args[3])
            except Exception:
                lib = sym = val = "?"
            txt = "%s %s %s" % (lib, sym, val)
            if "LED" in sym.upper() or "LED" in str(val)[:6].upper():
                continue
            if KEY.search(txt):
                print("%s:%d\t%s" % (os.path.basename(f), node.lineno, seg.replace("\n", " ")[:400]))
