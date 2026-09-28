#!/usr/bin/env python3
"""The records index (v2/docs/records/README.md, its first table `| folder | whose records |`) brought up to the folders
of 28 and 29 September 2026 (MESHSAT-1357, integration set 9). Seventeen folders had no row. Stream energy's own row
script runs first (it inserts after `h2/`); this script then appends the other sixteen rows at the end of the table, in
the order the work happened. Each row states what the folder holds, read from its files at integration set 9.
Asserted: every row names a folder that exists and was unlisted; after writing, the table lists every folder under
v2/docs/records/ and nothing else changed outside the table. Refuses a second run. Run from the repository root."""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE, capture_output=True, check=True).stdout.decode().strip()
IDX = os.path.join(TOP, "v2/docs/records/README.md")
ROWS = [
    ("retake6", "the consolidated re-take of set 6 (27 and 28 September 2026): the box scripts and readings (`box/`, `RESULT.txt`), the analysis of what moved, and the script that rebinds CON-010 and REQ-044 to the re-rendered evidence page"),
    ("int7", "integration set 6 (28 September 2026, branch `fnd/int7`): the registry merge resolver, CON-010 re-decided from the readings by a predicate, the waits_on dispositions, the answers to the three AI checks (`CHECK.md`, `CHECK-2.md`, `CHECK-3.md`, `CHECK-RESPONSE.md`), the closure record and the page rebind"),
    ("w5si", "stream w5si's record (27 September 2026), filed at set 7: its edges check, its readings and tools, and its recovery after the runner's reboot; the makers' IBIS models it used are never committed"),
    ("w5si2", "stream w5si2 (28 September 2026, branch `fnd/w5si2`): SI-001's edge rates made integrable without publishing a model, and board C's declarations, with readings and tools"),
    ("w5tray", "stream w5tray (28 September 2026): the QMX lid tray r2 (S-63, EQ-24), its passes, drafts and recovery record; AI work and AI review only"),
    ("d8dec31", "stream d8dec31 (28 September 2026): what the AI review of decision 31 (`v2/docs/reviews/DECISION-31-PROTECTION-TOPOLOGY.md`) was written from, its declaration, registry, hold and generator apply scripts, and the pin tables it read"),
    ("d6rel", "stream d6rel (28 September 2026, finding H3-01): REL-001's population read on an explicit inventory, the four-case matrix before and after the tool's repair, and its apply scripts"),
    ("p3bind", "stream p3bind (28 September 2026): the layout constraint sheets bound to their inputs, the rail commits and moves behind each sheet, and the rule and coverage apply script"),
    ("cx1", "the Codex pilot on finding I-03 (28 September 2026, branch `fnd/cx1`; an AI worker of a second model family): the A to B power leads reconciled against the makers' pages (`ANALYSIS.md`, its correction `CORRECTION.md`, `if_ab_power.py` with its output), the declarations draft, and the independent Claude checks under `checks/`"),
    ("int8", "integration set 7 (28 September 2026, branch `fnd/int8`): the apply scripts of the carried check items, the owner's rulings of that day (D-19, D-20, S-114), the I-03 items and the contact rating, the AI check and the closure record"),
    ("s99", "S-99, board A's +5V_DEV stage against the coincident demand (28 September 2026): the analysis, the Codex correction with its checks, the rail-by-rail actionable list (`RAILS-ACTIONABLE.md`), `dev_stage.py` and the D8 split draft"),
    ("s98", "stream s98 (28 September 2026): the interim alignment of the A to B power declarations, the contract and architecture apply scripts, the box regeneration of boards A and B, the lead ends, the closure text and the layer rows"),
    ("int9", "integration set 8 (28 and 29 September 2026, branch `fnd/int9`): S-98 closed for declaration consistency, the rebinds after the regeneration of boards A and B proved by AST and by parsed netlists, the netlist pins moved, the constraint sheets re-bound, and the box records"),
    ("s99a", "stream s99a (28 and 29 September 2026): S-99's corrected D8 split applied to board A's generator (decision 55): U41's divider arithmetic, the parsed comparison, the codec-floor and layout open items, the registry draft and the tests"),
    ("od01", "the OD-01 case package for the owner (28 September 2026): the checkout list, the machining request, the operator's test brief, and the two AI checks under `checks/`; purchasing stays with the owner"),
    ("int10", "integration set 9 (29 September 2026, branch `fnd/int10`): the regeneration of board A with S-99's D8 split, the pins moved on a parsed proof, sheet A re-bound, the judged rebind of the records bound to board A's netlist and generator, the page rebind, and the box records"),
]


def refuse(m):
    print("apply_records_index: REFUSED: %s" % m); sys.exit(2)


def listed(t):
    return set(re.findall(r"^\| `([A-Za-z0-9_.-]+)/` \|", t, re.M))


def main():
    t0 = open(IDX, encoding="utf-8").read()
    if "| `int10/` |" in t0: refuse("already applied")
    if "| `energy/` |" not in t0:
        r = subprocess.run([sys.executable, os.path.join(TOP, "v2/docs/records/energy/apply_records_readme_row.py")], capture_output=True, text=True)
        print(r.stdout.strip())
        if r.returncode: refuse("stream energy's row script failed: %s" % r.stderr[-300:])
    t = open(IDX, encoding="utf-8").read()
    dirs = {d for d in os.listdir(os.path.dirname(IDX)) if os.path.isdir(os.path.join(os.path.dirname(IDX), d))}
    have = listed(t)
    for name, _ in ROWS:
        if name not in dirs: refuse("no folder %s" % name)
        if name in have: refuse("%s is already listed" % name)
    lines = t.split("\n")
    head = next(i for i, l in enumerate(lines) if l.startswith("| folder | whose records |"))
    end = head + 2
    while end < len(lines) and lines[end].startswith("| "): end += 1
    new = ["| `%s/` | %s |" % (n, s) for n, s in ROWS]
    for s in new:
        if "—" in s or "–" in s: refuse("a dash character in a row")
    out = "\n".join(lines[:end] + new + lines[end:])
    if listed(out) & dirs != dirs: refuse("still unlisted: %s" % sorted(dirs - listed(out)))
    if out.replace("\n".join(new) + "\n", "", 1) != t: refuse("something outside the new rows changed")
    open(IDX, "w", encoding="utf-8").write(out)
    print("apply_records_index: %d rows appended; the index lists all %d folders" % (len(new), len(dirs)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
