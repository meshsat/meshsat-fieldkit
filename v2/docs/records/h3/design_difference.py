#!/usr/bin/env python3
"""What changed between the source commit of handover H2 and a commit, by class (MESHSAT-1357, 27 September 2026).

Written by the H3 pages worker for the statement the H3 pages make: H3's design content is H2's. It compares H2's
source commit, b89b50b4, with a commit (default HEAD) and prints every file that differs, in classes, and for the
registries and the tracked readings that differ it prints WHAT differs after parsing them (YAML and JSON are loaded,
never searched as text). It asserts the statement and exits 1 where it does not hold:

  1. no design file differs: no schematic, committed netlist, intent, provenance sidecar, board file, project file,
     allow list, land pattern, generator, board table, routeflow profile, export, CAD source, case release file,
     diagram or maker document;
  2. under v2/ecad/tools/ the only programs that differ are the packer and its test (no generator, no checking tool);
  3. in the requirements registry no record differs in a field outside its readings and notes;
  4. in the interfaces registry nothing differs but the `read_at` text of `board_to_board` and free-text labels;
  5. each tracked reading that differs gives the same verdict on the same inputs by content;
  6. the requirements registry at the commit differs from the registry at the commit its own `baseline_state` names
     (layer 3's baseline) in no record field outside the readings and notes, and in no need, ruling or choice.

It reads git only (`git diff --name-status`, `git show <commit>:<path>`), so it needs a checkout that holds both
commits; it does not run from an extracted snapshot, which has no history. It writes nothing but standard output.

Usage (from any folder of the checkout): python3 v2/docs/records/h3/design_difference.py [commit]
"""
import fnmatch, hashlib, json, subprocess, sys

import yaml

H2_SOURCE = "b89b50b4421fd882967b390a09c21dbd307ca98e"
AT = sys.argv[1] if len(sys.argv) > 1 else "HEAD"

# A design file is one whose change would change what H3 hands over as the design. First match decides.
CLASSES = [
    ("handover snapshot (an earlier snapshot's own files)", ["v2/release/handover/H*"]),
    ("DESIGN: export of a committed schematic", ["v2/release/handover/_generated/**"]),
    ("DESIGN: schematic, netlist, intent, provenance, board or project file, allow list",
     ["v2/ecad/pcb-*/*.kicad_sch", "v2/ecad/pcb-*/*.kicad_pcb", "v2/ecad/pcb-*/*.kicad_pro", "v2/ecad/pcb-*/out/**",
      "v2/ecad/pcb-*/fp-lib-table", "v2/ecad/pcb-*/*-allow.txt"]),
    ("tracked reading (a verdict copied to routed/)", ["v2/ecad/pcb-*/routed/**"]),
    ("DESIGN: land pattern", ["v2/ecad/meshsat.pretty/**"]),
    ("DESIGN: generator, board table or routeflow profile",
     ["v2/ecad/tools/gen_*.py", "v2/ecad/tools/kisch.py", "v2/ecad/tools/intent.py", "v2/ecad/tools/schlayout.py",
      "v2/ecad/tools/boards/**", "v2/ecad/tools/routeflow/**"]),
    ("packer and its test", ["v2/ecad/tools/handover_pack.py", "v2/ecad/tools/tests/test_handover_pack.py"]),
    ("registry", ["v2/ecad/tools/*.yaml", "v2/ecad/tools/*.json"]),
    ("TOOL: a checking tool, a pipeline script or a test", ["v2/ecad/tools/**"]),
    ("DESIGN: anything else under v2/ecad", ["v2/ecad/**"]),
    ("DESIGN: CAD source or case release", ["v2/cad/**", "v2/release/case-2026-09-27/**", "v2/release/revA/**"]),
    ("DESIGN: maker document or vendor record", ["v2/vendor/**"]),
    ("DESIGN: diagram", ["v2/docs/diagrams/**"]),
    ("page, review or record under v2/docs", ["v2/docs/**"]),
    ("overview", ["README.md", "v2/README.md"]),
]
FORBIDDEN = ("DESIGN:", "TOOL:")
# The fields of a requirement record outside its readings and notes (the H2 record's KEEP list, with `stages`,
# `holds_layout_entry`, `title`, `blocks` and the feasibility fields added).
KEEP = ("statement", "acceptance", "prototype_1", "prototype_1_basis", "prototype_1_choice", "prototype_1_why",
        "allocated_to", "verification_method", "verification_phase", "final_phase", "release_effect", "kind", "parent",
        "status", "satisfied_by", "rule_coverage", "rulings", "choices", "waits_on", "tbd_effect", "provisional",
        "source", "title", "stages", "holds_layout_entry", "blocks", "blocker_ids", "closing_evidence",
        "feasibility_page", "owner")


def _top():
    """The repository's top level, asked of git from this file's own folder, so that the script reads the same
    tree whatever folder it is started in. Run from its own folder on 27 September 2026 it listed no file (a git
    pathspec is relative to the working directory), compared nothing, and still printed that the statement holds:
    a pass of nothing. Every git call now runs at the top level, and comparing nothing is a failure (main)."""
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    return subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=here, capture_output=True,
                          check=True).stdout.decode().strip()


TOP = _top()
# The six declared phase folders with a schematic, and E5's board file: what MUST be among the files compared.
MUST_COMPARE = ["-a23/", "-b19/", "-c8/", "-d9/", "-e7/", "-p2/"]


def git(*a):
    return subprocess.run(["git"] + list(a), cwd=TOP, capture_output=True, check=True).stdout


def show(commit, path):
    return git("show", "%s:%s" % (commit, path))


def match(path, pat):
    if "**" in pat:
        head = pat.split("**")[0]
        return fnmatch.fnmatchcase(path, head + "*")
    return fnmatch.fnmatchcase(path, pat) and path.count("/") == pat.count("/")


def klass(path):
    for name, pats in CLASSES:
        if any(match(path, p) for p in pats):
            return name
    return "UNCLASSED"


def s16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def diff_paths(a, b, path=""):
    """Every leaf path at which two parsed values differ."""
    if type(a) is not type(b):
        return [path or "."]
    if isinstance(a, dict):
        out = []
        for k in sorted(set(a) | set(b), key=str):
            if k not in a or k not in b:
                out.append("%s/%s" % (path, k))
            else:
                out += diff_paths(a[k], b[k], "%s/%s" % (path, k))
        return out
    if isinstance(a, list):
        if len(a) != len(b):
            return ["%s (length %d to %d)" % (path or ".", len(a), len(b))]
        out = []
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff_paths(x, y, "%s[%d]" % (path, i))
        return out
    return [] if a == b else [path or "."]


def registry(P, old, new, what):
    """The registry at two commits, entry by entry; returns what differs that may not."""
    bad = []
    ta, tb = show(old, P), show(new, P)
    a, b = yaml.safe_load(ta), yaml.safe_load(tb)
    print("\n[%s: %s (%s, sha256/16 %s) to %s (sha256/16 %s)]" % (P, old[:8], what, s16(ta), new[:8], s16(tb)))
    for k in sorted(set(a) | set(b)):
        if k in ("needs", "owner_rulings", "session_choices", "open_items", "closed_items", "records"):
            continue
        if a.get(k) != b.get(k):
            print("  top-level %s: %r -> %r" % (k, a.get(k), b.get(k)))
    for sec in ("needs", "owner_rulings", "session_choices", "open_items", "closed_items", "records"):
        A = {x["id"]: x for x in a.get(sec) or []}
        B = {x["id"]: x for x in b.get(sec) or []}
        added = [k for k in B if k not in A]
        removed = [k for k in A if k not in B]
        changed = [k for k in A if k in B and A[k] != B[k]]
        print("  %s: %d to %d; added %s; removed %s; changed %s" % (
            sec, len(A), len(B), " ".join(added) or "none", " ".join(removed) or "none", len(changed) or "none"))
        for k in changed:
            fields = sorted(f for f in set(A[k]) | set(B[k]) if A[k].get(f) != B[k].get(f))
            print("      %s: %s" % (k, ", ".join(fields)))
            if sec == "records":
                bad += ["registry %s.%s" % (k, f) for f in fields if f in KEEP]
            if sec in ("needs", "owner_rulings", "session_choices"):
                bad.append("registry %s %s changed" % (sec, k))
        if sec in ("needs", "owner_rulings", "session_choices", "records") and (added or removed):
            bad.append("registry %s added or removed" % sec)
    print("  record fields outside the readings and notes, and needs, rulings and choices, that differ: %s" %
          (", ".join(bad) or "none"))
    return bad



def main():
    bad = []
    head = git("rev-parse", AT).decode().strip()
    print("design_difference: %s (H2's source commit) to %s (%s)" % (H2_SOURCE[:8], AT, head[:8]))
    rows = [ln.split("\t") for ln in git("diff", "--name-status", H2_SOURCE, head).decode().splitlines()]
    by = {}
    for r in rows:
        by.setdefault(klass(r[-1]), []).append((r[0], r[-1]))
    print("\n[files that differ: %d]" % len(rows))
    for name, _ in CLASSES + [("UNCLASSED", [])]:
        got = by.get(name, [])
        flag = " <-- NOT EXPECTED" if got and (name.startswith(FORBIDDEN) or name == "UNCLASSED") else ""
        print("  %-84s %d%s" % (name + ":", len(got), flag))
        if got and (name.startswith(FORBIDDEN) or name == "UNCLASSED"):
            bad += ["%s %s" % (name, p) for _, p in got]
        if got and not name.startswith("page, review"):
            for st, p in got:
                print("      %s %s" % (st, p))
    print("  (the pages, reviews and records under v2/docs are listed by `git diff --name-status %s %s -- v2/docs`)"
          % (H2_SOURCE[:8], AT))

    # ------------------------------------------------------------ each board's design files, by content
    print("\n[each board's committed design files, sha256/16 at both commits]")
    tree = git("ls-tree", "-r", "--name-only", head, "--", "v2/ecad").decode().splitlines()
    wanted = [p for p in tree if klass(p).startswith("DESIGN: schematic") and "/pcb-" in p
              and (p.endswith(".kicad_sch") or p.endswith(".net") or p.endswith("-intent.json")
                   or p.endswith(".net.prov.json") or p == "v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb")]
    old_tree = set(git("ls-tree", "-r", "--name-only", H2_SOURCE, "--", "v2/ecad").decode().splitlines())
    n_same = 0
    for p in sorted(wanted):
        b = s16(show(head, p))
        a = s16(show(H2_SOURCE, p)) if p in old_tree else "absent"
        if a != b:
            print("  DIFFERS %s: %s to %s" % (p, a, b)); bad.append("design file %s" % p)
        else:
            n_same += 1
            declared = any(d in p for d in ("-a23/", "-b19/", "-c8/", "-d9/", "-e7/", "-p2/"))
            if declared and (p.endswith(".net") or p.endswith(".kicad_sch")):      # the six declared phases
                print("  same    %s %s" % (p, b))
    print("  %d schematic, netlist, intent and provenance files (and E5's board file) compared, %d the same"
          % (len(wanted), n_same))
    for d in MUST_COMPARE:
        for ext in (".kicad_sch", ".net"):
            if not any(d in p and p.endswith(ext) for p in wanted):
                print("  NOTHING COMPARED for the declared phase %s (%s)" % (d.strip("-/"), ext))
                bad.append("no %s compared for the declared phase %s" % (ext, d.strip("-/")))
    if "v2/ecad/pcb-e5-block/pcb-e5-block.kicad_pcb" not in wanted:
        print("  NOTHING COMPARED for board E5's board file"); bad.append("E5's board file not compared")

    # ------------------------------------------------------------ the requirements registry
    P = "v2/ecad/tools/pcb_requirements.yaml"
    bad += registry(P, H2_SOURCE, head, "H2's source commit")
    base = (yaml.safe_load(show(head, P)).get("baseline_state") or "").split()
    if len(base) == 3 and base[:2] == ["BASELINED", "at"]:
        bad += registry(P, git("rev-parse", base[2]).decode().strip(), head, "the commit its baseline_state names")
    else:
        print("\n[%s: baseline_state is %r, no baseline commit to compare with]" % (P, " ".join(base)))
        bad.append("registry baseline_state")
    # ------------------------------------------------------------ the interfaces registry
    P = "v2/ecad/tools/pcb_interfaces.yaml"
    ta, tb = show(H2_SOURCE, P), show(head, P)
    a, b = yaml.safe_load(ta), yaml.safe_load(tb)
    print("\n[%s: sha256/16 %s to %s]" % (P, s16(ta), s16(tb)))
    dp = diff_paths(a, b)
    for d in dp:
        print("  differs at %s" % d)
    free = ("read_at", "note", "notes", "src_note", "why", "comment")
    hard = [d for d in dp if not any(d.rstrip("]0123456789[").endswith("/" + f) or ("/" + f + "[") in d or
                                     ("/" + f + "/") in d for f in free)]
    print("  parsed values that differ outside free text (%s): %s" % (", ".join(free), ", ".join(hard) or "none"))
    if hard:
        bad += ["interfaces %s" % d for d in hard]
    if not dp:
        print("  the parsed registry is equal: the file differs in comments or layout only")

    # ------------------------------------------------------------ the tracked readings
    print("\n[tracked readings that differ]")
    for st, p in by.get("tracked reading (a verdict copied to routed/)", []):
        ja, jb = json.loads(show(H2_SOURCE, p)), json.loads(show(head, p))
        dp = diff_paths(ja, jb)
        print("  %s: verdict %s to %s; differs at %s" % (p, ja.get("verdict"), jb.get("verdict"), ", ".join(dp)))
        if ja.get("verdict") != jb.get("verdict") or ja.get("counts") != jb.get("counts"):
            bad.append("reading %s verdict or counts" % p)
        ia, ib = ja.get("inputs") or {}, jb.get("inputs") or {}
        for k in sorted(set(ia) | set(ib)):
            if k in ("netlist", "intent", "board_file") and ia.get(k) != ib.get(k):
                bad.append("reading %s input %s" % (p, k))

    # ------------------------------------------------------------ the exports against the committed files
    print("\n[exports under v2/release/handover/_generated at %s, against the files of that commit]" % AT)
    n_exports = 0
    for p in sorted(x for x in git("ls-tree", "-r", "--name-only", head, "--",
                                   "v2/release/handover/_generated").decode().splitlines()
                    if x.endswith("/provenance.json")):
        j = json.loads(show(head, p))
        n_exports += 1
        sch = hashlib.sha256(show(head, j["schematic"])).hexdigest()
        net = hashlib.sha256(show(head, "%s/out/%s.net" % (j["phase_directory"], j["stem"]))).hexdigest()
        ok_s, ok_n = sch == j["schematic_sha256"], net == j.get("committed_netlist_sha256")
        print("  %s: made at %s; schematic %s %s; netlist %s %s" % (
            j["board"].upper(), j["commit"][:8], sch[:16], "is the one exported" if ok_s else "is NOT the one exported",
            net[:16], "is the one the export names" if ok_n else "is NOT the one the export names"))
        if not (ok_s and ok_n):
            bad.append("export %s" % p)

    if n_exports < len(MUST_COMPARE):
        print("  %d export(s) read where %d boards have a schematic" % (n_exports, len(MUST_COMPARE)))
        bad.append("%d exports read, %d expected" % (n_exports, len(MUST_COMPARE)))

    print("\nresult: %s" % ("THE STATEMENT HOLDS: no design file, generator or checking tool differs from H2's source "
                            "commit" if not bad else "THE STATEMENT DOES NOT HOLD: " + "; ".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
