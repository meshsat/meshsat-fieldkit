#!/usr/bin/env python3
"""apply_l5r4_rebind.py: the requirements registry's readings bound to PANEL.md, rebound after Layer 5's round 4 (MESHSAT-1357, set 29,
3 October 2026; record l5r4; the pattern of records/int28b/apply_set28b_rebind.py). The INTEGRATOR's script: it edits
v2/ecad/tools/pcb_requirements.yaml (the integrator's file) and nothing else.

apply_l5r4.py changes PANEL.md's section 5 only (the slot-fault rule, finding F-14, and its follow-up F-15 and S-37). The script
reads the bound file from the binding and the new one from the tree at run time, so it rebinds from set 28's file or, if it has
already run on round 4's first file, from that one. Five readings are bound to PANEL.md's content by
sha256/16 (CFL-001, CFL-005, CFL-014, CFL-015, CFL-016), so `rules_lib.py requirements` reads an error for each binding until they are
rebound. None of them rests on section 5:
  CFL-001  the head (line 5, bank 1's home and failover hosts), section 1's pin table and section 2's ribbon table
  CFL-005  section 7
  CFL-014  section 10 (the strap, VSYS and bench-question sentences)
  CFL-015  section 10 (the pack SMBus lead sentences); its ASSEMBLY.md binding is untouched
  CFL-016  sections 1, 6 and 7; its ASSEMBLY.md binding is untouched
For each, the sections it rests on must be byte-identical between the bound file and the tree's, and no section but 5 may differ at all
(any other change refuses: a judged re-read, not a rebind). The old file is the one the binding names, found in the history of PANEL.md
by its sha256/16; the new is the tree's. It adds one evidence entry per record and moves the binding; it changes no evidence_result, no
status and no other record. A second run refuses "already applied". The entries carry no word the ENV-002 claims screen counts and no
dash. Usage, from anywhere: apply_l5r4_rebind.py [--check | --write]. Exit 0 written or checked; 3 refused."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = "v2/ecad/tools/pcb_requirements.yaml"
PANEL = "v2/docs/PANEL.md"
ROUND = ("Layer 5's round 4 (records/l5r4/L5-R4-SLOT-FAULTS.md, branch fnd/l5r4 from set 28's 92a5c7d8; the panel firmware's finding "
         "F-14 decided: section 5's slot-fault rule now covers a module lost at start-up and one lost while running; with its "
         "follow-up F-15 and S-37: a power-on reset read as HAD_POR set and the watchdog's REASON zero, the slot record beside the "
         "wipe journal)")
ONLY = "5"   # the one section apply_l5r4.py changes
GROUND = {
    "CFL-001": (("head", "1", "2"), "line 5 (bank 1's home and failover hosts), section 1's pin table and section 2's ribbon table"),
    "CFL-005": (("7",), "section 7 (EMCON_HW's pull and the panel-less kit)"),
    "CFL-014": (("10",), "section 10's strap, VSYS and bench-question sentences"),
    "CFL-015": (("10",), "section 10's pack SMBus lead sentences"),
    "CFL-016": (("1", "6", "7"), "sections 1, 6 and 7 (the radios' EMCON path, the toggles, the bus table)"),
}


def refuse(msg):
    print("apply_l5r4_rebind: REFUSED: %s" % msg)
    sys.exit(3)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def sections(text):
    """{number: lines}; 'head' for the text before the first '## '; a heading's number is its first token without the dot."""
    out, cur = {"head": []}, "head"
    for line in text.split("\n"):
        if line.startswith("## "):
            cur = line[3:].split(" ")[0].rstrip(".")
            out[cur] = [line]
        else:
            out[cur].append(line)
    return out


def old_text(path, old16):
    log = subprocess.run(["git", "log", "--format=%H", "-n", "600", "--", path], cwd=TOP, capture_output=True, text=True, check=True).stdout.split()
    for c in log:
        r = subprocess.run(["git", "show", "%s:%s" % (c, path)], cwd=TOP, capture_output=True)
        if r.returncode == 0 and sha16(r.stdout) == old16:
            return r.stdout.decode("utf-8"), c[:8]
    refuse("no commit in the history of %s carries it at %s" % (path, old16))


def rec_span(t, rid):
    i = t.index("\n  - id: %s\n" % rid) + 1
    j = t.find("\n  - id: ", i + 5)
    return i, (j + 1 if j > 0 else len(t))


def wrap(s):
    words, lines, cur = s.split(), [], "         "
    for w in words:
        if len(cur) + 1 + len(w) > 120:
            lines.append(cur)
            cur = "          " + w
        else:
            cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def main(argv):
    write = "--write" in argv
    t = open(os.path.join(TOP, P), encoding="utf-8").read()
    new_text = open(os.path.join(TOP, PANEL), encoding="utf-8").read()
    new16 = sha16(new_text.encode("utf-8"))
    out, notes, moved = t, {}, []
    for rid, (same, rests) in GROUND.items():
        i, j = rec_span(out, rid)
        bound = re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(PANEL), out[i:j])
        if len(bound) != 1:
            refuse("%s carries %d binding(s) to %s, one expected" % (rid, len(bound), PANEL))
        old16 = bound[0]
        if old16 == new16:
            continue
        otext, ocommit = old_text(PANEL, old16)
        so, sn = sections(otext), sections(new_text)
        if set(so) != set(sn):
            refuse("%s: PANEL.md's sections differ in number between %s and the tree" % (rid, old16))
        differ = [k for k in sn if so[k] != sn[k]]
        if [k for k in differ if k != ONLY]:
            refuse("%s: sections %s differ, where only section %s may: a judged re-read, not a rebind" % (rid, differ, ONLY))
        for s in same:
            if so[s] != sn[s]:
                refuse("%s rests on section %s, which differs" % (rid, s))
        same_all = [k for k in sn if so[k] == sn[k]]
        name = lambda k: "the head" if k == "head" else k
        note = ("%s re-read at %s (MESHSAT-1357; the file before at %s, the content of %s). Of its sections, %s, and %s are "
                "byte-identical. This reading rests on %s: %s; so the ground it was decided on is unchanged. This entry rebinds the "
                "file and re-decides nothing: the result stands as set, bound to the file at %s."
                % (PANEL, ROUND, old16, ocommit, ("section %s differs" % ", ".join(differ)) if differ else "no section differs",
                   ", ".join(name(k) for k in same_all), rests,
                   "; ".join("%s byte-identical" % ("the head" if s == "head" else "section " + s) for s in same), new16))
        sys.path.insert(0, os.path.join(TOP, "v2", "ecad", "tools"))
        import claims_check as _cc
        hit = _cc.CLAIM.search(note)
        if hit:
            refuse("the entry for %s carries the claim word %r" % (rid, hit.group(0)))
        if chr(0x2014) in note or chr(0x2013) in note:
            refuse("the entry for %s carries a dash" % rid)
        r = out[i:j]
        res0 = re.search(r"(?m)^    evidence_result: (\S+)", r).group(1)
        r2 = r.replace('"%s@%s"' % (PANEL, old16), '"%s@%s"' % (PANEL, new16))
        k = r2.index("    evidence_bound_to:")
        r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
        assert r2 != r and re.search(r"(?m)^    evidence_result: (\S+)", r2).group(1) == res0
        out = out[:i] + r2 + out[j:]
        notes[rid] = (old16, note)
        moved.append((rid, old16, new16))
    if not moved:
        refuse("already applied: every binding of the five records to PANEL.md is the tree's")
    import yaml
    A, B = yaml.safe_load(t), yaml.safe_load(out)
    ra = {r["id"]: r for r in A["records"]}
    rb = {r["id"]: r for r in B["records"]}
    if list(ra) != list(rb) or {k: v for k, v in A.items() if k != "records"} != {k: v for k, v in B.items() if k != "records"}:
        refuse("something outside the five records changed")
    changed = sorted(k for k in ra if ra[k] != rb[k])
    if not set(changed) <= set(GROUND):
        refuse("records changed: %s" % changed)
    for k in changed:
        x, y = ra[k], rb[k]
        keys = sorted(f for f in set(x) | set(y) if x.get(f) != y.get(f))
        if keys != ["evidence", "evidence_bound_to"]:
            refuse("%s: fields changed: %s" % (k, keys))
        if y["evidence"][:-1] != x["evidence"]:
            refuse("%s: the evidence list is not the old list plus one entry" % k)
    for rid, o, n in moved:
        print("apply_l5r4_rebind: %s %s %s -> %s, evidence_result %s unchanged" % ("rebound" if write else "rebinds", rid, o, n,
                                                                                   rb[rid]["evidence_result"]))
    if not write:
        print("apply_l5r4_rebind: --check, nothing written; the entries:")
        for rid, (o, note) in notes.items():
            print("--- %s\n%s" % (rid, note))
        return 0
    with open(os.path.join(TOP, P), "w", encoding="utf-8") as fh:
        fh.write(out)
    if yaml.safe_load(open(os.path.join(TOP, P), encoding="utf-8").read()) != B:
        refuse("the file written does not re-parse to what was checked")
    print("apply_l5r4_rebind: next: rules_lib.py requirements (0 errors), rules_render.py --requirements, render_l3r2.py, the re-pins")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
