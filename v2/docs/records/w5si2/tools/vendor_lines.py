#!/usr/bin/env python3
"""Rewrites the thirteen model lines of v2/vendor/sources.txt and v2/vendor/vendor-status.txt from the manifest (stream
w5si2, 28 September 2026, MESHSAT-1357; the drafts check's M6 and the first lens's M9). Run once by the author on the
stream's own branch; kept in the record to show where each word of the lines came from.

WHAT WAS WRONG. Each of the thirteen lines of sources.txt said the file "carries the maker's copyright and
redistribution notice, held under this folder's README terms". Eight of the thirteen carry NO sentence on
redistribution, only a disclaimer and a copyright line, and the README's terms are publish-as-is with takedown on
request, which is not what the five that forbid distribution allow. Each line also wrote sixteen hex digits as
"sha256". And every line read as if the file were in the repository. Now each line says: the file is NOT in the
repository, what pins it and what fetches it, the maker's address and what it serves, the fetches, the digest as
sha256/16 with the full one in the manifest, and WHICH WORDING ITS OWN HEADER CARRIES, with the lines.

Usage: vendor_lines.py <repository root> [--dry-run]
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(a):
    root = os.path.abspath(a[0])
    sys.path.insert(0, os.path.join(root, "v2", "ecad", "tools"))
    import ibis_manifest as IM
    man = IM.load(root)
    assert not man["why"] and not man["refusals"] and len(man["models"]) == 13, (man["why"], man["refusals"])
    out = {}
    for name in ("sources.txt", "vendor-status.txt"):
        p = os.path.join(root, "v2", "vendor", name)
        lines = open(p, encoding="utf-8").read().split("\n")
        changed = 0
        for file, r in man["models"].items():
            key = file[len("v2/vendor/"):]
            hits = [i for i, l in enumerate(lines) if l.startswith(key + " ")]
            assert len(hits) == 1, "%s: %d lines for %s" % (name, len(hits), key)
            i = hits[0]
            old = lines[i]
            qs = r["notice"]["quotes"]
            where = ", ".join("line%s %s" % ("s" if " to " in x["lines"] else "", x["lines"]) for x in qs)
            if r["notice"]["kind"] == "PROHIBITS_DISTRIBUTION":
                says = ("its header FORBIDS reproduction and distribution without the maker's written permission (\"%s\", %s)"
                        % (qs[0]["text"], where))
            else:
                says = ("its header carries a disclaimer of warranty and a copyright line (\"%s\", %s) and NO sentence on copying or "
                        "distribution: nothing in the file grants a right to redistribute it" % (qs[0]["text"], where))
            if name == "sources.txt":
                serves = "the model itself" if r["container"] == "ibs" else "a zip whose %s is the model" % r["member"]
                arch = (" (where the maker refuses a host: %s; %s)" % (r["archive_url"], r["archive_note"])) if r.get("archive_url") else ""
                new = ("%s   # NOT IN THE REPOSITORY: a maker's IBIS model, withheld (publication is the owner's decision), pinned by "
                       "ibis-manifest.yaml (row %s) and fetched by v2/ecad/tools/ibis_fetch.py. %s, %s: %s, which serves %s%s; fetched %s "
                       "(stream w5si, MESHSAT-1357, rule SI-001), sha256/16 %s, the full sha256 in the manifest; file rev %s, %s; %s"
                       % (key, r["id"], r["maker"], r["literature"], r["url"], serves, arch, r["fetched"], r["sha256"][:16],
                          r["file_rev"], r["file_date"], says))
            else:
                m = re.match(r"^(\S+)\s+(\S+)\s+#\s*(.*)$", old)
                assert m and m.group(2) == "current", old
                reason = m.group(3)
                assert "not in the repository" not in reason
                new = "%s   %s   # %s; not in the repository: pinned by ibis-manifest.yaml and fetched by v2/ecad/tools/ibis_fetch.py" % (
                    key, m.group(2), reason)
            assert new != old and chr(0x2014) not in new and "\n" not in new
            lines[i] = new; changed += 1
        assert changed == 13
        text = "\n".join(lines)
        before = open(p, encoding="utf-8").read().split("\n")
        assert len(before) == len(lines) and sum(1 for x, y in zip(before, lines) if x != y) == 13, name
        out[p] = text
    if "--dry-run" in a:
        print("dry run: 13 lines of each file would change"); return
    for p, text in out.items():
        open(p, "w", encoding="utf-8").write(text)
        assert open(p, encoding="utf-8").read() == text
    print("sources.txt and vendor-status.txt: 13 lines each rewritten from %s" % man["path"])


if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(2)
    main(sys.argv[1:])
