#!/usr/bin/env python3
"""apply_set28b_rebind.py: L5R3-F01 (MESHSAT-1357, set 28, 3 October 2026; the pattern of records/int28/apply_set28_rebind.py and
records/retake6/apply_rebind_current_evidence.py). Layer 5's round 3 (records/l5r2/L5-PANEL-R3.md, fnd/l5r2 at d077fb91) adopted the
panel firmware's findings into v2/docs/PANEL.md and v2/docs/ASSEMBLY.md, and five readings of the requirements registry are bound to
their content by sha256/16 (CFL-001, CFL-005, CFL-014 to PANEL.md; CFL-015 and CFL-016 to both), so `rules_lib.py requirements` reads
an error for each binding. This script re-reads each record's ground in the new files and rebinds it, one evidence entry per record and
file; it changes no evidence_result, no status and no other record.

THE GROUND, per record (what its own evidence entries say it rests on), and what is asserted before a binding moves:
  CFL-001  PANEL.md's head (line 5, bank 1's home and failover hosts), section 1's pin table, section 2's ribbon table with its pin 15
           row: the head and section 2 byte-identical; in section 1 every changed line a PI-button line (below).
  CFL-005  PANEL.md section 7: byte-identical.
  CFL-014  PANEL.md section 10 (the strap, VSYS and bench-question sentences): byte-identical.
  CFL-015  PANEL.md section 10 (the pack SMBus lead sentences): byte-identical; ASSEMBLY.md section 2 (build step 7) byte-identical,
           section 4 (the J_SMB lead row): every changed line a PI-button line.
  CFL-016  PANEL.md sections 1, 6 and 7: 6 and 7 byte-identical, every changed line of 1 a PI-button line; ASSEMBLY.md sections 2,
           8 and 9 byte-identical and 4 (stream s122's scope) changed only in PI-button lines.
A PI-button line is a line whose old and new texts differ only inside the PI button's own clause: removing every clause that names
SW_PI, the PI button, PI_BTN_n, PIJ2 or SPARE1 from both leaves them equal, or the line names the PI button or SPARE1 in both. Any
other change in a section a record rests on refuses that record (it is then a judged re-read, not a rebind).

The old file is the one each binding names, found in the history of its path by its sha256/16; the new is the tree's. Every sha is read
at run time; a second run refuses "already applied". The entries carry no word the ENV-002 claims screen counts and no dash.
Usage, from anywhere: apply_set28b_rebind.py [--check | --write]. Exit 0 written or checked; 3 refused."""
import hashlib
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
P = "v2/ecad/tools/pcb_requirements.yaml"
PANEL, ASSEMBLY = "v2/docs/PANEL.md", "v2/docs/ASSEMBLY.md"
ROUND = ("Layer 5's round 3 (records/l5r2/L5-PANEL-R3.md, fnd/l5r2 at d077fb91, merged into set 28 on branch fnd/int28b; the panel "
         "firmware's findings F-01 and F-04 to F-13 adopted, the PI button's texts marked DRAFTED by record l8r2)")
# record -> file -> (sections byte-identical, sections where only PI-button lines may change, what the reading rests on)
GROUND = {
    "CFL-001": {PANEL: (("head", "2"), ("1",), "line 5 (bank 1's home and failover hosts), section 1's pin table and section 2's ribbon table with its pin 15 row")},
    "CFL-005": {PANEL: (("7",), (), "section 7 (EMCON_HW's pull and the panel-less kit)")},
    "CFL-014": {PANEL: (("10",), (), "section 10's strap, VSYS and bench-question sentences")},
    "CFL-015": {PANEL: (("10",), (), "section 10's pack SMBus lead sentences"),
                ASSEMBLY: (("2",), ("4",), "section 4's pack SMBus lead row and section 2's build step 7")},
    "CFL-016": {PANEL: (("6", "7"), ("1",), "sections 1, 6 and 7 (the radios' EMCON path, the toggles, the bus table)"),
                ASSEMBLY: (("2", "8", "9"), ("4",), "sections 2, 4, 8 and 9 (stream s122's scope)")},
}
PI = re.compile(r"SW_PI|PI button|PI_BTN|PIJ2|SPARE1")


def refuse(msg):
    print("apply_set28b_rebind: REFUSED: %s" % msg)
    sys.exit(3)


def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def sections(text):
    """{number: body}; 'head' for the text before the first '## '; a heading's number is its first token without the dot."""
    out, cur = {"head": []}, "head"
    for line in text.split("\n"):
        if line.startswith("## "):
            cur = line[3:].split(" ")[0].rstrip(".")
            out[cur] = [line]
        else:
            out[cur].append(line)
    return {k: v for k, v in out.items()}


def pi_only(old_lines, new_lines):
    """True when the lines that differ between the two bodies are all PI-button lines (see the docstring)."""
    rem = [l for l in old_lines if l not in new_lines]
    add = [l for l in new_lines if l not in old_lines]
    if len(rem) != len(add):
        return False
    for a, b in zip(rem, add):
        if PI.search(a) and PI.search(b):
            continue
        return False
    return True


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
            lines.append(cur); cur = "          " + w
        else:
            cur += " " + w
    return "\n".join(lines + [cur]) + "\n"


def main(argv):
    write = "--write" in argv
    t = open(os.path.join(TOP, P), encoding="utf-8").read()
    new_text = {f: open(os.path.join(TOP, f), encoding="utf-8").read() for f in (PANEL, ASSEMBLY)}
    new16 = {f: sha16(new_text[f].encode("utf-8")) for f in new_text}
    out, notes, moved = t, {}, []
    for rid, files in GROUND.items():
        i, j = rec_span(out, rid)
        for f, (same, pi_secs, rests) in files.items():
            bound = re.findall(r'"%s@([0-9a-f]{16})"' % re.escape(f), out[i:j])
            if len(bound) != 1:
                refuse("%s carries %d binding(s) to %s, one expected" % (rid, len(bound), f))
            old16 = bound[0]
            if old16 == new16[f]:
                continue
            otext, ocommit = old_text(f, old16)
            so, sn = sections(otext), sections(new_text[f])
            for s in same:
                if s not in so or s not in sn or so[s] != sn[s]:
                    refuse("%s rests on %s %s, which is not byte-identical between %s and the tree" % (rid, f, s, old16))
            for s in pi_secs:
                if s not in so or s not in sn or not pi_only(so[s], sn[s]):
                    refuse("%s rests on %s section %s, where a line other than the PI button's changed: a judged re-read, not a rebind" % (rid, f, s))
            differ = [k for k in sn if k in so and so[k] != sn[k]]
            added = [k for k in sn if k not in so]
            gone = [k for k in so if k not in sn]
            if gone:
                refuse("%s: %s lost section(s) %s" % (rid, f, gone))
            same_all = [k for k in sn if k in so and so[k] == sn[k]]
            name = lambda k: "the head" if k == "head" else ("the pictures section" if not k[:1].isdigit() else k)
            diff_txt = (("section %s differs" % differ[0]) if len(differ) == 1 else ("sections %s differ" % ", ".join(differ))) if differ else "no section differs"
            note = ("%s re-read at the set 28 integration of 3 October 2026 (MESHSAT-1357; %s; the file before at %s, the content of "
                    "%s). Of its sections, %s%s, and %s are byte-identical. This reading "
                    "rests on %s: %s; so the ground it was decided on is unchanged. This entry rebinds the file and re-decides "
                    "nothing: the result stands as set, bound to the file at %s."
                    % (f, ROUND, old16, ocommit, diff_txt, (", section %s is added" % ", ".join(added)) if added else "",
                       ", ".join(name(k) for k in same_all), rests,
                       "; ".join(["%s byte-identical" % ("the head" if s == "head" else "section " + s) for s in same]
                                 + ["section %s changed only in its PI button lines (SW_PI, the PI button, PI_BTN_n, PIJ2, SPARE1: "
                                    "drafted by record l8r2 at 29ffb518)" % s for s in pi_secs]),
                       new16[f]))
            sys.path.insert(0, os.path.join(TOP, "v2", "ecad", "tools"))
            import claims_check as _cc
            hit = _cc.CLAIM.search(note)
            if hit:
                refuse("the entry for %s carries the claim word %r" % (rid, hit.group(0)))
            if "—" in note or "–" in note:
                refuse("the entry for %s carries a dash" % rid)
            r = out[i:j]
            res0 = re.search(r"(?m)^    evidence_result: (\S+)", r).group(1)
            r2 = r.replace('"%s@%s"' % (f, old16), '"%s@%s"' % (f, new16[f]))
            k = r2.index("    evidence_bound_to:")
            r2 = r2[:k] + "      - >-\n" + wrap(note) + r2[k:]
            assert r2 != r and re.search(r"(?m)^    evidence_result: (\S+)", r2).group(1) == res0
            out = out[:i] + r2 + out[j:]
            i, j = rec_span(out, rid)
            notes.setdefault(rid, []).append((f, old16, note))
            moved.append((rid, f, old16, new16[f]))
    if not moved:
        refuse("already applied: every binding of the five records is the tree's")
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
        n = len([m for m in moved if m[0] == k])
        if y["evidence"][:-n] != x["evidence"]:
            refuse("%s: the evidence list is not the old list plus its new entries" % k)
    for rid, f, o, n in moved:
        print("apply_set28b_rebind: %s %s %s -> %s, evidence_result %s unchanged" % ("rebinds" if not write else "rebound", rid + " " + f, o, n, rb[rid]["evidence_result"]))
    if not write:
        print("apply_set28b_rebind: --check, nothing written; the entries:")
        for rid, lst in notes.items():
            for f, o, note in lst:
                print("--- %s %s\n%s" % (rid, f, note))
        return 0
    with open(os.path.join(TOP, P), "w", encoding="utf-8") as fh:
        fh.write(out)
    if yaml.safe_load(open(os.path.join(TOP, P), encoding="utf-8").read()) != B:
        refuse("the file written does not re-parse to what was checked")
    print("apply_set28b_rebind: next: rules_lib.py requirements (0 errors), rules_render.py --requirements, render_l3r2.py, the re-pins")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
