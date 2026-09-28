#!/usr/bin/env python3
"""The registry pins CONOPS.md's needs table by the file's sha256 (`needs_document_sha256`). apply_owner_rulings_2026_09_28.py
changed CONOPS.md in section 7 and section 3's M1 only; this script asserts that the needs table of section 2 is byte-identical
to the one at the commit the registry pins (read from git by that sha) and moves the pin to the file as it now is. Refuses when
the table differs or the pin already matches. Run from the repository root: python3 <this file>."""
import hashlib, os, re, subprocess, sys

import yaml

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REG = os.path.join(TOP, "v2/ecad/tools/pcb_requirements.yaml"); CON = os.path.join(TOP, "v2/docs/CONOPS.md")


def needs_table(text):
    i = text.index("| ID | Need | Source |"); rows = []
    for line in text[i:].split("\n"):
        if not line.startswith("|"): break
        rows.append(line)
    return "\n".join(rows)


def main():
    reg = open(REG, encoding="utf-8").read(); con = open(CON, encoding="utf-8").read()
    now = hashlib.sha256(con.encode("utf-8")).hexdigest()
    m = re.search(r"(?m)^needs_document_sha256: ([0-9a-f]{64})\n", reg)
    if not m: print("REFUSED: no needs_document_sha256"); return 2
    old = m.group(1)
    if old == now: print("REFUSED: the pin already matches the tree (a second run)"); return 2
    # find the pinned version in history
    pinned = None
    for rev in subprocess.run(["git", "-C", TOP, "rev-list", "--max-count=200", "HEAD", "--", "v2/docs/CONOPS.md"], capture_output=True, text=True).stdout.split():
        t = subprocess.run(["git", "-C", TOP, "show", "%s:v2/docs/CONOPS.md" % rev], capture_output=True, text=True).stdout
        if hashlib.sha256(t.encode("utf-8")).hexdigest() == old: pinned = t; break
    if pinned is None: print("REFUSED: no commit in the last 200 carries CONOPS.md at %s" % old[:16]); return 2
    if needs_table(pinned) != needs_table(con): print("REFUSED: the needs table changed; bring `needs` into line first"); return 2
    out = reg[:m.start()] + "needs_document_sha256: %s\n" % now + reg[m.end():]
    yaml.safe_load(out); open(REG, "w", encoding="utf-8").write(out)
    print("apply_needs_sha_conops: needs table byte-identical; pin moved %s -> %s" % (old[:16], now[:16])); return 0


if __name__ == "__main__":
    sys.exit(main())
