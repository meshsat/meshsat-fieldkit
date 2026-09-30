#!/usr/bin/env python3
"""The public-file scrub of the tree (MESHSAT-1357, 30 September 2026, written on main 8fec0733).

The owner's standing rule: public files carry no internal host names, user paths or addresses. The owner's words of
29 September 2026: "Complete the public-file cleanup as a bounded task. Preserve engineering provenance. Reissue affected
handover snapshots with new version records and hashes rather than silently modifying accepted releases. This
instruction does not authorize rewriting Git history." This script does the tree's part; reissue_snapshots.py does the
snapshots' part. Both redact with scrub_lib.redact, the one function and the one set of token classes.

WHAT IT DOES, per class of file (records/scrub/README.md gives the reasons and the decisions):
  DOCS      live documents: every hit becomes a neutral token.
  READINGS  a tool's output or a log: edited as text, because no tool can re-take the same reading (the tree, the
            scratch folder or the box it read is gone, or a re-take would be a new engineering reading and change a
            rule's evidence class); each entry says why.
  CHECKS    filed checks whose bytes no file cites by sha: redacted, with a filing note at the end.
  SCRIPTS   scripts whose path does work: the path is derived (an environment variable with a default under $HOME,
            git, or the transcript the script reads), then the comments are redacted like a document; each is tested
            by script_tests.py.
  REPIN     records/README.md rows that pin a script this changes by sha256: re-pinned, the filed sha kept in the row.
  LEFT      examined and left, with the reason (a filed check or record cited by sha, a reading a bound page cites by
            sha, an accepted release, a binary); records/scrub/README.md lists them for the owner.
It writes records/scrub/map_tree.tsv (file, line, token class, token, note, treatment), never a removed value.

It asserts each old text before it writes, re-parses every JSON file it writes, compiles every script, and refuses a
second run (a target that carries no hit any more is already done). Run: python3 <this file> [--check]
"""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scrub_lib as S

TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
BASE = "8fec0733"
TODAY = "30 September 2026"

DOCS = [
    "v2/docs/EXECUTION-PLAN.md", "v2/docs/MESHSAT-709-geometry-appendix.md", "v2/docs/respin-footprints-2026-09-04.md",
    "v2/release/revA/order/ORDER-LOG.md", "v2/docs/records/d6dec/README.md", "v2/docs/records/w5si/RECOVERY.md",
    "v2/docs/records/rf2walk/LOG.md", "v2/docs/records/s117/LOG.md", "v2/docs/records/s120/LOG.md", "v1/cad/FIXES.md",
    "v2/vendor/aioc/aioc-net.xml",
]
_GONE = "the tree, scratch folder or run it read no longer exists, so no tool can take the same reading again"
_VERDICT = ("a re-take by the tool would read this tree instead of the one recorded and would move DOC-002's evidence "
            "class on the board (a new engineering reading, not a redaction); the recorded input path keeps its "
            "temporary root, so rules_status.py still classes the reading as before")
READINGS = {
    "v2/docs/records/d4emcon/readings/tests-before-and-after.txt": "a hand-written header line of a test run log",
    "v2/docs/records/d6rel/apply-script-test.txt": _GONE,
    "v2/docs/records/int10/box/config-apply.log": _GONE,
    "v2/docs/records/int10/dryrun.out": _GONE + " (dryrun.py re-run today dry-runs today's tree)",
    "v2/docs/records/r8int6/fix/validators-760d7f41.txt": _GONE,
    "v2/docs/records/retake6/analysis/audit-diff-before-after.txt": _GONE,
    "v2/docs/records/retake6/analysis/audit-diff-main-after.txt": _GONE,
    "v2/docs/records/retake6/worktree/run.txt": _GONE,
    "v2/docs/records/s98/readings/apply-scripts-dryrun.out": _GONE,
    "v2/docs/records/s98/readings/ast-parse.out": _GONE,
    "v2/docs/records/s98/readings/lead-ends-projection.out": _GONE,
    "v2/docs/records/w5si/recovery/RESULT-w5si-author-1.json": "an author's result of 27 September 2026, recovered; " + _GONE,
    "v2/docs/records/w5tray/pass1/RESULT-w5tray-author-1.json": "an author's result of 27 September 2026, recovered; " + _GONE,
    "v2/ecad/pcb-c-display-c8/routed/doc_provenance_c.verdict.json": _VERDICT,
    "v2/ecad/pcb-e5-block/routed/doc_provenance_e5.verdict.json": _VERDICT,
    "v2/ecad/pcb-p-pack-p2/routed/doc_provenance_p.verdict.json": _VERDICT,
    "v2/ecad/pcb-c-display-c8/routed/ledger_verify.verdict.json": _VERDICT.replace("keeps its temporary root", "was never under a temporary directory"),
    "v2/ecad/pcb-e5-block/routed/ledger_verify.verdict.json": _VERDICT.replace("keeps its temporary root", "was never under a temporary directory"),
    "v2/ecad/pcb-p-pack-p2/routed/ledger_verify.verdict.json": _VERDICT.replace("keeps its temporary root", "was never under a temporary directory"),
}
CHECKS = [
    "v2/docs/records/cx1/checks/check-1-RESULT.md", "v2/docs/records/cx1/checks/check-2-RESULT.md",
    "v2/docs/records/int7/CHECK.md", "v2/docs/records/int7/CHECK-2.md", "v2/docs/records/int7/CHECK-3.md",
    "v2/docs/records/int7/checks/d6rel-check-1.md", "v2/docs/records/int7/checks/d8dec31-check-1.md",
    "v2/docs/records/int7/checks/p3bind-check-2.md", "v2/docs/records/int7/checks/w5si-check-2-drafts.md",
    "v2/docs/records/int7/checks/w5tray-check-2.md", "v2/docs/records/int8/CHECK-notes.md",
    "v2/docs/records/int8/checks/d6rel-check-2-notes.md", "v2/docs/records/int8/checks/d8dec31-check-2-notes.md",
    "v2/docs/records/int8/checks/d8dec31-check-2.md", "v2/docs/records/int8/checks/w5si2-check-1-notes.md",
    "v2/docs/records/int8/checks/w5si2-check-1.md", "v2/docs/records/w5si/check-1/RESULT-w5si-check-1.json",
    "v2/docs/records/cx1/checks/check-1-phase1.py",
]
_WT = '${WORKTREES:-$HOME/worktrees/meshsat-fieldkit}'
_PYWT = 'os.environ.get("WORKTREES", os.path.expanduser("~/worktrees/meshsat-fieldkit"))'
_SPOLD = S.TMPROOT + "1000/" + S.MANGLED
# SCRIPTS: path -> [(old, new, class, token as MAP writes it)]. Old texts are assembled from scrub_lib's decoded values.
SCRIPTS = {
    "v2/docs/records/d6dec/box/to_box.sh": [
        ("W=%s/worktrees/meshsat-fieldkit/d6dec\n" % S.HOME, "W=%s/d6dec\n" % _WT, S.RUNNER, "derived: $WORKTREES, default under $HOME"),
        ("B=%s/worktrees/meshsat-fieldkit/_bin\n" % S.HOME, "B=${BOX_BIN:-%s/_bin}\n" % _WT, S.RUNNER, "derived: $BOX_BIN, default under $WORKTREES"),
        ("S=${SCRATCH:-%s/97d77a0f-0370-4f6d-8c22-b95e41e6e4a1/scratchpad}/bx\n" % _SPOLD,
         "S=${SCRATCH:-${TMPDIR:-/tmp}/d6dec-to-box}/bx\n", S.TEMP, "derived: $SCRATCH, default under $TMPDIR"),
    ],
    "v2/docs/records/int7/box/int7_install_pack.sh": [
        ("W=%s/worktrees/meshsat-fieldkit/int7\n" % S.HOME, "W=%s/int7\n" % _WT, S.RUNNER, "derived: $WORKTREES, default under $HOME"),
        ("SP=%s/90a77d46-57cf-4758-b702-e06537d0a6cc/scratchpad/box\n" % _SPOLD,
         "SP=${SCRATCH:-${TMPDIR:-/tmp}/int7-install}/box\n", S.TEMP, "derived: $SCRATCH, default under $TMPDIR"),
        ('%s/worktrees/meshsat-fieldkit/_bin/bxs.sh "tar cf /root/int7/pack.tar -C /root/int7 pack" && %s/worktrees/meshsat-fieldkit/_bin/bxcp.sh from' % (S.HOME, S.HOME),
         'B=${BOX_BIN:-%s/_bin}; $B/bxs.sh "tar cf /root/int7/pack.tar -C /root/int7 pack" && $B/bxcp.sh from' % _WT,
         S.RUNNER, "derived: $BOX_BIN, default under $WORKTREES (two instances)"),
    ],
    "v2/docs/records/r8int6/commit_r8int6.sh": [
        ("bash %s/gitlab/products/meshsat/scripts/pre-commit-check.sh meshsat-fieldkit" % S.HOME,
         'bash "${PRECOMMIT_CHECK:-$(dirname "$(git rev-parse --path-format=absolute --git-common-dir)")/../scripts/pre-commit-check.sh}" meshsat-fieldkit',
         S.RUNNER, "derived: $PRECOMMIT_CHECK, default beside the main clone (git)"),
    ],
    "v2/docs/records/r8int6/copy_evidence.sh": [
        ("M=%s/gitlab/products/meshsat/meshsat-fieldkit\n" % S.HOME,
         'M=${MAIN_CLONE:-$(dirname "$(git -C "$(dirname "$0")" rev-parse --path-format=absolute --git-common-dir)")}\n',
         S.RUNNER, "derived: $MAIN_CLONE, default the main clone of this script's repository (git)"),
    ],
    "v2/docs/records/int10/dryrun.py": [
        ('if not os.path.realpath(scratch).startswith("%s/worktrees/meshsat-fieldkit/_scratch/"):' % S.HOME,
         'if not os.path.realpath(scratch).startswith(os.path.join(os.path.realpath(%s), "_scratch", "")):' % _PYWT,
         S.RUNNER, "derived: $WORKTREES, default under the home directory"),
    ],
    "v2/docs/records/w5si/recovery/replay.py": [
        ('REC = "%s/worktrees/meshsat-fieldkit/_recovered/w5si-author-1"\n' % S.HOME,
         'REC = os.environ.get("W5SI_RECOVERED", os.path.join(%s, "_recovered", "w5si-author-1"))\n' % _PYWT,
         S.RUNNER, "derived: $W5SI_RECOVERED, default under $WORKTREES"),
        ('OLDSP = ("%s/"\n         "3744628d-5552-4a03-8300-e043b6cdc9c8/scratchpad")\nOLDWT = OLDSP + "/wt/w5si"\n' % _SPOLD,
         'OLDSP = None  # the lost session\'s scratchpad, read by main() from the transcript itself (never typed in here)\n'
         'OLDWT = None  # OLDSP + "/wt/w5si", set with it\n',
         S.TEMP, "derived: read from the transcript's own commands"),
        ('def main(stg, wt):\n    C = commands(os.path.join(REC, "bash.log"))\n',
         'def main(stg, wt):\n    global OLDSP, OLDWT\n'
         '    m = re.search(r"(/tmp/[^\\s\'\\"]+/scratchpad)/wt/w5si\\b", open(os.path.join(REC, "bash.log"), encoding="utf-8", errors="replace").read())\n'
         '    assert m, "the transcript names no w5si worktree under a scratchpad"\n'
         '    OLDSP, OLDWT = m.group(1), m.group(1) + "/wt/w5si"\n'
         '    C = commands(os.path.join(REC, "bash.log"))\n',
         None, None),
    ],
    "v2/docs/records/w5tray/recovery/replay.py": [
        ('OLDW = "%s/3744628d-5552-4a03-8300-e043b6cdc9c8/scratchpad/wt/w5tray"\ne = json.load(open(os.path.join(SP, "a1.json")))\n' % _SPOLD,
         'e = json.load(open(os.path.join(SP, "a1.json")))\n'
         'OLDW = re.search(r"/tmp/[^\\s\'\\"]+/scratchpad/wt/w5tray", "\\n".join(x["cmd"] for x in e)).group(0)  # the lost worktree, read from the transcript\n',
         S.TEMP, "derived: read from the transcript's own commands"),
    ],
    "v2/docs/records/cx1/checks/check-1-phase1.py": [
        ("import hashlib, json, sys\n", "import hashlib, json, os, sys\n", None, None),
        ('W = "%s/worktrees/meshsat-fieldkit/cx1"\n' % S.HOME,
         'W = os.environ.get("CX1_WORKTREE", os.path.join(%s, "cx1"))\n' % _PYWT,
         S.RUNNER, "derived: $CX1_WORKTREE, default under $WORKTREES"),
    ],
    "v1/cad/inspect_doc.py": [
        ('import FreeCAD as App\n', 'import os\nimport FreeCAD as App\n', None, None),
        ('Import.open("%s/Downloads/field_kit/field_kit.step")\n' % S.LHOME,
         'Import.open(os.environ.get("FIELD_KIT_STEP", os.path.expanduser("~/Downloads/field_kit/field_kit.step")))\n',
         S.LHOMEC, "derived: $FIELD_KIT_STEP, default under the home directory"),
    ],
    "v1/cad/render.py": [
        ('STEP_PATH = "%s/Downloads/field_kit/field_kit.step"\n' % S.LHOME,
         'STEP_PATH = os.environ.get("FIELD_KIT_STEP", os.path.expanduser("~/Downloads/field_kit/field_kit.step"))\n',
         S.LHOMEC, "derived: $FIELD_KIT_STEP, default under the home directory"),
        ('OUT_DIR   = "%s/Downloads/field_kit/renders"\n' % S.LHOME,
         'OUT_DIR   = os.environ.get("FIELD_KIT_RENDERS", os.path.expanduser("~/Downloads/field_kit/renders"))\n',
         S.LHOMEC, "derived: $FIELD_KIT_RENDERS, default under the home directory"),
    ],
}
# The scripts whose records/README.md row pins their bytes (rule 5 of the brief: re-pinned by a script, with a reason).
REPIN = ["v2/docs/records/r8int6/commit_r8int6.sh", "v2/docs/records/r8int6/copy_evidence.sh"]
LEFT = {
    "v2/docs/reviews/REVIEW-A-LAYER-1-2026-09-27.md": "a filed review record of layer 1 whose sha256/16 the release records of H2 and H3, the H2 and H3 handover counts, the H3 coherence check, two later reviews and a candidate patch cite",
    "v2/docs/records/handover/H2-USABILITY-CHECK.md": "a filed check whose sha256 records/README.md pins",
    "v2/docs/records/handover/H3-COHERENCE-CHECK.md": "a filed check whose sha256 records/README.md pins",
    "v2/docs/records/handover/H3-USABILITY-CHECK.md": "a filed check whose sha256 records/README.md pins",
    "v2/docs/handover/candidates/hc3.patch": "the H1.1 candidate patch as it was reviewed; candidates/README.md pins its sha256",
    "v2/docs/feasibility/fab/out/pulldowns.txt": "a reading FAILOVER-FABRIC.md cites by sha256; the requirements registry binds that page by sha, so a re-pin would change the baselined registry",
    "v2/cad/render/meshsat-v2-concept.blend": "a binary Blender scene that stores the laptop's last-used folder; not editable as text",
}


def sha(b): return hashlib.sha256(b).hexdigest()


def rd(p): return open(os.path.join(TOP, p), "rb").read()


def refuse(msg):
    print("apply_scrub: REFUSED: " + msg); sys.exit(2)


def tokens_of(events):
    return ", ".join(sorted({"`%s`" % e["token"] if e["token"].startswith(("<", "/", "$")) else '"%s"' % e["token"] for e in events}))


def filing_note(events, kind):
    n = len(events)
    how = ("derived from an environment variable with a default" if all(e["token"].startswith("$") for e in events)
           else "written as neutral tokens")
    words = ("Filing note (scrub, %s, MESHSAT-1357): %d path%s in this check %s %s (%s) under the owner's rule that "
             "public files carry no internal host names, user paths or addresses; v2/docs/records/scrub/MAP.md lists "
             "each by line and token class. No other byte of the check changed; the check as filed is in the "
             "repository's history at commit %s and before." % (
                 TODAY, n, "" if n == 1 else "s", "is" if n == 1 else "are", how, tokens_of(events), BASE))
    if kind == "md": return "\n---\n" + words.replace("v2/docs/records/scrub/MAP.md", "`v2/docs/records/scrub/MAP.md`").replace("commit %s" % BASE, "commit `%s`" % BASE) + "\n"
    if kind == "py": return "\n# " + words.replace("No other byte of the check changed", "No other byte of the check changed but the import of os the derivation needs") + "\n"
    return words


def main(argv):
    check = "--check" in argv
    targets = DOCS + list(READINGS) + CHECKS + list(SCRIPTS)
    assert len(set(targets)) == len(targets) - len(set(CHECKS) & set(SCRIPTS)), "a file is in two classes"
    before = {p: S.count(rd(p)) for p in dict.fromkeys(targets)}
    done = [p for p, c in before.items() if not c]
    if done: refuse("already applied (no hit left) in %d file(s), first %s" % (len(done), done[0]))
    rows, out = [], {}
    # 1. scripts: derive first (their old texts are exact), then the comments are redacted like a document
    for p, edits in SCRIPTS.items():
        t = rd(p).decode("utf-8")
        for old, new, cls, tok in edits:
            if t.count(old) != 1: refuse("%s: an old text is there %d time(s)" % (p, t.count(old)))
            t = t.replace(old, new)
        for old, new, cls, tok in edits:
            if cls is None: continue
            line = t[:t.index(new)].count("\n") + 1
            rows.append((p, line, cls, tok, "", "script: the path is derived"))
        out[p] = t
    # 2. every text target through the one redaction function
    for p in dict.fromkeys(targets):
        t = out.get(p, rd(p).decode("utf-8"))
        kind = S.kind_of(p)
        try:
            new, ev = S.redact(t, kind)
        except S.Refused as e:
            refuse("%s: %s" % (p, e))
        treat = ("filed check, not cited by sha: redacted with a filing note" if p in CHECKS else
                 "reading, edited as text: " + READINGS[p] if p in READINGS else
                 "script comment or docstring" if p in SCRIPTS else "live document")
        for e in ev: rows.append((p, e["line"], e["class"], e["token"], e["note"], treat))
        if p in CHECKS:
            allev = list(ev) + [{"token": "$" + r[3].split("$")[1].split(",")[0], "class": r[2]}
                                for r in rows if r[0] == p and r[5].startswith("script")]
            if kind == "json":
                j = new.rstrip()
                assert j.endswith("}")
                new = j[:-1].rstrip() + ',\n "filing_note": ' + json.dumps(filing_note(allev, "json")) + "\n}" + new[len(j):]
            else:
                new = new.rstrip("\n") + "\n" + filing_note(allev, "py" if p.endswith(".py") else "md")
        if new == rd(p).decode("utf-8"): refuse("%s: nothing changed" % p)
        if S.count(new): refuse("%s: a hit is left: %s" % (p, S.count(new)))
        if kind == "json":
            a, b = json.loads(new), json.loads(S.redact(rd(p).decode("utf-8"), "json")[0])
            a.pop("filing_note", None)
            if a != b: refuse("%s: the JSON differs in more than the redaction" % p)
        out[p] = new
    # 3. re-pin the records index rows
    idx_p = "v2/docs/records/README.md"
    idx = rd(idx_p).decode("utf-8")
    for p in REPIN:
        rel = p[len("v2/docs/records/"):]
        old_b = rd(p); new_b = out[p].encode("utf-8")
        row = [l for l in idx.split("\n") if l.startswith("| `%s` | `%s` | %d |" % (rel, sha(old_b), len(old_b)))]
        if len(row) != 1: refuse("the records index row of %s is not the one expected" % rel)
        cells = row[0].split(" | ")
        cells[1], cells[2] = "`%s`" % sha(new_b), str(len(new_b))
        cells[3] += ("; re-pinned %s by the scrub (`scrub/apply_scrub.py`): a path it named is derived now, and the "
                     "bytes as filed are sha256 `%s`, %d bytes, in history at `%s`" % (TODAY, sha(old_b), len(old_b), BASE))
        idx = idx.replace(row[0], " | ".join(cells))
        rows.append((idx_p, idx[:idx.index(" | ".join(cells))].count("\n") + 1, "(re-pin)", "sha256 and bytes of " + rel, "", "records index row re-pinned"))
    out[idx_p] = idx
    # 4. compile every script (python by compile(), shell by bash -n on stdin) BEFORE anything is written, then write
    for p, t in out.items():
        if p.endswith(".py"): compile(t, p, "exec")
        if p.endswith(".sh"):
            r = subprocess.run(["bash", "-n"], input=t.encode(), capture_output=True)
            if r.returncode: refuse("%s: bash -n: %s" % (p, r.stderr.decode()[:200]))
    for p, t in out.items():
        if check: continue
        with open(os.path.join(TOP, p), "w", encoding="utf-8", newline="") as f: f.write(t)
    rows.sort(key=lambda r: (r[0], r[1]))
    tsv = "file\tline\ttoken class\ttoken\tnote\ttreatment\n" + "".join("\t".join(map(str, r)) + "\n" for r in rows)
    if not check:
        open(os.path.join(HERE, "map_tree.tsv"), "w", encoding="utf-8").write(tsv)
    tot_b = {}
    for c in before.values():
        for k, v in c.items(): tot_b[k] = tot_b.get(k, 0) + v
    print("apply_scrub: %d file(s) %s, %d replacement row(s); instances before by class: %s" % (
        len(out), "checked" if check else "written", len(rows), json.dumps(tot_b, sort_keys=True)))
    print("apply_scrub: left (examined, with the reason in records/scrub/README.md): %d file(s) and the H1 folder" % len(LEFT))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
