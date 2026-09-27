"""List the sections (by heading) of a document that differ between HEAD and the working tree, with line numbers."""
import subprocess, sys
def secs(text):
    out = []; cur = ("(before the first heading)", 1); buf = []
    for i, l in enumerate(text.split("\n"), 1):
        if l.startswith("#"):
            out.append((cur, buf)); cur = (l.strip(), i); buf = []
        buf.append(l)
    out.append((cur, buf)); return out
for p in sys.argv[1:]:
    old = subprocess.run(["git", "show", "HEAD:" + p], capture_output=True, text=True).stdout
    new = open(p, encoding="utf-8").read()
    so, sn = secs(old), secs(new)
    assert [h[0] for h, _ in so] == [h[0] for h, _ in sn], p + ": headings changed"
    ch = [h for (h, a), (_, b) in zip(so, sn) if a != b]
    print(p, "changed sections:")
    for h, ln in ch: print("   line %d: %s" % (ln, h[:110]))
