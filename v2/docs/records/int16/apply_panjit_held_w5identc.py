#!/usr/bin/env python3
"""Set 15's integration check (records/int16/checks/check-int16-1.md, B1 and B2) answered (MESHSAT-1357, 30 September 2026).
records/int16/apply_panjit_path_w5identc.py moved the three SS2040FL citations (D19 to D21) of stream w5identc's board C
table to the PANJIT sheet's held path but did not mark them held back, as the Uniroyal bindings are: on a host without the
sheet the identity test refused 'S-330f4dd290 cites a document not in the tree' and `part_identities.py check` refused all
three even with --unfetched-ok (B1); and the generated page BOARD-C-SELECTIONS.md was not re-rendered, so it still named
the old path (B2). This script, asserting each step:
  1. makes records/w5identc/build_table.py carry a binding's held_back and fetch fields from its input into the table
     for a PRINTED binding, as it already writes them for the DECODED Uniroyal bindings (one guarded edit);
  2. adds held_back: true and fetch: v2/docs/records/int16/fetch_held_back.py to exactly the three PANJIT datasheet
     citations of records/w5identc/w5ident-board-c-identities.json;
  3. re-runs build_table.py and requires the counts to be unchanged (21 printed, 23 decoded) and the table to differ from
     the committed one only by those two fields on the three bindings;
  4. re-runs part_identities.py check with --out into the pinned reading and requires 0 problems, and re-pins
     READING_SHA256 in records/w5identc/apply_identities_c.py;
  5. re-renders BOARD-C-SELECTIONS.md with part_identities.py render.
The held sheet must be present (records/int16/fetch_held_back.py). Refuses a second run. Run: python3 <this file>."""
import hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
REC = os.path.join(TOP, "v2/docs/records/w5identc")
HELD = "v2/vendor/power/held/panjit-ss2020fl-series.pdf"
FETCH = "v2/docs/records/int16/fetch_held_back.py"
TABLE = "v2/ecad/tools/pcb_part_identities.yaml"
PAGE = os.path.join(REC, "BOARD-C-SELECTIONS.md")
READING = os.path.join(REC, "readings", "check-board-c-b874b744.json")
WANT = {"PRINTED": 21, "DECODED": 23}
OLD_RET = 'return dict(path=path, sha256=got, page=pages[0], names=line, joined_by=ds.get("joined_by") or "this stream"), None'
NEW_RET = ('return dict(path=path, sha256=got, page=pages[0], names=line, joined_by=ds.get("joined_by") or "this stream",\n'
           '                **{k: ds[k] for k in ("held_back", "fetch") if k in ds}), None   # records/int16/apply_panjit_held_w5identc.py')


def refuse(m):
    print("apply_panjit_held_w5identc: REFUSED: %s" % m); sys.exit(2)


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def main():
    bp = os.path.join(REC, "build_table.py"); b = open(bp, encoding="utf-8").read()
    if NEW_RET in b: refuse("already applied")
    if b.count(OLD_RET) != 1: refuse("build_table.py's PRINTED return appears %d times, not once" % b.count(OLD_RET))
    if not os.path.exists(os.path.join(TOP, HELD)): refuse("the held sheet is not present: run %s" % FETCH)
    jp = os.path.join(REC, "w5ident-board-c-identities.json"); j = json.load(open(jp, encoding="utf-8"))
    hits = []
    def walk(o):
        if isinstance(o, dict):
            if o.get("path") == HELD: hits.append(o)
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(j)
    if len(hits) != 3: refuse("the input cites the held PANJIT path %d times, not 3" % len(hits))
    if any("held_back" in h or "fetch" in h for h in hits): refuse("a PANJIT citation already carries held_back or fetch")
    nb = b.replace(OLD_RET, NEW_RET); assert nb != b; compile(nb, bp, "exec")
    open(bp, "w", encoding="utf-8").write(nb)
    for h in hits: h["held_back"] = True; h["fetch"] = FETCH
    raw = open(jp, encoding="utf-8").read()
    if json.dumps(json.loads(raw), indent=0, ensure_ascii=True, sort_keys=True) != raw: refuse("the input is not in the form this script writes back")
    out = json.dumps(j, indent=0, ensure_ascii=True, sort_keys=True)   # the input's own form: indent 0, ASCII, sorted keys
    open(jp, "w", encoding="utf-8").write(out); json.load(open(jp, encoding="utf-8"))
    r = subprocess.run([sys.executable, bp], cwd=TOP, capture_output=True, text=True)
    if r.returncode: refuse("build_table failed: %s" % (r.stdout + r.stderr)[-400:])
    m = re.search(r"resolved by binding \{'PRINTED': (\d+), 'DECODED': (\d+)\}", r.stdout)
    if not m or {"PRINTED": int(m.group(1)), "DECODED": int(m.group(2))} != WANT: refuse("the rebuilt counts: %s" % r.stdout[-300:])
    d = subprocess.run(["git", "-C", TOP, "diff", "-U0", "--", TABLE], capture_output=True, text=True).stdout
    changed = [l for l in d.split("\n") if l and l[0] in "+-" and not l.startswith(("+++", "---"))]
    if len(changed) != 6 or any(not re.match(r"^\+\s+(held_back: true|fetch: %s)$" % re.escape(FETCH), l) for l in changed):
        refuse("the table moved beyond the two fields on the three bindings: %s" % changed[:8])
    ck = subprocess.run([sys.executable, "part_identities.py", "check", "--out", READING], cwd=os.path.join(TOP, "v2/ecad/tools"),
                        capture_output=True, text=True)
    if ck.returncode or not re.search(r"\b0 problems\b", ck.stdout): refuse("the check: %s" % (ck.stdout + ck.stderr)[-400:])
    ap = os.path.join(REC, "apply_identities_c.py"); a = open(ap, encoding="utf-8").read()
    old = re.search(r'READING_SHA256 = "([0-9a-f]{64})"[^\n]*', a)
    if not old or a.count(old.group(0)) != 1: refuse("apply_identities_c.py's pin")
    new_sha = sha(READING)
    open(ap, "w", encoding="utf-8").write(a.replace(old.group(0), 'READING_SHA256 = "%s"   # re-pinned by records/int16/apply_panjit_held_w5identc.py' % new_sha))
    rn = subprocess.run([sys.executable, "part_identities.py", "render", TABLE.split("/")[-1], "--out", PAGE],
                        cwd=os.path.join(TOP, "v2/ecad/tools"), capture_output=True, text=True)
    if rn.returncode: refuse("render: %s" % (rn.stdout + rn.stderr)[-300:])
    pg = open(PAGE, encoding="utf-8").read()
    if "v2/vendor/power/panjit-ss2020fl-series.pdf" in pg: refuse("the page still names the old path")
    print("apply_panjit_held_w5identc: three PANJIT bindings marked held back (fetch %s); table 21 printed, 23 decoded; check 0 problems; reading %s pinned; BOARD-C-SELECTIONS.md re-rendered" % (FETCH, new_sha[:16]))


if __name__ == "__main__":
    main()
