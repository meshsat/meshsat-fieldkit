#!/usr/bin/env python3
"""How the w5si stream was rebuilt from its transcripts on 27 September 2026 (MESHSAT-1357). A record, kept so the
recovery can be repeated and checked; it is not a tool of the pipeline.

Pass 1 of the stream wrote in a worktree under /tmp, committed nothing, and a reboot deleted the worktree. What
survived is under /home/claude-runner/worktrees/meshsat-fieldkit/_recovered/w5si-author-1/: the files the author wrote
with the Write tool (tree/), the Edit tool calls whose base file was not held (EDITS-NOT-APPLIED.txt, six of them),
and bash.log, every shell command with its output. The author changed edge_length.py, pcb_edge_rates.yaml, the test
file and three drafts mostly through Python patch scripts run from the shell, each asserting its old text; those
scripts are in bash.log whole, so they are run again here, in the transcript's order, on a staging copy laid out as
the lost worktree was.

Usage: replay.py <staging dir> <worktree at c23c5e76>      (writes only under the staging directory)

The order, and how each step's place in it is known:
  * the three Edit calls on edge_length.py come first: command 74's patch asserts text that only they introduce;
  * commands 74, 75, 78, 85, 88, 89, 94, 97, 98, 111, 113, 114, 115, 118, 119 in the transcript's order;
  * the Edit call on test_edge_length.py sits between 119 and 120: its old text is command 113's, and command 120's
    patch asserts text the Edit introduces;
  * commands 120, 121, 131, 132, 136, 137, 138, 149;
  * command 156 renamed apply_board_b_rf_classes.py to apply_board_b_declarations.py; its Python raised SyntaxError
    in the transcript and changed nothing, so it is not run; the two Edit calls on the renamed draft follow it, and
    command 157's patch asserts their text;
  * THE CHECK: command 158 printed the sha256/16 of three files at that point, and the replay must give the same;
  * command 160 (a comment block of edge_length.py and one line of the record).
"""
import sys, os, re, json, subprocess, hashlib

REC = "/home/claude-runner/worktrees/meshsat-fieldkit/_recovered/w5si-author-1"
OLDSP = ("/tmp/claude-1000/-home-claude-runner-gitlab-products-meshsat-meshsat-fieldkit/"
         "3744628d-5552-4a03-8300-e043b6cdc9c8/scratchpad")
OLDWT = OLDSP + "/wt/w5si"
T, D = "v2/ecad/tools", "drafts/w5si"
AT_158 = {T + "/pcb_edge_rates.yaml": "26ef827a1d9ff277", T + "/edge_length.py": "ea1b2211c8ff4f7a",
          T + "/ibis_read.py": "8fd2e9d1f6cb1f4c"}


def commands(path):
    """[{"desc", "cmd", "out"}] of a bash.log: '### description', '$ command', '--- result', output."""
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    cmds, cur, state = [], None, None
    for n, ln in enumerate(lines, 1):
        if ln.startswith("### ") and (n == 1 or lines[n - 2] == "") and n < len(lines) and lines[n].startswith("$ "):
            cur = {"desc": ln[4:], "cmd": [], "out": []}; cmds.append(cur); state = "desc"; continue
        if cur is None: continue
        if state == "desc" and ln.startswith("$ "): cur["cmd"].append(ln[2:]); state = "cmd"; continue
        if state == "cmd":
            if ln == "--- result": state = "out"; continue
            cur["cmd"].append(ln); continue
        if state == "out": cur["out"].append(ln)
    for c in cmds:
        c["cmd"] = "\n".join(c["cmd"]); c["out"] = "\n".join(c["out"]).rstrip("\n")
    return cmds


def heredocs(cmd):
    out, lines, i = [], cmd.split("\n"), 0
    while i < len(lines):
        m = re.search(r"<<-?\s*'?(\w+)'?", lines[i])
        if m:
            j, body = i + 1, []
            while j < len(lines) and lines[j].strip() != m.group(1): body.append(lines[j]); j += 1
            out.append((lines[i], "\n".join(body) + "\n")); i = j + 1
        else: i += 1
    return out


def edits():
    t = open(os.path.join(REC, "EDITS-NOT-APPLIED.txt"), encoding="utf-8").read()
    out = []
    for blk in t.split("\n=====\n"):
        if not blk.strip(): continue
        m = re.match(r"FILE (.*)\n--- old\n(.*)\n--- new\n(.*)\Z", blk, re.S)
        out.append((m.group(1).replace(OLDWT + "/", ""), m.group(2), m.group(3)))
    return out


def main(stg, wt):
    C = commands(os.path.join(REC, "bash.log"))
    assert len(C) == 168, len(C)
    E = edits()
    assert len(E) == 6
    sha = lambda p: hashlib.sha256(open(os.path.join(stg, p), "rb").read()).hexdigest()[:16]
    for d in (T + "/tests", "v2/vendor", D): os.makedirs(os.path.join(stg, d), exist_ok=True)
    for p in (T + "/edge_length.py", T + "/tests/test_edge_length.py"):
        r = subprocess.run(["git", "-C", wt, "show", "c23c5e76:" + p], capture_output=True, check=True)
        open(os.path.join(stg, p), "wb").write(r.stdout)
    for p in (T + "/ibis_read.py", T + "/pcb_edge_rates.yaml"):
        open(os.path.join(stg, p), "wb").write(open(os.path.join(REC, "tree", p), "rb").read())
    for f in os.listdir(os.path.join(REC, "tree", D)):
        open(os.path.join(stg, D, f), "wb").write(open(os.path.join(REC, "tree", D, f), "rb").read())

    def ed(i):
        f, old, new = E[i]
        p = os.path.join(stg, f)
        s = open(p, encoding="utf-8").read()
        assert s.count(old) == 1, "edit %d: its old text is in %s %d time(s)" % (i + 1, f, s.count(old))
        assert old != new
        open(p, "w", encoding="utf-8").write(s.replace(old, new))
        print("edit %d applied to %s" % (i + 1, f))

    def py(k, cwd):
        intro, body = heredocs(C[k]["cmd"])[0]
        assert "python3 -" in intro
        body = body.replace(OLDWT, stg)
        assert OLDSP not in body
        r = subprocess.run([sys.executable, "-"], input=body, text=True, capture_output=True, cwd=os.path.join(stg, cwd))
        assert r.returncode == 0, (k, r.stderr[-400:])
        print("command %d (%s): %s" % (k, C[k]["desc"], r.stdout.strip()[:80]))

    def sed(k, cwd, target):
        m = re.search(r"sed -i '((?:[^'])*)' ([^\s;]+)", C[k]["cmd"])
        assert m and m.group(2) == target
        p = os.path.join(stg, cwd, target)
        before = open(p).read()
        subprocess.run(["sed", "-i", m.group(1), target], cwd=os.path.join(stg, cwd), check=True)
        assert open(p).read() != before, "command %d's sed changed nothing" % k
        print("command %d (%s): sed on %s" % (k, C[k]["desc"], target))

    ed(0); ed(1); ed(2)
    for k in (74, 75, 78, 85, 88): py(k, T)
    sed(89, T, "pcb_edge_rates.yaml")
    for k in (94, 97, 98, 111): py(k, T)
    intro, body = heredocs(C[113]["cmd"])[0]
    assert intro.startswith("cat >> ") and intro.rstrip().endswith("tests/test_edge_length.py <<'PYEOF'")
    open(os.path.join(stg, T, "tests/test_edge_length.py"), "a", encoding="utf-8").write(body)
    print("command 113: %d characters appended to the test file" % len(body))
    sed(114, T, "tests/test_edge_length.py")
    for k in (115, 118, 119): py(k, T)
    ed(3)
    py(120, T + "/tests")
    sed(121, T, "pcb_edge_rates.yaml")
    py(131, D)
    for k in (132, 136, 137, 138): py(k, T)
    sed(149, D, "apply_coverage_si001.py")
    os.rename(os.path.join(stg, D, "apply_board_b_rf_classes.py"), os.path.join(stg, D, "apply_board_b_declarations.py"))
    ed(4); ed(5)
    py(157, D)
    bad = 0
    for p, want in sorted(AT_158.items()):
        got = sha(p)
        print("%s: sha256/16 %s, the transcript's command 158 printed %s: %s" % (p, got, want, "IDENTICAL" if got == want else "DIFFERENT"))
        bad += got != want
    py(160, ".")
    for p in (T + "/edge_length.py", T + "/tests/test_edge_length.py", T + "/pcb_edge_rates.yaml", T + "/ibis_read.py"):
        print("final %s %s" % (p, sha(p)))
    for f in sorted(os.listdir(os.path.join(stg, D))): print("final %s/%s %s" % (D, f, sha(D + "/" + f)))
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) != 3: print(__doc__); sys.exit(2)
    sys.exit(main(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])))
