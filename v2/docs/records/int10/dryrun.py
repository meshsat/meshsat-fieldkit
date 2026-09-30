#!/usr/bin/env python3
"""The dry run of the integration set 9 S-99 apply scripts on scratch copies (stream s99reg, MESHSAT-1357, 29 September
2026). NOT for the integrator's tree: it builds an overlay of the repository in a scratch folder and never writes in
the repository.

The overlay: every directory on the way to a file the scripts edit is a real directory whose other entries are symbolic
links to the repository; the edited files are real copies; `.git` is a link, so git can answer for commits. The scripts
run with `--root <overlay>` and their `write` refuses any path that resolves outside the overlay or through a link. It
runs, in the README's order: each script's --check, the script, the script again (it must refuse), then
rules_lib.py requirements from the overlay (so the registry, the decisions, the interfaces, the pages and the bindings
it checks are the overlay's). It asserts the repository's copies of the edited files are unchanged at the end.

Usage: python3 dryrun.py <scratch folder>   (the overlay is <scratch folder>/ov, rebuilt each time)"""
import hashlib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
EDITED = ["v2/ecad/tools/pcb_requirements.yaml", "v2/ecad/tools/pcb_decisions.yaml", "v2/ecad/tools/pcb_interfaces.yaml",
          "v2/docs/HW-FW-CONTRACT.md", "v2/docs/ASSEMBLY.md", "v2/docs/records/s98/README.md", "v2/docs/records/s98/LAYER-ROWS.md"]
ORDER = ["apply_rebind_generator_a_s99.py", "apply_s99_registry.py", "apply_decision_55.py", "apply_if_ab_power_s99.py",
         "apply_pages_s99.py"]


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def realize(ov, relp):
    """make ov/relp a real directory whose entries link to the repository's (recursively up to ov)"""
    if relp in ("", "."): return
    realize(ov, os.path.dirname(relp))
    d = os.path.join(ov, relp)
    if os.path.isdir(d) and not os.path.islink(d): return
    if os.path.islink(d): os.unlink(d)
    os.mkdir(d)
    src = os.path.join(REPO, relp)
    for e in os.listdir(src): os.symlink(os.path.join(src, e), os.path.join(d, e))


def build(scratch):
    ov = os.path.join(scratch, "ov")
    if not os.path.realpath(scratch).startswith(os.path.join(os.path.realpath(os.environ.get("WORKTREES", os.path.expanduser("~/worktrees/meshsat-fieldkit"))), "_scratch", "")):
        raise SystemExit("the scratch folder must be under _scratch/")
    if os.path.exists(ov): shutil.rmtree(ov)
    os.makedirs(ov)
    for e in os.listdir(REPO): os.symlink(os.path.join(REPO, e), os.path.join(ov, e))
    for f in EDITED:
        realize(ov, os.path.dirname(f))
        p = os.path.join(ov, f)
        os.unlink(p); shutil.copyfile(os.path.join(REPO, f), p)
        assert not os.path.islink(p)
    return ov


def run(cmd, label):
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    lines = (p.stdout + p.stderr).strip().split("\n")
    print("$ %s\n  exit %d; last line: %s" % (label, p.returncode, lines[-1] if lines else ""))
    return p.returncode, p.stdout + p.stderr


def main(argv):
    if len(argv) != 1: print(__doc__); return 2
    scratch = os.path.realpath(argv[0])
    before = {f: sha(os.path.join(REPO, f)) for f in EDITED}
    ov = build(scratch)
    print("overlay %s from %s" % (ov, REPO))
    rl = [sys.executable, os.path.join(ov, "v2/ecad/tools/rules_lib.py"), "requirements"]
    rc, out = run(rl, "rules_lib.py requirements (overlay, before the scripts)")
    for l in out.split("\n"):
        if l.startswith("ERROR") or l.startswith("warn"): print("    " + l[:200])
    ok = True
    for s in ORDER:
        sp = os.path.join(HERE, s)
        rc1, _ = run([sys.executable, sp, "--root", ov, "--check"], "%s --check" % s)
        rc2, o2 = run([sys.executable, sp, "--root", ov], s)
        for l in o2.strip().split("\n")[:-1]: print("    " + l[:300])
        rc3, _ = run([sys.executable, sp, "--root", ov], "%s (second run)" % s)
        ok &= rc1 == 0 and rc2 == 0 and rc3 != 0
    rc, out = run(rl, "rules_lib.py requirements (overlay, after the scripts)")
    for l in out.split("\n"):
        if l.startswith("ERROR") or l.startswith("warn"): print("    " + l[:200])
    ok &= rc == 0
    after = {f: sha(os.path.join(REPO, f)) for f in EDITED}
    same = before == after
    print("repository copies of the edited files unchanged: %s" % same)
    for f in EDITED:
        d = subprocess.run(["diff", "-u", os.path.join(REPO, f), os.path.join(ov, f)], capture_output=True, text=True).stdout
        n_add = sum(1 for l in d.split("\n") if l.startswith("+") and not l.startswith("+++"))
        n_del = sum(1 for l in d.split("\n") if l.startswith("-") and not l.startswith("---"))
        print("  %s: +%d -%d lines; overlay sha256/16 %s" % (f, n_add, n_del, sha(os.path.join(ov, f))[:16]))
        open(os.path.join(scratch, os.path.basename(f) + ".diff"), "w").write(d)
    print("DRY RUN %s" % ("PASSED" if ok and same else "FAILED"))
    return 0 if ok and same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
