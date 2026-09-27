#!/usr/bin/env python3
"""Write the MANIFEST.sha256 of a case release folder (MESHSAT-1357, 27 Sep 2026): one line per file, `sha256  relative/path`, sorted, the
manifest itself left out, in the format `sha256sum -c` reads. A release folder is an immutable copy of what the editable sources produced;
v2/cad/case_geometry_check.py `manifest()` (run by v2/ecad/tools/tests/test_case_geometry.py) refuses a folder whose files no longer carry the
digests written here. Run it last, after the folder's README.md is written. Stdlib only.

Usage: case_manifest.py <release folder> [--base <commit>]"""
import os, sys, hashlib, datetime


def manifest_lines(folder):
    out = []
    for root, dirs, files in os.walk(folder):
        dirs.sort()
        for f in sorted(files):
            p = os.path.join(root, f)
            rel = os.path.relpath(p, folder).replace(os.sep, "/")
            if rel == "MANIFEST.sha256" or rel.startswith("."):
                continue
            out.append((rel, hashlib.sha256(open(p, "rb").read()).hexdigest()))
    return sorted(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    folder = sys.argv[1]
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else os.environ.get("CASE_BASE_COMMIT", "")
    lines = manifest_lines(folder)
    with open(os.path.join(folder, "MANIFEST.sha256"), "w", encoding="utf-8") as fh:
        fh.write("# MeshSat V2 case release %s: sha256 of every file (sha256sum -c MANIFEST.sha256). Written %s by v2/cad/case_manifest.py%s.\n"
                 % (os.path.basename(os.path.normpath(folder)), datetime.date.today().isoformat(), (" from tree %s" % base) if base else ""))
        for rel, h in lines:
            fh.write("%s  %s\n" % (h, rel))
    print("wrote %s (%d files)" % (os.path.join(folder, "MANIFEST.sha256"), len(lines)))
