#!/usr/bin/env python3
"""PANJIT's SS2020FL series sheet held back from the public tree (MESHSAT-1357, integration set 15, 29 September 2026).
Found by stream w5identc: `v2/vendor/power/panjit-ss2020fl-series.pdf`, tracked since ccf5808e (26 September), reads on its
page 4 "Reproducing and modifying information of the document is prohibited without permission". Under the owner's rule of
27 September 2026 (third-party files: the session decides by each file's terms, conservatively) it is not published. This
script, asserting each old text once and refusing a second run:
  * untracks the file (git rm --cached) and moves it to v2/vendor/power/held/, which .gitignore now ignores;
  * points v2/vendor/SOURCES.yaml, v2/vendor/sources.txt and v2/vendor/vendor-status.txt at the held path, with the
    reason and the fetch script (records/int16/fetch_held_back.py), the sha256 already recorded in SOURCES.yaml kept;
  * asserts the file's page 4 carries the words and its sha256 is the recorded one.
The copy in git history and on the public mirror stays: removing it would rewrite published history, which is the owner's
decision, not taken here. Run: python3 <this file>."""
import hashlib, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
OLD = "v2/vendor/power/panjit-ss2020fl-series.pdf"
NEW = "v2/vendor/power/held/panjit-ss2020fl-series.pdf"
SHA = "92544a833cdaa6e17d9192a05ec84bbc8ec797c4cb5fa51c4250f158f2c534fe"
WORDS = "Reproducing and modifying information of the document is prohibited without permission"


def refuse(m):
    print("apply_hold_back_panjit: REFUSED: %s" % m); sys.exit(2)


def edit(rel, pairs):
    p = os.path.join(TOP, rel); s = open(p, encoding="utf-8").read(); s0 = s
    for o, n in pairs:
        if s.count(o) != 1: refuse("%s: %r found %d times" % (rel, o[:60], s.count(o)))
        s = s.replace(o, n)
    if s == s0: refuse("%s unchanged" % rel)
    open(p, "w", encoding="utf-8").write(s)


def main():
    if subprocess.run(["git", "-C", TOP, "ls-files", "--error-unmatch", OLD], capture_output=True).returncode:
        refuse("already applied (the file is not tracked)")
    src = os.path.join(TOP, OLD)
    if hashlib.sha256(open(src, "rb").read()).hexdigest() != SHA: refuse("the tracked file is not the recorded one")
    page4 = subprocess.run(["pdftotext", "-f", "4", "-l", "4", "-layout", src, "-"], capture_output=True, text=True).stdout
    if WORDS not in " ".join(page4.split()): refuse("page 4 does not carry the words")
    edit(".gitignore", [("v2/vendor/nexperia/held/\n",
        "v2/vendor/nexperia/held/\n"
        "# PANJIT's SS2020FL series sheet (board C's D19 to D21), held back by its terms from integration set 15 (29 September\n"
        "# 2026; its page 4: \"Reproducing and modifying information of the document is prohibited without permission\"):\n"
        "# fetched by v2/docs/records/int16/fetch_held_back.py and checked by sha256, never committed.\n"
        "v2/vendor/power/held/\n")])
    edit("v2/vendor/SOURCES.yaml", [('      - path: "%s"\n        doc_id: "PANJIT SS2020FL~SS20100FL"' % OLD,
          '      - path: "%s"\n        doc_id: "PANJIT SS2020FL~SS20100FL"' % NEW)])
    edit("v2/vendor/sources.txt", [("power/panjit-ss2020fl-series.pdf   # https://www.panjit.com.tw/upload/datasheet/SS2020FL_SERIES.pdf",
          "power/held/panjit-ss2020fl-series.pdf   # NOT IN THE REPOSITORY since integration set 15: held back by its terms (page 4, "
          "\"Reproducing and modifying information of the document is prohibited without permission\"); "
          "https://www.panjit.com.tw/upload/datasheet/SS2020FL_SERIES.pdf; sha256 %s; fetched by "
          "v2/docs/records/int16/fetch_held_back.py. Filed in the tree from ccf5808e to set 15; that copy stays in git history" % SHA)])
    edit("v2/vendor/vendor-status.txt", [("power/panjit-ss2020fl-series.pdf   current   # PANJIT SS2040FL",
          "power/held/panjit-ss2020fl-series.pdf   current, held back (its terms; fetch_held_back.py of records/int16)   # PANJIT SS2040FL")])
    subprocess.run(["git", "-C", TOP, "rm", "-q", "--cached", OLD], check=True)
    os.makedirs(os.path.dirname(os.path.join(TOP, NEW)), exist_ok=True)
    shutil.move(src, os.path.join(TOP, NEW))
    if not subprocess.run(["git", "-C", TOP, "check-ignore", "-q", NEW]).returncode == 0: refuse("the held path is not ignored")
    print("apply_hold_back_panjit: untracked, moved to %s (ignored), the three vendor records point there" % NEW)
    return 0


if __name__ == "__main__":
    sys.exit(main())
