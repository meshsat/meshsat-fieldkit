"""Replay the shell-made patches of pass 1 on the recovered files, in transcript order, in a staging copy.
Every python heredoc block of the listed entries is run with the old worktree path replaced by the staging root."""
import json, re, os, subprocess, sys, hashlib
SP = os.path.dirname(os.path.abspath(__file__))
RP = os.path.join(SP, "rp")
OLDW = "/tmp/claude-1000/-home-claude-runner-gitlab-products-meshsat-meshsat-fieldkit/3744628d-5552-4a03-8300-e043b6cdc9c8/scratchpad/wt/w5tray"
e = json.load(open(os.path.join(SP, "a1.json")))
def blocks(cmd):
    """(cwd relative to W, python source) for each `python3 - <<'EOF'` block, cwd from the last `cd $W...` before it."""
    out = []
    for m in re.finditer(r"python3 - <<'EOF'\n(.*?)\nEOF\n", cmd, re.S):
        pre = cmd[:m.start()]
        cds = re.findall(r"cd \$W(/[^\s&;]*)?", pre)
        cwd = (cds[-1] or "").lstrip("/") if cds else ""
        out.append((cwd, m.group(1)))
    return out
def run_block(n, k, cwd, src):
    src = src.replace(OLDW, RP)
    r = subprocess.run([sys.executable, "-"], input=src, text=True, capture_output=True, cwd=os.path.join(RP, cwd))
    print("entry %d block %d cwd %r: rc %d %s" % (n, k, cwd, r.returncode, (r.stdout + r.stderr).strip()[:300].replace("\n", " | ")))
    assert r.returncode == 0
def sh(n, line, cwd=""):
    r = subprocess.run(["bash", "-c", line], text=True, capture_output=True, cwd=os.path.join(RP, cwd))
    print("entry %d shell: rc %d %s" % (n, r.returncode, (r.stdout + r.stderr).strip()[:300].replace("\n", " | ")))
    assert r.returncode == 0
def h16(p): return hashlib.sha256(open(os.path.join(RP, p), "rb").read()).hexdigest()[:16]
PLAN = sys.argv[1:]
for step in PLAN:
    n = int(step)
    cmd = e[n]["cmd"]
    if n == 79:
        sh(n, r'''sed -i 's/"PC Blend 1.22 g\/cm3" if rho < 2 else "5052 2.68 g\/cm3"/"PC Blend 1.22 g\/cm3" if rho < 2e-3 else "5052 2.68 g\/cm3"/' v2/cad/lid_tray_qmx_r2.py''')
    elif n == 103:
        m = re.search(r"cat > \$W/v2/cad/build_lid_tray_r2.sh <<'EOF'\n(.*?\n)EOF\n", cmd, re.S)
        open(os.path.join(RP, "v2/cad/build_lid_tray_r2.sh"), "w").write(m.group(1)); os.chmod(os.path.join(RP, "v2/cad/build_lid_tray_r2.sh"), 0o755)
        print("entry 103: build_lid_tray_r2.sh written")
    elif n == 113:
        sh(n, r'''sed -i 's/    names = {ln.split(None, 1)\[1\] for ln in open(mf, encoding="utf-8") if ln.strip() and not ln.startswith("#")}/    names = {ln.split(None, 1)[1].strip() for ln in open(mf, encoding="utf-8") if ln.strip() and not ln.startswith("#")}/' v2/ecad/tools/tests/test_lid_tray_qmx_r2.py''')
    elif n == 118:
        sh(n, r'''sed -i 's#lid-tray-qmx-r2-readback#.lid-tray-qmx-r2-readback#g' v2/cad/build_lid_tray_r2.sh v2/cad/README.md && sed -i 's#(read the two PNGs in \.lid-tray-qmx-r2-readback/ before releasing)#(read the two PNGs in .lid-tray-qmx-r2-readback/ before releasing; case_manifest.py skips that dot folder)#' v2/cad/build_lid_tray_r2.sh''')
        for k, (cwd, src) in enumerate(blocks(cmd)): run_block(n, k, "", src)
    else:
        bl = blocks(cmd)
        assert bl, n
        for k, (cwd, src) in enumerate(bl): run_block(n, k, cwd, src)
    if n in (88, 98, 124, 160):
        for p in ("v2/cad/lid_tray_qmx_r2.py", "v2/cad/lid_tray_qmx_r2_check.py", "v2/cad/lid_tray_qmx_r2_drawing.py", "v2/vendor/qrp-labs/measure_qmx_figures.py"):
            print("   after %d: %s %s" % (n, h16(p), p))
