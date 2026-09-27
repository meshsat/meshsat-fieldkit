#!/usr/bin/env python3
"""Add the h3 records to v2/docs/records/README.md, the index of filed records (MESHSAT-1357, 27 September 2026).

Written by the H3 pages worker for the integrator to run: the README is a shared file with one writer, so the worker
does not edit it. The script makes three changes and nothing else:
  1. one row for the folder `h3/` in the folder table, after the row of `h2m/`;
  2. one row per file of `v2/docs/records/h3/` in the table "Filed files", after the last row of `h2m/`, each with
     the file's sha256 and size AS THEY ARE WHEN THE SCRIPT RUNS (so a record re-run by the integrator on the source
     commit is indexed as filed, not as the worker left it);
  3. in the row of `h2m/`, the packer's commit `992f2bc2` becomes `a54b1f4d`, main's commit with the same patch
     (v2/docs/records/h3/same_patches.out), since `992f2bc2` is on no pushed branch.
It asserts each old text is present exactly once, asserts the new text differs, reads the file back and checks that
every row it meant to write is there, and refuses a second run (a README that already holds the `h3/` row).

Usage (from the repository root): python3 v2/docs/records/h3/apply_records_readme.py
"""
import hashlib, os, subprocess, sys

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True).stdout.strip()
README = os.path.join(ROOT, "v2/docs/records/README.md")
H3 = os.path.join(ROOT, "v2/docs/records/h3")
WHO = "`fnd/h3` (authored in the tree by the H3 pages worker)"
CITED = {
    "handover_counts.py": "every count of the H3 handover pages (START-HERE, LAYER-STATUS, CONTINUATION-BRIEF, "
                          "ENGINEERING-QUESTIONS, REGENERATE, RELEASE-H3); a copy of `h2/handover_counts.py`, its "
                          "docstring listing the four differences",
    "handover_counts.out": "as for its script",
    "design_difference.py": "`v2/docs/handover/START-HERE.md` section 1a, `LAYER-STATUS.md` (Status at handover H3), "
                            "`REGENERATE.md` (Edition H3) and `RELEASE-H3.md`: H3's design content is H2's",
    "design_difference.out": "as for its script",
    "public_check.py": "`v2/docs/handover/REGENERATE.md` sections 7 and 9, `H2-RESPONSE.md` M1 and `RELEASE-H3.md`: "
                       "which commits are on the public repository, asked at the time it prints",
    "public_check.out": "as for its script",
    "same_patches.py": "`v2/docs/handover/H2-RESPONSE.md` (the correction of the commit ids) and `REGENERATE.md` "
                       "section 9",
    "same_patches.out": "as for its script",
    "zip_size_estimate.py": "`v2/docs/handover/pack.yaml` (the comment on H3): the ZIP's expected size against "
                            "`max_zip_bytes`, before the build",
    "zip_size_estimate.out": "as for its script",
    "apply_rebinds.py": "no page: the check that no page edited for H3 is bound by the requirements registry, and "
                        "the rebind path with its self-test",
    "apply_rebinds.out": "as for its script",
    "apply_records_readme.py": "this README (the rows of `h3/`)",
}
FOLDER_ROW = (
    "| `h3/` | the H3 pages worker (27 September 2026, branch `fnd/h3` from `6ec37197`), preparing the source commit "
    "of handover H3 by corrections to pages only: the count script of the H3 pages and its output; the difference "
    "from H2's source commit `b89b50b4` by class, which asserts that no design file, generator or checking tool "
    "changed and that the registry differs from its baseline `a54b793b` in no protected field; the public check of "
    "the commits the pages name; the patch ids of the commits `H2-RESPONSE.md` first cited against main's; the "
    "estimate of the ZIP's size before the build; the check that no edited page is bound by the registry, with the "
    "rebind path and its self-test; and this index's own apply script; authored in the tree, filed byte for byte |\n")


def main():
    text = open(README, encoding="utf-8").read()
    before = text
    if "| `h3/` |" in text:
        print("apply_records_readme: REFUSED, the README already holds the row of `h3/` (a second run)")
        return 1
    # 3. the packer's commit in the row of h2m/
    old = "`handover_pack.py repo` as committed in `992f2bc2`"
    assert text.count(old) == 1, "the row of h2m/ does not name 992f2bc2 exactly once"
    text = text.replace(old, "`handover_pack.py repo` as committed on main in `a54b1f4d` (first cited as `992f2bc2`, "
                             "the same patch on the branch before it was re-integrated)")
    # 1. the folder row
    lines = text.split("\n")
    i = [k for k, ln in enumerate(lines) if ln.startswith("| `h2m/` |")]
    assert len(i) == 1, "the folder table has not exactly one row of h2m/"
    lines.insert(i[0] + 1, FOLDER_ROW.rstrip("\n"))
    # 2. the file rows
    j = [k for k, ln in enumerate(lines) if ln.startswith("| `h2m/")]
    assert j, "the table of filed files has no row of h2m/"
    names = sorted(n for n in os.listdir(H3) if os.path.isfile(os.path.join(H3, n)))
    unknown = [n for n in names if n not in CITED]
    assert not unknown, "files of h3/ this script has no description for: %s" % ", ".join(unknown)
    rows = []
    for n in names:
        b = open(os.path.join(H3, n), "rb").read()
        rows.append("| `h3/%s` | `%s` | %d | %s | %s |" % (n, hashlib.sha256(b).hexdigest(), len(b), WHO, CITED[n]))
    lines[j[-1] + 1:j[-1] + 1] = rows
    text = "\n".join(lines)
    assert text != before
    open(README, "w", encoding="utf-8").write(text)
    back = open(README, encoding="utf-8").read()                       # read back: every row is there, once
    assert back.count("| `h3/` |") == 1 and "992f2bc2` as committed" not in back
    for r in rows:
        assert back.count(r) == 1, r[:60]
    assert len(back.split("\n")) == len(before.split("\n")) + 1 + len(rows)
    print("apply_records_readme: the row of `h3/`, %d file rows and the packer's commit in the row of `h2m/` written"
          % len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
