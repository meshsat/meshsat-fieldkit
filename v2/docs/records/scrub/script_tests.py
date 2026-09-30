#!/usr/bin/env python3
"""Each script the scrub changed still runs (MESHSAT-1357, 30 September 2026). A record of the scrub, not a tool.

apply_scrub.py replaced a typed-in path by a derived one in ten scripts (records of past sessions, a checker's script
and two V1 CAD scripts). This runs each one in a sandbox under <worktrees>/_scratch/ and prints what it did, with every
path written as scrub_lib writes it. It never writes in the repository or in another worktree, never reaches the
rented box (BOX_BIN points at stubs that only log) and removes the sandbox at the end. Where the filed script can run
too (w5si's replay, cx1's phase 1), the two outputs are compared line by line. A script whose inputs were never filed
(w5tray's replay needs its transcript entries, a1.json) is run as filed, where it stops at the same place as before,
and on a two-line fixture that exercises the derived path.

Usage: python3 script_tests.py    exit 1 if any test failed. Its output is script_tests.out beside it.
"""
import json, os, shutil, subprocess, sys, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_lib as S

TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
WT = os.environ.get("WORKTREES", os.path.expanduser("~/worktrees/meshsat-fieldkit"))
SB = os.path.join(WT, "_scratch", "scrub-tests")
BASE = "8fec0733"
R = "v2/docs/records/"
results = []


def norm(s):
    s = s.replace(SB, "<sandbox>")
    return S.redact(s.replace(TOP, "<this worktree>"))[0]


def run(cmd, env=None, cwd=None, timeout=900):
    e = dict(os.environ); e.update(env or {})
    p = subprocess.run(cmd, capture_output=True, text=True, env=e, cwd=cwd or SB, timeout=timeout)
    return p.returncode, norm(p.stdout + p.stderr)


def report(name, ok, what, out, keep=8):
    results.append(ok)
    print("%s  %s: %s" % ("PASS" if ok else "FAIL", name, what))
    for l in [l for l in out.strip().split("\n") if l.strip()][-keep:]: print("      " + l[:200])


def stubs():
    d = os.path.join(SB, "boxbin"); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "bxs.sh"), "w").write('#!/bin/bash\necho "stub bxs.sh: $*" >> "%s/box.log"\n' % SB)
    open(os.path.join(d, "bxcp.sh"), "w").write(textwrap.dedent('''\
        #!/bin/bash
        echo "stub bxcp.sh: $*" >> "%s/box.log"
        if [ "$1" = from ]; then d=$(mktemp -d); mkdir -p $d/pack; echo x > $d/pack/x
          (cd $d/pack && sha256sum x > SHA256SUMS); tar cf "$3/pack.tar" -C $d pack; rm -rf $d; fi
        ''' % SB))
    for f in ("bxs.sh", "bxcp.sh"): os.chmod(os.path.join(d, f), 0o755)
    return d


def git_status(p):
    return subprocess.run(["git", "-C", p, "status", "--porcelain"], capture_output=True, text=True).stdout


def main():
    if os.path.exists(SB): shutil.rmtree(SB)
    os.makedirs(SB)
    box = stubs()
    # 1. d6dec/box/to_box.sh: bundles the real d6dec worktree's branch (read only), the box calls go to the stubs
    rc, out = run(["bash", os.path.join(TOP, R, "d6dec/box/to_box.sh"), "t1"], {"BOX_BIN": box, "SCRATCH": SB})
    bundle = os.path.join(SB, "bx", "d6dec-t1.bundle")
    log = norm(open(os.path.join(SB, "box.log")).read()) if os.path.exists(os.path.join(SB, "box.log")) else ""
    report("d6dec/box/to_box.sh", rc == 0 and os.path.exists(bundle) and log.count("stub ") == 3,
           "exit %d; the bundle of fnd/d6dec written under $SCRATCH; %d box call(s) reached the stubs" % (rc, log.count("stub ")),
           out + "\n" + log)
    # 2. int7/box/int7_install_pack.sh: fetch through the stubs, the pack's checksum checked, then the HEAD refusal (the
    #    int7 worktree is not at a4b157f0), so nothing is installed; the worktree's status is compared before and after
    int7 = os.path.join(WT, "int7"); st0 = git_status(int7)
    rc, out = run(["bash", os.path.join(TOP, R, "int7/box/int7_install_pack.sh")], {"BOX_BIN": box, "SCRATCH": SB})
    report("int7/box/int7_install_pack.sh", rc == 3 and "int7 is not at a4b157f0" in out and git_status(int7) == st0,
           "exit %d; the pack fetched through the stubs and its checksum checked, then the refusal at the HEAD check; "
           "the int7 worktree unchanged" % rc, out)
    # 3. r8int6/commit_r8int6.sh: a sandbox repository, the message filler and the validator stubbed; the pre-commit
    #    check is found by its default, beside the sandbox clone, where a stub logs the call
    sp = os.path.join(SB, "r8"); rr = os.path.join(sp, "r8int6"); w = os.path.join(sp, "wt", "r8int6")
    for d in ("common", "msg", "kit/s1", ): os.makedirs(os.path.join(rr, d), exist_ok=True)
    for d in ("ecad", "docs", "vendor"): os.makedirs(os.path.join(w, "v2", d))
    os.makedirs(os.path.join(sp, "wt", "scripts"))
    open(os.path.join(rr, "common", "fill_msg_r8int6.py"), "w").write(
        "import sys\nopen(sys.argv[4], 'w').write(open(sys.argv[1]).read().replace('BASE', sys.argv[3]))\n")
    open(os.path.join(rr, "msg", "s1.tmpl"), "w").write("docs(test): a sandbox commit on BASE [MESHSAT-1357]\n")
    open(os.path.join(rr, "kit", "s1", "ids_r8int6.json"), "w").write("{}")
    open(os.path.join(rr, "validate.sh"), "w").write("#!/bin/bash\necho 'stub validate: rc=0'\n")
    os.chmod(os.path.join(rr, "validate.sh"), 0o755)
    open(os.path.join(sp, "wt", "scripts", "pre-commit-check.sh"), "w").write(
        '#!/bin/bash\ncat > /dev/null\necho "stub pre-commit-check: $*"\necho "pre-commit-check: PASSED"\n')
    subprocess.run(["git", "init", "-q", w], check=True)
    for d in ("ecad", "docs", "vendor"): open(os.path.join(w, "v2", d, "f.txt"), "w").write("x\n")
    rc, out = run(["bash", os.path.join(TOP, R, "r8int6/commit_r8int6.sh"), "s1", "abc12345"], {"SP": sp})
    report("r8int6/commit_r8int6.sh", rc == 0 and "sandbox commit on abc12345" in out and "stub validate" in out,
           "exit %d; the pre-commit check found beside the sandbox's main clone by the derived default, the commit made "
           "in the sandbox repository" % rc, out)
    # 4. r8int6/copy_evidence.sh: the main clone derived from the script's own repository; main's ignored files copied
    #    into a sandbox git repository
    sp = os.path.join(SB, "ce"); w = os.path.join(sp, "wt", "r8int6"); os.makedirs(os.path.join(sp, "r8int6"))
    subprocess.run(["git", "init", "-q", w], check=True)
    rc, out = run(["bash", os.path.join(TOP, R, "r8int6/copy_evidence.sh")], {"SP": sp})
    n = sum(len(f) for _, _, f in os.walk(os.path.join(w, "v2")))
    report("r8int6/copy_evidence.sh", rc == 0 and n > 0 and "to copy:" in out,
           "exit %d; %d file(s) copied from the main clone found by git into the sandbox" % (rc, n), out, keep=3)
    # 5. int10/dryrun.py: a scratch folder outside _scratch/ is refused; one inside runs the dry run on its overlay
    rc, out = run([sys.executable, os.path.join(TOP, R, "int10/dryrun.py"), os.path.join(SB, "..", "..", "scrub-outside")])
    report("int10/dryrun.py (outside)", rc != 0 and "must be under _scratch/" in out, "exit %d; refused" % rc, out, keep=2)
    # the filed script sits beside this one for the comparison (its apply scripts are found beside it), then goes
    filed = os.path.join(TOP, R, "int10", "_filed_dryrun.py")
    open(filed, "w").write(subprocess.run(["git", "-C", TOP, "show", "%s:%sint10/dryrun.py" % (BASE, R)], capture_output=True, check=True).stdout.decode())
    try:
        rc0, out0 = run([sys.executable, filed, os.path.join(SB, "dry")])
    finally:
        os.remove(filed)
    rc, out = run([sys.executable, os.path.join(TOP, R, "int10/dryrun.py"), os.path.join(SB, "dry")])
    report("int10/dryrun.py (inside)", "overlay <sandbox>/dry/ov from <this worktree>" in out and (rc, out) == (rc0, out0),
           "exit %d; the overlay built under the sandbox and every stage run, the output equal to the filed script's: %s "
           "(both end DRY RUN FAILED today: the S-99 scripts were applied on 29 September and refuse)" % (rc, (rc, out) == (rc0, out0)), out, keep=3)
    # 6. w5si/recovery/replay.py: the filed script and this one, each on its own staging copy, compared
    outs = []
    for tag, src in (("filed", subprocess.run(["git", "-C", TOP, "show", "%s:%sw5si/recovery/replay.py" % (BASE, R)], capture_output=True, check=True).stdout.decode()),
                     ("now", open(os.path.join(TOP, R, "w5si/recovery/replay.py")).read())):
        f = os.path.join(SB, "replay-w5si-%s.py" % tag); open(f, "w").write(src)
        stg = os.path.join(SB, "stg-" + tag); os.makedirs(stg)
        rc, out = run([sys.executable, f, stg, TOP])
        outs.append((rc, out.replace("stg-" + tag, "stg")))
    same = outs[0] == outs[1]
    report("w5si/recovery/replay.py", same and outs[1][0] == 0 and outs[1][1].count("IDENTICAL") == 3,
           "exit %d; the output equals the filed script's line for line: %s; three IDENTICAL at command 158" % (outs[1][0], same),
           outs[1][1], keep=4)
    # 7. w5tray/recovery/replay.py: as filed and now, both stop at the transcript entries that were never filed; on a
    #    fixture the derived path is found in the entries and replaced by the staging root
    for tag, src in (("filed", subprocess.run(["git", "-C", TOP, "show", "%s:%sw5tray/recovery/replay.py" % (BASE, R)], capture_output=True, check=True).stdout.decode()),
                     ("now", open(os.path.join(TOP, R, "w5tray/recovery/replay.py")).read())):
        d = os.path.join(SB, "w5tray-" + tag); os.makedirs(d); open(os.path.join(d, "replay.py"), "w").write(src)
        rc, out = run([sys.executable, os.path.join(d, "replay.py"), "0"])
        outs.append((rc, "a1.json" in out and "FileNotFoundError" in out))
    report("w5tray/recovery/replay.py (as filed)", outs[-1] == outs[-2] and outs[-1][1],
           "the filed script and this one stop at the same place: the transcript entries (a1.json) were never filed", "")
    d = os.path.join(SB, "w5tray-fixture"); os.makedirs(os.path.join(d, "rp", "v2"))
    shutil.copy(os.path.join(TOP, R, "w5tray/recovery/replay.py"), d)
    json.dump([{"cmd": "cd $W/v2 && python3 - <<'EOF'\nimport os\nprint(os.path.isdir('/tmp/fixture-session/s1/scratchpad/wt/w5tray/v2'))\nEOF\n"}],
              open(os.path.join(d, "a1.json"), "w"))
    rc, out = run([sys.executable, os.path.join(d, "replay.py"), "0"])
    report("w5tray/recovery/replay.py (fixture)", rc == 0 and "rc 0 True" in out,
           "exit %d; the old worktree path read from the entries and replaced by the staging root" % rc, out, keep=2)
    # 8. cx1/checks/check-1-phase1.py: the filed script and this one on the cx1 worktree, compared
    outs = []
    for tag, src in (("filed", subprocess.run(["git", "-C", TOP, "show", "%s:%scx1/checks/check-1-phase1.py" % (BASE, R)], capture_output=True, check=True).stdout.decode()),
                     ("now", open(os.path.join(TOP, R, "cx1/checks/check-1-phase1.py")).read())):
        f = os.path.join(SB, "cx1-%s.py" % tag); open(f, "w").write(src)
        outs.append(run([sys.executable, f]))
    report("cx1/checks/check-1-phase1.py", outs[0] == outs[1] and outs[1][0] == 0,
           "exit %d; %d line(s), equal to the filed script's output: %s" % (outs[1][0], outs[1][1].count("\n"), outs[0] == outs[1]),
           outs[1][1], keep=2)
    # 9. v1/cad: FreeCAD is not on the runner; with stand-in modules the scripts run against a sandbox home
    home = os.path.join(SB, "home"); os.makedirs(home)
    shim = os.path.join(SB, "freecad_shim.py")
    open(shim, "w").write(textwrap.dedent('''\
        import runpy, sys, time
        from unittest import mock
        calls = []
        for m in ("FreeCAD", "FreeCADGui", "Import", "ImportGui"):
            mod = mock.MagicMock(name=m); sys.modules[m] = mod
        sys.modules["Import"].open.side_effect = lambda p: calls.append(("Import.open", p))
        sys.modules["ImportGui"].open.side_effect = lambda p: calls.append(("ImportGui.open", p))
        time.sleep = lambda s: None
        try:
            runpy.run_path(sys.argv[1], run_name="__main__")
        except SystemExit as e:
            print("exit", e.code)
        print("calls", calls)
        '''))
    for f, want in (("v1/cad/inspect_doc.py", "Import.open"), ("v1/cad/render.py", "ImportGui.open")):
        rc, out = run([sys.executable, shim, os.path.join(TOP, f)], {"HOME": home}, timeout=300)
        ok = rc == 0 and ("'%s', '<sandbox>/home/Downloads/field_kit/field_kit.step'" % want) in out
        if f.endswith("render.py"): ok = ok and os.path.isdir(os.path.join(home, "Downloads", "field_kit", "renders"))
        report(f, ok, "exit %d; the STEP path derived from the home directory%s" % (
            rc, ", the render folder made under it" if f.endswith("render.py") else ""), out, keep=2)
    shutil.rmtree(SB)
    print("script_tests: %d of %d passed; sandbox removed" % (sum(results), len(results)))
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
