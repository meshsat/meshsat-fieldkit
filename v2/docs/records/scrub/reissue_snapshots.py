#!/usr/bin/env python3
"""The four handover snapshots reissued as redaction versions (MESHSAT-1357, 30 September 2026).

The owner's words of 29 September 2026: "Reissue affected handover snapshots with new version records and hashes rather
than silently modifying accepted releases. This instruction does not authorize rewriting Git history." H1, H1.1, H2 and
H3 each carry, in a few of their files, the runner's path, a session scratch path, the runner's host name or the
laptop's host name. None of them is edited: each stays in v2/release/handover/ byte for byte as published. Each gets a
NEW version beside it, <V>-R1, built the way the snapshots were built, so the reissue is reproducible:

  1. A REDACTION COMMIT whose only parent is the snapshot's own source commit (named in its SOURCE.txt). Its tree is the
     source commit's tree with (a) every bundled file that carries a pattern and that the tree's scrub redacts, redacted
     by the same function (scrub_lib.redact), and (b) v2/docs/handover/START-HERE.md opened by a box that names the
     version it supersedes, why, each changed file with its sha256/16 before and after, and each file left as it was
     with the reason. A file the tree's scrub leaves (apply_scrub.LEFT: a record cited by sha, a reading a bound page
     cites) is left here too, so every hash a page of the snapshot cites for it still holds. The commit is made with git
     plumbing (no checkout), as the owner, with a fixed date, so a second run makes the same commit id. Its diff goes
     through the repository's pre-commit check like any commit.
  2. THE BUILD: v2/ecad/tools/handover_pack.py build --commit <redaction commit> --version <V>-R1 --zip-only, the packer
     that built H3 (sha256 fd7e353f...), which reproduces H1, H1.1, H2 and H3 byte for byte from their source commits
     except SOURCE.txt (records/scrub/README.md, "Reproducibility"). Then handover_pack.py verify, and three assertions:
     every MANIFEST.tsv row equals the superseded snapshot's except the changed files, START-HERE (root copy and source)
     and SOURCE.txt; every entry of the new ZIP that carries a pattern is a file the tree leaves; the ZIP is under the
     spec's cap.
  3. THE RECORDS: v2/docs/handover/RELEASE-<V>-R1.md, the version record, and records/scrub/map_reissue.tsv, every
     replacement by snapshot, file, line and token class.
The redaction commits are not on any branch when this runs: the integrating commit records them in main's history with
a merge that keeps main's tree (git merge -s ours), so the snapshot's commit is public once main is.

`commits` sends each redaction commit's diff through the repository's pre-commit check: $PRECOMMIT_CHECK when it is set,
else scripts/pre-commit-check.sh in the folder that holds the main clone (found from git's common directory, as
r8int6/commit_r8int6.sh finds it). A clone elsewhere sets the variable.

Usage: python3 reissue_snapshots.py commits          make (or re-make, the same ids) the four redaction commits
       python3 reissue_snapshots.py build [--out D]  build, verify and compare, write the records (default out:
                                                     v2/release/handover of this worktree)
"""
import csv, hashlib, io, json, os, re, subprocess, sys, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_lib as S
import apply_scrub as A

TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
PACK = os.path.join(TOP, "v2/ecad/tools/handover_pack.py")
HO = "v2/release/handover"
TODAY = "30 September 2026"
DATE = "2026-09-30T08:00:00+02:00"
OWNER = ("Kyriakos Papadopoulos", "ncpjfuzl@mxmx.email")
SNAPS = [("H1", "8a19fe295f4f77b67366854d1006e1feff228fef"), ("H1.1", "98ce9f83269ef61d21b317d8eabbdf35a878923e"),
         ("H2", "b89b50b4421fd882967b390a09c21dbd307ca98e"), ("H3", "75ad6ee5bc98d7213b9a61d1f64cfa7ea19cc669")]
SH = "v2/docs/handover/START-HERE.md"
RECORD = {"H1": "H1's own `START-HERE.md` and `LAYER-STATUS.md` (H1 has no release page)",
          "H1.1": "H1.1's own `START-HERE.md`, `LAYER-STATUS.md` and `v2/docs/handover/H1.1-RESPONSE.md` (H1.1 has no release page)",
          "H2": "`v2/docs/handover/RELEASE-H2.md`", "H3": "`v2/docs/handover/RELEASE-H3.md`"}


def git(*a, inp=None, env=None):
    e = dict(os.environ); e.update(env or {})
    r = subprocess.run(["git", "-C", TOP] + list(a), input=inp, capture_output=True, env=e)
    if r.returncode: raise SystemExit("git %s: %s" % (" ".join(a[:3]), r.stderr.decode()[:300]))
    return r.stdout


def h16(b): return hashlib.sha256(b).hexdigest()[:16]


def old_zip(v): return os.path.join(TOP, HO, v + ".zip")


def old_manifest(v):
    """{path: row} of the superseded snapshot's MANIFEST.tsv, read from inside its ZIP (H1 has no copy beside it)."""
    with zipfile.ZipFile(old_zip(v)) as z:
        t = z.read("%s/MANIFEST.tsv" % v).decode()
    return {r["path"]: r for r in csv.DictReader(io.StringIO(t), delimiter="\t")}


def plan(v, src):
    """[(path, mode, old bytes, new bytes, events)] to change, and [(path, reason)] left, for one snapshot."""
    man = old_manifest(v)
    tree = {}
    for rec in git("ls-tree", "-r", "-z", src).split(b"\0"):
        if not rec: continue
        meta, p = rec.split(b"\t", 1); mode, typ, sha = meta.decode().split()
        tree[p.decode()] = (mode, sha)
    change, left = [], []
    for p, row in sorted(man.items()):
        if row["git_blob_sha"] == "-" or p not in tree: continue      # generated files and the root copies of pages
        b = git("cat-file", "blob", tree[p][1])
        if not S.count(b): continue
        if p in A.LEFT: left.append((p, A.LEFT[p])); continue
        if p in A.SCRIPTS or p in A.CHECKS: raise SystemExit("%s in %s is a script or a filed check: not planned for" % (p, v))
        new, ev = S.redact(b.decode("utf-8"), S.kind_of(p))
        change.append((p, tree[p][0], b, new.encode("utf-8"), ev))
    return change, left, tree


def box(v, src, change, left):
    """The Markdown box opened at the top of START-HERE.md in the reissue."""
    with open(old_zip(v) + ".sha256") as f: zsha = f.read().split()[0]
    L = ["> **This is %s-R1, a redaction reissue of handover snapshot %s (%s, MESHSAT-1357). It changes no engineering "
         "content, and it supersedes %s** (`%s/%s.zip`, sha256 `%s`), which stays published byte for byte beside it." % (
             v, v, TODAY, v, HO, v, zsha),
         ">",
         "> **Why.** The owner's rule is that public files carry no internal host names, user paths or addresses, and %s "
         "carried the runner's path, a session scratch path or a host name in %d of its files. The owner asked for a "
         "reissue with a new version record and new hashes rather than an edit of an accepted release, and did not "
         "authorize rewriting the repository's history, where %s's files stay as they were." % (v, len(change) + len(left), v),
         ">",
         "> **How.** The commit this snapshot is built from (named in `SOURCE.txt`) has %s's source commit `%s` as its only "
         "parent and changes the files below and this page, nothing else. The same packer built it "
         "(`v2/ecad/tools/handover_pack.py`, the one that built H3). Each replacement is a neutral token (`<worktrees>`, "
         "`<repo>`, `<runner home>`, `/tmp/<scratchpad>`, \"the runner\", \"the laptop\"); "
         "`v2/docs/records/scrub/MAP.md` on the public repository lists every one by file, line and token class, and "
         "`v2/docs/handover/RELEASE-%s-R1.md` there is this version's record." % (v, src[:8], v),
         ">",
         "> | File | sha256/16 in %s | sha256/16 here | What changed |" % v, "> |---|---|---|---|"]
    for p, mode, ob, nb, ev in change:
        cls = sorted({e["class"] for e in ev})
        L.append("> | `%s` | `%s` | `%s` | %d replacement%s (%s) |" % (p, h16(ob), h16(nb), len(ev), "" if len(ev) == 1 else "s", ", ".join(cls)))
    L += [">", "> A hash that a page of this snapshot cites for one of these files names %s's bytes, which %s and the "
          "public repository at `%s` hold." % (v, v, src[:8])]
    if left:
        L += [">", "> **Left as %s carried them**, so that every hash cited for them still holds:" % v]
        for p, why in left: L.append("> - `%s`: %s." % (p, why))
    L += [">", "> Every other file is byte for byte %s's: this snapshot's `MANIFEST.tsv` equals %s in every row but the "
          "files above, this page (at the root and under `v2/docs/handover/`) and `SOURCE.txt`." % (
              v, "the `MANIFEST.tsv` inside `H1.zip`" if v == "H1" else "`%s.MANIFEST.tsv`" % v)]
    return "\n".join(L) + "\n"


def commits():
    out = {}
    pcc = os.environ.get("PRECOMMIT_CHECK") or os.path.join(
        os.path.dirname(git("rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()),
        "..", "scripts", "pre-commit-check.sh")
    if not os.path.isfile(pcc): raise SystemExit("no pre-commit check found; set $PRECOMMIT_CHECK to the repository's one")
    for v, src in SNAPS:
        change, left, tree = plan(v, src)
        sh_mode, sh_sha = tree[SH]
        sh_old = git("cat-file", "blob", sh_sha).decode("utf-8")
        head, rest = sh_old.split("\n", 1)
        assert head.startswith("# ") and rest.startswith("\n"), "%s: START-HERE does not open with its title" % v
        sh_new = head + "\n\n" + box(v, src, change, left) + rest
        idx = os.path.join(git("rev-parse", "--path-format=absolute", "--git-dir").decode().strip(), "scrub-index-" + v)
        env = {"GIT_INDEX_FILE": idx}
        git("read-tree", src, env=env)
        for p, mode, ob, nb, ev in change + [(SH, sh_mode, sh_old.encode(), sh_new.encode(), [])]:
            blob = git("hash-object", "-w", "--stdin", inp=nb).decode().strip()
            git("update-index", "--cacheinfo", "%s,%s,%s" % (mode, blob, p), env=env)
        t = git("write-tree", env=env).decode().strip()
        os.remove(idx)
        subj = ("docs(handover): %s-R1, the redaction reissue of %s: %d file(s) carry neutral tokens where %s carried "
                "private paths or host names, and START-HERE names what it supersedes [MESHSAT-1357]" % (v, v, len(change), v))
        body = ("Only parent: %s's source commit. No engineering content changes; the files left as they were are named "
                "in START-HERE's box with the reason. Built into %s/%s-R1.zip by handover_pack.py; recorded in main's "
                "history by a merge that keeps main's tree (the owner did not authorize rewriting history)." % (v, HO, v))
        env = {"GIT_AUTHOR_NAME": OWNER[0], "GIT_AUTHOR_EMAIL": OWNER[1], "GIT_COMMITTER_NAME": OWNER[0],
               "GIT_COMMITTER_EMAIL": OWNER[1], "GIT_AUTHOR_DATE": DATE, "GIT_COMMITTER_DATE": DATE}
        c = git("commit-tree", t, "-p", src, "-m", subj, "-m", body, env=env).decode().strip()
        d = git("diff", src, c)
        r = subprocess.run(["bash", pcc, "meshsat-fieldkit", "--msg", subj], input=d, capture_output=True)
        ok = b"PASSED" in r.stdout
        names = git("diff", "--name-only", src, c).decode().split()
        print("%s-R1: redaction commit %s (parent %s), %d file(s) changed %s; pre-commit check %s" % (
            v, c, src[:8], len(names), names, "PASSED" if ok else "FAILED"))
        if not ok: raise SystemExit(r.stdout.decode()[-600:])
        out[v] = {"commit": c, "source": src, "subject": subj,
                  "changed": [(p, h16(ob), h16(nb), ev) for p, mode, ob, nb, ev in change], "left": left}
    json.dump(out, open(os.path.join(HERE, "reissue_commits.json"), "w"), indent=1)
    return 0


def rows(tsv):
    return {r["path"]: r for r in csv.DictReader(io.StringIO(tsv), delimiter="\t")}


def build(out_dir):
    info = json.load(open(os.path.join(HERE, "reissue_commits.json")))
    maprows, summary = [], []
    for v, src in SNAPS:
        rec = info[v]; nv = v + "-R1"; c = rec["commit"]
        r = subprocess.run([sys.executable, PACK, "build", "--commit", c, "--version", nv, "--out", out_dir, "--zip-only"],
                           capture_output=True, text=True)
        print(S.redact(r.stdout.strip().split("\n")[0])[0])
        if r.returncode: raise SystemExit("build %s: exit %d %s" % (nv, r.returncode, r.stderr[-400:]))
        z = os.path.join(out_dir, nv + ".zip")
        r = subprocess.run([sys.executable, PACK, "verify", z], capture_output=True, text=True)
        if r.returncode: raise SystemExit("verify %s: %s" % (nv, (r.stdout + r.stderr)[-400:]))
        new = rows(open(os.path.join(out_dir, nv + ".MANIFEST.tsv"), encoding="utf-8").read())
        old = old_manifest(v)
        changed = {p for p, _, _, _ in rec["changed"]}
        expect = changed | {SH, "START-HERE.md", "SOURCE.txt"}
        assert set(new) == set(old), "%s: the file lists differ: %s" % (nv, sorted(set(new) ^ set(old))[:5])
        differ = {p for p in new if new[p]["sha256"] != old[p]["sha256"]}
        assert differ == expect, "%s: rows differ beyond the plan: %s" % (nv, sorted(differ ^ expect))
        same_other = all(new[p][k] == old[p][k] for p in new if p not in expect for k in new[p])
        assert same_other, "%s: a row differs in a column other than its hash" % nv
        leftp = {p for p, _ in rec["left"]}
        with zipfile.ZipFile(z) as zf:
            hit = sorted(e.split("/", 1)[1] for e in zf.namelist() if not e.endswith("/") and S.count(zf.read(e)))
            n = len(zf.namelist())
        assert set(hit) <= leftp, "%s: entries carry a pattern that the plan did not leave: %s" % (nv, set(hit) - leftp)
        zsha = hashlib.sha256(open(z, "rb").read()).hexdigest(); zb = os.path.getsize(z)
        msha = hashlib.sha256(open(os.path.join(out_dir, nv + ".MANIFEST.tsv"), "rb").read()).hexdigest()
        with open(old_zip(v) + ".sha256") as f: osha = f.read().split()[0]
        summary.append((v, nv, c, src, zsha, zb, n, msha, osha, len(new) - len(expect), rec, hit))
        for p, a, b, ev in rec["changed"]:
            for e in ev: maprows.append((nv, p, e["line"], e["class"], e["token"], e["note"]))
        print("%s: zip sha256 %s, %d bytes, %d entries; manifest rows equal to %s's: %d; changed: %d file(s) + START-HERE "
              "(twice) + SOURCE.txt; entries left with a pattern: %s" % (nv, zsha, zb, n, v, len(new) - len(expect),
                                                                         len(changed), ", ".join(hit) or "none"))
    open(os.path.join(HERE, "map_reissue.tsv"), "w", encoding="utf-8").write(
        "snapshot\tfile\tline\ttoken class\ttoken\tnote\n" + "".join("\t".join(map(str, r)) + "\n" for r in maprows))
    for s in summary: write_release(*s)
    if os.path.realpath(out_dir) == os.path.realpath(os.path.join(TOP, HO)): start_here_row()
    return 0


def start_here_row():
    """The row of the tree's START-HERE.md that lists the snapshots names the reissues beside them (once)."""
    p = os.path.join(TOP, SH)
    t = open(p, encoding="utf-8").read()
    old = "the snapshots (`H1/` unzipped; `H1.zip`, `H1.1.zip`, `H2.zip` and `H3.zip` with their sha256 and manifests)"
    new = (old[:-1] + "; beside them since 30 September 2026 their redaction reissues `H1-R1.zip`, `H1.1-R1.zip`, "
           "`H2-R1.zip` and `H3-R1.zip`, which supersede them and change no engineering content, each with its record "
           "`v2/docs/handover/RELEASE-<version>-R1.md`)")
    if new in t: return
    assert t.count(old) == 1, "the START-HERE row of the snapshots is not the one expected"
    open(p, "w", encoding="utf-8").write(t.replace(old, new))
    print("START-HERE.md: the snapshots' row names the four reissues")


def write_release(v, nv, c, src, zsha, zb, n, msha, osha, same, rec, hit):
    B = "fd7e353f0fcaaba2a166997ad68403321a280368b8513100d4ae4e7002f7f5fe"
    L = ["# Handover release %s: what it is and how to check it" % nv, "",
         "Written %s (MESHSAT-1357) by the scrub of public files (`v2/docs/records/scrub/`), from the build's own figures "
         "(`reissue_snapshots.py build`). **%s is a redaction reissue of %s. It changes no engineering content and "
         "supersedes %s, which stays in `%s/` byte for byte as published.** Everything recorded in %s about %s's "
         "layers, reviews, checks and errata holds for %s unchanged. Nothing in it has been built, ordered, powered or measured." % (
             TODAY, nv, v, v, HO, RECORD[v], v, nv), "",
         "**Why.** The owner's rule is that public files carry no internal host names, user paths or addresses. %s carried "
         "the runner's path, a session scratch path or a host name in %d file(s). The owner's words of 29 September 2026: "
         "\"Reissue affected handover snapshots with new version records and hashes rather than silently modifying "
         "accepted releases. This instruction does not authorize rewriting Git history.\"" % (v, len(rec["changed"]) + len(rec["left"])), "",
         "## The package", "",
         "| Item | Value |", "|---|---|",
         "| File | `%s/%s.zip` (with `%s.zip.sha256` and `%s.MANIFEST.tsv` beside it) |" % (HO, nv, nv, nv),
         "| sha256 | `%s` |" % zsha,
         "| Size | %s bytes, %d entries (the same files as %s); the cap of `pack.yaml` is 52,428,800 bytes |" % (format(zb, ","), n, v),
         "| Manifest | `%s.MANIFEST.tsv`, sha256 `%s`, a byte copy of the ZIP's `MANIFEST.tsv` |" % (nv, msha),
         "| Supersedes | `%s/%s.zip`, sha256 `%s` |" % (HO, v, osha),
         "| Source commit | `%s`, the redaction commit (every file in the ZIP is its blob): its only parent is %s's source commit `%s`, and it changes the files below and `%s` |" % (c, v, src, SH),
         "| Snapshot commit | the commit of the scrub's set that adds this ZIP, its checksum, its manifest and this page |",
         "| Builder | `v2/ecad/tools/handover_pack.py` sha256 `%s`, the packer that built H3%s |" % (B, "" if v == "H3" else "; `SOURCE.txt` names it as the builder that ran, beside the older builder the commit holds"),
         "| Public | the redaction commit reaches main's history through the merge that keeps main's tree (`git merge -s ours`) in the scrub's set; `SOURCE.txt` marks it `public no` because it was built before that merge was published |",
         "| Check | `sha256sum -c %s.zip.sha256`, then `python3 v2/ecad/tools/handover_pack.py verify %s.zip` |" % (nv, nv),
         "| Rebuild | `python3 v2/ecad/tools/handover_pack.py build --commit %s --version %s --zip-only --out <folder>`: the ZIP is deterministic per host; across hosts compare `%s.MANIFEST.tsv` |" % (c[:12], nv, nv),
         "", "## What differs from %s" % v, "",
         "`MANIFEST.tsv` of %s has the same %d rows as %s's. %d are identical in every column. The others:" % (nv, same + len(rec["changed"]) + 3, v, same), "",
         "| File | sha256/16 in %s | sha256/16 in %s | Why |" % (v, nv), "|---|---|---|---|"]
    for p, a, b, ev in rec["changed"]:
        cls = sorted({e["class"] for e in ev})
        L.append("| `%s` | `%s` | `%s` | %d replacement%s: %s |" % (p, a, b, len(ev), "" if len(ev) == 1 else "s", ", ".join(cls)))
    L += ["| `START-HERE.md` and `%s` | | | opened by a box naming %s, why it is superseded, the table above and the files left |" % (SH, v),
          "| `SOURCE.txt` | | | the redaction commit, its tree and date, the builder and the tool versions of the host that built %s |" % nv, "",
          "A hash that a page of %s cites for a changed file names %s's bytes; %s and the public repository at `%s` hold "
          "them. Each replacement is listed by file, line and token class in `v2/docs/records/scrub/MAP.md`." % (nv, v, v, src[:8]), ""]
    if rec["left"]:
        L += ["## Left as %s carried them" % v, "",
              "The scrub of the tree leaves these files as they are (`v2/docs/records/scrub/README.md`, \"What was left\"), "
              "and %s keeps them the same way, so every hash that a page or a check cites for them still holds:" % nv, ""]
        for p, why in rec["left"]: L.append("- `%s`: %s." % (p, why))
        L.append("")
    L += ["## What was not done", "",
          "- No engineering file of %s changed: no schematic, netlist, generator, board table, checking tool, registry, "
          "export or maker document. The redacted files are pages, records and readings, and in each only a path or a "
          "host name changed." % v,
          "- No review or check read %s again: it is %s with the redactions listed above, and what %s's records say "
          "was reviewed, repeated or found applies to it unchanged." % (nv, v, v),
          "- The repository's history was not rewritten: %s's files and every earlier revision keep the old values there." % v, ""]
    open(os.path.join(TOP, "v2/docs/handover/RELEASE-%s.md" % nv), "w", encoding="utf-8").write("\n".join(L))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["commits"]: sys.exit(commits())
    if a[:1] == ["build"]:
        out = a[a.index("--out") + 1] if "--out" in a else os.path.join(TOP, HO)
        sys.exit(build(os.path.abspath(out)))
    print(__doc__); sys.exit(2)
